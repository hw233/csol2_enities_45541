# -*- coding: gb18030 -*-
#
# $Id: VehiclePanel.py,v 1.13 2008-09-04 06:34:43 yangkai Exp $

import event.EventCenter as ECenter
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ProgressBar import HProgressBar
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from VehicleRender import VehicleRender
from VechileItem import VechileItem
from gbref import rds
from VehicleDelVerifier import VehicleDelVerifier
from VehicleFeed import VehicleFeed
from StageUpgrade import StageUpgrade
from VehicleSealed import VehicleSealed
from config.VehicleUpStep import Datas as U_DATA
from VehicleHelper import getVehicleMaxStep
import csstatus
import Define
import csdefine
import csconst
import time
from Time import Time

class VehiclePanel( TabPanel ):

	_cc_items_rows = ( 3, 2 )

	def __init__( self, tabPanel, pyBinder = None ):
		TabPanel.__init__( self, tabPanel, pyBinder )
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( tabPanel )
		self.__turnModelCBID = 0
		self.__allModels = {}
		self.__deliverVerifier = None	#传功确认提示框
		self.__needRemind = True

	def __initialize( self, tabPanel ):
		self.__pyStExpRatio = StaticText( tabPanel.vehicle_exp.value ) #骑宠经验
		self.__pyStExpRatio.fontSize = 12
		self.__pyStExpRatio.text = ""

		self.__pyStVehicleName = StaticText( tabPanel.stVehicleName ) #骑宠名称
		self.__pyStVehicleName.text= ""

		self.__pyStStage = StaticText( tabPanel.vehicle_stage.value ) # 骑宠阶次
		self.__pyStStage.fontSize = 12
		self.__pyStStage.text = ""

		self.__pyStLevel = StaticText( tabPanel.vehicle_level.value ) # 骑宠等级
		self.__pyStLevel.fontSize = 12
		self.__pyStLevel.text = ""

		self.__pyStFull = StaticText( tabPanel.vehicle_full.value ) # 骑宠饱腹截止日期
		self.__pyStFull.fontSize = 12
		self.__pyStFull.text = ""

		self.__pyStStageName = CSRichText( tabPanel.vehicle_stage.stName )
		self.__pyStStageName.crossFocus = True
		self.__pyStStageName.text = labelGather.getText( "PetsWindow:VehiclesPanel", "stageText" )
		self.__pyStStageName.dsp = ""
		self.__pyStStageName.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyStStageName.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyStLevelName = CSRichText( tabPanel.vehicle_level.stName )
		self.__pyStLevelName.crossFocus = True
		self.__pyStLevelName.text = labelGather.getText( "PetsWindow:VehiclesPanel", "levelText" )
		self.__pyStLevelName.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "levelNameDsp" )
		self.__pyStLevelName.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyStLevelName.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyBtnUpStage = HButtonEx( tabPanel.btnUpStage ) #升阶
		self.__pyBtnUpStage.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnUpStage.onLClick.bind( self.__onUpStage )
		labelGather.setPyBgLabel( self.__pyBtnUpStage, "PetsWindow:VehiclesPanel", "btnUpStage")
		self.__pyBtnUpStage.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "btnUpStageDsp" )
		self.__pyBtnUpStage.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnUpStage.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyBtnPicture = HButtonEx( tabPanel.btnPicture ) #图鉴
		self.__pyBtnPicture.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnPicture.onLClick.bind( self.__onShowPicture )
		labelGather.setPyBgLabel( self.__pyBtnPicture, "PetsWindow:VehiclesPanel", "btnPicture")
		self.__pyBtnPicture.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "btnPictureDsp" )
		self.__pyBtnPicture.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnPicture.onMouseLeave.bind( self.__onBtnMouseLeave )
		self.__pyBtnPicture.enable = False
		
		self.__pyBtnDeliver = HButtonEx( tabPanel.btnDeliver ) #传功
		self.__pyBtnDeliver.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDeliver.onLClick.bind( self.__onDeliver )
		labelGather.setPyBgLabel( self.__pyBtnDeliver, "PetsWindow:VehiclesPanel", "btnDeliver")
		self.__pyBtnDeliver.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "btnDeliverDsp" )
		self.__pyBtnDeliver.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnDeliver.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyBtnFeed = HButtonEx( tabPanel.btnFeed ) #喂食
		self.__pyBtnFeed.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnFeed.onLClick.bind( self.__onFeed )
		labelGather.setPyBgLabel( self.__pyBtnFeed, "PetsWindow:VehiclesPanel", "btnFeed")
		self.__pyBtnFeed.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "btnFeedDsp" )
		self.__pyBtnFeed.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnFeed.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyBtnActivate = HButtonEx( tabPanel.btnActivate ) #激活
		self.__pyBtnActivate.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnActivate.onLClick.bind( self.__onActivate )
		labelGather.setPyBgLabel( self.__pyBtnActivate, "PetsWindow:VehiclesPanel", "btnActivate")
		self.__pyBtnActivate.dsp = ""
		self.__pyBtnActivate.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnActivate.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyBtnCancelActivate = HButtonEx( tabPanel.btnCancelActivate ) #取消激活
		self.__pyBtnCancelActivate.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancelActivate.visible = False
		self.__pyBtnCancelActivate.onLClick.bind( self.__onCancelActivate )
		labelGather.setPyBgLabel( self.__pyBtnCancelActivate, "PetsWindow:VehiclesPanel", "btnCancelActivate")

		self.__pyBtnSealed = HButtonEx( tabPanel.btnSealed ) #封灵
		self.__pyBtnSealed.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSealed.onLClick.bind( self.__onSealed )
		labelGather.setPyBgLabel( self.__pyBtnSealed, "PetsWindow:VehiclesPanel", "btnSealed")
		self.__pyBtnSealed.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "btnSealedDsp" )
		self.__pyBtnSealed.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnSealed.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyBtnLeft = Button( tabPanel.btnLeft ) #向左转动模型
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__onTurnLeft )

		self.__pyBtnRight = Button( tabPanel.btnRight ) #向右转动模型
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__onTurnRight )

		self.__pyVehiclesPage = ODPagesPanel( tabPanel.vehiclesPanel, tabPanel.pgIdxBar )
		self.__pyVehiclesPage.onViewItemInitialized.bind( self.__initListItem )
		self.__pyVehiclesPage.onDrawItem.bind( self.__drawListItem )
		self.__pyVehiclesPage.selectable = True
		self.__pyVehiclesPage.onItemSelectChanged.bind( self.__onVehicleSelectedChange )
		self.__pyVehiclesPage.viewSize = self._cc_items_rows

		self.__pyVehicleRender = VehicleRender( tabPanel.vehicleRender )

		labelGather.setLabel( tabPanel.vehicle_exp.stName, "PetsWindow:VehiclesPanel", "expText" )
		labelGather.setLabel( tabPanel.vehicle_full.stName, "PetsWindow:VehiclesPanel", "fullText" )
		labelGather.setLabel( tabPanel.listBg.bgTitle.stTitle, "PetsWindow:VehiclesPanel", "vehilceList")
		labelGather.setLabel( tabPanel.attrsPanel.bgTitle.stTitle, "PetsWindow:VehiclesPanel", "vehilceAttrs")
		self.__initVechicleAttr( tabPanel )

	def __initVechicleAttr( self, panel ):
		"""
		初始化骑宠基本属性
		"""
		self.__pyVehicleAttrs = {}
		for name, item in panel.attrsPanel.children:
			if "attr_" not in name:continue
			tag = name.split( "_" )[1]
			pyVehicleAttr = VehicleAttr( item )
			if tag == "growth":
				stTitle = pyVehicleAttr.getStTitle()
				stTitle.crossFocus = True
				stTitle.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "growthDsp" )
				stTitle.onMouseEnter.bind( self.__onBtnMouseEnter )
				stTitle.onMouseLeave.bind( self.__onBtnMouseLeave )
			pyVehicleAttr.title = labelGather.getText( "PetsWindow:VehiclesPanel", tag )
			pyVehicleAttr.text = ""
			self.__pyVehicleAttrs[tag] = pyVehicleAttr

	# ----------------------------------------------------------
	# private
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_VEHICLE_ENTER_WORLD"] = self.__onVehicleEnterWorld #骑宠进入世界
		self.__triggers["EVT_ON_PLAYER_ADD_VEHICLE"] = self.__onAddVehicle #增加骑宠
		self.__triggers["EVT_ON_VEHICLE_UPDATE_ATTR"] = self.__onVehicleAttrUpdate #骑宠属性更新
		self.__triggers["EVT_ON_VEHICLE_SLECTED"] = self.__onVehicleSelected #选择某个骑宠图标
		self.__triggers["EVT_ON_VEHICLE_EXP_UPDATE"] = self.__onVehicleExpUpdate # 骑宠经验值更新
#		self.__triggers["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onMountVehicle #上坐骑
#		self.__triggers["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onDisMountVehicle #下坐骑
		self.__triggers["EVT_ON_VEHICLE_ACTIVATED"] = self.__onVehicleActivated #激活骑宠
		self.__triggers["EVT_ON_VEHICLE_UNACTIVATED"] = self.__onVehicleUnActivated #取消激活骑宠	
		self.__triggers["EVT_ON_VEHICLE_FULLDEGREE_UPDATE"] = self.__onVehicleFeeded #骑宠喂食 by姜毅
		self.__triggers["EVT_ON_PLAYER_FREE_VEHICLE"] = self.__onVehicleSealed	#封印成功回调

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __initListItem( self, pyViewItem ):
		"""
		初始化添加的列表项
		"""
		pyVehicle = VechileItem()
		pyViewItem.pyVehicle = pyVehicle
		pyViewItem.addPyChild( pyVehicle )
		pyViewItem.dragFocus = False
		pyViewItem.focus = True
		pyVehicle.left = 0
		pyVehicle.top = 0

	def __drawListItem( self, pyViewItem ) :
		"""
		重画商品列表项
		"""
		vehicleData = pyViewItem.pageItem
		pyVehicle = pyViewItem.pyVehicle
		pyVehicle.selected = pyViewItem.selected
		player = BigWorld.player()
		if vehicleData is not None:
			isActived = hasattr( player,"activateVehicleID" ) and \
			vehicleData["id"] == player.activateVehicleID
		else:
			isActived = False
		pyVehicle.update( vehicleData, isActived )
		pyViewItem.focus = vehicleData is not None

	def __onAddVehicle( self, dbid ):
		"""
		1、服务器通知有骑宠增加
		2、客户端初始化骑宠信息
		"""
		player = BigWorld.player()
		if player is None: return
		vehicleDatas = player.vehicleDatas
		vehicleIndex = vehicleDatas.keys().index( dbid )
		viewAmout = self._cc_items_rows[0]*self._cc_items_rows[1]
		pageIndex = vehicleIndex / viewAmout + 1
		self.__pyVehiclesPage.pageIndex = pageIndex
		vehicleData = vehicleDatas.get( dbid, None )
		if vehicleData is None:return
		if not vehicleData in self.__pyVehiclesPage.items:
			self.__pyVehiclesPage.addItem( vehicleData )

	def __onVehicleSelectedChange( self, selIndex ):
		"""
		骑宠框点击触发
		"""
		StageUpgrade.instance().hide()	
		VehicleSealed.instance().hide()
		VehicleFeed.instance().hide()	
		if selIndex < 0:return
		player = BigWorld.player()
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is None:return

		curVehicleDBID = player.activateVehicleID 	#当前激活的骑宠
		selVehicleDBID = selVehicleData["id"]
		self.__pyBtnActivate.visible = selVehicleDBID != curVehicleDBID
		self.__pyBtnCancelActivate.visible = selVehicleDBID == curVehicleDBID
		self.__pyBtnSealed.enable = selVehicleDBID != curVehicleDBID
		if self.__pyBtnActivate.visible:
			self.__pyBtnActivate.enable = True	# 激活按钮可点击
		for pyViewItem in self.__pyVehiclesPage.pyViewItems:
			itemIndex = pyViewItem.itemIndex
			pyVehicle = pyViewItem.pyVehicle
			pyVehicle.selected = itemIndex == selIndex
			
		vehicleDatas = player.vehicleDatas

		# 刷新属性显示
		vehicleData = vehicleDatas.get( selVehicleDBID )
		if vehicleData is None:
			return
		# 喂养和放生界面相关调整 by姜毅

		# 刷新模型
		self.__setModel( selVehicleDBID )

		# 基本属性
		self.__setType( vehicleData["type"] ) #类型
		self.__onAttrUpdate( "growth", vehicleData["growth"] ) 	#成长度
		self.__onAttrUpdate( "strength", vehicleData["strength"] ) 	#力量
		self.__onAttrUpdate( "dexterity", vehicleData["dexterity"] ) 	#敏捷
		self.__onAttrUpdate( "intellect", vehicleData["intellect"] ) 	#智力
		self.__onAttrUpdate( "corporeity", vehicleData["corporeity"] ) 	#体质

		srcItemID = selVehicleData["srcItemID"]
		vehicleItem = BigWorld.player().createDynamicItem( srcItemID )
		# 名称
		name = vehicleItem.name().split("(")[-1].split(")")[0]
		self.__pyStVehicleName.text = "%s"%name
		self.__onUpdateSpeed( selVehicleDBID ) #移速

		self.__setStage( vehicleData ) #骑宠阶次
		self.__setLevel( vehicleData["level"] ) #骑宠等级
		self.__setFullDeadtime( selVehicleDBID ) #骑宠饱腹截止日期
		self.__updateExpBar( selVehicleDBID ) # 刷新经验值
		self.__updateBtnEnable( vehicleData["type"] ) #刷新骑宠类型

	def __updateBtnEnable( self, type ):
		"""
		根据骑宠类型更新按键
		"""
		if type == csdefine.VEHICLE_TYPE_FLY:	# 飞行骑宠
			labelGather.setPyBgLabel( self.__pyBtnActivate, "PetsWindow:VehiclesPanel", "btnRiding")
			self.__pyBtnUpStage.enable = False
			self.__pyBtnDeliver.enable = False
			self.__pyBtnActivate.dsp = ""
		else:
			labelGather.setPyBgLabel( self.__pyBtnActivate, "PetsWindow:VehiclesPanel", "btnActivate")
			self.__pyBtnUpStage.enable = True
			self.__pyBtnDeliver.enable = True
			self.__pyBtnActivate.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "btnActivateDsp" )

	def __onVehicleEnterWorld( self, vehicle ):
		"""
		骑宠进入世界，初始化装备栏和技能栏
		"""
		return

	def __onUpStage( self ):
		"""
		升阶
		"""
		vehicleData =  self.__pyVehiclesPage.selItem
		if vehicleData is None:return
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY:		#飞行骑宠不能升阶
			BigWorld.player().statusMessage( csstatus.VEHICLE_UPSTEP_TO_MAX )
			return
		if vehicleData["step"] == getVehicleMaxStep( vehicleData["id"] ):	#已经达到最大阶次
			BigWorld.player().statusMessage( csstatus.VEHICLE_UPSTEP_TO_MAX )
			return
		if vehicleData["id"] != BigWorld.player().activateVehicleID: #判断祭宠是不是当前激活的骑宠
			BigWorld.player().statusMessage( csstatus.VEHICLE_UPSTEP_NEED_TO_BE_ACTIVATED )
			return

		if vehicleData["level"] < U_DATA[ vehicleData["step"] ]["needLevel"]: #判断主骑宠等级
			BigWorld.player().statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_NO_LEVEL, U_DATA[ vehicleData["step"] ]["needLevel"] )
			return
		if vehicleData["id"] == BigWorld.player().vehicleDBID: #判断主骑宠是不是当前骑乘的骑宠
			BigWorld.player().cell.retractVehicle() #如果在骑宠上就下骑宠，回收进行升阶
		if BigWorld.player().activateVehicleID:
			StageUpgrade.instance().show()

	def __onShowPicture( self ):
		"""
		图鉴
		"""
		BigWorld.player().statusMessage( csstatus.VEHICLE_SHOW_PICTURE_NOT_OPEN )

	def __onBtnMouseEnter( self, pyBtn ):
		"""
		"""
		if pyBtn is None: return
		toolbox.infoTip.showToolTips( self, pyBtn.dsp )

	def __onBtnMouseLeave( self, pyBtn ):
		"""
		"""
		toolbox.infoTip.hide()

	def __remind( self, res, unremind ) :
		"""
		传功提示
		"""
		if res == RS_YES :
			self.__needRemind = not unremind
			self.__deliverToVehicle()

	def __onDeliver( self ):
		"""
		传功
		"""
		if BigWorld.player().intonating(): return
		if self.__deliverVerifier is None :
			self.__deliverVerifier = __import__( "guis/general/petswindow/vehiclepanel/VerifyBox" )
		if self.__needRemind:
			self.__deliverVerifier.show( self.__remind )
		else:
			self.__deliverToVehicle()

	def __deliverToVehicle( self ):
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is not None:
			vehicleDBID = selVehicleData["id"]
			BigWorld.player().transVehicle( vehicleDBID )

	def __onFeed( self ):
		"""
		喂食
		"""
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is not None:
			vehicleDBID = selVehicleData["id"]
			VehicleFeed.instance().show( vehicleDBID )

	def __checkIsSelVehicle( self, dbid ):
		"""
		骑宠dbid是否和当前选择的骑宠一致
		"""
		player = BigWorld.player()
		if player is None:
			return False
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is None:
			return False
		return dbid == selVehicleData["id"] 

	def __onVehicleExpUpdate( self, dbid ):
		"""
		骑乘经验条更新回调
		"""
		if not self.__checkIsSelVehicle( dbid ):
			return
		self.__updateExpBar( dbid )

	def __updateExpBar( self, dbid ):
		"""
		更新骑宠经验
		"""
		# 获取经验值和等级
		player = BigWorld.player()
		exp = float( player.vehicleDatas[dbid]["exp"] )
		level = player.vehicleDatas[dbid]["level"]
		type = player.vehicleDatas[dbid]["type"]

		# 获取当前等级需要的升级经验值
		upExp =  float( rds.vehicleExp.getExp( level ) )

		if upExp == 0.0 or type == csdefine.VEHICLE_TYPE_FLY:	# 已经达到最高级或者是飞行骑宠
			self.__pyStExpRatio.text = labelGather.getText( "PetsWindow:VehiclesPanel", "deliverExpMax" )
		else:
			self.__pyStExpRatio.text = labelGather.getText( "PetsWindow:VehiclesPanel", "deliverExp", upExp )

	def __onVehicleLevelUpdate( self, dbid ):
		"""
		骑宠等级更新回调
		"""
		if not self.__checkIsSelVehicle( dbid ):
			return

		level = player.vehicleDatas[dbid]["level"]
		self.__setLevel( level )

	def __setLevel( self, level ):
		"""
		更新骑宠等级
		"""
		self.__pyStLevel.text = labelGather.getText( "PetsWindow:VehiclesPanel", "levelInfo", level )

	def __onVehicleFeeded( self, dbid ):
		"""
		骑宠喂食成功回调 
		"""
		if self.__checkIsSelVehicle( dbid ):
			self.__setFullDeadtime( dbid )
		if VehicleFeed.instance().visible:
			VehicleFeed.instance().onFeedSuccess( )

	def __onVehicleSealed( self, vehicleDBID ):
		"""
		界面上删除被封印的骑宠
		"""
		player = BigWorld.player()
		if player is None:
			return
		for vehicleData in self.__pyVehiclesPage.items:
			if vehicleData["id"] == vehicleDBID:
				self.__pyVehiclesPage.removeItem( vehicleData )
				if self.__allModels.has_key( vehicleDBID ):
					self.__allModels.pop( vehicleDBID )
		if len( self.__pyVehiclesPage.items ) <= 0:
			self.reset()

		VehicleSealed.instance().hide()

	def __setFullDeadtime( self, dbid ):
		"""
		更新饱腹度截止日期
		"""
		player = BigWorld.player()
		vehicleData = player.vehicleDatas.get( dbid )
		if vehicleData is None:return
		fullDegree = vehicleData["fullDegree"]
		if fullDegree < int( Time.time() ):
			self.__pyStFull.text = labelGather.getText( "PetsWindow:VehicleFeed", "hungry" )
		else:
			ltFullDegree = time.localtime( fullDegree )
			self.__pyStFull.text = labelGather.getText( "PetsWindow:VehiclesPanel", "fullDays", ltFullDegree[0], ltFullDegree[1], ltFullDegree[2], ltFullDegree[3], ltFullDegree[4] )

	def __setStage( self, vehicleData ):
		"""
		更新骑宠阶次
		"""
		if vehicleData is None: return
		stage = vehicleData["step"]
		type = vehicleData["type"]
		self.__pyStStage.text = labelGather.getText( "PetsWindow:VehiclesPanel", "stageInfo", stage )
		if stage == getVehicleMaxStep( vehicleData["id"] ) or type == csdefine.VEHICLE_TYPE_FLY:	# 已达到最高阶或者是飞行骑宠
			self.__pyStStageName.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "stageNameMaxDsp" )
		else:
			maxStage = getVehicleMaxStep( vehicleData["id"] )
			needLevel = U_DATA[stage]["needLevel"]
			self.__pyStStageName.dsp = labelGather.getText( "PetsWindow:VehiclesPanel", "stageNameDsp", maxStage, needLevel )

	def __getVehicleNameByID( self, vehicleID ):
		"""
		获取骑宠名字
		"""
		vehicleName = ""
		player = BigWorld.player()
		vehicleData = player.vehicleDatas.get( vehicleID )
		if vehicleData is None:return vehicleName
		srcItemID = vehicleData["srcItemID"]
		vehicleItem = player.createDynamicItem( srcItemID )
		vehicleName = vehicleItem.name().split("(")[-1].split(")")[0]
		return vehicleName

	def __onVehicleActivated( self ):
		"""
		激活骑宠
		"""	
		self.__flashVehicle()
		vehicleData = self.__pyVehiclesPage.selItem
		if vehicleData is None:return
		if vehicleData.get("id") == BigWorld.player().activateVehicleID:
			self.__pyBtnActivate.visible = False
			self.__pyBtnCancelActivate.visible = True
			self.__pyBtnSealed.enable = False
			toolbox.infoTip.hide()

	def __onVehicleUnActivated( self, vehicleID ):
		"""
		取消激活骑宠
		"""
		self.__flashVehicle()
		StageUpgrade.instance().hide()
		vehicleData = self.__pyVehiclesPage.selItem
		if vehicleData is None:return
		if vehicleData.get("id") != BigWorld.player().activateVehicleID:
			self.__pyBtnActivate.visible = True
			self.__pyBtnCancelActivate.visible = False
			self.__pyBtnSealed.enable = True
			self.__pyBtnActivate.enable = True

	def __flashVehicle( self ):
		"""
		刷新骑宠界面
		"""
		for pyViewItem in self.__pyVehiclesPage.pyViewItems:
			pyVehicle = pyViewItem.pyVehicle
			vehicleData = pyViewItem.pageItem
			if pyVehicle.vehicleID == BigWorld.player().activateVehicleID:
				pyVehicle.update( vehicleData, True )
			else:
				pyVehicle.update( vehicleData, False )

	def __onVehicleSelected( self, vehicleID ):
		for pyViewItem in self.__pyVehiclesPage.pyViewItems:
			vehicleData = pyViewItem.pageItem
			pyVehicle = pyViewItem.pyVehicle
			if vehicleData is None:continue
			pyVehicle.selected = vehicleData["id"] == vehicleID
			if vehicleData["id"] == vehicleID:
				self.__pyVehiclesPage.selItem = vehicleData

	def __onFeedVehicle( self ):
		"""
		宠物喂食 by姜毅
		"""
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is None:return
		player = BigWorld.player()
		if player is None: return
		player.feedVehicle( selVehicleData["id"] )

	def __onActivate( self ):
		"""
		激活骑宠
		"""
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is None:return
		vehicleDBID = selVehicleData["id"]
		player = BigWorld.player()
		if player.vehicleDBID == vehicleDBID:
			player.cell.retractVehicle()
		else:
			player.conjureVehicle( vehicleDBID )

	def __onCancelActivate( self ):
		"""
		取消激活
		"""
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is None:return
		if selVehicleData["id"] == BigWorld.player().activateVehicleID:
			BigWorld.player().deactivateVehicle()

	def __onSealed( self ):
		"""
		封灵
		"""
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is None:return
		vehicleDBID = selVehicleData["id"]
		VehicleSealed.instance().show( vehicleDBID )

	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __onTurnLeft( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __onTurnRight( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		"""
		self.__pyVehicleRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	def __setModel( self, vehicleDBID ):
		"""
		设置DBID的模型
		"""
		player = BigWorld.player()
		if player is None: return

		vehicleData = player.vehicleDatas.get( vehicleDBID )
		if vehicleData is None: return

		itemID = vehicleData["srcItemID"]
		item = player.createDynamicItem( itemID )
		if item is None: return
		itemModelID = item.model()

		if vehicleDBID in self.__allModels:
			model = self.__allModels[vehicleDBID]
			self.__pyVehicleRender.update( itemModelID, model )
		else:
			rds.itemModel.createModelBG( itemModelID, Functor( self.__onModelCreated, vehicleDBID, itemModelID ) )

	def __onModelCreated( self, vehicleDBID, itemModelID, model ):
		"""
		模型后线程加载完回调
		"""
		if model:
			effectIDs = rds.itemModel.getMEffects( itemModelID )
			for effectID in effectIDs:
				dictData = rds.spellEffect.getEffectConfigDict( effectID )
				if len( dictData ) == 0: continue
				effect = rds.skillEffect.createEffect( dictData, model, model, Define.TYPE_PARTICLE_PLAYER,  Define.TYPE_PARTICLE_PLAYER )
				effect.start()
		self.__allModels[vehicleDBID] = model
		selVehicleData = self.__pyVehiclesPage.selItem
		if selVehicleData is None:return
		if selVehicleData["id"] == vehicleDBID:
			self.__pyVehicleRender.update( itemModelID, model )

	def __onVehicleAttrUpdate( self, dbid ):
		"""
		重新刷一遍属性
		"""		
		if not self.__checkIsSelVehicle( dbid ):
			return
		vehicleData = BigWorld.player().vehicleDatas.get( dbid )
		for attrTag, value in vehicleData.iteritems():
			if attrTag == "level":		
				self.__setLevel( value )
			elif attrTag == "step":
				self.__setStage( vehicleData )
			elif attrTag == "type":
				self.__setType( value )
			else:
				self.__onAttrUpdate( attrTag, value )	#刷新基本属性
		if self.__allModels.has_key( dbid ):
			self.__allModels.pop( dbid )
		self.__setModel( dbid )		#属性模型
		self.__onUpdateSpeed( dbid )	#更新速度
		self.__updateExpBar( dbid )
		self.__flashVehicle()
		vehicleName = self.__getVehicleNameByID( dbid )
		self.__pyStVehicleName.text = vehicleName
		if StageUpgrade.instance().visible:
			StageUpgrade.instance().show()

	def __setType( self, type ):
		typeDict = csconst.VEHICLE_TYPE_TEXT
		if typeDict.has_key( type ):
			vehicleTypeText = csconst.VEHICLE_TYPE_TEXT[ type ]
		else:
			vehicleTypeText = ""
		self.__onAttrUpdate( "type", vehicleTypeText )

	def __onUpdateSpeed( self, dbid ):
		"""
		更新速度
		"""
		player = BigWorld.player()
		if player is None: return
		itemID = player.vehicleDatas[dbid]["srcItemID"]
		item = player.createDynamicItem( itemID )
		if item is None: return
		accelerate = "%0.0f%%"%( (item.getVehicleMoveSpeed() )*100 )
		self.__onAttrUpdate( "accelerate", accelerate )

	def __onAttrUpdate( self, attrTag, value ):
		"""
		更新骑宠各战斗属性
		"""
		if self.__pyVehicleAttrs.has_key( attrTag ):
			pyStAttr = self.__pyVehicleAttrs[attrTag]
			pyStAttr.text = str( value )			

	def __clearAttrs( self ):
		"""
		重置骑宠基本属性
		"""
		for tag, pyStAttr in self.__pyVehicleAttrs.iteritems():
			pyStAttr.text = ""

	# -------------------------------------------------------
	# public
	# -------------------------------------------------------

	def onShow( self ) :
		self.__pyVehicleRender.enableDrawModel()
		TabPanel.onShow( self )
		if len( BigWorld.player().vehicleDatas):
			pass
#			toolbox.infoTip.showOperationTips( 0x0042, self.__pyBtnBeckon )

	def onHide( self ):
		TabPanel.onHide( self )
		self.__pyVehicleRender.disableDrawModel()
		toolbox.infoTip.hideOperationTips( 0x0042 )

	def onMove( self, dx, dz ):
		pass

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onTrigger( self ):
		player = BigWorld.player()
		vehicleDBID = player.activateVehicleID
		vehicleDatas = player.vehicleDatas
		vehicleAmount = len( vehicleDatas )
		if vehicleAmount <= 0:
			self.__pyBtnActivate.enable = False
			self.__pyBtnActivate.visible = True
			self.__pyBtnCancelActivate.visible = False
			self.__pyBtnSealed.enable = False
			return
		if vehicleDBID != 0:
			for index, vehicleData in enumerate( self.__pyVehiclesPage.items ):
				if vehicleData["id"] == vehicleDBID:
					#自动翻到激活骑宠那一页
					self.__pyVehiclesPage.pageIndex = index / 6
			self.__onVehicleSelected( vehicleDBID )
		else:
			self.__pyVehiclesPage.pageIndex = 0	#默认第一页
			self.__onVehicleSelected( self.__pyVehiclesPage.items[0]["id"] )
		self.__flashVehicle()

	def reset( self ):
		self.__pyVehiclesPage.clearItems()
		self.__clearAttrs()
		self.__pyVehicleRender.clearModel()
		self.__pyStStage.text = ""
		self.__pyStFull.text = ""
		self.__pyStLevel.text = ""
		self.__pyStVehicleName.text= ""
		self.__pyStExpRatio.text = ""
		self.__pyBtnActivate.visible = True
		self.__pyBtnActivate.enable = False
		self.__pyBtnSealed.visible = True
		self.__pyBtnSealed.enable = False
		self.__pyBtnCancelActivate.visible = False
		self.__turnModelCBID = 0
		self.__allModels = {}

	def onEnterWorld( self ):
		self.__needRemind = True

	def showSummonVehicle( self,idtId, srcItemID, doType ):
		"""
		指引激活骑宠内容
		"""
		pyViewItem = self.__getPyItemById( srcItemID )
		pyBtn = None
		if doType == 0: #选择骑宠	
			if pyViewItem is not None and not pyViewItem.selected:
				pyBtn = pyViewItem.pyVehicle.getObjectItem()					
		elif doType == 1:#激活骑宠
			if pyViewItem and pyViewItem.selected:
				pyBtn = self.__pyBtnActivate
		if pyBtn:
			toolbox.infoTip.showHelpTips( idtId, pyBtn )
			self.pyTopParent.addVisibleOpIdt( idtId )

	def __getPyItemById( self, vehicleID ):
		pyItem = None
		for pyViewItem in self.__pyVehiclesPage.pyViewItems:
			if pyViewItem.pageItem is None: continue
			if pyViewItem.pageItem["srcItemID"] == vehicleID:
				pyItem = pyViewItem
		return pyItem

class VehicleAttr( PyGUI ):
	def __init__( self, attrItem ):
		PyGUI.__init__( self, attrItem )
		self.__pyStTitle = CSRichText( attrItem.titleText )
		self.__pyStTitle.foreColor = ( 236.0, 218.0, 157.0 )
		self.__pyStValue = StaticText( attrItem.stValue )
		self.__pyStValue.color = ( 255.0, 255.0, 255.0 )
		self.__pyStValue.text = ""

	def updateValue( self, value ):
		self.__pyStValue.text = str( value )

	def clearValue( self ):
		self.__pyStValue.text = ""

	def _getText( self ):
		return self.__pyStValue.text

	def _setText( self, text ):
		self.__pyStValue.text = text

	def _getTitle( self ):
		return self.__pyStTitle.text

	def _setTitle( self, title ):
		self.__pyStTitle.text = title

	def getStTitle( self ):
		return self.__pyStTitle

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	title = property( _getTitle, _setTitle )

class GuardAttr( PyGUI ):
	def __init__( self, attrItem ):
		PyGUI.__init__( self, attrItem )
		self.__pyStTitle = StaticText( attrItem.titleText )
		self.__pyStTitle.color = ( 236.0, 218.0, 157.0 )
		self.__pyStValue = StaticText( attrItem.stValue )
		self.__pyStValue.color = ( 255.0, 255.0, 255.0 )
		self.__pyStValue.text = ""

	def updateValue( self, value ):
		self.__pyStValue.text = str( value )

	def clearValue( self ):
		self.__pyStValue.text = ""

	def _getText( self ):
		return self.__pyStValue.text

	def _setText( self, text ):
		self.__pyStValue.text = text

	def _getTitle( self ):
		return self.__pyStTitle.text

	def _setTitle( self, title ):
		self.__pyStTitle.text = title

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	title = property( _getTitle, _setTitle )