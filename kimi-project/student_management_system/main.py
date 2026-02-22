"""
学生管理系统 - 主程序

基于tkinter的现代化学生信息管理系统，采用VS Code暗色主题风格。
功能包括：学生信息增删改查、数据分页展示、统计图表可视化等。

作者：AI Assistant
版本：1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import threading

# 导入自定义模块
from utils import (
    COLORS, FONTS, CLASS_LIST, MAJOR_LIST,
    center_window, format_score, get_score_color
)
from database import DatabaseManager
from data_generator import generate_sample_data
from ui_components import (
    configure_styles, StyledButton, show_toast,
    StudentDialog, ChartFrame, ProgressDialog, confirm_delete
)


class MainApp(tk.Tk):
    """
    主应用程序类
    
    学生管理系统的主窗口，集成所有功能模块。
    采用现代化的暗色主题设计，支持数据管理、筛选查询和统计可视化。
    """
    
    def __init__(self):
        """初始化主应用程序"""
        super().__init__()
        
        # 窗口基本设置
        self.title('学生管理系统')
        self.configure(bg=COLORS['bg_primary'])
        
        # 设置最小尺寸
        self.minsize(800, 600)
        
        # 默认最大化窗口
        self.state('zoomed')
        
        # 初始化数据库
        self.db = DatabaseManager('students.db')
        if not self.db.init_database():
            messagebox.showerror('错误', '数据库初始化失败，程序无法启动')
            self.destroy()
            return
        
        # 配置全局样式
        configure_styles()
        
        # 分页参数
        self.current_page = 1
        self.page_size = 20
        self.total_records = 0
        
        # 排序参数
        self.sort_column = 'student_id'
        self.sort_desc = False
        
        # 筛选参数
        self.filter_keyword = ''
        self.filter_class = ''
        self.filter_major = ''
        self.filter_min_score = 0
        self.filter_max_score = 100
        
        # 选中的学生
        self.selected_student: Optional[Dict] = None
        
        # 创建UI
        self._create_ui()
        
        # 检查是否需要生成初始数据
        self.after(100, self._check_and_generate_data)
        
        # 加载数据
        self.after(200, self._load_data)
    
    def _create_ui(self):
        """创建用户界面"""
        # 主布局框架
        self.main_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 配置网格权重
        self.main_frame.columnconfigure(1, weight=3)  # 中间表格区域
        self.main_frame.columnconfigure(2, weight=1)  # 右侧图表区域
        self.main_frame.rowconfigure(1, weight=1)
        
        # ========== 顶部工具栏 ==========
        self._create_toolbar()
        
        # ========== 左侧筛选面板 ==========
        self._create_filter_panel()
        
        # ========== 中央数据表格 ==========
        self._create_data_table()
        
        # ========== 右侧统计图表 ==========
        self._create_chart_panel()
        
        # ========== 底部状态栏 ==========
        self._create_statusbar()
    
    def _create_toolbar(self):
        """创建顶部工具栏（白色主题风格）"""
        # 工具栏容器 - 使用圆角效果
        toolbar_container = tk.Frame(self.main_frame, bg=COLORS['bg_primary'])
        toolbar_container.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        
        toolbar = tk.Frame(toolbar_container, bg=COLORS['bg_secondary'], height=60, 
                          highlightbackground=COLORS['border'], highlightthickness=1)
        toolbar.pack(fill='x', padx=10, pady=5)
        toolbar.grid_propagate(False)
        toolbar.pack_propagate(False)
        
        # 左侧区域：标题和搜索
        left_frame = tk.Frame(toolbar, bg=COLORS['bg_secondary'])
        left_frame.pack(side='left', padx=20, pady=10)
        
        # 标题 - 添加图标背景
        title_container = tk.Frame(left_frame, bg=COLORS['accent_light'], padx=10, pady=5)
        title_container.pack(side='left', padx=(0, 20))
        
        title_label = tk.Label(
            title_container,
            text='📚 学生管理系统',
            bg=COLORS['accent_light'],
            fg=COLORS['accent'],
            font=FONTS['title']
        )
        title_label.pack()
        
        # 搜索框 - 美化样式
        search_frame = tk.Frame(left_frame, bg=COLORS['bg_tertiary'], 
                               highlightbackground=COLORS['border'], 
                               highlightthickness=1, padx=5, pady=3)
        search_frame.pack(side='left')
        
        # 搜索图标
        search_icon = tk.Label(
            search_frame,
            text='🔍',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_muted'],
            font=FONTS['normal']
        )
        search_icon.pack(side='left', padx=(5, 0))
        
        self.search_entry = tk.Entry(
            search_frame,
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['accent'],
            font=FONTS['normal'],
            width=25,
            relief='flat',
            highlightthickness=0
        )
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.insert(0, '搜索姓名...')
        self.search_entry.config(fg=COLORS['text_muted'])
        self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
        self.search_entry.bind('<Return>', lambda e: self._on_search())
        
        # 右侧按钮组
        btn_frame = tk.Frame(toolbar, bg=COLORS['bg_secondary'])
        btn_frame.pack(side='right', padx=20, pady=10)
        
        # 添加按钮
        add_btn = StyledButton(
            btn_frame,
            text='添加',
            icon='➕',
            bg_color=COLORS['success'],
            hover_color='#229954',
            command=self._on_add,
            width=85,
            height=36
        )
        add_btn.pack(side='left', padx=5)
        
        # 删除按钮
        self.delete_btn = StyledButton(
            btn_frame,
            text='删除',
            icon='🗑️',
            bg_color=COLORS['error'],
            hover_color='#c0392b',
            command=self._on_delete,
            width=85,
            height=36
        )
        self.delete_btn.pack(side='left', padx=5)
        
        # 刷新按钮
        refresh_btn = StyledButton(
            btn_frame,
            text='刷新',
            icon='🔄',
            bg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            command=self._load_data,
            width=85,
            height=36
        )
        refresh_btn.pack(side='left', padx=5)
        
        # 生成数据按钮
        gen_btn = StyledButton(
            btn_frame,
            text='生成数据',
            icon='📊',
            bg_color=COLORS['warning'],
            hover_color='#d68910',
            command=self._on_generate_data,
            width=95,
            height=36
        )
        gen_btn.pack(side='left', padx=5)
    
    def _create_filter_panel(self):
        """创建左侧筛选面板（带滚动功能）"""
        # 外框容器 - 白色卡片风格
        outer_frame = tk.Frame(
            self.main_frame,
            bg=COLORS['bg_secondary'],
            highlightbackground=COLORS['border'],
            highlightthickness=1
        )
        outer_frame.grid(row=1, column=0, sticky='nsew', padx=(10, 10), pady=(0, 10))
        outer_frame.grid_rowconfigure(1, weight=1)
        outer_frame.grid_columnconfigure(0, weight=1)
        
        # 标题栏
        title_bar = tk.Frame(outer_frame, bg=COLORS['accent'], height=40)
        title_bar.grid(row=0, column=0, columnspan=2, sticky='ew')
        title_bar.grid_propagate(False)
        
        tk.Label(
            title_bar,
            text='🔍 筛选条件',
            bg=COLORS['accent'],
            fg='white',
            font=FONTS['subtitle']
        ).pack(side='left', padx=15, pady=8)
        
        # 创建Canvas和滚动条
        canvas = tk.Canvas(outer_frame, bg=COLORS['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        
        # 创建内容框架
        filter_frame = tk.Frame(canvas, bg=COLORS['bg_secondary'], padx=15, pady=15)
        
        # 配置Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=1, column=0, sticky='nsew')
        scrollbar.grid(row=1, column=1, sticky='ns')
        
        # 在Canvas中创建窗口
        canvas_window = canvas.create_window((0, 0), window=filter_frame, anchor='nw', width=210)
        
        # 绑定事件以更新滚动区域
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        filter_frame.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        
        # 鼠标滚轮滚动
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        
        canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        # 保存引用以便后续使用
        self.filter_canvas = canvas
        
        # ===== 筛选内容 =====
        
        # 班级筛选 - 卡片样式
        class_card = tk.Frame(filter_frame, bg=COLORS['bg_tertiary'], padx=12, pady=12,
                             highlightbackground=COLORS['border'], highlightthickness=1)
        class_card.pack(fill='x', pady=(0, 12))
        
        tk.Label(
            class_card,
            text='📁 班级',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['accent'],
            font=FONTS['small']
        ).pack(anchor='w', pady=(0, 8))
        
        self.class_combo = ttk.Combobox(
            class_card,
            values=['全部'] + CLASS_LIST,
            state='readonly',
            font=FONTS['normal'],
            width=15
        )
        self.class_combo.pack(fill='x')
        self.class_combo.set('全部')
        self.class_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # 专业筛选 - 卡片样式
        major_card = tk.Frame(filter_frame, bg=COLORS['bg_tertiary'], padx=12, pady=12,
                             highlightbackground=COLORS['border'], highlightthickness=1)
        major_card.pack(fill='x', pady=(0, 12))
        
        tk.Label(
            major_card,
            text='🎓 专业',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['accent'],
            font=FONTS['small']
        ).pack(anchor='w', pady=(0, 8))
        
        self.major_combo = ttk.Combobox(
            major_card,
            values=['全部'] + list(set(MAJOR_LIST)),
            state='readonly',
            font=FONTS['normal'],
            width=15
        )
        self.major_combo.pack(fill='x')
        self.major_combo.set('全部')
        self.major_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # 成绩范围 - 卡片样式
        score_card = tk.Frame(filter_frame, bg=COLORS['bg_tertiary'], padx=12, pady=12,
                             highlightbackground=COLORS['border'], highlightthickness=1)
        score_card.pack(fill='x', pady=(0, 12))
        
        tk.Label(
            score_card,
            text='📊 成绩范围',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['accent'],
            font=FONTS['small']
        ).pack(anchor='w', pady=(0, 8))
        
        # 最低成绩
        min_frame = tk.Frame(score_card, bg=COLORS['bg_tertiary'])
        min_frame.pack(fill='x', pady=(0, 10))
        
        min_header = tk.Frame(min_frame, bg=COLORS['bg_tertiary'])
        min_header.pack(fill='x')
        
        tk.Label(
            min_header,
            text='最低分',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary'],
            font=FONTS['small']
        ).pack(side='left')
        
        self.min_score_label = tk.Label(
            min_header,
            text='0',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['accent'],
            font=FONTS['normal'],
            width=3
        )
        self.min_score_label.pack(side='right')
        
        self.min_score_var = tk.IntVar(value=0)
        self.min_score_slider = tk.Scale(
            min_frame,
            from_=0,
            to=100,
            orient='horizontal',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            highlightthickness=0,
            troughcolor=COLORS['border'],
            activebackground=COLORS['accent'],
            variable=self.min_score_var,
            command=self._on_score_change,
            length=150,
            showvalue=False
        )
        self.min_score_slider.pack(fill='x', pady=(5, 0))
        
        # 最高成绩
        max_frame = tk.Frame(score_card, bg=COLORS['bg_tertiary'])
        max_frame.pack(fill='x')
        
        max_header = tk.Frame(max_frame, bg=COLORS['bg_tertiary'])
        max_header.pack(fill='x')
        
        tk.Label(
            max_header,
            text='最高分',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary'],
            font=FONTS['small']
        ).pack(side='left')
        
        self.max_score_label = tk.Label(
            max_header,
            text='100',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['accent'],
            font=FONTS['normal'],
            width=3
        )
        self.max_score_label.pack(side='right')
        
        self.max_score_var = tk.IntVar(value=100)
        self.max_score_slider = tk.Scale(
            max_frame,
            from_=0,
            to=100,
            orient='horizontal',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            highlightthickness=0,
            troughcolor=COLORS['border'],
            activebackground=COLORS['accent'],
            variable=self.max_score_var,
            command=self._on_score_change,
            length=150,
            showvalue=False
        )
        self.max_score_slider.pack(fill='x', pady=(5, 0))
        
        # 重置筛选按钮 - 使用更醒目的样式
        reset_btn = StyledButton(
            filter_frame,
            text='重置筛选',
            icon='↺',
            bg_color=COLORS['text_muted'],
            hover_color='#7f8c8d',
            width=120,
            command=self._reset_filters
        )
        reset_btn.pack(pady=15)
        
        # 统计信息区域
        stats_section = tk.LabelFrame(
            filter_frame,
            text=' 统计信息 ',
            bg=COLORS['bg_secondary'],
            fg=COLORS['success'],
            font=FONTS['small'],
            padx=8,
            pady=8
        )
        stats_section.pack(fill='x', pady=(0, 10))
        
        self.filter_stats_label = tk.Label(
            stats_section,
            text='暂无统计数据',
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            font=FONTS['small'],
            justify='left',
            wraplength=180
        )
        self.filter_stats_label.pack(fill='x')
    
    def _create_data_table(self):
        """创建中央数据表格"""
        # 表格框架
        table_frame = tk.Frame(self.main_frame, bg=COLORS['bg_secondary'])
        table_frame.grid(row=1, column=1, sticky='nsew', padx=(0, 10))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Treeview表格
        columns = ('student_id', 'name', 'gender', 'age', 'class_name', 'major', 'score')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            style='Custom.Treeview'
        )
        
        # 定义列
        column_configs = {
            'student_id': ('学号', 100),
            'name': ('姓名', 80),
            'gender': ('性别', 50),
            'age': ('年龄', 50),
            'class_name': ('班级', 120),
            'major': ('专业', 160),
            'score': ('成绩', 60)
        }
        
        for col, (text, width) in column_configs.items():
            self.tree.heading(col, text=text, command=lambda c=col: self._on_sort(c))
            self.tree.column(col, width=width, anchor='center')
        
        # 滚动条
        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # 绑定事件
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Motion>', self._on_mouse_move)
        
        # 行悬停效果
        self.hover_row = None
        
        # 分页控制
        page_frame = tk.Frame(table_frame, bg=COLORS['bg_secondary'])
        page_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.first_btn = StyledButton(
            page_frame,
            text='首页',
            command=lambda: self._go_to_page(1),
            width=60
        )
        self.first_btn.pack(side='left', padx=2)
        
        self.prev_btn = StyledButton(
            page_frame,
            text='上一页',
            command=lambda: self._go_to_page(self.current_page - 1),
            width=70
        )
        self.prev_btn.pack(side='left', padx=2)
        
        self.page_label = tk.Label(
            page_frame,
            text='第 1 页',
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            font=FONTS['normal'],
            width=10
        )
        self.page_label.pack(side='left', padx=10)
        
        self.next_btn = StyledButton(
            page_frame,
            text='下一页',
            command=lambda: self._go_to_page(self.current_page + 1),
            width=70
        )
        self.next_btn.pack(side='left', padx=2)
        
        self.last_btn = StyledButton(
            page_frame,
            text='末页',
            command=self._go_to_last_page,
            width=60
        )
        self.last_btn.pack(side='left', padx=2)
    
    def _create_chart_panel(self):
        """创建右侧统计图表面板（白色主题）"""
        # 外框容器
        chart_container = tk.Frame(
            self.main_frame,
            bg=COLORS['bg_secondary'],
            highlightbackground=COLORS['border'],
            highlightthickness=1
        )
        chart_container.grid(row=1, column=2, sticky='nsew', padx=(0, 10))
        
        # 标题栏
        title_bar = tk.Frame(chart_container, bg=COLORS['success'], height=40)
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)
        
        tk.Label(
            title_bar,
            text='📈 统计图表',
            bg=COLORS['success'],
            fg='white',
            font=FONTS['subtitle']
        ).pack(side='left', padx=15, pady=8)
        
        # 内容区域
        chart_frame = tk.Frame(chart_container, bg=COLORS['bg_secondary'], padx=15, pady=15)
        chart_frame.pack(fill='both', expand=True)
        
        # 图表类型选择 - 使用卡片样式
        chart_type_card = tk.Frame(chart_frame, bg=COLORS['bg_tertiary'], padx=10, pady=10,
                                  highlightbackground=COLORS['border'], highlightthickness=1)
        chart_type_card.pack(fill='x', pady=(0, 15))
        
        self.chart_type_var = tk.StringVar(value='class_pie')
        
        chart_options = [
            ('班级分布', 'class_pie', '🥧'),
            ('成绩分布', 'score_hist', '📊'),
            ('专业成绩', 'major_bar', '📉')
        ]
        
        for text, value, icon in chart_options:
            btn_frame = tk.Frame(chart_type_card, bg=COLORS['bg_tertiary'])
            btn_frame.pack(side='left', padx=5)
            
            tk.Radiobutton(
                btn_frame,
                text=f'{icon} {text}',
                variable=self.chart_type_var,
                value=value,
                bg=COLORS['bg_tertiary'],
                fg=COLORS['text_primary'],
                selectcolor=COLORS['bg_secondary'],
                activebackground=COLORS['bg_tertiary'],
                activeforeground=COLORS['accent'],
                font=FONTS['normal'],
                command=self._update_chart
            ).pack()
        
        # 图表区域 - 添加边框
        chart_area = tk.Frame(chart_frame, bg=COLORS['bg_secondary'],
                             highlightbackground=COLORS['border'],
                             highlightthickness=1)
        chart_area.pack(fill='both', expand=True)
        
        self.chart_frame = ChartFrame(chart_area)
        self.chart_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    def _create_statusbar(self):
        """创建底部状态栏（白色主题）"""
        status_container = tk.Frame(self.main_frame, bg=COLORS['bg_primary'])
        status_container.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(15, 0))
        
        status_frame = tk.Frame(
            status_container,
            bg=COLORS['bg_secondary'],
            height=45,
            highlightbackground=COLORS['border'],
            highlightthickness=1
        )
        status_frame.pack(fill='x', padx=10, pady=5)
        status_frame.grid_propagate(False)
        status_frame.pack_propagate(False)
        
        # 左侧信息区域
        left_info = tk.Frame(status_frame, bg=COLORS['bg_secondary'])
        left_info.pack(side='left', padx=20, pady=8)
        
        # 总记录数 - 带图标
        self.total_label = tk.Label(
            left_info,
            text='📋 总记录: 0',
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            font=FONTS['normal']
        )
        self.total_label.pack(side='left', padx=(0, 20))
        
        # 当前选中 - 带图标
        self.selected_label = tk.Label(
            left_info,
            text='👤 未选中',
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted'],
            font=FONTS['normal']
        )
        self.selected_label.pack(side='left')
        
        # 当前选中
        self.selected_label = tk.Label(
            status_frame,
            text='未选中',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary'],
            font=FONTS['small']
        )
        self.selected_label.pack(side='left', padx=20)
        
        # 操作提示
        self.tip_label = tk.Label(
            status_frame,
            text='提示：双击表格行可编辑学生信息',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['accent'],
            font=FONTS['small']
        )
        self.tip_label.pack(side='right', padx=20)
    
    # ==================== 事件处理 ====================
    
    def _on_search_focus_in(self, event):
        """搜索框获得焦点"""
        if self.search_entry.get() == '搜索姓名...':
            self.search_entry.delete(0, 'end')
            self.search_entry.config(fg=COLORS['text_primary'])
    
    def _on_search_focus_out(self, event):
        """搜索框失去焦点"""
        if not self.search_entry.get():
            self.search_entry.insert(0, '搜索姓名...')
            self.search_entry.config(fg=COLORS['text_secondary'])
    
    def _on_search(self):
        """搜索按钮点击"""
        keyword = self.search_entry.get()
        if keyword == '搜索姓名...':
            keyword = ''
        self.filter_keyword = keyword
        self.current_page = 1
        self._load_data()
    
    def _on_filter_change(self, event=None):
        """筛选条件改变"""
        class_val = self.class_combo.get()
        major_val = self.major_combo.get()
        
        self.filter_class = '' if class_val == '全部' else class_val
        self.filter_major = '' if major_val == '全部' else major_val
        self.current_page = 1
        self._load_data()
    
    def _on_score_change(self, event=None):
        """成绩范围改变"""
        min_score = self.min_score_var.get()
        max_score = self.max_score_var.get()
        
        # 确保最小值不大于最大值
        if min_score > max_score:
            min_score = max_score
            self.min_score_var.set(min_score)
        
        self.min_score_label.config(text=str(min_score))
        self.max_score_label.config(text=str(max_score))
        
        self.filter_min_score = min_score
        self.filter_max_score = max_score
        self.current_page = 1
        self._load_data()
    
    def _reset_filters(self):
        """重置筛选条件"""
        self.filter_keyword = ''
        self.filter_class = ''
        self.filter_major = ''
        self.filter_min_score = 0
        self.filter_max_score = 100
        
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, '搜索姓名...')
        self.search_entry.config(fg=COLORS['text_secondary'])
        
        self.class_combo.set('全部')
        self.major_combo.set('全部')
        
        self.min_score_var.set(0)
        self.max_score_var.set(100)
        self.min_score_label.config(text='0')
        self.max_score_label.config(text='100')
        
        self.current_page = 1
        self._load_data()
    
    def _on_sort(self, column):
        """表头点击排序"""
        if self.sort_column == column:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_column = column
            self.sort_desc = False
        
        # 更新表头显示
        for col in ['student_id', 'name', 'gender', 'age', 'class_name', 'major', 'score']:
            text_map = {
                'student_id': '学号',
                'name': '姓名',
                'gender': '性别',
                'age': '年龄',
                'class_name': '班级',
                'major': '专业',
                'score': '成绩'
            }
            text = text_map.get(col, col)
            if col == self.sort_column:
                text += ' ▼' if self.sort_desc else ' ▲'
            self.tree.heading(col, text=text)
        
        self._load_data()
    
    def _on_select(self, event):
        """表格行选中"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            if values:
                self.selected_student = {
                    'student_id': values[0],
                    'name': values[1],
                    'gender': values[2],
                    'age': values[3],
                    'class_name': values[4],
                    'major': values[5],
                    'score': values[6]
                }
                self.selected_label.config(
                    text=f"选中: {values[1]} ({values[0]})",
                    fg=COLORS['accent']
                )
        else:
            self.selected_student = None
            self.selected_label.config(text='未选中', fg=COLORS['text_secondary'])
    
    def _on_double_click(self, event):
        """表格行双击"""
        if self.selected_student:
            self._on_edit()
    
    def _on_mouse_move(self, event):
        """鼠标移动（行悬停效果）"""
        item = self.tree.identify_row(event.y)
        if item != self.hover_row:
            # 恢复之前行的颜色
            if self.hover_row:
                try:
                    idx = self.tree.index(self.hover_row)
                    tag = 'even' if idx % 2 == 0 else 'odd'
                    self.tree.item(self.hover_row, tags=(tag,))
                except tk.TclError:
                    # 行可能已不存在（如数据刷新后）
                    pass
            
            # 设置新行的颜色
            self.hover_row = item
            if item:
                try:
                    self.tree.item(item, tags=('hover',))
                except tk.TclError:
                    pass
    
    def _go_to_page(self, page):
        """跳转到指定页"""
        max_page = (self.total_records + self.page_size - 1) // self.page_size
        max_page = max(1, max_page)
        
        if page < 1:
            page = 1
        elif page > max_page:
            page = max_page
        
        self.current_page = page
        self._load_data()
    
    def _go_to_last_page(self):
        """跳转到最后一页"""
        max_page = (self.total_records + self.page_size - 1) // self.page_size
        max_page = max(1, max_page)
        self._go_to_page(max_page)
    
    # ==================== 功能操作 ====================
    
    def _check_and_generate_data(self):
        """检查并生成初始数据"""
        if self.db.is_empty():
            self._on_generate_data()
    
    def _on_generate_data(self):
        """生成测试数据"""
        # 显示进度对话框
        progress = ProgressDialog(self, '生成数据', '正在生成测试数据...')
        
        def progress_callback(success, total, message):
            self.after(0, lambda: progress.update_progress(success, total, message))
        
        def do_generate():
            success, failed = generate_sample_data(self.db, 200, progress_callback)
            self.after(0, lambda: self._on_generate_complete(progress, success, failed))
        
        # 在后台线程中执行
        thread = threading.Thread(target=do_generate)
        thread.daemon = True
        thread.start()
    
    def _on_generate_complete(self, progress, success, failed):
        """生成数据完成回调"""
        progress.close()
        self._load_data()
        
        if success > 0:
            show_toast(self, f'成功生成 {success} 条学生数据！', 'success')
        else:
            show_toast(self, '数据生成完成', 'info')
    
    def _load_data(self):
        """加载数据"""
        # 计算偏移量
        offset = (self.current_page - 1) * self.page_size
        
        # 查询数据
        students, total = self.db.search_students(
            keyword=self.filter_keyword,
            class_name=self.filter_class,
            major=self.filter_major,
            min_score=self.filter_min_score,
            max_score=self.filter_max_score,
            order_by=self.sort_column,
            order_desc=self.sort_desc,
            limit=self.page_size,
            offset=offset
        )
        
        self.total_records = total
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 填充数据
        for idx, student in enumerate(students):
            values = (
                student['student_id'],
                student['name'],
                student['gender'],
                student['age'],
                student['class_name'],
                student['major'],
                format_score(student['score'])
            )
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert('', 'end', values=values, tags=(tag,))
        
        # 配置行颜色
        self.tree.tag_configure('odd', background=COLORS['row_odd'])
        self.tree.tag_configure('even', background=COLORS['row_even'])
        self.tree.tag_configure('hover', background=COLORS['row_hover'])
        
        # 更新分页控件
        self._update_pagination()
        
        # 更新状态栏
        self.total_label.config(text=f'总记录: {total}')
        
        # 更新统计
        self._update_stats()
        
        # 更新图表
        self._update_chart()
    
    def _update_pagination(self):
        """更新分页控件"""
        max_page = (self.total_records + self.page_size - 1) // self.page_size
        max_page = max(1, max_page)
        
        self.page_label.config(text=f'第 {self.current_page} / {max_page} 页')
        
        # 更新按钮状态
        if self.current_page <= 1:
            self.first_btn.config_button(state='disabled')
            self.prev_btn.config_button(state='disabled')
        else:
            self.first_btn.config_button(state='normal')
            self.prev_btn.config_button(state='normal')
        
        if self.current_page >= max_page:
            self.next_btn.config_button(state='disabled')
            self.last_btn.config_button(state='disabled')
        else:
            self.next_btn.config_button(state='normal')
            self.last_btn.config_button(state='normal')
    
    def _update_stats(self):
        """更新统计信息"""
        # 获取统计数据
        class_stats = self.db.get_class_statistics()
        major_stats = self.db.get_major_statistics()
        
        # 更新筛选面板统计
        stats_text = f"各班级人数:\n"
        for stat in class_stats:
            stats_text += f"  {stat['class_name']}: {stat['count']}人\n"
        
        stats_text += f"\n各专业平均成绩:\n"
        for stat in major_stats:
            avg = stat.get('avg_score', 0) or 0
            stats_text += f"  {stat['major']}: {avg:.1f}分\n"
        
        self.filter_stats_label.config(text=stats_text)
    
    def _update_chart(self):
        """更新图表"""
        chart_type = self.chart_type_var.get()
        
        if chart_type == 'class_pie':
            # 班级分布饼图
            stats = self.db.get_class_statistics()
            if stats:
                labels = [s['class_name'] for s in stats]
                sizes = [s['count'] for s in stats]
                self.chart_frame.draw_pie_chart(labels, sizes, '班级人数分布')
        
        elif chart_type == 'score_hist':
            # 成绩分布直方图
            students = self.db.get_all_students()
            if students:
                scores = [s['score'] for s in students]
                self.chart_frame.draw_histogram(
                    scores, bins=10, 
                    title='成绩分布直方图',
                    xlabel='成绩',
                    ylabel='人数'
                )
        
        elif chart_type == 'major_bar':
            # 专业平均成绩柱状图
            stats = self.db.get_major_statistics()
            if stats:
                categories = [s['major'] for s in stats]
                values = [s.get('avg_score', 0) or 0 for s in stats]
                self.chart_frame.draw_bar_chart(
                    categories, values,
                    title='各专业平均成绩',
                    xlabel='专业',
                    ylabel='平均成绩'
                )
    
    def _on_add(self):
        """添加学生"""
        dialog = StudentDialog(
            self,
            title='添加学生',
            check_student_id_exists=lambda sid: self.db.get_student(sid) is not None
        )
        
        if dialog.result:
            success, msg = self.db.add_student(dialog.result)
            if success:
                show_toast(self, '学生添加成功！', 'success')
                self._load_data()
            else:
                show_toast(self, f'添加失败: {msg}', 'error')
    
    def _on_edit(self):
        """编辑学生"""
        if not self.selected_student:
            show_toast(self, '请先选择要编辑的学生', 'warning')
            return
        
        # 获取完整数据
        student = self.db.get_student(self.selected_student['student_id'])
        if not student:
            show_toast(self, '学生数据不存在', 'error')
            return
        
        dialog = StudentDialog(
            self,
            title='编辑学生',
            student_data=student
        )
        
        if dialog.result:
            success, msg = self.db.update_student(student['student_id'], dialog.result)
            if success:
                show_toast(self, '学生信息更新成功！', 'success')
                self.selected_student = None
                self.selected_label.config(text='未选中', fg=COLORS['text_secondary'])
                self._load_data()
            else:
                show_toast(self, f'更新失败: {msg}', 'error')
    
    def _on_delete(self):
        """删除学生"""
        if not self.selected_student:
            show_toast(self, '请先选择要删除的学生', 'warning')
            return
        
        # 确认删除
        if confirm_delete(self, self.selected_student['name'], 
                         self.selected_student['student_id']):
            success, msg = self.db.delete_student(self.selected_student['student_id'])
            if success:
                show_toast(self, '学生删除成功！', 'success')
                self.selected_student = None
                self.selected_label.config(text='未选中', fg=COLORS['text_secondary'])
                self._load_data()
            else:
                show_toast(self, f'删除失败: {msg}', 'error')


def main():
    """
    程序入口函数
    """
    app = MainApp()
    app.mainloop()


if __name__ == '__main__':
    main()
