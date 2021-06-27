
from flask import Flask, render_template, request, session, redirect, url_for
import uuid
from flask_mysqldb import MySQL
# connect to data base

my_db = MySQL.connection(
  host="localhost",
  user="root",
  password="root",
  database="my_proj"
)


def create_weekly_table():
    cur = MySQL.connection.cursor()
    cur.execute("CREATE TABLE my_proj.weekly_schedule (user_id VARCHAR(255), workout_name VARCHAR(255), type VARCHAR(255), date VARCHAR(255), start_hour VARCHAR(255), duration VARCHAR(255))")


if __name__ == '__main__':
    create_weekly_table()