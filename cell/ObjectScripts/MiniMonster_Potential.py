# -*- coding: gb18030 -*-

"""
精简怪物类
"""
from MiniMonster import MiniMonster
import csstatus
from bwdebug import *

class MiniMonster_Potential(	MiniMonster	):
	"""
	基本精简怪物类，主要功能有：
	1、敌人有效性检查
	2、清理不在视野范围的敌人
	3、每隔4秒选择最高伤害为目标
	4、呼叫同伴
	"""
	def __init__( self ):
		"""
		初始化
		"""
		MiniMonster.__init__( self )
		self._potential = 0
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		战斗状态下AI 的 心跳
		"""
		MiniMonster.onFightAIHeartbeat( self, selfEntity )
		
		# 处理呼叫同伴功能
		if selfEntity.queryTemp( "callSign", True ):
			return
		if selfEntity.callRange:
			selfEntity.setTemp( "callSign", True )
			for e in selfEntity.entitiesInRangeExt( selfEntity.callRange, None, selfEntity.position ):
				if e.className in self.callList:
					e.onFightCall( selfEntity.targetID, selfEntity.className )
		
	def dieNotify( self, selfEntity, killerID ):
		"""
		死亡通知；当selfEntity的die()被触发时被调用
		"""
		spaceBase = selfEntity.queryTemp( "space", None )
		spaceEntity = None
		
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			
		try:
			killer = BigWorld.entities[ killerID ]
		except KeyError:
			DEBUG_MSG( "not find the Entity! %i" % killerID )
			killer = None
			
		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onKillMonster( spaceEntity, False )
		elif spaceBase:
			spaceBase.cell.remoteScriptCall( "onKillMonster", ( False, ) )