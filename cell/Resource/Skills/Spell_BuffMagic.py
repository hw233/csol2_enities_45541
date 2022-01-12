# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffMagic.py,v 1.4 2008-08-13 07:55:41 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
import random
from Spell_Item import Spell_Item
from Spell_Magic import Spell_Magic
from Spell_Magic import Spell_MagicVolley

class Spell_BuffMagic( Spell_Magic ):
	"""
	释放法术伤害型BUFF， 这个技能本身并不产生伤害， 但是他走法术技能 击中 命中路线
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Magic.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		damageType = self._damageType
		
		# 计算命中率
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return
			
		self.receiveLinkBuff( caster, receiver )
		# 执行命中后的行为
		caster.doAttackerOnHit( receiver, damageType )	#攻击者触发
		receiver.doVictimOnHit( caster, damageType )   #受击者触发
		
class Spell_BuffMagicVolley( Spell_MagicVolley ):
	"""
	释放法术伤害型BUFF， 这个技能本身并不产生伤害， 但是他走法术技能 击中 命中路线
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_MagicVolley.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_MagicVolley.init( self, dict )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		damageType = self._damageType
		# 计算命中率
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return
			
		self.receiveLinkBuff( caster, receiver )
		# 执行命中后的行为
		caster.doAttackerOnHit( receiver, damageType )	#攻击者触发
		receiver.doVictimOnHit( caster, damageType )   #受击者触发
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/07/04 03:50:57  kebiao
# 对效果状态的实现优化
#
# Revision 1.2  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.1  2008/05/27 02:10:37  kebiao
# no message
#
#