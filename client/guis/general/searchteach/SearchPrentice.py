# -*- coding: gb18030 -*-

# written by ganjinxing 2010-06-05

from guis import *
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.ODListPanel import ODListPanel
from LabelGather import labelGather
import csconst
import csstatus
import csdefine
import time
from guis.controls.TabCtrl import TabPanel

class SearchPrentice( TabPanel ) :

	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__initialize( panel )
		
		self.__nameTaxisFlag = False
		self.__levelTaxisFlag = False
		self.__jobTaxisFlag = False
		self.__onlineTimeTaxisFlag = False
		self.__publishTimeTaxisFlag = False

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		self.__pyListPanel = ODListPanel( panel.infoPanel, panel.scrollBar )			# 徒弟列表
		self.__pyListPanel.onViewItemInitialized.bind( self.__initItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.itemHeight = 23
		
		self.__pyNameBtn = HButtonEx( panel.btnPlayerName )
		self.__pyNameBtn.setExStatesMapping(UIState.MODE_R4C1)
		self.__pyNameBtn.onLClick.bind(self.__onSortByName)
		
		self.__pyLevelBtn = HButtonEx( panel.btnPlayerLevel )
		self.__pyLevelBtn.setExStatesMapping(UIState.MODE_R4C1)
		self.__pyLevelBtn.onLClick.bind(self.__onSortByLevel)
		
		self.__pyJobBtn = HButtonEx( panel.btnPlayerPro )
		self.__pyJobBtn.setExStatesMapping(UIState.MODE_R4C1)
		self.__pyJobBtn.onLClick.bind(self.__onSortByJob)
		
		self.__pyOnlineTimeBtn = HButtonEx( panel.btnLwOnline )
		self.__pyOnlineTimeBtn.setExStatesMapping(UIState.MODE_R4C1 )
		self.__pyOnlineTimeBtn.onLClick.bind(self.__onSortByOnlineTime )
		
		self.__pyPublishTimeBtn = HButtonEx( panel.btnPublishTime )
		self.__pyPublishTimeBtn.setExStatesMapping(UIState.MODE_R4C1 )
		self.__pyPublishTimeBtn.onLClick.bind(self.__onSortByPublishTime )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyNameBtn, "SearchTeachWindow:searchPrentice", "bar_prenticename" )
		labelGather.setPyBgLabel( self.__pyLevelBtn, "SearchTeachWindow:searchPrentice", "bar_prenticelevel" )
		labelGather.setPyBgLabel( self.__pyJobBtn, "SearchTeachWindow:searchPrentice", "bar_prenticePro" )
		labelGather.setPyBgLabel( self.__pyOnlineTimeBtn, "SearchTeachWindow:searchPrentice", "bar_onlineTime" )
		labelGather.setPyBgLabel( self.__pyPublishTimeBtn, "SearchTeachWindow:searchPrentice", "bar_publishTime" )

	# -------------------------------------------------
	# view draw
	# -------------------------------------------------
	def __initItem( self, pyViewItem ) :
		pyPrentice = PrenticeItem( pyViewItem )
		pyViewItem.pyPTItem = pyPrentice
		pyViewItem.addPyChild( pyPrentice )
		pyPrentice.pos = 0, 1

	def __drawItem( self, pyViewItem ) :
		pyPrentice = pyViewItem.pyPTItem
		prenticeInfo = pyViewItem.listItem
		pyPrentice.update( prenticeInfo )
		pyPrentice.selected = pyViewItem.selected

	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __onSortByName( self ) :
		"""
		按名称排序
		"""
		sortFunc = lambda item : item[1]
		self.__nameTaxisFlag = not self.__nameTaxisFlag
		self.__pyListPanel.sort( key = sortFunc, reverse = self.__nameTaxisFlag )
		
	def __onSortByLevel( self ) :
		"""
		按等级排序
		"""
		sortFunc = lambda item : item[2]
		self.__levelTaxisFlag = not self.__levelTaxisFlag
		self.__pyListPanel.sort( key = sortFunc, reverse = self.__levelTaxisFlag )
		
	def __onSortByJob( self ) :
		"""
		按职业排序
		"""
		sortFunc = lambda item : item[3]
		self.__jobTaxisFlag = not self.__jobTaxisFlag
		self.__pyListPanel.sort( key = sortFunc, reverse = self.__jobTaxisFlag )
		
	def __onSortByOnlineTime( self ) :
		"""
		按上周在线时长排序
		"""
		sortFunc = lambda item : item[5]
		self.__onlineTimeTaxisFlag = not self.__onlineTimeTaxisFlag
		self.__pyListPanel.sort( key = sortFunc, reverse = self.__onlineTimeTaxisFlag )
		
	def __onSortByPublishTime( self ) :
		"""
		按发布时间排序
		"""
		sortFunc = lambda item : item[6]
		self.__publishTimeTaxisFlag = not self.__publishTimeTaxisFlag
		self.__pyListPanel.sort( key = sortFunc, reverse = self.__publishTimeTaxisFlag )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def requestPlayerInfo( self ):
		"""
		刷新界面，重新查询数据
		"""
		self.__pyListPanel.clearItems()
		BigWorld.player().teach_queryTeachInfo()

	def requestBeMaster( self ) :
		"""
		请求收徒
		"""
		player = BigWorld.player()
		if csconst.TEACH_MASTER_MIN_LEVEL > player.level:
			player.statusMessage( csstatus.TEACH_MASTER_BELOW_LEVEL )
			return
		selectedItem = self.__pyListPanel.selItem
		if selectedItem is not None:
			player.teach_requestTeach( selectedItem[0] )
			
	def onAddPrenticeInfo( self, master ):
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

from guis.controls.ListItem import MultiColListItem
class PrenticeItem( MultiColListItem ) :

	def __init__( self, pyBinder = None ) :
		item = GUI.load( "guis/general/searchteachwindow/prenticeitem.gui" )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item, pyBinder )
		self.focus = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, prentice ) :
		"""
		更新徒弟信息
		@param		pyViewItem	: 徒弟信息
		@type		pyViewItem	: PrenticeItem类
		"""
		playerNameText = prentice[1]
		playerLevelText = prentice[2]
		race = prentice[3] & csdefine.RCMASK_CLASS
		playerProText = csconst.g_chs_class[race]
		onlineTimeText = self.__getTimeStr( prentice[7] )
		timeList = time.localtime( prentice[8] )
		publishTimeText = \
		labelGather.getText( "SearchTeachWindow:searchPrentice", "st_publishTime", timeList[1], timeList[2] )
		self.setTextes( playerNameText, playerLevelText, playerProText, onlineTimeText, publishTimeText )


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
