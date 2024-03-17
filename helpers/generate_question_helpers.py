from sqlalchemy.orm import Session

from models.db_models import Quiz, Question
from starlette.exceptions import HTTPException
from helpers import vectorstore_helpers
import uuid
from config.cloudwatch_logger import cloudwatch_logger

from models.llm import GeneratedQuestions

from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI


CHAIN_CACHE = {}


def get_generated_questions(user_id: str, question_generation_settings, db: Session):
    quiz, amount, round_specific_instructions, keywords = _parse_generation_settings(question_generation_settings,
                                                                                     user_id=user_id,
                                                                                     db=db)
    _validate_inputs_and_authorization(quiz=quiz, amount=amount)

    existing_questions = db.query(Question).filter(Question.quiz_id == quiz.quiz_id).all()

    prompt = _get_prompt(amount=amount, keywords=keywords, quiz=quiz, existing_questions=existing_questions,
                         round_specific_instructions=round_specific_instructions)
    chain = _get_chain(quiz=quiz)

    raw_response = chain.invoke(prompt)

    questions = _parse_questions(response=raw_response)

    for q in questions:
        ''' Generate a random id for each generated question. LLM is instructed to do this as well.
        This is for extra security and decoupling from the LLM, which may fail to provide a unique id at times.'''
        q['question_id'] = str(uuid.uuid4())
    return questions
 

def _get_chain(quiz: Quiz | None):
    global CHAIN_CACHE
    if quiz.quiz_id in CHAIN_CACHE:
        # Get chain from cache
        chain = CHAIN_CACHE[quiz.quiz_id]
        cloudwatch_logger.info(f'Retrieved chain from the cache')
    else:
        # Initialize chain and cache
        chain = _initialize_conversation_chain(quiz=quiz)
        CHAIN_CACHE[quiz.quiz_id] = chain
        cloudwatch_logger.info(f'Initialized the chain and stored it in the cache')
    return chain


def _initialize_conversation_chain(quiz: Quiz):
    cloudwatch_logger.info(f'Attempting to get conversation chain for the quiz ID: {quiz.quiz_id}')
    retriever = vectorstore_helpers.get_retriever(quiz=quiz)

    prompt = ChatPromptTemplate.from_template(_get_template(quiz=quiz))
    model = ChatOpenAI(temperature=0.9).bind_tools([GeneratedQuestions])

    chain = (
        {"context": retriever, 'question': RunnablePassthrough()}
        | prompt
        | model
        | JsonOutputToolsParser()
    )

    cloudwatch_logger.info(f'Chain successfully created')
    return chain



def _get_template(quiz: Quiz):
    template = (f'You are a helpful assistant for educators who want to automate the process of quiz creation from'
                f'their teaching material. You will get the relevant parts of the teaching material as the user wants '
                f'to generate questions. A user may generate questions multiple rounds. The title of this quiz is '
                f'{quiz.quiz_title}, which may or may not be relevant to the quiz topic. It is possible that the user'
                f' names it as "First Quiz", which has nothing to do with the context or the content of the quiz. Try '
                f'to be aware of these cases and use the quiz title information only when it makes sense.')
    
    if quiz.quiz_description:
        template += f'This is the description for the provided quiz: {quiz.quiz_description}'
    
    if quiz.keywords:
        template += (f'Here are the keywords from that the user provided. These should be the main focus on the '
                     f'questions that will be created: {quiz.keywords}. Pay special attention to these words and '
                     f'concepts.')
    
    if quiz.meta_prompt:
        template += (f"Lastly, these are the quiz instructions provided by the user, that should be taken into account "
                     f"for all generated questions: {quiz.meta_prompt}\n")
    
    template += ("Exclude irrelevant details such as research questions, methods, etc., and focus on generating "
                 "questions relevant to the educational context.")

    template += ("If relevant questions cannot be generated from the context, indicate so rather than providing "
                 "irrelevant outputs.")

    template += ("Do NOT include identifiers in multiple choices or numbering (e.g., (A), (B), (C), etc.). "
                 "Just include potential answers without any additional formatting.")

    template += """
    Create questions based on the following context
    {context}

    Question: {question}
    """
    
    return template


def _parse_generation_settings(question_generation_settings, user_id: str, db: Session):
    try:
        quiz_id = question_generation_settings.get('quiz_id')
        amount = question_generation_settings.get('amount')
        round_specific_instructions = question_generation_settings.get('instructions')
        keywords = question_generation_settings.get('keywords')

        quiz = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.quiz_id == quiz_id).first()

        cloudwatch_logger.info(f' Succesfully parsed question generation settings')
        return quiz, amount, round_specific_instructions, keywords
    except Exception as e:
        cloudwatch_logger.error(f'Error while parsing question generating settings.'
                                f'Details: {str(e)}')
        raise e


def _validate_inputs_and_authorization(quiz: Quiz | None, amount: str):
    if amount is None:
        raise HTTPException(status_code=400, detail="Bad request.")
    if not quiz:
        raise HTTPException(detail='Quiz not found', status_code=404)

    return True


def _parse_questions(response):
    return response[0].get('args').get('questions')


def _get_prompt(amount, quiz: Quiz, existing_questions: list[Question], keywords=None,
                round_specific_instructions=None):

    prompt = (f"Generate a list of {amount} quiz questions along with their correct answers. Ensure that the questions are relevant to the educational "
              f"context and focus on key concepts.")


    if round_specific_instructions:
        prompt += (f"Additionally, for this round of question generation, follow these "
                   f"specific instructions: {round_specific_instructions}.")
        prompt += "Ensure that each generated question adheres to all the instructions provided."

    if existing_questions:
        prompt += "The following questions are already in the quiz. Avoid duplicating them:"
        for question in existing_questions:
            prompt += f"Question: {question.question_text}, Correct Answer: {question.correct_answer}."

   
    prompt += "Avoid generating random trivia questions."


    return prompt

