class Job:
    def __init__(self, name, arrival, memory, duration):
        self.name = name
        self.arrival = arrival
        self.duration = duration
        self.memory = memory

        self.end = 0
        self.turnaround = 0
        # Turnaround weighted
        self.w = 0


    def updateEndTime(self, time):
        self.end = time
        self.turnaround = self.end - self.arrival
        self.w = self.turnaround/self.duration

    def print(self):
        print(f"    {self.name}: {self.arrival}, {self.memory}, {self.duration}, {self.end}, {self.turnaround}, {self.w}")


class JobMix:
    def __init__(self):
        self.list = []
        self.mean_turnaround = 0
        self.mean_w = 0


    def append(self, job):
        self.list.append(job)


    def updateStats(self):
        totalT = 0
        totalW = 0
        for job in self.list:
            totalT += job.turnaround
            totalW += job.w
        self.mean_turnaround = totalT/len(self.list)
        self.mean_w = totalW/len(self.list)


    def print(self):
        self.updateStats()
        print(f"\nJob Mix: [")
        print("    Name: arrival, memory, duration, end time, turnaround time, weighted turnaround time")
        for job in self.list:
            job.print()
        print("]")
        print(f"Mean Turnaround time: {self.mean_turnaround}")
        print(f"Mean Weighted Turnaround time: {self.mean_w}")
