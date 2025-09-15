import argparse
import hashlib
import secrets

from db import SessionLocal
from models.data import ApiKey


def create_api_key(user_id: int, description: str):

    session = SessionLocal()

    try:
        existing_api_key = (
            session.query(ApiKey).filter(ApiKey.user_id == user_id).first()
        )
        if existing_api_key:
            print(f"Erro: A chave API '{user_id}' já existe.")
            return

        api_key_plain = secrets.token_urlsafe(32)

        hashed_key = hashlib.sha256(api_key_plain.encode()).hexdigest()

        new_api_key = ApiKey(
            user_id=user_id, hashed_key=hashed_key, description=description
        )

        session.add(new_api_key)
        session.commit()
        session.refresh(new_api_key)

        print(f"Sucesso! Chave API criada com o ID: {new_api_key.id}")
        print(f"API Key: {api_key_plain}")
        print(
            "IMPORTANTE: Salve esta chave em local seguro! Ela não será mostrada novamente."
        )

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

        session.rollback()

    finally:

        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cria uma nova chave API no banco de dados."
    )
    parser.add_argument(
        "user_id", type=int, help="O ID do usuário a ser criado a chave API."
    )
    parser.add_argument("description", type=str, help="A descrição da chave API.")

    args = parser.parse_args()

    create_api_key(args.user_id, args.description)
