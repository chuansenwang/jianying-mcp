#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片服务功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jianyingdraft'))

from jianyingdraft.services.image_service import add_image_segment_service
from jianyingdraft.utils.index_manager import IndexManager
from jianyingdraft.jianying.track import Track
from jianyingdraft.jianying.video import VideoSegment
import uuid

def test_image_service():
    # 创建测试draft_id
    draft_id = str(uuid.uuid4())
    print(f"测试draft_id: {draft_id}")
    
    # 首先添加一个video轨道
    track_manager = Track(draft_id)
    track_id = track_manager.add_track("video", "video_track_1")
    print(f"创建轨道成功: {track_id}")
    
    # 添加轨道映射
    index_manager = IndexManager()
    index_manager.add_track_mapping(track_id, draft_id, "video_track_1", "video")
    print("添加轨道映射成功")
    
    # 测试图片文件路径
    image_path = "test_image.png"
    
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件 {image_path} 不存在")
        return False
    
    print(f"图片文件存在: {image_path}")
    
    # 调用图片服务
    result = add_image_segment_service(
        draft_id=draft_id,
        material=image_path,
        target_timerange="0s-3s",
        track_name="video_track_1"
    )
    
    print(f"服务调用结果: {result}")
    
    if result.success:
        print("✅ 图片添加成功!")
        print(f"返回数据: {result.data}")
        return True
    else:
        print("❌ 图片添加失败!")
        print(f"错误信息: {result.message}")
        return False

if __name__ == "__main__":
    test_image_service()