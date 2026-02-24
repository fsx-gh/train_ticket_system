import tkinter as tk
from tkinter import ttk, Label, Entry, Button, Frame, BOTH, LEFT, X
import datetime

from db.models import Train, Station, Price
from core.services import TrainService, SalespersonService

class TrainManagementInterface:
    """列车管理界面类，封装列车管理相关功能"""
    
    def __init__(self, parent_window, utility_functions):
        """
        初始化列车管理界面
        
        Args:
            parent_window: 主窗口
            utility_functions: 包含辅助函数的字典，如 create_modal_window, show_message 等
        """
        self.parent = parent_window
        self.utils = utility_functions
    
    def show_train_management_login(self):
        """显示列车管理员登录窗口"""
        login_window = self.utils['create_modal_window'](
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
                self.utils['show_error']("Error", "Please fill in all fields")
                return
                
            success, result = SalespersonService.verify_credentials(staff_id, password)
            
            if success and result.get('role') == 'Manager':
                login_window.destroy()
                self.show_train_management(result)  # 显示列车管理界面
            else:
                self.utils['show_error']("Login Failed", "Only managers can access this feature")
        
        Button(login_window, text="Login", 
               command=verify_login).pack(pady=10)
        Button(login_window, text="Cancel", 
               command=login_window.destroy).pack(pady=5)

    def show_train_management(self, manager_info):
        """显示列车管理界面"""
        self.utils['clear_frame'](self.parent)
        Label(self.parent, text="Train Management", font=("Arial", 16)).pack(pady=10)
        Label(self.parent, text=f"Logged in as: {manager_info['salesperson_name']} (Manager)", 
              font=("Arial", 10, "italic")).pack(pady=5)
        
        Button(self.parent, text="Manage Trains (Add/Edit/Delete)", 
               command=self.show_manage_trains, width=30).pack(pady=10)
               
        Button(self.parent, text="Manage Train Prices", 
               command=self.show_price_management, width=30).pack(pady=10)
        
        Button(self.parent, text="Back to Main Menu", 
               command=self.utils['show_main_menu'], width=30).pack(pady=20)

    def show_add_train_form(self):
        """显示添加列车表单"""
        add_window = self.utils['create_modal_window'](
            "Add New Train",
            "300x450"
        )
        
        Label(add_window, text="Add New Train", font=("Arial", 14)).pack(pady=10)
        
        # 列车号
        Label(add_window, text="Train Number:").pack(anchor="w", padx=20)
        train_number_entry = Entry(add_window, width=30)
        train_number_entry.pack(pady=5, padx=20)
        
        # 列车类型 - 替换为下拉选择框
        Label(add_window, text="Train Type:").pack(anchor="w", padx=20)
        train_types = ["High-Speed", "Bullet", "Express", "Fast", "Direct"]
        train_type_var = tk.StringVar(add_window)
        train_type_var.set(train_types[0])  # 默认选择第一项
        train_type_dropdown = tk.OptionMenu(add_window, train_type_var, *train_types)
        train_type_dropdown.config(width=25)
        train_type_dropdown.pack(pady=5, padx=20)
        
        # 总座位数
        Label(add_window, text="Total Seats:").pack(anchor="w", padx=20)
        seats_entry = Entry(add_window, width=30)
        seats_entry.insert(0, "1200")  # 默认值
        seats_entry.pack(pady=5, padx=20)
        
        # 出发站
        Label(add_window, text="Departure Station:").pack(anchor="w", padx=20)
        dep_station_entry = Entry(add_window, width=30)
        dep_station_entry.insert(0, "北京")  # 默认值
        dep_station_entry.pack(pady=5, padx=20)
        
        # 终点站
        Label(add_window, text="Arrival Station:").pack(anchor="w", padx=20)
        arr_station_entry = Entry(add_window, width=30)
        arr_station_entry.insert(0, "上海")  # 默认值
        arr_station_entry.pack(pady=5, padx=20)
        
        def save_train():
            train_number = train_number_entry.get().strip()
            train_type = train_type_var.get().strip()
            
            try:
                total_seats = int(seats_entry.get().strip())
                if total_seats <= 0:
                    self.utils['show_error']("Error", "Total seats must be a positive number")
                    return
            except ValueError:
                self.utils['show_error']("Error", "Total seats must be a number")
                return
                
            departure_station = dep_station_entry.get().strip()
            arrival_station = arr_station_entry.get().strip()
            
            if not train_number or not train_type or not departure_station or not arrival_station:
                self.utils['show_error']("Error", "All fields are required")
                return
                
            try:
                # 检查是否存在相同编号的列车
                existing_train = Train.find_one({"train_number": train_number})
                if existing_train:
                    self.utils['show_error']("Error", f"Train {train_number} already exists")
                    return
                    
                # 使用模型类创建新列车
                new_train = Train.set_train(
                    train_number, train_type, total_seats,
                    departure_station, arrival_station
                )
                
                self.utils['show_message']("Success", f"Train {train_number} has been added successfully")
                add_window.destroy()
            except Exception as e:
                self.utils['show_error']("Error", f"Failed to add train: {str(e)}")
        
        Button(add_window, text="Save", 
               command=save_train).pack(pady=20)
        Button(add_window, text="Cancel", 
               command=add_window.destroy).pack()

    def show_manage_trains(self):
        """显示管理现有列车界面"""
        def get_all_trains():
            try:
                trains = Train.get_all_trains_with_stations()
                formatted_trains = []
                for train in trains:
                    formatted_trains.append([
                        train['train_number'],
                        train['train_type'],
                        train['total_seats'],
                        train['departure_station'],
                        train['arrival_station']
                    ])
                return formatted_trains, None
            except Exception as e:
                return [], f"Error fetching trains: {str(e)}"
        
        def on_select(event):
            selected_items = tree.selection()
            if selected_items:
                edit_btn['state'] = 'normal'
                delete_btn['state'] = 'normal'
            else:
                edit_btn['state'] = 'disabled'
                delete_btn['state'] = 'disabled'
        
        def edit_train():
            selected_items = tree.selection()
            if not selected_items:
                return
            
            item = selected_items[0]
            train_data = tree.item(item)['values']
            
            self.show_edit_train_form(train_data, tree)
        
        def delete_train():
            selected_items = tree.selection()
            if not selected_items:
                return
                
            item = selected_items[0]
            train_number = tree.item(item)['values'][0]
            
            if self.utils['show_confirmation']("Confirm Delete", 
                              f"Are you sure you want to delete train {train_number}?\n\nThis will also delete all related stopovers, schedules and prices."):
                try:
                    # 删除列车
                    success = Train.delete({"train_number": train_number})
                    if success:
                        tree.delete(item)
                        self.utils['show_message']("Success", f"Train {train_number} has been deleted")
                    else:
                        self.utils['show_error']("Error", "Failed to delete train")
                except Exception as e:
                    self.utils['show_error']("Error", f"Failed to delete train: {str(e)}")
            
        def refresh_train_list():
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
            
            # 加载最新数据
            trains, error = get_all_trains()
            if error:
                self.utils['show_error']("Error", error)
                return
                
            for train in trains:
                tree.insert("", "end", values=train)
        
        manage_window = self.utils['create_modal_window'](
            "Manage Trains",
            "600x500"
        )
        
        Label(manage_window, text="Manage Trains", 
              font=("Arial", 14)).pack(pady=10)

        
        # 创建列车列表
        frame = Frame(manage_window)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        columns = ["Train No", "Type", "Seats", "Departure", "Arrival"]
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
        
        # 加载列车数据
        trains, error = get_all_trains()
        if error:
            self.utils['show_error']("Error", error)
        
        for train in trains:
            tree.insert("", "end", values=train)
        
        # 绑定选择事件
        tree.bind("<<TreeviewSelect>>", on_select)
        
        # 按钮区域
        btn_frame = Frame(manage_window)
        btn_frame.pack(fill=X, pady=10)

        # 添加新列车按钮
        add_btn = Button(btn_frame, text="Add New Train", 
                         command=self.show_add_train_form)
        add_btn.pack(side=LEFT, padx=5)
        
        edit_btn = Button(btn_frame, text="Edit Train", state="disabled", command=edit_train)
        edit_btn.pack(side=LEFT, padx=5)
        
        delete_btn = Button(btn_frame, text="Delete Train", state="disabled", command=delete_train)
        delete_btn.pack(side=LEFT, padx=5)
        
        refresh_btn = Button(btn_frame, text="Refresh List", command=refresh_train_list)
        refresh_btn.pack(side=LEFT, padx=5)
        
        Button(manage_window, text="Close", 
               command=manage_window.destroy).pack(pady=10)

    def show_edit_train_form(self, train_data, parent_tree):
        """显示编辑列车表单"""
        train_number = train_data[0]
        train_type = train_data[1]
        total_seats = train_data[2]
        departure_station = train_data[3]
        arrival_station = train_data[4]
        
        edit_window = self.utils['create_modal_window'](
            f"Edit Train {train_number}",
            "400x400"
        )
        
        Label(edit_window, text=f"Edit Train {train_number}", 
              font=("Arial", 14)).pack(pady=10)
        
        # 列车号不可编辑
        Label(edit_window, text="Train Number:").pack(anchor="w", padx=20)
        train_number_label = Label(edit_window, text=train_number, width=30, anchor="w", bg="light gray")
        train_number_label.pack(pady=5, padx=20)
        
        # 列车类型 - 替换为下拉选择框
        Label(edit_window, text="Train Type:").pack(anchor="w", padx=20)
        train_types = ["High-Speed", "Bullet", "Express", "Fast", "Direct"]
        train_type_var = tk.StringVar(edit_window)
        train_type_var.set(train_type if train_type in train_types else train_types[0])
        train_type_dropdown = tk.OptionMenu(edit_window, train_type_var, *train_types)
        train_type_dropdown.config(width=25)
        train_type_dropdown.pack(pady=5, padx=20)
        
        # 总座位数
        Label(edit_window, text="Total Seats:").pack(anchor="w", padx=20)
        seats_entry = Entry(edit_window, width=30)
        seats_entry.insert(0, total_seats)
        seats_entry.pack(pady=5, padx=20)
        
        # 出发站
        Label(edit_window, text="Departure Station:").pack(anchor="w", padx=20)
        dep_station_entry = Entry(edit_window, width=30)
        dep_station_entry.insert(0, departure_station)
        dep_station_entry.pack(pady=5, padx=20)
        
        # 终点站
        Label(edit_window, text="Arrival Station:").pack(anchor="w", padx=20)
        arr_station_entry = Entry(edit_window, width=30)
        arr_station_entry.insert(0, arrival_station)
        arr_station_entry.pack(pady=5, padx=20)
        
        def save_changes():
            new_train_type = train_type_var.get().strip()
            
            try:
                new_total_seats = int(seats_entry.get().strip())
                if new_total_seats <= 0:
                    self.utils['show_error']("Error", "Total seats must be a positive number")
                    return
            except ValueError:
                self.utils['show_error']("Error", "Total seats must be a number")
                return
                
            new_dep_station = dep_station_entry.get().strip()
            new_arr_station = arr_station_entry.get().strip()
            
            if not new_train_type or not new_dep_station or not new_arr_station:
                self.utils['show_error']("Error", "All fields are required")
                return
            
            try:
                # 查找或创建站点
                dep_station = Station.find_one({"station_name": new_dep_station})
                if not dep_station:
                    dep_station = Station(station_name=new_dep_station)
                    dep_station.save()
                    dep_station = Station.find_one({"station_name": new_dep_station})
                    
                arr_station = Station.find_one({"station_name": new_arr_station})
                if not arr_station:
                    arr_station = Station(station_name=new_arr_station)
                    arr_station.save()
                    arr_station = Station.find_one({"station_name": new_arr_station})
                
                # 更新列车信息
                train = Train(
                    train_number=train_number,
                    train_type=new_train_type,
                    total_seats=new_total_seats,
                    departure_station_id=dep_station['station_id'],
                    arrival_station_id=arr_station['station_id']
                )
                train.save()
                
                self.utils['show_message']("Success", f"Train {train_number} has been updated successfully")
                edit_window.destroy()
                
                # 刷新列车列表
                for item in parent_tree.get_children():
                    if parent_tree.item(item)['values'][0] == train_number:
                        parent_tree.item(item, values=[
                            train_number,
                            new_train_type,
                            new_total_seats,
                            new_dep_station,
                            new_arr_station
                        ])
                        break
            except Exception as e:
                self.utils['show_error']("Error", f"Failed to update train: {str(e)}")
        
        Button(edit_window, text="Save Changes", 
               command=save_changes).pack(pady=20)
        Button(edit_window, text="Cancel", 
               command=edit_window.destroy).pack()

    def show_price_management(self):
        """显示价格管理界面"""
        price_window = self.utils['create_modal_window'](
            "Train Price Management",
            "700x500"
        )
        
        Label(price_window, text="Train Price Management", 
              font=("Arial", 14)).pack(pady=10)
        
        # 创建价格列表
        frame = Frame(price_window)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        columns = ["ID", "Train No", "Train Type", "Departure Station", "Arrival Station", "Price"]
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
        
        # 加载价格数据
        try:
            prices = Price.get_all_prices_view()
            for price in prices:
                tree.insert("", "end", values=[
                    price['price_id'],
                    price['train_number'],
                    price['train_type'],
                    price['departure_station'],
                    price['arrival_station'],
                    price['price']
                ])
        except Exception as e:
            self.utils['show_error']("Error", f"Failed to load prices: {str(e)}")
        
        def on_select(event):
            selected_items = tree.selection()
            if selected_items:
                edit_price_btn['state'] = 'normal'
                delete_price_btn['state'] = 'normal'
            else:
                edit_price_btn['state'] = 'disabled'
                delete_price_btn['state'] = 'disabled'
                
        tree.bind("<<TreeviewSelect>>", on_select)
        
        def add_price():
            self.show_add_price_form(tree)
            
        def edit_price():
            selected_items = tree.selection()
            if not selected_items:
                return
                
            item = selected_items[0]
            price_data = tree.item(item)['values']
            self.show_edit_price_form(price_data, tree)
            
        def delete_price():
            selected_items = tree.selection()
            if not selected_items:
                return
                
            item = selected_items[0]
            price_id = tree.item(item)['values'][0]
            
            if self.utils['show_confirmation']("Confirm Delete", 
                               f"Are you sure you want to delete this price record?"):
                try:
                    success = Price.delete({"price_id": price_id})
                    if success:
                        tree.delete(item)
                        self.utils['show_message']("Success", "Price has been deleted")
                    else:
                        self.utils['show_error']("Error", "Failed to delete price")
                except Exception as e:
                    self.utils['show_error']("Error", f"Failed to delete price: {str(e)}")
                    
        def refresh_prices():
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
            
            # 加载最新数据
            try:
                prices = Price.get_all_prices_view()
                for price in prices:
                    tree.insert("", "end", values=[
                        price['price_id'],
                        price['train_number'],
                        price['train_type'],
                        price['departure_station'],
                        price['arrival_station'],
                        price['price']
                    ])
            except Exception as e:
                self.utils['show_error']("Error", f"Failed to load prices: {str(e)}")
        
        # 按钮区域
        btn_frame = Frame(price_window)
        btn_frame.pack(fill=X, pady=10)
        
        add_price_btn = Button(btn_frame, text="Add New Price", command=add_price)
        add_price_btn.pack(side=LEFT, padx=5)
        
        edit_price_btn = Button(btn_frame, text="Edit Price", state="disabled", command=edit_price)
        edit_price_btn.pack(side=LEFT, padx=5)
        
        delete_price_btn = Button(btn_frame, text="Delete Price", state="disabled", command=delete_price)
        delete_price_btn.pack(side=LEFT, padx=5)
        
        refresh_btn = Button(btn_frame, text="Refresh", command=refresh_prices)
        refresh_btn.pack(side=LEFT, padx=5)
        
        Button(price_window, text="Close", 
               command=price_window.destroy).pack(pady=10)
    
    def show_add_price_form(self, parent_tree):
        """显示添加价格表单"""
        add_window = self.utils['create_modal_window'](
            "Add New Price",
            "400x400"
        )
        
        Label(add_window, text="Add New Price", 
              font=("Arial", 14)).pack(pady=10)
        
        # 列车号
        Label(add_window, text="Train Number:").pack(anchor="w", padx=20)
        train_number_entry = Entry(add_window, width=30)
        train_number_entry.pack(pady=5, padx=20)
        
        # 出发站
        Label(add_window, text="Departure Station:").pack(anchor="w", padx=20)
        dep_station_entry = Entry(add_window, width=30)
        dep_station_entry.pack(pady=5, padx=20)
        
        # 到达站
        Label(add_window, text="Arrival Station:").pack(anchor="w", padx=20)
        arr_station_entry = Entry(add_window, width=30)
        arr_station_entry.pack(pady=5, padx=20)
        
        # 价格
        Label(add_window, text="Price:").pack(anchor="w", padx=20)
        price_entry = Entry(add_window, width=30)
        price_entry.insert(0, "100.0")
        price_entry.pack(pady=5, padx=20)
        
        def save_price():
            train_number = train_number_entry.get().strip()
            dep_station = dep_station_entry.get().strip()
            arr_station = arr_station_entry.get().strip()
            
            # 验证列车是否存在
            train = Train.find_one({"train_number": train_number})
            if not train:
                self.utils['show_error']("Error", f"Train {train_number} does not exist")
                return
                
            try:
                price = float(price_entry.get().strip())
                if price <= 0:
                    self.utils['show_error']("Error", "Price must be a positive number")
                    return
            except ValueError:
                self.utils['show_error']("Error", "Price must be a number")
                return
                
            if not train_number or not dep_station or not arr_station:
                self.utils['show_error']("Error", "All fields are required")
                return
            
            try:
                # 设置票价
                success = Price.set_price(
                    train_number, dep_station, arr_station, price
                )
                
                if success:
                    self.utils['show_message']("Success", f"Price set successfully for train {train_number}")
                    add_window.destroy()
                    
                    # 刷新价格列表
                    for item in parent_tree.get_children():
                        parent_tree.delete(item)
                        
                    prices = Price.get_all_prices_view()
                    for p in prices:
                        parent_tree.insert("", "end", values=[
                            p['price_id'],
                            p['train_number'],
                            p['train_type'],
                            p['departure_station'],
                            p['arrival_station'],
                            p['price']
                        ])
                else:
                    self.utils['show_error']("Error", "Failed to set price. Check if stations exist.")
            except Exception as e:
                self.utils['show_error']("Error", f"Failed to set price: {str(e)}")
        
        Button(add_window, text="Save", 
               command=save_price).pack(pady=20)
        Button(add_window, text="Cancel", 
               command=add_window.destroy).pack()
    
    def show_edit_price_form(self, price_data, parent_tree):
        """显示编辑价格表单"""
        price_id = price_data[0]
        train_number = price_data[1]
        departure_station = price_data[3]
        arrival_station = price_data[4]
        current_price = price_data[5]
        
        edit_window = self.utils['create_modal_window'](
            "Edit Price",
            "400x450"
        )
        
        Label(edit_window, text="Edit Price", 
              font=("Arial", 14)).pack(pady=10)
        
        # 价格ID不可编辑
        Label(edit_window, text="Price ID:").pack(anchor="w", padx=20)
        Label(edit_window, text=price_id, width=30, anchor="w", bg="light gray").pack(pady=5, padx=20)
        
        # 列车号不可编辑
        Label(edit_window, text="Train Number:").pack(anchor="w", padx=20)
        Label(edit_window, text=train_number, width=30, anchor="w", bg="light gray").pack(pady=5, padx=20)
        
        # 出发站不可编辑
        Label(edit_window, text="Departure Station:").pack(anchor="w", padx=20)
        Label(edit_window, text=departure_station, width=30, anchor="w", bg="light gray").pack(pady=5, padx=20)
        
        # 到达站不可编辑
        Label(edit_window, text="Arrival Station:").pack(anchor="w", padx=20)
        Label(edit_window, text=arrival_station, width=30, anchor="w", bg="light gray").pack(pady=5, padx=20)
        
        # 价格可编辑
        Label(edit_window, text="Price:").pack(anchor="w", padx=20)
        price_entry = Entry(edit_window, width=30)
        price_entry.insert(0, current_price)
        price_entry.pack(pady=5, padx=20)
        
        def save_changes():
            try:
                new_price = float(price_entry.get().strip())
                if new_price <= 0:
                    self.utils['show_error']("Error", "Price must be a positive number")
                    return
            except ValueError:
                self.utils['show_error']("Error", "Price must be a number")
                return
            
            try:
                # 更新价格
                success = Price.update(
                    {"price_id": price_id},
                    {"price": new_price}
                )
                
                if success:
                    self.utils['show_message']("Success", "Price has been updated")
                    edit_window.destroy()
                    
                    # 更新表格中的数据
                    for item in parent_tree.get_children():
                        if parent_tree.item(item)['values'][0] == price_id:
                            values = parent_tree.item(item)['values']
                            values[5] = new_price
                            parent_tree.item(item, values=values)
                            break
                else:
                    self.utils['show_error']("Error", "Failed to update price")
            except Exception as e:
                self.utils['show_error']("Error", f"Failed to update price: {str(e)}")
        
        Button(edit_window, text="Save Changes", 
               command=save_changes).pack(pady=20)
        Button(edit_window, text="Cancel", 
               command=edit_window.destroy).pack()