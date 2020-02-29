#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 17:50:36 2019

@author: doug hagey
"""

import pandas as pd
import requests

# Use requests to get the FPL data from the fbref website and put it into a Pandas Dataframe
def webscraper(league, passing_url,shooting_url, misc_url):
    try:
        print('Scraping data for',league)
        
        # Scrape data from passing URL
        print('    Scraping Passing Table')
        page_source = requests.get(passing_url)
        page_replace_open_tag = page_source.text.replace('<!--\n   <div class="table_outer_container"','<div class ="table_outer_container">')
        page_good_tags = page_replace_open_tag.replace('</div>\n-->','</div>')
        passing_df = pd.read_html(page_good_tags, header=1)[1]
        print('        Found',len(passing_df.columns),'columns of data')
        if len(passing_df.columns)<3 and len(passing_df.columns)>0:
            print('    Was not able to load table')


        # Scrape data from shooting URL
        print('    Scraping Shooting Table')
        page_source = requests.get(shooting_url)
        page_replace_open_tag = page_source.text.replace('<!--\n   <div class="table_outer_container"','<div class ="table_outer_container">')
        page_good_tags = page_replace_open_tag.replace('</div>\n-->','</div>')
        shooting_df = pd.read_html(page_good_tags)[1]
        print('        Found',len(shooting_df.columns),'columns of data')
        if len(shooting_df.columns)<3 and len(shooting_df.columns)>0:
            print('    Was not able to load table')

        #Scrape data from misc URL
        print('    Scraping Misc Table')
        # This page also has an additional header we need to ignore
        page_source = requests.get(misc_url)
        page_replace_open_tag = page_source.text.replace('<!--\n   <div class="table_outer_container"','<div class ="table_outer_container">')
        page_good_tags = page_replace_open_tag.replace('</div>\n-->','</div>')
        misc_df = pd.read_html(page_good_tags, header=1)[1]
        print('        Found',len(misc_df.columns),'columns of data')
        if len(misc_df.columns)<3 and len(misc_df.columns)>0:
            print('    Was not able to load table')

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
        misc_df = misc_df.rename(columns={'Pos':'Position','Fls':'FoulsCommitted','Fld':'FoulsDrawn','Off':'Offsides','Crs':'Crosses', 'TklW':'SuccessfulTackles','Int':'Interceptions','Succ':'SuccessfulDribbles','Att':'AttemptedDribbles','Succ%':'SuccessfulDribbles%','#Pl':'PlayersDribbledPast','Megs':'Nutmegs','Tkl':'DribblersTackled','Att.1':'DribblesContested','Tkl%':'%DribblersTackled','Past':'DribbledPastByOpponent'})
        misc_df = misc_df[misc_df.Player != 'Player']

        # Get rid of the rows that have NaN as they are bogus and don't relate to players
        shooting_df = shooting_df.fillna(0)
        
        #Replace Position indentifiers with something more useful
        shooting_df['Position'] = shooting_df['Position'].str.slice(0,2)
        position_map = {'DF':'DEF', 'FW':'FWD', 'MF':'MID'}
        shooting_df = shooting_df.replace({'Position': position_map})
        passing_df= passing_df.replace({'Position': position_map})
        
        #Drop the duplicate columns before merging
        passing_df.drop(['Nation', 'Position','Squad', 'Age', 'Born', '90s','Matches'], axis=1, inplace=True)
        shooting_df.drop(['Matches'], axis=1, inplace=True)
        misc_df.drop(['Nation', 'Position','Squad', 'Age', 'Born', '90s','Matches'], axis=1, inplace=True)

        #Merge the dataframes so that we have all the info together - on requires a list in brackets
        EPL_player_df = pd.merge(shooting_df, passing_df, on=['Rk','Player'])
        EPL_player_df = pd.merge(EPL_player_df, misc_df, on=['Rk','Player'])
        #print(EPL_player_df.head(5))
        
        # Export to .csv so we can use in tableau]
        print('Writing csv file for',league)
        EPL_player_df.to_csv('FBRef_'+league+'_Player_Data.csv', encoding='utf-8', index=False)

    except Exception as e:
        print(e)


print('Which league do you want to scrape FBRef.com for?')
print('1 - English Premier League')
print('2 - La Liga')
print('3 - Bundesliga')
print('4 - Serie A')
print('5 - Ligue 1')
print('6 - Champions League')
league = input('Type a single league number or hit enter for all leagues:')

if len(league)<1:
    EPL = webscraper('EPL', 'https://fbref.com/en/comps/9/passing/Premier-League-Stats', 'https://fbref.com/en/comps/9/shooting/Premier-League-Stats','https://fbref.com/en/comps/9/misc/Premier-League-Stats')
    LaLiga = webscraper('LaLiga', 'https://fbref.com/en/comps/12/passing/La-Liga-Stats','https://fbref.com/en/comps/12/shooting/La-Liga-Stats','https://fbref.com/en/comps/12/misc/La-Liga-Stats')
    Bundesliga = webscraper('BundesLiga', 'https://fbref.com/en/comps/20/passing/Bundesliga-Stats', 'https://fbref.com/en/comps/20/shooting/Bundesliga-Stats','https://fbref.com/en/comps/20/misc/Bundesliga-Stats')
    SerieA = webscraper('SerieA', 'https://fbref.com/en/comps/11/passing/Serie-A-Stats', 'https://fbref.com/en/comps/11/shooting/Serie-A-Stats','https://fbref.com/en/comps/11/misc/Serie-A-Stats')
    Ligue1 = webscraper('Ligue1', 'https://fbref.com/en/comps/13/passing/Ligue-1-Stats', 'https://fbref.com/en/comps/13/shooting/Ligue-1-Stats','https://fbref.com/en/comps/13/misc/Ligue-1-Stats')
    ChampionsLeague = webscraper('ChampionsLeague', 'https://fbref.com/en/comps/8/passing/Champions-League-Stats', 'https://fbref.com/en/comps/8/shooting/Champions-League-Stats','https://fbref.com/en/comps/8/misc/Champions-League-Stats')
elif league == '1':
    EPL = webscraper('EPL', 'https://fbref.com/en/comps/9/passing/Premier-League-Stats', 'https://fbref.com/en/comps/9/shooting/Premier-League-Stats','https://fbref.com/en/comps/9/misc/Premier-League-Stats')
elif league == '2':
    LaLiga = webscraper('LaLiga', 'https://fbref.com/en/comps/12/passing/La-Liga-Stats','https://fbref.com/en/comps/12/shooting/La-Liga-Stats','https://fbref.com/en/comps/12/misc/La-Liga-Stats')
elif league == '3':
    Bundesliga = webscraper('BundesLiga', 'https://fbref.com/en/comps/20/passing/Bundesliga-Stats', 'https://fbref.com/en/comps/20/shooting/Bundesliga-Stats','https://fbref.com/en/comps/20/misc/Bundesliga-Stats')
elif league == '4':
    SerieA = webscraper('SerieA', 'https://fbref.com/en/comps/11/passing/Serie-A-Stats', 'https://fbref.com/en/comps/11/shooting/Serie-A-Stats','https://fbref.com/en/comps/11/misc/Serie-A-Stats')
elif league == '5':
    Ligue1 = webscraper('Ligue1', 'https://fbref.com/en/comps/13/passing/Ligue-1-Stats', 'https://fbref.com/en/comps/13/shooting/Ligue-1-Stats','https://fbref.com/en/comps/13/misc/Ligue-1-Stats')
elif league == '6':
    ChampionsLeague = webscraper('ChampionsLeague', 'https://fbref.com/en/comps/8/passing/Champions-League-Stats', 'https://fbref.com/en/comps/8/shooting/Champions-League-Stats','https://fbref.com/en/comps/8/misc/Champions-League-Stats')
else:
    print('Invalid value selected!')