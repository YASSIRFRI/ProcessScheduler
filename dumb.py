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
        processes.sort(key=lambda process: (process.arrival_time, process.priority))
        #priority 1 is the highest
        max_priority = max([process.priority for process in processes])
        queues=[[] for _ in range(max_priority+1)]
        rrqueues =[[] for _ in range(max_priority+1)]
        for process in processes:
            queues[process.priority].append(process)
        print(queues)
        time_to_next = processes[0].arrival_time
        current_queue = processes[0].priority
        rrqueues[current_queue].append(queues[current_queue].pop(0))
        while not self.check_all_queues_empty(rrqueues):
            to_execute=rrqueues[current_queue].pop(0)
            names.append(to_execute.pid)
            start_times.append(time_to_next)
            if to_execute.remaining_time>self.quantum:
                duration.append(self.quantum)
                to_execute.remaining_time-=self.quantum
                time_to_next+=self.quantum
            else:
                duration.append(to_execute.remaining_time)
                time_to_next+=to_execute.remaining_time
                to_execute.remaining_time=0
            for i in range(len(queues)):
                if queues[i]:
                    for process in queues[i]:
                        if process.arrival_time<=time_to_next:
                            rrqueues[i].append(queues[i].pop(0))
            if to_execute.remaining_time>0:
                rrqueues[current_queue].append(to_execute)
            more_priorities=False
            for i in range(1,current_queue):
                if rrqueues[i]:
                    more_priorities=True
                    current_queue=i
                    break
            if more_priorities or rrqueues[current_queue]:
                continue
            else:
                less_priorities=False
                for i in range(current_queue+1,max_priority+1):
                    if rrqueues[i]:
                        less_priorities=True
                        current_queue=i
                        break
            if not more_priorities and not less_priorities :
                found_next=False
                time_to_next=1000000
                for i in range(1,max_priority+1):
                    if queues[i] and queues[i][0].arrival_time<time_to_next:
                        time_to_next=queues[i][0].arrival_time
                        found_next=True
                        current_queue=i
                if not found_next:
                    nxt=1
                    for i in range(1,max_priority+1):
                        if queues[i]:
                            if queues[i][0].arrival_time<time_to_next:
                                nxt=i
                                found_next=True
                                time_to_next=queues[i][0].arrival_time
                    if not found_next:
                        break
                    else:
                        rrqueues[nxt].append(queues[nxt].pop(0))
                else:
                    rrqueues[current_queue].append(queues[current_queue].pop(0))
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
    arrival_time=[0,0,0,10,0]#[9,1,18,18,0]
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