import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from database import DakaDatabase
from statistics import calculate_average_score, find_most_common_type, get_top_restaurants, calculate_restaurant_average_scores
import datetime
from PIL import Image, ImageTk
import os
import shutil
import sys

class RestaurantDakaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("餐厅打卡系统")
        self.root.geometry("1200x700")  # 增加窗口大小以获得更好的布局
        self.root.resizable(True, True)
        
        # 设置颜色主题
        self.setup_styles()
        
        # 初始化数据库
        self.db = DakaDatabase()
        
        # 创建图片存储目录
        self.image_dir = "restaurant_images"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        
        # 设置应用图标（可选）
        try:
            self.root.iconbitmap("restaurant_icon.ico")
        except:
            pass
        
        # 创建主框架 - 使用网格布局
        self.setup_layout()
        
        # 加载数据
        self.load_records()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """设置自定义样式"""
        self.style = ttk.Style()
        
        # 主色调
        primary_color = "#4a6fa5"  # 蓝色调
        secondary_color = "#f0f0f0"  # 浅灰色
        accent_color = "#e67e22"  # 橙色调
        
        # 配置各种控件样式
        self.style.configure("TFrame", background=secondary_color)
        self.style.configure("TLabel", background=secondary_color, font=('Microsoft YaHei UI', 10))
        self.style.configure("TLabelframe", background=secondary_color)
        self.style.configure("TLabelframe.Label", font=('Microsoft YaHei UI', 10, 'bold'))
        
        # 按钮样式
        self.style.configure("TButton", 
                            background=primary_color, 
                            foreground="white",
                            font=('Microsoft YaHei UI', 10),
                            padding=6)
        
        # 鼠标悬停效果
        self.style.map("TButton",
                      background=[('active', accent_color)],
                      foreground=[('active', 'white')])
        
        # 表格样式
        self.style.configure("Treeview", 
                            font=('Microsoft YaHei UI', 10),
                            rowheight=25)
        self.style.configure("Treeview.Heading", 
                            font=('Microsoft YaHei UI', 10, 'bold'),
                            background=primary_color,
                            foreground="white")
        
        # 标题样式
        self.style.configure("Title.TLabel", 
                            font=('Microsoft YaHei UI', 16, 'bold'),
                            foreground=primary_color)
        
        # 强调按钮样式
        self.style.configure("Accent.TButton", 
                            background=accent_color,
                            foreground="white")
        self.style.map("Accent.TButton",
                      background=[('active', primary_color)])
        
        # 统计数据样式
        self.style.configure("Stats.TLabel", 
                            font=('Microsoft YaHei UI', 11, 'bold'),
                            foreground=primary_color)
    
    def setup_layout(self):
        """创建主布局"""
        # 使用网格布局代替堆叠布局
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)  # 表格区域可扩展
        
        # 顶部标题区域
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky="ew")
        
        # 应用标题
        title_label = ttk.Label(title_frame, text="餐厅打卡系统", style="Title.TLabel")
        title_label.pack(side=tk.LEFT, padx=10)
        
        # 创建顶部功能区
        self.create_top_controls(title_frame)
        
        # 中间主内容区域 - 使用PanedWindow分割
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # 左侧记录表格区域
        table_frame = ttk.LabelFrame(main_paned, text="打卡记录", padding="10")
        main_paned.add(table_frame, weight=3)
        
        # 右侧信息面板
        info_frame = ttk.LabelFrame(main_paned, text="数据统计", padding="10")
        main_paned.add(info_frame, weight=1)
        
        # 创建记录表格
        self.create_records_table(table_frame)
        
        # 创建信息面板内容
        self.create_info_panel(info_frame)
        
        # 底部功能区
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=5)
        self.create_bottom_controls(bottom_frame)
    
    def create_top_controls(self, parent):
        """创建顶部控制按钮"""
        # 右侧控制区域
        control_frame = ttk.Frame(parent)
        control_frame.pack(side=tk.RIGHT)
        
        # 搜索框
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.LEFT, padx=10)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20, 
                                font=('Microsoft YaHei UI', 10))
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", self.search_records)
        
        search_btn = ttk.Button(search_frame, text="🔍 搜索", command=self.search_records, width=8)
        search_btn.pack(side=tk.LEFT)
        
        # 添加记录按钮 - 使用强调样式
        add_btn = ttk.Button(control_frame, text="➕ 添加记录", 
                            command=self.add_record, style="Accent.TButton", width=12)
        add_btn.pack(side=tk.LEFT, padx=5)
    
    def create_records_table(self, parent):
        """创建记录表格"""
        # 表格容器需要可扩展
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 创建表格和滚动条的框架
        table_container = ttk.Frame(parent)
        table_container.grid(row=0, column=0, sticky="nsew")
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        # 创建表格
        columns = ("id", "name", "type", "date", "score", "comment", "has_image")
        self.records_table = ttk.Treeview(
            table_container, 
            columns=columns, 
            show="headings",
            selectmode="browse"
        )
        
        # 设置列标题
        self.records_table.heading("id", text="ID", anchor=tk.W)
        self.records_table.heading("name", text="餐厅名称", anchor=tk.W)
        self.records_table.heading("type", text="类型", anchor=tk.W)
        self.records_table.heading("date", text="日期", anchor=tk.W)
        self.records_table.heading("score", text="评分", anchor=tk.W)
        self.records_table.heading("comment", text="短评", anchor=tk.W)
        self.records_table.heading("has_image", text="图片", anchor=tk.CENTER)
        
        # 设置列宽度
        self.records_table.column("id", width=50, minwidth=50, anchor=tk.W)
        self.records_table.column("name", width=150, minwidth=150, anchor=tk.W)
        self.records_table.column("type", width=100, minwidth=100, anchor=tk.W)
        self.records_table.column("date", width=100, minwidth=100, anchor=tk.W)
        self.records_table.column("score", width=80, minwidth=80, anchor=tk.W)
        self.records_table.column("comment", width=300, minwidth=300, anchor=tk.W)
        self.records_table.column("has_image", width=60, minwidth=60, anchor=tk.CENTER)
        
        # 添加垂直滚动条
        y_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.records_table.yview)
        self.records_table.configure(yscroll=y_scrollbar.set)
        
        # 添加水平滚动条
        x_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.records_table.xview)
        self.records_table.configure(xscroll=x_scrollbar.set)
        
        # 使用网格布局放置表格和滚动条
        self.records_table.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 绑定双击事件查看详情
        self.records_table.bind("<Double-1>", self.show_record_details)
        
        # 表格下方的操作按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # 删除记录按钮
        delete_btn = ttk.Button(btn_frame, text="🗑️ 删除记录", command=self.delete_record, width=12)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = ttk.Button(btn_frame, text="🔄 刷新", command=self.load_records, width=10)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_info_panel(self, parent):
        """创建右侧信息面板"""
        # 统计信息区域
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # 总记录数
        ttk.Label(stats_frame, text="总记录数:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.total_records_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.total_records_var, style="Stats.TLabel").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 最爱类型
        ttk.Label(stats_frame, text="最爱类型:", font=('Microsoft YaHei UI', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fav_type_var = tk.StringVar(value="无记录")
        ttk.Label(stats_frame, textvariable=self.fav_type_var, style="Stats.TLabel").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 分隔线
        separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=10)
        
        # 餐厅评分列表
        restaurant_frame = ttk.LabelFrame(parent, text="餐厅评分")
        restaurant_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建餐厅评分列表
        self.restaurant_list = ttk.Treeview(
            restaurant_frame, 
            columns=("name", "score"),
            show="headings",
            height=8
        )
        
        # 设置列标题
        self.restaurant_list.heading("name", text="餐厅名称")
        self.restaurant_list.heading("score", text="平均评分")
        
        # 设置列宽度
        self.restaurant_list.column("name", width=120)
        self.restaurant_list.column("score", width=80, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(restaurant_frame, orient=tk.VERTICAL, command=self.restaurant_list.yview)
        self.restaurant_list.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.restaurant_list.pack(fill=tk.BOTH, expand=True)
        
        # 分隔线
        separator2 = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator2.pack(fill=tk.X, pady=10)
        
        # 快速筛选区域
        filter_frame = ttk.LabelFrame(parent, text="快速筛选")
        filter_frame.pack(fill=tk.X, pady=10)
        
        # 类型筛选
        ttk.Button(filter_frame, text="按类型筛选", command=self.filter_records, width=15).pack(pady=5)
        
        # 评分排序
        ttk.Button(filter_frame, text="评分排序", command=self.sort_records, width=15).pack(pady=5)
        
        # 详细统计按钮
        stats_btn = ttk.Button(parent, text="📊 详细统计", command=self.show_statistics, 
                              style="Accent.TButton", width=15)
        stats_btn.pack(pady=10)
    
    def create_bottom_controls(self, parent):
        """创建底部状态栏"""
        # 状态信息
        status_label = ttk.Label(parent, text="就绪", font=('Microsoft YaHei UI', 9))
        status_label.pack(side=tk.LEFT)
        
        # 版本信息
        version_label = ttk.Label(parent, text="v1.0", font=('Microsoft YaHei UI', 9))
        version_label.pack(side=tk.RIGHT)
    
    def load_records(self):
        """加载所有记录到表格"""
        # 清空表格
        for item in self.records_table.get_children():
            self.records_table.delete(item)
        
        # 从数据库获取记录
        records = self.db.get_all_records()
        
        # 添加到表格
        for record in records:
            # 检查是否有图片
            has_image = "✓" if record[6] else ""
            values = list(record[:6]) + [has_image]
            self.records_table.insert("", tk.END, values=values)
        
        # 更新统计信息
        self.update_statistics()
    
    def update_statistics(self):
        """更新统计数据"""
        records = self.db.get_all_records()
        
        if records:
            # 更新最爱类型
            fav_type = find_most_common_type(records)
            self.fav_type_var.set(fav_type)
            self.total_records_var.set(f"{len(records)}")
            
            # 更新餐厅评分列表
            # 清空列表
            for item in self.restaurant_list.get_children():
                self.restaurant_list.delete(item)
            
            # 获取每个餐厅的平均评分
            restaurant_scores = calculate_restaurant_average_scores(records)
            
            # 添加到列表
            for name, score in restaurant_scores:
                self.restaurant_list.insert("", tk.END, values=(name, f"{score:.1f}"))
        else:
            self.fav_type_var.set("无记录")
            self.total_records_var.set("0")
            
            # 清空餐厅评分列表
            for item in self.restaurant_list.get_children():
                self.restaurant_list.delete(item)
    
    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择餐厅图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif"), ("所有文件", "*.*")]
        )
        return file_path if file_path else None
    
    def add_record(self):
        """打开添加记录对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新记录")
        dialog.geometry("550x600")  # 增加对话框大小以适应图片预览
        dialog.transient(self.root)  # 设为父窗口的临时窗口
        dialog.grab_set()  # 模式对话框
        
        # 设置对话框样式
        dialog.configure(background="#f0f0f0")
        
        # 标题
        title_frame = ttk.Frame(dialog)
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(title_frame, text="添加新餐厅记录", style="Title.TLabel").pack()
        
        # 表单框架
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用网格布局
        form_frame.columnconfigure(1, weight=1)
        
        # 餐厅名称
        ttk.Label(form_frame, text="餐厅名称:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30, font=('Microsoft YaHei UI', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.EW)
        name_entry.focus()
        
        # 餐厅类型
        ttk.Label(form_frame, text="餐厅类型:").grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, width=27, font=('Microsoft YaHei UI', 10))
        type_combo['values'] = ('火锅', '川菜', '粤菜', '湘菜', '鲁菜', '西餐', '日料', '韩餐', '快餐', '小吃', '其他')
        type_combo.grid(row=1, column=1, padx=5, pady=10, sticky=tk.EW)
        
        # 打卡日期
        ttk.Label(form_frame, text="打卡日期:").grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)
        today = datetime.date.today().strftime("%Y-%m-%d")
        date_var = tk.StringVar(value=today)
        date_entry = ttk.Entry(form_frame, textvariable=date_var, width=30, font=('Microsoft YaHei UI', 10))
        date_entry.grid(row=2, column=1, padx=5, pady=10, sticky=tk.EW)
        
        # 评分
        ttk.Label(form_frame, text="评分 (0-10):").grid(row=3, column=0, padx=5, pady=10, sticky=tk.W)
        score_var = tk.DoubleVar(value=8.0)
        
        score_frame = ttk.Frame(form_frame)
        score_frame.grid(row=3, column=1, padx=5, pady=10, sticky=tk.EW)
        
        score_scale = ttk.Scale(score_frame, from_=0, to=10, variable=score_var, length=300)
        score_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
         # 原代码
        score_value = ttk.Label(score_frame, textvariable=score_var, width=3, 
                       font=('Microsoft YaHei UI', 10, 'bold'))

        # 修改后的代码
        score_display_var = tk.StringVar()
        score_display_var.set(f"{score_var.get():.1f}")  # 初始化为一位小数格式

        def update_score_display(*args):
            """更新评分显示为一位小数"""
            score_display_var.set(f"{score_var.get():.1f}")

        score_var.trace_add("write", update_score_display)  # 监听评分值变化

        score_value = ttk.Label(score_frame, textvariable=score_display_var, width=3, 
                       font=('Microsoft YaHei UI', 10, 'bold'))
        score_value.pack(side=tk.LEFT, padx=5)
        
        # 短评
        ttk.Label(form_frame, text="短评:").grid(row=4, column=0, padx=5, pady=10, sticky=tk.NW)
        comment_entry = tk.Text(form_frame, width=30, height=4, font=('Microsoft YaHei UI', 10))
        comment_entry.grid(row=4, column=1, padx=5, pady=10, sticky=tk.EW)
        
        # 图片上传区域
        ttk.Label(form_frame, text="餐厅图片:").grid(row=5, column=0, padx=5, pady=10, sticky=tk.NW)
        
        image_frame = ttk.Frame(form_frame)
        image_frame.grid(row=5, column=1, padx=5, pady=10, sticky=tk.EW)
        
        # 图片预览标签
        image_preview = ttk.Label(image_frame)
        image_preview.pack(pady=5)
        
        # 存储选择的图片路径
        selected_image_path = [None]  # 使用列表存储，便于在内部函数中修改
        
        # 图片预览
        def update_preview(file_path):
            if file_path and os.path.exists(file_path):
                try:
                    # 加载图片并调整大小
                    img = Image.open(file_path)
                    img.thumbnail((200, 200))  # 调整预览大小
                    photo = ImageTk.PhotoImage(img)
                    
                    # 更新预览
                    image_preview.configure(image=photo)
                    image_preview.image = photo  # 保持引用以防止垃圾回收
                except Exception as e:
                    print(f"无法加载图片: {e}")
        
        # 选择图片按钮
        def browse_image():
            file_path = self.select_image()
            if file_path:
                selected_image_path[0] = file_path
                update_preview(file_path)
                select_btn.configure(text="更换图片")
        
        select_btn = ttk.Button(image_frame, text="选择图片", command=browse_image)
        select_btn.pack(pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        def submit():
            """提交表单"""
            name = name_var.get().strip()
            type_ = type_var.get().strip()
            date = date_var.get().strip()
            score = score_var.get()
            comment = comment_entry.get("1.0", tk.END).strip()
            image_path = selected_image_path[0]
            
            if not name:
                messagebox.showerror("错误", "餐厅名称不能为空")
                return
            
            if not type_:
                messagebox.showerror("错误", "请选择餐厅类型")
                return
            
            # 验证日期格式
            try:
                datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("错误", "日期格式应为 YYYY-MM-DD")
                return
            
            # 处理图片
            saved_image_path = None
            if image_path:
                # 创建唯一的文件名
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                file_ext = os.path.splitext(image_path)[1]
                new_filename = f"{name}_{timestamp}{file_ext}"
                saved_image_path = os.path.join(self.image_dir, new_filename)
                
                # 复制图片到应用目录
                try:
                    shutil.copy2(image_path, saved_image_path)
                except Exception as e:
                    messagebox.showerror("错误", f"保存图片失败: {e}")
                    saved_image_path = None
            
            # 添加记录到数据库
            if self.db.add_record(name, type_, date, score, comment, saved_image_path):
                self.load_records()
                dialog.destroy()
                messagebox.showinfo("成功", "记录添加成功！")
            else:
                # 如果添加失败，删除已复制的图片
                if saved_image_path and os.path.exists(saved_image_path):
                    try:
                        os.remove(saved_image_path)
                    except:
                        pass
                messagebox.showerror("错误", "添加记录失败")
        
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="提交", command=submit, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
    
    def delete_record(self):
        """删除选中的记录"""
        selected = self.records_table.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的记录")
            return
        
        record_id = self.records_table.item(selected[0], "values")[0]
        record_name = self.records_table.item(selected[0], "values")[1]
        
        confirm = messagebox.askyesno("确认删除", f"确定要删除记录: {record_name} (ID: {record_id}) 吗?")
        if confirm:
            # 获取完整记录以便删除图片
            records = self.db.get_all_records()
            for record in records:
                if str(record[0]) == record_id and record[6]:  # 如果有图片
                    try:
                        if os.path.exists(record[6]):
                            os.remove(record[6])
                    except Exception as e:
                        print(f"删除图片失败: {e}")
            
            if self.db.delete_record(record_id):
                self.load_records()
                messagebox.showinfo("成功", "记录删除成功！")
            else:
                messagebox.showerror("错误", "删除记录失败")
    
    def search_records(self, event=None):
        """搜索记录"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.load_records()
            return
        
        # 清空表格
        for item in self.records_table.get_children():
            self.records_table.delete(item)
        
        # 从数据库搜索记录
        records = self.db.search_by_name(keyword)
        
        # 添加到表格
        for record in records:
            # 检查是否有图片
            has_image = "✓" if record[6] else ""
            values = list(record[:6]) + [has_image]
            self.records_table.insert("", tk.END, values=values)
        
        # 更新标题
        if records:
            messagebox.showinfo("搜索结果", f"找到 {len(records)} 条匹配记录")
        else:
            messagebox.showinfo("搜索结果", "没有找到匹配记录")
    
    def sort_records(self):
        """按评分排序记录"""
        # 清空表格
        for item in self.records_table.get_children():
            self.records_table.delete(item)
        
        # 从数据库获取排序后的记录
        records = self.db.get_records_sorted_by_score(descending=True)
        
        # 添加到表格
        for record in records:
            # 检查是否有图片
            has_image = "✓" if record[6] else ""
            values = list(record[:6]) + [has_image]
            self.records_table.insert("", tk.END, values=values)
        
        messagebox.showinfo("排序", "已按评分从高到低排序")
    
    def filter_records(self):
        """按类型筛选记录"""
        # 获取所有存在的类型
        records = self.db.get_all_records()
        types = sorted(set(record[2] for record in records))
        
        if not types:
            messagebox.showinfo("提示", "没有记录可供筛选")
            return
        
        # 创建筛选对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("按类型筛选")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="选择类型:").pack(pady=10)
        
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=types, state="readonly")
        type_combo.pack(pady=5)
        type_combo.current(0)
        
        def apply_filter():
            """应用筛选"""
            type_ = type_var.get()
            if not type_:
                return
            
            # 清空表格
            for item in self.records_table.get_children():
                self.records_table.delete(item)
            
            # 从数据库获取筛选后的记录
            records = self.db.filter_by_type(type_)
            
            # 添加到表格
            for record in records:
                # 检查是否有图片
                has_image = "✓" if record[6] else ""
                values = list(record[:6]) + [has_image]
                self.records_table.insert("", tk.END, values=values)
            
            dialog.destroy()
            messagebox.showinfo("筛选结果", f"找到 {len(records)} 条 {type_} 类型的记录")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="应用", command=apply_filter).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def show_statistics(self):
        """显示详细统计信息"""
        records = self.db.get_all_records()
        
        if not records:
            messagebox.showinfo("统计", "没有记录可供统计")
            return
        
        # 创建统计窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("详细统计")
        dialog.geometry("600x500")
        
        # 创建选项卡控件
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 总体统计选项卡
        overall_tab = ttk.Frame(notebook)
        notebook.add(overall_tab, text="总体统计")
        
        # 计算类型分布
        type_count = {}
        for record in records:
            type_ = record[2]
            type_count[type_] = type_count.get(type_, 0) + 1
        
        # 总体统计信息框架
        stats_frame = ttk.LabelFrame(overall_tab, text="统计信息", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_frame, text=f"总记录数: {len(records)}").pack(anchor=tk.W, pady=5)
        ttk.Label(stats_frame, text=f"最常打卡的类型: {find_most_common_type(records)}").pack(anchor=tk.W, pady=5)
        
        # 餐厅评分框架
        restaurant_frame = ttk.LabelFrame(overall_tab, text="餐厅评分", padding="10")
        restaurant_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建表格显示餐厅评分
        columns = ("rank", "name", "score")
        restaurant_table = ttk.Treeview(restaurant_frame, columns=columns, show="headings")
        
        restaurant_table.heading("rank", text="排名")
        restaurant_table.heading("name", text="餐厅名称")
        restaurant_table.heading("score", text="平均评分")
        
        restaurant_table.column("rank", width=80, anchor=tk.CENTER)
        restaurant_table.column("name", width=200)
        restaurant_table.column("score", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(restaurant_frame, orient=tk.VERTICAL, command=restaurant_table.yview)
        restaurant_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        restaurant_table.pack(fill=tk.BOTH, expand=True)
        
        # 获取每个餐厅的平均评分
        restaurant_scores = calculate_restaurant_average_scores(records)
        
        # 添加数据到表格
        for i, (name, score) in enumerate(restaurant_scores, 1):
            restaurant_table.insert("", tk.END, values=(i, name, f"{score:.1f}"))
        
        # 类型分布框架
        type_frame = ttk.LabelFrame(overall_tab, text="类型分布", padding="10")
        type_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建表格显示类型分布
        columns = ("type", "count", "percentage", "avg_score")
        type_table = ttk.Treeview(type_frame, columns=columns, show="headings")
        
        type_table.heading("type", text="类型")
        type_table.heading("count", text="数量")
        type_table.heading("percentage", text="占比")
        type_table.heading("avg_score", text="平均评分")
        
        type_table.column("type", width=150)
        type_table.column("count", width=80, anchor=tk.CENTER)
        type_table.column("percentage", width=80, anchor=tk.CENTER)
        type_table.column("avg_score", width=80, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(type_frame, orient=tk.VERTICAL, command=type_table.yview)
        type_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        type_table.pack(fill=tk.BOTH, expand=True)
        
        # 添加数据到表格
        for type_, count in type_count.items():
            percentage = (count / len(records)) * 100
            type_avg = calculate_average_score(records, type_=type_)
            type_table.insert("", tk.END, values=(type_, count, f"{percentage:.1f}%", f"{type_avg:.1f}"))
        
        # 高分餐厅选项卡 - 这部分可以删除，因为我们已经有了餐厅评分列表
        # 但为了保持一致性，我们保留它
        top_tab = ttk.Frame(notebook)
        notebook.add(top_tab, text="高分餐厅")
        
        # 获取评分最高的餐厅
        top_restaurants = get_top_restaurants(records, limit=10)
        
        # 创建表格显示高分餐厅
        top_frame = ttk.LabelFrame(top_tab, text="评分最高的餐厅", padding="10")
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("rank", "name", "score")
        top_table = ttk.Treeview(top_frame, columns=columns, show="headings")
        
        top_table.heading("rank", text="排名")
        top_table.heading("name", text="餐厅名称")
        top_table.heading("score", text="平均评分")
        
        top_table.column("rank", width=80, anchor=tk.CENTER)
        top_table.column("name", width=200)
        top_table.column("score", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=top_table.yview)
        top_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        top_table.pack(fill=tk.BOTH, expand=True)
        
        # 添加数据到表格
        for i, (name, score) in enumerate(top_restaurants, 1):
            top_table.insert("", tk.END, values=(i, name, f"{score:.1f}"))
            
        # 自定义统计选项卡
        custom_tab = ttk.Frame(notebook)
        notebook.add(custom_tab, text="自定义统计")
        
        # 自定义统计框架
        custom_frame = ttk.LabelFrame(custom_tab, text="按条件筛选", padding="10")
        custom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建筛选选项
        filter_frame = ttk.Frame(custom_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        # 餐厅类型筛选
        ttk.Label(filter_frame, text="餐厅类型:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(filter_frame, textvariable=type_var, width=15)
        type_combo['values'] = ["全部"] + sorted(type_count.keys())
        type_combo.current(0)
        type_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 结果显示区域 - 使用表格代替文本框
        result_frame = ttk.LabelFrame(custom_frame, text="餐厅评分列表", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("rank", "name", "type", "score")
        result_table = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        result_table.heading("rank", text="排名")
        result_table.heading("name", text="餐厅名称")
        result_table.heading("type", text="类型")
        result_table.heading("score", text="平均评分")
        
        result_table.column("rank", width=60, anchor=tk.CENTER)
        result_table.column("name", width=150)
        result_table.column("type", width=100)
        result_table.column("score", width=80, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_table.yview)
        result_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_table.pack(fill=tk.BOTH, expand=True)
        
        # 初始加载所有餐厅
        for i, (name, score) in enumerate(restaurant_scores, 1):
            # 查找餐厅类型
            restaurant_type = ""
            for record in records:
                if record[1] == name:
                    restaurant_type = record[2]
                    break
            result_table.insert("", tk.END, values=(i, name, restaurant_type, f"{score:.1f}"))
        
        # 筛选函数
        def filter_by_type():
            # 清空表格
            for item in result_table.get_children():
                result_table.delete(item)
            
            selected_type = type_var.get()
            
            # 筛选记录
            filtered_records = records
            if selected_type != "全部":
                filtered_records = [r for r in filtered_records if r[2] == selected_type]
            
            # 计算筛选后的餐厅评分
            if filtered_records:
                restaurant_scores = calculate_restaurant_average_scores(filtered_records)
                
                # 添加到表格
                for i, (name, score) in enumerate(restaurant_scores, 1):
                    # 查找餐厅类型
                    restaurant_type = ""
                    for record in filtered_records:
                        if record[1] == name:
                            restaurant_type = record[2]
                            break
                    result_table.insert("", tk.END, values=(i, name, restaurant_type, f"{score:.1f}"))
            
        # 筛选按钮
        filter_btn = ttk.Button(filter_frame, text="应用筛选", command=filter_by_type)
        filter_btn.grid(row=0, column=2, padx=10, pady=5)
    
    def show_record_details(self, event):
        """显示选中记录的详细信息"""
        selected = self.records_table.selection()
        if not selected:
            return
        
        # 获取选中记录的ID
        record_id = self.records_table.item(selected[0], "values")[0]
        
        # 从数据库获取完整记录（包括图片路径）
        records = self.db.get_all_records()
        record = None
        for r in records:
            if str(r[0]) == record_id:
                record = r
                break
        
        if not record:
            return
        
        # 创建详情窗口
        dialog = tk.Toplevel(self.root)
        dialog.title(f"记录详情 - {record[1]}")
        dialog.geometry("600x500")
        
        # 创建滚动区域
        main_canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 详情框架
        detail_frame = ttk.Frame(scrollable_frame, padding="20")
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示详细信息
        details = [
            ("ID", record[0]),
            ("餐厅名称", record[1]),
            ("类型", record[2]),
            ("日期", record[3]),
            ("评分", record[4]),
            ("短评", record[5])
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(detail_frame, text=label + ":", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            # 对于短评，使用文本框显示
            if label == "短评" and value:
                text_widget = tk.Text(detail_frame, height=4, width=40, wrap=tk.WORD)
                text_widget.grid(row=i, column=1, sticky=tk.W, pady=5)
                text_widget.insert(tk.END, value)
                text_widget.config(state=tk.DISABLED)
            else:
                ttk.Label(detail_frame, text=str(value)).grid(row=i, column=1, sticky=tk.W, pady=5)
        
        # 显示图片（如果有）
        image_path = record[6]
        if image_path and os.path.exists(image_path):
            ttk.Label(detail_frame, text="餐厅图片:", font=("Arial", 10, "bold")).grid(row=len(details), column=0, sticky=tk.NW, pady=5)
            
            try:
                # 加载图片
                img = Image.open(image_path)
                
                # 调整图片大小
                img.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(img)
                
                # 显示图片
                image_label = ttk.Label(detail_frame, image=photo)
                image_label.grid(row=len(details), column=1, sticky=tk.W, pady=5)
                image_label.image = photo  # 保持引用以防止垃圾回收
            except Exception as e:
                ttk.Label(detail_frame, text=f"无法加载图片: {e}").grid(row=len(details), column=1, sticky=tk.W, pady=5)
    
    def on_closing(self):
        """关闭窗口时的处理"""
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    # 设置应用主题
    style = ttk.Style()
    try:
        # 尝试使用更现代的主题
        style.theme_use('clam')  # 可选值: 'clam', 'alt', 'default', 'classic'
    except:
        pass
    app = RestaurantDakaGUI(root)
    root.mainloop()
