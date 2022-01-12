# -*- coding: gb18030 -*-
# ��̯

import BigWorld
import time

from bwdebug import *

import csdefine
import csconst
import csstatus
import random

class RoleVend:
	"""
	��Ұ�̯ϵͳ
	"""
	def __init__( self ):
		"""
		"""
		pass

	def vend_petForSale( self, databaseID, price ):
		"""
		�����̯����
		"""
		epitome = self.pcg_getPetEpitome( databaseID )

		# ��ǳ���Ϊ��̯������
		epitome.updateAttr( "isInVend", True )
		epitome.updateAttr( "vendSellPrice", price )

	def vend_petEndForSale( self, databaseID ):
		"""
		�����¼ܣ�ֹͣ�������
		"""
		epitome = self.pcg_getPetEpitome( databaseID )
		# ���������۱��
		epitome.updateAttr( "isInVend", False )
		epitome.updateAttr( "vendSellPrice", 0 )

	def vend_buyerQueryPetInfo( self, buyerBaseMailBox, vendPetMerchandise ):
		"""
		�����·������ĳ�����Ϣ
		"""
		epitomes = []
		for e in vendPetMerchandise:
			epitome = self.pcg_getPetEpitome( e["databaseID"] )
			epitomes.append( epitome )

		buyerBaseMailBox.client.vend_receivePetData( epitomes )

	def vend_sellPet( self, buyerBaseMailBox, petDatabaseID ):
		"""
		��̯���۳����ɳ���ת��
		"""
		epitome = self.pcg_getPetEpitome( petDatabaseID )		# ȡ��vendor���۵ĳ���

		buyerBaseMailBox.vend_getPet( epitome )
#		buyer.pcg_addPet_( epitome )
#		epitome.updateAttr( "ownerDBID", buyer.databaseID, buyer, None )
#		epitome.updateAttr( "isInVend", False )
#		epitome.updateAttr( "vendSellPrice", 0 )

		self.pcg_removePet_( petDatabaseID, csdefine.DELETEPET_VEND_SELLPET )

	def vend_getPet( self, epitome ):
		"""
		��̯���۳���򷽻�ó���
		"""
		self.pcg_addPet_( epitome, csdefine.ADDPET_BUYFROMVEND )

		epitome.updateAttr( "isInVend", False )
		epitome.updateAttr( "vendSellPrice", 0 )

	def vend_addRecordNotify( self, buyerName, petDatabaseID, price, timeStr ):
		"""
		���ͻ��˷��ͽ��׼�¼
		"""
		epitome = self.pcg_getPetEpitome( petDatabaseID )
		petName = epitome.getAttr("uname")
		self.client.vend_addRecordNotify( [ buyerName, petName, price, timeStr, 1 ] )

