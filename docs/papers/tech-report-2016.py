
# coding: utf-8

# This page contains code associated with the following technical report:
# 
# Lee, Jackson L., Ross Burkholder, Gallagher B. Flinn, and Emily R. Coppess. 2016. [Working with CHAT transcripts in Python](http://www.cs.uchicago.edu/research/publications/techreports/TR-2016-02). Technical Report TR-2016-02, Department of Computer Science, University of Chicago.
# 
# Questions and comments can be directed to [Jackson Lee](http://jacksonllee.com/).
# 
# All code runs in Python 3.4+. [Download](tech-report-2016.py) this page as a `.py` Python script.

# Importing all necessary libraries
# ===================

# In[1]:

get_ipython().magic('matplotlib inline')

# libraries from the Python standard library
import os
from collections import Counter

# libraries for scientific computing and statistics
import pandas as pd
from scipy.stats.stats import pearsonr
import seaborn as sns
sns.set(color_codes=True)

# libraries for linguistic research
import pylangacq as pla
import pycantonese as pc


# Part 1: Computing MLUm
# ===============

# Reading CHAT transcripts of Eve in Brown
# -----------------------------------------------
# 
# We assume that Eve's data from the Brown portion of CHILDES ([source](http://childes.psy.cmu.edu/data/Eng-NA-MOR/Brown.zip); accessed in January 2016) are available at the current directory.

# In[2]:

eve = pla.read_chat('Brown/Eve/*.cha')  # reading in all 20 files from eve01.cha to eve20.cha


# Getting information of interest
# ------------------------------------
# 
# 1. filenames
# 2. age (in months) of Eve's in each CHAT file
# 3. mean length of utterance in morphemes (MLUm) of each file 

# In[3]:

eve_filenames = eve.filenames(sorted_by_age=True)  # absolute-path filenames sorted by age
eve_ages = eve.age(month=True)  # dict(filename: age in months)
eve_MLUs = eve.MLUm()  # dict(filename: MLUm)
eve_age_MLU_pairs = [(eve_ages[fn], eve_MLUs[fn]) for fn in eve_filenames]  # list of (age, MLUm)


# Testing correlation (using Pearson's *r*)
# -----------------------------------------------

# In[4]:

pearsonr(*zip(*eve_age_MLU_pairs))  # passing (list of ages, list of MLUs) to pearsonr()


# **Between age and MLUm:** Significant (positive) correlation (r = 0.84, p < 0.001)

# Visualizing the correlation
# -------------------------------

# In[5]:

eve_MLU_df = pd.DataFrame({'Eve\'s age in months': [age for age, _ in eve_age_MLU_pairs],
                           'MLUm': [MLU for _, MLU in eve_age_MLU_pairs]})


# In[6]:

eve_MLU_plot = sns.regplot(x='Eve\'s age in months', y='MLUm', data=eve_MLU_df)


# In[7]:

eve_MLU_plot.get_figure().savefig('Eve-MLU.pdf')  # save the figure for the tech report


# Printing LaTeX table code for the technical report
# ----------------------------------------------------------

# In[8]:

for fn in sorted(eve_filenames):
    print('{{\\tt {}}} & {} & {:.3f} \\\\'.format(os.path.basename(fn), eve_ages[fn], eve_MLUs[fn]))


# Part 2: Language dominance
# ================

# Reading CHAT transcripts from YipMatthews
# -----------------------------------------------
# 
# We assume that the YipMatthews datasets from the Biling portion of CHILDES ([source](http://childes.psy.cmu.edu/data/Biling/YipMatthews.zip); accessed in January 2016) are available at the current directory.
# 
# We are using the data from the three siblings of Timmy (eldest), Sophie, and Alicia (youngest) acquiring Cantonese and English simultaneously.

# In[9]:

tim_can = pla.read_chat('YipMatthews/CanWork/TimCan/*.cha')
sophie_can = pla.read_chat('YipMatthews/CanWork/SophieCan/*.cha')
alicia_can = pla.read_chat('YipMatthews/Can/AliciaCan/*.cha')

tim_eng = pla.read_chat('YipMatthews/Eng/TimEng/*.cha')
sophie_eng = pla.read_chat('YipMatthews/Eng/SophieEng/*.cha')
alicia_eng = pla.read_chat('YipMatthews/Eng/AliciaEng/*.cha')


# Visualizing language dominance by MLUw
# --------------------------------------------
# 
# We explore Cantonese-English language dominance (measured by MLUw) of the three siblings.

# In[10]:

def visualize_can_eng_MLUw(child_name, can_reader, eng_reader, legend=True):
    x_label = '{}\'s age in months'.format(child_name)
    
    can_filenames = can_reader.filenames(sorted_by_age=True)
    can_ages = can_reader.age(month=True)
    can_MLUs = can_reader.MLUw()
    
    eng_filenames = eng_reader.filenames(sorted_by_age=True)
    eng_ages = eng_reader.age(month=True)
    eng_MLUs = eng_reader.MLUw()
    
    df = pd.DataFrame({x_label: [can_ages[fn] for fn in can_filenames] + [eng_ages[fn] for fn in eng_filenames],
                       'MLUw': [can_MLUs[fn] for fn in can_filenames] + [eng_MLUs[fn] for fn in eng_filenames],
                       'Language': ['Cantonese']*len(can_reader) + ['English']*len(eng_reader)})
    
    MLU_plot = sns.lmplot(x=x_label, y='MLUw', hue='Language', data=df, markers=['o', 'x'],
                          legend=legend, legend_out=False)
    MLU_plot.set(xlim=(10, 45), ylim=(0, 4.5))
    MLU_plot.savefig('{}-MLU.pdf'.format(child_name))


# In[11]:

visualize_can_eng_MLUw('Timmy', tim_can, tim_eng, legend=False)  # figure saved: Timmy-MLU.pdf


# In[12]:

visualize_can_eng_MLUw('Sophie', sophie_can, sophie_eng)  # figure saved: Sophie-MLU.pdf


# In[13]:

visualize_can_eng_MLUw('Alicia', alicia_can, alicia_eng, legend=False)  # figure saved: Alicia-MLU.pdf


# Part 3: Phonological development
# ===================
# 
# Reading CHAT transcripts from LeeWongLeung
# ------------------------------------------------
# 
# We assume that the LeeWongLeung datasets from the EastAsian/Cantonese portion of CHILDES ([source](http://childes.psy.cmu.edu/data/EastAsian/Cantonese/LeeWongLeung.zip); accessed in January 2016) are available at the current directory.
# 
# We are using the data for the child "mhz".

# In[14]:

mhz = pla.read_chat('LeeWongLeung/mhz/*.cha')


# Getting information of interest
# ------------------------------------
# 
# 1. filenames
# 2. ages (in months)
# 3. list of tagged words for each file; a tagged word is a tuple of (word, pos, mor, rel)

# In[15]:

mhz_filenames = mhz.filenames(sorted_by_age=True)  # list of absolute-path filenames sorted by age
mhz_ages = mhz.age(month=True)  # dict(filename: age in months)
mhz_ages_sorted = [mhz_ages[fn] for fn in mhz_filenames]  # list of ages sorted by mhz_filenames
mhz_tagged_words = mhz.tagged_words(by_files=True, participant='CHI')  # dict(filename: list of tagged words)


# Counting tones in each file
# -------------------------------
# 
# Cantonese has six tones. Cantonese datasets in CHILDES simply have them transcribed as {1, 2, 3, 4, 5, 6}, following the convention in Cantonese linguistics.

# In[16]:

age_to_tones = dict()  # dict(age: dict(tone: tone count))

for fn in mhz_filenames:
    tagged_words = mhz_tagged_words[fn]
    age = mhz_ages[fn]
    
    age_to_tones[age] = Counter()
    
    for tagged_word in tagged_words:
        
        # jyutping should be like "gaa1jau2" (two syllables), "ngo5" (one syllable) etc
        mor = tagged_word[2]
        jyutping, _, _ = mor.partition('-')
        jyutping, _, _ = jyutping.partition('&')

        if not jyutping:
            continue
        
        # use PyCantonese to parse the "jyutping" str
        try:
            jyutping_parsed_list = pc.parse_jyutping(jyutping)
        except:
            continue
        
        for jyutping_parsed in jyutping_parsed_list:
            _, _, _, tone = jyutping_parsed  # (onset, nucleus, coda, tone)
            age_to_tones[age][tone] += 1


# Creating the dataframe for plotting the desired heatmap
# ---------------------------------------------------------------
# 
# The dataframe has three columns and is created by `data_dict`.

# In[17]:

data_dict = {'MHZ\'s age in months': list(),
             'Tone': list(),
             'Count': list(),
            }

for age in age_to_tones:
    for tone in age_to_tones[age]:
        count_ = age_to_tones[age][tone]
        data_dict['MHZ\'s age in months'].append(round(age, 1))
        data_dict['Tone'].append(int(tone))
        data_dict['Count'].append(count_)
        
df = pd.DataFrame(data_dict)
df_pivot = df.pivot('Tone', 'MHZ\'s age in months', 'Count')


# Plotting the heatmap
# -----------------------

# In[18]:

mhz_heatmap = sns.heatmap(df_pivot, annot=True, fmt='.3g', linewidths=0.1)
mhz_heatmap.get_figure().savefig('MHZ-Tone.pdf')

