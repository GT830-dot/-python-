"""
学生管理系统使用手册PDF生成器

使用ReportLab生成PDF格式的使用手册
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def create_manual_pdf(filename="学生管理系统使用手册.pdf"):
    """生成PDF使用手册"""
    
    # 注册中文字体
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
        chinese_font = 'SimSun'
        chinese_font_bold = 'SimHei'
    except:
        # 如果找不到中文字体，使用默认字体
        chinese_font = 'Helvetica'
        chinese_font_bold = 'Helvetica-Bold'
    
    # 创建文档
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 创建样式
    styles = getSampleStyleSheet()
    
    # 标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=chinese_font_bold,
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # 副标题样式
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=50,
        alignment=TA_CENTER
    )
    
    # 章节标题样式
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontName=chinese_font_bold,
        fontSize=18,
        textColor=colors.HexColor('#2980b9'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # 小节标题样式
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=chinese_font_bold,
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    # 正文样式
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=11,
        leading=20,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    # 列表样式
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=11,
        leading=18,
        leftIndent=20,
        spaceAfter=6
    )
    
    # 构建文档内容
    story = []
    
    # ========== 封面 ==========
    story.append(Spacer(1, 100))
    story.append(Paragraph("学生管理系统", title_style))
    story.append(Paragraph("使用手册", title_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("版本 1.0.0", subtitle_style))
    story.append(Paragraph("基于 Python + Tkinter 开发", subtitle_style))
    story.append(Spacer(1, 100))
    story.append(Paragraph("© 2024 学生管理系统开发团队", subtitle_style))
    story.append(PageBreak())
    
    # ========== 目录 ==========
    story.append(Paragraph("目录", heading1_style))
    story.append(Spacer(1, 20))
    
    toc_items = [
        ("1. 系统概述", ".................... 3"),
        ("2. 系统安装与启动", ".................... 4"),
        ("3. 主界面介绍", ".................... 5"),
        ("4. 学生管理功能", ".................... 6"),
        ("5. 数据筛选与查询", ".................... 8"),
        ("6. 统计图表功能", ".................... 10"),
        ("7. 常见问题解答", ".................... 12"),
    ]
    
    for item, page in toc_items:
        story.append(Paragraph(f"{item} {page}", body_style))
    
    story.append(PageBreak())
    
    # ========== 1. 系统概述 ==========
    story.append(Paragraph("1. 系统概述", heading1_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "学生管理系统是一款基于 Python 和 Tkinter 开发的桌面应用程序，采用现代化的 VS Code 暗色主题设计。"
        "系统提供了学生信息的增删改查、数据分页展示、统计图表可视化等功能，适用于学校、培训机构等教育场景。",
        body_style
    ))
    
    story.append(Paragraph("主要功能特性：", heading2_style))
    features = [
        "✓ 学生信息管理：添加、编辑、删除学生信息",
        "✓ 数据分页展示：支持大数据量的分页显示",
        "✓ 多条件筛选：按班级、专业、成绩范围筛选",
        "✓ 实时搜索：支持按姓名关键词搜索",
        "✓ 统计图表：成绩分布可视化展示",
        "✓ 数据持久化：SQLite 数据库存储",
        "✓ 暗色主题：现代化 UI 设计"
    ]
    for feature in features:
        story.append(Paragraph(feature, list_style))
    
    story.append(PageBreak())
    
    # ========== 2. 系统安装与启动 ==========
    story.append(Paragraph("2. 系统安装与启动", heading1_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("2.1 环境要求", heading2_style))
    requirements = [
        "• Python 3.8 或更高版本",
        "• 操作系统：Windows 10/11、macOS、Linux",
        "• 内存：至少 4GB RAM",
        "• 硬盘空间：至少 100MB 可用空间"
    ]
    for req in requirements:
        story.append(Paragraph(req, list_style))
    
    story.append(Paragraph("2.2 安装步骤", heading2_style))
    steps = [
        "1. 解压系统压缩包到目标目录",
        "2. 确保已安装 Python 3.8+",
        "3. 安装依赖库：pip install reportlab",
        "4. 运行主程序：python main.py"
    ]
    for step in steps:
        story.append(Paragraph(step, list_style))
    
    story.append(Paragraph("2.3 启动系统", heading2_style))
    story.append(Paragraph(
        "双击运行 main.py 文件，或在命令行中执行 'python main.py'。"
        "系统启动后会自动最大化窗口，并加载学生数据。首次启动时，系统会自动生成示例数据。",
        body_style
    ))
    
    story.append(PageBreak())
    
    # ========== 3. 主界面介绍 ==========
    story.append(Paragraph("3. 主界面介绍", heading1_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "系统主界面采用三栏式布局，从左到右依次为：筛选面板、数据表格、统计图表。"
        "顶部工具栏提供常用操作按钮。",
        body_style
    ))
    
    story.append(Paragraph("3.1 顶部工具栏", heading2_style))
    toolbar_items = [
        "• 搜索框：输入学生姓名关键词进行搜索",
        "• 添加按钮：打开对话框添加新学生",
        "• 删除按钮：删除选中的学生记录",
        "• 刷新按钮：重新加载数据",
        "• 生成数据按钮：生成示例测试数据"
    ]
    for item in toolbar_items:
        story.append(Paragraph(item, list_style))
    
    story.append(Paragraph("3.2 左侧筛选面板", heading2_style))
    filter_items = [
        "• 班级筛选：选择特定班级查看学生",
        "• 专业筛选：按专业过滤学生列表",
        "• 成绩范围：拖动滑块设置最低和最高成绩",
        "• 重置筛选：一键清除所有筛选条件",
        "• 统计信息：显示当前筛选结果的统计数据"
    ]
    for item in filter_items:
        story.append(Paragraph(item, list_style))
    
    story.append(Paragraph("3.3 中央数据表格", heading2_style))
    story.append(Paragraph(
        "表格显示学生的详细信息，包括学号、姓名、性别、年龄、班级、专业和成绩。"
        "点击表头可按该列排序，双击行可编辑学生信息，单击行可选中记录。",
        body_style
    ))
    
    story.append(Paragraph("3.4 右侧统计图表", heading2_style))
    story.append(Paragraph(
        "图表区域显示成绩分布的柱状图，包括优秀、良好、中等、及格、不及格五个等级的人数统计。"
        "图表会随筛选条件实时更新。",
        body_style
    ))
    
    story.append(PageBreak())
    
    # ========== 4. 学生管理功能 ==========
    story.append(Paragraph("4. 学生管理功能", heading1_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("4.1 添加学生", heading2_style))
    add_steps = [
        '1. 点击顶部工具栏的"添加"按钮',
        "2. 在弹出的对话框中填写学生信息",
        "3. 学号格式：年份+班级代码+序号（如 202401001）",
        "4. 选择班级后，专业会自动匹配",
        "5. 成绩范围：0-100 分",
        '6. 点击"保存"按钮完成添加'
    ]
    for step in add_steps:
        story.append(Paragraph(step, list_style))
    
    story.append(Paragraph("4.2 编辑学生", heading2_style))
    edit_steps = [
        "1. 在数据表格中双击要编辑的学生行",
        "2. 或先单击选中行，然后点击编辑按钮",
        "3. 在对话框中修改相关信息",
        '4. 点击"保存"按钮保存修改'
    ]
    for step in edit_steps:
        story.append(Paragraph(step, list_style))
    
    story.append(Paragraph("4.3 删除学生", heading2_style))
    delete_steps = [
        "1. 在数据表格中单击选中要删除的学生",
        '2. 点击顶部工具栏的"删除"按钮',
        '3. 在确认对话框中点击"确定"',
        "4. 系统会提示删除成功或失败"
    ]
    for step in delete_steps:
        story.append(Paragraph(step, list_style))
    
    story.append(Paragraph("4.4 数据验证规则", heading2_style))
    validation_rules = [
        "• 学号：必填，格式为 202401001（10位数字）",
        "• 姓名：必填，2-20 个字符",
        "• 性别：必填，选择男或女",
        "• 年龄：必填，范围 15-50 岁",
        "• 班级：必填，从下拉列表选择",
        "• 成绩：必填，范围 0-100 分"
    ]
    for rule in validation_rules:
        story.append(Paragraph(rule, list_style))
    
    story.append(PageBreak())
    
    # ========== 5. 数据筛选与查询 ==========
    story.append(Paragraph("5. 数据筛选与查询", heading1_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("5.1 关键词搜索", heading2_style))
    story.append(Paragraph(
        "在顶部工具栏的搜索框中输入学生姓名关键词，按回车键或等待自动搜索。"
        '系统会实时显示匹配的学生列表。输入"*"可显示所有学生。',
        body_style
    ))
    
    story.append(Paragraph("5.2 班级筛选", heading2_style))
    story.append(Paragraph(
        '在左侧筛选面板的"班级"下拉框中选择特定班级，表格会立即显示该班级的学生。'
        '选择"全部"可显示所有班级的学生。',
        body_style
    ))
    
    story.append(Paragraph("5.3 专业筛选", heading2_style))
    story.append(Paragraph(
        '在"专业"下拉框中选择专业进行筛选。系统支持以下专业：',
        body_style
    ))
    majors = [
        "• 计算机科学与技术",
        "• 软件工程",
        "• 人工智能"
    ]
    for major in majors:
        story.append(Paragraph(major, list_style))
    
    story.append(Paragraph("5.4 成绩范围筛选", heading2_style))
    story.append(Paragraph(
        '拖动"最低分"和"最高分"滑块设置成绩范围。'
        "表格会实时更新，只显示成绩在范围内的学生。"
        "滑块旁边的数字标签显示当前设置的分数值。",
        body_style
    ))
    
    story.append(Paragraph("5.5 组合筛选", heading2_style))
    story.append(Paragraph(
        "可以同时使用多种筛选条件进行组合筛选。"
        '例如：选择"计算机一班"+ 设置成绩范围 80-100，'
        "即可查看计算机一班成绩在 80-100 分之间的学生。",
        body_style
    ))
    
    story.append(Paragraph("5.6 重置筛选", heading2_style))
    story.append(Paragraph(
        '点击筛选面板底部的"重置筛选"按钮，可一键清除所有筛选条件，'
        "恢复显示所有学生数据。此操作会重置：",
        body_style
    ))
    reset_items = [
        "• 搜索关键词",
        '• 班级选择（恢复为"全部"）',
        '• 专业选择（恢复为"全部"）',
        "• 成绩范围（恢复为 0-100）",
        "• 页码（恢复为第 1 页）"
    ]
    for item in reset_items:
        story.append(Paragraph(item, list_style))
    
    story.append(PageBreak())
    
    # ========== 6. 统计图表功能 ==========
    story.append(Paragraph("6. 统计图表功能", heading1_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("6.1 成绩分布图表", heading2_style))
    story.append(Paragraph(
        "右侧图表区域显示当前筛选结果的成绩分布柱状图。"
        "图表将成绩分为五个等级：",
        body_style
    ))
    score_levels = [
        "• 优秀：90-100 分",
        "• 良好：80-89 分",
        "• 中等：70-79 分",
        "• 及格：60-69 分",
        "• 不及格：0-59 分"
    ]
    for level in score_levels:
        story.append(Paragraph(level, list_style))
    
    story.append(Paragraph("6.2 实时更新", heading2_style))
    story.append(Paragraph(
        "图表会随筛选条件的变化实时更新。"
        "当应用新的筛选条件后，图表会立即反映当前数据的成绩分布情况。",
        body_style
    ))
    
    story.append(Paragraph("6.3 统计数据", heading2_style))
    story.append(Paragraph(
        "筛选面板底部的统计信息区域显示以下数据：",
        body_style
    ))
    stats_items = [
        "• 总人数：当前显示的学生总数",
        "• 平均分：当前学生的平均成绩",
        "• 最高分：当前学生的最高成绩",
        "• 最低分：当前学生的最低成绩",
        "• 及格率：成绩≥60分的学生占比"
    ]
    for item in stats_items:
        story.append(Paragraph(item, list_style))
    
    story.append(PageBreak())
    
    # ========== 7. 常见问题解答 ==========
    story.append(Paragraph("7. 常见问题解答", heading1_style))
    story.append(Spacer(1, 10))
    
    faqs = [
        ("Q1: 系统启动失败怎么办？",
         "A: 请检查：1) Python 版本是否为 3.8+；2) 是否安装了所有依赖库；3) 数据库文件是否有写入权限。"),
        
        ("Q2: 如何备份学生数据？",
         "A: 系统使用 SQLite 数据库，直接备份项目目录下的 students.db 文件即可。"),
        
        ("Q3: 可以导入 Excel 数据吗？",
         "A: 当前版本暂不支持 Excel 导入，后续版本会添加此功能。目前可通过生成数据功能添加测试数据。"),
        
        ("Q4: 专业名称显示不完整怎么办？",
         "A: 表格列宽已优化，如仍有问题可调整窗口大小或使用筛选功能查看特定专业。"),
        
        ("Q5: 如何修改班级和专业列表？",
         "A: 编辑 utils.py 文件中的 CLASS_LIST 和 MAJOR_LIST 变量，重启系统后生效。"),
        
        ("Q6: 系统支持多用户吗？",
         "A: 当前版本为单机版，不支持多用户同时访问。建议每个用户使用独立的数据库文件。"),
        
        ("Q7: 数据量大时系统卡顿怎么办？",
         "A: 系统已优化分页功能，每页显示 20 条记录。如仍卡顿，可减少每页显示数量或升级硬件配置。"),
        
        ("Q8: 如何导出学生数据？",
         "A: 当前版本支持数据库文件备份。导出功能将在后续版本中添加。")
    ]
    
    for q, a in faqs:
        story.append(Paragraph(q, heading2_style))
        story.append(Paragraph(a, body_style))
        story.append(Spacer(1, 5))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("---", subtitle_style))
    story.append(Paragraph("感谢您使用学生管理系统！", subtitle_style))
    story.append(Paragraph("如有问题或建议，请联系开发团队。", subtitle_style))
    
    # 生成PDF
    doc.build(story)
    print(f"使用手册已生成: {filename}")
    return filename


if __name__ == '__main__':
    create_manual_pdf()
