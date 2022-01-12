# -*- coding: gb18030 -*-
#
# $Id: WeatherSystem.py,v 1.6 2007-04-20 03:36:40 phw Exp $

"""
此天气功能未看到效果。
具体分析见文档
"""

import BigWorld
from interface.GameObject import GameObject

def average(list):
	return reduce(lambda a,b: a + b, list) / len(list)


class WeatherSystem(GameObject):

	def __init__(self):
		GameObject.__init__( self )

	def enterWorld( self ):
		if not self.weatherMap.has_key(self.name):
			self.weatherMap[self.name] = [self]	
		else:
			self.weatherMap[self.name].append(self)
			
		self.recalcWeather()

	def leaveWorld( self ):
		self.weatherMap[self.name].remove(self)
		self.recalcWeather()

	def recalcWeather( self ):
		list = self.weatherMap[self.name]
		
		if self.name == "TEMPERATURE":
			if list == []:
				BigWorld.weather(self.spaceID).temperature(25, 1)
			else:
				temperature = average([item.arg0 for item in list])	
				BigWorld.weather(self.spaceID).temperature(temperature, 1)
				
		elif self.name == "WIND":
			if list == []:
				BigWorld.weather(self.spaceID).windAverage(0, 0)
				BigWorld.weather(self.spaceID).windGustiness(0)
			else:
				avgx = average([item.arg0 for item in list])
				avgy = average([item.arg1 for item in list])
				gustiness = average([item.arg2 for item in list])
				BigWorld.weather(self.spaceID).windAverage(avgx, avgy)
				BigWorld.weather(self.spaceID).windGustiness(gustiness)		
					
		else:
			if list == []:
				BigWorld.weather(self.spaceID).system(self.name).direct(0, (0,0,0,0), 1)
			else:				
				propensity = average([item.propensity for item in list])
				arg0 = average([item.arg0 for item in list])
				arg1 = average([item.arg1 for item in list])
				
				BigWorld.weather(self.spaceID).system(self.name).direct( \
					propensity, (arg0, arg1, 0, 0), 1)				

				

# The weatherMap is a global dictionary of all the weather systems
# in the client's AoI. It is keyed by weather type. For each weather
# type, there is a list of all the systems of that type. There is
# one default weatherSystem in the map, so that there will be clear
# weather if no other weatherSystems are spawned.

class WeatherSystemDummy:
	pass

defaultWeather = WeatherSystemDummy()
#defaultWeather.name = "CLEAR"
#defaultWeather.propensity = 1
#defaultWeather.arg0 = 0
#defaultWeather.arg1 = 0

defaultWeather.name = "WIND"
defaultWeather.propensity = 8
defaultWeather.arg0 = 20
defaultWeather.arg1 = 60
defaultWeather.arg2 = 90

#WeatherSystem.weatherMap = { "CLEAR" : [defaultWeather] }

WeatherSystem.weatherMap = { "WIND" : [defaultWeather] }


# WeatherSystem.py
