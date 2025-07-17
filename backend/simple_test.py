#!/usr/bin/env python3
"""
简单测试：验证环境变量设置
"""

import os
import sys
sys.path.append('.')

# 设置环境变量
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DOUBAO_API_KEY"] = "test_api_key"

# 重新导入配置
from app.core.config import settings, validate_ai_config

print(f"Environment: {settings.environment}")
print(f"Debug: {settings.debug}")
print(f"API Key: {settings.doubao_api_key}")
print(f"Validate AI Config: {validate_ai_config()}")

# 测试代码生成
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

request_data = {
    "description": "创建一个简单的测试脚本",
    "engine": "unity",
    "language": "csharp"
}

response = client.post("/api/v1/generate/code", json=request_data)
print(f"Response status: {response.status_code}")
if response.status_code != 200:
    print(f"Error: {response.text}")
else:
    print("Success!")
