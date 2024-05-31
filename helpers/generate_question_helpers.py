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
    quiz, amount, round_specific_instructions = _parse_generation_settings(question_generation_settings,
                                                                                     user_id=user_id,
                                                                                     db=db)
    _validate_inputs_and_authorization(quiz=quiz, amount=amount)

    existing_questions = db.query(Question).filter(Question.quiz_id == quiz.quiz_id).all()

    prompt = _get_prompt(amount=amount, quiz=quiz, existing_questions=existing_questions, round_specific_instructions=round_specific_instructions)
    chain = _get_chain(quiz=quiz)

    raw_response = chain.invoke(prompt)

    questions = _parse_questions(response=raw_response)

    for q in questions:
        ''' Generate a random id for each generated question. LLM is instructed to do this as well.
        This is for extra security and decoupling from the LLM, which may fail to provide a unique id at times.'''
        q['question_id'] = str(uuid.uuid4())
        q['question_type'] = 'multi' # TODO: handle different types when implemented
        if int(q['score']) > 5 or  int(q['score']) < 1:
             q['score'] = '3'
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
    model = ChatOpenAI(model_name='gpt-4', temperature=0.9).bind_tools([GeneratedQuestions]) 
    # TODO: Uncomment the above line to set model to GPT-4 before tests
    # model = ChatOpenAI(temperature=0.9).bind_tools([GeneratedQuestions])

    chain = (
        {"context": retriever, 'question': RunnablePassthrough()}
        | prompt
        | model
        | JsonOutputToolsParser()
    )

    cloudwatch_logger.info(f'Chain successfully created')
    
    return chain



def _get_template(quiz: Quiz):
    template = (
        "You are assisting educators in creating quiz questions from teaching materials. "
        "Ensure questions are relevant to the educational context and focused on key concepts. "
    )
    
    template += (
        "\n\nCreate questions based on the following context:\n"
        "{context}\n"
        "\nQuestion: {question}"
    )
    
    return template


def _parse_generation_settings(question_generation_settings, user_id: str, db: Session):
    try:
        quiz_id = question_generation_settings.get('quiz_id')
        amount = question_generation_settings.get('amount')
        round_specific_instructions = question_generation_settings.get('instructions')

        quiz = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.quiz_id == quiz_id).first()

        cloudwatch_logger.info(f' Succesfully parsed question generation settings')
        return quiz, amount, round_specific_instructions
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


def _get_prompt(amount, quiz:Quiz, existing_questions: list[Question], round_specific_instructions=None):

    prompt = (
        f"Generate {amount} multiple choice questions along with their correct answers. "
    )
    if quiz.learning_objectives:
        prompt += f"\n\n Focus on these learning objectives {quiz.learning_objectives}\n. Make sure that all generated questions align well with them."
    
    if quiz.keywords:
        prompt += f"\n\n Pay special attention to these keywords and concepts: {', '.join(quiz.keywords)}."
    
    if quiz.meta_prompt:
        prompt += f"\n\n{quiz.meta_prompt}\n"

    if round_specific_instructions:
        prompt += (
            f"{round_specific_instructions}. Ensure that each generated question adheres to all these instructions."
        )

    if existing_questions:
        prompt += "\n\nThe following questions are already in the quiz. Avoid duplicating them:\n"
        for question in existing_questions:
            prompt += f"Question: {question.question_text}, Correct Answer: {question.correct_answer}.\n"

    prompt += (
        "\nExclude irrelevant details such as research questions, methods, authors, table of contents, chapter titles and contents, etc. "
        "\nFocus on generating questions that will be in an assessment to test the understanding of the provided material."
    )
    
    prompt += (
        "\nIdentifiers in multiple choices shoud be A), B), C), D). Separate choices with a comma and a space. "
    )
    
    prompt += (
        "Focus on creating questions directly related to the educational material provided in the context."
        "Generate ONLY high quality questions that can be used in real world assesments with clear and formal language, correct grammar, plausible distractors, and a single correct answer."
        "Do not generate questions with obvious answers. Do not generate questions where the question imply the answer."
        "Ensure that none of the multiple choice questions include 'Both' or 'Neither' as potential answers. Always make sure to create 3 plausible distractors for each question."
        "Limit the use of 'All of the above', 'None of the above', 'Both B and C' type of distractors."
        "In case there is no context to generate questions from, just output 'No relevant context' as question, and 'N/A' as answers."
        "Never generate random, irrelevant questions."
    )

    return prompt


