# -*- coding: gb18030 -*-
import BigWorld
from SpaceCopy import SpaceCopy
import Love3

class SpaceCopyYeZhanFengQi( SpaceCopy ):
	# 夜战凤栖镇
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.minLevel = 0
		self.maxLevel = 0
		self.intervalLevel = 0
		self.minPlayer = 0
		self.maxPlayer = 0
		self.maxExit = 0
		self.minLevelPlayer = 0
		self.prepareTime = 0
		self.trapReviveTime = 0
		self.trapReviveNum = 0
		self.spaceLife = 0
	
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
		self.minLevelPlayer = section[ "Space" ][ "minLevelPlayer" ].asInt	# 一个等级段至少要多少人参与
		self.maxExit = section[ "Space" ][ "maxExit" ].asInt
		self.maxPlayer = section[ "Space" ][ "maxPlayer" ].asInt
		self.prepareTime = section[ "Space" ][ "prepareTime" ].asInt # 准备时间
		self.trapReviveTime = section[ "Space" ][ "trapReviveTime" ].asInt # 准备时间
		self.trapReviveNum = section[ "Space" ][ "trapReviveNum" ].asInt # 准备时间
		self.spaceLife = section[ "Space" ][ "spaceLife" ].asInt # 准备时间