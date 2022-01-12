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
from guis.tooluis.fulltext.FullText import FullText
from TaxRateSetBox import TaxRateSetBox
from Time import Time
from Color import cscolors
import Timer
import csconst
import csstring
import csdefine

class WarIntergral( Window ):
	"""
	城战积分界面
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/citywar/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__registerTriggers()
		self.__interInfos = {}
		self.lTongDBID = 0
		self.rTongDBID = 0
		self.dTongDBID = 0
		self.timeCBID = 0
		self.endTime = 0.0
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyTabCtrl = TabCtrl( wnd.tabCtrl )
		index = 0
		while True :											#初始化TabCtrl
			tabName = "tab_" + str( index )
			tab = getattr( wnd.tabCtrl, tabName, None )
			if tab is None : break
			panelName = "panel_" + str( index )
			panel = getattr( wnd.tabCtrl, panelName, None )
			if panel is None : break
			pyBtn = TabButton( tab )
			pyBtn.index = index
			pyBtn.isOffsetText = True
			pyBtn.setStatesMapping( UIState.MODE_R4C1 )
			pyBtn.onMouseEnter.bind( self.__onMouseEnterBtn )
			pyBtn.onMouseLeave.bind( self.__onMouseLeaveBtn )
			labelGather.setPyBgLabel( pyBtn, "TongAbout:WarIntergral", tabName )
			pyPanel = InterPanel( panel )
			pyPage = TabPage( pyBtn, pyPanel )
			self.__pyTabCtrl.addPage( pyPage )
			index += 1

		self.__pyRtContact = CSRichText( wnd.rtContact )
		self.__pyRtContact.maxWidth = 370.0
		self.__pyRtContact.text = ""

		self.__pyRtRemainTime = CSRichText( wnd.rtRemainTime )
		self.__pyRtRemainTime.text = ""

		self.__pyStEnemyTong = StaticText( wnd.stEnemyTong )
		self.__pyStEnemyTong.text = ""

		labelGather.setLabel( wnd.lbTitle, "TongAbout:WarIntergral", "lbTitle" )

	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_INTERGRAL_WINDOW"] = self.__onShowWnd
		self.__triggers["EVT_ON_ENTER_CITYWAR_SPACE"] = self.__onInitTime
		self.__triggers["EVT_ON_UPDTAE_WAR_REPORT"] = self.__onRecieveInter
		self.__triggers["EVT_ON_ROLE_LEAVE_CITYWAR_SPACE"] = self.__onRoleLeaveWar
		self.__triggers["EVT_ON_RECIEVE_CITY_TAXRATE"] = self.__onTaxRateBoxShow
		self.__triggers["EVT_ON_TONG_CITYWAR_OVER"]		= self.__onTongCityWarOver
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
		self.visible = not self.visible
	
	def __onMouseEnterBtn( self, pyBtn ):
		"""
		鼠标放到分页按钮
		"""
		if pyBtn.index == 0:return
		info = pyBtn.text
		if info == "":return
		wideStr = csstring.toWideString( info )
		if len( wideStr ) > 5:
			toolbox.infoTip.showToolTips( pyBtn, wideStr )
	
	def __onMouseLeaveBtn( self ):
		"""
		隐藏提示信息
		"""
		toolbox.infoTip.hide()

	def __onInitTime( self, warRemainTime, tongInfos ):
		"""
		战场时间刷新
		"""
		self.__interInfos = {}
		self.__clearItems()
		tongDBID = BigWorld.player().tong_dbID
		self.lTongDBID = tongInfos["left"]
		self.rTongDBID = tongInfos["right"]
		lTongName = tongInfos["leftTongName"]
		rTongName = ""
		if self.rTongDBID:
			rTongName = tongInfos["rightTongName"]
		self.__interInfos[self.lTongDBID] = []
		self.__interInfos[self.rTongDBID] = []
		self.__interInfos[self.dTongDBID] = []
		isHasDefend = tongInfos.has_key( "defend" )
		btnLeft = self.__pyTabCtrl.pyPages[1].pyBtn
		btnRight = self.__pyTabCtrl.pyPages[2].pyBtn
		btnDefend = self.__pyTabCtrl.pyPages[3].pyBtn
		btnRight.visible = self.rTongDBID > 0
		btnDefend.visible = isHasDefend
		btnLeft.text = lTongName
		btnRight.text = rTongName
		conTongNames = ""		#敌对帮会名字
		if not isHasDefend:
			if self.__checkIsLeague( self.lTongDBID, tongDBID ):
				btnLeft.commonForeColor = cscolors["c4"]
				btnLeft.selectedForeColor = cscolors["c4"]
				btnRight.commonForeColor = cscolors["c8"]
				btnRight.selectedForeColor = cscolors["c8"]
				if rTongName != "":
					conTongNames = labelGather.getText( "TongAbout:WarIntergral", "oneConTong" )%rTongName
			else:
				btnLeft.commonForeColor = cscolors["c8"]
				btnLeft.selectedForeColor = cscolors["c8"]
				btnRight.commonForeColor = cscolors["c4"]
				btnRight.selectedForeColor = cscolors["c4"]
				conTongNames = labelGather.getText( "TongAbout:WarIntergral", "oneConTong" )%lTongName
		else:
			self.dTongDBID = tongInfos["defend"]
			dTongName = tongInfos["defendTongName"]
			self.__interInfos[self.dTongDBID] = []
			btnDefend.text = dTongName
			if self.__checkIsLeague( self.dTongDBID, tongDBID ):
				btnDefend.commonForeColor = cscolors["c4"]
				btnDefend.selectedForeColor = cscolors["c4"]
				btnLeft.commonForeColor = cscolors["c8"]
				btnLeft.selectedForeColor = cscolors["c8"]
				btnRight.commonForeColor = cscolors["c8"]
				btnRight.selectedForeColor = cscolors["c8"]
				tongNames = ""
				if rTongName != "":
					tongNames = "%s,%s"%( lTongName, rTongName )
				else:
					tongNames = "%s"%lTongName
				conTongNames = labelGather.getText( "TongAbout:WarIntergral", "isDefTong" )%tongNames
			else:
				btnDefend.commonForeColor = cscolors["c8"]
				btnDefend.selectedForeColor = cscolors["c8"]
				if self.__checkIsLeague( self.lTongDBID, tongDBID ):
					btnLeft.commonForeColor = cscolors["c4"]
					btnLeft.selectedForeColor = cscolors["c4"]
					btnRight.commonForeColor = cscolors["c3"]
					btnRight.selectedForeColor = cscolors["c3"]
					if rTongName != "":
						conTongNames = labelGather.getText( "TongAbout:WarIntergral", "notDefTong" )%( rTongName, dTongName )
					else:
						noRightTong = labelGather.getText( "TongAbout:WarIntergral", "norightTong" )
						conTongNames = labelGather.getText( "TongAbout:WarIntergral", "notDefTong" )%( noRightTong, dTongName )
				else:
					btnLeft.commonForeColor = cscolors["c3"]
					btnLeft.selectedForeColor = cscolors["c3"]
					btnRight.commonForeColor = cscolors["c4"]
					btnRight.selectedForeColor = cscolors["c4"]
					conTongNames = labelGather.getText( "TongAbout:WarIntergral", "notDefTong" )%( lTongName, dTongName )
		self.__pyStEnemyTong.text = conTongNames
		self.__cancelRemianTimer()
		self.endTime = warRemainTime + Time.time()
		self.__refurbishStatusFlag()
		self.__remainTimeUpdate()
		
	def __checkIsLeague( self, tongDBID1,tongDBID2 ):
		"""
		判断是否是同盟帮会成员
		"""
		player = BigWorld.player()	
		belong1 = player.getCityWarTongBelong( tongDBID1 )
		belong2 = player.getCityWarTongBelong( tongDBID2 )
		return belong1 == belong2
		
	def __remainTimeUpdate( self ):
		remainTime = self.endTime - Time.time()
		self.__pyRtRemainTime.text = labelGather.getText( "TongAbout:WarIntergral", "remainTime" )%( int( remainTime/60 ), int( remainTime%60 ) )
		if remainTime <= 0.0:
			self.__pyRtRemainTime.text = ""
			self.__cancelRemianTimer()
		self.timeCBID = BigWorld.callback( 1.0, self.__remainTimeUpdate )

	def __cancelRemianTimer( self ):
		if self.timeCBID != 0:
			BigWorld.cancelCallback( self.timeCBID )
			self.timeCBID = 0	
	
	def __onRecieveInter( self, playerName, tongDBID, killCount, deadCount, inArea ):
		"""
		接受战场成员积分数据
		"""
		player = BigWorld.player()
		pyAllPanel = self.__pyTabCtrl.pyPages[0].pyPanel
		pyLeftPanel = self.__pyTabCtrl.pyPages[1].pyPanel
		pyRightPanel = self.__pyTabCtrl.pyPages[2].pyPanel
		pyDefendPanel = self.__pyTabCtrl.pyPages[3].pyPanel
		myTongDBID = player.tong_dbID
		area = ""
		if inArea:
			area = labelGather.getText( "TongAbout:WarIntergral", "inArea" )
		else:
			area = labelGather.getText( "TongAbout:WarIntergral", "out" )
		leftInters = self.__interInfos[self.lTongDBID]
		rightInters = self.__interInfos[self.rTongDBID]
		defeInters = self.__interInfos[self.dTongDBID]
		if tongDBID > 0:
			if tongDBID == self.lTongDBID or player.getCityWarTongBelong( tongDBID ) == csdefine.CITY_WAR_FINAL_FACTION_DEFEND:	#left
				if playerName in [interInfo.playerName for interInfo in leftInters]:
					for interInfo in leftInters:
						if interInfo.playerName == playerName:
							interInfo.updateInfo( killCount, deadCount, area )
					pyLeftPanel.updateIntergral( playerName, tongDBID, killCount, deadCount, area )
				else:
					interInfo = InterInfo( playerName, tongDBID, killCount, deadCount, area )
					leftInters.append( interInfo )
					pyLeftPanel.initIntergral( interInfo )
			elif tongDBID == self.rTongDBID or player.getCityWarTongBelong( tongDBID ) == csdefine.CITY_WAR_FINAL_FACTION_DEFEND:	#right
				if playerName in [interInfo.playerName for interInfo in rightInters]:
					for interInfo in rightInters:
						if interInfo.playerName == playerName:
							interInfo.updateInfo( killCount, deadCount, area )
					pyRightPanel.updateIntergral( playerName, tongDBID, killCount, deadCount, area )
				else:
					interInfo = InterInfo( playerName, tongDBID, killCount, deadCount, area )
					rightInters.append( interInfo )
					pyRightPanel.initIntergral( interInfo )
					
			elif tongDBID == self.dTongDBID:
				if playerName in [interInfo.playerName for interInfo in defeInters]:
					for interInfo in defeInters:
						if interInfo.playerName == playerName:
							interInfo.updateInfo( killCount, deadCount, area )
					pyDefendPanel.updateIntergral( playerName, tongDBID, killCount, deadCount, area )
				else:
					interInfo = InterInfo( playerName, tongDBID, killCount, deadCount, area )
					defeInters.append( interInfo )
					pyDefendPanel.initIntergral( interInfo )
			if self.__isInAllIters( tongDBID, playerName ):
				pyAllPanel.updateIntergral( playerName, tongDBID, killCount, deadCount, area )
			else:
				interInfo = InterInfo( playerName, tongDBID, killCount, deadCount, area )
				pyAllPanel.initIntergral( interInfo )
				
		else: # 玩家退出副本，清空积分信息
			for leftInter in leftInters:
				if leftInter.playerName == playerName:
					leftInters.remove( leftInter )
					pyLeftPanel.delIntergral( playerName )
			for rightInter in rightInters:
				if rightInter.playerName == playerName:
					rightInters.remove( leftInter )
					pyRightPanel.delIntergral( playerName )
			for defeInter in defeInters:
				if defeInter.playerName == playerName:
					defeInters.remove( leftInter )
					pyDefendPanel.delIntergral( playerName )
			pyAllPanel.delIntergral( playerName )
		contactStr = ""
		if self.dTongDBID > 0:	#有防守方
			if self.rTongDBID > 0:
				contactStr = labelGather.getText( "TongAbout:WarIntergral", "contactsdef" )%( len( leftInters ), len( rightInters ), len( defeInters ) )
			else:
				contactStr = labelGather.getText( "TongAbout:WarIntergral", "contacts" )%( len( leftInters ), len( defeInters ) )
		else:
			if myTongDBID == self.rTongDBID:
				contactStr = labelGather.getText( "TongAbout:WarIntergral", "contacts" )%( len( leftInters ), len( rightInters ) )
			else:
				contactStr = labelGather.getText( "TongAbout:WarIntergral", "contacts" )%( len( rightInters ), len( leftInters ) )
				
		self.__pyRtContact.text = contactStr
	
	def __onTongCityWarOver( self ):
		"""
		结束主动弹出统计框
		"""
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示
		self.show()
		self.__cancelRemianTimer()
		self.__pyRtRemainTime.text = ""
	
	def __isInAllIters( self, tongDBID, playerName ):
		interItems = self.__pyTabCtrl.pyPages[0].pyPanel.getInterItems()
		isInAll = False
		for interItem in interItems:
			if interItem.tongDBID == tongDBID and \
			interItem.playerName == playerName:
				isInAll = True
		return isInAll
	
	def __onUpdateReport( self, report ):
		pyPanel = self.__pyTabCtrl.pySelPage.pyPanel
		pyPanel.updateReport( report )

	def __refurbishStatusFlag( self ):
		for pyPage in self.__pyTabCtrl.pyPages:
			pyPanel = pyPage.pyPanel
			pyPanel.refurbishStatusFlag()

	def __onRoleLeaveWar( self, role ):
		pass

	def __onLeaveWorld( self ):
		self.__interInfos = {}
		self.__clearItems()

	def __onTaxRateBoxShow( self, rate ):
		TaxRateSetBox.instance().show( rate )

	def __onLeaveWar( self ): #离开战场
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().tong_leaveCityWarSpace()
		# "是否确定离开帮会战场？"
		showMessage( 0x0921, "", MB_OK_CANCEL, query )
		return True

	def __clearItems( self ):
		for pyPage in self.__pyTabCtrl.pyPages:
			pyPanel = pyPage.pyPanel
			pyPanel.clearItems()

	# -----------------------------------------------------------
	# public
	# -----------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		Window.show( self )

	def hide( self ):
		Window.hide( self )

	def onLeaveWorld( self ):
		self.__cancelRemianTimer()
		self.__onLeaveWorld()
		self.hide()
# -----------------------------------------------------------------
# 统计面板
# -----------------------------------------------------------------
from guis.controls.TabCtrl import TabPanel

class InterPanel( TabPanel ): #列表
	def __init__( self, tabPanel ):
		TabPanel.__init__( self, tabPanel )
		self.__initialize( tabPanel )

	def __initialize( self, tabPanel ):
		class ListPanel( ODListPanel ) :
			def getViewItem_( self ) :
				return InterItem( self )

		self.__pyListPanel = ListPanel( tabPanel.listPanel, tabPanel.listBar )
		self.__pyListPanel.onItemSelectChanged.bind( self.__interSelChanged )
		self.__pyListPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyListPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyListPanel.autoSelect = False
		self.__pyListPanel.itemHeight = 22
		self.__pyListPanel.ownerDraw = True							# 开启自定义绘制

		self.__pytaxisBtns = {}
		for name, item in tabPanel.children:
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
		pyViewItem.updateInter()

	def __interSelChanged( self, pyInter ):
		pass

	def __onSortByTaxi( self, pyBtn ) :
		index = pyBtn.index
		reverse = pyBtn.reverse
		
		self.__pyListPanel.sort( key = lambda interInfo : interInfo.items[index], reverse = reverse )
		pyBtn.reverse = not reverse

	def initIntergral( self, interInfo ):
		pyViewItems = self.__pyListPanel.pyViewItems
		playerNames = [ pyViewItem.listItem.playerName for pyViewItem in pyViewItems]
		if interInfo.playerName in playerNames:return
		pyInterItem = InterItem( self.__pyListPanel )
		self.__pyListPanel.addItem( interInfo )
		pyInterItem.updateInter()
		self.__pyListPanel.sort( key = lambda interInfo : interInfo.items[1], reverse = True )

	def updateIntergral( self, playerName, tongDBID, killCount, deadCount, area ):
		for pyViewItem in self.__pyListPanel.pyViewItems:
			listItem = pyViewItem.listItem
			if listItem.playerName == playerName:
				listItem.updateInfo( killCount, deadCount, area )
				pyViewItem.updateInter()
		self.__pyListPanel.sort( key = lambda interInfo : interInfo.items[1], reverse = True )

	def delIntergral( self, playerName ):
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
	
	def getInterItems( self ):
		return self.__pyListPanel.items

# ---------------------------------------------------------------------
from guis.common.Frame import HVFrame
class TaxisButton( Button ) :

	__pyHighlight_bg = None													# 高亮状态的背景
	__pyPressed_bg = None 													# 按下状态的背景

	def __init__( self, button ) :
		Button.__init__( self, button )
		self.isOffsetText = True
		self.__isSort = False
		self.__taxisReverse = False
		if TaxisButton.__pyHighlight_bg is None :
			gui = GUI.load( "guis/general/commissionsale/shopsviewer/taxisbtnbg_highlight.gui" )
			uiFixer.firstLoadFix( gui )
			TaxisButton.__pyHighlight_bg = HVFrame( gui )
			gui = GUI.load( "guis/general/commissionsale/shopsviewer/taxisbtnbg_pressed.gui" )
			uiFixer.firstLoadFix( gui )
			TaxisButton.__pyPressed_bg = HVFrame( gui )
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setStateView_( self, state ) :
		if not self.__isSort:return
		Button.setStateView_( self, state )
		if state == UIState.HIGHLIGHT :
			self.addPyChild( TaxisButton.__pyHighlight_bg, "statusBg" )
			TaxisButton.__pyHighlight_bg.width = self.width + 1
			TaxisButton.__pyHighlight_bg.height = self.height + 1
			TaxisButton.__pyHighlight_bg.pos = 0, 0
		elif state == UIState.PRESSED :
			self.addPyChild( TaxisButton.__pyPressed_bg, "statusBg" )
			TaxisButton.__pyPressed_bg.width = self.width + 1
			TaxisButton.__pyPressed_bg.height = self.height + 1
			TaxisButton.__pyPressed_bg.pos = 0, 1
		else :
			self.getGui().delChild( "statusBg" )

	def onLClick_( self, mode ) :
		if not self._setIsSort:return
		if self.isMouseHit() :
			self.taxisReverse = not self.__taxisReverse
		return Button.onLClick_( self, mode )

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTaxisReverse( self ) :
		return self.__taxisReverse

	def _setTaxisReverse( self, reverse ) :
		self.__taxisReverse = reverse

	def _getIsSort( self ):
		return self.__isSort

	def _setIsSort( self, isSort ):
		self.__isSort = isSort

	taxisReverse = property( _getTaxisReverse, _setTaxisReverse )			# 当前是否在反序排列
	isSort = property( _getIsSort, _setIsSort )								# 设置排序状态
# -----------------------------------------------------------
# 统计字段
# -----------------------------------------------------------
from guis.common.PyGUI import PyGUI
from guis.controls.ListItem import SingleColListItem
class InterItem( ViewItem ):
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
				
	def __checkIsLeague( self, tongDBID1,tongDBID2 ):
		"""
		判断是否是同盟帮会成员
		"""
		player = BigWorld.player()	
		belong1 = player.getCityWarTongBelong( tongDBID1 )
		belong2 = player.getCityWarTongBelong( tongDBID2 )
		return belong1 == belong2

	def updateInter( self ):
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
			if self.__checkIsLeague( tongDBID, pTongDBID ):
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
			if self.__checkIsLeague( tongDBID, pTongDBID ):
				foreColor = cscolors["c4"]
			else:
				foreColor = cscolors["c8"]
		for pyColItem in self.__pyColItems:
			pyColItem.textColor = foreColor
		util.setGuiState( self.__pyIcon.getGui(),(1, 2), iconMapping )

class InterInfo:
	def __init__( self, playerName = "", tongDBID = 0, killCount = 0, deadCount = 0, area = "" ):
		self.playerName = playerName
		self.tongDBID = tongDBID
		self.killCount = killCount
		self.deadCount = deadCount
		self.area = area
		self.items = [playerName, killCount, deadCount, area]

	def updateInfo( self, killCount, deadCount, area ):
		self.killCount = killCount
		self.deadCount = deadCount
		self.area = area
		self.items = [self.playerName, killCount, deadCount, area]

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


# ----------------------------------------------------------------------
# 我军、友军积分榜显示
# ----------------------------------------------------------------------
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from Color import cscolors

class MarkTips( RootGUI ):
	def __init__( self ):
		panel = GUI.load("guis/general/tongabout/citywar/marktips.gui")
		uiFixer.firstLoadFix( panel )
		RootGUI.__init__( self, panel )
		self.v_dockStyle = "TOP"
		self.h_dockStyle = "RIGHT"
		self.posZSegment = ZSegs.L4
		self.focus = False
		self.activable_ = False
		self.escHide_ 		 = False
		self.moveFocus		 = False
		self.hitable_ = False					# 如果为 False，鼠标点击在窗口上时，仍然判断鼠标点击的是屏幕
		self.__pyPoints = {}
		self.__pyItems =[]
		self.__timeCBID = 0
		self.__endTime = 0.0
		self.width = 250.0
		self.__pyStReTime = StaticText( panel.stReTime )
		self.__pyStReTime.text = ""
		self.__pyStReTime.color = cscolors["c3"]
		self.__triggers = {}
		self.__registerTriggers()

	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers["EVT_ON_ENTER_CITYWAR_SPACE"] = self.__onRoleEnterWar #进入战场
		self.__triggers["EVT_ON_UPDATE_CITYWAR_POINTS"] 	= self.__onUpdatePoints #帮会积分
		self.__triggers["EVT_ON_ROLE_LEAVE_CITYWAR_SPACE"] = self.__onRoleLeaveWar #离开战场
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )

	# -----------------------------------------------------------------
	def __onRoleEnterWar( self, warRemainTime, tongInfos ):
		self.visible = warRemainTime > 0
		self.__endTime = warRemainTime + Time.time()
		self.__cancelRemianTimer()
		self.__remainTimeUpdate()
		lTongDBID = tongInfos.get( "left", 0 )
		rTongDBID = tongInfos.get( "right", 0 )
		if lTongDBID > 0 and not self.__pyPoints.has_key( lTongDBID ):
			self.__onUpdatePoints( lTongDBID, 0 )
		if rTongDBID > 0 and not self.__pyPoints.has_key( rTongDBID ):
			self.__onUpdatePoints( rTongDBID, 0 )

	def __remainTimeUpdate( self ):
		remainTime = self.__endTime - Time.time()
		self.__pyStReTime.text = labelGather.getText( "TongAbout:WarIntergral", "remainTime" )%( int( remainTime/60 ), int( remainTime%60 ) )
		if remainTime <= 0.0:
			self.__pyStReTime.text = ""
			self.__cancelRemianTimer()
		self.__timeCBID = BigWorld.callback( 1.0, self.__remainTimeUpdate )

	def __cancelRemianTimer( self ):
		if self.__timeCBID != 0:
			BigWorld.cancelCallback( self.__timeCBID )
			self.__timeCBID = 0
			
	def __checkIsLeague( self, tongDBID1,tongDBID2 ):
		"""
		判断是否是同盟帮会成员
		"""
		player = BigWorld.player()	
		belong1 = player.getCityWarTongBelong( tongDBID1 )
		belong2 = player.getCityWarTongBelong( tongDBID2 )
		return belong1 == belong2

	def __onUpdatePoints( self, tongDBID, point ):
		player = BigWorld.player()
		pTongDBID = player.tong_dbID
		lTongDBID = player.tongInfos.get( "left", 0 )
		rTongDBID = player.tongInfos.get( "right", 0 )
		dTongDBID = 0
		if player.tongInfos.has_key("defend"):
			dTongDBID = player.tongInfos.get("defend")
		markTip = ""
		tongName = ""
		if tongDBID <= 0 and rTongDBID <= 0:return	#righttong的dbid可能为0
		if dTongDBID != 0 and dTongDBID == tongDBID:return	#不显示防守方积分
		if lTongDBID == tongDBID:
			tongName = player.tongInfos["leftTongName"]
		if rTongDBID == tongDBID:
			tongName = player.tongInfos["rightTongName"]
		if dTongDBID > 0:
			if tongDBID == pTongDBID:
				foreColor = cscolors["c4"]
				tongName = player.tongName
			else:
				if pTongDBID == dTongDBID:
					foreColor = cscolors["c8"]
				else:
					foreColor = cscolors["c3"]
		else:
			if self.__checkIsLeague( tongDBID, pTongDBID ):
				foreColor = cscolors["c4"]
			else:
				foreColor = cscolors["c8"]
		if tongName == "":return
		pointText = labelGather.getText( "TongAbout:WarIntergral", "otherMark" )%( tongName, point )
		markTip = PL_Font.getSource( pointText, fc = foreColor )
			
		if self.__pyPoints.has_key( tongDBID ):
				self.__pyPoints[tongDBID].point = point
				self.__pyPoints[tongDBID].text = markTip
		else:
			pyPoint = CSRichText()
			pyPoint.opGBLink = True
			pyPoint.text = markTip
			pyPoint.point = point
			self.addPyChild( pyPoint )
			self.__pyPoints[tongDBID] = pyPoint
			if len( self.__pyItems ) > 0:
				pyPoint.top = self.__pyItems[-1].bottom
			else:
				pyPoint.top = self.__pyStReTime.bottom + 3.0
			self.__pyItems.append( pyPoint )
			self.height = self.__pyItems[-1].bottom
		self.__layoutItems()
		
	def __layoutItems( self, startIndex = 0 ):
		"""
		按积分排序
		"""
		offset = self.__pyStReTime.bottom + 3.0
		itemCount = len( self.__pyItems )
		if itemCount == 0 : return
		self.__pyItems.sort( key = lambda pyPoint: pyPoint.point, reverse = True )
		pyPoint = self.__pyItems[startIndex]
		pyPoint.left = 0
		if startIndex == 0 :
			pyPoint.top = offset
		else :
			pyPoint.top = self.__pyItems[startIndex - 1].bottom + offset
		for pyNextPoint in self.__pyItems[( startIndex + 1 ):] :
			pyNextPoint.left = 0
			pyNextPoint.top = pyPoint.bottom
			pyPoint = pyNextPoint
			
	def __onRoleLeaveWar( self, role ):
		self.__onLeaveWorld()

	def __onLeaveWorld( self ):
		for pyPoint in self.__pyPoints.values():
			self.delPyChild( pyPoint )
		self.__pyPoints = {}
		self.__pyItems =[]
		self.__pyStReTime.text = ""
		self.visible = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.__onLeaveWorld()
		self.hide()