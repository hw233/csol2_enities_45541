# -*- coding: gb18030 -*-
#
# $Id: TextBox.py,v 1.33 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement textbox class
2006/04/10 : writen by huangyongwei
"""
"""
composing :
	GUI.Window
"""

import Font
import csstring
from guis import *
from guis.common.PyGUI import PyGUI
from StaticText import StaticText
from BaseInput import BaseInput
from csstring import KeyCharParser

class TextBox( BaseInput ) :
	__cg_selector = None

	def __init__( self, textBox = None, pyBinder = None ) :
		BaseInput.__init__( self, textBox, pyBinder )
		if TextBox.__cg_selector is None :
			TextBox.__cg_selector = GUI.load( "guis/controls/baseinput/selector.gui" )

		# -----------------------------------
		# protected
		# -----------------------------------
		self.pyLText_ = SegText()									# 光标左边的文本标签
		self.pyRText_ = SegText()									# 光标右边的文本标签
		self.__pySelector = PyGUI( util.copyGui( TextBox.__cg_selector ) )
		self.pyLText_.v_anchor = UIAnchor.MIDDLE
		self.pyRText_.v_anchor = UIAnchor.MIDDLE
		self.font = Font.defFont
		self.canTabIn = True
		self.__initialize( textBox )

		self.__readOnly = False										# 是否是只读
		self.__textAlign = "LEFT"									# 停靠方式（暂时没用）
		self.__maxLen = -1											# 允许输入的文本最大长度
		self.__filterChars = []										# 过滤字符（在该集合中的字符不允许输入）
		self.__selRange = ( 0, 0 )									# 选中文本的范围

		self.__foreColor = self.pyLText_.color						# 临时变量（记录输入框无效前的前景色）
		self.__tmpSelectStart = 0									# 临时变量（记录选中文本的起始位置）

	def subclass( self, textBox, pyBinder = None ) :
		BaseInput.subclass( self, textBox, pyBinder )
		self.__initialize( textBox )
		return self

	def __del__( self ) :
		BaseInput.__del__( self )
		if Debug.output_del_TextBox :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, textBox ) :
		if textBox is None : return
		self.focus = True

		self.addPyChild( self.pyLText_ )
		self.addPyChild( self.pyRText_ )
		self.addPyChild( self.__pySelector )
		self.pyLText_.v_dockStyle = "MIDDLE"
		self.pyRText_.v_dockStyle = "MIDDLE"
		self.__pySelector.v_dockStyle = "MIDDLE"
		self.__pySelector.width = 0
		self.__pySelector.height = self.height
		self.__pySelector.top = 1.0

		middle = self.height * 0.5
		self.pyLText_.middle = middle
		self.pyRText_.middle = middle

	# ----------------------------------------------------------------
	# events
	# ---------------------------------------------------------------
	def generateEvents_( self ) :
		BaseInput.generateEvents_( self )
		self.__onTextChanged = self.createEvent_( "onTextChanged" )

	@property
	def onTextChanged( self ) :
		"""
		当文本改变时被触发
		"""
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __intValidate( self, ch ) :
		"""
		是否是数值字符
		"""
		if ch in "0123456789" : return True							# ch is number
		if ch in "+-" and self.pyLText_.text == "" and \
			ch not in self.text : 									# ch is“＋” or “－”
				return True
		return False

	def __floatValidate( self, ch ) :
		"""
		是否是浮点字符
		"""
		if ch in '0123456789' : return True							# ch is number
		if ch == '.' and ch not in self.text : return True			# ch is“.”
		if ch in "+-" and self.pyLText_.text == "" and \
			ch not in self.text :									# ch is“＋” or “－”
				return True
		return False

	def __validate( self, ch ) :
		"""
		验证字符是否合法
		"""
		if ch in self.__filterChars :
			return False											# 过滤字符
		if self.inputMode == InputMode.COMMON :						# 普通模式
			return True
		if self.inputMode == InputMode.PASSWORD :					# 密码模式
			return True
		elif self.inputMode == InputMode.INTEGER :					# 整数模式
			return self.__intValidate( ch )
		elif self.inputMode == InputMode.FLOAT :					# 浮点数模式
			return self.__floatValidate( ch )
		elif self.inputMode == InputMode.NATURALNUM :				# 自然数
			if ch == "-" : return False
			return self.__intValidate( ch )
		return False

	# ---------------------------------------
	def __isSlopOver( self, addLen ) :
		"""
		字符的输入是否超出输入框的最多字符数限制
		"""
		if self.__maxLen < 0 : return False
		newLen = self.wlength + addLen
		if newLen <= self.__maxLen : return False
		return True

	# ---------------------------------------
	def __relocateCursor( self ) :
		"""
		重新设置光标位置
		"""
		if self.pyCursor_.capped( self ) :
			left = self.pyLText_.right						# 光标的默认左距
			right  = left + self.pyCursor_.width			# 光标的默认右距
			if left < 0 :									# 光标在最左边
				self.pyCursor_.left = 0
			elif right > self.width :						# 光标在最右边
				self.pyCursor_.right = self.width - 1
			else :
				self.pyCursor_.left = left
			self.pyLText_.right = self.pyCursor_.left
			self.pyRText_.left = self.pyCursor_.left

	# -------------------------------------------------
	def __setCursorToMouse( self ) :
		"""
		将光标定位到鼠标处
		"""
		cx = csol.pcursorPosition()[0]
		lx = self.pyLText_.leftToScreen
		ltext, rtext, wltext, wrtext = self.pyLText_.splitText( cx - lx, "ROUND", self.text )
		self.pyLText_.text = ltext
		self.pyRText_.text = rtext
		self.__relocateCursor()

	# -------------------------------------------------
	def __deleteSelectText( self ) :
		"""
		删除选中文本
		"""
		start, end = self.__selRange
		if start == end : return False						# 当前没有选中文本
		if start > end : start, end = end, start
		wtext = self.wtext
		self.pyLText_.text = wtext[:start]
		self.pyRText_.text = wtext[end:]
		self.__relocateCursor()
		self.__deselectText()
		return True


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __moveCursor( self, key, mods ) :
		"""
		通过键盘键盘移动光标
		"""
		if key == KEY_LEFTARROW and mods == 0 :
			self.__moveLeftChar()									# 往左移动一个字符
			return True
		if key == KEY_RIGHTARROW and mods == 0 :
			self.__moveRightChar()									# 往右移动一个字符
			return True
		if key == KEY_LEFTARROW and mods == MODIFIER_CTRL :
			self.__moveLeftWord()									# 往左移动一个单词
			return True
		if key == KEY_RIGHTARROW and mods == MODIFIER_CTRL :
			self.__moveRightWord()									# 往右移动一个单词
			return True
		if key == KEY_HOME and mods == 0 :
			self.__moveToLeft()										# 将光标移动到文本最前面
			return True
		if key == KEY_END and mods == 0 :
			self.__moveToRight()									# 将光标移动到文本最后面
			return True
		return False

	def __selectStr( self, key, mods ) :
		"""
		通过键盘来选中一组文本
		"""
		if key == KEY_LEFTARROW and mods == MODIFIER_SHIFT :
			self.__selectLeftChar()									# 选中光标坐标一个字符
			return True
		if key == KEY_RIGHTARROW and mods == MODIFIER_SHIFT :
			self.__selectRightChar()								# 选中光标右边一个字符
			return True
		if key == KEY_LEFTARROW and mods == MODIFIER_CTRL | MODIFIER_SHIFT :
			self.__selectLeftWord()									# 选中光标左边的一个单词
			return True
		if key == KEY_RIGHTARROW and mods == MODIFIER_CTRL | MODIFIER_SHIFT :
			self.__selectRightWord()				 				# 选中光标右边的一个单词
			return True
		if key == KEY_HOME and mods == MODIFIER_SHIFT :
			self.__selectLeftAll()									# 选中光标左边的文本
			return True
		if key == KEY_END and mods == MODIFIER_SHIFT :
			self.__selectRightAll()									# 选中光标有边的文本
			return True
		return False

	def __delSubStr( self, key, mods ) :
		"""
		通过键盘删除一个子串
		"""
		if key == KEY_BACKSPACE and mods == 0 :
			self.__delLeftChar()									# 删除光标坐标一个字符
			return True
		if key == KEY_DELETE and mods == 0 :
			self.__delRightChar()									# 删除光标右边一个字符
			return True
		if key == KEY_BACKSPACE and mods == MODIFIER_CTRL :
			self.__delLeftWord()									# 删除光标左边的一个单词
			return True
		if key == KEY_DELETE and mods == MODIFIER_CTRL :
			self.__delRightWord()					 				# 删除光标右边的一个单词
			return True
		return False

	def __edit( self, key, mods ) :
		"""
		通过快捷键编辑
		"""
		if key == keys.KEY_C and mods == keys.MODIFIER_CTRL :		# 按 CTRL + C 则复制
			self.__doCopy()
			return True
		if key == keys.KEY_X and mods == keys.MODIFIER_CTRL :		# 按 CTRL + V 则剪切
			self.__doCut()
			return True
		if key == keys.KEY_V and mods == keys.MODIFIER_CTRL :		# 按 CTRL + V 则粘贴粘贴版数据
			self.__doPaste()
			return True
		return False

	def __input( self, key, mods ) :
		"""
		通过键盘输入一个字符
		"""
		ch = KeyCharParser.keyToChar( key, mods == MODIFIER_SHIFT )
		if ch != '' :
			self.__deleteSelectText()								# 先删除选中文本
			if self.__isSlopOver( 1 ) :								# 超出了可输入的最大长度
				return True
			return self.__addChar( ch )
		return False

	# -------------------------------------------------
	# 移动光标
	# -------------------------------------------------
	def __moveLeftChar( self ) :
		"""
		将光标往左移一个字符
		"""
		start, end = self.__selRange
		if start < end :									# 如果当前有选中文本，并且是往右选中
			self.moveCursorTo( start )						# 则光标回到选中文本的最左端
		elif start == end :									# 如果当前没有选中文本
			self.moveCursorTo( self.pyLText_.wlength - 1 )	# 则光标往左移动一个字符的宽度
		self.__deselectText()								# 去掉选中文本的选定状态

	def __moveRightChar( self ) :
		"""
		将光标往右移一个字符
		"""
		start, end = self.__selRange
		if start > end :									# 如果当前有选中文本，并且是往左选中
			self.moveCursorTo( start )						# 则光标回到选中文本的最左端
		elif start == end :									# 如果当前没有选中文本
			self.moveCursorTo( self.pyLText_.wlength + 1 )	# 则光标往左移动一个字符的宽度
		self.__deselectText()								# 去掉选中文本的选定状态

	def __moveLeftWord( self ) :
		"""
		往左移动一个单词
		"""
		site = self.getRightWordStart( self.pyLText_.wtext )
		self.moveCursorTo( site )
		self.__deselectText()

	def __moveRightWord( self ) :
		"""
		往右移动一个单词
		"""
		rsite = self.getLeftWordEnd( self.pyRText_.wtext )
		self.moveCursorTo( self.pyLText_.wlength + rsite )
		self.__deselectText()

	def __moveToLeft( self ) :
		"""
		将光标移动到最左边
		"""
		self.moveCursorTo( 0 )
		self.__deselectText()

	def __moveToRight( self ) :
		self.moveCursorTo( self.wlength )
		self.__deselectText()

	# --------------------------------------
	# 选中子串
	# --------------------------------------
	def __selectLeftChar( self ) :
		"""
		选中光标左边的一个字符
		"""
		start, end = self.__selRange
		if start == end :							# 当前没有选中文本
			start = self.pyLText_.wlength
			end = start - 1
		else :										# 当前有选中文本
			end -= 1
		self.select( start, end )

	def __selectRightChar( self ) :
		"""
		选中光标有边的一个字符
		"""
		start, end = self.__selRange
		if start == end :							# 当前没有选中文本
			start = self.pyLText_.wlength
			end = start + 1
		else :										# 当前有选中文本
			end += 1
		self.select( start, end )

	def __selectLeftWord( self ) :
		"""
		选中光标左边一个单词
		"""
		start, end = self.__selRange
		if start == end :							# 当前没有选中文本
			start = self.pyLText_.wlength
		site = self.getRightWordStart( self.pyLText_.wtext )
		self.select( start, site )

	def __selectRightWord( self ) :
		"""
		选中光标有边一个单词
		"""
		start, end = self.__selRange
		if start == end :							# 当前没有选中文本
			start = self.pyLText_.wlength
		rsite = self.getLeftWordEnd( self.pyRText_.wtext )
		self.select( start, self.pyLText_.wlength + rsite )

	def __selectLeftAll( self ) :
		"""
		选中光标左边的全部文本
		"""
		start, end = self.__selRange
		if start == end :							# 当前没有选中文本
			start = self.pyLText_.wlength
		self.select( start, 0 )

	def __selectRightAll( self ) :
		"""
		选中光标有边的全部文本
		"""
		start, end = self.__selRange
		if start == end :							# 当前没有选中文本
			start = self.pyLText_.wlength
		self.select( start, self.wlength )

	# --------------------------------------
	# 删除字符
	# --------------------------------------
	def __delLeftChar( self ) :
		"""
		删除光标左边一个字符
		"""
		if self.__deleteSelectText() :									# 如果有选中文本则删除选中文本
			return
		self.pyLText_.text = self.pyLText_.wtext[:-1]
		self.__relocateCursor()

	def __delRightChar( self ) :
		"""
		删除光标右边一个字符
		"""
		if self.__deleteSelectText() :									# 如果有选中文本则删除选中文本
			return
		self.pyRText_.text = self.pyRText_.wtext[1:]
		self.__relocateCursor()

	def __delLeftWord( self ) :
		"""
		删除光标左边一个单词
		"""
		text = self.pyLText_.text
		newText = text.rstrip()
		if text == newText :											# 如果光标左边没有空格
			site = self.getRightWordStart( self.pyLText_.wtext )		# 则获取光标左边的一个单词
			self.pyLText_.text = self.pyLText_.wtext[:site]				# 删除该单词
		else :															# 否则
			self.pyLText_.text = newText								# 首先删除空格
		self.__deselectText()											# 如果有选中文本，则取消选中
		self.__relocateCursor()

	def __delRightWord( self ) :
		"""
		删除光标右边一个单词
		"""
		rsite = self.getLeftWordEnd( self.pyRText_.wtext )
		self.pyRText_.text = self.pyRText_.wtext[rsite:]
		self.__deselectText()											# 如果有选中文本，则取消选中
		self.__relocateCursor()

	# --------------------------------------
	# 编辑
	# --------------------------------------
	def __doCopy( self ) :
		"""
		复制
		"""
		if self.inputMode == InputMode.PASSWORD :			# 禁止复制密码
			return
		text = self.selectedText
		if text == "" : return
		csol.setClipboard( text )

	def __doCut( self ) :
		"""
		剪切
		"""
		if self.inputMode == InputMode.PASSWORD :			# 禁止剪切密码
			return
		selRng = self.__selRange
		if selRng == ( 0, 0 ) : return
		selText = self.selectedText							# 暂存选中文本
		self.__deleteSelectText()							# 删除选中文本
		csol.setClipboard( selText )						# 降选中文本放到粘贴版中
		self.onTextChanged_()								# 触发文本改变事件

	def __doPaste( self ) :
		"""
		粘贴
		"""
		if csol.getClipboard() == "" : return
		self.__deleteSelectText()							# 删除选中文本
		inputStr = csstring.toString( csol.getClipboard() )
		self.notifyInput( inputStr )						# 将粘贴版数据插入到文本框

	# -------------------------------------------------
	def __addChar( self, ch ) :
		"""
		在光标处添加一个字符
		"""
		if self.__validate( ch ) :							# 验证是否是可输入字符
			self.pyLText_.text += ch
			self.__relocateCursor()
			return True
		return False

	# ---------------------------------------
	def __deselectText( self ) :
		"""
		取消当前选定文本
		"""
		self.__selRange = ( 0, 0 )
		self.__pySelector.width = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabIn_( self ) :
		"""
		当获得焦点时被调用
		"""
		BaseInput.onTabIn_( self )
		self.moveCursorTo( self.wlength )

	def onTabOut_( self ) :
		"""
		当撤离焦点时被调用
		"""
		if self.pyCursor_.capped( self ) :
			self.pyLText_.text = self.text
			self.pyRText_.text = ""
			self.pyLText_.left = 0
			self.pyRText_.left = self.pyLText_.right
			self.__deselectText()
		BaseInput.onTabOut_( self )

	# -------------------------------------------------
	def showCursor_( self ) :
		"""
		显示光标
		"""
		BaseInput.showCursor_( self )
		self.pyCursor_.top = 2										# cursor's location of y-coordinate
		self.pyCursor_.height = self.height - 3						# cursor's height
		self.__relocateCursor()

	def isAllowInput_( self ) :
		"""
		指出当前是否允许输入
		"""
		if not BaseInput.isAllowInput_( self ) :
			return False
		if self.__readOnly : return False
		return True

	def keyInput_( self, key, mods ) :
		"""
		键盘输入
		"""
		if self.__moveCursor( key, mods ) :							# 作移动光标处理
			return True
		if self.__selectStr( key, mods ) :
			return True
		if self.__delSubStr( key, mods ) :							# 作删除字符处理
			self.onTextChanged_()
			return True
		if self.__edit( key, mods ) :
			return True
		if mods == 0 or mods == MODIFIER_SHIFT :
			if self.__input( key, mods ) :							# 输入字符
				self.onTextChanged_()
				return True
		return False

	# ---------------------------------------
	def onEnable_( self ) :
		"""
		有效时被调用
		"""
		BaseInput.onEnable_( self )
		self.pyLText_.color = self.__foreColor						# 恢复实效前的前景色
		self.pyRText_.color = self.__foreColor						# 恢复实效前的前景色

	def onDisable_( self ) :
		"""
		无效时被调用
		"""
		BaseInput.onDisable_( self )
		self.pyLText_.color = ( 128, 128, 128, 255 )
		self.pyRText_.color = ( 128, 128, 128, 255 )

	# -------------------------------------------------
	def onTextChanged_( self ) :
		"""
		文本改变时被调用
		"""
		self.onTextChanged()

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		"""
		鼠标左键按下时被调用
		"""
		BaseInput.onLMouseDown_( self, mods )
		if self.pyCursor_.capped( self ) :
			self.__setCursorToMouse()
			self.__deselectText()								# 清除原来的选中文本
			self.__tmpSelectStart = self.pyLText_.wlength 		# 记录下光标位置
			self.moveFocus = True								# 激活鼠标移动消息，以使得可以选中文本
			rds.uiHandlerMgr.capUI( self )
		return True

	def onLMouseUp_( self, mods ) :
		"""
		鼠标左键提起时被调用
		"""
		BaseInput.onLMouseUp_( self, mods )
		rds.uiHandlerMgr.uncapUI( self )
		self.moveFocus = False						# 取消鼠标移动消息
		return True

	def onMouseMove_( self, dx, dy ) :
		"""
		鼠标移动时被调用
		"""
		BaseInput.onMouseMove_( self, dx, dy )
		if not BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			return True
		self.__setCursorToMouse()
		start = self.__tmpSelectStart
		end = self.pyLText_.wlength
		self.select( start, end )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def notifyInput( self, text ) :
		"""
		在光标处插入一串字符
		"""
		if not self.isAllowInput_() : return
		wtext = csstring.toWideString( text )

		# 过滤掉不可输入的字符
		tmpText = ""
		for ch in wtext :
			if self.__validate( ch ) :
				tmpText += ch
		wtext = tmpText

		# 是否超出长度限制
		if self.__isSlopOver( len( wtext ) ) :
			count = self.maxLength - self.wlength
			wtext = wtext[: count]

		self.__deleteSelectText()
		text = csstring.toString( wtext )
		self.pyLText_.text += text
		self.__relocateCursor()
		self.onTextChanged_()

	def clear( self ) :
		"""
		清除所有文本
		"""
		self.__deselectText()										# 取消选中文本
		self.pyLText_.text = ""										# 清除光标左边的文本
		self.pyRText_.text = ""										# 清除光标有边的文本
		if self.pyCursor_.capped( self ) :
			self.pyCursor_.left = 0									# 重新设置光标位置

	# -------------------------------------------------
	def moveCursorTo( self, idx ) :
		"""
		移动光标到指定地方
		"""
		if not self.tabStop : return
		idx = max( 0, idx )
		idx = min( idx, self.wlength )
		wtext = self.wtext
		self.pyLText_.text = wtext[:idx]
		self.pyRText_.text = wtext[idx:]
		self.__relocateCursor()

	def select( self, start, end ) :
		"""
		选中指定文本
		"""
		start = max( 0, start )
		start = min( start, self.wlength )
		end = max( 0, end )
		end = min( end, self.wlength )
		self.__selRange = start, end
		if start == end :
			self.__deselectText()								# 取消选定文本
			self.moveCursorTo( start )
			return
		if self.pyCursor_.capped( self ) :
			self.moveCursorTo( start )
			if start < end :									# 向右选择
				left = self.pyCursor_.left
				self.moveCursorTo( end )
				right = self.pyCursor_.left
			else :												# 向左选择
				right = self.pyCursor_.right
				self.moveCursorTo( end )
				left = self.pyCursor_.right
			self.__pySelector.left = left
			self.__pySelector.width = right - left

	def selectAll( self ) :
		"""
		选中所有文本
		"""
		self.select( 0, self.wlength )

	# -------------------------------------------------
	def getTextesBesideCursor( self ) :
		"""
		获取光标左又两边的字符串，如果输入框没有焦点，则返回空串
		"""
		return self.pyLText_.text, self.pyRText_.text


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getInputMode( self ) :
		return self.pyLText_.inputMode

	def _setInputMode( self, mode ) :
		self.pyLText_.inputMode = mode
		self.pyRText_.inputMode = mode

	def _getPasswordChar( self ) :
		return self.__passwordChar

	def _setPasswordChar( self, ch ) :
		self.__passwordChar = ch

	# ---------------------------------------
	def _getFilterChars( self ) :
		return self.__filterChars

	def _setFilterChars( self, chars ) :
		"""
		set filter char
		"""
		self.__filterChars = chars

	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyLText_.text + self.pyRText_.text

	def _setText( self, text ) :
		self.clear()												# clear old text
		wtext = csstring.toWideString( text )
		textLen = len( wtext )
		if self.__maxLen > 0 :										# maxlength limitation
			textLen = min( textLen, self.__maxLen )					# remove the out side part
			text = wtext[0 : textLen]
		self.pyLText_.text = text
		self.pyLText_.left = 0
		self.__relocateCursor()
		self.onTextChanged_()

	def _getWideText( self ) :
		return csstring.toWideString( self.text )

	# ---------------------------------------
	def _getSelectedText( self ) :
		start, end = self.__selRange
		if start <= end :
			return csstring.toString( self.wtext[start : end] )
		return csstring.toString( self.wtext[end : start] )

	def _getWideSelectedText( self ) :
		start, end = self.__selRange
		if start <= end :
			return self.wtext[start : end]
		return self.wtext[end : start]

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyLText_.font

	def _setFont( self, font ) :
		self.pyLText_.font = font
		self.pyRText_.font = font
	
	def _getFontSize( self ):
		return self.pyLText_.fontSize
	
	def _setFontSize( self, fontSize ):
		self.pyLText_.fontSize = fontSize
		self.pyRText_.fontSize = fontSize

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.__foreColor

	def _setForeColor( self, color ) :
		self.__foreColor = color
		if self.enable :
			self.pyLText_.color = color
			self.pyRText_.color = color

	# ---------------------------------------
	def _getTextAlign( self ) :
		return self.__textAlign

	def _setTextAlign( self, anchor ) :
		self.__textAlign = anchor

	# ----------------------------------------------------------------
	def _getReadOnly( self ) :
		return self.__readOnly

	def _setReadOnly( self, isReadOnly ) :
		if self.tabStop :
			self.tabStop = False
		self.__readOnly = isReadOnly
		self.canTabIn = not isReadOnly

	# ---------------------------------------
	def _getMaxLength( self ) :
		return self.__maxLen

	def _setMaxLength( self, length ) :
		self.__maxLen = length

	# ---------------------------------------
	def _getLength( self ) :
		return len( self.text )

	def _getWLength( self ) :
		return len( self.wtext )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	inputMode = property( _getInputMode, _setInputMode )				# 获取/设置输入模式：
																		# ( uidefine.InputMode.COMMON uidefine.InputMode.PASSWORD,
																		# uidefine.InputMode.INTEGER, uidefine.InputMode.FLOAT )
	passwordChar = property( _getPasswordChar, _setPasswordChar )		# 获取/设置密码隐字符
	filterChars = property( _getFilterChars, _setFilterChars )			# 获取/设置过滤字符

	text = property( _getText, _setText )								# 获取/设置文本
	wtext = property( _getWideText )									# 获取宽字符串
	selectedText = property( _getSelectedText )							# 获取选中的文本
	wselectedText = property( _getWideSelectedText )					# 获取选中文本的宽字符串
	font = property( _getFont, _setFont )								# 获取/设置字体
	fontSize = property( _getFontSize, _setFontSize )								# 获取/设置字体大小
	foreColor = property( _getForeColor, _setForeColor )				# 获取/设置前景色
	textAlign = property( _getTextAlign, _setTextAlign )				# 获取/设置文本停靠方式( "LEFT"/"CENTER"/"RIGHT"，暂时无效 )

	readOnly = property( _getReadOnly, _setReadOnly )					# 获取/设置是否为只读
	maxLength = property( _getMaxLength, _setMaxLength )				# 获取/设置允许输入的最大长度
	length = property( _getLength )										# 获取文本长度
	wlength = property( _getWLength )									# 获取宽文本长度


# --------------------------------------------------------------------
# implement left or right label splited by cursor
# --------------------------------------------------------------------
class SegText( StaticText ) :
	def __init__( self ) :
		StaticText.__init__( self )

		self.__text = ""
		self.__inputMode = InputMode.COMMON
		self.__passwordChar = "*"

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def textWidth( self, text ) :
		"""
		获取文本宽度
		"""
		if self.__inputMode == InputMode.PASSWORD :
			sl = [self.__passwordChar for i in xrange( len( text ) )]
			text = "".join( sl )
		return StaticText.textWidth( self, text )


	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	def _getText( self ) :
		return csstring.toString( self.__text )

	def _setText( self, text ) :
		self.__text = text
		if self.__inputMode == InputMode.PASSWORD :
			sl = [self.__passwordChar for i in xrange( len( text ) )]
			text = "".join( sl )
		StaticText._setText( self, text )

	# ---------------------------------------
	def _getInputMode( self ) :
		return self.__inputMode

	def _setInputMode( self, mode ) :
		self.__inputMode = mode

	# ---------------------------------------
	def _getPasswordChar( self ) :
		return self.__passwordChar

	def _setPasswordChar( self, ch ) :
		self.__passwordChar = ch


	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	inputMode = property( _getInputMode, _setInputMode )
	passwordChar = property( _getPasswordChar, _setPasswordChar )
