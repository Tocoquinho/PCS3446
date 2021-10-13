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
        self.time = max(self.time, time)
    

    def print(self):
        print(f"CPU (Time: {self.time})", end=" ")

        if(self.current_job != None):
            print("[")
            self.current_job.print()
            print("]")


