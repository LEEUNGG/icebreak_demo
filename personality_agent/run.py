# run.py
import json
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

from graph import build_graph, invoke_with_json_support

def main():
    # 构建图
    graph = build_graph()

    # 示例输入
    input_state = {
        "type": "call_fans",
        "country": "US",
        "content_type": "photo",
        "gender": "female",
        "profile_pic": "https://storage.googleapis.com/avatarai/upload_file/2025-08-05/bd129e5a-135e-484e-b433-5400d356ab31_.png",
        "nickname": "Alice",
        "mbti": "ENFP",
        "about_me": "Love traveling and photography",
        "Others": "call_fans: fucking stupid"
    }
    
    # 测试字典输入
    print("=" * 50)
    print("测试字典输入:")
    print("=" * 50)
    result1 = graph.invoke(input_state)
    print("结果:")
    print(result1.get("output", "No output"))
    
    # 测试JSON字符串输入
    # print("\n" + "=" * 50)
    # print("测试JSON字符串输入:")
    # print("=" * 50)
    # json_input = json.dumps(input_state)
    # result2 = invoke_with_json_support(graph, json_input)
    # print("结果:")
    # print(result2.get("output", "No output"))

if __name__ == "__main__":
    main()
