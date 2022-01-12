# -*- coding: gb18030 -*-
#
# $Id: SystemWindow.py,v 1.18 2008-08-26 02:19:53 huangyongwei Exp $

"""
implement system setting window
"""

import BigWorld
import GUIFacade
from guis import *
from guis.common.PyGUI import PyGUI
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.ButtonEx import HButtonEx
from guis.controls.SelectableButton import SelectableButton
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ListItem import MultiColListItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from Notifier import Notifier
import event.EventCenter as ECenter
import ActivitySchedule
ActivityInstance = ActivitySchedule.g_activitySchedule
from Time import Time
import time
import Const

REFURBISH_INTERVAL_TIME = 5.0 #刷新间隔时间
LEVEL_FORBID = 3

class ActivityCalendar( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/activitycalendar/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.escHide_ = True
		self.activable_ = True
		self.__triggers = {}
		self.sortByTime = False
		self.sortByName = False
		self.sortByLevel = False
		self.sortByType = False
		self.sortByArea = False
		self.sortByLine = False
		self.notifyCheck = True #是否显示活动提示
		self.notShowTypes = []
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):

		self.__pyBtnTime = HButtonEx( wnd.btnTime )
		self.__pyBtnTime.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnTime.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnTime, "ActivityCalendar:main", "btnTime" )
		self.__pyBtnTime.onLClick.bind( self.__sortByTime ) #活动时间排序

		self.__pyBtnName = HButtonEx( wnd.btnName )
		self.__pyBtnName.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnName.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnName, "ActivityCalendar:main", "btnName" )
		self.__pyBtnName.onLClick.bind( self.__sortByName ) #

		self.__pyBtnLevel = HButtonEx( wnd.btnLevel )
		self.__pyBtnLevel.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnLevel.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnLevel, "ActivityCalendar:main", "btnLevel" )
		self.__pyBtnLevel.onLClick.bind( self.__sortByLevel )

		self.__pyBtnType = HButtonEx( wnd.btnType )
		self.__pyBtnType.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnType.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnType, "ActivityCalendar:main", "btnType" )
		self.__pyBtnType.onLClick.bind( self.__sortByType )

		self.__pyBtnArea = HButtonEx( wnd.btnArea )
		self.__pyBtnArea.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnArea.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnArea, "ActivityCalendar:main", "btnArea" )
		self.__pyBtnArea.onLClick.bind( self.__sortByArea )

		self.__pyBtnLine = HButtonEx( wnd.btnLine )
		self.__pyBtnLine.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnLine.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnLine, "ActivityCalendar:main", "btnLine" )
		self.__pyBtnLine.onLClick.bind( self.__sortByLine )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "ActivityCalendar:main", "lbTitle" )
		labelGather.setLabel( wnd.infoPanel.stTitle, "ActivityCalendar:main", "activeExp")
		labelGather.setLabel( wnd.expPanel.stTitle, "ActivityCalendar:main", "uiExp")
		labelGather.setLabel( wnd.comText, "ActivityCalendar:main", "commend")
		self.__pyDateBtns = SelectorGroup()
		self.__pyStateChecks = {}
		self.__pyStars = {}
		for name, item in wnd.children:
			if name.startswith( "dateBtn_" ):
				index = int( name.split( "_" )[1] )
				pyDateBtn = SelectableButton( item )
				pyDateBtn.setStatesMapping( UIState.MODE_R3C1 )
				pyDateBtn.isOffsetText = True
				pyDateBtn.date = index
				labelGather.setPyLabel( pyDateBtn, "ActivityCalendar:main", name )
				pyDateBtn.commonForeColor = ( 255, 255, 255, 255 )
				pyDateBtn.selectedForeColor = ( 255, 255, 0, 255 )
				self.__pyDateBtns.addSelector( pyDateBtn )
			if name.startswith( "stateCheck_" ):
				index = int( name.split( "_" )[1] )
				pyStateCheck = CheckBoxEx( item )
				pyStateCheck.state = index
				pyStateCheck.checked = False
				labelGather.setLabel( item.stext, "ActivityCalendar:main", name )
				labelGather.setLabel( item.hideText, "ActivityCalendar:main", "dontShow" )
				pyStateCheck.onCheckChanged.bind( self.__onStateCheck )
				self.__pyStateChecks[index] = pyStateCheck
			if name.startswith( "star_" ):
				index = int( name.split( "_" )[1] )
				pyStar = Control( item )
				pyStar.visible = False
				pyStar.crossFocus = True
				pyStar.onMouseEnter.bind( self.__onShowStarDsp )
				pyStar.onMouseLeave.bind( self.__onhideStarDsp )
				self.__pyStars[index] = pyStar
		self.__pyDateBtns.onSelectChanged.bind( self.__onSelectDate )

		self.__pyListPanel = ODListPanel( wnd.listPanel.clipPanel, wnd.listPanel.sbar )
		self.__pyListPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.itemHeight = 23.0
		self.__pyListPanel.autoSelect = True
		self.__pyListPanel.onItemSelectChanged.bind( self.__onItemSlected )

		self.__pyInfoPanel = CSTextPanel( wnd.infoPanel.clipPanel, wnd.infoPanel.sbar )
		self.__pyInfoPanel.opGBLink = True
		self.__pyInfoPanel.foreColor = ( 230, 227, 185, 255 )

		self.__pyBtnToday = HButtonEx( wnd.btnToday )
		self.__pyBtnToday.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnToday.onLClick.bind( self.__onShowToday )
		labelGather.setPyBgLabel( self.__pyBtnToday, "ActivityCalendar:main", "btnToday" )

		self.__pyNotifier = Notifier()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_ACTIVITY_WINDOW"] = self.__onShow
		# 策划要求活动开始时不再显示叹号，考虑到需求的变动是很快的，就只把事件屏蔽了。--pj
		#self.__triggers["EVT_ON_ACTIVITY_SOON_START"] = self.__onAcivityStart
#		self.__triggers["EVT_ON_SHOW_ACTIVITY_WINDOW"] = self.__showActivityWindow
#		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )
	# ------------------------------------------------------------

	def __initListItem( self, pyViewItem ) :
		pyCalendar = CalendarItem()
		pyViewItem.addPyChild( pyCalendar )
		pyViewItem.crossFocus = False
		pyCalendar.pos = -1.0, 1
		pyViewItem.pyItem = pyCalendar

	def __drawListItem( self, pyViewItem ) :
		pyCalendar = pyViewItem.pyItem
		pyCalendar.setCanlendar( pyViewItem )

	def __onShow( self ):
		if self.visible:
			self.hide()
		else:
			self.show()
	
	def __onResolutionChanged( self, preReso ):
		"""
		分辨率改变通知
		"""
		for pyViewItem in self.__pyListPanel.pyViewItems:
			pyCalendar = pyViewItem.pyItem
			uiFixer.fix( preReso, pyCalendar.getGui() )

	def __onAcivityStart( self ):
		if rds.statusMgr.isInWorld() and self.notifyCheck and \
			not self.visible:
			self.__pyNotifier.show()

	def __sortByTime( self ): #按时间排序
		flag = self.sortByTime and True or False
		self.__pyListPanel.sort( key = lambda item: item[0]*60 + item[1], reverse = flag )
		self.sortByTime = not self.sortByTime

	def __sortByName( self ): #按名称排序
		flag = self.sortByName and True or False
		self.__pyListPanel.sort( key = lambda item: item[2], reverse = flag )
		self.sortByName = not self.sortByName

	def __sortByLevel( self ): #按等级排序
		flag = self.sortByLevel and True or False
		self.__pyListPanel.sort( key = lambda item : item[5], reverse = flag )
		self.sortByLevel = not self.sortByLevel

	def __sortByType( self ):
		flag = self.sortByLine and True or False
		self.__pyListPanel.sort( key = lambda item : item[7], reverse = flag )
		self.sortByLine = not self.sortByLine

	def __sortByArea( self ): #按地区排序
		flag = self.sortByArea and True or False
		self.__pyListPanel.sort( key = lambda item : item[6], reverse = flag )
		self.sortByArea = not self.sortByArea

	def __sortByLine( self ):
		flag = self.sortByLine and True or False
		self.__pyListPanel.sort( key = lambda item : item[8], reverse = flag )
		self.sortByLine = not self.sortByLine

	def __freshCalendar( self ): #刷新列表
		self.__pyListPanel.clearItems()
		self.__pyInfoPanel.text = ""
		self.__setCalendarsInfo()
		self.__pyFreshBtn.enable=False
		BigWorld.callback(REFURBISH_INTERVAL_TIME,self.__setRefBtn)

	def __setRefBtn(self):
		self.__pyFreshBtn.enable=True

	def __setCurAction( self ):
		"""
		获取当前活动，如有多个，获取最后一个
		"""
		currActIndex = -1
		for index, calendar in enumerate( self.__pyListPanel.items ) :
			if calendar[-1] == 1:
				currActIndex = index
		self.__pyListPanel.selIndex = currActIndex

	def __onCheckNotify( self, checked ):
		self.notifyCheck = not checked

	def __shutCalendar( self ): #关闭
		self.hide()

	def __onItemSlected( self, index ):
		calendar = self.__pyListPanel.selItem
		if calendar is None:return
		self.__pyInfoPanel.text = calendar != None and calendar[4] or ""
		stars = calendar[9]
		for index, pyStar in self.__pyStars.items():
			pyStar.visible = index < stars

	def __setCalendarsInfo( self, minsDate, actTables ) :
		filterStates = self.__getFilterStates()
		self.__pyListPanel.clearItems()
		filterTables = []
		if minsDate != 0:
			for index, actTable in actTables.items():
				if actTable[-1] in filterStates:continue
				if actTable[5] == "":
					actTable[5] = 1
				if int( actTable[5] ) > BigWorld.player().getLevel() and \
				LEVEL_FORBID in filterStates:continue
				filterTables.append( actTable )
		else:
			levelForbid = LEVEL_FORBID in filterStates
			for state in [0, 1, 2]:
				if state in filterStates:
					continue
				if not levelForbid:
					filterTables += ActivityInstance.getActivityStateInfo( state )
				else:
					filterTables += self.__getLevelForbids( state )
		self.__pyListPanel.addItems( filterTables )
		self.__pyListPanel.sort( key = lambda item : item[0]*60 + item[1], reverse = False )

	def __onSelectDate( self, pyDateBtn ):
		if pyDateBtn is None:return
		date = pyDateBtn.date
		curDate = Time.localtime()[6]
		minsDate = date - curDate
		actTables = ActivityInstance.getDayActivityTable( minsDate )
		self.__setCalendarsInfo( minsDate, actTables )

	def __getFilterStates( self ):
		filterStates = []
		for pyChecker in self.__pyStateChecks.values():
			if pyChecker.checked:
				filterStates.append( pyChecker.state )
		return filterStates

	def __onStateCheck( self, checked ):
		pyDateBtn = self.__pyDateBtns.pyCurrSelector
		date = pyDateBtn.date
		curDate = Time.localtime()[6]
		minsDate = date - curDate
		actTables = ActivityInstance.getDayActivityTable( minsDate )
		self.__setCalendarsInfo( minsDate, actTables )

	def __setFilterCalendar( self, checked, state ):
		curDate = Time.localtime()[6]
		minsDate = date - curDate
		actTables = ActivityInstance.getDayActivityTable( minsDate )

	def __onShowToday( self ):
		curDate = Time.localtime()[6]
		for pyDateBtn in self.__pyDateBtns.pySelectors:
			if pyDateBtn.date == curDate:
				self.__pyDateBtns.pyCurrSelector = pyDateBtn
				break
		self.__setCurAction()

	def __getLevelForbids( self, state ):
		filterTables = []
		actTables = ActivityInstance.getActivityStateInfo( state )
		for actTable in actTables:
			if int( actTable[5] ) > BigWorld.player().getLevel():
				continue
			filterTables.append( actTable )
		return filterTables

	def __onShowStarDsp( self, pyStar ):
		if not pyStar.visible:return
		dsp = labelGather.getText( "ActivityCalendar:main", "starDsp" )
		toolbox.infoTip.showToolTips( self, dsp )

	def __onhideStarDsp( self ):
		toolbox.infoTip.hide()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.notifyCheck = True
		self.hide()

	def show( self ):
		curDate = Time.localtime()[6]
		for pyDateBtn in self.__pyDateBtns.pySelectors:
			if pyDateBtn.date == curDate:
				self.__pyDateBtns.pyCurrSelector = pyDateBtn
				break
		self.__setCurAction()
		Window.show( self )

	def hide( self ):
#		self.__pyListPanel.clearItems()
		self.__pyInfoPanel.text = ""
#		self.__pyDateBtns.pyCurrSelector = None
		Window.hide( self )


# --------------------------------------------------------
class CalendarItem( MultiColListItem ):

	_ITEM = None
	_STATECOLOR = { 0 : ( 232, 100, 27, 255 ),
					1 : ( 54, 210, 4, 255 ),
					2 : ( 152, 152, 152, 255 ),
				}

	def __init__( self ):
		if CalendarItem._ITEM is None :
			CalendarItem._ITEM = GUI.load( "guis/general/activitycalendar/calendarbar.gui" )
		item = util.copyGuiTree( CalendarItem._ITEM )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.focus = False

	def setCanlendar( self, pyViewItem ):
		"""
		更新活动
		"""
		# 设置外观显示
		canlendar = pyViewItem.listItem
		self.foreColor = Const._ACT_STATECOLOR[ canlendar[-1] ]
		self.selected = pyViewItem.selected
		if pyViewItem.selected :
			self.setState( UIState.SELECTED )
		elif self.isMouseHit() :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
		levelText = canlendar[5]
		level = 0
		if levelText != "":
			level = int( levelText )
		nameColor = self.foreColor
		if BigWorld.player().getLevel() < level:
			nameColor = ( 255, 0, 0, 255 )
		self.pyCols[2].foreColor = nameColor
		# 设置文字
		activityTimeStr = "%d:%.2d"%( canlendar[0], canlendar[1] )
		duration = canlendar[10]
		if duration > 0:
			mins = duration + canlendar[1]
			if mins >= 60:
				hours = mins/60
				mins = mins%60
				hours += canlendar[0]
				if hours > 24:
					hours = hours%24
				activityTimeStr += "--%d:%.2d"%( hours, mins )
			else:
				activityTimeStr += "--%d:%.2d"%( canlendar[0], mins )
		expFightStr = labelGather.getText( "ActivityCalendar:cldItem", "expFight" )
		potFightStr = labelGather.getText( "ActivityCalendar:cldItem", "potFight" )
		if canlendar[2] == expFightStr or canlendar[2] == potFightStr :
			activityTimeStr = labelGather.getText( "ActivityCalendar:cldItem", "daylong" )
		self.setTextes( activityTimeStr,
						canlendar[2],
						labelGather.getText( "ActivityCalendar:cldItem", "needLevel" )%levelText,
						canlendar[7],
						canlendar[6],
						canlendar[8]
						)

	def onStateChanged_( self, state ) :
		"""
		状态改变时调用
		"""
		elements = self.getGui().elements
		for element in elements.values():
			element.visible = state in [ UIState.HIGHLIGHT, UIState.SELECTED ]
