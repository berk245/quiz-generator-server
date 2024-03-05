from sqlalchemy.orm import Session

from database.db_models import Quiz
from starlette.exceptions import HTTPException
from helpers import vectorstore_helpers
import uuid
CHAIN_CACHE = {}


def get_generated_questions(user_id: str, question_generation_settings, db: Session):
    quiz, amount, instructions, keywords = _parse_generation_settings(question_generation_settings, user_id=user_id,
                                                                      db=db)
    _validate_inputs_and_authorization(quiz=quiz, amount=amount)

    chain = _get_chain(quiz=quiz)

    raw_response = chain.invoke(_get_prompt(amount, keywords, instructions))
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
    instructions = question_generation_settings.get('instructions')
    keywords = question_generation_settings.get('keywords')

    quiz = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.quiz_id == quiz_id).first()

    return quiz, amount, instructions, keywords


def _get_prompt(amount, keywords=None, instructions=None):
    prompt = (f"Generate a list of {amount} quiz questions along with their correct answers. "
              f"Make sure to have the exact amount of results!")
    prompt += "This tool is designed to assist teachers in creating quiz questions efficiently."
    prompt += "Do NOT include any identifiers in multiple choices, such as A), B), C) etc or 1,2,3."
    prompt += "Just include the potential answers without anything else."

    if keywords:
        prompt += f" Focus on the following keywords: {', '.join(keywords)}."

    if instructions:
        prompt += f" Follow the provided instructions: {instructions}."

    prompt += "Ensure that the generated questions are relevant in a quiz context, excluding irrelevant details such as"
    prompt += "research questions, methods, table of contents, authors, and the purpose of sections in the documents."

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
