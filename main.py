import time
import json
from typing import Optional

from GAPInterface import GAPInterface
from Well import Well
from enum_classes import AdaptationType, GapItem, GapParam

PATH_INIT_DATA = 'initial_data.json'
PATH_RESULT = 'result.json'
VNR_SRC = []
ADAPT_TYPES = [
    AdaptationType.by_every_well,
    AdaptationType.by_group,
    AdaptationType.by_all_wells
]
GROUPS = []

class AutoadapterPI:
    def __init__(
            self,
            adapt_types: list[AdaptationType],
            groups: Optional[list] = None
    ):
        self.adapt_types: list[AdaptationType] = adapt_types
        self.groups: list = groups if groups else []
        self.gap = GAPInterface()

        with open(PATH_INIT_DATA, encoding='utf-8') as file:
            init_data: list[dict] = json.load(file)

        self.wells: list[Well] = []
        for well in init_data:
            self.wells.append(Well(gap=self.gap, **well))

    def get_iter_dict(
            self, adapt_type: AdaptationType, group: str = None
    ) -> dict[str, list[Well]]:
        if adapt_type == AdaptationType.by_every_well:
            return {well.gap_well: [well] for i, well in enumerate(self.wells)}
        elif adapt_type == AdaptationType.by_group:
            data = {}
            for well in self.wells:
                data.setdefault(getattr(well, group), []).append(well)
            return data
        elif adapt_type == AdaptationType.by_all_wells:
            return {'all_wells': self.wells}

    def unmask_vnr(self):
        for item in VNR_SRC:
            self.gap.unmask_item(GapItem.src, item)

    def unmask_necessary_wells(self, wells: list[Well]) -> None:
        print('Unmasking necessary wells and sources...')
        for well in wells:
            well.unmask()
        print('Done')

    def get_accuracy(self, q_liq):
        if q_liq < 100:
            return 1
        elif q_liq < 200:
            return 3
        elif q_liq < 300:
            return 5
        elif q_liq < 400:
            return 6
        elif q_liq < 500:
            return 7
        else:
            return 10

    def start_adapt(self, adapt_type: AdaptationType, group: str = None):
        iter_dict: dict[str, list[Well]] = self.get_iter_dict(adapt_type, group)
        for index, wells in iter_dict.items():
            print(f'\n_________ Work has begun on element {index} _________')
            self.gap.mask_all_items(GapItem.src)
            self.gap.mask_all_items(GapItem.well)
            self.unmask_necessary_wells(wells)

            if adapt_type != AdaptationType.by_every_well:
                self.unmask_vnr()

            i = 1
            while True:
                print(f'\n========= Round of adaptation {i}. '
                      f'Element {index}. =========')
                cycle_time_start = time.time()
                self.gap.solve()

                print('Getting new values from GAP...')
                for well in wells:
                    well.q_liq_gap = well.get_param_value_from_gap(
                        GapParam.q_liq)
                    well.calc_delta_q_liq()
                    # TODO: Getting FWHP, GasRate, OilRate
                print('Done')

                print('Preparation of wells for adaptation...')
                good_wells = []
                for well in wells:
                    if (well.item_type == GapItem.well
                            and abs(well.d_q_liq) > self.get_accuracy(
                                well.q_liq)):
                        good_wells.append(well)

                wells_for_adapt = sorted(
                    good_wells,
                    key=lambda x: abs(x.d_q_liq)
                )[-3:]

                if not wells_for_adapt:
                    print('No adaptation is needed for the current element.')
                    break

                for well in wells_for_adapt:
                    result = well.adapt()

                    if not result:
                        for well in good_wells:
                            if well.item_type == GapItem.well:
                                well.reset_adapt_params()

                print(f'========= Adaptation round {i} is over. '
                      f'Round time: {(time.time() - cycle_time_start):.1f} sec. '
                      '=========')
                i += 1

    def run(self):
        for adapt_type in self.adapt_types:
            if adapt_type == AdaptationType.by_group:
                for group in self.groups:
                    self.start_adapt(adapt_type, group)
            else:
                self.start_adapt(adapt_type)

        with open(PATH_RESULT, 'w', encoding='utf-8') as file:
            json.dump(self.wells, file, default=class_to_json,
                      ensure_ascii=False, indent=4)


def class_to_json(obj):
    return obj.__dict__
    

if __name__ == '__main__':
    aa = AutoadapterPI([])
    aa.run()
