# -*- coding:gb18030 -*-

from bwdebug import *
from Buff_8006 import Buff_8006

class Buff_99026( Buff_8006 ):
	"""
	��ʱ�������buff����һ�ô�buff����Է���
	"""
	def __init__( self ):
		"""
		"""
		Buff_8006.__init__( self )
		self.vehicleModelNum = 0
		
	def init( self, data ):
		"""
		"""
		Buff_8006.init( self, data )
		self.vehicleModelNum = int( data["Param2"] if len( data["Param2"] ) > 0 else 9110032 )	# 9110032Ϊ���¹�ģ�ͱ��
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_8006.doBegin( self, receiver, buffData )
		receiver.vehicleModelNum = self.vehicleModelNum
		
	def doReload( self, receiver, buffData ):
		"""
		"""
		Buff_8006.doReload( self, receiver, buffData )
		receiver.vehicleModelNum = self.vehicleModelNum
		