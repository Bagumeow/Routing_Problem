from typing import List, Tuple
import requests
import polyline
import dotenv 
import folium
import os



dotenv.load_dotenv()
GOONG_API_KEY = os.getenv('GOONG_API_KEY')
def take_tuple_latlong(latlong):
    latlong = latlong.replace('(','').replace(')','').split(',')
    return (float(latlong[0]),float(latlong[1]))

def value_latlong_route(latlong:list,routing:List[List[int]]):
    list_rouing_latlong = []
    for idx,route in enumerate(routing):
        routin_latlong = []
        for i in route:
            routin_latlong.append(latlong[i])
        list_rouing_latlong.append(routin_latlong)
    return list_rouing_latlong

def concat_str_latlong(latlong):
    return ','.join([str(i) for i in latlong])

def concat_list_latlong(list_rout_latlong):
    string_latlong = []
    for list_latlong in list_rout_latlong:
        list_str_latlong= [concat_str_latlong(latlong) for latlong in list_latlong]
        s = ';'.join(list_str_latlong)
        string_latlong.append(s)
    result = [list_string.split(';') for list_string in string_latlong]
    return result

def api_direction(origin,destination,api_key=GOONG_API_KEY):
    url= f"https://rsapi.goong.io/Direction?origin={origin}&destination={destination}&vehicle=truck&api_key={api_key}"
    response = requests.get(url)
    response = response.json()
    best_route = polyline.decode(response['routes'][0]['overview_polyline']['points'])
    return best_route

def plot_latlong_routing(latlong:list,routing:List[List[int]],map=None):
    if map == None:
        map = folium.Map(location=latlong[0], zoom_start=11)
    list_routing=concat_list_latlong(value_latlong_route(latlong,routing))

    for idx, point in enumerate(latlong[1:]):
        folium.Marker(
            location=point,
            icon=folium.DivIcon(html=f'<div style="font-size: 20;"><b><div style="color:white; background-color:rgba(0, 128, 0, 0.8); border:1px solid black; width: 25px; height: 25px; border-radius: 50%; text-align: center; line-height: 25px;">{idx+1}</div></b></div>')
        ).add_to(map)
    colors = ['blue','green','purple','orange','darkred','lightred','beige','darkblue','darkgreen','cadetblue','darkpurple','white','pink','lightblue','lightgreen','gray','black','lightgray']
    for idx_rou,route in enumerate(routing):
        color = colors.pop(0)
        for i in range(len(route)-1):
            best_route = api_direction(list_routing[idx_rou][i],list_routing[idx_rou][i+1],GOONG_API_KEY)
            folium.PolyLine(best_route, color=color, weight=10, opacity=0.6).add_to(map)
            # folium.PolyLine([latlong[route[i]],latlong[route[i+1]]], color=color, weight=10, opacity=1).add_to(map)
    #poet points
    folium.Marker(
        location=latlong[0],
        icon=folium.DivIcon(html=f'<div style="font-size: 15;"><b><div style="color:white; background-color:rgba(255, 0, 0, 0.8); border:1px solid black; width: 40px; height: 40px; border-radius: 50%; text-align: center; line-height: 40px;">0</div></b></div>')
    ).add_to(map)
    return map