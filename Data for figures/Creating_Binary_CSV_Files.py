# Creating CSV Files of Feeding and Sucrose Activity
# Used to create binary CSV files for Fig. 3 through 7 in
# Time-Restricted Feeding in the Active Phase Drives Periods of Rapid Food Consumption in Rats Fed a High-Fat, High-Sugar Diet with Liquid Sucrose
# by Kush Attal, Julia Wickman Shihoko Kojima, Sarah N. Blythe, Natalia Toporikova


#----------------------------------------------------------
# Import libraries
#----------------------------------------------------------
import pandas as pd
import numpy as np
import datetime
import os 
import zipfile
import shutil
import sys

#----------------------------------------------------------
# Check Python Version
#----------------------------------------------------------
if sys.version < "3.8.2":
    raise Exception("Must be using Python 3.8.2 or newer")


#----------------------------------------------------------
# Define Custom Methods
#----------------------------------------------------------

# Method to calculate time spent consuming food during (1) light and (2) dark phases
def light_summary(df, timeseries):
    # Time of light on, the data start at light on
    light_start = pd.to_datetime('1970-01-02 09:00:00')
    #Separate dataframes into light and dark times
    dark = timeseries[timeseries.index<light_start]
    light = timeseries[timeseries.index>light_start]
    # Calculate total food consumption per rat
    total_eating_light = light.sum(axis=0)
    total_eating_dark  = dark.sum(axis=0)
    # Record food comsumption into a new dataframe, using rat number as index
    for x in total_eating_light.index[:-1]:
        ind = int(x[-2:])
        df.loc[ind]=[total_eating_light[x], total_eating_dark[x]]
    return (df)

# Method to collect all the .xlxs files into lists separated by diet and create a single dataframe
def get_dataframe(diet_name, video_archive):
    # Create a dataframe using .xlsx files from raw video data
    list_to_fill = [name for name in video_archive.namelist() 
                    if name.endswith((diet_name + ".xlsx", diet_name + ".xls")) 
                    & name.startswith(('Raw'))]
    diet_dataframe = pd.DataFrame()
    for i in list_to_fill:
        df = pd.read_excel(video_archive.open(i), index_col = "seconds")
        diet_dataframe = diet_dataframe.append(df)
    diet_dataframe = diet_dataframe.sort_index()
    return diet_dataframe


# Method to create diet dataframe with all of the data and add columns logging which activity was performed at each time interval
# A '1' indicates the activity STARTed and occured over that time interval. 
# A '0' indicates the activity STOPped and did not occur over that time interval. 
def add_binary(all_data):
    all_data_copy = all_data.copy()
    behaviors = ['Water', 'Feeding', 'Grooming', 'Rearing', 'Sleeping/Resting', 'Sucrose']
    #Add columns that log which activity was performed (except for Zoomie)
    for i in behaviors:
        behavior_dataframe = all_data_copy.where(all_data_copy.Behavior == i)
        to_binary_dict = {"START":1, "STOP":0}
        all_data_copy[i + "_" + 'Activity'] = behavior_dataframe["Status"].replace(to_binary_dict)
    #Add column for locomotor activity (Zoomie) since it uses POINT to indicate activity rather than START or STOP
    zoom = (all_data_copy['Status']>= 'POINT') & (all_data_copy['Behavior'] == 'Zoomie')
    all_data_copy['Zoomie_Activity'] = zoom.astype(int)
    
    return all_data_copy

# Method to design a 1-second bin pivot table ordered by rat Name and showing 'duration' of feeding activity indicated by '1's.
def times(activity_capitalized, all_data_copy, diet, counts = False):
    # Create a dataframe with rows as time indices and columns as rat numbers. Values will be "1" or "0".
    times = all_data_copy.pivot_table(index = 'seconds', columns = ['Name'], values = [activity_capitalized + '_Activity'])
    
    # Round up any non-zero fractions to '1' - there have been cases where 2 activities "START"ed at the exact same time so instead of a "1" for both columns, there was a "0.5" for both. Therefore, we need to round 0.5 up to 1 
    times = np.ceil(times)

    # Forward-fill the empty NaN values for each rat with the '0' or '1' that came before it - THIS WILL CALCULATE THE DURATION OF THE ACTIVITY (for counts/bouts, set the "counts" parameter to True)
    if counts == False:
        times = times.ffill()
    
    # Backward-fill remaining empty Nan values for each rat with a '0'
    times = times.fillna(0)
    
    # Resample dataframe into 1-second intervals
    if counts == False:
        times = times.resample("1S").ffill()
    else:
        times = times.resample("1S").max()
    
    # Backward-fill remaining empty Nan values for each rat with a '0'
    times = times.fillna(0)
    
    # Convert the dataframe to integers rather than floats - for faster processing
    times = times.astype(int)
    
    ## Actively look into the Excel files, find the hours or intervals not recorded for each rat, and set each of those hours to NaN
    if diet == "Control Adlib":
        times.loc['1970-01-01 08:00:00':'1970-01-01 10:59:59', (activity_capitalized + '_Activity','Rat09')] = np.nan
        times.loc['1970-01-01 19:00:00':'1970-01-01 19:59:59', (activity_capitalized + '_Activity','Rat09')] = np.nan
        
    if diet == "Control Restricted":
        times.loc['1970-01-01 07:00:00':'1970-01-01 07:59:59'] = np.nan
        times.loc['1970-01-01 18:00:00':'1970-01-01 18:59:59'] = np.nan
        times.loc['1970-01-01 23:00:00':'1970-01-01 23:59:59', (activity_capitalized + '_Activity','Rat14')] = np.nan
        times.loc['1970-01-01 23:00:00':'1970-01-01 23:59:59', (activity_capitalized + '_Activity','Rat18')] = np.nan
        
    if diet == "HFHS Adlib":
        times.loc['1970-01-01 14:00:00':'1970-01-01 19:59:59', (activity_capitalized + '_Activity','Rat27')] = np.nan
        
    # Rearrange hours so Hour 21 is the first hour
    m = times.index.get_level_values(0) > datetime.datetime(1970, 1, 1, 20, 59, 59)
    idx1 = times.index.get_level_values(0)
    times.index = idx1.where(m, idx1 +  datetime.timedelta(days=1))

    times = times.sort_index()                
    
    # Add 16 extra hours with value of '0' for time-restricted animals - 0's FOR FEEDING AND SUCROSE ACTIVITY FOR ANYTHING OUTSIDE 8-HOUR INTERVAL
    if diet == "HFHS Restricted" or diet == "Control Restricted":
        dates = ["1970-01-01 21:00:00", "1970-01-01 22:00:00", "1970-01-02 7:00:00", 
                 "1970-01-02 8:00:00", "1970-01-02 9:00:00", "1970-01-02 10:00:00", 
                 "1970-01-02 11:00:00", "1970-01-02 12:00:00", "1970-01-02 13:00:00", 
                 "1970-01-02 14:00:00", "1970-01-02 15:00:00", "1970-01-02 16:00:00", 
                 "1970-01-02 17:00:00", "1970-01-02 18:00:00", "1970-01-02 19:00:00", 
                 "1970-01-02 20:00:00"]

        for i in dates:
            ts = pd.to_datetime(i, format="%Y-%m-%d %H:%M:%S")
            # Change the number of 0's to the number of rats
            if diet == "HFHS Restricted":
                new_row = pd.DataFrame([[0, 0, 0, 0, 0, 0, 0]], columns = times.columns, index=[ts])
            if diet == "Control Restricted":
                new_row = pd.DataFrame([[0, 0, 0, 0, 0, 0, 0, 0, 0]], columns = times.columns, index=[ts])
            times = pd.concat([times, pd.DataFrame(new_row)], ignore_index=False)
        times = times.sort_index()
    
    
    # Construct normalized rat for diet group by finding the average of activity for all rats at each 1-second interval - Replace Nan values with 0 if any
    times[('','mean')] = times.mean(axis=1).fillna(0)
    
    # Drop duplicate rows based on the time indices
    times = times.loc[~times.index.duplicated(keep='first')]
    
    # Remove multi-level columns
    times.columns = times.columns.get_level_values(1)
    
    # Rename the Index from "Name" to ""
    times = times.rename_axis(columns = {"Name":""})
        
    return times




#----------------------------------------------------------
# Create Directories to Hold Figures In
#----------------------------------------------------------
if not os.path.exists("Feeding_Binary_CSV_Files"):
    os.mkdir("Feeding_Binary_CSV_Files")
if not os.path.exists("Sucrose_Binary_CSV_Files"):
    os.mkdir("Sucrose_Binary_CSV_Files")




#----------------------------------------------------------
# Download Raw Data
#----------------------------------------------------------
# Download all Binary Feeding Data
video_archive = zipfile.ZipFile(r'Raw Video Data.zip')

# Extract all .xlsx files from video archive into 4 pandas dataframes - separated by diet
cont_restr_compiled = get_dataframe("Control_Restricted", video_archive)
hfhs_restr_compiled = get_dataframe("HFHS_Restricted", video_archive)
cont_adlib_compiled = get_dataframe("Control_Adlib", video_archive)
hfhs_adlib_compiled = get_dataframe("HFHS_Adlib", video_archive)

# Add columns of 1s and 0s for each activity to specify whether a behavior is occurring 
# Create the binary dataframes
cont_restr_binary = add_binary(cont_restr_compiled)
hfhs_restr_binary = add_binary(hfhs_restr_compiled)
cont_adlib_binary = add_binary(cont_adlib_compiled)
hfhs_adlib_binary = add_binary(hfhs_adlib_compiled)




#----------------------------------------------------------
# Generate Feeding Binary CSV Files by diet group
#----------------------------------------------------------
# Design a dataframe to analyze time/duration of specific activity for all rats and a "normalized" rat (see below for explanation) over 24 hours
# Create the 1-second binary dataframes
hfhs_restr_feeding = times('Feeding', hfhs_restr_binary, "HFHS Restricted")
cont_restr_feeding = times('Feeding', cont_restr_binary, "Control Restricted")
hfhs_adlib_feeding = times('Feeding', hfhs_adlib_binary, "HFHS Adlib")
cont_adlib_feeding = times('Feeding', cont_adlib_binary, "Control Adlib")

# Create CSV file for Normalized Feeding Activity
# A normalized rat for a diet group is the average of all rat activity (excluding NaN values) for every 1-second interval of time
# 1 means all rats were performing the activity simultaneously in the 1-second time interval
# 0 means no rats were performing the activity simultaneously in the 1-second time interval
# Values range from 0 to 1
normalized_feeding = pd.DataFrame()
normalized_feeding = normalized_feeding.append(cont_adlib_feeding['mean'])
normalized_feeding = normalized_feeding.append(hfhs_adlib_feeding['mean'])
normalized_feeding = normalized_feeding.append(cont_restr_feeding['mean'])
normalized_feeding = normalized_feeding.append(hfhs_restr_feeding['mean'])
feeding_to_print = normalized_feeding.T
feeding_to_print = feeding_to_print.sort_index().fillna(0)
feeding_to_print.to_csv('Feeding_Binary_CSV_Files/Feeding_Normalized_Activity.csv', index = True, index_label = "Date_Time", header = ['Control Ad Lib', 'HFHS Ad Lib', 'Control Restricted', 'HFHS Restricted'], date_format='%Y-%m-%d %H:%M:%S')

# Create 1-Second Binned CSV files for Feeding Activity for All Rats in Each Diet Group
cont_restr_feeding.to_csv("Feeding_Binary_CSV_Files/Feeding_Control_Restricted_Binary.csv", index = True, columns = cont_restr_feeding.columns[:-1], date_format='%Y-%m-%d %H:%M:%S', index_label = "Date_Time")
hfhs_restr_feeding.to_csv("Feeding_Binary_CSV_Files/Feeding_HFHS_Restricted_Binary.csv", index = True, columns = hfhs_restr_feeding.columns[:-1], date_format='%Y-%m-%d %H:%M:%S', index_label = "Date_Time")
hfhs_adlib_feeding.to_csv("Feeding_Binary_CSV_Files/Feeding_HFHS_AdLib_Binary.csv", index = True, columns = hfhs_adlib_feeding.columns[:-1], date_format='%Y-%m-%d %H:%M:%S', index_label = "Date_Time")
cont_adlib_feeding.to_csv("Feeding_Binary_CSV_Files/Feeding_Control_AdLib_Binary.csv", index = True, columns = cont_adlib_feeding.columns[:-1], date_format='%Y-%m-%d %H:%M:%S', index_label = "Date_Time")




#----------------------------------------------------------
# Generate Feeding Hourly Activity CSV File
#----------------------------------------------------------
# Create CSV file for Light and Dark Feeding Activity for Each Rat
column_names = ["light_food", "dark_food"]
df = pd.DataFrame(columns = column_names)

df = light_summary(df, cont_adlib_feeding)
df = light_summary(df, cont_restr_feeding)
df = light_summary(df, hfhs_adlib_feeding)
df = light_summary(df, hfhs_restr_feeding)

# Create metafile that holds group information
body_weight = pd.read_csv("2018VT - daily weight log.csv").T
body_weight.columns = body_weight.iloc[0]
metafile = body_weight.iloc[1:3].T

# Create group variable that specifies diet for each rat
df['group']=metafile.loc[df.index].Diet+' '+metafile.loc[df.index].Feeding
df.to_csv('Feeding_Binary_CSV_Files/food_total.csv')

# Create CSV file that totals amount of time spent feeding per hour
# Resample all of the dataframes by 1 Hour. 
cont_adlib_feeding_hourly = cont_adlib_feeding.iloc[:, :-1].resample("1H").agg(pd.Series.sum, skipna=False).T
hfhs_adlib_feeding_hourly = hfhs_adlib_feeding.iloc[:, :-1].resample("1H").agg(pd.Series.sum, skipna=False).T
cont_restr_feeding_hourly = cont_restr_feeding.iloc[:, :-1].resample("1H").agg(pd.Series.sum, skipna=False).T
hfhs_restr_feeding_hourly = hfhs_restr_feeding.iloc[:, :-1].resample("1H").agg(pd.Series.sum, skipna=False).T

# Combine all 4 new dataframes into one list
hourly_feeding_frames = [cont_adlib_feeding_hourly, cont_restr_feeding_hourly, hfhs_adlib_feeding_hourly, hfhs_restr_feeding_hourly]

# Concatenate/Merge all 4 dataframes into 1 dataframe
feeding_hourly_frame = pd.concat(hourly_feeding_frames)

# Set the index of new dataframe as just rat numbers (i.e. "2" instead of "Rat2"). 
# This will set the index to the same index as the metafile
feeding_hourly_frame.index = feeding_hourly_frame.index.map(lambda x: int(str(x)[3:]))

# Add a new column that holds the diet group information (which of the 4 diet groups that the rat belongs to)
feeding_hourly_frame['group']=metafile.loc[feeding_hourly_frame.index].Diet+' '+metafile.loc[feeding_hourly_frame.index].Feeding

# Rename all of the columns into actual hour times - making it easier to choose columns
feeding_hourly_frame.columns = ["21:00", "22:00", "23:00", "0:00", "1:00", "2:00", "3:00", "4:00",
                                "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00",
                                "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
                                "group"]

# Create CSV file
feeding_hourly_frame.to_csv("Feeding_Binary_CSV_Files/food_total_by_hour.csv")




#----------------------------------------------------------
# Generate Sucrose Binary CSV Files by diet group
#----------------------------------------------------------
# Create the 1-second dataframes for Sucrose Activity
hfhs_restr_sucrose = times('Sucrose', hfhs_restr_binary, "HFHS Restricted")
hfhs_adlib_sucrose = times('Sucrose', hfhs_adlib_binary, "HFHS Adlib")

# Create CSV file for Normalized Sucrose Activity
normalized_sucrose = pd.DataFrame()
normalized_sucrose = normalized_sucrose.append(hfhs_adlib_sucrose['mean'])
normalized_sucrose = normalized_sucrose.append(hfhs_restr_sucrose['mean'])
sucrose_to_print = normalized_sucrose.T
sucrose_to_print = sucrose_to_print.sort_index().fillna(0)
sucrose_to_print.to_csv('Sucrose_Binary_CSV_Files/Sucrose_Normalized_Activity.csv', index = True, index_label = "Date_Time", header = ['HFHS Ad Lib', 'HFHS Restricted'], date_format='%Y-%m-%d %H:%M:%S')

# Create 1-Second Binned CSV file for Sucrose Activity for All Rats in Each HFHS Group
hfhs_restr_feeding.to_csv("Sucrose_Binary_CSV_Files/Sucrose_HFHS_Restricted_Binary.csv", index = True, columns = hfhs_restr_sucrose.columns[:-1], date_format='%Y-%m-%d %H:%M:%S', index_label = "Date_Time")
hfhs_adlib_feeding.to_csv("Sucrose_Binary_CSV_Files/Sucrose_HFHS_AdLib_Binary.csv", index = True, columns = hfhs_adlib_sucrose.columns[:-1], date_format='%Y-%m-%d %H:%M:%S', index_label = "Date_Time")




#----------------------------------------------------------
# Generate Sucrose Hourly Activity CSV Files by diet group
#----------------------------------------------------------
# Create CSV file for Light and Dark Sucrose Activity for Each Rat
column_names = ["light_sucrose", "dark_sucrose"]
df = pd.DataFrame(columns = column_names)

df = light_summary(df, hfhs_adlib_sucrose)
df = light_summary(df, hfhs_restr_sucrose)

df['group']=metafile.loc[df.index].Diet+' '+metafile.loc[df.index].Feeding
df.to_csv('Sucrose_Binary_CSV_Files/sucrose_total.csv')

# Create CSV file that total amount of time spent drinking sucrose per hour
# Resample all of the dataframes by 1 Hour.
hfhs_adlib_sucrose_hourly = hfhs_adlib_sucrose.iloc[:, :-1].resample("1H").agg(pd.Series.sum, skipna=False).T
hfhs_restr_sucrose_hourly = hfhs_restr_sucrose.iloc[:, :-1].resample("1H").agg(pd.Series.sum, skipna=False).T

# Combine 2 dataframes into one list
hourly_sucrose_frames = [hfhs_adlib_sucrose_hourly, hfhs_restr_sucrose_hourly]

# Concatenate/Merge both dataframes into 1 dataframe
sucrose_hourly_frame = pd.concat(hourly_sucrose_frames)

# Set the index of the new dataframe as just the rat numbers (i.e. "2" instead of "Rat2"). 
# This will set the index to the same index as the groups_data dataframe
sucrose_hourly_frame.index = sucrose_hourly_frame.index.map(lambda x: int(str(x)[3:]))

# Add a new column that holds the diet group information (which of the 2 HFHS groups that the rat belongs to)
sucrose_hourly_frame['group']=metafile.loc[sucrose_hourly_frame.index].Diet+' '+metafile.loc[sucrose_hourly_frame.index].Feeding

# Rename all of the columns into actual hour times - making it easier to choose columns
sucrose_hourly_frame.columns = ["21:00", "22:00", "23:00", "0:00", "1:00", "2:00", "3:00", "4:00",
                                "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00",
                                "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
                                "group"]

# Create CSV file
sucrose_hourly_frame.to_csv("Sucrose_Binary_CSV_Files/sucrose_total_by_hour.csv")




#----------------------------------------------------------
# Create Zip File and Remove Directory
#----------------------------------------------------------
# Create Zip File
shutil.make_archive("Feeding_Binary_CSV_Files", 'zip', "Feeding_Binary_CSV_Files")
shutil.make_archive("Sucrose_Binary_CSV_Files", 'zip', "Sucrose_Binary_CSV_Files")

# Remove Directories
folders_to_remove = [name for name in os.listdir()
                    if (name.startswith(('Feeding_Binary_CSV_Files')))  & (not name.endswith((".zip")))]
for folder in folders_to_remove:
    shutil.rmtree(folder)
    
folders_to_remove = [name for name in os.listdir()
                    if (name.startswith(('Sucrose_Binary_CSV_Files')))  & (not name.endswith((".zip")))]
for folder in folders_to_remove:
    shutil.rmtree(folder)

