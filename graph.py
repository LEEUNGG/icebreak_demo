"""
主图构建模块
构建LangGraph工作流
"""
from langgraph.graph import StateGraph, START, END
from state import ConversationState
from nodes import (
    user_input_node,
    engagement_classifier_node,
    maintain_mode_node,
    listener_node,
    determine_node_type_node,
    script_execution_message_node,
    script_execution_reaction_node,
    script_execution_choice_branch_node,
    script_execution_choice_ask_node,
    script_execution_action_node
)
from edges import should_classify, route_by_mode, route_by_node_type
import logging

logger = logging.getLogger(__name__)

def build_conversation_graph():
    """
    构建对话系统的LangGraph
    """
    graph = StateGraph(ConversationState)
    
    graph.add_node("user_input", user_input_node)
    graph.add_node("engagement_classifier", engagement_classifier_node)
    graph.add_node("maintain_mode", maintain_mode_node)
    graph.add_node("listener_mode", listener_node)
    graph.add_node("determine_node_type", determine_node_type_node)
    graph.add_node("script_message", script_execution_message_node)
    graph.add_node("script_reaction", script_execution_reaction_node)
    graph.add_node("script_choice_branch", script_execution_choice_branch_node)
    graph.add_node("script_choice_ask", script_execution_choice_ask_node)
    graph.add_node("script_action", script_execution_action_node)

    # 从START开始到状态初始化
    graph.add_edge(START, "user_input")
        
    graph.add_conditional_edges(
        "user_input",
        should_classify,
        {
            "classify": "engagement_classifier",
            "maintain": "maintain_mode"
        }
    )
    
    # 分类器后根据模式路由
    graph.add_conditional_edges(
        "engagement_classifier",
        route_by_mode,
        {
            "leader": "determine_node_type",
            "listener": "listener_mode"
        }
    )
    
    graph.add_conditional_edges(
        "maintain_mode",
        route_by_mode,
        {
            "leader": "determine_node_type",
            "listener": "listener_mode"
        }
    )

    graph.add_conditional_edges(
        "determine_node_type",
        route_by_node_type,
        {
            "message": "script_message",
            "reaction": "script_reaction",
            "choice_ask": "script_choice_ask",
            "choice_branch": "script_choice_branch",
            "action": "script_action",
            "end": END
        }
    )

    graph.add_conditional_edges(
        "script_reaction",
        route_by_node_type,
        {
            "message": "script_message",
            "choice_ask": "script_choice_ask",
            "choice_branch": "script_choice_branch",
            "action": "script_action",
        }
    )

    graph.add_conditional_edges(
        "script_choice_branch",
        route_by_node_type,
        {
            "message": "script_message",
            "reaction": "script_reaction",
            "action": "script_action",
        }
    )

    # END edges
    graph.add_edge("script_choice_ask", END)
    graph.add_edge("script_action", END)
    graph.add_edge("script_message", END)
    graph.add_edge("listener_mode", END)
    
    # 编译图
    return graph.compile()