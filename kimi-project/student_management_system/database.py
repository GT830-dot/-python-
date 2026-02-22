"""
数据库操作模块

提供学生管理系统所需的所有数据库操作，包括连接管理、CRUD操作等。
使用SQLite3作为数据库，支持参数化查询防止SQL注入。
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple, Any
from contextlib import contextmanager
from utils import validate_student_data


class DatabaseManager:
    """
    数据库管理类
    
    负责数据库连接、表结构初始化和所有CRUD操作。
    使用上下文管理器确保资源正确释放。
    """
    
    def __init__(self, db_path: str = 'students.db'):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认为当前目录下的students.db
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
    @contextmanager
    def _get_connection(self):
        """
        上下文管理器：获取数据库连接
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"数据库连接失败: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def init_database(self) -> bool:
        """
        初始化数据库，创建表结构
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建学生表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        gender TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        class_name TEXT NOT NULL,
                        major TEXT NOT NULL,
                        enrollment_date TEXT NOT NULL,
                        score REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引以提高查询性能
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_student_id ON students(student_id)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_name ON students(name)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_class ON students(class_name)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_major ON students(major)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_score ON students(score)
                ''')
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"初始化数据库失败: {str(e)}")
            return False
    
    def is_empty(self) -> bool:
        """
        检查学生表是否为空
        
        Returns:
            bool: 表是否为空
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM students')
                count = cursor.fetchone()[0]
                return count == 0
        except Exception as e:
            print(f"检查表是否为空失败: {str(e)}")
            return True
    
    def get_count(self) -> int:
        """
        获取学生总数
        
        Returns:
            int: 学生总数
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM students')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"获取学生总数失败: {str(e)}")
            return 0
    
    # ==================== CRUD 操作 ====================
    
    def add_student(self, student_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        添加学生
        
        Args:
            student_data: 包含学生信息的字典
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 数据验证
        valid, msg = validate_student_data(student_data)
        if not valid:
            return False, msg
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查学号是否已存在
                cursor.execute(
                    'SELECT id FROM students WHERE student_id = ?',
                    (student_data['student_id'],)
                )
                if cursor.fetchone():
                    return False, f"学号 {student_data['student_id']} 已存在"
                
                # 插入数据
                cursor.execute('''
                    INSERT INTO students 
                    (student_id, name, gender, age, class_name, major, enrollment_date, score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    student_data['student_id'],
                    student_data['name'],
                    student_data['gender'],
                    student_data['age'],
                    student_data['class_name'],
                    student_data['major'],
                    student_data['enrollment_date'],
                    student_data['score']
                ))
                
                conn.commit()
                return True, "添加成功"
                
        except sqlite3.IntegrityError as e:
            return False, f"数据完整性错误: {str(e)}"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def update_student(self, student_id: str, student_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新学生信息
        
        Args:
            student_id: 学生学号
            student_data: 包含更新字段的字典
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查学生是否存在
                cursor.execute(
                    'SELECT id FROM students WHERE student_id = ?',
                    (student_id,)
                )
                if not cursor.fetchone():
                    return False, f"学号 {student_id} 不存在"
                
                # 构建更新语句
                allowed_fields = ['name', 'gender', 'age', 'class_name', 
                                 'major', 'enrollment_date', 'score']
                updates = []
                values = []
                
                for field in allowed_fields:
                    if field in student_data:
                        updates.append(f"{field} = ?")
                        values.append(student_data[field])
                
                if not updates:
                    return False, "没有要更新的字段"
                
                values.append(student_id)
                
                cursor.execute(f'''
                    UPDATE students 
                    SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ?
                ''', values)
                
                conn.commit()
                return True, "更新成功"
                
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def delete_student(self, student_id: str) -> Tuple[bool, str]:
        """
        删除学生
        
        Args:
            student_id: 学生学号
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    'DELETE FROM students WHERE student_id = ?',
                    (student_id,)
                )
                
                if cursor.rowcount == 0:
                    return False, f"学号 {student_id} 不存在"
                
                conn.commit()
                return True, "删除成功"
                
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        根据学号获取学生信息
        
        Args:
            student_id: 学生学号
            
        Returns:
            Optional[Dict]: 学生信息字典，不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT student_id, name, gender, age, class_name, 
                           major, enrollment_date, score
                    FROM students WHERE student_id = ?
                ''', (student_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            print(f"获取学生信息失败: {str(e)}")
            return None
    
    def search_students(
        self,
        keyword: str = '',
        class_name: str = '',
        major: str = '',
        min_score: float = 0,
        max_score: float = 100,
        order_by: str = 'student_id',
        order_desc: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        搜索学生（支持分页和多种筛选条件）
        
        Args:
            keyword: 姓名关键词（模糊搜索）
            class_name: 班级名称筛选
            major: 专业名称筛选
            min_score: 最低成绩
            max_score: 最高成绩
            order_by: 排序字段
            order_desc: 是否降序
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            Tuple[List[Dict], int]: (学生列表, 总记录数)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建WHERE子句
                conditions = []
                params = []
                
                if keyword:
                    conditions.append('name LIKE ?')
                    params.append(f'%{keyword}%')
                
                if class_name:
                    conditions.append('class_name = ?')
                    params.append(class_name)
                
                if major:
                    conditions.append('major = ?')
                    params.append(major)
                
                conditions.append('score >= ?')
                params.append(min_score)
                
                conditions.append('score <= ?')
                params.append(max_score)
                
                where_clause = ' AND '.join(conditions) if conditions else '1=1'
                
                # 获取总记录数
                count_sql = f'SELECT COUNT(*) FROM students WHERE {where_clause}'
                cursor.execute(count_sql, params)
                total_count = cursor.fetchone()[0]
                
                # 验证排序字段
                allowed_order_fields = ['student_id', 'name', 'age', 'class_name', 
                                       'major', 'score', 'enrollment_date']
                if order_by not in allowed_order_fields:
                    order_by = 'student_id'
                
                order_direction = 'DESC' if order_desc else 'ASC'
                
                # 查询数据
                query_sql = f'''
                    SELECT student_id, name, gender, age, class_name, 
                           major, enrollment_date, score
                    FROM students 
                    WHERE {where_clause}
                    ORDER BY {order_by} {order_direction}
                    LIMIT ? OFFSET ?
                '''
                cursor.execute(query_sql, params + [limit, offset])
                
                rows = cursor.fetchall()
                students = [dict(row) for row in rows]
                
                return students, total_count
                
        except Exception as e:
            print(f"搜索学生失败: {str(e)}")
            return [], 0
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """
        获取所有学生（用于数据统计）
        
        Returns:
            List[Dict]: 所有学生信息列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT student_id, name, gender, age, class_name, 
                           major, enrollment_date, score
                    FROM students
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取所有学生失败: {str(e)}")
            return []
    
    # ==================== 统计查询 ====================
    
    def get_class_statistics(self) -> List[Dict[str, Any]]:
        """
        获取班级人数统计
        
        Returns:
            List[Dict]: 各班级人数统计
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT class_name, COUNT(*) as count
                    FROM students
                    GROUP BY class_name
                    ORDER BY class_name
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取班级统计失败: {str(e)}")
            return []
    
    def get_major_statistics(self) -> List[Dict[str, Any]]:
        """
        获取各专业平均成绩统计
        
        Returns:
            List[Dict]: 各专业平均成绩
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT major, 
                           COUNT(*) as student_count,
                           AVG(score) as avg_score,
                           MIN(score) as min_score,
                           MAX(score) as max_score
                    FROM students
                    GROUP BY major
                    ORDER BY avg_score DESC
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取专业统计失败: {str(e)}")
            return []
    
    def get_score_distribution(self, bins: int = 10) -> List[Dict[str, Any]]:
        """
        获取成绩分布统计
        
        Args:
            bins: 分段数量
            
        Returns:
            List[Dict]: 各分数段人数
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 计算每个区间的人数
                bin_size = 100 / bins
                distribution = []
                
                for i in range(bins):
                    min_val = i * bin_size
                    max_val = (i + 1) * bin_size
                    
                    cursor.execute('''
                        SELECT COUNT(*) as count
                        FROM students
                        WHERE score >= ? AND score < ?
                    ''', (min_val, max_val))
                    
                    count = cursor.fetchone()[0]
                    distribution.append({
                        'range': f'{int(min_val)}-{int(max_val)}',
                        'min': min_val,
                        'max': max_val,
                        'count': count
                    })
                
                # 处理满分情况
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM students
                    WHERE score = 100
                ''')
                perfect_count = cursor.fetchone()[0]
                if perfect_count > 0:
                    distribution[-1]['count'] += perfect_count
                
                return distribution
        except Exception as e:
            print(f"获取成绩分布失败: {str(e)}")
            return []
    
    def get_gender_statistics(self) -> List[Dict[str, Any]]:
        """
        获取性别统计
        
        Returns:
            List[Dict]: 男女人数统计
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT gender, COUNT(*) as count
                    FROM students
                    GROUP BY gender
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取性别统计失败: {str(e)}")
            return []
    
    def batch_insert(self, students: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        批量插入学生数据
        
        Args:
            students: 学生数据列表
            
        Returns:
            Tuple[int, int]: (成功数量, 失败数量)
        """
        success_count = 0
        fail_count = 0
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                for student in students:
                    try:
                        cursor.execute('''
                            INSERT INTO students 
                            (student_id, name, gender, age, class_name, major, enrollment_date, score)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            student['student_id'],
                            student['name'],
                            student['gender'],
                            student['age'],
                            student['class_name'],
                            student['major'],
                            student['enrollment_date'],
                            student['score']
                        ))
                        success_count += 1
                    except sqlite3.IntegrityError:
                        fail_count += 1
                        continue
                
                conn.commit()
                return success_count, fail_count
                
        except Exception as e:
            print(f"批量插入失败: {str(e)}")
            return success_count, fail_count
