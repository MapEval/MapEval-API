from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type, Optional
import requests
import time

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
                print("Status: ", data['matrix'][0][0]['status'])
                # time.sleep(10)
                return data['matrix'][0][0]['duration']['text']
            else:
                print(f"Failed to retrieve data: {response.status_code}")
                return "No route found. Please check the place ids and try again."
            
        except:
            return "No route found. Please check the place ids and try again."
    
    def _arun(self, originId: str, destinationId: str, travelMode: str):
        raise NotImplementedError("This tool does not support async")

    
class PlaceDetails(BaseModel):
    placeId: str = Field(description="Place Id of the location")

    
class PlaceDetailsTool(BaseTool):
    name: str = "PlaceDetails"
    description: str = "Get details for a given place ID."
    args_schema: Type[BaseModel] = PlaceDetails
    handle_tool_error: bool  = True
    
    def _run(self, placeId: str) -> str:        
        url = baseUrl+"/map/details/custom/"+placeId
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1haGlybGFiaWJkaWhhbiIsImlzcyI6Im1hcHF1ZXN0LWFwcC5vbnJlbmRlci5jb20iLCJpYXQiOjE3MTk0MDA4MTB9.H7OuYP43EOTIYpvRL2XcH3GDDvyVsnqYzLkHIDPCsSs"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['result']
            # Filter out the null values
            data = {k: v for k, v in data.items() if v is not None}
            # time.sleep(10)
            return data
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return "Incorrect Place ID. Please use correct place id."
            
class PlaceId(BaseModel):
    placeName: str = Field(description="Name of the place")
    
class PlaceIdTool(BaseTool):
    name: str = "PlaceId"
    description: str = "Get place ID for a given location."
    args_schema: Type[BaseModel] = PlaceId
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
        if response.status_code == 200 and len(response.json()['results']) > 0:
            data = response.json()
            # time.sleep(10)
            return data['results'][0]['place_id']
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return "Incorrect place name. Please use the same name as in the question."
  
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
        url = baseUrl+"/map/directions/custom"
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
            # time.sleep(10)
            return data['routes']
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return "No route found. Please check the place ids and try again."
    
    def _arun(self, originId: str, destinationId: str, travelMode: str):
        raise NotImplementedError("This tool does not support async")
    
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
        
        url = baseUrl+"/map/nearby/tool"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1haGlybGFiaWJkaWhhbiIsImlzcyI6Im1hcHF1ZXN0LWFwcC5vbnJlbmRlci5jb20iLCJpYXQiOjE3MTk0MDA4MTB9.H7OuYP43EOTIYpvRL2XcH3GDDvyVsnqYzLkHIDPCsSs"
        }
        params = {
            "location": placeId,
            "radius": None if rankby == 'distance' else radius,
            "type": type,
            "rankby": rankby
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # time.sleep(10)
            return data['results']
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return "No places found. Please check the place id and other parameters and try again."
    
    def _arun(self, placeId: str, type: str,  rankby: str = 'distance', radius: Optional[int] = None):
        raise NotImplementedError("This tool does not support async")
    