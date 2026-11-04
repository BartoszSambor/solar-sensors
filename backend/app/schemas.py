from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Serialized with camelCase keys; accepts snake_case too."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
