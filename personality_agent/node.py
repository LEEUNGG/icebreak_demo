# node.py
from typing import Dict
from common.models import LLMFactory, OPENAI_CONFIG
from .prompts import ALL_GENERATE_PROMPT, ALL_RE_GENERATE_PROMPT, SINGLE_GENERATE_PROMPT, SINGLE_RE_GENERATE_PROMPT
from .constants import CREATOR_FIELD_MAPPING 
from .state import AgentState

def regenerate_all(state: AgentState) -> Dict:
    """
    重新生成全部内容逻辑
    """
    llm = LLMFactory.get_model(OPENAI_CONFIG)
    chain = ALL_RE_GENERATE_PROMPT | llm
    
    creator_info_dict = {}
    fields = ["type", "country", "content_type", "gender", "profile_pic", 
              "nickname", "mbti", "about_me"]
    
    for field in fields:
        if field in state and state[field]:
            creator_info_dict[field] = state[field]
    
    creator_info = "\n".join([f"{key}: {value}" for key, value in creator_info_dict.items()])
    previous_version = str(state.get("Others", ""))
    
    result = chain.invoke({
        "previous_version": previous_version,
        "creator_info": creator_info
        })
    if hasattr(result, 'content'):
        output_text = result.content
    else:
        output_text = str(result)
    
    return {"output": output_text}

def generate_all(state: AgentState) -> Dict:
    """
    一键全部生成逻辑
    """
    llm = LLMFactory.get_model(OPENAI_CONFIG)
    chain = ALL_GENERATE_PROMPT | llm
    creator_info_dict = {}
    fields = ["type", "country", "content_type", "gender", "profile_pic", 
              "nickname", "mbti", "about_me", "Others"]
    
    for field in fields:
        if field in state and state[field]:
            creator_info_dict[field] = state[field]
    
    creator_info = "\n".join([f"{key}: {value}" for key, value in creator_info_dict.items()])
    
    result = chain.invoke({"creator_info": creator_info})
    
    if hasattr(result, 'content'):
        output_text = result.content
    else:
        output_text = str(result)
    
    return {"output": output_text}

def generate_single(state: AgentState) -> Dict:
    """
    单条生成逻辑
    """
    llm = LLMFactory.get_model(OPENAI_CONFIG)
    chain = SINGLE_GENERATE_PROMPT | llm

    type = state.get("type", "unknown")
    combined_info = ""
    if type in CREATOR_FIELD_MAPPING:
        explanation = CREATOR_FIELD_MAPPING[type].get("explanation", "")
        examples = CREATOR_FIELD_MAPPING[type].get("examples", [])

    creator_info_dict = {}
    fields = ["type", "country", "content_type", "gender", "profile_pic", 
              "nickname", "mbti", "about_me", "Others"]
    for field in fields:
        if field in state and state[field]:
            creator_info_dict[field] = state[field]
    creator_info = "\n".join([f"{key}: {value}" for key, value in creator_info_dict.items()]) 

    output_format = f'{{"{type}": ""}}'

    prompt_variables = {
        "creator_info": creator_info,
        "output_key": type,
        "explanation": explanation,
        "examples": examples,
        "output_format": output_format
    }
    
    result = chain.invoke(prompt_variables)
    
    if hasattr(result, 'content'):
        output_text = result.content
    else:
        output_text = str(result)
    
    return {"output": output_text}

def regenerate_single(state: AgentState) -> Dict:
    """
    重新生成单条内容逻辑
    """
    llm = LLMFactory.get_model(OPENAI_CONFIG)
    chain = SINGLE_RE_GENERATE_PROMPT | llm

    type = state.get("type", "unknown")
    combined_info = ""
    if type in CREATOR_FIELD_MAPPING:
        explanation = CREATOR_FIELD_MAPPING[type].get("explanation", "")
        examples = CREATOR_FIELD_MAPPING[type].get("examples", [])

    creator_info_dict = {}
    fields = ["type", "country", "content_type", "gender", "profile_pic", 
              "nickname", "mbti", "about_me", "Others"]
    for field in fields:
        if field in state and state[field]:
            creator_info_dict[field] = state[field]
    creator_info = "\n".join([f"{key}: {value}" for key, value in creator_info_dict.items()]) 

    output_format = f'{{"{type}": ""}}'

    prompt_variables = {
        "creator_info": creator_info,
        "output_key": type,
        "explanation": explanation,
        "examples": examples,
        "output_format": output_format,
        "previous_version": state.get("Others", "")
    }

    print("开始")
    print(prompt_variables)
    print("结束")
    
    result = chain.invoke(prompt_variables)
    
    if hasattr(result, 'content'):
        output_text = result.content
    else:
        output_text = str(result)
    
    return {"output": output_text}
    
    return {
        "output": f"重新生成单条内容: {content_type} for {nickname}",
        "explanation": combined_info  # 返回合并后的信息
    }

def fallback_node(state: AgentState) -> Dict:
    """
    默认逻辑
    """
    return {
        "output": "未知的生成类型，请检查 state['type']"
    }
