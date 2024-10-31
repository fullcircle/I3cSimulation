# Cycle-based simulation of an I3C bus with a controller and a target
class CycleSimulation:
    def __init__(self, total_cycles):
        self.current_cycle = 0
        self.total_cycles = total_cycles
        self.SCL = 1  # Clock line (1 = high, 0 = low)
        self.SDA = 1  # Data line (1 = high, 0 = low)
        self.controller_state = "IDLE"
        self.target_state = "IDLE"
        self.data_to_send = None  # Data buffer for communication
        self.ack = False  # Acknowledgment signal
    
    def run_cycle(self):
        # Run simulation for each cycle
        for cycle in range(self.total_cycles):
            print(f"Cycle {cycle}:")
            self.controller(cycle)
            self.target(cycle)
            self.toggle_SCL()  # Toggle SCL to simulate clock edges
            print(f"  SCL: {self.SCL}, SDA: {self.SDA}")
            self.current_cycle += 1
            print()  # Empty line for cycle separation

    def toggle_SCL(self):
        # Toggle SCL line to simulate clock pulse
        self.SCL = 1 - self.SCL

    def controller(self, cycle):
        if self.controller_state == "IDLE":
            print("  Controller at IDLE state")
            if cycle == 0:
                print("  Controller: Initiating communication.")
                self.controller_state = "START"
                self.SDA = 0  # Set SDA low for START condition
        elif self.controller_state == "START":
            if self.SCL == 1:
                print("  Controller: Sending data on SDA")
                self.SDA = 1  # Send data bits (example logic)
                self.controller_state = "WAIT_ACK"
        elif self.controller_state == "WAIT_ACK":
            if self.ack:
                print("  Controller: ACK received")
                self.controller_state = "IDLE"
            else:
                print("  Controller: Waiting for ACK...")

    def target(self, cycle):
        if self.target_state == "IDLE":
            print("  Target at IDLE state")
            if self.SDA == 0 and self.SCL == 1:  # Detect START condition
                print("  Target: START condition detected")
                self.target_state = "RECEIVE"
        elif self.target_state == "RECEIVE":
            if self.SCL == 1:
                print("  Target: Receiving data bit on SDA")
                self.ack = True  # Send ACK
                self.target_state = "IDLE"

# Running the cycle simulation for a specified number of cycles
sim = CycleSimulation(total_cycles=10)
sim.run_cycle()
