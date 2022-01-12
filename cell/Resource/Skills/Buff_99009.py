# -*- coding: gb18030 -*-

"""
�ı��̯���Ʊ��buff��buff������ı�Ϊ����״̬
"""
import csdefine
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99009( Buff_Normal ):
	"""
	�ı��̯���Ʊ��buff
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._vendSignboardNumber = ""
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._vendSignboardNumber = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 					# ���ܶ�Ӧ�İ�̯���Ʊ��
		
	def doBegin( self, receiver, buffData ):
		"""
		������̯���Ʊ��
		"""
		receiver.vendSignboardNumber = self._vendSignboardNumber
		
		Buff_Normal.doBegin( self, receiver, buffData )
	
	def doReload( self, receiver, buffData ):
		"""
		������̯���Ʊ��
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.vendSignboardNumber = self._vendSignboardNumber
	
	def doEnd( self, receiver, buffData ):
		"""
		������̯���Ʊ��
		"""
		receiver.vendSignboardNumber = ""
		
		Buff_Normal.doEnd( self, receiver, buffData )
		