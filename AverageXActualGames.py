from nba_api.stats.endpoints import playerfantasyprofile as pfp
from nba_api.stats.endpoints import playernextngames as nxt
from nba_api.stats.endpoints import playergamelog as pgl
from nba_api.stats.library import data
import list as li
import time
import re
import pandas as pd
from datetime import datetime as dt
import datetime, pytz

dateToday = dt.now(pytz.timezone('US/Central'))
daysAdd = 0 #Add days here if want to get the games after the specific date
allstar = 0
delay = 1

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
    return curdate + datetime.timedelta(days_ahead)

def weekEnd(curdate, weekend):
    days_behind = weekend - curdate.weekday()
    if days_behind <= 0: # Target day already happened this week
        days_behind += 7 + allstar #allstar
    return curdate + datetime.timedelta(days_behind + allstar)


def getGPNG(lis,wkEnd, wkStart):
    gp = pd.DataFrame(columns=['PlayerID', 'GTBP'])
    df = pd.DataFrame()
    for x in range(len(lis)):
        df = nxt.PlayerNextNGames(lis[x]).get_data_frames()[0]
        df.GAME_DATE = pd.to_datetime(df.GAME_DATE)
        df = df[df.GAME_DATE >= (wkStart + datetime.timedelta(daysAdd))]
        df = df[df.GAME_DATE <= wkEnd]
        gp = gp.append({'PlayerID': lis[x], 'GTBP': len(df)}, ignore_index=True)
        time.sleep(delay)
        if x % 8 == 0:
            print(str(x) + ' seconds has passed')
    print()
    return gp

def getGPGL(lis, wkStart):
    gp = pd.DataFrame(columns=['PlayerID', 'GTBP'])
    for x in range(len(lis)):
        df = pgl.PlayerGameLog(lis[x]).get_data_frames()[0]
        df.GAME_DATE = pd.to_datetime(df.GAME_DATE)
        df = df[df.GAME_DATE >= wkStart + datetime.timedelta(daysAdd)]
        gp = gp.append({'PlayerID': lis[x], 'GTBP': len(df)}, ignore_index=True)
        time.sleep(delay)
        if x % 8 == 0:
            print(str(x) + ' seconds has passed')
    print()
    return gp


def getTotalAve(lis, GTBP):
    df = pd.DataFrame()
    for x in range(len(lis)):
        df = df.append(pfp.PlayerFantasyProfile(lis[x]).get_data_frames()[0], ignore_index=True)
        time.sleep(delay)

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


    wkStart = dt.combine(weekStart(datetime.date(dateToday.year, dateToday.month, dateToday.day), 0), datetime.time())  # This variable should have the monday of this week
    wkEnd = dt.combine(weekEnd(datetime.date(dateToday.year, dateToday.month, dateToday.day), 6), datetime.time()) #0 is where it the weekstart which is sunday so add 1 for monday so on...

    lis = lis
    gp_ = 0
    """"
    print('')
    print('1. Total average for ALL the games this week')
    print('2. Total average for the REST of the games this week')
    print('')
    gp_ = input('Please select a number >> ')
    
    

    
    print('')
    print('1. My team')
    print('2. Opponent\'s')
    print('3. Enter a player ID')
    print('')
    a = input('What do you want to show? >> ')
    if a == '1':
        lis = li.lis1

    elif a == '2':
        lis = li.lis2
    else:

        lis = selPlayers()
    """

    print('The week starts at: ' + str(wkStart))
    print('The week ends at: ' + str(wkEnd))
    print('The date today is ' + str(dateToday))
    print()

    df_GPGL = getGPGL(lis, wkStart)
    df_GPNP = getGPNG(lis, wkEnd, wkStart)

    print(df_GPGL)
    print(df_GPNP)

    df_GP = df_GPNP

    if gp_ == '1':
        df_GP.GTBP = df_GPNP.GTBP + df_GPGL.GTBP
    print()

    print('There are ' + str(df_GPNP.GTBP.sum()) + ' more game(s) to be played \n')



    df_TotAve = (getTotalAve(lis, df_GP.GTBP))

    print(df_TotAve)
    print('')

    print(getTotal(df_TotAve))
    print('')

if __name__ == '__main__':
    main(li.lis1)
    main(li.lis2)