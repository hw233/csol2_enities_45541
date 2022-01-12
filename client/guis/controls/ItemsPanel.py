# -*- coding: gb18030 -*-
#
# $Id: ItemsPanel.py,v 1.16 2008-08-26 02:12:45 huangyongwei Exp $

"""
implement itemspanel calss

2006.04.28: writen by huangyongwei
"""

"""
composing :
	WindowsGUIComponent
	scroll bar
"""

from guis import *
from ScrollPanel import VScrollPanel

class ItemsPanel( VScrollPanel ) :
	def __init__( self, panel = None, scrollBar = None, pyBinder = None ) :
		VScrollPanel.__init__( self, panel, scrollBar, pyBinder )
		self.gradualScroll = False

		self.pyItems_ = []
		self.__viewCols = 1
		self.__colSpace = 0.0					# 列距
		self.__rowSpace = 0.0					# 行距
		self.__itemPerScroll = True

	def __del__( self ) :
		self.clearItems()
		VScrollPanel.__del__( self )
		if Debug.output_del_ItemsPanel :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setScrollProperty( self ) :
		if self.itemCount == 0 :
			self.wholeLen = 0
		else :
			self.wholeLen = self.pyItems_[-1].bottom


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def layoutItems_( self, startIndex = 0 ) :
		itemCount = self.itemCount
		if itemCount == 0 : return
		if startIndex >= itemCount : return
		pyItem = self.pyItems_[startIndex]
		if self.__viewCols == 1 :											# 单列( 分开单列和多列排列的目的是，单列支持每行的高度都不一样 )
			pyItem.left = 0
			if startIndex == 0 :
				pyItem.top = 0
			else :
				pyItem.top = self.pyItems_[startIndex - 1].bottom
			for pyNextItem in self.pyItems_[( startIndex + 1 ):] :
				pyNextItem.left = 0
				pyNextItem.top = pyItem.bottom
				pyItem = pyNextItem
		else :																# 多列
			itemWidth = pyItem.width + self.__colSpace
			itemHeight = pyItem.height + self.__rowSpace
			for index in xrange( startIndex, itemCount ) :
				pyItem = self.pyItems_[index]
				pyItem.left = itemWidth * ( index % self.__viewCols ) - 0.2
				pyItem.top = itemHeight * ( index / self.__viewCols ) - 0.2
		self.__setScrollProperty()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addItem( self, pyItem, index=-1) :
		"""
		add an python item
		@type			pyItem : instance of python gui
		@param			pyItem : the item you want to remove
		@return				   : None
		"""
		if pyItem in self.pyItems_ :
			DEBUG_MSG( "the item %s had been added!" % pyItem )
			return
		self.addPyChild( pyItem )
		if index != -1:
			self.pyItems_.insert( index, pyItem )
		else:
			self.pyItems_.append( pyItem )		
		if self.__itemPerScroll :
			self.perScroll = pyItem.height + self.__rowSpace
		if index == -1:
			index=self.itemCount - 1
		self.layoutItems_( index )

	def addItems( self, pyItems ) :
		"""
		add a list of python items
		@type			pyItems : a list of python items
		@param			pyItems : the items you want to remove
		@return					: None
		"""
		if not len( pyItems ) : return
		if self.__itemPerScroll :
			self.perScroll = pyItems[0].height + self.__rowSpace
		for pyItem in pyItems :
			if pyItem in self.pyItems_ :
				DEBUG_MSG( "the item %s had been added!" % pyItem )
				continue
			index = self.itemCount
			self.addPyChild( pyItem )
			pyItem.left = ( pyItem.width + self.__colSpace ) * ( index % self.__viewCols )
			if self.__viewCols > 1 :
				pyItem.top = ( pyItem.height + self.__rowSpace ) * ( index / self.__viewCols )
			elif index == 0 :
				pyItem.top = 0
			else :
				pyItem.top = self.pyItems_[index - 1].bottom
			self.pyItems_.append( pyItem )
		self.__setScrollProperty()

	def removeItem( self, pyItem ) :
		"""
		remove a python item
		@type			pyItem : instance of python item
		@param			pyItem : the item you want to remove
		@return				   : None
		"""
		if pyItem not in self.pyItems_ :
			DEBUG_MSG( "the item %s is not in the items panel!" % pyItem )
			return
		self.delPyChild( pyItem )
		index = self.pyItems_.index( pyItem )
		self.pyItems_.remove( pyItem )
		self.layoutItems_( index )

	def clearItems( self ) :
		"""
		clear all python items
		"""
		for pyItem in self.pyItems_ :
			self.delPyChild( pyItem )
		self.pyItems_ = []
		self.layoutItems_()
		self.resume()

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		获取指定索引的选项
		"""
		return self.pyItems_[index]

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		resort items
		"""
		self.pyItems_.sort( cmp, key, reverse )
		self.layoutItems_( 0 )
		
	def sort2( self, cmp = None, key = None, reverse = False, filter = None ) :
		"""
		resort items
		"""
		newItemsList = filter( self. pyItems_ )
		newItems = []
		for itemList in newItemsList:
			itemList.sort( cmp, key, reverse )
			newItems.extend( itemList )
		self.pyItems_ = newItems
		self.layoutItems_( 0 )

	# -------------------------------------------------
	def getItemAt( self, x, y ) :
		for pyItem in self.pyItems_ :
			if pyItem.hitTest( x, y ) :
				return pyItem
		return None

	def getHitItem( self ) :
		x, y = csol.pcursorPosition()
		return self.getItemAt( x, y )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItems( self ) :
		return self.pyItems_[:]

	def _getItemCount( self ) :
		return len( self.pyItems_ )

	# -------------------------------------------------
	def _getColSpace( self ) :
		return self.__colSpace

	def _setColSpace( self, space ) :
		self.__colSpace = space

	# -------------------------------------------------
	def _getViewCols( self ) :
		return self.__viewCols

	def _setViewCols( self, count ) :
		self.__viewCols = count

	# ---------------------------------------
	def _getRowSpace( self ) :
		return self.__rowSpace

	def _setRowSpace( self, space ) :
		self.__rowSpace = space

	# ---------------------------------------
	def _getItemPerScroll( self ) :
		return self.__itemPerScroll

	def _setItemPerScroll( self, isItemHeight ) :
		self.__itemPerScroll = isItemHeight

	# -------------------------------------------------
	def _setHeight( self, height ) :
		VScrollPanel._setHeight( self, height )
		self.__setScrollProperty()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyItems = property( _getItems )									# get all python items
	itemCount = property( _getItemCount )							# get the number of items
	viewCols = property( _getViewCols, _setViewCols )				# get or set column count
	rowSpace = property( _getRowSpace, _setRowSpace )				# get or set space between two items on verital
	colSpace = property( _getColSpace, _setColSpace )				# get or set space between two items on horizontal
	itemPerScroll = property( _getItemPerScroll, _setItemPerScroll )# get or set whether perscroll is equal to the item's height
	height = property( VScrollPanel._getHeight, _setHeight )		# get or set the height of panel
