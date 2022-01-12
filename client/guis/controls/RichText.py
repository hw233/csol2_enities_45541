# -*- coding: gb18030 -*-
#
# $Id: RichText.py,v 1.58 2008-08-29 02:39:07 huangyongwei Exp $

"""
implement label array class��

2007/03/15: writen by huangyongwei
2008/05/14: modified to plugins mode
"""

"""
composing :
	GUI.Window
"""

import re
import inspect
import weakref
import SmartImport
import Font
import csstring
import event.EventCenter as ECenter
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.GUIBaseObject import GUIBaseObject
from Control import Control
from guis.controls.StaticLabel import StaticLabel
from csstring import g_interpunctions

# --------------------------------------------------------------------
# implement RichText control class
# --------------------------------------------------------------------
class _TempInner( object ) :
	"""
	����˳��ճ���ı�ʱ������һЩ��ʱ����
	"""
	__slots__ = ( "top", "width", "height", "space", "align", "lineFlat", "elems" )

	def __init__( self ) :
		self.top = 0					# ��ǰ���ı��Ķ�������
		self.width = 0					# ��ǰ���ı��Ŀ��
		self.height = 0					# ��ǰ���ı��ĸ߶�
		self.space = 0					# ��ǰ���ı���ʣ����
		self.align = "L"				# ��ǰ���ı���ˮƽͣ����ʽ
		self.lineFlat = "B"				# ��ǰ���ı��Ĵ�ֱ���뷽ʽ
		self.elems = []					# ��ǰ���ı������� python Ԫ��

class TmpOuter( object ) :
	__slots__ = ( "font", "fontSize", "charSpace", "fcolor", "bcolor",
				  "bold", "italic", "underline", "strikeOut",
				  "limning", "limnColor" )
	def __init__( self, pyRich ) :
		self.font = pyRich.font
		self.fontSize = pyRich.fontSize
		self.charSpace = pyRich.charSpace
		self.fcolor = pyRich.foreColor
		self.bcolor = pyRich.backColor
		self.bold = False
		self.italic = False
		self.underline = False
		self.strikeOut = False
		self.limning = pyRich.limning
		self.limnColor = pyRich.limnColor


# --------------------------------------------------------------------
# implement RichText control class
# --------------------------------------------------------------------
class RichText( Control ) :
	"""
	��̬�ḻ�ı��ؼ�
	"""
	__cg_plugins = {}

	def __init__( self, panel = None, pyBinder = None ) :
		if panel :
			if isDebuged :
				assert type( panel ) is GUI.Window, "panel of richtext must be a GUI.Window!"
		else :
			panel = hfUILoader.load( "guis/controls/richtext/board.gui" )
		Control.__init__( self, panel, pyBinder )
		self.__pluginMgr = PluginMgr()							# ���������

		self.__text = ""										# ��¼Դ�ı�
		self.__align = 'L'										# Ĭ�϶��뷽ʽΪ����( ��ѡ���뷽ʽ��L, C, R )
		self.__lineFlat = "B"									# ���ǰ�������ı��߶Ȳ�һ��ʱ������ʲô���Ķ��뷽ʽ��T��M��B��
		self.__font = Font.defFont								# Ĭ������
		self.__fontSize = Font.defFontSize						# Ĭ�������С
		self.__fcolor = ( 255, 255, 255, 255 )					# Ĭ��������ɫ
		self.__bcolor = ( 255, 255, 255, 0 )					# Ĭ�ϱ���ɫ
		self.__charSpace = Font.defCharSpace					# Ĭ���ּ��
		self.__spacing = Font.defSpacing						# �м��
		self.__limning = Font.defLimning						# �����ʽ
		self.__limnColor = Font.defLimnColor					# �����ɫ

		self.__fontWidth = Font.getFontWidth( self.font )		# ������
		self.__maxWidth = max( self.width, self.__fontWidth )	# ���������ȣ��ı���ȳ����ÿ�Ƚ����Զ����У�
		Control._setHeight( self, 0.0 )							# Ĭ�ϸ߶�Ϊ�м��
		self.__autoNewline = True								# �Ƿ��Զ�����
		self.__widthAdapt = False								# �Ƿ�����Ӧ��ȣ�����еĿ����Ϊ����ȣ�

		self.lineInfos_ = []									# ����������ı���Ϣ����Ԫ��Ϊ��( ���ַ������� python Ԫ���б� )

		self.__tmpInner = _TempInner()							# ��¼��ǰ�е�����( ��粻������ )
		self.__tmpInner.top = self.__spacing					# ��ǰ�еĶ���
		self.__tmpInner.width = 0								# ��ǰ������Ԫ�صĿ��
		self.__tmpInner.height = 0								# ��ǰ�и߶ȣ������߶ȵ��ı���ǩ��Ϊ���еĸ߶ȣ�
		self.__tmpInner.space = self.maxWidth					# ��ǰ�е�ʣ����
		self.__tmpInner.align = self.__align					# ��ǰ�ı����뷽ʽ
		self.__tmpInner.lineFlat = self.__lineFlat				# ��ǰ�ı����뷽ʽ
		self.__tmpInner.elems = []								# ��ǰ�а���������Ԫ��

		self.__tmpWidthAdapt = self.__widthAdapt				# �жϵ�ǰ�Ƿ񻹴��� widthAdapt ״̬
		self.__tmpCurrWidth = 0.0								# ��ǰ����ճ�����ı�������ı��Ŀ��
		self.__tmpCRElems = {}									# ��� __widthAdapt Ϊ True�������ڱ��浱ǰ�м������Ҷ�����ı�: { ������ : ( ���뷽ʽ, �п�� ) }

		#self.tmpOuter__ = TmpOuter( self )						# ��¼��ǰ�е����ԣ�������޸ģ����������Ӽ���( ֻ�ڸ��ı��Ĺ�����ʹ�ã������ɾ����������ע�ͷ�ʽд������ֻ�Ǳ������ôһ������ )
		self.__tmpsForPL = {}									# ��������ʱ���������ڲ��֮�䴫��ֵ��

	def dispose( self ) :
		self.clear()
		Control.dispose( self )

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_RichText :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onTextChanged = self.createEvent_( "onTextChanged" )
		self.__onComponentLClick = self.createEvent_( "onComponentLClick" )
		self.__onComponentRClick = self.createEvent_( "onComponentRClick" )
		self.__onComponentMouseEnter = self.createEvent_( "onComponentMouseEnter" )
		self.__onComponentMouseLeave = self.createEvent_( "onComponentMouseLeave" )

	# -------------------------------------------------
	@property
	def onTextChanged( self ) :
		"""
		���ı��ı�ʱ������
		"""
		return self.__onTextChanged

	@property
	def onComponentLClick( self ) :
		"""
		���ı��еĳ����ӱ�ǩ�����������ʱ����
		"""
		return self.__onComponentLClick

	@property
	def onComponentRClick( self ) :
		"""
		���ı��еĳ����ӱ�ǩ������Ҽ����ʱ����
		"""
		return self.__onComponentRClick

	@property
	def onComponentMouseEnter( self ) :
		"""
		�������볬���ӱ�ǩʱ������
		"""
		return self.__onComponentMouseEnter

	@property
	def onComponentMouseLeave( self ) :
		"""
		������뿪�����ӱ�ǩʱ������
		"""
		return self.__onComponentMouseLeave


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __skipToNextRow( self ) :
		"""
		����һ��
		"""
		if len( self.__tmpInner.elems ) :
			self.paintCurrLine__()
		self.__tmpInner.width = 0
		self.__tmpInner.top += self.__tmpInner.height + self.spacing
		self.__tmpInner.height = 0
		self.__tmpInner.space = self.maxWidth
		self.__tmpInner.elems = []

	def __setWidth( self, width ) :
		"""
		���� RichText �Ŀ��
		"""
#		if not self.__autoNewline :							# �� autoNewline == False ʱ���ƺ������⣬������ʱע��
#			width = min( width, self.maxWidth + 1 )
		self.gui.width = width

	# -------------------------------------------------
	def __commonPaint( self ) :
		"""
		ճ��һ���ı���widthAdapt == False��
		"""
		pyElems = self.__tmpInner.elems								# ��ǰ�е�����Ԫ��
		align = self.__tmpInner.align								# �ı�ˮƽ���뷽ʽ
		lineFlat = self.__tmpInner.lineFlat							# �ı��ߵͶ��뷽ʽ
		space = self.__tmpInner.space								# ��ǰ��ʣ����
		height = self.__tmpInner.height								# ��ǰ�и߶�
		top = self.__tmpInner.top									# ��ǰ�ж���
		middle = top + height * 0.5									# ��ǰ���м����
		bottom = top + height										# ��ǰ�еײ�����

		text = ""
		for idx, pyElem in enumerate( pyElems ) :
			text += getattr( pyElem, "text", "" )
			self.addPyChild( pyElem )
			if lineFlat == "B" : pyElem.bottom = bottom				# ǰ�������ı��߶Ȳ�һ��ʱ�����õײ�����( ��������Ƚ϶࣬��˷���ǰ )
			elif lineFlat == "M" : pyElem.middle = middle			# ǰ�������ı��߶Ȳ�һ��ʱ�������м����
			else : pyElem.top = top									# ǰ�������ı��߶Ȳ�һ��ʱ�����ö�������
			if idx == 0 :											# ���õ�һ��Ԫ�ص�ˮƽλ��
				if align == 'L' or not self.__autoNewline :			# �������( ��������Ƚ϶࣬��˷���ǰ )��������Զ����У���ˮƽ���к�ˮƽ���Ҷ���Ч
					pyElem.left = 0
				elif align == 'R' :									# �������
					pyElem.left = space
				elif align == 'C' :									# �������
					pyElem.left = max( 0, space * 0.5 )
			else :													# ���õڶ�������Ԫ�ص�ˮƽλ��
				pyElem.left = pyElems[idx - 1].right
		self.lineInfos_.append( ( text, pyElems ) )					# ��ӵ�ǰ�е����б���
		self.__tmpInner.elems = []									# ��յ�ǰ׼��ճ������
		lineWidth = pyElems[-1].right + 1							# ��ǰ�п��
		if lineWidth > self.width :
			self.__setWidth( lineWidth )							# ���� RichText �Ŀ��Ϊ��еĿ��
		Control._setHeight( self, bottom + max( self.__spacing, 0 ) )			# ���� RichText �ĸ߶�
		self.__skipToNextRow()										# ����

	def __widthAdaptPaint( self ) :
		"""
		ճ��һ���ı���widthAdapt == True��
		"""
		align = self.__tmpInner.align								# �ı�ˮƽ���뷽ʽ
		lineFlat = self.__tmpInner.lineFlat							# �ı��ߵͶ��뷽ʽ
		space = self.__tmpInner.space								# ��ǰ��ʣ����
		height = self.__tmpInner.height								# ��ǰ�и߶�
		top = self.__tmpInner.top									# ��ǰ�ж���
		middle = top + height / 2									# ��ǰ���м����
		bottom = top + height										# ��ǰ�еײ�����

		if self.__autoNewline and space <= self.__fontWidth / 2 :	# ���ʣ����С�ڰ���֣�����Ϊ RichText �Ŀ�Ⱦ��������
			self.__tmpCurrWidth = self.__maxWidth					# �������õ�ǰ���Ϊ�����
			self.__tmpWidthAdapt = False							# ������ʱ�����ӦΪ False
			self.__commonPaint()									# תΪ�� common paint
			return

		lineWidth = self.__maxWidth - space							# ��ǰ�п�
		self.__tmpCurrWidth = max( self.__tmpCurrWidth, lineWidth )	# ��¼����п�
		if align != 'L' :											# �����ǰ���ı����м������Ҷ��룬��
			lineNo = len( self.lineInfos_ )							# ��ǰ������
			self.__tmpCRElems[lineNo] = ( align, lineWidth )		# ��¼�¸������ڻ�Ҫ���� X �������
		self.__commonPaint()

	def __realignElems( self ) :
		"""
		���������м������Ҷ����Ԫ��
		"""
		for lineNo, ( align, width ) in self.__tmpCRElems.iteritems() :
			space = self.__tmpCurrWidth - width						# ʣ����
			left = space 											# �����Ҷ������������
			if align == "C" : left = max( 0, space / 2 )			# ������м���룬���Ϊʣ���ȵ�һ��
			text, pyElems = self.lineInfos_[lineNo]					# ��ȡ
			for idx, pyElem in enumerate( pyElems ) :				# ���������м������Ҷ�����ı��� X ��λ��
				if idx == 0 : pyElem.left = left
				else : pyElem.left = pyElems[idx - 1].right
		self.__tmpCRElems = {}
		if self.__tmpWidthAdapt :
			self.__setWidth( self.__tmpCurrWidth )


	# ----------------------------------------------------------------
	# friend methods for plugins
	# ----------------------------------------------------------------
	def getCurrLineWidth__( self ) :
		"""
		��ȡ��ǰ�е�����Ԫ�صĿ��
		"""
		return self.__tmpInner.width

	def getCurrLineHeight__( self ) :
		"""
		��ȡ��ǰ�е����Ԫ�ظ߶�
		"""
		return self.__tmpInner.height

	def getCurrLineSpace__( self ) :
		"""
		��ȡ��ǰ�е�ʣ����
		"""
		return self.__tmpInner.space

	def isNewLine__( self ) :
		"""
		ָ����ǰճ���ı�ʱ���Ƿ�������һ��
		"""
		return len( self.__tmpInner.elems ) == 0

	# ---------------------------------------
	def setTmpAlign__( self, align ) :
		"""
		������ʱ�ı�ˮƽ���뷽ʽ
		@type				align : str
		@type				align : "L"������룻"C"�����У�"R"���Ҷ���
		"""
		if len( align ) != 1 : return
		if align not in "LCR" : return
		if len( self.__tmpInner.elems ) :
			self.__skipToNextRow()
		self.__tmpInner.align = align

	def setTmpLineFlat__( self, mode ) :
		"""
		����ǰ�������ı��ĸߵͶ��뷽ʽ
		@type				mode : str
		@type				mode : "T"���������룻"M"���м���룻"B"���ײ�����
		"""
		if len( mode ) != 1 : return
		if mode not in "TMB" : return
		self.__tmpInner.lineFlat = mode

	def addElement__( self, pyElem ) :
		"""
		���һ�� ui Ԫ��
		@type				pyElem : python ui
		@param				pyElem : Ҫ��ӵ� python ui
		"""
		height = self.__tmpInner.height
		self.__tmpInner.width += pyElem.width
		self.__tmpInner.height = max( pyElem.height, height )
		self.__tmpInner.space -= pyElem.width
		self.__tmpInner.elems.append( pyElem )

		if hasattr( pyElem, "onLClick" ) :
			pyElem.onLClick.bind( self.onComponentLClick_ )
		if hasattr( pyElem, "onRClick" ) :
			pyElem.onRClick.bind( self.onComponentRClick_ )
		if hasattr( pyElem, "onMouseEnter" ) :
			pyElem.onMouseEnter.bind( self.onComponentMouseEnter_ )
		if hasattr( pyElem, "onMouseLeave" ) :
			pyElem.onMouseLeave.bind( self.onComponentMouseLeave_ )

	# -------------------------------------------------
	def paintCurrLine__( self ) :
		"""
		ճ����ǰ������ python Ԫ�أ�������ʱ������
		"""
		pyElems = self.__tmpInner.elems								# ��ǰ�е�����Ԫ��
		if len( pyElems ) == 0 : return								# �����ǰ����û��Ԫ�أ��򷵻�
		if self.__tmpWidthAdapt :									# �������Ӧ���
			self.__widthAdaptPaint()
		else :
			self.__commonPaint()

	# -------------------------------------------------
	def newLine__( self, n = 1 ) :
		"""
		���� n ������
		@type				n : int
		@param				n : Ҫ����Ŀ�������������� 0
		"""
		if n < 1 : return
		if len( self.__tmpInner.elems ) :
			self.paintCurrLine__()
			n -= 1
		self.__tmpInner.width = 0
		self.__tmpInner.top += n * self.lineHeight
		self.__tmpInner.height = 0
		self.__tmpInner.space = self.maxWidth
		self.__tmpInner.elems = []

	# -------------------------------------------------
	def setTemp__( self, key, value, added = True ) :
		"""
		����/���һ����ʱ����
			�����������������һ����ʱ������Ȼ�󴫵ݸ���һ������ã�
			��������ʵ�ֲ��֮�����ݴ��ݣ��Ӷ�ʵ�ֲ��֮��Ĺ���
		@type			key	  : all types except list and dict
		@param			key	  : ��
		@type			value : all types
		@param			value : ֵ
		@type			added : bool
		@param			added : ��������ڸü����Ƿ����
		@rtype				  : bool
		@return				  : �������/��ӳɹ����򷵻� True�����򷵻� False
		"""
		if added :
			self.__tmpsForPL[key] = value
			return True
		if self.__tmpsForPL.has_key( key ) :
			self.__tmpsForPL[key] = value
			return True
		return False

	def getTemp__( self, key, default = None ) :
		"""
		��ȡ��ʱ����ֵ
		@type			key : all types except list and dict
		@param			key : ��
		@rtype				: all types
		@return				: ָ�����µ�ֵ
		"""
		return self.__tmpsForPL.get( key, default )

	def removeTemp__( self, key ) :
		"""
		ɾ��һ����ʱ����
		@type			key : all types except list and dict
		@param			key : ��
		@rtype				: bool
		@return				: ��������ڸü��򷵻� False�����򷵻� True
		"""
		if self.__tmpsForPL.has_key( key ) :
			self.__tmpsForPL.pop( key )
			return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setPluginsPath( self, path ) :
		"""
		���ò��·��
		@type				path : str
		@param				path : �������·��
		@return					 : None
		"""
		if path in self.__cg_plugins :
			self.__pluginMgr = self.__cg_plugins[path]
		else :
			self.__pluginMgr = PluginMgr( path )
			self.__cg_plugins[path] = self.__pluginMgr

	def clear( self ) :
		"""
		����ı�
		@return					: None
		"""
		self.__text = ""
		self.__tmpInner.top = 0								# �ж�������Ϊ 0
		self.__tmpInner.width = 0							# �п�����Ϊ 0
		self.__tmpInner.height = 0							# �и߶�����Ϊ 0
		self.__tmpInner.space = self.maxWidth				# ����Ϊ�����
		self.__tmpInner.align = self.__align				# �ָ���ʱ���뷽ʽ
		self.__tmpInner.lineFlat = self.__lineFlat			# �ָ���ʱ���뷽ʽ
		self.__tmpInner.elems = []							# �����Ԫ��
		self.__tmpsForPL = {}								# ɾ�������ʱ����

		self.__tmpWidthAdapt = self.__widthAdapt			# �ָ��������Ӧ���
		self.__tmpCurrWidth = 0.0							# ���������еĿ��
		self.__tmpCRElems = {}								# ����м������Ҷ��������Ϣ

		for text, pyElems in self.lineInfos_ :
			for pyElem in pyElems : pyElem.dispose()
		self.lineInfos_ = []
		self.__setWidth( 0 )
		Control._setHeight( self, 0.0 )
		for plugin in self.__pluginMgr.values() :
			plugin.onCleared( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onParentWidthChanged_( self, oldWidth, newWidth ) :
		"""
		�����׿�ȸı�ʱ������
		"""
		Control.onParentWidthChanged_( self, oldWidth, newWidth )
		if  self.h_dockStyle == "HFILL" :
			self.maxWidth += ( newWidth - oldWidth )

	# -------------------------------------------------
	def onComponentLClick_( self, pyComponent ) :
		"""
		��ĳ�����ӱ�ǩ������������ʱ����
		"""
		self.onComponentLClick( pyComponent )
		if not pyComponent.isMouseHit() :
			rds.ccursor.normal()
			self.onComponentMouseLeave( pyComponent )
		#INFO_MSG( "a component in RichText had been clicked by left mouse: ", pyComponent.linkMark )

	def onComponentRClick_( self, pyComponent ) :
		"""
		��ĳ�����ӱ�ǩ������Ҽ�����ʱ����
		"""
		self.onComponentRClick( pyComponent )
		if not pyComponent.isMouseHit() :
			rds.ccursor.normal()
		#INFO_MSG( "a component in RichText had been clicked by right mouse: ", pyComponent.linkMark )

	def onComponentMouseEnter_( self, pyComponent ) :
		"""
		��������ĳ�����ӱ�ǩʱ������
		"""
		self.onComponentMouseEnter( pyComponent )
		#INFO_MSG( "mouse enter a component in RichText: ", pyComponent.linkMark )

	def onComponentMouseLeave_( self, pyComponent ) :
		"""
		������뿪ĳ�����ӱ�ǩʱ������
		"""
		self.onComponentMouseLeave( pyComponent )
		#INFO_MSG( "mouse leave a component in RichText: ", pyComponent.linkMark )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getAlign( self ) :
		return self.__align

	def _setAlign( self, align ) :
		if isDebuged :
			assert len( align ) == 1 and align in "LCR", "algin mode must be 'L', 'C', 'R'!"
		self.__align = align
		self.__tmpInner.align = align
		self._setText( self.text )

	def _getLineFlat( self ) :
		return self.__lineFlat

	def _setLineFlat( self, mode ) :
		if isDebuged :
			assert len( mode ) == 1 and mode in "TMB", "algin mode must be 'T', 'M', 'B'!"
		self.__lineFlat = mode
		self.__tmpInner.lineFlat = mode
		self._setText( self.text )

	def _getAutoNewline( self ) :
		return self.__autoNewline

	def _setAutoNewline( self, autoNewline ) :
		if autoNewline != self.__autoNewline :
			self.__autoNewline = autoNewline
			self._setText( self.__text )

	def _getWidthAdapt( self ) :
		return self.__widthAdapt

	def _setWidthAdapt( self, adapted ) :
		self.__widthAdapt = adapted
		self.__tmpWidthAdapt = adapted
		self._setText( self.__text )

	# ---------------------------------------
	def _getText( self ) :
		return self.__text

	def _setText( self, text ) :
		TextType = type( text )
		if TextType is not str and TextType is not unicode :
			raise TypeError( "text must be str or unicude type, but not %s" % str( TextType ) )
		self.clear()
		self.tmpOuter__ = TmpOuter( self )
		self.__text += text											# �������ı�
		lineInfos = self.__pluginMgr.parse( self, text )			# ��ʹ�ò�������ı�
		for esc, info in lineInfos :								# �����ı���Ϣ��ճ���ı�
			self.__pluginMgr[esc].transform( self, info )			# ʹ�ò��ճ���ı�Ԫ��
		self.paintCurrLine__()										# ճ�����һ��
		self.__realignElems()										# �����м������Ҷ����Ԫ��
		self.__tmpsForPL = {}										# ɾ�������ʱ����
		del self.tmpOuter__
		self.onTextChanged()										# �����ı��ı��¼�

	# ---------------------------------------
	def _getViewText( self ) :
		text = ""
		for t, pyElems in self.lineInfos_ :
			text += t
		return text

	# ---------------------------------------
	def _getFont( self ) :
		return self.__font

	def _setFont( self, font ) :
		self.__font = font
		self.__fontWidth = Font.getFontWidth( font )
		self._setText( self.__text )

	def _getFontSize( self ) :
		return self.__fontSize

	def _setFontSize( self, size ) :
		if not self.__font.endswith( ".font" ) :
			self.__fontSize = size
			self._setText( self.__text )

	# ---------------------------------------
	def _getCharSpace( self ) :
		return self.__charSpace

	def _setCharSpace( self, space ) :
		self.__charSpace = space
		self._setText( self.__text )

	def _getSpacing( self ) :
		return self.__spacing

	def _setSpacing( self, spacing ) :
		self.__spacing = spacing
		self._setText( self.__text )

	# ---------------------------------------
	def _getLimning( self ) :
		return self.__limning

	def _setLimning( self, style ) :
		if isDebuged :
			assert style in ( Font.LIMN_NONE, Font.LIMN_OUT, Font.LIMN_SHD ), \
				"limning style must be: Font.LIMN_NONE or Font.LIMN_OUT or Font.LIMN_SHD"
		self.__limning = style
		self._setText( self.__text )

	def _getLimnColor( self ) :
		return self.__limnColor

	def _setLimnColor( self, color ) :
		self.__limnColor = color
		self._setText( self.__text )

	# -------------------------------------------------
	def _getForeColor( self ) :
		return self.__fcolor

	def _setForeColor( self, color ) :
		self.__fcolor = color
		self._setText( self.__text )

	def _getBackColor( self ) :
		return self.__bcolor

	def _setBackColor( self, color ) :
		self.__bcolor = color
		self._setText( self.__text )

	# -------------------------------------------------
	def _getLineCount( self ) :
		return len( self.lineInfos_ )

	def _getLineHeight( self ) :
		return Font.getFontHeight( self.font ) + self.spacing

	# -------------------------------------------------
	def _getMaxWidth( self ) :
		return self.__maxWidth

	def _setMaxWidth( self, width ) :
		maxWidth = max( self.__fontWidth, width )
		oldWidth = self.__maxWidth
		delta = width - oldWidth
		if self.h_dockStyle == "CENTER" :
			self.left -= delta / 2
		elif self.h_dockStyle == "RIGHT" :
			self.left -= delta
		self.__maxWidth = maxWidth
		self._setText( self.__text )

	# ---------------------------------------
	def _setWidth( self, width ) :
		pass

	def _getHeight( self ) :
		if self.text == "" :
			return 0
		return Control._getHeight( self )

	def _setHeight( self, height ) :
		pass


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	align = property( _getAlign, _setAlign )					# chr: ��ȡ/���ö�������( 'L'Ϊ�����, 'C'Ϊ�м����, 'R'Ϊ�Ҷ���)
	lineFlat = property( _getLineFlat, _setLineFlat )			# chr: ��ȡ/�����ı��߶ȵĶ��뷽ʽ�����ǰ�������ı��߶Ȳ�һ�����ǲ���
																#	   �������루'T'�������м���루'M'�������ǵײ����루'B'��
	autoNewline = property( _getAutoNewline, _setAutoNewline )	# bool: �Ƿ��Զ�����
	widthAdapt = property( _getWidthAdapt, _setWidthAdapt )		# bool: ���ڿ��󡢿��ҵ������Ƿ��Զ����Զ���Ӧ�Ŀ����Ϊ������( ֻ�� autoNewline Ϊ False ʱ��������)
	text = property( _getText, _setText )						# str: ��ȡ/����Դ�ı�
	viewText = property( _getViewText ) 						# str: ��ȡ�ɼ������ı�
	font = property( _getFont, _setFont )						# str: ��ȡ/����Ĭ������
	fontSize = property( _getFontSize, _setFontSize )			# int: ��ȡ/���������С
	charSpace = property( _getCharSpace, _setCharSpace )		# float: ��ȡ/�����ּ��
	spacing = property( _getSpacing, _setSpacing )				# float: ��ȡ/�����м��
	foreColor = property( _getForeColor, _setForeColor )		# tuple/Vector4/Vector3: ��ȡ/����Ĭ��ǰ����ɫ
	backColor = property( _getBackColor, _setBackColor )		# tuple/Vector4/Vector3: ��ȡ/����Ĭ�ϱ�����ɫ
	limning = property( _getLimning, _setLimning )				# MACRO DEFINATION: ��ȡ/�������Ч����Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( _getLimnColor, _setLimnColor )		# tuple: ��ȡ/���������ɫ

	lineCount = property( _getLineCount )						# int: ��ȡ�ı�������
	lineHeight = property( _getLineHeight )						# float: ��ȡĬ���и߶�

	maxWidth = property( _getMaxWidth, _setMaxWidth )			# float: ��ȡ/���� RichText ������ȣ������ÿ�ȣ����Զ����У������Ϊ���������ʾ���Զ�����
	width = property( Control._getWidth, _setWidth )			# float: ��ȡ RichText ��ʵ�ʿ��
	height = property( _getHeight, _setHeight )					# float: ��ȡ RichText �ĸ߶�


# --------------------------------------------------------------------
# implement line text for richtext
# --------------------------------------------------------------------
class TextLine( StaticLabel ) :
	def __init__( self ) :
		label = hfUILoader.load( "guis/controls/richtext/textline.gui" )
		StaticLabel.__init__( self, label )
		self._setFont( self.font )
		self.autoSize = True

	def __del__( self ) :
		StaticLabel.__del__( self )
		if Debug.output_del_RichTextElem :
			INFO_MSG( str( self ) )


# --------------------------------------------------------------------
# implement plugin factory for richtext
# --------------------------------------------------------------------
class PluginMgr( object ) :
	def __init__( self, path = "" ) :
		"""
		@type			path : str
		@param			path : �������·��
		"""
		self.__plugins = {}
		self.__plugins[""] = CommonPlugin( self )			# Ĭ�ϲ�����ת��Ĳ��
		self.__splitPattern = re.compile( "''" )			# ��ʽ������ģ��
		if path != "" :
			self.__intPlugins( path )						# ��ʼ�����в��

		self.__ptnNewline = re.compile( "(\r\n|\n)|(\r)" )	# ���з�ģ��

	def __getitem__( self, key ) :
		return self.__plugins[key]

	def __iter__( self ) :
		return self.__plugins.__iter__()

	def has_key( self, key ) :
		return self.__plugins.has_key( key )

	def keys( self ) :
		return self.__plugins.keys()

	def values( self ) :
		return self.__plugins.values()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __createPlugin( self, module ) :
		"""
		����һ�����
		"""
		def getPluginClasses( memberNames ) :											# ���˵����Ǽ̳��� BasePlugin ����
			classes = []
			for memberName in memberNames :
				member = getattr( module, memberName )
				if not inspect.isclass( member ) : continue
				if not issubclass( member, BasePlugin ) : continue
				if inspect.getmodule( member ) == module :
					classes.append( member )
			return classes

		plugins = {}
		pluginClasses = getPluginClasses( dir( module ) )								# ��ȡ�����
		for PluginClass in pluginClasses :
			plugin = PluginClass( self )												# ���ɲ��ʵ��
			if plugin.esc == "" :														# ����������ת���ַ�
				ERROR_MSG( "plugin's ESC mustn't be empty!" % module )
			else :
				plugins[plugin.esc] = plugin											# ���ز���������ת���ַ�
		return plugins

	def __intPlugins( self, path ) :
		"""
		��ʼ�����в��
		"""
		plmodules = SmartImport.importAll( path, "PL_*" )								# ��ȡ���в��ģ����( ����״̬�� )
		strPatterns = []
		reKeysPattern = re.compile( r"\.|\"|\^|\$|\*|\+|\?|\{|\[|\]|\\|\||\(|\)" )		# ������ʽ�ؼ���
		for module in plmodules :
			pluginInfos = self.__createPlugin( module )
			for esc, plugin in pluginInfos.iteritems() :
				if self.has_key( esc ) :
					WARNING_MSG( "ESC has been used by %s!" % str( self[esc] ) )
				else :
					self.__plugins[esc] = plugin
					strPatterns.append( re.escape( esc ) )								# ������ǰ����Ϸ�б�ܱ�ʾת��
		if len( strPatterns ) > 0 :
			self.__splitPattern = re.compile( "|".join( strPatterns ) )					# �������в����ƥ��ģʽ

	# -------------------------------------------------
	def __addFormatInfo( self, pyRichText, lineInfos, esc, text ) :
		"""
		����ת���ַ������������ı���ȡ��ʽ����Ϣ
		"""
		if esc == "" and text == "" : return []
		attrsInfo, leaveText = self[esc].format( pyRichText, text )			# ������ز������
		if attrsInfo is not None :											# ������ͳɹ�
			lineInfos.append( ( esc, attrsInfo ) )
		if leaveText != "" :
			if len( lineInfos ) and lineInfos[-1][0] == "" :				# ���ԭ���һ��Ҳ��Ĭ�ϸ�ʽ
				leaveText = lineInfos.pop()[1] + leaveText					# ��׷���ı�
			lineInfos.append( ( "", leaveText ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def parse( self, pyRichText, text ) :
		"""
		�������в������һ���ı�
		@type				pyRichText : RichText
		@param				pyRichText : ��������� RichText �ؼ�
		@type				text	 : str
		@param				text	 : Ҫ���͵��ı�
		@rtype						 : list
		@return						 : ת�����ı��б� [ ( ת���ַ�, ���͸�ʽ�����������Ϣ( ��ͬ��ת���ַ��в�ͬ�����ͣ������ɲ���Զ��� ) )]
		"""
		text = self.__ptnNewline.sub( lambda e : "@B" if e.groups()[0] else "", text )
		lineInfos = []															# ����ת����Ϣ
		currEsc = ""															# ��ǰ���͵���ת���ַ�(Ĭ��ʹ�û�����ת���ַ�)
		currStart = 0															# ��ǰ���͵���ת���ַ�����ʼλ��

		def getEscInfo( i ) :
			try :
				match = i.next()
				esc = match.group( 0 )											# ת���ַ�
				start = match.start()											# ת���ַ���ʼλ��
				end = match.end()												# ת���ַ�����λ��
				return esc, start, end
			except StopIteration, e :
				count = len( text )
				return "", count, count											# ����Ĭ�ϵĲ��ת����Ϣ

		wtext = csstring.toWideString( text )
		iter = self.__splitPattern.finditer( wtext )							# ����ת���ַ�
		while True :															# �����ȡת���ַ���Ϣ
			esc, start, end = getEscInfo( iter )								# ��ȡת����Ϣ��ת���ַ�����ʼ������λ�ã��Լ�ת���ַ�
			includedText = wtext[currStart : start]								# ��ǰ��ʽ���������ַ�
			includedText = csstring.toString( includedText )
			self.__addFormatInfo( pyRichText, lineInfos, currEsc, includedText )# ׷�Ӹ�ʽ����Ϣ��
			if start == end : break												# �������
			currEsc = esc
			currStart = end
		return lineInfos


# --------------------------------------------------------------------
# implement plugin base class for richtex text
# --------------------------------------------------------------------
class BasePlugin :
	"""
	������࣬���в��������̳и���
	"""
	esc_ = None															# �����Ӧ��ת���ַ����������ø��ַ�����������Ч��

	def __init__( self, owner ) :
		if owner :
			self.__owner = weakref.ref( owner )
		else :
			self.__owner = None
		if isDebuged :
			assert getattr( self.__class__, "esc_" ) is not None, \
				"%s: RichText plugin's ESC must be set a nonempty string!" % str( self.__class__.__name__ )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def esc( self ) :
		"""
		�������ת���ַ�
		"""
		return getattr( self.__class__, "esc_" )

	@property
	def owner( self ) :
		"""
		�����Ĳ������
		"""
		if self.__owner is None :
			return None
		self.__owner()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def format( self, pyRichText, text ) :
		"""
		���ݴ����δ��ʽ���ַ�������ʽ���ɱ�����Զ����������Ϣ
		ע�⣺���в��������д�÷������Ӷ����ظ�����Ҫ�ĸ�ʽ��������Ϣ
		@type				pyRichText : RichText
		@param				pyRichText : ����Ҫ���������� RichText �ؼ�
		@type				text	 : str
		@param				text	 : ����ʽ������������Ĵ���������ʽ����ǵ���һ����ʽ�����֮����ı�
		@rtype					 	 : tuple / None
		@return					 	 : �����ʽ��ʧ�ܣ��򷵻�: ( None, �������ı� )
									   ��������ص�����ı���û�и�ʽ������ԭ������ͨ�ı���ʾ
									   ����ֵ�����٣��ڣ�
									   �� �ɹ���Ϊ������ĸ�ʽ����Ϣ�����Ϳ����Լ����壬����� transform �ڶ��������������ֵ��ʧ����Ϊ None
									   �� ��ȡ��ʽ����Ϣ��ʣ����ı�����������û���õ���ʽ�������Щ�ı���
										  ��ԭ�����أ���Ĭ�ϲ��������ͨ�ı�����
										  ��Ȼ�������Ҫ�Ļ�Ҳ���Խ�ȡ��Щ�ı�����Ϊ������Լ�ĳ�����Ե��ı���
		"""
		return None, text

	# -------------------------------------------------
	def transform( self, pyRichText, attrInfo ) :
		"""
		�� format ���ͳ����Ľ����ת��Ϊ RichText ���õ� component�������� RichText �ṩ�� API ��� component ������һЩ����:
		@type				pyRichText : controls.RichText
		@param				pyRichText : ������ RichText �ؼ�
		@type				attrInfo : all types
		@param				attrInfo : �ò���ֵ�в���Լ����壬���뱾��� format �������ص� tuple �ĵ�һ��Ԫ��һ��

		������
		getCurrLineWidth__()		: ��ȡ��ǰ׼��ճ���еĿ��
		getCurrLineHeight__()		: ��ȡ��ǰ׼��ճ���еĸ߶ȣ�������Ǹ� python Ԫ�صĸ߶���Ϊ�и߶ȣ�
		getCurrLineSpace__()		: ��ȡ��ǰ׼��ճ���е�ʣ���ȣ��ɸ������������۶�һ�У����������ֵС�� 0�����ʾ���Զ�����
		isNewLine__()				: ��ȡ��ǰ׼��ճ�����Ƿ��Ǹո�����һ��
		setTmpAlign__( align )		: ������ʱ���ı����뷽ʽ
		addElement__( pyElem )		: ���ø÷������һ�� python Ԫ��
		paintCurrLine__()			: ������ʱ�����øýӿ�ճ����ǰ��Ԫ��
		newLine__( n = 1 )			: ���У�ͨ���ֶ����øú�������һ�л���У�ͨ�� n ָ��Ҫ����������n ������ڵ��� 1��
		���ԣ�
		tmpOut__['font']			: ���͵���ǰʱ����ʱ����( ���޸�ֵ )
		tmpOut__['fcolor']			: ���͵���ǰʱ����ʱǰ��ɫ( ���޸�ֵ )
		tmpOut__['bcolor']			: ���͵���ǰʱ����ʱ����ɫ( ���޸�ֵ )

		ע���� ���в��������д�����Ǹ÷����������Լ��� python ui Ԫ��
			�� �����ڸ÷����е��� RichText �κηǡ���Ԫ��������������������ķ�������ķ�����
			�� �����ڸ÷��������� RichText ���κ�����ֵ�����Ի�ȡ��
		"""
		pass


	# ----------------------------------------------------------------
	@staticmethod
	def getSource() :
		"""
		��ȡ��ʽ���ı�
		"""
		return ""


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onCleared( self, pyRichText ) :
		"""
		���ı����ʱ������
		"""
		pass



# --------------------------------------------------------------------
# implement common plugin class for richtex text
# --------------------------------------------------------------------
class CommonPlugin( BasePlugin ) :
	esc_ = ''

	def __init__( self, owner ) :
		BasePlugin.__init__( self, owner )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def format( self, pyRichText, text ) :
		return text, ""

	def transform( self, pyRichText, text ) :
		def createLine() :
			pyLine = TextLine()
			tmpOuter = pyRichText.tmpOuter__
			pyLine.foreColor = tmpOuter.fcolor							# ��ǰǰ��ɫ
			pyLine.backColor = tmpOuter.bcolor							# ��ǰ����ɫ
			pyLine.charSpace = tmpOuter.charSpace						# �ּ��
			pyLine.limning = tmpOuter.limning							# ���״̬
			pyLine.limnColor = tmpOuter.limnColor						# �����ɫ
			pyLine.setFontInfo( {
				"font"		: tmpOuter.font,							# ����
				"size"		: tmpOuter.fontSize,						# �����С
				"bold"		: tmpOuter.bold,							# �Ƿ�Ϊ����
				"italic"	: tmpOuter.italic,							# �Ƿ�б��
				"underline" : tmpOuter.underline,						# �Ƿ����»���
				"strikeOut" : tmpOuter.strikeOut,						# �Ƿ���ɾ����
				} )
			return pyLine

		while True :													# �ж��Ƿ����۶��ı�
			pyLine = createLine()										# ����һ���ı��� UI
			ltext, rtext = text, ""										# Ĭ���ܲ�����
			if pyRichText.autoNewline :									# �����Ҫ�Զ�����
				space = pyRichText.getCurrLineSpace__()					# ��ǰ��ʣ����
				ltext, rtext, lwtext, rwtext = \
					pyLine.splitText( space, "CUT", text )				# ����ַ���
				if len( rwtext ) :
					fchr = csstring.toString( rwtext[0] )
					if fchr in g_interpunctions :						# ���۶ϱ�����
						ltext += fchr
						rtext = csstring.toString( rwtext[1:] )
			if rtext == "" :											# ���ʣ��Ŀռ���Է��������ı�
				pyLine.text = ltext										# �������ı�
				pyRichText.addElement__( pyLine )						# �ŵ���ǰ����
				break													# ��������ı���ճ����������
			elif ltext == "" and not pyRichText.isNewLine__() :			# ���ʣ��Ŀ�Ȳ����Է���һ������
				pyRichText.paintCurrLine__()							# ճ����ǰ�У�������һ��
			elif ltext == "" :											# ��������̫С����һ����Ҳ�Ų���
				wtext = csstring.toWideString( text )					# ���Ƚ��ַ�����ת��Ϊ���ַ���
				pyLine.text = csstring.toString( wtext[0] )				# ��ֻ�ŵ�һ����
				pyRichText.addElement__( pyLine )						# ��ӵ���ǰ��
				pyRichText.paintCurrLine__()							# ճ����ǰ��
				text =  wtext[1:]										# ���ı��еĵ�һ���ַ�ȥ����ʣ�����Ϊ��һ��ѭ���� text
			else :														# ����ı����۶ϳ�������
				pyLine.text = ltext										# �Ȼ�ȡǰ�벿��
				pyRichText.addElement__( pyLine )						# ����ǰ�벿���ı��ŵ���ǰ��
				pyRichText.paintCurrLine__()							# ճ����ǰ��
				text = rtext											# ��ʣ����Ұ벿����Ϊ��һ��ѭ���� text

	# ----------------------------------------------------------------
	@staticmethod
	def getSource() :
		"""
		��ȡ��ʽ���ı�
		"""
		return ""
