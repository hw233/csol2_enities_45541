# -*- coding: gb18030 -*-
#
# $Id: Buff_65002.py,v 1.7 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_65002( Buff_Normal ):
	"""
	example:同归于尽	BUFF	所有伤害/伤害反射	BUFF存在时受到的伤害提高一定百分比，并使攻击者受到该伤害数值的一定百分比的无类型伤害%
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #受到的伤害提高加成
		self._p2 = 0 #反射伤害比率
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  / 100.0	

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
		#使自己受到的所有伤害提高，并且按此时受到伤害的x%反还给攻击者，这个返还的伤害是不走命中、防御、闪避、招架、暴击的
		rebound_damage = damage * self._p2
		rebound_damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_VOID, rebound_damage )		
		if rebound_damage <= 0: return
		caster.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_VOID, rebound_damage, 0 )
		caster.receiveDamage( receiver.id, 0, csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_VOID, rebound_damage )
		
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
		receiver.receive_damage_percent += self._p1
		receiver.receive_magic_damage_percent += self._p1
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )
		
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
		receiver.receive_damage_percent += self._p1
		receiver.receive_magic_damage_percent += self._p1
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )
		
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
		receiver.receive_damage_percent -= self._p1
		receiver.receive_magic_damage_percent -= self._p1
		receiver.removeVictimAfterDamage( buffData[ "skill" ].getUID() )
#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/08/11 07:55:59  kebiao
# 修正BUFF伤害在DOLOOP时 未进行护盾吸收操作
#
# Revision 1.5  2008/04/10 04:08:26  kebiao
# 改为在接受伤害之前通知客户端接受技能处理
#
# Revision 1.4  2008/04/10 03:25:50  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.3  2008/03/31 09:04:02  kebiao
# 修改receiveDamage和通知客户端接受某技能结果分开
# 技能通过receiveSpell通知客户端去表现，支持各技能不同的表现
#
# Revision 1.2  2008/02/28 08:25:56  kebiao
# 改变删除技能时的方式
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#