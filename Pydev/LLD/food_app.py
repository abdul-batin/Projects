from enum import Enum
from typing import List

class OrderStatus(Enum):
    CREATED = 1
    ACCEPTED = 2
    PREPARING = 3
    DISPATCHED = 4
    DELIVERED = 5
    
class Item():
    def __init__(self,name,price,qty):
        self.name = name
        self.price = price
        self.qty = qty

    def get_price(self):
        return self.price
    
    def get_qty(self):
        return self.qty

class Menu():
    def __init__(self,restaurant_id):
        self.items = {}
        self.restaurant_id = restaurant_id
    
    def add_item(self,item_code,item:Item):
        self.items[item_code] = item
    
    def remove_item(self,item_code):
        if item_code in self.items:
            del self.items[item_code]

def Cart():
    def __init__(self):
        self.items = []
        self.total_price = 0

    def add_item(self,item:Item):
        self.items.append(item)
        self.total_price += item.get_price()
    
    def remove_item(self,item:Item):
        if item in self.items:
            self.items.remove(item)
            self.total_price -= item.get_price()

    def reset_cart(self):
        self.items = []
        self.total_price = 0

        
class Restaurant():
    def __init__(self,id,menu:Menu):
        self.menu = menu
        self.id = id
        self.cart = []
        self.is_open = True
    
    def is_open(self):
        return self.is_open
    
    def get_menu(self):
        return self.menu
    
def Order():
    def __init__(self,order_id,total_price,restaurant:Restaurant,items:List[Item]):
        self.order_id = order_id
        self.restaurant = restaurant
        self.items = items
        self.status = OrderStatus.CREATED
        self.total_price = total_price

    def update_status(self,status:OrderStatus):
        self.status = status
    
