from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from calendar import Calendar
import random

# 1.4 RELEASE NOTES:
# - THIS VERSION ADDS THE "END_DAY" TO AVOID RUNNING IT UNTIL END OF MONTH
# - THE STATS NOW PRINT THE TOTAL BUSINESS DAYS AT THE VERY END

class Unavailable:
    def __init__(self, _day: int, _mor: bool = False, _after: bool = False) -> None:
        self.day= _day
        self.mor = _mor
        self.after = _after
    
    def __str__(self):
        return f'\nUnavailable day:{self.day} - Morning: {self.mor} - After: {self.after}'
    
    def __repr__(self):
        return f'\nUnavailable day:{self.day} - Morning: {self.mor} - After: {self.after}'

class Taker:
    def __init__(self, _email: str,_unavailableDays: list) -> None:
        self.email = _email
        self.unavailableDays = _unavailableDays
  
    def __str__(self):
        return f'Engineer Email: {self.email} -- Unavailable Days: {self.unavailableDays}'
    
MODE = "PROD" #IF MODE = PROD, it will send the emails

SCOPES = ['https://www.googleapis.com/auth/calendar']

# GC Notes: To stablish which month to analyze
YEAR = 2023
MONTH = 3
START_DAY = 1
END_DAY = 11

# GC Notes: To limit the creation and avoid 4th taker, 5th taker, 6th taker, onwards..
TAKERS_PER_SHIFT = 3 

# GC Notes: For calendar purposes
MORNING_SHIFT_START = "T10:00:00-03:00"
EVENING_SHIFT_START = "T14:00:00-03:00"
EVENING_SHIFT_END = "T18:00:00-03:00"

# GC Notes: Building the team, it will be considered unless they have an unavailability day in the morning or afternoon
TAKERS = [
     Taker("guido.laufer@mulesoft.com",[
        Unavailable(14,True,True),  
        Unavailable(15,True,True), 
        Unavailable(16,True,True), 
        Unavailable(17,True,True), 
        ]),
    Taker("aldo.murillo@mulesoft.com",[
        Unavailable(99,True,True),  
        ]),
    Taker("flamarina@mulesoft.com",[
        Unavailable(99,True,True),  
        ]),
    Taker("damian.lopez@mulesoft.com",[
        Unavailable(1,True,True),  
        Unavailable(2,True,True),
        Unavailable(3,True,True),    
        Unavailable(6,True,True),  
        Unavailable(7,True,True),  
        Unavailable(8,True,True),  
        Unavailable(9,True,True),  
        Unavailable(10,True,True),  
        Unavailable(15,True,True), 
        Unavailable(21,True,True), 

        ]),
    Taker("depstein@mulesoft.com",[
        Unavailable(99,True,True),   
        ]),
    Taker("german.corbetta@mulesoft.com",[
        Unavailable(1,True,True),  
        Unavailable(2,False,True),  
        Unavailable(9,True,False),  
        ]),
    Taker("ntellez@mulesoft.com",[
        Unavailable(99,True,True),    
        ]),
    Taker("gvalada@mulesoft.com",[
        Unavailable(99,True,True),  
        ])
    ]

# GC Notes: This is a copy&paste from Google Calendar usage
def sendEvent(engEmail :str, START :str, END :str, SUBJECT :str):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': SUBJECT,
        'description': SUBJECT + " -- Created by S1bot \n Order 1 = Primary \n Order 2 = Secondary \n Order 3 = Tertiary \n etc",
        'start': {
            'dateTime': START,
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'end': {
            'dateTime': END,
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        
        'attendees': [
            {'email': engEmail},
            
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 15}
            ],
        },
    }

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().insert(
        calendarId='c_k33lt3kuc7bn36jprer0jlffek@group.calendar.google.com',
        body=event).execute()
    #print(events_result)

# GC Notes: To change the order of Takers each Monday (the "monday" logic is on another method)
def randomize():
    random.shuffle(TAKERS)
    return TAKERS

# GC Notes: To get every day of the month, if it's Monday to Friday (it's not considering the public holidays)
def getMonthWeekdays():
    obj = Calendar()
    weekdays = []
    for day in obj.itermonthdays2(YEAR, MONTH):
        if ((day[0] > 0) and day[1] in {0, 1, 2, 3, 4}):
            day2 = str(YEAR) + "-" + str(MONTH) + "-" + str(day[0])
            weekdays.append((day[1], day2,day[0]))
    return weekdays

# GC Notes: Still not clear why?...
def rotate(l, n):
    return l[n:] + l[:n]

def main():
#    t1, t2 = randomize()
# GC Notes: get a list of days having 0, 1, 2, 3, 4 (L->V) + date YYYY-MM-DD + Day (1 -> 31)
    weekdays = getMonthWeekdays()
    businessDaysProcessed = 0
#    morning_team = t1
#    evening_team = t2
    print("*****************************************************")
    print("- - S1 RUNTIME SUPPORT BOT - - Running mode: " + MODE)
    print("*****************************************************")
   # print("Start,End,Engineer,Role,Email subject")
    schema = []
    team = randomize()
    stats= {} #dictoniary for stats counters
    for idx, eng in enumerate(team):
           stats[eng.email] = [0] * 6 #create an empty array for the key 
    for day in weekdays:
        # GC Notes: If day of the month >= START_DAY (it's not considering END_DAY in this script at all, it keeps running for the entire month)
        if  day[2] >= START_DAY and day[2] <= END_DAY: 
            businessDaysProcessed = businessDaysProcessed + 1
            # GC Notes: If day is Monday
            if day[0] == 0:
                team = randomize()
            # GC Notes: Not sure why he rotates it since is already randomized... the rotate moves from ABCD to CDAB
            team = rotate(team, (len(team)//2)+1)
            team_morning = team[:]
            team_afternoon = team[:]
            # GC Notes: previous movement (the ":") is to be able to use the "reverse" but still not sure why the rotate
            team_afternoon.reverse()

            print(day[1]+":")
            # GC Notes: FOR (team) and FOR (unavailable days) it removes them from morning and/or afternoon day by day
            for idx, eng in enumerate(team):
                for unDay in eng.unavailableDays:
                    x = day[1].split("-")
                    if ((str(unDay.day) == x[2]) and (unDay.mor == True)):
                        #print('Unavailable Morning:' + str(idx) + " "+ team[idx].email)
                        team_morning.remove(team[idx])
                    if ((str(unDay.day) == x[2]) and (unDay.after == True)):
                        #print('Unavailable Afteroon:' + str(idx) + " "+ team[idx].email)
                        team_afternoon.remove(team[idx])

            # GC Notes: Print the order BUT if the MODE == "PROD" it also send the event to Calendar
            print("Team Morning:")
            start = day[1]+MORNING_SHIFT_START
            end = day[1]+EVENING_SHIFT_START
            for idx, eng in enumerate(team_morning):
                order = idx+1
                if order < (TAKERS_PER_SHIFT + 1): 
                    subject="S1 Taker Order:"+ str(order) + " :" + eng.email
                    print(start + ","+ end + "," + eng.email + ","+ subject)
                    if MODE == "PROD":
                        sendEvent(eng.email, start, end, subject)
                    temp=stats[eng.email][:]
                    temp[idx] = temp[idx] + 1 
                    stats[eng.email] =temp[:] 
            print("Team After:")
            start = day[1]+EVENING_SHIFT_START
            end = day[1]+EVENING_SHIFT_END
            for idx, eng in enumerate(team_afternoon):
                order = idx+1
                if order < (TAKERS_PER_SHIFT + 1): 
                    subject="S1 Taker Order:"+ str(order) + " :" + eng.email
                    print(start + ","+ end + "," + eng.email + ","  + subject)
                    if MODE == "PROD":
                        sendEvent(eng.email, start, end, subject)
                    temp=stats[eng.email][:]
                    
                    temp[idx] = temp[idx] + 1 
                    stats[eng.email] =temp[:] 
    print("STATS: ")
    print(stats)
    print("Total Business Days: ", businessDaysProcessed)                          

if __name__ == '__main__':
    main()