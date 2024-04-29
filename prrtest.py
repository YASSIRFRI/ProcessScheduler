import Scheduler as Scheduler
import Process as Process
from SchedulingAlgorithm import SchedulingAlgorithm



class PriorityRR(SchedulingAlgorithm):

    def __init__(self, time_quantum):
        self.quantum = time_quantum
        self.name = "Priority with Round Robin Scheduling"

    def check_all_queues_empty(self, queues):
        for queue in queues:
            if queue:
                return False
        return True

    def schedule(self, processes):
        names = []
        start_times = []
        duration = []

        # Create queues for each priority level (up to 100 for simplicity)
        queues = [[] for _ in range(100)]

        current_time = 0

        # Sort processes by arrival time and then priority (descending)
        processes.sort(key=lambda process: (process.arrival_time, -process.priority))

        while not self.check_all_queues_empty(queues) or current_time == 0:

            # Add arriving processes to their respective queues
            for process in processes:
                if process.arrival_time <= current_time:
                    queues[process.priority].append(process)

            # Process each queue using round robin
            for i in range(len(queues)):
                queue = queues[i]
                for _ in range(len(queue)):  # Process elements in the queue until empty
                    if not queue:
                        break
                    process = queue.pop(0)
                    names.append(process.pid)
                    start_times.append(current_time)
                    if process.burst_time > self.quantum:
                        duration.append(self.quantum)
                        process.burst_time -= self.quantum
                        queue.append(process)  # Add remaining process back to the queue
                        current_time += self.quantum
                    else:
                        duration.append(process.burst_time)
                        current_time += process.burst_time

        return names, start_times, duration






#1,9,1,1
#2,1,4,2
#3,18,7,3
#4,18,3,4
#5,0,9,5

def main():
    quantum = 2 #3
    scheduler = Scheduler.Scheduler()
    alog=PriorityRR(quantum)
    scheduler.set_algorithm(alog)
    pid=["P1","P2","P3","P4","P5"]
    arrival_time=[0,0,0,0,0]#[9,1,18,18,0]
    burst_time=[4,5,8,7,3]#[1,4,7,3,9]
    priorities=[3,2,2,1,3]#[1,2,1,3,2]
    processes = [ Process.Process(pid[i], arrival_time[i], burst_time[i], priorities[i]) for i in range(5)]
    scheduler.set_processes(processes)
    processes_name, start_times, duration = scheduler.run()
    print(processes_name)
    print(start_times)
    print(duration)



if __name__ == "__main__":
    main() 