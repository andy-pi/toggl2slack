import requests
from config import *
import datetime
from slacker import Slacker

def lambda_handler(event, context):
    
    slack = Slacker(SLACKAPI)
    
    def get_entries(since,until):
        r = requests.get('https://toggl.com/reports/api/v2/summary', auth=(TOGGL_API, 'api_token'), params={
        'workspace_id': TOGGL_WORKSPACE,
        'since': since,
        'until': until,
        'user_agent': 'api_test'
        })
    
        return r.json()
        
    
    # Get all the time entries in the past week
    now = datetime.datetime.now()
    lastweek= now-datetime.timedelta(days=7)
    since = str(lastweek.year) + "-" + str(lastweek.month) + "-" + str(lastweek.day) 
    until = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
    data=get_entries(since,until)
    
    msgstring = "\nANDY'S TIMESHEET UPDATE \n\n"
    
    # For each toggl project
    for project in data['data']:
        title = project['title']['project']
        sumofproject=0
        # For each toggle time entry
        for i in project['items']:
            time_entry_label = i['title']['time_entry']
            time_of_entry = i['time']/(1000*60*60)
            sumofproject+=(i['time']/(1000*60*60)) # add up the total for each project as we go along in hours
            msgstring = msgstring + "    " + time_entry_label + ": " + str(time_of_entry) + "\n"
        msgstring = msgstring + "TOTAL for " + title + ": " + str(sumofproject) + "\n\n"
    
    
    # Get all the time entries in the past year
    since = str(now.year) + "-" + str(1) + "-" + str(1)
    until = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
    data=get_entries(since,until)
    
    # Total yearly hours of certain project completed
    for project in data['data']:
        title = project['title']['project']
        sumofproject=0
        if (title==YEARPROJECT):
            # For each toggle time entry
            for i in project['items']:
                sumofproject+=(i['time']/(1000*60*60)) # add up the total for each project as we go along in hours
            
    hours_remaining = 640 - sumofproject
    weeks_remaining = 52 - datetime.date(now.year, now.month, now.day).isocalendar()[1]
    average_hours_pwr = hours_remaining / weeks_remaining
    
    msgstring = msgstring + YEARPROJECT + " hours completed this year: " + str(sumofproject) + "\n"
    msgstring = msgstring + "Average hours per week remaining: " + str(average_hours_pwr) + "\n"
    
    for tries in range(8):
    	try:
    		slack.chat.post_message('#weather', msgstring)
    		break
    	except requests.exceptions.RequestException as e:
    		print e