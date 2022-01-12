# -*- coding: gb18030 -*-

"""
�ӳٴ��ͼ���
"""
import BigWorld
import Math
import csconst
from gbref import rds
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

	def receiveSpell( self, target, casterID, damageType, damage ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				return

		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		�ܻ�Ч����������Ч��
		"""
		if caster is None: return
		if target != player: return # ��������Լ�
		if caster.position.distTo( target.position ) >= csconst.PLAYER_TO_NPC_DISTANCE: return
		id = self.getID()
		self.pose.hit( id, target )
		rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )

		target.delayTeleport( self, caster, self._spaceName, self._pos, self._npcName, self._delayTime )  # �ӳٴ��ͽӿ�