# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal

class Buff_299038( Buff_Normal ):
	"""
	��ɫ��һ�ι�������Ҫ����ħ�������Ч��������buff��������Ҫ��Buff_199025���ʹ��
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._loopSpeed = 1 	# ÿ1����һ��

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
		# ��Ӳ���Ҫ����ħ����־
		receiver.setTemp( "NOT_NEED_MANA", True )

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
		# ��Ӳ���Ҫ����ħ����־
		receiver.setTemp( "NOT_NEED_MANA", True )

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
		if not receiver.queryTemp( "NOT_NEED_MANA", False ):
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
		@return: None
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		# ȥ������Ҫ����ħ����־
		receiver.detachNotNeedManaEffect()