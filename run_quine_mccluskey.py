import itertools
import math
from texttable import Texttable


class BFSet:
    def __init__(self):
        self.num = None
        self.s = str()
        self.stuck = False
        self.sets = list[BFSet]()

    def weight(self) -> int:
        s = 0
        for v in self.s:
            s += 1 if v == '1' else 0
        return s

    def __repr__(self) -> str:
        predecessors = f'({self.sets[-2]}, {self.sets[-1]}) —> ' if self.sets else ''
        itself = f'({self.num}) {self.s}'
        return '{:>15} {:>13} {:>1}'.format(predecessors, itself, '*' if self.stuck else '')

    def __lt__(self, other) -> bool:
        return self.num < other.num

    @staticmethod
    def stick_sets(lhs: 'BFSet', rhs: 'BFSet') -> 'BFSet':
        b = BFSet()
        b.sets.extend([lhs.num, rhs.num])
        for i, ch in enumerate(lhs.s):
            b.s += ch if ch == rhs.s[i] else '-'
        return b

    def covers_constituent(self, bfs: 'BFSet') -> bool:
        for i, ch in enumerate(self.s):
            if ch == '-':
                continue
            if not ch == bfs.s[i]:
                return False
        return True


def list_to_str(sets: list[BFSet]) -> str:
    return '\n'.join(list(map(str, sets)))


def hamming_distance(lhs: BFSet, rhs: BFSet) -> int:
    mistakes = 0
    for i, arg in enumerate(lhs.s):
        mistakes += 1 if not arg == rhs.s[i] else 0
    return mistakes


def stick_lists(sets: list[BFSet]) -> list[BFSet]:
    we_have = set[str]()
    num = 0
    ret_list = list[BFSet]()

    for i, iter_s in enumerate(sets):
        for j, init_s in enumerate(sets):
            if not hamming_distance(sets[i], sets[j]) == 1:
                continue
            b = BFSet.stick_sets(sets[i], sets[j])
            sets[i].stuck = True
            sets[j].stuck = True
            if b.s in we_have:
                continue
            num += 1
            b.num = num
            ret_list.append(b)
            we_have.add(b.s)
    return ret_list


def from_tt_to_normal(sets: list) -> list[BFSet]:
    i = 0
    out_list = list[BFSet]()

    for s, v in sets:
        if v == 0:
            continue
        bfset = BFSet()
        i += 1
        bfset.num = i
        bfset.s = s
        out_list.append(bfset)

    out_list.sort(key=lambda x: x.weight())
    return out_list


def quine_mccluskey(bfv: str) -> None:
    n = int(math.log2(len(bfv)))
    tt = list(itertools.product([0, 1], repeat=n))

    history = list[tuple[list[BFSet], list[BFSet]]]()

    for i, v in enumerate(bfv):
        tt[i] = (''.join(map(str, tt[i])), int(v))

    sets = from_tt_to_normal(tt)

    constituents = sets.copy()

    for i in range(len(sets)):
        sets[i].num = i + 1

    all_kernel_sets = list[BFSet]()

    while sets:
        sets_stuck = stick_lists(sets)

        inits = list[BFSet]()
        for bfs in sets:
            if not bfs.stuck:
                inits.append(bfs)
        all_kernel_sets.extend(inits)

        history.append((sets, inits))
        sets = sets_stuck

    with open('levels.txt', 'w') as logger:
        for i, level in enumerate(history):
            logger.write(f'Level {i + 1}\n')
            logger.write(list_to_str(level[0]) + '\n')
            if level[1]:
                logger.write(f'Primary implicants from level-{i + 1}:\n')
                logger.write(list_to_str(level[1]) + '\n')

    t = Texttable()
    header = 'consts\\covs'
    t.set_chars(['—', '|', '+', '—'])
    t.set_cols_dtype(['t'] * (len(all_kernel_sets) + 1))
    t.set_cols_align(['c'] * (len(all_kernel_sets) + 1))
    t.set_cols_width([len(header)] + [n] * len(all_kernel_sets))
    t.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)
    t.header([header] + list(map(lambda x: x.s, all_kernel_sets)))

    for c in constituents:
        cells = [c.s]
        for kernel_set in all_kernel_sets:
            cells.append('V' if kernel_set.covers_constituent(c) else ' ')
        t.add_row(cells)

    with open('table.txt', 'w') as logger:
        logger.write(t.draw())


def main():
    bfv = '1111001111110011111111000000000000001100000000000011110011111111'
    quine_mccluskey(bfv)


if __name__ == '__main__':
    main()
