from utils.job import Job, JobMix
from utils.continuous.event import EventQueue, EventQueueAntecipated
from utils.continuous.system import SystemFIFO, SystemShortest, SystemMultiprogrammedFirstChoice
from utils.continuous.system import SystemMultiprogrammedBestChoice, SystemMultiprogrammedWorstChoice

def fifoContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system)
    job_mix.generateCSV(name = "fifo_continuous.csv")
    system.plot(job_mix, False)


def shortestContinuous(job_mix, memory_size = 120e3):
    system = SystemShortest(memory_size)
    eventEngine(job_mix, system)
    job_mix.generateCSV(name = "shortest_continuous.csv")
    system.plot(job_mix, False)


def antecipatedContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system, EventQueueAntecipated())
    job_mix.generateCSV(name = "antecipated_continuous.csv")
    system.plot(job_mix, False)


def multiprogrammedFirstChoice(job_mix, memory_size = 120e3, time_slice = 0.1, n = 10):
    system = SystemMultiprogrammedFirstChoice(memory_size, time_slice, n)
    eventEngine(job_mix, system)
    job_mix.generateCSV(name = f"multiprogrammed_n{n}_quantum{time_slice}_first.csv")
    system.plot(job_mix)


def multiprogrammedBestChoice(job_mix, memory_size = 120e3, time_slice = 0.1, n = 10):
    system = SystemMultiprogrammedBestChoice(memory_size, time_slice, n)
    eventEngine(job_mix, system)
    job_mix.generateCSV(name = f"multiprogrammed_n{n}_quantum{time_slice}_best.csv")
    system.plot(job_mix)


def multiprogrammedWorstChoice(job_mix, memory_size = 120e3, time_slice = 0.1, n = 10):
    system = SystemMultiprogrammedWorstChoice(memory_size, time_slice, n)
    eventEngine(job_mix, system)
    job_mix.generateCSV(name = f"multiprogrammed_n{n}_quantum{time_slice}_worst.csv")
    system.plot(job_mix)


def jobMix1():
    j1 = Job("1", 20, 30e3, 60)
    j2 = Job("2", 30, 100e3, 120)
    j3 = Job("3", 40, 80e3, 80)
    j4 = Job("4", 50, 40e3, 40)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)

    return job_mix


def jobMix2():
    j1 = Job("1", 10.00, 30e3, 2)
    j2 = Job("2", 10.10, 40e3, 1)
    j3 = Job("3", 10.25, 50e3, 0.25)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)

    return job_mix


def jobMix3():
    j1 = Job("1", 10.0, 30, 0.3)
    j2 = Job("2", 10.2, 100, 0.5)
    j3 = Job("3", 10.4, 80, 0.1)
    j4 = Job("4", 10.5, 30, 0.4)
    j5 = Job("5", 10.8, 100, 0.1)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)

    return job_mix

def jobMixToco(num):
    if(num == 1):
        j1 = Job("1", 77,  20e3, 397)
        j2 = Job("2", 370, 40e3, 73)
        j3 = Job("3", 77,  30e3, 38)
        j4 = Job("4", 158, 35e3, 45)
        j5 = Job("5", 83,  50e3, 388)
        j6 = Job("6", 231, 10e3, 1)
    if(num == 2):
        j1 = Job("1", 10,  10, 397)
        j2 = Job("2", 285, 10, 73)
        j3 = Job("3", 177, 10, 38)
        j4 = Job("4", 3,   10, 45)
        j5 = Job("5", 17,  10, 388)
        j6 = Job("6", 10,  10, 1)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)
    job_mix.append(j6)

    return job_mix



def eventEngine(job_mix, system, event_queue = EventQueue()):
    # Create event queue
    event_queue.mix2Queue(job_mix)

    # Time slice counter (metrics)
    slice_counter = 0

    # Start event engine
    print("Type enter to start the simulation: ")
    while not event_queue.isEmpty():
        # Get simulation step command
        if(input() != ""):
            continue
        
        # Send next event to the system
        event = event_queue.getNextEvent()
        new_events = system.receiveEvent(event)

        for new_event in new_events:
            # If the new event is "stop", stop the simulation
            if new_event == "stop":
                break

            # If the new event is "cpu time slice", add one to the counter
            if new_event == "cpu time slice":
                slice_counter += 1

            # If there is a new event, add it to the queue
            if new_event != None:
                event_queue.addEvent(new_event)

        event_queue.print()
        system.memory.print()
        system.cpu.print()
        print("\n\n")
    
    job_mix.print()
    

def main():
    job_mix = jobMixToco(1)
    # job_mix = jobMix1()
    # multiprogrammedFirstChoice(job_mix, time_slice=5)
    # multiprogrammedWorstChoice(job_mix, time_slice=5)
    # multiprogrammedBestChoice(job_mix, time_slice=5)
    # fifoContinuous(job_mix)
    # shortestContinuous(job_mix)
    antecipatedContinuous(job_mix)


if __name__ == "__main__":
    main()

