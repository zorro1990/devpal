"""
代码生成器测试模块
测试代码生成相关的API端点
"""

import pytest
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.api.v1.schemas.generator import (
    CodeGenerateRequest,
    GameEngine,
    ProgrammingLanguage
)


class TestGeneratorAPI:
    """代码生成器API测试类"""
    
    @pytest.mark.integration
    def test_generate_code_success(self, client: TestClient):
        """测试代码生成成功场景"""
        request_data = {
            "description": "创建一个Unity C#脚本，让物体朝向鼠标位置",
            "engine": "unity",
            "language": "csharp",
            "include_comments": True,
            "code_style": "standard"
        }
        
        response = client.post("/api/v1/generate/code", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "generated_code" in data
        assert "explanation" in data
        assert data["engine"] == "unity"
        assert data["language"] == "csharp"
        assert len(data["generated_code"]) > 0
    
    @pytest.mark.integration
    def test_generate_code_empty_description(self, client: TestClient):
        """测试空描述的错误处理"""
        request_data = {
            "description": "",
            "engine": "unity",
            "language": "csharp"
        }
        
        response = client.post("/api/v1/generate/code", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    def test_generate_code_invalid_engine(self, client: TestClient):
        """测试无效引擎的错误处理"""
        request_data = {
            "description": "创建一个简单的游戏脚本",
            "engine": "invalid_engine",
            "language": "csharp"
        }
        
        response = client.post("/api/v1/generate/code", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    def test_get_supported_engines(self, client: TestClient):
        """测试获取支持的游戏引擎"""
        response = client.get("/api/v1/generate/engines")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "unity" in data
        assert "unreal" in data
        assert "godot" in data
        assert isinstance(data, dict)
    
    @pytest.mark.integration
    def test_get_supported_languages(self, client: TestClient):
        """测试获取支持的编程语言"""
        response = client.get("/api/v1/generate/languages")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "csharp" in data
        assert "cpp" in data
        assert "python" in data
        assert isinstance(data, dict)
    
    @pytest.mark.integration
    def test_generate_code_async(self, client: TestClient):
        """测试异步代码生成"""
        request_data = {
            "description": "创建一个简单的移动脚本",
            "engine": "unity",
            "language": "csharp"
        }
        
        response = client.post("/api/v1/generate/code/async", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "request_id" in data
        assert data["status"] == "pending"
        assert data["progress"] == 0
        
        # 测试状态查询
        task_id = data["request_id"]
        status_response = client.get(f"/api/v1/generate/status/{task_id}")
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["request_id"] == task_id
    
    @pytest.mark.integration
    def test_get_nonexistent_task_status(self, client: TestClient):
        """测试查询不存在任务的状态"""
        fake_task_id = "nonexistent-task-id"
        
        response = client.get(f"/api/v1/generate/status/{fake_task_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "任务不存在" in data["detail"]


class TestGeneratorAPIAsync:
    """代码生成器异步API测试类"""
    
    @pytest.mark.integration
    async def test_async_generate_code(self, async_client: AsyncClient):
        """异步测试代码生成"""
        request_data = {
            "description": "创建一个Unity C#脚本，实现简单的跳跃功能",
            "engine": "unity",
            "language": "csharp",
            "include_comments": True
        }
        
        response = await async_client.post("/api/v1/generate/code", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "MonoBehaviour" in data["generated_code"]
        assert data["engine"] == "unity"
        assert data["language"] == "csharp"
    
    @pytest.mark.integration
    async def test_async_different_engines(self, async_client: AsyncClient):
        """测试不同游戏引擎的代码生成"""
        engines_to_test = [
            ("unity", "csharp"),
            ("pygame", "python"),
            ("godot", "gdscript")
        ]
        
        for engine, language in engines_to_test:
            request_data = {
                "description": f"创建一个{engine}的简单脚本",
                "engine": engine,
                "language": language
            }
            
            response = await async_client.post("/api/v1/generate/code", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["engine"] == engine
            assert data["language"] == language


class TestGeneratorService:
    """代码生成器服务测试类"""
    
    @pytest.mark.unit
    def test_code_generate_request_validation(self):
        """测试代码生成请求的数据验证"""
        # 有效请求
        valid_request = CodeGenerateRequest(
            description="创建一个简单的游戏脚本",
            engine=GameEngine.UNITY,
            language=ProgrammingLanguage.CSHARP
        )
        
        assert valid_request.description == "创建一个简单的游戏脚本"
        assert valid_request.engine == GameEngine.UNITY
        assert valid_request.language == ProgrammingLanguage.CSHARP
        assert valid_request.include_comments is True  # 默认值
    
    @pytest.mark.unit
    def test_invalid_description_length(self):
        """测试描述长度验证"""
        with pytest.raises(ValueError):
            CodeGenerateRequest(
                description="短",  # 太短
                engine=GameEngine.UNITY,
                language=ProgrammingLanguage.CSHARP
            )
    
    @pytest.mark.unit
    @patch('app.services.code_generator.code_generator_service._call_ai_service')
    async def test_mock_ai_service(self, mock_ai_call):
        """测试模拟AI服务调用"""
        from app.services.code_generator import code_generator_service
        
        # 模拟AI响应
        mock_response = json.dumps({
            "code": "public class TestScript : MonoBehaviour { }",
            "explanation": "测试脚本",
            "dependencies": ["UnityEngine"],
            "usage_example": "// 添加到游戏对象",
            "suggestions": ["测试建议"],
            "complexity": "simple"
        }, ensure_ascii=False)
        
        mock_ai_call.return_value = mock_response
        
        request = CodeGenerateRequest(
            description="创建一个测试脚本",
            engine=GameEngine.UNITY,
            language=ProgrammingLanguage.CSHARP
        )
        
        result = await code_generator_service.generate_code(request)
        
        assert result.success is True
        assert "TestScript" in result.generated_code
        assert result.engine == GameEngine.UNITY
        assert result.language == ProgrammingLanguage.CSHARP
        
        # 验证AI服务被调用
        mock_ai_call.assert_called_once()


class TestGeneratorIntegration:
    """代码生成器集成测试类"""
    
    @pytest.mark.integration
    def test_full_generation_workflow(self, client: TestClient):
        """测试完整的代码生成工作流"""
        # 1. 获取支持的引擎和语言
        engines_response = client.get("/api/v1/generate/engines")
        languages_response = client.get("/api/v1/generate/languages")
        
        assert engines_response.status_code == 200
        assert languages_response.status_code == 200
        
        engines = engines_response.json()
        languages = languages_response.json()
        
        # 2. 选择一个引擎和语言进行生成
        selected_engine = "unity"
        selected_language = "csharp"
        
        assert selected_engine in engines
        assert selected_language in languages
        
        # 3. 生成代码
        request_data = {
            "description": "创建一个角色控制器脚本，支持WASD移动",
            "engine": selected_engine,
            "language": selected_language,
            "include_comments": True,
            "additional_requirements": "需要包含碰撞检测"
        }
        
        response = client.post("/api/v1/generate/code", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 4. 验证生成结果
        assert data["success"] is True
        assert len(data["generated_code"]) > 50  # 确保生成了足够的代码
        assert data["engine"] == selected_engine
        assert data["language"] == selected_language
        assert isinstance(data["suggestions"], list)
        assert isinstance(data["dependencies"], list)
