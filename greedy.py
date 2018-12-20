import numpy as np
from time import time
import random
from utils import read, write_to_csv, write_details

def greedy(instances_name, times):
    capacity, opening_cost, demand, cost = read(instances_name)
    customer_num = len(demand)
    facility_num = len(opening_cost)

    min_cost = np.inf
    min_is_opened = None
    min_assigned = None

    indices = list(range(customer_num))
    for k in range(times):
        tmp_capacity = capacity.copy()
        is_opened = [0] * facility_num
        assigned = [-1] * customer_num
        total_cost = 0
        for i in indices:
            cost_sort = np.argsort(cost[:, i])
            for j in cost_sort:
                if tmp_capacity[j] >= demand[i]:
                    if not is_opened[j]:
                        is_opened[j] = 1
                        total_cost += opening_cost[j]
                    total_cost += cost[j, i]
                    assigned[i] = j
                    tmp_capacity[j] -= demand[i]
                    break

        if min_cost > total_cost:
            min_cost = total_cost
            min_is_opened = is_opened
            min_assigned = assigned
        random.shuffle(indices)

    print('Final cost: {}'.format(min_cost))
    print('Opening list: {}'.format(min_is_opened))
    print('Assigned list: {}'.format(min_assigned))

    return min_cost, min_is_opened, min_assigned

if __name__ == '__main__':
    cost_time = []
    result = []
    for i in range(1, 72):
        print('instances: {}'.format(i))
        st = time()
        tc, io, ass = greedy('p{}'.format(i), 10)
        cost_time.append(time() - st)
        result.append(tc)
        write_details('greedy', i, tc, io, ass)

    write_to_csv('greedy', result, cost_time)
