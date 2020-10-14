# TRF-2020-Figures - Creating Binary Activity Files

This repository contains the raw data and Python scripts needed to reproduce figures from the manuscript: **Time-Restricted Feeding in the Active Phase Drives Periods of Rapid Food Consumption in Rats Fed a High-Fat, High-Sugar Diet with Liquid Sucrose**

To recreate the binary ZIP archives for feeding and sucrose drinking activity, follow 3 steps:
1. Download this entire repository into any local directory (if not done already)
2. These scripts were created using [Python version **3.8.6**](https://www.python.org/downloads/release/python-386/), so **ensure Python version 3.8.6 is installed.** Then, use *requirements.txt* to download the proper versions of all libraries needed to run the scripts. 
3. Run *Creating_Binary_CSV_Files.py* without making any changes to source code. ZIP files labeled "Feeding_Binary_CSV_Files.zip" and "Sucrose_Binary_CSV_Files.zip" will be located in the current folder "Data for Figures".

There are 4 types of CSV files created in these ZIP files:
1. A CSV file that totals time (in sec) spent feeding (or drinking sucrose) during the light phase (from 09:00 h to 21:00 h) and during the dark phase (from 21:00 h to 09:00 h) for each rat (ordered by ascending rat number). There is an additional column that specifies which of the 4 diet types the rat belongs to.
2. A CSV file that totals time (in sec) spent feeding (or drinking sucrose) for each hour and for every rat that was video-recorded. Hours are labeled by the beginning time, so a column labeled "23:00" measures all feeding (or sucrose drinking) activity from 23:00:00 to 23:59:59. There is an additional column that specifies which of the 4 diet types the rat belongs to.
3. CSV binary files that are separated (and labeled) by diet group. Columns represent the individual rats and rows represent 1-second intervals starting from 21:00 h to 20:59:59 h of the next day, in other words, spanning an entire 24-hour period. Column values are filled with either a "0" (denoting that the rat was not actively feeding or drinking sucrose in the 1-second interval) or a "1" (denoting that the rat was actively feeding or drinking sucrose in the 1-second interval). Here is an example from the binary feeding CSV file for the control group with unrestricted food access with the date-time index modified for clarity:
![image of binary data example](https://user-images.githubusercontent.com/38625335/95988886-8981cb00-0df7-11eb-98f9-fb62b081c32a.png)

For the third row (date-time index of 21:03:05), there is "1" for Rat08, signifying that for the 1-second interval from 21:03:05 until 21:03:06, Rat08 was actively eating solid-chow. The "0"'s elsewhere denote that for those 1-second intervals, the rats were not eating solid-chow

4. A CSV file that shows the proportion of rats (from 0 to 1) for every diet group that is engaged in feeding (or sucrose drinking) activity for each 1-second interval. The date-time index is the same as the example shown above; however, the columns - instead of showing individual rats - show each unique diet group. Column values are filled with a number from 0 (no rats engaged in feeding or sucrose drinking activity) to 1 (all rats engaged in feeding or sucrose drinking activity). Here is an example with from the feeding CSV file with the same date-time index:
![image](https://user-images.githubusercontent.com/38625335/95989935-e762e280-0df8-11eb-8f9d-076de28ba595.png)

For the third row (date-time index of 21:03:05), there is a "0.125" because 1 out of the 8 rats in the control, unrestricted access group is actively eating solid-chow in the 1-second interval from 21:03:05 until 21:03:06. The "0"'s denote that for those 1-second intervals, none of the rats in the diet group were eating solid-chow
