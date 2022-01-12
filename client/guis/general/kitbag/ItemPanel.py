# -*- coding: gb18030 -*-
#
# $Id: ItemPanel.py,v 1.9 2008-09-01 06:35:19 pengju Exp $

"""
implement ItemsPanel
"""
import GUI
from guis import *
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from ObjectItem import ObjectItem
import csdefine

class BagWindow( HVFlexExWindow ):
	itemwnd = ResMgr.openSection("guis/general/kitbag/subkitbag.gui")

	def __init__( self, kitbagID, maxSpace, kitbag=None, pyBinder = None ):
		kitbag=GUI.load(BagWindow.itemwnd)
		uiFixer.firstLoadFix( kitbag )
		HVFlexExWindow.__init__( self, kitbag )
		self.activable_ = True
		self.escHide_ = True
		self.posZSegment = ZSegs.L4
		self.addToMgr( "bagWindow" )
		self.__pyItemsPanel = ItemPanel( kitbagID , maxSpace, kitbag.itemsPanel )
		self.pyBinder = pyBinder
		self.kitbagID = kitbagID

	def dispose( self ) :
		self.__pyItemsPanel.dispose()
		HVFlexExWindow.dispose( self )

	def getItem( self, index ) :
		return self.__pyItemsPanel.getItem( index )

	def getItems( self ):
		return self.__pyItemsPanel.getItems()

	def delItems( self ):
		"""
		������Ʒͼ��Ϊ��wsf
		"""
		self.__pyItemsPanel.delItems()

	def getEmptyItem( self ):
		return self.__pyItemsPanel.getEmptyItem()

	def show( self, pyOwner = None ):
#		self.right = pyOwner.left
		HVFlexExWindow.show( self, pyOwner )

	def hide( self ):
		self.pyBinder.onKitBagHide( self.kitbagID )
		HVFlexExWindow.hide( self )

class ItemPanel( PyGUI ):

	def __init__( self, kitbagID = 0, maxSpace = 0, panel = None ):
		PyGUI.__init__( self, panel )
		self.__kitBagID = kitbagID
		self.__maxSpace = maxSpace
		self.itemsPanelItems = {}
		self.__initPanel( panel, maxSpace )

	def __initPanel( self, itemsPanel, maxSpace ):
		if self.__kitBagID != csdefine.KB_COMMON_ID: #���ر�����Ϣ������ж���Ҫ��������������Ʒ��������
			self.__pyItems = {}
			cols = csdefine.KB_MAX_COLUMN #���ñ���������
			rows = maxSpace / cols
			for index in xrange( 0, maxSpace ): #������Ʒ������
				item = GUI.load( "guis/general/kitbag/item.gui" )
				uiFixer.firstLoadFix( item )
				pyItem = PyGUI( item )
				self.addPyChild( pyItem, "item_%d"%index )
				pyItem.left = ( pyItem.width ) * ( index % cols )
				pyItem.top = ( pyItem.height ) * ( index / cols )
				self.itemsPanelItems[index] = pyItem
			pyRightItem = self.itemsPanelItems[cols - 1] #���������ұ߸���
			pyBottomItem = self.itemsPanelItems[maxSpace - 1] #���������±߸���
			self.width = pyRightItem.right#���ñ���panel�Ŀ�
			self.height = pyBottomItem.bottom #���ñ���panel�ĳ�
			self.pyTopParent.height = self.bottom + 25.0
			self.center = self.pyTopParent.width/2.0
			startIndex = len( self.__pyItems )
			for name, item in itemsPanel.children: #����Ʒ���������Ʒ����Ƥ
				if "item_" not in name : continue  #��Ҫ��ɸѡ���ã���ֹitemsPanel��������������
				index = int( name.split( "_" )[1] )
				if index in xrange( maxSpace ):
					gbIndex = startIndex + index
					pyItem = ObjectItem( self.__kitBagID, item, index, gbIndex )
					pyItem.focus = True
					self.__pyItems[gbIndex] = pyItem
		else: #������Ʒ����Ϣ
			self.__pyItems = {}
			startIndex = len( self.__pyItems )
			for name, item in itemsPanel.children:
				if "item_" not in name : continue
				index = int( name.split( "_" )[1] )
				if index in xrange( maxSpace ):
					gbIndex = startIndex + index
					pyItem = ObjectItem( self.__kitBagID, item, index, gbIndex )
					pyItem.focus = True
					self.__pyItems[gbIndex] = pyItem

	def __onDrop( self ):
		pass

	def getItem( self, index ) :
		if index < 0 : return None
		if index >= len( self.__pyItems ) : return None
		return self.__pyItems[index]

	def getItems( self ):
		return self.__pyItems

	def delItems( self ):
		"""
		������Ʒͼ��Ϊ��wsf
		"""
		for item in self.__pyItems.itervalues():
			item.update( None )

	def getEmptyItem( self ):
		for i in self.__pyItems:
			if self.__pyItems[i].itemInfo == None:
				return i
		return -1

	def dispose( self ):
		for i in self.__pyItems.itervalues():
			i.dispose()
		self.__pyItems = {}
		PyGUI.dispose( self )

