from typing import List

from etl.dtos import Data as DataDTO
from etl.dtos import Signal as SignalDTO
from etl.dtos import SignalWithData as SignalWithDataDTO
from etl.models import Data as DataModel
from etl.models import Signal as SignalModel


def to_signal_dto(model: SignalModel) -> SignalDTO:
    """
    Converte um objeto do modelo SQLAlchemy (SignalModel) para um DTO Pydantic (SignalDTO).
    """
    return SignalDTO.model_validate(model)


def to_signal_dto_list(models: List[SignalModel]) -> List[SignalDTO]:
    """
    Converte uma lista de objetos SignalModel para uma lista de SignalDTO.
    """
    return [to_signal_dto(model) for model in models]


def to_signal_with_data_dto(model: SignalModel) -> SignalWithDataDTO:
    """
    Converte um objeto SignalModel para um DTO SignalWithDataDTO, que inclui
    os data_points aninhados.
    """
    return SignalWithDataDTO.model_validate(model)


def to_data_dto(model: DataModel) -> DataDTO:
    """
    Converte um objeto do modelo SQLAlchemy (DataModel) para um DTO Pydantic (DataDTO).
    """
    return DataDTO.model_validate(model)


def to_data_dto_list(models: List[DataModel]) -> List[DataDTO]:
    """
    Converte uma lista de objetos DataModel para uma lista de DataDTO.
    """
    return [to_data_dto(model) for model in models]
