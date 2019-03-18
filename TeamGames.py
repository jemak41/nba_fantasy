from nba_api.stats.endpoints import commonteamroster as ctr
import AverageXActualGames as axag
import Teams as t
import time

dateToday = axag.dateToday
advanceDay = 1

def main():
    global wkStart,wkEnd

    wkEnd = axag.dt.combine(axag.weekEnd(axag.datetime.date(dateToday.year, dateToday.month, dateToday.day), 6), axag.datetime.time())
    wkStart = axag.dt.combine(axag.weekStart(axag.datetime.date(dateToday.year, dateToday.month, dateToday.day), 0), axag.datetime.time())
    lis = list(t.teamsList.values())

    df_GPGL = axag.getGPGL(lis, wkStart)
    df_GPNP = axag.getGPNG(lis, wkEnd, wkStart)

    print(str(wkStart))
    print(str(wkEnd))
    print('The date today is ' + str(dateToday))
    print()

    print()
    df_GPGL.insert(1, 'Teams', list(t.teamsList.keys()))
    df_GPNP.insert(1, 'Teams', list(t.teamsList.keys()))
    df_GPGL = df_GPGL.sort_values(by='GTBP', ascending=False)
    df_GPNP = df_GPNP.sort_values(by='GTBP', ascending=False)
    print(df_GPGL)
    print(df_GPNP)



    df_GP = df_GPNP

    df_GP.GTBP = df_GPNP.GTBP + df_GPGL.GTBP

    df_GP = df_GP.sort_values(by='GTBP', ascending=False)

    print(df_GP)


if __name__ == '__main__':
    main()