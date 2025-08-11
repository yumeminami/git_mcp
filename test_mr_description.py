#!/usr/bin/env python3
"""
Test script to verify GitLab MR description fix with exact original parameters
"""

import asyncio
from git_mcp.services.platform_service import PlatformService


async def test_mr_creation():
    """Test MR creation with the exact parameters from the original issue"""

    # Exact parameters from the original call
    platform = "lejurobot"
    project_id = "chengxin/llm_demo"
    title = "实现 GLM-4-Voice 语音模型调研演示"
    source_branch = "feature/issue-2827-glm4-voice-research"
    target_branch = "master"

    # The description that should appear in GitLab
    description = """## 概述

实现 GLM-4-Voice 语音模型调研演示，支持延迟测量和意图理解验证。

## 主要功能

- 语音交互演示（按回车录音）
- 实时延迟统计分析
- --debug 参数支持日志记录
- 音频文件自动保存

## 文件说明

- `glm4_voice/glm4_voice_demo.py` - 主程序
- `glm4_voice/README.md` - 使用文档

Closes https://www.lejuhub.com/carlos/softdev_doc/-/issues/2827"""

    print("🧪 Testing GitLab MR description fix...")
    print("=" * 60)
    print(f"Platform: {platform}")
    print(f"Project: {project_id}")
    print(f"Title: {title}")
    print(f"Source Branch: {source_branch}")
    print(f"Target Branch: {target_branch}")
    print(f"Description length: {len(description)} characters")
    print("=" * 60)

    try:
        # Create MR using the platform service directly with description as kwarg
        result = await PlatformService.create_merge_request(
            platform_name=platform,
            project_id=project_id,
            title=title,
            source_branch=source_branch,
            target_branch=target_branch,
            description=description,
        )

        print("✅ SUCCESS: Merge request created!")
        print(f"MR ID: {result.get('id')}")
        print(f"URL: {result.get('url')}")
        print("=" * 60)
        print(
            "🔍 Please check the GitLab interface to verify the description appears correctly:"
        )
        print(f"👉 {result.get('url')}")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"❌ ERROR: Failed to create merge request: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_mr_creation())
