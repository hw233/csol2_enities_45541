# -*- coding: gb18030 -*-

"""
����˲��
"""
import csdefine
from bwdebug import *
from SpellBase import *
from utils import vector3TypeConvert

class Spell_MonsterTeleport( Spell ):
	"""
	����˲�Ƶ�ָ���ص㣨���޵�ǰ��ͼ��
	param1��λ�ã���x,y,z
	param2�����򣩣�x,y,z�����Ÿ���
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Spell.__init__( self )
		self._position = ( 0.0, 0.0, 0.0 )	# λ��
		self._direction = ( 0.0, 0.0, 0.0 )	# ����

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		position = dict["param1"] if dict["param1"] else ""
		direction = dict["param2"] if dict["param2"] else ""
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error: skillID(%s), param1(%s)" % ( self.getID(), position ) )
			else:
				self._position = pos

		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error: skillID(%s), param2(%s)" % ( self.getID(), direction ) )
			else:
				self._direction = dir

	def __allowTeleport( self, entity ):
		"""
		entity��ǰ״̬�Ƿ����˲��
		@return bool
		"""
		if entity.effect_state & csdefine.EFFECT_STATE_VERTIGO: #ѣ��
			return False	
		if entity.effect_state & csdefine.EFFECT_STATE_SLEEP: #��˯
			return False
		if entity.effect_state & csdefine.EFFECT_STATE_FIX:	#����
			return False
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ): #�������ƶ���־
			return False
		return True

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if not self.__allowTeleport( receiver ):
			return

		receiver.position = self._position
		receiver.spawnPos = self._position
		receiver.direction = self._direction
		receiver.closeVolatileInfo()
		receiver.openVolatileInfo()
		receiver.planesAllClients( "setFilterLatency", () ) #˲���ƶ��������л������
		receiver.stopMoving()
		self.receiveLinkBuff( caster, receiver ) #֧��buff