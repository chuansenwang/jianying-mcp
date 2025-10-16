# -*- coding: utf-8 -*-
"""
Author: jian wei
File Name:debug.py
"""
from sys import base_prefix
import re
from moviepy import AudioFileClip

from jianyingdraft.jianying.draft import Draft
from jianyingdraft.jianying.track import Track
from jianyingdraft.jianying.audio import AudioSegment
from jianyingdraft.jianying.text import TextSegment
from jianyingdraft.jianying.export import ExportDraft
from jianyingdraft.utils.media_parser import get_media_duration
from jianyingdraft.jianying.video import VideoSegment


def get_audio_duration(file_path):
    clip = AudioFileClip(file_path)
    duration = clip.duration
    clip.close()
    return duration

def parse_srt_time(time_str):
    """将SRT时间格式转换为秒数"""
    time_parts = re.split('[:,]', time_str)
    hours, minutes, seconds, milliseconds = map(int, time_parts)
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0

def parse_srt_file(file_path):
    """解析SRT文件并返回字幕片段列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按双换行符分割字幕块
    # 先规范化换行符
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    blocks = content.strip().split('\n\n')
    
    parsed_subtitles = []
    
    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        # 检查是否至少有3行：编号、时间轴、文本
        if len(lines) >= 2:
            # 检查第二行是否包含时间轴格式
            if ' --> ' in lines[1]:
                try:
                    # 解析时间轴
                    time_line = lines[1]
                    start_time, end_time = time_line.split(' --> ')
                    start_seconds = parse_srt_time(start_time)
                    end_seconds = parse_srt_time(end_time)
                    
                    # 文本内容可能在多行
                    text_lines = lines[2:] if len(lines) > 2 else []
                    text = ' '.join(text_lines).strip()
                    
                    parsed_subtitles.append({
                        'start': start_seconds,
                        'end': end_seconds,
                        'text': text
                    })
                except Exception as e:
                    print(f"解析字幕块时出错: {e}, 块内容: {block}")
                    continue
    
    return parsed_subtitles

# 创建草稿
draft = Draft()
draft_id = draft.create_draft(draft_name='test')['draft_id']
print(draft_id)

# 创建轨道
text_track_id = Track(draft_id).add_track(track_type='text', track_name='text')
video_track_id = Track(draft_id).add_track(track_type='video', track_name='video')
Track(draft_id).add_track(track_type='audio', track_name='audio')

# 创建音频片段
# 使用示例
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


# 创建图片素材
video_segment = VideoSegment(draft_id, track_name='video')
material = f'{base_path}/material/1759353394132_总裁招待客人房间.png'

# 添加第一个图片素材
video_segment.add_video_segment(
    material=material,
    target_timerange=target_timerange,
    material_type='image'
)

# 添加第二个图片素材，使用auto_next自动计算时间位置
video_segment.add_video_segment(
    material=material,
    target_timerange=target_timerange1,
    material_type='image',
    auto_next=True
)

# # 创建视频片段
# video_segment1 = VideoSegment(draft_id, track_name='video')
# video_segment1.add_video_segment(
#     material='../material/video1.mp4',
#     target_timerange='0s-6s'
# )
# video_segment1.add_transition('叠化', '1s')
# video_segment1.add_filter('冬漫', intensity=50.0)
# video_segment2 = VideoSegment(draft_id, track_name='video')
# video_segment2.add_video_segment(
#     material='../material/video2.mp4',
#     target_timerange='6s-5s'
# )
# video_segment2.add_background_filling('blur', blur=0.5)
# video_segment2.add_mask(
#     mask_type='爱心',
#     center_x=0.5,
#     center_y=0.5,
#     size=0.5,
#     rotation=0.0,
#     feather=0.0,
#     invert=False,
#     rect_width=0.5,
#     round_corner=0.0
# )
# video_segment2.add_transition('闪黑', '1s')

# video_segment3 = VideoSegment(draft_id, track_name='video')
# video_segment3.add_video_segment(
#     material='../material/video3.mp4',
#     target_timerange='11s-5.20s'
# )
# 添加字幕

# 创建文本片段（调整时间避免与字幕冲突）
text_segment1 = TextSegment(
    draft_id=draft_id,
    track_name="text"
)
add_text_segment_params = text_segment1.add_text_segment(
    text="这是jianying-mcp制作的视频",
    timerange="0s-3s",
    clip_settings={"transform_y": -0.8}
)
# text_segment1.add_animation('TextIntro', animation_name='向上滑动', duration='1s')
# text_segment1.add_animation('TextOutro', animation_name='右上弹出', duration='1s')
#
# text_segment2 = TextSegment(
#     draft_id=draft_id,
#     track_name="text"
# )
# text_segment2.add_text_segment(
#     text="欢迎大家使用",
#     timerange="3s-3s",
#     clip_settings={"transform_y": -0.8}
# )
# text_segment3 = TextSegment(
#     draft_id=draft_id,
#     track_name="text"
# )
# text_segment3.add_text_segment(
#     text="如果这个项目对你有帮助，请给个 Star 支持一下！",
#     timerange="6s-3s",
#     clip_settings={"transform_y": -0.8}
# )
# text_segment3.add_animation("TextLoopAnim", "色差故障")

# 解析字幕文件，添加字幕内容
base_path = 'F:\\aigc\\jianying-mcp'
srt_files = [
    f'{base_path}/material/srt/63041799345930240.srt',
    f'{base_path}/material/srt/63041799345930241.srt',
    f'{base_path}/material/srt/63041799345930243.srt'
]

# 创建文本片段实例
subtitle_segment = TextSegment(draft_id=draft_id, track_name="text")

# 解析SRT文件获取字幕数据
all_subtitles = []
for srt_file in srt_files:
    subtitles = parse_srt_file(srt_file)
    all_subtitles.extend(subtitles)

# 使用add_text_segment方法添加字幕
for subtitle in all_subtitles:
    start_time = subtitle['start']
    end_time = subtitle['end']
    text = subtitle['text']
    duration = end_time - start_time
    
    # 设置字幕样式，包括颜色
    style = {
        "color": (1.0, 1.0, 0.0),  # 黄色 (RGB三元组，取值范围[0, 1])
        "size": 6.0,  # 字体大小
        "bold": True,  # 是否加粗
        "alpha": 1.0   # 不透明度
    }
    
    # 使用add_text_segment方法的auto_next参数添加字幕
    subtitle_segment.add_text_segment(
        text=text,
        timerange=f"0s-{duration:.3f}s",  # 提供持续时间，开始时间会自动计算
        clip_settings={"transform_y": -0.7},  # 位置设置在底部
        style=style,  # 设置字幕样式
        auto_next=True  # 启用自动追加功能
    )

ExportDraft().export(draft_id)