import argparse

from db import SessionLocal
from models.data import User


def create_user(username: str):
    """
    Cria um novo usuário no banco de dados.

    Args:
        username: O nome de usuário a ser criado.
    """

    session = SessionLocal()

    try:
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"Erro: O usuário '{username}' já existe.")
            session.close()
            return

        new_user = User(username=username)

        session.add(new_user)
        session.commit()
        session.refresh(new_user)  # Atualiza o objeto com o ID gerado

        print(f"Sucesso! Usuário '{username}' criado com o ID: {new_user.id}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

        session.rollback()

    finally:

        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cria um novo usuário no banco de dados."
    )
    parser.add_argument("username", type=str, help="O nome de usuário a ser criado.")

    args = parser.parse_args()

    create_user(args.username)
