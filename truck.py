class Truck:
    """
    Class representing a truck for shipping goods.
    Supports both small and big trucks with different capacities and delivery times.
    """
    def __init__(self, capacity, time_to_deliver, name=None):
        """
        Initialize a truck with specific capacity and delivery time.
        
        Args:
            capacity: Maximum load capacity (small truck: 1/3, big truck: 1.0)
            time_to_deliver: Time units required for a full delivery cycle
                             (loading + delivery + unloading + return)
            name: Optional name identifier for the truck
        """
        self.capacity = capacity
        self.time_to_deliver = time_to_deliver
        self.name = name or f"Truck-{capacity}"
        
        # State tracking
        self.state = "available"  # available, loading, delivering, returning
        self.current_load = 0
        self.time_remaining = 0
        self.client = None
        self.source_machine = None
    
    def set_client(self, client):
        """Link this truck to a client that will receive shipments"""
        self.client = client
        
    def set_machine(self, machine):
        """Link this truck to a machine that will be the source of products"""
        self.source_machine = machine
    
    def request_shipment(self):
        """
        Attempt to start a shipment if the truck is available.
        Returns True if shipment started, False otherwise.
        """
        if self.state != "available":
            return False
            
        if not self.source_machine or not self.client:
            return False
            
        # Retrieve product from the machine (up to capacity)
        retrieved_quantity = self.source_machine.retrieve_quantity(self.capacity)
        
        if retrieved_quantity <= 0:
            return False
            
        # Start shipment
        self.current_load = retrieved_quantity
        self.state = "delivering"
        self.time_remaining = self.time_to_deliver
        return True
    
    def step(self):
        """
        Advance the truck's state by one time unit.
        Returns True if the truck performed a delivery during this step.
        """
        delivery_completed = False
        
        if self.state == "delivering":
            self.time_remaining -= 1
            
            if self.time_remaining <= 0:
                # Delivery complete, transfer goods to client
                if self.client:
                    self.client.quantity_shipped(self.current_load)
                
                # Reset truck state
                self.state = "available"
                self.current_load = 0
                delivery_completed = True
        
        return delivery_completed
    
    def get_state(self):
        """Return the current state of the truck"""
        return {
            "name": self.name,
            "state": self.state,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "time_remaining": self.time_remaining
        }
    
    def is_available(self):
        """Check if the truck is available for a new shipment"""
        return self.state == "available"
    
    def reset(self):
        """Reset the truck to its initial state"""
        self.state = "available"
        self.current_load = 0
        self.time_remaining = 0