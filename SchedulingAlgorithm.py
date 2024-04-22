from abc import ABC, abstractmethod

class SchedulingAlgorithm(ABC):

    @abstractmethod
    def schedule(self, processes):
        raise NotImplementedError
    


class FCFS(SchedulingAlgorithm):
    def schedule(self, processes):
        # Sort the processes by arrival time
        processes.sort(key=lambda process: process.arrival_time)
        names=[]
        start_times=[]
        duration=[]
        names.append(processes[0].pid)
        start_times.append(processes[0].arrival_time)
        duration.append(processes[0].burst_time)
        for p in range(1,len(processes)):
            names.append(processes[p].pid)
            start_times.append(max(start_times[p-1]+duration[p-1],processes[p].arrival_time))
            duration.append(processes[p].burst_time)
        return names,start_times,duration


class SJF(SchedulingAlgorithm):
    def schedule(self, processes):
        # Sort the processes by burst time
        processes.sort(key=lambda process: process['burst_time'])
        return processes
    

class Priority(SchedulingAlgorithm):
    def schedule(self, processes):
        # Sort the processes by priority
        processes.sort(key=lambda process: process['priority'])
        return processes


    