import pydantic
import pydantic_settings

for package in (pydantic, pydantic_settings):
    if package is None:
        raise RuntimeError("Not found pydantic or pydantic_settings package")

from .rabbit import RabbitSettings
from .services import ServicesSettings
