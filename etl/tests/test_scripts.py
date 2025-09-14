"""
Testes essenciais para scripts auxiliares.
"""

import pytest

from models.data import Signal


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
        """Testa população de sinais."""
        # Simula o script populate_signals
        base_signals = ["test_signal"]
        suffixes = ["mean", "min"]

        all_signals = []
        for base in base_signals:
            for suffix in suffixes:
                all_signals.append(f"{base}_{suffix}")

        # Adiciona sinais
        signals_to_add = [Signal(name=name) for name in all_signals]
        test_session.add_all(signals_to_add)
        test_session.commit()

        # Verifica que foram adicionados
        count = (
            test_session.query(Signal).filter(Signal.name.like("test_signal_%")).count()
        )
        assert count == 2
