# -*- coding: gb18030 -*-
#
# $Id: FittingPanel.py,fangpengjun Exp $

"""
implement FittingPanel class

"""

from gbref import rds
from bwdebug import *
from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from FittingModelRender import FittingModelRender
from AbstractTemplates import Singleton
from LabelGather import labelGather
import csdefine
import Define
import Const
from Function import Functor

class FittingPanel(Singleton, Window ):

	__cc_role_config = "config/client/uimodel_configs/role.py" #时装试衣模型配置
	__cc_vehicle_config = "config/client/uimodel_configs/vehicle.py" #骑宠试骑模型配置

	def __init__( self ):
		fitWnd = GUI.load( "guis/general/specialshop/fittingwnd.gui" )
		uiFixer.firstLoadFix( fitWnd )
		Window.__init__( self, fitWnd )
		self.__turnModelCBID = 0
		self.itemModelID = 0
		self.__pyShutBtn = HButtonEx( fitWnd.shutBtn )
		self.__pyShutBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyShutBtn.onLClick.bind( self.__onShut )

		self.__pyLeftBtn = Button( fitWnd.leftBtn )
		self.__pyLeftBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyLeftBtn.onLMouseDown.bind( self.__onTurnLeft )

		self.__pyRightBtn = Button( fitWnd.rightBtn )
		self.__pyRightBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRightBtn.onLMouseDown.bind( self.__onTurnRight )

		self.__modelRender = FittingModelRender( fitWnd.modelRender )
		self.__modelRender.setModel( None )
		self.__modelRender.onModelChanged.bind( self.__onModelChange )

		self.addToMgr( "fittingPanel" )

		self.__roleDatas = gbref.PyConfiger().read( self.__cc_role_config, {} ) #角色时装配置
		self.__vehicleDatas = gbref.PyConfiger().read( self.__cc_vehicle_config, {} )

		# 试衣间当前加载模型
		self.__currLoadID = 0

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyShutBtn, "SpecialShop:FittingPanel", "shutBtn" )
		labelGather.setLabel( fitWnd.lbTitle, "SpecialShop:FittingPanel", "lbTitle" )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_FittingPanel :
			INFO_MSG( str( self ) )

	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __onTurnRight( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __onTurnLeft( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		turning model on the mirror
		"""
		self.__modelRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	def __onShut( self ):
		self.hide()

	def __onModelChange( self, model ):
		viewInfo = None
		if self.itemModelID != 0: #为骑宠模型
			viewInfo = self.__vehicleDatas.get( self.itemModelID, None )
		else:
			profession = BigWorld.player().getClass()
			viewInfo = self.__roleDatas.get( profession, None )
		if viewInfo:
			self.__modelRender.modelPos = viewInfo["position"]
			self.__modelRender.pitch = viewInfo["pitch"]

	# ---------------------------------------------------
	# public
	# ---------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		pass

	def resetModelAngle( self ) :
		"""
		turning model on the mirror
		"""
		self.__modelRender.yaw = 0

	def addNewModel( self, equipItem ):
		"""
		试衣, 时装
		时装，脸 组成模型
		"""
		player = BigWorld.player()
		if player is None: return
		if equipItem is None: return
		fashionNum = equipItem.model()
		if self.__currLoadID == fashionNum: return
		self.__currLoadID = fashionNum

		def onEquipModelLoad( modelDict ):
			"""
			试衣模型加载完毕
			"""
			if self.__currLoadID != fashionNum: return
			self.itemModelID = 0

			mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
			if mainModel is None: return
			hairModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
			rds.effectMgr.linkObject( mainModel, Const.MODEL_HAIR_HP, hairModel )
			#效果
			dyes = rds.roleMaker.getFashionModelDyes( fashionNum, gender, profession )
			rds.effectMgr.createModelDye( mainModel, dyes )
			effectIDs = rds.itemModel.getSEffects( fashionNum, gender, profession )
			for effectID in effectIDs:
				dictData = rds.spellEffect.getEffectConfigDict( effectID )
				if len( dictData ) == 0: continue
				effect = rds.skillEffect.createEffect( dictData, fashionModel, fashionModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
				effect.start()
			
			self.__modelRender.setModel( mainModel )

		# 职业性别
		profession = player.getClass()
		gender = player.getGender()

		paths = {}
		mainPaths = []
		# 脸
		faceNum = player.faceNumber
		facePaths = rds.roleMaker.getFaceModelPath( faceNum, profession, gender )
		mainPaths.extend( facePaths )
		# 时装
		fashionPaths = rds.roleMaker.getFashionModelPath( fashionNum, gender, profession )
		mainPaths.extend( fashionPaths )
		if len( mainPaths ):
			paths[Define.MODEL_EQUIP_MAIN] = mainPaths
		# 头发
		hairPaths = rds.roleMaker.getHairModelPath( player.hairNumber, fashionNum, profession, gender )
		if len( hairPaths ):
			paths[Define.MODEL_EQUIP_HEAD] = hairPaths
		rds.modelFetchMgr.fetchModels( player.id, onEquipModelLoad, paths )


	@staticmethod
	def instance():
		return FittingPanel.inst


	def addVehicleModel( self, vehicleItem ):
		"""
		试骑骑宠类的模型
		"""
		if vehicleItem is None: return
		modelNum = vehicleItem.model()
		self.itemModelID = modelNum
		player = BigWorld.player()
		if player is None: return

		rds.itemModel.createModelBG( modelNum, Functor( self.__onVehicleModelLoad, modelNum ) )

	def __onVehicleModelLoad( self, itemModelID, vehicleModel ):
		"""
		后线程骑宠模型加载完成回调
		"""
		if vehicleModel is None: return
		
		effectIDs = rds.itemModel.getMEffects( itemModelID )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, vehicleModel, vehicleModel, Define.TYPE_PARTICLE_PLAYER,  Define.TYPE_PARTICLE_PLAYER )
			effect.start()


		player = BigWorld.player()
		if player is None: return
		self.__modelRender.setModel( vehicleModel )
		profession = player.getClass()
		gender = player.getGender()
		def callback( playerModel ):
			def onHairModelLoad( hairModel ):
				if hairModel is None: return
				rds.effectMgr.linkObject( playerModel, Const.MODEL_HAIR_HP, hairModel )
			hairNum = player.hairNumber
			fashionNum = player.fashionNum
			rds.roleMaker.createHairModelBG( hairNum, fashionNum, profession, gender, onHairModelLoad )

			def createLWeapon( leftWeapon ): #左手武器
				player.weaponAttachEffect( leftWeapon, player.lefthandFDict )
				key = Const.MODEL_LEFT_SHIELD_HP
				if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
					key = Const.MODEL_LEFT_HAND_HP
				rds.effectMgr.linkObject( playerModel, key, leftWeapon )

			lefthandFDict = player.lefthandFDict
			rds.roleMaker.createMWeaponModelBG( lefthandFDict, createLWeapon )

			def createRWeapon( rightWeapon ): #右手武器
				player.weaponAttachEffect( rightWeapon, player.righthandFDict )
				key = Const.MODEL_RIGHT_HAND_HP
				rds.effectMgr.linkObject( playerModel, key, rightWeapon )

			righthandFDict = player.righthandFDict
			rds.roleMaker.createMWeaponModelBG( righthandFDict, createRWeapon )
			if playerModel:
				if hasattr( vehicleModel, Const.VEHICLE_HIP ):
					key = Const.VEHICLE_HIP_HP
					actionName = Const.MODEL_ACTION_RIDE_STAND
				elif hasattr( vehicleModel, Const.VEHICLE_PAN ):
					key = Const.VEHICLE_PAN_HP
					actionName = Const.MODEL_ACTION_CROSSLEG_STAND
				else:
					key = Const.VEHICLE_STAND_HP
					actionName = Const.MODEL_ACTION_FLOAT_STAND
					vehicleModel.scale = ( 0.7, 0.7, 0.7 )	# CSOL-1976飞行骑宠模型缩小比例为0.7
				rds.effectMgr.linkObject( vehicleModel, key, playerModel )
				rds.actionMgr.playAction( playerModel, actionName )

		modelInfo = player.getModelInfo()
		rds.roleMaker.createPartModelBG( player.id, modelInfo, callback )

	def show( self, pyOwner ):
		self.pyBinder = pyOwner
		self.top = pyOwner.top
		self.left = pyOwner.right
		self.__modelRender.enableDrawModel()
		Window.show( self, pyOwner )

	def hide( self ):
		self.pyBinder = None
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__modelRender.disableDrawModel()
		self.__modelRender.setModel( None )
		self.itemModelID = 0
		self.__currLoadID = 0
		Window.hide( self )
		self.removeFromMgr()
		self.__class__.releaseInst()
