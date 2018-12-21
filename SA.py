import numpy as np
import random
from copy import deepcopy
from time import time
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
        old_i = solution.assigned[i]
        old_j = solution.assigned[j]
        solution.assigned[i], solution.assigned[j] = old_j, old_i

        solution.cost -= self.cost[old_i, i] + \
            self.cost[old_j, j]
        solution.cost += self.cost[old_j, i] + \
            self.cost[old_i, j]

        solution.left[old_j] += self.demand[j] - self.demand[i]
        solution.left[old_i] += self.demand[i] - self.demand[j]

        return solution

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
        if not solution.is_opened[target]:  # 如果工厂没开
            solution.is_opened[target] = 1
            solution.cost += self.opening_cost[target]

        # 将其他客人分配到该工厂上
        indices = list(range(self.customer_num))
        random.shuffle(indices)
        for i in indices:
            old = solution.assigned[i]
            if old != target and solution.left[target] >= self.demand[i]:
                # 可以满足需求
                solution.cost += self.cost[target, i] - \
                    self.cost[old, i]
                solution.assigned[i] = target
                solution.left[target] -= self.demand[i]
                solution.left[old] += self.demand[i]
                if solution.left[old] == self.capacity[old]:    # 如果工厂无人使用
                    solution.cost -= self.opening_cost[old]
                    solution.is_opened[old] = 0

        return solution

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
        old = solution.assigned[cust]
        solution.assigned[cust] = fac

        solution.cost += self.cost[fac, cust] - \
            self.cost[old, cust]

        if not solution.is_opened[fac]:       # 如果工厂没开
            solution.is_opened[fac] = 1
            solution.cost += self.opening_cost[fac]

        solution.left[old] += self.demand[cust]
        solution.left[fac] -= self.demand[cust]

        if solution.left[old] == self.capacity[old] and solution.is_opened[old]:  # 如果工厂无人使用
            solution.is_opened[old] = 0
            solution.cost -= self.opening_cost[old]

        return solution

    def run(self, T, tmin, ntimes, T_ratio):
        solution = self.gen_init_solution()
        self.optimal = solution

        while T > tmin:
            # 内循环
            for j in range(ntimes):
                # 局部搜索
                new_solution = random.sample(
                    [self.move_facility, self.swap_facility, self.move_customer], 1)[0](deepcopy(solution))
                delta = new_solution.cost - solution.cost

                if delta <= 0 or np.random.ranf() < np.exp(-delta / T):     # 接受解的情况
                    solution = new_solution
                    if solution.cost < self.optimal.cost:   # 更新最优解
                        self.optimal = solution

                print('T: {} times: {}/{}: current: {} best: {}'.format(
                    T, j, ntimes, solution.cost, self.optimal.cost))

            T *= T_ratio
        self.constraint(self.optimal)
        print('Final cost: {}'.format(self.optimal.cost))
        print('Opening list: {}'.format(self.optimal.is_opened))
        print('Assigned list: {}'.format(self.optimal.assigned))

        return self.optimal.cost, self.optimal.is_opened, self.optimal.assigned

    def constraint(self, solution):
        cost = 0
        left = self.capacity.copy()
        should_open = [0] * self.facility_num
        for i in range(self.customer_num):
            cost += self.cost[solution.assigned[i], i]
            left[solution.assigned[i]] -= self.demand[i]
            should_open[solution.assigned[i]] = 1

        for i in range(self.facility_num):      # 计算开厂费用
            if solution.is_opened[i]:
                cost += self.opening_cost[i]

        if min(left) < 0:   # 超出容量
            raise Exception('Capacity Exceed')
        elif cost != solution.cost:     # 计算费用错误
            raise Exception('Cost calculation error')
        elif left != solution.left:     # 计算剩余容量错误
            raise Exception('Left calculation error')
        elif should_open != solution.is_opened:     # 工厂开多了或者开少了
            raise Exception('Open list error')
        print('Constraint pass')


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
