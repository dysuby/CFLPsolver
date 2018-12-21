import csv

GREEDY = 'result/greedy_result.csv'
SA = 'result/sa_result.csv'
COMPARE = 'result/compare.csv'


def compare():
    with open(GREEDY) as gf, open(SA) as sf, open(COMPARE, 'w') as cf:
        greedy_reader, sa_reader = csv.DictReader(gf), csv.DictReader(sf)
        cw = csv.writer(cf)
        cw.writerow(['', 'result', 'time(s)'])
        idx = 1
        for greedy, sa in zip(greedy_reader, sa_reader):
            tp = float(sa['time(s)']) / float(greedy['time(s)'])
            rp = float(sa['result']) / float(greedy['result'])
            print('p{}: SA cost {} times, solution cost {}'.format(
                idx, '%.2f%%' % tp, '%.2f%%' % rp))
            cw.writerow(['p{}'.format(idx), '%.2f%%' % rp, '%.2f%%' % tp])
            idx += 1


if __name__ == '__main__':
    compare()
