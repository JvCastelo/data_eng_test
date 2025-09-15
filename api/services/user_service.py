import hashlib
import secrets

from models.data import ApiKey, User
from sqlalchemy.orm import Session


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def generate_api_key(self, user_id: int, description: str):

        api_key_plain = secrets.token_urlsafe(32)

        hashed_key = hashlib.sha256(api_key_plain.encode()).hexdigest()

        try:
            new_db_key = ApiKey(
                user_id=user_id, hashed_key=hashed_key, description=description
            )
            self.session.add(new_db_key)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return api_key_plain

    def get_user_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()
