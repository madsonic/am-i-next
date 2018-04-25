
## Task 1
[Simulation Repo Link](https://github.com/madsonic/am-i-next)

## Task 2
### Qns 1
Least average time scheduler: SJF<br>
SJF 7.12<br>
RR 8.75

optimal Q:10<br>
optimal α: 0.5

![chart](https://i.imgur.com/xUGegXC.png)
### Qns 2a
Any scheduler would give roughly the same outcome, since they are short. But FCFS would be the simplest of all.

### Qns 2b
SRTF gives the best waiting time as it eagerly serves short procesess and comes back to long processes whenever possible. Given that it is interleaving, long processes would get serve quickly and would not starve.

### Qns 3
The scheduler will sit in front of all the cores and it would need to access the run queue of each core so that it would be able to load balance and utilise the cores efficiently. Otherwise the scheduler can used as is.
