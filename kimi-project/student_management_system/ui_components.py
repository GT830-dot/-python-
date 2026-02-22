"""
自定义UI组件模块

提供学生管理系统所需的各种自定义UI组件，包括样式按钮、对话框、图表框架等。
所有组件都采用VS Code暗色主题风格。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Any, List, Dict
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

from utils import COLORS, FONTS, center_window, validate_student_data


# ==================== 样式配置 ====================

def configure_styles():
    """
    配置ttk全局样式（白色主题）
    """
    style = ttk.Style()
    
    # 配置主题
    style.theme_use('clam')
    
    # 配置Treeview（表格）
    style.configure(
        'Custom.Treeview',
        background=COLORS['bg_secondary'],
        foreground=COLORS['text_primary'],
        fieldbackground=COLORS['bg_secondary'],
        font=FONTS['normal'],
        rowheight=32
    )
    style.configure(
        'Custom.Treeview.Heading',
        background=COLORS['bg_tertiary'],
        foreground=COLORS['accent'],
        font=FONTS['subtitle']
    )
    
    # 配置Combobox
    style.configure(
        'Custom.TCombobox',
        fieldbackground=COLORS['bg_secondary'],
        background=COLORS['bg_secondary'],
        foreground=COLORS['text_primary'],
        arrowcolor=COLORS['accent']
    )
    
    # 配置Entry
    style.configure(
        'Custom.TEntry',
        fieldbackground=COLORS['bg_secondary'],
        foreground=COLORS['text_primary']
    )
    
    # 配置Scale（滑块）
    style.configure(
        'Custom.Horizontal.TScale',
        background=COLORS['bg_secondary'],
        troughcolor=COLORS['border']
    )
    
    # 配置LabelFrame
    style.configure(
        'Custom.TLabelframe',
        background=COLORS['bg_secondary'],
        foreground=COLORS['text_primary']
    )
    style.configure(
        'Custom.TLabelframe.Label',
        background=COLORS['bg_secondary'],
        foreground=COLORS['text_primary'],
        font=FONTS['subtitle']
    )


# ==================== 自定义按钮 ====================

class StyledButton(tk.Canvas):
    """
    自定义样式按钮
    
    带有悬停效果、圆角和图标的现代化按钮。
    """
    
    def __init__(
        self, 
        parent, 
        text: str = '',
        icon: str = '',
        command: Optional[Callable] = None,
        bg_color: str = COLORS['accent'],
        hover_color: str = COLORS['accent_hover'],
        text_color: str = 'white',
        width: int = 100,
        height: int = 32,
        **kwargs
    ):
        """
        初始化样式按钮
        
        Args:
            parent: 父容器
            text: 按钮文本
            icon: 按钮图标（可选）
            command: 点击回调函数
            bg_color: 背景颜色
            hover_color: 悬停颜色
            text_color: 文字颜色
            width: 按钮宽度
            height: 按钮高度
        """
        super().__init__(
            parent, 
            width=width, 
            height=height,
            bg=parent.cget('bg'),
            highlightthickness=0,
            **kwargs
        )
        
        self.text = text
        self.icon = icon
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = bg_color
        
        # 绘制按钮
        self._draw_button()
        
        # 绑定事件
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        # 设置鼠标手型
        self.config(cursor='hand2')
    
    def _draw_button(self):
        """绘制按钮外观"""
        self.delete('all')
        
        # 圆角矩形
        radius = 4
        self.create_rounded_rect(2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2, 
                                 radius, fill=self.current_color, outline='')
        
        # 文字
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        self.create_text(
            self.winfo_reqwidth() // 2,
            self.winfo_reqheight() // 2,
            text=display_text,
            fill=self.text_color,
            font=FONTS['normal']
        )
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        """鼠标进入"""
        self.current_color = self.hover_color
        self._draw_button()
    
    def _on_leave(self, event):
        """鼠标离开"""
        self.current_color = self.bg_color
        self._draw_button()
    
    def _on_click(self, event):
        """鼠标按下"""
        # 稍微变暗的效果
        pass
    
    def _on_release(self, event):
        """鼠标释放"""
        if self.command:
            self.command()
    
    def config_button(self, **kwargs):
        """更新按钮配置"""
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'state' in kwargs:
            state = kwargs['state']
            if state == 'disabled':
                self.unbind('<ButtonRelease-1>')
                self.current_color = COLORS['text_secondary']
            else:
                self.bind('<ButtonRelease-1>', self._on_release)
                self.current_color = self.bg_color
        self._draw_button()


# ==================== Toast 提示 ====================

class ToastNotification:
    """
    Toast提示通知
    
    右下角弹出的自动消失提示框。
    """
    
    def __init__(self, parent, message: str, msg_type: str = 'info', duration: int = 3000):
        """
        初始化Toast通知
        
        Args:
            parent: 父窗口
            message: 提示消息
            msg_type: 消息类型（info/success/warning/error）
            duration: 显示时长（毫秒）
        """
        self.parent = parent
        self.message = message
        self.duration = duration
        
        # 根据类型选择颜色
        color_map = {
            'info': COLORS['accent'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'error': COLORS['error']
        }
        self.bg_color = color_map.get(msg_type, COLORS['accent'])
        
        self._create_window()
    
    def _create_window(self):
        """创建Toast窗口"""
        self.window = tk.Toplevel(self.parent)
        self.window.overrideredirect(True)  # 无边框
        self.window.attributes('-topmost', True)
        
        # 设置窗口大小和位置
        width = 300
        height = 60
        
        # 计算右下角位置
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + parent_width - width - 20
        y = parent_y + parent_height - height - 40
        
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # 创建内容
        frame = tk.Frame(self.window, bg=self.bg_color, padx=15, pady=10)
        frame.pack(fill='both', expand=True)
        
        label = tk.Label(
            frame,
            text=self.message,
            bg=self.bg_color,
            fg='white',
            font=FONTS['normal'],
            wraplength=width - 30
        )
        label.pack(fill='both', expand=True)
        
        # 自动关闭
        self.window.after(self.duration, self.close)
        
        # 渐显效果
        self.window.attributes('-alpha', 0)
        self._fade_in()
    
    def _fade_in(self):
        """渐显动画"""
        alpha = self.window.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.1
            self.window.attributes('-alpha', alpha)
            self.window.after(30, self._fade_in)
    
    def close(self):
        """关闭Toast"""
        if self.window and self.window.winfo_exists():
            self.window.destroy()


def show_toast(parent, message: str, msg_type: str = 'info', duration: int = 3000):
    """
    显示Toast提示
    
    Args:
        parent: 父窗口
        message: 提示消息
        msg_type: 消息类型
        duration: 显示时长
    """
    ToastNotification(parent, message, msg_type, duration)


# ==================== 学生编辑对话框 ====================

class StudentDialog(tk.Toplevel):
    """
    学生信息编辑对话框
    
    用于添加或编辑学生信息的模态对话框。
    """
    
    def __init__(
        self, 
        parent, 
        title: str = '添加学生',
        student_data: Optional[Dict] = None,
        on_save: Optional[Callable[[Dict], None]] = None,
        check_student_id_exists: Optional[Callable[[str], bool]] = None
    ):
        """
        初始化学生编辑对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            student_data: 编辑时的学生数据，None表示添加
            on_save: 保存回调函数
            check_student_id_exists: 检查学号是否存在的回调函数
        """
        super().__init__(parent)
        self.title(title)
        self.student_data = student_data or {}
        self.on_save = on_save
        self.check_student_id_exists = check_student_id_exists
        self.result = None
        
        # 设置为模态对话框
        self.transient(parent)
        self.grab_set()
        
        # 设置大小和位置
        self.geometry('450x550')
        center_window(self, 450, 550)
        
        # 配置背景色
        self.configure(bg=COLORS['bg_secondary'])
        
        # 创建UI
        self._create_ui()
        
        # 如果是编辑模式，填充数据
        if student_data:
            self._fill_data()
        
        # 绑定回车键
        self.bind('<Return>', lambda e: self._on_save())
        self.bind('<Escape>', lambda e: self.destroy())
        
        # 等待窗口关闭
        self.wait_window(self)
    
    def _create_ui(self):
        """创建对话框UI"""
        # 主框架
        main_frame = tk.Frame(self, bg=COLORS['bg_secondary'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text=self.title(),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            font=FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # 表单框架
        form_frame = tk.Frame(main_frame, bg=COLORS['bg_secondary'])
        form_frame.pack(fill='both', expand=True)
        
        # 表单字段
        self.entries = {}
        
        # 学号
        self._create_form_row(form_frame, 0, '学号：', 'student_id', 
                             readonly=bool(self.student_data))
        
        # 姓名
        self._create_form_row(form_frame, 1, '姓名：', 'name')
        
        # 性别
        self._create_combobox_row(form_frame, 2, '性别：', 'gender', 
                                  ['男', '女'])
        
        # 年龄
        self._create_form_row(form_frame, 3, '年龄：', 'age')
        
        # 班级
        from utils import CLASS_LIST
        self._create_combobox_row(form_frame, 4, '班级：', 'class_name', 
                                  CLASS_LIST)
        
        # 专业（只读，根据班级自动设置）
        self._create_form_row(form_frame, 5, '专业：', 'major', readonly=True)
        
        # 入学日期
        self._create_form_row(form_frame, 6, '入学日期：', 'enrollment_date',
                             placeholder='YYYY-MM-DD')
        
        # 成绩
        self._create_form_row(form_frame, 7, '成绩：', 'score')
        
        # 班级选择事件
        self.entries['class_name'].bind('<<ComboboxSelected>>', self._on_class_change)
        
        # 按钮框架
        btn_frame = tk.Frame(main_frame, bg=COLORS['bg_secondary'])
        btn_frame.pack(pady=20)
        
        # 保存按钮
        save_btn = StyledButton(
            btn_frame,
            text='保存',
            bg_color=COLORS['success'],
            hover_color='#3db89f',
            command=self._on_save
        )
        save_btn.pack(side='left', padx=10)
        
        # 取消按钮
        cancel_btn = StyledButton(
            btn_frame,
            text='取消',
            bg_color=COLORS['text_secondary'],
            hover_color='#666666',
            command=self.destroy
        )
        cancel_btn.pack(side='left', padx=10)
    
    def _create_form_row(self, parent, row, label_text, field_name, 
                         readonly=False, placeholder=''):
        """创建表单行"""
        label = tk.Label(
            parent,
            text=label_text,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            font=FONTS['normal'],
            width=10,
            anchor='e'
        )
        label.grid(row=row, column=0, pady=10, sticky='e')
        
        entry = tk.Entry(
            parent,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            font=FONTS['normal'],
            width=25,
            readonlybackground=COLORS['bg_tertiary']
        )
        entry.grid(row=row, column=1, pady=10, padx=10)
        
        if readonly:
            entry.config(state='readonly')
        
        self.entries[field_name] = entry
        
        if placeholder and not readonly:
            entry.insert(0, placeholder)
            entry.config(fg=COLORS['text_secondary'])
            entry.bind('<FocusIn>', lambda e: self._on_entry_focus_in(e, placeholder))
            entry.bind('<FocusOut>', lambda e: self._on_entry_focus_out(e, placeholder))
    
    def _create_combobox_row(self, parent, row, label_text, field_name, values):
        """创建下拉框行"""
        label = tk.Label(
            parent,
            text=label_text,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            font=FONTS['normal'],
            width=10,
            anchor='e'
        )
        label.grid(row=row, column=0, pady=10, sticky='e')
        
        combo = ttk.Combobox(
            parent,
            values=values,
            state='readonly',
            font=FONTS['normal'],
            width=23
        )
        combo.grid(row=row, column=1, pady=10, padx=10)
        
        # 设置样式
        combo.configure(background=COLORS['bg_tertiary'])
        
        self.entries[field_name] = combo
    
    def _on_entry_focus_in(self, event, placeholder):
        """输入框获得焦点"""
        if event.widget.get() == placeholder:
            event.widget.delete(0, 'end')
            event.widget.config(fg=COLORS['text_primary'])
    
    def _on_entry_focus_out(self, event, placeholder):
        """输入框失去焦点"""
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(fg=COLORS['text_secondary'])
    
    def _on_class_change(self, event=None):
        """班级改变时更新专业"""
        class_name = self.entries['class_name'].get()
        if class_name:
            from utils import get_major_by_class
            major = get_major_by_class(class_name)
            self.entries['major'].config(state='normal')
            self.entries['major'].delete(0, 'end')
            self.entries['major'].insert(0, major)
            self.entries['major'].config(state='readonly')
    
    def _fill_data(self):
        """填充编辑数据"""
        for field, entry in self.entries.items():
            if field in self.student_data:
                value = self.student_data[field]
                if isinstance(entry, ttk.Combobox):
                    entry.set(value)
                else:
                    entry.config(state='normal')
                    entry.delete(0, 'end')
                    entry.insert(0, str(value))
                    if entry.cget('readonlybackground'):
                        entry.config(state='readonly')
    
    def _on_save(self):
        """保存按钮回调"""
        # 收集数据
        data = {}
        for field, entry in self.entries.items():
            if isinstance(entry, ttk.Combobox):
                data[field] = entry.get()
            else:
                value = entry.get()
                # 跳过占位符
                if value in ['YYYY-MM-DD']:
                    value = ''
                data[field] = value
        
        # 类型转换
        try:
            data['age'] = int(data['age'])
            data['score'] = float(data['score'])
        except (ValueError, TypeError):
            messagebox.showwarning('输入错误', '年龄必须是整数，成绩必须是数字', parent=self)
            return
        
        # 验证数据
        valid, msg = validate_student_data(data)
        if not valid:
            messagebox.showwarning('验证失败', msg, parent=self)
            return
        
        # 检查学号唯一性（仅添加时）
        if not self.student_data and self.check_student_id_exists:
            if self.check_student_id_exists(data['student_id']):
                messagebox.showwarning('验证失败', f"学号 {data['student_id']} 已存在", parent=self)
                return
        
        # 保存
        self.result = data
        if self.on_save:
            self.on_save(data)
        self.destroy()


# ==================== 图表框架 ====================

class ChartFrame(tk.Frame):
    """
    图表显示框架
    
    集成matplotlib图表到tkinter界面中。
    """
    
    def __init__(self, parent, **kwargs):
        """
        初始化图表框架
        
        Args:
            parent: 父容器
        """
        super().__init__(parent, bg=COLORS['bg_secondary'], **kwargs)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.figure.patch.set_facecolor(COLORS['bg_secondary'])
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # 当前图表类型
        self.current_chart = None
    
    def clear(self):
        """清除图表"""
        self.figure.clear()
    
    def draw_pie_chart(self, labels, sizes, title='分布图'):
        """
        绘制饼图（白色主题）
        
        Args:
            labels: 标签列表
            sizes: 数值列表
            title: 图表标题
        """
        self.clear()
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_secondary'])
        
        # 颜色方案 - 使用现代配色
        modern_colors = ['#4a90e2', '#27ae60', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
        colors = modern_colors[:len(labels)] if len(labels) <= len(modern_colors) else plt.cm.Set3(range(len(labels)))
        
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': COLORS['text_primary'], 'fontsize': 10},
            wedgeprops={'edgecolor': COLORS['bg_secondary'], 'linewidth': 2}
        )
        
        # 设置标题
        ax.set_title(title, color=COLORS['text_primary'], fontsize=14, fontweight='bold', pad=15)
        
        # 调整布局
        self.figure.tight_layout()
        self.canvas.draw()
        
        self.current_chart = 'pie'
    
    def draw_bar_chart(self, categories, values, title='柱状图', xlabel='', ylabel=''):
        """
        绘制柱状图（白色主题）
        
        Args:
            categories: 类别列表
            values: 数值列表
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
        """
        self.clear()
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_secondary'])
        
        # 绘制柱状图 - 使用渐变色效果
        bars = ax.bar(categories, values, color=COLORS['accent'], edgecolor=COLORS['accent'], linewidth=1.5, alpha=0.8)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom',
                color=COLORS['text_primary'],
                fontsize=9
            )
        
        # 设置标题和标签
        ax.set_title(title, color=COLORS['text_primary'], fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, color=COLORS['text_secondary'], fontsize=11)
        ax.set_ylabel(ylabel, color=COLORS['text_secondary'], fontsize=11)
        
        # 设置刻度颜色
        ax.tick_params(colors=COLORS['text_secondary'])
        ax.spines['bottom'].set_color(COLORS['border'])
        ax.spines['top'].set_color(COLORS['border'])
        ax.spines['left'].set_color(COLORS['border'])
        ax.spines['right'].set_color(COLORS['border'])
        
        # 旋转X轴标签以防重叠
        plt.setp(ax.get_xticklabels(), rotation=15, ha='right')
        
        # 添加网格线
        ax.yaxis.grid(True, linestyle='--', alpha=0.3, color=COLORS['border'])
        ax.set_axisbelow(True)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        self.current_chart = 'bar'
    
    def draw_histogram(self, data, bins=10, title='直方图', xlabel='数值', ylabel='频数'):
        """
        绘制直方图
        
        Args:
            data: 数据列表
            bins: 分段数量
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
        """
        self.clear()
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_secondary'])
        
        # 绘制直方图
        n, bins_edges, patches = ax.hist(
            data, 
            bins=bins, 
            color=COLORS['accent'],
            edgecolor='white',
            linewidth=0.5,
            alpha=0.8
        )
        
        # 设置标题和标签
        ax.set_title(title, color=COLORS['text_primary'], fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, color=COLORS['text_secondary'], fontsize=11)
        ax.set_ylabel(ylabel, color=COLORS['text_secondary'], fontsize=11)
        
        # 设置刻度颜色
        ax.tick_params(colors=COLORS['text_secondary'])
        ax.spines['bottom'].set_color(COLORS['border'])
        ax.spines['top'].set_color(COLORS['border'])
        ax.spines['left'].set_color(COLORS['border'])
        ax.spines['right'].set_color(COLORS['border'])
        
        # 添加网格线
        ax.yaxis.grid(True, linestyle='--', alpha=0.3, color=COLORS['border'])
        ax.set_axisbelow(True)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        self.current_chart = 'histogram'


# ==================== 进度对话框 ====================

class ProgressDialog(tk.Toplevel):
    """
    进度对话框
    
    显示操作进度的模态对话框。
    """
    
    def __init__(self, parent, title='请稍候', message='正在处理...'):
        """
        初始化进度对话框
        
        Args:
            parent: 父窗口
            title: 标题
            message: 提示消息
        """
        super().__init__(parent)
        self.title(title)
        
        # 设置为模态
        self.transient(parent)
        self.grab_set()
        
        # 禁止关闭
        self.protocol('WM_DELETE_WINDOW', lambda: None)
        
        # 设置大小和位置
        self.geometry('400x120')
        center_window(self, 400, 120)
        
        # 配置背景
        self.configure(bg=COLORS['bg_secondary'])
        
        # 创建UI
        self._create_ui(message)
        
        # 强制更新
        self.update()
    
    def _create_ui(self, message):
        """创建UI"""
        frame = tk.Frame(self, bg=COLORS['bg_secondary'], padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        # 消息标签
        self.message_label = tk.Label(
            frame,
            text=message,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            font=FONTS['normal']
        )
        self.message_label.pack(pady=(0, 10))
        
        # 进度条
        self.progress = ttk.Progressbar(
            frame,
            mode='determinate',
            length=350
        )
        self.progress.pack(fill='x')
        
        # 配置进度条样式
        style = ttk.Style()
        style.configure(
            'Horizontal.TProgressbar',
            background=COLORS['accent'],
            troughcolor=COLORS['bg_tertiary']
        )
    
    def update_progress(self, value, maximum=100, message=None):
        """
        更新进度
        
        Args:
            value: 当前值
            maximum: 最大值
            message: 更新的消息（可选）
        """
        percentage = (value / maximum) * 100
        self.progress['value'] = percentage
        
        if message:
            self.message_label.config(text=message)
        
        self.update_idletasks()
    
    def close(self):
        """关闭对话框"""
        self.grab_release()
        self.destroy()


# ==================== 确认对话框 ====================

def confirm_delete(parent, student_name: str, student_id: str) -> bool:
    """
    显示删除确认对话框
    
    Args:
        parent: 父窗口
        student_name: 学生姓名
        student_id: 学生学号
        
    Returns:
        bool: 是否确认删除
    """
    result = messagebox.askyesno(
        '确认删除',
        f'确定要删除学生 "{student_name}"（学号：{student_id}）吗？\n此操作不可撤销！',
        icon='warning',
        parent=parent
    )
    return result
