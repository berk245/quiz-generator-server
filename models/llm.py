from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class GeneratedQuestion(BaseModel):
    question_id: str = Field(description='A unique identifier for each generated question.')
    question_text: str = Field(description="The question to be added to the quiz. If you can't generate a question from"
                                           "the context, just leave it blank. Do not make up trivia questions.")
    multiple_choices: str = Field(description="A string that includes four potential answers to the "
                                              "question. Identifiers should be A) B) C) and D)")
    correct_answer: str = Field(description='Correct answer to the question. Must be one of the four multiple choices.')
    difficulty: str = Field(description='The proposed difficulty of the question. Only possible options are easy, '
                                        'medium, hard')
    score: str = Field(description='A value from 0 to 5 representing the question quality. 5 being the best quality.')
    question_type: str = Field(default='multi', description='Question type. Always multi for multiple choice questions.')
    

class GeneratedQuestions(BaseModel):
    questions: List[GeneratedQuestion] = Field(description="List of generated questions in the specified amount")

