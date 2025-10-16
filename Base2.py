# -*- coding: utf-8 -*-
"""
Author: jian wei
File Name:debug.py
"""
from sys import base_prefix
import re
# 可选依赖：moviepy 未使用，避免无依赖时报错

from jianyingdraft.jianying.draft import Draft
from jianyingdraft.jianying.track import Track
from jianyingdraft.jianying.audio import AudioSegment
from jianyingdraft.jianying.text import TextSegment
from jianyingdraft.jianying.export import ExportDraft
from jianyingdraft.utils.media_parser import get_media_duration
from jianyingdraft.jianying.video import VideoSegment



# 创建草稿
draft = Draft()
draft_id = draft.create_draft(draft_name='test')['draft_id']
print(draft_id)

# 创建轨道
text_track_id = Track(draft_id).add_track(track_type='text', track_name='text')
video_track_id = Track(draft_id).add_track(track_type='video', track_name='video')
Track(draft_id).add_track(track_type='audio', track_name='audio')

# 创建音频片段
base_path = 'F:\\aigc\\jianying-mcp'
audio_file = f'{base_path}/material/audio/63041799345930240.mp3'
duration = get_media_duration(audio_file)
target_timerange = f'0s-{duration:.2f}s'
audio_segment = AudioSegment(draft_id, track_name='audio')
audio_segment.add_audio_segment(material=audio_file,
                                target_timerange=target_timerange)

audio_file = f'{base_path}/material/audio/63041799345930241.mp3'
duration = get_media_duration(audio_file)
target_timerange1 = f'0s-{duration:.2f}s'
# 使用auto_next参数自动在下一个时间位置添加音频片段
audio_segment.add_audio_segment(material=audio_file,
                                target_timerange=target_timerange1,
                                auto_next=True)

audio_segment.add_fade('1s', '0.5s')


# 创建背景素材
background_video_segment = VideoSegment(draft_id, track_name='video')
background_material = f'{base_path}/material/1759353394132_背景_总裁招待客人房间.png'

# 添加背景素材
background_video_segment.add_video_segment(
    material=background_material,
    target_timerange=target_timerange,
    material_type='image'
)

# 添加第二个背景素材，使用auto_next自动计算时间位置
background_video_segment.add_video_segment(
    material=background_material,
    target_timerange=target_timerange1,
    material_type='image',
    auto_next=True
)

# 创建角色1轨道
character1_track_id = Track(draft_id).add_track(track_type='video', track_name='character1')
character1_video_segment = VideoSegment(draft_id, track_name='character1')
character1_material = f'{base_path}/material/1758472604410_角色_索亚.png'

# 添加角色1素材
character1_video_segment.add_video_segment(
    material=character1_material,
    target_timerange=target_timerange,
    material_type='image',
    clip_settings={
        "scale_x": 0.85,
        "scale_y": 0.85,
        "transform_x": -0.55,  # 向左移动，单位为半个画布宽
        "transform_y": 0.12     # 向上微调，单位为半个画布高
    }
)

# 添加第二个角色1素材，使用auto_next自动计算时间位置
character1_video_segment.add_video_segment(
    material=character1_material,
    target_timerange=target_timerange1,
    material_type='image',
    clip_settings={
        "scale_x": 0.85,
        "scale_y": 0.85,
        "transform_x": -0.55,
        "transform_y": 0.12
    },
    auto_next=True
)

# 创建角色2轨道
character2_track_id = Track(draft_id).add_track(track_type='video', track_name='character2')
character2_video_segment = VideoSegment(draft_id, track_name='character2')
character2_material = f'{base_path}/material/1758472556136_角色_蓝色挑染男生.png'

# 添加角色2素材
character2_video_segment.add_video_segment(
    material=character2_material,
    target_timerange=target_timerange,
    material_type='image',
    clip_settings={
        "scale_x": 0.85,
        "scale_y": 0.85,
        "transform_x": 0.55,   # 向右移动
        "transform_y": 0.12,
        "flip_horizontal": True  # 水平镜像，角色朝向左侧
    }
)

# 添加第二个角色2素材，使用auto_next自动计算时间位置
character2_video_segment.add_video_segment(
    material=character2_material,
    target_timerange=target_timerange1,
    material_type='image',
    clip_settings={
        "scale_x": 0.85,
        "scale_y": 0.85,
        "transform_x": 0.55,
        "transform_y": 0.12,
        "flip_horizontal": True
    },
    auto_next=True
)

# 导出到临时路径，避免剪映占用默认草稿目录导致锁定
ExportDraft(output_path='D:/soft/JianyingPro Drafts/TempExports').export(draft_id)