
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

# ��Ἴ��
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
# ���� import �밴�����ŷ�
# mapArea �Էŵ� gbref.rds ��
# --------------------------------------------------------------------

class Role(
	GameObject,
	OPRecorder,							# ������¼����
	CombatUnit,							# ��ɫ������
	ItemsBag,							# ����( phw )
	Team,								# �����Ϣ
	RoleQuestInterface,
	RoleChangeBody,                                                 #����
	RoleChat, 							# ���շ��������ص���Ϣ��
	RoleImageVerify,
	QuickBar,							# �����( huangyongwei )
	SpaceFace,
	PetCage,							# ����Ȧ
	RoleCommissionSale,					# ��������
	Bank,								# Ǯׯ( wangshufeng )
	RoleMail,							# �ʼ�����
	RoleRelation,						# ��ҹ�ϵ( wangshufeng )
	TongInterface,						# ���ϵͳ(kebiao)
	RoleCredit,							# �����������( wangshufeng )
	RoleGem,							# ������Ҿ���ʯ( wangshufeng )
	RoleSpecialShop,					# ��ҵ����̳�( wangshufeng )
	HorseRacer,							# ����
	LotteryItem,						# ����(hd)
	RoleQuizGame,						# ֪ʶ�ʴ�( wsf )
	GameRanking,						# ���а�
	LivingSystem,						# ����ϵͳ( jy )
	ScrollCompose,                  #���������䷽
	YuanBaoTradeInterface,				# Ԫ������( jy )
	RoleEidolonHandler,
	RoleChallengeSpaceInterface,		# ��ս����
	RoleChallengeInterface,				# ����
	RoleUpgradeSkillInterface,			# ��������
	RolePlotLv40Interface,				# 40�����鸱��
	SpaceViewerInterface, 				# �����۲���
	RoleStarMapInterface,				# �Ǽʵ�ͼ
	CopyMatcherInterface,				# �������ϵͳ�����ӿ�
	BaoZangCopyInterface,				# ���ظ����ӿ�( Ӣ������ )
	RoleYeZhanFengQiInterface,			# ҹս����ս��
	ZhengDaoInterface,					# ֤��ϵͳ
	RoleDestinyTransInterface,			# �����ֻظ����ӿ�
	Fisher,								# �������
	TDBattleInterface,					# ��ħ��ս
	RoleYiJieZhanChangInterface,			# ���ս��
	RoleJueDiFanJiInterface,			# ���ط����ӿ�
	RoleCopyInterface,					#�����ӿ�
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
		self.skillList_ = []				# ����ID �б�
		self.vehicleSkillList_ = []			# ��輼��id�б�
		self.targetItems = []				# �۲�Է�ʱ��¼�Է���װ��ID
		self.espial_id = 0					# ��¼�۲�ĶԷ���ID
		self.firstHit = False	# ��ҵ��Ƿ��һ�α�����,�������receiveSpell�ж�����ܵ��ı��ι����Ƿ��ǵ�һ��(��Ҹı�Ϊս��״̬���Ǳ��ܵ�������)
		# Ĭ����������Ϊ����
		self.weaponType = Define.WEAPON_TYPE_NONE
		# Ĭ�Ϸ�������Ϊ�޷���
		self.armorType = Define.ARMOR_TYPE_EMPTY
		# ��¼��ҵ�ǰ�ķ���ģ��
		self.talismanModel = None
		self.isLoadModel = False #�Ƿ�����������
		self.delayActionNames = []#ģ�ͼ���δ���ʱ���ŵĶ����ص����ϣ������������зż��ܣ�
		self.delayCastEffects = [] #ģ�ͼ���δ���ʱ���ŵĹ�Ч�ص����ϣ������������зż��ܣ�

		# ��ҵĵ�ǰArea
		self._oldArea = None
		self._oldSpaceNumber = -1			# ��¼��һ�����ڵĸ���Ψһid
		self.money = 0
		self.EXP = 0

		self.randomActionsWithWeapon = []	# ��������������б�
		self.randomActionsWithDanWeapon = []	# ���ֽ�������������б�
		self.randomActionsWithShuangWeapon = []	# ˫�ֽ�������������б�
		self.randomActionsWithFuWeapon = []		# ��ͷ������������б�
		self.randomActionsWithChangWeapon = []	# ��ǹ������������б�
		self.randomActionsNoWeapon = []		# ��������������б�

		self.equipEffects = []				# ���װ��ģ����ظ�������
		self.vehicleEffects = []			# ����ģ����ظ�������

		self.gold = 0
		self.silver = 0
		self.queryASTimerID = 0				# ���־timerID
		self.copySpaceTimerID = 0			# ��������timerID

		self.isReceiveEnterInviteJoin = False	# ��ʱ����¼�Ƿ��ܵ��μ�֪ʶ�ʴ�����

		self.isEquipModelLoad = False	# ��¼װ��ģ���Ƿ�������
		self.tempFace = []

		self.nictationTimerID = -1			# գ��callback
		self.nictationOverTimerID = -1
		# ����ƥ����
		self.am = BigWorld.ActionMatcher( self )

		# ����motor
		self.tam = None

		# ����
		self.rightLoft = None
		self.rightLoftRender = None
		self.leftLoft = None
		self.leftLoftRender = None

		# ��������
		self.vehicleType = 0
		self.vehicleHP = ""
		self.isConjureVehicle = False

		#������ǲ������� ΪNoneû�������ӵ�֪ͨ�������ٸ�ֵ
		self.apexClient = None

		# �д�
		self.qieCuoQiZiModel = None
		self.qieCuoTargetID = 0

		# ��������ģ��
		self.vehicleModel = None

		# ����ģ�����
		self.emptyModel = None

		# ��������
		self.onWaterArea = False		# �Ƿ���ˮ��
		self.flyWaterTimerID = 0
		self.isJumpProcess= False                            #��ʾ����jump����
		self.isSprint = False 	#��ʾ���ڳ�̹���
		self.serverRequests = {}		# ��¼��Ҫ��������Ӧ���󣬵���������Ӧ��ϣ�����������б��б����

		self.lastJumpAttackDir = Math.Vector3()
		self.isLoadDefaultModelFailed = False # �Ƿ����Ĭ��ģ��ʧ�ܣ�����Ҳ���ָ�������ģ����Դ�����Ĭ��ģ�Ͳ����ô˱��ΪTrue
		self.spaceSkillList = []						# �ռ丱�������б�

		self.inFlyDownPose = False	# �·��������pose��־

		self.pkTargetList = {}		# PKĿ���б�
		self.modelVisibleType = -1
		self.isjumpVehiProcess = False

		self.parallelSpaceID = -1	# ��¼����λ��ǰ�Ŀռ�id����ʾ���͵�λ��ռ䴦����
		
		self.visibleRules = [csdefine.VISIBLE_RULE_BY_PLANEID,csdefine.VISIBLE_RULE_BY_WATCH,\
		 csdefine.VISIBLE_RULE_BY_TEL_AND_TEST,	csdefine.VISIBLE_RULE_BY_PROWL_2, csdefine. VISIBLE_RULE_BY_SETTING_1,\
		 csdefine.VISIBLE_RULE_BY_SHOW_SELF]

	# ----------------------------------------------------------------------------------------------------
	# called by engine
	# ----------------------------------------------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method will be called before EnterWorld method
		# �˷�����enterWorld����֮ǰ����
		# ��������ʹ�õ�ģ��·����BigWorld������Զ��ں�̨����·����Դ
		# ����ռ�����̵߳���Դ���������ᵼ����ҽ���Ƚ϶��entity������
		# ����������
		"""
		mNames = []
		mNames.extend( rds.roleMaker.getShowModelPath( self.getModelInfo() ) )
		return mNames

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.AvatarFilter()

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if not self.inWorld: return

		# ����ģ��
		self.createModel()

		self.entityDirProvider = BigWorld.EntityDirProvider( self, 1, 0 )

		# ���ⲿ��
		self.createRightLoft()
		self.createLeftLoft()

		# �����������ͺͷ������ʹ���ģ��֮��
		self.resetWeaponType()
		self.resetArmorType()

		# ģ�͵�RolePitchYaw��Entity����һ��
		self.am.turnModelToEntity = True
		self.am.footTwistSpeed = 0.9

		self.am.boredNotifier = self.onBored			#������ĳ���������� ���ᴥ��
		self.am.patience = random.random() * Const.RANDOM_TRIGGER_TIME_MIN + ( Const.RANDOM_TRIGGER_TIME_MAX - Const.RANDOM_TRIGGER_TIME_MIN )	#��ʼ��ʱ��patienceʱ�佻���������
		self.am.fuse = random.random() * Const.RANDOM_TRIGGER_TIME_MIN + ( Const.RANDOM_TRIGGER_TIME_MAX - Const.RANDOM_TRIGGER_TIME_MIN )		#��ǰ��fuseʱ��Ҳ�����������

		GameObject.onCacheCompleted( self )
		CombatUnit.onCacheCompleted( self )
		BigWorld.addShadowEntity( self )

		self.set_flags( 0 )						# �������������


		if not self.isPlayer() :
			self.fxenterWorld()

		# Ǳ���Ƿ�ɹ�
		self.resetSnake()

		# ������� by ����
		self.tongSignCheck()

		#�󶨽�ɫPitch���ȸı�ʱ�Ļص�����
		self.pitchNotifier = self.onPitchNotifier

		# �������״̬
		self.set_state( csdefine.ENTITY_STATE_FREE )

	def  setModelScale( self, model = None ):
		"""
		���ý�ɫģ�͵�����ֵ
		"""
		career = self.getClass()
		gender = self.getGender()
		scale = csconst.MATCHING_DICT[gender][career]
		if self.currentModelNumber:		# ����ģ��
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
		self.teamlogout() # ��������

		if self.queryASTimerID != 0:
			BigWorld.cancelCallback( self.queryASTimerID )

		if self.nictationTimerID != -1:						# ȡ��գ�۵�callback
			BigWorld.cancelCallback( self.nictationTimerID )
		if self.nictationOverTimerID != -1:
			BigWorld.cancelCallback( self.nictationOverTimerID )

		if self.vehicle and self.vehicle.inWorld and self.vehicle.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) :
			self.vehicle.onDisMountEntity( self.id, 0 )

		# leave world��role�պ�����ҹ۲��role ���ҹ۲�Է��Ĵ���δ��ʱ���ص����ڲ���ʾ��
		if self.id == BigWorld.player().espial_id and espial.endEspial == False:
			espial.stopEspial()
			BigWorld.player().statusMessage( csstatus.ESPIAL_TARGET_TARGET_DESTROY )

		# �Ƴ�ģ�͹���������ؼ�����Ϣ
		rds.modelFetchMgr.freeFetchModelTask( self.id )

		# ��ֹ��������
		self.am = None
		self.tam = None
		self.randomActionsWithWeapon = []
		self.randomActionsWithDanWeapon = []
		self.randomActionsWithShuangWeapon = []
		self.randomActionsWithFuWeapon = []
		self.randomActionsWithChangWeapon = []
		self.randomActionsNoWeapon = []
		self.model = None

		# ����
		self.rightLoft = None
		self.rightLoftRender = None
		self.leftLoft = None
		self.leftLoftRender = None

		# ��������
		self.vehicleType = 0
		self.vehicleHP = ""
		self.isConjureVehicle = False

		# ����ģ�����
		self.disableSkeletonCollider()
		self.disableUnitSelectModel()

		# ���������ؼ�¼
		self.equipEffects = []
		self.vehicleEffects = []			# ����ģ����ظ�������

		# �д�
		self.qieCuoTargetID = 0
		self.delQieCuoQiZiModel()

		#�Ƴ���ɫPitch���ȸı�ʱ�Ļص�����
		self.pitchNotifier = None
		BigWorld.delShadowEntity( self )

	def onPitchNotifier( self, pitch ):
		"""
		��ɫPitch���ȸı�ʱ�Ļص�����
		@type	return	:	float
		@param	return	:	���صײ��õ�Pitch����ֵ
		@type	pitch	:	float
		@param	pitch	:	�ײ�ص��˺���ʱ��������Pitch����ֵ
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
		challengeIndex �����������Σ�ע������������Ǵ�1��ʼ����20����
		"""
		pass

	def setVisibility( self, visible ) :
		"""
		����ģ�Ϳɼ���
		hyw -- 09.01.10
		"""
		GameObject.setVisibility( self, visible )

		# ����
		if self.talismanModel:
			self.talismanModel.visible = visible
		# ����ģ��
		model = self.getModel()
		if model and model != self.model:
			model.visible = visible

	# ----------------------------------------------------------------------------------------------------
	# �������
	# ----------------------------------------------------------------------------------------------------
	def switchVehicleEffect( self, switch ):
		"""
		����������ϵ�����Ч��
		"""
		if not self.inWorld: return
		for effect in self.vehicleEffects:
			if switch:
				effect.fadeIn()
			else:
				effect.fadeOut()

	def set_vehicleModelNum( self, old = 0 ):
		"""
		���ģ�ͱ��
		"""
		DEBUG_MSG( "oldNum", old, "newNum", self.vehicleModelNum, "self.model", self.model )

		# ��ʾ����
		if self.vehicleModelNum:
			self.createVehicleModel()
			# ���ڲ�������ٻ���Ч
			self.isConjureVehicle = True
		else:
			self.am.playAniScale = 1.0
			if self.model and self.vehicleType == Define.VEHICLE_MODEL_STAND:
				playModel = rds.effectMgr.getLinkObject( self.model, Const.VEHICLE_STAND_HP )
				if playModel is None:
					if self.vehicleModel: 	#�����������Ķ�����û���ʱ��ȡ������add by wuxo 2011-12-5
						self.model.root.detach( self.vehicleModel )
						self.set_hideInfoFlag( False )   # ��ʾ�����Ϣ
						self.inFlyDownPose = True
						rds.actionMgr.playActions( self.model, [Const.MODEL_ACTION_RIDE_DOWN, Const.MODEL_ACTION_RIDE_DOWN_OVER], callbacks = [self.onDownFlyVehicleOver] )
					else:
						self.createEquipModel()

				else:
					rds.effectMgr.detachObject( self.model, Const.VEHICLE_STAND_HP, playModel )
					self.vehicleModel = self.model
					self.setModel( playModel, Define.MODEL_LOAD_IN_WORLD_CHANGE )
					self.setModelScale( playModel )#��ԭ���ģ������
					self.addModel( self.vehicleModel )
					self.vehicleModel.position = self.position
					self.vehicleModel.yaw = self.yaw
					rds.actionMgr.playAction( self.vehicleModel, Const.MODEL_ACTION_STAND )
					self.setModelScale( self.vehicleModel )#��ԭ����ģ������
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

			# ��ռ�¼�����ģ���������
			self.vehicleEffects = []
			self.vehicleType = 0
			self.vehicleHP = ""
			self.isConjureVehicle = False

			#������ȥ�����ģ�ͼ�����ɵı��
			self.onFlyModelLoadFinished = False


	def vehicleSound( self, vehicleModelNum, actionNum ):
		"""
		�����Ч����ӿ� by����
		"""
		soundNameList = rds.npcModel.getVehicleSound( actionNum, vehicleModelNum )
		if len( soundNameList ) is 0: return
		soundName = random.choice( soundNameList )
		model = self.getModel()
		if model is None: return
		soundMgr.playVocality( soundName, model )

	def updateRoleModel( self, model ):
		"""
		���������ϵ����ģ��
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
		��趯������
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
		����������
		"""
		pass

	def onDisMountDart( self ):
		"""
		���ڳ�
		"""
		pass

	def onUpdateVehicleExp( self, dbid, exp ):
		"""
		Define Method
		��辭�����
		"""
		pass

	def onUpdateVehicleProperty( self, id, level,strength,intellect,dexterity,corporeity,step,growth,sID ):
		"""
		Define Method
		���������������Ըı�
		"""
		pass

	def onUpdateVehicleFullDegree( self, dbid, fullDegree ):
		"""
		Define Method
		��豥���ȸ���
		"""
		pass

	def onUpdateVehicleDead( self, dbid, deadTime ):
		"""
		Define Method
		�������ʱ����� by ����
		"""
		pass

	def onUpdateVehicleSkPoint( self, dbid, skPoint ):
		"""
		Define Method
		��輼�ܵ����
		"""
		pass

	def onVehicleAddSkill( self, skillID ):
		"""
		Define method.
		������¼���
		"""
		pass

	def onVehicleUpdateSkill( self, skillID ):
		"""
		Define method.
		��輼������
		"""
		pass

	def onFreeVehicle( self ):
		"""
		Defined Method
		������ by����
		"""
		pass

	def onUseVehicleItem( self, dbid, item ):
		"""
		���ʹ�������Ʒ֪ͨ
		"""
		pass

	def onFixTimeReward( self, timeTick, itemID ):
		"""
		defined method
		���ֶ�ʱ�����Ŀͻ���֪ͨ by����
		"""
		pass

	def onOldFixTimeReward( self, timeTick, RewardNum, RewardType, Param ):
		"""
		defined method
		���ֶ�ʱ�����Ŀͻ���֪ͨ by����
		timeTick: ʣ��ʱ��
		RewardNum: ��������
		RewardType: ��������
		Param: �������� ���羭��ֵ ��ƷID��
		"""
		pass

	def updateComboCount( self, comboCount ):
		pass

	def onShowAccumPoint( self, id, ap ):
		"""
		��ʾ����
		id : Ŀ�����
		ap ������
		"""
		pass

	def showRankList(self, msg):
		pass

	def onPlayMonsterSound( self, soundType, soundEvent ):
		pass

	def onStopMonsterSound( self ):
		pass
	# ----------------------------------------------------------------------------------------------------
	# ����������
	# ----------------------------------------------------------------------------------------------------

	def onBored( self, actionName ):
		"""
		�˻ص����ڲ����������
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		# ���action �ǿ�ʱ������fuse�����¿�ʼ��ʱ
		if actionName is None: return

		#���˻�˯��ѣ�Ρ������Ч��ʱ�������漴�����Լ�գ�۾�
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		if self.effect_state & EffectState_list != 0:
			self.resetAM()
			return

		# ��ɫ����������ս��״̬�д���գ�۾�( 0-8 )�����֮�󣬲���գ�۶���
		if self.state not in [ csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_FIGHT ]:
			self.nictationTimerID = BigWorld.callback( random.random() * 8, self.playNictation )

		# ֻ��վ�ŵ�ʱ��Ų����������
		if actionName.startswith( "stand" ): self.playRandomAction()
		self.playVehicleRandomAction( actionName )

		# ��һ��������ʼ����ʱ fuse ������Ϊ0
		# �����ƺ���bug����ʱ��û������ fuse ������ԣ���������������
		self.resetAM()

	def resetAM( self ):
		"""
		����ActionMatcher�е�fuse��patience��ֵ
		"""
		self.am.fuse = 0
		# ÿ֪ͨһ�� onBored  ������Զ��� patience ��Ϊһ����ֵ??
		# ֻ������ patience ֵ ���������Ĳ�ͣ���� onBored ����
		self.am.patience = random.random() * Const.RANDOM_TRIGGER_TIME_MIN + ( Const.RANDOM_TRIGGER_TIME_MAX - Const.RANDOM_TRIGGER_TIME_MIN )

	def playVehicleRandomAction( self, actionName ):
		"""
		���������������ϵ��������
		"""
		if self.vehicleModelNum == 0: return

		actionDatas = Const.VEHICLE_RANDOM_ACTION_MAPS.get( actionName, [] )
		if len( actionDatas ) == 0: return

		# �������������Ͳ������������Ĵ���
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

		# �������������Ͳ������������Ĵ���
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

		# ȡ������
		if randomActionCount == 0: return
		index = random.randint( 0, randomActionCount - 1 )
		capsIndex = Define.CAPS_INDEX25 + index

		caps.remove( Define.CAPS_DEFAULT )
		caps.append( capsIndex )
		caps.append( Define.CAPS_RANDOM )
		self.am.matchCaps = caps

		BigWorld.callback( 0.1, self.onOneShoot )

		if self.vehicleModelNum:	# ������������Ч by����
			self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_RANDOM )

	def onOneShoot( self ):
		"""
		<oneShot>
		Setting this to TRUE means that the Action Matcher will not continue
		playing that action past one cycle of it, if it is no longer triggered,
		but a <cancel> section was keeping it active.
		"""
		# ����Ѳ�����Ұ�����
		if not self.inWorld: return
		self.setArmCaps()

	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		��ȡ���������������������������̶���
		��ȡ���������random1��ʼ��random2,random3....��ȡʧ���򷵻�
		"""
		# ��������������б�
		self.randomActionsWithWeapon = []
		# �������������������������������ֿ�����
		for index in range(1,10):
			weaponActName = "random%s" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithWeapon.append( weaponActName )
			else:
				break

		# ���ֽ�������������б�
		self.randomActionsWithDanWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_dan" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithDanWeapon.append( weaponActName )
			else:
				break

		# ˫�ֽ�������������б�
		self.randomActionsWithShuangWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_shuang" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithShuangWeapon.append( weaponActName )
			else:
				break

		# ��ͷ������������б�
		self.randomActionsWithFuWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_fu" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithFuWeapon.append( weaponActName )
			else:
				break

		# ��ǹ������������б�
		self.randomActionsWithChangWeapon = []
		for index in range(1,10):
			weaponActName = "random%s_chang" % index
			if self.model.hasAction( weaponActName ):
				self.randomActionsWithChangWeapon.append( weaponActName )
			else:
				break

		# ��������������б�
		self.randomActionsNoWeapon = []
		for index in xrange( 1, 10 ):
			noWeaponActName = "random%s_noweapon" % index
			if self.model.hasAction( noWeaponActName ):
				self.randomActionsNoWeapon.append( noWeaponActName )
			else:
				break

	def playNictation( self, key = None ):
		"""
		գ�۾�
		"""
		self.nictationTimerID = -1
		model = self.getModel()
		if model is None: return
		if not model.inWorld: return
		if not hasattr( model, "lian1" ): return

		# �����ɵ���dye���Ա�ָ�
		# ��_2��β��dye���ǲ��ܹ���Ӱ���
		# _nictation Ϊգ�۾�dye
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
		# ����գ��6-9�룬�ָ��ɵ���dye
		faceNum = self.faceNumber
		functor = Functor( self.onPlayNictationOver, oldTint, faceNum )
		self.nictationOverTimerID = BigWorld.callback( random.random() * 3 + 6, functor )

	def onPlayNictationOver( self, oldTint, oldFaceNum ):
		"""
		գ�۶����������
		"""
		# ������ܻ��漰
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
		�������趯��Ч��
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
		ֹͣ���趯��Ч��
		"""
		# ֹͣ����Ч��
		rds.actionMgr.stopAction( self.model, Const.MODEL_ACTION_DANCE )
		rds.actionMgr.stopAction( self.model, Const.MODEL_ACTION_DANCE6 )

		self.updateVisibility()

	def playFaceAction( self, face ) :
		"""
		���ű��鶯��
		"""
		model = self.model
		if model.hasAction( face[0] ) :
			if len( face ) != 1 :
				rds.actionMgr.playActions( model, face )		# ��Ҫ�����������ɵ�Ч������������
			else :
				functor = Functor( self.cell.stopFaceAction, face ) # �����궯����֪ͨcell�˶�����ֹͣ������ԭ������ǰ��״̬
				rds.actionMgr.playAction( model, face[0], callback = functor )
			self.tempFace = face
		else :
			ERROR_MSG( "role has no face %i!" % face )
			return
		self.updateVisibility()

	def stopFaceAction( self, face ) :
		"""
		ֹͣ���ű��鶯��
		"""
		model = self.model
		if model is None: return
		if len( self.tempFace ) != 0 :
			if self.tempFace[0] != face[0] : return # ��ֹ����һ������δ����Ͳ���һ������ʱ����һ������û����ͽ���������
		if len( face ) > 1 :
			rds.actionMgr.stopAction( model, face[0] )
			rds.actionMgr.stopAction( model, face[1] )
		else :
			rds.actionMgr.stopAction( model, face[0] )
		self.tempFace = []
		self.updateVisibility()

	def playRequestDanceAction( self ):
		"""
		�����������趯��
		"""
		rds.actionMgr.playAction( self.model, Const.MODEL_ACTION_STAND )

	def stopRequestDanceAction( self ):
		"""
		ֹͣ�������趯��
		"""
		rds.actionMgr.stopAction( self.model, Const.MODEL_ACTION_STAND )

	# ----------------------------------------------------------------------------------------------------
	# �������
	# ----------------------------------------------------------------------------------------------------
	def createRightLoft( self ):
		"""
		�������ֵ���
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
		�������ֵ���
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
		���ֵ���Ч���������
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
		���ֵ���Ч���������
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
		װ�����ֵ���
		"""
		if model is None: return
		rds.effectMgr.attachObject( model, self.loftHP, self.rightLoft )

	def attachLeftLoft( self, model ):
		"""
		װ�����ֵ���
		"""
		if model is None: return
		rds.effectMgr.attachObject( model, self.loftHP, self.leftLoft )

	def detachRightLoft( self, model ):
		"""
		ж�����ֵ���
		"""
		if model is None: return
		if self.leftLoft is None: return
		rds.effectMgr.detachObject( model, self.loftHP, self.rightLoft )

	def detachLeftLoft( self, model ):
		"""
		ж�����ֵ���
		"""
		if model is None: return
		if self.leftLoft is None: return
		rds.effectMgr.detachObject( model, self.loftHP, self.leftLoft )

	def switchLoft( self, actionName ):
		"""
		��������Ч��
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
	# ����������
	# ----------------------------------------------------------------------------------------------------
	# ��set_��ͷ�Ľӿڣ�����ҵ�set_��������Ըı����Զ�������ؽӿ�
	# ���� set_level ,����ҵ�level���Ըı��������Զ����� set_level()
	def set_level( self, oldLevel = 0):
		"""
		��ҵȼ�
		"""
		# ������Ч
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.UPDATE_LEVEL_EFFECT, self.getModel(), self.getModel(), type, type )
		if effect:
			effect.start()
		CombatUnit.set_level( self, oldLevel )

	def set_yiJieFaction( self, oldValue ):
		"""
		��Ӫ�ı�
		"""
		ECenter.fireEvent( "EVT_ON_YIJIE_FACTION_CHANGED", self.yiJieFaction )

	def set_lifetime( self, lifetime ):
		"""
		�����Ϸ��ʱ��
		"""
		self.lifetime = lifetime

	def set_state( self, oldState = csdefine.ENTITY_STATE_FREE ):
		"""
		���״̬
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

		if self.state == csdefine.ENTITY_STATE_REQUEST_DANCE:		# ��ʼ�������趯��
			self.playRequestDanceAction()
		if oldState == csdefine.ENTITY_STATE_REQUEST_DANCE:			# �����������趯��
			self.stopRequestDanceAction()
		if len( self.tempFace ) != 0 and self.state == csdefine.ENTITY_STATE_FIGHT : # ֹͣ���ű��鶯��
			self.cell.stopFaceAction( self.tempFace )
		self.updateVisibility()

		if self.state == csdefine.ENTITY_STATE_DANCE:				# ��ʼ���趯��
			self.playDanceAction( "dance" )
		if self.state == csdefine.ENTITY_STATE_DOUBLE_DANCE:		# ��ʼ˫�����趯��
			self.playDanceAction( "doubleDance" )
		if oldState == csdefine.ENTITY_STATE_DANCE or oldState == csdefine.ENTITY_STATE_DOUBLE_DANCE:	# �������趯��
			self.stopDanceAction()

		# ����״̬�¸��Ӵ���
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
		���Ч��״̬ ������Դ���Ч��״̬ �� ѣ�Σ������
		"""
		CombatUnit.set_effect_state( self, oldEState )
		self.setArmCaps()


	def set_pkState( self, oldpkstate = csdefine.PK_STATE_PEACE ):
		"""
		pk״̬�ı�
		"""
		#֪ͨ�������
		BigWorld.callback( 2, self.onUpdateRoleNameColor )

	def set_goodnessValue( self, oldValue ):
		"""
		�ƶ�ֵ
		 """
		ECenter.fireEvent( "EVT_ON_ROLE_GOODNESS_CHANGE", self.goodnessValue )


	def set_titleName( self, oldValue ):
		"""
		�ƺ�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_TITLENAME_CHANGE", self, self.titleName, self.getTitleColor( self.title ) )

	def change_money( self, value, reason ):
		"""
		����Ǯ���Ըı�ʱ������������
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
		��Ԫ�������Ըı�ʱ�����á�

		@param newValue : ��ҵ�ǰ��Ԫ��
		@type newValue : UINT32
		"""
		oldValue = self.gold
		self.gold = newValue
		GUIFacade.onRoleGoldChanged( oldValue, self.gold, reason )	# ֪ͨ����

	def updateSilver( self, newValue, reason ):
		"""
		Define method.
		��Ԫ�������Ըı�ʱ�����á�

		@param newValue : ��ҵ�ǰ��Ԫ��
		@type newValue : UINT32
		"""
		oldValue = self.silver
		self.silver = newValue
		GUIFacade.onRoleSilverChanged( oldValue, self.silver, reason )	# ֪ͨ����

	def change_EXP( self, increasedExp, exp, reason ):
		"""
		���������Ըı�ʱ������������
		"""
		if  reason != csdefine.CHANGE_EXP_INITIAL and increasedExp > 0:
			self.statistic["statExp"] += increasedExp
		self.EXP = exp
		ECenter.fireEvent( "EVT_ON_ROLE_EXP_CHANGED", increasedExp, reason )


	# ----------------------------------------------------------------------------------------------------
	# ���ģ����أ�������װ��
	# ----------------------------------------------------------------------------------------------------
	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸���֪ͨ
		"""
		GameObject.onModelChange( self, oldModel, newModel )
		CombatUnit.onModelChange( self, oldModel, newModel )
		if newModel is None: return
		self.updateVisibility()
		if self.am.owner != None: self.am.owner.delMotor( self.am )
		newModel.motors = ( self.am, )

		# ˢ�����и�����
		self.flushAttachments_()
		# ���ö����ص�
		newModel.OnActionStart = self.onActionStart
		# ˢ�¼�¼ģ�͵������������
		self.getRandomActions()

		rds.areaEffectMgr.onModelChange( self )

		#������ҵ�����
		self.setModelScale()
		self.setArmCaps()

		# ������Ȧ����
		self.resetUnitSelectModel()

		self.doActionSkillAction()
		ECenter.fireEvent( "EVT_ON_TARGET_MODEL_CHANGED", self, oldModel, newModel )

	def doActionSkillAction( self ):
		"""
		��Ϊ����ʱ��������Ұ��Χ��Ҳ��������
		"""
		if not self.curActionSkillID: return
		skill = skills.getSkill( self.curActionSkillID )
		actionList = [ skill._datas["param1"], skill._datas["param2"] ]
		self.playFaceAction( actionList )

	def setModel( self, model, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		���������һ��ģ��
		"""
		if self.model is not None:
			self.model.OnActionStart = None
		GameObject.setModel( self, model, event )

	def getModel( self ):
		"""
		��ȡ����ģ�͡��漰��ҿ����������
		����ģ��Ϊ�գ����������ϻ�ȡ��
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
		��ȡ����ģ����ر�Ҫ����Ϣ
		"""
		infoDict = {}
		infoDict["roleID"]			= self.id
		infoDict["roleName"]		= self.playerName
		infoDict["level"]			= self.level
		infoDict["raceclass"]		= self.raceclass
		infoDict["talismanNum"]		= self.talismanNum
		infoDict["fashionNum"]		= self.fashionNum
		infoDict["adornNum"]		= self.adornNum
		if self.isLoadDefaultModelFailed:	# ����ϴ�ģ�ͼ���ʧ�ܣ��ٴμ�����ʹ��Ĭ��ֵ����ģ��
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
		��ȡ����ģ����ر�Ҫ����Ϣ���ֵ�
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
		# ����������
		self.onSwitchVehicle( actionName )

		# ���ⴥ��
		self.switchLoft( actionName )

		# ͷ���������
		self.switchHairAction( actionName )

		# �貨΢��ˮ��Ч������
		self.onSwtichWaterParticle( actionName )

	def createModel( self ):
		"""
		�������ģ��
		������ҵ�ǰ��״̬��������
		"""
		# ���
		if self.vehicleModelNum:
			self.createVehicleModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		## ���贫��
		#if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
		#	self.createFlyModel( Define.MODEL_LOAD_ENTER_WORLD )
		#	return
		# ��̯
		if self.state == csdefine.ENTITY_STATE_VEND:
			self.createVendModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		# ����
		if self.state == csdefine.ENTITY_STATE_RACER:
			self.createHorseModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		# ����
		if self.currentModelNumber:
			self.createChangeModel( Define.MODEL_LOAD_ENTER_WORLD )
			return
		# װ��
		self.createEquipModel( Define.MODEL_LOAD_ENTER_WORLD )

	# ----------------------------------------------------------------------------------------------------
	# ���װ��ģ�����
	# ----------------------------------------------------------------------------------------------------
	def createEquipModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		����װ��ģ��
		@type	event	:	int
		@param	event	: 	�����¼�
		"""
		paths = self.getEquipModelPaths()
		functor = Functor( self.onEquipModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getEquipModelPaths( self ):
		"""
		��ȡװ��ģ��·��
		@return dict
		"""
		roleInfo = self.getModelInfo()
		paths = {}
		profession = self.getClass()
		gender = self.getGender()
		# ��ɫ����ģ��
		bodyPaths= rds.roleMaker.getShowModelPath( roleInfo )
		if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
		# ����ģ�ͷ���
		hairPaths = rds.roleMaker.getHairModelPath( self.hairNumber, self.fashionNum, profession, gender )
		if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths
		# ����ģ����������
		rightHandPaths = rds.roleMaker.getMWeaponModelPath( self.righthandFDict )
		if len( rightHandPaths ): paths[Define.MODEL_EQUIP_RHAND] = rightHandPaths
		# ����ģ����������
		leftHandPaths = rds.roleMaker.getMWeaponModelPath( self.lefthandFDict )
		if len( leftHandPaths ): paths[Define.MODEL_EQUIP_LHAND] = leftHandPaths
		# ����ģ�ͷ���
		talismanPaths = rds.roleMaker.getTalismanModelPath( self.talismanNum )
		if len( talismanPaths ): paths[Define.MODEL_EQUIP_TALIS] = talismanPaths

		return paths

	def onEquipModelLoad( self, event, modelDict ):
		"""
		װ��ģ�ͼ������
		"""
		if not self.inWorld: return
		mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# ����ٴμ���ʧ�����ټ���
			if self.isLoadDefaultModelFailed:
				self.createEquipModel( event )
			return
		mainModel = self.composeEquipModel( modelDict )
		self.setModel( mainModel, event )

		# ������ڳ���
		slaveDart = self.getSlaveDart()
		if slaveDart:
			slaveDart.onMountEntity( self.id, 0 )
			return

		# �����ɫ������״̬���򲥷����趯��
		if self.state == csdefine.ENTITY_STATE_DANCE:
			self.playDanceAction( "dance" )
			return
		# �����ɫ��˫������״̬���򲥷����趯��
		if self.state == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			self.playDanceAction( "doubleDance" )
			return

		self.isLoadDefaultModelFailed = False
		self.isLoadModel = False
		if self.delayActionNames:
			self.playActions(self.delayActionNames)
		self.delayActionNames = []
		# ���Լ��������﹥����Ч
		for cb in self.delayCastEffects:
			if callable( cb ):
				cb()

	def composeEquipModel( self, modelDict ):
		"""
		���װ��ģ��
		"""
		# ����ģ��
		mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None: return
		roleInfo = self.getModelInfo()
		rds.roleMaker.partModelAttachEffect( mainModel, roleInfo )
		#����ģ�ͷ���
		headModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
		self.attachHairModel( mainModel, headModel )
		profession = self.getClass()
		gender = self.getGender()
		rds.roleMaker.hairModelAttachEffect( headModel, self.hairNumber, self.fashionNum, profession, gender )
		# ����ģ����������
		righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
		self.attachRHModel( mainModel, righthandModel )
		self.weaponAttachEffect( righthandModel, self.righthandFDict )
		# ����ģ����������
		lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
		self.attachLHModel( mainModel, lefthandModel )
		self.weaponAttachEffect( lefthandModel, self.lefthandFDict )
		# ����ģ��
		talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
		self.attachTalismanModel( mainModel, talismanModel )
		self.talismanAttachEffect( talismanModel )
		# �������ʱװģʽ������ʾ����װ������Ч��
		if not self.fashionNum: self.resetEquipEffect( mainModel )
		# ���ְҵ�Ƿ�ʦ������ʾ�ŵ�����Ч��
		if self.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = self.getParticleType() )

		return mainModel

	def weaponAttachEffect( self, model, weaponDict, pType = None ):
		"""
		������������Ч��
		@type		model 		: pyModel
		@param		model 		: ģ��
		@type		weaponDict 	: FDict
		@param		weaponDict 	: ��������
		"""
		if pType == None:
			pType = self.getParticleType()
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
			if not type:return
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, intensifyLevel )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )

	def talismanAttachEffect( self, model ):
		# ����Dyes
		talismanNum = self.talismanNum
		talismanDyes = rds.roleMaker.getTalismanModelDyes( talismanNum )
		rds.effectMgr.createModelDye( model, talismanDyes )
		# �Դ���Ч
		effectIDs = rds.itemModel.getMEffects( talismanNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, self.getParticleType(), self.getParticleType() )
			effect.start()
	# ----------------------------------------------------------------------------------------------------
	# ������װ��ģ�����
	# ----------------------------------------------------------------------------------------------------
	def createVehicleModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		�������װ��ģ��
		@type	event	:	int
		@param	event	: 	�����¼�
		"""
		paths = self.getVehicleModelPaths()
		functor = Functor( self.onVehicleModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )
		self.setArmCaps()

	def getVehicleModelPaths( self ):
		"""
		��ȡ�����װ��ģ��·��
		@return dict
		"""
		# ��ȡװ��ģ��
		paths = self.getEquipModelPaths()
		# ���ģ��
		if self.isLoadDefaultModelFailed:	# ����ϴ�ģ�ͼ���ʧ�ܣ��ٴμ�����ʹ��Ĭ��ֵ����ģ��
			if self.vehicleType == Define.VEHICLE_MODEL_STAND:
				self.vehicleModelNum = Const.SKY_VEHICLE_DEFAULT_MODEL_NUM
			else:
				self.vehicleModelNum = Const.LAND_VEHICLE_DEFAULT_MODEL_NUM
		vehiclePaths = rds.itemModel.getMSource( self.vehicleModelNum )
		if len( vehiclePaths ): paths[Define.MODEL_VEHICLE] = vehiclePaths

		return paths

	def onVehicleModelLoad( self, event, modelDict ):
		"""
		����װ��ģ�ͼ������
		"""
		if not self.inWorld: return
		if self.vehicleModelNum == 0: return

		# ���ģ��
		vehicleModel = modelDict.get( Define.MODEL_VEHICLE )
		if vehicleModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# ����ٴμ���ʧ�����ټ���
			if self.isLoadDefaultModelFailed:
				self.createVehicleModel( event )
			return

		# ����������ֵ
		if hasattr( vehicleModel, Const.VEHICLE_HIP ):
			self.vehicleType = Define.VEHICLE_MODEL_HIP
			self.vehicleHP = Const.VEHICLE_HIP_HP
		if hasattr( vehicleModel, Const.VEHICLE_STAND ):
			self.vehicleType = Define.VEHICLE_MODEL_STAND
			self.vehicleHP = Const.VEHICLE_STAND_HP
		if hasattr( vehicleModel, Const.VEHICLE_PAN ):
			self.vehicleType = Define.VEHICLE_MODEL_PAN
			self.vehicleHP = Const.VEHICLE_PAN_HP

		# ���dye������
		dyes = rds.itemModel.getMDyes( self.vehicleModelNum )
		rds.effectMgr.createModelDye( vehicleModel, dyes )
		effectIDs = rds.itemModel.getMEffects( self.vehicleModelNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, vehicleModel, vehicleModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
			self.vehicleEffects.append( effect )
			effect.start()

		# �����ٻ������Ч
		if self.isConjureVehicle:
			self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_CONJURE )
			rds.effectMgr.createParticleBG( vehicleModel, Const.VEHICLE_CONJURE_HP, Const.VEHICLE_CONJURE_PARTICLE, detachTime = 2.0, type = self.getParticleType() )

		# ������������������Ч�� 2011/5/23 16:29 yk
		if event == Define.MODEL_LOAD_IN_WORLD_CHANGE and self.vehicleType == Define.VEHICLE_MODEL_STAND:
			if self.model:
				if self.vehicleModel:	# �����һ���������Ĳ���
					self.onDownFlyVehiclePoseOver()
				self.vehicleModel = vehicleModel
				self.model.root.attach( vehicleModel )
				vehicleModel.yaw = self.yaw
				rds.actionMgr.playAction( vehicleModel, Const.MODEL_ACTION_STAND )
				rds.effectMgr.fadeInModel( vehicleModel, 1.0 )
				rds.actionMgr.playActions( self.model, [Const.MODEL_ACTION_RIDE_UP, Const.MODEL_ACTION_RIDE_UP_OVER], callbacks = [self.onUpFlyVehiclePoseOver] )
				self.set_hideInfoFlag( True ) # �������ͷ����Ϣ
				self.isjumpVehiProcess = True
		else:
			mainModel = self.composeEquipModel( modelDict )
			rds.effectMgr.linkObject( vehicleModel, self.vehicleHP, mainModel )
			self.setModel( vehicleModel, event )
			functor = Functor( self.setVehicleCamera, self.vehicleHP )
			BigWorld.callback( 0.1, functor )	# �ӳ�������辵ͷ
			mainModel.OnActionStart = self.switchLoft
			self.onSwitchVehicle( Const.MODEL_ACTION_STAND )

		# ����ģ�Ͷ�������Ƶ��
		tmpFreq = VehiFreqDatas.get( self.vehicleModelNum,1.0 ) #��ȡ����������Ϣ
		self.am.playAniScale = tmpFreq #���Ŵ���
		self.isLoadDefaultModelFailed = False
		self.onFlyModelLoadFinished = True  #�����ж��ڷ��о�ͷ��ģ���Ѿ��������˵ı�ǣ��ſ�ʼ����

	def setVehicleCamera( self, nodeName ):
		"""
		������辵ͷ
		"""
		pass

	def onUpFlyVehiclePoseOver( self ):
		"""
		�Ϸ�����趯����ɻص�
		"""
		if not self.inWorld: return
		if self.vehicleModel is None: return
		self.model.root.detach( self.vehicleModel )
		mainModel = self.model
		self.model = None
		rds.effectMgr.linkObject( self.vehicleModel, self.vehicleHP, mainModel )
		self.setModel( self.vehicleModel, Define.MODEL_LOAD_IN_WORLD_CHANGE )
		self.setModelScale( self.vehicleModel )#��ԭ����ģ������
		functor = Functor( self.setVehicleCamera, self.vehicleHP )
		BigWorld.callback( 0.1, functor )	# �ӳ�������辵ͷ
		mainModel.OnActionStart = self.switchLoft
		self.onSwitchVehicle( Const.MODEL_ACTION_STAND )
		self.vehicleModel = None
		self.set_hideInfoFlag( False ) # ��ʾ���ͷ����Ϣ
		self.isjumpVehiProcess = False
		self.setArmCaps()

	def onDownFlyVehicleOver( self ):
		"""
		��������Ķ�����û���ʱ�������ﶯ����ɻص�
		"""
		if not self.inWorld: return
		for actionName in self.getActionNames():	# �����ٻ����ļ���û��ʩ����������������Ҫֹͣ�ٻ����ļ���Loop����
			rds.actionMgr.stopAction( self.model, actionName )
		if hasattr( self, "isOnSomething" ) and self.isOnSomething():	# �ڵر��·�������
			self.isJumpProcess = False
		elif self.isJumpProcess:
			self.playActions( [Const.MODEL_ACTION_JUMP_AIR] )
		self.vehicleModel = None
		self.inFlyDownPose = False
		self.isjumpVehiProcess = False
		self.physics.fall = True 	# ����Ϸ�����趯���ص�������Bug
		self.setArmCaps()

	def onDownFlyVehiclePose( self ):
		"""
		�·�����趯��1������ɻص�
		"""
		if not self.inWorld: return
		if hasattr( self, "isOnSomething" ) and self.isOnSomething():	# �ڵر��·�������
			self.isJumpProcess = False
		elif self.isJumpProcess:
			self.playActions( [Const.MODEL_ACTION_JUMP_AIR] )
		self.inFlyDownPose = False
		self.setArmCaps()

	def onDownFlyVehiclePoseOver( self ):
		"""
		�·�����趯��2������ɻص�
		"""
		if not self.inWorld: return
		if self.vehicleModel not in list( self.models ): return
		self.delModel( self.vehicleModel )
		self.vehicleModel = None
		self.inFlyDownPose = False
		self.setArmCaps() #��ֹ����ʱ ����о���

	# ----------------------------------------------------------------------------------------------------
	# �������ģ�����
	# ----------------------------------------------------------------------------------------------------
	def createHorseModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		��������ģ��
		@type	event	:	int
		@param	event	: 	�����¼�
		"""
		paths = self.getHorseModelPaths()
		functor = Functor( self.onHorseModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getHorseModelPaths( self ):
		"""
		��ȡ����ģ��·��
		@return dict
		"""
		roleInfo = self.getModelInfo()
		paths = {}
		profession = self.getClass()
		gender = self.getGender()
		# ��ɫ����ģ��
		bodyPaths= rds.roleMaker.getShowModelPath( roleInfo )
		if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
		# ����ģ�ͷ���
		hairPaths = rds.roleMaker.getHairModelPath( self.hairNumber, self.fashionNum, profession, gender )
		if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths
		# ����ģ�ͷ���
		talismanPaths = rds.roleMaker.getTalismanModelPath( self.talismanNum )
		if len( talismanPaths ): paths[Define.MODEL_EQUIP_TALIS] = talismanPaths
		# ����ģ��
		horsePaths = [Const.HORSERACE_MODEL_PATH]
		if self.hasFlag( csdefine.ENTITY_FLAG_CHRISTMAS_HORSE ):
			horsePaths = rds.npcModel.getModelSources( Const.HORSERACE_CHRISTMAS_MODEL_NUMBER )

		if len( horsePaths ): paths[Define.MODEL_HORSE_MAIN] = horsePaths

		return paths

	def onHorseModelLoad( self, event, modelDict ):
		"""
		�������ģ�ͼ������
		"""
		if not self.inWorld: return

		# ����ģ��
		mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# ����ٴμ���ʧ�����ټ���
			if self.isLoadDefaultModelFailed:
				self.createHorseModel( event )
			return

		roleInfo = self.getModelInfo()
		rds.roleMaker.partModelAttachEffect( mainModel, roleInfo )
		#����ģ�ͷ���
		headModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
		self.attachHairModel( mainModel, headModel )
		profession = self.getClass()
		gender = self.getGender()
		rds.roleMaker.hairModelAttachEffect( headModel, self.hairNumber, self.fashionNum, profession, gender )
		# ����ģ��
		talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
		self.attachTalismanModel( mainModel, talismanModel )
		self.talismanAttachEffect( talismanModel )

		# ��ģ��
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
	# ��Ұ�̯ģ�����
	# ----------------------------------------------------------------------------------------------------
	def createVendModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		������̯ģ��
		@type	event	:	int
		@param	event	: 	�����¼�
		"""
		paths = self.getVendModelPaths()
		functor = Functor( self.onVendModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )
		self.setVendModel()

	def getVendModelPaths( self ):
		"""
		��ȡ��̯ģ��·��
		@return dict
		"""
		paths = {}
		modelNum = Const.VEND_MODELNUM[self.getGender()]
		modelPaths = rds.npcModel.getModelSources( modelNum )
		paths[Define.MODEL_DEFAULT_MAIN] = modelPaths

		return paths

	def onVendModelLoad( self, event, modelDict ):
		"""
		��Ұ�̯ģ�ͼ������
		"""
		if not self.inWorld: return

		# ����ģ��
		mainModel = modelDict.get( Define.MODEL_DEFAULT_MAIN )
		if mainModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# ����ٴμ���ʧ�����ټ���
			if self.isLoadDefaultModelFailed:
				self.createVendModel( event )
			return

		self.setModel( mainModel, event )
		self.isLoadDefaultModelFailed = False

	# ----------------------------------------------------------------------------------------------------
	# ��ұ���ģ�����
	# ----------------------------------------------------------------------------------------------------
	def createChangeModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		������̯ģ��
		@type	event	:	int
		@param	event	: 	�����¼�
		"""
		if not self.currentModelNumber: return
		paths = self.getChangeModelPaths()
		functor = Functor( self.onChangeModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getChangeModelPaths( self ):
		"""
		��ȡ����ģ��·��
		@return dict
		"""
		paths = {}
		# �Ǻ� yk ��Ҫ�޸� 2009-12-29 16:02
		if self.currentModelNumber == "fishing":
			profession = self.getClass()
			gender = self.getGender()
			roleInfo = self.getModelInfo()
			# ��ɫ����ģ��
			bodyPaths= rds.roleMaker.getShowModelPath( roleInfo )
			if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
			# ����ģ�ͷ���
			hairPaths = rds.roleMaker.getHairModelPath( self.hairNumber, self.fashionNum, profession, gender )
			if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths
			# ����ģ�ͷ���
			talismanPaths = rds.roleMaker.getTalismanModelPath( self.talismanNum )
			if len( talismanPaths ): paths[Define.MODEL_EQUIP_TALIS] = talismanPaths
			# ����ģ���������
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
		��ұ���ģ�ͼ������
		"""
		if not self.inWorld: return

		if self.currentModelNumber == "fishing":
			# ����ģ��
			mainModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
			if mainModel is None:
				self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# ����ٴμ���ʧ�����ټ���
				if self.isLoadDefaultModelFailed:
					self.createChangeModel( event )
				return

			roleInfo = self.getModelInfo()
			rds.roleMaker.partModelAttachEffect( mainModel, roleInfo )
			#����ģ�ͷ���
			headModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
			self.attachHairModel( mainModel, headModel )
			profession = self.getClass()
			gender = self.getGender()
			rds.roleMaker.hairModelAttachEffect( headModel, self.hairNumber, self.fashionNum, profession, gender )
			# ����ģ����������
			righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
			self.attachRHModel( mainModel, righthandModel )
			# ����ģ��
			talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
			self.attachTalismanModel( mainModel, talismanModel )
			self.talismanAttachEffect( talismanModel )
			# �������ʱװģʽ������ʾ����װ������Ч��
			if not self.fashionNum: self.resetEquipEffect( mainModel )
			# ���ְҵ�Ƿ�ʦ������ʾ�ŵ�����Ч��
			if self.getClass() == csdefine.CLASS_MAGE:
				rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = self.getParticleType() )
		else:
			mainModel = modelDict.get( Define.MODEL_DEFAULT_MAIN )
			if mainModel is None:
				self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# ����ٴμ���ʧ�����ټ���
				if self.isLoadDefaultModelFailed:
					self.createChangeModel( event )
				return

			if not self.onFengQi:	# �ڷ��ܸ�������ģ�����⴦��
				# ����ģ����������
				righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
				self.attachRHModel( mainModel, righthandModel )
				# ����ģ����������
				lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
				self.attachLHModel( mainModel, lefthandModel )
			else:
				self.set_lefthandFDict()
				self.set_righthandFDict()

			# ��ģ�͸�����Ч
			hps = rds.npcModel.getHps( self.currentModelNumber )
			particles = rds.npcModel.getParticles( self.currentModelNumber )
			for hp, particle in zip( hps, particles ):
				rds.effectMgr.createParticleBG( mainModel, hp, particle, type = self.getParticleType() )
			# ��ģ�͸���dye
			subDyes = rds.npcModel.getModelDyes( self.currentModelNumber )
			rds.effectMgr.createModelDye( mainModel, subDyes )
			self.delTalismanModel()

		self.setModel( mainModel, event )
		if self.currentModelNumber == "fishing":
			rds.actionMgr.playAction( mainModel, Const.MODEL_ACTION_FISHING )

		self.isLoadDefaultModelFailed = False

	# ----------------------------------------------------------------------------------------------------
	# �������ģ�����
	# ----------------------------------------------------------------------------------------------------
	def enableSkeletonCollider( self ):
		"""
		�����������ģ�͵���ײ����
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
		�ر��������ģ�͵���ײ����
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
		��������ģ�����й�Ȧ
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
		�ر�����ģ�����й�Ȧ
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
		��������������Ȧ
		"""
		if not self.inWorld: return
		if self.state != csdefine.ENTITY_STATE_DEAD: return
		model = self.getModel()
		if model is None: return
		pos = rds.effectMgr.accessNodePos( model, Const.ROLE_DEAD_HP )
		if pos == Math.Vector3():	#ֻ������������ʲ����󶨵�λ�õ�Bug
			BigWorld.callback( 1.0, self.resetUnitSelectModel )
		else:
			self.enableSkeletonCollider()
			self.enableUnitSelectModel()

	# ----------------------------------------------------------------------------------------------------
	# ��ҷ��д���ģ�����
	# ----------------------------------------------------------------------------------------------------
	def createFlyModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		��������ģ��
		@type	event	:	int
		@param	event	: 	�����¼�
		"""
		paths = self.getFlyModelPaths()
		functor = Functor( self.onFlyModelLoad, event )
		rds.modelFetchMgr.fetchModels( self.id, functor, paths )

	def getFlyModelPaths( self ):
		"""
		��ȡ����ģ��·��
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
		��ҷ���ģ�ͼ������
		"""
		if not self.inWorld: return

		mainModel = self.composeEquipModel( modelDict )

		# ���ģ��
		flyModel = modelDict.get( Define.MODEL_FLY_MAIN )
		if flyModel is None:
			self.isLoadDefaultModelFailed = not self.isLoadDefaultModelFailed	# ����ٴμ���ʧ�����ټ���
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
		��ȡ����������ڳ�
		"""
		if self.vehicle:
			if self.vehicle.inWorld and self.vehicle.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
				return self.vehicle
		return None

	def replacePartModel( self, newModels ):
		"""
		�滻�������岿��ģ��
		��װʱ�����
		"""
		if not self.inWorld: return
		if len( newModels ) == 0: return
		mainModel = newModels.get( Define.MODEL_EQUIP_MAIN )
		if mainModel is None: return

		oldModel = self.getModel()
		if oldModel is None: return

		self.onUpdateRoleModel()	# һЩ�������ƵĴ���

		if newModels.has_key( Define.MODEL_EQUIP_HEAD ):
			hairModel = newModels[Define.MODEL_EQUIP_HEAD]
		else:
			hairModel = oldModel.head

		self.set_hairNumber()
		# ���������滻
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
		# ��ЧЧ��
		if not self.fashionNum:
			self.resetEquipEffect( mainModel )
		# ��ʦ���й�Ч��˵
		if self.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( mainModel, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, self.onEquipParticleLoad, type = self.getParticleType() )
		# ���跨������Ŀ���
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
		��ɫģ�͸��»ص�
		"""
		pass

	def onReplaceModelLoad( self, partModel ):
		"""
		6С����ģ�ʹ������,��װ�ص�
		"""
		if not self.inWorld: return

		functor = Functor( self.replacePartModel, partModel )
		BigWorld.callback( 0.1, functor )

	def resetEquipEffect( self, model ):
		"""
		ˢ�¹�ЧЧ������
		"""
		self.equipEffects = []

		self.createBodyEffectBG( model, self.onEquipParticleLoad )
		self.createFeetEffectBG( model, self.onEquipParticleLoad )

	def createBodyEffectBG( self, model, callback = None ):
		"""
		�ز���Ч
		"""
		bodyFDict = self.bodyFDict
		profession = self.getClass()
		gender = self.getGender()
		intensifyLevel = bodyFDict["iLevel"]
		# ���µ����巢���âЧ��(�ز�װ��ǿ����4��ʱ����)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, callback, self.getParticleType() )

		# ���µĸ�ְҵ����������(�ز�װ��ǿ����6��ʱ����)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, callback, self.getParticleType() )

		# ���µ�������Χ�����������( �ز�װ��ǿ����9��ʱ���� )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, callback, self.getParticleType() )

		# ���µ�������ת�⻷( �ز�װ��ǿ����9��ʱ���� )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, callback, self.getParticleType() )

	def createFeetEffectBG( self, model, callback = None ):
		"""
		Ь�ӹ�Ч
		"""
		intensifyLevel = self.feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, callback, self.getParticleType() )

	def onEquipParticleLoad( self, particle ):
		"""
		װ���������Ӽ������
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
		���͸ı�
		"""
		rds.roleMaker.createHairModelBG( self.hairNumber, self.fashionNum, self.getClass(), self.getGender(), self.onHairModelLoad )

	def onHairModelLoad( self, hairModel ):
		"""
		callback Method
		���ͻ�װ��ɻص�
		"""
		if not self.inWorld: return
		self.attachHairModel( self.getModel(), hairModel )

	def attachHairModel( self, mainModel, hairModel ):
		"""
		����ͷ��
		"""
		rds.effectMgr.linkObject( mainModel, Const.MODEL_HAIR_HP, hairModel )
		self.updateVisibility()

	def switchHairAction( self, actionName ):
		"""
		ƥ��ͷ����ض���
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
		�Ƿ�������ʾװ������
		"""
		if self.state == csdefine.ENTITY_STATE_CHANGING: return False
		if self.actionSign( csdefine.ACTION_FORBID_CHANGE_MODEL ):
			return False
		return True

	def set_faceNumber( self, oldFaceNumber = 0 ):
		"""
		�����ı�
		"""
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onFaceModelLoad )

	def onFaceModelLoad( self, partModel ):
		"""
		callback Method
		���ͻ�װ��ɻص�
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_bodyFDict( self, oldbodyFDict = None ):
		"""
		����ı�
		"""
		# ��ʱװ����£�ֱ�ӷ���
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onBodyModelLoad )

	def onBodyModelLoad( self, partModel ):
		"""
		callback Method
		����װ��ɻص�
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_volaFDict( self, oldvolaFDict = None ):
		"""
		����ģ�ͱ�Ÿı�
		"""
		# ��ʱװ����£�ֱ�ӷ���
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onVolaModelLoad )

	def onVolaModelLoad( self, partModel ):
		"""
		callback Method
		���׻�װ��ɻص�
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_breechFDict( self, oldbreechFDict = None ):
		"""
		����ģ�ͱ�Ÿı�
		"""
		# ��ʱװ����£�ֱ�ӷ���
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onBreechModelLoad )

	def onBreechModelLoad( self, partModel ):
		"""
		callback Method
		����װ��ɻص�
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_feetFDict( self, oldfeetFDict = None ):
		"""
		Ь��ģ�ͱ�Ÿı�
		"""
		# ��ʱװ����£�ֱ�ӷ���
		if self.fashionNum: return
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )
		if self.onFengQi: return
		if not self.isEquipShow(): return
		roleInfo = self.getModelInfo()
		rds.roleMaker.createPartModelBG( self.id, roleInfo, self.onFeetModelLoad )

	def onFeetModelLoad( self, partModel ):
		"""
		callback Method
		Ь�ӻ�װ��ɻص�
		"""
		if not self.inWorld: return
		modelDict = {}
		modelDict[Define.MODEL_EQUIP_MAIN] = partModel
		self.replacePartModel( modelDict )

	def set_talismanNum( self, oldTalismanNum = 0 ):
		"""
		����ģ���иı�
		"""
		if not self.isEquipShow(): return
		rds.roleMaker.createTalismanModelBG( self.talismanNum, self.onTalismanModelLoad )

	def createTalismanAM( self ):
		"""
		��������motor
		"""
		# ����Բ�ι켣motor������motor�Ĳ���
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
		���÷����ĸ���Ŀ��
		��������Ϊ MatrixProvider ����
		"""
		# �����������ƶ�ƥ��
		if matrixProvider is None: return
		if self.tam is None: return

		self.tam.target = matrixProvider

	def talisManCallback( self ):
		"""
		�����ӽ��ص�
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
		������Զ�ӽ��ص�
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
		ɾ������ģ��
		"""
		if self.talismanModel and self.talismanModel in list( self.models ):
			self.delModel( self.talismanModel )
			if self.tam.owner != None: self.tam.owner.delMotor( self.tam )
			self.talismanModel = None

	def setTalismanModel( self, model, matrixProvider ):
		"""
		���÷���ģ��
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
		����ģ�ͼ��ػص�
		"""
		if not self.inWorld: return
		roleModel = self.getModel()
		if roleModel is None: return
		self.talismanAttachEffect ( model )
		self.attachTalismanModel( roleModel, model )

	def attachTalismanModel( self, mainModel, talismanModel ):
		"""
		���ӷ���ģ��
		"""
		matrixProvider = rds.effectMgr.accessNode( mainModel, Const.TALISMAN_TARGET_HP )
		self.setTalismanModel( talismanModel, matrixProvider )

	def switchEquipEffect( self, switch ):
		"""
		�������ϵ�Ч��
		��ĳЩʱ����Ҫ�ر����ϵ�����Ч����������
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
		װ����������
		"""
		if not self.isEquipShow(): return
		rds.roleMaker.createMWeaponModelBG( self.lefthandFDict, self.onLefthandModelLoad )
		# ������������
		self.resetWeaponType()
		# �����������
		self.resetArmorType()

	def onLefthandModelLoad( self, model ):
		"""
		��������ģ�ͼ������
		"""
		if not self.inWorld: return
		roleModel = self.getModel()
		if roleModel is None: return
		self.weaponAttachEffect( model, self.lefthandFDict )
		self.attachLHModel( roleModel, model )

	def attachLHModel( self, mainModel, lModel ):
		"""
		װ������ģ��
		"""
		if not hasattr( mainModel, "left_hand" ): return
		# ж�ؾɵ���
		self.detachLeftLoft( mainModel.left_hand )
		# ��ģ��
		profession = self.getClass()
		key = Const.MODEL_LEFT_SHIELD_HP
		if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
			key = Const.MODEL_LEFT_HAND_HP
		rds.effectMgr.linkObject( mainModel, key, lModel )
		# װ���µ���
		self.createLeftLoft()
		self.updateVisibility()

	def set_righthandFDict( self, oldRHFDict = 0 ):
		"""
		װ����������
		"""
		if not self.isEquipShow(): return
		rds.roleMaker.createMWeaponModelBG( self.righthandFDict, self.onRighthandModelLoad )
		# ������������
		self.resetWeaponType()

	def onRighthandModelLoad( self, model ):
		"""
		�����������ػص�
		"""
		if not self.inWorld: return
		roleModel = self.getModel()
		if roleModel is None: return
		self.weaponAttachEffect( model, self.righthandFDict )
		self.attachRHModel( roleModel, model )

	def attachRHModel( self, mainModel, rModel ):
		"""
		װ������ģ��
		"""
		if not hasattr( mainModel, "right_hand" ): return
		# ж�ؾɵ���
		self.detachRightLoft( mainModel.right_hand )
		# ��ģ��
		rds.effectMgr.linkObject( mainModel, Const.MODEL_RIGHT_HAND_HP, rModel )
		# װ�ص���
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
		ʱװ�ı�
		"""
		if self.onFengQi: return
		if not self.isEquipShow(): return
		if self.id == BigWorld.player().espial_id:
			ECenter.fireEvent( "EVT_ON_ESPIAL_TARGET_FASHIONNUM_CHANGE", self )
		rds.roleMaker.createFashionModelBG( self.id, self.getModelInfo(), self.onFashionModelLoad )

	def onFashionModelLoad( self, partModels ):
		"""
		ʱװģ�ͺ��̼߳�����ɻص�
		"""
		if not self.inWorld: return
		self.replacePartModel( partModels )

	def set_adornNum( self, oldAdornNum = 0 ):
		"""
		��Ʒ�ı�
		"""
		if not self.isEquipShow(): return
		pass

	def set_weaponAppendState( self, oldState = True ):
		"""
		��������״̬�ı�
		"""
		pass

	def set_headTexture( self, oldHeadTexture = 0 ):
		"""
		��ɫͷ����ͼ�ı� by����
		"""
		pass

	def onAddRoleHP( self, entityID, addHp ):
		"""
		define method
		ĳ��role����Ѫ����ص� Ŀǰ��Ҫ����Ѫ�ָ����� by ����
		"""
		pass

	def onGetSuitDatas( self, oksData ):
		"""
		define method
		���һ����װ����
		@param oksData : PY_DICT
		"""
		pass

	def onSwitchSuit( self, suitIndex ):
		"""
		������װ
		"""
		pass

	def onPlayActionStart( self, actionNames ):
		"""
		��ʼ���Ŷ���
		"""
		CombatUnit.onPlayActionStart( self, actionNames )

	def onPlayActionOver( self, actionNames ):
		"""
		�������Ž���
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
		����ģ����ʾ��ʽ
		�μ� Define.MODEL_VISIBLE_TYPE_*
		"""
		if not self.inWorld: return
		if self.model is None: return
		roleModel = self.getModel()
		if roleModel is None: return
		#if self.modelVisibleType == visibleType:return ȥ����䣬��Ϊ���ű��鶯��ʱ �����return
		self.modelVisibleType = visibleType
		# ����ʾģ��
		if visibleType == Define.MODEL_VISIBLE_TYPE_FALSE:
			self.setVisibility( False )
			rds.effectMgr.setModelAlpha( self.model, 0.0 )
			if self.talismanModel:
				rds.effectMgr.setModelAlpha( self.talismanModel, 0.0 )
			self.model.visibleAttachments = False
			roleModel.visibleAttachments = False
		# ��ʾ����ģ��
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
		# ����Ѫ������������ʾ
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
		# ��͸����ʾģ��
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
		����������ϵĸ���ģ��
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
			# ״̬Ϊ������߹���״̬���߱��鶯��, ��visibleΪTrueʱ���ܲ���ʾ������
			if ( isDance or isFace )  and visible:
				model.visible = False
			else:
				model.visible = visible

	def visibilitySettingChanged( self, key, value ) :
		"""
		�û�ͨ���������øı�ģ�Ϳɼ���
		"""
		BigWorld.player().isRolesVisible = True
		self.updateVisibility()

	def setVendModel( self ):	# 15:31 2008-9-1��wsf add
		"""
		���ð�̯״̬ģ��
		"""
		ECenter.fireEvent( "EVT_ON_VEND_ON_SET_SIGNBOARD", self.id )

	def canVendInArea( self ):
		"""
		ָ�������ܷ��̯
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
				armCaps.append( Define.CAPS_DAN_WEAPON )	# ���ֽ�
			elif self.weaponType == Define.WEAPON_TYPE_DOUBLEHAND:
				armCaps.append( Define.CAPS_SHUANG_WEAPON )	# ˫�ֽ�
			elif self.weaponType == Define.WEAPON_TYPE_WEIGHTSHARP:
				armCaps.append( Define.CAPS_FU_WEAPON )		# ��ͷ
			elif self.weaponType == Define.WEAPON_TYPE_LIGHTBLUNT:
				armCaps.append( Define.CAPS_CHANG_WEAPON )	# ��ǹ
			else:
				armCaps.append( Define.CAPS_WEAPON )
		else:
			armCaps.append( Define.CAPS_NOWEAPON )

		if self.onWaterArea or ( hasattr( self, "isPlayWaterRun" ) and self.isPlayWaterRun ):
			armCaps.append( Define.CAPS_FLY_WATER )

		if hasattr( self, "isJumpProcess" ) and self.isJumpProcess:
			armCaps.append( Define.CAPS_JUMP )

		if  self.findBuffByBuffID( Const.JUMP_FAST_BUFF_ID ): #Ѹ���ƶ�buff����
			armCaps.append( Define.CAPS_FASTMOVING )


		if  self.findBuffByBuffID( Const.VERTIGO_BUFF_ID1 ) or self.findBuffByBuffID( Const.VERTIGO_BUFF_ID2 ): #ѣ��buff����
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
		������������
		"""
		profession = self.getClass()
		if profession == csdefine.CLASS_ARCHER:
			weaponNum = self.lefthandFDict["modelNum"]
		else:
			weaponNum = self.righthandFDict["modelNum"]

		if weaponNum:
			weaponType = Define.CLASS_WEAPONTYPE.get( profession, [] )
			if len( weaponType ) == 0: weaponType = 0
			if profession == csdefine.CLASS_SWORDMAN:    # ����
				if not self.lefthandFDict["modelNum"]:
					weaponType = weaponType[0]
				else:
					weaponType = weaponType[1]
			elif profession == csdefine.CLASS_FIGHTER:  #սʿ
				if str( weaponNum )[1:3] == str( Define.PRE_EQUIP_TWOLANCE ):
					weaponType = weaponType[1]
				else:
					weaponType = weaponType[0]
			else:
				weaponType = weaponType[0]
			self.weaponType = weaponType
		else:
			self.weaponType = 0
		# ����ģ����������
		if self.currentModelNumber and not self.onFengQi:
			self.weaponType = Define.WEAPON_TYPE_BIANSHEN
		# ����Caps״̬
		self.setArmCaps()

	def resetArmorType( self ):
		"""
		���÷�������
		���ݲ߻����������ж�entity�����Ƿ�װ������
		���ж��Ƿ����ؼף����������ְҵ��Ӧ��������·��
		���û�����߲߻��Զ����������·��
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
		��ȡ��������
		"""
		return self.weaponType

	def getArmorType( self ):
		"""
		��ȡ��������
		"""
		return self.armorType

	def isPlayer( self ):
		"""
		��ǽ�ɫ���������
		"""
		return False

	def getName( self ):
		"""
		ȡ��entity����
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
			return "***"
		return self.playerName

	def getTitle( self ):
		"""
		virtual method.
		��ȡ�ƺ�
		@return: string
		"""
		return self.titleName

	def set_title( self, oldTitle ) :
		if oldTitle != self.title:
			ECenter.fireEvent( "EVT_ON_ENTITY_TITLE_CHANGED", self, oldTitle, self.titleName, self.getTitleColor( self.title ) )

	def getHeadTexture( self ) :
		"""
		��ȡ��ɫͷ�� modify by����
		"""
		headTexturePath = rds.iconsSound.getHeadTexturePath( self.headTextureID )
		if not headTexturePath is None: return headTexturePath
		return Const.ROLE_HEADERS[self.getClass()][self.getGender()]

	def getObjHeadTexture( self, objHeadTextureID ) :
		"""
		��ȡ��ɫͷ�� modify by����
		"""
		headTexturePath = rds.iconsSound.getHeadTexturePath( objHeadTextureID )
		return headTexturePath

	def getBoundingBox( self ):
		"""
		virtual method.
		���ش��������bounding box�ĳ����ߡ����Math.Vector3ʵ����
		��������ģ���б����Ź�����Ҫ�ṩ���ź��ֵ��

		@return: Math.Vector3
		"""
		# Ϊ��ʹ�ж�һ�£����ǵ�bounding box��������ͻ���ʹ����ͬ��ֵ��
		# ����б�Ҫ�����Կ��Ǹ��ݲ�ͬ��ְҵʹ�ò�ͬ��ֵ
		# ��������зŴ�ģ�͵ļ��ܣ�������Ҫ����ʵ����������Ƿ����Ŵ���
		if self.vehicle:
			return self.vehicle.getBoundingBox()
		if self.vehicleModelNum:
			return csconst.VEHICLE_MODEL_BOUND
		return csconst.ROLE_MODEL_BOUND

	def canSelect( self ):
		"""
		�Ƿ�����ѡ��
		"""
		if self.state == csdefine.ENTITY_STATE_PENDING:
			return False
		if self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return False
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:	# Ǳ��״̬���ܱ�ѡ��13:33 2008-12-1,wsf
			return False

		return True

	# ----------------------------------------------------------------------------------------------------
	#  ��ɫ��ΪĿ�����
	# ----------------------------------------------------------------------------------------------------
	def onTargetClick( self, player ):
		"""
		����ɫ��ΪĿ����������ʱ���÷���������
		"""
		GameObject.onTargetClick( self, player )
		if player.id == self.id:
			return Define.TARGET_CLICK_SUCC

	def onTargetFocus( self ) :
		"""
		������ƶ����ý�ɫ����ʱ���ú���������
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
		��ʾ�����Ȧ
		"""
		if rds.targetMgr.bindTargetCheck( self ):
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# ���ý����Ȧ��ɫ
				texture = UnitSelect().getTexture( self )
				UnitSelect().setFocusTexture( texture )
				UnitSelect().setFocus( self.emptyModel )
			else:
				UnitSelect().setFocus( self )

	def onTargetBlur( self ) :
		"""
		������뿪�ý�ɫ����ʱ���ú���������
		"""
		rds.ccursor.set( "normal" )
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		GameObject.onTargetBlur( self )

	# ----------------------------------------------------------------------------------------------------
	# ����
	# ----------------------------------------------------------------------------------------------------
	def gossipWith( self, entity, dlgKey ) :
		"""
		�� NPC �Ի�
		hyw--2008.10.08
		@type			entity : BigWorld.Entity
		@param			entity : Ҫ�Ի��� NPC
		@type			tag	   : str
		@param			tag	   : �Ի��ؼ���
		"""
		model = entity.getModel()
		if model and model.visible:	 # CSOL-1311ģ�Ϳɼ����ܶԻ�
			self.cell.gossipWith( entity.id, dlgKey )

	def fxenterWorld( self ):
		"""
		������Ϸʱ��ʾ�Ĺ�Ч
		"""
		rds.effectMgr.createParticleBG( self.getModel(), "HP_root", "particles/xw_0091/xw_0091.xml", type = self.getParticleType() )
		rds.effectMgr.createParticleBG( self.getModel(), "HP_root", "particles/xw_0091/xw_0091_a.xml", type = self.getParticleType() )

	def teleportPlayer( self, space, position, direction ):
		"""
		Server Teleport
		@type		space 		: str / int
		@param		space 		: ���������������Ϊ space ���ƣ�����Ϊ spaceID
		@type		position	: Math.Vector3 or tuple of 3 elements
		@param		position	: λ��
		@type		direction	: Math.Vector3 or tuple of 3 elements
		@param		direction	: ����
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
		Ҫ��ı�ͻ��˵�ʱ��
		@param newtime: new environment time��������������ʽ���֣�
						   һ���� ʱ���֣��磺  01:00 ���賿1�㣩
						   ��һ���Ǹ��������磺 1.0
						   �κ�������ʽ��ʱ�䲻���׳��쳣��Ҳ����������

		@param duration: time LAST HOW LONG�����߻���Ҫ���Է�Ϊ��λ
		@type  duration: UINT16
		"""
		self.cell.ChangeTime(newtime, duration)

	def ReceiveChangeTime( self, newtime):
		"""
		 �ı�ͻ���ʱ��Ϊnewtimeָ����ʱ��
		@param newtime: new environment time��������������ʽ���֣�
						   һ���� ʱ���֣��磺  01:00 ���賿1�㣩
						   ��һ���Ǹ��������磺 1.0
						   �κ�������ʽ��ʱ�䲻���׳��쳣��Ҳ����������
		@type newtime : FLOAT
		"""
		BigWorld.timeOfDay(newtime)

	def SetWeather( self, newweather, duration):
		"""
		�ı�ͻ�������Ϊnewweatherָ��������
		ע���˹���δ��ʵ��
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
		ֱ�ӽ�����Ϣ������Ƶ���ͷ�������Ϣ
		@type				chids 	 : ARRAY <of> INT8 </of>
		@param				chids 	 : Ƶ���б�
		@type				spkName	 : STRING
		@param				spkName	 : ����������
		@type				spkName	 : STRING
		@param				spkName	 : ��Ϣ����
		@return						 : None
		"""
		raise AttributeError( "role has not method 'onDirectMessage'" )

	def onStateChanged( self, old, new ):
		"""
		״̬�ı�
		"""
		CombatUnit.onStateChanged( self, old, new )
		if self.state == csdefine.ENTITY_STATE_DEAD :
			ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		if new == csdefine.ENTITY_STATE_DEAD :
			#�����򲥷�����������������ģ�����˹�Ȧ����ģ�ͱ䶯�Ĵ���
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
		�������ͷ����ǣ�����״̬��Я���е�Ѫ��Ʒ��
		�ӳ������ڵȣ�
		@param		oldFlag	:	�ɱ��
		@type		oldFlag	:	INT32
		@param		flag	:	���жϵı��
		@type		flag	:	int
		@param		type	:	������ͣ����̣��ӳ������ڵȣ�
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
			player.isTeamMember( self.id ):					#�������ʱ����
				self.flashTeamSign()

	def flashTeamSign( self ):
		"""
		ˢ�¶�����
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
		���������ң��������⣩�ӳ����
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_TEAMMING ):					#���״̬
			if self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN ):				#�ӳ�
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", False )
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "captain", value )
			else:															#��Ա
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", value )

	# ----------------------------------------------------------------
	# �������
	# ----------------------------------------------------------------
	def onPrisonContributeSure( self, money ):
		"""
		define method.
		����������ʾ
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().cell.onPrisonContribute()
		# "���Ҫ����%s����ô��"
		showMessage( mbmsgs[0x0121] % Function.switchMoney( money ), "", MB_OK_CANCEL, query )

	# ----------------------------------------------------------------
	# ���װ������
	# ----------------------------------------------------------------
	def equipRepairCompleteNotify( self ):
		"""
		�������
		@param all: �Ƿ�ȫ��
		@type all: bool
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_EQUIP_REPAIR_COMPLETE" )
		for item in self.getItems( csdefine.KB_EQUIP_ID ):
			if item is None:continue
			itemOrder = item.order
			GUIFacade.onKitbagItemUpdate( 0, itemOrder, item )

	# ----------------------------------------------------------------
	# ��ҽ����뿪�ռ�
	# ----------------------------------------------------------------
	def onEnterAreaFS( self ) :
		"""
		defined method.
		������ĳ������ʱ������( ͬ��ͼ��������תʱ������ )
		hyw -- 2008.10.08
		"""
		pass

	def onLeaveAreaFS( self ) :
		"""
		defined method.
		���뿪ĳ������ʱ������( ͬ��ͼ��������תʱ������ )
		hyw -- 2008.10.08
		"""
		pass

	def onLoginSpaceIsFull( self ):
		"""
		define method.
		��½��ĳ������ ������Ա��
		"""
		pass

	# -------------------------------------------------
	def onAssaultEnd( self ) :
		"""
		defined method.
		������ʱ������
		"""
		pass

	def onUseFlyItem( self ):
		"""
		define method.
		ʹ����·��ص�
		"""
		pass

	# ----------------------------------------------------------------
	# ��Ҽ������
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
		��ʼ�������б�

		@param skills: like as [ skillID, ... ]
		"""
		pass

	def initSpaceSkills( self, skillIDList, spaceType ):
		"""
		Define method.
		����ռ�ʱ��õĿռ�ר�������б�

		param skillIDList : ARRAY OF SKILLID
		"""
		pass

	def enterEquipMake( self, entityID ):
		"""
		��װ���������
		@param entityID: ��������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_EQUIP_PRODUCE_WND" )

	def enterEquipExtract( self, entityID ):
		"""
		��װ�����Գ�ȡ����
		@param entityID: ��������
		"""
		ECenter.fireEvent( "EVT_ON_EXTRACT_EQUIP", entityID )

	def enterEquipPour( self, entityID ):
		"""
		��װ�����Թ�ע����
		@param entityID: ��������
		"""
		ECenter.fireEvent( "EVT_ON_POUR_EQUIP", entityID )

	def equipAttrRebuildSuccess( self ):
		"""
		���������ɹ�֪ͨ
		"""
		ECenter.fireEvent( "EVT_ON_EQUIP_ATTR_REBUILD_SUCCESS" )

	def onJumpNotifyFS( self, jumpMask ):
		"""
		Exposed method
		�ɷ��������ã��㲥�����пͻ��ˣ�����jump����
		"""
		self.playJumpActions( jumpMask )

	def playJumpActions( self, jumpMask ):
		"""
		������Ծ����
		"""
		jumpTime = jumpMask & csdefine.JUMP_TIME_MASK
		if jumpTime == csdefine.JUMP_TIME_UP1:
			self.isJumpProcess = True
			self.playVehicleSound()
		elif jumpTime == csdefine.JUMP_TIME_END:
			self.isJumpProcess = False

		if self.vehicleModelNum:
			if self.vehicleType != Define.VEHICLE_MODEL_STAND:	# ������ϵ���Ծ���������������⣩
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
					if not self.isSnake:	# Ǳ��״̬�±���⵽�Ų��Ź�Ч
						self.playJumpEffect()
				else:
					self.playJumpEffect()

		if self.inFlyDownPose: return	# ����ڲ���������pose���������е����䶯��֪ͨ������

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
		if actionNames.__class__.__name__ == "dict": #�����ƶ��;�ֹʱ�Ķ�������
			if hasattr( self,"isMoving" ) and self.isMoving():
				actionNames = actionNames.get( weaponIndex, [] )[1]
			else:
				actionNames = actionNames.get( weaponIndex, [] )[0]
		else:
			actionNames = actionNames[weaponIndex]

		self.setArmCaps()  #����caps��ȥ����Ծ����������walk��run��run_weapon�ȶ���
		rds.actionMgr.playActions( self.model, actionNames )

	def playJumpEffect( self ):
		"""
		��Ծ��Ч
		"""
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.JUMP_EFFECT_ID, self.getModel(), self.getModel(), type, type )
		if effect:
			effect.start()

	def onJumpAttackOver( self ):
		"""
		������������
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
		�����������
		"""
		if self.vehicleModelNum:	# ���������Ծ��Ч��һ����˵��Ϸ������������ʱ������ by����
			rate = random.random()	# ��Ծʱһ�����ʷ���
			if rate < 0.3:
				self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_JUMP )

	def onFlyJumpUpNotifyFS( self ):
		"""
		Exposed method
		�ɷ��������ã��㲥�����пͻ��ˣ��������и߶�
		"""
		self.flyJumpUp()

	def onEnterFlyState( self ):
		"""
		define method
		�������״̬
		"""
		pass

	def onLeaveFlyState( self ):
		"""
		define method
		�뿪����״̬
		"""
		pass

	def jumpBegin( self ):
		"""
		��Ծ���ֶ���(�������¶׵Ķ���)
		"""
		pass

	def flyJumpUp( self ):
		"""
		����������
		"""
		rds.actionMgr.playAction( self.model, Const.MODEL_ACTION_JUMP_BEGIN )

		if self.vehicleModelNum:	# ���������Ծ��Ч��һ����˵��Ϸ������������ʱ������ by����
			rate = random.random()	# ��Ծʱһ�����ʷ���
			if rate < 0.3:
				self.vehicleSound( self.vehicleModelNum, csdefine.VEHICLE_ACTION_TYPE_JUMP )

	def onGetBenefitTime( self, benefitTime ):
		"""
		defined method
		�ӷ�������ô���֮��buff�ۻ�ʱ�� by����
		"""
		pass

	def onGetServerVersion( self, version ):
		"""
		��ȡ�������˰汾
		"""
		ECenter.fireEvent( "EVT_ON_SEND_SERVER_VERSION",version )

	def canPlayEffectAction( self ):
		"""
		�Ƿ��ܲ���Ч������
		�������ܣ��񵲣�������
		"""
		# �������ϲ�����
		if self.vehicleModelNum: return False
		#if self.isActionning(): return False
		# ���������ܲ�����
		#if self.isInHomingSpell: return False
		# ѣ��״̬���޵�״̬������
		EffectState_List = csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_BE_HOMING
		if self.effect_state & EffectState_List != 0: return False
		return True

	def onReceiveDamage( self, casterID, skill, damageType, damage ):
		"""
		�˺���ʾ
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ʵ��
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		CombatUnit.onReceiveDamage( self, casterID, skill, damageType, damage )
		player = BigWorld.player()
		sk = skill
		petID = -1
		pet = player.pcg_getActPet()
		if pet:
			petID = pet.id
		# �Լ��������ʩ���߲���ʾ
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

		# ���ܲ����˺�ʱ��ͷ��������Ϣ�ȴ���
		if damage > 0:
			if ( damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
				# �����˺�
				ECenter.fireEvent( "EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE", self.id, str( damage ) )
			else:
				# ��ͨ�˺�
				ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( damage ) )
			# �񵲶���
			if ( damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
				if self.canPlayEffectAction():
					self.playActions( [resistActionName] )

		else:
			# ���ܶ���������ϲ����Ŵ˶���
			if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
				if self.canPlayEffectAction():
					self.playActions( [dodgeActionName] )


		# ���ܲ����˺�ʱ��ϵͳ��Ϣ�ȴ���
		receiverName = self.getName()
		if player.onFengQi:
			receiverName = lbs_ChatFacade.masked
		if casterID == player.id:					# �Լ���ʩ����
			if damage > 0:
				if ( damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s�м������%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_FROM_SKILL, receiverName, sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# ���%s������%s���%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_TO, sk.getName(), receiverName, damage )
				else:
					if (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
						if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:
							# %s�ܵ��㷴����%i�㷨���˺���
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC_TO, receiverName, damage )
						else:
							# %s�ܵ��㷴����%i���˺���
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_PHY_TO, receiverName, damage )
					else:
						# ���%s��%s�����%i���˺���
						player.statusMessage( csstatus.SKILL_SPELL_DAMAGE_TO, sk.getName(), receiverName, damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s���������%s��
					player.statusMessage( csstatus.SKILL_SPELL_DODGE_FROM_SKILL, receiverName, sk.getName() )
		elif casterID == petID: 					# ������ʩ����
			if damage > 0:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s�м�����ĳ����%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_RESIST_HIT_FROM_SKILL, receiverName, pet.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# �����%s������%s���%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DOUBLEDAMAGE_TO, pet.getName(), sk.getName(), receiverName, damage )
				elif (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
					if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:

						# ����Ч���������Ե������%i�㷨���˺���
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_MAGIC_TO, damage )
					else:

						# ����Ч���������Ե������%i���˺���
						player.statusMessage( csstatus.SKILL_BUFF_PET_REBOUND_PHY_TO, damage )
				else:
					# �����%s��%s�����%i���˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DAMAGE_TO, pet.getName(), sk.getName(), receiverName, damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s�����˳����%s��
					player.statusMessage( csstatus.SKILL_SPELL_PET_DODGE_TO, receiverName, pet.getName(), sk.getName() )

	def showTargetAttribute( self, targetID ):
		"""
		��ʾ�Է���ҵ���Ϣ(�۲칦��)
		@param   targetID: �Է���ҵ�ID
		@type    targetID: OBJECT_ID
		"""
		pass

	def showTargetEquip(self ,items , indexs):
		"""
		��ʾ�Է���ҵ�װ��(�۲칦��)
		@param   items: �Է���ҵĲ�����Ϣ
		@type    items: LIST
		@param   targetID: �Է���ҵ�ID
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
		��ҽ��մ�cell���������ϻ�ӳɹ�/ʧ�ܵ���Ϣ
		anim 0x01:		���ųɹ�
			 0x02:		����ʧ��
			 0x04:		�����̻�(�ѷ���)
		"""
		# ����ĿǰЧ���ϲ��ʱ����
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
		��ʾ�������ƽ���
		"""
		pass

	def onEquipGodWeapon( self ):
		"""
		define method
		�������ɳɹ�
		"""
		pass

	def showSkillName( self, skillID ):
		"""
		��ʾ��������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SKILL_NAME", self.id, skillID )	#��ʾ�ͷż��ܵ�����

	def onTalismanLvUp( self ):
		"""
		����������ʱ����
		"""
		pass

	def onRebuildAttrCB( self, grade, index, key ):
		"""
		define
		�������Ը���ɹ����������˻ص�
		"""
		pass

	def onActivatyAttrCB( self, grade, index ):
		"""
		define
		�������Լ���ɹ����������˻ص�
		"""
		pass

	def onTalismanSkillLvUp( self ):
		"""
		��������������ʱ����
		"""
		pass

	def startCopyTime( self, time ):
		"""
		��ʼ��������ʱ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ENTER_COPY", time > 0 )
		ECenter.fireEvent( "EVT_ON_COPY_TIME_CHANGE", time )

	def endCopyTime( self ):
		"""
		������������ʱ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_LEVEL_COPY" )

	def set_flags( self, old ):
		"""
		��ұ�Ǹı䣬Ŀǰ��ǵ������ǿ����Ӧ����ʾ��һ��������
		���磬�������flag 0��ʱ���ʾ���ͷ��Ҫ��ʾ��������ҡ�
		      �������flag 1��ʱ���ʾ���ͷ��Ҫ��ʾ��Я����Ѫ��Ʒ��
		��ʾ��ʽ�ı䣺�Ѿ�����ʾ�����޸�Ϊ��ʾͼ����		modify by gjx 2009-4-3
		"""
		RoleRelation.set_flags( self, old )
		hasFlyFlag = self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )
		flag = 1 << csdefine.ROLE_FLAG_FLY_TELEPORT
		oldHasFlyFlag = ( old & flag == flag )
		# ����ROLE_FLAG_FLY_TELEPORT��־
		if hasFlyFlag and not oldHasFlyFlag:
			#self.createFlyModel()
			self.cell.withdrawEidolonBeforeBuff()

		# �Ƴ�ROLE_FLAG_FLY_TELEPORT��־
		if not hasFlyFlag and oldHasFlyFlag:
			#self.onTeleportVehicleModeEnd()
			if hasattr( self, "resetCamera" ):
				self.resetCamera()
			self.cell.conjureEidolonAfterBuff()

		hasFlyFlag = self.hasFlag( csdefine.ROLE_FLAG_FLY )
		flag = 1 << csdefine.ROLE_FLAG_FLY
		oldHasFlyFlag = ( old & flag == flag )

		# ����ROLE_FLAG_FLY��־
		if hasFlyFlag and not oldHasFlyFlag:
			self.cell.withdrawEidolonBeforeBuff()

		# �Ƴ�ROLE_FLAG_FLY��־
		if not hasFlyFlag and oldHasFlyFlag:
			self.cell.conjureEidolonAfterBuff()

		self.updateRoleSign( old, csdefine.ROLE_FLAG_MERCHANT, "merchant" )		# �������̱��
		self.updateRoleSign( old, csdefine.ROLE_FLAG_BLOODY_ITEM, "bloodyItem" )# ����Я����Ѫ��Ʒ���
		#self.updateRoleSign( old, csdefine.ROLE_FLAG_ROBBING, "pillage" )		# ���½���������
		self.updateRoleSign( old, csdefine.ROLE_FLAG_CAPTAIN, "captain" )		# ���¶ӳ����
		self.updateRoleSign( old, csdefine.ROLE_FLAG_TEAMMING, "teammate" )		# ���·Ƕӳ���Ա���
		self.updateRoleSign( old, csdefine.ROLE_FLAG_CP_ROBBING, "pillage" )	# ���½���������
		self.updateRoleSign( old, csdefine.ROLE_FLAG_XL_ROBBING, "pillage" )	# ���½���������
		self.updateRoleSign( old, csdefine.ROLE_FLAG_CITY_WAR_FUNGUS, "cityWarer" )	# ��սĢ�����

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
		�Ƿ����������Ϣ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_HAS_HIDEINFO_FLAG", self, value )

	def set_safeAreaFlag( self, value ):
		"""
		�Ƿ��а�ȫ��������ʶ
		"""
		if self.isPlayer():														#���������Լ���ǿ��ˢ����Χ������ҵ�Ѫ��
			roles = self.entitiesInRange( csconst.ROLE_AOI_RADIUS, cnd = lambda ent : ent.getEntityType() == csdefine.ENTITY_TYPE_ROLE and ent.id != self.id )
			for role in roles:
				ECenter.fireEvent( "EVT_ON_ROLE_HAS_SAFEAREA_FLAG", role, value )
		else:
			ECenter.fireEvent( "EVT_ON_ROLE_HAS_SAFEAREA_FLAG", self, value )

	def set_actWord( self, old ):
		"""
		���actWord�ı�֪ͨ
		"""
		CombatUnit.set_actWord( self, old )
		if old != self.actWord:
			ECenter.fireEvent( "EVT_ON_ROLE_ACTWORD_CHANGED", self, old, self.actWord )

	def queryActivityScheme( self ):
		"""
		��ѯһ���������
		"""
		self.base.queryActivityScheme( self.queryActivitySchemeIndex )


	def onAddScheme( self, activityName, isStart, des, cmd, condition, area, activityType, line, star, persist  ):
		"""
		define method
		"""
		ActivitySchedule.g_activitySchedule.add( activityName, isStart, des, cmd, condition, area, activityType, line, star, persist  )

	def onOneActivityDataSendOver( self ):
		"""
		һ����������
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
		����˫������BUFF
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().cell.onSaveDoubleExpBuff()
		# "�Ƿ񻨷�1��������潱��ʱ�䣿"
		showMessage( mbmsgs[0x0122] ,"", MB_OK_CANCEL, query )

	def saveDanceBuff( self ):
		"""
		define method.
		��������BUFF
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().cell.saveDanceBuff()
		# "����ľ���ʱ���޷����ֵ���һ�죬�������Ƿ�ȷ�϶��ᡣ"
		showMessage( mbmsgs[0x0123],"", MB_OK_CANCEL, query )

	def onTeleportVehicleModeActionChanged( self, actionName ):
		"""
		define method.
		���贫��ģʽ�����ı�
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
		���贫��ģʽ����
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
		#�򿪸�������
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
		#�رո�������
		self.spaceSkillList = []
		self.spaceSkillInitCompleted = False
		self.spaceSkillSpaceType = -1

		ECenter.fireEvent( "EVT_ON_CLOSE_COPY_INTERFACE" )
		if self.copySpaceTimerID != 0:
			BigWorld.cancelCallback( self.copySpaceTimerID )

	def updateCopySpaceInfo( self, shownDetails ):
		"""
		shownDetails ����������ʾ����
		[
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
			8: �m؅Ѫ���ٷֱ�
			11:���Ȫm؅��ǰ�׶�
			12:��һ�����￪ʼʱ��(�°�m؅)
			13:�m؅Ѫ���ٷֱ�
			14:Բ��Ѫ��
			15:��ʾ/���ػ���ŭ��ֵ��ŭ��ֵҲ������Ѫ����ģ����治ͬ��
			16��ի��Ѫ���ٷֱ�
			17:�������boss
			18�����踱������ʾ�ĸ�����������
			19: ���踱��ÿ����ս������ʱ������
		]
		"""
		try:
			for shownItemNumber in shownDetails:
				if shownItemNumber == 0:
					startTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_START_TIME)			#��ʼʱ��
					persistTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME)		#����ʱ��
					ECenter.fireEvent( "EVT_ON_COPY_TIME_UPDATE", startTime, persistTime )									#ʣ��ʱ�����
				elif shownItemNumber == 1:
					monsterNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER)	#ʣ��С��
					if monsterNumber != "":
						ECenter.fireEvent( "EVT_ON_COPY_MONSTERS_UPDATE", int( monsterNumber ) )								#С�ָ���
				elif shownItemNumber == 2:
					monsterPassel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEVEL)			#ʣ��С������
					if monsterPassel != "":
						ECenter.fireEvent( "EVT_ON_COPY_PASSEL_UPDATE", monsterPassel )											#С�����θ���
				elif shownItemNumber == 3:
					bossNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS)		#ʣ��BOSS
					if bossNumber != "":
						ECenter.fireEvent( "EVT_ON_COPY_BOSS_UPDATE", int( bossNumber ) )										#BOSS����
				elif shownItemNumber == 4:
					mengmengNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_MENGMENG)		#ʣ����������
					ECenter.fireEvent( "EVT_ON_COPY_MENGMENG_UPDATE", int( mengmengNumber ) )								#������������
				elif shownItemNumber == 5:
					mowenhuNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_MOWENHU)		#ʣ��ħ�ƻ�����
					ECenter.fireEvent( "EVT_ON_COPY_MOWENHU_UPDATE", int( mowenhuNumber ) )									#ħ�ƻ���������
				elif shownItemNumber == 6:
					guiyingNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_GUIYINGSHI)		#ʣ�����Ӱʨ����
					ECenter.fireEvent( "EVT_ON_COPY_ZHENGUIYING_UPDATE", int( guiyingNumber ) )								#���Ӱʨ��������
				elif shownItemNumber == 7:
					nextTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME)		#��һ�����￪ʼʱ��
					if nextTime != "":
						ECenter.fireEvent( "EVT_ON_COPY_NEXT_LEVEL_TIME", nextTime )
				elif shownItemNumber == 8:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_YAYU_HP_PRECENT )		#�m؅Ѫ���ٷֱ�
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_YAYU_HP_PRECENT", hpp )
				elif shownItemNumber == csconst.SPACE_SPACEDATA_TREE_HP_PRECENT:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_TREE_HP_PRECENT )		#����Ѫ���ٷֱ�
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_TREE_HP_PRECENT", hpp )
				elif shownItemNumber == 9:
					gate = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_CHALLENGE_GATE )		#��ɽ�󷨵�ǰ����
					if gate != "":
						ECenter.fireEvent( "EVT_ON_COPY_CHALLENGE_GATE", gate )
				elif shownItemNumber == 10:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_POTENTIAL_FLAG_HP )	#ʥ����Ѫ���ٷֱ�
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_POTENTIAL_FLAG_HP", hpp )
				elif shownItemNumber == 11:
					batch = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_BATCH )				#���Ȫm؅��ǰ�׶�
					if batch != "":
						ECenter.fireEvent( "EVT_ON_COPY_YAYU_BATCH", batch )
				elif shownItemNumber == 12:
					nextTime = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME )#��һ�����￪ʼʱ��
					if nextTime != "":
						ECenter.fireEvent( "EVT_ON_COPY_NEXT_BATCH_TIME", nextTime )
				elif shownItemNumber == 13:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_YAYU_NEW_HP )		#�m؅Ѫ���ٷֱ�
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_COPY_YAYU_NEW_HP", hpp )
				elif shownItemNumber == 14:
					ECenter.fireEvent( "EVT_ON_TRIGGER_CIRCLE_HP_BAR", True )										# ��ʾԲ��Ѫ��
				elif shownItemNumber == 15:
					isShow = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_ANGER_ISSHOW )
					ECenter.fireEvent( "EVT_ON_TRIGGER_CIRCLE_ANGER_BAR", eval( isShow ) )									# ��ʾ�����ػ���ŭ��ֵ
				elif shownItemNumber == 16:
					anger = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_ZHANNAN_ANGER_PERCENT )
					if anger != "":
						ECenter.fireEvent( "EVT_ON_COPY_TREE_ANGER_PRECENT", anger )							# ի��ŭ���ٷֱ�
				elif shownItemNumber == 17:
					bossNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS )		#ʣ��BOSS
					totalBossNumber = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_TOTAL_BOSS )	#BOSS������
					if bossNumber != "" and totalBossNumber != "":
						ECenter.fireEvent( "EVT_ON_COPY_SHMZ_BOSS_UPDATE", int( bossNumber ), int( totalBossNumber ) )		#BOSS����
				elif shownItemNumber == 18:
					comoboPoint = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_DANCECOPY_COMOBOPOINT )  #���踱������
					ECenter.fireEvent("EVT_ON_DANCECOPY_DATA_UPDATE_COMOBOPOINT", int(comoboPoint))
				elif shownItemNumber == 19:
					time = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_DANCECHALLENGE_TIMELIMIT)  #��ս���踱��ʱ������
					ECenter.fireEvent("EVT_ON_DANCECOPY_DATA_UPDATE_TIMILIMIT", int(time))
				elif shownItemNumber == 20:
					try:
						percent = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_COPY_MMP_YAOQI_PERCENT)  #���������������ٷֱ�
					except:
						percent = 0
					ECenter.fireEvent("EVT_ON_MMP_YAOQI_PERCENT_CHANGED", float(percent))
				elif shownItemNumber == 21:
					monsterPassel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_WAVE)			#ʣ����ﲨ��
					if monsterPassel != "":
						ECenter.fireEvent( "EVT_ON_COPY_MONSTER_WAVE_UPDATE", monsterPassel )
				elif shownItemNumber == 22:
					hpp = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NPC_HP_PRECENT )				#NPCѪ���ٷֱ�
					if hpp != "":
						ECenter.fireEvent( "EVT_ON_NPC_HP_UPDATE", hpp )
		except:
			pass
		functor = Functor( self.updateCopySpaceInfo, shownDetails )
		self.copySpaceTimerID = BigWorld.callback( 1, functor )

	def startKLJDActivity( self ):
		"""
		���ҵ�����
		"""
		pass

	def endKLJDReward( self ):
		"""
		һ���ҵ�����
		"""
		pass

	def startSuperKLJDActivity( self ):
		"""
		���ҵ�����
		"""
		pass

	def receiveRequestDance( self, requestEntityID ):
		"""
		���ܵ����빲��
		"""
		pass

	def askSuanGuaZhanBu( self, money ):
		"""
		���ܵ�����ռ��
		"""
		pass

	def stopRequestDance( self ):
		"""
		ȡ�����빲��
		"""
		pass

	def onNPCOwnerFamilyNameChanged( self, npcID, ownerName ):
		"""
		"""
		pass

	def onTeamCompetitionStart( self ):
		"""
		define method
		��Ӿ������ʼ
		"""
		ECenter.fireEvent( "EVT_ON_TEAM_COMPETITION_START" )
		self.teamCompetitionTimerID = BigWorld.callback( 2, self.teamCompetitionPointRefresh )
		BigWorld.callback( 2, self.onUpdateRoleNameColor )

	def onUpdateRoleNameColor( self ):
		"""
		����������ֵ���ɫ
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_PK_STATE_CHANGED", self )


	def onEnterTeamCompetitionSpace( self, endTime ):
		"""
		define method
		������Ӿ���������
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_TEAM_COMPETITION_SPACE", endTime )

	def onLeaveTeamCompetitionSpace( self ):
		"""
		define method
		�뿪��Ӿ���������
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_TEAM_COMPETITION_SPACE" )

	def onTeamCompetitionEnd( self ):
		"""
		define method
		��Ӿ��������
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


#----------------���ﶨ�巴��ҵĿսӿ�---------------------------------------------
	def clientRecvApexMessage( self, strMsg,nLength ):
		"""
		�յ�����ҵ����� ����Ĵ����Ƶ�playerRole,�����ǿսӿ�
		"""
		None

	def sendApexMessage( self, strMsg,nLength ):
		"""
		���ͷ���ҵ�����
		"""
		None

	def startClientApex( self ):
		"""
		�𶯿ͻ��˵ķ����
		"""
		None

	def alertMessageBox( self, msgContent, msgTitle ):
		"""
		define method.
		�ӷ������˴�һ����Ϣ�������ڿͻ��˵���һ���Ի���
		"""
		showMessage( msgContent, msgTitle, MB_OK )



	def disDartEntity( self, vehicleID, seat ):
		"""
		define method
		���ڳ�ר��
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
		������ѡ�����
		"""
		CommissionSale.instance().show()


	def onReceiveQueryShopInfo( self, roleDBID, roleName, shopName ):
		"""
		defined method
		�������۵��̲�ѯ��Ϣ
		"""
		ECenter.fireEvent( "ON_RECEIVE_COMMISSION_SHOP_INFO", roleDBID, roleName, shopName )

	def onReceiveQueryItemInfo( self, roleDBID, itemUID, item, price, roleName, shopName ):
		"""
		define method
		����������Ʒ��ѯ��Ϣ
		"""
		ECenter.fireEvent( "ON_RECEIVE_COMMISSION_GOODS_INFO", roleDBID, itemUID, item, price, roleName, shopName )

	def onReceiveQueryPetInfo( self, roleDBID, dbid, pet, price, roleName, shopName ):
		"""
		define method
		�������۳����ѯ��Ϣ
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
	# �д�
	# --------------------------------------------------
	def onReceivedQieCuo( self, targetID ):
		"""
		�յ��д�����
		"""
		pass

	def onRequestQieCuo( self, targetID ):
		"""
		�����д�����ɹ�
		"""
		print "self.id", self.id, BigWorld.player().id, targetID
		target = BigWorld.entities.get( targetID )
		if target is None: return
		self.qieCuoTargetID = targetID
		# ������
		dsVector3 = target.position - self.position
		dtPosition = self.position + ( dsVector3.x/2, dsVector3.y, dsVector3.z/2 )
		#������ײ���� ���⸡�ڿ���
		endDstPos = csarithmetic.getCollidePoint( self.spaceID, dtPosition + (0,10,0), dtPosition + (0,-10,0) )
		func = Functor( self.onQieCuoQiZiModelLoad, endDstPos, targetID )
		rds.effectMgr.createModelBG( [Const.QIECUO_QIZI_MODEL_PATH], func )
		# �������ƶ���
		#ECenter.fireEvent( "EVT_END_GOSSIP" ) # �ر����д���
		if self.vehicleModelNum == 0:
			rds.actionMgr.playAction( self.model, Const.MODEL_ACTION_DEFY )

	def onQieCuoEnd( self ):
		"""
		Define Method
		�д����
		"""
		self.delQieCuoQiZiModel()

	def onQieCuoQiZiModelLoad( self, dtPosition, targetID, model ):
		"""
		�д����Ӽ�����ɻص�
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
		ɾ���д�����ģ��
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
		����ͼƬ��֤

		@param imageData : ��֤ͼƬ���ݣ�STRING
		@param count : �ڼ�����֤
		"""
		DEBUG_MSG( "--->>>imageData", count, imageData )

	def onBuyPointCardInterface( self ):
		"""
		define method
		�򿪹���㿨����
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_POINT_CARD_BUY_WINDOW" )

	def onSellPointCardInterface( self ):
		"""
		define method
		�򿪳��۵㿨����
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_POINT_CARD_SELL_WINDOW" )

	def onAddPointCard( self, cardInfo ):
		"""
		define method
		����һ���㿨��Ϣ
		"""
		print cardInfo


	def removePointCard( self, cardNo ):
		"""
		define method
		�Ƴ�һ���㿨
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
		��Ὰ�����ʼ
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
		�����Ὰ��
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_FAMILY_COMPETITION_SPACE", endTime )

	def onLeaveFamilyCompetitionSpace( self ):
		"""
		define method
		�뿪��Ὰ��������
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_FAMILY_COMPETITION_SPACE" )


	def onFamilyCompetitionEnd( self ):
		"""
		define method
		��Ὰ������
		"""
		if hasattr( self, "tongCompetitionTimerID" ) and self.tongCompetitionTimerID != 0:
			BigWorld.cancelCallback( self.tongCompetitionTimerID )


	def onEnterRoleCompetitionSpace( self, endTime ,pkProtectTime):
		"""
		define method
		������˾���������
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_ROLE_COMPETITION_SPACE", endTime ,pkProtectTime)



	def onLeaveRoleCompetitionSpace( self ):
		"""
		define method
		�뿪���˾���������
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_ROLE_COMPETITION_SPACE" )


	def onRoleCompetitionEnd( self ):
		"""
		define method
		���˾�������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_COMPETITION_END" )
		pass

	def onShowExp2PotWindow( self, objectID ):
		"""
		��ʾ���黻Ǳ�ܽ���
		"""
		pass

	def onUpdateOwnCollectionItem( self, ownCollectionItem ):
		"""
		define method
		�����Լ��չ���һ����Ʒ
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_VEND_PURCHASING_ITEM", ownCollectionItem )

	def onUpdateCollectionItem( self, collectionItem ):
		"""
		define method
		�����Լ��չ���һ����Ʒ
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_TISHOU_PURCHASING_ITEM", collectionItem )

	def onClearCollectionTable( self, collectorDBID ):
		"""
		define method
		����չ����
		"""
		if self.databaseID == collectorDBID :
			ECenter.fireEvent( "EVT_ON_TS_PURCHASING_ITEM_CLEAR" )
		else :
			ECenter.fireEvent( "EVT_ON_TS_PURCHASED_ITEM_CLEAR" )

	def onAFLimitTimeChanged( self, af_time_limit ):
		"""
		define method
		�뿪�Զ�ս��״̬�ص�
		"""
		pass

	def onAFLimitTimeExtraChanged( self, af_time_extra ):
		"""
		define method
		�뿪�Զ�ս��ʱ��ص�2
		"""
		pass

	def openFeichengwuraoInterface( self ):
		"""
		�򿪷ǳ����Ź������
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
		װ��Ʒ�ʷ���
		"""
		ECenter.fireEvent( "EVT_ON_RAISE_EQUIP_QUALITY", npcId )

	def enterEquipAttrRebuild( self, npcId ) :
		"""
		װ����������
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
		10��������չ������
		"""
		ECenter.fireEvent( "EVT_ON_DISPLAY_SCENE", sceneId )

	def onCameraFly( self, graphID, startPos ):
		"""
		Define Method
		����ͷ����
		"""
		pass

	def interruptAttackByServer( self, reason ):
		"""
		define method
		server ֪ͨ��Ϲ�����Ϊ
		"""
		pass

#-------------------------���������صļ��Start by mushuang-------------------------#
	def enableFlyingRelatedDetection( self, spBoundingBoxMin, spBoundingBoxMax ):
		"""
		defined method
		@enableFlyingRelatedDetection: �����ͷ����йصļ��
		@spBoundingBoxMin: �ռ���Ӻе�һ���ԽǶ���
		@spBoundingBoxMax: ��spBoundingBoxMin��Ե���һ���ԽǶ���
		"""
		pass

	def disableFlyingRelatedDetection( self ):
		"""
		defined method
		@disableFlyingRelatedDetection: �رպͷ����йصļ��
		"""
		pass
#-------------------------���������صļ��End by mushuang-------------------------#

	def visibleRootUIs( self, visible ) :
		"""
		define method
		������֪ͨ��ʾ/���ص�ǰ����
		@param		visible : ��ʾ/���ر��
		@type		visible : bool
		"""
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", visible )

	def unifyYaw( self ):
		"""
		��$p.yaw��dcursor().yawͳһ�������ڷ�ֹ����Entity.teleport()��direction��ʧЧ�����⡣

		ͨ����ͨ��Entity.teleport()����ʱ������һ��direction�������������ڱ�ʾ��Ҵ���֮��ķ���
		���ǣ����ֱ��teleport(),���磺cell��player.teleport( None, somePosition, ( 0, 0 ,yaw ) ),
		�ڿͻ��˻ᷢ����ұ����ͺ�ķ�����Ȼû�иı䣬��������ԭ���ĳ��򣬿���ȥ����yaw����û�������á�
		������������ԭ����BW�����и����Խ�dcursor��ͨ��BigWorld.dcursor()��ȡ����dcursor.yaw�ᶨʱ��
		������$p.yaw����ʵ�ϣ�player.teleport( None, somePosition, ( 0, 0 ,yaw ) )������õ�ȷ�ı���$p.yaw,
		��dcursor������tick�н��Լ���yawֵд����$p.yaw����������yaw������ʧЧ������

		������cell������teleport()����֮����ô˽ӿڣ��Է������������⡣ by mushuang
		"""
		BigWorld.dcursor().yaw = BigWorld.player().yaw

	def changeWorldCamHandler( self, camControlType, yaw = -9.4, pitch = 3.766 ):
		"""
		Define method.
		������������Ʒ�ʽ
		"""
		rds.worldCamHandler = Const.g_worldCamHandlers[camControlType]
		if camControlType == csdefine.NORMAL_WORLD_CAM_HANDLER:
			rds.worldCamHandler.use()
		else:
			rds.worldCamHandler.use( yaw, pitch )

	def enterYXLMChangeCamera( self ):
		"""
		����Ӣ�����˸����ı侵ͷ
		"""
		if "ying_xiong_lian_meng_01" == BigWorld.getSpaceName( self.spaceID ):
			self.changeWorldCamHandler( 2, 3, 4 ) # �̶���ͷ,yawΪ3,pitchΪ4

	def levelYXLMChangeCamera( self ):
		"""
		�뿪Ӣ�����˸�����ͷ�ָ�
		"""
		self.changeWorldCamHandler( 1 )

	def setFogDistance( self, fogFarScale, fogNearScale ):
		"""
		Define method
		������ֵ
		"""
		csol.setChunkModelLodMaxDistance( fogFarScale, fogNearScale )

	def setFarPlane( self, farPlane ):
		"""
		Define method
		����Զ�ü���
		"""
		BigWorld.setGraphicsSetting( "FAR_PLANE", farPlane )

	def switchFlyWater( self, switch ):
		"""
		�������࿪��
		"""
		pass

	def set_onWaterArea( self, oldValue ):
		"""
		"""
		self.setArmCaps()

	def onSwtichWaterParticle( self, actionName ):
		"""
		����ˮ���ƶ�Ч��
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
		����ˮ���ƶ�Ч��
		"""
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.JUMP_WATER_EFFECTID, self.model, self.model, type, type )
		if effect is None: return
		effect.start()

	def startFlyWaterParticle( self ):
		"""
		��ʼˮ������Ч��
		"""
		if not self.inWorld: return
		if not self.onWaterArea: return
		self.switchFlyWaterParticle()
		self.flyWaterTimerID = BigWorld.callback( Const.JUMP_WATER_EFFECT_TIME, self.startFlyWaterParticle )
		#�貨΢��ˮ����Ч����
		rds.soundMgr.playVocality( Const.WATER_FLY_SOUND, self.getModel() )

	def stopFlyWaterParticle( self ):
		"""
		�ر�ˮ������Ч��
		"""
		if not self.inWorld: return
		BigWorld.cancelCallback( self.flyWaterTimerID )
		self.flyWaterTimerID = 0
		#�貨΢��ˮ����Ч�ر�
		rds.soundMgr.stopVocality( Const.WATER_FLY_SOUND, self.getModel() )

	def onLeaveWaterCallback( self, volumeID ):
		"""
		"""
		pass

	# ---------------------------------------------------------
	def showCastIndicator( self, idtId ) :
		"""
		Define method
		@param   idtId: ����/���߲�����ʾ��ID�б�
		@type    idtId: ARRAY of UINT16
		"""
		rds.castIndicator.indicateCast( idtId )

	def hideCastIndicator( self, idtId ) :
		"""
		Define method
		@param   idtId: ����/���߲�����ʾ��ID
		@type    idtId: ARRAY of UINT16
		"""
		rds.castIndicator.shutIndication( idtId )

	#--------------------------------------------------------------
	# ��������������
	# -------------------------------------------------------------
	def showQuestTrapTip( self, entityID ):
		"""
		Define method
		@param	entityID:	�����ID
		@type	entityID��	OBJECT_ID
		"""
		ECenter.fireEvent( "EVT_ON_TRAP_QUEST_TIP_SHOW", entityID )

	def hideQuestTrapTip( self, entityID ):
		"""
		Define method
		@param	entityID:	�����ID
		@type	entityID��	OBJECT_ID
		"""
		ECenter.fireEvent( "EVT_ON_TRAP_QUEST_TIP_HIDE", entityID )


	def playVideo( self, fileName ):
		"""
		Define method
		@param	fileName:	��Ƶ�ļ�
		@type	fileName��	string
		"""
		self.playingVideo = True
		csol.prepareVideo("videos/" + fileName )
		csol.playVideo()
		csol.setVideoCallback( self.onVideoEvent )

	def playSound( self, fileName, typeID, id, priority ):
		"""
		Define method add by wuxo 2012-1-17
		@param	fileName:	��Ƶ�ļ�·��
		@type	fileName��	string
		@param	typeID:	        ���� 2D/3D
		@type	fileName��	UINT
		@param	NPCID:	        NPC��id
		@type	fileName��	UINT
		"""
		pass

	def playSoundFromGender( self, fileName, id, flag ):
		"""
		Define method
		����ְҵ�Ĳ�ͬ������ҵĿͻ��˲��Ų�ͬ·������Ч
		"""
		pass

	def clearVideo( self ):
		"""
		"""
		csol.clearVideo()

	def onVideoEvent( self, event ):
		if event == "ON_COMPLETE":
			self.playingVideo = False
			#��Ƶ���Ž�����Ҫ�ж�BUFFER
			self.cell.onCompleteVideo() #add by wuxo 2011-11-26
			BigWorld.callback( 0.1, self.clearVideo )

	def setCameraFlyState(self,eventIDs):
		"""
		����CameraFly������״̬by wuxo 2011-11-26
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
		��ʼ����ҵı�����־��Ϣ����ض����csdefine.MATCH_TYPE_***

		��������UINT8��matchType

		���˾�������Ӿ�������Ὰ����
		�ϴβ�����û���INT32��param1
		�ۼƲ�����û���INT32��param2

		�����ᣬ�����̨�������̨:
		�ϴβ����������INT32��param1
		�����ò�������INT32��param2
		"""
		DEBUG_MSG( "match info:", matchType, param1, param2 )
		ECenter.fireEvent( "EVT_ON_INIITE_MATCH_RECORD", matchType, param1, param2 )

	def updateMatchRecord( self, matchType, param ):
		"""
		Define method.
		������ҵı�����־��Ϣ���������������ݣ��ͻ�������һ��ѯ��ǣ�����ͻ���û�в�ѯ��������ݣ���ô�ٴδ򿪽���ʱ��Ҫ���������ѯ��
		����ͻ����Ѿ����ܻ��ֻ�����ʷ����������ݣ�����ʾ���������ݼ��ɡ�

		��������UINT8��matchType,��ض����csdefine.MATCH_TYPE_***

		���˾�������Ӿ�������Ὰ����
		�ϴβ�����û���INT32��param

		�����ᣬ�����̨�������̨:
		�ϴβ����������INT32��param
		"""
		DEBUG_MSG( "match info:", matchType, param )
		ECenter.fireEvent( "EVT_ON_UPDATE_MATCH_RECORD", matchType, param )

	def isGMWatcher( self ) :
		"""
		�Ƿ���GM�۲���״̬
		"""
		return self.effect_state & csdefine.EFFECT_STATE_WATCHER != 0

	def isDeadWatcher( self ) :
		"""
		�Ƿ��������۲���״̬
		"""
		return self.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER != 0

	def updateSkill( self, floder, skillID ):
		"""
		define method
		���¿ͻ��˼��ܣ���Ҫ��֧�ּ��ܵı߲����Ĺ�����ʽ��
		"""
		Skill_test.updateSkill( floder, skillID )

	def updateItem( self, floder, ItemID ):
		"""
		define method
		���¿ͻ��˼��ܣ���Ҫ��֧�ּ��ܵı߲����Ĺ�����ʽ��
		"""
		Item_test.updateItem( floder, ItemID )

	def lineToPoint( self, position, speed ):
		"""
		�ƶ��������
		"""
		pass

	def doRandomRun( self, centerPos, radius ):
		"""
		define method
		�ߵ�centerPosΪԭ�㣬radiusΪ�뾶�����������
		"""
		pass

	def infoTongMember( self, lineNumber, casterName, showMessage, spaceName, position, direction ):
		"""
		define method.
		����Ƕ���˶�����������Ϣ�����Ŷӹ��򣬵�ǰһ����ʧ�Żᵯ���ڶ���������ʾ�򣬶�ͬ
		һ���ٻ���ֻ�����һ����ʾ�����������һ���ٻ����������ٻ�ȡ��
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
		ʵʱ�������Ӵ�������
		"""
		player = BigWorld.player()
		if player is None:
			return Define.TYPE_PARTICLE_OP

		if player.targetEntity == self:
			return Define.TYPE_PARTICLE_PIOP

		return Define.TYPE_PARTICLE_OP

	# ----------------------------------------------------------------------------------
	# Ӣ�����˸����������
	# ----------------------------------------------------------------------------------
	def onShowYXLMCopyNPCSign( self, copySpaceLabel ):
		"""
		define method
		Ӣ�����˸�����NPCλ����ʾ����
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_YXLMCOPY_MINIMAP", copySpaceLabel )

	def onCloseYXLMCopyNPCSign( self ):
		"""
		define method
		Ӣ�����˸����ر�NPCλ����ʾ����
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_YXLMCOPY_MINIMAP" )

	def onShowYXLMCopyBossSign( self, id, className, spawnPos, relation, signType ):
		"""
		define method
		boss�����ء�����������ʱ��ʾ���
		"""
		ECenter.fireEvent( "EVT_ON_SET_YXLMCOPY_BOSS_SPAWN_SIGN", id, className, spawnPos, relation, signType )

	def onUpdateYXLMCopyBossPos( self, id, className, pos, relation ):
		"""
		define method
		����Bossλ����Ϣ
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_YXLMCOPY_BOSS_SIGN", id, className, pos, relation )

	def onYXLMCopyBossDied( self, id, className, spawnPos, diedPos, relation ):
		"""
		boss�����ء������� ����ʱ���±��
		"""
		ECenter.fireEvent( "EVT_ON_SET_YXLMCOPY_BOSS_DIED_SIGN", id, className, spawnPos, diedPos, relation )

	def onYXLMMonsterGetDamage( self, id, seconds ):
		"""
		������������ܵ�һ���̶��˺�ʱ����
		"""
		ECenter.fireEvent( "EVT_ON_MONSTER_GET_DAMAGE", id, seconds )

	def baoZangOnReceiveEnemyPos( self, enemyId, pos ):
		"""
		define method
		���ն��ѷ����ĵ���λ����Ϣ
		"""
		ECenter.fireEvent( "EVT_ON_PVP_ON_RECEIVE_ENEMY_POS", enemyId, pos )

	def baoZangOnDisPoseEnemy( self, enemyId ):
		"""
		define method
		ɾ�����˱��
		"""
		ECenter.fireEvent( "EVT_ON_PVP_ON_DISPOSE_ENEMY_SIGN", enemyId )

	def onPKListChange( self, pkTargetList, id ):
		"""
		define method
		PK�б����ı�
		"""
		pass

	def set_sysPKMode( self, oldValue ):
		"""
		ϵͳĬ��PKģʽ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_SYSPKMODE_CHANGED", self, self.sysPKMode )

	def set_pkMode( self, oldValue ):
		"""
		pkģʽ�ı�
		"""
		self.refurbishHPColor()

	def refurbishHPColor( self ):
		"""
		ˢ��ͷ��Ѫ����ɫ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_PKMODE_CHANGED", self, self.pkMode )

	def canPkPlayer( self ):
		"""
		�ж�role�Ƿ����PK playerRole
		"""
		player = BigWorld.player()
		if self.id == player.id:return False
		# ����ͬһ��ͼ����PK
		if self.spaceID != player.spaceID:
			return False

		# ��ɫ���ڵ�ͼ�Ƿ�����pk
		if self.getCanNotPkArea(): return False

		# ������ڷ���״̬��������pk
		if isFlying( self ): return False

		# 30����ұ���
		if self.pkState == csdefine.PK_STATE_PROTECT: return False

		# �����Ա����PK
		if self.isTeamMember( player.id ):
			return False

		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and not player.actionSign( csdefine.ACTION_FORBID_PK ):
			if player.inDamageList( self ) or player.pkTargetList.has_key( self.id ):
				return True

		# 30���Է���ҽ�ֹpk
		if player.pkState == csdefine.PK_STATE_PROTECT:
			return False


		if self.sysPKMode:
			# ����ҵ�pkģʽ��ϵͳ��ƽģʽ
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_PEACE:
				return False


			# ��ս�����а���Ա����PK
			if self.tong_dbID != 0 and ( self.tong_dbID == player.tong_dbID ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG:
				return False

			# ��Ӫս��������Ӫ��Ա����PK
			if self.getCamp() != 0 and ( self.getCamp() == player.getCamp() ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP:
				return False

			if self.id in player.teamMember and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TEAMMATE:
				return False

			# ϵͳģʽΪ����ģʽ
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_LEAGUE:
				if self.checkCityWarTongBelong( self.tong_dbID, player.tong_dbID ):
					return False
		else:
			# ����ҵ�pkģʽ������ģʽ��ԭ�ƶ�ģʽ������entity���ǻƺ���
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_RIGHTFUL and player.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ]:
				return False

			# ����ҵ�pkģʽ������ģʽ����entity���ǻƺ���
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_JUSTICE and player.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ] \
				and self.getCamp() == player.getCamp():
				return False


		# �Է�����Ӹ���״̬�¿ɹ���
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and player.isFollowing():
			return True

		# ����ұ���ֹPK������Ҫpk��entity����ֹpk������ĳ���ڰ�ȫ����
		if self.actionSign( csdefine.ACTION_FORBID_PK ) or player.actionSign( csdefine.ACTION_FORBID_PK ):
			return False
		return True

	def getCanNotPkArea( self ) :
		"""
		���ڵ�ͼ�Ƿ�����pk
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
		��鵱ǰ�����Ƿ�����PK�����������������м�飬
		���������֮��Ĺ�ϵ
		"""
		# �ý�ɫ���ڵ�ͼ�Ƿ�����pk
		if self.getCanNotPkArea(): return False

		# ��ǰ�Ƿ�����ս״̬
		if self.effect_state & csdefine.EFFECT_STATE_NO_FIGHT :
			return False

		return True

	def onUpdateIntensifyItem( self, uid ):
		"""
		define method
		ǿ����Ʒ�����ı�
		"""
		pass

	def onOpenSpaceTowerInterface( self ):
		"""
		define method
		�����Ȫm؅����������
		"""
		pass

	def onCloseSpaceTowerInterface( self ):
		"""
		define method
		�ر����Ȫm؅����������
		"""
		pass

	def enterTowerDefenceSpace( self ):
		"""
		define method
		�������������ĸ���
		"""
		pass

	def addTowerDefenseSpaceSkill( self, skillID, spaceType ):
		"""
		define method
		�������������ĸ�������
		"""
		pass

	def endTowerDefenseSpaceSkill( self ):
		"""
		define method
		��������������������
		"""
		pass

	def showHeadPortraitAndText( self, type, monsterName, headTextureID, text, lastTime ):
		"""
		define method
		��ʾͷ�������
		"""
		pass

	def canChallengeDanceKingCb(self, index, result):
		#1��ʾ������ս
		#2��ʾ���ڱ���ʱ��
		#3��ʾ��������ս
		pass


	def addDancingKingInfo(self, index, dancingKingInfo):
		#Define method
		#���շ��������͵�������Ϣ���ڽ�������ʱ���ɷ���������
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
		��ѯ���װ������
		"""
		pass

	def onShowPatrol( self, path, model  ):
		"""
		define method
		��ʾ�ڵ�Ѱ··��
		"""
		pass

	def planeSpacePrepare( self ):
		"""
		Define method.
		λ�洫�ͽ�Ҫ��ʼ��
		"""
		pass



	def canGetDancePositionCb(self, index):
		"""
		define method
		���λ�õĻص�
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
	# �ƶ�ģʽ
	MOVE_WALK			= 1						# ��·
	MOVE_RUN			= 2						# �ܲ�
	MOVE_FLY			= 3						# ����( ��ʱû�� )
	INVALIDITY_POS		= Math.Vector3( -100000000, -100000000, -100000000 ) #��־Ϊ��Ч��ֵ

	def onBecomePlayer( self ):
		"""
		����Ϊ��ɫʱ������
		"""
		INFO_MSG( "PlayerRole::onBecomePlayer!" )
		self.actionState = 0						# ָ����ҵ�ǰ����ʲô״̬
		self.c_control_mod = Const.CAMERA_CONTROL_MOD_2	# ���ÿ��Ʒ�ʽ

		OPRecorder.__init__( self )
		Action.Action.__init__( self )
		Attack.__init__( self )
		Guide.__init__( self )
		Team.onBecomePlayer( self )
		self.setSelectable( False )						# ����Ϊ����ѡ���Լ�

		self.__bindShortcuts()
		self.moveTime = 0.0 #����ѣ���µ��ƶ�
		self.isRolesVisible = True					# ������ɫ�Ƿ�ɼ���hyw--2009.1.10��
		self.isRolesAndUIVisible = True					#������ɫ(����UI)�Ƿ�ɼ�
		self.isShowSelf = True                                          #�Ƿ���ʾ�Լ�
		self.allowInvite = True						# ��������	14:18 2008-6-24 yk
		self.allowTrade  = True						# ������	14:18 2008-6-24 yk
		self.controlForbid = 0						# ��ҿ�������

		self.jumpHeight1  = Const.JUMP_LAND_HEIGHT		# 1�����߶�
		self.jumpHeight2  = Const.JUMP_LAND_HEIGHT2           #2�����߶�
		self.jumpHeight3  = Const.JUMP_LAND_HEIGHT3          #3�����߶�

		self.isJump2 = False            #����2�����ɹ�����ǣ�dojump�����˾���ɹ���
		self.isJump3 = False            #����3�����ɹ�����ǣ�dojump�����˾���ɹ���
		self.startHeight = 0            #��ǰ��Ծ�������߶�
		self.wasdFlagTime = [ 0, 0, 0, 0 ]              #ǰ��/����/����/���ư�������ʱ��ʱ��
		self.wasdFlag     = [ False,False,False,False ]  #ǰ��/����/����/���ư������ΰ��������Ѹ���ƶ����
		self.key          =  None #��һ�εİ���
		self.isSameKey    = False #�ϴΰ����ͱ��ΰ����Ƿ���ͬ
		self.isPlayWaterRun = False #�Ƿ񲥷�ˮ�ж���
		self.jumpTime	= 0.0 						# �����Ծ���̵�ʱ��
		self.geneGravity = Const.JUMP_GENEGRAVITY 						# ��������������ʱ��������

		self.__moveMode = self.MOVE_RUN				# �ƶ�ģʽ( hyw--2008.12.29 )
		self.__jumpCBID = 0
		self.__jumpPos = ( 0, 0, 0 )
		self.__isAssaulting = False					# �Ƿ��ڳ��״̬( hyw--09.01.12 )
		self.__expectTarget = ""					# ��Ҫ�Ի���Ŀ��� className

		rds.gameMgr.onBecomePlayer()				# hyw -- 2008.01.20
		self.lotteryItems = {}						# �洢�������������������

		self.vehicleDBID = 0						# ��¼�����dbid
		self.vehicleDatas = {}						# ��¼���������
		self.activateVehicleID = 0					# ��¼�ļ������dbid

		rds.shortcutMgr.setHandler( "OTHER_TOGGLE_ROLES_MODEL", self.__toggleOtherRoles )			# ��ʾ/����������ɫģ��
		rds.shortcutMgr.setHandler( "COMBAT_SWITCH_PKMODEL", self.__switchPkMode )					# �л�PKģʽ

		self.queryActivitySchemeIndex = 0
		self.queryActivityScheme()

		self.statistic = {}
		self.initStatistic()						# ��ʼ�����顢��Ǯ��Ǳ�ܡ��ﹱ
		self.initMailbox()							# ��ʼ������

		self.currentShowMessage = None				# ��¼��ǰ�򿪵�showMessage
		self.__followCallBack = 0					# ����Ļص�����
		self.currentItemBoxID = 0					# ��ǰ��ͨ��Ʒ��ʰȡ��ID
		self.currentQuestItemBoxID = 0				# ��ǰ������Ʒ��ʰȡ��ID
		self.onLineTimer = None						# �������ʱ��Ŀͻ����ۻ���ʱ��
		self.onLineTimeTick = 0.0					# �������ʱ��Ŀͻ����ۻ�����
		self.benefitTime = 0.0						# ��ʼ��ʱ��¼�������ʱ��
		self.__spanSpaceDstLabel = ""				# �����糡��Ѱ·��Ŀ�곡����
		self.__spanSpaceDstPos = Math.Vector3( self.INVALIDITY_POS ) # �����糡��Ѱ·��Ŀ��λ��
		self.__spanSpaceDataLock = False			# ��ֹ�糡��Ѱ·��Ϣ���ݲ����۸�
		self.__spanSpaceNearby = 0					# ����糡��Ѱ·�£��ƶ���Ŀ��λ�ø����ľ���
		self.__spanSpaceTarget = ""					# ����糡��Ѱ·�µ�expectTarget
		self.onWaterJumpTimer = None				# ˮ����Ծ�ص�

		# ���������ģ�� by mushuang
		self.__flyingVehicle = FlyingVehicle( self )
		self.onFlyModelLoadFinished = False

		self.oksData = {}	# һ����װ����

		# ����濪��TimeOfDay����
		if Language.LANG == Language.LANG_BIG5:
			rds.enEffectMgr.start()
		self.spaceSkillList = []				# �ռ�ר������id�б�14:35 2010-4-27��wsf
		self.spaceSkillInitCompleted = False	# �ռ�ר�������Ƿ��ʼ�����
		self.spaceSkillSpaceType = -1			# �ռ�ר���������ڵĿռ�����

		self.waterVolumeListerID = BigWorld.addWaterVolumeListener( self.matrix, self.enterWaterCallback )

		# ��������
		self.onWater = False
		self.jumpType = csdefine.JUMP_TYPE_LAND

		# �ӳٴ������
		self.delayTeleportNpc = None
		self.delayTeleportTime = 0
		self.delayTeleportCBID = 0
		self.delayTeleportIsFail = False
		self.isBlowUp = False

		#��������Y�����ص�
		self.cameraInHomingID = 0
		self.actionCBID = 0 #�����ƶ����ƻص����
		self.cameraFollowCBID = 0 #������ͷ����ص����

		self.homingAction = None #��ǰ���ڲ�����������
		#���ͽ������������ͻ��˷��贫��
		self.continueFlyPath = ""

		self.cfCounter = [ [0] * len( Define.CONTROL_FORBID_ROLE_MOVE_LIST ), [0] * len( Define.CONTROL_FORBID_ROLE_CAMERA_LIST ) ]
		self.changeWorldCamHandler( csdefine.NORMAL_WORLD_CAM_HANDLER )

		BigWorld.setFogTargetMatrix( self.matrix )
		
		self.visibleRules = [csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_SHOW_SELF,\
		 csdefine.VISIBLE_RULE_BY_WATCH, csdefine.VISIBLE_RULE_BY_PROWL_1]

	def addControlForbid( self, stateWord, source ):
		"""
		��ҿ������Ƽ�������һ����ά����ҿ��ơ�
		@param stateWord	:	����״̬��
		@type stateWord		:	integer
		@param source		:	������Դ
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
		��ҿ��Ƽ�������һ����ά����ҿ��ơ�
		@param stateWord	:	����״̬��
		@type stateWord		:	integer
		@param source		:	������Դ
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
		��ҿ������Ʒ����ı�
		"""
		if disabled and act == Define.CONTROL_FORBID_ROLE_MOVE:
			if self.isMoving():
				self.stopMove()
			self.emptyDirection() #������Ӱ��

	def clearControlForbid( self ):
		"""
		�����ҿ�������
		"""
		self.controlForbid = 0
		self.cfCounter = [ [0] * len( Define.CONTROL_FORBID_ROLE_MOVE_LIST ), [0] * len( Define.CONTROL_FORBID_ROLE_CAMERA_LIST ) ]

	def clearSourceControlForbid( self, stateWord, source ):
		"""
		������source��Դ��stateWord�������Ƽ���
		"""
		for i, act in enumerate( Define.CONTROL_FORBID_ROLE_LIST ):
			if stateWord & act:
				self.cfCounter[i][source] = 0
				if sum( self.cfCounter[i] ) == 0:
					self.controlForbid &= ~act
					self.onControlForbidChanged( act, False )

	def hasControlForbid( self, controlState ):
		"""
		�Ƿ��п�������
		@param controlState : ��ҿ������� see Define.py CONTROL_FORBID_*
		@type controlState : Uint16
		@return BOOL
		"""
		return self.controlForbid & controlState != 0

	def __switchPkMode( self ):
		"""
		�л�pkģʽ
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
		�������ɫʱ������
		"""
		self.filter = BigWorld.AvatarFilter()
		# �� Action.__release__() �ƹ����ģ�10:41 2008-6-24 yk
		self.__unbindShortcuts()
		ActivitySchedule.g_activitySchedule.clean()
		rds.enEffectMgr.stop()

	# -------------------------------------------------
	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.PlayerAvatarFilter()			# we're using a filter tailor-made for us

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		INFO_MSG( "PlayerRole::enterWorld: begin" )
		BigWorld.dcursor().yaw = BigWorld.player().yaw	# ����½���ɫ��������ȷ������
		rds.worldCamHandler.reset()						# ���辵ͷ
		self.resetAutoFight()							# ����Ͻ�ɫ���Զ�ս����������
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

		GUIFacade.onRoleEnterWorld( self )					# ֪ͨ Facade
		#self.statusMessage( csstatus.ACCOUNT_STATE_CLIENT_VERSION, love3.versions ) ע���յ�¼ʱ�İ汾��ʾ��Ŀǰ�Ѳ���Ҫ
		self.resetPhysics()
		self.physics.fall = False							# Fix��Ϸ�������볡���Ľ�ɫ�����Bug
		self.updateMoveMode()								# �����ƶ��ٶ�( 2008.12.30 )
		self.switchFlyWater( True )							# ������������Ч��
		self.resetPatrol()									# ������ʾ�ڵ�·��

		rds.gameMgr.onRoleEnterWorld()						# ������Ϸʱ֪ͨ��Ϸ�����������Ҫ�ŵ������ hyw--2009.05.15��
		if isPublished:
			BigWorld.callback( 1.0, checkCurrentSpaceData )

		BigWorld.setGraphicsSetting( "HEAT_SHIMMER", 0 )
		rds.gameSettingMgr.onPlayerEnterSpace()				# Ӧ�õ�ͼ����Ϸ�Զ�������

	def leaveWorld( self ):
		"""
		���뿪����ʱ������
		"""
		Role.leaveWorld( self )
		Attack.leaveWorld( self )
		GUIFacade.onRoleLeaveWorld( self )					# ֪ͨ Facade

		self.leaveFishing()									# ����ڲ��㣬���뿪�泡

		rds.targetMgr.unbindTarget()						# ���ѡ����Ŀ��
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		ECenter.fireEvent( "EVT_ON_TRIGGER_PLAYER_LEAVE_WORLD" )	#�����װ����ʾ����
		rds.gameMgr.onRoleLeaveWorld()
		self.stopMove()										# ֹͣ�Զ��ƶ�
		self.endAutoRun( False )
		rds.areaEffectMgr.onStopAreaEffect( self )			# ֹͣˮЧ��
		rds.areaEffectMgr.stopSpaceEffect()					# ֹͣ������Ч

		self.clearMailbox()							# �������

		for linkEffect in self.linkEffect:
			linkEffect.stop()
		self.linkEffect = []

		if self.onLineTimer is not None:	# ֹͣ���߽�����ʾ��ʱ by����
			BigWorld.cancelCallback( self.onLineTimer )
			self.onLineTimer = None

		# ���ģ�͹���������ؼ�����Ϣ
		rds.modelFetchMgr.resetFetchModelTask()

		#�뿪��Ϸ��ֹͣ����ҡ�LuoCD
		if  self.apexClient != None:
			self.apexClient.StopApexClient()

		# ����Ƿ������巶Χ����������
		rds.soundMgr.lockBgPlay( False )
		rds.gameSettingMgr.onPlayerLeaveSpace()				# �ָ���ͼ����Ϸ�Զ�������

	def initCacheTasks( self ):
		"""
		��ʼ������������
		"""
		# ���Լ�role�������ÿ�
		pass

	def getPhysics( self ):
		"""
		��ȡ��ɫ�� physics
		"""
		entity = self
		if self.vehicle and self.vehicle.inWorld:
			entity = self.vehicle
		if hasattr( entity, "physics" ):
			return entity.physics
		return None

	def targetFocus( self, entity ):
		"""
		���ý�ɫ��������ĳ��Ŀ��ʱ���ú������������
		"""
		if getattr( self, "playingVideo", False ) == True:
			return
		if ( hasattr( entity, "onTargetFocus" ) ):
			entity.onTargetFocus()

	def targetBlur( self, entity ):
		"""
		���ý�ɫ������뿪ĳ��Ŀ��ʱ���ú������������
		"""
		if getattr( self, "playingVideo", False ) == True:
			return
		if ( hasattr( entity, "onTargetBlur" ) ):
			entity.onTargetBlur()

	# -------------------------------------------------
	def updateMoveMode( self ) :
		"""
		�����ƶ�ģʽ
		"""
		if self.vehicle:
			func = self.vehicle.setSpeed
			speed = self.vehicle.move_speed
			if self.__isAssaulting :					# ������ڳ��״̬
				speed = self.vehicle.move_speed
			elif self.__moveMode == self.MOVE_WALK :	# �������·״̬
				speed = 2.0								# �ݶ���·�ٶ�Ϊ 2.0m/s
			elif self.__moveMode == self.MOVE_RUN :		# ������ܲ�״̬
				speed = self.vehicle.move_speed
			elif self.__moveMode == self.MOVE_FLY :		# ����״̬
				pass
		else:
			func = self.setSpeed
			speed = self.move_speed
			if self.__isAssaulting :					# ������ڳ��״̬
				speed = self.move_speed
			elif self.__moveMode == self.MOVE_WALK :	# �������·״̬
				speed = 2.0								# �ݶ���·�ٶ�Ϊ 2.0m/s
			elif self.__moveMode == self.MOVE_RUN :		# ������ܲ�״̬
				speed = self.move_speed
			elif self.__moveMode == self.MOVE_FLY :		# ����״̬
				pass
		func( speed )

	def __toggleWalkRun( self ) :
		"""
		�����л�
		"""
		if self.__moveMode == self.MOVE_WALK :
			self.__moveMode = self.MOVE_RUN
		elif self.__moveMode == self.MOVE_RUN :
			self.__moveMode = self.MOVE_WALK
		self.updateMoveMode()

	def __toggleSitdownStandup( self ) :
		"""
		�����л�
		"""
		pass

	# -------------------------------------------------
	def __bindShortcuts( self ) :
		rds.shortcutMgr.setHandler( "FIXED_GO_TO_CURSOR", self.__moveToCursor )						# �ƶ�����갴�´�
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_WALK_RUN", self.__toggleWalkRun )				# �����л�
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_SITDOWN_STAND", self.__toggleSitdownStandup )	# �����л�
		rds.shortcutMgr.setHandler( "ACTION_AUTO_RUN", self.__autoMoveForward )						# �Զ���ǰ��
		rds.shortcutMgr.setHandler( "ACTION_FORWARD", self.__handleKeyEvent )			# move forward
		rds.shortcutMgr.setHandler( "ACTION_BACKWORD", self.__handleKeyEvent )			# move backward
		rds.shortcutMgr.setHandler( "ACTION_TURN_LEFT", self.__handleKeyEvent )			# move leftward
		rds.shortcutMgr.setHandler( "ACTION_TURN_RIGHT", self.__handleKeyEvent )		# move rightward
		rds.shortcutMgr.setHandler( "ACTION_JUMP_UP", self.__handleKeyEvent )			# jump up
		rds.shortcutMgr.setHandler( "ACTION_FOLLOW_TARGET", self.__followTarget )		# �Զ�����Ŀ��

	def __unbindShortcuts( self ) :
		rds.shortcutMgr.setHandler( "FIXED_GO_TO_CURSOR", None )						# �ƶ�����갴�´�
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_WALK_RUN", None )					# �����л�
		rds.shortcutMgr.setHandler( "ACTION_TOGGLE_SITDOWN_STAND", None )				# �����л�
		rds.shortcutMgr.setHandler( "ACTION_AUTO_RUN", None )							# �Զ���ǰ��
		rds.shortcutMgr.setHandler( "ACTION_FORWARD", None )							# move forward
		rds.shortcutMgr.setHandler( "ACTION_BACKWORD", None )							# move backward
		rds.shortcutMgr.setHandler( "ACTION_TURN_LEFT", None )							# move leftward
		rds.shortcutMgr.setHandler( "ACTION_TURN_RIGHT", None )							# move rightward
		rds.shortcutMgr.setHandler( "ACTION_JUMP_UP", None )							# jump up
		rds.shortcutMgr.setHandler( "ACTION_FOLLOW_TARGET", None )						# �Զ�����Ŀ��

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
		if self.affectAfeard:												# ���ڿ���״̬�����������߶�
			INFO_MSG("Fearing!! Can't Move!")
			return False
		def isAllKeysDown( downKeys ) :										# �ж�ָ���ļ��Ƿ񶼴��ڰ���״̬
			if len( downKeys ) == 0 : return False
			for downKey in downKeys :
				if not BigWorld.isKeyDown( downKey ) :
					return False
			return True
		#��WASD���ߵ�ʱ�������ı�����״̬��ǰ����ֹ
		if self.isActionState( Action.ASTATE_CONTROL ) and rds.uiHandlerMgr.getTabInUI() and not self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			self.stopMove()
		okayToGo = False													# ��ʱ���������ĳ�����İ����Ƿ���ȫ����
		keyUsed = False														# ���¼�ʱ���Ƿ��ҵ���Ӧ��ƥ�䶯����ֻҪ��һ����������Ϊ True��
		for downKeys, upKeySets, action in self.__getBindingKeys() :		# ѭ��������������
			if key not in downKeys : continue								# ���µļ��Ƿ��ڵ�ǰ�����У��Ƿ����ڸö�����
			okayToGo = isAllKeysDown( downKeys )							# ���赱ǰ������������������ж��������Ƿ��Ѿ�ȫ������
			if okayToGo :													# �����ǰ������ȫ���������ڰ���״̬
				for upKeys in upKeySets :									# Ѱ���Ƿ��б�� action �뵱ǰ���µ����м���ȫ�Ǻ�
					if isAllKeysDown( upKeys ) :							# ������ action �����а�����ȫ������
						okayToGo = False									# ��ǰ action �� okayToGo Ϊ False
						break

			keyUsed = keyUsed or action( okayToGo )							# ���� action
		if not down :
			return False
		return keyUsed

	def __moveForward( self, isDown ):
		"""
		��ǰ�ƶ�
		"""
		#�����ƶ�Ѹ�ݵİ����ж�
		if not isDown:
			self.wasdFlag[0] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			INFO_MSG("Forbid role move!!")
			return False

		if self.state == csdefine.ENTITY_STATE_DEAD:
			INFO_MSG("Role die, can't move!!")
			return False

		if isDown and (self.isSameKey or True in self.wasdFlag) :
			#�ж��Ƿ񴥷�Ѹ���ƶ�
			t = time.time()
			if (t - self.wasdFlagTime[0] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag ):
				self.wasdFlag[0] = True
				self.triggerFastMoving()
			self.wasdFlagTime[0] = time.time()
		else:
			self.wasdFlag[0] = False
			self.stopFastMoving() #����Ƿ�ȡ���ƶ�Ѹ��
		# �������裬���ػ񰴼���Ϣ
		if self.vehicle:
			self.vehicle.moveForward( isDown )
			return True
		self.updateDirection( Action.DIRECT_FORWARD, isDown )
		#if self.jumping_move( isDown ): return self.jumping_move( isDown )
		self.flushAction()
		return True

	def __moveBackward( self, isDown ):
		"""
		����ƶ�
		"""
		#�����ƶ�Ѹ�ݵİ����ж�
		if not isDown:
			self.wasdFlag[2] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if isDown and (self.isSameKey or True in self.wasdFlag):
			#�ж��Ƿ񴥷�Ѹ���ƶ�
			t = time.time()
			if  ( t - self.wasdFlagTime[2] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag ):
				self.wasdFlag[2] = True
				self.triggerFastMoving()
			self.wasdFlagTime[2] = time.time()
		else:
			self.wasdFlag[2] = False
			self.stopFastMoving() #����Ƿ�ȡ���ƶ�Ѹ��

		# �������裬���ػ񰴼���Ϣ
		if self.vehicle:
			self.vehicle.moveBack( isDown )
			return True

		self.updateDirection( Action.DIRECT_BACKWARD, isDown )

		#if self.jumping_move( isDown ): return self.jumping_move( isDown )

		self.flushAction()
		return True

	def __moveLeft( self, isDown ):
		"""
		�����ƶ�
		"""
		#�����ƶ�Ѹ�ݵİ����ж�
		if not isDown:
			self.wasdFlag[1] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if isDown and (self.isSameKey or True in self.wasdFlag):
			#�ж��Ƿ񴥷�Ѹ���ƶ�
			t = time.time()
			if  (t - self.wasdFlagTime[1] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag ):
				self.wasdFlag[1] = True
				self.triggerFastMoving()
			self.wasdFlagTime[1] = time.time()
		else:
			self.wasdFlag[1] = False
			self.stopFastMoving() #����Ƿ�ȡ���ƶ�Ѹ��

		# �������裬���ػ񰴼���Ϣ
		if self.vehicle:
			self.vehicle.moveLeft( isDown )
			return True

		self.updateDirection( Action.DIRECT_LEFT, isDown )

		#if self.jumping_move( isDown ): return self.jumping_move( isDown )

		self.flushAction()
		return True

	def __moveRight( self, isDown ):
		"""
		�����ƶ�
		"""
		#�����ƶ�Ѹ�ݵİ����ж�
		if not isDown:
			self.wasdFlag[3] = False
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if isDown and (self.isSameKey or True in self.wasdFlag):
			#�ж��Ƿ񴥷�Ѹ���ƶ�
			t = time.time()
			if ( t - self.wasdFlagTime[3] < Const.JUMP_FAST_BUFF_TRIGGER_TIME or True in self.wasdFlag):
				self.wasdFlag[3] = True
				self.triggerFastMoving()
			self.wasdFlagTime[3] = time.time()
		else:
			self.wasdFlag[3] = False
			self.stopFastMoving() #����Ƿ�ȡ���ƶ�Ѹ��

		# �������裬���ػ񰴼���Ϣ
		if self.vehicle:
			self.vehicle.moveRight( isDown )
			return True

		self.updateDirection( Action.DIRECT_RIGHT, isDown )

		#if self.jumping_move( isDown ):return self.jumping_move(isDown)

		self.flushAction()
		return True

	def jumping_move( self, isDown ) :
		"""
		��Ծ�е��ƶ�
		"""
		vec = self.physics.velocity
		if isDown:
			#�������Ծ״̬Ҫ����Ƿ�������������ǰ��
			if self.getJumpState() in [ Const.STATE_JUMP_UP, Const.STATE_JUMP_UP2, Const.STATE_JUMP_UP3 ]:
				self.physics.velocity = ( vec[0], vec[1], self.move_speed )
				return True
			elif self.getJumpState() == Const.STATE_JUMP_DOWN :
				return True
		else:
			#�������Ծ״̬�������ٶ�
			if self.getJumpState() != Const.STATE_JUMP_DEFAULT:
				self.physics.velocity = ( 0, vec[1], 0 ) #�ɿ����Ƽ�ʱ��ȡ��ˮƽ�����ϵ��ٶ�����
				return True

	def triggerFastMoving( self ):
		"""
		�ж��Ƿ񴥷�Ѹ���ƶ�buff
		"""
		if self.state  in [ csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_FIGHT ]:
			return
		if self.getJumpState() != Const.STATE_JUMP_DEFAULT: #�������Ծ������
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
		ֹͣѸ���ƶ�buff
		"""
		if isControl and True in self.wasdFlag and not self.isHavePairKey():
			return
		buffData = self.findBuffByBuffID(  Const.JUMP_FAST_BUFF_ID )
		if buffData : #Ѹ���ƶ�buff����
			self.requestRemoveBuff( buffData[ "index" ] )
			self.wasdFlag = [ False, False, False, False ]

	def isHavePairKey( self ):
		"""
		����Ƿ��������һ���෴�İ���
		����W+S ����A+D
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
		�����¼�ʱ���Զ���ǰ�ƶ�
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
		��seek��ʽ�ƶ��������ϰ���ʱ�Ļص�����
		"""
		UnitSelect().hideMoveGuider()
		self.stopMove()

	def __toggleOtherRoles( self ) :
		"""
		��ʾ/����������ɫģ��
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
		�����µ�λ��ID
		"""
		if oldValue ==  self.planesID:
			return

		if self.followTargetID:#����и��������ȡ��
			self.team_cancelFollow( csstatus.TEAM_FOLLOW_FAIL )

		for e in BigWorld.entities.values():
			if e.__class__.__name__ not in csconst.CLIENT_ENTITY_TYPE:
				e.updateVisibility()

	def setIsShowSelf( self, isShow ):
		"""
		�Ƿ���ʾ����Լ�ģ��
		"""
		self.isShowSelf = isShow
		self.updateVisibility()

	def isShowOtherRolesAndUI( self, isShow ) :
		"""
		��ʾ/����������ɫģ��(����UI)
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
		�Ƿ������Ծ
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

		# �ж����������ļ���
		self.interruptAttack( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )
		# ȡ������
		if self.currentModelNumber == "fishing":
			self.end_body_changing( "" )

		# ���ػ���Ϣ
		if self.vehicle:
			self.vehicle.updateDirection( Action.DIRECT_JUMPUP, True ) #��¼���������Ծ�� �� �жϸ���״̬
			if isDown:
				self.vehicle.jumpBegin()
			return True

		if self.getJumpState() == Const.STATE_JUMP_DEFAULT and self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			vec = self.physics.velocity
			if isDown:
				self.physics.fall = False
				self.physics.velocity = ( vec[0], self.move_speed, vec[2] )
				if vec[2] == 0:
					if not self.vehicleType: return False    #����������û�м�����ϣ���ƥ�䶯��
					self.onSwitchVehicle( Const.MODEL_ACTION_FLOAT_UP )
			else:
				self.physics.velocity = ( vec[0], 0, vec[2] )
				if vec[2] == 0:
					self.onSwitchVehicle( Const.MODEL_ACTION_STAND )
			return True # �����Ϊ������Ϣ�Ѿ�������Ӧ�÷���True �μ���InWorld.handleKeyEvent

		self.updateDirection( Action.DIRECT_JUMPUP, True ) #��¼���������Ծ�� �� �жϸ���״̬
		if isDown:
			self.jumpBegin()
		return True

	def __flyJumpUp( self ):
		self.cell.onFlyJumpUpNotifyFC()
		self.flyJumpUp()

	def setJumpType( self ):
		"""
		������Ծ����
		"""
		jumpType = csdefine.JUMP_TYPE_LAND
		if self.onWaterArea and not self.vehicleModelNum:
			jumpIndex = random.choice( range( len( csconst.JUMP_TYPE_WATERS ) ) )
			jumpType = csconst.JUMP_TYPE_WATERS[ jumpIndex ]

		self.jumpType = jumpType

	def jumpBegin( self ) :
		if self.getJumpState() == Const.STATE_JUMP_DEFAULT:
			#���㵯���ĳ�ʼ�ٶ�
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
		#���������2��/3����
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
		self.updateDirection( Action.DIRECT_JUMPUP, False )			# ��Ծ����ʱ��ȥ�����Ϸ����ǣ�hyw -- 2008.12.23��
		self.flushAction()
		self.floatOnWaterAreaCallback( self.onWater )				# ��ˮ������½�أ��Ƿ���ˮ�����Ƿ���ˮ����ͬ���ġ�
		self.isJump2 = False
		self.isJump3 = False
		self.startHeight = 0
		self.isJumpProcess = False
		if self.onWaterJumpTimer is not None:			# �ֶ���Ծ���¼�����ʱ��
			BigWorld.cancelCallback( self.onWaterJumpTimer )
			self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )

	def __jumpDownOnFly( self ):
		self.physics.fall = False
		self.physics.jumpState = Const.STATE_JUMP_DEFAULT
#		self.isJumpProcess = True
		self.setArmCaps() #����caps��ȥ����Ծ����������walk��run��run_weapon�ȶ���

	def __onFallToGround( self ):
		"""
		�����ر�ʱ�Ĵ���
		"""
		# if ����Ѿ�����
		if self.state == csdefine.ENTITY_STATE_DEAD:
			# ֹͣ������䣨������ҵ��䵽һ����ʹ�Լ����»���б����֮�����Ϊ�ͻ���������������ң�������������ΪENTITY.topSpeed = 0�ֲ��ܶ�����˲������ҵľ�ͷ��˸��
			self.physics.fall = False
			return

		self.physics.fall = True
		vec = self.physics.velocity
		v2 = 0 if (vec[2] == 0) else self.move_speed
		v2 = v2 if vec[2] > 0 else -v2
		self.physics.velocity = ( vec[0], 0, vec[2] )

	def isJumping( self ):
		"""
		�Ƿ�����Ծ��
		"""
		if self.model is None: return False
		return self.getJumpState() != Const.STATE_JUMP_DEFAULT

	def getJumpState( self ) :
		"""
		��ȡ��Ծ״̬
		"""
		return getattr( self.getPhysics(), "jumpState", None )

	def isMoving( self ):
		"""
		�Ƿ����ƶ���
		"""
		return Action.Action.isMoving( self )

	# --------------------------------------------------
	# ������ƶ�
	# --------------------------------------------------
	def __moveToCursor( self ) :
		"""
		move to cursor
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False

		if self.vehicle and not self.actionSign( csdefine.ACTION_FORBID_MOVE ):		# �����ǰ������裬����Ϣת������账��
			return self.vehicle.moveToCursor()

		if not self.allowMove(): return False
		entity = BigWorld.target.entity							# ����Ƿ����Ŀ�����ϣ������򲻻������ﴦ����ǰ��
		if entity is not None: return False

		toPos = gbref.cursorToDropPoint()						# ������갴�´�����ά����
		if toPos is None : return False
		if self.isJumping():									# �����ǰ��������Ծ״̬
			self.onMoveToCursorJump( toPos )					# ����Ծ��Ϻ����ߵ�ָ����
			return True

		if self.isActionState( Action.ASTATE_NAVIGATE ):		# �պ����Զ�Ѱ·��������Զ�Ѱ·
			self.endAutoRun( False )
		self.setActionState( Action.ASTATE_DEST )				# ����Ϊ�ߵ�ָ��Ŀ��

		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):				# ����״̬�£�ֱ����Ŀ��
			self.stopMove()
			self.moveToDirectly( toPos, self.__onMoveToDirectlyOver )
			UnitSelect().showMoveGuider( toPos )					# ���������ں��棬��ΪmoveTo()����stopMove()
			return True

		if self.moveTo( toPos, self.__onMoveToOver ):
			UnitSelect().showMoveGuider( toPos )					# ���������ں��棬��ΪmoveTo()����stopMove()

		return True


	def onMoveToCursorJump( self, pos ):
		"""
		���������������ƶ�ʱ����
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return
		self.__jumpPos = Math.Vector3( pos )							# ��¼�½�����Ծ����Ҫ�ƶ�����λ��
		UnitSelect().showMoveGuider( pos )
		BigWorld.cancelCallback( self.__jumpCBID )
		self.__jumpCBID = BigWorld.callback( 0.1, self.__moveJumpCB )	# �����Ծ����

	def __moveJumpCB( self ):
		"""
		�����ƶ�CB
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			UnitSelect().hideMoveGuider()
			return

		if self.isJumping():												# �����������Ծ��
			BigWorld.cancelCallback( self.__jumpCBID )
			self.__jumpCBID = BigWorld.callback( 0.1, self.__moveJumpCB )	# ��������
		else:																# �����Ծ����
			if self.isActionState( Action.ASTATE_NAVIGATE ):				# �պ����Զ�Ѱ·��������Զ�Ѱ·
				self.endAutoRun( False )
			self.setActionState( Action.ASTATE_DEST )						# ����Ϊ״̬����Ϊ�ƶ���ĳ��
			if self.moveTo( self.__jumpPos, self.__onMoveToOver ):				# MOVETO�������ǣ�������������һ��
				UnitSelect().showMoveGuider( self.__jumpPos )

	def __clearSpanSpaceData( self, withForce ):
		"""
		��տ糡����Ϣ����
		@type		withForce:	bool
		@param		withForce:	�Ƿ�ǿ�����
		"""
		if not self.__spanSpaceDataLock or withForce:
			self.__spanSpaceDstLabel = ""
			self.__spanSpaceDstPos = Math.Vector3( self.INVALIDITY_POS ) #��־Ϊ��Чλ��
			self.__spanSpaceNearby = 0
			self.__spanSpaceTarget = ""
			self.__spanSpaceDataLock = False

	def __followTarget( self ) :
		"""
		���浱ǰĿ��Ŀ�ݼ�
		"""
		target = self.targetEntity
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			self.autoFollow( target.id )

	def flushAction( self ):
		"""
		������Ϊ״̬���ƶ���ͼ���򣬸�����Ϊ������ֹͣ��ĳ�������ƶ���
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			return
		if not self.allowMove() :
			return
		if rds.uiHandlerMgr.getTabInUI():
			return
		if not ( self.vehicle or self.hasFlag( csdefine.ROLE_FLAG_FLY ) ):
			self.physics.fall = True					#���ڽ����������ż�����ֽ�ɫ�ɿյ�����
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
		�ж�����Ƿ���ָ����ͼ��
		"""
		spaceName = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		if spaceName in csconst.TEAM_INVIETE_FORBID_MAP:
			return True
		return False

#-------------------------���������صļ��Start by mushuang-------------------------#
	def isOnSomething( self ):
		"""
		����ڵ������Ƿ��䵽ĳ������
		"""
		return self.__flyingVehicle.isOnSomething()

	def enableFlyingRelatedDetection( self, spBoundingBoxMin, spBoundingBoxMax ):
		"""
		defined method
		@enableFlyingRelatedDetection: �����ͷ����йصļ��
		@spBoundingBoxMin: �ռ���Ӻе�һ���ԽǶ���
		@spBoundingBoxMax: ��spBoundingBoxMin��Ե���һ���ԽǶ���
		"""
		self.__flyingVehicle.enableFlyingRelatedDetection( spBoundingBoxMin, spBoundingBoxMax )

	def disableFlyingRelatedDetection( self ):
		"""
		defined method
		@disableFlyingRelatedDetection: �رպͷ����йصļ��
		"""
		self.__flyingVehicle.disableFlyingRelatedDetection()

	def onEnterFlyState( self ):
		"""
		�������״̬
		"""
		rds.worldCamHandler.cameraShell.camera_.minHeightOffsetLimit -= 3.0
		self.physics.fallToGroundDetectLen = 0
		self.physics.setJumpDownFn( self.__jumpDownOnFly )
		self.__flyingVehicle.updateSpaceBoundingBox()

	def onLeaveFlyState( self ):
		"""
		�뿪����״̬
		"""
		self.physics.fallToGroundDetectLen = -1.0
		self.physics.setJumpDownFn( self.__jumpDown )
		self.physics.fall = True
		self.physics.stop() # ��ֹ��Ұ��ſո�رշ�����裬Ȼ������ڿ��в��ű��ܶ�������ˤ��������߶�����ˤ���Ļ����ڿ��е����� by mushuang
		UnitSelect().hideMoveGuider()
		self.__flyingVehicle.updateSpaceBoundingBox()
#-------------------------���������صļ��End by mushuang-------------------------#

	def allowMove( self ):
		"""
		�жϽ�ɫ�Ƿ�����ƶ�
		"""
		if self.effect_state & csdefine.EFFECT_STATE_BE_HOMING :
			return True
		if self.actionSign( csdefine.ACTION_FORBID_MOVE )  :				# verify wether allow to move( defined in Charactor.py )
			INFO_MSG( "I can't move��" )
			return False
		if self.getPhysics() is None :												# Only controlled entities have a 'physics' attribute
			return False
		if not self.physics.fall and not self.hasFlag( csdefine.ROLE_FLAG_FLY ):	#��Ҵ��ڲ���׹��״̬ʱ�ҷǷ���״̬���������ƶ�
			return False
		return True

	def doRandomRun( self, centerPos, radius ):
		"""
		define method
		�ߵ�centerPosΪԭ�㣬radiusΪ�뾶�����������
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
				break	# ֱ������ѭ��

	def showTargetAttribute( self, targetID ):
		"""
		��ʾ�Է���ҵ�����(�۲칦��)
		@param   targetID: �Է���ҵ�ID
		@type    targetID: OBJECT_ID
		"""
		target = BigWorld.entities.get( targetID )
		if target is None: #û��������
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
			return

		otherInfo = {}
		otherInfo["TongName"] =	target.tongName				#�������
		if target.tongName:
			tongGrade = target.tong_grade						#��ȡ���Ȩ��
			if target.tong_dutyNames.has_key( tongGrade ):
				tongDuty = target.tong_dutyNames[tongGrade]
			else:
				tongDuty = Const.TONG_GRADE_MAPPING[tongGrade]
			otherInfo["TongDuty"]   =	tongDuty								#���ְλ
		otherInfo["Name"] = target.getName()									#����
		otherInfo["Gender"] = csconst.g_chs_gender[target.getGender()]			#�Ա�
		otherInfo["Pclass"] = csconst.g_chs_class[target.getClass()]			#ְҵ
		otherInfo["Level"] = target.getLevel()									#�ȼ�
		espial.showTargetOtherInfo(otherInfo)									#�ý���ȥ��ʾ��ҵ�������Ϣ ���� ְλ �ȼ� �Ա�......

	def showTargetEquip(self ,items , ifEnd):
		"""
		��ʾ�Է���ҵ�װ��(�۲칦��)
		@param   items: �Է���ҵĲ�����Ϣ
		@type    items: LIST
		@param   targetID: �Է���ҵ�ID
		@type    targetID: OBJECT_ID
		"""
		espial.showTargetEquip( items, ifEnd )			#�ý���ȥ��ʾ��ҵ�װ��

	def pursueEntity( self, entity, nearby, callback = lambda player, entity, success : False ) :
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���player, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
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
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���player, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
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
		����Ѱ·�ƶ���ָ��λ�ã����λ����ָ��λ�õľ���
		@type			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : �ƶ������ص�
		"""
		path_distance = 0
		runPathList = []
		#Ѱ·���ɵ��� ��ô������Ϊ1000
		#����·����ʱ�򣬽�����position�Ĵ���������������
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
		�ƶ���ָ��λ�ã�����ӿڻ������ҿͻ��˿�����������ж�
		@type			RETURN		  : bool
		@param			RETURN		  : Ŀ�ĵ��Ƿ���Եִ�
		@type			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : �ƶ������ص�
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return False
		if not self.allowMove(): return False
		return self.moveToPos( position, callback )

	def moveToPos( self, position, callback = None ) :
		"""
		�ƶ���ָ��λ��
		@type			RETURN		  : bool
		@param			RETURN		  : Ŀ�ĵ��Ƿ���Եִ�
		@type			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : �ƶ������ص�
		"""
		if self.vehicle:
			return self.vehicle.moveTo( position, callback )
		else:
			return Action.Action.moveTo( self, position, callback )


	def moveToDirectly( self, position, callback = None ) :
		"""
		��ֱ���ƶ���ָ��λ��
		@type			RETURN		  : bool
		@param			RETURN		  : Ŀ�ĵ��Ƿ���Եִ�
		@type			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			verticalRange : float
		@param			verticalRange : how heigh that the role can pass
		@type			callback	  : functor / method
		@param			callback	  : �ƶ������ص�
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
		�Զ�Ѱ·��ĳ��ͼ��ĳ����
		@type			position   : Math.Vector3
		@param			position   : Ŀ��λ��
		@type			nearby     : float
		@param			nearby     : �ƶ���Ŀ��λ�ø����ľ���
		@type			dstSpace   : string
		@param			dstSpace   : Ŀ��Space Name
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return

		if self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.statusMessage( csstatus.AUTO_RUN_NOT_IN_FLY_STATE ) #add by wuxo 2011-11-8
			return

		curSpaceLabel = self.getSpaceLabel()
		if dstSpace == curSpaceLabel or curSpaceLabel is None:
			dstSpace = "" #Ŀ����ڵ�ǰ�����������ÿ糡������

		if not dstSpace:
			if curSpaceLabel in spaceHeightDatas.keys() and \
				Math.Vector3( position ).y >= spaceHeightDatas.get( curSpaceLabel, 0.0 ) and \
				self.position.y < spaceHeightDatas.get( curSpaceLabel, 0.0 ):	# ��ͬһ�ռ䲢��Ŀ����ڿ��в�������ڵ���
					self.statusMessage( csstatus.AUTO_RUN_CAN_NOT_GET_PATH_AIR )
					self.stopMove()
					return
			if curSpaceLabel in spaceHeightDatas.keys() and \
				Math.Vector3( position ).y < spaceHeightDatas.get( curSpaceLabel, 0.0 ) and \
				self.position.y >= spaceHeightDatas.get( curSpaceLabel, 0.0 ):	# ��ͬһ�ռ䲢��Ŀ����ڵ��沢������ڿ���
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
		�ָ��Զ�Ѱ·
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
		self.physics.isMovingNotifier = self.onMoveChanged	# �����ƶ�֪ͨ����
		self.physics.scrambleHeight = 0.5

		self.physics.setJumpEndFn( self.__jumpEnd )
		self.physics.setJumpUpFn( self.__jumpUp )
		self.physics.setJumpDownFn( self.__jumpDown )
		self.physics.setJumpSecondUpFn( self.__jumpUp2 )
		self.physics.setJumpThreeUpFn( self.__jumpUp3 )
		self.physics.setjumpSecondPrepareFn( self.__jumpPrepare )
		self.physics.setjumpThreePrepareFn( self.__jumpPrepare )

		self.physics.setFallToGroundCallBackFn( self.__onFallToGround )
		self.__flyingVehicle.refreshFlyingSetting()			# ˢ�µ�ǰ��ͼ�ķ�������
		self.clearControlForbid() #������Ҫ��ʼ����ҿ�������

	def requestInitialize( self, initType, callback ) :
		"""
		�����ʼ����ɫ����( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : ��ʼ������
		@type				callback : functor
		@param				callback : ��ʼ�����ʱ�Ļص�
		"""
		if not csdefine.ROLE_INITIALIZE in self.serverRequests:
			self.serverRequests[csdefine.ROLE_INITIALIZE] = []
		self.serverRequests[csdefine.ROLE_INITIALIZE].append( initType )
		DEBUG_MSG( "start init type %i"%initType )
		self.__initializeCallback = callback
		if initType in csconst.ROLE_INIT_BASES :			# ���� base �ĳ�ʼ��
			self.base.requestInitialize( initType )
		elif initType in csconst.ROLE_INIT_CELLS :			# ���� cell �ĳ�ʼ��
			self.cell.requestInitialize( initType )
		else :
			raise "unrecognize initialize type: %d" % initType

	def onInitialized( self, initType ) :
		"""
		<Exposed/>
		��ĳ�����Գ�ʼ����ϱ�����( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : ��ʼ�����ͣ��� csdefine �ж���
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
		��ʼ������
		"""
		TongInterface.onEndInitialized( self )
		ECenter.fireEvent( "EVT_ON_ROLE_END_INIT" )				# ����ɫ��ʼ������Ժ���һ��������ϵ���Ϣ

	def playSpaceCameraEvent( self ) :
		"""
		����ĳЩ���鸱��ʱֱ���޷첥�ž�ͷ,���ž�ͷʱ������ʾ��ͼ������
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
		�ж��Ƿ��ڿ糡��Ѱ·
		"""
		return self.__spanSpaceDstLabel != ""

	def stopMove( self, isControl = False ) :
		"""
		ֹͣ�ƶ�
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) and not rds.roleFlyMgr.isFlyState :
			return
		
		if self.state == csdefine.ENTITY_STATE_PICK_ANIMA: #ʰȡ������״̬�£�������ֹͣ�ƶ�
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
		����һ�γ����������ʱ������
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			self.physics.fall = True

		if self.state == csdefine.ENTITY_STATE_DEAD:
			BigWorld.callback( 0.5, self.pointReviveClew )

		self.resetCamera() # �������þ�ͷ
		self.base.pcg_requestPet()
		rds.gameMgr.onFirstSpaceReady()
		rds.areaEffectMgr.startSpaceEffect( self )	# �ռ�ı䴥��������Ч

		if self.isReceiveEnterInviteJoin:	# ������յ��μ�֪ʶ�ʴ�����
			BigWorld.callback( 1.0, Functor( ECenter.fireEvent, "EVT_ON_QUIZ_ON_ENTER_INVITE_JOIN" ) )

		if self.campFengHuo_signUpFlag:		#�����ҳɹ���������Ӫ�������
			self.onStatusMessage( csstatus.CAMP_FENG_HUO_ONLINE_TIPS, "" )
		if self.benefitTime > Const.BENIFIT_PERIOD:	# ������ｱ��ʱ�������������ʾ ������ʾ��ʼ��ʱ by����
			LevelUpAwardReminder.instance().onRoleBenefit()

		else:
			onLineTimeLeft = Const.BENIFIT_PERIOD - self.benefitTime
			self.onLineTimer = BigWorld.callback( onLineTimeLeft, self.onLineCount )
		self.cell.onTeleportReady( self.spaceID )
		if not self.spaceSkillInitCompleted and len( self.spaceSkillList ):
			ECenter.fireEvent( "EVT_ON_ENTER_SPECIAL_COPYSPACE", self.spaceSkillList, self.spaceSkillSpaceType )

		self.__flyingVehicle.turnonDeathDepthDetect()				# ������������
		curWholeArea = self.getCurrWholeArea()
		if curWholeArea is None:return
		curWholeArea.setTimeOfDay()

	def onTeleportReady( self ) :
		"""
		������������Ϻ󣬸ú���������
		"""
		if not ( self.hasFlag( csdefine.ROLE_FLAG_FLY ) or self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) ) :
			self.physics.fall = True

		if self.state != csdefine.ENTITY_STATE_DEAD: #�Ӹ����������Զ������ʱ��Ҫȥ��������������⴦��
			Role.disableSkeletonCollider( self )
			Role.disableUnitSelectModel( self )

		rds.areaEffectMgr.startSpaceEffect( self )	# �ռ�ı䴥��������Ч

		# ֪ͨ����ˢ��
		actPet = self.pcg_getActPet()
		if actPet is not None :
			actPet.onTeleportReady()

		# ����з���������һ����ת
		if self.talismanModel:
			self.talismanModel.position = self.position + ( 1.0, 1.5, 0.0 )

		# �ر��Զ�Ѱ·����
		ECenter.fireEvent( "EVT_ON_HIDE_NAVIGATE_WINDOW" )
		self.cell.onTeleportReady( self.spaceID )
		if  self.__spanSpaceDataLock and self.isSpanSpaceNavigate():
			self.__expectTarget = self.__spanSpaceTarget
			self.autoRun( self.__spanSpaceDstPos, self.__spanSpaceNearby, self.__spanSpaceDstLabel )
			self.__spanSpaceDataLock = False
		elif self.__expectTarget != "":
			self.talkWithTarget( self.__expectTarget )		# ʹ����·�䴫��ʱ��Ŀ��NPC�Ի���
			self.__expectTarget = ""
		if not self.spaceSkillInitCompleted and len( self.spaceSkillList ):
			ECenter.fireEvent( "EVT_ON_ENTER_SPECIAL_COPYSPACE", self.spaceSkillList, self.spaceSkillSpaceType )

		self.__flyingVehicle.updateDeathDepth()				# ˢ�µ�ǰ��ͼ���������

	def checkTelepoertFly( self ):
		"""
		����Ƿ���Ҫ����������贫��
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
		ֱ�ӽ�����Ϣ������Ƶ���ͷ�������Ϣ
		@type				chids 	 : ARRAY <of> INT8 </of>
		@param				chids 	 : Ƶ���б�
		@type				spkName	 : STRING
		@param				spkName	 : ����������
		@type				spkName	 : STRING
		@param				spkName	 : ��Ϣ����
		@return						 : None
		"""
		RoleChat._onDirectMessage( self, chids, spkName, msg )

	# ----------------------------------------------------------------
	def isPlayer( self ) :
		"""
		��ǰ״̬Ϊ���
		@rtype				: bool
		@return				: ����ָ��ɫ�Ѿ���Ϊ��ұ���
		"""
		return True

	def isFirstEnterWorld( self ) :
		"""
		ָ����ɫ�Ƿ��ǵ�һ�ν�������
		hyw--2009.07.31
		"""
		return self.level == 1 and self.lifetime < 12.0										# ��ɫ����ʱ��С��ĳ��ֵ�͵ȼ�Ϊ1��ʱ����Ϊ�ǵ�һ�ν�����Ϸ

	def checkAlive( self ) :
		"""
		�������Ƿ��ڻ���״̬������Ѿ���ȥ�������ϵͳ��Ϣ
		@rtype				: bool
		@return				: ��һ����򷵻���
		"""
		if not self.isAlive() :
			self.statusMessage( csstatus.ACCOUNT_STATE_DEAD )			# defined in RoleChat.py
			return False
		return True

	# ----------------------------------------------------------------
	def handleKeyEvent(self, isDown, key, mods ):
		"""
		�������¼�
		"""

		if not self.vehicle == None:
			self.vehicle.handleKeyEvent( isDown, key, mods )
			# In this case, vehicle handles all input, otherwise we would
			# check return code and process if false (event not handled).
			return

	def onCameraDirChanged( self, direction ):
		"""
		�������ı�֪ͨ��
		�˵�������CamerasMgr::CameraHandler::handleMouseEvent()��
		��ֻ��BigWorld.player()��onCameraDirChanged()�����ᱻ���á�
		��ƴ˷�����Ŀ����������ӽǣ�������ķ��򣩸ı�ʱ������PlayerEntity��һЩ��Ҫ�����顣
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return

		# ��ɫ����ı�
		if not self.canChangeDirection(): return
		if not self.isMoving():
			BigWorld.dcursor().yaw = direction.yaw
			return

		# ��������ı�
		self.flyMove( direction )

		# ���ػ���Ϣ
		if self.vehicle:
			self.vehicle.onCameraDirChanged( direction )
			return

		Action.Action.onCameraDirChanged( self, direction )

	# ----------------------------------------------------------------
	def initSkillBox( self, skillIDs ):
		"""
		call in enterWorld method.
		��ʼ�������б�

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
		�Ƿ���ڿռ�ר������
		"""
		return skillID in self.spaceSkillList

	# -------------------------------------------------
	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		�������жϣ��ɷ��������أ�
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
		@summary		:	����Ǯ��Ǯ���޵�����
		@type	number	:	int32
		@param	number	:	Ǯ������
		@rtype			:	int32
		@return			:	Ǯ�Ĳ�ֵ��Ϊ��ʱ��ʾǮ�������ޣ�Ϊ��ʱ��ʾǮС������
		"""
		return self.money + number - csconst.ROLE_MONEY_UPPER_LIMIT

	def ifMoneyMax( self ):
		"""
		�ж���ҿ�Я���Ľ�Ǯ�Ƿ�����
		"""
		return self.money >= csconst.ROLE_MONEY_UPPER_LIMIT

	# ----------------------------------------------------------------
	def testAddGold( self, number ):
		"""
		@summary		:	����Ԫ����Ԫ�����޵�����
		@type	number	:	int32
		@param	number	:	Ԫ��������
		@rtype			:	int32
		@return			:	Ԫ���Ĳ�ֵ��Ϊ��ʱ��ʾǮ�������ޣ�Ϊ��ʱ��ʾԪ��С������
		"""
		return self.gold + number - csconst.ROLE_GOLD_UPPER_LIMIT

	def testAddSilver( self, number ):
		"""
		@summary		:	����Ԫ����Ԫ�����޵�����
		@type	number	:	int32
		@param	number	:	Ԫ��������
		@rtype			:	int32
		@return			:	Ԫ���Ĳ�ֵ��Ϊ��ʱ��ʾǮ�������ޣ�Ϊ��ʱ��ʾԪ��С������
		"""
		return self.silver + number - csconst.ROLE_SILVER_UPPER_LIMIT

	# ----------------------------------------------------------------
	def onAddSkill( self, skillID ) :
		"""
		���һ������
		@type		skillID	: INT
		@param		skillID : ��ӵļ��ܵ�ID��
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
			# ѧϰ���ܹ�Ч����ȥ����ܣ�
			if not lvcMgr.isLivingSkill( skillID ):
				self.playUpdateSkillEffect()

	def onRemoveSkill( self, skillID ) :
		"""
		�Ƴ�һ������
		@type		skillID	: INT
		@param		skillID : Ҫ�Ƴ��ļ���ID��
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
		������ͨ������
		"""
		skID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		item = skills.getSkill( skID )
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_UPDATE_NORMAL_SKILL", skID, item )

	def onUpdateSkill( self, oldSkillID, newSkillID ) :
		"""
		����һ������
		@type		oldSkillID : INT
		@param		oldSkillID : �ɵļ��� ID
		@type		newSkillID : INT
		@param		newSkillID : �µļ��� ID
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
		# �������ܹ�Ч
		self.playUpdateSkillEffect()

	def playUpdateSkillEffect( self ):
		"""
		����ѧϰ/�������ܹ�Ч
		"""
		type = self.getParticleType()
		effect = rds.skillEffect.createEffectByID( Const.UPDATE_SKILL_EFFECT, self.getModel(), self.getModel(), type, type )
		if effect:
			effect.start()

	def onUpdateSkill_2( self, oldSkillID, newSkillID ):
		"""
		����һ������ ������ʾ��Ϣ�汾
		@type		oldSkillID : INT
		@param		oldSkillID : �ɵļ��� ID
		@type		newSkillID : INT
		@param		newSkillID : �µļ��� ID
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
		��ȡ��ҵļ����б�
		"""
		return self.skillList_[:]

	# -------------------------------------------------
	def intonate( self, skillID, intonateTime,targetObject ):
		"""
		Define method.��������
		@type 		skillID : INT
		"""
		Role.intonate( self, skillID, intonateTime, targetObject )
		Attack.intonate( self, skillID, intonateTime, targetObject )

		# �ƶ�ʱ�жϵ�ǰ����ʩչ:
		if self.isMoving() or self.isJumping():
			self.interruptAttack( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 )

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		��ʽʩ�ŷ�����������ʩ��������
		@type 		skillID	 : INT
		@type 		targetID : [OBJECT_IDs]
		@type 		position : Math.Vector3
		"""
		Role.castSpell( self, skillID, targetObject )
		Attack.castSpell( self, skillID, targetObject )
		spell = skills.getSkill( skillID )

	def requestRemoveBuff( self, index ) :
		"""
		�Ƴ�����buff
		"""
		self.cell.requestRemoveBuff( index )

	def receiveSpell( self, casterID, skillID, damageType, damage ):
		"""
		Define method.
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  damageType: INT32
		@type	  damage: INT32
		"""
		spell = skills.getSkill( skillID )
		if spell.isMalignant():		#����Ƕ��Ե�
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
		��ʼ��������
		"""
		Role.onStartHomingSpell( self, persistent )
		Attack.onStartHomingSpell( self )

	def onFiniHomingSpell( self ):
		"""
		������������
		"""
		Role.onFiniHomingSpell( self )
		Attack.onFiniHomingSpell( self )
		ECenter.fireEvent( "EVT_ON_REFRESH_QBITEM" )  # CSOL-1380�������ܽ���ˢ�¿����

	def canChangeDirection( self ):
		"""
		����Ƿ��ܸı䳯��
		"""
		if self.isDead(): return False
		if self.isInHomingSpell: return False
		if self.state != csdefine.ENTITY_STATE_FREE and self.state != csdefine.ENTITY_STATE_FIGHT	:
			return False  #ֻ�����ɺ�ս��״̬�ܹ��Ҽ��ı��ɫ�ĳ���
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		#���˻�˯��ѣ�Ρ������Ч��ʱ�����Ҽ��ı���ҽ�ɫ�ĳ���
		if self.effect_state & EffectState_list != 0: return False
		return True

	def startPickUp( self, dropBoxEntity ):
		"""
		��ҿ�ʼʰȡ��16:03 2009-3-9,wsf
		"""
		self.rotate( dropBoxEntity )
		dropBoxEntity.cell.queryDropItems()

	def stopPickUp( self ):
		"""
		ֹͣʰȡ��16:03 2009-3-9��wsf
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_PICKUP_DISTURBED" )

	def stopPickUpQuestBox( self ):
		"""
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_QUEST_PICKUP_DISTURBED" )


	def rotate( self, entity ):
		"""
		ת������16:01 2009-3-9,wsf
		"""
		if self.id == entity.id:
			return
		new_yaw = ( entity.position - self.position ).yaw
		if abs( self.yaw - new_yaw ) > 0.0:
			self.turnaround( entity.matrix, None )


	def interruptAttackByServer( self, reason ):
		"""
		define method
		server ֪ͨ��Ϲ�����Ϊ
		"""
		self.interruptAttack( reason )

	# ----------------------------------------------------------------
	def set_actWord( self, old = 0):
		"""
		virtual method = 0;
		�ӷ������յ��������Ƹı�֪ͨ
		"""
		Role.set_actWord( self, old )
		if ( self.actWord ^ old ) & csdefine.ACTION_FORBID_MOVE :
			if not self.isSpanSpaceNavigate():
				self.stopMove()					# �ı���ACTION_FORBID_MOVE��״̬����Ҫ�ı��ƶ�(�п�����Ҫ�����ƶ�)
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
		����������ʵλ�ƶ�������֮ǰ����Physics�������
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
		����������ʵλ�ƶ��������������Physics�������
		"""
		#�������ܶ���������
		phy = self.getPhysics()
		if phy:
			if hasattr( phy, "attackTargetMatrix" ):
				phy.attackTargetMatrix = None
				phy.attackTargetDis = 0

	def onPlayActionStart( self, actionNames ):
		"""
		��ʼ���Ŷ���
		"""
		Role.onPlayActionStart( self, actionNames )
		if len( actionNames ) == 0: return
		atime = self.getModel().action( actionNames[0] ).duration
		# ��������
		if rds.spellEffect.checkActionLimit( actionNames[0] ):
			self.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_PLAY_ACTION )
			if self.actionCBID > 0:
				self.onActionTimeOver()
			self.actionCBID = BigWorld.callback( atime, self.onActionTimeOver )
		# ��ͷ�����ƶ�
		if rds.spellEffect.checkCameraFollowAction( actionNames[0] ):
			def cameraFollowActionStartDelay() :
				self.cameraFollowActionStart()
				if self.cameraFollowCBID > 0:
					self.cameraFollowActionOver()
				self.cameraFollowCBID = BigWorld.callback( atime, self.cameraFollowActionOver )

			# �ӳٵ�������������ԭ�򣺵������״̬��ʹ����Ҫ��ͷ����ļ���ʱ������ֱ�ӵ��û���־�ͷ���������ƫ�Ƶ����⡣
			# ���ԭ���Ǵ˿̻�ȡģ��"HP_head"�ڵ��λ��Ϊ 0 ��Ե�ʣ�δ֪����ԭ������ֻ����ʱ������bug��
			BigWorld.callback( min( 0.1, atime ), cameraFollowActionStartDelay )


	def onPlayActionOver( self, actionNames ):
		"""
		�������Ž���
		"""
		Role.onPlayActionOver( self, actionNames )
		if len( actionNames ) == 0: return
		if actionNames[0] == self.homingAction:
			self.resetPhysicsHomingEnd()
			self.homingAction = None
		self.flushActionByKeyEvent()
		# ��������
		if rds.spellEffect.checkActionLimit( actionNames[0] ):
			if self.actionCBID > 0:
				self.onActionTimeOver()
		# ��ͷ�����ƶ�
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
		ģ�͸ı�֪ͨ
		"""
		Role.onModelChange( self, oldModel, newModel )

		# ���ڽ�����Ŷ���������ģ�͸ı������һЩ����
		self.onModelChangeOver()

		if self.isJumpProcess and not self.vehicleModelNum:	# ������Ծ��
			self.playActions( [Const.MODEL_ACTION_JUMP_AIR] )
		if self.vehicleModel:	# �����ﶯ���ص�ʧ��
			self.clearSourceControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE )
			self.inFlyDownPose = False
			if self.vehicleModel not in list( self.models ): return
			self.delModel( self.vehicleModel )
			self.vehicleModel = None
		# ����ָ��
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
		��ɫģ�͸��»ص�
		"""
		self.actionCount = 0	# �ÿղ��Ŷ������ô���
		self.onModelChangeOver()

	def onModelChangeOver( self ):
		"""
		���Ŷ���������ģ�͸ı�ص�
		"""
		if not self.inWorld: return
		actionNames = self.getActionNames()
		if len( actionNames ) == 0: return
		self.actionRule.onActionOver( actionNames )  # �ÿյ�ǰ���Ŷ����б�����ᵼ�º���ĳЩ�������Ų�����
		# ��������
		if rds.spellEffect.checkActionLimit( actionNames[0] ):
			if self.actionCBID > 0:
				self.onActionTimeOver()
		# ��ͷ�����ƶ�
		if rds.spellEffect.checkCameraFollowAction( actionNames[0] ):
			if self.cameraFollowCBID > 0:
				self.cameraFollowActionOver()
		self.flushActionByKeyEvent()

	# -------------------------------------------------
	def getEnergy( self ):
		"""
		��ȡ��Ծ����ֵ
		"""
		return self.energy

	def getEnergyMax( slef ):
		"""
		��ȡ�����Ծ����ֵ
		"""
		return csdefine.JUMP_ENERGY_MAX

	def getEnergyReverValue( self ):
		"""
		��ȡ��Ծ����ֵ���Զ��ָ�ֵ
		"""
		return csdefine.ROLE_ENERGY_REVER_VALUE

	def getEXP( self ) :
		"""
		��ȡ����ֵ
		"""
		return self.EXP

	def getEXPMax( self ) :
		"""
		��ȡ��ǰ�ȼ��������ֵ
		"""
		return RoleLevelEXP.getEXPMax( self.level )

	def set_potential( self, oldValue ) :
		"""
		Ǳ��
		"""
		dispersion = self.potential - oldValue
		if dispersion > 0:
			self.statistic["statPot"] += dispersion
		GUIFacade.onPotentialChanged( oldValue, self.potential )

	def set_HP( self, oldValue ):
		"""
		�� HP �ı�ʱ������
		"""
		Role.set_HP( self, oldValue )
		GUIFacade.onRoleHPChanged( oldValue, self.id, self.HP, self.HP_Max )
		#Ѫ����ʱ����
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
		�� HP ���ֵ�ı�ʱ������
		"""
		Role.set_HP_Max( self, oldValue )
		GUIFacade.onRoleHPChanged( oldValue, self.id, self.HP, self.HP_Max )
		attrChangeMgr.deliverAttrMsg( "HP_Max", [ oldValue, self.HP_Max ] )

	def set_MP( self, oldValue ):
		"""
		�� MP �ı�ʱ������
		"""
		Role.set_MP( self, oldValue )
		GUIFacade.onRoleMPChanged( oldValue, self.id, self.MP, self.MP_Max )
		#ħ��ֵ��ʱ����
		if rds.statusMgr.isCurrStatus( Define.GST_IN_WORLD ):
			if self.HP/( self.HP_Max * 1.0 ) <= Const.DANGER_HP: return
			if self.MP/( self.MP_Max * 1.0 ) <= Const.DANGER_MP:
				ECenter.fireEvent( "EVT_ON_FLICKER_SCREEN", ( 0, 0, 255, 255 ) )
				return
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )

	def set_MP_Max( self, oldValue ):
		"""
		�� MP ���ֵ�ı�ʱ������
		"""
		Role.set_MP_Max( self, oldValue )
		GUIFacade.onRoleMPChanged( oldValue, self.id, self.MP, self.MP_Max )
		attrChangeMgr.deliverAttrMsg( "MP_Max", [ oldValue, self.MP_Max ]  )

	def set_level( self, oldValue ):
		"""
		���ȼ��ı�ʱ������
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

	def set_teachCredit( self, oldValue ):	# 10:44 2008-8-21��wsf
		"""
		����ѫֵ�ı�ʱ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_CREDIT_CHANGED", self.teachCredit )

	def set_honor( self, oldValue ):
		"""
		��ɫ����ֵ�ı�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_HONOR_CHANGED", self.honor )

	def set_vim( self, oldValue ):
		"""
		��ɫ����ֵ�ı�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_VIM_CHANGED", self.vim )

	def set_energy( self, oldValue ):
		"""
		��ɫ��Ծֵ�ı�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_EN_CHANGED", self.energy, self.getEnergyMax() )

	def set_combatCount( self, oldValue ):
		"""
		��ɫ�񶷵�ֵ�ı�
		"""
		ECenter.fireEvent( "EVT_ON_COMBATCOUNT_CHANGED" )

	# -------------------------------------------------
	# ģ�͸ı亯���� ���������Դ�������ʾ��ɫģ�� ��
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
		����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_STRENGTH_CHANGE", self.strength )

	def set_dexterity( self, oldValue ):
		"""
		����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DEXTER_CHANGE", self.dexterity )

	def set_corporeity( self, oldValue ):
		"""
		����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_CORPORE_CHANGE", self.corporeity )

	def set_intellect( self, oldValue ):
		"""
		����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_INTELLECT_CHANGE", self.intellect )

	def set_damage_min( self, oldValue ):
		"""
		��С������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MINDAMAGE_CHANGED", self.damage_min )
		oldDmg = ( oldValue + self.damage_max ) / 2
		newDmg = ( self.damage_min + self.damage_max ) / 2
		attrChangeMgr.deliverAttrMsg( "PHYSICS_DMG", [ oldDmg, newDmg ] )

	def set_damage_max( self, oldValue ):
		"""
		���������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAXDAMAGE_CHANGED", self.damage_max )
		oldDmg = ( oldValue + self.damage_min ) / 2
		newDmg = ( self.damage_min + self.damage_max ) / 2
		attrChangeMgr.deliverAttrMsg( "PHYSICS_DMG", [ oldDmg, newDmg ] )

	def set_magic_damage( self, oldValue ):
		"""
		��������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAGDAMAGE_CHANGED", self.magic_damage )
		attrChangeMgr.deliverAttrMsg( "MAGIC_DMG", [ oldValue, self.magic_damage ] )

	def set_armor( self, oldValue ):
		"""
		�������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ARMOR_CHANGED", self.armor )
		attrChangeMgr.deliverAttrMsg( "PHYSICS_ARMOR", [ oldValue, self.armor ] )

	def set_magic_armor( self, oldValue ):
		"""
		��������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAGARMOR_CHANGED", self.magic_armor )
		attrChangeMgr.deliverAttrMsg( "MAGIC_ARMOR", [ oldValue, self.magic_armor ] )

	def set_double_hit_probability( self, oldValue ):
		"""
		��������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DOUBLE_DAM_CHANGED", self.double_hit_probability )

	def set_magic_double_hit_probability( self, oldValue ):
		"""
		����������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAG_DOUBLE_CHANGED", self.magic_double_hit_probability )

	def set_hitProbability( self, oldValue ):
		"""
		����������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_HITTED_CHANGED", self.hitProbability )

	def set_magic_hitProbability( self, oldValue ):
		"""
		����������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_MAG_HITTED_CHANGED", self.magic_hitProbability )

	def set_dodge_probability( self, oldValue ):
		"""
		����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DODGE_CHANGED", self.dodge_probability )

	def set_resist_hit_probability( self, oldValue ):
		"""
		�м�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RESIST_CHANGED", self.resist_hit_probability )

	def set_resist_giddy_probability( self, oldValue ):
		"""
		�ֿ�ѣ����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RES_GIDDY_CHANGED", self.resist_giddy_probability )

	def set_resist_sleep_probability( self, oldValue ):
		"""
		�ֿ���˯��
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RES_SLEEP_CHANGED", self.resist_sleep_probability )

	def set_resist_fix_probability( self, oldValue ):
		"""
		�ֿ�������
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RES_FIX_CHANGED", self.resist_fix_probability )

	def set_resist_chenmo_probability( self, oldValue ):
		"""
		�ֿ���Ĭ��
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
			self.antoRunConjureVehicle()	# �Զ���˹���
			rds.soundMgr.stopFightMusic()
			self.setGuideModelVisible( True ) # ����ָ��
		elif oldState != csdefine.ENTITY_STATE_FIGHT and self.state == csdefine.ENTITY_STATE_FIGHT:	#�������ս��״̬
			self.statusMessage( csstatus.ROLE_BEGIN_FIGHT )
			self.firstHit = True
			ECenter.fireEvent( "EVT_ON_SHOW_FIGHTFIRE", True)
			self.stopPickUp()
			rds.soundMgr.playFightMusic()	# ս����������
			self.setGuideModelVisible( False ) # ����ָ��
		elif oldState == csdefine.ENTITY_STATE_QUIZ_GAME:
			self.quiz_reset()
		elif oldState == csdefine.ENTITY_STATE_PICK_ANIMA: #ʰȡ����
			self.pickAnima_stop()
			self.__bindShortcuts()
			self.__moveForward( False )

		if self.state == csdefine.ENTITY_STATE_DEAD:		# �����ɫ��������ر�ʰȡ/�ӳٴ��ͽ���
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

		if oldState == csdefine.ENTITY_STATE_DEAD and self.state == csdefine.ENTITY_STATE_FREE :	# �����ɫ�������
			if self.currentShowMessage :
				self.currentShowMessage.dispose()
			ECenter.fireEvent( "EVT_ON_HIDE_REVIVE_BOX" )
		if self.state != csdefine.ENTITY_STATE_FIGHT:
			ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "cityWarer", False )

		rds.areaEffectMgr.startSpaceEffect( self )		# ��ɫ״̬�ı䴥��������Ч
		ECenter.fireEvent( "EVT_ON_ROLE_STATE_CHANGED", self.state )


	def set_effect_state( self, oldEState = 0 ):
		"""
		���Ч��״̬
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
		elif self.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:	#��ս״̬
			self.refurbishAroundRoleHPColor()

	def set_pkState( self, oldpkstate = csdefine.PK_STATE_PEACE ):
		"""
		pk״̬�ı�
		"""
		Role.set_pkState( self, oldpkstate )
		#pk״̬�ı�֪ͨ�Լ�
		ECenter.fireEvent( "EVT_ON_ROLE_PKSTATE_CHANGED", self.pkState )

	def set_isPkModelock( self, oldValue ):
		"""
		pk״̬�ı�
		"""
		#pk״̬�ı�֪ͨ�Լ�
#		self.cell.setPkMode( self.pkMode )
		ECenter.fireEvent( "EVT_ON_ROLE_IS_PKMODE_LOCK", oldValue, self.isPkModelock )

	def set_pkValue( self, oldValue ):
		"""
		pkֵ�ı�
		"""
		#pkֵ�ı�֪ͨ
		ECenter.fireEvent( "EVT_ON_ROLE_PKVALUE_CHANGED", self.pkValue )

	def set_pkMode( self, oldValue ):
		"""
		pkģʽ�ı�
		"""
		Role.set_pkMode( self, oldValue )
		msg = Const.PK_MODEL_MSG_MAPS.get( self.pkMode )
		if msg is None: return
		self.statusMessage( csstatus.ROLE_PK_MODE_CHANGE, msg )
		self.refurbishAroundRoleHPColor()

	def refurbishAroundRoleHPColor( self ):
		"""
		������Χ��ҵ�Ѫ����ɫ
		"""
		roles = self.entitiesInRange( csconst.ROLE_AOI_RADIUS, \
		cnd = lambda ent : ent.getEntityType() == csdefine.ENTITY_TYPE_ROLE \
		and ent.id != self.id )
		for role in roles:
			if hasattr( role, "refurbishHPColor" ):
				role.refurbishHPColor()

	def set_sysPKMode( self, oldValue ):
		"""
		pkģʽ�ı�
		"""
		Role.set_sysPKMode( self, oldValue )

	# -------------------------------------------------
	# Ԫ������ֵ�����仯
	# -------------------------------------------------
	def set_elem_huo_damage( self, oldValue ) :
		"""
		��Ԫ���˺������仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_FIRE_DAMAGE_CHANGED", self.elem_huo_damage )

	def set_elem_huo_derate_ratio( self, oldValue ) :
		"""
		��Ԫ�ؿ��Է����仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_FIRE_DERATE_RATIO_CHANGED", self.elem_huo_derate_ratio )

	def set_elem_xuan_damage( self, oldValue ) :
		"""
		��Ԫ���˺������仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_XUAN_DAMAGE_CHANGED", self.elem_xuan_damage )

	def set_elem_xuan_derate_ratio( self, oldValue ) :
		"""
		��Ԫ�ؿ��Է����仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_XUAN_DERATE_RATIO_CHANGED", self.elem_xuan_derate_ratio )

	def set_elem_lei_damage( self, oldValue ) :
		"""
		��Ԫ���˺������仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_THUNDER_DAMAGE_CHANGED", self.elem_lei_damage )

	def set_elem_lei_derate_ratio( self, oldValue ) :
		"""
		��Ԫ�ؿ��Է����仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_THUNDER_DERATE_RATIO_CHANGED", self.elem_lei_derate_ratio )

	def set_elem_bing_damage( self, oldValue ) :
		"""
		��Ԫ���˺������仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_ICE_DAMAGE_CHANGED", self.elem_bing_damage )

	def set_elem_bing_derate_ratio( self, oldValue ) :
		"""
		��Ԫ�ؿ��Է����仯
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ELM_ICE_DERATE_RATIO_CHANGED", self.elem_bing_derate_ratio )

	def set_posture( self, oldValue ) :
		"""
		��̬�ı�
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_POSTURE_CHANGED", self.posture, oldValue )

	def set_range( self, oldValue ) :
		"""
		��������ı�
		"""
		self.onUpdateNormalSkill()

	# -------------------------------------------------
	def onMoveChanged( self, isMoving ) :
		"""
		�ƶ�״̬�ı�ص�
		"""
		Attack.onMoveChanged( self, isMoving )
		self.stopPickUp()
		if self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			self.stopDance()	# ֹͣ����
		if self.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:
			self.cell.stopRequestDance()	# ֹͣ�������裬ȡ������
		if len( self.tempFace ) != 0 :			# ֹͣ���ű��鶯��
			self.cell.stopFaceAction( self.tempFace )
		self.interuptPendingBuff()

	def onAssaultStart( self ):
		"""
		��ʼ���
		ԭ��Ϊ��onMovetoProtect����������Ϊ onAssaultStart( hyw--09.01.12 )
		"""
		self.__unbindShortcuts()						# ���η����
		self.__isAssaulting = True						# ����Ϊ���״̬
		self.updateMoveMode()

	def onAssaultEnd( self ) :
		"""
		defined method
		�������
		ע�⣺�������󣬸÷����ᱻ�������Σ�һ���Ƿ������ĳ��ص���һ���ǿͻ����Լ������ʱ�䵽��ص�
			  �����ܱ�֤�ĸ��ȵ��ã������Ǵε��ý��ᱻ self.__isAssaulting Ϊ False ���ض�������
			  �������ǲ��Եģ�������Ϊ�˼��ٳ��󣬽�ɫ���߹�ͷ�����⣬ȷ�������������Ͻ���ɫ�ƶ�ֹͣ����
		hyw--09.01.12
		"""
		self.__isAssaulting = False
		self.__bindShortcuts()							# ��η����
		self.stopMove()

	def onStateChanged( self, old, new ) :
		"""
		virtual method.
		״̬�л���
		@param old	:	������ǰ��״̬
		@type old	:	int
		@param new	:	�����Ժ��״̬
		@type new	:	int
		"""
		self.actionState = new
		Role.onStateChanged( self, old, new )
		Attack.onStateChanged( self, old, new )
		#��ȥ
		if new == csdefine.ENTITY_STATE_DEAD :
			# ������ʱ��Ӧ�ø�λ����ģʽ
			self.c_control_mod = Const.CAMERA_CONTROL_MOD_1

			#if old == csdefine.ENTITY_STATE_FIGHT:
			# ����κη����Ͽ����е��ٶ�
			self.stopMove()

			# ������������������ʲô��������ôֹͣ����
			if self.isOnSomething():
				DEBUG_MSG( "Corpse hit something, stop falling!" )
				self.physics.fall = False
			# else:
				# ˵����ʱ���ڵ��䣬�����κδ�������ҵ���ĳ�����棬__onFallToGround���Զ��رյ���
				# �Ӷ�������䵽ĳЩ�����ϻ���ֵľ�ͷ������˸������ by mushuang

			if self.isJumping():	#�������ʱ������Ծ״̬���������ڵ���
				self.physics.fall = True

			BigWorld.callback( 2.0, self.pointReviveClew )
		elif new == csdefine.ENTITY_STATE_FREE and old ==  csdefine.ENTITY_STATE_DEAD:
			self.physics.fall = True	#����֮��Ҫ������������ spf
			# ������ģʽ��λ
			self.c_control_mod = Const.CAMERA_CONTROL_MOD_2
			self.__flyingVehicle.resetDeathDepthReached()				# ������������

	def onPkStateChange( self, old, new ):
		"""
		virtual method.
		״̬�л���
		@param old	:	������ǰ��״̬
		@type old	:	int
		@param new	:	�����Ժ��״̬
		@type new	:	int
		"""
		#do something
		pass

	def pointReviveClew( self ):
		"""
		����㸴����ʾ
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
			ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX_ON_FALLING_DOWN" ) # �߿յ������ʱ������ѡ�����ޡ�ԭ�ظ��
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
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
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

		# ȫ����ս�ж�
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
			# �Ѻ���Ӫ�б��ж�
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

		# �����ս����
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

		# �����ǳ���
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = entity.getOwner()
			if owner is None:
				return csdefine.RELATION_NOFIGHT
			else:
				entity = owner

		# �������ˣ��д��ж�
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self.qieCuoTargetID == entity.id:
				return csdefine.RELATION_ANTAGONIZE

		# ��ս�ж�
		if self.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT

		if self.canPk( entity ):
			return csdefine.RELATION_ANTAGONIZE
		else:
			return csdefine.RELATION_FRIEND

	def queryGlobalCombatConstraint( self, entity ):
		"""
		��ѯȫ��ս��Լ��
		"""
		# �۲���ģʽ
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

		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_FRIEND_ROLE ): #�������Ҿ����Ѻñ�־
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
		if self.state == csdefine.ENTITY_STATE_RACER:											#����״̬�������Ѻ�
			return csdefine.RELATION_FRIEND

		# ��ս
		if self.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT

		# ȫ����ս�ж�
		if self.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
			entity.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT

		return csdefine.RELATION_NONE

	def refurbishAroundQuestStatus( self ):
		"""
		������ΧNPC������״̬
		"""
		for key, entity in BigWorld.entities.items():
			if hasattr( entity, "refurbishQuestStatus" ):
				entity.refurbishQuestStatus()

	# -------------------------------------------------
	def __queryGossipTarget( self, className ):
		"""
		�Զ�Ѱ·/��·�䴫�ͽ��������ID����Ŀ��NPC
		gjx 2009.02.18
		@type		className	: str
		@param		className	: �Զ�Ѱ·Ŀ��NPC��ID
		@rtype					: entity
		"""
		targetList = []
		for entity in BigWorld.entities.values():
			if hasattr( entity, 'className' ) and \
			entity.className == className and \
			rds.targetMgr.isDialogicTarget( entity ):						# �ǿɶԻ�Ŀ��
				targetList.append( entity )
		if len( targetList ) <= 0: return None
		t1 = targetList.pop()
		pos = self.position
		while targetList:
			t2 = targetList.pop()
			if pos.distTo( t1.position ) > pos.distTo( t2.position ):		# ���Ҿ�����������NPC
				t1 = t2
		return t1

	def talkWithTarget( self, className ):
		"""
		��Ŀ��Ի���ͬʱ��Ŀ���Ϊ��ǰĿ�꣬�Զ�Ѱ·/��·�䴫�ͽ��������
		gjx 2009.02.18
		@param		className	: Ŀ���ID����entity.className���Զ�Ӧ
		@type		className	: str
		"""
		retryTime = 6									# ���Բ��ҵĴ���
		def delayTalk( retryTime ) :					# �Ҳ���ʱ��ʱһ��ʱ�������
			if retryTime < 1 : 							# ʹ�������������Ϊ�ܶ������NPC��������ˢ��
				INFO_MSG( "Can't find gossip target by ID:%s!" % className  )
				return
			target = self.__queryGossipTarget( className )
			if target is not None :
				rds.targetMgr.talkWithTarget( target )	# �Ի�
			else :
				BigWorld.callback( 0.5, Functor( delayTalk, retryTime - 1 ) )
		delayTalk( retryTime )

	def onUseFlyItem( self ):
		"""
		define method.
		ʹ����·��ص�
		"""
		self.delayTeleportIsFail = True
		ECenter.fireEvent( "EVT_ON_HIDE_SPE_OCBOX" )

	def getExpectTarget( self ):
		"""
		��ȡ��Ҫ���ҶԻ��� NPC �� className
		"""
		return self.__expectTarget

	def setExpectTarget( self, className ) :
		"""
		���ý�Ҫ���ҶԻ��� NPC �� className( ��ҪѰ·���� teleport ����Ŀ�������������Ի� )
		"""
		self.__expectTarget = className

	def onBeforeAutoRun( self ):
		"""
		�Զ�Ѱ·֮ǰ����һЩ����
		"""
		self.stopAutoFight()

	def onStartAutoRun( self, position ):
		"""
		��ʼ�Զ�Ѱ·
		"""
		Action.Action.onStartAutoRun( self, position )
		if self.onWaterArea and self.onWaterJumpTimer is None:	# ����պô���ˮ���У�����ˮ����Ծ�ص�
			self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )
		ECenter.fireEvent( "EVT_ON_START_AUTORUN", position )

		# �Զ���˹���
		self.antoRunConjureVehicle()

	def antoRunConjureVehicle( self ):
		"""
		�Զ�Ѱ·�Զ���˹���
		"""
		if not self.inWorld: return
		# �ж��Ƿ����Զ�Ѱ·״̬��
		if not self.isActionState( Action.ASTATE_NAVIGATE ): return
		# �ж��Ƿ���ս��״̬��
		if self.state == csdefine.ENTITY_STATE_FIGHT: return
		# �ж��Ƿ���ˮ��
		if self.onWaterArea: return
		# �ж��Ƿ��м������
		if not self.activateVehicleID: return
		# �ж��Ƿ��Ѿ������״̬
		if self.vehicleModelNum: return

		self.conjureVehicle( self.activateVehicleID )

	def onEndAutoRun( self, state ):
		"""
		Ѱ·����ʱ������
		"""
		Action.Action.onEndAutoRun( self, state )
		if self.isMoving():		# ֹͣ��ǰ�ƶ�
			self.stopMove()
		if self.onWaterJumpTimer is not None:	# �Զ�Ѱ·����ֹͣˮ����Ծ�ص�
			BigWorld.cancelCallback( self.onWaterJumpTimer )
			self.onWaterJumpTimer = None
		ECenter.fireEvent( "EVT_ON_STOP_AUTORUN", state )
		if state and self.__expectTarget != "":
			self.talkWithTarget( self.__expectTarget )
		self.__expectTarget = ""

	def getAutoRunPathLst( self ):
		"""
		��ȡ�Զ�Ѱ·��·���ڵ��б�
		"""
		if self.vehicle:
			return self.vehicle.getAutoRunPathLst()
		return Action.Action.getAutoRunPathLst( self )

	def getAutoRunGoalPosition( self ):
		"""
		��ȡ�Զ�Ѱ·��Ŀ��λ��
		"""
		if self.vehicle:
			return self.vehicle.getAutoRunGoalPosition()
		return Action.Action.getAutoRunGoalPosition( self )

	# ----------------------------------------------------------------
	# ��ҽ����뿪�ռ�
	# ----------------------------------------------------------------
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
		#------------------------------����һ������ƶ�----------------
	def autoFollow(self, targetID ):
		"""
		����һ������ƶ�
		tidy up by huangyongwei -- 2008.12.24
		"""
		if self.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ): return

		if targetID == self.id : return 							# ���Լ�������ָ����ѡ��,��������ж�ֻ��Ϊ���Ͻ�.
		target = BigWorld.entities.get( targetID )
		if not target:
			return
		lenth = self.position.flatDistTo( target.position ) 		# ���������Ŀ��ľ���
		if lenth > 20.0 : 											# ������볬��20�� ��ʾ�����Զ ���ܸ���
			self.statusMessage( csstatus.FOLLOW_FAILD_FAR )
			return

		self.setActionState( Action.ASTATE_FOLLOW )				# ������ƶ���ʽ�޸�Ϊ�����ƶ�
		if self.vehicle:
			self.vehicle.setActionState( Action.ASTATE_FOLLOW )
		self.checkFollowing( targetID )

	def getSpeed( self ):
		"""
		PlayerRole��ͳһ�ӿ�,��ȡ�ٶ�
		"""
		if self.vehicle:
			return self.vehicle.getSpeed()
		else:
			return Action.Action.getSpeed( self )

	def checkFollowing( self, targetID ):
		"""
		�ص�����,���ڼ���Ƿ���Ҫ��Ŀ���ƶ��Լ��Ƿ񳬳���Χ,ֹͣ�ƶ�
		"""
		BigWorld.cancelCallback( self.__followCallBack )
		target = BigWorld.entities.get( targetID )
		if not target :
			return										# ���Ŀ�겻����
		position = target.position
		lenth = self.position.flatDistTo( target.position )			# ���������Ŀ��ľ���
		if lenth > Const.ROLE_FOLLOW_MAX_DISTANCE : return 									# ����������20���� ȡ������

		if not self.allowMove():									# ���Ŀǰ�������ƶ�
			return

		if self.vehicle and not self.vehicle.isActionState( Action.ASTATE_FOLLOW ):
			return
		elif not self.isActionState( Action.ASTATE_FOLLOW ): 	# ����ƻ����˸���״̬ ��ôȡ������
			return

		if lenth - 0.2 * self.getSpeed() < Const.ROLE_FOLLOW_NEAR_DISTANCE:					# �����һ�μ��ʱ�Ѿ��ܵ�С��Ŀ��1.0�״�,���ھ�ͣ��
			self.stopMove() 									# ֹͣ�ƶ�
			self.__followCallBack = BigWorld.callback( 0.2, Functor( self.checkFollowing, targetID ) )
			return
		else:   #������Ŀ��Ͻ�λ�ã������ں�Ŀ����ȫ�غ� add by wuxo
			disRate = (lenth - Const.ROLE_FOLLOW_NEAR_DISTANCE)/Const.ROLE_FOLLOW_NEAR_DISTANCE
			posX = (self.position[0] + disRate*position[0])/(1+disRate)
			posY = (self.position[1] + disRate*position[1])/(1+disRate)
			posZ = (self.position[2] + disRate*position[2])/(1+disRate)
			position = Math.Vector3(posX,posY,posZ)

		if self.getState() == csdefine.ENTITY_STATE_DEAD:			# ֻ�������� �Ż���Ӵ˱�� ������������ж��Ƿ�
			return

		self.moveTo( position, None )			# �����ȥ
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
		��ȡ��ǰ����space������ ���忴csdefine.SPACE_TYPE_*
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
		λ�洫�ͽ�Ҫ��ʼ��
		"""
		DEBUG_MSG( "ready." )
		BigWorld.planeSpacePrepare()
		self.parallelSpaceID = self.spaceID

	def onLeaveSpaceForPlane( self ):
		"""
		����뿪space�ص���������ҽ�Ҫ�뿪һ��space������Ľ���һ��λ�档
		�˺���������ײ�ֱ�ӵ��á�
		"""
		DEBUG_MSG( "old plane space:", self.spaceID )
		rds.targetMgr.unbindTarget()
		self.team_leaveSpace()
		self.parallelSpaceID = -1
		ECenter.fireEvent("EVT_ON_LEAVE_PLANE")

	def onEnterPlane( self ):
		"""
		��ҽ���λ��Ļص���������ҽ�����һ����spaceλ�档
		�˺���������ײ�ֱ�ӵ��á�
		"""
		DEBUG_MSG( "enter plane space:", self.spaceID )
		self.team_enterSpace()
		RoleQuestInterface.onEnterSpace_( self )
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_WM:
			ECenter.fireEvent("EVT_ON_ENTER_PLANE")

	def onLeaveSpace( self ):
		"""
		����뿪space�ص���������ҽ�Ҫ�뿪һ��space��
		�˺���������ײ�ֱ�ӵ��á�
		ע�⣺�˻ص���entity�˳�ʱ���磺�� PlayerRole �л� Account���������á�
		"""
		self.emptyDirection()
		self.stopAutoFight()			# ���пռ䴫��ʱֹͣ�Զ����(���������stopMove()) 2008-11-5 gjx
		rds.targetMgr.unbindTarget()
		self.team_leaveSpace()
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		BigWorld.clearDecals()
		rds.gameMgr.onLeaveSpace()
		self.disableFlyingRelatedDetection()          # �ռ䴫�Ͷ��������йرճ����߽���ײ��������͹���������
		rds.gameSettingMgr.onPlayerLeaveSpace()				# �ָ���ͼ����Ϸ�Զ�������
		self.levelYXLMChangeCamera()
		# �뿪λ��֪ͨ
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_WM:
			ECenter.fireEvent("EVT_ON_LEAVE_PLANE")

	def onEnterSpace( self ):
		"""
		��ҽ���space�Ļص���������ҽ�����һ����space��
		�˺���������ײ�ֱ�ӵ��á�
		ע�⣺�˽ӿ��ڵ�һ�ν�����Ϸʱ�������á�
		"""
		if isPublished:
			BigWorld.callback( 1.0, checkCurrentSpaceData )
		def func():
			BigWorld.dcursor().yaw = BigWorld.player().yaw
		BigWorld.callback( 0.2, func ) # dcursor().yaw�ᶨʱ�ı�player().yaw������player().yawδ����ı�ǰͬ��dcursor().yaw����ֹ��ɫ����֮�����򲻶�
		self.emptyDirection()
		if hasattr( self.physics, "fall" ):
			self.physics.fall = False
		if self.isJumping():
			self.physics.stop()
#			self.physics.fall = True
		self.team_enterSpace()
		self.stopMove()
		ECenter.fireEvent( "EVT_ON_PLAYER_ENTER_SPACE" )
		rds.gameSettingMgr.onPlayerEnterSpace()				# Ӧ�õ�ͼ����Ϸ�Զ�������
		RoleQuestInterface.onEnterSpace_( self )

	def onEnterArea( self, newArea ) :
		"""
		����ҽ���ĳ������ʱ������
		"""
		if self._oldArea is not None and self._oldArea == newArea:
			sn = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_NUMBER )
			if sn == self._oldSpaceNumber:
				return
			self._oldSpaceNumber = sn
		else:
			# ����濪��TimeOfDay����
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
				rds.soundMgr.switchMusic( newArea.getMusic() )		# ��������
				rds.soundMgr.switchBgEffect( newArea.getBgSound() )	# ������Ч
				self.statusMessage( csstatus.YOU_HAVE_COME_IN, newArea.name )
		ECenter.fireEvent( "EVT_ON_ROLE_ENTER_AREA", newArea )

	def onEnterAreaFS( self ) :
		"""
		defined method.
		������ĳ������ʱ������( ͬ��ͼ��������תʱ������ )
		hyw -- 2008.10.08
		"""
		BigWorld.dcursor().yaw = BigWorld.player().yaw # dcursor().yaw�ᶨʱ�ı�player().yaw������player().yawδ����ı�ǰͬ��dcursor().yaw����ֹ��ɫ����֮�����򲻶�
		self.emptyDirection()
		self.team_enterSpace()
		newArea = self.getCurrArea()
		self.onEnterArea( newArea )

	def onLeaveAreaFS( self ) :
		"""
		defined method.
		���뿪ĳ������ʱ������( ͬ��ͼ��������תʱ������ )
		hyw -- 2008.10.08
		"""
		if not rds.statusMgr.isInWorld() :
			return						# ĳЩ����£����������ڽ�ɫ��½�����н���ɫ���͵�ĳ��λ��
		self.emptyDirection()
		self.stopAutoFight()			# ����������ʱֹͣ�Զ���� 2008-11-5 gjx
		self.stopPickUp()				# ����������ʱ�ر�ʰȡ����
		self.team_leaveSpace()
		rds.targetMgr.unbindTarget()	# ����ʱȡ��ѡ��ǰĿ��
		ECenter.fireEvent( "EVT_ON_RESTORE_SCREEN" )
		rds.gameMgr.onLeaveArea()

	def beforeEnterDoor( self ):
		"""
		���봫����֮ǰ��Ҫ��һЩ���顣����
		"""
		if self.__expectTarget != "":
			self.__spanSpaceTarget = self.__expectTarget				# ��ʱ���棬��ֹ�������ź����
		self.__spanSpaceDataLock = True
		self.stopMove()

	def canSelectTarget( self, target ):
		return target.canSelect()

	def onLoginSpaceIsFull( self ):
		"""
		define method.
		��½��ĳ������ ������Ա��
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.disconnect()
		# "������¼�ĳ����Ѿ���Ա�ˣ����Ժ��½��"
		showMessage( 0x0124, "", MB_OK, query )

	def delayTeleport( self, skill, caster, spaceName, pos, npcName, delayTime ):
		"""
		�ӳٴ���
		"""
		if skill is None: return
		if caster is None: return
		if delayTime < 0: return
		ECenter.fireEvent( "EVT_ON_HIDE_SPE_OCBOX" )  # ����ǰ��Ľ���
		def teleport( id ):
			if id == RS_SPE_OK:
				result = True
			else:
				result = False
			self.atonceTeleport( spaceName, pos, result )
		self.delayTeleportNpc = caster
		self.delayTeleportTime = delayTime
		self.delayTeleportIsFail = False	# ��Ĭ��Ϊ���Դ���
		# "�ҽ�ʩչ%s�������͵�%s����׼��������? "
		msg =  mbmsgs[0x012d] % ( skill.getName(), npcName )
		showAutoHideMessage( delayTime + 1.0, msg, labelGather.getText( "MsgBox:speOCBox", "lbTitle" ), MB_SPE_OK_CANCEL, teleport, gstStatus = Define.GST_IN_WORLD )
		BigWorld.cancelCallback( self.delayTeleportCBID )
		self.delayTeleportCBID = BigWorld.callback( delayTime, Functor( self.delayOver, spaceName, pos ) )
		BigWorld.callback( 0.1, self.playerToNpc )

	def atonceTeleport( self, spaceName, pos, result ):
		"""
		�������̴��ͻ���ȡ�����Ͱ�ť
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
		�ӳ�ʱ���������ʼ����
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
		�����ʩ��NPC�������Ƽ��
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
		�˺���ʾ
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skill  : ����ʵ��
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
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

		# ���ܲ����˺�ʱ��ϵͳ��Ϣ�ȴ���
		if damage <= 0:
			if casterID > 0 and BigWorld.entities.has_key( casterID ):
				caster = BigWorld.entities[casterID]
				casterName = caster.getName()
				if self.onFengQi and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					casterName = lbs_ChatFacade.masked
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# ��������%s��%s��
					self.statusMessage( csstatus.SKILL_SPELL_DODGE_TO_SKILL, casterName, sk.getName() )
					# ���ܶ���
					if self.canPlayEffectAction():
						self.playActions( [dodgeActionName] )

			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# ��������%s��
					self.statusMessage( csstatus.SKILL_SPELL_DODGE_TO, sk.getName() )
					# ���ܶ���
					if self.canPlayEffectAction():
						self.playActions( [dodgeActionName] )
		else:
			if casterID > 0 and BigWorld.entities.has_key( casterID ):
				caster = BigWorld.entities[casterID]
				casterName = caster.getName()
				if self.onFengQi and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					casterName = lbs_ChatFacade.masked
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# ���м���%s��%s���ܵ�%i����˺���
					if (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
						self.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_TO_DOUBLEDAMAGE, casterName, sk.getName(), damage )
					else:
						self.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_TO, casterName, sk.getName(), damage )
					# �мܶ���
					if self.canPlayEffectAction():
						self.playActions( [resistActionName] )

				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# %s��%s�����������%i����˺���
					self.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_FROM_SKILL, casterName, sk.getName(), damage )
				else:#
					if (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
						if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:
							# ���ܵ���%s������%i�㷨���˺���
							self.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC, casterName, damage )
						else:
							# ���ܵ���%s������%i���˺���
							self.statusMessage( csstatus.SKILL_BUFF_REBOUND_PHY, casterName, damage )
					else:
						#%s��%s���������%i���˺���
						self.statusMessage( csstatus.SKILL_SPELL_DAMAGE_FROM_SKILL, casterName, sk.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# ���м���%s���ܵ�%i����˺���
					self.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_FROM, sk.getName(), damage )
					# �мܶ���
					if self.canPlayEffectAction():
						self.playActions( [resistActionName] )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# %s�����������%i����˺���
					self.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_FROM, sk.getName(), damage )
				else:
					# %s��%s���������%i���˺���
					self.statusMessage( csstatus.SKILL_SPELL_DAMAGE_FROM, sk.getName(), damage )

	def isSunBathing( self ):
		"""
		����Ƿ��ڽ����չ�ԡ
		"""
		spaceType = self.getCurrentSpaceType()
		return spaceType == csdefine.SPACE_TYPE_SUN_BATHING

	def addTalismanExp( self ):
		"""
		���ӷ�������
		"""
		if self.EXP == 0: return
		# �жϸ÷�����Ʒ�Ƿ����
		item = self.getItem_( ItemTypeEnum.CEL_TALISMAN )
		if item is None:return
		# �ж��ǲ��Ƿ�������
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN: return
		# ��������ﵽ��ߵȼ���ֱ�ӷ���
		itemLevel = item.getLevel()
		if itemLevel >= 150: return

		# ������ȡ�������ӹ��򣬷����ȼ�ֻ������Ʒ�ʵȼ���Χ���о���ֵ�仯 by����
		expMap = csconst.TALISMAN_LEVELUP_MAP
		grade = item.getGrade()
		if itemLevel >= expMap[grade][0]:
			self.statusMessage( expMap[grade][1] )
			return

		self.cell.addTalismanExp()

	def addTalismanPotential( self ):
		"""
		���ӷ���Ǳ�ܵ�
		"""
		# �������Ǳ�ܵ�Ϊ0��ֱ�ӷ���
		if self.potential == 0: return
		# �жϸ÷�����Ʒ�Ƿ����
		item = self.getItem_( ItemTypeEnum.CEL_TALISMAN )
		if item is None: return
		# �ж��ǲ��Ƿ�������
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN: return
		# ����������ܴﵽ��ߵȼ���ֱ�ӷ���
		skillLevel = item.getSkillLevel()
		if skillLevel >= 150: return

		# ������ȡǱ�����ӹ��򣬷����ȼ�ֻ������Ʒ�ʵȼ���Χ����Ǳ�ܱ仯 by����
		expMap = csconst.TALISMAN_LEVELUP_MAP
		grade = item.getGrade()
		if skillLevel >= expMap[grade][0]:
			self.statusMessage( expMap[grade][2] )
			return

		self.cell.addTalismanPotential()

	def updateTalismanGrade( self ):
		"""
		��������Ʒ��
		"""
		# �ж���Ʒ�Ƿ����
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# �ж��ǲ��Ƿ�������
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return
		grade = talismanItem.getGrade()
		level = talismanItem.getLevel()

		# ��������Ʒ��Ҫ����50��
		if grade == ItemTypeEnum.TALISMAN_COMMON and level < csconst.TALISMAN_UPTO_IMMORTAL_LEVEL:
			self.statusMessage( csstatus.TALISMAN_UPDATE_TOI_NEED_LEVEL )
			return
		# ��������Ʒ��Ҫ����100��
		if grade == ItemTypeEnum.TALISMAN_IMMORTAL and level < csconst.TALISMAN_UPTO_DEITY_LEVEL:
			self.statusMessage( csstatus.TALISMAN_UPDATE_TOD_NEED_LEVEL )
			return
		# �жϷ���Ʒ�ʵȼ��Ƿ��Ѿ��ﵽ��ߵȼ�
		if grade == ItemTypeEnum.TALISMAN_DEITY:
			self.statusMessage( csstatus.TALISMAN_GRADE_TOP )
			return

		# ������������Ƿ������Ӧ�Ĳ�����Ʒ
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
		���취������
		"""
		if len( grades ) == 0 or len( indexs ) == 0: return
		# �ж���Ʒ�Ƿ����
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# �ж��ǲ��Ƿ�������
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return

		# �ж����Я���Ĳ����Ƿ��㹻
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
		��ʾ�������ƽ���
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_GOD_WEAPON_MAKER" )

	def onEquipGodWeapon( self ):
		"""
		define method
		�������ɳɹ�
		"""
		ECenter.fireEvent( "EVT_ON_GOD_WEAPON_MAKER_SUCCESS" )

	def onRebuildAttrCB( self, grade, index, key ):
		"""
		define
		�������Ը���ɹ����������˻ص�
		"""
		ECenter.fireEvent( "EVT_ON_TALISMAN_ATTR_REBUILD", grade, index, key )

	def onActivatyAttrCB( self, grade, index ):
		"""
		define
		�������Լ���ɹ����������˻ص�
		"""

		ECenter.fireEvent( "EVT_ON_TALISMAN_ATTR_ACTIVATY", grade, index )

	def onTalismanLvUp( self ):
		"""
		����������ʱ����
		"""
		ECenter.fireEvent( "EVT_ON_TALISMAN_LV_UP" )

	def onTalismanSkillLvUp( self ):
		"""
		��������������ʱ����
		"""
		ECenter.fireEvent( "EVT_ON_TALISMAN_SK_UP" )

	def createDynamicItem( self, itemID, amount = 1 ):
		"""
		����ϵĽӿڴ���һ����̬��Ʒ
		"""
		return items.instance().createDynamicItem( itemID, amount )

	def canPk( self, entity ):
		"""
		�ж��Ƿ���pkһ��entity
		@param entity: entity
		@type  entity: entity
		"""
		if entity is None: return False

		# ������Լ����ܹ���
		if self.id == entity.id: return False

		# ����ͬһ��ͼ����PK
		if self.spaceID != entity.spaceID:
			return False

		# ��ɫ���ڵ�ͼ�Ƿ�����pk
		if self.getCanNotPkArea(): return False

		# ������ڷ���״̬��������pk
		if isFlying( self ): return False

		# 30����ұ���
		if self.pkState == csdefine.PK_STATE_PROTECT: return False

		# �ж��Ƿ�Ϊ����ǵĻ���Ŀ��ת�Ӹ�����
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			entity = entity.getOwner()
			# �Ҳ����ó�������� ���ܹ���
			if entity is None: return False

		# �ж��Ƿ������
		if not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return False

		# �����Ա����PK
		if self.isTeamMember( entity.id ):
			return False
		# 30���Է���ҽ�ֹpk
		if entity.pkState == csdefine.PK_STATE_PROTECT:
			return False

		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and not entity.actionSign( csdefine.ACTION_FORBID_PK ):
			if self.inDamageList( entity ) or self.pkTargetList.has_key( entity.id ):
				return True

		if self.sysPKMode:
			# ����ҵ�pkģʽ�Ǻ�ƽģʽ���ܹ���
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_PEACE:
				return False

			# ��ս�����а���Ա����PK
			if self.tong_dbID != 0 and ( self.tong_dbID == entity.tong_dbID ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG:
				return False

			# ��Ӫս��������Ӫ��Ա����PK
			if self.getCamp() != 0 and ( self.getCamp() == entity.getCamp() ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP:
				return False

			if self.sysPKMode in csdefine.SYS_PK_CONTOL_ACT:
				if self.sysPKMode == entity.sysPKMode:
					return False
			# ϵͳģʽΪ��ʱ��Ӫģʽ
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TEMPORARY_FACTION :
				if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG and ( not RoleYiJieZhanChangInterface.canPk( self, entity ) ) :
					return False
			# ϵͳģʽΪ����ģʽ
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_LEAGUE:
				if self.checkCityWarTongBelong( self.tong_dbID, entity.tong_dbID ):
					return False
		else:
			# ����ҵ�pkģʽ������ģʽ��ԭ�ƶ�ģʽ������entity���ǻƺ���
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_RIGHTFUL and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ]:
				return False

			# ����ҵ�pkģʽ������ģʽ����entity���ǻƺ���
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_JUSTICE and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ] \
				and self.getCamp() == entity.getCamp():
				return False

		# �Է�����Ӹ���״̬�¿ɹ���
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and entity.isFollowing(): return True

		# ����ұ���ֹPK������Ҫpk��entity����ֹpk������ĳ���ڰ�ȫ����
		if self.actionSign( csdefine.ACTION_FORBID_PK ) or entity.actionSign( csdefine.ACTION_FORBID_PK ):
			return False

		return True

	def pkStateMessage( self ):
		"""
		Ϊ�˸���NC��PK��ֹ��ʾ by����
		"""
		player = BigWorld.player()
		target = player.targetEntity
		if target is None: return None
		if target.getEntityType() != csdefine.ENTITY_TYPE_ROLE: return None

		# ������Լ����ܹ���
		if self.id == target.id: return None

		if self.qieCuoTargetID == target.id: return None

		# 30����ұ���
		if self.pkState == csdefine.PK_STATE_PROTECT:
			return csstatus.ROLE_LEVEL_LOWER_PK_LEVEL

		# 30���Է���ҽ�ֹpk
		if target.pkState == csdefine.PK_STATE_PROTECT:
			return csstatus.ROLE_CAN_NOT_PK_TARGET

		# �����pkģʽ�����ģʽ����entity�Ƕ���
		if self.isTeamMember( target.id ):
			return csstatus.ROLE_PK_MODE_NOT_ALLOW

		# ����ҵ�pkģʽ�ǰ��ģʽ����entity�ǰ���Ա
		if self.sysPKMode and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG and self.tong_dbID != 0 and ( self.tong_dbID == target.tong_dbID ):
			return csstatus.ROLE_PK_MODE_NOT_ALLOW

		# ����ҵ�ϵͳpkģʽ����Ӫģʽ����entity����Ӫ��Ա
		if self.sysPKMode and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP and self.getCamp() != 0 and ( self.getCamp() == target.getCamp() ):
			return csstatus.ROLE_PK_MODE_NOT_ALLOW

		return None

	def onGetBenefitTime( self, benefitTime ):
		"""
		defined method
		��ô���֮��buff�ۻ�ʱ�� by����
		"""
		self.benefitTime = benefitTime

	def onLineCount( self ):
		"""
		����ʱ����۵Ŀͻ��˺�̨���� by����
		"""
		LevelUpAwardReminder.instance().onRoleBenefit()

	def startKLJDActivity( self ):
		"""
		���ҵ�����
		"""
		INFO_MSG( '----------------startKLJDActivity' )
		pass

	def endKLJDReward( self ):
		"""
		һ���ҵ�����
		"""
		INFO_MSG( '----------------endKLJDReward' )
		pass

	def startSuperKLJDActivity( self ):
		"""
		���ҵ�����
		"""
		INFO_MSG( '----------------startKLJDActivity' )
		pass

	def stopDance( self ):
		"""
		ֹͣ����
		"""
		self.cell.stopDance()

	def receiveRequestDance( self, requestEntityID ):
		"""
		���ܵ����빲��
		"""
		ECenter.fireEvent( "EVT_ON_INVITE_JOIN_DANCE", requestEntityID )

	def askSuanGuaZhanBu( self, money ):
		"""
		���ܵ����빲��
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_MESSAGE_SUANGUAZHANBU", money )

	def stopRequestDance( self ):
		"""
		ȡ�����빲��
		"""
		ECenter.fireEvent( "EVT_ON_STOP_REQUEST_DANCE" )

	def onNPCOwnerFamilyNameChanged( self, npcID, ownerName ):
		"""
		"""
		ECenter.fireEvent( "EVT_ON_NPC_FAMILY_NAME_CHANGE", npcID, ownerName )

	def onFixTimeReward( self, timeTick, itemID, rewardOrder, lifetime , lastRewardID ):
		"""
		defined method
		��ʱ�����Ŀͻ���֪ͨ by����
		"""
		ECenter.fireEvent( "EVT_ON_FIX_TIME_REWARD", timeTick, itemID, rewardOrder, lifetime, lastRewardID )


	def onOldFixTimeReward( self, timeTick, rewardOrder, rewardType, param ):
		"""
		defined method
		���ֶ�ʱ�����Ŀͻ���֪ͨ by����
		timeTick: ʣ��ʱ��
		RewardNum: ��������
		RewardType: ��������
		Param: �������� ���羭��ֵ ��ƷID��
		"""
		INFO_MSG( "receive old reward: %i type: %i param: %i "%( rewardOrder, rewardType, param ) )
		ECenter.fireEvent( "EVT_ON_OLD_FIX_TIME_REWARD", timeTick, rewardOrder, rewardType, param )


#------------------����ҵĽӿ�--------------------------------------------------
	def clientRecvApexMessage( self, strMsg,nLength ):
		"""
		�յ�����ҵ�����
		"""
		self.apexClient.NoticeApec_UserData(strMsg,nLength)

	def sendApexMessage( self, strMsg,nLength ):
		"""
		���ͷ���ҵ����� ����ǹ�C����������õĻص�����
		"""
		if self.base == None or self.base.clientSendApexMessage == None :
			return False
		self.base.clientSendApexMessage(strMsg,nLength)
		return True

	def startClientApex( self ):
		"""
		�յ��𶯷���ҵ�֪ͨ
		"""
		self.apexClient = BigWorld.getApexClient( )
		self.apexClient.InitAPexClient(self.sendApexMessage)
		re = self.apexClient.StartApexClient()
		msg = " StartApexClient re =%d"%re
		self.sendApexMessage(msg,len(msg))

	# --------------------------------------------------
	# �µ������
	# --------------------------------------------------
	def onAddVehicle( self, vehicleData ):
		"""
		Defined Method
		����2������������ӿ�
		1������Ϸ��ʹ�����󷵻ص�������ݣ�
		2��������Ϸ��������cell�����������ݣ�
		@return None
		"""
		id = vehicleData["id"]
		self.vehicleDatas[id] = dict( vehicleData.items() )
		# ֪ͨ����
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
		���ιʳ by����
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		oldDeadTime = vehicleData.get( "deadTime" )
		if oldDeadTime is None: return

		newDeadTime = deadTime + oldDeadTime
		newData = { "deadTime" : newDeadTime }
		vehicleData.update( newData )

		# ������Ϊ
		ECenter.fireEvent( "EVT_ON_VEHICLE_FEEDED", id, newDeadTime )

	def onUpdateVehicleSkPoint( self, id, skPoint ):
		"""
		Define Method
		��輼�ܵ����
		"""
		# ���¿ͻ�������
		self.vehicleDatas[id].update( { "skPoint" : skPoint } )
		# ֪ͨ����
		ECenter.fireEvent( "EVT_ON_VEHICLE_SKPOINT_UPDATE", id )


	#��贫���й�
	def  transVehicle( self, id ):
		"""
		����ǰ�������贫��
		"""
		#���ܸ������Լ�6������贫��
		vehicleData = self.vehicleDatas.get( id )
		if not vehicleData: return
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_NO_TRANS_LEVEL_MAX )
			return
		#��ҵ�ǰǱ�ܵ��Ƿ����0
		if  self.potential <= 0 :
			self.statusMessage( csstatus.VEHICLE_NO_ENOUGH_POTENTIAL )
			return
		#�жϴ�������ǲ��ǵ�ǰ��������
		if self.activateVehicleID!= id:
			self.statusMessage( csstatus.VEHICLE_NO_CURRENT_ACTIVATE )
			return
		self.base.transVehicle( id )

	def onUpdateVehicleProperty( self, id, level,strength,intellect,dexterity,corporeity, step, growth, srcID ):
		"""
		Define Method
		������Ը���
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		# ���¿ͻ�������
		data = { "level"    	: level,
			 "strength"	: strength,
			 "intellect"	: intellect,
			 "dexterity"	: dexterity,
			 "corporeity"  	: corporeity,
			 "step"		: step,
			 "growth"  	: growth,
			 "srcItemID"    : srcID
			}
		if vehicleData["step"] != step: #ˢ������ nextStepItemID
			data["nextStepItemID"] = getNextStepItemID( srcID )
		vehicleData.update( data )

		# ֪ͨ����
		ECenter.fireEvent( "EVT_ON_VEHICLE_UPDATE_ATTR", id )

	def onUpdateVehicleExp( self, id, exp ):
		"""
		Define Method
		��辭�����
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		# ���¿ͻ�������
		vehicleData.update( { "exp" : exp } )

		# ֪ͨ����
		ECenter.fireEvent( "EVT_ON_VEHICLE_EXP_UPDATE", id )


	#���ι�������������
	def canDomesticate(self):
		"""
		�ܷ�ιʳ������
		"""
		if self.state == csdefine.ENTITY_STATE_FREE:
			return True
		return False

	def domesticateVehicle( self, id, needItemID, count ):
		"""
		���ι��
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		if not self.canDomesticate():return

		items = self.findItemsByIDFromNK( needItemID )
		scount = 0
		for item in items:
			scount += item.getAmount()
		#��������
		if scount < count:
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return
		self.cell.domesticateVehicle( id, needItemID,count )

	def onUpdateVehicleFullDegree( self, id, fullDegree ):
		"""
		Define Method
		��豥���ȸ���
		"""
		# ���¿ͻ�������
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		newData = { "fullDegree" : fullDegree }
		vehicleData.update( newData )

		# ֪ͨ����
		ECenter.fireEvent( "EVT_ON_VEHICLE_FULLDEGREE_UPDATE", id )


	#��輤��
	def activateVehicle( self, vehicleDBID ):
		"""
		�������
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
				# �����׳費��Ҫιʳ ���ر���ʾ
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
		ȡ������
		"""
		if self.activateVehicleID != 0:
			self.cell.deactivateVehicle()


	#����ٻ�
	def conjureVehicle( self, vehicleDBID ):
		"""
		�ٻ����
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
				# �����׳費��Ҫιʳ ���ر���ʾ
				srcItemID = vehicleData.get( "srcItemID" )
				if srcItemID in ItemTypeEnum.ITEM_CHILD_VEHICLE:
					self.statusMessage( csstatus.VEHICLE_FEED_CHILD )
				else:
					self.statusMessage( csstatus.VEHICLE_FEED_DIE )
				return
		# Ǳ��״̬�²������ٻ����
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:
			self.statusMessage( csstatus.VEHICLE_NOT_SNAKE )
			return
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_NO_CONJURE )
			return

		self.base.conjureVehicle( vehicleDBID )


	#�������
	def upStepVehicle( self, mainID, oblationID, needItem ):
		"""
		�������
		"""
		#�ж����״̬
		if self.state != csdefine.ENTITY_STATE_FREE:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STATE_ERROR )
			return

		#�ж������Ƿ���������
		vehicleData = self.vehicleDatas.get( mainID )
		if vehicleData is None: return
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return #������Ƿ�����費������
		if not vehicleData["nextStepItemID"] : return #����豾��Ͳ�������
		if self.activateVehicleID!= mainID: #�ж�������ǲ��ǵ�ǰ��������
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_NOACT )
			return
		if self.vehicleDBID == mainID: #�ж�������ǲ��ǵ�ǰ��˵����
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_ISCONJURE )
			return

		#�жϼ����Ƿ���������
		o_vehicleData = self.vehicleDatas.get( oblationID )
		if o_vehicleData is None: return
		if o_vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		if self.activateVehicleID == oblationID: #�жϼ����ǲ��ǵ�ǰ��������
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ACT )
			return
		if self.vehicleDBID == oblationID: #�жϼ����ǲ��ǵ�ǰ��˵����
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ISCONJURE )
			return
		if o_vehicleData["step"] != vehicleData["step"]: #����ͼ���״��ǲ���һ��
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NOT_SAME )
			return

		#����Ҫ��
		items = self.findItemsByIDFromNK( needItem )
		if len(items) <= 0:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NO_ITEM )
			return
		self.cell.upStepVehicle( mainID, oblationID, needItem )


	#�������Ʒ
	def canTurnBack( self, id, needItem ):
		"""
		�ж��ܷ���б����Ʒ����
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return False  #�ж�����Ƿ����
		if self.activateVehicleID == id: return False #�ж��ǲ��ǵ�ǰ��������
		if self.vehicleDBID == id:return False #�ж��ǲ��ǵ�ǰ�ٻ������
		if self.state != csdefine.ENTITY_STATE_FREE:
			return False
		#����Ҫ��
		items = self.findItemsByIDFromNK( needItem )
		if len(items) <= 0:
			return False
		return True

	def vehicleToItem( self, id, needItem ):
		"""
		�������Ʒ
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
		���ιʳ by����
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		baseDeadTime = vehicleData.get( "deadTime" )
		if baseDeadTime is None: return
		if baseDeadTime == 0:
			self.statusMessage( csstatus.VEHICLE_FEED_IS_MAX )
			return
		if baseDeadTime >= csconst.VEHICLE_DEADTIEM_LIMIT:
			# ����Ҫιʳ
			self.statusMessage( csstatus.VEHICLE_FEED_IS_MAX )
			return

		# �����׳費��Ҫιʳ ���ر���ʾ
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
			# �޺��ʲ���
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return

		self.base.feedVehicle( id )

	def fixFreeVehicle( self, id ):
		"""
		ȷ�Ϸ������
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None:
			self.statusMessage( csstatus.FREE_VEHECLE_IS_NOTEXIST )
			return
		if not self.isAlive():		# ���������
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_DEAD )
			return
		if self.intonating():		# �������ʩ��
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_BUSY )
			return
		if id == self.activateVehicleID:  # �պ��Ǽ����
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISCONJURE )
			return
		if id == self.vehicleDBID:		 # �պ�������裨��Ҫ��Է�����裩
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISUSE )
			return

		def query( rs_id ):
			if rs_id == RS_OK:
				self.freeVehicle( id )
		# "��������轫�޷��ָ���ȷ��Ҫ����?"
		showMessage( mbmsgs[0x0d02], "", MB_OK_CANCEL, query, pyOwner = rds.ruisMgr.petWindow )

	def freeVehicle( self, id ):
		"""
		�������
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None:
			self.statusMessage( csstatus.FREE_VEHECLE_IS_NOTEXIST )
			return
		if not self.isAlive():		# ���������
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_DEAD )
			return
		if self.intonating():		# �������ʩ��
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_BUSY )
			return
		if id == self.activateVehicleID:  # �պ��Ǽ����
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISCONJURE )
			return
		if id == self.vehicleDBID:		 # �պ�������裨��Ҫ��Է�����裩
			self.statusMessage( csstatus.FREE_VEHICLE_FORBID_ISUSE )
			return

		self.cell.freeVehicle( id )

	def onFreeVehicle( self, id ):
		"""
		����/��������֪ͨ������� by����
		"""
		self.vehicleDatas.pop( id )

		ECenter.fireEvent( "EVT_ON_PLAYER_FREE_VEHICLE", id )

	def getVehicleLevel( self ):
		"""
		��ȡ��ǰ���ĵȼ�,�ٻ��ߵ���
		"""
		if self.vehicleDBID == 0: return 0
		vehicleData = self.vehicleDatas.get( self.vehicleDBID )
		if vehicleData is None: return 0

		return vehicleData["level"]

	def onVehicleAddSkill( self, skillID ):
		"""
		Define method.
		������¼���
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
		��輼������
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
		��ȡ���ļ����б�
		"""
		vehicleData = self.vehicleDatas.get( dbID, None )
		if vehicleData is None : return []
		return vehicleData["attrSkillBox"]

	def set_rollState( self, oldValue ):
		"""
		��rollʱ�Ƿ�ʰȡ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ROLL_STATE_CHANGE", self.rollState )

	def onTongStorage( self, isShow ):
		"""
		�ڿ��հ��ֿ����ʱ by����
		"""
		ECenter.fireEvent( "EVT_ON_TONG_STORAGE", isShow )

	def set_realLookLevelAmend( self, oldLevel ):
		"""
		���ӵȼ��ı�
		"""
		print "realLookLevelAmend: oldLevel", oldLevel, "nowLevel", self.realLookLevelAmend
		if self.realLookLevelAmend == 0: return
		# ���AOI��Χ��������ң�Ŀǰֻ������Role
		for entity in BigWorld.entities.values():
			if not issubclass( entity.__class__, CombatUnit ): continue
			if entity.effect_state & csdefine.EFFECT_STATE_PROWL == 0: continue
			entity.resetSnake()
			entity.updateVisibility()


	def initStatistic( self ):
		"""
		��ʼ�����顢��Ǯ��Ǳ�ܡ��ﹱΪ0
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
	# �д�
	# --------------------------------------------------
	def onReceivedQieCuo( self, targetID ):
		"""
		�յ��д�����
		"""
		target = BigWorld.entities.get( targetID )
		if target is None: return

		def query( rs_id ):
			if rs_id == RS_OK:
				self.replyQieCuo( targetID, True )
			else:
				self.replyQieCuo( targetID, False )
		# "%s�����������д衣"
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
		�����д�
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
		�����д�����ɹ�
		"""
		target = BigWorld.entities.get( targetID )
		if target is None: return
		self.statusMessage( csstatus.QIECUO_SEND_REQUEST, target.getName() )
		# ����һ�������2D��Ч
		Role.onRequestQieCuo( self, targetID )

	def set_qieCuoTargetID( self, oldTargetID = 0 ):
		"""
		�д�Ŀ��ı�
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_QIECUOID_CHANGED", oldTargetID, self.qieCuoTargetID )

	def trigerImageVerify( self, imageData, count ):
		"""
		Define method.
		����ͼƬ��֤

		@param imageData : ��֤ͼƬ���ݣ�STRING
		@param count : �ڼ�����֤
		"""
		#�����ж��Ƿ��ھ�ͷ����״̬
		if rds.statusMgr.isInSubStatus(Define.GST_IN_WORLD, CameraEventStatus ):
			self.base.requestCancelVerify()
			return
		ECenter.fireEvent("EVT_ON_ANTI_RABOT_VERIFY", base64.b64decode( zlib.decompress( imageData ) ), count )

	# ----------------------------------------------------------------------------------------------------
	# ʹ�÷��������
	# ----------------------------------------------------------------------------------------------------
	def useFengHuangYin( self ):
		"""
		ʹ�÷��������
		"""
		def query( rs_id ):
			if rs_id == RS_YES:
				buffData = self.findBuffByBuffID( "099021" )
				self.requestRemoveBuff( buffData[ "index" ] )
			else:
				ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )
		# �Ƿ�ʹ�÷����ԭ�ظ���?
		showMessage( mbmsgs[ 0x0127 ] ,"", MB_YES_NO, query )

	# ----------------------------------------------------------------------------------------------------
	# ������װ��ģ�����
	# ----------------------------------------------------------------------------------------------------
	def setVehicleCamera( self, nodeName ):
		"""
		������辵ͷ
		"""
		if not self.inWorld: return
		if not nodeName: return
		if self.vehicleModelNum == 0: return

		pos = rds.effectMgr.accessNodePos( self.model, nodeName )

		# �����ȺͿ����������ӽǵĸ߶�Ϊ0.6�ȽϺ���
		y = ( pos - self.position ).y + 0.6
		minDistance = Const.CAMERA_MIN_DISTANCE_TO_VEHICLE
		# �ڸ����������ӽǵĸ߶ȶ�Ϊ2.0
		if nodeName == Const.VEHICLE_STAND_HP:
			y = ( pos - self.position ).y + 2.0
			minDistance = Const.CAMERA_MIN_DISTANCE_TO_STAND_VEHICLE
		# Ҫ��y < 0 ��������Ĭ�ϸ߶ȡ�
		if y <= 0 or y > 8.0: y = 1.8
		pivotPosition = ( 0.0, y, 0.0 )
		rds.worldCamHandler.cameraShell.setEntityTarget( self )
		rds.worldCamHandler.cameraShell.adjustToTarget( False, -0.8, pivotPosition, minDistance, 20 )

	def onUpFlyVehiclePoseOver( self ):
		"""
		�Ϸ�����趯����ɻص�
		"""
		if not self.inWorld: return
		if not self.vehicleModelNum: return	# ���������ﶯ����ɻص�����������
		Role.onUpFlyVehiclePoseOver( self )
		if self.state != csdefine.ENTITY_STATE_PICK_ANIMA: #Ϊ��ʰȡ�����淨����һ����ֵ��޸�
			self.physics.fall = False
		else:
			self.physics.fall = True
			
		UnitSelect().hideMoveGuider()
		self.setModelScale()

	def onDownFlyVehiclePoseOver( self ):
		"""
		�·�����趯��2������ɻص�
		"""
		if not self.inWorld: return
		Role.onDownFlyVehiclePoseOver( self )
		self.clearSourceControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_DOWN_VEHICLE )
		UnitSelect().hideMoveGuider()



	# ----------------------------------------------------------------------------------------------------
	# ��ҷ��д���ģ�����
	# ----------------------------------------------------------------------------------------------------
	def onFlyModelLoad( self, event, modelDict ):
		"""
		��ҷ���ģ�ͼ������
		"""
		if not self.inWorld: return
		Role.onFlyModelLoad( self, event, modelDict )

		functor = Functor( self.onTeleportVehicleCamera, Const.TELEPORT_HP )
		BigWorld.callback( 0.5, functor )

	def onTeleportVehicleCamera( self, nodeName ):
		"""
		"""
		# ��ȡ����ͷƫ�Ƹ߶�
		model = self.model
		if model is None: return
		# ��ȡ����ͷ
		camera = BigWorld.camera()
		camera.pivotPosition = ( 0.0, 4.0, 0.0 )
		rds.worldCamHandler.cameraShell.maxDistance = 20.0
		rds.worldCamHandler.cameraShell.setDistance( 16.0, True )

	def onTeleportVehicleModeEnd( self ):
		"""
		���贫��ģʽ����
		"""
		Role.onTeleportVehicleModeEnd( self )
		self.resetCamera()

	def resetCamera( self ):
		"""
		��������ͷλ��
		"""
		if self.vehicleModelNum:	# �������
			functor = Functor( self.setVehicleCamera, self.vehicleHP )
			BigWorld.callback( 0.1, functor )	# �ӳ�������辵ͷ
		else:
			pivotPosition = Const.CAMERA_PROVITE_OFFSET_TO_ROLE[ self.getClass() ]
			rds.worldCamHandler.cameraShell.setEntityTarget( self )
			rds.worldCamHandler.cameraShell.adjustToTarget( True, -0.8, pivotPosition, 1.0, 20 )

	def onShowExp2PotWindow( self, objectID ):
		"""
		��ʾ���黻Ǳ�ܽ���
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_SHOW_Exp2PotWindow" )

	# ----------------------------------------------------------------------------------------------------
	# ��ұ���ģ�����
	# ----------------------------------------------------------------------------------------------------
	def set_currentModelNumber( self, old = '' ):
		"""
		ģ�ͱ�ŷ����ı�
		����̫�ң��ĵ�̫���ᡣ
		"""
		Role.set_currentModelNumber( self, old )
		if self.currentModelNumber == "fishing":
			# ����ǵ���Ļ���Ҫ��������Ľ���
			GUIFacade.onFishingBegin( self, csstatus.SKILL_PLAYER_STOP_FISHING )
		if self.currentModelNumber == "":
			GUIFacade.onFishingEnd( self )
		self.resetWeaponType()

	def onAFLimitTimeChanged( self, af_time_limit ):
		"""
		define method
		�뿪�Զ�ս��״̬�ص�
		"""
		self.af_time_limit = af_time_limit

	def onAFLimitTimeExtraChanged( self, af_time_extra ):
		"""
		define method
		�뿪�Զ�ս��ʱ��ص�2
		"""
		self.af_time_extra = af_time_extra
		if self.af_time_extra > 0:
			ECenter.fireEvent( "EVT_ON_AUTO_FIGHT_TIMER_SHOW_ONLY", self.af_time_extra )

	def resetAutoFight( self ):
		"""
		���������Զ�ս������
		"""
		if self.hasAutoFight: return
		if self.level >= Const.SHOW_AUTOBAR_LEVEL_LIMITED:
			self.cell.openAutoFight()	# �����Զ�ս������

	def pickFruit( self, targetID ):
		"""
		�ɼ�����
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
			@des:	true,����ˮ��;false,�߳�ˮ��
		volume:
			@type:  ˮ����
			@des:	ˮ���ʶ����ͬ��ˮ��Ч����һ����
		"""

		if volume and volume.id == "":	#����û�б�ŵ�ˮ��ֱ�Ӻ���
			return
		if not volume:
			self.onLeaveWaterCallback( "" )
			return
		if getattr( self, "curWaterVolumeID", "" ) == "":
			self.curWaterVolumeID = ""
		#�����߼���Ҫ�Ǳ��������������ͬ���õ�ˮ����������ȥ������BUFF���ٵ����Ӽ��١�
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
		if volumeID == "":					#�뿪û�б�ŵ�ˮ���ǲ��ܺ��Եġ�����Ҫ�Ǵ��͵�ʱ�򣬴�һ���б�ŵ�ˮ�뿪��Ҳ�ᴫû�б�ŵĲ���������
			self.cell.onLeaveWater( "" )
			self.lastWaterVolumeID = ""
			self.curWaterVolumeID = ""
		if self.lastWaterVolumeID != self.curWaterVolumeID:
			self.cell.onLeaveWater( volumeID )
			self.lastWaterVolumeID = ""
			self.curWaterVolumeID = ""

	# --------------------------------------------------
	# ����ͷ����
	# --------------------------------------------------
	def onCameraFly( self, eventID ):
		"""
		Define Method
		����ͷ����
		"""
		self.startFly( eventID )

	def startFly( self, eventID ):
		"""
		��ʼ����
		"""
		rds.cameraEventMgr.trigger( eventID )

	def onCameraFlyNodeText( self, text ):
		"""
		��ʾ����
		"""
		if type( text ) != str: return
		ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS2", text )

	def changFashionNum( self ):
		"""
		�л�ʱװ��װ��
		"""
		if self.vehicleModel: return	# �Ϸ��������·����������в��ܻ�װ
		self.cell.changFashionNum()

	def set_fashionNum( self, oldValue ):
		"""
		��ɫʱװ�л�
		"""
		Role.set_fashionNum( self, oldValue )
		ECenter.fireEvent( "EVT_ON_ROLE_CHANGE_FASHIONNUM", self.fashionNum )
		ECenter.fireEvent( "EVT_ON_ROLE_MODEL_CHANGED" )

	def onAddRoleHP( self, entityID, addHp ):
		"""
		define method
		ĳ��role����Ѫ����ص� Ŀǰ��Ҫ����Ѫ�ָ����� by ����
		"""
		entity = BigWorld.entities.get( entityID )
		if entity is None:
			return
		GUIFacade.onRoleHPChanged( entity.HP - addHp, entityID, entity.HP, entity.HP_Max )

	# ------------------------------һ����װ by ����--------------------------------
	def onGetSuitDatas( self, oksData ):
		"""
		define method
		���һ����װ����
		@param oksData : PY_DICT
		"""
		self.oksData = oksData
		ECenter.fireEvent( "EVT_ON_INIT_SUIT_DATAS", self.oksIndex, oksData )

	def saveSuit( self, suitIndex, suitName ):
		"""
		������װ����
		"""
		suitEquips = [ 0, ] * 13		# ����UID�б�13����Ҫ����Ĳ�λ����
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
		��������װ
		"""
		if suitIndex not in self.oksData:
			return
		self.base.renameSuit( suitIndex, suitName )
		self.oksData[suitIndex]["suitName"] = suitName

	def switchSuit( self, suitIndex ):
		"""
		������װ
		"""
		# αCD���
		endTime = self.getCooldown( Const.ONE_KEY_SUIT_CD_ID )[3]
		if endTime > Time.Time.time():
			self.statusMessage( csstatus.OKS_COOL_DOWN )
			return
		self.base.onSwitchSuit( suitIndex )

	def onSwitchSuit( self, suitIndex ):
		"""
		define method
		������װ�ص�
		"""
		# װ������
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
		# ����αCD
		cdt = Const.ONE_KEY_SUIT_CD_TIME
		startTime = Time.Time.time()
		endTime = startTime + cdt
		self._attrCooldowns[Const.ONE_KEY_SUIT_CD_ID] = ( cdt, cdt, startTime, endTime )
		self.oksIndex = suitIndex
	# ------------------------------һ����װ--------------------------------

	# --------------------------------------------------
	# ��������
	# --------------------------------------------------
	def switchFlyWater( self, switch ):
		"""
		�������࿪��
		"""
		Role.switchFlyWater( self, switch )
		if self.physics is None: return

		if switch:
			callback = self.floatOnWaterCallback
		else:
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
		����ˮ��ص�
		"""
		if self.isSprint: return
		if self.onWaterArea == switch: return
		self.onWaterArea = switch
		self.cell.switchWater( switch )
		if switch:
			jumpHeight = Const.JUMP_WATER_HEIGHT
			geneGravity = Const.JUMP_WATER_GENEGRAVITY
			if self.isActionState( Action.ASTATE_NAVIGATE ):		# �Զ�Ѱ·����ˮ����Ծ�ص�
				self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )
		else:
			jumpHeight = Const.JUMP_LAND_HEIGHT
			geneGravity = Const.JUMP_GENEGRAVITY
			if self.onWaterJumpTimer is not None:	# ֹͣˮ����Ծ�ص�
				BigWorld.cancelCallback( self.onWaterJumpTimer )
				self.onWaterJumpTimer = None
			self.antoRunConjureVehicle()	# �Զ���˹���
		self.jumpHeight1 = jumpHeight
		self.geneGravity = geneGravity

	def onWaterJumpBegin( self ):
		"""
		ˮ����Ծ
		"""
		if not self.inWorld: return
		if self.isJumping(): return
		# �߻�Ҫ�������������Զ�Ѱ·������ˮ�漸����Ծ
		if self.vehicleModelNum: return
		pro = random.random()
		if pro <= Const.WATER_JUMP_PRO: # ͨ������������
			self.jumpBegin()
		else: 							# ��ͨ�����������»ص�
			self.onWaterJumpTimer = BigWorld.callback( Const.WATER_JUMP_TIME, self.onWaterJumpBegin )

	def startFlyWaterParticle( self ):
		"""
		��ʼˮ������Ч��
		"""
		if not self.onWater: return
		Role.startFlyWaterParticle( self )


	def onControlled( self, isControlled ):
		"""
		This callback method lets an entity know whether it is now being controlled locally by player physics,
		instead of the server. It happens in response to a call to BigWorld.controlEntity
		"""
		# ����һ����ʱ���롣 ��Ϊbigworld��bug���������ڽ��͵�ʹ��onPoseVolatile
		# ������Ҫʹ�� controled�ӿھ�������
		# ���Է��֣����ƺͷǿ���״̬�£��ͻ��˵�yaw���Իᷢ���ı䣬������������
		# ����״̬�£���ɫ�ͻ��˵�yawֵ��0.013046607375144958���ǿ���״̬����
		# 0.024543693289160728�����������˵�һֱ����0.024543693289160728
		DEBUG_MSG( "controlled---->>>", isControlled )

		if isControlled:
			try:
				self.resetPhysics()
			except:
				ERROR_MSG( "Reset physics failed!" )

		ECenter.fireEvent( "EVT_ON_ROLE_CONTROLL_STATE_CHANGE", isControlled )

	def getName( self ):
		"""
		@rType : string����ɫ����
		"""
		return self.playerName

	def jumpToPoint( self, pos, jumpTime, jumpType ):
		"""
		��Ծ��ĳ��
		@param pos			:	��Ծ���������
		@type pos			:	Vector3
		@param jumpTime		:	��Ծ����ߵ��ʱ��
		@type jumpTime		:	Float
		@param jumpType		:	��Ծ����,ͨ�����������Ĳ���
		@type jumpType		:	Defined in csdefine.py
		return None
		"""
		#���������п��������ƶ������Խ�ֹ���̰���
		self.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK  )
		self.moveToDirectly( pos, self.__onMoveToDirectlyOver )
		self.jumpType = jumpType
		jumpV0 = self.physics.gravity * jumpTime
		self.physics.doJump( jumpV0, 0 )
		BigWorld.callback( jumpTime*2, self.__onjumpToPointOver )

	def __onjumpToPointOver( self ):
		"""
		������������
		"""
		self.jumpType = csdefine.JUMP_TYPE_LAND
		self.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK )


	#��ͷ����Ծ
	def simulateJumpToPoint( self, pos, jumpTime, jumpSecondTime, cb=None ):
		"""
		��Ծ��ĳ��
		@param pos			:	��Ծ���������
		@type pos			:	Vector3
		@param jumpTime		:	��ʼ��Ծ��ʱ��
		@type jumpTime		:	Float
		@param jumpSecondTime	:	�ڶ�����Ծ��ʱ��
		@type jumpTime		:	Float
		return None
		"""
		#���������п��������ƶ������Խ�ֹ���̰���
		self.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK  )
		self.moveToDirectly( pos, self.__onMoveToDirectlyOver )
		time = ( self.position - pos ).length / self.move_speed
		if jumpTime > 0.0:
			if jumpSecondTime < 0.01: #��ʾû�ж�����
				h = pos[1] - self.position[1] 
				if h > 0.5: #��ʾҪ������Ծ
					dTime = ( time - jumpTime ) / 2.0 - math.sqrt( 2 * h / self.physics.gravity ) / 2.0
					lastTime = time - jumpTime - dTime
				elif h < -1.0:#��ʾҪ������Ծ
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
		������������
		"""
		self.jumpType = csdefine.JUMP_TYPE_LAND
		self.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_JUMP_ATTACK )
		if callable( cb ):
			cb()
	
	
	# ------------------------------------------------------------------------------
	# ģ��ͻ����ƶ����֣�����ѣ��״̬�µ�����ƶ���
	# ------------------------------------------------------------------------------
	def outputCallback( self, moveDir, needTime, dTime ):
		"""
		filter��λ��ˢ�»ص�����
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
		�ƶ�����
		"""
		self.moveTime = 0.0
		if hasattr(self.filter,"outputCallback"):
			self.filter.outputCallback = None
		# ͬ���������������ݣ���үֻ���������ˡ�
		self.filter = BigWorld.PlayerAvatarFilter()
		self.filter = BigWorld.AvatarDropFilter()
		self.filter = BigWorld.PlayerAvatarFilter()

	def lineToPoint( self, position, speed ):
		"""
		�ƶ��������
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
		ʵʱ�������Ӵ�������
		"""
		return Define.TYPE_PARTICLE_PLAYER

	def addBlurEffect( self ):
		"""
		���Ӷ�̬ģ��Ч��
		"""
		BigWorld.setGraphicsSetting("RADIO_BLUR", 1)

	def delBlurEffect( self, ):
		"""
		ɾ����̬ģ��Ч��
		"""
		flag = False
		if hasattr( self, "isSprint" ) and self.isSprint: #�Ƿ��ڳ��
			flag = True
		buffData = self.findBuffByBuffID(  Const.JUMP_FAST_BUFF_ID )
		if buffData : #Ѹ���ƶ�buff����
			flag = True
		if not flag:
			BigWorld.setGraphicsSetting("RADIO_BLUR", 0)

	def updateComboCount( self, comboCount ):
		"""
		combo����
		"""
		ECenter.fireEvent( "EVT_ON_HOMING_SPELL_COMBO", comboCount )

	def set_daoheng( self, oldValue ):
		"""
		����ֵ
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DAOHENG_CHANGE", self.daoheng )

	def flashTeamSign( self ):
		"""
		ˢ�¶�����
		"""
		isCurrShow = rds.viewInfoMgr.getSetting( "player", "sign" )
		self.teamSignSettingChanged( isCurrShow )

	def teamSignSettingChanged( self, value ):
		"""
		�������û��������
		"""
		if self.isInTeam():
			if self.isCaptain():
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "captain", value )
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", False )
			else:
				ECenter.fireEvent( "EVT_ON_ROLE_SIGN_CHANGED", self, "teammate", value )


	def set_qieCuoState( self, oldValue = 0 ):
		"""
		�д�״̬�ı�
		"""
		if self.qieCuoState == csdefine.QIECUO_READY:
			ECenter.fireEvent( "EVT_END_GOSSIP" ) # �ر����д���

	#���ظ������
	def baoZangBroadCastEnemyPos( self, enemyId, pos ):
		"""
		����ѷ����Ҹ�������λ����Ϣ
		"""
		self.base.baoZangBroadCastEnemyPos( enemyId, pos )

	def baoZangBroadCastDisposeEnemy( self, enemyId ):
		"""
		�����ܳ��ҵ�AOI��֪ͨ����
		"""
		self.base.baoZangBroadCastDisposeEnemy( enemyId )

	def onShowAccumPoint( self, id, ap ):
		"""
		��ʾ����
		id : Ŀ�����
		ap ������
		"""
		#���Ź�Ч
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
		PK�б����ı�
		"""
		self.pkTargetList = pkTargetList
		ECenter.fireEvent( "EVT_ON_ENTITY_PK_CHANGED", id )

	def onUpdateIntensifyItem( self, uid ):
		"""
		define method
		ǿ����Ʒ�����ı�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_UPDATE_INTENSIFY_ITEM", uid )

	def onOpenSpaceTowerInterface( self ):
		"""
		define method
		�����Ȫm؅����������
		"""
		ECenter.fireEvent( "EVT_ON_OPEN_SPACE_TOWER_INTERFACE" )

	def onCloseSpaceTowerInterface( self ):
		"""
		define method
		�ر����Ȫm؅����������
		"""
		ECenter.fireEvent( "EVT_ON_CLOSE_SPACE_TOWER_INTERFACE" )

	def showHeadPortraitAndText( self, type, monsterName, headTextureID, text, lastTime ):
		"""
		define method
		��ʾͷ�������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_HEAD_PORTRAIT_AND_TEXT", type, monsterName, headTextureID, text, lastTime )

	def cameraFollowActionStart( self ):
		"""
		����ڲ��Ŷ��������������Y�����
		"""
		self.cameraFollowActionOver()	# ������һ��
		model = self.getModel()
		ma = Math.Matrix( model.node("HP_head") )
		dis = ma.applyToOrigin()[1] - self.position[1]
		self.cameraInHomingID = BigWorld.callback( 0.1, Functor(self.setCameraTarget, dis, 0.0 ) )

	def setCameraTarget( self, dis, disY ):
		"""
		���������target
		"""
		cc= BigWorld.camera()
		model = self.getModel()
		ma = Math.Matrix( model.node("HP_head") )
		dis1 = ma.applyToOrigin()[1] - self.position[1]

		ma1 = Math.Matrix( self.matrix )
		if dis1 - dis > Const.CAMERA_FOLLOW_Y_DIS_1: #����
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
		���������ص���������������
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
		@param	fileName:	��Ƶ�ļ�·��
		@type	fileName��	string
		@param	typeID:	        ���� 2D/3D
		@type	fileName��	UINT
		@param	NPCID:	        NPC��id
		@type	fileName��	UINT
		@param	priority:	        �������ȼ�
		@type	priority��	UINT
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
			if self.soundPriority <= priority:						#��Ҫ���ŵ��������ȼ��ߣ����ϵ�ǰ����������ֻ�е�ǰ���������꣬�ſ��Բ���
				self.soundPriority = priority
				sound = None
				try:
					sound = BigWorld.getSound( fileName )
				except:
					return
				if gossipSound and sound:
					gossipSound.stop()								#ֹͣ��ǰ����
				rds.soundMgr.play2DSound( fileName, True )
			else:
				if gossipSound:
					state = gossipSound.state
					if state == "ready playing":						#��ǰ�����Ѳ�����
						rds.soundMgr.play2DSound( fileName, True )
				else:
					rds.soundMgr.play2DSound( fileName, True )

	def playSoundFromGender( self, fileName, id, flag ):
		"""
		Define method
		����ְҵ�Ĳ�ͬ������ҵĿͻ��˲��Ų�ͬ·������Ч
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
		ģ����Ծ
		"""
		if self.getPhysics():
			BigWorld.dcursor().yaw = yaw
			jumpV = math.sqrt( height * 2 * self.physics.gravity )
			self.physics.doJump( jumpV,0.0 )
			t0 = math.sqrt( height * 2 / self.physics.gravity ) #����ߵ�����ʱ��
			t1 = math.sqrt( height0 * 2 / self.physics.gravity )
			V0 = dis / ( t0 + t1 )
			if V0 > self.move_speed:
				V0 = self.move_speed
			self.physics.velocity = ( 0, 0, V0 )

	def stopSimulateJump( self ):
		"""
		ֹͣģ����Ծ
		"""
		if self.getPhysics():
			self.getPhysics().stop()

	def enterTowerDefenceSpace( self ):
		"""
		define method
		�������������ĸ���
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_TOWER_DEFENCE_SPACE", Const.TOWER_DEFENCE_SKILLNUM )


	def addTowerDefenseSpaceSkill( self, skillID, spaceType ):
		"""
		define method
		�������������ĸ�������
		"""
		ECenter.fireEvent( "EVT_ON_ADD_TOWER_DEFENCE_SPACE_SKILL", skillID, spaceType )

	def endTowerDefenseSpaceSkill( self ):
		"""
		define method
		��������������������
		"""
		ECenter.fireEvent( "EVT_ON_END_TOWER_DEFENCE_SPACE_SKILL" )

	def showRankList( self, msg ):
		"""
		����Ĺboss����ɱ֮���֪ͨ�����ʾ���а�
		param msg = [playerDamageInfos,tongDamageInfos, playerNameTotongName]
		playerDamageInfos = [ [playerName ,damages]}, ]
		tongDamageInfos = [ [tongName,damages], ]
		playerNameTotongName = {playerName: tongName}
		"""
		INFO_MSG( "liu wang mu ranklist %s" %msg )
		ECenter.fireEvent( "EVT_ON_LIU_WANG_MU_SHOW_RANKLIST", msg)

	def onPlayMonsterSound( self, soundType, soundEvent ):
		"""
		���ﲥ�����򳡾���Ч
		"""
		if not soundType:
			rds.soundMgr.switchMusic( soundEvent )
		else:
			rds.soundMgr.playVocality( soundEvent, self.getModel() )

	def onStopMonsterSound( self ):
		"""
		����ֹͣ���򳡾���Ч,���ŵ�ͼ��Ч
		"""
		currArea = self.getCurrArea()
		rds.soundMgr.switchMusic( currArea.getMusic() )



#------------------------------------------------------------------------------------------
#����ʱ��
#------------------------------------------------------------------------------------------
	def finishSkillPlayAction(self):
		DEBUG_MSG("finishSkillPlayAction find NPC %s"%self.entitiesInRange(csconst.ROLE_AOI_RADIUS))
		entity = self.entitiesInRange(csconst.ROLE_AOI_RADIUS)[1]#������ֻ��NPC������Լ�,�������ĵ�һ������ң��ڶ�����NPC
		#entity.speakResult()
		entity.cell.nextRound()

	def setDanceChallengeIndex(self, challengeIndex):
		"""
		challengeIndex �����������Σ�ע������������Ǵ�1��ʼ����19����
		"""
		self.cell.setDanceChallengeIndex(challengeIndex)
		self.cell.setRoleModelInfo(self.getModelInfoDict())




	def gotoDanceSpace(self, challengeIndex):
		"""
		������ҵ���ͻ��˽��水ť����ϰ�������ս���裩��ͳһ�ĵ��ýӿڣ�������������
		challengeIndex �����������Σ�ע������������Ǵ�1��ʼ����19����,0��ʾΪ��ϰ����
		"""
		if challengeIndex:#��ս����
			self.base.noticeDanceMgrIsChallenged(challengeIndex)
			#self.cell.teleportToDanceChallengeSpace(challengeIndex)
		else:
			self.cell.teleportToDancePracticeSpace(challengeIndex)
		self.setDanceChallengeIndex(challengeIndex)

	def canChallengeDanceKing(self, challengeIndex):
		#�ͻ��˲����Ƿ������ս����
		self.base.canChallengeDanceKing(challengeIndex)


	def canChallengeDanceKingCb(self, index, result):
		#1��ʾ������ս
		#2��ʾ���ڱ���ʱ��
		#3��ʾ��������ս
		#4��ʾ��ս�Լ�
		#5��ʾ��ս�͵ȼ��������Լ�Ҳ������
		#6��ʾ��ǰλ��û���������Լ�����ֱ�ӳ�Ϊ����
		#7��ʾ�л��۵ľ���δ��ȡ����Ҫ��ȡ������ܻ��λ��
		#8��ʾδ��ȡλ��
		if result == csdefine.DANCE_IN_PROTECT_TIME:
			self.statusMessage(csstatus.JING_WU_SHI_KE_DANCEKING_IN_PROTECTTIME)
		elif result == csdefine.DANCE_IS_CHALLENGED:
			self.statusMessage(csstatus.JING_WU_SHI_KE_DANCEKING_IS_CHALLENGED)
		elif result == csdefine.DANCE_CHALLENGE_MYSELF:
			self.statusMessage(csstatus.JING_WU_SHI_KE_DANCEKING_CHALLENGE_MYSELF)
		#elif result == csdefine.DANCE_CHALLENGE_LOWER_LEVEL_DANCER:  #������Ĵ����²��д�����
			#self.statusMessage(csstatus.JING_WU_SHI_KE_CHALLENGE_LOWER)
		elif result == csdefine.DANCEK_NOT_GET_POSITION:
			self.statusMessage(csstatus.JING_WU_SHI_KE_NOT_GET_POSITION)
		self.canChallengeDanceKing = result
		#������������ս��ť����
		ECenter.fireEvent("WU_WANG_BANG_CHALLENGE_BUTTON", index, result)


	def addDancingKingInfo(self, index, dancingKingInfo):
		#Define method
		#���շ��������͵�������Ϣ���ڽ�������ʱ���ɷ���������
		#dancingKingInfo = {"modelInfo":playerModelInfo ,"Time":time.time(),"isChallenge":0 , "dbid":0}
		ECenter.fireEvent("UPDATE_WU_WANG_BANG", index, dancingKingInfo)

	def sendDancingKingInfosOver(self):
		#define method
		DEBUG_MSG("ROLE_SEND_DANCING_KING_INFOS_OVER" )		# ����������������Ϣ����

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
		challengeIndex �����������Σ�ע������������Ǵ�1��ʼ����20����
		"""
		#pass

	def cancelParctice(self):
		#������ϰ���踱����npc��֪ͨ������ϰ
		for entity in self.entitiesInRange(35):
			if entity.__class__.__name__ ==  "DanceNPC":
				entity.cell.cancelParctice()

	def canGetDancePosition(self, index):
		#��⵱ǰλ���Ƿ�����
		self.cell.canGetDancePosition(index)

	def canGetDancePositionCb(self, index):
		#define method
		self.cell.addWuTingBuff(index, self.getModelInfoDict())

	def queryRoleEquip( self, queryName ):
		"""
		��ѯ���װ��
		"""
		self.base.queryRoleEquipItems( queryName )

	def onQueryRoleEquip( self, roleName, raceclass, roleLeve, tongName, roleModel, equips ):
		"""
		define method.
		��ѯ���װ������
		"""
		espialRemotely.onQueryRoleEquip( roleName, raceclass, roleLeve, tongName, roleModel, equips )

	def resetPatrol( self ):
		"""
		������ʾ�ڵ�·��
		"""
		if self.patrolPath and self.patrolModel:
			self.onShowPatrol( self.patrolPath, self.patrolModel )

	def onShowPatrol( self, path, model ):
		"""
		define method
		��ʾ�ڵ�Ѱ··��
		"""
		patrolMgr.showPatrol( path,model )
		self.cell.setPartrol( path, model )

	def onArrivePatrol( self ):
		"""
		����ڵ�·��������
		"""
		self.cell.setPartrol( "", "" )

	def setModel( self, model, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		���������һ��ģ��
		"""
		Role.setModel( self, model, event )
		#����Ų���
		self.boundFootSound()

	def boundFootSound( self ):
		"""
		����ƶ�ʱ�ĽŲ���
		"""
		if self.model is None: return  #�˴���self.model������self.getModel()����Ϊ��ҿ�������½��������
		try:
			lfoot = self.model.node( Const.FOOT_TRIGGER_LEFT_NODE )
			rfoot = self.model.node( Const.FOOT_TRIGGER_RIGHT_NODE )
		except: #���������ҽŰ󶨵��return
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
	���ͻ��������Ƿ���ȷ
	"""
	try:
		if not PackChecker.checkCurrentSpaceData():
				ERROR_MSG( "��Ϸ��Դ�����𻵣������°�װ��Ϸ�ͻ��ˡ�" )
				# "��Ϸ��Դ�����𻵣������°�װ��Ϸ�ͻ���"
				showAutoHideMessage( 15.0, 0x0126, "", MB_OK, lambda x: gbref.rds.gameMgr.quitGame( False ) )
				return
	except ValueError, errstr:
		ERROR_MSG( errstr )
		BigWorld.callback( 1.0, checkCurrentSpaceData )




# Role.py
