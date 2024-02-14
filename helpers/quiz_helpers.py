def serialize_quiz(quiz):
    return {
        "quiz_id": quiz.quiz_id,
        "user_id": quiz.user_id,
        "quiz_title": quiz.quiz_title,
        "quiz_description": quiz.quiz_description,
        "meta_prompt": quiz.meta_prompt,
        "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
        "is_active": quiz.is_active,
    }
