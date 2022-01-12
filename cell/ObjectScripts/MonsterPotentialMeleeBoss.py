# -*- coding: gb18030 -*-
#
# $Id: Monster_Potential.py,v 1.5 2008-04-15 06:19:17 kebiao Exp $

"""
怪物NPC的类
"""
import BigWorld
from Monster import Monster
from bwdebug import *
import csconst
import csdefine

class MonsterPotentialMeleeBoss(Monster):
	"""
	潜能乱斗怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		Monster.onLoadEntityProperties_( self, section )
		
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
			spaceEntity.getScript().onMeleeDie( spaceEntity, killer, tuple( selfEntity.spawnPos ) )
		elif spaceBase:
			spaceBase.cell.remoteScriptCall( "onMeleeDie", ( killer, tuple( selfEntity.spawnPos ), ) )

#
# $Log: not supported by cvs2svn $
#
#
