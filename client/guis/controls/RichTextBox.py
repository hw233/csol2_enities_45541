# -*- coding: gb18030 -*-
#

"""
implement richtext box class��

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

		self.__escTPLs = []							# ת��ģ��
		self.pyElems_ = []							# �����ı�Ԫ��
		self.__wtext = csstring.toWideString( "" )	# �ı��Ŀ��ַ���ʽ
		self.__readOnly = False						# �Ƿ���ֻ��
		self.__curSiteInfo = SiteInfo( 0, 0 )		# ���λ��

		self.__font = Font.defFont					# Ĭ������
		self.__fontSize = Font.defFontSize			# Ĭ�������С
		self.__charSpace = Font.defCharSpace		# �ּ��
		self.__limning = Font.defLimning			# �����ʽ
		self.__limnColor = Font.defLimnColor		# �����ɫ

		self.__foreColor = ( 255, 255, 255, 255 )	# Ĭ����ɫ
		self.__vTextAlgin = "BOTTOM"				# ��ֱ�������ı��Ķ��뷽ʽ��"TOP" / "MIDDLE" / "BOTTOM"
		self.__viewLen = 0							# �����ı��ֽ���
		self.__wviewLen = 0							# �����ı�����
		self.__maxLen = -1							# �������������ַ�����0 ��ʾ���������ⳤ( ע�⣺���Ǳ����ı��ĳ��� )
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
		���ı��ı�ʱ������
		"""
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		"""
		��ʼ��
		"""
		self.__selector = Selector( self.__fontSize )
		pyFirst = EFirst()
		pyLast = ELast()
		self.__linkBorderElems( pyFirst, pyLast )
		self.pyElems_ = [pyFirst, pyLast]

	def __clearText( self ) :
		"""
		��������ı�
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
		�����������ڵ�Ԫ��
		"""
		pyFore.setNextElem_( pyNext )
		pyNext.setForeElem_( pyFore )

	def __resizeCursor( self ) :
		"""
		�������ù���С
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
		��ȡ����ת������
		"""
		scopes = {}
		def wellhandled( start ) :							# �Ƿ�ת�崦���
			for s, ( e, clsElem ) in scopes.iteritems() :
				if s <= start < e :
					return True
			return False

		for tpl, clsElem in self.__escTPLs :				# �ҳ�����ת���
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
		�����ı�������Ԫ��
		"""
		self.__clearText()
		self.__wtext = wtext							# ������ı�
		scopes = self.__getTextScopes( wtext )			# ��ȡ���о߱�ת������������
		starts = sorted( scopes.keys() )				# ��������������ʼλ�ã���С��������

		if self.__vTextAlgin == "TOP" :					# �ı���������
			aname = "top"
			y = 1
		elif self.__vTextAlgin == "MIDDLE" :			# �ı��м����
			aname = "middle"
			y = self.height * 0.5
		else :
			aname = "bottom"							# �ı��ײ�����
			y = self.height - 1

		count = len( wtext )							# �ı��ַ�����
		left = 0
		index = 0
		pyFore = self.pyElems_[0]						# ��ʱ��¼ǰһ��Ԫ��
		pyLast = self.pyElems_.pop()					# ���һ��Ԫ��
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
			pyElem = clsElem.getInst( start, text )		# ����Ԫ��
			if pyElem is None :							# ����Ԫ��ʱ����ʧ��
				pyElem = EDefText( start, text )		# �ô��ı���ʾ
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
		����λ���ҳ�����Ӧ��Ԫ��
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
		��ȡָ����ദ��Ԫ��
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
		��ȡĳ���������ڵ�����Ԫ��
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
		���ݸ���������������ָ����������������������ʢ�Ź��ĵط��������
		��Ϊ�ƶ����ʱ����ЩԪ����Ҫ���鱻��Խ������겻��ͣ����Ԫ�ص��м�
		���أ�SiteInfo( site, left )
		"""
		pyElem = self.__getElemOfSite( site )
		return pyElem.getSiteInfoViaSite( site )

	def __getSiteInfoViaLeft( self, left ) :
		"""
		���ݸ�������࣬����ָ����������������������ʢ�Ź��ĵط��������
		��Ϊ�ƶ����ʱ����ЩԪ����Ҫ���鱻��Խ������겻��ͣ����Ԫ�ص��м�
		���أ�SiteInfo( site, left )
		"""
		pyElem = self.__getElemOfLeft( left )
		return pyElem.getSiteInfoViaLeft( left )

	# ---------------------------------------
	def __getEndSiteInfo( self ) :
		"""
		��ȡ�ı�����λ����Ϣ
		"""
		pyElem = self.pyElems_[-1]
		return SiteInfo( pyElem.end, pyElem.right )

	# -------------------------------------------------
	def __setCursorSite( self, siteInfo ) :
		"""
		���ù��λ��
		"""
		self.__curSiteInfo = siteInfo
		left = siteInfo.left
		self.pyCursor_.left = left

		right = self.pyCursor_.right + 1
		maxScroll = self.gui.maxScroll
		scroll = self.gui.scroll
		if right - scroll.x > self.width :		# ���λ�ó����ؼ�����
			x = right - self.width
			maxScroll.x = x						# ���ı���ǰ����ʹ�ù��ͣ���ڿؼ�ĩ��
			scroll.x = x
		elif left < scroll.x :					# ��������˿ؼ�ǰ��
			x = left - self.cc_end_skip_width
			maxScroll.x = x						# ���ı�������
			scroll.x = x


	# -------------------------------------------------
	# �ƶ����
	# -------------------------------------------------
	def __moveLeftChar( self ) :
		"""
		�����������һ���ַ�
		"""
		if self.__selector.selected :
			return self.__selector.minSiteInfo
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftChar( site )

	def __moveRightChar( self ) :
		"""
		�����������һ���ַ�
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightChar( site )

	def __moveLeftWord( self ) :
		"""
		�����ƶ�һ������
		"""
		site = self.__curSiteInfo.site
		if self.__selector.selected :
			site = self.__selector.minSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftWord( site )

	def __moveRightWord( self ) :
		"""
		�����ƶ�һ������
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightWord( site )

	def __moveLeftAll( self ) :
		"""
		������Ƶ���ʼ��
		"""
		return SiteInfo( 0, 0 )

	def __moveRightAll( self ) :
		"""
		������ƶ�����ĩ��
		"""
		return self.__getEndSiteInfo()

	# ---------------------------------------
	def __moveCursor( self, key, mods ) :
		"""
		ͨ�����̼����ƶ����
		"""
		handlers = {
			( KEY_LEFTARROW, 0 )				: self.__moveLeftChar,		# ���ǰ��һ���ַ�
			( KEY_RIGHTARROW, 0 )				: self.__moveRightChar,		# ������һ���ַ�
			( KEY_LEFTARROW, MODIFIER_CTRL )	: self.__moveLeftWord,		# ���ǰ��һ������
			( KEY_RIGHTARROW, MODIFIER_CTRL )	: self.__moveRightWord,		# ������һ������
			( KEY_HOME, 0 )						: self.__moveLeftAll,		# ����Ƶ���ǰ��
			( KEY_END, 0 )						: self.__moveRightAll,		# ����Ƶ������
			}
		if ( key, mods ) in handlers :
			self.cancelSelect()
			siteInfo = handlers[( key, mods )]()
			self.__setCursorSite( siteInfo )
			return True
		return False


	# -------------------------------------------------
	# ɾ���ı�
	# -------------------------------------------------
	def __delLeftChar( self ) :
		"""
		ɾ��������һ���ַ�
		"""
		endInfo = self.__curSiteInfo
		endSite = endInfo.site
		pyElem = self.__getElemOfSite( endSite )
		startInfo = pyElem.skipLeftChar( endSite )
		return startInfo, endInfo

	def __delRightChar( self ) :
		"""
		ɾ������ұ�һ���ַ�
		"""
		startInfo = self.__curSiteInfo
		startSite = startInfo.site
		pyElem = self.__getElemOfSite( startSite )
		endInfo = pyElem.skipRightChar( startSite )
		return startInfo, endInfo

	def __delLeftWord( self ) :
		"""
		ɾ��������һ������
		"""
		endInfo = self.__curSiteInfo
		endSite = endInfo.site
		pyElem = self.__getElemOfSite( endSite )
		startInfo = pyElem.skipLeftWord( endSite )
		return startInfo, endInfo

	def __delRightWord( self ) :
		"""
		ɾ������ұ�һ������
		"""
		startInfo = self.__curSiteInfo
		startSite = startInfo.site
		pyElem = self.__getElemOfSite( startSite )
		endInfo = pyElem.skipRightWord( startSite )
		return startInfo, endInfo

	# ---------------------------------------
	def __delScopeText( self, startInfo, endInfo ) :
		"""
		ɾ��ָ�������ڵ��ı�
		"""
		start = startInfo.site
		end = endInfo.site
		wtext = self.__wtext
		self.__setTextElements( wtext[:start] + wtext[end:] )
		self.__setCursorSite( startInfo )

	def __delSubStr( self, key, mods ) :
		"""
		ͨ������ɾ��һ���Ӵ�
		"""
		if self.__readOnly :
			return False

		handlers = {
			( KEY_BACKSPACE, 0 )			: self.__delLeftChar,		# ɾ�����ǰһ���ַ�
			( KEY_DELETE, 0 )				: self.__delRightChar,		# ɾ������һ���ַ�
			( KEY_BACKSPACE, MODIFIER_CTRL ): self.__delLeftWord,		# ɾ�������ߵ�һ������
			( KEY_DELETE, MODIFIER_CTRL )	: self.__delRightWord,		# ɾ������ұߵ�һ������
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
	# �����ı�
	# -------------------------------------------------
	def __getSelectWViewLen( self ) :
		"""
		��ȡѡ���ı��Ŀ��ӳ���
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
		�ڹ�괦�����ı�
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
		if maxLen > 0 :												# ���ı���������
			currCount = self.wviewLength							# ��ǰ�ı�����
			selCount = self.__getSelectWViewLen()					# ѡ���ı�����
			leaveCount = max( 0, maxLen - currCount + selCount )	# ������������ٸ���
			if count > 0 :
				if count > leaveCount :								# ��ӵ��ı���������󳤶�����
					return
			elif addCount > leaveCount :
				addedWText = addedWText[:leaveCount]				# ��ȡ������������
				addCount = leaveCount
		wtext = self.__wtext
		newWText = wtext[:start] + addedWText + wtext[end:]			# ��������ı�
		self.__setTextElements( newWText )
		siteInfo = self.__getSiteInfoViaSite( start + addCount )
		self.__setCursorSite( siteInfo )
		self.cancelSelect()
		self.onTextChanged_()

	# ---------------------------------------
	def __input( self, key, mods ) :
		"""
		ͨ����������һ���ַ�
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
	# ѡ���ı�
	# -------------------------------------------------
	def __selectLeftChar( self ) :
		"""
		ѡ�й��ǰһ���ַ�
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftChar( site )

	def __selectRightChar( self ) :
		"""
		ѡ�й���һ���ַ�
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightChar( site )

	def __selectLeftWord( self ) :
		"""
		ѡ�й��ǰһ������
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipLeftWord( site )

	def __selectRightWord( self ) :
		"""
		ѡ�й���һ������
		"""
		site = self.__curSiteInfo.site
		pyElem = self.__getElemOfSite( site )
		return pyElem.skipRightWord( site )

	def  __selectLeftAll( self ) :
		"""
		ѡ�й��ǰ�������ı�
		"""
		return SiteInfo( 0, 0 )

	def __selectRightAll( self ) :
		"""
		ѡ�й���������ı�
		"""
		return self.__getEndSiteInfo()

	# ---------------------------------------
	def __keySelectText( self, key, mods ) :
		"""
		���̰���ѡ���ı�
		"""
		if key == KEY_A and mods == MODIFIER_CTRL :
			self.selectAll()
			return True

		handlers = {
			( KEY_LEFTARROW, MODIFIER_SHIFT )					: self.__selectLeftChar,		# ѡ�й��ǰһ���ַ�
			( KEY_RIGHTARROW, MODIFIER_SHIFT )					: self.__selectRightChar,		# ѡ�й���һ���ַ�
			( KEY_LEFTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectLeftWord,		# ѡ�й��ǰһ������
			( KEY_RIGHTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectRightWord,		# ѡ�й���һ������
			( KEY_HOME, MODIFIER_SHIFT )						: self.__selectLeftAll,			# ѡ�й��ǰ�������ı�
			( KEY_END, MODIFIER_SHIFT )							: self.__selectRightAll,		# ѡ�й���������ı�
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
	# �༭�ı�
	# -------------------------------------------------
	def __copy( self ) :
		"""
		�����ı�
		"""
		text = self.selectText
		if len( text ) > 0 :
			csol.setClipboard( text )

	def __cut( self ) :
		"""
		�����ı�
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
		ճ���ı�
		"""
		if self.__readOnly : return
		text = csol.getClipboard()
		if text == "" : return
		self.__insertText( text )

	# ---------------------------------------
	def __keyEditText( self, key, mods ) :
		"""
		�����༭�ı�
		"""
		handlers = {
			( KEY_C, MODIFIER_CTRL )	: self.__copy,		# ����
			( KEY_X, MODIFIER_CTRL )	: self.__cut,		# ����
			( KEY_V, MODIFIER_CTRL )	: self.__paste,		# ճ��
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
		��ý���ʱ������
		"""
		self.showCursor_()
		BaseInput.onTabIn_( self )
		self.__resizeCursor()
		self.__setCursorSite( self.__curSiteInfo )

	def onLMouseDown_( self, mods ) :
		"""
		����������ʱ������
		"""
		BaseInput.onLMouseDown_( self, mods )
		if not self.tabStop :
			self.tabStop = True
		left = self.mousePos[0]								# ���λ��
		left += self.gui.scroll.x
		siteInfo = self.__getSiteInfoViaLeft( left )		# ����������λ�ú����
		self.__setCursorSite( siteInfo )					# ��������ʵ��λ��
		self.__selector.beginSelecting( siteInfo )			# ��ʼѡ���ı�
		rds.uiHandlerMgr.capUI( self )						# ׼��ѡ���ı�
		return True

	def onLMouseUp_( self, mods ) :
		"""
		����������ʱ������
		"""
		self.__selector.endSelecting()
		rds.uiHandlerMgr.uncapUI( self )
		BaseInput.onLMouseUp_( self, mods )
		return True

	def onMouseMove_( self, dx, dy ) :
		"""
		����ƶ�ʱ������
		"""
		if self.__selector.selecting :
			startInfo = self.__selector.startSiteInfo
			left = self.mousePos[0]
			left += self.gui.scroll.x							# ���֮ǰ��λ��
			endInfo = self.__getSiteInfoViaLeft( left )
			self.__setCursorSite( endInfo )						# ����������λ��
			self.__selector.select( self, startInfo, endInfo )
			BaseInput.onMouseMove_( self, dx, dy )
			return True
		return BaseInput.onMouseMove_( self, dx, dy )

	def onKeyDown_( self, key, mods ) :
		"""
		���̰�������ʱ������
		"""
		if key == KEY_ESCAPE and self.__selector.selected :
			self.cancelSelect()
			return True
		return BaseInput.onKeyDown_( self, key, mods )

	# ---------------------------------------
	def onTextChanged_( self ) :
		"""
		�ı��ı��Ǳ�����
		"""
		self.onTextChanged()

	# -------------------------------------------------
	def keyInput_( self, key, mods ) :
		"""
		���հ�������
		"""
		if self.__moveCursor( key, mods ) :			# ���ƶ���괦��
			return True
		if self.__delSubStr( key, mods ) :			# ��ɾ���ַ�����
			return True
		if self.__keySelectText( key, mods ) :		# ����ѡ���ı�
			return True
		if self.__keyEditText( key, mods ) :		# �༭�ı�
			return True
		if mods == 0 or mods == MODIFIER_SHIFT :
			if self.__input( key, mods ) :			# �����ַ�
				return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setEscTemplates( self, tpls ) :
		"""
		����ת��ģ��
		@type				tpl		: re._sre.SRE_Pattern
		@param				tpl		: ת��ģ��
		@type				clsElem : class
		@param				clsElem : BaseElement
		"""
		self.__escTPLs = tpls
		self._setText( self.__wtext )

	def clearTemplates( self ) :
		"""
		�������ģ��
		"""
		self.__escTPLs = []
		self._setText( self.__wtext )

	# -------------------------------------------------
	def notifyInput( self, text, count = 0 ) :
		"""
		�ڹ�괦����
		count ��ʾ text �����εĿ��ӳ��ȣ����Ϊ 0 ���ʾʹ��
		text ��ʵ�ʳ�����ȷ���ı������Ƿ񳬳� __maxLen ����
		"""
		if text == "" : return
		if self.__readOnly : return
		self.__insertText( text, count )

	def clear( self ) :
		"""
		��������ı�
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
		ѡ���ı�
		"""
		startInfo = self.__getSiteInfoViaSite( start )
		endInfo = self.__getSiteInfoViaSite( end )
		self.__selector.select( self, startInfo, endInfo )

	def selectAll( self ) :
		"""
		ѡ��ȫ���ı�
		"""
		self.select( 0, self.wlength )

	def cancelSelect( self ) :
		"""
		ȡ��ѡ��
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
	text = property( lambda self : csstring.toString( self.__wtext ), _setText )		# ��ȡ/����ԭʼ�ı�
	wtext = property( lambda self : self.__wtext )										# ��ȡԭʼ�ı��Ŀ��ı���ʽ
	viewText = property( lambda self : csstring.toString( self._getWViewText() ) )		# ��ȡ�����ı�
	wviewText = property( _getWViewText )												# ��ȡ�����ı��Ŀ��ı���ʽ
	selectText = property( lambda self : csstring.toString( self._getWSelectText() ) )	# ��ȡѡ���ı�
	wselectText = property( _getWSelectText )											# ��ȡѡ���ı��Ŀ��ַ���ʽ
	length = property( lambda self : len( self.text ) )									# ��ȡ�ı������ַ���
	wlength = property( lambda self : len( self.__wtext ) )								# ��ȡ�ı�����������
	viewLength = property( lambda self : self.__viewLen )								# ��ȡ�����ı����ַ���
	wviewLength = property( lambda self : self.__wviewLen )								# ��ȡ�����ı�������
	maxLength = property( lambda self : self.__maxLen, _setMaxLen )						# ��ȡ/��������������ַ�����ע�⣺���Ǳ����ı����ַ�����
	readOnly = property( lambda self : self.__readOnly, _setReadOnly )					# ��ȡ�����Ƿ�ֻ��
	font = property( lambda self : self.__font, _setFont )								# ��ȡ/��������
	fontSize = property( lambda self : self.__fontSize, _setFontSize )					# ��ȡ����߶�
	charSpace = property( lambda self : self.__charSpace, _setCharSpace )				# ��ȡ/�����ּ��
	limning = property( lambda self : self.__limning, _setLimning )						# ��ȡ/���������ʽ
	limnColor = property( lambda self : self.__limnColor, _setLimnColor )				# ��ȡ/���������ɫ
	foreColor = property( lambda self : self.__foreColor, _setForeColor )				# ��ȡ/����ǰ��ɫ
	vTextAlign = property( lambda self : self.__vTextAlgin, _setVTextAlign )			# ��ȡ/���ô�ֱ�������ı��Ķ��뷽ʽ
	textWidth = property( lambda self : self.pyElems_[-1].right )						# ��ȡ�����ı�����



# --------------------------------------------------------------------
# λ����Ϣ��װ
# --------------------------------------------------------------------
class SiteInfo( object ) :
	__slots__ = ( "site", "left" )
	def __init__( self, site, left ) :
		self.site = site
		self.left = left

	def __cmp__( self, siteInfo ) :
		return self.site - siteInfo.site


# --------------------------------------------------------------------
# richtextbox Ԫ��
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
		����ǰ��Ԫ��
		"""
		if pyElem is None :
			self.__pyFore = None
		self.__pyFore = weakref.ref( pyElem )

	def setNextElem_( self, pyElem ) :
		"""
		���ú���Ԫ��
		"""
		if pyElem is None :
			self.__pyNext = None
		self.__pyNext = weakref.ref( pyElem )

	# -------------------------------------------------
	def setAttributes_( self, pyRich ) :
		"""
		�������� pyRich �����ԣ�����Ԫ������
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def getInst( SELF, start, wtext ) :
		"""
		�Ƿ���Ч
		"""
		return SELF( start, wtext )

	# -------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		��ȡ�����ı�
		"""
		if scope is None :
			return self.originalText
		elif scope[0] < self.end and scope[1] > self.start :
			return self.originalText
		return csstring.toWideString( "" )

	# ---------------------------------------
	def getViewLen( self ) :
		"""
		��ȡ�����ı����ַ���
		"""
		return len( csstring.toString( self.originalText ) )

	def getWViewLen( self ) :
		"""
		��ȡ�����ı�������
		"""
		return len( self.originalText )

	# -------------------------------------------------
	def getSiteInfoViaSite( self, site ) :
		"""
		�����п��ܴ��ڲ��������Ԫ��λ�û�ȡ��ȷλ�ã�������ȷλ�ú����
		"""
		start = self.start
		end = self.end
		center = ( start + end ) / 2
		if site <= center :
			return SiteInfo( start, self.left )
		return SiteInfo( end, self.right )

	def getSiteInfoViaLeft( self, left ) :
		"""
		��������ȡλ�ã�������ȷλ�ú����
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
		��ȡָ��λ���£������һ���ַ�������������
		"""
		if site <= self.start :
			return self.pyFore.skipLeftChar( site )
		return SiteInfo( self.start, self.left )

	def skipRightChar( self, site ) :
		"""
		��ȡָ��λ���£��ұ���һ���ַ�������������
		"""
		if site >= self.end :
			return self.pyNext.skipRightChar( site )
		return SiteInfo( self.end, self.right )

	def skipLeftWord( self, site ) :
		"""
		��ȡָ��λ���£������һ������������������
		"""
		if site <= self.start :
			return self.pyFore.skipLeftWord( site )
		return SiteInfo( self.start, self.left )

	def skipRightWord( self, site ) :
		"""
		��ȡָ��λ���£��ұ���һ������������������
		"""
		if site >= self.end :
			return self.pyNext.skipRightWord( site )
		return SiteInfo( self.end, self.right )


# --------------------------------------------------------------------
# ��һ����Ԫ��
# --------------------------------------------------------------------
class EFirst( BaseElement ) :
	def __init__( self ) :
		BaseElement.__init__( self, 0, csstring.toWideString( "" ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def skipLeftChar( self, site ) :
		"""
		��ȡָ��λ�����һ���ַ�
		"""
		return SiteInfo( 0, 0 )

	def skipRightChar( self, site ) :
		"""
		��ȡָ��λ���ұ�һ���ַ�
		"""
		return self.pyNext.skipRightChar( site )

	def skipLeftWord( self, site ) :
		"""
		��ȡָ��λ�����һ������
		"""
		return SiteInfo( 0, 0 )

	def skipRightWord( self, site ) :
		"""
		��ȡָ��λ���ұ�һ������
		"""
		return self.pyNext.skipRightWord( site )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	left = property( lambda self : 0, lambda self, v : 0 )
	right = property( lambda self : 0, lambda self, v : 0 )


# --------------------------------------------------------------------
# ���һ����Ԫ��
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
		������ʼ��������λ��
		"""
		self.start = self.end = site


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSiteInfoViaSite( self, site ) :
		"""
		��ȡָ��λ�õ���࣬������ȷλ�ú����
		"""
		return SiteInfo( self.end, self.__posX )

	def getSiteInfoViaLeft( self, left ) :
		"""
		��������ȡλ�ã�������ȷλ�ú����
		"""
		return SiteInfo( self.end, self.__posX )

	# -------------------------------------------------
	def skipLeftChar( self, site ) :
		"""
		ɾ��ָ��λ�����һ���ַ�
		"""
		return self.pyFore.skipLeftChar( site )

	def skipRightChar( self, site ) :
		"""
		ɾ��ָ��λ���ұ�һ���ַ�
		"""
		return SiteInfo( self.start, self.right )

	def skipLeftWord( self, site ) :
		"""
		ɾ��ָ��λ�����һ������
		"""
		return self.pyFore.skipLeftWord( site )

	def skipRightWord( self, site ) :
		"""
		ɾ��ָ��λ���ұ�һ������
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
# Ĭ��Ԫ��
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
		�������� pyRich �����ԣ������ı�����
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
		��ȡ�����ı�
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
		��ȡָ��λ�õ����
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
		��������ȡλ�ã�������ȷλ�ú����
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
		��ȡָ��λ�����һ���ַ�λ��
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
		��ȡָ��λ���ұ�һ���ַ�λ��
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
		��ȡָ��λ�����һ������λ��
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
		��ȡָ��λ���ұ�һ������λ��
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
# �ı�ѡ����
# --------------------------------------------------------------------
class Selector( object ) :
	__cg_cover = None

	def __init__( self, lineHeight ) :
		if Selector.__cg_cover is None :
			Selector.__cg_cover = GUI.load( "guis/controls/baseinput/selector.gui" )
		self.__pyCover = None
		self.__lineHeight = lineHeight
		self.__startSiteInfo = None				# ѡ����ʼλ��
		self.__endSiteInfo = None				# ѡ������λ��
		self.__selecting = False				# ������ѡ���ı���


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
		�ı�ѡ�������Ƿ���ʹ����
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
		�Ƿ���ѡ���ı���
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
		�����ı��и߶�
		"""
		self.__lineHeight = lineHeight
		if self.__pyCover :
			self.__pyCover.height = lineHeight
		if self.__startSiteInfo and self.__endSiteInfo :
			self.select( pyBox, self.__startSiteInfo, self.__endSiteInfo )

	def flash_( self, pyBox ) :
		"""
		����ѡ�б���
		"""
		if self.__startSiteInfo and self.__endSiteInfo :
			self.select( pyBox, self.__startSiteInfo, self.__endSiteInfo )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def beginSelecting( self, startInfo ) :
		"""
		��ʼѡ���ı�
		"""
		self.cancelSelect()
		self.__selecting = True
		self.__startSiteInfo = startInfo

	def endSelecting( self ) :
		"""
		����ѡ���ı�
		"""
		self.__selecting = False

	# ---------------------------------------
	def select( self, pyBox, startInfo, endInfo ) :
		"""
		ѡ��һ������
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
		����ѡ��
		"""
		self.__pyCover = None
		self.__startSiteInfo = None
		self.__endSiteInfo = None
		self.__selecting = False
