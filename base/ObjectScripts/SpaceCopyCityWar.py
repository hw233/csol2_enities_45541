# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.1 2008-08-25 09:30:27 kebiao Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from SpaceCopy import SpaceCopy

class SpaceCopyCityWar( SpaceCopy ):
	"""
	用于匹配SpaceDomainCopyTeam的基础类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		self.roomLevel = section[ "Space" ][ "roomLevel" ].asInt
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.right_playerEnterPoint = ( pos, direction )
		
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.left_playerEnterPoint = ( pos, direction )
		
		if self.getRoomLevel() == 1:
			data = section[ "Space" ][ "defend_playerEnterPoint" ]
			pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
			self.defend_playerEnterPoint = ( pos, direction )
		
	def getRoomName( self ):
		return self.roomName
		
	def getRoomIndex( self ):
		return self.roomIndex
	
	def getRoomLevel( self ):
		return self.roomLevel
		
	def packedDomainData( self, entity ):
		"""
		virtual method.
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'tongDBID' : entity.cellData[ "tong_dbID" ], "ename" : entity.cellData[ "playerName" ], "dbid": entity.databaseID }