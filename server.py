from flask import Flask, render_template, request, session, redirect, url_for, jsonify
#  import interactionPlugin from '@fullcalendar/interaction'
import uuid
from datetime import date, timedelta, datetime
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import os

app = Flask(__name__)


# defined configuration
app.config['DEBUG'] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'my_proj' # name of data base
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'michal198767@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ['EMAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# connect to data base
mysql = MySQL(app)
# connect to manager-mail (me)
mail = Mail(app)


# funcs
def fetch_name_by_id(user_id, cur):
    cur.execute(f'SELECT user_name FROM my_proj.myusers WHERE user_id=%s', [user_id])
    user_name = cur.fetchone()
    return user_name


def get_current_month():
    now = datetime.now()  # current date and time
    curr_month = now.strftime("%m")
    month = f"_____{curr_month}%"
    return month


def reload_workouts(events, cur, user_id):
    cur.execute(f'SELECT workout_name,workout_date,start_hour FROM my_proj.workouts_schedule WHERE user_id=%s',
                [user_id])
    workouts = cur.fetchall()
    for workout in workouts:
        workout_name = workout[0]
        workout_start_hour = workout[2]
        title = f"{workout_name} {workout_start_hour}"
        date = workout[1]
        events.append({'title': title, 'date': date})


# TODO:def get_day_name()


def get_week_end():
    tod = datetime.today()
    today_str = datetime.strftime(tod, "%Y-%m-%d")
    today = datetime.strptime(today_str, '%Y-%m-%d')
    # SUN = 0 -> SUN = 7 MON = 1 TUE = 2 WED = 3 THU = 4 FRI = 5 SAT = 6
    day_indx = (tod.weekday() + 1) % 7
    i = day_indx
    end_of_week = today + timedelta(days=6 - i)
    return end_of_week


def get_week_start():
    tod = datetime.today()
    today_str = datetime.strftime(tod, "%Y-%m-%d")
    today = datetime.strptime(today_str, '%Y-%m-%d')
    # SUN = 0 -> SUN = 7 MON = 1 TUE = 2 WED = 3 THU = 4 FRI = 5 SAT = 6
    day_indx = (tod.weekday() + 1) % 7
    i = day_indx
    start_of_week = today - timedelta(days=i)
    return start_of_week


def get_current_week():
    start_of_week = get_week_start()
    mod_start_week = datetime.strftime(start_of_week, "%Y-%m-%d")
    end_of_week = get_week_end()
    mod_end_week = datetime.strftime(end_of_week, "%Y-%m-%d")
    curr_week = (mod_start_week, mod_end_week)
    return curr_week


def get_full_current_week():
    start_of_week = get_week_start()
    curr_day = start_of_week
    curr_day_mod = datetime.strftime(curr_day, "%Y-%m-%d")
    full_week_workout_time = {}
    full_week_workout_time[curr_day_mod] = '0'
    for i in range(0, 6):
        curr_day += timedelta(days=1)
        curr_day_mod = datetime.strftime(curr_day, "%Y-%m-%d")
        full_week_workout_time[curr_day_mod] = '0'
    return full_week_workout_time


def get_full_current_month():
    now = datetime.now()  # current date and time
    year = now.strftime("%Y")
    month = now.strftime("%m")
    first_day = f'{year}-{month}-01'
    curr_day_of_month = datetime.strptime(first_day, '%Y-%m-%d')
    full_month_workout_time = {}
    full_month_workout_time[first_day] = '0'
    for i in range(0, 30):
        curr_day_of_month += timedelta(days=1)
        curr_day_of_month_mod = datetime.strftime(curr_day_of_month, "%Y-%m-%d")
        full_month_workout_time[curr_day_of_month_mod] = '0'
    return full_month_workout_time


def calculate_percentages(pie_data):
    values = []
    total_num_of_workouts = sum(pie_data.values())
    for workout_type in pie_data.keys():
        workout_type_ratio = (pie_data[workout_type]) / total_num_of_workouts
        workout_type_percent = workout_type_ratio * 100
        values.append(workout_type_percent)
    return values


def create_motivation_chart_data(my_data_results):
    chart_data = []
    for item in my_data_results:
        workout_date = item[0]
        motiv = item[1]
        chart_data.append((workout_date, motiv))
    chart_data_sorted = sorted(chart_data)
    return chart_data_sorted


# def creat_total_time_chart_data(my_data_res):


def send_welcome_mail(user_name, user_email):
    msg = Message('FitFriend', sender='michal198767@gmail.com', recipients=[user_email])
    msg.body = f"Hey {user_name}!\nWelcome to Fitfriend"
    mail.send(msg)
    return "Welcome message sent!"


@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == "POST":
        details = request.form
        user_name = details['fname']
        email = details['email']
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT * FROM my_proj.myusers WHERE user_name=%s', [user_name])
        name_results = cur.fetchall()
        if not name_results:
            user_id = str(uuid.uuid1())
            user_email = email
            cur.execute("INSERT INTO my_proj.myusers (user_id,user_name,user_email) VALUES (%s,%s,%s)",
                        (user_id, user_name, user_email))
        else:
            cur.execute(f'SELECT user_id,user_email FROM my_proj.myusers WHERE user_name=%s', [user_name])
            fetch = cur.fetchall()
            user_id = fetch[0][0]
            user_email = fetch[0][1]

        mysql.connection.commit()
        cur.close()
        print(send_welcome_mail(user_name, user_email))
        return redirect(url_for('main_page', user_id=user_id))

    return render_template('welcome.html')


@app.route('/main_page/<uuid:user_id>', methods=['GET', 'POST'])
def main_page(user_id):
    if "btn_schedule" in request.form:
        if request.method == "POST":
            return redirect(url_for('my_schedule', user_id=user_id))
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    mysql.connection.commit()
    cur.close()
    return render_template('main_page.html', value=user_name[0], user_id=user_id)


@app.route('/my_schedule/<uuid:user_id>', methods=['GET', 'POST'])
def my_schedule(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    # reset events for this client
    events = []
    reload_workouts(events, cur, user_id)
    mysql.connection.commit()
    cur.close()
    return render_template('my_schedule.html', value=user_name[0], value_id=user_id, events=events)


@app.route('/insert workouts to DB', methods=['GET', 'POST'])
def insert_workouts_to_db():
    if request.method == 'POST':
        content = request.json
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO 
                my_proj.workouts_schedule (
                    user_id,
                    workout_name,
                    workout_type,
                    workout_date,
                    start_hour,
                    duration)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (content['_id'], content['workout_name'], content['workout_type'], content['workout_date'], content['start_hour'], content['duration']))
        mysql.connection.commit()
        cur.close()
        return 'in DB'


@app.route('/insert reports to DB', methods=['GET', 'POST'])
def insert_reports_to_db():
    if request.method == 'POST':
        content = request.json
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO 
                my_proj.reports (
                    user_id,
                    workout_date,
                    personal_difficulty,
                    workout_completion,
                    motivation)
            VALUES (%s,%s,%s,%s,%s)""",
            (content['_id'], content['workout_date'], content['personal_difficulty'], content['workout_completion'], content['motivation']))
        mysql.connection.commit()
        cur.close()
        return "1"


@app.route('/check if reported', methods=['GET', 'POST'])
def check_if_workout_has_been_reported():
    if request.method == 'POST':
        content = request.json
        cur = mysql.connection.cursor()
        cur.execute(
            """SELECT EXISTS(SELECT * FROM my_proj.reports 
               WHERE user_id=%s AND workout_date=%s)  
                """,
            (content['_id'], content['workout_date']))
        results = cur.fetchall()
        reported = 0
        # check if the bit is on -this workout has been reported already
        if results[0][0] == 1:
            reported = 1
        mysql.connection.commit()
        cur.close()
        return str(reported)


@app.route('/motivation/<uuid:user_id>', methods=['GET', 'POST'])
def create_motivation_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    week = get_current_week()
    cur.execute(f'SELECT workout_date,motivation FROM my_proj.reports WHERE workout_date BETWEEN %s AND %s AND user_id=%s', (week[0], week[1], user_id))
    my_data_res = cur.fetchall()
    chart_data = create_motivation_chart_data(my_data_res)
    mysql.connection.commit()
    cur.close()
    labels = [row[0] for row in chart_data]
    values = [row[1] for row in chart_data]
    return render_template('motivation.html', labels=labels, values=values, value_id=user_id, value=user_name[0])


@app.route('/motivation-month/<uuid:user_id>', methods=['GET', 'POST'])
def create_motivation_month_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    month = get_current_month()
    # Finds any values that have "07" in the fifth' position
    cur.execute(f'SELECT workout_date,motivation FROM my_proj.reports WHERE workout_date LIKE %s AND user_id=%s'
                , (month, user_id))
    my_data_results = cur.fetchall()
    chart_data = create_motivation_chart_data(my_data_results)
    mysql.connection.commit()
    cur.close()
    labels = [row[0] for row in chart_data]
    values = [row[1] for row in chart_data]
    return render_template('motivation.html', labels=labels, values=values, value_id=user_id, value=user_name[0])


@app.route('/total_workout_time/<uuid:user_id>', methods=['GET', 'POST'])
def create_total_workout_time_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    week = get_current_week()
    cur.execute(f'SELECT workout_date,duration FROM my_proj.workouts_schedule WHERE workout_date BETWEEN %s AND %s'
                f' AND user_id=%s', (week[0], week[1], user_id))
    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    full_week = get_full_current_week()
    chart_data = []
    total_workout_time = 0
    for item in my_data_results:
        workout_date = item[0]
        workout_duration = item[1]
        full_week[workout_date] = workout_duration
        total_workout_time += int(workout_duration)

    for workout_date in full_week.keys():
        chart_data.append((workout_date, full_week[workout_date]))

    labels = [row[0] for row in chart_data]
    print(labels)
    values = [row[1] for row in chart_data]
    print(values)

    notice = "Your total workout time this week : {} minutes".format(total_workout_time)
    return render_template('total_workout_time.html', labels=labels, values=values, value_id=user_id, value=user_name[0], notice=notice)


@app.route('/total_workout_time-month/<uuid:user_id>', methods=['GET', 'POST'])
def create_total_month_workout_time_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    month = get_current_month()
    # Finds any values that have "07" in the fifth' position
    cur.execute(f'SELECT workout_date,duration FROM my_proj.workouts_schedule WHERE workout_date LIKE %s AND'
                f' user_id=%s',(month, user_id))
    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    full_month = get_full_current_month()
    chart_data = []
    total_workout_time = 0
    for item in my_data_results:
        workout_date = item[0]
        workout_duration = item[1]
        full_month[workout_date] = workout_duration
        total_workout_time += int(workout_duration)

    for workout_date in full_month.keys():
        chart_data.append((workout_date, full_month[workout_date]))

    labels = [row[0] for row in chart_data]
    values = [row[1] for row in chart_data]

    notice = "Your total workout time this month : {} minutes".format(total_workout_time)
    return render_template('total_workout_time.html', labels=labels, values=values, value_id=user_id, value=user_name[0], notice=notice)


@app.route('/workout_types/<uuid:user_id>', methods=['GET', 'POST'])
def create_types_pie(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    week = get_current_week()
    cur.execute(f'SELECT workout_date,workout_type FROM my_proj.workouts_schedule WHERE workout_date BETWEEN %s AND %s'
                f' AND user_id=%s', (week[0], week[1], user_id))
    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    pie_data = {}
    labels = []
    for item in my_data_results:
        workout_type = item[1]
        if workout_type in pie_data:
            pie_data[workout_type] += 1
        else:
            pie_data[workout_type] = 1
            labels.append(workout_type)

    values = calculate_percentages(pie_data)

    return render_template('workout_Types.html', labels=labels, values=values, value_id=user_id, value=user_name[0])


@app.route('/workout_types-month/<uuid:user_id>', methods=['GET', 'POST'])
def create_month_types_pie(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    month = get_current_month()
    # Finds any values that have "07" in the fifth' position
    cur.execute(
        f'SELECT workout_date,workout_type FROM my_proj.workouts_schedule WHERE workout_date LIKE %s AND user_id=%s',
        (month, user_id))
    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    pie_data = {}
    labels = []
    for item in my_data_results:
        workout_type = item[1]
        if workout_type in pie_data:
            pie_data[workout_type] += 1
        else:
            pie_data[workout_type] = 1
            labels.append(workout_type)
    values = calculate_percentages(pie_data)
    return render_template('workout_Types.html', labels=labels, values=values, value_id=user_id, value=user_name[0])


@app.route('/workout_completion/<uuid:user_id>', methods=['GET', 'POST'])
def create_completion_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    week = get_current_week()
    cur.execute(f'SELECT my_proj.workouts_schedule.user_id,'
                f'workouts_schedule.workout_date,my_proj.workouts_schedule.workout_name,'
                f'my_proj.reports.workout_completion FROM my_proj.workouts_schedule LEFT JOIN my_proj.reports'
                f' ON my_proj.workouts_schedule.user_id=my_proj.reports.user_id AND '
                f'my_proj.workouts_schedule.workout_date=my_proj.reports.workout_date WHERE my_proj.reports.workout_date '
                f'BETWEEN %s AND %s AND my_proj.reports.user_id=%s', (week[0], week[1], user_id))

    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    labels = []
    values = []
    labels.append(" ")
    values.append("0")
    for item in my_data_results:
        workout_name = item[2]
        workout_comp = item[3]
        labels.append(workout_name)
        values.append(workout_comp)

    return render_template('completion.html', value_id=user_id, value=user_name[0], labels=labels, values=values)


@app.route('/workout_completion-month/<uuid:user_id>', methods=['GET', 'POST'])
def create_completion_month_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    month = get_current_month()
    # Finds any values that have "07" in the fifth' position
    cur.execute(f'SELECT my_proj.workouts_schedule.user_id,'
                f'workouts_schedule.workout_date,my_proj.workouts_schedule.workout_name,'
                f'my_proj.reports.workout_completion FROM my_proj.workouts_schedule LEFT JOIN my_proj.reports'
                f' ON my_proj.workouts_schedule.user_id=my_proj.reports.user_id AND '
                f'my_proj.workouts_schedule.workout_date=my_proj.reports.workout_date '
                f'WHERE my_proj.reports.workout_date LIKE %s AND my_proj.reports.user_id=%s', (month, user_id))

    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    labels = []
    values = []
    labels.append(" ")
    values.append("0")
    for item in my_data_results:
        workout_name = item[2]
        workout_comp = item[3]
        labels.append(workout_name)
        values.append(workout_comp)

    return render_template('completion.html', value_id=user_id, value=user_name[0], labels=labels, values=values)


@app.route('/personal_diff/<uuid:user_id>', methods=['GET', 'POST'])
def create_personal_diff_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    week = get_current_week()
    # Finds any values that have "07" in the fifth' position
    cur.execute(f'SELECT my_proj.workouts_schedule.user_id,my_proj.workouts_schedule.workout_type,'
                f'workouts_schedule.workout_date,my_proj.workouts_schedule.workout_name,'
                f'my_proj.reports.personal_difficulty FROM my_proj.workouts_schedule LEFT JOIN my_proj.reports ON '
                f'my_proj.workouts_schedule.user_id=my_proj.reports.user_id AND '
                f'my_proj.workouts_schedule.workout_date=my_proj.reports.workout_date WHERE my_proj.reports.workout_date '
                f'BETWEEN %s AND %s AND my_proj.reports.user_id=%s', (week[0], week[1], user_id))

    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    labels = []
    values = []
    labels.append(" ")
    values.append("0")
    diff_over_VERY_TOUGH = set()
    for item in my_data_results:
        workout_type = item[1]
        workout_name = item[3]
        workout_diff = item[4]
        if int(workout_diff) > 5:
            diff_over_VERY_TOUGH.add(workout_type)
        labels.append(workout_name)
        values.append(workout_diff)

    if len(diff_over_VERY_TOUGH)>1:
        notice = "{} are challenging for you this week ".format(diff_over_VERY_TOUGH)
    else:
        notice = "{} is challenging for you this week ".format(diff_over_VERY_TOUGH)

    return render_template('personal_diff.html', value_id=user_id, value=user_name[0], labels=labels, values=values, notice=notice)


@app.route('/personal_diff-month/<uuid:user_id>', methods=['GET', 'POST'])
def create_month_personal_diff_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    month = get_current_month()
    # Finds any values that have "07" in the fifth' position
    cur.execute(f'SELECT my_proj.workouts_schedule.user_id,my_proj.workouts_schedule.workout_type,'
                f'workouts_schedule.workout_date,my_proj.workouts_schedule.workout_name,'
                f'my_proj.reports.personal_difficulty FROM my_proj.workouts_schedule LEFT JOIN my_proj.reports ON '
                f'my_proj.workouts_schedule.user_id=my_proj.reports.user_id AND '
                f'my_proj.workouts_schedule.workout_date=my_proj.reports.workout_date WHERE my_proj.reports.workout_date'
                f' LIKE %s AND my_proj.reports.user_id=%s', (month, user_id))

    my_data_results = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    labels = []
    values = []
    labels.append(" ")
    values.append("0")
    diff_over_VERY_TOUGH = set()
    for item in my_data_results:
        workout_type = item[1]
        workout_name = item[3]
        workout_diff = item[4]
        if int(workout_diff) > 5:
            diff_over_VERY_TOUGH.add(workout_type)
        labels.append(workout_name)
        values.append(workout_diff)

    if len(diff_over_VERY_TOUGH) > 1:
        notice = "{} are challenging for you this month ".format(diff_over_VERY_TOUGH)
    else:
        notice = "{} is challenging for you this month ".format(diff_over_VERY_TOUGH)

    return render_template('personal_diff.html', value_id=user_id, value=user_name[0], labels=labels, values=values,
                           notice=notice)


if __name__ == '__main__':
    app.run()

