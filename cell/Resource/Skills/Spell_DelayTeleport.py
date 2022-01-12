# -*- coding:gb18030 -*-

import BigWorld
import Math
from bwdebug import *
from SpellBase import *

class Spell_DelayTeleport( Spell ):
	"""
	�ӳٴ���
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		# ��������
		self._spaceName = ""         # �ռ�����
		self._pos = Math.Vector3()	 # ����
		self._npcName = ""			 # NPC����
		self._delayTime = 0			 # �ӳ�ʱ��

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		self._spaceName = dict["param1"] if len( dict["param1"] ) > 0 else ""
		pos = dict["param2"] if len( dict["param2"] ) > 0 else ""
		if pos:
			self._pos = Math.Vector3( eval( pos ) )
		self._npcName = dict["param3"] if len( dict["param3"] ) > 0 else ""
		self._delayTime = int( dict["param4"] if len( dict["param4"] ) > 0 else 0 )

	def receive( self, caster, receiver ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		if caster.isReal():
			Spell.receive( self, caster, receiver )

		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )
