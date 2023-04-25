from pydantic import BaseModel


class SerializableTextData(BaseModel):
    name: str
    description: str
    txt: str


class SerializablePydanticModels(BaseModel):
    """A model intented to contain jsonable test data.

    You should be able to reconstitute a pydantic object with the data_type string and
    the data from json.loads. A factory method will likely be required to lookup an
    object constructor from the data_type string.
    """

    name: str
    description: str
    data_type: str
    data: list[BaseModel]
