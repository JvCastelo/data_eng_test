#!/usr/bin/env python3
"""
Script de teste para a autenticação por API Key.
Execute este script após iniciar o servidor com: uvicorn main:app --reload
"""

import requests

# Configuração
BASE_URL = "http://localhost:8000"
API_KEY = "bxaVbYE34pBWA5jDE5X3RPazdkXLZvDcwUdCQbyhxmM"  # Use a API key criada


def test_auth():
    """Testa a autenticação da API"""

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    print("🔐 Testando autenticação da API...")
    print(f"URL Base: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    print("-" * 50)

    # 1. Verificar API Key
    print("1. Verificando API Key...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/verify", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Key válida!")
            print(f"   Usuário: {data['username']} (ID: {data['user_id']})")
            print(f"   Mensagem: {data['message']}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

    print()

    # 2. Testar endpoint protegido (campos)
    print("2. Testando endpoint protegido (campos)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data/fields", headers=headers)
        if response.status_code == 200:
            fields = response.json()
            print("✅ Campos obtidos com sucesso!")
            print(f"   Campos disponíveis: {fields}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

    print()

    # 3. Testar sem autenticação (deve falhar)
    print("3. Testando sem autenticação (deve falhar)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data/fields")
        if response.status_code == 401:
            print("✅ Autenticação obrigatória funcionando!")
            print(f"   Erro esperado: {response.json()}")
        else:
            print(f"❌ Erro inesperado: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

    print()
    print("🎉 Teste de autenticação concluído!")


if __name__ == "__main__":
    test_auth()
