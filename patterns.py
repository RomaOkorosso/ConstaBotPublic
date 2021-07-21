# import help_func
#
# exp = help_func.exp_to_paragon(334, 50532320)
#
# print(exp)
# import datetime
# import calendar
# import pytz
#
# a = datetime.datetime.now(tz=pytz.utc)
# a = str(a)
# start_date = datetime.datetime.now(tz=pytz.utc)
# days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
# new_date = start_date + datetime.timedelta(days=days_in_month)
# print(new_date, '\n', start_date + datetime.timedelta(days=10))


# class Singleton(object):
# #     def __init__(self):
# #
# #     def __new__(cls):
# #         if not hasattr(cls, 'instance'):
# #             cls.instance = super(Singleton, cls).__new__(cls)
# #         return cls.instance
# #
# #
# # s = Singleton()
# # print("Object created", s)
# # s1 = Singleton()
# # print("Object created", s1)

import threading
import time


def foo():
    b = [1, 1, 1, 1, 1]

    print(time.ctime())
    print(
        threading.active_count(),
        "that is num:",
        threading.get_ident(),
        "len = ",
        len(b),
    )
    a = threading.Timer(1, foo).start()


foo()
