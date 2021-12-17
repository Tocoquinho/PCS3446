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
