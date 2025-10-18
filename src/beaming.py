import re

def is_valid_note(item):
    """
    检查项目是否有效：数字大于4且不是休止符
    """
    if not isinstance(item, str):
        return False

    if 'r' in item:  # 是休止符
        return False

    # 提取数字部分
    match = re.search(r'(\d+)', item)
    if match:
        num = int(match.group(1))
        return num > 4  # 数字大于4

    return False

def note_beaming(notes_list_2d):
    """
    处理二维列表，只修改第1维的音符信息
    """
    # 提取第1维的音符信息
    music_notes = [item[1] for item in notes_list_2d]

    # 处理音符信息
    processed_notes = process_music_notes(music_notes)

    # 构建结果二维列表
    result = []
    for i, item in enumerate(notes_list_2d):
        if isinstance(item, list) and len(item) > 1:
            # 保持时间序列不变，只更新音符信息
            new_item = [item[0], processed_notes[i]]
            result.append(new_item)
        else:
            # 一维元素，直接使用处理后的结果
            result.append(processed_notes[i])

    return result


def process_music_notes(music_notes):
    """
    处理一维的音符列表
    """
    result = []
    current_section = []

    for item in music_notes:
        if isinstance(item, str) and item.startswith('='):
            if current_section:
                process_section(current_section, result)
                current_section = []
            result.append(item)
        else:
            current_section.append(item)

    if current_section:
        process_section(current_section, result)

    return result


def process_section(section, result):
    """
    处理单个节拍段，对连续的数字大于4且不是休止符的项目进行分组标记
    """
    if not section:
        return

    valid_groups = find_valid_groups(section)

    # 对每个有效组进行标记（只有当组长度>1时才标记）
    if valid_groups:
        index_marks = {}

        for group in valid_groups:
            # 连续的有效音符数量大于1时才标记
            if len(group) > 1:
                first_idx = group[0]
                last_idx = group[-1]

                # 标记第一个项目
                if first_idx not in index_marks:
                    index_marks[first_idx] = 'L'

                # 标记最后一个项目
                if last_idx not in index_marks:
                    index_marks[last_idx] = 'J'

        modified_section = []
        for i, item in enumerate(section):
            if i in index_marks:
                modified_section.append(item + index_marks[i])
            else:
                modified_section.append(item)

        result.extend(modified_section)
    else:
        result.extend(section)


def find_valid_groups(section):
    """
    找出节拍段内所有连续的数字大于4且不是休止符的项目组
    """
    groups = []
    current_group = []

    for i, item in enumerate(section):
        if isinstance(item, str) and is_valid_note(item):
            current_group.append(i)
        else:
            # 遇到无效项目，结束当前组
            if len(current_group) > 0:
                groups.append(current_group)
                current_group = []

    # 添加最后一个组
    if len(current_group) > 0:
        groups.append(current_group)

    return groups

