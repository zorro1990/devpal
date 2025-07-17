"""
代码分析器数据模型
定义代码分析相关的请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class AnalysisType(str, Enum):
    """分析类型枚举"""
    EXPLAIN = "explain"  # 解释与文档
    OPTIMIZE = "optimize"  # 优化与重构
    DOCUMENT = "document"  # 生成文档


class CodeLanguage(str, Enum):
    """代码语言枚举"""
    CSHARP = "csharp"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    GDSCRIPT = "gdscript"
    LUA = "lua"
    HLSL = "hlsl"
    GLSL = "glsl"
    AUTO = "auto"  # 自动检测


class CodeAnalyzeRequest(BaseModel):
    """代码分析请求模型"""
    
    code: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="要分析的代码内容"
    )
    
    language: CodeLanguage = Field(
        default=CodeLanguage.AUTO,
        description="代码语言，auto表示自动检测"
    )
    
    analysis_type: AnalysisType = Field(
        default=AnalysisType.EXPLAIN,
        description="分析类型"
    )
    
    context: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="代码上下文信息，如项目背景、使用场景等"
    )
    
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="重点关注的分析领域，如性能、安全性、可读性等"
    )
    
    include_suggestions: bool = Field(
        default=True,
        description="是否包含改进建议"
    )
    
    detail_level: str = Field(
        default="medium",
        description="分析详细程度 (basic, medium, detailed)"
    )


class CodeExplanation(BaseModel):
    """代码解释模型"""
    
    overview: str = Field(
        description="代码整体功能概述"
    )
    
    detailed_explanation: str = Field(
        description="详细的逐行或逐块解释"
    )
    
    key_concepts: List[str] = Field(
        description="涉及的关键概念和技术"
    )
    
    complexity_analysis: str = Field(
        description="复杂度分析"
    )
    
    potential_issues: Optional[List[str]] = Field(
        default=None,
        description="潜在问题或注意事项"
    )


class CodeOptimization(BaseModel):
    """代码优化模型"""
    
    optimized_code: str = Field(
        description="优化后的代码"
    )
    
    optimization_summary: str = Field(
        description="优化总结"
    )
    
    changes_made: List[str] = Field(
        description="具体的修改内容"
    )
    
    performance_impact: str = Field(
        description="性能影响评估"
    )
    
    before_after_comparison: Dict[str, Any] = Field(
        description="优化前后对比"
    )


class CodeDocumentation(BaseModel):
    """代码文档模型"""
    
    documented_code: str = Field(
        description="添加了文档注释的代码"
    )
    
    api_documentation: Optional[str] = Field(
        default=None,
        description="API文档"
    )
    
    usage_examples: List[str] = Field(
        description="使用示例"
    )
    
    parameter_descriptions: Optional[Dict[str, str]] = Field(
        default=None,
        description="参数说明"
    )


class CodeAnalyzeResponse(BaseModel):
    """代码分析响应模型"""
    
    success: bool = Field(
        description="分析是否成功"
    )
    
    detected_language: CodeLanguage = Field(
        description="检测到的代码语言"
    )
    
    analysis_type: AnalysisType = Field(
        description="执行的分析类型"
    )
    
    explanation: Optional[CodeExplanation] = Field(
        default=None,
        description="代码解释结果"
    )
    
    optimization: Optional[CodeOptimization] = Field(
        default=None,
        description="代码优化结果"
    )
    
    documentation: Optional[CodeDocumentation] = Field(
        default=None,
        description="代码文档结果"
    )
    
    general_suggestions: List[str] = Field(
        description="通用改进建议"
    )
    
    code_quality_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="代码质量评分 (0-100)"
    )
    
    analysis_metadata: Dict[str, Any] = Field(
        description="分析元数据，如耗时、使用的模型等"
    )


class LanguageDetectionResponse(BaseModel):
    """语言检测响应模型"""
    
    detected_language: CodeLanguage = Field(
        description="检测到的编程语言"
    )
    
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="检测置信度"
    )
    
    possible_languages: List[Dict[str, float]] = Field(
        description="可能的语言及其概率"
    )


class CodeMetrics(BaseModel):
    """代码指标模型"""
    
    lines_of_code: int = Field(
        description="代码行数"
    )
    
    cyclomatic_complexity: Optional[int] = Field(
        default=None,
        description="圈复杂度"
    )
    
    function_count: int = Field(
        description="函数数量"
    )
    
    class_count: int = Field(
        description="类数量"
    )
    
    comment_ratio: float = Field(
        ge=0.0,
        le=1.0,
        description="注释比例"
    )
    
    maintainability_index: Optional[float] = Field(
        default=None,
        description="可维护性指数"
    )


class AnalysisErrorResponse(BaseModel):
    """分析错误响应模型"""
    
    success: bool = Field(
        default=False,
        description="分析是否成功"
    )
    
    error_code: str = Field(
        description="错误代码"
    )
    
    error_message: str = Field(
        description="错误信息"
    )
    
    suggestions: List[str] = Field(
        description="解决建议"
    )
