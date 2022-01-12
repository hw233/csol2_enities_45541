# -*- coding: gb18030 -*-
#
# $Id: LinkLabel.py,v 1.9 2008-08-29 02:40:40 huangyongwei Exp $

"""
implement hyperlink label class

2007/03/15: writen by huangyongwei
"""
"""
composing :
	GUI.Text
"""

import weakref
import Font
from guis import *
from guis.UIFixer import hfUILoader
from guis.controls.Label import Label

class LinkLabel( Label ) :
	def __init__( self, linkMark ) :
		label = hfUILoader.load( "guis/controls/richtext/textline.gui" )
		uiFixer.firstLoadFix( label )
		Label.__init__( self, label )
		self.isUnderline = True
		self.autoSize = True					# 背景宽度适应文本宽度

		self.__linkMark = linkMark

		self.__pyForeLabel = None
		self.__pyNextLabel = None

	def __del__( self ) :
		Label.__del__( self )
		if Debug.output_del_LinkLabel :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		Label.onMouseEnter_( self )
		rds.ccursor.set( "hand" )
		return True

	def onMouseLeave_( self ) :
		Label.onMouseLeave_( self )
		rds.ccursor.normal()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		设置标签状态
		"""
		if state == UIState.PRESSED :
			state = UIState.HIGHLIGHT
		Label.setState( self, state )
		pyLabel = pyFore = self
		while pyFore :										# 获取最前面那个
			if pyFore.pyForeLabel :
				pyLabel = pyFore.pyForeLabel
			pyFore = pyFore.pyForeLabel
		foreColor = self.foreColor
		backColor = self.backColor
		mapping = self.mapping
		while pyLabel :
			pyLabel.foreColor = foreColor
			pyLabel.backColor = backColor
			pyLabel.mapping = mapping
			pyLabel = pyLabel.pyNextLabel


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setFont( self, font ) :
		fheight = Font.getFontHeight( font )
		Label._setHeight( self, fheight + 2 )
		Label._setFont( self, font )

	# -------------------------------------------------
	def _getLinkMark( self ) :
		return self.__linkMark

	# -------------------------------------------------
	def _getForeLabel( self ) :
		if self.__pyForeLabel :
			return self.__pyForeLabel()
		return None

	def _setForeLabel( self, pyLabel ) :
		assert pyLabel != self, "do not allow link my self."				# 防止死循环
		if not pyLabel : return
		self.__pyForeLabel = weakref.ref( pyLabel )
		if pyLabel is not None :
			pyLabel._setNextLabel( self )

	# ---------------------------------------
	def _getNextLabel( self ) :
		if self.__pyNextLabel :
			return self.__pyNextLabel()
		return None

	def _setNextLabel( self, pyLabel ) :
		assert pyLabel != self, "do not allow link my self."				# 防止死循环
		if not pyLabel : return
		self.__pyNextLabel = weakref.ref( pyLabel )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	font = property( lambda self : self.pyText_._getFont, _setFont )	# 获取/设置字体
	linkMark = property( _getLinkMark )									# 获取链接标记
	pyForeLabel = property( _getForeLabel, _setForeLabel )				# 获取/设置同类型的前一个标签
	pyNextLabel = property( _getNextLabel, _setNextLabel )				# 获取/设置同类型的后一个标签
