# -*- coding: gb18030 -*-
#

"""
implement multiline richtext box class。

2009.12.17: writen by huangyongwei
"""


import re
import weakref
import Font
import csstring
from guis import *
from csstring import KeyCharParser
from guis.common.PyGUI import PyGUI
from guis.controls.ScrollBar import VScrollBar
from guis.controls.BaseInput import BaseInput
from guis.controls.StaticText import StaticText

"""
composing :
	GUI.Window
"""

# --------------------------------------------------------------------
# implement multiline RichTextbox
# --------------------------------------------------------------------
class MLRichTextBox( BaseInput ) :
	__cc_newline_tpl = re.compile( "\r\n|\n" )

	def __init__( self, panel, sb, pyBinder = None ) :
		BaseInput.__init__( self, panel, pyBinder )
		self.pySBar = VScrollBar( sb )
		self.pySBar.onScroll.bind( self.__onScroll )
		self.__sbarState = ScrollBarST.AUTO								# 默认自动显示滚动条
		self.focus = True
		self.moveFocus = True
		self.mouseScrollFocus = True
		self.__initScrollBar()

		self.lines_ = []							# 所有文本行
		self.__wtext = csstring.toWideString( "" )	# 文本的宽字符形式
		self.__readOnly = False						# 是否是只读
		self.__escTPLs = []							# 转义模板
		self.__curSiteInfo = SiteInfo( 0, 0, 0 )	# 光标位置

		self.__font = Font.defFont					# 默认字体
		self.__fontSize = Font.defFontSize			# 默认字体大小
		self.__foreColor = ( 255, 255, 255, 255 )	# 默认颜色
		self.__vTextAlgin = "BOTTOM"				# 垂直方向上文本的对齐方式："TOP" / "MIDDLE" / "BOTTOM"
		self.__viewLen = 0							# 可视文本字符数
		self.__wviewLen = 0							# 可是文本字数
		self.__maxLen = -1							# 允许输入的最大字符数，0 表示可输入任意长( 注意：这是表现文本的长度 )
		self.__charSpace = Font.defCharSpace		# 字间距
		self.__spacing = Font.defSpacing			# 行间距
		self.__limning = Font.defLimning			# 描边样式
		self.__limnColor = Font.defLimnColor		# 描边颜色
		self.__forceNewline = True					# 是否允许玩家换行

		wempty = csstring.toWideString( "" )
		self.__pyFirst = EFirst()					# 第一个元素
		self.__pyLast = ELast()						# 最后一个元素

		self.__selector = Selector( self.__fontSize )

	def __del__( self ) :
		BaseInput.__del__( self )
		if Debug.output_del_MultilineRichTextBox :
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
	def __clearText( self ) :
		"""
		清除所有文本
		"""
		pyFirst = self.__pyFirst
		pyLast = self.__pyLast
		pyLast.setScopeSite( 0 )
		pyFirst.setNextElem_( pyLast )
		pyLast.setForeElem_( pyFirst )

		line = Line( self, 0, 0 )
		self.lines_ = [line]
		line.addElem_( pyFirst )
		line.addElem_( pyLast )
		line.newline_()

		self.__wtext = csstring.toWideString( "" )
		self.__curSiteInfo = SiteInfo( 0, 0, 0 )
		self.__viewLen = 0
		self.__wviewLen = 0

		self.cancelSelect()
		if self.tabStop :
			self.__setCursorSite( self.__curSiteInfo )

		self.gui.maxScroll.y = 0
		self.gui.scroll.y = 0

	# -------------------------------------------------
	def __onScroll( self, value ) :
		"""
		滚动条滚动时被触发
		"""
		gui = self.gui
		gui.scroll.y = gui.maxScroll.y * value

	# -------------------------------------------------
	def __resizeCursor( self ) :
		"""
		重新设置光标大小
		"""
		fontHeight = self.__fontSize
		self.pyCursor_.height = fontHeight
		if self.__vTextAlgin == "TOP" :
			self.pyCursor_.top = 0
		elif self.__vTextAlgin == "MIDDLE" :
			self.pyCursor_.middle = self.lines_[0].middle
		else :
			self.pyCursor_.bottom = self.lines_[0].bottom

	# -------------------------------------------------
	def __getTextScopes( self, wtext ) :
		"""
		获取所有转义区域
		"""
		scopes = {}											# { start : ( end, clsElem ) }
		def wellhandled( start ) :							# 是否被转义处理过
			for s, ( e, clsElem ) in scopes.iteritems() :
				if s <= start < e :
					return True
			return False

		tpls = self.__escTPLs + [( self.__cc_newline_tpl, ENewline )]
		for tpl, clsElem in tpls :							# 找出所有转义符
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

	def __layoutElems( self, pyElems ) :
		"""
		排列所有元素
		"""
		def newline( pyForeLine ) :								# 换行
			index = pyForeLine.index + 1
			top = pyForeLine.newline_() + self.__spacing
			pyNextLine = Line( self, index, top )
			self.lines_.append( pyNextLine )
			pyNextLine.setForeLine_( pyForeLine )
			pyForeLine.setNextLine_( pyNextLine )
			pyForeLine = pyNextLine
			return pyNextLine

		self.lines_ = []
		left = 0
		maxWidth = self.width - self.pyCursor_.width
		pyForeLine = Line( self, 0, 0 )
		self.lines_.append( pyForeLine )
		pyForeLine.addElem_( self.__pyFirst )
		pyFore = self.__pyFirst
		for pyElem in pyElems :
			if isinstance( pyElem, ENewline ) :					# 换行符
				pyFore.setNextElem_( pyElem )
				pyElem.setForeElem_( pyFore )
				pyForeLine = newline( pyForeLine )
				pyForeLine.addElem_( pyElem )
				pyFore = pyElem
				left = 0
				continue
			while pyElem :
				self.addPyChild( pyElem )
				pyElem.setAttributes_( self )
				pyFore.setNextElem_( pyElem )
				pyElem.setForeElem_( pyFore )
				pyFore = pyElem
				pyElem.left = left
				right = pyElem.right
				if right <= maxWidth :							# 如果能放下该元素
					pyForeLine.addElem_( pyElem )				# 则添加到当前行
					left = right
					break

				pyNextElem = pyElem.cutText( maxWidth - left )	# 否则，试图折断该元素
				if pyNextElem and pyNextElem != pyElem :		# 如果折断成功，或者当前行中没有元素
					pyForeLine.addElem_( pyElem )				# 则，将前面一截添加到当前行
					pyForeLine = newline( pyForeLine )			# 并且另起一行
					pyElem = pyNextElem
					left = 0
				elif pyForeLine.hasElem_() :					# 如果折断失败，并且当前行已经有元素
					pyForeLine = newline( pyForeLine )			# 则，另起一行
					left = 0
				else :											# 如果截断失败，并且当前行还没有任何元素
					pyForeLine.addElem_( pyElem )				# 则只能直接将该元素放到当前行中
					left = pyElem.right
					break
		self.__pyLast.left = pyFore.right
		self.__pyLast.setForeElem_( pyFore )
		pyFore.setNextElem_( self.__pyLast )
		pyForeLine.addElem_( self.__pyLast )
		pyForeLine.newline_()

	def __resetScrollBar( self ) :
		"""
		更新滚动条
		"""
		viewHeight = self.height
		fontHeight = self.__fontSize
		lastLine = self.lines_[-1]
		maxHeight = lastLine.bottom + fontHeight			# 滚动条拉尽时，预留一行
		hideHeight = max( 0, maxHeight - viewHeight )
		self.gui.maxScroll.y = hideHeight
		self.pySBar.scrollScale = maxHeight / viewHeight
		if hideHeight > 0 :
			self.pySBar.perScroll = fontHeight / hideHeight
			if self.__sbarState == ScrollBarST.AUTO :
				self.pySBar.visible = True
		elif self.__sbarState == ScrollBarST.AUTO:
			self.pySBar.visible = False
			
	def __initScrollBar( self ):
		"""
		初始化滚动条可见性
		"""
		if self.__sbarState == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif self.__sbarState == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif self.__sbarState == ScrollBarST.AUTO :
			self.pySBar.visible = False 
			
	def __setTextElements( self, wtext ) :
		"""
		设置文本的所有元素
		注：原则上添加元素不应该在这里，而应该在 Line 里实现，
			但，Line 只是概念性的行，不是一个 UI，因此在这里添加元素直接一点。
		"""
		self.__clearText()
		self.__wtext = wtext							# 保存宽文本
		scopes = self.__getTextScopes( wtext )			# 获取所有具备转义条件的区域
		starts = sorted( scopes.keys() )				# 按区域索引的起始位置，从小到大排序

		pyElems = []
		count = len( wtext )
		index = 0
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
			text = wtext[start : end]
			pyElem = clsElem.getInst( start, text )				# 创建元素
			if pyElem is None :									# 创建元素时解释失败
				pyElem = EDefText( start, text )				# 用纯文本显示
			self.__viewLen += pyElem.getViewLen()
			self.__wviewLen += pyElem.getWViewLen()
			pyElems.append( pyElem )
		self.__pyLast.setScopeSite( count )
		self.__layoutElems( pyElems )
		self.__resetScrollBar()

	# -------------------------------------------------
	def __getLineOfSite( self, site ) :
		"""
		获取指定位置处的行
		"""
		if site <= 0 :
			return self.lines_[0]
		elif site >= self.lines_[-1].end :
			return self.lines_[-1]

		start = 0
		end = len( self.lines_ )
		while start < end :
			mid = ( start + end ) / 2
			line = self.lines_[mid]
			if site < line.start :
				end = mid
			elif site > line.end :
				start = mid
			else :
				return line
		return None

	def __getLineOfPos( self, pos ) :
		"""
		根据像素位置找出其所处的文本行
		"""
		x, y = pos
		if y <= 0 :
			return self.lines_[0]
		elif y >= self.lines_[-1].bottom :
			return self.lines_[-1]

		spacing = self.spacing
		start = 0
		end = len( self.lines_ )
		while start < end :
			mid = ( start + end ) / 2
			line = self.lines_[mid]
			if y < line.top :
				end = mid
			elif y > line.bottom + spacing :
				start = mid
			else :
				return line
		return None

	def __getLinesOfScope( self, ( start, end ) ) :
		"""
		获取指定索引范围内的文本行
		"""
		lines = []
		for line in self.lines_ :
			if line.end <= start :
				continue
			if line.start >= end :
				break
			lines.append( line )
		return lines

	# ---------------------------------------
	def __getSiteInfoViaSite( self, site, startLineIdx ) :
		"""
		根据 site 获取 SiteInfo
		"""
		if site <= 0 :
			line = self.lines_[0]
			return SiteInfo( line.index, 0, 0 )
		elif site >= self.wlength :
			return self.__getEndSiteInfo()

		line = self.lines_[startLineIdx]
		while line :
			if site <= line.end :
				break
			line = line.next
		return line.getRealSiteViaSite( site )

	def __getSiteInfoViaPos( self, pos ) :
		"""
		根据像素位置获取索引位置
		"""
		line = self.__getLineOfPos( pos )
		return line.getRealSiteViaLeft( pos[0] )

	def __getEndSiteInfo( self ) :
		"""
		文本最末端的位置信息
		"""
		line = self.lines_[-1]
		return SiteInfo( line.index, line.end, line.right )

	# -------------------------------------------------
	def __setCursorSite( self, siteInfo ) :
		"""
		设置光标位置
		"""
		if siteInfo is None : return
		line = self.lines_[siteInfo.lineIdx]
		self.__curSiteInfo = siteInfo
		self.pyCursor_.left = siteInfo.x
		if self.__vTextAlgin == "BOTTOM" :
			self.pyCursor_.bottom = line.bottom
		elif self.__vTextAlgin == "MIDDLE" :
			self.pyCursor_.middle = line.middle
		else :
			self.pyCursor_.top = line.top

		halfFontHeight = self.fontSize * 0.5
		gui = self.gui
		height = gui.height
		top = line.top - halfFontHeight
		bottom = line.bottom + halfFontHeight
		scrollY = gui.scroll.y
		if top < scrollY :
			scrollY = top
		elif bottom > scrollY + height :
			scrollY = bottom - height
		gui.scroll.y = scrollY
		if gui.maxScroll.y > 0 :
			self.pySBar.value = scrollY / gui.maxScroll.y


	# -------------------------------------------------
	# 滚动内容
	# -------------------------------------------------
	def __keyScroll( self, key, mods ) :
		"""
		利用按键滚动内容
		"""
		if key == KEY_UPARROW and mods == MODIFIER_CTRL :
			self.pySBar.decScroll()
			return True
		elif key == KEY_DOWNARROW and mods == MODIFIER_CTRL :
			self.pySBar.incScroll()
			return True
		return False


	# -------------------------------------------------
	# 移动光标
	# -------------------------------------------------
	def __moveLeftChar( self ) :
		"""
		将光标往左移一个字符
		"""
		if self.__selector.selected :
			return self.__selector.minSiteInfo
		siteInfo = self.__curSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipLeftChar( siteInfo )

	def __moveRightChar( self ) :
		"""
		将光标往右移一个字符
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		siteInfo = self.__curSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipRightChar( siteInfo )

	def __moveLeftWord( self ) :
		"""
		往左移动一个单词
		"""
		siteInfo = self.__curSiteInfo
		if self.__selector.selected :
			siteInfo = self.__selector.minSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipLeftWord( siteInfo )

	def __moveRightWord( self ) :
		"""
		往右移动一个单词
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		siteInfo = self.__curSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipRightWord( siteInfo )

	def __moveUpLine( self ) :
		"""
		光标往上跳一行
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipUpLine( self.__curSiteInfo )

	def __moveDownLine( self ) :
		"""
		光标往下跳一行
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipDownLine( self.__curSiteInfo )

	def __moveLeftAll( self ) :
		"""
		将光标移到最始端
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getStartSiteInfo()

	def __moveRightAll( self ) :
		"""
		将光标移动到最末端
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getEndSiteInfo()

	def __moveToTop( self ) :
		"""
		移动到最前端
		"""
		return self.lines_[0].getStartSiteInfo()

	def __moveToBottom( self ) :
		"""
		移动到最末端
		"""
		return self.lines_[-1].getEndSiteInfo()

	# ---------------------------------------
	def __moveCursor( self, key, mods ) :
		"""
		通过键盘键盘移动光标
		"""
		handlers = {
			( KEY_LEFTARROW, 0 )				: self.__moveLeftChar, 		# 往左移动一个字符
			( KEY_RIGHTARROW, 0 )				: self.__moveRightChar,		# 往右移动一个字符
			( KEY_LEFTARROW, MODIFIER_CTRL )	: self.__moveLeftWord,		# 往左移动一个单词
			( KEY_RIGHTARROW, MODIFIER_CTRL )	: self.__moveRightWord,		# 往右移动一个单词
			( KEY_UPARROW, 0 )					: self.__moveUpLine, 		# 往上跳一行
			( KEY_DOWNARROW, 0 )				: self.__moveDownLine,		# 往下跳一行
			( KEY_HOME, 0 )						: self.__moveLeftAll,		# 移到光标所在行的最前面
			( KEY_END, 0 )						: self.__moveRightAll,		# 移到光标所在行的最后面
			( KEY_HOME, MODIFIER_CTRL )			: self.__moveToTop,			# 移动到最前端
			( KEY_END, MODIFIER_CTRL )			: self.__moveToBottom,		# 移动到最末端
			}
		if ( key, mods ) in handlers :
			self.cancelSelect()
			siteInfo = handlers[( key, mods )]()
			self.__setCursorSite( siteInfo )
			return True
		return False

	# -------------------------------------------------
	# 删除字符
	# -------------------------------------------------
	def __delLeftChar( self ) :
		"""
		删除光标左边一个字符
		"""
		endInfo = self.__curSiteInfo
		curLine = self.lines_[endInfo.lineIdx]
		startInfo = curLine.skipLeftChar( endInfo )
		return startInfo, endInfo

	def __delRightChar( self ) :
		"""
		删除光标右边一个字符
		"""
		startInfo = self.__curSiteInfo
		curLine = self.lines_[startInfo.lineIdx]
		endInfo = curLine.skipRightChar( startInfo )
		return startInfo, endInfo

	def __delLeftWord( self ) :
		"""
		删除光标左边一个单词
		"""
		endInfo = self.__curSiteInfo
		curLine = self.lines_[endInfo.lineIdx]
		startInfo = curLine.skipLeftWord( endInfo )
		return startInfo, endInfo

	def __delRightWord( self ) :
		"""
		删除光标右边一个单词
		"""
		startInfo = self.__curSiteInfo
		curLine = self.lines_[startInfo.lineIdx]
		endInfo = curLine.skipRightWord( startInfo )
		return startInfo, endInfo

	# --------------------------------------
	def __delScopeText( self, startInfo, endInfo ) :
		"""
		删除指定区域内的文本
		"""
		start = startInfo.site
		end = endInfo.site
		wtext = self.__wtext
		self.__setTextElements( wtext[:start] + wtext[end:] )
		if startInfo.lineIdx >= self.lineCount :						# 删除完最后一行文本后，有可能减少一行，
			startInfo = self.lines_[-1].getEndSiteInfo()				# 而之前的光标索引不变，从而造成行索引越界
		self.__setCursorSite( startInfo )

	def __delSubStr( self, key, mods ) :
		"""
		通过键盘删除一个子串
		"""
		if self.__readOnly :
			return False

		handlers = {
			( KEY_BACKSPACE, 0 )			 : self.__delLeftChar,		# 删除光标坐标一个字符
			( KEY_DELETE, 0 )				 : self.__delRightChar,		# 删除光标右边一个字符
			( KEY_BACKSPACE, MODIFIER_CTRL ) : self.__delLeftWord,		# 删除光标左边的一个单词
			( KEY_DELETE, MODIFIER_CTRL )	 : self.__delRightWord,		# 删除光标右边的一个单词
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
		line = self.__getLineOfSite( start )
		count = 0
		while line and line.start < end :
			count += len( line.getWViewText( ( start, end ) ) )
			line = line.next
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
		site = start + addCount
		siteInfo = self.__getSiteInfoViaSite( site, startInfo.lineIdx )
		self.__setCursorSite( siteInfo )
		self.cancelSelect()
		self.onTextChanged_()

	def __input( self, key, mods ) :
		"""
		通过键盘输入一个字符
		"""
		if mods == MODIFIER_CTRL :
			return False

		if self.__readOnly :
			return False
		if key == KEY_RETURN or key == KEY_NUMPADENTER :
			if self.__forceNewline == True:
				ch = "\n"
			else :
				return True
		else :
			ch = KeyCharParser.keyToChar( key, mods == MODIFIER_SHIFT )
		if ch != '' :
			self.__insertText( ch )
			return True
		return False

	# -------------------------------------------------
	# 选择文本
	# -------------------------------------------------
	def __selectLeftChar( self ) :
		"""
		选中光标前一个字符
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipLeftChar( self.__curSiteInfo )

	def __selectRightChar( self ) :
		"""
		选中光标后一个字符
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipRightChar( self.__curSiteInfo )

	def __selectLeftWord( self ) :
		"""
		选中光标前一个单词
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipLeftWord( self.__curSiteInfo )

	def __selectRightWord( self ) :
		"""
		选中光标后一个单词
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipRightWord( self.__curSiteInfo )

	def  __selectLeftAll( self ) :
		"""
		选中当前行中，光标前的所有文本
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getStartSiteInfo()

	def __selectRightAll( self ) :
		"""
		选中光标后的所有文本
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getEndSiteInfo()

	def __selectUpLine( self ) :
		"""
		往上选择一行
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipUpLine( self.__curSiteInfo )

	def __selectDownLine( self ) :
		"""
		往下选择一行
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipDownLine( self.__curSiteInfo )

	def __selectUpAll( self ) :
		"""
		选中光标前的所有文本
		"""
		line = self.lines_[0]
		return line.getStartSiteInfo()

	def __selectDownAll( self ) :
		"""
		选中光标后的所有文本
		"""
		return self.__getEndSiteInfo()

	def __selectAll( self ) :
		"""
		选中所有文本
		"""
		startInfo = SiteInfo( 0, 0, 0 )
		endInfo = self.__getEndSiteInfo()
		self.__selector.select( self, startInfo, endInfo )

	# ---------------------------------------
	def __keySelectText( self, key, mods ) :
		"""
		键盘按键选中文本
		"""
		if key == KEY_A and mods == MODIFIER_CTRL :												# 选中全部文本
			self.__selectAll()
			return True

		handlers = {
			( KEY_LEFTARROW, MODIFIER_SHIFT )					: self.__selectLeftChar,		# 往左移动一个字符
			( KEY_RIGHTARROW, MODIFIER_SHIFT )					: self.__selectRightChar,		# 往右移动一个字符
			( KEY_LEFTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectLeftWord,		# 往左移动一个单词
			( KEY_RIGHTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectRightWord,		# 往右移动一个单词
			( KEY_HOME, MODIFIER_SHIFT )						: self.__selectLeftAll,			# 移到最前面
			( KEY_END, MODIFIER_SHIFT )							: self.__selectRightAll,		# 移到最后面
			( KEY_UPARROW, MODIFIER_SHIFT )						: self.__selectUpLine,			# 往上选择一行
			( KEY_DOWNARROW, MODIFIER_SHIFT )					: self.__selectDownLine,		# 往上选择一行
			( KEY_HOME, MODIFIER_SHIFT | MODIFIER_CTRL )		: self.__selectUpAll,			# 移到最前面
			( KEY_END, MODIFIER_SHIFT | MODIFIER_CTRL )			: self.__selectDownAll,			# 移到最后面
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
		x, y = self.mousePos								# 鼠标位置
		y += self.gui.scroll.y
		siteInfo = self.__getSiteInfoViaPos( ( x, y ) )		# 计算光标所在位置和左距
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
			x, y = self.mousePos
			y += self.gui.scroll.y								# 鼠标之前的位置
			endInfo = self.__getSiteInfoViaPos( ( x, y ) )
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

	def onMouseScroll_( self, dz ) :
		self.pySBar.onMouseScroll_( dz )
		return True

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
		if self.__keyScroll( key, mods ) :			# 用按键滚动内容
			return True
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
	def getEscTemplates( self ) :
		"""
		获取转义模板
		"""
		return self.__escTPLs

	def setEscTemplates( self, tpls ) :
		"""
		设置转义模板
		@type				tpl		: re._sre.SRE_Pattern
		@param				tpl		: 转义模板
		@type				clsElem : class
		@param				clsElem : Element
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
		self.onTextChanged_()

	# -------------------------------------------------
	def select( self, start, end ) :
		"""
		选中文本
		"""
		startInfo = self.__getSiteInfoViaSite( start, 0 )
		endInfo = self.__getSiteInfoViaSite( end, 0 )
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
		if self.tabStop :
			self.__setCursorSite( self.__getEndSiteInfo() )

	def _getWViewText( self ) :
		wtext = csstring.toWideString( "" )
		for line in self.lines_ :
			wtext += line.getWViewText()
		return wtext

	def _getWSelectText( self ) :
		wtext = csstring.toWideString( "" )
		if self.__selector.selected :
			startInfo = self.__selector.minSiteInfo
			endInfo = self.__selector.maxSiteInfo
			scope = ( startInfo.site, endInfo.site )
			lines = self.__getLinesOfScope( scope )
			for line in lines :
				wtext += line.getWViewText( scope )
			return wtext
		return wtext

	# ---------------------------------------
	def _getViewLen( self ) :
		count = 0
		for line in self.lines_ :
			count += line.getViewLen()
		return count

	def _getWViewLen( self ) :
		count = 0
		for line in self.lines_ :
			count += line.getWViewLen()
		return count

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
		self.__selector.cancelSelect()

	def _setFontSize( self, size ) :
		if self.__font.endswith( ".font" ) :
			return
		self.__fontSize = size
		self.__setTextElements( self.__wtext )
		if self.tabStop :
			self.__resizeCursor()
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.__selector.cancelSelect()
		self.__selector.setLineHeight_( self, size )

	def _setForeColor( self, color ) :
		self.__foreColor = color
		for line in self.lines_ :
			line.resetForeColor_( color )

	# -------------------------------------------------
	def _setCharSpace( self, space ) :
		self.__charSpace = space
		self.__setTextElements( self.__wtext )
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.__selector.cancelSelect()

	def _setSpacing( self, spacing ) :
		self.__spacing = spacing
		self.__setTextElements( self.__wtext )
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.__selector.cancelSelect()

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

	def _setForceNewline(self,value):
		self.__forceNewline = value

	# -------------------------------------------------
	def _setVTextAlign( self, align ) :
		if isDebuged :
			assert align in set( ["TOP", "MIDDLE", "BOTTOM"] ), "align must be one of 'TOP'/'MIDDLE'/'BOTTOM'"
		self.__vTextAlgin = align
		self._setText( self.__wtext )
		if self.tabStop :
			self.__resizeCursor()
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.__selector.cancelSelect()

	# -------------------------------------------------
	def _setWidth( self, width ) :
		width = max( width, Font.getFontWidth( self.__font ) )
		BaseInput._setWidth( self, width )
		self.__setTextElements( self.__wtext )
		self.__setCursorSite( self.__getEndSiteInfo() )
		self.__selector.cancelSelect()

	def _setHeight( self, height ) :
		height = max( height, Font.getFontHeight( self.__font ) )
		BaseInput._setHeight( self, height )
		self.pySBar.scrollScale = self.gui.maxScroll.y / height
		
	def _getSBarState( self ) :
		return self.__sbarState

	def _setSBarState( self, state ) :
		self.__sbarState = state
		if state == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif state == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif state == ScrollBarST.AUTO :
			self.pySBar.visible = False


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
	viewLength = property( _getViewLen )												# 获取可视文本的字符数
	wviewLength = property( _getWViewLen )												# 获取可视文本的字数
	maxLength = property( lambda self : self.__maxLen, _setMaxLen )						# 获取/设置最多可输入的字符数（注意：这是表现文本的字符数）
	readOnly = property( lambda self : self.__readOnly, _setReadOnly )					# 获取/设置是否只读
	font = property( lambda self : self.__font, _setFont )								# 获取/设置字体
	fontSize = property( lambda self : self.__fontSize, _setFontSize )					# 获取字体大小（高度）
	foreColor = property( lambda self : self.__foreColor, _setForeColor )				# 获取/设置前景色
	charSpace = property( lambda self : self.__charSpace, _setCharSpace )				# 获取/设置字间距
	spacing = property( lambda self : self.__spacing, _setSpacing )						# 获取/设置行间距
	limning = property( lambda self : self.__limning, _setLimning )						# 获取/设置描边样式
	limnColor = property( lambda self : self.__limnColor, _setLimnColor )				# 获取/设置描边颜色
	forceNewline = property( lambda self:self.__forceNewline,_setForceNewline)

	lineCount = property( lambda self : len( self.lines_ ) )							# 获取行数
	vTextalign = property( lambda self : self.__vTextAlgin, _setVTextAlign )			# 获取/设置垂直方向上文本的对齐方式
	textHeight = property( lambda self : self.lines_[-1].bottom )						# 获取所有文本长度

	width = property( lambda self : BaseInput._getWidth( self ), _setWidth )			# 获取/设置宽度
	height = property( lambda self : BaseInput._getHeight( self ), _setHeight )			# 获取/设置高度
	sbarState = property( _getSBarState, _setSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE


# --------------------------------------------------------------------
# 位置信息封装
# --------------------------------------------------------------------
class SiteInfo( object ) :
	__slots__ = ( "lineIdx", "site", "x" )
	def __init__( self, lineIdx, site, x ) :
		self.lineIdx = lineIdx		# 行索引
		self.site = site			# 索引位置
		self.x = x					# 位置左距

	def __cmp__( self, siteInfo ) :
		return self.site - siteInfo.site


# --------------------------------------------------------------------
# 文本行
# --------------------------------------------------------------------
class Line( object ) :
	"""
	行元素基类
	"""
	def __init__( self, pyBox, index, top ) :
		self.__pyBox = weakref.ref( pyBox )
		self.__index = index
		self.__fore = None
		self.__next = None

		self.__pyElems = []
		self.__top = top
		self.__height = pyBox.fontSize


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def index( self ) :
		return self.__index

	@property
	def fore( self ) :
		if self.__fore is None :
			return None
		return self.__fore()

	@property
	def next( self ) :
		if self.__next is None :
			return None
		return self.__next()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getElemOfSite( self, site ) :
		"""
		获取指定索引位置处的元素
		"""
		pyFirst = self.__pyElems[0]
		pyLast = self.__pyElems[-1]
		if site <= pyFirst.start :
			return pyFirst
		elif site >= pyLast.end :
			return pyLast

		start = 0
		end = len( self.__pyElems )
		while start < end :
			mid = ( start + end ) / 2
			pyElem = self.__pyElems[mid]
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
			return self.__pyElems[0]
		pyLast = self.__pyElems[-1]
		if left >= pyLast.right :
			return pyLast
		start = 0
		end = len( self.__pyElems )
		while start < end :
			mid = ( start + end ) / 2
			pyElem = self.__pyElems[mid]
			if left < pyElem.left :
				end = mid
			elif left > pyElem.right :
				start = mid
			else :
				return pyElem
		return None

	# ---------------------------------------
	def __getElemsOfScope( self, scope ) :
		"""
		获取指定区域内的所有元素
		"""
		pyElems = []
		start, end = scope
		for pyElem in self.__pyElems :
			if pyElem.end <= start :
				continue
			if pyElem.start >= end :
				break
			pyElems.append( pyElem )
		return pyElems


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setForeLine_( self, line ) :
		"""
		设置前置元素
		"""
		if line is None :
			self.__fore = None
		self.__fore = weakref.ref( line )

	def setNextLine_( self, line ) :
		"""
		设置后置元素
		"""
		if line is None :
			self.__next = None
		self.__next = weakref.ref( line )

	# -------------------------------------------------
	def addElem_( self, pyElem ) :
		"""
		添加一个元素
		"""
		pyElem.setLine_( self )
		self.__height = max( pyElem.height, self.__height )
		self.__pyElems.append( pyElem )

	def hasElem_( self ) :
		"""
		是否有非空元素
		"""
		pyElems = self.__pyElems
		count = len( pyElems )
		if count == 0 :
			return False
		elif count == 1 :
			pyElem = pyElems[0]
			if isinstance( pyElem, EFirst ) or \
				isinstance( pyElem, ELast ) :
					return False
		elif count == 2 :
			pyFirst, pyLiast = pyElems
			if isinstance( pyFirst, EFirst ) and \
				isinstance( pyLiast, ELast ) :
					return False
		return True

	def newline_( self ) :
		"""
		另起一行，排列所有元素，并返回自己的底部距离
		"""
		pyBox = self.__pyBox()
		textAlign = pyBox.vTextalign
		if textAlign == "TOP" :					# 文本顶部对齐
			aname = "top"
			y = self.top
		elif textAlign == "MIDDLE" :			# 文本中间对齐
			aname = "middle"
			y = self.middle
		else :
			aname = "bottom"					# 文本底部对齐
			y = self.bottom
		for pyElem in self.__pyElems :
			setattr( pyElem, aname, y )
		return self.bottom

	# -------------------------------------------------
	def resetForeColor_( self, color ) :
		"""
		重新设置字体颜色
		"""
		for pyElem in self.__pyElems :
			pyElem.color = color


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def inLineStart( self, site ) :
		"""
		指定位置是否在行首
		"""
		if site <= self.start :
			return True
		pyFirst = self.__pyElems[0]
		if isinstance( pyFirst, ENewline ) :
			if site <= pyFirst.end :
				return True
		return False

	def inLineEnd( self, site ) :
		"""
		指定位置是否在行尾
		"""
		return site >= self.end

	def getStartSiteInfo( self ) :
		"""
		获取行首的位置信息
		"""
		pyFirst = self.__pyElems[0]
		if isinstance( pyFirst, ENewline ) :
			return SiteInfo( self.index, pyFirst.end, 0 )
		return SiteInfo( self.index, self.start, 0 )

	def getEndSiteInfo( self ) :
		"""
		获取行尾位置信息
		"""
		return SiteInfo( self.index, self.end, self.right )

	# -------------------------------------------------
	def getRealSiteViaSite( self, site ) :
		"""
		根据有可能处于拆分完整单元的位置获取正确位置，返回正确位置和左距
		"""
		pyElem = self.__getElemOfSite( site )
		site, x = pyElem.calcRealSite( site )
		return SiteInfo( self.index, site, x )

	def getRealSiteViaLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		pyElem = self.__getElemOfLeft( left )
		site, x = pyElem.calcRealLeft( left )
		return SiteInfo( self.index, site, x )

	# -------------------------------------------------
	def skipLeftChar( self, siteInfo ) :
		"""
		在指定位置处往左跳一个字符，
		"""
		site = siteInfo.site
		if self.inLineStart( site ) :					# 如果当前位置在行首
			fore = self.fore
			if fore :									# 如果前面还有行
				return fore.getEndSiteInfo()			# 则，返回前一行的行末
			else :										# 如果前面已经没有行
				return siteInfo							# 则，返回当前行行首（原样返回）
		else :											# 当前位置在行中
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getLeftCharSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipRightChar( self, siteInfo ) :
		"""
		在指定位置处往右跳一个字符
		"""
		site = siteInfo.site
		if site >= self.end :							# 如果当前位置在行末
			next = self.next
			if next :
				return next.getStartSiteInfo()	# 则返回下一行的行首
			else :										# 如果后面已经没有行了
				return siteInfo							# 则，返回当前行行末（原样返回）
		else :											# 当前位置在行中
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getRightCharSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipLeftWord( self, siteInfo ) :
		"""
		在指定位置处，前跳一个单词
		"""
		site = siteInfo.site
		if self.inLineStart( site ) :					# 如果当前位置在行首
			fore = self.fore
			if fore :
				return fore.getEndSiteInfo()		# 则，返回前一行的行末
		else :											# 当前位置在行中
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getLeftWordSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipRightWord( self, siteInfo ) :
		"""
		在指定位置处，后跳一个单词
		"""
		site = siteInfo.site
		if site >= self.end :							# 如果当前位置在行末
			next = self.next
			if next :
				return next.getStartSiteInfo()	# 则返回下一行的行首
		else :											# 当前位置在行中
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getRightWordSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipUpLine( self, siteInfo ) :
		"""
		在指定位置处往上移一行
		"""
		fore = self.fore
		if fore is None : return siteInfo
		pyElem = fore.__getElemOfLeft( siteInfo.x )
		site, x = pyElem.calcRealLeft( siteInfo.x )
		return SiteInfo( fore.index, site, x )

	def skipDownLine( self, siteInfo ) :
		"""
		在指定位置处往下移一行
		"""
		next = self.next
		if next is None : return siteInfo
		pyElem = next.__getElemOfLeft( siteInfo.x )
		site, x = pyElem.calcRealLeft( siteInfo.x )
		return SiteInfo( next.index, site, x )

	# -------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		获取这一行文本的宽字符串
		"""
		wtext = csstring.toWideString( "" )
		if scope is None :
			for pyElem in self.__pyElems :
				wtext += pyElem.getWViewText( scope )
		else :
			pyElems = self.__getElemsOfScope( scope )
			for pyElem in pyElems :
				wtext += pyElem.getWViewText( scope )
		return wtext

	def getViewLen( self ) :
		"""
		获取本行可视文本的长度
		"""
		count = 0
		for pyElem in self.__pyElems :
			count += pyElem.getViewLen()
		return count

	def getWViewLen( self ) :
		"""
		获取本行可视文本的宽字符长度
		"""
		count = 0
		for pyElem in self.__pyElems :
			count += pyElem.getWViewLen()
		return count


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setTop( self, top ) :
		self.__top = top

	def _setMiddle( self, middle ) :
		self.__top = middle - self.__height * 0.5

	def _setBottom( self, bottom ) :
		self.__top = bottom - self.__height


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	start = property( lambda self : self.__pyElems[0].start )
	end = property( lambda self : self.__pyElems[-1].end )
	top = property( lambda self : self.__top, _setTop )
	right = property( lambda self : self.__pyElems[-1].right )
	middle = property( lambda self : self.__top + self.__height * 0.5, _setMiddle )
	bottom = property( lambda self : self.__top + self.__height, _setBottom )
	height = property( lambda self : self.__height )


# --------------------------------------------------------------------
# 文本元素
# --------------------------------------------------------------------
class BaseElement( object ) :
	"""
	元素基类
	"""
	def __init__( self, start, text ) :
		self.start = start
		self.end = start + len( text )
		self.originalText = text

		self.__line = None
		self.__pyFore = None
		self.__pyNext = None

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def line( self ) :
		return self.__line()

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
	def setLine_( self, line ) :
		"""
		设置所属的行
		"""
		self.__line = weakref.ref( line )

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
		根据 pyRich 的属性设置 element 的属性
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def getInst( SELF, start, text ) :
		"""
		是否有效
		"""
		return SELF( start, text )

	# -------------------------------------------------
	def getWViewText( self, scope ) :
		"""
		获取表现文本
		"""
		if scope is None :
			return self.originalText
		elif scope[0] < self.end and scope[1] > self.start :
			return self.originalText
		return csstring.toWideString( "" )

	# --------------------------------------
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
	def calcRealSite( self, site ) :
		"""
		根据有可能处于拆分完整单元的位置获取正确位置，返回正确位置和左距
		"""
		start = self.start
		end = self.end
		center = ( start + end ) / 2
		if site <= center :
			return start, self.left
		return self.end, self.right

	def calcRealLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		myLeft = self.left
		myRight = self.right
		center = ( myLeft + myRight ) * 0.5
		if left <= center :
			return self.start, myLeft
		return self.end, myRight

	# ---------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		获取指定位置下，左边找一个字符的索引位置和左距
		"""
		if site <= self.start :
			return self.pyFore.getLeftCharSiteX( site )
		elif site > self.end :
			self.pyNext.getLeftCharSiteX( site )
		return self.start, self.left

	def getRightCharSiteX( self, site ) :
		"""
		获取指定位置下，右边找一个字符的索引位置和左距
		"""
		if site < self.start :
			return self.pyFore.getRightCharSiteX( site )
		elif site >= self.end :
			return self.pyNext.getRightCharSiteX( site )
		return self.end, self.right

	def getLeftWordSiteX( self, site ) :
		"""
		获取指定位置下，左边找一个单词的索引位置和左距
		"""
		if site <= self.start :
			return self.pyFore.getLeftWordSiteX( site )
		elif site > self.end :
			return self.pyNext.getLeftWordSiteX( site )
		return self.start, self.left

	def getRightWordSiteX( self, site ) :
		"""
		获取指定位置下，右边找一个单词的索引位置和左距
		"""
		if site < self.start :
			return self.pyFore.getRightWordSiteX( site )
		elif site >= self.end :
			return self.pyNext.getRightWordSiteX( site )
		return self.end, self.right

	# -------------------------------------------------
	def cutText( self, width ) :
		"""
		剪切文本
		"""
		return None


# --------------------------------------------------------------------
# 第一个空元素
# --------------------------------------------------------------------
class EFirst( BaseElement ) :
	def __init__( self ) :
		BaseElement.__init__( self, 0, csstring.toWideString( "" ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def calcRealSite( self, site ) :
		"""
		获取指定位置的左距，返回正确位置和左距
		"""
		return 0, 0

	def calcRealLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		if left <= 0 : return 0, 0
		return self.pyNext.calcRealLeft( left )

	# -------------------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		获取指定位置下，左边找一个字符的索引位置和左距
		"""
		return 0, 0

	def getRightCharSiteX( self, site ) :
		"""
		获取指定位置右边一个字符的索引位置和左距
		"""
		return self.pyNext.getRightCharSiteX( site )

	def getLeftWordSiteX( self, site ) :
		"""
		获取指定位置左边一个单词的索引位置和左距
		"""
		return 0, 0

	def getRightWordSiteX( self, site ) :
		"""
		删除指定位置右边一个单词
		"""
		return self.pyNext.getRightWordSiteX( site )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	height = property( lambda self : self.line.height )
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
	# public
	# ----------------------------------------------------------------
	def setScopeSite( self, site ) :
		"""
		设置起始（结束）位置
		"""
		self.__posX = self.start = self.end = site

	# -------------------------------------------------
	def calcRealSite( self, site ) :
		"""
		获取指定位置的左距，返回正确位置和左距
		"""
		return self.end, self.__posX

	def calcRealLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		if left >= self.right :
			return self.end, self.right
		return self.pyFore.calcRealLeft( left )

	# -------------------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		获取指定位置左边一个字符
		"""
		return self.pyFore.getLeftCharSiteX( site )

	def getRightCharSiteX( self, site ) :
		"""
		获取指定位置右边一个字符
		"""
		return self.end, self.right

	def getLeftWordSiteX( self, site ) :
		"""
		获取指定位置左边一个单词
		"""
		return self.pyFore.getLeftWordSiteX( site )

	def getRightWordSiteX( self, site ) :
		"""
		获取指定位置右边一个单词
		"""
		return self.end, self.right


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setPosX( self, x ) :
		self.__posX = x


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	height = property( lambda self : self.line.height )
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
		根据 RichText 设置文本属性
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
	def getWViewText( self, scope ) :
		"""
		获取指定区域内的文本
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

	# ---------------------------------------
	def calcRealSite( self, site ) :
		"""
		获取指定位置的左距
		"""
		start = self.start
		end = self.end
		if site <= start :
			return start, self.left
		elif site >= end :
			return end, self.right
		count = site - start
		return site, self.left + self.textWidth( self.originalText[:count] )

	def calcRealLeft( self, x ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		left = self.left
		right = self.right
		if x <= left :
			return self.start, left
		elif x >= right :
			return self.end, right
		ltext, rtext, lwtext, rwtext = self.splitText( x - left, "ROUND" )
		return self.start + len( lwtext ), left + self.textWidth( lwtext )

	# -------------------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		获取指定位置左边一个字符，返回删除的索引区段
		"""
		if site <= self.start :
			return self.pyFore.getLeftCharSiteX( site )
		elif site > self.end :
			return self.pyNext.getLeftCharSiteX( site )
		site -= 1
		charStart = site - self.start
		x = self.left + self.textWidth( self.originalText[:charStart] )
		return site, x

	def getRightCharSiteX( self, site ) :
		"""
		获取指定位置右边一个字符
		"""
		if site < self.start :
			return self.pyFore.getRightCharSiteX( site )
		elif site >= self.end :
			return self.pyNext.getRightCharSiteX( site )
		site += 1
		chatEnd = site - self.start
		x = self.left + self.textWidth( self.originalText[:chatEnd] )
		return site, x

	def getLeftWordSiteX( self, site ) :
		"""
		获取指定位置左边一个单词
		"""
		if site <= self.start :
			return self.pyFore.getLeftWordSiteX( site )
		elif site > self.end :
			return self.pyNext.getLeftWordSiteX( site )
		wtext = self.originalText
		count = site - self.start
		start = csstring.getLastWordStart( wtext[:count] )
		x = self.left + self.textWidth( wtext[:start] )
		site = self.start + start
		return site, x

	def getRightWordSiteX( self, site ) :
		"""
		获取指定位置右边一个单词
		"""
		start = self.start
		end = self.end
		if site < start :
			return self.pyFore.getRightWordSiteX( site )
		elif site >= end :
			return self.pyNext.getRightWordSiteX( site )
		wtext = self.originalText
		count = site - start
		end = csstring.getFirstWordEnd( wtext[count:] )
		count += end
		x = self.left + self.textWidth( wtext[:count] )
		site = self.start + count
		return site, x

	# -------------------------------------------------
	def cutText( self, width ) :
		"""
		折断文本
		"""
		ltext, rtext, lwtext, rwtext = self.splitText( width, "CUT" )
		if lwtext == "" : return self
		self.end = self.start + len( lwtext )
		self.text = lwtext
		self.originalText = lwtext
		pyText = EDefText( self.end, rwtext )
		return pyText


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	font = property( StaticText._getFont, StaticText._setFont )
	color = property( StaticText._getColor, StaticText._setColor )

class ENewline( BaseElement ) :
	"""
	换行
	"""
	def __init__( self, start, text ) :
		BaseElement.__init__( self, start, text )
		self.__posX = 0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def calcRealSite( self, site ) :
		"""
		根据有可能处于拆分完整单元的位置获取正确位置，返回正确位置和左距
		"""
		return self.end, self.right

	def calcRealLeft( self, left ) :
		"""
		根据左距获取位置，返回正确位置和左距
		"""
		return self.end, self.right

	# -------------------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		获取指定位置下，左边找一个字符的索引位置和左距
		"""
		pyFore = self.pyFore
		return pyFore.end, pyFore.right

	def getRightCharSiteX( self, site ) :
		"""
		获取指定位置下，右边找一个字符的索引位置和左距
		"""
		return self.pyNext.getRightCharSiteX( self.end )

	def getLeftWordSiteX( self, site ) :
		"""
		获取指定位置下，左边找一个单词的索引位置和左距
		"""
		pyFore = self.pyFore
		return pyFore.end, pyFore.right

	def getRightWordSiteX( self, site ) :
		"""
		获取指定位置下，右边找一个单词的索引位置和左距
		"""
		return self.pyNext.getRightWordSiteX( self.end )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setPosX( self, x ) :
		self.__posX = x


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	height = property( lambda self : self.line.height )
	left = property( lambda self : self.__posX, _setPosX )
	right = property( lambda self : self.__posX, _setPosX )

# --------------------------------------------------------------------
class Selector( object ) :
	__cg_covers = None

	def __init__( self, lineHeight ) :
		if not self.__cg_covers :
			Selector.__cg_covers = GUI.load( "guis/controls/baseinput/selector.gui" )
		self.__lineHeight = lineHeight
		self.__pyCovers = []
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
	def __getCovers( self, count ) :
		pyCovers = self.__pyCovers
		self.__pyCovers = []
		moreCount = count - len( pyCovers )
		for i in xrange( moreCount ) :
			cover = util.copyGui( Selector.__cg_covers )
			cover.height = self.__lineHeight
			pyCovers.append( PyGUI( cover ) )
		return pyCovers


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setLineHeight_( self, pyBox, height ) :
		"""
		设置文本行高度
		"""
		self.__lineHeight = height
		for pyCover in self.__pyCovers :
			pyCover.height = height
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
		vAlign = pyBox.vTextalign
		startLineIdx = startInfo.lineIdx						# 起始位置
		endLineIdx = endInfo.lineIdx							# 结束位置
		endLineCount = endLineIdx + 1
		count = endLineCount - startLineIdx
		pyCovers = self.__getCovers( count )
		for idx in xrange( startLineIdx, endLineCount ) :
			line = pyBox.lines_[idx]
			pyCover = pyCovers[idx - startLineIdx]
			pyBox.addPyChild( pyCover )
			self.__pyCovers.append( pyCover )
			if idx == startLineIdx :
				pyCover.left = startInfo.x
			else :
				pyCover.left = 0
			if idx == endLineIdx :
				pyCover.width = endInfo.x - pyCover.left
			else :
				pyCover.width = line.right - pyCover.left

			if vAlign == "BOTTOM" :
				pyCover.bottom = line.bottom
			elif vAlign == "MIDDLE" :
				pyCover.middle = line.middle
			else :
				pyCover.top = line.top

	def cancelSelect( self ) :
		"""
		隐藏选中
		"""
		self.__pyCovers = []
		self.__startSiteInfo = None
		self.__endSiteInfo = None
		self.__selecting = False
