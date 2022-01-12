# -*- coding: gb18030 -*-
#
# $Id: RelationWindow.py,v 1.23 2008-08-26 02:18:45 huangyongwei Exp $

"""
implement SocialityPanel class
"""

from guis import *
import BigWorld
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.general.relationship.tong.TongPanel import TongPanel
from guis.general.relationship.relationship.RelationPanel import RelationPanel
from guis.general.relationship.athletics.AthlePanel import AthlePanel 
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csdefine

class RelationWindow( Window ):

	RELATION_NAMES = { 0: labelGather.getText( "RelationShip:main", "btn_0" ),
			1: labelGather.getText( "RelationShip:main", "btn_1" ),
			2: labelGather.getText( "RelationShip:main", "btn_2" ),
			}

	def __init__( self ):
		wnd = GUI.load( "guis/general/relationwindow/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4			# in uidefine.py
		self.activable_ = True				# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = True
		self.isAthleReady = False

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyLbTitle = StaticText( wnd.lbTitle )
		self.__pyLbTitle.text = ""
		self.__pyLbTitle.charSpace = 2

		self.__pyTabCtr = TabCtrl( wnd.tc )
		self.__pyTabCtr.onTabPageSelectedChanged.bind( self.__onPageSelected )

		self.__pyRelationPanel = RelationPanel( wnd.tc.panel_0, self )
		self.__pyBtnRelation = TabButton( wnd.tc.btn_0 )
		labelGather.setPyBgLabel( self.__pyBtnRelation, "RelationShip:main", "btn_0" )
		self.__pyRelationPage = TabPage( self.__pyBtnRelation, self.__pyRelationPanel )
		self.__pyTabCtr.addPage( self.__pyRelationPage )

		self.__pyTongPanel = TongPanel( wnd.tc.panel_1, self )
		self.__pyBtnTong = TabButton( wnd.tc.btn_1 )
		labelGather.setPyBgLabel( self.__pyBtnTong, "RelationShip:main", "btn_1" )
		self.__pyTongPage = TabPage( self.__pyBtnTong, self.__pyTongPanel )
		self.__pyTongPage.enable = False
		self.__pyTabCtr.addPage( self.__pyTongPage )

		self.__pyAthlePanel = AthlePanel( wnd.tc.panel_2, self )
		self.__pyBtnAthle = TabButton( wnd.tc.btn_2 )
		labelGather.setPyBgLabel( self.__pyBtnAthle, "RelationShip:main", "btn_2" )
		self.__pyAthlePage = TabPage( self.__pyBtnAthle, self.__pyAthlePanel )
		self.__pyAthlePage.enable = False
		self.__pyTabCtr.addPage( self.__pyAthlePage )

	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_SOCIALITY_WINDOW"] = self.__toggleRelationWindow # 关系窗口
		self.__triggers["EVT_ON_TOGGLE_TONG_WINDOW"] = self.__toggleTongWindow # 公会窗口
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_MEMBERINFO"] = self.__onSetTongMemberInfo #添加帮会成员
		self.__triggers["EVT_ON_TOGGLE_TONG_CLEAR_ALL"] = self.__onRoleRemoveFromTong #自己被移出帮会
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onUpdateLevel			# level changed trigger
		self.__triggers["EVT_ON_ENABLE_ACTIVITY_BUTTON"] = self.__onEnableAthle
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )
	# --------------------------------------------------------------
	def __toggleRelationWindow( self ) :
		if self.visible and self.__pyTabCtr.pySelPage.index == 0 :
			self.hide()
		else :
			self.show( 0 )

	def __toggleTongWindow( self ) :
		if self.visible and self.__pyTabCtr.pySelPage.index == 1 :
			self.hide()
		else :
			player = BigWorld.player()
			if not player.isJoinTong():
				self.pyTongBox = getattr( self, "pyTongBox", None )
				if self.pyTongBox:self.pyTongBox.hide()
				# "你还没有帮会"
				self.pyTongBox = showAutoHideMessage( 3.0, 0x0682, mbmsgs[0x0c22] )
				return
			self.show( 1 )

	def __onSetTongMemberInfo( self, familyDBID, familyGrade, memberDBID ):
		if memberDBID == BigWorld.player().databaseID:
			self.__pyTongPage.enable = True

	def __onRoleRemoveFromTong( self ):
		self.__pyTongPanel.reset()
		self.__pyTabCtr.pySelPage = self.__pyRelationPage
		self.__pyTongPage.enable = False
	
	def __onUpdateLevel( self, oldLevel, newLevel ):
		self.__pyAthlePage.enable = newLevel >= 55 and self.isAthleReady
		self.__pyAthlePanel.onUpdateLevel( oldLevel, newLevel )
	
	def __onEnableAthle( self ):
		self.isAthleReady = True
		self.__pyAthlePage.enable = BigWorld.player().getLevel() >= 55

	def __onPageSelected( self, tabCtrl ):
		selIndex = tabCtrl.pySelPage.index
		if selIndex == 0:
			tabCtrl.pySelPage.pyPanel.initUIs()
		elif selIndex ==1:
			BigWorld.player().base.tong_requestMemberContributeInfos()
		elif selIndex == 2:
			BigWorld.player().base.queryMatchLog()
		self.__pyLbTitle.text = self.RELATION_NAMES[selIndex]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ):
		player = BigWorld.player()
		self.__pyTongPage.enable = player.isJoinTong()

	def onLeaveWorld( self ):
		self.__pyTongPage.selected = False
		self.__pyTongPage.enable = False
		self.__pyRelationPanel.reset()
		self.__pyTongPanel.reset()
		self.__pyAthlePanel.reset()
		self.isAthleReady = False
		self.hide()

	# -------------------------------------------------
	def show( self, index = 0 ) :
		count = self.__pyTabCtr.pageCount
		player = BigWorld.player()
		if index < 0 or index >= count : index = 0
		self.__pyTabCtr.pyPages[index].selected = True
		self.__pyRelationPanel.initUIs()
		if player.isJoinTong() : # 有帮会才初始化帮会界面
			self.__pyTongPanel.initUIs()
		Window.show( self )
		rds.helper.courseHelper.openWindow( "shejiao_chuangkou" )


	def hide( self ):
		self.__pyTongPanel.cancelTimer()
		self.__pyAthlePanel.cancelTimer()
		Window.hide( self )
