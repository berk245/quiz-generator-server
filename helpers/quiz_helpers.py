import hashlib


def serialize_quiz(quiz):
    return {
        "quiz_id": quiz.quiz_id,
        "user_id": quiz.user_id,
        "quiz_title": quiz.quiz_title,
        "quiz_description": quiz.quiz_description,
        "keywords": quiz.keywords,
        "meta_prompt": quiz.meta_prompt,
        "learning_objectives": quiz.learning_objectives,
        "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
        "is_active": quiz.is_active,
    }


def get_file_hash(file: any, algorithm: str = 'sha256') -> str:
    hash_obj = hashlib.new(algorithm)
    if isinstance(file, str):
        hash_obj.update(file.encode())
    else:
        for chunk in iter(lambda: file.read(4096), b''):
            hash_obj.update(chunk)
        file.seek(0)
    return hash_obj.hexdigest()