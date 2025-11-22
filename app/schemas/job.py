from pydantic import BaseModel

class JobRequest(BaseModel):
    module_code: str
    phpsessid: str
    sucuri_cookie: str
