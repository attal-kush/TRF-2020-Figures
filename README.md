# TRF-2020-Figures

This repository contains the raw data and Python scripts needed to reproduce figures from the manuscript: **Time-Restricted Feeding in the Active Phase Drives Periods of Rapid Food Consumption in Rats Fed a High-Fat, High-Sugar Diet with Liquid Sucrose**

To generate figures 3, 4, and 5 from the manuscript, follow these steps:
1. Download the entire repository into any local directory
2. These scripts were created using Python version **3.8.6**, so **ensure Python version 3.8.6 (or newer) is installed.** Then, use *requirements.txt* to download the proper versions of all libraries needed to run the scripts. 
3. Run *figures_and_analysis.py* without making any changes. Results will be located in a newly-created directory labeled "Figures_And_Analysis", which itself will be created in this folder "TRF-2020-Figures"

Raw video data is located in "Data for Figures". To recreate the ZIP archives for feeding and sucrose binary activity, complete Step 1 from above and run *Creating_Binary_CSV_Files.py* located in "Data for Figures"

