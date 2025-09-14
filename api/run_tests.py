#!/usr/bin/env python3
"""
Script para executar os testes da API.
"""

import subprocess
import sys


def run_tests():
    """Executa todos os testes."""
    print("🧪 Executando testes da API...")
    print("=" * 50)

    try:
        # Executa pytest com verbose
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Exit code: {result.returncode}")

        if result.returncode == 0:
            print("✅ Todos os testes passaram!")
        else:
            print("❌ Alguns testes falharam!")

    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")


def run_specific_test(test_path):
    """Executa um teste específico."""
    print(f"🧪 Executando teste específico: {test_path}")
    print("=" * 50)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Exit code: {result.returncode}")

    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Executa teste específico
        test_path = sys.argv[1]
        run_specific_test(test_path)
    else:
        # Executa todos os testes
        run_tests()
