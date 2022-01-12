# -*- coding: gb18030 -*-

import Math
import math
import Const
import Define
import csdefine
import BigWorld

from keys import *
from gbref import rds
from Function import Functor
from interface.GameObject import GameObject
from skills.SpellBase.Effect import createSuitableEffect
from LoadingAnimation import loadingAnimation
ACTION_JUMP_BEGIN   = ["jump_begin","jump_process"]
ACTION_JUMP_DOWN    = [ "jump_process" ]
ACTION_JUMP_END     = ["jump_end"]

class CameraEntity( GameObject ):
	"""
	This implements the CameraEntity on the Client
	"""
	def __init__( self ):
		GameObject.__init__( self )
		self.isAlwaysExist = False #是否一直存在，不受播放镜头时间影响
		self.utype = csdefine.ENTITY_TYPE_MISC
		
		self.model = None
		self.callback = None
		self.cbid  = 0  #移动中设置模型朝向回调句柄
		self.onWater = False #进入水域标记
		self.flyWaterTimerID = 0 #凌波微步光效回调句柄
		#以下为模拟坐骑
		self.modelSource = None
		self.hardPoint = None
		self.attachEffects = None
		self.enModel = None
		self.vehicelModel = None
		self.vehicleType = 0
		self.setSelectable( False )
		self.onMouseEnter = None #鼠标进入
		self.onMouseLeave = None #鼠标离开
		self.onClick = None
		self.emptyModel  = None #跳跃时为了修改朝向问题 附加模型
	
	def onTargetFocus( self ) :
		"""
		鼠标进入模型时被调用
		"""
		if callable( self.onMouseEnter ) :
			self.onMouseEnter( self )

	def onTargetBlur( self ) :
		"""
		鼠标离开模型时被调用
		"""
		if callable( self.onMouseLeave ) :
			self.onMouseLeave( self )
	
	def onTargetClick( self, sender ) :
		"""
		鼠标点击模型时被调用
		"""
		GameObject.onTargetClick( self, sender )
		if callable( self.onClick ) :
			self.onClick( self )

	def prerequisites( self ):
		prerequisit = []
		path = rds.npcModel.getModelSources( self.modelNumber )
		prerequisit.extend( path )
		return prerequisit

	def enterWorld( self ):
		# model
		if self.modelNumber :
			rds.npcModel.createDynamicModelBG( self.modelNumber, self.__onModelLoad )
		else:
			self.usePlayerModel()
	
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return
		## Action Match
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# 模型的RolePitchYaw和Entity保持一致
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			self.am.matchCaps = [Define.CAPS_DEFAULT]
			self.model.motors = ( self.am, )
		# physics
		BigWorld.controlEntity( self, True )
		self.resetPhysics()
		if self.model:
			self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

	def resetPhysics( self ):
		"""
		刷新physics
		"""
		self.physics = SIMPLE_PHYSICS
		self.physics.fall = self.isFall
		self.physics.lodDistance = 150.0
		self.physics.collide = True
		self.physics.setJumpEndFn( self.__jumpEnd )
		self.physics.setJumpUpFn( self.__jumpUp )
		self.physics.setJumpDownFn( self.__jumpDown )
	
	def __onModelLoad( self, model):
		"""
		模型加载完毕
		"""
		if model is None:
			return
		self.setModel( model )
		BigWorld.callback( 0.05, self.onCacheCompleted )
	
	def setModel( self, model ):
		"""
		设置模型
		"""
		if model:
			self.model = model
			self.model.position = self.position
			self.model.yaw = self.yaw
			if not self.isShow:
				self.model.visible = False
				self.model.visibleAttachments = False
			else:
				self.model.visible = True
				self.model.visibleAttachments = True
			self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )
			model.OnActionStart = self.onActionStart
			# 访问Node点
			self.accessNodes()
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# 模型的RolePitchYaw和Entity保持一致
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			self.am.matchCaps = [Define.CAPS_DEFAULT]
			self.model.motors = ( self.am, )
		# physics
		BigWorld.controlEntity( self, True )
	
	def accessNodes( self ):
		"""
		访问常用的Node点
		"""
		if not self.inWorld: return
		if self.model is None: return
		nodes = Const.MODEL_ACCESS_NODES
		nodes.append( "HP_right_hand_1" )
		for nodeName in nodes :
			try:
				self.model.node( nodeName )
			except:
				pass
	
	def onActionStart( self, actionName ):
		"""
		"""
		if not self.inWorld: return
		# 凌波微波水面效果触发
		self.onSwtichWaterParticle( actionName )
	
	def onSwtichWaterParticle( self, actionName ):
		"""
		触发水面移动效果
		"""
		if not self.onWater: return 
		phy = self.getPhysics()
		if not phy: return
		if not phy.canFloatOnWater:return
		if actionName in ( "run", "walk", Const.MODEL_ACTION_WATER_RUN, Const.MODEL_ACTION_WATER_RUN_DAN, Const.MODEL_ACTION_WATER_RUN_SHUANG, Const.MODEL_ACTION_WATER_RUN_FU, Const.MODEL_ACTION_WATER_RUN_CHANG ):
			if not self.flyWaterTimerID:
				self.startFlyWaterParticle()
		else:
			self.stopFlyWaterParticle()
	
	def getModel( self ):
		"""
		获得模型
		"""
		if self.vehicelModel:
			return self.enModel
		else:
			return self.model
	
	def usePlayerModel( self ):
		"""
		使用玩家的模型
		"""
		roleInfo = BigWorld.player().getModelInfo()
		self.modelScale = BigWorld.player().getModel().scale[0]
		func = Functor( self.onModelLoadCompleted, roleInfo )
		rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )

	def weaponAttachEffect( self, model, weaponDict ):
		"""
		武器附加属性效果
		@type		model 		: pyModel
		@param		model 		: 模型
		@type		weaponDict 	: FDict
		@param		weaponDict 	: 武器数据
		"""
		pType = Define.TYPE_PARTICLE_PLAYER
		# 模型Dyes
		dyes = rds.roleMaker.getMWeaponModelDyes( weaponDict )
		rds.effectMgr.createModelDye( model, dyes )
		# 自带光效
		weaponNum = weaponDict["modelNum"]

		effectIDs = rds.itemModel.getMEffects( weaponNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, pType, pType )
			effect.start()

		# 镶嵌光效
		stAmount = weaponDict["stAmount"]
		xqHp = rds.equipParticle.getXqHp( stAmount )
		xqGx = rds.equipParticle.getXqGx( stAmount )
		for hp, particle in zip( xqHp, xqGx ):
			rds.effectMgr.createParticleBG( model, hp, particle, type = pType )
		# 强化自发光
		intensifyLevel = weaponDict["iLevel"]
		if intensifyLevel >= Const.EQUIP_WEAPON_GLOW_LEVEL:
			paths = rds.roleMaker.getMWeaponModelPath( weaponDict )
			if len( paths ) == 0: return
			weaponKey = paths[0]
			type = rds.equipParticle.getWType( weaponKey )
			texture = rds.equipParticle.getWTexture( weaponKey )
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, intensifyLevel )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )
	
	def onCreateModelLoad( self, roleInfo, model ):
		"""
		角色创建画面的整个身体模型加载完回调
		"""
		def onLoadRightModel( rightModel ):
			def onRightLoftLoad( particle ):
				"""
				右手刀光加载完成
				"""
				if particle is None: return
				rds.effectMgr.attachObject( rightModel, loftHP, particle )
			
			self.weaponAttachEffect( rightModel, roleInfo.getRHFDict() ) 
			key = "HP_right_hand"
			rds.effectMgr.linkObject( model, key, rightModel )
			hps = []
			particles = []
			profession = roleInfo.getClass()
			if profession == csdefine.CLASS_SWORDMAN:
				loftHP = Const.LOFT_SWORDMAN_HP
				rds.effectMgr.pixieCreateBG( Const.LOFT_SWORDMAN, onRightLoftLoad )
			elif profession == csdefine.CLASS_FIGHTER:
				loftHP = Const.LOFT_FIGHTER_HP
				rds.effectMgr.pixieCreateBG( Const.LOFT_FIGHTER, onRightLoftLoad )
				hps = Const.ROLE_CREATE_FIGHTER_HP
				particles = Const.ROLE_CREATE_FIGHTER_PATH
			elif profession == csdefine.CLASS_MAGE:
				hps = Const.ROLE_CREATE_MAGE_HP
				particles = Const.ROLE_CREATE_MAGE_PATH
		
			#for hp, particle in zip( hps, particles ):
			#	rds.effectMgr.createParticleBG( rightModel, hp, particle, type = Define.TYPE_PARTICLE_PLAYER )
		
		def onLoadLeftModel( leftModel ):
			def onLeftLoftLoad( particle ):
				"""
				左手刀光加载完成
				"""
				if particle is None: return
				rds.effectMgr.attachObject( leftModel, loftHP, particle )
			self.weaponAttachEffect( leftModel, roleInfo.getLHFDict() ) 
			profession = roleInfo.getClass()
			key = "HP_left_shield"
			if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
				key = "HP_left_hand"
			rds.effectMgr.linkObject( model, key, leftModel )
		
			hps = []
			particles = []
			if profession == csdefine.CLASS_SWORDMAN:
				loftHP = Const.LOFT_SWORDMAN_HP
				rds.effectMgr.pixieCreateBG( Const.LOFT_SWORDMAN, onLeftLoftLoad )
			elif profession == csdefine.CLASS_ARCHER:
				hps = Const.ROLE_CREATE_ARCHER_HP
				particles = Const.ROLE_CREATE_ARCHER_PATH
		
			for hp, particle in zip( hps, particles ):
				rds.effectMgr.createParticleBG( leftModel, hp, particle, type = Define.TYPE_PARTICLE_PLAYER )
		
		def onHairModelLoad( hairModel ):
			key = "HP_head"
			rds.effectMgr.linkObject( model, key, hairModel )
		
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		
		# 发型
		rds.roleMaker.createHairModelBG( roleInfo.getHairNumber(), roleInfo.getFashionNum(), profession, gender, onHairModelLoad )
		# 左右手武器
		rds.roleMaker.createMWeaponModelBG( roleInfo.getRHFDict(), onLoadRightModel )
		rds.roleMaker.createMWeaponModelBG( roleInfo.getLHFDict(), onLoadLeftModel )
		# 发光
		bodyFDict = roleInfo.getBodyFDict()
		feetFDict = roleInfo.getFeetFDict()
		
		############胸部位置光效######################
		intensifyLevel = bodyFDict["iLevel"]
		# 绑定新的身体发射光芒效果(胸部装备强化至4星时出现)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		# 绑定新的各职业向上升光线(胸部装备强化至6星时出现)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		# 绑定新的身体周围盘旋上升光带( 胸部装备强化至9星时出现 )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		# 绑定新的龙型旋转光环( 胸部装备强化至9星时出现 )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
		###########鞋子光效#################################
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		
		# 法师特有粒子效果
		if roleInfo.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER  )

	def onModelLoadCompleted( self, roleInfo, model ):
		"""
		玩家模型加载回调
		"""
		self.onCreateModelLoad( roleInfo, model )
		self.setModel( model )
		player = BigWorld.player()
		if  player.vehicleModelNum and self.spaceID == loadingAnimation.getSpaceID():
			vehiclePaths = rds.itemModel.getMSource( player.vehicleModelNum )
			paths = {}
			paths[Define.MODEL_VEHICLE] = vehiclePaths
			rds.modelFetchMgr.fetchModels( 0, self.onVehicleModelLoad, paths )
		else:
			self.setAM()
	
	def setAM( self ):
		model = self.getModel()
		## Action Match
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# 模型的RolePitchYaw和Entity保持一致
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			self.am.matchCaps = [Define.CAPS_DEFAULT]
			model.motors = ( self.am, )
		# physics
		BigWorld.controlEntity( self, True )
		self.physics = SIMPLE_PHYSICS
		self.physics.fall = self.isFall
		self.physics.lodDistance = 150.0
		self.physics.collide = True
		if model:
			model.scale = ( self.modelScale, self.modelScale, self.modelScale )
	
	def  onVehicleModelLoad( self, modelDict ):
		"""
		骑宠和装备模型加载完成
		"""
		model = self.getModel()
		player = BigWorld.player()
		vehicleModelNum = player.vehicleModelNum
		# 骑宠模型
		vehicleModel = modelDict.get( Define.MODEL_VEHICLE )
		if vehicleModel is None:
			return
		# 设置骑宠相关值
		if hasattr( vehicleModel, Const.VEHICLE_HIP ):
			vehicleType = Define.VEHICLE_MODEL_HIP
			vehicleHP = Const.VEHICLE_HIP_HP
		if hasattr( vehicleModel, Const.VEHICLE_STAND ):
			vehicleType = Define.VEHICLE_MODEL_STAND
			vehicleHP = Const.VEHICLE_STAND_HP
		if hasattr( vehicleModel, Const.VEHICLE_PAN ):
			vehicleType = Define.VEHICLE_MODEL_PAN
			vehicleHP = Const.VEHICLE_PAN_HP

		# 骑宠dye、粒子
		dyes = rds.itemModel.getMDyes( vehicleModelNum )
		rds.effectMgr.createModelDye( vehicleModel, dyes )
		effectIDs = rds.itemModel.getMEffects( vehicleModelNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, vehicleModel, vehicleModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
			effect.start()
		self.setModel( vehicleModel )
		rds.effectMgr.linkObject( vehicleModel, vehicleHP, model )
		self.playVehicleAction( model )

	def playVehicleAction( self, model, actionName = None ):
		"""
		播放对应动作
		"""
		if actionName == None:
			actionName = loadingAnimation.actionName
		rds.actionMgr.playAction( model, actionName )
	
	def leaveWorld( self ):
		self.model = None
		
		
	def setLodDistance( self, distance ):
		"""
		设置physics的lodDistance
		用于实现远距离（距离玩家）移动行为
		"""
		if not self.physics: return
		self.physics.lodDistance = distance
		

	def moveTo( self, position, speed = 0, moveFace = True ,jumpAction = "", jumpTime = 0.0, callback = None ) :
		"""
		seek to anywhere
		@type		position 		: tuple
		@param		position 		: destination position
		@type		nearby			: float
		@param		nearby			: how far close to the psotion
		@return				 		: None
		"""
		self.stopMove()
		#跳跃处理
		if jumpAction != "":
			self.physics.doJump( jumpTime,0.0 )
			rds.actionMgr.playAction( self.getModel(), jumpAction )
		
		distance = ( position - self.position ).length
		if speed != 0:
			self.moveSpeed = speed
		timeout = 1.5 * distance / self.moveSpeed
		# 计算yaw
		position = Math.Vector3( position )
		if moveFace:
			yaw = ( position - self.position ).yaw
		else:
			self.am.turnModelToEntity = False
			yaw = ( self.position - position ).yaw
			self.model.yaw = yaw
			BigWorld.callback( 0.001, Functor( self.setModelYaw, yaw ))
		self.callback = callback
		self.updateVelocity( True )
		self.physics.seek( ( position[0], position[1], position[2], yaw ), timeout, 10, self.onEndSeek )
		self.onSwitchVehicle( "run" )
		
	def onEndSeek(self, state):
		if not self.inWorld: return
		BigWorld.cancelCallback( self.cbid  )
		self.am.turnModelToEntity = True
		self.updateVelocity( False )
		if callable(self.callback):
			self.callback()
		self.onSwitchVehicle( Const.MODEL_ACTION_STAND )
		
	def setModelYaw( self, yaw ):
		"""
		设置模型的朝向
		"""
		if not self.inWorld: return
		if not self.model: return
		self.model.yaw = yaw
		self.cbid = BigWorld.callback( 0.001, Functor( self.setModelYaw, yaw ))

	def updateVelocity( self, isMove ):
		"""
		"""
		if not isMove:
			self.physics.velocity = ( 0, 0, 0 )
			return

		self.physics.velocity = ( 0, 0, self.moveSpeed )
		
	def setSpeed( self, speed ) :
		"""
		设置移动速度
		@type			speed  : float
		@param			speed  : 速度值
		"""
		self.moveSpeed = speed
		
	def stopMove( self ):
		"""
		"""
		if not self.inWorld: return
		BigWorld.cancelCallback( self.cbid  )
		if not self.physics: return
		if self.physics.seeking:
			self.physics.seek( None, 0, 0, None )
		self.physics.stop()
		
	def turnRound( self, yaw ):
		"""
		设置yaw
		"""
		self.stopMove()
		direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) ) 
		direction.normalise()
		dstPos = self.position + direction * 0.1
		self.moveTo( dstPos, 0.2 )
		
	def turnaround( self, matrix ):
		"""
		转向某个实体
		"""
		self.stopMove()
		dstPos = Math.Matrix( matrix ).applyToOrigin()
		dir = dstPos - self.position
		self.turnRound( dir.yaw )
		
	def showModel( self ):
		"""
		显示模型
		"""
		if self.model:
			self.model.visible = True
			self.model.visibleAttachments = True

	def hideModel( self ):
		"""
		隐藏模型
		"""
		if self.model:
			self.model.visible = False
			self.model.visibleAttachments = False
	
	def setFall( self, isFall):
		"""
		设置其physics.fall
		"""
		self.isFall = isFall
		self.physics.fall = self.isFall
	
	def setFloatOnWater( self, canF ):
		"""
		设置是否浮在水上
		"""
		self.physics.canFloatOnWater = canF
		self.switchFlyWater( canF )
	
	def jump( self, speed, jumpAction, jumpTime ):
		"""
		跳跃
		"""
		self.physics.fall = True
		self.physics.canFloatOnWater = False
		self.physics.velocity = ( 0, speed, 0 )
		self.physics.doJump( jumpTime, 0.0 )
		self.model.action( jumpAction )()

	def stopJump( self, isFall = True ):
		"""
		停止跳跃
		"""
		self.physics.velocity = ( 0, 0, 0 )
		self.setFall( isFall )

	def switchFlyWater( self, switch ):
		"""
		身轻如燕开关
		"""
		if self.physics is None: return
		if switch:
			if self.am:
				self.am.matchCaps = [ Define.CAPS_DEFAULT, Define.CAPS_FLY_WATER ]
			callback = self.floatOnWaterCallback
		else:
			if self.am:
				self.am.matchCaps = [ Define.CAPS_DEFAULT ]
			callback = None
			self.onWater = False
			self.floatOnWaterAreaCallback( False )

		# 先设置回调函数，再设置canFloatOnWater
		self.physics.setFloatOnWaterCallbackFn( callback )
		self.physics.canFloatOnWater = switch

	def floatOnWaterCallback( self, switch ):
		"""
		进出水面回调
		"""
		self.onWater = switch
		if switch:
			self.switchFlyWaterParticle()
			if not self.flyWaterTimerID:
				self.startFlyWaterParticle()
		else:
			self.stopFlyWaterParticle()

	def startFlyWaterParticle( self ):
		"""
		开始水面粒子效果
		"""
		if not self.inWorld: return
		if not self.onWater: return 
		if self.physics is None: return
		self.switchFlyWaterParticle()
		self.flyWaterTimerID = BigWorld.callback( Const.JUMP_WATER_EFFECT_TIME, self.startFlyWaterParticle )
	
	def stopFlyWaterParticle( self ):
		"""
		关闭水面粒子效果
		"""
		if not self.inWorld: return
		BigWorld.cancelCallback( self.flyWaterTimerID )
		self.flyWaterTimerID = 0
	
	def switchFlyWaterParticle( self ):
		"""
		触发水面移动效果
		"""
		if not self.onWater: return 
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.JUMP_WATER_EFFECTID, self.model, self.model, type, type )
		if effect is None: return
		effect.start()

	def setJumpPhysics( self ):
		"""
		设置physics为和玩家一样的physics
		"""
		self.physics = STANDARD_PHYSICS
		self.physics.collide = 1
		self.physics.fall = 1
		self.physics.gravity = 9.8
		self.physics.setJumpEndFn( self.__jumpEnd )
		self.physics.setJumpUpFn( self.__jumpUp )
		self.physics.setJumpDownFn( self.__jumpDown )

	def getPhysics( self ):
		"""
		获取角色的 physics
		"""
		if hasattr( self, "physics" ):
			return self.physics
		return None
	
	def simulateJump( self, height, height0, dis, yaw = 0.0 ):
		"""
		模拟玩家跳跃
		@type		height:	float
		@param		height: 向上的垂直距离
		@type		height:	float
		@param		height: 落下的垂直距离
		@type		dis:	float
		@param		dis:	跳跃的水平距离
		"""
		if not self.inWorld:return
		if yaw == 0.0:
			yaw = self.yaw
		model = self.getModel()
		if not model:return
		self.emptyModel = BigWorld.Model( model.sources[0])
		self.getModel().root.attach( self.emptyModel )
		model.visible = False
		self.emptyModel.canRotate = True
		self.emptyModel.yaw = yaw
		self.setJumpPhysics()
		jumpV = math.sqrt( height * 2 * self.physics.gravity )
		self.physics.doJump( jumpV,0.0 )
		y = yaw
		a1 = math.sin( y )
		a2 = math.cos( y )
		t0 = math.sqrt( height * 2 / self.physics.gravity ) #到最高点所需时间
		t1 = math.sqrt( height0 * 2 / self.physics.gravity )
		V0 = dis / ( t0 + t1 )
		self.physics.velocity = ( a1 * V0 , 0, a2 * V0 ) #速度分解
		
	def __jumpUp( self ):
		"""
		跳跃上升中
		"""
		if self.emptyModel:
			rds.actionMgr.playActions( self.emptyModel, ACTION_JUMP_BEGIN )
	
	def __jumpDown( self ):
		"""
		下落中
		"""
		if self.emptyModel:
			rds.actionMgr.playActions( self.emptyModel, ACTION_JUMP_DOWN )
	
	def __jumpEnd( self ):
		"""
		跳跃结束
		"""
		if self.emptyModel:
			rds.actionMgr.playActions( self.emptyModel, ACTION_JUMP_END )

	def stopSimulateJump( self ):
		self.physics.stop()
		self.resetPhysics()
		model =  self.getModel()
		if model :
			model.visible = True
			model.root.detach( self.emptyModel )
		self.emptyModel = None
		
	def upVehicle( self, effectID, cb=None ):
		"""
		模拟上坐骑
		effectID：带有坐骑模型的光效ID
		"""
		dict = rds.spellEffect.getEffectConfigDict( effectID )
		self.modelSource = dict.get( "particle_msource", "" )
		self.hardPoint = dict.get( "particle_hardpoint", "" )
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )# 模型附加配置
		rds.effectMgr.createModelBG( [self.modelSource], Functor( self.__onLoadVehicleModel, cb ) )
	
	def __onLoadVehicleModel( self, cb, model ):
		"""
		坐骑模型加载完毕
		"""
		if not model:return
		self.enModel = self.getModel()
		self.vehicelModel = model
		for effectID in self.attachEffects:											# 在后线程创建模型的附加光效
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# 获取配置数据
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.enModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )	# 创建效果实例
			if particlesEffect is None: continue
			particlesEffect.start()# 播放效果
		self.enModel.root.attach( self.vehicelModel )
		self.vehicelModel.yaw = self.yaw
		rds.actionMgr.playAction( self.vehicelModel, Const.MODEL_ACTION_STAND )
		rds.effectMgr.fadeInModel( self.vehicelModel, 1.0 )
		rds.actionMgr.playActions( self.enModel, [Const.MODEL_ACTION_RIDE_UP, Const.MODEL_ACTION_RIDE_UP_OVER], callbacks = [Functor(self.onUpFlyVehicleOver,cb)] )
		#if model.hasAction( Const.MODEL_ACTION_PLAY ):
		#	rds.actionMgr.playAction( model, Const.MODEL_ACTION_PLAY )
		
		
	def onUpFlyVehicleOver( self, cb ):
		"""
		上坐骑动作完成
		"""
		if not self.enModel:return
		if not self.vehicelModel:return
		self.enModel.root.detach( self.vehicelModel )
		self.setModel( self.vehicelModel )
		rds.effectMgr.attachObject( self.vehicelModel, self.hardPoint, self.enModel )
		self.vehicleType = Define.VEHICLE_MODEL_STAND
		self.onSwitchVehicle( Const.MODEL_ACTION_STAND )
	
	def downVehicle( self, fall = True, cb = None  ):
		"""
		下坐骑
		"""
		if not self.vehicelModel:return
		if not self.enModel:return
		self.isFall = fall
		self.resetPhysics()
		rds.effectMgr.detachObject( self.vehicelModel, self.hardPoint, self.enModel )
		self.vehicelModel.motors = ()
		self.setModel( self.enModel )
		self.addModel( self.vehicelModel )
		self.vehicelModel.yaw = self.yaw
		self.vehicelModel.position = self.position
		rds.effectMgr.fadeOutModel( self.vehicelModel, 1.0 )
		rds.actionMgr.playActions( self.enModel, [Const.MODEL_ACTION_RIDE_DOWN, Const.MODEL_ACTION_RIDE_DOWN_OVER], callbacks = [ None, Functor( self.onDownFlyVehiclePoseOver,  cb ) ] )
	
	def onDownFlyVehiclePoseOver( self, cb ):
		"""
		下坐骑完成回调
		"""
		self.delModel( self.vehicelModel )
		self.modelSource = None
		self.hardPoint = None
		self.attachEffects = None
		self.enModel = None
		self.vehicelModel = None
		self.vehicleType = 0
		if callable( cb ):
			cb()
		
	def onSwitchVehicle( self, actionName ):
		"""
		骑宠动作触发
		"""
		if not self.vehicelModel: return
			
		if actionName not in Const.VEHICLE_ACTION_MAPS: return
		
		model = self.getModel()
		if model is None: return
		
		p = BigWorld.player()
		for action in model.queue:
			if "random" in action and "float" in action:
				rds.actionMgr.stopAction( model, action )
		
		index = 0
		if self.vehicleType == Define.VEHICLE_MODEL_HIP:
			index = 0
		elif self.vehicleType == Define.VEHICLE_MODEL_PAN:
			index = 1
		elif self.vehicleType == Define.VEHICLE_MODEL_STAND:
			index = 2
		
		caps = p.am.matchCaps
		if Define.CAPS_WEAPON in caps:
			weaponIndex = 1
		elif Define.CAPS_DAN_WEAPON in caps:
			weaponIndex = 2
		elif Define.CAPS_SHUANG_WEAPON in caps:
			weaponIndex = 3
		elif Define.CAPS_FU_WEAPON in caps:
			weaponIndex = 4
		elif Define.CAPS_CHANG_WEAPON in caps:
			weaponIndex = 5
		else:
			weaponIndex = 0
		
		roleActionName = Const.VEHICLE_ACTION_MAPS[actionName][weaponIndex][index]
		rds.actionMgr.playAction( model, roleActionName )

