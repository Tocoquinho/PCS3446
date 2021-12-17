class File:
    def __init__(self, name, job_mix, size):
        self.name = name
        self.job_mix = job_mix
        self.size = size
        self.result = 0

    def print(self):
        print(f"File {self.name}, {self.size/1.0e3:.4}k, {self.result}")
        job_mix.print()
