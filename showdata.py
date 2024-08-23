from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from config import get_connection
from flask_paginate import Pagination, get_page_args
import time,socket

showdata = Blueprint('showdata',__name__)

@showdata.route("/loginpage")
def Loginpage():
    if "user_sess" not in session:
        return render_template("login.html",headername="เข้าใช้งานระบบ")
    else:
        return redirect(url_for('showdata.Showtkadmin'))
@showdata.route("/checklogin",methods=["POST"])
def Checklogin():
    user = request.form['username']
    passw = request.form['password']
    con = get_connection()

    with con.cursor() as cur:

        sql = "SELECT * FROM user_adm WHERE user_adm =%s AND pass_adm=%s"
        cur.execute(sql,(user,passw))
        rows = cur.fetchall()

        timestamp = time.time()
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        print("พบข้อมูล login="+str(len(rows))+" เวลา : "+str(formatted_time)+" IpAddress : "+str(ip_address))

        statuss = str(len(rows))
        times = str(formatted_time)
        ipss = str(ip_address)

        sql = "INSERT INTO logs_login (user, pass, time, ipaddress, status) VALUES (%s,%s,%s,%s,%s)"
        cur.execute(sql, (user, passw, times, ipss, statuss,))
        con.commit()

        if len(rows) > 0:
            session['user_sess'] = user
            session.permanent = True
            print("ผู้ใช้งานได้เข้าสู่ระบบโดยชื่อ Username: " + session['user_sess'])
            return redirect(url_for('showdata.Showtkadmin'))
        else:
            flash("ไม่พบข้อมูลในระบบ โปรดตรวจสอบหรือลองอีกครั้ง")
            return render_template('login.html',headername="เข้าใช้งานระบบ")

@showdata.route("/logout")
def Logout():
    session.clear()
    return redirect(url_for('showdata.Loginpage'))

@showdata.route("/ver")
def Ver():
    return render_template('ver.html',headername="Patch Notes")

@showdata.route("/")
def Showtk():
    con = get_connection()
    with con.cursor() as cur:

        cur.execute('select count(*) from message_line')
        total = cur.fetchone()[0]

        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')

        per_page = 25

        sql = "SELECT Text, DATE_FORMAT(FROM_UNIXTIME(dateline / 1000), '%d/%m/%Y %H:%i:%s') AS datetime_mill, note,note2, ID_Pre FROM message_line ORDER BY ID_Pre DESC LIMIT {} OFFSET {}" \
        .format(per_page, offset)
        cur.execute(sql)
        data = cur.fetchall()

        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total,
                                css_framework='bootstrap4')

        return render_template('index.html', datas=data,page=page,
                           per_page=per_page,
                           pagination=pagination,total2 = total, vername="0.10")

@showdata.route("/showtkadmin")
def Showtkadmin():
    con = get_connection()
    if "user_sess" not in session:
        return render_template('login.html',headername="Login เข้าใช้งาน")
    with con.cursor() as cur:
        sql = "SELECT Text,datetimes,note,note2,ID_Pre FROM message_line ORDER BY ID_Pre DESC"
        cur.execute(sql)
        data = cur.fetchall()
        return render_template('showtk_adm.html', datas=data)

@showdata.route("/showtkadmin",methods=["POST"])
def Showadmsearch():
    con = get_connection()
    if request.method == "POST":
        if 'ssearch' in request.form:
            searchs = request.form['ssearch']

            with con.cursor() as cur:
                sql = "SELECT Text,datetimes,note,note2 FROM message_line WHERE Text LIKE %s"
                cur.execute(sql,('%'+searchs+'%'))
                data = cur.fetchall()

                return render_template("showtk_adm.html",datas=data)
        else:
            dstart = request.form['dtstart']
            dend = request.form['dtend']

            with con.cursor() as cur:
                sql = "SELECT Text,datetimes,note,note2 FROM message_line WHERE datetimes between %s and %s"
                cur.execute(sql, (dstart, dend))
                data = cur.fetchall()

                return render_template("showtk_adm.html", datas=data)
    return render_template("showtk_adm.html")

@showdata.route("/showsearch",methods=["POST"])
def Showsearch():
    con = get_connection()
    if request.method == "POST":
        if 'ssearch' in request.form:
            searchs = request.form['ssearch']
            sworks = request.form['works']
            with con.cursor() as cur:

                sql_count = "select count(*) from message_line WHERE Text LIKE %s AND Text LIKE %s"
                cur.execute(sql_count,('%'+searchs+'%','%'+sworks+'%'))

                total = cur.fetchone()[0]

                page, per_page, offset = get_page_args(page_parameter='page',
                                                       per_page_parameter='per_page')

                per_page = 250

                sql_select = "SELECT Text,DATE_FORMAT(FROM_UNIXTIME(dateline / 1000), '%%d/%%m/%%Y %%H:%%i:%%s') AS datetime_mill,note,note2,ID_Pre FROM message_line WHERE Text LIKE %s AND Text LIKE %s ORDER BY ID_Pre DESC LIMIT {} OFFSET {}" \
        .format(per_page, offset)
                cur.execute(sql_select,('%'+searchs+'%','%'+sworks+'%'))
                data = cur.fetchall()
                print("ค้นหาข้อมูล(ข้อความ) : ",searchs)
                print("ค้นหางวดงาน : ",sworks)
                pagination = Pagination(page=page,
                                        per_page=per_page,
                                        total=total,
                                        css_framework='bootstrap4')

                return render_template("index.html",datas=data,total2 = total,pagination=pagination)
        elif 'dtstart' in request.form and 'dtend' in request.form:
            dstart = request.form['dtstart']
            dend = request.form['dtend']

            with con.cursor() as cur:

                sql2 = "select count(*) from message_line WHERE datetimes between %s AND DATE_ADD(%s, INTERVAL 1 DAY)"
                cur.execute(sql2, (dstart, dend))

                total = cur.fetchone()[0]

                page, per_page, offset = get_page_args(page_parameter='page',
                                                       per_page_parameter='per_page')

                per_page = 250

                sql = "SELECT Text,DATE_FORMAT(FROM_UNIXTIME(dateline / 1000), '%%d/%%m/%%Y %%H:%%i:%%s') AS datetime_mill,note,note2,ID_Pre FROM message_line WHERE datetimes BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 DAY) ORDER BY ID_Pre DESC LIMIT {} OFFSET {}" \
        .format(per_page, offset)
                cur.execute(sql, (dstart, dend))
                data = cur.fetchall()
                print("ค้นหาวันที่ (เริ่ม) : ", dstart)
                print("ค้นหาวันที่ (สุดท้าย) : ", dend)
                pagination = Pagination(page=page,
                                        per_page=per_page,
                                        total=total,
                                        css_framework='bootstrap4')
                return render_template("index.html", datas=data,total2 = total,pagination=pagination)
        else :
            nonulls = request.form['snonulls']

            with con.cursor() as cur:

                sql_count = "select count(*) from message_line WHERE note !=%s"
                cur.execute(sql_count,nonulls)

                total = cur.fetchone()[0]

                page, per_page, offset = get_page_args(page_parameter='page',
                                                       per_page_parameter='per_page')

                per_page = 250

                sql_select = "SELECT Text,DATE_FORMAT(FROM_UNIXTIME(dateline / 1000), '%%d/%%m/%%Y %%H:%%i:%%s') AS datetime_mill,note,note2,ID_Pre FROM message_line WHERE note !=%s ORDER BY ID_Pre DESC LIMIT {} OFFSET {}" \
                    .format(per_page, offset)
                cur.execute(sql_select,nonulls)
                data = cur.fetchall()
                pagination = Pagination(page=page,
                                        per_page=per_page,
                                        total=total,
                                        css_framework='bootstrap4')

                return render_template("index.html", datas=data, total2=total, pagination=pagination)

    return render_template("index.html")

@showdata.route("/editdata", methods=["POST"])
def Editdata():
    con = get_connection()
    if request.method == 'POST':
        # Get form data
        id_pres = request.form.get("id_pres")

        print (f"ไอดีที่ได้รับ: {id_pres}")

        notes = request.form.get("notes")
        notes2 = request.form.get("notes2")

        # Update database
        with con.cursor() as cur:
            sql = "UPDATE message_line SET note=%s ,note2=%s WHERE ID_Pre=%s"
            
            cur.execute(sql, (notes,notes2, id_pres))

            

            rows_affected = cur.rowcount
            if rows_affected > 0:
                print(f"Rows affected: {rows_affected}")
            else:
                print("No rows affected (consider checking WHERE clause)")


            con.commit()

            return redirect(url_for('showdata.Showtkadmin'))
