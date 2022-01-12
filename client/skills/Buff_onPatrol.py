# -*- coding: gb18030 -*-
"""
Ѳ��buff����ɫ���������ϣ�������ҿ��ƣ��ɷ�����֪ͨ�ƶ�
"""
import BigWorld
import Define
from SpellBase import Buff


class Buff_onPatrol( Buff ):
	"""
	Ѳ��buff����ɫ���������ϣ�������ҿ��ƣ��ɷ�����֪ͨ�ƶ�
	"""
	def __init__( self ):
		"""
		"""
		Buff.__init__( self )
		self.targetPreFilter = None

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_ONPATROL )
			self.targetPreFilter = target.filter
			target.filter = BigWorld.AvatarFilter()

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		if target.id == BigWorld.player().id:
			target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_ONPATROL )
			target.filter = self.targetPreFilter
