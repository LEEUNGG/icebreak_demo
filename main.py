"""
交互式主运行文件
模拟真实用户与bot的多轮对话
"""
import logging
import os
from dotenv import load_dotenv
from graph import build_conversation_graph
from langchain_core.messages import AIMessage
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversation.log'), 
    ]
)

class ConversationBot:
    def __init__(self):
        """初始化对话机器人"""
        self.graph = build_conversation_graph()
        self.state = {
            "messages": [],
            "turn_count": 0,
            "conversation_mode": "leader",  # 默认从leader模式开始
            "user_input": None,
            "current_node_id": None,
            "script": None,
            "current_node_type": None,
            "choice_node_status": "ask",
            "noScript": "false",
            "creator_background": """
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
        }
        
    def send_message(self, user_input: str):
        """发送用户消息并获取bot回复"""
        try:
            # 更新状态中的用户输入
            self.state["user_input"] = user_input
            
            # 调用图处理
            result = self.graph.invoke(self.state)
            
            # 更新状态
            self.state.update(result)
            
            # 获取最新的AI回复
            ai_messages = [msg for msg in result.get("messages", []) if isinstance(msg, AIMessage)]
            if ai_messages:
                return ai_messages[-1].content
            else:
                return "抱歉，我现在无法回复。"
                
        except Exception as e:
            logging.error(f"处理消息时发生错误: {e}")
            return f"抱歉，处理您的消息时出现了问题: {str(e)}"
    
    def get_conversation_info(self):
        """获取当前对话状态信息"""
        return {
            "turn_count": self.state.get("turn_count", 0),
            "conversation_mode": self.state.get("conversation_mode", "unknown"),
            "current_node_id": self.state.get("current_node_id"),
            "current_node_type": self.state.get("current_node_type"),
            "total_messages": len(self.state.get("messages", []))
        }

def print_separator():
    """打印分隔线"""
    print("\n" + "="*60)

def print_bot_response(response: str):
    """格式化打印bot回复"""
    print_separator()
    print("🤖 Bot回复:")
    print(f"   {response}")
    print_separator()

def run_interactive_conversation():
    """运行交互式对话"""
    print("🎯 OnlyFans创作者AI聊天机器人")
    print("💡 输入 'quit' 或 'exit' 退出对话")
    print("💡 输入 'reset' 重置对话状态")
    
    # 初始化bot
    bot = ConversationBot()
    
    print_separator()
    print("🚀 对话开始！和我聊聊吧~")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！感谢与我聊天~")
                break
            
            # 检查重置命令
            if user_input.lower() in ['reset', '重置']:
                bot = ConversationBot()
                print("\n🔄 对话状态已重置！")
                continue
            
            # 检查空输入
            if not user_input:
                print("⚠️  请输入一些内容...")
                continue
            
            # 发送消息并获取回复
            response = bot.send_message(user_input)
            
            # 打印回复
            print_bot_response(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 对话被中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            logging.error(f"主循环错误: {e}", exc_info=True)

def run_demo_conversation():
    """运行演示对话（自动化测试场景）"""
    print("🎬 演示模式：自动化对话测试")
    
    bot = ConversationBot()
    
    # 定义测试对话流程
    test_scenarios = [
        {
            "input": "Hi there! How are you doing today?",
            "description": "友好问候 - 应该触发listener模式"
        },
        {
            "input": "I had such a stressful day at work, my boss was being difficult",
            "description": "分享工作压力 - 应该保持listener模式"
        },
        {
            "input": "What do you think about that?",
            "description": "询问意见 - 可能切换到leader模式"
        },
        {
            "input": "Yeah, I want to hear your rules",
            "description": "表示兴趣 - 可能进入script模式"
        },
        {
            "input": "I want to break all the rules!",
            "description": "选择破坏规则 - script分支选择"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 测试场景 {i}: {scenario['description']}")
        print(f"👤 用户输入: {scenario['input']}")
        
        response = bot.send_message(scenario['input'])
        info = bot.get_conversation_info()
        
        print_bot_response(response, info)
        
        # 暂停以便查看结果
        input("按回车键继续下一个场景...")

def main():
    """主函数"""
    print("🎮 选择运行模式:")
    print("1. 交互式对话 (推荐)")
    print("2. 演示模式 (自动化测试)")
    
    try:
        choice = input("\n请选择模式 (1 或 2): ").strip()
        
        if choice == "1":
            run_interactive_conversation()
        elif choice == "2":
            run_demo_conversation()
        else:
            print("❌ 无效选择，启动交互式模式...")
            run_interactive_conversation()
            
    except Exception as e:
        logging.error(f"主函数执行错误: {e}", exc_info=True)
        print(f"❌ 程序执行出错: {e}")

if __name__ == "__main__":
    main()