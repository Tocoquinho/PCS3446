import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class Partition:
    def __init__(self, base, size, file = None):
        self.file = file
        self.base = base
        self.size = size

    def print(self):
        name_str = None
        if self.file != None:
            name_str = self.file.name
        else:
            name_str = "Hole"
        print(f"    {name_str}: {self.base:05}, {self.size:05}")


class Disk:
    def __init__(self, disk_size):
        self.size = disk_size
        self.partitions = [Partition(0, disk_size)]
        self.occupation_percentage = 0

        self.allocations_accepted = 0
        self.allocations_denied = 0
        

    def isAvailable(self, file):
        """
        Checks if there is an empty partition in disk that fits the file.
        Also checks if it is allowed by the multiprogrammed level.
        """
        if self.firstChoice(file.size) != -1:
            if not self.isFull():
                return True
        return False

    
    def isSmaller(self, file_size):
        """
        Checks if the file size would fit in the entire disk
        """
        if file_size <= self.size:
            return True
        return False


    def allocate(self, file):
        """
        Gets a file and allocates it inside the disk
        """
        i = self.firstChoice(file.size)
        self.splitEmptyPartition(i, file)

    def firstChoice(self, size):
        """
        Allocation algorithm. Finds the first partitition that fits the file, returning its index.
        If there is no partition available, returns False.
        """
        for i, partition in enumerate(self.partitions):
            if partition.file == None and partition.size >= size:
                return i
        return -1

    def splitEmptyPartition(self, index, file):
        """
        Allocate a file to an empty partition and split it if there is still empty space remaining
        """
        # Get the selected empty partition
        empty_partition = self.partitions.pop(index)
        base = empty_partition.base
        file.disk_base = base

        # Create the new partition with the file
        new_partition = Partition(base, file.size, file)
        self.partitions.insert(index, new_partition)

        # Update the file disk metrics
        file.disk_partition = new_partition
        file.disk_percentage = file.size/self.size * 100
        self.occupation_percentage += file.disk_percentage

        # Check if there will be a new empty partition
        size = empty_partition.size - new_partition.size
        if size > 0:
            # Create the new empty partition
            empty_partition = Partition(new_partition.base + new_partition.size, size)
            self.partitions.insert(index+1, empty_partition)    


    def isFull(self):
        """
        Checks if the multiprogrammed level is already satisfied.
        """
        file_counter = 0
        for partition in self.partitions:
            if partition.file != None:
                file_counter += 1
                if file_counter >= self.n:
                    return True

        return False    
    

    def free(self, file):
        """
        Frees the disk, deleting the referenced file of the allocation list (partitions)
        """
        # Find the referenced file in the partitions list
        i = -1
        for index, partition in enumerate(self.partitions):
            if partition.file != None:
                if partition.file.name == file.name:
                    i = index
                    break
        
        # Free the partition
        self.partitions[i].file = None
        file.disk_partition = None

        # Update file disk metrics
        self.occupation_percentage -= file.disk_percentage
        file.disk_percentage = 0

        # Check if the left partition is a hole
        if i > 0:
            if self.partitions[i - 1].file == None:
                # Merge both empty partitions
                self.mergePartitions(i - 1, i)
                i -= 1
        
        # Check if the right partition is a hole
        if i + 1 < len(self.partitions):
            if self.partitions[i + 1].file == None:
                # Merge both empty partitions
                self.mergePartitions(i, i + 1)

    def reorganizeDisk(self):
        """
        Reorganizes the disk, putting together all the empty spaces
        """
        new_partitions = []
        last_partition_ending = 0
        for partition in self.partitions:
            if partition.file != None:
                partition.base = last_partition_ending
                new_partitions.append(partition)
                last_partition_ending += partition.size
            
        #Only add an empty partition if there is space remaining
        if(last_partition_ending != self.size):
            new_partitions.append(Partition(last_partition_ending, self.size))
        
        self.partitions = new_partitions

    def mergePartitions(self, i, j):
        """
        Merges partitions[i] with partition[j] and pops partitions[i]
        """
        left = self.partitions[i]
        right = self.partitions[j]

        right.base = left.base
        right.size += left.size

        self.partitions.pop(i)

    def getAcceptionRate(self):
        return self.allocations_accepted/(self.allocations_accepted+self.allocations_denied)
    
    def print(self):
        print(f"Disk ({self.size/1e3:.4}k) [")
        for partition in self.partitions:
            partition.print()
        print("]")

    def plotFileControlBlock(self, files):
        # fig = plt.figure(figsize = (15, len(job_names) * 1.2))
        fig = plt.figure(figsize = (15, 5 * 1.2))
        ax = fig.add_subplot(1,1,1)

        plt.xlabel("Tempo")
        plt.ylabel("Tamanho do Disco (bytes)")
        end_time = 0
            
        for file in files:
            job_names = []
            job_arrivals = []
            job_execution_intervals = []
            job_memory_size = []
            job_memory_base = []

            file_start = min(file.job_mix.list, key=lambda c: c.states["Joined"]).states["Joined"]
            file_finish = max(file.job_mix.list, key=lambda c: c.states["Done"]).states["Done"]
            file_execution_interval = [file_start, file_finish]

            if file_finish > end_time:
                end_time = file_finish

            x = file_execution_interval[0]
            y = file.disk_base
            width = file_finish - file_start
            default_height = file.size
            rectangle = plt.Rectangle((x, y), width, height, fc='royalblue', ec='lightsteelblue')
            print(x,y,width,height)
            ax.add_patch(rectangle)

            for job in file.job_mix.list:
                job_names.append(job.name)
                job_memory_size.append(job.size)
                job_memory_base.append(job.memory_base)

                start = job.states["Joined"]
                final = job.states["Done"]
                file_finish = final
                job_execution_intervals.append([start, final])


            for i in range(len(file.job_mix.list)):
                x = job_execution_intervals[i][0]
                y = job_memory_base[i] + file.disk_base
                width = job_execution_intervals[i][1] - job_execution_intervals[i][0]
                height = job_memory_size[i]

                rectangle = plt.Rectangle((x, y), width, height, fc='lightskyblue', ec='lightslategray')
                ax.add_patch(rectangle)

                # Plot job names
                ax.text(x + width/2, y + height/2, f"{job_names[i]}", size=15, ha = "center", va = "center")
            
        plt.axis([0, end_time + 10, 0, self.size])
        # plt.title(f"Alocação de Disco\nTaxa de alocação: {self.getAcceptionRate()*100:.2f}%")

        plt.savefig("file_control_block.jpg")  

    def plot(self):
        fig = plt.figure(figsize = (15, 6))
        ax = fig.add_subplot(1,1,1)
        ax.axes.yaxis.set_visible(False)

        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/1e3))
        ax.xaxis.set_major_formatter(ticks_x)

        ax.xaxis.set_ticks(np.arange(0, self.size+1, 1e3))

        default_height = 1e3

        plt.xlabel("Espaço em Disco (Kilo bytes)")

        for partition in self.partitions:
            # Skip over empty partitions
            if partition.file == None:
                continue

            x = partition.base
            y = 0
            width = partition.size
            rectangle = plt.Rectangle((x, y), width, default_height, fc='lightsteelblue', ec='black')
            ax.add_patch(rectangle)

            y_mult = 0.025
            sep = 0.02
            x_mult = 0.04
            current_disk_index = x #+ partition.size * x_mult
            job_amount = len(partition.file.job_mix.list) - 1

            for job in partition.file.job_mix.list:
                x = current_disk_index
                y = default_height * y_mult
                width = job.size * (1 - 2*x_mult - sep * job_amount)
                height = default_height * (1 - 2*y_mult)
                current_disk_index += width + partition.size * sep

                rectangle = plt.Rectangle((x, y), width, height, fc='red', ec='black')
                ax.add_patch(rectangle)

                # Plot job names
                ax.text(x + width/2, y + height/2, f"{job.name}", size=15, ha = "center", va = "center")
            
        plt.axis([0, self.size + 10, 0, 1e3])
        plt.title(f"Alocação de Disco")

        plt.savefig("disk.jpg")  
