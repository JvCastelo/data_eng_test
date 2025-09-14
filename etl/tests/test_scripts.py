"""
Testes essenciais para scripts auxiliares.
"""

import pytest

from services import SignalService


class TestScripts:
    """Testes essenciais para scripts."""

    @pytest.mark.unit
    def test_signal_generation(self):
        """Testa geração automática de nomes de sinais."""
        base_signals = ["wind_speed", "power"]
        suffixes = ["mean", "min"]

        expected_signals = [
            "wind_speed_mean",
            "wind_speed_min",
            "power_mean",
            "power_min",
        ]

        all_signals = []
        for base in base_signals:
            for suffix in suffixes:
                all_signals.append(f"{base}_{suffix}")

        assert all_signals == expected_signals

    @pytest.mark.database
    def test_populate_signals(self, test_session):
        """Testa população de sinais usando SignalService."""
        signal_service = SignalService()

        # Simula o script populate_signals
        base_signals = ["test_signal"]
        suffixes = ["mean", "min"]

        all_signals = []
        for base in base_signals:
            for suffix in suffixes:
                all_signals.append(f"{base}_{suffix}")

        # Adiciona sinais usando o serviço
        signals_data = [{"name": name} for name in all_signals]
        created_signals = signal_service.create_many(test_session, signals_data)

        assert len(created_signals) == 2

        # Verifica que foram adicionados usando o serviço
        signal_names = signal_service.get_all_names(test_session)
        test_signal_names = [
            name for name in signal_names if name.startswith("test_signal_")
        ]
        assert len(test_signal_names) == 2
