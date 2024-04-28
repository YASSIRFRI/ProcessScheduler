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
        self.quantum = time_quantum
        self.name = "Round Robin Scheduling"
        
    def schedule(self, processes):
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
        next_idx=1
        while len(queue)>0:
            in_queue = queue.pop(0)
            names.append(in_queue.pid)
            start_times.append(time_to_next)
            if in_queue.remaining_time> self.quantum:
                duration.append(self.quantum)
                in_queue.remaining_time-=self.quantum
                time_to_next+=self.quantum
            else:
                duration.append(in_queue.remaining_time)
                time_to_next+=in_queue.remaining_time
                in_queue.remaining_time = 0
            to_enqueue=[]
            while next_idx<n and processes[next_idx].arrival_time<=time_to_next:
                to_enqueue.append(processes[next_idx])
                next_idx+=1
            queue.extend(to_enqueue)
            if in_queue.remaining_time>0:
                queue.append(in_queue)
            else: 
                if len(queue)==0:
                    if next_idx<n:
                        queue.append(processes[next_idx])
                        time_to_next=processes[next_idx].arrival_time
                        next_idx+=1
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

