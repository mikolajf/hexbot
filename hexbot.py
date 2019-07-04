import requests
import json
from pdb import set_trace as bp

from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from math import abs, floor
import matplotlib.pyplot as plt
from matplotlib.colors import hex2color
import numpy as np
import random



def api_response(*args, **kwargs):
        url = "http://api.noopschallenge.com/hexbot"
        payload = {name: kwargs[name] for name in kwargs if kwargs[name] is not None}

        myResponse = requests.get(url, params = payload)
        #print (myResponse.status_code)

        # For successful API call, response code will be 200 (OK)
        if(myResponse.ok):
                colors = json.loads(data)["colors"]
                return [item["value"] for item in colors]

        else:
          # If response code is not ok (200), print the resulting http error code with description
                myResponse.raise_for_status()


def read_from_file(file_name):
        # read file
        with open(file_name, 'r') as f:
                data=f.read()

        # parse file
        colors = json.loads(data)["colors"]
        return [item["value"] for item in colors]


def col_dist_matrix(sRGBColors):
        LabColorList = [convert_color(color,LabColor) for color in sRGBColors]
        matrix = np.array([[delta_e_cie1976(i, j) for j in LabColorList] for i in LabColorList])
        matrix = np.triu(matrix)
        matrix[matrix == 0] = np.nan
        return(matrix)

def plot(sRGBColors):
        class Coordinates:
                def __init__(self,n):
                        self.size = n
                        # create array of coordinates 
                        self.points = np.full((self.size, self.size, 3), np.nan)

                def choose(self, value, i = None, j = None):
                        if i and j:
                                matrix_dist = np.full((self.size, self.size), np.nan)
                                available = np.argwhere(np.isnan(self.points))

                                for point in available:
                                        matrix_dist[point[0],point[1]] = abs(point[0]-i) + abs(point[1]-j)

                                x,y = np.unravel_index(np.nanargmin(matrix_dist), matrix_dist.shape)[0:2]
                        else: 
                                x,y = random.choice(np.argwhere(np.isnan(np.array(self.points))).tolist())[0:2]

                        self.points[x,y] = value
                        return(x,y)


        col_distance = col_dist_matrix(sRGBColors)
        coord = Coordinates(floor(sqrt(len(sRGBColors))))

        fig = plt.figure()

        for idx, value in enumerate(sRGBColors):
                if idx >= coord.size**2:
                        break

                color3D = value.get_value_tuple()

                if any(col_distance[:idx, idx]<25):
                        # find the closest color
                        closest_color_id = np.argmin(col_distance[:idx, idx])
                        # find coordinate
                        ii = np.argwhere(coord.points == sRGBColors[closest_color_id].get_value_tuple())[0]
                        #choose point near ii
                        x,y = coord.choose(color3D, i = ii[0], j = ii[1])
                else:
                        #choose point randomly
                        x,y = coord.choose(color3D)


        plt.imshow(coord.points)
        plt.show()

if __name__ == "__main__":
        try: 
                hex_colors = api_response(count = 1000)
                print("API works.")
        except:
                hex_colors = read_from_file("example.json")
                print("Loaded from memory.")
        sRGBColors = [sRGBColor.new_from_rgb_hex(color) for color in hex_colors]
        plot(sRGBColors)
