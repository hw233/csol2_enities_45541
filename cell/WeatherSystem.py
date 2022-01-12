# -*- coding: gb18030 -*-
#
# $Id: WeatherSystem.py,v 1.7 2007-06-14 09:40:45 huangyongwei Exp $

"""
此天气功能未看到效果。
具体分析见文档
"""

import BigWorld
from interface.GameObject import GameObject
import csdefine

class WeatherSystem( GameObject ):
	"A weather system entity."
	def __init__( self ):
		"""
		"""
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_WEATHER_SYSTEM )

def clear( propensity, spaceID = 2, position = (0,0,0) ):

	dict = {}
	dict["name"] = "CLEAR"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def rain( propensity, spaceID = 2, position = (0,0,0) ):
	dict = {}
	dict["name"] = "RAIN"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def cloud( propensity, spaceID = 2, position = (0,0,0) ):
	dict = {}
	dict["name"] = "CLOUD"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def storm( propensity, spaceID = 2, position = (0,0,0) ):
	dict = {}
	dict["name"] = "STORM"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

##

def temperature( value, spaceID = 2, position = (0,0,0) ):
	dict = {}
	dict["name"] = "TEMPERATURE"
	dict["propensity"] = 0
	dict["arg0"] = value
	dict["arg1"] = 0.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def wind( x, y, gustiness, spaceID = 2, position = (0,0,0) ):
	dict = {}
	dict["name"] = "WIND"
	dict["propensity"] = 0
	dict["arg0"] = x
	dict["arg1"] = y
	dict["arg2"] = gustiness
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

##

def kill(name = ""):
	for e in BigWorld.entities.values():
		if e.__class__ == WeatherSystem:
			if name == "" or e.name == name:
				e.destroy()


# WeatherSystem.py
