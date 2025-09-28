# personality_agent/node.py
from typing import Dict, TypedDict, Optional
from .state import AgentState
from .prompts import ALL_GENERATE_PROMPT
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import LLMFactory, DEEPSEEK_V3_1_CONFIG

class InputSchema(TypedDict, total=False):
    type: str
    country: str
    content_type: str
    gender: str
    profile_pic: str
    nickname: str
    mbti: str
    about_me: str
    Others: Optional[str]

class OutputSchema(TypedDict, total=False):
    output: str

def generate_all(state: AgentState) -> OutputSchema:
    """
    一键全部生成逻辑
    """
    llm = LLMFactory.get_model(DEEPSEEK_V3_1_CONFIG)

    chain = ALL_GENERATE_PROMPT | llm
    creator_info_dict = {}
    for field in InputSchema.__annotations__:
        if field in state:
            creator_info_dict[field] = state[field]
    
    creator_info = "\n".join([f"{key}: {value}" for key, value in creator_info_dict.items()])
    print(f"Creator info:\n{creator_info}")
    
    result = chain.invoke(
        {
            "creator_info": creator_info,
        }
    )
    
    # 处理不同类型的返回值
    if hasattr(result, 'content'):
        output_text = result.content
    else:
        output_text = str(result)
    
    return {
        "output": output_text
    }

def generate_single(state: AgentState) -> OutputSchema:
    """
    单条生成逻辑
    """
    content_type = state.get("content_type", "unknown")
    return {
        "output": f"生成单条内容: {content_type} for {state.get('nickname', 'Unknown')}"
    }

def fallback_node(state: AgentState) -> OutputSchema:
    """
    默认逻辑（防止 type 不合法时的兜底）
    """
    return {
        "output": "未知的生成类型，请检查 state['type']"
    }
