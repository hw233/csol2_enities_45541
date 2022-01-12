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
		self.pyLText_ = SegText()									# �����ߵ��ı���ǩ
		self.pyRText_ = SegText()									# ����ұߵ��ı���ǩ
		self.__pySelector = PyGUI( util.copyGui( TextBox.__cg_selector ) )
		self.pyLText_.v_anchor = UIAnchor.MIDDLE
		self.pyRText_.v_anchor = UIAnchor.MIDDLE
		self.font = Font.defFont
		self.canTabIn = True
		self.__initialize( textBox )

		self.__readOnly = False										# �Ƿ���ֻ��
		self.__textAlign = "LEFT"									# ͣ����ʽ����ʱû�ã�
		self.__maxLen = -1											# ����������ı���󳤶�
		self.__filterChars = []										# �����ַ����ڸü����е��ַ����������룩
		self.__selRange = ( 0, 0 )									# ѡ���ı��ķ�Χ

		self.__foreColor = self.pyLText_.color						# ��ʱ��������¼�������Чǰ��ǰ��ɫ��
		self.__tmpSelectStart = 0									# ��ʱ��������¼ѡ���ı�����ʼλ�ã�

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
		���ı��ı�ʱ������
		"""
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __intValidate( self, ch ) :
		"""
		�Ƿ�����ֵ�ַ�
		"""
		if ch in "0123456789" : return True							# ch is number
		if ch in "+-" and self.pyLText_.text == "" and \
			ch not in self.text : 									# ch is������ or ������
				return True
		return False

	def __floatValidate( self, ch ) :
		"""
		�Ƿ��Ǹ����ַ�
		"""
		if ch in '0123456789' : return True							# ch is number
		if ch == '.' and ch not in self.text : return True			# ch is��.��
		if ch in "+-" and self.pyLText_.text == "" and \
			ch not in self.text :									# ch is������ or ������
				return True
		return False

	def __validate( self, ch ) :
		"""
		��֤�ַ��Ƿ�Ϸ�
		"""
		if ch in self.__filterChars :
			return False											# �����ַ�
		if self.inputMode == InputMode.COMMON :						# ��ͨģʽ
			return True
		if self.inputMode == InputMode.PASSWORD :					# ����ģʽ
			return True
		elif self.inputMode == InputMode.INTEGER :					# ����ģʽ
			return self.__intValidate( ch )
		elif self.inputMode == InputMode.FLOAT :					# ������ģʽ
			return self.__floatValidate( ch )
		elif self.inputMode == InputMode.NATURALNUM :				# ��Ȼ��
			if ch == "-" : return False
			return self.__intValidate( ch )
		return False

	# ---------------------------------------
	def __isSlopOver( self, addLen ) :
		"""
		�ַ��������Ƿ񳬳�����������ַ�������
		"""
		if self.__maxLen < 0 : return False
		newLen = self.wlength + addLen
		if newLen <= self.__maxLen : return False
		return True

	# ---------------------------------------
	def __relocateCursor( self ) :
		"""
		�������ù��λ��
		"""
		if self.pyCursor_.capped( self ) :
			left = self.pyLText_.right						# ����Ĭ�����
			right  = left + self.pyCursor_.width			# ����Ĭ���Ҿ�
			if left < 0 :									# ����������
				self.pyCursor_.left = 0
			elif right > self.width :						# ��������ұ�
				self.pyCursor_.right = self.width - 1
			else :
				self.pyCursor_.left = left
			self.pyLText_.right = self.pyCursor_.left
			self.pyRText_.left = self.pyCursor_.left

	# -------------------------------------------------
	def __setCursorToMouse( self ) :
		"""
		����궨λ����괦
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
		ɾ��ѡ���ı�
		"""
		start, end = self.__selRange
		if start == end : return False						# ��ǰû��ѡ���ı�
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
		ͨ�����̼����ƶ����
		"""
		if key == KEY_LEFTARROW and mods == 0 :
			self.__moveLeftChar()									# �����ƶ�һ���ַ�
			return True
		if key == KEY_RIGHTARROW and mods == 0 :
			self.__moveRightChar()									# �����ƶ�һ���ַ�
			return True
		if key == KEY_LEFTARROW and mods == MODIFIER_CTRL :
			self.__moveLeftWord()									# �����ƶ�һ������
			return True
		if key == KEY_RIGHTARROW and mods == MODIFIER_CTRL :
			self.__moveRightWord()									# �����ƶ�һ������
			return True
		if key == KEY_HOME and mods == 0 :
			self.__moveToLeft()										# ������ƶ����ı���ǰ��
			return True
		if key == KEY_END and mods == 0 :
			self.__moveToRight()									# ������ƶ����ı������
			return True
		return False

	def __selectStr( self, key, mods ) :
		"""
		ͨ��������ѡ��һ���ı�
		"""
		if key == KEY_LEFTARROW and mods == MODIFIER_SHIFT :
			self.__selectLeftChar()									# ѡ�й������һ���ַ�
			return True
		if key == KEY_RIGHTARROW and mods == MODIFIER_SHIFT :
			self.__selectRightChar()								# ѡ�й���ұ�һ���ַ�
			return True
		if key == KEY_LEFTARROW and mods == MODIFIER_CTRL | MODIFIER_SHIFT :
			self.__selectLeftWord()									# ѡ�й����ߵ�һ������
			return True
		if key == KEY_RIGHTARROW and mods == MODIFIER_CTRL | MODIFIER_SHIFT :
			self.__selectRightWord()				 				# ѡ�й���ұߵ�һ������
			return True
		if key == KEY_HOME and mods == MODIFIER_SHIFT :
			self.__selectLeftAll()									# ѡ�й����ߵ��ı�
			return True
		if key == KEY_END and mods == MODIFIER_SHIFT :
			self.__selectRightAll()									# ѡ�й���бߵ��ı�
			return True
		return False

	def __delSubStr( self, key, mods ) :
		"""
		ͨ������ɾ��һ���Ӵ�
		"""
		if key == KEY_BACKSPACE and mods == 0 :
			self.__delLeftChar()									# ɾ���������һ���ַ�
			return True
		if key == KEY_DELETE and mods == 0 :
			self.__delRightChar()									# ɾ������ұ�һ���ַ�
			return True
		if key == KEY_BACKSPACE and mods == MODIFIER_CTRL :
			self.__delLeftWord()									# ɾ�������ߵ�һ������
			return True
		if key == KEY_DELETE and mods == MODIFIER_CTRL :
			self.__delRightWord()					 				# ɾ������ұߵ�һ������
			return True
		return False

	def __edit( self, key, mods ) :
		"""
		ͨ����ݼ��༭
		"""
		if key == keys.KEY_C and mods == keys.MODIFIER_CTRL :		# �� CTRL + C ����
			self.__doCopy()
			return True
		if key == keys.KEY_X and mods == keys.MODIFIER_CTRL :		# �� CTRL + V �����
			self.__doCut()
			return True
		if key == keys.KEY_V and mods == keys.MODIFIER_CTRL :		# �� CTRL + V ��ճ��ճ��������
			self.__doPaste()
			return True
		return False

	def __input( self, key, mods ) :
		"""
		ͨ����������һ���ַ�
		"""
		ch = KeyCharParser.keyToChar( key, mods == MODIFIER_SHIFT )
		if ch != '' :
			self.__deleteSelectText()								# ��ɾ��ѡ���ı�
			if self.__isSlopOver( 1 ) :								# �����˿��������󳤶�
				return True
			return self.__addChar( ch )
		return False

	# -------------------------------------------------
	# �ƶ����
	# -------------------------------------------------
	def __moveLeftChar( self ) :
		"""
		�����������һ���ַ�
		"""
		start, end = self.__selRange
		if start < end :									# �����ǰ��ѡ���ı�������������ѡ��
			self.moveCursorTo( start )						# ����ص�ѡ���ı��������
		elif start == end :									# �����ǰû��ѡ���ı�
			self.moveCursorTo( self.pyLText_.wlength - 1 )	# ���������ƶ�һ���ַ��Ŀ��
		self.__deselectText()								# ȥ��ѡ���ı���ѡ��״̬

	def __moveRightChar( self ) :
		"""
		�����������һ���ַ�
		"""
		start, end = self.__selRange
		if start > end :									# �����ǰ��ѡ���ı�������������ѡ��
			self.moveCursorTo( start )						# ����ص�ѡ���ı��������
		elif start == end :									# �����ǰû��ѡ���ı�
			self.moveCursorTo( self.pyLText_.wlength + 1 )	# ���������ƶ�һ���ַ��Ŀ��
		self.__deselectText()								# ȥ��ѡ���ı���ѡ��״̬

	def __moveLeftWord( self ) :
		"""
		�����ƶ�һ������
		"""
		site = self.getRightWordStart( self.pyLText_.wtext )
		self.moveCursorTo( site )
		self.__deselectText()

	def __moveRightWord( self ) :
		"""
		�����ƶ�һ������
		"""
		rsite = self.getLeftWordEnd( self.pyRText_.wtext )
		self.moveCursorTo( self.pyLText_.wlength + rsite )
		self.__deselectText()

	def __moveToLeft( self ) :
		"""
		������ƶ��������
		"""
		self.moveCursorTo( 0 )
		self.__deselectText()

	def __moveToRight( self ) :
		self.moveCursorTo( self.wlength )
		self.__deselectText()

	# --------------------------------------
	# ѡ���Ӵ�
	# --------------------------------------
	def __selectLeftChar( self ) :
		"""
		ѡ�й����ߵ�һ���ַ�
		"""
		start, end = self.__selRange
		if start == end :							# ��ǰû��ѡ���ı�
			start = self.pyLText_.wlength
			end = start - 1
		else :										# ��ǰ��ѡ���ı�
			end -= 1
		self.select( start, end )

	def __selectRightChar( self ) :
		"""
		ѡ�й���бߵ�һ���ַ�
		"""
		start, end = self.__selRange
		if start == end :							# ��ǰû��ѡ���ı�
			start = self.pyLText_.wlength
			end = start + 1
		else :										# ��ǰ��ѡ���ı�
			end += 1
		self.select( start, end )

	def __selectLeftWord( self ) :
		"""
		ѡ�й�����һ������
		"""
		start, end = self.__selRange
		if start == end :							# ��ǰû��ѡ���ı�
			start = self.pyLText_.wlength
		site = self.getRightWordStart( self.pyLText_.wtext )
		self.select( start, site )

	def __selectRightWord( self ) :
		"""
		ѡ�й���б�һ������
		"""
		start, end = self.__selRange
		if start == end :							# ��ǰû��ѡ���ı�
			start = self.pyLText_.wlength
		rsite = self.getLeftWordEnd( self.pyRText_.wtext )
		self.select( start, self.pyLText_.wlength + rsite )

	def __selectLeftAll( self ) :
		"""
		ѡ�й����ߵ�ȫ���ı�
		"""
		start, end = self.__selRange
		if start == end :							# ��ǰû��ѡ���ı�
			start = self.pyLText_.wlength
		self.select( start, 0 )

	def __selectRightAll( self ) :
		"""
		ѡ�й���бߵ�ȫ���ı�
		"""
		start, end = self.__selRange
		if start == end :							# ��ǰû��ѡ���ı�
			start = self.pyLText_.wlength
		self.select( start, self.wlength )

	# --------------------------------------
	# ɾ���ַ�
	# --------------------------------------
	def __delLeftChar( self ) :
		"""
		ɾ��������һ���ַ�
		"""
		if self.__deleteSelectText() :									# �����ѡ���ı���ɾ��ѡ���ı�
			return
		self.pyLText_.text = self.pyLText_.wtext[:-1]
		self.__relocateCursor()

	def __delRightChar( self ) :
		"""
		ɾ������ұ�һ���ַ�
		"""
		if self.__deleteSelectText() :									# �����ѡ���ı���ɾ��ѡ���ı�
			return
		self.pyRText_.text = self.pyRText_.wtext[1:]
		self.__relocateCursor()

	def __delLeftWord( self ) :
		"""
		ɾ��������һ������
		"""
		text = self.pyLText_.text
		newText = text.rstrip()
		if text == newText :											# ���������û�пո�
			site = self.getRightWordStart( self.pyLText_.wtext )		# ���ȡ�����ߵ�һ������
			self.pyLText_.text = self.pyLText_.wtext[:site]				# ɾ���õ���
		else :															# ����
			self.pyLText_.text = newText								# ����ɾ���ո�
		self.__deselectText()											# �����ѡ���ı�����ȡ��ѡ��
		self.__relocateCursor()

	def __delRightWord( self ) :
		"""
		ɾ������ұ�һ������
		"""
		rsite = self.getLeftWordEnd( self.pyRText_.wtext )
		self.pyRText_.text = self.pyRText_.wtext[rsite:]
		self.__deselectText()											# �����ѡ���ı�����ȡ��ѡ��
		self.__relocateCursor()

	# --------------------------------------
	# �༭
	# --------------------------------------
	def __doCopy( self ) :
		"""
		����
		"""
		if self.inputMode == InputMode.PASSWORD :			# ��ֹ��������
			return
		text = self.selectedText
		if text == "" : return
		csol.setClipboard( text )

	def __doCut( self ) :
		"""
		����
		"""
		if self.inputMode == InputMode.PASSWORD :			# ��ֹ��������
			return
		selRng = self.__selRange
		if selRng == ( 0, 0 ) : return
		selText = self.selectedText							# �ݴ�ѡ���ı�
		self.__deleteSelectText()							# ɾ��ѡ���ı�
		csol.setClipboard( selText )						# ��ѡ���ı��ŵ�ճ������
		self.onTextChanged_()								# �����ı��ı��¼�

	def __doPaste( self ) :
		"""
		ճ��
		"""
		if csol.getClipboard() == "" : return
		self.__deleteSelectText()							# ɾ��ѡ���ı�
		inputStr = csstring.toString( csol.getClipboard() )
		self.notifyInput( inputStr )						# ��ճ�������ݲ��뵽�ı���

	# -------------------------------------------------
	def __addChar( self, ch ) :
		"""
		�ڹ�괦���һ���ַ�
		"""
		if self.__validate( ch ) :							# ��֤�Ƿ��ǿ������ַ�
			self.pyLText_.text += ch
			self.__relocateCursor()
			return True
		return False

	# ---------------------------------------
	def __deselectText( self ) :
		"""
		ȡ����ǰѡ���ı�
		"""
		self.__selRange = ( 0, 0 )
		self.__pySelector.width = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabIn_( self ) :
		"""
		����ý���ʱ������
		"""
		BaseInput.onTabIn_( self )
		self.moveCursorTo( self.wlength )

	def onTabOut_( self ) :
		"""
		�����뽹��ʱ������
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
		��ʾ���
		"""
		BaseInput.showCursor_( self )
		self.pyCursor_.top = 2										# cursor's location of y-coordinate
		self.pyCursor_.height = self.height - 3						# cursor's height
		self.__relocateCursor()

	def isAllowInput_( self ) :
		"""
		ָ����ǰ�Ƿ���������
		"""
		if not BaseInput.isAllowInput_( self ) :
			return False
		if self.__readOnly : return False
		return True

	def keyInput_( self, key, mods ) :
		"""
		��������
		"""
		if self.__moveCursor( key, mods ) :							# ���ƶ���괦��
			return True
		if self.__selectStr( key, mods ) :
			return True
		if self.__delSubStr( key, mods ) :							# ��ɾ���ַ�����
			self.onTextChanged_()
			return True
		if self.__edit( key, mods ) :
			return True
		if mods == 0 or mods == MODIFIER_SHIFT :
			if self.__input( key, mods ) :							# �����ַ�
				self.onTextChanged_()
				return True
		return False

	# ---------------------------------------
	def onEnable_( self ) :
		"""
		��Чʱ������
		"""
		BaseInput.onEnable_( self )
		self.pyLText_.color = self.__foreColor						# �ָ�ʵЧǰ��ǰ��ɫ
		self.pyRText_.color = self.__foreColor						# �ָ�ʵЧǰ��ǰ��ɫ

	def onDisable_( self ) :
		"""
		��Чʱ������
		"""
		BaseInput.onDisable_( self )
		self.pyLText_.color = ( 128, 128, 128, 255 )
		self.pyRText_.color = ( 128, 128, 128, 255 )

	# -------------------------------------------------
	def onTextChanged_( self ) :
		"""
		�ı��ı�ʱ������
		"""
		self.onTextChanged()

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		"""
		����������ʱ������
		"""
		BaseInput.onLMouseDown_( self, mods )
		if self.pyCursor_.capped( self ) :
			self.__setCursorToMouse()
			self.__deselectText()								# ���ԭ����ѡ���ı�
			self.__tmpSelectStart = self.pyLText_.wlength 		# ��¼�¹��λ��
			self.moveFocus = True								# ��������ƶ���Ϣ����ʹ�ÿ���ѡ���ı�
			rds.uiHandlerMgr.capUI( self )
		return True

	def onLMouseUp_( self, mods ) :
		"""
		����������ʱ������
		"""
		BaseInput.onLMouseUp_( self, mods )
		rds.uiHandlerMgr.uncapUI( self )
		self.moveFocus = False						# ȡ������ƶ���Ϣ
		return True

	def onMouseMove_( self, dx, dy ) :
		"""
		����ƶ�ʱ������
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
		�ڹ�괦����һ���ַ�
		"""
		if not self.isAllowInput_() : return
		wtext = csstring.toWideString( text )

		# ���˵�����������ַ�
		tmpText = ""
		for ch in wtext :
			if self.__validate( ch ) :
				tmpText += ch
		wtext = tmpText

		# �Ƿ񳬳���������
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
		��������ı�
		"""
		self.__deselectText()										# ȡ��ѡ���ı�
		self.pyLText_.text = ""										# ��������ߵ��ı�
		self.pyRText_.text = ""										# �������бߵ��ı�
		if self.pyCursor_.capped( self ) :
			self.pyCursor_.left = 0									# �������ù��λ��

	# -------------------------------------------------
	def moveCursorTo( self, idx ) :
		"""
		�ƶ���굽ָ���ط�
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
		ѡ��ָ���ı�
		"""
		start = max( 0, start )
		start = min( start, self.wlength )
		end = max( 0, end )
		end = min( end, self.wlength )
		self.__selRange = start, end
		if start == end :
			self.__deselectText()								# ȡ��ѡ���ı�
			self.moveCursorTo( start )
			return
		if self.pyCursor_.capped( self ) :
			self.moveCursorTo( start )
			if start < end :									# ����ѡ��
				left = self.pyCursor_.left
				self.moveCursorTo( end )
				right = self.pyCursor_.left
			else :												# ����ѡ��
				right = self.pyCursor_.right
				self.moveCursorTo( end )
				left = self.pyCursor_.right
			self.__pySelector.left = left
			self.__pySelector.width = right - left

	def selectAll( self ) :
		"""
		ѡ�������ı�
		"""
		self.select( 0, self.wlength )

	# -------------------------------------------------
	def getTextesBesideCursor( self ) :
		"""
		��ȡ����������ߵ��ַ�������������û�н��㣬�򷵻ؿմ�
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
	inputMode = property( _getInputMode, _setInputMode )				# ��ȡ/��������ģʽ��
																		# ( uidefine.InputMode.COMMON uidefine.InputMode.PASSWORD,
																		# uidefine.InputMode.INTEGER, uidefine.InputMode.FLOAT )
	passwordChar = property( _getPasswordChar, _setPasswordChar )		# ��ȡ/�����������ַ�
	filterChars = property( _getFilterChars, _setFilterChars )			# ��ȡ/���ù����ַ�

	text = property( _getText, _setText )								# ��ȡ/�����ı�
	wtext = property( _getWideText )									# ��ȡ���ַ���
	selectedText = property( _getSelectedText )							# ��ȡѡ�е��ı�
	wselectedText = property( _getWideSelectedText )					# ��ȡѡ���ı��Ŀ��ַ���
	font = property( _getFont, _setFont )								# ��ȡ/��������
	fontSize = property( _getFontSize, _setFontSize )								# ��ȡ/���������С
	foreColor = property( _getForeColor, _setForeColor )				# ��ȡ/����ǰ��ɫ
	textAlign = property( _getTextAlign, _setTextAlign )				# ��ȡ/�����ı�ͣ����ʽ( "LEFT"/"CENTER"/"RIGHT"����ʱ��Ч )

	readOnly = property( _getReadOnly, _setReadOnly )					# ��ȡ/�����Ƿ�Ϊֻ��
	maxLength = property( _getMaxLength, _setMaxLength )				# ��ȡ/���������������󳤶�
	length = property( _getLength )										# ��ȡ�ı�����
	wlength = property( _getWLength )									# ��ȡ���ı�����


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
		��ȡ�ı����
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
