import numpy as np
from time import time
import random
from utils import read, write_to_csv, write_details


def greedy(instances_name, times):
    capacity, opening_cost, demand, cost = read(instances_name)
    customer_num = len(demand)
    facility_num = len(opening_cost)

    # 保存最优解
    min_cost = np.inf
    min_is_opened = None
    min_assigned = None

    indices = list(range(customer_num))
    for k in range(times):
        tmp_capacity = capacity.copy()  # 剩余容量
        is_opened = [0] * facility_num  # 工厂是否开
        assigned = [-1] * customer_num  # 顾客分配到哪个厂
        total_cost = 0                  # 总代价
        for i in indices:
            cost_sort = np.argsort(cost[:, i])      # 按分配代价排序
            for j in cost_sort:
                if tmp_capacity[j] >= demand[i]:    # 可以满足需求
                    if not is_opened[j]:            # 没开厂则开厂
                        is_opened[j] = 1
                        total_cost += opening_cost[j]

                    # 计算代价
                    total_cost += cost[j, i]
                    assigned[i] = j
                    tmp_capacity[j] -= demand[i]
                    break

        # 更新最优解
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
