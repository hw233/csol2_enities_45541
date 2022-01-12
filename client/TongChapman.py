# -*- coding: gb18030 -*-
#
# $Id: Chapman.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Chapman基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import GUIFacade
from Chapman import Chapman

class TongChapman( Chapman ):
	"""
	帮会领地商人NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Chapman.__init__( self )

	def onReceiveMakeItemData( self, buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs ):
		"""
		define method.
		收到传来的帮会可生产物品列表
		@param buildingLevel		:建筑的级别 商店
		@param currentMakeHouqinVal	:当前研究物品所研究的后勤度
		@param currentMakeItem		:当前正在生产的物品
		@param canMakeItemIDs		:可生产的物品列表
		"""
		GUIFacade.tong_onShowTongMakeItemWindow( self, buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs )

	def makeItems( self, makeItemID ):
		"""
		向服务器请求生产这个物品
		@param makeItemID	:物品ID
		"""
		return

	def onChangeMakeItem( self, makeItemID, makeAmount ):
		"""
		当前研发物品被改变
		@param makeItemID	:物品ID
		@param makeAmount	:要生产的数量
		"""
		GUIFacade.tong_onChangeMakeItem( makeItemID, makeAmount )

	def onReceiveGoodsAmountChange( self, uid, currAmount ):
		"""
		接受到服务器商品数量改变通知

		@param	uid:		商品ID
		@type	uid:		UINT16
		@param	currAmount:	商品剩余数量
		@param	currAmount:	UINT16
		"""
		GUIFacade.updateInvoiceAmount( uid, currAmount )

# Chapman.py
