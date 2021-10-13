# Events:
    # START: time = 0
    # Arrival: time, job
    # Memory req.: memory, job
    # Process req.: job
    # End of process: time, job
    # END: time = final

class Event:
    def __init__(self, kind, time, job = None):
        self.kind = kind
        self.time = time
        self.job = job

    
    def print(self):
        job_str = ""
        if self.job != None:
            job_str = ": " + self.job.name
        
        print(f"    {self.time:03} - {self.kind}{job_str}")


class EventQueue:
    def __init__(self, end_time = 999):
        self.queue = [Event("start", 0), Event("end", end_time)]

    def isEmpty(self):
        return len(self.queue) == 0


    def mix2Queue(self, job_mix):
        for job in job_mix.list:
            self.addEvent(Event("arrival", job.arrival, job))
        

    def addEvent(self, new_event):
        for i, event in enumerate(self.queue):
            if event.time > new_event.time:
                index = i
                break
        self.queue.insert(i, new_event)


    def getNextEvent(self):
        return self.queue.pop(0)

    def print(self):
        print("Event Queue: ")
        for event in self.queue:
            event.print()

class EventQueueAntecipated(EventQueue):
    def __init__(self, end_time = 999):
        self.queue = [Event("start", 0), Event("end", end_time)]

    def mix2Queue(self, job_mix):
        for job in job_mix.list:
            self.addEvent(Event("arrival", job.arrival, job))

        self.queue.sort(key=self.sortQueue)

    def sortQueue(self, event):
        if(event.job == None):
            return event.time
        
        else:
            return event.job.duration
            
