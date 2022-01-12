# -*- coding: gb18030 -*-
#
from guis import *
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODListPanel import ODListPanel
from LabelGather import labelGather
import csconst
import csstatus
from guis.controls.TabCtrl import TabPanel

class SearchMaster( TabPanel ):
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )	
		self.__initialize( panel )
		
		self.__sortByName = False
		self.__sortByLevel = False
		self.__sortByPro = False
		self.__sortByTitle = False
		self.__sortByNum = False
		self.__sortByTime = False
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		self.__pyListPanel = ODListPanel( panel.infoPanel, panel.scrollBar )
		self.__pyListPanel.onViewItemInitialized.bind( self.__initItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.itemHeight = 23

		self.__pyNameBar = HButtonEx( panel.btnPlayerName )
		self.__pyNameBar.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyNameBar.isSort = True
		self.__pyNameBar.onLClick.bind( self.__onSortByName ) # 按名称排序

		self.__pyLevelBar = HButtonEx( panel.btnPlayerLevel )
		self.__pyLevelBar.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyLevelBar.isSort = True
		self.__pyLevelBar.onLClick.bind( self.__onSortByLevel ) # 按等级排序

		self.__pyProBar = HButtonEx( panel.btnPlayerPro )
		self.__pyProBar.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyProBar.isSort = True
		self.__pyProBar.onLClick.bind( self.__onSortByPro ) # 按职业排序

		self.__pyTitleBar = HButtonEx( panel.btnPlayerTitle )
		self.__pyTitleBar.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyTitleBar.isSort = True
		self.__pyTitleBar.onLClick.bind( self.__onSortByTitle ) # 按称号排序

		self.__pyPrenticedNumBar = HButtonEx( panel.btnPrenNum )
		self.__pyPrenticedNumBar.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyPrenticedNumBar.isSort = True
		self.__pyPrenticedNumBar.onLClick.bind( self.__onSortByPrenticedNum ) # 按徒弟数量排序	#改为已出师的弟子数量
		
		self.__pyLwOnlineTimeBar = HButtonEx( panel.btnLwOnline )
		self.__pyLwOnlineTimeBar.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyLwOnlineTimeBar.isSort = True
		self.__pyLwOnlineTimeBar.onLClick.bind( self.__onSortByLwOnlineTime ) # 按上周在线时长排序

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyPrenticedNumBar, "SearchTeachWindow:searchMaster", "bar_prenticednum" )
		labelGather.setPyBgLabel( self.__pyTitleBar, "SearchTeachWindow:searchMaster", "bar_mastertitle" )
		labelGather.setPyBgLabel( self.__pyProBar, "SearchTeachWindow:searchMaster", "bar_masterpro" )
		labelGather.setPyBgLabel( self.__pyLevelBar, "SearchTeachWindow:searchMaster", "bar_masterlevel" )
		labelGather.setPyBgLabel( self.__pyNameBar, "SearchTeachWindow:searchMaster", "bar_mastername" )
		labelGather.setPyBgLabel( self.__pyLwOnlineTimeBar, "SearchTeachWindow:searchMaster", "bar_onlineTime" )

	# -------------------------------------------------			
	def __initItem( self, pyViewItem ) :
		pyMaster = MasterInfo( pyViewItem )
		pyViewItem.pyPTItem = pyMaster
		pyViewItem.addPyChild( pyMaster )
		pyMaster.pos = 0, 2
		
	def __drawItem( self, pyViewItem ) :
		pyMaster = pyViewItem.pyPTItem
		masterInfo = pyViewItem.listItem
		pyMaster.update( masterInfo )
		pyMaster.selected = pyViewItem.selected
		
	# -------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onClickCloseBtn( self ):
		"""
		"""
		self.hide()

	def __onSortByName( self ):
		"""
		按名称排序
		"""
		flag = self.__sortByName
		self.__pyListPanel.sort( key = lambda item: item[1], reverse = flag )
		self.__sortByName = not self.__sortByName

	def __onSortByLevel( self ):
		"""
		按等级排序
		"""
		flag = self.__sortByLevel
		self.__pyListPanel.sort( key = lambda item: item[2], reverse = flag )
		self.__sortByLevel = not self.__sortByLevel

	def __onSortByPro( self ):
		"""
		按职业排序
		"""
		flag = self.__sortByPro
		self.__pyListPanel.sort( key = lambda item: item[3], reverse = flag )
		self.__sortByPro = not self.__sortByPro

	def __onSortByTitle( self ):
		"""
		按称号排序
		"""
		flag = self.__sortByTitle
		self.__pyListPanel.sort( key = lambda item: item[4], reverse = flag )
		self.__sortByTitle = not self.__sortByTitle

	def __onSortByPrenticedNum( self ):
		"""
		按徒弟数量排序
		"""
		flag = self.__sortByNum
		self.__pyListPanel.sort( key = lambda item: item[5], reverse = flag )
		self.__sortByNum = not self.__sortByNum
		
	def __onSortByLwOnlineTime( self ):
		"""
		按上周在线时长排序
		"""
		flag = self.__sortByTime
		self.__pyListPanel.sort( key = lambda item: item[7], reverse = flag )
		self.__sortByTime = not self.__sortByTime

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def requestPlayerInfo( self ):
		"""
		刷新界面，重新查询数据
		"""
		self.__pyListPanel.clearItems()
		BigWorld.player().teach_queryTeachInfo()

	def requestBePrentice( self ) :
		"""
		请求拜师
		"""
		player = BigWorld.player()
		if csconst.TEACH_PRENTICE_UPPER_LIMIT < player.level:
			player.statusMessage( csstatus.TEACH_PRENTICE_ABOVE_LEVEL )
			return
		selectedItem = self.__pyListPanel.selItem
		if selectedItem is not None:
			player.teach_requestTeach( selectedItem[0] )
			
	def onAddMasterInfo( self, master ):
		"""
		添加师傅信息
		@param		master	:	师傅列表信息
		@type		master	:	list
		"""
		for itemInfo in self.__pyListPanel.items:
			if itemInfo[0] == master[0]:
				return
		self.__pyListPanel.addItem( master )
		
	def clearItems( self ):
		"""
		"""
		self.__pyListPanel.clearItems()


#--------------------------------------------------------
from guis.controls.ListItem import MultiColListItem
from TitleMgr import TitleMgr
import csconst
import csdefine
titleIns = TitleMgr.instance()
class MasterInfo( MultiColListItem ):

	def __init__( self, pyBinder = None ) :
		item = GUI.load( "guis/general/searchteachwindow/masteritem.gui" )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item, pyBinder )
		self.focus = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	
	def update( self, master ):
		"""
		更新师傅信息
		@param		pyViewItem	: 师傅信息
		@type		pyViewItem	: MasterInfo类
		"""
		playerNameText = master[1]
		playerLevelText = master[2]
		raceclass = master[3] & csdefine.RCMASK_CLASS
		raceClassText = csconst.g_chs_class[raceclass]
		masterTitle = master[4]
		titleNameText = titleIns.getName( masterTitle )
		if titleNameText == "" :
			titleNameText = labelGather.getText( "SearchTeachWindow:searchMaster", "miNone" )
		prenticeNumText  = labelGather.getText( "SearchTeachWindow:searchMaster", "preNum", master[5] )
		onlineTimeText = self.__getTimeStr( master[7] )
		self.setTextes( playerNameText, playerLevelText, raceClassText, titleNameText, prenticeNumText, onlineTimeText )
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getTimeStr( self, seconds ):
		timeStr = ""
		totalSeconds = int( seconds )
		hours = totalSeconds/3600
		restSeconds = totalSeconds%3600
		minutes = restSeconds/360
		if hours <= 0:
			timeStr = labelGather.getText( "SearchTeachWindow:searchPrentice","st_onlineTime2", minutes )
		else:
			if minutes >= 30:
				hours = hours + 1  # 四舍五入
			timeStr = labelGather.getText( "SearchTeachWindow:searchPrentice","st_onlineTime", hours )
		return timeStr