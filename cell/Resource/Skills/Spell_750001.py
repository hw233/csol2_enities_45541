# -*- coding: gb18030 -*-
#
# $Id: Spell_312602.py,v 1.7 2008-08-13 02:24:55 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
import random
import csdefine

class Spell_750001( Spell ):
	"""
	遗忘技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
			
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return		
		receiver.removeSkill( receiver.popTemp( "clearSkillID" ) )

# $Log: not supported by cvs2svn $
#