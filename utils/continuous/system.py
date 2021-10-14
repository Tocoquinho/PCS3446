from utils.continuous.components.memory import Memory, MemoryMultiprogrammedFirstChoice
from utils.continuous.components.memory import MemoryMultiprogrammedBestChoice, MemoryMultiprogrammedWorstChoice
from utils.continuous.components.cpu import CPU, CPUMultiprogrammed
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
        return []


    def eventArrival(self, event):
        # The job is submitted to the system
        if event.job.states["Submitted"] == -1:
            event.job.states["Submitted"] = event.time

        if self.memory.isAvailable(event.job):
            # The job is accepted and joints the system
            event.job.start = event.time
            event.job.states["Joined"] = event.time

            # Update CPU execution time
            self.cpu.updateTime(event.time)

            # Send new event to the Queue
            return [Event("memory req", 0, event.job)]

        else:
            # Store this event to the wait list
            self.wait_list.append(event)
            return []

    
    def eventMemory(self, event):
        # Allocate memory to the new job
        if self.memory.isSmaller(event.job.memory):
            self.memory.allocate(event.job)
            # Send new event to the Queue
            return [Event("process req", 0, event.job)]

        else:
            print(f"\nThis job is bigger than the memory size: ")
            event.job.print()
            return []

    
    def eventProcess(self, event):
        # Allocate the CPU to the new job
        self.cpu.allocate(event.job)

        # The CPU starts the job execution
        event.job.states["Execution"].append([self.cpu.time])

        # Send new event to the Queue
        end_time = self.cpu.time + event.job.duration
        return [Event("end of process", end_time, event.job)]

    
    def eventEndProcess(self, event):
        # Update CPU execution time
        self.cpu.updateTime(event.time)

        # The CPU has finished the job execution
        event.job.states["Execution"][-1].append(event.time)
        event.job.executed = event.job.duration

        # Free CPU
        self.cpu.free()
        # Free memory
        self.memory.free(event.job.name)

        # The job leaves the system
        event.job.states["Done"] = self.cpu.time

        # Update the job stats
        event.job.updateEndTime(self.cpu.time)

        # Check the wait list and get the next waiting event
        return [self.updateWaitList()]


    def eventEnd(self, event):
        # Stop simulation
        print(f"\n[{self.cpu.time}] End of simulation at event:")
        event.print()
        return ["stop"]


    def updateWaitList(self):
        if len(self.wait_list) > 0:
            new_event = self.wait_list.pop(0)
            new_event.time = self.cpu.time

            output = self.eventArrival(new_event)
            if len(output) > 0:
                return output[0]
        return
class SystemFIFO(System):
    pass

class SystemShortest(System):
    def updateWaitList(self):
        if len(self.wait_list) > 0:
            self.wait_list.sort(key = lambda event: event.job.duration)
            new_event = self.wait_list.pop(0)
            new_event.time = self.cpu.time

            output = self.eventArrival(new_event)
            if len(output) > 0:
                return output[0]
        return
    

class SystemMultiprogrammed(System):
    def __init__(self, memory_size, time_slice):
        super().__init__(memory_size)
        self.cpu = CPUMultiprogrammed(time_slice)


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

        elif kind == "cpu time slice":
            return self.eventTimeSlice(event)

        elif kind == "end of process":
            return self.eventEndProcess(event)

        else:
            return self.eventEnd(event)

        
    def eventProcess(self, event):
        # Allocate the CPU to the new job and check if the CPU was idle
        was_idle = self.cpu.allocate(event.job)

        # If there was no execution, start the timer corresponding to the time slice
        if was_idle:
            # The CPU starts the job execution
            event.job.states["Execution"].append([self.cpu.time])

            # Check if the next time slice is the last for this job
            last_slice, switch_time = self.cpu.generateTimeSlice()
            if last_slice:
                end_time = self.cpu.time + event.job.duration
                return [Event("end of process", end_time, event.job)]

            # If its not the last time slice, raise a Time Slice event
            else:
                return [Event("cpu time slice", self.cpu.time + switch_time)]
        
        return []


    def eventTimeSlice(self, event):
        # Update CPU execution time
        self.cpu.updateTime(event.time)

        # Store the execution interval end of the current job
        job = self.cpu.current_job
        job.states["Execution"][-1].append(self.cpu.time)
    
        # Finish the time slice in the CPU, get the new time slice information
        # and execute a new job
        last_slice, switch_time = self.cpu.endTimeSlice()

        # Store the execution interval start of the new job
        new_job = self.cpu.current_job
        new_job.states["Execution"].append([self.cpu.time])

        if last_slice:
            remaining_time = new_job.duration - new_job.executed
            end_time = self.cpu.time + remaining_time
            return [Event("end of process", end_time, new_job)]
        
        # If its not the last time slice, raise a Time Slice event
        return [Event("cpu time slice", self.cpu.time + switch_time)]

    
    def eventEndProcess(self, event):
        # Initialize the return list
        output = []

        # Update CPU execution time
        self.cpu.updateTime(event.time)

        # The CPU has finished the job execution
        event.job.states["Execution"][-1].append(event.time)
        event.job.executed = event.job.duration

        # Free CPU
        self.cpu.free()
        # Free memory
        self.memory.free(event.job.name)

        # The job leaves the system
        event.job.states["Done"] = self.cpu.time

        # Update the job stats
        event.job.updateEndTime(self.cpu.time)

        # End this time slice
        last_slice, switch_time = self.cpu.endTimeSlice()
        new_job = self.cpu.current_job
        if new_job != None:
            if last_slice:
                remaining_time = new_job.duration - new_job.executed
                end_time = self.cpu.time + remaining_time
                output.append(Event("end of process", end_time, new_job))
            else:
                output.append(Event("cpu time slice", self.cpu.time + switch_time))

        # Check the wait list and get the next waiting event
        output.append(self.updateWaitList())
        
        return output


class SystemMultiprogrammedFirstChoice(SystemMultiprogrammed):
    def __init__(self, memory_size, time_slice, n):
        super().__init__(memory_size, time_slice)
        self.memory = MemoryMultiprogrammedFirstChoice(memory_size, n)


class SystemMultiprogrammedBestChoice(SystemMultiprogrammed):
    def __init__(self, memory_size, time_slice, n):
        super().__init__(memory_size, time_slice)
        self.memory = MemoryMultiprogrammedBestChoice(memory_size, n)


class SystemMultiprogrammedWorstChoice(SystemMultiprogrammed):
    def __init__(self, memory_size, time_slice, n):
        super().__init__(memory_size, time_slice)
        self.memory = MemoryMultiprogrammedWorstChoice(memory_size, n)

