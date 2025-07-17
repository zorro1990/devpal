# DevPal - 游戏代码副驾驶

🎮 AI驱动的游戏开发助手，提供智能代码生成、分析和优化功能，让你的游戏开发更高效。

## ✨ 功能特性

### 🚀 代码生成器
- **智能代码生成**: 基于自然语言描述生成高质量游戏代码
- **多引擎支持**: Unity、Unreal Engine、Godot、Cocos2d等
- **多语言支持**: C#、C++、JavaScript、Python、GDScript等
- **代码高亮**: 专业级语法高亮和一键复制功能
- **详细注释**: 可选择生成包含详细注释的代码

### 🔍 代码分析器 (开发中)
- **智能分析**: 深度分析代码结构和逻辑
- **优化建议**: 提供性能和代码质量改进建议
- **文档生成**: 自动生成代码文档和说明

## 🏗️ 技术架构

### 后端 (FastAPI)
- **框架**: FastAPI + Python 3.9+
- **AI集成**: 支持豆包、Kimi、DeepSeek、通义千问、智谱AI等国内主流模型
- **API设计**: RESTful API，完整的OpenAPI文档
- **测试覆盖**: 单元测试和集成测试全覆盖

### 前端 (Next.js)
- **框架**: Next.js 15 + TypeScript + Tailwind CSS
- **架构**: App Router + 服务端组件
- **UI组件**: 响应式设计，支持桌面端和移动端
- **代码展示**: react-syntax-highlighter + 多语言语法高亮

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- Docker (可选)

### 1. 克隆项目
```bash
git clone <repository-url>
cd 游戏代码助手
```

### 2. 启动后端服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (可选，用于AI功能)
export DOUBAO_API_KEY="your_api_key"
export DEFAULT_AI_PROVIDER="doubao"

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端应用: http://localhost:3001
- 后端API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 🐳 Docker 部署

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d
```

## 📖 使用指南

### 代码生成器使用流程

1. **访问生成器页面**: 点击首页的"开始生成"或导航到 `/generator`
2. **输入需求描述**: 详细描述你想要生成的代码功能
3. **选择引擎和语言**: 选择目标游戏引擎和编程语言
4. **配置选项**: 选择是否包含详细注释等选项
5. **生成代码**: 点击"生成代码"按钮，AI将为你生成代码
6. **复制使用**: 使用一键复制功能将代码复制到你的项目中

### API 使用示例

```bash
# 生成代码
curl -X POST http://localhost:8000/api/v1/generate/code \
  -H "Content-Type: application/json" \
  -d '{
    "description": "创建一个Unity C#脚本，让物体朝向鼠标位置",
    "engine": "unity",
    "language": "csharp",
    "include_comments": true
  }'
```

## 🧪 测试

### 后端测试
```bash
cd backend
python -m pytest tests/ -v
```

### 前端测试
```bash
cd frontend
npm test
```

## 📁 项目结构

```
游戏代码助手/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── main.py         # FastAPI应用入口
│   │   ├── core/           # 核心配置
│   │   ├── api/v1/         # API路由和数据模型
│   │   └── services/       # 业务逻辑服务
│   ├── tests/              # 测试文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── app/           # Next.js页面
│   │   ├── components/    # React组件
│   │   └── lib/          # 工具函数
│   ├── __tests__/        # 测试文件
│   └── package.json      # Node.js依赖
├── docker-compose.yml    # Docker编排
├── prd.md               # 产品需求文档
└── README.md           # 项目说明
```

## 🔧 配置说明

### 环境变量

#### 后端环境变量
```bash
# 基础配置
ENVIRONMENT=development
DEBUG=true

# AI提供商配置 (可选)
DEFAULT_AI_PROVIDER=doubao
DOUBAO_API_KEY=your_doubao_api_key
KIMI_API_KEY=your_kimi_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

#### 前端环境变量
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🎯 路线图

- [x] 代码生成器基础功能
- [x] 多AI模型支持
- [x] 前端界面和用户体验
- [ ] 代码分析器功能
- [ ] 用户认证和个人化
- [ ] 代码模板库
- [ ] 插件系统

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 加入讨论群

---

**DevPal** - 让AI成为你的游戏开发伙伴！ 🚀
