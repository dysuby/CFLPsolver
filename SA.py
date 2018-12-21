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
        customer = [[x, y] for x in range(
            self.customer_num) for y in range(self.customer_num)]
        i, j = random.sample(customer, 1)[0]
        while solution.left[solution.assigned[j]] + self.demand[j] < self.demand[i] or solution.left[solution.assigned[i]] + self.demand[i] < self.demand[j]:
            customer.remove([i, j])
            if not customer:
                return solution
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

    def move_facility(self, solution):
        target, = random.sample(range(self.facility_num), 1)

        new_is_opened = solution.is_opened.copy()
        new_cost = solution.cost
        if not solution.is_opened[target]:
            new_is_opened[target] = 1
            new_cost += self.opening_cost[target]
        new_left = solution.left.copy()
        new_assigned = solution.assigned.copy()

        indices = list(range(self.customer_num))
        random.shuffle(indices)
        for i in indices:
            if new_left[target] >= self.demand[i]:
                new_cost += self.cost[target, i] - \
                    self.cost[solution.assigned[i], i]
                new_assigned[i] = target
                new_left[target] -= self.demand[i]
                new_left[solution.assigned[i]] += self.demand[i]

        return Solution(new_cost, new_is_opened, new_assigned, new_left)

    def move_customer(self, solution):
        cust, = random.sample(range(self.customer_num), 1)
        can_choose = list(range(self.facility_num))
        fac, = random.sample(can_choose, 1)
        while solution.assigned[cust] == fac and solution.left[fac] < self.demand[cust]:
            can_choose.remove(fac)
            if not can_choose:
                return solution
            fac, = random.sample(can_choose, 1)
        new_assigned = solution.assigned.copy()
        new_assigned[cust] = fac

        new_cost = solution.cost
        new_cost += self.cost[fac, cust] - self.cost[solution.assigned[cust], cust]

        new_is_opened = solution.is_opened.copy()
        if not new_is_opened[fac]:
            new_is_opened[fac] = 1
            new_cost += self.opening_cost[fac]

        new_left = solution.left.copy()
        new_left[solution.assigned[cust]] += self.demand[cust]
        new_left[fac] -= self.demand[cust]

        return Solution(new_cost, new_is_opened, new_assigned, new_left)

    def localsearch(self, solution):
        neighbors = [self.move_customer(
            solution), self.swap_facility(solution)]
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
        tc, io, ass = sa.run(100, 1, 3000, 0.95)
        cost_time.append(time() - st)
        result.append(tc)
        write_details('sa', i, tc, io, ass)

    write_to_csv('sa', result, cost_time)
