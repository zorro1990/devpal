"""
主应用测试模块
测试FastAPI应用的基础功能
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestMainApp:
    """主应用测试类"""
    
    @pytest.mark.unit
    def test_root_endpoint(self, client: TestClient):
        """测试根路径端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "欢迎使用 DevPal - 游戏代码副驾驶"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    @pytest.mark.unit
    def test_health_check(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "DevPal Backend"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
    
    @pytest.mark.unit
    def test_api_status(self, client: TestClient):
        """测试API状态端点"""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["api_version"] == "v1"
        assert data["status"] == "operational"
        assert "features" in data
        assert data["features"]["code_generator"] == "available"
        assert data["features"]["code_analyzer"] == "available"
    
    @pytest.mark.unit
    def test_not_found_endpoint(self, client: TestClient):
        """测试404错误处理"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "请求的资源未找到"


class TestMainAppAsync:
    """主应用异步测试类"""
    
    @pytest.mark.integration
    async def test_async_health_check(self, async_client: AsyncClient):
        """异步测试健康检查端点"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.integration
    async def test_async_api_status(self, async_client: AsyncClient):
        """异步测试API状态端点"""
        response = await async_client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["api_version"] == "v1"
        assert data["status"] == "operational"
