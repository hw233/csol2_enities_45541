# -*- coding: gb18030 -*-

import BigWorld
import Math
import gbref
from SpellBase import *
import csstatus
import csarithmetic

"""
向当前鼠标方向的位置进宪施法
"""
class Spell_Cursor( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def useableCheck( self, caster, target ):
		cursorPos = ( 0.0, 0.0, 0.0 )
		if target:
			cursorPos = target.getObjectPosition()
		new_yaw = (cursorPos - caster.position).yaw
		if abs( caster.yaw - new_yaw ) > 0.0:
			return csstatus.SKILL_CANT_DIRECTION_ERR

		return Spell.useableCheck( self, caster, target )

	def rotate( self, caster, receiver ):
		pass

class Spell_CursorCheckLine( Spell_Cursor ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def useableCheck( self, caster, target ):
		if target:
			result = csarithmetic.checkSkillCollide( caster.spaceID, caster.position, target.getObjectPosition() )
			if result:
				return csstatus.SKILL_CANT_ARRIVAL
		return Spell_Cursor.useableCheck( self, caster, target )

	def rotate( self, caster, receiver ):
		pass


class Spell_CursorAnyDirection( Spell_Cursor ) :
	"""
	对鼠标位置施放，不需要进行方向判断
	"""
	def useableCheck( self, caster, target ):
		"""
		避开基类的方向判断，由于基类已经配置了好多技能，因此
		这里不修改基类了，继承一个新类
		"""
		return Spell.useableCheck( self, caster, target )
