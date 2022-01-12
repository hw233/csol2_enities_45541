# -*- coding: gb18030 -*-
#
# $Id: Spell_312602.py,v 1.7 2008-08-13 02:24:55 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
import random
import csdefine

class Spell_312602( Spell ):
	"""
	来去自如 解除自身的眩晕和定身状态，在眩晕状态下可以使用。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self._p1 = 150
		
	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF
		self._p1 = int( dict.get( "param1" , 0 ) )		# 能够清除BUFF的最高等级
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
			
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		for index, buff in enumerate( receiver.getBuffs() ):
			skill = buff["skill"]
			if skill.getLevel() <= self._p1:# 只能驱散比自己级别底的BUFF
				receiver.removeBuff( index, self._triggerBuffInterruptCode )
				break
						

# $Log: not supported by cvs2svn $
# Revision 1.6  2008/05/28 05:59:47  kebiao
# 修改BUFF的清除方式
#
# Revision 1.5  2007/12/17 01:36:36  kebiao
# 调整PARAM0为param1
#
# Revision 1.4  2007/12/06 01:24:22  kebiao
# 修改了一个可能导致的BUG
#
# Revision 1.3  2007/11/30 08:45:13  kebiao
# csstatus.BUFF_INTERRUPT
# TO：
# csdefine.BUFF_INTERRUPT
#
# Revision 1.2  2007/11/29 09:04:14  kebiao
# 修改BUG
#
# Revision 1.1  2007/11/24 08:35:30  kebiao
# no message
#