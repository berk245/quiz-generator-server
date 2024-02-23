def serialize_quiz_source(quiz_sources):
    serialized = []
    for quiz_source in quiz_sources:
        serialized.append(
            {
                "quiz_source_id": quiz_source.quiz_source_id,
                "source_id": quiz_source.source_id,
                "quiz_id": quiz_source.quiz_id,
                "created_at": quiz_source.created_at.isoformat() if quiz_source.created_at else None,
            }
        )
    return serialized


def serialize_source(sources):
    serialized = []
    for source in sources:
        serialized.append(
            {
                "source_id": source.source_id,
                "file_name": source.file_name,
                "file_hash": source.file_hash,
                "created_at": source.created_at.isoformat() if source.created_at else None,
            }
        )
    return serialized
