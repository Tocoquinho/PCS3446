import numpy as np
from utils.job import Job, JobMix
from utils.continuous.event import Event, EventQueue, EventQueueAntecipated
from utils.continuous.system import SystemFIFO, SystemShortest

def fifoContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system)


def shortestContinuous(job_mix, memory_size = 120e3):
    system = SystemShortest(memory_size)
    eventEngine(job_mix, system)


def antecipatedContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system, EventQueueAntecipated())


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
    j2 = Job("2", 10.10, 100e3, 1)
    j3 = Job("3", 10.25, 80e3, 0.25)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)

    return job_mix


def jobMix3():
    j1 = Job("1", 10.0, 30e3, 0.3)
    j2 = Job("2", 10.2, 100e3, 0.5)
    j3 = Job("3", 10.4, 80e3, 0.1)
    j4 = Job("4", 10.5, 30e3, 0.4)
    j5 = Job("5", 10.8, 100e3, 0.1)


    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)

    return job_mix


def eventEngine(job_mix, system, event_queue = EventQueue()):
    # Create event queue
    event_queue.mix2Queue(job_mix)

    # Start event engine
    print("Type enter to start the simulation: ")
    while not event_queue.isEmpty():
        # Get simulation step command
        if(input() != ""):
            continue
        
        event_queue.print()

        # Send next event to the system
        event = event_queue.getNextEvent()
        new_event = system.receiveEvent(event)

        # If the new event is "stop", stop the simulation
        if new_event == "stop":
            break

        # If there is a new event, add it to the queue
        if new_event != None:
            event_queue.addEvent(new_event)

        
        # system.cpu.print()
        # print("Step Finished!",end="\n")
    job_mix.print()


def main():
    job_mix = jobMix3()
    fifoContinuous(job_mix)


if __name__ == "__main__":
    main()

