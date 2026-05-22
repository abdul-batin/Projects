from enum import Enum
from typing import List

class BookingStatus(Enum):
    REQUESTED = 1
    ACCEPTED = 2
    IN_PROGRESS = 3
    COMPLETED = 4
    CANCELLED = 5

class PaymentStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3

class User():
    def __init__(self,user_id,name,contact):
        self.user_id = user_id
        self.name = name
        self.contact = contact
        self.status = None
    
    def request_ride(self,source,destination):
        pass
        
class Driver():
    def __init__(self,driver_id,name,contact):
        self.driver_id = driver_id
        self.name = name
        self.contact = contact
        self.is_available = True


class Ride():
    def __init__(self,user:User,driver:Driver,source,destination):
        self.ride_id = uuid.uuid4()
        self.user = user
        self.driver = driver
        self.source = source
        self.destination = destination
        self.status = BookingStatus.REQUESTED
        self.price = None
    
    def start_ride(self):
        pass

    def end_ride(self):
        pass

    def get_price(self):
        pass

    def set_price(self):
        pass

    def update_ride_status(self,status:BookingStatus):
        self.status = status
    
class RideMatchingStrategy():
    def __init__(self,user:User,drivers:List[Driver]):
        self.user = user
        self.drivers = drivers
    
    def match_drivers(self):
        self.drivers.sort(key = lambda x: x.location)
        for d in self.drivers:
            if d.is_available:
                return d
        return None

class PaymentStrategy():
    def __init__(self,payment_id,ride:Ride,amount):
        self.payment_id = payment_id
        self.ride = ride
        self.amount = amount
        self.is_paid = False
    
    def process_payment(self):
        print("Processing payment...")
        print("Payment successful.")
        

    def update_payment_status(self,status:PaymentStatus):
        self.is_paid = status == PaymentStatus.COMPLETED
        pass


class CabService():
    def __init__(self):
        self.users = {}
        self.drivers = {}
        self.vehicles = {}
        self.rides = {}

    def register_user(self,user:User):
        pass
    def register_driver(self,driver:Driver,vehicle:Vehicle):
        pass

    def book_ride(self,user:User,source,destination) ->Ride:
        #logic to match available driver and vehicle

        driver = RideMatchingStrategy(user,list(self.drivers.values())).match_drivers()

        if driver is None:
            return None
        
        ride = Ride(user,driver,source,destination)
        driver.is_available = False
        ride.update_ride_status(BookingStatus.ACCEPTED)

    def start_ride(self,ride:Ride):
        ride.update_ride_status(BookingStatus.IN_PROGRESS)

    def end_ride(self,ride:Ride):
        ride.update_ride_status(BookingStatus.COMPLETED)

        payment = PaymentStrategy(uuid.uuid4(),ride,ride.get_price())
        payment.process_payment()
        payment.update_payment_status(PaymentStatus.COMPLETED)
        ride.driver.is_available = True
        
