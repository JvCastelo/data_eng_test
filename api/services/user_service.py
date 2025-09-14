import hashlib
import secrets

from sqlalchemy.orm import Session

from models.data import ApiKey, User


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def generate_api_key(self, user_id: int, description: str):
        # 1. Gera uma chave segura e aleatória
        api_key_plain = secrets.token_urlsafe(32)

        # 2. Cria o hash da chave
        hashed_key = hashlib.sha256(api_key_plain.encode()).hexdigest()

        # 3. Salva o HASH no banco de dados
        try:
            new_db_key = ApiKey(
                user_id=user_id, hashed_key=hashed_key, description=description
            )
            self.session.add(new_db_key)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        # 4. Retorna a chave original para o usuário APENAS NESTE MOMENTO.
        # Você nunca mais poderá recuperá-la.
        return api_key_plain

    # def get_user_by_api_key(self, api_key: str):
    #     return self.session.query(ApiKey).filter(ApiKey.hashed_key == api_key).first()

    def get_user_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()
