
# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.99 2008-08-29 02:38:42 huangyongwei Exp $

"""
怪物类，继承自NPC
"""

import BigWorld
import GUI
from bwdebug import *
import csdefine
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit

import GUIFacade
import Define
import ItemTypeEnum
from utils import *
from gbref import rds
from UnitSelect import UnitSelect
import event.EventCenter as ECenter
from Sound import soundMgr
import random
import EntityCache
import csconst
import csstatus
import csstatus_msgs as StatusMsgs
import Const
from Function import Functor
from config.client.MonsterBlastConfig import Datas as MONSTERBLASTDATAS #add by wuxo 2011-11-17
import Math
from ModelLoaderMgr import ModelLoaderMgr
import csol
import skills
import Timer
import math
from config.client.BossGethitLightAndRockIDs import Datas as bossGetHitDatas
from config.client.SkillCauseLightAndRockIDs import Datas as skillCauseDatas
g_entityCache = EntityCache.EntityCache.instance()
g_mlMgr = ModelLoaderMgr.instance()      # 微端模型资源下载管理器

ACTION_MAPS = {	"walk" 			: [ "ride_walk", "crossleg_walk"],
				"run" 			: [ "ride_run", "crossleg_run" ],
				"stand"			: [ "ride_stand", "crossleg_stand" ],
					}

class Monster( NPCObject, CombatUnit ):
	"""
	怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPCObject.__init__( self )
		CombatUnit.__init__( self )

		self.am = None
		# 记录Monster 的随机动作集合，该属性会随着模型的改变而改变
		self.randomActions = []
		# 默认武器类型为空手
		self.weaponType = Define.WEAPON_TYPE_NONE
		# 默认防具类型为无防具
		self.armorType = Define.ARMOR_TYPE_EMPTY
		# skeletonCollider attr
		#self.skeletonCollider = BigWorld.SkeletonCollider()
		self.lefthandNumber = 0
		self.righthandNumber = 0
		self.canShowDescript = False	# 是否显示描述
		self.takeLevel = -1	# 可携带等级，10:15 2009-4-23，wsf

		self.isBlastFlag = False	#标记是否应该播放爆尸效果 add by wuxo 2011-11-17
		self.bootyOwner = ( 0, 0 )

		self.moveTime = 0.0
		self.faceTimerID = 0
		self.standbyEffect = None		# 待机光效
		self.admisActionFlag = False
		self.startEffect = None
		self.loopEffect = None
		self.adminEffect = None
		self.endEffect = None
		
		self.uiAttachsShow = True
		
		self.lastPos = Math.Vector3( 0, 0, 0 )
		self.isLoadModel = False       #是否正在改变模型中
		self.delayActionNames = []   #改变模型中放技能的施法动作
		self.delayCastEffects = []     #改变模型中技能的施法光效
		self.hipModels = []
		self.panModels = []
		self.pitchModelcbid = 0
		self.rotateTimerID = 0

		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ,\
		csdefine.VISIBLE_RULE_BY_SHOW_SELF]
	# ----------------------------------------------------------------
	# This method is called when the entity enters the world
	# Any of our properties may have changed underneath us,
	#  so we do most of the entity setup here
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return
		NPCObject.onCacheCompleted( self )
		CombatUnit.onCacheCompleted( self )

		# original model Boundbox be replaced with user skeletonCollider
		#baAttachNode = self.model.node("hips")
		#if( baAttachNode ):
		#	ba = BigWorld.BoxAttachment()
		#	ba.name = "hips"
		#	ba.minBounds = -0.5*self.model.scale
		#	ba.maxBounds = 0.5*self.model.scale
		#	baAttachNode.attach(ba)
		#	self.skeletonCollider.addCollider(ba)

		# 设置当前状态
		self.set_state()
		self.queryBootyOwner()
		#加入闪屏过程中召唤的怪物是否隐藏
		if not self.isshowModel():
			self.setModelVisible( Define.MODEL_VISIBLE_TYPE_FALSE )

	def leaveWorld( self ) :
		"""
		离开世界
		"""

		NPCObject.leaveWorld( self )
		CombatUnit.leaveWorld( self )
		self.am=None
		for linkEffect in self.linkEffect:
			linkEffect.stop()
		self.linkEffect = []
		if self.model is not None:
			self.model.OnActionStart = None
		self.model = None

	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		paths = NPCObject.prerequisites( self )
		paths.extend( rds.itemModel.getMSource( self.lefthandNumber ) )
		paths.extend( rds.itemModel.getMSource( self.righthandNumber ) )
		for i in paths[:]:
			if csol.isFileAtLocal(i) <= 0:
				paths.remove(i)
		vModelIDs = rds.npcModel.getVehicleModelIDs( self.modelNumber )
		for modelID in vModelIDs:
			paths.extend( rds.npcModel.getModelSources( modelID ) )
		return paths

	# ----------------------------------------------------------------
	# 模型相关
	# ----------------------------------------------------------------
	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		"""
		NPCObject.onModelChange( self, oldModel, newModel )
		CombatUnit.onModelChange( self, oldModel, newModel )
		if newModel is None: return

		am = self.am
		if am.owner != None: am.owner.delMotor( am )
		newModel.motors = ( am, )

		# 动态模型的放大必须在置 action match 之后做，否则会被复原
		newModel.scale = ( self.modelScale, self.modelScale, self.modelScale )

		# 设置左右手模型
		self.set_lefthandNumber()
		self.set_righthandNumber()

		# 获取该模型的随即动作
		self.getRandomActions()

		rds.areaEffectMgr.onModelChange( self )

	def fadeInModel( self ):
		"""
		渐入模型
		"""
		if not self.inWorld : return  # 如果已不在视野则过滤
		if self.hasFlag( csdefine.ENTITY_FLAG_CLOSE_FADE_MODEL ): return
		alpha = rds.npcModel.getModelAlpha( self.modelNumber )
		if alpha != 1:
			rds.effectMgr.setModelAlpha( self.model, alpha, 1.0 )
		else:
			rds.effectMgr.fadeInModel( self.model )

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型
		继承 NPCObject.createModel
		"""
		# Action Match
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# 模型的RolePitchYaw和Entity保持一致
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			# 模型的随机动作相关
			self.am.boredNotifier = self.onBored
			self.am.patience = random.random() * 6 + 6.0
			self.am.fuse = random.random() * 6 + 6.0
			self.setArmCaps()
		# 微端模型预加载处理
		modelSourceList = rds.npcModel.getModelSources( self.modelNumber )
		if modelSourceList:
			modelSource = modelSourceList[0]
		if len( modelSourceList ) == 1 and "avatar" not in modelSource :
			g_mlMgr.getSource( modelSource, self.id )
		self.isLoadModel = True
		self.delayActionNames = []   #改变模型中放技能的施法动作
		self.delayCastEffects = []     #改变模型中技能的施法光效
		if self.model is not None:
			self.model.OnActionStart = None
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.onModelLoad, event ) )
	
	def onModelLoad( self, event, model ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.setModel( model, event )
		self.updateVisibility()
		# 防止有待机动画的怪物更换模型后头顶名称无法显示
		self.showNameUI()
		self.flushAttachments_()
		self.isLoadModel = False
		if self.firstHide:
			self.playStandbyAction()
		if self.delayActionNames:
			rds.actionMgr.playActions( self.getModel(), self.delayActionNames )
		for cb in self.delayCastEffects:
			if callable( cb ):
				cb()
		self.getSubModel()
		self.onActionStart( "stand" )
		if self.model is not None:
			self.model.OnActionStart = self.onActionStart

	def getSubModel( self ):
		"""
		返回SubModel，用于骑宠类NPC
		"""
		for index in xrange( 1, 11 ):
			if index < 10: hipKey = "hip_0%s" % index
			else: hipKey = "hip_%s" % index
			if not hasattr( self.model, hipKey ): continue
			model = getattr( self.model, hipKey )
			if model is None: continue
			self.hipModels.append( model )

		for index in xrange( 1, 11 ):
			if index < 10: panKey = "pan_0%s" % index
			else: panKey = "pan_%s" % index
			if not hasattr( self.model, panKey ): continue
			model = getattr( self.model, panKey )
			if model is None: continue
			self.panModels.append( model )
		
	def getUSelectSize( self ):
		"""
		获取选择光圈大小
		配置大小按缩放倍率缩放
		"""
		uSelectSize = rds.npcModel.getUSelectSize( self.modelNumber )
		if uSelectSize != -1.0:
			uSelectSize *= self.modelScale
		return uSelectSize

	def onActionStart( self, actionName ):
		"""
		动作触发函数
		用于骑宠类模型的处理
		"""
		if actionName not in ACTION_MAPS: return
		if not self.inWorld: return
		for model in self.hipModels:
			rds.actionMgr.playAction( model, ACTION_MAPS[actionName][0] )
		for model in self.panModels:
			rds.actionMgr.playAction( model, ACTION_MAPS[actionName][1] )

	def resetWeaponType( self ):
		"""
		设置武器类型
		"""
		lefthandNum = self.lefthandNumber
		righthandNum = self.righthandNumber
		try:
			lNum = int( str( lefthandNum )[-6:-4] )
		except:
			lNum = Define.PRE_EQUIP_NULL
		try:
			rNum = int( str( righthandNum )[-6:-4] )
		except:
			rNum = Define.PRE_EQUIP_NULL
		# 如果左手为空或者为盾牌，则根据entity的右手武器来判断
		if lNum == Define.PRE_EQUIP_NULL or lNum == Define.PRE_EQUIP_SHIELD:
			try:
				type = Define.WEAPON_TYPE_MODEL_MAP[ rNum ]
			except:
				ERROR_MSG( "Can't find WeaponType Define by(%s)" % rNum )
				type = Define.WEAPON_TYPE_NONE

		else:

			if lNum == Define.PRE_EQUIP_BOW:
				type = Define.WEAPON_TYPE_BOW
			elif rNum == Define.PRE_EQUIP_NULL:
				type = Define.WEAPON_TYPE_NONE
			else:
				type = Define.WEAPON_TYPE_DOUBLEHAND
		self.weaponType = type

	def resetArmorType( self ):
		"""
		设置防具类型
		根据策划规则：首先判断entity左手是否装备盾牌
		再判断是否有胸甲，如果有则走职业对应防具类型路线
		如果没有则走策划自定义防具类型路线
		"""
		lefthandNum = self.lefthandNumber
		try:
			lNum = int( str( lefthandNum )[-6:-4] )
		except:
			lNum = Define.PRE_EQUIP_NULL
		if lNum == Define.PRE_EQUIP_SHIELD:
			type = Define.ARMOR_TYPE_SHIELD
		else:
			type = rds.spellEffect.getArmorTypeByNum( self.modelNumber )
		self.armorType = type

	def getWeaponType( self ):
		"""
		获取武器类型
		"""
		return self.weaponType

	def getArmorType( self ):
		"""
		获取防具类型
		"""
		return self.armorType

	def onSetLeftHandNumber( self, number ):
		"""
		define method.
		设置左手模型
		"""
		tnumber = self.lefthandNumber
		self.lefthandNumber = number
		self.set_lefthandNumber( tnumber )

	def onSetRightHandNumber( self, number ):
		"""
		define method.
		设置右手模型
		"""
		tnumber = self.righthandNumber
		self.righthandNumber = number
		self.set_righthandNumber( tnumber )

	def set_lefthandNumber( self, oldLefthandNumber = 0 ):
		"""
		左手装备模型
		"""
		if self.model is None: return
		if self.lefthandNumber == oldLefthandNumber: return

		# 重设武器防具类型
		self.resetWeaponType()
		self.resetArmorType()

		rds.itemModel.createModelBG( self.lefthandNumber, Functor( self._onLefthandModel, self.lefthandNumber,oldLefthandNumber ) )

	def _onLefthandModel( self, itemModelID, oldLefthandNumber, model ):
		"""
		左手武器模型加载回调，加载光效
		"""
		if self.model is None: return
		lefthandModel = model
		oldType = ( oldLefthandNumber / 10000 ) % 100
		newType = ( self.lefthandNumber / 10000 ) % 100
		if oldType == Define.PRE_EQUIP_SHIELD or newType == Define.PRE_EQUIP_SHIELD:
			equipPart = "left_shield"
		else:
			equipPart = "left_hand"

		if hasattr( self.model, equipPart ):
			if lefthandModel and not hasattr( lefthandModel, equipPart ):
				ERROR_MSG( "Can't find node(HP_%s) in (%s)" % ( equipPart, lefthandModel.sources ) )
			else:
				setattr( self.model, equipPart, lefthandModel )
		else:
			ERROR_MSG( "Can't find node(HP_%s) in (%s)" % ( equipPart, self.model.sources ) )

		# 光效
		effectIDs = rds.itemModel.getMEffects( itemModelID )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, self.getParticleType(), self.getParticleType() )
			effect.start()

	def set_righthandNumber( self, oldRighthandNumber = 0 ):
		"""
		右手装备模型
		"""
		if self.model is None: return
		if self.righthandNumber == oldRighthandNumber: return

		# 重设武器类型
		self.resetWeaponType()
		rds.itemModel.createModelBG( self.righthandNumber, Functor( self._onRighthandModel, self.righthandNumber ) )

	def _onRighthandModel( self, itemModelID, model ):
		"""
		右手武器模型加载回调，加载光效
		"""
		if self.model is None: return
		righthandModel = model
		if hasattr( self.model, "right_hand" ):
			if righthandModel and not hasattr( righthandModel, "right_hand" ):
				ERROR_MSG( "Can't find node(HP_right_hand) in (%s)" % ( righthandModel.sources ) )
			else:
				setattr( self.model, "right_hand", righthandModel )
		else:
			ERROR_MSG( "Can't find node(HP_right_hand) in (%s)" % ( self.model.sources ) )

		# 光效
		effectIDs = rds.itemModel.getMEffects( itemModelID )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, self.getParticleType(), self.getParticleType() )
			effect.start()


	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		获取随机动作，由于随机动作数量不固定，
		获取随机动作从random1开始，random2,random3....获取失败则返回
		"""
		#the range(1,10) is  provisional, because I can't find more than 2 randomActions for a entity
		for index in range(1,10):
			actName = "random"+str( index )
			if self.model.hasAction( actName ):
				self.randomActions.append( actName )
			else:
				return

	def onBored( self, actionName ):
		"""
		此回调用于播放随机动作
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""

		if actionName != "stand": return
		self.playRandomAction()
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
		#获取随机动作的数量
		randomActionCount = len( self.randomActions )
		if randomActionCount == 0:
			return
		else:
			matchCaps = [ Define.CAPS_RANDOM ]
			if self.righthandNumber or self.lefthandNumber:
				matchCaps.append(  Define.CAPS_WEAPON )
			else:
				matchCaps.append( Define.CAPS_NOWEAPON )
			if randomActionCount == 1:
				matchCaps.append( Define.CAPS_INDEX25 )
			else:
				index = random.randint( 0, randomActionCount - 1 )
				caps = Define.CAPS_INDEX25 + index
				matchCaps.append( caps )
			self.am.matchCaps = matchCaps

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
		# 只处理随机动作的过渡
		if Define.CAPS_RANDOM in self.am.matchCaps:
			self.setArmCaps()

	def onTargetFocus( self ):
		"""
		目标焦点事件
		"""
		if self.hasFlag(csdefine.ENTITY_FLAG_CAN_NOT_SELECTED):	#不可选择
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_CATCH ) and self.takeLevel == -1:
			self.canShowDescript = True
			self.cell.requestTakeLevel()
		else:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		NPCObject.onTargetFocus( self )
		if rds.ruisMgr.isMouseHitScreen():
			self.handleMouseShape()

	def handleMouseShape( self ):
		"""
		处理鼠标动画
		"""
		
		# 飞行状态下无攻击图标
		player = BigWorld.player()
		if player.hasFlag( csdefine.ROLE_FLAG_FLY ): # 飞行状态下的不显示可攻击的图标
			rds.ccursor.set( "normal" )
			return

		# 如果是自己的出战宠物，则不显示攻击图标 by mushuang
		player = BigWorld.player()
		pet = player.pcg_getActPet()
		if pet and pet.id == self.id:
			rds.ccursor.set( "normal" )
			return

		if self.flags != 0:
			if self.hasFlag(csdefine.ENTITY_FLAG_SPEAKER):		# 可以对话的
				rds.ccursor.set( "dialog" )
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_REPAIRER):	#修理工
				if self.isInteractionRange( BigWorld.player()):	#调用子类NPC的接口 判断当前是否能和该NPC直接交互  modified by hd(2008,9,16)
					rds.ccursor.set( "repair" )
				else:
					rds.ccursor.set( "repair" ,True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_BANK_CLERK):	#银行办事员
				if self.isInteractionRange( BigWorld.player()):	#调用子类NPC的接口 判断当前是否能和该NPC直接交互  modified by hd(2008,9,16)
					rds.ccursor.set( "storage" )
				else:
					rds.ccursor.set( "storage" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_EQUIP_MAKER):#装备制造
				if self.isInteractionRange( BigWorld.player()):	#调用子类NPC的接口 判断当前是否能和该NPC直接交互  modified by hd(2008,9,16)
					rds.ccursor.set( "calcine" )
				else:
					rds.ccursor.set( "calcine" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_SKILL_TRAINER):	#技能训练师
				if self.isInteractionRange( BigWorld.player()):	#调用子类NPC的接口 判断当前是否能和该NPC直接交互  modified by hd(2008,9,16)
					rds.ccursor.set( "skill" )
				else:
					rds.ccursor.set( "skill" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_PET_CARE):	#宠物保育
				if self.isInteractionRange( BigWorld.player()):	#调用子类NPC的接口 判断当前是否能和该NPC直接交互  modified by hd(2008,9,16)
					rds.ccursor.set( "petFoster" )
				else:
					rds.ccursor.set( "petFoster" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_POSTMAN):	#邮差
				if self.isInteractionRange( BigWorld.player()):	#调用子类NPC的接口 判断当前是否能和该NPC直接交互  modified by hd(2008,9,16)
					rds.ccursor.set( "mail" )
				else:
					rds.ccursor.set( "mail" , True)
				return
			elif self.hasFlag(csdefine.ENTITY_FLAG_CHAPMAN):	#商人
				if self.isInteractionRange( BigWorld.player()):	#如果他只具有商人的功能那么显示商人 鼠标
					rds.ccursor.set( "trade" )
				else:
					rds.ccursor.set( "trade" , True)
				return



		if BigWorld.player().queryRelation( self ) == csdefine.RELATION_ANTAGONIZE :
			rds.ccursor.set( "attack" )
			return

		#如果不具备其他功能,那么显示正常图标
		rds.ccursor.set( "normal" )		# modified by hyw( 2008.08.29 )


	# Quitting as target
	def onTargetBlur( self ):
		"""
		离开目标事件
		"""
		self.canShowDescript = False
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		NPCObject.onTargetBlur( self )
		if rds.ccursor.shape == "hand" or \
			rds.ccursor.shape == "attack" :		# modified by hyw( 2008.08.29 )
				rds.ccursor.set( "normal" )

	def receiveTakeLevel( self, takeLevel ):
		"""
		Define method.
		接收携带等级

		@param takeLevel : 携带等级
		@type takeLevel : UINT16
		"""
		self.takeLevel = takeLevel
		if self.canShowDescript:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )

	def getTakeLevel( self ):
		"""
		"""
		return  self.takeLevel

	def onTargetClick( self, player ):
		"""
		目标点击事件
		@type	player	:	instance
		@param	player	:	玩家实例
		@rtype			:	int
		@return			:	TARGET_CLICK_FAIL 点击失败, TARGET_CLICK_SUCC 点击成功,TARGET_CLICK_MOVE 点击移动
		"""
		NPCObject.onTargetClick( self, player )

	def onReviviscence( self ):
		"""
		复活事件
		"""
		rds.effectMgr.createParticleBG( self.getModel(), "HP_root", "particles/fuhuo/fuhuo.xml", detachTime = 3.0, type = Define.TYPE_PARTICLE_NPC )

	def onStateChanged( self, old, new ):
		"""
		virtual method.
		状态切换。

		@param old	:	更改以前的状态
		@type old	:	integer
		@param new	:	更改以后的状态
		@type new	:	integer
		"""
		CombatUnit.onStateChanged( self, old, new )
		if old == csdefine.ENTITY_STATE_HANG:
			self.setVisibility( True )
		if new == csdefine.ENTITY_STATE_HANG:
			self.setVisibility( False )
		return


	def set_state( self, oldState = None ):
		CombatUnit.set_state( self, oldState )
		if self.state == csdefine.ENTITY_STATE_DEAD:
			self.onDieSound()	# 怪物死亡音效 jy
			self.onDie()
			for linkEffect in self.linkEffect:
				linkEffect.stop()
			self.linkEffect = []
		elif self.state == csdefine.ENTITY_STATE_FIGHT:
			print "%s %d fight." % (self.getName(), self.id)
			self.onFightSound()	# 怪物进入战斗音效 jy
			if self.hasFlag( csdefine.ENTITY_FLAG_ONLY_FACE_LEFT_OR_RIGHT ):
				self.am.turnModelToEntity = False
				self.startFaceTimer()
			ECenter.fireEvent( "EVT_ON_MONSTER_FIGHT_STATE_CHANGE", self )
		else:
			if self.hasFlag( csdefine.ENTITY_FLAG_ONLY_FACE_LEFT_OR_RIGHT ):
				self.stopFaceTimer()
			ECenter.fireEvent( "EVT_ON_NPC_QUEST_STATE_CHANGED", self, self.questStates )
		self.setArmCaps()

	def onDie( self ):
		"""
		"""
		print "%s %d dead." % (self.getName(), self.id)
		if not self.isBlastFlag: #不符合播放碎裂效果的add by wuxo 2011-11-18
			BigWorld.callback( 0.5, self.playDieEvent ) #延迟回调是为了让隐藏更顺利
		self.setSelectable( False )
		rds.targetMgr.unbindTarget( self )	#怪物死亡时丢失目标modify by wuxo

	def playDieEvent(self):
		"""
		在AOI范围内所有的玩家客户端播放死亡镜头事件
		"""
		if not self.inWorld : return
		actionNameL =  [ Const.MODEL_ACTION_DIE,Const.MODEL_ACTION_DEAD ]
		eventID = 0

		actionAndevent = rds.npcModel.getDieEvent( self.modelNumber )
		if actionAndevent != "" :
			ae = actionAndevent.split(";")
			if len( ae ) > 0:
				actionNameL =  [ ae[0], Const.MODEL_ACTION_DEAD ]
			if len( ae ) > 1:
				eventID = int( ae[1] )
		if eventID != 0:
			rds.cameraEventMgr.trigger( eventID )
		rds.actionMgr.playActions( self.getModel(), actionNameL, callbacks = [ self.onFinishDieAction ] )

	# ----------------------------------------------------------------
	def queryRelation( self, entity ):
		"""
		virtual method.
		取目标和自己的关系

			角色与自己--友好
			角色与队友--友好
			角色与角色--友好（暂不考虑PK系统）
			角色与NPC--友好
			角色与非主动攻击怪物--中立
			角色与主动攻击怪物--敌对
			NPC与NPC（包含怪物之间）--中立

		@param entity: 目标玩家
		@param entity: 任何PYTHON原类型(建议使用数字或字符串)
		return : 关系 C_RELATION_FRIEND | C_RELATION_NEUTRALLY | C_RELATION_ANTAGONIZE
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			entity = entity.getRelationEntity()
			if entity:
				return self.queryCombatRelation( entity )
			else:
				return csdefine.RELATION_FRIEND
				
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			player = BigWorld.player()
			if self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				pid = self.ownerVisibleInfos[ 0 ]
				tid = self.ownerVisibleInfos[ 1 ]
				if pid == player.id or tid == player.teamID:
					return csdefine.RELATION_ANTAGONIZE
				else:
					return csdefine.RELATION_NOFIGHT

		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY

		return csdefine.RELATION_NEUTRALLY

	def onFinishDieAction( self ):
		BigWorld.callback( random.uniform( 1.0, 4.0), self.hideEntitymodel )

	def hideEntitymodel( self ):
		if not self.inWorld: return
		if self.hasFlag( csdefine.ENTITY_FLAG_CLOSE_FADE_MODEL ): return
		rds.effectMgr.fadeOutModel( self.getModel(),0.5 )

	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_FLY ):
			return  BigWorld.AvatarFilter()
		else:
			return BigWorld.AvatarDropFilter()

	def hideModelNow(self):
		"""
		直接隐藏模型，无延迟，无淡入淡出
		"""
		model = self.getModel()
		if model:
			model.visible = False

	def showSkillName( self, skillID ):
		"""
		显示技能名称
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SKILL_NAME", self.id, skillID )	 # 显示释放技能的名称
		
	def playBlastEffect( self, effect ):	
		self.isBlastFlag = True #写在这里的原因是为了容错  即使该怪物配置了碎裂效果  但是碎裂效果不存在/错误 都认为其碎裂效果没有
		BigWorld.callback( 0.3, self.hideModelNow )
		self.hideNameUI()
		effect.start()

	def onReceiveDamage( self, casterID, skill, damageType, damage ):
		"""
		伤害显示
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skill : 技能
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		CombatUnit.onReceiveDamage( self, casterID, skill, damageType, damage )
		#增加伤害判断和技能ID判断 是否播放爆尸效果add by wuxo 2011-11-17
		sk = skill
		skillid = None
		try:
			skillid = int(str(sk.getID())[:6])
		except:
			skillid = sk.getID()
		if self.HP <= damage:	#怪物死亡
			if  skillid not in MONSTERBLASTDATAS[1]:	#技能符合条件
				#死亡是否播放碎裂效果 add by wuxo 2011-11-17
				if self.className not in MONSTERBLASTDATAS[0]:
					model = self.getModel()
					if model:
						infos = rds.npcModel._datas[self.modelNumber]
						effectID = infos.get( "blast_effect", "" ) #效果由单纯的粒子效果改为光效modify by wuxo 2011-12-22
						type = self.getParticleType()
						effect = rds.skillEffect.createEffectByID( effectID, model, model, type, type )
						if effect :
							if self.__class__.__name__ in ["YXLMBoss", "MiniMonster_Lol"]:
								BigWorld.callback( 0.5, Functor( self.playBlastEffect, effect ) )
							else:
								self.playBlastEffect( effect )
		player = BigWorld.player()
		petID = -1
		pet = player.pcg_getActPet()
		if pet:
			petID = pet.id
		if casterID != player.id and casterID != petID :
			return
		self.onDamageSound()	# 受攻击音效 jy
		if damage > 0:
			if self.className in [item["bossID"] for item in bossGetHitDatas]:	
				if skillid in [item["skillID"] for item in skillCauseDatas]:					#具有使模型高亮的技能
					rds.effectMgr.setModelColor(self.model, (2.5,2.5,2.5,2.5), (1.0,1.0,1.0,1.0), 0.5)
				self.model.pitch = -0.5
				self.pitchModelcbid = BigWorld.callback( 0.3, self.disPitchModel )
			if ( damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
				# 致命伤害
				ECenter.fireEvent( "EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE", self.id, str( damage ) )
				if self.className in [item["bossID"] for item in bossGetHitDatas]:
					rds.effectMgr.setModelColor(self.model, (2.5,2.5,2.5,2.5), (1.0,1.0,1.0,1.0), 0.5)
			else:
				# 普通伤害
				ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( damage ) )
		else:
			# Miss
			ECenter.fireEvent( "EVT_ON_SHOW_MISS_ATTACK", self.id )

		# 技能产生伤害时的系统信息等处理
		if casterID == player.id:					# 自己是施法者
			if damage > 0:
				if ( damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s招架了你的%s，受到%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_FROM_SKILL, self.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# 你的%s暴击对%s造成%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_TO, sk.getName(), self.getName(), damage )
				else:
					if (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
						if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:
							# %s受到你反弹的%i点法术伤害。
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC_TO, self.getName(), damage )
						else:
							# %s受到你反弹的%i点伤害。
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_PHY_TO, self.getName(), damage )
					else:
						# 你的%s对%s造成了%i的伤害。
						player.statusMessage( csstatus.SKILL_SPELL_DAMAGE_TO, sk.getName(), self.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s闪躲了你的%s。
					player.statusMessage( csstatus.SKILL_SPELL_DODGE_FROM_SKILL, self.getName(), sk.getName() )
		elif casterID == petID: 					# 宠物是施法者
			if damage > 0:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s招架了你的宠物的%s，受到%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_PET_RESIST_HIT_FROM_SKILL, self.getName(), pet.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# 宠物的%s暴击对%s造成%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_PET_DOUBLEDAMAGE_TO, pet.getName(), sk.getName(), self.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
					if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:

						# 反震效果触发，对敌人造成%i点法术伤害。
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_MAGIC_TO, damage )
					else:

						# 反震效果触发，对敌人造成%i点伤害。
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_PHY_TO, damage )
				else:
						# 宠物的%s对%s造成了%i的伤害。
						player.statusMessage( csstatus.SKILL_SPELL_PET_DAMAGE_TO, pet.getName(), sk.getName(), self.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s闪躲了宠物的%s。
					player.statusMessage( csstatus.SKILL_SPELL_PET_DODGE_TO, self.getName(), pet.getName(), sk.getName() )
	
	def disPitchModel( self ):
		"""
		"""
		if self.pitchModelcbid > 0:
			BigWorld.cancelCallback( self.pitchModelcbid )
			self.pitchModelcbid = 0
		self.model.pitch = 0.0

	def getVisibility( self ) :
		"""
		有些实体类型使用self.models来作为表现，这个时候visible的处理就应该针对models
		"""
		model = self.getModel()
		if model:
			return model.visible
		return False

	def initCacheTasks( self ):
		"""
		初始化缓冲器任务
		"""
		NPCObject.initCacheTasks( self )
		CombatUnit.initCacheTasks( self )
		self.addCacheTask( csdefine.ENTITY_CACHE_TASK_TYPE_MONSTER0 )

# ------------------------------------------------------------------------------
# 怪物音效 by姜毅
# ------------------------------------------------------------------------------
	def playSound( self, soundName ):
		"""
		播放怪物声音
		@param entity	:	声音播放的位置
		@type entity	:	entity
		@param soundName:	声音文件对应的字段名
		@type soundName	:	string
		"""
		# rds.spellEffect.getNormalCastSound( weaponType )
		model = self.getModel()
		if model is None: return
		soundMgr.playVocality( soundName, model )

	def onFightSound( self ):
		"""
		怪物进入战斗音效
		"""
		if not self.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnFightSound( self.modelNumber )	# 获取怪物进入战斗音效
		if len( soundNames ) <= 0 :
			print "get monster FightSound null"
			return
		soundName = random.choice( soundNames )
		self.playSound( soundName )	# 播放怪物进入战斗音效

	def onDieSound( self ):
		"""
		怪物死亡音效
		"""
		if not self.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnDieSound( self.modelNumber )	# 获取怪物死亡音效
		if len( soundNames ) <= 0 :
			print "get monster DieSound null"
			return
		soundName = random.choice( soundNames )
		self.playSound( soundName )	# 播放怪物死亡音效

	def onDamageSound( self ):
		"""
		怪物受攻击音效
		"""
		if not self.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		soundNames = rds.npcModel.getMonsterOnDamageSound( self.modelNumber )	# 获取怪物受攻击音效
		if len( soundNames ) <= 0 :
			print "get monster DamageSound null"
			return
		soundName = random.choice( soundNames )
		self.playSound( soundName )	# 播放怪物受攻击音效

	def queryBootyOwner( self ) :
		"""
		向服务器申请怪物归属权信息
		"""
		if self.state == csdefine.ENTITY_STATE_FIGHT :
			self.cell.queryBootyOwner()

	def onSetBootyOwner( self, bootyOwner ) :
		"""
		defined method
		@param	bootyOwner		: 归属权信息
		@type	bootyOwner		: tuple of OBJECT_ID: ( ownerID, teamID )
		"""
		self.bootyOwner = bootyOwner
		player = BigWorld.player()
		if player.targetEntity and player.targetEntity.id == self.id :			# 如果玩家当前目标就是该怪物
			if ( bootyOwner[1] == player.teamID and bootyOwner[1] != 0 ) or \
			bootyOwner[0] in player.teamMember or bootyOwner[0] == player.id \
			or bootyOwner == ( 0, 0 ) :
				ECenter.fireEvent( "EVT_ON_SET_TARGET_BOOTY_OWNER", True )
			else :
				ECenter.fireEvent( "EVT_ON_SET_TARGET_BOOTY_OWNER", False )


	def onSetAsTarget( self ):
		"""
		define method
		"""
		rds.targetMgr.bindTarget( self )

	#----------------------------------------------------------------

	def outputCallback1( self, moveDir, needTime,a, dTime ):
		"""
		filter的位置刷新回调函数
		模拟重力加速度，以抛物线的方式运动
		"""
		yMoveDir =  Math.Vector3(0,1.0,0)
		self.moveTime += dTime
		if self.moveTime >= needTime:
			BigWorld.callback( 0.01, self._onMoveOver )
			return self.position
		else:
			return self.position + moveDir * dTime - yMoveDir * self.dertaHight( self.moveTime, dTime, a )

	def dertaHight( self, t1, t, a = 9.8 ):
		"""
		高度差Δh，a:加速度默认为9.8，t1:结束时间,t:时间差
		"""
		return ( t1 - 0.5 * t ) * a * t

	def throwToPoint( self, position, speed ):
		"""
		带加速度的抛物线运动到坐标点
		"""
		yawDir = position - self.position
		xYawDir = Math.Vector3(yawDir[0],0,yawDir[2])
		xYawDir.normalise()
		xMoveDir = xYawDir * speed
		distance = self.position.flatDistTo( position )
		needTime = distance / speed
		a = 2 * abs(yawDir[1]) / ( needTime * needTime )
		func = Functor( self.outputCallback1, xMoveDir, needTime, a )
		self.moveTime = 0.0
		if not hasattr(self.filter,"outputCallback"):
			self.filter = BigWorld.AvatarDropFilter()
		self.filter.outputCallback = func

	def actionToPoint( self, position, speed ):
		"""
		跳到坐标点
		"""
		rds.actionMgr.stopAction( self.model, rds.npcModel.getStandbyAction( self.modelNumber ) )
		vPosition = Math.Vector3( self.position - position )
		vPosition[1] = 0          # 只计算XOZ平面的移动
		self.throwToPoint( position, speed )
		time = vPosition.length/speed
		self.playAction( time-0.2 )

	def playAction( self,time2 ):
		"""
		起跳
		"""
		# 1 是初始，2是起跳动作能预订时间完成，3是起跳动作不能预订时间完成
		actionNames = rds.npcModel.getPreAction( self.modelNumber )
		preEffectIDs = rds.npcModel.getPreEffect( self.modelNumber )
		self.startOver = 1
		# 这样写 为了使得至少入场动作的start动作能播放完成
		def onStartActionCompleted():
			if self.startEffect:
				self.startEffect.stop()
			if self.startOver == 1:
				self.startOver = 2
				self.loopEffect = self.playEffect( preEffectIDs[1] )
			if self.startOver == 3:
				def stopEndEffect():
					if self.endEffect:
						self.endEffect.stop()
				rds.actionMgr.playAction( self.model, actionNames[2], 0, stopEndEffect )
				def shake():
					rds.worldCamHandler.cameraShell.camera_.shake(0.3,(0.1,0.2,0.1))
				BigWorld.callback( 0.2, shake )
				if self.loopEffect:
					self.loopEffect.stop()
				self.endEffect = self.playEffect( preEffectIDs[2] )  # 播放结束光效

		def onEndActionStart():
			if self.startOver == 1:
				self.startOver = 3
			if self.startOver == 2:
				def stopEndEffect():
					if self.endEffect:
						self.endEffect.stop()
				rds.actionMgr.playAction( self.model, actionNames[2], 0 ,stopEndEffect )
				def shake():
					rds.worldCamHandler.cameraShell.camera_.shake(0.3,(0.1,0.2,0.1))
				BigWorld.callback( 0.2, shake )
				if self.startEffect:
					self.startEffect.stop()
				if self.loopEffect:
					self.loopEffect.stop()
				self.endEffect = self.playEffect( preEffectIDs[2] )

		rds.actionMgr.playActions( self.model, [actionNames[0],actionNames[1]], 0, [onStartActionCompleted,None])
		if preEffectIDs:
			self.startEffect = self.playEffect( preEffectIDs[0] )   # 播放start光效
		BigWorld.callback( time2, onEndActionStart )

	def playEffect( self, effectID ):
		"""
		播放光效,并返回播放的光效
		"""
		effect = rds.skillEffect.createEffectByID( effectID, self.model, self.model, Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if effect:
			effect.start()
			return effect

	def playAdmissionAction( self ):
		"""
		播放无位移的入场动作,停止播放待机光效，开始播放入场光效
		"""
		rds.actionMgr.stopAction( self.model, rds.npcModel.getStandbyAction( self.modelNumber ) )   # 终止入场动作
		if not self.admisActionFlag :
			self.admisActionFlag = True
			self.am.turnModelToEntity = False
			def callback():
				self.am.turnModelToEntity = True
				if self.adminEffect:
					self.adminEffect.stop()
				self.showNameUI( )
			preAction = rds.npcModel.getPreAction( self.modelNumber )
			self.adminEffect = self.playAdmissionEffect()
			rds.actionMgr.playAction( self.model, preAction,0,callback )


	def playAdmissionEffect( self ):
		"""
		停止待机光效，开始播放入场光效
		"""
		if self.standbyEffect:
			self.standbyEffect.stop()
		preEffectID = rds.npcModel.getPreEffect( self.modelNumber )
		admissionEffect = rds.skillEffect.createEffectByID( preEffectID, self.model, self.model, Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if admissionEffect:
			admissionEffect.start()
			return admissionEffect

	def playStandbyAction( self ):
		"""
		播放待机动画,并待机播放光效
		"""
		standbyAction = rds.npcModel.getStandbyAction( self.modelNumber )
		standbyEffectID = rds.npcModel.getStandbyEffect( self.modelNumber )
		if not ( standbyAction or standbyEffectID ):return
		self.hideNameUI( )
		self.model.visible = False      # 为了防止播放一个从地上到待机动作的过度
		if standbyAction :
			rds.actionMgr.playAction( self.model, standbyAction )
		self.standbyEffect = rds.skillEffect.createEffectByID( standbyEffectID, self.model, self.model, Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if self.standbyEffect:
			self.standbyEffect.start()
		def callback():
			if self.model:
				self.updateVisibility()
		BigWorld.callback( 0.5, callback )
	
	def hideNameUI( self ):
		"""
		隐藏头顶相关UI
		"""
		self.uiAttachsShow = False
		model = self.getModel()
		try:
			node = model.node("HP_title")
		except:
			node = None
		if not node : return
		for ui in node.attachments:
			ui.component.visible = False #隐藏名字血条UI
		
	def showNameUI( self ):
		"""
		显示头顶相关UI
		"""
		self.uiAttachsShow = True
		self.notifyAttachments_( "onEnterWorld" )

	def onPlayActionOver( self, actionNames ):
		"""
		动作结束完成回调
		"""
		CombatUnit.onPlayActionOver( self, actionNames )
		if len( actionNames ) == 0: return
		if self.rotateTarget and self.rotateAction == actionNames[0]:
			self.rotateToTarget( self.rotateTarget )
			self.rotateTarget = None
			self.rotateAction = ""

	# ------------------------------------------------------------------------------
	# 横版副本怪物
	# ------------------------------------------------------------------------------
	def getFaceYaw( self ):
		"""
		get the face yaw
		"""
		target = BigWorld.entities.get( self.targetID )
		if target is None: return Const.ENTITY_FACE_LEFT_YAW

		yaw = ( target.position - self.position ).yaw

		if math.fabs( yaw - Const.ENTITY_FACE_LEFT_YAW ) <= math.pi/2.0:
			return Const.ENTITY_FACE_LEFT_YAW
		return Const.ENTITY_FACE_RIGHT_YAW

	def startFaceTimer( self ):
		"""
		start the face to Timer
		"""
		return
		if not self.inWorld: return

		self.model.yaw = self.getFaceYaw()
		#self.filter.setYaw( self.getFaceYaw() )
		self.faceTimerID = BigWorld.callback( Const.ENTITY_FACE_TO_TIME, self.startFaceTimer )

	def stopFaceTimer( self ):
		"""
		stop the face to Timer
		"""
		return
		if self.faceTimerID == 0: return
		BigWorld.cancelCallback( self.faceTimerID )
		self.am.turnModelToEntity = True
		self.faceTimerID = 0
	
	def jumpBackFC( self ):
		"""
		Define Method
		服务器通知向后跳
		"""
		model = self.model
		if model:
			if model.hasAction( Const.MODEL_ACTION_MAGIC_CAST ):
				rds.actionMgr.playAction( model, Const.MODEL_ACTION_MAGIC_CAST )

	def set_flags( self, oldFlag ):
		"""
		Monster的flags标记被设置时调用
		"""
		NPCObject.set_flags( self, oldFlag )
		self.setArmCaps()

	def setArmCaps( self ):
		"""
		动作匹配caps
		"""
		if not self.inWorld: return
		armCaps = []
		if self.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_LIE_DOWN ):
			armCaps.append( Define.CAPS_LIE_DOWN )      # 在普通状态下匹配躺下动作,但是这个动作实际是dead动作来实现
		if self.hasFlag( csdefine.ENTITY_FLAG_RAD_FOLLOW_ACTION ) and self.state == csdefine.ENTITY_STATE_FIGHT:
			armCaps.append( Define.CAPS_RADIFOLLOW )	# 在有游荡标志位并且是在战斗状态下才会匹配游荡Caps
		if self.findBuffByBuffID( Const.VERTIGO_BUFF_ID1 ) or self.findBuffByBuffID( Const.VERTIGO_BUFF_ID2 ): # 眩晕buff存在
			armCaps.append( Define.CAPS_VERTIGO )

		stateCaps = Define.MONSTER_CAPS.get( self.state, 0 )
		self.am.matchCaps = [stateCaps] + armCaps

	def setFilterYaw( self, yaw ):
		"""
		define method
		用于设置不动物体的方向。
		//瞬间改变朝向，不会有缓冲过程 csol-2739
		"""
		if not self.inWorld: return
		if hasattr( self.filter, "latency" ):
			self.filter.latency = 0.0
		NPCObject.setFilterYaw( self, yaw )

	def intonate( self, skillID, intonateTime, targetObject ):
		"""
		Define method.
		吟唱法术

		@type skillID: INT
		"""
		CombatUnit.intonate( self, skillID, intonateTime, targetObject )
		# 吟唱过程中实时转向
		sk = skills.getSkill( skillID )
		func = Functor( self.rotateToTarget, targetObject )
		if sk and not sk.isNotRotate:
			self.rotateTimerID = Timer.addTimer( 0.1, 0.1, func )

	def rotateToTarget( self, targetObject ):
		"""
		转向目标
		"""
		if not self.inWorld: return

		if self.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			return

		effectState = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP
		if not ( self.effect_state & effectState ) == 0: #禁止转向的判定
			return
		position = targetObject.getObjectPosition()
		disPos = position - self.position
		yaw = disPos.yaw
		if math.fabs( yaw ) > 0.0:
			if hasattr( self.filter, "setYaw" ):
				self.filter.setYaw( yaw )
			model = self.getModel()
			if model: model.yaw = yaw

	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		法术中断

		@type reason: INT
		"""
		CombatUnit.spellInterrupted( self, skillID, reason )
		if self.rotateTimerID != 0:
			Timer.cancel( self.rotateTimerID )
			self.rotateTimerID = 0

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		正式施放法术——该起施法动作了

		@type skillID: INT
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		CombatUnit.castSpell( self, skillID, targetObject )
		if self.rotateTimerID != 0:
			Timer.cancel( self.rotateTimerID )
			self.rotateTimerID = 0

# Monster.py
