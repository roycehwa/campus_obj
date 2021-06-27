import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import setting
from src.handler import manage_campus, manage_program, manage_student, manage_staff, manage_lecturer


def run():
    if __name__ == "__main__":
        start()


def start():

    mapping = {"1": {"title": "学校管理", "func": manage_campus},
               "2": {"title": "班级管理", "func": manage_program},
               "3": {"title": "学员管理", "func": manage_student},
               "4": {"title": "员工管理", "func": manage_staff},
               "5": {"title": "教师管理", "func": manage_lecturer}}

    while True:
        print("   校园管理系统【主页面】   ".center(70, "="))
        for k, v in mapping.items():
            print("   {}:{}   ".format(k, v["title"]), end=" ")

        choice = input("\n 请选择功能 》》》").strip()
        try:
            func = mapping[choice]["func"]
            func()

        except IndexError:
            print("非法选择")


run()