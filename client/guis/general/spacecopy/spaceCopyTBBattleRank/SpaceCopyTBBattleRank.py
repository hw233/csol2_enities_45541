# -*- coding: gb18030 -*-
#

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from SubPanel import SubPanel
from RewardDetails import RewardDetails

class SpaceCopyTBBattleRank( Window ):
	panel_map = {	"damagePanel":0,
			"curePanel":1,
			"diePanel":2,
	}
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyTBBattle/xmlz.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True

		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "SpaceCopyTBBattleRank:main", "lbTitle")
		self.__pyTabCtr = TabCtrl( wnd.tc )
		
		self.__pyDamagePanel = SubPanel( wnd.tc.panel_0, SpaceCopyTBBattleRank.panel_map["damagePanel"] ) # 伤害排名面板
		self.__pyBtnDamage = TabButton( wnd.tc.btn_0 )
		self.__pyBtnDamage.selectedForeColor = ( ( 255,255,255, 255 ) )
		labelGather.setPyBgLabel( self.__pyBtnDamage, "SpaceCopyTBBattleRank:main", "btn_0")
		self.__pyTabCtr.addPage( TabPage( self.__pyBtnDamage, self.__pyDamagePanel ) )

		self.__pyCurePanel = SubPanel( wnd.tc.panel_1, SpaceCopyTBBattleRank.panel_map["curePanel"] ) # 治疗排名面板
		self.__pyBtnCure = TabButton( wnd.tc.btn_1 )
		self.__pyBtnCure.selectedForeColor = ( ( 255,255,255, 255 ) )
		labelGather.setPyBgLabel( self.__pyBtnCure, "SpaceCopyTBBattleRank:main", "btn_1")
		self.__pyTabCtr.addPage( TabPage( self.__pyBtnCure, self.__pyCurePanel ) )

		self.__pyDiePanel = SubPanel( wnd.tc.panel_2, SpaceCopyTBBattleRank.panel_map["diePanel"] ) # 死亡排名面板
		self.__pyBtnDie = TabButton( wnd.tc.btn_2 )
		self.__pyBtnDie.selectedForeColor = ( ( 255,255,255, 255 ) )
		labelGather.setPyBgLabel( self.__pyBtnDie, "SpaceCopyTBBattleRank:main", "btn_2")
		self.__pyTabCtr.addPage( TabPage( self.__pyBtnDie, self.__pyDiePanel ) )

		self.__pyTabCtr.onTabPageSelectedChanged.bind( self.__onPageSelected )

	# -------------------------------------------------------------------
	# private
	#--------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TBBATTLE_SHOW_RANKLIST"] = self.__receiveRankInfo			
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	# -------------------------------------------------------
	def __onPageSelected( self, tabCtrl ):
		tabCtrl.pySelPage.pyPanel.onShow()
		
	def __receiveRankInfo( self, battleResultList ):
		self.clearItems()
		for pyPanel in self.__pyTabCtr.pyPanels:
			pyPanel.addRankInfo( battleResultList )
		Window.show( self )
		
	def clearItems( self ):
		for pyPanel in self.__pyTabCtr.pyPanels:
			pyPanel.clearItems()
		
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def hide( self ):
		if RewardDetails.instance().visible:
			RewardDetails.instance().hide()
		Window.hide( self )
		
	def onLeaveWorld( self ) :
		self.hide()
		
		