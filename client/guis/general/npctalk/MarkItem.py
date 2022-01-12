# -*- coding: gb18030 -*-
# $Id: MarkItem.py,v 1.4 2008-06-27 03:17:50 huangyongwei Exp $
#
"""
implement pet epitome type
2007/07/01: writen by huangyongwei
"""

from guis import *
from guis.common.PyGUI import PyGUI
from RespondItem import RespondItem

class MarkItem( RespondItem ) :
	__cg_item = None

	def __init__( self ) :
		if MarkItem.__cg_item is None :
			MarkItem.__cg_item = GUI.load( "guis/general/npctalk/markitem.gui" )

		item = util.copyGuiTree( MarkItem.__cg_item )
		uiFixer.firstLoadFix( item )
		RespondItem.__init__( self, item )
		self.__initialize( item )

	def __initialize( self, item ) :
		self.__pyMark = PyGUI( item.outMark )
		self.__pyMark.visible = True
		self.__pyMark.mark = 0
		self.pyRichText_.maxWidth = self.width - self.__pyMark.width - 3.0
		self.pyRichText_.left = self.__pyMark.right + 4.0  # 隔开mark与text
		self.__markType = -1


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	#def onStateChanged_( self, state ) :
	#	self.__pyLbID.color = self.foreColor


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------

	def _setMark( self, mark ):
		self.__pyMark.mark = mark

		util.setGuiState( self.__pyMark.getGui(), (1,32), mark )

	def _getMark( self ):
		return self.__pyMark.mark


	def _setMarkType( self, markType ):
		self.__markType = markType

	def _getMarkType( self ):
		return self.__markType

	def _setText( self, text ) :
		RespondItem._setText( self, text )
		self.__pyMark.top = 3.0

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	mark = property( _getMark, _setMark )
	markType = property( _getMarkType, _setMarkType )
	text = property( lambda self : RespondItem._getText( self ), _setText )
