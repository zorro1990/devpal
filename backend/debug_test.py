#!/usr/bin/env python3
"""
调试脚本：测试代码生成API
"""

import sys
import traceback
import os
sys.path.append('.')

# 设置测试环境变量
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DOUBAO_API_KEY"] = "test_api_key"
os.environ["DEFAULT_AI_PROVIDER"] = "doubao"

from fastapi.testclient import TestClient
from app.main import app

def test_generate_code():
    """测试代码生成功能"""
    client = TestClient(app)
    
    request_data = {
        "description": "创建一个Unity C#脚本，让物体朝向鼠标位置",
        "engine": "unity",
        "language": "csharp",
        "include_comments": True,
        "code_style": "standard"
    }
    
    try:
        print("发送请求...")
        response = client.post("/api/v1/generate/code", json=request_data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code != 200:
            print("请求失败!")
            return False
        
        data = response.json()
        print(f"成功响应: {data}")
        return True
        
    except Exception as e:
        print(f"异常: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始调试测试...")
    success = test_generate_code()
    print(f"测试结果: {'成功' if success else '失败'}")
