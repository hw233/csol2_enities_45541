# -*- coding: gb18030 -*-
import copy
import math
import random
import BigWorld

import Love3
from bwdebug import *
import csconst
import csstatus
from Message_logger import *
from ActivityLog import g_activityLog as g_aLog
import cschannel_msgs

class DanceKingData( object ):
	def __init__( self ):
		self.reset()
		
	def reset( self ):
		self.uname = ""
		self.title = ""
		self.tongName = ""
		self.level = 10
		self.raceclass = 0
		self.hairNumber = 0
		self.faceNumber = 0
		self.bodyFDict = { "iLevel":0, "modelNum":0 }
		self.volaFDict = { "iLevel":0, "modelNum":0 }
		self.breechFDict = { "iLevel":0, "modelNum":0 }
		self.feetFDict = { "iLevel":0, "modelNum":0 }
		self.lefthandFDict = { "iLevel":0, "modelNum":0, "stAmount":0 }
		self.righthandFDict = { "iLevel":0, "modelNum":0, "stAmount":0 }
		self.talismanNum = 0
		self.fashionNum = 0
		self.adornNum = 0
		self.headTextureID = 0
	
	def __setitem__( self, name, value ):
		setattr( self, name, value )
	
	def isSet( self ):
		return self.uname
		
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "uname" ] = obj.uname
		dict[ "title" ] = ""
		dict[ "tongName" ] = obj.tongName
		dict[ "level" ] = obj.level
		dict[ "raceclass" ] = obj.raceclass
		dict[ "hairNumber" ] = obj.hairNumber
		dict[ "faceNumber" ] = obj.faceNumber
		dict[ "bodyFDict" ] = obj.bodyFDict
		dict[ "volaFDict" ] = obj.volaFDict
		dict[ "breechFDict" ] = obj.breechFDict
		dict[ "feetFDict" ] = obj.feetFDict
		dict[ "lefthandFDict" ] = obj.lefthandFDict
		dict[ "righthandFDict" ] = obj.righthandFDict
		dict[ "talismanNum" ] = obj.talismanNum
		dict[ "fashionNum" ] = obj.fashionNum
		dict[ "adornNum" ] = obj.adornNum
		dict[ "headTextureID" ] = obj.headTextureID
		return dict
		
	def createObjFromDict( self, dict ):
		obj = DanceKingData()
		obj.uname = dict[ "uname" ]
		obj.title = dict[ "title" ]
		obj.tongName = dict[ "tongName" ]		
		obj.level = dict[ "level" ]
		obj.raceclass = dict[ "raceclass" ]
		obj.hairNumber = dict[ "hairNumber" ]
		obj.faceNumber = dict[ "faceNumber" ]
		obj.bodyFDict = dict[ "bodyFDict" ]
		obj.volaFDict = dict[ "volaFDict" ]
		obj.breechFDict = dict[ "breechFDict" ]
		obj.feetFDict = dict[ "feetFDict" ]
		obj.lefthandFDict = dict[ "lefthandFDict" ]
		obj.righthandFDict = dict[ "righthandFDict" ]
		obj.talismanNum = dict[ "talismanNum" ]
		obj.fashionNum = dict[ "fashionNum" ]
		obj.adornNum = dict[ "adornNum" ]
		obj.headTextureID = dict[ "headTextureID" ]
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, DanceKingData )

DanceKingIns = DanceKingData()