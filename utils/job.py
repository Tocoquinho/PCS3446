class Job:
    def __init__(self, name, arrival, memory, duration):
        self.name = name
        self.arrival = arrival
        self.memory = memory
        self.duration = duration
        
        self.start = 0
        self.end = 0
        self.executed = 0
        self.turnaround = 0.0
        # Turnaround weighted
        self.w = 0.0

        self.states = {"Submitted": -1,
                       "Joined": -1,
                       "Execution": [],
                       "Done": -1}


    def updateEndTime(self, time):
        self.end = time
        self.turnaround = self.end - self.arrival
        self.w = self.turnaround/self.duration

    def print(self):
        print(f"    {self.name}: {self.arrival}, {self.memory/1e3:.4}k, {self.duration}, {self.start}, {self.end}, {self.executed}, {self.turnaround:.3}, {self.w:.3}")
        print(self.states)


class JobMix:
    def __init__(self):
        self.list = []
        self.mean_turnaround = 0.0
        self.mean_w = 0.0


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
        print("    Name: arrival, memory, duration, start time, end time, executed time, turnaround time, weighted turnaround time")
        for job in self.list:
            job.print()
        print("]")
        print(f"Mean Turnaround time: {self.mean_turnaround:.4}")
        print(f"Mean Weighted Turnaround time: {self.mean_w:.4}")
