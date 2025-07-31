# PRMKit - Gmail到Google Groups多任务邮件迁移工具

这是一个功能强大的Gmail邮件迁移工具，支持多任务并行处理，可以同时将同一邮箱的不同标签迁移到不同的Google Groups，包含完整的Web管理界面。

## 功能特点

- 🔄 **多任务并行迁移** - 同时处理多个迁移任务
- 🏷️ **标签分类迁移** - 根据Gmail标签分别迁移到不同群组
- 📊 **实时监控面板** - Web界面实时查看所有任务状态
- ⚙️ **可视化任务管理** - 在线添加、编辑、删除迁移任务
- 📝 **详细运行日志** - 完整的迁移过程记录
- 🎯 **一键批量执行** - 手动触发所有启用的任务
- 📱 **响应式设计** - 完美支持桌面和移动设备
- 🔧 **灵活配置** - 每个任务独立配置源标签和目标群组

## 项目结构

```
PRMKit/
├── app.py                    # Flask Web应用主文件 (多任务API支持)
├── gmail_to_groups.py        # 多任务邮件迁移脚本
├── config.json              # 多任务配置文件
├── requirements.txt         # Python依赖包
├── install.bat              # Windows自动安装脚本
├── start_server.bat         # Windows启动脚本
├── templates/
│   └── index.html          # Web管理界面模板
├── static/
│   ├── css/
│   │   └── style.css       # 响应式样式文件
│   └── js/
│       └── main.js         # 任务管理JavaScript
└── README.md               # 项目说明文档
```

## 🎯 使用场景

**多任务迁移示例：**
- 任务1：将 `INBOX` 标签的邮件迁移到 `sales@company.com`
- 任务2：将 `SENT` 标签的邮件迁移到 `archive@company.com`
- 任务3：将 `Support` 标签的邮件迁移到 `support@company.com`
- 任务4：将所有邮件（无标签过滤）迁移到 `backup@company.com`

所有任务可以并行执行，大大提高迁移效率！

## 🛠️ 安装步骤

### 方法一：手动安装（使用 UV）

1. **安装 Python 和依赖**
   ```bash
   # 安装 Python（如果需要）
   uv python install 3.11
   
   # 创建虚拟环境并安装依赖
   uv sync
   ```

### 方法二：传统安装（使用 pip）

1. **环境准备**
   - 确保系统已安装Python 3.7+

2. **安装依赖**
   ```bash
   # 使用 pip 安装
   pip install -e .
   
   # 或者直接安装依赖
   pip install "flask>=3.0.0" google-api-python-client==2.100.0 google-auth==2.23.3 google-auth-oauthlib==1.0.0 google-auth-httplib2==0.1.1
   ```

### 3. Google Cloud配置

#### 3.1 创建Google Cloud项目
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用以下API：
   - Groups Migration API
   - Gmail API

#### 3.2 创建服务账户
1. 进入"IAM & Admin" > "Service Accounts"
2. 点击"Create Service Account"
3. 输入名称，点击"Create"
4. 点击创建的服务账户，进入"Keys"标签
5. 点击"Add Key" > "Create new key" > 选择JSON格式
6. 下载并保存为 `service-account-key.json`

#### 3.3 配置域范围授权
1. 在服务账户页面，启用"Domain-wide Delegation"
2. 记录下客户端ID
3. 登录 [Google Admin Console](https://admin.google.com/)
4. 进入"Security" > "API Controls" > "Manage Domain Wide Delegation"
5. 添加客户端ID和以下权限：
   ```
   https://www.googleapis.com/auth/gmail.readonly,
   https://www.googleapis.com/auth/apps.groups.migration
   ```

### 4. 配置应用

编辑 `config.json` 文件（支持多任务配置）：

```json
{
  "service_account_file": "service-account-key.json",
  "user_email": "user@yourdomain.com",
  "last_run": "Never",
  "migration_tasks": [
    {
      "id": "task1",
      "name": "收件箱迁移",
      "enabled": true,
      "source_label": "INBOX",
      "target_group": "sales@yourdomain.com",
      "description": "将收件箱邮件迁移到销售群组"
    },
    {
      "id": "task2",
      "name": "已发送迁移",
      "enabled": true,
      "source_label": "SENT",
      "target_group": "archive@yourdomain.com",
      "description": "将已发送邮件迁移到存档群组"
    }
  ]
}
```

**配置说明：**
- `service_account_file`: 服务账户JSON文件路径
- `user_email`: 源Gmail用户邮箱
- `migration_tasks`: 迁移任务数组
  - `id`: 任务唯一标识符
  - `name`: 任务显示名称
  - `enabled`: 是否启用该任务
  - `source_label`: Gmail标签（如INBOX、SENT或自定义标签）
  - `target_group`: 目标Google Groups邮箱
  - `description`: 任务描述

## 🚀 使用方法

### 启动Web管理面板

**方法一：使用批处理脚本（Windows）**
```cmd
start_server.bat
```

**方法二：使用 UV 手动启动**
```bash
uv run python app.py
```

**方法三：传统方式启动**
```bash
python app.py
```

访问 `http://localhost:5000` 打开Web管理界面

### Web界面功能

#### 📊 统计面板
- 实时显示迁移统计信息
- 成功/失败邮件数量
- 各任务执行状态
- 最后运行时间

#### 🎛️ 任务管理
- **添加任务**：点击"添加任务"按钮创建新的迁移任务
- **编辑任务**：修改任务配置（名称、标签、目标群组等）
- **启用/禁用**：快速切换任务状态
- **删除任务**：移除不需要的任务
- **批量执行**：一键运行所有启用的任务

#### 📝 日志监控
- 实时查看迁移日志
- 可调整显示行数
- 自动刷新功能

### 命令行运行

**使用 UV 运行所有启用的任务：**
```bash
uv run python gmail_to_groups.py
```

**传统方式运行：**
```bash
python gmail_to_groups.py
```

**任务执行流程：**
1. 加载配置文件中的所有任务
2. 过滤出启用状态的任务
3. 并行执行多个任务
4. 记录详细的执行日志
5. 更新统计信息

### 设置定时任务

#### Windows任务计划程序
1. 打开"任务计划程序"
2. 点击"创建基本任务"
3. 名称：Email Migration
4. 触发器：每天
5. 操作：启动程序
6. 程序：`python`
7. 参数：`C:\path\to\gmail_to_groups.py`

#### Linux/Mac cron
```bash
# 编辑crontab
crontab -e

# 添加这行（每天凌晨2点运行）
0 2 * * * /usr/bin/python3 /path/to/gmail_to_groups.py >> /var/log/email_migration.log 2>&1
```

## Web监控面板功能

### 📈 统计仪表板
- **总体统计**：成功迁移邮件数量、错误次数、总运行次数
- **任务级统计**：每个任务的独立统计信息
- **实时状态**：最后运行时间、当前执行状态
- **可视化展示**：直观的数据卡片和状态指示器

### 🎯 任务管理中心
- **任务列表**：卡片式展示所有配置的迁移任务
- **任务状态**：启用/禁用状态一目了然
- **快速操作**：编辑、启用/禁用、删除任务
- **任务详情**：显示源标签、目标群组、描述信息
- **添加任务**：通过模态框快速创建新任务

### ⚙️ 基础配置管理
- **服务账户配置**：在线修改服务账户文件路径
- **用户邮箱设置**：配置源Gmail用户邮箱
- **运行历史**：查看最后运行时间记录

### 控制中心
- **一键执行**：批量运行所有启用的迁移任务
- **实时刷新**：手动刷新统计信息和日志
- **状态监控**：实时显示执行状态和进度

### 📋 日志监控系统
- **实时日志**：动态显示迁移过程日志
- **日志过滤**：可调整显示行数（10-200行）
- **自动刷新**：每10秒自动更新日志内容
- **错误高亮**：重要信息和错误信息突出显示

## 故障排除

### 常见问题

1. **认证失败**
   - 检查服务账户JSON文件路径是否正确
   - 确认域范围授权已正确设置
   - 验证Gmail API和Groups Migration API是否已启用

2. **权限不足**
   - 确认服务账户有足够的权限访问Gmail和Google Groups
   - 检查Google Admin Console中的授权设置
   - 验证目标群组的访问权限

3. **多任务执行问题**
   - 并行任务可能触发API配额限制，可调整任务数量
   - 检查`config.json`中的任务配置格式是否正确
   - 确保每个任务的`source_label`和`target_group`字段填写正确

4. **API配额限制**
   - 检查Google Cloud Console中的Gmail API和Groups API使用情况
   - 多任务并行执行时可能触发限制，可在代码中调整延迟时间
   - 考虑申请更高的API配额

5. **邮件迁移失败**
   - 检查目标群组邮箱地址是否正确
   - 确认源用户邮箱有访问权限
   - 验证Gmail标签名称是否存在
   - 查看详细错误日志

6. **Web界面问题**
   - 如果任务列表不显示，检查`config.json`格式
   - 浏览器控制台可能显示JavaScript错误
   - 确保Flask服务正常运行在5000端口

### 日志文件

- `email_migration.log`: 详细的运行日志，包含所有任务执行信息和错误信息
- Web界面日志：实时显示当前执行状态和多任务进度

### 调试技巧

1. **启用详细日志**：在代码中设置更详细的日志级别
2. **单任务测试**：先禁用其他任务，单独测试问题任务
3. **检查网络连接**：确保能正常访问Google API服务
4. **验证配置**：使用Web界面检查任务配置是否正确

## 安全注意事项

- 妥善保管服务账户JSON密钥文件
- 不要将密钥文件提交到版本控制系统
- 定期检查和更新访问权限
- 监控迁移日志，及时发现异常

## 🛠️ 技术栈

### 后端技术
- **Python 3.8+**: 主要编程语言（推荐 3.11+）
- **UV**: 现代化 Python 包管理器和虚拟环境管理
- **Flask**: 轻量级Web框架，提供API服务
- **Google APIs**: Gmail API, Groups Migration API
- **ThreadPoolExecutor**: 多线程并行处理
- **JSON**: 配置文件和数据交换格式

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 响应式样式设计
- **JavaScript (ES6+)**: 交互逻辑和API调用
- **Fetch API**: 异步数据请求
- **Bootstrap风格**: 现代化UI组件

### 开发工具
- **UV**: 快速的 Python 包管理器，替代 pip 和 virtualenv
- **批处理脚本**: Windows自动化安装和启动（支持 UV）
- **pyproject.toml**: 现代化项目配置文件
- **日志系统**: 详细的运行和错误日志
- **配置管理**: 灵活的JSON配置系统

### API集成
- **Gmail API**: 邮件读取和标签管理
- **Groups Migration API**: 邮件迁移到Google Groups
- **RESTful API**: 前后端数据交互

## ✨ 项目亮点

### 🚀 高效并行处理
- 多任务同时执行，大幅提升迁移效率
- 智能任务调度，避免API限制冲突
- 实时进度监控，掌握执行状态

### 🎯 精准标签分类
- 支持Gmail所有标签类型（收件箱、已发送、自定义标签）
- 灵活的标签到群组映射配置
- 批量处理不同类型邮件

### 🖥️ 直观管理界面
- 现代化Web界面，操作简单直观
- 实时统计和日志监控
- 响应式设计，支持各种设备

### ⚙️ 现代化开发体验
- **UV 包管理**: 比 pip 快 10-100 倍的依赖安装
- **自动环境管理**: 无需手动创建虚拟环境
- **锁定文件**: 确保依赖版本一致性
- **JSON配置文件**: 易于维护的配置系统
- **在线配置管理**: 无需重启服务
- **任务级别配置**: 独立的任务配置

### 🛡️ 安全可靠
- Google官方API，安全稳定
- 详细日志记录，便于审计
- 错误处理机制，确保数据安全

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 支持

如果您在使用过程中遇到问题，请：
1. 查看本文档的故障排除部分
2. 检查项目的Issue页面
3. 提交新的Issue描述您的问题