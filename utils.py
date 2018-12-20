import numpy as np
import csv

INSTANCE_PATH = 'Instances'


def read(instance):
    with open('{}/{}'.format(INSTANCE_PATH, instance)) as f:
        array = f.read().split()
        facility_num, customer_num = [int(x) for x in array[:2]]
        capacity, opening_cost = [], []

        capacity = [float(x) for x in array[2:2 + facility_num * 2 - 1:2]]
        opening_cost = [float(x) for x in array[3:3 + facility_num * 2 - 1:2]]

        index = 2 + facility_num * 2
        demand = [float(x) for x in array[index:index + customer_num]]

        cost = []
        index += customer_num
        for i in range(facility_num):
            cost.append([float(x) for x in array[index:index + customer_num]])
            index += customer_num

        return np.array(capacity), np.array(opening_cost), np.array(demand), np.array(cost)


def write_to_csv(algo, result, time):
    headers = ['', 'result', 'time(s)']
    with open('result/{}_result.csv'.format(algo), 'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows([(p, r, t) for p, r, t in zip(['p{}'.format(i)
                                                 for i in range(0, len(result) + 1)], result, time)])


if __name__ == '__main__':
    ca, op, de, co = read('p1')
    print(ca.shape, op.shape, de.shape, co.shape)
