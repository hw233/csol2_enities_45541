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
		self.isAlwaysExist = False #�Ƿ�һֱ���ڣ����ܲ��ž�ͷʱ��Ӱ��
		self.utype = csdefine.ENTITY_TYPE_MISC
		
		self.model = None
		self.callback = None
		self.cbid  = 0  #�ƶ�������ģ�ͳ���ص����
		self.onWater = False #����ˮ����
		self.flyWaterTimerID = 0 #�貨΢����Ч�ص����
		#����Ϊģ������
		self.modelSource = None
		self.hardPoint = None
		self.attachEffects = None
		self.enModel = None
		self.vehicelModel = None
		self.vehicleType = 0
		self.setSelectable( False )
		self.onMouseEnter = None #������
		self.onMouseLeave = None #����뿪
		self.onClick = None
		self.emptyModel  = None #��ԾʱΪ���޸ĳ������� ����ģ��
	
	def onTargetFocus( self ) :
		"""
		������ģ��ʱ������
		"""
		if callable( self.onMouseEnter ) :
			self.onMouseEnter( self )

	def onTargetBlur( self ) :
		"""
		����뿪ģ��ʱ������
		"""
		if callable( self.onMouseLeave ) :
			self.onMouseLeave( self )
	
	def onTargetClick( self, sender ) :
		"""
		�����ģ��ʱ������
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
		EntityCache�������
		"""
		if not self.inWorld:
			return
		## Action Match
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# ģ�͵�RolePitchYaw��Entity����һ��
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
		ˢ��physics
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
		ģ�ͼ������
		"""
		if model is None:
			return
		self.setModel( model )
		BigWorld.callback( 0.05, self.onCacheCompleted )
	
	def setModel( self, model ):
		"""
		����ģ��
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
			# ����Node��
			self.accessNodes()
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# ģ�͵�RolePitchYaw��Entity����һ��
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			self.am.matchCaps = [Define.CAPS_DEFAULT]
			self.model.motors = ( self.am, )
		# physics
		BigWorld.controlEntity( self, True )
	
	def accessNodes( self ):
		"""
		���ʳ��õ�Node��
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
		# �貨΢��ˮ��Ч������
		self.onSwtichWaterParticle( actionName )
	
	def onSwtichWaterParticle( self, actionName ):
		"""
		����ˮ���ƶ�Ч��
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
		���ģ��
		"""
		if self.vehicelModel:
			return self.enModel
		else:
			return self.model
	
	def usePlayerModel( self ):
		"""
		ʹ����ҵ�ģ��
		"""
		roleInfo = BigWorld.player().getModelInfo()
		self.modelScale = BigWorld.player().getModel().scale[0]
		func = Functor( self.onModelLoadCompleted, roleInfo )
		rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )

	def weaponAttachEffect( self, model, weaponDict ):
		"""
		������������Ч��
		@type		model 		: pyModel
		@param		model 		: ģ��
		@type		weaponDict 	: FDict
		@param		weaponDict 	: ��������
		"""
		pType = Define.TYPE_PARTICLE_PLAYER
		# ģ��Dyes
		dyes = rds.roleMaker.getMWeaponModelDyes( weaponDict )
		rds.effectMgr.createModelDye( model, dyes )
		# �Դ���Ч
		weaponNum = weaponDict["modelNum"]

		effectIDs = rds.itemModel.getMEffects( weaponNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, pType, pType )
			effect.start()

		# ��Ƕ��Ч
		stAmount = weaponDict["stAmount"]
		xqHp = rds.equipParticle.getXqHp( stAmount )
		xqGx = rds.equipParticle.getXqGx( stAmount )
		for hp, particle in zip( xqHp, xqGx ):
			rds.effectMgr.createParticleBG( model, hp, particle, type = pType )
		# ǿ���Է���
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
		��ɫ�����������������ģ�ͼ�����ص�
		"""
		def onLoadRightModel( rightModel ):
			def onRightLoftLoad( particle ):
				"""
				���ֵ���������
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
				���ֵ���������
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
		
		# ����
		rds.roleMaker.createHairModelBG( roleInfo.getHairNumber(), roleInfo.getFashionNum(), profession, gender, onHairModelLoad )
		# ����������
		rds.roleMaker.createMWeaponModelBG( roleInfo.getRHFDict(), onLoadRightModel )
		rds.roleMaker.createMWeaponModelBG( roleInfo.getLHFDict(), onLoadLeftModel )
		# ����
		bodyFDict = roleInfo.getBodyFDict()
		feetFDict = roleInfo.getFeetFDict()
		
		############�ز�λ�ù�Ч######################
		intensifyLevel = bodyFDict["iLevel"]
		# ���µ����巢���âЧ��(�ز�װ��ǿ����4��ʱ����)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		# ���µĸ�ְҵ����������(�ز�װ��ǿ����6��ʱ����)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		# ���µ�������Χ�����������( �ز�װ��ǿ����9��ʱ���� )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		# ���µ�������ת�⻷( �ز�װ��ǿ����9��ʱ���� )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
		###########Ь�ӹ�Ч#################################
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		
		# ��ʦ��������Ч��
		if roleInfo.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER  )

	def onModelLoadCompleted( self, roleInfo, model ):
		"""
		���ģ�ͼ��ػص�
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
			# ģ�͵�RolePitchYaw��Entity����һ��
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
		����װ��ģ�ͼ������
		"""
		model = self.getModel()
		player = BigWorld.player()
		vehicleModelNum = player.vehicleModelNum
		# ���ģ��
		vehicleModel = modelDict.get( Define.MODEL_VEHICLE )
		if vehicleModel is None:
			return
		# ����������ֵ
		if hasattr( vehicleModel, Const.VEHICLE_HIP ):
			vehicleType = Define.VEHICLE_MODEL_HIP
			vehicleHP = Const.VEHICLE_HIP_HP
		if hasattr( vehicleModel, Const.VEHICLE_STAND ):
			vehicleType = Define.VEHICLE_MODEL_STAND
			vehicleHP = Const.VEHICLE_STAND_HP
		if hasattr( vehicleModel, Const.VEHICLE_PAN ):
			vehicleType = Define.VEHICLE_MODEL_PAN
			vehicleHP = Const.VEHICLE_PAN_HP

		# ���dye������
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
		���Ŷ�Ӧ����
		"""
		if actionName == None:
			actionName = loadingAnimation.actionName
		rds.actionMgr.playAction( model, actionName )
	
	def leaveWorld( self ):
		self.model = None
		
		
	def setLodDistance( self, distance ):
		"""
		����physics��lodDistance
		����ʵ��Զ���루������ң��ƶ���Ϊ
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
		#��Ծ����
		if jumpAction != "":
			self.physics.doJump( jumpTime,0.0 )
			rds.actionMgr.playAction( self.getModel(), jumpAction )
		
		distance = ( position - self.position ).length
		if speed != 0:
			self.moveSpeed = speed
		timeout = 1.5 * distance / self.moveSpeed
		# ����yaw
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
		����ģ�͵ĳ���
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
		�����ƶ��ٶ�
		@type			speed  : float
		@param			speed  : �ٶ�ֵ
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
		����yaw
		"""
		self.stopMove()
		direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) ) 
		direction.normalise()
		dstPos = self.position + direction * 0.1
		self.moveTo( dstPos, 0.2 )
		
	def turnaround( self, matrix ):
		"""
		ת��ĳ��ʵ��
		"""
		self.stopMove()
		dstPos = Math.Matrix( matrix ).applyToOrigin()
		dir = dstPos - self.position
		self.turnRound( dir.yaw )
		
	def showModel( self ):
		"""
		��ʾģ��
		"""
		if self.model:
			self.model.visible = True
			self.model.visibleAttachments = True

	def hideModel( self ):
		"""
		����ģ��
		"""
		if self.model:
			self.model.visible = False
			self.model.visibleAttachments = False
	
	def setFall( self, isFall):
		"""
		������physics.fall
		"""
		self.isFall = isFall
		self.physics.fall = self.isFall
	
	def setFloatOnWater( self, canF ):
		"""
		�����Ƿ���ˮ��
		"""
		self.physics.canFloatOnWater = canF
		self.switchFlyWater( canF )
	
	def jump( self, speed, jumpAction, jumpTime ):
		"""
		��Ծ
		"""
		self.physics.fall = True
		self.physics.canFloatOnWater = False
		self.physics.velocity = ( 0, speed, 0 )
		self.physics.doJump( jumpTime, 0.0 )
		self.model.action( jumpAction )()

	def stopJump( self, isFall = True ):
		"""
		ֹͣ��Ծ
		"""
		self.physics.velocity = ( 0, 0, 0 )
		self.setFall( isFall )

	def switchFlyWater( self, switch ):
		"""
		�������࿪��
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

		# �����ûص�������������canFloatOnWater
		self.physics.setFloatOnWaterCallbackFn( callback )
		self.physics.canFloatOnWater = switch

	def floatOnWaterCallback( self, switch ):
		"""
		����ˮ��ص�
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
		��ʼˮ������Ч��
		"""
		if not self.inWorld: return
		if not self.onWater: return 
		if self.physics is None: return
		self.switchFlyWaterParticle()
		self.flyWaterTimerID = BigWorld.callback( Const.JUMP_WATER_EFFECT_TIME, self.startFlyWaterParticle )
	
	def stopFlyWaterParticle( self ):
		"""
		�ر�ˮ������Ч��
		"""
		if not self.inWorld: return
		BigWorld.cancelCallback( self.flyWaterTimerID )
		self.flyWaterTimerID = 0
	
	def switchFlyWaterParticle( self ):
		"""
		����ˮ���ƶ�Ч��
		"""
		if not self.onWater: return 
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.JUMP_WATER_EFFECTID, self.model, self.model, type, type )
		if effect is None: return
		effect.start()

	def setJumpPhysics( self ):
		"""
		����physicsΪ�����һ����physics
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
		��ȡ��ɫ�� physics
		"""
		if hasattr( self, "physics" ):
			return self.physics
		return None
	
	def simulateJump( self, height, height0, dis, yaw = 0.0 ):
		"""
		ģ�������Ծ
		@type		height:	float
		@param		height: ���ϵĴ�ֱ����
		@type		height:	float
		@param		height: ���µĴ�ֱ����
		@type		dis:	float
		@param		dis:	��Ծ��ˮƽ����
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
		t0 = math.sqrt( height * 2 / self.physics.gravity ) #����ߵ�����ʱ��
		t1 = math.sqrt( height0 * 2 / self.physics.gravity )
		V0 = dis / ( t0 + t1 )
		self.physics.velocity = ( a1 * V0 , 0, a2 * V0 ) #�ٶȷֽ�
		
	def __jumpUp( self ):
		"""
		��Ծ������
		"""
		if self.emptyModel:
			rds.actionMgr.playActions( self.emptyModel, ACTION_JUMP_BEGIN )
	
	def __jumpDown( self ):
		"""
		������
		"""
		if self.emptyModel:
			rds.actionMgr.playActions( self.emptyModel, ACTION_JUMP_DOWN )
	
	def __jumpEnd( self ):
		"""
		��Ծ����
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
		ģ��������
		effectID����������ģ�͵Ĺ�ЧID
		"""
		dict = rds.spellEffect.getEffectConfigDict( effectID )
		self.modelSource = dict.get( "particle_msource", "" )
		self.hardPoint = dict.get( "particle_hardpoint", "" )
		self.attachEffects = dict.get( "particle_mparticle", "" ).split( ";" )# ģ�͸�������
		rds.effectMgr.createModelBG( [self.modelSource], Functor( self.__onLoadVehicleModel, cb ) )
	
	def __onLoadVehicleModel( self, cb, model ):
		"""
		����ģ�ͼ������
		"""
		if not model:return
		self.enModel = self.getModel()
		self.vehicelModel = model
		for effectID in self.attachEffects:											# �ں��̴߳���ģ�͵ĸ��ӹ�Ч
			if effectID == "": continue
			childSect = rds.spellEffect.getEffectConfigSect( effectID )				# ��ȡ��������
			if childSect is None: continue
			particlesEffect = createSuitableEffect( childSect, model, self.enModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )	# ����Ч��ʵ��
			if particlesEffect is None: continue
			particlesEffect.start()# ����Ч��
		self.enModel.root.attach( self.vehicelModel )
		self.vehicelModel.yaw = self.yaw
		rds.actionMgr.playAction( self.vehicelModel, Const.MODEL_ACTION_STAND )
		rds.effectMgr.fadeInModel( self.vehicelModel, 1.0 )
		rds.actionMgr.playActions( self.enModel, [Const.MODEL_ACTION_RIDE_UP, Const.MODEL_ACTION_RIDE_UP_OVER], callbacks = [Functor(self.onUpFlyVehicleOver,cb)] )
		#if model.hasAction( Const.MODEL_ACTION_PLAY ):
		#	rds.actionMgr.playAction( model, Const.MODEL_ACTION_PLAY )
		
		
	def onUpFlyVehicleOver( self, cb ):
		"""
		�����ﶯ�����
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
		������
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
		��������ɻص�
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
		��趯������
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

