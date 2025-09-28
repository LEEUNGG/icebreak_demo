"""
LLM 模型配置模块
支持 Google Vertex AI, 阿里云通义千问, 豆包等模型
"""
import os
from typing import Optional, Dict, Any
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_openai import ChatOpenAI
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
    def create_qwen_model(config: ModelConfig):
        """创建通义千问模型（包括阿里云上的DeepSeek）"""
        return ChatTongyi(
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens or 4096,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
        )
    
    @staticmethod
    def create_openrouter_model(config: ModelConfig):
        """
        创建 OpenRouter 模型
        支持 XAI 的 Grok 模型等
        """
        return ChatOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens or 4096,
            default_headers={
                "HTTP-Referer": os.getenv("YOUR_SITE_URL", "https://example.com"),
                "X-Title": os.getenv("YOUR_SITE_NAME", "IceBreak_demo")
            }
        )
    
    @classmethod
    def get_model(cls, config: ModelConfig):
        """根据配置获取模型实例"""
        model_creators = {
            "qwen": cls.create_qwen_model, 
            "openrouter": cls.create_openrouter_model,
        }
        
        creator = model_creators.get(config.model_type)
        if not creator:
            raise ValueError(f"Unsupported model type: {config.model_type}")
        
        return creator(config)

DEEPSEEK_V3_1_CONFIG = ModelConfig(
    model_type="qwen",  # 使用阿里云的接口
    model_name="deepseek-v3.1", 
    temperature=1
)

QWEN_FLASH_CONFIG = ModelConfig(
    model_type="qwen",
    model_name="qwen-flash",  
    temperature=1
)

DEEPSEEK_V3_1_TERMINUS_CONFIG = ModelConfig(
    model_type="openrouter",
    model_name="deepseek/deepseek-v3.1-terminus",
    temperature=1
)

GROK_CONFIG = ModelConfig(
    model_type="openrouter",
    model_name="x-ai/grok-4",
    temperature=1
)

OPENAI_41_CONFIG = ModelConfig(
    model_type="openrouter",
    model_name="openai/gpt-4.1",
    temperature=1
)
