from flask import Flask, request, url_for, render_template, redirect
from dataHandle import sql_insert, sql_select, connect_db, close_db, show_data, logic_del, total, find_guoqi
import json
import sqlite3
import datetime
app = Flask(__name__)


@app.route('/')  # 这里是根目录，也就是打开链接第一个访问的页面
def index():
    student = show_data()
    if student == None or student == []:
        student = ["lack of data"]
    total_num, total_fee,benyue = total()
    return render_template('index.html', student=student, total=total_num, fee=total_fee, benyue=benyue)


@app.route('/delstu', methods=['GET', 'POST'])  # 这里是删除模块，对应的页面是/delstu
def delstu():
    if request.method == 'POST':
        name = request.form.get('name')
        print(name)
        if sql_select(name) == []:
            return '该生不存在'
        else:
            logic_del(name)  
            return render_template('delstu.html', result=name)# 如果找到了输入的学号执行删除操作，并重定向到首页
    return render_template('delstu.html')


@app.route('/addstu', methods=['GET', 'POST'])  # 这里是添加模块
def addstu():
    if request.method == 'POST':
        name = request.form.get('name')  # 单独入库
        grade = request.form.get('grade')
        phone = request.form.get('phone')
        address = request.form.get('address')
        fee = request.form.get('fee')  # 本次缴费 不入库
        ruxue_time = datetime.datetime.now()  # 登记时间 不入库
        daoqi_time = ruxue_time  # 到期时间
        all_fee = 0  # 所有缴费
        yueshu = int(request.form.get('yueshu'))  # 月数
        days = yueshu*30
        last = '无记录'
        benyue_fee = 0
        if fee != '':
            all_fee += int(fee)
            benyue_fee += int(fee)
            last = str(ruxue_time.strftime('%Y-%m-%d')) + "金额:" + fee  # 单独入库
            if days == 0:
                return "请输入学费对应的月数"
            else:
                daoqi_time = ruxue_time+datetime.timedelta(days=days)
                daoqi_time = str(daoqi_time.strftime('%Y-%m-%d'))
        if sql_select(name) != []:
            return "您输入的姓名已存在"
        else:
            keys = ['年纪', '电话', '地址','到期时间', '总缴费', '剩余学费', '剩余月数']
            values = [grade, phone, address, daoqi_time, all_fee, benyue_fee, yueshu]
            value = dict(zip(keys, values))
            value = json.dumps(value)
            state = '在学'
            sql_insert(name, value, last, state)
            return redirect(url_for('index'))
    return render_template('addstu.html')  # 添加成功则重定向到首页


@app.route('/altstu', methods=['GET', 'POST'])  # 缴费模块
def altstu():
    if request.method == 'POST':
        name = request.form.get('name') #姓名
        fee = int(request.form.get('fee')) #缴费金额
        now_fee = fee
        yueshu = int(request.form.get('yueshu')) #对应月数
        if sql_select(name) == []:
            return '该生信息不存在'
        else:
            if name and fee and yueshu:
                con, cur = connect_db()
                cur.execute('select * from STU where name=?', (name,))
                data = cur.fetchall()
                value = json.loads(data[0][2])
                all_fee = value.get('总缴费', None)
                all_fee += fee
                fee += value.get('剩余学费', 0)
                now_time = datetime.datetime.now()
                yueshu += value.get('剩余月数', 0)
                days = yueshu*30
                daoqi_time = now_time+datetime.timedelta(days=days)
                daoqi_time = str(daoqi_time.strftime('%Y-%m-%d'))
                value.update({
                    '剩余学费':int(fee), '剩余月数':yueshu, '总缴费':all_fee, '到期时间':daoqi_time
                })
                value = json.dumps(value)
                cur.execute("update STU set value=? where name=?",(value, name,))
                last = str(now_time.strftime('%Y-%m-%d')) + "金额:" + str(now_fee)  # 单独入库
                cur.execute("update STU set last=? where name=?",(last, name,))
                con.commit()
                close_db(con, cur)
                student = sql_select(name)

            return render_template('altstu.html', change=student)

    return render_template('altstu.html',student='')


@app.route('/searchstu', methods=['GET', 'POST'])
def searchstu():
    if request.method == 'POST':
        name = request.form.get('name')
        if sql_select(name) == []:
            return '没有您要找的学生'
        else:
            find = sql_select(name)
            # 如果找到了学号，把该学生信息传给html
            return render_template('searchstu.html', find=find)
    return render_template('searchstu.html', student='')

@app.route('/guoqistu', methods=['GET', 'POST'])
def guoqistu():
    student = find_guoqi()
    if student == None or student == []:
        student = ["lack of data"]
    print(student)
    return render_template('guoqistu.html', find=student)


if __name__ == '__main__':
    '''
    连库,建表
    grade text, tel text, address text, expiry text, all_fee int, \
                benyue_fee int, last_time text, 
    '''

    con, cur = connect_db()
    try:
        cur.execute(
            'CREATE TABLE STU (id integer primary key autoincrement, name text, value text, last text, state text)')
        con.commit()
    except Exception as e:
        pass
    con.close()
    app.run(host='0.0.0.0', port='80', debug=True)