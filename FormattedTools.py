from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type, Optional
import requests
import time
import inflect
import traceback
import json
# Create an inflect engine
p = inflect.engine()
with open('types.json', 'r') as file:
    types = json.load(file)

baseUrl = "http://localhost:5000/api"
class TravelTime(BaseModel):
    originId: str = Field(description="Place Id of Origin")
    destinationId: str = Field(description="Place Id of Destination")
    travelMode: str = Field(description="Mode of transportation (driving, walking, bicycling, transit)")

class TravelTimeTool(BaseTool):
    name: str = "TravelTime"
    description: str = "Estimate the travel time between two places."
    args_schema: Type[BaseModel] = TravelTime
    handle_tool_error: bool  = True
    
    def _run(self, originId: str, destinationId: str, travelMode: str) -> str:
        url = baseUrl + "/map/distance/custom"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1haGlybGFiaWJkaWhhbiIsImlzcyI6Im1hcHF1ZXN0LWFwcC5vbnJlbmRlci5jb20iLCJpYXQiOjE3MTk0MDA4MTB9.H7OuYP43EOTIYpvRL2XcH3GDDvyVsnqYzLkHIDPCsSs"
        }
        params = {
            "origin": originId,
            "destination": destinationId,
            "mode": travelMode  # Assuming the API expects uppercase mode
        }
        response = requests.get(url, headers=headers, params=params)
        
        data = response.json()
        print("Response: ", data)
            
        try:
            if response.status_code == 200 and data['matrix'][0][0]['duration'] is not None:
                # print("Status: ", data['matrix'][0][0]['status'])
                time.sleep(30)
                # return data['matrix'][0][0]['duration']['text']
                mode = travelMode.lower()
                if mode == "transit":
                    return  f"Travel Time by public transport is {data['matrix'][0][0]['duration']['text']} ({data['matrix'][0][0]['distance']['text']})."
                elif mode == "driving":
                    return  f"Travel Time by car is {data['matrix'][0][0]['duration']['text']} ({data['matrix'][0][0]['distance']['text']})."
                elif mode == "bicycling":
                    return  f"Travel Time by cycle is {data['matrix'][0][0]['duration']['text']} ({data['matrix'][0][0]['distance']['text']})."
                elif mode == "walking":
                    return  f"Travel Time on foot is {data['matrix'][0][0]['duration']['text']} ({data['matrix'][0][0]['distance']['text']})."
            else:
                print(f"Failed to retrieve data: {response.status_code}")
                return "No route found. Please check the place ids and try again."
            
        except:
            return "No route found. Please check the place ids and try again."
    
    def _arun(self, originId: str, destinationId: str, travelMode: str):
        raise NotImplementedError("This tool does not support async")


def place_to_context(place):
    text = ""
    
    lat = place['geometry']['location']['lat']() if callable(place['geometry']['location']['lat']) else place['geometry']['location']['lat']
    lng = place['geometry']['location']['lng']() if callable(place['geometry']['location']['lng']) else place['geometry']['location']['lng']
    text += f"- Location: {place.get('formatted_address', '')}{' (' + str(lat) + ', ' + str(lng) + ')' }.\n"

    if place.get("phone_number"):
        text += f"- Phone Number: {place.get('phone_number', '')}.\n"

    try:
        if place.get("opening_hours") and place["opening_hours"].get("weekday_text"):
            text += f"- Open: {', '.join(place['opening_hours']['weekday_text'])}.\n"
    except:
        pass
    
    if place.get("rating"):
        text += f"- Rating: {place.get('rating', '')}. ({place.get('user_ratings_total', '0')} ratings).\n"

    # if "reviews" in place:
    #     reviews_text = "\n".join([f"   {index + 1}. {review['author_name']} (Rating: {review['rating']}): {review['text']}" for index, review in enumerate(place.get('reviews', []))])
    #     text += f"- Reviews: \n{reviews_text} "

    if place.get("price_level"):
        price_map = ["Free", "Inexpensive", "Moderate", "Expensive", "Very Expensive"]
        price_level = price_map[place.get('price_level', 0)]
        text += f"- Price Level: {price_level}.\n"

    if place.get("delivery"):
        text += "- Delivery Available.\n" if place.get('delivery') else "- Delivery Not Available.\n"

    if place.get("dine_in"):
        text += "- Dine In Available.\n" if place.get('dine_in') else "- Dine In Not Available.\n"

    # if place.get("takeaway") is not None:
    #     text += "- Takeaway Available.\n" if place.get('takeaway') else "- Takeaway Not Available.\n"

    if place.get("reservable"):
        text += "- Reservable.\n" if place.get('reservable') else "- Not Reservable.\n"

    if place.get("serves_breakfast"):
        text += "- Serves Breakfast.\n" if place.get('serves_breakfast') else "- Does Not Serve Breakfast.\n"

    if place.get("serves_lunch"):
        text += "- Serves Lunch.\n" if place.get('serves_lunch') else "- Does Not Serve Lunch.\n"

    if place.get("serves_dinner"):
        text += "- Serves Dinner.\n" if place.get('serves_dinner') else "- Does Not Serve Dinner.\n"

    if place.get("takeout"):
        text += "- Takeout Available.\n" if place.get('takeout') else "- Takeout Not Available.\n"

    if place.get("wheelchair_accessible_entrance"):
        text += "- Wheelchair Accessible Entrance.\n" if place.get('wheelchair_accessible_entrance') else "- Not Wheelchair Accessible Entrance.\n"

    return text

class PlaceDetails(BaseModel):
    placeId: str = Field(description="Place Id of the location")

    
class PlaceDetailsTool(BaseTool):
    name: str = "PlaceDetails"
    description: str = "Get details for a given place ID."
    args_schema: Type[BaseModel] = PlaceDetails
    handle_tool_error: bool  = True
    
    def _run(self, placeId: str) -> str:        
        url = baseUrl+"/map/details/"+placeId
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1haGlybGFiaWJkaWhhbiIsImlzcyI6Im1hcHF1ZXN0LWFwcC5vbnJlbmRlci5jb20iLCJpYXQiOjE3MTk0MDA4MTB9.H7OuYP43EOTIYpvRL2XcH3GDDvyVsnqYzLkHIDPCsSs"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['result']
            # Filter out the null values
            # data = {k: v for k, v in data.items() if v is not None}
            time.sleep(30)
            try:
                text = place_to_context(data)
                return text
            except Exception as e:
                print(f"Failed to retrieve data: {e}")
                traceback.print_exc()
                return "Incorrect Place ID. Please use correct place id."
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return "Incorrect Place ID. Please use correct place id."
            
class PlaceSearch(BaseModel):
    placeName: str = Field(description="Name and address of the place")
    # placeAddress: str = Field(description="Address of the place")
    
class PlaceSearchTool(BaseTool):
    name: str = "PlaceSearch"
    description: str = "Get place ID for a given location."
    args_schema: Type[BaseModel] = PlaceSearch
    handle_tool_error: bool  = True

    def _run(self, placeName: str) -> str:        
        url =  baseUrl+"/map/search"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1haGlybGFiaWJkaWhhbiIsImlzcyI6Im1hcHF1ZXN0LWFwcC5vbnJlbmRlci5jb20iLCJpYXQiOjE3MTk0MDA4MTB9.H7OuYP43EOTIYpvRL2XcH3GDDvyVsnqYzLkHIDPCsSs"
        }
        params = {
            "query": placeName
        }
        response = requests.get(url, headers=headers, params=params)
        try:
            if response.status_code == 200 and len(response.json()['results']) > 0:
                data = response.json()
                time.sleep(30)
                return data['results'][0]['place_id']
            else:
                print(f"Failed to retrieve data: {response.status_code}")
                return "Incorrect place name. Please use the same name as in the question."
        except Exception as e:
            print(f"Failed to retrieve data: {e}")
            traceback.print_exc()
            return "Incorrect place name. Please use the same name as in the question."
  
  
def directions_to_context(directions, mode):
    mode = mode.lower()
    text = ""
    if mode == "transit":
        text += f"There are {len(directions)} routes by public transport. They are:\n"
    elif mode == "driving":
        text +=  f"There are {len(directions)}  routes by car. They are:\n"
    elif mode == "bicycling":
        text +=  f"There are {len(directions)} routes by cycle. They are:\n"
    elif mode == "walking":
        text += f"There are {len(directions)} routes on foot. They are:\n"

    for index, route in enumerate(directions):
        text +=  f"{index + 1}. Via {route['summary']} | {route['legs'][0]['duration']['text']} | {route['legs'][0]['distance']['text']}\n"
        for step_index, step in enumerate(route['legs'][0]['steps']):
            text += f" - {step['html_instructions']}\n"
    return text
            
class Directions(BaseModel):
    originId: str = Field(description="Place Id of Origin")
    destinationId: str = Field(description="Place Id of Destination")
    travelMode: str = Field(description="Mode of transportation (driving, walking, bicycling, transit)")
    
class DirectionsTool(BaseTool):
    name: str = "Directions"
    description: str = "Get directions/routes between two places."
    args_schema: Type[BaseModel] = Directions
    handle_tool_error: bool  = True
    
    def _run(self, originId: str, destinationId: str, travelMode: str) -> str:
        url = baseUrl+"/map/directions"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1haGlybGFiaWJkaWhhbiIsImlzcyI6Im1hcHF1ZXN0LWFwcC5vbnJlbmRlci5jb20iLCJpYXQiOjE3MTk0MDA4MTB9.H7OuYP43EOTIYpvRL2XcH3GDDvyVsnqYzLkHIDPCsSs"
        }
        params = {
            "origin": originId,
            "destination": destinationId,
            "mode": travelMode  # Assuming the API expects uppercase mode
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200 :
            data = response.json()
            if len(data['routes']) == 0:
                return "No route found. Please check the place ids and try again."
            time.sleep(30)
            return directions_to_context(data['routes'],travelMode)
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return "No route found. Please check the place ids and try again."
    
    def _arun(self, originId: str, destinationId: str, travelMode: str):
        raise NotImplementedError("This tool does not support async")
    
def convert_from_snake(snake_str):
    """
    Convert a snake_case string to a more readable format.
    """
    components = snake_str.split('_')
    return ' '.join(x.capitalize() for x in components)

def nearby_to_context(places, type, rankby, radius):
    text = ''
    text += f"Nearby {p.plural(convert_from_snake(type))} are ({'in ' + str(radius) + ' m radius' if rankby == 'prominence' else 'sorted by distance in ascending order'}):\n"
    counter = 1
    for near_place in places:
        text += f"{counter}. {near_place.get('name', 'Unknown')} ({near_place.get('place_id')})\n"
        
        if near_place.get('vicinity'):
            text += f"   - Address: {near_place.get('vicinity', '')}.\n"

        if near_place.get('rating'):
            text += f"   - Rating: {near_place.get('rating', '')}. ({near_place.get('user_ratings_total', '0')} ratings).\n"

        price_map = [
            "Free",
            "Inexpensive",
            "Moderate",
            "Expensive",
            "Very Expensive",
        ]
        if near_place.get('price_level') is not None:
            text += f"   - Price Level: {price_map[near_place.get('price_level', 0)]}.\n"

        try:
            if near_place.get('opening_hours') and near_place['opening_hours'].get('weekday_text'):
                text += f"   - Open: {', '.join(near_place['opening_hours']['weekday_text'])}.\n"
        except:
            pass
            
        counter += 1
    return text
   
        
class NearbyPlaces(BaseModel):
    placeId: str = Field(description="The id of the place around which to retrieve nearby places.")
    type: str = Field(description="Type of place (e.g., restaurant, hospital, etc). Restricts the results to places matching the specified type.")
    rankby: str = Field(default='distance', description="Specifies the order in which places are listed. Possible values are: (1. prominence (default): This option sorts results based on their importance. When prominence is specified, the radius parameter is required. 2. distance: This option sorts places in ascending order by their distance from the specified location. When distance is specified, radius is disallowed. In case you are not concerned about the radius, use rankby as distance.)")
    radius: Optional[int] = Field(default=None,description="Defines the distance (in meters) within which to return place results.")
   
     
class NearbyPlacesTool(BaseTool):
    name: str = "NearbyPlaces"
    description: str = "Get nearby places around a location."
    args_schema: Type[BaseModel] = NearbyPlaces
    handle_tool_error: bool = True
    
    def _run(self, placeId: str, type: str,  rankby: str = 'distance', radius: Optional[int] = None) -> str:
        if rankby == "distance" and radius is not None and radius > 0:
            return "When rankby is distance, radius is disallowed. If want to use rankby as distance, please set radius to 0. And if you want to use radius, please set rankby as prominence."
        
        url = baseUrl+"/map/nearby"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1haGlybGFiaWJkaWhhbiIsImlzcyI6Im1hcHF1ZXN0LWFwcC5vbnJlbmRlci5jb20iLCJpYXQiOjE3MTk0MDA4MTB9.H7OuYP43EOTIYpvRL2XcH3GDDvyVsnqYzLkHIDPCsSs"
        }
        # Check if type is in types list
        
        params = {
            "location": placeId,
            "radius": None if rankby == 'distance' else radius,
            "type": type if type in types else None,
            "keyword": type if type not in types else None,
            "rankby": rankby
        }
        response = requests.get(url, headers=headers, params=params)
        try:
            if response.status_code == 200:
                data = response.json()
                time.sleep(30)
                print(data['results'])
                return nearby_to_context(data['results'], type, rankby, radius)
            else:
                print(f"Failed to retrieve data: {response.status_code}")
                return "No places found. Please check the place id and other parameters and try again."
        except Exception as e:
            print(f"Failed to retrieve data: {e}")
            traceback.print_exc()
            return "No places found. Please check the place id and other parameters and try again."
    
    def _arun(self, placeId: str, type: str,  rankby: str = 'distance', radius: Optional[int] = None):
        raise NotImplementedError("This tool does not support async")
    