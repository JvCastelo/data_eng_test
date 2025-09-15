from dtos.data import DataSchema as DataDTO
from models.data import Data as DataModel


def to_dto(data_model: DataModel) -> DataDTO:
    return DataDTO.model_validate(data_model)
