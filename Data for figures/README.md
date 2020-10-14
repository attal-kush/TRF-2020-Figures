# TRF-2020-Figures - Creating Binary Activity Files

This repository contains the raw data and Python scripts needed to reproduce figures from the manuscript: **Time-Restricted Feeding in the Active Phase Drives Periods of Rapid Food Consumption in Rats Fed a High-Fat, High-Sugar Diet with Liquid Sucrose**

To recreate the binary ZIP archives for feeding and sucrose drinking activity, follow 3 steps:
1. Download this entire repository into any local directory (if not done already)
2. These scripts were created using [Python version **3.8.6**](https://www.python.org/downloads/release/python-386/), so **ensure Python version 3.8.6 is installed.** Then, use *requirements.txt* to download the proper versions of all libraries needed to run the scripts. 
3. Run *Creating_Binary_CSV_Files.py* without making any changes to source code. ZIP files labeled "Feeding_Binary_CSV_Files.zip" and "Sucrose_Binary_CSV_Files.zip" will be located in the current folder "Data for Figures".

There are 4 types of CSV files created in these ZIP files:
1. A CSV file that totals time (in sec) spent feeding (or drinking sucrose) during the light phase (from 09:00 h to 21:00 h) and during the dark phase (from 21:00 h to 09:00 h) for each rat (ordered by ascending rat number). There is an additional column that specifies which of the 4 diet types the rat belongs to.
2. A CSV file that totals time (in sec) spent feeding (or drinking sucrose) for each hour and for every rat that was video-recorded. Hours are labeled by the beginning time, so a column labeled "23:00" measures all feeding (or sucrose drinking) activity from 23:00:00 to 23:59:59. There is an additional column that specifies which of the 4 diet types the rat belongs to.
3. CSV binary files that are separated (and labeled) by diet group. Columns represent the individual rats and rows represent 1-second intervals starting from 21:00 h to 20:59:59 h of the next day, in other words, spanning an entire 24-hour period. Column values are filled with either a "0" (denoting that the rat was not actively feeding or drinking sucrose in the 1-second interval) or a "1" (denoting that the rat was actively feeding or drinking sucrose in the 1-second interval). Here is an example:
