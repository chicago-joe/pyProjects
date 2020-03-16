from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from readdata import read_training_set, read_testing_set

start_date = datetime(2010, 1, 31)
first_date_of_year = datetime(2010,1,1)
list_of_months = []
list_of_weekdays = []
list_of_dates = []
list_of_days_from_start_of_year = []
weeks = []
quarters = []
seasons = []
times_of_day = []

dfTrain = read_training_set('../data/TRAINING_DATA.txt')
dfTest = read_testing_set('../data/TESTING_DATA.txt')

def Northern_Hemisphere_time_of_year(doy):
    spring = range(80, 172)
    summer = range(172, 264)
    fall = range(264, 355)
    # winter = everything else

    if doy in spring:
      season = 'spring'
    elif doy in summer:
      season = 'summer'
    elif doy in fall:
      season = 'fall'
    else:
      season = 'winter'
    seasons.append(season)


def convert_dayIndex_to_variables(file):
    # dayIndex = np.sort(file['day.index'])
    dayIndex = file['day.index']
    days = dayIndex.tolist()

    for day in days:
        # Starting on January 31st 2010.
        # so if day.index == 1, then it returns 02/01/2010, just as explained in the assignment document
        new_date = start_date + timedelta(day)

        # create new feature "months"
        list_of_months.append(new_date.month)

        # create new variable "weekday" numbered 1-7
        list_of_weekdays.append(new_date.isoweekday())

        # store all the new dates computed from day.index + start_date
        list_of_dates.append(new_date.date())

        # figure out the day of year (days from 01/01/2010 to the new date computed above
        # this will help us create "season" variable
        day_of_year = (new_date - first_date_of_year).days
        list_of_days_from_start_of_year.append(day_of_year)
    return


# this creates weekend vs weekday as a new feature for the model
def create_weeks_feature():
    for day in list_of_weekdays:
        if day >= 1 and day <=5:
            day = 'weekday'
        else:
            day = 'weekend'
        weeks.append(day)
    return

# creates quarters 1 - 4 out of months in the list of months.
# this creates 1st,2nd,3rd,4th quarter as a new feature for the model
def create_quarters_feature():
    for month in list_of_months:
        if month >= 1 and month <=3:
            quarter = 1
        elif month >= 4 and month <= 6:
            quarter = 2
        elif month >= 7 and month <= 9:
            quarter = 3
        elif month >= 10 and month <= 12:
            quarter = 4
        quarters.append(quarter)
    return

# creates seasons from the day of the year (for Northern Hemisphere)
def create_seasons_feature():
    days_from_start_of_year = pd.Series(list_of_days_from_start_of_year)
    for days in list_of_days_from_start_of_year:
        season = Northern_Hemisphere_time_of_year(days)
    seasons.append(season)
    return

def create_time_of_day_feature(file):
    time_index = file['time.of.day']
    time_index = pd.Series(time_index)

    for hour in time_index:
        if 5 <= hour <= 11:
            tod = 'morning'
        elif 12 <= hour <= 17:
            tod = 'afternoon'
        elif 18 <= hour <= 22:
            tod = 'evening'
        else:
            tod = 'night'
        times_of_day.append(tod)
    return


