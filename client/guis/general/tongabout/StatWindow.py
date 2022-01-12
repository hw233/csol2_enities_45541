# -*- coding: gb18030 -*-
#
# $Id: StatWindow.py,fangpengjun Exp $

"""
implement StoreWindow
"""
from Time import Time
from bwdebug import *
from guis import *
import BigWorld
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.ListItem import MultiColListItem
import event.EventCenter as ECenter
import csstatus
import csdefine


class StatWindow( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/familychallenge/statwindow.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__registerTriggers()
		self.__ourPlayers = {} #己方队伍
		self.__enemyPlayers = {} #敌方队伍
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyTabCtrl = TabCtrl( wnd.tc )
		index = 0
		while True :											#初始化TabCtrl
			tabName = "btn_" + str( index )
			tab = getattr( wnd.tc, tabName, None )
			if tab is None : break
			panelName = "panel_" + str( index )
			panel = getattr( wnd.tc, panelName, None )
			if panel is None : break
			pyBtn = TabButton( tab )
			pyBtn.isOffsetText = True
			labelGather.setPyBgLabel( pyBtn, "TongAba:StatWindow", tabName )
			pyBtn.setStatesMapping( UIState.MODE_R3C1 )
			pyPanel = ReportPanel( panel )
			pyPage = TabPage( pyBtn, pyPanel )
			self.__pyTabCtrl.addPage( pyPage )
			index += 1

		self.__pyBtnLeaveWar = Button( wnd.btnLeave )
		self.__pyBtnLeaveWar.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnLeaveWar.onLClick.bind( self.__onLeaveWar )
		labelGather.setPyLabel( self.pyLbTitle_, "TongAba:StatWindow", "lbTitle" )
		labelGather.setPyBgLabel( self.__pyBtnLeaveWar, "TongAba:StatWindow", "btnLeave" )
	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_STAT_WINDOW"] = self.__toggleStatWindow
		self.__triggers["EVT_ON_TOGGLE_TONGWAR_REPORT_CHANGE"] = self.__onUpdateWarReport
		self.__triggers["EVT_ON_TOGGLE_TONG_LEAVE_WAR"] = self.__onRoleLeaveWar
		self.__triggers["EVT_ON_TOGGLE_SHOW_ABA_RESULT"] = self.__onWndShow

		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
	# ----------------------------------------------------------------------
	def __toggleStatWindow( self ):
		self.visible = not self.visible

	def __onUpdateWarReport( self, playerID, playerName, playerTongDBID, killCount, dieCount ):
		pyColligatePanel = self.__pyTabCtrl.pyPages[0].pyPanel
		pyOurInterPanel = self.__pyTabCtrl.pyPages[1].pyPanel
		pyEnemyInterPanel = self.__pyTabCtrl.pyPages[2].pyPanel
		player = BigWorld.player()
		if playerName in self.__ourPlayers or playerName in self.__enemyPlayers: #在
			pyColligatePanel.updateReport( playerID, playerName, playerTongDBID, killCount, dieCount )
		else :
			pyColligatePanel.addReport( playerID, playerName, playerTongDBID, killCount, dieCount)
		if player.tong_dbID == playerTongDBID: #己方队员
			if self.__ourPlayers.has_key( playerName ):
				pyOurInterPanel.updateReport( playerID, playerName, playerTongDBID, killCount, dieCount ) #己方报表更新已有队员数据
			else:
				pyOurInterPanel.addReport( playerID, playerName, playerTongDBID, killCount, dieCount ) #己方报表添加新队员数据
			self.__ourPlayers[playerName] = ( playerID, playerName, playerTongDBID, killCount, dieCount )
		else: #敌方队员
			if self.__enemyPlayers.has_key( playerName ):
				pyEnemyInterPanel.updateReport( playerID, playerName, playerTongDBID, killCount, dieCount )
			else:
				pyEnemyInterPanel.addReport( playerID, playerName, playerTongDBID, killCount, dieCount )
			self.__enemyPlayers[playerName] = ( playerID, playerName, playerTongDBID, killCount, dieCount )

	def __onRoleLeaveWar( self ):
		self.__ourPlayers = {}
		self.__enemyPlayers = {}
		self.__clearItems()
		self.hide()

	def __onLeaveWar( self ): #离开战场
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().tong_leaveWarSpace()
		# "是否确定离开战斗？"
		showMessage( 0x0381, "", MB_OK_CANCEL, query )
		return True
	
	def __onWndShow( self ):
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示
		rds.uiHandlerMgr.setShieldUI( self )
		self.show()

	def __clearItems( self ):
		self.__pyTabCtrl.pyPages[0].pyPanel.clearItems()
		self.__pyTabCtrl.pyPages[1].pyPanel.clearItems()
		self.__pyTabCtrl.pyPages[2].pyPanel.clearItems()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		Window.show( self )

	def hide( self ):
		Window.hide( self )

	def onLeaveWorld( self ):
		self.__onRoleLeaveWar()

# -----------------------------------------------------------------
# 统计面板
# -----------------------------------------------------------------
from guis.controls.TabCtrl import TabPanel
from guis.controls.ListPanel import ListPanel
from guis.controls.ButtonEx import HButtonEx
class ReportPanel( TabPanel ): #列表
	def __init__( self, tabPanel ):
		TabPanel.__init__( self, tabPanel )
		self.sortByName = False
		self.sortByKillNum = False
		self.sortByDeathNum = False
		self.__pyListPanel = ListPanel( tabPanel.listPanel, tabPanel.listBar )

		self.__pyNameBtn = HButtonEx( tabPanel.btn_0 )
		self.__pyNameBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNameBtn.onLClick.bind( self.__onSortByName )
		labelGather.setPyBgLabel( self.__pyNameBtn, "TongAba:StatWindow", "taxisBtn_0" )

		self.__pyKillNumBtn = HButtonEx( tabPanel.btn_1 )
		self.__pyKillNumBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyKillNumBtn.onLClick.bind( self.__onSortByKillNum )
		labelGather.setPyBgLabel( self.__pyKillNumBtn, "TongAba:StatWindow", "taxisBtn_1" )

		self.__pyDeathNumBtn = HButtonEx( tabPanel.btn_2 )
		self.__pyDeathNumBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyDeathNumBtn.onLClick.bind( self.__onSortByDeathNum )
		labelGather.setPyBgLabel( self.__pyDeathNumBtn, "TongAba:StatWindow", "taxisBtn_2" )

	def __onSortByName( self ):
		flag = self.sortByName and True or False
		self.__pyListPanel.sort( key = lambda pyItem: pyItem.playerName, reverse = flag )
		self.sortByName = not self.sortByName

	def __onSortByKillNum( self ):
		flag = self.sortByKillNum and True or False
		self.__pyListPanel.sort( key = lambda pyItem: pyItem.killCount, reverse = flag )
		self.sortByKillNum = not self.sortByKillNum

	def __onSortByDeathNum( self ):
		flag = self.sortByDeathNum and True or False
		self.__pyListPanel.sort( key = lambda pyItem: pyItem.dieCount, reverse = flag )
		self.sortByDeathNum = not self.sortByDeathNum

	def addReport( self, playerID, playerName, playerTongDBID, killCount, dieCount ):
		playerNames = [pyItem.playerName for pyItem in self.__pyListPanel.pyItems]
		if playerName in playerNames:return
		pyReportItem = ReportItem()
		self.__pyListPanel.addItem( pyReportItem )
		pyReportItem.addReport( playerID, playerName, playerTongDBID, killCount, dieCount )

	def updateReport( self, playerID, playerName, playerTongDBID, killCount, dieCount ):
		for pyReport in self.__pyListPanel.pyItems:
			if pyReport.playerName == playerName:
				pyReport.updateReport( playerName, playerTongDBID, killCount, dieCount )

	def clearItems( self ):
		self.__pyListPanel.clearItems()

# -----------------------------------------------------------
# 统计字段
# -----------------------------------------------------------
class ReportItem( MultiColListItem ):
	def __init__( self ):
		item = GUI.load( "guis/general/familychallenge/reportitem.gui" )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.playerName = ""

	def addReport( self, playerID, playerName, playerTongDBID, killCount, dieCount ):
		player = BigWorld.player()
		self.playerID = playerID
		if playerTongDBID == player.tong_dbID: #己方
			self.commonForeColor = 0,255,255,255
		else: #对方
			self.commonForeColor = 255,0,0,255
		self.playerName = playerName
		self.killCount = killCount
		self.dieCount = dieCount
		self.setTextes( playerName, str( killCount ), str( dieCount ) )

	def updateReport( self, playerName, playerTongDBID, killCount, dieCount ):
		self.playerName = playerName
		self.killCount = killCount
		self.dieCount = dieCount
		self.setTextes( playerName, str( killCount ), str( dieCount ) )

# -----------------------------------------------------------------
# 复活确认框
# -----------------------------------------------------------------
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.StaticText import StaticText
from guis.controls.SelectableButton import SelectableButton
from Time import Time
import Timer
RELIVE_REMAIN_TIME = 10  #复活剩余初始时间

class ReliveMsgBox( Window ):

	def __init__( self ):
		box = GUI.load( "guis/general/familychallenge/relivemsg.gui" )
		uiFixer.firstLoadFix( box )
		Window.__init__( self, box )
		self.__initialize( box )
		self.posZSegment = ZSegs.L2
		self.escHide_ = False
		self.triggers_ = {}
		self.registerTriggers_()
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.__pyOwner = None
		self.reliveTimerID = 0
#		self.addToMgr( "reliveMsgBox" )

	def dispose( self ) :
		"""
		release resource
		"""
		del self.__pyOwner
		Window.dispose( self )

	def __initialize( self, box ):
		if box is None:return
		self.pyReliveGroup_ = SelectorGroup()
		self.__pyStMsg = StaticText( box.stMsg )
		labelGather.setPyLabel( self.__pyStMsg, "TongAba:ReliveMsgBox", "stMsg" )
		
		self.__pyAffirmBtn = HButtonEx( box.btnRelive )
		self.__pyAffirmBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyAffirmBtn.onLClick.bind( self.onAffirmRelive_ )
		labelGather.setPyBgLabel( self.__pyAffirmBtn, "TongAba:ReliveMsgBox", "btnRelive" )

		self.pyCloseBtn_.onLClick.bind( self.onHide_ )

		self.pyStTimer_ = StaticText( box.stTimer )
		self.pyStTimer_.text = ""

		self.__initReliveBtns( box )

	def __initReliveBtns( self, box ):
		for name, item in box.children:
			if "relive_" not in name:continue
			index = int( name.split( "_" )[1] )
			pyReliveBtn = SelectableButton( item )
			pyReliveBtn.setStatesMapping( UIState.MODE_R4C1 )
			pyReliveBtn.autoSelect = True
			labelGather.setPyBgLabel( pyReliveBtn, "TongAba:ReliveMsgBox", name )
			pyReliveBtn.index = index
			self.pyReliveGroup_.addSelector( pyReliveBtn )

	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_TOGGLE_FAMILY_RELIVE_BOX"] = self.__toggleReliveBox #触发复活框
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.triggers_.iterkeys():
			ECenter.unregisterEvent( key, self )

	# ---------------------------------------------------------------
	def __toggleReliveBox( self ): #弹出确认窗口
		self.show()
		self.reliveTimerID = Timer.addTimer( 0, 1, self.__reliveTimeUpdate )
		self.endTime = Time.time() + RELIVE_REMAIN_TIME
		self.pyReliveGroup_.pyCurrSelector = self.pyReliveGroup_.pySelectors[0]
		defReliveBtn = self.pyReliveGroup_.pyCurrSelector

	def __reliveTimeUpdate( self ): #复活读秒
		if not self.visible:
			self.cancelReliveTimer_()
			return
		remainTime = self.endTime - Time.time()
		self.pyStTimer_.text = labelGather.getText( "TongAba:ReliveMsgBox", "stTimer" )%remainTime
		if remainTime <= 0:
			index = self.pyReliveGroup_.pyCurrSelector.index
			BigWorld.player().tong_onInTongWarRelivePoint( index )
			self.cancelReliveTimer_()
			self.hide()

	def onHide_( self ):
		"""
		点关闭按钮触发
		"""
		index = self.pyReliveGroup_.pyCurrSelector.index
		BigWorld.player().tong_onInTongWarRelivePoint( index )
		self.cancelReliveTimer_()
		self.hide()

	def cancelReliveTimer_( self ): #清除计时器
		Timer.cancel( self.reliveTimerID )
		self.reliveTimerID = 0

	def onAffirmRelive_( self ): #确认复活
		pySelBtn = self.pyReliveGroup_.pyCurrSelector
		index = pySelBtn.index
		BigWorld.player().tong_onInTongWarRelivePoint( index )
		self.cancelReliveTimer_()
		self.hide()

	# ------------------------------------------------------------------
	# public
	# ----------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.triggers_[macroName]( *args )

	def show( self ):
		Window.show( self )

	def hide( self ):
		Window.hide( self )

class ReliveMsgBoxAba( ReliveMsgBox ):
	"""
	家族擂台，复活
	"""

	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_TOGGLE_TONG_ABA_RELIVE_BOX"] = self.__toggleAbaReliveBox	# 家族擂台复活框
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )

	def __toggleAbaReliveBox( self ): #弹出确认窗口
		self.show()
		self.reliveTimerID = Timer.addTimer( 0, 1, self.__abaReliveTimeUpdate )
		self.endTime = Time.time() + RELIVE_REMAIN_TIME
		self.pyReliveGroup_.pyCurrSelector = self.pyReliveGroup_.pySelectors[0]
		defReliveBtn = self.pyReliveGroup_.pyCurrSelector

	def __abaReliveTimeUpdate( self ): #复活读秒
		if not self.visible:
			self.cancelReliveTimer_()
			return
		remainTime = self.endTime - Time.time()
		self.pyStTimer_.text = labelGather.getText( "TongAba:ReliveMsgBox", "stTimer" )%remainTime
		if remainTime <= 0:
			index = self.pyReliveGroup_.pyCurrSelector.index
			BigWorld.player().tong_onInTongAbaRelivePoint( index )
			self.cancelReliveTimer_()
			self.hide()

	def onAffirmRelive_( self ): #确认复活
		pySelBtn = self.pyReliveGroup_.pyCurrSelector
		index = pySelBtn.index
		BigWorld.player().tong_onInTongAbaRelivePoint( index )
		self.cancelReliveTimer_()
		self.hide()

	def onHide_( self ):
		index = self.pyReliveGroup_.pyCurrSelector.index
		BigWorld.player().tong_onInTongAbaRelivePoint( index )
		self.cancelReliveTimer_()
		self.hide()

	# ----------------------------------------------------

class ReviveTeamCompeteBox( Window ):
	"""
	"""
	def __init__( self ):
		box = GUI.load( "guis/general/revivewindow/reviveteamcompetewnd.gui" )
		uiFixer.firstLoadFix( box )
		Window.__init__( self, box )
		self.__initialize( box )
		self.posZSegment = ZSegs.L2
		self.escHide_ = False
		self.__triggers = {}
		self.__registerTriggers()
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.__pyOwner = None
		self.reliveTimerID = 0
#		self.addToMgr( "reliveMsgBox" )

	def dispose( self ) :
		"""
		release resource
		"""
		del self.__pyOwner
		Window.dispose( self )

	def __initialize( self, box ):
		if box is None:return
		self.__pyReviveOriginBtn = Button( box.reviveOriginBtn )
		self.__pyReviveOriginBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyReviveOriginBtn.onLClick.bind( self.__onReviveOnOrigin )

		self.__pyReviveTombBtn = Button( box.reviveTombBtn )
		self.__pyReviveTombBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyReviveTombBtn.onLClick.bind( self.__onReviveOnTomb )

		self.__pyStTimer = StaticText( box.stTimer )
		self.__pyStTimer.text = ""
		
		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyReviveOriginBtn, "TongAba:ReviveTeamCompeteBox", "originBtn" )
		labelGather.setPyBgLabel( self.__pyReviveTombBtn, "TongAba:ReviveTeamCompeteBox", "tombBtn" )

	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_TEAM_COMPETE_REVIVE_BOX"] = self.__toggleReliveBox #触发复活框
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# ---------------------------------------------------------------
	def __toggleReliveBox( self ):
		"""
		弹出确认窗口
		"""
		self.show()
		self.reliveTimerID = Timer.addTimer( 0, 1, self.__reliveTimeUpdate )
		self.endTime = Time.time() + 30

	def __reliveTimeUpdate( self ):
		"""
		复活读秒
		"""
		if not self.visible:
			self.__cancelReliveTimer()
			return
		remainTime = self.endTime - Time.time()
		self.__pyStTimer.text = labelGather.getText( "TongAba:ReviveTeamCompeteBox", "stRemainTime", remainTime )
		if remainTime <= 0:
			self.__onReviveOnTomb()
			self.__cancelReliveTimer()
			self.hide()

	def __cancelReliveTimer( self ):
		"""
		清除计时器
		"""
		Timer.cancel( self.reliveTimerID )
		self.reliveTimerID = 0

	def __onReviveOnOrigin( self ):
		"""
		原地复活
		"""
		player = BigWorld.player()
		if not self.__canReviveAtCurrPoint() :
			player.statusMessage( csstatus.ROLE_CONDITION_OF_REVIVE_ORIGINAL )
			return
		player.cell.useItemRevive()
		player.onStateChanged( csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_FREE )
		self.hide()

	def __onReviveOnTomb( self ):
		"""
		复活点复活
		"""
		player = BigWorld.player()
		player.cell.revive( csdefine.REVIVE_ON_SPACECOPY )
		self.hide()

	def __canReviveAtCurrPoint( self ) :
		"""
		查找玩家身上的归命符，判断是否能原地复活
		"""
		player = BigWorld.player()
		if player.checkItemFromNKCK_( 110103001, 1 ) :
			return True
		return False

	# ----------------------------------------------------
	# public
	# ----------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		Window.show( self )

	def hide( self ):
		Window.hide( self )



# ----------------------------------------------------------------------
# 剩余时间、积分榜显示
# ----------------------------------------------------------------------
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from Function import Functor

class TipsPanel( RootGUI ):
	def __init__( self ):
		panel = GUI.load( "guis/general/familychallenge/tipspanel.gui" )
		uiFixer.firstLoadFix( panel )
		RootGUI.__init__( self, panel )
		self.v_dockStyle = "BOTTOM"
		self.h_dockStyle = "RIGHT"
		self.posZSegment = ZSegs.L4
		self.focus = False
		self.activable_ = False
		self.escHide_ 		 = False
		self.moveFocus		 = False
		self.hitable_ = False					# 如果为 False，鼠标点击在窗口上时，仍然判断鼠标点击的是屏幕
		self.__triggers = {}
		self.__registerTriggers()
		self.remainTimerID = 0
		self.endTime = 0.0
		self.__initPanel( panel )
		
		self.preEnemyMarkStr = "----"		# 上一次积分
		self.preSelfMarkStr = "----"		# 上一次积分
		self.selfTongName = ""
		self.enemyTongName = ""

	def __initPanel( self, panel ):
		self.__pyStRemTime = StaticText( panel.stRemainTime )
		self.__pyStRemTime.text = ""

		self.__pyRTMark = CSRichText( panel.rtMark )
		self.__pyRTMark.text = ""

		self.__pyBuyRecord = StaticText( panel.stBuyRecord )
		self.__pyBuyRecord.text = ""

	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers["EVT_ON_ROLE_ENTER_NPC_CHALLENGE"] = self.__onRoleChallenge	#玩家进入挑战
#		self.__triggers["EVT_ON_TOGGLE_FAMILYWAR_TIME_CHANGE"] = self.__onTimeChange #剩余时间更新
		self.__triggers["EVT_ON_TOGGLE_TONGWAR_MARK_CHANGE"] = self.__onWarMarkChange #战场积分更新
		self.__triggers["EVT_ON_TOGGLE_TONGABA_MARK_CHANGE"] = self.__onAbaMarkChange #家族擂台积分更新
		self.__triggers["EVT_ON_TOGGLE_TONG_LEAVE_WAR"] = self.__onRoleLeaveWar #离开战场更新
		self.__triggers["EVT_ON_TOGGLE_BUY_RECORD_CHANGE"] = self.__onRoleBuyRecordChange #购买积分更新
		self.__triggers["EVT_ON_ROLE_CORPS_NAME_CHANGED"] = self.__onTongNameChange
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )

	# -----------------------------------------------------------------
	def __onRoleChallenge( self, endTime ):
		self.visible = endTime > 0.0
#		self.endTime = endTime
		self.remainTimerID = Timer.addTimer( 0, 1, Functor( self.__remainTimeUpdate, endTime ) )

	def __remainTimeUpdate( self, endTime ):
		if not self.visible:
			self.__cancelRemianTimer()
			return
		remainTime = endTime - Time.time()
		self.__pyStRemTime.text = labelGather.getText( "TongAba:TipsPanel", "stRemainTime")%( remainTime/60, remainTime%60 )
		if remainTime <= 0.0:
			self.__pyStRemTime.text = ""
			self.__pyRTMark.text = ""
			self.__pyBuyRecord.text = ""
			self.__cancelRemianTimer()

	def __cancelRemianTimer( self ):
		Timer.cancel( self.remainTimerID )
#		self.endTime = 0.0
		self.remainTimerID = 0

	def __onWarMarkChange( self, enemyTongName, enemyTongMark, selfTongMark ):
		player = BigWorld.player()
		enemyMarkStr = ""
		selfMarkStr = ""
		if enemyTongMark < 0:
			enemyMarkStr = "--"
		else:
			enemyMarkStr = str( enemyTongMark )
		self.preEnemyMarkStr = enemyMarkStr

		if selfTongMark < 0:
			selfMarkStr = "--"
		else:
			selfMarkStr = str( selfTongMark )
		self.preSelfMarkStr = selfMarkStr

		selfTips = PL_Font.getSource( labelGather.getText( "TongAba:TipsPanel", "stSelfTips", selfMarkStr ), fc = ( 0, 255, 255, 255 ) )
		enemyTips = PL_Font.getSource( labelGather.getText( "TongAba:TipsPanel", "stEnemyTips", PL_NewLine.getSource(), enemyMarkStr ), fc = ( 255, 0, 0, 255 ) )
		self.__pyRTMark.text = selfTips + enemyTips

	def __onAbaMarkChange( self, enemyTongName, enemyTongMark, selfTongMark, isSelfMark ):
		player = BigWorld.player()
		if isSelfMark: #积分数据比帮会名称先到客户端，此时player.tongName 为 "",因此有__onTongNameChange通知
			self.selfTongName = enemyTongName
		else:
			self.enemyTongName = enemyTongName
		enemyMarkStr = ""
		selfMarkStr = ""
		if enemyTongMark < 0:
			enemyMarkStr = "--"
		elif enemyTongMark == 0:	# 如果是0，则不更新
			enemyMarkStr = self.preEnemyMarkStr
		else:
			enemyMarkStr = str( enemyTongMark )
		self.preEnemyMarkStr = enemyMarkStr

		if selfTongMark < 0:
			selfMarkStr = "--"
		elif selfTongMark == 0:
			selfMarkStr = self.preSelfMarkStr
		else:
			selfMarkStr = str( selfTongMark )
		self.preSelfMarkStr = selfMarkStr
		selfTips = PL_Font.getSource( labelGather.getText( "TongAba:TipsPanel", "stSelfTips")%( self.selfTongName, selfMarkStr ),\
		fc = ( 0, 255, 255, 255 ) )
		enemyTips = PL_Font.getSource( labelGather.getText( "TongAba:TipsPanel", "stEnemyTips")%( PL_NewLine.getSource(), \
		self.enemyTongName,enemyMarkStr ), fc = ( 255, 0, 0, 255 ) )
		self.__pyRTMark.text = selfTips + enemyTips

	def __onRoleLeaveWar( self ):
		self.__cancelRemianTimer()
		self.visible = False
		self.__pyStRemTime.text = ""
		self.__pyRTMark.text = ""
		self.__pyBuyRecord.text = ""
		self.preEnemyMarkStr = "----"		# 上一次积分
		self.preSelfMarkStr = "----"		# 上一次积分
		
	def __onRoleBuyRecordChange( self, buyRecord ):
		self.__pyBuyRecord.text = labelGather.getText( "TongAba:TipsPanel", "stBuyRecord") % buyRecord
	
	def __onTongNameChange( self, role, oldName, tongName ):
		if role is not BigWorld.player():return
		self.selfTongName = tongName
		selfTips = PL_Font.getSource( labelGather.getText( "TongAba:TipsPanel", "stSelfTips")%( self.selfTongName, self.preSelfMarkStr ),\
		fc = ( 0, 255, 255, 255 ) )
		enemyTips = PL_Font.getSource( labelGather.getText( "TongAba:TipsPanel", "stEnemyTips")%( PL_NewLine.getSource(), \
		self.enemyTongName,self.preEnemyMarkStr ), fc = ( 255, 0, 0, 255 ) )
		self.__pyRTMark.text = selfTips + enemyTips

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		系统状态改变通知
		"""
		if newStatus == Define.GST_IN_WORLD :
			currSpaceLabel = BigWorld.player().getSpaceLabel()
			self.visible = currSpaceLabel in [ "fu_ben_npc_zheng_duo_zhan", "tong_abattoir" ]
		else :
			self.visible = False

	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()
