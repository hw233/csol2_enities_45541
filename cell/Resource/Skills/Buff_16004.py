# -*- coding: gb18030 -*-
#
# $Id: Buff_16004.py,v 1.12 2008-08-11 07:55:59 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Rebound import Buff_Rebound_Magic

class Buff_16004( Buff_Rebound_Magic ):
	"""
	example:效果存在时将所受到的法术攻击力转移一定数值到攻击者身上。（被转移单位不能为自身）

	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Rebound_Magic.__init__( self )
		self._p1 = 0 #
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Rebound_Magic.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) 	

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
		if caster.id == receiver.id or receiver.state == csdefine.ENTITY_STATE_DEAD or skill.getType() != csdefine.BASE_SKILL_TYPE_MAGIC:
			return
		
		value = int( self.initPhysicsDotDamage( receiver, caster, self._p1 ) )
		value = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_MAGIC, value )
		if value <= 0:
			return
		caster.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_MAGIC, value, 0 )
		caster.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_MAGIC, value )
		SkillMessage.buff_ReboundDamageMagic( caster, receiver, value )

#
# $Log: not supported by cvs2svn $
# Revision 1.11  2008/04/10 04:08:26  kebiao
# 改为在接受伤害之前通知客户端接受技能处理
#
# Revision 1.10  2008/04/10 03:25:50  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.9  2008/03/31 09:04:02  kebiao
# 修改receiveDamage和通知客户端接受某技能结果分开
# 技能通过receiveSpell通知客户端去表现，支持各技能不同的表现
#
# Revision 1.8  2008/02/13 09:26:30  kebiao
# 将技能ID也传输到客护短,使其显示伤害
#
# Revision 1.7  2008/02/13 08:54:58  kebiao
# 修正反弹伤害没有施法者ID
#
# Revision 1.6  2008/02/13 08:41:30  kebiao
# 添加相关提示信息
#
# Revision 1.5  2008/01/30 08:59:37  kebiao
# 修改反弹信息处理方式
#
# Revision 1.4  2008/01/30 07:07:46  kebiao
# 修改了继承关系
#
# Revision 1.3  2007/12/21 08:52:11  kebiao
# no message
#
# Revision 1.2  2007/12/21 07:28:00  kebiao
# no message
#
# Revision 1.1  2007/12/20 03:34:17  kebiao
# no message
#
#