import xmltodict
from sys import argv
from random import randint
from collections import defaultdict
from blist import sortedlist

def read_xml(fname):
    return xmltodict.parse(open(fname).read())

def main():
    data = read_xml(argv[1])
    out = open(argv[2], 'w')
    runtime = int(data['system']['@runtime'])
    out.write(f'<trace runtime="{runtime}">\n')
    prior_to_tasks = defaultdict(sortedlist)
    id_to_task = dict()
    num_tasks = len(data['system']['task'])
    for i, task in enumerate(data['system']['task']):
        # prior->sortedlist(ready_time, id) longer period -> lower prior
        prior_to_tasks[-task['@period']].add((0, i))
        # id->task last item is time in [0, duration]
        id_to_task[i] = [task['@name'], int(task['@duration']), int(task['@period']), 0]
    priors = sorted(prior_to_tasks.keys(), reverse=True)
    t = 0
    cur_task = num_tasks
    while t < runtime:
        for prior in priors:
            tasks = prior_to_tasks[prior]
            # [0, idx] - ready tasks
            idx = tasks.bisect((t, num_tasks)) - 1
            if idx >= 0:
                k = randint(0, idx)
                task_id = tasks[k][1]
                task = id_to_task[task_id]
                if cur_task != task_id:
                    cur_task = task_id
                    out.write(f'<{["start", "continue"][task[-1] != 0]} name="{task[0]}" time="{t}"/>\n')
                task[-1] += 1
                # update task time
                tasks.pop(k)
                # done vs duration
                if task[-1] == task[1]:
                    # wait till next period
                    tasks.add((t + 1) + task[-2] - (t + 1) % task[-2])
                else:
                    # wait 1 tick
                    tasks.add((t + 1, task_id))
                break
        # update time
        nxt_t = runtime
        for prior in priors:
            for (tm, idx) in prior_to_tasks[prior]:
                nxt_t = min(tm, nxt_t)
        t = max(t + 1, nxt_t)
    out.write('</trace>\n')
    out.close()
    
if __name__ == '__main__':
    main()