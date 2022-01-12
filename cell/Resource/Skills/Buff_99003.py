# -*- coding: gb18030 -*-
#
# $Id:Exp $

"""
������Ч��
"""

from Buff_Normal import Buff_Normal


class Buff_99003( Buff_Normal ):
	"""
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
		self.param1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" )  		#��ʱ�����б�Key
		self.param2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 			#ʹ�ú󣬱�����������
		self.param3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 ) 			#ʹ�þ���
		self.param4 = 0
		self.param5 = 5
		
		if self.param2 == 0:
			self.param2 = 1
		
		if self.param1 == "":
			self.param1 = 'callMonstersTotal'
		
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
		self.param4 = receiver.queryTemp( self.param1, 0 )
		# self.param5 = receiver.queryTemp( 'callMonstersTimeTotal', 0 )
		receiver.setTemp( self.param1, self.param2 )	# �йָ���
		receiver.setTemp( 'callMonstersTimeTotal', 3 )	# �йִ���
		Buff_Normal.doBegin( self, receiver, buffData )
		
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
		self.param4 = receiver.queryTemp( self.param1, 0 )
		# self.param5 = receiver.queryTemp( 'callMonstersTimeTotal', 0 )
		receiver.setTemp( self.param1, self.param2 )	# �йָ���
		receiver.setTemp( 'callMonstersTimeTotal', 3 )	# �йִ���
		Buff_Normal.doReload( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.setTemp( self.param1, self.param4 )				# �йָ���
		receiver.setTemp( 'callMonstersTimeTotal', self.param5 )	# �йִ���
		Buff_Normal.doEnd( self, receiver, buffData )

