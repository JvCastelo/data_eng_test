from db import SessionLocal
from models.data import Signal

# Sinais base - apenas os nomes principais
base_signals = ["wind_speed", "power", "ambient_temperature"]

# Sufixos para as agregações (deve coincidir com o pandas)
suffixes = ["mean", "min", "max", "std"]

# Gera automaticamente todos os sinais
all_signals = []
for base in base_signals:
    for suffix in suffixes:
        all_signals.append(f"{base}_{suffix}")

session = SessionLocal()

try:
    # UMA ÚNICA query para buscar apenas os sinais que queremos verificar
    existing_signals = {
        s.name
        for s in session.query(Signal.name).filter(Signal.name.in_(all_signals)).all()
    }

    # Identifica apenas os sinais que precisam ser adicionados
    new_signals = [name for name in all_signals if name not in existing_signals]

    # Adiciona todos os novos sinais de uma vez
    if new_signals:
        signals_to_add = [Signal(name=name) for name in new_signals]
        session.add_all(signals_to_add)
        print(f"{len(new_signals)} novos sinais adicionados: {', '.join(new_signals)}")
    else:
        print("Todos os sinais já existem")

    session.commit()
    print(f"Processo concluído!")

except Exception as e:
    session.rollback()
    print(f"Error: {e}")
finally:
    session.close()
