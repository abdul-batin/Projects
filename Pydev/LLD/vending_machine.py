from abc import abstractmethod

class State():
    @abstractmethod
    def insert_coin(self,vm,amount):
        pass

    @abstractmethod
    def select_item(self,item):
        pass

    @abstractmethod
    def dispense_item(self,item):
        pass
    
    @abstractmethod
    def refund(self):
        pass


class IdleState(State):
    def insert_coin(self,vm,amount):
        #vm = vendingmachine object

        vm.insert_amount(amount)
        vm.set_state(HasMoneyState())

    def select_item(self,vm,item_code):
        print("Insert coin first.")
    
class HasMoneyState(State):
    def insert_coin(self):
        print("Coin already inserted.")
    
    def select_item(self,vm,item):
        item = vm.get_item(item)
        if item is None:
            print("Invalid item selected.")
            return

        vm.set_state(DispensingState())

class DispensingState(State):
    def insert_coin(self):
        print("Please wait, dispensing item.")
    
    def select_item(self):
        print("Please wait, dispensing item.")

    def dispense_item(self,vm,item):
        vm.dispense(item)
        vm.set_state(IdleState())

class Refund(State):
    def insert_coin(self):
        print("Transaction cancelled. Please collect your refund.")
    
    def select_item(self):
        print("Transaction cancelled. Please collect your refund.")

    def refund(self,vm):
        vm.refund_amount()
        vm.set_state(IdleState())

class VendingMachine():
    def __init__(self,inventory):
        self.state = IdleState()
        self.inventory = inventory
        self.amount = 0
    
    def set_state(self,state):
        self.state = state
        return self.state
    
    def insert_amount(self,amount):
        self.amount += amount
    
    def get_item(self,item_code):
        item = self.inventory.get(item_code,None)

        if item is None or item['qty'] <=0 or item['price']>self.amount:
            return None
        
        self.amount -= item['price']
        return item
    
    def dispense(self,item):
        item['qty'] -= 1
        print(f"Dispensing {item['name']}. Please collect your item.")
        self.inventory[item] = item

    def refund_amount(self):
        if self.amount > 0:
            print(f"Refunding amount: {self.amount}")
            self.amount = 0
            return self.amount
        print("No amount to refund.")

if __name__ == '__main__':
    inventory = {
        'A1': {'name': 'Soda', 'price': 150, 'qty': 10},
        'B2': {'name': 'Chips', 'price': 100, 'qty': 5},
        'C3': {'name': 'Candy', 'price': 75, 'qty': 20}
    }

    vm = VendingMachine(inventory)

    vm.state.insert_coin(vm,200)
    vm.state.select_item(vm,'A1')
    vm.state.dispense_item(vm,inventory['A1'])

    vm.state.insert_coin(vm,50)
    vm.state.select_item(vm,'B2')
    vm.state.refund(vm)