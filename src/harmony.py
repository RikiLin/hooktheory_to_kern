from maps import *

# === 计算和弦 ===
def chord_name(chord):
    root_pc = chord["root_pitch_class"]
    root_intervals = chord["root_position_intervals"]
    root = PITCH_MAP[1][root_pc]
    intervals = chord["root_position_intervals"]
    inversion = chord.get("inversion", 0)

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

    # 如果存在转位
    if 0 < inversion < len(intervals) + 1:
        # 计算低音音名
        bass_pc = (root_pc + sum(intervals[:inversion])) % 12
        bass_note = PITCH_MAP[1][bass_pc]
        return f"{root}{suffix}:{bass_note}"
    else:
        return f"{root}{suffix}"

# === 和弦解析 ===
def parse_harmony(song_data):
    harmony = song_data["annotations"]["harmony"]
    chords = dict()
    for h in harmony:
        onset = float(h["onset"])
        offset = h["offset"]
        dur = offset - onset
        name = chord_name(h)
        #chords.append({"onset": onset, "duration": dur, "token": name})
        chords[onset] = name
    return chords