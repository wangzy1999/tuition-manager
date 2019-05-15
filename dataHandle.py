#!/usr/bin/env python
# coding: utf-8

import sqlite3
import json
import datetime


def connect_db():
    # connect content database
    con = sqlite3.connect('student.db')
    cur = con.cursor()
    return con, cur

def logic_del(name):
    con, cur = connect_db()
    cur.execute("delete from STU where name=? ",(name, ))
    con.commit()
    close_db(con, cur)
    return 1

def sql_insert(name, value, last, state):
    # insert data
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


def total():
    con, cur = connect_db()
    cur.execute("select * from STU where state!='gunle'")
    data = cur.fetchall()
    close_db(con, cur)
    total = len(data)
    fee = 0
    benyue = 0
    for i in data:
        value = json.loads(i[2])
        fee += int(value.get("总缴费", 0))
        yueshu = int(value.get('剩余月数', 0))
        left_fee = int(value.get('剩余学费', 0))
        if yueshu != 0:
            benyue += left_fee/yueshu
    return total, fee, int(benyue)


def sql_select(name):
    con, cur = connect_db()
    cur.execute('select * from STU where name=?', (name,))
    data = cur.fetchall()
    close_db(con, cur)
    text = []
    for i in data:
        value = json.loads(i[2])
        text = str(i[0]) + "--姓名:%s --%s --上次缴费:%s --状态:%s"%(i[1], str(value).replace("'", '')\
			.replace("{", '').replace('}', '').replace(',', '--'), i[3], i[4])
    return text

def pass_month():
    con, cur = connect_db()
    cur.execute("select *from STU where state!='gunle'")
    data = cur.fetchall()
    for i in data:
        name = i[1]
        value = json.loads(i[2])
        left_fee = int(value.get('剩余学费', 0))
        left_yue = int(value.get('剩余月数', 0))
        if left_yue != 0:
            left_fee = left_fee-left_fee/left_yue
            left_yue -= 1
            value.update({
            '剩余学费':left_fee, '剩余月数':left_yue
        })
            value = json.dumps(value)
            cur.execute("update STU set value=? where name=?",(value, name,))
        if left_yue == 0:
            pass
    con.commit()
    close_db(con, cur)
def show_data():
    con, cur = connect_db()
    cur.execute("select *from STU where state!='gunle'")
    data = cur.fetchall()
    close_db(con, cur)
    result = []
    j=1
    for i in data:
        value = json.loads(i[2])
        text = str(j) + "--姓名:%s --%s --上次缴费:%s --状态:%s"%(i[1], str(value).replace("'", '')\
			.replace("{", '').replace('}', '').replace(',', '--'), i[3], i[4])
        result.append(text)
        j+=1
    return result

def find_guoqi():
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


def sql_all_select():
    con, cur = connect_db()
    cur.execute('select *from STU')
    result = cur.fetchall()
    close_db(con, cur)
    return result


def close_db(con, cur):
    # close database
    cur.close()
    con.close()

