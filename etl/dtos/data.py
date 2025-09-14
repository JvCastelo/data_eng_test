from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DataBase(BaseModel):
    """
    Esquema base para 'Data', com os campos comuns.
    """

    ts: datetime
    value: float | None = None


class DataCreate(DataBase):
    """
    Esquema usado para criar um novo registro na tabela 'data'.
    O signal_id será fornecido ao criar o registro.
    """

    signal_id: int


class Data(DataBase):
    """
    Esquema usado para ler dados do banco (respostas da API).
    Inclui todos os campos da tabela, incluindo a chave estrangeira e o created_at.
    """

    signal_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SignalBase(BaseModel):
    """
    Esquema base para 'Signal'.
    """

    name: str = Field(..., max_length=255)


class SignalCreate(SignalBase):
    """
    Esquema usado para criar um novo sinal.
    O 'id' é gerado pelo banco, então não é necessário aqui.
    """

    pass


class Signal(SignalBase):
    """
    Esquema para ler um sinal do banco.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class SignalWithData(Signal):
    """
    Um esquema mais completo que representa um Sinal e todos os seus
    pontos de dados associados. Útil para endpoints que retornam
    um objeto completo.
    """

    data_points: list[Data] = []
