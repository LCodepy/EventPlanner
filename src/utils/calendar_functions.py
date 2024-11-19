import datetime


def get_month_name(month: int) -> str:
    return ["siječanj", "veljača", "ožujak", "travanj", "svibanj", "lipanj",
            "srpanj", "kolovoz", "rujan", "listopad", "studeni", "prosinac"][month - 1]


def get_weekday_name(weekday: int) -> str:
    return ["pon", "uto", "sri", "čet", "pet", "sub", "ned"][weekday - 1]


def get_month_length(month: int) -> int:
    if month == 2:
        return 28
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    return 30


def get_month_starting_day(year: int, month: int) -> int:
    return datetime.datetime(year, month, 1).weekday()

