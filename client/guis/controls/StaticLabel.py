# -*- coding: gb18030 -*-
#
# $Id: StaticLabel.py,v 1.4 2008-06-27 08:17:06 huangyongwei Exp $

"""
implement static label class。
"""

"""
2005/11/24 : writen by huangyongwei
2008/06/27 : renamed from TextItem to StaticLabel hy huangyongwei
"""

"""
composing :
	GUI.Window
		-- lbText ( GUI.Text )
"""

import weakref
import Font
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.GUIBaseObject import GUIBaseObject
from StaticText import StaticText

class StaticLabel( GUIBaseObject ) :
	"""
	静态文本标签（带背景，不带事件）
	"""
	def __init__( self, label = None, pyBinder = None ) :
		if label is None :
			label = hfUILoader.load( "guis/controls/staticlabel/label.gui" )
		GUIBaseObject.__init__( self, label )

		self.__pyBinder = None
		self.__autoSize = False
		self.__initialize( label, pyBinder )

	def subclass( self, label, pyBinder = None ) :
		GUIBaseObject.subclass( self, label )
		self.__pyBinder = None
		self.__initialize( label, pyBinder )
		return self

	def __del__( self ) :
		GUIBaseObject.__del__( self )
		if Debug.output_del_StaticLabel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, label, pyBinder ) :
		if label is None : return
		self.pyText_ = StaticText( label.lbText )						# the label used to set text
		if pyBinder is not None :
			self.__pyBinder = weakref.ref( pyBinder )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __hLayout( self ) :
		"""
		reset position of the label according to anchor
		"""
		if self.__autoSize :
			self.pyText_.h_anchor = "LEFT"
			self.pyText_.left = 0
			GUIBaseObject._setWidth( self, self.pyText_.width )
			return
		if self.anchor == UIAnchor.CENTER :
			self.pyText_.center = self.width * 0.5
		elif self.anchor == UIAnchor.RIGHT :
			self.pyText_.right = self.width

	def __vLayout( self, space ) :
		textHeight = self.pyText_.height
		height = textHeight + space * 2
		self.gui.height = height + 2.0		# 考虑到有可能有阴影，因此下面多留两个像素
		self.pyText_.middle = height * 0.5


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getFontInfo( self ) :
		"""
		获取字体属性：
		{ "font"	  : str: 字体名称,
		  "size"	  : int: 字体大小,
		  "bold"	  : bool: 是否为粗体,
		  "italic"	  : bool: 是否斜体,
		  "underline" : bool: 是否有下划线,
		  "strikeOut" : bool: 是否有删除线,
		  "charSpace" : float: 字间距,
		}
		"""
		return self.pyText_.getFontInfo()

	def setFontInfo( self, info ) :
		"""
		设置字体属性：
		{ "font"	  : str: 字体名称,
		  "size"	  : int: 字体大小,
		  "bold"	  : bool: 是否为粗体,
		  "italic"	  : bool: 是否斜体,
		  "underline" : bool: 是否有下划线,
		  "strikeOut" : bool: 是否有删除线,
		  "charSpace" : float: 字间距,
		}
		注：该属性字典可以只包含其中某个/某些属性
		"""
		space = self.pyText_.top
		self.pyText_.setFontInfo( info )
		self.__hLayout()
		self.__vLayout( space )

	# -------------------------------------------------
	def limnOut( self, color = ( 0, 0, 0, 255 ) ) :
		"""
		描边
		"""
		self.pyText_.limnOut( color )

	def limnShader( self, color = ( 0, 0, 0, 255 ) ) :
		"""
		描阴影
		"""
		self.pyText_.limnShader( color )

	def cancelLimning( self ) :
		"""
		取消描边或阴影效果
		"""
		self.pyText_.cancelLimning()

	# -------------------------------------------------
	def textWidth( self, text = None ) :
		"""
		获取文本宽度，如果 text 为 None，则计算自身文本的宽度
		@type				text : str
		@param				text : 要计算宽度的文本
		@rtype					 : int
		@return					 : 指定文本的宽度
		"""
		return self.pyText_.textWidth( text )

	def splitText( self, width, cutMode, text = None ) :
		"""
		根据给定宽度，拆分文本，如果 text 为 None，拆分自身文本
		@type				width : int
		@param				width : 给定的宽度
		@param				cutMode : 截取模式："CUT" / "ROUND" / "CEIL"
									  CUT	: 如果在指定宽度内不能放下最后一个字时，将最后一个字截去
									  ROUND : 如果在指定宽度内能够放下最后一个字的一半，则不截去最后一个字，否则截去最后一个字
									  CEIL	: 如果在指定宽度内能够放下最后一个字的一点点，则不截去最后一个字
		@type				text  : str
		@param				text  : 给定的文本
		@rtype					  : tupe
		@return					  : 返回拆分后的两端文本：（左边的 ASCII 字符串, 右边的 ASCII 字符串, 左边的宽字符串, 右边的宽字符串）
		"""
		return self.pyText_.splitText( width, cutMode, text )

	def elideText( self, width, cutMode, text = None ) :
		"""
		省略文本
		@type				width	: int
		@param				width	: 给定的宽度
		@type				cutMode : str
		@param				cutMode : 截取模式："CUT" / "ROUND"
									  CUT	: 如果在指定宽度内不能放下最后一个字时，将最后一个字截去
									  ROUND : 如果在指定宽度内能够放下最后一个字的一半，则不截去最后一个字，否则截去最后一个字
		@type				text	: str
		@param				text	: 给定的文本
		@rtype						: tuple
		@return						: 返回被省略后剩余的文本：（str，wstr）
		"""
		return self.pyText_.elideText( width, cutMode, text )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# -------------------------------------------------
	def _getText( self ) :
		return self.pyText_.text

	def _setText( self, text ) :
		self.pyText_.text = text
		self.__hLayout()

	def _getWText( self ) :
		return self.pyText_.wtext

	# ---------------------------------------
	def _getAnchor( self ) :
		return self.pyText_.h_anchor

	def _setAnchor( self, anchor ) :
		self.pyText_.h_anchor = anchor
		self.__hLayout()

	def _getVAnchor( self ) :
		return self.pyText_.v_anchor

	def _setVAnchor( self, anchor ) :
		pass

	# ---------------------------------------
	def _getAutoSize( self ) :
		return self.__autoSize

	def _setAutoSize( self, isAutoSize ) :
		self.__autoSize = isAutoSize
		self.__hLayout()

	# -------------------------------------------------
	def _setFont( self, font ) :
		space = self.pyText_.top
		self.pyText_.font = font
		self.__hLayout()
		self.__vLayout( space )

	def _setFontSize( self, size ) :
		space = self.pyText_.top
		self.pyText_._setFontSize( size )
		self.__hLayout()
		self.__vLayout( space )

	def _setIsBold( self, isBold ) :
		space = self.pyText_.top
		self.pyText_._setIsBold( isBold )
		self.__hLayout()
		self.__vLayout( space )

	def _setIsItalic( self, isItalic ) :
		space = self.pyText_.top
		self.pyText_._setIsItalic( isItalic )
		self.__hLayout()
		self.__vLayout( space )

	def _setIsUnderline( self, isUnderline ) :
		self.pyText_._setIsUnderline( isUnderline )

	def _setIsStrikeOut( self, isStrikeOut ) :
		self.pyText_._setIsStrikeOut( isStrikeOut )

	def _setCharSpace( self, space ) :
		self.pyText_._setCharSpace( space )
		self.__hLayout()

	def _setLimning( self, style ) :
		self.pyText_._setLimning( style )

	def _setLimnColor( self, color ) :
		self.pyText_._setLimnColor( color )

	# -------------------------------------------------
	def _getForeColor( self ) :
		return self.pyText_.color

	def _setForeColor( self, color ) :
		self.pyText_.color = color

	# ---------------------------------------
	def _getBackColor( self ) :
		return self.color

	def _setBackColor( self, color ) :
		self.color = color

	# -------------------------------------------------
	def _getLength( self ) :
		return self.pyText_.length

	def _getWLength( self ) :
		return self.pyText_.wlength

	# -------------------------------------------------
	def _setWidth( self, width ) :
		if not self.__autoSize :
			GUIBaseObject._setWidth( self, width )
		self.__hLayout()

	def _setHeight( self, height ) :
		minHeight = self.pyText_.height
		height = max( height, minHeight )
		GUIBaseObject._setHeight( self, height )
		self.pyText_.middle = self.height / 2

	# ---------------------------------------
	def _setRWidth( self, width ) :
		if not self.__autoSize :
			GUIBaseObject._setRWidth( self, width )
		self.__hLayout()

	def _setRHeight( self, height ) :
		GUIBaseObject._setRHeight( self, height )
		self.pyText_.middle = self.height / 2


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )													# 获取绑定者
	text = property( _getText, _setText )												# 获取/设置文本
	wtext = property( _getWText )														# 获取/设置宽文本
	anchor = property( _getAnchor, _setAnchor )											# 获取/设置文本水平对齐方式
	h_anchor = property( _getAnchor, _setAnchor )										# 获取/设置文本水平对齐方式( 与 StaticText 一至都有 h_anchor 属性 )
	v_anchor = property( _getAnchor, _setVAnchor )										# 获取文本垂直对齐方式
	autoSize = property( _getAutoSize, _setAutoSize )									# 获取/设置文本背景是否适应文本的大小

	font = property( lambda self : self.pyText_.font, _setFont )						# 获取/设置文本字体
	fontSize = property( lambda self : self.pyText_.fontSize, _setFontSize )			# 获取/设置字体大小
	isBold = property( lambda self : self.pyText_.isBold, _setIsBold )					# 获取/设置字体是否为粗体
	isItalic = property( lambda self : self.pyText_.isItalic, _setIsItalic )			# 获取/设置字体是为斜体
	isUnderline = property( lambda self : self.pyText_.isUnderline, _setIsUnderline )	# 获取/设置字体是否有下划线
	isStrikeOut = property( lambda self : self.pyText_.isStrikeOut, _setIsStrikeOut )	# 获取/设置字体是否有删除线
	charSpace = property( lambda self : self.pyText_.charSpace, _setCharSpace )			# 获取/设置字间距
	limning = property( lambda self : self.pyText_.limning, _setLimning )				# 获取/设置描画效果：Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( lambda self : self.pyText_.limnColor, _setLimnColor )			# 获取/设置描边颜色

	foreColor = property( lambda self : self.pyText_.color, _setForeColor )				# 获取/设置字体前景色
	backColor = property( lambda self : self.color, _setBackColor )						# 获取/设置字体背景色
	length = property( _getLength )														# 获取文本长度
	wlength = property( _getWLength )													# 获取宽文本长度

	width = property( GUIBaseObject._getWidth, _setWidth )								# 获取/设置背景宽度
	height = property( GUIBaseObject._getHeight, _setHeight )							# 获取/设置背景高度
	r_width = property( GUIBaseObject._getRWidth, _setRWidth )							# 获取/设置背景相对坐标宽度
	r_height = property( GUIBaseObject._getRHeight, _setRHeight )						# 获取/设置背景相对坐标高度
