# -*- coding: gb18030 -*-
#
# $Id: Buff_18001.py,v 1.4 2008-08-29 07:16:10 qilan Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_18001( Buff_Normal ):
	"""
	example:每次普通攻击都获得所造成伤害的一定比例的生命值
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #%i%%的几率
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0	

	def springOnDamage( self, caster, receiver, skill, damage ):
		"""
		virtual method.
		在伤害计算后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在受到伤害以后再触发的效果；

		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   skill: 技能实例
		@type    skill: Entity
		@param   damage: 施法者造成的伤害
		@type    damage: int32
		"""
		restore = int( damage * self._p1 + 0.5 )							# 计算获取的HP，取整
		if restore > 0: 
			caster.addHP( restore )
		
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
		receiver.appendAttackerAfterDamage( buffData[ "skill" ] )
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.appendAttackerAfterDamage( buffData[ "skill" ] )
		
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
		receiver.removeAttackerAfterDamage( buffData[ "skill" ].getUID() )
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/02/28 08:25:56  kebiao
# 改变删除技能时的方式
#
# Revision 1.2  2007/12/21 04:21:10  kebiao
# 修正一些BUG
#
# Revision 1.1  2007/12/20 05:44:03  kebiao
# no message
#
#