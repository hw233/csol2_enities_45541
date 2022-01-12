# -*- coding: gb18030 -*-

import random
import BigWorld

import csstatus
import csdefine
from bwdebug import *

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal
STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP
BE_HOMING_MAX_SPEED = 50.0

class Buff_108007( Buff_Normal ):
	"""
	example:����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

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
		
		#�����������������Ǹ��ˣ���ô�����ƶ������ƶ�
		receiver.setTemp( "HOMING_TARGET", buffData["caster"] )

		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		# ִ�и���Ч��
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.effectStateInc( csdefine.EFFECT_STATE_BE_HOMING )
		else:
			receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterInc( STATES )
		if receiver.isMoving():
			# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
			receiver.stopMoving()
		
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.setTopSpeed( BE_HOMING_MAX_SPEED )	


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
		#�����������������Ǹ��ˣ���ô�����ƶ������ƶ�
		receiver.setTemp( "HOMING_TARGET", buffData["caster"] )
		# ִ�и���Ч��
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.effectStateInc( csdefine.EFFECT_STATE_BE_HOMING )
		else:
			receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterInc( STATES )
		if receiver.isMoving():
			# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
			receiver.stopMoving()
		
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.setTopSpeed( BE_HOMING_MAX_SPEED )
			
		
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
		#�����������������Ǹ��ˣ���ô�����ƶ������ƶ�
		receiver.removeTemp( "HOMING_TARGET" )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.effectStateDec( csdefine.EFFECT_STATE_BE_HOMING )
		else:
			receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterDec( STATES )
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.think( 0.1 )
		
