import re
import os
import pickle

from config import setting
from src.class_type import Staff, Lecturer, Students, Programs, Course, Campus


def manage_campus():
    mapping = {"1": {"title": "增设课程", "function": "add_course"},
               "2": {"title": "开设班级", "function": "start_program"},
               "3": {"title": "雇佣员工", "function": "hire"},
               "4": {"title": "发放工资", "function": "pay_salary"},
               "5": {"title": "学生统计", "function": "count_student"},
               "6": {"title": "员工列表", "function": "list_staffs"},
               "7": {"title": "班级列表", "function": "list_programs"},
               "8": {"title": "开设分校", "function": "open_campus"}}

    while True:

        print("  校区管理系统页面  ".center(70,"*"))
        if not os.path.exists(setting.SCHOOL_DATA):
            print("    目前还没有任何校区数据，请创建第一个校区     ".center(70, "-"))
            new_campus = Campus.open_campus()
            return

        while True:
            campus_dict = pickle.load(file=open(setting.SCHOOL_DATA, "rb"))
            print(" 现有如下校区可供管理操作  ".center(30,"-"))
            for k, v in campus_dict.items():
                print(" {} -- {} ".format(k, v.name))
            s_n = input("--- 请输入学区序号(3位|Q退出）--->").strip()
            if s_n.upper() == "Q":
                return

            try:
                campus_obj = Campus.load(s_n)
                print(" 欢迎进入{} - {} ".format(campus_obj.index, campus_obj.name))
                break

            except(ValueError, AttributeError):
                print("输入非法")

        while True:
            print("  {}   请选择功能[1-8]  ".format(campus_obj.name).center(100, "-"))
            for k, v in mapping.items():
                print(" {}:{}".format(k, v["title"]), end="    ")
            print("\n","请选择 【1 - 8】".center(100, "-"))

            choice = input("\n 请选择功能(输入序号, Q退出）>>>").strip()
            if choice.upper() == "Q":
                break

            try:
                func = mapping.get(choice).get("function")
                operate = getattr(campus_obj, func)
                operate()
                campus_obj.save(campus_obj)

            except(ValueError, IndexError, AttributeError):

                print("请选择 1-8 之间的数字")


def manage_program():
    mapping = {"1": {"title": "学生列表", "function": "stud_list"},
               "2": {"title": "招收学生", "function": "enroll"},
               "3": {"title": "学生转学", "function": "transfer"},
               "4": {"title": "学生退学", "function": "dropoff"}}

    while True:

        print("  班级管理系统页面  ".center(70, "*"))
        try:
            program_dict = pickle.load(file=open(setting.PROGRAM_DATA, "rb"))
        except FileNotFoundError:
            print("目前还没有任何校区开设班级，请先创建班级！")
            return

        while True:
            print("  现有如下班级可供管理操作  ".center(30, "-"))
            for k, v in program_dict.items():
                for pro, pro_obj in v.items():
                    print("校区:{}   课程号:{}   课程名:{}".format(k, pro, pro_obj.name))

            s_n = input("请输入班级序号：(6位,Q退出）").strip()
            if s_n.upper() == "Q":
                return

            camp_indx = s_n[:3]
            pro_indx = s_n

            try:
                program_obj = program_dict[camp_indx].get(pro_indx)
                if program_obj:
                    break
                else:
                    print("   无效输入   ")
            except (KeyError, ValueError, AttributeError):
                print("   无效的输入   ")

        while True:

            print("---".join("{}:{}".format(k, v["title"]) for k, v in mapping.items()))
            choice = input("请选择功能(输入序号）>>>").strip()
            if choice.upper() == "Q":
                break
            try:
                func = mapping[choice]["function"]
                operate = getattr(program_obj, func)
                operate()
                program_obj.save(program_obj)
            except (ValueError, IndexError,KeyError):
                print("请选择 1-4 之间的数字")


def manage_student():
    smap = {"1": {"title": "学生打卡", "function": "sign_in"},
            "2": {"title": "签到纪录", "function": "sign_in_li"},
            "3": {"title": "学生概况", "function": "over_view"}}

    while True:

        with open(setting.STUDENT_DATA, "rb") as s:
            student_dict = pickle.load(s)

        print("学生管理系统页面".center(70, "+"))

        s_n = input("请输入学生序号(Q退出）：(9位）").strip()
        if s_n.upper() == "Q":
            break

        try:
            table = list(re.findall("(((\d{3})\d{3})\d{3})", s_n))[0]
        except (ValueError, TypeError, IndexError):
            print("输入有误")
            continue

        try:
            stud_obj = student_dict.get(table[-1]).get(table[-2]).get(table[-3])
        except AttributeError:
            print("没有查到该学员！")
            continue

        if not stud_obj:
            print("没有查找到该学员")
            continue

        while True:

            print("    请选择功能[1-3]    ".center(70, "-"))
            print("---".join("{}:{}".format(k, v["title"]) for k, v in smap.items()))
            choice = input("   请选择功能(输入序号）>>>").strip()
            try:
                func = smap.get(choice).get("function")
                operate = getattr(stud_obj, func)
                operate()
                Students.save(stud_obj)
                break

            except (ValueError, IndexError):
                print("请选择 1-3 之间的数字")


def manage_staff():
    mmap = {"1": {"title": "员工打卡", "function": "sign_in"},
            "2": {"title": "员工概况", "function": "over_view"},
            "3": {"title": "员工签到表", "function": "sign_in_li"},
            "4": {"title": "员工概况", "function": "over_view"}}

    print("员工管理系统页面".center(70, "-"))

    while True:
        s_n = input("请输入员工序号(以s结尾的7位编号,Q退出）：").strip()
        if s_n.upper() == "Q":
            break

        try:
            choice = list(re.findall("((\d{3})\d{3}s)", s_n))[0]
            s_indx, c_indx = list(choice)
        except(ValueError, IndexError, TypeError):
            print("输入有误")
            continue

        try:
            staff_obj = Staff.load().get(c_indx).get(s_indx)
        except(ValueError, IndexError):
            print("没有查找到该员工")
            continue

        while True:
            for k, v in mmap.items():
                print(" {}:{}  ".format(k, v["title"]), end="    ")

            choice = input("\n  请选择功能[1-4] --->  ").strip()
            try:
                func = mmap.get(choice).get("function")
                operate = getattr(staff_obj, func)
                operate()
                Staff.save(staff_obj)
                break
            except(ValueError, IndexError):
                print("请选择 1-4 之间的数字")


def manage_lecturer():
    lmap = {"1": {"title": "教师设置教授课程", "function": "add_course"},
            "2": {"title": "教师打卡", "function": "sign_in"},
            "3": {"title": "教师签到表", "function": "sign_in_li"},
            "4": {"title": "教师概况", "function": "over_view"}}

    print("   教师管理系统页面   ".center(70, "*"))
    while True:

        s_n = input("请输入员工序号(以t结尾的7位编号,Q退出）：").strip()
        if s_n.upper() == "Q":
            break

        try:
            choice_2 = list(re.findall("((\d{3})\d{3}t)", s_n))[0]
            l_indx, c_indx = list(choice_2)
        except(ValueError, IndexError):
            print("输入有误")
            continue

        try:
            lec_obj = Lecturer.load().get(c_indx).get(l_indx)
            if not lec_obj:
                print("   没有查到这个老师    ")
                continue

        except (AttributeError, IndexError, FileNotFoundError, KeyError):
            print("     没有查询到该老师    ")


        while True:
            for k, v in lmap.items():
                print(" {}:{}  ".format(k, v["title"]), end="    ")
            choice = input("\n  请选择功能[1-4] --->  ").strip()

            try:
                func = lmap.get(choice).get("function")
                operate = getattr(lec_obj, func)
                operate()
                Lecturer.save(lec_obj)
                break

            except (ValueError, IndexError,AttributeError):
                print("请选择 1-4 之间的数字")
