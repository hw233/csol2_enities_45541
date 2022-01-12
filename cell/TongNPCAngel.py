# -*- coding: gb18030 -*-

from bwdebug import *

from NPC import NPC


LIVE_TIME	= 600	# ����ֻ����10����

class TongNPCAngel( NPC ):
	"""
	������飬�����������黻��npc������һ������base��npc
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )
		self.setTemp( "destroyTimerID", self.addTimer( LIVE_TIME ) )	# LIVE_TIME����������
		
		
	def onTimer( self, controllerID, userData ):
		"""
		"""
		# ����������ǰ��һЩ����
		destroyTimerID = self.queryTemp( "destroyTimerID" )
		if destroyTimerID == controllerID:
			self.destroy()
			
			
	def lock( self ):
		"""
		define method.
		NPC����ס�� ����Ա�޷���������
		"""
		self.locked = True
		
		
	def unlock( self ):
		"""
		define method.
		NPC�������� ����Ա�ָ���������
		"""
		self.locked = False
		