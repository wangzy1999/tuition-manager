#!/usr/bin/env python
# coding: utf-8

import sqlite3
import json
import datetime


def connect_db():
    """
    连接数据库
    """
    con = sqlite3.connect('student.db')
    cur = con.cursor()
    return con, cur


def real_del(name:'学生姓名'):
    """
    物理删除学生信息
    """
    con, cur = connect_db()
    cur.execute("delete from STU where name=? ",(name, ))
    con.commit()
    close_db(con, cur)


def sql_insert(name:'学生姓名', value:'缴费信息', last:'上次缴费时间', state:'是否在学'):
    """
    插入信息
    """
    con, cur = connect_db()
    command = "INSERT INTO STU (name, value, last, state)VALUES('" + \
        name+"', '"+value+"', '"+last+"', '"+state+"')"
    try:
        cur.execute(command)
        con.commit()
    except Exception as e:
        print(e)
    finally:
        close_db(con, cur)


def statistic():
    """
    统计总信息
    return 学生数量、总收入、当月收入
    """
    con, cur = connect_db()
    cur.execute("select * from STU where state!='gunle'")
    data = cur.fetchall() #所有学生信息 -> list
    close_db(con, cur)
    amount = len(data) #在读学生数量 -> int
    total_income = 0 #累计总收入
    instant_income = 0 #当月收入

    for i in data: #每个学生的信息 -> list
        value = json.loads(i[2]) #每个学生的缴费信息 -> dict
        total_income += int(value.get("总缴费", 0))
        left_time = int(value.get('剩余月数', 0))
        left_fee = int(value.get('剩余学费', 0))
        if left_time != 0: #如果还有学费
            instant_income += left_fee/left_time #本月收入=剩余学费/剩余月数

    return amount, total_income, int(instant_income)


def sql_select(name:'学生姓名'):
    """
    按姓名提取信息
    return 一条学生信息
    """
    con, cur = connect_db()
    cur.execute('select * from STU where name=?', (name,))
    data = cur.fetchall()
    close_db(con, cur)
    text = []
    for i in data: #每个学生的信息 -> list
        value = json.loads(i[2]) #每个学生的缴费信息 -> dict
        text = str(i[0]) + "--姓名:%s --%s --上次缴费:%s --状态:%s"%(i[1], str(value).replace("'", '')\
			.replace("{", '').replace('}', '').replace(',', '--'), i[3], i[4])
    return text


def pass_month():
    """
    更新一个月数据
    """
    con, cur = connect_db()
    cur.execute("select *from STU where state!='gunle'")
    data = cur.fetchall()
    for i in data:
        name = i[1]
        value = json.loads(i[2])
        left_fee = int(value.get('剩余学费', 0))
        left_time = int(value.get('剩余月数', 0))
        if left_time != 0:
            left_fee = int(left_fee-left_fee/left_time)
            left_time -= 1
            value.update({
            '剩余学费':left_fee, '剩余月数':left_time
        })
            value = json.dumps(value)
            cur.execute("update STU set value=? where name=?",(value, name,))
        if left_time == 0:
            #TODO: 需要添加一个反馈信息
            pass
    con.commit()
    close_db(con, cur)


def show_data():
    """
    显示信息
    return 所有学生信息
    """
    con, cur = connect_db()
    cur.execute("select *from STU where state!='gunle'")
    data = cur.fetchall()
    close_db(con, cur)
    result = []
    j=1 #显示编号
    for i in data:
        value = json.loads(i[2])
        text = str(j) + "--姓名:%s --%s --上次缴费:%s --状态:%s"%(i[1], str(value).replace("'", '')\
			.replace("{", '').replace('}', '').replace(',', '--'), i[3], i[4])
        result.append(text)
        j+=1
    return result


def find_expiry():
    """
    查找已过期的学生
    return 过期学生信息
    """
    con, cur = connect_db()
    cur.execute("select *from STU where state!='gunle'")
    data = cur.fetchall()
    close_db(con, cur)
    now_time = datetime.datetime.now()
    now_time_str = str(now_time.strftime('%Y-%m-%d'))
    result = []
    j=1
    for i in data:
        value = json.loads(i[2])
        daoqi_time_str = value.get('到期时间', 0)
        text = str(j) + "--姓名:%s --%s --上次缴费:%s --状态:%s"%(i[1], str(value).replace("'", '')\
			.replace("{", '').replace('}', '').replace(',', '--'), i[3], i[4])
        if daoqi_time_str<=now_time_str:
            result.append(text)
            j+=1
    return result

def close_db(con, cur):
    """
    关闭数据库
    """
    cur.close()
    con.close()

