class Scheduler:
    def __init__(self):
        self.algorithm = None
        self.processes = []
        
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        
    def get_algorithm(self):
        return self.algorithm
    
    def set_processes(self, processes):
        self.processes = processes

    def run(self):
        if self.algorithm is None:
            raise ValueError("No scheduling algorithm set")
        return self.algorithm.schedule(self.processes)