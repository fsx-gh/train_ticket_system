import tkinter as tk
from tkinter import ttk, Label, Entry, Button, Frame, BOTH, LEFT, X
import datetime

from db.models import Salesperson
from core.services import SalespersonService, OrderService

class StaffManagementInterface:
    """员工管理界面类，处理员工登录和操作"""
    
    def __init__(self, parent_window, utils, display_table_func, show_main_menu_func):
        """初始化员工管理界面
        
        Args:
            parent_window: 主窗口
            utils: GUI工具类实例
            display_table_func: 显示表格数据的函数
            show_main_menu_func: 返回主菜单的函数
        """
        self.parent = parent_window
        self.utils = utils
        self.display_table = display_table_func
        self.show_main_menu = show_main_menu_func
    
    def show_staff_login_for_orders(self):
        """显示乘务员登录窗口(订单处理专用)"""
        login_window = self.utils.create_modal_window(
            "Staff Login",
            "300x200"
        )
        
        Label(login_window, text="Staff Login", font=("Arial", 14)).pack(pady=10)
        
        # 乘务员ID输入
        Label(login_window, text="Staff ID:").pack()
        id_entry = Entry(login_window)
        id_entry.insert(0, "SP001")  # 默认值
        id_entry.pack(pady=5)
        
        # 密码输入
        Label(login_window, text="Password:").pack()
        password_entry = Entry(login_window, show="*")
        password_entry.insert(0, "1")  # 默认值
        password_entry.pack(pady=5)
        
        def verify_login():
            staff_id = id_entry.get().strip()
            password = password_entry.get().strip()
            
            if not staff_id or not password:
                self.utils.show_error("Error", "Please fill in all fields")
                return
                
            success, result = SalespersonService.verify_credentials(staff_id, password)
            
            if success:
                login_window.destroy()
                self.show_staff_dashboard(result)  # 传入验证成功的乘务员信息
            else:
                self.utils.show_error("Login Failed", result)
        
        Button(login_window, text="Login", 
            command=verify_login).pack(pady=10)
        Button(login_window, text="Cancel", 
            command=login_window.destroy).pack(pady=5)
    
    def show_staff_login_for_management(self):
        """显示管理员登录窗口(员工管理专用)"""
        login_window = self.utils.create_modal_window(
            "Manager Login",
            "300x200"
        )
        
        Label(login_window, text="Manager Login", font=("Arial", 14)).pack(pady=10)
        
        # 管理员ID输入
        Label(login_window, text="Manager ID:").pack()
        id_entry = Entry(login_window)
        id_entry.insert(0, "SP001")  # 默认值
        id_entry.pack(pady=5)
        
        # 密码输入
        Label(login_window, text="Password:").pack()
        password_entry = Entry(login_window, show="*")
        password_entry.insert(0, "1")  # 默认值
        password_entry.pack(pady=5)
        
        def verify_login():
            staff_id = id_entry.get().strip()
            password = password_entry.get().strip()
            
            if not staff_id or not password:
                self.utils.show_error("Error", "Please fill in all fields")
                return
                
            success, result = SalespersonService.verify_credentials(staff_id, password)
            
            if success and result.get('role') == 'Manager':
                login_window.destroy()
                self.show_staff_management(result)  # 显示员工管理界面，传入管理员信息
            else:
                self.utils.show_error("Login Failed", "Only managers can access this feature")
        
        Button(login_window, text="Login", 
            command=verify_login).pack(pady=10)
        Button(login_window, text="Cancel", 
            command=login_window.destroy).pack(pady=5)
    
    def show_staff_login_for_report(self):
        """显示管理员登录窗口(查看报表专用)"""
        login_window = self.utils.create_modal_window(
            "Manager Login",
            "300x200"
        )
        
        Label(login_window, text="Manager Login", font=("Arial", 14)).pack(pady=10)
        
        # 管理员ID输入
        Label(login_window, text="Manager ID:").pack()
        id_entry = Entry(login_window)
        id_entry.insert(0, "SP001")  # 默认值
        id_entry.pack(pady=5)
        
        # 密码输入
        Label(login_window, text="Password:").pack()
        password_entry = Entry(login_window, show="*")
        password_entry.insert(0, "1")  # 默认值
        password_entry.pack(pady=5)
        
        def verify_login():
            staff_id = id_entry.get().strip()
            password = password_entry.get().strip()
            
            if not staff_id or not password:
                self.utils.show_error("Error", "Please fill in all fields")
                return
                
            success, result = SalespersonService.verify_credentials(staff_id, password)
            
            if success and result.get('role') == 'Manager':
                login_window.destroy()
                self.show_staff_performance_report()  # 直接显示报表
            else:
                self.utils.show_error("Login Failed", "Only managers can access this feature")
        
        Button(login_window, text="Login", 
            command=verify_login).pack(pady=10)
        Button(login_window, text="Cancel", 
            command=login_window.destroy).pack(pady=5)
    
    def show_staff_dashboard(self, staff_info):
        """显示乘务员操作界面"""
        self.utils.clear_frame(self.parent)
        Label(self.parent, text=f"Welcome, {staff_info['salesperson_name']}", 
            font=("Arial", 14)).pack(pady=10)
        
        if staff_info.get('role') == 'Manager':  # 只有管理员可以查看报表和管理员工
            Button(self.parent, text="Staff Performance Report", 
                command=self.show_staff_performance_report, 
                width=30).pack(pady=5)
            
            Button(self.parent, text="Staff Management", 
                command=lambda: self.show_staff_management(staff_info), 
                width=30).pack(pady=5)
        
        Label(self.parent, text="Pending Orders", 
            font=("Arial", 12)).pack(pady=5)
        
        def refresh_orders():
            self.display_table(
                OrderService.get_pending_orders,
                ["Order ID", "Train No", "Type", "From", "To", 
                "Price", "Customer", "Phone", "Operation", 
                "Time", "Status"],
                is_staff_view=True,
                staff_info=staff_info,
                window_size="1200x400",
            )
        
        Button(self.parent, text="View Pending Orders", 
            command=refresh_orders, width=30).pack(pady=5)
        
        Button(self.parent, text="Back to Main Menu", 
            command=self.show_main_menu, width=30).pack(pady=20)
    
    def show_staff_performance_report(self):
        """显示业务员工作情况报表"""
        report_window = self.utils.create_modal_window("Staff Performance Report", "300x250")
        Label(report_window, text="Staff Performance Report", font=("Arial", 14)).pack(pady=10)
        
        # 乘务员ID输入
        Label(report_window, text="Staff ID (optional):").pack()
        staff_id_entry = Entry(report_window)
        staff_id_entry.pack(pady=5)
        
        # 日期输入
        Label(report_window, text="Date (YYYY-MM-DD):").pack()
        date_entry = Entry(report_window)
        date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=5)
        
        def view_report():
            staff_id = staff_id_entry.get().strip()
            report_date = date_entry.get().strip()
            
            if not self.utils.validate_date(report_date):
                self.utils.show_error("Error", "Invalid date format")
                return
                
            report_window.destroy()
            self.display_table(
                lambda: SalespersonService.get_daily_sales_report(report_date, staff_id),
                ["Staff ID", "Staff Name", "Total Orders", 
                "Booking Revenue", "Refund Amount"],
                is_staff_view=False
            )
        
        Button(report_window, text="View Report", 
            command=view_report).pack(pady=10)
            
        # 添加帮助提示
        help_text = "Leave Staff ID empty to view all staff performance"
        Label(report_window, text=help_text, 
            font=("Arial", 8, "italic")).pack(pady=5)
            
        Button(report_window, text="Cancel", 
            command=report_window.destroy).pack(pady=5)
    
    def process_order(self, order_id, staff_id, approve=True, refresh_callback=None):
        """处理订单（批准或拒绝）"""
        action = "approve" if approve else "reject"
        if self.utils.show_confirmation("Confirm Action", 
                                      f"Are you sure you want to {action} this order?"):
            success, message = OrderService.process_order(order_id, approve, staff_id)
            if success:
                self.utils.show_message("Success", message)
                if refresh_callback:
                    refresh_callback()  # 刷新订单列表
            else:
                self.utils.show_error("Error", message)
    
    def show_staff_management(self, manager_info):
        """显示员工管理界面"""
        self.utils.clear_frame(self.parent)
        Label(self.parent, text="Staff Management", font=("Arial", 16)).pack(pady=10)
        Label(self.parent, text=f"Logged in as: {manager_info['salesperson_name']} (Manager)", 
              font=("Arial", 10, "italic")).pack(pady=5)
        
        Button(self.parent, text="Manage Staff (Add/Edit/Delete)", 
               command=lambda: self.show_manage_staff(manager_info), width=30).pack(pady=10)
        
        Button(self.parent, text="Back to Main Menu", 
               command=self.show_main_menu, width=30).pack(pady=20)

    def show_manage_staff(self, manager_info=None):
        """显示管理员工界面
        
        Args:
            manager_info: 当前登录的管理员信息
        """
        # 保存当前管理员ID
        current_manager_id = manager_info.get('salesperson_id') if manager_info else None
        
        def get_all_staff():
            try:
                staff_list = Salesperson.get_all_staff()
                formatted_staff = []
                for staff in staff_list:
                    formatted_staff.append([
                        staff['salesperson_id'],
                        staff['salesperson_name'],
                        staff['role'],
                        staff['contact_number'] or 'N/A',
                        staff['email'] or 'N/A'
                    ])
                return formatted_staff, None
            except Exception as e:
                return [], f"Error fetching staff: {str(e)}"
        
        def on_select(event):
            selected_items = tree.selection()
            if selected_items:
                edit_btn['state'] = 'normal'
                
                # 检查是否选择了自己
                item = selected_items[0]
                selected_staff_id = tree.item(item)['values'][0]
                
                if selected_staff_id == current_manager_id:
                    delete_btn['state'] = 'disabled'  # 不能删除自己
                    delete_btn['text'] = "Cannot Delete Self"
                else:
                    delete_btn['state'] = 'normal'
                    delete_btn['text'] = "Delete Staff"
            else:
                edit_btn['state'] = 'disabled'
                delete_btn['state'] = 'disabled'
                delete_btn['text'] = "Delete Staff"
        
        def edit_staff():
            selected_items = tree.selection()
            if not selected_items:
                return
            
            item = selected_items[0]
            staff_data = tree.item(item)['values']
            
            self.show_edit_staff_form(staff_data, tree)
        
        def delete_staff():
            selected_items = tree.selection()
            if not selected_items:
                return
                
            item = selected_items[0]
            staff_id = tree.item(item)['values'][0]
            
            # 检查是否是当前管理员
            if staff_id == current_manager_id:
                self.utils.show_error("Not Allowed", "You cannot delete your own account")
                return
                
            if self.utils.show_confirmation("Confirm Delete", 
                          f"Are you sure you want to delete staff {staff_id}?\n\nThis action cannot be undone."):
                try:
                    # 删除员工
                    success, message = Salesperson.delete_staff(staff_id)
                    if success:
                        tree.delete(item)
                        self.utils.show_message("Success", message)
                    else:
                        self.utils.show_error("Error", message)
                except Exception as e:
                    self.utils.show_error("Error", f"Failed to delete staff: {str(e)}")
        
        def refresh_staff_list():
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
            
            # 加载最新数据
            staff_list, error = get_all_staff()
            if error:
                self.utils.show_error("Error", error)
                return
                
            for staff in staff_list:
                tree.insert("", "end", values=staff)
        
        manage_window = self.utils.create_modal_window(
            "Manage Staff",
            "600x500"
        )
        
        Label(manage_window, text="Manage Staff", 
              font=("Arial", 14)).pack(pady=10)
        
        # 创建员工列表
        frame = Frame(manage_window)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        columns = ["Staff ID", "Name", "Role", "Contact", "Email"]
        tree = ttk.Treeview(frame)
        tree["columns"] = columns
        tree["show"] = "headings"
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # 添加滚动条
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # 加载员工数据
        staff_list, error = get_all_staff()
        if error:
            self.utils.show_error("Error", error)
        
        for staff in staff_list:
            tree.insert("", "end", values=staff)
        
        # 绑定选择事件
        tree.bind("<<TreeviewSelect>>", on_select)
        
        # 按钮区域
        btn_frame = Frame(manage_window)
        btn_frame.pack(fill=X, pady=10)

        # 添加新员工按钮
        add_btn = Button(btn_frame, text="Add New Staff", 
                         command=lambda: self.show_add_staff_form(tree))
        add_btn.pack(side=LEFT, padx=5)
        
        edit_btn = Button(btn_frame, text="Edit Staff", state="disabled", command=edit_staff)
        edit_btn.pack(side=LEFT, padx=5)
        
        delete_btn = Button(btn_frame, text="Delete Staff", state="disabled", command=delete_staff)
        delete_btn.pack(side=LEFT, padx=5)
        
        refresh_btn = Button(btn_frame, text="Refresh List", command=refresh_staff_list)
        refresh_btn.pack(side=LEFT, padx=5)
        
        Button(manage_window, text="Close", 
               command=manage_window.destroy).pack(pady=10)

    def show_add_staff_form(self, parent_tree=None):
        """显示添加员工表单"""
        add_window = self.utils.create_modal_window(
            "Add New Staff",
            "400x450"
        )
        
        Label(add_window, text="Add New Staff", font=("Arial", 14)).pack(pady=10)
        
        # 员工ID
        Label(add_window, text="Staff ID:").pack(anchor="w", padx=20)
        id_entry = Entry(add_window, width=30)
        id_entry.pack(pady=5, padx=20)
        
        # 姓名
        Label(add_window, text="Name:").pack(anchor="w", padx=20)
        name_entry = Entry(add_window, width=30)
        name_entry.pack(pady=5, padx=20)
        
        # 联系电话
        Label(add_window, text="Contact:").pack(anchor="w", padx=20)
        contact_entry = Entry(add_window, width=30)
        contact_entry.pack(pady=5, padx=20)
        
        # 电子邮件
        Label(add_window, text="Email:").pack(anchor="w", padx=20)
        email_entry = Entry(add_window, width=30)
        email_entry.pack(pady=5, padx=20)
        
        # 密码
        Label(add_window, text="Password:").pack(anchor="w", padx=20)
        password_entry = Entry(add_window, width=30, show="*")
        password_entry.pack(pady=5, padx=20)
        
        # 角色选择
        Label(add_window, text="Role:").pack(anchor="w", padx=20)
        role_var = tk.StringVar(value="Salesperson")
        role_frame = tk.Frame(add_window)
        role_frame.pack(fill=X, padx=20, pady=5, anchor="w")
        
        tk.Radiobutton(role_frame, text="Salesperson", variable=role_var, 
                      value="Salesperson").pack(side=LEFT)
        tk.Radiobutton(role_frame, text="Manager", variable=role_var, 
                      value="Manager").pack(side=LEFT)
        
        # 添加一个状态标签用于显示错误信息
        status_label = Label(add_window, text="", fg="red")
        status_label.pack(pady=5)
        
        def save_staff():
            # 清除之前的状态信息
            status_label.config(text="")
            
            staff_id = id_entry.get().strip()
            name = name_entry.get().strip()
            contact = contact_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            role = role_var.get()
            
            # 详细的输入验证
            if not staff_id:
                status_label.config(text="Error: Staff ID is required")
                return
            
            if not name:
                status_label.config(text="Error: Name is required")
                return
            
            if not password:
                status_label.config(text="Error: Password is required")
                return
            
            # 员工ID格式验证
            if not staff_id.startswith("SP"):
                status_label.config(text="Error: Staff ID must start with 'SP'")
                return
            
            # 邮箱格式简单验证（如果提供）
            if email and "@" not in email:
                status_label.config(text="Error: Invalid email format")
                return
            
            try:
                # 调用模型方法进行添加
                success, message = Salesperson.add_staff(staff_id, name, contact, email, password, role)
                
                if success:
                    self.utils.show_message("Success", message)
                    add_window.destroy()
                    
                    # 如果是通过列表添加的，刷新列表
                    if parent_tree:
                        try:
                            # 清空现有数据
                            for item in parent_tree.get_children():
                                parent_tree.delete(item)
                            
                            # 重新加载数据
                            staff_list = Salesperson.get_all_staff()
                            for staff in staff_list:
                                parent_tree.insert("", "end", values=[
                                    staff['salesperson_id'],
                                    staff['salesperson_name'],
                                    staff['role'],
                                    staff['contact_number'] or 'N/A',
                                    staff['email'] or 'N/A'
                                ])
                        except Exception as e:
                            self.utils.show_error("Error", f"Failed to refresh staff list: {str(e)}")
                else:
                    # 在窗口中直接显示错误信息，更直观
                    status_label.config(text=f"Error: {message}")
                    # 同时显示错误对话框
                    self.utils.show_error("Error", message)
            except Exception as e:
                error_msg = f"Failed to add staff: {str(e)}"
                status_label.config(text=error_msg)
                self.utils.show_error("System Error", error_msg)
        
        Button(add_window, text="Save", 
               command=save_staff).pack(pady=10)
        Button(add_window, text="Cancel", 
               command=add_window.destroy).pack()

    def show_edit_staff_form(self, staff_data, parent_tree):
        """显示编辑员工表单"""
        staff_id = staff_data[0]
        name = staff_data[1]
        role = staff_data[2]
        contact = staff_data[3] if staff_data[3] != 'N/A' else ''
        email = staff_data[4] if staff_data[4] != 'N/A' else ''
        
        # 获取完整的员工信息
        staff_info = Salesperson.get_staff_by_id(staff_id)
        if not staff_info:
            self.utils.show_error("Error", f"Staff with ID {staff_id} not found")
            return
        
        edit_window = self.utils.create_modal_window(
            f"Edit Staff {staff_id}",
            "400x450"
        )
        
        Label(edit_window, text=f"Edit Staff {staff_id}", 
              font=("Arial", 14)).pack(pady=10)
        
        # 员工ID不可编辑
        Label(edit_window, text="Staff ID:").pack(anchor="w", padx=20)
        Label(edit_window, text=staff_id, width=30, anchor="w", bg="light gray").pack(pady=5, padx=20)
        
        # 姓名
        Label(edit_window, text="Name:").pack(anchor="w", padx=20)
        name_entry = Entry(edit_window, width=30)
        name_entry.insert(0, name)
        name_entry.pack(pady=5, padx=20)
        
        # 联系电话
        Label(edit_window, text="Contact:").pack(anchor="w", padx=20)
        contact_entry = Entry(edit_window, width=30)
        contact_entry.insert(0, contact)
        contact_entry.pack(pady=5, padx=20)
        
        # 电子邮件
        Label(edit_window, text="Email:").pack(anchor="w", padx=20)
        email_entry = Entry(edit_window, width=30)
        email_entry.insert(0, email)
        email_entry.pack(pady=5, padx=20)
        
        # 密码（可选）
        Label(edit_window, text="Password (leave blank to keep unchanged):").pack(anchor="w", padx=20)
        password_entry = Entry(edit_window, width=30, show="*")
        password_entry.pack(pady=5, padx=20)
        
        # 角色选择
        Label(edit_window, text="Role:").pack(anchor="w", padx=20)
        role_var = tk.StringVar(value=role)
        role_frame = tk.Frame(edit_window)
        role_frame.pack(fill=X, padx=20, pady=5, anchor="w")
        
        tk.Radiobutton(role_frame, text="Salesperson", variable=role_var, 
                      value="Salesperson").pack(side=LEFT)
        tk.Radiobutton(role_frame, text="Manager", variable=role_var, 
                      value="Manager").pack(side=LEFT)
        
        def save_changes():
            new_name = name_entry.get().strip()
            new_contact = contact_entry.get().strip()
            new_email = email_entry.get().strip()
            new_password = password_entry.get().strip() or None  # 空密码表示不更新密码
            new_role = role_var.get()
            
            if not new_name:
                self.utils.show_error("Error", "Name is required")
                return
            
            # 更新员工信息
            success, message = Salesperson.update_staff(staff_id, new_name, new_contact, new_email, new_password, new_role)
            
            if success:
                self.utils.show_message("Success", message)
                edit_window.destroy()
                
                # 更新表格中的数据
                for item in parent_tree.get_children():
                    if parent_tree.item(item)['values'][0] == staff_id:
                        parent_tree.item(item, values=[
                            staff_id,
                            new_name,
                            new_role,
                            new_contact or 'N/A',
                            new_email or 'N/A'
                        ])
                        break
            else:
                self.utils.show_error("Error", message)
        
        Button(edit_window, text="Save Changes", 
               command=save_changes).pack(pady=20)
        Button(edit_window, text="Cancel", 
               command=edit_window.destroy).pack()