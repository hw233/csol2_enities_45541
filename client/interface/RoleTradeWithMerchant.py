# -*- coding: gb18030 -*-
#


"""
"""

import BigWorld
import GUIFacade
import csdefine
import event.EventCenter as ECenter
from bwdebug import *

YINPIAO = 50101024													#��Ʊ

class RoleTradeWithMerchant:
	"""
	"""

	def __init__( self ) :
		self.__targetID = 0

	def leaveTradeWithMerchant( self ):
		"""
		Define Method
		"""
		self.__targetID = 0
		GUIFacade.onTradeWithNPCOver()

	def enterTradeWithMerchant( self, objectID ):
		"""
		Define Method
		"""
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return

		if self.__targetID == objectID : return
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )
		self.__targetID = objectID
		entity.cell.sendInvoiceListToClient()

		GUIFacade.onTradeWithMerchant( entity )
		"""

	def delRedeemItemUpdate( self, uid ):
		"""
		Define method.
		"""
		GUIFacade.onDelRedeemItem( uid )


	def addRedeemItemUpdate( self, item ):
		"""
		Define method.
		"""
		GUIFacade.onAddRedeemItem( item )

	def getTradeMerchantID( self ) :
		"""
		"""
		return self.__targetID

	def getAllYinpiaoValue( self ):
		"""
		��ȡ����������Ʊ����ֵ

		itemList = self.findItemsByIDFromNKCK( YINPIAO )			#��ƱID
		yinpiao = 0
		for i in itemList:
			yinpiao += i.yinpiao()
		return yinpiao
		"""
		pass