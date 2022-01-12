# -*- coding: gb18030 -*-

# $Id: PreviewRole.py,v 1.26 2008-08-20 01:47:08 yangkai Exp $


"""
candidate role, model only exists in client
-- 2006/04/21 written by wanhp( the old name Candidate )
-- 2006/08/25 modified by huangyongwei
-- 2007/02/30 rewriten by huangyongwei( from Candidate renamed to PreviewRole )
"""

import copy
import math
import BigWorld
import Math
import csdefine
import Define
import ItemTypeEnum as ITE
import event.EventCenter as ECenter
from bwdebug import *
from keys import *
from gbref import rds
from interface.GameObject import GameObject
from Function import Functor
import Const
import random
import Pixie

# --------------------------------------------------------------------
# global methods
# --------------------------------------------------------------------
def createPreviewRole( roleInfo, space ) :
	"""
	call to create a preview role
	@type			roleInfo : RoleInfo
	@param			roleInfo : instance of RoleInfo defined in RoleMaker
	@type			space	 : INT32
	@param			space	 : space id of the space the created preview locate in
	@rtype					 : PreviewRole
	@return					 : a new preview role map to roleInfo
	"""
	vehicle = 0
	position = ( 55.5, 1.0, -185.0 )
	direction = ( 0.0, 0.0, 2.76 )
	id = BigWorld.createEntity( "PreviewRole", space, vehicle, position, direction, {} )
	role = BigWorld.entity( id )
	return role


# --------------------------------------------------------------------
# implement preview role
# --------------------------------------------------------------------
class PreviewRole( GameObject ) :
	def __init__( self ) :
		GameObject.__init__( self )
		self.setSelectable( True )
		self.selectable = True
		self.model = None									# 模型
		self.talismanModel = None
		self.tam = None
		self.__roleInfo = None								# 绑定的角色相关信息
		self.__genderModels = {}							# 性别相关模型
		self.__genderModels[csdefine.GENDER_MALE]	= None
		self.__genderModels[csdefine.GENDER_FEMALE] = None
		self.__controled = False

		self.__rotateCBID = 0								# 角色旋转时的 callback ID

		self.onMouseEnter = None							# 鼠标进入时被触发的函数
		self.onMouseLeave = None							# 鼠标离开时被触发的函数
		self.onClick = None									# 鼠标点击时被触发的函数

		self.am = BigWorld.ActionMatcher( self )			# 动作匹配器
		self.am.matchCaps = [Define.CAPS_LOGIN, Define.CAPS_NOWEAPON]	# 默认Caps
		self.am.turnModelToEntity = True

		self.am.boredNotifier = self.onBored				# 当播放某个动作过长 将会触发
		#self.am.patience = random.random() * 6 + 6.0		# 初始化时的patience时间交给随机决定
		self.am.fuse = random.random() * 6 + 6.0			# 当前的fuse时间也交给随机决定

		# 默认武器类型为空手
		self.weaponType = Define.WEAPON_TYPE_NONE
		self.randomActionsWithWeapon = []					# 有武器随机动作列表
		self.randomActionsWithDanWeapon = []				# 单手剑武器随机动作列表
		self.randomActionsWithShuangWeapon = []				# 双手剑武器随机动作列表
		self.randomActionsWithFuWeapon = []					# 斧头武器随机动作列表
		self.randomActionsWithChangWeapon = []				# 长枪武器随机动作列表
		self.randomActionsNoWeapon = []						# 无武器随机动作列表

		self.faceInt = 0									# 临时变量，用于判定当前演示效果是否过期

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def roleInfo( self ) :
		"""
		获取对应角色相关信息
		"""
		return self.__roleInfo

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onTargetFocus( self ) :
		"""
		鼠标进入模型时被调用
		"""
		if self.useGlowEff and self.model and self.model.visible:
			self.model.enableShine = True

		if callable( self.onMouseEnter ) :
			self.onMouseEnter( self )

	def onTargetBlur( self ) :
		"""
		鼠标离开模型时被调用
		"""
		if self.useGlowEff and self.model and self.model.visible:
			self.model.enableShine = False

		if callable( self.onMouseLeave ) :
			self.onMouseLeave( self )

	def onTargetClick( self, sender ) :
		"""
		鼠标点击模型时被调用
		"""
		GameObject.onTargetClick( self, sender )
		if callable( self.onClick ) :
			self.onClick( self )

	# -------------------------------------------------
	def prerequisites( self ):
		"""
		当角色进入游戏时被调用
		以下代码主要是为了处理角色选择中的圆盘和角色创建的 PATROL_TARGET
		"""
		if len( self.modelName ):
			return [self.modelName, ]
		return []

	def enterWorld( self ) :
		"""
		当角色进入游戏时被调用
		以下代码主要是为了处理角色选择中的圆盘
		"""
		if len( self.modelName ) and self.model is None:
			self.model = BigWorld.Model( self.modelName )
			#if self.model:
			#	self.model.scale = (0.15, 0.15, 0.15)

	# -------------------------------------------------
	def onMovingNotify( self, isMoving ) :
		"""
		移动时实时触发
		"""
		self.notifyAttachments_( "onMovingNotify", isMoving )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setModel( self, model ):
		"""
		设置模型
		"""
		if model is not None:
			if model.attached :
				ERROR_MSG( "model '%s' is attached!" )				# output error message -- hyw( 2009.12.25 )
				return
			self.model = model
			if self.am.owner != None: self.am.owner.delMotor( self.am )
			self.model.motors = ( self.am, )
			# 头发动画
			hairModel = model.head
			rds.actionMgr.playAction( hairModel, Const.MODEL_ACTION_HAIR_BONE_1 )
		else:
			self.model = None
			self.models = []

		# 刷新记录模型的随机动作名称
		model = self.getModel()
		if hasattr( model, "shangshen1" ) :
			if model.shangshen1.tint[-2] == "_":
				if hasattr( model, "lian1" ) and not model.lian1.tint.endswith("_2") :
					tint = model.lian1.tint
					tint += "_2"
					model.lian1 = tint
		self.getRandomActions()

	def onPartModelLoad( self, model ):
		"""
		整个身体模型加载完成回调
		"""
		self.setModel( model )
		profession = self.__roleInfo.getClass()
		gender = self.__roleInfo.getGender()
		# 加载发型
		hairNum = self.__roleInfo.getHairNumber()
		fashionNum = self.__roleInfo.getFashionNum()
		rds.roleMaker.createHairModelBG( hairNum, fashionNum, profession, gender, self.onHairModelLoad )
		# 加载左右手模型
		rds.roleMaker.createMWeaponModelBG( self.__roleInfo.getRHFDict(), Functor( self.onRighthandModelLoad, self.__roleInfo.getRHFDict() ) )
		rds.roleMaker.createMWeaponModelBG( self.__roleInfo.getLHFDict(), Functor( self.onLefthandModelLoad, self.__roleInfo.getLHFDict() ) )
		# 加载法宝模型
		rds.roleMaker.createTalismanModelBG( self.__roleInfo.getTalismanNum(), Functor( self.onTalismanModelLoad, self.__roleInfo.getTalismanNum() ) )
		# 装备附加粒子效果
		if not self.__roleInfo.getFashionNum():
			self.resetEquipEffect( model )
		# 法师特有粒子效果
		if profession == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER )

	def onHairModelLoad( self, hairModel ):
		"""
		callback Method
		发型换装完成回调
		"""
		if self.__roleInfo is None: return
		model = self.model
		key = "HP_head"
		rds.effectMgr.linkObject( model, key, hairModel )
		rds.actionMgr.playAction( hairModel, Const.MODEL_ACTION_HAIR_BONE_1 )

	def onRighthandModelLoad( self, weaponDict, model ):
		"""
		右手武器加载回调
		"""
		if model:
			self.weaponAttachEffect( model, weaponDict )
		if self.__roleInfo is None: return
		roleModel = self.model
		if roleModel is None: return

		# 换模型
		key = "HP_right_hand"
		rds.effectMgr.linkObject( roleModel, key, model )

		weaponNum = self.__roleInfo.getRHFDict()["modelNum"]
		if weaponNum:
			actionName = rds.itemModel.getActionsName( weaponNum )
			if actionName:
				timetick = rds.itemModel.getTimetick( weaponNum )

				def callback():
					if not model:return
					if not model.inWorld:return
					if model.hasAction( actionName):
						rds.actionMgr.playAction( model, actionName )
					BigWorld.callback(random.randint( timetick[0], timetick[1] ),callback )
				callback()
		self.resetWeaponType()

	def onLefthandModelLoad( self, weaponDict, model ):
		"""
		左手武器模型加载完成
		"""
		if model:
			self.weaponAttachEffect( model, weaponDict )
		if self.__roleInfo is None: return
		roleModel = self.model
		if roleModel is None: return
		profession = self.__roleInfo.getClass()
		key = "HP_left_shield"
		if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
			key = "HP_left_hand"
		rds.effectMgr.linkObject( roleModel, key, model )

		self.resetWeaponType()

	def resetWeaponType( self ):
		"""
		设置武器类型
		"""
		if self.__roleInfo is None: return
		profession = self.__roleInfo.getClass()
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.__roleInfo.getLHFDict()["modelNum"]
		else:
			weaponNum = self.__roleInfo.getRHFDict()["modelNum"]

		if weaponNum:
			weaponType = Define.CLASS_WEAPONTYPE.get( profession, [] )
			if len( weaponType ) == 0: weaponType = 0
			if profession == csdefine.CLASS_SWORDMAN:    # 剑客
				if not self.__roleInfo.getLHFDict()["modelNum"]:
					weaponType = weaponType[0]
				else:
					weaponType = weaponType[1]
			elif profession == csdefine.CLASS_FIGHTER:  #战士
				if str( weaponNum )[1:3] == str(Define.PRE_EQUIP_TWOLANCE):
					weaponType = weaponType[1]
				else:
					weaponType = weaponType[0]
			else:
				weaponType = weaponType[0]
			self.weaponType = weaponType
		else:
			self.weaponType = 0
		# 重设Caps状态
		self.setArmCaps()

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

		if model.hasAction( "wwm_01_036_animations" ):
			rds.actionMgr.playAction( model, "wwm_01_036_animations" )

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
			if not type:return
			texture = rds.equipParticle.getWTexture( weaponKey )
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, intensifyLevel )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )

	def resetEquipEffect( self, model ):
		"""
		刷新光效效果表现
		"""
		profession = self.__roleInfo.getClass()
		gender = self.__roleInfo.getGender()
		bodyFDict = self.__roleInfo.getBodyFDict()
		feetFDict = self.__roleInfo.getFeetFDict()

		######################胸部光效#################################
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

		###########鞋子光效######################################################
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )


	def createTalismanAM( self ):
		"""
		法宝控制motor
		"""
		# 创建圆形轨迹motor，设置motor的参数
		self.tam = BigWorld.Orbitor()
		self.tam.spinRadius = 0.5
		self.tam.startSpin = 0.5
		self.tam.endSpeed = 1.0
		self.tam.speed = 1.0
		self.tam.wobble = True
		self.tam.wobbleFreq = 0.45
		self.tam.wobbleMax = 0.4
		self.tam.proximity = 0.8
		self.tam.target = rds.effectMgr.accessNode( self.getModel(), "HP_right_shoulder" )

	def setTalismanModel( self, model ):
		"""
		设置法宝模型
		"""
		if self.talismanModel and self.talismanModel in list( self.models ):
			self.delModel( self.talismanModel )
		self.talismanModel = model
		if self.talismanModel:
			self.addModel( self.talismanModel )
			self.talismanModel.position = self.position + ( 1.2, 1.7, 0.0 )
			rds.actionMgr.playAction( self.talismanModel, Const.MODEL_ACTION_PLAY )
			if self.tam is None:
				self.createTalismanAM()
			else:
				if self.tam.owner != None: self.tam.owner.delMotor( self.tam )
			self.talismanModel.addMotor( self.tam )

	def onTalismanModelLoad( self, talismanNum, model ):
		"""
		法宝模型加载回调
		"""
		# 法宝Dyes
		talismanDyes = rds.roleMaker.getTalismanModelDyes( talismanNum )
		rds.effectMgr.createModelDye( model, talismanDyes )
		# 自带光效
		effectIDs = rds.itemModel.getMEffects( talismanNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
			effect.start()

		self.setTalismanModel( model )

	def setInfo( self, info ):
		"""
		设置角色相关信息
		"""
		self.__roleInfo = info

	def setToControl( self ) :
		"""
		设置为可客户端独立控制
		"""
		self.__controled = True
		BigWorld.controlEntity( self, True )
		self.physics = STANDARD_PHYSICS									# defined in keys.py
		self.physics.velocity = ( 0.0, 0.0, 0.0 )
		self.physics.velocityMouse = "Direction"
		self.physics.angular = 0
		#self.physics.angularMouse = "MouseX"
		self.physics.collide = False
		self.physics.gravity = 0
		self.physics.fall = False
		self.physics.userDirected = False								# 这个是必须的，否则该模型的yaw会随鼠标方向改变
		self.physics.isMovingNotifier = self.onMovingNotify

	def destroy( self ) :
		"""
		销毁模型
		"""
		BigWorld.controlEntity( self, False )
		BigWorld.destroyEntity( self.id )

	def setArmCaps( self ) :
		"""
		set caps
		"""
		if self.__roleInfo is None: return

		profession = self.__roleInfo.getClass()
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.__roleInfo.getLHFDict()["modelNum"]
		else:
			weaponNum = self.__roleInfo.getRHFDict()["modelNum"]

		armCaps = []
		if weaponNum:
			if profession == csdefine.CLASS_FIGHTER:
				armCaps.append( Define.CAPS_CHANG_WEAPON )	# 长枪
			elif profession == csdefine.CLASS_SWORDMAN:
				armCaps.append( Define.CAPS_DAN_WEAPON )	# 单手剑
			else:
				armCaps.append( Define.CAPS_WEAPON )
			#if self.weaponType == Define.WEAPON_TYPE_LIGHTSHARP:
			#	armCaps.append( Define.CAPS_DAN_WEAPON )	# 单手剑
			#elif self.weaponType == Define.WEAPON_TYPE_DOUBLEHAND:
			#	armCaps.append( Define.CAPS_SHUANG_WEAPON )	# 双手剑
			#elif self.weaponType == Define.WEAPON_TYPE_WEIGHTSHARP:
			#	armCaps.append( Define.CAPS_FU_WEAPON )		# 斧头
			#elif self.weaponType == Define.WEAPON_TYPE_LIGHTBLUNT:	
			#	armCaps.append( Define.CAPS_CHANG_WEAPON )	# 长枪
			#else:
			#	armCaps.append( Define.CAPS_WEAPON )
		else:
			armCaps.append( Define.CAPS_NOWEAPON )
		stateCaps = Define.CAPS_LOGIN
		if stateCaps is None:
			caps = armCaps
		else:
			caps = [stateCaps] + armCaps
		self.am.matchCaps = caps

	# ----------------------------------------------------------------
	# 随机动作相关
	# ----------------------------------------------------------------
	def switchRandomAction( self, isTigger ):
		"""
		"""
		if isTigger:
			value = random.random() * 6 + 6.0
		else:
			value = 0.0
		self.am.patience = value

	def onBored( self, actionName ):
		"""
		此回调用于播放随机动作
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		# 如果action 是空时，重置fuse，重新开始计时
		if actionName is None: return

		# 触发眨眼睛( 0-8 )秒随机之后，播放眨眼动画
		BigWorld.callback( random.random() * 8, self.playNictation )

		# 只有站着的时候才播放随机动作
		if actionName == "login_stand": self.playRandomAction()
		# 当一个动作开始播放时 fuse 会重置为0
		# 引擎似乎有bug，有时候并没有重置 fuse 这个属性，现在在这里重置
		self.am.fuse = 0
		# 每通知一次 onBored  引擎会自动把 patience 设为一个负值??
		# 只有重置 patience 值 才能连续的不停调用 onBored 方法
		self.am.patience = random.random() * 6 + 6.0

	def playRandomAction( self ):
		"""
		play random Action
		"""
		caps = self.am.matchCaps
		if Define.CAPS_LOGIN not in caps: return

		# 分拿武器动作和不拿武器动作的处理
		if Define.CAPS_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithWeapon )
		elif Define.CAPS_DAN_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithDanWeapon )
		elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithShuangWeapon )
		elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithFuWeapon )
		elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
			randomActionCount = len( self.randomActionsWithChangWeapon )
		else:
			randomActionCount = len( self.randomActionsNoWeapon )

		# 取得索引
		if randomActionCount == 0: return
		index = random.randint( 0, randomActionCount - 1 )
		capsIndex = Define.CAPS_INDEX25 + index

		caps.remove( Define.CAPS_LOGIN )
		caps.append( capsIndex )
		caps.append( Define.CAPS_RANDOM )
		self.am.matchCaps = caps

		BigWorld.callback( 0.1, self.onOneShoot )

	def onOneShoot( self ):
		"""
		<oneShot>
		Setting this to TRUE means that the Action Matcher will not continue
		playing that action past one cycle of it, if it is no longer triggered,
		but a <cancel> section was keeping it active.
		"""
		# 如果已不在视野则过滤
		if not self.inWorld: return
		self.setArmCaps()

	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		获取随机动作，由于随机动作数量不固定，
		获取随机动作从random1开始，random2,random3....获取失败则返回
		"""
		if self.model is None: return

		# 有武器随机动作列表
		self.randomActionsWithWeapon = []
		# 将有武器随机动作和无武器随机动作分开处理
		for index in range(1,10):
			weaponActName = "random%s" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithWeapon.append( weaponActName )
			else:
				break

		# 单手剑武器随机动作列表
		self.randomActionsWithDanWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_dan" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithDanWeapon.append( weaponActName )
			else:
				break

		# 双手剑武器随机动作列表
		self.randomActionsWithShuangWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_shuang" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithShuangWeapon.append( weaponActName )
			else:
				break

		# 斧头武器随机动作列表
		self.randomActionsWithFuWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_fu" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithFuWeapon.append( weaponActName )
			else:
				break

		# 长枪武器随机动作列表
		self.randomActionsWithChangWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_chang" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithChangWeapon.append( weaponActName )
			else:
				break

		# 无武器随机动作列表
		self.randomActionsNoWeapon = []
		for index in xrange( 1, 10 ):
			noWeaponActName = "random%s_noweapon" % index
			if self.model.hasAction( noWeaponActName ):
				self.randomActionsNoWeapon.append( noWeaponActName )
			else:
				break

	def playPoseAction( self, delay = 0.0, cb = None ):
		"""
		play pose Action
		"""
		if self.model is None: return False
		if not self.inWorld: return False

		def onActionOver():
			if callable( cb ):cb()
			if self.model is None: return
			if "newlybuilt" in self.model.queue: return
			self.switchLoft( False )

		self.setArmCaps()
		if Define.CAPS_WEAPON in self.am.matchCaps:
			index = 1
		elif Define.CAPS_DAN_WEAPON in self.am.matchCaps:
			index = 2
		elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
			index = 3
		elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
			index = 4
		elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
			index = 5
		else:
			index = 0
		
		newlybuilt_list = Const.MODEL_ACTION_NEWLYBUILT_LIST
		rds.actionMgr.playAction( self.model, newlybuilt_list[index], time = delay, callback = onActionOver )
		self.playPoseEffect()
		return True

	def playPoseEffect( self ):
		"""
		播放职业演示效果
		"""

		def loadParticle( lastTime, hp, path ):
			"""
			延迟加载粒子
			"""
			def onParticleLoad( particle ):
				"""
				粒子加载完成回调
				"""
				if particle is None: return
				if not self.inWorld: return
				if faceInt != self.faceInt: return
				rds.effectMgr.attachObject( model, hp, particle )
				particle.force()
				functor = Functor( onFadeOut, hp, particle )
				BigWorld.callback( lastTime, functor )

			def onFadeOut( hp, particle ):
				"""
				渐隐粒子
				"""
				rds.effectMgr.fadeOutParticle( particle )
				functor = Functor( onDetach, hp, particle )
				BigWorld.callback( 3.0, functor )

			def onDetach( hp, particle ):
				"""
				卸载粒子
				"""
				rds.effectMgr.detachObject( model, hp, particle )

			if not self.inWorld: return
			if faceInt != self.faceInt: return
			rds.effectMgr.pixieCreateBG( path, onParticleLoad )

		model = self.model
		self.faceInt += 1
		faceInt = self.faceInt
		profession = self.__roleInfo.getClass()
		data = Const.ROLE_CREATE_EFFECT_CLASS_MAP.get( profession )
		if data is None: data = []
		for delayTime, lastTime, hp, path in data:
			functor = Functor( loadParticle, lastTime, hp, path )
			BigWorld.callback( delayTime, functor )
		if profession in [ csdefine.CLASS_FIGHTER, csdefine.CLASS_SWORDMAN ]:
			self.switchLoft( True )

	def switchLoft( self, switch ):
		attachments = []
		model = self.model
		if hasattr( model, "right_hand" ) and model.right_hand:
			rightHand = model.right_hand
			if hasattr( rightHand, "sfx1" ):
				attachments.extend( rightHand.node("HP_sfx1").attachments )
			if hasattr( rightHand, "sfx2" ):
				attachments.extend( rightHand.node("HP_sfx2").attachments )
		if hasattr( model, "left_hand" ) and model.left_hand:
			leftHand = model.left_hand
			if hasattr( leftHand, "sfx1" ):
				attachments.extend( leftHand.node("HP_sfx1").attachments )
			if hasattr( leftHand, "sfx2" ):
				attachments.extend( leftHand.node("HP_sfx2").attachments )
		for particle in attachments:
			if not isinstance( object, Pixie.MetaParticleSystem ): continue
			system = particle.system(0)
			if system is None: continue
			render = system.renderer
			if render.__class__.__name__ != "LoftRenderer": continue
			if switch:
				render.start()
			else:
				render.stop()

	def playNictation( self, key = None ):
		"""
		眨眼睛
		"""
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return
		if not hasattr( model, "lian1" ): return

		# 保留旧的脸dye，以便恢复
		oldTint = model.lian1.tint
		if hasattr( model, "shangshen1" ) :
			if model.shangshen1.tint[-2] == "_":
				if "_nictation_2" in oldTint: return
				if not oldTint.endswith("_2"):
					oldTint = oldTint + "_2"
				oldTint = oldTint.replace("_2","_nictation_2")
				model.lian1 = oldTint
			else:
				if "_nictation" in oldTint: return
				if oldTint.endswith("_2"):
					oldTint = oldTint.replace("_2","")
				oldTint = oldTint + "_nictation"
				model.lian1 = oldTint
		else:
			if "_nictation" in oldTint: return
			if oldTint.endswith("_2"):
				oldTint = oldTint.replace("_2","")
			oldTint = oldTint + "_nictation"
			model.lian1 = oldTint

		# 播放眨眼6-9秒，恢复旧的脸dye
		faceNum = self.__roleInfo.getFaceNumber()
		functor = Functor( self.onPlayNictationOver, oldTint, faceNum )
		BigWorld.callback( random.random() * 3 + 6, functor )

	def onPlayNictationOver( self, oldTint, oldFaceNum ):
		"""
		眨眼动作播放完毕
		"""
		# 这里可能会涉及
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return
		if not hasattr( model, "lian1" ): return

		faceNum = self.__roleInfo.getFaceNumber()
		if faceNum != oldFaceNum: return

		if oldTint.endswith("_nictation"):
			oldTint = oldTint.replace( "_nictation", "" )
		elif oldTint.endswith("_nictation_2"):
			oldTint = oldTint.replace( "_nictation_2", "_2" )
		if hasattr( model, "shangshen1" ):
			if model.shangshen1.tint[-2] == "_" and not oldTint.endswith("_2"):
				oldTint = oldTint + "_2"
			elif model.shangshen1.tint[-2] != "_" and oldTint.endswith("_2"):
				oldTine = oldTint.replace("_2","")
		elif oldTint.endswith("_2"):
			oldTint = oldTint.replace("_2","")

		model.lian1 = oldTint

	# -------------------------------------------------
	def faceTo( self, pos, callback = None ) :
		"""
		设置面向坐标
		@type			pos		 : Vector3
		@param			pos		 : 面向的坐标
		@type			callback : functor
		@param			callback : 旋转回调，它必须包含一个参数，指出面向是否成功
		"""
		yaw = ( pos - self.position ).yaw
		self.physics.seek( ( 0, 0, 0, yaw ), 1, 0, callback )

	def oppositeTo( self, pos, callback = None ) :
		"""
		设置背向坐标
		@type			pos		 : Vector3
		@param			pos		 : 背向的坐标
		@type			callback : functor
		@param			callback : 旋转回调，它必须包含一个参数，指出背向是否成功
		"""
		yaw = ( self.position - pos ).yaw
		self.physics.seek( ( 0, 0, 0, yaw ), 1, 0, callback )

	def turnaround( self, deltaRadian, callback = None ) :
		"""
		旋转指定角度
		@type			deltaRadian	: float
		@param			deltaRadian	: 旋转的弧度
		@type			callback	: functor
		@param			callback	: 旋转回调，它必须包含一个参数，指出背向是否成功
		"""
		self.physics.seek( ( 0, 0, 0, self.yaw + deltaRadian ), 1, 0, callback )
	
	def turnaroundToYaw( self, deltaRadian, callback = None ) :
		"""
		旋转指定角度
		@type			deltaRadian	: float
		@param			deltaRadian	: 旋转的弧度
		@type			callback	: functor
		@param			callback	: 旋转回调，它必须包含一个参数，指出背向是否成功
		"""
		self.physics.seek( ( 0, 0, 0, deltaRadian ), 1, 0, callback )

	def instantRotate( self, srcPos, dstPos, callback = None ) :
		"""
		旋转的角度为：srcPos 的向量角度 与 dstPos 的向量角度差
		@type				srcPos		: Vector3
		@param				srcPos		: 旋转前的面向向量
		@type				dstPos		: Vector3
		@param				dstPos		: 旋转后的面向向量
		@type				callback	: functor
		@param				callback	: 旋转结束后的调用
		@return							: None
		"""
		srcPos = Math.Vector3( srcPos )							# 旋转前的面向向量
		dstPos = Math.Vector3( dstPos )							# 旋转后的面向向量
		dstYaw = ( dstPos - self.position ).yaw					# 旋转后的方向
		srcYaw = ( srcPos - self.position ).yaw					# 旋转前的方向
		self.turnaround( dstYaw - srcYaw )						# 旋转后前的面向角度差
		if callback:
			callback()

	def sostenutoRotate( self, srcPos, dstPos, stepRadians, rotateSpeed = 0.1, cbArrived = None, cbRotating = None ):
		"""
		以一定速度持续地旋转自己，旋转的角度为：srcPos 的向量角度 与 dstPos 的向量角度差
		@type				srcPos		: Vector3
		@param				srcPos		: 旋转前的面向向量
		@type				dstPos		: Vector3
		@param				dstPos		: 旋转后的面向向量
		@type				stepRadians	: float
		@param				stepRadians	: 每 tick 旋转的的步长(弧度)
		@type				rotateSpeed	: int
		@param				rotateSpeed	: 速度(单位：秒/次)
		@type				cbArrived	: functor
		@param				cbArrived	: 旋转结束后的调用，包含一个参数，标示旋转结束时，是否如意旋转到位
		@type				cbRotating	: functor
		@param				cbRotating	: 旋转过程中每 tick 的回调
		@return							: None
		"""
		if self.__rotateCBID != 0 :							# 如果当前正在旋转
			BigWorld.cancelCallback( self.__rotateCBID )	# 则停止当前的旋转状态
			self.__rotateCBID = 0

		srcPos = Math.Vector3( srcPos )						# 旋转前的面向向量
		dstPos = Math.Vector3( dstPos )						# 旋转后的面向向量
		srcYaw = ( srcPos - self.position ).yaw				# 旋转前的方向
		dstYaw = ( dstPos - self.position ).yaw				# 旋转后的方向
		deltaRadian = dstYaw - srcYaw						# 旋转后与旋转前的面向角度差
		if deltaRadian > math.pi :
			deltaRadian = 2 * math.pi - deltaRadian
			stepRadians = -stepRadians						# 通过 stepRadians 的正负来确定旋转的方向
		elif deltaRadian < -math.pi :
			deltaRadian = 2 * math.pi + deltaRadian

		def rotate( radians, stepRadians ) :				# 循环旋转 radians 度
			if radians == 0 :								# 旋转结束
				if cbArrived : cbArrived( True )
				return
			if radians > abs( stepRadians ) :
				radians -= abs( stepRadians )
			else :
				if stepRadians < 0 : stepRadians = -radians
				else : stepRadians = radians
				radians = 0
			if self.physics is None :						# 对象被撤销
				if cbArrived : cbArrived( False )			# 旋转到中途时失败
				return
			self.physics.seek( ( 0, 0, 0, self.yaw + stepRadians ), 1, 0, None )
			if cbRotating : cbRotating( self.yaw )
			self.__rotateCBID = BigWorld.callback( rotateSpeed, Functor( rotate, radians, stepRadians ) )
		rotate( abs( deltaRadian ), stepRadians )

	def velocityTo( self, position, speed, callback = None, isSeekToGoal = True ) :
		"""
		velocity to one position( when arrived destination, it will not stop, so you must set stop at callback )
		注：当前移动到指定位置时会停下来，为了精确，我们需要修改底层physics.seek()接口，加入“到达后是否置velocity为0”的参数来解决。
		add: 底层新增参数 isSeekToGoal 为False 时， 目标节点间做物理运动平滑处理
		@type			position	: Vector3
		@param			position	: 移动到的目的位置
		@type			speed		: Float
		@param			speed		: 移动速度
		@type			callback	: Fucntor
		@param			callback	: 到达目的点后的回调
		@type			isSeekToGoal  : bool
		@param          isSeekToGoal  ：是否强制到达指定的目标地
		@return						  : None
		"""
		BigWorld.dcursor().yaw = 0
		pos = Math.Vector3( position )
		dist = pos.distTo( self.position )
		needTime = dist * 1.5 / speed

		self.physics.velocity = 0, 0, speed
		yaw = ( pos - self.position ).yaw
		self.physics.seek( ( pos.x,pos.y,pos.z, yaw ), needTime, 0.1, callback, isSeekToGoal )

	def stopVelocity( self ) :
		"""
		停止移动
		@return						: None
		"""
		self.physics.stop( True )		# stop velocity
		if self.physics.seeking:
			self.physics.seek( None )	# stop seek

