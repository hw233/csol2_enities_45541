
# -*- coding: gb18030 -*-
#
# $Id: Role.py,v 1.471 2008-09-05 09:27:54 yangkai Exp $

#-------------------------------------------------
# Python
import time
import sys
import math
import random
import base64
import zlib
import copy

#-------------------------------------------------
# Engine
import BigWorld
import csol
import GUI
import Language
import Pixie
import Math

#-------------------------------------------------
# Common
import csdefine
import csconst
import csstatus
import csstatus_msgs as StatusMsgs
from bwdebug import *
from Function import Functor
import ItemTypeEnum
import csarithmetic
from LevelEXP import VehicleLevelExp
import Function
import SkillTargetObjImpl

# 帮会技能
from TongDatas import tongSkill_instance
g_tongSkills = tongSkill_instance()
#-------------------------------------------------
# Client
import love3
import keys
import gbref
import Define
import Const
import event.EventCenter as ECenter
import skills
import items
import PackChecker
import ActivitySchedule
import GUIFacade

from gbref import rds
from UnitSelect import UnitSelect
from RoleMaker import RoleInfo
from RoleMaker import getDefaultRoleInfo
from ItemsFactory import ItemsFactory
from ItemsFactory import SkillItem as SkillItemInfo
from ItemsFactory import ObjectItem as ObjectItemInfo
from MessageBox import *
from Sound import soundMgr
from interface.Team import PreInviteTemmateStatus
import Time
from LabelGather import labelGather
from items.ItemDataList import ItemDataList

g_items = ItemDataList.instance()

from CameraEventMgr import CameraEventStatus
from QuestPatrolMgr import patrolMgr
from LivingConfigMgr import LivingConfigMgr

lvcMgr = LivingConfigMgr.instance()

# role's base class
from interface.GameObject import GameObject
from interface.OPRecorder import OPRecorder
from interface.CombatUnit import CombatUnit
from interface.ItemsBag import ItemsBag
from interface.Team import Team
from interface.RoleQuestInterface import RoleQuestInterface
from interface.RoleChat import RoleChat
from interface.RoleChangeBody import RoleChangeBody
from interface.RoleImageVerify import RoleImageVerify
from interface.QuickBar import QuickBar
from interface.SpaceFace import SpaceFace
from interface.PetCage import PetCage
from interface.RoleCommissionSale import RoleCommissionSale
from config.client.msgboxtexts import Datas as mbmsgs
from guis.general.npctalk.LevelUpAwardReminder import LevelUpAwardReminder
from guis.general.commissionsale.CommissionSale import CommissionSale
from interface.Bank import Bank
from interface.RoleMail import RoleMail
from interface.RoleRelation import RoleRelation
from interface.TongInterface import TongInterface
from interface.RoleCredit import RoleCredit
from interface.RoleGem import RoleGem
from interface.RoleSpecialShop import RoleSpecialShop
from EspialTarget import espial
from EspialTargetRemotely import espialRemotely
from interface.HorseRacer import HorseRacer
from interface.LotteryItem import LotteryItem
from interface.RoleQuizGame import RoleQuizGame
from AttrChangeMgr import attrChangeMgr
from LevelEXP import RoleLevelEXP
from interface.GameRanking import GameRanking
from interface.LivingSystem import LivingSystem
from interface.ScrollCompose import ScrollCompose
from interface.YuanBaoTradeInterface import YuanBaoTradeInterface
from FlyingVehicle import FlyingVehicle
from VehicleHelper import isFlying,getVehicleToItemNeed,getNextStepItemID
from interface.RoleEidolonHandler import RoleEidolonHandler
from config.client.VehicleActionFreq import Datas as VehiFreqDatas
from interface.RoleChallengeSpaceInterface import RoleChallengeSpaceInterface
from interface.RoleChallengeInterface import RoleChallengeInterface
from interface.RoleUpgradeSkillInterface import RoleUpgradeSkillInterface
from interface.RolePlotLv40Interface import RolePlotLv40Interface
from interface.SpaceViewerInterface import SpaceViewerInterface
from interface.RoleStarMapInterface import RoleStarMapInterface
from interface.CopyMatcherInterface import CopyMatcherInterface
from interface.BaoZangCopyInterface import BaoZangCopyInterface
from interface.RoleYeZhanFengQiInterface import RoleYeZhanFengQiInterface
from interface.ZhengDaoInterface import ZhengDaoInterface
from interface.RoleDestinyTransInterface import RoleDestinyTransInterface
from interface.Fisher import Fisher
from interface.TDBattleInterface import TDBattleInterface
from interface.RoleYiJieZhanChangInterface import RoleYiJieZhanChangInterface
from interface.RoleJueDiFanJiInterface import RoleJueDiFanJiInterface
from interface.RoleCopyInterface import RoleCopyInterface

from config.client.QuestSpaceCameraConfig import Datas as questConfig
from config.RoleVendConfig import Datas as roleVendData
from config.client.labels import ChatFacade as lbs_ChatFacade
from config.client.SpaceHeightConfig import Datas as spaceHeightDatas

# player role's base class
import Action
from Attack import Attack
from test import Skill_test
from test import Item_test
from keys import *
from Guide import Guide
# --------------------------------------------------------------------
# 以上 import 请按归类排放
# mapArea 以放到 gbref.rds 中
# --------------------------------------------------------------------

class Role(
	GameObject,
	OPRecorder,							# 操作记录管理
	CombatUnit,							# 角色基类类
	ItemsBag,							# 背包( phw )
	Team,								# 组队信息
	RoleQuestInterface,
	RoleChangeBody,                                                 #变身
	RoleChat, 							# 接收服务器返回的消息类
	RoleImageVerify,
	QuickBar,							# 快捷栏( huangyongwei )
	SpaceFace,
	PetCage,							# 宠物圈
	RoleCommissionSale,					# 寄卖功能
	Bank,								# 钱庄( wangshufeng )
	RoleMail,							# 邮件功能
	RoleRelation,						# 玩家关系( wangshufeng )
	TongInterface,						# 帮会系统(kebiao)
	RoleCredit,							# 处理玩家信誉( wangshufeng )
	RoleGem,							# 处理玩家经验石( wangshufeng )
	RoleSpecialShop,					# 玩家道具商城( wangshufeng )
	HorseRacer,							# 赛马
	LotteryItem,						# 锦囊(hd)
	RoleQuizGame,						# 知识问答( wsf )
	GameRanking,						# 排行榜
	LivingSystem,						# 生活系统( jy )
	ScrollCompose,                  #制作卷轴配方
	YuanBaoTradeInterface,				# 元宝交易( jy )
	RoleEidolonHandler,
	RoleChallengeSpaceInterface,		# 挑战副本
	RoleChallengeInterface,				# 竞技
	RoleUpgradeSkillInterface,			# 技能升级
	RolePlotLv40Interface,				# 40级剧情副本
	SpaceViewerInterface, 				# 副本观察者
	RoleStarMapInterface,				# 星际地图
	CopyMatcherInterface,				# 副本组队系统方法接口
	BaoZangCopyInterface,				# 宝藏副本接口( 英雄联盟 )
	RoleYeZhanFengQiInterface,			# 夜战凤栖战场
	ZhengDaoInterface,					# 证道系统
	RoleDestinyTransInterface,			# 天命轮回副本接口
	Fisher,								# 捕鱼达人
	TDBattleInterface,					# 仙魔论战
	RoleYiJieZhanChangInterface,			# 异界战场
	RoleJueDiFanJiInterface,			# 绝地反击接口
	RoleCopyInterface,					#副本接口
	 ):

	def __init__( self ):
		GameObject.__init__( self )
		CombatUnit.__init__( self )
		ItemsBag.__init__( self )
		Bank.__init__( self )
		Team.__init__( self )
		RoleQuestInterface.__init__( self )
		RoleChat.__init__( self )
		RoleImageVerify.__init__( self )
		SpaceFace.__init__( self )
		QuickBar.__init__( self )
		PetCage.__init__( self )
		RoleCommissionSale.__init__(self)
		RoleMail.__init__(self)
		RoleRelation.__init__( self )
		TongInterface.__init__( self )
		RoleCredit.__init__( self )
		RoleGem.__init__( self )
		RoleSpecialShop.__init__( self )
		HorseRacer.__init__( self )
		LotteryItem.__init__( self )
		RoleQuizGame.__init__( self )
		GameRanking.__init__( self )
		LivingSystem.__init__( self )
		ScrollCompose.__init__( self )
		RoleEidolonHandler.__init__( self )
		RoleChallengeSpaceInterface.__init__( self )
		RoleChallengeInterface.__init__( self )
		RoleUpgradeSkillInterface.__init__( self )
		RolePlotLv40Interface.__init__( self )
		SpaceViewerInterface.__init__( self )
		RoleStarMapInterface.__init__( self )
		CopyMatcherInterface.__init__( self )
		BaoZangCopyInterface.__init__( self )
		RoleYeZhanFengQiInterface.__init__( self )
		ZhengDaoInterface.__init__( self )
		RoleDestinyTransInterface.__init__( self )
		Fisher.__init__( self )
		TDBattleInterface.__init__( self )
		RoleYiJieZhanChangInterface.__init__( self )
		RoleJueDiFanJiInterface.__init__( self )
		RoleCopyInterface.__init__( self )

		self.flyTelModelNum = None
		self.armCaps = []
		self.setSelectable( True )
		self.selectable = True
		if not hasattr( self, "_attrCooldowns" ):
			self._attrCooldowns = {}
		self.tradeState = csdefine.TRADE_NONE
		self.skillList_ = []				# 技能ID 列表
		self.vehicleSkillList_ = []			# 骑宠技能id列表
		self.targetItems = []				# 观察对方时记录对方的装备ID
		self.espial_id = 0					# 记录观察的对方的ID
		self.firstHit = False	# 玩家的是否第一次被攻击,用于配合receiveSpell判断玩家受到的本次攻击是否是第一次(玩家改变为战斗状态总是比受到攻击先)
		# 默认武器类型为空手
		self.weaponType = Define.WEAPON_TYPE_NONE
		# 默认防具类型为无防具
		self.armorType = Define.ARMOR_TYPE_EMPTY
		# 记录玩家当前的法宝模型
		self.talismanModel = None
		self.isLoadModel = False #是否正在下坐骑
		self.delayActionNames = []#模型加载未完成时播放的动作回调集合（比如下坐骑中放技能）
		self.delayCastEffects = [] #模型加载未完成时播放的光效回调集合（比如下坐骑中放技能）

		# 玩家的当前Area
		self._oldArea = None
		self._oldSpaceNumber = -1			# 记录上一次所在的副本唯一id
		self.money = 0
		self.EXP = 0

		self.randomActionsWithWeapon = []	# 有武器随机动作列表
		self.randomActionsWithDanWeapon = []	# 单手剑武器随机动作列表
		self.randomActionsWithShuangWeapon = []	# 双手剑武器随机动作列表
		self.randomActionsWithFuWeapon = []		# 斧头武器随机动作列表
		self.randomActionsWithChangWeapon = []	# 长枪武器随机动作列表
		self.randomActionsNoWeapon = []		# 无武器随机动作列表

		self.equipEffects = []				# 玩家装备模型相关附加粒子
		self.vehicleEffects = []			# 坐骑模型相关附加粒子

		self.gold = 0
		self.silver = 0
		self.queryASTimerID = 0				# 活动日志timerID
		self.copySpaceTimerID = 0			# 副本界面timerID

		self.isReceiveEnterInviteJoin = False	# 临时，记录是否受到参加知识问答邀请

		self.isEquipModelLoad = False	# 记录装备模型是否加载完成
		self.tempFace = []

		self.nictationTimerID = -1			# 眨眼callback
		self.nictationOverTimerID = -1
		# 动作匹配器
		self.am = BigWorld.ActionMatcher( self )

		# 法宝motor
		self.tam = None

		# 刀光
		self.rightLoft = None
		self.rightLoftRender = None
		self.leftLoft = None
		self.leftLoftRender = None

		# 单人坐骑
		self.vehicleType = 0
		self.vehicleHP = ""
		self.isConjureVehicle = False

		#反外挂是不是启动 为None没启动，接到通知启动后再赋值
		self.apexClient = None

		# 切磋
		self.qieCuoQiZiModel = None
		self.qieCuoTargetID = 0

		# 飞行坐骑模型
		self.vehicleModel = None

		# 死亡模型相关
		self.emptyModel = None

		# 身轻如燕
		self.onWaterArea = False		# 是否在水域
		self.flyWaterTimerID = 0
		self.isJumpProcess= False                            #表示处在jump过程
		self.isSprint = False 	#表示处在冲刺过程
		self.serverRequests = {}		# 记录需要服务器回应请求，当服务器回应完毕，这个请求在列表中被清除

		self.lastJumpAttackDir = Math.Vector3()
		self.isLoadDefaultModelFailed = False # 是否加载默认模型失败，如果找不到指定的相关模型资源则加载默认模型并设置此标记为True
		self.spaceSkillList = []						# 空间副本技能列表

		self.inFlyDownPose = False	# 下飞行坐骑的pose标志

		self.pkTargetList = {}		# PK目标列表
		self.modelVisibleType = -1
		self.isjumpVehiProcess = False

		self.parallelSpaceID = -1	# 记录进入位面前的空间id，表示传送到位面空间处理中
		
		self.visibleRules = [csdefine.VISIBLE_RULE_BY_PLANEID,csdefine.VISIBLE_RULE_BY_WATCH,\
		 csdefine.VISIBLE_RULE_BY_TEL_AND_TEST,	csdefine.VISIBLE_RULE_BY_PROWL_2, csdefine. VISIBLE_RULE_BY_SETTING_1,\
		 csdefine.VISIBLE_RULE_BY_SHOW_SELF]

	# ----------------------------------------------------------------------------------------------------
	# called by engine
	# ----------------------------------------------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method will be called before EnterWorld method
		# 此方法在enterWorld方法之前调用
		# 返回主角使用的模型路径，BigWorld引擎会自动在后台加载路径资源
		# 而不占用主线程的资源，这样不会导致玩家进入比较多的entity场景中
		# 卡机的现象
		"""
		mNames = []
		mNames.extend( rds.roleMaker.getShowModelPath( self.getModelInfo() ) )
		return mNames

	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		return BigWorld.AvatarFilter()

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld: return

		# 加载模型
		self.createModel()

		self.entityDirProvider = BigWorld.EntityDirProvider( self, 1, 0 )

		# 刀光部分
		self.createRightLoft()
		self.createLeftLoft()

		# 设置武器类型和防具类型创建模型之后
		self.resetWeaponType()
		self.resetArmorType()

		# 模型的RolePitchYaw和Entity保持一致
		self.am.turnModelToEntity = True
		self.am.footTwistSpeed = 0.9

		self.am.boredNotifier = self.onBored			#当播放某个动作过长 将会触发
		self.am.patience = random.random() * Const.RANDOM_TRIGGER_TIME_MIN + ( Const.RANDOM_TRIGGER_TIME_MAX - Const.RANDOM_TRIGGER_TIME_MIN )	#初始化时的patience时间交给随机决定
		self.am.fuse = random.random() * Const.RANDOM_TRIGGER_TIME_MIN + ( Const.RANDOM_TRIGGER_TIME_MAX - Const.RANDOM_TRIGGER_TIME_MIN )		#当前的fuse时间也交给随机决定

		GameObject.onCacheCompleted( self )
		CombatUnit.onCacheCompleted( self )
		BigWorld.addShadowEntity( self )

		self.set_flags( 0 )						# 设置玩家特殊标记


		if not self.isPlayer() :
			self.fxenterWorld()

		# 潜行是否成功
		self.resetSnake()

		# 检测帮会会标 by 姜毅
		self.tongSignCheck()

		#绑定角色Pitch弧度改变时的回调函数
		self.pitchNotifier = self.onPitchNotifier

		# 重置玩家状态
		self.set_state( csdefine.ENTITY_STATE_FREE )

	def  setModelScale( self, model = None ):
		"""
		设置角色模型的缩放值
		"""
		career = self.getClass()
		gender = self.getGender()
		scale = csconst.MATCHING_DICT[gender][career]
		if self.currentModelNumber:		# 变身模型
			scale = self.currentModelScale
		if not model :
			model = self.getModel()
		if model:
			model.scale = ( scale, scale, scale )


	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		if self.model is not None:
			self.model.OnActionStart = None
		QuickBar.leaveWorld( self )
		GameObject.leaveWorld( self )
		CombatUnit.leaveWorld( self )
		PetCage.leaveWorld( self )
		ItemsBag.clearVendSignBoard( self )
		self.teamlogout() # 队伍下线

		if self.queryASTimerID != 0:
			BigWorld.cancelCallback( self.queryASTimerID )

		if self.nictationTimerID != -1:						# 取消眨眼的callback
			BigWorld.cancelCallback( self.nictationTimerID )
		if self.nictationOverTimerID != -1:
			BigWorld.cancelCallback( self.nictationOverTimerID )

		if self.vehicle and self.vehicle.inWorld and self.vehicle.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) :
			self.vehicle.onDisMountEntity( self.id, 0 )

		# leave world的role刚好是玩家观察的role 并且观察对方的窗口未关时，关掉窗口并提示。
		if self.id == BigWorld.player().espial_id and espial.endEspial == False:
			espial.stopEspial()
			BigWorld.player().statusMessage( csstatus.ESPIAL_TARGET_TARGET_DESTROY )

		# 移除模型管理器中相关加载信息
		rds.modelFetchMgr.freeFetchModelTask( self.id )

		# 防止交叉引用
		self.am = None
		self.tam = None
		self.randomActionsWithWeapon = []
		self.randomActionsWithDanWeapon = []
		self.randomActionsWithShuangWeapon = []
		self.randomActionsWithFuWeapon = []
		self.randomActionsWithChangWeapon = []
		self.randomActionsNoWeapon = []
		self.model = None

		# 刀光
		self.rightLoft = None
		self.rightLoftRender = None
		self.leftLoft = None
		self.leftLoftRender = None

		# 单人坐骑
		self.vehicleType = 0
		self.vehicleHP = ""
		self.isConjureVehicle = False

		# 死亡模型相关
		self.disableSkeletonCollider()
		self.disableUnitSelectModel()

		# 清空粒子相关记录
		self.equipEffects = []
		self.vehicleEffects = []			# 坐骑模型相关附加粒子

		# 切磋
		self.qieCuoTargetID = 0
		self.delQieCuoQiZiModel()

		#移除角色Pitch弧度改变时的回调函数
		self.pitchNotifier = None
		BigWorld.delShadowEntity( self )

	def onPitchNotifier( self, pitch ):
		"""
		角色Pitch弧度改变时的回调函数
		@type	return	:	float
		@param	return	:	返回底层用的Pitch弧度值
		@type	pitch	:	float
		@param	pitch	:	底层回调此函数时传进来的Pitch弧度值
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			#DEBUG_MSG( "pitch: %s"%pitch )
			if pitch < 0: return 0
			return pitch
		return 0

	def onInitialized( self, initType ) :
		pass

	def setDanceChallengeIndex(self, challengeIndex):
		"""
		challengeIndex 是舞王的名次，注意这里的名次是从1开始，到20结束
		"""
		pass

	def setVisibility( self, visible ) :
		"""
		设置模型可见性
		hyw -- 09.01.10
		"""
		GameObject.setVisibility( self, visible )

		# 法宝
		if self.talismanModel:
			self.talismanModel.visible = visible
		# 附加模型
		model = self.getModel()
		if model and model != self.model:
			model.visible = visible

	# ----------------------------------------------------------------------------------------------------
	# 单人骑宠
	# ----------------------------------------------------------------------------------------------------
	def switchVehicleEffect( self, switch ):
		"""
		开关骑宠身上的粒子效果
		"""
		if not self.inWorld: return
		for effect in self.vehicleEffects:
			if switch:
				effect.fadeIn()
			else:
				effect.fadeOut()

	def set_vehicleModelNum( self, old = 0 ):
		"""
		骑宠模型编号
		"""
		DEBUG_MSG( "oldNum", old, "newNum", self.vehicleModelNum, "self.model", self.model )

		# 表示上马
		if self.vehicleModelNum:
			self.createVehicleModel()
			# 用于播放骑宠召唤音效
			self.isConjureVehicle = True
		else:
			self.am.playAniScale = 1.0
			if self.model and self.vehicleType == Define.VEHICLE_MODEL_STAND:
				playModel = rds.effectMgr.getLinkObject( self.model, Const.VEHICLE_STAND_HP )
				if playModel is None:
					if self.vehicleModel: 	#解决在上坐骑的动作还没完成时，取消坐骑add by wuxo 2011-12-5
						self.model.root.detach( self.vehicleModel )
						self.set_hideInfoFlag( False )   # 显示玩家信息
						self.inFlyDownPose = True
						rds.actionMgr.playActions( self.model, [Const.MODEL_ACTION_RIDE_DOWN, Const.MODEL_ACTION_RIDE_DOWN_OVER], callbacks = [self.onDownFlyVehicleOver] )
					else:
						self.createEquipModel()

				else:
					rds.effectMgr.detachObject( self.model, Const.VEHICLE_STAND_HP, playModel )
					self.vehicleModel = self.model
					self.setModel( playModel, Define.MODEL_LOAD_IN_WORLD_CHANGE )
					self.setModelScale( playModel )#还原玩家模型缩放
					self.addModel( self.vehicleModel )
					self.vehicleModel.position = self.position
					self.vehicleModel.yaw = self.yaw
					rds.actionMgr.playAction( self.vehicleModel, Const.MODEL_ACTION_STAND )
					self.setModelScale( self.vehicleModel )#还原坐骑模型缩放
					rds.effectMgr.fadeOutModel( self.vehicleModel, 1.0 )
					if self.isPlayer():
						self.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE )
					self.inFlyDownPose = True
					rds.actionMgr.playActions( playModel, [Const.MODEL_ACTION_RIDE_DOWN, Const.MODEL_ACTION_RIDE_DOWN_OVER], callbacks = [self.onDownFlyVehiclePose, self.onDownFlyVehiclePoseOver] )

			else:
				self.isLoadModel = True
				self.delayActionNames = []
				self.delayCastEffects = []
				self.createEquipModel()

			# 清空记录的骑宠模型相关粒子
			self.vehicleEffects = []
			self.vehicleType = 0
			self.vehicleHP = ""
			self.isConjureVehicle = False

			#下坐骑去掉骑宠模型加载完成的标记
			self.onFlyModelLoadFinished = False


	def vehicleSound( self, vehicleModelNum, actionNum ):
		"""
		骑宠音效处理接口 by姜毅
		"""
		soundNameList = rds.npcModel.getVehicleSound( actionNum, vehicleModelNum )
		if len( soundNameList ) is 0: return
		soundName = random.choice( soundNameList )
		model = self.getModel()
		if model is None: return
		soundMgr.playVocality( soundName, model )

	def updateRoleModel( self, model ):
		"""
		更新坐骑上的玩家模型
		"""
		if self.vehicleModelNum == 0: return

		if self.vehicleType == Define.VEHICLE_MODEL_HIP:
			hardPoint = Const.VEHICLE_HIP_HP
		elif self.vehicleType == Define.VEHICLE_MODEL_STAND:
			hardPoint = Const.VEHICLE_STAND_HP
		else:
			hardPoint = Const.VEHICLE_PAN_HP

		rds.effectMgr.linkObject( self.model, hardPoint, model )
		self.onSwitchVehicle( Const.MODEL_ACTION_STAND )

	def onSwitchVehicle( self, actionName ):
		"""
		骑宠动作触发
		"""
		if self.vehicleModelNum == 0: return

		if actionName not in Const.VEHICLE_ACTION_MAPS: return

		model = self.getModel()
		if model is None: return

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

		caps = self.am.matchCaps
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

	def onAddVehicle( self, vehicleData ):
		"""
		Define Method
		添加骑宠数据
		"""
		pass

	def onDisMountDart( self ):
		"""
		下镖车
		"""
		pass

	def onUpdateVehicleExp( self, dbid, exp ):
		"""
		Define Method
		骑宠经验更新
		"""
		pass

	def onUpdateVehicleProperty( self, id, level,strength,intellect,dexterity,corporeity,step,growth,sID ):
		"""
		Define Method
		传功引起的骑宠属性改变
		"""
		pass

	def onUpdateVehicleFullDegree( self, dbid, fullDegree ):
		"""
		Define Method
		骑宠饱腹度更新
		"""
		pass

	def onUpdateVehicleDead( self, dbid, deadTime ):
		"""
		Define Method
		骑宠生存时间更新 by 姜毅
		"""
		pass

	def onUpdateVehicleSkPoint( self, dbid, skPoint ):
		"""
		Define Method
		骑宠技能点更新
		"""
		pass

	def onVehicleAddSkill( self, skillID ):
		"""
		Define method.
		骑宠获得新技能
		"""
		pass

	def onVehicleUpdateSkill( self, skillID ):
		"""
		Define method.
		骑宠技能升级
		"""
		pass

	def onFreeVehicle( self ):
		"""
		Defined Method
		骑宠放生 by姜毅
		"""
		pass

	def onUseVehicleItem( self, dbid, item ):
		"""
		玩家使用骑宠物品通知
		"""
		pass

	def onFixTimeReward( self, timeTick, itemID ):
		"""
		defined method
		新手定时奖励的客户端通知 by姜毅
		"""
		pass

	def onOldFixTimeReward( self, timeTick, RewardNum, RewardType, Param ):
		"""
		defined method
		老手定时奖励的客户端通知 by姜毅
		timeTick: 剩余时间
		RewardNum: 奖励份数
		RewardType: 奖励类型
		Param: 奖励参数 例如经验值 物品ID等
		"""
		pass

	def updateComboCount( self, comboCount ):
		pass

	def onShowAccumPoint( self, id, ap ):
		"""
		显示补刀
		id : 目标怪物
		ap ：灵魂币
		"""
		pass

	def showRankList(self, msg):
		pass

	def onPlayMonsterSound( self, soundType, soundEvent ):
		pass

	def onStopMonsterSound( self ):
		pass
	# ----------------------------------------------------------------------------------------------------
	# 随机动作相关
	# ----------------------------------------------------------------------------------------------------

	def onBored( self, actionName ):
		"""
		此回调用于播放随机动作
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		# 如果action 是空时，重置fuse，重新开始计时
		if actionName is None: return

		#中了昏睡、眩晕、定身等效果时不能做随即动作以及眨眼睛
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		if self.effect_state & EffectState_list != 0:
			self.resetAM()
			return

		# 角色不在死亡和战斗状态中触发眨眼睛( 0-8 )秒随机之后，播放眨眼动画
		if self.state not in [ csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_FIGHT ]:
			self.nictationTimerID = BigWorld.callback( random.random() * 8, self.playNictation )

		# 只有站着的时候才播放随机动作
		if actionName.startswith( "stand" ): self.playRandomAction()
		self.playVehicleRandomAction( actionName )

		# 当一个动作开始播放时 fuse 会重置为0
		# 引擎似乎有bug，有时候并没有重置 fuse 这个属性，现在在这里重置
		self.resetAM()

	def resetAM( self ):
		"""
		重置ActionMatcher中得fuse和patience的值
		"""
		self.am.fuse = 0
		# 每通知一次 onBored  引擎会自动把 patience 设为一个负值??
		# 只有重置 patience 值 才能连续的不停调用 onBored 方法
		self.am.patience = random.random() * Const.RANDOM_TRIGGER_TIME_MIN + ( Const.RANDOM_TRIGGER_TIME_MAX - Const.RANDOM_TRIGGER_TIME_MIN )

	def playVehicleRandomAction( self, actionName ):
		"""
		播放在玩家在骑宠上的随机动作
		"""
		if self.vehicleModelNum == 0: return

		actionDatas = Const.VEHICLE_RANDOM_ACTION_MAPS.get( actionName, [] )
		if len( actionDatas ) == 0: return

		# 分拿武器动作和不拿武器动作的处理
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

		actionNameDatas = actionDatas[index]
		if len( actionNameDatas ) == 0: return

		actionIndex = 0
		if self.vehicleType == Define.VEHICLE_MODEL_HIP:
			actionIndex = 0
		elif self.vehicleType == Define.VEHICLE_MODEL_PAN:
			actionIndex = 1
		elif self.vehicleType == Define.VEHICLE_MODEL_STAND:
			actionIndex = 2

		actionNames = actionNameDatas[actionIndex]
		if len( actionNames ) == 0: return

		actionName = random.choice( actionNames )
		rds.actionMgr.playAction( self.getModel(), actionName )

	def playRandomAction( self ):
		"""
		play random Action
		"""
		caps = self.am.matchCaps
		if Define.CAPS_DEFAULT not in caps: return

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

		caps.remove( Define.CAPS_DEFAULT )
		caps.append( capsIndex )
		caps.append( Define.CAPS_RANDOM )
		self.am.matchCaps = caps

		BigWorld.callback( 0.1, self.onOneShoot )

		if self.vehicleModelNum:	# 骑宠随机动作音效 by姜毅
			self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_RANDOM )

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

	def playNictation( self, key = None ):
		"""
		眨眼睛
		"""
		self.nictationTimerID = -1
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return
		if not hasattr( model, "lian1" ): return

		# 保留旧的脸dye，以便恢复
		# 以_2结尾的dye都是不受光照影响的
		# _nictation 为眨眼睛dye
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
		faceNum = self.faceNumber
		functor = Functor( self.onPlayNictationOver, oldTint, faceNum )
		self.nictationOverTimerID = BigWorld.callback( random.random() * 3 + 6, functor )

	def onPlayNictationOver( self, oldTint, oldFaceNum ):
		"""
		眨眼动作播放完毕
		"""
		# 这里可能会涉及
		self.nictationOverTimerID = -1
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return
		if not hasattr( model, "lian1" ): return
		faceNum = self.faceNumber
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

	def playDanceAction( self, danceType ):
		"""
		播放跳舞动作效果
		"""
		if danceType == "dance":
			actionName = Const.MODEL_ACTION_DANCE
		elif danceType == "doubleDance":
			actionName = Const.MODEL_ACTION_DANCE6
		else:
			actionName = ""

		rds.actionMgr.playAction( self.model, actionName )
		self.updateVisibility()

	def stopDanceAction( self ):
		"""
		停止跳舞动作效果
		"""
		# 停止动作效果
		rds.actionMgr.stopAction( self.model, Const.MODEL_ACTION_DANCE )
		rds.actionMgr.stopAction( self.model, Const.MODEL_ACTION_DANCE6 )

		self.updateVisibility()

	def playFaceAction( self, face ) :
		"""
		播放表情动作
		"""
		model = self.model
		if model.hasAction( face[0] ) :
			if len( face ) != 1 :
				rds.actionMgr.playActions( model, face )		# 需要两个动作构成的效果，比如坐下
			else :
				functor = Functor( self.cell.stopFaceAction, face ) # 播放完动作后通知cell端动作已停止，并还原到播放前的状态
				rds.actionMgr.playAction( model, face[0], callback = functor )
			self.tempFace = face
		else :
			ERROR_MSG( "role has no face %i!" % face )
			return
		self.updateVisibility()

	def stopFaceAction( self, face ) :
		"""
		停止播放表情动作
		"""
		model = self.model
		if model is None: return
		if len( self.tempFace ) != 0 :
			if self.tempFace[0] != face[0] : return # 防止出现一个动作未播完就播另一个动作时，另一个动作没播完就结束的问题
		if len( face ) > 1 :
			rds.actionMgr.stopAction( model, face[0] )
			rds.actionMgr.stopAction( model, face[1] )
		else :
			rds.actionMgr.stopAction( model, face[0] )
		self.tempFace = []
		self.updateVisibility()

	def playRequestDanceAction( self ):
		"""
		播放邀请跳舞动作
		"""
		rds.actionMgr.playAction( self.model, Const.MODEL_ACTION_STAND )

	def stopRequestDanceAction( self ):
		"""
		停止邀请跳舞动作
		"""
		rds.actionMgr.stopAction( self.model, Const.MODEL_ACTION_STAND )

	# ----------------------------------------------------------------------------------------------------
	# 刀光相关
	# ----------------------------------------------------------------------------------------------------
	def createRightLoft( self ):
		"""
		创建右手刀光
		"""
		self.loftHP = ""
		classes = self.getClass()
		if classes == csdefine.CLASS_FIGHTER:
			self.loftHP = Const.LOFT_FIGHTER_HP
			particles = Const.LOFT_FIGHTER
		elif classes == csdefine.CLASS_SWORDMAN:
			self.loftHP = Const.LOFT_SWORDMAN_HP
			particles = Const.LOFT_SWORDMAN
		else:
			return

		rds.effectMgr.pixieCreateBG( particles, self.onRightLoftLoad )

	def createLeftLoft( self ):
		"""
		创建左手刀光
		"""
		self.loftHP = ""
		classes = self.getClass()
		if classes == csdefine.CLASS_FIGHTER:
			self.loftHP = Const.LOFT_FIGHTER_HP
			particles = Const.LOFT_FIGHTER
		elif classes == csdefine.CLASS_SWORDMAN:
			self.loftHP = Const.LOFT_SWORDMAN_HP
			particles = Const.LOFT_SWORDMAN
		else:
			return

		rds.effectMgr.pixieCreateBG( particles, self.onLeftLoftLoad )

	def onRightLoftLoad( self, particle ):
		"""
		右手刀光效果加载完成
		"""
		if not self.inWorld: return
		if particle is None: return
		self.rightLoft = particle
		self.rightLoftRender = particle.system(0).renderer
		model = self.getModel()
		if model is None: return
		if hasattr( model, "right_hand" ):
			self.attachRightLoft( model.right_hand )

	def onLeftLoftLoad( self, particle ):
		"""
		左手刀光效果加载完成
		"""
		if not self.inWorld: return
		if particle is None: return
		self.leftLoft = particle
		self.leftLoftRender = particle.system(0).renderer
		model = self.getModel()
		if model is None: return
		if hasattr( model, "left_hand" ):
			self.attachLeftLoft( model.left_hand )

	def attachRightLoft( self, model ):
		"""
		装载右手刀光
		"""
		if model is None: return
		rds.effectMgr.attachObject( model, self.loftHP, self.rightLoft )

	def attachLeftLoft( self, model ):
		"""
		装载左手刀光
		"""
		if model is None: return
		rds.effectMgr.attachObject( model, self.loftHP, self.leftLoft )

	def detachRightLoft( self, model ):
		"""
		卸载右手刀光
		"""
		if model is None: return
		if self.leftLoft is None: return
		rds.effectMgr.detachObject( model, self.loftHP, self.rightLoft )

	def detachLeftLoft( self, model ):
		"""
		卸载左手刀光
		"""
		if model is None: return
		if self.leftLoft is None: return
		rds.effectMgr.detachObject( model, self.loftHP, self.leftLoft )

	def switchLoft( self, actionName ):
		"""
		触发刀光效果
		"""
		weaponType = self.weaponType
		actionList = Define.LOFT_MAPS.get( weaponType )
		if actionList is None: return
		if actionName in actionList:
			if self.rightLoftRender:
				self.rightLoftRender.start()
			if self.leftLoftRender:
				self.leftLoftRender.start()
		else:
			if self.rightLoftRender:
				self.rightLoftRender.stop()
			if self.leftLoftRender:
				self.leftLoftRender.stop()

	# ----------------------------------------------------------------------------------------------------
	# 玩家属性相关
	# ----------------------------------------------------------------------------------------------------
	# 以set_开头的接口，当玩家的set_后面的属性改变则自动调用相关接口
	# 例如 set_level ,当玩家的level属性改变后，引擎会自动调用 set_level()
	def set_level( self, oldLevel = 0):
		"""
		玩家等级
		"""
		# 升级光效
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.UPDATE_LEVEL_EFFECT, self.getModel(), self.getModel(), type, type )
		if effect:
			effect.start()
		CombatUnit.set_level( self, oldLevel )

	def set_yiJieFaction( self, oldValue ):
		"""
		阵营改变
		"""
		ECenter.fireEvent( "EVT_ON_YIJIE_FACTION_CHANGED", self.yiJieFaction )

	def set_lifetime( self, lifetime ):
		"""
		玩家游戏总时间
		"""
		self.lifetime = lifetime

	def set_state( self, oldState = csdefine.ENTITY_STATE_FREE ):
		"""
		玩家状态
		"""
		CombatUnit.set_state( self, oldState )

		if self.state == csdefine.ENTITY_STATE_VEND:
			self.createVendModel()
		elif oldState == csdefine.ENTITY_STATE_VEND:
			self.createEquipModel()
			self.vend_onVendEnd()
		elif self.state == csdefine.ENTITY_STATE_RACER:
			self.createHorseModel()
		elif oldState == csdefine.ENTITY_STATE_CHANGING:
			if self.isFishing() and self.state == csdefine.ENTITY_STATE_FIGHT:
				self.endFishing()
		elif oldState == csdefine.ENTITY_STATE_RACER:
			self.createEquipModel()

		if self.state == csdefine.ENTITY_STATE_REQUEST_DANCE:		# 开始邀请跳舞动作
			self.playRequestDanceAction()
		if oldState == csdefine.ENTITY_STATE_REQUEST_DANCE:			# 结束邀请跳舞动作
			self.stopRequestDanceAction()
		if len( self.tempFace ) != 0 and self.state == csdefine.ENTITY_STATE_FIGHT : # 停止播放表情动作
			self.cell.stopFaceAction( self.tempFace )
		self.updateVisibility()

		if self.state == csdefine.ENTITY_STATE_DANCE:				# 开始跳舞动作
			self.playDanceAction( "dance" )
		if self.state == csdefine.ENTITY_STATE_DOUBLE_DANCE:		# 开始双人跳舞动作
			self.playDanceAction( "doubleDance" )
		if oldState == csdefine.ENTITY_STATE_DANCE or oldState == csdefine.ENTITY_STATE_DOUBLE_DANCE:	# 结束跳舞动作
			self.stopDanceAction()

		# 死亡状态下附加处理
		if self.state == csdefine.ENTITY_STATE_DEAD:
			self.switchEquipEffect( False )
			self.enableSkeletonCollider()
			for linkEffect in self.linkEffect:
				linkEffect.stop()
			self.linkEffect = []
		if oldState == csdefine.ENTITY_STATE_DEAD:
			self.switchEquipEffect( True )
			self.disableSkeletonCollider()

		self.setArmCaps()

	def set_effect_state( self, oldEState = 0 ):
		"""
		玩家效果状态 这里可以处理效果状态 如 眩晕，定身等
		"""
		CombatUnit.set_effect_state( self, oldEState )
		self.setArmCaps()


	def set_pkState( self, oldpkstate = csdefine.PK_STATE_PEACE ):
		"""
		pk状态改变
		"""
		#通知其他玩家
		BigWorld.callback( 2, self.onUpdateRoleNameColor )

	def set_goodnessValue( self, oldValue ):
		"""
		善恶值
		 """
		ECenter.fireEvent( "EVT_ON_ROLE_GOODNESS_CHANGE", self.goodnessValue )


	def set_titleName( self, oldValue ):
		"""
		称号
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_TITLENAME_CHANGE", self, self.titleName, self.getTitleColor( self.title ) )

	def change_money( self, value, reason ):
		"""
		当金钱属性改变时被服务器调用
		"""
		rds.soundMgr.playUI( "ui/money1" )
		oldValue = self.money
		self.money = value
		dispersion = value - oldValue
		if reason != csdefine.CHANGE_MONEY_INITIAL and dispersion > 0:
			self.statistic["statMoney"] += dispersion
		GUIFacade.onRoleMoneyChanged( oldValue, value, reason )

	def updateGold( self, newValue, reason ):
		"""
		Define method.
		当元宝的属性改变时被调用。

		@param newValue : 玩家当前金元宝
		@type newValue : UINT32
		"""
		oldValue = self.gold
		self.gold = newValue
		GUIFacade.onRoleGoldChanged( oldValue, self.gold, reason )	# 通知界面

	def updateSilver( self, newValue, reason ):
		"""
		Define method.
		当元宝的属性改变时被调用。

		@param newValue : 玩家当前银元宝
		@type newValue : UINT32
		"""
		oldValue = self.silver
		self.silver = newValue
		GUIFacade.onRoleSilverChanged( oldValue, self.silver, reason )	# 通知界面

	def change_EXP( self, increasedExp, exp, reason ):
		"""
		当经验属性改变时被服务器调用
		"""
		if  reason != csdefine.CHANGE_EXP_INITIAL and increasedExp > 0:
			self.statistic["statExp"] += increasedExp
		self.EXP = exp
		ECenter.fireEvent( "EVT_ON_ROLE_EXP_CHANGED", increasedExp, reason )


	# ----------------------------------------------------------------------------------------------------
	# 玩家模型相关，包括换装等
	# ----------------------------------------------------------------------------------------------------
	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		"""
		GameObject.onModelChange( self, oldModel, newModel )
		CombatUnit.onModelChange( self, oldModel, newModel )
		if newModel is None: return
		self.updateVisibility()
		if self.am.owner != None: self.am.owner.delMotor( self.am )
		newModel.motors = ( self.am, )

		# 刷新所有附加物
		self.flushAttachments_()
		# 设置动作回调
		newModel.OnActionStart = self.onActionStart
		# 刷新记录模型的随机动作名称
		self.getRandomActions()

		rds.areaEffectMgr.onModelChange( self )

		#设置玩家的缩放
		self.setModelScale()
		self.setArmCaps()

		# 死亡光圈处理
		self.resetUnitSelectModel()

		self.doActionSkillAction()
		ECenter.fireEvent( "EVT_ON_TARGET_MODEL_CHANGED", self, oldModel, newModel )

	def doActionSkillAction( self ):
		"""
		行为技能时，进入视野范围，也正常播放
		"""
		if not self.curActionSkillID: return
		skill = skills.getSkill( self.curActionSkillID )
		actionList = [ skill._datas["param1"], skill._datas["param2"] ]
		self.playFaceAction( actionList )

	def setModel( self, model, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		给玩家设置一个模型
		"""
		if self.model is not None:
			self.model.OnActionStart = None
		GameObject.setModel( self, model, event )

	def getModel( self ):
		"""
		获取自身模型。涉及玩家可能在骑宠上
		自身模型为空，则从骑宠身上获取。
		"""
		if not self.inWorld: return None
		#if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
		#	return getattr( self.model, Const.TELEPORT_HIP, None )
		if self.state == csdefine.ENTITY_STATE_RACER:
			return getattr( self.model, Const.HORSERACE_MODEL_HIP, None )
		if self.vehicleType == Define.VEHICLE_MODEL_HIP:
			return getattr( self.model, Const.VEHICLE_HIP, None )
		elif self.vehicleType == Define.VEHICLE_MODEL_PAN:
			return getattr( self.model, Const.VEHICLE_PAN, None )
		elif self.vehicleType == Define.VEHICLE_MODEL_STAND:
			return getattr( self.model, Const.VEHICLE_STAND, None )
		else:
			return self.model

	def getModelInfo( self ):
		"""
		获取创建模型相关必要的信息
		"""
		infoDict = {}
		infoDict["roleID"]			= self.id
		infoDict["roleName"]		= self.playerName
		infoDict["level"]			= self.level
		infoDict["raceclass"]		= self.raceclass
		infoDict["talismanNum"]		= self.talismanNum
		infoDict["fashionNum"]		= self.fashionNum
		infoDict["adornNum"]		= self.adornNum
		if self.isLoadDefaultModelFailed:	# 如果上次模型加载失败，再次加载则使用默认值加载模型
			return getDefaultRoleInfo( infoDict )

		infoDict["hairNumber"]		= self.hairNumber
		infoDict["faceNumber"]		= self.faceNumber
		infoDict["bodyFDict"]		= self.bodyFDict
		infoDict["volaFDict"]		= self.volaFDict
		infoDict["breechFDict"]		= self.breechFDict
		infoDict["feetFDict"]		= self.feetFDict
		infoDict["lefthandFDict"]	= self.lefthandFDict
		infoDict["righthandFDict"]	= self.righthandFDict
		infoDict["headTextureID"]	= self.headTextureID
		return RoleInfo( infoDict )

	def getModelInfoDict(self):
		"""
		获取创建模型相关必要的信息的字典
		"""
		infoDict = {}
		#infoDict["roleID"]			= self.id
		infoDict["roleName"]		= self.playerName
		infoDict["level"]			= self.level
		infoDict["tongName"]		= self.tongName
		infoDict["raceclass"]		= self.raceclass
		infoDict["talismanNum"]		= self.talismanNum
		infoDict["fashionNum"]		= self.fashionNum
		infoDict["adornNum"]		= self.adornNum

		infoDict["hairNumber"]		= self.hairNumber
		infoDict["faceNumber"]		= self.faceNumber
		infoDict["bodyFDict"]		= self.bodyFDict
		infoDict["volaFDict"]		= self.volaFDict
		infoDict["breechFDict"]		= self.breechFDict
		infoDict["feetFDict"]		= self.feetFDict
		infoDict["lefthandFDict"]	= self.lefthandFDict
		infoDict["righthandFDict"]	= self.righthandFDict
		infoDict["headTextureID"]	= self.headTextureID
		return infoDict

	def onActionStart( self, actionName ):
		"""
		"""
		if not self.inWorld: return
		# 单人骑宠相关
		self.onSwitchVehicle( actionName )

		# 刀光触发
		self.switchLoft( actionName )

		# 头发动作相关
		self.switchHairAction( actionName )

		# 凌波微波水面效果触发
		self.onSwtichWaterParticle( actionName )

	def createModel( self ):
		"""
		创建玩家模型
		根据玩家当前的状态等来创建
		"""
		# 骑宠
		if self.vehicleModelNum:
			self.createVehicleModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		## 飞翔传送
		#if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
		#	self.createFlyModel( Define.MODEL_LOAD_ENTER_WORLD )
		#	return
		# 摆摊
		if self.state == csdefine.ENTITY_STATE_VEND:
			self.createVendModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		# 赛马
		if self.state == csdefine.ENTITY_STATE_RACER:
			self.createHorseModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		# 变身
		if self.currentModelNumber:
			self.createChangeModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		# 装备
		self.createEquipModel( Define.MODEL_LOAD_ENTER_WORLD )

	# ----------------------------------------------------------------------------------------------------
	# 玩家装备模型相关
	# ----------------------------------------------------------------------------------------------------
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
		# 额外模型法宝
		talismanPaths = rds.roleMaker.getTalismanModelPath( self.talismanNum )
		if len( talismanPaths ): paths[Define.MODEL_EQUIP_TALIS] = talismanPaths

		return paths

	def onEquipModelLoad( self, event, modelDict ):
		"""
		装备模型加载完成
		"""
		if not self.inWorld: return
		mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# 如果再次加载失败则不再加载
			if self.isLoadDefaultModelFailed:
				self.createEquipModel( event )
			return
		mainModel = self.composeEquipModel( modelDict )
		self.setModel( mainModel, event )

		# 如果在镖车上
		slaveDart = self.getSlaveDart()
		if slaveDart:
			slaveDart.onMountEntity( self.id, 0 )
			return

		# 如果角色在跳舞状态，则播放跳舞动作
		if self.state == csdefine.ENTITY_STATE_DANCE:
			self.playDanceAction( "dance" )
			return
		# 如果角色在双人跳舞状态，则播放跳舞动作
		if self.state == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			self.playDanceAction( "doubleDance" )
			return

		self.isLoadDefaultModelFailed = False
		self.isLoadModel = False
		if self.delayActionNames:
			self.playActions(self.delayActionNames)
		self.delayActionNames = []
		# 恶性技能下坐骑攻击光效
		for cb in self.delayCastEffects:
			if callable( cb ):
				cb()

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
		# 附属模型右手武器
		righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
		self.attachRHModel( mainModel, righthandModel )
		self.weaponAttachEffect( righthandModel, self.righthandFDict )
		# 附属模型左手武器
		lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
		self.attachLHModel( mainModel, lefthandModel )
		self.weaponAttachEffect( lefthandModel, self.lefthandFDict )
		# 法宝模型
		talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
		self.attachTalismanModel( mainModel, talismanModel )
		self.talismanAttachEffect( talismanModel )
		# 如果不是时装模式，则显示额外装备粒子效果
		if not self.fashionNum: self.resetEquipEffect( mainModel )
		# 如果职业是法师，则显示脚底粒子效果
		if self.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = self.getParticleType() )

		return mainModel

	def weaponAttachEffect( self, model, weaponDict, pType = None ):
		"""
		武器附加属性效果
		@type		model 		: pyModel
		@param		model 		: 模型
		@type		weaponDict 	: FDict
		@param		weaponDict 	: 武器数据
		"""
		if pType == None:
			pType = self.getParticleType()
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
			if not type:return
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, intensifyLevel )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )

	def talismanAttachEffect( self, model ):
		# 法宝Dyes
		talismanNum = self.talismanNum
		talismanDyes = rds.roleMaker.getTalismanModelDyes( talismanNum )
		rds.effectMgr.createModelDye( model, talismanDyes )
		# 自带光效
		effectIDs = rds.itemModel.getMEffects( talismanNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, self.getParticleType(), self.getParticleType() )
			effect.start()
	# ----------------------------------------------------------------------------------------------------
	# 玩家骑宠装备模型相关
	# ----------------------------------------------------------------------------------------------------
	def createVehicleModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		创建骑宠装备模型
		@type	event	:	int
		@param	event	: 	加载事件
		"""
		paths = self.getVehicleModelPaths()
		functor = Functor( self.onVehicleModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )
		self.setArmCaps()

	def getVehicleModelPaths( self ):
		"""
		获取骑宠与装备模型路径
		@return dict
		"""
		# 获取装备模型
		paths = self.getEquipModelPaths()
		# 骑宠模型
		if self.isLoadDefaultModelFailed:	# 如果上次模型加载失败，再次加载则使用默认值加载模型
			if self.vehicleType == Define.VEHICLE_MODEL_STAND:
				self.vehicleModelNum = Const.SKY_VEHICLE_DEFAULT_MODEL_NUM
			else:
				self.vehicleModelNum = Const.LAND_VEHICLE_DEFAULT_MODEL_NUM
		vehiclePaths = rds.itemModel.getMSource( self.vehicleModelNum )
		if len( vehiclePaths ): paths[Define.MODEL_VEHICLE] = vehiclePaths

		return paths

	def onVehicleModelLoad( self, event, modelDict ):
		"""
		骑宠和装备模型加载完成
		"""
		if not self.inWorld: return
		if self.vehicleModelNum == 0: return

		# 骑宠模型
		vehicleModel = modelDict.get( Define.MODEL_VEHICLE )
		if vehicleModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# 如果再次加载失败则不再加载
			if self.isLoadDefaultModelFailed:
				self.createVehicleModel( event )
			return

		# 设置骑宠相关值
		if hasattr( vehicleModel, Const.VEHICLE_HIP ):
			self.vehicleType = Define.VEHICLE_MODEL_HIP
			self.vehicleHP = Const.VEHICLE_HIP_HP
		if hasattr( vehicleModel, Const.VEHICLE_STAND ):
			self.vehicleType = Define.VEHICLE_MODEL_STAND
			self.vehicleHP = Const.VEHICLE_STAND_HP
		if hasattr( vehicleModel, Const.VEHICLE_PAN ):
			self.vehicleType = Define.VEHICLE_MODEL_PAN
			self.vehicleHP = Const.VEHICLE_PAN_HP

		# 骑宠dye、粒子
		dyes = rds.itemModel.getMDyes( self.vehicleModelNum )
		rds.effectMgr.createModelDye( vehicleModel, dyes )
		effectIDs = rds.itemModel.getMEffects( self.vehicleModelNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, vehicleModel, vehicleModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
			self.vehicleEffects.append( effect )
			effect.start()

		# 处理召唤骑宠音效
		if self.isConjureVehicle:
			self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_CONJURE )
			rds.effectMgr.createParticleBG( vehicleModel, Const.VEHICLE_CONJURE_HP, Const.VEHICLE_CONJURE_PARTICLE, detachTime = 2.0, type = self.getParticleType() )

		# 飞行骑宠的特有上坐骑效果 2011/5/23 16:29 yk
		if event == Define.MODEL_LOAD_IN_WORLD_CHANGE and self.vehicleType == Define.VEHICLE_MODEL_STAND:
			if self.model:
				if self.vehicleModel:	# 清掉上一个飞行骑宠的残留
					self.onDownFlyVehiclePoseOver()
				self.vehicleModel = vehicleModel
				self.model.root.attach( vehicleModel )
				vehicleModel.yaw = self.yaw
				rds.actionMgr.playAction( vehicleModel, Const.MODEL_ACTION_STAND )
				rds.effectMgr.fadeInModel( vehicleModel, 1.0 )
				rds.actionMgr.playActions( self.model, [Const.MODEL_ACTION_RIDE_UP, Const.MODEL_ACTION_RIDE_UP_OVER], callbacks = [self.onUpFlyVehiclePoseOver] )
				self.set_hideInfoFlag( True ) # 隐藏玩家头顶信息
				self.isjumpVehiProcess = True
		else:
			mainModel = self.composeEquipModel( modelDict )
			rds.effectMgr.linkObject( vehicleModel, self.vehicleHP, mainModel )
			self.setModel( vehicleModel, event )
			functor = Functor( self.setVehicleCamera, self.vehicleHP )
			BigWorld.callback( 0.1, functor )	# 延迟设置骑宠镜头
			mainModel.OnActionStart = self.switchLoft
			self.onSwitchVehicle( Const.MODEL_ACTION_STAND )

		# 处理模型动作缩放频率
		tmpFreq = VehiFreqDatas.get( self.vehicleModelNum,1.0 ) #读取缩放配置信息
		self.am.playAniScale = tmpFreq #缩放处理
		self.isLoadDefaultModelFailed = False
		self.onFlyModelLoadFinished = True  #用于判断在飞行镜头中模型已经加载完了的标记，才开始飞行

	def setVehicleCamera( self, nodeName ):
		"""
		设置骑宠镜头
		"""
		pass

	def onUpFlyVehiclePoseOver( self ):
		"""
		上飞行骑宠动作完成回调
		"""
		if not self.inWorld: return
		if self.vehicleModel is None: return
		self.model.root.detach( self.vehicleModel )
		mainModel = self.model
		self.model = None
		rds.effectMgr.linkObject( self.vehicleModel, self.vehicleHP, mainModel )
		self.setModel( self.vehicleModel, Define.MODEL_LOAD_IN_WORLD_CHANGE )
		self.setModelScale( self.vehicleModel )#还原坐骑模型缩放
		functor = Functor( self.setVehicleCamera, self.vehicleHP )
		BigWorld.callback( 0.1, functor )	# 延迟设置骑宠镜头
		mainModel.OnActionStart = self.switchLoft
		self.onSwitchVehicle( Const.MODEL_ACTION_STAND )
		self.vehicleModel = None
		self.set_hideInfoFlag( False ) # 显示玩家头顶信息
		self.isjumpVehiProcess = False
		self.setArmCaps()

	def onDownFlyVehicleOver( self ):
		"""
		在上坐骑的动作还没完成时，下坐骑动作完成回调
		"""
		if not self.inWorld: return
		for actionName in self.getActionNames():	# 由于召唤骑宠的技能没有施法动作，所以这里要停止召唤骑宠的技能Loop动作
			rds.actionMgr.stopAction( self.model, actionName )
		if hasattr( self, "isOnSomething" ) and self.isOnSomething():	# 在地表下飞行坐骑
			self.isJumpProcess = False
		elif self.isJumpProcess:
			self.playActions( [Const.MODEL_ACTION_JUMP_AIR] )
		self.vehicleModel = None
		self.inFlyDownPose = False
		self.isjumpVehiProcess = False
		self.physics.fall = True 	# 解决上飞行骑宠动作回调过慢的Bug
		self.setArmCaps()

	def onDownFlyVehiclePose( self ):
		"""
		下飞行骑宠动作1部分完成回调
		"""
		if not self.inWorld: return
		if hasattr( self, "isOnSomething" ) and self.isOnSomething():	# 在地表下飞行坐骑
			self.isJumpProcess = False
		elif self.isJumpProcess:
			self.playActions( [Const.MODEL_ACTION_JUMP_AIR] )
		self.inFlyDownPose = False
		self.setArmCaps()

	def onDownFlyVehiclePoseOver( self ):
		"""
		下飞行骑宠动作2部分完成回调
		"""
		if not self.inWorld: return
		if self.vehicleModel not in list( self.models ): return
		self.delModel( self.vehicleModel )
		self.vehicleModel = None
		self.inFlyDownPose = False
		self.setArmCaps() #防止跳下时 离地有距离

	# ----------------------------------------------------------------------------------------------------
	# 玩家赛马模型相关
	# ----------------------------------------------------------------------------------------------------
	def createHorseModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		创建赛马模型
		@type	event	:	int
		@param	event	: 	加载事件
		"""
		paths = self.getHorseModelPaths()
		functor = Functor( self.onHorseModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getHorseModelPaths( self ):
		"""
		获取赛马模型路径
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
		# 额外模型法宝
		talismanPaths = rds.roleMaker.getTalismanModelPath( self.talismanNum )
		if len( talismanPaths ): paths[Define.MODEL_EQUIP_TALIS] = talismanPaths
		# 赛马模型
		horsePaths = [Const.HORSERACE_MODEL_PATH]
		if self.hasFlag( csdefine.ENTITY_FLAG_CHRISTMAS_HORSE ):
			horsePaths = rds.npcModel.getModelSources( Const.HORSERACE_CHRISTMAS_MODEL_NUMBER )

		if len( horsePaths ): paths[Define.MODEL_HORSE_MAIN] = horsePaths

		return paths

	def onHorseModelLoad( self, event, modelDict ):
		"""
		玩家赛马模型加载完成
		"""
		if not self.inWorld: return

		# 主体模型
		mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# 如果再次加载失败则不再加载
			if self.isLoadDefaultModelFailed:
				self.createHorseModel( event )
			return

		roleInfo = self.getModelInfo()
		rds.roleMaker.partModelAttachEffect( mainModel, roleInfo )
		#附属模型发型
		headModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
		self.attachHairModel( mainModel, headModel )
		profession = self.getClass()
		gender = self.getGender()
		rds.roleMaker.hairModelAttachEffect( headModel, self.hairNumber, self.fashionNum, profession, gender )
		# 法宝模型
		talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
		self.attachTalismanModel( mainModel, talismanModel )
		self.talismanAttachEffect( talismanModel )

		# 马模型
		horseModel = modelDict.get( Define.MODEL_HORSE_MAIN )
		if horseModel is None: return
		if self.hasFlag( csdefine.ENTITY_FLAG_CHRISTMAS_HORSE ):
			subDyes = rds.npcModel.getModelDyes( Const.HORSERACE_CHRISTMAS_MODEL_NUMBER )
			rds.effectMgr.createModelDye( horseModel, subDyes )

		rds.effectMgr.linkObject( horseModel, Const.HORSERACE_MODEL_HP, mainModel )
		self.setModel( horseModel, event )
		rds.actionMgr.playAction( mainModel, Const.MODEL_ACTION_RIDE_STAND )

		self.isLoadDefaultModelFailed = False

	# ----------------------------------------------------------------------------------------------------
	# 玩家摆摊模型相关
	# ----------------------------------------------------------------------------------------------------
	def createVendModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		创建摆摊模型
		@type	event	:	int
		@param	event	: 	加载事件
		"""
		paths = self.getVendModelPaths()
		functor = Functor( self.onVendModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )
		self.setVendModel()

	def getVendModelPaths( self ):
		"""
		获取摆摊模型路径
		@return dict
		"""
		paths = {}
		modelNum = Const.VEND_MODELNUM[self.getGender()]
		modelPaths = rds.npcModel.getModelSources( modelNum )
		paths[Define.MODEL_DEFAULT_MAIN] = modelPaths

		return paths

	def onVendModelLoad( self, event, modelDict ):
		"""
		玩家摆摊模型加载完成
		"""
		if not self.inWorld: return

		# 主体模型
		mainModel = modelDict.get( Define.MODEL_DEFAULT_MAIN )
		if mainModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# 如果再次加载失败则不再加载
			if self.isLoadDefaultModelFailed:
				self.createVendModel( event )
			return

		self.setModel( mainModel, event )
		self.isLoadDefaultModelFailed = False

	# ----------------------------------------------------------------------------------------------------
	# 玩家变身模型相关
	# ----------------------------------------------------------------------------------------------------
	def createChangeModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		创建摆摊模型
		@type	event	:	int
		@param	event	: 	加载事件
		"""
		if not self.currentModelNumber: return
		paths = self.getChangeModelPaths()
		functor = Functor( self.onChangeModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getChangeModelPaths( self ):
		"""
		获取变身模型路径
		@return dict
		"""
		paths = {}
		# 记号 yk 需要修改 2009-12-29 16:02
		if self.currentModelNumber == "fishing":
			profession = self.getClass()
			gender = self.getGender()
			roleInfo = self.getModelInfo()
			# 角色主体模型
			bodyPaths= rds.roleMaker.getShowModelPath( roleInfo )
			if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
			# 附属模型发型
			hairPaths = rds.roleMaker.getHairModelPath( self.hairNumber, self.fashionNum, profession, gender )
			if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths
			# 额外模型法宝
			talismanPaths = rds.roleMaker.getTalismanModelPath( self.talismanNum )
			if len( talismanPaths ): paths[Define.MODEL_EQUIP_TALIS] = talismanPaths
			# 附属模型右手鱼竿
			paths[Define.MODEL_EQUIP_RHAND] = [Const.FISHING_MODEL_PATH]
		else:
			paths[Define.MODEL_DEFAULT_MAIN] = rds.npcModel.getModelSources( self.currentModelNumber )
			vHps = rds.npcModel.getVehicleHps( self.currentModelNumber )
			vModelIDs = rds.npcModel.getVehicleModelIDs( self.currentModelNumber )
			for hp, modelID in zip( vHps, vModelIDs ):
				if hp == Const.MODEL_RIGHT_HAND_HP:
					paths[Define.MODEL_EQUIP_RHAND] = rds.npcModel.getModelSources( modelID )
				elif hp == Const.MODEL_LEFT_HAND_HP:
					paths[Define.MODEL_EQUIP_LHAND] = rds.npcModel.getModelSources( modelID )
				elif hp == Const.MODEL_LEFT_SHIELD_HP:
					paths[Define.MODEL_EQUIP_LHAND] = rds.npcModel.getModelSources( modelID )

		return paths

	def onChangeModelLoad( self, event, modelDict ):
		"""
		玩家变身模型加载完成
		"""
		if not self.inWorld: return

		if self.currentModelNumber == "fishing":
			# 主体模型
			mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
			if mainModel is None:
				self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# 如果再次加载失败则不再加载
				if self.isLoadDefaultModelFailed:
					self.createChangeModel( event )
				return

			roleInfo = self.getModelInfo()
			rds.roleMaker.partModelAttachEffect( mainModel, roleInfo )
			#附属模型发型
			headModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
			self.attachHairModel( mainModel, headModel )
			profession = self.getClass()
			gender = self.getGender()
			rds.roleMaker.hairModelAttachEffect( headModel, self.hairNumber, self.fashionNum, profession, gender )
			# 附属模型右手武器
			righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
			self.attachRHModel( mainModel, righthandModel )
			# 法宝模型
			talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
			self.attachTalismanModel( mainModel, talismanModel )
			self.talismanAttachEffect( talismanModel )
			# 如果不是时装模式，则显示额外装备粒子效果
			if not self.fashionNum: self.resetEquipEffect( mainModel )
			# 如果职业是法师，则显示脚底粒子效果
			if self.getClass() == csdefine.CLASS_MAGE:
				rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = self.getParticleType() )
		else:
			mainModel = modelDict.get( Define.MODEL_DEFAULT_MAIN )
			if mainModel is None:
				self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# 如果再次加载失败则不再加载
				if self.isLoadDefaultModelFailed:
					self.createChangeModel( event )
				return

			if not self.onFengQi:	# 在凤栖副本武器模型特殊处理
				# 附属模型右手武器
				righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
				self.attachRHModel( mainModel, righthandModel )
				# 附属模型左手武器
				lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
				self.attachLHModel( mainModel, lefthandModel )
			else:
				self.set_lefthandFDict()
				self.set_righthandFDict()

			# 主模型附带光效
			hps = rds.npcModel.getHps( self.currentModelNumber )
			particles = rds.npcModel.getParticles( self.currentModelNumber )
			for hp, particle in zip( hps, particles ):
				rds.effectMgr.createParticleBG( mainModel, hp, particle, type = self.getParticleType() )
			# 主模型附带dye
			subDyes = rds.npcModel.getModelDyes( self.currentModelNumber )
			rds.effectMgr.createModelDye( mainModel, subDyes )
			self.delTalismanModel()

		self.setModel( mainModel, event )
		if self.currentModelNumber == "fishing":
			rds.actionMgr.playAction( mainModel, Const.MODEL_ACTION_FISHING )

		self.isLoadDefaultModelFailed = False

	# ----------------------------------------------------------------------------------------------------
	# 玩家死亡模型相关
	# ----------------------------------------------------------------------------------------------------
	def enableSkeletonCollider( self ):
		"""
		开启玩家死亡模型的碰撞盒子
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return
		BoundingBox = BigWorld.BoxAttachment()
		BoundingBox.name = Const.ROLE_DEAD_HP
		BoundingBox.minBounds = ( -0.5, -1.5, -0.5 )
		BoundingBox.maxBounds = ( 0.5, 1.5, 0.5 )
		model.node( Const.ROLE_DEAD_HP ).attach( BoundingBox )
		self.skeletonCollider = BigWorld.SkeletonCollider()
		self.skeletonCollider.addCollider( BoundingBox )

	def disableSkeletonCollider( self ):
		"""
		关闭玩家死亡模型的碰撞盒子
		"""
		if not self.inWorld: return
		BoundingBox = None
		if hasattr( self, "skeletonCollider" ) and self.skeletonCollider:
			BoundingBox = self.skeletonCollider.getCollider( 0 )
			self.skeletonCollider = None
			del self.skeletonCollider
		model = self.getModel()
		if model is None: return
		if BoundingBox:
			model.node( Const.ROLE_DEAD_HP ).detach( BoundingBox )

	def enableUnitSelectModel( self ):
		"""
		开启死亡模型特有光圈
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return
		self.emptyModel = BigWorld.Model( Const.EMPTY_MODEL_PATH )
		self.addModel( self.emptyModel )
		pos = rds.effectMgr.accessNodePos( model, Const.ROLE_DEAD_HP )
		self.emptyModel.position = pos
		target = rds.targetMgr.getTarget()
		if target is None: return
		if target.id == self.id:
			UnitSelect().setTarget( self.emptyModel )

	def disableUnitSelectModel( self ):
		"""
		关闭死亡模型特有光圈
		"""
		if not self.inWorld: return
		if self.emptyModel and ( self.emptyModel in list( self.models ) ):
			self.delModel( self.emptyModel )
		self.emptyModel = None
		target = rds.targetMgr.getTarget()
		if target is None: return
		if target.id == self.id:
			UnitSelect().setTarget( self )

	def resetUnitSelectModel( self ):
		"""
		重新设置死亡光圈
		"""
		if not self.inWorld: return
		if self.state != csdefine.ENTITY_STATE_DEAD: return
		model = self.getModel()
		if model is None: return
		pos = rds.effectMgr.accessNodePos( model, Const.ROLE_DEAD_HP )
		if pos == Math.Vector3():	#只能这样解决访问不到绑定点位置的Bug
			BigWorld.callback( 1.0, self.resetUnitSelectModel )
		else:
			self.enableSkeletonCollider()
			self.enableUnitSelectModel()

	# ----------------------------------------------------------------------------------------------------
	# 玩家飞行传送模型相关
	# ----------------------------------------------------------------------------------------------------
	def createFlyModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		创建飞行模型
		@type	event	:	int
		@param	event	: 	加载事件
		"""
		paths = self.getFlyModelPaths()
		functor = Functor( self.onFlyModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getFlyModelPaths( self ):
		"""
		获取飞行模型路径
		@return dict
		"""
		paths = self.getEquipModelPaths()

		if self.flyTelModelNum:
			modelNum = self.flyTelModelNum
		else:
			modelNum = Const.TELEPORT_MODELNUM
		flyModelPaths = rds.npcModel.getModelSources( modelNum )
		paths[Define.MODEL_FLY_MAIN] = flyModelPaths

		return paths

	def onFlyModelLoad( self, event, modelDict ):
		"""
		玩家飞行模型加载完成
		"""
		if not self.inWorld: return

		mainModel = self.composeEquipModel( modelDict )

		# 骑宠模型
		flyModel = modelDict.get( Define.MODEL_FLY_MAIN )
		if flyModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# 如果再次加载失败则不再加载
			if self.isLoadDefaultModelFailed:
				self.createFlyModel( event )
			return
		rds.effectMgr.linkObject( flyModel, Const.TELEPORT_HP, mainModel )

		self.setModel( flyModel, event )
		flyModel.scale = ( 0.9, 0.9, 0.9 )
		rds.actionMgr.playAction( mainModel, Const.MODEL_ACTION_RIDE_RUN )

		self.isLoadDefaultModelFailed = False

	def getSlaveDart( self ):
		"""
		获取玩家所属的镖车
		"""
		if self.vehicle:
			if self.vehicle.inWorld and self.vehicle.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
				return self.vehicle
		return None

	def replacePartModel( self, newModels ):
		"""
		替换整个身体部分模型
		换装时候调用
		"""
		if not self.inWorld: return
		if len( newModels ) == 0: return
		mainModel = newModels.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None: return

		oldModel = self.getModel()
		if oldModel is None: return

		self.onUpdateRoleModel()	# 一些动作限制的处理

		if newModels.has_key( Define.MODEL_EQUIP_HEAD ):
			hairModel = newModels[Define.MODEL_EQUIP_HEAD]
		else:
			hairModel = oldModel.head

		self.set_hairNumber()
		# 武器盾牌替换
		lefthand = oldModel.left_hand
		righthand = oldModel.right_hand
		leftshield = oldModel.left_shield

		oldModel.head = None
		oldModel.left_hand = None
		oldModel.right_hand = None
		oldModel.left_shield = None

		mainModel.head = hairModel
		mainModel.left_hand = lefthand
		mainModel.right_hand = righthand
		mainModel.left_shield = leftshield
		# 光效效果
		if not self.fashionNum:
			self.resetEquipEffect( mainModel )
		# 法师特有光效的说
		if self.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = self.getParticleType() )
		# 重设法宝跟随目标点
		matrixProvider = rds.effectMgr.accessNode( mainModel, Const.TALISMAN_TARGET_HP )
		self.setTalismanTarget( matrixProvider )

		slaveDart = self.getSlaveDart()
		if self.vehicleModelNum:
			oldModel.OnActionStart = None
			self.updateRoleModel( mainModel )
			self.flushAttachments_()
			mainModel.OnActionStart = self.onActionStart
		elif slaveDart:
			slaveDart.updateAttachModel( mainModel )
			self.flushAttachments_()
			mainModel.OnActionStart = self.onActionStart
		elif self.state == csdefine.ENTITY_STATE_RACER:
			oldModel.OnActionStart = None
			rds.effectMgr.linkObject( self.model, Const.HORSERACE_MODEL_HP, mainModel )
			self.flushAttachments_()
			rds.actionMgr.playAction( mainModel, Const.MODEL_ACTION_RIDE_RUN )
		else:
			self.setModel( mainModel )
		model = self.getModel()
		if hasattr( model, "shangshen1" ) :
			if model.shangshen1.tint[-2] == "_":
				if hasattr( model, "lian1" ):
					tint = model.lian1.tint
					tint += "_2"
					model.lian1 = tint

	def onUpdateRoleModel( self ):
		"""
		角色模型更新回调
		"""
		pass

	def onReplaceModelLoad( self, partModel ):
		"""
		6小部分模型创建完成,换装回调
		"""
		if not self.inWorld: return

		functor = Functor( self.replacePartModel, partModel )
		BigWorld.callback( 0.1, functor )

	def resetEquipEffect( self, model ):
		"""
		刷新光效效果表现
		"""
		self.equipEffects = []

		self.createBodyEffectBG( model, self.onEquipParticleLoad )
		self.createFeetEffectBG( model, self.onEquipParticleLoad )

	def createBodyEffectBG( self, model, callback = None ):
		"""
		胸部光效
		"""
		bodyFDict = self.bodyFDict
		profession = self.getClass()
		gender = self.getGender()
		intensifyLevel = bodyFDict["iLevel"]
		# 绑定新的身体发射光芒效果(胸部装备强化至4星时出现)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, callback, self.getParticleType() )

		# 绑定新的各职业向上升光线(胸部装备强化至6星时出现)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, callback, self.getParticleType() )

		# 绑定新的身体周围盘旋上升光带( 胸部装备强化至9星时出现 )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, callback, self.getParticleType() )

		# 绑定新的龙型旋转光环( 胸部装备强化至9星时出现 )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, callback, self.getParticleType() )

	def createFeetEffectBG( self, model, callback = None ):
		"""
		鞋子光效
		"""
		intensifyLevel = self.feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, callback, self.getParticleType() )

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
		if self.state in [csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_DANCE, csdefine.ENTITY_STATE_DOUBLE_DANCE] or not visible:
			rds.effectMgr.fadeOutParticle( particle )
		else:
			rds.effectMgr.fadeInParticle( particle )

	def set_hairNumber( self, oldHairNumber = 0 ):
		"""
		发型改变
		"""
		rds.roleMaker.createHairModelBG( self.hairNumber, self.fashionNum, self.getClass(), self.getGender(), self.onHairModelLoad )

	def onHairModelLoad( self, hairModel ):
		"""
		callback Method
		发型换装完成回调
		"""
		if not self.inWorld: return
		self.attachHairModel( self.getModel(), hairModel )

	def attachHairModel( self, mainModel, hairModel ):
		"""
		加载头发
		"""
		rds.effectMgr.linkObject( mainModel, Const.MODEL_HAIR_HP, hairModel )
		self.updateVisibility()

	def switchHairAction( self, actionName ):
		"""
		匹配头发相关动作
		"""
		model = self.getModel()
		if model is None: return

		hairModel = model.head
		if hairModel is None: return

		if "run" in actionName or "jump" in actionName:
			hairActionName = Const.HAIR_MODEL_ACTION2
		else:
			hairActionName = Const.HAIR_MODEL_ACTION1

		rds.actionMgr.playAction( hairModel, hairActionName )

	def isEquipShow( self ):
		"""
		是否立即显示装备更新
		"""
		if self.state == csdefine.ENTITY_STATE_CHANGING: return False
		if self.actionSign( csdefine.ACTION_FORBID_CHANGE_MODEL ):
			return False
		return True

	def set_faceNumber( self, oldFaceNumber = 0 ):
		"""
		脸部改变
		"""
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onFaceModelLoad )

	def onFaceModelLoad( self, partModel ):
		"""
		callback Method
		脸型换装完成回调
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_bodyFDict( self, oldbodyFDict = None ):
		"""
		上身改变
		"""
		# 有时装情况下，直接返回
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onBodyModelLoad )

	def onBodyModelLoad( self, partModel ):
		"""
		callback Method
		上身换装完成回调
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_volaFDict( self, oldvolaFDict = None ):
		"""
		手套模型编号改变
		"""
		# 有时装情况下，直接返回
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onVolaModelLoad )

	def onVolaModelLoad( self, partModel ):
		"""
		callback Method
		手套换装完成回调
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_breechFDict( self, oldbreechFDict = None ):
		"""
		裤子模型编号改变
		"""
		# 有时装情况下，直接返回
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onBreechModelLoad )

	def onBreechModelLoad( self, partModel ):
		"""
		callback Method
		下身换装完成回调
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_feetFDict( self, oldfeetFDict = None ):
		"""
		鞋子模型编号改变
		"""
		# 有时装情况下，直接返回
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onFeetModelLoad )

	def onFeetModelLoad( self, partModel ):
		"""
		callback Method
		鞋子换装完成回调
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_talismanNum( self, oldTalismanNum = 0 ):
		"""
		法宝模型有改变
		"""
		if not self.isEquipShow(): return
		rds.roleMaker.createTalismanModelBG( self.talismanNum, self.onTalismanModelLoad )

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
		self.tam.away = 1.0
		self.tam.proximityCallback = self.talisManCallback
		self.tam.awayCallback = self.talisManAwayCallback

	def setTalismanTarget( self, matrixProvider ):
		"""
		设置法宝的跟随目标
		参数必须为 MatrixProvider 类型
		"""
		# 触发法宝的移动匹配
		if matrixProvider is None: return
		if self.tam is None: return

		self.tam.target = matrixProvider

	def talisManCallback( self ):
		"""
		法宝接近回调
		"""
		if not self.inWorld: return
		if self.talismanModel is None: return
		if self.tam is None: return
		if self.model is None: return

		self.tam.endSpeed = 1.0
		self.tam.speed = 1.0
		self.tam.awayCallback = self.talisManAwayCallback

	def talisManAwayCallback( self ):
		"""
		法宝过远接近回调
		"""
		node =  rds.effectMgr.accessNode( self.model, Const.TALISMAN_TARGET_HP )
		nodeMatrix = Math.Matrix(node)
		if nodeMatrix.translation.length < 0.1:
			self.talismanModel.position = self.position
			BigWorld.callback( 1, self.talisManAwayCallback )
			return

		orbitorMotor = self.tam
		rolePosition = Math.Vector3( self.position )
		rolePosition.y += 2.0
		talismanPosition = Math.Vector3( self.talismanModel.position )
		distance = csarithmetic.distancePP3( rolePosition, talismanPosition )
		mayBeSpeed = distance / 1.0
		endSpeed = max( self.move_speed, mayBeSpeed )
		if distance > 2.0:
			orbitorMotor.endSpeed = endSpeed
			orbitorMotor.speed = endSpeed
		else:
			orbitorMotor.endSpeed = self.move_speed
			orbitorMotor.speed = self.move_speed
		orbitorMotor.proximityCallback = self.talisManCallback

	def delTalismanModel( self ):
		"""
		删除法宝模型
		"""
		if self.talismanModel and self.talismanModel in list( self.models ):
			self.delModel( self.talismanModel )
			if self.tam.owner != None: self.tam.owner.delMotor( self.tam )
			self.talismanModel = None

	def setTalismanModel( self, model, matrixProvider ):
		"""
		设置法宝模型
		"""
		self.delTalismanModel()
		self.talismanModel = model
		self.updateVisibility()
		if self.talismanModel is None: return
		self.addModel( self.talismanModel )
		self.talismanModel.position = self.position + ( 1.2, 1.7, 0.0 )
		rds.actionMgr.playAction( self.talismanModel, Const.MODEL_ACTION_PLAY )
		if self.tam is None: self.createTalismanAM()
		self.setTalismanTarget( matrixProvider )
		self.talismanModel.addMotor( self.tam )

	def onTalismanModelLoad( self, model ):
		"""
		法宝模型加载回调
		"""
		if not self.inWorld: return
		roleModel = self.getModel()
		if roleModel is None: return
		self.talismanAttachEffect ( model )
		self.attachTalismanModel( roleModel, model )

	def attachTalismanModel( self, mainModel, talismanModel ):
		"""
		附加法宝模型
		"""
		matrixProvider = rds.effectMgr.accessNode( mainModel, Const.TALISMAN_TARGET_HP )
		self.setTalismanModel( talismanModel, matrixProvider )

	def switchEquipEffect( self, switch ):
		"""
		开关身上的效果
		在某些时候需要关闭身上的粒子效果，如死亡
		"""
		if not self.inWorld: return

		isDance = ( self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE )
		isFace = len( self.tempFace )

		for particle in self.equipEffects:
			if ( isDance or isFace ) and switch:
				rds.effectMgr.fadeOutParticle( particle )
			elif switch:
				rds.effectMgr.fadeInParticle( particle )
			else:
				rds.effectMgr.fadeOutParticle( particle )

	def set_lefthandFDict( self, oldLHFDict = None ):
		"""
		装备左手武器
		"""
		if not self.isEquipShow(): return
		rds.roleMaker.createMWeaponModelBG( self.lefthandFDict, self.onLefthandModelLoad )
		# 重设武器类型
		self.resetWeaponType()
		# 重设防具类型
		self.resetArmorType()

	def onLefthandModelLoad( self, model ):
		"""
		左手武器模型加载完成
		"""
		if not self.inWorld: return
		roleModel = self.getModel()
		if roleModel is None: return
		self.weaponAttachEffect( model, self.lefthandFDict )
		self.attachLHModel( roleModel, model )

	def attachLHModel( self, mainModel, lModel ):
		"""
		装载左手模型
		"""
		if not hasattr( mainModel, "left_hand" ): return
		# 卸载旧刀光
		self.detachLeftLoft( mainModel.left_hand )
		# 换模型
		profession = self.getClass()
		key = Const.MODEL_LEFT_SHIELD_HP
		if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
			key = Const.MODEL_LEFT_HAND_HP
		rds.effectMgr.linkObject( mainModel, key, lModel )
		# 装载新刀光
		self.createLeftLoft()
		self.updateVisibility()

	def set_righthandFDict( self, oldRHFDict = 0 ):
		"""
		装备右手武器
		"""
		if not self.isEquipShow(): return
		rds.roleMaker.createMWeaponModelBG( self.righthandFDict, self.onRighthandModelLoad )
		# 重设武器类型
		self.resetWeaponType()

	def onRighthandModelLoad( self, model ):
		"""
		右手武器加载回调
		"""
		if not self.inWorld: return
		roleModel = self.getModel()
		if roleModel is None: return
		self.weaponAttachEffect( model, self.righthandFDict )
		self.attachRHModel( roleModel, model )

	def attachRHModel( self, mainModel, rModel ):
		"""
		装载右手模型
		"""
		if not hasattr( mainModel, "right_hand" ): return
		# 卸载旧刀光
		self.detachRightLoft( mainModel.right_hand )
		# 换模型
		rds.effectMgr.linkObject( mainModel, Const.MODEL_RIGHT_HAND_HP, rModel )
		# 装载刀光
		self.createRightLoft()
		self.updateVisibility()
		weaponNum = self.righthandFDict["modelNum"]
		if weaponNum:
			actionName = rds.itemModel.getActionsName( weaponNum )
			if actionName:
				timetick = rds.itemModel.getTimetick( weaponNum )
				def callback():
					if not rModel:return
					if rModel.hasAction( actionName ):
						rds.actionMgr.playAction( rModel, actionName )
					BigWorld.callback(random.randint( timetick[0], timetick[1] ),callback )
				callback()

	def set_fashionNum( self, oldFashionNum = 0 ):
		"""
		时装改变
		"""
		if self.onFengQi: return
		if not self.isEquipShow(): return
		if self.id == BigWorld.player().espial_id:
			ECenter.fireEvent( "EVT_ON_ESPIAL_TARGET_FASHIONNUM_CHANGE", self )
		rds.roleMaker.createFashionModelBG( self.id, self.getModelInfo(), self.onFashionModelLoad )

	def onFashionModelLoad( self, partModels ):
		"""
		时装模型后线程加载完成回调
		"""
		if not self.inWorld: return
		self.replacePartModel( partModels )

	def set_adornNum( self, oldAdornNum = 0 ):
		"""
		饰品改变
		"""
		if not self.isEquipShow(): return
		pass

	def set_weaponAppendState( self, oldState = True ):
		"""
		武器悬挂状态改变
		"""
		pass

	def set_headTexture( self, oldHeadTexture = 0 ):
		"""
		角色头像贴图改变 by姜毅
		"""
		pass

	def onAddRoleHP( self, entityID, addHp ):
		"""
		define method
		某个role增加血量后回调 目前主要用于血恢复表现 by 姜毅
		"""
		pass

	def onGetSuitDatas( self, oksData ):
		"""
		define method
		获得一键套装数据
		@param oksData : PY_DICT
		"""
		pass

	def onSwitchSuit( self, suitIndex ):
		"""
		更换套装
		"""
		pass

	def onPlayActionStart( self, actionNames ):
		"""
		开始播放动作
		"""
		CombatUnit.onPlayActionStart( self, actionNames )

	def onPlayActionOver( self, actionNames ):
		"""
		动作播放结束
		"""
		CombatUnit.onPlayActionOver( self, actionNames )
		if self.vehicleModelNum:
			self.onSwitchVehicle( Const.MODEL_ACTION_STAND )
		self.setArmCaps()

	# -------------------------------------------------				

	def resetSnake( self ):
		CombatUnit.resetSnake( self )
		for en in BigWorld.entities.values():
			if en.__class__.__name__ == "Pet":
				if en.getOwner() and en.getOwner().id == self.id:
					en.onSnakeStateChange()
					return

	def setModelVisible( self, visibleType ):
		"""
		设置模型显示方式
		参见 Define.MODEL_VISIBLE_TYPE_*
		"""
		if not self.inWorld: return
		if self.model is None: return
		roleModel = self.getModel()
		if roleModel is None: return
		#if self.modelVisibleType == visibleType:return 去掉这句，因为播放表情动作时 这里会return
		self.modelVisibleType = visibleType
		# 不显示模型
		if visibleType == Define.MODEL_VISIBLE_TYPE_FALSE:
			self.setVisibility( False )
			rds.effectMgr.setModelAlpha( self.model, 0.0 )
			if self.talismanModel:
				rds.effectMgr.setModelAlpha( self.talismanModel, 0.0 )
			self.model.visibleAttachments = False
			roleModel.visibleAttachments = False
		# 显示整体模型
		elif visibleType == Define.MODEL_VISIBLE_TYPE_TRUE:
			self.setVisibility( True )
			roleModel.visibleAttachments = False
			self.model.visibleAttachments = False
			rds.effectMgr.setModelAlpha( self.model, 1.0 )
			if self.talismanModel:
				rds.effectMgr.setModelAlpha( self.talismanModel, 1.0 )
			self.switchEquipPartModel( True )
			self.switchEquipEffect( True )
			self.switchVehicleEffect( True )
		# 除了血条，其他不显示
		elif visibleType == Define.MODEL_VISIBLE_TYPE_FBUTBILL:
			self.setVisibility( False )
			rds.effectMgr.setModelAlpha( self.model, 0.0 )
			if self.talismanModel:
				rds.effectMgr.setModelAlpha( self.talismanModel, 0.0 )
			self.model.visibleAttachments = True
			roleModel.visibleAttachments = True
			self.switchEquipPartModel( False )
			self.switchEquipEffect( False )
			self.switchVehicleEffect( False )
		# 半透明显示模型
		elif visibleType == Define.MODEL_VISIBLE_TYPE_SNEAK:
			self.setVisibility( True )
			rds.effectMgr.setModelAlpha( self.model, 0.5, 1.0 )
			if self.talismanModel:
				rds.effectMgr.setModelAlpha( self.talismanModel, 0.5, 1.0 )
			self.model.visibleAttachments = False
			roleModel.visibleAttachments = False
			self.switchEquipPartModel( True )
			self.switchEquipEffect( True )
			self.switchVehicleEffect( True )

	def switchEquipPartModel( self, visible ):
		"""
		开关玩家身上的附加模型
		"""
		if not self.inWorld: return
		roleModel = self.getModel()
		if roleModel is None: return

		for keyName in [ "head" ]:
			model = getattr( roleModel, keyName, None )
			if model is None: continue
			model.visible = visible

		isDance = ( self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE )
		isFace = len( self.tempFace )
		for keyName in [ "left_hand", "right_hand", "left_shield" ]:
			model = getattr( roleModel, keyName, None )
			if model is None: continue
			# 状态为跳舞或者共舞状态或者表情动作, 且visible为True时，总不显示武器。
			if ( isDance or isFace )  and visible:
				model.visible = False
			else:
				model.visible = visible

	def visibilitySettingChanged( self, key, value ) :
		"""
		用户通过界面设置改变模型可见性
		"""
		BigWorld.player().isRolesVisible = True
		self.updateVisibility()

	def setVendModel( self ):	# 15:31 2008-9-1，wsf add
		"""
		设置摆摊状态模型
		"""
		ECenter.fireEvent( "EVT_ON_VEND_ON_SET_SIGNBOARD", self.id )

	def canVendInArea( self ):
		"""
		指定区域能否摆摊
		"""
		pos = self.position
		x = pos[0]
		y = pos[1]
		z = pos[2]
		space = self.getSpaceLabel()
		if space in roleVendData.keys():
			data = roleVendData.get( space )
			for a, b in data.items():
				if not len( a ): return False
				if not len( b ): return False
				if abs( x - a[0] ) <= b[0] and abs( y - a[1] ) <= b[1] and abs( z - a[2] ) <= b[2]:
					return True
		return False

	def setArmCaps( self ) :
		"""
		set caps
		"""
		profession = self.getClass()
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.lefthandFDict["modelNum"]
		else:
			weaponNum = self.righthandFDict["modelNum"]

		armCaps = []
		if weaponNum:
			if self.weaponType == Define.WEAPON_TYPE_LIGHTSHARP:
				armCaps.append( Define.CAPS_DAN_WEAPON )	# 单手剑
			elif self.weaponType == Define.WEAPON_TYPE_DOUBLEHAND:
				armCaps.append( Define.CAPS_SHUANG_WEAPON )	# 双手剑
			elif self.weaponType == Define.WEAPON_TYPE_WEIGHTSHARP:
				armCaps.append( Define.CAPS_FU_WEAPON )		# 斧头
			elif self.weaponType == Define.WEAPON_TYPE_LIGHTBLUNT:
				armCaps.append( Define.CAPS_CHANG_WEAPON )	# 长枪
			else:
				armCaps.append( Define.CAPS_WEAPON )
		else:
			armCaps.append( Define.CAPS_NOWEAPON )

		if self.onWaterArea or ( hasattr( self, "isPlayWaterRun" ) and self.isPlayWaterRun ):
			armCaps.append( Define.CAPS_FLY_WATER )

		if hasattr( self, "isJumpProcess" ) and self.isJumpProcess:
			armCaps.append( Define.CAPS_JUMP )

		if  self.findBuffByBuffID( Const.JUMP_FAST_BUFF_ID ): #迅捷移动buff存在
			armCaps.append( Define.CAPS_FASTMOVING )


		if  self.findBuffByBuffID( Const.VERTIGO_BUFF_ID1 ) or self.findBuffByBuffID( Const.VERTIGO_BUFF_ID2 ): #眩晕buff存在
			armCaps.append( Define.CAPS_VERTIGO )

		if hasattr( self, "isSprint" ) and self.isSprint:
			armCaps.append( Define.CAPS_SPRINT )

		stateCaps = Define.STATE_CAPS.get( self.state )
		model = self.getModel()
		if self.effect_state & csdefine.EFFECT_STATE_PROWL and model.hasAction( Const.MODEL_ACTION_QX_STAND ):
			stateCaps = Define.CAPS_SNEAK
		if stateCaps is None:
			caps = armCaps
		else:
			caps = [stateCaps] + armCaps
		if self.isjumpVehiProcess:caps.append(Define.CAPS_JUMP)
		self.am.matchCaps = caps

	def resetWeaponType( self ):
		"""
		设置武器类型
		"""
		profession = self.getClass()
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.lefthandFDict["modelNum"]
		else:
			weaponNum = self.righthandFDict["modelNum"]

		if weaponNum:
			weaponType = Define.CLASS_WEAPONTYPE.get( profession, [] )
			if len( weaponType ) == 0: weaponType = 0
			if profession == csdefine.CLASS_SWORDMAN:    # 剑客
				if not self.lefthandFDict["modelNum"]:
					weaponType = weaponType[0]
				else:
					weaponType = weaponType[1]
			elif profession == csdefine.CLASS_FIGHTER:  #战士
				if str( weaponNum )[1:3] == str( Define.PRE_EQUIP_TWOLANCE ):
					weaponType = weaponType[1]
				else:
					weaponType = weaponType[0]
			else:
				weaponType = weaponType[0]
			self.weaponType = weaponType
		else:
			self.weaponType = 0
		# 变身模型武器类型
		if self.currentModelNumber and not self.onFengQi:
			self.weaponType = Define.WEAPON_TYPE_BIANSHEN
		# 重设Caps状态
		self.setArmCaps()

	def resetArmorType( self ):
		"""
		设置防具类型
		根据策划规则：首先判断entity左手是否装备盾牌
		再判断是否有胸甲，如果有则走职业对应防具类型路线
		如果没有则走策划自定义防具类型路线
		"""
		profession = self.getClass()
		weaponNum = self.lefthandFDict["modelNum"]
		if weaponNum and profession == csdefine.CLASS_FIGHTER:
			type = Define.ARMOR_TYPE_SHIELD
		else:
			type = rds.spellEffect.getArmorTypeByClass( self.getClass() )
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

	def isPlayer( self ):
		"""
		标记角色还不是玩家
		"""
		return False

	def getName( self ):
		"""
		取得entity名称
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
			return "***"
		return self.playerName

	def getTitle( self ):
		"""
		virtual method.
		获取称号
		@return: string
		"""
		return self.titleName

	def set_title( self, oldTitle ) :
		if oldTitle != self.title:
			ECenter.fireEvent( "EVT_ON_ENTITY_TITLE_CHANGED", self, oldTitle, self.titleName, self.getTitleColor( self.title ) )

	def getHeadTexture( self ) :
		"""
		获取角色头像 modify by姜毅
		"""
		headTexturePath = rds.iconsSound.getHeadTexturePath( self.headTextureID )
		if not headTexturePath is None: return headTexturePath
		return Const.ROLE_HEADERS[self.getClass()][self.getGender()]

	def getObjHeadTexture( self, objHeadTextureID ) :
		"""
		获取角色头像 modify by姜毅
		"""
		headTexturePath = rds.iconsSound.getHeadTexturePath( objHeadTextureID )
		return headTexturePath

	def getBoundingBox( self ):
		"""
		virtual method.
		返回代表自身的bounding box的长、高、宽的Math.Vector3实例；
		如果自身的模型有被缩放过，需要提供缩放后的值。

		@return: Math.Vector3
		"""
		# 为了使判断一致，主角的bounding box服务器与客户端使用相同的值，
		# 如果有必要，可以考虑根据不同的职业使用不同的值
		# 将来如果有放大模型的技能，可能需要根据实际情况决定是否加入放大倍率
		if self.vehicle:
			return self.vehicle.getBoundingBox()
		if self.vehicleModelNum:
			return csconst.VEHICLE_MODEL_BOUND
		return csconst.ROLE_MODEL_BOUND

	def canSelect( self ):
		"""
		是否允许被选择
		"""
		if self.state == csdefine.ENTITY_STATE_PENDING:
			return False
		if self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return False
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:	# 潜行状态不能被选择13:33 2008-12-1,wsf
			return False

		return True

	# ----------------------------------------------------------------------------------------------------
	#  角色作为目标相关
	# ----------------------------------------------------------------------------------------------------
	def onTargetClick( self, player ):
		"""
		当角色作为目标而被点击中时，该方法被调用
		"""
		GameObject.onTargetClick( self, player )
		if player.id == self.id:
			return Define.TARGET_CLICK_SUCC

	def onTargetFocus( self ) :
		"""
		当鼠标移动到该角色身上时，该函数被调用
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		if BigWorld.player().queryRelation( self ) == csdefine.RELATION_ANTAGONIZE :
			rds.ccursor.set( "attack" )
		else:
			rds.ccursor.set( "normal" )
		#if not BigWorld.player().canPk( self ) or \
		#not BigWorld.player().currAreaCanPk() or \
		#not self.currAreaCanPk():
		#	rds.ccursor.set( "normal" )
		#else:
		#	rds.ccursor.set( "attack" )
		GameObject.onTargetFocus( self )

	def onSetTargetFocus( self ):
		"""
		显示焦点光圈
		"""
		if rds.targetMgr.bindTargetCheck( self ):
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# 设置焦点光圈颜色
				texture = UnitSelect().getTexture( self )
				UnitSelect().setFocusTexture( texture )
				UnitSelect().setFocus( self.emptyModel )
			else:
				UnitSelect().setFocus( self )

	def onTargetBlur( self ) :
		"""
		当鼠标离开该角色身上时，该函数被调用
		"""
		rds.ccursor.set( "normal" )
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		GameObject.onTargetBlur( self )

	# ----------------------------------------------------------------------------------------------------
	# 其他
	# ----------------------------------------------------------------------------------------------------
	def gossipWith( self, entity, dlgKey ) :
		"""
		与 NPC 对话
		hyw--2008.10.08
		@type			entity : BigWorld.Entity
		@param			entity : 要对话的 NPC
		@type			tag	   : str
		@param			tag	   : 对话关键字
		"""
		model = entity.getModel()
		if model and model.visible:	 # CSOL-1311模型可见才能对话
			self.cell.gossipWith( entity.id, dlgKey )

	def fxenterWorld( self ):
		"""
		进入游戏时显示的光效
		"""
		rds.effectMgr.createParticleBG( self.getModel(), "HP_root", "particles/xw_0091/xw_0091.xml", type = self.getParticleType() )
		rds.effectMgr.createParticleBG( self.getModel(), "HP_root", "particles/xw_0091/xw_0091_a.xml", type = self.getParticleType() )

	def teleportPlayer( self, space, position, direction ):
		"""
		Server Teleport
		@type		space 		: str / int
		@param		space 		: 如果服务器存在则为 space 名称，否则为 spaceID
		@type		position	: Math.Vector3 or tuple of 3 elements
		@param		position	: 位置
		@type		direction	: Math.Vector3 or tuple of 3 elements
		@param		direction	: 面向
		@return					: None
		"""
		self.stopMove()
		if BigWorld.server() is None :
			self.physics.teleportSpace( space )
			self.physics.teleport( position, direction )
		else :
			self.cell.wizCommand( self.id, "goto", "%s %f %f %f %f %f %f" % ( (space,) + tuple(position) + tuple(direction) ) )

	def ChangeTime( self, newtime, duration):
		"""
		HZM 0308 , control time function
		要求改变客户端的时间
		@param newtime: new environment time，可以以两种形式出现：
						   一种是 时：分，如：  01:00 （凌晨1点）
						   另一种是浮点数，如： 1.0
						   任何其它格式的时间不会抛出异常，也不会起作用

		@param duration: time LAST HOW LONG，按策划案要求，以分为单位
		@type  duration: UINT16
		"""
		self.cell.ChangeTime(newtime, duration)

	def ReceiveChangeTime( self, newtime):
		"""
		 改变客户端时间为newtime指定的时间
		@param newtime: new environment time，可以以两种形式出现：
						   一种是 时：分，如：  01:00 （凌晨1点）
						   另一种是浮点数，如： 1.0
						   任何其它格式的时间不会抛出异常，也不会起作用
		@type newtime : FLOAT
		"""
		BigWorld.timeOfDay(newtime)

	def SetWeather( self, newweather, duration):
		"""
		改变客户端天气为newweather指定的天气
		注：此功能未能实现
		@param newweather: new environment Weather
		@type newweather: Weather OBJECT
		@param duration: Weather LAST HOW LONG
		@type duration: UINT16
		"""
		w = BigWorld.weather(self.spaceID)
		ws = w.system( "RAIN" )
		ws.direct( 2, (1, 10, 0, 0), 1)

	def onStatusMessage( self, statusID, sargs ) :
		"""
		def method
		receive all kind of status of operation
		@type				statusID : INT32
		@param				statusID : statusID defined in common/csstatus.py
		@type				sargs	 : STRING
		@param				sargs	 : in-line arguments of the status information defined in csstatus_msgs
		@return						 : None
		"""
		raise AttributeError( "role has not method 'onStatusMessage'" )

	def onDirectMessage( self, chids, spkName, msg ) :
		"""
		def method
		直接接收消息，包含频道和发言者信息
		@type				chids 	 : ARRAY <of> INT8 </of>
		@param				chids 	 : 频道列表
		@type				spkName	 : STRING
		@param				spkName	 : 发言者名称
		@type				spkName	 : STRING
		@param				spkName	 : 消息内容
		@return						 : None
		"""
		raise AttributeError( "role has not method 'onDirectMessage'" )

	def onStateChanged( self, old, new ):
		"""
		状态改变
		"""
		CombatUnit.onStateChanged( self, old, new )
		if self.state == csdefine.ENTITY_STATE_DEAD :
			ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		if new == csdefine.ENTITY_STATE_DEAD :
			#死亡则播放死亡动作。对死亡模型作了光圈更随模型变动的处理
			dieActionName = Const.MODEL_ACTION_DIE
			if Define.CAPS_DAN_WEAPON in self.am.matchCaps:
				dieActionName = Const.MODEL_ACTION_DIE_DAN
			elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
				dieActionName = Const.MODEL_ACTION_DIE_SHUANG
			elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
				dieActionName = Const.MODEL_ACTION_DIE_FU
			elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
				dieActionName = Const.MODEL_ACTION_DIE_CHANG
			rds.actionMgr.playAction( self.getModel(), dieActionName, 0.0, self.enableUnitSelectModel )
		if old == csdefine.ENTITY_STATE_DEAD :
			self.disableUnitSelectModel()

	def cooldownChanged( self, typeID, lastTime, totalTime ):
		"""
		define method
		@type 			typeID	: STRING
		@param			typeID	: cooldown type
		@type 			timeVal	: DOUBLE
		@param			timeVal	: unfreezed time
		"""
		startTime = Time.Time.time()
		endTime = startTime + lastTime
		self._attrCooldowns[typeID] = ( lastTime, totalTime, startTime, endTime )
		ECenter.fireEvent( "EVT_ON_ROLE_BEGIN_COOLDOWN", typeID, lastTime )

	def getCooldown( self, typeID ):
		"""
		"""
		coolDown = self._attrCooldowns.get( typeID )
		if coolDown is None: return ( 0, 0, 0, 0 )
		return coolDown

	def updateRoleSign( self, oldFlag, flag, type ) :
		"""
		更新玩家头顶标记（跑商状态，携带有滴血物品，
		队长，劫镖等）
		@param		oldFlag	:	旧标记
		@type		oldFlag	:	INT32
		@param		flag	:	需判断的标记
		@type		flag	:	int
		@param		type	:	标记类型（跑商，队长，劫镖等）
		@type		type	:	STRING
		@return				:	None
		"""
		isPreShow = False
		isCurrShow = self.hasFlag( flag )
		player = BigWorld.player()
		tmpFlag = flag
		if oldFlag is not None :
			flag = 1 << flag
			isPreShow = ( oldFlag & flag ) == flag
		if isCurrShow != isPreShow :
			if self.onFengQi: return
			ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, type, isCurrShow )
			if tmpFlag in [csdefine.ROLE_FLAG_CAPTAIN, csdefine.ROLE_FLAG_TEAMMING] and \
			player.isTeamMember( self.id ):					#进入队伍时调用
				self.flashTeamSign()

	def flashTeamSign( self ):
		"""
		刷新队伍标记
		"""
		player = BigWorld.player()
		isInPlayerTeam = player.isTeamMember( self.id )
		if isInPlayerTeam:
			isCurrShow = rds.viewInfoMgr.getSetting( "teammate", "sign" )
			sign = "teammate"
			if player.captainID == self.id:
				sign = "captain"
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", False )
			ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, sign, isCurrShow )
		else:
			isCurrShow = rds.viewInfoMgr.getSetting( "role", "sign" )
			self.teamSignSettingChanged( isCurrShow )

	def teamSignSettingChanged( self, value ):
		"""
		标记其他玩家（除队友外）队长标记
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_TEAMMING ):					#组队状态
			if self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN ):				#队长
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", False )
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "captain", value )
			else:															#队员
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", value )

	# ----------------------------------------------------------------
	# 监狱相关
	# ----------------------------------------------------------------
	def onPrisonContributeSure( self, money ):
		"""
		define method.
		监狱捐献提示
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().cell.onPrisonContribute()
		# "真的要花费%s捐献么？"
		showMessage( mbmsgs[0x0121] % Function.switchMoney( money ), "", MB_OK_CANCEL, query )

	# ----------------------------------------------------------------
	# 玩家装备修理
	# ----------------------------------------------------------------
	def equipRepairCompleteNotify( self ):
		"""
		修理完成
		@param all: 是否全部
		@type all: bool
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_EQUIP_REPAIR_COMPLETE" )
		for item in self.getItems( csdefine.KB_EQUIP_ID ):
			if item is None:continue
			itemOrder = item.order
			GUIFacade.onKitbagItemUpdate( 0, itemOrder, item )

	# ----------------------------------------------------------------
	# 玩家进入离开空间
	# ----------------------------------------------------------------
	def onEnterAreaFS( self ) :
		"""
		defined method.
		当进入某个区域时被触发( 同地图的区域跳转时被触发 )
		hyw -- 2008.10.08
		"""
		pass

	def onLeaveAreaFS( self ) :
		"""
		defined method.
		当离开某个区域时被触发( 同地图的区域跳转时被触发 )
		hyw -- 2008.10.08
		"""
		pass

	def onLoginSpaceIsFull( self ):
		"""
		define method.
		登陆到某场景， 场景满员了
		"""
		pass

	# -------------------------------------------------
	def onAssaultEnd( self ) :
		"""
		defined method.
		冲锋结束时被调用
		"""
		pass

	def onUseFlyItem( self ):
		"""
		define method.
		使用引路蜂回调
		"""
		pass

	# ----------------------------------------------------------------
	# 玩家技能相关
	# ----------------------------------------------------------------
	def onAddSkill( self, skillID ):
		pass

	def onRemoveSkill( self, skillID ):
		pass

	def onUpdateSkill( self, oldSkillID, newSkillID ) :
		pass

	def hasSkill( self, skillID ) :
		return skillID in self.skillList_

	def initSkillBox( self, skillIDs ):
		"""
		call in enterWorld method.
		初始化技能列表

		@param skills: like as [ skillID, ... ]
		"""
		pass

	def initSpaceSkills( self, skillIDList, spaceType ):
		"""
		Define method.
		进入空间时获得的空间专属技能列表

		param skillIDList : ARRAY OF SKILLID
		"""
		pass

	def enterEquipMake( self, entityID ):
		"""
		打开装备制造界面
		@param entityID: 操作对象
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_EQUIP_PRODUCE_WND" )

	def enterEquipExtract( self, entityID ):
		"""
		打开装备属性抽取界面
		@param entityID: 操作对象
		"""
		ECenter.fireEvent( "EVT_ON_EXTRACT_EQUIP", entityID )

	def enterEquipPour( self, entityID ):
		"""
		打开装备属性灌注界面
		@param entityID: 操作对象
		"""
		ECenter.fireEvent( "EVT_ON_POUR_EQUIP", entityID )

	def equipAttrRebuildSuccess( self ):
		"""
		属性重铸成功通知
		"""
		ECenter.fireEvent( "EVT_ON_EQUIP_ATTR_REBUILD_SUCCESS" )

	def onJumpNotifyFS( self, jumpMask ):
		"""
		Exposed method
		由服务器调用，广播给所有客户端，播放jump动作
		"""
		self.playJumpActions( jumpMask )

	def playJumpActions( self, jumpMask ):
		"""
		播放跳跃动作
		"""
		jumpTime = jumpMask & csdefine.JUMP_TIME_MASK
		if jumpTime == csdefine.JUMP_TIME_UP1:
			self.isJumpProcess = True
			self.playVehicleSound()
		elif jumpTime == csdefine.JUMP_TIME_END:
			self.isJumpProcess = False

		if self.vehicleModelNum:
			if self.vehicleType != Define.VEHICLE_MODEL_STAND:	# 在骑宠上的跳跃动作（飞行骑宠除外）
				actionNames = Const.JUMP_VEHICLE_ACTION_MAPS.get( jumpMask, [] )
				self.setArmCaps()
				rds.actionMgr.playActions( self.model, actionNames )
			return

		if jumpMask == csdefine.JUMP_TYPE_ATTACK | csdefine.JUMP_TIME_END:
			BigWorld.callback( Const.JUMP_ATTACK_DELAY, self.onJumpAttackOver )
		elif jumpMask == csdefine.JUMP_TYPE_LAND | csdefine.JUMP_TIME_UPPREPARE:
			if self.isPlayer():
				self.playJumpEffect()
			else:
				if self.effect_state & csdefine.EFFECT_STATE_PROWL:
					if not self.isSnake:	# 潜行状态下被侦测到才播放光效
						self.playJumpEffect()
				else:
					self.playJumpEffect()

		if self.inFlyDownPose: return	# 如果在播放下坐骑pose动作过程中的下落动作通知，忽略

		if Define.CAPS_DAN_WEAPON in self.am.matchCaps:
			weaponIndex = 1
		elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
			weaponIndex = 2
		elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
			weaponIndex = 3
		elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
			weaponIndex = 4
		else:
			weaponIndex = 0

		actionNames = Const.JUMP_ACTIONS_MAPS.get( jumpMask, [] )
		if len( actionNames ) == 0: return
		if actionNames.__class__.__name__ == "dict": #区分移动和静止时的动作区分
			if hasattr( self,"isMoving" ) and self.isMoving():
				actionNames = actionNames.get( weaponIndex, [] )[1]
			else:
				actionNames = actionNames.get( weaponIndex, [] )[0]
		else:
			actionNames = actionNames[weaponIndex]

		self.setArmCaps()  #设置caps以去除跳跃动作中融入walk、run、run_weapon等动作
		rds.actionMgr.playActions( self.model, actionNames )

	def playJumpEffect( self ):
		"""
		跳跃光效
		"""
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.JUMP_EFFECT_ID, self.getModel(), self.getModel(), type, type )
		if effect:
			effect.start()

	def onJumpAttackOver( self ):
		"""
		跳砍动作结束
		"""
		if not self.inWorld: return
		if self.lastJumpAttackDir == Math.Vector3(): return
		effectPos = self.position + self.lastJumpAttackDir * 2
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.JUMP_ATTACK_EFFECTID, None, None, type, type )
		if effect is None: return
		effect.setPosition( effectPos )
		effect.start()
		rds.skillEffect.playCameraEffect( Const.JUMP_ATTACK_CAMERA_EFFECTID )

	def playVehicleSound( self ):
		"""
		播放骑宠声音
		"""
		if self.vehicleModelNum:	# 处理骑宠跳跃音效，一般来说游戏都是起跳上升时发音的 by姜毅
			rate = random.random()	# 跳跃时一定几率发音
			if rate < 0.3:
				self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_JUMP )

	def onFlyJumpUpNotifyFS( self ):
		"""
		Exposed method
		由服务器调用，广播给所有客户端，提升飞行高度
		"""
		self.flyJumpUp()

	def onEnterFlyState( self ):
		"""
		define method
		进入飞行状态
		"""
		pass

	def onLeaveFlyState( self ):
		"""
		define method
		离开飞行状态
		"""
		pass

	def jumpBegin( self ):
		"""
		跳跃起手动作(类似于下蹲的动作)
		"""
		pass

	def flyJumpUp( self ):
		"""
		飞行中上升
		"""
		rds.actionMgr.playAction( self.model, Const.MODEL_ACTION_JUMP_BEGIN )

		if self.vehicleModelNum:	# 处理骑宠跳跃音效，一般来说游戏都是起跳上升时发音的 by姜毅
			rate = random.random()	# 跳跃时一定几率发音
			if rate < 0.3:
				self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_JUMP )

	def onGetBenefitTime( self, benefitTime ):
		"""
		defined method
		从服务器获得创世之光buff累积时间 by姜毅
		"""
		pass

	def onGetServerVersion( self, version ):
		"""
		获取服务器端版本
		"""
		ECenter.fireEvent( "EVT_ON_SEND_SERVER_VERSION",version )

	def canPlayEffectAction( self ):
		"""
		是否能播放效果动作
		例如闪避，格挡，被击中
		"""
		# 在坐骑上不播放
		if self.vehicleModelNum: return False
		#if self.isActionning(): return False
		# 在连续技能不播放
		#if self.isInHomingSpell: return False
		# 眩晕状态和无敌状态不播放
		EffectState_List = csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_BE_HOMING
		if self.effect_state & EffectState_List != 0: return False
		return True

	def onReceiveDamage( self, casterID, skill, damageType, damage ):
		"""
		伤害显示
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能实例
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		CombatUnit.onReceiveDamage( self, casterID, skill, damageType, damage )
		player = BigWorld.player()
		sk = skill
		petID = -1
		pet = player.pcg_getActPet()
		if pet:
			petID = pet.id
		# 自己或宠物是施法者才显示
		if casterID != player.id and casterID != petID:
			return

		dodgeActionName = Const.MODEL_ACTION_DODGE
		resistActionName = Const.MODEL_ACTION_RESIST
		if Define.CAPS_DAN_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_DAN
			resistActionName = Const.MODEL_ACTION_RESIST_DAN
		elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_SHUANG
			resistActionName = Const.MODEL_ACTION_RESIST_SHUANG
		elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_FU
			resistActionName = Const.MODEL_ACTION_RESIST_FU
		elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_CHANG
			resistActionName = Const.MODEL_ACTION_RESIST_CHANG

		# 技能产生伤害时的头顶文字信息等处理
		if damage > 0:
			if ( damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
				# 致命伤害
				ECenter.fireEvent( "EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE", self.id, str( damage ) )
			else:
				# 普通伤害
				ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( damage ) )
			# 格挡动作
			if ( damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
				if self.canPlayEffectAction():
					self.playActions( [resistActionName] )

		else:
			# 闪避动作，骑宠上不播放此动作
			if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
				if self.canPlayEffectAction():
					self.playActions( [dodgeActionName] )


		# 技能产生伤害时的系统信息等处理
		receiverName = self.getName()
		if player.onFengQi:
			receiverName = lbs_ChatFacade.masked
		if casterID == player.id:					# 自己是施法者
			if damage > 0:
				if ( damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s招架了你的%s，受到%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_FROM_SKILL, receiverName, sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# 你的%s暴击对%s造成%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_TO, sk.getName(), receiverName, damage )
				else:
					if (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
						if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:
							# %s受到你反弹的%i点法术伤害。
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC_TO, receiverName, damage )
						else:
							# %s受到你反弹的%i点伤害。
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_PHY_TO, receiverName, damage )
					else:
						# 你的%s对%s造成了%i的伤害。
						player.statusMessage( csstatus.SKILL_SPELL_DAMAGE_TO, sk.getName(), receiverName, damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s闪躲了你的%s。
					player.statusMessage( csstatus.SKILL_SPELL_DODGE_FROM_SKILL, receiverName, sk.getName() )
		elif casterID == petID: 					# 宠物是施法者
			if damage > 0:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s招架了你的宠物的%s，受到%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_PET_RESIST_HIT_FROM_SKILL, receiverName, pet.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# 宠物的%s暴击对%s造成%i点的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_PET_DOUBLEDAMAGE_TO, pet.getName(), sk.getName(), receiverName, damage )
				elif (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
					if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:

						# 反震效果触发，对敌人造成%i点法术伤害。
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_MAGIC_TO, damage )
					else:

						# 反震效果触发，对敌人造成%i点伤害。
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_PHY_TO, damage )
				else:
					# 宠物的%s对%s造成了%i的伤害。
					player.statusMessage( csstatus.SKILL_SPELL_PET_DAMAGE_TO, pet.getName(), sk.getName(), receiverName, damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s闪躲了宠物的%s。
					player.statusMessage( csstatus.SKILL_SPELL_PET_DODGE_TO, receiverName, pet.getName(), sk.getName() )

	def showTargetAttribute( self, targetID ):
		"""
		显示对方玩家的信息(观察功能)
		@param   targetID: 对方玩家的ID
		@type    targetID: OBJECT_ID
		"""
		pass

	def showTargetEquip(self ,items , indexs):
		"""
		显示对方玩家的装备(观察功能)
		@param   items: 对方玩家的部分信息
		@type    items: LIST
		@param   targetID: 对方玩家的ID
		@type    targetID: OBJECT_ID
		"""
		pass


	def startRacehorse( self ):
		"""
		"""
		INFO_MSG( "receive racehorse " )


	def startTongRacehorse( self ):
		"""
		"""
		INFO_MSG( "receive tong racehorse !" )

	def onCasketResult( self, anim ):
		"""
		玩家接收从cell发来的神机匣子成功/失败的消息
		anim 0x01:		播放成功
			 0x02:		播放失败
			 0x04:		播放烟花(已废弃)
		"""
		# 由于目前效果较差，暂时屏蔽
		if anim & 1:
			ECenter.fireEvent( "EVT_ON_PLAY_SUCCEED" )
		elif anim & 2:
			ECenter.fireEvent( "EVT_ON_PLAY_FAILED" )
#		elif anim & 4:
#			ECenter.fireEvent( "EVT_ON_PLAY_FIREWORDKS" )
		elif anim & 8:
			ECenter.fireEvent( "EVT_ON_CASKET_CRYSTEQUIP_REMOVE" )

	def showGodWeaponMaker( self ):
		"""
		define method
		显示神器炼制界面
		"""
		pass

	def onEquipGodWeapon( self ):
		"""
		define method
		神器练成成功
		"""
		pass

	def showSkillName( self, skillID ):
		"""
		显示技能名称
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SKILL_NAME", self.id, skillID )	#显示释放技能的名称

	def onTalismanLvUp( self ):
		"""
		当法宝升级时调用
		"""
		pass

	def onRebuildAttrCB( self, grade, index, key ):
		"""
		define
		法宝属性改造成功，服务器端回调
		"""
		pass

	def onActivatyAttrCB( self, grade, index ):
		"""
		define
		法宝属性激活成功，服务器端回调
		"""
		pass

	def onTalismanSkillLvUp( self ):
		"""
		当法宝技能升级时调用
		"""
		pass

	def startCopyTime( self, time ):
		"""
		开始副本倒计时
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ENTER_COPY", time > 0 )
		ECenter.fireEvent( "EVT_ON_COPY_TIME_CHANGE", time )

	def endCopyTime( self ):
		"""
		结束副本倒计时
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_LEVEL_COPY" )

	def set_flags( self, old ):
		"""
		玩家标记改变，目前标记的作用是看玩家应该显示哪一种特殊标记
		例如，当玩家有flag 0的时候表示玩家头上要显示“跑商玩家”
		      当玩家有flag 1的时候表示玩家头上要显示“携带带血商品”
		显示方式改变：已经由显示文字修改为显示图标标记		modify by gjx 2009-4-3
		"""
		RoleRelation.set_flags( self, old )
		hasFlyFlag = self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )
		flag = 1 << csdefine.ROLE_FLAG_FLY_TELEPORT
		oldHasFlyFlag = ( old & flag == flag )
		# 新增ROLE_FLAG_FLY_TELEPORT标志
		if hasFlyFlag and not oldHasFlyFlag:
			#self.createFlyModel()
			self.cell.withdrawEidolonBeforeBuff()

		# 移除ROLE_FLAG_FLY_TELEPORT标志
		if not hasFlyFlag and oldHasFlyFlag:
			#self.onTeleportVehicleModeEnd()
			if hasattr( self, "resetCamera" ):
				self.resetCamera()
			self.cell.conjureEidolonAfterBuff()

		hasFlyFlag = self.hasFlag( csdefine.ROLE_FLAG_FLY )
		flag = 1 << csdefine.ROLE_FLAG_FLY
		oldHasFlyFlag = ( old & flag == flag )

		# 新增ROLE_FLAG_FLY标志
		if hasFlyFlag and not oldHasFlyFlag:
			self.cell.withdrawEidolonBeforeBuff()

		# 移除ROLE_FLAG_FLY标志
		if not hasFlyFlag and oldHasFlyFlag:
			self.cell.conjureEidolonAfterBuff()

		self.updateRoleSign( old, csdefine.ROLE_FLAG_MERCHANT, "merchant" )		# 更新跑商标记
		self.updateRoleSign( old, csdefine.ROLE_FLAG_BLOODY_ITEM, "bloodyItem" )# 更新携带滴血物品标记
		#self.updateRoleSign( old, csdefine.ROLE_FLAG_ROBBING, "pillage" )		# 更新劫镖任务标记
		self.updateRoleSign( old, csdefine.ROLE_FLAG_CAPTAIN, "captain" )		# 更新队长标记
		self.updateRoleSign( old, csdefine.ROLE_FLAG_TEAMMING, "teammate" )		# 更新非队长队员标记
		self.updateRoleSign( old, csdefine.ROLE_FLAG_CP_ROBBING, "pillage" )	# 更新劫镖任务标记
		self.updateRoleSign( old, csdefine.ROLE_FLAG_XL_ROBBING, "pillage" )	# 更新劫镖任务标记
		self.updateRoleSign( old, csdefine.ROLE_FLAG_CITY_WAR_FUNGUS, "cityWarer" )	# 城战蘑菇标记

		if self.isPlayer() :
			ECenter.fireEvent( "EVT_ON_ROLE_FLAGS_CHANGED", old )

		if self.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
			self.set_hideInfoFlag( True )

		self.set_pkState()

		hasTeamCompetitionFlag = self.hasFlag( csdefine.ROLE_FLAG_SPEC_COMPETETE )
		flag = 1 << csdefine.ROLE_FLAG_SPEC_COMPETETE
		oldHasFlyFlag = ( old & flag == flag )
		if hasTeamCompetitionFlag:
			self.onTeamCompetitionStart()

		hasSafeFlag = self.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA )
		BigWorld.callback( 1.0, Functor( self.set_safeAreaFlag, hasSafeFlag ) )

	def set_hideInfoFlag( self, value ):
		"""
		是否隐藏玩家信息
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_HAS_HIDEINFO_FLAG", self, value )

	def set_safeAreaFlag( self, value ):
		"""
		是否有安全区保护标识
		"""
		if self.isPlayer():														#如果是玩家自己，强制刷新周围其他玩家的血条
			roles = self.entitiesInRange( csconst.ROLE_AOI_RADIUS, cnd = lambda ent : ent.getEntityType() == csdefine.ENTITY_TYPE_ROLE and ent.id != self.id )
			for role in roles:
				ECenter.fireEvent( "EVT_ON_ROLE_HAS_SAFEAREA_FLAG", role, value )
		else:
			ECenter.fireEvent( "EVT_ON_ROLE_HAS_SAFEAREA_FLAG", self, value )

	def set_actWord( self, old ):
		"""
		玩家actWord改变通知
		"""
		CombatUnit.set_actWord( self, old )
		if old != self.actWord:
			ECenter.fireEvent( "EVT_ON_ROLE_ACTWORD_CHANGED", self, old, self.actWord )

	def queryActivityScheme( self ):
		"""
		查询一个活动的数据
		"""
		self.base.queryActivityScheme( self.queryActivitySchemeIndex )


	def onAddScheme( self, activityName, isStart, des, cmd, condition, area, activityType, line, star, persist  ):
		"""
		define method
		"""
		ActivitySchedule.g_activitySchedule.add( activityName, isStart, des, cmd, condition, area, activityType, line, star, persist  )

	def onOneActivityDataSendOver( self ):
		"""
		一个活动数据完毕
		"""
		self.queryActivitySchemeIndex += 1
		self.queryASTimerID = BigWorld.callback( 0.1, self.queryActivityScheme )

	def onActivityDataSendOver( self ):
		"""
		define method
		"""
		self.queryASTimerID = 0
		ActivitySchedule.g_activitySchedule.start()
		ECenter.fireEvent( "EVT_ON_ENABLE_ACTIVITY_BUTTON" )

	def onSaveDoubleExpBuff( self ):
		"""
		define method.
		保存双倍奖励BUFF
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().cell.onSaveDoubleExpBuff()
		# "是否花费1金币来保存奖励时间？"
		showMessage( mbmsgs[0x0122] ,"", MB_OK_CANCEL, query )

	def saveDanceBuff( self ):
		"""
		define method.
		保存跳舞BUFF
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().cell.saveDanceBuff()
		# "冻结的劲舞时间无法保持到下一天，请问您是否确认冻结。"
		showMessage( mbmsgs[0x0123],"", MB_OK_CANCEL, query )

	def onTeleportVehicleModeActionChanged( self, actionName ):
		"""
		define method.
		飞翔传送模式动作改变
		"""
		if not self.inWorld: return
		if self.model is None: return
		if not self.model.inWorld: return

		if actionName == "run":
			[ rds.actionMgr.stopAction( self.model, name ) for name in self.model.queue ]
		else:
			rds.actionMgr.playAction( self.model, actionName )

	def onTeleportVehicleModeEnd( self ):
		"""
		飞翔传送模式结束
		"""
		rModel = getattr( self.model, Const.TELEPORT_HIP, None )
		rds.effectMgr.detachObject( self.model, Const.TELEPORT_HP, rModel )

		if rModel is None:
			self.createEquipModel()
		else:
			self.setModel( rModel )

		rds.effectMgr.createParticleBG( rModel, Const.TELEPORT_VEHICLE_HP, Const.TELEPORT_VEHICLE_PARTICLE, detachTime = 2.0, type = self.getParticleType() )

	def onOpenCopySpaceInterface( self, shownDetails ):
		"""
		define method
		"""
		#打开副本界面
		BigWorld.cancelCallback( self.copySpaceTimerID )
		spaceType = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY )
		if int( spaceType ) in csconst.HAVE_SPACE_COPY_INTERFACE:
			ECenter.fireEvent( "EVT_ON_OPEN_COPY_INTERFACE" )
			functor = Functor( self.updateCopySpaceInfo, shownDetails )
			self.copySpaceTimerID = BigWorld.callback( 10.0, functor )

	def onCloseCopySpaceInterface( self ):
		"""
		define method
		"""
		#关闭副本界面
		self.spaceSkillList = []
		self.spaceSkillInitCompleted = False
		self.spaceSkillSpaceType = -1

		ECenter.fireEvent( "EVT_ON_CLOSE_COPY_INTERFACE" )
		if self.copySpaceTimerID != 0:
			BigWorld.cancelCallback( self.copySpaceTimerID )

	def updateCopySpaceInfo( self, shownDetails ):
		"""
		shownDetails 副本内容显示规则：
		[
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
			8: 猰貐血量百分比
			11:拯救猰貐当前阶段
			12:下一波怪物开始时间(新版猰貐)
			13:猰貐血量百分比
			14:圆环血条
			15:显示/隐藏环形怒气值（怒气值也是用气血计算的，界面不同）
			16：斋南血量百分比
			17:神魂迷阵boss
			18：斗舞副本中显示的副本的连击数
			19: 斗舞副本每次挑战动作的时间限制
		]
		"""
		try:
			for shownItemNumber in shownDetails:
				if shownItemNumber == 0:
					startTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_START_TIME)			#开始时间
					persistTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME)		#持续时间
					ECenter.fireEvent( "EVT_ON_COPY_TIME_UPDATE", startTime, persistTime )									#剩余时间更新
				elif shownItemNumber == 1:
					monsterNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER)	#剩余小怪
					if monsterNumber != "":
						ECenter.fireEvent( "EVT_ON_COPY_MONSTERS_UPDATE", int( monsterNumber ) )								#小怪更新
				elif shownItemNumber == 2:
					monsterPassel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEVEL)			#剩余小怪批次
					if monsterPassel != "":
						ECenter.fireEvent( "EVT_ON_COPY_PASSEL_UPDATE", monsterPassel )											#小怪批次更新
				elif shownItemNumber == 3:
					bossNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS)		#剩余BOSS
					if bossNumber != "":
						ECenter.fireEvent( "EVT_ON_COPY_BOSS_UPDATE", int( bossNumber ) )										#BOSS更新
				elif shownItemNumber == 4:
					mengmengNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_MENGMENG)		#剩余蒙蒙数量
					ECenter.fireEvent( "EVT_ON_COPY_MENGMENG_UPDATE", int( mengmengNumber ) )								#蒙蒙数量更新
				elif shownItemNumber == 5:
					mowenhuNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_MOWENHU)		#剩余魔纹虎数量
					ECenter.fireEvent( "EVT_ON_COPY_MOWENHU_UPDATE", int( mowenhuNumber ) )									#魔纹虎数量更新
				elif shownItemNumber == 6:
					guiyingNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_GUIYINGSHI)		#剩余真鬼影狮数量
					ECenter.fireEvent( "EVT_ON_COPY_ZHENGUIYING_UPDATE", int( guiyingNumber ) )								#真鬼影狮数量更新
				elif shownItemNumber == 7:
					nextTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME)		#下一波怪物开始时间
					if nextTime != "":
						ECenter.fireEvent( "EVT_ON_COPY_NEXT_LEVEL_TIME", nextTime )
				elif shownItemNumber == 8:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_YAYU_HP_PRECENT )		#猰貐血量百分比
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_YAYU_HP_PRECENT", hpp )
				elif shownItemNumber == csconst.SPACE_SPACEDATA_TREE_HP_PRECENT:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_TREE_HP_PRECENT )		#神树血量百分比
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_TREE_HP_PRECENT", hpp )
				elif shownItemNumber == 9:
					gate = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_CHALLENGE_GATE )		#华山阵法当前层数
					if gate != "":
						ECenter.fireEvent( "EVT_ON_COPY_CHALLENGE_GATE", gate )
				elif shownItemNumber == 10:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_POTENTIAL_FLAG_HP )	#圣魂旗血量百分比
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_POTENTIAL_FLAG_HP", hpp )
				elif shownItemNumber == 11:
					batch = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_BATCH )				#拯救猰貐当前阶段
					if batch != "":
						ECenter.fireEvent( "EVT_ON_COPY_YAYU_BATCH", batch )
				elif shownItemNumber == 12:
					nextTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME )#下一波怪物开始时间
					if nextTime != "":
						ECenter.fireEvent( "EVT_ON_COPY_NEXT_BATCH_TIME", nextTime )
				elif shownItemNumber == 13:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_YAYU_NEW_HP )		#猰貐血量百分比
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_YAYU_NEW_HP", hpp )
				elif shownItemNumber == 14:
					ECenter.fireEvent( "EVT_ON_TRIGGER_CIRCLE_HP_BAR", True )										# 显示圆环血条
				elif shownItemNumber == 15:
					isShow = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_ANGER_ISSHOW )
					ECenter.fireEvent( "EVT_ON_TRIGGER_CIRCLE_ANGER_BAR", eval( isShow ) )									# 显示、隐藏环形怒气值
				elif shownItemNumber == 16:
					anger = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_ZHANNAN_ANGER_PERCENT )
					if anger != "":
						ECenter.fireEvent( "EVT_ON_COPY_TREE_ANGER_PRECENT", anger )							# 斋南怒气百分比
				elif shownItemNumber == 17:
					bossNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS )		#剩余BOSS
					totalBossNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_TOTAL_BOSS )	#BOSS总数量
					if bossNumber != "" and totalBossNumber != "":
						ECenter.fireEvent( "EVT_ON_COPY_SHMZ_BOSS_UPDATE", int( bossNumber ), int( totalBossNumber ) )		#BOSS更新
				elif shownItemNumber == 18:
					comoboPoint = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_DANCECOPY_COMOBOPOINT )  #斗舞副本连击
					ECenter.fireEvent("EVT_ON_DANCECOPY_DATA_UPDATE_COMOBOPOINT", int(comoboPoint))
				elif shownItemNumber == 19:
					time = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_DANCECHALLENGE_TIMELIMIT)  #挑战斗舞副本时间限制
					ECenter.fireEvent("EVT_ON_DANCECOPY_DATA_UPDATE_TIMILIMIT", int(time))
				elif shownItemNumber == 20:
					try:
						percent = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_COPY_MMP_YAOQI_PERCENT)  #炼妖壶副本妖气百分比
					except:
						percent = 0
					ECenter.fireEvent("EVT_ON_MMP_YAOQI_PERCENT_CHANGED", float(percent))
				elif shownItemNumber == 21:
					monsterPassel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_WAVE)			#剩余怪物波数
					if monsterPassel != "":
						ECenter.fireEvent( "EVT_ON_COPY_MONSTER_WAVE_UPDATE", monsterPassel )
				elif shownItemNumber == 22:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NPC_HP_PRECENT )				#NPC血量百分比
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_NPC_HP_UPDATE", hpp )
		except:
			pass
		functor = Functor( self.updateCopySpaceInfo, shownDetails )
		self.copySpaceTimerID = BigWorld.callback( 1, functor )

	def startKLJDActivity( self ):
		"""
		打开砸蛋界面
		"""
		pass

	def endKLJDReward( self ):
		"""
		一次砸蛋结束
		"""
		pass

	def startSuperKLJDActivity( self ):
		"""
		打开砸蛋界面
		"""
		pass

	def receiveRequestDance( self, requestEntityID ):
		"""
		接受到邀请共舞
		"""
		pass

	def askSuanGuaZhanBu( self, money ):
		"""
		接受到算卦占卜
		"""
		pass

	def stopRequestDance( self ):
		"""
		取消邀请共舞
		"""
		pass

	def onNPCOwnerFamilyNameChanged( self, npcID, ownerName ):
		"""
		"""
		pass

	def onTeamCompetitionStart( self ):
		"""
		define method
		组队竞赛活动开始
		"""
		ECenter.fireEvent( "EVT_ON_TEAM_COMPETITION_START" )
		self.teamCompetitionTimerID = BigWorld.callback( 2, self.teamCompetitionPointRefresh )
		BigWorld.callback( 2, self.onUpdateRoleNameColor )

	def onUpdateRoleNameColor( self ):
		"""
		更新玩家名字的颜色
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_PK_STATE_CHANGED", self )


	def onEnterTeamCompetitionSpace( self, endTime ):
		"""
		define method
		进入组队竞赛竞技场
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_TEAM_COMPETITION_SPACE", endTime )

	def onLeaveTeamCompetitionSpace( self ):
		"""
		define method
		离开组队竞赛竞技场
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_TEAM_COMPETITION_SPACE" )

	def onTeamCompetitionEnd( self ):
		"""
		define method
		组队竞赛活动结束
		"""
		ECenter.fireEvent( "EVT_ON_TEAM_COMPETITION_END" )
		if hasattr( self, "teamCompetitionTimerID" ) and self.teamCompetitionTimerID != 0:
			BigWorld.cancelCallback( self.teamCompetitionTimerID )


	def teamCompetitionPointRefresh( self ):
		"""
		"""

		self.cell.queryTeamCompetitionInfo()

	def onTeamCompetitionInfo( self, teamID, leaderName, point, place ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TEAM_COMPETITION_POINT", teamID, leaderName, point, place )

	def updataTeamCompetitionInfo( self ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TEAM_COMPETITION_UPDATE" )
		self.teamCompetitionTimerID = BigWorld.callback( 2, self.teamCompetitionPointRefresh )


#----------------这里定义反外挂的空接口---------------------------------------------
	def clientRecvApexMessage( self, strMsg,nLength ):
		"""
		收到反外挂的数据 具体的处理，移到playerRole,这里是空接口
		"""
		None

	def sendApexMessage( self, strMsg,nLength ):
		"""
		发送反外挂的数据
		"""
		None

	def startClientApex( self ):
		"""
		起动客户端的反外挂
		"""
		None

	def alertMessageBox( self, msgContent, msgTitle ):
		"""
		define method.
		从服务器端穿一个消息过来，在客户端弹出一个对话框
		"""
		showMessage( msgContent, msgTitle, MB_OK )



	def disDartEntity( self, vehicleID, seat ):
		"""
		define method
		下镖车专用
		"""
		self.createEquipModel()
		if self.vehicle and self.vehicle.inWorld:
			self.vehicle.onDisMountEntity( self.id, seat )
		else:
			vehicle = BigWorld.entities.get( vehicleID )
			if vehicle and vehicle.inWorld: vehicle.onDisMountEntity( self.id, seat )


	def openTiShouSelect( self ):
		"""
		define method
		打开替售选择界面
		"""
		CommissionSale.instance().show()


	def onReceiveQueryShopInfo( self, roleDBID, roleName, shopName ):
		"""
		defined method
		接收替售店铺查询信息
		"""
		ECenter.fireEvent( "ON_RECEIVE_COMMISSION_SHOP_INFO", roleDBID, roleName, shopName )

	def onReceiveQueryItemInfo( self, roleDBID, itemUID, item, price, roleName, shopName ):
		"""
		define method
		接收替售物品查询信息
		"""
		ECenter.fireEvent( "ON_RECEIVE_COMMISSION_GOODS_INFO", roleDBID, itemUID, item, price, roleName, shopName )

	def onReceiveQueryPetInfo( self, roleDBID, dbid, pet, price, roleName, shopName ):
		"""
		define method
		接收替售宠物查询信息
		"""
		ECenter.fireEvent( "ON_RECEIVE_COMMISSION_PET_INFO", roleDBID, dbid, pet, price, roleName, shopName )

	def removeTSItemFromQueryInterFace( self, uid ):
		"""
		"""
		ECenter.fireEvent( "ON_REMOVE_COMMISSION_GOODS", uid )

	def removeTSPetFromQueryInterFace( self, dbid ):
		"""
		"""
		ECenter.fireEvent( "ON_REMOVE_COMMISSION_PET", dbid )

	def newTSItem( self, item, price, ownerDBID ):
		"""
		define method
		"""
		if self.databaseID == ownerDBID :
			ECenter.fireEvent( "EVT_ON_TISHOU_ITEM_SELLING", item, price )
		else :
			ECenter.fireEvent( "EVT_ON_TISHOU_RECEIVE_ITEMS", item, price, ownerDBID )

	def removeTSItem( self, uid, ownerDBID ):
		"""
		define method
		"""
		if self.databaseID == ownerDBID :
			ECenter.fireEvent( "EVT_ON_TISHOU_ITEM_REMOVE", uid )
		else :
			ECenter.fireEvent( "EVT_ON_TISHOU_ITEM_SELLED", uid )

	def newTSPet( self, pet, price, ownerDBID ):
		"""
		define method
		"""
		if self.databaseID == ownerDBID :
			ECenter.fireEvent( "EVT_ON_TISHOU_PET_SELLING", pet, price )
		else :
			ECenter.fireEvent( "EVT_ON_TISHOU_RECEIVE_PETEPITOME", pet, price, ownerDBID )


	def removeTSPet( self, dbid, ownerDBID ):
		"""
		define method
		"""
		if self.databaseID == ownerDBID :
			ECenter.fireEvent( "EVT_ON_TISHOU_PET_REMOVE", dbid )
		else :
			ECenter.fireEvent( "EVT_ON_TISHOU_PET_SELLED", dbid )


	def updateTSItemPrice( self, uid, price, ownerDBID ):
		"""
		define method
		"""
		if self.databaseID == ownerDBID :
			ECenter.fireEvent( "EVT_ON_TISHOU_ITEM_UPDATE", uid, price )
		else :
			ECenter.fireEvent( "EVT_ON_UPDATE_TISHOU_SELLED_ITEM", uid, price )


	def updateTSPetPrice( self, dbid, price, ownerDBID ):
		"""
		define method
		"""
		if self.databaseID == ownerDBID :
			ECenter.fireEvent( "EVT_ON_TISHOU_PET_UPDATE", dbid, price )
		else :
			ECenter.fireEvent( "EVT_ON_UPDATE_SELLED_PET", dbid, price )

	def moveToTSNPC( self, space, lineNumber, position, direction ):
		"""
		define method
		"""
		if self.getSpaceLabel() != space or BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) != str(lineNumber):
			self.statusMessage( csstatus.TISHOU_NPC_NOT_IN_THIS_SPACE )
			return

		self.moveTo( position )

	def onReceiveTSRecord( self, name, sellName, price, time, amount ):
		"""
		define method
		"""
		records = ( name, sellName, price, time, amount )
		ECenter.fireEvent( "EVT_ON_TISHOU_ADD_SELL_RECORD", records )

	def receiveStatistic( self, statistic ):
		"""
		define method
		"""
		pass

	# --------------------------------------------------
	# 切磋
	# --------------------------------------------------
	def onReceivedQieCuo( self, targetID ):
		"""
		收到切磋邀请
		"""
		pass

	def onRequestQieCuo( self, targetID ):
		"""
		发送切磋邀请成功
		"""
		print "self.id", self.id, BigWorld.player().id, targetID
		target = BigWorld.entities.get( targetID )
		if target is None: return
		self.qieCuoTargetID = targetID
		# 插旗子
		dsVector3 = target.position - self.position
		dtPosition = self.position + ( dsVector3.x/2, dsVector3.y, dsVector3.z/2 )
		#计算碰撞坐标 以免浮在空中
		endDstPos = csarithmetic.getCollidePoint( self.spaceID, dtPosition + (0,10,0), dtPosition + (0,-10,0) )
		func = Functor( self.onQieCuoQiZiModelLoad, endDstPos, targetID )
		rds.effectMgr.createModelBG( [Const.QIECUO_QIZI_MODEL_PATH], func )
		# 播放挑衅动作
		#ECenter.fireEvent( "EVT_END_GOSSIP" ) # 关闭所有窗口
		if self.vehicleModelNum == 0:
			rds.actionMgr.playAction( self.model, Const.MODEL_ACTION_DEFY )

	def onQieCuoEnd( self ):
		"""
		Define Method
		切磋结束
		"""
		self.delQieCuoQiZiModel()

	def onQieCuoQiZiModelLoad( self, dtPosition, targetID, model ):
		"""
		切磋旗子加载完成回调
		"""
		if not self.inWorld: return
		if self.qieCuoTargetID != targetID: return
		if model is None: return
		self.addModel( model )
		self.qieCuoQiZiModel = model
		model.position = dtPosition
		rds.actionMgr.playAction( model, Const.MODEL_ACTION_WJ_STAND )

	def delQieCuoQiZiModel( self ):
		"""
		删除切磋旗帜模型
		"""
		if self.qieCuoQiZiModel:
			if self.qieCuoQiZiModel in list( self.models ):
				self.delModel( self.qieCuoQiZiModel )
			self.qieCuoQiZiModel = None

	def onReceivePointCard( self, pointCard ):
		"""
		"""
		print pointCard.cardNo
		ECenter.fireEvent( "EVT_ON_RECEIVE_POINT_CARD", pointCard )

	def trigerImageVerify( self, imageData, count ):
		"""
		Define method.
		触发图片验证

		@param imageData : 验证图片数据，STRING
		@param count : 第几次验证
		"""
		DEBUG_MSG( "--->>>imageData", count, imageData )

	def onBuyPointCardInterface( self ):
		"""
		define method
		打开购买点卡界面
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_POINT_CARD_BUY_WINDOW" )

	def onSellPointCardInterface( self ):
		"""
		define method
		打开出售点卡界面
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_POINT_CARD_SELL_WINDOW" )

	def onAddPointCard( self, cardInfo ):
		"""
		define method
		新增一个点卡信息
		"""
		print cardInfo


	def removePointCard( self, cardNo ):
		"""
		define method
		移除一个点卡
		"""
		print cardNo
		ECenter.fireEvent( "EVT_ON_REMOVE_POINT_CARD", cardNo )


	def onReceiveCollectionItem( self, collectorDBID, collectionItem ):
		"""
		define method
		"""
		if self.databaseID == collectorDBID :
			ECenter.fireEvent( "EVT_ON_RECEIVE_TISHOU_PURCHASING_ITEM", collectionItem )
		else :
			ECenter.fireEvent( "EVT_ON_RECEIVE_TISHOW_PURCHASED_ITEM", collectionItem )

	def onAddCollectionItem( self, collectionItem ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_TISHOU_PURCHASING_ITEM", collectionItem )

	def onRemoveCollectionItem( self, uid ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_REMOVE_TISHOU_PURCHASING_ITEM", uid )

	def showRollInterface( self, index, item, id ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_ROLL_WINDOW", index, item, id )

	def receiverRollValue( self, index, point, id ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_ROLL_POINT", index, point, id )

	def closeRollInterface( self, index, id ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_CLOSE_ROLL_BOX", index, id )


	def onAddOwnCollectionItem( self, ownCollectionItem ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_VEND_PURCHASING_ITEM", ownCollectionItem )

	def onRemoveOwnCollectionItem( self, uid ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_REMOVE_VEND_PURCHASING_ITEM", uid )


	def onQueryOwnCollectionItem( self, ownCollectionItem, sellerID ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_VEND_PURCHASED_ITEM", ownCollectionItem, sellerID )

	def removeOwnCollectionItemTotal( self, ownCollectionItem ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_VEND_PURCHASE_ITEM_UPDATE", ownCollectionItem )

	def onTongCompetitionStart( self ):
		"""
		define method
		帮会竞技活动开始
		"""
		ECenter.fireEvent( "EVT_ON_TONG_COMPETITION_START" )
		BigWorld.callback( 2, self.onUpdateRoleNameColor )
		self.tongCompetitionTimerID = BigWorld.callback( 2, self.tongCompetitionPointRefresh )

	def tongCompetitionPointRefresh( self ):
		"""
		"""
		self.cell.queryTongCompetitionInfo()

	def onTongCompetitionInfo( self, tongDBID, tongName, point, place ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TONG_COMPETITION_POINT", tongDBID, tongName, point, place )

	def updataTongCompetitionInfo( self ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_TONG_COMPETITION_UPDATE" )
		self.tongCompetitionTimerID = BigWorld.callback( 2, self.tongCompetitionPointRefresh )


	def onEnterFamilyCompetitionSpace( self, endTime ):
		"""
		define method
		进入帮会竞技
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_FAMILY_COMPETITION_SPACE", endTime )

	def onLeaveFamilyCompetitionSpace( self ):
		"""
		define method
		离开帮会竞赛竞技场
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_FAMILY_COMPETITION_SPACE" )


	def onFamilyCompetitionEnd( self ):
		"""
		define method
		帮会竞技结束
		"""
		if hasattr( self, "tongCompetitionTimerID" ) and self.tongCompetitionTimerID != 0:
			BigWorld.cancelCallback( self.tongCompetitionTimerID )


	def onEnterRoleCompetitionSpace( self, endTime ,pkProtectTime):
		"""
		define method
		进入个人竞赛竞技场
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_ROLE_COMPETITION_SPACE", endTime ,pkProtectTime)



	def onLeaveRoleCompetitionSpace( self ):
		"""
		define method
		离开个人竞赛竞技场
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_ROLE_COMPETITION_SPACE" )


	def onRoleCompetitionEnd( self ):
		"""
		define method
		个人竞技结束
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_COMPETITION_END" )
		pass

	def onShowExp2PotWindow( self, objectID ):
		"""
		显示经验换潜能界面
		"""
		pass

	def onUpdateOwnCollectionItem( self, ownCollectionItem ):
		"""
		define method
		更新自己收购的一个物品
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_VEND_PURCHASING_ITEM", ownCollectionItem )

	def onUpdateCollectionItem( self, collectionItem ):
		"""
		define method
		更新自己收购的一个物品
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_TISHOU_PURCHASING_ITEM", collectionItem )

	def onClearCollectionTable( self, collectorDBID ):
		"""
		define method
		清空收购表格
		"""
		if self.databaseID == collectorDBID :
			ECenter.fireEvent( "EVT_ON_TS_PURCHASING_ITEM_CLEAR" )
		else :
			ECenter.fireEvent( "EVT_ON_TS_PURCHASED_ITEM_CLEAR" )

	def onAFLimitTimeChanged( self, af_time_limit ):
		"""
		define method
		离开自动战斗状态回调
		"""
		pass

	def onAFLimitTimeExtraChanged( self, af_time_extra ):
		"""
		define method
		离开自动战斗时间回调2
		"""
		pass

	def openFeichengwuraoInterface( self ):
		"""
		打开非诚勿扰公告界面
		define method
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_BULLETIN_SHOW" )

	def receiveLoveMsgs( self, msgInstance ):
		"""
		define method
		"""
		#msgs = getattr( self, "fcwrMsgs", {} )
		#msgs[msgInstance.index] = msgInstance
		#setattr( self, "fcwrMsgs", msgs )
		ECenter.fireEvent( "EVT_ON_RECIEVE_LOVE_MSG", msgInstance )

	def receiveLoveMsgsResult( self, results ):
		"""
		define method
		"""
		self.fcwrResult = results
		ECenter.fireEvent( "EVT_ON_RECIEVE_REWARDS_RESULTS", results )

	def onVoteLoveMsgSuccessful( self, msgInstance ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_VOTE_LOVEMSG_SUCC", msgInstance )

		self.successfulVoteMsg = msgInstance

	def onSendLoveMsgSucc( self ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_SEND_LOVEMSG_SUCC" )

	def enterEquipUp( self, npcId ): # just a stub here
		"""
		装备品质飞升
		"""
		ECenter.fireEvent( "EVT_ON_RAISE_EQUIP_QUALITY", npcId )

	def enterEquipAttrRebuild( self, npcId ) :
		"""
		装备属性重铸
		"""
		ECenter.fireEvent( "EVT_ON_EQUIP_ATTR_REBUILD", npcId )

	def shakeCamera( self, duration, shakeCenter ):
		"""
		define method
		"""
		rds.effectMgr.cameraShake( duration, ( 0.1, 0.0, 0.1 ), shakeCenter )

	def onBuffQuestionStart( self, quetionItem ):
		"""
		"""
		ECenter.fireEvent( "EVT_ON_RABBIT_QUESTION_RECEIVE", quetionItem )

	def onBuffQuestionEnd( self ):
		"""
		"""
		ECenter.fireEvent( "EVT_ON_RABBIT_QUESTION_END" )

	def unfoldScroll( self, npcID, sceneId ):
		"""
		10级副本中展开画卷
		"""
		ECenter.fireEvent( "EVT_ON_DISPLAY_SCENE", sceneId )

	def onCameraFly( self, graphID, startPos ):
		"""
		Define Method
		摄像头飞行
		"""
		pass

	def interruptAttackByServer( self, reason ):
		"""
		define method
		server 通知打断攻击行为
		"""
		pass

#-------------------------飞行骑宠相关的检测Start by mushuang-------------------------#
	def enableFlyingRelatedDetection( self, spBoundingBoxMin, spBoundingBoxMax ):
		"""
		defined method
		@enableFlyingRelatedDetection: 开启和飞行有关的检测
		@spBoundingBoxMin: 空间外接盒的一个对角顶点
		@spBoundingBoxMax: 和spBoundingBoxMin相对的另一个对角顶点
		"""
		pass

	def disableFlyingRelatedDetection( self ):
		"""
		defined method
		@disableFlyingRelatedDetection: 关闭和飞行有关的检测
		"""
		pass
#-------------------------飞行骑宠相关的检测End by mushuang-------------------------#

	def visibleRootUIs( self, visible ) :
		"""
		define method
		服务器通知显示/隐藏当前界面
		@param		visible : 显示/隐藏标记
		@type		visible : bool
		"""
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", visible )

	def unifyYaw( self ):
		"""
		将$p.yaw和dcursor().yaw统一化，用于防止诸如Entity.teleport()中direction假失效的问题。

		通常，通过Entity.teleport()传送时，会有一个direction参数被传入用于表示玩家传送之后的方向。
		但是，如果直接teleport(),比如：cell上player.teleport( None, somePosition, ( 0, 0 ,yaw ) ),
		在客户端会发现玩家被传送后的方向仍然没有改变，即保持了原来的朝向，看上去好像yaw参数没有起作用。
		产生这个问题的原因是BW本身有个属性叫dcursor（通过BigWorld.dcursor()获取），dcursor.yaw会定时自
		动更新$p.yaw，事实上，player.teleport( None, somePosition, ( 0, 0 ,yaw ) )这个调用的确改变了$p.yaw,
		而dcursor在随后的tick中将自己的yaw值写回了$p.yaw，因而造成了yaw参数假失效的现象。

		建议在cell上所有teleport()调用之后调用此接口，以防出现上述问题。 by mushuang
		"""
		BigWorld.dcursor().yaw = BigWorld.player().yaw

	def changeWorldCamHandler( self, camControlType, yaw = -9.4, pitch = 3.766 ):
		"""
		Define method.
		更换摄像机控制方式
		"""
		rds.worldCamHandler = Const.g_worldCamHandlers[camControlType]
		if camControlType == csdefine.NORMAL_WORLD_CAM_HANDLER:
			rds.worldCamHandler.use()
		else:
			rds.worldCamHandler.use( yaw, pitch )

	def enterYXLMChangeCamera( self ):
		"""
		进出英雄联盟副本改变镜头
		"""
		if "ying_xiong_lian_meng_01" == BigWorld.getSpaceName( self.spaceID ):
			self.changeWorldCamHandler( 2, 3, 4 ) # 固定镜头,yaw为3,pitch为4

	def levelYXLMChangeCamera( self ):
		"""
		离开英雄联盟副本镜头恢复
		"""
		self.changeWorldCamHandler( 1 )

	def setFogDistance( self, fogFarScale, fogNearScale ):
		"""
		Define method
		设置雾化值
		"""
		csol.setChunkModelLodMaxDistance( fogFarScale, fogNearScale )

	def setFarPlane( self, farPlane ):
		"""
		Define method
		设置远裁剪面
		"""
		BigWorld.setGraphicsSetting( "FAR_PLANE", farPlane )

	def switchFlyWater( self, switch ):
		"""
		身轻如燕开关
		"""
		pass

	def set_onWaterArea( self, oldValue ):
		"""
		"""
		self.setArmCaps()

	def onSwtichWaterParticle( self, actionName ):
		"""
		触发水面移动效果
		"""
		if not self.onWaterArea: return
		if actionName in ( Const.MODEL_ACTION_WATER_RUN, Const.MODEL_ACTION_WATER_RUN_DAN, Const.MODEL_ACTION_WATER_RUN_SHUANG, Const.MODEL_ACTION_WATER_RUN_FU, Const.MODEL_ACTION_WATER_RUN_CHANG ):
			if not self.flyWaterTimerID:
				self.startFlyWaterParticle()
		else:
			self.stopFlyWaterParticle()

		if actionName in [ Const.MODEL_ACTION_WATER_JUMP_BEGIN1, Const.MODEL_ACTION_WATER_JUMP_BEGIN2, Const.MODEL_ACTION_WATER_JUMP_BEGIN3 ]:
			self.switchFlyWaterParticle()

	def switchFlyWaterParticle( self ):
		"""
		触发水面移动效果
		"""
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.JUMP_WATER_EFFECTID, self.model, self.model, type, type )
		if effect is None: return
		effect.start()

	def startFlyWaterParticle( self ):
		"""
		开始水面粒子效果
		"""
		if not self.inWorld: return
		if not self.onWaterArea: return
		self.switchFlyWaterParticle()
		self.flyWaterTimerID = BigWorld.callback( Const.JUMP_WATER_EFFECT_TIME, self.startFlyWaterParticle )
		#凌波微步水上音效开启
		rds.soundMgr.playVocality( Const.WATER_FLY_SOUND, self.getModel() )

	def stopFlyWaterParticle( self ):
		"""
		关闭水面粒子效果
		"""
		if not self.inWorld: return
		BigWorld.cancelCallback( self.flyWaterTimerID )
		self.flyWaterTimerID = 0
		#凌波微步水上音效关闭
		rds.soundMgr.stopVocality( Const.WATER_FLY_SOUND, self.getModel() )

	def onLeaveWaterCallback( self, volumeID ):
		"""
		"""
		pass

	# ---------------------------------------------------------
	def showCastIndicator( self, idtId ) :
		"""
		Define method
		@param   idtId: 技能/道具操作提示的ID列表
		@type    idtId: ARRAY of UINT16
		"""
		rds.castIndicator.indicateCast( idtId )

	def hideCastIndicator( self, idtId ) :
		"""
		Define method
		@param   idtId: 技能/道具操作提示的ID
		@type    idtId: ARRAY of UINT16
		"""
		rds.castIndicator.shutIndication( idtId )

	#--------------------------------------------------------------
	# 随机任务陷阱相关
	# -------------------------------------------------------------
	def showQuestTrapTip( self, entityID ):
		"""
		Define method
		@param	entityID:	陷阱的ID
		@type	entityID：	OBJECT_ID
		"""
		ECenter.fireEvent( "EVT_ON_TRAP_QUEST_TIP_SHOW", entityID )

	def hideQuestTrapTip( self, entityID ):
		"""
		Define method
		@param	entityID:	陷阱的ID
		@type	entityID：	OBJECT_ID
		"""
		ECenter.fireEvent( "EVT_ON_TRAP_QUEST_TIP_HIDE", entityID )


	def playVideo( self, fileName ):
		"""
		Define method
		@param	fileName:	视频文件
		@type	fileName：	string
		"""
		self.playingVideo = True
		csol.prepareVideo("videos/" + fileName )
		csol.playVideo()
		csol.setVideoCallback( self.onVideoEvent )

	def playSound( self, fileName, typeID, id, priority ):
		"""
		Define method add by wuxo 2012-1-17
		@param	fileName:	音频文件路径
		@type	fileName：	string
		@param	typeID:	        类型 2D/3D
		@type	fileName：	UINT
		@param	NPCID:	        NPC的id
		@type	fileName：	UINT
		"""
		pass

	def playSoundFromGender( self, fileName, id, flag ):
		"""
		Define method
		根据职业的不同，在玩家的客户端播放不同路径的音效
		"""
		pass

	def clearVideo( self ):
		"""
		"""
		csol.clearVideo()

	def onVideoEvent( self, event ):
		if event == "ON_COMPLETE":
			self.playingVideo = False
			#视频播放结束需要中断BUFFER
			self.cell.onCompleteVideo() #add by wuxo 2011-11-26
			BigWorld.callback( 0.1, self.clearVideo )

	def setCameraFlyState(self,eventIDs):
		"""
		设置CameraFly的陷阱状态by wuxo 2011-11-26
		"""
		str_eventIDList = eventIDs.split(";")
		eventIDList  = []
		for i in str_eventIDList:
			eventIDList.append(eval(i))
		for e in BigWorld.entities.values():
			if e.__class__.__name__ == "CameraFly" and e.eventID in eventIDList:
				e.setTrapState(True)


	def initMatchRecord( self, matchType, param1, param2 ):
		"""
		Define method.
		初始化玩家的比赛日志信息，相关定义见csdefine.MATCH_TYPE_***

		比赛类型UINT8：matchType

		个人竞技，组队竞技，帮会竞技：
		上次参赛获得积分INT32：param1
		累计参赛获得积分INT32：param2

		武道大会，组队擂台，帮会擂台:
		上次参赛获得名次INT32：param1
		获得最好参赛名次INT32：param2
		"""
		DEBUG_MSG( "match info:", matchType, param1, param2 )
		ECenter.fireEvent( "EVT_ON_INIITE_MATCH_RECORD", matchType, param1, param2 )

	def updateMatchRecord( self, matchType, param ):
		"""
		Define method.
		更新玩家的比赛日志信息，仅更新最新数据，客户端需置一查询标记，如果客户端没有查询过相关数据，那么再次打开界面时需要向服务器查询。
		如果客户端已经有总积分或者历史最好名次数据，那显示计算后的数据即可。

		比赛类型UINT8：matchType,相关定义见csdefine.MATCH_TYPE_***

		个人竞技，组队竞技，帮会竞技：
		上次参赛获得积分INT32：param

		武道大会，组队擂台，帮会擂台:
		上次参赛获得名次INT32：param
		"""
		DEBUG_MSG( "match info:", matchType, param )
		ECenter.fireEvent( "EVT_ON_UPDATE_MATCH_RECORD", matchType, param )

	def isGMWatcher( self ) :
		"""
		是否处于GM观察者状态
		"""
		return self.effect_state & csdefine.EFFECT_STATE_WATCHER != 0

	def isDeadWatcher( self ) :
		"""
		是否处于死亡观察者状态
		"""
		return self.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER != 0

	def updateSkill( self, floder, skillID ):
		"""
		define method
		更新客户端技能（主要是支持技能的边测边配的工作方式）
		"""
		Skill_test.updateSkill( floder, skillID )

	def updateItem( self, floder, ItemID ):
		"""
		define method
		更新客户端技能（主要是支持技能的边测边配的工作方式）
		"""
		Item_test.updateItem( floder, ItemID )

	def lineToPoint( self, position, speed ):
		"""
		移动到坐标点
		"""
		pass

	def doRandomRun( self, centerPos, radius ):
		"""
		define method
		走到centerPos为原点，radius为半径的随机采样点
		"""
		pass

	def infoTongMember( self, lineNumber, casterName, showMessage, spaceName, position, direction ):
		"""
		define method.
		如果是多个人都发来传送信息，按排队规则，等前一个消失才会弹出第二个传送提示框，而同
		一被召唤者只会出现一个提示框，如接受任意一个召唤，则其他召唤取消
		"""
		SpaceName = csconst.g_maps_info[ spaceName ]
		def query( rs_id ):
			if rs_id == RS_YES:
				BigWorld.player().cell.infoTongMemberFly( lineNumber, spaceName, position, direction )

		if showMessage == 1:
			showAutoHideMessage( 60.0, mbmsgs[ 0x0128 ] % ( casterName, SpaceName ), "", MB_YES_NO, query )
			return
		if showMessage == 2:
			showAutoHideMessage( 60.0, mbmsgs[ 0x0129 ] % ( casterName ), "", MB_YES_NO, query )
			return

	def getParticleType( self ):
		"""
		实时返回粒子创建类型
		"""
		player = BigWorld.player()
		if player is None:
			return Define.TYPE_PARTICLE_OP

		if player.targetEntity == self:
			return Define.TYPE_PARTICLE_PIOP

		return Define.TYPE_PARTICLE_OP

	# ----------------------------------------------------------------------------------
	# 英雄联盟副本界面相关
	# ----------------------------------------------------------------------------------
	def onShowYXLMCopyNPCSign( self, copySpaceLabel ):
		"""
		define method
		英雄联盟副本打开NPC位置显示界面
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_YXLMCOPY_MINIMAP", copySpaceLabel )

	def onCloseYXLMCopyNPCSign( self ):
		"""
		define method
		英雄联盟副本关闭NPC位置显示界面
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_YXLMCOPY_MINIMAP" )

	def onShowYXLMCopyBossSign( self, id, className, spawnPos, relation, signType ):
		"""
		define method
		boss、基地、防御塔创建时显示标记
		"""
		ECenter.fireEvent( "EVT_ON_SET_YXLMCOPY_BOSS_SPAWN_SIGN", id, className, spawnPos, relation, signType )

	def onUpdateYXLMCopyBossPos( self, id, className, pos, relation ):
		"""
		define method
		更新Boss位置信息
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_YXLMCOPY_BOSS_SIGN", id, className, pos, relation )

	def onYXLMCopyBossDied( self, id, className, spawnPos, diedPos, relation ):
		"""
		boss、基地、防御塔 死亡时更新标记
		"""
		ECenter.fireEvent( "EVT_ON_SET_YXLMCOPY_BOSS_DIED_SIGN", id, className, spawnPos, diedPos, relation )

	def onYXLMMonsterGetDamage( self, id, seconds ):
		"""
		防御塔或基地受到一定程度伤害时调用
		"""
		ECenter.fireEvent( "EVT_ON_MONSTER_GET_DAMAGE", id, seconds )

	def baoZangOnReceiveEnemyPos( self, enemyId, pos ):
		"""
		define method
		接收队友发来的敌人位置信息
		"""
		ECenter.fireEvent( "EVT_ON_PVP_ON_RECEIVE_ENEMY_POS", enemyId, pos )

	def baoZangOnDisPoseEnemy( self, enemyId ):
		"""
		define method
		删除敌人标记
		"""
		ECenter.fireEvent( "EVT_ON_PVP_ON_DISPOSE_ENEMY_SIGN", enemyId )

	def onPKListChange( self, pkTargetList, id ):
		"""
		define method
		PK列表发生改变
		"""
		pass

	def set_sysPKMode( self, oldValue ):
		"""
		系统默认PK模式
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_SYSPKMODE_CHANGED", self, self.sysPKMode )

	def set_pkMode( self, oldValue ):
		"""
		pk模式改变
		"""
		self.refurbishHPColor()

	def refurbishHPColor( self ):
		"""
		刷新头顶血条颜色
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_PKMODE_CHANGED", self, self.pkMode )

	def canPkPlayer( self ):
		"""
		判断role是否可以PK playerRole
		"""
		player = BigWorld.player()
		if self.id == player.id:return False
		# 不在同一地图不能PK
		if self.spaceID != player.spaceID:
			return False

		# 角色所在地图是否允许pk
		if self.getCanNotPkArea(): return False

		# 如果处于飞行状态，则不允许pk
		if isFlying( self ): return False

		# 30级玩家保护
		if self.pkState == csdefine.PK_STATE_PROTECT: return False

		# 队伍成员不能PK
		if self.isTeamMember( player.id ):
			return False

		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and not player.actionSign( csdefine.ACTION_FORBID_PK ):
			if player.inDamageList( self ) or player.pkTargetList.has_key( self.id ):
				return True

		# 30级对方玩家禁止pk
		if player.pkState == csdefine.PK_STATE_PROTECT:
			return False


		if self.sysPKMode:
			# 如果我的pk模式是系统和平模式
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_PEACE:
				return False


			# 帮战副本中帮会成员不能PK
			if self.tong_dbID != 0 and ( self.tong_dbID == player.tong_dbID ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG:
				return False

			# 阵营战副本中阵营成员不能PK
			if self.getCamp() != 0 and ( self.getCamp() == player.getCamp() ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP:
				return False

			if self.id in player.teamMember and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TEAMMATE:
				return False

			# 系统模式为联盟模式
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_LEAGUE:
				if self.checkCityWarTongBelong( self.tong_dbID, player.tong_dbID ):
					return False
		else:
			# 如果我的pk模式是善意模式（原善恶模式）并且entity不是黄红名
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_RIGHTFUL and player.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ]:
				return False

			# 如果我的pk模式是正义模式并且entity不是黄红名
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_JUSTICE and player.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ] \
				and self.getCamp() == player.getCamp():
				return False


		# 对方在组队跟随状态下可攻击
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and player.isFollowing():
			return True

		# 如果我被禁止PK或者我要pk的entity被禁止pk（例如某方在安全区）
		if self.actionSign( csdefine.ACTION_FORBID_PK ) or player.actionSign( csdefine.ACTION_FORBID_PK ):
			return False
		return True

	def getCanNotPkArea( self ) :
		"""
		所在地图是否允许pk
		"""
		try :
			canNotPkArea = int( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_CANNOTPK ) )
			if canNotPkArea == 1 :
				return True
			else :
				return False
		except :
			return False

	def currAreaCanPk( self ) :
		"""
		检查当前区域是否允许PK，这里是针对区域进行检查，
		不代表玩家之间的关系
		"""
		# 该角色所在地图是否允许pk
		if self.getCanNotPkArea(): return False

		# 当前是否处于免战状态
		if self.effect_state & csdefine.EFFECT_STATE_NO_FIGHT :
			return False

		return True

	def onUpdateIntensifyItem( self, uid ):
		"""
		define method
		强化物品发生改变
		"""
		pass

	def onOpenSpaceTowerInterface( self ):
		"""
		define method
		打开拯救猰貐防御塔界面
		"""
		pass

	def onCloseSpaceTowerInterface( self ):
		"""
		define method
		关闭拯救猰貐防御塔界面
		"""
		pass

	def enterTowerDefenceSpace( self ):
		"""
		define method
		进入塔防副本的副本
		"""
		pass

	def addTowerDefenseSpaceSkill( self, skillID, spaceType ):
		"""
		define method
		增加塔防副本的副本技能
		"""
		pass

	def endTowerDefenseSpaceSkill( self ):
		"""
		define method
		结束塔防副本副本技能
		"""
		pass

	def showHeadPortraitAndText( self, type, monsterName, headTextureID, text, lastTime ):
		"""
		define method
		显示头像和文字
		"""
		pass

	def canChallengeDanceKingCb(self, index, result):
		#1表示可以挑战
		#2表示处于保护时间
		#3表示有人在挑战
		pass


	def addDancingKingInfo(self, index, dancingKingInfo):
		#Define method
		#接收服务器发送的舞王信息，在进入舞厅时，由服务器发送
		#dancingKingInfo = {"modelInfo":playerModelInfo ,"Time":time.time(),"isChallenge":0 }
		pass

	def sendDancingKingInfosOver(self):
		#define method
		pass

	def enterWuTing(self):
		#defined method
		pass
	def leaveWuTing(self):
		#defined method
		pass
	def enterDanceCopy(self, type):
		#defined method
		pass
	def leaveDanceCopy(self, type):
		#defined method
		pass

	def onQueryRoleEquip( self, roleName, raceclass, roleLeve, tongName, roleModel, equips ):
		"""
		define method.
		查询玩家装备返回
		"""
		pass

	def onShowPatrol( self, path, model  ):
		"""
		define method
		显示摆点寻路路径
		"""
		pass

	def planeSpacePrepare( self ):
		"""
		Define method.
		位面传送将要开始。
		"""
		pass



	def canGetDancePositionCb(self, index):
		"""
		define method
		检测位置的回调
		"""
		pass



############################
# End of class Role        #
############################


	#
	# PlayerRole C++ Interface Note:
	# The identifier 'physics' refers to the C++ Python Object Physics. It is a
	# special variable as it is initially set to a specified value to initialise
	# it to a particular physics model.
	#
	# eg. self.physics = STANDARD_PHYSICS will initialise the physics object
	#     for the PlayerRole instance.
	#
	# Any subsequent call can then treat 'physics' as a structure with data
	# members that control physics behaviour.
	#
	# eg. self.physics.collide = true will turn on collision detection for the
	# PlayerRole.
	#
	# The list of physics data members are:
	#     velocity, (X,Y,Z) movement velocity
	#     velocityMouse, Direction|MouseX|MouseY indicating how the mouse
	#         behave velocity.
	#     angularMouse, Direction|MouseX|MouseY indicating how the mouse
	#         affects direction.
	#     angular, a double value indicating current angular velocity.
	#     nudge, the (X,Y,Z) movement value to be moved this frame.
	#     turn, the double value indicating turned amount this frame.
	#     fall, a true or false value indicating if gravity should affect it.
	#     collide, a true or false value indicating if collision detection is
	#              turned on or off for this Role.
	#

"""
-- 2006/10/14 : modified by huangyw roundly
"""
class PlayerRole( Action.Action, Attack, Role, Guide ):
	# 移动模式
	MOVE_WALK			= 1						# 走路
	MOVE_RUN			= 2						# 跑步
	MOVE_FLY			= 3						# 飞行( 暂时没有 )
	INVALIDITY_POS		= Math.Vector3( -100000000, -100000000, -100000000 ) #标志为无效的值

	def onBecomePlayer( self ):
		"""
		当成为角色时被调用
		"""
		INFO_MSG( "PlayerRole::onBecomePlayer!" )
		self.actionState = 0						# 指出玩家当前处于什么状态
		self.c_control_mod = Const.CAMERA_CONTROL_MOD_2	# 设置控制方式

		OPRecorder.__init__( self )
		Action.Action.__init__( self )
		Attack.__init__( self )
		Guide.__init__( self )
		Team.onBecomePlayer( self )
		self.setSelectable( False )						# 设置为不能选择自己

		self.__bindShortcuts()
		self.moveTime = 0.0 #用于眩晕下的移动
		self.isRolesVisible = True					# 其他角色是否可见（hyw--2009.1.10）
		self.isRolesAndUIVisible = True					#其他角色(包括UI)是否可见
		self.isShowSelf = True                                          #是否显示自己
		self.allowInvite = True						# 允许邀请	14:18 2008-6-24 yk
		self.allowTrade  = True						# 允许交易	14:18 2008-6-24 yk
		self.controlForbid = 0						# 玩家控制限制

		self.jumpHeight1  = Const.JUMP_LAND_HEIGHT		# 1段跳高度
		self.jumpHeight2  = Const.JUMP_LAND_HEIGHT2           #2段跳高度
		self.jumpHeight3  = Const.JUMP_LAND_HEIGHT3          #3段跳高度

		self.isJump2 = False            #进行2段跳成功与否标记（dojump设置了就算成功）
		self.isJump3 = False            #进行3段跳成功与否标记（dojump设置了就算成功）
		self.startHeight = 0            #当前跳跃的起跳高度
		self.wasdFlagTime = [ 0, 0, 0, 0 ]              #前进/左移/后退/右移按键按下时的时间
		self.wasdFlag     = [ False,False,False,False ]  #前进/左移/后退/右移按键两次按下引起的迅捷移动标记
		self.key          =  None #上一次的按键
		self.isSameKey    = False #上次按键和本次按键是否相同
		self.isPlayWaterRun = False #是否播放水中动作
		self.jumpTime	= 0.0 						# 这个跳跃过程的时间
		self.geneGravity = Const.JUMP_GENEGRAVITY 						# 重力因子在下落时增加重力

		self.__moveMode = self.MOVE_RUN				# 移动模式( hyw--2008.12.29 )
		self.__jumpCBID = 0
		self.__jumpPos = ( 0, 0, 0 )
		self.__isAssaulting = False					# 是否处于冲锋状态( hyw--09.01.12 )
		self.__expectTarget = ""					# 将要对话的目标的 className

		rds.gameMgr.onBecomePlayer()				# hyw -- 2008.01.20
		self.lotteryItems = {}						# 存储锦囊里面随机出的数据

		self.vehicleDBID = 0						# 记录的骑宠dbid
		self.vehicleDatas = {}						# 记录的骑宠数据
		self.activateVehicleID = 0					# 记录的激活骑宠dbid

		rds.shortcutMgr.setHandler( "OTHER_TOGGLE_ROLES_MODEL", self.__toggleOtherRoles )			# 显示/隐藏其他角色模型
		rds.shortcutMgr.setHandler( "COMBAT_SWITCH_PKMODEL", self.__switchPkMode )					# 切换PK模式

		self.queryActivitySchemeIndex = 0
		self.queryActivityScheme()

		self.statistic = {}
		self.initStatistic()						# 初始化经验、金钱、潜能、帮贡
		self.initMailbox()							# 初始化邮箱

		self.currentShowMessage = None				# 记录当前打开的showMessage
		self.__followCallBack = 0					# 跟随的回调函数
		self.currentItemBoxID = 0					# 当前普通物品的拾取框ID
		self.currentQuestItemBoxID = 0				# 当前任务物品的拾取框ID
		self.onLineTimer = None						# 玩家在线时间的客户端累积计时器
		self.onLineTimeTick = 0.0					# 玩家在线时间的客户端累积触发
		self.benefitTime = 0.0						# 初始化时记录玩家在线时间
		self.__spanSpaceDstLabel = ""				# 保留跨场景寻路的目标场景名
		self.__spanSpaceDstPos = Math.Vector3( self.INVALIDITY_POS ) # 保留跨场景寻路的目标位置
		self.__spanSpaceDataLock = False			# 防止跨场景寻路信息数据不被篡改
		self.__spanSpaceNearby = 0					# 保存跨场景寻路下，移动到目标位置附近的距离
		self.__spanSpaceTarget = ""					# 保存跨场景寻路下的expectTarget
		self.onWaterJumpTimer = None				# 水面跳跃回调

		# 飞行骑宠子模块 by mushuang
		self.__flyingVehicle = FlyingVehicle( self )
		self.onFlyModelLoadFinished = False

		self.oksData = {}	# 一键换装数据

		# 繁体版开启TimeOfDay功能
		if Language.LANG == Language.LANG_BIG5:
			rds.enEffectMgr.start()
		self.spaceSkillList = []				# 空间专属技能id列表，14:35 2010-4-27，wsf
		self.spaceSkillInitCompleted = False	# 空间专属技能是否初始化完毕
		self.spaceSkillSpaceType = -1			# 空间专属技能所在的空间类型

		self.waterVolumeListerID = BigWorld.addWaterVolumeListener( self.matrix, self.enterWaterCallback )

		# 身轻如燕
		self.onWater = False
		self.jumpType = csdefine.JUMP_TYPE_LAND

		# 延迟传送相关
		self.delayTeleportNpc = None
		self.delayTeleportTime = 0
		self.delayTeleportCBID = 0
		self.delayTeleportIsFail = False
		self.isBlowUp = False

		#连击动作Y轴跟随回调
		self.cameraInHomingID = 0
		self.actionCBID = 0 #动作移动限制回调句柄
		self.cameraFollowCBID = 0 #动作镜头跟随回调句柄

		self.homingAction = None #当前正在播放连击动作
		#传送结束后继续进入客户端飞翔传送
		self.continueFlyPath = ""

		self.cfCounter = [ [0] * len( Define.CONTROL_FORBID_ROLE_MOVE_LIST ), [0] * len( Define.CONTROL_FORBID_ROLE_CAMERA_LIST ) ]
		self.changeWorldCamHandler( csdefine.NORMAL_WORLD_CAM_HANDLER )

		BigWorld.setFogTargetMatrix( self.matrix )
		
		self.visibleRules = [csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_SHOW_SELF,\
		 csdefine.VISIBLE_RULE_BY_WATCH, csdefine.VISIBLE_RULE_BY_PROWL_1]

	def addControlForbid( self, stateWord, source ):
		"""
		玩家控制限制计数器加一，并维护玩家控制。
		@param stateWord	:	动作状态字
		@type stateWord		:	integer
		@param source		:	限制来源
		@type source		:	integer
		"""
		for i, act in enumerate( Define.CONTROL_FORBID_ROLE_LIST ):
			if stateWord & act:
				if sum( self.cfCounter[i] ) == 0:
					self.controlForbid |= act
					self.onControlForbidChanged( act, True )
				self.cfCounter[i][source] += 1

	def removeControlForbid( self, stateWord, source ):
		"""
		玩家控制计数器减一，并维护玩家控制。
		@param stateWord	:	动作状态字
		@type stateWord		:	integer
		@param source		:	限制来源
		@type source		:	integer
		"""
		for i, act in enumerate( Define.CONTROL_FORBID_ROLE_LIST ):
			if stateWord & act:
				if self.cfCounter[i][source] >= 1:
					self.cfCounter[i][source] -= 1
					if sum( self.cfCounter[i] ) == 0:
						self.controlForbid &= ~act
						self.onControlForbidChanged( act, False )

	def onControlForbidChanged( self, act, disabled ):
		"""
		玩家控制限制发生改变
		"""
		if disabled and act == Define.CONTROL_FORBID_ROLE_MOVE:
			if self.isMoving():
				self.stopMove()
			self.emptyDirection() #清理按键影响

	def clearControlForbid( self ):
		"""
		清除玩家控制限制
		"""
		self.controlForbid = 0
		self.cfCounter = [ [0] * len( Define.CONTROL_FORBID_ROLE_MOVE_LIST ), [0] * len( Define.CONTROL_FORBID_ROLE_CAMERA_LIST ) ]

	def clearSourceControlForbid( self, stateWord, source ):
		"""
		清除玩家source来源的stateWord控制限制计数
		"""
		for i, act in enumerate( Define.CONTROL_FORBID_ROLE_LIST ):
			if stateWord & act:
				self.cfCounter[i][source] = 0
				if sum( self.cfCounter[i] ) == 0:
					self.controlForbid &= ~act
					self.onControlForbidChanged( act, False )

	def hasControlForbid( self, controlState ):
		"""
		是否有控制限制
		@param controlState : 玩家控制限制 see Define.py CONTROL_FORBID_*
		@type controlState : Uint16
		@return BOOL
		"""
		return self.controlForbid & controlState != 0

	def __switchPkMode( self ):
		"""
		切换pk模式
		"""
		pkModeOrder = [
						csdefine.PK_CONTROL_PROTECT_RIGHTFUL,
						csdefine.PK_CONTROL_PROTECT_JUSTICE,
						csdefine.PK_CONTROL_PROTECT_NONE,
						]
		nextIndex = 0
		if self.pkMode in pkModeOrder:
			nextIndex = pkModeOrder.index( self.pkMode ) + 1
			if nextIndex >= len( pkModeOrder ):
				nextIndex = 0
		self.cell.setPkMode( pkModeOrder[nextIndex] )

	def onBecomeNonPlayer( self ):
		"""
		当脱离角色时被调用
		"""
		self.filter = BigWorld.AvatarFilter()
		# 从 Action.__release__() 移过来的，10:41 2008-6-24 yk
		self.__unbindShortcuts()
		ActivitySchedule.g_activitySchedule.clean()
		rds.enEffectMgr.stop()

	# -------------------------------------------------
	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		return BigWorld.PlayerAvatarFilter()			# we're using a filter tailor-made for us

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		INFO_MSG( "PlayerRole::enterWorld: begin" )
		BigWorld.dcursor().yaw = BigWorld.player().yaw	# 解决新建角色的面向不正确的问题
		rds.worldCamHandler.reset()						# 重设镜头
		self.resetAutoFight()							# 解决老角色的自动战斗开启问题
		Role.onCacheCompleted( self )
		# hyw, notify the cache is completed. about attack
		Attack.onCacheCompleted( self )
		# phw : notify the cache is completed. init Itembag's some property
		ItemsBag.onCacheCompleted( self )
		# phw : notify the cache is completed. init RoleQuestInterface's some property
		RoleQuestInterface.onCacheCompleted( self )
		# hyw : notify the cache is completed. initialize quickbar
		QuickBar.onCacheCompleted( self )
		# hyw : notify the cache is completed. initialize PetCage
		PetCage.onCacheCompleted( self )
		# wsf : notify the cache is completed. initialize RoleGem,10:16 2008-7-31
		RoleGem.onCacheCompleted( self )
		# hyw : notify the cache is completed. chat
		RoleChat.onCacheCompleted( self )
		TDBattleInterface.onCacheCompleted( self )
		RoleJueDiFanJiInterface.onCacheCompleted( self )

		GUIFacade.onRoleEnterWorld( self )					# 通知 Facade
		#self.statusMessage( csstatus.ACCOUNT_STATE_CLIENT_VERSION, love3.versions ) 注掉刚登录时的版本提示，目前已不需要
		self.resetPhysics()
		self.physics.fall = False							# Fix游戏启动进入场景的角色下落的Bug
		self.updateMoveMode()								# 更新移动速度( 2008.12.30 )
		self.switchFlyWater( True )							# 开启身轻如燕效果
		self.resetPatrol()									# 上线显示摆点路径

		rds.gameMgr.onRoleEnterWorld()						# 进入游戏时通知游戏管理器（这个要放到最后面 hyw--2009.05.15）
		if isPublished:
			BigWorld.callback( 1.0, checkCurrentSpaceData )

		BigWorld.setGraphicsSetting( "HEAT_SHIMMER", 0 )
		rds.gameSettingMgr.onPlayerEnterSpace()				# 应用地图的游戏自定义配置

	def leaveWorld( self ):
		"""
		当离开世界时被调用
		"""
		Role.leaveWorld( self )
		Attack.leaveWorld( self )
		GUIFacade.onRoleLeaveWorld( self )					# 通知 Facade

		self.leaveFishing()									# 如果在捕鱼，则离开渔场

		rds.targetMgr.unbindTarget()						# 清除选定的目标
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		ECenter.fireEvent( "EVT_ON_TRIGGER_PLAYER_LEAVE_WORLD" )	#清除穿装备提示界面
		rds.gameMgr.onRoleLeaveWorld()
		self.stopMove()										# 停止自动移动
		self.endAutoRun( False )
		rds.areaEffectMgr.onStopAreaEffect( self )			# 停止水效果
		rds.areaEffectMgr.stopSpaceEffect()					# 停止场景光效

		self.clearMailbox()							# 清空邮箱

		for linkEffect in self.linkEffect:
			linkEffect.stop()
		self.linkEffect = []

		if self.onLineTimer is not None:	# 停止在线奖励提示计时 by姜毅
			BigWorld.cancelCallback( self.onLineTimer )
			self.onLineTimer = None

		# 清空模型管理器中相关加载信息
		rds.modelFetchMgr.resetFetchModelTask()

		#离开游戏，停止反外挂。LuoCD
		if  self.apexClient != None:
			self.apexClient.StopApexClient()

		# 玩家是否在陷阱范围背景音乐中
		rds.soundMgr.lockBgPlay( False )
		rds.gameSettingMgr.onPlayerLeaveSpace()				# 恢复地图的游戏自定义配置

	def initCacheTasks( self ):
		"""
		初始化缓冲器任务
		"""
		# 把自己role的任务置空
		pass

	def getPhysics( self ):
		"""
		获取角色的 physics
		"""
		entity = self
		if self.vehicle and self.vehicle.inWorld:
			entity = self.vehicle
		if hasattr( entity, "physics" ):
			return entity.physics
		return None

	def targetFocus( self, entity ):
		"""
		当该角色的鼠标进入某个目标时，该函数被引擎调用
		"""
		if getattr( self, "playingVideo", False ) == True:
			return
		if ( hasattr( entity, "onTargetFocus" ) ):
			entity.onTargetFocus()

	def targetBlur( self, entity ):
		"""
		当该角色的鼠标离开某个目标时，该函数被引擎调用
		"""
		if getattr( self, "playingVideo", False ) == True:
			return
		if ( hasattr( entity, "onTargetBlur" ) ):
			entity.onTargetBlur()

	# -------------------------------------------------
	def updateMoveMode( self ) :
		"""
		更新移动模式
		"""
		if self.vehicle:
			func = self.vehicle.setSpeed
			speed = self.vehicle.move_speed
			if self.__isAssaulting :					# 如果处于冲锋状态
				speed = self.vehicle.move_speed
			elif self.__moveMode == self.MOVE_WALK :	# 如果是走路状态
				speed = 2.0								# 暂定走路速度为 2.0m/s
			elif self.__moveMode == self.MOVE_RUN :		# 如果是跑步状态
				speed = self.vehicle.move_speed
			elif self.__moveMode == self.MOVE_FLY :		# 飞行状态
				pass
		else:
			func = self.setSpeed
			speed = self.move_speed
			if self.__isAssaulting :					# 如果处于冲锋状态
				speed = self.move_speed
			elif self.__moveMode == self.MOVE_WALK :	# 如果是走路状态
				speed = 2.0								# 暂定走路速度为 2.0m/s
			elif self.__moveMode == self.MOVE_RUN :		# 如果是跑步状态
				speed = self.move_speed
			elif self.__moveMode == self.MOVE_FLY :		# 飞行状态
				pass
		func( speed )

	def __toggleWalkRun( self ) :
		"""
		行走切换
		"""
		if self.__moveMode == self.MOVE_WALK :
			self.__moveMode = self.MOVE_RUN
		elif self.__moveMode == self.MOVE_RUN :
			self.__moveMode = self.MOVE_WALK
		self.updateMoveMode()

	def __toggleSitdownStandup( self ) :
		"""
		坐立切换
		"""
		pass

	# -------------------------------------------------
	def __bindShortcuts( self ) :
		rds.shortcutMgr.setHandler( "FIXED_GO_TO_CURSOR", self.__moveToCursor )						# 移动到鼠标按下处
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_WALK_RUN", self.__toggleWalkRun )				# 行走切换
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_SITDOWN_STAND", self.__toggleSitdownStandup )	# 坐立切换
		rds.shortcutMgr.setHandler( "ACTION_AUTO_RUN", self.__autoMoveForward )						# 自动向前走
		rds.shortcutMgr.setHandler( "ACTION_FORWARD", self.__handleKeyEvent )			# move forward
		rds.shortcutMgr.setHandler( "ACTION_BACKWORD", self.__handleKeyEvent )			# move backward
		rds.shortcutMgr.setHandler( "ACTION_TURN_LEFT", self.__handleKeyEvent )			# move leftward
		rds.shortcutMgr.setHandler( "ACTION_TURN_RIGHT", self.__handleKeyEvent )		# move rightward
		rds.shortcutMgr.setHandler( "ACTION_JUMP_UP", self.__handleKeyEvent )			# jump up
		rds.shortcutMgr.setHandler( "ACTION_FOLLOW_TARGET", self.__followTarget )		# 自动更随目标

	def __unbindShortcuts( self ) :
		rds.shortcutMgr.setHandler( "FIXED_GO_TO_CURSOR", None )						# 移动到鼠标按下处
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_WALK_RUN", None )					# 行走切换
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_SITDOWN_STAND", None )				# 坐立切换
		rds.shortcutMgr.setHandler( "ACTION_AUTO_RUN", None )							# 自动向前走
		rds.shortcutMgr.setHandler( "ACTION_FORWARD", None )							# move forward
		rds.shortcutMgr.setHandler( "ACTION_BACKWORD", None )							# move backward
		rds.shortcutMgr.setHandler( "ACTION_TURN_LEFT", None )							# move leftward
		rds.shortcutMgr.setHandler( "ACTION_TURN_RIGHT", None )							# move rightward
		rds.shortcutMgr.setHandler( "ACTION_JUMP_UP", None )							# jump up
		rds.shortcutMgr.setHandler( "ACTION_FOLLOW_TARGET", None )						# 自动更随目标

	def __getBindingKeys( self ) :
		scAhead = rds.shortcutMgr.getShortcutInfo( "ACTION_FORWARD" ).key
		scBack = rds.shortcutMgr.getShortcutInfo( "ACTION_BACKWORD" ).key
		scLTurn = rds.shortcutMgr.getShortcutInfo( "ACTION_TURN_LEFT" ).key
		scRTurn = rds.shortcutMgr.getShortcutInfo( "ACTION_TURN_RIGHT" ).key
		scJump = rds.shortcutMgr.getShortcutInfo( "ACTION_JUMP_UP" ).key

		downKeyBindings = []
		downKeyBindings.append( ( [scLTurn], self.__moveLeft ) )	# move leftward
		downKeyBindings.append( ( [scRTurn], self.__moveRight ) )	# move rightward

		if self.getState() != csdefine.ENTITY_STATE_PICK_ANIMA:
			downKeyBindings.append( ( [scAhead], self.__moveForward ) )	# move forward
			downKeyBindings.append( ( [scBack], self.__moveBackward ) )	# move backward
			downKeyBindings.append( ( [scJump], self.__jumpStart ) )	# start jump up

		return keys.buildBindList( downKeyBindings )						# Build our actual key bindings list.

	def __handleKeyEvent( self, down, key, mods ) :
		"""
		control actions via keys
		"""
		if self.key == key:
			self.isSameKey = True
		else:
			self.isSameKey = False
		self.key = key
		if self.isFollowing():
			INFO_MSG("Team Following!! Can't Move!")
			return False
		if self.affectAfeard:												# 处于狂乱状态，不能自行走动
			INFO_MSG("Fearing!! Can't Move!")
			return False
		def isAllKeysDown( downKeys ) :										# 判断指定的键是否都处于按下状态
			if len( downKeys ) == 0 : return False
			for downKey in downKeys :
				if not BigWorld.isKeyDown( downKey ) :
					return False
			return True
		#在WASD行走的时候，切入文本输入状态会前进不止
		if self.isActionState( Action.ASTATE_CONTROL ) and rds.uiHandlerMgr.getTabInUI() and not self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			self.stopMove()
		okayToGo = False													# 临时变量，标记某动作的按键是否完全按下
		keyUsed = False														# 按下键时，是否找到相应的匹配动作（只要有一个动作，则为 True）
		for downKeys, upKeySets, action in self.__getBindingKeys() :		# 循环遍历按键动作
			if key not in downKeys : continue								# 按下的键是否在当前键集中（是否属于该动作）
			okayToGo = isAllKeysDown( downKeys )							# 假设当前动作包含多个键，则判断其他健是否已经全部按下
			if okayToGo :													# 如果当前动作的全部键都处于按下状态
				for upKeys in upKeySets :									# 寻找是否有别的 action 与当前按下的所有键完全吻合
					if isAllKeysDown( upKeys ) :							# 如果别的 action 的所有按键都全部按下
						okayToGo = False									# 则当前 action 的 okayToGo 为 False
						break

			keyUsed = keyUsed or action( okayToGo )							# 调用 action
		if not down :
			return False
		return keyUsed

	def __moveForward( self, isDown ):
		"""
		向前移动
		"""
		#加上移动迅捷的按键判断
		if not isDown:
			self.wasdFlag[0] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			INFO_MSG("Forbid role move!!")
			return False

		if self.state == csdefine.ENTITY_STATE_DEAD:
			INFO_MSG("Role die, can't move!!")
			return False

		if isDown and (self.isSameKey or True in self.wasdFlag) :
			#判断是否触发迅捷移动
			t = time.time()
			if (t - self.wasdFlagTime[0] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag ):
				self.wasdFlag[0] = True
				self.triggerFastMoving()
			self.wasdFlagTime[0] = time.time()
		else:
			self.wasdFlag[0] = False
			self.stopFastMoving() #检测是否取消移动迅捷
		# 如果有骑宠，骑宠截获按键消息
		if self.vehicle:
			self.vehicle.moveForward( isDown )
			return True
		self.updateDirection( Action.DIRECT_FORWARD, isDown )
		#if self.jumping_move( isDown ): return self.jumping_move( isDown )
		self.flushAction()
		return True

	def __moveBackward( self, isDown ):
		"""
		向后移动
		"""
		#加上移动迅捷的按键判断
		if not isDown:
			self.wasdFlag[2] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if isDown and (self.isSameKey or True in self.wasdFlag):
			#判断是否触发迅捷移动
			t = time.time()
			if  ( t - self.wasdFlagTime[2] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag ):
				self.wasdFlag[2] = True
				self.triggerFastMoving()
			self.wasdFlagTime[2] = time.time()
		else:
			self.wasdFlag[2] = False
			self.stopFastMoving() #检测是否取消移动迅捷

		# 如果有骑宠，骑宠截获按键消息
		if self.vehicle:
			self.vehicle.moveBack( isDown )
			return True

		self.updateDirection( Action.DIRECT_BACKWARD, isDown )

		#if self.jumping_move( isDown ): return self.jumping_move( isDown )

		self.flushAction()
		return True

	def __moveLeft( self, isDown ):
		"""
		向左移动
		"""
		#加上移动迅捷的按键判断
		if not isDown:
			self.wasdFlag[1] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if isDown and (self.isSameKey or True in self.wasdFlag):
			#判断是否触发迅捷移动
			t = time.time()
			if  (t - self.wasdFlagTime[1] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag ):
				self.wasdFlag[1] = True
				self.triggerFastMoving()
			self.wasdFlagTime[1] = time.time()
		else:
			self.wasdFlag[1] = False
			self.stopFastMoving() #检测是否取消移动迅捷

		# 如果有骑宠，骑宠截获按键消息
		if self.vehicle:
			self.vehicle.moveLeft( isDown )
			return True

		self.updateDirection( Action.DIRECT_LEFT, isDown )

		#if self.jumping_move( isDown ): return self.jumping_move( isDown )

		self.flushAction()
		return True

	def __moveRight( self, isDown ):
		"""
		向右移动
		"""
		#加上移动迅捷的按键判断
		if not isDown:
			self.wasdFlag[3] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if isDown and (self.isSameKey or True in self.wasdFlag):
			#判断是否触发迅捷移动
			t = time.time()
			if ( t - self.wasdFlagTime[3] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag):
				self.wasdFlag[3] = True
				self.triggerFastMoving()
			self.wasdFlagTime[3] = time.time()
		else:
			self.wasdFlag[3] = False
			self.stopFastMoving() #检测是否取消移动迅捷

		# 如果有骑宠，骑宠截获按键消息
		if self.vehicle:
			self.vehicle.moveRight( isDown )
			return True

		self.updateDirection( Action.DIRECT_RIGHT, isDown )

		#if self.jumping_move( isDown ):return self.jumping_move(isDown)

		self.flushAction()
		return True

	def jumping_move( self, isDown ) :
		"""
		跳跃中的移动
		"""
		vec = self.physics.velocity
		if isDown:
			#如果在跳跃状态要检查是否是面向正方向前进
			if self.getJumpState() in [ Const.STATE_JUMP_UP, Const.STATE_JUMP_UP2, Const.STATE_JUMP_UP3 ]:
				self.physics.velocity = ( vec[0], vec[1], self.move_speed )
				return True
			elif self.getJumpState() == Const.STATE_JUMP_DOWN :
				return True
		else:
			#如果在跳跃状态不更新速度
			if self.getJumpState() != Const.STATE_JUMP_DEFAULT:
				self.physics.velocity = ( 0, vec[1], 0 ) #松开控制键时，取消水平方向上的速度向量
				return True

	def triggerFastMoving( self ):
		"""
		判断是否触发迅捷移动buff
		"""
		if self.state  in [ csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_FIGHT ]:
			return
		if self.getJumpState() != Const.STATE_JUMP_DEFAULT: #如果在跳跃过程中
			return
		if self.isHavePairKey():
			self.wasdFlag = [ False, False, False, False ]
			self.stopFastMoving()
		fmSkillID = 0
		for skillID in Const.JUMP_FAST_BUFF_TRIGGER_SKILLS:
			if skillID  in self.skillList_:
				fmSkillID = skillID
				break
		if fmSkillID != 0:
			skillInstance = skills.getSkill( fmSkillID )
			target = SkillTargetObjImpl.createTargetObjEntity( self )
			skillInstance.spell( self, target )

	def stopFastMoving( self, isControl = True ):
		"""
		停止迅捷移动buff
		"""
		if isControl and True in self.wasdFlag and not self.isHavePairKey():
			return
		buffData = self.findBuffByBuffID(  Const.JUMP_FAST_BUFF_ID )
		if buffData : #迅捷移动buff存在
			self.requestRemoveBuff( buffData[ "index" ] )
			self.wasdFlag = [ False, False, False, False ]

	def isHavePairKey( self ):
		"""
		检查是否仅仅按了一对相反的按键
		比如W+S 或者A+D
		"""
		if ( self.wasdFlag[0] == self.wasdFlag[2] == True and self.wasdFlag[1] == self.wasdFlag[3] == False ):
			return True
		if ( self.wasdFlag[0] == self.wasdFlag[2] == False and self.wasdFlag[1] == self.wasdFlag[3] == True ):
			return True
		if  self.wasdFlag.count( True ) == 4:
			return True
		return False

	def __autoMoveForward( self ):
		"""
		当按下键时，自动向前移动
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if self.vehicle:
			self.vehicle.autoMoveForward()
			return True

		if self.isActionState( Action.ASTATE_AUTOFORWARD ) :
			self.setActionState( Action.ASTATE_CONTROL )
			self.stopMove()
		else :
			self.setActionState( Action.ASTATE_AUTOFORWARD )
			BigWorld.dcursor().yaw = BigWorld.camera().direction.yaw
			self.startMove()
		self.flushAction()
		return True

	def __onMoveToOver( self, success ):
		"""
		when move to a position this method will called at seekCallback method
		"""
		UnitSelect().hideMoveGuider()
		if success :
			self.flushActionByKeyEvent()
			self.setActionState( Action.ASTATE_CONTROL )

	def __onMoveToDirectlyOver( self, success ):
		"""
		when move to a position directly this method will called at seekCallback method
		"""
		UnitSelect().hideMoveGuider()
		self.stopMove()
		if success :
			self.flushActionByKeyEvent()
			self.setActionState( Action.ASTATE_CONTROL )

	def __onSeekCollisionCBF( self ):
		"""
		以seek方式移动中碰到障碍物时的回调函数
		"""
		UnitSelect().hideMoveGuider()
		self.stopMove()

	def __toggleOtherRoles( self ) :
		"""
		显示/隐藏其他角色模型
		hyw -- 09.01.10
		"""
		toggleTypes = [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_VEHICLE]
		self.isRolesVisible = not self.isRolesVisible
		vehicle = self.vehicle
		for ent in BigWorld.entities.values() :
			if ent.getEntityType() not in toggleTypes : continue
			if ent == self : continue
			if vehicle and ent.vehicle == vehicle: continue
			if ent.isEntityType( csdefine.ENTITY_TYPE_PET ) :
				if ent.getOwner() == self : continue
			if ent.isEntityType( csdefine.ENTITY_TYPE_VEHICLE ) :
				if vehicle == ent: continue
			ent.updateVisibility()

	def set_planesID( self, oldValue ):
		"""
		设置新的位面ID
		"""
		if oldValue ==  self.planesID:
			return

		if self.followTargetID:#如果有跟随对象，则取消
			self.team_cancelFollow( csstatus.TEAM_FOLLOW_FAIL )

		for e in BigWorld.entities.values():
			if e.__class__.__name__ not in csconst.CLIENT_ENTITY_TYPE:
				e.updateVisibility()

	def setIsShowSelf( self, isShow ):
		"""
		是否显示玩家自己模型
		"""
		self.isShowSelf = isShow
		self.updateVisibility()

	def isShowOtherRolesAndUI( self, isShow ) :
		"""
		显示/隐藏其他角色模型(包括UI)
		by wuxo 2012-4-12
		"""
		toggleTypes = [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_VEHICLE]
		self.isRolesAndUIVisible = isShow
		vehicle = self.vehicle
		for ent in BigWorld.entities.values() :
			if ent.getEntityType() not in toggleTypes : continue
			if ent == self : continue
			if vehicle and ent.vehicle == vehicle: continue
			if ent.isEntityType( csdefine.ENTITY_TYPE_PET ) :
				if ent.getOwner() == self : continue
			if ent.isEntityType( csdefine.ENTITY_TYPE_VEHICLE ) :
				if vehicle == ent: continue
			ent.updateVisibility()


	def canJump( self ):
		"""
		是否可以跳跃
		"""
		return self.actWord & csdefine.ACTION_FORBID_JUMP != csdefine.ACTION_FORBID_JUMP

	def __jumpStart( self, isDown ) :
		"""
		jump up when hold key "space"
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if not self.isAlive() or not self.canJump():
			return False

		if BigWorld.isKeyDown( keys.KEY_LCONTROL ) or BigWorld.isKeyDown( keys.KEY_RCONTROL ):
			return False

		model = self.getModel()
		if self.currentModelNumber and model and not model.hasAction( Const.MODEL_ACTION_JUMP_AIR ):
			self.statusMessage( csstatus.ROLE_CAN_NOT_JUMP )
			return False

		# 中断正在吟唱的技能
		self.interruptAttack( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )
		# 取消钓鱼
		if self.currentModelNumber == "fishing":
			self.end_body_changing( "" )

		# 骑宠截获消息
		if self.vehicle:
			self.vehicle.updateDirection( Action.DIRECT_JUMPUP, True ) #记录玩家曾经跳跃过 即 中断跟随状态
			if isDown:
				self.vehicle.jumpBegin()
			return True

		if self.getJumpState() == Const.STATE_JUMP_DEFAULT and self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			vec = self.physics.velocity
			if isDown:
				self.physics.fall = False
				self.physics.velocity = ( vec[0], self.move_speed, vec[2] )
				if vec[2] == 0:
					if not self.vehicleType: return False    #如果飞行骑宠没有加载完毕，则不匹配动作
					self.onSwitchVehicle( Const.MODEL_ACTION_FLOAT_UP )
			else:
				self.physics.velocity = ( vec[0], 0, vec[2] )
				if vec[2] == 0:
					self.onSwitchVehicle( Const.MODEL_ACTION_STAND )
			return True # 如果认为按键消息已经被处理，应该返回True 参见：InWorld.handleKeyEvent

		self.updateDirection( Action.DIRECT_JUMPUP, True ) #记录玩家曾经跳跃过 即 中断跟随状态
		if isDown:
			self.jumpBegin()
		return True

	def __flyJumpUp( self ):
		self.cell.onFlyJumpUpNotifyFC()
		self.flyJumpUp()

	def setJumpType( self ):
		"""
		设置跳跃类型
		"""
		jumpType = csdefine.JUMP_TYPE_LAND
		if self.onWaterArea and not self.vehicleModelNum:
			jumpIndex = random.choice( range( len( csconst.JUMP_TYPE_WATERS ) ) )
			jumpType = csconst.JUMP_TYPE_WATERS[ jumpIndex ]

		self.jumpType = jumpType

	def jumpBegin( self ) :
		if self.getJumpState() == Const.STATE_JUMP_DEFAULT:
			#计算弹跳的初始速度
			if self.jumpHeight1 > 0.0:
				jumpV0 = math.sqrt(self.jumpHeight1*2*self.physics.gravity)
			if self.jumpTime > 0.0 and self.jumpHeight1 <= 0.0:
				jumpV0 = self.physics.gravity * self.jumpTime
			if jumpV0 > 0.0:
				self.setJumpType()
				self.physics.doJump(jumpV0,0.0)
			self.isJump2 = False
			self.isJump3 = False
			self.startHeight = self.position[1]
			return True
		#屏蔽坐骑的2段/3段跳
		if self.vehicleModelNum or self.getState() == csdefine.ENTITY_STATE_RACER:
			return False
		if self.getJumpState() == Const.STATE_JUMP_DEFAULT : return False
		if self.onWaterArea:return False
		if self.position[1] > self.startHeight and not self.isJump2 :
			if (self.hasSkill( csdefine.JUMP_UP2_SKILLID ) or self.hasSkill( csdefine.JUMP_UP3_SKILLID ) ) and self.energy >= csdefine.JUMP_UP2_ENERGY :
				jumpV0 = math.sqrt(self.jumpHeight2*2*self.physics.gravity)
				self.physics.doJump(jumpV0,Const.JUMP_PREPARE_TIME)
				self.isJump2 = True
				self.startHeight = self.position[1]
				return True
		if self.isJump2 and self.position[1] > self.startHeight and not self.isJump3:
			if self.hasSkill( csdefine.JUMP_UP3_SKILLID )  and self.energy >= csdefine.JUMP_UP3_ENERGY:
				jumpV0 = math.sqrt(self.jumpHeight3*2*self.physics.gravity)
				self.physics.doJump(jumpV0,Const.JUMP_PREPARE_TIME)
				self.isJump3 = True
				return True
		return False

	def __jumpUp( self ):
		self.isJumpProcess = True
		jumpMask = self.jumpType | csdefine.JUMP_TIME_UP1
		self.cell.onJumpNotifyFC( jumpMask )
		self.playJumpActions( jumpMask )

	def __jumpUp2( self ):
		jumpMask = self.jumpType | csdefine.JUMP_TIME_UP2
		self.cell.onJumpNotifyFC( jumpMask )
		self.playJumpActions( jumpMask )

	def __jumpUp3( self ):
		jumpMask = self.jumpType | csdefine.JUMP_TIME_UP3
		self.cell.onJumpNotifyFC( jumpMask )
		self.playJumpActions( jumpMask )

	def __jumpPrepare( self ):
		jumpMask = self.jumpType | csdefine.JUMP_TIME_UPPREPARE
		self.cell.onJumpNotifyFC( jumpMask )
		self.playJumpActions( jumpMask )

	def __jumpDown( self ) :
		jumpMask = self.jumpType | csdefine.JUMP_TIME_DOWN
		self.cell.onJumpNotifyFC( jumpMask )
		self.physics.gravity = self.geneGravity * 9.8
		self.isJumpProcess = True
		self.playJumpActions( jumpMask )


	def __jumpEnd( self ) :
		if self.getJumpState() != Const.STATE_JUMP_DEFAULT:
			jumpMask = self.jumpType | csdefine.JUMP_TIME_END
			self.cell.onJumpNotifyFC( jumpMask )
			self.playJumpActions( jumpMask )
		self.physics.gravity = 9.8
		self.updateDirection( Action.DIRECT_JUMPUP, False )			# 跳跃结束时，去掉向上方向标记（hyw -- 2008.12.23）
		self.flushAction()
		self.floatOnWaterAreaCallback( self.onWater )				# 从水中跳到陆地，是否在水面与是否在水域是同步的。
		self.isJump2 = False
		self.isJump3 = False
		self.startHeight = 0
		self.isJumpProcess = False
		if self.onWaterJumpTimer is not None:			# 手动跳跃重新计算间隔时间
			BigWorld.cancelCallback( self.onWaterJumpTimer )
			self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )

	def __jumpDownOnFly( self ):
		self.physics.fall = False
		self.physics.jumpState = Const.STATE_JUMP_DEFAULT
#		self.isJumpProcess = True
		self.setArmCaps() #设置caps以去除跳跃动作中融入walk、run、run_weapon等动作

	def __onFallToGround( self ):
		"""
		贴进地表时的处理
		"""
		# if 玩家已经死亡
		if self.state == csdefine.ENTITY_STATE_DEAD:
			# 停止玩家下落（否则玩家掉落到一个会使自己向下滑的斜面上之后会因为客户端引擎往下拉玩家，而服务器端因为ENTITY.topSpeed = 0又不能动，因此产生剧烈的镜头闪烁）
			self.physics.fall = False
			return

		self.physics.fall = True
		vec = self.physics.velocity
		v2 = 0 if (vec[2] == 0) else self.move_speed
		v2 = v2 if vec[2] > 0 else -v2
		self.physics.velocity = ( vec[0], 0, vec[2] )

	def isJumping( self ):
		"""
		是否在跳跃中
		"""
		if self.model is None: return False
		return self.getJumpState() != Const.STATE_JUMP_DEFAULT

	def getJumpState( self ) :
		"""
		获取跳跃状态
		"""
		return getattr( self.getPhysics(), "jumpState", None )

	def isMoving( self ):
		"""
		是否在移动中
		"""
		return Action.Action.isMoving( self )

	# --------------------------------------------------
	# 鼠标点击移动
	# --------------------------------------------------
	def __moveToCursor( self ) :
		"""
		move to cursor
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if self.vehicle and not self.actionSign( csdefine.ACTION_FORBID_MOVE ):		# 如果当前骑着骑宠，则将消息转换给骑宠处理
			return self.vehicle.moveToCursor()

		if not self.allowMove(): return False
		entity = BigWorld.target.entity							# 检测是否点在目标身上，点在则不会在这里处理往前走
		if entity is not None: return False

		toPos = gbref.cursorToDropPoint()						# 计算鼠标按下处的三维坐标
		if toPos is None : return False
		if self.isJumping():									# 如果当前正处于跳跃状态
			self.onMoveToCursorJump( toPos )					# 则，跳跃完毕后再走到指定点
			return True

		if self.isActionState( Action.ASTATE_NAVIGATE ):		# 刚好在自动寻路，则结束自动寻路
			self.endAutoRun( False )
		self.setActionState( Action.ASTATE_DEST )				# 设置为走到指定目标

		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):				# 飞行状态下，直冲向目标
			self.stopMove()
			self.moveToDirectly( toPos, self.__onMoveToDirectlyOver )
			UnitSelect().showMoveGuider( toPos )					# 这个必须放在后面，因为moveTo()会先stopMove()
			return True

		if self.moveTo( toPos, self.__onMoveToOver ):
			UnitSelect().showMoveGuider( toPos )					# 这个必须放在后面，因为moveTo()会先stopMove()

		return True


	def onMoveToCursorJump( self, pos ):
		"""
		当跳起按下鼠标左键移动时调用
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return
		self.__jumpPos = Math.Vector3( pos )							# 记录下结束跳跃后，需要移动到的位置
		UnitSelect().showMoveGuider( pos )
		BigWorld.cancelCallback( self.__jumpCBID )
		self.__jumpCBID = BigWorld.callback( 0.1, self.__moveJumpCB )	# 侦测跳跃结束

	def __moveJumpCB( self ):
		"""
		跳起移动CB
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			UnitSelect().hideMoveGuider()
			return

		if self.isJumping():												# 如果还处于跳跃中
			BigWorld.cancelCallback( self.__jumpCBID )
			self.__jumpCBID = BigWorld.callback( 0.1, self.__moveJumpCB )	# 则继续侦测
		else:																# 如果跳跃结束
			if self.isActionState( Action.ASTATE_NAVIGATE ):				# 刚好在自动寻路，则结束自动寻路
				self.endAutoRun( False )
			self.setActionState( Action.ASTATE_DEST )						# 则将行为状态更改为移动到某点
			if self.moveTo( self.__jumpPos, self.__onMoveToOver ):				# MOVETO会清除标记，所以下面再来一次
				UnitSelect().showMoveGuider( self.__jumpPos )

	def __clearSpanSpaceData( self, withForce ):
		"""
		清空跨场景信息数据
		@type		withForce:	bool
		@param		withForce:	是否强制清除
		"""
		if not self.__spanSpaceDataLock or withForce:
			self.__spanSpaceDstLabel = ""
			self.__spanSpaceDstPos = Math.Vector3( self.INVALIDITY_POS ) #标志为无效位置
			self.__spanSpaceNearby = 0
			self.__spanSpaceTarget = ""
			self.__spanSpaceDataLock = False

	def __followTarget( self ) :
		"""
		跟随当前目标的快捷键
		"""
		target = self.targetEntity
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			self.autoFollow( target.id )

	def flushAction( self ):
		"""
		根据行为状态和移动意图方向，更新行为动作（停止或按某个方向移动）
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			return
		if not self.allowMove() :
			return
		if rds.uiHandlerMgr.getTabInUI():
			return
		if not ( self.vehicle or self.hasFlag( csdefine.ROLE_FLAG_FLY ) ):
			self.physics.fall = True					#用于解决过传送门偶尔出现角色飞空的问题
		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.__onMoveToDirectlyOver( False )

		Action.Action.flushAction( self )

	def flushActionByKeyEvent( self ):
		if not self.allowMove(): return
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return
		if rds.uiHandlerMgr.getTabInUI():
			return
		Action.Action.flushActionByKeyEvent(self)

	def flyMove( self, camDirection ):
		"""
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return
		if not self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		vec = self.physics.velocity
		if self.isMoving() and vec[2] != 0:
			if self.isActionState( Action.ASTATE_DEST ):
				self.__onMoveToDirectlyOver( True )
				return
			y_sp = xz_sp = sp = self.move_speed
			if self.physics.fall :
				y_sp = 0
			else :
				xz_sp = sp * math.sqrt( camDirection[2]**2 + camDirection[0]**2 )
				y_sp = sp * camDirection[1]
				if self.testDirection( Action.DIRECT_BACKWARD ) :
					y_sp = -y_sp
			self.physics.velocity = ( 0, y_sp, xz_sp )

	def isInTeamInviteForbidSpace( self ):
		"""
		判断玩家是否在指定地图中
		"""
		spaceName = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		if spaceName in csconst.TEAM_INVIETE_FORBID_MAP:
			return True
		return False

#-------------------------飞行骑宠相关的检测Start by mushuang-------------------------#
	def isOnSomething( self ):
		"""
		检测在掉落中是否落到某物体上
		"""
		return self.__flyingVehicle.isOnSomething()

	def enableFlyingRelatedDetection( self, spBoundingBoxMin, spBoundingBoxMax ):
		"""
		defined method
		@enableFlyingRelatedDetection: 开启和飞行有关的检测
		@spBoundingBoxMin: 空间外接盒的一个对角顶点
		@spBoundingBoxMax: 和spBoundingBoxMin相对的另一个对角顶点
		"""
		self.__flyingVehicle.enableFlyingRelatedDetection( spBoundingBoxMin, spBoundingBoxMax )

	def disableFlyingRelatedDetection( self ):
		"""
		defined method
		@disableFlyingRelatedDetection: 关闭和飞行有关的检测
		"""
		self.__flyingVehicle.disableFlyingRelatedDetection()

	def onEnterFlyState( self ):
		"""
		进入飞行状态
		"""
		rds.worldCamHandler.cameraShell.camera_.minHeightOffsetLimit -= 3.0
		self.physics.fallToGroundDetectLen = 0
		self.physics.setJumpDownFn( self.__jumpDownOnFly )
		self.__flyingVehicle.updateSpaceBoundingBox()

	def onLeaveFlyState( self ):
		"""
		离开飞行状态
		"""
		self.physics.fallToGroundDetectLen = -1.0
		self.physics.setJumpDownFn( self.__jumpDown )
		self.physics.fall = True
		self.physics.stop() # 防止玩家按着空格关闭飞行骑宠，然后出现在空中播放奔跑动作，且摔死（如果高度足以摔死的话）在空中的问题 by mushuang
		UnitSelect().hideMoveGuider()
		self.__flyingVehicle.updateSpaceBoundingBox()
#-------------------------飞行骑宠相关的检测End by mushuang-------------------------#

	def allowMove( self ):
		"""
		判断角色是否可以移动
		"""
		if self.effect_state & csdefine.EFFECT_STATE_BE_HOMING :
			return True
		if self.actionSign( csdefine.ACTION_FORBID_MOVE )  :				# verify wether allow to move( defined in Charactor.py )
			INFO_MSG( "I can't move！" )
			return False
		if self.getPhysics() is None :												# Only controlled entities have a 'physics' attribute
			return False
		if not self.physics.fall and not self.hasFlag( csdefine.ROLE_FLAG_FLY ):	#玩家处于不可坠落状态时且非飞行状态，不允许移动
			return False
		return True

	def doRandomRun( self, centerPos, radius ):
		"""
		define method
		走到centerPos为原点，radius为半径的随机采样点
		"""
		initRad = 2 * math.pi * random.random()
		for tryNum in xrange( 0, 8 ):
			rad = initRad + tryNum * 45.0
			pos = Math.Vector3( centerPos )
			distance = radius * random.random()
			if distance < 2:
				distance = 2
			pos.x += distance * math.sin( rad )
			pos.z += distance * math.cos( rad )
			if self.moveToPos( pos ):
				break	# 直接跳出循环

	def showTargetAttribute( self, targetID ):
		"""
		显示对方玩家的属性(观察功能)
		@param   targetID: 对方玩家的ID
		@type    targetID: OBJECT_ID
		"""
		target = BigWorld.entities.get( targetID )
		if target is None: #没有这个玩家
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
			return

		otherInfo = {}
		otherInfo["TongName"] =	target.tongName				#帮会名称
		if target.tongName:
			tongGrade = target.tong_grade						#获取帮会权限
			if target.tong_dutyNames.has_key( tongGrade ):
				tongDuty = target.tong_dutyNames[tongGrade]
			else:
				tongDuty = Const.TONG_GRADE_MAPPING[tongGrade]
			otherInfo["TongDuty"]   =	tongDuty								#帮会职位
		otherInfo["Name"] = target.getName()									#名字
		otherInfo["Gender"] = csconst.g_chs_gender[target.getGender()]			#性别
		otherInfo["Pclass"] = csconst.g_chs_class[target.getClass()]			#职业
		otherInfo["Level"] = target.getLevel()									#等级
		espial.showTargetOtherInfo(otherInfo)									#让界面去显示玩家的其他信息 如帮会 职位 等级 性别......

	def showTargetEquip(self ,items , ifEnd):
		"""
		显示对方玩家的装备(观察功能)
		@param   items: 对方玩家的部分信息
		@type    items: LIST
		@param   targetID: 对方玩家的ID
		@type    targetID: OBJECT_ID
		"""
		espial.showTargetEquip( items, ifEnd )			#让界面去显示玩家的装备

	def pursueEntity( self, entity, nearby, callback = lambda player, entity, success : False ) :
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是player, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return
		if not self.allowMove(): return

		if self.vehicle:
			self.vehicle.pursueEntity( entity, nearby, callback )
		elif self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.moveToDirectly( entity.position, self.__onMoveToDirectlyOver )
		else:
			Action.Action.pursueEntity( self, entity, nearby, callback )

	def pursuePosition( self, pos, nearby, callback = lambda player, entity, success : False ) :
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是player, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return
		if not self.allowMove(): return

		if self.vehicle:
			self.vehicle.pursuePosition( pos, nearby, callback )
		elif self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.moveToDirectly( pos, self.__onMoveToDirectlyOver )
		else:
			Action.Action.pursuePosition( self, pos, nearby, callback )

	def disToPos( self, position, callback = None ) :
		"""
		利用寻路移动到指定位置，玩家位置与指定位置的距离
		@type			position	  : Vector3
		@param			position	  : 目标位置
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : 移动结束回调
		"""
		path_distance = 0
		runPathList = []
		#寻路不可到达 那么距离设为1000
		#设置路径的时候，进行了position的处理，所以来个拷贝
		position1 = copy.copy( position )
		runPathList =  Action.Action.getSrcAndNearDstPos( self, position1 )
		if len( runPathList ) < 1:
			path_distance = 1000
			return path_distance
		dis_temp1 = Math.Vector3().distTo( self.position - runPathList[0] )
		path_distance += dis_temp1
		if len( runPathList ) > 1 :
			for index in xrange( 1, ( len( runPathList ) - 1) ):
				dis_temp2 = Math.Vector3().distTo( runPathList[index] - runPathList[index-1] )
				path_distance += dis_temp2
		return path_distance

	def moveTo( self, position, callback = None ) :
		"""
		移动到指定位置，这个接口会进行玩家客户端控制限制相关判断
		@type			RETURN		  : bool
		@param			RETURN		  : 目的地是否可以抵达
		@type			position	  : Vector3
		@param			position	  : 目标位置
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : 移动结束回调
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False
		if not self.allowMove(): return False
		return self.moveToPos( position, callback )

	def moveToPos( self, position, callback = None ) :
		"""
		移动到指定位置
		@type			RETURN		  : bool
		@param			RETURN		  : 目的地是否可以抵达
		@type			position	  : Vector3
		@param			position	  : 目标位置
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : 移动结束回调
		"""
		if self.vehicle:
			return self.vehicle.moveTo( position, callback )
		else:
			return Action.Action.moveTo( self, position, callback )


	def moveToDirectly( self, position, callback = None ) :
		"""
		笔直地移动到指定位置
		@type			RETURN		  : bool
		@param			RETURN		  : 目的地是否可以抵达
		@type			position	  : Vector3
		@param			position	  : 目标位置
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : 移动结束回调
		"""
		self.seek( position, 0.0, callback, True, True )
		if self.hasFlag( csdefine.ROLE_FLAG_FLY ) or  self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
			s = position - self.position
			s.normalise()
			self.physics.velocity = self.move_speed * s
		else:
			self.physics.velocity = ( 0, 0, self.move_speed )

		self.physics.setSeekCollisionCallBackFn( self.__onSeekCollisionCBF )


	def autoRun( self, position, nearby = 0.0, dstSpace = "" ) :
		"""
		自动寻路，某地图，某坐标
		@type			position   : Math.Vector3
		@param			position   : 目标位置
		@type			nearby     : float
		@param			nearby     : 移动到目标位置附近的距离
		@type			dstSpace   : string
		@param			dstSpace   : 目标Space Name
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return

		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.statusMessage( csstatus.AUTO_RUN_NOT_IN_FLY_STATE ) #add by wuxo 2011-11-8
			return

		curSpaceLabel = self.getSpaceLabel()
		if dstSpace == curSpaceLabel or curSpaceLabel is None:
			dstSpace = "" #目标点在当前场景，不启用跨场景搜索

		if not dstSpace:
			if curSpaceLabel in spaceHeightDatas.keys() and \
				Math.Vector3( position ).y >= spaceHeightDatas.get( curSpaceLabel, 0.0 ) and \
				self.position.y < spaceHeightDatas.get( curSpaceLabel, 0.0 ):	# 在同一空间并且目标点在空中并且玩家在地面
					self.statusMessage( csstatus.AUTO_RUN_CAN_NOT_GET_PATH_AIR )
					self.stopMove()
					return
			if curSpaceLabel in spaceHeightDatas.keys() and \
				Math.Vector3( position ).y < spaceHeightDatas.get( curSpaceLabel, 0.0 ) and \
				self.position.y >= spaceHeightDatas.get( curSpaceLabel, 0.0 ):	# 在同一空间并且目标点在地面并且玩家在空中
					self.statusMessage( csstatus.AUTO_RUN_CAN_NOT_GET_PATH_FLOOR )
					self.stopMove()
					return

		if self.vehicle :
			self.vehicle.autoRun( position, nearby, dstSpace )
		else :
			Action.Action.autoRun( self, position, nearby, dstSpace )

		self.__spanSpaceDstLabel = dstSpace
		self.__spanSpaceDstPos = Math.Vector3( position )
		self.__spanSpaceNearby = nearby

	def resumeAutoRun( self ):
		"""
		恢复自动寻路
		"""
		if self.__spanSpaceDstPos == self.INVALIDITY_POS:
			return
		self.autoRun( self.__spanSpaceDstPos, self.__spanSpaceNearby, self.__spanSpaceDstLabel )

	def resetPhysics( self ) :
		"""
		"""
		self.physics = keys.STANDARD_PHYSICS
		self.physics.velocity = ( 0.0, 0.0, 0.0 )
		self.physics.velocityMouse = "Direction"
		self.physics.angular = 0
		self.physics.angularMouse = "MouseX"
		self.physics.collide = 1
		self.physics.fall = 1
		self.physics.modelWidth = 0.4
		self.physics.modelDepth = 0.3
		self.physics.modelHeight = 2.5
		self.physics.isMovingNotifier = self.onMoveChanged	# 设置移动通知函数
		self.physics.scrambleHeight = 0.5

		self.physics.setJumpEndFn( self.__jumpEnd )
		self.physics.setJumpUpFn( self.__jumpUp )
		self.physics.setJumpDownFn( self.__jumpDown )
		self.physics.setJumpSecondUpFn( self.__jumpUp2 )
		self.physics.setJumpThreeUpFn( self.__jumpUp3 )
		self.physics.setjumpSecondPrepareFn( self.__jumpPrepare )
		self.physics.setjumpThreePrepareFn( self.__jumpPrepare )

		self.physics.setFallToGroundCallBackFn( self.__onFallToGround )
		self.__flyingVehicle.refreshFlyingSetting()			# 刷新当前地图的飞行设置
		self.clearControlForbid() #这里需要初始化玩家控制限制

	def requestInitialize( self, initType, callback ) :
		"""
		请求初始化角色属性( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : 初始化类型
		@type				callback : functor
		@param				callback : 初始化完毕时的回调
		"""
		if not csdefine.ROLE_INITIALIZE in self.serverRequests:
			self.serverRequests[csdefine.ROLE_INITIALIZE] = []
		self.serverRequests[csdefine.ROLE_INITIALIZE].append( initType )
		DEBUG_MSG( "start init type %i"%initType )
		self.__initializeCallback = callback
		if initType in csconst.ROLE_INIT_BASES :			# 请求 base 的初始化
			self.base.requestInitialize( initType )
		elif initType in csconst.ROLE_INIT_CELLS :			# 请求 cell 的初始化
			self.cell.requestInitialize( initType )
		else :
			raise "unrecognize initialize type: %d" % initType

	def onInitialized( self, initType ) :
		"""
		<Exposed/>
		当某类属性初始化完毕被调用( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : 初始化类型，在 csdefine 中定义
		"""
		self.__initializeCallback()
		DEBUG_MSG( "Role init type %i finish!"%initType )
		if initType == csdefine.ROLE_INIT_QUICK_BAR:
			self.cell.requestInitSpaceSkill()
		if initType == csdefine.ROLE_INIT_QUEST_LOGS:
			ECenter.fireEvent( "EVT_ON_ROLE_QUESTLOG_INITED" )
		if initType == csdefine.ROLE_INIT_VEHICLES:
			ECenter.fireEvent( "EVT_ON_ROLE_VEHICLES_INITED" )
		self.serverRequests[csdefine.ROLE_INITIALIZE].remove( initType )

	def onEndInitialized( self ) :
		"""
		初始化结束
		"""
		TongInterface.onEndInitialized( self )
		ECenter.fireEvent( "EVT_ON_ROLE_END_INIT" )				# 当角色初始化完毕以后发送一个加载完毕的消息

	def playSpaceCameraEvent( self ) :
		"""
		进入某些剧情副本时直接无缝播放镜头,播放镜头时，不显示地图区域检测
		"""
		spaceName = BigWorld.getSpaceName( self.spaceID )
		for questID in self.currentDoingQuestIDList :
			data = questConfig.get( ( spaceName, questID ), None )
			if data:
				rds.cameraEventMgr.trigger( data )
		for key_info in questConfig.keys():
			if key_info[0] == spaceName and key_info[1] == 0:
				eventID = questConfig[ key_info ]
				rds.cameraEventMgr.trigger( eventID )

	# ------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		QuickBar.onEvent( self, eventMacro, *args )

	@property
	def targetEntity( self ) :
		return rds.targetMgr.getTarget()

	def isSpanSpaceNavigate( self ):
		"""
		判断是否处于跨场景寻路
		"""
		return self.__spanSpaceDstLabel != ""

	def stopMove( self, isControl = False ) :
		"""
		停止移动
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) and not rds.roleFlyMgr.isFlyState :
			return
		
		if self.state == csdefine.ENTITY_STATE_PICK_ANIMA: #拾取灵气的状态下，不充许停止移动
			return
		
		self.__clearSpanSpaceData( False )
		if self.vehicle and self.vehicle.inWorld:
			self.vehicle.stopMove()
			self.stopFastMoving(isControl)
			return
		Action.Action.stopMove( self )
		self.stopFastMoving(isControl)

	def onFirstSpaceReady( self ):
		"""
		当第一次场景加载完毕时被调用
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.physics.fall = True

		if self.state == csdefine.ENTITY_STATE_DEAD:
			BigWorld.callback( 0.5, self.pointReviveClew )

		self.resetCamera() # 重新设置镜头
		self.base.pcg_requestPet()
		rds.gameMgr.onFirstSpaceReady()
		rds.areaEffectMgr.startSpaceEffect( self )	# 空间改变触发场景光效

		if self.isReceiveEnterInviteJoin:	# 如果有收到参加知识问答请求
			BigWorld.callback( 1.0, Functor( ECenter.fireEvent, "EVT_ON_QUIZ_ON_ENTER_INVITE_JOIN" ) )

		if self.campFengHuo_signUpFlag:		#如果玩家成功报名了阵营烽火连天
			self.onStatusMessage( csstatus.CAMP_FENG_HUO_ONLINE_TIPS, "" )
		if self.benefitTime > Const.BENIFIT_PERIOD:	# 如果到达奖励时间则给出奖励提示 否则提示开始计时 by姜毅
			LevelUpAwardReminder.instance().onRoleBenefit()

		else:
			onLineTimeLeft = Const.BENIFIT_PERIOD - self.benefitTime
			self.onLineTimer = BigWorld.callback( onLineTimeLeft, self.onLineCount )
		self.cell.onTeleportReady( self.spaceID )
		if not self.spaceSkillInitCompleted and len( self.spaceSkillList ):
			ECenter.fireEvent( "EVT_ON_ENTER_SPECIAL_COPYSPACE", self.spaceSkillList, self.spaceSkillSpaceType )

		self.__flyingVehicle.turnonDeathDepthDetect()				# 打开死亡深度侦测
		curWholeArea = self.getCurrWholeArea()
		if curWholeArea is None:return
		curWholeArea.setTimeOfDay()

	def onTeleportReady( self ) :
		"""
		当场景加载完毕后，该函数被调用
		"""
		if not ( self.hasFlag( csdefine.ROLE_FLAG_FLY ) or self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) ) :
			self.physics.fall = True

		if self.state != csdefine.ENTITY_STATE_DEAD: #从副本传出后自动复活，此时需要去掉玩家死亡的特殊处理
			Role.disableSkeletonCollider( self )
			Role.disableUnitSelectModel( self )

		rds.areaEffectMgr.startSpaceEffect( self )	# 空间改变触发场景光效

		# 通知宠物刷新
		actPet = self.pcg_getActPet()
		if actPet is not None :
			actPet.onTeleportReady()

		# 如果有法宝，法宝一起跳转
		if self.talismanModel:
			self.talismanModel.position = self.position + ( 1.0, 1.5, 0.0 )

		# 关闭自动寻路窗口
		ECenter.fireEvent( "EVT_ON_HIDE_NAVIGATE_WINDOW" )
		self.cell.onTeleportReady( self.spaceID )
		if  self.__spanSpaceDataLock and self.isSpanSpaceNavigate():
			self.__expectTarget = self.__spanSpaceTarget
			self.autoRun( self.__spanSpaceDstPos, self.__spanSpaceNearby, self.__spanSpaceDstLabel )
			self.__spanSpaceDataLock = False
		elif self.__expectTarget != "":
			self.talkWithTarget( self.__expectTarget )		# 使用引路蜂传送时打开目标NPC对话框
			self.__expectTarget = ""
		if not self.spaceSkillInitCompleted and len( self.spaceSkillList ):
			ECenter.fireEvent( "EVT_ON_ENTER_SPECIAL_COPYSPACE", self.spaceSkillList, self.spaceSkillSpaceType )

		self.__flyingVehicle.updateDeathDepth()				# 刷新当前地图的死亡深度

	def checkTelepoertFly( self ):
		"""
		检查是否需要继续进入飞翔传送
		"""
		if self.continueFlyPath != "":
			rds.roleFlyMgr.startRoleFly( self.continueFlyPath, 0, 0 )
			self.continueFlyPath = ""

	def onStatusMessage( self, statusID, sargs ) :
		"""
		def method
		receive all kind of status of operation
		@type				statusID : INT32
		@param				statusID : statusID defined in common/csstatus.py
		@type				sargs	 : STRING
		@param				sargs	 : in-line arguments of the status information defined in csstatus_msgs
		@return						 : None
		"""
		if sargs == "":
			args = ()
		else:
			args = eval( sargs )
		RoleChat.onStatusMessage_( self, statusID, *args )
		ECenter.fireEvent( "EVT_ON_RECEIVE_STATUS_MESSAGE", statusID, *args )

	def onDirectMessage( self, chids, spkName, msg ) :
		"""
		def method
		直接接收消息，包含频道和发言者信息
		@type				chids 	 : ARRAY <of> INT8 </of>
		@param				chids 	 : 频道列表
		@type				spkName	 : STRING
		@param				spkName	 : 发言者名称
		@type				spkName	 : STRING
		@param				spkName	 : 消息内容
		@return						 : None
		"""
		RoleChat._onDirectMessage( self, chids, spkName, msg )

	# ----------------------------------------------------------------
	def isPlayer( self ) :
		"""
		当前状态为玩家
		@rtype				: bool
		@return				: 返回指角色已经成为玩家本身
		"""
		return True

	def isFirstEnterWorld( self ) :
		"""
		指出角色是否是第一次进入世界
		hyw--2009.07.31
		"""
		return self.level == 1 and self.lifetime < 12.0										# 角色在线时间小于某个值和等级为1级时被认为是第一次进入游戏

	def checkAlive( self ) :
		"""
		检查玩家是否处于活着状态，如果已经死去，则输出系统信息
		@rtype				: bool
		@return				: 玩家活着则返回真
		"""
		if not self.isAlive() :
			self.statusMessage( csstatus.ACCOUNT_STATE_DEAD )			# defined in RoleChat.py
			return False
		return True

	# ----------------------------------------------------------------
	def handleKeyEvent(self, isDown, key, mods ):
		"""
		处理按键事件
		"""

		if not self.vehicle == None:
			self.vehicle.handleKeyEvent( isDown, key, mods )
			# In this case, vehicle handles all input, otherwise we would
			# check return code and process if false (event not handled).
			return

	def onCameraDirChanged( self, direction ):
		"""
		相机方向改变通知。
		此调用来自CamerasMgr::CameraHandler::handleMouseEvent()，
		且只有BigWorld.player()的onCameraDirChanged()方法会被调用。
		设计此方法的目的是让相机视角（相机看的方向）改变时可以让PlayerEntity做一些需要的事情。
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return

		# 角色面向改变
		if not self.canChangeDirection(): return
		if not self.isMoving():
			BigWorld.dcursor().yaw = direction.yaw
			return

		# 飞行面向改变
		self.flyMove( direction )

		# 骑宠截获消息
		if self.vehicle:
			self.vehicle.onCameraDirChanged( direction )
			return

		Action.Action.onCameraDirChanged( self, direction )

	# ----------------------------------------------------------------
	def initSkillBox( self, skillIDs ):
		"""
		call in enterWorld method.
		初始化技能列表

		@param skills: like as [ skillID, ... ]
		"""
		self.skillList_ = list( skillIDs )
		for itemInfo in ItemsFactory().getActionSkillItems() :
			ECenter.fireEvent( "EVT_ON_PLAYERROLE_ADD_SKILL", itemInfo )
		for skillID in skillIDs :
			skill = skills.getSkill( skillID )
			if skill is None:continue
			itemInfo = SkillItemInfo( skill )
			ECenter.fireEvent( "EVT_ON_PLAYERROLE_ADD_SKILL", itemInfo )

	def initSpaceSkills( self, skillList, spaceType ):
		"""
		Define method.

		@param skillList: like as [ skillID, ... ]
		"""
		self.spaceSkillList = list( skillList )
		self.spaceSkillSpaceType = spaceType
		if self.inWorld:
			self.spaceSkillInitCompleted = True
			ECenter.fireEvent( "EVT_ON_ENTER_SPECIAL_COPYSPACE", skillList, spaceType )

	def hasSpaceSkill( self, skillID ):
		"""
		是否存在空间专属技能
		"""
		return skillID in self.spaceSkillList

	# -------------------------------------------------
	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		法术被中断（由服务器返回）
		@type reason: INT
		"""
		Role.spellInterrupted( self, skillID, reason )
		Attack.onSpellInterrupted( self, skillID, reason  )
		if not self.isAlive():
			return
		self.statusMessage( reason )

	# ----------------------------------------------------------------
	def testAddMoney( self, number ):
		"""
		@summary		:	测试钱到钱上限的数量
		@type	number	:	int32
		@param	number	:	钱的数量
		@rtype			:	int32
		@return			:	钱的差值，为正时表示钱大于上限，为负时表示钱小于上限
		"""
		return self.money + number - csconst.ROLE_MONEY_UPPER_LIMIT

	def ifMoneyMax( self ):
		"""
		判断玩家可携带的金钱是否已满
		"""
		return self.money >= csconst.ROLE_MONEY_UPPER_LIMIT

	# ----------------------------------------------------------------
	def testAddGold( self, number ):
		"""
		@summary		:	测试元宝到元宝上限的数量
		@type	number	:	int32
		@param	number	:	元宝的数量
		@rtype			:	int32
		@return			:	元宝的差值，为正时表示钱大于上限，为负时表示元宝小于上限
		"""
		return self.gold + number - csconst.ROLE_GOLD_UPPER_LIMIT

	def testAddSilver( self, number ):
		"""
		@summary		:	测试元宝到元宝上限的数量
		@type	number	:	int32
		@param	number	:	元宝的数量
		@rtype			:	int32
		@return			:	元宝的差值，为正时表示钱大于上限，为负时表示元宝小于上限
		"""
		return self.silver + number - csconst.ROLE_SILVER_UPPER_LIMIT

	# ----------------------------------------------------------------
	def onAddSkill( self, skillID ) :
		"""
		添加一个技能
		@type		skillID	: INT
		@param		skillID : 添加的技能的ID号
		@return				: None
		"""
		if skillID not in self.skillList_ :
			self.skillList_.append( skillID )
			sk = skills.getSkill( skillID )
			itemInfo = SkillItemInfo( sk )
			ECenter.fireEvent( "EVT_ON_PLAYERROLE_ADD_SKILL", itemInfo )

			tongSkillType = g_tongSkills.getSkillTypes()
			if skillID / 1000 not in tongSkillType:
				self.statusMessage( csstatus.SKILL_HAS_LEARNED, sk.getLevel(), sk.getName() )
			else:
				self.statusMessage( csstatus.TONG_SKILL_HAS_LEARNED, sk.getLevel(), sk.getName()  )
			# 学习技能光效（除去生活技能）
			if not lvcMgr.isLivingSkill( skillID ):
				self.playUpdateSkillEffect()

	def onRemoveSkill( self, skillID ) :
		"""
		移除一个技能
		@type		skillID	: INT
		@param		skillID : 要移除的技能ID号
		@return				: None
		"""
		if skillID in self.skillList_ :
			self.skillList_.remove( skillID )
		sk = skills.getSkill( skillID )
		itemInfo = SkillItemInfo( sk )
		Attack.onRemoveSkill( self, skillID )
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_REMOVE_SKILL", itemInfo )

	def onUpdateNormalSkill( self ):
		"""
		更新普通物理技能
		"""
		skID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		item = skills.getSkill( skID )
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_UPDATE_NORMAL_SKILL", skID, item )

	def onUpdateSkill( self, oldSkillID, newSkillID ) :
		"""
		更新一个技能
		@type		oldSkillID : INT
		@param		oldSkillID : 旧的技能 ID
		@type		newSkillID : INT
		@param		newSkillID : 新的技能 ID
		@return				   : None
		"""
		RoleUpgradeSkillInterface.onUpdateSkill( self, oldSkillID, newSkillID )
		for index, skillID in enumerate( self.skillList_ ) :
			if skillID == oldSkillID :
				self.skillList_[index] = newSkillID
				break
		sk = skills.getSkill( newSkillID )
		itemInfo = SkillItemInfo( sk )
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_UPDATE_SKILL", oldSkillID, itemInfo )
		self.statusMessage( csstatus.SKILL_HAS_LEARNED, sk.getLevel(), sk.getName() )
		# 升级技能光效
		self.playUpdateSkillEffect()

	def playUpdateSkillEffect( self ):
		"""
		播放学习/升级技能光效
		"""
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.UPDATE_SKILL_EFFECT, self.getModel(), self.getModel(), type, type )
		if effect:
			effect.start()

	def onUpdateSkill_2( self, oldSkillID, newSkillID ):
		"""
		更新一个技能 不带提示信息版本
		@type		oldSkillID : INT
		@param		oldSkillID : 旧的技能 ID
		@type		newSkillID : INT
		@param		newSkillID : 新的技能 ID
		@return				   : None
		"""
		for index, skillID in enumerate( self.skillList_ ) :
			if skillID == oldSkillID :
				self.skillList_[index] = newSkillID
				break
		sk = skills.getSkill( newSkillID )
		itemInfo = SkillItemInfo( sk )
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_UPDATE_SKILL", oldSkillID, itemInfo )

	def getSkillList( self ) :
		"""
		获取玩家的技能列表
		"""
		return self.skillList_[:]

	# -------------------------------------------------
	def intonate( self, skillID, intonateTime,targetObject ):
		"""
		Define method.吟唱法术
		@type 		skillID : INT
		"""
		Role.intonate( self, skillID, intonateTime, targetObject )
		Attack.intonate( self, skillID, intonateTime, targetObject )

		# 移动时中断当前法术施展:
		if self.isMoving() or self.isJumping():
			self.interruptAttack( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 )

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		正式施放法术——该起施法动作了
		@type 		skillID	 : INT
		@type 		targetID : [OBJECT_IDs]
		@type 		position : Math.Vector3
		"""
		Role.castSpell( self, skillID, targetObject )
		Attack.castSpell( self, skillID, targetObject )
		spell = skills.getSkill( skillID )

	def requestRemoveBuff( self, index ) :
		"""
		移除良性buff
		"""
		self.cell.requestRemoveBuff( index )

	def receiveSpell( self, casterID, skillID, damageType, damage ):
		"""
		Define method.
		接受技能处理

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  damageType: INT32
		@type	  damage: INT32
		"""
		spell = skills.getSkill( skillID )
		if spell.isMalignant():		#如果是恶性的
			Attack.onReceiveSpell( self, casterID, skillID, damageType, damage )
			if not rds.targetMgr.getTarget() and self.firstHit:
				target = BigWorld.entities.get( casterID )
				if target and target.getState() != csdefine.ENTITY_STATE_DEAD:
					rds.targetMgr.bindTarget( target )
				self.firstHit = False
		Role.receiveSpell( self, casterID, skillID, damageType, damage )

	def onStartHomingSpell( self, persistent ):
		"""
		define method.
		开始引导技能
		"""
		Role.onStartHomingSpell( self, persistent )
		Attack.onStartHomingSpell( self )

	def onFiniHomingSpell( self ):
		"""
		结束引导技能
		"""
		Role.onFiniHomingSpell( self )
		Attack.onFiniHomingSpell( self )
		ECenter.fireEvent( "EVT_ON_REFRESH_QBITEM" )  # CSOL-1380引导技能结束刷新快捷栏

	def canChangeDirection( self ):
		"""
		玩家是否能改变朝向
		"""
		if self.isDead(): return False
		if self.isInHomingSpell: return False
		if self.state != csdefine.ENTITY_STATE_FREE and self.state != csdefine.ENTITY_STATE_FIGHT	:
			return False  #只有自由和战斗状态能够右键改变角色的朝向
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		#中了昏睡、眩晕、定身等效果时不能右键改变玩家角色的朝向
		if self.effect_state & EffectState_list != 0: return False
		return True

	def startPickUp( self, dropBoxEntity ):
		"""
		玩家开始拾取。16:03 2009-3-9,wsf
		"""
		self.rotate( dropBoxEntity )
		dropBoxEntity.cell.queryDropItems()

	def stopPickUp( self ):
		"""
		停止拾取。16:03 2009-3-9，wsf
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_PICKUP_DISTURBED" )

	def stopPickUpQuestBox( self ):
		"""
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_QUEST_PICKUP_DISTURBED" )


	def rotate( self, entity ):
		"""
		转动方向。16:01 2009-3-9,wsf
		"""
		if self.id == entity.id:
			return
		new_yaw = ( entity.position - self.position ).yaw
		if abs( self.yaw - new_yaw ) > 0.0:
			self.turnaround( entity.matrix, None )


	def interruptAttackByServer( self, reason ):
		"""
		define method
		server 通知打断攻击行为
		"""
		self.interruptAttack( reason )

	# ----------------------------------------------------------------
	def set_actWord( self, old = 0):
		"""
		virtual method = 0;
		从服务器收到动作限制改变通知
		"""
		Role.set_actWord( self, old )
		if ( self.actWord ^ old ) & csdefine.ACTION_FORBID_MOVE :
			if not self.isSpanSpaceNavigate():
				self.stopMove()					# 改变了ACTION_FORBID_MOVE的状态，需要改变移动(有可能需要结束移动)
		if ( self.actWord ^ old ) & csdefine.ACTION_FORBID_TRADE :
			if self.tradeState == csdefine.TRADE_CHAPMAN:
				GUIFacade.endTradeWithNPC()
			if self.tradeState == csdefine.TRADE_SWAP:
				self.si_tradeCancel()
		if ( self.actWord ^old ) & csdefine.ACTION_FORBID_TALK:
			ECenter.fireEvent( "EVT_ON_ROLE_DEAD" )
		ECenter.fireEvent( "EVT_ON_ACTWORD_CHANGED", old, self.actWord )
		roles = self.entitiesInRange( csconst.ROLE_AOI_RADIUS, cnd = lambda ent : ent.getEntityType() == csdefine.ENTITY_TYPE_ROLE and ent.id != self.id )
		for role in roles:
			ECenter.fireEvent( "EVT_ON_ROLE_ACTWORD_CHANGED", role, old, self.actWord )

	def setPhysicsHoming( self, attackTargetDis, attackTrackDis, target ):
		"""
		连击技能真实位移动作播放之前设置Physics相关属性
		"""
		if self.id == target.id: return
		phy = self.getPhysics()
		if phy and target.matrix:
			if attackTargetDis > 0.0:
				phy.attackTargetDis = attackTargetDis
				phy.attackTrackDis = attackTrackDis
				phy.attackTargetMatrix = target.matrix
				self.turnaround( target.matrix )
			else:
				if hasattr( phy,"attackTargetMatrix" ):
					phy.attackTargetMatrix = None

	def resetPhysicsHomingEnd( self ):
		"""
		连击技能真实位移动作播放完毕设置Physics相关属性
		"""
		#连击技能动作结束后
		phy = self.getPhysics()
		if phy:
			if hasattr( phy, "attackTargetMatrix" ):
				phy.attackTargetMatrix = None
				phy.attackTargetDis = 0

	def onPlayActionStart( self, actionNames ):
		"""
		开始播放动作
		"""
		Role.onPlayActionStart( self, actionNames )
		if len( actionNames ) == 0: return
		atime = self.getModel().action( actionNames[0] ).duration
		# 动作限制
		if rds.spellEffect.checkActionLimit( actionNames[0] ):
			self.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_PLAY_ACTION )
			if self.actionCBID > 0:
				self.onActionTimeOver()
			self.actionCBID = BigWorld.callback( atime, self.onActionTimeOver )
		# 镜头跟随移动
		if rds.spellEffect.checkCameraFollowAction( actionNames[0] ):
			def cameraFollowActionStartDelay() :
				self.cameraFollowActionStart()
				if self.cameraFollowCBID > 0:
					self.cameraFollowActionOver()
				self.cameraFollowCBID = BigWorld.callback( atime, self.cameraFollowActionOver )

			# 延迟调用摄像机跟随的原因：当在骑乘状态下使用需要镜头跟随的技能时，这里直接调用会出现镜头大幅度向上偏移的问题。
			# 查的原因是此刻获取模型"HP_head"节点的位置为 0 的缘故，未知根本原因，这里只是暂时解决这个bug。
			BigWorld.callback( min( 0.1, atime ), cameraFollowActionStartDelay )


	def onPlayActionOver( self, actionNames ):
		"""
		动作播放结束
		"""
		Role.onPlayActionOver( self, actionNames )
		if len( actionNames ) == 0: return
		if actionNames[0] == self.homingAction:
			self.resetPhysicsHomingEnd()
			self.homingAction = None
		self.flushActionByKeyEvent()
		# 动作限制
		if rds.spellEffect.checkActionLimit( actionNames[0] ):
			if self.actionCBID > 0:
				self.onActionTimeOver()
		# 镜头跟随移动
		if rds.spellEffect.checkCameraFollowAction( actionNames[0] ):
			if self.cameraFollowCBID > 0:
				self.cameraFollowActionOver()

	def onActionTimeOver( self ):
		"""
		"""
		self.clearSourceControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_PLAY_ACTION )
		BigWorld.cancelCallback( self.actionCBID )
		self.actionCBID = 0

	def onModelChange( self, oldModel, newModel ):
		"""
		模型改变通知
		"""
		Role.onModelChange( self, oldModel, newModel )

		# 用于解决播放动作过程中模型改变产生的一些问题
		self.onModelChangeOver()

		if self.isJumpProcess and not self.vehicleModelNum:	# 正在跳跃中
			self.playActions( [Const.MODEL_ACTION_JUMP_AIR] )
		if self.vehicleModel:	# 下坐骑动作回调失败
			self.clearSourceControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE )
			self.inFlyDownPose = False
			if self.vehicleModel not in list( self.models ): return
			self.delModel( self.vehicleModel )
			self.vehicleModel = None
		# 副本指引
		self.disModelInNode()
		self.setFubenGuideYaw()

		# flora collision
		if oldModel:
			oldModel.floraCollision = False
		if newModel:
			newModel.floraCollision = True
			newModel.floraCollisionForce = 1.5


	def onUpdateRoleModel( self ):
		"""
		角色模型更新回调
		"""
		self.actionCount = 0	# 置空播放动作调用次数
		self.onModelChangeOver()

	def onModelChangeOver( self ):
		"""
		播放动作过程中模型改变回调
		"""
		if not self.inWorld: return
		actionNames = self.getActionNames()
		if len( actionNames ) == 0: return
		self.actionRule.onActionOver( actionNames )  # 置空当前播放动作列表，否则会导致后续某些动作播放不出来
		# 动作限制
		if rds.spellEffect.checkActionLimit( actionNames[0] ):
			if self.actionCBID > 0:
				self.onActionTimeOver()
		# 镜头跟随移动
		if rds.spellEffect.checkCameraFollowAction( actionNames[0] ):
			if self.cameraFollowCBID > 0:
				self.cameraFollowActionOver()
		self.flushActionByKeyEvent()

	# -------------------------------------------------
	def getEnergy( self ):
		"""
		获取跳跃能量值
		"""
		return self.energy

	def getEnergyMax( slef ):
		"""
		获取最大跳跃能量值
		"""
		return csdefine.JUMP_ENERGY_MAX

	def getEnergyReverValue( self ):
		"""
		获取跳跃能量值的自动恢复值
		"""
		return csdefine.ROLE_ENERGY_REVER_VALUE

	def getEXP( self ) :
		"""
		获取经验值
		"""
		return self.EXP

	def getEXPMax( self ) :
		"""
		获取当前等级的最大经验值
		"""
		return RoleLevelEXP.getEXPMax( self.level )

	def set_potential( self, oldValue ) :
		"""
		潜能
		"""
		dispersion = self.potential - oldValue
		if dispersion > 0:
			self.statistic["statPot"] += dispersion
		GUIFacade.onPotentialChanged( oldValue, self.potential )

	def set_HP( self, oldValue ):
		"""
		当 HP 改变时被调用
		"""
		Role.set_HP( self, oldValue )
		GUIFacade.onRoleHPChanged( oldValue, self.id, self.HP, self.HP_Max )
		#血量少时警告
		if rds.statusMgr.isCurrStatus( Define.GST_IN_WORLD ):
			if self.HP/( self.HP_Max * 1.0 ) <= Const.DANGER_HP:
				if self.MP/( self.MP_Max * 1.0 ) <= Const.DANGER_MP:
					ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
					ECenter.fireEvent( "EVT_ON_FLICKER_SCREEN", ( 255, 0, 0, 255 ) )
				else :
					ECenter.fireEvent( "EVT_ON_FLICKER_SCREEN", ( 255, 0, 0, 255 ) )
				return
			elif  self.MP/( self.MP_Max * 1.0 ) <= Const.DANGER_MP:
				ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
				ECenter.fireEvent( "EVT_ON_FLICKER_SCREEN", ( 0, 0, 255, 255 ) )
				return
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )

	def set_HP_Max( self, oldValue ):
		"""
		当 HP 最大值改变时被调用
		"""
		Role.set_HP_Max( self, oldValue )
		GUIFacade.onRoleHPChanged( oldValue, self.id, self.HP, self.HP_Max )
		attrChangeMgr.deliverAttrMsg( "HP_Max", [ oldValue, self.HP_Max ] )

	def set_MP( self, oldValue ):
		"""
		当 MP 改变时被调用
		"""
		Role.set_MP( self, oldValue )
		GUIFacade.onRoleMPChanged( oldValue, self.id, self.MP, self.MP_Max )
		#魔法值少时警告
		if rds.statusMgr.isCurrStatus( Define.GST_IN_WORLD ):
			if self.HP/( self.HP_Max * 1.0 ) <= Const.DANGER_HP: return
			if self.MP/( self.MP_Max * 1.0 ) <= Const.DANGER_MP:
				ECenter.fireEvent( "EVT_ON_FLICKER_SCREEN", ( 0, 0, 255, 255 ) )
				return
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )

	def set_MP_Max( self, oldValue ):
		"""
		当 MP 最大值改变时被调用
		"""
		Role.set_MP_Max( self, oldValue )
		GUIFacade.onRoleMPChanged( oldValue, self.id, self.MP, self.MP_Max )
		attrChangeMgr.deliverAttrMsg( "MP_Max", [ oldValue, self.MP_Max ]  )

	def set_level( self, oldValue ):
		"""
		当等级改变时被调用
		"""
		Role.set_level( self, oldValue )
		GUIFacade.onRoleLevelChanged( oldValue, self.getLevel() )
		self.refurbishAroundQuestStatus()
		if self.level > oldValue:
			self.statusMessage( csstatus.ACCOUNT_STATE_UPDATE_GRADE, self.getName(), self.level )
		rds.helper.courseHelper.roleUpgrade( self.level )

	def set_move_speed( self, speed ) :
		if self.move_speed <= 0.0:
			self.stopMove()
		self.updateMoveMode()
		pet = self.pcg_getActPet()
		if pet:
			pet.updateChaseSpeed()

	def set_teachCredit( self, oldValue ):	# 10:44 2008-8-21，wsf
		"""
		当功勋值改变时
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_CREDIT_CHANGED", self.teachCredit )

	def set_honor( self, oldValue ):
		"""
		角色荣誉值改变
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_HONOR_CHANGED", self.honor )

	def set_vim( self, oldValue ):
		"""
		角色活力值改变
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_VIM_CHANGED", self.vim )

	def set_energy( self, oldValue ):
		"""
		角色跳跃值改变
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_EN_CHANGED", self.energy, self.getEnergyMax() )

	def set_combatCount( self, oldValue ):
		"""
		角色格斗点值改变
		"""
		ECenter.fireEvent( "EVT_ON_COMBATCOUNT_CHANGED" )

	# -------------------------------------------------
	# 模型改变函数（ 用于在属性窗口中显示角色模型 ）
	# -------------------------------------------------
	def replacePartModel( self, model ):
		"""
		"""
		Role.replacePartModel( self, model )
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )

	def set_hairNumber( self, oldHairNumber = 0 ):
		"""
		"""
		Role.set_hairNumber( self, oldHairNumber )
		ECenter.fireEvent( "EVT_ON_ROLE_HAIR_CHANGED" )

	def set_righthandFDict( self, oldRHFDict = 0 ):
		"""
		"""
		Role.set_righthandFDict( self, oldRHFDict )
		ECenter.fireEvent( "EVT_ON_ROLE_RIGHTHAND_CHANGED" )

	def set_lefthandFDict( self, oldLHFDict = 0 ):
		"""
		"""
		Role.set_lefthandFDict( self, oldLHFDict )
		ECenter.fireEvent( "EVT_ON_ROLE_LEFTHAND_CHANGED" )

 #-----------------------------------------------------------

	def set_strength( self, oldValue ):
		"""
		力量
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_STRENGTH_CHANGE", self.strength )

	def set_dexterity( self, oldValue ):
		"""
		敏捷
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DEXTER_CHANGE", self.dexterity )

	def set_corporeity( self, oldValue ):
		"""
		体质
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_CORPORE_CHANGE", self.corporeity )

	def set_intellect( self, oldValue ):
		"""
		智力
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_INTELLECT_CHANGE", self.intellect )

	def set_damage_min( self, oldValue ):
		"""
		最小物理攻击
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MINDAMAGE_CHANGED", self.damage_min )
		oldDmg = ( oldValue + self.damage_max ) / 2
		newDmg = ( self.damage_min + self.damage_max ) / 2
		attrChangeMgr.deliverAttrMsg( "PHYSICS_DMG", [ oldDmg, newDmg ] )

	def set_damage_max( self, oldValue ):
		"""
		最大物理攻击
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAXDAMAGE_CHANGED", self.damage_max )
		oldDmg = ( oldValue + self.damage_min ) / 2
		newDmg = ( self.damage_min + self.damage_max ) / 2
		attrChangeMgr.deliverAttrMsg( "PHYSICS_DMG", [ oldDmg, newDmg ] )

	def set_magic_damage( self, oldValue ):
		"""
		法术攻击
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAGDAMAGE_CHANGED", self.magic_damage )
		attrChangeMgr.deliverAttrMsg( "MAGIC_DMG", [ oldValue, self.magic_damage ] )

	def set_armor( self, oldValue ):
		"""
		物理防御
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ARMOR_CHANGED", self.armor )
		attrChangeMgr.deliverAttrMsg( "PHYSICS_ARMOR", [ oldValue, self.armor ] )

	def set_magic_armor( self, oldValue ):
		"""
		法术防御
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAGARMOR_CHANGED", self.magic_armor )
		attrChangeMgr.deliverAttrMsg( "MAGIC_ARMOR", [ oldValue, self.magic_armor ] )

	def set_double_hit_probability( self, oldValue ):
		"""
		物理暴击率
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DOUBLE_DAM_CHANGED", self.double_hit_probability )

	def set_magic_double_hit_probability( self, oldValue ):
		"""
		法术暴击率
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAG_DOUBLE_CHANGED", self.magic_double_hit_probability )

	def set_hitProbability( self, oldValue ):
		"""
		物理命中率
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_HITTED_CHANGED", self.hitProbability )

	def set_magic_hitProbability( self, oldValue ):
		"""
		法术命中率
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAG_HITTED_CHANGED", self.magic_hitProbability )

	def set_dodge_probability( self, oldValue ):
		"""
		闪避
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DODGE_CHANGED", self.dodge_probability )

	def set_resist_hit_probability( self, oldValue ):
		"""
		招架
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RESIST_CHANGED", self.resist_hit_probability )

	def set_resist_giddy_probability( self, oldValue ):
		"""
		抵抗眩晕率
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RES_GIDDY_CHANGED", self.resist_giddy_probability )

	def set_resist_sleep_probability( self, oldValue ):
		"""
		抵抗昏睡率
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RES_SLEEP_CHANGED", self.resist_sleep_probability )

	def set_resist_fix_probability( self, oldValue ):
		"""
		抵抗定身率
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RES_FIX_CHANGED", self.resist_fix_probability )

	def set_resist_chenmo_probability( self, oldValue ):
		"""
		抵抗沉默率
		"""
		ECenter.fireEvent("EVT_ON_ROLE_RES_HUSH_CHANGED", self.resist_chenmo_probability )

	# ---------------------------------------
	def set_state( self, oldState = csdefine.ENTITY_STATE_FREE ):
		#if ( self.isInSpelling() ) and ( oldState == ENTITY_STATE_FIGHT ):
		#	return
		Role.set_state( self, oldState )

		if oldState == csdefine.ENTITY_STATE_FIGHT and self.state != csdefine.ENTITY_STATE_FIGHT:
			BigWorld.callback( 1.0, Functor( self.statusMessage, csstatus.ROLE_BREAK_FIGHT ) )
			ECenter.fireEvent( "EVT_ON_SHOW_FIGHTFIRE", False )
			self.antoRunConjureVehicle()	# 自动骑乘功能
			rds.soundMgr.stopFightMusic()
			self.setGuideModelVisible( True ) # 副本指引
		elif oldState != csdefine.ENTITY_STATE_FIGHT and self.state == csdefine.ENTITY_STATE_FIGHT:	#如果切入战斗状态
			self.statusMessage( csstatus.ROLE_BEGIN_FIGHT )
			self.firstHit = True
			ECenter.fireEvent( "EVT_ON_SHOW_FIGHTFIRE", True)
			self.stopPickUp()
			rds.soundMgr.playFightMusic()	# 战斗背景音乐
			self.setGuideModelVisible( False ) # 副本指引
		elif oldState == csdefine.ENTITY_STATE_QUIZ_GAME:
			self.quiz_reset()
		elif oldState == csdefine.ENTITY_STATE_PICK_ANIMA: #拾取灵气
			self.pickAnima_stop()
			self.__bindShortcuts()
			self.__moveForward( False )

		if self.state == csdefine.ENTITY_STATE_DEAD:		# 如果角色死亡，则关闭拾取/延迟传送界面
			self.stopPickUp()
			self.delayTeleportIsFail = True
			UnitSelect().hideMoveGuider()
			ECenter.fireEvent( "EVT_ON_HIDE_SPE_OCBOX" )
		elif self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			self.quiz_enterGameState()
		elif self.state == csdefine.ENTITY_STATE_PICK_ANIMA:
			self.pickAnima_start()
			self.__unbindShortcuts()
			rds.shortcutMgr.setHandler( "ACTION_TURN_LEFT", self.__handleKeyEvent )			# move leftward
			rds.shortcutMgr.setHandler( "ACTION_TURN_RIGHT", self.__handleKeyEvent )		# move rightward
			BigWorld.callback( 1, Functor( self.__moveForward, True ) )

		if oldState == csdefine.ENTITY_STATE_DEAD and self.state == csdefine.ENTITY_STATE_FREE :	# 如果角色活过来了
			if self.currentShowMessage :
				self.currentShowMessage.dispose()
			ECenter.fireEvent( "EVT_ON_HIDE_REVIVE_BOX" )
		if self.state != csdefine.ENTITY_STATE_FIGHT:
			ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "cityWarer", False )

		rds.areaEffectMgr.startSpaceEffect( self )		# 角色状态改变触发场景光效
		ECenter.fireEvent( "EVT_ON_ROLE_STATE_CHANGED", self.state )


	def set_effect_state( self, oldEState = 0 ):
		"""
		玩家效果状态
		"""
		Role.set_effect_state( self, oldEState )
		if self.effect_state & csdefine.EFFECT_STATE_FOLLOW:
			self.team_startFollow()
			self.__unbindShortcuts()
			ECenter.fireEvent( "EVT_ON_FOLLOW_STATE_CHANGE" )
		elif oldEState & csdefine.EFFECT_STATE_FOLLOW:
			self.team_stopFollow()
			self.__bindShortcuts()
			ECenter.fireEvent( "EVT_ON_FOLLOW_STATE_CHANGE" )
		elif self.effect_state & csdefine.EFFECT_STATE_LEADER or oldEState & csdefine.EFFECT_STATE_LEADER:
			ECenter.fireEvent( "EVT_ON_FOLLOW_STATE_CHANGE" )
		elif self.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:	#免战状态
			self.refurbishAroundRoleHPColor()

	def set_pkState( self, oldpkstate = csdefine.PK_STATE_PEACE ):
		"""
		pk状态改变
		"""
		Role.set_pkState( self, oldpkstate )
		#pk状态改变通知自己
		ECenter.fireEvent( "EVT_ON_ROLE_PKSTATE_CHANGED", self.pkState )

	def set_isPkModelock( self, oldValue ):
		"""
		pk状态改变
		"""
		#pk状态改变通知自己
#		self.cell.setPkMode( self.pkMode )
		ECenter.fireEvent( "EVT_ON_ROLE_IS_PKMODE_LOCK", oldValue, self.isPkModelock )

	def set_pkValue( self, oldValue ):
		"""
		pk值改变
		"""
		#pk值改变通知
		ECenter.fireEvent( "EVT_ON_ROLE_PKVALUE_CHANGED", self.pkValue )

	def set_pkMode( self, oldValue ):
		"""
		pk模式改变
		"""
		Role.set_pkMode( self, oldValue )
		msg = Const.PK_MODEL_MSG_MAPS.get( self.pkMode )
		if msg is None: return
		self.statusMessage( csstatus.ROLE_PK_MODE_CHANGE, msg )
		self.refurbishAroundRoleHPColor()

	def refurbishAroundRoleHPColor( self ):
		"""
		更新周围玩家的血条颜色
		"""
		roles = self.entitiesInRange( csconst.ROLE_AOI_RADIUS, \
		cnd = lambda ent : ent.getEntityType() == csdefine.ENTITY_TYPE_ROLE \
		and ent.id != self.id )
		for role in roles:
			if hasattr( role, "refurbishHPColor" ):
				role.refurbishHPColor()

	def set_sysPKMode( self, oldValue ):
		"""
		pk模式改变
		"""
		Role.set_sysPKMode( self, oldValue )

	# -------------------------------------------------
	# 元素属性值发生变化
	# -------------------------------------------------
	def set_elem_huo_damage( self, oldValue ) :
		"""
		火元素伤害发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_FIRE_DAMAGE_CHANGED", self.elem_huo_damage )

	def set_elem_huo_derate_ratio( self, oldValue ) :
		"""
		火元素抗性发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_FIRE_DERATE_RATIO_CHANGED", self.elem_huo_derate_ratio )

	def set_elem_xuan_damage( self, oldValue ) :
		"""
		玄元素伤害发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_XUAN_DAMAGE_CHANGED", self.elem_xuan_damage )

	def set_elem_xuan_derate_ratio( self, oldValue ) :
		"""
		玄元素抗性发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_XUAN_DERATE_RATIO_CHANGED", self.elem_xuan_derate_ratio )

	def set_elem_lei_damage( self, oldValue ) :
		"""
		雷元素伤害发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_THUNDER_DAMAGE_CHANGED", self.elem_lei_damage )

	def set_elem_lei_derate_ratio( self, oldValue ) :
		"""
		雷元素抗性发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_THUNDER_DERATE_RATIO_CHANGED", self.elem_lei_derate_ratio )

	def set_elem_bing_damage( self, oldValue ) :
		"""
		冰元素伤害发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_ICE_DAMAGE_CHANGED", self.elem_bing_damage )

	def set_elem_bing_derate_ratio( self, oldValue ) :
		"""
		冰元素抗性发生变化
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_ICE_DERATE_RATIO_CHANGED", self.elem_bing_derate_ratio )

	def set_posture( self, oldValue ) :
		"""
		姿态改变
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_POSTURE_CHANGED", self.posture, oldValue )

	def set_range( self, oldValue ) :
		"""
		攻击距离改变
		"""
		self.onUpdateNormalSkill()

	# -------------------------------------------------
	def onMoveChanged( self, isMoving ) :
		"""
		移动状态改变回调
		"""
		Attack.onMoveChanged( self, isMoving )
		self.stopPickUp()
		if self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			self.stopDance()	# 停止跳舞
		if self.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:
			self.cell.stopRequestDance()	# 停止邀请跳舞，取消邀请
		if len( self.tempFace ) != 0 :			# 停止播放表情动作
			self.cell.stopFaceAction( self.tempFace )
		self.interuptPendingBuff()

	def onAssaultStart( self ):
		"""
		开始冲锋
		原名为：onMovetoProtect，现重命名为 onAssaultStart( hyw--09.01.12 )
		"""
		self.__unbindShortcuts()						# 屏蔽方向键
		self.__isAssaulting = True						# 设置为冲锋状态
		self.updateMoveMode()

	def onAssaultEnd( self ) :
		"""
		defined method
		结束冲锋
		注意：冲锋结束后，该方法会被调用两次：一次是服务器的冲锋回调，一次是客户端自己检查冲锋时间到后回调
			  但不能保证哪个先调用，后面那次调用将会被 self.__isAssaulting 为 False 返回而不做事
			  这样做是不对的，但这是为了减少冲锋后，角色会走过头的问题，确保冲锋结束后，马上将角色移动停止下来
		hyw--09.01.12
		"""
		self.__isAssaulting = False
		self.__bindShortcuts()							# 解蔽方向键
		self.stopMove()

	def onStateChanged( self, old, new ) :
		"""
		virtual method.
		状态切换。
		@param old	:	更改以前的状态
		@type old	:	int
		@param new	:	更改以后的状态
		@type new	:	int
		"""
		self.actionState = new
		Role.onStateChanged( self, old, new )
		Attack.onStateChanged( self, old, new )
		#死去
		if new == csdefine.ENTITY_STATE_DEAD :
			# 在死亡时，应该复位操作模式
			self.c_control_mod = Const.CAMERA_CONTROL_MOD_1

			#if old == csdefine.ENTITY_STATE_FIGHT:
			# 清除任何方向上可能有的速度
			self.stopMove()

			# 如果掉落过程中碰到了什么东西，那么停止掉落
			if self.isOnSomething():
				DEBUG_MSG( "Corpse hit something, stop falling!" )
				self.physics.fall = False
			# else:
				# 说明此时还在掉落，不做任何处理，当玩家掉到某个表面，__onFallToGround会自动关闭掉落
				# 从而避免掉落到某些表面上会出现的镜头剧烈闪烁的问题 by mushuang

			if self.isJumping():	#如果死的时候是跳跃状态，让其死在地面
				self.physics.fall = True

			BigWorld.callback( 2.0, self.pointReviveClew )
		elif new == csdefine.ENTITY_STATE_FREE and old ==  csdefine.ENTITY_STATE_DEAD:
			self.physics.fall = True	#复活之后要设置允许下落 spf
			# 将操作模式复位
			self.c_control_mod = Const.CAMERA_CONTROL_MOD_2
			self.__flyingVehicle.resetDeathDepthReached()				# 重置死亡掉落

	def onPkStateChange( self, old, new ):
		"""
		virtual method.
		状态切换。
		@param old	:	更改以前的状态
		@type old	:	int
		@param new	:	更改以后的状态
		@type new	:	int
		"""
		#do something
		pass

	def pointReviveClew( self ):
		"""
		复活点复活提示
		"""
		if self.state != csdefine.ENTITY_STATE_DEAD:
			return

		self.stopMove()

		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_TONG_ABA:
			self.tong_onTongAbaDie()
			return

		if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
			self.tong_onCityWarDie()
			return

		if spaceType == csdefine.SPACE_TYPE_TEAM_COMPETITION:
			return

		if spaceType == csdefine.SPACE_TYPE_ROLE_COMPETITION:
			return

		if spaceType == csdefine.SPACE_TYPE_TEAM_CHALLENGE:
			self.teamChallengeDied()
			return

		if spaceType == csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI:
			return

		if self.findBuffByBuffID( "099021" ) != None:
			self.useFengHuangYin()
			return

		if self.__flyingVehicle.isDeathDepthReached() :
			ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX_ON_FALLING_DOWN" ) # 高空跌落而死时，复活选项中无“原地复活”
			DEBUG_MSG( "Fall off to die!" )
			return

		if spaceType == csdefine.SPACE_TYPE_TONG_COMPETITION:
			return

		if spaceType == csdefine.SPACE_TYPE_TONG_TURN_WAR:
			return

		if spaceType == csdefine.SPACE_TYPE_CAMP_TURN_WAR:
			return

		if spaceType == csdefine.SPACE_TYPE_JUE_DI_FAN_JI:
			return

		if spaceType == csdefine.SPACE_TYPE_AO_ZHAN_QUN_XIONG:
			return

		ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )

	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND

		if entity.isDead():
			return csdefine.RELATION_NOFIGHT


		if isFlying( self ):
			return csdefine.RELATION_NOFIGHT

		if self.isQuestMonster( entity ):
			return csdefine.RELATION_FRIEND

		# 全体免战判定
		if self.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
			entity.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT

		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_GUARD ) and self.pkState != csdefine.PK_STATE_REDNAME:
			return csdefine.RELATION_FRIEND

		if self.isUseCombatCamp and entity.isUseCombatCamp:
			entity = entity.getRelationEntity()
			if entity:
				combatConstraint = self.queryGlobalCombatConstraint( entity )
				if combatConstraint != csdefine.RELATION_NONE:
					return combatConstraint
				else:
					relation = self.queryCombatRelation( entity )
					if relation == csdefine.RELATION_NEUTRALLY:
						if self.canPk( entity ):
							return csdefine.RELATION_ANTAGONIZE
						else:
							return csdefine.RELATION_FRIEND
					else:
						return relation
			else:
				return csdefine.RELATION_FRIEND

		# it's monster
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			if entity.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ):
				return csdefine.RELATION_FRIEND
			elif entity.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
				return csdefine.RELATION_FRIEND
			elif entity.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE_2 ):
				return csdefine.RELATION_FRIEND
			elif entity.hasFlag( csdefine.ENTITY_FLAG_FRIEND_ROLE ):
				return csdefine.RELATION_FRIEND
			elif entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				pid = entity.ownerVisibleInfos[ 0 ]
				tid = entity.ownerVisibleInfos[ 1 ]
				if pid == self.id or tid == self.teamID:
					return csdefine.RELATION_ANTAGONIZE
				else:
					return csdefine.RELATION_NOFIGHT
			# 友好阵营列表判断
			sCamp = self.getCamp()
			tCamp = entity.getCamp()
			if ( sCamp == tCamp ) or ( sCamp in entity.friendlyCamps ) or ( tCamp in self.friendlyCamps ):
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_TONG_NAGUAL ):
			if self.tong_dbID in entity.enemyTongDBIDList:
				return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
			if entity.ownerID == self.id:
				return csdefine.RELATION_FRIEND
			return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_TREASURE_MONSTER ):
			return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ):
			if self.tong_dbID == entity.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_XIAN_FENG ) or entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_ALTAR ) or \
			entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_TOWER ) or entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_BASE_TOWER ):
			if self.getCamp() == entity.ownCamp:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_XIAN_FENG ) or entity.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_ALTAR ) or \
			entity.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_TOWER ) or entity.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER ):
			if self.tong_dbID == entity.ownTongDBID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ):
			if entity.belong == self.teamID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		if entity.isEntityType( csdefine.ENTITY_TYPE_YAYU ):
			return csdefine.RELATION_FRIEND

		# 帮会夺城战决赛
		if entity.utype == csdefine.ENTITY_TYPE_CITY_WAR_FINAL_BASE:
			if entity.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ):
				return csdefine.RELATION_FRIEND
			elif entity.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
				return csdefine.RELATION_FRIEND
			elif entity.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE_2 ):
				return csdefine.RELATION_FRIEND
			elif entity.hasFlag( csdefine.ENTITY_FLAG_FRIEND_ROLE ):
				return csdefine.RELATION_FRIEND
			elif entity.belong == self.getCityWarTongBelong( self.tong_dbID ):
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		# 对手是宠物
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = entity.getOwner()
			if owner is None:
				return csdefine.RELATION_NOFIGHT
			else:
				entity = owner

		# 对手是人，切磋判定
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self.qieCuoTargetID == entity.id:
				return csdefine.RELATION_ANTAGONIZE

		# 免战判定
		if self.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT

		if self.canPk( entity ):
			return csdefine.RELATION_ANTAGONIZE
		else:
			return csdefine.RELATION_FRIEND

	def queryGlobalCombatConstraint( self, entity ):
		"""
		查询全局战斗约束
		"""
		# 观察者模式
		if self.effect_state  & csdefine.EFFECT_STATE_WATCHER:
			return csdefine.RELATION_NOFIGHT

		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND

		if self.state == csdefine.ENTITY_STATE_PENDING:
			return csdefine.RELATION_NOFIGHT

		if self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return csdefine.RELATION_NOFIGHT

		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_GUARD ) and self.pkState != csdefine.PK_STATE_REDNAME:
			return csdefine.RELATION_FRIEND

		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_FRIEND_ROLE ): #怪物对玩家绝对友好标志
			return csdefine.RELATION_FRIEND
		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_SPEAKER ):
			return csdefine.RELATION_FRIEND
		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
			return csdefine.RELATION_FRIEND
		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE_2 ):
			return csdefine.RELATION_FRIEND

		if entity.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
			if self.pkState == csdefine.PK_STATE_PROTECT:
				return csdefine.RELATION_FRIEND

		if entity.state == csdefine.ENTITY_STATE_PENDING:
			return csdefine.RELATION_NOFIGHT
		if entity.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return csdefine.RELATION_NOFIGHT
		if self.state == csdefine.ENTITY_STATE_RACER:											#赛马状态，返回友好
			return csdefine.RELATION_FRIEND

		# 免战
		if self.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT

		# 全体免战判定
		if self.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
			entity.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT

		return csdefine.RELATION_NONE

	def refurbishAroundQuestStatus( self ):
		"""
		更新周围NPC的任务状态
		"""
		for key, entity in BigWorld.entities.items():
			if hasattr( entity, "refurbishQuestStatus" ):
				entity.refurbishQuestStatus()

	# -------------------------------------------------
	def __queryGossipTarget( self, className ):
		"""
		自动寻路/引路蜂传送结束后根据ID查找目标NPC
		gjx 2009.02.18
		@type		className	: str
		@param		className	: 自动寻路目标NPC的ID
		@rtype					: entity
		"""
		targetList = []
		for entity in BigWorld.entities.values():
			if hasattr( entity, 'className' ) and \
			entity.className == className and \
			rds.targetMgr.isDialogicTarget( entity ):						# 是可对话目标
				targetList.append( entity )
		if len( targetList ) <= 0: return None
		t1 = targetList.pop()
		pos = self.position
		while targetList:
			t2 = targetList.pop()
			if pos.distTo( t1.position ) > pos.distTo( t2.position ):		# 查找距离玩家最近的NPC
				t1 = t2
		return t1

	def talkWithTarget( self, className ):
		"""
		与目标对话，同时将目标绑定为当前目标，自动寻路/引路蜂传送结束后调用
		gjx 2009.02.18
		@param		className	: 目标的ID，与entity.className属性对应
		@type		className	: str
		"""
		retryTime = 6									# 尝试查找的次数
		def delayTalk( retryTime ) :					# 找不到时延时一段时间继续找
			if retryTime < 1 : 							# 使用这个方法是因为很多情况下NPC都来不及刷新
				INFO_MSG( "Can't find gossip target by ID:%s!" % className  )
				return
			target = self.__queryGossipTarget( className )
			if target is not None :
				rds.targetMgr.talkWithTarget( target )	# 对话
			else :
				BigWorld.callback( 0.5, Functor( delayTalk, retryTime - 1 ) )
		delayTalk( retryTime )

	def onUseFlyItem( self ):
		"""
		define method.
		使用引路蜂回调
		"""
		self.delayTeleportIsFail = True
		ECenter.fireEvent( "EVT_ON_HIDE_SPE_OCBOX" )

	def getExpectTarget( self ):
		"""
		获取将要与我对话的 NPC 的 className
		"""
		return self.__expectTarget

	def setExpectTarget( self, className ) :
		"""
		设置将要与我对话的 NPC 的 className( 需要寻路或者 teleport 到达目标才能真正与其对话 )
		"""
		self.__expectTarget = className

	def onBeforeAutoRun( self ):
		"""
		自动寻路之前做的一些事情
		"""
		self.stopAutoFight()

	def onStartAutoRun( self, position ):
		"""
		开始自动寻路
		"""
		Action.Action.onStartAutoRun( self, position )
		if self.onWaterArea and self.onWaterJumpTimer is None:	# 如果刚好处于水域中，则开启水面跳跃回调
			self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )
		ECenter.fireEvent( "EVT_ON_START_AUTORUN", position )

		# 自动骑乘功能
		self.antoRunConjureVehicle()

	def antoRunConjureVehicle( self ):
		"""
		自动寻路自动骑乘功能
		"""
		if not self.inWorld: return
		# 判断是否在自动寻路状态下
		if not self.isActionState( Action.ASTATE_NAVIGATE ): return
		# 判断是否在战斗状态下
		if self.state == csdefine.ENTITY_STATE_FIGHT: return
		# 判断是否在水域
		if self.onWaterArea: return
		# 判断是否有激活骑宠
		if not self.activateVehicleID: return
		# 判断是否已经在骑乘状态
		if self.vehicleModelNum: return

		self.conjureVehicle( self.activateVehicleID )

	def onEndAutoRun( self, state ):
		"""
		寻路结束时被调用
		"""
		Action.Action.onEndAutoRun( self, state )
		if self.isMoving():		# 停止当前移动
			self.stopMove()
		if self.onWaterJumpTimer is not None:	# 自动寻路结束停止水面跳跃回调
			BigWorld.cancelCallback( self.onWaterJumpTimer )
			self.onWaterJumpTimer = None
		ECenter.fireEvent( "EVT_ON_STOP_AUTORUN", state )
		if state and self.__expectTarget != "":
			self.talkWithTarget( self.__expectTarget )
		self.__expectTarget = ""

	def getAutoRunPathLst( self ):
		"""
		获取自动寻路的路径节点列表
		"""
		if self.vehicle:
			return self.vehicle.getAutoRunPathLst()
		return Action.Action.getAutoRunPathLst( self )

	def getAutoRunGoalPosition( self ):
		"""
		获取自动寻路的目标位置
		"""
		if self.vehicle:
			return self.vehicle.getAutoRunGoalPosition()
		return Action.Action.getAutoRunGoalPosition( self )

	# ----------------------------------------------------------------
	# 玩家进入离开空间
	# ----------------------------------------------------------------
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
		#------------------------------跟随一个玩家移动----------------
	def autoFollow(self, targetID ):
		"""
		跟随一个玩家移动
		tidy up by huangyongwei -- 2008.12.24
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return

		if targetID == self.id : return 							# 对自己不会出现跟随的选项,加入这个判断只是为了严谨.
		target = BigWorld.entities.get( targetID )
		if not target:
			return
		lenth = self.position.flatDistTo( target.position ) 		# 计算玩家与目标的距离
		if lenth > 20.0 : 											# 如果距离超过20米 提示距离过远 不能跟随
			self.statusMessage( csstatus.FOLLOW_FAILD_FAR )
			return

		self.setActionState( Action.ASTATE_FOLLOW )				# 人物的移动方式修改为跟随移动
		if self.vehicle:
			self.vehicle.setActionState( Action.ASTATE_FOLLOW )
		self.checkFollowing( targetID )

	def getSpeed( self ):
		"""
		PlayerRole层统一接口,获取速度
		"""
		if self.vehicle:
			return self.vehicle.getSpeed()
		else:
			return Action.Action.getSpeed( self )

	def checkFollowing( self, targetID ):
		"""
		回调函数,用于检测是否需要向目标移动以及是否超出范围,停止移动
		"""
		BigWorld.cancelCallback( self.__followCallBack )
		target = BigWorld.entities.get( targetID )
		if not target :
			return										# 如果目标不存在
		position = target.position
		lenth = self.position.flatDistTo( target.position )			# 计算玩家与目标的距离
		if lenth > Const.ROLE_FOLLOW_MAX_DISTANCE : return 									# 如果距离大于20米了 取消跟随

		if not self.allowMove():									# 如果目前不允许移动
			return

		if self.vehicle and not self.vehicle.isActionState( Action.ASTATE_FOLLOW ):
			return
		elif not self.isActionState( Action.ASTATE_FOLLOW ): 	# 如果破坏掉了跟随状态 那么取消跟随
			return

		if lenth - 0.2 * self.getSpeed() < Const.ROLE_FOLLOW_NEAR_DISTANCE:					# 如果下一次检测时已经跑到小于目标1.0米处,现在就停下
			self.stopMove() 									# 停止移动
			self.__followCallBack = BigWorld.callback( 0.2, Functor( self.checkFollowing, targetID ) )
			return
		else:   #计算离目标较近位置，不至于和目标完全重合 add by wuxo
			disRate = (lenth - Const.ROLE_FOLLOW_NEAR_DISTANCE)/Const.ROLE_FOLLOW_NEAR_DISTANCE
			posX = (self.position[0] + disRate*position[0])/(1+disRate)
			posY = (self.position[1] + disRate*position[1])/(1+disRate)
			posZ = (self.position[2] + disRate*position[2])/(1+disRate)
			position = Math.Vector3(posX,posY,posZ)

		if self.getState() == csdefine.ENTITY_STATE_DEAD:			# 只有死亡后 才会添加此标记 所以这里就是判断是否
			return

		self.moveTo( position, None )			# 跟随过去
		self.__followCallBack = BigWorld.callback( 0.2, Functor( self.checkFollowing, targetID ) )

	def getSpaceLabel( self ) :
		"""
		infact it the english name of current space
		"""
		try :
			return BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		except :
			return None

	def getSpaceFolder( self ) :
		"""
		the folder of current space's config locates
		"""
		try :
			spaceData = BigWorld.getSpaceDataFirstForKey( self.spaceID, 1 )
			return spaceData.split( "/" )[-1]
		except :
			return None

	def getCurrentSpaceType( self ):
		"""
		获取当前所在space的类型 具体看csdefine.SPACE_TYPE_*
		"""
		try:
			return int( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) )
		except ValueError:
			return csdefine.SPACE_TYPE_NORMAL

	def getCurrWholeArea( self ) :
		return rds.mapMgr.getWholeArea( self.getSpaceLabel(), self.position[1] )

	def getCurrArea( self ) :
		return rds.mapMgr.getArea( self.getSpaceLabel(), self.position )

	def getWholeAreaBySpaceLabel( self, spaceLabel ):
		return rds.mapMgr.getWholeArea( spaceLabel, self.position[1] ).fullName

	# -------------------------------------------------
	def planeSpacePrepare( self ):
		"""
		Define method.
		位面传送将要开始。
		"""
		DEBUG_MSG( "ready." )
		BigWorld.planeSpacePrepare()
		self.parallelSpaceID = self.spaceID

	def onLeaveSpaceForPlane( self ):
		"""
		玩家离开space回调，告诉玩家将要离开一个space，进入的将是一个位面。
		此函数由引擎底层直接调用。
		"""
		DEBUG_MSG( "old plane space:", self.spaceID )
		rds.targetMgr.unbindTarget()
		self.team_leaveSpace()
		self.parallelSpaceID = -1
		ECenter.fireEvent("EVT_ON_LEAVE_PLANE")

	def onEnterPlane( self ):
		"""
		玩家进入位面的回调，告诉玩家进入了一个新space位面。
		此函数由引擎底层直接调用。
		"""
		DEBUG_MSG( "enter plane space:", self.spaceID )
		self.team_enterSpace()
		RoleQuestInterface.onEnterSpace_( self )
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_WM:
			ECenter.fireEvent("EVT_ON_ENTER_PLANE")

	def onLeaveSpace( self ):
		"""
		玩家离开space回调，告诉玩家将要离开一个space。
		此函数由引擎底层直接调用。
		注意：此回调在entity退出时（如：从 PlayerRole 切换 Account）不被调用。
		"""
		self.emptyDirection()
		self.stopAutoFight()			# 进行空间传送时停止自动打怪(里面调用了stopMove()) 2008-11-5 gjx
		rds.targetMgr.unbindTarget()
		self.team_leaveSpace()
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		BigWorld.clearDecals()
		rds.gameMgr.onLeaveSpace()
		self.disableFlyingRelatedDetection()          # 空间传送读条过程中关闭场景边界碰撞，解决传送过慢的问题
		rds.gameSettingMgr.onPlayerLeaveSpace()				# 恢复地图的游戏自定义配置
		self.levelYXLMChangeCamera()
		# 离开位面通知
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_WM:
			ECenter.fireEvent("EVT_ON_LEAVE_PLANE")

	def onEnterSpace( self ):
		"""
		玩家进入space的回调，告诉玩家进入了一个新space。
		此函数由引擎底层直接调用。
		注意：此接口在第一次进入游戏时不被调用。
		"""
		if isPublished:
			BigWorld.callback( 1.0, checkCurrentSpaceData )
		def func():
			BigWorld.dcursor().yaw = BigWorld.player().yaw
		BigWorld.callback( 0.2, func ) # dcursor().yaw会定时改变player().yaw，所以player().yaw未被其改变前同化dcursor().yaw，防止角色传送之后面向不对
		self.emptyDirection()
		if hasattr( self.physics, "fall" ):
			self.physics.fall = False
		if self.isJumping():
			self.physics.stop()
#			self.physics.fall = True
		self.team_enterSpace()
		self.stopMove()
		ECenter.fireEvent( "EVT_ON_PLAYER_ENTER_SPACE" )
		rds.gameSettingMgr.onPlayerEnterSpace()				# 应用地图的游戏自定义配置
		RoleQuestInterface.onEnterSpace_( self )

	def onEnterArea( self, newArea ) :
		"""
		当玩家进入某个区域时被调用
		"""
		if self._oldArea is not None and self._oldArea == newArea:
			sn = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NUMBER )
			if sn == self._oldSpaceNumber:
				return
			self._oldSpaceNumber = sn
		else:
			# 繁体版开启TimeOfDay功能
			if Language.LANG == Language.LANG_BIG5:
				rds.enEffectMgr.updateTime()
			else:
				try:
					curWholeArea = self.getCurrWholeArea()
					curWholeArea.setTimeOfDay()
				except Exception, err:
					ERROR_MSG( err )
			rds.areaEffectMgr.onAreaChange( self, self._oldArea, newArea )
			self._oldArea = newArea
			spaceName = BigWorld.getSpaceName( self.spaceID )
			canPlaySpaceCamera = False
			for questID in self.currentDoingQuestIDList :
				data = questConfig.get( ( spaceName, questID ), None )
				if data:
					canPlaySpaceCamera = True
			if not canPlaySpaceCamera:
				rds.soundMgr.switchMusic( newArea.getMusic() )		# 背景音乐
				rds.soundMgr.switchBgEffect( newArea.getBgSound() )	# 背景音效
				self.statusMessage( csstatus.YOU_HAVE_COME_IN, newArea.name )
		ECenter.fireEvent( "EVT_ON_ROLE_ENTER_AREA", newArea )

	def onEnterAreaFS( self ) :
		"""
		defined method.
		当进入某个区域时被触发( 同地图的区域跳转时被触发 )
		hyw -- 2008.10.08
		"""
		BigWorld.dcursor().yaw = BigWorld.player().yaw # dcursor().yaw会定时改变player().yaw，所以player().yaw未被其改变前同化dcursor().yaw，防止角色传送之后面向不对
		self.emptyDirection()
		self.team_enterSpace()
		newArea = self.getCurrArea()
		self.onEnterArea( newArea )

	def onLeaveAreaFS( self ) :
		"""
		defined method.
		当离开某个区域时被触发( 同地图的区域跳转时被触发 )
		hyw -- 2008.10.08
		"""
		if not rds.statusMgr.isInWorld() :
			return						# 某些情况下，服务器会在角色登陆过程中将角色传送到某个位置
		self.emptyDirection()
		self.stopAutoFight()			# 进行区域传送时停止自动打怪 2008-11-5 gjx
		self.stopPickUp()				# 进行区域传送时关闭拾取界面
		self.team_leaveSpace()
		rds.targetMgr.unbindTarget()	# 传送时取消选择当前目标
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		rds.gameMgr.onLeaveArea()

	def beforeEnterDoor( self ):
		"""
		进入传送门之前需要做一些事情。。。
		"""
		if self.__expectTarget != "":
			self.__spanSpaceTarget = self.__expectTarget				# 临时保存，防止过传送门后被清空
		self.__spanSpaceDataLock = True
		self.stopMove()

	def canSelectTarget( self, target ):
		return target.canSelect()

	def onLoginSpaceIsFull( self ):
		"""
		define method.
		登陆到某场景， 场景满员了
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.disconnect()
		# "你所登录的场景已经满员了，请稍后登陆。"
		showMessage( 0x0124, "", MB_OK, query )

	def delayTeleport( self, skill, caster, spaceName, pos, npcName, delayTime ):
		"""
		延迟传送
		"""
		if skill is None: return
		if caster is None: return
		if delayTime < 0: return
		ECenter.fireEvent( "EVT_ON_HIDE_SPE_OCBOX" )  # 隐藏前面的界面
		def teleport( id ):
			if id == RS_SPE_OK:
				result = True
			else:
				result = False
			self.atonceTeleport( spaceName, pos, result )
		self.delayTeleportNpc = caster
		self.delayTeleportTime = delayTime
		self.delayTeleportIsFail = False	# 先默认为可以传送
		# "我将施展%s将您传送到%s处，准备好了吗? "
		msg =  mbmsgs[0x012d] % ( skill.getName(), npcName )
		showAutoHideMessage( delayTime + 1.0, msg, labelGather.getText( "MsgBox:speOCBox", "lbTitle" ), MB_SPE_OK_CANCEL, teleport, gstStatus = Define.GST_IN_WORLD )
		BigWorld.cancelCallback( self.delayTeleportCBID )
		self.delayTeleportCBID = BigWorld.callback( delayTime, Functor( self.delayOver, spaceName, pos ) )
		BigWorld.callback( 0.1, self.playerToNpc )

	def atonceTeleport( self, spaceName, pos, result ):
		"""
		点了立刻传送或者取消传送按钮
		"""
		BigWorld.cancelCallback( self.delayTeleportCBID )
		self.delayTeleportTime = 0
		self.delayTeleportCBID = 0
		self.delayTeleportNpc = None
		if self.delayTeleportIsFail:
			self.delayTeleportIsFail = False
		else:
			self.cell.delayTeleport( spaceName, pos, result )

	def delayOver( self, spaceName, pos ):
		"""
		延迟时间结束，开始传送
		"""
		self.delayTeleportTime = 0
		self.delayTeleportCBID = 0
		self.delayTeleportNpc = None
		if self.delayTeleportIsFail:
			self.delayTeleportIsFail = False
		else:
			self.cell.delayTeleport( spaceName, pos, True )

	def playerToNpc( self ):
		"""
		玩家与施法NPC距离限制检测
		"""
		if self.delayTeleportNpc is None: return
		if self.position.distTo( self.delayTeleportNpc.position ) >= csconst.PLAYER_TO_NPC_DISTANCE:
			self.delayTeleportNpc = None
			self.delayTeleportIsFail = True
			ECenter.fireEvent( "EVT_ON_HIDE_SPE_OCBOX" )
			return
		BigWorld.callback( 0.1, self.playerToNpc )

	# -------------------------------------------------
	def onReceiveDamage( self, casterID, skill, damageType, damage ):
		"""
		伤害显示
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skill  : 技能实例
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		self.onDamageModelColor( damageType, damage )
		sk = skill

		dodgeActionName = Const.MODEL_ACTION_DODGE
		resistActionName = Const.MODEL_ACTION_RESIST
		if Define.CAPS_DAN_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_DAN
			resistActionName = Const.MODEL_ACTION_RESIST_DAN
		elif Define.CAPS_SHUANG_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_SHUANG
			resistActionName = Const.MODEL_ACTION_RESIST_SHUANG
		elif Define.CAPS_FU_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_FU
			resistActionName = Const.MODEL_ACTION_RESIST_FU
		elif Define.CAPS_CHANG_WEAPON in self.am.matchCaps:
			dodgeActionName = Const.MODEL_ACTION_DODGE_CHANG
			resistActionName = Const.MODEL_ACTION_RESIST_CHANG

		# 技能产生伤害时的系统信息等处理
		if damage <= 0:
			if casterID > 0 and BigWorld.entities.has_key( casterID ):
				caster = BigWorld.entities[casterID]
				casterName = caster.getName()
				if self.onFengQi and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					casterName = lbs_ChatFacade.masked
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# 你闪躲了%s的%s。
					self.statusMessage( csstatus.SKILL_SPELL_DODGE_TO_SKILL, casterName, sk.getName() )
					# 闪避动作
					if self.canPlayEffectAction():
						self.playActions( [dodgeActionName] )

			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# 你闪躲了%s。
					self.statusMessage( csstatus.SKILL_SPELL_DODGE_TO, sk.getName() )
					# 闪避动作
					if self.canPlayEffectAction():
						self.playActions( [dodgeActionName] )
		else:
			if casterID > 0 and BigWorld.entities.has_key( casterID ):
				caster = BigWorld.entities[casterID]
				casterName = caster.getName()
				if self.onFengQi and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					casterName = lbs_ChatFacade.masked
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# 你招架了%s的%s，受到%i点的伤害。
					if (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
						self.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_TO_DOUBLEDAMAGE, casterName, sk.getName(), damage )
					else:
						self.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_TO, casterName, sk.getName(), damage )
					# 招架动作
					if self.canPlayEffectAction():
						self.playActions( [resistActionName] )

				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# %s的%s暴击对你造成%i点的伤害。
					self.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_FROM_SKILL, casterName, sk.getName(), damage )
				else:#
					if (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
						if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:
							# 你受到了%s反弹的%i点法术伤害。
							self.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC, casterName, damage )
						else:
							# 你受到了%s反弹的%i点伤害。
							self.statusMessage( csstatus.SKILL_BUFF_REBOUND_PHY, casterName, damage )
					else:
						#%s的%s对你造成了%i的伤害。
						self.statusMessage( csstatus.SKILL_SPELL_DAMAGE_FROM_SKILL, casterName, sk.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# 你招架了%s，受到%i点的伤害。
					self.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_FROM, sk.getName(), damage )
					# 招架动作
					if self.canPlayEffectAction():
						self.playActions( [resistActionName] )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# %s暴击对你造成%i点的伤害。
					self.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_FROM, sk.getName(), damage )
				else:
					# %s的%s对你造成了%i的伤害。
					self.statusMessage( csstatus.SKILL_SPELL_DAMAGE_FROM, sk.getName(), damage )

	def isSunBathing( self ):
		"""
		玩家是否在进行日光浴
		"""
		spaceType = self.getCurrentSpaceType()
		return spaceType == csdefine.SPACE_TYPE_SUN_BATHING

	def addTalismanExp( self ):
		"""
		增加法宝经验
		"""
		if self.EXP == 0: return
		# 判断该法宝物品是否存在
		item = self.getItem_( ItemTypeEnum.CEL_TALISMAN )
		if item is None:return
		# 判断是不是法宝类型
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN: return
		# 如果法宝达到最高等级，直接返回
		itemLevel = item.getLevel()
		if itemLevel >= 150: return

		# 法宝吸取经验增加规则，法宝等级只能在其品质等级范围内有经验值变化 by姜毅
		expMap = csconst.TALISMAN_LEVELUP_MAP
		grade = item.getGrade()
		if itemLevel >= expMap[grade][0]:
			self.statusMessage( expMap[grade][1] )
			return

		self.cell.addTalismanExp()

	def addTalismanPotential( self ):
		"""
		增加法宝潜能点
		"""
		# 如果人物潜能点为0，直接返回
		if self.potential == 0: return
		# 判断该法宝物品是否存在
		item = self.getItem_( ItemTypeEnum.CEL_TALISMAN )
		if item is None: return
		# 判断是不是法宝类型
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN: return
		# 如果法宝技能达到最高等级，直接返回
		skillLevel = item.getSkillLevel()
		if skillLevel >= 150: return

		# 法宝吸取潜能增加规则，法宝等级只能在其品质等级范围内有潜能变化 by姜毅
		expMap = csconst.TALISMAN_LEVELUP_MAP
		grade = item.getGrade()
		if skillLevel >= expMap[grade][0]:
			self.statusMessage( expMap[grade][2] )
			return

		self.cell.addTalismanPotential()

	def updateTalismanGrade( self ):
		"""
		提升法宝品质
		"""
		# 判断物品是否存在
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# 判断是不是法宝类型
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return
		grade = talismanItem.getGrade()
		level = talismanItem.getLevel()

		# 升级到仙品需要法宝50级
		if grade == ItemTypeEnum.TALISMAN_COMMON and level < csconst.TALISMAN_UPTO_IMMORTAL_LEVEL:
			self.statusMessage( csstatus.TALISMAN_UPDATE_TOI_NEED_LEVEL )
			return
		# 升级到神品需要法宝100级
		if grade == ItemTypeEnum.TALISMAN_IMMORTAL and level < csconst.TALISMAN_UPTO_DEITY_LEVEL:
			self.statusMessage( csstatus.TALISMAN_UPDATE_TOD_NEED_LEVEL )
			return
		# 判断法宝品质等级是否已经达到最高等级
		if grade == ItemTypeEnum.TALISMAN_DEITY:
			self.statusMessage( csstatus.TALISMAN_GRADE_TOP )
			return

		# 查找玩家身上是否有相对应的材料物品
		needItemID = rds.talismanEffects.getUpItem( grade )
		needItemAmount = rds.talismanEffects.getUpItemAmount( grade )
		needItemList = self.findItemsByIDFromNKCK( needItemID )
		amount = sum( [item.amount for item in needItemList] )
		if amount < needItemAmount:
			self.statusMessage( csstatus.TALISMAN_UPDATE_GRADE_NEED )
			return

		self.cell.updateTalismanGrade()

	def rebuildTalismanAttr( self, grades, indexs ):
		"""
		改造法宝属性
		"""
		if len( grades ) == 0 or len( indexs ) == 0: return
		# 判断物品是否存在
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# 判断是不是法宝类型
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return

		# 判断玩家携带的材料是否足够
		reDatas = {}
		for grade in grades:
			rebuildItemID = rds.talismanEffects.getRebuildItem( grade )
			rAmount = rds.talismanEffects.getRebuildItemAmount( grade )
			if reDatas.has_key( rebuildItemID ):
				reDatas[rebuildItemID] += rAmount
			else:
				reDatas[rebuildItemID] = rAmount

		noteItemDatas = {}
		for itemID, amount in reDatas.iteritems():
			itemsList = self.findItemsByIDFromNKCK( itemID )
			noteItemDatas[itemID] = itemsList
			totalAmount = sum( [item.amount for item in itemsList] )
			if totalAmount < amount:
				self.statusMessage( csstatus.TALISMAN_REBUILDSTONE_LESS )
				return

		self.cell.rebuildTalismanAttr( grades, indexs )

	def showGodWeaponMaker( self ):
		"""
		define method
		显示神器炼制界面
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_GOD_WEAPON_MAKER" )

	def onEquipGodWeapon( self ):
		"""
		define method
		神器练成成功
		"""
		ECenter.fireEvent( "EVT_ON_GOD_WEAPON_MAKER_SUCCESS" )

	def onRebuildAttrCB( self, grade, index, key ):
		"""
		define
		法宝属性改造成功，服务器端回调
		"""
		ECenter.fireEvent( "EVT_ON_TALISMAN_ATTR_REBUILD", grade, index, key )

	def onActivatyAttrCB( self, grade, index ):
		"""
		define
		法宝属性激活成功，服务器端回调
		"""

		ECenter.fireEvent( "EVT_ON_TALISMAN_ATTR_ACTIVATY", grade, index )

	def onTalismanLvUp( self ):
		"""
		当法宝升级时调用
		"""
		ECenter.fireEvent( "EVT_ON_TALISMAN_LV_UP" )

	def onTalismanSkillLvUp( self ):
		"""
		当法宝技能升级时调用
		"""
		ECenter.fireEvent( "EVT_ON_TALISMAN_SK_UP" )

	def createDynamicItem( self, itemID, amount = 1 ):
		"""
		玩家上的接口创建一个动态物品
		"""
		return items.instance().createDynamicItem( itemID, amount )

	def canPk( self, entity ):
		"""
		判断是否能pk一个entity
		@param entity: entity
		@type  entity: entity
		"""
		if entity is None: return False

		# 如果是自己则不能攻击
		if self.id == entity.id: return False

		# 不在同一地图不能PK
		if self.spaceID != entity.spaceID:
			return False

		# 角色所在地图是否允许pk
		if self.getCanNotPkArea(): return False

		# 如果处于飞行状态，则不允许pk
		if isFlying( self ): return False

		# 30级玩家保护
		if self.pkState == csdefine.PK_STATE_PROTECT: return False

		# 判断是否为宠物，是的话把目标转接给主人
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			entity = entity.getOwner()
			# 找不到该宠物的主人 不能攻击
			if entity is None: return False

		# 判断是否是玩家
		if not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return False

		# 队伍成员不能PK
		if self.isTeamMember( entity.id ):
			return False
		# 30级对方玩家禁止pk
		if entity.pkState == csdefine.PK_STATE_PROTECT:
			return False

		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and not entity.actionSign( csdefine.ACTION_FORBID_PK ):
			if self.inDamageList( entity ) or self.pkTargetList.has_key( entity.id ):
				return True

		if self.sysPKMode:
			# 如果我的pk模式是和平模式则不能攻击
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_PEACE:
				return False

			# 帮战副本中帮会成员不能PK
			if self.tong_dbID != 0 and ( self.tong_dbID == entity.tong_dbID ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG:
				return False

			# 阵营战副本中阵营成员不能PK
			if self.getCamp() != 0 and ( self.getCamp() == entity.getCamp() ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP:
				return False

			if self.sysPKMode in csdefine.SYS_PK_CONTOL_ACT:
				if self.sysPKMode == entity.sysPKMode:
					return False
			# 系统模式为临时阵营模式
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TEMPORARY_FACTION :
				if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG and ( not RoleYiJieZhanChangInterface.canPk( self, entity ) ) :
					return False
			# 系统模式为联盟模式
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_LEAGUE:
				if self.checkCityWarTongBelong( self.tong_dbID, entity.tong_dbID ):
					return False
		else:
			# 如果我的pk模式是善意模式（原善恶模式）并且entity不是黄红名
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_RIGHTFUL and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ]:
				return False

			# 如果我的pk模式是正义模式并且entity不是黄红名
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_JUSTICE and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ] \
				and self.getCamp() == entity.getCamp():
				return False

		# 对方在组队跟随状态下可攻击
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and entity.isFollowing(): return True

		# 如果我被禁止PK或者我要pk的entity被禁止pk（例如某方在安全区）
		if self.actionSign( csdefine.ACTION_FORBID_PK ) or entity.actionSign( csdefine.ACTION_FORBID_PK ):
			return False

		return True

	def pkStateMessage( self ):
		"""
		为了给个NC的PK禁止提示 by姜毅
		"""
		player = BigWorld.player()
		target = player.targetEntity
		if target is None: return None
		if target.getEntityType() != csdefine.ENTITY_TYPE_ROLE: return None

		# 如果是自己则不能攻击
		if self.id == target.id: return None

		if self.qieCuoTargetID == target.id: return None

		# 30级玩家保护
		if self.pkState == csdefine.PK_STATE_PROTECT:
			return csstatus.ROLE_LEVEL_LOWER_PK_LEVEL

		# 30级对方玩家禁止pk
		if target.pkState == csdefine.PK_STATE_PROTECT:
			return csstatus.ROLE_CAN_NOT_PK_TARGET

		# 如果的pk模式是组队模式并且entity是队友
		if self.isTeamMember( target.id ):
			return csstatus.ROLE_PK_MODE_NOT_ALLOW

		# 如果我的pk模式是帮会模式并且entity是帮会成员
		if self.sysPKMode and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG and self.tong_dbID != 0 and ( self.tong_dbID == target.tong_dbID ):
			return csstatus.ROLE_PK_MODE_NOT_ALLOW

		# 如果我的系统pk模式是阵营模式并且entity是阵营成员
		if self.sysPKMode and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP and self.getCamp() != 0 and ( self.getCamp() == target.getCamp() ):
			return csstatus.ROLE_PK_MODE_NOT_ALLOW

		return None

	def onGetBenefitTime( self, benefitTime ):
		"""
		defined method
		获得创世之光buff累积时间 by姜毅
		"""
		self.benefitTime = benefitTime

	def onLineCount( self ):
		"""
		在线时间积累的客户端后台触发 by姜毅
		"""
		LevelUpAwardReminder.instance().onRoleBenefit()

	def startKLJDActivity( self ):
		"""
		打开砸蛋界面
		"""
		INFO_MSG( '----------------startKLJDActivity' )
		pass

	def endKLJDReward( self ):
		"""
		一次砸蛋结束
		"""
		INFO_MSG( '----------------endKLJDReward' )
		pass

	def startSuperKLJDActivity( self ):
		"""
		打开砸蛋界面
		"""
		INFO_MSG( '----------------startKLJDActivity' )
		pass

	def stopDance( self ):
		"""
		停止跳舞
		"""
		self.cell.stopDance()

	def receiveRequestDance( self, requestEntityID ):
		"""
		接受到邀请共舞
		"""
		ECenter.fireEvent( "EVT_ON_INVITE_JOIN_DANCE", requestEntityID )

	def askSuanGuaZhanBu( self, money ):
		"""
		接受到邀请共舞
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_MESSAGE_SUANGUAZHANBU", money )

	def stopRequestDance( self ):
		"""
		取消邀请共舞
		"""
		ECenter.fireEvent( "EVT_ON_STOP_REQUEST_DANCE" )

	def onNPCOwnerFamilyNameChanged( self, npcID, ownerName ):
		"""
		"""
		ECenter.fireEvent( "EVT_ON_NPC_FAMILY_NAME_CHANGE", npcID, ownerName )

	def onFixTimeReward( self, timeTick, itemID, rewardOrder, lifetime , lastRewardID ):
		"""
		defined method
		定时奖励的客户端通知 by姜毅
		"""
		ECenter.fireEvent( "EVT_ON_FIX_TIME_REWARD", timeTick, itemID, rewardOrder, lifetime, lastRewardID )


	def onOldFixTimeReward( self, timeTick, rewardOrder, rewardType, param ):
		"""
		defined method
		老手定时奖励的客户端通知 by姜毅
		timeTick: 剩余时间
		RewardNum: 奖励份数
		RewardType: 奖励类型
		Param: 奖励参数 例如经验值 物品ID等
		"""
		INFO_MSG( "receive old reward: %i type: %i param: %i "%( rewardOrder, rewardType, param ) )
		ECenter.fireEvent( "EVT_ON_OLD_FIX_TIME_REWARD", timeTick, rewardOrder, rewardType, param )


#------------------反外挂的接口--------------------------------------------------
	def clientRecvApexMessage( self, strMsg,nLength ):
		"""
		收到反外挂的数据
		"""
		self.apexClient.NoticeApec_UserData(strMsg,nLength)

	def sendApexMessage( self, strMsg,nLength ):
		"""
		发送反外挂的数据 这个是供C＋＋代码调用的回调函数
		"""
		if self.base == None or self.base.clientSendApexMessage == None :
			return False
		self.base.clientSendApexMessage(strMsg,nLength)
		return True

	def startClientApex( self ):
		"""
		收到起动反外挂的通知
		"""
		self.apexClient = BigWorld.getApexClient( )
		self.apexClient.InitAPexClient(self.sendApexMessage)
		re = self.apexClient.StartApexClient()
		msg = " StartApexClient re =%d"%re
		self.sendApexMessage(msg,len(msg))

	# --------------------------------------------------
	# 新单人骑宠
	# --------------------------------------------------
	def onAddVehicle( self, vehicleData ):
		"""
		Defined Method
		下面2种情况会调用这接口
		1、在游戏中使用骑宠后返回的骑宠数据；
		2、进入游戏后主动向cell申请的骑宠数据；
		@return None
		"""
		id = vehicleData["id"]
		self.vehicleDatas[id] = dict( vehicleData.items() )
		# 通知界面
		rds.opIndicator.onPlayerAddedVehicle( vehicleData )
		ECenter.fireEvent( "EVT_ON_PLAYER_ADD_VEHICLE", id )

	def onDisMountDart( self ):
		"""
		Defined Method
		"""
		self.resetPhysics()
		self.resetCamera()


	def onUpdateVehicleDead( self, id, deadTime ):
		"""
		骑宠喂食 by姜毅
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		oldDeadTime = vehicleData.get( "deadTime" )
		if oldDeadTime is None: return

		newDeadTime = deadTime + oldDeadTime
		newData = { "deadTime" : newDeadTime }
		vehicleData.update( newData )

		# 界面行为
		ECenter.fireEvent( "EVT_ON_VEHICLE_FEEDED", id, newDeadTime )

	def onUpdateVehicleSkPoint( self, id, skPoint ):
		"""
		Define Method
		骑宠技能点更新
		"""
		# 更新客户端数据
		self.vehicleDatas[id].update( { "skPoint" : skPoint } )
		# 通知界面
		ECenter.fireEvent( "EVT_ON_VEHICLE_SKPOINT_UPDATE", id )


	#骑宠传功有关
	def  transVehicle( self, id ):
		"""
		给当前激活的骑宠传功
		"""
		#不能给高于自己6级的骑宠传功
		vehicleData = self.vehicleDatas.get( id )
		if not vehicleData: return
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_NO_TRANS_LEVEL_MAX )
			return
		#玩家当前潜能点是否大于0
		if  self.potential <= 0 :
			self.statusMessage( csstatus.VEHICLE_NO_ENOUGH_POTENTIAL )
			return
		#判断传功骑宠是不是当前激活的骑宠
		if self.activateVehicleID!= id:
			self.statusMessage( csstatus.VEHICLE_NO_CURRENT_ACTIVATE )
			return
		self.base.transVehicle( id )

	def onUpdateVehicleProperty( self, id, level,strength,intellect,dexterity,corporeity, step, growth, srcID ):
		"""
		Define Method
		骑宠属性更新
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		# 更新客户端数据
		data = { "level"    	: level,
			 "strength"	: strength,
			 "intellect"	: intellect,
			 "dexterity"	: dexterity,
			 "corporeity"  	: corporeity,
			 "step"		: step,
			 "growth"  	: growth,
			 "srcItemID"    : srcID
			}
		if vehicleData["step"] != step: #刷新属性 nextStepItemID
			data["nextStepItemID"] = getNextStepItemID( srcID )
		vehicleData.update( data )

		# 通知界面
		ECenter.fireEvent( "EVT_ON_VEHICLE_UPDATE_ATTR", id )

	def onUpdateVehicleExp( self, id, exp ):
		"""
		Define Method
		骑宠经验更新
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		# 更新客户端数据
		vehicleData.update( { "exp" : exp } )

		# 通知界面
		ECenter.fireEvent( "EVT_ON_VEHICLE_EXP_UPDATE", id )


	#骑宠喂养、饱腹度相关
	def canDomesticate(self):
		"""
		能否喂食饱腹度
		"""
		if self.state == csdefine.ENTITY_STATE_FREE:
			return True
		return False

	def domesticateVehicle( self, id, needItemID, count ):
		"""
		骑宠喂养
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		if not self.canDomesticate():return

		items = self.findItemsByIDFromNK( needItemID )
		scount = 0
		for item in items:
			scount += item.getAmount()
		#数量不足
		if scount < count:
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return
		self.cell.domesticateVehicle( id, needItemID,count )

	def onUpdateVehicleFullDegree( self, id, fullDegree ):
		"""
		Define Method
		骑宠饱腹度更新
		"""
		# 更新客户端数据
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		newData = { "fullDegree" : fullDegree }
		vehicleData.update( newData )

		# 通知界面
		ECenter.fireEvent( "EVT_ON_VEHICLE_FULLDEGREE_UPDATE", id )


	#骑宠激活
	def activateVehicle( self, vehicleDBID ):
		"""
		激活骑宠
		"""
		vehicleData = self.vehicleDatas.get( vehicleDBID )
		if vehicleData is None: return

		if vehicleDBID == self.activateVehicleID: return
		fullDegree = vehicleData.get( "fullDegree" )
		if not fullDegree : return
		if int( Time.Time.time() ) >= fullDegree :
			self.statusMessage( csstatus.VEHICLE_NO_JOYANCY )
			return

		deadTime = vehicleData.get( "deadTime" )
		if deadTime != 0:
			nowTime = int( Time.Time.time() )
			if nowTime > deadTime:
				# 对于幼宠不需要喂食 做特别提示
				srcItemID = vehicleData.get( "srcItemID" )
				if srcItemID in ItemTypeEnum.ITEM_CHILD_VEHICLE:
					self.statusMessage( csstatus.VEHICLE_FEED_CHILD )
				else:
					self.statusMessage( csstatus.VEHICLE_FEED_DIE )
				return
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_LEVEL_TOO_HIGN )
			return
		self.base.activateVehicle( vehicleDBID )

	def deactivateVehicle( self ):
		"""
		取消激活
		"""
		if self.activateVehicleID != 0:
			self.cell.deactivateVehicle()


	#骑宠召唤
	def conjureVehicle( self, vehicleDBID ):
		"""
		召唤骑宠
		"""
		vehicleData = self.vehicleDatas.get( vehicleDBID )
		if vehicleData is None: return

		fullDegree = vehicleData.get( "fullDegree" )
		if not fullDegree : return
		if int( Time.Time.time() ) >= fullDegree :
			self.statusMessage( csstatus.VEHICLE_NO_JOYANCY )
			return

		deadTime = vehicleData.get( "deadTime" )
		if deadTime != 0:
			nowTime = int( Time.Time.time() )
			if nowTime > deadTime:
				# 对于幼宠不需要喂食 做特别提示
				srcItemID = vehicleData.get( "srcItemID" )
				if srcItemID in ItemTypeEnum.ITEM_CHILD_VEHICLE:
					self.statusMessage( csstatus.VEHICLE_FEED_CHILD )
				else:
					self.statusMessage( csstatus.VEHICLE_FEED_DIE )
				return
		# 潜行状态下不允许召唤骑宠
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:
			self.statusMessage( csstatus.VEHICLE_NOT_SNAKE )
			return
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_NO_CONJURE )
			return

		self.base.conjureVehicle( vehicleDBID )


	#骑宠升阶
	def upStepVehicle( self, mainID, oblationID, needItem ):
		"""
		骑宠升阶
		"""
		#判断玩家状态
		if self.state != csdefine.ENTITY_STATE_FREE:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STATE_ERROR )
			return

		#判断主宠是否满足条件
		vehicleData = self.vehicleDatas.get( mainID )
		if vehicleData is None: return
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return #主骑宠是飞行骑宠不能升阶
		if not vehicleData["nextStepItemID"] : return #主骑宠本身就不能升阶
		if self.activateVehicleID!= mainID: #判断主骑宠是不是当前激活的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_NOACT )
			return
		if self.vehicleDBID == mainID: #判断主骑宠是不是当前骑乘的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_ISCONJURE )
			return

		#判断祭宠是否满足条件
		o_vehicleData = self.vehicleDatas.get( oblationID )
		if o_vehicleData is None: return
		if o_vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		if self.activateVehicleID == oblationID: #判断祭宠是不是当前激活的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ACT )
			return
		if self.vehicleDBID == oblationID: #判断祭宠是不是当前骑乘的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ISCONJURE )
			return
		if o_vehicleData["step"] != vehicleData["step"]: #主宠和祭宠阶次是不是一样
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NOT_SAME )
			return

		#道具要求
		items = self.findItemsByIDFromNK( needItem )
		if len(items) <= 0:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NO_ITEM )
			return
		self.cell.upStepVehicle( mainID, oblationID, needItem )


	#骑宠变回物品
	def canTurnBack( self, id, needItem ):
		"""
		判断能否进行变回物品操作
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return False  #判断骑宠是否存在
		if self.activateVehicleID == id: return False #判断是不是当前激活的骑宠
		if self.vehicleDBID == id:return False #判断是不是当前召唤的骑宠
		if self.state != csdefine.ENTITY_STATE_FREE:
			return False
		#道具要求
		items = self.findItemsByIDFromNK( needItem )
		if len(items) <= 0:
			return False
		return True

	def vehicleToItem( self, id, needItem ):
		"""
		骑宠变回物品
		"""
		def query( rs_id ):
			if rs_id == RS_YES:
				self.base.vehicleToItem( id,needItem )
		if self.canTurnBack( id, needItem ):
			vehicleData = self.vehicleDatas.get( id )
			if vehicleData["exp"] > 0:
				showMessage( mbmsgs[ 0x012c ] ,"", MB_YES_NO, query )
			else:
				self.base.vehicleToItem( id,needItem )


	def feedVehicle( self, id ):
		"""
		骑宠喂食 by姜毅
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		baseDeadTime = vehicleData.get( "deadTime" )
		if baseDeadTime is None: return
		if baseDeadTime == 0:
			self.statusMessage( csstatus.VEHICLE_FEED_IS_MAX )
			return
		if baseDeadTime >= csconst.VEHICLE_DEADTIEM_LIMIT:
			# 不需要喂食
			self.statusMessage( csstatus.VEHICLE_FEED_IS_MAX )
			return

		# 对于幼宠不需要喂食 做特别提示
		srcItemID = vehicleData.get( "srcItemID" )
		if srcItemID in ItemTypeEnum.ITEM_CHILD_VEHICLE:
			self.statusMessage( csstatus.VEHICLE_FEED_CHILD )
			return

		fodder = VehicleLevelExp.instance().getFodderID( srcItemID )
		if len(fodder) <= 0: return
		item = None
		for fd in fodder:
			item = self.findItemFromNKCK_( fd )
			if not item is None:
				break
		if item is None:
			# 无合适草料
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return

		self.base.feedVehicle( id )

	def fixFreeVehicle( self, id ):
		"""
		确认放生骑宠
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None:
			self.statusMessage( csstatus.FREE_VEHECLE_IS_NOTEXIST )
			return
		if not self.isAlive():		# 玩家已死亡
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_DEAD )
			return
		if self.intonating():		# 玩家正在施法
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_BUSY )
			return
		if id == self.activateVehicleID:  # 刚好是激活的
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISCONJURE )
			return
		if id == self.vehicleDBID:		 # 刚好是主骑宠（主要针对飞行骑宠）
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISUSE )
			return

		def query( rs_id ):
			if rs_id == RS_OK:
				self.freeVehicle( id )
		# "放生后骑宠将无法恢复，确认要放生?"
		showMessage( mbmsgs[0x0d02], "", MB_OK_CANCEL, query, pyOwner = rds.ruisMgr.petWindow )

	def freeVehicle( self, id ):
		"""
		放生骑宠
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None:
			self.statusMessage( csstatus.FREE_VEHECLE_IS_NOTEXIST )
			return
		if not self.isAlive():		# 玩家已死亡
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_DEAD )
			return
		if self.intonating():		# 玩家正在施法
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_BUSY )
			return
		if id == self.activateVehicleID:  # 刚好是激活的
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISCONJURE )
			return
		if id == self.vehicleDBID:		 # 刚好是主骑宠（主要针对飞行骑宠）
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISUSE )
			return

		self.cell.freeVehicle( id )

	def onFreeVehicle( self, id ):
		"""
		放生/升阶骑宠后通知界面更新 by姜毅
		"""
		self.vehicleDatas.pop( id )

		ECenter.fireEvent( "EVT_ON_PLAYER_FREE_VEHICLE", id )

	def getVehicleLevel( self ):
		"""
		获取当前骑宠的等级,召唤者调用
		"""
		if self.vehicleDBID == 0: return 0
		vehicleData = self.vehicleDatas.get( self.vehicleDBID )
		if vehicleData is None: return 0

		return vehicleData["level"]

	def onVehicleAddSkill( self, skillID ):
		"""
		Define method.
		骑宠获得新技能
		"""
		vehicleData = self.vehicleDatas.get( self.vehicleDBID )
		if vehicleData is None: return
		vehicleData["attrSkillBox"].append( skillID )

		skillInstance = skills.getSkill( skillID )
		self.statusMessage( csstatus.SKILL_VEHICLE_LEARN, skillInstance.getLevel(), skillInstance.getName() )
		ECenter.fireEvent( "EVT_ON_VEHICLE_UPDATE_SKILL", self.vehicleDBID )

	def onVehicleUpdateSkill( self, oldSkillID, newSkillID ):
		"""
		Define method.
		骑宠技能升级
		"""
		vehicleData = self.vehicleDatas.get( self.vehicleDBID )
		if vehicleData is None: return
		skillIDs = vehicleData["attrSkillBox"]
		if oldSkillID not in skillIDs: return
		index = skillIDs.index( oldSkillID )
		vehicleData["attrSkillBox"][index] = newSkillID

		skillInstance = skills.getSkill( newSkillID )
		self.statusMessage( csstatus.SKILL_VEHICLE_LEARN, skillInstance.getLevel(), skillInstance.getName() )
		ECenter.fireEvent( "EVT_ON_VEHICLE_UPDATE_SKILL", self.vehicleDBID )

	def getVehicleSkills( self, dbID ) :
		"""
		获取骑宠的技能列表
		"""
		vehicleData = self.vehicleDatas.get( dbID, None )
		if vehicleData is None : return []
		return vehicleData["attrSkillBox"]

	def set_rollState( self, oldValue ):
		"""
		在roll时是否拾取
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ROLL_STATE_CHANGE", self.rollState )

	def onTongStorage( self, isShow ):
		"""
		在开闭帮会仓库界面时 by姜毅
		"""
		ECenter.fireEvent( "EVT_ON_TONG_STORAGE", isShow )

	def set_realLookLevelAmend( self, oldLevel ):
		"""
		明视等级改变
		"""
		print "realLookLevelAmend: oldLevel", oldLevel, "nowLevel", self.realLookLevelAmend
		if self.realLookLevelAmend == 0: return
		# 检测AOI范围的所有玩家，目前只检测玩家Role
		for entity in BigWorld.entities.values():
			if not issubclass( entity.__class__, CombatUnit ): continue
			if entity.effect_state & csdefine.EFFECT_STATE_PROWL == 0: continue
			entity.resetSnake()
			entity.updateVisibility()


	def initStatistic( self ):
		"""
		初始化经验、金钱、潜能、帮贡为0
		"""
		self.statistic["statExp"] = 0
		self.statistic["statPot"] = 0
		self.statistic["statMoney"] = 0
		self.statistic["statTongContribute"] = 0

	def receiveStatistic( self, receiveStat ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_TODAY_STATISTIC", receiveStat )

	# --------------------------------------------------
	# 切磋
	# --------------------------------------------------
	def onReceivedQieCuo( self, targetID ):
		"""
		收到切磋邀请
		"""
		target = BigWorld.entities.get( targetID )
		if target is None: return

		def query( rs_id ):
			if rs_id == RS_OK:
				self.replyQieCuo( targetID, True )
			else:
				self.replyQieCuo( targetID, False )
		# "%s邀请您进行切磋。"
		showAutoHideMessage( csconst.QIECUO_REQUEST_TIME, mbmsgs[0x0125] % target.getName() ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

	def replyQieCuo( self, targetID, re ):
		def query( rs_id ):
			if rs_id == RS_OK:
				self.cell.replyQieCuo( targetID, True )
			else:
				self.cell.replyQieCuo( targetID, False )

		if re and self.HP_Max != self.HP:
			showAutoHideMessage( csconst.QIECUO_HP_NOT_FULL, mbmsgs[0x012b] ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )
		else:
			self.cell.replyQieCuo( targetID, re )

	def requestQieCuo( self, targetID ):
		"""
		请求切磋
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				self.cell.requestQieCuo( targetID )
		if self.HP_Max == self.HP:
			self.cell.requestQieCuo( targetID )
		else:
			showAutoHideMessage( csconst.QIECUO_HP_NOT_FULL, mbmsgs[0x012a] ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

	def onRequestQieCuo( self, targetID ):
		"""
		发送切磋邀请成功
		"""
		target = BigWorld.entities.get( targetID )
		if target is None: return
		self.statusMessage( csstatus.QIECUO_SEND_REQUEST, target.getName() )
		# 播放一个邀请的2D音效
		Role.onRequestQieCuo( self, targetID )

	def set_qieCuoTargetID( self, oldTargetID = 0 ):
		"""
		切磋目标改变
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_QIECUOID_CHANGED", oldTargetID, self.qieCuoTargetID )

	def trigerImageVerify( self, imageData, count ):
		"""
		Define method.
		触发图片验证

		@param imageData : 验证图片数据，STRING
		@param count : 第几次验证
		"""
		#增加判断是否处于镜头播放状态
		if rds.statusMgr.isInSubStatus(Define.GST_IN_WORLD, CameraEventStatus ):
			self.base.requestCancelVerify()
			return
		ECenter.fireEvent("EVT_ON_ANTI_RABOT_VERIFY", base64.b64decode( zlib.decompress( imageData ) ), count )

	# ----------------------------------------------------------------------------------------------------
	# 使用凤凰引复活
	# ----------------------------------------------------------------------------------------------------
	def useFengHuangYin( self ):
		"""
		使用凤凰引复活
		"""
		def query( rs_id ):
			if rs_id == RS_YES:
				buffData = self.findBuffByBuffID( "099021" )
				self.requestRemoveBuff( buffData[ "index" ] )
			else:
				ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )
		# 是否使用凤凰引原地复活?
		showMessage( mbmsgs[ 0x0127 ] ,"", MB_YES_NO, query )

	# ----------------------------------------------------------------------------------------------------
	# 玩家骑宠装备模型相关
	# ----------------------------------------------------------------------------------------------------
	def setVehicleCamera( self, nodeName ):
		"""
		设置骑宠镜头
		"""
		if not self.inWorld: return
		if not nodeName: return
		if self.vehicleModelNum == 0: return

		pos = rds.effectMgr.accessNodePos( self.model, nodeName )

		# 在盘腿和跨腿坐骑上视角的高度为0.6比较合适
		y = ( pos - self.position ).y + 0.6
		minDistance = Const.CAMERA_MIN_DISTANCE_TO_VEHICLE
		# 在浮空坐骑上视角的高度定为2.0
		if nodeName == Const.VEHICLE_STAND_HP:
			y = ( pos - self.position ).y + 2.0
			minDistance = Const.CAMERA_MIN_DISTANCE_TO_STAND_VEHICLE
		# 要是y < 0 ，则设置默认高度。
		if y <= 0 or y > 8.0: y = 1.8
		pivotPosition = ( 0.0, y, 0.0 )
		rds.worldCamHandler.cameraShell.setEntityTarget( self )
		rds.worldCamHandler.cameraShell.adjustToTarget( False, -0.8, pivotPosition, minDistance, 20 )

	def onUpFlyVehiclePoseOver( self ):
		"""
		上飞行骑宠动作完成回调
		"""
		if not self.inWorld: return
		if not self.vehicleModelNum: return	# 修正上坐骑动作完成回调缓慢的问题
		Role.onUpFlyVehiclePoseOver( self )
		if self.state != csdefine.ENTITY_STATE_PICK_ANIMA: #为了拾取灵气玩法，做一个奇怪的修改
			self.physics.fall = False
		else:
			self.physics.fall = True
			
		UnitSelect().hideMoveGuider()
		self.setModelScale()

	def onDownFlyVehiclePoseOver( self ):
		"""
		下飞行骑宠动作2部分完成回调
		"""
		if not self.inWorld: return
		Role.onDownFlyVehiclePoseOver( self )
		self.clearSourceControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE )
		UnitSelect().hideMoveGuider()



	# ----------------------------------------------------------------------------------------------------
	# 玩家飞行传送模型相关
	# ----------------------------------------------------------------------------------------------------
	def onFlyModelLoad( self, event, modelDict ):
		"""
		玩家飞行模型加载完成
		"""
		if not self.inWorld: return
		Role.onFlyModelLoad( self, event, modelDict )

		functor = Functor( self.onTeleportVehicleCamera, Const.TELEPORT_HP )
		BigWorld.callback( 0.5, functor )

	def onTeleportVehicleCamera( self, nodeName ):
		"""
		"""
		# 获取摄像头偏移高度
		model = self.model
		if model is None: return
		# 获取摄像头
		camera = BigWorld.camera()
		camera.pivotPosition = ( 0.0, 4.0, 0.0 )
		rds.worldCamHandler.cameraShell.maxDistance = 20.0
		rds.worldCamHandler.cameraShell.setDistance( 16.0, True )

	def onTeleportVehicleModeEnd( self ):
		"""
		飞翔传送模式结束
		"""
		Role.onTeleportVehicleModeEnd( self )
		self.resetCamera()

	def resetCamera( self ):
		"""
		重设摄像头位置
		"""
		if self.vehicleModelNum:	# 在骑宠上
			functor = Functor( self.setVehicleCamera, self.vehicleHP )
			BigWorld.callback( 0.1, functor )	# 延迟设置骑宠镜头
		else:
			pivotPosition = Const.CAMERA_PROVITE_OFFSET_TO_ROLE[ self.getClass() ]
			rds.worldCamHandler.cameraShell.setEntityTarget( self )
			rds.worldCamHandler.cameraShell.adjustToTarget( True, -0.8, pivotPosition, 1.0, 20 )

	def onShowExp2PotWindow( self, objectID ):
		"""
		显示经验换潜能界面
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_SHOW_Exp2PotWindow" )

	# ----------------------------------------------------------------------------------------------------
	# 玩家变身模型相关
	# ----------------------------------------------------------------------------------------------------
	def set_currentModelNumber( self, old = '' ):
		"""
		模型编号发生改变
		钓鱼太乱，改的太纠结。
		"""
		Role.set_currentModelNumber( self, old )
		if self.currentModelNumber == "fishing":
			# 如果是钓鱼的话，要弹出钓鱼的界面
			GUIFacade.onFishingBegin( self, csstatus.SKILL_PLAYER_STOP_FISHING )
		if self.currentModelNumber == "":
			GUIFacade.onFishingEnd( self )
		self.resetWeaponType()

	def onAFLimitTimeChanged( self, af_time_limit ):
		"""
		define method
		离开自动战斗状态回调
		"""
		self.af_time_limit = af_time_limit

	def onAFLimitTimeExtraChanged( self, af_time_extra ):
		"""
		define method
		离开自动战斗时间回调2
		"""
		self.af_time_extra = af_time_extra
		if self.af_time_extra > 0:
			ECenter.fireEvent( "EVT_ON_AUTO_FIGHT_TIMER_SHOW_ONLY", self.af_time_extra )

	def resetAutoFight( self ):
		"""
		重新设置自动战斗功能
		"""
		if self.hasAutoFight: return
		if self.level >= Const.SHOW_AUTOBAR_LEVEL_LIMITED:
			self.cell.openAutoFight()	# 开放自动战斗功能

	def pickFruit( self, targetID ):
		"""
		采集果树
		"""
		target = BigWorld.entities.get( targetID )
		if target is None: return

		if not target.isRipe:
			self.statusMessage( csstatus.FRUIT_NOT_RIPE )
			return
		self.cell.pickFruit( targetID )


	def enterWaterCallback( self, entering, volume ):
		"""
		entering:
			@type:	bool
			@des:	true,进入水面;false,走出水面
		volume:
			@type:  水对象
			@des:	水面标识（不同的水面效果不一样）
		"""

		if volume and volume.id == "":	#进入没有编号的水，直接忽略
			return
		if not volume:
			self.onLeaveWaterCallback( "" )
			return
		if getattr( self, "curWaterVolumeID", "" ) == "":
			self.curWaterVolumeID = ""
		#如下逻辑主要是避免玩家在两块相同作用的水里面走来走去，导致BUFF快速的增加减少。
		if entering:
			self.curWaterVolumeID = volume.id
			if getattr( self, "lastWaterVolumeID", "" ) != self.curWaterVolumeID:
				self.lastWaterVolumeID = self.curWaterVolumeID
				self.cell.onEnterWater( volume.id )
		else:
			self.curWaterVolumeID = ""
			functor = Functor( self.onLeaveWaterCallback, volume.id )
			BigWorld.callback( 1, functor )

	def onLeaveWaterCallback( self, volumeID ):
		"""
		"""
		if volumeID == "":					#离开没有编号的水，是不能忽略的。这主要是传送的时候，从一块有编号的水离开，也会传没有编号的参数进来。
			self.cell.onLeaveWater( "" )
			self.lastWaterVolumeID = ""
			self.curWaterVolumeID = ""
		if self.lastWaterVolumeID != self.curWaterVolumeID:
			self.cell.onLeaveWater( volumeID )
			self.lastWaterVolumeID = ""
			self.curWaterVolumeID = ""

	# --------------------------------------------------
	# 摄像头飞行
	# --------------------------------------------------
	def onCameraFly( self, eventID ):
		"""
		Define Method
		摄像头飞行
		"""
		self.startFly( eventID )

	def startFly( self, eventID ):
		"""
		开始飞翔
		"""
		rds.cameraEventMgr.trigger( eventID )

	def onCameraFlyNodeText( self, text ):
		"""
		提示文字
		"""
		if type( text ) != str: return
		ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS2", text )

	def changFashionNum( self ):
		"""
		切换时装和装备
		"""
		if self.vehicleModel: return	# 上飞行骑宠和下飞行骑宠过程中不能换装
		self.cell.changFashionNum()

	def set_fashionNum( self, oldValue ):
		"""
		角色时装切换
		"""
		Role.set_fashionNum( self, oldValue )
		ECenter.fireEvent( "EVT_ON_ROLE_CHANGE_FASHIONNUM", self.fashionNum )
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )

	def onAddRoleHP( self, entityID, addHp ):
		"""
		define method
		某个role增加血量后回调 目前主要用于血恢复表现 by 姜毅
		"""
		entity = BigWorld.entities.get( entityID )
		if entity is None:
			return
		GUIFacade.onRoleHPChanged( entity.HP - addHp, entityID, entity.HP, entity.HP_Max )

	# ------------------------------一键套装 by 姜毅--------------------------------
	def onGetSuitDatas( self, oksData ):
		"""
		define method
		获得一键套装数据
		@param oksData : PY_DICT
		"""
		self.oksData = oksData
		ECenter.fireEvent( "EVT_ON_INIT_SUIT_DATAS", self.oksIndex, oksData )

	def saveSuit( self, suitIndex, suitName ):
		"""
		保存套装数据
		"""
		suitEquips = [ 0, ] * 13		# 构造UID列表，13是需要保存的部位数量
		oldName = None if suitIndex not in self.oksData else self.oksData[suitIndex]["suitName"]
		for cwt, index in self.suitPartDict.iteritems():
			equip = self.itemsBag.getByOrder( cwt )
			uid = 0 if equip is None else equip.getUid()
			suitEquips[index] = uid
		if oldName == suitName:
			self.base.updateSuit( suitIndex, suitEquips )
		else:
			self.base.addSuit( suitIndex, suitName, suitEquips )
		self.oksData[suitIndex] = { "suitName":suitName, "suitList":suitEquips }

	def renameSuit( self, suitIndex, suitName ):
		"""
		重命名套装
		"""
		if suitIndex not in self.oksData:
			return
		self.base.renameSuit( suitIndex, suitName )
		self.oksData[suitIndex]["suitName"] = suitName

	def switchSuit( self, suitIndex ):
		"""
		更换套装
		"""
		# 伪CD检测
		endTime = self.getCooldown( Const.ONE_KEY_SUIT_CD_ID )[3]
		if endTime > Time.Time.time():
			self.statusMessage( csstatus.OKS_COOL_DOWN )
			return
		self.base.onSwitchSuit( suitIndex )

	def onSwitchSuit( self, suitIndex ):
		"""
		define method
		更换套装回调
		"""
		# 装备更换
		uids = self.oksData[suitIndex]["suitList"]
		freeOrders = self.getAllNormalKitbagFreeOrders()
		kb_max = csdefine.KB_MAX_SPACE
		pm = Const.ONE_KEY_SUIT_PART_MAP
		showSuccess = True
		for cwt, index in self.suitPartDict.iteritems():
			uid = uids[index]
			equipUID = self.order2uid( cwt )
			if equipUID == uid:
				continue
			if uid != 0:
				order = self.uid2order( uid )
				if order < 0:
					showSuccess = False
					self.statusMessage( csstatus.OKS_CANT_FIND, labelGather.getText( "PlayerProperty:EquipPanel", pm[cwt] ) )
					continue
				if not self.getItem_( order )._checkHardiness():
					showSuccess = False
					self.statusMessage( csstatus.OKS_HARDNESS, labelGather.getText( "PlayerProperty:EquipPanel", pm[cwt] ) )
					continue
				self.swapItem( order/kb_max, order%kb_max, csdefine.KB_EQUIP_ID, cwt, False )
			elif equipUID > 0:
				if len(freeOrders) > 0:
					dstOrderID = freeOrders.pop(0)
					self.moveItem( csdefine.KB_EQUIP_ID, cwt, dstOrderID/kb_max, dstOrderID%kb_max )
				else:
					showSuccess = False
					self.statusMessage( csstatus.OKS_KITBAG_FULL )
					continue
		if showSuccess:
			self.statusMessage( csstatus.OKS_SWITCH_OVER, self.oksData[suitIndex]["suitName"] )
		# 设置伪CD
		cdt = Const.ONE_KEY_SUIT_CD_TIME
		startTime = Time.Time.time()
		endTime = startTime + cdt
		self._attrCooldowns[Const.ONE_KEY_SUIT_CD_ID] = ( cdt, cdt, startTime, endTime )
		self.oksIndex = suitIndex
	# ------------------------------一键套装--------------------------------

	# --------------------------------------------------
	# 身轻如燕
	# --------------------------------------------------
	def switchFlyWater( self, switch ):
		"""
		身轻如燕开关
		"""
		Role.switchFlyWater( self, switch )
		if self.physics is None: return

		if switch:
			callback = self.floatOnWaterCallback
		else:
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
		if self.isSprint: return
		self.onWater = switch
		self.switchFlyWaterParticle()
		self.stopFlyWaterParticle()
		if switch:
			onWaterArea = True
		else:
			if self.getJumpState() == Const.STATE_JUMP_DEFAULT:
				onWaterArea = False
			else:
				return

		self.floatOnWaterAreaCallback( onWaterArea )

	def floatOnWaterAreaCallback( self, switch ):
		"""
		进出水域回调
		"""
		if self.isSprint: return
		if self.onWaterArea == switch: return
		self.onWaterArea = switch
		self.cell.switchWater( switch )
		if switch:
			jumpHeight = Const.JUMP_WATER_HEIGHT
			geneGravity = Const.JUMP_WATER_GENEGRAVITY
			if self.isActionState( Action.ASTATE_NAVIGATE ):		# 自动寻路开启水面跳跃回调
				self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )
		else:
			jumpHeight = Const.JUMP_LAND_HEIGHT
			geneGravity = Const.JUMP_GENEGRAVITY
			if self.onWaterJumpTimer is not None:	# 停止水面跳跃回调
				BigWorld.cancelCallback( self.onWaterJumpTimer )
				self.onWaterJumpTimer = None
			self.antoRunConjureVehicle()	# 自动骑乘功能
		self.jumpHeight1 = jumpHeight
		self.geneGravity = geneGravity

	def onWaterJumpBegin( self ):
		"""
		水面跳跃
		"""
		if not self.inWorld: return
		if self.isJumping(): return
		# 策划要求，玩家在骑宠上自动寻路不触发水面几率跳跃
		if self.vehicleModelNum: return
		pro = random.random()
		if pro <= Const.WATER_JUMP_PRO: # 通过概率则起跳
			self.jumpBegin()
		else: 							# 不通过概率则重新回调
			self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )

	def startFlyWaterParticle( self ):
		"""
		开始水面粒子效果
		"""
		if not self.onWater: return
		Role.startFlyWaterParticle( self )


	def onControlled( self, isControlled ):
		"""
		This callback method lets an entity know whether it is now being controlled locally by player physics,
		instead of the server. It happens in response to a call to BigWorld.controlEntity
		"""
		# 这是一段临时代码。 因为bigworld有bug，导致现在将就的使用onPoseVolatile
		# 将来需要使用 controled接口就正常了
		# 测试发现，控制和非控制状态下，客户端的yaw属性会发生改变，服务器的正常
		# 控制状态下，角色客户端的yaw值是0.013046607375144958，非控制状态下是
		# 0.024543693289160728，而服务器端的一直都是0.024543693289160728
		DEBUG_MSG( "controlled---->>>", isControlled )

		if isControlled:
			try:
				self.resetPhysics()
			except:
				ERROR_MSG( "Reset physics failed!" )

		ECenter.fireEvent( "EVT_ON_ROLE_CONTROLL_STATE_CHANGE", isControlled )

	def getName( self ):
		"""
		@rType : string，角色名称
		"""
		return self.playerName

	def jumpToPoint( self, pos, jumpTime, jumpType ):
		"""
		跳跃至某点
		@param pos			:	跳跃到的坐标点
		@type pos			:	Vector3
		@param jumpTime		:	跳跃到最高点的时间
		@type jumpTime		:	Float
		@param jumpType		:	跳跃类型,通常决定动作的播放
		@type jumpType		:	Defined in csdefine.py
		return None
		"""
		#由于跳砍中可以自由移动，所以禁止键盘按键
		self.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK  )
		self.moveToDirectly( pos, self.__onMoveToDirectlyOver )
		self.jumpType = jumpType
		jumpV0 = self.physics.gravity * jumpTime
		self.physics.doJump( jumpV0, 0 )
		BigWorld.callback( jumpTime*2, self.__onjumpToPointOver )

	def __onjumpToPointOver( self ):
		"""
		跳砍动作结束
		"""
		self.jumpType = csdefine.JUMP_TYPE_LAND
		self.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK )


	#镜头中跳跃
	def simulateJumpToPoint( self, pos, jumpTime, jumpSecondTime, cb=None ):
		"""
		跳跃至某点
		@param pos			:	跳跃到的坐标点
		@type pos			:	Vector3
		@param jumpTime		:	开始跳跃的时间
		@type jumpTime		:	Float
		@param jumpSecondTime	:	第二次跳跃的时间
		@type jumpTime		:	Float
		return None
		"""
		#由于跳砍中可以自由移动，所以禁止键盘按键
		self.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK  )
		self.moveToDirectly( pos, self.__onMoveToDirectlyOver )
		time = ( self.position - pos ).length / self.move_speed
		if jumpTime > 0.0:
			if jumpSecondTime < 0.01: #表示没有二段跳
				h = pos[1] - self.position[1] 
				if h > 0.5: #表示要向上跳跃
					dTime = ( time - jumpTime ) / 2.0 - math.sqrt( 2 * h / self.physics.gravity ) / 2.0
					lastTime = time - jumpTime - dTime
				elif h < -1.0:#表示要向下跳跃
					disPos = ( self.position - pos )
					disPos[1] = 0.0
					time = disPos.length / self.move_speed
					lastTime = ( time - jumpTime ) / 2.0
				else:
					lastTime = ( time - jumpTime ) / 2.0
				if lastTime < 0.5:
					lastTime = 0.5
				BigWorld.callback( jumpTime, Functor( self._startJump, lastTime ) )
			else:
				BigWorld.callback( jumpTime, self.jumpBegin )
		if jumpSecondTime > 0.0:
			BigWorld.callback( jumpSecondTime, self.jumpBegin )
		BigWorld.callback( time, Functor( self.__onjumpOver, cb ) )
		
	
	def _startJump( self, lastTime ):
		"""
		"""
		self.jumpType = csdefine.JUMP_TYPE_SIMULATE
		jumpV0 = self.physics.gravity * lastTime
		self.physics.doJump( jumpV0, 0 )

	def __onjumpOver( self, cb ):
		"""
		跳砍动作结束
		"""
		self.jumpType = csdefine.JUMP_TYPE_LAND
		self.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK )
		if callable( cb ):
			cb()
	
	
	# ------------------------------------------------------------------------------
	# 模拟客户端移动表现（用于眩晕状态下的玩家移动）
	# ------------------------------------------------------------------------------
	def outputCallback( self, moveDir, needTime, dTime ):
		"""
		filter的位置刷新回调函数
		"""
		if dTime > 1: dTime = 0
		self.moveTime += dTime
		if self.moveTime >= needTime:
			BigWorld.callback( 0.1, self._onMoveOver )
			return self.position
		else:
			self.movePos = self.position + moveDir * dTime
			return self.movePos

	def _onMoveOver( self ):
		"""
		移动结束
		"""
		self.moveTime = 0.0
		if hasattr(self.filter,"outputCallback"):
			self.filter.outputCallback = None
		# 同步服务器坐标数据，大爷只能用这招了。
		self.filter = BigWorld.PlayerAvatarFilter()
		self.filter = BigWorld.AvatarDropFilter()
		self.filter = BigWorld.PlayerAvatarFilter()

	def lineToPoint( self, position, speed ):
		"""
		移动到坐标点
		"""
		self.filter = BigWorld.AvatarDropFilter()
		yawDir = position - self.position
		yawDir.normalise()
		moveDir = yawDir * speed
		distance = self.position.flatDistTo( position )
		needTime = distance / speed
		func = Functor( self.outputCallback, moveDir, needTime )
		self.moveTime = 0.0
		self.movePos = self.position
		self.filter.outputCallback = func

	def getParticleType( self ):
		"""
		实时返回粒子创建类型
		"""
		return Define.TYPE_PARTICLE_PLAYER

	def addBlurEffect( self ):
		"""
		增加动态模糊效果
		"""
		BigWorld.setGraphicsSetting("RADIO_BLUR", 1)

	def delBlurEffect( self, ):
		"""
		删除动态模糊效果
		"""
		flag = False
		if hasattr( self, "isSprint" ) and self.isSprint: #是否在冲刺
			flag = True
		buffData = self.findBuffByBuffID(  Const.JUMP_FAST_BUFF_ID )
		if buffData : #迅捷移动buff存在
			flag = True
		if not flag:
			BigWorld.setGraphicsSetting("RADIO_BLUR", 0)

	def updateComboCount( self, comboCount ):
		"""
		combo计数
		"""
		ECenter.fireEvent( "EVT_ON_HOMING_SPELL_COMBO", comboCount )

	def set_daoheng( self, oldValue ):
		"""
		道行值
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DAOHENG_CHANGE", self.daoheng )

	def flashTeamSign( self ):
		"""
		刷新队伍标记
		"""
		isCurrShow = rds.viewInfoMgr.getSetting( "player", "sign" )
		self.teamSignSettingChanged( isCurrShow )

	def teamSignSettingChanged( self, value ):
		"""
		队伍标记用户设置相关
		"""
		if self.isInTeam():
			if self.isCaptain():
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "captain", value )
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", False )
			else:
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", value )


	def set_qieCuoState( self, oldValue = 0 ):
		"""
		切磋状态改变
		"""
		if self.qieCuoState == csdefine.QIECUO_READY:
			ECenter.fireEvent( "EVT_END_GOSSIP" ) # 关闭所有窗口

	#宝藏副本相关
	def baoZangBroadCastEnemyPos( self, enemyId, pos ):
		"""
		向队友发送我附近敌人位置信息
		"""
		self.base.baoZangBroadCastEnemyPos( enemyId, pos )

	def baoZangBroadCastDisposeEnemy( self, enemyId ):
		"""
		敌人跑出我的AOI，通知队友
		"""
		self.base.baoZangBroadCastDisposeEnemy( enemyId )

	def onShowAccumPoint( self, id, ap ):
		"""
		显示补刀
		id : 目标怪物
		ap ：灵魂币
		"""
		#播放光效
		type = self.getParticleType()
		target = BigWorld.entities.get( id )
		if target:
			effect = rds.skillEffect.createEffectByID( Const.ACCUMPOINT_EFFECT_ID, target.getModel(), target.getModel(), type, type )
			if effect:
				effect.start()
			ECenter.fireEvent( "EVT_ON_SHOW_ACCUM_POINT", id, ap )

	def onPKListChange( self, pkTargetList, id ):
		"""
		define method
		PK列表发生改变
		"""
		self.pkTargetList = pkTargetList
		ECenter.fireEvent( "EVT_ON_ENTITY_PK_CHANGED", id )

	def onUpdateIntensifyItem( self, uid ):
		"""
		define method
		强化物品发生改变
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_UPDATE_INTENSIFY_ITEM", uid )

	def onOpenSpaceTowerInterface( self ):
		"""
		define method
		打开拯救猰貐防御塔界面
		"""
		ECenter.fireEvent( "EVT_ON_OPEN_SPACE_TOWER_INTERFACE" )

	def onCloseSpaceTowerInterface( self ):
		"""
		define method
		关闭拯救猰貐防御塔界面
		"""
		ECenter.fireEvent( "EVT_ON_CLOSE_SPACE_TOWER_INTERFACE" )

	def showHeadPortraitAndText( self, type, monsterName, headTextureID, text, lastTime ):
		"""
		define method
		显示头像和文字
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_HEAD_PORTRAIT_AND_TEXT", type, monsterName, headTextureID, text, lastTime )

	def cameraFollowActionStart( self ):
		"""
		玩家在播放动作过程中摄像机Y轴跟随
		"""
		self.cameraFollowActionOver()	# 先重置一下
		model = self.getModel()
		ma = Math.Matrix( model.node("HP_head") )
		dis = ma.applyToOrigin()[1] - self.position[1]
		self.cameraInHomingID = BigWorld.callback( 0.1, Functor(self.setCameraTarget, dis, 0.0 ) )

	def setCameraTarget( self, dis, disY ):
		"""
		设置摄像机target
		"""
		cc= BigWorld.camera()
		model = self.getModel()
		ma = Math.Matrix( model.node("HP_head") )
		dis1 = ma.applyToOrigin()[1] - self.position[1]

		ma1 = Math.Matrix( self.matrix )
		if dis1 - dis > Const.CAMERA_FOLLOW_Y_DIS_1: #距离
			if abs( dis1 - disY ) > Const.CAMERA_FOLLOW_Y_DIS_2:
				pos = self.position + ( 0.0, dis1 - dis, 0.0 )
				ma1.setTranslate( pos )
				cc.target = ma1
				disY = dis1
			else:
				pos = self.position + ( 0.0, disY - dis, 0.0 )
				ma1.setTranslate( pos )
				cc.target = ma1
		else:
			cc.target = self.matrix
			disY = 0.0

		self.cameraInHomingID = BigWorld.callback( 0.01, Functor( self.setCameraTarget, dis, disY ) )

	def cameraFollowActionOver( self ):
		"""
		动作结束回调，摄像机跟随结束
		"""
		BigWorld.cancelCallback( self.cameraFollowCBID )
		BigWorld.cancelCallback( self.cameraInHomingID )
		cc= BigWorld.camera()
		cc.target = self.matrix
		self.cameraFollowCBID = 0
		self.cameraInHomingID = 0

	def playSound( self, fileName, typeID, id, priority ):
		"""
		Define method add by wuxo 2012-1-17
		@param	fileName:	音频文件路径
		@type	fileName：	string
		@param	typeID:	        类型 2D/3D
		@type	fileName：	UINT
		@param	NPCID:	        NPC的id
		@type	fileName：	UINT
		@param	priority:	        语音优先级
		@type	priority：	UINT
		"""
		if fileName == "":return
		try:
			npc = BigWorld.entities[id]
			model = npc.getModel()
		except:
			model = None
		if typeID == 3 and model != None:
			rds.soundMgr.playVocality(fileName,model)
		elif typeID == 2 :
			gossipSound = rds.soundMgr.getGossipSound()
			if self.soundPriority <= priority:						#需要播放的语音优先级高，则打断当前语音，否则只有当前语音播放完，才可以播放
				self.soundPriority = priority
				sound = None
				try:
					sound = BigWorld.getSound( fileName )
				except:
					return
				if gossipSound and sound:
					gossipSound.stop()								#停止当前语音
				rds.soundMgr.play2DSound( fileName, True )
			else:
				if gossipSound:
					state = gossipSound.state
					if state == "ready playing":						#当前语音已播放完
						rds.soundMgr.play2DSound( fileName, True )
				else:
					rds.soundMgr.play2DSound( fileName, True )

	def playSoundFromGender( self, fileName, id, flag ):
		"""
		Define method
		根据职业的不同，在玩家的客户端播放不同路径的音效
		"""
		try:
			npc = BigWorld.entities[id]
			model = npc.getModel()
		except:
			model = None
		if not flag and model != None:
			rds.soundMgr.playVocality( fileName, model )
		elif flag:
			rds.soundMgr.play2DSound( fileName )

	def simulateJump( self, height,height0, dis, yaw ):
		"""
		模拟跳跃
		"""
		if self.getPhysics():
			BigWorld.dcursor().yaw = yaw
			jumpV = math.sqrt( height * 2 * self.physics.gravity )
			self.physics.doJump( jumpV,0.0 )
			t0 = math.sqrt( height * 2 / self.physics.gravity ) #到最高点所需时间
			t1 = math.sqrt( height0 * 2 / self.physics.gravity )
			V0 = dis / ( t0 + t1 )
			if V0 > self.move_speed:
				V0 = self.move_speed
			self.physics.velocity = ( 0, 0, V0 )

	def stopSimulateJump( self ):
		"""
		停止模拟跳跃
		"""
		if self.getPhysics():
			self.getPhysics().stop()

	def enterTowerDefenceSpace( self ):
		"""
		define method
		进入塔防副本的副本
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_TOWER_DEFENCE_SPACE", Const.TOWER_DEFENCE_SKILLNUM )


	def addTowerDefenseSpaceSkill( self, skillID, spaceType ):
		"""
		define method
		增加塔防副本的副本技能
		"""
		ECenter.fireEvent( "EVT_ON_ADD_TOWER_DEFENCE_SPACE_SKILL", skillID, spaceType )

	def endTowerDefenseSpaceSkill( self ):
		"""
		define method
		结束塔防副本副本技能
		"""
		ECenter.fireEvent( "EVT_ON_END_TOWER_DEFENCE_SPACE_SKILL" )

	def showRankList( self, msg ):
		"""
		六王墓boss被击杀之后会通知玩家显示排行榜
		param msg = [playerDamageInfos,tongDamageInfos, playerNameTotongName]
		playerDamageInfos = [ [playerName ,damages]}, ]
		tongDamageInfos = [ [tongName,damages], ]
		playerNameTotongName = {playerName: tongName}
		"""
		INFO_MSG( "liu wang mu ranklist %s" %msg )
		ECenter.fireEvent( "EVT_ON_LIU_WANG_MU_SHOW_RANKLIST", msg)

	def onPlayMonsterSound( self, soundType, soundEvent ):
		"""
		怪物播放区域场景音效
		"""
		if not soundType:
			rds.soundMgr.switchMusic( soundEvent )
		else:
			rds.soundMgr.playVocality( soundEvent, self.getModel() )

	def onStopMonsterSound( self ):
		"""
		怪物停止区域场景音效,播放地图音效
		"""
		currArea = self.getCurrArea()
		rds.soundMgr.switchMusic( currArea.getMusic() )



#------------------------------------------------------------------------------------------
#劲舞时刻
#------------------------------------------------------------------------------------------
	def finishSkillPlayAction(self):
		DEBUG_MSG("finishSkillPlayAction find NPC %s"%self.entitiesInRange(csconst.ROLE_AOI_RADIUS))
		entity = self.entitiesInRange(csconst.ROLE_AOI_RADIUS)[1]#副本中只有NPC和玩家自己,搜索到的第一个是玩家，第二个是NPC
		#entity.speakResult()
		entity.cell.nextRound()

	def setDanceChallengeIndex(self, challengeIndex):
		"""
		challengeIndex 是舞王的名次，注意这里的名次是从1开始，到19结束
		"""
		self.cell.setDanceChallengeIndex(challengeIndex)
		self.cell.setRoleModelInfo(self.getModelInfoDict())




	def gotoDanceSpace(self, challengeIndex):
		"""
		这是玩家点击客户端界面按钮（练习斗舞和挑战斗舞）上统一的调用接口，参数含义如下
		challengeIndex 是舞王的名次，注意这里的名次是从1开始，到19结束,0表示为练习斗舞
		"""
		if challengeIndex:#挑战斗舞
			self.base.noticeDanceMgrIsChallenged(challengeIndex)
			#self.cell.teleportToDanceChallengeSpace(challengeIndex)
		else:
			self.cell.teleportToDancePracticeSpace(challengeIndex)
		self.setDanceChallengeIndex(challengeIndex)

	def canChallengeDanceKing(self, challengeIndex):
		#客户端测试是否可以挑战舞王
		self.base.canChallengeDanceKing(challengeIndex)


	def canChallengeDanceKingCb(self, index, result):
		#1表示可以挑战
		#2表示处于保护时间
		#3表示有人在挑战
		#4表示挑战自己
		#5表示挑战低等级舞王，自己也是舞王
		#6表示当前位置没有舞王，自己可以直接成为舞王
		#7表示有积累的经验未领取，需要领取经验才能获得位置
		#8表示未获取位置
		if result == csdefine.DANCE_IN_PROTECT_TIME:
			self.statusMessage(csstatus.JING_WU_SHI_KE_DANCEKING_IN_PROTECTTIME)
		elif result == csdefine.DANCE_IS_CHALLENGED:
			self.statusMessage(csstatus.JING_WU_SHI_KE_DANCEKING_IS_CHALLENGED)
		elif result == csdefine.DANCE_CHALLENGE_MYSELF:
			self.statusMessage(csstatus.JING_WU_SHI_KE_DANCEKING_CHALLENGE_MYSELF)
		#elif result == csdefine.DANCE_CHALLENGE_LOWER_LEVEL_DANCER:  #在下面的触发事伯中处理了
			#self.statusMessage(csstatus.JING_WU_SHI_KE_CHALLENGE_LOWER)
		elif result == csdefine.DANCEK_NOT_GET_POSITION:
			self.statusMessage(csstatus.JING_WU_SHI_KE_NOT_GET_POSITION)
		self.canChallengeDanceKing = result
		#更新舞王榜挑战按钮界面
		ECenter.fireEvent("WU_WANG_BANG_CHALLENGE_BUTTON", index, result)


	def addDancingKingInfo(self, index, dancingKingInfo):
		#Define method
		#接收服务器发送的舞王信息，在进入舞厅时，由服务器发送
		#dancingKingInfo = {"modelInfo":playerModelInfo ,"Time":time.time(),"isChallenge":0 , "dbid":0}
		ECenter.fireEvent("UPDATE_WU_WANG_BANG", index, dancingKingInfo)

	def sendDancingKingInfosOver(self):
		#define method
		DEBUG_MSG("ROLE_SEND_DANCING_KING_INFOS_OVER" )		# 服务器发送舞王信息结束

	def enterWuTing(self):
		#defined method
		ECenter.fireEvent( "EVT_ON_ENTER_WUTING" )

	def leaveWuTing(self):
		#defined method
		ECenter.fireEvent( "EVT_ON_LEAVE_WUTING" )

	def enterDanceCopy(self, type):
		#defined method
		ECenter.fireEvent( "EVT_ON_ENTER_DANCE_SPACE", type )

	def leaveDanceCopy(self, type):
		#defined method
		ECenter.fireEvent( "EVT_ON_LEAVE_DANCE_SPACE", type )

	def quitDance(self):
		self.cell.quitDance()

	#def setDanceChallengeIndex(self, challengeIndex):
		"""
		challengeIndex 是舞王的名次，注意这里的名次是从1开始，到20结束
		"""
		#pass

	def cancelParctice(self):
		#搜索练习斗舞副本中npc，通知结束练习
		for entity in self.entitiesInRange(35):
			if entity.__class__.__name__ ==  "DanceNPC":
				entity.cell.cancelParctice()

	def canGetDancePosition(self, index):
		#检测当前位置是否有人
		self.cell.canGetDancePosition(index)

	def canGetDancePositionCb(self, index):
		#define method
		self.cell.addWuTingBuff(index, self.getModelInfoDict())

	def queryRoleEquip( self, queryName ):
		"""
		查询玩家装备
		"""
		self.base.queryRoleEquipItems( queryName )

	def onQueryRoleEquip( self, roleName, raceclass, roleLeve, tongName, roleModel, equips ):
		"""
		define method.
		查询玩家装备返回
		"""
		espialRemotely.onQueryRoleEquip( roleName, raceclass, roleLeve, tongName, roleModel, equips )

	def resetPatrol( self ):
		"""
		上线显示摆点路径
		"""
		if self.patrolPath and self.patrolModel:
			self.onShowPatrol( self.patrolPath, self.patrolModel )

	def onShowPatrol( self, path, model ):
		"""
		define method
		显示摆点寻路路径
		"""
		patrolMgr.showPatrol( path,model )
		self.cell.setPartrol( path, model )

	def onArrivePatrol( self ):
		"""
		任务摆点路径已走完
		"""
		self.cell.setPartrol( "", "" )

	def setModel( self, model, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		给玩家设置一个模型
		"""
		Role.setModel( self, model, event )
		#加入脚步声
		self.boundFootSound()

	def boundFootSound( self ):
		"""
		玩家移动时的脚步声
		"""
		if self.model is None: return  #此处用self.model而不用self.getModel()是因为玩家可能骑在陆行坐骑上
		try:
			lfoot = self.model.node( Const.FOOT_TRIGGER_LEFT_NODE )
			rfoot = self.model.node( Const.FOOT_TRIGGER_RIGHT_NODE )
		except: #不存在左右脚绑定点就return
			return

		# create left & right feet
		footSoundPath = Const.FOOT_TRIGGER_SOUND_PATH
		self.footTriggers = [BigWorld.FootTrigger( 0, footSoundPath ),BigWorld.FootTrigger( 1, footSoundPath )]
		lfoot.attach( self.footTriggers[0] )
		rfoot.attach( self.footTriggers[1] )


# ----------------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------------
def checkCurrentSpaceData():
	"""
	检查客户端数据是否正确
	"""
	try:
		if not PackChecker.checkCurrentSpaceData():
				ERROR_MSG( "游戏资源数据损坏，请重新安装游戏客户端。" )
				# "游戏资源数据损坏，请重新安装游戏客户端"
				showAutoHideMessage( 15.0, 0x0126, "", MB_OK, lambda x: gbref.rds.gameMgr.quitGame( False ) )
				return
	except ValueError, errstr:
		ERROR_MSG( errstr )
		BigWorld.callback( 1.0, checkCurrentSpaceData )




# Role.py
