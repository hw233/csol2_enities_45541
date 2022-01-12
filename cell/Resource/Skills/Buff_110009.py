# -*- coding: gb18030 -*-

from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_110009( Buff_Normal ):
	"""
	增加receiver受到伤害时的暴击几率。
	"""
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.beDoubleHitrate = int( data["Param1"] if len( data["Param1"] ) > 0 else 0 ) * 100		# 增加的被暴击概率( 0 - 100 )
		
	def doBegin( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.be_double_hit_probability += self.beDoubleHitrate
		
	def doReload( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.be_double_hit_probability += self.beDoubleHitrate
		
	def doEnd( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.be_double_hit_probability -= self.beDoubleHitrate
		