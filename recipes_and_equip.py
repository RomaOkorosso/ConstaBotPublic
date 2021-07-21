import psycopg2
import config
import time
import datetime
import pytz
from help_func import sep_by_3 as sep3


def send_resources(txt: str):
    resources = [[], []]
    if "Ресурсы:\n" in txt:
        left = txt.find("Ресурсы:\n") + len("Ресурсы:\n")
        lenght = len(txt)
        txt = txt[left:lenght]
        left = 0
        lenght = len(txt)
        right = 0
        while right != lenght:
            right = txt.find("\n", left)
            if right == -1:
                right = lenght
            res = txt[left:right]
            name = res[: res.find("(")]
            if "🗝" not in name:
                count = res[res.find("(") + 1 : res.find(")")]
            else:
                extra_left = res.find("(", res.find("(") + 1)
                count = res[extra_left + 1 : res.find(")", extra_left)]
            resources[0].append(name)
            resources[1].append(int(count))
            if right + 1 < lenght:
                left = right + 1
    return resources
