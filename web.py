from flask import Flask, request, url_for, render_template, redirect, abort, flash, session
from dataHandle import sql_insert, sql_select, connect_db, close_db, show_data, real_del, statistic, find_expiry, pass_month
import json
import sqlite3
import datetime
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'shangmei' or \
                request.form['password'] != '127101':
            error = '用户名/密码错误'
        else:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
    
@app.route('/')
def index():
    """
    主页 显示统计学生信息
    """
    if 'username' in session:
        student = show_data()
        if student == None or student == []:
            student = ["缺少学生数据"]
        amount, total_income, instant_income = statistic()
        return render_template('index.html', student=student, amount=amount, total_income=total_income, instant_income=instant_income)
    else:
        return redirect(url_for('login'))


@app.route('/delstu', methods=['GET', 'POST'])
def delstu():
    """
    删除模块(物理删除)
    """
    if request.method == 'POST':
        name = request.form.get('name')
        if sql_select(name) == []: #如果无该生信息
            return '该生不存在'
        else:
            real_del(name)   #物理删除该省信息
            return render_template('delstu.html', rm_name=name)
    return render_template('delstu.html')


@app.route('/addstu', methods=['GET', 'POST'])
def addstu():
    """
    添加模块(姓名;学费信息[年纪、电话、地址、到期时间、总缴费、剩余学费、剩余月数];上次缴费时间;状态)
    """
    if request.method == 'POST':
        name = request.form.get('name')  # 单独入库
        grade = request.form.get('grade') #value 入库
        phone = request.form.get('phone') #value 入库
        address = request.form.get('address') #value 入库
        fee = request.form.get('fee')  # 本次缴费 以last单独入库
        ruxue_time = datetime.datetime.now()  # 登记时间 不入库
        daoqi_time = ruxue_time  # 到期时间 #value 入库
        all_fee = 0  # 总缴费 #value 入库
        yueshu = int(request.form.get('yueshu'))  # 剩余月数 value 入库
        days = yueshu*30
        last = '无记录' # 单独入库
        left_fee = 0 #剩余学费 value入库
        if fee != '':
            all_fee += int(fee)
            left_fee += int(fee)
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
            values = [grade, phone, address, daoqi_time, all_fee, left_fee, yueshu]
            value = dict(zip(keys, values))
            value = json.dumps(value)
            state = '在学'
            sql_insert(name, value, last, state)
            return redirect(url_for('index')) # 添加成功则重定向到首页
    return render_template('addstu.html')


@app.route('/altstu', methods=['GET', 'POST'])
def altstu():
    """
    缴费模块
    """
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
    """
    查找信息模块
    """
    if request.method == 'POST':
        name = request.form.get('name')
        if sql_select(name) == []:
            return '没有您要找的学生'
        else:
            find = sql_select(name)
            return render_template('searchstu.html', find=find)
    return render_template('searchstu.html', student='')

@app.route('/guoqistu', methods=['GET', 'POST'])
def guoqistu():
    """
    查找到期的学生
    """
    student = find_expiry()
    if student == None or student == []:
        student = ["lack of data"]
    print(student)
    return render_template('guoqistu.html', find=student)

@app.route('/update', methods=['GET', 'POST'])
def update():
    """
    更新一个月的数据
    """
    if request.method == 'POST':
        passwd = request.form.get('passwd')
        if passwd == '127101':
            pass_month()
            result = 'success'
            return render_template('update.html', result=result)
    return render_template('update.html', result='')

"""
@app.route('/notfound', methods=['GET', 'POST'])
def notfound():
    return render_template('index.html'), 404
"""


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
    app.run(host='0.0.0.0', port='8088', debug=True)