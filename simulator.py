'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys

from collections import deque
from heapq import heappush, heappop
from copy import deepcopy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time, time_slice = 0, prediction = 5):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time

    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

class ProcessRR(Process):
    def __init__(self, id, arrive_time, burst_time, time_slice = 0):
        super().__init__(id, arrive_time, burst_time)
        self.time_slice = time_slice

class ProcessSRTF(Process):
    def __lt__(self, other):
        return self.burst_time < other.burst_time

class ProcessSJF(Process):
    def __init__(self, id, arrive_time, burst_time, prediction = 5):
        super().__init__(id, arrive_time, burst_time)
        self.prediction = prediction

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.prediction < other.prediction

    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d, prediction %.3f]'%(self.id, self.arrive_time, self.burst_time, self.prediction))


def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in deepcopy(process_list):
        if (current_time < process.arrive_time):
            current_time = process.arrive_time

        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time

    average_waiting_time = waiting_time / float(len(process_list))

    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    """
    Time quantum should be a positive number
    Running task that has left over burst time will run first even if there
    is a new process that arrives due to the way 'leftover' task are queued

    Loop invariant 1: nothing is ever inserted back to the processes queue

    Loop invariant 2: A process burst time is decremented when it runs, eventually, no tasks will be requeued and ready_queue will become empty
    """
    if time_quantum < 1:
        return "time_quantum should be a positive integer"

    rr_process_list = \
        [ProcessRR(p.id, p.arrive_time, p.burst_time, time_quantum)
         for p
         in deepcopy(process_list)]
    processes = deque(rr_process_list)
    ready_queue = deque([]) # uses a queue
    running = None
    schedule = []
    current_time = 0
    waiting_time = 0
    num_processes = len(processes)

    while processes or ready_queue:
        # new process ready
        if processes and current_time == processes[0].arrive_time:
            ready_queue.append(processes.popleft())

        # interrupt / yield
        if running:
            if running.time_slice == 0: # end of time slice
                # requeue if uncompleted
                if running.burst_time > 0:
                    running.arrive_time = current_time
                    ready_queue.append(running)

                running = None
            elif running.burst_time == 0: # completed
                running = None

        # find something to run if idling
        if not running and ready_queue:
            running = ready_queue.popleft()
            running.time_slice = time_quantum
            waiting_time += current_time - running.arrive_time
            schedule.append((current_time, running.id))

        # run the process
        if running:
            running.burst_time -= 1
            running.time_slice -= 1

        # tick
        current_time += 1

    average_waiting_time = waiting_time / float(num_processes)

    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    srtf_process_list = \
        [ProcessSRTF(p.id, p.arrive_time, p.burst_time)
         for p
         in deepcopy(process_list)]
    processes = deque(srtf_process_list)
    ready_queue = [] # uses a min heap
    running = None
    schedule = []
    current_time = 0
    waiting_time = 0
    num_processes = len(processes)

    while processes or ready_queue:
        # new process ready
        if processes and current_time == processes[0].arrive_time:
            newProcess = processes.popleft()

            # pre-empt
            if not running:
                running = newProcess
                waiting_time += current_time - running.arrive_time
                schedule.append((current_time, running.id))
            elif newProcess.burst_time < running.burst_time:
                if running.burst_time > 0:
                    running.arrive_time = current_time
                    heappush(ready_queue, running)

                running = newProcess
                waiting_time += current_time - running.arrive_time
                schedule.append((current_time, running.id))
            else:
                heappush(ready_queue, newProcess)

        # complete
        if running and running.burst_time == 0:
            if ready_queue:
                running = heappop(ready_queue)
                waiting_time += current_time - running.arrive_time
                schedule.append((current_time, running.id))
            else:
                running = None # idle

        # run the process
        if running:
            running.burst_time -= 1

        # tick
        current_time += 1

    average_waiting_time = waiting_time / float(num_processes)

    return schedule, average_waiting_time

def SJF_scheduling(process_list, alpha):
    processes = deque(deepcopy(process_list))
    ready_queue = [] # uses a min heap
    running = None
    schedule = []
    processStat = {}
    current_time = 0
    waiting_time = 0
    num_processes = len(processes)

    while processes or ready_queue:
        # new process ready
        if processes and current_time == processes[0].arrive_time:
            newProcess = processes.popleft()

            # retrive record and update prediction
            if newProcess.id in processStat:
                record = processStat[newProcess.id]
                prediction = predict(record.burst_time, record.prediction, alpha)
                record.arrive_time = newProcess.arrive_time
                record.burst_time = newProcess.burst_time
                record.prediction = prediction
                processStat[record.id] = record
            else:
                newRecord = ProcessSJF(newProcess.id, newProcess.arrive_time, newProcess.burst_time, prediction = 5)
                processStat[newProcess.id] = newRecord

            # schedule
            if not running:
                running = newProcess
                waiting_time += current_time - running.arrive_time
                schedule.append((current_time, running.id))
            else:
                heappush(ready_queue, processStat[newProcess.id])

        # complete
        if running and running.burst_time == 0:
            if ready_queue:
                next = heappop(ready_queue)
                running = Process(next.id, next.arrive_time, next.burst_time)
                waiting_time += current_time - running.arrive_time
                schedule.append((current_time, running.id))
            else:
                running = None # idle

        # run the process
        if running:
            running.burst_time -= 1

        # tick
        current_time += 1

    average_waiting_time = waiting_time / float(num_processes)

    return schedule, average_waiting_time

def predict(actual_burst_time, predicted_burst_time, alpha):
    """
    Returns the prediction of running time using exponential averaging
    T(n+1) = at(n) + (1-a)T(n)
    where a = weight, T = predicted value, t = actual value
    """
    return alpha * actual_burst_time + (1 - alpha) * predicted_burst_time


def read_input():
    """
    each line in input file will be read as
    pid arriving_time burst_time
    """
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))

    return result

def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f\n'%(avg_waiting_time))

def main(argv):
    process_list = read_input()

    print ("printing input ----")
    for process in process_list:
        print (process)

    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('output/FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )

    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list, time_quantum = 7)
    write_output('output/RR.txt', RR_schedule, RR_avg_waiting_time )

    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('output/SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )

    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('output/SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
