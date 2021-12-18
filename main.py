from utils.job import Job, JobMix
from utils.event import EventQueue, EventQueueAntecipated
from utils.system import SystemFIFO, SystemShortest, SystemMultiprogrammedFirstChoice
from utils.system import SystemMultiprogrammedBestChoice, SystemMultiprogrammedWorstChoice

def fifoContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system)
    job_mix.generateCSV(name = "fifo_continuous.csv")
    system.plot(job_mix)


def shortestContinuous(job_mix, memory_size = 120e3):
    system = SystemShortest(memory_size)
    eventEngine(job_mix, system)
    job_mix.generateCSV(name = "shortest_continuous.csv")
    system.plot(job_mix)


def antecipatedContinuous(job_mix, memory_size = 120e3):
    system = SystemFIFO(memory_size)
    eventEngine(job_mix, system, EventQueueAntecipated())
    job_mix.generateCSV(name = "antecipated_continuous.csv")
    system.plot(job_mix, antecipated=True)


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
    j1 = Job("1", 10.00, 30e3, 1.999)
    j2 = Job("2", 10.10, 40e3, 0.999)
    j3 = Job("3", 10.25, 50e3, 0.24999)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)

    return job_mix


def jobMix2():
    j1 = Job("1", 10.0, 30e3, 0.3)
    j2 = Job("2", 10.2, 80e3, 0.5)
    j3 = Job("3", 10.4000001, 20e3, 0.1)
    j4 = Job("4", 10.5, 35e3, 0.4)
    j5 = Job("5", 10.8, 25e3, 0.1)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)

    return job_mix

def jobMix3():
    j1 = Job("1", 10.0, 20e3, 0.1)
    j2 = Job("2", 10.0, 20e3, 0.1)
    j3 = Job("3", 10.0, 20e3, 0.1)
    j4 = Job("4", 10.0, 20e3, 0.1)
    j5 = Job("5", 10.0, 20e3, 0.1)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)

    return job_mix

def jobMix4():
    j1 = Job("1", 77,  20e3, 397)
    j2 = Job("2", 370, 40e3, 73)
    j3 = Job("3", 77,  30e3, 38)
    j4 = Job("4", 158, 35e3, 45)
    j5 = Job("5", 83,  50e3, 388)
    j6 = Job("6", 231, 10e3, 1)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)
    job_mix.append(j6)

    return job_mix

def jobMix5():
    j1 = Job("1", 10,  20e3, 397)
    j2 = Job("2", 285, 35e3, 73)
    j3 = Job("3", 177, 30e3, 38)
    j4 = Job("4", 3,   35e3, 45)
    j5 = Job("5", 17,  50e3, 388)
    j6 = Job("6", 10,  10e3, 1)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)
    job_mix.append(j6)

    return job_mix


def jobMix6():
    j1 = Job("1", 58,  20e3, 397)
    j2 = Job("2", 58, 35e3, 73)
    j3 = Job("3", 58, 30e3, 38)
    j4 = Job("4", 58,   35e3, 45)
    j5 = Job("5", 58,  50e3, 388)
    j6 = Job("6", 58,  10e3, 1)

    job_mix = JobMix()
    job_mix.append(j1)
    job_mix.append(j2)
    job_mix.append(j3)
    job_mix.append(j4)
    job_mix.append(j5)
    job_mix.append(j6)

    return job_mix

def eventEngine(job_mix, system, event_queue = None):
    # Create event queue
    if event_queue == None:
        event_queue = EventQueue()
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

            # If there is a new event, add it to the queue
            if new_event != None:
            # If the new event is "cpu time slice", add one to the counter
                if new_event.kind == "cpu time slice":
                slice_counter += 1

                event_queue.addEvent(new_event)

        event_queue.print()
        system.memory.print()
        system.cpu.print()
        print(f"slices = {slice_counter}")
        print("\n\n")
    
    job_mix.print()
    

def main():
    create_file = 0
    while(create_file not in("y", "Y", "yes", "Yes", "n", "N", "no", "No")):
        create_file = input("Create a new file? (y/n) ")
        if(create_file in ("y", "Y", "yes", "Yes")):
            print("\nType 'eof' to finish the file")
            file_txt = []
            txt_input = ""
            while(txt_input != "eof"):
                file_txt.append(txt_input)
                txt_input = input()
        elif(create_file in ("n", "N", "no", "No")):
            pass
        else:
            print("\nPlease type a valid answer!")



    job_mix_1 = jobMix1()
    job_mix_2 = jobMix2()
    job_mix_3 = jobMix3()
    job_mix_4 = jobMix4()
    job_mix_5 = jobMix5()
    job_mix_6 = jobMix6()
    
    # fifoContinuous(job_mix_1)
    # fifoContinuous(job_mix_2)
    # fifoContinuous(job_mix_3)
    # fifoContinuous(job_mix_4)
    # fifoContinuous(job_mix_5)
    # fifoContinuous(job_mix_6)
    # shortestContinuous(job_mix)
    # antecipatedContinuous(job_mix)
    multiprogrammedFirstChoice(job_mix_4, memory_size=120e3, time_slice=1)
    multiprogrammedFirstChoice(job_mix_5, memory_size=120e3, time_slice=1)
    multiprogrammedFirstChoice(job_mix_6, memory_size=120e3, time_slice=1)
    # multiprogrammedWorstChoice(job_mix, memory_size=120e3, time_slice=1)
    # multiprogrammedBestChoice(job_mix, memory_size=120e3, time_slice=1)




    disk = Disk(400e3)
    files = []
    file_1 = File("file 1", 125e3, job_mix_4)
    file_2 = File("file 2", 125e3, job_mix_6)
    file_3 = File("file 3", 125e3, job_mix_5)
    # file_4 = File("file 4", 120e3, job_mix_6)
    # file_5 = File("file 5", 120e3, job_mix_5)
    files.append(file_1)
    files.append(file_2)
    files.append(file_3)
    # files.append(file_4)
    # files.append(file_5)

    disk.print()

    for file in files:
        disk.allocate(file)
    disk.print()

    disk.free(file_2)
    # disk.free(file_4)
    disk.print()

    # disk.reorganizeDisk()
    # disk.print()

    disk.plot(files)
if __name__ == "__main__":
    main()

