from abc import ABC, abstractmethod

class SchedulingAlgorithm(ABC):

    @abstractmethod
    def schedule(self, processes):
        raise NotImplementedError
    


class FCFS(SchedulingAlgorithm):
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
    def schedule(self, processes):
        n= len(processes)
        processes.sort(key=lambda process: (process.arrival_time, process.priority))
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

    