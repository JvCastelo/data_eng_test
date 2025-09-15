from typing import List

from dtos import Data as DataDTO
from dtos import Signal as SignalDTO
from dtos import SignalWithData as SignalWithDataDTO
from models import Data as DataModel
from models import Signal as SignalModel


def to_signal_dto(model: SignalModel) -> SignalDTO:
    return SignalDTO.model_validate(model)


def to_signal_dto_list(models: List[SignalModel]) -> List[SignalDTO]:
    return [to_signal_dto(model) for model in models]


def to_signal_with_data_dto(model: SignalModel) -> SignalWithDataDTO:
    return SignalWithDataDTO.model_validate(model)


def to_data_dto(model: DataModel) -> DataDTO:
    return DataDTO.model_validate(model)


def to_data_dto_list(models: List[DataModel]) -> List[DataDTO]:
    return [to_data_dto(model) for model in models]
