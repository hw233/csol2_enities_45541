# -*- coding: gb18030 -*-
#
# $Id: PetWindow.py,v 1.18 2008-08-26 02:16:24 huangyongwei Exp $


import GUIFacade
import csdefine
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.StaticText import StaticText
from guis.general.petswindow.petpanel.PetPanel import PetPanel
from guis.general.petswindow.vehiclepanel.VehiclePanel import VehiclePanel
from guis.general.petswindow.guardpanel.GuardPanel import GuardPanel
from guis.OpIndicatorObj import OpIndicatorObj
from Helper import courseHelper

class PetWindow( Window, OpIndicatorObj ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/petswindow/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		OpIndicatorObj.__init__( self )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyTabCtr = TabCtrl( wnd.tc )

		self.__pyPetPanel = PetPanel( wnd.tc.panel_0, self )
		self.__pyPetbtn= TabButton( wnd.tc.btn_0 )
		self.__pyPetbtn.commonMapping = util.getStateMapping( self.__pyPetbtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__pyPetbtn.selectedMapping = util.getStateMapping(self.__pyPetbtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__pyPetbtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pyPetbtn, "PetsWindow:PetsPanel", "lbTitle" )
		self.__pyTabCtr.addPage( TabPage( self.__pyPetbtn, self.__pyPetPanel ) )
		self.__pyPetPanel.onHide()				# 主要是disable ModelRenderer的渲染

		self.__pyVehiclePanel = VehiclePanel( wnd.tc.panel_1, self )
		self.__pyVehicleBtn = TabButton( wnd.tc.btn_1 )
		self.__pyVehicleBtn.commonMapping = util.getStateMapping( self.__pyVehicleBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__pyVehicleBtn.selectedMapping = util.getStateMapping(self.__pyVehicleBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__pyVehicleBtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pyVehicleBtn, "PetsWindow:VehiclesPanel", "lbTitle" )
		self.__pyTabCtr.addPage( TabPage( self.__pyVehicleBtn, self.__pyVehiclePanel ) )

		self.__pyGuardPanel = GuardPanel( wnd.tc.panel_2, self )
		self.__pyGuardBtn = TabButton( wnd.tc.btn_2 )
		self.__pyGuardBtn.commonMapping = util.getStateMapping( self.__pyVehicleBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__pyGuardBtn.selectedMapping = util.getStateMapping(self.__pyVehicleBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__pyGuardBtn.selectedForeColor = ( 142, 216, 217, 255 )
		self.__pyGuardBtn.visible = False
		labelGather.setPyBgLabel( self.__pyGuardBtn, "PetsWindow:GuardPanel", "lbTitle" )
		self.__pyTabCtr.addPage( TabPage( self.__pyGuardBtn, self.__pyGuardPanel ) )

		self.__pyTabCtr.onTabPageSelectedChanged.bind( self.__onPageSelected )

		self.pyLbTitle_.color = ( 255.0, 241.0, 192.0 )
		self.pyLbTitle_.charSpace = 2
	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_PET_WINDOW"] = self.__togglePetPanel
		self.__triggers["EVT_ON_TOGGLE_VEHICLE_WINDOW"] = self.__toggleVehiclePanel
#		self.__triggers["EVT_ON_TRIGGER_PG_CONTROL_PANEL"] = self.__triggerGuardPanel
#		self.__triggers["EVT_ON_HIDE_PG_CONTROL_PANEL"] = self.__hideGuardPanel
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )
	# ---------------------------------------------------------------
	def __togglePetPanel( self ) :
		if self.visible and self.__pyTabCtr.pySelPage.index == 0 :
			self.hide()
		else :
			self.show( 0 )

	def __toggleVehiclePanel( self ):
		if self.visible and self.__pyTabCtr.pySelPage.index == 1:
			self.hide()
		else:
			self.show( 1 )

	def __triggerGuardPanel( self ):
		"""
		触发守护界面
		"""
		self.__pyGuardBtn.visible = True
		self.show( 2 )
		
	def __hideGuardPanel( self ):
		"""
		隐藏守护界面
		"""
		self.__pyGuardBtn.visible = False

	def __onPageSelected( self, pyCtrl ):
		pySelPage = pyCtrl.pySelPage
		selIndex = pySelPage.index
		self.show( selIndex )
		toolbox.infoTip.hideOperationTips( 0x0041 )
		self.clearIndications()
		rds.opIndicator.registerValidQuestIdts()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","petWindow" ) )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMove_( self, dx, dy ) :
		Window.onMove_( self, dx, dy )
		self.__pyTabCtr.pySelPage.pyPanel.onMove( dx, dy )
#		toolbox.infoTip.moveOperationTips( 0x0041 )
#		toolbox.infoTip.moveOperationTips( 0x0042 )
		self.relocateIndications()

	# ----------------------------------------------------------------
	# operate indication methods
	# ----------------------------------------------------------------
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		trigger = ( "gui_visible","petWindow" )
		condition1 = ( "has_quest", )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition1, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showIndication
		
		condition2 = ( "quest_uncompleted", "checkHasVehicle" )	
		idtIds = rds.opIndicator.idtIdsOfCmd( condition2, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showIndicatePanel
			
		trigger1 = ( "gui_sub_panel_visible", "petWindow")
		idtIds = rds.opIndicator.idtIdsOfCmd( condition2, trigger1 )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showSummonVehicle
		
		

	def __showIndication( self, idtId, label ) :
		"""
		"""
		if label == "call_pet" :
			self.__indiacteSummonPet( idtId )

	def __indiacteSummonPet( self, idtId ) :
		"""
		指引玩家召唤宠物
		"""
		self.__pyPetPanel.indiacteSummonPet( idtId )
		
	def __showIndicatePanel( self, idtId, btnIndex ):
		"""
		指引玩家召唤骑宠
		"""
		pyPanel = self.__pyTabCtr.pyPanels[ int(btnIndex )]
		if pyPanel.visible:return
		pyBtn = self.__pyTabCtr.pyBtns[ int( btnIndex )]	
		toolbox.infoTip.showHelpTips( idtId, pyBtn )
		self.addVisibleOpIdt( idtId )
	
	def __showSummonVehicle( self, idtId, *args ):
		panelIndex = int( args[0])
		srcItemID = int( args[1] )
		doType= int( args[2] )
		pyPanel = self.__pyTabCtr.pyPanels[ panelIndex]
		pyPanel.showSummonVehicle( idtId, srcItemID, doType )
		

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# -----------------------------------------------------------------
	def show( self, index = 0 ):
		count = self.__pyTabCtr.pageCount
		if index < 0 or index >= count : index = 0
		self.__pyTabCtr.pyPages[index].selected = True
		Window.show( self )
		if index == 0:
			self.pyLbTitle_.text = labelGather.getText( "PetsWindow:PetsPanel", "lbTitle" )
			self.__pyPetPanel.onTrigger()
#			toolbox.infoTip.showOperationTips( 0x0041, self.__pyVehicleBtn )
		elif index == 1:
			self.pyLbTitle_.text = labelGather.getText( "PetsWindow:VehiclesPanel", "lbTitle" )
			self.__pyVehiclePanel.onTrigger()
		else:
			self.pyLbTitle_.text = labelGather.getText( "PetsWindow:GuardPanel", "lbTitle" )
			self.__pyGuardPanel.onTrigger()
		self.__pyTabCtr.pySelPage.pyPanel.onShow()
		rds.opIndicator.registerValidQuestIdts()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","petWindow" ) )
#		rds.opIndicator.triggerValidQuestIdts()		#在注册提示的时候，玩家的vehicleDatas还没发过来，在这里另外触发

	def setPropertyPanel( self, index ):
		self.__pyPetPanel.setComIndex( index )

	def hide( self ):
		Window.hide( self )
		toolbox.infoTip.hideOperationTips( 0x0041 )
		self.__pyTabCtr.pySelPage.pyPanel.onHide()
		self.clearIndications()

	def onLeaveWorld( self ) :
		self.__pyPetPanel.reset()
		self.__pyVehiclePanel.reset()
		self.__pyGuardPanel.reset()
		self.hide()
		
	def onEnterWorld( self ):
		self.__pyVehiclePanel.onEnterWorld()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setPos( self, ( left, top ) ) :
		Window._setPos( self, ( left, top ) )
		self.__pyTabCtr.pySelPage.pyPanel.onMove( 0, 0 )
#		toolbox.infoTip.moveOperationTips( 0x0041 )
#		toolbox.infoTip.moveOperationTips( 0x0042 )
		self.relocateIndications()
		
	def _getPanels( self ):
		return self.__pyTabCtr.pyPanels

	pos = property( Window._getPos, _setPos )
	pyPanels = property( _getPanels )