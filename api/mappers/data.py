from api.dtos.data import DataSchema as DataDTO
from api.models.data import Data as DataModel


def to_dto(data_model: DataModel) -> DataDTO:
    """
    Converte um objeto do modelo SQLAlchemy (DataModel) para um DTO Pydantic (DataDTO).

    """
    return DataDTO.model_validate(data_model)
