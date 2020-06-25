import requests
import json
import sqlite3

#login
payload = json.dumps({
	"login_id": "triose", 
	"password": "triose123",
})
login_url = "http://3.6.0.2/inject-solar-angular/inject_solar_server/admin/Admin/login"
response = requests.post( login_url,data=payload)
result = json.loads(response.text)['resultObject']
user_id = result['id']
token = result['token']

#generation
payload = json.dumps({
    "month" : "01",
    "year" : "2020",
    "user_id" : "triose",
})
header = {"Authorization":token}
req_url = "http://3.6.0.2/inject-solar-angular/inject_solar_server/graph/Graph/cumulative_month_graph"
response = requests.post( req_url,headers = header, data=payload)
gen_list = json.loads(response.text)['resultObject']

payload = json.dumps({
    "month" : "02",
    "year" : "2020",
    "user_id" : "triose",
})
header = {"Authorization":token}
req_url = "http://3.6.0.2/inject-solar-angular/inject_solar_server/graph/Graph/cumulative_month_graph"
response = requests.post( req_url,headers = header, data=payload)
gen_list.extend(json.loads(response.text)['resultObject'])

#uncleared alarms
payload = json.dumps({
    "user_id" : user_id,
    "start_date" : "2020-01-01",
    "end_date" : "2020-02-29",
    "limit" : None,
    "offset" : 0,
})
req_url = "http://3.6.0.2/inject-solar-angular/inject_solar_server/normal/Alarms/getUnclearedNormalAlarms"
response = requests.post( req_url,headers = header, data=payload)
unclearedalarms = json.loads(response.text)['resultObject']

#cleared alarms
payload = json.dumps({
    "user_id" : user_id,
    "start_date" : "2020-01-01",
    "end_date" : "2020-02-29",
    "limit" : None,
    "offset" : 0,
})
req_url = "http://3.6.0.2/inject-solar-angular/inject_solar_server/normal/Alarms/getClearedNormalAlarms"
response = requests.post( req_url,headers = header, data=payload)
clearedalarms = json.loads(response.text)['resultObject']

#database initialization
mydb = sqlite3.connect('my.db')
myc=mydb.cursor()

#creating tables
myc.execute('''CREATE TABLE IF NOT EXISTS DAILY_GENERATION  (date TEXT,
								            power_generation REAL);''')

myc.execute('''CREATE TABLE IF NOT EXISTS UNCLEAERED_ALARMS (dev_name TEXT,
                                                name TEXT,
                                                inv_name TEXT,
                                                alarm_id TEXT,
                                                date_time TEXT,
                                                alarm_msg TEXT)''')

myc.execute('''CREATE TABLE IF NOT EXISTS CLEAERED_ALARMS (dev_name TEXT,
                                                name TEXT,
                                                inv_name TEXT,
                                                alarm_id TEXT,
                                                date_time TEXT,
                                                clear_time TEXT,
                                                alarm_msg TEXT)''')

#inserting data into tables
to_db = [(i['date'],i['power_generation']) for i in gen_list]
myc.executemany("INSERT INTO DAILY_GENERATION (date, power_generation) VALUES (?, ?);",to_db)

to_db = [(i['dev_name'],i['name'],i['inv_name'],i['alarm_id'],i['date_time'],i['alarm_msg']) for i in unclearedalarms]
myc.executemany("INSERT INTO UNCLEAERED_ALARMS (dev_name, name, inv_name, alarm_id, date_time, alarm_msg) VALUES (?, ?, ?, ?, ?, ?);",to_db)

to_db = [(i['dev_name'],i['name'],i['inv_name'],i['alarm_id'],i['date_time'],i['clear_time'],i['alarm_msg']) for i in clearedalarms]
myc.executemany("INSERT INTO CLEAERED_ALARMS (dev_name, name, inv_name, alarm_id, date_time, clear_time, alarm_msg) VALUES (?, ?, ?, ?, ?, ?, ?);",to_db)