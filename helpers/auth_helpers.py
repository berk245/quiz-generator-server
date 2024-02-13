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


def validate_jwt(token):
    try:
        print('Parsing token', token)
        decoded_token = jwt.decode(token, 'secret', algorithms=["HS256"])

        # Retrieve and return the user_id from the decoded token
        user_id = decoded_token.get("user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        # Handle token expiration
        return None
    except jwt.InvalidTokenError:
        # Handle invalid token
        return None
