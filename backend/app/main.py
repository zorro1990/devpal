"""
游戏代码副驾驶 (DevPal) - 主应用入口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.api.v1.endpoints import generator, analyzer
# from app.api.v1.endpoints import config  # 临时禁用

# 创建FastAPI应用实例
app = FastAPI(
    title="DevPal - 游戏代码副驾驶",
    description="AI驱动的游戏开发助手，提供代码生成、分析和优化功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3004", "http://127.0.0.1:3004", "http://localhost:3005", "http://127.0.0.1:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载API路由
app.include_router(generator.router, prefix="/api/v1")
app.include_router(analyzer.router, prefix="/api/v1")
# app.include_router(config.router, prefix="/api/v1/config", tags=["config"])  # 临时禁用


@app.get("/")
async def root():
    """根路径欢迎信息"""
    return {
        "message": "欢迎使用 DevPal - 游戏代码副驾驶",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "DevPal Backend",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/api/v1/status")
async def api_status():
    """API状态检查"""
    return {
        "api_version": "v1",
        "status": "operational",
        "features": {
            "code_generator": "available",
            "code_analyzer": "available"
        },
        "timestamp": datetime.now().isoformat()
    }


# 异常处理器
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "请求的资源未找到"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
