"""
代码生成器数据模型
定义请求和响应的Pydantic模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class GameEngine(str, Enum):
    """支持的游戏引擎枚举"""
    UNITY = "unity"
    UNREAL = "unreal"
    GODOT = "godot"
    COCOS2D = "cocos2d"
    PYGAME = "pygame"
    VANILLA = "vanilla"


class ProgrammingLanguage(str, Enum):
    """支持的编程语言枚举"""
    CSHARP = "csharp"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    GDSCRIPT = "gdscript"
    LUA = "lua"
    HLSL = "hlsl"
    GLSL = "glsl"


class CodeGenerateRequest(BaseModel):
    """代码生成请求模型 - 简化版，只保留核心参数"""

    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="代码需求描述，详细说明要实现的功能（包含引擎和语言信息）"
    )

    additional_requirements: Optional[str] = Field(
        default=None,
        max_length=500,
        description="额外要求或约束条件"
    )

    include_comments: bool = Field(
        default=True,
        description="是否包含详细注释"
    )

    code_style: Optional[str] = Field(
        default="standard",
        description="代码风格偏好 (standard, compact, verbose)"
    )


class CodeGenerateResponse(BaseModel):
    """代码生成响应模型 - 简化版，移除冗余的引擎和语言字段"""

    success: bool = Field(
        description="生成是否成功"
    )

    generated_code: str = Field(
        description="生成的代码内容"
    )

    explanation: str = Field(
        description="代码解释和使用说明（包含引擎和语言信息）"
    )

    suggestions: Optional[List[str]] = Field(
        default=None,
        description="优化建议或相关提示"
    )

    dependencies: Optional[List[str]] = Field(
        default=None,
        description="所需的依赖库或组件"
    )

    usage_example: Optional[str] = Field(
        default=None,
        description="使用示例"
    )

    estimated_complexity: Optional[str] = Field(
        default=None,
        description="代码复杂度评估 (simple, medium, complex)"
    )


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    success: bool = Field(
        default=False,
        description="操作是否成功"
    )
    
    error_code: str = Field(
        description="错误代码"
    )
    
    error_message: str = Field(
        description="错误信息"
    )
    
    details: Optional[str] = Field(
        default=None,
        description="详细错误信息"
    )


class GenerationStatus(BaseModel):
    """生成状态模型"""
    
    request_id: str = Field(
        description="请求ID"
    )
    
    status: str = Field(
        description="状态 (pending, processing, completed, failed)"
    )
    
    progress: int = Field(
        ge=0,
        le=100,
        description="进度百分比"
    )
    
    estimated_time: Optional[int] = Field(
        default=None,
        description="预估剩余时间（秒）"
    )
    
    message: Optional[str] = Field(
        default=None,
        description="状态消息"
    )
