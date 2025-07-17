"""
配置管理模块
管理环境变量和应用配置
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "DevPal - 游戏代码副驾驶"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS配置
    allowed_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # AI模型配置 - 豆包/字节跳动
    doubao_api_key: str = "be79af19-6223-4ed3-904a-8fbd5ee59f84"
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    doubao_model: str = "doubao-seed-1-6-thinking-250715"
    
    # AI模型配置 - Kimi/月之暗面
    kimi_api_key: Optional[str] = None
    kimi_base_url: str = "https://api.moonshot.cn/v1"
    kimi_model: str = "moonshot-v1-8k"
    
    # AI模型配置 - DeepSeek
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-coder"
    
    # AI模型配置 - 通义千问
    qwen_api_key: Optional[str] = None
    qwen_model: str = "qwen-turbo"
    
    # AI模型配置 - 智谱AI
    zhipu_api_key: Optional[str] = None
    zhipu_model: str = "glm-4"
    
    # 默认使用的AI模型提供商
    default_ai_provider: str = "doubao"
    
    # AI生成配置
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/devpal.log"
    
    # 安全配置
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()


def get_ai_config(provider: str = None) -> dict:
    """
    获取指定AI提供商的配置
    
    Args:
        provider: AI提供商名称，如果为None则使用默认提供商
        
    Returns:
        包含API密钥、基础URL和模型名称的配置字典
    """
    if provider is None:
        provider = settings.default_ai_provider
    
    config_map = {
        "doubao": {
            "api_key": settings.doubao_api_key,
            "base_url": settings.doubao_base_url,
            "model": settings.doubao_model
        },
        "kimi": {
            "api_key": settings.kimi_api_key,
            "base_url": settings.kimi_base_url,
            "model": settings.kimi_model
        },
        "deepseek": {
            "api_key": settings.deepseek_api_key,
            "base_url": settings.deepseek_base_url,
            "model": settings.deepseek_model
        },
        "qwen": {
            "api_key": settings.qwen_api_key,
            "base_url": None,  # 通义千问使用dashscope SDK
            "model": settings.qwen_model
        },
        "zhipu": {
            "api_key": settings.zhipu_api_key,
            "base_url": None,  # 智谱AI使用专用SDK
            "model": settings.zhipu_model
        }
    }
    
    return config_map.get(provider, config_map["doubao"])


def validate_ai_config(provider: str = None) -> bool:
    """
    验证AI提供商配置是否完整

    Args:
        provider: AI提供商名称

    Returns:
        配置是否有效
    """
    # 在测试环境中跳过验证
    if settings.environment == "test":
        return True

    config = get_ai_config(provider)

    # 调试信息
    print(f"验证AI配置 - 提供商: {provider or settings.default_ai_provider}")
    print(f"API密钥: {config['api_key'][:10] if config['api_key'] else 'None'}...")

    return config["api_key"] is not None and config["api_key"] != ""
