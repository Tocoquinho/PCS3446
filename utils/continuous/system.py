from utils.continuous.components.memory import Memory, MemoryMultiprogrammedFirstChoice
from utils.continuous.components.memory import MemoryMultiprogrammedBestChoice, MemoryMultiprogrammedWorstChoice
from utils.continuous.components.cpu import CPU, CPUMultiprogrammed
from utils.continuous.event import Event

import numpy as np

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

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
            event.job.states["Joined"] = event.time

            # Update memory allocation metrics
            self.memory.allocations_accepted += 1

            # Update CPU execution time
            self.cpu.updateTime(event.time)

            # Send new event to the Queue
            return [Event("memory req", 0, event.job)]

        else:
            # Store this event to the wait list
            self.wait_list.append(event.job)
            event.job.wait_time.append(self.cpu.time)

            # Update memory allocation metrics
            self.memory.allocations_denied += 1

            return []

    
    def eventMemory(self, event):
        # Allocate memory to the new job
        if self.memory.isSmaller(event.job.size):
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
        self.memory.free(event.job)

        # The job leaves the system
        event.job.states["Done"] = self.cpu.time

        # Check the wait list and get the next waiting event
        return [self.updateWaitList()]


    def eventEnd(self, event):
        # Stop simulation
        print(f"\n[{self.cpu.time}] End of simulation at event:")
        event.print()
        return ["stop"]


    def updateWaitList(self):
        # Check if there is a job in the wait list
        if len(self.wait_list) > 0:
            # Get the first job and load it into the system
            new_job = self.wait_list.pop(0)
            new_job.wait_time.append(self.cpu.time)
            
            # Generate a new event to join the system
            new_event = Event("arrival", self.cpu.time, new_job)
            output = self.eventArrival(new_event)
            if len(output) > 0:
                return output[0]
        return


    def plot(self, job_mix):
        job_names = []
        job_arrivals = []
        job_execution_intervals = []
        # Prepare the list of each job to plot
        for job in job_mix.list:
            job_names.append(job.name)
            job_arrivals.append(job.arrival)

            start = job.states["Joined"]
            final = job.states["Done"]
            job_execution_intervals.append([start, final])

        fig = plt.figure(figsize = (10, len(job_names) * 0.8))
        ax = fig.add_subplot(1,1,1)

        # Plot the execution intervals
        for i in range(len(job_names)):
            line = ax.plot(job_execution_intervals[i], [i, i], lw = 15, color = "lightskyblue",
                           path_effects = [pe.Stroke(linewidth = 20, foreground = "lightslategray"), 
                           pe.Normal()])
            line[0].set_solid_capstyle("butt")
            ax.scatter(job_arrivals[i], i, marker = "*", s = 500, facecolor = "gold", 
                       edgecolors = "lightslategray", linewidths = 2, zorder = 10000)
            ax.scatter(job_execution_intervals[i][1], i, marker = "$↓$", s = 700, facecolor = "gold", 
                       edgecolors = "lightslategray", linewidths = 1, zorder = 10000)

        plt.yticks(list(range(len(job_names))), job_names)
        plt.ylim(bottom = -0.5, top = len(job_names) - 0.5)
        plt.savefig("plot.jpg")



class SystemFIFO(System):
    pass

class SystemShortest(System):
    def updateWaitList(self):
        if len(self.wait_list) > 0:
            self.wait_list.sort(key = lambda job: job.duration)
            # Get the first job and load it into the system
            new_job = self.wait_list.pop(0)
            new_job.wait_time.append(self.cpu.time)
            
            # Generate a new event to join the system
            new_event = Event("arrival", self.cpu.time, new_job)
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

        # Update the multiprogrammed level time stamp of the cpu
        self.cpu.updateNTimeStamp()

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

        # Generate the time slice of the new job
        new_job = self.cpu.current_job
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

        # Update the multiprogrammed level time stamp of the cpu
        self.cpu.updateNTimeStamp()

        # Free memory
        self.memory.free(event.job)

        # The job leaves the system
        event.job.states["Done"] = self.cpu.time

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

