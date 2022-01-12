# -*- coding: gb18030 -*-
#
# $Id: Spell_522612.py,v 1.7 2008-06-26 00:54:56 zhangyuxing Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_Magic import Spell_Magic
import random
import csdefine

class Spell_522612( Spell_Magic ):
	"""
	法术技能
	攻击目标，造成目标法力值的减少，减少的数值成为宠物的法力值
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

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		SkillMessage.spell_ConsumeMP( self, caster, receiver, damage )
		#damage = caster.calcShieldSuck( receiver, damage, self._damageType )
		receiver.addMP( -damage )
		caster.addMP( damage )
			
			
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/02/25 09:29:18  kebiao
# 修改 护盾减伤相关
#
# Revision 1.5  2008/02/13 08:46:53  kebiao
# 修改了底层结构
#
# Revision 1.4  2008/01/30 06:06:16  kebiao
# no message
#
# Revision 1.3  2007/12/26 09:03:57  kebiao
# no message
#
# Revision 1.2  2007/12/26 08:19:50  kebiao
# no message
#
# Revision 1.1  2007/12/26 03:54:24  kebiao
# no message
#
#