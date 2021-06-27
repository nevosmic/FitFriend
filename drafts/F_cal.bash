<!doctype html>

<html>
<html lang='en'>
    <head>
        <title>Weekly Schedule</title>
        <meta charset='utf-8' />
        <link href="../myFullcalendar/lib/main.min.css" rel="stylesheet" />
        <script src="../myFullcalendar/lib/main.min.js"></script>
        <script>

          document.addEventListener('DOMContentLoaded', function() {
            let calendarEl = document.getElementById('calendar');
            let calendar = new FullCalendar.Calendar(calendarEl, {
              initialView: 'dayGridMonth'
            });
            calendar.render();
          });

        </script>
    </head>
    <body>
        <p> Hello {{value}} !</p>
        <br><br><br>
        <caption><h2> Here is your schedule: </h2></caption>
        <br><br>
        <div id="calendar"></div>
        <!--<script src="/node_modules/fullcalendar/calendar.js"></script>-->
    </body>