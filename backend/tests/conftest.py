"""
pytest 配置文件
定义测试夹具和共享配置
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """同步测试客户端"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client():
    """异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_ai_response():
    """模拟AI响应的夹具"""
    return {
        "code": "// Generated code example\nconsole.log('Hello, World!');",
        "explanation": "这是一个简单的JavaScript代码示例",
        "language": "javascript",
        "framework": "vanilla"
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """自动设置测试环境变量"""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DOUBAO_API_KEY", "test_api_key")
    monkeypatch.setenv("DEFAULT_AI_PROVIDER", "doubao")

    # 重新创建settings对象以读取新的环境变量
    from app.core.config import Settings
    import app.core.config as config_module
    config_module.settings = Settings()
