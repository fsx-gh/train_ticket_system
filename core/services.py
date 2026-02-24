from db import db  # Import the singleton database instance
from db.models import Train, Station, Price
from mysql.connector import Error
from utils.hash_utils import hash_password

class TrainService:
    @staticmethod
    def get_train_route(train_number, departure_date=None):
        """获取列车路线信息

        Args:
            train_number (str): 列车号
            departure_date (str, optional): 发车日期，格式YYYY-MM-DD
    
        Returns:
            tuple: (route_data, error_message)
                route_data: 包含以下字段的列表:
                    - train_number: 列车号
                    - start_date: 发车日期
                    - station_name: 站点名称
                    - station_code: 站点代码
                    - arrival_time: 到达时间
                    - departure_time: 出发时间
                    - stop_type: 站点类型
                    - stop_order: 站点顺序
                    - sold_tickets: 已售票数
        """
        try:
            result = db.call_proc('sp_get_train_route', (train_number, departure_date))
            
            if not result:
                error_msg = "No route information found"
                if departure_date:
                    error_msg += f" for date {departure_date}"
                return [], error_msg

            route_data = []
            for stop in result:
                # Check if stop is a tuple instead of a dictionary
                if isinstance(stop, tuple):
                    # Assuming the columns are returned in this order - adjust indexes if needed
                    train_number_idx = 0
                    start_date_idx = 1
                    station_name_idx = 2
                    station_code_idx = 3
                    arrival_time_idx = 4
                    departure_time_idx = 5
                    stop_type_idx = 6
                    stop_order_idx = 7
                    sold_tickets_idx = 8
                    
                    arrival_time = stop[arrival_time_idx].strftime('%Y-%m-%d %H:%M:%S') if stop[arrival_time_idx] else '-'
                    departure_time = stop[departure_time_idx].strftime('%Y-%m-%d %H:%M:%S') if stop[departure_time_idx] else '-'
                    
                    route_data.append([
                        stop[train_number_idx],
                        stop[start_date_idx].strftime('%Y-%m-%d'),
                        stop[station_name_idx],
                        stop[station_code_idx] or '-',
                        arrival_time,
                        departure_time,
                        stop[stop_type_idx],
                        stop[stop_order_idx],
                        stop[sold_tickets_idx]
                    ])
                else:
                    # Original dictionary-based code
                    arrival_time = stop['arrival_time'].strftime('%Y-%m-%d %H:%M:%S') if stop['arrival_time'] else '-'
                    departure_time = stop['departure_time'].strftime('%Y-%m-%d %H:%M:%S') if stop['departure_time'] else '-'
                    
                    route_data.append([
                        stop['train_number'],
                        stop['start_date'].strftime('%Y-%m-%d'),
                        stop['station_name'],
                        stop['station_code'] or '-',
                        arrival_time,
                        departure_time,
                        stop['stop_type'],
                        stop['stop_order'],
                        stop['sold_tickets']
                    ])

            return route_data, None
            
        except Exception as e:
            return [], f"Error getting train route: {str(e)}"

    @staticmethod
    def list_all_trains():
        trains = Train.find_all()
        train_data = []
        
        if not trains:
            return train_data, "No trains found."

        for t in trains:
            dep_station = Station.find_one({'station_id': t.get('departure_station_id')})
            arr_station = Station.find_one({'station_id': t.get('arrival_station_id')})
            train_data.append([
                str(t.get('train_number', '')),
                str(t.get('train_type', '')),
                str(t.get('total_seats', '0')),
                dep_station.get('station_name', 'Unknown') if dep_station else 'Unknown',
                arr_station.get('station_name', 'Unknown') if arr_station else 'Unknown'
            ])
        return train_data, None

    @staticmethod
    def get_train_schedules():
        """获取列车时刻表信息
        
        Returns:
            tuple: (data, error_message) - 成功返回(data, None)，失败返回(None, error_message)
        """
        try:
            query = """
            SELECT * FROM TrainSchedulesView 
            """
            result = db.execute_query(query, fetch_all=True)
            
            if not result:
                return [], "No train schedules found"
                
            data = []
            for row in result:
                data.append([
                    row['train_number'],
                    row['train_type'],
                    row['departure_station'],
                    row['arrival_station'],
                    row['stopover_station'] or 'N/A',
                    row['stop_order'] or 'N/A',
                    row['seats'] or 'N/A',
                    row['arrival_time'] or 'N/A',
                    row['departure_time'] or 'N/A'
                ])
            return data, None
            
        except Exception as e:
            return [], f"Error fetching train schedules: {str(e)}"

class StationService:
    @staticmethod
    def list_all_stations():
        stations = Station.find_all()
        station_data = []
        
        if not stations:
            return station_data, "No stations found."

        for s in stations:
            station_data.append([
                str(s.get('station_id', '')),
                str(s.get('station_name', '')),
                str(s.get('station_code', 'N/A'))
            ])
        return station_data, None

class TicketService:
    @staticmethod
    def search_available_tickets(dep_station_name, arr_station_name, departure_date=None):
        """
        查询所有经过指定起点和终点站点的列车信息，按列车和发车日期分组

        参数:
            dep_station_name: 起点站名
            arr_station_name: 终点站名
            departure_date: 可选，指定出发日期 (格式: YYYY-MM-DD)

        返回:
            包含符合条件的列车信息的列表，以及错误信息(如果有)
        """
        # Step 1: 验证车站是否存在
        dep_station = Station.find_one({'station_name': dep_station_name})
        arr_station = Station.find_one({'station_name': arr_station_name})
        if not dep_station or not arr_station:
            return [], "Departure or arrival station not found."
        
        # Step 2: 构建日期过滤条件
        date_filter = ""
        params = []
        if departure_date:
            date_filter = "AND DATE(s1.departure_time) = %s"
            params.append(departure_date)
        
        # Step 3: 查询所有经过起点站和终点站的列车，并获取价格信息
        route_query = """
        SELECT 
            s1.train_number,
            s1.start_date,
            s1.departure_time,
            s2.arrival_time,
            MIN(s3.seats) as min_seats,
            t.train_type,
            p.price
        FROM 
            Stopovers s1
            JOIN Stopovers s2 ON s1.train_number = s2.train_number AND s1.start_date = s2.start_date
            JOIN Stopovers s3 ON s1.train_number = s3.train_number AND s1.start_date = s3.start_date
            JOIN Trains t ON s1.train_number = t.train_number
            JOIN Prices p ON s1.train_number = p.train_number 
                AND s1.station_id = p.departure_station_id
                AND s2.station_id = p.arrival_station_id
        WHERE 
            s1.station_id = %s
            AND s2.station_id = %s
            AND s1.stop_order < s2.stop_order
            AND s3.stop_order >= s1.stop_order
            AND s3.stop_order < s2.stop_order
            """ + date_filter + """
        GROUP BY
            s1.train_number, s1.start_date, s1.departure_time, s2.arrival_time, t.train_type, p.price
        ORDER BY 
            s1.departure_time
        """
    
        params = [dep_station.get('station_id'), arr_station.get('station_id')] + params
    
        train_results = db.execute_query(route_query, tuple(params), fetch_all=True)
    
        if not train_results:
            return [], "No trains found passing through both stations in the correct order."
    
        # Step 4: 构建返回结果
        train_data = []
    
        for train in train_results:
            train_info = [
                train['train_number'],
                train['start_date'].strftime('%Y-%m-%d'),
                dep_station_name,
                train['departure_time'].strftime('%Y-%m-%d %H:%M:%S') if train['departure_time'] else '-',
                arr_station_name,
                train['arrival_time'].strftime('%Y-%m-%d %H:%M:%S') if train['arrival_time'] else '-',
                float(train['price']),
                train['min_seats'],
                train['train_type']
            ]
        
            train_data.append(train_info)
    
        return train_data, None

class OrderService:
    @staticmethod
    def create_order(train_number, start_date, departure_station, arrival_station, 
                    price, customer_name, customer_id_card):
        """创建订单"""
        try:
            # 验证客户信息
            customer_query = """
            SELECT * FROM Customers 
            WHERE name = %s AND id_card = %s
            """
            customer = db.execute_query(
                customer_query, 
                (customer_name, customer_id_card),
                fetch_one=True
            )
            
            if not customer:
                return False, "Customer information not found or incorrect."
            
            # 查询出发站和到达站的ID
            dep_station_query = "SELECT station_id FROM Stations WHERE station_name = %s"
            arr_station_query = "SELECT station_id FROM Stations WHERE station_name = %s"
            
            dep_station = db.execute_query(dep_station_query, (departure_station,), fetch_one=True)
            arr_station = db.execute_query(arr_station_query, (arrival_station,), fetch_one=True)
            
            if not dep_station or not arr_station:
                return False, "Departure or arrival station not found."
            
            # 生成订单号 (年月日时分秒+4位随机数)
            import datetime
            import random
            order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + \
                      str(random.randint(1000, 9999))
            
            # 插入订单
            order_query = """
            INSERT INTO SalesOrders (
                order_id, train_number, start_date,
                departure_station_id, arrival_station_id,
                price, customer_id, 
                operation_type, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, 
                'Booking', 'Ready'
            )
            """
            
            # 执行订单插入
            db.execute_query(
                order_query,
                (order_id, train_number, start_date,
                 dep_station['station_id'], arr_station['station_id'],
                 price, customer_id_card)
            )
            
            return True, f"Order created successfully! Order ID: {order_id}"
            
        except Exception as e:
            return False, f"Failed to create order: {str(e)}"
    
    @staticmethod
    def get_orders_by_passenger(name, id_card):
        """根据乘客信息查询订单"""
        try:
            print(f"Querying orders for passenger {name} with ID: {id_card}")
            query = """
                SELECT 
                    so.order_id,
                    so.train_number,
                    t.train_type,
                    dep.station_name AS departure_station,
                    arr.station_name AS arrival_station,
                    so.price,
                    c.name AS customer_name,
                    c.phone AS customer_phone,
                    so.operation_type,
                    so.operation_time,
                    so.status
                FROM SalesOrders so
                JOIN Trains t ON so.train_number = t.train_number
                JOIN Stations dep ON so.departure_station_id = dep.station_id
                JOIN Stations arr ON so.arrival_station_id = arr.station_id
                JOIN Customers c ON so.customer_id = c.id_card
                WHERE c.name = %s AND c.id_card = %s
                ORDER BY so.operation_time DESC
            """
            
            orders = db.execute_query(query, (name, id_card), fetch_all=True)

            if not orders:
                return [], "No orders found for this passenger"

            orders_data = []
            for order in orders:
                orders_data.append([
                    order['order_id'],
                    order['train_number'],
                    order['train_type'],
                    order['departure_station'],
                    order['arrival_station'],
                    f"${float(order['price']):.2f}",
                    order['customer_name'],
                    order['customer_phone'],
                    order['operation_type'],
                    order['operation_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    order['status']
                ])
                
            return orders_data, None
            
        except Exception as e:
            return [], f"Error querying orders: {str(e)}"
    
    @staticmethod
    def cancel_order(order_id):
        """取消订单"""
        try:
            # 检查订单状态
            check_query = """
            SELECT status FROM SalesOrders 
            WHERE order_id = %s
            """
            order = db.execute_query(check_query, (order_id,), fetch_one=True)
            
            if not order:
                return False, "Order not found"
            
            if order['status'] != 'Ready':
                return False, "Only orders in Ready status can be cancelled"
            
            # 更新订单状态
            update_query = """
            UPDATE SalesOrders 
            SET status = 'Cancelled'
            WHERE order_id = %s
            """
            db.execute_query(update_query, (order_id,))
            
            return True, "Order cancelled successfully"
            
        except Exception as e:
            return False, f"Failed to cancel order: {str(e)}"

    @staticmethod
    def request_refund(order_id):
        """申请退款"""
        try:
            # 检查订单状态
            check_query = """
            SELECT status FROM SalesOrders 
            WHERE order_id = %s
            """
            order = db.execute_query(check_query, (order_id,), fetch_one=True)
            
            if not order:
                return False, "Order not found"
            
            if order['status'] != 'Success':
                return False, "Only successful orders can request refund"
            
            # 更新订单状态为待退款
            update_query = """
            UPDATE SalesOrders 
            SET status = 'RefundPending',
                operation_type = 'Refund'
            WHERE order_id = %s
            """
            db.execute_query(update_query, (order_id,))
            
            return True, "Refund request submitted successfully"
            
        except Exception as e:
            return False, f"Failed to request refund: {str(e)}"

    @staticmethod
    def get_pending_orders():
        """获取待处理订单"""
        try:
            query = """
                SELECT * FROM PendingOrdersView
            """
            orders = db.execute_query(query, fetch_all=True)

            if not orders:
                return [], "No pending orders found"

            orders_data = []
            for order in orders:
                orders_data.append([
                    order['order_id'],
                    order['train_number'],
                    order['train_type'],
                    order['departure_station'],
                    order['arrival_station'],
                    f"${float(order['price']):.2f}",
                    order['customer_name'],
                    order['customer_phone'],
                    order['operation_type'],
                    order['operation_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    order['status']
                ])
                
            return orders_data, None
            
        except Exception as e:
            return [], f"Error querying orders: {str(e)}"

    @staticmethod
    def process_order(order_id, approve=True, salesperson_id=None):
        """处理订单（确认或拒绝）
        
        Args:
            order_id (str): 订单ID
            approve (bool): True为批准，False为拒绝
            salesperson_id (str): 处理订单的乘务员ID
        """
        try:
            # 检查订单状态和信息
            check_query = """
            SELECT so.status, so.operation_type, so.price, 
                   so.train_number, so.start_date, 
                   dep.station_name AS departure_station, 
                   arr.station_name AS arrival_station,
                   so.departure_station_id,
                   so.arrival_station_id
            FROM SalesOrders so
            JOIN Stations dep ON so.departure_station_id = dep.station_id
            JOIN Stations arr ON so.arrival_station_id = arr.station_id 
            WHERE so.order_id = %s
            """
            order = db.execute_query(check_query, (order_id,), fetch_one=True)
            
            if not order:
                return False, "Order not found"
            
            if order['status'] not in ('Ready', 'RefundPending'):
                return False, "Order cannot be processed in current status"
            
            # 确定新状态和操作类型
            original_status = order['status']
            operation_type = 'Approve' if approve else 'Reject'
            
            # 如果是批准新订单，需要检查余票
            if approve and original_status == 'Ready':
                # 检查所有经过站点是否有余票
                check_seats_query = """
                SELECT MIN(s.seats) as min_seats
                FROM Stopovers s
                WHERE s.train_number = %s
                AND s.start_date = %s
                AND s.stop_order >= (
                    SELECT stop_order 
                    FROM Stopovers s2 
                    WHERE s2.train_number = %s
                    AND s2.start_date = %s
                    AND s2.station_id = %s
                )
                AND s.stop_order < (
                    SELECT stop_order 
                    FROM Stopovers s3 
                    WHERE s3.train_number = %s
                    AND s3.start_date = %s
                    AND s3.station_id = %s
                )
                """
                
                seats_result = db.execute_query(
                    check_seats_query, 
                    (order['train_number'], order['start_date'],
                     order['train_number'], order['start_date'], order['departure_station_id'],
                     order['train_number'], order['start_date'], order['arrival_station_id']),
                    fetch_one=True
                )
                
                if not seats_result or seats_result['min_seats'] <= 0:
                    return False, "No available seats for this route"
    
            if original_status == 'Ready':
                new_status = 'Success' if approve else 'Cancelled'
            else:
                new_status = 'Refunded' if approve else 'Success'
            
            # 生成操作备注
            remarks = None
            if original_status == 'Ready':
                remarks = f"Order {'approved' if approve else 'rejected'} by salesperson"
            else:
                remarks = f"Refund request {'approved' if approve else 'rejected'} by salesperson"
            
            # 更新订单状态
            update_query = """
            UPDATE SalesOrders 
            SET status = %s
            WHERE order_id = %s
            """
            db.execute_query(update_query, (new_status, order_id))
            
            # 记录操作
            success = OrderService.record_operation(
                order_id=order_id,
                salesperson_id=salesperson_id,
                operation_type=operation_type,
                original_status=original_status,
                new_status=new_status,
                price=float(order['price']),
                remarks=remarks
            )
            
            if not success:
                return False, "Operation recorded but failed to log the operation"
            
            return True, f"Order {new_status.lower()} successfully"
            
        except Exception as e:
            return False, f"Failed to process order: {str(e)}"
    
    @staticmethod
    def record_operation(order_id, salesperson_id, operation_type, 
                        original_status, new_status, price=None, remarks=None):
        """记录订单操作历史
        
        Args:
            order_id (str): 订单ID
            salesperson_id (str): 操作人员ID
            operation_type (str): 操作类型 ('Approve', 'Reject')
            original_status (str): 原始状态
            new_status (str): 新状态
            price (decimal, optional): 不再使用，保留参数以兼容旧代码
            remarks (str, optional): 备注说明

        Returns:
            bool: 操作是否成功
        """
        try:
            query = """
                INSERT INTO OrderOperations (
                    order_id,
                    salesperson_id,
                    operation_type,
                    original_status,
                    new_status,
                    operation_time,
                    remarks
                ) VALUES (
                    %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s
                )
            """
            db.execute_query(
                query,
                (order_id, salesperson_id, operation_type, 
                original_status, new_status, remarks)
            )
            return True
        except Exception as e:
            print(f"Error recording operation: {e}")
            return False

class SalespersonService:
    @staticmethod
    def verify_credentials(salesperson_id, password):
        """验证乘务员凭据"""
        try:
            query = """
            SELECT salesperson_id, salesperson_name, role
            FROM Salespersons 
            WHERE salesperson_id = %s AND password = %s
            """

            hashed_password = hash_password(password)
            result = db.execute_query(query, (salesperson_id, hashed_password), fetch_one=True)

            if result:
                return True, result
            return False, "Invalid credentials"
            
        except Exception as e:
            return False, f"Error verifying credentials: {str(e)}"    
    @staticmethod
    def get_daily_sales_report(report_date, staff_id=None):
        """获取指定日期的销售报表
        
        Args:
            report_date (str): 报表日期，格式为YYYY-MM-DD
            staff_id (str, optional): 指定乘务员ID，为空时显示所有乘务员
            
        Returns:
            tuple: (data, error_message)
        """
        try:
            if staff_id:
                result = db.call_proc('sp_daily_staff_report', (report_date, staff_id))
            else:
                result = db.call_proc('sp_daily_sales_report', (report_date,))

            if result:
                data = []
                for row in result:
                    # Check if the result is a tuple or a dictionary
                    if isinstance(row, tuple):
                        # Assuming the stored procedure returns columns in this order
                        # Adjust the indices based on the actual order of columns returned
                        salesperson_id = str(row[0]) if row[0] is not None else ''
                        salesperson_name = str(row[1]) if row[1] is not None else ''
                        total_orders = str(row[2]) if row[2] is not None else '0'
                        booking_revenue = float(row[3] or 0)
                        refund_amount = float(row[4] or 0)
                        
                        data.append([
                            salesperson_id,
                            salesperson_name,
                            total_orders,
                            f"${booking_revenue:.2f}",
                            f"${refund_amount:.2f}"
                        ])
                    else:
                        # Dictionary-based access
                        data.append([
                            str(row.get('salesperson_id', '')),
                            str(row.get('salesperson_name', '')),
                            str(row.get('total_orders', '0')),
                            f"${float(row.get('booking_revenue') or 0):.2f}",
                            f"${float(row.get('refund_amount') or 0):.2f}"
                        ])
                return data, None
                
            return [], "No data found"
            
        except Exception as e:
            return None, str(e)
