# personality_agent/__init__.py
# 延迟导入，避免循环引用
from .state import AgentState

def build_graph():
    from .graph import build_graph as _build_graph
    return _build_graph()

def invoke_with_json_support(graph, input_data):
    from .graph import invoke_with_json_support as _invoke
    return _invoke(graph, input_data)

__all__ = [
    'build_graph',
    'invoke_with_json_support',
    'AgentState'
]
