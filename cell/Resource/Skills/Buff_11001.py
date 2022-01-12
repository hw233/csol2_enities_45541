# -*- coding: gb18030 -*-

#����buff
#����λ�Ƽ���Ч����Ӱ��,����ѣ�Ρ�������˯BUFFЧ����Ӱ��,�������ܻ������Ĳ���
#by wuxo 2012-3-21 
	

"""
������Ч��
"""

# common
import csdefine
import csstatus
from bwdebug import *
# cell
from Buff_Normal import Buff_Normal



class Buff_11001( Buff_Normal ):
	"""
	����buffer
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._immuneBuffs = []		#���ߵ�buff id
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict[ "Param1" ] != "":
			self._immuneBuffs =  eval( dict[ "Param1" ] )
		
	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		bid = buff.getBuffID()
		if bid in self._immuneBuffs: #Ҫ���ߵ�buff
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
		receiver.effectStateInc( csdefine.EFFECT_STATE_HEGEMONY_BODY )
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		
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
		receiver.effectStateDec( csdefine.EFFECT_STATE_HEGEMONY_BODY )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		