#!/usr/bin/env python
# coding: utf-8

# # Creating Figures and Performing Statistical Analysis
# Used to create and perform statistical analysis for Fig. 3, 4, and 5 in Time-Restricted Feeding in the Active Phase Drives Periods of Rapid Food Consumption in Rats Fed a High-Fat, High-Sugar Diet with Liquid Sucrose by Kush Attal, Julia Wickman Shihoko Kojima, Sarah N. Blythe, Natalia Toporikova
# 

# In[1]:


#----------------------------------------------------------
# Import libraries
#----------------------------------------------------------
import pandas as pd
import numpy as np
import datetime
import os 
import matplotlib.pyplot as plt
import seaborn as sns
import math 
import matplotlib.gridspec as gridspec
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import statsmodels.stats.multicomp
import zipfile
import shutil
import sys

#----------------------------------------------------------
# Set Fonts and Background for the Figures
#----------------------------------------------------------
sns.set()
sns.set_style("whitegrid", {'axes.grid' : False, 'axes.edgecolor': 'black', 'font.family': 'Arial'})
plt.rcParams['figure.dpi'] = 1000

#----------------------------------------------------------
# Check Python Version
#----------------------------------------------------------
if sys.version < "3.8.6":
    raise Exception("Must be using Python 3.8.6 or newer")


# In[46]:


#----------------------------------------------------------
# Define Custom Methods
#----------------------------------------------------------

# Method to run Anova
def anova_analysis(anova_data):
    
    # The numerical response variable (Consumption Rate - number of seconds spent feeding) and 
    # the categorical explanatory variable (Phase Type)
    formula = 'Consumption_Rate ~ C(phase)'
    
    # Setting up the linear model
    model = ols(formula, anova_data).fit()
    
    # I am using Type I ANOVA because that is the type of ANOVA used in R
    aov_table = anova_lm(model, typ=1)
    return aov_table

# Method to create a rolling-average plot over 15 minutes
def runing_avg(x, window):
    
    # Apply rolling window averaging
    z = x.rolling(window, win_type='boxcar').mean()
    z = z.dropna()
    return(z)

# Method to adjust the lightness of colors
def adjust_lightness(color, amount=1.5):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


# Function that creates Fig3A box plot
def eating_graph(df, variable, title, palette_type, ymax = 8000):
    ax1 = sns.swarmplot(x=df.group, y=df[variable], color='black', size=3)
    ax = sns.boxplot    (x=df.group, y=df[variable], color='white', linewidth=1, palette=palette_type.fill_color, showfliers = False)
    # Make hatched pattern to distinguish between Ad lib and restriction
    for i, hatch, patch in zip(palette_type.hatch_colors, palette_type.hatches, ax.artists):
        patch.set_hatch(hatch)
        patch.set_edgecolor(i)
    # Add x- and y-labels, ticks, and units
    plt.ylabel(title, fontsize=10, fontweight = "bold", color = "black")
    plt.ylim(0,ymax)
    plt.xlabel('')
    if len(palette_type.index) == 4:
        plt.xticks(range(len(palette_type.index)), ('Cont\nAL', 'Cont\nRes', 'HFHS\nAL', 'HFHS\nRes'), fontweight = 'bold', fontsize=10, color = "black")
    if len(palette_type.index) == 2:
        plt.xticks(range(len(palette_type.index)), ('HFHS\nAL', 'HFHS\nRes'), fontweight = 'bold', fontsize=10, color = "black")
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    plt.setp(ax.lines, color="black")
    return()

# Function that creates Fig3B bar plot
def Fig3B_bar_plot_graph(df, title, barplot_plot_parameters, ymax = 5000):
    ax = sns.barplot(x="group", y="Consumption_Rate", data = df, hue = "phase", 
                     ci = 68, capsize=.1, errwidth=0.9)
    
    # Collect the color properties for the bars
    first_phase_bars = ax.patches[0:2]
    second_phase_bars = ax.patches[2:4]
    
    # Make hatched pattern to distinguish between Ad lib and restriction
    for i, hatch, fill, firstphase, secondphase,  in zip(barplot_plot_parameters.edgecolors, barplot_plot_parameters.hatches, barplot_plot_parameters.fill_color, first_phase_bars, second_phase_bars):
        # Set same face color for all 2 phases
        firstphase.set_facecolor(fill)
        secondphase.set_facecolor(adjust_lightness(fill))
        
        # Set same hatch color for all 2 phases
        firstphase.set_hatch(hatch)
        secondphase.set_hatch(hatch)
        
        # Set same edge color for all 2 phases - set new column in DropBox
        firstphase.set_edgecolor(i)
        secondphase.set_edgecolor(i)
        
        # Set "Day" and "Night" labels
        ax.text(firstphase.get_x() + firstphase.get_width() / 2, 0, "Night", ha = "center", va = "bottom", fontweight = 'bold', fontsize=10, color = "black")
        ax.text(secondphase.get_x() + secondphase.get_width() / 2, 0, "Day", ha = "center", va = "bottom", fontweight = 'bold', fontsize=10, color = "black")
           
    # Add x- and y-labels, ticks, and units
    plt.ylabel(title, fontsize=10, fontweight = "bold", color = "black")
    plt.ylim(0,ymax)
    plt.xlabel('')
    plt.xticks(range(len(barplot_plot_parameters.index)), ('Cont AL', 'HFHS AL'), fontweight = 'bold', fontsize=10, color = "black")
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    
    # Set error bar colors
    plt.setp(ax.lines[0:3] + ax.lines[6:9] + ax.lines[12:15] + ax.lines[18:21], color = "black")
    plt.setp(ax.lines[3:6] + ax.lines[9:12] + ax.lines[15:18] + ax.lines[21:24], color = "darkred")
    
    # Remove legend
    ax.get_legend().remove()
    
    # Remove unnecessary axes
    sns.despine()
    plt.tight_layout()

# Function to create Fig4A-D rolling-average Time Chart 
def time_plot_panel_v2(diet_column, color, linestyle, ymax=0.4, ylabel = "Normalized \nFeeding Activity"):
    plt.plot(runing_avg(diet_column, 1800), color = color, linestyle = linestyle, lw = 1)
    plt.yticks(fontname = 'Arial', fontsize=10, color = 'black')
    plt.ylabel(ylabel, color = 'black', fontname = 'Arial', fontsize=12, fontweight='bold')
    plt.ylim(0, ymax)
    plt.xlim('1970-01-01 21:00:00.000', '1970-01-02 21:00:00.000')
    plt.xlabel('Time (hr)', fontname = 'Arial', fontsize=10, fontweight='bold', color = 'black')
    # Span 0.5 days (span the last 1/8 of 1970-01-01 and the first 3/8 of 1970-01-02)
    plt.axvspan(0.875, 1.375, facecolor='black', alpha=0.15)
    # Clean up plot
    plt.tight_layout()
    
# Function to create Fig4E and 4F time plot of hourly feeding activity during 8-hour restricted window 
def plot_feeding_vs_time(hourly_dataframe, group, color, metafile):
    # Separate into subgroups according to diet and food accesibility
    hours = np.arange(0, hourly_dataframe.shape[0])
    ids = metafile[metafile == group].index
    feeding_series = hourly_dataframe[ids]
    line = plt.errorbar(hours, feeding_series.mean(axis = 1).fillna(0), yerr=feeding_series.std(axis = 1).fillna(0)/np.sqrt(feeding_series.shape[1]), color = color, marker = 'o', ls=plot_parameters.loc[group].line_type, markersize = 3, capsize=5, lw = 1)
    plt.xlim(0, 24)
    plt.ylim(0, 1100)
    plt.xlabel('Time (hr)', fontname = 'Arial', fontsize=10, fontweight = "bold", color = "black")
    plt.ylabel('Time Spent Feeding (sec)', fontsize=10, color = "black", fontweight = "bold")
    plt.yticks(fontname = 'Arial', fontsize=10, color = "black")
    plt.xticks([0, 6, 12, 18, 24],['21:00', '3:00', '9:00', '15:00', '21:00'], rotation=0, fontname = 'Arial', fontsize=10, color = 'black')
    
    plt.axvspan(0, 12, facecolor='black', alpha=0.15)

    # Clean up plot
    plt.tight_layout()
    
# Function to create Fig5 bar plot
def bar_plot_graph(df, title, barplot_plot_parameters, ymax = 600):
    ax = sns.barplot(x="group", y="Consumption_Rate", data = df, hue = "phase", 
                     ci = 68, capsize=.1, errwidth=0.9)
    
    # Collect the color properties for the bars
    first_phase_bars = ax.patches[0:2]
    second_phase_bars = ax.patches[2:4]
    third_phase_bars = ax.patches[4:6]
    
    # Make hatched pattern to distinguish between Ad lib and restriction
    for i, hatch, fill, firstphase, secondphase, thirdphase,  in zip(barplot_plot_parameters.edgecolors,
                                                                     barplot_plot_parameters.hatches, barplot_plot_parameters.fill_color, 
                                                                     first_phase_bars, second_phase_bars, third_phase_bars):
        # Set same face color for all 3 phases
        firstphase.set_facecolor(fill)
        secondphase.set_facecolor(fill)
        thirdphase.set_facecolor(fill)
        
        # Set same hatch color for all 3 phases
        firstphase.set_hatch(hatch)
        secondphase.set_hatch(hatch)
        thirdphase.set_hatch(hatch)
        
        # Set same edge color for all 3 phases - set new column in DropBox
        firstphase.set_edgecolor(i)
        secondphase.set_edgecolor(i)
        thirdphase.set_edgecolor(i)
        
        # Set "Hour" labels
        ax.text(firstphase.get_x() + firstphase.get_width() / 2, 0, "6th", ha = "center", va = "bottom", fontweight = 'bold', fontsize=9, color = "black")
        ax.text(secondphase.get_x() + secondphase.get_width() / 2, 0, "7th", ha = "center", va = "bottom", fontweight = 'bold', fontsize=9, color = "black")
        ax.text(thirdphase.get_x() + thirdphase.get_width() / 2, 0, "8th", ha = "center", va = "bottom", fontweight = 'bold', fontsize=9, color = "black")
        
        
    # Add x- and y-labels, ticks, and units
    plt.ylabel(title, fontsize=10, fontweight = "bold", color = "black")
    plt.ylim(0,ymax)
    plt.xlabel('')
    plt.xticks(range(len(barplot_plot_parameters.index)), ('Cont Res', 'HFHS Res'), fontweight = 'bold', fontsize=10, color = "black")
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    
    # Set error bar colors
    plt.setp(ax.lines[0:3] + ax.lines[6:9] + ax.lines[12:15] + ax.lines[18:21] + ax.lines[24:27] + ax.lines[30:33], color = "black")
    plt.setp(ax.lines[3:6] + ax.lines[9:12] + ax.lines[15:18] + ax.lines[21:24] + ax.lines[27:30] + ax.lines[33:36], color = "darkred")
    
    # Remove legend
    ax.get_legend().remove()
    
    # Remove unnecessary axes
    sns.despine()
    plt.tight_layout()


# In[3]:


#----------------------------------------------------------
# Create Directory to Hold Figures In
#----------------------------------------------------------
if not os.path.exists("Figures_And_Analysis"):
    os.mkdir("Figures_And_Analysis")


# In[4]:


#----------------------------------------------------------
# Download Raw Data
#----------------------------------------------------------
# Download plot parameters
plot_parameters = pd.read_csv("Data for figures/plotting_by_group.csv", index_col=0)

# Download raw Body Weight Data
body_weight = pd.read_csv("Data for figures/2018VT - final weight log.csv")

# Create metafile that holds group information
groups_weight = pd.read_csv("Data for figures/2018VT - final weight log.csv").T
groups_weight.columns = groups_weight.iloc[0]
groups_data = groups_weight.iloc[1:3].T

# Download all Binary Feeding Data
feeding_archive = zipfile.ZipFile(r'Data for figures/Feeding_Binary_CSV_Files.zip')
sucrose_archive = zipfile.ZipFile(r'Data for figures/Sucrose_Binary_CSV_Files.zip')

# Download data on total amount of time spent feeding
#Variables "light_food" and "dark_food" contain total time(in sec) each rat spent eating during light and dark period respectively
#Dark Period: before 9:00
#Light Period: after 9:00
feeding_data = pd.read_csv(feeding_archive.open('food_total.csv'), index_col = 0)

#Combine number of seconds in dark and light periods together into new column called "total_food"
feeding_data['total_food'] = feeding_data['light_food'] + feeding_data['dark_food']

# Download data on total amount of time spent drinking sucrose
sucrose_data = pd.read_csv(sucrose_archive.open('sucrose_total.csv'), index_col = 0)

# Combine number of seconds in dark and light periods together into new column called "total_food"
sucrose_data['total_sucrose'] = sucrose_data['light_sucrose'] + sucrose_data['dark_sucrose']

# Create dataframe with total amount of time spent drinking sucrose AND feeding
sucrose_and_feeding_data = feeding_data.drop(["group"], axis = 1).rename(columns={"light_food": "light", "dark_food": "dark", "total_food": "total"})
sucrose_and_feeding_data = sucrose_and_feeding_data.add(sucrose_data.drop(["group"], axis = 1).rename(columns={"light_sucrose": "light", "dark_sucrose": "dark", "total_sucrose": "total"}), fill_value = 0)
sucrose_and_feeding_data = sucrose_and_feeding_data.astype(int)
sucrose_and_feeding_data["group"] = feeding_data["group"]

# Create dataframe with ratios spent drinking sucrose AND feeding
sucrose_and_feeding_data_ratio = sucrose_and_feeding_data.copy()
sucrose_and_feeding_data_ratio["light"] = sucrose_and_feeding_data["light"]/sucrose_and_feeding_data["total"]
sucrose_and_feeding_data_ratio["dark"] = sucrose_and_feeding_data["dark"]/sucrose_and_feeding_data["total"]
sucrose_and_feeding_data_ratio["total"] = sucrose_and_feeding_data["total"]/sucrose_and_feeding_data["total"]

# Download normalized data on binary feeding data for each experimental group
normalized_feeding = pd.read_csv(feeding_archive.open('Feeding_Normalized_Activity.csv'), index_col='Date_Time', parse_dates=True)

# Download hourly feeding data
feeding_hourly_frame = pd.read_csv(feeding_archive.open('food_total_by_hour.csv'), index_col = 0)

# Create metafile of just group data for rats with video recordings
metafile = feeding_hourly_frame["group"]


# In[5]:


#----------------------------------------------------------
# Figure3 Generation
#----------------------------------------------------------
# Divide the dataframe into 2 phases (Day and Night)

# Day Dataframe
# Create an empty dataframe
day_phase = pd.DataFrame()

# Combine/Merge the hourly sucrose values from the first 2 hours into a single column
day_phase["Consumption_Rate"] = pd.concat([sucrose_and_feeding_data["light"]])

# Add the "group" column into this dataframe
day_phase["group"] = sucrose_and_feeding_data["group"]

# Create a new column with just the label "1st Phase" for all of the column values
day_phase["phase"] = "Day"

# Make an arbitary index
day_phase = day_phase.reset_index(drop = True)

# Night Dataframe - same process
night_phase = pd.DataFrame()
night_phase["Consumption_Rate"] = pd.concat([sucrose_and_feeding_data["dark"]])
night_phase["group"] = sucrose_and_feeding_data["group"]
night_phase["phase"] = "Night"
night_phase = night_phase.reset_index(drop = True)

# Create a single dataframe for plotting
# Combine previous dataframes into 1, keep only the ad lib animals
final_phase_frame = pd.concat([night_phase, day_phase])
final_phase_frame = final_phase_frame.where((final_phase_frame.group == "HFHS ad lib") | (final_phase_frame.group == "control ad lib"))
final_phase_frame = final_phase_frame.dropna()

# Reorder the dataframe according to diet group:
#1. Cont AL
#2. HFHS AL
#Create a new column that orders the values in the order given
final_phase_frame["barplot_order"] = pd.Categorical(final_phase_frame.phase, categories=["Night","Day"], ordered=True)
# Reorder the dataframe based on custom order
final_barplot_frame = final_phase_frame.sort_values(["barplot_order", "phase"]).reset_index(drop = True)

# Create a custom plot parameter for the barplot figure
barplot_plot_parameters = plot_parameters.reindex(["control restriction", "HFHS restriction", "control ad lib", "HFHS ad lib"]).iloc[-2:]
# Add custom edge colors
barplot_plot_parameters["edgecolors"] = ["black", "darkred"]

# Figure 3 Size
plt.figure(figsize=(7.48, 2.5))

# Figure 3A
plt.subplot(1,2,1)
eating_graph(sucrose_and_feeding_data, 'total', "Total Time Consuming \n Calories (sec)", plot_parameters)
plt.figtext(0.03, 0.93, "A", fontsize = 15, color = "black", fontweight = "bold")
# Add Significance markers
plt.annotate('#', (0.95, 7000), fontsize=15, color = 'black', fontweight='bold')

# Figure 3B
plt.subplot(1,2,2)
Fig3B_bar_plot_graph(final_barplot_frame,  "Time Spent Consuming \n Calories (sec)", barplot_plot_parameters)
plt.figtext(0.52, 0.93, "B", fontsize = 15, color = "black", fontweight = "bold")
# Add Numbers
plt.annotate('29.47%', (0.09, 2000), fontsize=10, color = 'black', fontweight='bold')
plt.annotate('70.53%', (-0.3, 4100), fontsize=10, color = 'black', fontweight='bold')
plt.annotate('18.16%', (1.05, 1000), fontsize=10, color = 'red', fontweight='bold')
plt.annotate('81.84%', (0.65, 3300), fontsize=10, color = 'red', fontweight='bold')

# Add Significance markers
plt.annotate('*', (0.17, 3000), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (1.17, 2000), fontsize=15, color = 'black', fontweight='bold')
plt.plot([0, 1], [4500, 4500], 'k-', lw=1)
plt.annotate('a', (0.45, 4600), fontsize=10, color = 'black', fontweight='bold')

plt.savefig('Figures_And_Analysis/Fig3.tif', dpi = 1000)


# In[6]:


#----------------------------------------------------------
# Figure3 Statistical Analysis
#----------------------------------------------------------
# T-Tests for Fig3
df = pd.DataFrame(columns = ["group1", "group2", "t-statistic", "p-value"])

# T-Test #1: Control Ad Lib vs Control Restriction Total Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "control restriction").dropna())
df.loc[0] = ["control ad lib", "control restriction", t, p]
# T-Test #2: HFHS Ad Lib vs HFHS Restriction Total Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "HFHS ad lib").dropna(), 
                      sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "HFHS restriction").dropna())
df.loc[1] = ["HFHS ad lib", "HFHS restriction", t, p]
# T-Test #3: Control Ad Lib Day vs Night Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["light"].where(sucrose_and_feeding_data.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data["dark"].where(sucrose_and_feeding_data.group == "control ad lib").dropna())
df.loc[2] = ["Control ad lib Day", "Control ad lib Night", t, p]
# T-Test #4: HFHS Ad Lib Day vs Night Total Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["light"].where(sucrose_and_feeding_data.group == "HFHS ad lib").dropna(), 
                      sucrose_and_feeding_data["dark"].where(sucrose_and_feeding_data.group == "HFHS ad lib").dropna())
df.loc[3] = ["HFHS ad lib Day", "HFHS ad lib Night", t, p]
# T-Test #5 Control Ad Lib Day Ratio vs HFHS Ad Lib Day Ratio Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data_ratio["light"].where(sucrose_and_feeding_data_ratio.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data_ratio["light"].where(sucrose_and_feeding_data_ratio.group == "HFHS ad lib").dropna())
df.loc[4] = ["control ad lib Day Ratio", "HFHS ad lib Day Ratio", t, p]

# T-Test #6 Control Ad Lib Night Ratio vs HFHS Ad Lib Night Ratio Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data_ratio["dark"].where(sucrose_and_feeding_data_ratio.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data_ratio["dark"].where(sucrose_and_feeding_data_ratio.group == "HFHS ad lib").dropna())
df.loc[5] = ["control ad lib Night Ratio", "HFHS ad lib Night Ratio", t, p]
df.set_index("group1").to_csv("Figures_And_Analysis/Fig3_T_Tests.csv")


# In[47]:


#----------------------------------------------------------
# Figure4 Generation
#----------------------------------------------------------
# Figure 4 Size
f = plt.figure(figsize = (7.48, 7))

# Fig4A - Control AdLib
plt.subplot(3, 2, 1)
time_plot_panel_v2(normalized_feeding["Control Ad Lib"], "0.1", "-")
# Remove x-axis and ticks for subplot
plt.xlabel('')
plt.xticks([])

## Remove '0' from y-axis
plt.gca().yaxis.get_major_ticks()[0].label1.set_visible(False)
plt.figtext(0.04, 0.97, "A", fontsize = 15, color = "black", fontweight = "bold")

# Fig4B - HFHS AdLib
plt.subplot(3, 2, 2)
time_plot_panel_v2(normalized_feeding["HFHS Ad Lib"], "red", "-")
plt.xlabel('')
plt.xticks([])
# Remove y-axis and ticks for subplot
plt.ylabel('')
plt.yticks([])
plt.figtext(0.53, 0.97, "B", fontsize = 15, color = "black", fontweight = "bold")

# Fig4C - Control Restricted
plt.subplot(3, 2, 3)
time_plot_panel_v2(normalized_feeding["Control Restricted"], "0.1", "--")
plt.xlabel('')
plt.xticks([])

## Remove '0' from y-axis
plt.gca().yaxis.get_major_ticks()[0].label1.set_visible(False)
plt.figtext(0.04, 0.67, "C", fontsize = 15, color = "black", fontweight = "bold")

# Fig4D - HFHS Restricted
plt.subplot(3, 2, 4)
time_plot_panel_v2(normalized_feeding["HFHS Restricted"], "red", "--")
plt.ylabel('')
plt.yticks([])
plt.xlabel('')
plt.xticks([])
plt.figtext(0.53, 0.67, "D", fontsize = 15, color = "black", fontweight = "bold")
plt.tight_layout()

# Fig4E - Control Restrited - 8-Hour Period
plt.subplot(3, 2, 5)
plot_feeding_vs_time(feeding_hourly_frame.T.iloc[:-1, :], "control restriction", "0.1", metafile)
# Add Significance markers
plt.annotate('*', (5.9, 220), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (6.9, 150), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (7.9, 220), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (8.9, 240), fontsize=15, color = 'black', fontweight='bold')
plt.figtext(0.04, 0.36, "E", fontsize = 15, color = "black", fontweight = "bold")

# Fig4F - HFHS Restrited - 8-Hour Period
plt.subplot(3, 2, 6)
plot_feeding_vs_time(feeding_hourly_frame.T.iloc[:-1, :], "HFHS restriction", "red", metafile)
plt.ylabel('')
plt.yticks([])
# Add Significance markers
plt.annotate('*', (4.9, 200), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (5.9, 210), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (7.7, 160), fontsize=15, color = 'black', fontweight='bold')
plt.figtext(0.53, 0.36, "F", fontsize = 15, color = "black", fontweight = "bold")

plt.tight_layout()
plt.savefig("Figures_And_Analysis/Fig4.tif", dpi = 1000)


# In[8]:


#----------------------------------------------------------
# Figure4 Statistical Analysis
#----------------------------------------------------------
# Running T-Tests to Compare All Hours Against the First Hour of Binge-Eating
df = pd.DataFrame(columns = ["diet", "hour1", "hour2", "t-statistic", "p-value"])
diet_groups = ["control restriction", "HFHS restriction"]
i = 0
hours_to_check = ["0:00", "1:00","2:00", "3:00","4:00", "5:00","6:00"]
for group in diet_groups:
    ids = metafile[metafile == group].index
    for hour in feeding_hourly_frame.iloc[:, :-1]:
        feeding_series = feeding_hourly_frame.iloc[:, :-1].loc[ids]
        if feeding_series[hour].isnull().all() or hour not in hours_to_check:
            pass
        else:
            t, p = stats.ttest_ind(feeding_series["23:00"].dropna(), 
                          feeding_series[hour].dropna())
            df.loc[i] = [group, "23:00", hour, t, p]
            i += 1
df.set_index("diet").to_csv("Figures_and_Analysis/Fig4_T_Tests.csv")


# In[9]:


#----------------------------------------------------------
# Figure5 Generation
#----------------------------------------------------------
# Select only the final 3 hours of interest (from 4:00 to 7:00)
final_hours_of_interest = feeding_hourly_frame[["4:00", "5:00", "6:00", "group"]]
final_hours_of_interest = final_hours_of_interest[(final_hours_of_interest["group"] == "control restriction") | (final_hours_of_interest["group"] == "HFHS restriction")]


# 6th Hour Dataframe (4:00)
# Create an empty dataframe
final_first_phase = pd.DataFrame()

# Combine/Merge the hourly feeding values from the first 2 hours into a single column
final_first_phase["Consumption_Rate"] = pd.concat([final_hours_of_interest["4:00"]])

# Add the "group" column into this dataframe
final_first_phase["group"] = final_hours_of_interest["group"]

# Create a new column with just the label "1st Phase" for all of the column values
final_first_phase["phase"] = "6th Hour"

# Make an arbitary index
final_first_phase = final_first_phase.reset_index(drop = True)

# Follow the same procedure for the other 2 phases.
# The only difference is the hours chosen for the "Consumption_Rate" column

# 7th Hour Dataframe (5:00)
final_mid_phase = pd.DataFrame()
final_mid_phase["Consumption_Rate"] = pd.concat([final_hours_of_interest["5:00"]])
final_mid_phase["group"] = final_hours_of_interest["group"]
final_mid_phase["phase"] = "7th Hour"
final_mid_phase = final_mid_phase.reset_index(drop = True)

# 8th Hour Dataframe (6:00)
final_last_phase = pd.DataFrame()
final_last_phase["Consumption_Rate"] = pd.concat([final_hours_of_interest["6:00"]])
final_last_phase["group"] = final_hours_of_interest["group"]
final_last_phase["phase"] = "8th Hour"
final_last_phase = final_last_phase.reset_index(drop = True)

# Final 3 Hour Dataframe
# Combine all of the 3 previous dataframes into 1
final_frame = pd.concat([final_first_phase, final_mid_phase, final_last_phase])
final_frame['group_and_phase'] = final_frame["group"].astype(str) +" "+ final_frame["phase"].astype(str)
final_frame = final_frame.dropna()

#Create a new column that orders the values in the order given
final_frame["barplot_order"] = pd.Categorical(final_frame.group, categories=["control restriction","HFHS restriction"], ordered=True)

# Reorder the dataframe based on custom order
final_barplot_frame = final_frame.sort_values(["barplot_order", "phase"]).reset_index(drop = True)

# Create a custom plot parameter for the barplot figure
final_barplot_plot_parameters = plot_parameters.reindex(["control ad lib", "HFHS ad lib", "control restriction", "HFHS restriction"]).iloc[-2:]

# Add custom edge colors
final_barplot_plot_parameters["edgecolors"] = ["grey", "red"]

# Figure 5 Size
plt.figure(figsize=(3.75, 2.5))

# Final 3 Hours
bar_plot_graph(final_barplot_frame, "Time Spent Feeding (sec)", final_barplot_plot_parameters)
# Add Significance markers
plt.annotate('ab', (1.225, 550), fontsize=10, color = 'black', fontweight='bold')

#Save Figure in a TIFF file
plt.savefig("Figures_And_Analysis/Fig5.tif", dpi = 1000)


# In[10]:


#----------------------------------------------------------
# Figure5 Statistical Analysis
#----------------------------------------------------------
#----ANOVA for Final 3 Hours------   
# Perform 1-Way ANOVA and place the results in a dataframe
anova_df = anova_analysis(final_frame)

# Perform Tukey post-hoc
mc_interaction = statsmodels.stats.multicomp.MultiComparison(final_frame["Consumption_Rate"], final_frame['group_and_phase'])
mc_interaction_results = mc_interaction.tukeyhsd(alpha = 0.05)

# Place the Tukey results in a dataframe
mc_interaction = pd.DataFrame(data=mc_interaction_results._results_table.data[1:], columns=mc_interaction_results._results_table.data[0])

# Combine the 1-Way ANOVA results and Tukey PostHoc results into 1 dataframe
result = pd.concat([anova_df, mc_interaction], axis = 0, sort = False)
# Remove irrelevant comparisons
result.drop([2, 3, 4, 6, 7, 8, 9, 10, 11], axis = 0, inplace = True)
result.fillna("").rename(index={0:'', 1:'', 5:'', 12:'', 13:'', 14:''}).to_csv("Figures_and_Analysis/Fig5_ANOVA_and_TukeyHSD.csv")

