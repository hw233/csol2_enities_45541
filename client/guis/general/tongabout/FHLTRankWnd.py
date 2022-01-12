# -*- coding: gb18030 -*-
#
# $Id: WarIntergral.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from  guis.controls.Button import Button
from  guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabButton
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ODListPanel import ViewItem
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticLabel import StaticLabel
from guis.tooluis.fulltext.FullText import FullText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.controls.ItemsPanel import ItemsPanel
import Font
from Time import Time

class FHLTRankWnd( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongfhlt/rnkwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__registerTriggers()
		self.__cdcbid = 0
		self.__delaycbid = 0
		self.__endTime = 0.0
		self.__enemyInter = 0
		self.__ownInter = 0
		self.__ranks = {}					#排序数据
		self.__tongNames = {}				#帮会名称
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
			pyBtn.index = index
			pyBtn.isOffsetText = True
			pyBtn.commonMapping = util.getStateMapping( pyBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
			pyBtn.selectedMapping = util.getStateMapping( pyBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
			pyBtn.selectedForeColor = ( 142, 216, 217, 255 )
			labelGather.setPyBgLabel( pyBtn, "TongAbout:FHLTRankWnd", tabName )
			pyPanel = RankPanel( panel )
			pyPage = TabPage( pyBtn, pyPanel )
			self.__pyTabCtrl.addPage( pyPage )
			index += 1
		
		self.__pyRtLeftName = CSRichText( wnd.rstPanel.rtLeftName )	#自己帮会
		self.__pyRtLeftName.aglin = "C"
		self.__pyRtLeftName.text = ""
		
		self.__pyRtRightName = CSRichText( wnd.rstPanel.rtRightName )	#对方帮会
		self.__pyRtRightName.aglin = "C"
		self.__pyRtRightName.text = ""

		self.__pyRtLeftInter = CSRichText( wnd.rstPanel.rtLeftInter )		#自己帮会积分
		self.__pyRtLeftInter.aglin = "C"
		self.__pyRtLeftInter.text = ""
		
		self.__pyRtRightInter = CSRichText( wnd.rstPanel.rtRightInter )		#对方帮会积分
		self.__pyRtRightInter.aglin = "C"
		self.__pyRtRightInter.text = ""
		
		self.__pyRstPanel = PyGUI( wnd.rstPanel )
		
		self.__pyLbLeft = StaticLabel( wnd.rstPanel.lbLeft )				#自己帮会胜负状态
		self.__pyLbLeft.text = ""
		self.__pyLbLeft.autoSize = True
		self.__pyLbLeft.limning = Font.LIMN_NONE
		self.__pyLbLeft.visible = False
		
		self.__pyLbRight = StaticLabel( wnd.rstPanel.lbRight )				#对方帮会胜负状态
		self.__pyLbRight.text = ""
		self.__pyLbRight.autoSize = True
		self.__pyLbRight.limning = Font.LIMN_NONE
		self.__pyLbRight.visible = False
		
		self.__pyLbInter = StaticLabel( wnd.rstPanel.lbInter )				#积分高亮
		self.__pyLbInter.text = labelGather.getText( "TongAbout:FHLTRankWnd", "intergal" )
		self.__pyLbInter.foreColor = ( 0, 0, 0, 255 )
		self.__pyLbInter.backColor = ( 204, 155, 0, 255 )
		self.__pyLbInter.autoSize = True
		self.__pyLbInter.limning = Font.LIMN_NONE
		self.__pyLbInter.visible = False
		
		self.__pyRtRival = CSRichText( wnd.infoPanel.rtRival )				#对手名称
		self.__pyRtRival.align = "L"
		self.__pyRtRival.text = ""
		
		self.__pyRtInteral = CSRichText( wnd.infoPanel.rtInteral )			#即时积分
		self.__pyRtInteral.align = "R"
		self.__pyRtInteral.text = ""
		self.__pyRtInteral.autoNewline = False
		
		self.__pyRtTime = CSRichText( wnd.infoPanel.rtTime )				#剩余时间
		self.__pyRtTime.align = "R"
		self.__pyRtTime.text = ""
		
		labelGather.setLabel( wnd.lbTitle, "TongAbout:FHLTRankWnd", "lbTitle" )
		labelGather.setLabel( wnd.rstPanel.title.stTitle, "TongAbout:FHLTRankWnd", "result" )
	
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_FHLTRANK_WND"] = self.__onShowWnd
		self.__triggers["EVT_ON_ENTER_FHLT_SPACE"] = self.__onEnterSpace
		self.__triggers["EVT_ON_RECIEVE_FHLTRANK_DATAS"] = self.__onRecieveDatas
		self.__triggers["EVT_ON_UPDATE_FHLT_POINT"] = self.__onUpdatePoint
		self.__triggers["EVT_ON_FHLT_SPACE_OVER"] = self.__onSpaceOver
#		self.__triggers["EVT_ON_LEAVE_FHLT_SPACE"] = self.__onLeaveSpace
		for macroName in self.__triggers.iterkeys():
			ECenter.registerEvent( macroName, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for macroName in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( macroName, self )
	# -------------------------------------------------------
	def __onShowWnd( self ):
		"""
		窗口显示
		"""
		self.visible = not self.visible
	
	def __onEnterSpace( self, endTime, tongInfos ):
		"""
		进入副本回调
		"""
		player = BigWorld.player()
		pTongDBID = player.tong_dbID
		ltName = tongInfos[ "leftTongName" ]
		rtName = tongInfos[ "rightTongName" ]
		ltDBID = tongInfos[ "left" ]
		rtDBID = tongInfos[ "right" ]
		rvalName = ""
		if pTongDBID != ltDBID:
			rvalName = ltName
		if pTongDBID != rtDBID:
			rvalName = rtName
		self.__pyRtRival.text = labelGather.getText( "TongAbout:FHLTRankWnd", "rvalName" )%rvalName
		self.__tongNames[ltDBID] = ltName
		self.__tongNames[rtDBID] = rtName
		self.__endTime = endTime
		self.__cancelCountdown()
		self.__cdcbid = BigWorld.callback( 0, self.__remainCountdown )
	
	def __remainCountdown( self ):
		"""
		剩余时间倒计时
		"""
		remainTime = self.__endTime - Time.time()
		if remainTime > 0:
			min = int( remainTime )/60
			sec = int( remainTime )%60
			timeText = "%02d:%02d"%( min, sec )
			timeText = PL_Font.getSource( timeText , fc = ( 230, 227, 185, 255 ) )
			timeText = labelGather.getText( "TongAbout:FHLTRankWnd", "remainTime" ) % timeText
			self.__pyRtTime.text = PL_Font.getSource( timeText, fc = ( 84, 194, 23, 255 ) )
			self.__cdcbid = BigWorld.callback( 1.0, self.__remainCountdown )
		else:
			self.__cancelCountdown()
	
	def __onRecieveDatas( self, tongDBID, playerName, kill, dead, isInWar ):
		"""
		接收积分数据
		"""
		player = BigWorld.player()
		pyAllPanel = self.__pyTabCtrl.pyPages[0].pyPanel
		pyOwnPanel = self.__pyTabCtrl.pyPages[1].pyPanel
		pyEnemyPanel = self.__pyTabCtrl.pyPages[2].pyPanel
		pTongDBID = player.tong_dbID
		area = labelGather.getText( "TongAbout:WarIntergral", "out" )
		if isInWar:
			area = labelGather.getText( "TongAbout:WarIntergral", "inArea" )
			if tongDBID in self.__ranks:
				ranks = self.__ranks[tongDBID]
				if playerName in [info.playerName for info in ranks]:
					for rankInfo in ranks:
						if rankInfo.playerName == playerName:
							rankInfo.updateInfo( kill, dead, area )
					if tongDBID == pTongDBID:
						pyOwnPanel.updateRank( tongDBID, playerName, kill, dead, area )
					else:
						pyEnemyPanel.updateRank( tongDBID, playerName, kill, dead, area )
				else:
					rankInfo = RankInfo( tongDBID, playerName, kill, dead, area )
					self.__ranks[tongDBID].append( rankInfo )
					if tongDBID == pTongDBID:
						pyOwnPanel.initRank( rankInfo )
					else:
						pyEnemyPanel.initRank( rankInfo )
			else:
				rankInfo = RankInfo( tongDBID, playerName, kill, dead, area )
				self.__ranks[tongDBID] = [rankInfo]
				if tongDBID == pTongDBID:
					pyOwnPanel.initRank( rankInfo )
				else:
					pyEnemyPanel.initRank( rankInfo )
			if self.__isInAllRanks( tongDBID, playerName ):										#全部
				pyAllPanel.updateRank( tongDBID, playerName, kill, dead, area )
			else:
				rankInfo = RankInfo( tongDBID, playerName, kill, dead, area )
				pyAllPanel.initRank( rankInfo )
		else:																				# 离开副本
			if tongDBID in self.__ranks:
				ranks = self.__ranks[tongDBID]
				for rank in ranks:
					if rank.playerName == playerName:
						ranks.remove( rank )
				if tongDBID == pTongDBID:
					pyOwnPanel.delRank( playerName )
				else:
					pyEnemyPanel.delRank( playerName )
				pyAllPanel.delRank( playerName )
	
	def __onUpdatePoint( self, tongDBID, point ):
		"""
		更新即时积分
		"""
		player = BigWorld.player()
		interText = ""
		if tongDBID == player.tong_dbID:
			self.__ownInter = point
			interText = "%02d:%02d"%( point, self.__enemyInter )
		else:
			self.__enemyInter = point
			interText = "%02d:%02d"%( self.__ownInter, point )
		self.__pyRtInteral.text = labelGather.getText( "TongAbout:FHLTRankWnd", "immInter" )%interText
	
	def __onSpaceOver( self ):
		"""
		副本结束回调
		"""
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示
		self.__pyLbLeft.visible = True
		self.__pyLbRight.visible = True
		self.__pyLbInter.visible = True
		winText = labelGather.getText( "TongAbout:FHLTRankWnd", "winer" )
		loseText = labelGather.getText( "TongAbout:FHLTRankWnd", "loser" )
		player = BigWorld.player()
		self.__pyRtLeftName.text = self.__tongNames.get( player.tong_dbID, "" )
		self.__pyRtRightName.text = self.__getEnemyName()
		if self.__ownInter > self.__enemyInter:					#己方胜利
			self.__pyLbLeft.text = winText
			self.__pyLbLeft.foreColor = ( 0, 0, 0, 255 )
			self.__pyLbLeft.backColor = ( 255, 0, 0, 255 )
			self.__pyLbRight.text = loseText
			self.__pyLbRight.foreColor = ( 255, 0, 0, 255 )
			self.__pyLbRight.backColor = ( 204, 153, 255, 255 )
		else:
			self.__pyLbLeft.text = loseText
			self.__pyLbLeft.foreColor = ( 255, 0, 0, 255 )
			self.__pyLbLeft.backColor = ( 204, 153, 255, 255 )
			self.__pyLbRight.text = winText
			self.__pyLbRight.foreColor = ( 0, 0, 0, 255 ) 
			self.__pyLbRight.backColor = ( 255, 0, 0, 255 )
		self.__pyLbRight.right = self.__pyRstPanel.width - 5.0
		self.__pyRtLeftInter.text = "%02d"%self.__ownInter
		self.__pyRtRightInter.text = "%02d"%self.__enemyInter
		self.__delaycbid = BigWorld.callback( 60.0, self.__delayHide )
		self.show()
	
	def __delayHide( self ):
		"""
		离开副本
		"""
		self.__pyLbLeft.visible = False
		self.__pyLbRight.visible = False
		self.__pyLbInter.visible = False
		self.hide()
		if self.__delaycbid > 0:
			BigWorld.cancelCallback( self.__delaycbid )
			self.__delaycbid = 0

	def __isInAllRanks( self, tongDBID, playerName ):
		pyAllPanel = self.__pyTabCtrl.pyPages[0].pyPanel
		rankItems = pyAllPanel.getRankItems()
		for rankItem in rankItems:
			if rankItem.tongDBID == tongDBID and \
			rankItem.playerName == playerName:
				return True
		return False
	
	def __cancelCountdown( self ):
		if self.__cdcbid > 0:
			BigWorld.cancelCallback( self.__cdcbid )
			self.__cdcbid = 0
	
	def __getEnemyName( self ):
		"""
		获取敌方帮会名称
		"""
		enemyName = ""
		pTongDBID = BigWorld.player().tong_dbID
		for tongDBID, tongName in self.__tongNames.items():
			if pTongDBID != tongDBID:
				enemyName = tongName
		return enemyName
	
	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def onLeaveWorld( self ):
		for pyPanel in self.__pyTabCtrl.pyPanels:
			pyPanel.clearItems()
		self.__pyLbLeft.visible = False
		self.__pyLbRight.visible = False
		self.__pyLbInter.visible = False
		self.__cancelCountdown()
		self.__endTime = 0.0
		self.__enemyInter = 0
		self.__ownInter = 0
		self.__ranks = {}					#排序数据
		self.__tongNames = {}				#帮会名称
		self.hide()

	def show( self ):
		player = BigWorld.player()
		Window.show( self )

	def hide( self ):
		Window.hide( self )

# -----------------------------------------------------------------
# 统计面板
# -----------------------------------------------------------------
from guis.controls.TabCtrl import TabPanel

class RankPanel( TabPanel ): #
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__initialize( panel )

	def __initialize( self, panel ):
		class ListPanel( ODListPanel ) :
			def getViewItem_( self ) :
				return RankItem( self )

		self.__pyListPanel = ListPanel( panel.listPanel, panel.listBar )
		self.__pyListPanel.onItemSelectChanged.bind( self.__interSelChanged )
		self.__pyListPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyListPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyListPanel.autoSelect = False
		self.__pyListPanel.itemHeight = 22
		self.__pyListPanel.ownerDraw = True							# 开启自定义绘制
		self.__pyListPanel.sbarState = ScrollBarST.SHOW

		self.__pytaxisBtns = {}
		for name, item in panel.children:
			if name.startswith( "btn_" ):
				index = int( name.split( "_" )[1] )
				pySortBtn = HButtonEx( item )
				pySortBtn.index = index
				pySortBtn.reverse = False
				pySortBtn.setExStatesMapping( UIState.MODE_R3C1 )
				labelGather.setPyBgLabel( pySortBtn, "TongAbout:WarIntergral", name )
				pySortBtn.onLClick.bind( self.__onSortByTaxi )
				self.__pytaxisBtns[index] = pySortBtn

	def __onInitItem( self, pyViewItem ) :
		pass

	def __onDrawItem( self, pyViewItem ) :
		pyViewItem.updateRank()

	def __interSelChanged( self, pyInter ):
		pass

	def __onSortByTaxi( self, pyBtn ) :
		index = pyBtn.index
		reverse = pyBtn.reverse
		self.__pyListPanel.sort( key = lambda rankInfo : rankInfo.items[index], reverse = reverse )
		pyBtn.reverse = not reverse

	def initRank( self, rankInfo ):
		pyViewItems = self.__pyListPanel.pyViewItems
		playerNames = [ pyViewItem.listItem.playerName for pyViewItem in pyViewItems]
		if rankInfo.playerName in playerNames:return
		pyInterItem = RankItem( self.__pyListPanel )
		self.__pyListPanel.addItem( rankInfo )
		pyInterItem.updateRank()
		self.__pyListPanel.sort( key = lambda rankInfo : rankInfo.items[1], reverse = True )

	def updateRank( self, tongDBID, playerName, kill, dead, area ):
		for pyViewItem in self.__pyListPanel.pyViewItems:
			listItem = pyViewItem.listItem
			if listItem.playerName == playerName:
				listItem.updateInfo( kill, dead, area )
				pyViewItem.updateRank()
		self.__pyListPanel.sort( key = lambda rankInfo : rankInfo.items[1], reverse = True )

	def delRank( self, playerName ):
		for pyViewItem in self.__pyListPanel.pyViewItems:
			listItem = pyViewItem.listItem
			if listItem.playerName == playerName:
				self.__pyListPanel.removeItem( listItem )
				break
	
	def updateReport( self, report ):
		for pyViewItem in self.__pyListPanel.pyViewItems:
			listItem = pyViewItem.listItem
			playerName = listItem.playerName
			if playerName in report:
				pass

	def refurbishStatusFlag( self ):
		for pyViewItem in self.__pyListPanel.pyViewItems:
			pyViewItem.refurbishStatusFlag()

	def clearItems( self ):
		self.__pyListPanel.clearItems()
	
	def getRankItems( self ):
		return self.__pyListPanel.items
		
# -------------------------------------------------------------------------------------------
#积分信息控件
# -------------------------------------------------------------------------------------------
class RankItem( ViewItem ):
	def __init__( self, pyPanel ):
		item = GUI.load( "guis/general/tongabout/citywar/reportitem.gui" )
		uiFixer.firstLoadFix( item )
		ViewItem.__init__( self, pyPanel, item )
		self.__pyIcon = PyGUI( item.icon )
		self.__pyColItems = []
		for name, item in item.children:
			if name.startswith( "col_" ):
				index = int( name.split( "_" )[1] )
				self.__pyColItems.append( ColItem( item ) )

	def updateRank( self ):
		listItem = self.listItem
		if listItem is None:return
		player = BigWorld.player()
		pTongDBID = player.tong_dbID
		tongDBID = listItem.tongDBID
		cwTongInfos = player.tongInfos
		dTongDBID = 0
		if cwTongInfos.has_key( "defend" ):
			dTongDBID = cwTongInfos["defend"]
		foreColor = cscolors["c1"]
		texturePath = ""
		iconMapping = (1, 1)
		if dTongDBID > 0: #有防守方，王位争夺战
			if tongDBID == pTongDBID: #同一帮会
				foreColor = cscolors["c4"]
				if pTongDBID == dTongDBID:
					iconMapping = (1, 2)
				texturePath = "guis/general/tongabout/citywar/ourbg.tga"
			else:
				if tongDBID == dTongDBID: #防守方
					foreColor = cscolors["c8"]
					iconMapping = (1, 2)
				else:
					if pTongDBID == dTongDBID:
						foreColor = cscolors["c8"]
					else:
						foreColor = cscolors["c3"]
				texturePath = "guis/general/tongabout/citywar/enemybg.tga"
		else:	#资源点争夺战，cityWarPointLogs数据为空
			if tongDBID == pTongDBID:
				foreColor = cscolors["c4"]
				texturePath = "guis/general/tongabout/citywar/ourbg.tga"
			else:
				foreColor = cscolors["c8"]
				texturePath = "guis/general/tongabout/citywar/enemybg.tga"
		for pyColItem in self.__pyColItems:
			pyColItem.textColor = foreColor
		util.setGuiState( self.__pyIcon.getGui(),(1, 2), iconMapping )
		self.texture = texturePath
		for pyCItem, info in zip( self.__pyColItems, listItem.items ) :
			pyCItem.update( str( info ))

	def refurbishStatusFlag( self ):
		listItem = self.listItem
		if listItem is None:return
		tongDBID = listItem.tongDBID
		cwTongInfos = player.tongInfos
		player = BigWorld.player()
		pTongDBID = player.tong_dbID
		dTongDBID = 0
		if cwTongInfos.has_key( "defend" ):
			dTongDBID = cwTongInfos["defend"]
		iconMapping = (1, 1)
		foreColor = cscolors["c1"]
		if dTongDBID: #有防守方，王位争夺战
			if tongDBID == pTongDBID: #同一帮会
				foreColor = cscolors["c4"]
				if pTongDBID == dTongDBID:
					iconMapping = (1, 2)
			else:
				if tongDBID == dTongDBID: #防守方
					foreColor = cscolors["c8"]
					iconMapping = (1, 2)
				else:
					if pTongDBID == dTongDBID:
						foreColor = cscolors["c8"]
					else:
						foreColor = cscolors["c3"]
		else:
			if tongDBID == pTongDBID:
				foreColor = cscolors["c4"]
			else:
				foreColor = cscolors["c8"]
		for pyColItem in self.__pyColItems:
			pyColItem.textColor = foreColor
		util.setGuiState( self.__pyIcon.getGui(),(1, 2), iconMapping )

# ----------------------------------------------------------------
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
class ColItem( Control ) :
	def __init__( self, colItem, pyBinder = None ) :
		Control.__init__( self, colItem, pyBinder )
		self.focus = False
		self.crossFocus = True

		self.pyText_ = None
		self.initialize_( colItem )

	def initialize_( self, colItem ) :
		self.pyText_ = StaticText( colItem.lbText )
		self.pyText_.text = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		if self.pyText_.left < 0 or self.pyText_.right > self.width :
			FullText.show( self, self.pyText_ )
		return Control.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		FullText.hide()
		return Control.onMouseLeave_( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, info ) :
		self.pyText_.text = info
		if self.isMouseHit() and \
		( self.pyText_.left < 0 or self.pyText_.right > self.width ) :
			FullText.show( self, self.pyText_, False )
	
	
	def _setTextColor( self, color ):
		self.pyText_.color = color
	
	def _getTextColor( self ):
		return self.pyText_.color
	
	textColor = property( _getTextColor, _setTextColor )							# 获取/设置 Item 在父列表中的索引值
	

class RankInfo:
	def __init__( self, tongDBID = 0, playerName = "",  kill = 0, dead = 0, area = "" ):
		self.tongDBID = tongDBID
		self.playerName = playerName
		self.kill = kill
		self.dead = dead
		self.area = area
		self.items = [playerName, kill, dead, area]

	def updateInfo( self, kill, dead, area ):
		self.kill = kill
		self.dead = dead
		self.area = area
		self.items = [self.playerName, kill, dead, area]

#---------------------------------------------------------------------------------------------
from guis.common.RootGUI import RootGUI
from AbstractTemplates import Singleton

class FHLTTimer( RootGUI, Singleton ):
	"""
	烽火连天倒计时面板
	"""
	
	__triggers = {}
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongfhlt/fhltimer.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.__remainTime = 0.0				#剩余时间
		self.__remTimeCBID = 0				#倒计时的cbid
		self.__flashBtnCBID = 0					#按钮闪烁的cbid
		self.__isFlash = True 					# 用于控制按钮闪烁
		self.__initialize( wnd )
		self.addToMgr( "fhltimer" )
		
	def __initialize( self, wnd ):
		self.__pyStTimeText = StaticText( wnd.stTimeText )
		self.__pyStTimeText.text = ""
		
		self.__pyBtnStart = HButtonEx( wnd.btnStart )
		self.__pyBtnStart.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnStart.focus = False
		self.__pyBtnStart.crossFocus = False
		labelGather.setPyBgLabel( self.__pyBtnStart, "TongAbout:FHLTTimer", "btnStart" )
		
		self.__pyStTimer = StaticText( wnd.bgTimer.stTimer )
		self.__pyStTimer.text = ""
		
		self.__btnFader = wnd.btnStart.fader
		self.__btnFader.speed = 0.5
		self.__btnFader.value = 1.0
		
		self.__bgTimer = wnd.bgTimer
		
	def dispose( self ) :
		RootGUI.dispose( self )
		self.__class__.releaseInst()
	
	def onUpdateTime( self, time ):
		self.__remainTime = time
		self.__cancelRemTime()
		self.__pyBtnStart.setState( UIState.COMMON )
		self.__remTimeCBID = BigWorld.callback( 0.0, self.__remTimeCount )
		self.show()
	
	def __remTimeCount( self ):
		"""
		开始倒计时
		"""
		self.__remainTime -= 1.0
		if self.__remainTime > 0:
			mins = self.__remainTime/60
			secs = self.__remainTime%60
			timeText = "%02d:%02d:%02d"%( 0, mins, secs )
			self.__pyStTimeText.text = labelGather.getText( "TongAbout:FHLTTimer", "remTime")%self.__remainTime
			self.__pyStTimer.text = timeText
			if self.__remainTime <= 5.0:			#开始按钮高亮并闪烁
				self.__pyBtnStart.setState( UIState.HIGHLIGHT )
				self.__flashBtnStart()
			self.__remTimeCBID = BigWorld.callback( 1.0, self.__remTimeCount )
		else:
			self.hide()

	def __flashBtnStart( self ):
		self.__stopFlash()
		if self.__isFlash:
			self.__btnFader.value = 1.0
		else:
			self.__btnFader.value = 0.2
		self.__isFlash = not self.__isFlash
		self.__flashBtnCBID = BigWorld.callback( self.__btnFader.speed, self.__flashBtnStart  )
		
	def __cancelRemTime( self ):
		"""
		取消倒计时
		"""
		if self.__remTimeCBID > 0:
			BigWorld.cancelCallback( self.__remTimeCBID )
			self.__remTimeCBID = 0
	
	def __stopFlash( self ):
		"""
		停止闪烁
		"""
		if self.__flashBtnCBID:
			BigWorld.cancelCallback( self.__flashBtnCBID )
			self.__flashBtnCBID = 0
	
	def show( self ):
		RootGUI.show( self )

	def onLeaveWorld( self ):
		self.hide()
	
	def hide( self ):
		self.__cancelRemTime()
		self.__stopFlash()
		self.__btnFader.value = 1.0
		self.__pyStTimeText.text = ""
		self.__pyStTimer.text = ""
		self.__pyBtnStart.setState( UIState.COMMON )
		RootGUI.hide( self )
		
	@classmethod
	def __onUpdateTime( SELF, time ):
		SELF.inst.onUpdateTime( time )
		
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_UPDATE_FHLT_PROTECT_TIME"] = SELF.__onUpdateTime
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[evtMacro]( *args )

# -----------------------------------------------------------------------
class FHLTTips( RootGUI, Singleton ):
	"""
	剩余时间 积分面板
	"""
	__triggers = {}

	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongfhlt/fhltinfo.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.__cdcbid = 0
		self.__initialize( wnd )
		self.addToMgr( "fhltips" )
	
	def __initialize( self, panel ):
		self.__pyBtnClose = Button( panel.btnClose )
		self.__pyBtnClose.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnClose.onLClick.bind( self.__onClose )
		
		self.__pyRtRTime = CSRichText( panel.rtRTime )
		self.__pyRtRTime.text = ""
		
		self.__pyItemsPanel = ItemsPanel( panel.itemsPanel, panel.itemsBar )
		self.__tongs = {}
	
	def __onClose( self, pyBtn ):
		if pyBtn is None:return
		self.hide()
	
	def __cancelCountdown( self ):
		"""
		取消倒计时
		"""
		if self.__cdcbid > 0:
			BigWorld.cancelCallback( self.__cdcbid )
			self.__cdcbid = 0

	def show( self ):
		RootGUI.show( self )
	
	def hide( self ):
		self.__cancelCountdown()
		self.__pyRtRTime.text = ""
		RootGUI.hide( self )

	def onLeaveWorld( self ):
		self.__tongs = {}
		self.__pyItemsPanel.clearItems()
		self.hide()

	def __remainCountdown( self ):
		"""
		剩余时间倒计时
		"""
		remainTime = self.__endTime - Time.time()
		if remainTime > 0:
			min = int( remainTime )/60
			sec = int( remainTime )%60
			timeText = "%02d:%02d"%( min, sec )
			timeText = PL_Font.getSource( timeText , fc = ( 230, 227, 185, 255 ) )
			timeText = labelGather.getText( "TongAbout:FHLTRankWnd", "remainTime" ) % timeText
			self.__pyRtRTime.text = PL_Font.getSource( timeText, fc = ( 84, 194, 23, 255 ) )
			self.__cdcbid = BigWorld.callback( 1.0, self.__remainCountdown )
		else:
			self.__cancelCountdown()
	
	def __getInfoColor( self, dbid ):
		"""
		获取颜色
		"""
		player = BigWorld.player()
		tongInfos = player.tongInfos
		ptdbID = player.tong_dbID
		dTongDBID = 0
		if tongInfos.has_key( "defend" ):
			dTongDBID = tongInfos["defend"]
		foreColor = cscolors["c1"]
		if dTongDBID: #有防守方，王位争夺战
			if dbid == ptdbID: #同一帮会
				foreColor = cscolors["c4"]
			else:
				if dbid == dTongDBID: #防守方
					foreColor = cscolors["c8"]
				else:
					if ptdbID == dTongDBID:
						foreColor = cscolors["c8"]
					else:
						foreColor = cscolors["c3"]
		else:
			if dbid == ptdbID:
				foreColor = cscolors["c4"]
			else:
				foreColor = cscolors["c8"]
		return foreColor

	@classmethod
	def __onEnterSpace( SELF, endTime, tongInfos ):
		self = SELF.inst
		player = BigWorld.player()
		pTongDBID = player.tong_dbID
		ltName = tongInfos["leftTongName"]
		rtName = tongInfos["rightTongName"]
		ltDBID = tongInfos["left"]
		rtDBID = tongInfos["right"]
		self.__tongs[ltDBID] = ltName
		self.__tongs[rtDBID] = rtName
		for dbid, name in self.__tongs.items():
			item = GUI.load( "guis/general/tongabout/tongfhlt/infoitem.gui" )
			uiFixer.firstLoadFix( item )
			pyInfoItem = InfoItem( item, dbid, name )
			color = self.__getInfoColor( dbid )
			
			pyInfoItem.setForeColor( color )
			self.__pyItemsPanel.addItem( pyInfoItem )
		self.__endTime = endTime
		self.__cancelCountdown()
		self.__cdcbid = BigWorld.callback( 0, self.__remainCountdown )
		self.show()
		
	@classmethod
	def __onUpdatePoint( SELF, tongDBID, point ):
		"""
		更新积分
		"""
		self = SELF.inst
		for pyItem in self.__pyItemsPanel.pyItems:
			if pyItem.dbid == tongDBID:
				pyItem.updateInteral( point )
		self.__pyItemsPanel.sort( key = lambda pyItem: pyItem.interal, reverse = True )
		
	@classmethod
	def __onLeaveSpace( SELF ):
		"""
		离开副本
		"""
		self = SELF.inst
		self.__tongs = {}
		self.__pyItemsPanel.clearItems()
		self.hide()
		
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_ENTER_FHLT_SPACE"] = SELF.__onEnterSpace
		SELF.__triggers["EVT_ON_UPDATE_FHLT_POINT"] = SELF.__onUpdatePoint
		SELF.__triggers["EVT_ON_LEAVE_FHLT_SPACE"] = SELF.__onLeaveSpace
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[evtMacro]( *args )

class InfoItem( PyGUI ):
	def __init__( self, item, dbid, name ):
		PyGUI.__init__( self, item )
		self.__pyRtName = CSRichText( item.rtName )
		self.__pyRtName.text = name
		
		self.__pyRtInteral = CSRichText( item.rtInteral )
		self.__pyRtInteral.text = ""

		self.dbid = dbid
		self.interal = 0
		self.updateInteral( self.interal )
	
	def updateInteral( self, interal ):
		self.interal = interal
		self.__pyRtInteral.text = "%02d"%interal
	
	def setForeColor( self, color ):
		self.__pyRtName.foreColor = color
		self.__pyRtInteral.foreColor = color

FHLTTimer.registerTriggers()
FHLTTips.registerTriggers()