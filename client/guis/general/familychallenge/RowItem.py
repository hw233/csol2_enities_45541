# -*- coding: gb18030 -*-

# һ��RowItem�ܰ��������(ColItem)�����һ����Ϣ�У���ӵ���Ϣ����С�
# written by ganjinxing 2009-7-6


from guis import *
from guis.controls.StaticLabel import StaticLabel
from guis.controls.ODListPanel import ViewItem
from guis.controls.Control import Control
from guis.tooluis.fulltext.FullText import FullText
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.PyGUI import PyGUI

# --------------------------------------------------------------------
# Implement the RowItem class
# RowItem is used in ODListPanel as the child of the ViewItem.
# It may include several ColItems to make up of the info row of
# the info panel item.
# --------------------------------------------------------------------
class RowItem( ViewItem ) :
	__cg_item = None
#	__highlight_bg = None

	def __init__( self, pyPanel ) :
		if RowItem.__cg_item is None :
			RowItem.__cg_item = GUI.load( "guis/general/familychallenge/fcstatus/rowinfo.gui" )
			uiFixer.firstLoadFix( RowItem.__cg_item )
		item = util.copyGuiTree( RowItem.__cg_item )
		ViewItem.__init__( self, pyPanel, item )
		self.moveFocus = True
#		if RowItem.__highlight_bg is None :
#			bgUI = GUI.load( "guis/general/familychallenge/fcstatus/sl_bg.gui" )
#			uiFixer.firstLoadFix( bgUI )
#			RowItem.__highlight_bg = PyGUI( bgUI )

		self.__pyColItems = []
		self.__highlightTexture = "guis/general/familychallenge/fcstatus/hl_bg.dds"	# ����״̬�µı���
		self.__initialize( item )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, rowUI ) :
		for name, colUI in rowUI.children :
			if not "col_" in name : continue
			pyColItem = ColItem( colUI )
			self.__pyColItems.append( pyColItem )

	def __notifyChildren( self ) :
		colItems = self.__pyColItems[:]
		for i in xrange( len( colItems ) - 1, -1, -1 ) :
			pyCItem = colItems[i]
			if pyCItem.isMouseHit() : continue
			pyCItem.onMouseLeave()									# �ȴ�������뿪��Ϣ
			colItems.remove( pyCItem )
		for pyCItem in colItems :
			pyCItem.onMouseEnter()									# �ٴ�����������Ϣ


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseMove_( self, dx, dy ) :
		self.__notifyChildren()
		return ViewItem.onMouseMove_( self, dx, dy )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onMouseLeave_( self ) :
		self.__notifyChildren()
		return ViewItem.onMouseLeave_( self )

	def refreshInfo( self, rowInfo ) :
		for pyCItem, info in zip( self.__pyColItems, rowInfo ) :
			pyCItem.update( info )
		if self.highlight :
			self.texture = self.__highlightTexture
		else :
			self.texture = ""


# --------------------------------------------------------------------
# Implement the ColItem class
# --------------------------------------------------------------------
class ColItem( StaticLabel ) :

	def __init__( self, colUI, pyBinder = None ) :
		StaticLabel.__init__( self, colUI, pyBinder )
		self.__isLastHit = False									# �Ƿ��������������Ǹ�Item
		self.text = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onMouseEnter( self ) :
		if self.__isLastHit : return
		self.__isLastHit = True
		if self.pyText_.right > self.width or self.pyText_.left < 0 :
			FullText.show( self, self.pyText_ )

	def onMouseLeave( self ) :
		if not self.__isLastHit : return
		self.__isLastHit = False
		FullText.hide()

	def update( self, info ) :
		self.text = str( info[0] )
		self.foreColor = info[1]
		if self.isMouseHit() and \
		( self.pyText_.right > self.width or self.pyText_.left < 0 ) :
			FullText.show( self, self.pyText_, False )
