# -*- coding: gb18030 -*-

from NPC import NPC
import BigWorld
import ECBExtend
import csconst
import Const
import csstatus
import csdefine
from MsgLogger import g_logger
from bwdebug import *

TI_SHOU_DATA_QUERY_MOD = 300		#����������Ʒ�ڶ��ķ�Χ��ȡģ��Ŀ���Ǵﵽ�Ƚ�ƽ�ȵĻ�ȡ�������ݵ�Ŀ��

class TiShouNPC( NPC ):
	"""
	����NPC
	"""
	def __init__( self ):
		NPC.__init__( self )
		self.base.setTSInfo( self.shopName, self.ownerName, self.destroyTime, self.ownerDBID )
		self.setTitle("")
		self.setName( self.shopName )
		"""
		����ͬʱ��ȡ�������ݶ��������ݿ������Ĵ���:
		�Ե�ǰ����NPC��id��TI_SHOU_DATA_QUERY_MOD ȡģ������ģ�Ľ��ȥ������timer��ʱ��
		"""
		if self.initByMgr:
			INFO_MSG("tishouNPC create from Mgr, when server start.")
			self.addTimer( self.id%TI_SHOU_DATA_QUERY_MOD / 10.0 , 0, ECBExtend.TISHOU_QUERY_DATA_CBID )
		else:
			INFO_MSG("tishouNPC create from player.")
			self.addTimer( 1.0 , 0, ECBExtend.TISHOU_QUERY_DATA_CBID )

	#---------------------------------- �ӿ� ---------------------------------------------------------
	def queryTSInfo( self, srcEntityID ):
		"""
		exposed method
		��ѯ����ҳ��
		"""
		if not self._isAllowOperate():
			return
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		player.clientEntity( self.id ).receiveTSInfo( self.shopName, self.ownerDBID, self.destroyTime )

	def startTS( self, srcEntityID ):
		"""
		exposed method
		���۲�����Ϊ��
		��ʼ��̯
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return
		if self._isTSing():
			return
		self._setTSState( True )
		player.startTS()
		player.clientEntity( self.id ).onStartTS()
		self.base.startTS()

	def stopTS( self, srcEntityID ):
		"""
		exposed method
		���۲�����Ϊ��
		ֹͣ��̯
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return

		if not self._isTSing():
			return

		self._setTSState( False )
		player.stopTS()
		player.clientEntity( self.id ).onStopTS()
		self.base.stopTS()

	def addTSItem( self, srcEntityID, uid, price ):
		"""
		exposed method
		���۲�����Ϊ��
		����������Ʒ
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return

		if self._isTSing():
			return

		player.addTSItem( uid, price, self.base )


	def takeTSItem( self, srcEntityID, uid, itemID, count ):
		"""
		exposed method
		���۲�����Ϊ��
		ȡ��������Ʒ
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return

		if self._isTSing():
			return

		player.takeTSItem( uid, self.base, itemID, count )

	def updateTSItemPrice( self, srcEntityID, uid, newPrice ):
		"""
		exposed method
		����������Ʒ�۸�
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return
		if self._isTSing():
			return

		self.base.updateTSItemPrice( uid, newPrice, player.databaseID, player.base )

	def takeTSMoney( self, srcEntityID ):
		"""
		exposed method
		ȡ�����۳ɽ���Ǯ
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return

		if self._isTSing():
			return

		self.base.takeTSMoney( player.base )


	def addTSPet( self, srcEntityID, dbid, price ):
		"""
		exposed method
		�������۳���
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return

		if self._isTSing():
			return

		player.addTSPet( dbid, price, self.base )

	def takeTSPet( self, srcEntityID, dbid ):
		"""
		exposed method
		ȡ�����۳���
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return

		if self._isTSing():
			return
		
		if player.pcg_isFull():
			player.client.onStatusMessage( csstatus.PET_CANNOT_TAKE_MORE, "" )
			return
		
		player.takeTSPet( dbid, self.base )

	def updateTSPetPrice( self, srcEntityID, dbid, newPrice ):
		"""
		exposed method
		�������۳���۸�
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return

		if self._isTSing():
			return
		self.base.updateTSPetPrice( dbid, newPrice, player.databaseID, player.base )


	def buyTSItem( self, srcEntityID, uid, itemID, count, price ):
		"""
		exposed method
		��������Ʒ
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isTSBuyer( player ):
			return

		if not self._isTSing():
			return
		player.buyTSItem( uid, self.base, itemID, count, price )
		try:
			g_logger.tiShouBuyItemLog( player.databaseID, player.getName(), self.ownerDBID, self.ownerName, uid, itemID, count, price )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def buyTSPet( self, srcEntityID, dbid, price ):
		"""
		exposed method
		�����۳���
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isTSBuyer( player ):
			return

		if not self._isTSing():
			return

		player.buyTSPet( dbid, self.base, price )
		try:
			g_logger.tiShouBuyPetLog( player.databaseID, player.getName(), self.ownerDBID, self.ownerName, dbid, price )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def queryTSItems( self, srcEntityID ):
		"""
		exposed method
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )

		if self._isTSBuyer( player ) and not self._isTSing():
			return
		if player:
			self.base.queryTSItems( player.base )

	def queryTSPets( self, srcEntityID ):
		"""
		exposed method
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )

		if self._isTSBuyer( player ) and not self._isTSing():
			return
		if player:
			self.base.queryTSPets( player.base )

	def takeOwnerToMe( self, playerBaseMB, way ):
		"""
		define method
		"""
		if way == 0:
			playerBaseMB.cell.gotoSpaceLineNumber( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.getCurrentSpaceLineNumber(), self.position, self.direction )
		else:
			playerBaseMB.client.moveToTSNPC( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.getCurrentSpaceLineNumber(), self.position, self.direction )

	def queryTSRecord( self, srcEntityID ):
		"""
		exposed method
		"""
		player = BigWorld.entities.get( srcEntityID, None )
		if player:
			self.base.queryTSRecord( player.base )


	def setShopName( self, srcEntityID, shopName ):
		"""
		exposed method
		"""
		if not self._isAllowOperate():
			return
		self._addOperateControl()
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		if not self._isOwner( player ):
			return
		self.shopName = shopName
		self.setName( shopName )
		self.base.setTSInfo( self.shopName, self.ownerName, self.destroyTime, self.ownerDBID )

	def updateTSNPCModel( self, srcEntityID, npcType ):
		"""
		exposed method
		��������NPCģ��
		"""
		player = BigWorld.entities[srcEntityID]
		
		if not self._isOwner( player ):
			return
		
		self.modelNumber =  Const.tsNpcs[npcType]
		
		BigWorld.globalData["TiShouMgr"].changeTiShouNPCModel( player.databaseID, Const.tsNpcs[npcType] )


	#---------------------------------- ˽�з��� ---------------------------------------------------------
	def _isTSBuyer( self, player ):
		"""
		���߼��
		"""
		#if not self._isTSing():				#���ڳ���״̬�ſ�������
		#	return False

		if self._isOwner( player ):
			return False
		return True


	def _setTSState( self, state ):
		"""
		��������״̬
		"""
		self.tsState = state

	def _isTSing( self ):
		"""
		�ǲ�������״̬
		"""
		return self.tsState


	def _isOwner( self, player ):
		"""
		�ǲ�������
		"""
		return player.databaseID == self.ownerDBID

	def _isAllowOperate( self ):
		"""
		�Ƿ�����������Ϊ����Ҫ���������Ʋ����ٶȵģ�
		"""
		return self.queryTemp( "allowOperate", True )


	def _addOperateControl( self ):
		"""
		���Ӳ�����ΪԼ��
		"""
		self.setTemp( "allowOperate", False )
		self.addTimer( 0.1, 0, ECBExtend.TISHOU_OPERATE_SPEED_CBID )


	def onAllowOperate( self, timerID, cbID ) :
		"""
		�������
		"""
		self.setTemp( "allowOperate", True )


	def onQueryTiShouData( self, timerID, cbID ):
		"""
		��ȡ�������ݣ�������Ʒ�����۳���չ���Ʒ��
		"""
		BigWorld.globalData["TiShouMgr"].queryTiShouData( self.base, self.ownerDBID )
		BigWorld.globalData["TiShouMgr"].addTiShouUnit( self.base, self.ownerDBID )