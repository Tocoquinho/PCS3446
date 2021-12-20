from utils.job import Job, JobMix

import copy

class FileMapper:
    def __init__(self, file, disk):

        file = [string for string in file if string != ""]

        self.file = file
        self.disk = disk
        self.output = {
                        "SIZE": 0,
                        "JOB START": {},
                        "JOB MIX": None,
                        "DATA": [],
                        "SYSTEM ARCHITECTURE": None,
                        "RESULT": {}
                      }
        self.program_counter = 0

        self.open_scope_instructions = [
                                        "JOBMIX", 
                                        "JOB",
                                        "EXEC",
                                        "REPEAT"
                                       ]
        self.close_scope_instructions = [
                                        "ENDMIX",
                                        "ENDJOB",
                                        "ENDPROC",
                                        "ENDREP"
                                        ]
        self.scope_stack = []

        self.calculateSize()


    def calculateSize(self):
        """
        Calculate the size of the file in bytes
        """
        self.output["SIZE"] += sum([len(command) for command in self.file])


    def readInstructions(self):
        """
        Convert the list of instructions and process it
        """
       
        while self.program_counter < len(self.file):
            command = self.file[self.program_counter]

            # numeric input 
            if command[0] != "#":
                self.output["DATA"].append(float(command))

            else:
                instruction, parameters = self.translateInstruction(command)

                # Understand the instruction
                if instruction in self.open_scope_instructions:
                    self.scope_stack.append(parameters[0])
                    if instruction == "JOBMIX":
                        job_mix_mapper = JobMixMapper(self.file, self.program_counter, self.scope_stack, self.disk)
                        job_mix_output, self.program_counter, self.scope_stack = job_mix_mapper.readInstructions()
                        self.output["JOB MIX"] = job_mix_output["JOB MIX"]
                        self.output["JOB START"] = job_mix_output["JOB START"]
                        self.output["RESULT"] = job_mix_output["RESULT"]

            self.program_counter += 1


    def translateInstruction(self, command):
        """
        Gets a string "# Instruction Parameter1 Parameter2 ... ParameterN"
        and splits into instruction and [parameters]
        """
        # Split command into a instruction and [parameters]
        instruction = command.split(sep = " ", maxsplit = 2)[1]
        parameters = command.split(sep = " ")[2:]

        return instruction, parameters


class JobMixMapper(FileMapper):
    def __init__(self, file, program_counter, scope_stack, disk):
        super().__init__(file, disk)
        self.program_counter = program_counter
        self.scope_stack = scope_stack
        self.name = self.scope_stack[-1]

        self.output = {
                        "JOB MIX": JobMix(), 
                        "SIZE": 0,
                        "JOB START": {},
                        "RESULT": {}
                      }

    def readInstructions(self):
        """
        """

        self.program_counter += 1
        while self.program_counter < len(self.file):
            command = self.file[self.program_counter]
            instruction, parameters = self.translateInstruction(command)

             # Understand the instruction
            if instruction in self.open_scope_instructions:
                self.scope_stack.append(parameters[0])
                if instruction == "JOB":
                    self.output["JOB START"][parameters[0]] = sum([len(command) for command in self.file[:self.program_counter]])
                    job_mapper = JobMapper(self.file, self.program_counter, self.scope_stack, self.disk)
                    job_output, self.program_counter, self.scope_stack = job_mapper.readInstructions()
                    self.output["JOB MIX"].append(job_output["JOB"])
                    self.output["SIZE"] += job_output["SIZE"]
                    self.output["RESULT"][parameters[0]] = job_output["RESULT"]
                    
            elif instruction in self.close_scope_instructions:
                current_scope = self.scope_stack.pop()
                if instruction == "ENDMIX" and self.name == current_scope:
                    return self.output, self.program_counter, self.scope_stack

            self.program_counter += 1

class JobMapper(JobMixMapper):
    def __init__(self, file, program_counter, scope_stack, disk):
        super().__init__(file, program_counter, scope_stack, disk)
        self.arrival = 0
        self.size = self.calculateJobSize()
        self.duration = 0

        self.attributes = {
                            "BUFFER": [],
                            "LABELS": {},
                            "PROCEDURES": {},
                            "ENDPROCEDURES": {},
                            "REPEATS": {},
                            "VARIABLES": {}
                          }

        self.generateAttributes()
        
        self.output = {
                        "JOB": None,
                        "SIZE": 0,
                        "RESULT": "Finished execution"
                      }


    def calculateJobSize(self):
        """
        """
        size = 0
        start = False
        for i, command in enumerate(self.file):
            instruction, parameters = self.translateInstruction(command)
            if instruction == "JOB" and parameters[0] == self.name:
                start = i
            if start:
                size += len(command)
            if instruction == "ENDJOB" and parameters[0] == self.name:
                return size

    
    def generateAttributes(self):
        """
        Traverse the program getting all labels, procedures and repeats
        """
        for i, command in enumerate(self.file):
            instruction, parameters = self.translateInstruction(command)
            if instruction == "LABEL":
                self.attributes["LABELS"][parameters[0]] = i
            elif instruction == "PROC":
                self.attributes["PROCEDURES"][parameters[0]] = i
            elif instruction == "ENDPROC":
                self.attributes["ENDPROCEDURES"][parameters[0]] = i
            elif instruction == "REPEAT":
                self.attributes["LABELS"][parameters[0]] = i
            elif instruction == "ENDREP":
                self.attributes["REPEATS"][parameters[0]] = i
            elif instruction == "ENDJOB" and parameters[0] == self.name:
                self.attributes["END"] = i


    def readInstructions(self):
        """
        """
        self.program_counter += 1
        while self.program_counter < len(self.file):
            command = self.file[self.program_counter]
            instruction, parameters = self.translateInstruction(command)

            if instruction in self.open_scope_instructions:
                self.scope_stack.append(parameters[0])
                if instruction == "EXEC":
                    procedure_mapper = ProcedureMapper(self.file, self.program_counter, self.scope_stack, copy.deepcopy(self.attributes), self.disk)
                    procedure_output, self.scope_stack, procedure_duration = procedure_mapper.readInstructions()
                    self.duration += procedure_duration
                    self.attributes["VARIABLES"][parameters[1]] = procedure_output["RETURN"]

            elif instruction in self.close_scope_instructions:
                current_scope = self.scope_stack.pop()
                if instruction[:3] == "END" and self.name == current_scope:
                    return self.scopeReturn()

                elif instruction == "EXIT" and parameters[0] == current_scope:
                    self.program_counter = self.attributes["REPEATS"][current_scope]

            elif instruction == "PROC":
                self.program_counter = self.attributes["ENDPROCEDURES"][parameters[0]]

            elif instruction == "FILE":
                file_name = parameters[0] 

                for partition in self.disk.partitions:
                    if partition.file == None:
                        continue
                    if partition.file.name == file_name:
                        self.attributes["BUFFER"] += partition.file.data
                        
            elif instruction == "DATA":
                self.instructionDATA(parameters)

            elif instruction == "SET":
                # If second parameter is a number
                try:
                    self.attributes["VARIABLES"][parameters[0]] = float(parameters[1])
                # If second parameter is a variable
                except:
                    self.attributes["VARIABLES"][parameters[0]] = float(self.attributes["VARIABLES"][parameters[1]])

            elif instruction == "GOTO":
                self.program_counter = self.attributes["LABELS"][parameters[0]]

            elif instruction == "IF":
                label_options = parameters[1].split(sep = ',')
                if self.attributes["VARIABLES"][parameters[0]] < 0:
                    self.program_counter = self.attributes["LABELS"][label_options[0]]
                elif self.attributes["VARIABLES"][parameters[0]] == 0:
                    self.program_counter = self.attributes["LABELS"][label_options[1]]
                else:
                    self.program_counter = self.attributes["LABELS"][label_options[2]]

            elif instruction == "SPEND":
                self.duration += float(parameters[0])

            elif instruction == "INCR":
                # If parameter is a number
                    try:
                        self.attributes["VARIABLES"][parameters[0]] += float(parameters[1])
                    # If parameter is a variable
                    except:
                        self.attributes["VARIABLES"][parameters[0]] += float(self.attributes["VARIABLES"][parameters[1]])

            elif instruction == "DECR":
                # If parameter is a number
                    try:
                        self.attributes["VARIABLES"][parameters[0]] -= float(parameters[1])
                    # If parameter is a variable
                    except:
                        self.attributes["VARIABLES"][parameters[0]] -= float(self.attributes["VARIABLES"][parameters[1]])

            elif instruction == "MULT":
                # If parameter is a number
                    try:
                        self.attributes["VARIABLES"][parameters[0]] *= float(parameters[1])
                    # If parameter is a variable
                    except:
                        self.attributes["VARIABLES"][parameters[0]] *= float(self.attributes["VARIABLES"][parameters[1]])

            elif instruction == "DIVI":
                # If parameter is a number
                    try:
                        self.attributes["VARIABLES"][parameters[0]] /= float(parameters[1])
                    # If parameter is a variable
                    except:
                        self.attributes["VARIABLES"][parameters[0]] /= float(self.attributes["VARIABLES"][parameters[1]])

            elif instruction == "RETURN":
                self.instructionRETURN(parameters) 

            elif instruction == "SYSCALL":
                if parameters[0] == "result":
                    self.output["RESULT"]= f"{parameters[1]}={self.attributes['VARIABLES'][parameters[1]]}"
                elif parameters[0] == "end":
                    self.output["RESULT"] = "System call finished execution"

                self.program_counter = self.attributes["END"] - 1
                return self.scopeReturn()

            elif instruction == "ARRIVAL":
                self.arrival = float(parameters[0])
            elif instruction == "SIZE":
                self.size = float(parameters[0])
            elif instruction == "DURATION":
                self.duration = float(parameters[0])

            self.program_counter += 1


    def instructionDATA(self, parameters):
        """
        When instruction is DATA in the JOB scope, get the inputs from the buffer
        """
        for parameter in parameters:
            self.attributes["VARIABLES"][parameter] = self.attributes["BUFFER"].pop(0)


    def instructionRETURN(self):
        """
        Do nothing when instruction RETURN is inside a JOB
        """
        pass


    def scopeReturn(self):
        """
        Return the information generated by the job mapper
        """
        self.output["JOB"] = Job(self.name, self.arrival, self.size, self.duration)
        self.output["SIZE"] = self.size
        
        return self.output, self.program_counter, self.scope_stack


class RepeatMapper(JobMapper):
    def __init__(self, file, program_counter, scope_stack, attributes, disk):
        super().__init__(file, program_counter, scope_stack, disk)
        self.attributes = attributes
        self.program_counter = attributes["REPEATS"][self.name][0]

    
    def scopeReturn(self):
        """
        Return the information generated by the repeat mapper
        """
        return self.attributes, self.duration
        



class ProcedureMapper(JobMapper):
    def __init__(self, file, program_counter, scope_stack, attributes, disk):
        super().__init__(file, program_counter, scope_stack, disk)
        _, self.inputs = self.translateInstruction(self.file[self.program_counter])
        self.attributes = attributes
        self.program_counter = attributes["PROCEDURES"][self.name]
        
        self.output = {
                        "RETURN": None
                      }


    def instructionDATA(self, parameters):
        """
        """
        local_variables = self.attributes["VARIABLES"]
        for i, variable in enumerate(parameters):
            # If parameter is a number
            try:
                local_variables[variable] = float(self.inputs[i + 2])
            # If parameter is a variable
            except:
                local_variables[variable] = float(self.attributes["VARIABLES"][self.inputs[i + 2]])
        self.attributes["VARIABLES"] = local_variables
    

    def instructionRETURN(self, parameters):
        """
        Set the correct return variable when instruction RETURN is inside a PROC
        """
        self.output["RETURN"] = self.attributes["VARIABLES"][parameters[0]]


    def scopeReturn(self):
        """
        Return the information generated by the procedure mapper
        """
        return self.output, self.scope_stack, self.duration
