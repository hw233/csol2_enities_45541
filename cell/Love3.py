# -*- coding: gb18030 -*-
# Love3.py
# Love3 Module(cell)
# 2004-12-24
import Language
import items

import BigWorld

from Resource import DispersionTable
from NPCExpLoader import NPCExpLoader								# ���ﾭ�������
from NPCBaseAttrLoader import NPCBaseAttrLoader					# ��������������Լ�����
from Resource.GoodsLoader import GoodsLoader								# NPC����Ʒ�б�
from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader	# NPC�����������Ʒ���ñ�
from Resource.NPCTalkLoader import NPCTalkLoader							# NPC�Ի����ñ�
from Resource.BoundingBoxLoader import BoundingBoxLoader					# �����bounding box
from TitleMgr import TitleMgr								# �ƺ�����
from Resource.NPCExcDataLoader import NPCExcDataLoader						# NPC������������
from Resource.QuestRewardFromTableLoader import QuestRewardFromTableLoader		# ����������������Ϊ�������
from Resource.RewardQuestLoader import RewardQuestLoader		# ������������
from Resource.TongRobWarRewardLoader import TongRobWarRewardLoader
from RelationStaticModeMgr import RelationStaticModeMgr
from Resource.RewardsMgr import RewardsMgr
import LevelEXP
import Resource.SpaceData
import Resource.AIData
import Resource.TransporterData
import Function
import time

import CellAppActions
import EntityCacheTask
import Resource.BoardEventLoader
import Resource.CopyStageData

print "Love3 cell Module is Loading..."
print "Start load Love3 time:", time.time()

Function.initRand()


from Resource.PatrolMgr import PatrolMgr
g_patrolMgr = PatrolMgr.instance()
g_patrolMgr.loadCustomNPCPatrol( "config/server/patrolData" )

g_aiActions = Resource.AIData.aiAction_instance()
g_aiActions.load( "config/server/ai/AIAction.xml" )	# ��ʼ������
g_aiConditions = Resource.AIData.aiConditon_instance()
g_aiConditions.load( "config/server/ai/AICondition.xml" )	# ��ʼ������
g_aiTemplates = Resource.AIData.aiTemplate_instance()
g_aiTemplates.load( "config/server/ai/AITemplet.xml" )	# ��ʼ������
g_aiDatas = Resource.AIData.aiData_instance()
g_aiDatas.load( "config/server/ai/AIData.xml" )	# ��ʼ������
g_npcaiDatas = Resource.AIData.NPCAI_instance()
g_npcaiDatas.load( "config/server/gameObject/NPCAI.xml" )	# ��ʼ������

# CopyStage���,���ڸ���֮ǰ����
g_copyStageActions = Resource.CopyStageData.copyStageAction_instance()
g_copyStageActions.load( "config/server/copyStage/copyEvent/CopyStageAction.xml" )			# ��ʼ������
g_copyStageConditions = Resource.CopyStageData.copyStageConditon_instance()
g_copyStageConditions.load( "config/server/copyStage/copyEvent/CopyStageCondition.xml" )	# ��ʼ������

g_npcExp = NPCExpLoader.instance()
g_npcBaseAttr = NPCBaseAttrLoader.instance()

g_npcExcData = NPCExcDataLoader.instance()
#g_npcExcData.load( "config/server/gameObject/NPCExcData.xml" )
g_rewards = RewardsMgr()	# ���������ݳ�ʼ��
g_goods = GoodsLoader.instance()
g_goods.load( "config/server/gameObject/NPCGoods.xml" )
g_npcQuestDroppedItems = NPCQuestDroppedItemLoader.instance()
g_npcQuestDroppedItems.load( "config/server/gameObject/NPCQuestDroppedItem.xml" )
g_npcBoundingBoxs = BoundingBoxLoader.instance()
g_titleLoader = TitleMgr.instance()					# ��ʼ���ƺ�ϵͳ
g_questRewardFromTable = QuestRewardFromTableLoader.instance()
g_questRewardFromTable.load( "config/server/gameObject/QuestRewardFromTable.xml" )
g_tongRobWarRewards = TongRobWarRewardLoader.instance()
g_tongRobWarRewards.load( "config/server/gameObject/TongRobWarReward.xml" )

# init cooldown
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()
g_cooldowns.load( "config/skill/CooldownType.xml" )
from Resource.SkillLoader import g_skills

# ������skill֮ǰ����
#g_dispersionTable = DispersionTable.instance()
#g_dispersionTable.load( "config/skill/dispel_define.xml" )

from Resource.SkillLoader import g_buffLimit
g_buffLimit.load( "config/skill/buff_limit.xml" )  #5KB
from Resource.SkillTrainerLoader import SkillTrainerLoader
g_skillTrainerList = SkillTrainerLoader.instance()
g_skillTrainerList.load( "config/server/gameObject/NPCTeachSkillList.xml" )
from Resource.SkillTeachLoader import g_skillTeachDatas		# ����ѧϰ���ݹ���
# ȫ�ֵ����б�
g_itemsDict = items.instance()
g_npcTalk = NPCTalkLoader.instance()
g_npcTalk.load( "config/server/gameObject/NPCTalk.xml" )
# װ����������
from items.EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()

# װ����װ����
from items.EquipSuitLoader import EquipSuitLoader
g_equipSuit = EquipSuitLoader.instance()

# ��ʾ��Ʒ����
from items.CueItemsLoader import CueItemsLoader
g_cueItem = CueItemsLoader.instance()

# ���Ϻϳ�
from ItemSystemExp import StuffMergeExp
g_stuff = StuffMergeExp.instance()

# װ��ǿ��(���ʼ�����Ѿ���������)
from ItemSystemExp import EquipIntensifyExp
g_equipIntensify = EquipIntensifyExp.instance()
# װ������/����
from ItemSystemExp import EquipMakeExp
g_equipMake = EquipMakeExp.instance()

# װ��Ʒ��((���ʼ�����Ѿ���������))
from ItemSystemExp import EquipQualityExp
g_equipQuality = EquipQualityExp.instance()

#����Ʒ�ʵ�����ǰ׺�ķֲ���Ϣ
from ItemSystemExp import PrefixAllotExp
g_prefixAllotExp  = PrefixAllotExp.instance()

#��ְҵ��װ��ǰ׺B�����ɸ������ݼ���
from ItemSystemExp import PrefixDistribute
g_prefixDistribute  = PrefixDistribute.instance()


#��������ǰ׺����Ϣ
from ItemSystemExp import PropertyPrefixExp
g_propertyPrefixExp  = PropertyPrefixExp.instance()


# װ����Ƕ
from ItemSystemExp import EquipStuddedExp
g_equipStudded = EquipStuddedExp.instance()

# װ����
from ItemSystemExp import EquipBindExp
g_equipBind = EquipBindExp.instance()

# ����ϳ�
from ItemSystemExp import SpecialComposeExp
g_specialCompose = SpecialComposeExp.instance()

#ˮ��ժ��
from ItemSystemExp import RemoveCrystalExp
g_removeCrystal = RemoveCrystalExp.instance()

#��װ��Ʒ
from ItemSystemExp import EquipImproveQualityExp
g_equipImproveQuality = EquipImproveQualityExp.instance()

#ϴǰ׺
from ItemSystemExp import ChangePropertyExp
g_changeProperty = ChangePropertyExp.instance()

# �������ͷ���ֵ����
from ItemSystemExp import ItemTypeAmendExp
g_armorAmend = ItemTypeAmendExp.instance()

# װ�����
from ItemSystemExp import EquipSplitExp
g_equipSplitExp = EquipSplitExp.instance()

# �������
from items.ItemDropLoader import ItemDropInWorldLoader
g_itemDropInWorld = ItemDropInWorldLoader.instance()

# ���������Ʒ
from items.ItemDropLoader import ItemDropTreasureBoxLoader
g_itemTreasureBoxDrop = ItemDropTreasureBoxLoader.instance()


# ���ҵ�����
from items.ItemDropLoader import ItemDropLotteryLoader
g_itemDropLotteryLoader = ItemDropLotteryLoader.instance()

# �콵���е���:�вƱ���
from items.ItemDropLoader import ItemDropLuckyBoxZhaocai
g_itemDropLuckyBoxZhaocai = ItemDropLuckyBoxZhaocai.instance()

# �콵���е���:��������
from items.ItemDropLoader import ItemDropLuckyBoxJinbao
g_itemDropLuckyBoxJinbao = ItemDropLuckyBoxJinbao.instance()

# �������滻�����
from items.ItemDropLoader import HonorItemZhaocai
g_honorItemZhaocai = HonorItemZhaocai.instance()

# �������滻��Ʒ
from items.ItemDropLoader import HonorItemJinbao
g_honorItemJinbao = HonorItemJinbao.instance()


# ������ʿ���
from items.ItemDropLoader import SpecialDropLoader
g_SpecialDropLoader = SpecialDropLoader.instance()

# ����������
from items.ItemDropLoader import EquipMakeDropLoader
g_EquipMakeDropLoader = EquipMakeDropLoader.instance()

# ��������
from items.TalismanEffectLoader import TalismanEffectLoader
g_tmEffect = TalismanEffectLoader.instance()

# ��ʼ����������
from PetFormulas import formulas as g_petFormulas
g_petFormulas.initialize()

# ����NPC��
from ObjectScripts.GameObjectFactory import g_objFactory
g_objFactory.load( "config/server/gameObject/objPath.xml" )

LevelEXP.RoleLevelEXP.initialize()
LevelEXP.PetLevelEXP.initialize()
LevelEXP.TongLevelEXP.initialize()
g_amendExp = LevelEXP.AmendExp.instance()

g_spacedata = Resource.SpaceData.g_spacedata
g_transporterData = Resource.TransporterData.g_transporterData

# penghuawei in 2005-07-29, ����ƺ�ֻ�ܷ������
from Resource.QuestLoader import QuestsFlyweight
g_taskData = QuestsFlyweight.instance()
g_taskData.load( "config/quest/" )	# ��ʼ������

from ChatProfanity import chatProfanity as g_chatProfanity
g_chatProfanity.initialize()

from Resource.TreasurePositions import TreasurePositions
g_TreasurePositions = TreasurePositions.instance()		# �ر�ͼλ������

from Resource.BigWorldLevelMaps import BigWorldLevelMaps
g_BigWorldLevelMaps = BigWorldLevelMaps.instance()		# �����ͼ��Ӧ�Ĺ��Ｖ����Ϣ

from Resource.MonsterActivityMgr import MonsterActivityMgr
#����������Ҫ�������ýӿ�

# wsf:��ά������11:08 2009-1-8
from Resource.TongFeteDataLoader import TongFeteDataLoader
TongFeteDataLoader.instance().load( "config/server/TongFeteReward.xml" )

# NPCλ������
from config.NPCDatas import NPCDatas
g_NPCsPosition = NPCDatas.cellDatas

# ͽ�������������Ӧ�Ľ���
from Resource.TeachCreditLoader import TeachCreditLoader
g_teachCreditLoader = TeachCreditLoader.instance()

g_questQuestionSection = Language.openConfigSection("config/server/QuestQuestion.xml")

g_ieQuestionSection = Language.openConfigSection("config/server/ImperialExaminations.xml")

# ����ֽ�
from KuaiLeJinDan import KuaiLeJinDan
g_KuaiLeJinDan = KuaiLeJinDan.instance()

# ����ռ��
from Resource.SuanGuaZhanBuLoader import SuanGuaZhanBuLoader
g_SuanGuaZhanBuLoader = SuanGuaZhanBuLoader.instance()
g_SuanGuaZhanBuLoader.load( "config/server/SuanGuaZhanBu.xml" )

# ͳ��ģ��
from Statistic import Statistic
g_Statistic = Statistic.instance()
g_Statistic.load( "config/server/questTypeStr.xml" )

# �ȼ�������ͨ��Ʒ
from config.item import LevelRestrainItems
g_levelResItems = LevelRestrainItems.Datas


# add reward configs by ����
g_rewards.addRewardProj( "rewardsCfg.rwp" )

# �������
from LevelEXP import VehicleLevelExp
g_vehicleExp = VehicleLevelExp.instance()

from Resource.TanabataQuizQuestionLoader import TanabataQuizQuestionLoader
g_tanabataQuizLoader = TanabataQuizQuestionLoader.instance()
g_tanabataQuizLoader.load( "config/server/TanabataQuizQuestion.xml" )

from config.skill.Skill.SkillDataMgr import Datas as SkillConfigScript


print "Start Init skill cfgs:", time.time()
SkillConfigScript.initSkillCfgs()
print "End Init skill cfgs:", time.time()

print "Start Init skill script:", time.time()
SkillConfigScript.initSkillScript()
print "End Init skill script:", time.time()

from Resource.SpaceHuaShanData import SpaceHuaShanData
g_spaceHuaShanData = SpaceHuaShanData.instance()
g_spaceHuaShanData.load( "config/server/SpaceChallengeMonsterInfos.xml" )

from Resource.SpaceCopyDataLoader import SpaceCopyDataLoader
g_spaceCopyData = SpaceCopyDataLoader.instance()
g_spaceCopyData.load( "config/SpaceCopyInfos.xml" )

# �������ϵͳ��Դ����
from CellSpaceCopyFormulas import spaceCopyFormulas
spaceCopyFormulas.loadCopiesData( "config/matchablecopies.xml" )

# Ǳ���Ҷ���������
from Resource.CopyPotentialMeleeLoader import CopyPotentialMeleeLoader
g_copyPotentialMeleeLoader = CopyPotentialMeleeLoader.instance()
g_copyPotentialMeleeLoader.initData()

#����������������
from Resource.SpaceCopyCountLoader import SpaceCopyCountLoader
g_SpaceCopyCount = SpaceCopyCountLoader.instance()
g_SpaceCopyCount.initCnfData()

#���������
from SpaceCopyReviveConfigLoader import SpaceCopyReviveConfigLoader
g_SpaceCopyReviveCfg = SpaceCopyReviveConfigLoader.instance()
g_SpaceCopyReviveCfg.initCnfData()

# �ƾٿ������
from Resource.ImperialExaminationsLoader import g_imperialExaminationsLoader
g_imperialExaminationsLoader.load( "config/server/ImperialExaminations.xml" )  #5KB

# �����¼�
g_boardEventLoader = Resource.BoardEventLoader.g_boardEventLoader()
g_boardEventLoader.load( "config/server/BoardEvent.xml" )

g_rewardQuestLoader = RewardQuestLoader.instance()
g_rewardQuestLoader.initTimeAndProbilityData()
g_rewardQuestLoader.initQuestData()

# ������Ч
from Resource.TrapSoundsLoader import g_trapSoundsLoader
g_trapSoundsLoader.load( "config/server/TrapEntitySounds.xml" )

# ��Ἴ��
from TongDatas import tongSkill_instance
g_tongSkills = tongSkill_instance()

g_relationStaticMgr = RelationStaticModeMgr.instance()
g_relationStaticMgr.initCampRelationCfg()
g_relationStaticMgr.createRelationInstance()


# ----------------------
# ��֤����entity��һ������
#-----------------------
GLOBAL_CALL_CELL_METHOD_KEY = "onCallEntityMedthod"

def callEntityMedthod( targetID, methodName, methodArgs ):
	"""
	Զ�̵���һ��cell entity����
	��entity���ڵ�ǰcellʱ���˷�����㲥����cell�� ���Ǳ�Ҫ�ľ�������
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		method = getattr( e, methodName )
		method( *methodArgs )
	else:
		BigWorld.cellAppData[ GLOBAL_CALL_CELL_METHOD_KEY ] = ( targetID, methodName, methodArgs )

def onCallEntityMedthod( targetID, methodName, methodArgs ):
	"""
	Զ�̵���һ��cell entity�����Ļص�
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		method = getattr( e, methodName )
		method( *methodArgs )

# ----------------------
# ��֤����һ��entity��ֵ
#-----------------------
GLOBAL_SET_CELL_PRO_KEY		= "onSetEntityPro"

def setEntityPro( targetID, proName, proValue ):
	"""
	����һ��cell entity��ֵ
	��entity���ڵ�ǰcellʱ���˷�����㲥����cell�� ���Ǳ�Ҫ�ľ�������
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		setattr( e, proName, proValue )
	else:
		BigWorld.cellAppData[ GLOBAL_SET_CELL_PRO_KEY ] = ( targetID, proName, proValue )

def onSetEntityPro( targetID, proName, proValue ):
	"""
	����һ��cell entity��ֵ�ص�
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		setattr( e, proName, proValue )

def onCellAppData( key, value ):
	"""
	BigWorld.cellAppData�ֵ����õĻص�
	"""
	if key == GLOBAL_CALL_CELL_METHOD_KEY:
		onCallEntityMedthod( *value )
		del BigWorld.cellAppData[ GLOBAL_CALL_CELL_METHOD_KEY ]
	
	if key == GLOBAL_SET_CELL_PRO_KEY:
		onSetEntityPro( *value )
		del BigWorld.cellAppData[ GLOBAL_SET_CELL_PRO_KEY ]


import TraceBackHook
# Love3.py

print "Love3 cell Module Load Over!"
print "End load Love3 time:", time.time()
