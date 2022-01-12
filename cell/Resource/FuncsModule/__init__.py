# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.39 2008-08-20 01:24:53 zhangyuxing Exp $

"""
"""
from FuncSell import FuncSell
from FuncBuy import FuncBuy
from FuncTeleport import FuncTeleport
from FuncViewCityRevenue import FuncViewCityRevenue
from FuncWarehouse import FuncWarehouse
from FuncLearn import FuncLearn
from FuncRaceclass import FuncRaceclass
from FuncTransporter import FuncTransporter
from FuncPayMoney import FuncPayMoney
from FuncTongCityWarReward import FuncGetCityTongMoney
from FuncTongCityWarReward import FuncGetCityTongItem
from FuncTongCityWarReward import FuncGetCityTongChampion
from FuncTongCityWarReward import FuncGetCityTongChief
from FuncAboutRanQuest import FuncRecordRanQuest
from FuncAboutRanQuest import FuncCancelRanQuest
from FuncLevel import FuncLevel
from FuncTeleportTongPosition import FuncTeleportTongPosition
from FuncQuestStatu import FuncQuestStatu
from FuncQuestFailureCheck import FuncQuestFailureCheck
from FuncTeleportPotentialMelee import FuncTeleportPotentialMelee
from FuncPotentialMeleeReward import FuncPotentialMeleeReward
from FuncEnterExpMelee import FuncEnterExpMelee
from FuncQueryCityWarTable import FuncQueryCityWarTable
from FuncAboutPet import FuncCombinePet
from FuncAboutPet import FuncBuyGem
from FuncAboutPet import FuncProcreatePet
from FuncAboutPet import FuncGetProcreatedPet
from FuncAboutPet import FuncHireStorage
from FuncAboutPet import FuncOpenStorage
from FuncTakeExpBuff import FuncTakeExpBuff
from FuncMail import FuncMail
from FuncRegRevivePoint import FuncRegRevivePoint
from FuncEquipMake import FuncEquipMake
from FuncQueryDoubleExpRemainTime import FuncQueryDoubleExpRemainTime
from FuncResumeDoubleExpRemainTime import FuncResumeDoubleExpRemainTime
from FuncCloseDoubleExpRemainTime import FuncCloseDoubleExpRemainTime
from FuncOpenCreateTong import FuncOpenCreateTong
from FuncContestFamilyNPC import FuncContestFamilyNPC
from FuncQueryFamilyNPC import FuncQueryFamilyNPC
from FuncGetFamilyNPCBuff import FuncGetFamilyNPCBuff
from FuncGetFamilyNPCMoney import FuncGetFamilyNPCMoney
from FuncEnterFamilyWar import FuncEnterFamilyWar
from FuncTongCityWar import FuncTongCityWarEnter
from FuncTongCityWar import FuncConstCityWar
from FuncTongCityWar import FuncTongCityWarLeave
from FuncTongCityWar import FuncAbandonTongCity
from FuncContributeToTongMoney import FuncContributeToTongMoney
from FuncFamilyChallenge import FuncFamilyChallenge
from FuncToBuildTongBuilding import FuncToBuildTongBuilding
from FuncCommitCityWarQuest import FuncCommitCityWarQuest
from FuncGoToTongTerritory import FuncGoToTongTerritory
from FuncSelectTongShenShou import FuncSelectTongShenShou
from FuncRequestRobWar import FuncRequestRobWar
from FuncTeachTongSkill import FuncTeachTongSkill
from FuncTeachTongSkill import FuncTeachTongPetSkill
from FuncClearTongSkill import FuncClearTongSkill
from FuncResearchTongSkill import FuncResearchTongSkill
from FuncResearchTongSkill import FuncResearchTongPetSkill
from FuncMakeTongItem import FuncMakeTongItem
from FuncBuyTongItem import FuncBuyTongItem
from FuncTongStorage import FuncTongStorage	# 帮会仓库
from FuncTongCampaignRaid import FuncTongCampaignRaid
from FuncQueryCityTong import FuncQueryCityTong
from FuncQueryCityContestTong import FuncQueryCityContestTong
from FuncGetCityTongSkill import FuncGetCityTongSkill
from FuncRequestTongFete import FuncRequestTongFete
from FuncTongCityWarBuyLP import FuncTongCityWarBuyLP
from FuncTongCityWarBuyXJ import FuncTongCityWarBuyXJ
from FuncTongCityWarBuildTower import FuncTongCityWarBuildTower
from FuncQueryContestFamilyNPC import FuncQueryContestFamilyNPC
from FuncTeach import TeachPrentice
from FuncTeach import TeachDisband
from FuncTeach import TeachSuccess
from FuncTeach import TeachQueryTeachInfo
from FuncTeach import TeacherRegister
from FuncTeach import TeacherDeregister
from FuncTeach import TeachKillMonsterCopyEnter
from FuncTeach import TeachKillMonsterCopyBossTalk
from FuncTeach import TeachEverydayReward
from FuncTeach import TeachCreditChangeTitle
from FuncTeach import PrenticeRegister
from FuncTeach import PrenticeDeregister

from FuncCouple import MarryRequest
from FuncCouple import DivorceRequest
from FuncCouple import FindWeddingRing
from FuncGetTongRobWarPoint import FuncGetTongRobWarPoint
from FuncQueryTongRobWarPoint import FuncQueryTongRobWarPoint
from FuncEnterRobWarTerritory import FuncEnterRobWarTerritory
from FuncSelEnterXinShouCun import FuncSelEnterXinShouCun
from FuncTianguan	import FuncCreateTianguan
from FuncTianguan	import FuncLastReward
from FuncTeleportFlyToPos import FuncTeleportFlyToPos
from FuncEnterProtectTong import FuncEnterProtectTong
from FuncGuess	import FuncGuess
from FuncSubQuestStatu	import FuncSubQuestStatu
from FuncDartReward import FuncDartReward
from FuncAboutDartQuest import FuncCancelDartQuest
from FuncAboutDartQuest import FuncGotoDart
from FuncTreasureMap import FuncTreasureMap
from FuncRacehorse import SignUpRacehorse
from FuncOpenTongList import FuncOpenTongList
from FuncWuDao import FuncSingUpWuDao
from FuncWuDao import FuncWuDaoGetReward
from FuncWuDao import FuncWuDaoEnterSpace
from FuncSuanGuaZhanBu import FuncSuanGuaZhanBu
from FuncEnterShenGuiMiJing import FuncEnterShenGuiMiJing
from FuncEnterShenGuiMiJing import FuncEnterShenGuiMiJingEasy
from FuncEnterShenGuiMiJing import FuncEnterShenGuiMiJingDefficulty
from FuncEnterShenGuiMiJing import FuncEnterShenGuiMiJingNightmare
from FuncEnterWuYaoQianShao import FuncEnterWuYaoQianShao
from FuncEnterWuYaoQianShao import FuncEnterWuYaoQianShaoEasy
from FuncEnterWuYaoQianShao import FuncEnterWuYaoQianShaoDefficulty
from FuncEnterWuYaoQianShao import FuncEnterWuYaoQianShaoNightmare
from FuncEnterWuYaoWangBaoZang import FuncEnterWuYaoWangBaoZang
from FuncEnterWuYaoWangBaoZang import FuncEnterWuYaoWangBaoZangEasy
from FuncEnterWuYaoWangBaoZang import FuncEnterWuYaoWangBaoZangDefficulty
from FuncEnterWuYaoWangBaoZang import FuncEnterWuYaoWangBaoZangNightmare
from FuncDartCondition import FuncDartCondition
from FuncTeleToSunBath import FuncTeleToSunBath
from FuncImperialExaminations import FuncImperialExaminations
from FuncImperialExaminations import FuncImperialExamCheck		# 乡试、会试考官对话
from FuncImperialExaminations import FuncImperialXHSignUpCheck	# 乡试会试报名检查
from FuncImperialExaminations import FuncImperialDSignUpCheck	# 殿试报名检查
from FuncImperialExaminations import FuncImperialHuiShiBuKao	# 科举会试补考
from FuncImperialExaminations import FuncFetchIEReward			# 领取科举奖励(会试、殿试)
from FuncMerchant import FuncMoneyToYinpiao
from FuncSetCityRevenueRate import FuncSetCityRevenueRate
from FuncTradeWithDarkTrader import FuncTradeWithDarkTrader
from FuncTongFeteExchange import FuncTongFeteExchange	# 帮会祭祀仙灵换物
from FuncTradeWithItemChapman import FuncTradeWithItemChapman	# 与特殊商人对话（用物品换取物品的NPC）
from FuncTradeWithPointChapman import FuncTradeWithPointChapman	# 与特殊商人对话（用物品换取物品的NPC）
from FuncCollectShell import *							# 采集贝壳相关的对话
from FuncAugury import FuncAugury						# 占卜抽签的相关对话
from FuncBodyChange import *							# 变身大赛的相关对话
from FuncMerchantCharge import FuncMerchantCharge
from FuncAboutRanQuest import FuncReAcceptLoopQuest		# 重新接取环任务
from FuncQuestNPCMonster import FuncQuestNPCMonster		# 与野外任务怪对话
from FuncTalkToQuestNPCMonster import FuncTalkToQuestNPCMonster
from FuncAboutRanQuest import FuncReadRanQuest			# 读取保存好的环任务数据
from FuncShuijing import FuncShuijing
from FuncShuijing import FuncShuijingCallEntity
from FuncShuijing import FuncLeaveShuijing
from FuncRacehorse import CreateTongRacehorse
from FuncRacehorse import EnterTongRacehorse
from FuncRacehorse import FuncRacehorseRewardItem
from FuncTongAba import FuncTongAbaReward
from FuncGumigong  import FuncGumigong
from FuncGumigong  import FuncGumigongQuestTalk
from FuncQueryTongMoney import FuncQueryTongMoney
from FuncOnlineBenefit import FuncOnlineBenefit			# 在线累计时间奖励
from FuncOnlineBenefit import FuncOnlineBenefitCheck	# 在线累计时间奖励查询
from FuncAnswer import FuncAnswer
from FuncGold import FuncChangeGoldToItem
from FuncKuaiLeJinDan import FuncKuaiLeJinDan
from FuncKuaiLeJinDan import FuncKuaiLeJinDanZuoQi
from FuncKuaiLeJinDan import FuncSuperKuaiLeJinDan
from FuncKuaiLeJinDan import FuncKuaiLeJinDanExpReward
from FuncTeamCompetition import FuncTeamCompetition
from FuncTeamCompetition import FuncTeamCompetitionRequest
from FuncQueryCityContestTongHistroy import FuncQueryCityContestTongHistroy
from FuncDance import *									# 快乐劲舞活动
from FuncShiTuGuanhuai import *							# 师徒关怀活动对话
from FuncHundun import FuncHundun						# 混沌入侵
from FuncHundun import FuncQueryJiFen					# 查询积分
from FuncHundun import FuncChangeJifen					# 兑换积分
from FuncFishing import *								# 换取钓鱼时间对话
from FuncTianjiangqishou import FuncTianjiangqishou		# 天将奇兽
# 嘟嘟猪
from FuncDuDuzhu import FuncDuDuzhu
from FuncDuDuzhu import FuncDuDuzhuEasy
from FuncDuDuzhu import FuncDuDuzhuDifficulty
from FuncDuDuzhu import FuncDuDuzhuNightmare

from FuncDrawPresent import FuncDrawPresent				# 获取活动的礼物
from FuncDrawPresent import FuncDrawPresentSingle				# 一次领取一份获取活动的礼物
from FuncDrawSilverCoins import FuncDrawSilverCoins		# 获取银元宝奖励
from FuncDrawAllPresnts import FuncDrawAllPresnts		# 获取所有奖励
from FuncTestActivityGift import FuncTestActivityGift	#封测奖励
from FuncTestActivityGift import FuncTestWeekGift		#封测每周元宝奖励
from FuncTestActivityGift import FuncSpreaderGift		#推广员奖励
from FuncTestActivityGift import FuncTestQueryGift		# 查询奖励
from FuncTestActivityGift import FuncQueryWeekOnlineTime		# 查询本周在线时间
from FuncTestActivityGift import FuncGetWeekOnlineTimeGift		# 领取上周工资
from FuncTakeLingyao import FuncTakeLingyao						# 领取灵药
from FuncTeamCompetitionReward import FuncTeamCompetitionReward # 领取组队竞赛奖励
from FuncAwardItems import FuncAwardItemsByAccount		# 通过账号获取玩家的物品奖励
from FuncAwardItems import FuncAwardItemsByPlayerName	# 通过玩家名字获取玩家的物品奖励
from FuncAwardItems import FuncAwardItemsByOrder		# 通过订单号获取玩家的物品奖励
from FuncAwardItems import FuncAwardItemsByANO		# 通过订单号、玩家账户、名字获取玩家的物品奖励
from FuncTalkQuest import FuncTalkQuest
from FuncTalkQuest import FuncTalkRandomQuest
from FuncTalkQuest import FuncTalkRandomQuestWithAction
from FuncClose import FuncClose
from FuncCancelHoldFamilyNPC import FuncCancelHoldFamilyNPC
from FuncMultiRewardQuest import FuncMultiRewardQuest			# 接取多倍奖励的任务
from FuncOpenTongADEditWindow import FuncOpenTongADEditWindow
from FuncVieRanking import FuncVieRanking
from FuncGetjackarooCardGift import FuncGetjackarooCardGift
from FuncLeavePrison import FuncLeavePrison
from FuncPrisonContribute import FuncPrisonContribute
from FuncYayu import FuncEnterYayu
from FuncYayu import FuncHelpYayu
from FuncYayu import FuncYayuThanks
from FuncYayu import FuncEnterYayuEasy
from FuncYayu import FuncEnterYayuDefficulty
from FuncYayu import FuncEnterYayuNightmare
from FuncYayuNew import FuncEnterYayuNew
from FuncYayuNew import FuncEnterYayuNewDifficulty
from FuncYayuNew import FuncEnterYayuNewNightmare
from FuncGotoLastSpacePos import FuncGotoLastSpacePos
from FuncPointCard import FuncBuyPointCard
from FuncPointCard import FuncSellPointCard
from FuncCollectPoint import FuncCollectPoint
from FuncTeachLivingSkill import FuncTeachLivingSkill
# 邪龙副本
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXue
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXueEasy
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXueDefficulty
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXueNightmare
# 封剑神宫
from FuncEnterFJSG import FuncEnterFJSG
from FuncEnterFJSG import FuncEnterFJSGEasy
from FuncEnterFJSG import FuncEnterFJSGDefficulty
from FuncEnterFJSG import FuncEnterFJSGNightmare
# 摄魂迷阵
from FuncEnterShehunmizhen import FuncEnterShehunmizhen
from FuncEnterShehunmizhen import FuncEnterShehunmizhenEasy
from FuncEnterShehunmizhen import FuncEnterShehunmizhenDefficulty
from FuncEnterShehunmizhen import FuncEnterShehunmizhenNightmare

from FuncChangeAILevel import *
from FuncChristmas import FuncChristmasSocks
from FuncChangeName import FuncChangeFamilyName
from FuncChangeName import FuncChangeTongName
from FuncRoleCompetition import FuncRoleCompetition
from FuncRoleCompetition import FuncSignUpRoleCompetition
from FuncTongCompetition import FuncTongCompetition
from FuncTouch import *
from FuncTouch import FuncOpenDoor
from FuncChangeNPCToMonster import FuncChangeNPCToMonster
from FuncTakeHonorGift import FuncTakeHonorGift
from FuncSpringRiddle import FuncSpringRiddle	# 春节灯谜
from FuncExp2Pot import FuncExp2Pot
from FuncTongSign import FuncTongSign
from FuncSpaceCopyChallenge import FuncSpaceCopyChallenge
from FuncSpaceCopyChallenge import FuncSpaceCopyChallengeThree
from FuncSpaceCopyChallenge import FuncSpaceCopyPiShanEnter
from FuncSpaceCopyChallenge import FuncSpaceCopyPiShanLevel
from FuncSpaceCopyChallenge import FuncSpaceCopyBaoXiangEnter
from FuncTriggerAIEventByDialog import FuncTriggerAIEventByDialog	#对话触发AI事件
from FuncTongCompetition import FuncCompetitionSignUp
from FuncCreateBootyMonsterForQuest import FuncCreateBootyMonsterForQuest
from FuncCopyConditionChange import FuncCopyConditionChange
from FuncSunBath import FuncEnterSunBath

from FuncYXLM import FuncEnterCopyYXYMEasy
from FuncYXLM import FuncEnterCopyYXYMDefficulty
from FuncYXLM import FuncEnterCopyYXYMNightmare
from FuncYXLM import FuncYXYMCloseSpace
from FuncYXLM import FuncBaoZangReqPVP	# 申请英雄联盟副本PVP
from FuncYXLM import FuncBaoZangEnterPVP	# 请求进入英雄联盟副本PVP


from FuncCampYingXiaongCopy import FuncCampYingXiaongEnter
from FuncCampYingXiaongCopy import FuncCampYingXiaongReq	# 申请英雄联盟副本PVP

from FuncYXLMEquipTrade import FuncYXLMEquipTrade
from FuncSummonMonster import FuncSummonMonster
from FuncSetFollow import FuncSetFollow

# 结拜系统相关
from FuncAlly import FuncAllyRequest			# 请求结拜
from FuncAlly import FuncAllyJoinNewMember	# 加入新成员
from FuncAlly import FuncAllyChangeTitle		# 更改结拜称号
from FuncAlly import FuncQuitAlly				# 退出结拜

# 背包强制解锁
from FuncKigbagLock import FuncKitbagForceUnlock	# 背包强制解锁

# 仓库强制解锁
from FuncBankLock import FuncBankForceUnlock		# 仓库强制解锁

#改变NPC位置
from FuncChangePosition import FuncChangePosition

from FuncGodWeapon import FuncGodWeapon	# 神器制造

from FuncTakeSilver import FuncTakeSilver #领取银元宝

from FuncTanabataQuiz import FuncTanabataQuiz
from FuncFeichengwurao import FuncFeichengwurao
from FuncGetFruit import FuncGetFruit
from FuncEquipExtract import FuncEquipExtract
from FuncEquipPour import FuncEquipPour
from FuncEquipUp import FuncEquipUp
from FuncEquipAttrRebuild import FuncEquipAttrRebuild
from FuncRabbitRun import FuncRabbitRun
from FuncKuafuRemain import FuncKuafuRemain
from FuncKuafuRemain import FuncKuafuBossTalk

from FuncInScheme import FuncInScheme
from FuncBeforeNirvana import FuncBeforeNirvana
from FuncUnfoldScroll import FuncUnfoldScroll
from FuncCompletedQuest import FuncCompletedQuest						#是否完成了某任务
from FuncHasQuest import FuncHasQuest									#是否有某个任务
from FuncCompleteQuestBySign import FuncCompleteQuestBySign				#根据是否有标记来决定任务完成
from FuncCompleteQuestWithItem import FuncCompleteQuestWithItem 		#完成任务，并给玩家一个物品
from FuncAbandonQuest import FuncAbandonQuest							#对话放弃一个任务
from FuncIncTaskState import FuncIncTaskState							#对话触发某个任务完成一步（至于任务是否因这一步而完成由任务配置决定）

from FuncTongAba import FuncTongAbaRequest
from FuncTongAba import FuncTongAbaEnter

from FuncTongCityWarFashion import FuncTongCityWarFashionMember		# 帮会城战领取时装
from FuncTongCityWarFashion import FuncTongCityWarFashionChairman		# 帮会城战领取限量时装
from FuncCityWarGetTongActionVal import FuncCityWarGetTongActionVal
from FuncSpellTarget import FuncSpellTarget

# 小精灵对话
from FuncEidolonDirect import FuncEidolonDirect
from FuncEidolonLevelHelp import FuncEidolonLevelHelp
from FuncEidolonQueryHelp import FuncEidolonQueryHelp
from FuncEidolonVip import FuncVipTradeWithNPC			# vip商人交易
from FuncEidolonVip import FuncVipWarehouse				# vip钱庄功能
from FuncEidolonVip import FuncVipMail					# vip邮箱功能
from FuncEidolonVip import FuncVipCheckConvert			# vip对话功能转换
from FuncEidolonVip import FuncVipAcceptQuest			# 通过对话接取任务。
from FuncEidolonVip import FuncWithdrawEidolon			# 收回小精灵

from FuncDart import FuncDartPointQuery					# 运镖积分查询
from FuncDart import FuncDartSpaceInfoQuery				# 查询当前地图发出的镖车数量

# 组队擂台
from FuncTeamChallenge import FuncTeamChallengeSignUp
from FuncTeamChallenge import FuncTeamChallengeGetReward
from FuncTeamChallenge import FuncTeamChallengeEnterSpace
from FuncTeamChallenge import FuncTeamChallengeSubstitute

# 塔防副本
from FuncTowerDefense import FuncTowerDefenseEasy
from FuncTowerDefense import FuncTowerDefenseDefficulty
from FuncTowerDefense import FuncTowerDefenseNightmare

from FuncPlayVideo  import FuncPlayVideo

from FuncDrawSalary import FuncDrawSalary 				# 帮众领取俸禄

# 凤栖战场
from FuncYeZhanFengQi import FuncYeZhanFengQi

# 异界战场
from FuncYiJieZhanChang import FuncYiJieZhanChang

# 帮会车轮战
from FuncTongTurnWar import FuncTongTurnWarSignUp

#帮会夺城战复赛（烽火连天）
from FuncTongFengHuoLianTian import FuncTongFengHuoLianTian

#阵营烽火连天
from FuncCampFengHuoLianTian import FuncCampFengHuoLianTianSignUp
from FuncCampFengHuoLianTian import FuncEnterCampFengHuoLianTian

from FuncEndQuestTaskThenTeleport import FuncEndQuestTaskThenTeleport			#是否完成某个任务的任务目标,完成再进行传送
from FuncCheckLivingSkill import FuncCheckLivingSkill
from FuncTeleLevelCheck import FuncTeleLevelCheck
from FuncTongQuestStatus import FuncTongQuestStatus

# 防沉迷
from FuncAntiWallow import FuncCheckUsedWallow

# 天命轮回副本
from FuncEnterDestinyTrans import FuncEnterDestinyTransCommon
from FuncPlaySound import FuncPlaySound
from FuncPlaySound import FuncPlaySoundFromGender

#劲舞时刻
from FuncDancing import FuncDancePractice
from FuncDancing import FuncDanceChallenge
from FuncDancing import FuncPlayAction
from FuncDancing import FuncQueryDanceExp
from FuncDancing import FuncGetDanceExp
from FuncAoZhanQunXiong import FuncAoZhanSignUp
from FuncAoZhanQunXiong import FuncAoZhanEnter
from FuncIsInSpace import FuncIsInSpace
from FuncOpenTongQuest import FuncOpenTongDartQuest
from FuncOpenTongQuest import FuncOpenTongNormalQuest

#显示摆点
from FuncShowPatrol import FuncShowPatrol
from FuncTongBattleLeague import FuncTongBattleLeague	# 战争结盟

from FuncCampTurnWar import FuncCampTurnWarSignUp
from FuncBuyTongSpecial import FuncBuyTongSpecial

# 位面空间
from FuncTeleportPlane import FuncTeleportPlane

# 帮会夺城战决赛
from FuncTongCityWarFinal import FuncTongCityWarFinalEnter
from FuncTongCityWarFinal import FuncCityWarFinalBaseTeleport

from FuncIfQualifiedDoSth import FuncGiveItemIfQualified
from FuncIfQualifiedDoSth import FuncSpellTargetIfQualified

from FuncPickAnima import FuncStartPickAnima
from FuncPickAnima import FuncStopPickAnima

m_functions= {
				"sell"					: FuncSell,					# no param
				"buy"					: FuncBuy,					# no param
				"teleport"				: FuncTeleport,				# spaceName, x, y, z, dx, dy, dz
				"warehouse"				: FuncWarehouse,			# no param
				"learn"					: FuncLearn,				# no param
				"raceclass"				: FuncRaceclass,			# RCMASK_*, raceclass
				"transporter"			: FuncTransporter, 			# no param
				"payMoney"				: FuncPayMoney,				# how money?

				"combinePet"			: FuncCombinePet,			# 宠物合成
				"buyGem"				: FuncBuyGem,				# 购买经验石
				"procreatePet"			: FuncProcreatePet,			# 宠物繁殖
				"getProcreatedPet"		: FuncGetProcreatedPet,		# 领取繁殖完成宠物
				"hireStorage"			: FuncHireStorage,			# 租用宠物小仓库
				"openStorage"			: FuncOpenStorage,			# 打开宠物仓库

				"recordRandomQuest"		: FuncRecordRanQuest,		# 存储随机任务记录
				"cancelRandomQuest"		: FuncCancelRanQuest, 		# 取消随机任务

				"level"					: FuncLevel,				# 等级判断
				"questStatus"			: FuncQuestStatu,			# 任务状态判断
				"questFailureCheck"		: FuncQuestFailureCheck,	# 任务状态判断
				"receiveMail" 			: FuncMail,					# 收发邮件
				"registerRevivePoint"	: FuncRegRevivePoint,		# 复活点记录
				"equipMake"				: FuncEquipMake,			# 装备制造
				"changeFamilyName"	: FuncChangeFamilyName,			# 家族改名
				"changeTongName"		: FuncChangeTongName,		# 帮会改名
				"openCreateTong"		: FuncOpenCreateTong,		# 打开帮会创建界面
				"cancelHoldFamilyNPC"	: FuncCancelHoldFamilyNPC,	# 取消占领某个家族NPC
				"contestFamilyNPC"		: FuncContestFamilyNPC,		# 争夺家族NPC
				"queryFamilyNPC"		: FuncQueryFamilyNPC,		# 查询家族NPC
				"queryContestFamilyNPC"	: FuncQueryContestFamilyNPC,# 查询争夺家族NPC
				"getFamilyNPCMoney"		: FuncGetFamilyNPCMoney,	# 收取家族NPC管理费
				"getFamilyNPCBuff"		: FuncGetFamilyNPCBuff,		# 收取家族NPC Buff
				"enterFamilyWar"		: FuncEnterFamilyWar,		# 进入家族战场
				"familyChallenge"		: FuncFamilyChallenge,		# 申请家族挑战
				"tongAbaRequest"		: FuncTongAbaRequest,		# 申请帮会擂台赛
				"tongAbaEnter"			: FuncTongAbaEnter,	    	# 申请进入擂台赛战场
				"enterCityWar"			: FuncTongCityWarEnter,			# 进入城市战场
				"contestCity"			: FuncConstCityWar,			# 申请争夺城市竞拍
				"commitCityWarQuest"	: FuncCommitCityWarQuest,	# 提交城市战场任务
				"tongCityWarBuyLP"		: FuncTongCityWarBuyLP,		# 城市战购买龙炮
				"tongCityWarBuyXJ"		: FuncTongCityWarBuyXJ,		# 城市战购买玄坚
				"tongCityWarBuildTower"	: FuncTongCityWarBuildTower,# 建造一座塔楼
				"toBuildTongBuilding"	: FuncToBuildTongBuilding,	# 修建帮会建筑
				"gotoTongTerritory"		: FuncGoToTongTerritory,	# 返回帮会领地
				"gotoTongTerritoryPos"	: FuncTeleportTongPosition,	# 进入帮会领地指定位置
				"selectTongShenShou"	: FuncSelectTongShenShou,	# 选择帮会神兽
				"requestRobWar"			: FuncRequestRobWar,		# 申请帮会掠夺战
				"enterRobWarTerritory"	: FuncEnterRobWarTerritory,	# 进入帮会掠夺战对方帮会领地
				"teachTongSkill"		: FuncTeachTongSkill,		# 学习帮会技能
				"teachTongPetSkill"		: FuncTeachTongPetSkill,		# 学习宠物帮会技能
				"clearTongSkill"		: FuncClearTongSkill,		# 遗忘帮会技能
				"researchTongSkill"		: FuncResearchTongSkill,	# 研究帮会技能
				"researchTongPetSkill"		: FuncResearchTongPetSkill,	# 研究宠物帮会技能
				"makeTongItem"			: FuncMakeTongItem,			# 生产帮会物品
				"buyTongItem"			: FuncBuyTongItem,			# 购买帮会物品
				"tongStorage"			: FuncTongStorage,			# 帮会仓库
				"tongCampaignRaid"		: FuncTongCampaignRaid,		# 申请魔物来袭活动
				"queryCityTong"			: FuncQueryCityTong,		# 查询占领城市的帮会
				"queryCityContestTong"	: FuncQueryCityContestTong,	# 查询当前竞争争夺城市的帮会
				"queryCityContestTongHistroy" : FuncQueryCityContestTongHistroy,	# 查询上周竞争争夺城市的帮会
				"getCityTongItem"		: FuncGetCityTongItem,		# 领取帮会占领城市利益 经验果实
				"getCityTongChampion"	: FuncGetCityTongChampion,  # 领取城战冠军奖励
				"getCityTongChief"		: FuncGetCityTongChief, 	# 领取城战帮主奖励
				"getCityTongSkill"		: FuncGetCityTongSkill,		# 领取帮会占领城市利益 技能
				"getCityTongMoney"		: FuncGetCityTongMoney,		# 领取帮会占领城市利益 管理费
				"abandonTongCity"	: FuncAbandonTongCity,			# 放弃城市占领
				"requestTongFete"		: FuncRequestTongFete,		# 申请帮会祭祀活动
				"teachPrentice"			: TeachPrentice,			# 收徒弟
				"teachDisband"			: TeachDisband,				# 解除师徒关系
				"teachSuccess"			: TeachSuccess,				# 成功出师
				"enterPotentialMelee"	: FuncTeleportPotentialMelee,# 进入潜能乱斗副本
				"rewardPotentialMelee"	: FuncPotentialMeleeReward, # 潜能乱斗奖励
				"enterExpMelee"			: FuncEnterExpMelee,		# 进入经验乱斗副本
				"teachQuery"			: TeachQueryTeachInfo,	# 查询师徒列表
				"teachRegister"			: TeacherRegister,			# 注册收徒
				"teachDeregister"		: TeacherDeregister,		# 注册收徒
				"enterTeachKillMonsterCopy" :TeachKillMonsterCopyEnter,# 进入凤鸣后山（师徒副本）
				"talkToTeachCopyMonsterBoss":TeachKillMonsterCopyBossTalk,# 和师徒副本boss对话
				"teachEverydayReward" : TeachEverydayReward,	# 师徒每日奖励
				"exchangeTeachTitle" : TeachCreditChangeTitle,		# 兑换师父称号
				"prenticeRegister"		: PrenticeRegister,			# 注册拜师
				"prenticeDeregister"	: PrenticeDeregister,		# 注销拜师

				"marryRequest"			: MarryRequest,				# 申请结婚
				"divorceRequest"		: DivorceRequest,			# 申请离婚
				"findWeddingRing"		: FindWeddingRing,			# 找回结婚戒指
				"createTianguan"		: FuncCreateTianguan,		#
				"takeExpBuff"			: FuncTakeExpBuff,			# 领取经验BUFF
				"queryDoubleExpRemainTime": FuncQueryDoubleExpRemainTime, # 查看双倍奖励剩余时间
				"resumeDoubleExpRemainTime" : FuncResumeDoubleExpRemainTime, #恢复双倍奖励时间
				"closeDoubleExpRemainTime" : FuncCloseDoubleExpRemainTime, #冻结双倍奖励时间
				"guessQuest"			: FuncGuess,				# 猜拳
				"subQuestStatus"		: FuncSubQuestStatu,		# 子任务完成状态
				"dartReward"			: FuncDartReward,			# 镖局每周奖励
				"cancelDart"			: FuncCancelDartQuest,		# 放弃镖局任务
				"gotoDart"				: FuncGotoDart,				# 到镖车去
				"lastReward"			: FuncLastReward,			# 天关最后奖励
				"treasureMap"			: FuncTreasureMap,			# 获得藏宝图物品
				"SignUpRacehorse"		: SignUpRacehorse,			# 参加赛马
				"dartContidion"			: FuncDartCondition,		# 跑商对话条件
				"teleToSunBath"			: FuncTeleToSunBath,		# 移动到日光浴地图
				"iExaminations"			: FuncImperialExaminations, # 科举
				"FuncMoneyToYinpiao"	: FuncMoneyToYinpiao,
				"tradeWithDark"			: FuncTradeWithDarkTrader,	# 从黑市商人处购买物品
				"tongFeteExchange"		: FuncTongFeteExchange,		# 帮会祭祀仙灵换物
				"singUpWuDao"           : FuncSingUpWuDao,          # 参加武道大会
				"wuDaoGetReward"        : FuncWuDaoGetReward,       # 领取武道大会冠军奖励
				"wuDaoEnterSapce"       : FuncWuDaoEnterSpace,      # 进入武道大会副本
				"tradeWithItemChapman"	: FuncTradeWithItemChapman,	# 用物品换取物品的交易
				"tradeWithPointChapman"	: FuncTradeWithPointChapman,# 用积分换取物品的交易
				"augury"				: FuncAugury,				# 占卜抽签
				"dragonCiFu"			: FuncCiFu,					# 祈求海神赐福
				"dragonXianLing"		: FuncXianLing,				# 祈求龙王显灵
				"dragonJianZheng"		: FuncJianZheng,			# 龙王见证情缘
				"pearlPrime"			: FuncPearlPrime,			# 吸取珍珠精华
				"imperialExamCheck"		: FuncImperialExamCheck,	# 科举乡试对话检查
				"imperialXHSignUpCheck"	: FuncImperialXHSignUpCheck,# 科举乡试、会试报名检查
				"ieHuiShiBuKao"			: FuncImperialHuiShiBuKao,	# 科举会试补考
				"imperialDSignUpCheck"	: FuncImperialDSignUpCheck,	# 科举殿试报名检查
				"loginBCGame"			: FuncLoginBCGame,			# 报名参加变身大赛
				"gainBCReward"			: FuncBCReward,				# 领取变身大赛奖励
				"enterShenGuiMiJing"			: FuncEnterShenGuiMiJing,	# 进入神鬼秘境（简单）
				"enterShenGuiMiJingEasy"		: FuncEnterShenGuiMiJingEasy,	# 进入神鬼秘境（简单）
				"enterShenGuiMiJingDefficulty"	: FuncEnterShenGuiMiJingDefficulty,	# 进入神鬼秘境（困难）
				"enterShenGuiMiJingNightmare" 	: FuncEnterShenGuiMiJingNightmare,	# 进入神鬼秘境（噩梦）
				"enterWuYaoQianShao"			: FuncEnterWuYaoQianShao,	# 进入巫妖前哨（简单）
				"enterWuYaoQianShaoEasy"		: FuncEnterWuYaoQianShaoEasy,	# 进入巫妖前哨（简单）
				"enterWuYaoQianShaoDefficulty"	: FuncEnterWuYaoQianShaoDefficulty,	# 进入巫妖前哨（困难）
				"enterWuYaoQianShaoNightmare"	: FuncEnterWuYaoQianShaoNightmare,	# 进入巫妖前哨（噩梦）
				"enterWuYaoWangBaoZang"	: FuncEnterWuYaoWangBaoZang,# 进入巫妖王宝藏（简单）
				"enterWuYaoWangBaoZangEasy"	: FuncEnterWuYaoWangBaoZangEasy,# 进入巫妖王宝藏（简单）
				"enterWuYaoWangBaoZangDefficulty"	: FuncEnterWuYaoWangBaoZangDefficulty,# 进入巫妖王宝藏（困难）
				"enterWuYaoWangBaoZangNightmare"	: FuncEnterWuYaoWangBaoZangNightmare,# 进入巫妖王宝藏（噩梦）
				"suanGuaZhanBu"			: FuncSuanGuaZhanBu,		# 算卦占卜
				"moneyToYinpiao"		: FuncMerchantCharge,		# 冲值银票
				"reAcceptLoopQuest"		: FuncReAcceptLoopQuest,	# 重新接取环任务
				"questNPCMonsterTalk"	: FuncQuestNPCMonster,		# 与野外任务怪对话
				"talkToQuestNPCMonster"	: FuncTalkToQuestNPCMonster,	# 与野外任务怪对话（任务未完成对话）
				"enterShuijing"			: FuncShuijing,				# 进入水晶副本
				"createTongRace"		: CreateTongRacehorse,		# 创建帮会赛马
				"enterTongRace"			: EnterTongRacehorse,		# 进入帮会赛马
				"racehorseRewardItem"	: FuncRacehorseRewardItem,	# 赛马物品奖励
				"enterGumigong"			: FuncGumigong,				# 进入古秘宫副本
				"gumigongTalk"			: FuncGumigongQuestTalk,	# 古秘宫对话
				"queryTongMoney"		: FuncQueryTongMoney,		# 查看帮会资金
				"onlineBenefit"			: FuncOnlineBenefit,		# 在线累计时间奖励
				"onlineBenefitCheck"	: FuncOnlineBenefitCheck,	# 在线累计时间奖励查询
				"readRanQuestRecord"	: FuncReadRanQuest,			# 读取保存环任务数据
				"answer"				: FuncAnswer,				# 回答问题
				"fetchIEReward"			: FuncFetchIEReward,		# 领取科举奖励(会试、殿试)
				"selEnterXinShouCun"	: FuncSelEnterXinShouCun,	# 选择进入N线的新手村
				"teleportFlyToPos"		: FuncTeleportFlyToPos,		# 传送 乘坐坐骑传送的版本
				"kuaiLeJinDan"			: FuncKuaiLeJinDan,			# 快乐金蛋活动
				"kuaiLeJinDanZuoQi"		: FuncKuaiLeJinDanZuoQi,	# 快乐金蛋坐骑奖励
				"superKuaiLeJinDan"		: FuncSuperKuaiLeJinDan,	# 快乐金蛋超级砸蛋
				"kuaiLeJinDanExpReward"	: FuncKuaiLeJinDanExpReward,# 快乐金蛋经验奖励
				"openGoldChangeItem"	: FuncChangeGoldToItem,		# 开始金元宝兑换物品界面
				"shiTuReward"			: FuncShiTuReward,			# 师徒关怀活动奖励对话
				"shiTuChouJiang"		: FuncShiTuChouJiang,		# 师徒关怀抽奖
				"chuShiReward"			: FuncChuShiReward,			# 师徒关怀出师奖励(30级和45级)
				"teamCompetitionRequest": FuncTeamCompetitionRequest,# 申请组队竞赛
				"enterTeamCompetition"	: FuncTeamCompetition,		# 进入组队竞赛副本
				"enterProtectTong"		: FuncEnterProtectTong,		# 进入保护帮派副本
				"takeDanceBuff"			: FuncTakeDanceBuff,		# 领取劲舞时刻
				"freezeDanceBuff"		: FuncFreezeDanceBuff,		# 冻结劲舞时刻
				"resumeDanceBuff"		: FuncResumeDanceBuff,		# 解冻劲舞时刻
				"queryDancePoint"		: FuncQueryDancePoint,		# 查询跳舞积分
				"enterHundun"			: FuncHundun,				# 进入混沌副本
				"fishingForFree"		: FuncFishingForFree,		# 免费领取钓鱼时间
				"fishingInCharge"		: FuncFishingInCharge,		# 用渔场垂钓卡换取钓鱼时间
				"enterTianjiangqishou"	: FuncTianjiangqishou,		# 进入天降奇兽
				"changeHundunJifen"		: FuncChangeJifen,			# 兑换混沌积分
				"queryHundunjifen"		: FuncQueryJiFen,			# 查询混沌积分
				"drawPresent"			: FuncDrawPresent,			# 获取活动的礼物
				"drawPresentSingle"		: FuncDrawPresentSingle,	# 一次领取一份获取活动的礼物
				"drawSilverCoins"		: FuncDrawSilverCoins,		# 获取银元宝奖励
				"drawAllPresnts"		: FuncDrawAllPresnts,		# 获取银元宝奖励
				"testActivityGift"		: FuncTestActivityGift,		# 封闭测试奖励
				"testWeekGift"			: FuncTestWeekGift,			# 封测每周元宝奖励
				"takeLingyao"			: FuncTakeLingyao,			# 领取灵药
				"getTeamCompetitionReward"	: FuncTeamCompetitionReward, 	# 领取组队竞赛奖励
				"spreaderGift"			: FuncSpreaderGift,			# 推广员奖励
				"queryGift" 			: FuncTestQueryGift,		# 查询奖励
				"queryWeekOnlineTime"	: FuncQueryWeekOnlineTime,	# 查询本周在线时间
				"getWeekOnlineTimeGift" : FuncGetWeekOnlineTimeGift,# 领取上周工资
				"questTalk"				: FuncTalkQuest,			# 对话任务
				"questRandomTalk"		: FuncTalkRandomQuest,		# 组对话任务
				"questRandomTalkWA"		: FuncTalkRandomQuestWithAction, # 组任务对话，带动作
				"enterDuDuZhu"			: FuncDuDuzhu,				# 进入嘟嘟猪
				"enterDuDuZhuEasy"		: FuncDuDuzhuEasy,			# 进入嘟嘟猪（简单）
				"enterDuDuZhuDifficulty": FuncDuDuzhuDifficulty,	# 进入嘟嘟猪（困难）
				"enterDuDuZhuNightmare"	: FuncDuDuzhuNightmare,		# 进入嘟嘟猪（噩梦）
				"close"					: FuncClose,				# 关闭当前对话
				"openTongList"			: FuncOpenTongList,			# 打开帮会查询界面
				"multiRewardQuest"		: FuncMultiRewardQuest,		# 领取多倍奖励任务
				"openTongADEditWindow"	: FuncOpenTongADEditWindow,	# 打开帮会宣传编辑窗口
				"showGameRanking"		: FuncVieRanking,			# 打开排行榜界面
				"getjackaroocardgift"	: FuncGetjackarooCardGift,	# 领取新手卡奖励
				"leavePrison"			: FuncLeavePrison,			# 离开监狱
				"prisonContribute"		: FuncPrisonContribute,		# 监狱捐献
				"enterYayu"				: FuncEnterYayu,			# 进入猰貐地图
				"enterYayuEasy"			: FuncEnterYayuEasy,		# 进入猰貐地图（简单）
				"enterYayuDefficulty"	: FuncEnterYayuDefficulty,	# 进入猰貐地图（困难）
				"enterYayuNightmare"	: FuncEnterYayuNightmare,	# 进入猰貐地图（噩梦）
				"helpYayuBeginFight"	: FuncHelpYayu,				# 帮助猰貐，进入战斗
				"yayuThanks"			: FuncYayuThanks,			# 猰貐表示感谢
				"enterYayuNew"			: FuncEnterYayuNew,			# 进入新猰貐地图（困难）
				"enterYayuNewDifficulty": FuncEnterYayuNewDifficulty,# 进入新猰貐地图（困难）
				"enterYayuNewNightmare"	: FuncEnterYayuNewDifficulty,# 进入新猰貐地图（噩梦）
				"tongCityWarLeave"		: FuncTongCityWarLeave,		# 离开城市战场
				"queryCityWarTable"		: FuncQueryCityWarTable,	# 查看赛程表
				"gotoLastSpacePos"		: FuncGotoLastSpacePos,		# 创送到上一个地图进来当前地图的位置
				"sellPointCard"			: FuncSellPointCard,		# 出售点卡
				"buyPointCard"			: FuncBuyPointCard,			# 购买点卡
				"viewCityRevenue"		: FuncViewCityRevenue,		# 查看城市税收
				"collectPoint"			: FuncCollectPoint, 		# 材料采集点采集材料 by 姜毅
				"teachLivingSkill"		: FuncTeachLivingSkill, 	# 学习生活技能 by 姜毅
				"checkLivingSkill"		: FuncCheckLivingSkill, 	# 检测生活技能是否已经学过 by wuxo
				"enterXieLongDongXue"			: FuncEnterXieLongDongXue,			# 进入邪龙洞穴副本
				"enterXieLongDongXueEasy"		: FuncEnterXieLongDongXueEasy,			# 进入邪龙洞穴副本（简单）
				"enterXieLongDongXueDefficulty"	: FuncEnterXieLongDongXueDefficulty,	# 进入邪龙洞穴副本（困难）
				"enterXieLongDongXueNightmare"	: FuncEnterXieLongDongXueNightmare,		# 进入邪龙洞穴副本（噩梦）
				"enterFJSGEasy"			: FuncEnterFJSGEasy,		# 进入封剑神宫副本（简单）
				"enterFJSGDefficulty"	: FuncEnterFJSGDefficulty,	# 进入封剑神宫副本（困难）
				"enterFJSGNightmare"	: FuncEnterFJSGNightmare,	# 进入封剑神宫副本（噩梦）
				"enterFJSG"				: FuncEnterFJSG,			# 进入封剑神宫副本
				"changeAILeave"			: FuncChangeAILevel,		# 改变AI级别
				"enterSHMZ"				: FuncEnterShehunmizhen,			# 进入摄魂迷阵副本
				"enterSHMZEasy"			: FuncEnterShehunmizhenEasy,		# 进入摄魂迷阵副本（简单）
				"enterSHMZDefficulty"	: FuncEnterShehunmizhenDefficulty,	# 进入摄魂迷阵副本（困难）
				"enterSHMZNightmare"	: FuncEnterShehunmizhenNightmare,	# 进入摄魂迷阵副本（噩梦）
				"chirstmasSocks"		: FuncChristmasSocks,		# 圣诞袜子
				"setCityRevenueRate" 	: FuncSetCityRevenueRate, 	# 设置城市消费税率
				"touch"					: FuncTouch,				# 对话触发
				"openDoor"				: FuncOpenDoor,				# 对话开门
				"changeNPCToMonster"	: FuncChangeNPCToMonster,	# 对话变身NPC为怪物
				"roleCompetition"		: FuncRoleCompetition,		# 个人竞技
				"familyCompetition"		: FuncTongCompetition,		# 帮会竞技
				"exp2Pot"				: FuncExp2Pot,				# 经验换潜能
				"takeHonorGift"			: FuncTakeHonorGift,		# 荣誉度换物品
				"funcSpringRiddle" 		: FuncSpringRiddle,			# 春节灯谜
				"getTongRobWarPoint"	: FuncGetTongRobWarPoint,	# 获取帮会掠夺战奖励
				"queryTongRobWarPoint"	: FuncQueryTongRobWarPoint, # 查询帮会掠夺战积分
				"contributeToTongMoney" : FuncContributeToTongMoney,# 帮会捐献金钱
				"tongSign"				: FuncTongSign,				# 帮会会标 by 姜毅
				"allyRequest"			: FuncAllyRequest,			# 请求结拜
				"joinNewAllyMember"		: FuncAllyJoinNewMember,	# 加入新成员
				"changeAllyTitle"		: FuncAllyChangeTitle,		# 更改结拜称号
				"quitAlly"				: FuncQuitAlly,				# 退出结拜
				"kitbagForceUnlock"		: FuncKitbagForceUnlock,	# 背包强制解锁
				"bankForceUnlock"		: FuncBankForceUnlock,		# 仓库强制解锁
				"changeNPCPosition"		: FuncChangePosition,		# 改变NPC位置
				"awardItemsByAccount"	: FuncAwardItemsByAccount,	# 通过账号获取玩家的物品奖励
				"awardItemsByPlayerName": FuncAwardItemsByPlayerName,# 通过玩家名字获取玩家的物品奖励
				"awardItemsByOrder"		: FuncAwardItemsByOrder,	# 通过订单号获取玩家的物品奖励
				"awardItemsByANO"		: FuncAwardItemsByANO,	# 通过订单号、玩家账户、名字获取玩家的物品奖励
				"godWeaponMake"			: FuncGodWeapon,			# 神器制造
				"takeSilver"			: FuncTakeSilver,			# 领取银元宝
				"tanabataQuiz"			: FuncTanabataQuiz,			# 七夕感情问答活动
				"openFeichengwurao" 	: FuncFeichengwurao,		# 打开非诚勿扰界面
				"getFruit"				: FuncGetFruit,				# 领取魅力种子
				"equipExtract"			: FuncEquipExtract,			# 装备属性抽取
				"equipPour"				: FuncEquipPour,			# 装备属性灌注
				"equipUp"				: FuncEquipUp,				# 装备飞升
				"equipAttrRebuild"		: FuncEquipAttrRebuild,		# 装备属性重铸
				"enterRabbitRun"		: FuncRabbitRun,			# 小兔快跑
				"enterKuafuRemain"		: FuncKuafuRemain,			# 夸父神殿
				"schemeTalk"			: FuncInScheme,				# 固定时间对话
				"enterBeforeNirvana"	: FuncBeforeNirvana,		# 10级副本“前世记忆”
				"unfoldScroll"			: FuncUnfoldScroll, 		# 10级副本中展开画卷
				"kuafuBossTalk"			: FuncKuafuBossTalk,		# 夸父神殿后卿对话
				"isCompleteQuest"		: FuncCompletedQuest,		# 是否完成了某任务
				"hasQuest"				: FuncHasQuest,				# 是否有某个任务
				"tongCityWarFashion"	: FuncTongCityWarFashionMember,		# 帮会城战领取时装
				"tongCityWarFashionLimit"	: FuncTongCityWarFashionChairman,	# 帮会城战领取限量时装
				"tongCityWarGetTongActionVal" : FuncCityWarGetTongActionVal,	# 获取占领帮会城市的行动力奖励
				"spellTarget"			: FuncSpellTarget,			# （由玩家自己）向玩家施法
				"eidolonDirect"			: FuncEidolonDirect,		# 精灵指引
				"eidolonLevelHelp"		: FuncEidolonLevelHelp,		# 精灵等级帮助
				"eidolonQueryHelp"		: FuncEidolonQueryHelp,		# 精灵查询帮助
				"vipTradeWithNPC"		: FuncVipTradeWithNPC,		# vip商人交易
				"vipWarehouse"			: FuncVipWarehouse,			# vip钱庄功能
				"vipMail"				: FuncVipMail,				# vip邮箱
				"vipCheckConvert"		: FuncVipCheckConvert,		# vip对话功能转换
				"vipAcceptQuest"		: FuncVipAcceptQuest,		# 通过对话接取任务，取名vip的原因是，建议只在vip对话时使用。
				"withDrawEidolon"		: FuncWithdrawEidolon,		# 收回小精灵
				"dartPointQuery"		: FuncDartPointQuery,		# 运镖积分查询
				"dartSpaceInfoQuery"	: FuncDartSpaceInfoQuery,	# 查询当前地图发出的镖车数量
				"enterFuBenChallenge"	: FuncSpaceCopyChallenge, 	# 进入挑战副本
				"enterFuBenChallengeThree":FuncSpaceCopyChallengeThree, # 进入三人模式的挑战副本
				"enterFuBenPiShan"		: FuncSpaceCopyPiShanEnter, # 进入劈山副本
				"levelFuBenPiShan"		: FuncSpaceCopyPiShanLevel, # 退出劈山副本
				"enterFuBenBaoXiang"	: FuncSpaceCopyBaoXiangEnter, # 进入宝箱副本
				"completeQuestBySign"	: FuncCompleteQuestBySign,	# 根据是否有标记来决定完成任务
				"triggerAIEventByDialog": FuncTriggerAIEventByDialog, 	# 对话触发AI事件（该对话选项不显示）
				"completeQuestWithItem"	: FuncCompleteQuestWithItem,	# 完成任务，并给玩家一个物品
				"tongAbaReward"			: FuncTongAbaReward,		# 帮会擂台奖励
				"teamChallengeSignUp"	: FuncTeamChallengeSignUp,	# 组队擂台报名
				"teamChallengeReward"	: FuncTeamChallengeGetReward,	# 组队擂台奖励
				"teamChallengeEnter"	: FuncTeamChallengeEnterSpace,	# 组队擂台进入
				"teamChallengeSubstitute" : FuncTeamChallengeSubstitute, # 加入组队擂台替补名单
				"playVideo"				: FuncPlayVideo,				# 播放视频
				"tongCompetitionSign"	: FuncCompetitionSignUp,		# 帮会竞技报名
				"signUpRoleCompetition"	: FuncSignUpRoleCompetition,	# 个人竞技报名
				"createBootyMonsterForQuest" : FuncCreateBootyMonsterForQuest,	# 为拥有某个任务的玩家创建一个entity，并且拥有这个entity的战利品所有权
				"abandonQuest"			: FuncAbandonQuest,			# 放弃任务
				"incTaskState"			: FuncIncTaskState,	 		# 对话触发某个任务完成一步（至于任务是否因这一步而完成由任务配置决定）
				"tongDrawSalary"		: FuncDrawSalary,			# 帮众领取俸禄
				"copyConditionChange"	: FuncCopyConditionChange,	# 对话触发所在副本条件改变
				"enterSunBath"			: FuncEnterSunBath,			# 进入土星副本
				"enterYXLMEasy"			: FuncEnterCopyYXYMEasy,			# 进入英雄联盟(1)
				"enterYXLMDefficulty"	: FuncEnterCopyYXYMDefficulty,		# 进入英雄联盟(3)
				"enterYXLMNightmare"	: FuncEnterCopyYXYMNightmare,		# 进入英雄联盟(5)
				"closeYXLMSpace"		: FuncYXYMCloseSpace, 				# 关闭英雄联盟副本
				"requestBaoZangPVPCopy"	: FuncBaoZangReqPVP,
				"enterBaoZangPVPCopy"	: FuncBaoZangEnterPVP,
				"readyCampYXC"			: FuncCampYingXiaongEnter,				# 阵营英雄王座准备
				"SignUpCampYXC"			: FuncCampYingXiaongReq,				# 阵营英雄王座报名
				"yxlmEquipTrade"		: FuncYXLMEquipTrade,				# 英雄联盟NPC装备交易
				"summonMonster"			: FuncSummonMonster,				# 召唤某一类型的Monster
				"setFollowID"			: FuncSetFollow,			# 设置跟随者ID
				"enterTowerDefenseEasy" : FuncTowerDefenseEasy, 	#进入塔防副本简单模式
				"enterTowerDefenseDefficulty" : FuncTowerDefenseDefficulty, 	#进入塔防副本困难模式
				"enterTowerDefenseNightmare" : FuncTowerDefenseNightmare, 	#进入塔防副本噩梦模式
				"isEndQuestTaskThenTeleport"	: FuncEndQuestTaskThenTeleport,			#是否完成某个任务的任务目标
				"teleLevelCheck"	: FuncTeleLevelCheck,			# 传送需求等级判断
				"shuijingCallEntity"	: FuncShuijingCallEntity,			#水晶副本对话召唤出多个怪物同时开始第二关刷怪
				"tongQuestStatus"	: FuncTongQuestStatus,			#帮会任务状态检测
				"enterFengQiCopy"	: FuncYeZhanFengQi,				#进入凤栖战场
				"signUpTongTurnWar"	: FuncTongTurnWarSignUp,		# 报名帮会车轮战
				"leaveShuijing"		: FuncLeaveShuijing,			#退出水晶副本
				"enterFengHuoLianTian"	: FuncTongFengHuoLianTian,		#进入帮会夺城战复赛（烽火连天）
				"isCheckUsedWallow"		: FuncCheckUsedWallow,	# 是否受未沉迷影响
				"enterDestinyTrans"		:FuncEnterDestinyTransCommon,	# 进入天命轮回副本
				"playSound"				: FuncPlaySound,	# 播放指定路径语音
				"dancePractice"			: FuncDancePractice, # 舞厅副本NPC练习斗舞
				"danceChallenge"		: FuncDanceChallenge, #舞厅副本NPC挑战斗舞
				"playAction"			: FuncPlayAction,	#舞厅副本NPC播放舞蹈动作
				"aoZhanSignUp"		: FuncAoZhanSignUp, #鏖战群雄活动报名
				"aoZhanEnter"		: FuncAoZhanEnter, #鏖战群雄活动进入
				"isInSpace"				: FuncIsInSpace,	# 是否处于某地图
				"enterYiJieZhanChang"	: FuncYiJieZhanChang,			# 进入异界战场
				"openTongDartQuest"		: FuncOpenTongDartQuest,		# 开启帮会运镖任务
				"openTongNormalQuest"	: FuncOpenTongNormalQuest,		# 开启帮会日常任务
				"showPatrol"	        : FuncShowPatrol,		#显示摆点路径
				"signUpCampTurnWar"	: FuncCampTurnWarSignUp,		# 报名阵营车轮战
				"battleLeague"			: FuncTongBattleLeague,		# 战争结盟
				"teleportPlane"			: FuncTeleportPlane,		# 传送位面
				"buyTongSpecial" 	:FuncBuyTongSpecial,				#购买帮会特殊商品
				"playSoundFromGender"	: FuncPlaySoundFromGender,	# 根据性别播放指定路径语音
				"queryDanceExp"	:FuncQueryDanceExp,			#查询舞厅中经验
				"getDanceExp"	:FuncGetDanceExp,			#领取舞厅中经验
				"enterCityWarFinal":	 FuncTongCityWarFinalEnter,	# 进入帮会夺城战决赛
				"campFengHuoSignUp"	: FuncCampFengHuoLianTianSignUp,	# 阵营烽火连天报名
				"campFengHuoEnter"	: FuncEnterCampFengHuoLianTian,		# 阵营烽火连天进入
				"cityWarBaseTeleport":FuncCityWarFinalBaseTeleport,		# 帮会夺城战决赛据点传送
				"giveItemIfQualified"				:FuncGiveItemIfQualified,		# 所有物品不存在才给与物品
				"spellTargetIfQualified"			:FuncSpellTargetIfQualified,	# 所有物品不存在才对玩家释放技能
				"startPickAnima"			:FuncStartPickAnima,#拾取灵气玩法开始
				"stopPickAnima"			:FuncStopPickAnima,#拾取灵气玩法结束
			}
#
# $Log: not supported by cvs2svn $
# Revision 1.38  2008/08/20 00:53:10  kebiao
# 加入城市战相关
#
# Revision 1.37  2008/08/05 06:31:44  zhangyuxing
# 增加猜拳功能，子任务完成状态判断
#
# Revision 1.36  2008/08/01 08:11:42  zhangyuxing
# 改名： tianguan - > enterTianguan
#
# Revision 1.35  2008/07/28 02:32:40  zhangyuxing
# 增加天关接口
#
# Revision 1.34  2008/07/25 03:17:17  kebiao
# no message
#
# Revision 1.33  2008/07/19 04:06:20  kebiao
# add FuncGetFamilyNPCMoney
#
# Revision 1.31  2008/07/18 06:22:49  kebiao
# add:
# 				"contestFamilyNPC"		: FuncContestFamilyNPC,		# 争夺家族NPC
# 				"queryFamilyNPC"		: FuncQueryFamilyNPC,		# 查询家族NPC
#
# Revision 1.30  2008/06/21 08:01:14  wangshufeng
# 加入师徒系统和夫妻系统npc对话功能选项
#
# Revision 1.29  2008/06/20 01:23:02  fangpengjun
# no message
#
# Revision 1.28  2008/06/19 07:49:11  fangpengjun
# 去掉了宠物大仓库租赁
#
# Revision 1.27  2008/06/19 07:33:23  fangpengjun
# no message
#
# Revision 1.26  2008/06/14 06:21:57  phw
# ERROR: EntityType::importEntityClass: Could not load module Role
# Traceback (most recent call last):
#   File "entities/cell/Role.py", line 39, in <module>
#     from Love3 import *
#   File "entities/cell/Love3.py", line 13, in <module>
#     from Resource.NPCTalkLoader import NPCTalkLoader							# NPC对话配置表
#   File "entities/cell/Resource/NPCTalkLoader.py", line 7, in <module>
#     from Resource.DialogManager import DialogManager
#   File "entities/cell/Resource/DialogManager.py", line 10, in <module>
#     from DialogData import DialogData
#   File "entities/cell/Resource/DialogData.py", line 11, in <module>
#     from Resource.FuncsModule.Functions import Functions
#   File "entities/cell/Resource/FuncsModule/__init__.py", line 63
#     "openCreateTong"		: FuncOpenCreateTong		# 打开帮会创建界面
#                    ^
# SyntaxError: invalid syntax
#
# Revision 1.25  2008/06/14 05:40:34  kebiao
# no message
#
# Revision 1.24  2008/06/05 02:01:13  kebiao
# add:FuncOpenCreateFamily
#
# Revision 1.23  2008/05/15 02:06:06  phw
# from FuncEquipMake import FuncEquipMake
#
# Revision 1.22  2008/05/15 02:05:01  phw
# 增加功能:equipMake
#
# Revision 1.21  2008/04/25 01:50:18  kebiao
# add FuncRegRevivePoint
#
# Revision 1.20  2008/03/06 09:12:27  fangpengjun
# 添加邮件功能模块FuncMail
#
# Revision 1.19  2008/02/05 02:50:42  zhangyuxing
# 修改简单BUG
#
# Revision 1.18  2008/01/31 05:17:53  zhangyuxing
# 多加功能， 处理等级判断 和 任务状态判断
#
# Revision 1.17  2008/01/25 07:29:58  zhangyuxing
# no message
#
# Revision 1.16  2008/01/11 06:49:16  zhangyuxing
# no message
#
# Revision 1.15  2008/01/09 03:01:27  zhangyuxing
# 增加FuncRecordRanQuest 和FuncReadRanQuestRecord 两个功能选项
#
# Revision 1.14  2007/12/26 09:29:42  huangyongwei
# 添加了宠物相关的对话函数
#
# Revision 1.13  2007/10/29 04:17:10  yangkai
# 删除了：
# - 装备强化功能
# - 材料合成功能
# - 装备分解功能
# - 首饰合成功能
# - 火云石合成功能
#
# Revision 1.12  2007/06/14 00:39:14  kebiao
# 材料合成
#
# Revision 1.11  2007/05/18 08:40:58  kebiao
# 添加付钱功能
#
# Revision 1.10  2007/05/10 02:28:55  panguankong
# 添加funcTransporter功能
#
# Revision 1.9  2007/04/05 09:37:02  panguankong
# 添加：analyzeEquip
#
# Revision 1.8  2007/04/05 04:03:46  phw
# no message
#
# Revision 1.7  2007/04/05 03:58:23  phw
# merge:FuncMerge -> ornamentCompose:FuncOrnamentCompose
#
# Revision 1.6  2007/04/05 02:03:56  panguankong
# 添加材料合成功能
#
# Revision 1.5  2007/03/30 08:43:54  phw
# 新增FuncEquipIntensify类，用于打开装备强化
#
# Revision 1.4  2007/01/23 04:20:33  kebiao
# merge 支持
#
# Revision 1.3  2006/02/28 08:13:07  phw
# no message
#
# Revision 1.2  2005/12/22 09:55:27  xuning
# no message
#
# Revision 1.1  2005/12/08 01:08:03  phw
# no message
#
#
