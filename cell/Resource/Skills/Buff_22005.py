# -*- coding: gb18030 -*-
#
# $Id: Buff_22005.py,v 1.2 2008-08-05 08:44:27 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random
import csconst
				 
class Buff_22005( Buff_Normal ):
	"""
	example:�޵�R	BUFF	��������Ч�����������˺�����������100%��	���ڸ�Ч��ʱ�����зǵ�λ��Դ�ĸ���Ӱ�춼������Լ�����Ч����������Ϣ��ʾ�����ߡ���
	����������
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
		self.spaceNames = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) .split("|")	
		self._loopSpeed = 3 # ǿ��3����һ��
		
	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		isRayRingEffect = buff.isRayRingEffect()

		if not isRayRingEffect and buff.isMalignant(): #�Ƕ��Ե����ǹ⻷Ч�� ��ô����
			return csstatus.SKILL_BUFF_IS_RESIST
		elif isRayRingEffect:   # �ǹ⻷Ч��
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# �߻��涨�� ������Լ��ͷŵĶ��Թ⻷Ч���� ���޵п�������
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
					return csstatus.SKILL_BUFF_IS_RESIST
		
		return csstatus.SKILL_GO_ON
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�
		dels = []
		
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# �߻��涨�� ������Լ��ͷŵĶ��Թ⻷Ч���� ���޵п�������
				if buffData[ "caster" ] == caster.id:
					dels.append( idx )
				else:				
					receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
					
		for i in dels:
			receiver.removeBuff( i, [ 0 ] )
			
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )

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
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if not spaceType in self.spaceNames:
			return False
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
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		dels = []
		
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# �߻��涨�� ������Լ��ͷŵĶ��Թ⻷Ч���� ���޵п�������
				if buffData[ "caster" ] == caster.id:
					dels.append( idx )
				else:				
					receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
					
		for i in dels:
			receiver.removeBuff( i, [ 0 ] )
			
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
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
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# �߻��涨�� ������Լ��ͷŵĶ��Թ⻷Ч���� ���޵п�������
				if buffData[ "caster" ] != caster.id:			
					receiver.removeBuffState( idx, csdefine.BUFF_STATE_DISABLED )
					
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/08/05 06:36:02  kebiao
# no message
#
#
#