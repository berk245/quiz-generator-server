from pydantic import BaseModel


class CreateQuizRequest(BaseModel):
    quiz_name: str
    quiz_description: str
    keywords: str
    meta_prompts: str


