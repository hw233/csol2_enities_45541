# -*- coding: gb18030 -*-

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyMaps( SpaceCopy ):
	"""
	多地图单人副本脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		self._spaceMapsClassNames = []
		self._spaceMapsNo = 0
		self.bossID = []

	def load( self, section ):
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		for idx, item in enumerate( section[ "Space" ][ "spaceMapsInfos" ].values() ):
			className = item[ "className" ].asString
			self._spaceMapsClassNames.append( className )
			if className == self.getClassName():
				self._spaceMapsNo = idx
		self.bossID = section[ "Space" ][ "bossID" ].asString.split(";")
		
		SpaceCopy.load( self, section )
	
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
		return { 'dbID' : entity.databaseID, "enterCopyNo" : self._spaceMapsNo }
	
	def getCopyNo( self ):
		"""
		获取当前的地图的编号
		"""
		return self._spaceMapsNo
	
	def getSpaceClassName( self, copyNo ):
		"""
		获取对应地图的ClassName
		"""
		return self._spaceMapsClassNames[ copyNo ]