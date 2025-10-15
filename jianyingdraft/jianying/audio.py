# -*- coding: utf-8 -*-
"""
Author: jian wei
File Name: audio.py
"""
import json
import os
import uuid
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取环境变量
SAVE_PATH = os.getenv('SAVE_PATH')
from jianyingdraft.jianying.track import Track
from jianyingdraft.validators.overlap_validator import validate_overlap
from jianyingdraft.validators.material_validator import download_and_validate_material


class AudioSegment:
    """
    音频片段管理类
    负责音频片段的创建和数据存储
    """

    def __init__(self, draft_id: str, audio_segment_id: str = None, track_name: str = None):
        """
        初始化音频片段

        Args:
            draft_id: 草稿ID
            audio_segment_id: 音频片段ID，在添加特效等可用，创建音频时不用
            track_name: 指定的轨道名称（可选）
        """
        self.draft_id = draft_id
        self.audio_segment_id = audio_segment_id
        self.track_name = track_name

    def add_audio_segment(self, material: str, target_timerange: str,
                          source_timerange: Optional[str] = None, speed: Optional[float] = None,
                          volume: float = 1.0, change_pitch: bool = False,
                          track_name: Optional[str] = None, 
                          auto_next: bool = False) -> Dict[str, Any]:
        """
        创建音频片段配置

        Args:
            material: 音频文件路径,包括本地路径或者url
            target_timerange: 片段在轨道上的目标时间范围，格式如 "0s-4.2s",表示在轨道上从0s开始
            source_timerange: 从源视频文件中截取的时间范围，格式如 "1s-4.2s",表示从源视频的1s开始截取，持续4.2s，默认从开头根据`speed`截取与`target_timerange`等长的一部分
            speed: (`float`, optional): 播放速度, 默认为1.0，此项与`source_timerange`同时指定时, 将覆盖`target_timerange`中的时长
            volume: 音量，默认1.0
            change_pitch: 是否跟随变速改变音调，默认False，一般不修改
            track_name: 指定的轨道名称（可选），如果不指定则使用实例的track_name
            auto_next: 是否自动在轨道上一个片段之后添加，默认False
        """
        # 确定使用的轨道名称（参数优先，然后是实例属性）
        final_track_name = track_name or self.track_name
        
        # 如果启用了自动下一个时间位置，则计算新的target_timerange
        if auto_next and final_track_name:
            target_timerange = self._calculate_next_time_position(final_track_name, target_timerange)

        # 生成音频片段ID
        audio_segment_id = str(uuid.uuid4())

        # 解析target_timerange
        if not target_timerange or "-" not in target_timerange:
            raise ValueError(f"Invalid target_timerange format: {target_timerange}")

        start_str, duration_str = target_timerange.split("-", 1)
        target_timerange_data = {
            "start": start_str.strip(),
            "duration": duration_str.strip()
        }

        # 解析source_timerange（如果有）
        source_timerange_data = None
        if source_timerange is not None:
            # 解析source_timerange
            if "-" not in source_timerange:
                raise ValueError(f"Invalid source_timerange format: {source_timerange}")
            src_start_str, src_duration_str = source_timerange.split("-", 1)
            source_timerange_data = {
                "start": src_start_str.strip(),
                "duration": src_duration_str.strip()
            }

        # 下载并验证素材，获取本地化路径
        local_material_path = download_and_validate_material(
            self.draft_id,
            material,
            "audio",
            target_timerange_data
        )

        # 构建add_audio_segment参数（使用本地化后的路径）
        add_audio_segment_params = {
            "material": local_material_path,  # 使用本地化后的相对路径
            "target_timerange": target_timerange_data
        }

        # 只添加用户明确传入的可选参数
        if source_timerange_data is not None:
            add_audio_segment_params["source_timerange"] = source_timerange_data

        if speed is not None:
            add_audio_segment_params["speed"] = speed
        if volume != 1.0:  # 只有非默认值才保存
            add_audio_segment_params["volume"] = volume
        if change_pitch:  # 只有True才保存
            add_audio_segment_params["change_pitch"] = change_pitch

        # 验证轨道
        if final_track_name:
            self._validate_track_for_audio(final_track_name)

        # 验证片段重叠
        if final_track_name:
            validate_overlap(self.draft_id, "audio", final_track_name, target_timerange_data)

        # 构建完整的片段数据
        segment_data = {
            "audio_segment_id": audio_segment_id,
            "operation": "add_audio_segment",
            "add_audio_segment": add_audio_segment_params,
        }
        return_data = {
            "draft_id": self.draft_id,
            "track_name": final_track_name,
            "audio_segment_id": audio_segment_id,
            "operation": "add_audio_segment",
            "add_audio_segment": add_audio_segment_params,
        }
        # 只在指定了轨道名称时才添加track_name字段
        if final_track_name:
            segment_data["track_name"] = final_track_name

        # 保存参数
        self.add_json_to_file(segment_data)
        self.audio_segment_id = audio_segment_id
        return return_data

    def _calculate_next_time_position(self, track_name: str, target_timerange: str) -> str:
        """
        计算轨道上下一个可用的时间位置
        
        Args:
            track_name: 轨道名称
            target_timerange: 原始时间范围
            
        Returns:
            str: 计算后的时间范围
        """
        try:
            # 解析原始时间范围
            start_str, duration_str = target_timerange.split("-", 1)
            
            # 获取轨道上所有现有的音频片段
            existing_segments = self._get_existing_audio_segments(track_name)
            
            # 如果没有现有片段，则从0开始
            if not existing_segments:
                return target_timerange
                
            # 计算所有现有片段的结束时间，找出最大的结束时间
            max_end_time = 0.0
            for segment in existing_segments:
                timerange_data = segment.get("add_audio_segment", {}).get("target_timerange", {})
                if timerange_data:
                    start = self._time_str_to_seconds(timerange_data.get("start", "0s"))
                    duration = self._time_str_to_seconds(timerange_data.get("duration", "0s"))
                    end_time = start + duration
                    max_end_time = max(max_end_time, end_time)
            
            # 新片段从最大结束时间开始
            new_start_time = max_end_time
            return f"{new_start_time:.2f}s-{duration_str}"
            
        except Exception as e:
            print(f"计算下一个时间位置失败: {e}")
            # 出错时返回原始时间范围
            return target_timerange

    def _get_existing_audio_segments(self, track_name: str) -> List[Dict[str, Any]]:
        """
        获取指定轨道上所有现有的音频片段
        
        Args:
            track_name: 轨道名称
            
        Returns:
            List[Dict]: 音频片段列表
        """
        try:
            file_path = f"{SAVE_PATH}/{self.draft_id}/audio.json"
            if not os.path.exists(file_path):
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                all_segments = json.load(f)

            # 筛选同轨道的音频片段
            track_segments = []
            for segment in all_segments:
                if segment.get("track_name") == track_name and segment.get("operation") == "add_audio_segment":
                    track_segments.append(segment)

            return track_segments
        except Exception as e:
            print(f"获取现有音频片段失败: {e}")
            return []

    def _time_str_to_seconds(self, time_str: str) -> float:
        """
        将时间字符串转换为秒数
        
        Args:
            time_str: 时间字符串，如 "1.5s"
            
        Returns:
            float: 秒数
        """
        if time_str.endswith('s'):
            return float(time_str[:-1])
        return float(time_str)

    def add_effect(self, effect_type: str, effect_name: str,
                   params: Optional[List[Optional[float]]] = None,
                   audio_segment_id: Optional[str] = None) -> bool:
        """
        添加音频特效

        Args:
            effect_type: 特效类型，"AudioSceneEffectType"、"ToneEffectType"、"SpeechToSongType"
            effect_name: 特效名称，如 "雨声"、"机器人"、"Lofi" 等
            params: 特效参数列表（可选），参数范围0-100

        Returns:
            bool: 添加是否成功
        """
        if self.audio_segment_id is None and audio_segment_id is None:
            print("错误: audio_segment_id不能为空")
            return False
        audio_segment_id = audio_segment_id or self.audio_segment_id
        # 验证特效类型
        valid_types = ["AudioSceneEffectType", "ToneEffectType", "SpeechToSongType"]
        if effect_type not in valid_types:
            print(f"错误: 无效的特效类型 '{effect_type}'，支持的类型: {valid_types}")
            return False

        # 构建add_effect参数
        add_effect_params = {
            "effect_type": effect_type,
            "effect_name": effect_name
        }

        # 只添加用户明确传入的可选参数
        if params is not None:
            add_effect_params["params"] = params

        # 构建完整的特效数据
        effect_data = {
            "audio_segment_id": audio_segment_id,
            "operation": "add_effect",
            "add_effect": add_effect_params
        }

        # 保存参数
        self.add_json_to_file(effect_data)
        return True

    def add_fade(self, in_duration: str, out_duration: str, audio_segment_id: Optional[str] = None) -> bool:
        """
        添加音频淡入淡出效果

        Args:
            in_duration: 音频淡入时长，格式如 "1s"、"500ms"
            out_duration: 音频淡出时长，格式如 "1s"、"500ms"

        Returns:
            bool: 添加是否成功
        """
        if self.audio_segment_id is None and audio_segment_id is None:
            print("错误: audio_segment_id不能为空")
            return False
        audio_segment_id = audio_segment_id or self.audio_segment_id
        # 验证参数
        if not in_duration or not out_duration:
            print("错误: in_duration和out_duration不能为空")
            return False

        # 构建add_fade参数
        add_fade_params = {
            "in_duration": in_duration,
            "out_duration": out_duration
        }

        # 构建完整的淡入淡出数据
        fade_data = {
            "audio_segment_id": audio_segment_id,
            "operation": "add_fade",
            "add_fade": add_fade_params
        }

        # 保存参数
        self.add_json_to_file(fade_data)
        return True

    def add_keyframe(self, time_offset: str, volume: float, audio_segment_id: Optional[str] = None) -> bool:
        """
        添加音频音量关键帧

        Args:
            time_offset: 关键帧的时间偏移量，格式如 "0s"、"1.5s"
            volume: 音量在time_offset处的值，范围通常0.0-1.0

        Returns:
            bool: 添加是否成功
        """
        if self.audio_segment_id is None and audio_segment_id is None:
            print("错误: audio_segment_id不能为空")
            return False
        audio_segment_id = audio_segment_id or self.audio_segment_id
        # 验证参数
        if not time_offset:
            print("错误: time_offset不能为空")
            return False

        if volume < 0.0:
            print(f"错误: 音量值不能为负数，当前值: {volume}")
            return False

        # 构建add_keyframe参数
        add_keyframe_params = {
            "time_offset": time_offset,
            "volume": volume
        }

        # 构建完整的关键帧数据
        keyframe_data = {
            "audio_segment_id": audio_segment_id,
            "operation": "add_keyframe",
            "add_keyframe": add_keyframe_params
        }

        # 保存参数
        self.add_json_to_file(keyframe_data)
        return True

    def add_json_to_file(self, new_data: Dict[str, Any]) -> bool:
        """
        向现有JSON文件中添加新的JSON数据，保持文件结构规范

        Args:
            new_data: 要添加的新数据

        Returns:
            bool: 添加是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(f"{SAVE_PATH}/{self.draft_id}", exist_ok=True)
            file_path = f"{SAVE_PATH}/{self.draft_id}/audio.json"

            # 读取现有数据
            existing_data = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        # 如果不是列表，转换为列表
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                except (json.JSONDecodeError, FileNotFoundError):
                    # 如果文件不存在或格式错误，初始化为空列表
                    existing_data = []

            # 添加新数据
            existing_data.append(new_data)

            # 保存为规范的JSON数组格式
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"添加JSON数据失败: {e}")
            return False

    def get_audio_segments(self) -> list:
        """
        获取所有音频片段记录

        Returns:
            List: 音频片段记录列表
        """
        try:
            file_path = f"{SAVE_PATH}/{self.draft_id}/audio.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"读取音频片段数据失败: {e}")
            return []

    def get_audio_segment_by_id(self, audio_segment_id: str) -> Optional[Dict[str, Any]]:
        """
        根据音频片段ID获取音频片段信息

        Args:
            audio_segment_id: 音频片段ID

        Returns:
            Dict: 音频片段信息，如果不存在返回None
        """
        audio_segments = self.get_audio_segments()
        for segment in audio_segments:
            if segment.get("audio_segment_id") == audio_segment_id:
                return segment
        return None

    def _validate_track_for_audio(self, track_name: str):
        """验证轨道是否适用于音频片段"""
        track_manager = Track(self.draft_id)

        # 检查轨道是否存在
        if not track_manager.validate_track_exists(track_name):
            raise NameError(f"轨道不存在: {track_name}")

        # 检查轨道类型是否为音频类型
        track_info = track_manager.get_track_by_name(track_name)
        if track_info:
            add_track_data = track_info.get("add_track", {})
            track_type = add_track_data.get("track_type")
            if track_type != "audio":
                raise TypeError(f"轨道 '{track_name}' 的类型是 '{track_type}'，不能添加音频片段")