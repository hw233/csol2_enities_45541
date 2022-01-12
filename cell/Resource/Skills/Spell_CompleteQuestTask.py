# -*- coding: gb18030 -*-

from SpellBase import *
import csdefine

class Spell_CompleteQuestTask( Spell ):
	"""
	���ָ������Ŀ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.questID = 0	# ����ID
		self.taskIdx = 0	# ����Ŀ������

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.questID = int( dict["param1"] )
		self.taskIdx = int( dict["param2"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return

		if receiver.hasTaskIndex( self.questID, self.taskIdx ):
			receiver.questTaskIncreaseState( self.questID, self.taskIdx )
