# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPotential.py,v 1.3 2008-02-23 08:39:57 kebiao Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from SpaceCopyTeam import SpaceCopyTeam

class SpaceCopyPotential( SpaceCopyTeam ):
	"""
	用于匹配SpaceDomainCopyTeam的基础类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		self.spawnFileList = {}

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )
		data = section[ "Space" ][ "playerEnterPoint" ]
		if not section.has_key("spawn"):
			ERROR_MSG( "SpaceCopyPotential:spawn config is None." )
		else:
			for file in section["spawn"].values():
				if not file.has_key("spawnFile"):
					ERROR_MSG( "SpaceCopyPotential:spawnFile config is None." )
					break
				self.spawnFileList[ file["playerAmount"].asInt ] = file["spawnFile"].asString
		self._playerEnterPoint = ( eval( data[ "pos" ].asString ), eval( data[ "direction" ].asString ) )
		
	def onSpaceTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData ):
		"""
		domain找到相应的spaceNormal后，spaceNormal开始传送一个entity到他的space上时的通知
		"""
		SpaceCopyTeam.onSpaceTeleportEntity( self, selfEntity, self._playerEnterPoint[0], self._playerEnterPoint[1], baseMailbox, pickData )
		
		
	def getSpaceSpawnFile( self, selfEntity ):
		"""
		获取出生点文件
		"""
		if selfEntity.params["playerAmount"] == 0:
			ERROR_MSG( "SpaceCopyPotential:playerAmount is not ready." )
		else:
			self._spawnFile = self.spawnFileList[ selfEntity.params["playerAmount"] ]
			return self._spawnFile
		
	def getSpawnSection( self ):
		"""
		"""
		self._spawnSection = Language.openConfigSection( self._spawnFile )
		return self._spawnSection
# SpaceCopyPotential.py
