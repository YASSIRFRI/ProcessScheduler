from abc import ABC, abstractmethod

class SchedulingAlgorithm(ABC):

    
    def __init__(self):
        pass
    
    @abstractmethod
    def schedule(self, processes):
        raise NotImplementedError
    
    


class FCFS(SchedulingAlgorithm):
    
    
    def __init__(self):
        self.name = "First-Come, First-Served"
        
    def schedule(self, processes):
        # Sort processes by arrival time
        #print the type of variable arrial_time
        processes=sorted(processes,key=lambda x: x.arrival_time)
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
    
    def __init__(self):
        self.name = "Shortest Job First"
        
    def schedule(self, processes):
        n= len(processes)
        processes.sort(key=lambda process: (process.arrival_time, process.burst_time))
        names = []
        start_times = []
        duration = []
        names.append(processes[0].pid)
        start_times.append(processes[0].arrival_time)
        duration.append(processes[0].burst_time)
        time_to_next=processes[0].arrival_time+processes[0].burst_time
        processes.remove(processes[0])
        while len(names)<n:
            candidates=[]
            for p in range(len(processes)):
                if processes[p].arrival_time<=time_to_next:
                    candidates.append(processes[p])
            if len(candidates)==0:
                time_to_next=processes[0].arrival_time
                continue
            candidates.sort(key=lambda process: process.burst_time)
            names.append(candidates[0].pid)
            start_times.append(time_to_next)
            duration.append(candidates[0].burst_time)
            time_to_next+=candidates[0].burst_time
            processes.remove(candidates[0])
        return names, start_times, duration


class Priority(SchedulingAlgorithm):
    
    """Priority scheduling algorithm"""
    
    
    def __init__(self):
        self.name = "Priority Scheduling"
        
        
    def schedule(self, processes):
        n= len(processes)
        processes.sort(key=lambda process: (process.arrival_time, -process.priority))
        names = []
        start_times = []
        duration = []
        names.append(processes[0].pid)
        start_times.append(processes[0].arrival_time)
        duration.append(processes[0].burst_time)
        time_to_next=processes[0].arrival_time+processes[0].burst_time
        processes.remove(processes[0])
        while len(names)<n:
            candidates=[]
            for p in range(len(processes)):
                if processes[p].arrival_time<=time_to_next:
                    candidates.append(processes[p])
            
            if len(candidates)==0:
                time_to_next=processes[0].arrival_time
                continue
            
            candidates.sort(key=lambda process: process.priority)
            names.append(candidates[0].pid)
            start_times.append(time_to_next)
            duration.append(candidates[0].burst_time)
            time_to_next+=candidates[0].burst_time
            processes.remove(candidates[0])
        return names, start_times, duration


class RR(SchedulingAlgorithm):
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum
        self.name = "Round Robin Scheduling"

    def schedule(self, processes):
        remaining_time = [process.burst_time for process in processes]
        names = []
        start_times = []
        duration = []
        current_time = 0
        while any(remaining_time):
            for i in range(len(processes)):
                if remaining_time[i] > 0:
                    execute_time = min(self.time_quantum, remaining_time[i])
                    names.append(processes[i].pid)
                    start_times.append(current_time)
                    duration.append(execute_time)
                    remaining_time[i] -= execute_time
                    current_time += execute_time
        return names, start_times, duration

class PriorityRR(SchedulingAlgorithm):
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum
        self .name = "Priority Round Robin Scheduling"
    def schedule(self, processes):
        remaining_time = [process.burst_time for process in processes]
        current_priorities = [process.priority for process in processes]
        
        names = []
        start_times = []
        duration = []
        current_time = 0

        while any(remaining_time):
            # Sort processes based on remaining burst time
            sorted_indices = sorted(range(len(processes)), key=lambda i: (current_priorities[i], remaining_time[i]))
            
            for idx in sorted_indices:
                if remaining_time[idx] > 0:
                    execute_time = min(self.time_quantum, remaining_time[idx])
                    names.append(processes[idx].pid)
                    start_times.append(current_time)
                    duration.append(execute_time)
                    
                    remaining_time[idx] -= execute_time
                    current_time += execute_time

                    # Update priorities based on the remaining burst time
                    current_priorities[idx] = max(1, current_priorities[idx] - 1)

        return names, start_times, duration

