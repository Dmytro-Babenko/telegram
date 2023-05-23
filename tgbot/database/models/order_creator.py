from tgbot.database.models.fields import OrderDate, OrderType, Subject, University, Client, OrderTheme, OrderVar
    
class OrderDesc:

    def __init__(
            self, type_order: OrderType, subject: Subject, 
            date_time:OrderDate, t_or_v:OrderTheme|OrderVar, 
            university:University=None) -> None:
        self.type_order = type_order
        self.subject = subject
        self.datetime = date_time
        self.t_or_v = t_or_v
        self.university = university
        self.elements = (self.type_order, self.subject, self.datetime, self.university, self.t_or_v)

    def __str__(self):
        output = '\n'.join(f'{el._category_name}: {el}' for el in self.elements)
        return output 
    
    def get_values_lst(self):
        return [el.get_key() for el in self.elements]

class Order:

    def __init__(self, client:Client, desc:OrderDesc, id_=None, task_files:Files=None, solutions:Solutions=None, **kwargs) -> None:
        self.order_id = id_
        self.client = client
        self.desc = desc
        self.task_files = task_files
        self.solutions = solutions      

    def form_description(self):
        return str(self.desc)

    def insert_to_db(self, cur):
        cur.row_factory = lambda cursor, row: row[0]
        insert_order = """INSERT INTO orders (client_id, type_id, subject_id, order_date, univ_id, theme_or_variant)
                        VALUES (?, ?, ?, ?, ?, ?) """
        values = (self.client.telegram_id, *self.desc.get_values_lst())
        cur.execute(insert_order, values)
        self.order_id = cur.lastrowid

        self.task_files.insert_to_db(self.order_id, cur, 'task')
        self.solutions.insert_to_db(self.order_id, cur)

    @staticmethod
    def select_from_db(order_id, cur):
        
        sql_select_order = """SELECT client_id, type_id, subject_id, order_date, univ_id, theme_or_variant 
                            FROM orders
                            WHERE id = ?"""
        
        client_id, type_id, subject_id, order_date, univ_id, t_or_v = cur.execute(sql_select_order,
                                                                                    (order_id,)).fetchone()
        
        order_client = Client.select_from_db(client_id, cur)  
        order_type = OrderType.select_from_db(type_id, cur)
        order_subject = Subject.select_from_db(subject_id, cur)
        order_univ = University.select_from_db(univ_id, cur)
        order_date = OrderDate(order_date)
        t_or_v = OrderVar(t_or_v) if order_type.kind == 'он' else OrderVar(t_or_v)

        desc = OrderDesc(order_type, order_subject, order_date, t_or_v, order_univ)

        task_files = Files()
        task_files.add_from_db(order_id, 'task', cur)

        solutions = Solutions(Files)
        solutions.add_from_db(order_id, cur)    

        order = Order(
            client=order_client,
            order_id=order_id,
            desc=desc,
            task_files=task_files,
            solutions=solutions
        )
      
        return order
    

    
        

    
