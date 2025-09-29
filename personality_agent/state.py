# state.py
from typing import TypedDict, Optional

class AgentState(TypedDict, total=False):
    type: str
    country: str
    content_type: str
    gender: str
    profile_pic: str
    nickname: str
    mbti: str
    about_me: str
    Others: Optional[dict]
    output: Optional[str]  