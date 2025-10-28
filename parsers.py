from langchain_core.output_parsers import JsonOutputParser
from states import *

type_parser = JsonOutputParser(pydantic_object=TypeModel)
task_parser = JsonOutputParser(pydantic_object=TaskModel)
