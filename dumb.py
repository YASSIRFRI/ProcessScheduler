
import Scheduler as Scheduler
import Process as Process

class RT():
    """Round Robin scheduling algorithm"""
    def __init__(self,quantum):
        self.name = "Round Robin"
        self.quantum = quantum
        
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

#1,9,1,1
#2,1,4,2
#3,18,7,3
#4,18,3,4
#5,0,9,5

def main():
    quantum = 3
    scheduler = Scheduler.Scheduler()
    alog=RT(quantum)
    scheduler.set_algorithm(alog)
    pid=[1,2,3,4,5]
    arrival_time=[9,1,18,18,0]
    burst_time=[1,4,7,3,9]
    processes = [ Process.Process(pid[i], arrival_time[i], burst_time[i]) for i in range(5)]
    scheduler.set_processes(processes)
    processes_name, start_times, duration = scheduler.run()
    print(processes_name)
    print(start_times)
    print(duration)
    


if __name__ == "__main__":
    main() 