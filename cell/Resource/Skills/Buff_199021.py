# -*- coding: gb18030 -*-

import copy
import csdefine
from bwdebug import *
from Resource.SkillLoader import g_skills
from Buff_Normal import Buff_Normal

class Buff_199021( Buff_Normal ):
	"""
	仙魔论战特用buff
	此buff将一个“统计被治疗量的技能”加到受术者的“被治疗时触发的技能列表（springReceiverCureList）”中
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
	
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		if receiver.getEntityType() != csdefine.ENTITY_TYPE_ROLE:			# 此buff只用在玩家身上
			return
		try:
			skill = g_skills[ self.param1 ]
		except:
			ERROR_MSG( "%i: skill %i not exist." % ( self.id, self.param1 ) )
			return
		receiver.appendReceiverCure( buffData[ "skill" ] )
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		fightMonster = receiver.queryTemp( "TDB_fightingMonster ", [] )
		if not fightMonster:
			return False
			
		for monsterID in copy.copy( fightMonster ):
			monster = BigWorld.entities.get( monsterID )
			if not monster or monster.targetID != receiver.id:
				fightMonster.remove( monsterID )
			
		if len( fightMonster ) == 0:					# 如果没有被任何仙魔论战怪物选为当前战斗目标，此buff移除
			receiver.removeTemp( "TDB_fightingMonster " )
			return False
			
		receiver.setTemp( "TDB_fightingMonster ", fightMonster )
		return Buff_Normal.doLoop( self, receiver, buffData )
			
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeCasterCure( buffData[ "skill" ].getUID() )