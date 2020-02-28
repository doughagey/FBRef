#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 17:50:36 2019

@author: doug hagey
"""
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time

# Use selenium to get the FPL data from the fbref website and put it into a Pandas Dataframe
def webscraper(league, passing_url,shooting_url):
    try:
        print('Scraping data for',league)
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(passing_url)
        time.sleep(10)
        # Have to use header=1 because there are two headers on the passing table
        # NOT using header=1 will cause the column names to be oddly named and it won't merge properly later
        passing_df = pd.read_html(driver.page_source, header=1)[10]

        driver.get(shooting_url)
        time.sleep(10)
        #shooting_element = driver.find_element_by_xpath("//*[@id=\"stats_shooting\"]/tbody")
        shooting_df = pd.read_html(driver.page_source)[10]

        # Rename the df columns to something more useful by using a map vs. just renaming, which is dangerous if things move around
        passing_df = passing_df.rename(columns={'Pos':'Position','Ast':'Assists','A-xA':'Assists-xA','KP':'KeyPasses','Left':'Passes With LF', 'Right':'Passes with RF', 'FK':'Free Kick Passes', 'TB':'Through Ball Passes', 'CK':'Corner Kicks', 'TI':'Throw Ins', '1/3':'Passes into final third', 'PPA':'Passes Into Penalty Box', 'CrsPA':'Crosses into Penalty Box'})
        passing_df = passing_df[passing_df.Player != 'Player']
        # Get rid of the rows that have NaN as they are bogus and don't relate to players
        passing_df = passing_df.fillna(0)
        #print(passing_df.head(5))
        shooting_df = shooting_df.rename(columns={'Pos':'Position','Gls':'Goals','Sh':'Shots Total','FK':'FK Shots','SoT':'Shots on Target', 'FK':'FK Shots','SoT%':'Shots on Target %','Sh/90':'Shots per 90','SoT/90':'SOT per 90','G/Sh':'Goals per Shot','G/SoT':'Goals per SOT','npxG/Sh':'npxG per Shot','G-xG':'Goals minus xG','np:G-xG':'np Goals minus xG'})
        # Passing df has names that are duplicates because the top row was chopped off earlier, needed to rename them to clarify
        passing_df = passing_df.rename(columns={'Cmp.1':'Short Passes Completed','Att.1':'Short Attempted Passes','Cmp%.1':'Short Passes Completed%','Cmp.2':'Medium Passes Completed','Att.2':'Medium Passes Attempted','Cmp%.2':'Medium Passes Completed%','Cmp.3':'Long Passes Completed','Att.3':'Long Passes Attempted','Cmp%.3':'Long Passes Completed%','Cmp':'Total Passes Completed','Att':'Total Passes Attempted','Cmp%':'Total Passes Completed%'})
        shooting_df = shooting_df[shooting_df.Player != 'Player']

        # Get rid of the rows that have NaN as they are bogus and don't relate to players
        shooting_df = shooting_df.fillna(0)
        #print(shooting_df.head(5))
        
        #Replace Position indentifiers with something more useful
        shooting_df['Position'] = shooting_df['Position'].str.slice(0,2)
        position_map = {'DF':'DEF', 'FW':'FWD', 'MF':'MID'}
        shooting_df = shooting_df.replace({'Position': position_map})
        passing_df= passing_df.replace({'Position': position_map})
        #Drop the duplicate columns before merging
        passing_df.drop(['Player', 'Nation', 'Position','Squad', 'Age', 'Born', '90s','Matches'], axis=1, inplace=True)
        shooting_df.drop(['Matches'])

        #Merge the dataframes so that we have all the info together
        EPL_player_df = pd.merge(shooting_df, passing_df, on='Rk')
        #print(EPL_player_df.head(5))
        
        # Export to .csv so we can use in tableau]
        #assists_df.to_csv(league+'FBRef_Assists.csv', encoding='utf-8', index=False)
        #shooting_df.to_csv(league+'FBRef_Goals.csv', encoding='utf-8', index=False)
        print('Writing csv file for',league)
        EPL_player_df.to_csv('FBRef_'+league+'_Player_Data.csv', encoding='utf-8', index=False)
        driver.close()
    
    except Exception as e:
        print(e)
        driver.close()
        time.sleep(5)

EPL = webscraper('EPL', 'https://fbref.com/en/comps/9/passing/Premier-League-Stats', 'https://fbref.com/en/comps/9/shooting/Premier-League-Stats')
LaLiga = webscraper('LaLiga', 'https://fbref.com/en/comps/12/passing/La-Liga-Stats','https://fbref.com/en/comps/12/shooting/La-Liga-Stats')
Bundesliga = webscraper('BundesLiga', 'https://fbref.com/en/comps/20/passing/Bundesliga-Stats', 'https://fbref.com/en/comps/20/shooting/Bundesliga-Stats')
SerieA = webscraper('SerieA', 'https://fbref.com/en/comps/11/passing/Serie-A-Stats', 'https://fbref.com/en/comps/11/shooting/Serie-A-Stats')
Ligue1 = webscraper('Ligue1', 'https://fbref.com/en/comps/13/passing/Ligue-1-Stats', 'https://fbref.com/en/comps/13/shooting/Ligue-1-Stats')
ChampionsLeague = webscraper('ChampionsLeague', 'https://fbref.com/en/comps/8/passing/Champions-League-Stats', 'https://fbref.com/en/comps/8/shooting/Champions-League-Stats')

