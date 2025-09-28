"""
剧本处理模块
负责加载、解析和执行剧本
"""
from typing import List, Dict, Any, Optional
import json
import logging
import os

logger = logging.getLogger(__name__)

def load_script_from_examples() -> List[Dict[str, Any]]:
    """
    从examples文件夹加载剧本JSON文件
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建examples/example_script.json文件的完整路径
        script_file_path = os.path.join(current_dir, 'examples', 'example_script.json')

        with open(script_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        return json_data
    except FileNotFoundError:
        logger.error(f"剧本文件不存在: {script_file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"JSON格式错误: {script_file_path}")
        raise
    except Exception as e:
        logger.error(f"从examples文件夹加载剧本失败: {e}")
        raise

def get_type_by_id(script: List[Dict[str, Any]], node_id: str) -> Optional[str]:
    """
    根据节点ID获取节点类型
    """
    for node in script:
        if node.get("id") == node_id:
            return node.get("type")
    logger.warning(f"未找到节点: {node_id}")
    return None

def get_node_text_by_id(script: List[Dict[str, Any]], node_id: str) -> Optional[str]:
    """
    根据节点ID获取节点的文本内容
    支持MessageNode、ActionNode、ChoiceNode等不同类型节点
    """
    for node in script:
        if node.get("id") == node_id:
            node_type = node.get("type")
            
            if node_type == "MessageNode":
                return node.get("content", {}).get("text")
            elif node_type == "ActionNode":
                return node.get("parameters", {}).get("prompt")
            elif node_type == "ChoiceNode":
                return node.get("prompt")
            logger.warning(f"节点类型 {node_type} 不支持获取文本内容")
            return None
    logger.warning(f"未找到节点: {node_id}")
    return None

def get_next_node_id(script: List[Dict[str, Any]], node_id: str, user_input: Optional[str] = None) -> Optional[str]:
    """
    根据节点ID和类型获取下一个节点ID
    
    Args:
        script: 剧本数据
        node_id: 当前节点ID
        user_input: 用户输入，用于处理ReactionNode和ChoiceNode类型
        
    Returns:
        下一个节点ID，如果未找到则返回None
    """
    # 获取节点类型
    node_type = get_type_by_id(script, node_id)
    if not node_type:
        return None
    
    # 获取节点信息
    node = get_node_by_id(script, node_id)
    if not node:
        return None
    
    # 根据不同类型处理
    if node_type == "MessageNode" or node_type == "ActionNode":
        # 直接从节点获取next
        return node.get("next", "")
    elif node_type == "ReactionNode":
        # 使用process_reaction_node处理ReactionNode
        if user_input:
            return process_reaction_node(node, user_input)
        else:
            logger.warning(f"处理ReactionNode需要用户输入，节点ID: {node_id}")
            return ""
    elif node_type == "ChoiceNode":
        # 处理ChoiceNode类型
        if user_input:
            branches = node.get("branches", [])
            user_input_lower = user_input.lower()
            
            # 遍历所有分支，查找匹配项
            for branch in branches:
                condition = branch.get("condition", "").lower()
                if condition in user_input_lower:
                    logger.info(f"用户输入匹配分支条件: {condition}")
                    return branch.get("next", "")
            
            # 如果没有匹配项，返回默认值
            logger.warning(f"没有匹配的分支条件，用户输入: {user_input}")
            return ""
        else:
            logger.warning(f"处理ChoiceNode需要用户输入，节点ID: {node_id}")
            return ""
    else:
        logger.warning(f"未知节点类型: {node_type}")
        # 对于未知类型，尝试直接获取next属性
        return node.get("next", "")

def get_node_by_id(script: List[Dict[str, Any]], node_id: str) -> Optional[Dict[str, Any]]:
    """
    根据节点ID获取节点信息
    """
    for node in script:
        if node.get("id") == node_id:
            return node
    logger.warning(f"未找到节点: {node_id}")
    return None

def process_reaction_node(node: Dict[str, Any], user_input: str) -> str:
    """
    处理ReactionNode，根据用户输入匹配条件
    """
    if node.get("type") != "ReactionNode":
        raise ValueError(f"节点类型错误，应为ReactionNode: {node.get('type')}")
    
    conditions = node.get("conditions", [])
    user_input_lower = user_input.lower()
    
    # 遍历所有条件，查找匹配项
    for condition in conditions:
        patterns = condition.get("patterns", [])
        for pattern in patterns:
            if pattern.lower() in user_input_lower:
                logger.info(f"用户输入匹配条件: {condition.get('label')}")
                return condition.get("next", "")
    
    # 如果没有匹配项，返回默认值
    logger.warning(f"没有匹配的条件，用户输入: {user_input}")
    return ""

def process_choice_node(node: Dict[str, Any], user_input: str) -> str:
    """
    处理ChoiceNode，根据用户选择匹配分支
    """
    if node.get("type") != "ChoiceNode":
        raise ValueError(f"节点类型错误，应为ChoiceNode: {node.get('type')}")
    
    branches = node.get("branches", [])
    user_input_lower = user_input.lower()
    
    # 遍历所有分支，查找匹配项
    for branch in branches:
        condition = branch.get("condition", "").lower()
        if condition in user_input_lower:
            logger.info(f"用户选择匹配分支: {condition}")
            return branch.get("next", "")
    
    # 如果没有匹配项，返回第一个分支的next（默认）
    if branches:
        default_next = branches[0].get("next", "")
        logger.warning(f"没有匹配的分支，使用默认分支: {default_next}")
        return default_next
    
    logger.warning(f"ChoiceNode没有分支，节点ID: {node.get('id')}")
    return ""

def get_node_content(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取节点的内容信息
    """
    content = node.get("content", {})
    result = {
        "text": content.get("text", ""),
        "media": content.get("media", [])
    }
    
    # 如果是ActionNode，添加action信息
    if node.get("type") == "ActionNode":
        result["action"] = node.get("action", "")
        result["parameters"] = node.get("parameters", {})
    
    # 如果是ChoiceNode，添加prompt信息
    if node.get("type") == "ChoiceNode":
        result["prompt"] = node.get("prompt", "")
        result["branches"] = node.get("branches", [])
    
    return result