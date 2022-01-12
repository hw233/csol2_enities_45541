# -*- coding: gb18030 -*-
#
#$Id: Buff_111002.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $


from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus
import random

from SpellBase import *
from Buff_Normal import Buff_Normal

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_JUMP

class Buff_111002( Buff_Normal ):
	"""
	ħ�����������ߣ�������������ʧѪ
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
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		
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
		id = buffData["caster"]
		if BigWorld.entities.has_key( id ):
			caster = BigWorld.entities[ id ]
			p = self.initPhysicsDotDamage( caster, receiver, self._p1 )
			#buffData[ "skill" ] = self.createFromDict( { "param":{ "p1":p } } )
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_PHYSICS, self._p1 )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage )
		return Buff_Normal.doLoop( self, receiver, buffData )
		
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
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		
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
		receiver.effectStateDec( csdefine.EFFECT_STATE_FIX )
		receiver.actCounterDec( STATES )
		
		
		
#$Id: Buff_111002.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $
#
#