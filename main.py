import tkinter as tk
from tkinter import messagebox, ttk
import datetime

# Import from packages
from db import db  # Import the singleton database instance
from db.db_setup import setup_database
from db.models import *

from core.services import TrainService, StationService, SalespersonService
from core.train_management import TrainManagementInterface
from core.ticket_search import TicketSearchInterface
from core.order_management import OrderManagementInterface
from core.route_viewer import RouteViewerInterface
from core.staff_management import StaffManagementInterface
from core.login_manager import LoginManager

from utils.gui_utils import GUIUtils

class MainApplication:
    """主应用程序类，负责管理所有界面和模块"""
    
    def __init__(self):
        """初始化主应用程序"""
        self.main_window = tk.Tk()
        self.main_window.withdraw()  # 初始隐藏
        
        self.main_window.title("Train Station Management System")
        self.main_window.geometry("375x450")
          # Use the singleton database connection from db package
        self.db = db
        
        # 初始化GUI工具类
        self.utils = GUIUtils(self.main_window)
        
        # 初始化登录管理器
        self.login_manager = LoginManager(self.main_window, self.utils)
        
        # 初始化各个界面模块
        self.ticket_search = TicketSearchInterface(
            self.main_window, self.utils, self.display_table, self.show_main_menu_frame
        )
        
        self.order_management = OrderManagementInterface(
            self.main_window, self.utils, self.display_table, self.show_main_menu_frame
        )
        
        self.route_viewer = RouteViewerInterface(
            self.main_window, self.utils, self.display_table, self.show_main_menu_frame
        )
        
        self.staff_management = StaffManagementInterface(
            self.main_window, self.utils, self.display_table, self.show_main_menu_frame
        )
        
        # 创建列车管理接口的工具函数字典
        train_mgmt_utils = {
            'create_modal_window': self.utils.create_modal_window,
            'show_message': self.utils.show_message,
            'show_error': self.utils.show_error,
            'show_confirmation': self.utils.show_confirmation,
            'clear_frame': self.utils.clear_frame,
            'validate_date': self.utils.validate_date,
            'show_main_menu': self.show_main_menu_frame
        }
        
        self.train_management = TrainManagementInterface(self.main_window, train_mgmt_utils)
        
    def run(self):
        """运行应用程序"""
        # 初始化数据库
        # print("Initializing database setup...")
        # if setup_database():
        #     print("Database initialized successfully!")
        # else:
        #     self.utils.show_error("Database Setup Failed", 
        #                       "Could not set up the database. Check your MySQL connection and permissions.")
        #     self.main_window.destroy()
        #     return

        # 显示登录界面
        self.login_manager.show_login_frame(self.show_main_menu_frame)
        
        # 窗口居中显示
        self.utils.center_window(self.main_window)
        self.main_window.deiconify()
        
        # 设置关闭窗口的处理
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.main_window.mainloop()
        
        # 关闭数据库连接
        db.close()
    
    def on_closing(self):
        """窗口关闭处理"""
        db.close()  # 关闭数据库连接
        self.main_window.destroy()
    
    def show_main_menu_frame(self):
        """显示主菜单界面"""
        self.utils.clear_frame(self.main_window)
        self.main_window.title("Train Station Management System")

        # 显示当前登录用户信息
        user_info = ""
        if self.login_manager.is_logged_in():
            user = self.login_manager.get_current_user()
            if self.login_manager.is_staff_user():
                user_info = f"Staff: {user['salesperson_name']} ({user['role']})"
            else:
                user_info = f"Customer: {user['name']}"
        
        user_frame = tk.Frame(self.main_window)
        user_frame.pack(fill=tk.X, pady=5)
        
        if user_info:
            tk.Label(user_frame, text=user_info, font=("Arial", 10, "italic")).pack(side=tk.LEFT, padx=10)
            tk.Button(user_frame, text="Log Out", command=self.handle_logout).pack(side=tk.RIGHT, padx=10)
        else:
            tk.Button(user_frame, text="Log In", command=lambda: self.login_manager.show_login_frame(self.show_main_menu_frame)).pack(side=tk.RIGHT, padx=10)

        tk.Label(self.main_window, text="Station Management Menu", font=("Arial", 16)).pack(pady=10)

        # 添加功能按钮
        tk.Button(self.main_window, text="Search Trains", 
               command=self.ticket_search.show_search_trains_frame, width=30).pack(pady=5)

        tk.Button(self.main_window, text="View Train Route", 
               command=self.route_viewer.show_train_route_frame, width=30).pack(pady=5)

        tk.Button(self.main_window, text="View Train Information", 
               command=lambda: self.display_table(
                   TrainService.list_all_trains,
                   ["Train No", "Type", "Seats", "Departure", "Arrival"],
                   window_size="500x400"
               ), width=30).pack(pady=5)
               
        # 添加新按钮：查看列车时刻表
        tk.Button(self.main_window, text="View Train Schedules", 
               command=lambda: self.display_table(
                   TrainService.get_train_schedules,
                   ["Train No", "Type", "Departure", "Arrival", "Stopover", 
                   "Stop Order", "Seats", "Arrival Time", "Departure Time"],
                   window_size="1200x500"
               ), width=30).pack(pady=5)

        tk.Button(self.main_window, text="View Station Information", 
               command=lambda: self.display_table(
                   StationService.list_all_stations,
                   ["ID", "Name", "Code"],
                   window_size="300x600"
               ), width=30).pack(pady=5)
        
        # 只有登录后才显示的功能
        if self.login_manager.is_logged_in():
            if self.login_manager.is_staff_user():
                # 工作人员特有功能
                tk.Button(self.main_window, text="Staff Operations", 
                       command=lambda: self.staff_management.show_staff_dashboard(self.login_manager.get_current_user()), 
                       width=30).pack(pady=5)
                
                # 只有管理员才能访问的列车管理功能
                if self.login_manager.get_current_user()['role'] == 'Manager':
                    tk.Button(self.main_window, text="Train Management", 
                           command=lambda: self.train_management.show_train_management(self.login_manager.get_current_user()), 
                           width=30).pack(pady=5)
            else:
                # 顾客特有功能
                tk.Button(self.main_window, text="Query My Orders", 
                       command=lambda: self.order_management.show_order_query(
                           self.login_manager.get_current_user()['name'],
                           self.login_manager.get_current_user()['id_card']
                       ), 
                       width=30).pack(pady=5)

        tk.Button(self.main_window, text="Exit", command=self.main_window.quit, width=30).pack(pady=5)
    
    def handle_logout(self):
        """处理登出操作"""
        self.login_manager.logout()
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")
        self.show_main_menu_frame()
    
    def display_table(self, get_data_func, columns, enable_booking=False, is_order_view=False, 
         is_staff_view=False, staff_info=None, window_size="800x400"):
        """显示数据表格窗口

        参数:
            get_data_func: 获取数据的函数
            columns: 表格列名列表
            enable_booking: 是否启用订票功能
            is_order_view: 是否为订单视图
            is_staff_view: 是否为员工视图
            staff_info: 员工信息
            window_size: 窗口大小，格式为"宽x高"，如"800x400"
        """
        data_window = self.utils.create_modal_window(
            "Data View",
            window_size
        )
        
        # 创建Treeview
        tree = ttk.Treeview(data_window)
        tree["columns"] = columns
        tree["show"] = "headings"

        # 配置列
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # 添加滚动条
        vsb = ttk.Scrollbar(data_window, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(data_window, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # 放置组件
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # 配置网格权重
        data_window.grid_rowconfigure(0, weight=1)
        data_window.grid_columnconfigure(0, weight=1)
        
        # 跟踪鼠标单击的单元格位置
        selected_cell = {"item": None, "column": None}
        
        def on_cell_click(event):
            # 获取单击的行和列
            item = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            
            # 如果单击了有效的行和列
            if item and column:
                # 转换列索引为整数（格式为#1, #2等）
                col_idx = int(column.replace('#', '')) - 1
                if col_idx >= 0 and col_idx < len(columns):
                    selected_cell["item"] = item
                    selected_cell["column"] = col_idx
                    
                    # 显示选中的单元格
                    tree.selection_set(item)
                    
                    # 更新状态标签
                    if "values" in tree.item(item):
                        values = tree.item(item)["values"]
                        if values and col_idx < len(values):
                            status_label.config(text=f"Selected cell: {columns[col_idx]} = {values[col_idx]}")
        
        # 绑定单击事件
        tree.bind("<ButtonRelease-1>", on_cell_click)

        # 添加右键菜单，用于复制
        context_menu = tk.Menu(tree, tearoff=0)
        
        def copy_cell():
            if selected_cell["item"] and selected_cell["column"] is not None:
                item = selected_cell["item"]
                col_idx = selected_cell["column"]
                values = tree.item(item)["values"]
                if col_idx < len(values):
                    cell_value = values[col_idx]
                    data_window.clipboard_clear()
                    data_window.clipboard_append(str(cell_value))
    
        def copy_selected_row():
            selected_items = tree.selection()
            if not selected_items:
                return
            item = selected_items[0]
            values = tree.item(item)['values']
            row_text = "\t".join([str(val) for val in values])
            data_window.clipboard_clear()
            data_window.clipboard_append(row_text)
    
        def copy_all():
            items = tree.get_children()
            if not items:
                return
            
            all_rows = []
            # 添加表头
            header_row = "\t".join(columns)
            all_rows.append(header_row)
            
            # 添加数据行
            for item in items:
                values = tree.item(item)['values']
                row_text = "\t".join([str(val) for val in values])
                all_rows.append(row_text)
            
            # 复制到剪贴板
            data_window.clipboard_clear()
            data_window.clipboard_append("\n".join(all_rows))
    
        # 添加菜单项
        context_menu.add_command(label="Copy Cell", command=copy_cell)
        context_menu.add_command(label="Copy Row", command=copy_selected_row)
        context_menu.add_command(label="Copy All Data", command=copy_all)
        
        # 绑定右键点击事件
        tree.bind("<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root))

        # 添加状态栏显示当前选中的单元格
        status_label = tk.Label(data_window, text="Right-click to copy cell content", anchor="w")
        status_label.grid(row=2, column=0, sticky="ew", pady=2, padx=5)

        try:
            data, error = get_data_func()
            
            if error:
                messagebox.showinfo("Information", error)
            
            if data:
                for row in data:
                    tree.insert("", "end", values=[str(item) if item is not None else "-" for item in row])
                    
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        # 订票功能
        if enable_booking:
            selected_train_info = None
            
            def on_select(event):
                nonlocal selected_train_info
                selected_items = tree.selection()
                if not selected_items:
                    return
                item = selected_items[0]
                selected_train_info = tree.item(item)['values']

            def on_book():
                if not selected_train_info:
                    messagebox.showwarning("Warning", "Please select a train first")
                    return
                self.ticket_search.create_booking_window(selected_train_info,    
                        self.login_manager.get_current_user()['name'],
                        self.login_manager.get_current_user()['id_card']
                        )
            
            tree.bind('<<TreeviewSelect>>', on_select)
            
            booking_frame = tk.Frame(data_window)
            booking_frame.grid(row=2, column=0, pady=5)
            
            tk.Label(booking_frame, text="Select a train and click Book to proceed", 
                font=("Arial", 10, "italic")).pack(side=tk.LEFT, padx=5)
            tk.Button(booking_frame, text="Book Selected Train", 
                command=on_book).pack(side=tk.LEFT, padx=5)

        # 订单操作功能
        if is_order_view:
            def on_select(event):
                selected_items = tree.selection()
                if not selected_items:
                    return
                item = selected_items[0]
                values = tree.item(item)['values']
                order_status = values[-1]  # status是最后一列
                cancel_btn['state'] = 'normal' if order_status == 'Ready' else 'disabled'
                refund_btn['state'] = 'normal' if order_status == 'Success' else 'disabled'

            def refresh_orders():
                tree.delete(*tree.get_children())
                data, _ = get_data_func()
                if data:
                    for row in data:
                        tree.insert("", "end", values=[str(item) if item is not None else "-" for item in row])

            def cancel_order():
                selected_items = tree.selection()
                if not selected_items:
                    messagebox.showwarning("Warning", "Please select an order first")
                    return
                item = selected_items[0]
                order_id = tree.item(item)['values'][0]
                self.order_management.cancel_order(order_id, refresh_orders)

            def request_refund():
                selected_items = tree.selection()
                if not selected_items:
                    messagebox.showwarning("Warning", "Please select an order first")
                    return
                item = selected_items[0]
                order_id = tree.item(item)['values'][0]
                self.order_management.request_refund(order_id, refresh_orders)

            tree.bind('<<TreeviewSelect>>', on_select)
            
            action_frame = tk.Frame(data_window)
            action_frame.grid(row=2, column=0, pady=5)
            
            cancel_btn = tk.Button(action_frame, text="Cancel Order", state='disabled', command=cancel_order)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            refund_btn = tk.Button(action_frame, text="Request Refund", state='disabled', command=request_refund)
            refund_btn.pack(side=tk.LEFT, padx=5)

        # 乘务员操作功能
        if is_staff_view:
            def on_select(event):
                selected_items = tree.selection()
                if not selected_items:
                    return
                item = selected_items[0]
                values = tree.item(item)['values']
                status = values[-1]
                approve_btn['state'] = 'normal' if status in ('Ready', 'RefundPending') else 'disabled'
                reject_btn['state'] = 'normal' if status in ('Ready', 'RefundPending') else 'disabled'

            def refresh_orders():
                tree.delete(*tree.get_children())
                data, _ = get_data_func()
                if data:
                    for row in data:
                        tree.insert("", "end", values=[str(item) if item is not None else "-" for item in row])

            def process_order_approve():
                selected_items = tree.selection()
                if not selected_items:
                    messagebox.showwarning("Warning", "Please select an order first")
                    return
                item = selected_items[0]
                order_id = tree.item(item)['values'][0]
                self.staff_management.process_order(
                    order_id, staff_info['salesperson_id'], True, refresh_orders
                )

            def process_order_reject():
                selected_items = tree.selection()
                if not selected_items:
                    messagebox.showwarning("Warning", "Please select an order first")
                    return
                item = selected_items[0]
                order_id = tree.item(item)['values'][0]
                self.staff_management.process_order(
                    order_id, staff_info['salesperson_id'], False, refresh_orders
                )

            tree.bind('<<TreeviewSelect>>', on_select)
            
            action_frame = tk.Frame(data_window)
            action_frame.grid(row=2, column=0, pady=5)
            
            approve_btn = tk.Button(action_frame, text="Approve", state='disabled', command=process_order_approve)
            approve_btn.pack(side=tk.LEFT, padx=5)
            
            reject_btn = tk.Button(action_frame, text="Reject", state='disabled', command=process_order_reject)
            reject_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(data_window, text="Close", command=data_window.destroy).grid(row=3, column=0, pady=5)


# 应用程序入口
if __name__ == "__main__":
    app = MainApplication()
    app.run()