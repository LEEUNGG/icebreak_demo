"""
测试图运行
"""
import logging
import os
from dotenv import load_dotenv
from graph import build_conversation_graph
from langchain_core.messages import HumanMessage

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_listener_mode():
    """测试倾听者模式"""
    print("\n" + "="*50)
    print("测试 Listener 模式")
    print("="*50)
    
    graph = build_conversation_graph()
    
    # 初始状态 - Listener模式
    initial_state = {
        "messages": [],
        "turn_count": 1,  # 奇数轮次，跳过分类器
        "conversation_mode": "listener",
        "user_input": "I had such a stressful day at work today, everything went wrong"
    }
    
    try:
        result = graph.invoke(initial_state)
        print("✓ Listener模式运行成功!")
        
        # 打印消息历史
        for msg in result.get('messages', []):
            role = "User" if msg.__class__.__name__ == "HumanMessage" else "AI"
            content = msg.content if hasattr(msg, 'content') else str(msg)
            print(f"\n{role}: {content}")
            
    except Exception as e:
        logging.error(f"Listener模式运行失败: {e}", exc_info=True)

def test_script_mode():
    """测试剧本模式"""
    print("\n" + "="*50)
    print("测试 Script 模式")
    print("="*50)
    
    graph = build_conversation_graph()
    
    # 直接设置为leader模式，使用奇数轮次跳过分类器
    initial_state = {
        "messages": [],
        "turn_count": 1,  # 奇数，跳过分类器
        "conversation_mode": "leader",
        "user_input": "yes I want to break all the rules!",
        "current_node_id": "hook",
        "current_node_type": "MessageNode"
    }
    
    try:
        print("\n初始节点: hook (MessageNode)")
        print("用户输入: yes I want to break all the rules!")
        
        result = graph.invoke(initial_state)
        print("\n✓ Script模式运行成功!")
        
        # 打印结果
        for msg in result.get('messages', []):
            role = "User" if msg.__class__.__name__ == "HumanMessage" else "AI"
            content = msg.content if hasattr(msg, 'content') else str(msg)
            print(f"\n{role}: {content[:200]}...")
            
        print(f"\n下一个节点: {result.get('current_node_id')} ({result.get('current_node_type')})")
        
    except Exception as e:
        logging.error(f"Script模式运行失败: {e}", exc_info=True)

def test_engagement_classifier():
    """测试 Engagement 分类器"""
    print("\n" + "="*50)
    print("测试 Engagement 分类器")
    print("="*50)
    
    graph = build_conversation_graph()
    
    # 测试场景1: 用户主动分享故事（应该是listener）
    test_cases = [
        {
            "messages": [
                HumanMessage(content="Let me tell you about my crazy day at work...")
            ],
            "turn_count": 0,  # 偶数轮次触发分类器
            "user_input": "So my boss was being really difficult today",
            "expected": "listener"
        },
        {
            "messages": [
                HumanMessage(content="Hi"),
                # AIMessage可能的回复
            ],
            "turn_count": 0,
            "user_input": "What's up?",
            "expected": "leader"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test['user_input'][:50]}...")
        initial_state = {
            "messages": test["messages"],
            "turn_count": test["turn_count"],
            "user_input": test["user_input"]
        }
        
        try:
            result = graph.invoke(initial_state)
            mode = result.get('conversation_mode', 'unknown')
            print(f"分类结果: {mode}")
            print(f"期望结果: {test['expected']}")
            print(f"{'✓' if mode == test['expected'] else '✗'} 测试{'通过' if mode == test['expected'] else '失败'}")
        except Exception as e:
            print(f"✗ 测试失败: {e}")

if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("错误: DASHSCOPE_API_KEY 环境变量未设置")
        exit(1)
    
    print(f"使用API密钥: {os.getenv('DASHSCOPE_API_KEY')[:10]}...")
    print("使用模型: DeepSeek V3.1")
    
    # 运行测试
    test_listener_mode()
    test_script_mode()
    test_engagement_classifier()
    
    print("\n" + "="*50)
    print("所有测试完成!")
    print("="*50)
