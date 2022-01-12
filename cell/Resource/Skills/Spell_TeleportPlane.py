# -*- coding: gb18030 -*-

# add by gjx 7/1/14

"""
���ͼ��ܻ���
"""

from SpellBase import *
from bwdebug import *
import csconst
import csdefine

class Spell_TeleportPlane( Spell ):
	"""
	λ�洫�ͼ��ܻ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self._planeType = "" #λ���ͼ����

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._planeType =  dict["param1"].strip()   	#��ͼ����

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isReal():
			if receiver.spaceType != self._planeType:
				receiver.setTemp("MOVE_INTO_PLANE", True)
				receiver.enterPlane(self._planeType)
		else:
			receiver.receiveOnReal(caster.id, self)


class Spell_TeleportPlaneOnEnterTrap(Spell_TeleportPlane):
	"""
	��������ʱ������λ�洫��
	"""

	def __init__( self ):
		"""
		���캯����
		"""
		Spell_TeleportPlane.__init__(self)

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# ֻ�����ʩ�ţ����������
			return

		if receiver.isReal():
			tp_plane_counter = receiver.queryTemp("TP_PLANE_COUNTER", 0)
			receiver.setTemp("TP_PLANE_COUNTER", tp_plane_counter + 1)
			INFO_MSG("----->>> Enter: TP_PLANE_COUNTER of %i is %i" % (receiver.id, tp_plane_counter))
			if tp_plane_counter <= 0 and self._planeType:
				INFO_MSG("----->>> Enter: Role %i has been teleported to plane %s" % (receiver.id, self._planeType))
				Spell_TeleportPlane.receive(self, caster, receiver)
		else:
			receiver.receiveOnReal(caster.id, self)


class Spell_TeleportPlaneOnLeaveTrap(Spell_TeleportPlane):
	"""
	�뿪����ʱ������λ�洫��
	"""

	def __init__( self ):
		"""
		���캯����
		"""
		Spell_TeleportPlane.__init__(self)

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# ֻ�����ʩ�ţ����������
			return

		if receiver.isReal():
			tp_plane_counter = receiver.queryTemp("TP_PLANE_COUNTER", 0)
			INFO_MSG("----->>> Leave: TP_PLANE_COUNTER of %i is %i" % (receiver.id, tp_plane_counter))
			if tp_plane_counter <= 1:
				receiver.removeTemp("TP_PLANE_COUNTER")
				if self._planeType:
					INFO_MSG("----->>> Leave: Role %i has been teleported to plane %s" % (receiver.id, self._planeType))
					Spell_TeleportPlane.receive(self, caster, receiver)
			else:
				receiver.setTemp("TP_PLANE_COUNTER", tp_plane_counter - 1)
		else:
			receiver.receiveOnReal(caster.id, self)

#