from maps import *



# === 计算节拍长度 ===
def beat_to_duration(beat_len):
    """将拍长转换为 Humdrum 记号"""
    mapping = {2: "2", 1: "4", 0.5: "8", 0.25: "16"}
    # 匹配不到时，选择最接近的
    dur = min(mapping.keys(), key=lambda x: abs(x - beat_len))
    return mapping[dur]

# === 旋律解析 ===
def parse_melody(song_data, bpb):
    """
    传入需要处理的歌曲数据，返回一个带有时间标记的可用记号
    :param song_data:
    :return: melodydic[onset, name]
    """
    current_time = float(0)
    current_bar = 1
    current_bar_time = 0.0
    bar_time = 1
    melody = song_data["annotations"]["melody"]
    lines = [["=1", "=1"]]

    for n in melody:
        # 检查是否需要休符
        if n["onset"] > current_time:
            dur = n["onset"] - current_time
            dur_code = beat_to_duration(dur)
            lines.append([current_time, f"{dur_code}r"])
            current_bar_time += dur

        # 检查小节是否需要增加
        if current_bar_time >= 4:
            current_bar_time = current_bar_time % 4
            current_bar += 1
            lines.append([f"={current_bar}", f"={current_bar}"])


        # Note
        pc = n["pitch_class"]
        oct = n["octave"] + 2
        note_name = PITCH_MAP[oct][pc]

        # duration
        onset, offset = n["onset"], n["offset"]
        dur = offset - onset

        # 检查是否需要连音，即出现跨小节
        if onset  < current_bar * bpb < offset:
            last = current_bar * bpb - onset
            lines.append([onset, f"[{beat_to_duration(last)}{note_name}"])
            current_bar += 1
            lines.append([f"={current_bar}", f"={current_bar}"])
            lines.append([(current_bar - 1) * bpb, f"{beat_to_duration(dur - last)}{note_name}]"])
            current_bar_time = dur - last

        else:
            dur_code = beat_to_duration(dur)
            lines.append([onset, f"{dur_code}{note_name}"])
            current_bar_time += dur

        current_time = n["offset"]

    return lines
