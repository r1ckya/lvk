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
        # prior->sortedlist(ready_time, id)
        prior_to_tasks[task['@priority']].add((0, i))
        # id->task_dict
        id_to_task[i] = dict(name=task['@name'],            
                             duration=int(task['@duration']),
                             period=int(task['@period']))
    priors = sorted(prior_to_tasks.keys(), reverse=True)
    t = 0
    while t < runtime:
        for prior in priors:
            tasks = prior_to_tasks[prior]
            # [0, idx] - ready tasks
            idx = tasks.bisect((t, num_tasks)) - 1
            if idx >= 0:
                k = randint(0, idx)
                task_id = tasks[k][1]
                task = id_to_task[task_id]
                out.write(f'<start name="{task["name"]}" time="{t}"/>\n')
                t += task['duration'] - 1
                # update task time
                tasks.pop(k)
                tasks.add((t + task['period'] - t % task['period'], task_id))
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