# -*- coding: gb18030 -*-
#
# $Id: QuestHelp.py,v 1.5 2008-08-26 02:18:23 huangyongwei Exp $

"""
implement quest list class
"""

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from QuestList import QuestList
from QuestCacept import QuestCacept
from QuestQuery import QuestQuery
import GUIFacade
import Font

class QuestHelp( Window ):
	titles_map = {	0: labelGather.getText( "QuestHelp:main", "btn_0" ),
			1: labelGather.getText( "QuestHelp:main", "btn_1" ),
			2: labelGather.getText( "QuestHelp:main", "btn_2" )
	}
	def __init__( self, guiPath = None ):
		wnd = GUI.load( "guis/general/questlist/window.gui" )
		if guiPath:
			wnd = GUI.load( guiPath )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True

		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ):
		self.__pyStTitle = StaticText( wnd.lbTitle )
		self.__pyStTitle.text = ""
		self.__pyStTitle.charSpace = 2

		self.__pyTabCtr = TabCtrl( wnd.tc )

		self.__pyListPanel = QuestList( wnd.tc.panel_0, self ) # 任务日志面板
		self.__pyQuestBtn = TabButton( wnd.tc.btn_0 )
		self.__pyQuestBtn.commonForeColor = ( 252, 235, 179, 255 )
		self.__pyQuestBtn.selectedForeColor = ( 252, 235, 179, 255 )
		labelGather.setPyBgLabel( self.__pyQuestBtn, "QuestHelp:main", "btn_0" )
		self.__pyQuestBtn.limning = Font.LIMN_OUT
		self.__pyQuestBtn.foreColor = ( 231, 205, 140, 255 )
		self.__pyTabCtr.addPage( TabPage( self.__pyQuestBtn, self.__pyListPanel ) )

		self.__pyCacceptPanel = QuestCacept( wnd.tc.panel_1, self )
		self.__pyCaceptBtn = TabButton( wnd.tc.btn_1 )
		self.__pyCaceptBtn.commonForeColor = ( 252, 235, 179, 255 )
		self.__pyCaceptBtn.selectedForeColor = ( 252, 235, 179, 255 )
		labelGather.setPyBgLabel( self.__pyCaceptBtn, "QuestHelp:main", "btn_1" )
		self.__pyCaceptBtn.limning = Font.LIMN_OUT
		self.__pyCaceptBtn.foreColor = ( 231, 205, 140, 255 )
		self.__pyTabCtr.addPage( TabPage( self.__pyCaceptBtn, self.__pyCacceptPanel ) )

		self.__pyQueryPanel = QuestQuery( wnd.tc.panel_2, self ) # 任务查询面板
		self.__pyQueryBtn = TabButton( wnd.tc.btn_2 )
		self.__pyQueryBtn.commonForeColor = ( 252, 235, 179, 255 )
		self.__pyQueryBtn.selectedForeColor = ( 252, 235, 179, 255 )
		labelGather.setPyBgLabel( self.__pyQueryBtn, "QuestHelp:main", "btn_2" )
		self.__pyQueryBtn.limning = Font.LIMN_OUT
		self.__pyQueryBtn.foreColor = ( 231, 205, 140, 255 )
		self.__pyTabCtr.addPage( TabPage( self.__pyQueryBtn, self.__pyQueryPanel ) )

		self.__pyTabCtr.onTabPageSelectedChanged.bind( self.__onPageSelected )

	# -------------------------------------------------------------------
	# private
	#--------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TOGGLE_QUEST_WINDOW"] = self.__toggleQuestLog #已接任务
		self.__triggers["EVT_ON_HIDE_QUEST_WINDOW"] = self.__hideQuestLog
		self.__triggers["EVT_ON_SHOW_QUEST_WINDOW"] = self.__showQuestLog
		self.__triggers["EVT_ON_TOGGLE_QUESTS_CACCEPT"] = self.__toggleQuestCaccept #可接任务
		self.__triggers["EVT_ON_HIDE_QUESTS_CACCEPT"] = self.__hideQuestCaccept
		self.__triggers["EVT_ON_TOGGLE_QUESTS_QUERY"] = self.__toggleQuestQuery #查询任务
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# -------------------------------------------------------
	def __toggleQuestLog( self ):
		if self.visible and self.__pyTabCtr.pySelPage.index == 0 :
			self.hide()
		else:
			self.show( 0 )

	def __hideQuestLog( self ):
		self.hide()

	def __showQuestLog( self ):
		self.show(0)

	def __toggleQuestCaccept( self ):
		pass

	def __hideQuestCaccept( self ):
		if self.__pyTabCtr.pySelPage.index == 1:
			self.hide()

	def __toggleQuestQuery( self ):
		if self.visible and self.__pyTabCtr.pySelPage.index == 2:
			self.hide()
		else:
			self.show( 1 )

	def __onPageSelected( self, tabCtrl ):
		selIndex = tabCtrl.pySelPage.index
		self.__pyStTitle.text = self.titles_map[selIndex]
		self.__pyStTitle.font = "STLITI.TTF"
		self.__pyStTitle.fontSize = 16.0
		self.__pyStTitle.limning = Font.LIMN_OUT
		self.__pyStTitle.color = ( 231, 205, 140, 255 )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ):
		self.__pyCacceptPanel.initQuests()
		self.__pyListPanel.initConstQuestType()

	def onLeaveWorld( self ):
		self.hide()
		self.__pyListPanel.reset()
		self.__pyQueryPanel.reset()
		self.__pyCacceptPanel.reset()

	def onMove_( self, dx, dy ):
		Window.onMove_( self, dx, dy )
		selIndex = self.__pyTabCtr.pySelPage.index
		if selIndex == 0:
			self.__pyListPanel.onMove( dx, dy )

	def onKeyDown_( self, key, mods ) :
		"""
		"""
		keyEventHandler = getattr( self.__pyTabCtr.pySelPage.pyPanel, "keyEventHandler", None )
		if callable( keyEventHandler ) :
			return keyEventHandler( key, mods )
		return Window.onKeyDown_( self, key, mods )

	def show( self, index ):
		count = self.__pyTabCtr.pageCount
		if index < 0 or index >= count: index = 0
		self.__pyTabCtr.pyPages[index].selected = True
		self.__pyStTitle.text = self.titles_map[index]
		self.__pyStTitle.font = "STLITI.TTF"
		self.__pyStTitle.fontSize = 16.0
		self.__pyStTitle.limning = Font.LIMN_OUT
		self.__pyStTitle.color = ( 231, 205, 140, 255 )
		Window.show( self )
		if index == 0:
			self.__pyListPanel.onShow()
		rds.helper.courseHelper.openWindow( "renwu_chuangkou" )

	def hide( self ):
		Window.hide( self )
		ECenter.fireEvent( "EVT_ON_SHOW_TRACE_OPERATION_TIPS" ) # 显示任务追踪提示帮助
		selIndex = self.__pyTabCtr.pySelPage.index
		if selIndex == 0:
			self.__pyListPanel.onHide()
	
	def reloadGui( self, index ):
		guis = { 0: "window_0", 1:"window_1" }
		gui = guis.get( index, None )
		if gui is None:return
		