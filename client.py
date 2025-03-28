import random

class Client:
    # The client is the one who places the order
    
    def __init__(self, priority_distribution={"low": 0.4, "medium": 0.5, "high": 0.1}, 
                 order_penalties={"low": (20, 5, 1), "medium": (15, 10, 2), "high": (10, 15, 1)}):
        """
        Initialize a client object.
        
        Args:
            priority_distribution: Distribution of order priorities (probabilities must sum to 1)
            order_penalties: Dictionary mapping priorities to tuples of (time_limit, in_time_payment, out_of_time_payment)
        """
        self.state = "idle"
        self.priority_distribution = priority_distribution
        self.order_penalties = order_penalties
        self.time_passed = 0
        self.order_quantity = 0
        self.current_payment = 0
        self.current_priority = None
        self.time_limit = None
        self.in_time_payment = None
        self.out_of_time_payment = None
    
    def place_order(self):
        """
        Place a new order with priority selected according to the distribution.
        Returns the selected priority.
        """
        if self.state != "idle":
            raise ValueError("Cannot place an order when not in idle state")
        
        # Select a priority based on the probability distribution
        rand_val = random.random()
        cumulative_prob = 0
        
        for priority, prob in self.priority_distribution.items():
            cumulative_prob += prob
            if rand_val <= cumulative_prob:
                self.current_priority = priority
                break
                
        # Set order parameters based on priority
        self.time_limit, self.in_time_payment, self.out_of_time_payment = self.order_penalties[self.current_priority]
        
        # Update state
        self.state = "order_placed"
        self.time_passed = 0
        self.order_quantity = 0
        self.current_payment = 0
        
        return self.current_priority
    
    def quantity_shipped(self, quantity):
        """
        Record quantity shipped and calculate payment.
        
        Args:
            quantity: Amount shipped (0 to 1, where 1 is full order)
        
        Returns:
            Payment generated by this shipment
        """
        if self.state not in ["order_placed", "wait_for_completion"]:
            raise ValueError("Cannot receive shipment when no order is placed")
        
        if quantity <= 0 or self.order_quantity + quantity > 1:
            raise ValueError(f"Invalid quantity: {quantity}. Current total: {self.order_quantity}")
        
        # Calculate payment based on timing
        if self.time_passed <= self.time_limit:
            # In-time payment
            payment = quantity * self.in_time_payment
        else:
            # Late payment
            payment = quantity * self.out_of_time_payment
        
        # Update total quantity and payment
        self.order_quantity += quantity
        self.current_payment += payment
        
        # Update state if order is complete
        if self.order_quantity >= 1:
            self.state = "completed"
        else:
            self.state = "wait_for_completion"
            
        return payment
    
    def step_time(self):
        """
        Advances time by one unit.
        Returns True if still within time limit, False if exceeded.
        """
        if self.state in ["order_placed", "wait_for_completion"]:
            self.time_passed += 1
            return self.time_passed <= self.time_limit
        return False
    
    def get_state(self):
        """
        Returns the current state and details of the client.
        """
        return {
            "state": self.state,
            "priority": self.current_priority,
            "time_passed": self.time_passed,
            "time_limit": self.time_limit,
            "order_quantity": self.order_quantity,
            "current_payment": self.current_payment,
            "in_time": self.time_passed <= self.time_limit if self.time_limit else None
        }
    
    def reset(self):
        """
        Reset the client to the initial state.
        """
        self.state = "idle"
        self.time_passed = 0
        self.order_quantity = 0
        self.current_payment = 0
        self.current_priority = None
        self.time_limit = None
        self.in_time_payment = None
        self.out_of_time_payment = None