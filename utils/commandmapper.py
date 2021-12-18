from os import read
from utils.job import Job, JobMix

class CommandMapper:
    def __init__(self, file):
        self.file = file
        self.output = {
                        "SIZE": 0,
                        "JOBMIX": None, 
                        "SYSTEM ARCHITECTURE": None,
                        "RESULT": None
                      }

        self.program_counter = 0
        self.open_scope_instructions = [
                                        "JOBMIX", 
                                        "JOB"
                                       ]
        self.close_scope_instructions = [
                                        "ENDMIX",
                                        "ENDJOB"
                                        ]
        self.scope_stack = []


    def readFile(self):
        """
        Gets a list of strings (file) and converts it to the mapper output
        """
        self.output["SIZE"] += sum([len(command) * 8 for command in self.file])

        while self.program_counter < len(self.file):
            command = self.file[self.program_counter]    
            instruction, parameters = self.readCommand(command)

            # Understand the instruction
            if instruction in self.open_scope_instructions:
                self.scope_stack.append(parameters[0])
                if instruction == "JOBMIX":
                    self.readJobMix()
            else:
                pass

            self.program_counter += 1
    

    def readCommand(self, command):
        """
        Gets a string "# Instruction Parameter1 Parameter2 ... ParameterN",
        calculates its size in bits and splits into instruction and [parameters]
        """
        # Add bit count of the command to the total count (ASCII)
        command_size = len(command) * 8

        # Split command into a instruction and [parameters]
        instruction = command.split(sep = " ", maxsplit = 2)[1]
        parameters = command.split(sep = " ")[2:]

        return instruction, parameters


    def readJobMix(self):
        name = self.scope_stack[-1]
        self.output["JOBMIX"] = JobMix()

        self.program_counter += 1
        while self.program_counter < len(self.file):
            command = self.file[self.program_counter]
            instruction, parameters = self.readCommand(command)

             # Understand the instruction
            if instruction in self.open_scope_instructions:
                self.scope_stack.append(parameters[0])
                if instruction == "JOB":
                    self.readJob()

            elif instruction in self.close_scope_instructions:
                current_scope = self.scope_stack.pop()
                if instruction == "ENDMIX" and name == current_scope:
                    break
            else:
                pass

            self.program_counter += 1


    def readJob(self):
        name = self.scope_stack[-1]
        arrival = None
        size = 0
        duration = 0

        labels = {}
        procedures = {}
        buffer = []
        variables = {}
        
        # Get all labels and procedures
        for i, command in enumerate(self.file):
            command = self.file[i]
            instruction, parameters = self.readCommand(command)
            if instruction == "LABEL":
                labels[parameters[0]] = i
            elif instruction == "PROC":
                procedures[parameters[0]] = i
            
        # Read and execute job
        self.program_counter += 1
        while self.program_counter < len(self.file):
            command = self.file[self.program_counter]
            instruction, parameters = self.readCommand(command)

            if instruction in self.open_scope_instructions:
                pass

            elif instruction in self.close_scope_instructions:
                current_scope = self.scope_stack.pop()
                if instruction == "ENDJOB" and name == current_scope:
                    job = Job(name, arrival, size, duration)
                    self.output["JOBMIX"].append(job)
                    break

            elif instruction == "FILE":
                # TODO: Create a function to fetch and read another file
                # Temporary solution(
                file_path = "../" + parameters[0] 
                file = open(file_path, "r")
                file = [line.rstrip() for line in file.readlines()]
                file = [float(string) for string in file if string != ""]
                buffer += file
                # )Temporary solution

            elif instruction == "DATA":
                for parameter in parameters:
                    variables[parameter] = buffer.pop(0)

            elif instruction == "SET":
                variables = self.readSet(variables, parameters)

            elif instruction == "GOTO":
                self.program_counter = labels[parameters[0]]

            elif instruction == "IF":
                label_options = parameters[1].split(sep = ',')
                if variables[parameters[0]] < 0:
                    self.program_counter = labels[label_options[0]]
                elif variables[parameters[0]] == 0:
                    self.program_counter = labels[label_options[1]]
                else:
                    self.program_counter = labels[label_options[2]]

            elif instruction == "EXEC":
                self.readProcedure(duration, variables, procedures, parameters)

            elif instruction == "ARRIVAL":
                arrival = float(parameters[0])
            elif instruction == "SIZE":
                size = float(parameters[0])
            elif instruction == "DURATION":
                duration = float(parameters[0])

            self.program_counter += 1
            print(variables)


    def readSet(self, variables, parameters):
        # If second parameter is a number
        try:
            variables[parameters[0]] = float(parameters[1])
        # If second parameter is a variable
        except:
            variables[parameters[0]] = float(variables[parameters[1]])

        return variables
    

    def readProcedure(self, duration, global_variables, procedures, inputs):
        name = inputs[0]
        program_counter = procedures[name] + 1
        
        local_variables = {}

        instruction = ""
        parameters = [None]
        while instruction != "ENDPROC" and parameters[0] != name:
            command = self.file[program_counter]
            instruction, parameters = self.readCommand(command)

            if instruction == "DATA":
                for i, variable in enumerate(parameters):
                    # If parameter is a number
                    try:
                        local_variables[variable] = float(inputs[i + 2])
                    # If parameter is a variable
                    except:
                        local_variables[variable] = float(global_variables[inputs[i + 2]])

            elif instruction == "SPEND":
                duration += float(parameters[0])
            
            elif instruction == "SET":
                local_variables = self.readSet(local_variables, parameters)

            elif instruction == "RETURN":
                global_variables[inputs[1]] = local_variables[parameters[0]]

            elif instruction == "INCR":
                # If parameter is a number
                    try:
                        local_variables[parameters[0]] += float(parameters[1])
                    # If parameter is a variable
                    except:
                        local_variables[parameters[0]] += float(local_variables[parameters[1]])

            elif instruction == "DECR":
                # If parameter is a number
                    try:
                        local_variables[parameters[0]] -= float(parameters[1])
                    # If parameter is a variable
                    except:
                        local_variables[parameters[0]] -= float(local_variables[parameters[1]])

            elif instruction == "MULT":
                # If parameter is a number
                    try:
                        local_variables[parameters[0]] *= float(parameters[1])
                    # If parameter is a variable
                    except:
                        local_variables[parameters[0]] *= float(local_variables[parameters[1]])

            elif instruction == "DIVI":
                # If parameter is a number
                    try:
                        local_variables[parameters[0]] /= float(parameters[1])
                    # If parameter is a variable
                    except:
                        local_variables[parameters[0]] /= float(local_variables[parameters[1]])

            program_counter += 1
        return duration, global_variables


if __name__ == "__main__":
    file_path = "../example2.txt"
    file = open(file_path, "r")
    file = [line.rstrip() for line in file.readlines()]
    file = [string for string in file if string != ""]

    command_mapper = CommandMapper(file)
    command_mapper.readFile()
    print(command_mapper.output)
    for job in command_mapper.output["JOBMIX"].list:
        print(job.name, job.arrival, job.size, job.duration)
