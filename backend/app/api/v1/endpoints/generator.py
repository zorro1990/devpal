"""
代码生成器API端点
定义代码生成相关的路由
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uuid
from datetime import datetime

from app.api.v1.schemas.generator import (
    CodeGenerateRequest,
    CodeGenerateResponse,
    ErrorResponse,
    GenerationStatus
)
from app.services.code_generator import code_generator_service
from app.core.config import settings

# 创建路由器
router = APIRouter(prefix="/generate", tags=["代码生成器"])

# 存储生成任务状态
generation_tasks: Dict[str, Dict[str, Any]] = {}


@router.post(
    "/code",
    response_model=CodeGenerateResponse,
    summary="生成游戏代码",
    description="根据用户描述生成对应的游戏代码"
)
async def generate_code(request: CodeGenerateRequest) -> CodeGenerateResponse:
    """
    生成游戏代码的主要端点
    
    Args:
        request: 代码生成请求
        
    Returns:
        生成的代码和相关信息
        
    Raises:
        HTTPException: 当生成失败时抛出异常
    """
    try:
        # 验证请求参数
        if not request.description.strip():
            raise HTTPException(
                status_code=400,
                detail="代码描述不能为空"
            )
        
        # 调用生成服务
        response = await code_generator_service.generate_code(request)
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=response.explanation
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"代码生成失败: {str(e)}"
        )


@router.post(
    "/code/async",
    response_model=GenerationStatus,
    summary="异步生成游戏代码",
    description="异步方式生成代码，返回任务ID用于查询状态"
)
async def generate_code_async(
    request: CodeGenerateRequest,
    background_tasks: BackgroundTasks
) -> GenerationStatus:
    """
    异步生成代码
    
    Args:
        request: 代码生成请求
        background_tasks: FastAPI后台任务
        
    Returns:
        生成任务状态
    """
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        generation_tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now(),
            "request": request,
            "result": None,
            "error": None
        }
        
        # 添加后台任务
        background_tasks.add_task(
            _process_generation_task,
            task_id,
            request
        )
        
        return GenerationStatus(
            request_id=task_id,
            status="pending",
            progress=0,
            estimated_time=15,
            message="任务已创建，正在排队处理"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建生成任务失败: {str(e)}"
        )


@router.get(
    "/status/{task_id}",
    response_model=GenerationStatus,
    summary="查询生成任务状态",
    description="根据任务ID查询代码生成的进度和状态"
)
async def get_generation_status(task_id: str) -> GenerationStatus:
    """
    查询生成任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态信息
        
    Raises:
        HTTPException: 当任务不存在时抛出异常
    """
    if task_id not in generation_tasks:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
    
    task = generation_tasks[task_id]
    
    return GenerationStatus(
        request_id=task_id,
        status=task["status"],
        progress=task["progress"],
        estimated_time=task.get("estimated_time"),
        message=task.get("message", "")
    )


@router.get(
    "/result/{task_id}",
    response_model=CodeGenerateResponse,
    summary="获取生成结果",
    description="根据任务ID获取代码生成的最终结果"
)
async def get_generation_result(task_id: str) -> CodeGenerateResponse:
    """
    获取生成结果
    
    Args:
        task_id: 任务ID
        
    Returns:
        代码生成结果
        
    Raises:
        HTTPException: 当任务不存在或未完成时抛出异常
    """
    if task_id not in generation_tasks:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
    
    task = generation_tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"任务尚未完成，当前状态: {task['status']}"
        )
    
    if task["error"]:
        raise HTTPException(
            status_code=500,
            detail=task["error"]
        )
    
    return task["result"]


# 移除了引擎和语言列表API，因为这些信息现在包含在模板中


async def _process_generation_task(task_id: str, request: CodeGenerateRequest):
    """
    处理代码生成任务的后台函数
    
    Args:
        task_id: 任务ID
        request: 生成请求
    """
    try:
        # 更新任务状态为处理中
        generation_tasks[task_id].update({
            "status": "processing",
            "progress": 10,
            "message": "正在分析需求..."
        })
        
        # 调用生成服务
        result = await code_generator_service.generate_code(request)
        
        # 更新进度
        generation_tasks[task_id].update({
            "progress": 50,
            "message": "正在生成代码..."
        })
        
        # 模拟处理时间
        import asyncio
        await asyncio.sleep(2)
        
        # 完成任务
        generation_tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "代码生成完成",
            "result": result,
            "completed_at": datetime.now()
        })
        
    except Exception as e:
        # 任务失败
        generation_tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"生成失败: {str(e)}",
            "error": str(e),
            "failed_at": datetime.now()
        })
