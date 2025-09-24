"""
LLM 模型配置模块
支持 Google Vertex AI, 阿里云通义千问, 豆包等模型
"""
import os
from typing import Optional, Dict, Any
from langchain_google_vertexai import ChatVertexAI
from langchain_community.chat_models.tongyi import ChatTongyi
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置类"""
    model_type: str
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    extra_params: Optional[Dict[str, Any]] = None


class LLMFactory:
    """LLM 工厂类，用于创建不同的模型实例"""
    
    @staticmethod
    def create_vertex_ai_model(config: ModelConfig):
        """创建 Google Vertex AI 模型"""
        return ChatVertexAI(
            model_name=config.model_name,
            temperature=config.temperature,
            max_output_tokens=config.max_tokens or 1024,
            project=os.getenv("VERTEX_AI_PROJECT"),
            location=os.getenv("VERTEX_AI_LOCATION", "us-central1")
        )
    
    @staticmethod
    def create_qwen_model(config: ModelConfig):
        """创建通义千问模型（包括阿里云上的DeepSeek）"""
        return ChatTongyi(
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens or 4096,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
        )
    
    @staticmethod
    def create_doubao_model(config: ModelConfig):
        """
        创建豆包模型
        注：这里需要根据豆包的具体SDK进行调整
        """
        pass
    
    @classmethod
    def get_model(cls, config: ModelConfig):
        """根据配置获取模型实例"""
        model_creators = {
            "vertex_ai": cls.create_vertex_ai_model,
            "qwen": cls.create_qwen_model, 
            "doubao": cls.create_doubao_model,
        }
        
        creator = model_creators.get(config.model_type)
        if not creator:
            raise ValueError(f"Unsupported model type: {config.model_type}")
        
        return creator(config)


# 预定义的模型配置

# 通义千问系列
QWEN_TURBO_CONFIG = ModelConfig(
    model_type="qwen",
    model_name="qwen-turbo",
    temperature=0.7
)

QWEN_PLUS_CONFIG = ModelConfig(
    model_type="qwen",
    model_name="qwen-plus",
    temperature=0.7
)

QWEN_MAX_CONFIG = ModelConfig(
    model_type="qwen",
    model_name="qwen-max",
    temperature=0.7
)

# DeepSeek V3.1 - 最新版本
DEEPSEEK_V3_1_CONFIG = ModelConfig(
    model_type="qwen",  # 使用阿里云的接口
    model_name="deepseek-v3.1",  # DeepSeek V3.1模型
    temperature=1,  # 稍微提高温度让回复更生动
    max_tokens=4096
)

# 设置默认使用的配置 - 使用 V3.1
DEEPSEEK_CONFIG = DEEPSEEK_V3_1_CONFIG

# 通义千问Flash模型配置
QWEN_FLASH_CONFIG = ModelConfig(
    model_type="qwen",
    model_name="qwen-plus",  # 使用qwen-plus作为替代
    temperature=0.7,
    max_tokens=4096
)
