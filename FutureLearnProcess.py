import csv
import sys
import datetime
#import numpy

#### Basic constants:
dummyTime = datetime.datetime(2000,1,1)


#### Import data from files into tables (ex: thing = inputFrom(sys.argv[1]))
def inputFrom(file):
    input = open(file, 'r')
    reader = csv.reader(input)
    lines = list(reader)
    input.close()
    return lines


#### Settings
# Default
if len(sys.argv) == 1:
    inputFile = "input.csv"
    outputFile = "output.csv"
    noticeTreshhold = 60 # number of seconds under which an activity is ignored
#    maxGraphLength = 600 # number of seconds after which an activity is seen as too long
    dropOutTreshhold = 3
    comeBackMin = 3
    lateEarlyTreshhold = 2
# If there is a settings file
else:
    settingsFile = sys.argv[1]
    allSettings = inputFrom(settingsFile)
    inputFile = allSettings[0][1]
    outputFile = allSettings[1][1]
    noticeTreshhold = int(allSettings[2][1])#60 # number of seconds under which an activity is ignored
#    maxGraphLength = int(allSettings[3][1])#600 # number of seconds after which an activity is seen as too long
    dropOutTreshhold = float(allSettings[3][1])#3
    comeBackMin = int(allSettings[4][1])#3
    lateEarlyTreshhold = int(allSettings[5][1])#2


#### Get data from file
allDataWithHead = inputFrom(inputFile)
head = allDataWithHead[0]
allData = allDataWithHead[1:]
completeData = [[line[0],line[2],line[3],line[4],line[5]] for line in allData if not line[5]=='']


#### Get the number of weeks and steps per week
numWeeks = max([int(line[1]) for line in completeData])
def getNumSteps(week):
    return max([int(line[2]) for line in completeData if int(line[1]) == week+1])
numSteps = [getNumSteps(week) for week in range(numWeeks)]
print(numSteps)
numActivity = sum(numSteps)


#### Merge the columns on week and step into a global step number, change formats
def globalStep(week,step):
    return sum(numSteps[:week-1])+ step
inputFormat = "%Y-%m-%d %H:%M:%S UTC"
def timed(string):
    return datetime.datetime.strptime(string, inputFormat)
def simplifyStep(line):
    return [line[0],int(line[1]),int(line[2]),timed(line[3]),timed(line[4]),globalStep(int(line[1]),int(line[2]))]
processed = [simplifyStep(line) for line in completeData]


print("Imported")


#### Create ActivityType and User classes for easy access to the data
# User objects contain a list of "UserActivities", which are what that user has done with one resource
class ActivityType:
    list = []
    finder = {}
    def __init__(self,ID):
        self.number = ID
        self.totalListOfActivities = []
        ActivityType.list.append(self)
        ActivityType.finder[ID] = self

class User:
    list = []
    finder = {}
    def __init__(self,ID):
        self.code = ID
        self.totalListOfActivities = []
        self.setOfActivityNumbers = set()
        User.list.append(self)
        User.finder[ID] = self

class UserActivity:
    list = []
    totalList = []
    def __init__(self,user,activ,startTime,endTime,real):
        self.user = user
        self.activ = activ
        self.number = activ.number
        self.startTime = startTime
        self.endTime = endTime # missing values are filtered earlier
        self.real = real
        self.duration = endTime-startTime
        self.duration = self.duration.total_seconds() #trick to turn the delta into seconds
        user.totalListOfActivities.append(self)
        user.setOfActivityNumbers.add(activ.number)
        activ.totalListOfActivities.append(self)
        UserActivity.totalList.append(self)
for userID in list(set([line[0] for line in processed])): User(userID)
for activ in range(numActivity): ActivityType(activ+1)

# Import all the data in these classes, line by line from the data in a table
def addActivity(line):
    user = User.finder[line[0]]
    activ = ActivityType.finder[line[5]]
    UserActivity(user,activ,line[3],line[4],True)
for line in processed: addActivity(line)

# Make dummy activities when users skipped them completely
def addDummyActivity(user,activID):
    activ = ActivityType.finder[activID]
    UserActivity(user,activ,dummyTime,dummyTime,False)
for user in User.list:
    for activID in range(1,numActivity+1):
        if not activID in user.setOfActivityNumbers:
            addDummyActivity(user,activID)


print('..', end='', flush=True)


#### Compute basic features of activity types
# Compute what is the median time spent per activity (and each decile value)
# Note: these medians are extremely variable: many people come back vs many skip to next immediately
#for activ in ActivityType.list:
#    times = [min(activity.duration,maxGraphLength) for activity in activ.totalListOfActivities if activity.duration>noticeTreshhold]
#    activ.decile = [numpy.percentile(times,k*10) for k in range(11)]
#ActivityType.list.sort(key=lambda x: x.number)
#totalExpectedTime = 0

# Compute how much time one is expected to spend in the course after each activity
#for activ in reversed(ActivityType.list):
#    activ.expectedRemainingTime = totalExpectedTime
#    totalExpectedTime += activ.decile[5]


print('.', end='', flush=True)


#### Compute basic features of user activities, with the main purpose of noticing drop-out
# Compute whether activities are done at all
# Note: as of now, if people spend more than the notice treshhold seconds
# but it may be useful to compare that to video length, for nistance.
for activity in UserActivity.totalList:
    activity.noticeable = activity.duration>noticeTreshhold

# Remove empty users
for user in User.list:
    user.toRemove = False
for activity in UserActivity.totalList:
    activity.toRemove = False
for user in User.list:
    activitiesTotal = 0
    for activity in user.totalListOfActivities:
        if activity.noticeable:
            activitiesTotal += 1
    if activitiesTotal == 0:
        user.toRemove = True
        for activity in user.totalListOfActivities:
            activity.toRemove = True

User.list = [item for item in User.list if not item.toRemove]
UserActivity.totalList = [item for item in UserActivity.totalList if not item.toRemove]
UserActivity.list = [item for item in UserActivity.list if not item.toRemove]
for activ in ActivityType.list:
    activ.totalListOfActivities = [item for item in activ.totalListOfActivities if not item.toRemove]


print("Preprocessed")


## Compute how much work time is spent on later activities (capped at 5 min per activity) (useful for drop-out)
#for user in User.list:
#    user.totalListOfActivities.sort(key=lambda x: x.number)
#for user in User.list:
#    timeSpentAfter = 0
#    for activity in reversed(user.totalListOfActivities):
#        activity.timeSpentAfter = timeSpentAfter
#        timeSpentAfter += min(activity.duration,maxGraphLength)

# Compute how many later activities were done more than a small minimum (useful for drop-out) and remove empty users
for user in User.list:
    activitiesDoneAfter = 0
    for activity in reversed(user.totalListOfActivities):
        activity.activitiesDoneAfter = activitiesDoneAfter
        if activity.noticeable:
            activitiesDoneAfter += 1

print('.', end='', flush=True)

# Compute how many activities were not done more than a small minimum right after (useful for drop-out)
for user in User.list:
    lastNumber = numActivity+1
    for activity in reversed(user.totalListOfActivities):
        activity.numSkippedAfter = lastNumber-activity.number-1
        if activity.noticeable: lastNumber = activity.number


print("Basic features computed")


#### Compute when users drop out:

## in practice compute if at least the next activity is skipped and the total time spent is extremely low
#def gaveUpRightAfter(activity):
#    return activity.timeSpentAfter<activity.activ.expectedRemainingTime/4 and activity.numSkippedAfter>3
#for user in User.list:
#    user.dropOutPoint = numActivity
#    for activity in user.totalListOfActivities:
#        if gaveUpRightAfter(activity):
#            user.dropOutPoint = activity.number
#            break

# other method: in practice compute if 2/3 of any part of the rest of the activity is not done
def mayGiveUpRightAfter(activity):
    return activity.activitiesDoneAfter<numActivity-activity.number/dropOutTreshhold and activity.numSkippedAfter>0
def didGiveUpRightAfter(user,activityNumber):
    numDone = 0
    total = 0
    for activity in user.totalListOfActivities[activityNumber:]:
        if activity.noticeable:
            numDone+=1
        total +=1
        if numDone>=total/dropOutTreshhold:
            return False
    return True
for user in User.list:
    user.dropOutPoint = numActivity
    for activity in user.totalListOfActivities:
        if mayGiveUpRightAfter(activity):
            if didGiveUpRightAfter(user,activity.number):
                user.dropOutPoint = activity.number
                break


#### Compute status of user activities
# Compute when people skip something, or peek at something
def hadDroppedOut(activity):
    return activity.user.dropOutPoint<activity.number
for user in User.list:
    for activity in user.totalListOfActivities:
        if hadDroppedOut(activity):
            if activity.noticeable: activity.type = "Peeked"
            else: activity.type = "Dropped"
        else:
            if not activity.noticeable: activity.type = "Skipped"
            else: activity.type = "Done"

# Compute when people came back to an earlier activity
def between(a,b,c):
    return a<b and b<c
def cameBackTo(activity,user):
    count = 0
    for a in user.totalListOfActivities:
        if between(activity.startTime,a.startTime,activity.endTime) and activity.number<a.number:
            count +=1
    return count>=comeBackMin
for user in User.list:
    for activity in user.totalListOfActivities:
        activity.cameBackTo = False
        if activity.type == "Done":
            if cameBackTo(activity,user): activity.cameBackTo = True
#    user.listOfActivities.sort(key=lambda x: x.endTime)


#### Compute when people do something late or early
def validEarlyExceptions(exceptions):
    goodExceptions = [a for a in exceptions if len(a.laterExceptions)<len(exceptions)]
    return len(goodExceptions) >= lateEarlyTreshhold

def validLaterExceptions(exceptions):
    goodExceptions = [a for a in exceptions if len(a.earlyExceptions)<len(exceptions)]
    return len(goodExceptions) >= lateEarlyTreshhold

def early(activity1,activity2):
    return activity1.startTime<activity2.startTime and activity1.number>activity2.number and activity1.type=="Done"

def later(activity1,activity2):
    return activity1.startTime>activity2.startTime and activity1.number<activity2.number and activity1.type=="Done"

for user in User.list:
    for activity in user.totalListOfActivities:
        if activity.type=="Done":
            time = activity.startTime
            id = activity.number
            activity.earlyExceptions = [a for a in user.totalListOfActivities if early(a,activity)]
            activity.laterExceptions = [a for a in user.totalListOfActivities if later(a,activity)]
for user in User.list:
    for activity in user.totalListOfActivities:
        activity.timeType = "NothingSpecial"
for user in User.list:
    for activity in user.totalListOfActivities:
        if activity.type=="Done":
            if validEarlyExceptions(activity.earlyExceptions):
                activity.timeType = "DoneLate"
            if validLaterExceptions(activity.laterExceptions):
                if activity.timeType=="DoneLate":
                    print("A somewhat unusual thing happened. Please contact the programmer.")
                else: activity.timeType = "DoneEarly"


print("Ready to export")


#### Aggregate all that at the activity type level
for activ in ActivityType.list:
    activ.done = 0
    activ.skipped = 0
    activ.peeked = 0
    activ.dropped = 0
    activ.comeBackTo = 0
    activ.doneEarly = 0
    activ.doneLater = 0
for activity in UserActivity.totalList:
    if activity.type == "Done": activity.activ.done +=1
    if activity.type == "Skipped": activity.activ.skipped +=1
    if activity.type == "Dropped": activity.activ.dropped +=1
    if activity.type == "Peeked": activity.activ.peeked +=1
    if activity.cameBackTo: activity.activ.comeBackTo +=1
    if activity.timeType == "DoneEarly": activity.activ.doneEarly +=1
    if activity.timeType == "DoneLate": activity.activ.doneLater +=1


#### Compute how many people are still here for the computation of proportions
for activ in ActivityType.list:
    activ.dropPoint = 0
    activ.stillHere = 0
for user in User.list:
    dop = user.dropOutPoint
    activ = ActivityType.finder[dop]
    activ.dropPoint +=1
remaining = 0
for activ in reversed(ActivityType.list):
    remaining += activ.dropPoint
    activ.stillHere = remaining

# Corner case of the first activity
activ = ActivityType.finder[1]
for activity in activ.totalListOfActivities:
    if activity.user.dropOutPoint == 1 and not activity.type == "Done":
        activ.dropPoint += -1
        activ.stillHere += -1
        activ.dropped += 1


#### Compute proportions
for activ in ActivityType.list:
    activ.doneProp = round(activ.done/activ.stillHere,4)
    activ.skippedProp = round(activ.skipped/activ.stillHere,4)
    activ.peekedProp = round(activ.peeked/len(user.list),4)
    activ.droppedProp = round(activ.dropped/activ.stillHere,4)
    activ.comeBackToProp = round(activ.comeBackTo/activ.stillHere,4)
    activ.doneEarlyProp = round(activ.doneEarly/activ.stillHere,4)
    activ.doneLaterProp = round(activ.doneLater/activ.stillHere,4)
    activ.dropPointProp = round(activ.dropPoint/activ.stillHere,4)
# Corner case of the last activity
ActivityType.finder[numActivity].dropPointProp = 0.0


#### Export to file (ex: outputTo("Result\\thing.txt", thing))
def outputTo(file,table):
    tempOutput = open(file, 'w', newline='')
    csvthing = csv.writer(tempOutput)
    csvthing.writerows(table)
    tempOutput.close()

# prepare the output
#decile = ["Decile"+str(k) for k in range(11)]
basic = ["Active","Drop","Skip","Back"]
extra = ["Early","Late","Peek","Total"]
header = ["ID"]+basic+extra#+decile
def outputLine(activ):
    basic = [activ.stillHere,activ.dropPointProp,activ.skippedProp,activ.comeBackToProp]
#    decile = activ.decile
    extra = [activ.doneEarlyProp,activ.doneLaterProp,activ.peekedProp,len(User.list)]
    return [activ.number]+basic+extra#+decile
output = [outputLine(activ) for activ in ActivityType.list]

# export
outputTo(outputFile,[header]+output)

# exportForPDF
if len(sys.argv) == 3:
    outputTo(sys.argv[2],[header]+output)

print("Results exported")
