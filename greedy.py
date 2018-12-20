import numpy as np
from time import time

from utils import read, write_to_csv

def greedy(instances_name):
    capacity, opening_cost, demand, cost = read(instances_name)
    customer_num = len(demand)
    facility_num = len(opening_cost)

    is_opened = [0] * facility_num
    assigned = [-1] * customer_num
    total_cost = 0
    for i in range(customer_num):
        cost_sort = np.argsort(cost[:, i])
        flag = True # 是否无解
        for j in cost_sort:
            if capacity[j] >= demand[i]:
                if not is_opened[j]:
                    is_opened[j] = 1
                    total_cost += opening_cost[j]
                total_cost += cost[j, i]
                assigned[i] = j
                capacity[j] -= demand[i]
                flag = False
                break
        if flag:
            print('No solution!')
            exit(1)

    print('Final cost: {}'.format(total_cost))
    print('Opening list: {}'.format(is_opened))
    print('Assigned list: {}'.format(assigned))

    return total_cost, is_opened, assigned

if __name__ == '__main__':
    cost_time = []
    result = []
    for i in range(1, 72):
        print('instances: {}'.format(i))
        st = time()
        tc, io, ass = greedy('p{}'.format(i))
        cost_time.append(time() - st)
        result.append(tc)

    write_to_csv(result, cost_time)
