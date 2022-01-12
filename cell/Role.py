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

from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader	# NPC�����������Ʒ���ñ�
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
�� Ϊ��������������� import ��ʱ�����ʶ�ذ������һ����( ÿ���� import ��ǰ��from import �ں� )
�� ��Ҫ import *
�� ���� AA.BB ( BB Ϊ class ) ʹ�� from AA import BB
����adviced by hyw
"""

# ------------------------------------------------------------------------------
# Section: class Role
# ------------------------------------------------------------------------------
class Role(
	GameObject,						# top layer of entity
	RoleEnmity, 					#
	ItemsBag, 						# ����( phw )
	RoleChangeBody,                             #����ϵͳ
	Team,	 						# ���( pgk )
	RoleDialogForward,				# �Ի�( phw )
	RoleQuestInterface,				# ����( kb )
	RoleChat, 						# ��Ϣ( phw )
	SpaceFace,						# �ռ����( pgk )
	PostInterface,					# �ʼ�ϵͳ( pgk )
	PetCage, 						# ����Ȧ( hyw )
	SkillBox,						# ����( phw )
	RoleCommissionSale,				# ����ϵͳ( wsf )
	Bank,							# Ǯׯ( wsf )
	RoleMail,						# �ʼ�ϵͳ (zyx)
	RoleRelation,					# ��ҹ�ϵ( wsf )
	TongInterface,					# ���ϵͳ(kebiao)
	RoleCredit,						# �����������( wsf )
	RoleGem,						# ��Ҿ���ʯϵͳ( wsf )
	RoleSpecialShop,				# ��ҵ����̳�( wsf )
	HorseRacer,						# ����(zyx)
	LotteryItem,					# ����(hd)
	AntiWallow,					# ������ϵͳ( spf )
	AmbulantObject,					# �ƶ���� ( kebiao )1
	RoleQuizGame,					# ֪ʶ�ʴ�( wsf )
	PresentChargeUnite,				# ��Ʒ�ͳ�ֵ��ȡģ��( hd )
	LivingSystem,					# ����ϵͳģ�� ( jy )
	YuanBaoTradeInterface,			# Ԫ������( jy )
	ItemBagSpecialInterface,			# ����������⹦�ܽӿڣ�jy��
	RoleEidolonHandler,				# ���С����ӿ�
	RoleMagicChangeInterface,		# ����ӿ�
	RoleChallengeSpaceInterface,	# ��ս�����Ի�����ӿ�
	RoleChallengeInterface,			# �����ӿ�
	RoleUpgradeSkillInterface,		# ��ɫ���������ӿ�
	SpaceViewerInterface,			# �����۲���ģʽ�ӿ�
	RoleStarMapInterface,			# �Ǽʵ�ͼ�ӿ�
	CopyMatcherInterface,			# �������ϵͳ�����ӿ�
	RoleCampInterface,				# ��Ӫ�ӿ�
	BaoZangCopyInterface,			# ���ظ����ӿ�
	ScrollCompose,					# �������䷽�ӿ�
	RoleShuijingSpaceInterface,		#ˮ�������ӿ�
	RoleYeZhanFengQiInterface,   # ҹս����ս��
	ZhengDaoInterface,				# ֤��ϵͳ�ӿ�
	RoleDestinyTransInterface,		# �����ֻظ����ӿ�
	Fisher,							# �������
	TDBattleInterface,				# ��ħ��ս
	RoleYiJieZhanChangInterface,		# ���ս��
	RoleJueDiFanJiInterface,		# ���ط����ӿ�
	RoleCopyInterface,				#�����ӿ�
	):

	"An Role entity."

	def __init__( self ):
		# ������ܻ�������ֱ�ӵ���self.getName()����
		INFO_MSG( "player %s(%i) init..." % ( self.playerName, self.id ) )

		# ����ģ��
		GameObject.__init__( self )
		Team.__init__( self )
		RoleChat.__init__( self )
		AmbulantObject.__init__( self ) #��ɫ����贫�͹�������Ҫ�ƶ�

		# ����ģ��2
		ItemsBag.__init__( self )		# װ��Ч��
		Bank.__init__( self )

		# ��չģ��
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

		# entity ���Ͷ���
		self.setEntityType( csdefine.ENTITY_TYPE_ROLE )
		# ���¼�������ֵ�������Ա����������漰�����Ե�ģ��֮ǰ��ʼ��
		#��ɫ�������Գ�ʼ��
		self.hit_speed_base = Const.ROLE_HIT_SPEED_BASE
		self.move_speed_base = Const.ROLE_MOVE_SPEED_RADIX
		self.topSpeedY = csconst.ROLE_TOP_SPEED_Y			#Y���ϵ��˶�������������

		# ���� calcDynamicProperties �� calcHPMax ���ж���ҵ�ǰHP��HP_Max��ֵ������HP��ֵ
		# �����ڳ�ʼ�������ݿ��ж�ȡ��HPֵ��HP_Max��ȫ��ʼ��֮ǰ�ǲ��ܵ�����������������
		hp = self.HP
		mp = self.MP
		# 1�����´���װ������װ��Ч��
		for equip in self.getItems( csdefine.KB_EQUIP_ID ):
			equip.wield( self, False )
		# 2��ʹbuff������Ч�� reload Buff ʱ����Ҫʵʱ������ҵ�����ֵ ��
		self.buffReload()
		# 3����ʼ������Ч���������ͱ������ܣ�
		self.initSkills()
		#4.��ʼ������װ��Ч��
		for daofa in self.equipedDaofa:
			daofa.wield( self )

		self.calcDynamicProperties()  # ��������ֵ

		#�����������õ�ǰ����ֵ�ͷ���ֵ
		self.setHP( hp )
		self.setMP( mp )

		# ��������������Ʒ
		self.resetLifeItems( True )

		# ���״̬��Ϊ����״̬����ظ�������״̬������سǸ���
		state = self.getState()
		if	state != csdefine.ENTITY_STATE_DEAD and \
			state != csdefine.ENTITY_STATE_PENDING and \
			state != csdefine.ENTITY_STATE_QUIZ_GAME:
			self.changeState( csdefine.ENTITY_STATE_FREE )

		# ��ʼHP\MP�ָ�
		#self.startRevert()
		# ����pk״̬
		self.resetPkState()
		self.unLockPkMode()

		# �������ǵ��ƶ���Ϊ����ǰ���Ǳ���һ�������ܹ㲥������Ϣ��
		self.volatileInfo = (BigWorld.VOLATILE_ALWAYS, BigWorld.VOLATILE_ALWAYS, None, None)
		self._lasttime =  BigWorld.time()	# ����cellǨ�Ƶ���ʱ����

		g_Statistic.initStat( self )	# ��ʼ����ɫͳ������

		self.addTimer( 0.0, Const.HONOR_RECOVER_TIME, ECBExtend.HONOR_RETURN_CBID )

		self.fallDownHeight = 0.0	# ����������߶�

		# ˮ�����Ч������
		self.isAccelerate = False

		#��������ֵ���������е����仯
		self.optionReduceRD_goodness()

		#���������������е����仯
		self.optionReduceRD_tong()

		#����ʱ����ս������λ�ã���1��19�������Ϊ0��ʾ��ϰ����
		self.challengeIndex = 0
		self.playerModelInfo = None  #����������ҵ�����ģ��

		#��Ӫ����������ߺ���Ҫ���������Ϣ
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
		������һ�� buff ʱ������(
		by hyw -- 2008.09.23
		"""
		RoleEnmity.onAddBuff( self, buff )
		Team.onAddBuff( self, buff )
		RoleQuestInterface.onAddBuff( self, buff )

	def onRemoveBuff( self, buff ) :
		"""
		ɾ��һ�� buff ʱ������
		by hyw -- 2008.09.23
		"""
		RoleEnmity.onRemoveBuff( self, buff )
		Team.onRemoveBuff( self, buff )
		RoleQuestInterface.onRemoveBuff( self, buff )

	def onUpdateBuff( self, index, buff ) :
		"""
		��ĳ�� buff ����ʱ������
		by hyw -- 2008.09.23
		"""
		RoleEnmity.onUpdateBuff( self, buff )
		Team.onUpdateBuff( self, buff )

	def onPetAddBuff( self, buff ):
		"""
		�������buff��֪ͨ����
		"""
		Team.onPetAddBuff( self, buff )

	def onPetRemoveBuff( self, buff ):
		"""
		�����Ƴ�buff��֪ͨ����
		"""
		Team.onPetRemoveBuff( self, buff )

	def onBuffMiss( self, receiver, skill ):
		"""
		buffδ����
		"""
		if receiver is None: return
		if skill is None: return
		self.statusMessage( csstatus.SKILL_BUFF_NOT_EFFECT, receiver.getName(), skill.getName() )

	def onBuffResist( self, receiver, buff ):
		"""
		buff���ֿ�
		"""
		if receiver is None: return
		if buff is None: return
		self.statusMessage( csstatus.SKILL_BUFF_IS_BE_RESIST_EFFECT, receiver.getName(), buff.getBuff().getName() )

	def onBuffResistHit( self, buff ):
		"""
		�ֿ���buffЧ��
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
		�����ʼ��(�����������е�skillID�����������ڵ�client)
		"""
		self.client.initSkillBox( self.getSkills() )
		self.client.onInitialized( csdefine.ROLE_INIT_SKILLS )

	def requestInitialize( self, srcEntityID, initType ) :
		"""
		<Exposed/>
		�����ʼ��( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : ��ʼ�����ͣ��� csdefine.py �ж���
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
		��cell���ɺ󣬿����ٴ���һЩ����.
		Ʃ��������һЩ���ݸ��ͻ���
		"""
		self.onEnterSpace_()
		RoleRelation.onCellReady( self )
		self.calBenefitTime = BigWorld.time()
		self.client.change_money( self.money, csdefine.CHANGE_MONEY_INITIAL )
		self.client.change_EXP( self.EXP, self.EXP, csdefine.CHANGE_EXP_INITIAL )
		self.title_onLogin()	# ��ʼ�ƺŵĳ�ʼ������Ϊ�ƺ���Ҫ�õ�ʦͽ�����޵�һЩ���ݣ����ʦͽ�����޳�ʼ����ϲſ�ʼ�Ա����첽���⡣
		self.client.onGetBenefitTime( self.benefitTime )	# ���߻���ʱ��Ŀͻ��˼�ʱ���� by����
		self.clientGetLivingSkill()							# ��ʼ���ͻ��˲ɼ��������� by ����
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

	def addMoney( self, number, reason ):
		"""
		@summary		:	��Ǯ
		@type	number	:	int32
		@param	number	:	Ҫ��ӵ�Ǯ
		@type	reason	:	UINT
		@param	reason	:	ʲôԭ����ӽ�Ǯ
		"""
		# ���ڻ�С��0����������ģ�������0�����������������⣬ʵ�����벻����ʲô����
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
		��Ҹ�Ǯ

		@param value: ������
		@type  value: INT32
		@return:      �������ɹ��򷵻�True�����򷵻�False��ʧ�ܵ�ԭ��������Ǯ����
		@rtype:       BOOL
		"""
		if self.money - value < 0:
			return False
		self.addMoney( - value, reason )
		return True

	def onMoneyChanged( self, value, reason ):
		"""
		��Ǯ�ı���
		@param value: ��Ǯ�ı������
		@type  value: INT32
		"""
		ItemsBag.onMoneyChanged( self, value, reason )

	def gainMoney( self, value, reason ):
		"""
		�����Ǯ

		@param value: ������
		@type  value: INT32
		@return:      ������ɹ��򷵻�True�����򷵻�False��ʧ�ܵ�ԭ��������Ǯ̫�࣬��������
		@rtype:       BOOL
		"""
		if self.money + value > csconst.ROLE_MONEY_UPPER_LIMIT:
			return False
		self.addMoney( value, reason )
		return True

	def freezeMoney( self ):
		"""
		�����Ǯ����
		@return: BOOL, true == ����ɹ���false == ����ʧ�ܣ�ʧ�ܵ�ԭ�������Ѷ�����
		"""
		return True

	def unfreezeMoney( self ):
		"""
		�ⶳ��Ǯ����
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
		# ����AoI
		self.setAoIRadius( csconst.ROLE_AOI_RADIUS )

	def addTeachCredit( self, value, reason = csdefine.CHANGE_TEACH_CREDIT_NORMAL ):
		"""
		@summary	:	���ӹ�ѫֵ
		@type value	:	int32
		@param value :	��ѫֵ
		@param reason : ��ѫֵ�ı��ԭ��
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
		���ɱ�־���

		"""
		# ����ʯ����ӳ�
		gemExp = value * ( self.gem_getComGemCount() + self.ptn_getComGemCount() ) * csconst.GEM_PET_COMMON_EXP_PERCENT
		if gemExp > 0:
			self.statusMessage( csstatus.EXP_GET_FOR_STONE, gemExp )
			value += int( gemExp )
		self.addExp( value, csdefine.CHANGE_EXP_KILLMONSTER )
		self.doAddKillMonsterExp( value )

	def addExp( self, value, reason ):
		"""
		define method.
		@summary	  : ���Ӿ���ֵ
		@type	value : int32
		@param	value : ����ֵ
		"""
		#--------- ����Ϊ������ϵͳ���ж� --------#
		if value == 0:
			return
		gameYield = self.wallow_getLucreRate()		# ��������Ϸ����
		level = self.level
		if level >= csconst.ROLE_LEVEL_UPPER_LIMIT:			# ��ҵȼ�������ʱ���ŵ�110����
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
				self.statusMessage( csstatus.ACCOUNT_STATE_LOST_EXP, int( -value ) )	# �㵽��ô�ѿ�����Ϊ�˸���ʾ by����
		#--------- ����Ϊ������ϵͳ���ж� --------#

		exp = value + self.EXP							# EXP �����
		expMax = RLevelEXP.getEXPMax( self.level )	# ��ǰ�ȼ��� exp ���ֵ
		while exp >= expMax :
			exp -= expMax								# ��ȥ��Ҫ������ exp ���ֵ
			level += 1
			expMax = RLevelEXP.getEXPMax( level )
			if expMax <= 0 :
				ERROR_MSG( "error exp max: %d" % expMax )
				break
		if level > csconst.ROLE_LEVEL_UPPER_LIMIT : # ���ȼ����������Ƶȼ�����
			level = csconst.ROLE_LEVEL_UPPER_LIMIT
			exp = RLevelEXP.getEXPMax( level )
		try:
			g_logger.expChangeLog( self.databaseID, self.getName(),self.EXP,self.level,max( 0, exp ),level,reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		self.setLevel( level )
		self.EXP = max( 0, exp )						# ����ʣ�µ�exp
		self.client.change_EXP( value, self.EXP, reason ) # ֪ͨ�ͻ���

	def addTeamCompetitionReward( self, place ):
		"""
		Define method.
		������Ӿ������齱��
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
		������Ӿ�����
		"""
		self.addFlag( csdefine.ROLE_FLAG_SPEC_COMPETETE )

	def onEnterTongCompetition( self ):
		"""
		Define method.
		�����Ὰ����
		"""
		self.client.onTongCompetitionStart()

	def onLeaveTeamCompetition( self ):
		"""
		Define method.
		�뿪��Ӿ�����
		"""
		self.removeFlag( csdefine.ROLE_FLAG_SPEC_COMPETETE )

	def setLevel( self, level ):
		"""
		@summary		:	���õȼ�
		@type	level	:	int16
		@param	level	:	�µĵȼ�
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
		����ͨ��
		"""
		# ֪ͨbase
		self.base.updateLevel( self.level )
		# ��Ѫ��ħ
		self.full()
		# �����Ƿ�����Ӧ�ȼ������񴥷�
		self.enumLevelUpQuest()
		# �����Ƿ�����Ϊ�ȼ��仯��ɵ�����
		self.questRoleLevelUp( self.level )
		# ˢ��pk״̬
		self.resetPkState()
		# ʦͽϵͳ֪ͨ
		self.teach_onLevelUp()

		# ��Ҿ���ʯϵͳ֪ͨ,wsf,16:23 2008-7-22
		self.gem_onLevelUp()
		# ���ﾭ��ʯϵͳ֪ͨ��wsf16:27 2008-7-29
		self.ptn_onLevelUp()

		# �������ϵͳ֪ͨ��by ���� 11:48 2009-11-26
		self.liv_onLevelUp( deltaLevel )
		# �������������Χ�˺�����
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
		�������������Χ�˺�����
		"""
		skl = str( self.level ).zfill( 3 )
		skillID = int( Const.ROLE_SKILL_IDS_ON_LEVEL_UP[self.getClass()] + skl )
		# ��ȡ����ID���ͷż���
		self.spellTarget( skillID, self.id )

	def wizCommand(self, srcEntityID, dstEntityID, command, args):
		"""
		exposed method.
		GM������ָ��

		@param command: STRING; ����ؼ��֣������鿴wizCommand::wizCommand()
		@param args: STRING; ��������������ɸ�ָ���Լ�����
		"""
		if not self.hackVerify_( srcEntityID ) : return
		wizCommand.wizCommand( self, dstEntityID, command, args )

	def onDestroy( self ):
		"""
		�����ٵ�ʱ����������
		ע�⣬��ʱself.isDestroyed��Ȼ��False
		"""
		RoleRelation.onDestroy( self )
		self.onRoleOff()			#֪ͨ�����������
		self.updateBenefitTime()
		# ��������������Ʒ
		self.resetLifeItems( False )
		self.onLeaveSpace_()

		#### ����ǰ��Ҫ���� ####
		# ����ʱ,����ս��״̬��ʱ��ǿ�Ƹı�״̬,��֪ͨ������ȡ������
		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			self.changeState( csdefine.ENTITY_STATE_PENDING )
		# ����ʱ,���ڽ���״̬��ʱ��ȡ������״̬
		if self.si_myState != csdefine.TRADE_SWAP_DEFAULT:
			tradeTarget = BigWorld.entities.get( self.si_targetID, None )
			if tradeTarget :
				self.si_tradeCancelFC( self.id )
				self.si_resetData()

		self.endRevert() # ����HP\MP�ָ�

		# �����ڽ���״̬ʱ��Ҫ֪ͨ
		PetCage.onDestroy( self )
		ItemsBag.onDestroy( self )
		RoleQuestInterface.onDestroy( self )
		# ��ȡ����֮ǰ������ֵ��ħ��ֵ
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

		#���ٷǷ���/½���������
		if  not VehicleHelper.getCurrVehicleID( self ): #modify by wuxo 2012-5-30
			self.currVehicleData = VehicleHelper.getDefaultVehicleData()
		#���ټ����������
		if  not VehicleHelper.getCurrAttrVehicleID( self ):
			self.currAttrVehicleData = VehicleHelper.getDefaultVehicleData_Attr()

		# �ڳ�
		dart = BigWorld.entities.get( self.queryTemp( "dart_id", 0) )
		if dart:
			dart.onRoleDestroy( self.id )

		# �д�
		self.changeQieCuoState( csdefine.QIECUO_NONE )

		self.withdrawEidolon( self.id ) # ����С����

	# Change Time
	def ChangeTime(self, source, newtime, duration):
		"""
		 Ҫ��ı�ͻ���ʱ��

		@param source: source id
		@type source: INT

		@param newtime: new environment time��������������ʽ���֣�
						   һ���� ʱ���֣��磺  01:00 ���賿1�㣩
						   ��һ���Ǹ��������磺 1.0
						   �κ�������ʽ��ʱ�䲻���׳��쳣��Ҳ����������

		@param duration: time LAST HOW LONG
		@type duration: UINT16
		"""
		# duration in mintues
		self.addTimer( duration*60, 0, ECBExtend.RESTORETIME_TIMER_CBID )
		self.planesAllClients( "ReceiveChangeTime", (newtime,) )

	# Get Time
	def GetTime(self):
		"""
		 ���ϵͳʱ��
		"""
		TimeInSecs = BigWorld.timeOfDay(self.spaceID)
		return math.fmod(TimeInSecs/3600, 24)

	# Restore Time
	def onRestoreTime( self, timerID, cbID ):
		"""
		 �ָ��ͻ��˵�ʱ��Ϊϵͳʱ��

		@param timerID: �ص����� id
		@type timerID: INT
		"""
		self.cancel( timerID )
		RestoreTime = self.GetTime()
		self.planesAllClients( "ReceiveChangeTime", (RestoreTime,) )

	def onDie( self, killerID ):
		"""
		virtual method.

		�������鴦��
		"""

		killer = BigWorld.entities.get( killerID )
		if killer is None:		# ����BUFF��˵�Ҳ���ɱ�����Ǻ�����������
			killerID = 0

		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		spaceScript.onRoleDie( self, killer )

		# ��spaceScript.isSpaceDesideDrop����������˼
		if not spaceScript.isSpaceCalcPkValue:
			# ����pkֵ
			self.calcPkValue( killer )
			# ��ʧװ���;�
			self.equipAbrasionOnDied( killer )

		if not spaceScript.isSpaceDesideDrop and self.getLevel() > csdefine.ROLE_DIE_DROP_PROTECT_LEVEL:	# 2009-07-11 SPF
			# isSpaceDesideDrop�������ǵ��䲿����spaceģ�鴦���������ﴦ��
			# ��ϸ�������spaceScript.onRoleDie�� ��Ϊ��Щ��ͼ�����Լ��Ĵ�������
			# ���羺��������Ӧ�õ����κζ�������ô����������̾ͽ���spaceScript.onRoleDie�д���
			# ���ԣ����������ͼ�����������䣬��������ͳһ����������
			# ������������SPF
			# �����Ǯ
			self.moneyDropOnDied( killer )
			# �����󣬵�����Ʒװ������
			self.dropOnDied()

		# ������ұ����ֵ���ɱ�� ������Ӧ��ʾ by����
		if killer is not None:
			killerType = killer.getEntityType()
			if killerType == csdefine.ENTITY_TYPE_ROLE:
				killerName = killer.getName()
				if self.onFengQi:
					killerName = ST.CHAT_CHANNEL_MASED
				self.statusMessage( csstatus.ROLE_BE_KILLED_BY_ROLE, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2, killerName )		# �����ɱ
				try:
					g_logger.roleBeKillLog( killer.databaseID, self.databaseID, killer.grade )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )

			elif killerType == csdefine.ENTITY_TYPE_PET:
				owner = killer.getOwner()
				earg, m_killer = owner.etype, owner.entity
				if earg != "MAILBOX" :		# һ�㲻����mailbox
					killerName = m_killer.getName()
					if self.onFengQi:
						killerName = ST.CHAT_CHANNEL_MASED
					self.statusMessage( csstatus.ROLE_BE_KILLED_BY_ROLE, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2, killerName )		# �����ɱ
					try:
						g_logger.roleBeKillLog( m_killer.databaseID, self.databaseID, m_killer.grade )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )

			else:
				self.statusMessage( csstatus.ROLE_BE_KILLED_BY_MONSTER, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2, killer.getName() )	#����ɱ
				if killer.className in csconst.TDB_MONSTERS:			# ��ħ��ս������
					BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].recordDieData( killer.getCamp(), self.base, self.getName(), self.getLevel(), self.tongName )
				try:
					g_logger.roleBeKillLog( 0, self.databaseID, 0 )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
		else :
			self.statusMessage( csstatus.ACCOUNT_STATE_DEAD, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_2 )

		self.team_notifyKilledMessage( killer )

		# ��������������Զ�ȡ������ 2009-07-01 spf
		if self.intonating():
			self.interruptSpell( csstatus.SKILL_IN_ATTACK )

		#�����������������������ɵ�Ӱ�죬��������������ʧ�ܣ� 2008-09-25 spf
		self.onDieAffectQuest( self )

		PetCage.onDie( self )
		RoleQuizGame.onDie( self )
		# �����˳��д�
		self.changeQieCuoState( csdefine.QIECUO_NONE )

		# �������÷����б�
		if len( self.pkTargetList ) > 0:
			self.resetPKTargetList()

	def afterDie( self, killerID ):
		"""
		virtual method.

		������ص���ִ��һЩ�����ڹ�����������������顣
		"""

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI:
			RoleYeZhanFengQiInterface.afterDie( self, killerID )

		RoleEnmity.afterDie( self, killerID )

	def interruptSpellFC( self, srcEntityID, reason ):
		"""
		exposed method.
		�����ж�֮ǰ��ʩ��
		"""
		if not self.hackVerify_( srcEntityID ) : return

		if self.attrIntonateSkill or self.attrHomingSpell:
			self.interruptSpell( reason )

	def onActWordChanged( self, act, disabled ):
		"""
		��������.
		"""
		# ��֪ͨ�ײ�
		RoleEnmity.onActWordChanged( self, act, disabled )

		if act == csdefine.ACTION_FORBID_MOVE:
			self.updateTopSpeed()
			self.calcMoveSpeed()

		#ItemsBag.onActWordChanged( self, act, disabled )

	def updateTopSpeed( self ):
		"""
		virtual method = 0.

		�����ƶ��ٶ�����(topSpeed)
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):return#���ڷ��д���״̬����Ӧ�ٶ�����ֵ�޸�
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
		�����ƶ��ٶ�����(topSpeed)
		"""
		self.topSpeed = topspeed

	def setMoveSpeed( self, speed ):
		"""
		����֮ǰȷ��ΪRealEntity
		"""
		RoleEnmity.setMoveSpeed( self, speed )

	def doRandomRun( self, centerPos, radius ):
		"""
		�ߵ�centerPosΪԭ�㣬radiusΪ�뾶�����������
		@param  centerPos: ԭ��
		@type   centerPos: Vector3
		@param  radius:    �뾶
		@type   radius:    FLOAT
		"""
		self.topSpeed = self.move_speed * ( 1 + csconst.ROLE_MOVE_SPEED_BIAS ) 	# ��������topSpeed
		self.client.doRandomRun( centerPos, radius )

	def onStateChanged( self, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		RoleEnmity.onStateChanged( self, old, new )
		Team.onStateChanged( self, old, new )
		self.revertCheck()	# �ָ�״̬�ĸı�
		self.flyingCheck()	# ����µ�״̬Ϊ���У���ִ��һЩ�ͷ�����صı�Ҫ����
		self.autoEnergyCheck()  #�Զ��ָ���Ծֵ���
		self.autoCombatCountCheck() #��˥�����
		if new == csdefine.ENTITY_STATE_FREE:
			self.updateTopSpeed()

	def changePosture( self, posture ):
		"""
		�ı���̬

		@param posture : Ŀ����̬
		@type posture : UINT16
		"""
		if posture == csdefine.ENTITY_POSTURE_NONE:	# ��ɫ�ķ�ֻ���л��������ÿ�
			return
		RoleEnmity.changePosture( self, posture )

	def flyingCheck( self ):
		"""
		����µ�״̬Ϊ���У���ִ��һЩ�ͷ�����صı�Ҫ����
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			return

		# if ����г�ս���� then �ջس���
		if self.pcg_getActPet():
			self.pcg_withdrawPet( self.id )

	def withdrawPet( self ):
		# define method.
		# Զ���ջس�
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
		����һ���ƺ�.

		@type title: UINT8
		@return: None
		"""
	#	self.titles.append( title )
	#	self.client.onTitleAdded( title )

	#def hasTitle( self, title ):
		"""
		�жϽ�ɫ�Ƿ�ӵ��ĳ�ֳƺ�

		@type title: UINT8
		@rtype: BOOL
		"""
	#	return title in self.titles

	def changeCooldown( self, typeID, lastTime, totalTime, endTimeVal ):
		"""
		virtual method.
		�ı�һ��cooldown������

		@type  typeID: INT16
		@type timeVal: INT32
		"""
		RoleEnmity.changeCooldown( self, typeID, lastTime, totalTime, endTimeVal )
		self.client.cooldownChanged( typeID, lastTime, totalTime )

	def calcRange( self ):
		"""
		virtual method.

		���㹥������
		"""
		if self.primaryHandEmpty():
			self.range_base = Const.ROLE_HANDEDS_FREE_RANGE
		RoleEnmity.calcRange( self )	# call to AvatarCommon.calcRange()


	def hasPotential( self, potential ):
		"""
		�Ƿ���Ǳ�ܵ�
		@type  			potential	: INT
		@param 			potential	: Ǳ�ܵ�
		@return					: TRUE�����㹻��Ǳ�ܵ㣬FALSE��Ǳ�ܵ㲻��
		"""
		if self.potential < potential:
			return False
		return True

	def payPotential( self, potential, reason = csdefine.CHANGE_POTENTIAL_INITIAL ):
		"""
		֧��Ǳ�ܵ�
		@type  			potential	: INT
		@param 			potential	: Ǳ�ܵ�
		@return					: TRUE������֧����FALSE��Ǳ�ܵ㲻��
		"""
		orgPotential = self.potential
		if self.potential < potential:
			return False
		self.potential -= potential
		if not reason == csdefine.CHANGE_POTENTIAL_TRANS:	# ��������ʾ
			self.statusMessage( csstatus.ACCOUNT_STATE_LOSE_POTENTIAL, int( potential ) )
		# Ǳ�ܸı���־
		try:
			g_logger.potentialChangeLog( self.databaseID, self.getName(), orgPotential, self.potential, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def addPotential( self, potential, reason = csdefine.CHANGE_POTENTIAL_INITIAL ):
		"""
		define method.
		����Ǳ�ܵ�
		@type  			potential	: INT
		@param 			potential	: Ǳ�ܵ�
		@return					: TRUE
		"""
		if self.potential > csconst.ROLE_POTENTIAL_UPPER:
			self.statusMessage( csstatus.ACCOUNT_CANT_GAIN_POTENTIAL )
			return False
		orgPotential = self.potential
		#--------- ����Ϊ������ϵͳ���ж� --------#
		gameYield = self.wallow_getLucreRate()
		if potential >=0:
			potential = potential * gameYield
		#--------- ����Ϊ������ϵͳ���ж� --------#

		if self.potential + potential > csconst.ROLE_POTENTIAL_UPPER:
			potential = csconst.ROLE_POTENTIAL_UPPER - self.potential
			self.statusMessage( csstatus.ACCOUNT_CANT_GAIN_POTENTIAL )
		self.potential += potential
		if reason == csdefine.CHANGE_POTENTIAL_FABAO:
			pass	# ͨ���������Ǳ�ܵ��ô˷���ʱ����ϵͳϵͳ���˴�����
		elif reason == csdefine.CHANGE_POTENTIAL_ZHAOCAI:
			tempString = str( int( potential ) ) + cschannel_msgs.QIAN_NENG_LUAN_DOU_INFO_1
			self.statusMessage( csstatus.CIB_ZHAOCAI_ADD_REWARD, tempString )
		elif reason == csdefine.CHANGE_POTENTIAL_JINBAO:
			tempString = str( int( potential ) ) + cschannel_msgs.QIAN_NENG_LUAN_DOU_INFO_1
			self.statusMessage( csstatus.CIB_JINBAO_ADD_REWARD, tempString )
		else:
			self.statusMessage( csstatus.ACCOUNT_STATE_GAIN_POTENTIAL, int( potential ) )
		# Ǳ�ܸı���־
		try:
			g_logger.potentialChangeLog( self.databaseID, self.getName(), orgPotential, self.potential, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def addPotentialBook( self, potential ):
		"""
		define method.
		����Ǳ����Ǳ�ܵ�
		@type  			potential	: INT
		@param 			potential	: Ǳ�ܵ�
		@return					: TRUE
		"""
		potentialBook = self.getItem_( ItemTypeEnum.CEL_POTENTIAL_BOOK )
		if potentialBook is None:
			return
		potentialBook.addPotential( potential, self )

	def addPotentialPickAnima( self, potential ):
		"""
		define method.
		����Ǳ����Ǳ�ܵ�
		@type  			potential	: INT
		@param 			potential	: Ǳ�ܵ�
		@return					: TRUE
		"""
		decRewardPotential = self.queryTemp( "decRewardPotential", 0.0 )
		cpotential = int( potential * ( 1 - decRewardPotential ) )
		self.addPotential( cpotential, csdefine.CHANGE_POTENTIAL_PICK_ANIMA )
		
	def addDaoheng( self, value, reason = 0 ):
		# ����������ֵ
		"""
		@summary	  : ���ӵ���ֵ
		@type	value : int32
		@param	value : ����ֵ
		@type	reason : int32
		@param	reason : ԭ��
		"""
		#--------- ����Ϊ������ϵͳ���ж� --------#
		gameYield = self.wallow_getLucreRate()		# ��������Ϸ����
		if value > 0:
			value = value * gameYield
		if  int( value ) == 0 :
			return
		self.statusMessage( csstatus.ACCOUNT_STATE_GAIN_DAOHENG, int( value ) )
		#--------- ����Ϊ������ϵͳ���ж� --------#

		CombatUnit.addDaoheng( self, value, reason )
		try:
			g_logger.daohengAddLog( self.databaseID, self.getName(), self.getDaoheng(), value, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setDaoheng( self, dxValue, reason = 0 ):
		# �����������ֵ
		"""
		@summary	  : ���ӵ���ֵ
		@type	value : int32
		@param	value : ����ֵ
		@type	reason : int32
		@param	reason : ԭ��
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
		����HP
		"""
		RoleEnmity.setHP( self, value )

		self.revertCheck()

	def setMP( self, value ):
		"""
		real entity method.
		virtual method
		����MP
		"""
		RoleEnmity.setMP( self, value )

		self.revertCheck()

	def calcPhysicsDPSBase( self ):
		"""
		��������DPS_baseֵ
		"""
		try:  # add by wuxo 2012-1-10 Ϊ�˷�ֹ��GM������ʹ�üӹ�����BUFFERʱ��������,����̫�� ���
			self.physics_dps_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcRolePhysicsDPS( self ) * csconst.FLOAT_ZIP_PERCENT )
		except:
			self.physics_dps_base = 0

	def calcHPMaxBase( self ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
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
		��������ֵ����ֵ
		"""
		v =  CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcRoleMPMaxBase( self )
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].MP_Max_value	# ÿ��MP���޼�ֵ
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
		������С�������� ����ֵ
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps_value
		physic_dps_base = v + v_value * ( self.level - 1 )  # ��������������ֵ
		self.damage_min_base = int( self.physics_dps * self.hit_speed * ( 1.0 - self.wave_dps ) + physic_dps_base )

	def calcDamageMaxBase( self ):
		"""
		��������������� ����ֵ
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].physics_dps_value
		physic_dps_base = v + v_value * ( self.level - 1 )	# ��������������ֵ
		self.damage_max_base = int( self.physics_dps * self.hit_speed * ( 1.0 + self.wave_dps ) + physic_dps_base )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		����������
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].magic_dps
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].magic_dps_value
		magic_dps_base = v + v_value * ( self.level - 1 )	# ����������������ֵ
		self.magic_damage_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcRoleMagicDamage( self ) + magic_dps_base )

	def startRevert( self ):
		"""
		����HP��MP�ָ��ٶ�
		"""
		if self.revertID:
			WARNING_MSG( "Revert addTimer Again !!!" )
			self.cancel( self.revertID )

		self.revertID = self.addTimer( Const.ROLE_MP_REVER_INTERVAL, Const.ROLE_MP_REVER_INTERVAL, ECBExtend.REVERT_HPMP_TIMER_CBID )

	def endRevert( self ):
		"""
		����HP��MP�ָ��ٶ�
		"""
		if self.revertID:
			self.cancel( self.revertID )
			self.revertID = 0

	def revertCheck( self ):
		"""
		�ָ����
		"""
		state = self.getState()
		if state != csdefine.ENTITY_STATE_FIGHT and state != csdefine.ENTITY_STATE_DEAD:
			if (self.HP_Max > self.HP or self.MP_Max > self.MP) and self.revertID == 0:
				self.startRevert()
		elif self.revertID:
			self.endRevert()

	def onRevertTimer( self, controllerID, userData ):
		"""
		ʱ�䴦���¼�
		"""
		if self.HP_Max > self.HP and self.queryTemp( "forbid_revert_hp", True ):
			self.addHP( self.HP_regen )
		if self.MP_Max > self.MP and self.queryTemp( "forbid_revert_mp", True ):
			self.addMP( self.MP_regen )
		if self.HP_Max == self.HP and self.MP_Max == self.MP:
			self.endRevert()

	# ----------------------------------------------------------------
	# �Զ��ָ���Ծֵ���
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
		������Ծ����ֵ�ָ��ٶ�
		"""
		if self.autoEnergyID:
			WARNING_MSG( "auto EnergyID addTimer Again !!!" )
			self.cancel( self.autoEnergyID )

		self.autoEnergyID = self.addTimer( csdefine.ROLE_ENERGY_REVER_INTERVAL, csdefine.ROLE_ENERGY_REVER_INTERVAL, ECBExtend.REVERT_ENERGY_TIMER_CBID )

	def endAutoEnergy( self ):
		"""
		������Ծ����ֵ�ָ��ٶ�
		"""
		self.cancel( self.autoEnergyID )
		self.autoEnergyID = 0

	def onAutoEnergyTimer( self, controllerID, userData ):
		"""
		ʱ�䴥���¼�
		"""
		if self.energy < csdefine.JUMP_ENERGY_MAX:
			self.calEnergy( csdefine.ROLE_ENERGY_REVER_VALUE )
		if self.energy == csdefine.JUMP_ENERGY_MAX :
			self.endAutoEnergy()

	def calEnergy( self, value ):
		"""
		real entity method.
		����Energy
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
	# �񶷵������
	# ----------------------------------------------------------------
	def autoCombatCountCheck( self ):
		"""
		����Ƿ���timmer
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
		��ֵ����/����
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
		����ս���񶷵����Զ�˥��
		"""
		if self.autoCombatCountID:
			WARNING_MSG( "auto CombatCount addTimer Again !!!" )
			self.cancel( self.autoCombatCountID )
		if self.combatCount > 0:
			self.autoCombatCountID = self.addTimer( csdefine.ROLE_CombatCount_TIMMER, csdefine.ROLE_CombatCount_TIMMER, ECBExtend.CombatCount_TIMER_CBID )

	def onAutoCombatCountTimer( self, controllerID, userData ):
		"""
		timmer�ص�
		"""
		if self.combatCount > 0:
			self.calCombatCount( -csdefine.ROLE_CombatCount_TIMMER_VALUE )
		else:
			self.endAutoCombatCount()

	def endAutoCombatCount( self ):
		"""
		����timmer
		"""
		self.cancel( self.autoCombatCountID )
		self.autoCombatCountID = 0


	# ----------------------------------------------------------------
	# װ���������
	# ----------------------------------------------------------------
	def _calcuRepairEquipMoney( self, equip, repairType, revenueRate ):
		"""
		��������һ��װ���ļ۸�
		@param    equip: װ������
		@type     equip: instance
		@param    repairType: ��������
		@type     repairType: UNIT8
		@param    revenueRate	: ˰�ձ���
		@type     revenueRate	: UINT16
		@return: ���ռ۸�, ����˰
		"""
		# ��ͨ���������ѱ���Ϊ 1
		if repairType == csdefine.EQUIP_REPAIR_NORMAL:
			repairCostRate = 1
		# �������������ѱ���Ϊ 3
		elif repairType == csdefine.EQUIP_REPAIR_SPECIAL:
			repairCostRate = 1.5
		elif repairType == csdefine.EQUIP_REPAIR_ITEM:
			return 0, 0
		else:
			assert "That is a Error!!!, use undefine repair type "

		# Ʒ��ϵ��*��1-��ʵ���;ö�/ԭʼ����;öȣ���*���߼۸���ȥ��С����1�ķ���ȡ����
		repairRate = EquipQualityExp.instance().getRepairRateByQuality( equip.getQuality() )
		repairMoney = repairRate * ( 1 - float( equip.getHardiness() ) / float( equip.getHardinessLimit() ) ) * equip.getRecodePrice() * repairCostRate
		revenueMoney = 0
		iMoney = int( repairMoney )
		if iMoney != repairMoney:
			repairMoney = iMoney + 1

		# ����ռ�������10%
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
		����װ������
		@param    repairType	: ��������
		@type     repairType	: int
		@param    kitBagID		: ��������
		@type     kitBagID		: UINT16
		@param    orderID		: ��Ʒ����
		@type     orderID		: INT32
		@param    revenueRate	: ˰�ձ���
		@type     revenueRate	: UINT16
		@param    npcID			: NPC��ID
		@type     npcID			: STRING
		@return   ��
		"""
		# ��ȡҪ���������װ��
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_REPARE, "" )
			return
		equip = self.getItem_( orderID )
		if equip == None:
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_EXIST )
			return
		#  �ж�װ���ܷ�����
		if not equip.canRepair():
			self.statusMessage( csstatus.EQUIP_REPAIR_CANT_REPAIR )
			return
		#  �ж�װ���;ö��Ƿ���������
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
		# ��¼����˰��
		if revenueMoney > 0:
			BigWorld.globalData[ "TongManager" ].onTakeCityRevenue( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), revenueMoney )

	def repairAllEquip( self, repairType, revenueRate, npcID):
		"""
		define method.
		������������װ��
		@param    repairType: ��������
		@type     repairType: int
		@param    revenueRate	: ˰�ձ���
		@type     revenueRate	: UINT16
		@param    npcID			: NPC��ID
		@type     npcID			: STRING
		@return   ��
		"""
		if self.iskitbagsLocked():	# ����������by����
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
		# ��¼����˰��
		if revenueMoney > 0:
			BigWorld.globalData[ "TongManager" ].onTakeCityRevenue( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), revenueMoney )

	# ----------------------------------------------------------------
	# װ��ĥ��
	# ----------------------------------------------------------------
	def _addHardiness( self, equip, value ):
		"""
		����;ö�
		@param equip: װ��
		@type  equip: instance
		@param value: �;ö�
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

		# װ���½�����;���װ�����ڵ��;ò�ֵ����10000����֪ͨ�ͻ���
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
		#TEMP_MSG("װ��%i�;ö����: %s"%(equip.query("type"), max( 1.0, demageValue * hardinessAbrasion ) )	)
		self._addHardiness( equip, -max( 1.0, demageValue * hardinessAbrasion ) )

	def onEquipHardinessDegrade( self, equip ):
		"""
		װ���;ö�С��20%
		@param equip: װ��
		@type  equip: instance
		"""
		self.statusMessage( csstatus.CIB_MSG_EQUIP_HARDINESS, equip.query("name") )

	def equipAbrasionOnDied( self, killer ):
		"""
		�������װ���;õ�ĥ��

		��NPCɱ���������;ö���ʧΪ5%�����û�ɱ��������16:43 2009-6-12,wsf

		�����������ʱ��ʧװ���;öȵ���Ϊ4% �����������ʱ��ʧװ���;ö�Ϊ40%
		������ҵ�������ʧ���ڱ�NPCɱ��ʱ��Ч�����������ɱ�����κ���ʧ��
		������ҵ�������ʧ�ڱ�NPCɱ��ʱ���������ɱ��ʱ����Ч�� 10:45 2009-9-25 by����
		"""
		if killer is None:		# ���ʼǱ�ɱ���������;�ĥ��
			return

		if killer.getEntityType() == csdefine.ENTITY_TYPE_ROLE and self.pkValue <= 0:
			return

		# ��NPCɱ���������;ö���ʧΪ5%��
		equipList = self.getItems( csdefine.KB_EQUIP_ID )
		if self.pkValue <= 0:
			for equip in equipList:
				if equip.isEquip(): self._addHardiness( equip, -equip.getHardinessMax() * 0.04 )
		else:
			for equip in equipList:
				if equip.isEquip(): self._addHardiness( equip, -equip.getHardinessMax() * 0.2 )

	def moneyDropOnDied( self, killer ):
		"""
		������Ǯ����

		��NPCɱ����������ʧ����10%�Ľ�Ǯ��
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

		#TEMP_MSG("װ�����ܹ�������: %s"%demageValue)
		equipList = self.getItems( csdefine.KB_EQUIP_ID )
		equipList = [ k for k in equipList if k.getHardiness() != 0 ]	# ֻȡ���;öȵ�װ��
		if len( equipList ) == 0: return

		tempA = 1.0 #�ܳ־ö�
		tempB = 0.0 #�ж���ʱ��û�����װ���Ŀ�λ�ķ�̯��������
		tempC = 0.0 #�޶���ʱ��û�����װ���Ŀ�λ�ķ�̯��������
		hasNombril = False
		weapon = 0
		for i in equipList:
			eq_type = i.query("type")
			if eq_type == ItemTypeEnum.ITEM_WEAPON_SHIELD:
				hasNombril = True
			if eq_type in ItemTypeEnum.WEAPON_LIST:
				weapon = i
				continue
			tempB += g_armorAmend.getEquipDemageValueWithNombril( eq_type )	 #�ж���ʱ���˺���̯����
			tempC += g_armorAmend.getEquipDemageValueWithoutNombril( eq_type ) #�޶���ʱ���˺���̯����

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
		#TEMP_MSG("������������ƻ�����: %s"%demageValue )
		equipList = self.getItems( csdefine.KB_EQUIP_ID )
		equipList = [ k for k in equipList if k.getHardiness() != 0 and k.query("type") in ItemTypeEnum.WEAPON_LIST ]	# ֻȡ���;öȵ�װ��
		for equip in equipList:
			self._calcuEquipConsume( equip, demageValue, 0, False )

	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ��Ҫô�ж�Ҫô�Ѻ�
		ע��: ��Ϊ���������ʹ��Ƶ�ʼ���ĸߣ�Ϊ��Ч�ʣ����ֵĴ������ߺ������õķ�ʽ
		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		# �۲���ģʽ
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
						# ����δ����canPk�з������
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
			# ���ڻ��͵Ĺ����Ҫ�������⴦��
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_FRIEND_ROLE ): # ��ҶԹ�������Ѻñ�־
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
			if entity.queryTemp( "ownerTongDBID",0 ) != 0 and entity.queryTemp( "ownerTongDBID" ) == self.tong_dbID:		# ����ڳ������Ա�Ĺ�ϵΪ�Ѻ�
				return csdefine.RELATION_FRIEND
			ownerID = entity.getOwnerID()
			if BigWorld.entities.has_key( ownerID ):											#�ж��������˵ĵжԹ�ϵ
				if ownerID == self.id:
					return csdefine.RELATION_FRIEND
				return self.queryRelation( BigWorld.entities[ownerID] )
			elif self.pkState == csdefine.PK_STATE_PROTECT:
				return csdefine.RELATION_FRIEND
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_TREASURE_MONSTER:
			# ���ڵ�����������ǵ���
			return csdefine.RELATION_ANTAGONIZE

		# �ǰ����ս����
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

		# �����������
		if entity.utype == csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM:
			if entity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
				return csdefine.RELATION_FRIEND
			if self.teamMailbox and entity.belong == self.teamMailbox.id:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		# �m؅
		if entity.utype == csdefine.ENTITY_TYPE_YAYU:
			return csdefine.RELATION_FRIEND

		# ���ս������
		if entity.utype == csdefine.ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER:
			if self.yiJieFaction != 0 and entity.battleCamp == self.yiJieFaction :
				return csdefine.RELATION_FRIEND

		# �����ս����
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
			# �ѳ���ĵжԱȽ�ת�޸���������
			# ��Ȼ�˹�ϵδ�����ܻ���ݲ�ͬ��״̬��buff���¹�ϵ�ĸı䣬����ǰ��û�д�����
			entity = owner.entity

		if entity.state == csdefine.ENTITY_STATE_PENDING:
			return csdefine.RELATION_NOFIGHT
		if entity.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return csdefine.RELATION_NOFIGHT
		if self.state == csdefine.ENTITY_STATE_RACER:											#����״̬�������Ѻ�
			return csdefine.RELATION_FRIEND


		# ��ս�ж�
		# ��������
		if entity.utype == csdefine.ENTITY_TYPE_ROLE:
			if self.qieCuoState == csdefine.QIECUO_FIRE:
				if self.isQieCuoTarget( entity.id ):
					return csdefine.RELATION_ANTAGONIZE

		# ��ս
		if self.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT

		# ȫ����ս�ж�
		if self.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
			entity.effect_state  & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT

		# ����δ����canPk�з������
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and not entity.actionSign( csdefine.ACTION_FORBID_PK ):
			if self.hasEnemy( entity.id ) or self.pkTargetList.has_key( entity.id ):
				return csdefine.RELATION_ANTAGONIZE

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

	# ----------------------------------------------------------------
	# ��������
	# ----------------------------------------------------------------

	def dropOnDied( self ):
		"""
		��������
		"""
		# װ�����䶼��������װ������δ�󶨵�װ����
		# ������ȫ���װ�����Ѿ����򲻷�������
		# pkֵ == 0		��0.5%���ʵ���δ��װ��1��  �޸�Ϊͬ���ʵ���δ����װ��1�� by����
		# Pkֵ > 0		��10%�ļ�����ʧ1��2��	  by����
		# 30��pk����
		dropItemsOnDied = []	# ������Ʒ��copy
		dropItemsOrder = []		# ������Ʒ��order

		# ����������Ʒ
		for iItem in self.getAllItems():
			if iItem.query( 'merchantItem', False ):
				iItem.onDieDrop()
				dropItemsOnDied.append( iItem.copy() )
				dropItemsOrder.append( iItem.order )
				INFO_MSG( "Drop iItem %s (%s) Obey State %s"%( iItem.name, str(iItem.uid), str(iItem.isObey()) ) )

		if len( dropItemsOnDied ) != 0:
			# �������ӣ�������Ʒװ������
			x, y, z = self.position
			collide = BigWorld.collide( self.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
			# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
			if collide != None: y = collide[0].y
			itemBox = BigWorld.createEntity( "DroppedBox", self.spaceID, ( x, y, z ), self.direction, {} )
			itemBox.init( [], dropItemsOnDied )
			# phw: ��������Ȱ�Ҫɾ������Ʒ�������������ֱ��return�Ĵ��룬
			# �ᵼ�±�ɱ������Ʒ�������ˣ������ϵ���Ʒû��ɾ�������⡣
			for order in dropItemsOrder:
				self.removeItem_( order, reason = csdefine.DELETE_ITEM_DROPONDIED )
			# �����ÿ�Ҫɾ������Ʒ�б��Դ�����ʹ�á�
			dropItemsOrder = []

		# ����װ��
		if self.level <= csconst.PK_PROTECT_LEVEL: return
		# ����pkֵ��ȡ����
		if self.pkValue > 0:
			dropOdds = Const.PK_REDNAME_DROP_ODDS
		else:
			dropOdds = Const.PK_PEACE_DROP_ODDS

		# �ж��Ƿ������
		if random.random() > dropOdds: return
		# ��ȡδ������װ��
		unObeyEquips = self.getUnObeyEquips()
		canDropList = []
		if len( unObeyEquips ) <= 0: return
		# ��ÿɵ������װ��
		for uequip in unObeyEquips:
			if uequip.getType() not in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
				canDropList.append( uequip )
		if len( canDropList ) <= 0: return
		# �����ȡһ��װ��
		dropItem = random.choice( canDropList )
		dropItem.unWield( self )
		dropItemsOrder.append( dropItem.order )
		INFO_MSG( "%s(%i) drop Equip %s (%s) Obey State %s"%( self.getName(), self.id, dropItem.name, str(dropItem.uid), str(dropItem.isObey()) ) )
		# ����Ǻ��� ����һ��װ��
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
	# ��ʱ����
	# ----------------------------------------------------------------
	def delayCall( self, delay, methodName, *args ) :
		"""
		�ӳٵ���ĳ����������
		@param		delay	`	:	��ʱ����ʱ�䣬��λ����
		@type		delay		:	float
		@param		methodName	:	���ú�����
		@type		methodName	:	str
		@param		args		:	�����ú����Ĳ����б�ע��Ҫ�͵��ú����Ĳ�����Ӧ
		@type		args		:	int/float/str/double
		@rtype					:	int
		"""
		timerID = self.addTimer( delay, 0, ECBExtend.DELAY_CALL_TIMER_CBID )
		self.setTemp( "delayCallMethodName" + str( timerID ), methodName )
		self.setTemp( "delayCallParameter" + str( timerID ), args )
		return timerID

	def onDelayCallTimer( self, timerID, cbID ) :
		"""
		��delayCall��Ӧ��ʱ�䵽����ø�������
		@param		timerID	:	ʹ��addTimer()����ʱ�����ı�־����onTimer()������ʱ�Զ����ݽ���
		@type		timerID	:	int
		@param		cbID	:	��ǰ����������ı�ţ�ͬ����onTimer()������ʱ�Զ����ݽ���
		@type		cbID	:	int
		"""
		methodName = self.popTemp( "delayCallMethodName" + str( timerID ) )
		args = self.popTemp( "delayCallParameter" + str( timerID ) )
		method = getattr( self, methodName )
		method( *args )

	def showQuestLog( self, questID ) :
		"""
		֪ͨ�ͻ��˴�ָ�������������־
		@param		questID:	����ID
		@type		questID:	uint32
		"""
		self.client.onShowQuestLog( questID )


	# ----------------------------------------------------------------
	# space�������
	# ----------------------------------------------------------------
	def onLeaveSpace_( self ):
		"""
		����뿪�ռ�
		���ã�����뿪һ���ռ䣬�˹��ܻᱻ������
		"""
		if self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:	# �����ɫ������״̬����ֹͣ����
			self.stopDance( self.id )

		SpaceFace.onLeaveSpace_( self )
		self.cmi_onLeaveSpace()

	def onEnterSpace_( self ):
		"""
		define
		��ҽ���ռ�
		���ã�������ҽ�����һ���¿ռ䡣
		"""
		self.removeTemp( "isTeleporting" )

		SpaceFace.onEnterSpace_( self )
		RoleQuestInterface.onEnterSpace_( self )
		RoleQuizGame.onEnterSpace_( self )		# 17:09 2009-4-27,wsf
		CopyMatcherInterface.cmi_onEnterSpace( self )

		#�����ɫ��������ת�����������
		dieTeleport = self.queryTemp( "role_die_teleport", False )
		if dieTeleport:
			self.removeTemp( "role_die_teleport" )
			self.tombPunish()
			self.changeState( csdefine.ENTITY_STATE_FREE )
			self.setHP( self.HP_Max )
			self.setMP( self.MP_Max )

		#��������뿪�����Ƿ��쳣�ж� add by wuxo 2012-2-16
		sid = self.queryTemp("LeaveQuestTrapError",0)
		if sid != 0:
			self.client.hideQuestTrapTip( sid )#�ر���ʾ��Ϣ
			self.removeTemp("LeaveQuestTrapError")

		#�˵�ͼ�������ٻ�С���� add by wuxo 2011-12-7
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canConjureEidolon:
			if self.callEidolonCell() or self.queryTemp( "autoWithdrawEidolon", False ):#modify by wuxo 2011-12-1		#by cwl �������ǰС���鴦���Զ��ջ�״̬��ҲҪ����temp���Ա�����������ͼʱ�������г���
				self.withdrawEidolon( self.id )
				self.setTemp("eidolonState",True)#С����״̬��¼�Ա��ٻ�
		else:
			if self.queryTemp("eidolonState",False) and not self.queryTemp( "autoWithdrawEidolon", False ):		# ��������Զ�����С����״̬���ٻ�
				self.conjureEidolon( self.id )

		# �˵�ͼ��ֹ�ٻ�����
		if not spaceScript.canConjurePet:
			if self.pcg_getActPet():
				self.pcg_withdrawPet( self.id )



	def onEnterArea( self ) :
		"""
		Define Method
		ͬ��ͼ��ת�󱻵���
		hyw--2008.10.08
		"""
		self.removeTemp( "isTeleporting" )

		dieTeleport = self.queryTemp( "role_die_teleport", False )
		if dieTeleport : #�����ɫ��������ת���������¸����
			self.removeTemp( "role_die_teleport" )
			self.tombPunish()
			self.changeState( csdefine.ENTITY_STATE_FREE )
			self.setHP( self.HP_Max )
			self.setMP( self.MP_Max )
		self.client.onEnterAreaFS()

		# ��Ϊ�����������ת�Ļ����ﻹû�뿪��ɫ��AOI��Χ��
		# ��ת��ͻ��˾�û��ִ��enterworld������û��������������������ݣ����³���������ʧ��
		# Ŀǰ�����AI�����ɫ�뿪�����Զ�������Զ���ת��ȥ���������ΰ��������ת��
		#actPet = self.pcg_getActPet()
		#if actPet : 						# �������г�ս������֪ͨ
		#	self.pcg_teleportPet()			# ���������

	def onLeaveArea( self ):
		"""
		Define Method
		ͬ��ͼ��תǰ������
		hyw--2008.10.08
		"""
		# δ��BUFF
		if self.getState() == csdefine.ENTITY_STATE_DANCE or self.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:	# �����ɫ������״̬����ֹͣ����
			self.stopDance( self.id )
		self.spellTarget( csconst.PENDING_SKILL_ID, self.id )
		self.client.onLeaveAreaFS()

	def teleportToSpace( self, position, direction, cellMailBox, dstSpaceID ):
		"""
		���ã����͵�ָ��space�������������Ĺ��ܣ��������ָ���ռ䡣
		@type     		position	: vector3
		@param    		position	: Ŀ��λ��
		@type    		direction	: vector3
		@param   		direction	: ����
		@type  			cellMailBox	: MAILBOX
		@param 			cellMailBox	: ���ڶ�λ��Ҫ��ת��Ŀ��space����mailbox�������������Ч��cell mailbox
		"""
		isTeleporting = self.queryTemp( "isTeleporting", False )
		if self.vehicle is not None:
			DEBUG_MSG( "spaceID", self.spaceID, self.getName(), "id", self.id, "vid", self.vehicle.id, self.position, "dst", position, "inTeleporting", isTeleporting )
		else:
			DEBUG_MSG( "spaceID", self.spaceID, self.getName(), "id", self.id, self.position, "dst", position, "inTeleporting", isTeleporting )

		if self.queryTemp( "isTeleporting", False ): return
		self.setTemp( "isTeleporting", True )
		# ������������ж�����
		if self.attrIntonateSkill:
			self.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )
		# ����ڵ�����ȡ������
		if self.currentModelNumber == "fishing":
			self.end_body_changing( self.id, "" )
		SpaceFace.teleportToSpace( self, position, direction, cellMailBox, dstSpaceID )

	def tagTransport( self, spaceSign ):
		"""
		��Ǵ��������
		@param spaceSign: ������־
		@type  spaceSign: int
		"""
		self.transportHistory = self.transportHistory | spaceSign

	def onGotoSpaceBefore( self, spaceName ):
		"""
		����ǰ����
		"""
		pass

	def beforeEnterSpaceDoor( self, destPosition, destDirection ):
		"""
		���봫����֮ǰ��������
		"""
		RoleQuestInterface.beforeEnterSpaceDoor( self, destPosition, destDirection )
		Team.beforeEnterSpaceDoor( self, destPosition, destDirection )

	# ----------------------------------------------------------------
	# ���ģ�����
	# ----------------------------------------------------------------
	def resetEquipModel( self, order, newItem ):
		"""
		������ҵ�ģ�����
		"""
		# ���ͺ�����ģ�͵�������
	# ����ж��ƶ����ͻ���ȥ��,�Է���������ʱ�ͻ��˶�װ����ˢ�µ��쳣
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
			# �����Ƿ���...
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
		�����������ҿ���
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
		��ҵ�ǰĿ��ID�ı�
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ): return
		if self.targetID == targetID: return
		self.targetID = targetID
		#self.resetWAppendState()

	def changeHeadAbout( self, srcEntityID, newHairID, newFaceID, newHeadTextureID ):
		"""
		Exposed method
		�������ý�ɫ���͡�����ͷ��
		"""
		if self.hairNumber != newHairID: self.hairNumber = newHairID
		if self.faceNumber != newFaceID: self.faceNumber = newFaceID
		if self.headTextureID != newHeadTextureID: self.headTextureID = newHeadTextureID

	# ----------------------------------------------------------------
	# ��Ҹ������
	# ----------------------------------------------------------------
	def onRevive( self ):
		"""
		����ڸ��������һЩ����
		"""
		# ���¼���pk״̬
		self.onPkAttackChangeCheck()
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.getCurrentSpaceBase().cell.onRoleRevive( self.databaseID )

	def revive( self, srcEntityID, reviveType ):
		"""
		Exposed method
		�����ڸ����
		"""
		if not self.hackVerify_( srcEntityID ) : return
		# �������Ƿ�����
		if self.getState() != csdefine.ENTITY_STATE_DEAD:
			return

		self.setTemp( "role_die_teleport", True ) #������ʱ�������

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
		��������ʱ���п�����Ҫ��һЩ���������
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
		NPC���ûسǸ����
		"""
		self.reviveSpace = spaceName
		self.revivePosition = tuple( position )
		self.reviveDirection = tuple( direction )
		self.questSetRevivePos( spaceName )

	def setCurPosRevivePos( self ):
		"""
		Define Method
		��Ӧ��revivePreSpace
		"""
		self.setTemp( "enterPreSpaceType", self.spaceType )
		self.setTemp( "enterPreSpacePos", tuple( self.position ) )
		self.setTemp( "enterPreSpaceDirection", tuple( self.direction ) )

	def tombPunish( self ):
		"""
		�ظ����ͷ���
		"""
		pass

	def reviveOnTomb( self ):
		"""
		Ĺ�ظ���
		"""
		# ��������������һ��Ĺ�ص㸴��
		try:
			tomb = g_spacedata["tomb"][self.spaceType]
		except:
			ERROR_MSG("revive error!, not has tomb.", self.spaceType )
			return
		l = len( tomb )
		# �޸����
 		if l == 0:
			ERROR_MSG("revive error!, not has tomb.", self.spaceType )
			return
		# ����
		dict = None
		if l == 1:
			# ������������˵����
			dict = tomb[0]
		else:
			# ȡ����ĸ���㸴��
			near = None
			for info in tomb:
				distance = self.position.flatDistTo( Math.Vector3( info["position"] ) )
				if near == None or distance < near:
					near = distance
					dict = info
		# �ռ���Խ
		if dict != None:
			self.setTemp( "ignoreFullRule", True )	# ����һ����ǣ� �ڶ��ߵ�ͼ�к������ߵĹ��� �����ڸ������޷������������
			self.gotoSpace( dict["name"], dict["position"], dict["direction"] )
			self.removeTemp( "ignoreFullRule" )
		# ����ͷ����ı�״̬����Ѫ��ħ�Ƶ���onEnterArea��������,��Ϊ������Ļ���һῴ����ɫ��Ѫ��վ�����ٴ���

		self.onRevive()

	def reviveOnOrigin( self, hpPercent = 1.0, mpPercent = 1.0 ):
		"""
		ԭ�ظ���
		"""
		#����������ĵط�����
		if self.queryTemp( "role_die_to_revive_cbid", -1 ) != -1:							#ȡ�������ʱtimer
			self.cancel( self.queryTemp( "role_die_to_revive_cbid" ) )
		self.tombPunish()
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max*hpPercent )
		self.setMP( self.MP_Max*mpPercent )

		self.onRevive()

		self.reTriggerNearTrap()


	def reviveOnCity( self ):
		"""
		�سǸ��
		"""
		# ͨ����NPC��¼�㸴��
		self.setTemp( "ignoreFullRule", True )	# ����һ����ǣ� �ڶ��ߵ�ͼ�к������ߵĹ��� �����ڸ������޷������������
		self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )
		self.removeTemp( "ignoreFullRule" )
		self.onRevive()
		# ����ͷ����ı�״̬����Ѫ��ħ�Ƶ���onEnterArea��������,��Ϊ������Ļ���һῴ����ɫ��Ѫ��վ�����ٴ���
		self.TDB_onReviveOnCity()

	def reviveActivity( self ):
		# define method
		# ���Ѫ��������
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( 0 )
		self.setMP( 0 )
		self.onRevive()

	def revivePreSpace( self ):
		"""
		�ڽ��븱����ǰһ����ͼ����
		"""
		enterPreSpaceType = self.queryTemp( "enterPreSpaceType", self.reviveSpace )
		enterPreSpacePos = self.queryTemp( "enterPreSpacePos", self.revivePosition )
		enterPreSpaceDirection = self.queryTemp( "enterPreSpaceDirection", self.reviveDirection )
		self.gotoSpace( enterPreSpaceType, enterPreSpacePos, enterPreSpaceDirection )
		self.onRevive()

	def reviveOnSpace(self, space_label, position, direction):
		"""
		��ָ����ͼ����
		"""
		DEBUG_MSG("%s revive on space %s %s %s" % (self.getName(), space_label, position, direction))
		# ����һ����ǣ� �ڶ��ߵ�ͼ�к������ߵĹ��� �����ڸ������޷������������
		self.setTemp( "ignoreFullRule", True )
		self.gotoSpace(space_label, position, direction)
		self.removeTemp( "ignoreFullRule" )

		self.onRevive()

	# ----------------------------------------------------------------
	# ���ϻ����
	# ���Ϻϳɡ�װ����ס�װ��������װ����Ƕ��װ��ǿ����װ�����졢װ���󶨡�
	# ----------------------------------------------------------------
	def doCasketFunction( self, srcEntityID, functionIndex ):
		"""
		Exposed method
		# ִ�����ϻ����
		@param functionIndex: ���ϻ��������
		@type  functionIndex: UINT8
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.doCasketFucntionInterface( functionIndex )

	def doSpecialCompose( self, srcEntityID, idx ):
		"""
		Exposed method
		# ������ϳ�
		@param idx: �䷽����
		@type  idx: UINT8
		"""
		if not self.hackVerify_( srcEntityID ) :
			return False

		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#������ϻ��ʹ�ô���
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return
		if self.specialCompose( idx ):
			#���ϻ������1
			useDegree -= 1
			kitCasketItem.setUseDegree( useDegree )
			self.client.onUpdateUseDegree( useDegree )

	def stuffCompose( self, srcEntityID, baseAmount ):
		"""
		Exposed method
		���Ϻϳ�
		@param baseAmount: �ϳɻ���
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
		���Ϻϳ�
		@param uids: ��Ʒ��uid
		@type  baseAmount: list
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) :
			return
		if self.iskitbagsLocked():
			#��ʾ �����Ѿ�����
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#������ϻ��ʹ�ô���
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return
		if self.equipIntensify( uids ):
			#���ϻ������1
			useDegree -= 1
			kitCasketItem.setUseDegree( useDegree )
			self.client.onUpdateUseDegree( useDegree )

	# ----------------------------------------------------------------
	# װ������
	# ----------------------------------------------------------------
	def equipMake( self, srcEntityID, makeItemID, orders ):
		"""
		Exposed method
		װ������
		@param makeItemID	: Ҫ����װ����ID
		@type  makeItemID	: ITEM_ID
		@param orders		: array of Uint8
		@type  orders		: order �б�
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) : return
		INFO_MSG( "equipMake srcEntityID : %i"%srcEntityID )
		self.equipMakeIntereface( makeItemID, orders )

	def createDynamicItem( self, itemID ):
		"""
		role �ϵĴ�����Ʒ�ӿ�
		@param itemID	:	��ƷID
		@type itemID	:	ITEM_ID
		@return None/inherit CItemBase instance
		"""
		return items.instance().createDynamicItem( itemID )

	# ----------------------------------------------------------------
	# CombatUnit��������
	# ----------------------------------------------------------------
	def calcStrengthBase( self ):
		"""
		������������ֵ
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].strength
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].strength_value
		self.strength_base = v + v_value * ( self.level - 1 )

	def calcDexterityBase( self ):
		"""
		�������ݻ���ֵ
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].dexterity
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].dexterity_value
		self.dexterity_base = v + v_value * ( self.level - 1 )

	def calcIntellectBase( self ):
		"""
		������������ֵ
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].intellect
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].intellect_value
		self.intellect_base = v + v_value * ( self.level - 1 )

	def calcCorporeityBase( self ):
		"""
		�������ʻ���ֵ
		"""
		v = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].corporeity
		v_value = CombatUnitConfig.ROLE_COMBAT_RADIX[self.getClass()].corporeity_value
		self.corporeity_base = v + v_value * ( self.level - 1 )

	def calcHPCureSpeed( self ):
		"""
		���������ָ��ٶ�
		��ɫ���������ԣ�������ɫÿ3����Իָ���������ֵ��ս��ʱ��Ч����ֵ����
		"""
		self.HP_regen_base = int( 3.0 * self.corporeity * 0.03 + 11 )
		RoleEnmity.calcHPCureSpeed( self )

	def calcMPCureSpeed( self ):
		"""
		��ɫ���������ԣ�������ɫÿ3����Իָ��ķ�����ֵ��ս��ʱ��Ч����ֵ����
		"""
		self.MP_regen_base = int( 3.0 * self.intellect * 0.03 + 15 )
		RoleEnmity.calcMPCureSpeed( self )

	# ----------------------------------------------------------------
	def onJumpNotifyFC( self, srcEntityID, jumpMask ):
		"""
		Exposed method
		��������������пͻ���jump�����Ĺ㲥��Ϣ�����ͻ��˵���
		"""
		if self.id != srcEntityID: return

		jumpTime = jumpMask & csdefine.JUMP_TIME_MASK

		# �����˺�= ��ɫ��ǰ��������ֵ x ��������� �C �����˺��߶ȣ�/50
		if jumpTime == csdefine.JUMP_TIME_UP1:
			self.fallDownHeight = self.position.y
		if jumpTime == csdefine.JUMP_TIME_DOWN:
			self.fallDownHeight = self.position.y
			# ����������
			#self.actCounterInc( csdefine.ACTION_FORBID_INTONATING )
		elif jumpTime == csdefine.JUMP_TIME_END:
			# ��غ�����������������
			#self.actCounterDec( csdefine.ACTION_FORBID_INTONATING )
			self.__receiveFallDownDmg()
		elif jumpTime == csdefine.JUMP_TIME_UP2:
			#����2����
			if self.vehicleModelNum == 0 and (self.hasSkill( csdefine.JUMP_UP2_SKILLID ) or self.hasSkill( csdefine.JUMP_UP3_SKILLID )) and self.energy >= csdefine.JUMP_UP2_ENERGY:
				self.calEnergy( - csdefine.JUMP_UP2_ENERGY )
			else: #��������
				self.fallDownHeight = self.position.y
				#self.actCounterInc( csdefine.ACTION_FORBID_INTONATING )
				jumpMask = csdefine.JUMP_TYPE_LAND |csdefine.JUMP_TIME_DOWN
		elif jumpTime == csdefine.JUMP_TIME_UP3:
			#����2����
			if self.vehicleModelNum == 0 and self.hasSkill( csdefine.JUMP_UP3_SKILLID ) and self.energy >= csdefine.JUMP_UP3_ENERGY:
				self.calEnergy( - csdefine.JUMP_UP3_ENERGY )
			else: #��������
				self.fallDownHeight = self.position.y
				#self.actCounterInc( csdefine.ACTION_FORBID_INTONATING )
				jumpMask = csdefine.JUMP_TYPE_LAND |csdefine.JUMP_TIME_DOWN
		# ����Ҫ֪ͨ�Լ���ֻ��Ҫ֪ͨ�Լ���Χ����Ҽ���
		self.planesOtherClients( "onJumpNotifyFS", ( jumpMask, ) )

	def __receiveFallDownDmg( self ):
		"""
		�����˺�����
		"""
		damage = int( self.HP_Max * ( self.fallDownHeight - self.position.y - Const.ROLE_DROP_DAMAGE_HEIGHT ) / 50 )
		if damage > 0:
			self.HP = max( 0, self.HP - damage )
			if self.HP == 0:
				self.MP = 0
				self.die(0)
			else:				# ûˤ���ͻ�Ѫ
				self.revertCheck()
		self.fallDownHeight = 0.0

	def onFlyJumpUpNotifyFC( self, srcEntityID ):
		"""
		Exposed method
		��������������пͻ���j���и߶������Ĺ㲥��Ϣ���������ͻ��˵���
		"""
		if self.id != srcEntityID:
			return
		if not self.hasFlag( csdefine.ROLE_FLAG_FLY ):
			return
		p = self.position
		if p.y >= 100:p.y = 100.0			# ��������
		self.position = (p.x,p.y+1.8,p.z)		# ƽ��ÿ�������߶ȵ���һ����Ծ�߶�
		self.planesOtherClients( "onFlyJumpUpNotifyFS", () )

	def getBoundingBox( self ):
		"""
		virtual method.
		���ش��������bounding box�ĳ����ߡ����Vector3ʵ����
		��������ģ���б����Ź�����Ҫ�ṩ���ź��ֵ��

		@return: Vector3
		"""
		# Ϊ��ʹ�ж�һ�£����ǵ�bounding box��������ͻ���ʹ����ͬ��ֵ��
		# ����б�Ҫ�����Կ��Ǹ��ݲ�ͬ��ְҵʹ�ò�ͬ��ֵ
		# ��������зŴ�ģ�͵ļ��ܣ�������Ҫ����ʵ����������Ƿ����Ŵ���
		if self.vehicle:
			return self.vehicle.getBoundingBox()
		if VehicleHelper.getCurrVehicleID( self ):
			return csconst.VEHICLE_MODEL_BOUND
		return csconst.ROLE_MODEL_BOUND

	def recordLastSpaceLineData( self, lineNumber, maxLine ):
		"""
		define method.
		��¼���һ�ν�����ߵ�ͼ������Ϣ
		"""
		self.lastSpaceLineNumber = lineNumber
		self.lastSpaceMaxLine = maxLine

	def createNPCObjectFormBase( self, spaceKey, npcID, position, direction, state ):
		"""
		define method
		��base�����ƶ���space�д���һ������ҿ��ƶ���

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# ���__lineNumber__���ṩ�߿��Ƶģ� ���磺���ʹ�������ⲿ�ƶ���һ��Ҫˢ���ߣ���ôĳ���������������ߵĻ�
		# ������ｫ��ˢ��ָ�������ϣ� ���û��ָ���ߣ� ��ˢ���������¼�����һ�ν�����ߵ�Ŀ��space��
		if state.get( "_lineNumber_", 0 ) == 0:
			state[ "_lineNumber_" ] = self.lastSpaceLineNumber
		self.getSpaceManager().createNPCObjectFormBase( spaceKey, npcID, position, direction, state )

	def createCellNPCObjectFormBase( self, spaceKey, npcID, position, direction, state ):
		"""
		define method
		��base�����ƶ���space�д���һ������ҿ��ƶ���

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# ���__lineNumber__���ṩ�߿��Ƶģ� ���磺���ʹ�������ⲿ�ƶ���һ��Ҫˢ���ߣ���ôĳ���������������ߵĻ�
		# ������ｫ��ˢ��ָ�������ϣ� ���û��ָ���ߣ� ��ˢ���������¼�����һ�ν�����ߵ�Ŀ��space��
		if state.get( "_lineNumber_", 0 ) == 0:
			state[ "_lineNumber_" ] = self.lastSpaceLineNumber
		self.getSpaceManager().createCellNPCObjectFormBase( spaceKey, npcID, position, direction, state )

	# ----------------------------------------------------------------
	# ��·��
	# ----------------------------------------------------------------
	def flyToNpc( self, srcEntityID, npcID, questID, order ):
		"""
		Exposed Method
		ʹ����·�䵽��ָ��NPC
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# ������ʹ����·��ĸ���״̬
		cantFlyings = [ ( csdefine.ENTITY_STATE_FIGHT, csstatus.SKILL_USE_ITEM_WHILE_FIGHTING ),# ս��
						( csdefine.ENTITY_STATE_DEAD, csstatus.SKILL_USE_ITEM_WHILE_DEAD ),		# ����
						( csdefine.ENTITY_STATE_VEND, csstatus.ROLE_VEND_CANNOT_FLY ),			# ��̯
						( csdefine.ENTITY_STATE_RACER, csstatus.ROLE_RACE_CANNOT_FLY ),			# ����
						( csdefine.ENTITY_STATE_QUIZ_GAME, csstatus.ROLE_QUIZ_CANNOT_FLY ),		# ֪ʶ�ʴ�
					]
		for (state, infoMessage) in cantFlyings:
			if ( state == self.getState() ):
				self.statusMessage( infoMessage )
				return

		if not self.controlledBy:	# ���ʧȥ����ʱ������ʹ��
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#Я��������Ʒ������ʹ����·��
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# ����з�������buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#�ڼ����в��ܴ���
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

		# ������Ʒ���������ᡢ����״̬��Ӱ�� by����
		if item.isFrozen(): return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		if self.getState() == csdefine.ENTITY_STATE_CHANGING:
			# ʹ����·��Ҫȡ������״̬
			self.changeState( csdefine.ENTITY_STATE_FREE )

		# Ŀ������x,z���ƫ����
		x = random.randint( -1, 1 )
		z = random.randint( -1, 1 )

		if npcID in g_NPCsPosition:	#�������ͨNPC
			npcPosition = g_NPCsPosition[ npcID ]
			if npcPosition[ "fixed" ]:	# ���λ����ȷ����
				x = 0
				z = 0

			self.gotoSpace( npcPosition['spaceLabel'], Math.Vector3( npcPosition['position'] ) +  Math.Vector3( x, 0, z ), (0,0,0) )

		elif questID and self.questsTable and self.questsTable.has_quest( questID ) and \
			self.getQuest( questID ).getType() == csdefine.QUEST_TYPE_POTENTIAL:
			#�����Ǳ�ܸ���NPC, ȡ��space id���漴���ɵ��Ǹ�����
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
		self.removeItem_( order, 1, csdefine.DELETE_ITEM_USEFLY )	#�Ƴ�����·��
		self.client.onUseFlyItem()

	# ----------------------------------------------------------------
	# ��·��
	# ----------------------------------------------------------------
	def flyToSpacePosition( self, srcEntityID, treasureOrder, order ):
		"""
		Exposed Method
		ʹ����·�䵽��ָ����ͼ��λ��
		"""
		if not self.hackVerify_( srcEntityID ) : return
		#ս��״̬��������·��
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
		if not self.controlledBy:	# ���ʧȥ����ʱ������ʹ��
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#Я��������Ʒ������ʹ����·��
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# ����з�������buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#�ڼ����в��ܴ���
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

		# ������Ʒ���������ᡢ����״̬��Ӱ�� by����
		if item.isFrozen(): return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		treasureSpace = treasureItem.query( "treasure_space", "" )		# ȡ���ر�ͼ�еĵ�ͼ��Ϣ
		treasurePosStr = treasureItem.query( "treasure_position", None )# ȡ���ر�ͼ�е�������Ϣ
		treasurePos = eval( treasurePosStr )
		self.gotoSpace( treasureSpace, treasurePos, (0,0,0) )

		self.removeItem_( order, 1, csdefine.DELETE_ITEM_USEFLY  )	#�Ƴ�����·��
		self.client.onUseFlyItem()


	def flyToPlayerPosition( self, srcEntityID, space, lineNumber, position, order ):
		"""
		Exposed Method
		�ɵ����λ��
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# ������ʹ����·��ĸ���״̬
		cantFlyings = [ ( csdefine.ENTITY_STATE_FIGHT, csstatus.SKILL_USE_ITEM_WHILE_FIGHTING ),# ս��
						( csdefine.ENTITY_STATE_DEAD, csstatus.SKILL_USE_ITEM_WHILE_DEAD ),		# ����
						( csdefine.ENTITY_STATE_VEND, csstatus.ROLE_VEND_CANNOT_FLY ),			# ��̯
						( csdefine.ENTITY_STATE_RACER, csstatus.ROLE_RACE_CANNOT_FLY ),			# ����
						( csdefine.ENTITY_STATE_QUIZ_GAME, csstatus.ROLE_QUIZ_CANNOT_FLY ),		# ֪ʶ�ʴ�
					]
		for (state, infoMessage) in cantFlyings:
			if ( state == self.getState() ):
				self.statusMessage( infoMessage )
				return

		if not self.controlledBy:	# ���ʧȥ����ʱ������ʹ��
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#Я��������Ʒ������ʹ����·��
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# ����з�������buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#�ڼ����в��ܴ���
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

		# ������Ʒ���������ᡢ����״̬��Ӱ�� by����
		if item.isFrozen(): return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		if self.getState() == csdefine.ENTITY_STATE_CHANGING:
			# ʹ����·��Ҫȡ������״̬
			self.changeState( csdefine.ENTITY_STATE_FREE )

		if lineNumber > 0:
			self.gotoSpaceLineNumber( space, lineNumber, position, (0,0,0) )
		else:
			self.gotoSpace( space, position, (0,0,0) )

		self.removeItem_( order, 1, csdefine.DELETE_ITEM_USEFLY )	#�Ƴ�����·��
		self.client.onUseFlyItem()

	def onRequestCell( self, cellMailbox, baseMailbox ):
		"""
		���������ռ� entity��cell����
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
		�ӳٴ��ͣ���ʼ����
		"""
		if not self.hackVerify_( srcEntityID ): return
		if self.getState() == csdefine.ENTITY_STATE_DEAD: return  # ����״̬����ʧ��
		if not result: return
		self.gotoSpace( spaceName, pos, (0,0,0) )

	#-------------------------�۲�Է� ��ش���------------------
	def getTargetEspialAttribute( self , observer):
		"""
		�����Լ��Ĳ������Ը��۲���
		@param observer	: �۲��ߵ�MAILBOX
		@type  observer	: MAILBOX
		"""
		observer.client.showTargetAttribute( self.id )

	def	getTargetEspialEquip( self, observer, BeginPos, GetNumber ):
		"""
		��ȡָ���ļ���λ�õ�װ��
		"""
		targetEquips = self.getItems(csdefine.KB_EQUIP_ID)				#װ������Ϣ
		Items = []
		for	i in xrange(GetNumber):
			try:
				item = targetEquips[BeginPos + i]
			except IndexError: #��ʾ�Ѿ�û�п���ȡ����
				observer.client.showTargetEquip( Items , True)
				return
			Items.append( item)
		observer.client.showTargetEquip( Items , False)

	def getTargetAttribute( self , srcEntityID, targetID):
		"""
		Exposed method
		��ȡҪ�۲����ҵĲ���������Ϣ
		@param srcEntityID	: ����Լ���ID
		@type  makeItemID	: OBJECT_ID
		@param targetID		: ���۲�Ķ����ID
		@type  targetID		: OBJECT_ID
		@return None
		"""
		if srcEntityID != self.id: #�ж��Ƿ����Լ��Ŀͻ���������
			return

		target = BigWorld.entities.get( targetID )
		if target is None: #û��������
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
			return
		target.getTargetEspialAttribute( self ) #��ȡ�Է���ҵĲ�������

	def getTargetEquip(self, srcEntityID, targetID, BeginPos, GetNumber):
		"""
		Exposed method
		��ȡҪ�۲�����װ����Ϣ
		@param srcEntityID	: ����Լ���ID
		@type  makeItemID	: OBJECT_ID
		@param targetID		: ���۲�Ķ����ID
		@type  targetID		: OBJECT_ID
		@param BeginPos		: Ҫ��ȡ��װ���Ŀ�ʼλ��
		@type  BeginPos		: INT
		@param GetNumber	: Ҫ��ȡ��װ��������
		@type  GetNumber	: INT
		@return None
		"""
		if srcEntityID != self.id: #�ж��Ƿ����Լ��Ŀͻ���������
			return

		target = BigWorld.entities.get( targetID )
		if target is None: #û��������
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
			return
		target.getTargetEspialEquip( self , BeginPos, GetNumber) #��ȡ�Է���ҵĲ�������

	def isSunBathing( self ):
		"""
		����Ƿ��ڽ����չ�ԡ
		"""
		spaceType = self.getCurrentSpaceType()
		return spaceType == csdefine.SPACE_TYPE_SUN_BATHING

	def gotoRacehorseMap( self, srcEntityID ):
		"""
		Exposed method
		���������ͼ
		"""
		if srcEntityID != self.id: #�ж��Ƿ����Լ��Ŀͻ���������
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
		��ɫ���ı�֪ͨ������ϵ
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
		��ò�ͬentity�ļ����ͷ�ƫ��ֵ��ģ�巽��

		ƫ�����������ڿͻ��˴����ͷż��ܵ�entity�����壬����entityĿǰֻ�н�ɫ��
		"""
		return csconst.ATTACK_RANGE_BIAS


	# ----------------------------------------------------------------
	#��Ʒ��ش���ʰȡ��Ʒ�����������Ʒ�ȣ�
	# ----------------------------------------------------------------
	def useItemRevive( self,srcEntityID ):
		"""
		Exposed method
		�ø�����Ʒ����
		"""
		if self.id != srcEntityID:return
		if not self.state == csdefine.ENTITY_STATE_DEAD:return
		itemID  = 110103001
		items = self.findItemsByIDFromNKCK( itemID )
		if items :
			if self.iskitbagsLocked() :
				self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
				return
			if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_WU_DAO:		# ��������������������޷�����
				self.statusMessage( csstatus.WU_DAO_NOT_REVIVE )
				return
			item = items[0]
			item.use( self,self ) #��Ϊuse���������е���checkUse���м�飬�����ݲ���飬ֱ��ʹ��
			self.removeItem_( item.order,1, csdefine.DELETE_ITEM_USEITEMREVIVE )
			self.reTriggerNearTrap() #ԭ�ظ���ٴδ���30�׷�Χ����������

	def requestAddItem( self, id, index, item, isQuestItem ):
		"""
		�ж��Ƿ��ܼ��������Ʒ���Ǯ
		"""
		dropBoxEntity = BigWorld.entities.get( id )
		if dropBoxEntity is None: return

		if item.isType( ItemTypeEnum.ITEM_MONEY ):
			if self.gainMoney( item.amount, csdefine.CHANGE_MONEY_REQUESTADDITEM  ):
				dropBoxEntity.receiveItemPickedCB( self.id, index, True, isQuestItem, True, self.databaseID )
			else:
				dropBoxEntity.receiveItemPickedCB( self.id, index, False, isQuestItem, True, 0 )
		else:
			# �������ӵĵ����������ж�
			# ��������ǹ��ﱬ�����ģ���ô�Թ��ﱬ����ʽ�����Ʒ
			# ��������ǿ����䱬�����ģ���ô�Կ����䷽ʽ�����Ʒ
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
		����������������Ʒ
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
		�ж��Ƿ��ܼ��������Ʒ
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
		ʰȡһ����ƷEntity

		@param itemMailbox: ����ȡ��Item Entity's cell mailbox
		@type  itemMailbox: MAILBOX
		@param    itemData: ��Ʒ����ʵ��
		@type     itemData: ITEM
		@return:            �������ķ�����û�з���ֵ
		"""
		DEBUG_MSG( "itemMailbox = %i, itemData = %s" % (itemMailbox.id,  itemData.id ) )

		self.onPickUpTrigger()

		if self.addItemAndNotify_( itemData, csdefine.ADD_ITEM_PICKUPITEM ):
			itemMailbox.pickupCB( 1 )	# True
		else:
			itemMailbox.pickupCB( 0 )	# False

	def onPickUpTrigger( self ):
		"""
		ʰȡ��Ϊ������13:37 2008-12-1,wsf
		"""
		self.removeAllBuffByBuffID( csconst.PROWL_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )	# ��Ͻ�ɫ��Ǳ��Ч��buff

	def pickupMoney( self, mailbox, amount ):
		"""
		Define method.
		��Ǯ

		@param itemMailbox: ����ȡ��Item Entity's cell mailbox
		@type  itemMailbox: MAILBOX
		@param      amount: Ǯ������
		@type       amount: UINT32
		"""
		if self.gainMoney( amount, csdefine.CHANGE_MONEY_PICKUPMONEY ):
			mailbox.pickupCB( 1 )	# �ɹ�
		else:
			mailbox.pickupCB( 0 )	# ʧ��
		return	# the end



	# ----------------------------------------------------------------
	# ����
	# ----------------------------------------------------------------
	def addTalismanExp( self, srcEntityID ):
		"""
		Exposed method
		���ӷ�������
		"""
		if srcEntityID != self.id:return
		self.addTalismanExpInterface()

	def addTalismanPotential( self, srcEntityID ):
		"""
		Exposed method
		������������
		"""
		if srcEntityID != self.id:return
		self.addTalismanPotentialInterface()

	def updateTalismanGrade( self, srcEntityID ):
		"""
		Exposed method
		��������Ʒ��
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.updateTalismanGradeInterface()

	def activateTalismanAttr( self, srcEntityID, uid ):
		"""
		Exposed method
		���������
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.activateTalismanAttrInterface( uid )

	def rebuildTalismanAttr( self, srcEntityID, grades, indexs ):
		"""
		Exposed method
		���취������
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.rebuildTalismanAttrInterface( grades, indexs )

	def reloadTalismanSkill( self, srcEntityID ):
		"""
		Exposed method
		����ˢ����
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.reloadTalismanSkillInterface()

	# --------------------------------------------------------------------------------------------------
	def equipGodWeapon( self, srcEntityID, weaponItem ):
		"""
		Exposed method

		��������
		"""
		self.equipGodWeaponInterface( weaponItem )
	# --------------------------------------------------------------------------------------------------

	def addSunBathCount( self, controllerID, userData ):
		"""
		�����չ�ԡʱ��
		"""
		self.updateSunBathCount( 10 )

	def updateSunBathCount( self, value ):
		"""
		����(�����)����չ�ԡʱ��
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
		Ч���ı�.13:58 2009-3-13��wsf
			@param estate		:	Ч����ʶ(�����)
			@type estate		:	integer
			@param disabled		:	Ч���Ƿ���Ч
			@param disabled		:	bool
		"""
		Team.effectStateChanged( self, estate, disabled )

	def addPkValue( self, value ):
		"""
		Define Method
		����pkֵ
		"""
		self.setPkValue( self.pkValue + value )

	def onPKValueChanged( self, oldPkValue ):
		"""
		pkֵ�ı�
		"""
		# �Ƿ�����
		if self.pkValue > oldPkValue and self.pkValue >= csdefine.PK_CATCH_VALUE:
			self.prisonHunt()
		elif self.pkValue <= 0:
			self.endPkValueTimer()

	def prisonHunt( self ):
		"""
		����׷��
		"""
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		# �ж��Ƿ��ץ���ﷸ�ĵ�ͼ �������ͷ�׷��buff
		if not spaceScript.canArrest:
			self.spellTarget( csdefine.SKILL_ID_CATCH_PRISON, self.id )
		else:
			self.setTemp( "gotoPrison", True )
			self.gotoSpace( "fu_ben_jian_yu", (0,0,0), (0,0,0) )

	def setPkValue( self, value ):
		"""
		����pkֵ
		���ô˷���ȷ���Լ���RealEntity
		"""
		# pkֵȡֵ��Χ 0~65535
		if value < 0: value = 0
		if value > 0xffff: value = 0xffff

		if self.pkValue == value: return
		oldPkValue = self.pkValue
		self.pkValue = value
		self.onPKValueChanged( oldPkValue )

		# ���pkֵ����0���ر�pkֵtimer����������ֵtimer
		# ���pkֵ����0������pkֵtimer���ر�����ֵtimer��ÿ��20����pkֵ��1
		if self.pkValue == 0:
			self.addPkFlag( csdefine.PK_STATE_PEACE )
			
		elif 0 < self.pkValue < 18:
			# pkֵ����0~17��ʾ����״̬��С������
			self.setGoodnessValue( 0 )		#��PKֵ������ƶ�ֵ			
			self.addPkFlag( csdefine.PK_STATE_ORANGENAME )		
			
		else:
			# pkֵ18���ϱ�ʾ����״̬
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
		����pkֵ�ı�ʱ�������
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
		ȡ���ƶ�ֵ�ı�ʱ�������
		"""
		if self.pkValueTimer != 0:
			DEBUG_MSG( "end pkvalue[%i] Timer!" % ( self.pkValue ) )
			self.cancel( self.pkValueTimer )
		self.pkValueTimer = 0

	def optionReduceRD_goodness( self ):
		"""
		����ֵ�ı�����������ӡ�ɾ��
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
		��������ֵ
		"""
		if value < 0: value = 0
		if value > csconst.PK_GOODNESS_MAX_VALUE: value = csconst.PK_GOODNESS_MAX_VALUE
		if self.goodnessValue == value: return
		self.goodnessValue = value

		#�������мӳ�buff
		self.optionReduceRD_goodness()
		if value == csconst.PK_GOODNESS_MAX_VALUE:
			self.addPkFlag( csdefine.PK_STATE_BLUENAME )
		else:
			self.removePkFlag( csdefine.PK_STATE_BLUENAME )
	
	def addPkFlag( self, nameFlag ):
		"""
		����һ��PK״̬
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
		����һ��PK״̬
		"""
		if self.pkFlags & nameFlag > 0:
			self.pkFlags &= ~nameFlag
		
		self.updatePkState()
			
	def updatePkState( self ):
		"""
		����PK״̬
		��>��>��>��>��>��
		"""
		#�ְ������ܳ��ֹ�������	
		#��ɫ�ͻ�ɫ�����κ�һ��������棨��Ϊ�����PKֵ�������ƶ�ֵ������ɾ��������
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
		����pkֵ�ı�ʱ�������
		"""
		if self.goodnessTimer != 0: return
		self.goodnessTimer = self.addTimer( Const.PK_GOOSNESS_ADD_TIME, Const.PK_GOOSNESS_ADD_TIME, ECBExtend.PK_ADD_GOODNESS_TIMER_CBID )

	def endGoodnessTimer( self ):
		"""
		ȡ���ƶ�ֵ�ı�ʱ�������
		"""
		if self.goodnessTimer != 0:
			self.cancel( self.goodnessTimer )
		self.goodnessTimer = 0

	def resetPkState( self ):
		"""
		�ȼ��������¼���pk״̬
		"""
		# �����ǰpk״̬��pk����״̬��ֱ�ӹ���
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
		����pk״̬
		"""
		if self.pkState == state: return
		self.pkState = state

		if state == csdefine.PK_STATE_PEACE:
			# �ر�pkֵ����timer
			self.endPkValueTimer()
			# �����ƶ�ֵ����timer
			self.startGoodnessTimer()
		elif state == csdefine.PK_STATE_REDNAME or state == csdefine.PK_STATE_ORANGENAME:
			# ����pkֵ����timer
			self.startPkValueTimer()
			# �ر��ƶ�ֵ����timer
			self.endGoodnessTimer()
			# �ر�pkAttackTimer
			self.endPkAttackTimer()
		elif state == csdefine.PK_STATE_BLUENAME:
			# �ر��ƶ�ֵ����timer
			self.endGoodnessTimer()

	def setPkMode( self, srcEntityID, mode ):
		"""
		Exposed Method
		����pkģʽ
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
		���ð�ḱ����pkģʽ
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
		# ����ڰ�ȫ���Ͳ���PK�ĸ����в�����
		if self.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ) or not spaceScript.canPk:
			return

		self.statusMessage( csstatus.ROLE_PK_MODE_UNLOCK )
		self.isPkModelock = False

	def addPKTarget( self, id ):
		"""
		��PK�б�
		"""
		if not self.pkTargetList.has_key( id ):
			self.pkTargetList[ id ] = BigWorld.time()
			self.pkTargetList = self.pkTargetList
			self.onPKListChange( id )
		self.startPKFightBackTimer( id )
		INFO_MSG( " My pkTargetLsit is %s, pkFightBackTimer %s" % ( self.pkTargetList, self.pkFightBackTimer ) )

	def resetPKTargetList( self ):
		"""
		����PK�б�
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
		���һ��PK����
		"""
		if self.pkTargetList.has_key( entityID ):
			self.pkTargetList.pop( entityID )
			self.onPKListChange( entityID )
			self.endPKFightBackTimer( entityID )
		else:
			return

	def onPKListChange( self, id ):
		"""
		PK �б����ı䣬��Ҫ��Ӱ��ͻ��˽�����ʾ
		"""
		INFO_MSG( " Info client pkTargetList change %s " % self.pkTargetList )
		self.client.onPKListChange( self.pkTargetList, id )

	def startPKFightBackTimer( self, id ):
		"""
		����PK����״̬ʱ�������
		"""
		self.endPKFightBackTimer( id )
		self.pkFightBackTimer[ id ] = self.addTimer( Const.PK_FIGHT_BACK_TIME, 0, ECBExtend.PK_STATE_FIGHT_BACK_TIMER_CBID)

	def endPKFightBackTimer( self, id  ):
		"""
		����PK����Timer
		"""
		if self.pkFightBackTimer.has_key( id ):
			if self.pkFightBackTimer[id] != 0:
				self.cancel( self.pkFightBackTimer[id] )
				self.pkFightBackTimer[id] = 0

	def onPkFightBackChangeTimer( self, controllerID, userData ):
		"""
		pk����״̬���
		"""
		for eid, controlID in self.pkFightBackTimer.iteritems():
			if controlID == controllerID:
				self.cancel( controlID )
				self.pkFightBackTimer[eid] = 0
				self.removePKTarget( eid )

	def startPkAttackTimer( self ):
		"""
		����pk����״̬�ı�ʱ�������
		"""
		self.endPkAttackTimer()
		self.addPkFlag( csdefine.PK_STATE_ATTACK )
		self.pkAttackTimer = self.addTimer( Const.PK_STATE_ATTACK_TIME, 0, ECBExtend.PK_STATE_ATTACK_TIMER_CBID )

	def endPkAttackTimer( self ):
		"""
		����pk����״̬ʱ�������
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
		#120��ʱ�䵽������pk״̬
		self.endPkAttackTimer()
		self.onPkAttackChangeCheck()

	def onPkAttackChangeCheck( self ):
		"""
		pk����״̬���
		"""
		# ������Ҳ������pk����״̬
		# ��Pk����״̬�������״̬���ֹͣpkAttackTimer
		# ����Ҫô�ָ�������Ҫô����
		if self.level < csconst.PK_PROTECT_LEVEL: return
		if self.pkState == csdefine.PK_STATE_PROTECT:	# pk����״̬������󲻸ı�pk״̬ by����
			return
		if self.pkState == csdefine.PK_STATE_REDNAME or self.pkState == csdefine.PK_STATE_ORANGENAME:	# �����˺���״̬���׵���� ���Լ�������ж� by����
			return
		if self.goodnessValue == csconst.PK_GOODNESS_MAX_VALUE:
			self.addPkFlag( csdefine.PK_STATE_BLUENAME )
		else:
			self.addPkFlag( csdefine.PK_STATE_PEACE )

	def pkAttackStateCheck( self, entityID, isMalignant ):
		"""
		Define Method
		pk״̬��⣬�ж��Լ��Ƿ���Ҫ����pk����״̬
		@param    entityID				: �����Ķ���
		@type     entityID				: EntityID
		@param    isMalignant			: ���������Ƿ�Ϊ����
		@type     isMalignant			: BOOL
		"""
		if entityID == self.id: return
		# ���Ŀ���Ƿ����
		target = BigWorld.entities.get( entityID )
		if target is None: return

		if target.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY != 0: return

		# �д費����pk
		if self.isQieCuoTarget( entityID ): return
		if self.level < csconst.PK_PROTECT_LEVEL: return

		# ������ڵ�ͼ������Ҫ����PK
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )

		if spaceScript.isSpaceCalcPkValue:return

		# ����Լ����ǶԷ�PKģʽ������PK��Ŀ�꣬˫�����ֱ�Ϊ��ɫ
		if isMalignant  and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and not target.canPk( self ):
			self.addPKTarget( target.id )
			target.addPKTarget( self.id )

		# ����Լ��Ǻ���״̬�������빥��״̬ ������ж������� ����һЩ�������������pk״̬�ı� by����
		if self.pkState == csdefine.PK_STATE_REDNAME or self.pkState == csdefine.PK_STATE_ORANGENAME: return

		if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if target.pkState in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ATTACK, csdefine.PK_STATE_ORANGENAME ]:
				# �Ժ���״̬�͹���״̬����ͷ�����Ч����������ֺ���״̬
				return
			if not isMalignant and target.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ATTACK, csdefine.PK_STATE_ORANGENAME ]:
				# �Բ����ں���״̬�͹���״̬������ͷ�����Ч����������ֺ���״̬
				return

		self.startPkAttackTimer()				# ���������빥������״̬

	def calcPkValue( self, killer ):
		"""
		����pkֵ
		@param    killer: ���Ҹɵ�����
		@type     killer: RoleEntity
		"""
		if killer == None: return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if not killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return

		DEBUG_MSG( "%s(id = %i, pkState = %i ) kill %s( %i, pkState = %i ) " % ( killer.getName(), killer.id, killer.pkState, self.getName(), self.id, self.pkState ) )

		killer.increaseHomicideNum()		# �Է�ɱ�˴�������1�� �����Ƿ�����PKֵ ɱ�˺ͱ�ɱ����Ҫ��ͳ��
		self.deadNumber += 1				# �Լ�����������1��

		# ���ڰ���Ӷ�ս��Ӱ��PKֵ
		if self.tong_isInRobWar( killer.tong_dbID ):
			INFO_MSG( "Not add PK value. %s(%i) kill %s(%i) and in RobWar!" % ( killer.getName(), killer.id, self.getName(), self.id ) )
			return
		#����������ںͽ��ڹ�ϵ����ô��Ӱ��PKֵ
		if self.isDartRelation( killer ):
			INFO_MSG( "Not add PK value. %s(%i) kill %s(%i) and in DartWar!" % ( killer.getName(), killer.id, self.getName(), self.id ) )
			return

		# ����Լ��ǹ���״̬���ߺ���״̬��ɱ���߶�����������Ӱ��PKֵ
		if self.pkState in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ATTACK, csdefine.PK_STATE_ORANGENAME ]:
			INFO_MSG( " Not add PK value. %s(%i) kill redName player %s(%i)!" % ( killer.getName(), killer.id, self.getName(), self.id ) )
			return
		#��������ڹ����������ʱ��PKֵ�������ӣ����԰���������ȥ��
		#if not self.pkTargetList.has_key( killer.id ):
		#	return
		# pkֵ���ӵȼ������ by ����
		levelOffcent = ( killer.level - self.level ) / 10
		# ��10<=ɱ�˷��ȼ�-��ɱ���ȼ�<20��ɱ��ͨ���+7��ɱ����+14
		# ��20<=ɱ�˷��ȼ�-��ɱ���ȼ�<30��ɱ��ͨ���+8��ɱ����+16
		# ��30<=ɱ�˷��ȼ�-��ɱ���ȼ�<40��ɱ��ͨ���+9��ɱ����+18
		# ��40<=ɱ�˷��ȼ�-��ɱ���ȼ���ɱ��ͨ���+10��ɱ����+20
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
		# �Է�pkֵ���ӣ��ѶԷ������������
		self.base.addKillerFoe( killer.databaseID, killer.getName(), killer.base )

	def increaseHomicideNum( self ):
		"""
		Define method.
		ɱ����������Ŀǰ��������1
		"""
		self.homicideNumber += 1

	def canPk( self, entity ):
		"""
		�ж��Ƿ���pkһ��entity
		@param value: pkֵ
		@type  value: int
		"""
		if entity is None: return False

		# ������Լ����ܹ���
		if self.id == entity.id: return False

		# ����ͬһ��ͼ����PK
		if self.spaceID != entity.spaceID:
			return False

		# ��ɫ���ڵ�ͼ�Ƿ�����pk
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canPk:
			return False

		# ������ڷ���״̬��������pk
		if len( self.attrBuffs ) > 0:
			if VehicleHelper.isFlying( self ):	return False

		# 30����ұ���
		if self.pkState == csdefine.PK_STATE_PROTECT: return False

		# �ж��Ƿ�Ϊ����ǵĻ���Ŀ��ת�Ӹ�����
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			INFO_MSG( "PK taget is a pet in canPK function " )
			owner = entity.getOwner()
			if owner.etype == "MAILBOX" :
				return False
			entity = owner.entity

		# �ж��Ƿ������
		if not entity.utype == csdefine.ENTITY_TYPE_ROLE: return False

		# 30���Է���ҽ�ֹpk
		if entity.pkState == csdefine.PK_STATE_PROTECT: return False

		# �����Ա����PK
		if self.isTeamMember( entity ):
			return False

		 # ϵͳģʽ����
		if  self.sysPKMode:
			# ϵͳģʽΪ��ƽģʽ����PK
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_PEACE:
				return False

			# ��ս�����а���Ա����PK
			if self.tong_dbID != 0 and ( self.tong_dbID == entity.tong_dbID ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG:
				return False

			# ��Ӫս��������Ӫ��Ա����PK
			if self.getCamp() != 0 and ( self.getCamp() == entity.getCamp() ) and self.sysPKMode == csdefine.PK_CONTROL_PROTECT_CAMP:
				return False

			# ϵͳģʽΪ��ʱ��Ӫģʽ
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_TEMPORARY_FACTION :
				if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG and ( not RoleYiJieZhanChangInterface.canPk( self, entity ) ) :
					return False

			# ϵͳģʽΪ����ģʽ
			if self.sysPKMode == csdefine.PK_CONTROL_PROTECT_LEAGUE:
				if self.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) !=0 and self.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) == entity.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ):
					return False

			if self.sysPKMode in csdefine.SYS_PK_CONTOL_ACT:
				if self.sysPKMode == entity.sysPKMode:
					return False
		else:
			# ����ҵ�pkģʽ������ģʽ��ԭ�ƶ�ģʽ������entity���ǻƺ���
			if  self.pkMode == csdefine.PK_CONTROL_PROTECT_RIGHTFUL and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ]:
				return False

			# ����ҵ�pkģʽ������ģʽ����entity���ǻƺ���������Է�����ͬһ��Ӫ
			if self.pkMode == csdefine.PK_CONTROL_PROTECT_JUSTICE and entity.pkState not in [ csdefine.PK_STATE_REDNAME, csdefine.PK_STATE_ORANGENAME ] \
				and self.getCamp() == entity.getCamp():
				return False

		# �Է�����Ӹ���״̬�¿ɹ���
		if not self.actionSign( csdefine.ACTION_FORBID_PK ) and entity.isFollowing(): return True

		# ����ұ���ֹPK������Ҫpk��entity����ֹpk������ĳ���ڰ�ȫ����
		if self.actionSign( csdefine.ACTION_FORBID_PK ) or entity.actionSign( csdefine.ACTION_FORBID_PK ): return False

		return True

	def onPrisonContribute( self, srcEntity ):
		"""
		Expose method.
		��������
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
		��ͻ��˷��ͱ���BUFF֪ͨ
		"""
		if self.money < 10000:
			self.statusMessage( csstatus.TAKE_EXP_SAVE_MONEY_FAIL )
			return
		self.client.onSaveDoubleExpBuff()

	def onSaveDoubleExpBuff( self, srcEntity ):
		"""
		Expose method.
		����˫������BUFF
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
			# ����BUFF��ʣ��ʱ��
			buff[ "persistent" ] = int( buff[ "persistent" ] - time.time() )
			self.takeExpRecord[ "freezeBuff" ] = buff

			# ��¼��󶳽��ʱ��
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
		��������Buff
		"""
		buffs = self.findBuffsByBuffID( Const.JING_WU_SHI_KE_DANCE_BUFF )

		if len( buffs ) > 0:
			buff = self.getBuff( buffs[0] )
			if buff[ "persistent" ] <= 0:
				DEBUG_MSG( "saveDoubleExpBuff:persistent is 0." )
				return

			# ����BUFF��ʣ��ʱ��
			buff[ "persistent" ] = int( buff[ "persistent" ] - time.time() )
			self.danceRecord[ "freezeBuff" ] = buff

			# ��¼��󶳽��ʱ��
			self.danceRecord[ "freezeDanceDailyRecord" ].reset()
			self.removeBuff( buffs[0], [csdefine.BUFF_INTERRUPT_NONE] )

			h = int( buff[ "persistent" ] / ( 60 * 60 ) )
			m = int( ( buff[ "persistent" ] - ( h * 60 * 60 ) ) / 60 )
			s = int( ( buff[ "persistent" ] - ( h * 60 * 60 ) ) % 60 )
			self.statusMessage( csstatus.JING_WU_SHI_KE_BUFF_SAVE, h, m, s )
		else:
			self.statusMessage( csstatus.JING_WU_SHI_KE_NO_BUFF )

	"""
	GM ��Ϣ��ѯ
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
		ˢ�½���ʱ��
		"""
		now = BigWorld.time()
		benefitTime = now - self.calBenefitTime
		self.calBenefitTime = now
		self.benefitTime += benefitTime

	def canBenefit( self ):
		"""
		�Ƿ��ܹ���ȡ����
		"""
		self.updateBenefitTime()
		return self.benefitTime >= Const.BENIFIT_PERIOD

	def resetBenefitTime( self ):
		"""
		���ý�������
		"""
		self.benefitTime = 0.0
		self.client.onGetBenefitTime( self.benefitTime )

	def getRestBenefitTime( self ):
		"""
		��û�ʣ����ʱ����ܱ�����
		"""
		self.updateBenefitTime()
		return self.benefitTime - Const.BENIFIT_PERIOD

	def giveNewPlayerReward( self, lifeTime, rewardNum ):
		"""
		defined method
		����ʵʱ���ֽ��� by����
		"""
		if not self.wallow_getLucreRate(): # �������Ϊ0���򲻽���
			return

		rewardTimeList = g_onlineReward.getRewardTick( lifeTime )
		if rewardNum > len( rewardTimeList ):			# �������ȡ��������С�������������û�п���ȡ�Ľ���
			ERROR_MSG( "Can't get the %i newPlayerReward before right time" % rewardNum )
			return
		rewardTick = rewardTimeList[rewardNum-1]
		# ������(�����޷������������ʼ���ʽ�������)
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
		self.base.addRewardRecord( rewardTick )				# ֪ͨbase������ȡ��¼�����浽DB

		if rewardNum == g_onlineReward.getCount():			# ���ֽ�����ȡ�꣬�رս���
			self.client.onFixTimeReward( 0, 0, -1, 0, 0)
			return
		self.sendNextAwarderToClient( lifeTime, rewardNum, awarder.items[0].id )

	def sendNextAwarderToClient( self, lifeTime, rewardNum, lastItemID ):
		"""
		defined method
		��ȡ�´����ֽ������ݲ�֪ͨ�ͻ���
		"""
		nextRewardTick = g_onlineReward.rewardKeys()[ rewardNum ]
		nextAwarder = g_rewards.fetch( g_onlineReward.getRewardUid( nextRewardTick ), self )
		if nextAwarder is None:
			self.client.onFixTimeReward( 0, 0, -1, 0, 0 )#֪ͨ����ر�
		else:
			nextItem = random.choice( nextAwarder.items )	# �����һ��
			self.client.onFixTimeReward( nextRewardTick, nextItem.id, rewardNum, lifeTime, lastItemID )	# �ͻ�����ʾ

	def giveOldPlayerReward( self, rewardNum ):
		"""
		defined method
		ͨ��ֱ�Ӹ�������ʼ���ʽ�������ʵʱ���ֽ��� by����
		"""
		if not self.wallow_getLucreRate(): # �������Ϊ0���򲻽���
			return
		reason = 0
		param = 0
		lastReward = 0
		rewardNum += 1
		levelLimit = max( self.level/10, 3 )				# �õȼ�ÿ�����ȡ�����������
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
			upperOdd = random.random()	# ��Ʒ����
			if upperOdd < 0.1: upperRate = 3	# ��������
			exp = int( 3 * (rewardNum**0.5) * (self.level**1.4) * 10 ) * upperRate
			self.addExp( exp, csdefine.CHANGE_EXP_OLD_PLAYER_REWARD )
			reason = 1
			param = exp
		elif rewardTypeOdd <= 50:
			INFO_MSG( "give protential" )
			upperRate = 1
			upperOdd = random.random()	# ��Ʒ����
			if upperOdd < 0.1: upperRate = 3	# ��������
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
			selectedItem = random.choice( awarder.items )	# �����һ��
			reason = 3
			param = selectedItem.id
		if self.getLevel() > csconst.OLD_REWARD_LEVEL_LIM:
			self.statusMessage( csstatus.FIX_TIME_OLD_REWARD_LEVEL_LIM, csconst.OLD_REWARD_LEVEL_LIM+1 )
			self.client.onOldFixTimeReward( -1, 0, 0, 0 )
		else:
			self.client.onOldFixTimeReward( lastReward, rewardNum, reason, param )	# �ͻ�����ʾ���˷���������

	def giveKJReward( self, eType ):
		"""
		define method
		����ģ��������ÿƾٽ��� by ����
		"""
		blobItems = []
		awarder = g_rewards.fetch( csdefine.RCG_KJ, self )
		checkRes = self.checkItemsPlaceIntoNK_( awarder.items )
		if checkRes == csdefine.KITBAG_CAN_HOLD:
			for item in awarder.items:
				blobItems.append( ChatObjParser.dumpItem( item ) )	# ������Ʒ��Ϣ����
			awarder.award( self, csdefine.ADD_ITEM_REQUESTIEEXP )
		if eType == 3:
			self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "",  cschannel_msgs.BCT_KJXS_COMMENDATION %( self.getName() ), blobItems )
		if eType == 4:
			self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", cschannel_msgs.BCT_KJHS_COMMENDATION %( self.getName() ), blobItems )

	#-----------------------------------------------------------------------------------------------------
	# Ѳ�����  kb
	#-----------------------------------------------------------------------------------------------------
	def onPatrolToPointOver( self, command ):
		"""
		virtual method.
		����onPatrolToPointFinish()������ECBExtendģ���еĻص�����

		@param command: Ѳ�ߵ�һ�������õ����������
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
		���贫�ͳ���������� ��������
		"""
		DEBUG_MSG( "onFlyTeleportContinue >>>%i." % srcEntityID )
		if srcEntityID != self.id:
			return

		indexs = self.findBuffsByBuffID( 99010 )
		self.getBuff( indexs[0] )["skill"].continuePatrol( self )

	def closeVolatileInfo( self ):
		"""
		virtual method.
		�ر�������Ϣ���͹��ܡ�
		�������ģ��ᱻ��ͬ��entity���ã���ĳЩentity���ܻ���Ҫ�Բ�ͬ
		�ķ�ʽ��ʱ���ر������Ϊ���������ӿ�����������ء�
		"""
		# �������ش˽ӿڣ��������κ����飬���ڲ�ִ�йر�������Ϣ֪ͨ����Ϊ
		# ����ر�����һ�Ư�ƣ���Ϊ����ƶ�ʱ��û�б�֪ͨҪ��������Ϣ֪ͨ���ܡ�
		pass

	def openVolatileInfo( self ):
		"""
		virtual method.
		��������Ϣ���͹���
		�������ģ��ᱻ��ͬ��entity���ã���ĳЩentity���ܻ���Ҫ�Բ�ͬ
		�ķ�ʽ��ʱ���ر������Ϊ���������ӿ�����������ء�
		"""
		# ���ز����Ǵ˷����Ĺ��ܣ�ʹ֮������������н�����Ҳ����㲥���ݡ�
		pass

	#-----------------------------------------------------------------------------------------------------
	# ��������Ʒ�ص�
	#-----------------------------------------------------------------------------------------------------
	def resetLifeItems( self, onLine ):
		"""
		ˢ������������Ʒ
		onLineΪTrue��ʾ�������ˢ��
		onLineΪFalse��ʾ�������ˢ��
		"""
		uids = []
		deadTimes = []
		items = self.itemsBag.getDatas()
		for item in items:
			lifeType = item.getLifeType()
			if lifeType == ItemTypeEnum.CLTT_NONE: continue
			deadTime = item.getDeadTime()
			# ���߿�ʼ��ʱ�������жϸ���Ʒ�Ƿ��ѵ��ڣ����������ɾ����û���ڻָ���ʼ״̬��
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
		������ϵĽӿ����һ����Ʒ����������Ʒ������
		"""
		if item is None: return
		self.addLifeItemsToManage( [item.uid], [item.getDeadTime()] )

	def addLifeItemsToManage( self, uids, lifeTimes ):
		"""
		�����Ʒ����������
		"""
		BigWorld.globalData["LifeItemMgr"].addItems( self.base, uids, lifeTimes )

	def removeLifeItemsFromManage( self, uids, lifeTimes ):
		"""
		�Ƴ���Ʒ�ӹ�������
		"""
		BigWorld.globalData["LifeItemMgr"].removeItems( self.base, uids, lifeTimes )

	def onItemLifeOver( self, uid ):
		"""
		Define method.
		��������Ʒ�������ڵ���ص�
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
		�Ƴ����ڱ�־
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
			self.removeFlag( csdefine.ROLE_FLAG_CP_ROBBING )
		else:
			self.removeFlag( csdefine.ROLE_FLAG_XL_ROBBING )

	def onTeleportReady( self, srcEntityID, spaceID ):
		"""
		�ͻ��˵�ͼ�������
		Exposed method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if spaceID != self.spaceID:
			return

		spaceBase = self.getCurrentSpaceBase()

		# ���ΪNone��space�����Ѿ�����
		if spaceBase:
			spaceBase.cell.onTeleportReady( self.base )
		else:
			assert False, "spaceBase is None, data=[%s]" % BigWorld.getSpaceDataFirstForKey( self.spaceID, 1 ).split()

		if not self.isCurrSpaceCanFly() and VehicleHelper.isFlying( self ):
			# �ӿ��Է��еĿռ�����˲����Է��еĿռ䣬��Ϸ���buff
			self.removeBuffByBuffID( csdefine.FLYING_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

		if not self.isCurrSpaceCanVehicle():
			# �ӿ����ٻ����Ŀռ�����˲������ٻ����Ŀռ䣬������buff
			if VehicleHelper.isFlying( self ):
				self.removeBuffByBuffID( csdefine.FLYING_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )
			elif VehicleHelper.isOnLandVehicle( self ):
				self.removeBuffByBuffID( csdefine.VEHICLE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

		# CSOL-1561���ͺ����Ǳ��buff
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:
			self.removeAllBuffByBuffID( csconst.PROWL_BUFF_ID, [csdefine.BUFF_INTERRUPT_NONE] )

		self.destinyTransCheck()		# �����ֻظ������

	def doKLJDActivity( self, srcEntityID ):
		"""
		�ҵ���
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		g_KuaiLeJinDan.doKLJDActivity( self )

	def doSuperKLJDActivity( self, srcEntityID ):
		"""
		�����ҵ���
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		g_KuaiLeJinDan.doSuperKLJDActivity( self )

	def singleDance( self ):
		"""
		defined method
		��������
		Exposed method
		"""
		if self.actionSign( csdefine.ACTION_ALLOW_DANCE ):			# �жϽ�ɫ�Ƿ���������
			self.spellTarget( Const.JING_WU_SHI_KE_SINGLE_DANCE_SKILL, self.id )
			self.spellTarget( Const.JING_WU_SHI_KE_POINT_SKILL, self.id )
		self.changeState( csdefine.ENTITY_STATE_DANCE )				# ��������״̬

	def doubleDance( self ):
		"""
		defined method
		˫����
		"""
		if self.actionSign( csdefine.ACTION_ALLOW_DANCE ):			# �жϽ�ɫ�Ƿ���������
			self.spellTarget( Const.JING_WU_SHI_KE_DOUBLE_DANCE_SKILL, self.id )
			self.spellTarget( Const.JING_WU_SHI_KE_POINT_SKILL, self.id )
		self.changeState( csdefine.ENTITY_STATE_DOUBLE_DANCE )				# ����˫������״̬

	def teamDance( self ):
		"""
		���鼯������
		"""
		if not self.isInTeam():
			self.statusMessage( csstatus.JING_WU_SHI_KE_NO_TEAM )
		else:
			if not self.isTeamCaptain():
				self.statusMessage( csstatus.JING_WU_SHI_KE_TEAM_NOT_CAPTAIN )
				return

			allMemberInRange = self.getAllMemberInRange( Const.JING_WU_SHI_KE_TEAM_RANGE )	# �õ���Χ�����ж����Ա
			for teamMember in  allMemberInRange:
				state = teamMember.getState()
				# ������У������ж��鹲��
				if not (state == csdefine.ENTITY_STATE_FREE or state == csdefine.ENTITY_STATE_DANCE or state == csdefine.ENTITY_STATE_DOUBLE_DANCE) or VehicleHelper.getCurrVehicleID( teamMember ):
					continue
				if state == csdefine.ENTITY_STATE_DANCE or state == csdefine.ENTITY_STATE_DOUBLE_DANCE:
					teamMember.stopDance( teamMember.id )
				if teamMember.actionSign( csdefine.ACTION_ALLOW_DANCE ):
					teamMember.spellTarget( Const.JING_WU_SHI_KE_TEAM_DANCE_SKILL, teamMember.id )
					teamMember.spellTarget( Const.JING_WU_SHI_KE_POINT_SKILL, teamMember.id )
				EffectState_List = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP
				# ����ѣ�Ρ���˯״̬��������
				if teamMember.effect_state & EffectState_List != 0:
					teamMember.statusMessage( csstatus.JING_WU_SHI_KE_NOT_FREE )
					continue
				teamMember.changeState( csdefine.ENTITY_STATE_DANCE )

	def stopDance( self, srcEntityID ):
		"""
		ֹͣ����
		Exposed method
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		dancePartner = BigWorld.entities.get( self.dancePartnerID )
		if dancePartner:		# ����й�������
			self.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_DOUBLE_DANCE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			self.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_POINT_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			self.changeState( csdefine.ENTITY_STATE_FREE )
			dancePartner.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_DOUBLE_DANCE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			dancePartner.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_POINT_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
			dancePartner.changeState( csdefine.ENTITY_STATE_FREE )
			self.dancePartnerID = 0		# �����Ϊ��
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
		���ű��鶯��
		"""
		self.planesAllClients( "playFaceAction", ( face, ) )
		self.setTemp( "Temp_Face", face ) # �Ӹ���ǣ����ƿ����ظ�����ͬһ������

	def stopFaceAction( self, srcEntityId, face ) :
		"""
		ֹͣ���ű��鶯��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return
		self.curActionSkillID = 0
		self.planesAllClients( "stopFaceAction", ( face, ) )
		self.removeTemp("Temp_Face") # �Ӹ���ǣ����ƿ����ظ�����ͬһ������

	def sendRequestDance( self, target ):
		"""
		���빲��
		"""
		if not target.isReal() or self.distanceBB( target ) > 3:
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_TOO_FAR )
			return

		#if not self.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# �жϽ�ɫ�Ƿ���������
		#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
		#	return
		#if not target.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# �жϽ�ɫ�Ƿ���������
		#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
		#	return
		if ( self.getState() != csdefine.ENTITY_STATE_FREE ) and ( not (self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0) ):	# �жϽ�ɫ�Ƿ�Ϊ����״̬������״̬
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE )
			return
		if ( target.getState() != csdefine.ENTITY_STATE_FREE ) and ( not (target.getState() == csdefine.ENTITY_STATE_DANCE and target.dancePartnerID == 0) ):#�ж���������Ƿ�Ϊ����״̬������״̬
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE_TOO )
			return

		if self.getGender() == target.getGender():
			self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_DANCE_GENDER )
			return

		if self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0:	# �����ɫ������״̬����ֹͣ����
			self.stopDance( self.id )

		self.changeState( csdefine.ENTITY_STATE_REQUEST_DANCE )						# ��ɫ������������״̬
		self.requestDanceID = target.id										# ��ɫ��������
		target.client.receiveRequestDance( self.id )
		self.statusMessage( csstatus.JING_WU_SHI_KE_INVITE, target.getName() )

	def answerDanceRequest( self, srcEntityID, result, requestEntityID ):
		"""
		<Exposed/>
		�𸴹��������
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		requestEntity = BigWorld.entities.get( requestEntityID )
		if requestEntity:
			if result:	# ������ܹ���
				#if not self.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# �жϽ�ɫ�Ƿ���������
				#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
				#	return
				#if not requestEntity.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# �жϽ�ɫ�Ƿ���������
				#	self.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_RESTRICT )
				#	return
				if ( self.getState() != csdefine.ENTITY_STATE_FREE ) and ( not (self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0) ):	# �жϽ�ɫ�Ƿ�Ϊ����״̬������״̬
					self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE )
					return
				if not requestEntity.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:		# �ж���������Ƿ�Ϊ����״̬
					self.statusMessage( csstatus.JING_WU_SHI_KE_REQUEST_NOT_REQUEST_DANCE )
					return
				if self.distanceBB( requestEntity ) > 10:		# �������������뷽���������10
					self.statusMessage( csstatus.JING_WU_SHI_KE_ANSWER_TOO_FAR, requestEntity.playerName )
					requestEntity.changeState( csdefine.ENTITY_STATE_FREE )
					requestEntity.statusMessage( csstatus.JING_WU_SHI_KE_ANSWER_TOO_FAR, self.playerName )
					return
				if requestEntity.requestDanceID != self.id:		# ������뷽����Ķ������Լ�
					self.statusMessage( csstatus.JING_WU_SHI_KE_NOT_REQUST, requestEntity.playerName )
					return

				if self.getState() == csdefine.ENTITY_STATE_DANCE and self.dancePartnerID == 0:	# �����ɫ������״̬����ֹͣ����
					self.stopDance( self.id )

				self.position = requestEntity.position		# �ƶ������뷽��Ϊ�˲��Ź��趯��
				self.direction = requestEntity.direction
				self.doubleDance()
				if requestEntity.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:		# �ж���������Ƿ�Ϊ����״̬����Ϊ����״̬������������״̬�£��޷�ʹ�ü���
					requestEntity.changeState( csdefine.ENTITY_STATE_FREE )
				requestEntity.doubleDance()
				requestEntity.client.onStatusMessage( csstatus.JING_WU_SHI_KE_ACCEPT, "(\'%s\',)" % self.getName() )	# ���ӽ���������ʾ��hyw--2009.07.23��

				self.dancePartnerID = requestEntityID		# ��¼����ID
				requestEntity.dancePartnerID = self.id
			else:		# ��������ܹ���
				if requestEntity.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:
					requestEntity.changeState( csdefine.ENTITY_STATE_FREE )
				requestEntity.statusMessage( csstatus.JING_WU_SHI_KE_REFUSE_DANCE, self.playerName )

	def stopRequestDance( self, srcEntityID ):
		"""
		ȡ�����������
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		if self.getState() == csdefine.ENTITY_STATE_REQUEST_DANCE:
			requestDancer = BigWorld.entities.get( self.requestDanceID )
			if requestDancer:
				requestDancer.client.stopRequestDance()		# ֪ͨ������ģ�����ȡ����
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
		������Ϸ��¼
		"""
		self.roleRecord[key] = value
		if not hasattr( self, "base" ):
			WARNING_MSG("Role entity not has base!!")
			return
		self.base.saveRoleRecord( cPickle.dumps( { key:value }, 2 ) )


	def queryAccountRecord( self, key ):
		"""
		��ѯ��Ϸ��¼
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
		������Ϸ��¼
		"""
		self.accountRecord[key] = value
		self.base.saveAccountRecord( cPickle.dumps( {key: value}, 2 ) )


	def queryRoleRecord( self, key ):
		"""
		��ѯ��Ϸ��¼
		"""
		if not self.roleRecord.has_key( key ):
			return ""

		return self.roleRecord[key]

	def queryRoleRecordTime( self, key ):
		"""
		��ѯ��Ϸ��¼����
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
		����ˮ����¼
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
		�л���ǰ��
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
		�뿪�ڳ�
		"""
		if not self.vehicle:
			return
		self.actCounterDec( states )
		self.alightVehicle()
		self.client.onDisMountDart()
		self.planesAllClients( "disDartEntity", ( id, 0 ) )

	def selectSuanGuaZhanBu( self, srcEntityID ):
		"""
		ѡ������ռ��
		"""
		if srcEntityID != self.id:
			return

		# ��δ��뱾����FuncSuanGuaZhanBu�У������ƶ����ˣ��Է�ֹ�ٳ������磺CSOL-9799���������� mushuang
		if not self.suanGuaZhanBuDailyRecord.checklastTime():				# �ж��Ƿ�ͬһ��
			self.suanGuaZhanBuDailyRecord.reset()
		if self.suanGuaZhanBuDailyRecord.getDegree() >= 1:					# һ��ֻ����һ��
			self.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_LIMIT_NUM )
			return

		if self.payMoney( g_SuanGuaZhanBuLoader.getNeedMoney( self.level ), csdefine.CHANGE_MONEY_SUANGUAZHANBU ):		# ��ҿ۳���Ǯ
			self.suanGuaZhanBuDailyRecord.incrDegree()	# ����ռ��������1
			self.spellTarget( g_SuanGuaZhanBuLoader.getRandomSkill(), self.id )


	def hasActivityFlag( self, flag ):
		"""
		�Ƿ���ĳ���¼��־
		"""
		return self.activityFlags & ( 1 << flag )


	def setActivityFlag( self, flag ):
		"""
		define method
		����һ������
		"""
		self.activityFlags = self.activityFlags | ( 1 << flag)
		self.broadcastActFlagsToTeammates( flag )

	def removeActivityFlag( self, flag ):
		"""
		ȡ��һ������
		"""
		self.activityFlags = self.activityFlags &~ ( 1 << flag )
		self.broadcastActFlagsToTeammates( flag )

	def getMapping( self ):
		return self.persistentMapping

	def query( self, key, default = None ):
		"""
		���ݹؼ��ֲ�ѯmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻�defaultֵ
		"""
		try:
			return self.persistentMapping[key]
		except KeyError:
			return default

	def set( self, key, value ):
		"""
		define method
		��һ��key��дһ��ֵ

		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
		"""
		self.persistentMapping[key] = value

	def remove( self, key ):
		"""
		define method
		�Ƴ�һ����key���Ӧ��ֵ
		"""
		self.persistentMapping.pop( key, None )

	def addInt( self, key, value ):
		"""
		��һ��key���Ӧ��ֵ���һ��ֵ��
		ע�⣺�˷����������Դ��Ŀ���ֵ�Ƿ�ƥ�����ȷ
		"""
		v = self.queryInt( key )
		self.set( key, value + v )

	def queryInt( self, key ):
		"""
		���ݹؼ��ֲ�ѯmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻�0
		"""
		try:
			return self.persistentMapping[key]
		except KeyError:
			return 0

	def queryStr( self, key ):
		"""
		���ݹؼ��ֲ�ѯmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻ؿ��ַ���""
		"""
		try:
			return self.persistentMapping[key]
		except KeyError:
			return ""

	def getjkCardGiftResult( self, presentID):
		"""
		�����ȡ���ֿ�����
		"""
		item = g_items.createDynamicItem( presentID )
		# ���ж��ܷ���뱳��
		checkReult = self.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD :
			self.base.onGetjkCardGiftFailed()					#֪ͨ�������˴���ȡʧ��
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return
		self.addItem( item, csdefine.ADD_ITEM_TAKEJKCARDPRESENT )


	# ----------------------------------------------------------------
	# �µ������
	# ----------------------------------------------------------------
	def useVehicleItem( self, srcEntityID, uid ):
		"""
		Exposed Method
		ʹ�������Ʒ
		@param uid: ��ƷΨһID
		@type  uid:	int64
		@return None
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# �ж���Ʒ�Ƿ����
		item = self.getItemByUid_( uid )
		if item is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		# �ж��Ƿ��������Ʒ
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_VEHICLE:
			self.statusMessage( csstatus.VEHICLE_ITEM_LAWLESS )
			return

		# �ж�ʹ�õȼ�
		if self.level < item.getReqLevel():
			self.statusMessage( csstatus.VEHICLE_ITEM_LEVEL )
			return

		# �ж���Ʒ�Ƿ񶳽�
		if item.isFrozen():
			ERROR_MSG( "Item(%s, uid = %i, ownerName = %s, ownerDBID = %i) isFrozen!" % ( item.name(), item.uid, self.getName(), self.databaseID ) )
			return

		# ��Ʒ����
		item.freeze()
		# ֪ͨbase
		self.base.useVehicleItem( item )

	def onUseVehicleItemNotify( self, uid, state ):
		"""
		Define Method
		baseʹ�������Ʒ֪ͨ
		"""
		# �ж���Ʒ�Ƿ����
		item = self.getItemByUid_( uid )
		if item is None:
			ERROR_MSG( "Vehicle Item missed durning useing! playerName(%s), itemUID(%i)"%( self.playerName, uid ) )
			return

		# ��Ʒ����
		item.unfreeze()

		# ʹ�óɹ����Ƴ���Ʒ
		if state:
			self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_USEVEHICLEITEM )


	#ʹ��ת���������Ʒ
	def useTurnVehicleItem( self, srcEntityID, uid ):
		"""
		Exposed Method
		ʹ��ת���������Ʒ
		@param uid: ��ƷΨһID
		@type  uid:	int64
		@return None
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# �ж���Ʒ�Ƿ����
		item = self.getItemByUid_( uid )
		if item is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		# �ж��Ƿ���ת���������Ʒ
		if item.getType() != ItemTypeEnum.ITEM_VEHICLE_TURN:
			self.statusMessage( csstatus.VEHICLE_ITEM_LAWLESS )
			return

		# �ж�ʹ�õȼ�
		if self.level < item.getReqLevel():
			self.statusMessage( csstatus.VEHICLE_ITEM_LEVEL )
			return

		# �ж���Ʒ�Ƿ񶳽�
		if item.isFrozen():
			ERROR_MSG( "Item(%s, uid = %i, ownerName = %s, ownerDBID = %i) isFrozen!" % ( item.name(), item.uid, self.getName(), self.databaseID ) )
			return

		# ��Ʒ����
		item.freeze()
		# ֪ͨbase
		self.base.useTurnVehicleItem( item )

	def onUseTurnVehicleItemNotify( self, uid, state ):
		"""
		Define Method
		baseʹ��ת�������Ʒ֪ͨ
		"""
		# �ж���Ʒ�Ƿ����
		item = self.getItemByUid_( uid )
		if item is None:
			ERROR_MSG( "Vehicle Item missed durning useing! playerName(%s), itemUID(%i)"%( self.playerName, uid ) )
			return

		# ��Ʒ����
		item.unfreeze()

		# ʹ�óɹ����Ƴ���Ʒ
		if state:
			self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_VEHICLE_TO_ITEM )


	#����������
	def activateVehicle( self, vehicleData ):
		"""
		define method
		�������
		"""
		if vehicleData["level"] - self.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			self.statusMessage( csstatus.VEHICLE_LEVEL_TOO_HIGN )
			return
		if self.currAttrVehicleData["id"] == vehicleData["id"]:return
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		if self.queryTemp( "activateVehicleData", {} ) and self.intonating():return
		# ���Լ��ͷ�һ���������ļ���
		self.setTemp( "activateVehicleData", vehicleData )
		state = self.spellTarget( Const.VEHICLE_ACTIVATE_SKILLID, self.id )
		if state != csstatus.SKILL_GO_ON:
			self.popTemp( "activateVehicleData" )
			self.statusMessage( state )


	def onactivateVehicle( self, vehicleData ):
		"""
		�������ɹ�
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
		#�������
		if self.currVehicleData["type"] != csdefine.VEHICLE_TYPE_FLY and self.currVehicleData["id"] != vehicleData["id"]:
			self.conjureVehicle( vehicleData )

	def addA_VehicleFDTimmer( self ):
		"""
		��һ���������ı�����timmer
		"""
		if self.fd_aTimmerID:
			self.cancel( self.fd_aTimmerID )
		#���뱥���ȵĵ���ʱ�ж�
		disTime = self.currAttrVehicleData["fullDegree"] - int( time.time() )
		if disTime <= 0:
			disTime = 1
		if disTime > 7*24*3600:
			disTime = 7*24*3600
		self.fd_aTimmerID = self.addTimer( disTime, 0, ECBExtend.VEHICLE_ACTIVATE_FULLDEGREE_TIMMER_CBID )

	def onActivateVehicleFD( self,controllerID, userData ):
		"""
		�������豥ʳ�Ȼص�
		"""
		if self.currAttrVehicleData["fullDegree"] <= int( time.time() ):
			self.cancelActiveVehicle()

	def cancelActiveVehicle( self ):
		"""
		ȡ����ǰ��������
		"""
		if self.fd_aTimmerID:
			self.cancel( self.fd_aTimmerID )
		self.removeBuffByBuffID( Const.VEHICLE_ACTIVATE_BUFFID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def deactivateVehicle(self,srcEntityID ):
		"""
		ȡ���������
		Exposed Method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.cancelActiveVehicle()
		#����½�����ȡ�����
		if self.currVehicleData["type"] != csdefine.VEHICLE_TYPE_FLY :
			self.cancelConjureVehicle()

	def actAndConjureVehicle( self, vehicleData ):
		"""
		define method
		�������
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

	#�ٻ�������
	def conjureVehicle( self, vehicleData ):
		"""
		Define Method
		ͨ��ָ����id�ٻ����
		@param id: �����������ݵ�Ψһ��ʾ��
		@type  id:	UINT8
		@return None
		"""
		if self.queryTemp( "conjureVehicleData", {} ) and self.intonating():
			ERROR_MSG( "Already in conjuring process! playerName(%s)"%self.playerName   )
			return

		id = vehicleData["id"]
		type = vehicleData["type"]
		# �Ƿ����ٻ�
		state = VehicleHelper.canMount( self, id, type )
		if state != csstatus.SKILL_GO_ON:
			self.statusMessage( state )
			return

		# ���ԭ�����buff
		self.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		# ���Լ��ͷ�һ���ٻ����ļ���
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
		�ٻ����ɹ�
		"""
		# ע�������ΪPersistent���ԣ������buff reloadʱ����������������Իָ������״̬
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
		#�������Լӳ����
		if self.currAttrVehicleData["id"] != vehicleData["id"]:
			self.activateVehicle( vehicleData )


	def addC_VehicleFDTimmer(self):
		"""
		��һ���ٻ����ı�����timmer
		"""
		if self.fd_cTimmerID:
			self.cancel( self.fd_cTimmerID )
		#���뱥���ȵĵ���ʱ�ж�
		disTime = self.currVehicleData["fullDegree"] - int( time.time() )
		if disTime <= 0:
			disTime = 1
		if disTime > 7*24*3600:
			disTime = 7*24*3600
		self.fd_cTimmerID = self.addTimer( disTime, 0, ECBExtend.VEHICLE_CONJURE_FULLDEGREE_TIMMER_CBID )

	def onConjureVehicleFD( self,controllerID, userData ):
		"""
		�ٻ�����豥ʳ�Ȼص�
		"""
		if self.currVehicleData["fullDegree"] <= int( time.time() ):
			self.cancelConjureVehicle()

	def cancelConjureVehicle(self):
		"""
		ȡ����ǰ�ٻ������
		"""
		if self.fd_cTimmerID:
			self.cancel( self.fd_cTimmerID )
		for buffID in Const.VEHICLE_CONJURE_BUFFID:
			if len( self.findBuffsByBuffID( buffID ) ) > 0:
				self.removeBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				return


	#�����淨
	def transVehicle( self, id, exp ):
		"""
		define method
		���Լ���Ǳ�ܻ�ȡ���ľ���
		"""
		#��ǰ���������������Ƿ�����裬����һ������
		if self.currAttrVehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		#����Ѵ���ߵȼ�������Ҫ�ٴ���
		if exp <= 0:
			self.statusMessage( csstatus.VEHICLE_MAX_LEVEL )
			return
		#��ҵ�ǰǱ�ܵ��Ƿ�������������Ҫ�ľ���
		if not self.hasPotential( exp ):
			self.statusMessage( csstatus.VEHICLE_NO_ENOUGH_POTENTIAL )
			return
		#�жϴ�������ǲ��ǵ�ǰ��������
		if VehicleHelper.getCurrAttrVehicleID( self ) != id:
			self.statusMessage( csstatus.VEHICLE_NO_CURRENT_ACTIVATE )
			return
		#���ܸ������Լ�6������贫��
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
		��������ʹ�� �ɹ�
		"""
		if not self.hasPotential( exp ):
			self.statusMessage( csstatus.VEHICLE_NO_ENOUGH_POTENTIAL )
			return
		self.payPotential( exp, csdefine.CHANGE_POTENTIAL_TRANS )
		self.base.transAddVehicleExp( id, exp )

	def onVehiclePropertyNotify( self, id, level, strength, intellect, dexterity, corporeity, reason ):
		"""
		������ԣ���base�����ĸ��£����ݸ��� �����Ǵ������������������
		defined method
		"""
		#�ж�����ǲ��ǵ�ǰ��������
		if VehicleHelper.getCurrAttrVehicleID( self ) != id:
			return
		#ˢ��֮ǰ��ȥ��֮ǰ�����Լӳ�
		self.strength_value -= self.currAttrVehicleData["strength"]
		self.intellect_value -= self.currAttrVehicleData["intellect"]
		self.dexterity_value -=  self.currAttrVehicleData["dexterity"]
		self.corporeity_value -=  self.currAttrVehicleData["corporeity"]

		#����ˢ��
		self.currAttrVehicleData["level"]     = level
		self.currAttrVehicleData["strength"]  = strength
		self.currAttrVehicleData["intellect"] = intellect
		self.currAttrVehicleData["dexterity"] = dexterity
		self.currAttrVehicleData["corporeity"]= corporeity
		#���ؼ�����buff
		for idx, buff in enumerate( self.attrBuffs ):
			spell = buff["skill"]
			if spell.getBuffID() == Const.VEHICLE_ACTIVATE_BUFFID:
				spell.doReload( self, buff )
				break
		# ����������ֵ
		self.calcDynamicProperties()

	#�������
	def upStepVehicle( self, srcEntityID, mainID, oblationID, needItem ):
		"""
		exposed method
		�������
		"""
		if not self.hackVerify_( srcEntityID ) : return

		#�ж����״̬
		if self.state != csdefine.ENTITY_STATE_FREE:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STATE_ERROR )
			return

		#�ж������Ƿ���������
		if self.currAttrVehicleData["id"] != mainID: #�ж�������ǲ��ǵ�ǰ��������
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_NOACT )
			return
		if self.currVehicleData["id"] == mainID: #�ж�������ǲ��ǵ�ǰ��˵����
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_ISCONJURE )
			return

		#�жϼ����Ƿ���������
		if self.currAttrVehicleData["id"] == oblationID: #�жϼ����ǵ�ǰ��������
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ACT )
			return
		if self.currVehicleData["id"] == oblationID: #�жϼ����ǲ��ǵ�ǰ��˵����
			self.statusMessage( csstatus.VEHICLE_UPSTEP_OBLATION_ISCONJURE )
			return

		#����Ҫ��
		items = self.findItemsByIDFromNK( needItem )
		if len(items) <= 0:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NO_ITEM )
			return
		#��������
		order = items[0].getOrder()
		self.freezeItem_( order )
		self.setTemp( "VEHICLE_UP_STEP_ORDER", order )
		self.base.upStepVehicle( mainID, oblationID, needItem )

	def onUpStepVehicle( self ):
		"""
		define method
		���׳ɹ���ص�
		"""
		#����
		order = self.popTemp( "VEHICLE_UP_STEP_ORDER", -1 )
		# �Ƴ�����Ʒ
		self.removeItem_( order, 1, csdefine.DELETE_ITEM_UP_STEP )
		if order > 0:
			self.unfreezeItem_( order )


	#�������Ʒ
	def vehicleToItem( self, vehicleData, needItem ):
		"""
		define method
		�������Ʒ(����base)
		"""
		#------------------�жϱ�����λ-------------------
		orderIDs = self.getAllNormalKitbagFreeOrders()
		if len( orderIDs ) < 1 :
			self.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_NO_SPACE )
			return False
		#------------------�ж���û��ת���ĵ���------------
		itemID = U_DATA[ vehicleData["step"] ]["toItemNeedItem"]
		if needItem != itemID:
			return

		sitems = self.findItemsByIDFromNK( needItem )
		if len( sitems ) <= 0:
			return False

		#------------------ɾ��ת���ĵ���----------------
		if not self.removeItemTotal( needItem, 1, csdefine.DELETE_ITEM_VEHICLE_TO_ITEM ):
			return False

		#------------------�����µ���Ʒ-------------------
		newItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		if newItem is None: return False
		newItem.setAmount( 1 )
		vehicleData["exp"] = 0 #���ݲ߻���Ҫ������Ʒ����赱ǰ����ֵ��0
		#һЩ��Ҫ������������
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
		#֪ͨbase ɾ�����
		self.base.vehicleToItemSuc( vehicleData["id"] )


	#��������淨
	def addVehicleBuff( self, id, buff ):
		"""
		������buff
		defined method
		"""
		if self.currVehicleData is None:
			return
		self.currentVehicleBuffIndexs.append( buff["index"] )
		self.base.addVehicleBuff( id, buff )

	def retractVehicle( self, srcEntityID ):
		"""
		�ջ����, �����Ҫ������裬��ʹ�ô˽ӿ�
		Exposed Method
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

	def addVehicleSkPoint( self, id, skPoint ):
		"""
		������輼�ܵ�
		defined method
		"""
		self.base.addVehicleSkPoint( id, skPoint )

	def onVehicleSkPointNotify( self, id, skPoint ):
		"""
		��輼�ܵ����
		defined method
		"""
		if VehicleHelper.getCurrVehicleID( self ) != id: return
		self.currVehicleData["skPoint"] = skPoint

	def feedVehicle( self, id, srcItemID ):
		"""
		���ιʳ
		defined method
		"""
		fodders = g_vehicleExp.getFodderID( srcItemID )
		item = None
		for f in fodders:
			item = self.findItemFromNKCK_( f )
			if not item is None:
				break
		if item is None:
			# ����û�к��ʵĲ���
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return

		lifeTime = item.getLifeTime()
		self.base.addVehicleDeadTime( id, lifeTime )

		# �Ƴ�����Ʒ
		item.setAmount( item.getAmount() - 1, self, csdefine.DELETE_ITEM_FEEDVEHICLE )

	#��豥�������
	def onUpdateVehicleFullDegree( self, id, fullDegree ):
		"""
		Define Method
		��豥���ȸ���
		"""
		if VehicleHelper.getCurrVehicleID( self ) == id:
			self.currVehicleData["fullDegree"] = fullDegree
			self.addC_VehicleFDTimmer()
		if VehicleHelper.getCurrAttrVehicleID( self ) == id:
			self.currAttrVehicleData["fullDegree"] = fullDegree
			self.addA_VehicleFDTimmer()

	def canDomesticate(self):
		"""
		�ܷ�ιʳ������
		"""
		if self.state == csdefine.ENTITY_STATE_FREE:
			return True
		return False

	def domesticateVehicle( self, srcEntityID, id, needItemID, count ):
		"""
		exposed method
		�ͻ��˵���ιʳ��豥����
		"""
		if not self.hackVerify_( srcEntityID ) : return

		if not self.canDomesticate(): return

		items = self.findItemsByIDFromNK( needItemID )
		scount = 0
		fullDegree = 0
		for item in items:
			scount += item.getAmount()
			fullDegree = item.query( "fullDegree", 0 )
		#��������
		if scount < count:
			self.statusMessage( csstatus.VEHICLE_FEED_NEED )
			return
		# �Ƴ�����Ʒ
		self.removeItemTotal(  needItemID, count, csdefine.DELETE_ITEM_DOMESTICATEVEHICLE )
		self.base.addVehicleFullDegree( id, fullDegree*count )

	def addVehicleSkill( self, id, skillID ):
		"""
		���ѧϰ����
		"""
		self.base.addVehicleSkill( id, skillID )

	def onVehicleAddSkillNotify( self, id, skillID ):
		"""
		Define Method
		������Ӽ���֪ͨ
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
		��������
		"""
		self.base.updateVehicleSkill( id, oldSkillID, newSkillID )

	def onUpdateVehicleSkillNotify( self, id, oldSkillID, newSkillID ):
		"""
		Define Method
		�����¼���֪ͨ
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
		������
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
			HACK_MSG( "����ĳ���dbid��" )
			return
		if self.pcg_isPetBinded( dbid ):
			self.statusMessage( csstatus.PET_HAD_BEEN_BIND )
			return
		if price > csconst.ROLE_MONEY_UPPER_LIMIT:
			HACK_MSG( "���õİ�̯����۸���ߡ�" )
			return

		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :	# ���Ҫ��̯���۵ĳ����ڳ�ս�У����Ȼ���
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
	# �ȼ�������ͨ��Ʒ
	# ----------------------------------------------------------------
	def canGiveItem( self, itemID ):
		"""
		�ض���Ʒ���ض��ȼ����ơ�
		�ж�����Ƿ�����ͨһ����Ʒ���������ס���̯���ʼġ����ֿ��
		"""
		if itemID in g_levelResItems and self.level < csconst.SPECIFIC_ITEM_GIVE_LEVEL: return False
		return True

	def canVendInArea( self ):
		"""
		ָ�������ܷ��̯
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
		��Ҽ��۵㿨
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
		���۵㿨�ɹ�����ȡѺ��
		"""
		self.payMoney( csconst.SELL_POINT_CARD_YAJIN, csdefine.CHANGE_MONEY_POINT_CARD_YAJIN )

	def buyPointCard( self, srcEntityID, cardNo ):
		"""
		exposed method
		����㿨
		"""
		self.base.buyPointCard( cardNo, self.money )

	def onBuyPointCard( self, price ):
		"""
		����㿨�ص���
		�����Ƿ�ɹ�������ȡ���á�������ɹ��������黹��
		"""
		self.payMoney( price, csdefine.CHANGE_MONEY_POINT_CARD_YAJIN )


	def incRoleProcess( self ):
		"""
		���ӽ�ɫ����ֵ
		"""
		self.recordProcess += 1


	def startTS( self ):
		"""
		define method
		��ʼ����
		"""
		self.writeToDB()

	def stopTS( self ):
		"""
		define method
		��������
		"""
		pass


	def testTakeTishouItems( self, items ):
		"""
		define method
		�ж��ܷ��������������Ʒ
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
		ȡ�����۳���
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
		�����������ý�Ǯ
		"""
		self.gainMoney( money, csdefine.CHANGE_MONEY_RECEIVETS_MONEY )
		BigWorld.globalData["TiShouMgr"].onTiShouMoneyTaked( self.databaseID )


	def addTSFlag( self ):
		"""
		define method
		������������۱�־
		"""
		self.addFlag( csdefine.ROLE_FLAG_TISHOU )

	def removeTSFlag( self ):
		"""
		define method
		�Ƴ�������۱�־
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
	# �д�ϵͳ
	# ----------------------------------------------------------------
	def isQieCuoTarget( self, targetID ):
		"""
		�ж�Ŀ��ID�Ƿ��ǵ�ǰ�д�ID
		"""

		if VehicleHelper.isFlying( self ): return False # ����ڷɣ�һ����̸
		if self.qieCuoTargetID != targetID: return False
		if self.qieCuoState != csdefine.QIECUO_FIRE: return False
		return True

	def canQieCuo( self, target ):
		"""
		�ж��Ƿ���������Ŀ���д�
		"""
		if target is None: return False
		if not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return False
		if VehicleHelper.isFlying( self ):
			self.statusMessage( csstatus.CANT_QIECUO_WHEN_FLYING )
			return False

		if VehicleHelper.isFlying( target ):
			self.statusMessage( csstatus.CANT_QIECUO_WHEN_TARGET_FLYING )
			return False

		# �жϵ�ǰ��ͼ�ܷ��д�
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
		��������д�
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
		�ظ��д�����
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
		���뷽18���ӳ�ȡ���д�
		"""
		if self.qieCuoState == csdefine.QIECUO_INVITE:
			target = BigWorld.entities.get( self.qieCuoTargetID )
			if target is not None:
				target.statusMessage( csstatus.QIECUO_REFUSE, self.getName() )
			self.changeQieCuoState( csdefine.QIECUO_NONE )

	def inviteQieCuo( self ):
		"""
		�����д�
		"""
		msg = random.choice( csconst.QIECUO_REQUEST_SAY_MSGS )
		self.chat_handleMessage( csdefine.CHAT_CHANNEL_NEAR, "", msg, [] )
		self.planesAllClients( "onRequestQieCuo", ( self.qieCuoTargetID, ) )

	def beInviteQieCuo( self ):
		"""
		�������д�
		"""
		self.client.onReceivedQieCuo( self.qieCuoTargetID )

	def readyQieCuo( self ):
		"""
		׼���д�
		"""
		self.addTimer( 0.0, Const.QIECUO_NOTIFY_INTERVAL_TIME, ECBExtend.QIECUO_NOTIFY_CBID )

	def onQieCuoTimerNotify( self, controllerID, userData ):
		"""
		�д�1��timer֪ͨ
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
		��ʼ�д�
		"""
		self.statusMessage( csstatus.QIECUO_START )
		self.qieCuoTimer = self.addTimer( 0, Const.QIECUO_CHECK_INTERVAL_TIME, ECBExtend.QIECUO_CHECK_CBID )

	def onQieCuoTimerCheck( self, controllerID, userData ):
		"""
		�д�timer���,ÿ10����һ��
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
		�����д�
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
		�д�����Ƴ�����BUFF
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD: return
		buffIndexs = self.getBuffIndexsByEffectType( csdefine.SKILL_EFFECT_STATE_MALIGNANT )
		buffIndexs.reverse()
		for index in buffIndexs:
			self.removeBuff( index, [csdefine.BUFF_INTERRUPT_NONE] )

	def changeQieCuoState( self, state ):
		"""
		Define method
		�д�״̬�ı�
		"""
		if self.qieCuoState == state: return
		oldState = self.qieCuoState
		self.qieCuoState = state
		self.onQieCuoStateChange( oldState, state )

	def onQieCuoStateChange( self, oldState, newState ):
		"""
		�д�״̬�ı�
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
		�ı��д�ID
		"""
		if self.qieCuoTargetID == targetID: return
		self.qieCuoTargetID = targetID
		target = BigWorld.entities.get( targetID )

	def loseQieCuo( self ):
		"""
		�д��������ʤ����
		"""
		target = BigWorld.entities.get( self.qieCuoTargetID )
		if target is None: return

		# ���Լ���Ŀ�꼰������޵�Buff
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
		������¼ͳ��
		"""
		g_Statistic.refreshDayStat( self )	# ������¼֮ǰˢ��һ��

		record = self.statistic.get( recordType, 0 )		# ��ȡĳ���¼����
		if record == 0:
			self.statistic[recordType] = 1
		else:
			self.statistic[recordType] = record + 1

	def getStatistic( self, srcEntityID ):
		"""
		<Exposed/>
		��ȡ���ͳ������
		"""
		if srcEntityID != self.id: return
		sendStat = self.statistic.copy()	# ��ȡ��¼��ͳ��
		sendStat[cschannel_msgs.SHUIJING_INFO_1] = self.queryRoleRecordTime( "shuijing_record" )
		sendStat[cschannel_msgs.TIAN_GUAN_MONSTER_DEF_2] = self.queryRoleRecordTime( "tianguan_record" )
		sendStat[cschannel_msgs.YA_YU_VOICE18] = self.queryRoleRecordTime( "yayu_record" )
		self.client.receiveStatistic( sendStat )

	def onRobotVerifyResult( self, statusID ):
		"""
		Define method.
		�������֤���������statusID��������ͷ�
		"""
		#DEBUG_MSG( "--->>>player( %s ), result( %i )" % ( self.getName(), statusID ) )
		self.statusMessage( statusID )
		if statusID == csstatus.ANTI_ROBOT_FIGHT_VERIFY_ERROR:		# ������
			self.prisonHunt()
		elif statusID == csstatus.ANTI_ROBOT_FIGHT_VERIFY_RIGHT:	# ������
			# ����������Ǳ�ܽ���
			if random.random() < 0.5:
				self.addExp( 497+100*( self.level**1.2 ), csdefine.CHANGE_EXP_ROBOT_VERIFY_RIGHT )
			else:
				self.addPotential( self.level*100, csdefine.CHANGE_POTENTIAL_ROBOT_VERIFY )

	def enterAutoFight( self, srcEntityID ):
		"""
		Exposed method.
		�����Զ�ս��
		"""
		if srcEntityID != self.id:
			return
		self.addFlag( csdefine.ROLE_FLAG_AUTO_FIGHT )

	def leaveAutoFight( self, srcEntityID ):
		"""
		Exposed method.
		�뿪�Զ�ս��
		"""
		if srcEntityID != self.id:
			return
		self.removeFlag( csdefine.ROLE_FLAG_AUTO_FIGHT )

	def isInAutoFight( self ):
		"""
		�Ƿ����Զ�ս����
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_AUTO_FIGHT )

	def openAutoFight( self, srcEntityID ):
		"""
		�����Զ�ս������
		"""
		if srcEntityID != self.id:
			return
		self.hasAutoFight = True	# ��ʾ�Զ�ս�������Ѿ�����

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

		# ��������������򷵻�
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
		����ROLL
		"""
		if not self.hackVerify_( srcEntityID ) : return

		dropBox = BigWorld.entities.get( dropBoxID )
		if dropBox:
			dropBox.abandonRoll( self.id, index )



	def addOwnCollectionItem( self, srcEntityID, ownCollectionItem ):
		"""
		Exposed method
		���������չ���Ʒ
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
		�Ƴ�һ�������չ���Ʒ
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
		��ѯ�����չ���Ʒ
		"""
		player = BigWorld.entities.get( srcEntityID )
		if player:
			for i in self.collectionBag:
				player.client.onQueryOwnCollectionItem( i, self.id )


	def sellOwnCollectionItem( self, sellerID, ownCollectionItem ):
		"""
		Exposed method
		�����չ���Ʒ
		ע�⣺����� sellerID ��ʵ�� srcEntityID
		"""
		#if not self.hackVerify_( srcEntityID ): return
		if sellerID == self.id:
			self.statusMessage( csstatus.COLLECT_ITEM_FORBID_YOURSELF_ITEM )
			return
		seller = BigWorld.entities.get( sellerID, None )
		if seller is None:
			return
		# ��������������򷵻�
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
		������Ƹı�
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
		���Ӱ�Ὰ������
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
		���ٰ�Ὰ������
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
		����������
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
		����������
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
		������
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
		���Ӹ��˾�������
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
		���ٸ��˾�������
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
		������Ӿ������ֻ���
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
		������Ӿ������ֻ���
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
		�þ���һ�Ǳ��
		"""
		expVal = potVal * csconst.ROLE_EXP2POT_MULTIPLE
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return
		if potVal <= 0: # ��Ȼ���������ƣ�������������Ӧ����һ��
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
		count = oldCollectionItem.collectAmount - oldCollectionItem.collectedAmount				#������Ʒ��Ϣ��ֻ���¼۸�����Ҫ�Է��������ο�

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
		֪ͨ��ȡ�չ�Ѻ��
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
		���ڹ�����Ҷ���ĳ�������Ľ������ by ����
		"""
		if self.query( spaceKey, 0 ) == spaceID:
			return
		self.set( spaceKey, spaceID )
		g_activityRecordMgr.add( self, activityType )

	def addActivityCount( self, activityType ):
		"""
		��Ӽ�¼
		"""
		g_activityRecordMgr.add( self, activityType )

	def removeActivityRecord( self, activityType ):
		"""
		�Ƴ����¼
		"""
		g_activityRecordMgr.remove( self, activityType )

	def isActivityCanNotJoin( self, activityType ):
		"""
		�������״̬����Ҫ�ǿ��Բ��� �� ���ɲ��� ����״̬��
		"""
		return g_activityRecordMgr.queryActivityJoinState( self, activityType ) == csdefine.ACTIVITY_CAN_NOT_JOIN


	def onAbandonDartQuestCBID( self, controllerID, userData ):
		"""
		�ص��ķ�ʽ������������
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
		�������ڹ㲥��������Ϣ�ӿ� by ����
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
		�������ڹ㲥�ɹ���������Ϣ�ӿ� by ����
		������Ľӿ���factionID�Ļ�ȡ��ʽ��������ͬ��������Ҫ����
		"""
		killerDartName = Const.DARKOFFICE_NAME[75 - factionID]
		targetDartName = Const.DARKOFFICE_NAME[factionID]
		msg = g_cueItem.getDartCueMsg( specialMsgMap["BCT_ROBSUCCESS_NOTIFY"] )
		msg = g_cueItem.getCueMsgString( _keyMsg = msg, _p = self.getName(), _b = killerDartName, _o = targetDartName )
		self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, [] )


	#------------------ItemAwards ��ȡ��Ʒ����
	def awardItem( self, itemList ):
		"""
		@define method
		��ȡ��Ʒ
		"""
		itemInstances = []
		for id,amount in itemList:
			item = g_items.createDynamicItem( int( id ))
			iAmount = int(amount)
			stackable = item.getStackable()
			if iAmount > 0 and iAmount <= stackable:		# ������õ�����С�ڸ���Ʒ�ɵ�������
				item.setAmount( iAmount )		# ��ô��������
				itemInstances.append( item )
			elif iAmount > stackable:
				itemInstances.extend( [ g_items.createDynamicItem( item.id, stackable ) for a in xrange(0, iAmount/stackable)] )
				m_amount = iAmount%stackable
				if m_amount > 0:
					itemInstances.append(  g_items.createDynamicItem( item.id, m_amount ) )
		# ���ж��ܷ���뱳��
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
		���ڴ���һЩ������Ϊ�Ľ����ص�
		"""
		BigWorld.globalData["MessyMgr"].onMessyOver( messyID, self.databaseID )


	def onRoleRecordInitFinish( self ):
		"""
		��ɫ��Ϣ��roleRecord����ʼ����ϵĵ��á�
		������ú󣬻���ɫ����һ����־λ csdefine.ACTIVITY_FLAGS_INIT_OVER
		��������־λû�б����ã�����ع��ܽ�����ͣʹ�á�
		"""
		self.addFlag( csdefine.ROLE_FLAG_ROLE_RECORD_INIT_OVER )
		g_activityRecordMgr.initAllActivitysJoinState( self )


	def onAccountRecordInitFinish( self ):
		"""
		��ɫ��Ϣ��roleRecord����ʼ����ϵĵ��á�
		������ú󣬻���ɫ����һ����־λ csdefine.ACTIVITY_FLAGS_INIT_OVER
		��������־λû�б����ã�����ع��ܽ�����ͣʹ�á�
		"""
		self.setActivityFlag( csdefine.ROLE_FLAG_ACCOUNT_RECORD_INIT_OVER )

	def sendLoveMsg( self, receiverName, msg, isAnonymity, isSendMail ):
		"""
		define method
		�ǳ����ţ����͸����Ϣ
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
	# ��������
	# ----------------------------------------------------------------
	def pickFruit( self, srcEntityID, targetID ):
		"""
		Exposed Method
		�ɼ�������ʵ
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		target = BigWorld.entities.get( targetID )
		if target is None: return
		if target.isDestroyed: return
		# �ж�����
		if not target.isEntityType( csdefine.ENTITY_TYPE_FRUITTREE ): return
		# �жϾ���
		distance = self.position.distTo( target.position )
		if distance > csconst.FRUIT_PICK_DISTANCE: return
		# �ж��Ƿ����
		if not target.isRipe:
			self.statusMessage( csstatus.FRUIT_NOT_RIPE )
			return
		# �ж��Ƿ����Լ���ֲ
		if self.getName() != target.planterName:
			self.statusMessage( csstatus.FRUIT_NOT_YOU )
			return
		# �ж����״̬
		if self.state == csdefine.ENTITY_STATE_FIGHT:
			self.statusMessage( csstatus.FRUIT_NOT_PICK )
			return
		# �ж��Ƿ񱻲ɼ�
		if target.pickerDBID !=0:
			self.statusMessage( csstatus.FRUIT_IS_PICK )
			return

		# �ɼ�Ʒ
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

		# ���ж��ܷ���뱳��
		checkReult = self.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD:
			self.statusMessage( csstatus.FRUIT_CANT_HOLD )
			return

		self.addItem( item, reason = csdefine.ADD_ITEM_FRUIT_TREE )

		target.onPick( self.databaseID )


	# ----------------------------------------------------------------
	# װ�����Գ�ȡ
	# ----------------------------------------------------------------
	def equipExtract( self, srcEntityID, uids ):
		"""
		Exposed Method
		װ����ȡ����
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		if self.iskitbagsLocked():
			#��ʾ �����Ѿ�����
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return
		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#������ϻ��ʹ�ô���
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return

		itemList = [ self.getItemByUid_( uid ) for uid in uids ]
		if len( itemList ) == 0:
			# ������ȡ���Ե�װ��
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_EQUIP )
			return

		equips = []					# ��¼Ҫ��ȡ��װ��
		needItems = []				# ��¼����ʯ
		needSuperItems = []			# ��¼��������ʯ
		excItems = []				# ��¼������

		for item in itemList:
			if item.isFrozen():
				# ��Ʒ������ �޷���ȡ
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

		# �����Ҫ��ȡ��װ��
		if len( equips ) == 0:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_EQUIP )
			return

		# ֻ�ܷ���һ��װ��
		if len( equips ) > 1:
			self.statusMessage( csstatus.EQUIP_EXTRACT_ONE_EQUIP )
			return

		equip = equips[0]
		# ֻ�ܷ���10�����ϵ�װ��
		level = equip.getLevel()
		if level < csconst.EQUIP_EXTRACT_LEVEL_MIN:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_LEVEL )
			return

		# ֻ�ܷ�����ɫ����Ʒ�ʵ�װ��
		quality = equip.getQuality()
		if quality not in csconst.EQUIP_EXTRACT_QUALITYS:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_QUALITY )
			return

		# װ��û�������ܱ���ȡ �����ע���Եĳ�ȡ by wuxo csol-1055
		extractEffect = [] #���Գ�ȡ�������б�
		poureEffect = equip.getPouredCreateEffect()
		disCount = len( equip.getCreateEffect() ) - len( poureEffect )
		eqExtraEffect = dict( equip.getExtraEffect() )
		extractEffect = copy.deepcopy( poureEffect )
		for attrE,attrV in eqExtraEffect.iteritems():
			extractEffect.append( (attrE, attrV ) )
		if len( extractEffect ) == 0:
			self.statusMessage( csstatus.EQUIP_EXTRACT_NO_EFFECT )
			return

		# �ж��õ��Ƿ���ʯ���ǳ�������ʯ
		if len( needItems ):
			if len( needSuperItems ):
				# 2�ַ���ʯ����ͬʱʹ��
				self.statusMessage( csstatus.EQUIP_EXTRACT_NO_USE )
				return

			# ��Ǯ = װ���ȼ�^2*װ��Ʒ��*2^ʯͷƷ��*2*�����ʯͷ����
			equipLevel = equip.getLevel()
			equipQuality = equip.getQuality()
			itemQuality = needItems[0].getQuality()
			itemAmount = len( needItems ) if len( needItems ) <= len( extractEffect ) else len( extractEffect )
			money = ( equipLevel ** 2 ) * equipQuality * ( 2 ** itemQuality ) * 2 * itemAmount
			if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIP_EXTRACT ):
				self.statusMessage( csstatus.EQUIP_EXTRACT_NO_MONEY )
				return

			# ʹ�÷���ʯ
			odds = csconst.EQUIP_EXTRACT_ITEM_ODDS
			# �ж��Ƿ���������
			if len( excItems ) != 0:
				odds += csconst.EQUIP_EXTRACT_EXCITEM_ODDS
			if random.random() > odds:
				# װ����ȡʧ��
				self.statusMessage( csstatus.EQUIP_EXTRACT_FIALD )
				# ����װ���ɳ�ȡ���������Ƴ�����ʯ�����¶����
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
				# ��������ʯ���߳�������ʯ
				self.statusMessage( csstatus.EQUIP_EXTRACT_NEED_ITEM )
				return

			# ��Ǯ = װ���ȼ�^2*װ��Ʒ��*2^ʯͷƷ��*2*�����ʯͷ����
			equipLevel = equip.getLevel()
			equipQuality = equip.getQuality()
			itemQuality = needSuperItems[0].getQuality()
			itemAmount = len( needSuperItems ) if len( needSuperItems ) <= len( extractEffect ) else len( extractEffect )
			money = ( equipLevel ** 2 ) * equipQuality * ( 2 ** itemQuality ) * 2 * itemAmount
			if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIP_EXTRACT ):
				self.statusMessage( csstatus.EQUIP_EXTRACT_NO_MONEY )
				return

			# ʹ�ó�������ʯ
			odds = csconst.EQUIP_EXTRACT_SUITEMS_ODDs
			# �ж��Ƿ���������
			if len( excItems ) != 0:
				odds += csconst.EQUIP_EXTRACT_EXCITEM_ODDS
			if random.random() > odds:
				# װ����ȡʧ��
				self.statusMessage( csstatus.EQUIP_EXTRACT_FIALD )
				# ����װ���ɳ�ȡ���������Ƴ���������ʯ�����¶����
				if len( extractEffect ) >= len( needSuperItems ):
					for item in needSuperItems:
						self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				else:
					for i in xrange( len( extractEffect ) ):
						item = needSuperItems[ i ]
						self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
				return

			extraCount = 0 #��ȡ�������Ե�����
			poureCount = 0 #��ȡ��ע���Ե�����
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


			# ��������������ٶ�eqExtraEffectȫ������ȡ������װ������Ȼ�й�ע���Դ��ڣ����װ������ʧ��
			# ���Ǵ�ʱ����Ʒ��Ϣ�Ͳ�����µ��ͻ��ˣ�������ݲ�һ��
			# ��������ǣ������ӵ�һ��if�����ó���
			# updated by mushuang
			newEquip = equip.copy()
			self.removeItemByUid_( equip.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
			newEquip.set( "eq_extraEffect", eqExtraEffect, self )
			if len( eqExtraEffect )!= 0 or len( poureEffect ) != 0:
				createEffect = [ ( 0, 0 ) ]*( extraCount + disCount)
				createEffect.extend( poureEffect )
				newEquip.setCreateEffect( createEffect, self )
				# ����ɾ������ǰ׺���򵥵������ܻ��и��ָ��������⣬
				# װ��ϵͳ�仯�ܿ죬һ�����ز����ò��˶�þ��п���
				# ���¹��ܷ�����ͻ��Ȼ����Ҫ�������ء���Ȼװ���Ѿ�
				# ������ԭ�й���Ҫǰ׺Ҳû���ã�
				newEquip.removeAllPrefix( self )
				# Ϊ��֪ͨװ����ȡ��������
				self.addItemByOrderAndNotify_( newEquip, self.getNormalKitbagFreeOrder(), csdefine.DELETE_ITEM_EQUIP_EXTRACT )

			for item in excItems:
				self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_EQUIP_EXTRACT )
		#���ϻ������1
		useDegree -= 1
		kitCasketItem.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )

		self.statusMessage( csstatus.EQUIP_EXTRACT_SUCCESS )


	# ----------------------------------------------------------------
	# װ�����Թ�ע
	# ----------------------------------------------------------------
	def equipPour( self, srcEntityID, uids ):
		"""
		Exposed Method
		װ�����Թ�ע����
		"""
		if srcEntityID != self.id:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		if self.iskitbagsLocked():
			#��ʾ �����Ѿ�����
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#������ϻ��ʹ�ô���
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return

		itemList = [ self.getItemByUid_( uid ) for uid in uids ]
		if len( itemList ) == 0:
			# �����Ҫ��ע���Ե�װ��
			self.statusMessage( csstatus.EQUIP_POUR_NEED_EQUIP )
			return

		equips = []					# ��¼Ҫ��ȡ��װ��
		needItems = []				# ��¼��������

		for item in itemList:
			if item.isFrozen():
				# ��Ʒ������ �޷���ȡ
				self.statusMessage( csstatus.EQUIP_POUR_ISFROZEN )
				return
			if item.isEquip():
				equips.append( item )
			elif item.id == csconst.EQUIP_EXTRACT_PROITEM:
				needItems.append( item )

		# �����Ҫ��ע���Ե�װ��
		if len( equips ) == 0:
			self.statusMessage( csstatus.EQUIP_POUR_NEED_EQUIP )
			return

		# ֻ�ܷ���һ��װ��
		if len( equips ) > 1:
			self.statusMessage( csstatus.EQUIP_POUR_ONE_EQUIP )
			return

		# �������������
		if len( needItems ) == 0:
			self.statusMessage( csstatus.EQUIP_POUR_NO_USEITEM )
			return

		# һ��ֻ�ܷ���һ����������
		if len( needItems ) > 1:
			self.statusMessage( csstatus.EQUIP_POUR_ONE_USEITEM )
			return

		equip = equips[0]
		# ֻ�ܷ���10�����ϵ�װ��
		equipLevel = equip.getLevel()
		if equipLevel < csconst.EQUIP_EXTRACT_LEVEL_MIN:
			self.statusMessage( csstatus.EQUIP_POUR_NEED_LEVEL )
			return

		# ֻ�ܷ�����ɫ����Ʒ�ʵ�װ��
		quality = equip.getQuality()
		if quality not in csconst.EQUIP_EXTRACT_QUALITYS:
			self.statusMessage( csstatus.EQUIP_POUR_NEED_QUALITY )
			return

		# װ�����Կ�λ����
		emptyIndex = -1
		createEffect = equip.getCreateEffect()
		for index, data in enumerate( createEffect ):
			if data[0] != 0: continue
			emptyIndex = index
		if emptyIndex == -1:
			self.statusMessage( csstatus.EQUIP_POUR_NO_EFFECT )
			return

		needItem = needItems[0]
		# �����Ե���������
		bjEffect = needItem.getBjExtraEffect()
		if len( bjEffect ) == 0:
			self.statusMessage( csstatus.EQUIP_POUR_NO_USE )
			return

		# ��������ĵȼ���װ���ȼ�����
		level = needItem.getLevel()
		if level > equipLevel:
			self.statusMessage( csstatus.EQUIP_POUR_USE_LEVEL )
			return

		# ����ͬ����(�����������ԣ��ѹ�ע���ԣ�����װ����)���ܹ�ע
		#һ��װ������ͬ�ĸ������Բ��ܳ���2���� by csol-1055
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


		# ������ֻ�ܹ�ע����Ӧ��װ����λ
		wieldType = needItem.query( "bj_slotLocation", [] )
		equipType = equip.getType()
		if equipType not in wieldType:
			self.statusMessage( csstatus.EQUIP_POUR_ON_WIELDTYPE )
			return

		# ��Ǯ=װ���ȼ�^2*װ��Ʒ��^2* 10
		money = equipLevel ** 2 * quality ** 2 * 10
		if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIP_POUR ):
			self.statusMessage( csstatus.EQUIP_POUR_NO_MONEY )
			return

		newEquip = equip.copy()
		self.removeItemByUid_( equip.uid, reason = csdefine.DELETE_ITEM_EQUIP_POUR )
		if needItem.isBinded(): newEquip.setBindType( ItemTypeEnum.CBT_HAND, self )

		createEffect[emptyIndex] = effect
		newEquip.setCreateEffect( createEffect, self )


		# ����ɾ������ǰ׺���򵥵������ܻ��и��ָ��������⣬
		# װ��ϵͳ�仯�ܿ죬һ�����ز����ò��˶�þ��п���
		# ���¹��ܷ�����ͻ��Ȼ����Ҫ�������ء���Ȼװ���Ѿ�
		# ������ԭ�й���Ҫǰ׺Ҳû���ã�
		newEquip.removeAllPrefix( self )

		# Ϊ��֪ͨװ����ע��������
		self.addItemByOrderAndNotify_( newEquip, self.getNormalKitbagFreeOrder(), csdefine.DELETE_ITEM_EQUIP_POUR )
		self.removeItemByUid_( needItem.uid, reason = csdefine.DELETE_ITEM_EQUIP_POUR )
		#���ϻ������1
		useDegree -= 1
		kitCasketItem.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )

		self.statusMessage( csstatus.EQUIP_POUR_SUCCESS )

	# ----------------------------------------------------------------
	# װ������ by mushuang
	# ----------------------------------------------------------------
	def EquipUp( self, srcEntityId, equipUid, jadeUid ):
		"""
		װ������cell���룬exposed
		@equipId(int):����װ����uid
		@jadeId(int):���������uid
		"""
		if not self.hackVerify_( srcEntityId ) : return

		equip = self.getItemByUid_( equipUid )
		if equip is None :
			# ֪ͨ�ͻ��ˣ����û�и���Ʒ
			self.statusMessage( csstatus.KIT_EQUIP_INVALID )
			return

		jade = self.getItemByUid_( jadeUid )
		if jade is None:
			# ֪ͨ�ͻ��ˣ����û�и���Ʒ
			self.statusMessage( csstatus.KIT_EQUIP_INVALID )
			return

		# if ����������
		if self.iskitbagsLocked():
			#��ʾ �����Ѿ�����
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		# if ��Ʒ�Ѿ����᣺
		if equip.isFrozen():
			# ��ʾ ��Ʒ�Ѿ�����
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			# return
			return

		equiplevel = equip.getLevel()
		# ����ָ����װ����������Ʒ
		if equiplevel < csconst.EQUIP_UP_BASE_LEVEL:
			self.statusMessage( csstatus.KIT_EQUIP_UP_LEVEL_TOO_LOW )
			return

		quality = equip.getQuality()
		# �Ƿ�ɫװ����������Ʒ
		if quality != ItemTypeEnum.CQT_PINK:
			self.statusMessage( csstatus.KIT_EQUIP_UP_QUALITY_TOO_LOW )
			return

		needItemID = jadeData.get( equiplevel )

		if jade.id != needItemID:
			# ֪ͨ��ң���������ȼ�����
			self.statusMessage( csstatus.KIT_EQUIP_UP_JADE_INVALID )
			return

		#������Ҫ�Ľ�Ǯ�����۷����ɹ���񶼲��᷵����Ǯ
		payment = equiplevel ** 2.1 * 4 ** 3.5

		if not self.payMoney( payment, csdefine.CHANGE_MONEY_EQUIP_UP ):
			# ֪ͨ��ҽ�Ǯ����
			self.statusMessage( csstatus.KIT_EQUIP_UP_LOW_FUND )
			return

		if random.random() > csconst.EQUIP_UP_RATE : # �̶������ɹ���90%
			#��Ʒ���ԣ���������û��
			self.removeItemByUid_( jadeUid, reason = csdefine.DELETE_ITEM_EQUIP_UP )
			#��ʾ�����Ʒʧ��
			self.statusMessage( csstatus.KIT_EQUIP_UP_FAILED )
			return

		# ����ɾ������ǰ׺���򵥵������ܻ��и��ָ��������⣬
		# װ��ϵͳ�仯�ܿ죬һ�����ز����ò��˶�þ��п���
		# ���¹��ܷ�����ͻ��Ȼ����Ҫ�������ء���Ȼװ���Ѿ�
		# ������ԭ�й���Ҫǰ׺Ҳû���ã�
		equip.removeAllPrefix( self )

		# �����趨��������Ʒ�ʱ��ʣ���Ϊ��װ�Ļ������Ա�������װ������
		rnd = random.random()
		exp = EquipQualityExp.instance()
		baseQualityRate = 0.0
		if rnd < BaseQualityRateProb[0] : # ������װ
			baseQualityRate = exp.getBaseRateByQuality( ItemTypeEnum.CQT_GREEN, ItemTypeEnum.CPT_MYGOD )
		elif rnd < BaseQualityRateProb[1] : # ����װ
			baseQualityRate = exp.getBaseRateByQuality( ItemTypeEnum.CQT_GREEN, ItemTypeEnum.CPT_MYTHIC )
		elif rnd < BaseQualityRateProb[2] : # ��˵��װ
			baseQualityRate = exp.getBaseRateByQuality( ItemTypeEnum.CQT_GREEN, ItemTypeEnum.CPT_FABULOUS )

		CItemBase.setBaseRate( equip, baseQualityRate, self )

		# ��Ϊ��װ
		CItemBase.setQuality( equip, ItemTypeEnum.CQT_GREEN, self )

		# ���¼����;ö�
		equip.CalculateHardiness( self )

		# ˢ�¼۸�
		equip.updatePrice( self )

		# ����и������ԣ��Ͷ�װ���ĸ������Խ�����������
		extraEffect = equip.query("eq_extraEffect")
		if extraEffect :
			for effectId,effectValue in extraEffect.iteritems():
				equip.attrRebuild( "eq_extraEffect", effectId, self )

		slotAmount = 1
		# 0.3%�ļ��ʲ����ڶ������Կ�λ
		if random.random() < csconst.EQUIP_UP_EXTRA_SLOT_RATE:
			slotAmount = 2


		equip.addCreateEffect( [(0,0)] * slotAmount, self ) # �������Կ�λ

		equip.setQualityUpper( self.getName(), self ) # ���÷����ߵ�����

		equip.set( "eq_upFlag", True, self ) # ���÷�����ı�־���Ա�������װ����

		self.removeItemByUid_( jadeUid, amount =1, reason = csdefine.DELETE_ITEM_EQUIP_UP ) # �Ƴ���������
		self.statusMessage( csstatus.KIT_EQUIP_UP_SUCCESS ) # ��ʾ��ҳɹ�


	# ----------------------------------------------------------------
	# װ���������� by mushuang
	# ----------------------------------------------------------------
	def EquipAttrRebuild(self, srcEntityId, equipUid, attrType, effectId):
		"""
		װ����������
		@equipUid װ����uid
		@attrType ���Ե����(�ַ���)����eq_extraEffect,eq_createEffect....
		@effectId ��Ҫ����������id
		"""
		if not self.hackVerify_( srcEntityId ) : return


		# ��ȡuidָ����װ��
		equip = self.getItemByUid_( equipUid )

		#if ���û�����װ�� :
		if equip == None :
			#��ʾ��Чװ��
			self.statusMessage( csstatus.KIT_EQUIP_INVALID )
			#return
			return

		# if ����������
		if self.iskitbagsLocked():
			#��ʾ �����Ѿ�����
			self.statusMessage( csstatus.ROLE_QUEST_BAG_LOCK )
			#return
			return

		# if ��Ʒ�Ѿ����᣺
		if equip.isFrozen():
			# ��ʾ ��Ʒ�Ѿ�����
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			# return
			return

		# if ����Ʒ����װ�� :
		if not equip.isEquip() :
			#��ʾ���
			self.statusMessage( csstatus.KIT_EQUIP_NOT_EQUIP )
			#return
			return

		# if ��������������Ʒ :
		if equip.isAlreadyWield() :
			#��ʾ���
			self.statusMessage( csstatus.KIT_EQUIP_ALREADY_WIELD )
			#return
			return

		# if װ���ȼ� �� Ʒ�ʲ���
		if not ( equip.isGreen() and equip.getLevel() >= csconst.EQUIP_ATTR_REBUILD_LEVEL ) :
			#��ʾ���
			self.statusMessage( csstatus.KIT_EQUIP_NOT_GREEN_AND_REBUILDABLE )
			#return
			return


		# ��ȡ���豦��id
		pearlId = pearlData[ equip.getLevel() ]

		# ����������ϸñ���
		pearl = self.findItemFromNKCK_( pearlId )

		# if ���û����Ҫ�ı���
		if pearl == None :
			#��ʾ��ң�������һ���������ӵ���ʾ��Ϣ��
			pearl = g_items.createDynamicItem( pearlId )
			itemObj = ChatObjParser.dumpItem( pearl )
			self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", cschannel_msgs.EQUIP_ATTR_REBUILD_NEED ,[itemObj] )
			#return
			return

		# ��������������ĳЩ�쳣������������ɹ����򷵻�)
		if not equip.attrRebuild( attrType, effectId, self ) : return

		# ����ɾ������ǰ׺���򵥵������ܻ��и��ָ��������⣬
		# װ��ϵͳ�仯�ܿ죬һ�����ز����ò��˶�þ��п���
		# ���¹��ܷ�����ͻ��Ȼ����Ҫ�������ء���Ȼװ���Ѿ�
		# ������ԭ�й���Ҫǰ׺Ҳû���ã�
		equip.removeAllPrefix( self )

		# ��ȥ�������
		self.removeItemByUid_( pearl.uid, 1, csdefine.DELETE_ITEM_EQUIP_ATTR_REBUILD )

		# ��ʾ���
		self.statusMessage( csstatus.KIT_EQUIP_ATTR_REBUILD_SUCCESS )

		# ֪ͨ�ͻ��˳ɹ�
		self.client.equipAttrRebuildSuccess()

	def onEnterWater( self, srcEntityID, waterID ):
		"""
		Exposed method
		����һ��ˮ���õ���Ч��
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if waterID in WaterBuffDatas:
			self.setTemp( "lastWaterID", waterID )
			g_skills[int(WaterBuffDatas[waterID])].receiveLinkBuff( None, self )


	def onLeaveWater( self, srcEntityID, waterID ):
		"""
		Exposed method
		�뿪һ��ˮ���Ƴ���Ч��
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
		��ɫ����С�ÿ���·��ʱ����
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
				self.addItem( item, reason = csdefine.ADD_ITEM_RABBIT_RUN )			#���ܲ�
				count = self.countItemTotal_( csconst.RABBIT_RUN_ITEM_RADISH )
				if count >= 4:														#����ܲ��������ڵ��� 4�� ��ʤ��
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
		�������
		"""
		g_skills[csconst.RABBIT_RUN_CATCH_RABBIT_SKILL_ID].getBuffLink(1).getBuff().receive( None, self )
		self.client.initSpaceSkills( g_objFactory.getObject("fu_ben_rabbit_run").wolfSkillIDs, csdefine.SPACE_TYPE_RABBIT_RUN )

	def changeToRabbit( self ):
		"""
		���������
		"""
		g_skills[csconst.RABBIT_RUN_CATCH_RABBIT_SKILL_ID].getBuffLink(0).getBuff().receive( None, self )
		self.client.initSpaceSkills( g_objFactory.getObject("fu_ben_rabbit_run").rabbitSkillIDs, csdefine.SPACE_TYPE_RABBIT_RUN )

	def beforePostureChange( self, newPosture ):
		"""
		��̬�ı�֮ǰ

		@param newPosture : �ı�����̬
		"""
		SkillBox.beforePostureChange( self, newPosture )

	def afterPostureChange( self, oldPosture ):
		"""
		��̬�ı��

		@param oldPosture : �ı�ǰ����̬
		"""
		SkillBox.afterPostureChange( self, oldPosture )

	def onRemoveBuffProwl( self ):
		"""
		���Ǳ��Buff��Ĵ��� by ������ 2010-09-28
		"""
		self.reTriggerNearTrap()


	def addPersistentFlag( self, flag ):
		"""
		define method
		���Ӵ洢�ı�־λ
		"""
		flag = 1 << flag
		self.persistentFlags |= flag


	def removePersistentFlag( self, flag ):
		"""
		define method
		�Ƴ��洢�ı�־λ
		"""
		flag = 1 << flag
		self.persistentFlags &= flag ^ 0x7FFFFFFF

	def hasPersistentFlag( self, flag ):
		"""
		�Ƿ�ӵ��ĳ���洢�ı�־λ
		"""
		flag = 1 << flag
		return ( self.persistentFlags & flag ) == flag

	def changFashionNum( self, srcEntityID ):
		"""
		exposed method
		ʱװ�л�
		"""
		if not self.hackVerify_( srcEntityID ) : return
		# ��������״̬��ҹս���ܸ����С������С����������ж�������װ
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
		����ǰPkģʽѹջ��������Ϊ�µ�PKģʽ  by mushuang
		@newPkMode: Ҫ���õ���Pkģʽ
		"""
		stack = self.queryTemp( "pushedPkMode", [] )
		stack.append( self.pkMode )
		self.setTemp( "pushedPkMode", stack )

		self.setPkMode( self.id, newPkMode )

	def popPkMode( self ):
		"""
		defined method
		���ϴ�ѹջ��Pkģʽ��ջ��������Ϊ��ǰPKģʽ by mushuang
		"""
		stack = self.queryTemp( "pushedPkMode", [] )
		if len(stack) == 0:
			WARNING_MSG( "Can't find last pushed pk mode! Have you forgot to do a push before pop?" )
			return

		lastPkMode = stack.pop() # ����stackһ�������ö����ǿ��������Բ�����setTemp

		self.setPkMode( self.id, lastPkMode )

	def onMinHeightDetected( self, srcEntityID ):
		"""
		defined method
		exposed method
		��ҵ��䵽�����Ⱥ��֪ͨ by mushuang
		"""
		if not self.hackVerify_( srcEntityID ): return

		########################################################
		# ���ﲻ����֤��ֱ���ý�ɫ�����������������ǲ���ȫ�ģ� #
		# ���ǣ���ʵ����������ǣ��п��ܵ��ô˷�����ֻ������� #
		# ���Ŀͻ��ˣ����Դ˴�������֤Ҳ����������˵����⡣   #
		########################################################

		# �����ҵ�ǰλ�õ���������ȣ����뽫��ҵ�λ������������������ϣ���������ڸ����ʱ��,
		# �����������ڿɷ��пռ䣬��ô��һ���Ϊ��ǰλ�õ���������ȶ�����һ��
		deathDepth = float( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_DEATH_DEPTH ) )
		if self.position.y <= deathDepth :
			self.position.y = deathDepth + 1

		self.die( 0 )
		INFO_MSG( "Player( %s ) died because reaching death depth( %s )"%( self.id, deathDepth ) )

	#-----------------------------------------------------------------------------------------------------
	# ֱ���˶����,�����˶�������ײ�������ײ
	#-----------------------------------------------------------------------------------------------------
	def lineToPoint( self, dstPos, moveSpeed, faceMovement ):
		"""
		virtual method.
		�˶���ĳ�㣬�����˶�������ײ�������ײ,��entity���յ㲻һ����dstPos��
		@param dstPos			: �˶�Ŀ���
		@type dstPos			: Vector3
		@param faceMovement		: entity�����Ƿ���˶�����һ��
		@type faceMovement		: Bool
		"""
		self.controlledBy = None
		return AmbulantObject.lineToPoint( self, dstPos, moveSpeed, faceMovement )

	def onLineToPointFinish( self, controllerID, userData, state ):
		"""
		virtual method.
		�ƶ���ĳ��ص�
		"""
		self.controlledBy = self.base

	def switchWater( self, srcEntityID, switch ):
		"""
		Exposed Method
		��ҳ���ˮ�������֪ͨ�������
		"""
		if not self.hackVerify_( srcEntityID ): return
		self.onWaterArea = switch
		if switch:
			# csol-2047 ����ˮ���Զ�ȡ�����½�����
			if VehicleHelper.isOnLandVehicle( self ):
				self.removeBuffByBuffID( csdefine.VEHICLE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

			if not self.isAccelerate:
				# �߻�Ҫ��ֻ����û����������²Ŵ���ˮ�����Ч��
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
		����뿪����
		"""
		if not self.hackVerify_( srcEntityID ): return
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			self.gotoForetime()

	def onDelayPlayCamera(self,controllerID,userData):
		"""
		���ž�ͷ�¼� by wuxo 2011-11-26
		"""
		eventID = self.queryTemp("playCamera_eventID",0)
		if eventID :
			self.client.onCameraFly( eventID )
		self.removeTemp("playCamera_eventID")

	def onCompleteVideo(self,sourceID):
		"""
		��Ƶ���Ž��� by wuxo 2011-11-26
		"""
		if not self.hackVerify_( sourceID ): return
		self.clearBuff( [csdefine.BUFF_INTERRUPT_COMPLETE_VIDEO] )

	def reTriggerNearTrap( self ):
		"""
		���´�����Χ������
		"""
		es = self.entitiesInRangeExt( Const.REVIVE_ON_ORIGIN_RANGE, None, self.position )
		for e in es:
			if e.getEntityTypeName() == "AreaRestrictTransducer":
				if e.radius > 0:
					range = self.position.flatDistTo( e.position )
					if e.radius >= range:
						e.onEnterTrapExt( self, range, e.controlID )		# ��ɫ��������

			if not hasattr( e, "triggerTrap" ):
				continue

			if e.initiativeRange > 0:
				range = self.position.flatDistTo( e.position )
				if e.initiativeRange >= range:
					e.triggerTrap( self.id, range )

	def infoTongMemberFly( self, srcEntityID, lineNumber, spaceName, position, direction ):
		"""
		Exposed method.
		֪ͨ����Ա�ɵ��Լ���ߣ����ڰ�����ڣ�
		"""
		if not self.hackVerify_( srcEntityID ) : return

		# ������ʹ����·��ĸ���״̬
		cantFlyings = [ ( csdefine.ENTITY_STATE_FIGHT, csstatus.SKILL_USE_ITEM_WHILE_FIGHTING ),# ս��
						( csdefine.ENTITY_STATE_DEAD, csstatus.SKILL_USE_ITEM_WHILE_DEAD ),		# ����
						( csdefine.ENTITY_STATE_VEND, csstatus.ROLE_VEND_CANNOT_FLY ),			# ��̯
						( csdefine.ENTITY_STATE_RACER, csstatus.ROLE_RACE_CANNOT_FLY ),			# ����
						( csdefine.ENTITY_STATE_QUIZ_GAME, csstatus.ROLE_QUIZ_CANNOT_FLY ),		# ֪ʶ�ʴ�
					]
		for (state, infoMessage) in cantFlyings:
			if ( state == self.getState() ):
				self.statusMessage( infoMessage )
				return

		if not self.controlledBy:	# ���ʧȥ����ʱ������ʹ��
			self.statusMessage( csstatus.ROLE_USE_NOT_FIY_ITEM )
			return

		#Я��������Ʒ������ʹ����·��
		if self.hasMerchantItem():
			self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
			return

		# ����з�������buff
		if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		#�ڼ����в��ܴ���
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
	
	#���贫�������ȡ
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
		���÷�������
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
		��ҹ�������
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
		�ȴ�ʱ��δ������سǸ���
		"""
		if self.state != csdefine.ENTITY_STATE_FREE:
			self.setTemp( "role_die_teleport", True )
			self.reviveOnCity()

	def addFlag( self, flag ):
		"""
		�������ñ�־

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		"""
		GameObject.addFlag( self, flag )
		# ���밲ȫ��������PKģʽ
		if flag == csdefine.ROLE_FLAG_SAFE_AREA:
			self.lockPkMode()

	def removeFlag( self, flag ):
		"""
		�������ñ�־
		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		# ��32λ��ʹ�ã����Ǳ�־λ�����ʹ���������Ҫ��UINT32����ǰ�õ���INT32
		# ��ʹ��UINT32������һ��ԭ�������ǿ��ܲ�������ô���־��
		# ��һ��ԭ�������ʹ��UINT32��python��ʹ����INT64���������ֵ
		"""
		GameObject.removeFlag( self, flag )
		if flag == csdefine.ROLE_FLAG_SAFE_AREA:			 # �뿪��ȫ��������PKģʽ
			if self.queryTemp( "copy_space_lock_pkmode",0 ): # �����в�����
				return
			self.unLockPkMode()

	def beforeSpellUse( self, spell, target ):
		"""
		��ʹ�ü���֮ǰҪ��������
		@param  skillID:	Ҫʹ�õļ��ܱ�ʶ
		@type   skillID:	SKILLID
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		RoleEnmity.beforeSpellUse( self, spell, target )
		if spell.isMalignant():#���ʹ�ö��Լ��ܻ���½������
			self.clearBuff( [csdefine.BUFF_INTERRUPT_LAND_VEHICLE] )

	def getSpaceCopyLevel( self ):
		"""
		��ȡ������ڸ����ĵȼ�����ͨ�ã�Ŀǰֻ����YXLM����Buff�ӳɵļ��㣩
		"""
		copyLevel = 0
		spaceBase = self.getCurrentSpaceBase()
		if spaceBase is None: return copyLevel
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if hasattr( spaceEntity, "teamLevel" ):
			copyLevel = spaceEntity.teamLevel
		return copyLevel

#----------------------------------------------------
#����ʱ��
#----------------------------------------------------
	def setDanceChallengeIndex(self, srcEntityID, challengeIndex):
		#exposed methodName
		#challengeIndex ��ʾ�����ս������λ�ã�1��19�������Ϊ0��ʾ��ϰ����
		self.challengeIndex = challengeIndex
		if challengeIndex:#��ս����ʱ������6����
			self._dancechellengeTimerID =self.addTimer(360, 0, ECBExtend.DANCECHELLENGETIMER)
		#self.getCurrentSpaceBase().cell.setDanceChallengeIndex(challengeIndex)

	def onTimerDanceChellengeTimeOver(self, timerID, cbid ):#6����ʱ�䵽����ս����
		for entity in self.entitiesInRangeExt(35):
			if entity.__class__.__name__ == "Role":
				entity.cancelChallenge()
				DEBUG_MSG("player[%s] ,dancechellenge time is over "%self.playerName)

	def noticeChallengeResult(self, challengeResult):
		#define method
		INFO_MSG("noticeChallengeResult is %d to player[%s]"%(challengeResult, self.planterName))
		if challengeResult:#��ս�ɹ�
			self.challengeSuccess()
		else:
			self.challengeFailed()

	def setRoleModelInfo(self, srcEntityID, playerModelInfo):
		#exposed methodName
		self.playerModelInfo = playerModelInfo

	def challengeSuccess(self):
		#define method
		DEBUG_MSG("player[%s] challengeSuccess"%self.playerName)
		#BigWorld.globalData["DanceMgr"].getDanceExp(self.playerName, self.base, False, self.level)  #��ս��Ϊ����������������ͨ��������
		BigWorld.globalData["DanceMgr"].setModelInfo(self.playerModelInfo, self.challengeIndex, self.base, self.databaseID)#�ٸ��ĳɹ���ս�ߵ�ģ�͵���Ӧ��λ��
		#�Լ����Ͽ���������buff����ȥ�����ٸ��Լ����µ�buff
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
		#�������鱶��
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
		if self.queryTemp("danceType"):  #�����ս֮���Temp
			self.removeTemp("danceType")

	def challengeFailed(self):
		DEBUG_MSG("player[%s] challengeFailed"%self.playerName)
		self.danceKingType = csdefine.DANCER_NONE  #δ��������
		self.spellTarget(csconst.DanceingPunishSkillID, self.id) #add challengeFailed punish Buff (5 mintues can not challenge again)
		self.clearDanceInfo()

	def teleportToDanceChallengeSpace(self,  srcEntityID, challengeIndex):
		#exposed method
		#��ս�ڼ�λ���� 0��ʾ��ϰ���ݲ���1��19��ʾ��ս1��19������
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
		������������Ϣ���ͻ���

		"""
		self.setTemp( "DancingKingInfos", DancingKingInfos)
		self.setTemp( "dancing_king_infos_order", 1 )
		DEBUG_MSG("ROLE_SEND_DANCING_KING_INFOS_START DancingKingInfos = %s"%DancingKingInfos)		# ��ʼ����������Ϣ���ͻ���
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_DANCING_KING_INFOS_CBID ) #ÿ0.15�뷢һ�Σ�һ��5����


	def onTimer_updateClientDancingKingInfos( self, timerID, cbid ) :
		"""
		�ְ�����������Ϣ
		"""
		count = 19 #�ܹ�19������
		infos = self.queryTemp("DancingKingInfos")

		startOrder = self.queryTempInt( "dancing_king_infos_order" )
		endOrder = min( count, startOrder + 5 )							# ÿ�η� 5 ��
		for order in xrange( startOrder, endOrder ) :					# һ�η�5����������Ϣ
			self.client.addDancingKingInfo( order, infos.get(order, None) )
		if endOrder < count :											# �������ʣ��
			self.addTempInt( "dancing_king_infos_order", 5 )			# ������ָ������ 5 ��
		else :															# ���û��ʣ����Ʒ
			self.cancel( timerID )										# ɾ������ timer
			self.removeTemp( "dancing_king_infos_order" )				# ɾ����ʱ����ָ��
			self.removeTemp(  "DancingKingInfos" )
			self.client.sendDancingKingInfosOver()   #������Ϣ���
			DEBUG_MSG("ROLE_SEND_DANCING_KING_INFOS_OVER" )		# ��������������Ϣ���ͻ���

	def updateDanceKingInfos(self, DancingKingInfos):
		"""
		defined method
		�����������������ҵĿͻ�����������Ϣ
		"""
		if self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_WUTING:
			self.requestDancingKingInfos(DancingKingInfos)  #��������Ϣ�ı�ʱ��������������ҵĿͻ��˵�������Ϣ

	def removeDanceTypeTemp(self ,srcEntityID ):
		#Expoesd method
		if self.queryTemp("danceType"):
			self.removeTemp("danceType")

	def onEnterDanceCopy(self):
		#defined method
		if self.queryTemp("danceType"):
			self.getCurrentSpaceBase().cell.enterDanceCopy(time.time())
			self.client.enterDanceCopy(True)
			self.client.initSpaceSkills( csconst.spaceDanceSkills, csdefine.SPACE_TYPE_DANCECOPY_CHALLENGE )#��ʼ������ʹ�õĿռ似��
		else:
			self.getCurrentSpaceBase().cell.enterDanceCopy(0)
			self.client.enterDanceCopy(False)
			self.client.initSpaceSkills( csconst.spaceDanceSkills, csdefine.SPACE_TYPE_DANCECOPY_PARCTICE ) #��ʼ������ʹ�õĿռ似��

	def onLeaveDanceCopy(self):
		#defined method
		if self.queryTemp("danceType"):
			self.client.leaveDanceCopy(True)  #��ս���踱��
		else:
			self.client.leaveDanceCopy(False)		#��ϰ���踱��

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
		#index : ���ѡ���λ�����20 - 39
		BigWorld.globalData["DanceMgr"].addDanceExpTime(self.playerName)
		self.getCurrentSpaceBase().cell.setDanceHallInfo(index, self.databaseID, modelInfo)
		self.getCurrentSpaceBase().cell.spawnDanceKing(index, modelInfo)

	def quitDance(self, srcEntityID):
		#Exposed method
		if self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_WUTING : #���������˳�
			self.gotoSpace( "fengming",Math.Vector3(-171.636002 ,4.871000 ,-52.265999) ,Math.Vector3(0, 0, 0))
			self.client.leaveWuTing()
		elif self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_DANCE_CHALLENGE: #����ս���踱�����˳�
			BigWorld.globalData["DanceMgr"].indexIsChallenged(self.challengeIndex, False) #ȥ����ǰλ����������ս�ı��
			for entity in self.entitiesInRangeExt(35):
				if entity and entity.__class__.__name__ == "DanceNPC":
					entity.cancelChallenge()
			self.challengeFailed()
			self.gotoSpace( "fu_ben_wu_tai_001",Math.Vector3(29, 2, 18) ,Math.Vector3(0, 0, 0))
			self.client.enterWuTing()
		elif self.getCurrentSpaceData(csconst.SPACE_SPACEDATA_KEY) == csconst.SPACE_DANCE_PRACTICE: #����ϰ���踱�����˳�
			self.gotoSpace( "fu_ben_wu_tai_001",Math.Vector3(29, 2, 18) ,Math.Vector3(0, 0, 0))
			self.client.enterWuTing()
		else:
			ERROR_MSG("can't find those type space by Button exit in wuting!")

	def getDanceExp(self, exp, type):
		"""
		#define method
		#time ��ʾ���˶�õ���(��λ�Ƿ���) int���ͣ� time <= 480 �Ѿ��Ǵ������
		#type��BOOL ��Ϊ0��ʾ��������ͨ���飬1Ϊ�������顣
		#exp = (3.5*lv^1.5 + 9) * ���� * time ��ͨ1������ѡ2����ͭ��3��������5��������10��
		"""
		if type :
			self.addExp(exp, csdefine.CHANGE_EXP_DANCEKING)
		else:
			self.addExp(exp, csdefine.CHANGE_EXP_DANCE)




	#Զ�̻�ȡ���װ����Ϣ
	def onQueryRoleEquipItems( self, queryMB ):
		"""
		define method.
		���Զ�̲�ѯ��ɫ��װ����Ϣ
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
		��ҽ������巶Χ��������״̬��������
		"""
		quest = self.getQuest( questID )
		if quest and quest.query( self ) == questStatus:
			self.client.onPlayMonsterSound( 0, soundEvent )

#-------------------------------���Ȫm؅����------------------------
	def onLeaveYaYuCopy( self ):
		"""
		define method
		�뿪�m؅����
		"""
		#�����������
		for item in copy.copy( self.itemsBag.getDatas() ):
			if item.id in csconst.YA_YU_COPY_SPECAIL_ITEMS:
				self.deleteItem_( item.order, item.amount, True, csdefine.DELETE_ITEM_DESTROYITEM )

	def transConditionCheck( self ):
		"""
		����Ƿ���Դ���
		"""
		if VehicleHelper.isFlying( self ):
			# ����
			self.client.onStatusMessage( csstatus.CANNOT_TRANSPORT_IN_FLY, "" )
			return False

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			# ����
			self.client.onStatusMessage( csstatus.CANNOT_TRANSPORT_IN_PRISON, "" )
			return False

		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			# ������ͨ��ͼ
			self.client.onStatusMessage( csstatus.CANNOT_TRANSPORT_IN_SPACE_COPY, "" )
			return False

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# ����
			self.client.onStatusMessage( csstatus.CANNOT_FLY_WHILE_DEAD, "" )
			return False

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# ս��
			self.client.onStatusMessage( csstatus.CANNOT_FLY_WHILE_FIGHTING, "" )
			return False

		return True

	def setPartrol( self, srcEntityID, path, model ):
		"""
		exposed method
		����Ѱ·�ڵ�����
		"""
		if srcEntityID != self.id: return
		self.patrolPath = path		#·��
		self.patrolModel = model	#ģ��

	def onCreatePotential( self ):
		"""
		define method
		base�˴�����Ǳ�ܸ����Ļص�
		"""
		info = self.popTemp( "potential_creating", None )
		if not info: return
		selfEntity = BigWorld.entities.get( info[0] )
		if not selfEntity:
			return
		selfEntity.setTemp( "potential_createSpaceName", info[1] )

