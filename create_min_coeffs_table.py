import itertools
import math
import re

from openpyxl import Workbook, cell
from openpyxl.styles import Alignment, Font, PatternFill

from run_quine_mccluskey import BFV
from texttable import Texttable


class Cell:
    def __init__(self, s: str, co: bool):
        self.s = s
        self.crossed_out = co

    def __repr__(self) -> str:
        return self.s

    def __len__(self) -> int:
        return len(self.s)

    def __eq__(self, other):
        return self.s == other.s


def get_table(tab: list[list[Cell]]) -> str:
    t = Texttable()
    t.set_chars(['—', '|', '+', '—'])
    t.set_cols_dtype(['t'] * len(tab[0]))
    t.set_cols_align(['c'] * len(tab[0]))
    t.set_cols_width([len(c) for c in tab[0]])
    t.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)
    t.add_rows(tab)
    return t.draw()


def main():
    table = list[list[Cell]]()
    n = int(math.log2(len(BFV)))
    assert n > 0

    header = list[Cell]()
    for k in range(1, n + 1):
        combs = itertools.combinations(range(n), k)
        header.extend([Cell(''.join(list(map(str, comb))), False) for comb in combs])

    table.append(header + [Cell('F', False)])

    sets = list(map(lambda s: list(map(lambda x: Cell(str(x), False), s)),
                    list(itertools.product([0, 1], repeat=n))))

    table.extend(sets)

    for j in range(n, len(table[0]) - 1):
        indexes = re.split('', table[0][j].s)
        indexes.pop(0)
        indexes.pop(-1)
        indexes = list(map(int, indexes))

        for i in range(1, len(table)):
            cur_set = list(map(lambda ind: str(table[i][ind]), indexes))
            table[i].append(Cell(''.join(cur_set), False))

    for i in range(1, len(table)):
        table[i].append(Cell(str(BFV[i - 1]), False))

    # Crossing out lines F = 0
    for i in range(1, len(table)):
        if table[i][-1].s == '1':
            continue
        for j in range(len(table[i])):
            table[i][j].crossed_out = True

    # Crossing out excess in columns
    for j in range(len(table[0])):
        for i in range(1, len(table)):
            if not table[i][j].crossed_out:
                continue

            for secondary_i in range(1, len(table)):
                if table[secondary_i][j].s == table[i][j].s:
                    table[secondary_i][j].crossed_out = True

    with open('mc-table.txt', 'w') as writer:
        writer.write(get_table(table))

    wb = Workbook()
    ws = wb.active

    for row in table:
        ws.append(list(map(str, row)))

    al = Alignment(horizontal='center', vertical='center')

    ok_fill = PatternFill('solid', fgColor='00FFFFFF')
    ok_font = Font(bold=False, color='000000')

    bad_fill = PatternFill('solid', fgColor='00969696')
    bad_font = Font(bold=False, color='000000')

    for j in range(len(table[0])):
        c = cell.cell.Cell(ws, row=1, column=j + 1)
        ws.column_dimensions[c.column_letter].width = len(table[0][j])

    for i in range(1, len(table)):
        for j in range(len(table[i])):
            c = cell.cell.Cell(ws, row=i + 1, column=j + 1)
            ws[c.coordinate].alignment = al

            if table[i][j].crossed_out:
                ws[c.coordinate].fill = bad_fill
                ws[c.coordinate].font = bad_font
                continue

            ws[c.coordinate].fill = ok_fill
            ws[c.coordinate].font = ok_font

    wb.save('mc-table.xlsx')


if __name__ == '__main__':
    main()
