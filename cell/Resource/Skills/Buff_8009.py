# -*- coding: gb18030 -*-
#

"""
����״̬��buff by mushuang
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_6005 import Buff_6005
from csdefine import ROLE_FLAG_FLY, PET_WITHDRAW_BUFF

class Buff_8009( Buff_6005 ):
	"""
	��buff��������ʹ�ã��������ط�ʹ�û�����������Buff_Vehicle�е�ʵ��
	���Գ����Ƿ���������жϣ�����GMָ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_6005.__init__( self )
		
	def __setupEffect( self, receiver ):
		"""
		��receiver���Ӵ�buff��Ч��
		"""
		# �趨���Ϊ���б�־
		receiver.addFlag( ROLE_FLAG_FLY )
		
		# ����г�ս������ջس���
		actPet = receiver.pcg_getActPet()
		if actPet:
			actPet.entity.withdraw( PET_WITHDRAW_BUFF )
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		# param1: �ٶ����ӵİٷֱȣ����������Ҫ�ٶ�����50%���뽫param1����Ϊ50
		
		Buff_6005.init( self, dict )
		
		
		# ����ٶȵ�����ٷֱȳ��������ֵ����ô����Ϊ���ֵ
		if self.speedIncPercent > csconst.MAX_FLYING_SPEED_INC_PERCENT:
			self.speedIncPercent = csconst.MAX_FLYING_SPEED_INC_PERCENT
		
	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		Buff_6005.receive( self, caster, receiver )

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
		
		self.__setupEffect( receiver )
		
		# �����ƶ��ٶȲ������buff���ص��������
		Buff_6005.doBegin( self, receiver, buffData )

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
		self.__setupEffect( receiver )
		
		# �����ƶ��ٶȲ������buff���ص��������
		Buff_6005.doReload( self, receiver, buffData )
			
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		
		# �Ƴ�������ϵķ��б�־
		receiver.removeFlag( ROLE_FLAG_FLY )
		
		# �ָ��ƶ��ٶȣ�����������ϳ����������buff
		Buff_6005.doEnd( self, receiver, buffData )


#
# $Log: not supported by cvs2svn $
#
#