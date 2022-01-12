# -*- coding: gb18030 -*-

from bwdebug import *
from Monster import Monster

class MonsterYXLM( Monster ):
	"""
	英雄联盟怪物（塔，基地）
	"""
	def __init__( self ):
		Monster.__init__( self )
		
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		yxlm副本特有的补刀处理
		"""
		self.dieNotify( selfEntity, killerID )
		selfEntity.getSpaceCell().unRegistMonster( selfEntity.className, selfEntity )
		bootyOwner = selfEntity.getBootyOwner()					# 气运拥有者
		if bootyOwner[0] != 0:							# 获得单人杀怪气运
			killers = selfEntity.gainSingleReward( bootyOwner[0] )
			for entity in killers:
				entity.client.onShowAccumPoint( selfEntity.id, selfEntity.accumPoint )
		else:
			INFO_MSG( "%s(%i): I died, but no booty owner." % ( selfEntity.className, selfEntity.id ) )
