from enum import Enum


class UserStatus(Enum):
    NO_FILTERS = 0
    STEP_TYPE = 1
    STEP_CITY = 2
    STEP_PRICE = 3
    STEP_ROOMS = 4
    STEP_REGIONS = 5
    STEP_METRO = 6
    YES_FILTERS = 7
    EDIT_MENU = 8
