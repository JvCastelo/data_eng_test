#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "bxaVbYE34pBWA5jDE5X3RPazdkXLZvDcwUdCQbyhxmM"


def test_auth():

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    print("Testando autenticação da API...")
    print(f"URL Base: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    print("-" * 50)

    print("Verificando API Key...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/verify", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("API Key válida!")
            print(f"   Usuário: {data['username']} (ID: {data['user_id']})")
            print(f"   Mensagem: {data['message']}")
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

    print()

    print("Testando endpoint protegido (campos)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data/fields", headers=headers)
        if response.status_code == 200:
            fields = response.json()
            print("Campos obtidos com sucesso!")
            print(f"   Campos disponíveis: {fields}")
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

    print()

    print("Testando sem autenticação (deve falhar)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data/fields")
        if response.status_code == 401:
            print("Autenticação obrigatória funcionando!")
            print(f"   Erro esperado: {response.json()}")
        else:
            print(f"Erro inesperado: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

    print("Teste de autenticação concluído!")


if __name__ == "__main__":
    test_auth()
