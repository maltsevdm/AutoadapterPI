from openserver import OpenServer

from enum_classes import GapItem, GapParam


class GAPInterface:
    def __init__(self):
        self.c: OpenServer = OpenServer()
        self.c.connect()

    def unmask_item(self, item_type: GapItem, name: str):
        self.c.DoCmd(f'GAP.MOD[{{PROD}}].{item_type}[{{{name}}}].UNMASK()')

    def mask_item(self, item_type: GapItem, name: str):
        self.c.DoCmd(f'GAP.MOD[{{PROD}}].{item_type}[{{{name}}}].MASK()')

    def mask_all_items(self, item_type: GapItem):
        self.c.DoCmd(f'GAP.MOD[{{PROD}}].{item_type}[$].MASK()')

    def get_solver_results(self, well: str, prop: GapParam):
        return self.c.DoGet(
            f'GAP.MOD[{{PROD}}].WELL[{{{well}}}].SolverResults[0].{prop}')

    def set_pi(self, well: str, pi: float):
        self.c.DoSet(f'GAP.MOD[{{PROD}}].WELL[{{{well}}}].IPR[0].PI', pi)

    def solve(self):
        print('GAP solving...')
        self.c.DoCmd('GAP.SOLVENETWORK(0, MOD[0])')
        print('Done')

    def disconnect(self):
        self.c.disconnect()
