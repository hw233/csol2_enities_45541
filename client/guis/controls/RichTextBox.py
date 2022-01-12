# -*- coding: gb18030 -*-
#

"""
implement richtext box class。

2009.12.17: writen by huangyongwei
"""


import re
import weakref
import Font
import csstring
from guis import *
from csstring import KeyCharParser
from guis.common.PyGUI import PyGUI
from guis.controls.ScrollPanel import VScrollPanel
from guis.controls.BaseInput import BaseInput
from guis.controls.StaticText import StaticText

"""
composing :
	GUI.Window
"""

class RichTextBox( BaseInput ) :
	cc_end_skip_width = 40

	def __init__( self, panel, pyBinder = None ) :
		BaseInput.__init__( self, panel, pyBinder )
		self.focus = True
		self.moveFocus = True

		self.__escTPLs = []							# 转义模板
		self.pyElems_ = []							# 所有文本元素
		self.__wtext = csstring.toWideString( "" )	# 文本的宽字符形式
		self.__readOnly = False						# 是否是只读
		self.__curSiteInfo = SiteInfo( 0, 0 )		# 光标位置

		self.__font = Font.defFont					# 默认字体
		self.__fontSize = Font.defFontSize			# 默认字体大小
		self.__charSpace = Font.defCharSpace		# 字间距
		self.__limning = Font.defLimning			# 描边样式
		self.__limnColor = Font.defLimnColor		# 描边颜色

		self.__foreColor = ( 255, 255, 255, 255 )	# 默认颜色
		self.__vTextAlgin = "BOTTOM"				# 垂直方向上文本的对齐方式："TOP" / "MIDDLE" / "BOTTOM"
		self.__viewLen = 0							# 可视文本字节数
		self.__wviewLen = 0							# 可视文本字数
		self.__maxLen = -1							# 允许输入的最大字符数，0 表示可输入任意长( 注意：这是表现文本的长度 )
		self.__initialize( panel )

	def __del__( self ) :
		BaseInput.__del__( self )
		if Debug.output_del_RichTextBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		BaseInput.generateEvents_( self )
		self.__onTextChanged = self.createEvent_( "onTextChanged" )

	# -------------------------------------------------
	@property
	def onTextChanged( self ) :
		"""
		当文本改变时被触发
		"""
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		"""
		初始化
		"""
		self.__selector = Selector( self.__fontSize )
		pyFirst = EFirst()
		pyLast = ELast()
		self.__linkBorderElems( pyFirst, pyLast )
		self.pyElems_ = [pyFirst, pyLast]

	def __clearText( self ) :
		"""
		清除所有文本
		"""
		pyElems = self.pyElems_
		pyFirst = pyElems.pop( 0 )
		pyLast = pyElems.pop()
		pyLast.setScopeSite_( 0 )
		self.pyElems_ = [pyFirst, pyLast]
		self.__linkBorderElems( pyFirst, pyLast )

		for pyElem in pyElems :
			self.delPyChild( pyElem )

		self.__viewLen = 0
		self.__wviewLen = 0

	# -------------------------------------------------
	@staticmethod
	def __linkBorderElems( pyFore, pyNext ) :
		"""
		连接两个相邻的元素
		"""
		pyFore.setNextElem_( pyNext )
		pyNext.setForeElem_( pyFore )

	def __resizeCursor( self ) :
		"""
		重新设置光标大小
		"""
		fontHeight = self.__fontSize
		self.pyCursor_.height = fontHeight
		if self.__vTextAlgin == "TOP" :
			self.pyCursor_.top = 0
		elif self.__vTextAlgin == "MIDDLE" :
			self.pyCursor_.middle = self.height * 0.5
		else :
			self.pyCursor_.bottom = self.height

	# -------------------------------------------------
	def __getTextScopes( self, wtext ) :
		"""
		获取所有转义区域
		"""
		scopes = {}
		def wellhandled( start ) :							# 是否被转义处理过
			for s, ( e, clsElem ) in scopes.iteritems() :
				if s <= start < e :
					return True
			return False

		for tpl, clsElem in self.__escTPLs :				# 找出所有转义符
			iter = tpl.finditer( wtext )
			while True :
				try :
					match = iter.next()
					start = match.start()
					if wellhandled( start ) :
						continue
					end = match.end()
					scopes[start] = ( end, clsElem )
				except StopIteration :
					break
		return scopes

	def __setTextElements( self, wtext ) :
		"""
		设置文本的所有元素
		"""
		self.__clearText()
		self.__wtext = wtext							# 保存宽文本
		scopes = self.__getTextScopes( wtext )			# 获取所有具备转义条件的区域
		starts = sorted( scopes.keys() )				# 按区域索引的起始位置，从小到大排序

		if self.__vTextAlgin == "TOP" :					# 文本顶部对齐
			aname = "top"
			y = 1
		elif self.__vTextAlgin == "MIDDLE" :			# 文本中间对齐
			aname = "middle"
			y = self.height * 0.5
		else :
			aname = "bottom"							# 文本底部对齐
			y = self.height - 1

		count = len( wtext )							# 文本字符个数
		left = 0
		index = 0
		pyFore = self.pyElems_[0]						# 临时记录前一个元素
		pyLast = self.pyElems_.pop()					# 最后一个元素
		while index < count :
			start = index
			end = count
			if len( starts ) :
				start = starts[0]
				if index == start :
					end, clsElem = scopes[start]
					starts.pop( 0 )
				else :
					end = start
					start = index
					clsElem = EDefText
			else :
				clsElem = EDefText
			index = end
			text = wtext[start:end]
			pyElem = clsElem.getInst( start, text )		# 创建元素
			if pyElem is None :							# 创建元素时解释失败
				pyElem = EDefText( start, text )		# 用纯文本显示
			self.__viewLen += pyElem.getViewLen()
			self.__wviewLen += pyElem.getWViewLen()
			pyElem.setAttributes_( self )
			self.addPyChild( pyElem )
			pyElem.left = left
			setattr( pyElem, aname, y )
			left = pyElem.right
			self.pyElems_.append( pyElem )
			pyFore.setNextElem_( pyElem )
			pyElem.setForeElem_( pyFore )
			pyFore = pyElem
		self.pyElems_.append( pyLast )
		pyLast.setScopeSite_( count )
		pyLast.left = left
		self.__linkBorderElems( pyFore, pyLast )

	# -------------------------------------------------
	def __getElemOfSite( self, site ) :
		"""
		根据位置找出其相应的元素
		"""
		if site <= 0 :
			return self.pyElems_[0]
		pyLast = self.pyElems_[-1]
		if site >= pyLast.end :
			return pyLast
		pyElems = self.pyElems_[1:-1]
		start = 0
		end = len( pyElems )
		while start < end :
			mid = ( start + end ) / 2
			pyElem = pyElems[mid]
			if site <= pyElem.start :
				end = mid
			elif site > pyElem.end :
				start = mid
			else :
				return pyElem
		return None

	def __getElemOfLeft( self, left ) :
		"""
		获取指定左距处的元素
		"""
		if left <= 0 :
			return self.pyElems_[0]
		pyLast = self.pyElems_[-1]
		if left >= pyLast.right :
			return pyLast
		pyElems = self.pyElems_[1:-1]
		start = 0
		end = len( pyElems )
		while start < end :
			mid = ( start + end ) / 2
			pyElem = pyElems[mid]
			if left < pyElem.left :
				end = mid
			elif left > pyElem.right :
				start = mid
			else :
				return pyElem
		return None

	def __getElemOfScope( self, ( start, end ) ) :
		"""
		获取某索引区域内的所有元素
		"""
		pyElems = []
		for pyElem in self.pyElems_ :
			if pyElem.end <= start :
				continue
			if pyElem.start >= end :
				break
			pyElems.append( pyElem )
		return pyElems

	# ---------------------------------------
	def __getSiteInfoViaSite( self, site ) :
		"""
		根据给出的索引，计算指定索引处的真正索引（可盛放光标的地方）和左距
		因为移动光标时，有些元素需要整块被跨越，即光标不能停留在元素的中间
		返回：SiteInfo( site, left )
		"""
		pyElem = self.__getElemOfSite( site )
		return pyElem.getSiteInfoViaSite( site )

	def __getSiteInfoViaLeft( self, left ) :
		"""
		根据给出的左距，计算指定索引处的真正索引（可盛放光标的地方）和左距
		因为移动光标时，有些元素需要整块被跨越，即光标不能停留在元素的中间
		返回：SiteInfo( site, left )
		"""
		pyElem = self.__getElemOfLeft( left )
		return pyElem.getSiteInfoViaLeft( left )

	# ---------------------------------------
	def __getEndSiteInfo( self ) :
		"""
		获取文本最后的位置信息
		"""
		pyElem = self.pyElems_[-1]
		return SiteInfo( pyElem.end, pyElem.right )

	# -------------------------------------------------
	def __setCursorSite( self, siteInfo ) :
		"""
		设置光标位置
		"""
		self.__curSiteInfo = siteInfo
		left = siteInfo.left
		self.pyCursor_.left = left

		right = self.pyCursor_.right + 1
		maxScroll = self.gui.maxScroll
		scroll = self.gui.scroll
		if right - scroll.x > self.width :		# 光标位置超出控件长度
			x = right - self.width
			maxScroll.x = x						# 把文本往前拉，使得光标停留在控件末端
			scroll.x = x
		elif left < scroll.x :					# 光标隐到了控件前方
			x = left - self.cc_end_skip_width
			maxScroll.x = x						# 把文本往后拖
			scroll.x = x


	# -------------------------------------------------
	# 移动光标
	# -------------------------------------------------
	def __moveLeftChar( self ) :
		"""
		将光标往左移一个字符
		"""
		if self.__selector.selected :
			return self.__selector.minSiteInfo
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftChar( site )

	def __moveRightChar( self ) :
		"""
		将光标往右移一个字符
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightChar( site )

	def __moveLeftWord( self ) :
		"""
		往左移动一个单词
		"""
		site = self.__curSiteInfo.site
		if self.__selector.selected :
			site = self.__selector.minSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftWord( site )

	def __moveRightWord( self ) :
		"""
		往右移动一个单词
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightWord( site )

	def __moveLeftAll( self ) :
		"""
		将光标移到最始端
		"""
		return SiteInfo( 0, 0 )

	def __moveRightAll( self ) :
		"""
		将光标移动到最末端
		"""
		return self.__getEndSiteInfo()

	# ---------------------------------------
	def __moveCursor( self, key, mods ) :
		"""
		通过键盘键盘移动光标
		"""
		handlers = {
			( KEY_LEFTARROW, 0 )				: self.__moveLeftChar,		# 光标前移一个字符
			( KEY_RIGHTARROW, 0 )				: self.__moveRightChar,		# 光标后以一个字符
			( KEY_LEFTARROW, MODIFIER_CTRL )	: self.__moveLeftWord,		# 光标前移一个单词
			( KEY_RIGHTARROW, MODIFIER_CTRL )	: self.__moveRightWord,		# 光标后移一个单词
			( KEY_HOME, 0 )						: self.__moveLeftAll,		# 光标移到最前面
			( KEY_END, 0 )						: self.__moveRightAll,		# 光标移到最后面
			}
		if ( key, mods ) in handlers :
			self.cancelSelect()
			siteInfo = handlers[( key, mods )]()
			self.__setCursorSite( siteInfo )
			return True
		return False


	# -------------------------------------------------
	# 删除文本
	# -------------------------------------------------
	def __delLeftChar( self ) :
		"""
		删除光标左边一个字符
		"""
		endInfo = self.__curSiteInfo
		endSite = endInfo.site
		pyElem = self.__getElemOfSite( endSite )
		startInfo = pyElem.skipLeftChar( endSite )
		return startInfo, endInfo

	def __delRightChar( self ) :
		"""
		删除光标右边一个字符
		"""
		startInfo = self.__curSiteInfo
		startSite = startInfo.site
		pyElem = self.__getElemOfSite( startSite )
		endInfo = pyElem.skipRightChar( startSite )
		return startInfo, endInfo

	def __delLeftWord( self ) :
		"""
		删除光标左边一个单词
		"""
		endInfo = self.__curSiteInfo
		endSite = endInfo.site
		pyElem = self.__getElemOfSite( endSite )
		startInfo = pyElem.skipLeftWord( endSite )
		return startInfo, endInfo

	def __delRightWord( self ) :
		"""
		删除光标右边一个单词
		"""
		startInfo = self.__curSiteInfo
		startSite = startInfo.site
		pyElem = self.__getElemOfSite( startSite )
		endInfo = pyElem.skipRightWord( startSite )
		return startInfo, endInfo

	# ---------------------------------------
	def __delScopeText( self, startInfo, endInfo ) :
		"""
		删除指定区域内的文本
		"""
		start = startInfo.site
		end = endInfo.site
		wtext = self.__wtext
		self.__setTextElements( wtext[:start] + wtext[end:] )
		self.__setCursorSite( startInfo )

	def __delSubStr( self, key, mods ) :
		"""
		通过键盘删除一个子串
		"""
		if self.__readOnly :
			return False

		handlers = {
			( KEY_BACKSPACE, 0 )			: self.__delLeftChar,		# 删除光标前一个字符
			( KEY_DELETE, 0 )				: self.__delRightChar,		# 删除光标后一个字符
			( KEY_BACKSPACE, MODIFIER_CTRL ): self.__delLeftWord,		# 删除光标左边的一个单词
			( KEY_DELETE, MODIFIER_CTRL )	: self.__delRightWord,		# 删除光标右边的一个单词
			}

		if ( key, mods ) not in handlers :
			return False
		elif self.__selector.selected :
			startInfo = self.__selector.minSiteInfo
			endInfo = self.__selector.maxSiteInfo
			self.cancelSelect()
		else :
			startInfo, endInfo = handlers[( key, mods )]()
		self.__delScopeText( startInfo, endInfo )
		self.onTextChanged_()
		return True

	# -------------------------------------------------
	# 插入文本
	# -------------------------------------------------
	def __getSelectWViewLen( self ) :
		"""
		获取选中文本的可视长度
		"""
		if not self.__selector.selected :
			return 0

		startInfo = self.__selector.minSiteInfo
		endInfo = self.__selector.maxSiteInfo
		start = startInfo.site
		end = endInfo.site
		pyElem = self.__getElemOfSite( start )
		count = 0
		while pyElem and pyElem.start < end :
			count += len( pyElem.getWViewText( ( start, end ) ) )
			pyElem = pyElem.pyNext
		return count

	def __insertText( self, text, count = 0 ) :
		"""
		在光标处插入文本
		"""
		addedWText = csstring.toWideString( text )
		if len( addedWText ) == 0 :
			return

		maxLen = self.__maxLen
		addCount = len( addedWText )

		if self.__selector.selected :
			startInfo = self.__selector.minSiteInfo
			endInfo = self.__selector.maxSiteInfo
		else :
			startInfo = endInfo = self.__curSiteInfo
		start = startInfo.site
		end = endInfo.site
		if maxLen > 0 :												# 有文本长度限制
			currCount = self.wviewLength							# 当前文本长度
			selCount = self.__getSelectWViewLen()					# 选中文本长度
			leaveCount = max( 0, maxLen - currCount + selCount )	# 还可以输入多少个字
			if count > 0 :
				if count > leaveCount :								# 添加的文本超出了最大长度限制
					return
			elif addCount > leaveCount :
				addedWText = addedWText[:leaveCount]				# 截取部分文字输入
				addCount = leaveCount
		wtext = self.__wtext
		newWText = wtext[:start] + addedWText + wtext[end:]			# 新输入的文本
		self.__setTextElements( newWText )
		siteInfo = self.__getSiteInfoViaSite( start + addCount )
		self.__setCursorSite( siteInfo )
		self.cancelSelect()
		self.onTextChanged_()

	# ---------------------------------------
	def __input( self, key, mods ) :
		"""
		通过键盘输入一个字符
		"""
		if mods == MODIFIER_CTRL :
			return False

		if self.readOnly :
			return True
		ch = KeyCharParser.keyToChar( key, mods == MODIFIER_SHIFT )
		if ch != '' :
			self.__insertText( ch )
			return True
		return False

	# -------------------------------------------------
	# 选中文本
	# -------------------------------------------------
	def __selectLeftChar( self ) :
		"""
		选中光标前一个字符
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftChar( site )

	def __selectRightChar( self ) :
		"""
		选中光标后一个字符
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightChar( site )

	def __selectLeftWord( self ) :
		"""
		选中光标前一个单词
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftWord( site )

	def __selectRightWord( self ) :
		"""
		选中光标后一个单词
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightWord( site )

	def  __selectLeftAll( self ) :
		"""
		选中光标前的所有文本
		"""
		return SiteInfo( 0, 0 )

	def __selectRightAll( self ) :
		"""
		选中光标后的所有文本
		"""
		return self.__getEndSiteInfo()

	# ---------------------------------------
	def __keySelectText( self, key, mods ) :
		"""
		键盘按键选中文本
		"""
		if key == KEY_A and mods == MODIFIER_CTRL :
			self.selectAll()
			return True

		handlers = {
			( KEY_LEFTARROW, MODIFIER_SHIFT )					: self.__selectLeftChar,		# 选中光标前一个字符
			( KEY_RIGHTARROW, MODIFIER_SHIFT )					: self.__selectRightChar,		# 选中光标后一个字符
			( KEY_LEFTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectLeftWord,		# 选中光标前一个单词
			( KEY_RIGHTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectRightWord,		# 选中光标后一个单词
			( KEY_HOME, MODIFIER_SHIFT )						: self.__selectLeftAll,			# 选中光标前的所有文本
			( KEY_END, MODIFIER_SHIFT )							: self.__selectRightAll,		# 选中光标后的所有文本
			}
		if ( key, mods ) in handlers :
			startInfo = self.__curSiteInfo
			if self.__selector.selected :
				startInfo = self.__selector.startSiteInfo
			endInfo = handlers[( key, mods )]()
			self.__setCursorSite( endInfo )
			self.__selector.select( self, startInfo, endInfo )
		return False

	# -------------------------------------------------
	# 编辑文本
	# -------------------------------------------------
	def __copy( self ) :
		"""
		复制文本
		"""
		text = self.selectText
		if len( text ) > 0 :
			csol.setClipboard( text )

	def __cut( self ) :
		"""
		剪切文本
		"""
		if self.__readOnly : return
		if self.__selector.selected :
			startInfo = self.__selector.minSiteInfo
			endInfo = self.__selector.maxSiteInfo
			start, end = startInfo.site, endInfo.site
			csol.setClipboard( self.selectText )
			self.__delScopeText( startInfo, endInfo )
			self.cancelSelect()
			self.onTextChanged_()

	def __paste( self ) :
		"""
		粘贴文本
		"""
		if self.__readOnly : return
		text = csol.getClipboard()
		if text == "" : return
		self.__insertText( text )

	# ---------------------------------------
	def __keyEditText( self, key, mods ) :
		"""
		按键编辑文本
		"""
		handlers = {
			( KEY_C, MODIFIER_CTRL )	: self.__copy,		# 复制
			( KEY_X, MODIFIER_CTRL )	: self.__cut,		# 剪切
			( KEY_V, MODIFIER_CTRL )	: self.__paste,		# 粘贴
			}
		if ( key, mods ) in handlers :
			handlers[( key, mods )]()
			return True
		return False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabIn_( self ) :
		"""
		获得焦点时被调用
		"""
		self.showCursor_()
		BaseInput.onTabIn_( self )
		self.__resizeCursor()
		self.__setCursorSite( self.__curSiteInfo )

	def onLMouseDown_( self, mods ) :
		"""
		鼠标左键按下时被调用
		"""
		BaseInput.onLMouseDown_( self, mods )
		if not self.tabStop :
			self.tabStop = True
		left = self.mousePos[0]								# 鼠标位置
		left += self.gui.scroll.x
		siteInfo = self.__getSiteInfoViaLeft( left )		# 计算光标所在位置和左距
		self.__setCursorSite( siteInfo )					# 设置鼠标的实际位置
		self.__selector.beginSelecting( siteInfo )			# 开始选择文本
		rds.uiHandlerMgr.capUI( self )						# 准备选择文本
		return True

	def onLMouseUp_( self, mods ) :
		"""
		鼠标左键提起时被调用
		"""
		self.__selector.endSelecting()
		rds.uiHandlerMgr.uncapUI( self )
		BaseInput.onLMouseUp_( self, mods )
		return True

	def onMouseMove_( self, dx, dy ) :
		"""
		鼠标移动时被调用
		"""
		if self.__selector.selecting :
			startInfo = self.__selector.startSiteInfo
			left = self.mousePos[0]
			left += self.gui.scroll.x							# 鼠标之前的位置
			endInfo = self.__getSiteInfoViaLeft( left )
			self.__setCursorSite( endInfo )						# 设置鼠标的新位置
			self.__selector.select( self, startInfo, endInfo )
			BaseInput.onMouseMove_( self, dx, dy )
			return True
		return BaseInput.onMouseMove_( self, dx, dy )

	def onKeyDown_( self, key, mods ) :
		"""
		键盘按键按下时被调用
		"""
		if key == KEY_ESCAPE and self.__selector.selected :
			self.cancelSelect()
			return True
		return BaseInput.onKeyDown_( self, key, mods )

	# ---------------------------------------
	def onTextChanged_( self ) :
		"""
		文本改变是被调用
		"""
		self.onTextChanged()

	# -------------------------------------------------
	def keyInput_( self, key, mods ) :
		"""
		接收按键输入
		"""
		if self.__moveCursor( key, mods ) :			# 作移动光标处理
			return True
		if self.__delSubStr( key, mods ) :			# 作删除字符处理
			return True
		if self.__keySelectText( key, mods ) :		# 按键选中文本
			return True
		if self.__keyEditText( key, mods ) :		# 编辑文本
			return True
		if mods == 0 or mods == MODIFIER_SHIFT :
			if self.__input( key, mods ) :			# 输入字符
				return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setEscTemplates( self, tpls ) :
		"""
		设置转义模板
		@type				tpl		: re._sre.SRE_Pattern
		@param				tpl		: 转义模板
		@type				clsElem : class
		@param				clsElem : BaseElement
		"""
		self.__escTPLs = tpls
		self._setText( self.__wtext )

	def clearTemplates( self ) :
		"""
		清除所有模板
		"""
		self.__escTPLs = []
		self._setText( self.__wtext )

	# -------------------------------------------------
	def notifyInput( self, text, count = 0 ) :
		"""
		在光标处输入
		count 表示 text 受信任的可视长度，如果为 0 则表示使用
		text 的实际长度来确定文本长度是否超出 __maxLen 设置
		"""
		if text == "" : return
		if self.__readOnly : return
		self.__insertText( text, count )

	def clear( self ) :
		"""
		清除所有文本
		"""
		self.__clearText()
		self.__wtext = csstring.toWideString( "" )
		self.__curSiteInfo = SiteInfo( 0, 0 )
		self.cancelSelect()
		if self.tabStop :
			self.pyCursor_.left = 0
		self.gui.maxScroll.x = 0
		self.gui.scroll.x = 0
		self.onTextChanged_()

	# -------------------------------------------------
	def select( self, start, end ) :
		"""
		选中文本
		"""
		startInfo = self.__getSiteInfoViaSite( start )
		endInfo = self.__getSiteInfoViaSite( end )
		self.__selector.select( self, startInfo, endInfo )

	def selectAll( self ) :
		"""
		选中全部文本
		"""
		self.select( 0, self.wlength )

	def cancelSelect( self ) :
		"""
		取消选择
		"""
		self.__selector.cancelSelect()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setText( self, text ) :
		wtext = csstring.toWideString( text )
		self.__setTextElements( wtext )
		self.__curSiteInfo = self.__getEndSiteInfo()
		if self.tabStop :
			self.__setCursorSite( self.__curSiteInfo )

	def _getWViewText( self ) :
		wtext = csstring.toWideString( "" )
		for pyElem in self.pyElems_ :
			wtext += pyElem.getWViewText()
		return wtext

	def _getWSelectText( self ) :
		wtext = csstring.toWideString( "" )
		if self.__selector.selected :
			startInfo = self.__selector.minSiteInfo
			endInfo = self.__selector.maxSiteInfo
			scope = startInfo.site, endInfo.site
			pyElems = self.__getElemOfScope( scope )
			for pyElem in pyElems :
				wtext += pyElem.getWViewText( scope )
			return wtext
		return wtext

	# ---------------------------------------
	def _setMaxLen( self, length ) :
		self.__maxLen = length

	# ---------------------------------------
	def _setReadOnly( self, readOnly ) :
		self.__readOnly = readOnly

	def _setFont( self, font ) :
		self.__font = font
		self.__setTextElements( self.__wtext )
		if self.tabStop :
			self.__resizeCursor()
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.cancelSelect()

	def _setFontSize( self, size ) :
		if self.__font.endswith( ".font" ) :
			return
		self.__fontSize = size
		self.__setTextElements( self.__wtext )
		if self.tabStop :
			self.__resizeCursor()
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.cancelSelect()
		self.__selector.setLineHeight_( size )

	def _setCharSpace( self, space ) :
		self.__charSpace = space
		self.__setTextElements( self.__wtext )
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.cancelSelect()

	# -------------------------------------------------
	def _getLimning( self ) :
		return self.__limning

	def _setLimning( self, style ) :
		if isDebuged :
			assert style in ( Font.LIMN_NONE, Font.LIMN_OUT, Font.LIMN_SHD ), \
				"limning style must be: Font.LIMN_NONE or Font.LIMN_OUT or Font.LIMN_SHD"
		self.__limning = style
		self.__setTextElements( self.__wtext )

	def _getLimnColor( self ) :
		return self.__limnColor

	def _setLimnColor( self, color ) :
		self.__limnColor = color
		self.__setTextElements( self.__wtext )

	# -------------------------------------------------
	def _setForeColor( self, color ) :
		self.__foreColor = color
		for pyElem in self.pyElems_ :
			pyElem.color = color

	# -------------------------------------------------
	def _setVTextAlign( self, align ) :
		if isDebuged :
			assert align in set( ["TOP", "MIDDLE", "BOTTOM"] ), "align must be one of 'TOP'/'MIDDLE'/'BOTTOM'"
		self.__vTextAlgin = align
		self._setText( self.__wtext )
		if self.tabStop :
			self.__resizeCursor()
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.cancelSelect()

	# ----------------------------------------------------------------
	# privaties
	# ----------------------------------------------------------------
	text = property( lambda self : csstring.toString( self.__wtext ), _setText )		# 获取/设置原始文本
	wtext = property( lambda self : self.__wtext )										# 获取原始文本的宽文本形式
	viewText = property( lambda self : csstring.toString( self._getWViewText() ) )		# 获取可视文本
	wviewText = property( _getWViewText )												# 获取可视文本的宽文本形式
	selectText = property( lambda self : csstring.toString( self._getWSelectText() ) )	# 获取选中文本
	wselectText = property( _getWSelectText )											# 获取选中文本的宽字符形式
	length = property( lambda self : len( self.text ) )									# 获取文本包含字符数
	wlength = property( lambda self : len( self.__wtext ) )								# 获取文本包含的字数
	viewLength = property( lambda self : self.__viewLen )								# 获取可视文本的字符数
	wviewLength = property( lambda self : self.__wviewLen )								# 获取可视文本的字数
	maxLength = property( lambda self : self.__maxLen, _setMaxLen )						# 获取/设置最多可输入的字符数（注意：这是表现文本的字符数）
	readOnly = property( lambda self : self.__readOnly, _setReadOnly )					# 获取设置是否只读
	font = property( lambda self : self.__font, _setFont )								# 获取/设置字体
	fontSize = property( lambda self : self.__fontSize, _setFontSize )					# 获取字体高度
	charSpace = property( lambda self : self.__charSpace, _setCharSpace )				# 获取/设置字间距
	limning = property( lambda self : self.__limning, _setLimning )						# 获取/设置描边样式
	limnColor = property( lambda self : self.__limnColor, _setLimnColor )				# 获取/设置描边颜色
	foreColor = property( lambda self : self.__foreColor, _setForeColor )				# 获取/设置前景色
	vTextAlign = property( lambda self : self.__vTextAlgin, _setVTextAlign )			# 获取/设置垂直方向上文本的对齐方式
	textWidth = property( lambda self : self.pyElems_[-1].right )						# 获取所有文本长度



# --------------------------------------------------------------------
# 位置信息封装
# --------------------------------------------------------------------
class SiteInfo( object ) :
	__slots__ = ( "site", "left" )
	def __init__( self, site, left ) :
		self.site = site
		self.left = left

	def __cmp__( self, siteInfo ) :
		return self.site - siteInfo.site


# --------------------------------------------------------------------
# richtextbox 元素
# --------------------------------------------------------------------
class BaseElement( object ) :
	def __init__( self, start, wtext ) :
		self.start = start
		self.end = start + len( wtext )
		self.originalText = wtext
		self.__pyFore = None
		self.__pyNext = None

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def pyFore( self ) :
		if self.__pyFore is None :
			return None
		return self.__pyFore()

	@property
	def pyNext( self ) :
		if self.__pyNext is None :
			return None
		return self.__pyNext()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setForeElem_( self, pyElem ) :
		"""
		设置前置元素
		"""
		if pyElem is None :
			self.__pyFore = None
		self.__pyFore = weakref.ref( pyElem )

	def setNextElem_( self, pyElem ) :
		"""
		设置后置元素
		"""
		if pyElem is None :
			self.__pyNext = None
		self.__pyNext = weakref.ref( pyElem )

	# -------------------------------------------------
	def setAttributes_( self, pyRich ) :
		"""
		根据所属 pyRich 的属性，设置元素属性
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def getInst( SELF, start, wtext ) :
		"""
		是否有效
		"""
		return SELF( start, wtext )

	# -------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		获取表现文本
		"""
		if scope is None :
			return self.originalText
		elif scope[0] < self.end and scope[1] > self.start :
			return self.originalText
		return csstring.toWideString( "" )

	# ---------------------------------------
	def getViewLen( self ) :
		"""
		获取可视文本的字符数
		"""
		return len( csstring.toString( self.originalText ) )

	def getWViewLen( self ) :
		"""
		获取可视文本的字数
		"""
		return len( self.originalText )

	# -------------------------------------------------
	def getSiteInfoViaSite( self, site ) :
		"""
		根据有可能处于拆分完整单元的位置获取正确位置，返回正确位置和左距
		"""
		start = self.start
		end = self.end
		center = ( start + end ) / 2
		if site <= center :
			return SiteInfo( start, self.left )
		return SiteInfo( end, self.right )

	def getSiteInfoViaLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		myLeft = self.left
		myRight = self.right
		center = ( myLeft + myRight ) * 0.5
		if left < center :
			return SiteInfo( self.start, myLeft )
		return SiteInfo( self.end, myRight )

	# ---------------------------------------
	def skipLeftChar( self, site ) :
		"""
		获取指定位置下，左边找一个字符所囊括的区域
		"""
		if site <= self.start :
			return self.pyFore.skipLeftChar( site )
		return SiteInfo( self.start, self.left )

	def skipRightChar( self, site ) :
		"""
		获取指定位置下，右边找一个字符所囊括的区域
		"""
		if site >= self.end :
			return self.pyNext.skipRightChar( site )
		return SiteInfo( self.end, self.right )

	def skipLeftWord( self, site ) :
		"""
		获取指定位置下，左边找一个单词所囊括的区域
		"""
		if site <= self.start :
			return self.pyFore.skipLeftWord( site )
		return SiteInfo( self.start, self.left )

	def skipRightWord( self, site ) :
		"""
		获取指定位置下，右边找一个单词所囊括的区域
		"""
		if site >= self.end :
			return self.pyNext.skipRightWord( site )
		return SiteInfo( self.end, self.right )


# --------------------------------------------------------------------
# 第一个空元素
# --------------------------------------------------------------------
class EFirst( BaseElement ) :
	def __init__( self ) :
		BaseElement.__init__( self, 0, csstring.toWideString( "" ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def skipLeftChar( self, site ) :
		"""
		获取指定位置左边一个字符
		"""
		return SiteInfo( 0, 0 )

	def skipRightChar( self, site ) :
		"""
		获取指定位置右边一个字符
		"""
		return self.pyNext.skipRightChar( site )

	def skipLeftWord( self, site ) :
		"""
		获取指定位置左边一个单词
		"""
		return SiteInfo( 0, 0 )

	def skipRightWord( self, site ) :
		"""
		获取指定位置右边一个单词
		"""
		return self.pyNext.skipRightWord( site )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	left = property( lambda self : 0, lambda self, v : 0 )
	right = property( lambda self : 0, lambda self, v : 0 )


# --------------------------------------------------------------------
# 最后一个空元素
# --------------------------------------------------------------------
class ELast( BaseElement ) :
	def __init__( self ) :
		BaseElement.__init__( self, 0, csstring.toWideString( "" ) )
		self.__posX = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setScopeSite_( self, site ) :
		"""
		设置起始（结束）位置
		"""
		self.start = self.end = site


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSiteInfoViaSite( self, site ) :
		"""
		获取指定位置的左距，返回正确位置和左距
		"""
		return SiteInfo( self.end, self.__posX )

	def getSiteInfoViaLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		return SiteInfo( self.end, self.__posX )

	# -------------------------------------------------
	def skipLeftChar( self, site ) :
		"""
		删除指定位置左边一个字符
		"""
		return self.pyFore.skipLeftChar( site )

	def skipRightChar( self, site ) :
		"""
		删除指定位置右边一个字符
		"""
		return SiteInfo( self.start, self.right )

	def skipLeftWord( self, site ) :
		"""
		删除指定位置左边一个单词
		"""
		return self.pyFore.skipLeftWord( site )

	def skipRightWord( self, site ) :
		"""
		删除指定位置右边一个单词
		"""
		return SiteInfo( self.start, self.right )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setPosX( self, x ) :
		self.__posX = x


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	left = property( lambda self : self.__posX, _setPosX )
	right = property( lambda self : self.__posX, _setPosX )


# --------------------------------------------------------------------
# 默认元素
# --------------------------------------------------------------------
class EDefText( BaseElement, StaticText ) :
	def __init__( self, start, text ) :
		BaseElement.__init__( self, start, text )
		StaticText.__init__( self )
		self.text = text


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setAttributes_( self, pyRich ) :
		"""
		根据所属 pyRich 的属性，设置文本属性
		"""
		self.font = pyRich.font
		self.fontSize = pyRich.fontSize
		self.charSpace = pyRich.charSpace
		self.color = pyRich.foreColor
		self.limning = pyRich.limning
		self.limnColor = pyRich.limnColor

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		获取表现文本
		"""
		if scope is None :
			return self.originalText
		else :
			myStart = self.start
			myEnd = self.end
			start = max( scope[0], myStart ) - myStart
			end = min( scope[1], myEnd ) - myStart
			return self.originalText[start:end]
		return csstring.toWideString( "" )

	# -------------------------------------------------
	def getSiteInfoViaSite( self, site ) :
		"""
		获取指定位置的左距
		"""
		start = self.start
		end = self.end
		if site <= start :
			return SiteInfo( start, self.left )
		elif site >= end :
			return SiteInfo( end, self.right )
		count = site - self.start
		left = self.left + self.textWidth( self.originalText[:count] )
		return SiteInfo( site, left )

	def getSiteInfoViaLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		myLeft = self.left
		myRight = self.right
		if left <= myLeft :
			return SiteInfo( self.start, self.left )
		elif left >= self.right :
			return SiteInfo( self.end, self.right )
		ltext, rtext, lwtext, rwtext = self.splitText( left - self.left, "ROUND" )
		site = self.start + len( lwtext )
		left = self.left + self.textWidth( lwtext )
		return SiteInfo( site, left )

	# -------------------------------------------------
	def skipLeftChar( self, site ) :
		"""
		获取指定位置左边一个字符位置
		"""
		start = self.start
		end = self.end
		if site <= start :
			return self.pyFore.skipLeftChar( site )
		site -= 1
		count = site - start
		left = self.left + self.textWidth( self.originalText[:count] )
		return SiteInfo( site, left )

	def skipRightChar( self, site ) :
		"""
		获取指定位置右边一个字符位置
		"""
		start = self.start
		end = self.end
		if site >= end :
			return self.pyNext.skipRightChar( site )
		site += 1
		count = site - start
		left = self.left + self.textWidth( self.originalText[:count] )
		return SiteInfo( site, left )

	def skipLeftWord( self, site ) :
		"""
		获取指定位置左边一个单词位置
		"""
		start = self.start
		end = self.end
		if site <= start :
			return self.pyFore.skipLeftWord( site )
		wtext = self.originalText
		count = site - start
		count = csstring.getLastWordStart( wtext[:count] )
		site = start + count
		left = self.left + self.textWidth( wtext[:count] )
		return SiteInfo( site, left )

	def skipRightWord( self, site ) :
		"""
		获取指定位置右边一个单词位置
		"""
		start = self.start
		end = self.end
		if site >= end :
			return self.pyNext.skipRightWord( site )
		wtext = self.originalText
		count = site - start
		end = csstring.getFirstWordEnd( wtext[count:] )
		count += end
		left = self.left + self.textWidth( wtext[:count] )
		site = self.start + count
		return SiteInfo( site, left )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	font = property( StaticText._getFont, StaticText._setFont )
	color = property( StaticText._getColor, StaticText._setColor )


# --------------------------------------------------------------------
# 文本选择器
# --------------------------------------------------------------------
class Selector( object ) :
	__cg_cover = None

	def __init__( self, lineHeight ) :
		if Selector.__cg_cover is None :
			Selector.__cg_cover = GUI.load( "guis/controls/baseinput/selector.gui" )
		self.__pyCover = None
		self.__lineHeight = lineHeight
		self.__startSiteInfo = None				# 选区起始位置
		self.__endSiteInfo = None				# 选区结束位置
		self.__selecting = False				# 正处于选择文本中


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def startSiteInfo( self ) :
		return self.__startSiteInfo

	@property
	def endSiteInfo( self ) :
		return self.__endSiteInfo

	@property
	def minSiteInfo( self ) :
		return min( self.__startSiteInfo, self.__endSiteInfo )

	@property
	def maxSiteInfo( self ) :
		return max( self.__startSiteInfo, self.__endSiteInfo )

	# -------------------------------------------------
	@property
	def selected( self ) :
		"""
		文本选中器，是否处于使用中
		"""
		if self.__startSiteInfo is None :
			return False
		if self.__endSiteInfo is None :
			return False
		if self.__startSiteInfo == self.__endSiteInfo :
			return False
		return True

	@property
	def selecting( self ) :
		"""
		是否处于选择文本中
		"""
		return self.__selecting


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getCover( self, pyBox ) :
		if self.__pyCover :
			return self.__pyCover
		self.__pyCover = PyGUI( util.copyGui( Selector.__cg_cover ) )
		pyBox.addPyChild( self.__pyCover )
		return self.__pyCover


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setLineHeight_( self, pyBox, height ) :
		"""
		设置文本行高度
		"""
		self.__lineHeight = lineHeight
		if self.__pyCover :
			self.__pyCover.height = lineHeight
		if self.__startSiteInfo and self.__endSiteInfo :
			self.select( pyBox, self.__startSiteInfo, self.__endSiteInfo )

	def flash_( self, pyBox ) :
		"""
		更新选中表现
		"""
		if self.__startSiteInfo and self.__endSiteInfo :
			self.select( pyBox, self.__startSiteInfo, self.__endSiteInfo )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def beginSelecting( self, startInfo ) :
		"""
		开始选择文本
		"""
		self.cancelSelect()
		self.__selecting = True
		self.__startSiteInfo = startInfo

	def endSelecting( self ) :
		"""
		结束选择文本
		"""
		self.__selecting = False

	# ---------------------------------------
	def select( self, pyBox, startInfo, endInfo ) :
		"""
		选中一个区域
		"""
		self.__startSiteInfo = startInfo
		self.__endSiteInfo = endInfo

		if startInfo > endInfo :
			startInfo, endInfo = endInfo, startInfo
		vAlign = pyBox.vTextAlign
		pyCover = self.__getCover( pyBox )
		pyCover.left = startInfo.left
		pyCover.width = endInfo.left - pyCover.left
		if vAlign == "BOTTOM" :
			pyCover.bottom = pyBox.height
		elif vAlign == "MIDDLE" :
			pyCover.middle = pyBox.height * 0.5
		else :
			pyCover.top = 0

	def cancelSelect( self ) :
		"""
		隐藏选中
		"""
		self.__pyCover = None
		self.__startSiteInfo = None
		self.__endSiteInfo = None
		self.__selecting = False
