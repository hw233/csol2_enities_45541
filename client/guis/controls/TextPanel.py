# -*- coding: gb18030 -*-
#
# $Id: TextPanel.py,v 1.12 2008-08-09 09:43:49 huangyongwei Exp $

"""
implement static text panel class。

2005.06.19: writen by huangyongwei
"""
"""
composing :
	GUI.Window
	scrollBar ( gui of csui.controls.ScrollBar.ScrollBar )
"""

from guis import *
from ScrollPanel import VScrollPanel
from RichText import RichText

class TextPanel( VScrollPanel ) :
	def __init__( self, panel = None, scrollBar = None, pyBinder = None ) :
		VScrollPanel.__init__( self, panel, scrollBar, pyBinder )
		self.__initialize( panel )
		self.perScroll = 60.0

	def subclass( self, panel, scrollBar, pyBinder = None ) :
		VScrollPanel.subclass( self, panel, pyBinder )
		self.__initialize( panel )
		return self

	def __del__( self ) :
		VScrollPanel.__del__( self )
		if Debug.output_del_TextPanel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, panel ) :
		if panel is None : return
		self.pyRichText_ = self.createRichText_()				# 使用 RichText 作为 TextPanel 的文本解释方式（并使用 RichText 的默认插件）
		self.addPyChild( self.pyRichText_ )
		self.pyRichText_.pos = ( 0, 0 )
		self.pyRichText_.maxWidth = self.width


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	@property
	def onComponentLClick( self ) :
		"""
		当文本上的某个超链接标签被左键点击时触发
		"""
		return self.pyRichText_.onComponentLClick

	@property
	def onComponentRClick( self ) :
		"""
		当文本上的某个超链接标签被右键点击时触发
		"""
		return self.pyRichText_.onComponentRClick

	@property
	def onComponentMouseEnter( self ) :
		"""
		当鼠标进入文本上的某个超链接标签时被触发
		"""
		return self.pyRichText_.onComponentMouseEnter

	@property
	def onComponentMouseLeave( self ) :
		"""
		当鼠标离开文本上的某个超链接标签时被触发
		"""
		return self.pyRichText_.onComponentMouseLeave


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __resetScrollProperties( self ) :
		"""
		重新设置滚动属性
		"""
		self.wholeLen = self.pyRichText_.bottom
		self.scroll = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def createRichText_( self ) :
		return RichText()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyRichText_.text

	def _setText( self, text ) :
		self.pyRichText_.text = text
		self.__resetScrollProperties()

	# -------------------------------------------------
	def _getFont( self ) :
		return self.pyRichText_.font

	def _setFont( self, font ) :
		self.pyRichText_.font = font
		self.__resetScrollProperties()

	def _getFontSize( self ) :
		return self.pyRichText_._getFontSize()

	def _setFontSize( self, size ) :
		self.pyRichText_._setFontSize( size )
		self.__resetScrollProperties()

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.pyRichText_.foreColor

	def _setForeColor( self, color ) :
		self.pyRichText_.foreColor = color

	# -------------------------------------------------
	def _getCharSpace( self ) :
		return self.pyRichText_.charSpace

	def _setCharSpace( self, space ) :
		self.pyRichText_._setCharSpace( space )
		self.__resetScrollProperties()

	def _getSpacing( self ) :
		return self.pyRichText_.spacing

	def _setSpacing( self, spacing ) :
		self.pyRichText_.spacing = spacing
		self.__resetScrollProperties()

	# -------------------------------------------------
	def _getLimning( self ) :
		return self.pyRichText_._getLimning()

	def _setLimning( self, limning ) :
		self.pyRichText_._setLimning()

	def _getLimnColor( self ) :
		self.pyRichText_._getLimnColor()

	def _setLimnColor( self, color ) :
		self.pyRichText_._setLimnColor( color )

	# -------------------------------------------------
	def _getLineCount( self ) :
		return self.pyRichText_.lineCount


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )						# 获取/设置文本
	font = property( _getFont, _setFont )						# 获取/设置字体
	fontSize = property( _getFontSize, _setFontSize )			# 获取/设置字体大小
	foreColor = property( _getForeColor, _setForeColor )		# 获取/设置前景色
	charSpace = property( _getCharSpace, _setCharSpace )		# 获取/设置字间距
	spacing = property( _getSpacing, _setSpacing )				# 获取/设置行间距
	limning = property( _getLimning, _setLimning )				# MACRO DEFINATION: 获取/设置描边效果：Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( _getLimnColor, _setLimnColor )		# tuple: 获取/设置描边颜色

	lineCount = property( _getLineCount )						# 获取当前文本的行数
