import numpy as np
import random
from time import time
from greedy import greedy
from utils import read, write_to_csv, write_details


class Solution:
    def __init__(self, cost, is_opened, assigned, left):
        self.cost = cost
        self.is_opened = is_opened
        self.assigned = assigned
        self.left = left


class SA:
    def __init__(self, instance_name):
        self.instance_name = instance_name
        self.capacity, self.opening_cost, self.demand, self.cost = read(
            instance_name)
        self.facility_num, self.customer_num = len(
            self.capacity), len(self.demand)

    def gen_init_solution(self):
        is_opened = [0] * self.facility_num
        assigned = [-1] * self.customer_num
        left = self.capacity.copy()

        cost = 0
        for i in range(self.customer_num):
            can_choose = list(range(self.facility_num))
            j, = random.sample(can_choose, 1)
            while left[j] < self.demand[i]:
                can_choose.remove(j)
                j, = random.sample(can_choose, 1)
            if not is_opened[j]:
                is_opened[j] = 1
                cost += self.opening_cost[j]
            assigned[i] = j
            cost += self.cost[j, i]
            left[j] -= self.demand[i]
        return Solution(cost, is_opened, assigned, left)

    def swap_facility(self, solution):
        customer = [[x, y] for x in range(self.customer_num) for y in range(self.customer_num)]
        i, j = random.sample(customer, 1)[0]
        while solution.left[solution.assigned[j]] + self.demand[j] < self.demand[i] or solution.left[solution.assigned[i]] + self.demand[i] < self.demand[j]:
            customer.remove([i, j])
            i, j = random.sample(customer, 1)[0]

        new_assigned = solution.assigned.copy()
        new_assigned[i] = solution.assigned[j]
        new_assigned[j] = solution.assigned[i]

        new_cost = solution.cost
        new_cost -= self.cost[solution.assigned[i], i] + \
            self.cost[solution.assigned[j], j]
        new_cost += self.cost[solution.assigned[j], i] + \
            self.cost[solution.assigned[i], j]

        new_left = solution.left.copy()
        new_left[solution.assigned[j]] += self.demand[j] - self.demand[i]
        new_left[solution.assigned[i]] += self.demand[i] - self.demand[j]

        return Solution(new_cost, solution.is_opened, new_assigned, new_left)

    def open_facility(self, solution):
        non_open = np.where(solution.is_opened == 0)
        to_open = random.sample(non_open, 1)
        new_is_opened = solution.is_opened.copy()
        new_is_opened[to_open] = 1

        new_cost = solution.cost + self.opening_cost[to_open]
        new_left = solution.left.copy()
        new_assigned = solution.assigned.copy()
        for i in range(self.customer_num):
            if self.cost[to_open, i] < self.cost[solution.assigned[i], i] and new_left[to_open] > self.demand[i]:
                new_cost += self.cost[to_open, i] - self.cost[solution.assigned[i], i]
                new_assigned[i] = to_open
                new_left[to_open] -= self.demand[i]

        return Solution(new_cost, new_is_opened, new_assigned, new_left)                

    def localsearch(self, solution):
        neighbors = [self.swap_facility(solution)]
        if np.count_nonzero(solution.is_opened == 0):
            neighbors.append(self.open_facility(solution))
        return min(neighbors, key=lambda s: s.cost)

    def run(self, T, tmin, ntimes, T_ratio):
        solution = self.gen_init_solution()
        self.optimal = solution

        self.s_set = [solution]
        while T > tmin:
            for j in range(ntimes):
                new_solution = self.localsearch(solution)
                delta = new_solution.cost - solution.cost

                if delta <= 0 or np.random.ranf() < np.exp(-delta / T):
                    solution = new_solution
                    if solution.cost < self.optimal.cost:
                        self.optimal = solution
                        self.s_set.append(solution)

                print('T: {} times: {}/{}: current: {} best: {}'.format(
                    T, j, ntimes, solution.cost, self.optimal.cost))

            T *= T_ratio

        print('Final cost: {}'.format(self.optimal.cost))
        print('Opening list: {}'.format(self.optimal.is_opened))
        print('Assigned list: {}'.format(self.optimal.assigned))

        return self.optimal.cost, self.optimal.is_opened, self.optimal.assigned


if __name__ == '__main__':
    cost_time = []
    result = []
    for i in range(1, 72):
        print('instances: {}'.format(i))
        st = time()
        sa = SA('p{}'.format(i))
        tc, io, ass = sa.run(100, 5, 5000, 0.97)
        cost_time.append(time() - st)
        result.append(tc)
        write_details('sa', i, tc, io, ass)

    write_to_csv('sa', result, cost_time)
