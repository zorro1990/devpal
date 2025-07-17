"""
代码分析器服务
实现代码分析、解释和优化功能
"""

import asyncio
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.config import settings, get_ai_config, validate_ai_config
from app.api.v1.schemas.analyzer import (
    CodeAnalyzeRequest,
    CodeAnalyzeResponse,
    CodeExplanation,
    CodeOptimization,
    CodeDocumentation,
    AnalysisType,
    CodeLanguage,
    LanguageDetectionResponse,
    CodeMetrics
)


class CodeAnalyzerService:
    """代码分析器服务类"""
    
    def __init__(self):
        self.language_patterns = {
            CodeLanguage.CSHARP: [r'using\s+\w+;', r'public\s+class', r'void\s+\w+\(', r'MonoBehaviour'],
            CodeLanguage.CPP: [r'#include\s*<', r'std::', r'int\s+main\(', r'class\s+\w+'],
            CodeLanguage.PYTHON: [r'import\s+\w+', r'def\s+\w+\(', r'if\s+__name__', r'print\('],
            CodeLanguage.JAVASCRIPT: [r'function\s+\w+', r'var\s+\w+', r'console\.log', r'=>'],
            CodeLanguage.TYPESCRIPT: [r'interface\s+\w+', r'type\s+\w+', r':\s*\w+\s*='],
            CodeLanguage.GDSCRIPT: [r'extends\s+\w+', r'func\s+\w+', r'var\s+\w+:', r'_ready\(\)'],
            CodeLanguage.LUA: [r'function\s+\w+', r'local\s+\w+', r'end$', r'require\('],
        }
    
    async def analyze_code(self, request: CodeAnalyzeRequest) -> CodeAnalyzeResponse:
        """
        分析代码的主要方法
        
        Args:
            request: 代码分析请求
            
        Returns:
            代码分析响应
        """
        try:
            # 检测代码语言
            detected_language = self._detect_language(request.code)
            if request.language == CodeLanguage.AUTO:
                request.language = detected_language
            
            # 根据分析类型执行不同的分析
            if request.analysis_type == AnalysisType.EXPLAIN:
                explanation = await self._explain_code(request)
                return CodeAnalyzeResponse(
                    success=True,
                    detected_language=detected_language,
                    analysis_type=request.analysis_type,
                    explanation=explanation,
                    general_suggestions=self._get_general_suggestions(request),
                    code_quality_score=self._calculate_quality_score(request.code),
                    analysis_metadata=self._get_analysis_metadata()
                )
            
            elif request.analysis_type == AnalysisType.OPTIMIZE:
                optimization = await self._optimize_code(request)
                return CodeAnalyzeResponse(
                    success=True,
                    detected_language=detected_language,
                    analysis_type=request.analysis_type,
                    optimization=optimization,
                    general_suggestions=self._get_general_suggestions(request),
                    code_quality_score=self._calculate_quality_score(request.code),
                    analysis_metadata=self._get_analysis_metadata()
                )
            
            elif request.analysis_type == AnalysisType.DOCUMENT:
                documentation = await self._document_code(request)
                return CodeAnalyzeResponse(
                    success=True,
                    detected_language=detected_language,
                    analysis_type=request.analysis_type,
                    documentation=documentation,
                    general_suggestions=self._get_general_suggestions(request),
                    code_quality_score=self._calculate_quality_score(request.code),
                    analysis_metadata=self._get_analysis_metadata()
                )
            
            else:
                raise ValueError(f"不支持的分析类型: {request.analysis_type}")
                
        except Exception as e:
            return CodeAnalyzeResponse(
                success=False,
                detected_language=CodeLanguage.AUTO,
                analysis_type=request.analysis_type,
                general_suggestions=[f"分析失败: {str(e)}", "请检查代码格式和网络连接"],
                analysis_metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
            )
    
    def _detect_language(self, code: str) -> CodeLanguage:
        """
        检测代码语言
        
        Args:
            code: 代码内容
            
        Returns:
            检测到的语言
        """
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, code, re.IGNORECASE | re.MULTILINE))
                score += matches
            scores[language] = score
        
        if not scores or max(scores.values()) == 0:
            return CodeLanguage.AUTO
        
        return max(scores, key=scores.get)
    
    async def _explain_code(self, request: CodeAnalyzeRequest) -> CodeExplanation:
        """
        解释代码功能
        
        Args:
            request: 分析请求
            
        Returns:
            代码解释结果
        """
        # 构建解释prompt
        prompt = self._build_explanation_prompt(request)
        
        # 调用AI服务
        ai_response = await self._call_ai_service(prompt)
        
        # 解析响应
        return self._parse_explanation_response(ai_response, request)
    
    async def _optimize_code(self, request: CodeAnalyzeRequest) -> CodeOptimization:
        """
        优化代码
        
        Args:
            request: 分析请求
            
        Returns:
            代码优化结果
        """
        # 构建优化prompt
        prompt = self._build_optimization_prompt(request)
        
        # 调用AI服务
        ai_response = await self._call_ai_service(prompt)
        
        # 解析响应
        return self._parse_optimization_response(ai_response, request)
    
    async def _document_code(self, request: CodeAnalyzeRequest) -> CodeDocumentation:
        """
        为代码生成文档
        
        Args:
            request: 分析请求
            
        Returns:
            代码文档结果
        """
        # 构建文档prompt
        prompt = self._build_documentation_prompt(request)
        
        # 调用AI服务
        ai_response = await self._call_ai_service(prompt)
        
        # 解析响应
        return self._parse_documentation_response(ai_response, request)
    
    def _build_explanation_prompt(self, request: CodeAnalyzeRequest) -> str:
        """构建代码解释prompt"""
        return f"""你是一个专业的代码分析师，请详细分析以下{request.language.value}代码。

## 代码内容
```{request.language.value}
{request.code}
```

## 分析要求
{request.context or '请对以下代码进行详细的质量审查'}

请严格按照以下JSON格式返回分析结果，不要添加任何其他文本：

{{
    "overview": "代码整体功能的简洁概述（1-2句话）",
    "detailed_explanation": "详细的代码分析，包括功能、实现方式、设计模式等",
    "key_concepts": ["关键技术概念1", "关键技术概念2", "关键技术概念3"],
    "complexity_analysis": "代码复杂度评估和分析",
    "potential_issues": ["具体的潜在问题1", "具体的潜在问题2", "具体的潜在问题3"],
    "code_quality_score": 75
}}

注意：
1. 请确保返回的是有效的JSON格式
2. potential_issues应该包含具体的、可操作的问题描述
3. 所有字段都必须填写，不能为空
4. code_quality_score应该是0-100的整数"""
    
    def _build_optimization_prompt(self, request: CodeAnalyzeRequest) -> str:
        """构建代码优化prompt"""
        return f"""你是一个专业的代码优化专家，请分析并优化以下{request.language.value}代码。

## 原始代码
```{request.language.value}
{request.code}
```

## 上下文信息
{request.context or '无特殊上下文'}

## 优化重点
{', '.join(request.focus_areas) if request.focus_areas else '性能、可读性、可维护性'}

请按照以下JSON格式返回优化结果：
{{
    "optimized_code": "优化后的完整代码",
    "optimization_summary": "优化总结",
    "changes_made": ["具体修改1", "具体修改2"],
    "performance_impact": "性能影响评估",
    "before_after_comparison": {{
        "before": "优化前的关键指标",
        "after": "优化后的关键指标"
    }}
}}"""
    
    def _build_documentation_prompt(self, request: CodeAnalyzeRequest) -> str:
        """构建代码文档prompt"""
        return f"""你是一个专业的技术文档编写专家，请为以下{request.language.value}代码生成完整的文档。

## 代码内容
```{request.language.value}
{request.code}
```

## 上下文信息
{request.context or '无特殊上下文'}

请按照以下JSON格式返回文档结果：
{{
    "documented_code": "添加了详细注释的代码",
    "api_documentation": "API文档说明",
    "usage_examples": ["使用示例1", "使用示例2"],
    "parameter_descriptions": {{
        "参数名": "参数说明"
    }}
}}"""
    
    async def _call_ai_service(self, prompt: str) -> str:
        """调用AI服务"""
        try:
            import httpx
            from app.core.config import settings

            # 构建请求数据
            request_data = {
                "model": settings.doubao_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            # 构建请求头
            headers = {
                "Authorization": f"Bearer {settings.doubao_api_key}",
                "Content-Type": "application/json"
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.doubao_base_url}/chat/completions",
                    json=request_data,
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_content = result["choices"][0]["message"]["content"]
                    return ai_content
                else:
                    # AI调用失败时返回默认响应
                    return json.dumps({
                        "overview": "代码分析服务暂时不可用",
                        "detailed_explanation": "AI服务调用失败，请稍后重试",
                        "key_concepts": ["代码分析", "服务异常"],
                        "complexity_analysis": "无法分析",
                        "potential_issues": ["AI服务连接失败", "请检查网络连接"]
                    }, ensure_ascii=False)

        except Exception as e:
            # 异常时返回默认响应
            return json.dumps({
                "overview": f"代码分析过程中发生错误: {str(e)}",
                "detailed_explanation": "由于技术问题，无法完成详细分析",
                "key_concepts": ["错误处理", "异常情况"],
                "complexity_analysis": "分析中断",
                "potential_issues": ["系统异常", "请稍后重试"]
            }, ensure_ascii=False)
    
    def _parse_explanation_response(self, ai_response: str, request: CodeAnalyzeRequest) -> CodeExplanation:
        """解析解释响应"""
        try:
            data = json.loads(ai_response)
            return CodeExplanation(
                overview=data.get("overview", "代码功能概述"),
                detailed_explanation=data.get("detailed_explanation", "详细解释"),
                key_concepts=data.get("key_concepts", []),
                complexity_analysis=data.get("complexity_analysis", "复杂度分析"),
                potential_issues=data.get("potential_issues", [])
            )
        except json.JSONDecodeError:
            # JSON解析失败时，尝试从文本中提取有用信息
            return self._parse_text_response(ai_response, request)

    def _parse_text_response(self, ai_response: str, request: CodeAnalyzeRequest) -> CodeExplanation:
        """解析文本格式的AI响应"""
        # 尝试从文本中提取结构化信息
        overview = "代码分析完成"
        detailed_explanation = ai_response
        key_concepts = []
        complexity_analysis = "中等复杂度"
        potential_issues = []

        # 简单的文本解析逻辑
        if "Unity" in ai_response:
            key_concepts.append("Unity引擎")
        if "MonoBehaviour" in ai_response:
            key_concepts.append("Unity脚本")
        if "Input" in ai_response:
            key_concepts.append("输入系统")
        if "Transform" in ai_response:
            key_concepts.append("Transform组件")
        if "Rigidbody" in ai_response:
            key_concepts.append("物理组件")

        # 提取潜在问题
        if "问题" in ai_response or "issue" in ai_response.lower():
            potential_issues.append("代码中可能存在需要优化的地方")
        if "性能" in ai_response or "performance" in ai_response.lower():
            potential_issues.append("建议关注性能优化")
        if "安全" in ai_response or "security" in ai_response.lower():
            potential_issues.append("建议进行安全性检查")

        return CodeExplanation(
            overview=overview,
            detailed_explanation=detailed_explanation,
            key_concepts=key_concepts,
            complexity_analysis=complexity_analysis,
            potential_issues=potential_issues
        )
    
    def _parse_optimization_response(self, ai_response: str, request: CodeAnalyzeRequest) -> CodeOptimization:
        """解析优化响应"""
        try:
            data = json.loads(ai_response)
            return CodeOptimization(
                optimized_code=data.get("optimized_code", request.code),
                optimization_summary=data.get("optimization_summary", "优化总结"),
                changes_made=data.get("changes_made", []),
                performance_impact=data.get("performance_impact", "性能影响评估"),
                before_after_comparison=data.get("before_after_comparison", {})
            )
        except json.JSONDecodeError:
            return CodeOptimization(
                optimized_code=request.code,
                optimization_summary="优化失败",
                changes_made=["响应解析错误"],
                performance_impact="无法评估",
                before_after_comparison={}
            )
    
    def _parse_documentation_response(self, ai_response: str, request: CodeAnalyzeRequest) -> CodeDocumentation:
        """解析文档响应"""
        try:
            data = json.loads(ai_response)
            return CodeDocumentation(
                documented_code=data.get("documented_code", request.code),
                api_documentation=data.get("api_documentation"),
                usage_examples=data.get("usage_examples", []),
                parameter_descriptions=data.get("parameter_descriptions")
            )
        except json.JSONDecodeError:
            return CodeDocumentation(
                documented_code=request.code,
                usage_examples=["文档生成失败"],
                parameter_descriptions={}
            )
    
    def _get_general_suggestions(self, request: CodeAnalyzeRequest) -> List[str]:
        """获取通用建议"""
        suggestions = []
        
        # 基于代码长度的建议
        if len(request.code) > 5000:
            suggestions.append("代码较长，建议考虑模块化拆分")
        
        # 基于语言的建议
        if request.language == CodeLanguage.CSHARP:
            suggestions.append("建议遵循C#编码规范，使用PascalCase命名")
        elif request.language == CodeLanguage.PYTHON:
            suggestions.append("建议遵循PEP 8编码规范")
        
        # 通用建议
        suggestions.extend([
            "建议添加单元测试",
            "考虑添加错误处理机制",
            "定期进行代码审查"
        ])
        
        return suggestions
    
    def _calculate_quality_score(self, code: str) -> int:
        """计算代码质量评分"""
        score = 50  # 基础分数
        
        # 基于代码长度
        lines = len(code.split('\n'))
        if 10 <= lines <= 100:
            score += 10
        
        # 基于注释比例
        comment_lines = len([line for line in code.split('\n') if line.strip().startswith(('//', '#', '/*'))])
        comment_ratio = comment_lines / lines if lines > 0 else 0
        if comment_ratio > 0.1:
            score += 15
        
        # 基于函数数量
        function_count = len(re.findall(r'(def |function |void |public |private )', code))
        if function_count > 0:
            score += 10
        
        return min(score, 100)
    
    def _get_analysis_metadata(self) -> Dict[str, Any]:
        """获取分析元数据"""
        return {
            "timestamp": datetime.now().isoformat(),
            "analyzer_version": "1.0.0",
            "ai_provider": settings.default_ai_provider
        }


# 创建全局服务实例
code_analyzer_service = CodeAnalyzerService()
