#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试图片功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jianyingdraft'))

from jianyingdraft.services.image_service import add_image_segment_service, add_image_animation_service
from jianyingdraft.utils.index_manager import IndexManager
from jianyingdraft.jianying.track import Track
from jianyingdraft.jianying.draft import Draft
import uuid

def test_full_image_workflow():
    """测试完整的图片工作流"""
    print("=== 开始完整图片功能测试 ===")
    
    # 创建测试draft_id
    draft_id = str(uuid.uuid4())
    print(f"测试draft_id: {draft_id}")
    
    # 创建草稿
    draft = Draft()
    draft_data = draft.create_draft("测试图片功能")
    print("✅ 草稿创建成功")
    
    # 创建video轨道
    track_manager = Track(draft_id)
    track_id = track_manager.add_track("video", "video_track_1")
    print(f"✅ 创建轨道成功: {track_id}")
    
    # 添加轨道映射
    index_manager = IndexManager()
    index_manager.add_track_mapping(track_id, draft_id, "video_track_1", "video")
    print("✅ 添加轨道映射成功")
    
    # 测试图片文件路径
    image_path = "test_image.png"
    
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        print(f"❌ 错误: 图片文件 {image_path} 不存在")
        return False
    
    print(f"✅ 图片文件存在: {image_path}")
    
    # 步骤1: 添加图片片段
    print("\n--- 步骤1: 添加图片片段 ---")
    result1 = add_image_segment_service(
        draft_id=draft_id,
        material=image_path,
        target_timerange="0s-3s",
        track_name="video_track_1"
    )
    
    if not result1.success:
        print(f"❌ 图片添加失败: {result1.message}")
        return False
    
    print("✅ 图片添加成功!")
    image_segment_id = result1.data["image_segment_id"]
    print(f"图片片段ID: {image_segment_id}")
    
    # 添加图片片段映射
    index_manager.add_image_segment_mapping(image_segment_id, track_id)
    print("✅ 添加图片片段映射成功")
    
    # 步骤2: 添加图片动画
    print("\n--- 步骤2: 添加图片动画 ---")
    result2 = add_image_animation_service(
        draft_id=draft_id,
        image_segment_id=image_segment_id,
        animation_type="IntroType",
        animation_name="淡入",
        duration="1s",
        track_name="video_track_1"
    )
    
    if not result2.success:
        print(f"❌ 动画添加失败: {result2.message}")
        return False
    
    print("✅ 图片动画添加成功!")
    print(f"动画信息: {result2.data}")
    
    print("\n=== 完整图片功能测试完成 ===")
    return True

if __name__ == "__main__":
    success = test_full_image_workflow()
    if success:
        print("🎉 所有测试通过!")
    else:
        print("💥 测试失败!")
        sys.exit(1)