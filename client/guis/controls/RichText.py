# -*- coding: gb18030 -*-
#
# $Id: RichText.py,v 1.58 2008-08-29 02:39:07 huangyongwei Exp $

"""
implement label array class。

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
	用于顺序粘贴文本时，保存一些临时变量
	"""
	__slots__ = ( "top", "width", "height", "space", "align", "lineFlat", "elems" )

	def __init__( self ) :
		self.top = 0					# 当前行文本的顶部距离
		self.width = 0					# 当前行文本的宽度
		self.height = 0					# 当前行文本的高度
		self.space = 0					# 当前行文本的剩余宽度
		self.align = "L"				# 当前行文本的水平停靠方式
		self.lineFlat = "B"				# 当前行文本的垂直对齐方式
		self.elems = []					# 当前行文本包含的 python 元素

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
	静态丰富文本控件
	"""
	__cg_plugins = {}

	def __init__( self, panel = None, pyBinder = None ) :
		if panel :
			if isDebuged :
				assert type( panel ) is GUI.Window, "panel of richtext must be a GUI.Window!"
		else :
			panel = hfUILoader.load( "guis/controls/richtext/board.gui" )
		Control.__init__( self, panel, pyBinder )
		self.__pluginMgr = PluginMgr()							# 插件管理器

		self.__text = ""										# 记录源文本
		self.__align = 'L'										# 默认对齐方式为靠左( 可选对齐方式：L, C, R )
		self.__lineFlat = "B"									# 如果前后两行文本高度不一样时，采用什么样的对齐方式（T，M，B）
		self.__font = Font.defFont								# 默认字体
		self.__fontSize = Font.defFontSize						# 默认字体大小
		self.__fcolor = ( 255, 255, 255, 255 )					# 默认字体颜色
		self.__bcolor = ( 255, 255, 255, 0 )					# 默认背景色
		self.__charSpace = Font.defCharSpace					# 默认字间距
		self.__spacing = Font.defSpacing						# 行间距
		self.__limning = Font.defLimning						# 描边样式
		self.__limnColor = Font.defLimnColor					# 描边颜色

		self.__fontWidth = Font.getFontWidth( self.font )		# 字体宽度
		self.__maxWidth = max( self.width, self.__fontWidth )	# 允许的最大宽度（文本宽度超出该宽度将会自动换行）
		Control._setHeight( self, 0.0 )							# 默认高度为行间距
		self.__autoNewline = True								# 是否自动换行
		self.__widthAdapt = False								# 是否自适应宽度（将最长行的宽度作为最大宽度）

		self.lineInfos_ = []									# 存放所有行文本信息，其元素为：( 行字符串，行 python 元素列表 )

		self.__tmpInner = _TempInner()							# 记录当前行的属性( 外界不可设置 )
		self.__tmpInner.top = self.__spacing					# 当前行的顶距
		self.__tmpInner.width = 0								# 当前行所有元素的宽度
		self.__tmpInner.height = 0								# 当前行高度（以最大高度的文本标签作为这行的高度）
		self.__tmpInner.space = self.maxWidth					# 当前行的剩余宽度
		self.__tmpInner.align = self.__align					# 当前文本对齐方式
		self.__tmpInner.lineFlat = self.__lineFlat				# 当前文本对齐方式
		self.__tmpInner.elems = []								# 当前行包括的所有元素

		self.__tmpWidthAdapt = self.__widthAdapt				# 判断当前是否还处于 widthAdapt 状态
		self.__tmpCurrWidth = 0.0								# 当前所有粘贴的文本行中最长文本的宽度
		self.__tmpCRElems = {}									# 如果 __widthAdapt 为 True，则用于保存当前中间对齐和右对齐的文本: { 行索引 : ( 对齐方式, 行宽度 ) }

		#self.tmpOuter__ = TmpOuter( self )						# 记录当前行的属性，插件可修改，但不可增加键。( 只在赋文本的过程中使用，用完后删除，这里以注释方式写出来，只是标记有这么一个属性 )
		self.__tmpsForPL = {}									# 保存插件临时变量（用于插件之间传递值）

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
		当文本改变时被触发
		"""
		return self.__onTextChanged

	@property
	def onComponentLClick( self ) :
		"""
		当文本中的超链接标签被鼠标左键点击时触发
		"""
		return self.__onComponentLClick

	@property
	def onComponentRClick( self ) :
		"""
		当文本中的超链接标签被鼠标右键点击时触发
		"""
		return self.__onComponentRClick

	@property
	def onComponentMouseEnter( self ) :
		"""
		当鼠标进入超链接标签时被触发
		"""
		return self.__onComponentMouseEnter

	@property
	def onComponentMouseLeave( self ) :
		"""
		当鼠标离开超链接标签时被触发
		"""
		return self.__onComponentMouseLeave


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __skipToNextRow( self ) :
		"""
		下挑一行
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
		设置 RichText 的宽度
		"""
#		if not self.__autoNewline :							# 对 autoNewline == False 时，似乎有问题，所以暂时注销
#			width = min( width, self.maxWidth + 1 )
		self.gui.width = width

	# -------------------------------------------------
	def __commonPaint( self ) :
		"""
		粘贴一行文本（widthAdapt == False）
		"""
		pyElems = self.__tmpInner.elems								# 当前行的所有元素
		align = self.__tmpInner.align								# 文本水平对齐方式
		lineFlat = self.__tmpInner.lineFlat							# 文本高低对齐方式
		space = self.__tmpInner.space								# 当前行剩余宽度
		height = self.__tmpInner.height								# 当前行高度
		top = self.__tmpInner.top									# 当前行顶距
		middle = top + height * 0.5									# 当前行中间距离
		bottom = top + height										# 当前行底部距离

		text = ""
		for idx, pyElem in enumerate( pyElems ) :
			text += getattr( pyElem, "text", "" )
			self.addPyChild( pyElem )
			if lineFlat == "B" : pyElem.bottom = bottom				# 前后两段文本高度不一致时，采用底部对齐( 这种情况比较多，因此放在前 )
			elif lineFlat == "M" : pyElem.middle = middle			# 前后两段文本高度不一致时，采用中间对齐
			else : pyElem.top = top									# 前后两段文本高度不一致时，采用顶部对齐
			if idx == 0 :											# 设置第一个元素的水平位置
				if align == 'L' or not self.__autoNewline :			# 如果靠左( 这种情况比较多，因此放在前 )，如果不自动换行，则水平居中和水平靠右都无效
					pyElem.left = 0
				elif align == 'R' :									# 如果靠右
					pyElem.left = space
				elif align == 'C' :									# 如果居中
					pyElem.left = max( 0, space * 0.5 )
			else :													# 设置第二个以上元素的水平位置
				pyElem.left = pyElems[idx - 1].right
		self.lineInfos_.append( ( text, pyElems ) )					# 添加当前行到行列表中
		self.__tmpInner.elems = []									# 清空当前准备粘贴的行
		lineWidth = pyElems[-1].right + 1							# 当前行宽度
		if lineWidth > self.width :
			self.__setWidth( lineWidth )							# 设置 RichText 的宽度为最长行的宽度
		Control._setHeight( self, bottom + max( self.__spacing, 0 ) )			# 设置 RichText 的高度
		self.__skipToNextRow()										# 换行

	def __widthAdaptPaint( self ) :
		"""
		粘贴一行文本（widthAdapt == True）
		"""
		align = self.__tmpInner.align								# 文本水平对齐方式
		lineFlat = self.__tmpInner.lineFlat							# 文本高低对齐方式
		space = self.__tmpInner.space								# 当前行剩余宽度
		height = self.__tmpInner.height								# 当前行高度
		top = self.__tmpInner.top									# 当前行顶距
		middle = top + height / 2									# 当前行中间距离
		bottom = top + height										# 当前行底部距离

		if self.__autoNewline and space <= self.__fontWidth / 2 :	# 如果剩余宽度小于半个字，则认为 RichText 的宽度就是最大宽度
			self.__tmpCurrWidth = self.__maxWidth					# 并且设置当前宽度为最大宽度
			self.__tmpWidthAdapt = False							# 设置临时宽度适应为 False
			self.__commonPaint()									# 转为用 common paint
			return

		lineWidth = self.__maxWidth - space							# 当前行宽
		self.__tmpCurrWidth = max( self.__tmpCurrWidth, lineWidth )	# 记录最大行宽
		if align != 'L' :											# 如果当前行文本是中间对齐或右对齐，则
			lineNo = len( self.lineInfos_ )							# 当前行索引
			self.__tmpCRElems[lineNo] = ( align, lineWidth )		# 记录下该行属于还要调整 X 坐标的行
		self.__commonPaint()

	def __realignElems( self ) :
		"""
		重新排列中间对齐和右对齐的元素
		"""
		for lineNo, ( align, width ) in self.__tmpCRElems.iteritems() :
			space = self.__tmpCurrWidth - width						# 剩余宽度
			left = space 											# 假设右对齐来设置左距
			if align == "C" : left = max( 0, space / 2 )			# 如果是中间对齐，左距为剩余宽度的一半
			text, pyElems = self.lineInfos_[lineNo]					# 获取
			for idx, pyElem in enumerate( pyElems ) :				# 重新设置中间对齐和右对齐的文本的 X 轴位置
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
		获取当前行的所有元素的宽度
		"""
		return self.__tmpInner.width

	def getCurrLineHeight__( self ) :
		"""
		获取当前行的最大元素高度
		"""
		return self.__tmpInner.height

	def getCurrLineSpace__( self ) :
		"""
		获取当前行的剩余宽度
		"""
		return self.__tmpInner.space

	def isNewLine__( self ) :
		"""
		指出当前粘贴文本时，是否正新起一行
		"""
		return len( self.__tmpInner.elems ) == 0

	# ---------------------------------------
	def setTmpAlign__( self, align ) :
		"""
		设置临时文本水平对齐方式
		@type				align : str
		@type				align : "L"：左对齐；"C"：居中；"R"；右对齐
		"""
		if len( align ) != 1 : return
		if align not in "LCR" : return
		if len( self.__tmpInner.elems ) :
			self.__skipToNextRow()
		self.__tmpInner.align = align

	def setTmpLineFlat__( self, mode ) :
		"""
		设置前后两段文本的高低对齐方式
		@type				mode : str
		@type				mode : "T"：顶部对齐；"M"：中间对齐；"B"；底部对齐
		"""
		if len( mode ) != 1 : return
		if mode not in "TMB" : return
		self.__tmpInner.lineFlat = mode

	def addElement__( self, pyElem ) :
		"""
		添加一个 ui 元素
		@type				pyElem : python ui
		@param				pyElem : 要添加的 python ui
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
		粘贴当前行所有 python 元素，当行满时被调用
		"""
		pyElems = self.__tmpInner.elems								# 当前行的所有元素
		if len( pyElems ) == 0 : return								# 如果当前行中没有元素，则返回
		if self.__tmpWidthAdapt :									# 如果自适应宽度
			self.__widthAdaptPaint()
		else :
			self.__commonPaint()

	# -------------------------------------------------
	def newLine__( self, n = 1 ) :
		"""
		插入 n 个空行
		@type				n : int
		@param				n : 要插入的空行数，必须大于 0
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
		设置/添加一个临时变量
			插件可以在这里设置一个临时变量，然后传递给下一个插件用，
			这样可以实现插件之间数据传递，从而实现插件之间的关联
		@type			key	  : all types except list and dict
		@param			key	  : 键
		@type			value : all types
		@param			value : 值
		@type			added : bool
		@param			added : 如果不存在该键，是否添加
		@rtype				  : bool
		@return				  : 如果设置/添加成功，则返回 True，否则返回 False
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
		获取临时变量值
		@type			key : all types except list and dict
		@param			key : 键
		@rtype				: all types
		@return				: 指定键下的值
		"""
		return self.__tmpsForPL.get( key, default )

	def removeTemp__( self, key ) :
		"""
		删除一个临时变量
		@type			key : all types except list and dict
		@param			key : 键
		@rtype				: bool
		@return				: 如果不存在该键则返回 False，否则返回 True
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
		设置插件路径
		@type				path : str
		@param				path : 插件所在路径
		@return					 : None
		"""
		if path in self.__cg_plugins :
			self.__pluginMgr = self.__cg_plugins[path]
		else :
			self.__pluginMgr = PluginMgr( path )
			self.__cg_plugins[path] = self.__pluginMgr

	def clear( self ) :
		"""
		清除文本
		@return					: None
		"""
		self.__text = ""
		self.__tmpInner.top = 0								# 行顶距设置为 0
		self.__tmpInner.width = 0							# 行宽设置为 0
		self.__tmpInner.height = 0							# 行高度设置为 0
		self.__tmpInner.space = self.maxWidth				# 设置为最大宽度
		self.__tmpInner.align = self.__align				# 恢复临时对齐方式
		self.__tmpInner.lineFlat = self.__lineFlat			# 恢复临时对齐方式
		self.__tmpInner.elems = []							# 清空行元素
		self.__tmpsForPL = {}								# 删除插件临时变量

		self.__tmpWidthAdapt = self.__widthAdapt			# 恢复宽度自适应标记
		self.__tmpCurrWidth = 0.0							# 清除最大宽度行的宽度
		self.__tmpCRElems = {}								# 清除中间对齐和右对齐的行信息

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
		当父亲宽度改变时被调用
		"""
		Control.onParentWidthChanged_( self, oldWidth, newWidth )
		if  self.h_dockStyle == "HFILL" :
			self.maxWidth += ( newWidth - oldWidth )

	# -------------------------------------------------
	def onComponentLClick_( self, pyComponent ) :
		"""
		当某个链接标签被鼠标左键单击时调用
		"""
		self.onComponentLClick( pyComponent )
		if not pyComponent.isMouseHit() :
			rds.ccursor.normal()
			self.onComponentMouseLeave( pyComponent )
		#INFO_MSG( "a component in RichText had been clicked by left mouse: ", pyComponent.linkMark )

	def onComponentRClick_( self, pyComponent ) :
		"""
		当某个链接标签被鼠标右键单击时调用
		"""
		self.onComponentRClick( pyComponent )
		if not pyComponent.isMouseHit() :
			rds.ccursor.normal()
		#INFO_MSG( "a component in RichText had been clicked by right mouse: ", pyComponent.linkMark )

	def onComponentMouseEnter_( self, pyComponent ) :
		"""
		当鼠标进入某个链接标签时被调用
		"""
		self.onComponentMouseEnter( pyComponent )
		#INFO_MSG( "mouse enter a component in RichText: ", pyComponent.linkMark )

	def onComponentMouseLeave_( self, pyComponent ) :
		"""
		当鼠标离开某个链接标签时被调用
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
		self.__text += text											# 设置新文本
		lineInfos = self.__pluginMgr.parse( self, text )			# 再使用插件解释文本
		for esc, info in lineInfos :								# 遍历文本信息，粘贴文本
			self.__pluginMgr[esc].transform( self, info )			# 使用插件粘贴文本元素
		self.paintCurrLine__()										# 粘贴最后一行
		self.__realignElems()										# 重排中间对齐和右对齐的元素
		self.__tmpsForPL = {}										# 删除插件临时变量
		del self.tmpOuter__
		self.onTextChanged()										# 触发文本改变事件

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
	align = property( _getAlign, _setAlign )					# chr: 获取/设置对齐属性( 'L'为左对齐, 'C'为中间对齐, 'R'为右对齐)
	lineFlat = property( _getLineFlat, _setLineFlat )			# chr: 获取/设置文本高度的对齐方式，如果前后两行文本高度不一样，是采用
																#	   顶部对齐（'T'）还是中间对齐（'M'），还是底部对齐（'B'）
	autoNewline = property( _getAutoNewline, _setAutoNewline )	# bool: 是否自动换行
	widthAdapt = property( _getWidthAdapt, _setWidthAdapt )		# bool: 对于靠左、靠右的设置是否自动按自动适应的宽度作为对齐宽度( 只有 autoNewline 为 False 时才起作用)
	text = property( _getText, _setText )						# str: 获取/设置源文本
	viewText = property( _getViewText ) 						# str: 获取可见到的文本
	font = property( _getFont, _setFont )						# str: 获取/设置默认字体
	fontSize = property( _getFontSize, _setFontSize )			# int: 获取/设置字体大小
	charSpace = property( _getCharSpace, _setCharSpace )		# float: 获取/设置字间距
	spacing = property( _getSpacing, _setSpacing )				# float: 获取/设置行间距
	foreColor = property( _getForeColor, _setForeColor )		# tuple/Vector4/Vector3: 获取/设置默认前景颜色
	backColor = property( _getBackColor, _setBackColor )		# tuple/Vector4/Vector3: 获取/设置默认背景颜色
	limning = property( _getLimning, _setLimning )				# MACRO DEFINATION: 获取/设置描边效果：Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( _getLimnColor, _setLimnColor )		# tuple: 获取/设置描边颜色

	lineCount = property( _getLineCount )						# int: 获取文本总行数
	lineHeight = property( _getLineHeight )						# float: 获取默认行高度

	maxWidth = property( _getMaxWidth, _setMaxWidth )			# float: 获取/设置 RichText 的最大宽度（超出该宽度，则自动换行），如果为负数，则表示不自动换行
	width = property( Control._getWidth, _setWidth )			# float: 获取 RichText 的实际宽度
	height = property( _getHeight, _setHeight )					# float: 获取 RichText 的高度


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
		@param			path : 插件所在路径
		"""
		self.__plugins = {}
		self.__plugins[""] = CommonPlugin( self )			# 默认不进行转义的插件
		self.__splitPattern = re.compile( "''" )			# 格式化拦截模板
		if path != "" :
			self.__intPlugins( path )						# 初始化所有插件

		self.__ptnNewline = re.compile( "(\r\n|\n)|(\r)" )	# 换行符模板

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
		创建一个插件
		"""
		def getPluginClasses( memberNames ) :											# 过滤调不是继承于 BasePlugin 的类
			classes = []
			for memberName in memberNames :
				member = getattr( module, memberName )
				if not inspect.isclass( member ) : continue
				if not issubclass( member, BasePlugin ) : continue
				if inspect.getmodule( member ) == module :
					classes.append( member )
			return classes

		plugins = {}
		pluginClasses = getPluginClasses( dir( module ) )								# 获取插件类
		for PluginClass in pluginClasses :
			plugin = PluginClass( self )												# 生成插件实例
			if plugin.esc == "" :														# 插件必须包含转义字符
				ERROR_MSG( "plugin's ESC mustn't be empty!" % module )
			else :
				plugins[plugin.esc] = plugin											# 返回插件及插件的转义字符
		return plugins

	def __intPlugins( self, path ) :
		"""
		初始化所有插件
		"""
		plmodules = SmartImport.importAll( path, "PL_*" )								# 获取所有插件模块名( 调试状态下 )
		strPatterns = []
		reKeysPattern = re.compile( r"\.|\"|\^|\$|\*|\+|\?|\{|\[|\]|\\|\||\(|\)" )		# 正则表达式关键字
		for module in plmodules :
			pluginInfos = self.__createPlugin( module )
			for esc, plugin in pluginInfos.iteritems() :
				if self.has_key( esc ) :
					WARNING_MSG( "ESC has been used by %s!" % str( self[esc] ) )
				else :
					self.__plugins[esc] = plugin
					strPatterns.append( re.escape( esc ) )								# 则在其前面加上反斜杠表示转义
		if len( strPatterns ) > 0 :
			self.__splitPattern = re.compile( "|".join( strPatterns ) )					# 编译所有插件的匹配模式

	# -------------------------------------------------
	def __addFormatInfo( self, pyRichText, lineInfos, esc, text ) :
		"""
		根据转义字符和其囊括的文本获取格式化信息
		"""
		if esc == "" and text == "" : return []
		attrsInfo, leaveText = self[esc].format( pyRichText, text )			# 调用相关插件解释
		if attrsInfo is not None :											# 如果解释成功
			lineInfos.append( ( esc, attrsInfo ) )
		if leaveText != "" :
			if len( lineInfos ) and lineInfos[-1][0] == "" :				# 如果原最后一行也是默认格式
				leaveText = lineInfos.pop()[1] + leaveText					# 则追加文本
			lineInfos.append( ( "", leaveText ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def parse( self, pyRichText, text ) :
		"""
		根据所有插件解释一段文本
		@type				pyRichText : RichText
		@param				pyRichText : 发出命令的 RichText 控件
		@type				text	 : str
		@param				text	 : 要解释的文本
		@rtype						 : list
		@return						 : 转义后的文本列表 [ ( 转义字符, 解释格式化后的属性信息( 不同的转义字符有不同的类型，可以由插件自定义 ) )]
		"""
		text = self.__ptnNewline.sub( lambda e : "@B" if e.groups()[0] else "", text )
		lineInfos = []															# 所有转义信息
		currEsc = ""															# 当前解释到的转义字符(默认使用基类插件转义字符)
		currStart = 0															# 当前解释到的转义字符的起始位置

		def getEscInfo( i ) :
			try :
				match = i.next()
				esc = match.group( 0 )											# 转义字符
				start = match.start()											# 转义字符起始位置
				end = match.end()												# 转义字符结束位置
				return esc, start, end
			except StopIteration, e :
				count = len( text )
				return "", count, count											# 返回默认的插件转义信息

		wtext = csstring.toWideString( text )
		iter = self.__splitPattern.finditer( wtext )							# 搜索转义字符
		while True :															# 逐个获取转义字符信息
			esc, start, end = getEscInfo( iter )								# 获取转义信息：转义字符的起始、结束位置，以及转义字符
			includedText = wtext[currStart : start]								# 当前格式化囊括的字符
			includedText = csstring.toString( includedText )
			self.__addFormatInfo( pyRichText, lineInfos, currEsc, includedText )# 追加格式化信息行
			if start == end : break												# 解释完毕
			currEsc = esc
			currStart = end
		return lineInfos


# --------------------------------------------------------------------
# implement plugin base class for richtex text
# --------------------------------------------------------------------
class BasePlugin :
	"""
	插件基类，所有插件都必须继承该类
	"""
	esc_ = None															# 插件对应的转义字符（必须设置该字符，否则插件无效）

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
		本插件的转义字符
		"""
		return getattr( self.__class__, "esc_" )

	@property
	def owner( self ) :
		"""
		所属的插件工厂
		"""
		if self.__owner is None :
			return None
		self.__owner()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def format( self, pyRichText, text ) :
		"""
		根据传入的未格式化字符串，格式化成本插件自定义的属性信息
		注意：所有插件必须重写该方法，从而返回各自想要的格式化属性信息
		@type				pyRichText : RichText
		@param				pyRichText : 发出要求解释命令的 RichText 控件
		@type				text	 : str
		@param				text	 : 本格式化标记所囊括的串，即本格式化标记到下一个格式化标记之间的文本
		@rtype					 	 : tuple / None
		@return					 	 : 如果格式化失败，则返回: ( None, 囊括的文本 )
									   这样，相关的这段文本都没有格式化，而原样按普通文本显示
									   返回值：（①，②）
									   ① 成功则为本插件的格式化信息，类型可以自己定义，下面的 transform 第二个参数将是这个值；失败则为 None
									   ② 提取格式化信息后，剩余的文本，如果本插件没有用到格式化后的这些文本，
										  则原样返回，给默认插件来按普通文本处理。
										  当然，如果需要的话也可以截取这些文本，作为本插件自己某个属性的文本。
		"""
		return None, text

	# -------------------------------------------------
	def transform( self, pyRichText, attrInfo ) :
		"""
		将 format 解释出来的结果，转化为 RichText 可用的 component，并根据 RichText 提供的 API 添加 component 和设置一些属性:
		@type				pyRichText : controls.RichText
		@param				pyRichText : 所属的 RichText 控件
		@type				attrInfo : all types
		@param				attrInfo : 该参数值有插件自己定义，它与本插件 format 方法返回的 tuple 的第一个元素一致

		方法：
		getCurrLineWidth__()		: 获取当前准备粘贴行的宽度
		getCurrLineHeight__()		: 获取当前准备粘贴行的高度（以最高那个 python 元素的高度作为行高度）
		getCurrLineSpace__()		: 获取当前准备粘贴行的剩余宽度（可根据这个宽度来折断一行），如果返回值小于 0，则表示不自动换行
		isNewLine__()				: 获取当前准备粘贴行是否是刚刚新起一行
		setTmpAlign__( align )		: 设置临时的文本对齐方式
		addElement__( pyElem )		: 调用该方法添加一个 python 元素
		paintCurrLine__()			: 当行满时，调用该接口粘贴当前行元素
		newLine__( n = 1 )			: 换行，通过手动调用该函数重起一行或多行（通过 n 指定要换的行数，n 必须大于等于 1）
		属性：
		tmpOut__['font']			: 解释到当前时的临时字体( 可修改值 )
		tmpOut__['fcolor']			: 解释到当前时的临时前景色( 可修改值 )
		tmpOut__['bcolor']			: 解释到当前时的临时背景色( 可修改值 )

		注：① 所有插件必须重写并覆盖该方法来设置自己的 python ui 元素
			② 不能在该方法中调用 RichText 任何非“友元”方法（即除上面给出的方法以外的方法）
			③ 不能在该方法中设置 RichText 的任何属性值（可以获取）
		"""
		pass


	# ----------------------------------------------------------------
	@staticmethod
	def getSource() :
		"""
		获取格式化文本
		"""
		return ""


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onCleared( self, pyRichText ) :
		"""
		当文本清空时被调用
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
			pyLine.foreColor = tmpOuter.fcolor							# 当前前景色
			pyLine.backColor = tmpOuter.bcolor							# 当前背景色
			pyLine.charSpace = tmpOuter.charSpace						# 字间距
			pyLine.limning = tmpOuter.limning							# 描边状态
			pyLine.limnColor = tmpOuter.limnColor						# 描边颜色
			pyLine.setFontInfo( {
				"font"		: tmpOuter.font,							# 字体
				"size"		: tmpOuter.fontSize,						# 字体大小
				"bold"		: tmpOuter.bold,							# 是否为粗体
				"italic"	: tmpOuter.italic,							# 是否斜体
				"underline" : tmpOuter.underline,						# 是否有下划线
				"strikeOut" : tmpOuter.strikeOut,						# 是否有删除线
				} )
			return pyLine

		while True :													# 判断是否有折断文本
			pyLine = createLine()										# 创建一个文本行 UI
			ltext, rtext = text, ""										# 默认总不换行
			if pyRichText.autoNewline :									# 如果需要自动换行
				space = pyRichText.getCurrLineSpace__()					# 当前行剩余宽度
				ltext, rtext, lwtext, rwtext = \
					pyLine.splitText( space, "CUT", text )				# 拆分字符串
				if len( rwtext ) :
					fchr = csstring.toString( rwtext[0] )
					if fchr in g_interpunctions :						# 不折断标点符号
						ltext += fchr
						rtext = csstring.toString( rwtext[1:] )
			if rtext == "" :											# 如果剩余的空间可以放下所有文本
				pyLine.text = ltext										# 将所有文本
				pyRichText.addElement__( pyLine )						# 放到当前行中
				break													# 完成所有文本的粘贴，并跳出
			elif ltext == "" and not pyRichText.isNewLine__() :			# 如果剩余的宽度不足以放下一个文字
				pyRichText.paintCurrLine__()							# 粘贴当前行，并另起一行
			elif ltext == "" :											# 如果最大宽度太小，连一个字也放不下
				wtext = csstring.toWideString( text )					# 首先将字符串，转换为宽字符串
				pyLine.text = csstring.toString( wtext[0] )				# 则只放第一个字
				pyRichText.addElement__( pyLine )						# 添加到当前行
				pyRichText.paintCurrLine__()							# 粘贴当前行
				text =  wtext[1:]										# 将文本中的第一个字符去掉，剩余的作为下一个循环的 text
			else :														# 如果文本被折断成两部分
				pyLine.text = ltext										# 先获取前半部分
				pyRichText.addElement__( pyLine )						# 将折前半部分文本放到当前行
				pyRichText.paintCurrLine__()							# 粘贴当前行
				text = rtext											# 将剩余的右半部分作为下一个循环的 text

	# ----------------------------------------------------------------
	@staticmethod
	def getSource() :
		"""
		获取格式化文本
		"""
		return ""
