from flask import Flask, render_template, request, session, redirect, url_for, jsonify
#  import interactionPlugin from '@fullcalendar/interaction'
import uuid
from datetime import date, timedelta, datetime
from flask_mysqldb import MySQL
app = Flask(__name__)


# connect to data base
app.config['DEBUG'] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'my_proj' # name of data base
mysql = MySQL(app)


# funcs
def fetch_name_by_id(user_id, cur):
    cur.execute(f'SELECT user_name FROM my_proj.myusers WHERE user_id=%s', [user_id])
    user_name = cur.fetchone()
    return user_name


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


def current_week():
    today = datetime.today()
    now = datetime.now()  # current date and time
    day = now.strftime("%d")
    curr_month = now.strftime("%m")
    #days = {"SUN": 0, "MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6}
    days = {0: "SUN", 1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT"}
    # SUN = 0 -> SUN = 7 MON = 1 TUE = 2 WED = 3 THU = 4 FRI = 5 SAT = 6
    day_indx = (today.weekday() + 1) % 7
    i = day_indx
    start_of_week = int(day) - i
    end_of_week = int(day) + (6 - i)
    curr_week = (f'2021-{curr_month}-{start_of_week}', f'2021-{curr_month}-{end_of_week}')
    return curr_week




def calculate_percentages(pie_data):
    values = []
    total_num_of_workouts = sum(pie_data.values())
    for workout_type in pie_data.keys():
        workout_type_ratio = (pie_data[workout_type]) / total_num_of_workouts
        workout_type_percent = workout_type_ratio * 100
        values.append(workout_type_percent)
    return values


def create_chart_data(my_data_results):
    chart_data = []
    for item in my_data_results:
        workout_date = item[0]
        motiv = item[1]
        chart_data.append((workout_date, motiv))

    chart_data_sorted = sorted(chart_data)
    return chart_data_sorted


@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == "POST":
        details = request.form
        username = details['fname']
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT * FROM my_proj.myusers WHERE user_name=%s', [username])
        name_results = cur.fetchall()
        if not name_results:
            user_id = str(uuid.uuid1())
            cur.execute("INSERT INTO my_proj.myusers (user_id,user_name) VALUES (%s,%s)", (user_id, username))
        else:
            cur.execute(f'SELECT user_id FROM my_proj.myusers WHERE user_name=%s', [username])
            user_id = cur.fetchone()
        mysql.connection.commit()
        cur.close()
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
    week = current_week()
    cur.execute(f'SELECT workout_date,motivation FROM my_proj.reports WHERE workout_date BETWEEN %s AND %s AND user_id=%s', (week[0], week[1], user_id))
    my_data_res = cur.fetchall()
    chart_data = create_chart_data(my_data_res)
    mysql.connection.commit()
    cur.close()
    labels = [row[0] for row in chart_data]
    values = [row[1] for row in chart_data]
    return render_template('motivation.html', labels=labels, values=values, value_id=user_id, value=user_name[0])


@app.route('/motivation-month/<uuid:user_id>', methods=['GET', 'POST'])
def create_motivation_month_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    now = datetime.now()  # current date and time
    today = date_time = now.strftime("%Y-%m-%d")
    day = now.strftime("%d")
    curr_month = now.strftime("%m")
    month = '_____{current_month}%'
    # Finds any values that have "07" in the fifth' position
    cur.execute(f'SELECT workout_date,motivation FROM my_proj.reports WHERE workout_date LIKE %s AND user_id=%s', (month, user_id))
    my_data_results = cur.fetchall()
    chart_data = create_chart_data(my_data_results)
    mysql.connection.commit()
    cur.close()
    labels = [row[0] for row in chart_data]
    values = [row[1] for row in chart_data]
    return render_template('motivation.html', labels=labels, values=values, value_id=user_id, value=user_name[0])


@app.route('/total_workout_time/<uuid:user_id>', methods=['GET', 'POST'])
def create_total_workout_time_chart(user_id):
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT user_name FROM my_proj.myusers WHERE user_id=%s', [user_id])
    user_name = cur.fetchone()
    # need to handle days..
    today = date.today()
    end_of_week = today + timedelta(6)
    print("today ", today)
    print("end_of_week ", end_of_week)
    week = ('2021-07-04', '2021-07-10')
    cur.execute(f'SELECT workout_date,duration FROM my_proj.workouts_schedule WHERE workout_date BETWEEN %s AND %s AND user_id=%s', (week[0], week[1], user_id))
    my_data_results = cur.fetchall()
    print("my_data_results: ", my_data_results)
    chart_data = []
    total_workout_time = 0
    for item in my_data_results:
        #  workout_date = item[0]
        workout_duration = item[1]
        total_workout_time += int(workout_duration)
    mysql.connection.commit()
    cur.close()
    labels1 = [row[0] for row in my_data_results]
    minutes_per_workout = [row[1] for row in my_data_results]
    day_hours_in_minutes = 12 * 60
    values1 = []
    for workout_minutes in minutes_per_workout:
        workout_time_ratio = str(int(workout_minutes)/day_hours_in_minutes)
        values1.append(workout_time_ratio)

    notice = "Your total workout time this week : {} minutes".format(total_workout_time)
    total_workout_hours = total_workout_time/60
    rest_of_week = (7*12) - total_workout_hours
    return render_template('total_workout_time.html', labels1=labels1, values1=values1, value_id=user_id, value=user_name[0], notice=notice, total_workout_hours=total_workout_hours, rest_of_week_hours=rest_of_week)


@app.route('/workout_types/<uuid:user_id>', methods=['GET', 'POST'])
def create_types_pie(user_id):
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT user_name FROM my_proj.myusers WHERE user_id=%s', [user_id])
    user_name = cur.fetchone()
    today = date.today()
    end_of_week = today + timedelta(6)
    print("today ",today)
    print("end_of_week ", end_of_week)
    week = ('2021-07-04', '2021-07-10')
    cur.execute(f'SELECT workout_date,workout_type FROM my_proj.workouts_schedule WHERE workout_date BETWEEN %s AND %s AND user_id=%s', (week[0], week[1], user_id))
    my_data_results = cur.fetchall()
    print("my_data_results: ", my_data_results)
    pie_data = {}
    labels = []
    for item in my_data_results:
        workout_type = item[1]
        if workout_type in pie_data:
            pie_data[workout_type] += 1
        else:
            pie_data[workout_type] = 1
            labels.append(workout_type)

    print("pie_data: ", pie_data)
    mysql.connection.commit()
    cur.close()
    values = calculate_percentages(pie_data)

    return render_template('workout_Types.html', labels=labels, values=values, value_id=user_id, value=user_name[0])


if __name__ == '__main__':
    app.run()

