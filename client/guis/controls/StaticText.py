# -*- coding: gb18030 -*-
#
# $Id: StaticText.py,v 1.3 2008-06-27 08:17:06 huangyongwei Exp $

"""
implement static text class

2005/11/20 : writen by huangyongwei
2008/06/27 : renamed from "Label" to "StaticText" by huangyongwei
"""
"""
composing :
	GUI.Text
"""

import weakref
import Font
import csstring
from guis import *
from guis.common.GUIBaseObject import GUIBaseObject

class StaticText( GUIBaseObject ) :
	"""
	静态文本（不带背景）
	"""
	def __init__( self, label = None, pyBinder = None ) :
		if label is None :
			label = GUI.Text( "" )					# 创建一个默认的 GUI.Text
			label.horizontalAnchor = "LEFT"			# 默认对齐方式
			label.verticalAnchor = "CENTER"
		GUIBaseObject.__init__( self, label )
		self.__pyBinder = None
		self.__limnColor = Font.defLimnColor
		self.limning = Font.defLimning
		self.__initialize( label, pyBinder )

	def subclass( self, label, pyBinder = None ) :
		GUIBaseObject.subclass( self, label )
		self.__pyBinder = None
		self.__initialize( label, pyBinder )
		return self

	def dispose( self ) :
		self.__label = None
		GUIBaseObject.dispose( self )

	def __del__( self ) :
		GUIBaseObject.__del__( self )
		if Debug.output_del_StaticText :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, label, pyBinder ) :
		self.__label = label
		self.__text = label.text
		if pyBinder is not None :
			self.__pyBinder = weakref.ref( pyBinder )

		self.__label.fontDescription( {
			"font" : Font.defFont,
			"size" : Font.defFontSize,
			"charOffset" : ( Font.defCharSpace, 0 ),
			} )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cancelLimning( self ) :
		"""
		取消描边或描阴影效果
		"""
		gui = self.gui
		limner_shader = getattr( gui, "limner", None )
		if limner_shader :
			gui.delShader( limner_shader )
		limmer_shader = getattr( gui, "limmer", None )
		if limmer_shader :
			gui.delShader( limmer_shader )
		


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getFontInfo( self ) :
		"""
		获取字体信息：
		{ "font"	  : str: 字体名称,
		  "size"	  : int: 字体大小,
		  "bold"	  : bool: 是否为粗体,
		  "italic"	  : bool: 是否斜体,
		  "underline" : bool: 是否有下划线,
		  "strikeOut" : bool: 是否有删除线,
		  "charSpace" : float: 字间距,
		}
		"""
		dsp = self.__label.fontDescription()
		if self.__label.font.endswith( ".font" ) :
			dsp["size"] = Font.getFontHeight( self.__label.font )
			dsp["bold"] = False
			dsp["italic"] = False
			dsp["underline"] = False
			dsp["strikeOut"] = False
		dsp["charSpace"] = dsp.pop( "charOffset" )[0]
		return dsp

	def setFontInfo( self, info ) :
		"""
		设置字体属性信息：
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
		if "charSpace" in info :
			info["charOffset"] = ( info.pop( "charSpace" ), 0 )
		self.__label.fontDescription( info )

	# -------------------------------------------------
	def textWidth( self, text = None ) :
		"""
		获取文本宽度，如果 text 为 None，则计算自身文本的宽度
		@type				text : str
		@param				text : 要计算宽度的文本
		@rtype					 : int
		@return					 : 指定文本的宽度
		"""
		if text == None : text = self.text
		text = csstring.toWideString( text )
		return self.getGui().stringWidth( text )

	def splitText( self, width, cutMode, text = None ) :
		"""
		根据给定宽度，拆分文本，如果 text 为 None，拆分自身文本
		@type				width	: int
		@param				width	: 给定的宽度
		@type				cutMode : str
		@param				cutMode : 截取模式："CUT" / "ROUND"
									  CUT	: 如果在指定宽度内不能放下最后一个字时，将最后一个字截去
									  ROUND : 如果在指定宽度内能够放下最后一个字的一半，则不截去最后一个字，否则截去最后一个字
		@type				text	: str
		@param				text	: 给定的文本
		@rtype						: tupe
		@return						: 返回拆分后的两端文本：（左边的 ASCII 字符串, 右边的 ASCII 字符串, 左边的宽字符串, 右边的宽字符串）
		"""
		if text == None : text = self.text
		wtext = csstring.toWideString( text )
		start = 0
		end = len( wtext )
		mid = end / 2
		while start < end :												# 使用折半查找法，找出折断位置
			spWidth = self.textWidth( wtext[:mid] )
			if start == mid :
				charWidth = self.textWidth( wtext[mid] )
				if cutMode == "CUT" :
					if width >= spWidth + charWidth :
						mid += 1
				if cutMode == "ROUND" :
					if width > spWidth + charWidth / 2 :
						mid += 1
				break
			if spWidth >  width :										# 左半部分文本大于折断宽度
				end = mid
			else :
				start = mid
			mid = ( start + end ) / 2
		lwtext = wtext[:mid]
		rwtext = wtext[mid:]
		ltext = csstring.toString( lwtext )
		rtext = csstring.toString( rwtext )
		return ltext, rtext, lwtext, rwtext

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
		ltext, rtext, lwtext, rwtext = self.splitText( width, cutMode, text )
		wtext = lwtext
		if rtext != "" :						# 文本被折断
			wtext = lwtext[:-1] + ".."
		text = csstring.toString( wtext )
		return text, wtext

	def setFloatNameFont( self ):
		"""
		设置头顶文字字体
		"""
		font = Font.floatFont
		fontSize = Font.floatFontSize
		charSpace = Font.floatCharSpace
		limning = Font.floatLimning
		limnColor = Font.floatLimnColor
		self._setFont( font )
		self._setFontSize( fontSize )
		self._setCharSpace( charSpace )
		self._setLimning( limning )
		self._setLimnColor( limnColor )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# -------------------------------------------------
	def _getText( self ) :
		return csstring.toString( self.__text )

	def _setText( self, text ) :
		self.__text = text
		try :
			if Font.isWideFont( self.font ) :							# 如果是宽字体
				self.__label.text = csstring.toWideString( text )		# 则设置文本为宽文本
			else :														# 否则
				self.__label.text = text								# 设置为 ascii 文本
		except TypeError, err :
			self.__label.text = len( text ) * "*"

	# ---------------------------------------
	def _getWideText( self ) :
		return csstring.toWideString( self.text )

	# -------------------------------------------------
	def _getFont( self ) :
		return self.__label.font

	def _setFont( self, font ) :
		self.__label.font = font
		self._setText( self.__text )

	# ---------------------------------------
	def _getFontSize( self ) :
		if self.__label.font.endswith( ".font" ) :
			return Font.getFontHeight( self.__label.font )
		return self.__label.fontDescription()["size"]

	def _setFontSize( self, size ) :
		self.__label.fontDescription( { "size" : size } )

	# ---------------------------------------
	def _getIsBold( self ) :
		if self.__label.font.endswith( ".font" ) :
			return False
		return self.__label.fontDescription()["bold"]

	def _setIsBold( self, isBold ) :
		self.__label.fontDescription( { "bold" : isBold } )

	# ---------------------------------------
	def _getIsItalic( self ) :
		if self.__label.font.endswith( ".font" ) :
			return False
		return self.__label.fontDescription()["italic"]

	def _setIsItalic( self, isItalic ) :
		self.__label.fontDescription( { "italic" : isItalic } )

	# ---------------------------------------
	def _getIsUnderline( self ) :
		if self.__label.font.endswith( ".font" ) :
			return False
		return self.__label.fontDescription()["underline"]

	def _setIsUnderline( self, isUnderline ) :
		self.__label.fontDescription( { "underline" : isUnderline } )

	# ---------------------------------------
	def _getIsStrikeOut( self ) :
		if self.__label.font.endswith( ".font" ) :
			return False
		return self.__label.fontDescription()["strikeOut"]

	def _setIsStrikeOut( self, isStrikeOut ) :
		self.__label.fontDescription( { "strikeOut" : isStrikeOut } )

	# ---------------------------------------
	def _getCharSpace( self ) :
		return self.__label.fontDescription()["charOffset"][0]

	def _setCharSpace( self, space ) :
		self.__label.fontDescription( { "charOffset" : ( space, 0 ) } )

	# ---------------------------------------
	def _getLimning( self ) :
		shader = getattr( self.gui, "limner", None )
		if shader is None :
			return Font.LIMN_NONE
		elif shader.shadow :
			return Font.LIMN_SHD
		return Font.LIMN_OUT

	def _setLimning( self, style ) :
		if isDebuged :
			assert style in ( Font.LIMN_NONE, Font.LIMN_OUT, Font.LIMN_SHD ), \
				"limning style must be: Font.LIMN_NONE or Font.LIMN_OUT or Font.LIMN_SHD"
		if style == Font.LIMN_NONE :
			self.__cancelLimning()
		else :
			shader = Font.createLimnShader( style, self.__limnColor )
			self.gui.addShader( shader, "limner" )

	def _getLimnColor( self ) :
		return self.__limnColor

	def _setLimnColor( self, color ) :
		self.__limnColor = color
		shader = getattr( self.gui, "limner", None )
		if shader is None : return
		if shader.shadow :
			shader = Font.createLimnShader( Font.LIMN_SHD, color )
		else :
			shader = Font.createLimnShader( Font.LIMN_OUT, color )
		self.gui.addShader( shader, "limner" )

	# -------------------------------------------------
	def _getHAnchor( self ) :
		return self.__label.horizontalAnchor

	def _setHAnchor( self, anchor ) :
		left = self.left
		self.__label.horizontalAnchor = anchor
		self.left = left

	# ---------------------------------------
	def _getVAnchor( self ) :
		return self.__label.verticalAnchor

	def _setVAnchor( self, anchor ) :
		top = self.top
		self.__label.verticalAnchor = anchor
		self.top = top

	# ---------------------------------------
	def _getLength( self ) :
		return len( self.text )

	def _getWLength( self ) :
		return len( self.wtext )

	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )							# 获取/设置绑定者
	text = property( _getText, _setText )						# 获取/设置文本
	wtext = property( _getWideText )							# 获取宽文本
	font = property( _getFont, _setFont )						# 获取/设置字体
	fontSize = property( _getFontSize, _setFontSize )			# 获取/设置字体大小
	isBold = property( _getIsBold, _setIsBold )					# 获取/设置字体是否为粗体
	isItalic = property( _getIsItalic, _setIsItalic )			# 获取/设置字体是为斜体
	isUnderline = property( _getIsUnderline, _setIsUnderline )	# 获取/设置字体是否有下划线
	isStrikeOut = property( _getIsStrikeOut, _setIsStrikeOut )	# 获取/设置字体是否有删除线
	charSpace = property( _getCharSpace, _setCharSpace )		# 获取/设置字间距
	limning = property( _getLimning, _setLimning )				# 获取/设置描画效果：Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( _getLimnColor, _setLimnColor )		# 获取/设置描边颜色

	h_anchor = property( _getHAnchor, _setHAnchor )				# 获取/设置水平方向上文本的对齐方式: "LEFT" / "CENTER" / "RIGHT"
	v_anchor = property( _getVAnchor, _setVAnchor )				# 获取/设置垂直方向上文本的对齐方式: "TOP" / "CENTER" / "BOTTOM"
	length = property( _getLength )								# 获取文本的字符数
	wlength = property( _getWLength )							# 获取文本的宽字符数

	width = property( GUIBaseObject._getWidth ) 				# 获取标签宽度
	height = property( GUIBaseObject._getHeight )				# 获取标签高度
