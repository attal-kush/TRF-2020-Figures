# Creating Figures and Performing Statistical Analysis
# Used to create and perform statistical analysis for all figures in 
# Time-Restricted Feeding in the Active Phase Drives Periods of Rapid Food Consumption in Rats Fed a High-Fat, High-Sugar Diet with Liquid Sucrose 
# by Kush Attal, Julia Wickman Shihoko Kojima, Sarah N. Blythe, Natalia Toporikova

#----------------------------------------------------------
# Import libraries
#----------------------------------------------------------
import pandas as pd
import numpy as np
import datetime
import os 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
plt.rcParams['hatch.linewidth'] = 3
plt.rcParams['figure.dpi'] = 1000

#----------------------------------------------------------
# Check Python Version
#----------------------------------------------------------
if sys.version < "3.8.6":
    raise Exception("Must be using Python 3.8.6 or newer")


#----------------------------------------------------------
# Define Custom Methods
#----------------------------------------------------------

# Function to create Fig1A time plot
def Fig1A_timeplot(metafile, body_weight):
    # Separate into subgroups according to diet and food accesibility, then plot each subgroup
    regime = metafile.Feeding.unique()
    diet   = metafile.Diet.unique()
    days = np.arange(0, body_weight.shape[0])
    restriction_start = 27
    artists = []
    for x in diet:
        for y in regime:
            group = str(x)+' '+str(y)
            ids = metafile[(metafile.Diet==x) & (metafile.Feeding==y)].index
            weight_series = body_weight[ids]
            # Create line plot with SEM
            line = plt.errorbar(days, weight_series.mean(axis = 1), yerr=weight_series.std(axis = 1)/np.sqrt(weight_series.shape[1]), color = plot_parameters.loc[group].color, marker = 'o', ls=plot_parameters.loc[group].line_type, markevery=5, markersize = 3, capsize=5, errorevery=5, lw = 1)
            plt.axvline(x=restriction_start, ymin=0, ymax=400, color='black', ls ='--')
            artists.append(line)     
    # Add x- and y-labels, ticks, and units
    plt.xlabel('Days on diet', fontsize=10, fontweight = "bold", color = "black")
    plt.ylabel('Body Weight (g)', fontsize=10, fontweight = "bold", color = "black")
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    plt.xticks(fontweight = 'bold', fontsize=10, color = "black")
    plt.legend(artists, ('Cont\nAL', 'Cont\nRes', 'HFHS\nAL', 'HFHS\nRes'), fontsize = 8.6)
    
# Method to run ANOVA stats and Tukey Posthoc on body weight data for each day
def day_anova_analysis(day, anova_data):
    formula = 'Q("' + day + '") ~ C(Diet) + C(Feeding) + C(Diet):C(Feeding)'
    model = ols(formula, anova_data).fit()
    aov_table = anova_lm(model, typ=1)

    mc_interaction = statsmodels.stats.multicomp.MultiComparison(anova_data[day], anova_data['diet_and_schedule'])
    mc_interaction_results = mc_interaction.tukeyhsd()
    mc_interaction = pd.DataFrame(data=mc_interaction_results._results_table.data[1:], columns=mc_interaction_results._results_table.data[0])

    result = pd.concat([aov_table, mc_interaction], axis = 0, sort = False)
     
    return result
    
# Function to create Fig1B boxplot
def Fig1B_boxplot(master_data, plot_parameters):
    ax1 = sns.swarmplot(x=master_data.group, y=master_data.total_fat_pad, color='black', size=3)
    ax = sns.boxplot    (x=master_data.group, y=master_data.total_fat_pad, color='white', linewidth=1, palette=plot_parameters.fill_color, showfliers = False)
    # Make hatched pattern to distinguish between ad lib and restriction
    for i, hatch, patch in zip(plot_parameters.hatch_colors, plot_parameters.hatches, ax.artists):
        patch.set_hatch(hatch)
        patch.set_edgecolor(i)

    # Add x- and y-labels, ticks, and units
    plt.ylabel('Total Fat Mass (g)', fontsize=10, fontweight = "bold", color = "black")
    plt.xlabel('')
    plt.xticks(range(len(plot_parameters.index)), ('Cont\nAL', 'Cont\nRes', 'HFHS\nAL', 'HFHS\nRes'), fontweight = 'bold', fontsize=10, color = "black")
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    plt.setp(ax.lines, color="black")
    
    
# Function to create Fig2 boxplot
def Fig2_boxplot(metabolite, unit, name):
    # Set the size, dashed lines, and colors for the figure
    ax = sns.boxplot(x=master_data.index, y=metabolite, color='white', linewidth=1, palette=plot_parameters.fill_color, showfliers = False)
    hatches = ["", "///", "", "///"]
    colors = ["black", "gray", "black", "red"]
    for i, hatch, patch in zip(plot_parameters.hatch_colors, plot_parameters.hatches, ax.artists):
        patch.set_hatch(hatch)
        patch.set_edgecolor(i)

    # Add x- and y-labels, ticks, and units
    plt.ylabel(name + ' (' + unit + ')', fontsize=10, fontweight = "bold", color = "black")
    plt.xlabel('')
    #plt.xticks(range(len(plot_parameters.index)), plot_parameters.label, fontweight = 'bold', fontsize=10, color = "black")
    ax.tick_params(labelbottom=False) 
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    plt.setp(ax.lines, color="black")

    # Clean up and save the figure
    sns.despine()
    plt.tight_layout()
    
# Method to create legend for Fig2
def make_legend():
    a_val = 0.6
    colors = ['gray','gray','red','red']

    circ1 = mpatches.Patch( facecolor=colors[0],hatch='',label='Cont\nAL')
    circ2 = mpatches.Patch( facecolor=colors[1],hatch='//',label='Cont\nRes')
    circ3 = mpatches.Patch(facecolor=colors[2],hatch='',label='HFHS\nAL')
    circ4 = mpatches.Patch(facecolor=colors[3],hatch='//',label='HFHS\nRes')

    plt.legend(handles = [circ1,circ2,circ3, circ4],loc=0, bbox_to_anchor=(1, 1))
    plt.tight_layout()
    return()

    
# Method to run ANOVA stats and Tukey Posthoc on metabolite data
def metabolite_anova_analysis(metabolite, anova_data):
    formula = metabolite + ' ~ C(diet) + C(feeding_schedule) + C(diet):C(feeding_schedule)'
    model = ols(formula, anova_data).fit()
    aov_table = anova_lm(model, typ=1)
    
    mc_interaction = statsmodels.stats.multicomp.MultiComparison(anova_data[metabolite], anova_data['group'])
    mc_interaction_results = mc_interaction.tukeyhsd()
    mc_interaction = pd.DataFrame(data=mc_interaction_results._results_table.data[1:], columns=mc_interaction_results._results_table.data[0])
    
    result = pd.concat([aov_table, mc_interaction], axis = 0, sort = False)

    return result

# Function to create Fig3A box plot
def Fig3A_boxplot(df, variable, title, palette_type, ymax = 8000):
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
    plt.xticks(range(len(palette_type.index)), ('Cont\nAL', 'Cont\nRes', 'HFHS\nAL', 'HFHS\nRes'), fontweight = 'bold', fontsize=10, color = "black")
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    plt.setp(ax.lines, color="black")
    return()

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

# Function to create Fig3B bar plot
def Fig3B_barplot(df, title, barplot_plot_parameters, ymax = 5000):
    ax = sns.barplot(x="group", y="Consumption_Rate", data = df, hue = "phase", 
                     ci = 68, capsize=.1, errwidth=0.9)
    
    # Collect the color properties for the bars
    first_phase_bars = ax.patches[0:2]
    second_phase_bars = ax.patches[2:4]
    
    # Make hatched pattern to distinguish between ad lib and restriction
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
        
        # Set "Night" and "Day" labels
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

# Method to create a rolling-average plot over 30 minutes
def runing_avg(x, window):
    
    # Apply rolling window averaging
    z = x.rolling(window, win_type='boxcar').mean()
    z = z.dropna()
    return(z)
    
# Function to create Fig4A-D rolling-average Time Chart 
def Fig4AD_timeplot(diet_column, color, linestyle, ymax=0.4, ylabel = "Normalized \nFeeding Activity"):
    plt.plot(runing_avg(diet_column, 1800), color = color, linestyle = linestyle, lw = 1)
    
    # Add x- and y-labels, ticks, and units
    plt.yticks(fontname = 'Arial', fontsize=10, color = 'black')
    plt.ylabel(ylabel, color = 'black', fontname = 'Arial', fontsize=10, fontweight='bold')
    plt.ylim(0, ymax)
    plt.xlim('1970-01-01 21:00:00.000', '1970-01-02 21:00:00.000')
    plt.xlabel('Time (hr)', fontname = 'Arial', fontsize=10, fontweight='bold', color = 'black')
    
    # Span 0.5 days (span the last 1/8 of Day 1 and the first 3/8 of Day 2) and shade for dark phase
    plt.axvspan(0.875, 1.375, facecolor='black', alpha=0.15)
    # Clean up plot
    plt.tight_layout()
    
# Function to create Fig4E and 4F time plot of hourly feeding activity during 8-hour restricted window 
def Fig4EF_timeplot(hourly_dataframe, group, color, video_metafile):
    # Separate new dataframe into subgroups according to diet and food accesibility
    hours = np.arange(0, hourly_dataframe.shape[0]) + 1
    ids = video_metafile[video_metafile == group].index
    feeding_series = hourly_dataframe[ids]
    
    # Create line with SEM
    line = plt.errorbar(hours, feeding_series.mean(axis = 1).fillna(0), yerr=feeding_series.std(axis = 1).fillna(0)/np.sqrt(feeding_series.shape[1]), color = color, marker = 'o', ls=plot_parameters.loc[group].line_type, markersize = 3, capsize=5, lw = 1)
    
    # Add x- and y-labels, ticks, and units
    plt.xlim(0, 24)
    plt.ylim(0, 1100)
    plt.xlabel('Time (hr)', fontname = 'Arial', fontsize=10, fontweight = "bold", color = "black")
    plt.ylabel('Time Spent Feeding (sec)', fontsize=10, color = "black", fontweight = "bold")
    plt.yticks(fontname = 'Arial', fontsize=10, color = "black")
    plt.xticks([0, 6, 12, 18, 24],['21:00', '3:00', '9:00', '15:00', '21:00'], rotation=0, fontname = 'Arial', fontsize=10, color = 'black')
    
    # Add shading to depic "night" vs "day" phase
    plt.axvspan(0, 12, facecolor='black', alpha=0.15)

    # Clean up plot
    plt.tight_layout()
    
# Function to create Fig5 bar plot
def Fig5_barplot(df, title, barplot_plot_parameters, ymax = 600):
    # Create barplot 
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
        # Set same face color for each of the 3 phases
        firstphase.set_facecolor(fill)
        secondphase.set_facecolor(fill)
        thirdphase.set_facecolor(fill)
        
        # Set same hatch color for each of the 3 phases
        firstphase.set_hatch(hatch)
        secondphase.set_hatch(hatch)
        thirdphase.set_hatch(hatch)
        
        # Set same edge color for each of the 3 phases
        firstphase.set_edgecolor(i)
        secondphase.set_edgecolor(i)
        thirdphase.set_edgecolor(i)
        
        # Set "Hour" labels at bottom
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
    
# Function to create Fig6AB rolling-average Time Chart 
def Fig6AB_timeplot(diet_column, color, linestyle, ymax=0.08, ylabel = "Normalized \nSucrose Activity"):
    plt.plot(runing_avg(diet_column, 1800), color = color, linestyle = linestyle, lw = 1)
    
    # Add x- and y-labels, ticks, and units
    plt.yticks(fontname = 'Arial', fontsize=10, color = 'black')
    plt.ylabel(ylabel, color = 'black', fontname = 'Arial', fontsize=10, fontweight='bold')
    plt.ylim(0, ymax)
    plt.xlim('1970-01-01 21:00:00.000', '1970-01-02 21:00:00.000')
    plt.xlabel('Time (hr)', fontname = 'Arial', fontsize=10, fontweight='bold', color = 'black')
    
    # Span 0.5 days (span the last 1/8 of Day 1 and the first 3/8 of Day 2) and shade dark phase
    plt.axvspan(0.875, 1.375, facecolor='black', alpha=0.15)
    # Clean up plot
    plt.tight_layout()
    
# Function to create Fig6C time plot of hourly sucrose activity during 8-hour restricted window 
def Fig6C_timeplot(hourly_dataframe, group, color, video_metafile):
    # Separate new dataframe into subgroups according to diet and food accesibility
    hours = np.arange(0, hourly_dataframe.shape[0]) + 1
    ids = video_metafile[video_metafile == group].index
    sucrose_series = hourly_dataframe[ids]
    
    # Create line with SEM
    line = plt.errorbar(hours, sucrose_series.mean(axis = 1).fillna(0), yerr=sucrose_series.std(axis = 1).fillna(0)/np.sqrt(sucrose_series.shape[1]), color = color, marker = 'o', ls=plot_parameters.loc[group].line_type, markersize = 3, capsize=5, lw = 1)
    
    # Add x- and y-labels, ticks, and units
    plt.xlim(0, 24)
    plt.ylim(0, 250)
    plt.xlabel('Time (hr)', fontname = 'Arial', fontsize=10, fontweight = "bold", color = "black")
    plt.ylabel('Time Spent Drinking \nSucrose (sec)', fontsize=10, color = "black", fontweight = "bold")
    plt.yticks(fontname = 'Arial', fontsize=10, color = "black")
    plt.xticks([0, 6, 12, 18, 24],['21:00', '3:00', '9:00', '15:00', '21:00'], rotation=0, fontname = 'Arial', fontsize=10, color = 'black')
    
    # Add shading to depict "night" vs "day" phase
    plt.axvspan(0, 12, facecolor='black', alpha=0.15)

    # Clean up plot
    plt.tight_layout()
    
# Function to create Fig7 bar plot
def Fig7_barplot(df, title, barplot_plot_parameters, ymax = 150):
    # Create barplot 
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
        # Set same face color for each of the 3 phases
        firstphase.set_facecolor(fill)
        secondphase.set_facecolor(fill)
        thirdphase.set_facecolor(fill)
        
        # Set same hatch color for each of the 3 phases
        firstphase.set_hatch(hatch)
        secondphase.set_hatch(hatch)
        thirdphase.set_hatch(hatch)
        
        # Set same edge color for each of the 3 phases
        firstphase.set_edgecolor(i)
        secondphase.set_edgecolor(i)
        thirdphase.set_edgecolor(i)
        
        # Set "Hour" labels at bottom
        ax.text(firstphase.get_x() + firstphase.get_width() / 2, 0, "6th", ha = "center", va = "bottom", fontweight = 'bold', fontsize=9, color = "black")
        ax.text(secondphase.get_x() + secondphase.get_width() / 2, 0, "7th", ha = "center", va = "bottom", fontweight = 'bold', fontsize=9, color = "black")
        ax.text(thirdphase.get_x() + thirdphase.get_width() / 2, 0, "8th", ha = "center", va = "bottom", fontweight = 'bold', fontsize=9, color = "black")
        
        
    # Add x- and y-labels, ticks, and units
    plt.ylabel(title, fontsize=10, fontweight = "bold", color = "black")
    plt.ylim(0,ymax)
    plt.xlabel('')
    plt.xticks(range(len(barplot_plot_parameters.index)), ('HFHS AL', 'HFHS Res'), fontweight = 'bold', fontsize=10, color = "black")
    plt.yticks(fontweight = 'bold', fontsize=10, color = "black")
    
    # Set error bar colors
    plt.setp(ax.lines[0:3] + ax.lines[6:9] + ax.lines[12:15] + ax.lines[18:21] + ax.lines[24:27] + ax.lines[30:33], color = "darkred")
    plt.setp(ax.lines[3:6] + ax.lines[9:12] + ax.lines[15:18] + ax.lines[21:24] + ax.lines[27:30] + ax.lines[33:36], color = "darkred")
    
    # Remove legend
    ax.get_legend().remove()
    
    # Remove unnecessary axes
    sns.despine()
    plt.tight_layout()
    
# Method to run ANOVA and Tukey on feeding and sucrose activity (final 3 hours)
def activity_anova(anova_data):
    
    # The numerical response variable (Consumption Rate - number of seconds spent feeding) and 
    # the categorical explanatory variable (Phase Type)
    formula = 'Consumption_Rate ~ C(phase)'
    
    # Setting up the linear model
    model = ols(formula, anova_data).fit()
    
    # Using Type I ANOVA because that is standard in R
    aov_table = anova_lm(model, typ=1)
    
    # Perform Tukey post-hoc
    mc_interaction = statsmodels.stats.multicomp.MultiComparison(anova_data["Consumption_Rate"], anova_data['group_and_phase'])
    mc_interaction_results = mc_interaction.tukeyhsd(alpha = 0.05)

    # Place the Tukey results in a dataframe
    mc_interaction = pd.DataFrame(data=mc_interaction_results._results_table.data[1:], columns=mc_interaction_results._results_table.data[0])

    # Combine the 1-Way ANOVA results and Tukey PostHoc results into 1 dataframe
    result = pd.concat([aov_table, mc_interaction], axis = 0, sort = False)
    # Remove irrelevant comparisons
    result.drop([2, 3, 4, 6, 7, 8, 9, 10, 11], axis = 0, inplace = True)
    result = result.fillna("").rename(index={0:'', 1:'', 5:'', 12:'', 13:'', 14:''})
    return result

# Function to create Fig8 boxplot
def Fig8_boxplot(data, plot_parameters, name):
    #ax1 = sns.swarmplot(x=data.group, y=data[name], color='black', size=6)
    ax = sns.boxplot   (x=data.group, y=data[name], color='white', linewidth=1, palette=plot_parameters.fill_color, showfliers = False)
    # Make hatched pattern to distinguish between Ad lib and restriction
    for i, hatch, patch in zip(plot_parameters.hatch_colors, plot_parameters.hatches, ax.artists):
        patch.set_hatch(hatch)
        patch.set_edgecolor(i)
    # Add x- and y-labels, ticks, and units    
    plt.xlabel('')
    plt.ylabel(c.capitalize(), fontstyle = "italic", fontsize = "x-large")
    ax.xaxis.set_major_formatter(plt.NullFormatter())

# Method to create legend for Fig8
def make_gene_legend():
    a_val = 0.6
    colors = ['gray','none','red','none']

    circ1 = mpatches.Patch(facecolor=colors[0],hatch='',label='Cont AL')
    circ2 = mpatches.Patch(facecolor=colors[1],hatch='//', edgecolor = "gray", label='Cont Res')
    circ3 = mpatches.Patch(facecolor=colors[2],hatch='',label='HFHS AL')
    circ4 = mpatches.Patch(facecolor=colors[3],hatch='//', edgecolor = "red", label='HFHS Res')

    plt.legend(handles = [circ1,circ2,circ3, circ4],loc="upper left", bbox_to_anchor=[0, 1], 
              fancybox = True, borderaxespad=0., prop={'size': 15})
    return()



#----------------------------------------------------------
# Create Directory to Hold Figures In
#----------------------------------------------------------
if not os.path.exists("Figures_And_Analysis"):
    os.mkdir("Figures_And_Analysis")



#----------------------------------------------------------
# Download Raw Data
#----------------------------------------------------------
# Download plot parameters
plot_parameters = pd.read_csv("Data for figures/plotting_by_group.csv", index_col=0)

# Download raw Body Weight Data
body_weight = pd.read_csv("Data for figures/2018VT - daily weight log.csv")

# Create metafile that holds group information for ALL rats
plot_body_weight = body_weight.T
plot_body_weight.columns = plot_body_weight.iloc[0]
metafile = plot_body_weight.iloc[1:3].T

# Download master document with metabolite data
master_data = pd.read_csv("Data for figures/2018VT_termination_data_master_document.csv")
# Correct column names and add columns
master_data['diet_and_schedule']=master_data.diet+' '+master_data.feeding_schedule
master_data = master_data.set_index('diet_and_schedule')
master_data['group']=master_data.diet+' '+master_data.feeding_schedule
master_data = master_data.rename(columns={" Leptin": "Leptin", "triglyceride (mg/mL)": "Triglyceride"}, index = {"control ad lib": "Control Ad Lib", "control restriction": "Control Restricted", "HFHS ad lib": "HFHS Ad Lib", "HFHS restriction": "HFHS Restricted"})

# Download all Binary Feeding Data
feeding_archive = zipfile.ZipFile(r'Data for figures/Feeding_Binary_CSV_Files.zip')
sucrose_archive = zipfile.ZipFile(r'Data for figures/Sucrose_Binary_CSV_Files.zip')

# Download data on total amount of time spent feeding
# Variables "light_food" and "dark_food" contain total time(in sec) each rat spent eating during light and dark period respectively
# Dark Period: before 9:00
# Light Period: after 9:00
feeding_data = pd.read_csv(feeding_archive.open('food_total.csv'), index_col = 0)

# Download normalized data on binary feeding data for each experimental group
normalized_feeding = pd.read_csv(feeding_archive.open('Feeding_Normalized_Activity.csv'), index_col='Date_Time', parse_dates=True)

# Download hourly feeding data 
feeding_hourly_frame = pd.read_csv(feeding_archive.open('food_total_by_hour.csv'), index_col = 0)

# Create metafile of just group data for rats with video recordings
video_metafile = feeding_hourly_frame["group"]

# Download data on total amount of time spent drinking sucrose
sucrose_data = pd.read_csv(sucrose_archive.open('sucrose_total.csv'), index_col = 0)

# Download normalized data on binary sucrose data for each experimental group
normalized_sucrose = pd.read_csv(sucrose_archive.open('Sucrose_Normalized_Activity.csv'), index_col='Date_Time', parse_dates=True)

# Download hourly sucrose data 
sucrose_hourly_frame = pd.read_csv(sucrose_archive.open('sucrose_total_by_hour.csv'), index_col = 0)

# Download gene data
gene_data = pd.read_csv("Data for figures/qPCR_normalized_gapdph.csv", index_col=0)



#----------------------------------------------------------
# Figure1 Generation
#----------------------------------------------------------
# Modify raw data for figures
plot_body_weight.drop(['Rat', 'Diet', 'Feeding'], inplace = True)

# Figure 1 Size
plt.figure(figsize = (7.48, 3.0))

# Create Fig1A subplot
plt.subplot(1,2,1)
Fig1A_timeplot(metafile, plot_body_weight)
# Significance Markers
plt.annotate('*', (4.4, 80), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('#', (44.2, 365), fontsize=10, color = 'gray', fontweight='bold')
# Subplot Text Label
plt.figtext(0.03, 0.93, "A", fontsize = 15, color = "black", fontweight = "bold")

#plt.text(-7.5, 380, 'A', fontsize=15, fontweight='bold')

# Create Fig1B subplot
plt.subplot(1,2,2)
Fig1B_boxplot(master_data.set_index("Rat"), plot_parameters)
# Significance Markers
plt.annotate('*', (1.96, 26.8), fontsize=15, color = 'black', fontweight='bold')
# Subplot Text Label
plt.figtext(0.52, 0.93, "B", fontsize = 15, color = "black", fontweight = "bold")

#plt.text(-0.8, 28, 'B', fontsize=15, fontweight='bold')

# Clean up and save the figure
sns.despine()
plt.tight_layout()

plt.savefig('Figures_And_Analysis/Fig1.tif', dpi = 1000)


#----------------------------------------------------------
# Figure1 Statistical Analysis
#----------------------------------------------------------
# Modify Raw Data
body_weight.set_index("Rat", inplace = True)
body_weight['diet_and_schedule'] = body_weight["Diet"].astype(str) +" "+ body_weight["Feeding"].astype(str)

# Fig1A - preTRF 
# Hold results in dictionary to send to CSV File
cont_hfhs_t_test_results = {}

daynumber = 1
for day in plot_body_weight.index:
    groupa = body_weight.where((body_weight.diet_and_schedule == "control ad lib") | (body_weight.diet_and_schedule == "control restriction"))[day].dropna()
    groupb = body_weight.where((body_weight.diet_and_schedule == "HFHS ad lib") | (body_weight.diet_and_schedule == "HFHS restriction"))[day].dropna()
    # Control AdLib + Control Restricted vs HFHS AdLib + HFHS Restricted
    cont_hfhs_t_test_results["Day " + str(daynumber) + ": " + day + " - Control AdLib + Control Restricted vs HFHS AdLib + HFHS Restricted"] = stats.ttest_ind(groupa,groupb)
    daynumber += 1
    
# Control AdLib + Control Restricted vs HFHS AdLib + HFHS Restricted Results
cont_hfhs_t_test_results_df = pd.DataFrame.from_dict(cont_hfhs_t_test_results, orient='Index')
cont_hfhs_t_test_results_df.columns = ['statistic','pvalue']
# Send Results to CSV File
cont_hfhs_t_test_results_df.to_csv("Figures_And_Analysis/Fig1A_T_Test_preTRF.csv")

# Fig1A - postTRF
body_weight_anova_results = pd.DataFrame()

# Run ANOVA and Tukey of body weight for each of 4 diet groups every day
daynumber = 1
for day in plot_body_weight.index:
    result = day_anova_analysis(day, body_weight)
    result.iloc[0, -1] = day
    result.iloc[1, -1] = "Day: " + str(daynumber)
    body_weight_anova_results = body_weight_anova_results.append(result)
    daynumber += 1
# Send Results to CSV File
body_weight_anova_results.fillna("").rename(index={0:'', 1:'', 2:'', 3:'', 4:'', 5:''}).to_csv("Figures_And_Analysis/Fig1A_ANOVA_and_TukeyHSD_postTRF.csv")

# Fig1B ANOVA analysis
total_fat_mass_anova = metabolite_anova_analysis("total_fat_pad", master_data.set_index("Rat"))

# Send Results to CSV File
total_fat_mass_anova.fillna("").rename(index={0:'', 1:'', 2:'', 3:'', 4:'', 5:''}).to_csv("Figures_And_Analysis/Fig1B_ANOVA_and_TukeyHSD.csv")


#----------------------------------------------------------
# Figure2 Generation
#----------------------------------------------------------

# Figure 2 Size
plt.figure(figsize = (7.48, 2.5))

# LIVER WEIGHT
plt.subplot(1, 4, 4)
Fig2_boxplot(master_data.liver_weight, "g", "Liver Mass")
# Subplot Text Label
plt.figtext(0.64, 0.93, "D", fontsize = 15, color = "black", fontweight = "bold")

# Create Legend
make_legend()

# TRIGLYCERIDE
plt.subplot(1, 4, 3)
Fig2_boxplot(master_data.Triglyceride, "mg/mL", "Triglyceride")
# Significance Markers
plt.annotate('*', (1.85, 4.7), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('#', (2.8, 3.5), fontsize=10, color = 'black', fontweight='bold')
# Subplot Text Label
plt.figtext(0.44, 0.93, "C", fontsize = 15, color = "black", fontweight = "bold")

# ADIPONECTIN
plt.subplot(1, 4, 2)
Fig2_boxplot(master_data.Adiponectin, "mcg/mL", "Adiponectin")
# Increase number of yticks
plt.yticks(np.arange(4, 10, 1))
# Significance Markers
plt.annotate('#', (0.8, 9.5), fontsize=10, color = 'black', fontweight='bold')
plt.annotate('*', (2.85, 7.5), fontsize=15, color = 'black', fontweight='bold')
# Subplot Text Label
plt.figtext(0.23, 0.93, "B", fontsize = 15, color = "black", fontweight = "bold")

# LEPTIN
plt.subplot(1, 4, 1)
Fig2_boxplot(master_data.Leptin, "mcg/mL", "Leptin")
# Significance Markers
plt.annotate('#', (2.8, 2.1), fontsize=10, color = 'black', fontweight='bold')
# Subplot Text Label
plt.figtext(0.015, 0.93, "A", fontsize = 15, color = "black", fontweight = "bold")


plt.savefig("Figures_And_Analysis/Fig2.tif", dpi = 1000)


#----------------------------------------------------------
# Figure2 Statistical Analysis
#----------------------------------------------------------
metabolites_hormones = ['Leptin', 'Adiponectin', 'Triglyceride', 'liver_weight']

metabolite_results = pd.DataFrame()

# ANOVA and Tukey for all 4 metabolites and liver weight
for group in metabolites_hormones:
    result = metabolite_anova_analysis(group, master_data.set_index("Rat"))

    result.iloc[0, -1] = group
    metabolite_results = metabolite_results.append(result)

# Send Results to CSV File
metabolite_results.fillna("").rename(index={0:'', 1:'', 2:'', 3:'', 4:'', 5:''}).to_csv("Figures_And_Analysis/Fig2_ANOVA_and_Tukey.csv")



#----------------------------------------------------------
# Figure3 Generation
#----------------------------------------------------------
# Modify raw data for figures
# Combine number of seconds in dark and light periods together into new column called "total_food"
feeding_data['total_food'] = feeding_data['light_food'] + feeding_data['dark_food']

# Combine number of seconds in dark and light periods together into new column called "total_food"
sucrose_data['total_sucrose'] = sucrose_data['light_sucrose'] + sucrose_data['dark_sucrose']

# Create dataframe with total amount of time spent drinking sucrose AND feeding
sucrose_and_feeding_data = feeding_data.drop(["group"], axis = 1).rename(columns={"light_food": "light", "dark_food": "dark", "total_food": "total"})
# Combine time spent feeding with time drinking sucrose 
sucrose_and_feeding_data = sucrose_and_feeding_data.add(sucrose_data.drop(["group"], axis = 1).rename(columns={"light_sucrose": "light", "dark_sucrose": "dark", "total_sucrose": "total"}), fill_value = 0)
sucrose_and_feeding_data = sucrose_and_feeding_data.astype(int)
sucrose_and_feeding_data["group"] = feeding_data["group"]

# Create dataframe with ratios spent drinking sucrose AND feeding
sucrose_and_feeding_data_ratio = sucrose_and_feeding_data.copy()
sucrose_and_feeding_data_ratio["light"] = sucrose_and_feeding_data["light"]/sucrose_and_feeding_data["total"]
sucrose_and_feeding_data_ratio["dark"] = sucrose_and_feeding_data["dark"]/sucrose_and_feeding_data["total"]
sucrose_and_feeding_data_ratio["total"] = sucrose_and_feeding_data["total"]/sucrose_and_feeding_data["total"]


# Create a dataframe that combines the "dark" and "light" calorie-consuming hourly values into one column - for simple plotting
# Create an empty dataframe
plot_feeding_frame = pd.DataFrame()
# Combine/Merge the hourly sucrose AND feeding values from dark and light phase into one column
plot_feeding_frame["Consumption_Rate"] = pd.concat([sucrose_and_feeding_data["dark"], sucrose_and_feeding_data["light"]])
# Add the diet "group" column - add twice because combining 2 phases
plot_feeding_frame["group"] = pd.concat([sucrose_and_feeding_data["group"], sucrose_and_feeding_data["group"]])
# Create a new column with just the label "Night" or "Day" for all of the column values
plot_feeding_frame["phase"] = pd.concat([sucrose_and_feeding_data["group"].replace(sucrose_and_feeding_data["group"].values, "Night"), sucrose_and_feeding_data["group"].replace(sucrose_and_feeding_data["group"].values, "Day")])
# Keep only the ad lib animals
plot_feeding_frame = plot_feeding_frame.where((plot_feeding_frame.group == "HFHS ad lib") | (plot_feeding_frame.group == "control ad lib")).dropna()
# Make a normal index that makes it easy to index
plot_feeding_frame = plot_feeding_frame.reset_index(drop = True)

# Create a custom plot parameters for this barplot figure
barplot_plot_parameters = plot_parameters.reindex(["control restriction", "HFHS restriction", "control ad lib", "HFHS ad lib"]).iloc[-2:]
# Add custom edge colors
barplot_plot_parameters["edgecolors"] = ["black", "darkred"]

# Figure 3 Size
plt.figure(figsize=(7.48, 2.5))

# Figure 3A
plt.subplot(1,2,1)
Fig3A_boxplot(sucrose_and_feeding_data, 'total', "Total Time Consuming \n Calories (sec)", plot_parameters)
plt.figtext(0.03, 0.93, "A", fontsize = 15, color = "black", fontweight = "bold")
# Significance Markers
plt.annotate('#', (0.95, 7000), fontsize=15, color = 'black', fontweight='bold')

# Figure 3B
plt.subplot(1,2,2)
Fig3B_barplot(plot_feeding_frame,  "Time Spent Consuming \n Calories (sec)", barplot_plot_parameters)
plt.figtext(0.52, 0.93, "B", fontsize = 15, color = "black", fontweight = "bold")
# Add Numbers
plt.annotate('29.47%', (0.09, 2000), fontsize=10, color = 'black', fontweight='bold')
plt.annotate('70.53%', (-0.3, 4100), fontsize=10, color = 'black', fontweight='bold')
plt.annotate('18.16%', (1.05, 1000), fontsize=10, color = 'red', fontweight='bold')
plt.annotate('81.84%', (0.65, 3300), fontsize=10, color = 'red', fontweight='bold')

# Significance Markers
plt.annotate('*', (0.17, 3000), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (1.17, 2000), fontsize=15, color = 'black', fontweight='bold')
plt.plot([0, 1], [4500, 4500], 'k-', lw=1)
plt.annotate('a', (0.45, 4600), fontsize=10, color = 'black', fontweight='bold')

plt.savefig('Figures_And_Analysis/Fig3.tif', dpi = 1000)


#----------------------------------------------------------
# Figure3 Statistical Analysis
#----------------------------------------------------------
# T-Tests for Fig3
results = pd.DataFrame(columns = ["group1", "group2", "t-statistic", "p-value"])

# T-Test #1: Control Ad Lib vs Control Restriction Total Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "control restriction").dropna())
results.loc[0] = ["control ad lib", "control restriction", t, p]
# T-Test #2: HFHS Ad Lib vs HFHS Restriction Total Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "HFHS ad lib").dropna(), 
                      sucrose_and_feeding_data["total"].where(sucrose_and_feeding_data.group == "HFHS restriction").dropna())
results.loc[1] = ["HFHS ad lib", "HFHS restriction", t, p]
# T-Test #3: Control Ad Lib Day vs Night Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["light"].where(sucrose_and_feeding_data.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data["dark"].where(sucrose_and_feeding_data.group == "control ad lib").dropna())
results.loc[2] = ["Control ad lib Day", "Control ad lib Night", t, p]
# T-Test #4: HFHS Ad Lib Day vs Night Total Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data["light"].where(sucrose_and_feeding_data.group == "HFHS ad lib").dropna(), 
                      sucrose_and_feeding_data["dark"].where(sucrose_and_feeding_data.group == "HFHS ad lib").dropna())
results.loc[3] = ["HFHS ad lib Day", "HFHS ad lib Night", t, p]
# T-Test #5 Control Ad Lib Day Ratio vs HFHS Ad Lib Day Ratio Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data_ratio["light"].where(sucrose_and_feeding_data_ratio.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data_ratio["light"].where(sucrose_and_feeding_data_ratio.group == "HFHS ad lib").dropna())
results.loc[4] = ["control ad lib Day Ratio", "HFHS ad lib Day Ratio", t, p]

# T-Test #6 Control Ad Lib Night Ratio vs HFHS Ad Lib Night Ratio Calorie Consumption
t, p = stats.ttest_ind(sucrose_and_feeding_data_ratio["dark"].where(sucrose_and_feeding_data_ratio.group == "control ad lib").dropna(), 
                      sucrose_and_feeding_data_ratio["dark"].where(sucrose_and_feeding_data_ratio.group == "HFHS ad lib").dropna())
results.loc[5] = ["control ad lib Night Ratio", "HFHS ad lib Night Ratio", t, p]

results.set_index("group1").to_csv("Figures_And_Analysis/Fig3_T_Tests.csv")

#----------------------------------------------------------
# Figure4 Generation
#----------------------------------------------------------
# Figure 4 Size
f = plt.figure(figsize = (7.48, 7))

# Fig4A - Control AdLib
plt.subplot(3, 2, 1)
Fig4AD_timeplot(normalized_feeding["Control Ad Lib"], "0.1", "-")
# Remove x-axis and ticks for subplot
plt.xlabel('')
plt.xticks([])

## Remove '0' from y-axis
plt.gca().yaxis.get_major_ticks()[0].label1.set_visible(False)
plt.figtext(0.04, 0.97, "A", fontsize = 15, color = "black", fontweight = "bold")

# Fig4B - HFHS AdLib
plt.subplot(3, 2, 2)
Fig4AD_timeplot(normalized_feeding["HFHS Ad Lib"], "red", "-")
plt.xlabel('')
plt.xticks([])
# Remove y-axis and ticks for subplot
plt.ylabel('')
plt.yticks([])
plt.figtext(0.53, 0.97, "B", fontsize = 15, color = "black", fontweight = "bold")

# Fig4C - Control Restricted
plt.subplot(3, 2, 3)
Fig4AD_timeplot(normalized_feeding["Control Restricted"], "0.1", "--")
plt.xlabel('')
plt.xticks([])

## Remove '0' from y-axis
plt.gca().yaxis.get_major_ticks()[0].label1.set_visible(False)
plt.figtext(0.04, 0.67, "C", fontsize = 15, color = "black", fontweight = "bold")

# Fig4D - HFHS Restricted
plt.subplot(3, 2, 4)
Fig4AD_timeplot(normalized_feeding["HFHS Restricted"], "red", "--")
plt.ylabel('')
plt.yticks([])
plt.xlabel('')
plt.xticks([])
plt.figtext(0.53, 0.67, "D", fontsize = 15, color = "black", fontweight = "bold")
plt.tight_layout()

# Fig4E - Control Restrited - 8-Hour Period
plt.subplot(3, 2, 5)
Fig4EF_timeplot(feeding_hourly_frame.T.iloc[:-1, :], "control restriction", "0.1", video_metafile)
# Significance Markers
plt.annotate('*', (6.7, 220), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (7.7, 150), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (8.7, 220), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (9.7, 240), fontsize=15, color = 'black', fontweight='bold')
plt.figtext(0.04, 0.36, "E", fontsize = 15, color = "black", fontweight = "bold")

# Fig4F - HFHS Restrited - 8-Hour Period
plt.subplot(3, 2, 6)
Fig4EF_timeplot(feeding_hourly_frame.T.iloc[:-1, :], "HFHS restriction", "red", video_metafile)
plt.ylabel('')
plt.yticks([])
# Significance Markers
plt.annotate('*', (5.7, 200), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (6.7, 210), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (8.5, 160), fontsize=15, color = 'black', fontweight='bold')
plt.figtext(0.53, 0.36, "F", fontsize = 15, color = "black", fontweight = "bold")

plt.tight_layout()
plt.savefig("Figures_And_Analysis/Fig4.tif", dpi = 1000)


#----------------------------------------------------------
# Figure4 Statistical Analysis
#----------------------------------------------------------
# Running T-Tests to Compare All Hours Against the First Hour of Binge-Eating
first_hour_results = pd.DataFrame(columns = ["diet", "hour1", "hour2", "t-statistic", "p-value"])
diet_groups = ["control restriction", "HFHS restriction"]
i = 0
hours_to_check = ["0:00", "1:00","2:00", "3:00","4:00", "5:00","6:00"]
for group in diet_groups:
    ids = video_metafile[video_metafile == group].index
    for hour in feeding_hourly_frame.iloc[:, :-1]:
        feeding_series = feeding_hourly_frame.iloc[:, :-1].loc[ids]
        if feeding_series[hour].isnull().all() or hour not in hours_to_check:
            pass
        else:
            t, p = stats.ttest_ind(feeding_series["23:00"].dropna(), 
                          feeding_series[hour].dropna())
            first_hour_results.loc[i] = [group, "23:00", hour, t, p]
            i += 1
            
first_hour_results.set_index("diet").to_csv("Figures_and_Analysis/Fig4_T_Tests.csv")



#----------------------------------------------------------
# Figure5 Generation
#----------------------------------------------------------
# Select only the final 3 hours of interest (from 4:00 to 7:00)
final_hours_of_interest = feeding_hourly_frame[["4:00", "5:00", "6:00", "group"]]
final_hours_of_interest = final_hours_of_interest[(final_hours_of_interest["group"] == "control restriction") | (final_hours_of_interest["group"] == "HFHS restriction")]

# Create a dataframe that combines the final 3 hours of feeding into one column - for simple plotting and ANOVA
# Create an empty dataframe
final_feeding_frame = pd.DataFrame()
# Combine/Merge the hourly feeding values from final 3 hours into one column
final_feeding_frame["Consumption_Rate"] = pd.concat([final_hours_of_interest["4:00"],
                                            final_hours_of_interest["5:00"],
                                            final_hours_of_interest["6:00"]])
# Add the diet "group" column into this dataframe
final_feeding_frame["group"] = pd.concat([final_hours_of_interest["group"],
                                 final_hours_of_interest["group"],
                                 final_hours_of_interest["group"]])
# Create a new column with just the label "6th", "7th" or "8th" for all of the column values
final_feeding_frame["phase"] = pd.concat([final_hours_of_interest["group"].replace(final_hours_of_interest["group"].values, "6th Hour"), 
                                 final_hours_of_interest["group"].replace(final_hours_of_interest["group"].values, "7th Hour"),
                                 final_hours_of_interest["group"].replace(final_hours_of_interest["group"].values, "8th Hour")])
# Sort values by alphabetical diet type and ascending hour
final_feeding_frame = final_feeding_frame.sort_values(["group", "phase"], ascending=[False, True]).reset_index(drop = True)
# Add column that combines diet type and hour
final_feeding_frame['group_and_phase'] = final_feeding_frame["group"].astype(str) +" "+ final_feeding_frame["phase"].astype(str)
final_feeding_frame = final_feeding_frame.dropna()

# Create a custom plot parameter for the barplot figure
final_barplot_plot_parameters = plot_parameters.reindex(["control ad lib", "HFHS ad lib", "control restriction", "HFHS restriction"]).iloc[-2:]
# Add custom edge colors
final_barplot_plot_parameters["edgecolors"] = ["grey", "red"]

# Figure 5 Size
plt.figure(figsize=(3.543, 2.5))

# Final 3 Hours
Fig5_barplot(final_feeding_frame, "Time Spent Feeding (sec)", final_barplot_plot_parameters)
# Increase number of yticks
plt.yticks(np.arange(0, 700, 100))
# Significance Markers
plt.annotate('ab', (1.225, 550), fontsize=10, color = 'black', fontweight='bold')

plt.savefig("Figures_And_Analysis/Fig5.tif", dpi = 1000)



#----------------------------------------------------------
# Figure5 Statistical Analysis
#----------------------------------------------------------
#----ANOVA for Final 3 Hours------   
# Perform 1-Way ANOVA and Tukey and place the results in a dataframe
result = activity_anova(final_feeding_frame)

result.to_csv("Figures_and_Analysis/Fig5_ANOVA_and_TukeyHSD.csv")



#----------------------------------------------------------
# Figure6 Generation
#----------------------------------------------------------
# Figure 6 Size
plt.figure(figsize = (3.543, 7))

# Fig6A - HFHS AdLib
plt.subplot(3, 1, 1)
Fig6AB_timeplot(normalized_sucrose["HFHS Ad Lib"], "red", "-")
# Remove x-axis and ticks for subplot
plt.xlabel('')
plt.xticks([])

# Remove leading 0
plt.gca().yaxis.get_major_ticks()[0].label1.set_visible(False)
plt.figtext(0.04, 0.97, "A", fontsize = 15, color = "black", fontweight = "bold")

# Fig6B - HFHS Restriction
plt.subplot(3, 1, 2)
Fig6AB_timeplot(normalized_sucrose["HFHS Restricted"], "red", "--")
# Remove x-axis and ticks for subplot
plt.xlabel('')
plt.xticks([])

## Remove leading 0
plt.gca().yaxis.get_major_ticks()[0].label1.set_visible(False)
plt.figtext(0.04, 0.67, "B", fontsize = 15, color = "black", fontweight = "bold")

# HFHS Restrited - Binge
plt.subplot(3, 1, 3)
Fig6C_timeplot(sucrose_hourly_frame.T.iloc[:-1, :], "HFHS restriction", "red", video_metafile)
# Significance Markers
plt.annotate('*', (3.7, 45), fontsize=15, color = 'black', fontweight='bold')
plt.annotate('*', (5.7, 75), fontsize=15, color = 'black', fontweight='bold')
plt.figtext(0.04, 0.36, "C", fontsize = 15, color = "black", fontweight = "bold")
plt.savefig("Figures_And_Analysis/Fig6.tif", dpi = 1000)



#----------------------------------------------------------
# Figure6 Statistical Analysis
#----------------------------------------------------------
# Running T-Tests to Compare All Hours Against the First Hour of Binge-Eating
first_hour_sucrose_results = pd.DataFrame(columns = ["diet", "hour1", "hour2", "t-statistic", "p-value"])
diet_groups = ["HFHS restriction"]
i = 0
hours_to_check = ["0:00", "1:00","2:00", "3:00","4:00", "5:00","6:00"]
for group in diet_groups:
    ids = video_metafile[video_metafile == group].index
    for hour in sucrose_hourly_frame.iloc[:, :-1]:
        sucrose_series = sucrose_hourly_frame.iloc[:, :-1].loc[ids]
        if sucrose_series[hour].isnull().all() or hour not in hours_to_check:
            pass
        else:
            t, p = stats.ttest_ind(sucrose_series["23:00"].dropna(), 
                          sucrose_series[hour].dropna())
            first_hour_sucrose_results.loc[i] = [group, "23:00", hour, t, p]
            i += 1
            
first_hour_sucrose_results.set_index("diet").to_csv("Figures_and_Analysis/Fig6_T_Tests.csv")



#----------------------------------------------------------
# Figure7 Generation
#----------------------------------------------------------
# Select only the final 3 hours of interest (from 4:00 to 7:00)
final_hours_of_interest = sucrose_hourly_frame[["4:00", "5:00", "6:00", "group"]]
final_hours_of_interest = final_hours_of_interest[(final_hours_of_interest["group"] == "HFHS ad lib") | (final_hours_of_interest["group"] == "HFHS restriction")]

# Create a dataframe that combines the final 3 hours of feeding into one column - for simple plotting and ANOVA
# Create an empty dataframe
final_sucrose_frame = pd.DataFrame()
# Combine/Merge the hourly feeding values from final 3 hours into one column
final_sucrose_frame["Consumption_Rate"] = pd.concat([final_hours_of_interest["4:00"],
                                            final_hours_of_interest["5:00"],
                                            final_hours_of_interest["6:00"]])
# Add the diet "group" column into this dataframe
final_sucrose_frame["group"] = pd.concat([final_hours_of_interest["group"],
                                 final_hours_of_interest["group"],
                                 final_hours_of_interest["group"]])
# Create a new column with just the label "6th", "7th" or "8th" for all of the column values
final_sucrose_frame["phase"] = pd.concat([final_hours_of_interest["group"].replace(final_hours_of_interest["group"].values, "6th Hour"), 
                                 final_hours_of_interest["group"].replace(final_hours_of_interest["group"].values, "7th Hour"),
                                 final_hours_of_interest["group"].replace(final_hours_of_interest["group"].values, "8th Hour")])
# Sort values by alphabetical diet type and ascending hour
final_sucrose_frame = final_sucrose_frame.sort_values(["group", "phase"], ascending=[True, True]).reset_index(drop = True)
# Add column that combines diet type and hour
final_sucrose_frame['group_and_phase'] = final_sucrose_frame["group"].astype(str) +" "+ final_sucrose_frame["phase"].astype(str)
final_sucrose_frame = final_sucrose_frame.dropna()

# Create a custom plot parameter for the barplot figure
final_barplot_plot_parameters = plot_parameters.reindex(["control ad lib", "control restriction", "HFHS ad lib", "HFHS restriction"]).iloc[-2:]
# Add custom edge colors
final_barplot_plot_parameters["edgecolors"] = ["darkred", "red"]

# Figure 7 Size
plt.figure(figsize=(3.543, 2.5))

# Final 3 Hours
Fig7_barplot(final_sucrose_frame, "Time Spent Drinking \nSucrose (sec)", final_barplot_plot_parameters)
# Increase number of yticks
plt.yticks(np.arange(0, 175, 25))

plt.savefig("Figures_And_Analysis/Fig7.tif", dpi = 1000)



#----------------------------------------------------------
# Figure7 Statistical Analysis
#----------------------------------------------------------
#----ANOVA for Final 3 Hours------   
# Perform 1-Way ANOVA and Tukey and place the results in a dataframe
result = activity_anova(final_sucrose_frame)

result.to_csv("Figures_and_Analysis/Fig7_ANOVA_and_TukeyHSD.csv")


#----------------------------------------------------------
# Figure8 Generation
#----------------------------------------------------------
metafile['group']=metafile.Diet+' '+metafile.Feeding

# Rearrange so that Oxtr is the last gene column
col_list = list(gene_data)
col_list[11], col_list[8] = col_list[8], col_list[11]
gene_data = gene_data.loc[:,col_list]


gene_list = gene_data.columns.unique()
# Remove outliers, that is the measurments which is larger than 7
for c in gene_list:
    # Find index of an outlier and replace it with NAN
    out_ind = gene_data[c][gene_data[c]>=7].index
    gene_data[c][out_ind ]=np.NaN
# Add experimental group as a column to the gene dataset
ids_in_gene_data = gene_data.index
gene_data['group'] = metafile.group.loc[ids_in_gene_data]
gene_data['diet'] = metafile.Diet.loc[ids_in_gene_data]
gene_data['feeding_schedule'] = metafile.Feeding.loc[ids_in_gene_data]

# Figure 8 Size
plt.figure(figsize = (7.48,7.48))

# Adjust subplot size
plt.subplots_adjust(wspace = 0.3 )
subplot_n=1
for c in gene_list[:-1]:
    plt.subplot(4,3,subplot_n)
    Fig8_boxplot(gene_data, plot_parameters, c)
    if subplot_n == 2:
        # Significance Markers for NPY
        plt.annotate('*', (2.9, 1.6), fontsize=15, color = 'black', fontweight='bold')
    if subplot_n == 6:
        # Significance Markers for Ghsr
        plt.annotate('#', (0.9, 2.3), fontsize=10, color = 'black', fontweight='bold')
    if subplot_n == 7:
        # Significance Markers for Insr
        plt.annotate('#', (0.9, 1.35), fontsize=10, color = 'black', fontweight='bold')
        plt.annotate('#', (2.9, 1.45), fontsize=10, color = 'black', fontweight='bold')
    if subplot_n == 8:
        # Significance Markers for Lepr
        plt.annotate('#', (0.9, 1.8), fontsize=10, color = 'black', fontweight='bold')
    
    subplot_n = subplot_n+1 
    

### Designate the last subplot for the legend
ax = plt.subplot(4,3,subplot_n)
# Remove the x- and y-ticks
plt.xticks([])
plt.yticks([])
# Remove the x- and y-axis lines
ax.set_frame_on(False)
make_gene_legend()

# Clean up plot
sns.despine()
plt.tight_layout()
plt.savefig('Figures_and_Analysis/Fig8.tiff', dpi = 1000)



#----------------------------------------------------------
# Figure8 Statistical Analysis
#----------------------------------------------------------
# Create a dictionary to hold MannU Whitney Results
feeding = metafile.Feeding.unique()
diet   = metafile.Diet.unique()
group_dict={}
for x in diet:
        for y in feeding:
            group = str(x)+' '+str(y)
            ids = gene_data[(gene_data.diet==x) & (gene_data.feeding_schedule==y)].index
            genes_by_group = gene_data.loc[ids]
            genes_by_group.dropna(inplace = True)
            group_dict[group]=genes_by_group
            
# MannU Whitney Analysis
groups = metafile.group.unique()
column_names = ["gene", "group1", "group2", "p_value"]
gene_df = pd.DataFrame(columns = column_names)
i=0
for c in gene_list:
    
    for x in groups:
        group1 = group_dict[x][c]
        
        for y in groups:
            if(y!= x):
                group2 = group_dict[y][c]
                u_statistic, pVal = stats.mannwhitneyu(group1, group2)
                gene_df.loc[i]=[c, x, y, pVal]
                i+=1
gene_df.set_index("gene").to_csv('Figures_and_Analysis/Fig8_Mann_Whitney.csv')

