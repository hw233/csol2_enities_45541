# -*- coding: gb18030 -*-
#

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
import csdefine

CAMP_MAPS = { csdefine.ENTITY_CAMP_NONE: "",
				csdefine.ENTITY_CAMP_TAOISM: labelGather.getText( "CampFHLTRankWnd:campFHLTRankWnd", "tCamp" ),
				csdefine.ENTITY_CAMP_DEMON: labelGather.getText( "CampFHLTRankWnd:campFHLTRankWnd", "mCamp" )
			}

class CampFHLTRankWnd( Window ):
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
		self.__campInfos = {}				#阵营名称
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
		
		self.__pyRtLeftName = CSRichText( wnd.rstPanel.rtLeftName )	#自己阵营
		self.__pyRtLeftName.aglin = "C"
		self.__pyRtLeftName.text = ""
		
		self.__pyRtRightName = CSRichText( wnd.rstPanel.rtRightName )	#对方阵营
		self.__pyRtRightName.aglin = "C"
		self.__pyRtRightName.text = ""

		self.__pyRtLeftInter = CSRichText( wnd.rstPanel.rtLeftInter )		#自己阵营积分
		self.__pyRtLeftInter.aglin = "C"
		self.__pyRtLeftInter.text = ""
		
		self.__pyRtRightInter = CSRichText( wnd.rstPanel.rtRightInter )		#对方阵营积分
		self.__pyRtRightInter.aglin = "C"
		self.__pyRtRightInter.text = ""
		
		self.__pyRstPanel = PyGUI( wnd.rstPanel )
		
		self.__pyLbLeft = StaticLabel( wnd.rstPanel.lbLeft )				#自己阵营胜负状态
		self.__pyLbLeft.text = ""
		self.__pyLbLeft.autoSize = True
		self.__pyLbLeft.limning = Font.LIMN_NONE
		self.__pyLbLeft.visible = False
		
		self.__pyLbRight = StaticLabel( wnd.rstPanel.lbRight )				#对方阵营胜负状态
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
		self.__pyRtRival.autoNewline = False
		self.__pyRtRival.text = ""		
		
		self.__pyRtInteral = CSRichText( wnd.infoPanel.rtInteral )			#即时积分
		self.__pyRtInteral.align = "R"
		self.__pyRtInteral.autoNewline = False
		self.__pyRtInteral.text = ""
		
		self.__pyRtTime = CSRichText( wnd.infoPanel.rtTime )				#剩余时间
		self.__pyRtTime.align = "R"
		self.__pyRtTime.autoNewline = False
		self.__pyRtTime.text = ""	
		
		labelGather.setLabel( wnd.lbTitle, "TongAbout:FHLTRankWnd", "lbTitle" )
		labelGather.setLabel( wnd.rstPanel.title.stTitle, "TongAbout:FHLTRankWnd", "result" )
	
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_CAMP_FHLTRANK_WND"] = self.__onShowWnd
		self.__triggers["EVT_ON_ENTER_CAMP_FHLT_SPACE"] = self.__onEnterSpace
		self.__triggers["EVT_ON_RECIEVE_CAMP_FHLTRANK_DATAS"] = self.__onRecieveDatas
		self.__triggers["EVT_ON_UPDATE_CAMP_FHLT_POINT"] = self.__onUpdatePoint
		self.__triggers["EVT_ON_CAMP_FHLT_SPACE_OVER"] = self.__onSpaceOver
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
	
	def __onEnterSpace( self, entity, warEndTime, campInfos):
		"""
		进入副本回调
		"""
		player = BigWorld.player()
		pCamp = player.getCamp()		
		lCamp = campInfos[ "left" ]
		rCamp = campInfos[ "right" ]
		rvalName = ""
		if pCamp != lCamp:	
			rvalName = CAMP_MAPS.get( lCamp, "" )		
		if pCamp != rCamp:
			rvalName = CAMP_MAPS.get( rCamp, "" )					
		self.__pyRtRival.text = labelGather.getText( "TongAbout:FHLTRankWnd", "rvalName" )%rvalName
		self.__campInfos[lCamp] = CAMP_MAPS.get( lCamp, "" )	
		self.__campInfos[rCamp] = CAMP_MAPS.get( rCamp, "" )	
		self.__endTime = warEndTime
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
	
	def __onRecieveDatas( self, camp, playerName, kill, dead, isInWar ):
		"""
		接收积分数据
		"""
		player = BigWorld.player()
		pyAllPanel = self.__pyTabCtrl.pyPages[0].pyPanel
		pyOwnPanel = self.__pyTabCtrl.pyPages[1].pyPanel
		pyEnemyPanel = self.__pyTabCtrl.pyPages[2].pyPanel
		pCamp = player.getCamp()
		area = labelGather.getText( "TongAbout:WarIntergral", "out" )
		if isInWar:
			area = labelGather.getText( "TongAbout:WarIntergral", "inArea" )
			if camp in self.__ranks:
				ranks = self.__ranks[camp]
				if playerName in [info.playerName for info in ranks]:
					for rankInfo in ranks:
						if rankInfo.playerName == playerName:
							rankInfo.updateInfo( kill, dead, area )
					if camp == pCamp:
						pyOwnPanel.updateRank( camp, playerName, kill, dead, area )
					else:
						pyEnemyPanel.updateRank( camp, playerName, kill, dead, area )
				else:
					rankInfo = RankInfo( camp, playerName, kill, dead, area )
					self.__ranks[camp].append( rankInfo )
					if camp == pCamp:
						pyOwnPanel.initRank( rankInfo )
					else:
						pyEnemyPanel.initRank( rankInfo )
			else:
				rankInfo = RankInfo( camp, playerName, kill, dead, area )
				self.__ranks[camp] = [rankInfo]
				if camp == pCamp:
					pyOwnPanel.initRank( rankInfo )
				else:
					pyEnemyPanel.initRank( rankInfo )
			if self.__isInAllRanks( camp, playerName ):										#全部
				pyAllPanel.updateRank( camp, playerName, kill, dead, area )
			else:
				rankInfo = RankInfo( camp, playerName, kill, dead, area )
				pyAllPanel.initRank( rankInfo )
		else:																				# 离开副本
			if camp in self.__ranks:
				ranks = self.__ranks[camp]
				for rank in ranks:
					if rank.playerName == playerName:
						ranks.remove( rank )
				if camp == pCamp:
					pyOwnPanel.delRank( playerName )
				else:
					pyEnemyPanel.delRank( playerName )
				pyAllPanel.delRank( playerName )
	
	def __onUpdatePoint( self, camp, point ):
		"""
		更新即时积分
		"""
		player = BigWorld.player()
		interText = ""
		if camp == player.getCamp():
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
		pCamp = player.getCamp()
		self.__pyRtLeftName.text = self.__campInfos.get( pCamp, "" )
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

	def __isInAllRanks( self, camp, playerName ):
		pyAllPanel = self.__pyTabCtrl.pyPages[0].pyPanel
		rankItems = pyAllPanel.getRankItems()
		for rankItem in rankItems:
			if rankItem.camp == camp and \
			rankItem.playerName == playerName:
				return True
		return False
	
	def __cancelCountdown( self ):
		if self.__cdcbid > 0:
			BigWorld.cancelCallback( self.__cdcbid )
			self.__cdcbid = 0
	
	def __getEnemyName( self ):
		"""
		获取敌方阵营名称
		"""
		enemyName = ""
		pCamp = BigWorld.player().getCamp()
		for camp, campName in self.__campInfos.items():
			if pCamp != camp:
				enemyName = campName
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
		self.__campInfos = {}				#阵营名称
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

	def updateRank( self, camp, playerName, kill, dead, area ):
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
		pCamp = player.getCamp()
		camp = listItem.camp
		foreColor = cscolors["c1"]
		texturePath = ""
		iconMapping = (1, 1)
			
		if camp == pCamp:
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
	def __init__( self, camp = 0, playerName = "",  kill = 0, dead = 0, area = "" ):
		self.camp = camp
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

# -----------------------------------------------------------------------
from guis.common.RootGUI import RootGUI
from AbstractTemplates import Singleton

class CFHLTTips( RootGUI, Singleton ):
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
		self.__campInfos = {}
	
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
		self.__campInfos = {}
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
	
	def __getInfoColor( self, camp ):
		"""
		获取颜色
		"""
		player = BigWorld.player()
		pCamp = player.getCamp()		
		if camp == pCamp:
			foreColor = cscolors["c4"]
		else:
			foreColor = cscolors["c8"]
		return foreColor

	@classmethod
	def __onEnterSpace( SELF, entity, endTime, campInfos ):
		self = SELF.inst
		player = BigWorld.player()
		pCamp = player.getCamp()
		lCamp = campInfos["left"]
		lCampName = CAMP_MAPS[lCamp]
		rCamp = campInfos["right"]
		rCampName = CAMP_MAPS[rCamp]
		
		self.__campInfos[lCamp] = lCampName
		self.__campInfos[rCamp] = rCampName
		for camp, campName in self.__campInfos.items():
			item = GUI.load( "guis/general/tongabout/tongfhlt/infoitem.gui" )
			uiFixer.firstLoadFix( item )
			pyInfoItem = InfoItem( item, camp, campName )
			color = self.__getInfoColor( camp )
			
			pyInfoItem.setForeColor( color )
			self.__pyItemsPanel.addItem( pyInfoItem )
		self.__endTime = endTime
		self.__cancelCountdown()
		self.__cdcbid = BigWorld.callback( 0, self.__remainCountdown )
		self.show()
		
	@classmethod
	def __onUpdatePoint( SELF, camp, point ):
		"""
		更新积分
		"""
		self = SELF.inst
		for pyItem in self.__pyItemsPanel.pyItems:
			if pyItem.camp == camp:
				pyItem.updateInteral( point )
		self.__pyItemsPanel.sort( key = lambda pyItem: pyItem.interal, reverse = True )
		
	@classmethod
	def __onLeaveSpace( SELF ):
		"""
		离开副本
		"""
		self = SELF.inst
		self.__campInfos = {}
		self.__pyItemsPanel.clearItems()
		self.hide()
		
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_ENTER_CAMP_FHLT_SPACE"] = SELF.__onEnterSpace
		SELF.__triggers["EVT_ON_UPDATE_CAMP_FHLT_POINT"] = SELF.__onUpdatePoint
		SELF.__triggers["EVT_ON_LEAVE_CAMP_FHLT_SPACE"] = SELF.__onLeaveSpace
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[evtMacro]( *args )

class InfoItem( PyGUI ):
	def __init__( self, item, camp, name ):
		PyGUI.__init__( self, item )
		self.__pyRtName = CSRichText( item.rtName )
		self.__pyRtName.text = name
		
		self.__pyRtInteral = CSRichText( item.rtInteral )
		self.__pyRtInteral.text = ""

		self.camp = camp
		self.interal = 0
		self.updateInteral( self.interal )
	
	def updateInteral( self, interal ):
		self.interal = interal
		self.__pyRtInteral.text = "%02d"%interal
	
	def setForeColor( self, color ):
		self.__pyRtName.foreColor = color
		self.__pyRtInteral.foreColor = color

CFHLTTips.registerTriggers()