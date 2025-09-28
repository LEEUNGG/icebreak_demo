from typing import Literal, Union
from state import ConversationState
import logging

logger = logging.getLogger(__name__)

def should_classify(state: ConversationState) -> Literal["classify", "maintain"]:
    """
    判断是否需要进行engagement分类
    每隔两轮（偶数轮次）运行一次分类器
    """
    if state.get("noScript", "false") == "true":
        return "maintain"
    else:
        turn_count = state.get("turn_count", 0)
        if turn_count % 2 == 0:
            logger.debug(f"轮次 {turn_count} 为偶数，执行分类")
            return "classify"
        else: 
            logger.debug(f"轮次 {turn_count} 为奇数，维持当前模式")
            return "maintain"

def route_by_mode(state: ConversationState) -> Literal["leader", "listener"]:
    """
    根据conversation_mode路由到不同的处理节点
    """
    mode = state.get("conversation_mode", "listener")
    
    # 确保mode是有效值
    if mode not in ["leader", "listener"]:
        mode = "listener"
        logger.warning(f"无效的conversation_mode，使用默认值: {mode}")
    
    logger.debug(f"route_by_mode结果: {mode}")
    return mode

def route_by_node_type(state: ConversationState) -> Union[Literal["message", "reaction", "choice", "action", "end"]]:
    """
    根据node_type路由到不同的处理节点
    如果node_type为空，返回"end"
    """
    node_type = state.get("current_node_type", "")
    
    # 如果节点类型为空或None，返回end
    if not node_type:
        logger.debug("节点类型为空，路由到END")
        return "end"
    
    # 转换节点类型名称到简短版本
    type_mapping = {
        "MessageNode": "message",
        "ReactionNode": "reaction",
        "ActionNode": "action"
    }

    if node_type != "ChoiceNode":
           route_target = type_mapping.get(node_type, "")
    else:
        if state.get("choice_node_status")  == "ask":   
            route_target = "choice_ask"
        else:
            route_target = "choice_branch"

    if not route_target:
        logger.warning(f"未知节点类型: {node_type}，路由到END")
        return "end"
    logger.debug(f"根据节点类型路由结果: {route_target}")
    return route_target
