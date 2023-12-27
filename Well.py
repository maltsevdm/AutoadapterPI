from GAPInterface import GAPInterface
from config import MAX_PI, MIN_PI, MAX_ITER
from enum_classes import GapItem, GapParam


class Well:
    def __init__(
            self,
            gap: GAPInterface,
            field: str,
            pad: str,
            well: str,
            gap_well: str,
            gap_src: str,
            pi: float,
            q_liq: float,
            item_type: GapItem,
            **kwargs
    ):
        self.gap: GAPInterface = gap
        self.field: str = field
        self.pad: str = pad
        self.well: str = well
        self.gap_well: str = gap_well
        self.gap_src: str = gap_src
        self.pi: float = pi
        self.q_liq: float = q_liq
        self.q_liq_gap: float = 0
        self.d_q_liq: float = self.q_liq - self.q_liq_gap
        self.prev_d_q_liq: float = self.d_q_liq
        self.iteration: int = 0
        self.over_max: int = 0
        self.less_min: int = 0
        self.pi_factor: float = self.get_pi_factor()
        self.item_type: GapItem = item_type

        for k, v in kwargs.items():
            setattr(self, k, v)

    def mask(self) -> None:
        self.gap.mask_item(
            self.item_type,
            self.gap_well if self.item_type == GapItem.well else self.gap_src
        )

    def unmask(self) -> None:
        self.gap.unmask_item(
            self.item_type,
            self.gap_well if self.item_type == GapItem.well else self.gap_src
        )

    def get_param_value_from_gap(self, param: GapParam):
        return self.gap.get_solver_results(self.gap_well, param)

    def calc_delta_q_liq(self) -> float:
        self.d_q_liq = self.q_liq - self.q_liq_gap
        return self.d_q_liq

    def exclude_from_adapt(self) -> None:
        self.mask()
        self.item_type = GapItem.src
        self.unmask()

        output_str = f'| The well {self.gap_well} is not adapting |'
        print('-' * len(output_str))
        print(output_str)
        print('-' * len(output_str))

    def reset_adapt_params(self) -> None:
        self.iteration = 0
        self.over_max = 0
        self.less_min = 0
        self.pi_factor = self.get_pi_factor()

    def get_pi_factor(self) -> float:
        if self.pi <= 1:
            return 0.5
        elif self.pi <= 5:
            return 1
        elif self.pi <= 10:
            return 2
        else:
            return 5

    def adapt(self) -> bool:
        if self.prev_d_q_liq * self.d_q_liq < 0:
            self.pi_factor /= 2
            self.iteration += 1
        self.prev_d_q_liq = self.d_q_liq
        self.pi = (self.pi + self.pi_factor if self.d_q_liq > 0
                   else self.pi - self.pi_factor)
        if self.pi < MIN_PI:
            self.pi = MIN_PI
            if self.less_min <= 10:
                self.less_min += 1
            else:
                self.exclude_from_adapt()
                return False
        elif self.pi > MAX_PI:
            self.pi = MAX_PI
            if self.over_max <= 3:
                self.over_max += 1
            else:
                self.exclude_from_adapt()
                return False

        print(f'New PI: {self.pi} | iteration: {self.iteration}')

        if self.iteration >= MAX_ITER:
            self.exclude_from_adapt()
            return False
        else:
            self.gap.set_pi(self.gap_well, self.pi)
            return True
