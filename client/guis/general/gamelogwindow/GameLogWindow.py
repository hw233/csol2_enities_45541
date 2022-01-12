# -*- coding: gb18030 -*-
#
# written by ganjinxing 2009-11-25

"""
implement GameLogWindow
"""
from bwdebug import *
from guis import *
from AbstractTemplates import Singleton
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.ODListPanel import ODListPanel
from ActivitySchedule import g_activitySchedule
from LabelGather import labelGather
from guis.ScreenViewer import ScreenViewer
import Const
import csdefine
import csstatus
from VehicleHelper import isFalling


class GameLogWindow( Singleton, Window ) :

	__triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/gamelogwindow/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L2
		self.addToMgr( "gameLogWindow" )

		self.__isOffline = False
		self.__initialize( wnd )

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_GameLogWindow :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __onShow( SELF ) :
		SELF.inst.show()
		printStackTrace()

	def __initialize( self, wnd ) :
		self.__pyOLInfo = CSRichText( wnd.OLFrame.infoPanel )
		self.__pyOLInfo.autoNewline = False
		self.__pyOLInfo.text = ""

		self.__pyStatLog = ODListPanel( wnd.TDSFrame.clipPanel, wnd.TDSFrame.sbar )
		self.__pyStatLog.itemHeight = 22

		self.__pyActLog = ODListPanel( wnd.TDAFrame.clipPanel, wnd.TDAFrame.sbar )
		self.__pyActLog.onViewItemInitialized.bind( self.__onInitActItem )
		self.__pyActLog.onDrawItem.bind( self.__onDrawActItem )
		self.__pyActLog.ownerDraw = True
		self.__pyActLog.itemHeight = 22

		self.__pyQuitBtn = self.__createDefBtn( wnd.exitBtn, self.__onQuitGame )
		self.__pyReloadBtn = self.__createDefBtn( wnd.reloadBtn, self.__onBackToSelect )
		self.__pyBackBtn = self.__createDefBtn( wnd.backBtn, self.__onBackToGame )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( wnd.TDAFrame.stTitle, "gamelogwindow:main", "stTDGain" )
		labelGather.setLabel( wnd.TDSFrame.stTitle, "gamelogwindow:main", "stTDStat" )
		labelGather.setLabel( wnd.OLFrame.bgTitle.stTitle, "gamelogwindow:main", "stThisGain" )
		labelGather.setLabel( wnd.lbTitle, "gamelogwindow:main", "lbTitle" )
		labelGather.setPyBgLabel( self.__pyQuitBtn, "gamelogwindow:main", "btnExit" )
		labelGather.setPyBgLabel( self.__pyReloadBtn, "gamelogwindow:main", "btnReload" )
		labelGather.setPyBgLabel( self.__pyBackBtn, "gamelogwindow:main", "btnBack" )

	def __createDefBtn( self, btnGui, handler ) :
		pyBtn = HButtonEx( btnGui )
		pyBtn.isOffsetText = True
		pyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtn.onLClick.bind( handler )
		return pyBtn

	def __onQuitGame( self ) :
		if not self.__canLogout():
			return

		BigWorld.savePreferences()
		self.__isOffline = True
		rds.gameMgr.quitGame( False )
		self.hide()

	def __onBackToSelect( self ) :
		if not self.__canLogout():
			return

		rds.gameMgr.roleLogoff()
		self.__isOffline = True
		self.hide()

	def __onBackToGame( self ) :
		self.hide()

	def __canLogout( self ):
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.ROLE_FIGHT_CANNOT_LOGOUT )
			return False

		# 如果在掉落过程中，不允许下线
		if isFalling( player ):
			player.statusMessage( csstatus.CANT_LOGOUT_WHEN_FALLING )
			return False

		return True

	def __refreshAct( self ):
		"""
		刷新活动信息
		"""
		stateColor = Const._ACT_STATECOLOR.items()
		stateColor.sort( key = lambda sc : sc[0], reverse = True )
		self.__pyActLog.clearItems()
		for state, color in stateColor :
			if state == 2:continue
			stateActs = g_activitySchedule.getActivityStateInfo( state )
			for act in stateActs :
				self.__pyActLog.addItem( ( act[2], color ) )

	def __refreshTDStat( self ) :
		"""
		刷新任务及副本信息
		"""
		self.__pyStatLog.clearItems()
		BigWorld.player().cell.getStatistic()

	def __refreshOLGain( self ) :
		"""
		刷新本次在线收获
		"""
		gain = BigWorld.player().statistic
		moneyStr = self.__formatMoneyStr( gain["statMoney"] )
		gainStr = labelGather.getText( "gamelogwindow:main", "rtThisGain" )
		gainStr %= gain["statExp"], moneyStr, gain["statPot"], gain["statTongContribute"]
		self.__pyOLInfo.text = gainStr

	def __formatMoneyStr( self, money ) :
		price = utils.currencyToViewText( money )
		return price != "" and price or "0"

	def __onInitActItem( self, pyViewItem ) :
		pyText = StaticText()
		pyViewItem.addPyChild( pyText )
		pyViewItem.pyText = pyText
		pyText.left = 0
		pyText.middle = pyViewItem.height / 2.0

	def __onDrawActItem( self, pyViewItem ) :
		text, color = pyViewItem.listItem
		pyText = pyViewItem.pyText
		pyText.text = text
		pyText.color = color

		if pyViewItem.selected :
			pyViewItem.color = self.__pyActLog.itemSelectedBackColor			# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.color = self.__pyActLog.itemHighlightBackColor			# 高亮状态下的背景色
		else :
			pyViewItem.color = self.__pyActLog.itemCommonBackColor

	@classmethod
	def __onRefreshTDStat( SELF, statInfo ) :
		"""
		接收到任务及副本信息
		@param	statInfo	: 任务及副本完成数据
		@type	statInfo	: dict
		"""
		if not SELF.insted : return
		SELF.inst.__pyStatLog.clearItems()
		tdStatContent = labelGather.getText( "gamelogwindow:main", "statContent" )
		pyStatLog = SELF.inst.__pyStatLog
		for statStr in tdStatContent :
			title, count = statStr.split( "-" )
			amount = int( statInfo.get( title, 0 ) )
			text = title + count % amount
			pyStatLog.addItem( text )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers["EVT_ON_SHOW_GAME_LOG"] = SELF.__onShow
		SELF.__triggers["EVT_ON_RECEIVE_TODAY_STATISTIC"] = SELF.__onRefreshTDStat
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[ evtMacro ]( *args )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	def hide( self ) :
		Window.hide( self )
		self.removeFromMgr()
		if not self.__isOffline :
			ECenter.fireEvent( "EVT_ON_GOT_CONTROL" )
		self.dispose()

	def show( self ) :
		self.__refreshAct()
		self.__refreshTDStat()
		self.__refreshOLGain()
		Window.show( self )

	def onLeaveWorld( self ) :
		self.hide()


GameLogWindow.registerEvents()
