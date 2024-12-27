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


def calculate_easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return year, month, day

