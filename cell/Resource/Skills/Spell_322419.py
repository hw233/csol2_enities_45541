# -*- coding: gb18030 -*-
#
from Spell_BuffNormal import Spell_BuffNormal
import random
import csdefine
import csstatus

class Spell_322419( Spell_BuffNormal ):
	"""
	���㼼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )

	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ��
		"""
		# ֻ����Ǳ��״̬��ʹ��
		if caster.effect_state & csdefine.EFFECT_STATE_PROWL == 0:
			return csstatus.SKILL_NEED_STATE_PROWL
		# �޷��������ʹ��
		if caster.vehicleModelNum:
			return csstatus.SKILL_NEED_STATE_NO_VEHICLE
		return Spell_BuffNormal.useableCheck( self, caster, receiver )