# graph.py
from langgraph.graph import StateGraph, END
import json
import logging
from .state import AgentState
from .node import generate_all, generate_single, fallback_node, regenerate_all, regenerate_single

logger = logging.getLogger(__name__)

def router(state: AgentState):
    """Router edge"""
    if state.get("type") == "all":
        others = state.get("Others")
        if others is None or (isinstance(others, dict) and not others):
            return "generate_all"
        return "regenerate_all"
    elif state.get("type"):
        others = state.get("Others")
        if others is None or (isinstance(others, dict) and not others):
            return "generate_single"
        return "regenerate_single"
    return "fallback"

def build_graph():
    """
    构建 LangGraph Workflow
    """
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("regenerate_all", regenerate_all)
    workflow.add_node("generate_all", generate_all)
    workflow.add_node("regenerate_single", regenerate_single)
    workflow.add_node("generate_single", generate_single)
    workflow.add_node("fallback", fallback_node)
    
    # 设置条件边
    workflow.set_conditional_entry_point(
        router,
        {
            "regenerate_all": "regenerate_all",
            "generate_all": "generate_all",
            "regenerate_single": "regenerate_single",
            "generate_single": "generate_single",
            "fallback": "fallback",
        }
    )
    
    # 添加结束边
    workflow.add_edge("regenerate_all", END)
    workflow.add_edge("generate_all", END)
    workflow.add_edge("regenerate_single", END)
    workflow.add_edge("generate_single", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()

def invoke_with_json_support(graph, input_data):
    """
    调用图并支持JSON字符串输入
    """
    if isinstance(input_data, str):
        try:
            input_data = json.loads(input_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON string provided: {e}")
            return {"error": "Invalid JSON string provided"}
    
    return graph.invoke(input_data)
