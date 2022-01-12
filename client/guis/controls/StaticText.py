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
	��̬�ı�������������
	"""
	def __init__( self, label = None, pyBinder = None ) :
		if label is None :
			label = GUI.Text( "" )					# ����һ��Ĭ�ϵ� GUI.Text
			label.horizontalAnchor = "LEFT"			# Ĭ�϶��뷽ʽ
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
		ȡ����߻�����ӰЧ��
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
		��ȡ������Ϣ��
		{ "font"	  : str: ��������,
		  "size"	  : int: �����С,
		  "bold"	  : bool: �Ƿ�Ϊ����,
		  "italic"	  : bool: �Ƿ�б��,
		  "underline" : bool: �Ƿ����»���,
		  "strikeOut" : bool: �Ƿ���ɾ����,
		  "charSpace" : float: �ּ��,
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
		��������������Ϣ��
		{ "font"	  : str: ��������,
		  "size"	  : int: �����С,
		  "bold"	  : bool: �Ƿ�Ϊ����,
		  "italic"	  : bool: �Ƿ�б��,
		  "underline" : bool: �Ƿ����»���,
		  "strikeOut" : bool: �Ƿ���ɾ����,
		  "charSpace" : float: �ּ��,
		}
		ע���������ֵ����ֻ��������ĳ��/ĳЩ����
		"""
		if "charSpace" in info :
			info["charOffset"] = ( info.pop( "charSpace" ), 0 )
		self.__label.fontDescription( info )

	# -------------------------------------------------
	def textWidth( self, text = None ) :
		"""
		��ȡ�ı���ȣ���� text Ϊ None������������ı��Ŀ��
		@type				text : str
		@param				text : Ҫ�����ȵ��ı�
		@rtype					 : int
		@return					 : ָ���ı��Ŀ��
		"""
		if text == None : text = self.text
		text = csstring.toWideString( text )
		return self.getGui().stringWidth( text )

	def splitText( self, width, cutMode, text = None ) :
		"""
		���ݸ�����ȣ�����ı������ text Ϊ None����������ı�
		@type				width	: int
		@param				width	: �����Ŀ��
		@type				cutMode : str
		@param				cutMode : ��ȡģʽ��"CUT" / "ROUND"
									  CUT	: �����ָ������ڲ��ܷ������һ����ʱ�������һ���ֽ�ȥ
									  ROUND : �����ָ��������ܹ��������һ���ֵ�һ�룬�򲻽�ȥ���һ���֣������ȥ���һ����
		@type				text	: str
		@param				text	: �������ı�
		@rtype						: tupe
		@return						: ���ز�ֺ�������ı�������ߵ� ASCII �ַ���, �ұߵ� ASCII �ַ���, ��ߵĿ��ַ���, �ұߵĿ��ַ�����
		"""
		if text == None : text = self.text
		wtext = csstring.toWideString( text )
		start = 0
		end = len( wtext )
		mid = end / 2
		while start < end :												# ʹ���۰���ҷ����ҳ��۶�λ��
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
			if spWidth >  width :										# ��벿���ı������۶Ͽ��
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
		ʡ���ı�
		@type				width	: int
		@param				width	: �����Ŀ��
		@type				cutMode : str
		@param				cutMode : ��ȡģʽ��"CUT" / "ROUND"
									  CUT	: �����ָ������ڲ��ܷ������һ����ʱ�������һ���ֽ�ȥ
									  ROUND : �����ָ��������ܹ��������һ���ֵ�һ�룬�򲻽�ȥ���һ���֣������ȥ���һ����
		@type				text	: str
		@param				text	: �������ı�
		@rtype						: tuple
		@return						: ���ر�ʡ�Ժ�ʣ����ı�����str��wstr��
		"""
		ltext, rtext, lwtext, rwtext = self.splitText( width, cutMode, text )
		wtext = lwtext
		if rtext != "" :						# �ı����۶�
			wtext = lwtext[:-1] + ".."
		text = csstring.toString( wtext )
		return text, wtext

	def setFloatNameFont( self ):
		"""
		����ͷ����������
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
			if Font.isWideFont( self.font ) :							# ����ǿ�����
				self.__label.text = csstring.toWideString( text )		# �������ı�Ϊ���ı�
			else :														# ����
				self.__label.text = text								# ����Ϊ ascii �ı�
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
	pyBinder = property( _getBinder )							# ��ȡ/���ð���
	text = property( _getText, _setText )						# ��ȡ/�����ı�
	wtext = property( _getWideText )							# ��ȡ���ı�
	font = property( _getFont, _setFont )						# ��ȡ/��������
	fontSize = property( _getFontSize, _setFontSize )			# ��ȡ/���������С
	isBold = property( _getIsBold, _setIsBold )					# ��ȡ/���������Ƿ�Ϊ����
	isItalic = property( _getIsItalic, _setIsItalic )			# ��ȡ/����������Ϊб��
	isUnderline = property( _getIsUnderline, _setIsUnderline )	# ��ȡ/���������Ƿ����»���
	isStrikeOut = property( _getIsStrikeOut, _setIsStrikeOut )	# ��ȡ/���������Ƿ���ɾ����
	charSpace = property( _getCharSpace, _setCharSpace )		# ��ȡ/�����ּ��
	limning = property( _getLimning, _setLimning )				# ��ȡ/�����軭Ч����Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( _getLimnColor, _setLimnColor )		# ��ȡ/���������ɫ

	h_anchor = property( _getHAnchor, _setHAnchor )				# ��ȡ/����ˮƽ�������ı��Ķ��뷽ʽ: "LEFT" / "CENTER" / "RIGHT"
	v_anchor = property( _getVAnchor, _setVAnchor )				# ��ȡ/���ô�ֱ�������ı��Ķ��뷽ʽ: "TOP" / "CENTER" / "BOTTOM"
	length = property( _getLength )								# ��ȡ�ı����ַ���
	wlength = property( _getWLength )							# ��ȡ�ı��Ŀ��ַ���

	width = property( GUIBaseObject._getWidth ) 				# ��ȡ��ǩ���
	height = property( GUIBaseObject._getHeight )				# ��ȡ��ǩ�߶�
