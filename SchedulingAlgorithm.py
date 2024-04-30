from abc import ABC, abstractmethod

class SchedulingAlgorithm(ABC):
    """Abstract base class for scheduling algorithms."""

    def __init__(self):
        pass
    
    @abstractmethod
    def schedule(self, processes):
        """Abstract method to schedule processes."""
        raise NotImplementedError

class FCFS(SchedulingAlgorithm):
    """First-Come, First-Served scheduling algorithm."""
    
    def __init__(self):
        self.name = "First-Come, First-Served"
        
    def schedule(self, processes):
        """Schedule processes using First-Come, First-Served algorithm.

        Args:
            processes (list): List of Process objects to be scheduled.

        Returns:
            tuple: A tuple containing lists of process names, start times, and durations.
        """
        # Sort processes by arrival time
        processes = sorted(processes, key=lambda x: x.arrival_time)
        names = []
        start_times = []
        duration = []

        # Initialize lists with the first process
        names.append(processes[0].pid)
        start_times.append(processes[0].arrival_time)
        duration.append(processes[0].burst_time)

        for p in range(1, len(processes)):
            names.append(processes[p].pid)
            start_times.append(max(start_times[p - 1] + duration[p - 1], processes[p].arrival_time))
            duration.append(processes[p].burst_time)

        return names, start_times, duration

class SJF(SchedulingAlgorithm):
    """Shortest Job First scheduling algorithm."""
    
    def __init__(self):
        self.name = "Shortest Job First"
        
    def schedule(self, processes):
        """Schedule processes using Shortest Job First algorithm.

        Args:
            processes (list): List of Process objects to be scheduled.

        Returns:
            tuple: A tuple containing lists of process names, start times, and durations.
        """
        n = len(processes)
        processes.sort(key=lambda process: (process.arrival_time, process.burst_time))
        names = []
        start_times = []
        duration = []

        # Initialize lists with the first process
        names.append(processes[0].pid)
        start_times.append(processes[0].arrival_time)
        duration.append(processes[0].burst_time)
        time_to_next = processes[0].arrival_time + processes[0].burst_time
        processes.remove(processes[0])

        while len(names) < n:
            candidates = []
            for p in range(len(processes)):
                if processes[p].arrival_time <= time_to_next:
                    candidates.append(processes[p])

            if len(candidates) == 0:
                time_to_next = processes[0].arrival_time
                continue

            candidates.sort(key=lambda process: process.burst_time)
            names.append(candidates[0].pid)
            start_times.append(time_to_next)
            duration.append(candidates[0].burst_time)
            time_to_next += candidates[0].burst_time
            processes.remove(candidates[0])

        return names, start_times, duration

class Priority(SchedulingAlgorithm):
    """Priority scheduling algorithm."""
    
    def __init__(self):
        self.name = "Priority Scheduling"
        
    def schedule(self, processes):
        """Schedule processes using Priority Scheduling algorithm.

        Args:
            processes (list): List of Process objects to be scheduled.

        Returns:
            tuple: A tuple containing lists of process names, start times, and durations.
        """
        n = len(processes)
        processes.sort(key=lambda process: (process.arrival_time, -process.priority))
        names = []
        start_times = []
        duration = []

        # Initialize lists with the first process
        names.append(processes[0].pid)
        start_times.append(processes[0].arrival_time)
        duration.append(processes[0].burst_time)
        time_to_next = processes[0].arrival_time + processes[0].burst_time
        processes.remove(processes[0])

        while len(names) < n:
            candidates = []
            for p in range(len(processes)):
                if processes[p].arrival_time <= time_to_next:
                    candidates.append(processes[p])
            
            if len(candidates) == 0:
                time_to_next = processes[0].arrival_time
                continue
            
            candidates.sort(key=lambda process: process.priority)
            names.append(candidates[0].pid)
            start_times.append(time_to_next)
            duration.append(candidates[0].burst_time)
            time_to_next += candidates[0].burst_time
            processes.remove(candidates[0])

        return names, start_times, duration

class RR(SchedulingAlgorithm):
    """Round Robin Scheduling algorithm."""
    
    def __init__(self, time_quantum):
        self.quantum = time_quantum
        self.name = "Round Robin Scheduling"
    
    def schedule(self, processes):
        """Schedule processes using Round Robin Scheduling algorithm.

        Args:
            processes (list): List of Process objects to be scheduled.

        Returns:
            tuple: A tuple containing lists of process names, start times, and durations.
        """
        processes.sort(key=lambda process: process.arrival_time)
        n = len(processes)
        queue = []
        names = []
        start_times = []
        duration = []

        for i in range(n):
            processes[i].remaining_time = processes[i].burst_time

        time_to_next = processes[0].arrival_time
        queue.append(processes[0])
        next_idx = 1

        while len(queue) > 0:
            in_queue = queue.pop(0)
            names.append(in_queue.pid)
            start_times.append(time_to_next)

            if in_queue.remaining_time > self.quantum:
                duration.append(self.quantum)
                in_queue.remaining_time -= self.quantum
                time_to_next += self.quantum
            else:
                duration.append(in_queue.remaining_time)
                time_to_next += in_queue.remaining_time
                in_queue.remaining_time = 0

            to_enqueue = []
            while next_idx < n and processes[next_idx].arrival_time <= time_to_next:
                to_enqueue.append(processes[next_idx])
                next_idx += 1
            queue.extend(to_enqueue)

            if in_queue.remaining_time > 0:
                queue.append(in_queue)
            else:
                if len(queue) == 0:
                    if next_idx < n:
                        queue.append(processes[next_idx])
                        time_to_next = processes[next_idx].arrival_time
                        next_idx += 1

        return names, start_times, duration

class PriorityRR(SchedulingAlgorithm):
    """Priority with Round Robin Scheduling algorithm."""
    
    def __init__(self, time_quantum):
        self.quantum = time_quantum
        self.name = "Priority with Round Robin Scheduling"

    def check_all_queues_empty(self, queues):
        for queue in queues:
            if queue:
                return False
        return True

    def schedule(self, processes):
        """Schedule processes using Priority with Round Robin Scheduling algorithm.

        Args:
            processes (list): List of Process objects to be scheduled.

        Returns:
            tuple: A tuple containing lists of process names, start times, and durations.
        """
        names = []
        start_times = []
        duration = []
        processes.sort(key=lambda process: (process.arrival_time, process.priority))
        max_priority = max([process.priority for process in processes])
        queues = [[] for _ in range(max_priority + 1)]
        rrqueues = [[] for _ in range(max_priority + 1)]
        for process in processes:
            queues[process.priority].append(process)
        time_to_next = processes[0].arrival_time
        current_queue = processes[0].priority
        rrqueues[current_queue].append(queues[current_queue].pop(0))
        while not self.check_all_queues_empty(rrqueues):
            to_execute = rrqueues[current_queue].pop(0)
            names.append(to_execute.pid)
            start_times.append(time_to_next)
            if to_execute.remaining_time > self.quantum:
                duration.append(self.quantum)
                to_execute.remaining_time -= self.quantum
                time_to_next += self.quantum
            else:
                duration.append(to_execute.remaining_time)
                time_to_next += to_execute.remaining_time
                to_execute.remaining_time = 0
            for i in range(len(queues)):
                if queues[i]:
                    for process in queues[i]:
                        if process.arrival_time <= time_to_next:
                            rrqueues[i].append(queues[i].pop(0))
            if to_execute.remaining_time > 0:
                rrqueues[current_queue].append(to_execute)
            more_priorities = False
            for i in range(1, current_queue):
                if rrqueues[i]:
                    more_priorities = True
                    current_queue = i
                    break
            if more_priorities or rrqueues[current_queue]:
                continue
            else:
                less_priorities = False
                for i in range(current_queue + 1, max_priority + 1):
                    if rrqueues[i]:
                        less_priorities = True
                        current_queue = i
                        break
            if not more_priorities and not less_priorities:
                found_next = False
                time_to_next = 1000000
                for i in range(1, max_priority + 1):
                    if queues[i] and queues[i][0].arrival_time < time_to_next:
                        time_to_next = queues[i][0].arrival_time
                        found_next = True
                        current_queue = i
                if not found_next:
                    nxt = 1
                    for i in range(1, max_priority + 1):
                        if queues[i]:
                            if queues[i][0].arrival_time < time_to_next:
                                nxt = i
                                found_next = True
                                time_to_next = queues[i][0].arrival_time
                    if not found_next:
                        break
                    else:
                        rrqueues[nxt].append(queues[nxt].pop(0))
                else:
                    rrqueues[current_queue].append(queues[current_queue].pop(0))

        return names, start_times, duration
