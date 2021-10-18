class CPU:
    def __init__(self):
        self.time = 0
        self.current_job = None


    def allocate(self, job):
        """
        Gets a job and tries to allocate it inside the CPU
        """
        if self.isAvailable():
            self.current_job = job
            return True
        return False


    def isAvailable(self):
        """
        Checks if the CPU is empty
        """
        if self.current_job == None:
            return True
        return False


    def free(self):
        """
        Frees the memory, deleting the job in execution
        """
        self.current_job = None


    def updateTime(self, time):
        self.time = round(max(self.time, time), 2)
    

    def print(self):
        print(f"CPU (Time: {self.time})", end = " ")

        if(self.current_job != None):
            print("[")
            self.current_job.print()
            print("]")


class CPUMultiprogrammed(CPU):
    def __init__(self, time_slice):
        super().__init__()
        self.time_slice = time_slice # Quantum of time
        self.ready_list = [] # List of jobs in the execution circular list

        # Simulation Metrics
        self.n_time_stamps = [[0, 0]] # Time stamps containing the multiprogrammed level

        # Post Simulation Metrics
        self.mean_n = 0.0


    def allocate(self, job):
        """
        Gets a job and tries to allocate it inside the CPU.
        If it is not available, the job goes to the wait list.
        """
        if self.isAvailable():
            self.current_job = job
            return True
        
        self.ready_list.append(job)
        return False


    def generateTimeSlice(self):
        """
        Calculates the time slice. It is the minimum between the configured time slice 
        and the remaining execution time of the current job.
        """
        # Calculate the remaining execution time of the current job in the CPU
        remaining_time = self.current_job.duration - self.current_job.executed
        # Check if the next time slice is enough to finish the current job execution
        if remaining_time <= self.time_slice:
            return True, remaining_time
        
        return False, self.time_slice


    def endTimeSlice(self):
        """
        Finishes the time slice by pushing the current job in execution to the wait list,
        and gets the new current job from it.
        """
        if self.current_job != None:
            # Update the current job execution time
            self.current_job.executed = round(self.current_job.executed + self.time_slice, 2)

            # Send the current job to the wait list
            self.ready_list.append(self.current_job)

        # Get new current job
        if len(self.ready_list) != 0:
            self.current_job = self.ready_list.pop(0)
            self.current_job.states["Execution"].append([self.time])

            # Check if the next time slice is the last for this job
            last_slice, switch_time = self.generateTimeSlice()
        
            return last_slice, switch_time
        return 0, 0


    def updateNTimeStamp(self):
        """
        Update the multiprogrammed level time stamp, 
        according to the number of jobs in the wait list + current job.
        """
        n = 0
        if self.current_job != None:
            n += 1
        n += len(self.ready_list)
        self.n_time_stamps.append([self.time, n])


    def getMeanN(self):
        total_n = 0
        for time_stamp in self.n_time_stamps:
            total_n += time_stamp[1]
        self.mean_n = total_n / len(self.n_time_stamps)
        return self.mean_n
