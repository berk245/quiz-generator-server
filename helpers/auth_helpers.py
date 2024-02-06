import bcrypt


def hash_password(password):
    salt = bcrypt.gensalt()
    encoded_password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password=encoded_password, salt=salt)
    return hashed_password
