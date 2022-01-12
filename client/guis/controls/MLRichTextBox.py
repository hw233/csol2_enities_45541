# -*- coding: gb18030 -*-
#

"""
implement multiline richtext box class��

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
		self.__sbarState = ScrollBarST.AUTO								# Ĭ���Զ���ʾ������
		self.focus = True
		self.moveFocus = True
		self.mouseScrollFocus = True
		self.__initScrollBar()

		self.lines_ = []							# �����ı���
		self.__wtext = csstring.toWideString( "" )	# �ı��Ŀ��ַ���ʽ
		self.__readOnly = False						# �Ƿ���ֻ��
		self.__escTPLs = []							# ת��ģ��
		self.__curSiteInfo = SiteInfo( 0, 0, 0 )	# ���λ��

		self.__font = Font.defFont					# Ĭ������
		self.__fontSize = Font.defFontSize			# Ĭ�������С
		self.__foreColor = ( 255, 255, 255, 255 )	# Ĭ����ɫ
		self.__vTextAlgin = "BOTTOM"				# ��ֱ�������ı��Ķ��뷽ʽ��"TOP" / "MIDDLE" / "BOTTOM"
		self.__viewLen = 0							# �����ı��ַ���
		self.__wviewLen = 0							# �����ı�����
		self.__maxLen = -1							# �������������ַ�����0 ��ʾ���������ⳤ( ע�⣺���Ǳ����ı��ĳ��� )
		self.__charSpace = Font.defCharSpace		# �ּ��
		self.__spacing = Font.defSpacing			# �м��
		self.__limning = Font.defLimning			# �����ʽ
		self.__limnColor = Font.defLimnColor		# �����ɫ
		self.__forceNewline = True					# �Ƿ�������һ���

		wempty = csstring.toWideString( "" )
		self.__pyFirst = EFirst()					# ��һ��Ԫ��
		self.__pyLast = ELast()						# ���һ��Ԫ��

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
		���ı��ı�ʱ������
		"""
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearText( self ) :
		"""
		��������ı�
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
		����������ʱ������
		"""
		gui = self.gui
		gui.scroll.y = gui.maxScroll.y * value

	# -------------------------------------------------
	def __resizeCursor( self ) :
		"""
		�������ù���С
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
		��ȡ����ת������
		"""
		scopes = {}											# { start : ( end, clsElem ) }
		def wellhandled( start ) :							# �Ƿ�ת�崦���
			for s, ( e, clsElem ) in scopes.iteritems() :
				if s <= start < e :
					return True
			return False

		tpls = self.__escTPLs + [( self.__cc_newline_tpl, ENewline )]
		for tpl, clsElem in tpls :							# �ҳ�����ת���
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
		��������Ԫ��
		"""
		def newline( pyForeLine ) :								# ����
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
			if isinstance( pyElem, ENewline ) :					# ���з�
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
				if right <= maxWidth :							# ����ܷ��¸�Ԫ��
					pyForeLine.addElem_( pyElem )				# ����ӵ���ǰ��
					left = right
					break

				pyNextElem = pyElem.cutText( maxWidth - left )	# ������ͼ�۶ϸ�Ԫ��
				if pyNextElem and pyNextElem != pyElem :		# ����۶ϳɹ������ߵ�ǰ����û��Ԫ��
					pyForeLine.addElem_( pyElem )				# �򣬽�ǰ��һ����ӵ���ǰ��
					pyForeLine = newline( pyForeLine )			# ��������һ��
					pyElem = pyNextElem
					left = 0
				elif pyForeLine.hasElem_() :					# ����۶�ʧ�ܣ����ҵ�ǰ���Ѿ���Ԫ��
					pyForeLine = newline( pyForeLine )			# ������һ��
					left = 0
				else :											# ����ض�ʧ�ܣ����ҵ�ǰ�л�û���κ�Ԫ��
					pyForeLine.addElem_( pyElem )				# ��ֻ��ֱ�ӽ���Ԫ�طŵ���ǰ����
					left = pyElem.right
					break
		self.__pyLast.left = pyFore.right
		self.__pyLast.setForeElem_( pyFore )
		pyFore.setNextElem_( self.__pyLast )
		pyForeLine.addElem_( self.__pyLast )
		pyForeLine.newline_()

	def __resetScrollBar( self ) :
		"""
		���¹�����
		"""
		viewHeight = self.height
		fontHeight = self.__fontSize
		lastLine = self.lines_[-1]
		maxHeight = lastLine.bottom + fontHeight			# ����������ʱ��Ԥ��һ��
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
		��ʼ���������ɼ���
		"""
		if self.__sbarState == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif self.__sbarState == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif self.__sbarState == ScrollBarST.AUTO :
			self.pySBar.visible = False 
			
	def __setTextElements( self, wtext ) :
		"""
		�����ı�������Ԫ��
		ע��ԭ�������Ԫ�ز�Ӧ���������Ӧ���� Line ��ʵ�֣�
			����Line ֻ�Ǹ����Ե��У�����һ�� UI��������������Ԫ��ֱ��һ�㡣
		"""
		self.__clearText()
		self.__wtext = wtext							# ������ı�
		scopes = self.__getTextScopes( wtext )			# ��ȡ���о߱�ת������������
		starts = sorted( scopes.keys() )				# ��������������ʼλ�ã���С��������

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
			pyElem = clsElem.getInst( start, text )				# ����Ԫ��
			if pyElem is None :									# ����Ԫ��ʱ����ʧ��
				pyElem = EDefText( start, text )				# �ô��ı���ʾ
			self.__viewLen += pyElem.getViewLen()
			self.__wviewLen += pyElem.getWViewLen()
			pyElems.append( pyElem )
		self.__pyLast.setScopeSite( count )
		self.__layoutElems( pyElems )
		self.__resetScrollBar()

	# -------------------------------------------------
	def __getLineOfSite( self, site ) :
		"""
		��ȡָ��λ�ô�����
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
		��������λ���ҳ����������ı���
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
		��ȡָ��������Χ�ڵ��ı���
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
		���� site ��ȡ SiteInfo
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
		��������λ�û�ȡ����λ��
		"""
		line = self.__getLineOfPos( pos )
		return line.getRealSiteViaLeft( pos[0] )

	def __getEndSiteInfo( self ) :
		"""
		�ı���ĩ�˵�λ����Ϣ
		"""
		line = self.lines_[-1]
		return SiteInfo( line.index, line.end, line.right )

	# -------------------------------------------------
	def __setCursorSite( self, siteInfo ) :
		"""
		���ù��λ��
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
	# ��������
	# -------------------------------------------------
	def __keyScroll( self, key, mods ) :
		"""
		���ð�����������
		"""
		if key == KEY_UPARROW and mods == MODIFIER_CTRL :
			self.pySBar.decScroll()
			return True
		elif key == KEY_DOWNARROW and mods == MODIFIER_CTRL :
			self.pySBar.incScroll()
			return True
		return False


	# -------------------------------------------------
	# �ƶ����
	# -------------------------------------------------
	def __moveLeftChar( self ) :
		"""
		�����������һ���ַ�
		"""
		if self.__selector.selected :
			return self.__selector.minSiteInfo
		siteInfo = self.__curSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipLeftChar( siteInfo )

	def __moveRightChar( self ) :
		"""
		�����������һ���ַ�
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		siteInfo = self.__curSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipRightChar( siteInfo )

	def __moveLeftWord( self ) :
		"""
		�����ƶ�һ������
		"""
		siteInfo = self.__curSiteInfo
		if self.__selector.selected :
			siteInfo = self.__selector.minSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipLeftWord( siteInfo )

	def __moveRightWord( self ) :
		"""
		�����ƶ�һ������
		"""
		if self.__selector.selected :
			return self.__selector.maxSiteInfo
		siteInfo = self.__curSiteInfo
		line = self.lines_[siteInfo.lineIdx]
		return line.skipRightWord( siteInfo )

	def __moveUpLine( self ) :
		"""
		���������һ��
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipUpLine( self.__curSiteInfo )

	def __moveDownLine( self ) :
		"""
		���������һ��
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipDownLine( self.__curSiteInfo )

	def __moveLeftAll( self ) :
		"""
		������Ƶ���ʼ��
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getStartSiteInfo()

	def __moveRightAll( self ) :
		"""
		������ƶ�����ĩ��
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getEndSiteInfo()

	def __moveToTop( self ) :
		"""
		�ƶ�����ǰ��
		"""
		return self.lines_[0].getStartSiteInfo()

	def __moveToBottom( self ) :
		"""
		�ƶ�����ĩ��
		"""
		return self.lines_[-1].getEndSiteInfo()

	# ---------------------------------------
	def __moveCursor( self, key, mods ) :
		"""
		ͨ�����̼����ƶ����
		"""
		handlers = {
			( KEY_LEFTARROW, 0 )				: self.__moveLeftChar, 		# �����ƶ�һ���ַ�
			( KEY_RIGHTARROW, 0 )				: self.__moveRightChar,		# �����ƶ�һ���ַ�
			( KEY_LEFTARROW, MODIFIER_CTRL )	: self.__moveLeftWord,		# �����ƶ�һ������
			( KEY_RIGHTARROW, MODIFIER_CTRL )	: self.__moveRightWord,		# �����ƶ�һ������
			( KEY_UPARROW, 0 )					: self.__moveUpLine, 		# ������һ��
			( KEY_DOWNARROW, 0 )				: self.__moveDownLine,		# ������һ��
			( KEY_HOME, 0 )						: self.__moveLeftAll,		# �Ƶ���������е���ǰ��
			( KEY_END, 0 )						: self.__moveRightAll,		# �Ƶ���������е������
			( KEY_HOME, MODIFIER_CTRL )			: self.__moveToTop,			# �ƶ�����ǰ��
			( KEY_END, MODIFIER_CTRL )			: self.__moveToBottom,		# �ƶ�����ĩ��
			}
		if ( key, mods ) in handlers :
			self.cancelSelect()
			siteInfo = handlers[( key, mods )]()
			self.__setCursorSite( siteInfo )
			return True
		return False

	# -------------------------------------------------
	# ɾ���ַ�
	# -------------------------------------------------
	def __delLeftChar( self ) :
		"""
		ɾ��������һ���ַ�
		"""
		endInfo = self.__curSiteInfo
		curLine = self.lines_[endInfo.lineIdx]
		startInfo = curLine.skipLeftChar( endInfo )
		return startInfo, endInfo

	def __delRightChar( self ) :
		"""
		ɾ������ұ�һ���ַ�
		"""
		startInfo = self.__curSiteInfo
		curLine = self.lines_[startInfo.lineIdx]
		endInfo = curLine.skipRightChar( startInfo )
		return startInfo, endInfo

	def __delLeftWord( self ) :
		"""
		ɾ��������һ������
		"""
		endInfo = self.__curSiteInfo
		curLine = self.lines_[endInfo.lineIdx]
		startInfo = curLine.skipLeftWord( endInfo )
		return startInfo, endInfo

	def __delRightWord( self ) :
		"""
		ɾ������ұ�һ������
		"""
		startInfo = self.__curSiteInfo
		curLine = self.lines_[startInfo.lineIdx]
		endInfo = curLine.skipRightWord( startInfo )
		return startInfo, endInfo

	# --------------------------------------
	def __delScopeText( self, startInfo, endInfo ) :
		"""
		ɾ��ָ�������ڵ��ı�
		"""
		start = startInfo.site
		end = endInfo.site
		wtext = self.__wtext
		self.__setTextElements( wtext[:start] + wtext[end:] )
		if startInfo.lineIdx >= self.lineCount :						# ɾ�������һ���ı����п��ܼ���һ�У�
			startInfo = self.lines_[-1].getEndSiteInfo()				# ��֮ǰ�Ĺ���������䣬�Ӷ����������Խ��
		self.__setCursorSite( startInfo )

	def __delSubStr( self, key, mods ) :
		"""
		ͨ������ɾ��һ���Ӵ�
		"""
		if self.__readOnly :
			return False

		handlers = {
			( KEY_BACKSPACE, 0 )			 : self.__delLeftChar,		# ɾ���������һ���ַ�
			( KEY_DELETE, 0 )				 : self.__delRightChar,		# ɾ������ұ�һ���ַ�
			( KEY_BACKSPACE, MODIFIER_CTRL ) : self.__delLeftWord,		# ɾ�������ߵ�һ������
			( KEY_DELETE, MODIFIER_CTRL )	 : self.__delRightWord,		# ɾ������ұߵ�һ������
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
		line = self.__getLineOfSite( start )
		count = 0
		while line and line.start < end :
			count += len( line.getWViewText( ( start, end ) ) )
			line = line.next
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
		site = start + addCount
		siteInfo = self.__getSiteInfoViaSite( site, startInfo.lineIdx )
		self.__setCursorSite( siteInfo )
		self.cancelSelect()
		self.onTextChanged_()

	def __input( self, key, mods ) :
		"""
		ͨ����������һ���ַ�
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
	# ѡ���ı�
	# -------------------------------------------------
	def __selectLeftChar( self ) :
		"""
		ѡ�й��ǰһ���ַ�
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipLeftChar( self.__curSiteInfo )

	def __selectRightChar( self ) :
		"""
		ѡ�й���һ���ַ�
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipRightChar( self.__curSiteInfo )

	def __selectLeftWord( self ) :
		"""
		ѡ�й��ǰһ������
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipLeftWord( self.__curSiteInfo )

	def __selectRightWord( self ) :
		"""
		ѡ�й���һ������
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipRightWord( self.__curSiteInfo )

	def  __selectLeftAll( self ) :
		"""
		ѡ�е�ǰ���У����ǰ�������ı�
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getStartSiteInfo()

	def __selectRightAll( self ) :
		"""
		ѡ�й���������ı�
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.getEndSiteInfo()

	def __selectUpLine( self ) :
		"""
		����ѡ��һ��
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipUpLine( self.__curSiteInfo )

	def __selectDownLine( self ) :
		"""
		����ѡ��һ��
		"""
		line = self.lines_[self.__curSiteInfo.lineIdx]
		return line.skipDownLine( self.__curSiteInfo )

	def __selectUpAll( self ) :
		"""
		ѡ�й��ǰ�������ı�
		"""
		line = self.lines_[0]
		return line.getStartSiteInfo()

	def __selectDownAll( self ) :
		"""
		ѡ�й���������ı�
		"""
		return self.__getEndSiteInfo()

	def __selectAll( self ) :
		"""
		ѡ�������ı�
		"""
		startInfo = SiteInfo( 0, 0, 0 )
		endInfo = self.__getEndSiteInfo()
		self.__selector.select( self, startInfo, endInfo )

	# ---------------------------------------
	def __keySelectText( self, key, mods ) :
		"""
		���̰���ѡ���ı�
		"""
		if key == KEY_A and mods == MODIFIER_CTRL :												# ѡ��ȫ���ı�
			self.__selectAll()
			return True

		handlers = {
			( KEY_LEFTARROW, MODIFIER_SHIFT )					: self.__selectLeftChar,		# �����ƶ�һ���ַ�
			( KEY_RIGHTARROW, MODIFIER_SHIFT )					: self.__selectRightChar,		# �����ƶ�һ���ַ�
			( KEY_LEFTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectLeftWord,		# �����ƶ�һ������
			( KEY_RIGHTARROW, MODIFIER_SHIFT | MODIFIER_CTRL )	: self.__selectRightWord,		# �����ƶ�һ������
			( KEY_HOME, MODIFIER_SHIFT )						: self.__selectLeftAll,			# �Ƶ���ǰ��
			( KEY_END, MODIFIER_SHIFT )							: self.__selectRightAll,		# �Ƶ������
			( KEY_UPARROW, MODIFIER_SHIFT )						: self.__selectUpLine,			# ����ѡ��һ��
			( KEY_DOWNARROW, MODIFIER_SHIFT )					: self.__selectDownLine,		# ����ѡ��һ��
			( KEY_HOME, MODIFIER_SHIFT | MODIFIER_CTRL )		: self.__selectUpAll,			# �Ƶ���ǰ��
			( KEY_END, MODIFIER_SHIFT | MODIFIER_CTRL )			: self.__selectDownAll,			# �Ƶ������
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
		x, y = self.mousePos								# ���λ��
		y += self.gui.scroll.y
		siteInfo = self.__getSiteInfoViaPos( ( x, y ) )		# ����������λ�ú����
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
			x, y = self.mousePos
			y += self.gui.scroll.y								# ���֮ǰ��λ��
			endInfo = self.__getSiteInfoViaPos( ( x, y ) )
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

	def onMouseScroll_( self, dz ) :
		self.pySBar.onMouseScroll_( dz )
		return True

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
		if self.__keyScroll( key, mods ) :			# �ð�����������
			return True
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
	def getEscTemplates( self ) :
		"""
		��ȡת��ģ��
		"""
		return self.__escTPLs

	def setEscTemplates( self, tpls ) :
		"""
		����ת��ģ��
		@type				tpl		: re._sre.SRE_Pattern
		@param				tpl		: ת��ģ��
		@type				clsElem : class
		@param				clsElem : Element
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
		self.onTextChanged_()

	# -------------------------------------------------
	def select( self, start, end ) :
		"""
		ѡ���ı�
		"""
		startInfo = self.__getSiteInfoViaSite( start, 0 )
		endInfo = self.__getSiteInfoViaSite( end, 0 )
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
	text = property( lambda self : csstring.toString( self.__wtext ), _setText )		# ��ȡ/����ԭʼ�ı�
	wtext = property( lambda self : self.__wtext )										# ��ȡԭʼ�ı��Ŀ��ı���ʽ
	viewText = property( lambda self : csstring.toString( self._getWViewText() ) )		# ��ȡ�����ı�
	wviewText = property( _getWViewText )												# ��ȡ�����ı��Ŀ��ı���ʽ
	selectText = property( lambda self : csstring.toString( self._getWSelectText() ) )	# ��ȡѡ���ı�
	wselectText = property( _getWSelectText )											# ��ȡѡ���ı��Ŀ��ַ���ʽ
	length = property( lambda self : len( self.text ) )									# ��ȡ�ı������ַ���
	wlength = property( lambda self : len( self.__wtext ) )								# ��ȡ�ı�����������
	viewLength = property( _getViewLen )												# ��ȡ�����ı����ַ���
	wviewLength = property( _getWViewLen )												# ��ȡ�����ı�������
	maxLength = property( lambda self : self.__maxLen, _setMaxLen )						# ��ȡ/��������������ַ�����ע�⣺���Ǳ����ı����ַ�����
	readOnly = property( lambda self : self.__readOnly, _setReadOnly )					# ��ȡ/�����Ƿ�ֻ��
	font = property( lambda self : self.__font, _setFont )								# ��ȡ/��������
	fontSize = property( lambda self : self.__fontSize, _setFontSize )					# ��ȡ�����С���߶ȣ�
	foreColor = property( lambda self : self.__foreColor, _setForeColor )				# ��ȡ/����ǰ��ɫ
	charSpace = property( lambda self : self.__charSpace, _setCharSpace )				# ��ȡ/�����ּ��
	spacing = property( lambda self : self.__spacing, _setSpacing )						# ��ȡ/�����м��
	limning = property( lambda self : self.__limning, _setLimning )						# ��ȡ/���������ʽ
	limnColor = property( lambda self : self.__limnColor, _setLimnColor )				# ��ȡ/���������ɫ
	forceNewline = property( lambda self:self.__forceNewline,_setForceNewline)

	lineCount = property( lambda self : len( self.lines_ ) )							# ��ȡ����
	vTextalign = property( lambda self : self.__vTextAlgin, _setVTextAlign )			# ��ȡ/���ô�ֱ�������ı��Ķ��뷽ʽ
	textHeight = property( lambda self : self.lines_[-1].bottom )						# ��ȡ�����ı�����

	width = property( lambda self : BaseInput._getWidth( self ), _setWidth )			# ��ȡ/���ÿ��
	height = property( lambda self : BaseInput._getHeight( self ), _setHeight )			# ��ȡ/���ø߶�
	sbarState = property( _getSBarState, _setSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE


# --------------------------------------------------------------------
# λ����Ϣ��װ
# --------------------------------------------------------------------
class SiteInfo( object ) :
	__slots__ = ( "lineIdx", "site", "x" )
	def __init__( self, lineIdx, site, x ) :
		self.lineIdx = lineIdx		# ������
		self.site = site			# ����λ��
		self.x = x					# λ�����

	def __cmp__( self, siteInfo ) :
		return self.site - siteInfo.site


# --------------------------------------------------------------------
# �ı���
# --------------------------------------------------------------------
class Line( object ) :
	"""
	��Ԫ�ػ���
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
		��ȡָ������λ�ô���Ԫ��
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
		��ȡָ����ദ��Ԫ��
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
		��ȡָ�������ڵ�����Ԫ��
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
		����ǰ��Ԫ��
		"""
		if line is None :
			self.__fore = None
		self.__fore = weakref.ref( line )

	def setNextLine_( self, line ) :
		"""
		���ú���Ԫ��
		"""
		if line is None :
			self.__next = None
		self.__next = weakref.ref( line )

	# -------------------------------------------------
	def addElem_( self, pyElem ) :
		"""
		���һ��Ԫ��
		"""
		pyElem.setLine_( self )
		self.__height = max( pyElem.height, self.__height )
		self.__pyElems.append( pyElem )

	def hasElem_( self ) :
		"""
		�Ƿ��зǿ�Ԫ��
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
		����һ�У���������Ԫ�أ��������Լ��ĵײ�����
		"""
		pyBox = self.__pyBox()
		textAlign = pyBox.vTextalign
		if textAlign == "TOP" :					# �ı���������
			aname = "top"
			y = self.top
		elif textAlign == "MIDDLE" :			# �ı��м����
			aname = "middle"
			y = self.middle
		else :
			aname = "bottom"					# �ı��ײ�����
			y = self.bottom
		for pyElem in self.__pyElems :
			setattr( pyElem, aname, y )
		return self.bottom

	# -------------------------------------------------
	def resetForeColor_( self, color ) :
		"""
		��������������ɫ
		"""
		for pyElem in self.__pyElems :
			pyElem.color = color


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def inLineStart( self, site ) :
		"""
		ָ��λ���Ƿ�������
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
		ָ��λ���Ƿ�����β
		"""
		return site >= self.end

	def getStartSiteInfo( self ) :
		"""
		��ȡ���׵�λ����Ϣ
		"""
		pyFirst = self.__pyElems[0]
		if isinstance( pyFirst, ENewline ) :
			return SiteInfo( self.index, pyFirst.end, 0 )
		return SiteInfo( self.index, self.start, 0 )

	def getEndSiteInfo( self ) :
		"""
		��ȡ��βλ����Ϣ
		"""
		return SiteInfo( self.index, self.end, self.right )

	# -------------------------------------------------
	def getRealSiteViaSite( self, site ) :
		"""
		�����п��ܴ��ڲ��������Ԫ��λ�û�ȡ��ȷλ�ã�������ȷλ�ú����
		"""
		pyElem = self.__getElemOfSite( site )
		site, x = pyElem.calcRealSite( site )
		return SiteInfo( self.index, site, x )

	def getRealSiteViaLeft( self, left ) :
		"""
		��������ȡλ�ã�������ȷλ�ú����
		"""
		pyElem = self.__getElemOfLeft( left )
		site, x = pyElem.calcRealLeft( left )
		return SiteInfo( self.index, site, x )

	# -------------------------------------------------
	def skipLeftChar( self, siteInfo ) :
		"""
		��ָ��λ�ô�������һ���ַ���
		"""
		site = siteInfo.site
		if self.inLineStart( site ) :					# �����ǰλ��������
			fore = self.fore
			if fore :									# ���ǰ�滹����
				return fore.getEndSiteInfo()			# �򣬷���ǰһ�е���ĩ
			else :										# ���ǰ���Ѿ�û����
				return siteInfo							# �򣬷��ص�ǰ�����ף�ԭ�����أ�
		else :											# ��ǰλ��������
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getLeftCharSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipRightChar( self, siteInfo ) :
		"""
		��ָ��λ�ô�������һ���ַ�
		"""
		site = siteInfo.site
		if site >= self.end :							# �����ǰλ������ĩ
			next = self.next
			if next :
				return next.getStartSiteInfo()	# �򷵻���һ�е�����
			else :										# ��������Ѿ�û������
				return siteInfo							# �򣬷��ص�ǰ����ĩ��ԭ�����أ�
		else :											# ��ǰλ��������
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getRightCharSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipLeftWord( self, siteInfo ) :
		"""
		��ָ��λ�ô���ǰ��һ������
		"""
		site = siteInfo.site
		if self.inLineStart( site ) :					# �����ǰλ��������
			fore = self.fore
			if fore :
				return fore.getEndSiteInfo()		# �򣬷���ǰһ�е���ĩ
		else :											# ��ǰλ��������
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getLeftWordSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipRightWord( self, siteInfo ) :
		"""
		��ָ��λ�ô�������һ������
		"""
		site = siteInfo.site
		if site >= self.end :							# �����ǰλ������ĩ
			next = self.next
			if next :
				return next.getStartSiteInfo()	# �򷵻���һ�е�����
		else :											# ��ǰλ��������
			pyElem = self.__getElemOfSite( site )
			site, x = pyElem.getRightWordSiteX( site )
			return SiteInfo( self.index, site, x )

	def skipUpLine( self, siteInfo ) :
		"""
		��ָ��λ�ô�������һ��
		"""
		fore = self.fore
		if fore is None : return siteInfo
		pyElem = fore.__getElemOfLeft( siteInfo.x )
		site, x = pyElem.calcRealLeft( siteInfo.x )
		return SiteInfo( fore.index, site, x )

	def skipDownLine( self, siteInfo ) :
		"""
		��ָ��λ�ô�������һ��
		"""
		next = self.next
		if next is None : return siteInfo
		pyElem = next.__getElemOfLeft( siteInfo.x )
		site, x = pyElem.calcRealLeft( siteInfo.x )
		return SiteInfo( next.index, site, x )

	# -------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		��ȡ��һ���ı��Ŀ��ַ���
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
		��ȡ���п����ı��ĳ���
		"""
		count = 0
		for pyElem in self.__pyElems :
			count += pyElem.getViewLen()
		return count

	def getWViewLen( self ) :
		"""
		��ȡ���п����ı��Ŀ��ַ�����
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
# �ı�Ԫ��
# --------------------------------------------------------------------
class BaseElement( object ) :
	"""
	Ԫ�ػ���
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
		������������
		"""
		self.__line = weakref.ref( line )

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
		���� pyRich ���������� element ������
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def getInst( SELF, start, text ) :
		"""
		�Ƿ���Ч
		"""
		return SELF( start, text )

	# -------------------------------------------------
	def getWViewText( self, scope ) :
		"""
		��ȡ�����ı�
		"""
		if scope is None :
			return self.originalText
		elif scope[0] < self.end and scope[1] > self.start :
			return self.originalText
		return csstring.toWideString( "" )

	# --------------------------------------
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
	def calcRealSite( self, site ) :
		"""
		�����п��ܴ��ڲ��������Ԫ��λ�û�ȡ��ȷλ�ã�������ȷλ�ú����
		"""
		start = self.start
		end = self.end
		center = ( start + end ) / 2
		if site <= center :
			return start, self.left
		return self.end, self.right

	def calcRealLeft( self, left ) :
		"""
		��������ȡλ�ã�������ȷλ�ú����
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
		��ȡָ��λ���£������һ���ַ�������λ�ú����
		"""
		if site <= self.start :
			return self.pyFore.getLeftCharSiteX( site )
		elif site > self.end :
			self.pyNext.getLeftCharSiteX( site )
		return self.start, self.left

	def getRightCharSiteX( self, site ) :
		"""
		��ȡָ��λ���£��ұ���һ���ַ�������λ�ú����
		"""
		if site < self.start :
			return self.pyFore.getRightCharSiteX( site )
		elif site >= self.end :
			return self.pyNext.getRightCharSiteX( site )
		return self.end, self.right

	def getLeftWordSiteX( self, site ) :
		"""
		��ȡָ��λ���£������һ�����ʵ�����λ�ú����
		"""
		if site <= self.start :
			return self.pyFore.getLeftWordSiteX( site )
		elif site > self.end :
			return self.pyNext.getLeftWordSiteX( site )
		return self.start, self.left

	def getRightWordSiteX( self, site ) :
		"""
		��ȡָ��λ���£��ұ���һ�����ʵ�����λ�ú����
		"""
		if site < self.start :
			return self.pyFore.getRightWordSiteX( site )
		elif site >= self.end :
			return self.pyNext.getRightWordSiteX( site )
		return self.end, self.right

	# -------------------------------------------------
	def cutText( self, width ) :
		"""
		�����ı�
		"""
		return None


# --------------------------------------------------------------------
# ��һ����Ԫ��
# --------------------------------------------------------------------
class EFirst( BaseElement ) :
	def __init__( self ) :
		BaseElement.__init__( self, 0, csstring.toWideString( "" ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def calcRealSite( self, site ) :
		"""
		��ȡָ��λ�õ���࣬������ȷλ�ú����
		"""
		return 0, 0

	def calcRealLeft( self, left ) :
		"""
		��������ȡλ�ã�������ȷλ�ú����
		"""
		if left <= 0 : return 0, 0
		return self.pyNext.calcRealLeft( left )

	# -------------------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		��ȡָ��λ���£������һ���ַ�������λ�ú����
		"""
		return 0, 0

	def getRightCharSiteX( self, site ) :
		"""
		��ȡָ��λ���ұ�һ���ַ�������λ�ú����
		"""
		return self.pyNext.getRightCharSiteX( site )

	def getLeftWordSiteX( self, site ) :
		"""
		��ȡָ��λ�����һ�����ʵ�����λ�ú����
		"""
		return 0, 0

	def getRightWordSiteX( self, site ) :
		"""
		ɾ��ָ��λ���ұ�һ������
		"""
		return self.pyNext.getRightWordSiteX( site )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	height = property( lambda self : self.line.height )
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
	# public
	# ----------------------------------------------------------------
	def setScopeSite( self, site ) :
		"""
		������ʼ��������λ��
		"""
		self.__posX = self.start = self.end = site

	# -------------------------------------------------
	def calcRealSite( self, site ) :
		"""
		��ȡָ��λ�õ���࣬������ȷλ�ú����
		"""
		return self.end, self.__posX

	def calcRealLeft( self, left ) :
		"""
		��������ȡλ�ã�������ȷλ�ú����
		"""
		if left >= self.right :
			return self.end, self.right
		return self.pyFore.calcRealLeft( left )

	# -------------------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		��ȡָ��λ�����һ���ַ�
		"""
		return self.pyFore.getLeftCharSiteX( site )

	def getRightCharSiteX( self, site ) :
		"""
		��ȡָ��λ���ұ�һ���ַ�
		"""
		return self.end, self.right

	def getLeftWordSiteX( self, site ) :
		"""
		��ȡָ��λ�����һ������
		"""
		return self.pyFore.getLeftWordSiteX( site )

	def getRightWordSiteX( self, site ) :
		"""
		��ȡָ��λ���ұ�һ������
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
		���� RichText �����ı�����
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
		��ȡָ�������ڵ��ı�
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
		��ȡָ��λ�õ����
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
		��������ȡλ�ã�������ȷλ�ú����
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
		��ȡָ��λ�����һ���ַ�������ɾ������������
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
		��ȡָ��λ���ұ�һ���ַ�
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
		��ȡָ��λ�����һ������
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
		��ȡָ��λ���ұ�һ������
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
		�۶��ı�
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
	����
	"""
	def __init__( self, start, text ) :
		BaseElement.__init__( self, start, text )
		self.__posX = 0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def calcRealSite( self, site ) :
		"""
		�����п��ܴ��ڲ��������Ԫ��λ�û�ȡ��ȷλ�ã�������ȷλ�ú����
		"""
		return self.end, self.right

	def calcRealLeft( self, left ) :
		"""
		��������ȡλ�ã�������ȷλ�ú����
		"""
		return self.end, self.right

	# -------------------------------------------------
	def getLeftCharSiteX( self, site ) :
		"""
		��ȡָ��λ���£������һ���ַ�������λ�ú����
		"""
		pyFore = self.pyFore
		return pyFore.end, pyFore.right

	def getRightCharSiteX( self, site ) :
		"""
		��ȡָ��λ���£��ұ���һ���ַ�������λ�ú����
		"""
		return self.pyNext.getRightCharSiteX( self.end )

	def getLeftWordSiteX( self, site ) :
		"""
		��ȡָ��λ���£������һ�����ʵ�����λ�ú����
		"""
		pyFore = self.pyFore
		return pyFore.end, pyFore.right

	def getRightWordSiteX( self, site ) :
		"""
		��ȡָ��λ���£��ұ���һ�����ʵ�����λ�ú����
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
		�����ı��и߶�
		"""
		self.__lineHeight = height
		for pyCover in self.__pyCovers :
			pyCover.height = height
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
		vAlign = pyBox.vTextalign
		startLineIdx = startInfo.lineIdx						# ��ʼλ��
		endLineIdx = endInfo.lineIdx							# ����λ��
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
		����ѡ��
		"""
		self.__pyCovers = []
		self.__startSiteInfo = None
		self.__endSiteInfo = None
		self.__selecting = False
