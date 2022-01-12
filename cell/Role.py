# -*- coding: gb18030 -*-
#
# $Id: Role.py,v 1.336 2008-09-05 09:28:32 yangkai Exp $


"""
This module implements the Role entity.
"""

# python
import time
import cschannel_msgs
import ShareTexts as ST
import math
import random
import time
# engine
import BigWorld
import Math
import copy

# common global
import Language
import csdefine
import csconst
import csstatus
import ChatObjParser
import ItemTypeEnum
import cPickle
import csstatus_msgs as StatusMsgs

from bwdebug import *
from Message_logger import *
from LevelEXP import RoleLevelEXP as RLevelEXP
from Resource import QuestsTrigger
from ItemSystemExp import EquipQualityExp
from PetFormulas import formulas
from interface.PresentChargeUnite import PresentChargeUnite

# cell
import Const
import ECBExtend
import wizCommand
from Love3 import *
from interface.CombatUnit import CombatUnit
import items
g_items = items.instance()
import Resource.AIData
import sys
from Resource.SkillLoader import g_skills
import SkillTargetObjImpl
from items.CueItemsLoader import CueItemsLoader
from items.CueItemsLoader import specialMsgMap
g_cueItem = CueItemsLoader.instance()

# base class
from interface.GameObject import GameObject
from interface.RoleEnmity import RoleEnmity
from interface.ItemsBag import ItemsBag
from interface.RoleChangeBody import RoleChangeBody
from interface.Team import Team
from interface.RoleDialogForward import RoleDialogForward
from interface.RoleQuestInterface import RoleQuestInterface
from interface.RoleMagicChangeInterface import RoleMagicChangeInterface
from interface.RoleCommissionSale import RoleCommissionSale
from interface.Bank import Bank
from interface.RoleMail import RoleMail
from interface.RoleRelation import RoleRelation
from interface.RoleCredit import RoleCredit
from interface.RoleGem import RoleGem
from interface.RoleSpecialShop import RoleSpecialShop
from ObjectScripts.GameObjectFactory import g_objFactory
from interface.HorseRacer import HorseRacer
from interface.LotteryItem import LotteryItem
from interface.AntiWallow import AntiWallow
from interface.AmbulantObject import AmbulantObject
from interface.RoleQuizGame import RoleQuizGame
from interface.LivingSystem import LivingSystem
from interface.YuanBaoTradeInterface import YuanBaoTradeInterface
from interface.ItemBagSpecialInterface import ItemBagSpecialInterface
from interface.RoleEidolonHandler import RoleEidolonHandler
from interface.RoleChallengeSpaceInterface import RoleChallengeSpaceInterface
from interface.RoleChallengeInterface import RoleChallengeInterface
from interface.RoleUpgradeSkillInterface import RoleUpgradeSkillInterface
from interface.SpaceViewerInterface import SpaceViewerInterface
from interface.RoleStarMapInterface import RoleStarMapInterface
from interface.CopyMatcherInterface import CopyMatcherInterface
from interface.RoleCampInterface import RoleCampInterface
from interface.ScrollCompose import ScrollCompose
# hyw
from interface.RoleChat import RoleChat
from interface.SpaceFace import SpaceFace
from interface.PetCage import PetCage
from interface.PostInterface import PostInterface
from interface.SkillBox import SkillBox
from interface.TongInterface import TongInterface

from interface.BaoZangCopyInterface import BaoZangCopyInterface
from interface.RoleShuijingSpaceInterface import RoleShuijingSpaceInterface
from interface.RoleYeZhanFengQiInterface import RoleYeZhanFengQiInterface
from interface.ZhengDaoInterface import ZhengDaoInterface
from interface.RoleDestinyTransInterface import RoleDestinyTransInterface
from interface.Fisher import Fisher
from interface.TDBattleInterface import TDBattleInterface
from interface.RoleYiJieZhanChangInterface import RoleYiJieZhanChangInterface
from interface.RoleJueDiFanJiInterface import RoleJueDiFanJiInterface
from interface.RoleCopyInterface import RoleCopyInterface

from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader	# NPC的任务掉落物品配置表
g_npcQuestDroppedItems = NPCQuestDroppedItemLoader.instance()
g_aiDatas = Resource.AIData.aiData_instance()

from Resource.Rewards.RewardManager import g_rewardMgr

from KuaiLeJinDan import KuaiLeJinDan
g_KuaiLeJinDan = KuaiLeJinDan.instance()

from Resource.SuanGuaZhanBuLoader import SuanGuaZhanBuLoader
g_SuanGuaZhanBuLoader = SuanGuaZhanBuLoader.instance()

from ActivityRecordMgr import g_activityRecordMgr
from Love3 import g_levelResItems

from Function import newUID

from MsgLogger import g_logger

from LoveMsg import LoveMsg
from config.item.FruitItems import Datas as FruitItemsDatas
from config.server.WaterBuffConfig import Datas as WaterBuffDatas
from config.VehicleUpStep import Datas as U_DATA

from config.item.EquipUpNeedItem import Datas as jadeData
from config.item.EquipAttrRebuildItem import Datas as pearlData
from config.item.BaseQualityRateProb import Datas as BaseQualityRateProb
from config.RoleVendConfig import Datas as roleVendData
from items.CItemBase import CItemBase
import ChatObjParser
import VehicleHelper
import CombatUnitConfig
from Domain_Fight import g_fightMgr
from OnlineRewardMgr import OnlineRewardMgr


g_onlineReward = OnlineRewardMgr.instance()


"""
① 为了清晰起见，请在 import 的时侯，有意识地按上面归一下类( 每组中 import 在前，from import 在后 )
② 不要 import *
③ 对于 AA.BB ( BB 为 class ) 使用 from AA import BB
－－adviced by hyw
"""

# ------------------------------------------------------------------------------
# Section: class Role
# ------------------------------------------------------------------------------
class Role(
	GameObject,						# top layer of entity
	RoleEnmity, 					#
	ItemsBag, 						# 背包( phw )
	RoleChangeBody,                             #变身系统
	Team,	 						# 组队( pgk )
	RoleDialogForward,				# 对话( phw )
	RoleQuestInterface,				# 任务( kb )
	RoleChat, 						# 消息( phw )
	SpaceFace,						# 空间管理( pgk )
	PostInterface,					# 邮件系统( pgk )
	PetCage, 						# 宠物圈( hyw )
	SkillBox,						# 技能( phw )
	RoleCommissionSale,				# 寄卖系统( wsf )
	Bank,							# 钱庄( wsf )
	RoleMail,						# 邮件系统 (zyx)
	RoleRelation,					# 玩家关系( wsf )
	TongInterface,					# 帮会系统(kebiao)
	RoleCredit,						# 处理玩家信誉( wsf )
	RoleGem,						# 玩家经验石系统( wsf )
	RoleSpecialShop,				# 玩家道具商城( wsf )
	HorseRacer,						# 赛马(zyx)
	LotteryItem,					# 锦囊(hd)
	AntiWallow,					# 防沉迷系统( spf )
	AmbulantObject,					# 移动相关 ( kebiao )1
	RoleQuizGame,					# 知识问答( wsf )
	PresentChargeUnite,				# 奖品和充值领取模块( hd )
	LivingSystem,					# 生活系统模块 ( jy )
	YuanBaoTradeInterface,			# 元宝交易( jy )
	ItemBagSpecialInterface,			# 背包相关特殊功能接口（jy）
	RoleEidolonHandler,				# 玩家小精灵接口
	RoleMagicChangeInterface,		# 变身接口
	RoleChallengeSpaceInterface,	# 挑战副本对话界面接口
	RoleChallengeInterface,			# 竞技接口
	RoleUpgradeSkillInterface,		# 角色技能升级接口
	SpaceViewerInterface,			# 副本观察者模式接口
	RoleStarMapInterface,			# 星际地图接口
	CopyMatcherInterface,			# 副本组队系统方法接口
	RoleCampInterface,				# 阵营接口
	BaoZangCopyInterface,			# 宝藏副本接口
	ScrollCompose,					# 制作卷配方接口
	RoleShuijingSpaceInterface,		#水晶副本接口
	RoleYeZhanFengQiInterface,   # 夜战凤栖战场
	ZhengDaoInterface,				# 证道系统接口
	RoleDestinyTransInterface,		# 天命轮回副本接口
	Fisher,							# 捕鱼达人
	TDBattleInterface,				# 仙魔轮战
	RoleYiJieZhanChangInterface,		# 异界战场
	RoleJueDiFanJiInterface,		# 绝地反击接口
	RoleCopyInterface,				#副本接口
	):

	"An Role entity."

	def __init__( self ):
		# 这里可能还不可以直接调用self.getName()方法
		INFO_MSG( "player %s(%i) init..." % ( self.playerName, self.id ) )

		# 基本模块
		GameObject.__init__( self )
		Team.__init__( self )
		RoleChat.__init__( self )
		AmbulantObject.__init__( self ) #角色在骑宠传送过程中需要移动

		# 基本模块2
		ItemsBag.__init__( self )		# 装备效果
		Bank.__init__( self )

		# 扩展模块
		RoleEnmity.__init__( self )
		RoleQuestInterface.__init__( self )
		SkillBox.__init__( self )
		SpaceFace.__init__( self )
		PostInterface.__init__( self )
		PetCage.__init__( self )
		RoleCommissionSale.__init__( self )
		RoleMail.__init__(self)
		RoleRelation.__init__( self )
		TongInterface.__init__( self )
		RoleCredit.__init__( self )
		RoleGem.__init__( self )
		RoleSpecialShop.__init__( self )
		HorseRacer.__init__( self )
		LotteryItem.__init__( self )
		AntiWallow.__init__( self )
		RoleQuizGame.__init__( self )
		PresentChargeUnite.__init__( self )
		LivingSystem.__init__( self )
		ItemBagSpecialInterface.__init__( self )
		RoleEidolonHandler.__init__( self )
		RoleMagicChangeInterface.__init__( self )
		RoleChallengeSpaceInterface.__init__( self )
		RoleShuijingSpaceInterface.__init__( self )
		RoleChallengeInterface.__init__( self )
		RoleUpgradeSkillInterface.__init__( self )
		SpaceViewerInterface.__init__( self )
		RoleStarMapInterface.__init__( self )
		CopyMatcherInterface.__init__( self )
		RoleCampInterface.__init__( self )
		BaoZangCopyInterface.__init__( self )
		RoleYeZhanFengQiInterface.__init__( self )
		ScrollCompose.__init__( self )
		ZhengDaoInterface.__init__( self )
		RoleDestinyTransInterface.__init__( self )
		Fisher.__init__( self )
		TDBattleInterface.__init__( self )
		RoleYiJieZhanChangInterface.__init__( self )
		RoleJueDiFanJiInterface.__init__( self )
		RoleCopyInterface.__init__( self )

		# entity 类型定义
		self.setEntityType( csdefine.ENTITY_TYPE_ROLE )
		# 重新计算属性值，此属性必须在其它涉及到属性的模块之前初始化
		#角色基础属性初始化
		self.hit_speed_base = Const.ROLE_HIT_SPEED_BASE
		self.move_speed_base = Const.ROLE_MOVE_SPEED_RADIX
		self.topSpeedY = csconst.ROLE_TOP_SPEED_Y			#Y轴上的运动不作回拉处理

		# 方法 calcDynamicProperties 和 calcHPMax 会判定玩家当前HP与HP_Max的值来重设HP的值
		# 所以在初始化从数据库中读取的HP值在HP_Max完全初始化之前是不能调用上述二个方法的
		hp = self.HP
		mp = self.MP
		# 1、重新处理装备栏的装备效果
		for equip in self.getItems( csdefine.KB_EQUIP_ID ):
			equip.wield( self, False )
		# 2、使buff重新生效（ reload Buff 时不需要实时计算玩家的属性值 ）
		self.buffReload()
		# 3、初始化技能效果（主动和被动技能）
		self.initSkills()
		#4.初始化道法装备效果
		for daofa in self.equipedDaofa:
			daofa.wield( self )

		self.calcDynamicProperties()  # 计算属性值

		#上线重新设置当前生命值和法力值
		self.setHP( hp )
		self.setMP( mp )

		# 处理有生命的物品
		self.resetLifeItems( True )

		# 如果状态不为以下状态，则回复到自由状态，否则回城复活
		state = self.getState()
		if	state != csdefine.ENTITY_STATE_DEAD and \
			state != csdefine.ENTITY_STATE_PENDING and \
			state != csdefine.ENTITY_STATE_QUIZ_GAME:
			self.changeState( csdefine.ENTITY_STATE_FREE )

		# 开始HP\MP恢复
		#self.startRevert()
		# 重设pk状态
		self.resetPkState()
		self.unLockPkMode()

		# 重置主角的移动行为，当前主角必须一出生就能广播坐标信息。
		self.volatileInfo = (BigWorld.VOLATILE_ALWAYS, BigWorld.VOLATILE_ALWAYS, None, None)
		self._lasttime =  BigWorld.time()	# 允许cell迁移的临时数据

		g_Statistic.initStat( self )	# 初始化角色统计数据

		self.addTimer( 0.0, Const.HONOR_RECOVER_TIME, ECBExtend.HONOR_RETURN_CBID )

		self.fallDownHeight = 0.0	# 起跳后下落高度

		# 水域加速效果触发
		self.isAccelerate = False

		#开启善良值带来的御敌点数变化
		self.optionReduceRD_goodness()

		#开启帮会带来的御敌点数变化
		self.optionReduceRD_tong()

		#劲舞时刻挑战的舞王位置（从1到19），如果为0表示练习斗舞
		self.challengeIndex = 0
		self.playerModelInfo = None  #用于舞厅玩家的替身模型

		#阵营烽火连天上线后需要更新玩家信息
		self.updateCampFengHuoInfo()

		self.combatCamp = self.getCamp()
		self.isUseCombatCamp = True


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def hackVerify_( self, srcEntityID ) :
		"""
		verify if the operation is legal or not( by huangyongwei )
		@type				srcEntityID : OBJECT_ID
		@param				srcEntityID : role's entity id
		@rtype							: bool
		@return							: if it is not hack operating return true
		"""
		if srcEntityID != self.id :
			hacker = BigWorld.entities.get( srcEntityID, None )
			if hacker :
				hacker.statusMessage( csstatus.GB_INVALID_CALLER )
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return False
		return True

	# -------------------------------------------------
	def onAddBuff( self, buff ) :
		"""
		当增加一个 buff 时被调用(
		by hyw -- 2008.09.23
		"""
		RoleEnmity.onAddBuff( self, buff )
		Team.onAddBuff( self, buff )
		RoleQuestInterface.onAddBuff( self, buff )

	def onRemoveBuff( self, buff ) :
		"""
		删除一个 buff 时被调用
		by hyw -- 2008.09.23
		"""
		RoleEnmity.onRemoveBuff( self, buff )
		Team.onRemoveBuff( self, buff )
		RoleQuestInterface.onRemoveBuff( self, buff )

	def onUpdateBuff( self, index, buff ) :
		"""
		当某个 buff 更新时被调用
		by hyw -- 2008.09.23
		"""
		RoleEnmity.onUpdateBuff( self, buff )
		Team.onUpdateBuff( self, buff )

	def onPetAddBuff( self, buff ):
		"""
		宠物添加buff，通知队友
		"""
		Team.onPetAddBuff( self, buff )

	def onPetRemoveBuff( self, buff ):
		"""
		宠物移除buff，通知队友
		"""
		Team.onPetRemoveBuff( self, buff )

	def onBuffMiss( self, receiver, skill ):
		"""
		buff未命中
		"""
		if receiver is None: return
		if skill is None: return
		self.statusMessage( csstatus.SKILL_BUFF_NOT_EFFECT, receiver.getName(), skill.getName() )

	def onBuffResist( self, receiver, buff ):
		"""
		buff被抵抗
		"""
		if receiver is None: return
		if buff is None: return
		self.statusMessage( csstatus.SKILL_BUFF_IS_BE_RESIST_EFFECT, receiver.getName(), buff.getBuff().getName() )

	def onBuffResistHit( self, buff ):
		"""
		抵抗了buff效果
		"""
		if buff is None: return
		self.statusMessage( csstatus.SKILL_BUFF_IS_RESIST_EFFECT, buff.getBuff().getName() )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	def statusMessage( self, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = len(args) and str(args) or ""
		self.client.onStatusMessage( statusID, args )

	def requestSkillBox( self ) :
		"""
		请求初始化(发送自身所有的skillID到请求者所在的client)
		"""
		self.client.initSkillBox( self.getSkills() )
		self.client.onInitialized( csdefine.ROLE_INIT_SKILLS )

	def requestInitialize( self, srcEntityID, initType ) :
		"""
		<Exposed/>
		请求初始化( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : 初始化类型，在 csdefine.py 中定义
		"""
		if not self.hackVerify_( srcEntityID ) : return

		if csdefine.ROLE_INIT_KITBAGS == initType:
			self.requestKitbags()
		elif csdefine.ROLE_INIT_ITEMS == initType:
			self.requestItems()
		elif csdefine.ROLE_INIT_COMPLETE_QUESTS == initType:
			self.requestCompletedQuest()
		elif csdefine.ROLE_INIT_QUEST_LOGS == initType:
			self.requestQuestLog()
		elif csdefine.ROLE_INIT_SKILLS == initType:
			self.requestSkillBox()
		elif csdefine.ROLE_INIT_BUFFS == initType:
			self.requestSelfBuffs()
		elif csdefine.ROLE_INIT_COLLDOWN == initType:
			self.requestSelfCooldowns()
		elif csdefine.ROLE_INIT_PRESTIGE == initType:
			self.requestSelfPrestige()
		elif csdefine.ROLE_INIT_REWARD_QUESTS == initType:
			self.requestRewardQuest()

	def onCellReady( self ):
		"""
		当cell生成后，可以再此做一些操作.
		譬如主动发一些数据给客户端
		"""
		self.onEnterSpace_()
		RoleRelation.onCellReady( self )
		self.calBenefitTime = BigWorld.time()
		self.client.change_money( self.money, csdefine.CHANGE_MONEY_INITIAL )
		self.client.change_EXP( self.EXP, self.EXP, csdefine.CHANGE_EXP_INITIAL )
		self.title_onLogin()	# 开始称号的初始化，因为称号需要用到师徒、夫妻的一些数据，需等师徒、夫妻初始化完毕才开始以避免异步问题。
		self.client.onGetBenefitTime( self.benefitTime )	# 在线积累时间的客户端计时触发 by姜毅
		self.clientGetLivingSkill()							# 初始化客户端采集技能数据 by 姜毅
		self.manageEidolon4Login()
		self.queryAboutDart()
		BigWorld.globalData["TiShouMgr"].queryRoleTSFlag( self.base, self.databaseID )
		RoleChallengeInterface.onCellReady( self )
		RoleYiJieZhanChangInterface.onCellReady( self )


	# ----------------------------------------------------------------
	# money handle
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

	def addMoney( self, number, reason ):
		"""
		@summary		:	加钱
		@type	number	:	int32
		@param	number	:	要添加的钱
		@type	reason	:	UINT
		@param	reason	:	什么原因添加金钱
		"""
		# 大于或小于0都是有意义的，但等于0，除了增加运算以外，实在是想不出有什么意义
		if number == 0:
			return

		oldMoney = self.money
		money = self.money + number
		if money > csconst.ROLE_MONEY_UPPER_LIMIT:
			self.money = csconst.ROLE_MONEY_UPPER_LIMIT
			self.statusMessage( csstatus.CIB_WARN_CANNOT_ADD_ANY_MONEY )
		elif money < 0:
			self.money = 0
		else:
			self.money = money
		self.client.change_money( self.money, reason )
		except_reasons = [	csdefine.CHANGE_MONEY_INITIAL,
							csdefine.CHANGE_MONEY_STORE,
							csdefine.CHANGE_MONEY_FETCH
							]
		if reason not in except_reasons:
			try:
				g_logger.moneyChangeLog( self.databaseID, self.getName(), oldMoney, self.money, reason, self.grade )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

		self.onMoneyChanged( number, reason )

	def payMoney( self, value, reason ):
		"""
		玩家付钱

		@param value: 付多少
		@type  value: INT32
		@return:      如果付款成功则返回True，否则返回False，失败的原因是由于钱不够
		@rtype:       BOOL
		"""
		if self.money - value < 0:
			return False
		self.addMoney( - value, reason )
		return True

	def onMoneyChanged( self, value, reason ):
		"""
		金钱改变了
		@param value: 金钱改变的数量
		@type  value: INT32
		"""
		ItemsBag.onMoneyChanged( self, value, reason )

	def gainMoney( self, value, reason ):
		"""
		给玩家钱

		@param value: 给多少
		@type  value: INT32
		@return:      如果给成功则返回True，否则返回False，失败的原因是由于钱太多，超出上限
		@rtype:       BOOL
		"""
		if self.money + value > csconst.ROLE_MONEY_UPPER_LIMIT:
			return False
		self.addMoney( value, reason )
		return True

	def freezeMoney( self ):
		"""
		冻结金钱操作
		@return: BOOL, true == 冻结成功，false == 冻结失败，失败的原因是它已冻结了
		"""
		return True

	def unfreezeMoney( self ):
		"""
		解冻金钱操作
		@return: None
		"""
		pass

	def getName( self ):
		"""
		virtual method.
		@return: the name of character entity
		@rtype:  STRING
		"""
		return self.playerName

	def getNameAndID( self ):
		"""
		virtual method.
		@return: the name of character entity and database id
		@rtype:  STRING
		"""
		return self.playerName + "(%s)" % self.databaseID

	def onGetWitness( self ):
		TEMP_MSG( "Set AoI to %d meter." % csconst.ROLE_AOI_RADIUS )
		# 设置AoI
		self.setAoIRadius( csconst.ROLE_AOI_RADIUS )

	def addTeachCredit( self, value, reason = csdefine.CHANGE_TEACH_CREDIT_NORMAL ):
		"""
		@summary	:	增加功勋值
		@type value	:	int32
		@param value :	功勋值
		@param reason : 功勋值改变的原因
		@type reason : INT8
		"""
		oldCredit = self.teachCredit
		self.teachCredit = self.teachCredit + value

		if reason == csdefine.CHANGE_TEACH_CREDIT_NORMAL:
			if value > 0:
				self.statusMessage( csstatus.TEACH_CREDIT_INCREASE, value )
			else:
				self.statusMessage( csstatus.TEACH_CREDIT_REDUCE, -value )
		elif reason == csdefine.CHANGE_TEACH_CREDIT_REWARD:
			pass

	def addKillMonsterExp( self, value ):
		"""
		Define method.
		获得杀怪经验

		"""
		# 经验石经验加成
		gemExp = value * ( self.gem_getComGemCount() + self.ptn_getComGemCount() ) * csconst.GEM_PET_COMMON_EXP_PERCENT
		if gemExp > 0:
			self.statusMessage( csstatus.EXP_GET_FOR_STONE, gemExp )
			value += int( gemExp )
		self.addExp( value, csdefine.CHANGE_EXP_KILLMONSTER )
		self.doAddKillMonsterExp( value )

	def addExp( self, value, reason ):
		"""
		define method.
		@summary	  : 增加经验值
		@type	value : int32
		@param	value : 经验值
		"""
		#--------- 以下为防沉迷系统的判断 --------#
		if value == 0:
			return
		gameYield = self.wallow_getLucreRate()		# 获得玩家游戏收益
		level = self.level
		if level >= csconst.ROLE_LEVEL_UPPER_LIMIT:			# 玩家等级上限暂时开放到110级。
			self.statusMessage( csstatus.ROLE_LEVEL_CAN_NOT_GAIN_EXP )
			return
		if value > 0:
			value = value * gameYield
			if reason == csdefine.CHANGE_EXP_LUCKYBOXZHAOCAI:
				tempString = str( int( value ) ) + cschannel_msgs.JING_YAN_LUAN_DOU_INFO_1
				self.statusMessage( csstatus.CIB_ZHAOCAI_ADD_REWARD, tempString )
			elif reason == csdefine.CHANGE_EXP_LUCKYBOXJINBAO:
				tempString = str( int( value ) ) + cschannel_msgs.JING_YAN_LUAN_DOU_INFO_1
				self.statusMessage( csstatus.CIB_JINBAO_ADD_REWARD, tempString )
			elif reason in [ csdefine.REWARD_TEAMCOMPETITION_EXP, csdefine.REWARD_ROLECOMPETITION_EXP, csdefine.CHANGE_EXP_TONGCOMPETITION ]:
				self.statusMessage( csstatus.ROLE_GET_KILL_EXP,int( value ) )
			elif reason in [ csdefine.REWARD_TEAMCOMPETITION_BOX_EXP, csdefine.REWARD_ROLECOMPETITION_BOX_EXP, csdefine.CHANGE_EXP_TONGCOMPETITION_BOX ]:
				self.statusMessage( csstatus.ROLE_GET_BOX_EXP,int( value ) )
			elif reason == csdefine.CHANGE_EXP_CITYWAR_OVER:
				self.statusMessage( csstatus.TONG_CITY_WAR_REWARD_WIN,int( value ) )
			elif reason == csdefine.CHANGE_EXP_CITYWAR_MASTER:
				self.statusMessage( csstatus.TONG_CITY_WAR_REWARD_MASTER,int( value ) )
			else:
				self.statusMessage( csstatus.ACCOUNT_STATE_GAIN_EXP, int( value ) )
		else:
			if reason == csdefine.CHANGE_EXP_FABAO:
				self.statusMessage( csstatus.ACCOUNT_LOST_EXP_FABAO, int( -value ) )
			else:
				self.statusMessage( csstatus.ACCOUNT_STATE_LOST_EXP, int( -value ) )	# 搞到这么难看就是为了个提示 by姜毅
		#--------- 以上为防沉迷系统的判断 --------#

		exp = value + self.EXP							# EXP 总余额
		expMax = RLevelEXP.getEXPMax( self.level )	# 当前等级的 exp 最大值
		while exp >= expMax :
			exp -= expMax								# 减去将要升级的 exp 最大值
			level += 1
			expMax = RLevelEXP.getEXPMax( level )
			if expMax <= 0 :
				ERROR_MSG( "error exp max: %d" % expMax )
				break
		if level > csconst.ROLE_LEVEL_UPPER_LIMIT : # 将等级限制在限制等级以内
			level = csconst.ROLE_LEVEL_UPPER_LIMIT
			exp = RLevelEXP.getEXPMax( level )
		try:
			g_logger.expChangeLog( self.databaseID, self.getName(),self.EXP,self.level,max( 0, exp ),level,reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		self.setLevel( level )
		self.EXP = max( 0, exp )						# 设置剩下的exp
		self.client.change_EXP( value, self.EXP, reason ) # 通知客户端

	def addTeamCompetitionReward( self, place ):
		"""
		Define method.
		给予组队竞赛经验奖励
		"""
		if place < 1 or place > len( csconst.RCG_TEAM_COMP_EXP ):
			ERROR_MSG( "Team Competition Exp Reward place error %i. RoleName %s ."%( place, self.getName() ) )
			return
		#awarder = g_rewards.fetch( csconst.RCG_TEAM_COMP_EXP[(place-1)], self )
		#awarder.award( self, csdefine.REWARD_TEAMCOMPETITION_EXP )
		if place == 1:
			self.setRoleRecord( "teamCompetitionWiner", "1" )

	def onEnterTeamCompetition( self ):
		"""
		Define method.
		进入组队竞技场
		"""
		self.addFlag( csdefine.ROLE_FLAG_SPEC_COMPETETE )

	def onEnterTongCompetition( self ):
		"""
		Define method.
		进入帮会竞技场
		"""
		self.client.onTongCompetitionStart()

	def onLeaveTeamCompetition( self ):
		"""
		Define method.
		离开组队竞技场
		"""
		self.removeFlag( csdefine.ROLE_FLAG_SPEC_COMPETETE )

	def setLevel( self, level ):
		"""
		@summary		:	设置等级
		@type	level	:	int16
		@param	level	:	新的等级
		"""
		if self.level == level: return
		deltaLevel = level - self.level
		self.level = level
		self.calcDynamicProperties()
		self.onLevelUp( deltaLevel )

	def getLevel( self ):
		"""
		"""
		return self.level

	def onLevelUp( self, deltaLevel ):
		"""
		升级通报
		"""
		# 通知base
		self.base.updateLevel( self.level )
		# 满血满魔
		self.full()
		# 查找是否有相应等级的任务触发
		self.enumLevelUpQuest()
		# 查找是否有因为等级变化完成的任务
		self.questRoleLevelUp( self.level )
		# 刷新pk状态
		self.resetPkState()
		# 师徒系统通知
		self.teach_onLevelUp()

		# 玩家经验石系统通知,wsf,16:23 2008-7-22
		self.gem_onLevelUp()
		# 宠物经验石系统通知，wsf16:27 2008-7-29
		self.ptn_onLevelUp()

		# 玩家生活系统通知，by 姜毅 11:48 2009-11-26
		self.liv_onLevelUp( deltaLevel )
		# 玩家升级触发范围伤害技能
		self.useSkill_onLevelUp()

		self.levelUp4Eidolon()


	def enumLevelUpQuest( self ):
		for level, questID in QuestsTrigger.g_QuestsLevelUpTrigger:
			if ( self.level == level ):
				quest = self.getQuest( questID )
				if not quest:
					return
				if quest.query( self ) == csdefine.QUEST_STATE_NOT_HAVE:
					quest.onPlayerLevelUp( self )
		return

	def useSkill_onLevelUp( self ):
		"""
		玩家升级触发范围伤害技能
		"""
		skl = str( self.level ).zfill( 3 )
		skillID = int( Const.ROLE_SKILL_IDS_ON_LEVEL_UP[self.getClass()] + skl )
		# 获取技能ID，释放技能
		self.spellTarget( skillID, self.id )

	def wizCommand(self, srcEntityID, dstEntityID, command, args):
		"""
		exposed method.
		GM及调试指令

		@param command: STRING; 命令关键字，相关请查看wizCommand::wizCommand()
		@param args: STRING; 命令参数，参数由各指令自己解释
		"""
		if not self.hackVerify_( srcEntityID ) : return
		wizCommand.wizCommand( self, dstEntityID, command, args )

	def onDestroy( self ):
		"""
		当销毁的时候做点事情
		注意，此时self.isDestroyed依然是False
		"""
		RoleRelation.onDestroy( self )
		self.onRoleOff()			#通知锦囊玩家下线
		self.updateBenefitTime()
		# 处理有生命的物品
		self.resetLifeItems( False )
		self.onLeaveSpace_()

		#### 离线前必要动作 ####
		# 下线时,处于战斗状态的时候强制改变状态,以通知怪物们取消敌意
		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			self.changeState( csdefine.ENTITY_STATE_PENDING )
		# 下线时,处于交易状态的时候取消交易状态
		if self.si_myState != csdefine.TRADE_SWAP_DEFAULT:
			tradeTarget = BigWorld.entities.get( self.si_targetID, None )
			if tradeTarget :
				self.si_tradeCancelFC( self.id )
				self.si_resetData()

		self.endRevert() # 结束HP\MP恢复

		# 当处于交易状态时需要通知
		PetCage.onDestroy( self )
		ItemsBag.onDestroy( self )
		RoleQuestInterface.onDestroy( self )
		# 获取下线之前的生命值、魔法值
		hp = self.HP
		mp = self.MP
		SkillBox.onDestroy( self )
		self.HP = hp
		self.MP = mp
		RoleChallengeSpaceInterface.onDestroy( self )
		RoleChallengeInterface.onDestroy( self )
		RoleDestinyTransInterface.onDestroy( self )
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI:
			RoleYeZhanFengQiInterface.onDestroy( self )
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			RoleYiJieZhanChangInterface.onDestroy( self )
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_FANG_SHOU :
			RoleCopyInterface.fangShou_onDestroy( self )

		#销毁非飞行/陆行骑宠数据
		if  not VehicleHelper.getCurrVehicleID( self ): #modify by wuxo 2012-5-30
			self.currVehicleData = VehicleHelper.getDefaultVehicleData()
		#销毁激活骑宠数据
		if  not VehicleHelper.getCurrAttrVehicleID( self ):
			self.currAttrVehicleData = VehicleHelper.getDefaultVehicleData_Attr()

		# 镖车
		dart = BigWorld.entities.get( self.queryTemp( "dart_id", 0) )
		if dart:
			dart.onRoleDestroy( self.id )

		# 切磋
		self.changeQieCuoState( csdefine.QIECUO_NONE )

		self.withdrawEidolon( self.id ) # 销毁小精灵

	# Change Time
	def ChangeTime(self, source, newtime, duration):
		"""
		 要求改变客户端时间

		@param source: source id
		@type source: INT

		@param newtime: new environment time，可以以两种形式出现：
						   一种是 时：分，如：  01:00 （凌晨1点）
						   另一种是浮点数，如： 1.0
						   任何其它格式的时间不会抛出异常，也不会起作用

		@param duration: time LAST HOW LONG
		@type duration: UINT16
		"""
		# duration in mintues
		self.addTimer( duration*60, 0, ECBExtend.RESTORETIME_TIMER_CBID )
		self.planesAllClients( "ReceiveChangeTime", (newtime,) )

	# Get Time
	def GetTime(self):
		"""
		 获得系统时间
		"""
		TimeInSecs = BigWorld.timeOfDay(self.spaceID)
		return math.fmod(TimeInSecs/3600, 24)

	# Restore Time
	def onRestoreTime( self, timerID, cbID ):
		"""
		 恢复客户端的时间为系统时间

		@param timerID: 回调函数 id
		@type timerID: INT
		"""
		self.cancel( timerID )
		RestoreTime = self.GetTime()
		self.planesAllClients( "ReceiveChangeTime", (RestoreTime,) )

	def onDie( self, killerID ):
		"""
		virtual method.

		死亡事情处理。
		"""

		killer = BigWorld.entities.get( killerID )
		if killer is None:		# 对于BUFF来说找不到杀人者是很正常的事情
			killerID = 0

		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		spaceScript.onRoleDie( self, killer )

		# 和spaceScript.isSpaceDesideDrop描述相似意思
		if not spaceScript.isSpaceCalcPkValue:
			# 计算pk值
			self.calcPkValue( killer )
			# 损失装备耐久
			self.equipAbrasionOnDied( killer )

		if not spaceScript.isSpaceDesideDrop and self.getLevel() > csdefine.ROLE_DIE_DROP_PROTECT_LEVEL:	# 2009-07-11 SPF
			# isSpaceDesideDrop的作用是掉落部分由space模块处理还是由这里处理
			# 详细见上面的spaceScript.onRoleDie， 因为有些地图是有自己的处理规则的
			# 比如竞赛死亡后不应该掉落任何东西，那么这个处理流程就交给spaceScript.onRoleDie中处理
			# 所以，如果副本地图不来决定掉落，才在这里统一处理掉落规则
			# 如有疑问请问SPF
			# 掉落金钱
			self.moneyDropOnDied( killer )
			# 死亡后，掉落物品装箱子里
			self.dropOnDied()

		# 对于玩家被那种敌人杀死 加入相应提示 by姜毅
		if killer is not None:
			killerType = killer.getEntityType()
			if killerType == csdefine.ENTITY_TYPE_ROLE:
				killerName = killer.getName()
				if self.onFengQi:
					killerName = ST.CHAT_CHANNEL_MASED
				self.statusMessage( csstatus.ROLE_BE_KILLED_BY_ROLE, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2, killerName )		# 被玩家杀
				try:
					g_logger.roleBeKillLog( killer.databaseID, self.databaseID, killer.grade )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )

			elif killerType == csdefine.ENTITY_TYPE_PET:
				owner = killer.getOwner()
				earg, m_killer = owner.etype, owner.entity
				if earg != "MAILBOX" :		# 一般不会是mailbox
					killerName = m_killer.getName()
					if self.onFengQi:
						killerName = ST.CHAT_CHANNEL_MASED
					self.statusMessage( csstatus.ROLE_BE_KILLED_BY_ROLE, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2, killerName )		# 被玩家杀
					try:
						g_logger.roleBeKillLog( m_killer.databaseID, self.databaseID, m_killer.grade )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )

			else:
				self.statusMessage( csstatus.ROLE_BE_KILLED_BY_MONSTER, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2, killer.getName() )	#被怪杀
				if killer.className in csconst.TDB_MONSTERS:			# 仙魔论战中死亡
					BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].recordDieData( killer.getCamp(), self.base, self.getName(), self.getLevel(), self.tongName )
				try:
					g_logger.roleBeKillLog( 0, self.databaseID, 0 )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
		else :
			self.statusMessage( csstatus.ACCOUNT_STATE_DEAD, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2 )

		self.team_notifyKilledMessage( killer )

		# 增加了玩家死亡自动取消吟唱 2009-07-01 spf
		if self.intonating():
			self.interruptSpell( csstatus.SKILL_IN_ATTACK )

		#处理玩家身上死亡对任务造成的影响，比如死亡则任务失败！ 2008-09-25 spf
		self.onDieAffectQuest( self )

		PetCage.onDie( self )
		RoleQuizGame.onDie( self )
		# 死亡退出切磋
		self.changeQieCuoState( csdefine.QIECUO_NONE )

		# 死亡重置反击列表
		if len( self.pkTargetList ) > 0:
			self.resetPKTargetList()

	def afterDie( self, killerID ):
		"""
		virtual method.

		死亡后回掉，执行一些子类在怪物死后必须做的事情。
		"""

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI:
			RoleYeZhanFengQiInterface.afterDie( self, killerID )

		RoleEnmity.afterDie( self, killerID )

	def interruptSpellFC( self, srcEntityID, reason ):
		"""
		exposed method.
		请求中断之前的施法
		"""
		if not self.hackVerify_( srcEntityID ) : return

		if self.attrIntonateSkill or self.attrHomingSpell:
			self.interruptSpell( reason )

	def onActWordChanged( self, act, disabled ):
		"""
		动作限制.
		"""
		# 先通知底层
		RoleEnmity.onActWordChanged( self, act, disabled )

		if act == csdefine.ACTION_FORBID_MOVE:
			self.updateTopSpeed()
			self.calcMoveSpeed()

		#ItemsBag.onActWordChanged( self, act, disabled )

	def updateTopSpeed( self ):
		"""
		virtual method = 0.

		更新移动速度限制(topSpeed)
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):return#处于飞行传送状态不响应速度上限值修改
		if self.hasFlag( csdefine.ROLE_FLAG_FORBID_TOPSPEED ):return
		if self.actionSign( csdefine.ACTION_FORBID_MOVE ) and ( not ( self.effect_state & csdefine.EFFECT_STATE_BE_HOMING ) ):
			self.topSpeed = 0.001
		else:
			topSpeed = self.move_speed * ( 1 + csconst.ROLE_MOVE_SPEED_BIAS )
			if self.queryTemp( "TOP_SPEED", 0.0 ) > 0.1:
				self.setTemp( "TOP_SPEED", 0.0 )
			else:
				self.topSpeed = topSpeed

	def setTopSpeed( self, topspeed ):
		"""
		设置移动速度限制(topSpeed)
		"""
		self.topSpeed = topspeed

	def setMoveSpeed( self, speed ):
		"""
		调用之前确保为RealEntity
		"""
		RoleEnmity.setMoveSpeed( self, speed )

	def doRandomRun( self, centerPos, radius ):
		"""
		走到centerPos为原点，radius为半径的随机采样点
		@param  centerPos: 原点
		@type   centerPos: Vector3
		@param  radius:    半径
		@type   radius:    FLOAT
		"""
		self.topSpeed = self.move_speed * ( 1 + csconst.ROLE_MOVE_SPEED_BIAS ) 	# 重新设置topSpeed
		self.client.doRandomRun( centerPos, radius )

	def onStateChanged( self, old, new ):
		"""
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
			@type new	:	integer
		"""
		RoleEnmity.onStateChanged( self, old, new )
		Team.onStateChanged( self, old, new )
		self.revertCheck()	# 恢复状态的改变
		self.flyingCheck()	# 如果新的状态为飞行，则执行一些和飞行相关的必要操作
		self.autoEnergyCheck()  #自动恢复跳跃值检查
		self.autoCombatCountCheck() #格斗衰减检查
		if new == csdefine.ENTITY_STATE_FREE:
			self.updateTopSpeed()

	def changePosture( self, posture ):
		"""
		改变姿态

		@param posture : 目标姿态
		@type posture : UINT16
		"""
		if posture == csdefine.ENTITY_POSTURE_NONE:	# 角色心法只能切换，不能置空
			return
		RoleEnmity.changePosture( self, posture )

	def flyingCheck( self ):
		"""
		如果新的状态为飞行，则执行一些和飞行相关的必要操作
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			return

		# if 玩家有出战宠物 then 收回宠物
		if self.pcg_getActPet():
			self.pcg_withdrawPet( self.id )

	def withdrawPet( self ):
		# define method.
		# 远程收回宠
		if self.pcg_getActPet():
			self.pcg_withdrawPet( self.id )

	#def selectTitle( self, srcEntityID, title ):
		"""
		Exposed method.

		@type title: UINT8
		"""
	#	if not self.hackVerify_( srcEntityID ) : return
	#	if title not in self.titles:
	#		ERROR_MSG( "%s(%i): title not found." % (self.playerName, self.id) )
	#		return
	#	self.title = title


	#def addTitle( self, title ):
		"""
		增加一个称号.

		@type title: UINT8
		@return: None
		"""
	#	self.titles.append( title )
	#	self.client.onTitleAdded( title )

	#def hasTitle( self, title ):
		"""
		判断角色是否拥有某种称号

		@type title: UINT8
		@rtype: BOOL
		"""
	#	return title in self.titles

	def changeCooldown( self, typeID, lastTime, totalTime, endTimeVal ):
		"""
		virtual method.
		改变一个cooldown的类型

		@type  typeID: INT16
		@type timeVal: INT32
		"""
		RoleEnmity.changeCooldown( self, typeID, lastTime, totalTime, endTimeVal )
		self.client.cooldownChanged( typeID, lastTime, totalTime )

	def calcRange( self ):
		"""
		virtual method.

		计算攻击距离
		"""
		if self.primaryHandEmpty():
			self.range_base = Const.ROLE_HANDEDS_FREE_RANGE
		RoleEnmity.calcRange( self )	# call to AvatarCommon.calcRange()


	def hasPotential( self, potential ):
		"""
		是否有潜能点
		@type  			potential	: INT
		@param 			potential	: 潜能点
		@return					: TRUE　有足够的潜能点，FALSE　潜能点不足
		"""
		if self.potential < potential:
			return False
		return True

	def payPotential( self, potential, reason = csdefine.CHANGE_POTENTIAL_INITIAL ):
		"""
		支付潜能点
		@type  			potential	: INT
		@param 			potential	: 潜能点
		@return					: TRUE　可以支付，FALSE　潜能点不足
		"""
		orgPotential = self.potential
		if self.potential < potential:
			return False
		self.potential -= potential
		if not reason == csdefine.CHANGE_POTENTIAL_TRANS:	# 传功不提示
			self.statusMessage( csstatus.ACCOUNT_STATE_LOSE_POTENTIAL, int( potential ) )
		# 潜能改变日志
		try:
			g_logger.potentialChangeLog( self.databaseID, self.getName(), orgPotential, self.potential, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def addPotential( self, potential, reason = csdefine.CHANGE_POTENTIAL_INITIAL ):
		"""
		define method.
		增加潜能点
		@type  			potential	: INT
		@param 			potential	: 潜能点
		@return					: TRUE
		"""
		if self.potential > csconst.ROLE_POTENTIAL_UPPER:
			self.statusMessage( csstatus.ACCOUNT_CANT_GAIN_POTENTIAL )
			return False
		orgPotential = self.potential
		#--------- 以下为防沉迷系统的判断 --------#
		gameYield = self.wallow_getLucreRate()
		if potential >=0:
			potential = potential * gameYield
		#--------- 以上为防沉迷系统的判断 --------#

		if self.potential + potential > csconst.ROLE_POTENTIAL_UPPER:
			potential = csconst.ROLE_POTENTIAL_UPPER - self.potential
			self.statusMessage( csstatus.ACCOUNT_CANT_GAIN_POTENTIAL )
		self.potential += potential
		if reason == csdefine.CHANGE_POTENTIAL_FABAO:
			pass	# 通过法宝获得潜能调用此方法时已做系统系统，此处过滤
		elif reason == csdefine.CHANGE_POTENTIAL_ZHAOCAI:
			tempString = str( int( potential ) ) + cschannel_msgs.QIAN_NENG_LUAN_DOU_INFO_1
			self.statusMessage( csstatus.CIB_ZHAOCAI_ADD_REWARD, tempString )
		elif reason == csdefine.CHANGE_POTENTIAL_JINBAO:
			tempString = str( int( potential ) ) + cschannel_msgs.QIAN_NENG_LUAN_DOU_INFO_1
			self.statusMessage( csstatus.CIB_JINBAO_ADD_REWARD, tempString )
		else:
			self.statusMessage( csstatus.ACCOUNT_STATE_GAIN_POTENTIAL, int( potential ) )
		# 潜能改变日志
		try:
			g_logger.potentialChangeLog( self.databaseID, self.getName(), orgPotential, self.potential, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def addPotentialBook( self, potential ):
		"""
		define method.
		增加潜能书潜能点
		@type  			potential	: INT
		@param 			potential	: 潜能点
		@return					: TRUE
		"""
		potentialBook = self.getItem_( ItemTypeEnum.CEL_POTENTIAL_BOOK )
		if potentialBook is None:
			return
		potentialBook.addPotential( potential, self )

	def addPotentialPickAnima( self, potential ):
		"""
		define method.
		增加潜能书潜能点
		@type  			potential	: INT
		@param 			potential	: 潜能点
		@return					: TRUE
		"""
		decRewardPotential = self.queryTemp( "decRewardPotential", 0.0 )
		cpotential = int( potential * ( 1 - decRewardPotential ) )
		self.addPotential( cpotential, csdefine.CHANGE_POTENTIAL_PICK_ANIMA )
		
	def addDaoheng( self, value, reason = 0 ):
		# 添加自身道行值
		"""
		@summary	  : 增加道行值
		@type	value : int32
		@param	value : 道行值
		@type	reason : int32
		@param	reason : 原因
		"""
		#--------- 以下为防沉迷系统的判断 --------#
		gameYield = self.wallow_getLucreRate()		# 获得玩家游戏收益
		if value > 0:
			value = value * gameYield
		if  int( value ) == 0 :
			return
		self.statusMessage( csstatus.ACCOUNT_STATE_GAIN_DAOHENG, int( value ) )
		#--------- 以上为防沉迷系统的判断 --------#

		CombatUnit.addDaoheng( self, value, reason )
		try:
			g_logger.daohengAddLog( self.databaseID, self.getName(), self.getDaoheng(), value, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setDaoheng( self, dxValue, reason = 0 ):
		# 设置自身道行值
		"""
		@summary	  : 增加道行值
		@type	value : int32
		@param	value : 道行值
		@type	reason : int32
		@param	reason : 原因
		"""
		CombatUnit.setDaoheng( self, dxValue, reason )
		try:
			g_logger.daohengSetLog( self.databaseID, self.getName(), value, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setHP( self, value ):
		"""
		real entity method.
		virtual method
		设置HP
		"""
		RoleEnmity.setHP( self, value )

		self.revertCheck()

	def setMP( self, value ):
		"""
		real entity method.
		virtual method
		设置MP
		"""
		RoleEnmity.setMP( self, value )

		self.revertCheck()

	def calcPhysicsDPSBase( self ):
		"""
		计算物理DPS_base值
		"""
		try:  # add by wuxo 2012-1-10 为了防止拿GM武器在使用加攻击的BUFFER时报错的情况,数据太大 溢出
			self.physics_dps_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcRolePhysicsDPS( self ) * csconst.FLOAT_ZIP_PERCENT )
		except:
			self.physics_dps_base = 0

	def calcHPMaxBase( self ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		self.HP_Max_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcRoleHPMaxBase( self ) )

	def calcHPMax( self ):
		"""
		real entity method.
		virtual method
		"""
		RoleEnmity.calcHPMax( self )
		self.revertCheck()

	def calcMPMaxBase( self ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		v =  CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcRoleMPMaxBase( self )
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].MP_Max_value	# 每级MP上限加值
		self.MP_Max_base = int( v + v_value * self.level )

	def calcMPMax( self ):
		"""
		real entity method.
		virtual method
		"""
		RoleEnmity.calcMPMax( self )
		self.revertCheck()

	def calcDamageMinBase( self ):
		"""
		计算最小物理攻击力 基础值
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps_value
		physic_dps_base = v + v_value * ( self.level - 1 )  # 基础物理攻击力加值
		self.damage_min_base = int( self.physics_dps * self.hit_speed * ( 1.0 - self.wave_dps ) + physic_dps_base )

	def calcDamageMaxBase( self ):
		"""
		计算最大物理攻击力 基础值
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps_value
		physic_dps_base = v + v_value * ( self.level - 1 )	# 基础物理攻击力加值
		self.damage_max_base = int( self.physics_dps * self.hit_speed * ( 1.0 + self.wave_dps ) + physic_dps_base )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		法术攻击力
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].magic_dps
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].magic_dps_value
		magic_dps_base = v + v_value * ( self.level - 1 )	# 基础法术攻击力加值
		self.magic_damage_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcRoleMagicDamage( self ) + magic_dps_base )

	def startRevert( self ):
		"""
		启动HP和MP恢复速度
		"""
		if self.revertID:
			WARNING_MSG( "Revert addTimer Again !!!" )
			self.cancel( self.revertID )

		self.revertID = self.addTimer( Const.ROLE_MP_REVER_INTERVAL, Const.ROLE_MP_REVER_INTERVAL, ECBExtend.REVERT_HPMP_TIMER_CBID )

	def endRevert( self ):
		"""
		结束HP和MP恢复速度
		"""
		if self.revertID:
			self.cancel( self.revertID )
			self.revertID = 0

	def revertCheck( self ):
		"""
		恢复检查
		"""
		state = self.getState()
		if state != csdefine.ENTITY_STATE_FIGHT and state != csdefine.ENTITY_STATE_DEAD:
			if (self.HP_Max > self.HP or self.MP_Max > self.MP) and self.revertID == 0:
				self.startRevert()
		elif self.revertID:
			self.endRevert()

	def onRevertTimer( self, controllerID, userData ):
		"""
		时间处发事件
		"""
		if self.HP_Max > self.HP and self.queryTemp( "forbid_revert_hp", True ):
			self.addHP( self.HP_regen )
		if self.MP_Max > self.MP and self.queryTemp( "forbid_revert_mp", True ):
			self.addMP( self.MP_regen )
		if self.HP_Max == self.HP and self.MP_Max == self.MP:
			self.endRevert()

	# ----------------------------------------------------------------
	# 自动恢复跳跃值相关
	# ----------------------------------------------------------------
	def autoEnergyCheck( self ):
		state = self.getState()
		if state != csdefine.ENTITY_STATE_FIGHT and state != csdefine.ENTITY_STATE_DEAD:
			if self.energy < csdefine.JUMP_ENERGY_MAX and self.autoEnergyID == 0:
				self.startAutoEnergy()
		elif self.autoEnergyID:
			self.endAutoEnergy()

	def startAutoEnergy( self ):
		"""
		启动跳跃能量值恢复速度
		"""
		if self.autoEnergyID:
			WARNING_MSG( "auto EnergyID addTimer Again !!!" )
			self.cancel( self.autoEnergyID )

		self.autoEnergyID = self.addTimer( csdefine.ROLE_ENERGY_REVER_INTERVAL, csdefine.ROLE_ENERGY_REVER_INTERVAL, ECBExtend.REVERT_ENERGY_TIMER_CBID )

	def endAutoEnergy( self ):
		"""
		结束跳跃能量值恢复速度
		"""
		self.cancel( self.autoEnergyID )
		self.autoEnergyID = 0

	def onAutoEnergyTimer( self, controllerID, userData ):
		"""
		时间触发事件
		"""
		if self.energy < csdefine.JUMP_ENERGY_MAX:
			self.calEnergy( csdefine.ROLE_ENERGY_REVER_VALUE )
		if self.energy == csdefine.JUMP_ENERGY_MAX :
			self.endAutoEnergy()

	def calEnergy( self, value ):
		"""
		real entity method.
		设置Energy
		"""
		preValue = self.energy
		value += preValue
		if value < 0:
			value = 0
		elif value > csdefine.JUMP_ENERGY_MAX:
			value = csdefine.JUMP_ENERGY_MAX
		self.energy = value
		self.autoEnergyCheck()

	# ----------------------------------------------------------------
	# 格斗点数相关
	# ----------------------------------------------------------------
	def autoCombatCountCheck( self ):
		"""
		检查是否开启timmer
		"""
		state = self.getState()
		if state == csdefine.ENTITY_STATE_DEAD:
			self.combatCount = 0
			return
		if state != csdefine.ENTITY_STATE_FIGHT:
			self.startAutoCombatCount()
		else:
			if self.autoCombatCountID:
				self.endAutoCombatCount()

	def calCombatCount( self, value ):
		"""
		格斗值增加/减少
		"""
		preValue = self.combatCount
		preValue += value
		if preValue < 0:
			preValue = 0
		elif preValue > csdefine.ROLE_CombatCount_MAX:
			preValue = csdefine.ROLE_CombatCount_MAX
		self.combatCount = preValue
		self.autoCombatCountCheck()

	def startAutoCombatCount( self ):
		"""
		脱离战斗格斗点数自动衰减
		"""
		if self.autoCombatCountID:
			WARNING_MSG( "auto CombatCount addTimer Again !!!" )
			self.cancel( self.autoCombatCountID )
		if self.combatCount > 0:
			self.autoCombatCountID = self.addTimer( csdefine.ROLE_CombatCount_TIMMER, csdefine.ROLE_CombatCount_TIMMER, ECBExtend.CombatCount_TIMER_CBID )

	def onAutoCombatCountTimer( self, controllerID, userData ):
		"""
		timmer回调
		"""
		if self.combatCount > 0:
			self.calCombatCount( -csdefine.ROLE_CombatCount_TIMMER_VALUE )
		else:
			self.endAutoCombatCount()

	def endAutoCombatCount( self ):
		"""
		结束timmer
		"""
		self.cancel( self.autoCombatCountID )
		self.autoCombatCountID = 0


	# ----------------------------------------------------------------
	# 装备修理相关
	# ----------------------------------------------------------------
	def _calcuRepairEquipMoney( self, equip, repairType, revenueRate ):
		"""
		计算修理一个装备的价格
		@param    equip: 装备数据
		@type     equip: instance
		@param    repairType: 修理类型
		@type     repairType: UNIT8
		@param    revenueRate	: 税收比率
		@type     revenueRate	: UINT16
		@return: 最终价格, 额外税
		"""
		# 普通修理的修理费比率为 1
		if repairType == csdefine.EQUIP_REPAIR_NORMAL:
			repairCostRate = 1
		# 特殊修理的修理费比率为 3
		elif repairType == csdefine.EQUIP_REPAIR_SPECIAL:
			repairCostRate = 1.5
		elif repairType == csdefine.EQUIP_REPAIR_ITEM:
			return 0, 0
		else:
			assert "That is a Error!!!, use undefine repair type "

		# 品质系数*（1-（实际耐久度/原始最大耐久度））*道具价格，用去掉小数＋1的方法取整。
		repairRate = EquipQualityExp.instance().getRepairRateByQuality( equip.getQuality() )
		repairMoney = repairRate * ( 1 - float( equip.getHardiness() ) / float( equip.getHardinessLimit() ) ) * equip.getRecodePrice() * repairCostRate
		revenueMoney = 0
		iMoney = int( repairMoney )
		if iMoney != repairMoney:
			repairMoney = iMoney + 1

		# 城市占领帮会打折10%
		spaceType = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if self.tong_holdCity == spaceType:
			repairMoney *= 0.9
		elif revenueRate > 0:
			revenueMoney = int( repairMoney * ( revenueRate / 100.0 ) )
			repairMoney += revenueMoney
		return int( math.ceil( repairMoney ) ), revenueMoney

	def repairOneEquip( self, repairType, kitBagID, orderID, revenueRate, npcID ):
		"""
		define method.
		单个装备修理
		@param    repairType	: 修理类型
		@type     repairType	: int
		@param    kitBagID		: 背包索引
		@type     kitBagID		: UINT16
		@param    orderID		: 物品索引
		@type     orderID		: INT32
		@param    revenueRate	: 税收比率
		@type     revenueRate	: UINT16
		@param    npcID			: NPC的ID
		@type     npcID			: STRING
		@return   无
		"""
		# 获取要单个修理的装备
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_REPARE, "" )
			return
		equip = self.getItem_( orderID )
		if equip == None:
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_EXIST )
			return
		#  判断装备能否修理
		if not equip.canRepair():
			self.statusMessage( csstatus.EQUIP_REPAIR_CANT_REPAIR )
			return
		#  判断装备耐久度是否无需修理
		if equip.getHardiness() == equip.getHardinessLimit():
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_REPAIR )
			return
		repairMoney, revenueMoney = self._calcuRepairEquipMoney( equip, repairType, revenueRate )
		if not self.payMoney( repairMoney, csdefine.CHANGE_MONEY_REPAIRONEEQUIPBASE ):
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
			return
		if repairType != csdefine.EQUIP_REPAIR_SPECIAL and repairType != csdefine.EQUIP_REPAIR_ITEM:
			hardinessLimit = equip.getHardinessLimit()
			hardinessMax = equip.getHardinessMax()
			if hardinessLimit*1.0/hardinessMax > Const.EQUIP_REPAIL_LIMIT:
				equip.addHardinessLimit( -int( hardinessMax * 0.05 ),  self )

			try:
				g_logger.equipRepairNormalLog( self.databaseID, self.getName(), equip.uid, equip.name(), hardinessLimit, equip.getHardinessLimit(), repairMoney, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), npcID )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

		equip.addHardiness( equip.getHardinessLimit(),  self )
		self.statusMessage( csstatus.EQUIP_REPAIR_SUCCEED, equip.name() )
		self.client.equipRepairCompleteNotify()
		# 记录城市税收
		if revenueMoney > 0:
			BigWorld.globalData[ "TongManager" ].onTakeCityRevenue( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), revenueMoney )

	def repairAllEquip( self, repairType, revenueRate, npcID):
		"""
		define method.
		修理身上所有装备
		@param    repairType: 修理类型
		@type     repairType: int
		@param    revenueRate	: 税收比率
		@type     revenueRate	: UINT16
		@param    npcID			: NPC的ID
		@type     npcID			: STRING
		@return   无
		"""
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_REPARE, "" )
			return
		repairMoney = 0
		revenueMoney = 0
		repairEquips = []
		for item in self.getAllItems():
			if item.isEquip():
				if not item.canRepair():	# wsf,16:21 2008-7-2
					DEBUG_MSG( "( %i )'s equip( id:%s ) can not be repaired." % ( self.id, item.id ) )
					continue
				if item.getHardiness() == item.getHardinessLimit():
					continue
				repairEquips.append( item )
				tmpRepairMoney, tmpRevenueMoney = self._calcuRepairEquipMoney( item, repairType, revenueRate )
				revenueMoney += tmpRevenueMoney
				repairMoney += tmpRepairMoney

		if len( repairEquips ) == 0:
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_REPAIR )
			return

		if not self.payMoney( repairMoney, csdefine.CHANGE_MONEY_REPAIRALLEQUIPBASE ):
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
			return

		for equip in repairEquips:
			if repairType != csdefine.EQUIP_REPAIR_SPECIAL and repairType != csdefine.EQUIP_REPAIR_ITEM:
				hardinessLimit = equip.getHardinessLimit()
				hardinessMax = equip.getHardinessMax()
				if hardinessLimit*1.0/hardinessMax > Const.EQUIP_REPAIL_LIMIT:
					equip.addHardinessLimit( - int( hardinessMax * 0.05 ), self )
					try:
						repairMoney = self._calcuRepairEquipMoney( equip, repairType, revenueRate )[0]
						g_logger.equipRepairNormalLog( self.databaseID, self.getName(), equip.uid, equip.name(), hardinessLimit, equip.getHardinessLimit(), repairMoney, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), npcID )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )

			equip.addHardiness( equip.getHardinessLimit(), self )

		self.statusMessage( csstatus.EQUIP_REPAIR_ALL_SUCCEED )
		self.client.equipRepairCompleteNotify()
		# 记录城市税收
		if revenueMoney > 0:
			BigWorld.globalData[ "TongManager" ].onTakeCityRevenue( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), revenueMoney )

	# ----------------------------------------------------------------
	# 装备磨损
	# ----------------------------------------------------------------
	def _addHardiness( self, equip, value ):
		"""
		添加耐久度
		@param equip: 装备
		@type  equip: instance
		@param value: 耐久度
		@type  value: int
		@return : None
		"""
		if value == 0:
			return

		ecull = equip.getHardiness()
		hardiness = ecull + value
		emax = equip.getHardinessLimit()

		if hardiness < emax * 0.2 and ecull > emax * 0.2:
			self.onEquipHardinessDegrade( equip )

		# 装备下降后的耐久与装备现在的耐久差值少于10000，则不通知客户端
		if hardiness > 0 and int( hardiness )/csconst.EQUIP_HARDINESS_UPDATE_VALUE == ecull/csconst.EQUIP_HARDINESS_UPDATE_VALUE:
			owner = None
		else:
			owner = self

		equip.setHardiness( int( hardiness ), owner )

	def _calcuEquipConsume( self, equip, demageValue, amemdValue, hasNombril ):
		"""
		"""
		if hasNombril:
			hardinessAbrasion = g_armorAmend.getEquipDemageValueWithNombril(equip.query("type")) + amemdValue
		else:
			hardinessAbrasion = g_armorAmend.getEquipDemageValueWithoutNombril(equip.query("type")) + amemdValue
		#TEMP_MSG("装备%i耐久度损耗: %s"%(equip.query("type"), max( 1.0, demageValue * hardinessAbrasion ) )	)
		self._addHardiness( equip, -max( 1.0, demageValue * hardinessAbrasion ) )

	def onEquipHardinessDegrade( self, equip ):
		"""
		装备耐久度小于20%
		@param equip: 装备
		@type  equip: instance
		"""
		self.statusMessage( csstatus.CIB_MSG_EQUIP_HARDINESS, equip.query("name") )

	def equipAbrasionOnDied( self, killer ):
		"""
		玩家死亡装备耐久的磨损

		被NPC杀死，死亡耐久度损失为5%；被用户杀死，无损。16:43 2009-6-12,wsf

		白名玩家死亡时损失装备耐久度调整为4% 红名玩家死亡时损失装备耐久度为40%
		白名玩家的死亡损失仅在被NPC杀死时有效，被其他玩家杀死无任何损失。
		红名玩家的死亡损失在被NPC杀死时或被其他玩家杀死时均有效。 10:45 2009-9-25 by姜毅
		"""
		if killer is None:		# 被笔记本杀死，无视耐久磨损
			return

		if killer.getEntityType() == csdefine.ENTITY_TYPE_ROLE and self.pkValue <= 0:
			return

		# 被NPC杀死，死亡耐久度损失为5%。
		equipList = self.getItems( csdefine.KB_EQUIP_ID )
		if self.pkValue <= 0:
			for equip in equipList:
				if equip.isEquip(): self._addHardiness( equip, -equip.getHardinessMax() * 0.04 )
		else:
			for equip in equipList:
				if equip.isEquip(): self._addHardiness( equip, -equip.getHardinessMax() * 0.2 )

	def moneyDropOnDied( self, killer ):
		"""
		死亡金钱掉落

		被NPC杀死，死亡损失身上10%的金钱。
		"""
		if self.level < csconst.PK_PROTECT_LEVEL:
			return
		if killer is None:
			return
		if killer.getEntityType() == csdefine.ENTITY_TYPE_ROLE and self.pkValue <= 0:
			return
		if self.pkValue <= 0: self.payMoney( int( self.money * 0.1 ), csdefine.CHANGE_MONEY_MONEYDROPONDIED )
		else: self.payMoney( int( self.money * 0.2 ), csdefine.CHANGE_MONEY_MONEYDROPONDIED )

	def equipDamage( self, demageValue ):
		"""
		define method.
		"""
		self.totalEquipDamage += demageValue
		if self.totalEquipDamage > 10000:
			demageValue = self.totalEquipDamage
			self.totalEquipDamage = 0
		else:
			return

		#TEMP_MSG("装备承受攻击总数: %s"%demageValue)
		equipList = self.getItems( csdefine.KB_EQUIP_ID )
		equipList = [ k for k in equipList if k.getHardiness() != 0 ]	# 只取有耐久度的装备
		if len( equipList ) == 0: return

		tempA = 1.0 #总持久度
		tempB = 0.0 #有盾牌时，没有佩带装备的空位的分摊比例叠加
		tempC = 0.0 #无盾牌时，没有佩带装备的空位的分摊比例叠加
		hasNombril = False
		weapon = 0
		for i in equipList:
			eq_type = i.query("type")
			if eq_type == ItemTypeEnum.ITEM_WEAPON_SHIELD:
				hasNombril = True
			if eq_type in ItemTypeEnum.WEAPON_LIST:
				weapon = i
				continue
			tempB += g_armorAmend.getEquipDemageValueWithNombril( eq_type )	 #有盾牌时的伤害分摊比例
			tempC += g_armorAmend.getEquipDemageValueWithoutNombril( eq_type ) #无盾牌时的伤害分摊比例

		equipLen = len( equipList )
		if weapon:
			equipLen -= 1

		if equipLen <= 0:
			return
		if hasNombril:
			tempD = (tempA - tempB) / equipLen
		else:
			tempD = (tempA - tempC) / equipLen
		for i in equipList:
			if i is weapon: continue
			self._calcuEquipConsume( i, demageValue, tempD, hasNombril )

	def equipAbrasion( self, demageValue ):
		"""
		define method.
		"""
		self.totalEquipDamage += demageValue
		if self.totalEquipDamage > 10000:
			demageValue = self.totalEquipDamage
			self.totalEquipDamage = 0
		else:
			return
		#TEMP_MSG("武器攻击造成破坏总数: %s"%demageValue )
		equipList = self.getItems( csdefine.KB_EQUIP_ID )
		equipList = [ k for k in equipList if k.getHardiness() != 0 and k.query("type") in ItemTypeEnum.WEAPON_LIST ]	# 只取有耐久度的装备
		for equip in equipList:
			self._calcuEquipConsume( equip, demageValue, 0, False )

	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系，要么敌对要么友好
		注意: 因为这个函数的使用频率极其的高，为了效率，部分的处理将不走函数调用的方式
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		# 观察者模式
		if self.effect_state  & csdefine.EFFECT_STATE_WATCHER:
			return csdefine.RELATION_NOFIGHT

		#if not isinstance( entity, CombatUnit ):
		#	return csdefine.RELATION_FRIEND

		if self.state == csdefine.ENTITY_STATE_PENDING:
			return csdefine.RELATION_NOFIGHT

		if self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
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
						# 将这段代码从canPk中分离出来
						if not self.actionSign( csdefine.ACTION_FORBID_PK ) and not entity.actionSign( csdefine.ACTION_FORBID_PK ):
							if self.hasEnemy( entity.id ) or self.pkTargetList.has_key( entity.id ):
								return csdefine.RELATION_ANTAGONIZE
						
						if self.canPk( entity ):
							return csdefine.RELATION_ANTAGONIZE
						else:
							return csdefine.RELATION_FRIEND
					else:
						return relation
			else:
				return csdefine.RELATION_FRIEND
			
		# it's monster
		if entity.utype == csdefine.ENTITY_TYPE_MONSTER:
			# 对于护送的怪物，需要增加特殊处理
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_FRIEND_ROLE ): # 玩家对怪物绝对友好标志
				return csdefine.RELATION_FRIEND
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_SPEAKER ):
				return csdefine.RELATION_FRIEND
			if hasattr( entity, "ownTongDBID" ) and entity.ownTongDBID == self.tong_dbID:
				return csdefine.RELATION_FRIEND
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
				return csdefine.RELATION_FRIEND
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE_2 ):
				return csdefine.RELATION_FRIEND
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND

			bootyOwner = entity.queryTemp( "ToxinFrog_bootyOwner", () )
			if bootyOwner:
				getTeam = getattr( self, "getTeamMailbox", None )
				if getTeam and getTeam():
					if getTeam().id != bootyOwner[1]:
						return csdefine.RELATION_FRIEND
				else:
					if self.id != bootyOwner[0]:
						return csdefine.RELATION_FRIEND
			return self.queryCampRelation( entity )

		if entity.isEntityType( csdefine.ENTITY_TYPE_TONG_NAGUAL ):
			if self.tong_dbID in entity.enemyTongDBIDList:
				return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_SLAVE_MONSTER or entity.utype == csdefine.ENTITY_TYPE_VEHICLE_DART:
			if self.actionSign( csdefine.ACTION_FORBID_PK ) or entity.actionSign( csdefine.ACTION_FORBID_PK ) or self.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT:
				return csdefine.RELATION_FRIEND
			if entity.queryTemp( "ownerTongDBID",0 ) != 0 and entity.queryTemp( "ownerTongDBID" ) == self.tong_dbID:		# 帮会镖车与帮会成员的关系为友好
				return csdefine.RELATION_FRIEND
			ownerID = entity.getOwnerID()
			if BigWorld.entities.has_key( ownerID ):											#判定怪物主人的敌对关系
				if ownerID == self.id:
					return csdefine.RELATION_FRIEND
				return self.queryRelation( BigWorld.entities[ownerID] )
			elif self.pkState == csdefine.PK_STATE_PROTECT:
				return csdefine.RELATION_FRIEND
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_TREASURE_MONSTER:
			# 对于盗宝贼怪物，就是敌人
			return csdefine.RELATION_ANTAGONIZE

		# 是帮会夺城战怪物
		if entity.utype == csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER:
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			if entity.belong == self.tong_dbID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_XIAN_FENG or entity.utype == csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_ALTAR or \
			entity.utype == csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_TOWER or entity.utype == csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER:
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			if entity.ownTongDBID == self.tong_dbID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_CAMP_XIAN_FENG or entity.utype == csdefine.ENTITY_TYPE_CAMP_FENG_HUO_ALTAR or \
			entity.utype == csdefine.ENTITY_TYPE_CAMP_FENG_HUO_TOWER or entity.utype == csdefine.ENTITY_TYPE_CAMP_FENG_HUO_BASE_TOWER:
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			if entity.ownCamp == self.getCamp():
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		# 队伍归属怪物
		if entity.utype == csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM:
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			if self.teamMailbox and entity.belong == self.teamMailbox.id:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		# 猰貐
		if entity.utype == csdefine.ENTITY_TYPE_YAYU:
			return csdefine.RELATION_FRIEND

		# 异界战场箭塔
		if entity.utype == csdefine.ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER:
			if self.yiJieFaction != 0 and entity.battleCamp == self.yiJieFaction :
				return csdefine.RELATION_FRIEND

		# 帮会夺城战决赛
		if entity.utype == csdefine.ENTITY_TYPE_CITY_WAR_FINAL_BASE:
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			if entity.belong == self.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ):
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		# it's a pet
		if entity.utype == csdefine.ENTITY_TYPE_PET:
			owner = entity.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_FRIEND
			# 把宠物的敌对比较转嫁给它的主人
			# 虽然此关系未来可能会根据不同的状态或buff导致关系的改变，但当前并没有此需求
			entity = owner.entity

		if entity.state == csdefine.ENTITY_STATE_PENDING:
			return csdefine.RELATION_NOFIGHT
		if entity.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return csdefine.RELATION_NOFIGHT
		if self.state == csdefine.ENTITY_STATE_RACER:											#赛马状态，返回友好
			return csdefine.RELATION_FRIEND


		# 免战判定
		# 对手是人
		if entity.utype == csdefine.ENTITY_TYPE_ROLE:
			if self.qieCuoState == csdefine.QIECUO_FIRE:
				if self.isQieCuoTarget( entity.id ):
					return csdefine.RELATION_ANTAGONIZE

		# 免战
		if self.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT

		# 全体免战判定
		if self.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
			entity.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT

		# 将这段代码从canPk中分离出来
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and not entity.actionSign( csdefine.ACTION_FORBID_PK ):
			if self.hasEnemy( entity.id ) or self.pkTargetList.has_key( entity.id ):
				return csdefine.RELATION_ANTAGONIZE

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
				
		if hasattr( entity, "getSubState" ) and entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return csdefine.RELATION_FRIEND
			
		if entity.utype == csdefine.ENTITY_TYPE_SLAVE_MONSTER or entity.utype == csdefine.ENTITY_TYPE_VEHICLE_DART:
			if self.actionSign( csdefine.ACTION_FORBID_PK ) or entity.actionSign( csdefine.ACTION_FORBID_PK ):
				return csdefine.RELATION_FRIEND
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

	# ----------------------------------------------------------------
	# 死亡掉落
	# ----------------------------------------------------------------

	def dropOnDied( self ):
		"""
		死亡掉落
		"""
		# 装备掉落都发生在已装备的且未绑定的装备上
		# 如果玩家全身的装备都已经绑定则不发生掉落
		# pk值 == 0		：0.5%几率掉落未绑定装备1件  修改为同几率掉落未认主装备1件 by姜毅
		# Pk值 > 0		：10%的几率损失1至2件	  by姜毅
		# 30级pk保护
		dropItemsOnDied = []	# 掉落物品的copy
		dropItemsOrder = []		# 掉落物品的order

		# 掉落跑商物品
		for iItem in self.getAllItems():
			if iItem.query( 'merchantItem', False ):
				iItem.onDieDrop()
				dropItemsOnDied.append( iItem.copy() )
				dropItemsOrder.append( iItem.order )
				INFO_MSG( "Drop iItem %s (%s) Obey State %s"%( iItem.name, str(iItem.uid), str(iItem.isObey()) ) )

		if len( dropItemsOnDied ) != 0:
			# 掉落箱子，掉落物品装箱子里
			x, y, z = self.position
			collide = BigWorld.collide( self.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
			# 掉落物品的时候对地面进行碰撞检测避免物品陷入地下
			if collide != None: y = collide[0].y
			itemBox = BigWorld.createEntity( "DroppedBox", self.spaceID, ( x, y, z ), self.direction, {} )
			itemBox.init( [], dropItemsOnDied )
			# phw: 这里必须先把要删除的物品清除，否则下面直接return的代码，
			# 会导致被杀的人物品掉出来了，但身上的物品没有删除的问题。
			for order in dropItemsOrder:
				self.removeItem_( order, reason = csdefine.DELETE_ITEM_DROPONDIED )
			# 重新置空要删除的物品列表，以待下面使用。
			dropItemsOrder = []

		# 掉落装备
		if self.level <= csconst.PK_PROTECT_LEVEL: return
		# 根据pk值获取掉率
		if self.pkValue > 0:
			dropOdds = Const.PK_REDNAME_DROP_ODDS
		else:
			dropOdds = Const.PK_PEACE_DROP_ODDS

		# 判断是否随机到
		if random.random() > dropOdds: return
		# 获取未认主的装备
		unObeyEquips = self.getUnObeyEquips()
		canDropList = []
		if len( unObeyEquips ) <= 0: return
		# 获得可掉落类的装备
		for uequip in unObeyEquips:
			if uequip.getType() not in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
				canDropList.append( uequip )
		if len( canDropList ) <= 0: return
		# 随机获取一个装备
		dropItem = random.choice( canDropList )
		dropItem.unWield( self )
		dropItemsOrder.append( dropItem.order )
		INFO_MSG( "%s(%i) drop Equip %s (%s) Obey State %s"%( self.getName(), self.id, dropItem.name, str(dropItem.uid), str(dropItem.isObey()) ) )
		# 如果是红名 则多抽一件装备
		if self.pkValue > 0:
			dropItem2 = random.choice( canDropList )
			if dropItem != dropItem2:
				dropItem2.unWield( self )
				dropItemsOrder.append( dropItem2.order )
				INFO_MSG( "%s(%i) drop Equip2 %s (%s) Obey State %s"%( self.getName(), self.id, dropItem.name, str(dropItem.uid), str(dropItem.isObey()) ) )

		for order in dropItemsOrder:
			self.resetEquipModel( order, None )
			self.removeItem_( order, reason = csdefine.DELETE_ITEM_DROPONDIED )


	# ----------------------------------------------------------------
	# 延时调用
	# ----------------------------------------------------------------
	def delayCall( self, delay, methodName, *args ) :
		"""
		延迟调用某个给定函数
		@param		delay	`	:	延时调用时间，单位：秒
		@type		delay		:	float
		@param		methodName	:	调用函数名
		@type		methodName	:	str
		@param		args		:	所调用函数的参数列表，注意要和调用函数的参数对应
		@type		args		:	int/float/str/double
		@rtype					:	int
		"""
		timerID = self.addTimer( delay, 0, ECBExtend.DELAY_CALL_TIMER_CBID )
		self.setTemp( "delayCallMethodName" + str( timerID ), methodName )
		self.setTemp( "delayCallParameter" + str( timerID ), args )
		return timerID

	def onDelayCallTimer( self, timerID, cbID ) :
		"""
		与delayCall对应，时间到后调用给定函数
		@param		timerID	:	使用addTimer()方法时产生的标志，由onTimer()被触发时自动传递进来
		@type		timerID	:	int
		@param		cbID	:	当前方法所代表的编号，同样由onTimer()被触发时自动传递进来
		@type		cbID	:	int
		"""
		methodName = self.popTemp( "delayCallMethodName" + str( timerID ) )
		args = self.popTemp( "delayCallParameter" + str( timerID ) )
		method = getattr( self, methodName )
		method( *args )

	def showQuestLog( self, questID ) :
		"""
		通知客户端打开指定任务的任务日志
		@param		questID:	任务ID
		@type		questID:	uint32
		"""
		self.client.onShowQuestLog( questID )


	# ----------------------------------------------------------------
	# space场景相关
	# ----------------------------------------------------------------
	def onLeaveSpace_( self ):
		"""
		玩家离开空间
		作用：玩家离开一个空间，此功能会被触发。
		"""
		if self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:	# 如果角色在跳舞状态，则停止跳舞
			self.stopDance( self.id )

		SpaceFace.onLeaveSpace_( self )
		self.cmi_onLeaveSpace()

	def onEnterSpace_( self ):
		"""
		define
		玩家进入空间
		作用：告诉玩家进入了一个新空间。
		"""
		self.removeTemp( "isTeleporting" )

		SpaceFace.onEnterSpace_( self )
		RoleQuestInterface.onEnterSpace_( self )
		RoleQuizGame.onEnterSpace_( self )		# 17:09 2009-4-27,wsf
		CopyMatcherInterface.cmi_onEnterSpace( self )

		#如果角色是死亡跳转，需做复活处理
		dieTeleport = self.queryTemp( "role_die_teleport", False )
		if dieTeleport:
			self.removeTemp( "role_die_teleport" )
			self.tombPunish()
			self.changeState( csdefine.ENTITY_STATE_FREE )
			self.setHP( self.HP_Max )
			self.setMP( self.MP_Max )

		#增加玩家离开陷阱是否异常判断 add by wuxo 2012-2-16
		sid = self.queryTemp("LeaveQuestTrapError",0)
		if sid != 0:
			self.client.hideQuestTrapTip( sid )#关闭提示信息
			self.removeTemp("LeaveQuestTrapError")

		#此地图不允许召唤小精灵 add by wuxo 2011-12-7
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canConjureEidolon:
			if self.callEidolonCell() or self.queryTemp( "autoWithdrawEidolon", False ):#modify by wuxo 2011-12-1		#by cwl 如果传送前小精灵处于自动收回状态则也要设置temp，以便跳到其他地图时能重新招出。
				self.withdrawEidolon( self.id )
				self.setTemp("eidolonState",True)#小精灵状态记录以便召唤
		else:
			if self.queryTemp("eidolonState",False) and not self.queryTemp( "autoWithdrawEidolon", False ):		# 如果处于自动隐藏小精灵状态则不召唤
				self.conjureEidolon( self.id )

		# 此地图禁止召唤宠物
		if not spaceScript.canConjurePet:
			if self.pcg_getActPet():
				self.pcg_withdrawPet( self.id )



	def onEnterArea( self ) :
		"""
		Define Method
		同地图跳转后被调用
		hyw--2008.10.08
		"""
		self.removeTemp( "isTeleporting" )

		dieTeleport = self.queryTemp( "role_die_teleport", False )
		if dieTeleport : #如果角色是死亡跳转，则做以下复活处理
			self.removeTemp( "role_die_teleport" )
			self.tombPunish()
			self.changeState( csdefine.ENTITY_STATE_FREE )
			self.setHP( self.HP_Max )
			self.setMP( self.MP_Max )
		self.client.onEnterAreaFS()

		# 因为在这里跟随跳转的话宠物还没离开角色的AOI范围，
		# 跳转后客户端就没有执行enterworld，所以没有向服务器请求宠物的数据，导致宠物名字消失。
		# 目前宠物的AI里面角色离开宠物过远后宠物会自动跳转过去，所以屏蔽把这里的跳转。
		#actPet = self.pcg_getActPet()
		#if actPet : 						# 如果玩家有出战宠物则通知
		#	self.pcg_teleportPet()			# 则，让其跟随

	def onLeaveArea( self ):
		"""
		Define Method
		同地图跳转前被调用
		hyw--2008.10.08
		"""
		# 未决BUFF
		if self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:	# 如果角色在跳舞状态，则停止跳舞
			self.stopDance( self.id )
		self.spellTarget( csconst.PENDING_SKILL_ID, self.id )
		self.client.onLeaveAreaFS()

	def teleportToSpace( self, position, direction, cellMailBox, dstSpaceID ):
		"""
		作用：传送到指定space，调用玩家自身的功能，让其进入指定空间。
		@type     		position	: vector3
		@param    		position	: 目标位置
		@type    		direction	: vector3
		@param   		direction	: 方向
		@type  			cellMailBox	: MAILBOX
		@param 			cellMailBox	: 用于定位需要跳转的目标space，此mailbox可以是任意的有效的cell mailbox
		"""
		isTeleporting = self.queryTemp( "isTeleporting", False )
		if self.vehicle is not None:
			DEBUG_MSG( "spaceID", self.spaceID, self.getName(), "id", self.id, "vid", self.vehicle.id, self.position, "dst", position, "inTeleporting", isTeleporting )
		else:
			DEBUG_MSG( "spaceID", self.spaceID, self.getName(), "id", self.id, self.position, "dst", position, "inTeleporting", isTeleporting )

		if self.queryTemp( "isTeleporting", False ): return
		self.setTemp( "isTeleporting", True )
		# 如果在吟唱则中断吟唱
		if self.attrIntonateSkill:
			self.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )
		# 如果在钓鱼则取消钓鱼
		if self.currentModelNumber == "fishing":
			self.end_body_changing( self.id, "" )
		SpaceFace.teleportToSpace( self, position, direction, cellMailBox, dstSpaceID )

	def tagTransport( self, spaceSign ):
		"""
		标记传送器标记
		@param spaceSign: 场景标志
		@type  spaceSign: int
		"""
		self.transportHistory = self.transportHistory | spaceSign

	def onGotoSpaceBefore( self, spaceName ):
		"""
		传送前调用
		"""
		pass

	def beforeEnterSpaceDoor( self, destPosition, destDirection ):
		"""
		进入传送门之前做点事情
		"""
		RoleQuestInterface.beforeEnterSpaceDoor( self, destPosition, destDirection )
		Team.beforeEnterSpaceDoor( self, destPosition, destDirection )

	# ----------------------------------------------------------------
	# 玩家模型相关
	# ----------------------------------------------------------------
	def resetEquipModel( self, order, newItem ):
		"""
		重设玩家的模型相关
		"""
		# 发型和脸部模型单独处理
	# 这个判断移动到客户端去做,以防产生变身时客户端对装备的刷新的异常
	#	if self.actionSign( csdefine.ACTION_FORBID_CHANGE_MODEL ):
	#		return

		if order == ItemTypeEnum.CEL_FASHION1:
			if newItem == None: data = 0
			else: data = newItem.getFDict()
			self.fashionNum = data
		elif order == ItemTypeEnum.CEL_TALISMAN:
			if newItem == None: data = 0
			else: data = newItem.getFDict()
			self.talismanNum = data
		elif order == ItemTypeEnum.CEL_BODY:
			if newItem is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = newItem.getFDict()
			self.bodyFDict = data
		elif order == ItemTypeEnum.CEL_BREECH:
			if newItem is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = newItem.getFDict()
			self.breechFDict = data
		elif order == ItemTypeEnum.CEL_VOLA:
			if newItem is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = newItem.getFDict()
			self.volaFDict = data
		elif order == ItemTypeEnum.CEL_FEET:
			if newItem is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = newItem.getFDict()
			self.feetFDict = data
		elif order == ItemTypeEnum.CEL_LEFTHAND:
			# 盾牌是防具...
			if newItem is None:
				self.lefthandFDict = { "modelNum" : 0, "iLevel" : 0, "stAmount" : 0 }
			else:
				self.lefthandFDict = {	"modelNum"		: newItem.model(),
										"iLevel"		: newItem.getIntensifyLevel(),
										"stAmount"		: newItem.getBjExtraEffectCount(),
										}
		elif order == ItemTypeEnum.CEL_RIGHTHAND:
			if newItem is None:
				data = { "modelNum" : 0, "iLevel" : 0, "stAmount" : 0 }
			else:
				data = newItem.getFDict()
			profession = self.getClass()
			if profession == csdefine.CLASS_ARCHER:
				self.lefthandFDict = data
			elif profession == csdefine.CLASS_SWORDMAN:
				if newItem is None or newItem.getType() == ItemTypeEnum.ITEM_WEAPON_TWOSWORD :
					self.lefthandFDict = self.righthandFDict = data
				elif newItem.getType() == ItemTypeEnum.ITEM_WEAPON_SWORD1:
					self.righthandFDict = data
					self.lefthandFDict = { "modelNum" : 0, "iLevel" : 0, "stAmount" : 0 }
			else:
				self.righthandFDict = data

	def resetWAppendState( self ):
		"""
		重设武器悬挂开关
		"""
		try:
			target = BigWorld.entities[self.targetID]
		except:
			target = None
		if target is not None:
			if self.queryRelation( target ) == csdefine.RELATION_ANTAGONIZE:
				if self.weaponAppendState != 0:
					self.weaponAppendState = 0
		else:
			if self.getState() != csdefine.ENTITY_STATE_FIGHT:
				if self.weaponAppendState != 1:
					self.weaponAppendState = 1

	def changeTargetID( self, srcEntityID, targetID ):
		"""
		玩家当前目标ID改变
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ): return
		if self.targetID == targetID: return
		self.targetID = targetID
		#self.resetWAppendState()

	def changeHeadAbout( self, srcEntityID, newHairID, newFaceID, newHeadTextureID ):
		"""
		Exposed method
		重新设置角色发型、脸、头像
		"""
		if self.hairNumber != newHairID: self.hairNumber = newHairID
		if self.faceNumber != newFaceID: self.faceNumber = newFaceID
		if self.headTextureID != newHeadTextureID: self.headTextureID = newHeadTextureID

	# ----------------------------------------------------------------
	# 玩家复活相关
	# ----------------------------------------------------------------
	def onRevive( self ):
		"""
		玩家在复活后做的一些处理
		"""
		# 重新计算pk状态
		self.onPkAttackChangeCheck()
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.getCurrentSpaceBase().cell.onRoleRevive( self.databaseID )

	def revive( self, srcEntityID, reviveType ):
		"""
		Exposed method
		复活在复活点
		"""
		if not self.hackVerify_( srcEntityID ) : return
		# 检查玩家是否死亡
		if self.getState() != csdefine.ENTITY_STATE_DEAD:
			return

		self.setTemp( "role_die_teleport", True ) #设置临时死亡标记

		if reviveType == csdefine.REVIVE_ON_CITY:
			self.reviveOnCity()
		elif reviveType == csdefine.REVIVE_ON_SPACECOPY:
			spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			spaceType = self.getCurrentSpaceType()
			if spaceType == csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN:
				self.getCurrentSpaceBase().cell.onRoleRelive( self.base, self.tong_dbID )
			elif spaceType == csdefine.SPACE_TYPE_JUE_DI_FAN_JI:
				self.getCurrentSpaceBase().cell.onRoleRelive( self.base, self.databaseID )
			elif spaceType == csdefine.SPACE_TYPE_CITY_WAR_FINAL:
				self.getCurrentSpaceBase().cell.onRoleRelive( self.base, self.tong_dbID )
			elif spaceType == csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN:
				self.getCurrentSpaceBase().cell.onRoleRelive( self.base, self.getCamp() )
			elif spaceType == csdefine.SPACE_TYPE_WM:
				g_objFactory.getObject(spaceLabel).onRoleRevive(self)
			else:
				pos = g_SpaceCopyReviveCfg.getSpaceRevivePos( self, spaceLabel, spaceType )
				if pos:
					self.position = pos
					self.reviveOnOrigin()
				else:
					self.reviveOnCity()

		elif reviveType == csdefine.REVIVE_PRE_SPACE:
			self.revivePreSpace()

	def onReviveTimer( self, timerID, cbID ):
		"""
		ROLE_REVIVE_TOMB_TIMER
		"""
		self.dieReviveDoSth( self.id, csdefine.REVIVE_ON_TOMB )

	def dieReviveDoSth( self, srcEntityID, reviveType ):
		"""
		Exposed method.
		死亡复活时，有可能需要做一些特殊的事情
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if self.queryTemp( "role_die_to_revive_type" ) != None:
			reviveType = self.queryTemp( "role_die_to_revive_type" )
		self.revive( self.id, reviveType )
		if reviveType == csdefine.REVIVE_ON_TOMB:
			spellID = self.queryTemp('team_compete_revive_spell', 0 )
			if spellID != 0:
				self.spellTarget( spellID, self.id )
			self.removeTemp( 'team_compete_revive_spell' )
		self.removeTemp( "role_die_to_revive_type" )

		self.onRevive()

	def setRevivePos( self, spaceName, position, direction ):
		"""
		Define Method
		NPC设置回城复活点
		"""
		self.reviveSpace = spaceName
		self.revivePosition = tuple( position )
		self.reviveDirection = tuple( direction )
		self.questSetRevivePos( spaceName )

	def setCurPosRevivePos( self ):
		"""
		Define Method
		对应：revivePreSpace
		"""
		self.setTemp( "enterPreSpaceType", self.spaceType )
		self.setTemp( "enterPreSpacePos", tuple( self.position ) )
		self.setTemp( "enterPreSpaceDirection", tuple( self.direction ) )

	def tombPunish( self ):
		"""
		回复活点惩罚。
		"""
		pass

	def reviveOnTomb( self ):
		"""
		墓地复活
		"""
		# 搜索离玩家最近的一个墓地点复活
		try:
			tomb = g_spacedata["tomb"][self.spaceType]
		except:
			ERROR_MSG("revive error!, not has tomb.", self.spaceType )
			return
		l = len( tomb )
		# 无复活点
 		if l == 0:
			ERROR_MSG("revive error!, not has tomb.", self.spaceType )
			return
		# 复活
		dict = None
		if l == 1:
			# 单个复活点比如说副本
			dict = tomb[0]
		else:
			# 取最近的复活点复活
			near = None
			for info in tomb:
				distance = self.position.flatDistTo( Math.Vector3( info["position"] ) )
				if near == None or distance < near:
					near = distance
					dict = info
		# 空间跳越
		if dict != None:
			self.setTemp( "ignoreFullRule", True )	# 设置一个标记， 在多线地图中忽略满线的规则， 避免在副本中无法被复活的现象
			self.gotoSpace( dict["name"], dict["position"], dict["direction"] )
			self.removeTemp( "ignoreFullRule" )
		# 复活惩罚、改变状态和满血满魔移到了onEnterArea函数里面,因为在这里的话玩家会看到角色回血和站起来再传送

		self.onRevive()

	def reviveOnOrigin( self, hpPercent = 1.0, mpPercent = 1.0 ):
		"""
		原地复活
		"""
		#在玩家死亡的地方复活
		if self.queryTemp( "role_die_to_revive_cbid", -1 ) != -1:							#取消复活倒计时timer
			self.cancel( self.queryTemp( "role_die_to_revive_cbid" ) )
		self.tombPunish()
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max*hpPercent )
		self.setMP( self.MP_Max*mpPercent )

		self.onRevive()

		self.reTriggerNearTrap()


	def reviveOnCity( self ):
		"""
		回城复活。
		"""
		# 通过与NPC记录点复活
		self.setTemp( "ignoreFullRule", True )	# 设置一个标记， 在多线地图中忽略满线的规则， 避免在副本中无法被复活的现象
		self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )
		self.removeTemp( "ignoreFullRule" )
		self.onRevive()
		# 复活惩罚、改变状态和满血满魔移到了onEnterArea函数里面,因为在这里的话玩家会看到角色回血和站起来再传送
		self.TDB_onReviveOnCity()

	def reviveActivity( self ):
		# define method
		# 活动空血空蓝复活
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( 0 )
		self.setMP( 0 )
		self.onRevive()

	def revivePreSpace( self ):
		"""
		在进入副本的前一个地图复活
		"""
		enterPreSpaceType = self.queryTemp( "enterPreSpaceType", self.reviveSpace )
		enterPreSpacePos = self.queryTemp( "enterPreSpacePos", self.revivePosition )
		enterPreSpaceDirection = self.queryTemp( "enterPreSpaceDirection", self.reviveDirection )
		self.gotoSpace( enterPreSpaceType, enterPreSpacePos, enterPreSpaceDirection )
		self.onRevive()

	def reviveOnSpace(self, space_label, position, direction):
		"""
		在指定地图复活
		"""
		DEBUG_MSG("%s revive on space %s %s %s" % (self.getName(), space_label, position, direction))
		# 设置一个标记， 在多线地图中忽略满线的规则， 避免在副本中无法被复活的现象
		self.setTemp( "ignoreFullRule", True )
		self.gotoSpace(space_label, position, direction)
		self.removeTemp( "ignoreFullRule" )

		self.onRevive()

	# ----------------------------------------------------------------
	# 神机匣功能
	# 材料合成、装备打孔、装备炼化、装备镶嵌、装备强化、装备改造、装备绑定。
	# ----------------------------------------------------------------
	def doCasketFunction( self, srcEntityID, functionIndex ):
		"""
		Exposed method
		# 执行神机匣功能
		@param functionIndex: 神机匣功能索引
		@type  functionIndex: UINT8
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.doCasketFucntionInterface( functionIndex )

	def doSpecialCompose( self, srcEntityID, idx ):
		"""
		Exposed method
		# 制作卷合成
		@param idx: 配方索引
		@type  idx: UINT8
		"""
		if not self.hackVerify_( srcEntityID ) :
			return False

		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#获得神机匣的使用次数
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return
		if self.specialCompose( idx ):
			#神机匣次数减1
			useDegree -= 1
			kitCasketItem.setUseDegree( useDegree )
			self.client.onUpdateUseDegree( useDegree )

	def stuffCompose( self, srcEntityID, baseAmount ):
		"""
		Exposed method
		材料合成
		@param baseAmount: 合成基数
		@type  baseAmount: int
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) :
			self.client.unLockCasket()
			return False
		self.stuffComposeInterface( baseAmount )

	def doEquipIntensify( self, srcEntityID, uids ):
		"""
		Exposed method
		材料合成
		@param uids: 物品的uid
		@type  baseAmount: list
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) :
			return
		if self.iskitbagsLocked():
			#提示 背包已经锁定
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#获得神机匣的使用次数
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return
		if self.equipIntensify( uids ):
			#神机匣次数减1
			useDegree -= 1
			kitCasketItem.setUseDegree( useDegree )
			self.client.onUpdateUseDegree( useDegree )

	# ----------------------------------------------------------------
	# 装备制造
	# ----------------------------------------------------------------
	def equipMake( self, srcEntityID, makeItemID, orders ):
		"""
		Exposed method
		装备制造
		@param makeItemID	: 要制造装备的ID
		@type  makeItemID	: ITEM_ID
		@param orders		: array of Uint8
		@type  orders		: order 列表
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) : return
		INFO_MSG( "equipMake srcEntityID : %i"%srcEntityID )
		self.equipMakeIntereface( makeItemID, orders )

	def createDynamicItem( self, itemID ):
		"""
		role 上的创建物品接口
		@param itemID	:	物品ID
		@type itemID	:	ITEM_ID
		@return None/inherit CItemBase instance
		"""
		return items.instance().createDynamicItem( itemID )

	# ----------------------------------------------------------------
	# CombatUnit函数重载
	# ----------------------------------------------------------------
	def calcStrengthBase( self ):
		"""
		计算力量基础值
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].strength
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].strength_value
		self.strength_base = v + v_value * ( self.level - 1 )

	def calcDexterityBase( self ):
		"""
		计算敏捷基础值
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].dexterity
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].dexterity_value
		self.dexterity_base = v + v_value * ( self.level - 1 )

	def calcIntellectBase( self ):
		"""
		计算智力基础值
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].intellect
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].intellect_value
		self.intellect_base = v + v_value * ( self.level - 1 )

	def calcCorporeityBase( self ):
		"""
		计算体质基础值
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].corporeity
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].corporeity_value
		self.corporeity_base = v + v_value * ( self.level - 1 )

	def calcHPCureSpeed( self ):
		"""
		计算生命恢复速度
		角色的隐藏属性，决定角色每3秒可以恢复的生命数值。战斗时无效。数值读表。
		"""
		self.HP_regen_base = int( 3.0 * self.corporeity * 0.03 + 11 )
		RoleEnmity.calcHPCureSpeed( self )

	def calcMPCureSpeed( self ):
		"""
		角色的隐藏属性，决定角色每3秒可以恢复的法力数值。战斗时无效。数值读表。
		"""
		self.MP_regen_base = int( 3.0 * self.intellect * 0.03 + 15 )
		RoleEnmity.calcMPCureSpeed( self )

	# ----------------------------------------------------------------
	def onJumpNotifyFC( self, srcEntityID, jumpMask ):
		"""
		Exposed method
		向服务器请求所有客户端jump动作的广播消息－供客户端调用
		"""
		if self.id != srcEntityID: return

		jumpTime = jumpMask & csdefine.JUMP_TIME_MASK

		# 掉落伤害= 角色当前生命上限值 x （掉落距离 – 掉落伤害高度）/50
		if jumpTime == csdefine.JUMP_TIME_UP1:
			self.fallDownHeight = self.position.y
		if jumpTime == csdefine.JUMP_TIME_DOWN:
			self.fallDownHeight = self.position.y
			# 不允许吟唱
			#self.actCounterInc( csdefine.ACTION_FORBID_INTONATING )
		elif jumpTime == csdefine.JUMP_TIME_END:
			# 落地后解除不许吟唱的限制
			#self.actCounterDec( csdefine.ACTION_FORBID_INTONATING )
			self.__receiveFallDownDmg()
		elif jumpTime == csdefine.JUMP_TIME_UP2:
			#播放2段跳
			if self.vehicleModelNum == 0 and (self.hasSkill( csdefine.JUMP_UP2_SKILLID ) or self.hasSkill( csdefine.JUMP_UP3_SKILLID )) and self.energy >= csdefine.JUMP_UP2_ENERGY:
				self.calEnergy( - csdefine.JUMP_UP2_ENERGY )
			else: #进入下落
				self.fallDownHeight = self.position.y
				#self.actCounterInc( csdefine.ACTION_FORBID_INTONATING )
				jumpMask = csdefine.JUMP_TYPE_LAND |csdefine.JUMP_TIME_DOWN
		elif jumpTime == csdefine.JUMP_TIME_UP3:
			#播放2段跳
			if self.vehicleModelNum == 0 and self.hasSkill( csdefine.JUMP_UP3_SKILLID ) and self.energy >= csdefine.JUMP_UP3_ENERGY:
				self.calEnergy( - csdefine.JUMP_UP3_ENERGY )
			else: #进入下落
				self.fallDownHeight = self.position.y
				#self.actCounterInc( csdefine.ACTION_FORBID_INTONATING )
				jumpMask = csdefine.JUMP_TYPE_LAND |csdefine.JUMP_TIME_DOWN
		# 不需要通知自己，只需要通知自己周围的玩家即可
		self.planesOtherClients( "onJumpNotifyFS", ( jumpMask, ) )

	def __receiveFallDownDmg( self ):
		"""
		掉落伤害计算
		"""
		damage = int( self.HP_Max * ( self.fallDownHeight - self.position.y - Const.ROLE_DROP_DAMAGE_HEIGHT ) / 50 )
		if damage > 0:
			self.HP = max( 0, self.HP - damage )
			if self.HP == 0:
				self.MP = 0
				self.die(0)
			else:				# 没摔死就回血
				self.revertCheck()
		self.fallDownHeight = 0.0

	def onFlyJumpUpNotifyFC( self, srcEntityID ):
		"""
		Exposed method
		向服务器请求所有客户端j飞行高度上升的广播消息　－　供客户端调用
		"""
		if self.id != srcEntityID:
			return
		if not self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		p = self.position
		if p.y >= 100:p.y = 100.0			# 上升上限
		self.position = (p.x,p.y+1.8,p.z)		# 平均每次上升高度等于一次跳跃高度
		self.planesOtherClients( "onFlyJumpUpNotifyFS", () )

	def getBoundingBox( self ):
		"""
		virtual method.
		返回代表自身的bounding box的长、高、宽的Vector3实例；
		如果自身的模型有被缩放过，需要提供缩放后的值。

		@return: Vector3
		"""
		# 为了使判断一致，主角的bounding box服务器与客户端使用相同的值，
		# 如果有必要，可以考虑根据不同的职业使用不同的值
		# 将来如果有放大模型的技能，可能需要根据实际情况决定是否加入放大倍率
		if self.vehicle:
			return self.vehicle.getBoundingBox()
		if VehicleHelper.getCurrVehicleID( self ):
			return csconst.VEHICLE_MODEL_BOUND
		return csconst.ROLE_MODEL_BOUND

	def recordLastSpaceLineData( self, lineNumber, maxLine ):
		"""
		define method.
		记录最后一次进入分线地图的线信息
		"""
		self.lastSpaceLineNumber = lineNumber
		self.lastSpaceMaxLine = maxLine

	def createNPCObjectFormBase( self, spaceKey, npcID, position, direction, state ):
		"""
		define method
		从base上在制定的space中创建一个非玩家控制对象

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# 这个__lineNumber__是提供线控制的， 比如：如果使用者在外部制定了一条要刷的线，那么某个副本如果有这个线的话
		# 这个怪物将被刷到指定的线上， 如果没有指定线， 将刷到玩家所记录的最后一次进入的线的目的space。
		if state.get( "_lineNumber_", 0 ) == 0:
			state[ "_lineNumber_" ] = self.lastSpaceLineNumber
		self.getSpaceManager().createNPCObjectFormBase( spaceKey, npcID, position, direction, state )

	def createCellNPCObjectFormBase( self, spaceKey, npcID, position, direction, state ):
		"""
		define method
		从base上在制定的space中创建一个非玩家控制对象

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# 这个__lineNumber__是提供线控制的， 比如：如果使用者在外部制定了一条要刷的线，那么某个副本如果有这个线的话
		# 这个怪物将被刷到指定的线上， 如果没有指定线， 将刷到玩家所记录的最后一次进入的线的目的space。
		if state.get( "_lineNumber_", 0 ) == 0:
			state[ "_lineNumber_" ] = self.lastSpaceLineNumber
		self.getSpaceManager().createCellNPCObjectFormBase( spaceKey, npcID, position, direction, state )

	# ----------------------------------------------------------------
	# 引路蜂
	# ----------------------------------------------------------------
	def flyToNpc( self, srcEntityID, npcID, questID, order ):
		"""
		Exposed Method
		使用引路蜂到达指定NPC
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# 不允许使用引路蜂的各种状态
		cantFlyings = [ ( csdefine.ENTITY_STATE_FIGHT, csstatus.SKILL_USE_ITEM_WHILE_FIGHTING ),# 战斗
						( csdefine.ENTITY_STATE_DEAD, csstatus.SKILL_USE_ITEM_WHILE_DEAD ),		# 死亡
						( csdefine.ENTITY_STATE_VEND, csstatus.ROLE_VEND_CANNOT_FLY ),			# 摆摊
						( csdefine.ENTITY_STATE_RACER, csstatus.ROLE_RACE_CANNOT_FLY ),			# 比赛
						( csdefine.ENTITY_STATE_QUIZ_GAME, csstatus.ROLE_QUIZ_CANNOT_FLY ),		# 知识问答
					]
		for (state, infoMessage) in cantFlyings:
			if ( state == self.getState() ):
				self.statusMessage( infoMessage )
				return

		if not self.controlledBy:	# 玩家失去控制时不允许使用
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#携带跑商物品，不能使用引路蜂
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# 如果有法术禁咒buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#在监狱中不能传送
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			return self.statusMessage( csstatus.SPACE_MISS_LEAVE_PRISON )

		if self.getCurrentSpaceType() in [ csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN, csdefine.SPACE_TYPE_TOWER_DEFENSE, csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN ]:
			return self.statusMessage( csstatus.SPACE_COPY_CANNOT_USE_ITEM_TELEPORT )

		if self.vehicle is not None and self.vehicle.isSlaveDart():
			self.statusMessage( csstatus.TRANSPORT_FORBID_ON_DART )
			return

		item = self.getItem_( order )
		if item is None:
			return
		if item.id not in [ 50101002, 50101003 ] :
			return

		# 加入物品、背包冻结、锁定状态的影响 by姜毅
		if item.isFrozen(): return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		if self.getState() == csdefine.ENTITY_STATE_CHANGING:
			# 使用引路蜂要取消变身状态
			self.changeState( csdefine.ENTITY_STATE_FREE )

		# 目标坐标x,z随机偏移量
		x = random.randint( -1, 1 )
		z = random.randint( -1, 1 )

		if npcID in g_NPCsPosition:	#如果是普通NPC
			npcPosition = g_NPCsPosition[ npcID ]
			if npcPosition[ "fixed" ]:	# 如果位置是确定的
				x = 0
				z = 0

			self.gotoSpace( npcPosition['spaceLabel'], Math.Vector3( npcPosition['position'] ) +  Math.Vector3( x, 0, z ), (0,0,0) )

		elif questID and self.questsTable and self.questsTable.has_quest( questID ) and \
			self.getQuest( questID ).getType() == csdefine.QUEST_TYPE_POTENTIAL:
			#如果是潜能副本NPC, 取出space id和随即生成的那个坐标
			lineNumber = self.questsTable[ questID ].query( "lineNumber", -1 )
			spaceId = self.questsTable[ questID ].query( "dest_space_id", "" )
			npcPos = self.questsTable[ questID ].query( "des_position", ( 0, 0, 0 ) )
			posX, posY, posZ = npcPos
			posX += x
			posZ += z
			if lineNumber > 0:
				self.gotoSpaceLineNumber( spaceId, lineNumber, (posX, posY, posZ), (0,0,0) )
			else:
				self.gotoSpace( spaceId, (posX, posY, posZ), (0,0,0) )
		else:
			return
		self.removeItem_( order, 1, csdefine.DELETE_ITEM_USEFLY )	#移除掉引路蜂
		self.client.onUseFlyItem()

	# ----------------------------------------------------------------
	# 引路蜂
	# ----------------------------------------------------------------
	def flyToSpacePosition( self, srcEntityID, treasureOrder, order ):
		"""
		Exposed Method
		使用引路蜂到达指定地图、位置
		"""
		if not self.hackVerify_( srcEntityID ) : return
		#战斗状态限制用引路蜂
		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			self.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )
			return
		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			self.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_DEAD )
			return
		if self.getState() == csdefine.ENTITY_STATE_QUIZ_GAME:
			self.statusMessage( csstatus.ROLE_QUIZ_CANNOT_FLY )
			return
		if  self.getState() == csdefine.ENTITY_STATE_VEND: #
			return
		if self.getState() == csdefine.ENTITY_STATE_CHANGING:
			self.changeState( csdefine.ENTITY_STATE_FREE )
		if not self.controlledBy:	# 玩家失去控制时不允许使用
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#携带跑商物品，不能使用引路蜂
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# 如果有法术禁咒buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#在监狱中不能传送
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			return self.statusMessage( csstatus.SPACE_MISS_LEAVE_PRISON )

		if self.getCurrentSpaceType() in [ csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN, csdefine.SPACE_TYPE_TOWER_DEFENSE, csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN ]:
			return self.statusMessage( csstatus.SPACE_COPY_CANNOT_USE_ITEM_TELEPORT )

		if self.vehicle is not None and self.vehicle.isSlaveDart():
			self.statusMessage( csstatus.TRANSPORT_FORBID_ON_DART )
			return

		treasureItem = self.getItem_( treasureOrder )
		if ( treasureItem is None ) or ( treasureItem.id != 60101005 ):
			return

		item = self.getItem_( order )
		if item is None:
			return
		if item.id not in [ 50101002, 50101003 ] :
			return

		# 加入物品、背包冻结、锁定状态的影响 by姜毅
		if item.isFrozen(): return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		treasureSpace = treasureItem.query( "treasure_space", "" )		# 取出藏宝图中的地图信息
		treasurePosStr = treasureItem.query( "treasure_position", None )# 取出藏宝图中的坐标信息
		treasurePos = eval( treasurePosStr )
		self.gotoSpace( treasureSpace, treasurePos, (0,0,0) )

		self.removeItem_( order, 1, csdefine.DELETE_ITEM_USEFLY  )	#移除掉引路蜂
		self.client.onUseFlyItem()


	def flyToPlayerPosition( self, srcEntityID, space, lineNumber, position, order ):
		"""
		Exposed Method
		飞到玩家位置
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# 不允许使用引路蜂的各种状态
		cantFlyings = [ ( csdefine.ENTITY_STATE_FIGHT, csstatus.SKILL_USE_ITEM_WHILE_FIGHTING ),# 战斗
						( csdefine.ENTITY_STATE_DEAD, csstatus.SKILL_USE_ITEM_WHILE_DEAD ),		# 死亡
						( csdefine.ENTITY_STATE_VEND, csstatus.ROLE_VEND_CANNOT_FLY ),			# 摆摊
						( csdefine.ENTITY_STATE_RACER, csstatus.ROLE_RACE_CANNOT_FLY ),			# 比赛
						( csdefine.ENTITY_STATE_QUIZ_GAME, csstatus.ROLE_QUIZ_CANNOT_FLY ),		# 知识问答
					]
		for (state, infoMessage) in cantFlyings:
			if ( state == self.getState() ):
				self.statusMessage( infoMessage )
				return

		if not self.controlledBy:	# 玩家失去控制时不允许使用
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#携带跑商物品，不能使用引路蜂
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# 如果有法术禁咒buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#在监狱中不能传送
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			return self.statusMessage( csstatus.SPACE_MISS_LEAVE_PRISON )

		if self.getCurrentSpaceType() in [ csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN, csdefine.SPACE_TYPE_TOWER_DEFENSE, csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN ]:
			return self.statusMessage( csstatus.SPACE_COPY_CANNOT_USE_ITEM_TELEPORT )

		if self.vehicle is not None and self.vehicle.isSlaveDart():
			self.statusMessage( csstatus.TRANSPORT_FORBID_ON_DART )
			return

		item = self.getItem_( order )
		if item is None:
			return
		if item.id not in [ 50101002, 50101003 ] :
			return

		# 加入物品、背包冻结、锁定状态的影响 by姜毅
		if item.isFrozen(): return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		if self.getState() == csdefine.ENTITY_STATE_CHANGING:
			# 使用引路蜂要取消变身状态
			self.changeState( csdefine.ENTITY_STATE_FREE )

		if lineNumber > 0:
			self.gotoSpaceLineNumber( space, lineNumber, position, (0,0,0) )
		else:
			self.gotoSpace( space, position, (0,0,0) )

		self.removeItem_( order, 1, csdefine.DELETE_ITEM_USEFLY )	#移除掉引路蜂
		self.client.onUseFlyItem()

	def onRequestCell( self, cellMailbox, baseMailbox ):
		"""
		创建副本空间 entity的cell返回
		"""
		pass

	def onAutoTalk( self, controllerID, userData ):
		"""
		"""
		if self.queryTemp( "talkID", "" ) != "":
			self.gossipWith( self.id, self.queryTemp( "talkNPCID", 0 ), self.queryTemp( "talkID", "" ) )
			self.removeTemp( "talkID" )
			#self.removeTemp( "talkNPCID" )

	def delayTeleport( self, srcEntityID, spaceName, pos, result ):
		"""
		exposed method.
		延迟传送，开始传送
		"""
		if not self.hackVerify_( srcEntityID ): return
		if self.getState() == csdefine.ENTITY_STATE_DEAD: return  # 死亡状态传送失败
		if not result: return
		self.gotoSpace( spaceName, pos, (0,0,0) )

	#-------------------------观察对方 相关代码------------------
	def getTargetEspialAttribute( self , observer):
		"""
		发送自己的部分属性给观察者
		@param observer	: 观察者的MAILBOX
		@type  observer	: MAILBOX
		"""
		observer.client.showTargetAttribute( self.id )

	def	getTargetEspialEquip( self, observer, BeginPos, GetNumber ):
		"""
		获取指定的几个位置的装备
		"""
		targetEquips = self.getItems(csdefine.KB_EQUIP_ID)				#装备的信息
		Items = []
		for	i in xrange(GetNumber):
			try:
				item = targetEquips[BeginPos + i]
			except IndexError: #表示已经没有可以取的了
				observer.client.showTargetEquip( Items , True)
				return
			Items.append( item)
		observer.client.showTargetEquip( Items , False)

	def getTargetAttribute( self , srcEntityID, targetID):
		"""
		Exposed method
		获取要观察的玩家的部分数据信息
		@param srcEntityID	: 玩家自己的ID
		@type  makeItemID	: OBJECT_ID
		@param targetID		: 被观察的对象的ID
		@type  targetID		: OBJECT_ID
		@return None
		"""
		if srcEntityID != self.id: #判断是否是自己的客户端在请求
			return

		target = BigWorld.entities.get( targetID )
		if target is None: #没有这个玩家
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
			return
		target.getTargetEspialAttribute( self ) #获取对方玩家的部分属性

	def getTargetEquip(self, srcEntityID, targetID, BeginPos, GetNumber):
		"""
		Exposed method
		获取要观察的玩家装备信息
		@param srcEntityID	: 玩家自己的ID
		@type  makeItemID	: OBJECT_ID
		@param targetID		: 被观察的对象的ID
		@type  targetID		: OBJECT_ID
		@param BeginPos		: 要获取的装备的开始位置
		@type  BeginPos		: INT
		@param GetNumber	: 要获取的装备的数量
		@type  GetNumber	: INT
		@return None
		"""
		if srcEntityID != self.id: #判断是否是自己的客户端在请求
			return

		target = BigWorld.entities.get( targetID )
		if target is None: #没有这个玩家
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
			return
		target.getTargetEspialEquip( self , BeginPos, GetNumber) #获取对方玩家的部分属性

	def isSunBathing( self ):
		"""
		玩家是否在进行日光浴
		"""
		spaceType = self.getCurrentSpaceType()
		return spaceType == csdefine.SPACE_TYPE_SUN_BATHING

	def gotoRacehorseMap( self, srcEntityID ):
		"""
		Exposed method
		进入赛马地图
		"""
		if srcEntityID != self.id: #判断是否是自己的客户端在请求
			return
		BigWorld.globalData['RacehorseManager'].enterRacehorseMap( self.base, self.databaseID )


	def onTongRaceCreateSuccessed( self ):
		"""
		Define method
		"""
		for iMember in self.getTongOnlineMember():
			iMember.client.startTongRacehorse()

	def tong_onChanged( self ):
		"""
		角色帮会改变通知其他关系
		"""
		RoleRelation.tong_onChanged( self )
		TongInterface.tong_onChanged( self )

	def hasMerchantItem( self ):
		for iItem in self.getAllItems():
			if iItem.reqYinpiao() != 0:
				return True
		return False


	def gotoSpaceTianguan( self, spaceType, position, direction ):
		"""
		define method
		"""
		self.setTemp( "tianguan_spaceType", spaceType )
		self.setTemp( "tianguan_position", position )
		self.setTemp( "tianguan_direnction", direction )
		self.addTimer( 1.0, 0, ECBExtend.TIANGUAN_MENBER_GOIN )


	def enterTianguan( self, controllerID, userData ):
		"""
		"""
		spaceType = self.queryTemp( "tianguan_spaceType", "" )
		position = self.queryTemp( "tianguan_position", (0,0,0) )
		direction = self.queryTemp( "tianguan_direnction", (0,0,0) )

		self.gotoSpace( spaceType, position, direction )


	def getRangeBias( self ):	# wsf add,16:23 2008-12-30
		"""
		获得不同entity的技能释放偏移值，模板方法

		偏移量仅对于在客户端触发释放技能的entity有意义，此类entity目前只有角色。
		"""
		return csconst.ATTACK_RANGE_BIAS


	# ----------------------------------------------------------------
	#物品相关处理（拾取物品、获得任务物品等）
	# ----------------------------------------------------------------
	def useItemRevive( self,srcEntityID ):
		"""
		Exposed method
		用复活物品复活
		"""
		if self.id != srcEntityID:return
		if not self.state == csdefine.ENTITY_STATE_DEAD:return
		itemID  = 110103001
		items = self.findItemsByIDFromNKCK( itemID )
		if items :
			if self.iskitbagsLocked() :
				self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
				return
			if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_WU_DAO:		# 如果在武道大会中死亡，无法复活
				self.statusMessage( csstatus.WU_DAO_NOT_REVIVE )
				return
			item = items[0]
			item.use( self,self ) #因为use函数里面有调用checkUse进行检查，这里暂不检查，直接使用
			self.removeItem_( item.order,1, csdefine.DELETE_ITEM_USEITEMREVIVE )
			self.reTriggerNearTrap() #原地复活，再次触发30米范围的所有陷阱

	def requestAddItem( self, id, index, item, isQuestItem ):
		"""
		判断是否能加入这个物品或金钱
		"""
		dropBoxEntity = BigWorld.entities.get( id )
		if dropBoxEntity is None: return

		if item.isType( ItemTypeEnum.ITEM_MONEY ):
			if self.gainMoney( item.amount, csdefine.CHANGE_MONEY_REQUESTADDITEM  ):
				dropBoxEntity.receiveItemPickedCB( self.id, index, True, isQuestItem, True, self.databaseID )
			else:
				dropBoxEntity.receiveItemPickedCB( self.id, index, False, isQuestItem, True, 0 )
		else:
			# 根据箱子的掉落类型来判断
			# 如果箱子是怪物爆出来的，那么以怪物爆出方式添加物品
			# 如果箱子是开宝箱爆出来的，那么以开宝箱方式添加物品
			dropType = dropBoxEntity.dropType
			itemGetType = ItemTypeEnum.ITEM_GET_GM
			droperName = ""
			droperSpace = ""
			if dropType == csdefine.DROPPEDBOX_TYPE_MONSTER:
				itemGetType = ItemTypeEnum.ITEM_GET_PICK
				droperName = dropBoxEntity.droperName
				droperSpace = csconst.g_maps_info.get( self.spaceType )
				if droperSpace is None: droperSpace = ""
			elif dropType == csdefine.DROPPEDBOX_TYPE_STROE:
				itemGetType = ItemTypeEnum.ITEM_GET_STROE
			if self.addItemAndRadio( item, itemGetType, droperSpace, droperName , reason = csdefine.ADD_ITEM_REQUESTADDITEM ):
				dropBoxEntity.receiveItemPickedCB( self.id, index, True, isQuestItem, False, self.databaseID )
			else:
				dropBoxEntity.receiveItemPickedCB( self.id, index, False, isQuestItem, False, 0 )

	def requestAddRollItem( self, id, index, item ):
		"""
		define method
		"""
		dropBoxEntity = BigWorld.entities.get( id )
		if dropBoxEntity is None: return
		dropType = dropBoxEntity.dropType
		itemGetType = ItemTypeEnum.ITEM_GET_GM
		droperName = ""
		droperSpace = ""
		if dropType == csdefine.DROPPEDBOX_TYPE_MONSTER:
			itemGetType = ItemTypeEnum.ITEM_GET_PICK
			droperName = dropBoxEntity.droperName
			droperSpace = csconst.g_maps_info.get( self.spaceType )
			if droperSpace is None: droperSpace = ""
		elif dropType == csdefine.DROPPEDBOX_TYPE_STROE:
			itemGetType = ItemTypeEnum.ITEM_GET_STROE
		if self.addItemAndRadio( item, itemGetType, droperSpace, droperName , reason = csdefine.ADD_ITEM_REQUESTADDITEM ):
			dropBoxEntity.receiveAddRollItemCB( self.id, index, True )
		else:
			dropBoxEntity.receiveAddRollItemCB( self.id, index, False )

	def addTasksItem( self, id, className ):
		"""
		define method
		给箱子增加任务物品
		"""
		if not BigWorld.entities.has_key( id ):
			return

		itemList = []
		tempQuestID, tempDict  = self.questsTable.getReadQuestID()
		for questID, items in g_npcQuestDroppedItems.get( className ).iteritems():
			if not questID in tempQuestID : continue
			# the items seen like as [ (rate, itemID, amount), ... ]
			for item in items:
				if random.random() > item[0]: continue
				if tempDict.has_key( questID ):
					questID = tempDict[questID]
				questTasks = self.getQuestTasks( questID )
				if not questTasks.deliverIsComplete( item[1], self ):
					tempItem = g_items.createDynamicItem( item[1], item[2] )
					itemList.append( tempItem )

		if itemList != []:
			BigWorld.entities[id].addQuestItems( self.id, itemList )

	def requestAddQuestItem( self, id, index, item ):
		"""
		define method
		判断是否能加入这个物品
		"""
		player = BigWorld.entities.get( id, None )
		if player is None:
			return
		if self.addItemAndNotify_( item, csdefine.ADD_ITEM_ADDQUESTITEM ):
			BigWorld.entities[id].receiveQuestItemPickedCB( self.id, index, True )
		else:
			BigWorld.entities[id].receiveQuestItemPickedCB( self.id, index, False )

	def pickupItem( self, itemMailbox, itemData ):
		"""
		Define method.
		拾取一个物品Entity

		@param itemMailbox: 被捡取的Item Entity's cell mailbox
		@type  itemMailbox: MAILBOX
		@param    itemData: 物品数据实例
		@type     itemData: ITEM
		@return:            被声明的方法，没有返回值
		"""
		DEBUG_MSG( "itemMailbox = %i, itemData = %s" % (itemMailbox.id,  itemData.id ) )

		self.onPickUpTrigger()

		if self.addItemAndNotify_( itemData, csdefine.ADD_ITEM_PICKUPITEM ):
			itemMailbox.pickupCB( 1 )	# True
		else:
			itemMailbox.pickupCB( 0 )	# False

	def onPickUpTrigger( self ):
		"""
		拾取行为触发。13:37 2008-12-1,wsf
		"""
		self.removeAllBuffByBuffID( csconst.PROWL_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )	# 打断角色的潜行效果buff

	def pickupMoney( self, mailbox, amount ):
		"""
		Define method.
		捡钱

		@param itemMailbox: 被捡取的Item Entity's cell mailbox
		@type  itemMailbox: MAILBOX
		@param      amount: 钱的数量
		@type       amount: UINT32
		"""
		if self.gainMoney( amount, csdefine.CHANGE_MONEY_PICKUPMONEY ):
			mailbox.pickupCB( 1 )	# 成功
		else:
			mailbox.pickupCB( 0 )	# 失败
		return	# the end



	# ----------------------------------------------------------------
	# 法宝
	# ----------------------------------------------------------------
	def addTalismanExp( self, srcEntityID ):
		"""
		Exposed method
		增加法宝经验
		"""
		if srcEntityID != self.id:return
		self.addTalismanExpInterface()

	def addTalismanPotential( self, srcEntityID ):
		"""
		Exposed method
		法宝技能升级
		"""
		if srcEntityID != self.id:return
		self.addTalismanPotentialInterface()

	def updateTalismanGrade( self, srcEntityID ):
		"""
		Exposed method
		提升法宝品质
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.updateTalismanGradeInterface()

	def activateTalismanAttr( self, srcEntityID, uid ):
		"""
		Exposed method
		激活法宝属性
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.activateTalismanAttrInterface( uid )

	def rebuildTalismanAttr( self, srcEntityID, grades, indexs ):
		"""
		Exposed method
		改造法宝属性
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.rebuildTalismanAttrInterface( grades, indexs )

	def reloadTalismanSkill( self, srcEntityID ):
		"""
		Exposed method
		重新刷技能
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.reloadTalismanSkillInterface()

	# --------------------------------------------------------------------------------------------------
	def equipGodWeapon( self, srcEntityID, weaponItem ):
		"""
		Exposed method

		神器炼制
		"""
		self.equipGodWeaponInterface( weaponItem )
	# --------------------------------------------------------------------------------------------------

	def addSunBathCount( self, controllerID, userData ):
		"""
		增加日光浴时间
		"""
		self.updateSunBathCount( 10 )

	def updateSunBathCount( self, value ):
		"""
		增加(或减少)玩家日光浴时间
		"""
		if self.sunBathDailyRecord.sunBathCount < 7200:
			self.sunBathDailyRecord.sunBathCount += value
			if self.sunBathDailyRecord.sunBathCount >= 7200:
				self.onQuestBoxStateUpdate()
		elif value < 0:
			self.sunBathDailyRecord.sunBathCount += value
			if self.sunBathDailyRecord.sunBathCount < 7200:
				self.onQuestBoxStateUpdate()

	def effectStateChanged( self, estate, disabled ):
		"""
		效果改变.13:58 2009-3-13，wsf
			@param estate		:	效果标识(非组合)
			@type estate		:	integer
			@param disabled		:	效果是否生效
			@param disabled		:	bool
		"""
		Team.effectStateChanged( self, estate, disabled )

	def addPkValue( self, value ):
		"""
		Define Method
		增加pk值
		"""
		self.setPkValue( self.pkValue + value )

	def onPKValueChanged( self, oldPkValue ):
		"""
		pk值改变
		"""
		# 是否入狱
		if self.pkValue > oldPkValue and self.pkValue >= csdefine.PK_CATCH_VALUE:
			self.prisonHunt()
		elif self.pkValue <= 0:
			self.endPkValueTimer()

	def prisonHunt( self ):
		"""
		监狱追捕
		"""
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		# 判断是否可抓捕罪犯的地图 不是则释放追捕buff
		if not spaceScript.canArrest:
			self.spellTarget( csdefine.SKILL_ID_CATCH_PRISON, self.id )
		else:
			self.setTemp( "gotoPrison", True )
			self.gotoSpace( "fu_ben_jian_yu", (0,0,0), (0,0,0) )

	def setPkValue( self, value ):
		"""
		设置pk值
		调用此方法确定自己是RealEntity
		"""
		# pk值取值范围 0~65535
		if value < 0: value = 0
		if value > 0xffff: value = 0xffff

		if self.pkValue == value: return
		oldPkValue = self.pkValue
		self.pkValue = value
		self.onPKValueChanged( oldPkValue )

		# 如果pk值等于0，关闭pk值timer，开启善良值timer
		# 如果pk值大于0，开启pk值timer，关闭善良值timer，每隔20分钟pk值减1
		if self.pkValue == 0:
			self.addPkFlag( csdefine.PK_STATE_PEACE )
			
		elif 0 < self.pkValue < 18:
			# pk值处于0~17表示橙名状态（小红名）
			self.setGoodnessValue( 0 )		#有PK值后清除善恶值			
			self.addPkFlag( csdefine.PK_STATE_ORANGENAME )		
			
		else:
			# pk值18以上表示红名状态
			self.setGoodnessValue( 0 )			
			self.addPkFlag( csdefine.PK_STATE_REDNAME )			

	def onLessPkValueTimer( self, controllerID, userData ):
		"""
		Timer Callback
		ECBExtend.PK_VALUE_LESS_TIMER_CBID
		"""
		self.setPkValue( self.pkValue - 1 )
		DEBUG_MSG( "pkvalue[%i] Timer is trigger!" % ( self.pkValue ) )

	def startPkValueTimer( self, startTime = 0, loopTime = 0 ):
		"""
		触发pk值改变时间控制器
		"""
		if self.pkValueTimer != 0:
			return

		if startTime == 0:
			startTime = Const.PK_VALUE_LESS_TIME
		if loopTime == 0:
			loopTime = Const.PK_VALUE_LESS_TIME

		DEBUG_MSG( "startTime = %i, loopTime = %i" % ( startTime, loopTime ) )
		self.pkValueTimer = self.addTimer( startTime, loopTime, ECBExtend.PK_VALUE_LESS_TIMER_CBID )

	def endPkValueTimer( self ):
		"""
		取消善恶值改变时间控制器
		"""
		if self.pkValueTimer != 0:
			DEBUG_MSG( "end pkvalue[%i] Timer!" % ( self.pkValue ) )
			self.cancel( self.pkValueTimer )
		self.pkValueTimer = 0

	def optionReduceRD_goodness( self ):
		"""
		善良值改变带来御敌增加、删除
		"""
		if self.goodnessValue == csconst.PK_GOODNESS_MAX_VALUE:
			if not self.queryTemp( "ADD_REDUCE_ROEL_D_GN", False ) :
				self.reduce_role_damage_extra += Const.GOODNESS_ADD_REDUCE_ROLE_DAMAGE
				self.calcReduceRoleDamage()
				self.setTemp( "ADD_REDUCE_ROEL_D_GN", True )
		else:
			if self.queryTemp( "ADD_REDUCE_ROEL_D_GN", False ):
				self.reduce_role_damage_extra -= Const.GOODNESS_ADD_REDUCE_ROLE_DAMAGE
				self.calcReduceRoleDamage()
				self.setTemp( "ADD_REDUCE_ROEL_D_GN", False )

	def setGoodnessValue( self, value ):
		"""
		设置善良值
		"""
		if value < 0: value = 0
		if value > csconst.PK_GOODNESS_MAX_VALUE: value = csconst.PK_GOODNESS_MAX_VALUE
		if self.goodnessValue == value: return
		self.goodnessValue = value

		#触发御敌加成buff
		self.optionReduceRD_goodness()
		if value == csconst.PK_GOODNESS_MAX_VALUE:
			self.addPkFlag( csdefine.PK_STATE_BLUENAME )
		else:
			self.removePkFlag( csdefine.PK_STATE_BLUENAME )
	
	def addPkFlag( self, nameFlag ):
		"""
		增加一个PK状态
		"""
		if self.pkFlags & nameFlag == 0:
			self.pkFlags |= nameFlag
						
			if nameFlag == csdefine.PK_STATE_PEACE:
				self.pkFlags &= ~csdefine.PK_STATE_REDNAME
				self.pkFlags &= ~csdefine.PK_STATE_ORANGENAME
			if nameFlag == csdefine.PK_STATE_ORANGENAME:
				self.pkFlags &= ~csdefine.PK_STATE_PEACE
				self.pkFlags &= ~csdefine.PK_STATE_REDNAME
				self.pkFlags &= ~csdefine.PK_STATE_ATTACK
			if nameFlag == csdefine.PK_STATE_REDNAME:
				self.pkFlags &= ~csdefine.PK_STATE_PEACE
				self.pkFlags &= ~csdefine.PK_STATE_ORANGENAME
				self.pkFlags &= ~csdefine.PK_STATE_ATTACK
			
		self.updatePkState()
		
	
	def removePkFlag( self, nameFlag ):
		"""
		减少一个PK状态
		"""
		if self.pkFlags & nameFlag > 0:
			self.pkFlags &= ~nameFlag
		
		self.updatePkState()
			
	def updatePkState( self ):
		"""
		更新PK状态
		红>黄>褐>蓝>白>绿
		"""
		#褐白蓝可能出现共存的情况	
		#红色和黄色不和任何一种情况共存（因为玩家有PK值后会清除善恶值，并且删除褐名）
		if self.pkFlags & csdefine.PK_STATE_REDNAME > 0:
			self.setPkState( csdefine.PK_STATE_REDNAME )
			return			
		if self.pkFlags & csdefine.PK_STATE_ORANGENAME > 0:
			self.setPkState( csdefine.PK_STATE_ORANGENAME )
			return
		if self.pkFlags & csdefine.PK_STATE_ATTACK > 0:
			self.setPkState( csdefine.PK_STATE_ATTACK )
			return			
		if self.pkFlags & csdefine.PK_STATE_BLUENAME > 0:
			self.setPkState( csdefine.PK_STATE_BLUENAME )
			return									
		if self.pkFlags & csdefine.PK_STATE_PEACE > 0:
			self.setPkState( csdefine.PK_STATE_PEACE )
			return		
		if self.pkFlags & csdefine.PK_STATE_PROTECT > 0:
			self.setPkState( csdefine.PK_STATE_PROTECT )
			return			

	def onAddGoodnessTimer( self, controllerID, userData ):
		"""
		Timer Callback
		ECBExtend.PK_VALUE_LESS_TIMER_CBID
		"""
		self.setGoodnessValue( self.goodnessValue + 1 )

	def startGoodnessTimer( self ):
		"""
		触发pk值改变时间控制器
		"""
		if self.goodnessTimer != 0: return
		self.goodnessTimer = self.addTimer( Const.PK_GOOSNESS_ADD_TIME, Const.PK_GOOSNESS_ADD_TIME, ECBExtend.PK_ADD_GOODNESS_TIMER_CBID )

	def endGoodnessTimer( self ):
		"""
		取消善恶值改变时间控制器
		"""
		if self.goodnessTimer != 0:
			self.cancel( self.goodnessTimer )
		self.goodnessTimer = 0

	def resetPkState( self ):
		"""
		等级提升重新计算pk状态
		"""
		# 如果当前pk状态是pk攻击状态，直接过。
		if self.pkState == csdefine.PK_STATE_ATTACK: return
		self.pkFlags = 0
		if self.level >= csconst.PK_PROTECT_LEVEL:
			if self.goodnessValue == csconst.PK_GOODNESS_MAX_VALUE:
				self.addPkFlag( csdefine.PK_STATE_BLUENAME )			
			if self.pkValue == 0:				
				self.addPkFlag( csdefine.PK_STATE_PEACE )
			elif 0 < self.pkValue < 18:
				self.addPkFlag( csdefine.PK_STATE_ORANGENAME )
			else:
				self.addPkFlag( csdefine.PK_STATE_REDNAME )
		else:
			self.addPkFlag( csdefine.PK_STATE_PROTECT )

	def setPkState( self, state ):
		"""
		设置pk状态
		"""
		if self.pkState == state: return
		self.pkState = state

		if state == csdefine.PK_STATE_PEACE:
			# 关闭pk值减少timer
			self.endPkValueTimer()
			# 开启善恶值增长timer
			self.startGoodnessTimer()
		elif state == csdefine.PK_STATE_REDNAME or state == csdefine.PK_STATE_ORANGENAME:
			# 开启pk值减少timer
			self.startPkValueTimer()
			# 关闭善恶值增长timer
			self.endGoodnessTimer()
			# 关闭pkAttackTimer
			self.endPkAttackTimer()
		elif state == csdefine.PK_STATE_BLUENAME:
			# 关闭善恶值增长timer
			self.endGoodnessTimer()

	def setPkMode( self, srcEntityID, mode ):
		"""
		Exposed Method
		设置pk模式
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if self.isPkModelock:
			#self.statusMessage( csstatus.PKMODE_IS_LOCKED )
			return
		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			self.statusMessage( csstatus.ROLE_PK_NOT_ALLOW_CHANGE )
			return
		if self.pkMode == mode: return
		self.pkMode = mode

	def setSysPKMode( self, mode ):
		"""
		Define Method
		设置帮会副本中pk模式
		"""
		self.sysPKMode = mode

	def lockPkMode( self ):
		"""
		define method
		"""
		self.statusMessage( csstatus.ROLE_PK_MODE_IS_LOCDED )
		self.isPkModelock = True

	def unLockPkMode( self ):
		"""
		define method
		"""
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		# 玩家在安全区和不能PK的副本中不解锁
		if self.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ) or not spaceScript.canPk:
			return

		self.statusMessage( csstatus.ROLE_PK_MODE_UNLOCK )
		self.isPkModelock = False

	def addPKTarget( self, id ):
		"""
		可PK列表
		"""
		if not self.pkTargetList.has_key( id ):
			self.pkTargetList[ id ] = BigWorld.time()
			self.pkTargetList = self.pkTargetList
			self.onPKListChange( id )
		self.startPKFightBackTimer( id )
		INFO_MSG( " My pkTargetLsit is %s, pkFightBackTimer %s" % ( self.pkTargetList, self.pkFightBackTimer ) )

	def resetPKTargetList( self ):
		"""
		重置PK列表
		"""
		bwe = BigWorld.entities
		for eid, val in self.pkTargetList.items():
			try:
				e = bwe[ eid ]
			except KeyError:
				if eid != 0:
					WARNING_MSG( "pkTarget(%i): is not exist! " % eid  )
				continue
			e.removePKTarget( self.id )
			self.removePKTarget( e.id )

	def removePKTarget( self, entityID ):
		"""
		清除一个PK对象
		"""
		if self.pkTargetList.has_key( entityID ):
			self.pkTargetList.pop( entityID )
			self.onPKListChange( entityID )
			self.endPKFightBackTimer( entityID )
		else:
			return

	def onPKListChange( self, id ):
		"""
		PK 列表发生改变，主要是影响客户端界面显示
		"""
		INFO_MSG( " Info client pkTargetList change %s " % self.pkTargetList )
		self.client.onPKListChange( self.pkTargetList, id )

	def startPKFightBackTimer( self, id ):
		"""
		触发PK反击状态时间控制器
		"""
		self.endPKFightBackTimer( id )
		self.pkFightBackTimer[ id ] = self.addTimer( Const.PK_FIGHT_BACK_TIME, 0, ECBExtend.PK_STATE_FIGHT_BACK_TIMER_CBID)

	def endPKFightBackTimer( self, id  ):
		"""
		结束PK反击Timer
		"""
		if self.pkFightBackTimer.has_key( id ):
			if self.pkFightBackTimer[id] != 0:
				self.cancel( self.pkFightBackTimer[id] )
				self.pkFightBackTimer[id] = 0

	def onPkFightBackChangeTimer( self, controllerID, userData ):
		"""
		pk反击状态检测
		"""
		for eid, controlID in self.pkFightBackTimer.iteritems():
			if controlID == controllerID:
				self.cancel( controlID )
				self.pkFightBackTimer[eid] = 0
				self.removePKTarget( eid )

	def startPkAttackTimer( self ):
		"""
		触发pk攻击状态改变时间控制器
		"""
		self.endPkAttackTimer()
		self.addPkFlag( csdefine.PK_STATE_ATTACK )
		self.pkAttackTimer = self.addTimer( Const.PK_STATE_ATTACK_TIME, 0, ECBExtend.PK_STATE_ATTACK_TIMER_CBID )

	def endPkAttackTimer( self ):
		"""
		结束pk攻击状态时间控制器
		"""
		if self.pkAttackTimer != 0:
			self.cancel( self.pkAttackTimer )
		self.pkAttackTimer = 0
		self.removePkFlag( csdefine.PK_STATE_ATTACK )

	def onPkAttackChangeTimer( self, controllerID, userData ):
		"""
		Timer Callback
		ECBExtend.PK_STATE_ATTACK_TIMER_CBID
		"""
		#120秒时间到，重置pk状态
		self.endPkAttackTimer()
		self.onPkAttackChangeCheck()

	def onPkAttackChangeCheck( self ):
		"""
		pk攻击状态检测
		"""
		# 红名玩家不会进入pk攻击状态
		# 由Pk攻击状态进入红名状态后会停止pkAttackTimer
		# 所以要么恢复到白名要么蓝名
		if self.level < csconst.PK_PROTECT_LEVEL: return
		if self.pkState == csdefine.PK_STATE_PROTECT:	# pk保护状态玩家死后不改变pk状态 by姜毅
			return
		if self.pkState == csdefine.PK_STATE_REDNAME or self.pkState == csdefine.PK_STATE_ORANGENAME:	# 出现了红名状态反白的情况 所以加入红名判断 by姜毅
			return
		if self.goodnessValue == csconst.PK_GOODNESS_MAX_VALUE:
			self.addPkFlag( csdefine.PK_STATE_BLUENAME )
		else:
			self.addPkFlag( csdefine.PK_STATE_PEACE )

	def pkAttackStateCheck( self, entityID, isMalignant ):
		"""
		Define Method
		pk状态检测，判断自己是否需要进入pk攻击状态
		@param    entityID				: 攻击的对象
		@type     entityID				: EntityID
		@param    isMalignant			: 攻击类型是否为恶性
		@type     isMalignant			: BOOL
		"""
		if entityID == self.id: return
		# 检测目标是否存在
		target = BigWorld.entities.get( entityID )
		if target is None: return

		if target.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY != 0: return

		# 切磋不进入pk
		if self.isQieCuoTarget( entityID ): return
		if self.level < csconst.PK_PROTECT_LEVEL: return

		# 如果所在地图，不需要计算PK
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )

		if spaceScript.isSpaceCalcPkValue:return

		# 如果自己不是对方PK模式下允许PK的目标，双方名字变为紫色
		if isMalignant  and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and not target.canPk( self ):
			self.addPKTarget( target.id )
			target.addPKTarget( self.id )

		# 如果自己是红名状态，不进入攻击状态 把这个判定提上来 修正一些攻击引起的自身pk状态改变 by姜毅
		if self.pkState == csdefine.PK_STATE_REDNAME or self.pkState == csdefine.PK_STATE_ORANGENAME: return

		if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if target.pkState in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ATTACK, csdefine.PK_STATE_ORANGENAME ]:
				# 对红名状态和攻击状态玩家释放任意效果，不进入褐红名状态
				return
			if not isMalignant and target.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ATTACK, csdefine.PK_STATE_ORANGENAME ]:
				# 对不处于红名状态和攻击状态的玩家释放良性效果，不进入褐红名状态
				return

		self.startPkAttackTimer()				# 攻击方进入攻击橙名状态

	def calcPkValue( self, killer ):
		"""
		计算pk值
		@param    killer: 把我干掉的人
		@type     killer: RoleEntity
		"""
		if killer == None: return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if not killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return

		DEBUG_MSG( "%s(id = %i, pkState = %i ) kill %s( %i, pkState = %i ) " % ( killer.getName(), killer.id, killer.pkState, self.getName(), self.id, self.pkState ) )

		killer.increaseHomicideNum()		# 对方杀人次数增加1次 无论是否增加PK值 杀人和被杀都需要被统计
		self.deadNumber += 1				# 自己死亡次数加1次

		# 处于帮会掠夺战则不影响PK值
		if self.tong_isInRobWar( killer.tong_dbID ):
			INFO_MSG( "Not add PK value. %s(%i) kill %s(%i) and in RobWar!" % ( killer.getName(), killer.id, self.getName(), self.id ) )
			return
		#如果符合运镖和劫镖关系，那么不影响PK值
		if self.isDartRelation( killer ):
			INFO_MSG( "Not add PK value. %s(%i) kill %s(%i) and in DartWar!" % ( killer.getName(), killer.id, self.getName(), self.id ) )
			return

		# 如果自己是攻击状态或者红名状态，杀人者都不犯法，不影响PK值
		if self.pkState in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ATTACK, csdefine.PK_STATE_ORANGENAME ]:
			INFO_MSG( " Not add PK value. %s(%i) kill redName player %s(%i)!" % ( killer.getName(), killer.id, self.getName(), self.id ) )
			return
		#橙名玩家在攻击白名玩家时，PK值不会增加，所以把下面两行去掉
		#if not self.pkTargetList.has_key( killer.id ):
		#	return
		# pk值增加等级差规则 by 姜毅
		levelOffcent = ( killer.level - self.level ) / 10
		# 当10<=杀人方等级-被杀方等级<20，杀普通玩家+7，杀蓝名+14
		# 当20<=杀人方等级-被杀方等级<30，杀普通玩家+8，杀蓝名+16
		# 当30<=杀人方等级-被杀方等级<40，杀普通玩家+9，杀蓝名+18
		# 当40<=杀人方等级-被杀方等级，杀普通玩家+10，杀蓝名+20
		if levelOffcent < 0: levelOffcent = 0
		elif levelOffcent > 4: levelOffcent = 4
		addValueNormal = 6 + levelOffcent
		addValueBlue = 12 + levelOffcent * 2
		if self.pkState == csdefine.PK_STATE_PEACE:
			INFO_MSG( "Add PK value. %s(%i) kill %s(%i), before value:%i, after value:%i!" % ( killer.getName(), killer.id, self.getName(), self.id, killer.pkValue, killer.pkValue + addValueNormal ) )
			killer.addPkValue( addValueNormal )
		elif self.pkState == csdefine.PK_STATE_BLUENAME:
			INFO_MSG( "Add PK value. %s(%i) kill %s(%i), before value:%i, after value:%i!" % ( killer.getName(), killer.id, self.getName(), self.id, killer.pkValue, killer.pkValue + addValueBlue ) )
			killer.addPkValue( addValueBlue )
		# 对方pk值增加，把对方加入仇人名单
		self.base.addKillerFoe( killer.databaseID, killer.getName(), killer.base )

	def increaseHomicideNum( self ):
		"""
		Define method.
		杀人数增长，目前的增量是1
		"""
		self.homicideNumber += 1

	def canPk( self, entity ):
		"""
		判断是否能pk一个entity
		@param value: pk值
		@type  value: int
		"""
		if entity is None: return False

		# 如果是自己则不能攻击
		if self.id == entity.id: return False

		# 不在同一地图不能PK
		if self.spaceID != entity.spaceID:
			return False

		# 角色所在地图是否允许pk
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canPk:
			return False

		# 如果处于飞行状态，则不允许pk
		if len( self.attrBuffs ) > 0:
			if VehicleHelper.isFlying( self ):	return False

		# 30级玩家保护
		if self.pkState == csdefine.PK_STATE_PROTECT: return False

		# 判断是否为宠物，是的话把目标转接给主人
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			INFO_MSG( "PK taget is a pet in canPK function " )
			owner = entity.getOwner()
			if owner.etype == "MAILBOX" :
				return False
			entity = owner.entity

		# 判断是否是玩家
		if not entity.utype == csdefine.ENTITY_TYPE_ROLE: return False

		# 30级对方玩家禁止pk
		if entity.pkState == csdefine.PK_STATE_PROTECT: return False

		# 队伍成员不能PK
		if self.isTeamMember( entity ):
			return False

		 # 系统模式优先
		if  self.sysPKMode:
			# 系统模式为和平模式不能PK
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_PEACE:
				return False

			# 帮战副本中帮会成员不能PK
			if self.tong_dbID != 0 and ( self.tong_dbID == entity.tong_dbID ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG:
				return False

			# 阵营战副本中阵营成员不能PK
			if self.getCamp() != 0 and ( self.getCamp() == entity.getCamp() ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP:
				return False

			# 系统模式为临时阵营模式
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TEMPORARY_FACTION :
				if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG and ( not RoleYiJieZhanChangInterface.canPk( self, entity ) ) :
					return False

			# 系统模式为联盟模式
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_LEAGUE:
				if self.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) !=0 and self.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) == entity.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ):
					return False

			if self.sysPKMode in csdefine.SYS_PK_CONTOL_ACT:
				if self.sysPKMode == entity.sysPKMode:
					return False
		else:
			# 如果我的pk模式是善意模式（原善恶模式）并且entity不是黄红名
			if  self.pkMode == csdefine.PK_CONTROL_PROTECT_RIGHTFUL and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ]:
				return False

			# 如果我的pk模式是正义模式并且entity不是黄红名并且与对方属于同一阵营
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_JUSTICE and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ] \
				and self.getCamp() == entity.getCamp():
				return False

		# 对方在组队跟随状态下可攻击
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and entity.isFollowing(): return True

		# 如果我被禁止PK或者我要pk的entity被禁止pk（例如某方在安全区）
		if self.actionSign( csdefine.ACTION_FORBID_PK ) or entity.actionSign( csdefine.ACTION_FORBID_PK ): return False

		return True

	def onPrisonContribute( self, srcEntity ):
		"""
		Expose method.
		监狱捐献
		"""
		if self.id != srcEntity:
			return

		money = 0
		lv = self.level
		for item in csconst.PRISON_CONTRIBUTE_DATAS:
			if lv <= item[ 1 ]:
				money = item[ 2 ]
				break

		if self.money < money:
			return

		self.payMoney( money, csdefine.CHANGE_MONEY_PRISON_CONTRIBUTE )
		self.spellTarget( 780039001, self.id )

	def saveDoubleExpBuff( self ):
		"""
		向客户端发送保存BUFF通知
		"""
		if self.money < 10000:
			self.statusMessage( csstatus.TAKE_EXP_SAVE_MONEY_FAIL )
			return
		self.client.onSaveDoubleExpBuff()

	def onSaveDoubleExpBuff( self, srcEntity ):
		"""
		Expose method.
		保存双倍奖励BUFF
		"""
		buffs = self.findBuffsByBuffID( 22117 )

		if len( buffs ) > 0:
			if self.money < 10000:
				self.statusMessage( csstatus.TAKE_EXP_SAVE_MONEY_FAIL )
				return

			buff = self.getBuff( buffs[0] )
			if buff[ "persistent" ] <= 0:
				DEBUG_MSG( "saveDoubleExpBuff:persistent is 0." )
				return

			self.payMoney( 10000, csdefine.CHANGE_MONEY_SAVEDOUBLEEXPBUFF )
			# 计算BUFF的剩余时间
			buff[ "persistent" ] = int( buff[ "persistent" ] - time.time() )
			self.takeExpRecord[ "freezeBuff" ] = buff

			# 记录最后冻结的时间
			self.takeExpRecord[ "freezeTime" ] = int( time.time() )
			self.removeBuff( buffs[0], [csdefine.BUFF_INTERRUPT_NONE] )

			h = int( buff[ "persistent" ] / ( 60 * 60 ) )
			m = int( ( buff[ "persistent" ] - ( h * 60 * 60 ) ) / 60 )
			s = int( ( buff[ "persistent" ] - ( h * 60 * 60 ) ) % 60 )
			b = "%i%%" % buff[ "skill" ].getPercent()
			self.statusMessage( csstatus.TAKE_EXP_HOUR_SAVE, b, h, m, s )
		else:

			self.statusMessage( csstatus.TAKE_EXP_NOT_CLOSE_FAIL )

	def saveDanceBuff( self, srcEntity ):
		"""
		Expose method.
		保存跳舞Buff
		"""
		buffs = self.findBuffsByBuffID( Const.JING_WU_SHI_KE_DANCE_BUFF )

		if len( buffs ) > 0:
			buff = self.getBuff( buffs[0] )
			if buff[ "persistent" ] <= 0:
				DEBUG_MSG( "saveDoubleExpBuff:persistent is 0." )
				return

			# 计算BUFF的剩余时间
			buff[ "persistent" ] = int( buff[ "persistent" ] - time.time() )
			self.danceRecord[ "freezeBuff" ] = buff

			# 记录最后冻结的时间
			self.danceRecord[ "freezeDanceDailyRecord" ].reset()
			self.removeBuff( buffs[0], [csdefine.BUFF_INTERRUPT_NONE] )

			h = int( buff[ "persistent" ] / ( 60 * 60 ) )
			m = int( ( buff[ "persistent" ] - ( h * 60 * 60 ) ) / 60 )
			s = int( ( buff[ "persistent" ] - ( h * 60 * 60 ) ) % 60 )
			self.statusMessage( csstatus.JING_WU_SHI_KE_BUFF_SAVE, h, m, s )
		else:
			self.statusMessage( csstatus.JING_WU_SHI_KE_NO_BUFF )

	"""
	GM 信息查询
	"""
	def queryMoneyInfo( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_MONEY, str(( self.money, )) )


	def queryPosInfo( self, queryerMB, params  ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_MAP, str(( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), str(self.position) )) )


	def queryStateInfo( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_STATE, str(( Const.state_dict[self.getState()], )) )


	def queryBankInfo( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_BANK_MONEY, str(( self.bankMoney, )) )

	def queryBagInfo( self, queryerMB, params ):
		"""
		define method
		"""
		itemsInfo = []
		info = ""
		for i in self.itemsBag.getDatasByRange(255):
			itemsInfo.append( i.name() + "(" + str(i.uid)+ ")"  )
		if len(itemsInfo) == 0:
			queryerMB.client.onStatusMessage( csstatus.STRING_BAG_HAS_NO_ITEM, "" )
		else:
			for i in itemsInfo:
				info += i + "\n "
			queryerMB.client.onStatusMessage( csstatus.STRING_BAG_ITEM, str(( info, )) )


	def querySkillInfo( self, queryerMB, params ):
		"""
		define method
		"""
		info = "skill: "
		for i in self.attrSkillBox:
			info += g_skills[i].getName() + " level: %i"%g_skills[i].getLevel() + ", "

		queryerMB.client.onStatusMessage( csstatus.STRING_SKILL_INFO, str(( info, )) )


	def catchAction( self, catcherMB, params ):
		"""
		define method
		"""

		self.gotoSpaceLineNumber( params['spaceType'], params['lineNumber'], params['pos'], (0,0,0) )

	def cometoAction( self, comerMB, params ):
		"""
		define method
		"""
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			comerMB.client.onStatusMessage( csstatus.TRANSPORT_FORBID_TARGET_NOT_ARRIVE, "" )
			return

		comerMB.cell.gotoSpaceLineNumber( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.getCurrentSpaceLineNumber(), self.position, self.direction )

	def updateBenefitTime( self ):
		"""
		刷新奖励时间
		"""
		now = BigWorld.time()
		benefitTime = now - self.calBenefitTime
		self.calBenefitTime = now
		self.benefitTime += benefitTime

	def canBenefit( self ):
		"""
		是否能够领取奖励
		"""
		self.updateBenefitTime()
		return self.benefitTime >= Const.BENIFIT_PERIOD

	def resetBenefitTime( self ):
		"""
		重置奖励数据
		"""
		self.benefitTime = 0.0
		self.client.onGetBenefitTime( self.benefitTime )

	def getRestBenefitTime( self ):
		"""
		获得还剩多少时间才能被奖励
		"""
		self.updateBenefitTime()
		return self.benefitTime - Const.BENIFIT_PERIOD

	def giveNewPlayerReward( self, lifeTime, rewardNum ):
		"""
		defined method
		发放实时新手奖励 by姜毅
		"""
		if not self.wallow_getLucreRate(): # 如果收益为0，则不奖励
			return

		rewardTimeList = g_onlineReward.getRewardTick( lifeTime )
		if rewardNum > len( rewardTimeList ):			# 如果可领取奖励份数小于已领次数，则没有可领取的奖励
			ERROR_MSG( "Can't get the %i newPlayerReward before right time" % rewardNum )
			return
		rewardTick = rewardTimeList[rewardNum-1]
		# 发奖励(背包无法给奖励就用邮件方式发给玩家)
		INFO_MSG( "give new player reward, fixtimeTick %i "%( rewardTick ) )
		awarder = g_rewards.fetch( g_onlineReward.getRewardUid(rewardTick), self )
		if awarder is None or len( awarder.items ) <= 0:
			ERROR_MSG( "new player rewardConfig get nothing. rewardTick: %i" % rewardTick )
			return
		for item in awarder.items:
			item.setBindType( ItemTypeEnum.CBT_PICKUP )
		if self.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_CAN_HOLD:
			awarder.award( self, csdefine.ADD_ITEM_GIVEFIXTIMEREWARD )
		else:
			title = ST.ROLE_YOUR_TREASURE
			content = ST.ROLE_SYSTEM_MAIL
			self.mail_send_on_air_withItems( self.getName(), csdefine.MAIL_TYPE_QUICK, title, content, awarder.items )
			self.statusMessage( csstatus.FIX_TIME_REWARD_WITH_MAIL, rewardNum )
		self.base.addRewardRecord( rewardTick )				# 通知base增加领取记录并保存到DB

		if rewardNum == g_onlineReward.getCount():			# 新手奖励领取完，关闭界面
			self.client.onFixTimeReward( 0, 0, -1, 0, 0)
			return
		self.sendNextAwarderToClient( lifeTime, rewardNum, awarder.items[0].id )

	def sendNextAwarderToClient( self, lifeTime, rewardNum, lastItemID ):
		"""
		defined method
		获取下次新手奖励内容并通知客户端
		"""
		nextRewardTick = g_onlineReward.rewardKeys()[ rewardNum ]
		nextAwarder = g_rewards.fetch( g_onlineReward.getRewardUid( nextRewardTick ), self )
		if nextAwarder is None:
			self.client.onFixTimeReward( 0, 0, -1, 0, 0 )#通知界面关闭
		else:
			nextItem = random.choice( nextAwarder.items )	# 随机给一个
			self.client.onFixTimeReward( nextRewardTick, nextItem.id, rewardNum, lifeTime, lastItemID )	# 客户端提示

	def giveOldPlayerReward( self, rewardNum ):
		"""
		defined method
		通过直接给与或者邮件方式给与玩家实时老手奖励 by姜毅
		"""
		if not self.wallow_getLucreRate(): # 如果收益为0，则不奖励
			return
		reason = 0
		param = 0
		lastReward = 0
		rewardNum += 1
		levelLimit = max( self.level/10, 3 )				# 该等级每天可领取的最大奖励份数
		if rewardNum > levelLimit:
			self.client.onOldFixTimeReward( -1, rewardNum, reason, param )
			return
		if rewardNum == levelLimit:
			lastReward = -1
		rewardTypeOdd = random.uniform( 1, 100 )
		INFO_MSG( "give old player reward, odd %i num: %i "%( rewardTypeOdd, rewardNum ) )
		if rewardTypeOdd <= 25:
			INFO_MSG( "give exp" )
			upperRate = 1
			upperOdd = random.random()	# 礼品暴击
			if upperOdd < 0.1: upperRate = 3	# 暴击三倍
			exp = int( 3 * (rewardNum**0.5) * (self.level**1.4) * 10 ) * upperRate
			self.addExp( exp, csdefine.CHANGE_EXP_OLD_PLAYER_REWARD )
			reason = 1
			param = exp
		elif rewardTypeOdd <= 50:
			INFO_MSG( "give protential" )
			upperRate = 1
			upperOdd = random.random()	# 礼品暴击
			if upperOdd < 0.1: upperRate = 3	# 暴击三倍
			protential = int( (rewardNum**0.5) * (self.level**1.4) * 10 ) * upperRate
			self.addPotential( protential, csdefine.CHANGE_POTENTIAL_OLD_PLAYER_REWARD )
			reason = 2
			param = protential
		else:
			INFO_MSG( "give item" )
			awarder = g_rewards.fetch( csdefine.RCG_OLD_PLAYER_FIXTIME, self )
			if awarder is None: return
			if len( awarder.items ) <= 0: return
			for item in awarder.items:
				item.setBindType( ItemTypeEnum.CBT_PICKUP )
			checkRes = self.checkItemsPlaceIntoNK_( awarder.items )
			if checkRes == csdefine.KITBAG_CAN_HOLD:
				awarder.award( self, csdefine.ADD_ITEM_OLD_PLAYER_REWARD )
			else:
				title = ST.ROLE_YOUR_PRESENT
				content = ST.ROLE_SYSTEM_MAIL
				self.mail_send_on_air_withItems( self.getName(), csdefine.MAIL_TYPE_QUICK, title, content, awarder.items )
				self.statusMessage( csstatus.FIX_TIME_REWARD_WITH_MAIL, rewardNum )
			selectedItem = random.choice( awarder.items )	# 随机给一个
			reason = 3
			param = selectedItem.id
		if self.getLevel() > csconst.OLD_REWARD_LEVEL_LIM:
			self.statusMessage( csstatus.FIX_TIME_OLD_REWARD_LEVEL_LIM, csconst.OLD_REWARD_LEVEL_LIM+1 )
			self.client.onOldFixTimeReward( -1, 0, 0, 0 )
		else:
			self.client.onOldFixTimeReward( lastReward, rewardNum, reason, param )	# 客户端提示，浪费数据流量

	def giveKJReward( self, eType ):
		"""
		define method
		奖励模块整理，获得科举奖励 by 姜毅
		"""
		blobItems = []
		awarder = g_rewards.fetch( csdefine.RCG_KJ, self )
		checkRes = self.checkItemsPlaceIntoNK_( awarder.items )
		if checkRes == csdefine.KITBAG_CAN_HOLD:
			for item in awarder.items:
				blobItems.append( ChatObjParser.dumpItem( item ) )	# 用于物品消息链接
			awarder.award( self, csdefine.ADD_ITEM_REQUESTIEEXP )
		if eType == 3:
			self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "",  cschannel_msgs.BCT_KJXS_COMMENDATION %( self.getName() ), blobItems )
		if eType == 4:
			self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", cschannel_msgs.BCT_KJHS_COMMENDATION %( self.getName() ), blobItems )

	#-----------------------------------------------------------------------------------------------------
	# 巡逻相关  kb
	#-----------------------------------------------------------------------------------------------------
	def onPatrolToPointOver( self, command ):
		"""
		virtual method.
		用于onPatrolToPointFinish()函数在ECBExtend模块中的回调处理

		@param command: 巡逻到一个点所得到的命令参数
		"""
		if command != -1:
			ai = g_aiDatas[ command ]
			if ai.check( self ):
				ai.do( self )
		if BigWorld.time() - self.queryTemp( "patrol_moving_start_time" )  < 0.01:
			return False
		return True

	def onFlyTeleportContinue( self, srcEntityID ):
		"""
		Expose method.
		飞翔传送场景加载完毕 继续飞翔
		"""
		DEBUG_MSG( "onFlyTeleportContinue >>>%i." % srcEntityID )
		if srcEntityID != self.id:
			return

		indexs = self.findBuffsByBuffID( 99010 )
		self.getBuff( indexs[0] )["skill"].continuePatrol( self )

	def closeVolatileInfo( self ):
		"""
		virtual method.
		关闭坐标信息传送功能。
		由于这个模块会被不同的entity调用，而某些entity可能会需要以不同
		的方式或时机关闭这个行为，因此这个接口允许玩家重载。
		"""
		# 主角重载此接口，但不做任何事情，等于不执行关闭坐标信息通知的行为
		# 如果关闭了玩家会漂移，因为玩家移动时并没有被通知要打开坐标信息通知功能。
		pass

	def openVolatileInfo( self ):
		"""
		virtual method.
		打开坐标信息传送功能
		由于这个模块会被不同的entity调用，而某些entity可能会需要以不同
		的方式或时机关闭这个行为，因此这个接口允许玩家重载。
		"""
		# 重载并覆盖此方法的功能，使之主角在骑鸟飞行结束后也不会广播数据。
		pass

	#-----------------------------------------------------------------------------------------------------
	# 有生命物品回调
	#-----------------------------------------------------------------------------------------------------
	def resetLifeItems( self, onLine ):
		"""
		刷新有生命的物品
		onLine为True表示玩家上线刷新
		onLine为False表示玩家下线刷新
		"""
		uids = []
		deadTimes = []
		items = self.itemsBag.getDatas()
		for item in items:
			lifeType = item.getLifeType()
			if lifeType == ItemTypeEnum.CLTT_NONE: continue
			deadTime = item.getDeadTime()
			# 下线开始计时，上线判断该物品是否已到期，如果到期则删除，没到期恢复初始状态。
			if lifeType == ItemTypeEnum.CLTT_ON_OFFLINE:
				if onLine:
					if time.time() > deadTime:
						self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_ITEMLIFEOVER )
					else:
						item.setDeadTime( 0, self )
				else:
					item.activaLifeTime()
			elif lifeType == ItemTypeEnum.CLTT_ON_OFFLINE_EVER:
				if onLine:
					if time.time() > deadTime:
						item.setLifeTime( 0, self )
					item.setDeadTime( 0, self )
				else:
					item.activaLifeTime()
			else:
				if deadTime == 0: continue
				uids.append( item.uid )
				deadTimes.append( deadTime )


		if len( uids ) == 0: return
		if len( deadTimes ) == 0: return
		if onLine:
			self.addLifeItemsToManage( uids, deadTimes )
		else:
			self.removeLifeItemsFromManage( uids, deadTimes )

	def addLifeItemToMgr( self, item ):
		"""
		玩家身上的接口添加一个物品到有生命物品管理器
		"""
		if item is None: return
		self.addLifeItemsToManage( [item.uid], [item.getDeadTime()] )

	def addLifeItemsToManage( self, uids, lifeTimes ):
		"""
		添加物品到管理器中
		"""
		BigWorld.globalData["LifeItemMgr"].addItems( self.base, uids, lifeTimes )

	def removeLifeItemsFromManage( self, uids, lifeTimes ):
		"""
		移除物品从管理器中
		"""
		BigWorld.globalData["LifeItemMgr"].removeItems( self.base, uids, lifeTimes )

	def onItemLifeOver( self, uid ):
		"""
		Define method.
		有生命物品生命周期到达回调
		"""
		item = self.getItemByUid_( uid )
		if item is None: return
		lifeType = item.getLifeType()
		if lifeType in [ItemTypeEnum.CLTT_ON_GET, ItemTypeEnum.CLTT_ON_WIELD]:
			if item.isAlreadyWield():
				item.unWield( self )
				self.resetEquipModel( item.order, None )
			self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_ITEMLIFEOVER )
		elif lifeType in [ItemTypeEnum.CLTT_ON_GET_EVER, ItemTypeEnum.CLTT_ON_WIELD_EVER]:
			item.setLifeTime( 0, self )
			item.setDeadTime( 0, self )
			if item.isAlreadyWield():
				item.unWield( self )
				self.resetEquipModel( item.order, None )

	def onRemoveRobFlag( self, timerID, cbID ):
		"""
		移除劫镖标志
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
			self.removeFlag( csdefine.ROLE_FLAG_CP_ROBBING )
		else:
			self.removeFlag( csdefine.ROLE_FLAG_XL_ROBBING )

	def onTeleportReady( self, srcEntityID, spaceID ):
		"""
		客户端地图加载完成
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if spaceID != self.spaceID:
			return

		spaceBase = self.getCurrentSpaceBase()

		# 如果为None则space可能已经销毁
		if spaceBase:
			spaceBase.cell.onTeleportReady( self.base )
		else:
			assert False, "spaceBase is None, data=[%s]" % BigWorld.getSpaceDataFirstForKey( self.spaceID, 1 ).split()

		if not self.isCurrSpaceCanFly() and VehicleHelper.isFlying( self ):
			# 从可以飞行的空间进入了不可以飞行的空间，打断飞行buff
			self.removeBuffByBuffID( csdefine.FLYING_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

		if not self.isCurrSpaceCanVehicle():
			# 从可以召唤骑宠的空间进入了不可以召唤骑宠的空间，打断骑宠buff
			if VehicleHelper.isFlying( self ):
				self.removeBuffByBuffID( csdefine.FLYING_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )
			elif VehicleHelper.isOnLandVehicle( self ):
				self.removeBuffByBuffID( csdefine.VEHICLE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

		# CSOL-1561传送后清除潜行buff
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:
			self.removeAllBuffByBuffID( csconst.PROWL_BUFF_ID, [csdefine.BUFF_INTERRUPT_NONE] )

		self.destinyTransCheck()		# 天命轮回副本检测

	def doKLJDActivity( self, srcEntityID ):
		"""
		砸蛋中
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		g_KuaiLeJinDan.doKLJDActivity( self )

	def doSuperKLJDActivity( self, srcEntityID ):
		"""
		超级砸蛋中
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		g_KuaiLeJinDan.doSuperKLJDActivity( self )

	def singleDance( self ):
		"""
		defined method
		单人跳舞
		Exposed method
		"""
		if self.actionSign( csdefine.ACTION_ALLOW_DANCE ):			# 判断角色是否在舞厅中
			self.spellTarget( Const.JING_WU_SHI_KE_SINGLE_DANCE_SKILL, self.id )
			self.spellTarget( Const.JING_WU_SHI_KE_POINT_SKILL, self.id )
		self.changeState( csdefine.ENTITY_STATE_DANCE )				# 进入跳舞状态

	def doubleDance( self ):
		"""
		defined method
		双人舞
		"""
		if self.actionSign( csdefine.ACTION_ALLOW_DANCE ):			# 判断角色是否在舞厅中
			self.spellTarget( Const.JING_WU_SHI_KE_DOUBLE_DANCE_SKILL, self.id )
			self.spellTarget( Const.JING_WU_SHI_KE_POINT_SKILL, self.id )
		self.changeState( csdefine.ENTITY_STATE_DOUBLE_DANCE )				# 进入双人跳舞状态

	def teamDance( self ):
		"""
		队伍集体跳舞
		"""
		if not self.isInTeam():
			self.statusMessage( csstatus.JING_WU_SHI_KE_NO_TEAM )
		else:
			if not self.isTeamCaptain():
				self.statusMessage( csstatus.JING_WU_SHI_KE_TEAM_NOT_CAPTAIN )
				return

			allMemberInRange = self.getAllMemberInRange( Const.JING_WU_SHI_KE_TEAM_RANGE )	# 得到范围内所有队伍成员
			for teamMember in  allMemberInRange:
				state = teamMember.getState()
				# 在骑宠中，不进行队伍共舞
				if not (state == csdefine.ENTITY_STATE_FREE or state == csdefine.ENTITY_STATE_DANCE or state == csdefine.ENTITY_STATE_DOUBLE_DANCE) or VehicleHelper.getCurrVehicleID( teamMember ):
					continue
				if state == csdefine.ENTITY_STATE_DANCE or state == csdefine.ENTITY_STATE_DOUBLE_DANCE:
					teamMember.stopDance( teamMember.id )
				if teamMember.actionSign( csdefine.ACTION_ALLOW_DANCE ):
					teamMember.spellTarget( Const.JING_WU_SHI_KE_TEAM_DANCE_SKILL, teamMember.id )
					teamMember.spellTarget( Const.JING_WU_SHI_KE_POINT_SKILL, teamMember.id )
				EffectState_List = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP
				# 定身、眩晕、昏睡状态不能跳舞
				if teamMember.effect_state & EffectState_List != 0:
					teamMember.statusMessage( csstatus.JING_WU_SHI_KE_NOT_FREE )
					continue
				teamMember.changeState( csdefine.ENTITY_STATE_DANCE )

	def stopDance( self, srcEntityID ):
		"""
		停止跳舞
		Exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		dancePartner = BigWorld.entities.get( self.dancePartnerID )
		if dancePartner:		# 如果有共舞的舞伴
			self.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_DOUBLE_DANCE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			self.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_POINT_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			self.changeState( csdefine.ENTITY_STATE_FREE )
			dancePartner.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_DOUBLE_DANCE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			dancePartner.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_POINT_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			dancePartner.changeState( csdefine.ENTITY_STATE_FREE )
			self.dancePartnerID = 0		# 舞伴置为空
			dancePartner.dancePartnerID = 0
		else:
			if len( self.findBuffsByBuffID( Const.JING_WU_SHI_KE_SINGLE_DANCE_BUFF ) ) > 0:
				self.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_SINGLE_DANCE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			elif len( self.findBuffsByBuffID( Const.JING_WU_SHI_KE_TEAM_DANCE_BUFF ) ) > 0:
				self.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_TEAM_DANCE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			self.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_POINT_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			self.changeState( csdefine.ENTITY_STATE_FREE )

	def playFaceAction( self, face ) :
		"""
		播放表情动作
		"""
		self.planesAllClients( "playFaceAction", ( face, ) )
		self.setTemp( "Temp_Face", face ) # 加个标记，限制快速重复播放同一个表情

	def stopFaceAction( self, srcEntityId, face ) :
		"""
		停止播放表情动作
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return
		self.curActionSkillID = 0
		self.planesAllClients( "stopFaceAction", ( face, ) )
		self.removeTemp("Temp_Face") # 加个标记，限制快速重复播放同一个表情

	def sendRequestDance( self, target ):
		"""
		邀请共舞
		"""
		if not target.isReal() or self.distanceBB( target ) > 3:
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_TOO_FAR )
			return

		#if not self.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# 判断角色是否在舞厅中
		#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
		#	return
		#if not target.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# 判断角色是否在舞厅中
		#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
		#	return
		if ( self.getState() != csdefine.ENTITY_STATE_FREE ) and ( not (self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0) ):	# 判断角色是否为自由状态或单人舞状态
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE )
			return
		if ( target.getState() != csdefine.ENTITY_STATE_FREE ) and ( not (target.getState() == csdefine.ENTITY_STATE_DANCE and target.dancePartnerID == 0) ):#判断邀请对象是否为自由状态或单人舞状态
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE_TOO )
			return

		if self.getGender() == target.getGender():
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_DANCE_GENDER )
			return

		if self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0:	# 如果角色单人舞状态，则停止跳舞
			self.stopDance( self.id )

		self.changeState( csdefine.ENTITY_STATE_REQUEST_DANCE )						# 角色进入邀请跳舞状态
		self.requestDanceID = target.id										# 角色邀请的舞伴
		target.client.receiveRequestDance( self.id )
		self.statusMessage( csstatus.JING_WU_SHI_KE_INVITE, target.getName() )

	def answerDanceRequest( self, srcEntityID, result, requestEntityID ):
		"""
		<Exposed/>
		答复共舞的邀请
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		requestEntity = BigWorld.entities.get( requestEntityID )
		if requestEntity:
			if result:	# 如果接受共舞
				#if not self.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# 判断角色是否在舞厅中
				#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
				#	return
				#if not requestEntity.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# 判断角色是否在舞厅中
				#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
				#	return
				if ( self.getState() != csdefine.ENTITY_STATE_FREE ) and ( not (self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0) ):	# 判断角色是否为自由状态或单人舞状态
					self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE )
					return
				if not requestEntity.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:		# 判断邀请对象是否为邀请状态
					self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_REQUEST_DANCE )
					return
				if self.distanceBB( requestEntity ) > 10:		# 被邀请者与邀请方，距离大于10
					self.statusMessage( csstatus.JING_WU_SHI_KE_ANSWER_TOO_FAR, requestEntity.playerName )
					requestEntity.changeState( csdefine.ENTITY_STATE_FREE )
					requestEntity.statusMessage( csstatus.JING_WU_SHI_KE_ANSWER_TOO_FAR, self.playerName )
					return
				if requestEntity.requestDanceID != self.id:		# 如果邀请方邀请的对象不是自己
					self.statusMessage( csstatus.JING_WU_SHI_KE_NOT_REQUST, requestEntity.playerName )
					return

				if self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0:	# 如果角色单人舞状态，则停止跳舞
					self.stopDance( self.id )

				self.position = requestEntity.position		# 移动到邀请方，为了播放共舞动作
				self.direction = requestEntity.direction
				self.doubleDance()
				if requestEntity.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:		# 判断邀请对象是否为邀请状态，置为自由状态，否则在邀请状态下，无法使用技能
					requestEntity.changeState( csdefine.ENTITY_STATE_FREE )
				requestEntity.doubleDance()
				requestEntity.client.onStatusMessage( csstatus.JING_WU_SHI_KE_ACCEPT, "(\'%s\',)" % self.getName() )	# 增加接受邀请提示（hyw--2009.07.23）

				self.dancePartnerID = requestEntityID		# 记录舞伴的ID
				requestEntity.dancePartnerID = self.id
			else:		# 如果不接受共舞
				if requestEntity.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:
					requestEntity.changeState( csdefine.ENTITY_STATE_FREE )
				requestEntity.statusMessage( csstatus.JING_WU_SHI_KE_REFUSE_DANCE, self.playerName )

	def stopRequestDance( self, srcEntityID ):
		"""
		取消共舞的邀请
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		if self.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:
			requestDancer = BigWorld.entities.get( self.requestDanceID )
			if requestDancer:
				requestDancer.client.stopRequestDance()		# 通知被邀请的，邀请取消了
				requestDancer.statusMessage( csstatus.JING_WU_SHI_KE_STOP_REQUEST_DANCE, self.playerName )
			self.changeState( csdefine.ENTITY_STATE_FREE )

	def initRoleRecord( self, recordString ):
		"""
		define method
		"""
		recordArray = cPickle.loads( recordString )
		self.roleRecord = {}
		for i in recordArray:
			self.roleRecord[i[0]] = i[1]

	def createAccountRecord( self, recordString ):
		"""
		define method
		"""
		recordArray = cPickle.loads( recordString )
		for i in recordArray:
			self.accountRecord[i[0]] = i[1]

	def setRoleRecord( self, key, value ):
		"""
		保存游戏记录
		"""
		self.roleRecord[key] = value
		if not hasattr( self, "base" ):
			WARNING_MSG("Role entity not has base!!")
			return
		self.base.saveRoleRecord( cPickle.dumps( { key:value }, 2 ) )


	def queryAccountRecord( self, key ):
		"""
		查询游戏记录
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_ACCOUNT_RECORD_INIT_OVER ):
			self.client.onStatusMessage( csstatus.ROLE_RECORD_INIT_FAILED, "" )
			ERROR_MSG( "Role(%s)'s accountRecord init Failed!"%self.playerName )
			assert 0

		if not self.accountRecord.has_key( key ):
			return ""

		return self.accountRecord[key]


	def setAccountRecord( self, key, value ):
		"""
		保存游戏记录
		"""
		self.accountRecord[key] = value
		self.base.saveAccountRecord( cPickle.dumps( {key: value}, 2 ) )


	def queryRoleRecord( self, key ):
		"""
		查询游戏记录
		"""
		if not self.roleRecord.has_key( key ):
			return ""

		return self.roleRecord[key]

	def queryRoleRecordTime( self, key ):
		"""
		查询游戏记录次数
		"""
		record = self.queryRoleRecord( key )
		if record == "":
			return 0

		return int( record.split( "_" )[1] )

	def removeRoleRecord( self, key ):
		"""
		"""
		if key in self.roleRecord:
			del self.roleRecord[key]

	def updateShuijingRecord( self ):
		"""
		define method
		更新水晶记录
		"""
		self.lastShuijingTime = time.localtime()[2]

	def queryDartInfo( self, mailbox ):
		"""
		define method
		"""
#		dart_HP_Max						= self.popTemp("Dart_HP_Max")
		dart_destNpcClassName			= self.popTemp( "Dart_destNpcClassName" )
		dart_questID					= self.popTemp( "Dart_questID" )
		dart_eventIndex					= self.popTemp( "Dart_eventIndex" )
		dart_factionID					= self.popTemp( "Dart_factionID" )
		dart_level						= self.popTemp( "Dart_level" )
		dart_type						= self.popTemp( "Dart_type" )

		mailbox.onReceiveDartInfo( dart_destNpcClassName, dart_questID, dart_eventIndex, dart_factionID, dart_level, dart_type )


	def queryTeamCompetitionInfo( self, srcEntityID ):
		"""
		expose method
		"""
		if srcEntityID != self.id:
			return

		if self.queryTemp( "stored_pk_mode" ) is None:
			return

		self.getCurrentSpaceBase().queryCompetitionInfo( self.base )

	def queryTongCompetitionInfo( self, srcEntityID ):
		"""
		expose method
		"""
		if srcEntityID != self.id:
			return

		if self.queryTemp( "stored_pk_mode" ) is None:
			return

		if self.getCurrentSpaceBase().id != BigWorld.globalData[ "TongCompetitionID" ]:
			return
		self.getCurrentSpaceBase().queryTongCompInfo( self.base )

	def switchSpaceLineNumber( self, srcEntityID, lineNumber ):
		"""
		expose method
		切换当前线
		"""
		if srcEntityID != self.id or self.controlledBy is None or self.getState() == csdefine.ENTITY_STATE_FIGHT:
			return

		if self.vehicle and self.vehicle.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
			self.statusMessage( csstatus.TRANSPORT_FORBID_ON_DART )
			return

		spaceType = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		self.gotoSpaceLineNumber( spaceType, lineNumber, self.position, self.direction )

	def leaveDart( self, states, id ):
		"""
		define method
		离开镖车
		"""
		if not self.vehicle:
			return
		self.actCounterDec( states )
		self.alightVehicle()
		self.client.onDisMountDart()
		self.planesAllClients( "disDartEntity", ( id, 0 ) )

	def selectSuanGuaZhanBu( self, srcEntityID ):
		"""
		选择算卦占卜
		"""
		if srcEntityID != self.id:
			return

		# 这段代码本来在FuncSuanGuaZhanBu中，将其移动到此，以防止再出现诸如：CSOL-9799这样的问题 mushuang
		if not self.suanGuaZhanBuDailyRecord.checklastTime():				# 判断是否同一天
			self.suanGuaZhanBuDailyRecord.reset()
		if self.suanGuaZhanBuDailyRecord.getDegree() >= 1:					# 一天只能祈福一次
			self.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_LIMIT_NUM )
			return

		if self.payMoney( g_SuanGuaZhanBuLoader.getNeedMoney( self.level ), csdefine.CHANGE_MONEY_SUANGUAZHANBU ):		# 玩家扣除金钱
			self.suanGuaZhanBuDailyRecord.incrDegree()	# 算卦占卜次数加1
			self.spellTarget( g_SuanGuaZhanBuLoader.getRandomSkill(), self.id )


	def hasActivityFlag( self, flag ):
		"""
		是否有某活动记录标志
		"""
		return self.activityFlags & ( 1 << flag )


	def setActivityFlag( self, flag ):
		"""
		define method
		设置一个活动标记
		"""
		self.activityFlags = self.activityFlags | ( 1 << flag)
		self.broadcastActFlagsToTeammates( flag )

	def removeActivityFlag( self, flag ):
		"""
		取消一个活动标记
		"""
		self.activityFlags = self.activityFlags &~ ( 1 << flag )
		self.broadcastActFlagsToTeammates( flag )

	def getMapping( self ):
		return self.persistentMapping

	def query( self, key, default = None ):
		"""
		根据关键字查询mapping中与之对应的值

		@return: 如果关键字不存在则返回default值
		"""
		try:
			return self.persistentMapping[key]
		except KeyError:
			return default

	def set( self, key, value ):
		"""
		define method
		往一个key里写一个值

		@param   key: 任何PYTHON原类型(建议使用字符串)
		@param value: 任何PYTHON原类型(建议使用数字或字符串)
		"""
		self.persistentMapping[key] = value

	def remove( self, key ):
		"""
		define method
		移除一个与key相对应的值
		"""
		self.persistentMapping.pop( key, None )

	def addInt( self, key, value ):
		"""
		放一个key相对应的值里加一个值；
		注意：此方法并不检查源和目标的值是否匹配或正确
		"""
		v = self.queryInt( key )
		self.set( key, value + v )

	def queryInt( self, key ):
		"""
		根据关键字查询mapping中与之对应的值

		@return: 如果关键字不存在则返回0
		"""
		try:
			return self.persistentMapping[key]
		except KeyError:
			return 0

	def queryStr( self, key ):
		"""
		根据关键字查询mapping中与之对应的值

		@return: 如果关键字不存在则返回空字符串""
		"""
		try:
			return self.persistentMapping[key]
		except KeyError:
			return ""

	def getjkCardGiftResult( self, presentID):
		"""
		玩家领取新手卡奖励
		"""
		item = g_items.createDynamicItem( presentID )
		# 先判断能否加入背包
		checkReult = self.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD :
			self.base.onGetjkCardGiftFailed()					#通知服务器此次领取失败
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return
		self.addItem( item, csdefine.ADD_ITEM_TAKEJKCARDPRESENT )


	# ----------------------------------------------------------------
	# 新单人骑宠
	# ----------------------------------------------------------------
	def useVehicleItem( self, srcEntityID, uid ):
		"""
		Exposed Method
		使用骑宠物品
		@param uid: 物品唯一ID
		@type  uid:	int64
		@return None
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# 判断物品是否存在
		item = self.getItemByUid_( uid )
		if item is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		# 判断是否是骑宠物品
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_VEHICLE:
			self.statusMessage( csstatus.VEHICLE_ITEM_LAWLESS )
			return

		# 判断使用等级
		if self.level < item.getReqLevel():
			self.statusMessage( csstatus.VEHICLE_ITEM_LEVEL )
			return

		# 判断物品是否冻结
		if item.isFrozen():
			ERROR_MSG( "Item(%s, uid = %i, ownerName = %s, ownerDBID = %i) isFrozen!" % ( item.name(), item.uid, self.getName(), self.databaseID ) )
			return

		# 物品冻结
		item.freeze()
		# 通知base
		self.base.useVehicleItem( item )

	def onUseVehicleItemNotify( self, uid, state ):
		"""
		Define Method
		base使用骑宠物品通知
		"""
		# 判断物品是否存在
		item = self.getItemByUid_( uid )
		if item is None:
			ERROR_MSG( "Vehicle Item missed durning useing! playerName(%s), itemUID(%i)"%( self.playerName, uid ) )
			return

		# 物品解锁
		item.unfreeze()

		# 使用成功，移除物品
		if state:
			self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_USEVEHICLEITEM )


	#使用转换的骑宠物品
	def useTurnVehicleItem( self, srcEntityID, uid ):
		"""
		Exposed Method
		使用转换的骑宠物品
		@param uid: 物品唯一ID
		@type  uid:	int64
		@return None
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# 判断物品是否存在
		item = self.getItemByUid_( uid )
		if item is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		# 判断是否是转换的骑宠物品
		if item.getType() != ItemTypeEnum.ITEM_VEHICLE_TURN:
			self.statusMessage( csstatus.VEHICLE_ITEM_LAWLESS )
			return

		# 判断使用等级
		if self.level < item.getReqLevel():
			self.statusMessage( csstatus.VEHICLE_ITEM_LEVEL )
			return

		# 判断物品是否冻结
		if item.isFrozen():
			ERROR_MSG( "Item(%s, uid = %i, ownerName = %s, ownerDBID = %i) isFrozen!" % ( item.name(), item.uid, self.getName(), self.databaseID ) )
			return

		# 物品冻结
		item.freeze()
		# 通知base
		self.base.useTurnVehicleItem( item )

	def onUseTurnVehicleItemNotify( self, uid, state ):
		"""
		Define Method
		base使用转换骑宠物品通知
		"""
		# 判断物品是否存在
		item = self.getItemByUid_( uid )
		if item is None:
			ERROR_MSG( "Vehicle Item missed durning useing! playerName(%s), itemUID(%i)"%( self.playerName, uid ) )
			return

		# 物品解锁
		item.unfreeze()

		# 使用成功，移除物品
		if state:
			self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_VEHICLE_TO_ITEM )


	#激活骑宠相关
	def activateVehicle( self, vehicleData ):
		"""
		define method
		激活骑宠
		"""
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_LEVEL_TOO_HIGN )
			return
		if self.currAttrVehicleData["id"] == vehicleData["id"]:return
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		if self.queryTemp( "activateVehicleData", {} ) and self.intonating():return
		# 对自己释放一个激活骑宠的技能
		self.setTemp( "activateVehicleData", vehicleData )
		state = self.spellTarget( Const.VEHICLE_ACTIVATE_SKILLID, self.id )
		if state != csstatus.SKILL_GO_ON:
			self.popTemp( "activateVehicleData" )
			self.statusMessage( state )


	def onactivateVehicle( self, vehicleData ):
		"""
		激活骑宠成功
		"""
		vehicleData_attr = {"id":vehicleData["id"],
					"srcItemID":vehicleData["srcItemID"],
				    "level":vehicleData["level"],
				    "exp":vehicleData["exp"],
				    "deadTime":vehicleData["deadTime"],
				    "fullDegree":vehicleData["fullDegree"],
				    "type":vehicleData["type"],
				    "strength":vehicleData["strength"],
				    "intellect":vehicleData["intellect"],
				    "dexterity":vehicleData["dexterity"],
				     "corporeity":vehicleData["corporeity"]}
		self.currAttrVehicleData = vehicleData_attr
		self.addA_VehicleFDTimmer()
		#尝试骑乘
		if self.currVehicleData["type"] != csdefine.VEHICLE_TYPE_FLY and self.currVehicleData["id"] != vehicleData["id"]:
			self.conjureVehicle( vehicleData )

	def addA_VehicleFDTimmer( self ):
		"""
		加一个激活骑宠的饱腹度timmer
		"""
		if self.fd_aTimmerID:
			self.cancel( self.fd_aTimmerID )
		#加入饱腹度的倒计时判断
		disTime = self.currAttrVehicleData["fullDegree"] - int( time.time() )
		if disTime <= 0:
			disTime = 1
		if disTime > 7*24*3600:
			disTime = 7*24*3600
		self.fd_aTimmerID = self.addTimer( disTime, 0, ECBExtend.VEHICLE_ACTIVATE_FULLDEGREE_TIMMER_CBID )

	def onActivateVehicleFD( self,controllerID, userData ):
		"""
		激活的骑宠饱食度回调
		"""
		if self.currAttrVehicleData["fullDegree"] <= int( time.time() ):
			self.cancelActiveVehicle()

	def cancelActiveVehicle( self ):
		"""
		取消当前激活的骑宠
		"""
		if self.fd_aTimmerID:
			self.cancel( self.fd_aTimmerID )
		self.removeBuffByBuffID( Const.VEHICLE_ACTIVATE_BUFFID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def deactivateVehicle(self,srcEntityID ):
		"""
		取消激活骑宠
		Exposed Method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.cancelActiveVehicle()
		#如是陆行骑宠取消骑乘
		if self.currVehicleData["type"] != csdefine.VEHICLE_TYPE_FLY :
			self.cancelConjureVehicle()

	def actAndConjureVehicle( self, vehicleData ):
		"""
		define method
		激活骑宠
		"""
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_LEVEL_TOO_HIGN )
			return

		if self.queryTemp( "activateVehicleData", {} ) and self.intonating():return

		if self.currAttrVehicleData["id"] == vehicleData["id"] or vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY:
			self.conjureVehicle( vehicleData )
		else:
			self.setTemp( "activateVehicleData", vehicleData )
			state = self.spellTarget( Const.VEHICLE_ACTIVATE_SKILLID, self.id )
			if state != csstatus.SKILL_GO_ON:
				self.popTemp( "activateVehicleData" )
				self.statusMessage( state )

	#召唤骑宠相关
	def conjureVehicle( self, vehicleData ):
		"""
		Define Method
		通过指定的id召唤骑宠
		@param id: 骑宠在玩家数据的唯一标示符
		@type  id:	UINT8
		@return None
		"""
		if self.queryTemp( "conjureVehicleData", {} ) and self.intonating():
			ERROR_MSG( "Already in conjuring process! playerName(%s)"%self.playerName   )
			return

		id = vehicleData["id"]
		type = vehicleData["type"]
		# 是否能召唤
		state = VehicleHelper.canMount( self, id, type )
		if state != csstatus.SKILL_GO_ON:
			self.statusMessage( state )
			return

		# 清除原有骑宠buff
		self.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		# 对自己释放一个召唤骑宠的技能
		self.setTemp( "conjureVehicleData", vehicleData )
		skillID = Const.VEHICLE_CONJURE_SKILLID
		if type == csdefine.VEHICLE_TYPE_FLY:
			skillID = Const.VEHICLE_FLY_CONJURE_SKILLID
		state = self.spellTarget( skillID, self.id )
		if state != csstatus.SKILL_GO_ON:
			self.popTemp( "conjureVehicleData" )
			self.statusMessage( state )
			return

	def onConjureVehicle( self, vehicleData ):
		"""
		召唤骑宠成功
		"""
		# 注意此属性为Persistent属性，在骑宠buff reload时，可以利用这个属性恢复到骑乘状态
		vehicleData_speed = {"id":vehicleData["id"],
				"srcItemID":vehicleData["srcItemID"],
				"deadTime":vehicleData["deadTime"],
				"fullDegree":vehicleData["fullDegree"],
				"type":vehicleData["type"],
				"skPoint":vehicleData["skPoint"],
				"attrSkillBox":vehicleData["attrSkillBox"],
				"attrBuffs":vehicleData["attrBuffs"]}
		self.currVehicleData = vehicleData_speed

		skillID = VehicleHelper.getVehicleSkillID( vehicleData )

		if skillID == -1:
			ERROR_MSG( "Can't find vehicle binded skill! id(%s)"%vehicleData['id'] )
			return

		self.spellTarget( skillID, self.id )

		self.addC_VehicleFDTimmer()
		self.questVehicleActived( vehicleData["srcItemID"] )
		#激活属性加成骑宠
		if self.currAttrVehicleData["id"] != vehicleData["id"]:
			self.activateVehicle( vehicleData )


	def addC_VehicleFDTimmer(self):
		"""
		加一个召唤骑宠的饱腹度timmer
		"""
		if self.fd_cTimmerID:
			self.cancel( self.fd_cTimmerID )
		#加入饱腹度的倒计时判断
		disTime = self.currVehicleData["fullDegree"] - int( time.time() )
		if disTime <= 0:
			disTime = 1
		if disTime > 7*24*3600:
			disTime = 7*24*3600
		self.fd_cTimmerID = self.addTimer( disTime, 0, ECBExtend.VEHICLE_CONJURE_FULLDEGREE_TIMMER_CBID )

	def onConjureVehicleFD( self,controllerID, userData ):
		"""
		召唤的骑宠饱食度回调
		"""
		if self.currVehicleData["fullDegree"] <= int( time.time() ):
			self.cancelConjureVehicle()

	def cancelConjureVehicle(self):
		"""
		取消当前召唤的骑宠
		"""
		if self.fd_cTimmerID:
			self.cancel( self.fd_cTimmerID )
		for buffID in Const.VEHICLE_CONJURE_BUFFID:
			if len( self.findBuffsByBuffID( buffID ) ) > 0:
				self.removeBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				return


	#传功玩法
	def transVehicle( self, id, exp ):
		"""
		define method
		用自己的潜能换取骑宠的经验
		"""
		#当前激活的骑宠类型若是飞行骑宠，这是一个错误
		if self.currAttrVehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		#骑宠已达最高等级，不需要再传功
		if exp <= 0:
			self.statusMessage( csstatus.VEHICLE_MAX_LEVEL )
			return
		#玩家当前潜能点是否大于骑宠升级需要的经验
		if not self.hasPotential( exp ):
			self.statusMessage( csstatus.VEHICLE_NO_ENOUGH_POTENTIAL )
			return
		#判断传功骑宠是不是当前激活的骑宠
		if VehicleHelper.getCurrAttrVehicleID( self ) != id:
			self.statusMessage( csstatus.VEHICLE_NO_CURRENT_ACTIVATE )
			return
		#不能给高于自己6级的骑宠传功
		if self.currAttrVehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_NO_TRANS_LEVEL_MAX )
			return
		if self.queryTemp( "transVehicle_exp", None ) and self.intonating():
			return
		self.setTemp( "transVehicle_exp", (id,exp) )
		state = self.spellTarget( Const.VEHICLE_TRANS_SKILLID, self.id )
		if state != csstatus.SKILL_GO_ON:
			self.popTemp( "transVehicle_exp" )
			self.statusMessage( state )
			return

	def ontransVehicle( self, id, exp ):
		"""
		传功技能使用 成功
		"""
		if not self.hasPotential( exp ):
			self.statusMessage( csstatus.VEHICLE_NO_ENOUGH_POTENTIAL )
			return
		self.payPotential( exp, csdefine.CHANGE_POTENTIAL_TRANS )
		self.base.transAddVehicleExp( id, exp )

	def onVehiclePropertyNotify( self, id, level, strength, intellect, dexterity, corporeity, reason ):
		"""
		骑宠属性（从base端来的更新）数据更新 可能是传功或者是升阶引起的
		defined method
		"""
		#判断骑宠是不是当前激活的骑宠
		if VehicleHelper.getCurrAttrVehicleID( self ) != id:
			return
		#刷新之前先去掉之前的属性加成
		self.strength_value -= self.currAttrVehicleData["strength"]
		self.intellect_value -= self.currAttrVehicleData["intellect"]
		self.dexterity_value -=  self.currAttrVehicleData["dexterity"]
		self.corporeity_value -=  self.currAttrVehicleData["corporeity"]

		#属性刷新
		self.currAttrVehicleData["level"]     = level
		self.currAttrVehicleData["strength"]  = strength
		self.currAttrVehicleData["intellect"] = intellect
		self.currAttrVehicleData["dexterity"] = dexterity
		self.currAttrVehicleData["corporeity"]= corporeity
		#重载加属性buff
		for idx, buff in enumerate( self.attrBuffs ):
			spell = buff["skill"]
			if spell.getBuffID() == Const.VEHICLE_ACTIVATE_BUFFID:
				spell.doReload( self, buff )
				break
		# 最后计算属性值
		self.calcDynamicProperties()

	#骑宠升阶
	def upStepVehicle( self, srcEntityID, mainID, oblationID, needItem ):
		"""
		exposed method
		骑宠升阶
		"""
		if not self.hackVerify_( srcEntityID ) : return

		#判断玩家状态
		if self.state != csdefine.ENTITY_STATE_FREE:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STATE_ERROR )
			return

		#判断主宠是否满足条件
		if self.currAttrVehicleData["id"] != mainID: #判断主骑宠是不是当前激活的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_NOACT )
			return
		if self.currVehicleData["id"] == mainID: #判断主骑宠是不是当前骑乘的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_ISCONJURE )
			return

		#判断祭宠是否满足条件
		if self.currAttrVehicleData["id"] == oblationID: #判断祭宠是当前激活的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ACT )
			return
		if self.currVehicleData["id"] == oblationID: #判断祭宠是不是当前骑乘的骑宠
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ISCONJURE )
			return

		#道具要求
		items = self.findItemsByIDFromNK( needItem )
		if len(items) <= 0:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NO_ITEM )
			return
		#锁定道具
		order = items[0].getOrder()
		self.freezeItem_( order )
		self.setTemp( "VEHICLE_UP_STEP_ORDER", order )
		self.base.upStepVehicle( mainID, oblationID, needItem )

	def onUpStepVehicle( self ):
		"""
		define method
		升阶成功后回调
		"""
		#解锁
		order = self.popTemp( "VEHICLE_UP_STEP_ORDER", -1 )
		# 移除该物品
		self.removeItem_( order, 1, csdefine.DELETE_ITEM_UP_STEP )
		if order > 0:
			self.unfreezeItem_( order )


	#骑宠变回物品
	def vehicleToItem( self, vehicleData, needItem ):
		"""
		define method
		骑宠变回物品(来自base)
		"""
		#------------------判断背包空位-------------------
		orderIDs = self.getAllNormalKitbagFreeOrders()
		if len( orderIDs ) < 1 :
			self.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_NO_SPACE )
			return False
		#------------------判断有没有转换的道具------------
		itemID = U_DATA[ vehicleData["step"] ]["toItemNeedItem"]
		if needItem != itemID:
			return

		sitems = self.findItemsByIDFromNK( needItem )
		if len( sitems ) <= 0:
			return False

		#------------------删除转换的道具----------------
		if not self.removeItemTotal( needItem, 1, csdefine.DELETE_ITEM_VEHICLE_TO_ITEM ):
			return False

		#------------------创建新的物品-------------------
		newItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		if newItem is None: return False
		newItem.setAmount( 1 )
		vehicleData["exp"] = 0 #根据策划的要求变回物品的骑宠当前经验值归0
		#一些需要保存的骑宠属性
		newItem.set("type", ItemTypeEnum.ITEM_VEHICLE_TURN )
		newItem.set("reqLevel", max( 1,vehicleData["level"] - csconst.VEHICLE_DIS_LEVEL_MAX ) )
		newItem.set("param1",str( vehicleData["level"] ) )
		newItem.set("param2",str( vehicleData["exp"] ) )
		newItem.set("param3",str( vehicleData["fullDegree"] ) )
		newItem.set("param4",str( vehicleData["growth"] ) )
		newItem.set("param5",str( vehicleData["strength"] ) )
		newItem.set("param6",str( vehicleData["intellect"] ) )
		newItem.set("param7",str( vehicleData["dexterity"] ) )
		newItem.set("param8",str( vehicleData["corporeity"] ) )
		newItem.set("param9",str( vehicleData["deadTime"] ) )
		otherInfo = str( vehicleData["step"] )+ ";" + str( vehicleData["type"] )+ ";" + str( vehicleData["nextStepItemID"] ) + ";" + str( vehicleData["skPoint"] )+ ";" + str( vehicleData["attrSkillBox"] ) + ";" + str( vehicleData["attrBuffs"] )
		newItem.set("param10",otherInfo )
		self.addItemByOrderAndNotify_( newItem, self.getNormalKitbagFreeOrder(), csdefine.ADD_ITEM_VEHICLE_TO_ITEM )
		#通知base 删除骑宠
		self.base.vehicleToItemSuc( vehicleData["id"] )


	#骑宠其他玩法
	def addVehicleBuff( self, id, buff ):
		"""
		添加骑宠buff
		defined method
		"""
		if self.currVehicleData is None:
			return
		self.currentVehicleBuffIndexs.append( buff["index"] )
		self.base.addVehicleBuff( id, buff )

	def retractVehicle( self, srcEntityID ):
		"""
		收回骑宠, 如果需要撤回骑宠，请使用此接口
		Exposed Method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

	def addVehicleSkPoint( self, id, skPoint ):
		"""
		增加骑宠技能点
		defined method
		"""
		self.base.addVehicleSkPoint( id, skPoint )

	def onVehicleSkPointNotify( self, id, skPoint ):
		"""
		骑宠技能点更新
		defined method
		"""
		if VehicleHelper.getCurrVehicleID( self ) != id: return
		self.currVehicleData["skPoint"] = skPoint

	def feedVehicle( self, id, srcItemID ):
		"""
		骑宠喂食
		defined method
		"""
		fodders = g_vehicleExp.getFodderID( srcItemID )
		item = None
		for f in fodders:
			item = self.findItemFromNKCK_( f )
			if not item is None:
				break
		if item is None:
			# 身上没有合适的草料
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return

		lifeTime = item.getLifeTime()
		self.base.addVehicleDeadTime( id, lifeTime )

		# 移除该物品
		item.setAmount( item.getAmount() - 1, self, csdefine.DELETE_ITEM_FEEDVEHICLE )

	#骑宠饱腹度相关
	def onUpdateVehicleFullDegree( self, id, fullDegree ):
		"""
		Define Method
		骑宠饱腹度更新
		"""
		if VehicleHelper.getCurrVehicleID( self ) == id:
			self.currVehicleData["fullDegree"] = fullDegree
			self.addC_VehicleFDTimmer()
		if VehicleHelper.getCurrAttrVehicleID( self ) == id:
			self.currAttrVehicleData["fullDegree"] = fullDegree
			self.addA_VehicleFDTimmer()

	def canDomesticate(self):
		"""
		能否喂食饱腹度
		"""
		if self.state == csdefine.ENTITY_STATE_FREE:
			return True
		return False

	def domesticateVehicle( self, srcEntityID, id, needItemID, count ):
		"""
		exposed method
		客户端调用喂食骑宠饱腹度
		"""
		if not self.hackVerify_( srcEntityID ) : return

		if not self.canDomesticate(): return

		items = self.findItemsByIDFromNK( needItemID )
		scount = 0
		fullDegree = 0
		for item in items:
			scount += item.getAmount()
			fullDegree = item.query( "fullDegree", 0 )
		#数量不足
		if scount < count:
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return
		# 移除该物品
		self.removeItemTotal(  needItemID, count, csdefine.DELETE_ITEM_DOMESTICATEVEHICLE )
		self.base.addVehicleFullDegree( id, fullDegree*count )

	def addVehicleSkill( self, id, skillID ):
		"""
		骑宠学习技能
		"""
		self.base.addVehicleSkill( id, skillID )

	def onVehicleAddSkillNotify( self, id, skillID ):
		"""
		Define Method
		骑宠增加技能通知
		"""
		if VehicleHelper.getCurrVehicleID( self ) != id: return
		self.currVehicleData["attrSkillBox"].append( skillID )

		if not g_skills.has( skillID ):
			WARNING_MSG( "Skills(%i) does not exist!" % skillID )
			return

		skill = g_skills[skillID]
		skill.attach( self )

		actPet = self.pcg_getActPet()
		if actPet:
			vehicleJoyancyEffect = self.queryTemp( "vehicleJoyancyEffect", 0.0 )
			pet = actPet.entity
			pet.onVehicleAddSkills( [skillID], vehicleJoyancyEffect )

	def updateVehicleSkill( self, id, oldSkillID, newSkillID ):
		"""
		技能升级
		"""
		self.base.updateVehicleSkill( id, oldSkillID, newSkillID )

	def onUpdateVehicleSkillNotify( self, id, oldSkillID, newSkillID ):
		"""
		Define Method
		骑宠更新技能通知
		"""
		if VehicleHelper.getCurrVehicleID( self ) != id: return
		currVehicleSkillIDs = VehicleHelper.getCurrVehicleSkillIDs( self )
		if oldSkillID not in currVehicleSkillIDs: return
		index = currVehicleSkillIDs.index( oldSkillID )
		self.currVehicleData["attrSkillBox"][index] = newSkillID

		if not g_skills.has( oldSkillID ):
			WARNING_MSG( "Skills(%i) does not exist!" % oldSkillID )
			return

		if not g_skills.has( newSkillID ):
			WARNING_MSG( "Skills(%i) does not exist!" % newSkillID )
			return

		oldSkill = g_skills[oldSkillID]
		self.setTemp( "SAME_TYPE_SKILL_REPLACE", True )
		oldSkill.detach( self )
		self.setTemp( "SAME_TYPE_SKILL_REPLACE", False )
		newSkill = g_skills[newSkillID]
		newSkill.attach( self )

		actPet = self.pcg_getActPet()
		if actPet:
			vehicleJoyancyEffect = self.queryTemp( "vehicleJoyancyEffect", 0.0 )
			pet = actPet.entity
			pet.onVehicleRemoveSkills( [oldSkillID], vehicleJoyancyEffect )
			pet.onVehicleAddSkills( [newSkillID], vehicleJoyancyEffect )

	def freeVehicle( self, srcEntityID, id ):
		"""
		Exposed method
		骑宠放生
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if VehicleHelper.getCurrAttrVehicleID( self ) == id:
			return
		if VehicleHelper.getCurrVehicleID( self ) == id:
			return

		self.base.freeVehicle( id )

	# ----------------------------------------------------------------
	# Roll
	# ----------------------------------------------------------------
	def setRollState( self, srcEntityID, state ):
		"""
		exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.rollState = state


	def buyTSItem( self, uid, NPCbaseMailbox, itemID, count, price ):
		"""
		define method
		"""
		#if self.getNormalKitbagFreeOrderCount() <= 0:
		#	return

		item = g_items.createDynamicItem( itemID , count )

		if self.checkItemsPlaceIntoNK_( [item] ) != csdefine.KITBAG_CAN_HOLD:
			self.statusMessage( csstatus.KITBAG_IS_FULL )
			return

		NPCbaseMailbox.buyTSItem( uid, self.base, self.getName(), self.money, self.databaseID, itemID, count, price )

	def onReceiveTSItem( self, item, price ):
		"""
		define method
		"""
		self.addMoney( -price, csdefine.CHANGE_MONEY_RECEIVETSITEM )
		self.addItem( item, reason = csdefine.ADD_ITEM_SALEGOODS )


	def addTSItem( self, uid, price, NPCbaseMailbox ):
		"""
		define method
		"""
		item = self.getItemByUid_( uid )
		if item is None:
			return

		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.TISHOU_FORBID_CANNOT_GIVE_ITEM, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return
		if item.isBinded():
			self.statusMessage( csstatus.TISHOU_FORBID_FOR_BIND_ITEM )
			return
		if item.isFrozen():
			self.statusMessage( csstatus.TISHOU_FORBID_FOR_FREEZE_ITEM )
			return
		if item.reqYinpiao() != 0:
			self.statusMessage( csstatus.TISHOU_FORBID_FOR_YINPIAO_ITEM )
			return

		itemType= item.getTsItemType()

		level	= item.getReqLevel()
		quality = item.getQuality()

		metier = ""
		if csdefine.CLASS_FIGHTER in item.queryReqClasses():
			metier += csconst.TI_SHOU_CLASS_FIGHTER
		if csdefine.CLASS_SWORDMAN in item.queryReqClasses():
			metier += csconst.TI_SHOU_CLASS_SWORDMAN
		if csdefine.CLASS_ARCHER in item.queryReqClasses():
			metier += csconst.TI_SHOU_CLASS_ARCHER
		if csdefine.CLASS_MAGE in item.queryReqClasses():
			metier += csconst.TI_SHOU_CLASS_MAGE

		self.incRoleProcess()
		NPCbaseMailbox.addTSItem( item, price, itemType, level, quality, metier, self.databaseID, self.base, self.recordProcess )

	def onAddTSItem( self, uid ):
		"""
		define method
		"""
		self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_SALEGOODS )


	def takeTSItem( self, uid, NPCbaseMailbox, itemID, count ):
		"""
		define method
		"""
		#if self.getNormalKitbagFreeOrderCount() <= 0:
		#	return
		item = g_items.createDynamicItem( itemID , count )

		if self.checkItemsPlaceIntoNK_( [item] ) != csdefine.KITBAG_CAN_HOLD:
			self.statusMessage( csstatus.KITBAG_IS_FULL )
			return
		self.incRoleProcess()
		NPCbaseMailbox.takeTSItem( uid, self.base, self.databaseID, self.recordProcess, itemID, count )


	def addTSPet( self, dbid, price, NPCbaseMailbox ):
		"""
		define method
		"""
		if not self.pcg_petDict.has_key( dbid ):
			HACK_MSG( "错误的宠物dbid。" )
			return
		if self.pcg_isPetBinded( dbid ):
			self.statusMessage( csstatus.PET_HAD_BEEN_BIND )
			return
		if price > csconst.ROLE_MONEY_UPPER_LIMIT:
			HACK_MSG( "设置的摆摊宠物价格过高。" )
			return

		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :	# 如果要摆摊出售的宠物在出战中，则先回收
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )
			return
		if self.pcg_isTradingPet_( dbid ):
			self.statusMessage( csstatus.TISHOU_FORBID_FOR_TRADING_PET )
			return
		if self.queryTemp( "pcg_conjuring_dbid", 0 ) == dbid:
			self.statusMessage( csstatus.TISHOU_FORBID_FOR_CONJURING_PET )
			return
		self.incRoleProcess()
		self.base.addTSPet( dbid, price, NPCbaseMailbox, self.recordProcess )

	def takeTSPet( self, dbid, NPCbaseMailbox ):
		"""
		define method
		"""
		self.incRoleProcess()
		NPCbaseMailbox.takeTSPet( dbid, self.base, self.databaseID, self.recordProcess )

	def buyTSPet( self, dbid, NPCbaseMailbox, price ):
		"""
		define method
		"""
		if self.pcg_isFull():
			self.statusMessage( csstatus.PETCAGE_IS_FULL )
			return
		NPCbaseMailbox.buyTSPet( dbid, self.base, self.getName(), self.level, self.money, self.databaseID, price )

	def buyTSItemFromTishouMgr( self, srcEntityID, uid, itemID , count, price ):
		"""
		exposed method
		"""
		item = g_items.createDynamicItem( itemID , count )

		if self.checkItemsPlaceIntoNK_( [item] ):
			self.statusMessage( csstatus.KITBAG_IS_FULL )
			return
		BigWorld.globalData["TiShouMgr"].buyTSItemFromTishouMgr( self.base, self.databaseID, uid, itemID , count, price )

	def buyTSPetFromTishouMgr( self, srcEntityID, dbid, price ):
		"""
		exposed method
		"""
		if self.pcg_isFull():
			self.statusMessage( csstatus.PETCAGE_IS_FULL )
			return
		BigWorld.globalData["TiShouMgr"].buyTSPetFromTishouMgr( self.base, self.databaseID,  dbid, price )

	def createTSNPC( self, srcEntityID, npcType, shopName ):
		"""
		exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if not self.canVendInArea():
			self.statusMessage( csstatus.TISHOU_FORBID_AREA )
			return
		if self.level < 15:
			self.statusMessage( csstatus.TISHOU_FORBID_LEVEL )
			return

		if self.isState( csdefine.ENTITY_STATE_VEND ) :
			self.statusMessage( csstatus.TISHOU_FORBID_VENDING )
			return

		if BigWorld.globalData.has_key( "TiShouSystemIsAllow" ) and BigWorld.globalData["TiShouSystemIsAllow"] == "0":
			self.statusMessage( csstatus.TISHOU_TEMP_CLOSE )
			return

		mapName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		self.createNPCObjectFormBase( mapName, csconst.TISHOU_NPC_CLASSNAME, self.position, self.direction, { "ownerDBID": self.databaseID, "ownerName":self.getName(), "shopName": shopName, "destroyTime" : int( time.time() + 3600 * 24 ), "modelNumber" : Const.tsNpcs[npcType] } )
		BigWorld.globalData["TiShouMgr"].addNewTiShou( self.databaseID, self.getName(), shopName, time.time(), Const.tsNpcs[npcType], mapName, str(self.position) )
		self.addFlag( csdefine.ROLE_FLAG_TISHOU )
		self.statusMessage( csstatus.TISHOU_ACTION_SUCCESSFUL_NOTICE )

	# ----------------------------------------------------------------
	# 等级限制流通物品
	# ----------------------------------------------------------------
	def canGiveItem( self, itemID ):
		"""
		特定物品的特定等级限制。
		判断玩家是否能流通一个物品，包括交易、摆摊、邮寄、帮会仓库等
		"""
		if itemID in g_levelResItems and self.level < csconst.SPECIFIC_ITEM_GIVE_LEVEL: return False
		return True

	def canVendInArea( self ):
		"""
		指定区域能否摆摊
		"""
		pos = self.position
		x = pos[0]
		y = pos[1]
		z = pos[2]
		space = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if space in roleVendData.keys():
			data = roleVendData.get( space )
			for a, b in data.items():
				if not len( a ): return False
				if not len( b ): return False
				if abs( x - a[0] ) <= b[0] and abs( y - a[1] ) <= b[1] and abs( z - a[2] ) <= b[2]:
					return True
		return False

	def sellPointCard( self, srcEntityID, cardNo, pwd, severName, cardPrice ):
		"""
		exposed method
		玩家寄售点卡
		"""
		if self.money < csconst.SELL_POINT_CARD_YAJIN:
			self.statusMessage( csstatus.POINT_CARD_FORBID_NOT_ENOUGH_MONEY )
			return
		if not BigWorld.globalData.has_key( "serverName" ):
			self.statusMessage( csstatus.POINT_CARD_FORBID_CELL_HAS_NOT_NAME )
			return
		self.base.sellPointCard( cardNo, pwd, BigWorld.globalData["serverName"], cardPrice )


	def onSellPointCard( self ):
		"""
		define method
		寄售点卡成功，收取押金
		"""
		self.payMoney( csconst.SELL_POINT_CARD_YAJIN, csdefine.CHANGE_MONEY_POINT_CARD_YAJIN )

	def buyPointCard( self, srcEntityID, cardNo ):
		"""
		exposed method
		购买点卡
		"""
		self.base.buyPointCard( cardNo, self.money )

	def onBuyPointCard( self, price ):
		"""
		购买点卡回调。
		不管是否成功都先收取费用。如果不成功，后面会归还。
		"""
		self.payMoney( price, csdefine.CHANGE_MONEY_POINT_CARD_YAJIN )


	def incRoleProcess( self ):
		"""
		增加角色进度值
		"""
		self.recordProcess += 1


	def startTS( self ):
		"""
		define method
		开始替售
		"""
		self.writeToDB()

	def stopTS( self ):
		"""
		define method
		结束寄售
		"""
		pass


	def testTakeTishouItems( self, items ):
		"""
		define method
		判定能否加入所有替售物品
		"""
		checkReult = self.checkItemsPlaceIntoNK_( items )
		if checkReult == csdefine.KITBAG_CAN_HOLD :
			self.incRoleProcess()
			BigWorld.globalData["TiShouMgr"].roleHadTakeTishouItems( self.databaseID, self.recordProcess )
			for item in items:
				self.addItem( item, csdefine.ADD_ITEM_SALEGOODS  )
		else:
			self.statusMessage( csstatus.KITBAG_IS_FULL )

	def testTakeTishouPets( self, pets ):
		"""
		define method
		取走替售宠物
		"""
		if self.pcg_isOverbrim( len( pets ) ):
			self.statusMessage( csstatus.PETCAGE_IS_FULL )
			return
		self.incRoleProcess()
		self.base.testTakeTishouPets( pets )
		BigWorld.globalData["TiShouMgr"].roleHadTakeTishouPets( self.databaseID, self.recordProcess )

	def addTSMoney( self, money ):
		"""
		define method
		增加替售所得金钱
		"""
		self.gainMoney( money, csdefine.CHANGE_MONEY_RECEIVETS_MONEY )
		BigWorld.globalData["TiShouMgr"].onTiShouMoneyTaked( self.databaseID )


	def addTSFlag( self ):
		"""
		define method
		给玩家增加替售标志
		"""
		self.addFlag( csdefine.ROLE_FLAG_TISHOU )

	def removeTSFlag( self ):
		"""
		define method
		移除玩家替售标志
		"""
		self.removeFlag( csdefine.ROLE_FLAG_TISHOU )

	def cometoTSNPC( self, srcEntityID, way ):
		"""
		exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return

		if not self.hasFlag( csdefine.ROLE_FLAG_TISHOU ):
			self.statusMessage( csstatus.TISHOU_NOT_FIND )
			return

		if way == 0:
			if not self.removeItemTotal(  50101002, 1, csdefine.DELETE_ITEM_SALEGOODS ):
				if not self.removeItemTotal(  50101003, 1, csdefine.DELETE_ITEM_SALEGOODS ):
					self.statusMessage( csstatus.FLY_ITEM_NOT_FIND )
					return

		BigWorld.globalData["TiShouMgr"].playerCometoTiShouNpc( self.base, self.databaseID, way )


	# ----------------------------------------------------------------
	# 切磋系统
	# ----------------------------------------------------------------
	def isQieCuoTarget( self, targetID ):
		"""
		判断目标ID是否是当前切磋ID
		"""

		if VehicleHelper.isFlying( self ): return False # 如果在飞，一切免谈
		if self.qieCuoTargetID != targetID: return False
		if self.qieCuoState != csdefine.QIECUO_FIRE: return False
		return True

	def canQieCuo( self, target ):
		"""
		判断是否能邀请与目标切磋
		"""
		if target is None: return False
		if not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return False
		if VehicleHelper.isFlying( self ):
			self.statusMessage( csstatus.CANT_QIECUO_WHEN_FLYING )
			return False

		if VehicleHelper.isFlying( target ):
			self.statusMessage( csstatus.CANT_QIECUO_WHEN_TARGET_FLYING )
			return False

		# 判断当前地图能否切磋
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canQieCuo:
			self.statusMessage( csstatus.QIECUO_REFUSE_IN_THIS_SPACE )
			return False


		if self.spaceID != target.spaceID:
			self.statusMessage( csstatus.QIECUO_TARGET_SOFAR )
			return False
		if self.state != csdefine.ENTITY_STATE_FREE:
			self.statusMessage( csstatus.QIECUO_SELF_NOFREE )
			return False
		if target.state != csdefine.ENTITY_STATE_FREE:
			self.statusMessage( csstatus.QIECUO_TARGET_NOFREE )
			return False
		return True

	def requestQieCuo( self, srcEntityID, targetID ):
		"""
		Expoesd Method
		玩家请求切磋
		"""
		if srcEntityID != self.id: return

		target = BigWorld.entities.get( targetID )
		if target is None: return

		if self.qieCuoState != csdefine.QIECUO_NONE:
			self.statusMessage( csstatus.QIECUO_SELF_NOFREE )
			return False
		if target.qieCuoState != csdefine.QIECUO_NONE:
			self.statusMessage( csstatus.QIECUO_TARGET_NOFREE )
			return False

		if self.position.flatDistTo( target.position ) > csconst.QIECUO_REQUEST_MAXDIS:
			self.statusMessage( csstatus.QIECUO_TARGET_SOFAR )
			return False

		if not self.canQieCuo( target ): return

		self.addTimer( Const.QIECUO_CONFIRM_TIME, 0, ECBExtend.QIECUO_CONFIRM_CBID )

		self.changeQieCuoTarget( targetID )
		target.changeQieCuoTarget( self.id )
		self.changeQieCuoState( csdefine.QIECUO_INVITE )
		target.changeQieCuoState( csdefine.QIECUO_BEINVITE )

	def replyQieCuo( self, srcEntityID, targetID, isQieCuo ):
		"""
		Exposed Method
		回复切磋申请
		"""
		if srcEntityID != self.id: return

		target = BigWorld.entities.get( targetID )
		if target is None:
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			return

		if self.qieCuoState != csdefine.QIECUO_BEINVITE or target.qieCuoState != csdefine.QIECUO_INVITE:
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			target.changeQieCuoState( csdefine.QIECUO_NONE )
			return

		if not isQieCuo:
			target.statusMessage( csstatus.QIECUO_REFUSE, self.getName() )
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			target.changeQieCuoState( csdefine.QIECUO_NONE )
			return

		if not self.canQieCuo( target ):
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			target.changeQieCuoState( csdefine.QIECUO_NONE )
			return

		self.changeQieCuoState( csdefine.QIECUO_READY )
		target.changeQieCuoState( csdefine.QIECUO_READY )

	def onQieCuoConfirm( self, controllerID, userData ):
		"""
		邀请方18秒延迟取消切磋
		"""
		if self.qieCuoState == csdefine.QIECUO_INVITE:
			target = BigWorld.entities.get( self.qieCuoTargetID )
			if target is not None:
				target.statusMessage( csstatus.QIECUO_REFUSE, self.getName() )
			self.changeQieCuoState( csdefine.QIECUO_NONE )

	def inviteQieCuo( self ):
		"""
		邀请切磋
		"""
		msg = random.choice( csconst.QIECUO_REQUEST_SAY_MSGS )
		self.chat_handleMessage( csdefine.CHAT_CHANNEL_NEAR, "", msg, [] )
		self.planesAllClients( "onRequestQieCuo", ( self.qieCuoTargetID, ) )

	def beInviteQieCuo( self ):
		"""
		被邀请切磋
		"""
		self.client.onReceivedQieCuo( self.qieCuoTargetID )

	def readyQieCuo( self ):
		"""
		准备切磋
		"""
		self.addTimer( 0.0, Const.QIECUO_NOTIFY_INTERVAL_TIME, ECBExtend.QIECUO_NOTIFY_CBID )

	def onQieCuoTimerNotify( self, controllerID, userData ):
		"""
		切磋1秒timer通知
		"""
		target = BigWorld.entities.get( self.qieCuoTargetID )
		if target is None:
			self.cancel( controllerID )
			self.removeTemp( "qieCuoNotifyTime" )
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			return

		if not self.canQieCuo( target ):
			self.cancel( controllerID )
			self.removeTemp( "qieCuoNotifyTime" )
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			return

		qieCuoNotifyTime = self.queryTemp( "qieCuoNotifyTime", 0 )
		if qieCuoNotifyTime >= Const.QIECUO_NOTIFY_TIME:
			self.cancel( controllerID )
			self.removeTemp( "qieCuoNotifyTime" )
			self.changeQieCuoState( csdefine.QIECUO_FIRE )
			self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, self.qieCuoTargetID )
			return

		noteTime = Const.QIECUO_NOTIFY_INTERVAL_TIME + qieCuoNotifyTime
		self.setTemp( "qieCuoNotifyTime", noteTime )
		noticeTime = Const.QIECUO_NOTIFY_TIME - qieCuoNotifyTime
		self.statusMessage( csstatus.QIECUO_NOTIFY_TIME, noticeTime )

	def startQieCuo( self ):
		"""
		开始切磋
		"""
		self.statusMessage( csstatus.QIECUO_START )
		self.qieCuoTimer = self.addTimer( 0, Const.QIECUO_CHECK_INTERVAL_TIME, ECBExtend.QIECUO_CHECK_CBID )

	def onQieCuoTimerCheck( self, controllerID, userData ):
		"""
		切磋timer检测,每10秒检测一次
		"""
		target = BigWorld.entities.get( self.qieCuoTargetID )
		if target is None:
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			return
		if self.state == csdefine.ENTITY_STATE_DEAD or target.state == csdefine.ENTITY_STATE_DEAD\
			or self.spaceID != target.spaceID or ( not self.checkViewRange( target ) ):
			self.changeQieCuoState( csdefine.QIECUO_NONE )
			return

	def endQieCuo( self ):
		"""
		结束切磋
		"""
		qieCuoTarget = BigWorld.entities.get(self.qieCuoTargetID)
		if qieCuoTarget:
			g_fightMgr.breakEnemyRelation( self, qieCuoTarget )
			self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, self.qieCuoTargetID )
		
		self.qieCuoTargetID = 0
		self.statusMessage( csstatus.QIECUO_END )
		if self.qieCuoTimer != 0:
			self.cancel( self.qieCuoTimer )
			self.qieCuoTimer = 0
		self.planesAllClients( "onQieCuoEnd", () )

	def removeBuffOnQieCuoEnd( self ):
		"""
		切磋结束移除恶性BUFF
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD: return
		buffIndexs = self.getBuffIndexsByEffectType( csdefine.SKILL_EFFECT_STATE_MALIGNANT )
		buffIndexs.reverse()
		for index in buffIndexs:
			self.removeBuff( index, [csdefine.BUFF_INTERRUPT_NONE] )

	def changeQieCuoState( self, state ):
		"""
		Define method
		切磋状态改变
		"""
		if self.qieCuoState == state: return
		oldState = self.qieCuoState
		self.qieCuoState = state
		self.onQieCuoStateChange( oldState, state )

	def onQieCuoStateChange( self, oldState, newState ):
		"""
		切磋状态改变
		"""
		if newState == csdefine.QIECUO_INVITE:
			self.inviteQieCuo()
		elif newState == csdefine.QIECUO_BEINVITE:
			self.beInviteQieCuo()
		elif newState == csdefine.QIECUO_READY:
			self.readyQieCuo()
		elif newState == csdefine.QIECUO_FIRE:
			self.startQieCuo()
		elif newState == csdefine.QIECUO_NONE:
			if oldState == csdefine.QIECUO_FIRE:
				self.removeBuffOnQieCuoEnd()
			self.endQieCuo()

	def changeQieCuoTarget( self, targetID ):
		"""
		Define Method
		改变切磋ID
		"""
		if self.qieCuoTargetID == targetID: return
		self.qieCuoTargetID = targetID
		target = BigWorld.entities.get( targetID )

	def loseQieCuo( self ):
		"""
		切磋结束，有胜负的
		"""
		target = BigWorld.entities.get( self.qieCuoTargetID )
		if target is None: return

		# 给自己和目标及宠物加无敌Buff
		self.changeQieCuoState( csdefine.QIECUO_NONE )
		self.spellTarget( Const.QIECUO_PROJECT_SKILLID, self.id )

		actPet = self.pcg_getActPet()
		if actPet:
			pet = actPet.entity
			self.spellTarget( Const.QIECUO_PROJECT_SKILLID, pet.id)

		msg = random.choice( csconst.QIECUO_LOSE_SAY_MSGS )
		self.chat_handleMessage( csdefine.CHAT_CHANNEL_NEAR, "", msg, [] )

		target.changeQieCuoState( csdefine.QIECUO_NONE )
		self.spellTarget( Const.QIECUO_PROJECT_SKILLID, target.id )

		targetActPet = target.pcg_getActPet()
		if targetActPet:
			targetPet = targetActPet.entity
			targetPet.setActionMode( self.id, csdefine.PET_ACTION_MODE_FOLLOW )

		msg = random.choice( csconst.QIECUO_WIN_SAY_MSGS )
		target.chat_handleMessage( csdefine.CHAT_CHANNEL_NEAR, "", msg, [] )

	def addDayStat( self, recordType ):
		"""
		新增记录统计
		"""
		g_Statistic.refreshDayStat( self )	# 新增记录之前刷新一下

		record = self.statistic.get( recordType, 0 )		# 获取某项记录次数
		if record == 0:
			self.statistic[recordType] = 1
		else:
			self.statistic[recordType] = record + 1

	def getStatistic( self, srcEntityID ):
		"""
		<Exposed/>
		获取玩家统计数据
		"""
		if srcEntityID != self.id: return
		sendStat = self.statistic.copy()	# 获取记录的统计
		sendStat[cschannel_msgs.SHUIJING_INFO_1] = self.queryRoleRecordTime( "shuijing_record" )
		sendStat[cschannel_msgs.TIAN_GUAN_MONSTER_DEF_2] = self.queryRoleRecordTime( "tianguan_record" )
		sendStat[cschannel_msgs.YA_YU_VOICE18] = self.queryRoleRecordTime( "yayu_record" )
		self.client.receiveStatistic( sendStat )

	def onRobotVerifyResult( self, statusID ):
		"""
		Define method.
		反外挂验证结果，根据statusID给奖励或惩罚
		"""
		#DEBUG_MSG( "--->>>player( %s ), result( %i )" % ( self.getName(), statusID ) )
		self.statusMessage( statusID )
		if statusID == csstatus.ANTI_ROBOT_FIGHT_VERIFY_ERROR:		# 进监狱
			self.prisonHunt()
		elif statusID == csstatus.ANTI_ROBOT_FIGHT_VERIFY_RIGHT:	# 给奖励
			# 随机给经验或潜能奖励
			if random.random() < 0.5:
				self.addExp( 497+100*( self.level**1.2 ), csdefine.CHANGE_EXP_ROBOT_VERIFY_RIGHT )
			else:
				self.addPotential( self.level*100, csdefine.CHANGE_POTENTIAL_ROBOT_VERIFY )

	def enterAutoFight( self, srcEntityID ):
		"""
		Exposed method.
		进入自动战斗
		"""
		if srcEntityID != self.id:
			return
		self.addFlag( csdefine.ROLE_FLAG_AUTO_FIGHT )

	def leaveAutoFight( self, srcEntityID ):
		"""
		Exposed method.
		离开自动战斗
		"""
		if srcEntityID != self.id:
			return
		self.removeFlag( csdefine.ROLE_FLAG_AUTO_FIGHT )

	def isInAutoFight( self ):
		"""
		是否在自动战斗中
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_AUTO_FIGHT )

	def openAutoFight( self, srcEntityID ):
		"""
		开放自动战斗功能
		"""
		if srcEntityID != self.id:
			return
		self.hasAutoFight = True	# 表示自动战斗功能已经开放

	def addCollectionItem( self, srcEntityID, collectionItem ):
		"""
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if self.iskitbagsLocked(): return

		if self.money < collectionItem.collectAmount * collectionItem.price:
			self.statusMessage( csstatus.MONEY_NOT_ENOUGH )
			return
		collectionItem.collectorDBID = self.databaseID
		BigWorld.globalData["CollectionMgr"].addCollectionItem( collectionItem, self.base )


	def onAddCollectionItem( self, collectionItem ):
		"""
		define method
		"""
		if self.payMoney( collectionItem.collectAmount * collectionItem.price, csdefine.CHANGE_MONEY_BUYCOLLECTIONITEM ):
			BigWorld.globalData["CollectionMgr"].onAddCollectionItem( collectionItem, self.base )


	def removeCollectionItem( self, srcEntityID, uid ):
		"""
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if self.iskitbagsLocked(): return

		BigWorld.globalData["CollectionMgr"].removeCollectionItem( uid, self.databaseID, self.base )


	def onRemoveCollectionItem( self, collectionItem ):
		"""
		define method
		"""
		if self.gainMoney( ( collectionItem.collectAmount - collectionItem.collectedAmount ) * collectionItem.price, csdefine.CHANGE_MONEY_CANCELCOLLECTIONITEM ):
			BigWorld.globalData["CollectionMgr"].onRemoveCollectionItem( collectionItem.uid, self.databaseID, self.base )


	def takeCollectedItems( self, srcEntityID ):
		"""
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		BigWorld.globalData["CollectionMgr"].takeCollectedItems( self.databaseID, self.base )


	def onTakeCollectedItems( self, collectionItems ):
		"""
		define method
		"""
		items = []
		for i in collectionItems:
			items.append(  g_items.createDynamicItem( i.itemID , i.collectedAmount ) )

		checkReult = self.checkItemsPlaceIntoNK_( items )
		if checkReult == csdefine.KITBAG_CAN_HOLD :
			for item in items:
				self.addItem( item, csdefine.ADD_ITEM_COLLECTION  )

			BigWorld.globalData["CollectionMgr"].onTakeCollectedItems( self.databaseID, self.base )
		else:
			self.statusMessage( csstatus.KITBAG_IS_FULL )

	def queryCollectionInfo( self, srcEntityID, collectorDBID ):
		"""
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return

		BigWorld.globalData["CollectionMgr"].queryCollectionInfo( collectorDBID, self.base )


	def sellCollectionItems( self, srcEntityID, collectionItems, collectorDBID ):
		"""
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# 如果在吟唱则中则返回
		if self.attrIntonateSkill:
			self.statusMessage( TI_SHOU_SELL_FORBIDDEN_IN_INTONATING )
			return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		BigWorld.globalData["CollectionMgr"].sellCollectionItems( collectionItems, collectorDBID, self.base  )


	def onSellCollectionItems( self, collectionItems, collectorDBID ):
		"""
		define method
		"""
		money = 0
		for i in collectionItems:
			if self.countItemTotalWithBinded_( i.itemID, False ) < i.collectAmount:
				return
			money += i.collectAmount * i.price

		if not self.gainMoney( money, csdefine.CHANGE_MONEY_SELLCOLLECTIONITEM ):
			self.statusMessage( csstatus.SELL_ITEM_FORBID_MONEY_IS_FULL )
			return

		for i in collectionItems:
			self.removeItemTotalWithNoBind( i.itemID, i.collectAmount, csdefine.DELETE_ITEM_COLLECTION )
			money += i.collectAmount * i.price


		BigWorld.globalData["CollectionMgr"].onSellCollectionItems( collectionItems, collectorDBID, self.base  )


	def rollRandom( self, srcEntityID, dropBoxID, index ):
		"""
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return

		dropBox = BigWorld.entities.get( dropBoxID )
		if dropBox:
			dropBox.rollRandom( self.id, index )



	def abandonRoll( self, srcEntityID, dropBoxID, index ):
		"""
		Exposed method
		放弃ROLL
		"""
		if not self.hackVerify_( srcEntityID ) : return

		dropBox = BigWorld.entities.get( dropBoxID )
		if dropBox:
			dropBox.abandonRoll( self.id, index )



	def addOwnCollectionItem( self, srcEntityID, ownCollectionItem ):
		"""
		Exposed method
		增加自身收购物品
		"""
		if not self.hackVerify_( srcEntityID ): return

		if self.money < ownCollectionItem.getTotalPrice():
			self.statusMessage( csstatus.MONEY_NOT_ENOUGH )
			return

		if not ownCollectionItem.isValid(): return
		ownCollectionItem.uid = newUID()
		self.collectionBag.append( ownCollectionItem )

		self.client.onAddOwnCollectionItem( ownCollectionItem )


	def removeOwnCollectionItem( self, srcEntityID, uid ):
		"""
		Exposed method
		移除一个自身收购物品
		"""
		if not self.hackVerify_( srcEntityID ): return

		item = None
		for i in self.collectionBag:
			if i.uid == uid:
				self.collectionBag.remove( i )
				break

		self.client.onRemoveOwnCollectionItem( uid )



	def queryOwnCollectionItem( self, srcEntityID ):
		"""
		Exposed method
		查询自身收购物品
		"""
		player = BigWorld.entities.get( srcEntityID )
		if player:
			for i in self.collectionBag:
				player.client.onQueryOwnCollectionItem( i, self.id )


	def sellOwnCollectionItem( self, sellerID, ownCollectionItem ):
		"""
		Exposed method
		出售收购物品
		注意：这里的 sellerID 其实是 srcEntityID
		"""
		#if not self.hackVerify_( srcEntityID ): return
		if sellerID == self.id:
			self.statusMessage( csstatus.COLLECT_ITEM_FORBID_YOURSELF_ITEM )
			return
		seller = BigWorld.entities.get( sellerID, None )
		if seller is None:
			return
		# 如果在吟唱则中则返回
		if seller.attrIntonateSkill:
			self.statusMessage( TI_SHOU_SELL_FORBIDDEN_IN_INTONATING )
			return
		if seller.iskitbagsLocked():
			seller.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		collectionTime = self.queryTemp( "OwnCollectionTime", 0 )
		if collectionTime != 0 and time.time() - collectionTime  < 1.0:
			return
		seller = BigWorld.entities.get( sellerID )

		if self.money < ownCollectionItem.getTotalPrice():
			self.client.onStatusMessage( csstatus.MONEY_NOT_ENOUGH, "" )
			seller.client.onStatusMessage( csstatus.TARGET_MONEY_NOT_ENOUGH, "" )
			return
		items = []
		items.append(  g_items.createDynamicItem( ownCollectionItem.itemID , ownCollectionItem.collectAmount ) )

		checkReult = self.checkItemsPlaceIntoNK_( items )
		if checkReult != csdefine.KITBAG_CAN_HOLD :
			self.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			seller.client.onStatusMessage( csstatus.TARGET_KITBAG_IS_FULL, "" )
			return
		for i in self.collectionBag:
			if i.uid == ownCollectionItem.uid:
				if i.check( ownCollectionItem ):
					self.setTemp( "OwnCollectionTime", time.time() )
					seller.doCollectionItemTrade( self.id, ownCollectionItem )
				else:
					seller.client.onStatusMessage( csstatus.COLLECT_MSG_IS_CHANGED, "" )
					self.queryOwnCollectionItem( seller.id )
				return


	def doCollectionItemTrade( self, collectorID, ownCollectionItem ):
		"""
		define method
		"""
		collector = BigWorld.entities.get( collectorID )

		if collector:
			if self.money + ownCollectionItem.getTotalPrice() > csconst.ROLE_MONEY_UPPER_LIMIT:
				self.statusMessage( csstatus.MONEY_IS_FULL )
				return

			if self.countItemTotalWithBinded_( ownCollectionItem.itemID, False ) < ownCollectionItem.collectAmount:
				self.statusMessage( csstatus.TISHOU_FORBID_ITEM_IS_NOT_ENOUGH )
				return

			if self.removeItemTotalWithNoBind( ownCollectionItem.itemID, ownCollectionItem.collectAmount, csdefine.DELETE_ITEM_COLLECTION ):
				self.gainMoney( ownCollectionItem.getTotalPrice(), csdefine.CHANGE_MONEY_SELLCOLLECTIONITEM )

				collector.onDoCollectionItemTrade( self.id, ownCollectionItem )


	def onDoCollectionItemTrade( self, sellerID, ownCollectionItem ):
		"""
		define method
		"""
		items = []
		items.append(  g_items.createDynamicItem( ownCollectionItem.itemID , ownCollectionItem.collectAmount ) )

		for item in items:
			self.addItem( item, csdefine.ADD_ITEM_COLLECTION  )

		self.payMoney( ownCollectionItem.getTotalPrice(), csdefine.CHANGE_MONEY_BUYCOLLECTIONITEM )
		cItem = None
		for i in self.collectionBag:
			if i.uid == ownCollectionItem.uid:
				i.removeTotal( ownCollectionItem.collectAmount )
				if i.collectAmount == 0:
					self.collectionBag.remove( i )
				cItem = i
				break
		if cItem:
			self.client.removeOwnCollectionItemTotal( cItem )
			seller = BigWorld.entities.get( sellerID )
			timeStr = "%s:%s"%( time.localtime()[3], time.localtime()[4] )
			self.client.vend_addRecordNotify2( [ self.getName(), item.name(), ownCollectionItem.getTotalPrice(), timeStr, item.amount ] )
			if seller:
				seller.client.removeOwnCollectionItemTotal( cItem )

	def tong_onSetTongName( self, tongName ):
		"""
		帮会名称改变
		"""
		TongInterface.tong_onSetTongName( self, tongName )
		RoleRelation.tong_onSetTongName( self, tongName )


	def requestReward( self, spaceMailbox ):
		"""
		define method
		"""
		spaceMailbox.requestReward( self.teamMailbox.id, self.base )

	def removeTongRaceItem( self ):
		"""
		define method
		"""
		items = self.findItemsByIDFromNKCK( Const.TONG_RACE_ITEM )
		if items == []:
			return
		self.removeItem_( items[0].order, 1, csdefine.DELETE_ITEM_CREATETONGRACEHORSE  )

	def addTongScore( self, tongScore, reason = 0 ):
		"""
		define method
		增加帮会竞技积分
		"""
		if self.tongCompetitionScore + tongScore >= 65535:
			self.tongCompetitionScore = 65535
		else:
			self.tongCompetitionScore += tongScore

		try:
			g_logger.scoreTongAddLog( self.databaseID, self.getName(), tongScore, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def subTongScore( self, score, reason = 0 ):
		"""
		define method
		减少帮会竞技积分
		"""
		self.tongCompetitionScore -= score
		if self.tongCompetitionScore < 0:
			self.tongCompetitionScore = 0

		try:
			g_logger.scoreTongSubLog( self.databaseID, self.getName(), tongScore, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def addHonor( self, honor, reason ):
		"""
		define method
		增加荣誉度
		"""
		if self.honor + honor  >= 100000000:
			self.honor = 100000000
		else:
			self.honor += honor

		try:
			g_logger.scoreHonorAddLog( self.databaseID, self.getName(), honor, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def subHonor( self, honor, reason ):
		"""
		define method
		减少荣誉度
		"""
		self.honor -= honor
		if self.honor < 0:
			self.honor = 0

		try:
			g_logger.scoreHonorSubLog( self.databaseID, self.getName(), honor, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def onHonorRecover( self, controllerID, userData ):
		"""
		荣誉度
		"""
		if self.honor > 100:
			pass
		elif self.honor + Const.HONOR_RECOVER_VALUE >= 100:
			self.addHonor( 100 - self.honor, csdefine.HONOR_CHANGE_REASON_RECOVER )
		else:
			self.addHonor( Const.HONOR_RECOVER_VALUE, csdefine.HONOR_CHANGE_REASON_RECOVER )

	def addPersonalScore( self, personalScore, reason ):
		"""
		define method
		增加个人竞技积分
		"""
		if self.personalScore + personalScore  >= 65535:
			self.presonalScore = 65535
		else:
			self.personalScore += personalScore

		try:
			g_logger.scorePersonalAddLog( self.databaseID, self.getName(), personalScore, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def subPersonalScore( self, personalScore, reason ):
		"""
		define method
		减少个人竞技积分
		"""
		self.personalScore -= personalScore
		if self.personalScore < 0:
			self.personalScore = 0

		try:
			g_logger.scorePersonalSubLog( self.databaseID, self.getName(), personalScore, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def addTeamCompetitionScore( self, score, reason ):
		"""
		define method
		增加组队竞技积分积分
		"""
		if self.teamCompetitionPoint + score  >= 65535:
			self.teamCompetitionPoint = 65535
		else:
			self.teamCompetitionPoint += score

		try:
			g_logger.scorePersonalAddLog( self.databaseID, self.getName(), score, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def subTeamCompetitionScore( self, score, reason ):
		"""
		define method
		减少组队竞技积分积分
		"""
		self.teamCompetitionPoint -= score
		if self.teamCompetitionPoint < 0:
			self.teamCompetitionPoint = 0

		try:
			g_logger.scorePersonalSubLog( self.databaseID, self.getName(), score, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onExp2PotFC( self, srcEntityID, potVal ):
		"""
		用经验兑换潜能
		"""
		expVal = potVal * csconst.ROLE_EXP2POT_MULTIPLE
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return
		if potVal <= 0: # 虽然界面有限制，但服务器还是应该判一下
			return
		if expVal > self.EXP:
			self.statusMessage( csstatus.POTENTIAL_NOT_ENOUGH_EXP_TO_CHANGE )
			return
		if self.potential + potVal > csconst.ROLE_POTENTIAL_UPPER:
			self.statusMessage( csstatus.POTENTIAL_WILL_RUN_OVER )
			return
		self.addExp( -expVal, csdefine.CHANGE_EXP_AND_POTENTIAL )
		self.addPotential( potVal )


	def updateOwnCollectionItemInfo( self, srcEntityID, ownCollectionItem ):
		"""
		exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return
		for i in self.collectionBag:
			if i.uid == ownCollectionItem.uid:
				i.price = ownCollectionItem.price
				i.collectAmount = ownCollectionItem.collectAmount
				self.client.onUpdateOwnCollectionItem( i )
				return


	def updateCollectionItemInfo( self, srcEntityID, collectionItem ):
		"""
		exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return
		if self.iskitbagsLocked():
			return

		collectionItem.collectorDBID = self.databaseID
		BigWorld.globalData["CollectionMgr"].updateCollectionItem( collectionItem, self.base )


	def onUpdateCollectionItem( self, oldCollectionItem, newCollectionItem ):
		"""
		define method
		"""
		count = oldCollectionItem.collectAmount - oldCollectionItem.collectedAmount				#更新物品信息，只更新价格，数量要以服务器做参考

		newTotalPrice = count * newCollectionItem.price
		oldTotalPrice = count * oldCollectionItem.price


		money = oldTotalPrice - newTotalPrice

		print money

		if money > 0:
			self.gainMoney( money, csdefine.CHANGE_MONEY_UPDATE_COLLECTION_ITEM_INFO )
		else:
			if self.money < -money:
				self.statusMessage( csstatus.MONEY_NOT_ENOUGH )
				return
			self.payMoney( -money, csdefine.CHANGE_MONEY_UPDATE_COLLECTION_ITEM_INFO )


		oldCollectionItem.price  = newCollectionItem.price

		BigWorld.globalData["CollectionMgr"].onUpdateCollectionItem( oldCollectionItem, self.base )

	def takeCollectionDeposit( self, srcEntityID ):
		"""
		exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return
		BigWorld.globalData["CollectionMgr"].takeCollectionDeposit( self.databaseID, self.base )

	def onTakeCollectionDeposit( self, totalPrice ):
		"""
		define method
		"""
		self.gainMoney( totalPrice, csdefine.CHANGE_MONEY_CANCELCOLLECTIONITEM )
		BigWorld.globalData["CollectionMgr"].onTakeCollectionDeposit( self.databaseID )
		if totalPrice != 0:
			g = totalPrice / 10000
			s = ( totalPrice - g * 10000 ) / 100
			t = totalPrice%100

			gStr = ""
			sStr = ""
			tStr = ""

			if g != 0:
				gStr = StatusMsgs.getStatusInfo( csstatus.STRING_GOLD, g ).msg
			if s != 0:
				sStr = StatusMsgs.getStatusInfo( csstatus.STRING_SILVER, s ).msg
			if t != 0:
				tStr = StatusMsgs.getStatusInfo( csstatus.STRING_COIN, t ).msg
			str = gStr+sStr+tStr
			self.statusMessage( csstatus.TAKE_COLLECTION_DEPOSIT_SUCCESS, str )
		else:
			self.statusMessage( csstatus.COLLECTION_DEPOSIT_IS_NONE )

	def onNoticeCollectionOver( self ):
		"""
		define method
		通知领取收购押金。
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_TISHOU ):
			return

		self.statusMessage( csstatus.TAKE_COLLECTION_DEPOSIT_PLEASE )

	def hasInitActivityFlag( self ):
		"""
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_ROLE_RECORD_INIT_OVER )

	def remoteAddActivityCount( self, spaceID, activityType, spaceKey ):
		"""
		define method
		用于管理玩家对于某个副本的进入次数 by 姜毅
		"""
		if self.query( spaceKey, 0 ) == spaceID:
			return
		self.set( spaceKey, spaceID )
		g_activityRecordMgr.add( self, activityType )

	def addActivityCount( self, activityType ):
		"""
		添加记录
		"""
		g_activityRecordMgr.add( self, activityType )

	def removeActivityRecord( self, activityType ):
		"""
		移除活动记录
		"""
		g_activityRecordMgr.remove( self, activityType )

	def isActivityCanNotJoin( self, activityType ):
		"""
		检查活动参与状态（主要是可以参与 和 不可参与 两种状态）
		"""
		return g_activityRecordMgr.queryActivityJoinState( self, activityType ) == csdefine.ACTIVITY_CAN_NOT_JOIN


	def onAbandonDartQuestCBID( self, controllerID, userData ):
		"""
		回调的方式放弃运镖任务
		"""
		questID = self.queryTemp("abandonDartQuestID",0)
		if questID == 0:
			return
		self.getQuest( questID ).abandoned( self, csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE )
		self.questRemove( questID, True )
		self.onQuestBoxStateUpdate()

	def brocastMessageDart( self, questID ):
		"""
		define method
		用于运镖广播的特殊信息接口 by 姜毅
		"""
		playerDartID = self.questsTable[questID].query( "factionID" )
		playerDartName = Const.DARKOFFICE_NAME[playerDartID]
		targetDartName = Const.DARKOFFICE_NAME[75 - playerDartID]
		msg = g_cueItem.getDartCueMsg( specialMsgMap["BCT_DARTSUCCESS_NOTIFY"] )
		msg = g_cueItem.getCueMsgString( _keyMsg = msg, _p = self.getName(), _b = playerDartName, _o = targetDartName )
		self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, [] )

	def brocastMessageSlaveDart( self, factionID ):
		"""
		define method
		用于运镖广播成功的特殊信息接口 by 姜毅
		与上面的接口在factionID的获取方式上有所不同，所以需要区别
		"""
		killerDartName = Const.DARKOFFICE_NAME[75 - factionID]
		targetDartName = Const.DARKOFFICE_NAME[factionID]
		msg = g_cueItem.getDartCueMsg( specialMsgMap["BCT_ROBSUCCESS_NOTIFY"] )
		msg = g_cueItem.getCueMsgString( _keyMsg = msg, _p = self.getName(), _b = killerDartName, _o = targetDartName )
		self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, [] )


	#------------------ItemAwards 领取物品奖励
	def awardItem( self, itemList ):
		"""
		@define method
		领取物品
		"""
		itemInstances = []
		for id,amount in itemList:
			item = g_items.createDynamicItem( int( id ))
			iAmount = int(amount)
			stackable = item.getStackable()
			if iAmount > 0 and iAmount <= stackable:		# 如果设置的数量小于该物品可叠加数量
				item.setAmount( iAmount )		# 那么增加数量
				itemInstances.append( item )
			elif iAmount > stackable:
				itemInstances.extend( [ g_items.createDynamicItem( item.id, stackable ) for a in xrange(0, iAmount/stackable)] )
				m_amount = iAmount%stackable
				if m_amount > 0:
					itemInstances.append(  g_items.createDynamicItem( item.id, m_amount ) )
		# 先判断能否加入背包
		checkReult = self.checkItemsPlaceIntoNK_( itemInstances )
		if checkReult != csdefine.KITBAG_CAN_HOLD :
			self.base.awardResult( False )
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return
		for item in itemInstances:
			self.addItem( item, csdefine.ADD_ITEM_TAKEPRESENT )

		self.base.awardResult( True )


	def onMessyRecall( self, messyID ):
		"""
		用于处理一些杂乱行为的结束回调
		"""
		BigWorld.globalData["MessyMgr"].onMessyOver( messyID, self.databaseID )


	def onRoleRecordInitFinish( self ):
		"""
		角色信息（roleRecord）初始化完毕的调用。
		这个调用后，会帮角色设置一个标志位 csdefine.ACTIVITY_FLAGS_INIT_OVER
		如果这个标志位没有被设置，则相关功能将被暂停使用。
		"""
		self.addFlag( csdefine.ROLE_FLAG_ROLE_RECORD_INIT_OVER )
		g_activityRecordMgr.initAllActivitysJoinState( self )


	def onAccountRecordInitFinish( self ):
		"""
		角色信息（roleRecord）初始化完毕的调用。
		这个调用后，会帮角色设置一个标志位 csdefine.ACTIVITY_FLAGS_INIT_OVER
		如果这个标志位没有被设置，则相关功能将被暂停使用。
		"""
		self.setActivityFlag( csdefine.ROLE_FLAG_ACCOUNT_RECORD_INIT_OVER )

	def sendLoveMsg( self, receiverName, msg, isAnonymity, isSendMail ):
		"""
		define method
		非诚勿扰，发送告白信息
		"""
		needMoney = 0
		if isAnonymity:
			needMoney = csconst.ANONYMITY_LOVE_MSG_PAY
		else:
			needMoney = csconst.LOVE_MSG_PAY

		if self.isActivityCanNotJoin( csdefine.ACTIVITY_FEI_CHENG_WU_YAO ):
			self.statusMessage( csstatus.FCWR_HAS_SENDED_LOVEMSG_TODAY )
			return

		if not self.payMoney( needMoney, csdefine.CHANGE_MONEY_FCWR_FOR_MSG ):
			self.statusMessage( csstatus.FCWR_NOT_ENOUGH_MONEY_FOR_MSG )
			return
		self.addActivityCount( csdefine.ACTIVITY_FEI_CHENG_WU_YAO )

		msgInstance = LoveMsg()
		msgInstance.init( 0, self.databaseID, int(time.time()), self.playerName, receiverName, msg, isAnonymity )

		BigWorld.globalData["FeichengwuraoMgr"].addLoveMsg( msgInstance )
		if isSendMail:
			if isAnonymity:
				senderName = cschannel_msgs.FCWR_MAIL_SENDER_ANONYMITY
			else:
				senderName = self.getName()
			BigWorld.globalData["MailMgr"].send( None, receiverName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_PLAYER, senderName, cschannel_msgs.FCWR_MAIL_TITLE, msg, 0, [] )

		self.statusMessage( csstatus.FCWR_SEND_LOVEMSG_SUCCESSFUL )
		self.client.onSendLoveMsgSucc()

	# ----------------------------------------------------------------
	# 魅力果树
	# ----------------------------------------------------------------
	def pickFruit( self, srcEntityID, targetID ):
		"""
		Exposed Method
		采集魅力果实
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		target = BigWorld.entities.get( targetID )
		if target is None: return
		if target.isDestroyed: return
		# 判定类型
		if not target.isEntityType( csdefine.ENTITY_TYPE_FRUITTREE ): return
		# 判断距离
		distance = self.position.distTo( target.position )
		if distance > csconst.FRUIT_PICK_DISTANCE: return
		# 判定是否成熟
		if not target.isRipe:
			self.statusMessage( csstatus.FRUIT_NOT_RIPE )
			return
		# 判定是否是自己种植
		if self.getName() != target.planterName:
			self.statusMessage( csstatus.FRUIT_NOT_YOU )
			return
		# 判定玩家状态
		if self.state == csdefine.ENTITY_STATE_FIGHT:
			self.statusMessage( csstatus.FRUIT_NOT_PICK )
			return
		# 判定是否被采集
		if target.pickerDBID !=0:
			self.statusMessage( csstatus.FRUIT_IS_PICK )
			return

		# 采集品
		itemID = 0
		r = random.random()
		data = FruitItemsDatas.get( target.fruitseedID )
		datas = data.get( "data" )
		if datas is None: return
		for key, odds in datas:
			if r <= odds:
				itemID = key
				break
		if itemID == 0: return
		item = g_items.createDynamicItem( int( itemID ))
		if item is None: return

		# 先判断能否加入背包
		checkReult = self.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD:
			self.statusMessage( csstatus.FRUIT_CANT_HOLD )
			return

		self.addItem( item, reason = csdefine.ADD_ITEM_FRUIT_TREE )

		target.onPick( self.databaseID )


	# ----------------------------------------------------------------
	# 装备属性抽取
	# ----------------------------------------------------------------
	def equipExtract( self, srcEntityID, uids ):
		"""
		Exposed Method
		装备抽取功能
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		if self.iskitbagsLocked():
			#提示 背包已经锁定
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return
		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#获得神机匣的使用次数
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return

		itemList = [ self.getItemByUid_( uid ) for uid in uids ]
		if len( itemList ) == 0:
			# 请放入抽取属性的装备
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_EQUIP )
			return

		equips = []					# 记录要抽取的装备
		needItems = []				# 记录封灵石
		needSuperItems = []			# 记录超级封灵石
		excItems = []				# 记录神征令

		for item in itemList:
			if item.isFrozen():
				# 物品被锁定 无法抽取
				self.statusMessage( csstatus.EQUIP_EXTRACT_ISFROZEN )
				return

			if item.isEquip():
				equips.append( item )
			elif item.id == csconst.EQUIP_EXTRACT_NEEDITEMS:
				needItems.append( item )
			elif item.id == csconst.EQUIP_EXTRACT_SUNEEDITEMS:
				needSuperItems.append( item )
			elif item.id == csconst.EQUIP_EXTRACT_EXCITEM:
				excItems.append( item )

		# 请放入要抽取的装备
		if len( equips ) == 0:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_EQUIP )
			return

		# 只能放入一件装备
		if len( equips ) > 1:
			self.statusMessage( csstatus.EQUIP_EXTRACT_ONE_EQUIP )
			return

		equip = equips[0]
		# 只能放入10级以上的装备
		level = equip.getLevel()
		if level < csconst.EQUIP_EXTRACT_LEVEL_MIN:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_LEVEL )
			return

		# 只能放入蓝色以上品质的装备
		quality = equip.getQuality()
		if quality not in csconst.EQUIP_EXTRACT_QUALITYS:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_QUALITY )
			return

		# 装备没有属性能被抽取 加入灌注属性的抽取 by wuxo csol-1055
		extractEffect = [] #可以抽取的属性列表
		poureEffect = equip.getPouredCreateEffect()
		disCount = len( equip.getCreateEffect() ) - len( poureEffect )
		eqExtraEffect = dict( equip.getExtraEffect() )
		extractEffect = copy.deepcopy( poureEffect )
		for attrE,attrV in eqExtraEffect.iteritems():
			extractEffect.append( (attrE, attrV ) )
		if len( extractEffect ) == 0:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NO_EFFECT )
			return

		# 判定用的是封灵石还是超级封灵石
		if len( needItems ):
			if len( needSuperItems ):
				# 2种封灵石不能同时使用
				self.statusMessage( csstatus.EQUIP_EXTRACT_NO_USE )
				return

			# 金钱 = 装备等级^2*装备品质*2^石头品质*2*放入的石头数量
			equipLevel = equip.getLevel()
			equipQuality = equip.getQuality()
			itemQuality = needItems[0].getQuality()
			itemAmount = len( needItems ) if len( needItems ) <= len( extractEffect ) else len( extractEffect )
			money = ( equipLevel ** 2 ) * equipQuality * ( 2 ** itemQuality ) * 2 * itemAmount
			if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIP_EXTRACT ):
				self.statusMessage( csstatus.EQUIP_EXTRACT_NO_MONEY )
				return

			# 使用封灵石
			odds = csconst.EQUIP_EXTRACT_ITEM_ODDS
			# 判定是否有神征令
			if len( excItems ) != 0:
				odds += csconst.EQUIP_EXTRACT_EXCITEM_ODDS
			if random.random() > odds:
				# 装备抽取失败
				self.statusMessage( csstatus.EQUIP_EXTRACT_FIALD )
				# 根据装备可抽取属性数量移除封灵石，留下多余的
				if len( extractEffect ) >= len( needItems ):
					for item in needItems:
						self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				else:
					for i in xrange( len( extractEffect ) ):
						item = needItems[ i ]
						self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				return

			for item in needItems:
				if len( extractEffect ) == 0: break
				key,value = random.choice( extractEffect )
				extractEffect.remove( ( key,value) )
				if eqExtraEffect.has_key(key) and eqExtraEffect[key] == value:
					del eqExtraEffect[ key ]
				else:
					poureEffect.remove(( key,value) )
				newItem = self.createDynamicItem( csconst.EQUIP_EXTRACT_PROITEM )
				if newItem is None: return
				newItem.addBjExtraEffect( [( key, value )] )
				newItem.set( "bj_slotLocation", [ equip.getType()] )
				newItem.setLevel( equip.getLevel() )
				#newItem.setBindType( ItemTypeEnum.CBT_NONE )

				self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				self.addItemAndNotify_( newItem, reason = csdefine.ADD_ITEM_EQUIP_EXTRACT )

			self.removeItemByUid_( equip.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
			for item in excItems:
				self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )

		else:
			if len( needSuperItems ) == 0:
				# 请放入封灵石或者超级封灵石
				self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_ITEM )
				return

			# 金钱 = 装备等级^2*装备品质*2^石头品质*2*放入的石头数量
			equipLevel = equip.getLevel()
			equipQuality = equip.getQuality()
			itemQuality = needSuperItems[0].getQuality()
			itemAmount = len( needSuperItems ) if len( needSuperItems ) <= len( extractEffect ) else len( extractEffect )
			money = ( equipLevel ** 2 ) * equipQuality * ( 2 ** itemQuality ) * 2 * itemAmount
			if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIP_EXTRACT ):
				self.statusMessage( csstatus.EQUIP_EXTRACT_NO_MONEY )
				return

			# 使用超级封灵石
			odds = csconst.EQUIP_EXTRACT_SUITEMS_ODDs
			# 判定是否有神征令
			if len( excItems ) != 0:
				odds += csconst.EQUIP_EXTRACT_EXCITEM_ODDS
			if random.random() > odds:
				# 装备抽取失败
				self.statusMessage( csstatus.EQUIP_EXTRACT_FIALD )
				# 根据装备可抽取属性数量移除超级封灵石，留下多余的
				if len( extractEffect ) >= len( needSuperItems ):
					for item in needSuperItems:
						self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				else:
					for i in xrange( len( extractEffect ) ):
						item = needSuperItems[ i ]
						self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				return

			extraCount = 0 #抽取附加属性的数量
			poureCount = 0 #抽取灌注属性的数量
			for item in needSuperItems:
				if len( extractEffect ) == 0: break
				key,value = random.choice( extractEffect )
				extractEffect.remove( ( key,value) )
				if eqExtraEffect.has_key(key) and eqExtraEffect[key] == value:
					del eqExtraEffect[ key ]
					extraCount += 1
				else:
					poureEffect.remove(( key,value) )
					poureCount += 1
				newItem = self.createDynamicItem( csconst.EQUIP_EXTRACT_PROITEM )
				if newItem is None: return
				newItem.addBjExtraEffect( [( key, value )] )
				newItem.set( "bj_slotLocation", [ equip.getType()] )
				newItem.setLevel( equip.getLevel() )
				#newItem.setBindType( ItemTypeEnum.CBT_NONE )
				self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				self.addItemAndNotify_( newItem, reason = csdefine.ADD_ITEM_EQUIP_EXTRACT )


			# 考虑这种情况：假定eqExtraEffect全部被抽取，但是装备上仍然有灌注属性存在，因此装备不消失，
			# 但是此时的物品信息就不会更新到客户端，造成数据不一致
			# 解决方法是：把这句从第一个if里面拿出来
			# updated by mushuang
			newEquip = equip.copy()
			self.removeItemByUid_( equip.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
			newEquip.set( "eq_extraEffect", eqExtraEffect, self )
			if len( eqExtraEffect )!= 0 or len( poureEffect ) != 0:
				createEffect = [ ( 0, 0 ) ]*( extraCount + disCount)
				createEffect.extend( poureEffect )
				newEquip.setCreateEffect( createEffect, self )
				# 彻底删除各种前缀，简单的隐藏总会有各种各样的问题，
				# 装备系统变化很快，一个隐藏策略用不了多久就有可能
				# 和新功能发生冲突，然后又要重新隐藏。既然装备已经
				# 不符合原有规则，要前缀也没有用！
				newEquip.removeAllPrefix( self )
				# 为了通知装备抽取引导任务
				self.addItemByOrderAndNotify_( newEquip, self.getNormalKitbagFreeOrder(), csdefine.DELETE_ITEM_EQUIP_EXTRACT )

			for item in excItems:
				self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
		#神机匣次数减1
		useDegree -= 1
		kitCasketItem.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )

		self.statusMessage( csstatus.EQUIP_EXTRACT_SUCCESS )


	# ----------------------------------------------------------------
	# 装备属性灌注
	# ----------------------------------------------------------------
	def equipPour( self, srcEntityID, uids ):
		"""
		Exposed Method
		装备属性灌注功能
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		if self.iskitbagsLocked():
			#提示 背包已经锁定
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#获得神机匣的使用次数
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return

		itemList = [ self.getItemByUid_( uid ) for uid in uids ]
		if len( itemList ) == 0:
			# 请放入要灌注属性的装备
			self.statusMessage( csstatus.EQUIP_POUR_NEED_EQUIP )
			return

		equips = []					# 记录要抽取的装备
		needItems = []				# 记录韵灵琥珀

		for item in itemList:
			if item.isFrozen():
				# 物品被锁定 无法抽取
				self.statusMessage( csstatus.EQUIP_POUR_ISFROZEN )
				return
			if item.isEquip():
				equips.append( item )
			elif item.id == csconst.EQUIP_EXTRACT_PROITEM:
				needItems.append( item )

		# 请放入要灌注属性的装备
		if len( equips ) == 0:
			self.statusMessage( csstatus.EQUIP_POUR_NEED_EQUIP )
			return

		# 只能放入一件装备
		if len( equips ) > 1:
			self.statusMessage( csstatus.EQUIP_POUR_ONE_EQUIP )
			return

		# 请放入韵灵琥珀
		if len( needItems ) == 0:
			self.statusMessage( csstatus.EQUIP_POUR_NO_USEITEM )
			return

		# 一次只能放入一个韵灵琥珀
		if len( needItems ) > 1:
			self.statusMessage( csstatus.EQUIP_POUR_ONE_USEITEM )
			return

		equip = equips[0]
		# 只能放入10级以上的装备
		equipLevel = equip.getLevel()
		if equipLevel < csconst.EQUIP_EXTRACT_LEVEL_MIN:
			self.statusMessage( csstatus.EQUIP_POUR_NEED_LEVEL )
			return

		# 只能放入蓝色以上品质的装备
		quality = equip.getQuality()
		if quality not in csconst.EQUIP_EXTRACT_QUALITYS:
			self.statusMessage( csstatus.EQUIP_POUR_NEED_QUALITY )
			return

		# 装备属性空位不足
		emptyIndex = -1
		createEffect = equip.getCreateEffect()
		for index, data in enumerate( createEffect ):
			if data[0] != 0: continue
			emptyIndex = index
		if emptyIndex == -1:
			self.statusMessage( csstatus.EQUIP_POUR_NO_EFFECT )
			return

		needItem = needItems[0]
		# 无属性的韵灵琥珀
		bjEffect = needItem.getBjExtraEffect()
		if len( bjEffect ) == 0:
			self.statusMessage( csstatus.EQUIP_POUR_NO_USE )
			return

		# 韵灵琥珀的等级与装备等级不符
		level = needItem.getLevel()
		if level > equipLevel:
			self.statusMessage( csstatus.EQUIP_POUR_USE_LEVEL )
			return

		# 有相同属性(包括附加属性，已灌注属性，和套装属性)不能灌注
		#一件装备上相同的附加属性不能超过2条。 by csol-1055
		effect = bjEffect[0]
		effectkey = effect[0]
		count = 0
		for key, value in createEffect:
			if key == effectkey:
				count += 1
		for key in equip.getExtraEffect().keys():
			if  key == effectkey:
				count += 1
		if count >= csconst.EQUIP_POURE_ATTR_SAME_COUNT:
			self.statusMessage( csstatus.EQUIP_POUR_SAME_EFFECT )
			return


		# 该属性只能灌注到相应的装备部位
		wieldType = needItem.query( "bj_slotLocation", [] )
		equipType = equip.getType()
		if equipType not in wieldType:
			self.statusMessage( csstatus.EQUIP_POUR_ON_WIELDTYPE )
			return

		# 金钱=装备等级^2*装备品质^2* 10
		money = equipLevel ** 2 * quality ** 2 * 10
		if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIP_POUR ):
			self.statusMessage( csstatus.EQUIP_POUR_NO_MONEY )
			return

		newEquip = equip.copy()
		self.removeItemByUid_( equip.uid, reason = csdefine.DELETE_ITEM_EQUIP_POUR )
		if needItem.isBinded(): newEquip.setBindType( ItemTypeEnum.CBT_HAND, self )

		createEffect[emptyIndex] = effect
		newEquip.setCreateEffect( createEffect, self )


		# 彻底删除各种前缀，简单的隐藏总会有各种各样的问题，
		# 装备系统变化很快，一个隐藏策略用不了多久就有可能
		# 和新功能发生冲突，然后又要重新隐藏。既然装备已经
		# 不符合原有规则，要前缀也没有用！
		newEquip.removeAllPrefix( self )

		# 为了通知装备灌注引导任务
		self.addItemByOrderAndNotify_( newEquip, self.getNormalKitbagFreeOrder(), csdefine.DELETE_ITEM_EQUIP_POUR )
		self.removeItemByUid_( needItem.uid, reason = csdefine.DELETE_ITEM_EQUIP_POUR )
		#神机匣次数减1
		useDegree -= 1
		kitCasketItem.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )

		self.statusMessage( csstatus.EQUIP_POUR_SUCCESS )

	# ----------------------------------------------------------------
	# 装备飞升 by mushuang
	# ----------------------------------------------------------------
	def EquipUp( self, srcEntityId, equipUid, jadeUid ):
		"""
		装备飞升cell代码，exposed
		@equipId(int):飞升装备的uid
		@jadeId(int):飞升灵玉的uid
		"""
		if not self.hackVerify_( srcEntityId ) : return

		equip = self.getItemByUid_( equipUid )
		if equip is None :
			# 通知客户端，玩家没有该物品
			self.statusMessage( csstatus.KIT_EQUIP_INVALID )
			return

		jade = self.getItemByUid_( jadeUid )
		if jade is None:
			# 通知客户端，玩家没有该物品
			self.statusMessage( csstatus.KIT_EQUIP_INVALID )
			return

		# if 背包锁定：
		if self.iskitbagsLocked():
			#提示 背包已经锁定
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		# if 物品已经冻结：
		if equip.isFrozen():
			# 提示 物品已经冻结
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			# return
			return

		equiplevel = equip.getLevel()
		# 低于指定级装备不可以升品
		if equiplevel < csconst.EQUIP_UP_BASE_LEVEL:
			self.statusMessage( csstatus.KIT_EQUIP_UP_LEVEL_TOO_LOW )
			return

		quality = equip.getQuality()
		# 非粉色装备不可以升品
		if quality != ItemTypeEnum.CQT_PINK:
			self.statusMessage( csstatus.KIT_EQUIP_UP_QUALITY_TOO_LOW )
			return

		needItemID = jadeData.get( equiplevel )

		if jade.id != needItemID:
			# 通知玩家，飞升灵玉等级不符
			self.statusMessage( csstatus.KIT_EQUIP_UP_JADE_INVALID )
			return

		#计算需要的金钱，无论飞升成功与否都不会返还金钱
		payment = equiplevel ** 2.1 * 4 ** 3.5

		if not self.payMoney( payment, csdefine.CHANGE_MONEY_EQUIP_UP ):
			# 通知玩家金钱不足
			self.statusMessage( csstatus.KIT_EQUIP_UP_LOW_FUND )
			return

		if random.random() > csconst.EQUIP_UP_RATE : # 固定飞升成功率90%
			#人品不对，飞升灵玉没收
			self.removeItemByUid_( jadeUid, reason = csdefine.DELETE_ITEM_EQUIP_UP )
			#提示玩家升品失败
			self.statusMessage( csstatus.KIT_EQUIP_UP_FAILED )
			return

		# 彻底删除各种前缀，简单的隐藏总会有各种各样的问题，
		# 装备系统变化很快，一个隐藏策略用不了多久就有可能
		# 和新功能发生冲突，然后又要重新隐藏。既然装备已经
		# 不符合原有规则，要前缀也没有用！
		equip.removeAllPrefix( self )

		# 重新设定基础属性品质比率，因为绿装的基本属性必须是绿装的设置
		rnd = random.random()
		exp = EquipQualityExp.instance()
		baseQualityRate = 0.0
		if rnd < BaseQualityRateProb[0] : # 逆天绿装
			baseQualityRate = exp.getBaseRateByQuality( ItemTypeEnum.CQT_GREEN, ItemTypeEnum.CPT_MYGOD )
		elif rnd < BaseQualityRateProb[1] : # 神话绿装
			baseQualityRate = exp.getBaseRateByQuality( ItemTypeEnum.CQT_GREEN, ItemTypeEnum.CPT_MYTHIC )
		elif rnd < BaseQualityRateProb[2] : # 传说绿装
			baseQualityRate = exp.getBaseRateByQuality( ItemTypeEnum.CQT_GREEN, ItemTypeEnum.CPT_FABULOUS )

		CItemBase.setBaseRate( equip, baseQualityRate, self )

		# 变为绿装
		CItemBase.setQuality( equip, ItemTypeEnum.CQT_GREEN, self )

		# 重新计算耐久度
		equip.CalculateHardiness( self )

		# 刷新价格
		equip.updatePrice( self )

		# 如果有附加属性，就对装备的附加属性进行属性重铸
		extraEffect = equip.query("eq_extraEffect")
		if extraEffect :
			for effectId,effectValue in extraEffect.iteritems():
				equip.attrRebuild( "eq_extraEffect", effectId, self )

		slotAmount = 1
		# 0.3%的几率产生第二个属性空位
		if random.random() < csconst.EQUIP_UP_EXTRA_SLOT_RATE:
			slotAmount = 2


		equip.addCreateEffect( [(0,0)] * slotAmount, self ) # 设置属性空位

		equip.setQualityUpper( self.getName(), self ) # 设置飞升者的名字

		equip.set( "eq_upFlag", True, self ) # 设置飞升后的标志，以便隐藏套装属性

		self.removeItemByUid_( jadeUid, amount =1, reason = csdefine.DELETE_ITEM_EQUIP_UP ) # 移除飞升灵玉
		self.statusMessage( csstatus.KIT_EQUIP_UP_SUCCESS ) # 提示玩家成功


	# ----------------------------------------------------------------
	# 装备属性重铸 by mushuang
	# ----------------------------------------------------------------
	def EquipAttrRebuild(self, srcEntityId, equipUid, attrType, effectId):
		"""
		装备属性重铸
		@equipUid 装备的uid
		@attrType 属性的类别(字符串)，如eq_extraEffect,eq_createEffect....
		@effectId 需要重铸的属性id
		"""
		if not self.hackVerify_( srcEntityId ) : return


		# 获取uid指定的装备
		equip = self.getItemByUid_( equipUid )

		#if 玩家没有这个装备 :
		if equip == None :
			#提示无效装备
			self.statusMessage( csstatus.KIT_EQUIP_INVALID )
			#return
			return

		# if 背包锁定：
		if self.iskitbagsLocked():
			#提示 背包已经锁定
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		# if 物品已经冻结：
		if equip.isFrozen():
			# 提示 物品已经冻结
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			# return
			return

		# if 此物品不是装备 :
		if not equip.isEquip() :
			#提示玩家
			self.statusMessage( csstatus.KIT_EQUIP_NOT_EQUIP )
			#return
			return

		# if 玩家正穿着这件物品 :
		if equip.isAlreadyWield() :
			#提示玩家
			self.statusMessage( csstatus.KIT_EQUIP_ALREADY_WIELD )
			#return
			return

		# if 装备等级 和 品质不符
		if not ( equip.isGreen() and equip.getLevel() >= csconst.EQUIP_ATTR_REBUILD_LEVEL ) :
			#提示玩家
			self.statusMessage( csstatus.KIT_EQUIP_NOT_GREEN_AND_REBUILDABLE )
			#return
			return


		# 获取所需宝珠id
		pearlId = pearlData[ equip.getLevel() ]

		# 查找玩家身上该宝珠
		pearl = self.findItemFromNKCK_( pearlId )

		# if 玩家没有需要的宝珠
		if pearl == None :
			#提示玩家（这里是一个包含连接的提示信息）
			pearl = g_items.createDynamicItem( pearlId )
			itemObj = ChatObjParser.dumpItem( pearl )
			self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", cschannel_msgs.EQUIP_ATTR_REBUILD_NEED ,[itemObj] )
			#return
			return

		# 进行属性重铸（某些异常情况下重铸不成功，则返回)
		if not equip.attrRebuild( attrType, effectId, self ) : return

		# 彻底删除各种前缀，简单的隐藏总会有各种各样的问题，
		# 装备系统变化很快，一个隐藏策略用不了多久就有可能
		# 和新功能发生冲突，然后又要重新隐藏。既然装备已经
		# 不符合原有规则，要前缀也没有用！
		equip.removeAllPrefix( self )

		# 扣去相关消耗
		self.removeItemByUid_( pearl.uid, 1, csdefine.DELETE_ITEM_EQUIP_ATTR_REBUILD )

		# 提示玩家
		self.statusMessage( csstatus.KIT_EQUIP_ATTR_REBUILD_SUCCESS )

		# 通知客户端成功
		self.client.equipAttrRebuildSuccess()

	def onEnterWater( self, srcEntityID, waterID ):
		"""
		Exposed method
		进入一块水，得到的效果
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if waterID in WaterBuffDatas:
			self.setTemp( "lastWaterID", waterID )
			g_skills[int(WaterBuffDatas[waterID])].receiveLinkBuff( None, self )


	def onLeaveWater( self, srcEntityID, waterID ):
		"""
		Exposed method
		离开一块水，移除的效果
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if waterID == "":
			waterID = self.queryTemp( "lastWaterID" )

		if waterID:
			self.removeBuffByID(  int(WaterBuffDatas[waterID]+"01"), [csdefine.BUFF_INTERRUPT_NONE] )
			self.removeTemp( "lastWaterID" )




	def onEnterRabbitRunRoadPoint( self, pointIndex, pointsCount, isEndPoint ):
		"""
		define method
		角色进入小兔快跑路点时触发
		"""
		points = self.queryTemp( "pointIDs", [] )
		if pointIndex == len( points ) + 1:
			points.append( pointIndex )
			self.setTemp("pointIDs", points )

		if isEndPoint:
			if self.findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is None:
				self.removeTemp( "pointIDs" )
				return
			if len( points ) >= pointsCount:
				self.removeTemp( "pointIDs" )
				item = g_items.createDynamicItem( csconst.RABBIT_RUN_ITEM_RADISH, 1 )
				checkReult = self.checkItemsPlaceIntoNK_( [item] )
				if checkReult != csdefine.KITBAG_CAN_HOLD:
					self.statusMessage( csstatus.RABBIT_RUN_CANT_GIVE_RADISH )
					return
				self.addItem( item, reason = csdefine.ADD_ITEM_RABBIT_RUN )			#加萝卜
				count = self.countItemTotal_( csconst.RABBIT_RUN_ITEM_RADISH )
				if count >= 4:														#如果萝卜数量大于等于 4， 则胜利
					self.getCurrentSpaceBase().onArriveDestination( self.playerName, self.base )


	def winInRabbitRun( self, place ):
		"""
		define method
		"""
		self.gotoForetime()
		self.set( "rabbit_run_place", place )
		g_rewardMgr.rewards( self, csdefine.REWARD_RABBIT_RUN )


	def answerBuffQuestion( self, srcEntityID, buffID, answer ):
		"""
		exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		buffs = self.findBuffsByBuffID( buffID )
		for i in buffs:
			self.attrBuffs[i]["skill"].answerQuestion( self, answer )

	def changeToWolf( self ):
		"""
		变身成狼
		"""
		g_skills[csconst.RABBIT_RUN_CATCH_RABBIT_SKILL_ID].getBuffLink(1).getBuff().receive( None, self )
		self.client.initSpaceSkills( g_objFactory.getObject("fu_ben_rabbit_run").wolfSkillIDs, csdefine.SPACE_TYPE_RABBIT_RUN )

	def changeToRabbit( self ):
		"""
		变身成兔子
		"""
		g_skills[csconst.RABBIT_RUN_CATCH_RABBIT_SKILL_ID].getBuffLink(0).getBuff().receive( None, self )
		self.client.initSpaceSkills( g_objFactory.getObject("fu_ben_rabbit_run").rabbitSkillIDs, csdefine.SPACE_TYPE_RABBIT_RUN )

	def beforePostureChange( self, newPosture ):
		"""
		姿态改变之前

		@param newPosture : 改变后的姿态
		"""
		SkillBox.beforePostureChange( self, newPosture )

	def afterPostureChange( self, oldPosture ):
		"""
		姿态改变后

		@param oldPosture : 改变前的姿态
		"""
		SkillBox.afterPostureChange( self, oldPosture )

	def onRemoveBuffProwl( self ):
		"""
		解除潜行Buff后的处理 by 陈晓鸣 2010-09-28
		"""
		self.reTriggerNearTrap()


	def addPersistentFlag( self, flag ):
		"""
		define method
		增加存储的标志位
		"""
		flag = 1 << flag
		self.persistentFlags |= flag


	def removePersistentFlag( self, flag ):
		"""
		define method
		移除存储的标志位
		"""
		flag = 1 << flag
		self.persistentFlags &= flag ^ 0x7FFFFFFF

	def hasPersistentFlag( self, flag ):
		"""
		是否拥有某个存储的标志位
		"""
		flag = 1 << flag
		return ( self.persistentFlags & flag ) == flag

	def changFashionNum( self, srcEntityID ):
		"""
		exposed method
		时装切换
		"""
		if not self.hackVerify_( srcEntityID ) : return
		# 不是自由状态、夜战凤栖副本中、吟唱中、连击技能中都不允许换装
		if self.state != csdefine.ENTITY_STATE_FREE or self.onFengQi or self.intonating() or self.inHomingSpell():
			self.statusMessage( csstatus.CIB_MSG_CANNOT_SWITCH_FASHION_NOT_FREE )
			return
		fashionItem = self.itemsBag.getByOrder( ItemTypeEnum.CEL_FASHION1 )
		if fashionItem is None:return
		fashionNum = fashionItem.model()
		if self.fashionNum > 0:
			self.fashionNum = 0
		else:
			self.fashionNum = fashionNum

	def pushPkMode( self, newPkMode ):
		"""
		defined method
		将当前Pk模式压栈，并设置为新的PK模式  by mushuang
		@newPkMode: 要设置的新Pk模式
		"""
		stack = self.queryTemp( "pushedPkMode", [] )
		stack.append( self.pkMode )
		self.setTemp( "pushedPkMode", stack )

		self.setPkMode( self.id, newPkMode )

	def popPkMode( self ):
		"""
		defined method
		将上次压栈的Pk模式出栈，并设置为当前PK模式 by mushuang
		"""
		stack = self.queryTemp( "pushedPkMode", [] )
		if len(stack) == 0:
			WARNING_MSG( "Can't find last pushed pk mode! Have you forgot to do a push before pop?" )
			return

		lastPkMode = stack.pop() # 这里stack一定是引用而不是拷贝，所以不用再setTemp

		self.setPkMode( self.id, lastPkMode )

	def onMinHeightDetected( self, srcEntityID ):
		"""
		defined method
		exposed method
		玩家跌落到最大深度后的通知 by mushuang
		"""
		if not self.hackVerify_( srcEntityID ): return

		########################################################
		# 这里不做验证，直接让角色死亡。理论上这样是不安全的， #
		# 但是，从实际情况来考虑，有可能调用此方法的只有玩家自 #
		# 己的客户端，所以此处不做验证也不会出现踢人的问题。   #
		########################################################

		# 如果玩家当前位置低于死亡深度，必须将玩家的位置修正到死亡深度以上，否则玩家在复活的时候,
		# 且如果复活点在可飞行空间，那么玩家会因为当前位置低于死亡深度而再死一次
		deathDepth = float( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_DEATH_DEPTH ) )
		if self.position.y <= deathDepth :
			self.position.y = deathDepth + 1

		self.die( 0 )
		INFO_MSG( "Player( %s ) died because reaching death depth( %s )"%( self.id, deathDepth ) )

	#-----------------------------------------------------------------------------------------------------
	# 直线运动相关,考虑运动方向碰撞与地面碰撞
	#-----------------------------------------------------------------------------------------------------
	def lineToPoint( self, dstPos, moveSpeed, faceMovement ):
		"""
		virtual method.
		运动至某点，考虑运动方向碰撞与地面碰撞,故entity最终点不一定是dstPos。
		@param dstPos			: 运动目标点
		@type dstPos			: Vector3
		@param faceMovement		: entity朝向是否和运动方向一致
		@type faceMovement		: Bool
		"""
		self.controlledBy = None
		return AmbulantObject.lineToPoint( self, dstPos, moveSpeed, faceMovement )

	def onLineToPointFinish( self, controllerID, userData, state ):
		"""
		virtual method.
		移动至某点回调
		"""
		self.controlledBy = self.base

	def switchWater( self, srcEntityID, switch ):
		"""
		Exposed Method
		玩家出入水面服务器通知其他玩家
		"""
		if not self.hackVerify_( srcEntityID ): return
		self.onWaterArea = switch
		if switch:
			# csol-2047 进入水域自动取消骑乘陆行骑宠
			if VehicleHelper.isOnLandVehicle( self ):
				self.removeBuffByBuffID( csdefine.VEHICLE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

			if not self.isAccelerate:
				# 策划要求只有在没有骑宠的情况下才触发水域加速效果
				if self.vehicleModelNum == 0:
					self.move_speed_value += Const.WATER_SPEED_ACCELERATE
					self.calcMoveSpeed()
					self.isAccelerate = True
		else:
			if self.isAccelerate:
				self.move_speed_value -= Const.WATER_SPEED_ACCELERATE
				self.calcMoveSpeed()
				self.isAccelerate = False

	def leaveCopySpace( self, srcEntityID ):
		"""
		Exposed Method
		玩家离开副本
		"""
		if not self.hackVerify_( srcEntityID ): return
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			self.gotoForetime()

	def onDelayPlayCamera(self,controllerID,userData):
		"""
		播放镜头事件 by wuxo 2011-11-26
		"""
		eventID = self.queryTemp("playCamera_eventID",0)
		if eventID :
			self.client.onCameraFly( eventID )
		self.removeTemp("playCamera_eventID")

	def onCompleteVideo(self,sourceID):
		"""
		视频播放结束 by wuxo 2011-11-26
		"""
		if not self.hackVerify_( sourceID ): return
		self.clearBuff( [csdefine.BUFF_INTERRUPT_COMPLETE_VIDEO] )

	def reTriggerNearTrap( self ):
		"""
		重新触发周围的陷阱
		"""
		es = self.entitiesInRangeExt( Const.REVIVE_ON_ORIGIN_RANGE, None, self.position )
		for e in es:
			if e.getEntityTypeName() == "AreaRestrictTransducer":
				if e.radius > 0:
					range = self.position.flatDistTo( e.position )
					if e.radius >= range:
						e.onEnterTrapExt( self, range, e.controlID )		# 角色进入陷阱

			if not hasattr( e, "triggerTrap" ):
				continue

			if e.initiativeRange > 0:
				range = self.position.flatDistTo( e.position )
				if e.initiativeRange >= range:
					e.triggerTrap( self.id, range )

	def infoTongMemberFly( self, srcEntityID, lineNumber, spaceName, position, direction ):
		"""
		Exposed method.
		通知帮会成员飞到自己身边（用于帮会运镖）
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# 不允许使用引路蜂的各种状态
		cantFlyings = [ ( csdefine.ENTITY_STATE_FIGHT, csstatus.SKILL_USE_ITEM_WHILE_FIGHTING ),# 战斗
						( csdefine.ENTITY_STATE_DEAD, csstatus.SKILL_USE_ITEM_WHILE_DEAD ),		# 死亡
						( csdefine.ENTITY_STATE_VEND, csstatus.ROLE_VEND_CANNOT_FLY ),			# 摆摊
						( csdefine.ENTITY_STATE_RACER, csstatus.ROLE_RACE_CANNOT_FLY ),			# 比赛
						( csdefine.ENTITY_STATE_QUIZ_GAME, csstatus.ROLE_QUIZ_CANNOT_FLY ),		# 知识问答
					]
		for (state, infoMessage) in cantFlyings:
			if ( state == self.getState() ):
				self.statusMessage( infoMessage )
				return

		if not self.controlledBy:	# 玩家失去控制时不允许使用
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#携带跑商物品，不能使用引路蜂
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# 如果有法术禁咒buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#在监狱中不能传送
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			return self.statusMessage( csstatus.SPACE_MISS_LEAVE_PRISON )

		if self.getCurrentSpaceType() in [ csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN, csdefine.SPACE_TYPE_TOWER_DEFENSE, csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN ]:
			return self.statusMessage( csstatus.SPACE_COPY_CANNOT_USE_ITEM_TELEPORT )

		self.gotoSpaceLineNumber( spaceName, lineNumber, Math.Vector3( position ) + ( random.randint(-2,2),0,random.randint(-2,2) ), direction )


	def setAoI( self, srcEntityID, range ):
		"""
		Exposed method.
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if range == 0.0 or range > Const.MAX_AOI_RANGE:
			range = csconst.ROLE_AOI_RADIUS
		self.setAoIRadius( range )

	def sendAICmd( self, srcEntityID, entityIDs, aicmdID ):
		"""
		Exposed method.
		"""
		if not self.hackVerify_( srcEntityID ) : return
		for entityID in entityIDs:
			try:
				entity = BigWorld.entities[ entityID ]
			except:
				return
			entity.onAICommand( self.id, "", aicmdID )
	
	#飞翔传送坐骑获取
	def onGetAllVehicleDatas( self, vehicleDatas ):
		"""
		define method
		"""
		flyVehicleNumber = []
		for vehicleDBID in vehicleDatas:
			vehicleData = vehicleDatas.get( vehicleDBID )
			if vehicleData is None: continue
			type = vehicleData["type"]
			if type == csdefine.VEHICLE_TYPE_FLY:
				itemID = vehicleData["srcItemID"]
				item = self.createDynamicItem( itemID )
				if item is None: continue
				itemModelID = item.model()
				flyVehicleNumber.append( itemModelID )
		self.setFlyVehicleNumber( flyVehicleNumber )

	def setFlyVehicleNumber( self, flyVehicleNumber ):
		"""
		设置飞翔坐骑
		"""
		flyInfo = self.popTemp( "FLY_TELEPORT_VEHICLE_INFO", None )
		isChoose = flyInfo[1]
		modelNum = flyInfo[0]
		if isChoose and len( flyVehicleNumber ) > 0:
			self.vehicleModelNum = random.choice( flyVehicleNumber )
		else:
			if len( modelNum ) > 0:
				self.vehicleModelNum = random.choice( modelNum )

	def addComboCount( self ):
		"""
		define method
		玩家攻击计数
		"""
		combo_tid = self.queryTemp( "COMBO_COUNT_TIMMERID", 0 )
		if combo_tid:
			self.cancel( combo_tid )
		count = self.queryTemp( "COMBO_COUNT", 0 )
		count += 1
		if count > Const.COMBO_COUNT_MAX :
			count = 0
		self.setTemp( "COMBO_COUNT", count )
		self.client.updateComboCount( count )
		tid = self.addTimer( Const.COMBO_COUNT_CLEAR_TIME, 0, ECBExtend.COMBO_COUNT_TIMER_CBID )
		self.setTemp( "COMBO_COUNT_TIMMERID", tid )

	def clearComboCount( self, controllerID, userData ):
		combo_tid = self.queryTemp( "COMBO_COUNT_TIMMERID", 0 )
		self.cancel( combo_tid )
		self.setTemp( "COMBO_COUNT", 0 )
		self.setTemp( "COMBO_COUNT_TIMMERID", 0 )

	def onTime_RoleRevive( self, controllerID, userData ):
		"""
		等待时间未复活则回城复活
		"""
		if self.state != csdefine.ENTITY_STATE_FREE:
			self.setTemp( "role_die_teleport", True )
			self.reviveOnCity()

	def addFlag( self, flag ):
		"""
		重新设置标志

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		"""
		GameObject.addFlag( self, flag )
		# 进入安全区，锁定PK模式
		if flag == csdefine.ROLE_FLAG_SAFE_AREA:
			self.lockPkMode()

	def removeFlag( self, flag ):
		"""
		重新设置标志
		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		# 第32位不使用，那是标志位，如果使用了则必须要用UINT32，当前用的是INT32
		# 不使用UINT32的其中一个原因是我们可能不会有这么多标志，
		# 另一个原因是如果使用UINT32，python会使用是INT64来保存这个值
		"""
		GameObject.removeFlag( self, flag )
		if flag == csdefine.ROLE_FLAG_SAFE_AREA:			 # 离开安全区，解锁PK模式
			if self.queryTemp( "copy_space_lock_pkmode",0 ): # 副本中不解锁
				return
			self.unLockPkMode()

	def beforeSpellUse( self, spell, target ):
		"""
		在使用技能之前要做的事情
		@param  skillID:	要使用的技能标识
		@type   skillID:	SKILLID
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		RoleEnmity.beforeSpellUse( self, spell, target )
		if spell.isMalignant():#玩家使用恶性技能会下陆行坐骑
			self.clearBuff( [csdefine.BUFF_INTERRUPT_LAND_VEHICLE] )

	def getSpaceCopyLevel( self ):
		"""
		获取玩家所在副本的等级（不通用，目前只用于YXLM副本Buff加成的计算）
		"""
		copyLevel = 0
		spaceBase = self.getCurrentSpaceBase()
		if spaceBase is None: return copyLevel
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if hasattr( spaceEntity, "teamLevel" ):
			copyLevel = spaceEntity.teamLevel
		return copyLevel

#----------------------------------------------------
#劲舞时刻
#----------------------------------------------------
	def setDanceChallengeIndex(self, srcEntityID, challengeIndex):
		#exposed methodName
		#challengeIndex 表示玩家挑战舞王的位置（1到19），如果为0表示练习斗舞
		self.challengeIndex = challengeIndex
		if challengeIndex:#挑战斗舞时间限制6分钟
			self._dancechellengeTimerID =self.addTimer(360, 0, ECBExtend.DANCECHELLENGETIMER)
		#self.getCurrentSpaceBase().cell.setDanceChallengeIndex(challengeIndex)

	def onTimerDanceChellengeTimeOver(self, timerID, cbid ):#6分钟时间到，挑战结束
		for entity in self.entitiesInRangeExt(35):
			if entity.__class__.__name__ == "Role":
				entity.cancelChallenge()
				DEBUG_MSG("player[%s] ,dancechellenge time is over "%self.playerName)

	def noticeChallengeResult(self, challengeResult):
		#define method
		INFO_MSG("noticeChallengeResult is %d to player[%s]"%(challengeResult, self.planterName))
		if challengeResult:#挑战成功
			self.challengeSuccess()
		else:
			self.challengeFailed()

	def setRoleModelInfo(self, srcEntityID, playerModelInfo):
		#exposed methodName
		self.playerModelInfo = playerModelInfo

	def challengeSuccess(self):
		#define method
		DEBUG_MSG("player[%s] challengeSuccess"%self.playerName)
		#BigWorld.globalData["DanceMgr"].getDanceExp(self.playerName, self.base, False, self.level)  #挑战成为舞王，立即结算普通舞厅经验
		BigWorld.globalData["DanceMgr"].setModelInfo(self.playerModelInfo, self.challengeIndex, self.base, self.databaseID)#再更改成功挑战者的模型到相应的位置
		#自己身上可以有舞王buff，先去掉，再给自己加新的buff
		if self.challengeIndex == 1:
			self.danceKingType = csdefine.DANCER_GOLDEN
		elif self.challengeIndex in [2,3,4]:
			self.danceKingType = csdefine.DANCER_SILVER
		elif self.challengeIndex in [5,6,7,8,9]:
			self.danceKingType = csdefine.DANCER_COPPER
		elif self.challengeIndex >= 10 and self.challengeIndex < 20:
			self.danceKingType = csdefine.DANCER_CANDIDATE
		self.clearDanceInfo()
		self.cancel(self._dancechellengeTimerID)

	def getDanceKingBuffRatio(self):
		#舞王经验倍率
		if self.danceKingType == csdefine.DANCER_GOLDEN:
			return 10
		elif self.danceKingType == csdefine.DANCER_SILVER:
			return 5
		elif self.danceKingType == csdefine.DANCER_COPPER:
			return 3
		elif self.danceKingType == csdefine.DANCER_CANDIDATE:
			return 2
		return 0

	def clearDanceInfo(self):
		self.playerModelInfo = None
		self.challengeIndex = 0
		if self.queryTemp("danceType"):  #清除挑战之后的Temp
			self.removeTemp("danceType")

	def challengeFailed(self):
		DEBUG_MSG("player[%s] challengeFailed"%self.playerName)
		self.danceKingType = csdefine.DANCER_NONE  #未上舞王榜
		self.spellTarget(csconst.DanceingPunishSkillID, self.id) #add challengeFailed punish Buff (5 mintues can not challenge again)
		self.clearDanceInfo()

	def teleportToDanceChallengeSpace(self,  srcEntityID, challengeIndex):
		#exposed method
		#挑战第几位舞王 0表示练习斗暂不，1到19表示挑战1到19号舞王
		self.gotoDanceChallengeSpace(challengeIndex)

	def teleportToDancePracticeSpace(self,  srcEntityID, challengeIndex = 0):
		#exposed method
		self.setTemp("danceType", False)
		self.gotoSpace( "dancepractice",(42, 1, 50), ( 0, 0, 0 ))
		INFO_MSG("player[%s] goto space dancepractice"%self.playerName)


	def gotoDanceChallengeSpace(self, challengeIndex):
		#defined method
		self.setTemp("danceType", True)
		self.base.noticeDanceMgrIsChallenged(challengeIndex)
		self.gotoSpace( "dancechellenge", (42, 1, 50), ( 0, 0, 0 ) )
		INFO_MSG("player[%s] goto space dancechellenge"%self.playerName)



	def askforDanceInfos(self, srcEntityID):
		#Expoesd method
		BigWorld.globalData["DanceMgr"].sendDanceKingInfos(self)

	def requestDancingKingInfos( self,DancingKingInfos) :
		"""
		defined method
		请求发送舞王信息到客户端

		"""
		self.setTemp( "DancingKingInfos", DancingKingInfos)
		self.setTemp( "dancing_king_infos_order", 1 )
		DEBUG_MSG("ROLE_SEND_DANCING_KING_INFOS_START DancingKingInfos = %s"%DancingKingInfos)		# 开始发送舞王信息到客户端
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_DANCING_KING_INFOS_CBID ) #每0.15秒发一次（一次5个）


	def onTimer_updateClientDancingKingInfos( self, timerID, cbid ) :
		"""
		分包发送舞王信息
		"""
		count = 19 #总共19个舞王
		infos = self.queryTemp("DancingKingInfos")

		startOrder = self.queryTempInt( "dancing_king_infos_order" )
		endOrder = min( count, startOrder + 5 )							# 每次发 5 个
		for order in xrange( startOrder, endOrder ) :					# 一次发5个舞王的信息
			self.client.addDancingKingInfo( order, infos.get(order, None) )
		if endOrder < count :											# 如果还有剩余
			self.addTempInt( "dancing_king_infos_order", 5 )			# 则索引指针下跳 5 个
		else :															# 如果没有剩余物品
			self.cancel( timerID )										# 删除更新 timer
			self.removeTemp( "dancing_king_infos_order" )				# 删除临时索引指针
			self.removeTemp(  "DancingKingInfos" )
			self.client.sendDancingKingInfosOver()   #发送信息完毕
			DEBUG_MSG("ROLE_SEND_DANCING_KING_INFOS_OVER" )		# 结束发送舞王信息到客户端

	def updateDanceKingInfos(self, DancingKingInfos):
		"""
		defined method
		更新玩家在舞厅中玩家的客户端舞王的信息
		"""
		if self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_WUTING:
			self.requestDancingKingInfos(DancingKingInfos)  #有舞王信息改变时，更新在舞厅玩家的客户端的舞王信息

	def removeDanceTypeTemp(self ,srcEntityID ):
		#Expoesd method
		if self.queryTemp("danceType"):
			self.removeTemp("danceType")

	def onEnterDanceCopy(self):
		#defined method
		if self.queryTemp("danceType"):
			self.getCurrentSpaceBase().cell.enterDanceCopy(time.time())
			self.client.enterDanceCopy(True)
			self.client.initSpaceSkills( csconst.spaceDanceSkills, csdefine.SPACE_TYPE_DANCECOPY_CHALLENGE )#初始化斗舞使用的空间技能
		else:
			self.getCurrentSpaceBase().cell.enterDanceCopy(0)
			self.client.enterDanceCopy(False)
			self.client.initSpaceSkills( csconst.spaceDanceSkills, csdefine.SPACE_TYPE_DANCECOPY_PARCTICE ) #初始化斗舞使用的空间技能

	def onLeaveDanceCopy(self):
		#defined method
		if self.queryTemp("danceType"):
			self.client.leaveDanceCopy(True)  #挑战斗舞副本
		else:
			self.client.leaveDanceCopy(False)		#练习斗舞副本

	def enterWuTing(self):
		#defined method
		self.client.enterWuTing()
		self.base.enterWuTing()
		BigWorld.globalData["DanceMgr"].enterDanceHall(self.databaseID, self.getCurrentSpaceBase(), self.playerName, self.base)
		if self.queryTemp("getDancePositionNow"):
			self.gotoSpace("fu_ben_wu_tai_001", (35,1,8), (0,0,0))
			BigWorld.globalData["DanceMgr"].getLoseDanceKingPosition(self.databaseID, self.base)
			self.popTemp("getDancePositionNow", None)


	def leaveWuTing(self):
		#define methodName
		self.client.leaveWuTing()
		self.base.leaveWuTing()

	def canGetDancePosition(self, srcEntityID, index):
		#exposed method
		BigWorld.globalData["DanceMgr"].canGetDancePosition(self.base, index, self.databaseID, self.playerName)

	def loseDancePosition(self, index):
		#define method
		self.getCurrentSpaceBase().cell.spawnDanceKing(index, None)

	def addWuTingBuff(self, srcEntityID, index, modelInfo):
		#exposed method
		#index : 玩家选择的位置序号20 - 39
		BigWorld.globalData["DanceMgr"].addDanceExpTime(self.playerName)
		self.getCurrentSpaceBase().cell.setDanceHallInfo(index, self.databaseID, modelInfo)
		self.getCurrentSpaceBase().cell.spawnDanceKing(index, modelInfo)

	def quitDance(self, srcEntityID):
		#Exposed method
		if self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_WUTING : #在舞厅中退出
			self.gotoSpace( "fengming",Math.Vector3(-171.636002 ,4.871000 ,-52.265999) ,Math.Vector3(0, 0, 0))
			self.client.leaveWuTing()
		elif self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_DANCE_CHALLENGE: #在挑战斗舞副本中退出
			BigWorld.globalData["DanceMgr"].indexIsChallenged(self.challengeIndex, False) #去掉当前位置上有人挑战的标记
			for entity in self.entitiesInRangeExt(35):
				if entity and entity.__class__.__name__ == "DanceNPC":
					entity.cancelChallenge()
			self.challengeFailed()
			self.gotoSpace( "fu_ben_wu_tai_001",Math.Vector3(29, 2, 18) ,Math.Vector3(0, 0, 0))
			self.client.enterWuTing()
		elif self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_DANCE_PRACTICE: #在练习斗舞副本中退出
			self.gotoSpace( "fu_ben_wu_tai_001",Math.Vector3(29, 2, 18) ,Math.Vector3(0, 0, 0))
			self.client.enterWuTing()
		else:
			ERROR_MSG("can't find those type space by Button exit in wuting!")

	def getDanceExp(self, exp, type):
		"""
		#define method
		#time 表示跳了多久的舞(单位是分钟) int类型， time <= 480 已经是处理过的
		#type：BOOL ，为0表示舞厅中普通经验，1为舞王经验。
		#exp = (3.5*lv^1.5 + 9) * 倍率 * time 普通1倍，候选2倍，铜牌3倍，银牌5倍，金牌10倍
		"""
		if type :
			self.addExp(exp, csdefine.CHANGE_EXP_DANCEKING)
		else:
			self.addExp(exp, csdefine.CHANGE_EXP_DANCE)




	#远程获取玩家装备信息
	def onQueryRoleEquipItems( self, queryMB ):
		"""
		define method.
		玩家远程查询角色的装备信息
		"""
		obj = {}
		obj["roleID"] = self.id
		obj[ "hairNumber" ] = self.hairNumber
		obj[ "faceNumber" ] = self.faceNumber
		obj[ "bodyFDict" ] = self.bodyFDict
		obj[ "volaFDict" ] = self.volaFDict
		obj[ "breechFDict" ] = self.breechFDict
		obj[ "feetFDict" ] = self.feetFDict
		obj[ "lefthandFDict" ] = self.lefthandFDict
		obj[ "righthandFDict" ] = self.righthandFDict
		obj[ "talismanNum" ] = self.talismanNum
		obj[ "fashionNum" ] = self.fashionNum
		obj[ "adornNum" ] = self.adornNum
		equips = self.getItems(csdefine.KB_EQUIP_ID)
		queryMB.client.onQueryRoleEquip( self.getName(), self.raceclass, self.getLevel(), self.tongName, obj, equips )

	def playSoundByQuest( self, questID, questStatus, soundEvent ):
		"""
		define method
		玩家进入陷阱范围根据任务状态播放声音
		"""
		quest = self.getQuest( questID )
		if quest and quest.query( self ) == questStatus:
			self.client.onPlayMonsterSound( 0, soundEvent )

#-------------------------------拯救猰貐副本------------------------
	def onLeaveYaYuCopy( self ):
		"""
		define method
		离开猰貐副本
		"""
		#销毁特殊道具
		for item in copy.copy( self.itemsBag.getDatas() ):
			if item.id in csconst.YA_YU_COPY_SPECAIL_ITEMS:
				self.deleteItem_( item.order, item.amount, True, csdefine.DELETE_ITEM_DESTROYITEM )

	def transConditionCheck( self ):
		"""
		检测是否可以传送
		"""
		if VehicleHelper.isFlying( self ):
			# 飞行
			self.client.onStatusMessage( csstatus.CANNOT_TRANSPORT_IN_FLY, "" )
			return False

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# 监狱
			self.client.onStatusMessage( csstatus.CANNOT_TRANSPORT_IN_PRISON, "" )
			return False

		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			# 不在普通地图
			self.client.onStatusMessage( csstatus.CANNOT_TRANSPORT_IN_SPACE_COPY, "" )
			return False

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# 死亡
			self.client.onStatusMessage( csstatus.CANNOT_FLY_WHILE_DEAD, "" )
			return False

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# 战斗
			self.client.onStatusMessage( csstatus.CANNOT_FLY_WHILE_FIGHTING, "" )
			return False

		return True

	def setPartrol( self, srcEntityID, path, model ):
		"""
		exposed method
		任务寻路摆点数据
		"""
		if srcEntityID != self.id: return
		self.patrolPath = path		#路径
		self.patrolModel = model	#模型

	def onCreatePotential( self ):
		"""
		define method
		base端创建好潜能副本的回调
		"""
		info = self.popTemp( "potential_creating", None )
		if not info: return
		selfEntity = BigWorld.entities.get( info[0] )
		if not selfEntity:
			return
		selfEntity.setTemp( "potential_createSpaceName", info[1] )

