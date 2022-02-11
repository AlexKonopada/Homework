import csv
import pandas as pd
from geopy.geocoders import Nominatim
import argparse
from geopy.distance import geodesic
import folium
def converting_to_csv(locations):
    '''
    Convert the given file into csv and return it
    '''
    list_for_csv = []
    with open(locations, 'r+', encoding='latin1') as loc:
        data = loc.readlines()[14:50]

    for film in data:
        film_info = []
        name = film[:film.find('(')-1].replace('"',"")
        try:
            year = int(film[film.find('(')+1:film.find(')')])    
        except ValueError:
            year = 1900  
        par_idx = film.find('}')
        if par_idx != -1:
            if film.count('(') == 2:
                location = film[par_idx+1:]
            else:
                val = -1
                for i in range(0, 3):
                    val = film.find('(', val + 1)
                location = film[par_idx+1:val]
        else:
            if film.count('(') == 2:
                par2_idx = film.find('(', film.find('(')+1)
                location = film[film.find(')')+1:par2_idx]
            else:
                location = film[film.find(')')+1:]
        film_info.append(name)
        film_info.append(year)
        film_info.append(location)
        list_for_csv.append(film_info)
        for film_ in list_for_csv:
            new = film_[2].strip()
            film_[2] = new
            
    with open('locations.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'year', 'location'])
        writer.writerows(list_for_csv)
    
    return writer
def pandas():
    '''
    Return converted csv file to a dataframe
    '''
    df = pd.read_csv('locations.csv')
    return df
    
def latitude_longitude(country):
    '''
    return tuple of latitude and longitude by given location
    '''
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(country)
    if location:
        lat = location.latitude
        lon = location.longitude
    else:
        lat = 0
        lon = 0 
    return lat, lon





def adding_coordinates(dataframe):
    '''
    return the dataframe with added coordinates of every location in previous data frame
    '''
    df = dataframe
    df['latitude_longitude'] = df.apply(lambda x: latitude_longitude(x['location']), axis = 1)     
    return df

def specific_year(dataframe, year):
    '''
    return the dataframe of specific year(for example 2015 - will return dataframe with films of 2015)
    '''
    df = dataframe
    df = df.loc[df['year'] == year].drop_duplicates(subset='latitude_longitude')
    return df
def main():
    '''
    main function
    return the map with markers of places where films were created
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int)
    parser.add_argument('latitude', type=float)
    parser.add_argument('longitude', type=float)
    parser.add_argument('path_to_dataset')
    args = parser.parse_args()
    user_coords = (args.latitude, args.longitude) 
    to_csv = converting_to_csv(args.path_to_dataset)
    new_df = pandas()
    df = adding_coordinates(new_df)
    specific_year_data = specific_year(df, args.year)
    specific_year_data['distance'] = specific_year_data.apply(lambda x: geodesic(x['latitude_longitude'], user_coords).miles, axis=1)
    if len(specific_year_data) <= 10:
        df = specific_year_data
    else:
        df = specific_year_data.nsmallest(10, 'distance')
    df[['latitude', 'longitude']] = pd.DataFrame(df['latitude_longitude'].tolist(), index=df.index)
    df.drop(df.index[df['latitude'] == 0], inplace = True)
    lat = df['latitude']
    lon = df['longitude']
    films = df['name']
    map = folium.Map(location=[args.latitude, args.longitude])
    fg = folium.FeatureGroup(name='Films')
    for lt, ln, f in zip(lat, lon, films):
        fg.add_child(folium.CircleMarker(location=[lt, ln], radius=10, popup=f))
    
    map.add_child(fg)
    map.save('Films.html')
    return df
print(main())
