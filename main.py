from utils.job import Job, JobMix
from utils.continuous.event import EventQueue, EventQueueAntecipated
from utils.continuous.system import SystemFIFO, SystemShortest, SystemMultiprogrammedFirstChoice
from utils.continuous.system import SystemMultiprogrammedBestChoice, SystemMultiprogrammedWorstChoice

def fifoContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system)


def shortestContinuous(job_mix, memory_size = 120e3):
    system = SystemShortest(memory_size)
    eventEngine(job_mix, system)


def antecipatedContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system, EventQueueAntecipated())


def multiprogrammedFirstChoice(job_mix, memory_size = 120e3, time_slice = 0.1):
    system = SystemMultiprogrammedFirstChoice(memory_size, time_slice)
    eventEngine(job_mix, system)


def multiprogrammedBestChoice(job_mix, memory_size = 120e3, time_slice = 0.1):
    system = SystemMultiprogrammedBestChoice(memory_size, time_slice)
    eventEngine(job_mix, system)


def multiprogrammedWorstChoice(job_mix, memory_size = 120e3, time_slice = 0.1):
    system = SystemMultiprogrammedWorstChoice(memory_size, time_slice)
    eventEngine(job_mix, system)


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
        new_events = system.receiveEvent(event)

        for new_event in new_events:
            # If the new event is "stop", stop the simulation
            if new_event == "stop":
                break

            # If there is a new event, add it to the queue
            if new_event != None:
                event_queue.addEvent(new_event)


        system.memory.print()

        system.cpu.print()

    job_mix.print()


def main():
    job_mix = jobMix3()
    multiprogrammedFirstChoice(job_mix, time_slice=0.03)


if __name__ == "__main__":
    main()

