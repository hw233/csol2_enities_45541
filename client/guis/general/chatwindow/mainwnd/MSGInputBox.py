# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement text for input message

2009/03/17: writen by huangyongwei
"""

import weakref
import csconst
from ChatFacade import emotionParser, chatFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.ODListWindow import ODListWindow
from guis.controls.Control import Control
from guis.controls.ODComboBox import ODComboBox, IBox
from guis.controls.Button import Button
from guis.tooluis.CSRichTextBox import CSRichTextBox
from guis.tooluis.fulltext.FullText import FullText as BaseFullText
from guis.tooluis.CSRichTextBox import EItem
from guis.tooluis.CSRichTextBox import LItem

class MSGInputBox( Control ) :
	__cc_history_maxcount	= 60

	def __init__( self, box, pyBinder ) :
		Control.__init__( self, box, pyBinder )
		self.pyCBInput_ = ODComboBox( box.cbMSG, InputBox )						# ��Ϣ�����
		self.pyCBInput_.itemHeight = emotionParser.cc_emote_size[1]
		self.pyCBInput_.ownerDraw = True
		self.pyCBInput_.h_dockStyle = "HFILL"
		self.pyCBInput_.readOnly = False
		self.pyCBInput_.viewCount = 16
		self.pyCBInput_.viewItem = ""
		self.pyCBInput_.pyComboList_.posZSegment = ZSegs.L4
		self.pyCBInput_.pyBox.maxLength = csconst.CHAT_MESSAGE_UPPER_LIMIT
		self.pyCBInput_.onViewItemInitialized.bind( self.__onInputBoxInitialized )
		self.pyCBInput_.onDrawItem.bind( self.__onInputBoxDrawItem )
		self.pyCBInput_.onItemMouseEnter.bind( self.__onInputBoxMouseEnter )
		self.pyCBInput_.onItemMouseLeave.bind( self.__onInputBoxMouseLeave )
		self.pyCBInput_.onKeyDown.bind( self.onKeyDown_ )
		self.pyCBInput_.onTabIn.bind( self.onTabIn_ )
		self.pyCBInput_.onTabOut.bind( self.onTabOut_ )

		self.pyActionsBtn_ = Button( box.actionsBtn )							# ��Ϊ�б�ť
		self.pyActionsBtn_.h_dockStyle = "RIGHT"
		self.pyActionsBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyActionsBtn_.onLClick.bind( self.__showActionList )
		self.pyEmoteBtn_ = Button( box.emoteBtn )								# ����ѡ��
		self.pyEmoteBtn_.h_dockStyle = "RIGHT"
		self.pyEmoteBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyEmoteBtn_.onLClick.bind( self.__showEmotions )

		self.__tmpMsg = ""														# ���浱ǰ�������Ϣ


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		Control.generateEvents_( self )
		self.__onMessageReady = self.createEvent_( "onMessageReady" )			# ��Ϣ׼���ã�֪ͨ����

	@property
	def onMessageReady( self ) :
		"""
		������ĳ����������Ϣʱ������
		"""
		return self.__onMessageReady


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onInputBoxInitialized( self, pyViewItem ) :
		"""
		��ʼ����ʷѡ��
		"""
		box = util.copyGui( pyViewItem.gui )
		pyViewItem.gui.addChild( box )
		pyBox = CSRichTextBox( box )
		pyBox.font = self.pyCBInput_.font
		pyBox.width -= 8
		pyBox.pos = 4, 0
		pyBox.readOnly = True
		pyBox.canTabIn = False
		pyBox.focus = False
		pyBox.moveFocus = False
		pyBox.crossFocus = False
		pyBox.vTextAlign = "MIDDLE"
		pyViewItem.pyBox = pyBox

	def __onInputBoxDrawItem( self, pyViewItem ) :
		"""
		�ػ���ʷѡ��
		"""
		pyBox = pyViewItem.pyBox
		pyBox.width = pyViewItem.width - 8
		if pyViewItem.selected :
			pyBox.foreColor = self.pyCBInput_.itemSelectedForeColor				# ѡ��״̬�µ�ǰ��ɫ
			pyViewItem.color = self.pyCBInput_.itemSelectedBackColor			# ѡ��״̬�µı���ɫ
		elif pyViewItem.highlight :
			pyBox.foreColor = self.pyCBInput_.itemHighlightForeColor			# ����״̬�µ�ǰ��ɫ
			pyViewItem.color = self.pyCBInput_.itemHighlightBackColor			# ����״̬�µı���ɫ
		else :
			pyBox.foreColor = self.pyCBInput_.itemCommonForeColor
			pyViewItem.color = self.pyCBInput_.itemCommonBackColor
		pyBox.text = pyViewItem.listItem

	def __onInputBoxMouseEnter( self, pyViewItem ) :
		"""
		������ѡ��
		"""
		pyBox = pyViewItem.pyBox
		if pyBox.textWidth > pyBox.width :
			FullText.show( pyViewItem, pyBox )

	def __onInputBoxMouseLeave( self, pyViewItem ) :
		"""
		����뿪ѡ��
		"""
		FullText.hide()

	# -------------------------------------------------
	def __onEmotionChosen( self, sign ) :
		"""
		ĳ������ѡ��ʱ������
		"""
		if rds.ruisMgr.emotionBox.pyBinder == self :
			if not self.pyCBInput_.tabStop :
				self.pyCBInput_.tabStop = True
			self.pyCBInput_.pyBox.notifyInput( sign )

	# -------------------------------------------------
	def __showActionList( self ) :
		"""
		��ʾ��Ϊ�����б�
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_SKILL_WINDOW", 3 )

	def __showEmotions( self ) :
		"""
		��ʾ����ѡ�񴰿�
		"""
		emotionBox = rds.ruisMgr.emotionBox
		emotionBox.toggle( self.__onEmotionChosen, self )
		emotionBox.left = self.leftToScreen + 15.0
		emotionBox.bottom = self.topToScreen + 10.0
		if not self.pyCBInput_.tabStop :
			self.pyCBInput_.tabStop = True


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		��������������У����а�������ʱ������
		"""
		return Control.onKeyDown_( self, key, mods )

	def onTabIn_( self ) :
		"""
		��ý���ʱ������( ���Ǹ���� onTabIn_ ���� )
		"""
		self.onTabIn()
		rds.helper.courseHelper.openWindow( "liaotian_chuangkou" )

	def onTabOut_( self ) :
		"""
		ʧȥ����ʱ������( ���Ǹ���� onTabOut_ ���� )
		"""
		self.onTabOut()
		rds.ruisMgr.emotionBox.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def insertMessage( self, text ) :
		"""
		����Ϣ�����������һ���ı�
		ע���ṩ����ӿڲ��Ǻ�ǡ���������ȷʵ��Ҫ�ýӿ�
		"""
		if not self.tabStop : self.tabStop = True
		self.pyCBInput_.pyBox.notifyInput( text, 4 )						# ������Ʒ���ֵ��������� 4

	def saveMessage( self, text ) :
		"""
		����һ����Ϣ����ʷ�б�
		"""
		text = text.strip()
		if text == "" : return
		if text in self.pyCBInput_.items :									# ��ʷ�б����Ѿ����ڸ�������
			self.pyCBInput_.sort( key = lambda pyItem : pyItem == text )	# ��������ù��������߷ŵ����
		else :
			if self.pyCBInput_.itemCount >= self.__cc_history_maxcount :	# �����ʷ�����Ѿ�����ָ��ֵ
				self.pyCBInput_.removeItemOfIndex( 0 )						# ɾ����ǰ��һ��
			self.pyCBInput_.addItem( text )									# �����µ���ӵ����
		self.pyCBInput_.selIndex = self.pyCBInput_.itemCount - 1			# ѡ��������ӵ�ѡ��

	def notifyInput( self, text ) :
		"""
		����Ϣ�����������һ���ı�
		����ӿ���msgInserter��ʹ��
		"""
		self.insertMessage( text )

	# -------------------------------------------------
	def reset( self ) :
		"""
		���»ָ�ΪĬ��״̬
		"""
		self.pyCBInput_.pyBox.text = ""
		self.pyCBInput_.clearItems()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( lambda self : self.pyCBInput_.pyBox.text, \
		lambda self, v : self.pyCBInput_.pyBox._setText( v ) )
	wtext = property( lambda self : self.pyCBInput_.pyBox.wtext )
	viewText = property( lambda self : self.pyCBInput_.pyBox.viewText )
	tabStop = property( lambda self : self.pyCBInput_.tabStop, \
		lambda self, v : self.pyCBInput_._setTabStop( v ) )


# --------------------------------------------------------------------
# ��д�����
# --------------------------------------------------------------------
class InputBox( CSRichTextBox, IBox ) :
	__cc_exposed_attrs = set( [
		"text",											# ��ǰ�ı�
		] )												# ��Ҫ������Ϊ ComboBox ���Ե�����

	def __init__( self, box, pyBombo ) :
		CSRichTextBox.__init__( self, box )
		IBox.__init__( self, pyBombo )
		self.__followSelCBID = 0							# �����ı�ʱ������ѡ���б�ѡ��� callback ID

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __selectStartswithInput( self ) :
		"""
		ѡ���� box ��������ı���ͷ��ѡ��
		"""
		if self.readOnly : return								# ֻ���ڷ�ֻ��ʱ���Ż�����ı����е��ı���ѡ���ı���һ�µ�����
		wtext = self.wtext
		if wtext == "" : return									# ���ı�������
		pyComboList_ = self.pyComboList_
		items = []
		for index, item in enumerate( pyComboList_.items ) :	# ��ȡ�б��������� Box ���ı���ͷ��ѡ��
			if item.startswith( wtext ) :
				items.append( ( index, item ) )
		if len( items ) == 0 :									# ���û���� Box ���ı���ͷ��ѡ��
			pyComboList_.selIndex = -1							# ��Ԥ��ѡ���κ�ѡ��
		else :													# ����
			items.sort( key = lambda item : item[1] )			# ѡ���б��е�һ��ѡ��
			pyComboList_.selIndex = items[0][0]

	def __switchChannel( self, text ) :
		if text == "" or text[0] != "/" : return
		cmds = text.split( " " )								# ���ָ��
		if len( cmds ) < 2 : return
		shortcut = cmds[0][1:]									# ȡָ��֣���ȥ��"/"��
		chid = chatFacade.shortcutToCHID( shortcut )
		if chid is None : return
		self.pyTopParent.selectChinnelViaID( chid )				# pyTopParent��ChatWindow
		self.text = text[len(cmds[0])+1:]						# ���¸�ֵΪ��ָ��֣�+1���������һ���ո�һ��ȥ����


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onBeforeDropDown_( self ) :
		"""
		��ʾѡ���б�ǰ������
		"""
		self.__selectStartswithInput()

	# -------------------------------------------------
	def getExposedAttr_( self, name ) :
		"""
		ͨ����д�÷������԰� Box ������ת��Ϊ ComboBox ������
		"""
		if name in self.__cc_exposed_attrs :
			return getattr( self, name )
		return IBox.getExposedAttr_( self, name )

	def setExposedAttr_( self, name, value ) :
		"""
		ͨ����д�÷������԰� Box ������ת��Ϊ ComboBox ������
		"""
		if name in self.__cc_exposed_attrs :
			setattr( self, name, value )
		IBox.setExposedAttr_( self, name, value )

	def getViewItem_ ( self ) :
		"""
		��ȡ��ǰ Box �е����ݣ���� readOnly Ϊ True���������� selItem ��
		"""
		return self.viewText

	def setViewItem_( self, viewItem ) :
		"""
		���õ�ǰ Box �е����ݣ���� readOnly Ϊ True������Ӧ������һ��
		"""
		if not self.readOnly :
			self.text = viewItem
		else :
			IBox.setViewItem_( self, viewItem )

	# -------------------------------------------------
	def onTextChanged_( self ) :
		"""
		�ı��ı�ʱ�����ã����� combobox ���ı��� textbox ���ı�һ��
		"""
		CSRichTextBox.onTextChanged_( self )
		self.__switchChannel( self.text )							# �����л�����ݼ�ָ����Ƶ��
		pyEItems = []
		for pyElem in self.pyElems_:
			if isinstance( pyElem, EItem ) or isinstance( pyElem,LItem ):
				pyEItems.append( pyElem )
		chatFacade.onChatObjCount( len( pyEItems ) )
		if not self.pyComboBox.isDropped : return
		BigWorld.cancelCallback( self.__followSelCBID )
		self.__followSelCBID = BigWorld.callback( 0.3, self.__selectStartswithInput )

	def onItemSelectChanged_( self, index ) :
		"""
		ѡ��ı�ʱ������
		"""
		if index < 0 :
			self.text = ""
		else :
			self.text = self.pyComboBox.items[index]


# --------------------------------------------------------------------
# ��д�����
# --------------------------------------------------------------------
class FullText( BaseFullText ) :
	def __init__( self ) :
		BaseFullText.__init__( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onFullDuplicate_( self, pyUI ) :
		"""
		����Ҫ��ȫ��ʾ�� UI ����
		"""
		gui = self.gui
		dup = util.copyGuiTree( pyUI.gui )
		dup.scroll = 0, 0
		dup.width = pyUI.textWidth
		gui.addChild( dup, "dup" )
		self.__pyDup = PyGUI( dup )
		self.__pyDup.pos = self.edgeLeft_, self.edgeTop_
		self.width = self.__pyDup.width + self.edgeLeft_ * 2
		self.height = self.__pyDup.height + self.edgeTop_ * 2
