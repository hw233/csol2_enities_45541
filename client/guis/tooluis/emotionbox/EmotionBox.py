# -*- coding: gb18030 -*-
#
#$Id: EmotionBox.py,v 1.10 2008-08-29 02:40:28 huangyongwei Exp $
#

"""
implement emotion face selector

2008/03/28: writen by huangyongwei
"""

import weakref
from AbstractTemplates import Singleton
from ChatFacade import emotionParser
from guis import *
from guis.common.RootGUI import RootGUI
from guis.controls.TabCtrl import TabCtrl,TabButton,TabPanel,TabPage
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.tooluis.emotionbox.FaceIcon import FaceIcon

class EmotionBox( Singleton, RootGUI, TabCtrl ) :
	
	__cc_tab_left		= 0.0						# ��ҳ��ť�����
	__cc_tab_space		= 4							# ÿ����ҳ��ť�ļ������

	def __init__( self ) :
		wnd = GUI.load( "guis/tooluis/emotionbox/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		TabCtrl.__init__( self, wnd )
		self.activable_ = False
		self.movable_ = False

		self.__emotions = {}
		self.__pyBinder = None										# ���� UI��������� UI ������ʾ�����鴰�ڣ�
		self.callback = None

		self.__initialize( wnd )

	def __del__( self ) :
		RootGUI.__del__( self )
		if Debug.output_del_EmotionBox :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		RootGUI.dispose( self )
		self.__class__.releaseInst()

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		RootGUI.generateEvents_( self )
		TabCtrl.generateEvents_( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		emotionSigns = emotionParser.emotionSigns
		for index, signs in emotionSigns.items():
			page = GUI.load( "guis/tooluis/emotionbox/emotpage.gui" )
			uiFixer.firstLoadFix( page )
			pyEmotPage = EmotionPage( page, self )
			titleName = emotionParser.titleNames.get( index, "" )
			pyEmotPage.pgName = titleName
			pyEmotPage.color = ( 28, 28, 28, 100 )
			emotions = []
			for sign in signs:
				path, dsp = emotionParser.getEmotion( sign )
				emotions.append( Emote( sign, path, dsp ) )
			pyEmotPage.updateEmote( emotions )
			self.addPage( pyEmotPage )
		self.__layoutPages()
		self.onTabPageSelectedChanged.bind( self.__onTabPageChanged )
	
	def addPage( self, pyPage ):
		TabCtrl.addPage( self, pyPage )
		self.addPyChild( pyPage )
		pyPage.pos = 0, 0

	# -------------------------------------------------
	def __onLastKeyDown( self, key, mods ) :
		if ( key == KEY_LEFTMOUSE or key == KEY_RIGHTMOUSE ) and mods == 0 :
			if not self.isMouseHit() and not self.pyBinder.isMouseHit() :
				self.hide()
	
	def __layoutPages( self ) :
		"""
		�������з�ҳ
		"""
		pyPages = self.pyPages								# ����ͣ����ҳ��
		totalWidth = 0										# ҳ�水ť�ܿ�
		fitWidths = []										# ˳����ÿҳ���
		for pyPage in pyPages :								# �ҳ�����ͣ����ҳ�棬���Ҽ�������ҳ�水ť���ܿ��
			pyBtn = pyPage.pyBtn
			fitWidth = pyBtn.fitWidth
			totalWidth += fitWidth
			fitWidths.append( fitWidth )
		left = self.__cc_tab_left
		wasteSpace = self.pageCount * \
			self.__cc_tab_space + left						# �հ׵ط�
		ratio = ( self.width - wasteSpace ) / totalWidth	# ҳ�水ť���ÿռ���ҳ�水ť�ܿ��
		for idx, pyPage in enumerate( pyPages ) :
			pyBtn = pyPage.pyBtn
			pyBtn.width = fitWidths[idx] * ratio			# ����������ҳ�水ť���
			pyBtn.left = left
			left = pyBtn.right + self.__cc_tab_space
	
	def __onTabPageChanged( self, pyTabCtrl ):
		"""
		ѡ������ҳ
		"""
		pySelPage = pyTabCtrl.pySelPage
		if pySelPage is None:return
		pyPanel = pySelPage.pyPanel
		pyPanel.setPages()

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		self.hide()
		self.callback = None
		self.__pyBinder = None
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, callback, pyBinder ) :
		"""
		��ʾ�������
		@type				callback : function
		@param				callback : �ص�
		@type				pyBinder : python ui
		@param				pyBinder : �󶨵Ŀؼ�
		@return						 : None
		"""
		self.callback = callback
		self.__pyBinder = weakref.ref( pyBinder )
		RootGUI.show( self, pyBinder )
		LastKeyDownEvent.attach( self.__onLastKeyDown )

	def hide( self ) :
		"""
		���ر������
		@return						  : None
		"""
		LastKeyDownEvent.detach( self.__onLastKeyDown )
		RootGUI.hide( self )
		self.__pyBinder = None
		rds.ccursor.normal()

	def toggle( self, callback, pyBinder ) :
		"""
		������ڴ�����ʾ״̬�������أ�������ʾ
		"""
		if self.visible :
			self.hide()
		else :
			self.show( callback, pyBinder )

	# -------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )

# ------------------------------------------------------------------------
from guis.controls.Control import Control
class EmotionPage( Control, TabPage ):
	
	def __init__( self, page, pyBinder ):
		self.__isInitPages = False				# ��ǣ���ֹ�ظ����������¼�
		Control.__init__( self, page, pyBinder )
		self.__isInitPages = True
		self.__initialize( page )

	def dispose( self ) :
		Control.dispose( self )

	def __del__( self ) :
		Control.__del__( self )
	
	def __initialize( self, page ):
		pyBtnTab = EmoteBtn( page.tabBtn )
		self.__pyEmotPanel = EmotionPanel( page.tabPanel )
		TabPage.__init__( self, pyBtnTab, self.__pyEmotPanel )

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		if self.__isInitPages :
			TabPage.generateEvents_( self )
			Control.generateEvents_( self )
			del self.__isInitPages
	
	def updateEmote( self, emotes ):
		"""
		���±���ͼ��
		"""
		self.__pyEmotPanel.updateEmote( emotes )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPGName( self ) :
		return self.pyBtn.text

	def _setPGName( self, name ) :
		self.pyBtn.text = name

	def _getColor( self ) :
		return self.pyPanel.color

	def _setColor( self, color ) :
		self.pyBtn.selectedBackColor = color
		self.pyPanel.color = color

	pgName = property( _getPGName, _setPGName )							# str: ��ȡ/����ҳ��
	color = property( _getColor, _setColor )							# Color/tuple: ��ȡ/���ð�����ɫ
	
# ------------------------------------------------------------------------
from guis.controls.StaticText import StaticText
class EmotionPanel( TabPanel ):
	
	_cc_items_rows = ( 4, 8 )
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__pyStPages = StaticText( panel.stPages )
		self.__pyStPages.text = ""
		
		self.__pyEmotPage = ODPagesPanel( panel.emotsPanel, panel.pgIdxBar )
		self.__pyEmotPage.onViewItemInitialized.bind( self.__initEmotion )
		self.__pyEmotPage.onDrawItem.bind( self.__drawEmotion )
		self.__pyEmotPage.viewSize = self._cc_items_rows
		self.__pyEmotPage.selectable = True
		self.__pyEmotPage.onItemSelectChanged.bind( self.__onEmotionSelected )
	
	def __initEmotion( self, pyViewItem ):
		"""
		��ʼ������ͼ��
		"""
		pyEmote = FaceIcon( self )
		pyViewItem.pyEmote = pyEmote
		pyViewItem.addPyChild( pyEmote )
		pyViewItem.focus = True
		pyEmote.left = 0
		pyEmote.top = 0
	
	def __drawEmotion( self, pyViewItem ):
		"""
		�ػ�����ͼ��
		"""
		emote = pyViewItem.pageItem
		pyEmote = pyViewItem.pyEmote
		pyEmote.selected = pyViewItem.selected
		pyEmote.update( emote )
		curPageIndex = self.__pyEmotPage.pageIndex
		totalPageIndex = self.__pyEmotPage.maxPageIndex
		self.__pyStPages.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )
	
	def __onEmotionSelected(self, index ):
		"""
		ѡ�����
		"""
		itemInfo = self.__pyEmotPage.selItem
		if itemInfo is None:return
		sign = itemInfo.sign
		pyParent = self.pyTopParent
		pyParent.callback( sign )
		if self.__pyEmotPage.selIndex != -1:
			self.__pyEmotPage.selIndex = -1

	def updateEmote( self, emotes ):
		"""
		���±���
		"""
		for emote in emotes:
			if emote not in self.__pyEmotPage.items:
				self.__pyEmotPage.addItem( emote )
	
	def setPages( self ):
		curPageIndex = self.__pyEmotPage.pageIndex
		totalPageIndex = self.__pyEmotPage.maxPageIndex
		self.__pyStPages.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )

class EmoteBtn( TabButton ):
	
	__cc_max_width				= 80			# ��ť�����
	__cc_com_width				= 56			# ���ʿ�ȣ����������֣�
	__cc_text_space				= 4				# �ı���ǩ����С���
	
	def __init__( self, btn ) :
		TabButton.__init__( self, btn )
		self.moveFocus = True
		self.isOffsetText = False
		self.__text = ""

		mapping = ( ( 0, 0 ), ( 0, 1 ), ( 1, 1 ), ( 1, 0 ) )
		self.mappings_[UIState.COMMON] = mapping
		self.mappings_[UIState.HIGHLIGHT] = mapping
		self.mappings_[UIState.PRESSED] = mapping
		self.mappings_[UIState.SELECTED] = mapping
		self.mappings_[UIState.DISABLE] = mapping

	# ---------------------------------------
	def onMouseEnter_( self ) :
		TabButton.onMouseEnter_( self )
		if self.__text != self.pyText_.text :
			toolbox.infoTip.showToolTips( self, self.__text )

	def onMouseLeave_( self ) :
		TabButton.onMouseLeave_( self )
		toolbox.infoTip.hide( self )

	def _getText( self ) :
		return self.__text

	def _setSelectedBackColor( self, color ) :
		TabButton._setSelectedBackColor( self, color )
		r, g, b, a = color
		commonColor = r, g, b, max( 0, a - 60 )
		self.commonBackColor = commonColor
		self.highlightBackColor = commonColor
		self.pressedBackColor = color
		self.disableBackColor = color

	# -------------------------------------------------
	def _setText( self, text ) :
		self.__text = text
		TabButton._setText( self, text )

	def _setWidth( self, width  ) :
		space = self.__cc_text_space * 2
		width = min( width, self.__cc_max_width )
		textWidth = self.pyText_.textWidth( self.__text )
		comWidth = self.__cc_com_width
		if textWidth < comWidth - space and width > comWidth :				# �������ȿ���С��������ȣ����ң�Ԥ���ȴ����������
			self.pyText_.text = self.__text									# ��Ԥ�����ڿ������������ı�
			TabButton._setWidth( self, comWidth )							# ��ˣ����������Ϊ�������
			self.pyText_.center = self.width * 0.5
			return
		if comWidth - space < textWidth <= width - space :					# ����ı���ȴ���
			self.pyText_.text = self.__text
			TabButton._setWidth( self, textWidth + space )
			self.pyText_.center = self.width * 0.5
			return
		text, wtext = self.pyText_.elideText( width, "CUT", self.__text )	# �������������ȡ�����ı�
		self.pyText_.text = text
		TabButton._setWidth( self, width )
		self.pyText_.center = self.width * 0.5

	def _getFitWidth( self ) :
		width = self.pyText_.textWidth( self.__text ) + self.__cc_text_space * 2
		return min( width, self.__cc_max_width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	selectedBackColor = property( TabButton._getSelectedBackColor, _setSelectedBackColor )
	width = property( TabButton._getWidth, _setWidth )
	fitWidth = property( _getFitWidth )

# -------------------------------------------------------------------
class Emote:
	def __init__( self, sign, path, dsp ):
		self.sign = sign
		self.path = path
		self.dsp = dsp