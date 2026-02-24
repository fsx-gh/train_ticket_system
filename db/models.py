# models.py

from db import db  # Import the singleton database instance

class BaseModel:
    """Base class for common CRUD operations."""
    _table_name = None
    _primary_key = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_all(cls, conditions=None):
        query = f"SELECT * FROM `{cls._table_name}`"
        params = []
        if conditions:
            where_clauses = []
            for k, v in conditions.items():
                if v is not None:
                    where_clauses.append(f"`{k}` = %s")
                    params.append(v)
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        return db.execute_query(query, tuple(params) if params else None, fetch_all=True)

    @classmethod
    def find_one(cls, conditions):
        if not conditions:
            return None
            
        where_clauses = []
        params = []
        for k, v in conditions.items():
            if v is not None:
                where_clauses.append(f"`{k}` = %s")
                params.append(v)
        
        if not where_clauses:
            return None
            
        query = f"SELECT * FROM `{cls._table_name}` WHERE " + " AND ".join(where_clauses)
        return db.execute_query(query, tuple(params), fetch_one=True)

    def save(self):
        try:        
            # Determine if it's an insert or update
            if hasattr(self, self._primary_key) and getattr(self, self._primary_key) is not None:
                # Update existing record
                updates = []
                params = []
                for k, v in self.__dict__.items():
                    if k != self._primary_key and k != "_table_name" and k != "_primary_key":
                        updates.append(f"`{k}` = %s")
                        params.append(v)
                query = f"UPDATE `{self._table_name}` SET {', '.join(updates)} WHERE `{self._primary_key}` = %s"
                params.append(getattr(self, self._primary_key))
                return db.execute_query(query, tuple(params))
            else:
                # Insert new record
                columns = []
                values = []
                for k, v in self.__dict__.items():
                    if k != "_table_name" and k != "_primary_key":
                        columns.append(f"`{k}`")
                        values.append(v)
                placeholders = ", ".join(["%s"] * len(columns))
                query = f"INSERT INTO `{self._table_name}` ({', '.join(columns)}) VALUES ({placeholders})"
                return db.execute_query(query, tuple(values))
        except Exception as e:
            print(f"Error during save: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def delete(cls, conditions):
        if not conditions:
            return False
            
        where_clauses = []
        params = []
        for k, v in conditions.items():
            if v is not None:
                where_clauses.append(f"`{k}` = %s")
                params.append(v)
        
        if not where_clauses:
            return False
            
        query = f"DELETE FROM `{cls._table_name}` WHERE " + " AND ".join(where_clauses)
        return db.execute_query(query, tuple(params))


class Station(BaseModel):
    _table_name = "Stations"
    _primary_key = "station_id"

    def __init__(self, station_id=None, station_name=None, station_code=None):
        super().__init__(station_id=station_id, station_name=station_name, station_code=station_code)


class Train(BaseModel):
    _table_name = "Trains"
    _primary_key = "train_number"

    def __init__(self, train_number=None, train_type=None, total_seats=None,
                 departure_station_id=None, arrival_station_id=None):
        super().__init__(
            train_number=train_number, train_type=train_type, total_seats=total_seats,
            departure_station_id=departure_station_id, arrival_station_id=arrival_station_id
        )
    
    @classmethod
    def set_train(cls, train_number, train_type, total_seats, departure_station_name, arrival_station_name):
        try:            
            # 查找或创建出发站
            dep_station = Station.find_one({"station_name": departure_station_name})
            if not dep_station:
                new_dep_station = Station(station_name=departure_station_name)
                new_dep_station.save()
                dep_station = Station.find_one({"station_name": departure_station_name})
                if not dep_station:
                    return False
            
            # 查找或创建到达站
            arr_station = Station.find_one({"station_name": arrival_station_name})
            if not arr_station:
                new_arr_station = Station(station_name=arrival_station_name)
                new_arr_station.save()
                arr_station = Station.find_one({"station_name": arrival_station_name})
                if not arr_station:
                    return False
                
            # 检查现有列车 - 应在这里处理更新逻辑
            existing_train = cls.find_one({"train_number": train_number})
            
            # 直接使用原始SQL插入而非ORM
            if not existing_train:
                query = """
                INSERT INTO `Trains` (`train_number`, `train_type`, `total_seats`, `departure_station_id`, `arrival_station_id`) 
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (train_number, train_type, int(total_seats), dep_station['station_id'], arr_station['station_id'])
                result = db.execute_query(query, params)
            else:
                # 如果列车已存在，使用UPDATE语句
                query = """
                UPDATE `Trains` 
                SET `train_type` = %s, `total_seats` = %s, `departure_station_id` = %s, `arrival_station_id` = %s 
                WHERE `train_number` = %s
                """
                params = (train_type, int(total_seats), dep_station['station_id'], arr_station['station_id'], train_number)
                result = db.execute_query(query, params)
                
            # 验证保存结果
            verify = cls.find_one({"train_number": train_number})
            return verify is not None
            
        except Exception as e:
            print(f"Error in set_train: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @classmethod
    def get_all_trains_with_stations(cls):
        """获取所有列车信息，包括站点名称"""
        query = """
        SELECT t.*, 
               dep.station_name AS departure_station, 
               arr.station_name AS arrival_station
        FROM Trains t
        JOIN Stations dep ON t.departure_station_id = dep.station_id
        JOIN Stations arr ON t.arrival_station_id = arr.station_id
        ORDER BY t.train_number
        """
        return db.execute_query(query, fetch_all=True)
 

class Stopover(BaseModel):
    _table_name = "Stopovers"
    _primary_key = "stopover_id"

    def __init__(self, stopover_id=None, train_number=None, station_id=None,
                start_date=None, arrival_time=None, departure_time=None, 
                stop_order=None, seats=None, distance=None):
        super().__init__(
            stopover_id=stopover_id, train_number=train_number, station_id=station_id,
            start_date=start_date, arrival_time=arrival_time, departure_time=departure_time, 
            stop_order=stop_order, seats=seats
        )


class Price(BaseModel):
    _table_name = "Prices"
    _primary_key = "price_id"

    def __init__(self, price_id=None, train_number=None, departure_station_id=None,
                 arrival_station_id=None, price=None):
        super().__init__(
            price_id=price_id, train_number=train_number, 
            departure_station_id=departure_station_id,
            arrival_station_id=arrival_station_id, price=price
        )
        
    @classmethod
    def get_all_prices_view(cls):
        """
        获取所有价格信息，使用PricesView视图
        
        Returns:
            包含所有价格信息的列表，每个价格包含列车号、出发站、到达站、票价等信息
        """
        query = """
        SELECT 
            price_id,
            train_number,
            train_type,
            departure_station,
            arrival_station,
            price
        FROM 
            PricesView
        ORDER BY 
            train_number, departure_station, arrival_station
        """
        try:
            return db.execute_query(query, fetch_all=True)
        except Exception as e:
            print(f"Error fetching prices view: {e}")
            return []
            
    @classmethod
    def get_train_prices(cls, train_number):
        """
        获取指定列车的所有价格信息
        
        Args:
            train_number: 列车编号
            
        Returns:
            包含指定列车所有价格信息的列表
        """
        query = """
        SELECT 
            price_id,
            train_number,
            train_type,
            departure_station,
            arrival_station,
            price
        FROM 
            PricesView
        WHERE
            train_number = %s
        ORDER BY 
            departure_station, arrival_station
        """
        try:
            return db.execute_query(query, (train_number,), fetch_all=True)
        except Exception as e:
            print(f"Error fetching train prices: {e}")
            return []
        
        
    @classmethod
    def set_price(cls, train_number, departure_station_name, arrival_station_name, price):
        """
        设置列车特定路段的票价
        
        Args:
            train_number: 列车编号
            departure_station_name: 出发站名称
            arrival_station_name: 到达站名称
            price: 票价
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            # 查找站点
            dep_station = Station.find_one({"station_name": departure_station_name})
            arr_station = Station.find_one({"station_name": arrival_station_name})
            
            if not dep_station or not arr_station:
                return False
            
            # 查找现有价格
            existing_price = Price.find_one({
                "train_number": train_number,
                "departure_station_id": dep_station['station_id'],
                "arrival_station_id": arr_station['station_id']
            })
            
            if existing_price:
                # 更新价格
                price_obj = Price(
                    price_id=existing_price['price_id'],
                    train_number=train_number,
                    departure_station_id=dep_station['station_id'],
                    arrival_station_id=arr_station['station_id'],
                    price=price
                )
                price_obj.save()
            else:
                # 创建新价格
                price_obj = Price(
                    train_number=train_number,
                    departure_station_id=dep_station['station_id'],
                    arrival_station_id=arr_station['station_id'],
                    price=price
                )
                price_obj.save()
                
            return True
            
        except Exception as e:
            print(f"Error setting price: {e}")
            return False
       
    @classmethod
    def update(cls, conditions, values):
        """
        更新价格记录
        
        Args:
            conditions: 更新条件，通常是 {"price_id": price_id}
            values: 要更新的值，如 {"price": new_price}
            
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            if not conditions or not values:
                return False
                
            where_clauses = []
            where_params = []
            for k, v in conditions.items():
                if v is not None:
                    where_clauses.append(f"`{k}` = %s")
                    where_params.append(v)
            
            if not where_clauses:
                return False
                
            set_clauses = []
            set_params = []
            for k, v in values.items():
                set_clauses.append(f"`{k}` = %s")
                set_params.append(v)
                
            if not set_clauses:
                return False
                
            query = f"UPDATE `{cls._table_name}` SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
            params = set_params + where_params
            
            return db.execute_query(query, tuple(params))
            
        except Exception as e:
            print(f"Error updating price: {e}")
            return False

class Salesperson(BaseModel):
    _table_name = "Salespersons"
    _primary_key = "salesperson_id"

    def __init__(self, salesperson_id=None, salesperson_name=None, contact_number=None, 
                 email=None, password=None, role=None):
        super().__init__(
            salesperson_id=salesperson_id, 
            salesperson_name=salesperson_name, 
            contact_number=contact_number,
            email=email, 
            password=password, 
            role=role
        )
    
    @classmethod
    def get_all_staff(cls):
        """获取所有员工信息"""
        query = """
        SELECT salesperson_id, salesperson_name, contact_number, email, role 
        FROM Salespersons 
        ORDER BY role, salesperson_name
        """
        try:
            return db.execute_query(query, fetch_all=True)
        except Exception as e:
            print(f"Error getting staff list: {e}")
            return []
    
    @classmethod
    def get_staff_by_id(cls, staff_id):
        """根据ID获取员工信息"""
        return cls.find_one({"salesperson_id": staff_id})
    
    @classmethod
    def add_staff(cls, staff_id, name, contact, email, password, role):
        """添加新员工
    
        Args:
            staff_id: 员工ID
            name: 员工姓名
            contact: 联系电话
            email: 电子邮件
            password: 密码
            role: 角色 (Manager 或 Salesperson)
        
        Returns:
            (success, message) 元组
        """
        try:
            # 检查邮箱是否已存在
            if email:  # 只有当提供了邮箱时才检查
                existing_with_email = cls.find_one({"email": email})
                if existing_with_email:
                    return False, f"Email {email} is already in use"
        
            # 检查ID是否已存在
            existing_with_id = cls.find_one({"salesperson_id": staff_id})
            if existing_with_id:
                return False, f"Staff ID {staff_id} is already in use"
        
            # 使用直接SQL插入而不是ORM
            query = """
            INSERT INTO `Salespersons` 
            (`salesperson_id`, `salesperson_name`, `contact_number`, `email`, `password`, `role`) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (staff_id, name, contact, email, password, role)
        
            # 执行SQL并获取结果
            result = db.execute_query(query, params)
        
            # 验证是否成功添加
            if result:
                # 可选：通过查询验证添加是否成功
                verify = cls.find_one({"salesperson_id": staff_id})
                if verify:
                    return True, f"Staff {name} with ID {staff_id} added successfully"
                else:
                    return False, "Staff was not added properly despite successful query"
            else:
                return False, "Failed to add staff - database error"
            
        except Exception as e:
            error_message = str(e)
            # 针对常见的MySQL错误提供更友好的消息
            if "Duplicate entry" in error_message:
                if "salesperson_id" in error_message:
                    return False, f"Staff ID {staff_id} is already in use"
                elif "email" in error_message:
                    return False, f"Email {email} is already in use"
        
            # 对于其他错误，返回详细的错误信息
            return False, f"Database error: {error_message}"
    
    @classmethod
    def update_staff(cls, staff_id, name, contact, email, password, role):
        """更新员工信息
        
        Args:
            staff_id: 员工ID
            name: 员工姓名
            contact: 联系电话
            email: 电子邮件
            password: 密码 (如果为None，则不更新密码)
            role: 角色 (Manager 或 Salesperson)
            
        Returns:
            (success, message) 元组
        """
        try:
            # 检查邮箱是否已被其他员工使用
            email_check_query = """
            SELECT * FROM Salespersons 
            WHERE email = %s AND salesperson_id != %s
            """
            
            existing_email = db.execute_query(email_check_query, (email, staff_id), fetch_one=True)
            if existing_email:
                return False, f"Email {email} is already in use by another staff"
            
            # 获取现有员工信息
            existing_staff = cls.find_one({"salesperson_id": staff_id})
            if not existing_staff:
                return False, f"Staff ID {staff_id} not found"
            
            # 准备更新的数据
            if password:
                # 包括更新密码
                staff = cls(
                    salesperson_id=staff_id,
                    salesperson_name=name,
                    contact_number=contact,
                    email=email,
                    password=password,
                    role=role
                )
            else:
                # 不更新密码，保留原密码
                staff = cls(
                    salesperson_id=staff_id,
                    salesperson_name=name,
                    contact_number=contact,
                    email=email,
                    password=existing_staff["password"],
                    role=role
                )
            
            result = staff.save()
            if result:
                return True, "Staff updated successfully"
            else:
                return False, "Failed to update staff"
                
        except Exception as e:
            return False, f"Error updating staff: {str(e)}"
    
    @classmethod
    def delete_staff(cls, staff_id):
        """删除员工
        
        Args:
            staff_id: 要删除的员工ID
            
        Returns:
            (success, message) 元组
        """
        try:
            # 检查是否有此员工处理的未完成订单
            check_query = """
            SELECT COUNT(*) as count 
            FROM OrderOperations 
            WHERE salesperson_id = %s
            """
            
            result = db.execute_query(check_query, (staff_id,), fetch_one=True)
            if result and result['count'] > 0:
                return False, f"Cannot delete staff with {result['count']} processed orders. Reassign orders first."
            
            # 删除员工
            deleted = cls.delete({"salesperson_id": staff_id})
            if deleted:
                return True, "Staff deleted successfully"
            else:
                return False, "Failed to delete staff"
                
        except Exception as e:
            return False, f"Error deleting staff: {str(e)}"
    
    @classmethod
    def verify_credentials(cls, salesperson_id, password):
        """验证销售人员凭据
    
        Args:
            salesperson_id: 销售人员ID
            password: 密码
        
        Returns:
            如果验证成功，返回销售人员信息；否则返回None
        """
        try:
            query = """
            SELECT salesperson_id, salesperson_name, role
            FROM Salespersons 
            WHERE salesperson_id = %s AND password = %s
            """
            return db.execute_query(query, (salesperson_id, password), fetch_one=True)
        except Exception as e:
            print(f"Error verifying credentials: {e}")
            return None
    
    @classmethod
    def get_daily_sales_report(cls, report_date, staff_id=None):
        """获取指定日期的销售报表
    
        Args:
            report_date: 报表日期，格式为YYYY-MM-DD
            staff_id: 指定乘务员ID，为空时显示所有乘务员
        
        Returns:
            tuple: (data, error_message)
        """
        try:
            if staff_id:
                result = db.call_proc('sp_daily_staff_report', (report_date, staff_id))
            else:
                result = db.call_proc('sp_daily_sales_report', (report_date,))

            if result:
                data = [
                    [
                        str(row['salesperson_id']),
                        str(row['salesperson_name']),
                        str(row['total_orders']),
                        f"${float(row['booking_revenue'] or 0):.2f}",
                        f"${float(row['refund_amount'] or 0):.2f}"
                    ]
                    for row in result
                ]
                return data, None
                
            return [], "No data found"
            
        except Exception as e:
            return None, str(e)
