# -*- coding: gb18030 -*-
#
# $Id: TargetInfo.py,v 1.44 2008-09-05 09:27:18 yangkai Exp $

"""
implement target info window
"""

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.Button import Button
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from bwdebug import *
import VehicleHelper
import csdefine

class VehicleInfo( RootGUI ):
	def __init__( self ):
		vehead = GUI.load( "guis/general/petswindow/vehiclepanel/vehicleinfo.gui" )
		uiFixer.firstLoadFix( vehead )
		RootGUI.__init__( self, vehead )
		self.h_dockStyle == "CENTER"
		self.v_dockStyle = "TOP"
		self.moveFocus = True
		self.focus = True
		self.crossFocus = True
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= False
		self.visible = False
		self.__triggers = {}
		self.__delayCBID = 0
		self.__registerTriggers()
		self.__initHead( vehead )

	def __initHead( self, vehead ):
		self.__pyVehicleHead = PyGUI( vehead.vehiHead )
		self.__pyVehicleHead.texture = ""

		self.__pyCloseBtn = Button( vehead.closeBtn )
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseBtn.onLClick.bind( self.__onRecallVehicle )

	def dispose( self ) :
		self.__deregisterTriggers()
		RootGUI.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onMountVehicle #上坐骑
		self.__triggers["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onDisMountVehicle #下坐骑
		self.__triggers["EVT_ON_TARGET_BINDED"]			= self.__onTargetBinded
		self.__triggers["EVT_ON_TARGET_UNBINDED"]		= self.__onTrargetUnbinded
		self.__triggers["EVT_ON_VEHICLE_DATA_LOADED"]	= self.__onVehicleDataLoaded # 游戏刚刚启动时，骑宠数据加载完毕的通知
		
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __onVehicleDataLoaded( self ):
		"""
		此方法只会在游戏刚刚启动，并加载完毕骑宠数据的时候调用，
		用来解决骑宠buff通知界面更新骑宠相关表现，但是实际上骑宠
		数据还没有传过来的问题。by mushuang
		"""
		player = BigWorld.player()
		
		if VehicleHelper.isOnVehicle( player ):
			ECenter.fireEvent( "EVT_ON_PLAYER_UP_VEHICLE" ) 
		else:
			ECenter.fireEvent( "EVT_ON_PLAYER_DOWN_VEHICLE" )
		
	
	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	 # --------------------------------------------------------------------------
	def __onMountVehicle( self ): #骑宠进入世界
	 	player = BigWorld.player()
	 	vehicleData = player.vehicleDatas.get( player.vehicleDBID, None )
	 	if vehicleData is None:
	 		WARNING_MSG( "vehicleData is None, may be transferring!" ) # 这并不是真正出错，有可能是服务器的数据在调用这个方法的时候还没有发送过来
	 		return
	 	srcItemID = vehicleData["srcItemID"]
	 	item = player.createDynamicItem( srcItemID )
	 	headText = item.icon()
	 	self.__pyVehicleHead.texture = headText
		width = BigWorld.screenWidth()
		self.center = width/2.0
		self.top = 5.0
	 	self.show()
	 	

	def __onDisMountVehicle( self ):
		self.__pyVehicleHead.texture = ""
		self.hide()

	def __onTargetBinded( self, target ):
		self.__delayCBID = BigWorld.callback( 0.1, self.__delayLout )

	def __onTrargetUnbinded( self, target ):
		self.__delayCBID = BigWorld.callback( 0.1, self.__delayLout )
	
	def __delayLout( self ):
		if self.visible:
			targetInfo = rds.ruisMgr.targetMgr.targetUI
			if targetInfo:
				self.left = targetInfo.right - 30.0
			else:
				self.center = BigWorld.windowSize()[0]/2.0

	def __onRecallVehicle( self ):
		player = BigWorld.player()
		player.cell.retractVehicle()

	def onMouseEnter_( self ):
		RootGUI.onMouseEnter_( self )
		player = BigWorld.player()
		if player is None: return
		vehicledbid = player.vehicleDBID
		vehicleData = player.vehicleDatas.get( player.vehicleDBID )
		if vehicleData is None: return

		srcItemID = vehicleData["srcItemID"]
		item = player.createDynamicItem( srcItemID )
		name = item.name()
		nameText = name.split("(")[-1].split(")")[0]
		level = player.vehicleDatas[vehicledbid]["level"]
		levelText = labelGather.getText( "PetsWindow:VehiclesPanel", "levelInfo" )%level
		speed = item.getVehicleMoveSpeed()*100  #移动增加速度
		speedText = labelGather.getText( "PetsWindow:VehiclesPanel", "addSpeed" )%speed
		type = player.vehicleDatas[vehicledbid]["type"]
		typeText = None
		if type == csdefine.VEHICLE_TYPE_LAND:
			typeText = labelGather.getText( "PetsWindow:VehiclesPanel", "landVehicle" )
		elif type == csdefine.VEHICLE_TYPE_FLY:
			typeText = labelGather.getText( "PetsWindow:VehiclesPanel", "flyVehicle" )
		else:
			ERROR_MSG("No type of this vehicle!")
		tips = [nameText, levelText, typeText, speedText]
		toolbox.infoTip.showItemTips( self, tips )

	def onMouseLeave_( self ):
		RootGUI.onMouseLeave_( self )
		toolbox.infoTip.hide()

	def onMove_( self, dx, dy ):
		RootGUI.onMove_( self, dx, dy )
#		toolbox.infoTip.moveOperationTips( 0x0045 )

	# -------------------------------------------------------
	# public
	# -------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		targetInfo = rds.ruisMgr.targetMgr.targetUI
		if targetInfo and targetInfo.visible:
			self.left = targetInfo.right - 30.0
		else:
			self.center = BigWorld.windowSize()[0]/2.0
		RootGUI.show( self )
#		toolbox.infoTip.showOperationTips( 0x0045, self )

	def hide( self ):
		RootGUI.hide( self )
		self.__delayCBID = 0
#		toolbox.infoTip.hideOperationTips( 0x0045 )

	def onLeaveWorld( self ):
		self.hide()