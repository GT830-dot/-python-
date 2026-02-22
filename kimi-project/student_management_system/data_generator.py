"""
数据生成器模块

使用faker库生成中文真实学生数据，包括姓名、学号、成绩等。
支持批量生成和进度回调。
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional, Tuple
from faker import Faker

from utils import CLASS_LIST, MAJOR_LIST, CLASS_CODE_MAP, GENDER_OPTIONS

# 类型提示导入（避免循环导入）
if __name__ != '__main__':
    from database import DatabaseManager


class DataGenerator:
    """
    学生数据生成器
    
    使用faker生成真实的中文学生数据，支持自定义数量和参数。
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        初始化数据生成器
        
        Args:
            seed: 随机种子，用于可重复的结果
        """
        self.fake = Faker('zh_CN')
        if seed is not None:
            self.fake.seed_instance(seed)
            random.seed(seed)
            np.random.seed(seed)
        
        # 记录每个班级的当前流水号
        self.class_counters = {cls: 0 for cls in CLASS_LIST}
    
    def generate_student_id(self, class_name: str) -> str:
        """
        生成学号
        
        格式：2024 + 班级代码(2位) + 流水号(3位)
        例如：202401001
        
        Args:
            class_name: 班级名称
            
        Returns:
            str: 生成的学号
        """
        class_code = CLASS_CODE_MAP.get(class_name, '01')
        self.class_counters[class_name] += 1
        serial = self.class_counters[class_name]
        return f"2024{class_code}{serial:03d}"
    
    def generate_name(self) -> str:
        """
        生成中文姓名
        
        Returns:
            str: 随机中文姓名
        """
        return self.fake.name()
    
    def generate_gender(self) -> str:
        """
        生成性别
        
        Returns:
            str: '男' 或 '女'
        """
        return random.choice(GENDER_OPTIONS)
    
    def generate_age(self) -> int:
        """
        生成年龄
        
        大学生年龄通常在18-25岁之间
        
        Returns:
            int: 随机年龄
        """
        return random.randint(18, 25)
    
    def generate_class(self) -> str:
        """
        生成班级
        
        Returns:
            str: 随机班级名称
        """
        return random.choice(CLASS_LIST)
    
    def get_major_by_class(self, class_name: str) -> str:
        """
        根据班级获取专业
        
        Args:
            class_name: 班级名称
            
        Returns:
            str: 对应的专业名称
        """
        try:
            index = CLASS_LIST.index(class_name)
            return MAJOR_LIST[index]
        except ValueError:
            return "计算机科学与技术"
    
    def generate_score(self, mean: float = 75, std: float = 15) -> float:
        """
        生成成绩
        
        使用正态分布生成成绩，默认均值75，标准差15
        成绩范围限制在0-100之间
        
        Args:
            mean: 均值
            std: 标准差
            
        Returns:
            float: 随机成绩，保留一位小数
        """
        score = np.random.normal(mean, std)
        # 限制在0-100范围内
        score = max(0, min(100, score))
        return round(score, 1)
    
    def generate_enrollment_date(self) -> str:
        """
        生成入学日期
        
        在2021-2024年间生成随机日期
        
        Returns:
            str: 格式为YYYY-MM-DD的日期字符串
        """
        # 生成2021-2024年间的随机日期
        start_date = datetime(2021, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        random_date = start_date + timedelta(days=random_days)
        
        return random_date.strftime('%Y-%m-%d')
    
    def generate_student(self, class_name: Optional[str] = None) -> Dict[str, Any]:
        """
        生成单个学生数据
        
        Args:
            class_name: 指定班级，None则随机选择
            
        Returns:
            Dict: 学生信息字典
        """
        if class_name is None:
            class_name = self.generate_class()
        
        student = {
            'student_id': self.generate_student_id(class_name),
            'name': self.generate_name(),
            'gender': self.generate_gender(),
            'age': self.generate_age(),
            'class_name': class_name,
            'major': self.get_major_by_class(class_name),
            'enrollment_date': self.generate_enrollment_date(),
            'score': self.generate_score(),
        }
        
        return student
    
    def generate_students(
        self, 
        count: int = 200,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量生成学生数据
        
        确保每个班级都有学生，尽量平均分配
        
        Args:
            count: 要生成的学生数量
            progress_callback: 进度回调函数，参数为(当前数量, 总数)
            
        Returns:
            List[Dict]: 学生数据列表
        """
        students = []
        
        # 计算每个班级的基础数量
        num_classes = len(CLASS_LIST)
        base_count = count // num_classes
        remainder = count % num_classes
        
        # 为每个班级生成学生
        for i, class_name in enumerate(CLASS_LIST):
            # 前remainder个班级多一个学生
            class_count = base_count + (1 if i < remainder else 0)
            
            for _ in range(class_count):
                student = self.generate_student(class_name)
                students.append(student)
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(len(students), count)
        
        # 打乱顺序，使数据更真实
        random.shuffle(students)
        
        return students
    
    def generate_class_distribution(self, total: int = 200) -> Dict[str, int]:
        """
        生成分配到各班级的学生数量
        
        Args:
            total: 总学生数
            
        Returns:
            Dict: 各班级学生数量
        """
        num_classes = len(CLASS_LIST)
        base = total // num_classes
        remainder = total % num_classes
        
        distribution = {}
        for i, class_name in enumerate(CLASS_LIST):
            count = base + (1 if i < remainder else 0)
            distribution[class_name] = count
        
        return distribution
    
    def reset_counters(self):
        """
        重置班级流水号计数器
        """
        self.class_counters = {cls: 0 for cls in CLASS_LIST}


def generate_sample_data(
    db_manager,
    count: int = 200,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Tuple[int, int]:
    """
    生成示例数据并插入数据库
    
    Args:
        db_manager: 数据库管理器实例
        count: 要生成的学生数量
        progress_callback: 进度回调函数，参数为(成功数, 总数, 状态信息)
        
    Returns:
        Tuple[int, int]: (成功数量, 失败数量)
    """
    generator = DataGenerator(seed=42)  # 使用固定种子以便可重复
    
    def internal_progress(current, total):
        if progress_callback:
            progress_callback(current, total, f"正在生成数据... ({current}/{total})")
    
    # 生成数据
    students = generator.generate_students(count, internal_progress)
    
    # 批量插入
    if progress_callback:
        progress_callback(count, count, "正在插入数据库...")
    
    success, failed = db_manager.batch_insert(students)
    
    if progress_callback:
        progress_callback(success, count, f"完成！成功插入{success}条数据")
    
    return success, failed
