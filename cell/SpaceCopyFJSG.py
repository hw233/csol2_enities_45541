# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 20.0						#���ȫ���뿪�����󣬸���ø�����ɾ��

GOD_WEAPON_QUEST_FJSG			= 40202004		# ��������ID

class SpaceCopyFJSG( SpaceCopy ):
	# �⽣��
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.addTimer( 3600, 0, 3600 )		# 3600s�󣬸����Զ��ر�


	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]
	
	def onGodWeaponFJSG( self ):
		"""
		define method
		�����������
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_FJSG, 1 )