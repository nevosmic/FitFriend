"""from datetime import date, timedelta, datetime
#import datetime
now = datetime.now() # current date and time

year = now.strftime("%Y")
print("year:", year)

month = now.strftime("%m")
print("month:", month)

day = now.strftime("%d")
print("day:", day)

time = now.strftime("%H:%M:%S")
print("time:", time)

date_time = now.strftime("%m/%d/%Y")
print("date and time:",date_time)
#print(len('4f10eca0-bbb4-11eb-9c8a-84fdd1c7d4ae'))

#today2 = datetime.date.today()
today2 = datetime.today()
now = datetime.now() # current date and time
print(now)
today = now.strftime("%Y-%m-%d")
print('today' , today)
day = now.strftime("%d")
print("day:", day)
curr_month = now.strftime("%m")
print("month:", curr_month)

days = {0: "SUN", 1: "MON", 2: "TUE",  3: "WED", 4: "THU", 5: "FRI", 6: "SAT"}
# SUN = 0 -> SUN = 7 MON = 1 TUE = 2 WED = 3 THU = 4 FRI = 5 SAT = 6
day_indx = (today2.weekday() + 1) % 7
#day = days[day_indx]
#print(day)
i = day_indx
start_of_week = int(day) - i
end_of_week = int(day) + (6 - i)
curr_week = (f'2021-{curr_month}-{start_of_week}', f'2021-{curr_month}-{end_of_week}')
print(curr_week)
#print('start_of_week ',days[start_of_week])
#print('end_of_week ', days[end_of_week])
events: [
    { % for event in events %}
{
    title: '{{event.title}}',
    start: '{{event.date}}',
    
},
{ % endfor %}
],
<a rel="stylesheet" href="https://cdn.jsdelivr.net/npm/fullcalendar@5.7.2/main.min.css"></a>
        <script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.7.2/main.min.js"> </script>

"""

'''@app.route('/total_workout_time/<uuid:user_id>', methods=['GET', 'POST'])
def create_total_workout_time_chart(user_id):
    cur = mysql.connection.cursor()
    user_name = fetch_name_by_id(user_id, cur)
    week = get_current_week()
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
'''
from datetime import datetime, timedelta

s = "2004-03-30"
date = datetime.strptime(s, "%Y-%m-%d")
modified = date + timedelta(days=1)
modified_date = datetime.strftime(modified, "%Y-%m-%d")


def get_week():
    tod = datetime.today()
    today_str = datetime.strftime(tod, "%Y-%m-%d")
    today = datetime.strptime(today_str, '%Y-%m-%d')
    days = {0: "SUN", 1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT"}
    # SUN = 0 -> SUN = 7 MON = 1 TUE = 2 WED = 3 THU = 4 FRI = 5 SAT = 6
    day_indx = (tod.weekday() + 1) % 7
    print(day_indx)
    i = day_indx
    start_of_week = today - timedelta(days=i)
    mod_start_week = datetime.strftime(start_of_week, "%Y-%m-%d")
    end_of_week = today + timedelta(days=6 - i)
    mod_end_week = datetime.strftime(end_of_week, "%Y-%m-%d")
    curr_week = (mod_start_week, mod_end_week)
    return curr_week


print(get_week())
days = {0: "SUN", 1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT"}

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

    for i in range (0,6):
        curr_day += timedelta(days=1)
        curr_day_mod = datetime.strftime(curr_day, "%Y-%m-%d")
        full_week_workout_time[curr_day_mod] = '0'
    print(full_week_workout_time)

#get_full_current_week()


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


#print(get_full_current_month())

print('80'+'%')