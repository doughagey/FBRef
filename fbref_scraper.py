#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 17:50:36 2019

@author: doug hagey
"""
from selenium import webdriver
import pandas as pd

# Use selenium to get the FPL data from the fbref website and put it into a Pandas Dataframe
def webscraper(league, passing_url,shooting_url):
    driver = webdriver.Firefox()
    driver.get(passing_url)
    #info = driver.find_element_by_xpath("//*[@id=\"stats_standard\"]/tbody")
    assists_df = pd.read_html(driver.page_source)[10]
    
    driver.get(shooting_url)
    #info = driver.find_element_by_xpath("//*[@id=\"stats_standard\"]/tbody")
    shooting_df = pd.read_html(driver.page_source)[10]
    driver.close()
    
    # Rename the df columns to something more useful
    assists_df.columns =['Rk','Player','Nation','Position','Squad','90s','Assists','xA', 'Assists-xA','KeyPasses', 'Total Completed Passes', 'Total Attempted Passes', 'Total Pass Completion %', 'Short Completed Passes', 'Short Attempted Passes', 'Short Pass Completion %', 'Medium Completed Passes', 'Medium Attempted Passes', 'Medium Pass Completion %', 'Long Completed Passes', 'Long Attempted Passes', 'Long Pass Completion %', 'Passes to Left', 'Passes to Right', 'Free Kick Passes', 'Through Ball Passes', 'Corner Kicks', 'Throw In Passes', 'Passes into final third', 'Passes Into Penalty Box', 'Crosses into Penalty Box', 'Matches']
    assists_df = assists_df[assists_df.Player != 'Player']
    # Get rid of the rows that have NaN as they are bogus and don't relate to players
    assists_df = assists_df.fillna(0)
    
    shooting_df.columns =['Rk','Player','Nation','Position','Squad','90s','Goals','PK', 'PK Attempts','Shots Total', 'Shots on Target', 'FK Shots', 'Shots on Target %', 'Shots per 90', 'SOT per 90', 'Goals per Shot', 'Goals per SOT', 'xG', 'npxG', 'npxG per Shot', 'Goals minus xG', 'np Goals minus xG ', 'Matches']
    shooting_df = shooting_df[shooting_df.Player != 'Player']
    # Get rid of the rows that have NaN as they are bogus and don't relate to players
    shooting_df = shooting_df.fillna(0)
    
    #Cut out the parts we really don't need
    assists_df = assists_df[['Rk','Player','Position','Squad','90s','Assists','xA', 'Assists-xA','KeyPasses', 'Total Completed Passes', 'Total Attempted Passes', 'Total Pass Completion %', 'Short Completed Passes', 'Short Attempted Passes', 'Short Pass Completion %', 'Medium Completed Passes', 'Medium Attempted Passes', 'Medium Pass Completion %', 'Long Completed Passes', 'Long Attempted Passes', 'Long Pass Completion %', 'Through Ball Passes', 'Corner Kicks', 'Passes into final third', 'Passes Into Penalty Box', 'Crosses into Penalty Box']]
    shooting_df = shooting_df[['Rk','Goals','PK', 'PK Attempts','Shots Total', 'Shots on Target', 'FK Shots', 'Shots on Target %', 'Shots per 90', 'SOT per 90', 'Goals per Shot', 'Goals per SOT', 'xG', 'npxG', 'npxG per Shot', 'Goals minus xG', 'np Goals minus xG ']]
    
    #Replace Position indentifiers with something more useful
    assists_df['Position'] = assists_df['Position'].str.slice(0,2)
    position_map = {'DF':'DEF', 'FW':'FWD', 'MF':'MID'}
    assists_df = assists_df.replace({'Position': position_map})
    
    #Merge the dataframes so that we have all the info together
    EPL_player_df = pd.merge(assists_df, shooting_df, on='Rk')
    
    # Export to .csv so we can use in tableau]
    #assists_df.to_csv(league+'FBRef_Assists.csv', encoding='utf-8', index=False)
    #shooting_df.to_csv(league+'FBRef_Goals.csv', encoding='utf-8', index=False)
    EPL_player_df.to_csv('FBRef_'+league+'_Player_Data.csv', encoding='utf-8', index=False)


EPL = webscraper('EPL', 'https://fbref.com/en/comps/9/passing/Premier-League-Stats', 'https://fbref.com/en/comps/9/shooting/Premier-League-Stats')
LaLiga = webscraper('LaLiga', 'https://fbref.com/en/comps/12/passing/La-Liga-Stats','https://fbref.com/en/comps/12/shooting/La-Liga-Stats')
Bundesliga = webscraper('BundesLiga', 'https://fbref.com/en/comps/20/passing/Bundesliga-Stats', 'https://fbref.com/en/comps/20/shooting/Bundesliga-Stats')
