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
	__cc_page_cfg_name	= "chat_pages.xml"			# 分页配置文件名称
	__cc_max_pagecount	= 8							# 最多能创建多少个分页
	__cc_tab_left		= 4							# 分页按钮的左距
	__cc_tab_space		= 4							# 每个分页按钮的间隔距离
	__family_chid		= 4							# 家族频道id

	def __init__( self, msgBg, pyBinder ) :
		TabCtrl.__init__( self, msgBg, pyBinder )
		self.rMouseSelect = True
		self.pyFixedPages_ = MapList()				# 系统分配的，不能由用户删除或改名的分页
		self.pyMSGPages_ = []						# 按顺序保存所有分页（包括上面的系统固定分页）
		self.__initFixedPages( msgBg )				# 初始化所有系统分配的分页
		self.__initOPMenu()							# 初始化右键菜单

		self.__cfgPath = ""
		self.__cfgSect = None
		self.__layoutCBID = 0						# 宽度改变时，触发按钮宽度改变（延时一会处理）

		self.__triggers = {}
		self.__registerTriggers()

		rds.shortcutMgr.setHandler( "CHAT_UP_HISTORY", self.__upScrollHistory )			# 往上滚动历史信息
		rds.shortcutMgr.setHandler( "CHAT_DOWN_HISTORY", self.__downScrollHistory )		# 往下滚动历史信息
		rds.shortcutMgr.setHandler( "CHAT_END_HISTORY", self.__scrollMSGToEnd )			# 滚动到信息最低端


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生控件事件
		"""
		TabCtrl.generateEvents_( self )
		self.__onLinkMessageLClick = self.createEvent_( "onLinkMessageLClick" )
		self.__onLinkMessageRClick = self.createEvent_( "onLinkMessageRClick" )

	@property
	def onLinkMessageLClick( self ) :
		"""
		左键点击某个超链接消息时被触发
		"""
		return self.__onLinkMessageLClick

	@property
	def onLinkMessageRClick( self ) :
		"""
		右键点击某个超链接消息时被触发
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
		排列所有分页
		"""
		pyPages = self.pyPages								# 所有停靠的页面
		totalWidth = 0										# 页面按钮总宽
		fitWidths = []										# 顺序上每页宽度
		for pyPage in pyPages :								# 找出所有停靠的页面，并且计算所有页面按钮的总宽度
			pyBtn = pyPage.pyBtn
			fitWidth = pyBtn.fitWidth
			totalWidth += fitWidth
			fitWidths.append( fitWidth )

		left = self.__cc_tab_left
		wasteSpace = self.pageCount * \
			self.__cc_tab_space + left						# 空白地方
		ratio = ( self.width - wasteSpace ) / totalWidth	# 页面按钮可用空间与页面按钮总宽比
		for idx, pyPage in enumerate( pyPages ) :
			pyBtn = pyPage.pyBtn
			pyBtn.width = fitWidths[idx] * ratio			# 按比例设置页面按钮宽度
			pyBtn.left = left
			left = pyBtn.right + self.__cc_tab_space

	def __createPage( self, CLS, name, layout = False ) :
		"""
		创建分页
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
		初始化所有固定消息板面
		"""
		pgGatherText = labelGather.getText( "ChatWindow:MSGReceiver", "tpGather" )		# 综合分页
		pgPersonalText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_PERSONAL]		# 个人分页
		pgCombatText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_COMBAT]			# 战斗分页
		pgTongText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG]				# 帮会分页
		pgTongActivityText = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG_CITY_WAR]		# 帮会战场分页
		self.pyUPage_ = self.__createPage( GatherPage, pgGatherText )
		self.pyFixedPages_[pgGatherText] = self.pyUPage_
		self.pyFixedPages_[pgPersonalText] = self.__createPage( PersonalPage, pgPersonalText )
		self.pyFixedPages_[pgCombatText] = self.__createPage( CombatPage, pgCombatText )
		self.pyFixedPages_[pgTongText] = self.__createPage( TongPage, pgTongText )
		self.pyFixedPages_[pgTongActivityText] = self.__createPage( TongBattlePage, pgTongActivityText )

	# ---------------------------------------
	def __initOPMenu( self ) :
		"""
		初始化操作菜单
		"""
		self.pyOPMenu_ = ContextMenu()
		self.pyOPMenu_.onBeforePopup.bind( self.__onMenuBeforePopup )
		self.pyOPMenu_.onAfterClose.bind( self.__onMenuAfterClosed )
		self.pyOPMenu_.onItemClick.bind( self.onOPMeuItemClick_ )

		# 与点击页面相关的操作菜单项
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

		# 分割条
		pySpliter = DefMenuItem( style = MIStyle.SPLITTER )

		# 与点击页面无关的操作
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
		弹出菜单前被触发
		"""
		pyPage = pyMenu.pyBinders[0].pyTabPage
		if pyPage.unlockable :							# 不可解锁的分页
			self.pyFreeItem_.enable = False
		else :											# 可以解锁的分页
			if not pyPage.docked :
				self.pyFreeItem_.text = labelGather.getText( "ChatWindow:pgMenu", "miDock" )
			elif pyPage.locked :						# 分页处于锁定状态
				self.pyFreeItem_.text = labelGather.getText( "ChatWindow:pgMenu", "miUnlock" )
			else :										# 分页处于解锁状态
				self.pyFreeItem_.text = labelGather.getText( "ChatWindow:pgMenu", "miLock" )
			self.pyFreeItem_.enable = True

		deletable = pyPage.deletable
		self.pyRemoveItem_.enable = deletable			# 移除分页的状态
		self.pyRenameItem_.enable = deletable			# 不能移除的分页不可重命名
		self.pyAddItem_.enable = \
			self.pageCount < self.__cc_max_pagecount	# 是否允许创建新分页
		return True

	def __onMenuAfterClosed( self, pyMenu ) :
		"""
		收起菜单时被触发
		"""
		pyMenu.clearBinders()

	# -------------------------------------------------
	def __isPageNameExist( self, name ) :
		"""
		分页名字是否已经存在
		"""
		for pyPage in self.pyMSGPages_ :
			if name == pyPage.pgName :
				return True
		return False

	# -------------------------------------------------
	def __upScrollHistory( self ) :
		"""
		往上滚动历史信息
		"""
		self.pySelPage.pyMSGPanel.upScrollHistory()
		return True

	def __downScrollHistory( self ) :
		"""
		往下滚动历史信息
		"""
		self.pySelPage.pyMSGPanel.downScrollHistory()
		return True

	def __scrollMSGToEnd( self ) :
		"""
		滚动到信息最低端
		"""
		self.pySelPage.pyMSGPanel.scrollToEnd()
		return True

	# -------------------------------------------------
	def __freePage( self, pyPage ) :
		"""
		解锁/锁定分页
		"""
		if not pyPage.docked :						# 如果分页处于分离状态
			pyPage.dock( self.pageCount )			# 将分页停靠到最后
		else :
			pyPage.locked = not pyPage.locked

	def __renamePage( self, pyPage ) :
		"""
		重命名
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
		重置分页
		"""
		pyPage.reset()

	def __setPageColor( self, pyPage ) :
		"""
		底色
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
		频道设置
		"""
		def callback( ok, checkedChannels ) :
			if ok : pyPage.careCHIDs = checkedChannels
		ChannelFilter().show( pyPage.pgName, pyPage.careCHIDs, callback, pyPage )

	def __deletePage( self, pyPage ) :
		"""
		移除分页
		"""
		if not pyPage.deletable : return
		self.removePage( pyPage )
		self.pyMSGPages_.remove( pyPage )
		pyPage.dispose()
		self.__layoutPages()

	# ---------------------------------------
	def __addPage( self, pyPage ) :
		"""
		创建新分页
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
		设置频道颜色
		"""
		def cbChanging( chid, color ) :
			"""
			某频道的颜色设置改变时被调用
			"""
			for pyPage in self.pyPages :
				pyPage.pyMSGPanel.resetMSGColor( { chid : color } )

		def cbResult( res, chcolors ) :
			"""
			频道颜色改变后被调用
			"""
			for pyPage in self.pyPages :
				pyPage.pyMSGPanel.resetMSGColor( chcolors )
			chatFacade.saveChannelConfig()
		ColorSetter().show( pyPage, cbResult, cbChanging )

	# -------------------------------------------------
	def __saveConfig( self ) :
		"""
		保存配置文件
		"""
		if self.__cfgSect is None :
			return
		for name, sect in self.__cfgSect.items() :					# 先清除所有选项
			self.__cfgSect.deleteSection( name )
		for pyPage in self.pyMSGPages_ :							# 重新写入每一页信息
			sect = self.__cfgSect.createSection( pyPage.pgName )
			sect.writeVector4( "color", pyPage.color )
			chsect = sect.createSection( "chids" )					# 关注的频道列表
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
		当我的宽度改变时被调用
		"""
		TabCtrl.onWidthChanged_( self, oldWidth )
		BigWorld.cancelCallback( self.__layoutCBID )
		self.__layoutCBID = BigWorld.callback( 0.3, self.__layoutPages )

	def onPageSelected_( self, pyPage ) :
		"""
		页面被选中时调用
		"""
		TabCtrl.onPageSelected_( self, pyPage )
		for pyTmpPage in self.pyMSGPages_ :			# 重排深度值
			pyTmpPage.posZ = 0.9					# 保证选中的分页在最前面
		pyPage.posZ = 0.1
		self.resort()

	# -------------------------------------------------
	def onLinkMessageLClick_( self, pyCom ) :
		"""
		左键点击某个超链接消息时被调用
		"""
		self.onLinkMessageLClick( pyCom )

	def onLinkMessageRClick_( self, pyCom ) :
		"""
		右键点击某个超链接消息时被调用
		"""
		self.onLinkMessageRClick( pyCom )

	# ---------------------------------------
	def onOPMeuItemClick_( self, pyMenu, pyItem ) :
		"""
		点击菜单选项时被触发
		"""
		pyPage = pyMenu.pyBinders[0].pyTabPage
		pyItem.handler( pyPage )

	def onPageTabMouseUp_( self, pyBtn ) :
		"""
		右键点击页卡时被调用
		"""
		self.pyOPMenu_.addBinder( pyBtn )
		self.pyOPMenu_.popup()

	# -------------------------------------------------
	def onPageLeft_( self, pyPage ) :
		"""
		分页脱离时被调用
		"""
		pyPage.h_dockStyle = "LEFT"				# 清除停靠
		pyPage.v_dockStyle = "TOP"
		self.removePage( pyPage )
		self.pyPages[0].selected = True
		self.__layoutPages()

	def onPageDocked_( self, pyPage, index ) :
		"""
		停靠分页时被调用
		"""
		self.addPyChild( pyPage )
		pyPage.pos = self.pyPages[0].pos
		pyPage.size = self.size
		self.insertPage( index + 1, pyPage )
		pyPage.selected = True
		pyPage.h_dockStyle = "HFILL"			# 重新设置停靠状态
		pyPage.v_dockStyle = "VFILL"
		self.__layoutPages()

	def onPageMoving_( self, pyPage ) :
		"""
		分页拖动过程中被调用
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
		分页停止拖动时被调用
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
		重设所有页面( onEenterWorld 时被调用 )
		"""
		setableCHIDs = set( chatFacade.getSetableCHIDs() )				# 所有可设置频道
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]	# 当前账号名
		roleName = rds.gameMgr.getCurrRoleHexName()						# 当前角色名
		self.__cfgPath = "account/%s/%s/%s" % ( accountName, \
			roleName, self.__cc_page_cfg_name )							# 配置保存在账号和角色相关的文件夹里
		self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )		# 获取配置上的所有分页

		pyFixedPages = copy.copy( self.pyFixedPages_ )

		customIndexs = []
		for index, ( name, subSect ) in enumerate( self.__cfgSect.items() ) :
			pyPage = pyFixedPages.pop( name, None )
			if pyPage is None :											# 如果不是是固定页面
				pyPage = self.__createPage( MSGPage, name )				# 则，创建一个新的分页
				customIndexs.insert( 0, index )
			pyPage.color = subSect.readVector4( "color" )				# 设置页面颜色
			chsect = subSect["chids"]									# 页面关注的频道列表
			if chsect is not None :										# 是否设置了频道（一般不会为 None，除非玩家手动修改配置）
				chids = chsect.readInts( "item" )
				if self.__family_chid in chids:
					chids = set( chids ).remove( self.__family_chid )
				if chids is not None:
					pyPage.careCHIDs = setableCHIDs.intersection( tuple( chids ) )	# 设置页面关注的频道（注：类型为 set）
			docked = subSect.readBool( "docked" )						# 是否处于停靠状态
			if not docked :												# 如果页面不停靠
				self.removePage( pyPage )								# 并从选项卡中删除页面
				pyPage.size = subSect.readVector2( "size" )				# 设置页面大小
				pyPage.undock( subSect.readVector2( "pos" ) )			# 则，解靠
			self.pyMSGPages_.append( pyPage )

		pyCurrPages = self.pyPages
		for pyPage in pyFixedPages.itervalues() :						# 配置中没有包含部分固定分页（只有配置损坏或者首次登陆时才会出现这种情况）
			self.pyMSGPages_.append( pyPage )
			if pyPage not in pyCurrPages :
				self.addPage( pyPage )

		overCount = len( self.pyMSGPages_ ) - self.__cc_max_pagecount
		if overCount > 0 :												# 分页超出了最大限制
			for i in xrange( overCount ) :								# 则，删除后面几个自定义分页
				pyPage = self.pyMSGPages_.pop( customIndexs[i] )
				self.destroyPage( pyPage )

		if self.pyMSGPages_[0] != self.pyUPage_ :						# 将“综合”版面固定为第一页
			self.pyMSGPages_.remove( self.pyUPage_ )
			self.pyMSGPages_.insert( 0, self.pyUPage_ )
		self.pyUPage_.selected = True									# 默认选中“综合分页”
		for pyPage in self.pyMSGPages_:
			pyPage.reset()
		self.__layoutPages()

	def onLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		self.__saveConfig()												# 保存配置
		for pyPage in self.pyMSGPages_[:] :
			if pyPage.deletable :										# 如果是可删除分页
				self.destroyPage( pyPage )
			else :
				pyPage.dock( 0 )
		self.pyMSGPages_ = []
		ResMgr.purge( self.__cfgPath )

	def onGameQuit( self ) :
		"""
		退出游戏时被调用
		"""
		self.__saveConfig()												# 保存配置

	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		指出鼠标是否落在半透明背景上
		"""
		for pyPage in self.pyPages :
			if pyPage.isMouseHit() :
				return True
		return False

	def addPage( self, pyPage ) :
		"""
		添加一组选项页
		"""
		TabCtrl.addPage( self, pyPage )
		self.addPyChild( pyPage )

	def removePage( self, pyPage ) :
		"""
		删除一个分页
		"""
		TabCtrl.removePage( self, pyPage )
		self.delPyChild( pyPage )

	def destroyPage( self, pyPage ) :
		"""
		销毁指定分页
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
		往上滚动历史信息
		"""
		self.__upScrollHistory()

	def downScrollHistory( self ) :
		"""
		往下滚动历史信息
		"""
		self.__downScrollHistory()

	def scrollMSGToEnd( self ) :
		"""
		滚动到信息最低端
		"""
		self.__scrollMSGToEnd()

	def showChannelFilter( self ) :
		"""
		打开频道设置界面
		"""
		self.__configPage( self.pySelPage )

	def showSettingMenu( self, pos ) :
		"""
		显示设置菜单，并设置菜单位置
		"""
		self.pyOPMenu_.addBinder( self.pySelPage.pyBtn )
		self.pyOPMenu_.popup()
		self.pyOPMenu_.pos = pos
