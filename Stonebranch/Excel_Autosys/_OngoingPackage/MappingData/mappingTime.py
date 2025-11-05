import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Time Mapping.xlsx'
OUTPUT_SHEETNAME = 'Time Result'
OUTPUT_SHEETNAME_ADDITIONAL = 'Day of Week Result Additional'
OUTPUT_SHEETNAME_ADDITIONAL_CALENDAR = 'Calendar Result Additional'
OUTPUT_SHEETNAME_LOG = 'Time Log'

JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'jobBox'
MAINBOX_COLUMN = 'Main Box'


sys.setrecursionlimit(10000)


def replaceNan(value):
    if pd.isna(value):
        return ''
    return value


def recursiveSearchStartBox(df_dict, task_name, cache):
    if task_name in cache:
        return cache[task_name]
    
    # Find row in pre-indexed dataframe dictionary
    row_data = df_dict.get(task_name)
    
    if row_data:
        box_name = row_data['box_name']
        if pd.notna(box_name):
            result = recursiveSearchStartBox(df_dict, box_name, cache)
            cache[task_name] = result  # Cache the result
            return result
        cache[task_name] = row_data  # Cache final result if no recursion
        return row_data
    else:
        cache[task_name] = None  # Cache empty result
        return None
        
def searchRootTime(df):
    job_start_root_time = []
    number_of_rows = len(df)
    count = 0
    df_dict = df.set_index('jobName').to_dict(orient='index')
    cache = {}
    for row in df.itertuples(index=False):
        #print(row)
        start_row = recursiveSearchStartBox(df_dict, row.jobName, cache)
        #print(start_row)
        if start_row is None:
            job_start_root_time.append({
                'jobName': row.jobName,
                'rootBox': None,
            })
        else:
            start_row_job_name = next((key for key, value in df_dict.items() if value == start_row), None)
            if start_row_job_name == row.jobName:
                job_start_root_time.append({
                    'jobName': row.jobName,
                    'jobType': replaceNan(row.jobType),
                    'rootBox': 'Self Start',
                    'rootDateCondition': replaceNan(row.date_conditions),
                    'rootDayOfWeek': replaceNan(row.days_of_week),
                    'rootBoxStartTime': replaceNan(row.start_times),
                    'rootBoxCondition': replaceNan(row.condition),
                    'rootBoxRunCalendar': replaceNan(row.run_calendar),
                    'rootBoxExcludeCalendar': replaceNan(row.exclude_calendar),
                })
            else:
                job_start_root_time.append({
                    'jobName': row.jobName,
                    'jobType': replaceNan(row.jobType),
                    'jobBox': row.box_name,
                    'rootBox': start_row_job_name,
                    'rootDateCondition': replaceNan(start_row['date_conditions']),
                    'rootDayOfWeek': replaceNan(start_row['days_of_week']),
                    'rootBoxType': replaceNan(start_row['jobType']),
                    'rootBoxStartTime': replaceNan(start_row['start_times']),
                    'rootBoxCondition': replaceNan(start_row['condition']),
                    'rootBoxRunCalendar': replaceNan(start_row['run_calendar']),
                    'rootBoxExcludeCalendar': replaceNan(start_row['exclude_calendar']),
                    'jobDateCondition': replaceNan(row.date_conditions),
                    'jobDayOfWeek': replaceNan(row.days_of_week),
                    'jobStartTime': replaceNan(row.start_times),
                    'jobCondition': replaceNan(row.condition),
                    'jobRunCalendar': replaceNan(row.run_calendar),
                    'jobExcludeCalendar': replaceNan(row.exclude_calendar),
                })
        count += 1
        print(f'{count}/{number_of_rows} done | {row.jobName}')
    return job_start_root_time



def findingTimeOfBox(df_root_start):
    time_series_job_dict = {}
    time_result_list = []
    day_of_week_additional_result_list = []
    calendar_additional_result_list = []
    time_log_list = []
    
    max_count = 0
    for row in df_root_start.itertuples(index=False):
        job_name = getattr(row, 'jobName')
        job_box_name = getattr(row, 'jobBox')
        main_box = getattr(row, 'rootBox')

        root_date_conditions = getattr(row, 'rootDateCondition')
        job_date_conditions = getattr(row, 'jobDateCondition')
        if root_date_conditions == 1:

            if job_date_conditions == 1:
                start_times = getattr(row, 'jobStartTime')
                days_of_week = getattr(row, 'jobDayOfWeek')
                calendar = getattr(row, 'jobRunCalendar')
                #exclude_calendar = getattr(row, 'jobExcludeCalendar')
            else:
                start_times = getattr(row, 'rootBoxStartTime')
                days_of_week = getattr(row, 'rootDayOfWeek')
                calendar = getattr(row, 'rootBoxRunCalendar')
                #exclude_calendar = getattr(row, 'rootBoxExcludeCalendar')

            start_time_list = []
            
            if pd.notna(start_times):
                start_time_list = [time.strip() for time in start_times.split(',')]
                for time in start_time_list:
                    if len(time) < 5 and len(time) != 0:
                        time = '0' + time
                        
                    time_series_job_dict.setdefault(time, {})
                    
                    # Add job to days_of_week if it exists
                    if pd.notna(days_of_week) and str(days_of_week).strip() != '':
                        schedule_key = f"Day"
                        time_series_job_dict[time].setdefault(schedule_key, {})
                        days_of_week_list = [day.strip() for day in days_of_week.split(',')]
                        for day_of_week in days_of_week_list:
                            time_series_job_dict[time][schedule_key].setdefault(day_of_week, [])
                            time_series_job_dict[time][schedule_key][day_of_week].append(job_name)
                    
                    # Add job to calendar if it exists  
                    if pd.notna(calendar) and str(calendar).strip() != '':
                        schedule_key = f"Calendar"
                        time_series_job_dict[time].setdefault(schedule_key, {})
                        time_series_job_dict[time][schedule_key].setdefault(calendar, [])
                        time_series_job_dict[time][schedule_key][calendar].append(job_name)
                    

                    time_log_list.append({
                        'Job Name': job_name,
                        'Box Name': job_box_name,
                        'Main Box': main_box,
                        'Start Time': time,
                        'Root Date Condition': getattr(row, 'rootDateCondition'),
                        'Root days of week': getattr(row, 'rootDayOfWeek'),
                        'Root Calendar': getattr(row, 'rootBoxRunCalendar'),
                        'Root Exclude Calendar': getattr(row, 'rootBoxExcludeCalendar'),
                        'Job Date Condition': getattr(row, 'jobDateCondition'),
                        'Job days of week': getattr(row, 'jobDayOfWeek'),
                        'Job Calendar': getattr(row, 'jobRunCalendar'),
                        'Job Exclude Calendar': getattr(row, 'jobExcludeCalendar'),
                        
                    })
                    max_count += 1
            else:
                print(f'No start time for job: {job_name}')
                    
        elif root_date_conditions == 0:
            time_log_list.append({
                'Job Name': job_name,
                'Box Name': job_box_name,
                'Main Box': main_box,
                'Start Time': 'N/A',
                'Root Date Condition': getattr(row, 'rootDateCondition'),
                'Root days of week': getattr(row, 'rootDayOfWeek'),
                'Root Calendar': getattr(row, 'rootBoxRunCalendar'),
                'Root Exclude Calendar': getattr(row, 'rootBoxExcludeCalendar'),
                'Job Date Condition': getattr(row, 'jobDateCondition'),
                'Job days of week': getattr(row, 'jobDayOfWeek'),
                'Job Calendar': getattr(row, 'jobRunCalendar'),
                'Job Exclude Calendar': getattr(row, 'jobExcludeCalendar'),
                
            })
            max_count += 1

    for time, schedule_dict in time_series_job_dict.items():
        total_jobs_for_time = 0
        
        for schedule_key, schedule_values in schedule_dict.items():
            for schedule_value, jobs in schedule_values.items():
                job_count = len(jobs)
                total_jobs_for_time += job_count
                if schedule_key == "Day":
                    day_of_week_additional_result_list.append({
                        'Time': time,
                        'Days of Week': schedule_value,
                        'Count': job_count,
                    })
                elif schedule_key == "Calendar":
                    calendar_additional_result_list.append({
                        'Time': time,
                        'Calendar': schedule_value,
                        'Count': job_count,
                    })
                else:  # No Schedule
                    print(f'No Schedule for time: {time}')


        time_result_list.append({
            'Time': time,
            'Count': total_jobs_for_time,
        })

    df_time_result = pd.DataFrame(time_result_list)
    df_time_result = df_time_result[df_time_result['Count'] > 0]

    df_day_of_week_additional_result = pd.DataFrame(day_of_week_additional_result_list, columns=['Time', 'Days of Week', 'Count'])
    df_calendar_additional_result = pd.DataFrame(calendar_additional_result_list, columns=['Time', 'Calendar', 'Count'])
    df_time_log_list = pd.DataFrame(time_log_list)

    return df_time_result, df_day_of_week_additional_result, df_calendar_additional_result, df_time_log_list


def main():
    df_job = getDataExcel("input main job file")
    column_list = ['jobName', 'jobType', 'jobBox', 'rootBox', 'rootBoxType', 'rootDateCondition','rootDayOfWeek','rootBoxStartTime', 
                                            'rootBoxCondition','rootBoxRunCalendar', 'rootBoxExcludeCalendar', 
                                            'jobDateCondition', 'jobDayOfWeek', 'jobStartTime', 'jobCondition', 'jobRunCalendar', 'jobExcludeCalendar']
    if df_job.columns.tolist() != column_list:
        root_start_list = searchRootTime(df_job)
        df_root_start = pd.DataFrame(root_start_list, 
                                    columns=column_list)
    else:
        df_root_start = df_job
    df_result, df_day_of_week_additional, df_calendar_additional, df_log = findingTimeOfBox(df_root_start)

    createExcel(OUTPUT_EXCEL_NAME,(OUTPUT_SHEETNAME, df_result), (OUTPUT_SHEETNAME_ADDITIONAL, df_day_of_week_additional), (OUTPUT_SHEETNAME_ADDITIONAL_CALENDAR, df_calendar_additional), (OUTPUT_SHEETNAME_LOG, df_log))
if __name__ == '__main__':
    main()