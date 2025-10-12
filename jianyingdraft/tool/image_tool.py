# -*- coding: utf-8 -*-
"""
Author: jian wei
File Name: image_tool.py
"""
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
from jianyingdraft.services.image_service import add_image_segment_service, add_image_animation_service
from jianyingdraft.utils.response import ToolResponse
from jianyingdraft.utils.index_manager import index_manager
from jianyingdraft.utils.time_format import parse_start_end_format

from jianyingdraft.utils.effect_manager import JianYingResourceManager

manager = JianYingResourceManager()


def image_tools(mcp: FastMCP):
    @mcp.tool()
    def add_image_segment(
            track_id: str,
            material: str,
            target_start_end: str,
            display_duration: str = "5s",
            image_settings: Optional[Dict[str, Any]] = None,
            clip_settings: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        添加图片片段到视频轨道

        Args:
            track_id: 轨道ID，通过create_track获得
            material: 图片文件路径或URL，支持PNG、JPG、JPEG、BMP、WebP等格式
            target_start_end: 片段在轨道上的目标时间范围，格式如 "1s-6s"，表示在轨道上从1s开始，到6s结束
            display_duration: 图片显示持续时间，默认5秒，格式如 "5s"
            image_settings: 图片显示设置（可选）
                默认 image_settings = {
                        "scale_x": 1.0,  # 水平缩放比例，默认为1.0
                        "scale_y": 1.0,  # 垂直缩放比例，默认为1.0
                        "transform_x": 0.0,  # 水平位移，单位为半个画布宽，默认为0.0
                        "transform_y": 0.0,  # 垂直位移，单位为半个画布高，默认为0.0
                        "rotation": 0.0,  # 顺时针旋转角度，可正可负，默认为0.0
                    }
            clip_settings: 图像调节设置字典（可选），哪些需要修改就填哪些字段
                默认 clip_settings = {
                        "alpha": 1.0,  # 图像不透明度, 0-1. 默认为1.0
                        "flip_horizontal": False,  # 是否水平翻转. 默认为False
                        "flip_vertical": False,  # 是否垂直翻转. 默认为False
                        "rotation": 0.0,  # 顺时针旋转的**角度**, 可正可负. 默认为0.0
                        "scale_x": 1.0,  # 水平缩放比例. 默认为1.0
                        "scale_y": 1.0,  # 垂直缩放比例. 默认为1.0
                        "transform_x": 0.0,  # 水平位移, 单位为半个画布宽. 默认为0.0
                        "transform_y": 0.0  # 垂直位移, 单位为半个画布高. 默认为0.0
                        }

        Returns:
            ToolResponse: 包含操作结果的响应，格式为 {"success": bool, "message": str, "data": dict, "image_segment_id": str}

        Examples:
            # 基本用法
            add_image_segment("track_id", "/path/to/image.png", "0s-5s")

            # 设置显示时长
            add_image_segment("track_id", "/path/to/image.png", "0s-8s", display_duration="8s")

            # 设置图片缩放和位置
            add_image_segment("track_id", "/path/to/image.png", "0s-5s",
                            image_settings={"scale_x": 0.8, "scale_y": 0.8, "transform_y": 0.2})

            # 设置透明度和旋转
            add_image_segment("track_id", "/path/to/image.png", "0s-5s",
                            clip_settings={"alpha": 0.7, "rotation": 45})
        """
        # 解析目标时间范围
        try:
            target_timerange = parse_start_end_format(target_start_end)
        except ValueError as e:
            return ToolResponse(
                success=False,
                message=f"target_start_end格式错误: {str(e)}"
            )

        # 解析显示时长
        try:
            duration_seconds = float(display_duration.replace('s', ''))
            if duration_seconds <= 0:
                return ToolResponse(
                    success=False,
                    message="显示时长必须大于0秒"
                )
        except (ValueError, AttributeError):
            return ToolResponse(
                success=False,
                message="display_duration格式错误，请使用格式如 '5s'"
            )

        # 通过track_id获取draft_id和track_name
        draft_id = index_manager.get_draft_id_by_track_id(track_id)
        track_name = index_manager.get_track_name_by_track_id(track_id)

        if not draft_id:
            return ToolResponse(
                success=False,
                message=f"未找到轨道ID对应的草稿: {track_id}"
            )

        if not track_name:
            return ToolResponse(
                success=False,
                message=f"未找到轨道ID对应的轨道名: {track_id}"
            )

        # 合并图片设置和剪辑设置
        final_clip_settings = clip_settings or {}
        if image_settings:
            final_clip_settings.update(image_settings)

        # 调用服务层处理业务逻辑
        result = add_image_segment_service(
            draft_id=draft_id,
            material=material,
            target_timerange=target_timerange,
            display_duration=display_duration,
            clip_settings=final_clip_settings,
            track_name=track_name
        )

        # 如果图片片段添加成功，添加索引记录
        if result.success and result.data and "image_segment_id" in result.data:
            image_segment_id = result.data["image_segment_id"]
            index_manager.add_image_segment_mapping(image_segment_id, track_id)

        return result

    @mcp.tool()
    def add_image_animation(
            image_segment_id: str,
            animation_type: str,
            animation_name: str,
            duration: Optional[str] = ''
    ) -> ToolResponse:
        """
        为图片片段添加动画效果

        Args:
            image_segment_id: 图片片段ID，通过add_image_segment获得
            animation_type: 动画类型，支持 "IntroType", "OutroType", "GroupAnimationType"
            animation_name: 动画名称，如 "淡入", "缩放" 等，可以使用find_effects_by_type工具，资源类型选择IntroType、OutroType、GroupAnimationType，从而获取动画类型有哪些
            duration: 动画持续时间，格式如 "1s"（可选）
        """
        # 动画类型验证
        valid_animation_types = ["IntroType", "OutroType", "GroupAnimationType"]
        if animation_type not in valid_animation_types:
            return ToolResponse(
                success=False,
                message=f"无效的动画类型 '{animation_type}'，支持的类型: {', '.join(valid_animation_types)}"
            )

        # 动画存在性验证
        effects = manager.find_by_type(
            effect_type=animation_type,
            keyword=animation_name,
            limit=1
        )

        # 检查是否找到完全匹配的动画
        exact_match = False
        if effects:
            for effect in effects:
                if effect.get('title') == animation_name:
                    exact_match = True
                    break

        if not effects or not exact_match:
            # 获取建议动画
            animation_suggestions = manager.find_by_type(animation_type, keyword=animation_name)

            all_suggestions = []
            for effect in animation_suggestions:
                if effect.get('title'):
                    all_suggestions.append(effect.get('title'))

            return ToolResponse(
                success=False,
                message=f"在 {animation_type} 中未找到动画 '{animation_name}'",
                data={
                    "error_type": "animation_not_found",
                    "animation_type": animation_type,
                    "animation_name": animation_name,
                    "suggestions": all_suggestions
                }
            )

        # 通过image_segment_id获取相关信息
        draft_id = index_manager.get_draft_id_by_image_segment_id(image_segment_id)
        track_info = index_manager.get_track_info_by_image_segment_id(image_segment_id)
        print(duration, type(duration))
        if not draft_id:
            return ToolResponse(
                success=False,
                message=f"未找到图片片段ID对应的草稿: {image_segment_id}"
            )

        if not track_info:
            return ToolResponse(
                success=False,
                message=f"未找到图片片段ID对应的轨道信息: {image_segment_id}"
            )

        # 调用服务层处理业务逻辑
        result = add_image_animation_service(
            draft_id=draft_id,
            image_segment_id=image_segment_id,
            animation_type=animation_type,
            animation_name=animation_name,
            duration=duration,
            track_name=track_info.get('track_name')
        )

        return result