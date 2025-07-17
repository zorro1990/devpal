"""
配置管理API端点
提供AI配置测试和管理功能
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import httpx
from datetime import datetime

from app.core.config import settings
from app.services.code_generator import CodeGeneratorService

router = APIRouter()


class ModelConfig(BaseModel):
    """模型配置"""
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    top_p: float = Field(default=0.9, ge=0, le=1)
    frequency_penalty: float = Field(default=0, ge=-2, le=2)
    presence_penalty: float = Field(default=0, ge=-2, le=2)


class ConfigTestRequest(BaseModel):
    """配置测试请求"""
    provider: str = Field(..., description="AI提供商")
    api_key: str = Field(..., description="API密钥")
    model: str = Field(..., description="模型名称")
    model_settings: Optional[ModelConfig] = None
    base_url: Optional[str] = Field(None, description="自定义API基础URL")


class ConfigTestResponse(BaseModel):
    """配置测试响应"""
    success: bool
    message: str
    provider: str
    model: str
    response_time_ms: Optional[int] = None
    timestamp: str


@router.post("/test", response_model=ConfigTestResponse)
async def test_config(request: ConfigTestRequest):
    """
    测试AI配置是否有效
    
    Args:
        request: 配置测试请求
        
    Returns:
        测试结果
    """
    start_time = datetime.now()
    
    try:
        # 验证提供商是否支持
        supported_providers = ["doubao", "kimi", "deepseek", "qwen", "zhipu", "openai", "claude", "gemini"]
        if request.provider not in supported_providers:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的AI提供商: {request.provider}"
            )
        
        # 创建代码生成服务实例进行测试
        generator_service = CodeGeneratorService()
        
        # 构建测试配置
        test_config = {
            "provider": request.provider,
            "api_key": request.api_key,
            "model": request.model,
            "base_url": request.base_url,
            "temperature": request.model_config.temperature,
            "max_tokens": min(request.model_config.max_tokens, 100),  # 测试时限制token数
            "top_p": request.model_config.top_p
        }
        
        # 执行简单的测试请求
        test_prompt = "请回复'测试成功'四个字。"
        
        try:
            # 使用临时配置进行测试
            response = await generator_service.test_connection(test_config, test_prompt)
            
            end_time = datetime.now()
            response_time = int((end_time - start_time).total_seconds() * 1000)
            
            if response and "测试" in response:
                return ConfigTestResponse(
                    success=True,
                    message=f"连接成功！模型 {request.model} 响应正常",
                    provider=request.provider,
                    model=request.model,
                    response_time_ms=response_time,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return ConfigTestResponse(
                    success=False,
                    message="连接成功但模型响应异常，请检查模型配置",
                    provider=request.provider,
                    model=request.model,
                    response_time_ms=response_time,
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            error_msg = str(e)
            
            # 根据错误类型提供更友好的错误信息
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                error_msg = "API密钥无效，请检查密钥是否正确"
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                error_msg = "API密钥权限不足，请检查密钥权限"
            elif "404" in error_msg:
                error_msg = "模型不存在或不可用，请检查模型名称"
            elif "timeout" in error_msg.lower():
                error_msg = "连接超时，请检查网络连接或稍后重试"
            elif "connection" in error_msg.lower():
                error_msg = "网络连接失败，请检查网络设置"
            
            return ConfigTestResponse(
                success=False,
                message=f"连接失败: {error_msg}",
                provider=request.provider,
                model=request.model,
                timestamp=datetime.now().isoformat()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        return ConfigTestResponse(
            success=False,
            message=f"测试过程中发生错误: {str(e)}",
            provider=request.provider,
            model=request.model,
            timestamp=datetime.now().isoformat()
        )


@router.get("/providers")
async def get_supported_providers():
    """
    获取支持的AI提供商列表
    
    Returns:
        支持的提供商信息
    """
    providers = {
        "domestic": [
            {
                "id": "doubao",
                "name": "豆包",
                "description": "字节跳动的AI大模型",
                "models": ["doubao-lite-4k", "doubao-lite-32k", "doubao-lite-128k"],
                "default_model": "doubao-lite-32k"
            },
            {
                "id": "kimi",
                "name": "Kimi",
                "description": "Moonshot AI的智能助手",
                "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
                "default_model": "moonshot-v1-32k"
            },
            {
                "id": "deepseek",
                "name": "DeepSeek",
                "description": "深度求索的AI模型",
                "models": ["deepseek-chat", "deepseek-coder"],
                "default_model": "deepseek-coder"
            },
            {
                "id": "qwen",
                "name": "通义千问",
                "description": "阿里云的大语言模型",
                "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
                "default_model": "qwen-plus"
            },
            {
                "id": "zhipu",
                "name": "智谱AI",
                "description": "智谱AI的GLM系列模型",
                "models": ["glm-4", "glm-4-air", "glm-4-flash"],
                "default_model": "glm-4"
            }
        ],
        "international": [
            {
                "id": "openai",
                "name": "OpenAI GPT",
                "description": "OpenAI的GPT系列模型",
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"],
                "default_model": "gpt-4"
            },
            {
                "id": "claude",
                "name": "Anthropic Claude",
                "description": "Anthropic的Claude模型",
                "models": ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"],
                "default_model": "claude-3-sonnet"
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "description": "Google的Gemini模型",
                "models": ["gemini-pro", "gemini-pro-vision", "gemini-ultra"],
                "default_model": "gemini-pro"
            }
        ]
    }
    
    return {
        "providers": providers,
        "total_count": len(providers["domestic"]) + len(providers["international"]),
        "categories": ["domestic", "international"]
    }


@router.get("/current")
async def get_current_config():
    """
    获取当前服务器配置状态
    
    Returns:
        当前配置信息（不包含敏感信息）
    """
    return {
        "default_provider": settings.default_ai_provider,
        "available_providers": {
            "doubao": settings.doubao_api_key is not None,
            "kimi": settings.kimi_api_key is not None,
            "deepseek": settings.deepseek_api_key is not None,
            "qwen": settings.qwen_api_key is not None,
            "zhipu": settings.zhipu_api_key is not None
        },
        "default_model_config": {
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "timeout": settings.timeout
        },
        "environment": settings.environment,
        "version": settings.app_version
    }
