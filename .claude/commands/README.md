# Git MCP Issue-to-Code Workflow

这些斜杠命令提供了完整的 issue 驱动开发工作流，结合我们的 Git MCP 服务器实现自动化开发流程。

**命令类型：** 用户级命令（在所有项目中可用）
**安装位置：** `~/.claude/commands/`

## 🚀 完整工作流

```bash
# 1. 分析工单
/issue https://gitlab.com/group/project/-/issues/123

# 2. 生成开发计划
/plan

# 3. 实现功能
/implement

# 4. 编写测试
/test

# 5. 更新文档
/doc

# 6. 创建PR/MR
/pr 123
```

## 📋 命令详解

### `/issue` - Issue 分析
- 无参数：显示分配给我的工单列表
- 有参数：从 GitLab/GitHub URL 获取具体 issue 详情
- 分析技术需求和上下文
- 提供实现建议

**用法:**
```bash
# 查看我的工单列表
/issue

# 分析具体工单
/issue https://gitlab.com/group/project/-/issues/123
# 或
/issue my-gitlab project-id 123
```

### `/plan` - 开发计划
- 基于 issue 分析生成开发计划
- 分析当前代码库结构
- 提供分支策略和实现步骤

### `/implement` - 功能实现
- 按计划实现功能
- 创建特性分支
- 编写高质量代码
- 遵循项目规范

### `/test` - 测试生成
- 为实现的功能生成测试
- 包含单元测试、集成测试
- 处理边界情况和错误处理
- 确保测试覆盖率

### `/doc` - 文档更新
- 更新 API 文档
- 添加使用示例
- 更新 README 和配置指南
- 保持文档一致性

### `/pr` - 创建 PR/MR
- 提交代码并推送分支
- 创建 Pull Request 或 Merge Request
- 自动关联和关闭 issue
- 请求代码审查

## 🛠️ 集成功能

### MCP 工具集成
这些命令利用我们的 Git MCP 服务器工具：
- `get_issue_by_url()` - URL 解析获取 issue
- `get_issue_details()` - 获取详细信息
- `create_merge_request()` - 创建 MR
- `get_platform_config()` - 获取配置信息

### 自动化特性
- **智能分析**: 基于 issue 内容和代码库上下文
- **代码生成**: 遵循项目模式和最佳实践
- **测试覆盖**: 自动生成全面测试用例
- **文档同步**: 保持文档与代码同步
- **工单关联**: 自动关联 PR 和 issue

## 🎯 适用场景

### 团队协作
- Issue 驱动开发流程
- 标准化开发工作流
- 自动化重复性任务
- 提高代码质量

### 个人开发
- 快速原型实现
- 功能迭代开发
- 文档和测试自动化
- 项目维护简化

## ⚡ 使用提示

1. **按顺序使用**: 建议按照 issue → plan → implement → test → doc → pr 的顺序
2. **灵活调整**: 可以跳过某些步骤或重复执行
3. **上下文保持**: 每个命令都会考虑之前步骤的结果
4. **项目适应**: 命令会自动适应不同的项目结构和技术栈

开始你的 issue-to-code 自动化开发之旅吧！🚀
