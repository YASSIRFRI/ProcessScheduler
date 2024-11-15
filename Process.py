class Process:
    """Process class representing a process for scheduling."""

    def __init__(self, pid=None, arrival_time=None, burst_time=None, priority=None):
        """Initialize the Process.

        Args:
            pid (int): Process ID.
            arrival_time (float): Arrival time of the process.
            burst_time (float): Burst time of the process.
            priority (int): Priority of the process.
        """
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.priority = priority

    def __str__(self):
        """Return string representation of the process."""
        return f"Process {self.pid} - Arrival Time: {self.arrival_time}, Burst Time: {self.burst_time}, Remaining Time: {self.remaining_time}, Waiting Time: {self.waiting_time}, Turnaround Time: {self.turnaround_time}"

    def __repr__(self):
        """Return string representation of the process."""
        return f"Process {self.pid} - Arrival Time: {self.arrival_time}, Burst Time: {self.burst_time}, Remaining Time: {self.remaining_time}, Waiting Time: {self.waiting_time}, Turnaround Time: {self.turnaround_time}"
    
    def __lt__(self, other):
        """Comparison method for sorting processes based on arrival time."""
        return self.arrival_time < other.arrival_time
    
    def serialize(self):
        """Serialize the process attributes."""
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time
        }
    
    def deserialize(self, data):
        """Deserialize the process attributes from given data."""
        if "pid" not in data:
            raise ValueError("Process ID not found in data")
        self.pid = data["pid"]
        if "arrival_time" not in data:
            raise ValueError("Arrival time not found in data")
        self.arrival_time = data["arrival_time"]
        if "burst_time" not in data:
            raise ValueError("Burst time not found in data")
        self.burst_time = data["burst_time"]
        if "remaining_time" in data:
            self.remaining_time = data["remaining_time"]
        if "waiting_time" in data:
            self.waiting_time = data["waiting_time"]
        if "turnaround_time" in data:
            self.turnaround_time = data["turnaround_time"]
        return self
    
    def setStartTime(self, time):
        """Set the start time of the process."""
        self.start_time = time
