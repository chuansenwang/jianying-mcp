# -*- coding: utf-8 -*-
"""
Author: jian wei
File Name: image_service.py
"""
from typing import Optional, Dict, Any, List
from jianyingdraft.jianying.video import VideoSegment
from jianyingdraft.utils.response import ToolResponse
from jianyingdraft.validators.material_validator import MaterialValidator
from jianyingdraft.utils.index_manager import index_manager


def add_image_segment_service(
    draft_id: str,
    material: str,
    target_timerange: str,
    display_duration: str = "5s",
    clip_settings: Optional[Dict[str, Any]] = None,
    track_name: Optional[str] = None
) -> ToolResponse:
    """
    图片片段创建服务 - 封装复杂的图片片段创建逻辑
    
    Args:
        draft_id: 草稿ID
        material: 图片文件路径或URL，支持PNG、JPG等格式
        target_timerange: 片段在轨道上的目标时间范围，格式如 "0s-5s"
        display_duration: 图片显示持续时间，默认5秒
        clip_settings: 图像调节设置字典（可选）
        track_name: 指定的轨道名称（可选）
    
    Returns:
        ToolResponse: 包含操作结果的响应对象
    """
    try:
        # 创建VideoSegment实例（复用现有的视频片段处理逻辑）
        video_segment = VideoSegment(draft_id, track_name=track_name)
        
        # 调用视频片段创建方法（图片也会被视为视频素材处理）
        # 让add_video_segment内部处理素材验证和本地化
        result_data = video_segment.add_video_segment(
            material=material,
            target_timerange=target_timerange,
            source_timerange=None,  # 图片不需要源时间范围
            speed=None,  # 图片不需要速度设置
            volume=1.0,  # 图片没有音量，但保持默认值
            change_pitch=False,  # 图片不需要音调设置
            clip_settings=clip_settings,
            track_name=track_name,
            material_type="image"  # 指定素材类型为图片
        )
        
        # 获取轨道ID用于索引映射
        track_id = video_segment.track_id if hasattr(video_segment, 'track_id') else None
        
        # 构建返回数据，包含image_segment_id
        response_data = {
            "image_segment_id": video_segment.video_segment_id,
            "draft_id": draft_id,
            "add_image_segment": result_data
        }
        
        # 如果有轨道名称，添加到返回数据中
        if track_name:
            response_data["track_name"] = track_name
        
        # 记录图片片段映射到索引管理器
        if track_id and video_segment.video_segment_id:
            # 图片片段用到的视频片段ID，同步记录到两类映射，确保后续视频类接口（如关键帧）可通过视频片段ID正常检索
            index_manager.add_image_segment_mapping(video_segment.video_segment_id, track_id, draft_id)
            index_manager.add_video_segment_mapping(video_segment.video_segment_id, track_id)
        
        return ToolResponse(
            success=True,
            message="图片片段创建成功",
            data=response_data
        )
        
    except ValueError as e:
        # 处理参数错误（时间范围格式、轨道类型等）
        return ToolResponse(
            success=False,
            message=f"参数错误: {str(e)}"
        )
        
    except NameError as e:
        # 处理轨道不存在错误
        return ToolResponse(
            success=False,
            message=f"轨道错误: {str(e)}"
        )
        
    except TypeError as e:
        # 处理轨道类型错误
        return ToolResponse(
            success=False,
            message=f"轨道类型错误: {str(e)}"
        )
        
    except FileNotFoundError as e:
        # 处理文件不存在错误
        return ToolResponse(
            success=False,
            message=f"文件错误: {str(e)}"
        )
        
    except Exception as e:
        # 处理其他未预期的错误
        return ToolResponse(
            success=False,
            message=f"图片片段创建失败: {str(e)}"
        )


def add_image_animation_service(
    draft_id: str,
    image_segment_id: str,
    animation_type: str,
    animation_name: str,
    duration: Optional[str] = None,
    track_name: Optional[str] = None
) -> ToolResponse:
    """
    图片动画添加服务 - 为图片片段添加动画效果

    Args:
        draft_id: 草稿ID
        image_segment_id: 图片片段ID
        animation_type: 动画类型，支持 "IntroType", "OutroType", "GroupAnimationType"
        animation_name: 动画名称，如 "淡入", "缩放" 等
        duration: 动画持续时间，格式如 "1s"（可选）
        track_name: 轨道名称（可选）

    Returns:
        ToolResponse: 包含操作结果的响应对象
    """
    try:
        # 创建VideoSegment实例，传入image_segment_id（复用视频片段逻辑）
        video_segment = VideoSegment(draft_id, video_segment_id=image_segment_id, track_name=track_name)

        # 调用视频动画添加方法（图片片段也支持动画）
        result_data = video_segment.add_animation(
            animation_type=animation_type,
            animation_name=animation_name,
            duration=duration
        )

        # 构建返回数据
        response_data = {
            "image_segment_id": image_segment_id,
            "draft_id": draft_id,
            "animation_type": animation_type,
            "animation_name": animation_name,
            "duration": duration,
            "add_animation": result_data
        }

        # 如果有轨道名称，添加到返回数据中
        if track_name:
            response_data["track_name"] = track_name

        return ToolResponse(
            success=True,
            message=f"图片动画添加成功: {animation_type}.{animation_name}",
            data=response_data
        )

    except ValueError as e:
        # 处理参数错误
        return ToolResponse(
            success=False,
            message=f"参数错误: {str(e)}"
        )

    except NameError as e:
        # 处理轨道不存在错误
        return ToolResponse(
            success=False,
            message=f"轨道错误: {str(e)}"
        )

    except Exception as e:
        # 处理其他未预期的错误
        return ToolResponse(
            success=False,
            message=f"图片动画添加失败: {str(e)}"
        )