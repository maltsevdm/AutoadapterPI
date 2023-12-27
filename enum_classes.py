import enum


class AdaptationType(enum.Enum):
    by_every_well = 0
    by_group = 1
    by_all_wells = 2


class GapParam(enum.Enum):
    q_liq = 'LiqRate'
    q_gaz = 'GasRate'
    q_oil = 'OilRate'
    fwhp = 'FWHP'


class GapItem(enum.Enum):
    well = 'WELL'
    src = 'SOURCE'
