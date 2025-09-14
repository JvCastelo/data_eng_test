from services import SignalService

# Sinais base - apenas os nomes principais
base_signals = ["wind_speed", "power", "ambient_temperature"]

# Sufixos para as agregações (deve coincidir com o pandas)
suffixes = ["mean", "min", "max", "std"]

# Gera automaticamente todos os sinais
all_signals = []
for base in base_signals:
    for suffix in suffixes:
        all_signals.append(f"{base}_{suffix}")

signal_service = SignalService()
session = signal_service.get_session()

try:
    # Busca sinais existentes usando o serviço
    existing_signals = set(signal_service.get_all_names(session))

    # Identifica apenas os sinais que precisam ser adicionados
    new_signals = [name for name in all_signals if name not in existing_signals]

    # Adiciona todos os novos sinais de uma vez usando o serviço
    if new_signals:
        signals_data = [{"name": name} for name in new_signals]
        created_signals = signal_service.create_many(session, signals_data)
        if created_signals:
            print(
                f"{len(new_signals)} novos sinais adicionados: {', '.join(new_signals)}"
            )
        else:
            print("Erro ao criar sinais")
    else:
        print("Todos os sinais já existem")

    print(f"Processo concluído!")

except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
