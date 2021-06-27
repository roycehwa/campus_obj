import re
from datetime import datetime
import pickle
from config import setting


class Campus(object):
    """
    self.name:学校名称
    self.index:三位数校区序号，在开设时自动生成（根据类campus_dict长度+1）
    self.balance:账户
    self.staff/lecturer 该学区员工和教师列表，存储员工号便于搜索
    self.course: 该学区可以授课的种类
    self.program_list：学区开班列表（存储班级编号 - 六位，前三位是校区号，后三位是班级号）
    self.branch_list：开分校列表（学区编号）
    """
    group = "DIGI Edu Camp"
    website = "www.TeachU.edu"
    # campus_dict = {}  # {campus.index :campus_obj...}

    def __init__(self, name, location):
        self.name = name
        self.index = None
        # 学校序号，三位数字
        self.location = location
        self.__balance = 0
        self.staff = []
        self.lecturer = []
        # staff和lecturer列表均存储员工号
        self.course = []

    @classmethod
    def open_campus(cls):

        while True:
            basic = input(">>>开设新校区, 请输入[校区名称|地址]>>>")
            try:
                name, location = re.split("\|", basic)
                new_campus = Campus(name, location)
                break
            except (IndexError, ValueError):
                print("输入不正确！")
        try:
            camp_dict = pickle.load(file=open(setting.SCHOOL_DATA, "rb"))
            new_campus.index = str(len(camp_dict) + 1).zfill(3)
        except FileNotFoundError:
            new_campus.index = "001"

        Campus.save(new_campus)
        print("----   创建新校区成功，{}校区序号为 {}   ----".format(new_campus.name, new_campus.index))

    @classmethod
    def save(cls, campus_obj):
        try:
            camp_dict = pickle.load(file=open(setting.SCHOOL_DATA, "rb"))
        except FileNotFoundError:
            camp_dict = {}

        camp_dict[campus_obj.index] = campus_obj
        pickle.dump(camp_dict, file=open(setting.SCHOOL_DATA, "wb"))

    @classmethod
    def load(cls, campus_index):
        with open(setting.SCHOOL_DATA, "rb") as c:
            campus_dict = pickle.load(c)
            return campus_dict.get(campus_index)

    def add_course(self):
        # 增设课程种类：开设的课程将被添加到COURSE_DATA，课程序号添加到校区course_list属性中
        new_course = None  # 初始值，开设成功后将课程对象赋值给他
        try:
            course_dict = pickle.load(file=open(setting.COURSE_DATA, 'rb'))
        except FileNotFoundError:
            course_dict = {}

        print("    {}校区可以添加如下现有课程    ".format(self.name))
        for k, v in course_dict.items():
            if k not in self.course:
                print("    {} -- {}    ".format(k, list(v)[0]))
        # 全部的课程列表去掉本校区已有的课程

        while True:
            choice = input("输入添加课程序号(Q退出，直接添加新课程）：")
            if choice.upper() == "Q":
                break

            if choice in course_dict.keys():
                if choice not in self.course:
                    self.course.append(choice)
                    print("  {} 校区新增加{}课程".format(self.name, list(course_dict[choice])[0]))
                    Campus.save(self)
                    return
                else:
                    print("输入错误")

        while True:
            isexist = False  # 课程是否存在在本学区course列表里
            param = input("{}增加新课程请输入(Q退出）: [课程名|价格|大纲]".format(self.name)).strip()
            params = param.split("|")

            if param.upper() == "Q":
                return

            else:
                if len(params) != 3:
                    print("输入非法！")
                    continue

            for k in course_dict.values():
                if k.get(params[0]):
                    print("   学校已经有该课程，无需重新开设！   ")
                    isexist = True
                    break

            if isexist:
                break

            else:
                try:
                    new_course = Course(*params)
                    break

                except (ValueError, IndexError):
                    print("输入格式错误")

        if new_course:
            self.course.append(new_course.index)
            print("  {}校区新增加{}课程,编号{} ".format(self.name, new_course.name, new_course.index))
            Campus.save(self)
        else:
            print("添加课程失败")

    def start_program(self):

        # 开设授课班级
        print("  {}开设新班级流程  ".format(self.name).center(50, "*"))
        course_dict = Course.load()

        while True:
            nick = input("{}开设新班级，该班级名称(Q退出）>>".format(self.name))
            if nick.upper() == "Q":
                break

            while True:
                for i in self.course:
                    print(i, list(course_dict.get(i))[0])
                choice = input("选择课程种类>>>").strip()

                if choice in self.course:
                    break
                else:
                    print("输入错误！")

            try:
                course_name = list(course_dict.get(choice))[0]
                course_obj = course_dict.get(choice).get(course_name)

            except (ValueError, AttributeError, IndexError):
                print("输入错误")
                continue

            semester = input("本课程第几期：").strip()
            program_name = "{}-{}-{}-{}期".format(self.name, nick, course_name, semester)
            confirm = input(program_name + "确认开设新课程(y/n)？")
            if confirm.upper() == "Y":
                program = Programs(program_name, course_obj, self, semester)
                break
            else:
                print("开课未成功！")
                return

        print("现已开设{},请分配导师。".format(program_name))

        lec_dict = Lecturer.load().get(self.index)

        while True:

            print("{}现有授课老师：".format(self.name))
            for k, v in lec_dict.items():
                print("{} - {} - 教授课程: ".format(k, v.name))
                for course_detail in v.course.values():
                    course_name = (list(course_detail)[0])
                    print(course_name)

            lec_choice = input("请选择导师(输入序号）:").strip()
            if lec_choice not in lec_dict.keys():
                print(" 输入错误(三位数+t)")
                continue

            try:
                lec_object = lec_dict.get(lec_choice)
                result = program.assign_lecturer(lec_object)

            except ValueError:
                print("Value Error")
            except AttributeError:
                print("Attribute Error")

            if result:
                Programs.save(program)
                Campus.save(self)
                break

    def hire(self):

        # 雇佣员工和老师
        print("  {}招聘新员工流程  ".format(self.name).center(50, "*"))

        while True:
            basic = input("请输入招收员工:输入姓名-年龄(数字)-性别(男/女）").strip()
            try:
                name, age, gendre = re.findall("(\w+)-(\d{1,2})-([男|女])", basic)[0]
                break
            except (ValueError, IndexError):
                print("输入格式不对")

        while True:
            s = input("请输入工资(整数）")
            try:
                salary = int(s)
                break
            except (ValueError):
                print("输入格式或者类型不对")

        while True:
            islecturer = input("新员工是否为授课老师(y/n) >>>").strip()

            if islecturer.upper() == "N":
                title = input("请输入员工职位 -->  ").strip()
                staff = Staff(self, name, age, gendre, title, salary)
                Staff.save(staff)
                print(staff, "招收完成")
                break

            elif islecturer.upper() == "Y":
                title = "授课老师"
                lecturer = Lecturer(self, name, age, gendre, title, salary)
                Lecturer.save(lecturer)
                print("招收完成", lecturer)
                break

            else:
                print("输入错误（y/n) ")

    def pay_salary(self):

        self.list_staffs()
        try:
            staff_dic = Staff.load().get(self.index)
        except TypeError:
            staff_dic = {}

        try:
            lec_dic = Lecturer.load().get(self.index)
        except TypeError:
            lec_dic = {}

        while True:
            target = {}
            choice = input("向{}校区员工支付工资 1. 全体教师   2.全体员工   3.全体教师和员工  Q:退出".format(self.name)).strip()

            if choice.upper() == "Q":
                return
            elif choice == "1":
                target.update(lec_dic)
                break
            elif choice == "2":
                target.update(staff_dic)
                break
            elif choice == "3":
                target.update(lec_dic)
                target.update(staff_dic)
                break
            else:
                print("  选择错误  ")

        fee = 0
        for employee in target.values():
           self.__balance -= employee.salary
           fee += employee.salary
           print(" {}向{}支付了工资{}元 ".format(self.name, employee.name, employee.salary))

        Campus.save(self)
        print("支付完成，共向{}人支付{}元，{}校区账户余额{}元".format(len(target), fee, self.name, self.__balance))

    def count_student(self):

        stud_dict = Students.load()
        if not stud_dict:
            print(" {} 还没有学生。".format(self.name))
            return

        if not stud_dict.get(self.index):
            print(" {} 还没有学生。".format(self.name))
            return

        total = 0
        for program, stud_list in stud_dict.get(self.index).items():
            total += len(stud_list)
            print("  班级编号 {}  ".format(program))
            for stud_index, stud_obj in stud_list.items():
                print("  {} --  {} ".format(stud_index, stud_obj.name))
        print("  {}校区共有学生{}人 ".format(self.name, total))


    def list_programs(self):

        try:
            program_dict = Programs.load().get(self.index)
            print("--- {}现在开设班级{}个 ---".format(self.name, len(program_dict)))
            for program_index, program_obj in program_dict.items():
                print("{} -- {}".format(program_index, program_obj.name))
        except (AttributeError, TypeError):
            print("没有查询到班级")


    def list_staffs(self):
        try:
            staff_dict = Staff.load().get(self.index)
            print(" {}现在有员工{}人 ".format(self.name, len(staff_dict)))
            for staff in staff_dict.values():
                print("{} -- {}".format(staff.index, staff.name))
        except (AttributeError, TypeError):
            print("没有查询到员工")

        try:
            lec_dict = Lecturer.load().get(self.index)
            print(" {}现在有老师{}人 ".format(self.name, len(lec_dict)))
            for lecturer in lec_dict.values():
                print("{} -- {}".format(lecturer.index, lecturer.name))
        except (AttributeError, TypeError):
            print("没有查询到老师")

class Course(object):
    #    course_dict = {} # {序号：{课程名：课程对象},...}

    def __init__(self, name, price, outline):
        self.name = name
        self.price = int(price)
        self.outline = outline
        self.index = None
        Course.add_new(self)

    @classmethod
    def add_new(cls, course_obj):
        try:
            course_dict = pickle.load(file=open(setting.COURSE_DATA, "rb"))
            for c_v in course_dict.values():  # 用同样名称
                if course_obj.name in c_v.items():
                    return
        except FileNotFoundError:
            course_dict = {}

        course_obj.index = str(len(course_dict) + 1).zfill(2)
        course_dict[course_obj.index] = {course_obj.name: course_obj}
        with open(setting.COURSE_DATA, "wb") as e:
            pickle.dump(course_dict, e)

    @classmethod
    def load(cls):
        try:
            course_dict = pickle.load(file=open(setting.COURSE_DATA, "rb"))
            return course_dict
        except FileNotFoundError:
            return None

class Programs(object):

    # 存储所有班级信息{"校区index":{program_index: program_obj,....}}

    def __init__(self, name, course_obj, campus_obj, semester):
        self.name = name
        self.course = course_obj.index
        self.campus = campus_obj.index
        self.semester = semester
        self.student_list = {}
        # {"campus" : { "program" : { "student" : "student_obj"...}}}
        try:
            program_dict = pickle.load(file=open(setting.PROGRAM_DATA, "rb")).get(campus_obj.index)
            ind = str(len(program_dict) + 1).zfill(3)
        except (FileNotFoundError,AttributeError,TypeError):
            ind = "001"
        self.index = campus_obj.index + ind
        self.student_list = {self.campus: {self.index: {}}}
        self.lecturer = None

    @classmethod
    def save(cls, program_obj):
        try:
            program_dict = pickle.load(file=open(setting.PROGRAM_DATA, "rb"))
        except FileNotFoundError:
            program_dict = {program_obj.campus: {program_obj.index: program_obj}}

        if not program_dict.get(program_obj.campus):
            program_dict[program_obj.campus] = {}

        program_dict[program_obj.campus].update({program_obj.index:program_obj})
        pickle.dump(program_dict, file=open(setting.PROGRAM_DATA, "wb"))

    @classmethod
    def load(cls):
        try:
            program_dict = pickle.load(file=open(setting.PROGRAM_DATA, "rb"))
            return program_dict
        except FileNotFoundError:
            return None

    def assign_lecturer(self, lec_obj):
        # 分配导师，传入lecturer类实例
        if not lec_obj.course.keys():
            print("  该导师还没有设置授课类型！重新选择导师...  ")

        for course in lec_obj.course.keys():
            if self.course == course:
                print("{}将任教{}".format(lec_obj.name, self.name))
                self.lecturer = lec_obj
                return True

        print("这个导师科目不匹配，重新分配")
        return None

    def enroll(self):
        student_obj = Students()
        student_obj.enroll()
        student_obj.pay_tuition(self)

        if student_obj.tuition:
            student_obj.campus = self.campus
            student_obj.program = self.index
            if self.student_list:
                ind = str(len(self.student_list.get(self.campus).get(self.index)) + 1).zfill(3)
                student_obj.index = self.index + str(ind)
            else:
                self.student_list = {self.campus: {self.index: {}}}
                student_obj.index = self.index + "001"
            Students.save(student_obj)
            self.student_list[self.campus][self.index].update({student_obj.index: student_obj})
            print("  {}参加了{}班  ".format(student_obj.name, self.name))

        else:
            print("报名未成功")

    def stud_list(self):  # 输出学生列表

        print("{}...学生列表".format(self.name))
        try:
            for stud_obj in self.student_list.get(self.campus).get(self.index).values():
                print(stud_obj.index, stud_obj.name)
        except (TypeError,AttributeError):
            print("该班级还没有学生")

    def transfer(self):
        self.stud_list()
        while True:
            choice = input("   请输入转学学生序号(Q退出） ---->  ").strip()

            if choice.upper()=="Q":
                return

            stud_object = self.student_list.get(self.campus).get(self.index).get(choice)
            if stud_object:
                break
            else:
                print("   没有查询到该学生   ")

        program_dict = Programs.load()

        while True:
            print(" 启动{}转学程序...其他班级列表如下：".format(stud_object.name))
            for k, v in program_dict.items():
                for prog_i, prog_obj in v.items():
                    print(" {} - {} ".format(prog_i, prog_obj.name))

            receive_program = input("请输入新课程号(6位）").strip()
            try:
                prog, camp = list(re.findall("((\d{3})\d{3})",receive_program))[0]
            except(ValueError,IndexError):
                print(" 输入错误  ")
                continue

            try:
                accpt_obj = program_dict.get(camp).get(prog)
            except (FileNotFoundError, KeyError, AttributeError):
                print("  没有查询到该班级  ")
                continue

            if self.index == accpt_obj.index:
                print("  不能在同一个班级转学  ")
            else:
                break

        self.student_list[self.campus][self.index].pop(stud_object.index)
        Programs.save(self)

        s_dict = Students.load()
        s_dict[self.campus][self.index].pop(stud_object.index)
        pickle.dump(s_dict, file=open(setting.STUDENT_DATA, "wb"))

        ind = str(len(accpt_obj.student_list[accpt_obj.campus][accpt_obj.index]) + 1)
        new_ind = accpt_obj.index + ind.zfill(3)
        stud_object.index = new_ind
        stud_object.campus = accpt_obj.campus
        stud_object.program = accpt_obj.index
        Students.save(stud_object)

        accpt_obj.student_list[accpt_obj.campus][accpt_obj.index].update({stud_object.index:stud_object})
        Programs.save(accpt_obj)

        date = datetime.strftime(datetime.now(), "%y-%m-%d")
        print("{}于{}\n从{}---转学到---> {}".format(stud_object.name, date, self.name, accpt_obj.name))



    def dropoff(self):

        self.stud_list()
        while True:
            choice = input("   请输入转学学生序号(Q退出） ---->  ").strip()
            if choice.upper() == "Q":
                return

            stud_object = self.student_list.get(self.campus).get(self.index).get(choice)
            if stud_object:
                break
            else:
                print("   没有查询到该学生   ")

        confirm = input(" 启动{}退学程序...确认？(y确认，其他退出）".format(stud_object.name)).strip()
        if confirm.upper() != "Y":
            return
        else:
            s_dict = Students.load()
            s_dict[self.campus][self.index].pop(stud_object.index)
            pickle.dump(s_dict, file=open(setting.STUDENT_DATA, "wb"))
            self.student_list[self.campus][self.index].pop(stud_object.index)
            Programs.save(self)
            date = datetime.strftime(datetime.now(), "%y-%m-%d")
            print("{}于{}从{}退学".format(stud_object.name, date, self.name))


class Individual(object):
    role = "Individual"

    def __init__(self):
        self.name = None
        self.age = None
        self.gendre = None
        self.account = 100000

class Staff(Individual):
    role = "Staff"

    # staff_list = {}   {校区序号：{员工号：员工实例对象，...}}

    def __init__(self, campus_obj, name, age, gendre, title, salary):
        super().__init__()
        self.campus = campus_obj.index
        self.name = name
        self.age = age
        self.gendre = gendre
        self.title = title
        self.salary = salary
        self.sign_in_list = []
        try:
            staff_dict = pickle.load(file=open(setting.STAFF_DATA, "rb"))
            index = str(len(staff_dict.get(self.campus)) + 1).zfill(3) + "s"
            self.index = self.campus + index

        except(FileNotFoundError, KeyError, TypeError):
            self.index = self.campus + "001s"

    def sign_in(self):
        sign_date = datetime.now()
        sign_d = datetime.strftime(sign_date, "%y-%m-%d")
        self.sign_in_list.append(sign_d)
        print("{} {}签到成功".format(self.name, sign_d))

    def sign_in_li(self):
        print("  {} 上班签到如下：".format(self.name))
        text = "--".join(self.sign_in_list)
        print(text)

    @classmethod
    def load(cls):
        try:
            staff_dict = pickle.load(file=open(setting.STAFF_DATA, "rb"))
            return staff_dict
        except FileNotFoundError:
            return None

    @classmethod
    def save(cls, staff_obj):
        try:
            staff_dict = pickle.load(file=open(setting.STAFF_DATA, "rb"))
        except FileNotFoundError:
            staff_dict = {staff_obj.campus: {}}

        if not staff_dict.get(staff_obj.campus):
            staff_dict[staff_obj.campus] = {}

        staff_dict[staff_obj.campus].update({staff_obj.index: staff_obj})
        pickle.dump(staff_dict, file=open(setting.STAFF_DATA, "wb"))

    def over_view(self):
        line = "姓名：{}  职位：{} 校区：{} 员工号：{} ".format(self.name, self.title, self.campus, self.index)
        print(line)

    def __str__(self):
        line = "姓名：{}  职位：{} 校区：{} 员工号：{} ".format(self.name, self.title, self.campus, self.index)
        return line

class Lecturer(Staff):
    role = "Lecturer"

    # {校区序号：{员工号：老师实例对象，...}}

    def __init__(self, campus_obj, name, age, gendre, title, salary):
        super().__init__(campus_obj, name, age, gendre, title, salary)
        self.course = {}
        try:
            lec_dict = pickle.load(file=open(setting.LECTURER_DATA, "rb"))
            self.index = self.campus + str(len(lec_dict.get(campus_obj.index)) + 1).zfill(3) + "t"
        except (FileNotFoundError, AttributeError, TypeError):
            self.index = self.campus + "001t"

    @classmethod
    def save(cls, lec_obj):
        try:
            lec_dict = pickle.load(file=open(setting.LECTURER_DATA, "rb"))
        except FileNotFoundError:
            lec_dict = {lec_obj.campus: {}}

        if not lec_dict.get(lec_obj.campus):
            lec_dict[lec_obj.campus] = {}

            # 文件不存在，设置新的老师列表
        lec_dict[lec_obj.campus].update({lec_obj.index: lec_obj})
        pickle.dump(lec_dict, file=open(setting.LECTURER_DATA, "wb"))

    @classmethod
    def load(cls):
        try:
            lec_dict = pickle.load(file=open(setting.LECTURER_DATA, "rb"))
            return lec_dict
        except FileNotFoundError:
            return {}

    def add_course(self):
        print("  设置{}老师授课门类 -->>>   ".format(self.name))
        course_dict = Course.load()

        while True:
            for k, v in course_dict.items():
                if k not in self.course.keys():
                    for m in v.values():
                        print(k, m.name, end="   ***   ")

            choice = input("选择添加科目序号(Q退出）").strip()
            if choice.upper() == "Q":
                break

            try:
                course_ = course_dict.get(choice)
                self.course[choice] = course_
                print("{}增加了授课种类{}".format(self.name, list(course_.keys())[0]))

            except IndexError or TypeError:
                print("选择不合法")

    def sign_in(self):
        sign_ = datetime.now()
        sign_d = datetime.strftime(sign_, "%y-%m-%d")
        self.sign_in_list.append(sign_d)
        print("{} {}签到成功".format(self.name, sign_d))

    def sign_in_li(self):
        print("  {} 上班签到如下：".format(self.name))
        text = "--".join(self.sign_in_list)
        print(text)

    def over_view(self):
        camp = Campus.load(self.campus).name
        title = "员工姓名：{}  职位：{}  校区：{} 员工号：{}  教授课程：".format(self.name, self.title, camp, self.index)
        if self.course:
            courses = '***'.join("{}".format(list(k)[0]) for k in self.course.values())
        else:
            courses = "  还没有添加可教授课程  "

        print(title, courses)

class Students(Individual):
    role = "Student"

    # Student_list = {} # {校区序号：{班级序号：{ 学生序号：对象，...}}
    def __init__(self):
        super().__init__()
        self.campus = None
        self.program = None
        self.tuition = False
        self.index = None
        self.sign_in_list = []

    def enroll(self):

        while True:
            basic = input("请输入招收学生:输入姓名|年龄(数字）|性别(男/女）").strip()
            try:
                self.name, self.age, self.gendre = re.findall("(\w+)\|(\d{1,2})\|([男|女])", basic)[0]
                break
            except IndexError:
                print("输入格式不对")

    def pay_tuition(self, program_obj):
        for name, course_obj in Course.load().get(program_obj.course).items():
            print("支付{}班学费...".format(name), end="-->")
            campus_obj = Campus.load(program_obj.campus)
            if self.account <= course_obj.price:
                print("余额不足")

            else:
                self.account -= course_obj.price
                campus_obj._Campus__balance += course_obj.price
                print("{}支付了课程费{}元".format(self.name, course_obj.price))
                self.tuition = True
                Campus.save(campus_obj)

    def sign_in(self):
        sign_date = datetime.now()
        sign_d = datetime.strftime(sign_date, "%y-%m-%d")
        self.sign_in_list.append(sign_d)
        print("{} {}上课签到成功".format(self.name, sign_d))

    def sign_in_li(self):
        print("  {} 上课签到如下：".format(self.name))
        text = "--".join(self.sign_in_list)
        print(text)

    def over_view(self):
        pro = Programs.load().get(self.campus).get(self.program).name
        text = "学生姓名：{}  学号: {}  所在班级: {} ".format(self.name, self.index, pro)
        print(text)


    @classmethod
    def load(cls):
        try:
            stud_dict = pickle.load(file=open(setting.STUDENT_DATA, "rb"))
            return stud_dict
        except FileNotFoundError:
            return None

    @classmethod
    def save(cls, stud_obj):
        try:
            stud_dict = pickle.load(file=open(setting.STUDENT_DATA, "rb"))
        except FileNotFoundError:
            stud_dict = {stud_obj.campus: {stud_obj.program: {stud_obj.index: stud_obj}}}

        if not stud_dict.get(stud_obj.campus):
            stud_dict[stud_obj.campus] = {}

        if not stud_dict.get(stud_obj.campus).get(stud_obj.program):
            stud_dict[stud_obj.campus][stud_obj.program] = {}

        stud_dict.get(stud_obj.campus).get(stud_obj.program).update({stud_obj.index: stud_obj})
        pickle.dump(stud_dict, file=open(setting.STUDENT_DATA, "wb"))

