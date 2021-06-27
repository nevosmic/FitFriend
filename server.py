from flask import Flask, render_template, request, session, redirect, url_for
#  import interactionPlugin from '@fullcalendar/interaction'
import uuid
from flask_mysqldb import MySQL
app = Flask(__name__)

events = [
    {
        'title':"Yoga 9:00",
        'date':"2021-06-08"
    },
]

# connect to data base
app.config['DEBUG'] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'my_proj' # name of data base
mysql = MySQL(app)


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
    if "btn" in request.form:
        if request.method == "POST":
            return redirect(url_for('weekly_schedule', user_id=user_id))
    print("user_id ", user_id)
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT user_name FROM my_proj.myusers WHERE user_id=%s', [user_id])
    my_results = cur.fetchone()
    print("my results: ", my_results[0])
    mysql.connection.commit()
    cur.close()
    print('request.form', request.form)

    return render_template('main_page.html', value=my_results[0])


@app.route('/weekly_schedule/<uuid:user_id>', methods=['GET', 'POST'])
def weekly_schedule(user_id):
    #if "btn" in request.form:
       # if request.method == "POST":
        #    return redirect(url_for('weekly_schedule', user_id=user_id))
    print("user_id2 ", user_id)
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT user_name FROM my_proj.myusers WHERE user_id=%s', [user_id])
    my_results2 = cur.fetchone()
    events = []
    cur.execute(f'SELECT workout_name,workout_date,start_hour FROM my_proj.weekly_schedule WHERE user_id=%s', [user_id])
    workouts = cur.fetchall()
    for workout in workouts:
        workout_name = workout[0]
        workout_start_hour = workout[2]
        title = workout_name+" "+workout_start_hour
        date = workout[1]
        events.append({'title': title, 'date': date})

        print("workouts: ", workouts)
        print(events)

    mysql.connection.commit()
    cur.close()
    return render_template('weekly_schedule.html', value=my_results2[0], value_id=user_id, events=events)

@app.route('/insert_to_DB', methods=['GET', 'POST'])
def insert_to_db():
    if request.method == 'POST':
        content = request.json
        print("content: ", content)
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO 
                my_proj.weekly_schedule (
                    user_id,
                    workout_name,
                    type,
                    workout_date,
                    start_hour,
                    duration)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (content['_id'], content['workout_name'], content['workout_type'], content['workout_date'], content['start_hour'], content['duration']))
        mysql.connection.commit()
        cur.close()
        return 'in DB'

if __name__ == '__main__':
    app.run()

