# -*- coding: gb18030 -*-

from MiniMonster_Mini import MiniMonster_Mini
import BigWorld
import csdefine
from bwdebug import *
import time
from YXLMBoss import YXLMBoss
from Resource.LolMiniMonsterData import LolMiniMonsterData

g_lolMiniMonsterData = LolMiniMonsterData.instance()


class MiniMonster_Lol( MiniMonster_Mini ):
	"""
	英雄联盟小怪
	"""
	def __init__( self ):
		"""
		初始化
		"""
		MiniMonster_Mini.__init__( self )
		self.patrolList = ""
		self.enemyClasses = []		# 敌对怪物ID
	
	def loadLolData( self, selfEntity ):
		"""
		加载小怪数据
		"""
		data = g_lolMiniMonsterData.getLolMiniMonsterData( selfEntity.className )
		self.patrolList = data["patrolList"]
		self.enemyIDs = data["enemyIDs"].split( "|" )
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		战斗状态下AI 的 心跳
		"""
		MiniMonster_Mini.onFightAIHeartbeat( self, selfEntity )
		
		# 每隔3秒优先选择最近的小怪作为攻击目标
		if selfEntity.fightStartTime > 0 and int( ( time.time() - selfEntity.fightStartTime ) ) % 3 == 0:
			target = BigWorld.entities.get( selfEntity.targetID )
			if target:
				if target.utype == csdefine.ENTITY_TYPE_ROLE or isinstance( target, YXLMBoss ):
					selfEntity.getNearByEnemy( float( selfEntity.viewRange ) )	# 如果追击玩家或Boss，强制切换目标
	
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		yxlm副本特有的补刀处理
		"""
		self.dieNotify( selfEntity, killerID )
		bootyOwner = selfEntity.getBootyOwner()					# 气运拥有者
		if bootyOwner[0] != 0:							# 获得单人杀怪气运
			killers = selfEntity.gainSingleReward( bootyOwner[0] )
			for entity in killers:
				entity.client.onShowAccumPoint( selfEntity.id, selfEntity.accumPoint )
		else:
			INFO_MSG( "%s(%i): I died, but no booty owner." % ( selfEntity.className, selfEntity.id ) )

