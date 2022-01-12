# -*- coding:gb18030 -*-

from Buff_Normal import Buff_Normal
from bwdebug import *
import csdefine

class Buff_299027( Buff_Normal ):
	"""
	处理玩家vip时效的buff
	"""
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.vipLevel = int( data[ "Param1" ] if len( data[ "Param1" ] ) > 0 else 0 )
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.setVIP( self.vipLevel )
		
	def doReload( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setVIP( self.vipLevel )
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.setVIP( csdefine.ROLE_VIP_LEVEL_NONE )
		