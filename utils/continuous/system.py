from utils.continuous.components.memory import Partition, Memory
from utils.continuous.components.cpu import CPU
from utils.continuous.event import Event

class System:
    def __init__(self, memory_size):
        self.memory = Memory(memory_size)
        self.cpu = CPU()
        self.wait_list = []

    
    def receiveEvent(self, event):
        kind = event.kind

        if kind == "start":
            return self.eventStart()
        
        elif kind == "arrival":
            return self.eventArrival(event)

        elif kind == "memory req":
            return self.eventMemory(event)
        
        elif kind == "process req":
            return self.eventProcess(event)

        elif kind == "end of process":
            return self.eventEndProcess(event)

        else:
            return self.eventEnd(event)


    def eventStart(self):
        print("Initializing simulation:\n")
        return


    def eventArrival(self, event):
        if self.memory.isAvailable():
            # Update CPU execution time
            self.cpu.updateTime(event.time)

            # Send new event to the Queue
            return Event("memory req", 0, event.job)

        else:
            # Store this event to the wait list
            self.wait_list.append(event)
            return

    
    def eventMemory(self, event):
        # Allocate memory to the new job
        if self.memory.isSmaller(event.job.memory):
            self.memory.allocate(event.job)
            # Send new event to the Queue
            return Event("process req", 0, event.job)

        else:
            print(f"\nThis job is bigger than the memory size: ")
            event.job.print()
            return

    
    def eventProcess(self, event):
        # Allocate the CPU to the new job
        self.cpu.allocate(event.job)
        # Send new event to the Queue
        end_time = self.cpu.time + event.job.duration
        return Event("end of process", end_time, event.job)

    
    def eventEndProcess(self, event):
        # Update CPU execution time
        self.cpu.updateTime(event.time)
        # Free memory
        self.memory.free()
        # Free CPU
        self.cpu.free()

        # Update the job stats
        event.job.updateEndTime(self.cpu.time)

        # Check the wait list and get the next waiting event
        return self.updateWaitList()


    def eventEnd(self, event):
        # Stop simulation
        print(f"\n[{self.cpu.time}] End of simulation at event:")
        event.print()
        return "stop"


    def updateWaitList(self):
        pass

class SystemFIFO(System):
    def updateWaitList(self):
        if len(self.wait_list) > 0:
            new_event = self.wait_list.pop(0)
            new_event.time = self.cpu.time
            return self.eventArrival(new_event)
        
        return

class SystemShortest(System):
    def updateWaitList(self):
        if len(self.wait_list) > 0:
            self.wait_list.sort(key = lambda event: event.job.duration)
            new_event = self.wait_list.pop(0)
            new_event.time = self.cpu.time
            return self.eventArrival(new_event)
        
        return

