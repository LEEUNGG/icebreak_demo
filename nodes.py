"""
节点函数模块
定义图中各个节点的处理逻辑
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from script_utils import (load_script_from_examples, get_type_by_id, get_node_text_by_id, get_next_node_id, get_node_by_id)  
from state import ConversationState
from models import LLMFactory, DEEPSEEK_V3_1_TERMINUS_CONFIG
from prompts import (
    ENGAGEMENT_CLASSIFIER_LEADER_PROMPT,
    ENGAGEMENT_CLASSIFIER_LISTENER_PROMPT,
    LISTENER_MODE_PROMPT,
    SCRIPT_EXECUTION_MODE_MESSAGE_PROMPT,
    SCRIPT_EXECUTION_MODE_REACTION_PROMPT,
    SCRIPT_EXECUTION_MODE_CHOICE_ASK_PROMPT,
    SCRIPT_EXECUTION_MODE_CHOICE_BRANCH_PROMPT,
    SCRIPT_EXECUTION_MODE_ACTION_PROMPT
)
import logging
import requests

logger = logging.getLogger(__name__)

def user_input_node(state: ConversationState) -> Dict[str, Any]:
    user_input = state.get("user_input", "")
    if user_input:
        user_message = HumanMessage(content=user_input)
        return {
            "messages": [user_message],
            "user_input": None
        }
    return {}

def engagement_classifier_node(state: ConversationState) -> Dict[str, Any]:    
    try:
        messages = state.get("messages", [])
                
        llm = LLMFactory.get_model(DEEPSEEK_V3_1_TERMINUS_CONFIG)

        if state.get("conversation_mode", "leader") == "leader":
            chain = ENGAGEMENT_CLASSIFIER_LEADER_PROMPT | llm
            result = chain.invoke({
                "script_content": state.get("script_content", ""),
                "messages": messages})
        else: 
            chain = ENGAGEMENT_CLASSIFIER_LISTENER_PROMPT | llm
            result = chain.invoke({"messages": messages})
                
        if hasattr(result, 'content'):
            content = result.content.strip().lower()
        else:
            content = str(result).strip().lower()
            
        if "leader" in content:
            mode = "leader"
        elif "listener" in content:
            mode = "listener"
        else:
            mode = "listener"
            logger.warning(f"分类器返回无效结果: {content}，使用默认模式: listener")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"连接API失败: {e}")
        mode = "listener"
    except Exception as e:
        logger.error(f"分类器执行失败: {e}")
        mode = "listener"
    
    logger.debug(f"engagement_classifier_node结果: {mode}")
    
    return {
        "conversation_mode": mode
    }

def maintain_mode_node(state: ConversationState) -> Dict[str, Any]:
    current_mode = state.get("conversation_mode", "listener")
    if not state.get("conversation_mode"):
        logger.debug(f"maintain_mode_node: {current_mode}")  
        return {"conversation_mode": "listener"}

    if state.get("noScript", "false") == "true":
        logger.debug(f"maintain_mode_node: no script any more")
        return {"conversation_mode": "listener"}
    return {"conversation_mode": current_mode}

def listener_node(state: ConversationState) -> Dict[str, Any]:
    try:
        messages = state.get("messages", [])
        llm = LLMFactory.get_model(DEEPSEEK_V3_1_TERMINUS_CONFIG)
        chain = LISTENER_MODE_PROMPT | llm
        response = chain.invoke(
            {
                "messages": messages,  
                "creator_background_info": state.get("creator_background", "")
            }
        ) 
        print(response)
        
        if hasattr(response, 'content'):
            ai_message = AIMessage(content=response.content)
        else:
            ai_message = AIMessage(content=str(response))       
    except requests.exceptions.RequestException as e:
        logger.error(f"连接API失败: {e}")
        mock_response = "很抱歉当前无法连接到模型服务。"
        ai_message = AIMessage(content=mock_response)
    except Exception as e:
        logger.error(f"Listener模式执行失败: {e}")
        mock_response = f"很抱歉，我现在无法回复。让我们重新开始吧！"
        ai_message = AIMessage(content=mock_response)
    logger.debug(f"Listener模式回复: {ai_message.content[:100]}...")
    return {
        "messages": [ai_message],
        "turn_count": state.get("turn_count", 0) + 1
    }

def determine_node_type_node(state: ConversationState) -> Dict[str, Any]:
    """
    节点类型判断节点
    以及加载剧本
    """
    logger.debug("执行节点类型判断")

    if state.get("script") is None:
        logger.debug("剧本不存在，从examples文件夹加载")
        state["script"] = load_script_from_examples()

    current_node_id = state.get("current_node_id", "")
    
    if not current_node_id:
        current_node_id = state["script"][0].get("id", None)
        logger.debug(f"current_node不存在，使用第一个节点: {current_node_id}")

    current_node_type = get_type_by_id(state["script"], current_node_id)

    logger.debug(f"determine_node_type_node结果")
    logger.debug(f"current_node_id: {current_node_id}")
    logger.debug(f"current_node_type: {current_node_type}")
    current_node = get_node_by_id(state["script"], current_node_id)
    logger.debug(f"current_node: {current_node}")
    logger.debug(f"determine_node_type_node结束")
        
    return {
        "current_node_id": current_node_id,
        "script": state["script"],
        "current_node_type": current_node_type
    }

# script mode

def script_execution_message_node(state: ConversationState) -> Dict[str, Any]:  
    try:
        # 获取LLM
        llm = LLMFactory.get_model(DEEPSEEK_V3_1_TERMINUS_CONFIG)
        
        # 构建提示词链
        chain = SCRIPT_EXECUTION_MODE_MESSAGE_PROMPT | llm
        
        creator_background_info = state.get("creator_background", "")
        message = get_node_text_by_id(state.get("script", []), state.get("current_node_id", "")) or ""
        next_node_id = get_next_node_id(state.get("script", []), state.get("current_node_id", ""))
        next_node_type = get_type_by_id(state.get("script", []), next_node_id)
        
    
        response = chain.invoke(
            {
                "creator_background_info": creator_background_info,
                "message": message,
                "messages": state.get("messages", [])
            }
        )        
        
        # 添加AI回复到消息历史
        if hasattr(response, 'content'):
            ai_message = AIMessage(content=response.content)
        else:
            ai_message = AIMessage(content=str(response))
        
    except Exception as e:
        logger.error(f"Script message模式执行失败: {e}")
        mock_response = "很抱歉当前无法连接到模型服务。"
        ai_message = AIMessage(content=mock_response)
        next_node_id = None
        next_node_type = None

    logger.debug(f"历史聊天记录开始")
    logger.debug(f"{state.get('messages', [])}")
    logger.debug(f"历史聊天记录结束")
    logger.debug(f"script_execution_message_node结果")
    logger.debug(f"response: {response}")
    logger.debug(f"next_node_id: {next_node_id}")
    logger.debug(f"next_node_type: {next_node_type}")
    logger.debug(f"script_execution_message_node结束")

    noScript = "true" if next_node_id == "script_end" else "false"

    return {
        "messages": [ai_message],
        "turn_count": state.get("turn_count", 0) + 1,
        "current_node_id": next_node_id,
        "current_node_type": next_node_type,
        "noScript": noScript
    }

def script_execution_reaction_node(state: ConversationState) -> Dict[str, Any]:
    logger.debug("执行剧本模式 - reaction")
  
    try:
        # 获取LLM
        llm = LLMFactory.get_model(DEEPSEEK_V3_1_TERMINUS_CONFIG)
      
        # 构建提示词链
        chain = SCRIPT_EXECUTION_MODE_REACTION_PROMPT | llm
      
        # 获取节点信息，然后只提取conditions部分
        node = get_node_by_id(state.get("script", []), state.get("current_node_id", ""))
        data_from_DB = node.get("conditions", []) if node else []
        
      
        response = chain.invoke(
            {
                "data_from_DB": data_from_DB,
                "messages": state.get("messages", [])
            }
        )
        logger.debug(f"script_execution_reaction_node开始")
        logger.debug(f"当前节点条件: {data_from_DB}")
        logger.debug(f"原始content: {response}")
      
        # 增强的JSON解析
        next_node_id = ""
        if hasattr(response, 'content'):
            content = response.content
            # 尝试修复不完整的JSON
            if content.strip().startswith('{') and not content.strip().endswith('}'):
                content = content.strip()
                if '"next_node": "' in content:
                    import re
                    match = re.search(r'"next_node":\s*"([^"]*)', content)
                    if match:
                        next_node_id = match.group(1)
                        logger.debug(f"从不完整JSON中提取到next_node_id: {next_node_id}")
            else:
                # 尝试完整解析JSON
                try:
                    import json
                    result = json.loads(content)
                    next_node_id = result.get("next_node", "")
                    logger.debug(f"完整JSON解析得到next_node_id: {next_node_id}")
                except json.JSONDecodeError as je:
                    logger.error(f"JSON解析失败: {je}")
                    import re
                    match = re.search(r'"next_node":\s*"([^"]*)"', content)
                    if match:
                        next_node_id = match.group(1)
                        logger.debug(f"正则提取得到next_node_id: {next_node_id}")
          
        next_node_type = get_type_by_id(state.get("script", []), next_node_id) if next_node_id else None

    except Exception as e:
        logger.error(f"Reaction模式执行失败: {e}")
        next_node_id = ""
        next_node_type = None


    logger.debug(f"next_node_id: {next_node_id}")
    logger.debug(f"next_node_type: {next_node_type}")
    logger.debug(f"script_execution_reaction_node结束")

    return {
        "turn_count": state.get("turn_count", 0) + 1,
        "current_node_id": next_node_id,
        "current_node_type": next_node_type
    }

def script_execution_action_node(state: ConversationState) -> Dict[str, Any]:    
    try:
        # 获取LLM
        llm = LLMFactory.get_model(DEEPSEEK_V3_1_TERMINUS_CONFIG)
        
        # 构建提示词链
        chain = SCRIPT_EXECUTION_MODE_ACTION_PROMPT | llm
        
        creator_background_info = state.get("creator_background", "")
        
        # 获取ActionNode的prompt
        node = get_node_by_id(state.get("script", []), state.get("current_node_id", ""))
        message = node.get("parameters", {}).get("prompt", "") if node else ""
        
        next_node_id = get_next_node_id(state.get("script", []), state.get("current_node_id", ""))
        next_node_type = get_type_by_id(state.get("script", []), next_node_id) if next_node_id else None
        
        # 获取用户输入
        user_input = ""
        messages = state.get("messages", [])
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content and msg.__class__.__name__ == "HumanMessage":
                user_input = msg.content
                break
        
        # 过滤空消息
        valid_messages = []
        for msg in messages:
            if hasattr(msg, 'content') and msg.content and msg.content.strip():
                valid_messages.append(msg)
    
        response = chain.invoke(
            {
                "creator_background_info": creator_background_info,
                "message": message,
                "messages": valid_messages
            }
        )        
        
        # 添加AI回复到消息历史
        if hasattr(response, 'content'):
            ai_message = AIMessage(content=response.content)
        else:
            ai_message = AIMessage(content=str(response))
        
    except Exception as e:
        logger.error(f"Action模式执行失败: {e}")
        mock_response = "很抱歉当前无法连接到模型服务。"
        ai_message = AIMessage(content=mock_response)
        next_node_id = None
        next_node_type = None

    logger.debug(f"script_execution_action_node结果")
    logger.debug(f"response: {response}")
    logger.debug(f"next_node_id: {next_node_id}")
    logger.debug(f"next_node_type: {next_node_type}")
    logger.debug(f"script_execution_action_node结束")

    return {
        "messages": [ai_message],
        "turn_count": state.get("turn_count", 0) + 1,
        "current_node_id": next_node_id,
        "current_node_type": next_node_type
    }

def script_execution_choice_branch_node(state: ConversationState) -> Dict[str, Any]:
    try:
        llm = LLMFactory.get_model(DEEPSEEK_V3_1_TERMINUS_CONFIG)
        chain = SCRIPT_EXECUTION_MODE_CHOICE_BRANCH_PROMPT | llm

        node = get_node_by_id(state.get("script", []), state.get("current_node_id", ""))
        branch_info = node.get("branches", []) if node else []

        messages = state.get("messages", [])

        response = chain.invoke(
            {
                "branch_info": branch_info,
                "messages": messages
            }
        )       

        # 解析响应
        if hasattr(response, 'content'):
            import json
            try:
                result = json.loads(response.content)
                next_node_id = result.get("next_node", "")
            except:
                next_node_id = branch_info[0].get("next", "") if branch_info else ""
        else:
            next_node_id = branch_info[0].get("next", "") if branch_info else ""

    except Exception as e:
        logger.error(f"Choice branch模式执行失败: {e}")
        node = get_node_by_id(state.get("script", []), state.get("current_node_id", ""))
        branch_info = node.get("branches", []) if node else []
        next_node_id = branch_info[0].get("next", "") if branch_info else ""

    next_node_type = get_type_by_id(state.get("script", []), next_node_id) if next_node_id else None  

    logger.debug(f"script_execution_choice_node结果_branch_start")
    logger.debug(f"branch_info: {branch_info}")
    logger.debug(f"response:{response}")
    logger.debug(f"⚠️next_node_id: {next_node_id}")
    logger.debug(f"⚠️next_node_type: {next_node_type}")    
    logger.debug(f"script_execution_choice_node结果_branch_end")

    return {
        "current_node_type": next_node_type, 
        "current_node_id": next_node_id,
        "choice_node_status": "ask"
    }

def script_execution_choice_ask_node(state: ConversationState) -> Dict[str, Any]:
    try:
        llm = LLMFactory.get_model(DEEPSEEK_V3_1_TERMINUS_CONFIG)
        chain = SCRIPT_EXECUTION_MODE_CHOICE_ASK_PROMPT | llm

        creator_background_info = state.get("creator_background", "")
        
        # 获取ChoiceNode的prompt
        node = get_node_by_id(state.get("script", []), state.get("current_node_id", ""))
        message = node.get("prompt", "") if node else ""

        messages = state.get("messages", [])
    
        response = chain.invoke(
            {
                "creator_background_info": creator_background_info,
                "message": message,
                "messages": messages
            }
        )        
        
        # 添加AI回复到消息历史
        if hasattr(response, 'content'):
            ai_message = AIMessage(content=response.content)
        else:
            ai_message = AIMessage(content=str(response))
    
    except Exception as e:
        logger.error(f"Choice ask模式执行失败: {e}")
        mock_response = "很抱歉当前无法连接到模型服务。"
        ai_message = AIMessage(content=mock_response)

    logger.debug(f"script_execution_choice_node结果_ask")
    current_node_id = state.get("current_node_id", "")
    current_node_type = state.get("current_node_type", "")
    logger.debug(f"response: {response}")
    logger.debug(f"current_node_id: {current_node_id}")
    logger.debug(f"current_node_type: {current_node_type}")
    logger.debug(f"script_execution_choice_node结束_ask")

    return {
        "messages": [ai_message],
        "turn_count": state.get("turn_count", 0) + 1,
        "choice_node_status": "branch"
    }