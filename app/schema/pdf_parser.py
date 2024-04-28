from typing import List
from pydantic import BaseModel


class ParserSchema(BaseModel):
    base64_code: List[str]      # base64 编码, 支持批量，但是会比较慢
    code_of: str                # eg. pdf、picture
    extract_method: str         # eg. best、fast
