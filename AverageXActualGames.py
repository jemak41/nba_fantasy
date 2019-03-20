from nba_api.stats.endpoints import playerfantasyprofile as pfp
from nba_api.stats.endpoints import playernextngames as nxt
from nba_api.stats.endpoints import playergamelog as pgl
from nba_api.stats.library import data
import list as li
import time as Time
import re
import pandas as pd
from datetime import timedelta, time, date, datetime
import pytz

dateAdvance = 2 #Add days when you want to start
realdateToday = datetime.now(pytz.timezone('US/Central'))
dateToday = datetime.now(pytz.timezone('US/Central')) + timedelta(days=dateAdvance)
allstar = 0
delay = 1 #delay time

def selPlayers():
    lisP = []
    dfPlayers = pd.DataFrame(data.players)

    while True:
        print('')
        inPlayer = str(input('Please query a player name >> '))

        if inPlayer:
            inPlayerQuery = dfPlayers[(dfPlayers[3].str.contains(inPlayer, flags=re.IGNORECASE))]
            print('')
            print(inPlayerQuery)
            print('')
            inPlayerID = int(input('Please enter Player ID (1st Column) >> '))
            print('')
            print('You selected:')
            print('')
            print(str(inPlayerQuery[inPlayerQuery[0]==inPlayerID]))
            lisP.append(str(inPlayerID))
        else:
            print('')
            return lisP

def weekStart(curdate, weekstart):
    days_ahead = weekstart - curdate.weekday()
    if days_ahead > 0:
        days_ahead += -7
    return curdate + timedelta(days_ahead)

#curdate is dateToday in date format e.g.: (2019, 3, 24)
#weekday monday = 1, thursday =4
#weekend is 6
def weekEnd(curdate, weekend):
    days_behind = weekend - curdate.weekday()
    if days_behind < 0: # Target day already happened this week
        days_behind += 7 + allstar #allstar
    return curdate + timedelta(days_behind + allstar)


def getGamesNotPlayed(lis, wkEnd, wkStart):
    gp = pd.DataFrame(columns=['PlayerID', 'GTBP'])
    df = pd.DataFrame()
    for x in range(len(lis)):
        df = nxt.PlayerNextNGames(lis[x]).get_data_frames()[0]
        df.GAME_DATE = pd.to_datetime(df.GAME_DATE)
        df = df[df.GAME_DATE >= date(dateToday.year, dateToday.month, dateToday.day)]#(wkStart + timedelta(dateAdvance))]
        df = df[df.GAME_DATE <= wkEnd]
        gp = gp.append({'PlayerID': lis[x], 'GTBP': len(df)}, ignore_index=True)
        Time.sleep(delay)
        if x % 8 == 0:
            print(str(x) + ' seconds has passed')
    print()
    return gp

def getGamesPlayed(lis, wkStart):
    gp = pd.DataFrame(columns=['PlayerID', 'GTBP'])
    for x in range(len(lis)):
        df = pgl.PlayerGameLog(lis[x]).get_data_frames()[0]
        df.GAME_DATE = pd.to_datetime(df.GAME_DATE)
        df = df[df.GAME_DATE >= wkStart + timedelta(dateAdvance)]
        gp = gp.append({'PlayerID': lis[x], 'GTBP': len(df)}, ignore_index=True)
        Time.sleep(delay)
        if x % 8 == 0:
            print(str(x) + ' seconds has passed')
    print()
    return gp


def getTotalAve(lis, GTBP):
    df = pd.DataFrame()
    for x in range(len(lis)):
        df = df.append(pfp.PlayerFantasyProfile(lis[x]).get_data_frames()[0], ignore_index=True)
        Time.sleep(delay)

    df = df.drop(columns=['GROUP_SET',
                          'GROUP_VALUE',
                          'W',
                          'L',
                          'W_PCT',
                          'MIN',
                          'OREB',
                          'DREB',
                          'BLKA',
                          'PF',
                          'PFD',
                          'PLUS_MINUS',
                          'DD2',
                          'TD3',
                          'FAN_DUEL_PTS',
                          'NBA_FANTASY_PTS',
                          'FG3A',
                          'FG3_PCT',
                          'FG_PCT',
                          'FT_PCT'
                          ])
    df.insert(1, 'FGMPG', df.FGM / df.GP)
    df.insert(2, 'FGAPG', df.FGA / df.GP)
    df.insert(3, 'FTMPG', df.FTM / df.GP)
    df.insert(4, 'FTAPG', df.FTA / df.GP)
    df.insert(7, '3PTMPG', df.FG3M / df.GP)
    df.insert(9, 'PPG', df.PTS / df.GP)
    df.insert(10, 'RPG', df.REB / df.GP)
    df.insert(11, 'APG', df.AST / df.GP)
    df.insert(16, 'TOPG', df.TOV / df.GP)
    df.insert(13, 'SPG', df.STL / df.GP)
    df.insert(15, 'BPG', df.BLK / df.GP)
    df.insert(0, 'GTBP', GTBP)
    df = df.drop(columns=['PTS',
                          'AST',
                          'REB',
                          'BLK',
                          'STL',
                          'TOV',
                          'FGA',
                          'FG3M',
                          'GP',
                          'FTA',
                          'FTM',
                          'FGM'
                          ])

    return df

def getTotal(df_TotAve):

    df1 = df_TotAve.mul(df_TotAve.GTBP, axis=0)

    cols = list(df1)

    df_final = pd.DataFrame(columns= cols)

    df_final = df_final.append(df1.sum(axis=0), ignore_index=True)

    df_final.insert(2, 'FG%', df_final.FGMPG / df_final.FGAPG)
    df_final.insert(5, 'FT%', df_final.FTMPG / df_final.FTAPG)

    df_final = df_final.drop(columns=['FGMPG',
                      'FGAPG',
                      'FTMPG',
                      'FTAPG',
                      'GTBP'
                      ])

    return df_final

def main(lis):


    wkStart = datetime.combine(weekStart(date(dateToday.year, dateToday.month, dateToday.day), 0), time())  # This variable should have the monday of this week
    wkEnd = datetime.combine(weekEnd(date(dateToday.year, dateToday.month, dateToday.day), 6), time()) #0 is where it the weekstart which is sunday so add 1 for monday so on...

    lis = lis
    gp_ = 0

    print('The week starts at: ' + str(wkStart))
    print('The week ends at: ' + str(wkEnd))
    print('The modified date today is ' + str(dateToday))
    print('The real date today is ' + str(realdateToday))
    print()

    df_GamesPlayed = getGamesPlayed(lis, wkStart)
    df_GamesNotPlayed = getGamesNotPlayed(lis, wkEnd, wkStart)

    print(df_GamesPlayed)
    print(df_GamesNotPlayed)

    df_GP = df_GamesNotPlayed

    if gp_ == '1':
        df_GP.GTBP = df_GamesNotPlayed.GTBP + df_GamesPlayed.GTBP
    print()

    print('There are ' + str(df_GamesNotPlayed.GTBP.sum()) + ' more game(s) to be played \n')



    df_TotAve = (getTotalAve(lis, df_GP.GTBP))

    print(df_TotAve)
    print('')

    print(getTotal(df_TotAve))
    print('')

if __name__ == '__main__':
    main(li.lis1)
    main(li.lis2)