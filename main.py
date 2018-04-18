import xmltodict
from sys import argv
from random import randint
from collections import defaultdict
from blist import sortedlist

def read_xml(fname):
    return xmltodict.parse(open(fname).read())

class Task(object):
    
    def __init__(self, x):
        self.name = x['@name']
        self.duration = int(x['@duration'])
        self.period = int(x['@period'])
        # longer period -> lower prior
        self.prior = -self.period
        self.done = 0

def main():
    data = read_xml(argv[1])
    out = open(argv[2], 'w')
    runtime = int(data['system']['@runtime'])
    out.write(f'<trace runtime="{runtime}">\n')
    prior_to_tasks = defaultdict(sortedlist)
    id_to_task = dict()
    num_tasks = len(data['system']['task'])
    for i, task in enumerate(data['system']['task']):
        # prior->sortedlist(ready_time, id)
        cur = Task(task)
        prior_to_tasks[cur.prior].add((0, i))
        # id->task last item is time in [0, duration]
        id_to_task[i] = cur
    priors = sorted(prior_to_tasks.keys(), reverse=True)
    t = 0
    while t < runtime:
        # min time to swap tasks
        any_task = 0
        pref_t = runtime
        for prior in priors:
            tasks = prior_to_tasks[prior]
            # [0, idx] - ready tasks
            idx = tasks.bisect((t, num_tasks)) - 1
            if idx >= 0:
                any_task = 1
                k = randint(0, idx)
                task_id = tasks[k][1]
                task = id_to_task[task_id]
                out.write(f'<{["start", "continue"][task.done != 0]} name="{task.name}" time="{t}"/>\n')
                # next task time
                nxt_t = min(t + task.duration - task.done, pref_t)
                task.done += nxt_t - t
                # update task time
                tasks.pop(k)
                # update t
                t = nxt_t
                # done vs duration
                if task.done == task.duration:
                    # task done
                    task.done = 0
                    # wait till next period
                    tasks.add((t + task.period - t % task.period, task_id))
                else:
                    tasks.add((t, task_id))
                # go to task with higher prior
                if t == pref_t:
                    break
            pref_t = min(pref_t, prior_to_tasks[prior][0][0])
        if not any_task:
            t = pref_t
    out.write('</trace>\n')
    out.close()

if __name__ == '__main__':
    main()