# -*- coding: gb18030 -*-
# 摆摊

import BigWorld
import time

from bwdebug import *

import csdefine
import csconst
import csstatus
import random

class RoleVend:
	"""
	玩家摆摊系统
	"""
	def __init__( self ):
		"""
		"""
		pass

	def vend_petForSale( self, databaseID, price ):
		"""
		宠物摆摊出售
		"""
		epitome = self.pcg_getPetEpitome( databaseID )

		# 标记宠物为摆摊出售中
		epitome.updateAttr( "isInVend", True )
		epitome.updateAttr( "vendSellPrice", price )

	def vend_petEndForSale( self, databaseID ):
		"""
		宠物下架，停止宠物待售
		"""
		epitome = self.pcg_getPetEpitome( databaseID )
		# 解除宠物待售标记
		epitome.updateAttr( "isInVend", False )
		epitome.updateAttr( "vendSellPrice", 0 )

	def vend_buyerQueryPetInfo( self, buyerBaseMailBox, vendPetMerchandise ):
		"""
		给买方下发卖方的宠物信息
		"""
		epitomes = []
		for e in vendPetMerchandise:
			epitome = self.pcg_getPetEpitome( e["databaseID"] )
			epitomes.append( epitome )

		buyerBaseMailBox.client.vend_receivePetData( epitomes )

	def vend_sellPet( self, buyerBaseMailBox, petDatabaseID ):
		"""
		摆摊出售宠物，完成宠物转移
		"""
		epitome = self.pcg_getPetEpitome( petDatabaseID )		# 取得vendor出售的宠物

		buyerBaseMailBox.vend_getPet( epitome )
#		buyer.pcg_addPet_( epitome )
#		epitome.updateAttr( "ownerDBID", buyer.databaseID, buyer, None )
#		epitome.updateAttr( "isInVend", False )
#		epitome.updateAttr( "vendSellPrice", 0 )

		self.pcg_removePet_( petDatabaseID, csdefine.DELETEPET_VEND_SELLPET )

	def vend_getPet( self, epitome ):
		"""
		摆摊出售宠物，买方获得宠物
		"""
		self.pcg_addPet_( epitome, csdefine.ADDPET_BUYFROMVEND )

		epitome.updateAttr( "isInVend", False )
		epitome.updateAttr( "vendSellPrice", 0 )

	def vend_addRecordNotify( self, buyerName, petDatabaseID, price, timeStr ):
		"""
		给客户端发送交易记录
		"""
		epitome = self.pcg_getPetEpitome( petDatabaseID )
		petName = epitome.getAttr("uname")
		self.client.vend_addRecordNotify( [ buyerName, petName, price, timeStr, 1 ] )

