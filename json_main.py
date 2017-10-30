import os
from datetime import datetime

import re
import requests
from icalendar import Calendar, Event

import secrets

AUTH_ENDPOINT = 'https://my.southampton.ac.uk/campusm/sso/ldap/100'
EVENTS_ENDPOINT = 'https://my.southampton.ac.uk/campusm/sso/calendar/course_timetable/'

AUTH_PAYLOAD = {'username': secrets.USERNAME, 'password': secrets.PASSWORD}

# Fill in desired .ics file save path, use \\ as directory separator
ICAL_SAVE_PATH = ''

def get_cal_json():
    with requests.Session() as s:
        # Auth with SSO
        auth_resp = s.post(AUTH_ENDPOINT, data=AUTH_PAYLOAD)
        # Check Auth successful
        if auth_resp.status_code == 200:
            print('Successful Auth')
        else:
            print('Auth Failed')
            exit()

        # Form cal URL from relevant day of the year
        now = datetime.today()
        # Append year and day of year on events base url
        req_time = now.strftime('%Y%j')
        cal_url = EVENTS_ENDPOINT + req_time
        # Get Calendar JSON
        cal_resp = s.get(cal_url)
        return cal_resp.json()


# Probably not possible to implement as both require redirect uris
def auth_outlook_cal():
    pass


def auth_google_cal():
    pass


def json_to_ical(cal_json):
    # Get list of event dicts
    events = cal_json['events']
    # Setup ical object
    ical = Calendar()
    # Add required compliance properties
    ical.add('prodid', '-//SotonCal//mxm.dk//')
    ical.add('version', '0.9')
    #Iter through events adding each one to ical
    for event in events:
        e = Event()
        # Format datetimes compliantly
        start = datetime.strptime(event['start'].replace(':', '') , '%Y-%m-%dT%H%M%S.%f%z')
        end = datetime.strptime(event['end'].replace(':', '') , '%Y-%m-%dT%H%M%S.%f%z')
        now = datetime.now()
        # Add properties to event
        e.add('summary', event['desc2'] + classify_event(event['desc1']))
        e.add('dtstart', start)
        e.add('dtend', end)
        e.add('dtstamp', now)
        e.add('location', event['locCode'])
        e.add('uid', event['id'])
        if e.has_key('teacherName'):
            e.add('description', 'Teacher: ' + event['teacherName'] + '\nCode: ' + event['desc1'])
        else:
            e.add('description', 'Code: ' + event['desc1'])
        # Add event to icalendar
        ical.add_component(e)
    # Save ical file
    path = os.path.join(ICAL_SAVE_PATH, 'course.ics')
    f = open(path, 'wb')
    f.write(ical.to_ical())
    print('Completed\nEvents: ' + len(events).__str__())
    f.close()


def classify_event(code):
    # Try to match event code to each event types respective regex
    if re.search('(?<=\s)L\d\w?(?=\s)', code) is not None:
        return ' Lecture'
    elif re.search('(?<=\s)C\d\w?(?=\s)', code) is not None:
        return ' Computing Lab'
    elif re.search('(?<=\s)T\d?\w?(?=\s)', code) is not None:
        return ' Tutorial'
    else:
        return ''

def main():
    json_to_ical(get_cal_json())



if __name__ == '__main__':
    main()
    
