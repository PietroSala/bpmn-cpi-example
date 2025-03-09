from truck import Truck
from client import Client
from machine import Machine

class System:
    """
    A fixed system with exactly two machines, two trucks, and one client for 
    manufacturing and delivery simulation. The client places an order at initialization.
    """
    def __init__(self):
        """
        Initialize the system with a fixed configuration:
        - Two machines (M1 and M2)
        - Two trucks (one small, one big)
        - One client who places an order right away
        """
        
        # Create client
        self.client = Client()
        
        # Create machines
        self.m1 = Machine(name="M1")  # First machine
        self.m2 = Machine(name="M2")  # Second machine (connects to M1)
        self.m2.set_source_machine(self.m1)
        
        # Create trucks
        self.small_truck = Truck(capacity=1/3, time_to_deliver=2, name="Small Truck")
        self.big_truck = Truck(capacity=1.0, time_to_deliver=3, name="Big Truck")
        
        # Connect trucks to the final machine and client
        self.small_truck.set_machine(self.m2)
        self.small_truck.set_client(self.client)
        self.big_truck.set_machine(self.m2)
        self.big_truck.set_client(self.client)
        
        # System tracking
        self.time = 0
        self.total_profit = 0
        
        # Place initial order
        self.current_priority = self.client.place_order()
        
        # Store components in lists for easier iteration
        self.machines = [self.m1, self.m2]
        self.trucks = [self.small_truck, self.big_truck]

        self.current_enacted_strategy = 0
        self.m1_processing_full()

    def get_state(self):
        """
        Returns the current state of the system as a tuple.
        
        Values representing quantities are discretized to the set {0/6, 1/6, 2/6, 3/6, 4/6, 5/6, 6/6},
        with intermediate values rounded down to the nearest discrete value.
        
        Returns:
            tuple: (
                client_current_priority,
                quantity_shipped_to_the_client,
                time_to_penalty,
                m1_status,
                m1_stored,
                m1_to_completion,
                m2_status,
                m2_stored,
                m2_to_completion,
                ts_status,
                ts_to_completion,
                tb_status,
                tb_to_completion
            )
        """
        # Helper function to quantize values to multiples of 1/6
        def quantize(value):
            """Convert a value to the nearest lower multiple of 1/6 between 0 and 1"""
            # Ensure value is between 0 and 1
            value = max(0, min(1, value))
            # Convert to sixths (0/6, 1/6, 2/6, ..., 6/6)
            sixths = int(value * 6)
            return sixths / 6
        
        # Client state
        client_state = self.client.get_state()
        client_priority = client_state["priority"] if client_state["priority"] else "none"
        quantity_shipped = quantize(client_state["order_quantity"])
        
        # Calculate time to penalty
        if client_state["state"] in ["order_placed", "wait_for_completion"]:
            time_to_penalty = max(0, client_state["time_limit"] - client_state["time_passed"])
            # If penalty has already started
            if client_state["time_passed"] > client_state["time_limit"]:
                time_to_penalty = -1
        else:
            # No active order
            time_to_penalty = -1
        
        # Machine 1 state
        m1_state = self.m1.get_state()
        if m1_state["state"] == "processing":
            m1_status = f"processing_{m1_state['current_batch_size']}"
            m1_to_completion = m1_state["time_remaining"]
        else:
            m1_status = m1_state["state"]  # idle or maintenance
            m1_to_completion = 0
        m1_stored = quantize(m1_state["stored_output"])
        
        # Machine 2 state
        m2_state = self.m2.get_state()
        if m2_state["state"] == "processing":
            m2_status = f"processing_{m2_state['current_batch_size']}"
            m2_to_completion = m2_state["time_remaining"]
        else:
            m2_status = m2_state["state"]  # idle or maintenance
            m2_to_completion = 0
        m2_stored = quantize(m2_state["stored_output"])
        
        # Small truck state
        ts_state = self.small_truck.get_state()
        if ts_state["state"] == "delivering":
            if ts_state["current_load"] == 0:
                ts_status = "shipping_zero"
            else:
                # Small truck can only carry up to 1/3
                ts_status = "shipping_third"
            ts_to_completion = ts_state["time_remaining"]
        else:
            ts_status = "idle"
            ts_to_completion = 0
        
        # Big truck state
        tb_state = self.big_truck.get_state()
        if tb_state["state"] == "delivering":
            load = quantize(tb_state["current_load"])
            if load == 0:
                tb_status = "shipping_zero"
            elif load <= 1/3:
                tb_status = "shipping_third"
            elif load <= 2/3:
                tb_status = "shipping_half"
            else:
                tb_status = "shipping_full"
            tb_to_completion = tb_state["time_remaining"]
        else:
            tb_status = "idle"
            tb_to_completion = 0
        
        # Construct and return the tuple
        return (
            client_priority,
            quantity_shipped,
            time_to_penalty,
            m1_status,
            m1_stored,
            m1_to_completion,
            m2_status,
            m2_stored,
            m2_to_completion,
            ts_status,
            ts_to_completion,
            tb_status,
            tb_to_completion
        )
    def m1_processing_third(self):
        """
        Request Machine 1 to process a third of a batch.
        Returns the system state regardless of success.
        """
        try:
            self.m1.request_processing(batch_size="third")
        except Exception:
            pass
        return self.get_state()

    def m1_processing_half(self):
        """
        Request Machine 1 to process half of a batch.
        Returns the system state regardless of success.
        """
        try:
            self.m1.request_processing(batch_size="half")
        except Exception:
            pass
        return self.get_state()

    def m1_processing_full(self):
        """
        Request Machine 1 to process a full batch.
        Returns the system state regardless of success.
        """
        try:
            self.m1.request_processing(batch_size="full")
        except Exception:
            pass
        return self.get_state()

    def m1_maintenance(self):
        """
        Request maintenance for Machine 1.
        Returns the system state regardless of success.
        """
        try:
            self.m1.request_maintenance()
        except Exception:
            pass
        return self.get_state()

    def m2_processing_third(self):
        """
        Request Machine 2 to process a third of a batch.
        Returns the system state regardless of success.
        """
        try:
            self.m2.request_processing(batch_size="third")
        except Exception:
            pass
        return self.get_state()

    def m2_processing_half(self):
        """
        Request Machine 2 to process half of a batch.
        Returns the system state regardless of success.
        """
        try:
            self.m2.request_processing(batch_size="half")
        except Exception:
            pass
        return self.get_state()

    def m2_processing_full(self):
        """
        Request Machine 2 to process a full batch.
        Returns the system state regardless of success.
        """
        try:
            self.m2.request_processing(batch_size="full")
        except Exception:
            pass
        return self.get_state()

    def m2_maintenance(self):
        """
        Request maintenance for Machine 2.
        Returns the system state regardless of success.
        """
        try:
            self.m2.request_maintenance()
        except Exception:
            pass
        return self.get_state()

    def small_truck_shipment(self):
        """
        Request the small truck to make a shipment.
        Returns the system state regardless of success.
        """
        try:
            self.small_truck.request_shipment()
        except Exception:
            pass
        return self.get_state()

    def big_truck_shipment(self):
        """
        Request the big truck to make a shipment.
        Returns the system state regardless of success.
        """
        try:
            self.big_truck.request_shipment()
        except Exception:
            pass
        return self.get_state()

    def step(self):
        """
        Advance all components by one time unit.
        Returns the system state after advancement.
        """
        # Step all machines
        for machine in self.machines:
            try:
                machine.step()
            except Exception:
                pass
        
        # Step all trucks
        for truck in self.trucks:
            try:
                truck.step()
            except Exception:
                pass
        
        # Step client
        try:
            self.client.step_time()
        except Exception:
            pass
        
        return self.get_state()

    def reset(self):
        """
        Reset all components and place a new client order.
        Returns the system state after reset.
        """
        self.current_enacted_strategy = 0

        # Reset client
        try:
            self.client.reset()
        except Exception:
            pass
        
        # Reset all machines
        for machine in self.machines:
            try:
                machine.reset()
            except Exception:
                pass
        
        # Reset all trucks
        for truck in self.trucks:
            try:
                truck.reset()
            except Exception:
                pass
        
        # Place new order
        try:
            self.current_priority = self.client.place_order()
            self.m1_processing_full() # Start processing immediately
        except Exception:
            pass
        
        return self.get_state()

    # learning methods

    def action(self, action_str, repr=True):
        """
        Execute an action based on the provided string.
        
        Args:
            action_str: String name of the method to call
            repr: If True, returns a string representation of the state
                instead of the state tuple
        
        Returns:
            The result of the called method (system state or its string representation)
        """
        # Dictionary mapping action strings to methods
        action_methods = {
            "m1_processing_third": self.m1_processing_third,
            "m1_processing_half": self.m1_processing_half,
            "m1_processing_full": self.m1_processing_full,
            "m1_maintenance": self.m1_maintenance,
            "m2_processing_third": self.m2_processing_third,
            "m2_processing_half": self.m2_processing_half,
            "m2_processing_full": self.m2_processing_full,
            "m2_maintenance": self.m2_maintenance,
            "small_truck_shipment": self.small_truck_shipment,
            "big_truck_shipment": self.big_truck_shipment,
            "step": self.step,
            "reset": self.reset
        }
        
        # Call the corresponding method if it exists
        if action_str in action_methods:
            state = action_methods[action_str]()
            
            # If repr=True, format the state as a string
            if repr:
                # Define the component names
                component_names = [
                    "client_current_priority", 
                    "quantity_shipped_to_the_client",
                    "time_to_penalty",
                    "m1_status", 
                    "m1_stored",
                    "m1_to_completion",
                    "m2_status", 
                    "m2_stored",  
                    "m2_to_completion",
                    "ts_status",
                    "ts_to_completion",
                    "tb_status",
                    "tb_to_completion"
                ]
                
                # Create formatted string with key:value pairs
                state_dict = {}
                for i, name in enumerate(component_names):
                    value = state[i]
                    # Format floats to two decimal places
                    if isinstance(value, float):
                        state_dict[name] = f"{value:.2f}"
                    else:
                        state_dict[name] = value
                
                # Convert dict to string format: {key1:value1, key2:value2, ...}
                result = "{"
                for idx, (key, value) in enumerate(state_dict.items()):
                    if isinstance(value, str):
                        result += f"{key}:'{value}'"
                    else:
                        result += f"{key}:{value}"
                    if idx < len(state_dict) - 1:
                        result += ", "
                result += "}"
                return result
            
            return state
        else:
            # Handle unknown action
            raise ValueError(f"Unknown action: {action_str}")

    def alphabet(self):
        """
        Returns the list of available action strings, excluding 'reset'.
        
        Returns:
            list: List of strings representing available actions
        """
        actions = [
            "m1_processing_third",
            "m1_processing_half",
            "m1_processing_full",
            "m1_maintenance",
            "m2_processing_third",
            "m2_processing_half",
            "m2_processing_full",
            "m2_maintenance",
            "small_truck_shipment",
            "big_truck_shipment",
            "step"
        ]
        
        return actions
    
    def enact_strategy(self, selected_components=None, bound=None):
        """
        Applies the strategy logic for managing machines and trucks based on current state.
        If no action is enabled by the strategy, performs a step action.
        The black diamond (◆) indicates the machine has maintenance active OR is currently 
        undergoing maintenance.
        
        Args:
            selected_components: List of component names to include in the output.
                                If None, includes only the base components.
            bound: Maximum number of strategy executions before stopping.
        
        Returns:
            String representation of the system state after strategy execution,
            or "Stopped"/"Completed" if terminal conditions are met.
        """

        if self.client.state == "completed" and self.client.order_quantity >= 1:
            return f"Completed {self.client.time_passed <= self.client.time_limit} {self.client.current_priority}"
        
        
        # Extract relevant state information
        m1_status = self.m1.state
        m1_stored = self.m1.stored_output
        m2_status = self.m2.state
        m2_stored = self.m2.stored_output
        ts_status = self.small_truck.state
        tb_status = self.big_truck.state
        
        # Get quantity shipped to client
        client_quantity = self.client.order_quantity
        
        # Compute all decision variables
        m1_running = m1_status != "idle"
        m2_running = m2_status != "idle"
        ts_running = ts_status != "available"
        tb_running = tb_status != "available"
        
        # Calculate processing amounts
        processing_m2_amount = 0
        if m2_status.startswith("processing"):
            if "full" in m2_status:
                processing_m2_amount = 1
            elif "half" in m2_status:
                processing_m2_amount = 0.5
            elif "third" in m2_status:
                processing_m2_amount = 1/3
        
        # Calculate shipped amounts (in transit)
        shipped_m2_amount = 0
        if ts_running:
            shipped_m2_amount += self.small_truck.current_load
        if tb_running:
            shipped_m2_amount += self.big_truck.current_load
        
        # Calculate total material (including what's already been delivered to client)
        total_material = m1_stored + processing_m2_amount + m2_stored + shipped_m2_amount + client_quantity
        
        # Check maintenance status
        m1_maintenance_active = self.m1.maintenance_active or m1_status == "maintenance"
        m2_maintenance_active = self.m2.maintenance_active or m2_status == "maintenance"
        
        # Track the command to be executed
        command = None
        
        # Apply M2 Management strategy
        if not m2_maintenance_active:
            command = "m2_maintenance"
        elif not m2_running and m1_stored > 0 and (client_quantity < 1):
            command = "m2_processing_third"
        
        # Apply M1 Management strategy (if no command selected yet)
        elif not m1_running and not m1_maintenance_active and (client_quantity < 1):
            command = "m1_maintenance"
        elif not m1_running and (client_quantity < 1):
            command = "m1_processing_full"
        
        # Apply Small Truck Management strategy (if no command selected yet)
        elif not ts_running and m2_stored > 0:
            command = "small_truck_shipment"
        
        # Apply Big Truck Management strategy (if no command selected yet)
        elif not ts_running and not tb_running and m2_stored > 0:
            command = "big_truck_shipment"
        
        # If no action was taken, perform a step
        else:
            command = "step"
        
        # Execute the selected command
        state = self.action(command, repr=False)
        
        # Get current revenue
        client_state = self.client.get_state()
        current_revenue = client_state["current_payment"]
        
        # Define all possible components
        all_components = {
            # Base state components
            "client_current_priority": state[0],
            "quantity_shipped_to_the_client": state[1],
            "time_to_penalty": state[2],
            "m1_status": state[3],
            "m1_stored": state[4],
            "m1_to_completion": state[5],
            "m2_status": state[6],
            "m2_stored": state[7],
            "m2_to_completion": state[8],
            "ts_status": state[9],
            "ts_to_completion": state[10],
            "tb_status": state[11],
            "tb_to_completion": state[12],
            
            # Strategy decision variables
            "command_executed": command,
            "current_revenue": current_revenue,
            "m1_running": m1_running,
            "m2_running": m2_running,
            "ts_running": ts_running,
            "tb_running": tb_running,
            "m1_maintenance_active": m1_maintenance_active,
            "m2_maintenance_active": m2_maintenance_active,
            "processing_m2_amount": processing_m2_amount,
            "shipped_m2_amount": shipped_m2_amount,
            "client_quantity": client_quantity,
            "total_material": total_material
        }
        
        # Format values
        formatted_components = {}
        for key, value in all_components.items():
            if isinstance(value, float):
                formatted_components[key] = f"{value:.2f}"
            else:
                formatted_components[key] = value
        
        # Filter components if requested
        if selected_components is not None:
            formatted_components = {k: v for k, v in formatted_components.items() if k in selected_components}
        else:
            # Default to include only base components
            base_components = [
                "client_current_priority",
                "quantity_shipped_to_the_client",
                "time_to_penalty",
                "m1_status", 
                "m1_stored",
                "m1_to_completion",
                "m2_status", 
                "m2_stored",  
                "m2_to_completion",
                "ts_status",
                "ts_to_completion",
                "tb_status",
                "tb_to_completion"
            ]
            formatted_components = {k: v for k, v in formatted_components.items() if k in base_components}
        
        # Convert to string format
        result = "{"
        items = list(formatted_components.items())
        for idx, (key, value) in enumerate(items):
            if isinstance(value, str) and not value.replace('.', '', 1).isdigit():
                result += f"{key}:'{value}'"
            else:
                result += f"{key}:{value}"
            if idx < len(items) - 1:
                result += ", "
        result += "}"
        
        return result