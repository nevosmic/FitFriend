from datetime import date, timedelta, datetime
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
"""events: [
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