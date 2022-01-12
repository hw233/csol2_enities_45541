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

class Monster_Potential(Monster):
	"""
	潜能任务怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
		self._potential = 0

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
		死亡；当selfEntity的die()被触发时被调用
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
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/04/15 06:03:07  kebiao
# 修正die接口
#
# Revision 1.3  2008/02/18 08:52:24  kebiao
# 增加初始化加载该怪对应的潜能点
#
# Revision 1.2  2008/02/03 00:52:04  kebiao
# 潜能任务调整
#
# Revision 1.1  2008/01/28 06:12:36  kebiao
# no message
#
#
