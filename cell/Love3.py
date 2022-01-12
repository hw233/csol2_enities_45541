# -*- coding: gb18030 -*-
# Love3.py
# Love3 Module(cell)
# 2004-12-24
import Language
import items

import BigWorld

from Resource import DispersionTable
from NPCExpLoader import NPCExpLoader								# 怪物经验加载器
from NPCBaseAttrLoader import NPCBaseAttrLoader					# 怪物四项基础属性加载器
from Resource.GoodsLoader import GoodsLoader								# NPC的商品列表
from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader	# NPC的任务掉落物品配置表
from Resource.NPCTalkLoader import NPCTalkLoader							# NPC对话配置表
from Resource.BoundingBoxLoader import BoundingBoxLoader					# 怪物的bounding box
from TitleMgr import TitleMgr								# 称号配置
from Resource.NPCExcDataLoader import NPCExcDataLoader						# NPC附加属性配置
from Resource.QuestRewardFromTableLoader import QuestRewardFromTableLoader		# 任务奖励，奖励内容为表格配置
from Resource.RewardQuestLoader import RewardQuestLoader		# 悬赏任务配置
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
g_aiActions.load( "config/server/ai/AIAction.xml" )	# 初始化数据
g_aiConditions = Resource.AIData.aiConditon_instance()
g_aiConditions.load( "config/server/ai/AICondition.xml" )	# 初始化数据
g_aiTemplates = Resource.AIData.aiTemplate_instance()
g_aiTemplates.load( "config/server/ai/AITemplet.xml" )	# 初始化数据
g_aiDatas = Resource.AIData.aiData_instance()
g_aiDatas.load( "config/server/ai/AIData.xml" )	# 初始化数据
g_npcaiDatas = Resource.AIData.NPCAI_instance()
g_npcaiDatas.load( "config/server/gameObject/NPCAI.xml" )	# 初始化数据

# CopyStage相关,需在副本之前加载
g_copyStageActions = Resource.CopyStageData.copyStageAction_instance()
g_copyStageActions.load( "config/server/copyStage/copyEvent/CopyStageAction.xml" )			# 初始化数据
g_copyStageConditions = Resource.CopyStageData.copyStageConditon_instance()
g_copyStageConditions.load( "config/server/copyStage/copyEvent/CopyStageCondition.xml" )	# 初始化数据

g_npcExp = NPCExpLoader.instance()
g_npcBaseAttr = NPCBaseAttrLoader.instance()

g_npcExcData = NPCExcDataLoader.instance()
#g_npcExcData.load( "config/server/gameObject/NPCExcData.xml" )
g_rewards = RewardsMgr()	# 奖励总数据初始化
g_goods = GoodsLoader.instance()
g_goods.load( "config/server/gameObject/NPCGoods.xml" )
g_npcQuestDroppedItems = NPCQuestDroppedItemLoader.instance()
g_npcQuestDroppedItems.load( "config/server/gameObject/NPCQuestDroppedItem.xml" )
g_npcBoundingBoxs = BoundingBoxLoader.instance()
g_titleLoader = TitleMgr.instance()					# 初始化称号系统
g_questRewardFromTable = QuestRewardFromTableLoader.instance()
g_questRewardFromTable.load( "config/server/gameObject/QuestRewardFromTable.xml" )
g_tongRobWarRewards = TongRobWarRewardLoader.instance()
g_tongRobWarRewards.load( "config/server/gameObject/TongRobWarReward.xml" )

# init cooldown
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()
g_cooldowns.load( "config/skill/CooldownType.xml" )
from Resource.SkillLoader import g_skills

# 必须在skill之前加载
#g_dispersionTable = DispersionTable.instance()
#g_dispersionTable.load( "config/skill/dispel_define.xml" )

from Resource.SkillLoader import g_buffLimit
g_buffLimit.load( "config/skill/buff_limit.xml" )  #5KB
from Resource.SkillTrainerLoader import SkillTrainerLoader
g_skillTrainerList = SkillTrainerLoader.instance()
g_skillTrainerList.load( "config/server/gameObject/NPCTeachSkillList.xml" )
from Resource.SkillTeachLoader import g_skillTeachDatas		# 技能学习数据管理
# 全局道具列表
g_itemsDict = items.instance()
g_npcTalk = NPCTalkLoader.instance()
g_npcTalk.load( "config/server/gameObject/NPCTalk.xml" )
# 装备附加属性
from items.EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()

# 装备套装属性
from items.EquipSuitLoader import EquipSuitLoader
g_equipSuit = EquipSuitLoader.instance()

# 提示物品配置
from items.CueItemsLoader import CueItemsLoader
g_cueItem = CueItemsLoader.instance()

# 材料合成
from ItemSystemExp import StuffMergeExp
g_stuff = StuffMergeExp.instance()

# 装备强化(类初始化就已经加载数据)
from ItemSystemExp import EquipIntensifyExp
g_equipIntensify = EquipIntensifyExp.instance()
# 装备制造/改造
from ItemSystemExp import EquipMakeExp
g_equipMake = EquipMakeExp.instance()

# 装备品质((类初始化就已经加载数据))
from ItemSystemExp import EquipQualityExp
g_equipQuality = EquipQualityExp.instance()

#加载品质的属性前缀的分布信息
from ItemSystemExp import PrefixAllotExp
g_prefixAllotExp  = PrefixAllotExp.instance()

#各职业的装备前缀B的生成概率数据加载
from ItemSystemExp import PrefixDistribute
g_prefixDistribute  = PrefixDistribute.instance()


#加载属性前缀的信息
from ItemSystemExp import PropertyPrefixExp
g_propertyPrefixExp  = PropertyPrefixExp.instance()


# 装备镶嵌
from ItemSystemExp import EquipStuddedExp
g_equipStudded = EquipStuddedExp.instance()

# 装备绑定
from ItemSystemExp import EquipBindExp
g_equipBind = EquipBindExp.instance()

# 特殊合成
from ItemSystemExp import SpecialComposeExp
g_specialCompose = SpecialComposeExp.instance()

#水晶摘除
from ItemSystemExp import RemoveCrystalExp
g_removeCrystal = RemoveCrystalExp.instance()

#绿装升品
from ItemSystemExp import EquipImproveQualityExp
g_equipImproveQuality = EquipImproveQualityExp.instance()

#洗前缀
from ItemSystemExp import ChangePropertyExp
g_changeProperty = ChangePropertyExp.instance()

# 防具类型防御值修正
from ItemSystemExp import ItemTypeAmendExp
g_armorAmend = ItemTypeAmendExp.instance()

# 装备拆分
from ItemSystemExp import EquipSplitExp
g_equipSplitExp = EquipSplitExp.instance()

# 世界掉落
from items.ItemDropLoader import ItemDropInWorldLoader
g_itemDropInWorld = ItemDropInWorldLoader.instance()

# 宝箱掉落物品
from items.ItemDropLoader import ItemDropTreasureBoxLoader
g_itemTreasureBoxDrop = ItemDropTreasureBoxLoader.instance()


# 锦囊掉落率
from items.ItemDropLoader import ItemDropLotteryLoader
g_itemDropLotteryLoader = ItemDropLotteryLoader.instance()

# 天降宝盒掉落:招财宝盒
from items.ItemDropLoader import ItemDropLuckyBoxZhaocai
g_itemDropLuckyBoxZhaocai = ItemDropLuckyBoxZhaocai.instance()

# 天降宝盒掉落:进宝宝盒
from items.ItemDropLoader import ItemDropLuckyBoxJinbao
g_itemDropLuckyBoxJinbao = ItemDropLuckyBoxJinbao.instance()

# 荣誉度替换经验等
from items.ItemDropLoader import HonorItemZhaocai
g_honorItemZhaocai = HonorItemZhaocai.instance()

# 荣誉度替换物品
from items.ItemDropLoader import HonorItemJinbao
g_honorItemJinbao = HonorItemJinbao.instance()


# 掉落概率控制
from items.ItemDropLoader import SpecialDropLoader
g_SpecialDropLoader = SpecialDropLoader.instance()

# 制作卷掉落表
from items.ItemDropLoader import EquipMakeDropLoader
g_EquipMakeDropLoader = EquipMakeDropLoader.instance()

# 法宝数据
from items.TalismanEffectLoader import TalismanEffectLoader
g_tmEffect = TalismanEffectLoader.instance()

# 初始化宠物数据
from PetFormulas import formulas as g_petFormulas
g_petFormulas.initialize()

# 加载NPC类
from ObjectScripts.GameObjectFactory import g_objFactory
g_objFactory.load( "config/server/gameObject/objPath.xml" )

LevelEXP.RoleLevelEXP.initialize()
LevelEXP.PetLevelEXP.initialize()
LevelEXP.TongLevelEXP.initialize()
g_amendExp = LevelEXP.AmendExp.instance()

g_spacedata = Resource.SpaceData.g_spacedata
g_transporterData = Resource.TransporterData.g_transporterData

# penghuawei in 2005-07-29, 这个似乎只能放在最后。
from Resource.QuestLoader import QuestsFlyweight
g_taskData = QuestsFlyweight.instance()
g_taskData.load( "config/quest/" )	# 初始化数据

from ChatProfanity import chatProfanity as g_chatProfanity
g_chatProfanity.initialize()

from Resource.TreasurePositions import TreasurePositions
g_TreasurePositions = TreasurePositions.instance()		# 藏宝图位置坐标

from Resource.BigWorldLevelMaps import BigWorldLevelMaps
g_BigWorldLevelMaps = BigWorldLevelMaps.instance()		# 世界地图对应的怪物级别信息

from Resource.MonsterActivityMgr import MonsterActivityMgr
#保留怪物活动需要数据配置接口

# wsf:帮会奖励配置11:08 2009-1-8
from Resource.TongFeteDataLoader import TongFeteDataLoader
TongFeteDataLoader.instance().load( "config/server/TongFeteReward.xml" )

# NPC位置数据
from config.NPCDatas import NPCDatas
g_NPCsPosition = NPCDatas.cellDatas

# 徒弟升级，级别对应的奖励
from Resource.TeachCreditLoader import TeachCreditLoader
g_teachCreditLoader = TeachCreditLoader.instance()

g_questQuestionSection = Language.openConfigSection("config/server/QuestQuestion.xml")

g_ieQuestionSection = Language.openConfigSection("config/server/ImperialExaminations.xml")

# 活动快乐金蛋
from KuaiLeJinDan import KuaiLeJinDan
g_KuaiLeJinDan = KuaiLeJinDan.instance()

# 算卦占卜
from Resource.SuanGuaZhanBuLoader import SuanGuaZhanBuLoader
g_SuanGuaZhanBuLoader = SuanGuaZhanBuLoader.instance()
g_SuanGuaZhanBuLoader.load( "config/server/SuanGuaZhanBu.xml" )

# 统计模块
from Statistic import Statistic
g_Statistic = Statistic.instance()
g_Statistic.load( "config/server/questTypeStr.xml" )

# 等级限制流通物品
from config.item import LevelRestrainItems
g_levelResItems = LevelRestrainItems.Datas


# add reward configs by 姜毅
g_rewards.addRewardProj( "rewardsCfg.rwp" )

# 骑宠数据
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

# 副本组队系统资源加载
from CellSpaceCopyFormulas import spaceCopyFormulas
spaceCopyFormulas.loadCopiesData( "config/matchablecopies.xml" )

# 潜能乱斗怪物数据
from Resource.CopyPotentialMeleeLoader import CopyPotentialMeleeLoader
g_copyPotentialMeleeLoader = CopyPotentialMeleeLoader.instance()
g_copyPotentialMeleeLoader.initData()

#副本怪物死亡计数
from Resource.SpaceCopyCountLoader import SpaceCopyCountLoader
g_SpaceCopyCount = SpaceCopyCountLoader.instance()
g_SpaceCopyCount.initCnfData()

#副本复活点
from SpaceCopyReviveConfigLoader import SpaceCopyReviveConfigLoader
g_SpaceCopyReviveCfg = SpaceCopyReviveConfigLoader.instance()
g_SpaceCopyReviveCfg.initCnfData()

# 科举考试题库
from Resource.ImperialExaminationsLoader import g_imperialExaminationsLoader
g_imperialExaminationsLoader.load( "config/server/ImperialExaminations.xml" )  #5KB

# 棋盘事件
g_boardEventLoader = Resource.BoardEventLoader.g_boardEventLoader()
g_boardEventLoader.load( "config/server/BoardEvent.xml" )

g_rewardQuestLoader = RewardQuestLoader.instance()
g_rewardQuestLoader.initTimeAndProbilityData()
g_rewardQuestLoader.initQuestData()

# 陷阱音效
from Resource.TrapSoundsLoader import g_trapSoundsLoader
g_trapSoundsLoader.load( "config/server/TrapEntitySounds.xml" )

# 帮会技能
from TongDatas import tongSkill_instance
g_tongSkills = tongSkill_instance()

g_relationStaticMgr = RelationStaticModeMgr.instance()
g_relationStaticMgr.initCampRelationCfg()
g_relationStaticMgr.createRelationInstance()


# ----------------------
# 保证调用entity的一个方法
#-----------------------
GLOBAL_CALL_CELL_METHOD_KEY = "onCallEntityMedthod"

def callEntityMedthod( targetID, methodName, methodArgs ):
	"""
	远程调用一个cell entity方法
	当entity不在当前cell时，此方法会广播所有cell， 不是必要的尽量少用
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		method = getattr( e, methodName )
		method( *methodArgs )
	else:
		BigWorld.cellAppData[ GLOBAL_CALL_CELL_METHOD_KEY ] = ( targetID, methodName, methodArgs )

def onCallEntityMedthod( targetID, methodName, methodArgs ):
	"""
	远程调用一个cell entity方法的回调
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		method = getattr( e, methodName )
		method( *methodArgs )

# ----------------------
# 保证设置一个entity的值
#-----------------------
GLOBAL_SET_CELL_PRO_KEY		= "onSetEntityPro"

def setEntityPro( targetID, proName, proValue ):
	"""
	设置一个cell entity的值
	当entity不在当前cell时，此方法会广播所有cell， 不是必要的尽量少用
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		setattr( e, proName, proValue )
	else:
		BigWorld.cellAppData[ GLOBAL_SET_CELL_PRO_KEY ] = ( targetID, proName, proValue )

def onSetEntityPro( targetID, proName, proValue ):
	"""
	设置一个cell entity的值回调
	"""
	e = BigWorld.entities.get( targetID, None )
	if e and e.isReal():
		setattr( e, proName, proValue )

def onCellAppData( key, value ):
	"""
	BigWorld.cellAppData字典设置的回调
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
