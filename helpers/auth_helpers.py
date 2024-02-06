import bcrypt
import jwt


def hash_password(password):
    salt = bcrypt.gensalt()
    encoded_password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password=encoded_password, salt=salt)
    return hashed_password


def verify_password(hashed_password, input_password):
    hashed_password_bytes = hashed_password.encode('utf-8')  # Convert the stored hash to bytes
    input_password_bytes = input_password.encode('utf-8')
    return bcrypt.checkpw(input_password_bytes, hashed_password_bytes)


def create_jwt(login_user):
    user_info = {
        "user_id": login_user.user_id,
        "email": login_user.email
    }

    return jwt.encode(user_info, "secret", algorithm="HS256")
