from nba_api.stats.endpoints import commonteamroster as ctr
import AverageXActualGames as axag
import Teams as t
import time

dateToday = axag.dateToday

def main():

    wkStart_ = axag.datetime.combine(axag.weekStart(axag.date(dateToday.year, dateToday.month, dateToday.day), 0), axag.time())
    wkEnd_ = axag.datetime.combine(axag.weekEnd(axag.date(dateToday.year, dateToday.month, dateToday.day), 6), axag.time())


    lis = list(t.teamsList.values())

    df_GPGL = axag.getGamesPlayed(lis, wkStart_)
    df_GPNP = axag.getGamesNotPlayed(lis, wkEnd_, wkStart_)

    print('The week starts at: ' + str(wkStart_))
    print('The week ends at: ' + str(wkEnd_))
    print('The modified date today is ' + str(dateToday))
    print('The real date today is ' + str(axag.realdateToday))
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