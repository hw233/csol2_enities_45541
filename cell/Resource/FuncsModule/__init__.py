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
from FuncTongStorage import FuncTongStorage	# ���ֿ�
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
from FuncImperialExaminations import FuncImperialExamCheck		# ���ԡ����Կ��ٶԻ�
from FuncImperialExaminations import FuncImperialXHSignUpCheck	# ���Ի��Ա������
from FuncImperialExaminations import FuncImperialDSignUpCheck	# ���Ա������
from FuncImperialExaminations import FuncImperialHuiShiBuKao	# �ƾٻ��Բ���
from FuncImperialExaminations import FuncFetchIEReward			# ��ȡ�ƾٽ���(���ԡ�����)
from FuncMerchant import FuncMoneyToYinpiao
from FuncSetCityRevenueRate import FuncSetCityRevenueRate
from FuncTradeWithDarkTrader import FuncTradeWithDarkTrader
from FuncTongFeteExchange import FuncTongFeteExchange	# ���������黻��
from FuncTradeWithItemChapman import FuncTradeWithItemChapman	# ���������˶Ի�������Ʒ��ȡ��Ʒ��NPC��
from FuncTradeWithPointChapman import FuncTradeWithPointChapman	# ���������˶Ի�������Ʒ��ȡ��Ʒ��NPC��
from FuncCollectShell import *							# �ɼ�������صĶԻ�
from FuncAugury import FuncAugury						# ռ����ǩ����ضԻ�
from FuncBodyChange import *							# �����������ضԻ�
from FuncMerchantCharge import FuncMerchantCharge
from FuncAboutRanQuest import FuncReAcceptLoopQuest		# ���½�ȡ������
from FuncQuestNPCMonster import FuncQuestNPCMonster		# ��Ұ������ֶԻ�
from FuncTalkToQuestNPCMonster import FuncTalkToQuestNPCMonster
from FuncAboutRanQuest import FuncReadRanQuest			# ��ȡ����õĻ���������
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
from FuncOnlineBenefit import FuncOnlineBenefit			# �����ۼ�ʱ�佱��
from FuncOnlineBenefit import FuncOnlineBenefitCheck	# �����ۼ�ʱ�佱����ѯ
from FuncAnswer import FuncAnswer
from FuncGold import FuncChangeGoldToItem
from FuncKuaiLeJinDan import FuncKuaiLeJinDan
from FuncKuaiLeJinDan import FuncKuaiLeJinDanZuoQi
from FuncKuaiLeJinDan import FuncSuperKuaiLeJinDan
from FuncKuaiLeJinDan import FuncKuaiLeJinDanExpReward
from FuncTeamCompetition import FuncTeamCompetition
from FuncTeamCompetition import FuncTeamCompetitionRequest
from FuncQueryCityContestTongHistroy import FuncQueryCityContestTongHistroy
from FuncDance import *									# ���־���
from FuncShiTuGuanhuai import *							# ʦͽ�ػ���Ի�
from FuncHundun import FuncHundun						# ��������
from FuncHundun import FuncQueryJiFen					# ��ѯ����
from FuncHundun import FuncChangeJifen					# �һ�����
from FuncFishing import *								# ��ȡ����ʱ��Ի�
from FuncTianjiangqishou import FuncTianjiangqishou		# �콫����
# ����
from FuncDuDuzhu import FuncDuDuzhu
from FuncDuDuzhu import FuncDuDuzhuEasy
from FuncDuDuzhu import FuncDuDuzhuDifficulty
from FuncDuDuzhu import FuncDuDuzhuNightmare

from FuncDrawPresent import FuncDrawPresent				# ��ȡ�������
from FuncDrawPresent import FuncDrawPresentSingle				# һ����ȡһ�ݻ�ȡ�������
from FuncDrawSilverCoins import FuncDrawSilverCoins		# ��ȡ��Ԫ������
from FuncDrawAllPresnts import FuncDrawAllPresnts		# ��ȡ���н���
from FuncTestActivityGift import FuncTestActivityGift	#��⽱��
from FuncTestActivityGift import FuncTestWeekGift		#���ÿ��Ԫ������
from FuncTestActivityGift import FuncSpreaderGift		#�ƹ�Ա����
from FuncTestActivityGift import FuncTestQueryGift		# ��ѯ����
from FuncTestActivityGift import FuncQueryWeekOnlineTime		# ��ѯ��������ʱ��
from FuncTestActivityGift import FuncGetWeekOnlineTimeGift		# ��ȡ���ܹ���
from FuncTakeLingyao import FuncTakeLingyao						# ��ȡ��ҩ
from FuncTeamCompetitionReward import FuncTeamCompetitionReward # ��ȡ��Ӿ�������
from FuncAwardItems import FuncAwardItemsByAccount		# ͨ���˺Ż�ȡ��ҵ���Ʒ����
from FuncAwardItems import FuncAwardItemsByPlayerName	# ͨ��������ֻ�ȡ��ҵ���Ʒ����
from FuncAwardItems import FuncAwardItemsByOrder		# ͨ�������Ż�ȡ��ҵ���Ʒ����
from FuncAwardItems import FuncAwardItemsByANO		# ͨ�������š�����˻������ֻ�ȡ��ҵ���Ʒ����
from FuncTalkQuest import FuncTalkQuest
from FuncTalkQuest import FuncTalkRandomQuest
from FuncTalkQuest import FuncTalkRandomQuestWithAction
from FuncClose import FuncClose
from FuncCancelHoldFamilyNPC import FuncCancelHoldFamilyNPC
from FuncMultiRewardQuest import FuncMultiRewardQuest			# ��ȡ�౶����������
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
# а������
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXue
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXueEasy
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXueDefficulty
from FuncEnterXieLongDongXue import FuncEnterXieLongDongXueNightmare
# �⽣��
from FuncEnterFJSG import FuncEnterFJSG
from FuncEnterFJSG import FuncEnterFJSGEasy
from FuncEnterFJSG import FuncEnterFJSGDefficulty
from FuncEnterFJSG import FuncEnterFJSGNightmare
# �������
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
from FuncSpringRiddle import FuncSpringRiddle	# ���ڵ���
from FuncExp2Pot import FuncExp2Pot
from FuncTongSign import FuncTongSign
from FuncSpaceCopyChallenge import FuncSpaceCopyChallenge
from FuncSpaceCopyChallenge import FuncSpaceCopyChallengeThree
from FuncSpaceCopyChallenge import FuncSpaceCopyPiShanEnter
from FuncSpaceCopyChallenge import FuncSpaceCopyPiShanLevel
from FuncSpaceCopyChallenge import FuncSpaceCopyBaoXiangEnter
from FuncTriggerAIEventByDialog import FuncTriggerAIEventByDialog	#�Ի�����AI�¼�
from FuncTongCompetition import FuncCompetitionSignUp
from FuncCreateBootyMonsterForQuest import FuncCreateBootyMonsterForQuest
from FuncCopyConditionChange import FuncCopyConditionChange
from FuncSunBath import FuncEnterSunBath

from FuncYXLM import FuncEnterCopyYXYMEasy
from FuncYXLM import FuncEnterCopyYXYMDefficulty
from FuncYXLM import FuncEnterCopyYXYMNightmare
from FuncYXLM import FuncYXYMCloseSpace
from FuncYXLM import FuncBaoZangReqPVP	# ����Ӣ�����˸���PVP
from FuncYXLM import FuncBaoZangEnterPVP	# �������Ӣ�����˸���PVP


from FuncCampYingXiaongCopy import FuncCampYingXiaongEnter
from FuncCampYingXiaongCopy import FuncCampYingXiaongReq	# ����Ӣ�����˸���PVP

from FuncYXLMEquipTrade import FuncYXLMEquipTrade
from FuncSummonMonster import FuncSummonMonster
from FuncSetFollow import FuncSetFollow

# ���ϵͳ���
from FuncAlly import FuncAllyRequest			# ������
from FuncAlly import FuncAllyJoinNewMember	# �����³�Ա
from FuncAlly import FuncAllyChangeTitle		# ���Ľ�ݳƺ�
from FuncAlly import FuncQuitAlly				# �˳����

# ����ǿ�ƽ���
from FuncKigbagLock import FuncKitbagForceUnlock	# ����ǿ�ƽ���

# �ֿ�ǿ�ƽ���
from FuncBankLock import FuncBankForceUnlock		# �ֿ�ǿ�ƽ���

#�ı�NPCλ��
from FuncChangePosition import FuncChangePosition

from FuncGodWeapon import FuncGodWeapon	# ��������

from FuncTakeSilver import FuncTakeSilver #��ȡ��Ԫ��

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
from FuncCompletedQuest import FuncCompletedQuest						#�Ƿ������ĳ����
from FuncHasQuest import FuncHasQuest									#�Ƿ���ĳ������
from FuncCompleteQuestBySign import FuncCompleteQuestBySign				#�����Ƿ��б���������������
from FuncCompleteQuestWithItem import FuncCompleteQuestWithItem 		#������񣬲������һ����Ʒ
from FuncAbandonQuest import FuncAbandonQuest							#�Ի�����һ������
from FuncIncTaskState import FuncIncTaskState							#�Ի�����ĳ���������һ�������������Ƿ�����һ����������������þ�����

from FuncTongAba import FuncTongAbaRequest
from FuncTongAba import FuncTongAbaEnter

from FuncTongCityWarFashion import FuncTongCityWarFashionMember		# ����ս��ȡʱװ
from FuncTongCityWarFashion import FuncTongCityWarFashionChairman		# ����ս��ȡ����ʱװ
from FuncCityWarGetTongActionVal import FuncCityWarGetTongActionVal
from FuncSpellTarget import FuncSpellTarget

# С����Ի�
from FuncEidolonDirect import FuncEidolonDirect
from FuncEidolonLevelHelp import FuncEidolonLevelHelp
from FuncEidolonQueryHelp import FuncEidolonQueryHelp
from FuncEidolonVip import FuncVipTradeWithNPC			# vip���˽���
from FuncEidolonVip import FuncVipWarehouse				# vipǮׯ����
from FuncEidolonVip import FuncVipMail					# vip���书��
from FuncEidolonVip import FuncVipCheckConvert			# vip�Ի�����ת��
from FuncEidolonVip import FuncVipAcceptQuest			# ͨ���Ի���ȡ����
from FuncEidolonVip import FuncWithdrawEidolon			# �ջ�С����

from FuncDart import FuncDartPointQuery					# ���ڻ��ֲ�ѯ
from FuncDart import FuncDartSpaceInfoQuery				# ��ѯ��ǰ��ͼ�������ڳ�����

# �����̨
from FuncTeamChallenge import FuncTeamChallengeSignUp
from FuncTeamChallenge import FuncTeamChallengeGetReward
from FuncTeamChallenge import FuncTeamChallengeEnterSpace
from FuncTeamChallenge import FuncTeamChallengeSubstitute

# ��������
from FuncTowerDefense import FuncTowerDefenseEasy
from FuncTowerDefense import FuncTowerDefenseDefficulty
from FuncTowerDefense import FuncTowerDefenseNightmare

from FuncPlayVideo  import FuncPlayVideo

from FuncDrawSalary import FuncDrawSalary 				# ������ȡٺ»

# ����ս��
from FuncYeZhanFengQi import FuncYeZhanFengQi

# ���ս��
from FuncYiJieZhanChang import FuncYiJieZhanChang

# ��ᳵ��ս
from FuncTongTurnWar import FuncTongTurnWarSignUp

#�����ս������������죩
from FuncTongFengHuoLianTian import FuncTongFengHuoLianTian

#��Ӫ�������
from FuncCampFengHuoLianTian import FuncCampFengHuoLianTianSignUp
from FuncCampFengHuoLianTian import FuncEnterCampFengHuoLianTian

from FuncEndQuestTaskThenTeleport import FuncEndQuestTaskThenTeleport			#�Ƿ����ĳ�����������Ŀ��,����ٽ��д���
from FuncCheckLivingSkill import FuncCheckLivingSkill
from FuncTeleLevelCheck import FuncTeleLevelCheck
from FuncTongQuestStatus import FuncTongQuestStatus

# ������
from FuncAntiWallow import FuncCheckUsedWallow

# �����ֻظ���
from FuncEnterDestinyTrans import FuncEnterDestinyTransCommon
from FuncPlaySound import FuncPlaySound
from FuncPlaySound import FuncPlaySoundFromGender

#����ʱ��
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

#��ʾ�ڵ�
from FuncShowPatrol import FuncShowPatrol
from FuncTongBattleLeague import FuncTongBattleLeague	# ս������

from FuncCampTurnWar import FuncCampTurnWarSignUp
from FuncBuyTongSpecial import FuncBuyTongSpecial

# λ��ռ�
from FuncTeleportPlane import FuncTeleportPlane

# �����ս����
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

				"combinePet"			: FuncCombinePet,			# ����ϳ�
				"buyGem"				: FuncBuyGem,				# ������ʯ
				"procreatePet"			: FuncProcreatePet,			# ���ﷱֳ
				"getProcreatedPet"		: FuncGetProcreatedPet,		# ��ȡ��ֳ��ɳ���
				"hireStorage"			: FuncHireStorage,			# ���ó���С�ֿ�
				"openStorage"			: FuncOpenStorage,			# �򿪳���ֿ�

				"recordRandomQuest"		: FuncRecordRanQuest,		# �洢��������¼
				"cancelRandomQuest"		: FuncCancelRanQuest, 		# ȡ���������

				"level"					: FuncLevel,				# �ȼ��ж�
				"questStatus"			: FuncQuestStatu,			# ����״̬�ж�
				"questFailureCheck"		: FuncQuestFailureCheck,	# ����״̬�ж�
				"receiveMail" 			: FuncMail,					# �շ��ʼ�
				"registerRevivePoint"	: FuncRegRevivePoint,		# ������¼
				"equipMake"				: FuncEquipMake,			# װ������
				"changeFamilyName"	: FuncChangeFamilyName,			# �������
				"changeTongName"		: FuncChangeTongName,		# ������
				"openCreateTong"		: FuncOpenCreateTong,		# �򿪰�ᴴ������
				"cancelHoldFamilyNPC"	: FuncCancelHoldFamilyNPC,	# ȡ��ռ��ĳ������NPC
				"contestFamilyNPC"		: FuncContestFamilyNPC,		# �������NPC
				"queryFamilyNPC"		: FuncQueryFamilyNPC,		# ��ѯ����NPC
				"queryContestFamilyNPC"	: FuncQueryContestFamilyNPC,# ��ѯ�������NPC
				"getFamilyNPCMoney"		: FuncGetFamilyNPCMoney,	# ��ȡ����NPC�����
				"getFamilyNPCBuff"		: FuncGetFamilyNPCBuff,		# ��ȡ����NPC Buff
				"enterFamilyWar"		: FuncEnterFamilyWar,		# �������ս��
				"familyChallenge"		: FuncFamilyChallenge,		# ���������ս
				"tongAbaRequest"		: FuncTongAbaRequest,		# ��������̨��
				"tongAbaEnter"			: FuncTongAbaEnter,	    	# ���������̨��ս��
				"enterCityWar"			: FuncTongCityWarEnter,			# �������ս��
				"contestCity"			: FuncConstCityWar,			# ����������о���
				"commitCityWarQuest"	: FuncCommitCityWarQuest,	# �ύ����ս������
				"tongCityWarBuyLP"		: FuncTongCityWarBuyLP,		# ����ս��������
				"tongCityWarBuyXJ"		: FuncTongCityWarBuyXJ,		# ����ս��������
				"tongCityWarBuildTower"	: FuncTongCityWarBuildTower,# ����һ����¥
				"toBuildTongBuilding"	: FuncToBuildTongBuilding,	# �޽���Ὠ��
				"gotoTongTerritory"		: FuncGoToTongTerritory,	# ���ذ�����
				"gotoTongTerritoryPos"	: FuncTeleportTongPosition,	# ���������ָ��λ��
				"selectTongShenShou"	: FuncSelectTongShenShou,	# ѡ��������
				"requestRobWar"			: FuncRequestRobWar,		# �������Ӷ�ս
				"enterRobWarTerritory"	: FuncEnterRobWarTerritory,	# �������Ӷ�ս�Է�������
				"teachTongSkill"		: FuncTeachTongSkill,		# ѧϰ��Ἴ��
				"teachTongPetSkill"		: FuncTeachTongPetSkill,		# ѧϰ�����Ἴ��
				"clearTongSkill"		: FuncClearTongSkill,		# ������Ἴ��
				"researchTongSkill"		: FuncResearchTongSkill,	# �о���Ἴ��
				"researchTongPetSkill"		: FuncResearchTongPetSkill,	# �о������Ἴ��
				"makeTongItem"			: FuncMakeTongItem,			# ���������Ʒ
				"buyTongItem"			: FuncBuyTongItem,			# ��������Ʒ
				"tongStorage"			: FuncTongStorage,			# ���ֿ�
				"tongCampaignRaid"		: FuncTongCampaignRaid,		# ����ħ����Ϯ�
				"queryCityTong"			: FuncQueryCityTong,		# ��ѯռ����еİ��
				"queryCityContestTong"	: FuncQueryCityContestTong,	# ��ѯ��ǰ����������еİ��
				"queryCityContestTongHistroy" : FuncQueryCityContestTongHistroy,	# ��ѯ���ܾ���������еİ��
				"getCityTongItem"		: FuncGetCityTongItem,		# ��ȡ���ռ��������� �����ʵ
				"getCityTongChampion"	: FuncGetCityTongChampion,  # ��ȡ��ս�ھ�����
				"getCityTongChief"		: FuncGetCityTongChief, 	# ��ȡ��ս��������
				"getCityTongSkill"		: FuncGetCityTongSkill,		# ��ȡ���ռ��������� ����
				"getCityTongMoney"		: FuncGetCityTongMoney,		# ��ȡ���ռ��������� �����
				"abandonTongCity"	: FuncAbandonTongCity,			# ��������ռ��
				"requestTongFete"		: FuncRequestTongFete,		# ���������
				"teachPrentice"			: TeachPrentice,			# ��ͽ��
				"teachDisband"			: TeachDisband,				# ���ʦͽ��ϵ
				"teachSuccess"			: TeachSuccess,				# �ɹ���ʦ
				"enterPotentialMelee"	: FuncTeleportPotentialMelee,# ����Ǳ���Ҷ�����
				"rewardPotentialMelee"	: FuncPotentialMeleeReward, # Ǳ���Ҷ�����
				"enterExpMelee"			: FuncEnterExpMelee,		# ���뾭���Ҷ�����
				"teachQuery"			: TeachQueryTeachInfo,	# ��ѯʦͽ�б�
				"teachRegister"			: TeacherRegister,			# ע����ͽ
				"teachDeregister"		: TeacherDeregister,		# ע����ͽ
				"enterTeachKillMonsterCopy" :TeachKillMonsterCopyEnter,# ���������ɽ��ʦͽ������
				"talkToTeachCopyMonsterBoss":TeachKillMonsterCopyBossTalk,# ��ʦͽ����boss�Ի�
				"teachEverydayReward" : TeachEverydayReward,	# ʦͽÿ�ս���
				"exchangeTeachTitle" : TeachCreditChangeTitle,		# �һ�ʦ���ƺ�
				"prenticeRegister"		: PrenticeRegister,			# ע���ʦ
				"prenticeDeregister"	: PrenticeDeregister,		# ע����ʦ

				"marryRequest"			: MarryRequest,				# ������
				"divorceRequest"		: DivorceRequest,			# �������
				"findWeddingRing"		: FindWeddingRing,			# �һؽ���ָ
				"createTianguan"		: FuncCreateTianguan,		#
				"takeExpBuff"			: FuncTakeExpBuff,			# ��ȡ����BUFF
				"queryDoubleExpRemainTime": FuncQueryDoubleExpRemainTime, # �鿴˫������ʣ��ʱ��
				"resumeDoubleExpRemainTime" : FuncResumeDoubleExpRemainTime, #�ָ�˫������ʱ��
				"closeDoubleExpRemainTime" : FuncCloseDoubleExpRemainTime, #����˫������ʱ��
				"guessQuest"			: FuncGuess,				# ��ȭ
				"subQuestStatus"		: FuncSubQuestStatu,		# ���������״̬
				"dartReward"			: FuncDartReward,			# �ھ�ÿ�ܽ���
				"cancelDart"			: FuncCancelDartQuest,		# �����ھ�����
				"gotoDart"				: FuncGotoDart,				# ���ڳ�ȥ
				"lastReward"			: FuncLastReward,			# ��������
				"treasureMap"			: FuncTreasureMap,			# ��òر�ͼ��Ʒ
				"SignUpRacehorse"		: SignUpRacehorse,			# �μ�����
				"dartContidion"			: FuncDartCondition,		# ���̶Ի�����
				"teleToSunBath"			: FuncTeleToSunBath,		# �ƶ����չ�ԡ��ͼ
				"iExaminations"			: FuncImperialExaminations, # �ƾ�
				"FuncMoneyToYinpiao"	: FuncMoneyToYinpiao,
				"tradeWithDark"			: FuncTradeWithDarkTrader,	# �Ӻ������˴�������Ʒ
				"tongFeteExchange"		: FuncTongFeteExchange,		# ���������黻��
				"singUpWuDao"           : FuncSingUpWuDao,          # �μ�������
				"wuDaoGetReward"        : FuncWuDaoGetReward,       # ��ȡ������ھ�����
				"wuDaoEnterSapce"       : FuncWuDaoEnterSpace,      # ���������ḱ��
				"tradeWithItemChapman"	: FuncTradeWithItemChapman,	# ����Ʒ��ȡ��Ʒ�Ľ���
				"tradeWithPointChapman"	: FuncTradeWithPointChapman,# �û��ֻ�ȡ��Ʒ�Ľ���
				"augury"				: FuncAugury,				# ռ����ǩ
				"dragonCiFu"			: FuncCiFu,					# ������͸�
				"dragonXianLing"		: FuncXianLing,				# ������������
				"dragonJianZheng"		: FuncJianZheng,			# ������֤��Ե
				"pearlPrime"			: FuncPearlPrime,			# ��ȡ���龫��
				"imperialExamCheck"		: FuncImperialExamCheck,	# �ƾ����ԶԻ����
				"imperialXHSignUpCheck"	: FuncImperialXHSignUpCheck,# �ƾ����ԡ����Ա������
				"ieHuiShiBuKao"			: FuncImperialHuiShiBuKao,	# �ƾٻ��Բ���
				"imperialDSignUpCheck"	: FuncImperialDSignUpCheck,	# �ƾٵ��Ա������
				"loginBCGame"			: FuncLoginBCGame,			# �����μӱ������
				"gainBCReward"			: FuncBCReward,				# ��ȡ�����������
				"enterShenGuiMiJing"			: FuncEnterShenGuiMiJing,	# ��������ؾ����򵥣�
				"enterShenGuiMiJingEasy"		: FuncEnterShenGuiMiJingEasy,	# ��������ؾ����򵥣�
				"enterShenGuiMiJingDefficulty"	: FuncEnterShenGuiMiJingDefficulty,	# ��������ؾ������ѣ�
				"enterShenGuiMiJingNightmare" 	: FuncEnterShenGuiMiJingNightmare,	# ��������ؾ���ج�Σ�
				"enterWuYaoQianShao"			: FuncEnterWuYaoQianShao,	# ��������ǰ�ڣ��򵥣�
				"enterWuYaoQianShaoEasy"		: FuncEnterWuYaoQianShaoEasy,	# ��������ǰ�ڣ��򵥣�
				"enterWuYaoQianShaoDefficulty"	: FuncEnterWuYaoQianShaoDefficulty,	# ��������ǰ�ڣ����ѣ�
				"enterWuYaoQianShaoNightmare"	: FuncEnterWuYaoQianShaoNightmare,	# ��������ǰ�ڣ�ج�Σ�
				"enterWuYaoWangBaoZang"	: FuncEnterWuYaoWangBaoZang,# �������������أ��򵥣�
				"enterWuYaoWangBaoZangEasy"	: FuncEnterWuYaoWangBaoZangEasy,# �������������أ��򵥣�
				"enterWuYaoWangBaoZangDefficulty"	: FuncEnterWuYaoWangBaoZangDefficulty,# �������������أ����ѣ�
				"enterWuYaoWangBaoZangNightmare"	: FuncEnterWuYaoWangBaoZangNightmare,# �������������أ�ج�Σ�
				"suanGuaZhanBu"			: FuncSuanGuaZhanBu,		# ����ռ��
				"moneyToYinpiao"		: FuncMerchantCharge,		# ��ֵ��Ʊ
				"reAcceptLoopQuest"		: FuncReAcceptLoopQuest,	# ���½�ȡ������
				"questNPCMonsterTalk"	: FuncQuestNPCMonster,		# ��Ұ������ֶԻ�
				"talkToQuestNPCMonster"	: FuncTalkToQuestNPCMonster,	# ��Ұ������ֶԻ�������δ��ɶԻ���
				"enterShuijing"			: FuncShuijing,				# ����ˮ������
				"createTongRace"		: CreateTongRacehorse,		# �����������
				"enterTongRace"			: EnterTongRacehorse,		# ����������
				"racehorseRewardItem"	: FuncRacehorseRewardItem,	# ������Ʒ����
				"enterGumigong"			: FuncGumigong,				# ������ع�����
				"gumigongTalk"			: FuncGumigongQuestTalk,	# ���ع��Ի�
				"queryTongMoney"		: FuncQueryTongMoney,		# �鿴����ʽ�
				"onlineBenefit"			: FuncOnlineBenefit,		# �����ۼ�ʱ�佱��
				"onlineBenefitCheck"	: FuncOnlineBenefitCheck,	# �����ۼ�ʱ�佱����ѯ
				"readRanQuestRecord"	: FuncReadRanQuest,			# ��ȡ���滷��������
				"answer"				: FuncAnswer,				# �ش�����
				"fetchIEReward"			: FuncFetchIEReward,		# ��ȡ�ƾٽ���(���ԡ�����)
				"selEnterXinShouCun"	: FuncSelEnterXinShouCun,	# ѡ�����N�ߵ����ִ�
				"teleportFlyToPos"		: FuncTeleportFlyToPos,		# ���� �������ﴫ�͵İ汾
				"kuaiLeJinDan"			: FuncKuaiLeJinDan,			# ���ֽ𵰻
				"kuaiLeJinDanZuoQi"		: FuncKuaiLeJinDanZuoQi,	# ���ֽ����ｱ��
				"superKuaiLeJinDan"		: FuncSuperKuaiLeJinDan,	# ���ֽ𵰳����ҵ�
				"kuaiLeJinDanExpReward"	: FuncKuaiLeJinDanExpReward,# ���ֽ𵰾��齱��
				"openGoldChangeItem"	: FuncChangeGoldToItem,		# ��ʼ��Ԫ���һ���Ʒ����
				"shiTuReward"			: FuncShiTuReward,			# ʦͽ�ػ�������Ի�
				"shiTuChouJiang"		: FuncShiTuChouJiang,		# ʦͽ�ػ��齱
				"chuShiReward"			: FuncChuShiReward,			# ʦͽ�ػ���ʦ����(30����45��)
				"teamCompetitionRequest": FuncTeamCompetitionRequest,# ������Ӿ���
				"enterTeamCompetition"	: FuncTeamCompetition,		# ������Ӿ�������
				"enterProtectTong"		: FuncEnterProtectTong,		# ���뱣�����ɸ���
				"takeDanceBuff"			: FuncTakeDanceBuff,		# ��ȡ����ʱ��
				"freezeDanceBuff"		: FuncFreezeDanceBuff,		# ���ᾢ��ʱ��
				"resumeDanceBuff"		: FuncResumeDanceBuff,		# �ⶳ����ʱ��
				"queryDancePoint"		: FuncQueryDancePoint,		# ��ѯ�������
				"enterHundun"			: FuncHundun,				# ������縱��
				"fishingForFree"		: FuncFishingForFree,		# �����ȡ����ʱ��
				"fishingInCharge"		: FuncFishingInCharge,		# ���泡��������ȡ����ʱ��
				"enterTianjiangqishou"	: FuncTianjiangqishou,		# �����콵����
				"changeHundunJifen"		: FuncChangeJifen,			# �һ��������
				"queryHundunjifen"		: FuncQueryJiFen,			# ��ѯ�������
				"drawPresent"			: FuncDrawPresent,			# ��ȡ�������
				"drawPresentSingle"		: FuncDrawPresentSingle,	# һ����ȡһ�ݻ�ȡ�������
				"drawSilverCoins"		: FuncDrawSilverCoins,		# ��ȡ��Ԫ������
				"drawAllPresnts"		: FuncDrawAllPresnts,		# ��ȡ��Ԫ������
				"testActivityGift"		: FuncTestActivityGift,		# ��ղ��Խ���
				"testWeekGift"			: FuncTestWeekGift,			# ���ÿ��Ԫ������
				"takeLingyao"			: FuncTakeLingyao,			# ��ȡ��ҩ
				"getTeamCompetitionReward"	: FuncTeamCompetitionReward, 	# ��ȡ��Ӿ�������
				"spreaderGift"			: FuncSpreaderGift,			# �ƹ�Ա����
				"queryGift" 			: FuncTestQueryGift,		# ��ѯ����
				"queryWeekOnlineTime"	: FuncQueryWeekOnlineTime,	# ��ѯ��������ʱ��
				"getWeekOnlineTimeGift" : FuncGetWeekOnlineTimeGift,# ��ȡ���ܹ���
				"questTalk"				: FuncTalkQuest,			# �Ի�����
				"questRandomTalk"		: FuncTalkRandomQuest,		# ��Ի�����
				"questRandomTalkWA"		: FuncTalkRandomQuestWithAction, # ������Ի���������
				"enterDuDuZhu"			: FuncDuDuzhu,				# ��������
				"enterDuDuZhuEasy"		: FuncDuDuzhuEasy,			# ���������򵥣�
				"enterDuDuZhuDifficulty": FuncDuDuzhuDifficulty,	# �����������ѣ�
				"enterDuDuZhuNightmare"	: FuncDuDuzhuNightmare,		# ��������ج�Σ�
				"close"					: FuncClose,				# �رյ�ǰ�Ի�
				"openTongList"			: FuncOpenTongList,			# �򿪰���ѯ����
				"multiRewardQuest"		: FuncMultiRewardQuest,		# ��ȡ�౶��������
				"openTongADEditWindow"	: FuncOpenTongADEditWindow,	# �򿪰�������༭����
				"showGameRanking"		: FuncVieRanking,			# �����а����
				"getjackaroocardgift"	: FuncGetjackarooCardGift,	# ��ȡ���ֿ�����
				"leavePrison"			: FuncLeavePrison,			# �뿪����
				"prisonContribute"		: FuncPrisonContribute,		# ��������
				"enterYayu"				: FuncEnterYayu,			# ����m؅��ͼ
				"enterYayuEasy"			: FuncEnterYayuEasy,		# ����m؅��ͼ���򵥣�
				"enterYayuDefficulty"	: FuncEnterYayuDefficulty,	# ����m؅��ͼ�����ѣ�
				"enterYayuNightmare"	: FuncEnterYayuNightmare,	# ����m؅��ͼ��ج�Σ�
				"helpYayuBeginFight"	: FuncHelpYayu,				# �����m؅������ս��
				"yayuThanks"			: FuncYayuThanks,			# �m؅��ʾ��л
				"enterYayuNew"			: FuncEnterYayuNew,			# �����ªm؅��ͼ�����ѣ�
				"enterYayuNewDifficulty": FuncEnterYayuNewDifficulty,# �����ªm؅��ͼ�����ѣ�
				"enterYayuNewNightmare"	: FuncEnterYayuNewDifficulty,# �����ªm؅��ͼ��ج�Σ�
				"tongCityWarLeave"		: FuncTongCityWarLeave,		# �뿪����ս��
				"queryCityWarTable"		: FuncQueryCityWarTable,	# �鿴���̱�
				"gotoLastSpacePos"		: FuncGotoLastSpacePos,		# ���͵���һ����ͼ������ǰ��ͼ��λ��
				"sellPointCard"			: FuncSellPointCard,		# ���۵㿨
				"buyPointCard"			: FuncBuyPointCard,			# ����㿨
				"viewCityRevenue"		: FuncViewCityRevenue,		# �鿴����˰��
				"collectPoint"			: FuncCollectPoint, 		# ���ϲɼ���ɼ����� by ����
				"teachLivingSkill"		: FuncTeachLivingSkill, 	# ѧϰ����� by ����
				"checkLivingSkill"		: FuncCheckLivingSkill, 	# ���������Ƿ��Ѿ�ѧ�� by wuxo
				"enterXieLongDongXue"			: FuncEnterXieLongDongXue,			# ����а����Ѩ����
				"enterXieLongDongXueEasy"		: FuncEnterXieLongDongXueEasy,			# ����а����Ѩ�������򵥣�
				"enterXieLongDongXueDefficulty"	: FuncEnterXieLongDongXueDefficulty,	# ����а����Ѩ���������ѣ�
				"enterXieLongDongXueNightmare"	: FuncEnterXieLongDongXueNightmare,		# ����а����Ѩ������ج�Σ�
				"enterFJSGEasy"			: FuncEnterFJSGEasy,		# ����⽣�񹬸������򵥣�
				"enterFJSGDefficulty"	: FuncEnterFJSGDefficulty,	# ����⽣�񹬸��������ѣ�
				"enterFJSGNightmare"	: FuncEnterFJSGNightmare,	# ����⽣�񹬸�����ج�Σ�
				"enterFJSG"				: FuncEnterFJSG,			# ����⽣�񹬸���
				"changeAILeave"			: FuncChangeAILevel,		# �ı�AI����
				"enterSHMZ"				: FuncEnterShehunmizhen,			# ����������󸱱�
				"enterSHMZEasy"			: FuncEnterShehunmizhenEasy,		# ����������󸱱����򵥣�
				"enterSHMZDefficulty"	: FuncEnterShehunmizhenDefficulty,	# ����������󸱱������ѣ�
				"enterSHMZNightmare"	: FuncEnterShehunmizhenNightmare,	# ����������󸱱���ج�Σ�
				"chirstmasSocks"		: FuncChristmasSocks,		# ʥ������
				"setCityRevenueRate" 	: FuncSetCityRevenueRate, 	# ���ó�������˰��
				"touch"					: FuncTouch,				# �Ի�����
				"openDoor"				: FuncOpenDoor,				# �Ի�����
				"changeNPCToMonster"	: FuncChangeNPCToMonster,	# �Ի�����NPCΪ����
				"roleCompetition"		: FuncRoleCompetition,		# ���˾���
				"familyCompetition"		: FuncTongCompetition,		# ��Ὰ��
				"exp2Pot"				: FuncExp2Pot,				# ���黻Ǳ��
				"takeHonorGift"			: FuncTakeHonorGift,		# �����Ȼ���Ʒ
				"funcSpringRiddle" 		: FuncSpringRiddle,			# ���ڵ���
				"getTongRobWarPoint"	: FuncGetTongRobWarPoint,	# ��ȡ����Ӷ�ս����
				"queryTongRobWarPoint"	: FuncQueryTongRobWarPoint, # ��ѯ����Ӷ�ս����
				"contributeToTongMoney" : FuncContributeToTongMoney,# �����׽�Ǯ
				"tongSign"				: FuncTongSign,				# ����� by ����
				"allyRequest"			: FuncAllyRequest,			# ������
				"joinNewAllyMember"		: FuncAllyJoinNewMember,	# �����³�Ա
				"changeAllyTitle"		: FuncAllyChangeTitle,		# ���Ľ�ݳƺ�
				"quitAlly"				: FuncQuitAlly,				# �˳����
				"kitbagForceUnlock"		: FuncKitbagForceUnlock,	# ����ǿ�ƽ���
				"bankForceUnlock"		: FuncBankForceUnlock,		# �ֿ�ǿ�ƽ���
				"changeNPCPosition"		: FuncChangePosition,		# �ı�NPCλ��
				"awardItemsByAccount"	: FuncAwardItemsByAccount,	# ͨ���˺Ż�ȡ��ҵ���Ʒ����
				"awardItemsByPlayerName": FuncAwardItemsByPlayerName,# ͨ��������ֻ�ȡ��ҵ���Ʒ����
				"awardItemsByOrder"		: FuncAwardItemsByOrder,	# ͨ�������Ż�ȡ��ҵ���Ʒ����
				"awardItemsByANO"		: FuncAwardItemsByANO,	# ͨ�������š�����˻������ֻ�ȡ��ҵ���Ʒ����
				"godWeaponMake"			: FuncGodWeapon,			# ��������
				"takeSilver"			: FuncTakeSilver,			# ��ȡ��Ԫ��
				"tanabataQuiz"			: FuncTanabataQuiz,			# ��Ϧ�����ʴ�
				"openFeichengwurao" 	: FuncFeichengwurao,		# �򿪷ǳ����Ž���
				"getFruit"				: FuncGetFruit,				# ��ȡ��������
				"equipExtract"			: FuncEquipExtract,			# װ�����Գ�ȡ
				"equipPour"				: FuncEquipPour,			# װ�����Թ�ע
				"equipUp"				: FuncEquipUp,				# װ������
				"equipAttrRebuild"		: FuncEquipAttrRebuild,		# װ����������
				"enterRabbitRun"		: FuncRabbitRun,			# С�ÿ���
				"enterKuafuRemain"		: FuncKuafuRemain,			# �丸���
				"schemeTalk"			: FuncInScheme,				# �̶�ʱ��Ի�
				"enterBeforeNirvana"	: FuncBeforeNirvana,		# 10��������ǰ�����䡱
				"unfoldScroll"			: FuncUnfoldScroll, 		# 10��������չ������
				"kuafuBossTalk"			: FuncKuafuBossTalk,		# �丸������Ի�
				"isCompleteQuest"		: FuncCompletedQuest,		# �Ƿ������ĳ����
				"hasQuest"				: FuncHasQuest,				# �Ƿ���ĳ������
				"tongCityWarFashion"	: FuncTongCityWarFashionMember,		# ����ս��ȡʱװ
				"tongCityWarFashionLimit"	: FuncTongCityWarFashionChairman,	# ����ս��ȡ����ʱװ
				"tongCityWarGetTongActionVal" : FuncCityWarGetTongActionVal,	# ��ȡռ������е��ж�������
				"spellTarget"			: FuncSpellTarget,			# ��������Լ��������ʩ��
				"eidolonDirect"			: FuncEidolonDirect,		# ����ָ��
				"eidolonLevelHelp"		: FuncEidolonLevelHelp,		# ����ȼ�����
				"eidolonQueryHelp"		: FuncEidolonQueryHelp,		# �����ѯ����
				"vipTradeWithNPC"		: FuncVipTradeWithNPC,		# vip���˽���
				"vipWarehouse"			: FuncVipWarehouse,			# vipǮׯ����
				"vipMail"				: FuncVipMail,				# vip����
				"vipCheckConvert"		: FuncVipCheckConvert,		# vip�Ի�����ת��
				"vipAcceptQuest"		: FuncVipAcceptQuest,		# ͨ���Ի���ȡ����ȡ��vip��ԭ���ǣ�����ֻ��vip�Ի�ʱʹ�á�
				"withDrawEidolon"		: FuncWithdrawEidolon,		# �ջ�С����
				"dartPointQuery"		: FuncDartPointQuery,		# ���ڻ��ֲ�ѯ
				"dartSpaceInfoQuery"	: FuncDartSpaceInfoQuery,	# ��ѯ��ǰ��ͼ�������ڳ�����
				"enterFuBenChallenge"	: FuncSpaceCopyChallenge, 	# ������ս����
				"enterFuBenChallengeThree":FuncSpaceCopyChallengeThree, # ��������ģʽ����ս����
				"enterFuBenPiShan"		: FuncSpaceCopyPiShanEnter, # ������ɽ����
				"levelFuBenPiShan"		: FuncSpaceCopyPiShanLevel, # �˳���ɽ����
				"enterFuBenBaoXiang"	: FuncSpaceCopyBaoXiangEnter, # ���뱦�丱��
				"completeQuestBySign"	: FuncCompleteQuestBySign,	# �����Ƿ��б���������������
				"triggerAIEventByDialog": FuncTriggerAIEventByDialog, 	# �Ի�����AI�¼����öԻ�ѡ���ʾ��
				"completeQuestWithItem"	: FuncCompleteQuestWithItem,	# ������񣬲������һ����Ʒ
				"tongAbaReward"			: FuncTongAbaReward,		# �����̨����
				"teamChallengeSignUp"	: FuncTeamChallengeSignUp,	# �����̨����
				"teamChallengeReward"	: FuncTeamChallengeGetReward,	# �����̨����
				"teamChallengeEnter"	: FuncTeamChallengeEnterSpace,	# �����̨����
				"teamChallengeSubstitute" : FuncTeamChallengeSubstitute, # ���������̨�油����
				"playVideo"				: FuncPlayVideo,				# ������Ƶ
				"tongCompetitionSign"	: FuncCompetitionSignUp,		# ��Ὰ������
				"signUpRoleCompetition"	: FuncSignUpRoleCompetition,	# ���˾�������
				"createBootyMonsterForQuest" : FuncCreateBootyMonsterForQuest,	# Ϊӵ��ĳ���������Ҵ���һ��entity������ӵ�����entity��ս��Ʒ����Ȩ
				"abandonQuest"			: FuncAbandonQuest,			# ��������
				"incTaskState"			: FuncIncTaskState,	 		# �Ի�����ĳ���������һ�������������Ƿ�����һ����������������þ�����
				"tongDrawSalary"		: FuncDrawSalary,			# ������ȡٺ»
				"copyConditionChange"	: FuncCopyConditionChange,	# �Ի��������ڸ��������ı�
				"enterSunBath"			: FuncEnterSunBath,			# �������Ǹ���
				"enterYXLMEasy"			: FuncEnterCopyYXYMEasy,			# ����Ӣ������(1)
				"enterYXLMDefficulty"	: FuncEnterCopyYXYMDefficulty,		# ����Ӣ������(3)
				"enterYXLMNightmare"	: FuncEnterCopyYXYMNightmare,		# ����Ӣ������(5)
				"closeYXLMSpace"		: FuncYXYMCloseSpace, 				# �ر�Ӣ�����˸���
				"requestBaoZangPVPCopy"	: FuncBaoZangReqPVP,
				"enterBaoZangPVPCopy"	: FuncBaoZangEnterPVP,
				"readyCampYXC"			: FuncCampYingXiaongEnter,				# ��ӪӢ������׼��
				"SignUpCampYXC"			: FuncCampYingXiaongReq,				# ��ӪӢ����������
				"yxlmEquipTrade"		: FuncYXLMEquipTrade,				# Ӣ������NPCװ������
				"summonMonster"			: FuncSummonMonster,				# �ٻ�ĳһ���͵�Monster
				"setFollowID"			: FuncSetFollow,			# ���ø�����ID
				"enterTowerDefenseEasy" : FuncTowerDefenseEasy, 	#��������������ģʽ
				"enterTowerDefenseDefficulty" : FuncTowerDefenseDefficulty, 	#����������������ģʽ
				"enterTowerDefenseNightmare" : FuncTowerDefenseNightmare, 	#������������ج��ģʽ
				"isEndQuestTaskThenTeleport"	: FuncEndQuestTaskThenTeleport,			#�Ƿ����ĳ�����������Ŀ��
				"teleLevelCheck"	: FuncTeleLevelCheck,			# ��������ȼ��ж�
				"shuijingCallEntity"	: FuncShuijingCallEntity,			#ˮ�������Ի��ٻ����������ͬʱ��ʼ�ڶ���ˢ��
				"tongQuestStatus"	: FuncTongQuestStatus,			#�������״̬���
				"enterFengQiCopy"	: FuncYeZhanFengQi,				#�������ս��
				"signUpTongTurnWar"	: FuncTongTurnWarSignUp,		# ������ᳵ��ս
				"leaveShuijing"		: FuncLeaveShuijing,			#�˳�ˮ������
				"enterFengHuoLianTian"	: FuncTongFengHuoLianTian,		#��������ս������������죩
				"isCheckUsedWallow"		: FuncCheckUsedWallow,	# �Ƿ���δ����Ӱ��
				"enterDestinyTrans"		:FuncEnterDestinyTransCommon,	# ���������ֻظ���
				"playSound"				: FuncPlaySound,	# ����ָ��·������
				"dancePractice"			: FuncDancePractice, # ��������NPC��ϰ����
				"danceChallenge"		: FuncDanceChallenge, #��������NPC��ս����
				"playAction"			: FuncPlayAction,	#��������NPC�����赸����
				"aoZhanSignUp"		: FuncAoZhanSignUp, #��սȺ�ۻ����
				"aoZhanEnter"		: FuncAoZhanEnter, #��սȺ�ۻ����
				"isInSpace"				: FuncIsInSpace,	# �Ƿ���ĳ��ͼ
				"enterYiJieZhanChang"	: FuncYiJieZhanChang,			# �������ս��
				"openTongDartQuest"		: FuncOpenTongDartQuest,		# ���������������
				"openTongNormalQuest"	: FuncOpenTongNormalQuest,		# ��������ճ�����
				"showPatrol"	        : FuncShowPatrol,		#��ʾ�ڵ�·��
				"signUpCampTurnWar"	: FuncCampTurnWarSignUp,		# ������Ӫ����ս
				"battleLeague"			: FuncTongBattleLeague,		# ս������
				"teleportPlane"			: FuncTeleportPlane,		# ����λ��
				"buyTongSpecial" 	:FuncBuyTongSpecial,				#������������Ʒ
				"playSoundFromGender"	: FuncPlaySoundFromGender,	# �����Ա𲥷�ָ��·������
				"queryDanceExp"	:FuncQueryDanceExp,			#��ѯ�����о���
				"getDanceExp"	:FuncGetDanceExp,			#��ȡ�����о���
				"enterCityWarFinal":	 FuncTongCityWarFinalEnter,	# ��������ս����
				"campFengHuoSignUp"	: FuncCampFengHuoLianTianSignUp,	# ��Ӫ������챨��
				"campFengHuoEnter"	: FuncEnterCampFengHuoLianTian,		# ��Ӫ����������
				"cityWarBaseTeleport":FuncCityWarFinalBaseTeleport,		# �����ս�����ݵ㴫��
				"giveItemIfQualified"				:FuncGiveItemIfQualified,		# ������Ʒ�����ڲŸ�����Ʒ
				"spellTargetIfQualified"			:FuncSpellTargetIfQualified,	# ������Ʒ�����ڲŶ�����ͷż���
				"startPickAnima"			:FuncStartPickAnima,#ʰȡ�����淨��ʼ
				"stopPickAnima"			:FuncStopPickAnima,#ʰȡ�����淨����
			}
#
# $Log: not supported by cvs2svn $
# Revision 1.38  2008/08/20 00:53:10  kebiao
# �������ս���
#
# Revision 1.37  2008/08/05 06:31:44  zhangyuxing
# ���Ӳ�ȭ���ܣ����������״̬�ж�
#
# Revision 1.36  2008/08/01 08:11:42  zhangyuxing
# ������ tianguan - > enterTianguan
#
# Revision 1.35  2008/07/28 02:32:40  zhangyuxing
# ������ؽӿ�
#
# Revision 1.34  2008/07/25 03:17:17  kebiao
# no message
#
# Revision 1.33  2008/07/19 04:06:20  kebiao
# add FuncGetFamilyNPCMoney
#
# Revision 1.31  2008/07/18 06:22:49  kebiao
# add:
# 				"contestFamilyNPC"		: FuncContestFamilyNPC,		# �������NPC
# 				"queryFamilyNPC"		: FuncQueryFamilyNPC,		# ��ѯ����NPC
#
# Revision 1.30  2008/06/21 08:01:14  wangshufeng
# ����ʦͽϵͳ�ͷ���ϵͳnpc�Ի�����ѡ��
#
# Revision 1.29  2008/06/20 01:23:02  fangpengjun
# no message
#
# Revision 1.28  2008/06/19 07:49:11  fangpengjun
# ȥ���˳����ֿ�����
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
#     from Resource.NPCTalkLoader import NPCTalkLoader							# NPC�Ի����ñ�
#   File "entities/cell/Resource/NPCTalkLoader.py", line 7, in <module>
#     from Resource.DialogManager import DialogManager
#   File "entities/cell/Resource/DialogManager.py", line 10, in <module>
#     from DialogData import DialogData
#   File "entities/cell/Resource/DialogData.py", line 11, in <module>
#     from Resource.FuncsModule.Functions import Functions
#   File "entities/cell/Resource/FuncsModule/__init__.py", line 63
#     "openCreateTong"		: FuncOpenCreateTong		# �򿪰�ᴴ������
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
# ���ӹ���:equipMake
#
# Revision 1.21  2008/04/25 01:50:18  kebiao
# add FuncRegRevivePoint
#
# Revision 1.20  2008/03/06 09:12:27  fangpengjun
# ����ʼ�����ģ��FuncMail
#
# Revision 1.19  2008/02/05 02:50:42  zhangyuxing
# �޸ļ�BUG
#
# Revision 1.18  2008/01/31 05:17:53  zhangyuxing
# ��ӹ��ܣ� ����ȼ��ж� �� ����״̬�ж�
#
# Revision 1.17  2008/01/25 07:29:58  zhangyuxing
# no message
#
# Revision 1.16  2008/01/11 06:49:16  zhangyuxing
# no message
#
# Revision 1.15  2008/01/09 03:01:27  zhangyuxing
# ����FuncRecordRanQuest ��FuncReadRanQuestRecord ��������ѡ��
#
# Revision 1.14  2007/12/26 09:29:42  huangyongwei
# ����˳�����صĶԻ�����
#
# Revision 1.13  2007/10/29 04:17:10  yangkai
# ɾ���ˣ�
# - װ��ǿ������
# - ���Ϻϳɹ���
# - װ���ֽ⹦��
# - ���κϳɹ���
# - ����ʯ�ϳɹ���
#
# Revision 1.12  2007/06/14 00:39:14  kebiao
# ���Ϻϳ�
#
# Revision 1.11  2007/05/18 08:40:58  kebiao
# ��Ӹ�Ǯ����
#
# Revision 1.10  2007/05/10 02:28:55  panguankong
# ���funcTransporter����
#
# Revision 1.9  2007/04/05 09:37:02  panguankong
# ��ӣ�analyzeEquip
#
# Revision 1.8  2007/04/05 04:03:46  phw
# no message
#
# Revision 1.7  2007/04/05 03:58:23  phw
# merge:FuncMerge -> ornamentCompose:FuncOrnamentCompose
#
# Revision 1.6  2007/04/05 02:03:56  panguankong
# ��Ӳ��Ϻϳɹ���
#
# Revision 1.5  2007/03/30 08:43:54  phw
# ����FuncEquipIntensify�࣬���ڴ�װ��ǿ��
#
# Revision 1.4  2007/01/23 04:20:33  kebiao
# merge ֧��
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
