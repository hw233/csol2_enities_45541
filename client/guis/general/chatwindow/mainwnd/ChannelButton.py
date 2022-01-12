# -*- coding: gb18030 -*-
#
# $Id: ChannelLister.py,v 1.10 2008-06-27 03:16:55 huangyongwei Exp $

"""
implement channel lister class

2008.04.01: writen by huangyongwei
"""

import csdefine
import GUIFacade
from ChatFacade import chatFacade
from cscollections import MapList
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.common.FrameEx import HVFrameEx
from guis.controls.Button import Button
from guis.controls.SelectableButton import SelectableButton
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.CheckerGroup import CheckerGroup


# --------------------------------------------------------------------
# implement button for choose channel
# --------------------------------------------------------------------
class ChannelButton( Button ) :
	def __init__( self, btn ) :
		Button.__init__( self, btn )
		self.pyLister_ = ChannelLister()
		self.pyLister_.onChannelSelectChanged.bind( self.onChannelSelectChanged_ )
		self.pyLister_.pySelItem = self.pyLister_.pyItems[csdefine.CHAT_CHANNEL_NEAR]


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Button.generateEvents_( self )
		self.__onChannelSelectChanged = self.createEvent_( "onChannelSelectChanged" )

	# ---------------------------------------
	@property
	def onChannelSelectChanged( self ) :
		return self.__onChannelSelectChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onLastKeyDown( self, key, mods ) :
		"""
		����ʲô����£����¼��̼������ʱ���ᱻ����
		"""
		if ( key == KEY_LEFTMOUSE or key == KEY_RIGHTMOUSE ) and \
			( not self.isMouseHit() and not self.pyLister_.isMouseHit() ) :
				self.collapse()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onChannelSelectChanged_( self, channel ) :
		"""
		��Ƶ����ѡ��ʱ����
		"""
		self.text = channel.name
		self.commonForeColor = channel.color
		self.highlightForeColor = channel.color
		self.pressedForeColor = channel.color
		self.onChannelSelectChanged( channel )
		self.collapse()

	# -------------------------------------------------
	def onLClick_( self, mods ) :
		"""
		�������ʱ������
		"""
		Button.onLClick_( self, mods )
		self.pyLister_.left = self.leftToScreen
		self.pyLister_.bottom = self.topToScreen
		if self.pyLister_.visible :
			self.collapse()
		else :
			self.dropDown()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def dropDown( self ) :
		"""
		����Ƶ���б�
		"""
		if not self.pyLister_.visible :
			self.pyLister_.show( self )
			LastKeyDownEvent.attach( self.__onLastKeyDown )

	def collapse( self ) :
		"""
		�ر�Ƶ���б�
		"""
		if self.pyLister_.visible :
			self.pyLister_.hide()
			LastKeyDownEvent.detach( self.__onLastKeyDown )

	def selectChinnelViaID( self, id ) :
		"""
		ѡ��ָ�� ID ��Ƶ��
		"""
		self.pyLister_.selectChinnelViaID( id )

	# -------------------------------------------------
	def reset( self ) :
		"""
		���»ָ�ΪĬ��״̬
		"""
		for pyItem in self.pyItems.values() :
			pyItem.reset()
		self.pySelItem = self.pyItems[csdefine.CHAT_CHANNEL_NEAR]


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	isDropped = property( lambda self : self.pyLister_.visible )
	pyItems = property( lambda self : self.pyLister_.pyItems )
	pySelItem = property( lambda self : self.pyLister_.pySelItem, \
		lambda self, v : self.pyLister_._setSelItem( v ) )
	pyCheckItems = property( lambda self : self.pyLister_.pyCheckItems )


# --------------------------------------------------------------------
# implement channel list
# --------------------------------------------------------------------
class ChannelLister( HVFrameEx, RootGUI ) :
	def __init__( self ) :
		lister = GUI.load( "guis/general/chatwindow/mainwnd/funcbar/channel/bg.gui" )
		uiFixer.firstLoadFix( lister )
		HVFrameEx.__init__( self, lister )
		RootGUI.__init__( self, lister )
		self.focus = True
		self.crossFocus = False
		self.moveFocus = False
		self.addToMgr( "chatChannelLister" )

		self.__pyItems = MapList()
		self.__pySpliter = []											# �ָ���
		self.__pySelGroup = SelectorGroup()								# ����Ƶ��
		self.__pySelGroup.onSelectChanged.bind( self.onItemSelectChanged_ )
		self.__initChannels()											# ��ʼ������Ƶ��

		# ��ݼ�
		rds.shortcutMgr.setHandler( "CHAT_CHN_WHISPER", self.__toChannelWhisper )		# �л�������Ƶ��
		rds.shortcutMgr.setHandler( "CHAT_CHN_TEAM", self.__toChannelTeam )				# �л�������Ƶ��
		rds.shortcutMgr.setHandler( "CHAT_CHN_WORLD", self.__toChannelWorld )			# �л�������Ƶ��
		rds.shortcutMgr.setHandler( "CHAT_CHN_RUMOR", self.__toChannelRumor )			# �л���ҥ��Ƶ��
		rds.shortcutMgr.setHandler( "CHAT_CHN_COMMON", self.__toChannelCommon )			# �л�������Ƶ��
		rds.shortcutMgr.setHandler( "CHAT_CHN_CAMP", self.__toChannelCamp )				# �л�����ӪƵ��

		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_CH_TEAM", self.__toggleTeamMsg )		# ����/�򿪶���Ƶ����Ϣ
		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_CH_TONG", self.__toggleTongMsg )		# ����/�򿪰����Ϣ
		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_CH_WORLD", self.__toggleWorldMsg )		# ����/��������Ϣ
		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_CH_RUMOR", self.__toggleRumorMsg )		# ����/��ҥ��
		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_CH_COMMON", self.__toggleCommonMsg )	# ����/�򿪸�����Ϣ
		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_CH_SYSTEM", self.__toggleSystemMsg )	# ����/��ϵͳ��Ϣ
		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_CH_CAMP", self.__toggleCampMsg )		# ����/����Ӫ��Ϣ
		

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		RootGUI.generateEvents_( self )
		self.__onChannelSelectChanged = self.createEvent_( "onChannelSelectChanged" )			# ��ѡ��״̬�ı�ʱ����

	@property
	def onChannelSelectChanged( self ) :
		"""
		����ѡ��ʱ����
		"""
		return self.__onChannelSelectChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initChannels( self ) :
		"""
		��ʼ������Ƶ��
		"""
		sendableChns = [ chn for chn in chatFacade.setableChannels if chn.sendable ]
		if len( sendableChns ) == 0 : return
		spliter = GUI.load( "guis/general/chatwindow/mainwnd/funcbar/channel/chnspliter.gui" )
		v_offset = top = 6											# ��ֱƫ�ƣ���ʼ����λ��
		h_offset = 4												# ˮƽƫ��
		maxWidth = 0												# ���Ƶ��item�Ŀ��
		chnNameFmt = "%s(/%s)"
		def addChnItem( top, channel ) :
			pyItem = ChannelItem( channel, self )
			pyItem.foreColor = channel.color
			shortcut = chatFacade.chidToShortcut( channel.id )
			if shortcut is None : shortcut = "?"
			pyItem.text = chnNameFmt % ( channel.name, shortcut )
			self.addPyChild( pyItem )
			pyItem.pos = ( h_offset, top )
			pyItem.onItemLClick.bind( self.onItemLClick_ )
			self.__pyItems[channel.id] = pyItem
			self.__pySelGroup.addSelector( pyItem )
			return pyItem
		def addSpliter( top ) :
			pySpliter = PyGUI( util.copyGuiTree( spliter ) )
			self.addPyChild( pySpliter )
			pySpliter.top = top
			self.__pySpliter.append( pySpliter )
			return pySpliter
		for channel in sendableChns[:-1] :
			pyChn = addChnItem( top, channel )
			maxWidth = max( maxWidth, pyChn.width )
			pySpliter = addSpliter( pyChn.bottom )
			top = pySpliter.bottom
		pyChn = addChnItem( top, sendableChns[-1] )
		self.width = maxWidth + 2 * h_offset
		self.height = pyChn.bottom + v_offset
		for pySpliter in self.__pySpliter :
			pySpliter.width = maxWidth
			pySpliter.center = self.width * 0.5

	# -------------------------------------------------
	def __toChannelWhisper( self ) :
		"""
		�л�������Ƶ��
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_WHISPER )
		return True

	def __toChannelTeam( self ) :
		"""
		�л�������Ƶ��
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_TEAM )
		return True

	def __toChannelWorld( self ) :
		"""
		�л�������Ƶ��
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_WORLD )
		return True

	def __toChannelRumor( self ) :
		"""
		�л���ҥ��Ƶ��
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_RUMOR )
		return True

	def __toChannelCommon( self ) :
		"""
		�л�������Ƶ��
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_NEAR )
		return True
	
	def __toChannelCamp( self ) :
		"""
		�л�����ӪƵ��
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_CAMP )
		return True

	# ---------------------------------------
	def __toggleTeamMsg( self ) :
		"""
		����/�򿪶���Ƶ����Ϣ
		"""
		pyItem = self.__pyItems[csdefine.CHAT_CHANNEL_TEAM]
		pyItem.checked = not pyItem.checked
		return True

	def __toggleTongMsg( self ) :
		"""
		����/�򿪰����Ϣ
		"""
		pyItem = self.__pyItems[csdefine.CHAT_CHANNEL_TONG]
		pyItem.checked = not pyItem.checked
		return True

	def __toggleWorldMsg( self ) :
		"""
		����/��������Ϣ
		"""
		pyItem = self.__pyItems[csdefine.CHAT_CHANNEL_WORLD]
		pyItem.checked = not pyItem.checked
		return True

	def __toggleRumorMsg( self ) :
		"""
		����/��ҥ��
		"""
		pyItem = self.__pyItems[csdefine.CHAT_CHANNEL_RUMOR]
		pyItem.checked = not pyItem.checked
		return True

	def __toggleCommonMsg( self ) :
		"""
		����/�򿪸�����Ϣ
		"""
		pyItem = self.__pyItems[csdefine.CHAT_CHANNEL_NEAR]
		pyItem.checked = not pyItem.checked
		return True

	def __toggleSystemMsg( self ) :
		"""
		����/��ϵͳ��Ϣ
		"""
		pyItem = self.__pyItems[csdefine.CHAT_CHANNEL_SYSTEM]
		pyItem.checked = not pyItem.checked
		return True
	
	def __toggleCampMsg( self ) :
		"""
		����/����Ӫ��Ϣ
		"""
		pyItem = self.__pyItems[csdefine.CHAT_CHANNEL_CAMP]
		pyItem.checked = not pyItem.checked
		return True

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onItemSelectChanged_( self, pyItem ) :
		"""
		��һ��Ƶ��ѡ����ʱ����
		"""
		self.onChannelSelectChanged( pyItem.channel )
		self.hide()

	def onItemLClick_( self, pyItem ) :
		"""
		��ĳѡ�������ʱ����
		"""
		self.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def selectChinnelViaID( self, id ) :
		"""
		ѡ��ָ�� ID ��Ƶ��
		"""
		for pyItem in self.__pySelGroup.pySelectors :
			if pyItem.channel.id == id :
				if not pyItem.selected :
					pyItem.selected = True
				else :
					self.onChannelSelectChanged( pyItem.channel )
				break


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setVisible( self, visible ) :
		if visible : self.hide()
		else : self.show( self.pyOwner )

	# -------------------------------------------------
	def _getItems( self ) :
		return self.__pyItems

	def _getChannelCount( self ) :
		return len( self.__pyItems )

	# -------------------------------------------------
	def _getSelItem( self ) :
		return self.__pySelGroup.pyCurrSelector

	def _setSelItem( self, pyItem ) :
		pyItem.selected = True

	def _getCheckedItems( self ) :
		pyItems = []
		for pyItem in self.__pySelGroup.pySelectors :
			if pyItem.checked :
				pyItems.append( pyItem )
		return pyItems


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	visible = property( RootGUI._getVisible, _setVisible )			# ���ÿɼ���
	pyItems = property( _getItems )									# ��ȡ����Ƶ��
	channelCount = property( _getChannelCount )						# ��ȡƵ������
	pySelItem = property( _getSelItem, _setSelItem )				# ��ȡ/���õ�ǰ���ѡ�е�Ƶ��
	pyCheckItems = property( _getCheckedItems )						# ��ȡ��ǰ Check ѡ�е�����Ƶ��


# --------------------------------------------------------------------
# implement channel item class
# --------------------------------------------------------------------
class ChannelItem( Control ) :
	def __init__( self, channel, pyBinder ) :
		item = GUI.load( "guis/general/chatwindow/mainwnd/funcbar/channel/item.gui" )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item, pyBinder )
		self.__channel = channel									# ��Ӧ��Ƶ��
		self.__initialize( item, channel )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item, channel ) :
		self.pyBtnSend_ = SelectableButton( item.btnSend )						# ����Ƶ��
		#self.pyBtnSend_.text = channel.name
		self.pyBtnSend_.commonBackColor = 255, 255, 255, 0
		self.pyBtnSend_.highlightBackColor = 10, 36, 106, 255
		self.pyBtnSend_.onSelectChanged.bind( self.onItemSelectChanged_ )
		self.pyBtnSend_.onLClick.bind( self.onBtnSendLClick_ )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Control.generateEvents_( self )
		self.__onItemLClick = self.createEvent_( "onItemLClick" )				# ��ѡ�������ʱ����
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )			# ��ѡ��״̬�ı�ʱ����

	@property
	def onItemLClick( self ) :
		return self.__onItemLClick

	@property
	def onSelectChanged( self ) :
		"""
		����ѡ��ʱ����
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onItemSelectChanged_( self, selected ) :
		"""
		����Ƶ����ѡ��ʱ����
		"""
		self.onSelectChanged( selected )

	def onBtnSendLClick_( self ) :
		"""
		������ʱ������
		"""
		self.onItemLClick()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		��������Ƶ��״̬
		"""
		self.pyBtnSend_.commonForeColor = self.__channel.color
		self.pyBtnSend_.highlightForeColor = self.__channel.color
		self.pyBtnSend_.selectedForeColor = self.__channel.color


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getChannel( self ) :
		return self.__channel

	# ---------------------------------------
	def _getChannelName( self ) :
		return self.__pyText.text

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.__pyText.color

	def _setForeColor( self, color ) :
		self.__pyText.color = color

	# ---------------------------------------
	def _setText( self, text ) :
		pyText = self.pyBtnSend_.pyText_
		pyText.text = text
		self.pyBtnSend_.width = pyText.width
		pyText.center = self.pyBtnSend_.width * 0.5
		self.pyBtnSend_.text = text
		self.width = self.pyBtnSend_.right + 2

	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	channel = property( _getChannel )									# Ƶ��
	selected = property( lambda self : self.pyBtnSend_.selected, \
		lambda self, v : self.pyBtnSend_._setSelected( v ) )			# ѡ��Ƶ��
	height = property( lambda self : self.pyBtnSend_.height + 5 )		# ���ø߶�Ϊֻ��
	text = property( lambda self : self.pyBtnSend_.text, _setText )		# �����ı�
