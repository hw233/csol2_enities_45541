# -*- coding: gb18030 -*-
#
# $Id: MessagePanel.py,v 1.10 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement panel for showing chating message

2009/04/07: writen by huangyongwei
"""

import copy
import ResMgr
import csdefine
import csconst
from ChatFacade import chatFacade
from event import EventCenter as ECenter
from LabelGather import labelGather
from guis import *
from guis.controls.TabCtrl import TabCtrl
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.tooluis.inputbox.InputBox import InputBox
from guis.tooluis.colorboard.ColorBoard import ColorBoard
from MSGPage import MSGPage, GatherPage, PersonalPage, CombatPage, TongPage, TongBattlePage
from guis.general.chatwindow.channelfilter.ChannelFilter import ChannelFilter
from guis.general.chatwindow.channelcolorsetter.ColorSetter import ColorSetter

class MSGReceiver( TabCtrl ) :
	__cc_page_cfg_name	= "chat_pages.xml"			# ��ҳ�����ļ�����
	__cc_max_pagecount	= 8							# ����ܴ������ٸ���ҳ
	__cc_tab_left		= 4							# ��ҳ��ť�����
	__cc_tab_space		= 4							# ÿ����ҳ��ť�ļ������
	__family_chid		= 4							# ����Ƶ��id

	def __init__( self, msgBg, pyBinder ) :
		TabCtrl.__init__( self, msgBg, pyBinder )
		self.rMouseSelect = True
		self.pyFixedPages_ = MapList()				# ϵͳ����ģ��������û�ɾ��������ķ�ҳ
		self.pyMSGPages_ = []						# ��˳�򱣴����з�ҳ�����������ϵͳ�̶���ҳ��
		self.__initFixedPages( msgBg )				# ��ʼ������ϵͳ����ķ�ҳ
		self.__initOPMenu()							# ��ʼ���Ҽ��˵�

		self.__cfgPath = ""
		self.__cfgSect = None
		self.__layoutCBID = 0						# ��ȸı�ʱ��������ť��ȸı䣨��ʱһ�ᴦ��

		self.__triggers = {}
		self.__registerTriggers()

		rds.shortcutMgr.setHandler( "CHAT_UP_HISTORY", self.__upScrollHistory )			# ���Ϲ�����ʷ��Ϣ
		rds.shortcutMgr.setHandler( "CHAT_DOWN_HISTORY", self.__downScrollHistory )		# ���¹�����ʷ��Ϣ
		rds.shortcutMgr.setHandler( "CHAT_END_HISTORY", self.__scrollMSGToEnd )			# ��������Ϣ��Ͷ�


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		TabCtrl.generateEvents_( self )
		self.__onLinkMessageLClick = self.createEvent_( "onLinkMessageLClick" )
		self.__onLinkMessageRClick = self.createEvent_( "onLinkMessageRClick" )

	@property
	def onLinkMessageLClick( self ) :
		"""
		������ĳ����������Ϣʱ������
		"""
		return self.__onLinkMessageLClick

	@property
	def onLinkMessageRClick( self ) :
		"""
		�Ҽ����ĳ����������Ϣʱ������
		"""
		return self.__onLinkMessageRClick


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_BEFORE_GAME_QUIT"] = self.onGameQuit
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# -----------------------------------------------------------
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

	def __createPage( self, CLS, name, layout = False ) :
		"""
		������ҳ
		"""
		pyPage = CLS( self )
		pyPage.pgName = name
		pyPage.onTabMouseUp.bind( self.onPageTabMouseUp_ )
		pyPage.pyMSGPanel.onLinkMessageLClick.bind( self.onLinkMessageLClick_ )
		pyPage.pyMSGPanel.onLinkMessageRClick.bind( self.onLinkMessageRClick_ )
		self.addPage( pyPage )
		pyPage.size = self.size
		pyPage.h_dockStyle = "HFILL"
		pyPage.v_dockStyle = "VFILL"
		if layout : self.__layoutPages()
		return pyPage

	def __initFixedPages( self, msgBg ) :
		"""
		��ʼ�����й̶���Ϣ����
		"""
		pgGatherText = labelGather.getText( "ChatWindow:MSGReceiver", "tpGather" )		# �ۺϷ�ҳ
		pgPersonalText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_PERSONAL]		# ���˷�ҳ
		pgCombatText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_COMBAT]			# ս����ҳ
		pgTongText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG]				# ����ҳ
		pgTongActivityText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG_CITY_WAR]		# ���ս����ҳ
		self.pyUPage_ = self.__createPage( GatherPage, pgGatherText )
		self.pyFixedPages_[pgGatherText] = self.pyUPage_
		self.pyFixedPages_[pgPersonalText] = self.__createPage( PersonalPage, pgPersonalText )
		self.pyFixedPages_[pgCombatText] = self.__createPage( CombatPage, pgCombatText )
		self.pyFixedPages_[pgTongText] = self.__createPage( TongPage, pgTongText )
		self.pyFixedPages_[pgTongActivityText] = self.__createPage( TongBattlePage, pgTongActivityText )

	# ---------------------------------------
	def __initOPMenu( self ) :
		"""
		��ʼ�������˵�
		"""
		self.pyOPMenu_ = ContextMenu()
		self.pyOPMenu_.onBeforePopup.bind( self.__onMenuBeforePopup )
		self.pyOPMenu_.onAfterClose.bind( self.__onMenuAfterClosed )
		self.pyOPMenu_.onItemClick.bind( self.onOPMeuItemClick_ )

		# ����ҳ����صĲ����˵���
		self.pyFreeItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miUnlock" ) )
		self.pyFreeItem_.handler = self.__freePage
		self.pyRenameItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miRename" ) )
		self.pyRenameItem_.handler = self.__renamePage
		self.pyResetItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miReset" ) )
		self.pyResetItem_.handler = self.__resetPage
		self.pySetBCItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miBackColor" ) )
		self.pySetBCItem_.handler = self.__setPageColor
		self.pySetCHItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miSetChannel" ) )
		self.pySetCHItem_.handler = self.__configPage
		self.pyRemoveItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miDelete" ) )
		self.pyRemoveItem_.handler = self.__deletePage

		# �ָ���
		pySpliter = DefMenuItem( style = MIStyle.SPLITTER )

		# ����ҳ���޹صĲ���
		self.pyAddItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miCreate" ) )
		self.pyAddItem_.handler = self.__addPage
		self.pyCHColorItem_ = DefMenuItem( labelGather.getText( "ChatWindow:pgMenu", "miSetColor" ) )
		self.pyCHColorItem_.handler = self.__setChannelColor

		self.pyOPMenu_.pyItems.adds( ( \
			self.pyFreeItem_, self.pyRenameItem_, \
			self.pyResetItem_, self.pySetBCItem_, \
			self.pySetCHItem_, self.pyRemoveItem_, \
			pySpliter, \
			self.pyAddItem_, self.pyCHColorItem_ ) )

	def __onMenuBeforePopup( self, pyMenu ) :
		"""
		�����˵�ǰ������
		"""
		pyPage = pyMenu.pyBinders[0].pyTabPage
		if pyPage.unlockable :							# ���ɽ����ķ�ҳ
			self.pyFreeItem_.enable = False
		else :											# ���Խ����ķ�ҳ
			if not pyPage.docked :
				self.pyFreeItem_.text = labelGather.getText( "ChatWindow:pgMenu", "miDock" )
			elif pyPage.locked :						# ��ҳ��������״̬
				self.pyFreeItem_.text = labelGather.getText( "ChatWindow:pgMenu", "miUnlock" )
			else :										# ��ҳ���ڽ���״̬
				self.pyFreeItem_.text = labelGather.getText( "ChatWindow:pgMenu", "miLock" )
			self.pyFreeItem_.enable = True

		deletable = pyPage.deletable
		self.pyRemoveItem_.enable = deletable			# �Ƴ���ҳ��״̬
		self.pyRenameItem_.enable = deletable			# �����Ƴ��ķ�ҳ����������
		self.pyAddItem_.enable = \
			self.pageCount < self.__cc_max_pagecount	# �Ƿ��������·�ҳ
		return True

	def __onMenuAfterClosed( self, pyMenu ) :
		"""
		����˵�ʱ������
		"""
		pyMenu.clearBinders()

	# -------------------------------------------------
	def __isPageNameExist( self, name ) :
		"""
		��ҳ�����Ƿ��Ѿ�����
		"""
		for pyPage in self.pyMSGPages_ :
			if name == pyPage.pgName :
				return True
		return False

	# -------------------------------------------------
	def __upScrollHistory( self ) :
		"""
		���Ϲ�����ʷ��Ϣ
		"""
		self.pySelPage.pyMSGPanel.upScrollHistory()
		return True

	def __downScrollHistory( self ) :
		"""
		���¹�����ʷ��Ϣ
		"""
		self.pySelPage.pyMSGPanel.downScrollHistory()
		return True

	def __scrollMSGToEnd( self ) :
		"""
		��������Ϣ��Ͷ�
		"""
		self.pySelPage.pyMSGPanel.scrollToEnd()
		return True

	# -------------------------------------------------
	def __freePage( self, pyPage ) :
		"""
		����/������ҳ
		"""
		if not pyPage.docked :						# �����ҳ���ڷ���״̬
			pyPage.dock( self.pageCount )			# ����ҳͣ�������
		else :
			pyPage.locked = not pyPage.locked

	def __renamePage( self, pyPage ) :
		"""
		������
		"""
		def callback( res, text ) :
			if res == DialogResult.OK and text.strip() != "" :
				if self.__isPageNameExist( text ) :
					showAutoHideMessage( 3.0, 0x0244, "", MB_OK )
				else :
					pyPage.pgName = text
					self.__layoutPages()
		tips = labelGather.getText( "ChatWindow:MSGReceiver", "InputBoxTips" )
		InputBox().show( tips, callback, self )

	def __resetPage( self, pyPage ) :
		"""
		���÷�ҳ
		"""
		pyPage.reset()

	def __setPageColor( self, pyPage ) :
		"""
		��ɫ
		"""
		def cbChanging( color ) :
			pyPage.color = color
		def cbResult( res, color ) :
			pyPage.color = color
		pyBtn = pyPage.pyBtn
		left = self.pyTopParent.rightToScreen
		top = pyBtn.topToScreen
		ColorBoard().show( self, pyPage.color, cbResult, cbChanging, ( left, top ) )

	def __configPage( self, pyPage ) :
		"""
		Ƶ������
		"""
		def callback( ok, checkedChannels ) :
			if ok : pyPage.careCHIDs = checkedChannels
		ChannelFilter().show( pyPage.pgName, pyPage.careCHIDs, callback, pyPage )

	def __deletePage( self, pyPage ) :
		"""
		�Ƴ���ҳ
		"""
		if not pyPage.deletable : return
		self.removePage( pyPage )
		self.pyMSGPages_.remove( pyPage )
		pyPage.dispose()
		self.__layoutPages()

	# ---------------------------------------
	def __addPage( self, pyPage ) :
		"""
		�����·�ҳ
		"""
		def callback( res, title ) :
			if res == DialogResult.OK and title.strip() != "" :
				if self.__isPageNameExist( title ) :
					showAutoHideMessage( 3.0, 0x0244, "", MB_OK )
				else :
					pyPage = self.__createPage( MSGPage, title, True )
					self.pyMSGPages_.append( pyPage )
		tips = labelGather.getText( "ChatWindow:MSGReceiver", "InputBoxTips" )
		InputBox().show( tips, callback, self )

	def __setChannelColor( self, pyPage ) :
		"""
		����Ƶ����ɫ
		"""
		def cbChanging( chid, color ) :
			"""
			ĳƵ������ɫ���øı�ʱ������
			"""
			for pyPage in self.pyPages :
				pyPage.pyMSGPanel.resetMSGColor( { chid : color } )

		def cbResult( res, chcolors ) :
			"""
			Ƶ����ɫ�ı�󱻵���
			"""
			for pyPage in self.pyPages :
				pyPage.pyMSGPanel.resetMSGColor( chcolors )
			chatFacade.saveChannelConfig()
		ColorSetter().show( pyPage, cbResult, cbChanging )

	# -------------------------------------------------
	def __saveConfig( self ) :
		"""
		���������ļ�
		"""
		if self.__cfgSect is None :
			return
		for name, sect in self.__cfgSect.items() :					# ���������ѡ��
			self.__cfgSect.deleteSection( name )
		for pyPage in self.pyMSGPages_ :							# ����д��ÿһҳ��Ϣ
			sect = self.__cfgSect.createSection( pyPage.pgName )
			sect.writeVector4( "color", pyPage.color )
			chsect = sect.createSection( "chids" )					# ��ע��Ƶ���б�
			chsect.writeInts( "item", tuple( pyPage.careCHIDs) )
			sect.writeBool( "docked", pyPage.docked )
			sect.writeVector2( "pos", pyPage.pos )
			sect.writeVector2( "size", pyPage.size )
		try :
			self.__cfgSect.save()
		except IOError, err :
			ERROR_MSG( "save chat pages failed!" )
			
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onWidthChanged_( self, oldWidth ) :
		"""
		���ҵĿ�ȸı�ʱ������
		"""
		TabCtrl.onWidthChanged_( self, oldWidth )
		BigWorld.cancelCallback( self.__layoutCBID )
		self.__layoutCBID = BigWorld.callback( 0.3, self.__layoutPages )

	def onPageSelected_( self, pyPage ) :
		"""
		ҳ�汻ѡ��ʱ����
		"""
		TabCtrl.onPageSelected_( self, pyPage )
		for pyTmpPage in self.pyMSGPages_ :			# �������ֵ
			pyTmpPage.posZ = 0.9					# ��֤ѡ�еķ�ҳ����ǰ��
		pyPage.posZ = 0.1
		self.resort()

	# -------------------------------------------------
	def onLinkMessageLClick_( self, pyCom ) :
		"""
		������ĳ����������Ϣʱ������
		"""
		self.onLinkMessageLClick( pyCom )

	def onLinkMessageRClick_( self, pyCom ) :
		"""
		�Ҽ����ĳ����������Ϣʱ������
		"""
		self.onLinkMessageRClick( pyCom )

	# ---------------------------------------
	def onOPMeuItemClick_( self, pyMenu, pyItem ) :
		"""
		����˵�ѡ��ʱ������
		"""
		pyPage = pyMenu.pyBinders[0].pyTabPage
		pyItem.handler( pyPage )

	def onPageTabMouseUp_( self, pyBtn ) :
		"""
		�Ҽ����ҳ��ʱ������
		"""
		self.pyOPMenu_.addBinder( pyBtn )
		self.pyOPMenu_.popup()

	# -------------------------------------------------
	def onPageLeft_( self, pyPage ) :
		"""
		��ҳ����ʱ������
		"""
		pyPage.h_dockStyle = "LEFT"				# ���ͣ��
		pyPage.v_dockStyle = "TOP"
		self.removePage( pyPage )
		self.pyPages[0].selected = True
		self.__layoutPages()

	def onPageDocked_( self, pyPage, index ) :
		"""
		ͣ����ҳʱ������
		"""
		self.addPyChild( pyPage )
		pyPage.pos = self.pyPages[0].pos
		pyPage.size = self.size
		self.insertPage( index + 1, pyPage )
		pyPage.selected = True
		pyPage.h_dockStyle = "HFILL"			# ��������ͣ��״̬
		pyPage.v_dockStyle = "VFILL"
		self.__layoutPages()

	def onPageMoving_( self, pyPage ) :
		"""
		��ҳ�϶������б�����
		"""
		if s_util.isMouseHit( self.gui ) :
			for pyPage in self.pyPages :
				pyBtn = pyPage.pyBtn
				if pyBtn.isMouseHit() :
					pyBtn.showDropMarker()
				else :
					pyBtn.hideDropMarker()

	def onPageStopMoving_( self, pyMovPage ) :
		"""
		��ҳֹͣ�϶�ʱ������
		"""
		index = -1
		pyPages = self.pyPages
		for idx, pyPage in enumerate( pyPages ) :
			pyPage.pyBtn.hideDropMarker()
			if pyPage.pyBtn.isMouseHit() :
				index = idx
		if index >= 0 :
			pyMovPage.dock( index )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	# ---------------------------------------
	def onEnterWorld( self ) :
		"""
		��������ҳ��( onEenterWorld ʱ������ )
		"""
		setableCHIDs = set( chatFacade.getSetableCHIDs() )				# ���п�����Ƶ��
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]	# ��ǰ�˺���
		roleName = rds.gameMgr.getCurrRoleHexName()						# ��ǰ��ɫ��
		self.__cfgPath = "account/%s/%s/%s" % ( accountName, \
			roleName, self.__cc_page_cfg_name )							# ���ñ������˺źͽ�ɫ��ص��ļ�����
		self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )		# ��ȡ�����ϵ����з�ҳ

		pyFixedPages = copy.copy( self.pyFixedPages_ )

		customIndexs = []
		for index, ( name, subSect ) in enumerate( self.__cfgSect.items() ) :
			pyPage = pyFixedPages.pop( name, None )
			if pyPage is None :											# ��������ǹ̶�ҳ��
				pyPage = self.__createPage( MSGPage, name )				# �򣬴���һ���µķ�ҳ
				customIndexs.insert( 0, index )
			pyPage.color = subSect.readVector4( "color" )				# ����ҳ����ɫ
			chsect = subSect["chids"]									# ҳ���ע��Ƶ���б�
			if chsect is not None :										# �Ƿ�������Ƶ����һ�㲻��Ϊ None����������ֶ��޸����ã�
				chids = chsect.readInts( "item" )
				if self.__family_chid in chids:
					chids = set( chids ).remove( self.__family_chid )
				if chids is not None:
					pyPage.careCHIDs = setableCHIDs.intersection( tuple( chids ) )	# ����ҳ���ע��Ƶ����ע������Ϊ set��
			docked = subSect.readBool( "docked" )						# �Ƿ���ͣ��״̬
			if not docked :												# ���ҳ�治ͣ��
				self.removePage( pyPage )								# ����ѡ���ɾ��ҳ��
				pyPage.size = subSect.readVector2( "size" )				# ����ҳ���С
				pyPage.undock( subSect.readVector2( "pos" ) )			# �򣬽⿿
			self.pyMSGPages_.append( pyPage )

		pyCurrPages = self.pyPages
		for pyPage in pyFixedPages.itervalues() :						# ������û�а������̶ֹ���ҳ��ֻ�������𻵻����״ε�½ʱ�Ż�������������
			self.pyMSGPages_.append( pyPage )
			if pyPage not in pyCurrPages :
				self.addPage( pyPage )

		overCount = len( self.pyMSGPages_ ) - self.__cc_max_pagecount
		if overCount > 0 :												# ��ҳ�������������
			for i in xrange( overCount ) :								# ��ɾ�����漸���Զ����ҳ
				pyPage = self.pyMSGPages_.pop( customIndexs[i] )
				self.destroyPage( pyPage )

		if self.pyMSGPages_[0] != self.pyUPage_ :						# �����ۺϡ�����̶�Ϊ��һҳ
			self.pyMSGPages_.remove( self.pyUPage_ )
			self.pyMSGPages_.insert( 0, self.pyUPage_ )
		self.pyUPage_.selected = True									# Ĭ��ѡ�С��ۺϷ�ҳ��
		for pyPage in self.pyMSGPages_:
			pyPage.reset()
		self.__layoutPages()

	def onLeaveWorld( self ) :
		"""
		��ɫ�뿪����ʱ������
		"""
		self.__saveConfig()												# ��������
		for pyPage in self.pyMSGPages_[:] :
			if pyPage.deletable :										# ����ǿ�ɾ����ҳ
				self.destroyPage( pyPage )
			else :
				pyPage.dock( 0 )
		self.pyMSGPages_ = []
		ResMgr.purge( self.__cfgPath )

	def onGameQuit( self ) :
		"""
		�˳���Ϸʱ������
		"""
		self.__saveConfig()												# ��������

	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		ָ������Ƿ����ڰ�͸��������
		"""
		for pyPage in self.pyPages :
			if pyPage.isMouseHit() :
				return True
		return False

	def addPage( self, pyPage ) :
		"""
		���һ��ѡ��ҳ
		"""
		TabCtrl.addPage( self, pyPage )
		self.addPyChild( pyPage )

	def removePage( self, pyPage ) :
		"""
		ɾ��һ����ҳ
		"""
		TabCtrl.removePage( self, pyPage )
		self.delPyChild( pyPage )

	def destroyPage( self, pyPage ) :
		"""
		����ָ����ҳ
		"""
		if pyPage in self.pyPages :
			self.removePage( pyPage )
		self.pyMSGPages_.remove( pyPage )
		pyPage.dispose()

	# -------------------------------------------------
	# public functions
	# -------------------------------------------------
	def upScrollHistory( self ) :
		"""
		���Ϲ�����ʷ��Ϣ
		"""
		self.__upScrollHistory()

	def downScrollHistory( self ) :
		"""
		���¹�����ʷ��Ϣ
		"""
		self.__downScrollHistory()

	def scrollMSGToEnd( self ) :
		"""
		��������Ϣ��Ͷ�
		"""
		self.__scrollMSGToEnd()

	def showChannelFilter( self ) :
		"""
		��Ƶ�����ý���
		"""
		self.__configPage( self.pySelPage )

	def showSettingMenu( self, pos ) :
		"""
		��ʾ���ò˵��������ò˵�λ��
		"""
		self.pyOPMenu_.addBinder( self.pySelPage.pyBtn )
		self.pyOPMenu_.popup()
		self.pyOPMenu_.pos = pos
