"""
工具函数模块

提供学生管理系统所需的各类工具函数，包括数据验证、格式化、常量定义等。
"""

import re
from datetime import datetime
from typing import Optional, Tuple


# ==================== 常量定义 ====================

# 配色方案 - 现代白色主题
COLORS = {
    'bg_primary': '#f5f7fa',        # 主背景色（浅灰白）
    'bg_secondary': '#ffffff',       # 次级背景色（纯白）
    'bg_tertiary': '#eef2f7',        # 第三层背景色
    'accent': '#4a90e2',             # 强调色（现代蓝）
    'accent_hover': '#357abd',       # 强调色悬停
    'accent_light': '#e3f2fd',       # 强调色浅色背景
    'text_primary': '#2c3e50',       # 主要文字颜色（深蓝灰）
    'text_secondary': '#5a6c7d',     # 次要文字颜色
    'text_muted': '#95a5a6',         # 柔和文字颜色
    'border': '#e1e8ed',             # 边框颜色
    'border_light': '#f0f4f8',       # 浅色边框
    'success': '#27ae60',            # 成功绿色
    'success_light': '#d5f4e6',      # 成功浅色背景
    'warning': '#f39c12',            # 警告橙色
    'warning_light': '#fef5e7',      # 警告浅色背景
    'error': '#e74c3c',              # 错误红色
    'error_light': '#fadbd8',        # 错误浅色背景
    'info': '#3498db',               # 信息蓝色
    'row_odd': '#ffffff',            # 表格奇数行
    'row_even': '#f8fafc',           # 表格偶数行
    'row_hover': '#e3f2fd',          # 表格悬停行（浅蓝）
    'shadow': 'rgba(0,0,0,0.08)',    # 阴影颜色
}

# 字体设置
FONTS = {
    'title': ('微软雅黑', 14, 'bold'),
    'subtitle': ('微软雅黑', 12, 'bold'),
    'normal': ('微软雅黑', 11),
    'small': ('微软雅黑', 10),
    'monospace': ('Consolas', 10),
}

# 班级列表
CLASS_LIST = [
    '计算机一班',
    '计算机二班', 
    '软件工程一班',
    '软件工程二班',
    '人工智能班'
]

# 专业列表（与班级对应）
MAJOR_LIST = [
    '计算机科学与技术',
    '计算机科学与技术',
    '软件工程',
    '软件工程',
    '人工智能'
]

# 班级代码映射（用于生成学号）
CLASS_CODE_MAP = {
    '计算机一班': '01',
    '计算机二班': '02',
    '软件工程一班': '03',
    '软件工程二班': '04',
    '人工智能班': '05',
}

# 性别选项
GENDER_OPTIONS = ['男', '女']


# ==================== 验证函数 ====================

def validate_student_id(student_id: str) -> Tuple[bool, str]:
    """
    验证学号格式
    
    学号格式：2024 + 班级代码(2位) + 流水号(3位)，共9位数字
    
    Args:
        student_id: 待验证的学号
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not student_id:
        return False, "学号不能为空"
    
    if not re.match(r'^\d{9}$', student_id):
        return False, "学号必须为9位数字"
    
    if not student_id.startswith('2024'):
        return False, "学号必须以2024开头"
    
    class_code = student_id[4:6]
    valid_codes = list(CLASS_CODE_MAP.values())
    if class_code not in valid_codes:
        return False, f"班级代码{class_code}无效"
    
    serial = student_id[6:9]
    if not (1 <= int(serial) <= 999):
        return False, "流水号必须在001-999之间"
    
    return True, ""


def validate_name(name: str) -> Tuple[bool, str]:
    """
    验证姓名格式
    
    Args:
        name: 待验证的姓名
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not name:
        return False, "姓名不能为空"
    
    if len(name) < 2 or len(name) > 20:
        return False, "姓名长度必须在2-20个字符之间"
    
    # 只允许中文、英文和空格
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s·]+$', name):
        return False, "姓名只能包含中文、英文字母和空格"
    
    return True, ""


def validate_age(age: int) -> Tuple[bool, str]:
    """
    验证年龄范围
    
    Args:
        age: 待验证的年龄
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not isinstance(age, int):
        return False, "年龄必须为整数"
    
    if age < 1 or age > 100:
        return False, "年龄必须在1-100岁之间"
    
    return True, ""


def validate_score(score: float) -> Tuple[bool, str]:
    """
    验证成绩范围
    
    Args:
        score: 待验证的成绩
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    try:
        score = float(score)
        if score < 0 or score > 100:
            return False, "成绩必须在0-100分之间"
        return True, ""
    except (ValueError, TypeError):
        return False, "成绩必须为数字"


def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    验证日期格式
    
    Args:
        date_str: 待验证的日期字符串（格式：YYYY-MM-DD）
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not date_str:
        return False, "日期不能为空"
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "日期格式必须为YYYY-MM-DD"


def validate_student_data(data: dict) -> Tuple[bool, str]:
    """
    验证完整的学生数据
    
    Args:
        data: 包含学生信息的字典
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    required_fields = ['student_id', 'name', 'gender', 'age', 'class_name', 'major', 'enrollment_date', 'score']
    
    # 检查必填字段
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            field_names = {
                'student_id': '学号',
                'name': '姓名',
                'gender': '性别',
                'age': '年龄',
                'class_name': '班级',
                'major': '专业',
                'enrollment_date': '入学日期',
                'score': '成绩'
            }
            return False, f"{field_names.get(field, field)}不能为空"
    
    # 验证各字段
    valid, msg = validate_student_id(data['student_id'])
    if not valid:
        return False, msg
    
    valid, msg = validate_name(data['name'])
    if not valid:
        return False, msg
    
    valid, msg = validate_age(data['age'])
    if not valid:
        return False, msg
    
    valid, msg = validate_score(data['score'])
    if not valid:
        return False, msg
    
    valid, msg = validate_date(data['enrollment_date'])
    if not valid:
        return False, msg
    
    if data['gender'] not in GENDER_OPTIONS:
        return False, "性别必须是男或女"
    
    if data['class_name'] not in CLASS_LIST:
        return False, f"班级必须是以下之一：{', '.join(CLASS_LIST)}"
    
    return True, ""


# ==================== 格式化函数 ====================

def format_score(score: float, decimals: int = 1) -> str:
    """
    格式化成绩显示
    
    Args:
        score: 成绩数值
        decimals: 小数位数
        
    Returns:
        str: 格式化后的成绩字符串
    """
    try:
        return f"{float(score):.{decimals}f}"
    except (ValueError, TypeError):
        return "0.0"


def format_date(date_str: str) -> str:
    """
    格式化日期显示
    
    Args:
        date_str: 日期字符串
        
    Returns:
        str: 格式化后的日期字符串
    """
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y年%m月%d日')
    except (ValueError, TypeError):
        return date_str


def get_score_level(score: float) -> str:
    """
    根据成绩获取等级
    
    Args:
        score: 成绩数值
        
    Returns:
        str: 等级（优秀/良好/中等/及格/不及格）
    """
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"


def get_score_color(score: float) -> str:
    """
    根据成绩获取对应的颜色
    
    Args:
        score: 成绩数值
        
    Returns:
        str: 颜色代码
    """
    if score >= 90:
        return '#4ec9b0'  # 绿色
    elif score >= 80:
        return '#569cd6'  # 蓝色
    elif score >= 70:
        return '#dcdcaa'  # 黄色
    elif score >= 60:
        return '#ce9178'  # 橙色
    else:
        return '#f48771'  # 红色


def truncate_string(text: str, max_length: int = 20) -> str:
    """
    截断过长字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        
    Returns:
        str: 截断后的字符串
    """
    if len(text) > max_length:
        return text[:max_length-3] + '...'
    return text


# ==================== 辅助函数 ====================

def generate_student_id(class_name: str, serial: int) -> str:
    """
    根据班级和流水号生成学号
    
    Args:
        class_name: 班级名称
        serial: 流水号（1-999）
        
    Returns:
        str: 生成的学号
    """
    class_code = CLASS_CODE_MAP.get(class_name, '01')
    return f"2024{class_code}{serial:03d}"


def get_major_by_class(class_name: str) -> str:
    """
    根据班级获取对应的专业
    
    Args:
        class_name: 班级名称
        
    Returns:
        str: 专业名称
    """
    try:
        index = CLASS_LIST.index(class_name)
        return MAJOR_LIST[index]
    except ValueError:
        return "计算机科学与技术"


def center_window(window, width: int, height: int):
    """
    将窗口居中显示
    
    Args:
        window: tkinter窗口对象
        width: 窗口宽度
        height: 窗口高度
    """
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')
