import json
from pprint import pprint
import statistics

PITCH_MAP = [
    ['CC', 'CC#', 'DD', 'DD#', 'EE', 'FF', 'FF#', 'GG', 'GG#', 'AA', 'AA#', 'BB'],
    ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'], # < C4
    ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b'], # >= C4
    ['cc', 'cc#', 'dd', 'dd#', 'ee', 'ff', 'ff#', 'gg', 'gg#', 'aa', 'aa#', 'bb']
]

with open("fileExample.json", "r", encoding="utf-8") as f:
    data = json.load(f)

song_id = list(data.keys())[0]
song = data[song_id]

# === 基础信息 ===
info = song["hooktheory"]
print(f"!!!COM: {info['artist']}")
print(f"!!!OPR@@DE: {info['song']}")
print("!!!OPR@EN: Youtube")
print("!!!voices: 2")

# === 谱表 ==
print("**kern\t**mxhm")
print("*clef:G2\t*")

'''
# === Alignment & Tempo ===
align = song["alignment"]
beats = align["refined"]["beats"]
times = align["refined"]["times"]
beat_durations = [t2 - t1 for t1, t2 in zip(times[:-1], times[1:])]
avg_tempo = 60 / (sum(beat_durations) / len(beat_durations))
print(f"Tempo ≈ {avg_tempo:.1f} BPM")
'''

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
print(f"*k[{''.join(PITCH_MAP[2][p] for p in scale if p in {1, 3, 6, 8, 10})}]\t*")

# === 拍号 ===
print(f"*M{meter['beats_per_bar']}/{meter['beat_unit']}\t*")

# === 计算节拍长度 ===
def beat_to_duration(beat_len):
    """将拍长转换为 Humdrum 记号"""
    mapping = {2: "2", 1: "4", 0.5: "8", 0.25: "16"}
    # 匹配不到时，选择最接近的
    dur = min(mapping.keys(), key=lambda x: abs(x - beat_len))
    return mapping[dur]

# === Melody ===

# === 旋律解析 ===
def parse_melody(song_data):
    """
    传入需要处理的歌曲数据，返回一个带有时间标记的可用记号
    :param song_data:
    :return: melodydic[onset, name]
    """
    melody = song["annotations"]["melody"]
    lines = []
    for n in melody:
        # duration
        onset, offset = n["onset"], n["offset"]
        dur = offset - onset
        dur_code = beat_to_duration(dur)

        # Note
        pc = n["pitch_class"]
        oct = n["octave"] + 2
        note_name = PITCH_MAP[oct][pc]

        #lines.append({"onset": onset, "duration": dur, "token": f"{dur_code}{note_name}"})
        lines.append([onset, dur, f"{dur_code}{note_name}"])

    return lines

# === Harmony ===

# === 计算和弦 ===
def chord_name(chord):
    root_pc = chord["root_pitch_class"]
    root_intervals = chord["root_position_intervals"]
    root = PITCH_MAP[1][root_pc]

    if root_intervals == [4, 3]:
        suffix = ""
    elif root_intervals == [3, 4]:
        suffix = "m"
    elif root_intervals == [3, 3]:
        suffix = "dim"
    elif root_intervals == [4, 4]:
        suffix = "aug"
    else:
        suffix = "?"

    if suffix:
        return root + ":" + suffix
    else:
        return root

# === 和弦解析 ===
def parse_harmony(song_data):
    harmony = song_data["annotations"]["harmony"]
    chords = []
    for h in harmony:
        onset = h["onset"]
        offset = h["offset"]
        dur = offset - onset
        name = chord_name(h)
        #chords.append({"onset": onset, "duration": dur, "token": name})
        chords.append([onset, dur, name])
    return chords


def combine_melody_harmony(melody_list, harmony_list, beats_per_bar=4):
    """双指针合成，自动小节划分"""
    time = 0.0
    bar_accum = 0.0

    i, j = 0, 0
    active_chord = None
    lines = []

    while i < len(melody_list) or j < len(harmony_list):
        # 更新当前和弦
        if j < len(harmony_list):
            onset_h, dur_h, chord_code = harmony_list[j]
            if time >= onset_h:
                active_chord = chord_code
            if time >= onset_h + dur_h:
                j += 1
                if j < len(harmony_list):
                    active_chord = harmony_list[j][2]

        # 输出旋律事件
        if i < len(melody_list):
            onset_m, dur_m, note_code = melody_list[i]
            if abs(time - onset_m) < 1e-6:  # 当前时间有音符开始
                lines.append(f"{note_code}\t{active_chord or '.'}")
                time += dur_m
                bar_accum += dur_m
                i += 1
            else:
                # 若当前时间无旋律事件，推进到下个onset
                next_onset = melody_list[i][0]
                step = next_onset - time
                time += step
                bar_accum += step
        else:
            break

        # 检查是否该换小节
        if bar_accum >= beats_per_bar - 1e-6:
            lines.append("=\t=")
            bar_accum = 0.0

    lines.append("*–\t*–")

    return "\n".join(lines)
# === 生成 ===
#def to_humdrum(song_data):



melody_output = parse_melody(song)
harmony_output = parse_harmony(song)
print(combine_melody_harmony(melody_output, harmony_output))

'''melody = song["annotations"]["melody"]
print(f"旋律音符总数: {len(melody)}")
print("前10个音符:")
for n in melody[:10]:
    onset, offset = n["onset"], n["offset"]
    dur = offset - onset
    pc = n["pitch_class"]
    oct = n["octave"] + 2
    name = PITCH_MAP[oct][pc]
    print(f"  起拍={onset:<5} 终拍={offset:<5} 时值={dur:<4} 音名={name}")

durations = [n["offset"] - n["onset"] for n in melody]
pitch_classes = [n["pitch_class"] for n in melody]
print(f"平均音长: {statistics.mean(durations):.2f} 拍")
print(f"音阶集合: {sorted({PITCH_MAP[p] for p in pitch_classes})}")'''
