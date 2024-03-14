from sqlalchemy.orm import Session

from database.db_models import Quiz, Question
from starlette.exceptions import HTTPException
from helpers import vectorstore_helpers
import uuid

CHAIN_CACHE = {}


def get_generated_questions(user_id: str, question_generation_settings, db: Session):
    quiz, amount, round_specific_instructions, keywords = _parse_generation_settings(question_generation_settings,
                                                                                     user_id=user_id,
                                                                                     db=db)
    _validate_inputs_and_authorization(quiz=quiz, amount=amount)

    existing_questions = db.query(Question).filter(Question.quiz_id == quiz.quiz_id).all()

    chain = _get_chain(quiz=quiz)
    prompt = _get_prompt(amount=amount, keywords=keywords, quiz=quiz, existing_questions=existing_questions,
                         round_specific_instructions=round_specific_instructions)
    raw_response = chain.invoke(prompt)
    questions = _parse_questions(response=raw_response)

    for q in questions:
        # Generate a random id for each generated question
        # LLM is instructed to do this as well. This is for extra security and decoupling from the LLM, which
        # may fail to provide a unique id at times.
        q['question_id'] = str(uuid.uuid4())
    return questions


def _parse_generation_settings(question_generation_settings, user_id: str, db: Session):
    quiz_id = question_generation_settings.get('quiz_id')
    amount = question_generation_settings.get('amount')
    round_specific_instructions = question_generation_settings.get('instructions')
    keywords = question_generation_settings.get('keywords')

    quiz = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.quiz_id == quiz_id).first()

    return quiz, amount, round_specific_instructions, keywords


def _get_prompt(amount, quiz: Quiz, existing_questions: list[Question], keywords=None,
                round_specific_instructions=None):
    global_quiz_instructions = quiz.meta_prompt

    prompt = (f"Generate a list of {amount} quiz questions along with their correct answers, for a tool that helps "
              f"educators create quiz questions efficiently. Make sure to have the exact amount of results and"
              f"limit your answers to the content you have just received!")

    if global_quiz_instructions:
        prompt += f"This quiz includes global instructions that apply to all question sets: {global_quiz_instructions}\n"

    if round_specific_instructions:
        prompt += (f"In addition, there are some specific instructions that should be applied only to this round of "
                   f"question generation. Be sure to follow them: {round_specific_instructions}.")
        prompt += "Ensure that each generated question adheres to all the instructions mentioned above."

    if keywords:
        prompt += f" While generating questions, pay special attention and focus to the following keywords and concepts: {', '.join(keywords)}."

    if existing_questions:
        prompt += 'The following is a list of questions that are already in the quiz. Please do not have duplicate quesitons.'
        for question in existing_questions:
            prompt += f'Question: {question.question_text}, correct answer: {question.correct_answer}.'

    prompt += "Ensure that the generated questions are relevant in a quiz context, excluding irrelevant details such as"
    prompt += "research questions, methods, table of contents, authors, and the purpose of sections in the documents."

    prompt += "Do NOT include any identifiers in multiple choices or numbering (A), B), C) etc or 1,2,3)."
    prompt += "Just include the potential answers without anything else."

    return prompt


def _validate_inputs_and_authorization(quiz: Quiz | None, amount: str):
    if amount is None:
        raise HTTPException(status_code=400, detail="Bad request.")
    if not quiz:
        raise HTTPException(detail='Quiz not found', status_code=404)

    return True


def _get_chain(quiz: Quiz | None):
    global CHAIN_CACHE
    if quiz.quiz_id in CHAIN_CACHE:
        # Get chain from cache
        chain = CHAIN_CACHE[quiz.quiz_id]
    else:
        # Initialize chain and cache
        chain = vectorstore_helpers.get_conversation_chain(quiz=quiz)
        CHAIN_CACHE[quiz.quiz_id] = chain
    return chain


def _parse_questions(response):
    return response[0].get('args').get('questions')
