# -*- coding: gb18030 -*-

import BigWorld
import Math
import gbref
from SpellBase import *
import csstatus
import csarithmetic

"""
��ǰ��귽���λ�ý���ʩ��
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
	�����λ��ʩ�ţ�����Ҫ���з����ж�
	"""
	def useableCheck( self, caster, target ):
		"""
		�ܿ�����ķ����жϣ����ڻ����Ѿ������˺ö༼�ܣ����
		���ﲻ�޸Ļ����ˣ��̳�һ������
		"""
		return Spell.useableCheck( self, caster, target )
