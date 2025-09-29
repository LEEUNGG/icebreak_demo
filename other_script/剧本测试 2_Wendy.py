#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剧本内容处理器
使用说明：将JSON内容放入input_data.json文件中，运行脚本即可自动处理并保存
"""

import os
import json
import re
from typing import Dict, Any
from datetime import datetime

class ScriptProcessor:
    def __init__(self):
        # 获取脚本所在目录
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(self.script_dir, "outputs")
        self.input_file = os.path.join(self.script_dir, "input_data.json")
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            print(f"📂 已创建输出目录: {self.base_path}")

    def clean_folder_name(self, name: str) -> str:
        """清理文件夹名称，移除非法字符"""
        # 移除 <think> 标签内容
        name = re.sub(r"<think>.*?</think>", "", name, flags=re.DOTALL).strip()
        # 移除文件系统非法字符 + 换行符等空白
        name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', name)
        # 限制长度
        if len(name) > 50:
            name = name[:47] + "..."
        return name or "unnamed_script"

    def read_input_file(self) -> Dict[str, Any]:
        """从输入文件读取内容"""
        if not os.path.exists(self.input_file):
            print(f"❌ 输入文件 '{os.path.basename(self.input_file)}' 不存在")
            print(f"💡 请在脚本目录下创建 '{os.path.basename(self.input_file)}' 文件")
            print(f"📍 期望位置: {self.input_file}")
            return {}

        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            if not content:
                print(f"❌ 输入文件 '{self.input_file}' 为空")
                return {}

            print(f"📖 从 '{self.input_file}' 读取到 {len(content)} 个字符")
            return self.parse_input_content(content)

        except Exception as e:
            print(f"❌ 读取输入文件时出错: {str(e)}")
            return {}

    def parse_input_content(self, content: str) -> Dict[str, Any]:
        """解析输入的JSON内容"""
        try:
            # 尝试直接解析JSON
            data = json.loads(content)
            return data
        except json.JSONDecodeError:
            # 如果失败，尝试提取JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    return data
                except json.JSONDecodeError:
                    pass

            # 如果都失败，返回原始内容包装
            return {"raw_content": content}

    def save_outputs(self, data: Dict[str, Any]) -> str:
        """保存处理后的内容到文件"""
        try:
            # 获取文件夹名称
            folder_name = data.get("name", "default_script")
            folder_name = self.clean_folder_name(folder_name)

            # 添加时间戳避免重复
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{folder_name}_{timestamp}"

            folder_path = os.path.join(self.base_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            print(f"\n📂 创建文件夹: {folder_path}")

            saved_files = []

            # 定义要保存的键值对应关系（更新后的键）
            save_mapping = {
                "content": ("content.md", "markdown"),
                "script": ("script.json", "json"),
                "plot1_prompt": ("plot1_prompt.json", "json"),
                "plot2_prompt": ("plot2_prompt.json", "json"),
                "name": ("name.txt", "text")
            }

            # 保存各个部分
            for key, (filename, file_type) in save_mapping.items():
                if key in data and data[key]:
                    file_path = os.path.join(folder_path, filename)

                    if file_type == "json":
                        if key == "script":
                            # Script需要特殊处理
                            self.save_script(data[key], file_path, folder_path)
                        else:
                            # 其他JSON文件
                            with open(file_path, "w", encoding="utf-8") as f:
                                if isinstance(data[key], str):
                                    json.dump({key: data[key]}, f, ensure_ascii=False, indent=2)
                                else:
                                    json.dump(data[key], f, ensure_ascii=False, indent=2)

                    elif file_type == "markdown":
                        with open(file_path, "w", encoding="utf-8") as f:
                            content = data[key].replace("\\n", "\n")
                            f.write(content)

                    elif file_type == "text":
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(str(data[key]))

                    saved_files.append(file_path)
                    print(f"✅ 已保存: {filename}")

            # 如果没有找到标准字段，保存原始内容
            if not saved_files and "raw_content" in data:
                file_path = os.path.join(folder_path, "raw_content.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(data["raw_content"])
                saved_files.append(file_path)
                print(f"✅ 已保存: raw_content.txt")

            # 创建汇总文件
            self.create_summary(data, folder_path)

            return folder_path

        except Exception as e:
            print(f"❌ 保存过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""

    def save_script(self, script_content: str, file_path: str, folder_path: str):
        """特殊处理script内容"""
        try:
            # 保存原始script
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"script": script_content}, f, ensure_ascii=False, indent=2)

            # 尝试解析并保存可读版本
            script_clean = re.sub(r"^```json\n?|```$", "", script_content.strip())
            try:
                script_dict = json.loads(script_clean)
                readable_path = os.path.join(folder_path, "script_readable.json")
                with open(readable_path, "w", encoding="utf-8") as f:
                    json.dump(script_dict, f, ensure_ascii=False, indent=2)
                print(f"📖 已保存可读版本: script_readable.json")
            except json.JSONDecodeError:
                print("⚠️ Script内容不是有效的JSON格式，跳过可读版本生成")

        except Exception as e:
            print(f"⚠️ 保存script时出错: {e}")

    def create_summary(self, data: Dict[str, Any], folder_path: str):
        """创建内容汇总文件"""
        summary_path = os.path.join(folder_path, "summary.md")

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("# 剧本内容汇总\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if "name" in data:
                f.write(f"## 名称\n{data['name']}\n\n")

            # 列出包含的键
            f.write("## 包含内容\n")
            keys = ["name", "content", "script", "plot1_prompt", "plot2_prompt"]
            for key in keys:
                if key in data and data[key]:
                    f.write(f"- ✅ {key}\n")
                else:
                    f.write(f"- ❌ {key} (未找到或为空)\n")
            f.write("\n")

            # 统计信息
            f.write("## 文件统计\n")
            file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
            f.write(f"- 总文件数: {file_count}\n")

            for filename in os.listdir(folder_path):
                if filename != "summary.md":
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        f.write(f"- {filename}: {size} bytes\n")

        print(f"📋 已生成汇总文件: summary.md")

    def run(self):
        """主运行流程"""
        print("=" * 60)
        print("🎬 剧本内容处理器")
        print("=" * 60)
        print(f"说明: 从文件 '{os.path.basename(self.input_file)}' 读取JSON内容并处理")
        print(f"文件路径: {self.input_file}")
        print("支持的键: name, content, script, plot1_prompt, plot2_prompt")
        print("-" * 60)

        # 从文件读取内容
        parsed_data = self.read_input_file()
        
        if not parsed_data:
            print("❌ 没有读取到有效内容")
            return

        print("🔍 内容解析完成")

        # 显示找到的键
        found_keys = [key for key in ["name", "content", "script", "plot1_prompt", "plot2_prompt"] 
                     if key in parsed_data and parsed_data[key]]
        if found_keys:
            print(f"📋 找到的键: {', '.join(found_keys)}")
        else:
            print("⚠️ 未找到预期的键，将保存原始内容")

        # 保存文件
        print("💾 正在保存文件...")
        output_folder = self.save_outputs(parsed_data)

        if output_folder:
            print(f"\n🎉 处理完成!")
            print(f"📁 文件保存位置: {os.path.abspath(output_folder)}")
            print(f"📂 您可以在 '{output_folder}' 文件夹中查看所有生成的文件")
        else:
            print("❌ 处理失败")

def main():
    """主函数"""
    processor = ScriptProcessor()
    
    try:
        processor.run()
    except KeyboardInterrupt:
        print("\n👋 程序被中断")
    except Exception as e:
        print(f"❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()