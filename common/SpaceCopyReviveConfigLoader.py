# -*- coding: gb18030 -*-
import random

import csdefine
from config.SpaceCopyReviveConfig import Datas as datas_config

class SpaceCopyReviveConfigLoader:
	# 副本复活点
	_instance = None
	_datas = {}
	def __init__( self ):
		assert SpaceCopyReviveConfigLoader._instance is None
		
	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = SpaceCopyReviveConfigLoader()
		return self._instance
	
	def initCnfData( self ):
		"""
		初始化数据
		"""
		for cnf in datas_config:
			revivePostion = eval( cnf[ "revivePostion" ] )
			reviveRandom = []
			if cnf[ "reviveRandom" ]:
				reviveRandom = [ float( r ) for r in cnf[ "reviveRandom" ].split( "," ) ]
				
			self._datas[ cnf[ "className" ] ] = ( revivePostion, reviveRandom )
	
	def getRandomIndex( self, reviveRandom ):
		for i, r in reviveRandom:
			if r > random.randint( 0, 100 ):
				return i
		
		return -1
	
	@classmethod
	def _getPos( self, spaceLabel ):
		"""
		获取副本指定类型entity的className
		@param clsType : 查询entity的类型，如bossCls，speCls等
		@type clsType : STRING
		"""
		revivePostion, reviveRandom = self._datas[ spaceLabel ]
		
		if len( reviveRandom ):
			loop = 5
			while loop:
				loop -= 1
				i = self.getRandomIndex( reviveRandom )
				if i >= 0:
					return revivePostion[ i ]
			
		return random.choice( revivePostion )
	
	@classmethod
	def _getYXLMPos( self, player, spaceLabel ):
		revivePostion, reviveRandom = self._datas[ spaceLabel ]
		return revivePostion[ player.baoZangTeamIndex() ]
	
	@classmethod
	def _getYeZhanFengQiPos( self, player, spaceLabel ):
		return player.fengQiGetRevivePosition()
	
	@classmethod
	def _getTongTurnWarOrMercuryCorePos( self, player, spaceLabel ):
		return player.position
	
	@classmethod
	def _getCampTurnWarOrMercuryCorePos( self, player, spaceLabel ):
		return player.position
	
	@classmethod
	def _getYiJieZhanChangPos( self, player, spaceLabel ):
		return player.yiJieGetRevivePosition( spaceLabel )
	
	@classmethod
	def _getShuiJingPos( self, player, spaceLabel ):
		return player.shuiJingGetRevivePosition( spaceLabel )
	
	def reviveIsCfg( self, spaceLabel ):
		return self._datas.has_key( spaceLabel )
	
	def getSpaceRevivePos( self, player, spaceLabel, spaceType ):
		global FUNC_DICT
		if FUNC_DICT.has_key( spaceType ):
			return FUNC_DICT[ spaceType ]( player, spaceLabel )
		else:
			return self._getPos( spaceLabel )

FUNC_DICT = { \
	csdefine.SPACE_TYPE_YXLM_PVP : SpaceCopyReviveConfigLoader._getYXLMPos,
	csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI : SpaceCopyReviveConfigLoader._getYeZhanFengQiPos,
	csdefine.SPACE_TYPE_TONG_TURN_WAR	: SpaceCopyReviveConfigLoader._getTongTurnWarOrMercuryCorePos,
	csdefine.SPACE_TYPE_CAMP_TURN_WAR	: SpaceCopyReviveConfigLoader._getCampTurnWarOrMercuryCorePos,
	csdefine.SPACE_TYPE_MERCURY_CORE_MAP	: SpaceCopyReviveConfigLoader._getTongTurnWarOrMercuryCorePos,
	csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG	: SpaceCopyReviveConfigLoader._getYiJieZhanChangPos,
	csdefine.SPACE_TYPE_SHUIJING			: SpaceCopyReviveConfigLoader._getShuiJingPos,
}