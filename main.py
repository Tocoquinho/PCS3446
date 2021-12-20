from utils.file import File
from utils.job import Job, JobMix
from utils.components.disk import Disk
from utils.file_mapper import FileMapper
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

def P1():
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
    # multiprogrammedFirstChoice(job_mix_4, memory_size=120e3, time_slice=1)
    # multiprogrammedFirstChoice(job_mix_5, memory_size=120e3, time_slice=1)
    # multiprogrammedFirstChoice(job_mix_6, memory_size=120e3, time_slice=1)
    # multiprogrammedWorstChoice(job_mix, memory_size=120e3, time_slice=1)
    # multiprogrammedBestChoice(job_mix, memory_size=120e3, time_slice=1)

def read_input(disk):
    """
    Reads a script written by the user in the terminal and transforms it into a file
    """
    file_name = input("Type the file name: ")

    file_commands = []
    txt_input = ""
    print("\nType 'eof' to finish the file")
    while(txt_input != "eof"):
        file_commands.append(txt_input)
        txt_input = input()

    # Translate the instructions and create a file with it
    file_mapper = FileMapper(file_commands, disk)
    file_mapper.readInstructions()

    total_size = 0
    if file_mapper.output["JOB MIX"] != None:
        for job in file_mapper.output["JOB MIX"].list:
            total_size += job.size
    file_size = max(total_size, file_mapper.output["SIZE"])


    return File(file_name, file_mapper.output["JOB MIX"], file_size, file_mapper.output["DATA"])

    

def main():
    disk = Disk(3e3)

    # Create a file based on the user input
    while(True):
        create_file = input("Create a new file? (y/n) ")
        if(create_file in ("y", "Y", "yes", "Yes")):
            new_file = read_input(disk)
            disk.allocate(new_file)

        elif(create_file in ("n", "N", "no", "No")):
            break

        else:
            print("\nPlease type a valid answer!")

    # join all the jobs together for execution
    job_mixes = JobMix()
    for p in disk.partitions:
        if p.file == None or p.file.job_mix == None:
            continue
        job_mixes.list += p.file.job_mix.list

    # Execute the simulation
    disk.print()
    multiprogrammedFirstChoice(job_mixes, memory_size=2e3, time_slice=10)

    disk.print()
    # If you want to free some space and test garbage collection,  run the following code
    file_to_remove = "inputs1.txt"
    disk.free(file_to_remove)
    disk.print()

    disk.reorganizeDisk()
    disk.print()

    disk.plot()


if __name__ == "__main__":
    main()

