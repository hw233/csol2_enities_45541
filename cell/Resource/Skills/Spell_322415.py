# -*- coding: gb18030 -*-
#
from Spell_BuffNormal import Spell_BuffNormal
import random
import csdefine
import csstatus

class Spell_322415( Spell_BuffNormal ):
	"""
	���似��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )
		self._isCanFight = 0  #�Ƿ��ս��״̬��ʹ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell_BuffNormal.init( self, dict )
		if dict["param1"] != "":
			self._isCanFight = int( dict["param1"] )	

	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ��
		"""
		if not self._isCanFight: #0 ֻ��������״̬��ʹ��
			if caster.state != csdefine.ENTITY_STATE_FREE:
				return csstatus.SKILL_NEED_STATE_FREE
		return Spell_BuffNormal.useableCheck( self, caster, receiver )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet:
				petEntiy = actPet.entity
				if not petEntiy.isReal():
					petEntiy.receiveOnReal( caster.id, self )
				else:
					self.receiveLinkBuff( caster, petEntiy )
