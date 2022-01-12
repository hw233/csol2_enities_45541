# -*- coding: gb18030 -*-
#
# $Id: Buff_65004.py,v 1.4 12:16 2010-5-19 jiangyi Exp $

"""
持续性效果
"""
import random
import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_65004( Buff_Normal ):
	"""
	example:buff存在时效内，单位任何一次成功的物理攻击，均为攻击者恢复相当于本次伤害的x%的法力值
				并扣除目标等量的法力值。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #均为攻击者恢复相当于本次伤害的x%的生命值
		 
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0	
		self.odd = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

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
		n_odd = random.randint(0,100)
		if self.odd > 0 and n_odd > self.odd:
			return
		if skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS and skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL:
			return
		mpAdd = int( damage * self._p1 )
		if mpAdd > 0:
			caster.addMP( mpAdd )

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
# Revision 1.3  2007/12/21 04:21:10  kebiao
# 修正一些BUG
#
# Revision 1.2  2007/12/06 08:14:04  kebiao
# 修改BUG
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#