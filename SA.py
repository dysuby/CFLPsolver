import numpy as np
import random
from time import time
from greedy import greedy
from utils import read, write_to_csv, write_details


class Solution:
    """
    保存解
    """
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
        """
        随机产生初始解
        """
        is_opened = [0] * self.facility_num
        assigned = [-1] * self.customer_num
        left = self.capacity.copy()

        cost = 0
        for i in range(self.customer_num):
            can_choose = list(range(self.facility_num))
            j, = random.sample(can_choose, 1)   # 随机选择一个工厂
            while left[j] < self.demand[i]:     # 直到可以分配给顾客
                can_choose.remove(j)
                j, = random.sample(can_choose, 1)
            if not is_opened[j]:                # 如果没工厂开
                is_opened[j] = 1
                cost += self.opening_cost[j]
            # 更新解
            assigned[i] = j
            cost += self.cost[j, i]
            left[j] -= self.demand[i]
        return Solution(cost, is_opened, assigned, left)

    def swap_facility(self, solution):
        """
        交换两个顾客分配到的工厂
        """
        # 随机出两个顾客
        customer = [[x, y] for x in range(
            self.customer_num) for y in range(self.customer_num)]
        i, j = random.sample(customer, 1)[0]
        while solution.left[solution.assigned[j]] + self.demand[j] < self.demand[i] or solution.left[solution.assigned[i]] + self.demand[i] < self.demand[j]:
            # 直到对方的工厂可以满足自己的需求
            customer.remove([i, j])
            customer.remove([j, i])
            if not customer:
                return solution
            i, j = random.sample(customer, 1)[0]

        # 更新解
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

        return Solution(new_cost, solution.is_opened.copy(), new_assigned, new_left)

    def move_facility(self, solution):
        """
        选择某个工厂，将客人分配到它上
        """
        # 随机选择一个工厂
        can_choose = list(range(self.facility_num))
        target, = random.sample(can_choose, 1)
        while solution.left[target] < min(self.demand):
            # 直到至少可以满足一位顾客
            can_choose.remove(target)
            if not can_choose:
                return solution
            target, = random.sample(can_choose, 1)

        # 更新解
        new_is_opened = solution.is_opened.copy()
        new_cost = solution.cost
        if not solution.is_opened[target]:  # 如果工厂没开
            new_is_opened[target] = 1
            new_cost += self.opening_cost[target]
        new_left = solution.left.copy()
        new_assigned = solution.assigned.copy()

        # 将其他客人分配到该工厂上
        indices = list(range(self.customer_num))
        random.shuffle(indices)
        for i in indices:
            if solution.assigned[i] != target and new_left[target] >= self.demand[i]:
                # 可以满足需求
                new_cost += self.cost[target, i] - \
                    self.cost[solution.assigned[i], i]
                new_assigned[i] = target
                new_left[target] -= self.demand[i]
                new_left[solution.assigned[i]] += self.demand[i]

        return Solution(new_cost, new_is_opened, new_assigned, new_left)

    def move_customer(self, solution):
        """
        随机选择一位顾客，将他分配到一个新的随机工厂
        """
        # 随机选择顾客和工厂
        customer_can_choose = list(range(self.customer_num))
        cust, = random.sample(customer_can_choose, 1)

        facility_can_choose = list(range(self.facility_num))
        fac, = random.sample(facility_can_choose, 1)
        while solution.assigned[cust] == fac or solution.left[fac] < self.demand[cust]:
            # 直到工厂可以满足顾客的需求
            facility_can_choose.remove(fac)
            if not facility_can_choose:      # 该顾客已经无法选择其他工厂
                customer_can_choose.remove(cust)
                if not customer_can_choose:     # 已经没有可以移动的顾客
                    return solution
                cust, = random.sample(customer_can_choose, 1)   # 重新选择顾客
                facility_can_choose = list(range(self.facility_num))
            fac, = random.sample(facility_can_choose, 1)

        # 更新解
        new_assigned = solution.assigned.copy()
        new_assigned[cust] = fac

        new_cost = solution.cost
        new_cost += self.cost[fac, cust] - \
            self.cost[solution.assigned[cust], cust]

        new_is_opened = solution.is_opened.copy()
        if not new_is_opened[fac]:       # 如果工厂没开
            new_is_opened[fac] = 1
            new_cost += self.opening_cost[fac]

        new_left = solution.left.copy()
        new_left[solution.assigned[cust]] += self.demand[cust]
        new_left[fac] -= self.demand[cust]

        return Solution(new_cost, new_is_opened, new_assigned, new_left)

    def localsearch(self, solution):
        return random.sample([self.move_facility, self.swap_facility, self.move_customer], 1)[0](solution)

    def run(self, T, tmin, ntimes, T_ratio):
        solution = self.gen_init_solution()
        self.optimal = solution

        while T > tmin:
            # 内循环
            for j in range(ntimes):
                new_solution = self.localsearch(solution)
                delta = new_solution.cost - solution.cost

                if delta <= 0 or np.random.ranf() < np.exp(-delta / T):     # 接受解的情况
                    solution = new_solution
                    if solution.cost < self.optimal.cost:   # 更新最优解
                        self.optimal = solution

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
        tc, io, ass = sa.run(100, 5, 3000, 0.95)
        cost_time.append(time() - st)
        result.append(tc)
        write_details('sa', i, tc, io, ass)

    write_to_csv('sa', result, cost_time)
