# -*- coding: gb18030 -*-
import BigWorld
from SpaceCopy import SpaceCopy
import Love3

class SpaceCopyYiJieZhanChang( SpaceCopy ):
	# 异界战场
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.minLevel = 0
		self.maxLevel = 0
		self.intervalLevel = 0
		self.minPlayer = 0
		self.maxPlayer = 0
		self.enterInfos = []
	
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		self.minLevel = section[ "Space" ][ "minLevel" ].asInt
		self.maxLevel = section[ "Space" ][ "maxLevel" ].asInt
		self.intervalLevel = section[ "Space" ][ "intervalLevel" ].asInt
		self.minPlayer = section[ "Space" ][ "minPlayer" ].asInt
		self.maxPlayer = section[ "Space" ][ "maxPlayer" ].asInt
		self.maxOfflineTime = section[ "Space" ][ "maxOfflineTime" ].asInt
		
		for idx, item in enumerate( section[ "Space" ][ "enterInfos" ].values() ):
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self.enterInfos.append( ( pos, direction ) )
		

	def packedDomainData( self, entity ):
		"""
		virtual method.
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		pickDict = {}
		pickDict["dbID"] 		= entity.databaseID
		pickDict["lastOffline"]	= entity.role_last_offline
		return pickDict