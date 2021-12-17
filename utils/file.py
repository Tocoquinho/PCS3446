class File:
    def __init__(self, name, size, job_mix = None):
        self.name = name
        self.job_mix = job_mix
        self.size = size
        self.result = 0

        self.disk_partition = None
        self.disk_percentage = None


    def print(self):
        print(f"File {self.name}, {self.size/1.0e3:.4}k, {self.result}")
        job_mix.print()
