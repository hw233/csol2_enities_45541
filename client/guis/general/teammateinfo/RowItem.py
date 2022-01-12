# -*- coding: gb18030 -*-

# implement the RowItem for TeamInfoPanel
# written by gjx 2009-9-16

from guis import *
from guis.general.familychallenge.RowItem import ColItem as CItem
from guis.controls.ODListPanel import ViewItem
from guis.tooluis.fulltext.FullText import FullText

# --------------------------------------------------------------------
# 行选项，由三个列组成
# --------------------------------------------------------------------
class RowItem( ViewItem ) :

	__cg_item = None

	def __init__( self, pyPanel ) :
		if RowItem.__cg_item is None :
			RowItem.__cg_item = GUI.load( "guis/general/teammateinfo/teaminfo/row.gui" )
			uiFixer.firstLoadFix( RowItem.__cg_item )
		item = util.copyGuiTree( RowItem.__cg_item )
		ViewItem.__init__( self, pyPanel, item )
		self.moveFocus = True

		self.__pyColItems = []
		self.__initialize( item )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __del__( self ) :
		if Debug.output_del_ODListPanel :
			INFO_MSG( self )

	def __initialize( self, rowGUI ) :
		for name, colGUI in rowGUI.children :
			if not "col_" in name : continue
			pyCItem = ColItem( colGUI )
			self.__pyColItems.append( pyCItem )

	def __notifyChildren( self ) :
		colItems = self.__pyColItems[:]
		for i in xrange( len( colItems ) - 1, -1, -1 ) :
			pyCItem = colItems[i]
			if pyCItem.isMouseHit() : continue
			pyCItem.onMouseLeave()								# 先处理鼠标离开消息
			colItems.remove( pyCItem )
		for pyCItem in colItems :
			pyCItem.onMouseEnter()								# 再处理鼠标进入消息


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseMove_( self, dx, dy ) :
		self.__notifyChildren()
		return ViewItem.onMouseMove_( self, dx, dy )

	def onMouseLeave_( self ) :
		self.__notifyChildren()
		return ViewItem.onMouseLeave_( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refreshInfo( self, rowInfo ) :
		for pyCItem, info in zip( self.__pyColItems, rowInfo ) :
			pyCItem.update( info )
		if self.selected :					# 高亮或选中状态
			for pyCol in self.__pyColItems :
				pyCol.foreColor = ( 60, 255, 0, 255 )
		elif self.highlight :
			for pyCol in self.__pyColItems :
				pyCol.foreColor = ( 60, 255, 255, 255 )
		else :
			for pyCol in self.__pyColItems :
				pyCol.foreColor = ( 255, 255, 255, 255 )


# --------------------------------------------------------------------
# 行中的列选项
# --------------------------------------------------------------------
class ColItem( CItem ) :

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, info ) :
		self.text = str( info )
		if self.isMouseHit() and \
		( self.pyText_.right > self.width or self.pyText_.left < 0 ) :
			FullText.show( self, self.pyText_, False )