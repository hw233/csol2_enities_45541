# -*- coding: gb18030 -*-

from bwdebug import *

from NPC import NPC


LIVE_TIME	= 600	# 仙灵只存在10分钟

class TongNPCAngel( NPC ):
	"""
	帮会仙灵，帮会祭祀活动的仙灵换物npc，这是一个具有base的npc
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )
		self.setTemp( "destroyTimerID", self.addTimer( LIVE_TIME ) )	# LIVE_TIME后销毁自身
		
		
	def onTimer( self, controllerID, userData ):
		"""
		"""
		# 可以在销毁前做一些事情
		destroyTimerID = self.queryTemp( "destroyTimerID" )
		if destroyTimerID == controllerID:
			self.destroy()
			
			
	def lock( self ):
		"""
		define method.
		NPC被锁住， 帮会成员无法和他交互
		"""
		self.locked = True
		
		
	def unlock( self ):
		"""
		define method.
		NPC被开锁， 帮会成员恢复和他交互
		"""
		self.locked = False
		