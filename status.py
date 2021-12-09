from enum import Enum


class UserStatus(Enum):
    NO_FILTERS = 0
    STEP_CITY = 1
    STEP_TYPE = 2
    STEP_ROOMS = 3
    STEP_PRICE = 4
    STEP_REGIONS = 5
    STEP_METRO = 6
    YES_FILTERS = 7
    EDIT_MENU = 8
