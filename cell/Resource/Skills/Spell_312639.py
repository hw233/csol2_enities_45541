# -*- coding:gb18030 -*-

#

from bwdebug import *
from Spell_Magic import Spell_Magic
import csdefine


class Spell_312639( Spell_Magic ):
	"""
	�����
	"""
	def receive( self, caster, receiver ):
		"""
		"""
		Spell_Magic.receive( self, caster, receiver )
		if caster.utype == csdefine.ENTITY_TYPE_ROLE :		# ���ʩ��������ң�������ֻ��½������ modify by dqh 2012-03-28
			if not bool( receiver.findBuffByBuffID( csdefine.FLYING_BUFF_ID )):
				receiver.retractVehicle( receiver.id )
		else:												# ���ʩ���߲������,��������½�С���������
			receiver.retractVehicle( receiver.id )
