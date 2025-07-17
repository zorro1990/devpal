"""
代码分析器API端点
定义代码分析相关的路由
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import BaseModel, Field

from app.api.v1.schemas.analyzer import (
    CodeAnalyzeRequest,
    CodeAnalyzeResponse,
    AnalysisType,
    CodeLanguage,
    LanguageDetectionResponse,
    CodeMetrics,
    AnalysisErrorResponse
)
from app.services.code_analyzer import code_analyzer_service
from app.core.config import settings

# 创建路由器
router = APIRouter(prefix="/analyze", tags=["代码分析器"])


# 前端期望的统一分析请求模型
class UnifiedAnalyzeRequest(BaseModel):
    """统一代码分析请求模型（前端兼容）"""
    code: str = Field(..., description="要分析的代码内容")
    language: str = Field(..., description="编程语言")
    analysis_types: List[str] = Field(..., description="分析类型列表")
    options: Dict[str, Any] = Field(default_factory=dict, description="分析选项")


# 前端期望的统一分析响应模型
class UnifiedAnalyzeResponse(BaseModel):
    """统一代码分析响应模型（前端兼容）"""
    id: str = Field(..., description="分析任务ID")
    status: str = Field(..., description="分析状态")
    results: List[Dict[str, Any]] = Field(..., description="分析结果列表")
    timestamp: str = Field(..., description="分析时间戳")


@router.post(
    "/code",
    response_model=UnifiedAnalyzeResponse,
    summary="统一代码分析接口",
    description="前端统一调用的代码分析接口，支持多种分析类型"
)
async def analyze_code_unified(request: UnifiedAnalyzeRequest) -> UnifiedAnalyzeResponse:
    """
    统一代码分析端点（前端兼容）

    Args:
        request: 统一分析请求

    Returns:
        统一分析响应
    """
    try:
        import uuid
        from datetime import datetime

        # 生成分析任务ID
        analysis_id = str(uuid.uuid4())

        # 验证请求参数
        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="代码内容不能为空"
            )

        if len(request.code) > 10000:
            raise HTTPException(
                status_code=400,
                detail="代码长度不能超过10000字符"
            )

        # 映射语言名称
        language_mapping = {
            'csharp': CodeLanguage.CSHARP,
            'c#': CodeLanguage.CSHARP,
            'cpp': CodeLanguage.CPP,
            'c++': CodeLanguage.CPP,
            'javascript': CodeLanguage.JAVASCRIPT,
            'js': CodeLanguage.JAVASCRIPT,
            'typescript': CodeLanguage.TYPESCRIPT,
            'ts': CodeLanguage.TYPESCRIPT,
            'python': CodeLanguage.PYTHON,
            'py': CodeLanguage.PYTHON,
            'gdscript': CodeLanguage.GDSCRIPT,
            'lua': CodeLanguage.LUA,
        }

        detected_language = language_mapping.get(
            request.language.lower(),
            CodeLanguage.AUTO
        )

        # 处理分析类型
        analysis_results = []

        # 获取自定义提示词
        custom_prompt = request.options.get('custom_prompt', '')

        # 如果有自定义提示词，使用AI服务进行分析
        if custom_prompt:
            # 构建分析请求
            analyze_request = CodeAnalyzeRequest(
                code=request.code,
                language=detected_language,
                analysis_type=AnalysisType.EXPLAIN,  # 默认使用解释类型
                context=custom_prompt,
                focus_areas=request.options.get('focus_areas', []),
                include_suggestions=request.options.get('include_comments', True),
                detail_level=request.options.get('detail_level', 'medium')
            )

            # 调用分析服务
            response = await code_analyzer_service.analyze_code(analyze_request)

            if response.success:
                # 构建结果
                result = {
                    "type": "quality_review",
                    "title": "代码质量审查",
                    "content": "",
                    "suggestions": [],
                    "codeBlocks": []
                }

                if response.explanation:
                    result["content"] = f"""
## 代码概述
{response.explanation.overview}

## 详细分析
{response.explanation.detailed_explanation}

## 关键概念
{', '.join(response.explanation.key_concepts)}

## 复杂度分析
{response.explanation.complexity_analysis}
"""

                    # 基于实际问题生成具体建议
                    if response.explanation.potential_issues:
                        suggestions = []
                        for i, issue in enumerate(response.explanation.potential_issues):
                            # 解析问题并生成具体建议
                            if "移动与物理冲突" in issue or "transform.Translate" in issue:
                                suggestions.append({
                                    "type": "warning",
                                    "severity": "high",
                                    "title": "移动方式冲突",
                                    "description": "建议使用Rigidbody.MovePosition()替代transform.Translate()以保持物理一致性"
                                })
                            elif "无限跳跃" in issue or "地面检测" in issue:
                                suggestions.append({
                                    "type": "warning",
                                    "severity": "medium",
                                    "title": "缺少地面检测",
                                    "description": "建议添加地面检测逻辑，如使用Raycast或碰撞检测来限制跳跃"
                                })
                            elif "空引用" in issue or "null" in issue:
                                suggestions.append({
                                    "type": "error",
                                    "severity": "high",
                                    "title": "空引用风险",
                                    "description": "建议在Start()中添加null检查：if (rb == null) Debug.LogError(\"Missing Rigidbody component\")"
                                })
                            elif "硬编码" in issue:
                                suggestions.append({
                                    "type": "improvement",
                                    "severity": "low",
                                    "title": "硬编码数值",
                                    "description": "建议将跳跃力度设为public变量：public float jumpForce = 10f"
                                })
                            else:
                                suggestions.append({
                                    "type": "warning",
                                    "severity": "medium",
                                    "title": f"代码问题 {i+1}",
                                    "description": issue[:100] + "..." if len(issue) > 100 else issue
                                })
                        result["suggestions"] = suggestions

                # 添加通用建议
                if response.general_suggestions:
                    for suggestion in response.general_suggestions:
                        result["suggestions"].append({
                            "type": "improvement",
                            "severity": "low",
                            "title": "改进建议",
                            "description": suggestion
                        })

                # 添加质量评分
                if response.code_quality_score:
                    result["content"] += f"\n\n## 代码质量评分\n{response.code_quality_score}/100"

                analysis_results.append(result)
            else:
                # 分析失败时返回错误信息
                analysis_results.append({
                    "type": "error",
                    "title": "分析失败",
                    "content": "代码分析过程中发生错误，请检查代码格式或稍后重试。",
                    "suggestions": [
                        {
                            "type": "error",
                            "severity": "high",
                            "title": "分析错误",
                            "description": "无法完成代码分析，请确保代码格式正确"
                        }
                    ]
                })

        # 返回统一响应
        return UnifiedAnalyzeResponse(
            id=analysis_id,
            status="completed" if analysis_results else "failed",
            results=analysis_results,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        # 返回错误响应
        return UnifiedAnalyzeResponse(
            id=str(uuid.uuid4()),
            status="failed",
            results=[{
                "type": "error",
                "title": "系统错误",
                "content": f"分析过程中发生系统错误: {str(e)}",
                "suggestions": [
                    {
                        "type": "error",
                        "severity": "high",
                        "title": "系统错误",
                        "description": "请稍后重试或联系技术支持"
                    }
                ]
            }],
            timestamp=datetime.now().isoformat()
        )


@router.post(
    "/explain",
    response_model=CodeAnalyzeResponse,
    summary="解释代码功能",
    description="分析并解释代码的功能、实现原理和关键概念"
)
async def explain_code(request: CodeAnalyzeRequest) -> CodeAnalyzeResponse:
    """
    解释代码功能的端点
    
    Args:
        request: 代码分析请求
        
    Returns:
        包含代码解释的分析结果
        
    Raises:
        HTTPException: 当分析失败时抛出异常
    """
    try:
        # 设置分析类型为解释
        request.analysis_type = AnalysisType.EXPLAIN
        
        # 验证请求参数
        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="代码内容不能为空"
            )
        
        if len(request.code) > 10000:
            raise HTTPException(
                status_code=400,
                detail="代码长度不能超过10000字符"
            )
        
        # 调用分析服务
        response = await code_analyzer_service.analyze_code(request)
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail="代码分析失败，请稍后重试"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"代码解释失败: {str(e)}"
        )


@router.post(
    "/optimize",
    response_model=CodeAnalyzeResponse,
    summary="优化代码",
    description="分析代码并提供优化建议和重构方案"
)
async def optimize_code(request: CodeAnalyzeRequest) -> CodeAnalyzeResponse:
    """
    优化代码的端点
    
    Args:
        request: 代码分析请求
        
    Returns:
        包含代码优化结果的分析响应
    """
    try:
        # 设置分析类型为优化
        request.analysis_type = AnalysisType.OPTIMIZE
        
        # 验证请求参数
        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="代码内容不能为空"
            )
        
        # 调用分析服务
        response = await code_analyzer_service.analyze_code(request)
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail="代码优化失败，请稍后重试"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"代码优化失败: {str(e)}"
        )


@router.post(
    "/document",
    response_model=CodeAnalyzeResponse,
    summary="生成代码文档",
    description="为代码生成详细的文档和注释"
)
async def document_code(request: CodeAnalyzeRequest) -> CodeAnalyzeResponse:
    """
    生成代码文档的端点
    
    Args:
        request: 代码分析请求
        
    Returns:
        包含代码文档的分析结果
    """
    try:
        # 设置分析类型为文档生成
        request.analysis_type = AnalysisType.DOCUMENT
        
        # 验证请求参数
        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="代码内容不能为空"
            )
        
        # 调用分析服务
        response = await code_analyzer_service.analyze_code(request)
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail="文档生成失败，请稍后重试"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文档生成失败: {str(e)}"
        )


class LanguageDetectionRequest(BaseModel):
    """语言检测请求模型"""
    code: str = Field(..., description="要检测的代码内容")


@router.post(
    "/detect-language",
    response_model=LanguageDetectionResponse,
    summary="检测代码语言",
    description="自动检测代码的编程语言"
)
async def detect_language(request: LanguageDetectionRequest) -> LanguageDetectionResponse:
    """
    检测代码语言的端点
    
    Args:
        code: 要检测的代码内容
        
    Returns:
        语言检测结果
    """
    try:
        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="代码内容不能为空"
            )

        # 使用分析服务检测语言
        detected_language = code_analyzer_service._detect_language(request.code)
        
        return LanguageDetectionResponse(
            detected_language=detected_language,
            confidence=0.85,  # 模拟置信度
            possible_languages=[
                {"language": detected_language.value, "probability": 0.85},
                {"language": "auto", "probability": 0.15}
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"语言检测失败: {str(e)}"
        )


class MetricsRequest(BaseModel):
    """代码指标请求模型"""
    code: str = Field(..., description="要分析的代码内容")
    language: CodeLanguage = Field(CodeLanguage.AUTO, description="代码语言")


@router.post(
    "/metrics",
    response_model=CodeMetrics,
    summary="计算代码指标",
    description="计算代码的各种质量指标和统计信息"
)
async def calculate_metrics(request: MetricsRequest) -> CodeMetrics:
    """
    计算代码指标的端点
    
    Args:
        code: 要分析的代码内容
        language: 代码语言
        
    Returns:
        代码指标统计
    """
    try:
        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="代码内容不能为空"
            )

        # 计算基础指标
        lines = request.code.split('\n')
        lines_of_code = len([line for line in lines if line.strip()])

        # 计算注释比例
        comment_patterns = [r'//.*', r'#.*', r'/\*.*?\*/', r'""".*?"""', r"'''.*?'''"]
        comment_lines = 0
        for pattern in comment_patterns:
            import re
            comment_lines += len(re.findall(pattern, request.code, re.DOTALL))

        comment_ratio = comment_lines / lines_of_code if lines_of_code > 0 else 0

        # 计算函数和类数量
        import re
        function_patterns = [r'def\s+\w+', r'function\s+\w+', r'void\s+\w+', r'public\s+\w+\s+\w+\(']
        function_count = 0
        for pattern in function_patterns:
            function_count += len(re.findall(pattern, request.code))

        class_patterns = [r'class\s+\w+', r'public\s+class\s+\w+', r'interface\s+\w+']
        class_count = 0
        for pattern in class_patterns:
            class_count += len(re.findall(pattern, request.code))
        
        return CodeMetrics(
            lines_of_code=lines_of_code,
            cyclomatic_complexity=None,  # 需要更复杂的分析
            function_count=function_count,
            class_count=class_count,
            comment_ratio=min(comment_ratio, 1.0),
            maintainability_index=None  # 需要更复杂的分析
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"指标计算失败: {str(e)}"
        )


@router.get(
    "/supported-languages",
    response_model=Dict[str, str],
    summary="获取支持的编程语言",
    description="返回所有支持分析的编程语言列表"
)
async def get_supported_languages() -> Dict[str, str]:
    """获取支持的编程语言列表"""
    return {
        lang.value: lang.value.upper()
        for lang in CodeLanguage
        if lang != CodeLanguage.AUTO
    }


@router.get(
    "/analysis-types",
    response_model=Dict[str, str],
    summary="获取支持的分析类型",
    description="返回所有支持的代码分析类型"
)
async def get_analysis_types() -> Dict[str, str]:
    """获取支持的分析类型列表"""
    return {
        analysis_type.value: {
            "explain": "代码解释与文档",
            "optimize": "代码优化与重构", 
            "document": "生成代码文档"
        }[analysis_type.value]
        for analysis_type in AnalysisType
    }


@router.get(
    "/health",
    summary="分析器健康检查",
    description="检查代码分析器服务的健康状态"
)
async def analyzer_health_check():
    """分析器健康检查"""
    try:
        return {
            "status": "healthy",
            "service": "Code Analyzer",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "explain": "available",
                "optimize": "available", 
                "document": "available",
                "language_detection": "available",
                "metrics": "available"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"分析器服务不可用: {str(e)}"
        )
