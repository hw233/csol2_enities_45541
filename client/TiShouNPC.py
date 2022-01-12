# -*- coding: gb18030 -*-

from NPC import NPC
import BigWorld
import event.EventCenter as ECenter
from bwdebug import *

class TiShouNPC( NPC ):
	"""
	����NPC
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )


	def removeTSItem( self, uid ):
		"""
		define method
		"""
		print uid


	def testAddItem( self ):
		"""
		"""
		for i in xrange(255, 350):
			item = BigWorld.player().getItem_(i)
			if item:
				uid = BigWorld.player().getItem_(i).uid
				self.cell.addTSItem( uid, 100 )


	def receiveTSInfo( self, shopName, ownerDBID, destroyTime ):
		"""
		define method
		����������Ϣ
		"""
		if BigWorld.player().databaseID == ownerDBID : 							# ���Լ������۴���
			ECenter.fireEvent( "EVT_ON_TOGGLE_COMMISSION_SALE_WND", self, destroyTime )
		else :																# �鿴���˵�������Ʒ
			ECenter.fireEvent( "EVT_ON_TRIGGER_TISHOU_BUY_WINDOW", shopName, BigWorld.player().playerName, self )


	def onStartTS( self ):
		"""
		define method
		��ʼ����
		"""
		INFO_MSG( "begin sell" )

	def onStopTS( self ):
		"""
		define method
		��������
		"""
		INFO_MSG( "end sell" )

	def set_tsState( self, old ):
		"""
		����״̬�ı�
		"""
		if BigWorld.player().databaseID == self.ownerDBID :
			ECenter.fireEvent( "EVT_ON_TSNPC_FLAGS_CHANGED", old )

