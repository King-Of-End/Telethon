from langchain_core.output_parsers import JsonOutputParser
from states import *

type_parser = JsonOutputParser(pydantic_object=TypeModel)

__all__ = [
    'type_parser',
]