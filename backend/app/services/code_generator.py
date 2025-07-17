"""
代码生成器服务
实现AI调用逻辑和Prompt模板构建
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.core.config import settings, get_ai_config, validate_ai_config
from app.api.v1.schemas.generator import (
    CodeGenerateRequest,
    CodeGenerateResponse,
    ErrorResponse
)


class CodeGeneratorService:
    """代码生成器服务类"""
    
    def __init__(self):
        self.request_cache = {}

    async def test_connection(self, config: dict, test_prompt: str) -> str:
        """
        测试AI连接是否正常

        Args:
            config: 临时配置字典
            test_prompt: 测试提示词

        Returns:
            AI响应内容
        """
        try:
            # 根据提供商类型选择不同的测试方法
            provider = config.get("provider", "doubao")

            if provider == "doubao":
                return await self._test_doubao_connection(config, test_prompt)
            elif provider == "kimi":
                return await self._test_kimi_connection(config, test_prompt)
            elif provider == "deepseek":
                return await self._test_deepseek_connection(config, test_prompt)
            else:
                # 对于其他提供商，使用通用的OpenAI兼容接口测试
                return await self._test_openai_compatible_connection(config, test_prompt)

        except Exception as e:
            raise Exception(f"Connection test failed: {str(e)}")

    async def _test_doubao_connection(self, config: dict, test_prompt: str) -> str:
        """测试豆包连接"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": config.get("max_tokens", 100),
            "temperature": config.get("temperature", 0.7)
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{config.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3')}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _test_kimi_connection(self, config: dict, test_prompt: str) -> str:
        """测试Kimi连接"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": config.get("max_tokens", 100),
            "temperature": config.get("temperature", 0.7)
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{config.get('base_url', 'https://api.moonshot.cn/v1')}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _test_deepseek_connection(self, config: dict, test_prompt: str) -> str:
        """测试DeepSeek连接"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": config.get("max_tokens", 100),
            "temperature": config.get("temperature", 0.7)
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{config.get('base_url', 'https://api.deepseek.com/v1')}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _test_openai_compatible_connection(self, config: dict, test_prompt: str) -> str:
        """测试OpenAI兼容接口连接"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": config.get("max_tokens", 100),
            "temperature": config.get("temperature", 0.7)
        }

        # 根据提供商确定基础URL
        base_urls = {
            "openai": "https://api.openai.com/v1",
            "claude": "https://api.anthropic.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
            "qwen": "https://dashscope.aliyuncs.com/api/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4"
        }

        base_url = config.get('base_url') or base_urls.get(config['provider'], base_urls['openai'])

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def generate_code(self, request: CodeGenerateRequest) -> CodeGenerateResponse:
        """
        生成代码的主要方法
        
        Args:
            request: 代码生成请求
            
        Returns:
            代码生成响应
        """
        try:
            # 验证AI配置（测试环境跳过）
            if settings.environment != "test" and not validate_ai_config():
                raise ValueError("AI配置无效，请检查API密钥设置")
            
            # 构建Prompt
            prompt = self._build_prompt(request)
            
            # 调用AI生成代码
            ai_response = await self._call_ai_service(prompt, request)
            
            # 解析AI响应
            parsed_response = self._parse_ai_response(ai_response, request)
            
            return parsed_response
            
        except Exception as e:
            # 返回错误响应
            return CodeGenerateResponse(
                success=False,
                generated_code="",
                explanation=f"代码生成失败: {str(e)}",
                suggestions=["请检查网络连接和API配置", "尝试简化需求描述"]
            )
    
    def _build_prompt(self, request: CodeGenerateRequest) -> str:
        """
        构建AI Prompt模板 - 简化版，引擎和语言信息包含在description中

        Args:
            request: 代码生成请求

        Returns:
            构建好的prompt字符串
        """
        # 简化的prompt模板，不再依赖外部的引擎和语言参数
        prompt = f"""你是一个专业的游戏开发代码助手。请根据以下要求生成高质量的游戏代码。

## 任务要求
{request.description}

## 代码要求
- 代码风格：{request.code_style}
- 包含注释：{'是' if request.include_comments else '否'}
- 遵循最佳实践和编码规范
- 确保代码的可读性和可维护性
- 根据需求描述中指定的引擎和语言生成对应的代码

## 额外要求
{request.additional_requirements or '无特殊要求'}

## 输出格式要求
请按照以下JSON格式返回结果：
{{
    "code": "生成的完整代码",
    "explanation": "代码功能和实现原理的详细解释，使用换行符分段，包含：\n1. 代码功能概述\n2. 主要实现逻辑\n3. 关键技术点说明\n4. 使用注意事项\n5. 适用的引擎和语言信息",
    "dependencies": ["所需的依赖库或组件"],
    "usage_example": "使用示例代码",
    "suggestions": ["优化建议或注意事项"],
    "complexity": "代码复杂度评估(simple/medium/complex)"
}}

请确保代码：
1. 语法正确，可以直接运行
2. 遵循最佳实践和编码规范
3. 包含必要的错误处理
4. 性能优化合理
5. 注释清晰（如果要求包含注释）
6. 符合需求描述中指定的引擎和语言的规范

现在请生成代码："""

        return prompt
    
    # 移除了引擎和语言上下文方法，因为这些信息现在包含在模板描述中
    
    async def _call_ai_service(self, prompt: str, request: CodeGenerateRequest) -> str:
        """
        调用AI服务生成代码（带重试机制）

        Args:
            prompt: 构建好的prompt
            request: 原始请求

        Returns:
            AI响应文本
        """
        import asyncio

        max_retries = 3
        retry_delay = 2  # 秒

        for attempt in range(max_retries):
            try:
                # 获取AI配置
                ai_config = get_ai_config()

                # 添加provider字段
                ai_config["provider"] = settings.default_ai_provider

                # 根据提供商调用相应的API
                if ai_config["provider"] == "doubao":
                    return await self._call_doubao_api(prompt, ai_config)
                elif ai_config["provider"] == "kimi":
                    return await self._call_kimi_api(prompt, ai_config)
                elif ai_config["provider"] == "deepseek":
                    return await self._call_deepseek_api(prompt, ai_config)
                else:
                    # 其他提供商使用OpenAI兼容接口
                    return await self._call_openai_compatible_api(prompt, ai_config)

            except Exception as e:
                error_msg = str(e)

                # 检查是否是可重试的错误
                is_retryable = any(keyword in error_msg.lower() for keyword in [
                    'timeout', 'connection', 'network', 'temporary', 'rate limit'
                ])

                if attempt < max_retries - 1 and is_retryable:
                    # 等待后重试
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    # 最后一次尝试失败或不可重试的错误
                    if 'timeout' in error_msg.lower():
                        raise Exception(f"AI服务响应超时，请稍后重试。已尝试 {attempt + 1} 次。")
                    elif 'rate limit' in error_msg.lower():
                        raise Exception(f"API调用频率限制，请稍后重试。")
                    else:
                        raise Exception(f"代码生成失败: {error_msg}")

        # 理论上不会到达这里
        raise Exception("代码生成失败: 未知错误")

    async def _call_doubao_api(self, prompt: str, config: dict) -> str:
        """调用豆包API生成代码"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get("max_tokens", 2000),
            "temperature": config.get("temperature", 0.7)
        }

        # 代码生成需要更长时间，设置120秒超时
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_kimi_api(self, prompt: str, config: dict) -> str:
        """调用Kimi API生成代码"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get("max_tokens", 2000),
            "temperature": config.get("temperature", 0.7)
        }

        # Kimi代码生成需要更长时间，设置120秒超时
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_deepseek_api(self, prompt: str, config: dict) -> str:
        """调用DeepSeek API生成代码"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get("max_tokens", 2000),
            "temperature": config.get("temperature", 0.7)
        }

        # DeepSeek代码生成需要更长时间，设置120秒超时
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_openai_compatible_api(self, prompt: str, config: dict) -> str:
        """调用OpenAI兼容API生成代码"""
        import httpx

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get("max_tokens", 2000),
            "temperature": config.get("temperature", 0.7)
        }

        # OpenAI兼容API代码生成需要更长时间，设置120秒超时
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _generate_mock_code(self, request: CodeGenerateRequest) -> str:
        """生成模拟代码 - 基于描述内容推断类型"""
        # 简单的关键词检测来生成合适的模拟代码
        description_lower = request.description.lower()

        if "unity" in description_lower and "c#" in description_lower:
            return f"""using UnityEngine;

public class GeneratedScript : MonoBehaviour
{{
    // {request.description}

    void Start()
    {{
        // 初始化代码
        Debug.Log("脚本已启动");
    }}

    void Update()
    {{
        // 每帧更新逻辑
        // TODO: 实现具体功能
    }}
}}"""
        elif "python" in description_lower:
            return f"""# {request.description}
# 生成的Python代码

def main():
    print("Hello, DevPal!")
    # TODO: 实现具体功能

if __name__ == "__main__":
    main()"""
        else:
            return f"""// {request.description}
// 生成的代码

function main() {{
    console.log('Hello, DevPal!');
    // TODO: 实现具体功能
}}

main();"""
    
    def _get_mock_dependencies(self, request: CodeGenerateRequest) -> list:
        """获取模拟依赖 - 基于描述内容推断"""
        description_lower = request.description.lower()

        if "unity" in description_lower:
            return ["UnityEngine", "UnityEngine.UI"]
        elif "pygame" in description_lower:
            return ["pygame", "pygame.sprite"]
        elif "unreal" in description_lower:
            return ["UnrealEngine", "CoreUObject"]
        elif "godot" in description_lower:
            return ["Godot"]
        else:
            return []
    
    def _parse_ai_response(self, ai_response: str, request: CodeGenerateRequest) -> CodeGenerateResponse:
        """
        解析AI响应

        Args:
            ai_response: AI返回的原始响应
            request: 原始请求

        Returns:
            解析后的响应对象
        """
        try:
            # 首先尝试解析JSON响应
            try:
                response_data = json.loads(ai_response)
                return CodeGenerateResponse(
                    success=True,
                    generated_code=response_data.get("code", ""),
                    explanation=response_data.get("explanation", ""),
                    dependencies=response_data.get("dependencies", []),
                    usage_example=response_data.get("usage_example", ""),
                    suggestions=response_data.get("suggestions", []),
                    complexity=response_data.get("complexity", "medium")
                )
            except json.JSONDecodeError:
                # 如果不是JSON，则作为纯文本处理
                return self._parse_text_response(ai_response, request)

        except Exception as e:
            # 解析失败，返回错误响应
            return CodeGenerateResponse(
                success=False,
                generated_code="",
                explanation=f"响应解析失败: {str(e)}",
                suggestions=["请重试或联系技术支持"]
            )

    def _parse_text_response(self, ai_response: str, request: CodeGenerateRequest) -> CodeGenerateResponse:
        """
        解析纯文本AI响应

        Args:
            ai_response: AI返回的纯文本响应
            request: 原始请求

        Returns:
            解析后的响应对象
        """
        # 提取代码块（如果存在）
        import re

        # 查找代码块
        code_blocks = re.findall(r'```(?:csharp|cs|c#)?\s*\n(.*?)\n```', ai_response, re.DOTALL | re.IGNORECASE)

        if code_blocks:
            # 使用第一个代码块作为生成的代码
            generated_code = code_blocks[0].strip()
        else:
            # 如果没有代码块，使用整个响应
            generated_code = ai_response.strip()

        # 生成简单的解释
        explanation = f"基于您的需求生成了代码。请查看代码内容了解具体的引擎和语言信息。"

        return CodeGenerateResponse(
            success=True,
            generated_code=generated_code,
            explanation=explanation,
            dependencies=self._get_mock_dependencies(request),
            usage_example="// 将此脚本添加到游戏对象上即可使用",
            suggestions=[
                "建议在使用前测试功能",
                "可以根据需求调整参数",
                "注意性能优化"
            ],
            complexity="medium"
        )


# 创建全局服务实例
code_generator_service = CodeGeneratorService()
