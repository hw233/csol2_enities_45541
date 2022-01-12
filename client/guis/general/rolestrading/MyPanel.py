# -*- coding: gb18030 -*-
#
# $Id: MyPanel.py,v 1.3 2008-06-11 01:09:07 fangpengjun Exp $

"""
implement my items panel class
"""

from guis import *
from ItemsPanel import ItemsPanel
import csdefine
import GUIFacade

class MyPanel( ItemsPanel ) :
	def __init__( self, panel = None, pyBinder = None ) :
		ItemsPanel.__init__( self, panel, pyBinder )


	def subclass( self, panel, pyBinder ) :
		ItemsPanel.subclass( self, panel, pyBinder )
		return self

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getItemDescription( self, pyItem ) :
		"""
		get pyItem's description
		"""
		return GUIFacade.getSelfSwapItemDescription( pyItem.index )

	def getFirstIndex( self ):
		"""
		获取玩家间交易，交易格中的第一个索引（位置）
		"""
		for index, pyItem in self.pyItems.iteritems():
			if not pyItem.itemInfo:		# 如果位置为空
				return index
		return -1

	# -------------------------------------------------
	def onItemRClick( self, pyItem ) :
		"""
		if an item has been clicked by right mouse button, it will be invoked
		This method is invalid
		"""
		print "--------->>> my panel is right clicked!"
		GUIFacade.removeSwapItem( pyItem.index )

	def onItemDrop( self, pyTarget, pyDropped ) :
		"""
		when an item droped, it will be called
		pyTarget : the target item
		pyDropped: the item dropped
		"""
		if pyDropped.dragMark == DragMark.KITBAG_WND :
			kitBag = csdefine.KB_COMMON_ID
			GUIFacade.changeSwapItem( pyTarget.index, kitBag, pyDropped.gbIndex )
		elif pyDropped.dragMark == DragMark.ROLES_TRADING_WND :
			pass