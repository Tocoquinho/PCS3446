class Job:
    def __init__(self, name, arrival, size, duration):
        self.name = name
        self.arrival = arrival
        self.size = size
        self.duration = duration

        # Simulation Metrics
        self.wait_time = [] # Interval of time spent while waiting in the system wait list
        self.executed = 0 # Runtime already elapsed

        self.states = {"Submitted": -1,
                       "Joined": -1,
                       "Execution": [],
                       "Done": -1}

        self.memory = None # Partition of memory occupied by the job
        self.memory_base = 0 # Base of memory that was occupied by the job
        self.memory_percentage = 0 # Percentage of memory occupied by the job

        # Post Simulation Metrics
        self.turnaround = 0.0
        self.weighted_turnaround = 0.0

        self.permanence_interval = 0.0

        self.total_time_wait_list = 0.0
        self.total_time_ready_list = 0.0

        self.percentage_wait_list = 0.0
        self.percentage_ready_list = 0.0


    def getTurnaround(self):
        time = self.states["Done"]
        self.turnaround = float(time - self.arrival)
        return self.turnaround


    def getWeightedTurnaround(self):
        self.weighted_turnaround = float(self.turnaround/self.duration)
        return self.weighted_turnaround

    
    def getPermanenceInterval(self):
        start = self.states["Joined"]
        final = self.states["Done"]
        self.permanence_interval = final - start
        return self.permanence_interval

    
    def getTotalTimeWaitList(self):
        if len(self.wait_time) > 0:
            start = self.wait_time[0]
            final = self.wait_time[1]
            self.total_time_wait_list = final - start
        return self.total_time_wait_list


    def getTotalTimeReadyList(self):
        start = self.states["Joined"]
        final = self.states["Execution"][0][0]
        self.total_time_ready_list = final - start
        for i in range(len(self.states["Execution"]) - 1):
            start = self.states["Execution"][i][1]
            final = self.states["Execution"][i + 1][0]
            self.total_time_ready_list += final - start

        return self.total_time_ready_list


    def getPercentageWaitList(self):
        start = self.states["Submitted"]
        final = self.states["Done"]
        self.percentage_wait_list = self.total_time_wait_list / (final - start)
        return self.percentage_wait_list
    
    def getPercentageReadyList(self):
        start = self.states["Joined"]
        final = self.states["Done"]
        self.percentage_ready_list = self.total_time_ready_list / (final - start)
        return self.percentage_ready_list

    def print(self):
        print(f"    {self.name}: {self.arrival}, {self.size/1.0e3:.4}k, {self.duration}, {self.executed}, {self.turnaround}, {self.weighted_turnaround}")
        # print(f"    {self.states}")


class JobMix:
    def __init__(self):
        self.list = []

        # Post Simulation Metrics
        self.mean_turnaround = 0.0
        self.mean_weighted_turnaround = 0.0
        self.mean_permanence_interval = 0.0
        self.mean_time_wait_list = 0.0
        self.mean_time_ready_list = 0.0
        self.mean_percentage_wait_list = 0.0
        self.mean_percentage_ready_list = 0.0


    def append(self, job):
        self.list.append(job)

    
    def setPostSimulationMetrics(self):
        total_T = 0
        total_W = 0
        total_PI = 0
        total_RL = 0
        total_WL = 0
        total_PWL = 0
        total_PRL = 0
        for job in self.list:
            # Mean turnaround
            total_T += job.getTurnaround()
            
            # Mean weighted turnaround
            total_W += job.getWeightedTurnaround()

            # Mean permanence interval
            total_PI += job.getPermanenceInterval()

            # Mean time in wait list
            total_WL += job.getTotalTimeWaitList()

            # Mean time in ready list
            total_RL += job.getTotalTimeReadyList()
            
            # Mean percentage in wait list
            total_PWL += job.getPercentageWaitList()

            # Mean percentage in ready list
            total_PRL += job.getPercentageReadyList()

        self.mean_turnaround = total_T / len(self.list)
        self.mean_weighted_turnaround = total_W / len(self.list)
        self.mean_permanence_interval = total_PI / len(self.list)
        self.mean_time_wait_list = total_WL / len(self.list)
        self.mean_time_ready_list = total_RL / len(self.list)
        self.mean_percentage_wait_list = total_PWL / len(self.list)
        self.mean_percentage_ready_list = total_PRL / len(self.list)


    def generateCSV(self, name = "metrics.csv"):
        self.setPostSimulationMetrics()

        attributes = ["Job", "Chegada", "Início", "Término", "T", "W", 
                      "Intervalo de Permanência", "Tempo na fila de espera",
                      "Tempo na ready list" , "\n"]
        
        with open(name, 'w') as file:
            file.write(",".join(attributes))
            for job in self.list:
                data = [job.name, job.arrival, job.states["Joined"], job.states["Done"],
                        job.turnaround, job.weighted_turnaround, job.permanence_interval,
                        job.total_time_wait_list, job.total_time_ready_list, "\n"]
                data = ",".join(list(map(str, data)))
                file.write(data)

            file.write("\n" * 3)

            string = ["T médio", self.mean_turnaround, "\n"]
            file.write(",".join(list(map(str, string))))
            
            string = ["W médio", self.mean_weighted_turnaround, "\n"]
            file.write(",".join(list(map(str, string))))
            
            string = ["Intervalo de Permanência médio", self.mean_permanence_interval, "\n"]
            file.write(",".join(list(map(str, string))))
            
            string = ["Tempo médio na fila de espera", self.mean_time_wait_list, "\n"]
            file.write(",".join(list(map(str, string))))

            string = ["Tempo médio na ready list", self.mean_time_ready_list, "\n"]
            file.write(",".join(list(map(str, string))))


    def print(self):
        self.setPostSimulationMetrics()
        print(f"\nJob Mix: [")
        print("    Name: arrival, memory size, duration, executed time, turnaround time, weighted turnaround time")
        for job in self.list:
            job.print()
        print("]")
        print(f"Mean Turnaround time: {self.mean_turnaround:.4}")
        print(f"Mean Weighted Turnaround time: {self.mean_weighted_turnaround:.4}")
        
