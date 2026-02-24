import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial
from core.services import SalespersonService
from db import db  # Import the singleton database instance
from utils.hash_utils import hash_password

class LoginManager:
    """登录管理类，处理用户身份验证和会话管理"""
    
    def __init__(self, parent, utils):
        """初始化登录管理器
        
        Args:
            parent: 父窗口对象
            utils: 工具类对象，提供GUI工具函数
        """
        self.parent = parent
        self.utils = utils
        self.current_user = None  # 当前登录用户信息
        self.is_staff = False     # 是否为工作人员
    
    def show_login_frame(self, callback=None):
        """显示登录界面
        
        Args:
            callback: 登录成功后的回调函数
        """
        self.utils.clear_frame(self.parent)
        self.parent.title("Train Ticket System - Login")
        
        # 标题
        tk.Label(self.parent, text="Welcome to Train Ticket System", 
                font=("Arial", 16, "bold")).pack(pady=(20, 10))
        
        # 选择登录类型的框架
        login_type_frame = tk.Frame(self.parent)
        login_type_frame.pack(pady=10)
        
        login_type = tk.StringVar(value="customer")
        
        tk.Radiobutton(login_type_frame, text="Customer", variable=login_type, 
                      value="customer").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(login_type_frame, text="Staff", variable=login_type, 
                      value="staff").pack(side=tk.LEFT, padx=10)
        
        # 用户信息框架
        info_frame = tk.Frame(self.parent)
        info_frame.pack(pady=10)
        
        # 顾客登录字段
        customer_frame = tk.Frame(info_frame)
        
        tk.Label(customer_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(customer_frame, width=25)
        name_entry.insert(0, "张三")
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(customer_frame, text="ID Card:").grid(row=1, column=0, sticky=tk.W, pady=5)
        id_card_entry = tk.Entry(customer_frame, width=25)
        id_card_entry.insert(0, "110101199001011234")
        id_card_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 员工登录字段
        staff_frame = tk.Frame(info_frame)
        
        tk.Label(staff_frame, text="Staff ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        staff_id_entry = tk.Entry(staff_frame, width=25)
        staff_id_entry.insert(0, "SP001")
        staff_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(staff_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = tk.Entry(staff_frame, width=25, show="*")
        password_entry.insert(0, "1")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 默认显示客户登录界面
        customer_frame.pack()
        
        def switch_login_type(*args):
            """切换登录类型的处理函数"""
            if login_type.get() == "customer":
                staff_frame.pack_forget()
                customer_frame.pack()
            else:
                customer_frame.pack_forget()
                staff_frame.pack()
        
        # 绑定切换事件
        login_type.trace("w", switch_login_type)
        
        # 登录按钮
        def on_login():
            if login_type.get() == "customer":
                self._handle_customer_login(
                    name_entry.get(), 
                    id_card_entry.get(), 
                    callback
                )
            else:
                self._handle_staff_login(
                    staff_id_entry.get(), 
                    password_entry.get(), 
                    callback
                )
        
        tk.Button(self.parent, text="Login", width=15, 
                 command=on_login).pack(pady=10)
        
        # 返回按钮
        if callback:
            tk.Button(self.parent, text="Cancel", width=15, 
                     command=callback).pack(pady=5)
    
    def _handle_customer_login(self, name, id_card, callback=None):
        """处理顾客登录
        
        Args:
            name: 顾客姓名
            id_card: 身份证号
            callback: 登录成功后的回调函数
        """
        if not name or not id_card:
            messagebox.showerror("Login Error", "Name and ID Card are required!")
            return
        
        try:
            # 验证用户身份
            query = "SELECT * FROM Customers WHERE name = %s AND id_card = %s"
            customer = db.execute_query(query, (name, id_card), fetch_one=True)
            
            if customer:
                self.current_user = {
                    "name": customer["name"],
                    "id_card": customer["id_card"],
                    "phone": customer["phone"]
                }
                self.is_staff = False
                
                messagebox.showinfo("Login Success", f"Welcome, {name}!")
                if callback:
                    callback()
            else:
                messagebox.showerror("Login Error", "Invalid name or ID card!")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during login: {str(e)}")
    
    def _handle_staff_login(self, staff_id, password, callback=None):
        """处理工作人员登录
        
        Args:
            staff_id: 工作人员ID
            password: 密码
            callback: 登录成功后的回调函数
        """
        if not staff_id or not password:
            messagebox.showerror("Login Error", "Staff ID and password are required!")
            return
        
        # 使用SalespersonService验证凭据
        success, result = SalespersonService.verify_credentials(staff_id, password)
        
        if success:
            self.current_user = {
                "salesperson_id": result["salesperson_id"],
                "salesperson_name": result["salesperson_name"], 
                "role": result["role"]
            }
            self.is_staff = True
            
            messagebox.showinfo("Login Success", f"Welcome, {result['salesperson_name']}!")
            if callback:
                callback()
        else:
            messagebox.showerror("Login Error", "Invalid staff ID or password!")
    
    def logout(self):
        """退出登录"""
        self.current_user = None
        self.is_staff = False
    
    def is_logged_in(self):
        """检查是否已登录
        
        Returns:
            bool: 是否已登录
        """
        return self.current_user is not None
    
    def is_staff_user(self):
        """检查当前用户是否为工作人员
        
        Returns:
            bool: 是否为工作人员
        """
        return self.is_staff
    
    def get_current_user(self):
        """获取当前用户信息
        
        Returns:
            dict: 当前用户信息，未登录时返回None
        """
        return self.current_user