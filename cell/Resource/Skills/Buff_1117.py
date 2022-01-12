# -*- coding:gb18030 -*-
import BigWorld
import csconst
import csdefine

from Buff_Normal import Buff_Normal
from bwdebug import *

STATE = csdefine.EFFECT_STATE_NO_FIGHT

class Buff_1117( Buff_Normal ):
	"""
	����սս����Աר��buff : ȡ����ս�������е���
	"""
	def __init__( self ):
		Buff_Normal.__init__( self )
		#self.reduceDamagePoint = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		#self.reduceDamagePoint = int( dict["Param1"] )
	
	def doBegin( self, receiver, buffData ):
		# ��״̬
		receiver.effectStateDec( STATE )
		Buff_Normal.doBegin( self, receiver, buffData )
		#receiver.reduce_role_damage_extra += self.reduceDamagePoint
		#receiver.calcReduceRoleDamage()
		
	def doLoop( self, receiver, buffData ):
		"""
		"""
		if not ( receiver.queryTemp( "turnWar_isFightPlayer", False ) or receiver.queryTemp( "campTurnWar_isFightPlayer", False  ) ):		# ûս�����Ƴ�buff
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.effectStateInc( STATE )
		#receiver.reduce_role_damage_extra -= self.reduceDamagePoint
		#receiver.calcReduceRoleDamage()
		Buff_Normal.doEnd( self, receiver, buffData )
		