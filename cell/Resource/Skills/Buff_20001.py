# -*- coding: gb18030 -*-

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_20001( Buff_Normal ):
	"""
	Ǳ��buff
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		
		
	def springOnUseSkill( self, caster, skill ):
		"""
		ʹ�ü��ܱ�����
		"""
		caster.removeAllBuffByBuffID( self.getBuffID(), [ csdefine.BUFF_INTERRUPT_NONE ] )
		
	def springOnDamage( self, caster, skill ):
		"""
		�����˺���
		"""
		caster.removeAllBuffByBuffID( self.getBuffID(), [ csdefine.BUFF_INTERRUPT_NONE ] )
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.appendOnUseSkill( buffData[ "skill" ] )	# ʩչ����ʱ
		receiver.appendVictimHit( buffData[ "skill" ] )	# �����к�
		receiver.effectStateInc( csdefine.EFFECT_STATE_PROWL )
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.appendOnUseSkill( buffData[ "skill" ] )
		receiver.appendVictimHit( buffData[ "skill" ] )
		receiver.effectStateInc( csdefine.EFFECT_STATE_PROWL )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeOnUseSkill( buffData[ "skill" ].getUID() )
		receiver.removeVictimHit( buffData[ "skill" ].getUID() )
		receiver.effectStateDec( csdefine.EFFECT_STATE_PROWL )