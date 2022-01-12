# -*- coding:gb18030 -*-

from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_104005( Buff_Normal ):
	"""
	效果：物理防御力降低%，按百分比降低物理防御力。
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0
		
	def init( self, data ):
		"""
		armor_percent
		"""
		Buff_Normal.init( self, data )
		self.param1 = float( data["Param1"] if len( data["Param1"] ) > 0 else 0 ) * 100
		
	def doBegin( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.armor_percent -= self.param1
		receiver.calcArmor()
		
	def doReload( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.armor_percent -= self.param1
		
	def doEnd( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.armor_percent += self.param1
		receiver.calcArmor()