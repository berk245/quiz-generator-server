from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class GeneratedQuestion(BaseModel):
    question_id: str = Field(description='A unique identifier for each generated question.')
    question_text: str = Field(description="The question to be added to the quiz")
    multiple_choices: str = Field(description="A string that includes four, comma separated potential answers to the "
                                              "question")
    correct_answer: str = Field(description='Correct answer to the question. Must be one of the four multiple choices.')
    difficulty: str = Field(description='The proposed difficulty of the question. Only possible options are easy, medium, hard')
    score: str = Field(description='The score of the question, defining the question quality. A value from 0 to 5, 5 being the best quality.')
    question_type: str = Field(description='Always set it as "multi"')
    

class GeneratedQuestions(BaseModel):
    questions: List[GeneratedQuestion] = Field(description="List of generated questions in the specified amount")

