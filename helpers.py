import mobitools as mobi
import numpy as np

def filter_ddf(df, date=None, cats=None, stations=None):
    print("filter_ddf")
    if (date is None) and (cats is None) and (stations is None):
        return df
    
    if stations is not None:
        df = df[df['Departure station'].isin(stations)]
    
    if date is not None:
        if len(date) == 2:
            df = df.set_index('Departure')[date[0]:date[1]].reset_index()
        else:
            df = df.set_index('Departure')[date].reset_index()
   
            
    if cats is not None:
      
        if 'all' in cats:
            pass
        
        else:
            idx = np.array([False for x in range(len(df))])
            
            if '24h' in cats:
                idx24 = np.array((df['Membership Type']=='24 Hour'))
                idx = idx | idx24
            if '365S' in cats:
                idx365s = np.array(df['Membership Type'].str.contains('365.+Standard'))
                idx = idx | idx365s
            if '365P' in cats:
                idx365p = np.array(df['Membership Type'].str.contains('365.+Plus'))
                idx = idx | idx365p                
            if '90d' in cats:
                idx90 = np.array(df['Membership Type'].str.contains('90')) 
                idx = idx | idx90
                
            df = df.iloc[idx]
    sdf = mobi.get_stationsdf('../mobi/')
    df = mobi.system.add_station_coords(df,sdf)
    return df