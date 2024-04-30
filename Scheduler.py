class Scheduler:
    """Scheduler class for executing scheduling algorithms."""

    def __init__(self):
        """Initialize the Scheduler."""
        self.algorithm = None
        self.processes = []
        
    def set_algorithm(self, algorithm):
        """Set the scheduling algorithm.

        Args:
            algorithm (SchedulingAlgorithm): An instance of a scheduling algorithm.
        """
        self.algorithm = algorithm
        
    def get_algorithm(self):
        """Get the currently set scheduling algorithm.

        Returns:
            SchedulingAlgorithm: The currently set scheduling algorithm.
        """
        return self.algorithm
    
    def set_processes(self, processes):
        """Set the processes to be scheduled.

        Args:
            processes (list): List of Process objects to be scheduled.
        """
        self.processes = processes

    def run(self):
        """Run the scheduling algorithm.

        Returns:
            tuple: A tuple containing lists of process names, start times, and durations.
        """
        if self.algorithm is None:
            raise ValueError("No scheduling algorithm set")
        return self.algorithm.schedule(self.processes)
