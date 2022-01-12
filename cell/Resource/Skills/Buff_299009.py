# -*- coding: gb18030 -*-
#
# ������ϵͳ֮ ƣ�� debuff 2009-03-20 SongPeifang
#

from Buff_Normal import Buff_Normal

class Buff_299009( Buff_Normal ):
	"""
	������ϵͳ֮ ƣ��debuff
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
		receiver.setTemp( "anti_indulgence_tired", True )

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
		receiver.setTemp( "anti_indulgence_tired", True )
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���
		"""
		# �����ƣ�͵ı��
		receiver.removeTemp( "anti_indulgence_tired" )