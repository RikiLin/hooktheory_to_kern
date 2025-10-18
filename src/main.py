import json
from melody import *
from harmony import *
from beaming import *

with open("Hooktheory.json", "r") as f:
    data = json.load(f)

song_id = list(data.keys())[0]
song = data[song_id]

# === 基础信息 ===
info = song["hooktheory"]
head = [
    f"!!!COM: {info['artist']}",
    f"!!!OPR@@DE: {info['song']}",
    "!!!OPR@EN: Youtube", "!!!voices: 2",
    "**kern\t**mxhm",
    "*clefG2\t*"
]

# === 谱表 ==
meter = song["annotations"]["meters"][0]
key = song["annotations"]["keys"][0]

# === 调号 ===
def get_scale_map(tonic_pitch_class, scale_intervals):
    scale_pcs = [tonic_pitch_class]
    for interval in scale_intervals:
        scale_pcs.append((scale_pcs[-1] + interval) % 12)
    return scale_pcs

tonic_pc = key["tonic_pitch_class"]  # D major
intervals = key["scale_degree_intervals"]
scale = get_scale_map(tonic_pc, intervals)
head.append(f"*k[{''.join(PITCH_MAP[2][p] for p in scale if p in {1, 3, 6, 8, 10})}]\t*")

# === 拍号 ===
beats_per_bar = meter["beats_per_bar"]
beat_unit = meter["beat_unit"]
head.append(f"*M{beats_per_bar}/{meter['beat_unit']}\t*")

# === Melody ===
melody_output = parse_melody(song, beats_per_bar)
melody_output = note_beaming(melody_output)

# === Harmony ===
harmony_output = parse_harmony(song)

# === 生成 ===
def combine_melody_harmony(melody_list, harmony_list):
    """双指针合成，自动小节划分"""
    lines = []

    for m in melody_list:
        if type(m[0]) != str:
            if m[0] in harmony_list:
                lines.append(f"{m[1]}\t{harmony_list[m[0]]}")
            else:
                lines.append(f"{m[1]}\t.")
        else:
            lines.append(f"{m[0]}\t{m[0]}")

    lines.append("*–\t*–")
    return "\n".join(lines)

head = "\n".join(head)
sheet = combine_melody_harmony(melody_output, harmony_output)

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(head + "\n")  # 第一行
    f.write(sheet)