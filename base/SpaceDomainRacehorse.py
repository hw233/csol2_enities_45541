# -*- coding: gb18030 -*-
#
# $Id:  Exp $

"""
Space domain class
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomainCopyTeam import SpaceDomainCopyTeam
import random
from csconst import Start_Positions
from csconst import Start_Positions_03
import csdefine

class SpaceDomainRacehorse(SpaceDomainCopyTeam):
	"""
	赛马
	"""
	def __init__( self ):
		SpaceDomainCopyTeam.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS


	def _onRegisterSpaceManager(self, complete):
		"""
		"""
		if not complete:
			ERROR_MSG( "Register SpaceDomainRacehorse Fail!" )
			# again
			self.registerGlobally("SpaceDomainRacehorse", self._onRegisterSpaceManager)
		else:
			BigWorld.globalData["SpaceDomainRacehorse"] = self				# 注册到所有的服务器中
			INFO_MSG("SpaceDomainRacehorse Create Complete!")


	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method
		"""
		baseMailbox.logonSpaceInSpaceCopy()


	def createRaceMap( self, groupID ):
		"""
		define method
		创建比赛地图
		"""
		spaceItem = self.createSpaceItem( {"spaceKey": groupID, "dbID" : groupID } )
		self.keyToSpaceNumber[groupID] = spaceItem.spaceNumber


	def createSpaceItem( self, param ):
		"""
		"""		
		spaceItem = SpaceDomainCopyTeam.createSpaceItem( self, param )
		return spaceItem

	def teleportRacer( self, playerBaseMailBox, params ):
		"""
		define method
		传送一个玩家
		"""
		spaceItem = self.findSpaceItem( params )
		if spaceItem:
			positions = None
			if BigWorld.globalData["RacehorseType"] == "sai_ma_chang_01":
				positions = Start_Positions
				direction = (0.000000, 0.000000, -1.5)
			elif BigWorld.globalData["RacehorseType"] == "sai_ma_chang_03":
				positions = Start_Positions_03
				direction = (0.000000, 0.000000, -1.7)
				
			pickData = self.pickToSpaceData( playerBaseMailBox, params )
			spaceItem.enter( playerBaseMailBox, random.choice( positions ), direction, pickData )


	def closeRacehorseSpace( self, groupID ):
		"""
		define method
		"""
		del self.keyToSpaceNumber[groupID]