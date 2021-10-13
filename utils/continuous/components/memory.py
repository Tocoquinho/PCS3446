class Partition:
    def __init__(self, index, job):
        self.index = index
        self.size = job.memory
        self.end = index + self.size
        self.job = job

    
    def print(self):
        print(f"    [{self.index:05} - {self.end:05}]: {self.job.name}")


class Memory:
    def __init__(self, memory_size):
        self.size = memory_size
        self.partitions = []
        

    def allocate(self, job):
        """
        Gets a job and tries to allocate it inside the memory
        """
        self.partitions.append(Partition(0, job))
 
    
    def isAvailable(self):
        """
        Checks if the memory is empty
        """
        if len(self.partitions) == 0:
            return True
        return False

    
    def isSmaller(self, job_size):
        """
        Checks if the job size fits
        """
        if job_size <= self.size:
            return True
        return False


    def free(self):
        """
        Frees the memory, deleting the job
        """
        self.partitions = []

    
    def print(self):
        print(f"Memory ({self.size}) [")
        for partition in self.partitions:
            partition.print()
        print("]\n")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "..")

    from job import Job


    j1 = Job("1", 20, 30e3, 60)
    j2 = Job("2", 30, 100e3, 120)
    j3 = Job("3", 40, 80e3, 80)
    j4 = Job("4", 50, 40e3, 40)

    mem = Memory(80e3)

    mem.print()
    mem.allocate(j1)
    mem.print()

    mem.allocate(j2)
    mem.print()

    mem.free()

    mem.print()

    mem.allocate(j2)
    mem.print()

