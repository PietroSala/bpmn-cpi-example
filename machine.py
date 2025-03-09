
import random

class Machine:
    """
    Class representing a manufacturing machine that can process materials,
    undergo maintenance, and produce output.
    """
    def __init__(self, 
                 name,
                 processing_times={"full": 3, "half": 2, "third": 1},
                 success_probabilities={
                     "full": {"full": 0.7, "half": 0.05, "third": 0.2, "none": 0.05},
                     "half": {"half": 0.8, "third": 0.15, "none": 0.05},
                     "third": {"third": 0.85, "none": 0.15}
                 },
                 maintenance_effect={
                     "full": {"full": 0.75, "half": 0.15, "third": 0.05, "none": 0.05},
                     "half": {"half": 0.85, "third": 0.10, "none": 0.05},
                     "third": {"third": 0.9, "none": 0.1}
                 },
                 maintenance_time=2,
                 maintenance_operator_cost=1):
        """
        Initialize a machine with specific processing characteristics.
        
        Args:
            name: Identifier for the machine
            processing_times: Dictionary mapping batch size to processing time
            success_probabilities: Nested dictionary of success probabilities by batch size
            maintenance_effect: Improved probabilities after maintenance
            maintenance_time: Time units required for maintenance
            maintenance_operator_cost: Cost in operator time for maintenance
        """
        self.name = name
        self.processing_times = processing_times
        self.success_probabilities = success_probabilities
        self.maintenance_effect = maintenance_effect
        self.maintenance_time = maintenance_time
        self.maintenance_operator_cost = maintenance_operator_cost
        
        # State tracking
        self.state = "idle"  # idle, processing, maintenance
        self.current_batch_size = None
        self.time_remaining = 0
        self.stored_output = 0
        self.source_machine = None
        self.raw_material_consumed = 0
        self.maintenance_active = False
        self.total_operator_time = 0
        
    def set_source_machine(self, machine):
        """Link this machine to a source machine for materials"""
        self.source_machine = machine
    
    def retrieve_quantity(self, max_quantity):
        """
        Retrieve up to max_quantity from this machine's stored output.
        Returns the actual quantity retrieved.
        """
        quantity = min(max_quantity, self.stored_output)
        self.stored_output -= quantity
        return quantity
    
    def request_maintenance(self):
        """
        Attempt to start maintenance if the machine is idle.
        Returns True if maintenance started, False otherwise.
        """
        if self.state != "idle":
            return False
            
        # Start maintenance
        self.state = "maintenance"
        self.time_remaining = self.maintenance_time
        self.total_operator_time += self.maintenance_operator_cost
        return True
    
    def request_processing(self, batch_size="full"):
        """
        Attempt to start processing a batch of the specified size.
        Returns True if processing started, False otherwise.
        
        Args:
            batch_size: "full", "half", or "third"
        """
        if self.state != "idle":
            return False
            
        if batch_size not in ["full", "half", "third"]:
            raise ValueError(f"Invalid batch size: {batch_size}")
        
        # Determine raw material needs
        raw_material_needed = {"full": 1.0, "half": 0.5, "third": 1/3}[batch_size]
        
        # Check if source machine has enough material (if there is a source)
        if self.source_machine:
            available = self.source_machine.retrieve_quantity(raw_material_needed)
            if available < raw_material_needed:
                return False
        else:
            # M1 always has raw material available
            self.raw_material_consumed += raw_material_needed
        
        # Start processing
        self.state = "processing"
        self.current_batch_size = batch_size
        self.time_remaining = self.processing_times[batch_size]
        return True
    
    def step(self):
        """
        Advance the machine's state by one time unit.
        Returns True if the machine completed a process during this step.
        """
        completed = False
        
        if self.state == "processing":
            self.time_remaining -= 1
            
            if self.time_remaining <= 0:
                # Processing complete, determine outcome
                probabilities = self.maintenance_effect[self.current_batch_size] if self.maintenance_active else self.success_probabilities[self.current_batch_size]
                
                outcomes = list(probabilities.keys())
                probs = list(probabilities.values())
                
                # Select outcome based on probabilities
                outcome = random.choices(outcomes, weights=probs, k=1)[0]
                
                # Add output based on outcome
                if outcome != "none":
                    output_quantity = {"full": 1.0, "half": 0.5, "third": 1/3}[outcome]
                    self.stored_output += output_quantity
                
                # Reset state
                self.state = "idle"
                self.current_batch_size = None
                completed = True
                
        elif self.state == "maintenance":
            self.time_remaining -= 1
            
            if self.time_remaining <= 0:
                # Maintenance complete
                self.maintenance_active = True
                self.state = "idle"
                completed = True
        
        return completed
    
    def get_state(self):
        """Return the current state of the machine"""
        return {
            "name": self.name,
            "state": self.state,
            "current_batch_size": self.current_batch_size,
            "time_remaining": self.time_remaining,
            "stored_output": self.stored_output,
            "raw_material_consumed": self.raw_material_consumed,
            "maintenance_active": self.maintenance_active,
            "total_operator_time": self.total_operator_time
        }
    
    def is_idle(self):
        """Check if the machine is idle"""
        return self.state == "idle"
    
    def reset(self):
        """Reset the machine to its initial state"""
        self.state = "idle"
        self.current_batch_size = None
        self.time_remaining = 0
        self.stored_output = 0
        self.raw_material_consumed = 0
        self.maintenance_active = False
        self.total_operator_time = 0