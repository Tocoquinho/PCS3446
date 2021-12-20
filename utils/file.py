class File:
    def __init__(self, name, job_mix, size = 0):
        self.name = name
        self.job_mix = job_mix
        self.result = 0

        # set file size based on jobs size
        if size == 0:
            for job in job_mix.list:
                size += job.size
        self.size = size

        self.disk_partition = None
        self.disk_percentage = None
        self.disk_base = 0


    def print(self):
        print(f"File {self.name}, {self.size/1.0e3:.4}k, {self.result}")
        job_mix.print()
