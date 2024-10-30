import simpy
import random

# Define constants
BUS_CLOCK = 12.5e6    # 12.5 MHz clock rate in SDR mode
I3C_ADDR_CONTROLLER = 0x7E
I3C_ADDR_TARGET_START = 0x10

# Define roles on the bus
class I3CDevice:
    def __init__(self, env, bus, name, addr):
        self.env = env
        self.bus = bus
        self.name = name
        self.addr = addr
        self.is_active = False
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(random.uniform(0.1, 1))

    def request_bus(self):
        yield self.env.process(self.bus.arbitration(self.addr))

class I3CController(I3CDevice):
    def __init__(self, env, bus, name):
        super().__init__(env, bus, name, I3C_ADDR_CONTROLLER)

    def run(self):
        while True:
            print(f"{self.name} at time {self.env.now}: Initiating communication.")
            yield self.env.timeout(1 / BUS_CLOCK)
            yield from self.request_bus()
            if self.bus.is_active:
                print(f"{self.name} at time {self.env.now}: Bus acquired, sending data.")
                yield from self.send_data(I3C_ADDR_TARGET_START, [0x01, 0x02, 0x03])
                self.bus.release_bus()
            yield self.env.timeout(1)

    def send_data(self, target_addr, data):
        for byte in data:
            print(f"{self.name} at time {self.env.now}: Sending byte {byte} to {target_addr}")
            yield self.env.timeout(1 / BUS_CLOCK)

class I3CTarget(I3CDevice):
    def __init__(self, env, bus, name, addr):
        super().__init__(env, bus, name, addr)

    def run(self):
        while True:
            yield self.env.timeout(random.uniform(0.1, 1))
            if self.bus.current_addr == self.addr and self.bus.is_active:
                print(f"{self.name} at time {self.env.now}: Received data.")
                yield self.env.timeout(1 / BUS_CLOCK)

class I3CBus:
    def __init__(self, env):
        self.env = env
        self.is_active = False
        self.current_addr = None

    def arbitration(self, addr):
        if not self.is_active or addr < self.current_addr:
            self.is_active = True
            self.current_addr = addr
            yield self.env.timeout(1 / BUS_CLOCK)  # Simulate bus acquisition delay
            print(f"Bus arbitration: Address {addr} acquired the bus at {self.env.now}")
        else:
            print(f"Bus arbitration: Address {addr} lost arbitration at {self.env.now}")

    def release_bus(self):
        self.is_active = False
        self.current_addr = None
        print(f"Bus released at {self.env.now}")

# Simulation setup
env = simpy.Environment()
bus = I3CBus(env)
controller = I3CController(env, bus, "Controller")
target1 = I3CTarget(env, bus, "Target 1", I3C_ADDR_TARGET_START)
target2 = I3CTarget(env, bus, "Target 2", I3C_ADDR_TARGET_START + 1)

# Run the simulation
env.run(until=20)
