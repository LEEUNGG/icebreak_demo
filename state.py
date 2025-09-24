"""
状态定义模块
定义对话系统的状态结构
"""
from typing import Literal, Optional, List, Dict, Any
from langgraph.graph import MessagesState


class ConversationState(MessagesState):
    """
    对话状态类，继承自MessagesState
    """
    # 轮次计数器
    turn_count: int = 0
    
    # 记录当前模式：leader 或 listener
    conversation_mode: Optional[Literal["leader", "listener"]] = "leader"
    
    # 用户输入（临时存储）
    user_input: Optional[str] = None

    # the ID of the current node
    current_node_id: Optional[str] = None

    # Script
    script: Optional[List[Dict[str, Any]]] = None

    # the type of the current node
    current_node_type: Optional[str] = None

    # choice node status
    choice_node_status: Optional[str] = "ask"

    # usedScript
    # usedScript: Optional[List[Dict[str, Any]]] = None

    # usedScript
    noScript: Optional[str] = "false"

    # creator background
    creator_background: Optional[str] = """
# Character Card — OnlyFans Creator

**Name (Stage Name):** Luna  
**Age:** 24  
**Gender / Orientation:** Female / Bisexual  
**Appearance:** Long straight black hair, deep brown eyes, fair skin, slim with soft curves, usually dresses in a cozy but slightly sensual style  
**Tagline / Persona Type:** Girl-next-door × Playful tease  

## Account Info
- **OnlyFans Username:** MoonLuna  
- **Content Type:** Casual photo sets + home-style short videos + sweet private chats  
- **Style/Persona:** Approachable / Interactive (likes chatting with fans)  
- **Subscription Price:** $12.99/month  

## Personality & Persona
- **Public Persona:** Sweet, clingy, playful  
- **Private Personality:** A bit introverted, enjoys reading quietly  
- **Phrases / Chat Style:**  
  - *“Hey, are you thinking of me?”*  
  - *“Want to keep me company for a bit?”*  
    """