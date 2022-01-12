# -*- coding: gb18030 -*-
import math

import BigWorld
import Math
from Function import Functor
import cschannel_msgs
import Define
import Const
import csdefine
import Pixie
from gbref import rds
from interface.GameObject import GameObject
import event.EventCenter as ECenter
from RoleMaker import RoleInfo
from config.client.DanceActivityConfig import Datas
titleColor = {'gold':(218,178,115,255),'sliver':(233,233,216,255), 'copper':(186,110,64,255), 'wait':(255,255,255,255)}

class DanceKing( GameObject ):
	def __init__( self ):
		GameObject.__init__( self )
		self.talismanModel = None
		self.modelScale = 1.0
		self.equipEffects = []

	def onCacheCompleted( self ):
		self.createModel()
		GameObject.onCacheCompleted( self )
	

	def initCacheTasks( self ):
		"""
		初始化缓冲器任务
		"""
		self.addCacheTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT1 )

	def createModel( self ):
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			self.am.matchCaps = [Define.CAPS_ENVIRONMENT_OBJECT]
		self.createEquipModel( Define.MODEL_LOAD_ENTER_WORLD )

	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		"""
		GameObject.onModelChange( self, oldModel, newModel )
		if newModel is None: return
		if self.am.owner != None: self.am.owner.delMotor( self.am )
		newModel.motors = ( self.am, )
		newModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
		self.flushAttachments_()

	def createEquipModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		创建装备模型
		@type	event	:	int
		@param	event	: 	加载事件
		"""
		paths = self.getEquipModelPaths()
		functor = Functor( self.onEquipModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getEquipModelPaths( self ):
		"""
		获取装备模型路径
		@return dict
		"""
		roleInfo = self.getModelInfo()
		paths = {}
		profession = self.getClass()
		gender = self.getGender()
		# 角色主体模型
		bodyPaths= rds.roleMaker.getShowModelPath( roleInfo )
		if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
		# 附属模型发型
		hairPaths = rds.roleMaker.getHairModelPath( self.hairNumber, self.fashionNum, profession, gender )
		if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths
		# 附属模型右手武器
		rightHandPaths = rds.roleMaker.getMWeaponModelPath( self.righthandFDict )
		if len( rightHandPaths ): paths[Define.MODEL_EQUIP_RHAND] = rightHandPaths
		# 附属模型左手武器
		leftHandPaths = rds.roleMaker.getMWeaponModelPath( self.lefthandFDict )
		if len( leftHandPaths ): paths[Define.MODEL_EQUIP_LHAND] = leftHandPaths
		return paths

	def onEquipModelLoad( self, event, modelDict ):
		"""
		装备模型加载完成
		"""
		if not self.inWorld: return

		mainModel = self.composeEquipModel( modelDict )
		self.setModel( mainModel, event )
		self.setArmCaps()
		if self.locationIndex:
			if self.getDictFromDatas(self.locationIndex):
				path = self.getDictFromDatas(self.locationIndex)["path"]
				hardPoint = self.getDictFromDatas(self.locationIndex)["hardPoint"]
				p =  Pixie.create(path)
				self.model.node(hardPoint).attach( p )
				p.force()
			else:
				print "DanceActivityConfig has not index",self.locationIndex,"config about particle"

		rds.actionMgr.playAction(self.model, "dance")   #模型加载完，播放动作dance
		self.model.scale = (self.modelScale, self.modelScale, self.modelScale)  #调整模型大小

	def setArmCaps( self ):
		"""
		set caps
		"""
		if not self.inWorld: return
		profession = self.raceclass & csdefine.RCMASK_CLASS
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.lefthandFDict["modelNum"]
		else:
			weaponNum = self.righthandFDict["modelNum"]

		armCaps = []
		if weaponNum:
			if profession == csdefine.CLASS_SWORDMAN:
				if not self.lefthandFDict["modelNum"]:
					armCaps.append( Define.CAPS_DAN_WEAPON )	# 单手剑
				else:
					armCaps.append( Define.CAPS_SHUANG_WEAPON )	# 双手剑
			elif profession == csdefine.CLASS_FIGHTER:
				if str( weaponNum )[1:3] == str(Define.PRE_EQUIP_TWOLANCE):
					armCaps.append( Define.CAPS_CHANG_WEAPON )	# 长枪
				else:
					armCaps.append( Define.CAPS_FU_WEAPON )		# 斧头

		self.am.matchCaps = [Define.CAPS_ENVIRONMENT_OBJECT] + armCaps

	def getModelInfo( self ):
		"""
		获取创建模型相关必要的信息
		"""
		infoDict = {}
		infoDict["roleID"]			= 0
		infoDict["roleName"]	 	= self.uname
		infoDict["level"]			= 0
		infoDict["raceclass"]		= self.raceclass
		infoDict["hairNumber"]		= self.hairNumber
		infoDict["faceNumber"]		= self.faceNumber
		infoDict["bodyFDict"]		= self.bodyFDict
		infoDict["volaFDict"]		= self.volaFDict
		infoDict["breechFDict"]		= self.breechFDict
		infoDict["feetFDict"]		= self.feetFDict
		infoDict["lefthandFDict"]	= self.lefthandFDict
		infoDict["righthandFDict"]	= self.righthandFDict
		infoDict["talismanNum"]		= self.talismanNum
		infoDict["fashionNum"]		= self.fashionNum
		infoDict["adornNum"]		= self.adornNum
		infoDict["headTextureID"]	= 0
		return RoleInfo( infoDict )

	def composeEquipModel( self, modelDict ):
		"""
		组合装备模型
		"""
		# 主体模型
		mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None: return
		roleInfo = self.getModelInfo()
		rds.roleMaker.partModelAttachEffect( mainModel, roleInfo )
		#附属模型发型
		headModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
		self.attachHairModel( mainModel, headModel )
		profession = self.getClass()
		gender = self.getGender()
		rds.roleMaker.hairModelAttachEffect( headModel, self.hairNumber, self.fashionNum, profession, gender )
		"""
		# 附属模型右手武器
		righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
		self.attachRHModel( mainModel, righthandModel )
		self.weaponAttachEffect( righthandModel, self.righthandFDict  )
		# 附属模型左手武器
		lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
		self.attachLHModel( mainModel, lefthandModel )
		self.weaponAttachEffect( lefthandModel, self.lefthandFDict )
		"""
		# 如果不是时装模式，则显示额外装备粒子效果
		if not self.fashionNum: self.resetEquipEffect( mainModel )
		# 如果职业是法师，则显示脚底粒子效果
		if self.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = Define.TYPE_PARTICLE_NPC )

		return mainModel

	def weaponAttachEffect( self, model, weaponDict ):
		"""
		武器附加属性效果
		@type		model 		: pyModel
		@param		model 		: 模型
		@type		weaponDict 	: FDict
		@param		weaponDict 	: 武器数据
		"""
		pType = Define.TYPE_PARTICLE_NPC
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


	def resetEquipEffect( self, model ):
		"""
		刷新光效效果表现
		"""
		self.equipEffects = []

		######################胸部光效#################################
		bodyFDict = self.bodyFDict
		profession = self.getClass()
		gender = self.getGender()
		intensifyLevel = bodyFDict["iLevel"]
		# 绑定新的身体发射光芒效果(胸部装备强化至4星时出现)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		# 绑定新的各职业向上升光线(胸部装备强化至6星时出现)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		# 绑定新的身体周围盘旋上升光带( 胸部装备强化至9星时出现 )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		# 绑定新的龙型旋转光环( 胸部装备强化至9星时出现 )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )

		###########鞋子光效######################################################
		feetFDict = self.feetFDict
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, self.onEquipParticleLoad, Define.TYPE_PARTICLE_NPC )


	def onEquipParticleLoad( self, particle ):
		"""
		装备附加粒子加载完毕
		"""
		if not self.inWorld: return
		if particle is None: return
		self.equipEffects.append( particle )

		roleModel = self.getModel()
		if roleModel and roleModel.visible:
			visible = True
		else:
			visible = False

		rds.effectMgr.fadeOutParticle( particle )

	def attachHairModel( self, mainModel, hairModel ):
		"""
		加载头发
		"""
		rds.effectMgr.linkObject( mainModel, Const.MODEL_HAIR_HP, hairModel )
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )

	def attachRHModel( self, mainModel, rModel ):
		"""
		装载右手模型
		"""
		if not hasattr( mainModel, "right_hand" ): return
		# 换模型
		rds.effectMgr.linkObject( mainModel, Const.MODEL_RIGHT_HAND_HP, rModel )
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )

	def attachLHModel( self, mainModel, lModel ):
		"""
		装载左手模型
		"""
		if not hasattr( mainModel, "left_hand" ): return
		# 换模型
		profession = self.getClass()
		key = Const.MODEL_LEFT_SHIELD_HP
		if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
			key = Const.MODEL_LEFT_HAND_HP
		rds.effectMgr.linkObject( mainModel, key, lModel )
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )

	def attachTalismanModel( self, mainModel, talismanModel ):
		"""
		附加法宝模型
		"""
		matrixProvider = rds.effectMgr.accessNode( mainModel, Const.TALISMAN_TARGET_HP )
		self.setTalismanModel( talismanModel, matrixProvider )

	def setTalismanModel( self, model, matrixProvider ):
		"""
		设置法宝模型
		"""
		self.talismanModel = model
		self.setModelVisible( Define.MODEL_VISIBLE_TYPE_TRUE )
		if self.talismanModel is None: return
		self.addModel( self.talismanModel )
		self.talismanModel.position = self.position + ( 1.2, 1.7, 0.0 )
		rds.actionMgr.playAction( self.talismanModel, Const.MODEL_ACTION_PLAY )
		#if self.tam is None: self.createTalismanAM()
		#self.setTalismanTarget( matrixProvider )
		#self.talismanModel.addMotor( self.tam )

	def setModelVisible( self, visibleType ):
		if not self.model:
			return

		self.setVisibility( True )
		self.model.visibleAttachments = False

	def setVisibility( self, visible ) :
		"""
		设置模型可见性
		hyw -- 09.01.10
		"""
		GameObject.setVisibility( self, visible )
		# 附加模型
		model = self.getModel()
		if model and model != self.model:
			model.visible = visible

	def setName( self, uname ):
		"""
		define method.
		设置名称
		"""
		self.uname = uname
		ECenter.fireEvent( "EVT_ON_DANCEKING_NAME_CHANGED", self.id, uname )
		

	def getName( self ):
		"""
		取得entity名称
		"""
		return self.uname

	def setTitle( self, title ):
		# define method
		self.title = self.getTitlefromIndex(self.locationIndex)
		if self.title:
			ECenter.fireEvent( "EVT_ON_DANCEKING_TITLENAME_CHANGE", self.id, title )
			#ECenter.fireEvent( "EVT_ON_DANCEKING_TITLECOLOR_CHANGE", self.id, self.getColorfromIndex(self.locationIndex) )
		

	def getTitle( self ):
		"""
		virtual method.
		获取头衔
		@return: string
		"""
		return self.title

	def setRaceclass( self, race ):
		# define method
		self.raceclass = race

	def isRaceclass( self, rc, mask = csdefine.RCMASK_ALL):
		"""
		是否为指定种族职业。
		@return: bool
		"""
		return self.raceclass & mask == rc

	def getClass( self ):
		"""
		取得自身职业
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def getGender( self ):
		"""
		取得自身性别
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_GENDER

	def getRace( self ):
		"""
		取得自身种族
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_RACE

	def getFaction( self ):
		"""
		取得自身所属的势力
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_FACTION ) >> 12

	def setHairNumber( self, hair ):
		# define method
		self.hairNumber = hair

	def setFaceNumber( self , face ):
		# define method
		self.faceNumber = face

	def setBodyFDict( self, body ):
		# define method
		self.bodyFDict = body

	def setVolaFDict( self, volaf ):
		self.volaFDict = volaf

	def setBreechFDict( self, breechf ):
		# define method
		self.breechFDict = breechf

	def	setFeetFDict( self, feet ):
		# define method
		self.feetFDict = feet

	def setLefthandFDict( self, lefthand ):
		# define method
		self.lefthandFDict = lefthand

	def setRighthandFDict( self, righthand ):
		# define method
		self.righthandFDict = righthand

	def setTalismanNum( self, talisman ):
		# define method
		self.talismanNum = talisman

	def setFashionNum( self, fashion ):
		# define method
		self.fashionNum = fashion

	def setAdornNum( self, adorn ):
		# define method
		self.adornNum = adorn

	def setHeadTextureID( self, headTexture ):
		# define method
		self.headTextureID = headTexture

	def setAction( self, act ):
		# define method
		self.playAction = act

	def setModelScale( self, modelScale ):
		# define method
		self.modelScale = modelScale
		
	def setTongName( self, tongName ):
		# define method
		self.tongName = tongName
		
	def getDictFromDatas(self, index):
		for item in Datas:
			if index == item["locationIndex"]:
				return item
		return None

	def getColorfromIndex(self, index):
		if index == 1:
			return titleColor['gold']
		if index < 4:
			return titleColor['sliver']
		if index < 10:
			return titleColor['copper']
		if index < 20:
			return titleColor['wait']
	
	def getTitlefromIndex(self, index):
		if index == 1:
			return cschannel_msgs.DANCEGOLD
		if index < 4:
			return cschannel_msgs.DANCESILVER
		if index < 10:
			return cschannel_msgs.DANCECOPPER
		if index < 20:
			return 	cschannel_msgs.DANCEWAIT
		return ''
