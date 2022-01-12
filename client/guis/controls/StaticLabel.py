# -*- coding: gb18030 -*-
#
# $Id: StaticLabel.py,v 1.4 2008-06-27 08:17:06 huangyongwei Exp $

"""
implement static label class��
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
	��̬�ı���ǩ���������������¼���
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
		self.gui.height = height + 2.0		# ���ǵ��п�������Ӱ��������������������
		self.pyText_.middle = height * 0.5


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getFontInfo( self ) :
		"""
		��ȡ�������ԣ�
		{ "font"	  : str: ��������,
		  "size"	  : int: �����С,
		  "bold"	  : bool: �Ƿ�Ϊ����,
		  "italic"	  : bool: �Ƿ�б��,
		  "underline" : bool: �Ƿ����»���,
		  "strikeOut" : bool: �Ƿ���ɾ����,
		  "charSpace" : float: �ּ��,
		}
		"""
		return self.pyText_.getFontInfo()

	def setFontInfo( self, info ) :
		"""
		�����������ԣ�
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
		space = self.pyText_.top
		self.pyText_.setFontInfo( info )
		self.__hLayout()
		self.__vLayout( space )

	# -------------------------------------------------
	def limnOut( self, color = ( 0, 0, 0, 255 ) ) :
		"""
		���
		"""
		self.pyText_.limnOut( color )

	def limnShader( self, color = ( 0, 0, 0, 255 ) ) :
		"""
		����Ӱ
		"""
		self.pyText_.limnShader( color )

	def cancelLimning( self ) :
		"""
		ȡ����߻���ӰЧ��
		"""
		self.pyText_.cancelLimning()

	# -------------------------------------------------
	def textWidth( self, text = None ) :
		"""
		��ȡ�ı���ȣ���� text Ϊ None������������ı��Ŀ��
		@type				text : str
		@param				text : Ҫ�����ȵ��ı�
		@rtype					 : int
		@return					 : ָ���ı��Ŀ��
		"""
		return self.pyText_.textWidth( text )

	def splitText( self, width, cutMode, text = None ) :
		"""
		���ݸ�����ȣ�����ı������ text Ϊ None����������ı�
		@type				width : int
		@param				width : �����Ŀ��
		@param				cutMode : ��ȡģʽ��"CUT" / "ROUND" / "CEIL"
									  CUT	: �����ָ������ڲ��ܷ������һ����ʱ�������һ���ֽ�ȥ
									  ROUND : �����ָ��������ܹ��������һ���ֵ�һ�룬�򲻽�ȥ���һ���֣������ȥ���һ����
									  CEIL	: �����ָ��������ܹ��������һ���ֵ�һ��㣬�򲻽�ȥ���һ����
		@type				text  : str
		@param				text  : �������ı�
		@rtype					  : tupe
		@return					  : ���ز�ֺ�������ı�������ߵ� ASCII �ַ���, �ұߵ� ASCII �ַ���, ��ߵĿ��ַ���, �ұߵĿ��ַ�����
		"""
		return self.pyText_.splitText( width, cutMode, text )

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
	pyBinder = property( _getBinder )													# ��ȡ����
	text = property( _getText, _setText )												# ��ȡ/�����ı�
	wtext = property( _getWText )														# ��ȡ/���ÿ��ı�
	anchor = property( _getAnchor, _setAnchor )											# ��ȡ/�����ı�ˮƽ���뷽ʽ
	h_anchor = property( _getAnchor, _setAnchor )										# ��ȡ/�����ı�ˮƽ���뷽ʽ( �� StaticText һ������ h_anchor ���� )
	v_anchor = property( _getAnchor, _setVAnchor )										# ��ȡ�ı���ֱ���뷽ʽ
	autoSize = property( _getAutoSize, _setAutoSize )									# ��ȡ/�����ı������Ƿ���Ӧ�ı��Ĵ�С

	font = property( lambda self : self.pyText_.font, _setFont )						# ��ȡ/�����ı�����
	fontSize = property( lambda self : self.pyText_.fontSize, _setFontSize )			# ��ȡ/���������С
	isBold = property( lambda self : self.pyText_.isBold, _setIsBold )					# ��ȡ/���������Ƿ�Ϊ����
	isItalic = property( lambda self : self.pyText_.isItalic, _setIsItalic )			# ��ȡ/����������Ϊб��
	isUnderline = property( lambda self : self.pyText_.isUnderline, _setIsUnderline )	# ��ȡ/���������Ƿ����»���
	isStrikeOut = property( lambda self : self.pyText_.isStrikeOut, _setIsStrikeOut )	# ��ȡ/���������Ƿ���ɾ����
	charSpace = property( lambda self : self.pyText_.charSpace, _setCharSpace )			# ��ȡ/�����ּ��
	limning = property( lambda self : self.pyText_.limning, _setLimning )				# ��ȡ/�����軭Ч����Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( lambda self : self.pyText_.limnColor, _setLimnColor )			# ��ȡ/���������ɫ

	foreColor = property( lambda self : self.pyText_.color, _setForeColor )				# ��ȡ/��������ǰ��ɫ
	backColor = property( lambda self : self.color, _setBackColor )						# ��ȡ/�������屳��ɫ
	length = property( _getLength )														# ��ȡ�ı�����
	wlength = property( _getWLength )													# ��ȡ���ı�����

	width = property( GUIBaseObject._getWidth, _setWidth )								# ��ȡ/���ñ������
	height = property( GUIBaseObject._getHeight, _setHeight )							# ��ȡ/���ñ����߶�
	r_width = property( GUIBaseObject._getRWidth, _setRWidth )							# ��ȡ/���ñ������������
	r_height = property( GUIBaseObject._getRHeight, _setRHeight )						# ��ȡ/���ñ����������߶�
