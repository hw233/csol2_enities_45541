# -*- coding: gb18030 -*-
#
# $Id: UIFactory.py,v 1.116 2008-09-02 10:09:49 fangpengjun Exp $

"""
implement root gui factory

2006.07.04: writen by huangyongwei
"""

# -----------------------------------------------------
# ���� UI�����۵�¼״̬����������״̬�������õ� UI ��
# -----------------------------------------------------
from guis.common.DragObject import DragObject
from guis.otheruis.LoadingGround import LoadingGround

# -----------------------------------------------------
# ��¼ UI���ڵ�¼��ʱ���Ҫ�õ��� UI��
# -----------------------------------------------------
from guis.loginuis.logindialog.LoginDialog import LoginDialog
from guis.loginuis.roleselector.RoleSelector import RoleSelector
from guis.loginuis.rolecreator.RoleCreator import RoleCreator
from guis.loginuis.campselector.CampSelector import CampSelector

# -----------------------------------------------------
# ����״̬ UI��ֻ����ҽ����������õ��� UI��
# -----------------------------------------------------
# ����״̬�µĳ��� UI�����һ��������Ϳ��Կ����� UI��
from guis.general.minimap.MiniMap import MiniMap
from guis.general.bigmap.BigMap import BigMap
from guis.general.playerinfo.PlayerInfo import PlayerInfo
from guis.general.chatwindow.ChatWindow import ChatWindow
from guis.general.quickbar.QuickBar import QuickBar
from guis.general.quickBar.QuickBar import SystemBar
from guis.general.quickbar.HideBar import HideBar

# ����״̬�µķǳ���ͨ�� UI����ҽ�������ʱ�������Կ����ģ����Ա���Ϊ�����õ� UI��
from guis.tooluis.passwordbox.PasswordWindow import PasswordWindow
from guis.tooluis.pickupbox.PickupBox import PickupBox
from guis.tooluis.pickupbox.PickupBox import PickupQuestBox

from guis.otheruis.FlyText import FlyTextDrive
from guis.otheruis.floatnames.NameFactory import NameFactory
from guis.otheruis.CenterMessage import CenterMessageController
from guis.general.targetinfo.TargetMgr import TargetMgr

# ����״̬�µķǳ������ UI����ҽ�������ʱ�������Կ����� UI��

from guis.general.helper.HelpWindow import HelpWindow
from guis.general.helper.CastIndicator import CastIndicator
#from guis.general.targetinfo.TargetInfo import TargetInfo
from guis.general.petswindow.vehiclepanel.VehicleInfo import VehicleInfo
from guis.general.teammateinfo.TeammateArray import TeammateArray
from guis.general.teammateinfo.TeamInfoWindow import TeamInfoWindow
from guis.general.playerprowindow.PlayProWindow import PlayProWindow
from guis.general.kitbag.KitBag import KitBag
from guis.general.kitbag.SplitBox import SplitBox
from guis.general.equipdurability.EquipDurability import EquipDurability
from guis.general.skilltree.SkillTree import SkillTree
from guis.general.skilllist.SkillList import SkillList
from guis.general.skilltrainer.SkillTrainer import SkillTrainer
from guis.general.questlist.QuestHelp import QuestHelp
from guis.general.questlist.RewardQuestList import RewardQuestList
from guis.general.bduffpanel.BDuffPanel import BDuffPanel
from guis.general.tradewindow.TradeWindow import TradeWindow as TradeWindow
from guis.general.tradewindow.TradeWindow import ItemChapmanTradeWindow
from guis.general.tradewindow.TradeWindow import PointChapmanTradeWindow

from guis.general.specialMerchantWnd.SpecialMerchantWnd import DarkMerchantWindow
from guis.general.specialMerchantWnd.SpecialMerchantWnd import SpecialMerchantWindow
from guis.general.specialMerchantWnd.SpecialMerchantWnd import DarkTradeWindow
from guis.general.specialMerchantWnd.LolTradeWnd import LolTradeWnd

from guis.general.npctalk.QuestTalkWindow import QuestTalkWindow as TalkingWindow
from guis.general.npctalk.NpcMsgWindow import NpcMsgWindow as NpcMsgWindow
from guis.general.npctalk.LevelUpAwardReminder import LevelUpAwardReminder
from guis.general.npctalk.GroupRewards import GroupRewards
from guis.general.npctalk.ArtiRefine import ArtiRefine
from guis.general.intonatebar.IntonateBar import IntonateBar
from guis.general.rolestrading.TradingWindow import TradingWindow	# ��ҽ��״���
from guis.general.pettrade.PetTrade import PetTrade
from guis.general.petswindow.aboutnpc.PetFoster import PetFoster
from guis.general.petswindow.aboutnpc.PetStorage import PetStorage
from guis.general.petswindow.aboutnpc.StorageTenancy import StorageTenancy

from guis.general.storewindow.StoreWindow import StoreWindow

from guis.general.relationship.RelationWindow import RelationWindow

from guis.general.petswindow.petinfo.PetInfo import PetInfo
from guis.general.petswindow.PetWindow import PetWindow
from guis.general.petswindow.EspialPet import EspialPet
from guis.general.petswindow.petpanel.PetEnhance import PetEnhance

#from guis.general.videosetting.VideoSetting import VideoSetting
#from guis.general.audiosetting.AudioSetting import AudioSetting
#from guis.general.shortcutsettingwindow.ShortcutSettingWindow import ShortcutSettingWindow

from guis.otheruis.entityResume.EntityResume import EntityResume

from guis.general.mailwindow.MailWindow import MailWindow

from guis.general.equipproduce.EquipProduce import EquipProduce

from guis.otheruis.StatusText import StatusTextController	#�Զ���ֺ��Զ�Ѱ·��ʾ��Ϣ�� 2007-10-23��gjx

from guis.general.vendwindow.sellwindow.SellWindow import VendSellWindow
from guis.general.vendwindow.buywindow.BuyWindow import VendBuyWindow
from guis.general.playerprowindow.EspialWindow import EspialWindow	#����۲�Է���UI
from guis.general.playerprowindow.EspialWindowRemote import EspialWindowRemote	#����Զ�̹۲�Է���UI

from guis.general.commissionsale.tishouwindow.sellwindow.TiShouSellWindow import TiShouSellWindow
from guis.general.commissionsale.tishouwindow.buywindow.TiShouBuyWindow import TiShouBuyWindow

from guis.general.commissionsale.pointcardwindow.PCBuyWindow import PCBuyWindow
from guis.general.commissionsale.pointcardwindow.PCSellWindow import PCSellWindow

from guis.general.specialshop.SpecialShop import SpecialShop

from guis.general.tongabout.StatWindow import StatWindow
from guis.general.tongabout.StatWindow import ReliveMsgBox
from guis.general.tongabout.StatWindow import ReliveMsgBoxAba
from guis.general.tongabout.StatWindow import ReviveTeamCompeteBox
from guis.general.tongabout.StatWindow import TipsPanel
from guis.general.tongabout.TongDetails import TongDetails
from guis.general.familychallenge.FCStatusWindow import FCStatusWindow

from guis.general.lottery.LotteryWindow import LotteryWindow

from guis.general.tongabout.ShenShouBeckon import ShenShouBeckon
from guis.general.tongabout.tongstorage.StorageWindow import StorageWindow
from guis.general.tongabout.TongMoney import TongMoneyGUI
from guis.general.tongabout.ApplyRobWar import ApplyRobWar
from guis.general.tongabout.TongQuery import TongQuery
from guis.general.tongabout.WarIntergral import WarIntergral
from guis.general.tongabout.WarRanking import WarRanking
#from guis.general.tongabout.WarFixture import WarFixture
from guis.general.tongabout.WarIntergral import MarkTips
from guis.general.tongabout.TongFixture import TongFixture
from guis.general.tongturnwar.TurnWarMatchWnd import TurnWarMatchWnd

from guis.general.activitycalendar.ActivityCalendar import ActivityCalendar

#from guis.general.searchmaster.SearchMaster import SearchMaster
#from guis.general.searchprentice.SearchPrenticeWindow import SearchPrenticeWindow
from guis.general.searchteach.SearchTeachWindow import SearchTeachWindow

from guis.general.knowledgeQandA.QandAWindow import QandAWindow
from guis.general.gamequiz.GameQuiz import GameQuizWnd
from guis.otheruis.CopySpaceInfo import CopySpaceInfo
from guis.otheruis.TeamPoints import TeamPoints
from guis.general.quickbar.RaceBar import RaceHorseDataPanel
from guis.tooluis.pickupbox.RollBox import RollsManager
from guis.general.rankwindow.RankWindow import RankWindow
from guis.tooluis.fixrewardbox.FixRewardBox import FixRewardBox
from guis.tooluis.emotionbox.EmotionBox import EmotionBox
from guis.general.spacecopy.SpaceCopyPlotLv40 import SpaceCopyPlotLv40
from guis.general.spacecopy.SpaceCopyLiuWangMuRank import SpaceCopyLiuWangMuRank
from guis.general.spacecopy.spaceCopyTBBattleRank.SpaceCopyTBBattleRank import SpaceCopyTBBattleRank
from guis.general.spacecopy.spaceCopyTBBattleRank.CopyTBBattleTransBox import CopyTBBattleTransBox
from guis.general.spacecopy.spaceCopyTBBattleRank.CopyTBBattleTransPanel import CopyTBBattleTransPanel
from guis.general.spacecopy.spaceCopyJueDiFanJi.CopyJueDiFanJiBox import CopyJueDiFanJiBox
from guis.general.spacecopy.spaceCopyJueDiFanJi.CopyJueDiFanJiResult import CopyJueDiFanJiResult
from guis.general.spacecopy.spaceCopyJueDiFanJi.CopyJueDiFanJiRank import CopyJueDiFanJiRank
from guis.general.highdance.HighDanceEntrance import HighDanceEntrance
from guis.general.highdance.HighDance import HighDance
from guis.general.spacecopy.spaceCopyAoZhan.CopyAoZhanBox import CopyAoZhanBox
from guis.general.spacecopy.spaceCopyAoZhan.CopyAoZhanSignUp import CopyAoZhanSignUp
from guis.general.spacecopy.spaceCopyAoZhan.CopyAoZhanRank import CopyAoZhanRank
from guis.general.spacecopy.spaceCopyAoZhan.CopyAoZhanResult import CopyAoZhanResult
from guis.general.spacecopy.spaceCopyYiJieZhanChang.YiJieSignUp import YiJieSignUp
from guis.general.spacecopy.spaceCopyYiJieZhanChang.AngerPoint import AngerPoint
from guis.general.spacecopy.spaceCopyYiJieZhanChang.YiJieScore import YiJieScore
from guis.general.spacecopy.spaceCopyYiJieZhanChang.YiJieBattleInfos import YiJieBattleInfos
from guis.general.spacecopy.tongsBattle.TongsAlliance import TongsAlliance

#from guis.general.eidolonwindow.EidolonWindow import EidolonWindow
from guis.general.tanabata.BulletinBoard import BulletinBoard
from guis.general.pixiewindow.PixieWindow import PixieWindow

from guis.general.challengecopy.ChallengeCopy import ChallengeCopy
from guis.general.quickbar.TriggerIndicator import TrigIntorMgr
from guis.general.copyteam.CopyTeamSys import CopyTeamSys
from guis.general.copyteam.CopyTeamNotify import FixedTeamNotify
from guis.general.minimap.LoLMiniMap import LoLMiniMap
from guis.general.lolpvp.RobotChoice import RobotChoice
from guis.general.lolpvp.RobotProperty import RobotProperty
from guis.general.lolpvp.PvPTeamWnd import PvPTeamWnd
from guis.general.yezhanfengqi.RankWindow import RankWindow as YeZhanRank

from guis.general.tongabout.FHLTRankWnd import FHLTRankWnd
from guis.general.tongabout.FHLTAgainst import FHLTAgainst
from guis.general.sermonsys.SermonWnd import SermonWnd
from guis.otheruis.HeadPortrait import PortraitDriver
from guis.general.destranscopy.DestransWnd import DestransWnd
from guis.general.tongabout.TongSpecialShop import TongSpecialShop

from guis.otheruis.SlotMachine import SlotMachine 
from guis.general.spaceCopy.spaceCopyCFHLT.CampFHLTRankWnd import CampFHLTRankWnd
from guis.general.spaceCopy.spaceCopyCFHLT.CampFHLTSign import CampFHLTSign


#from guis.general.syssetting.GameSetting import GameSetting

# --------------------------------------------------------------------
# ����ʽ���ڣ�ֻ�� import ���贴����
# --------------------------------------------------------------------
from guis.general.antirabotwindow.AntiRabotWindow import AntiRabotWindow
from guis.general.gamelogwindow.GameLogWindow import GameLogWindow
from guis.general.revivewindow.ReviveBox import ReviveBox
from guis.general.npctalk.Exp2PotWindow import Exp2PotWindow
from guis.general.tongabout.IconUploadWnd import IconUploadWnd
from guis.general.tongabout.IconChangeWnd import IconChangeWnd
from guis.general.familychallenge.ChallengeApplyWnd import ChallengeApplyWnd
from guis.general.quickbar.MasterSkBar import MasterSkBar
from guis.general.equipremake.EQExtractWnd import EQExtractWnd
from guis.general.equipremake.EQQualityUp import EQQualityUp
from guis.general.equipremake.EQPourWnd import EQPourWnd
from guis.general.equipremake.EQAttrRebuild import EQAttrRebuild
from guis.general.npctalk.RabbitQuest import RabbitQuest
from guis.general.ScenePlayer import ScenePlayer
from guis.tooluis import GlobalMenu
from guis.tooluis.helptips.UseTipWnd import UseTipWnd
from guis.general.petswindow.guardpanel.GuardCtrlWnd import GuardCtrlWnd
from guis.general.copyteam.CopyTeamConfirm import CopyTeamConfirm
from guis.general.copyteam.CopyTeamMatch import CopyTeamMatch
from guis.general.tongturnwar import CompetitionInfo
from guis.general.tongabout.FHLTRankWnd import FHLTTimer
from guis.general.tongabout.FHLTRankWnd import FHLTTips
from guis.general.yayutowers.YaYuTowers import YaYuTowers
from guis.general.sermonsys.TaoHeartWnd import TaoHeartWnd
from guis.general.sermonsys.ExchangeWnd import ExchangeWnd
from guis.general.fishing import ControlPanel
from guis.general.spaceCopy.spaceCopyCFHLT.CampFHLTRankWnd import CFHLTTips
from guis.otheruis.ReikiPick import ReikiPick

# --------------------------------------------------------------------
# usable imports
# --------------------------------------------------------------------
import inspect
import SmartImport
import reimpl_login
from cscollections import MapList
from AbstractTemplates import Singleton
from RootUIsMgr import ruisMgr
from UISounder import uiSounder
from guis.common.RootGUI import RootGUI


class UIFactory( Singleton ) :
	"""
	UI ���������ڴ�����Ϸ����Ҫ�����г�פ����
	ע�⣺�����ﴴ���� UI ���ǳ�פ�ڴ�ģ���Ϸ�����в��ᱻɾ�����������ؽ�ɫѡ����ɫ��¼��
	"""
	def __init__( self ) :
		self.__comRoots = MapList()					# ͨ�ô��ڣ���ʼ����Ϻ���գ�
		self.__loginRoots = MapList()				# ��¼��ش��ڣ���ʼ����Ϻ���գ�
		self.__worldRoots = MapList()				# �����������õ��Ĵ��ڣ���ʼ����Ϻ���գ�
		self.__setCommonRoots()						# ��������ͨ�ô��ڣ���ʼ����Ϻ���գ�
		self.__setLoginRoots()						# �������е�¼���ڣ���ʼ����Ϻ���գ�
		self.__setWorldRoots()						# �����������細�ڣ���ʼ����Ϻ���գ�

	# -------------------------------------------------
	def __setCommonRoots( self ) :
		"""
		����ͨ�� UI�����۵�¼ʱ���ǽ�������󶼿����ã�
		ע�⣺ֵ�ĵڶ�ά�ǲ���ֵ����ʾ�Ƿ���ӵ� UI ������
		"""
		self.__comRoots["dragObj"]				= ( DragObject, True ) 				# �ϷŶ���
		self.__comRoots["loadingGround"]		= ( LoadingGround, True )			# �������ؽ���

	@reimpl_login.deco_uiFactorySetLoginRoots
	def __setLoginRoots( self ) :
		"""
		������¼ʱʹ�õ� UI����������󲻿���ʹ�ã�
		ע�⣺ֵ�ĵڶ�ά�ǲ���ֵ����ʾ�Ƿ���ӵ� UI ������
		"""
		self.__loginRoots["loginDialog"]		= ( LoginDialog, True ) 			# ��¼����
		self.__loginRoots["roleSelector"]		= ( RoleSelector, True )			# ��ɫѡ�����
		self.__loginRoots["roleCreator"]		= ( RoleCreator, True ) 			# ��ɫ��������
		self.__loginRoots["campSelector"]		= ( CampSelector, True ) 
	@reimpl_login.deco_uiFactorySetWorldRoots
	def __setWorldRoots( self ) :
		"""
		��������״̬ UI��������������ʹ�ã�
		ע�⣺ֵ�ĵڶ�ά�ǲ���ֵ����ʾ�Ƿ���ӵ� UI ������
		"""
		# ������ʾ�� UI
		self.__worldRoots["miniMap"]			= ( MiniMap, True )					# С��ͼ
		self.__worldRoots["bigMap"]				= ( BigMap, True )					# ���ͼ
		self.__worldRoots["playerInfo"]			= ( PlayerInfo, True )				# ��ɫ��Ϣ
		self.__worldRoots["chatWindow"]			= ( ChatWindow, True )				# ����
		self.__worldRoots["quickBar"]			= ( QuickBar, True )				# ���ܿ����
		self.__worldRoots["systemBar"]			= ( SystemBar, True )				# ���ܿ����
		self.__worldRoots["hideBar"]			= ( HideBar, True )

		# �ǳ�����ʾ��ͨ�� UI
		self.__worldRoots["pickupBox"]			= ( PickupBox, True )				# ��Ʒʰȡ��
		self.__worldRoots["pickupQuestBox"]		= ( PickupQuestBox, True )			# ���������Ʒʰȡ��

		self.__worldRoots["flyTextDrive"]		= ( FlyTextDrive, False )			# ��������
		self.__worldRoots["nameFactory"]		= ( NameFactory, False )			# entity ���ֹ���
		self.__worldRoots["centerMessageCtrl"]	= ( CenterMessageController, False )# ��Ļ�м���Ϣ��ʾ
		self.__worldRoots["targetMgr"] 			=  ( TargetMgr, False )		# Ŀ��ѡ��ͷ��

		# �ǳ�����ʾ�ľ��� UI
		self.__worldRoots["helpWindow"]			= ( HelpWindow, True )				# ϵͳ��������
		self.__worldRoots["castIndicator"]			= ( CastIndicator, True )		# ϵͳ��������
#		self.__worldRoots["targetInfo"]			= ( TargetInfo, True )				# Ŀ����ϢС����
		self.__worldRoots["vehicleHead"]		= ( VehicleInfo, True )				# ���ͷ����Ϣ
		self.__worldRoots["teammateArray"]		= ( TeammateArray, True )			# �����б�
		self.__worldRoots["teamInfoWindow"]		= ( TeamInfoWindow, True )			# ������Ϣ����
		self.__worldRoots["playProWindow"]		= ( PlayProWindow, True )			# ��ɫ���Դ���
		self.__worldRoots["espialWindow"]		= ( EspialWindow, True )			# �鿴�Է�װ�������Դ���
		self.__worldRoots["espialWindowRemote"]		= ( EspialWindowRemote, True )			# �鿴�Է�װ�������Դ���
		self.__worldRoots["kitBag"]				= ( KitBag, True )					# ����
		self.__worldRoots["equipDurability"]	= ( EquipDurability, True )			# װ���;���ʾ
		self.__worldRoots["skillTree"]			= ( SkillTree, True )				# �����б���
		self.__worldRoots["skillList"]			= ( SkillList, True )				# �����б���
		self.__worldRoots["skillTrainer"]		= ( SkillTrainer, True )			# ����ѧϰ����
		self.__worldRoots["questHelp"]			= ( QuestHelp, True )				# �����б���
		self.__worldRoots["rewardQuestList"]	= ( RewardQuestList, True )			# �������񴰿�
		self.__worldRoots["bduffPanel"]			= ( BDuffPanel, True )				# buff ����
		self.__worldRoots["tradeWindow"]		= ( TradeWindow, True )				# ���״���
		self.__worldRoots["petTrade"]			= ( PetTrade, True )				# ���ｻ�׽���
		self.__worldRoots["specialMerchantWindow"]		= ( SpecialMerchantWindow, True )		# ���̴���
		self.__worldRoots["darkMerchantWindow"]		= ( DarkMerchantWindow, True )			# �������˴���
		self.__worldRoots["darkTradeWindow"]	= ( DarkTradeWindow, True )			# Ͷ�����˽��״���
		self.__worldRoots["itemChapmanTradeWindow"]	= ( ItemChapmanTradeWindow, True )	# �������˽��״��ڣ���ĳ��Ʒ��ȡĳ��Ʒ�Ľ��ף�
		self.__worldRoots["pointChapmanTradeWindow"]= ( PointChapmanTradeWindow, True )	# �������˽��״��ڣ��û��ֻ�ȡĳ��Ʒ�Ľ��ף�

		self.__worldRoots["tradingWindow"]		= ( TradingWindow, True )			# ��Ҽ佻�״���
		self.__worldRoots["talkingWindow"]		= ( TalkingWindow, True )			# �� NPC �Ի�����
		self.__worldRoots["npcMsgWindow"]		= ( NpcMsgWindow, True )			# �� NPC ��Ϣ����
		self.__worldRoots["groupRewards"]		= ( GroupRewards, True )			# ��������fpj���ŵ� TalkingWindow �У���Ϊ��Ա��
		self.__worldRoots["artiRefine"]			= ( ArtiRefine, True )				# ������������
		self.__worldRoots["intonateBar"]		= ( IntonateBar, True )				# ������

		self.__worldRoots["storeWindow"]		= ( StoreWindow, True )				# �ֿ�

		self.__worldRoots["relationWindow"]		= ( RelationWindow, True )			# �˼ʹ�ϵ����

		self.__worldRoots["petWindow"]			= ( PetWindow, True)				# ���ﴰ��
		self.__worldRoots["petInfo"]			= ( PetInfo, True )					# ������Ϣͼ��
		self.__worldRoots["petFoster"]			= ( PetFoster, True )				# ���ﷱֳ����
		self.__worldRoots["petStorage"]			= ( PetStorage, True )				# ����ֿ����
		self.__worldRoots["storageTenancy"]		= ( StorageTenancy, True )			# ����ֿ�����

#		self.__worldRoots["videoSetting"]		= ( VideoSetting, True )			# ��ʾ���ô���
#		self.__worldRoots["audioSetting"]		= ( AudioSetting, True )			# ��Ƶ���ô���
		#self.__worldRoots["shortcutSettingWindow"] = ( ShortcutSettingWindow, True )# ��ݼ����ô���


		self.__worldRoots["entityResume"]		= ( EntityResume, False )			# ��������


		self.__worldRoots["mailWindow"]			= ( MailWindow, True )				# �ʼ�����
		self.__worldRoots["equipProduce"]		= ( EquipProduce, True )			# װ�����촰��

		self.__worldRoots["statusTextController"]= ( StatusTextController, False )	# �Զ���ֺ��Զ�Ѱ·ͼƬ


		self.__worldRoots["tishouSellWnd"]		= ( TiShouSellWindow, True )		# ������Ʒ������
		self.__worldRoots["tishouBuyWnd"]		= ( TiShouBuyWindow, True )			# ������Ʒ���򴰿�

		self.__worldRoots["pointCardBuyWnd"]	= ( PCBuyWindow, True )				# �㿨���۳��۴���
		self.__worldRoots["pointCardSellWnd"]	= ( PCSellWindow, True )			# �㿨���۹��򴰿�

		self.__worldRoots["sellWindow"]			= ( VendSellWindow, True )			# ���Ұ�̯����
		self.__worldRoots["buyWindow"]			= ( VendBuyWindow, True )			# ��Ҳ鿴��̯����
		self.__worldRoots["specialShop"]		= ( SpecialShop, True )				# �����̳�
		self.__worldRoots["statWindow"]			= ( StatWindow, True )				# NPC����ս��ͳ��
		self.__worldRoots["fcStatusWindow"]		= ( FCStatusWindow, True )			# ������սս������
		self.__worldRoots["reliveMsgBox"]		= ( ReliveMsgBox, True )			# NPC����ս���������
		self.__worldRoots["reliveMsgBoxAba"]	= ( ReliveMsgBoxAba, True )			# ������̨���������
		self.__worldRoots["reviveTeamCompeteBox"]= ( ReviveTeamCompeteBox, True )	# ��Ӿ������������
		self.__worldRoots["tipsPanel"]			= ( TipsPanel, True )
		self.__worldRoots["TongDetails"]			= ( TongDetails, True )			# �鿴�����߰�����

		self.__worldRoots["lotteryWindow"]		= ( LotteryWindow, True )			# ���ҽ���

		self.__worldRoots["shenShouBeckon"]		= ( ShenShouBeckon, True )			# ��������ٻ�
		self.__worldRoots["storageWindow"]		= ( StorageWindow, True )			# ���ֿ�
		self.__worldRoots["applyRobWar"]		= ( ApplyRobWar, True )				# ����Ӷ�վ����ӽ���
		self.__worldRoots["tongQuery"]			= ( TongQuery, True )				# �����Ϣ��ѯ
		self.__worldRoots["warIntergral"]		= ( WarIntergral, True )			# ����ս����
		self.__worldRoots["warRanking"]			= ( WarRanking, True )				# ����ս��¹��
#		self.__worldRoots["warFixture"]			= ( WarFixture, True )				# ������̡�������
		self.__worldRoots["markTips"]			= ( MarkTips, True )				# ����ս����ͳ��
		self.__worldRoots["tongFixture"]		= ( TongFixture, True )				# �°�����̡�������
		self.__worldRoots["turnwarwnd"]			= ( TurnWarMatchWnd, True )			# ��ᳵ��ս����ƥ�����

		self.__worldRoots["activityCalendar"]	= ( ActivityCalendar, True )		# ���ʾ����

#		self.__worldRoots["searchMaster"]		= ( SearchMaster, True )			# ����ʦ������
#		self.__worldRoots["searchPrentice"]		= ( SearchPrenticeWindow, True )	# ����ͽ�ܽ���
		self.__worldRoots["searchTeachWindow"]		= ( SearchTeachWindow, True )			# ����ʦͽ����

		self.__worldRoots["qandAWindow"]		= ( QandAWindow, True )				# �����ʴ����
		self.__worldRoots["gameQuizWnd"]		= ( GameQuizWnd, True )				# ֪ʶ�ʴ����

		self.__worldRoots["copySpaceInfo"]		= ( CopySpaceInfo, True )			# ����ͳ����Ϣ
		self.__worldRoots["teamPoints"]			= ( TeamPoints, True )				# ��Ӿ�������ͳ��
		self.__worldRoots["raceHorseData"]		= ( RaceHorseDataPanel, True )		# ����ͳ�ƽ���
		self.__worldRoots["rollsManager"]		= ( RollsManager, False )			# �������ROLL����
		self.__worldRoots["rankWindow"]			= ( RankWindow, True )				# ���а����
		self.__worldRoots["fixRewardBox"]		= ( FixRewardBox, True ) 			# �̶�ʱ�佱��
		self.__worldRoots["espialPet"]			= ( EspialPet, True )				# �鿴�Է���������
		self.__worldRoots["petEnhance"]			= ( PetEnhance, True )				# ����ǿ������
#		self.__worldRoots["EidolonWindow"]		= ( EidolonWindow, True ) 			# �����������
		self.__worldRoots["bulletinBoard"]		= ( BulletinBoard, True )			# ��Ϧ���԰�
		self.__worldRoots["pixieWindow"]		= ( PixieWindow, True )				# ������Ի�����
		self.__worldRoots["emotionBox"]			= ( EmotionBox, True )				# ������ʾ����
		self.__worldRoots["challengeCopy"]		= ( ChallengeCopy, True )			# ��ս��������
		self.__worldRoots["trigIntorMgr"]		= ( TrigIntorMgr, False )			# ��ս��������
		self.__worldRoots["SpaceCopyPlotLv40"]	= ( SpaceCopyPlotLv40, True )		# 40�����鸱��������ʾѪ��
		self.__worldRoots["copyTeamSys"]		= ( CopyTeamSys, True )				# �������ϵͳ����
		self.__worldRoots["fixedTeamNotify"]	= ( FixedTeamNotify, True )			# �������ϵͳ����
		self.__worldRoots["lolMiniMap"]			= ( LoLMiniMap, True )				# Ӣ�����˸���С��ͼ
		self.__worldRoots["lolTradeWnd"]			= ( LolTradeWnd, True )		# Ӣ�����˸������״���
		self.__worldRoots["robotChoice"]			= ( RobotChoice, True )			# ʧ�䱦��pve�����˽���
		self.__worldRoots["robotProperty"]			= ( RobotProperty, True )		# ʧ�䱦��pve���������Խ���
		self.__worldRoots["pvpTeamWnd"]			= ( PvPTeamWnd, True )		# ʧ�䱦��pvp����
		self.__worldRoots["yeZhanRank"]			= ( YeZhanRank, True )		# ҹս���ܻ���ͳ�ƽ���
		self.__worldRoots["fhltRankWnd"]			= ( FHLTRankWnd, True )	# �������ͳ�ƽ���
		self.__worldRoots["fhltAgainst"]			= ( FHLTAgainst, True )			# ���ս���������
		self.__worldRoots["sermonWnd"]			= ( SermonWnd, True )			# ֤������
		self.__worldRoots["portraitDriver"]			= ( PortraitDriver, False )			# AI������Ϣ����
		self.__worldRoots["destransWnd"]			= ( DestransWnd, True )			# AI������Ϣ����
#		self.__worldRoots["gameSetting"]			= ( GameSetting, True )		# ��Ϸ���ý���
		self.__worldRoots["spaceCopyLiuWangMuRank"] = ( SpaceCopyLiuWangMuRank, True )		# ����Ĺ���а����
		self.__worldRoots["spaceCopyTBBattleRank"] = ( SpaceCopyTBBattleRank, True )		# ��ħ��ս���а����
		self.__worldRoots["copyTBBattleTransBox"] = ( CopyTBBattleTransBox, True )	# ��ħ��ս���ͽ���
		self.__worldRoots["copyTBBattleTransPanel"] = ( CopyTBBattleTransPanel, True )
		self.__worldRoots["copyJueDiFanJiBox"] = ( CopyJueDiFanJiBox, True )	# ���ط��������
		self.__worldRoots["copyJueDiFanJiResult"] = ( CopyJueDiFanJiResult, True )
		self.__worldRoots["copyJueDiFanJiRank"] = ( CopyJueDiFanJiRank, True )
		self.__worldRoots["highDanceEntrance"] = ( HighDanceEntrance, True )		# ����������
		self.__worldRoots["highDance"] = ( HighDance, True )		# ������ذ�ť
		self.__worldRoots["tongSpecialShop"] = ( TongSpecialShop, True )		# ��������̳ǽ���
		self.__worldRoots["copyAoZhanBox"] = ( CopyAoZhanBox, True )		# ��սȺ�ۻ����
		self.__worldRoots["copyAoZhanSignUp"] = ( CopyAoZhanSignUp, True )
		self.__worldRoots["copyAoZhanRank"] = ( CopyAoZhanRank, True )
		self.__worldRoots["copyAoZhanResult"] = ( CopyAoZhanResult, True )
		self.__worldRoots["yiJieSignUp"] = ( YiJieSignUp, True )				# ���ս����������
		self.__worldRoots["angerPoint"] = ( AngerPoint, True )					# ���ս��ŭ�������
		self.__worldRoots["yiJieScore"] = ( YiJieScore, True )					# ���ս�����ְ����
		self.__worldRoots["yiJieBattleInfos"] = ( YiJieBattleInfos, True )		# ���ս��ս��ͳ�ƽ���
		self.__worldRoots["tongAlliance"] = ( TongsAlliance, True )				# ���ս������ս����
		self.__worldRoots["slotMachine"] = ( SlotMachine, True )				# �ϻ���
		self.__worldRoots["campFHLTRankWnd"] = ( CampFHLTRankWnd, True )			# ��Ӫ���������Ϣ
		self.__worldRoots["campFHLTSign"] = ( CampFHLTSign, True )					# ��Ӫ������챨��

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def createRoot( self, hookName, UIClass, addToMgr = True ) :
		"""
		����һ�� Root UI ʵ����ע�⣺�����ﴴ���� UI ���ǳ�פ�ڴ�ģ�
		@type				UIClass	 : classtype
		@param				UIClass	 : ui ��
		@type				hookName : str
		@param				hookName : ui ����
		@type				addToMgr : bool
		@param				addToMgr : �Ƿ���ӵ�������������̳��� RootGUI ������ӵ���������
		"""
		pyRoot = UIClass()														# ����ʵ��
		setattr( ruisMgr, hookName, pyRoot )
		if addToMgr : ruisMgr.add( pyRoot, hookName )							# ��ӵ�������
		uiSounder.initRootSound( pyRoot )

		if hookName in self.__comRoots :
			self.__comRoots.pop( hookName )
		if hookName in self.__loginRoots :
			self.__loginRoots.pop( hookName )
		if hookName in self.__worldRoots :
			self.__worldRoots.pop( hookName )									# ���б��������ֻ����һ�Σ�

	# ---------------------------------------
	def getCommonRoots( self ) :
		"""
		����ͨ�� UI�����۵�¼ʱ���ǽ�������󶼿����ã�
		@rtype					: list
		@return					: [( ʵ����, ��, �Ƿ���ӵ� RootUIMgr ), ...]
		"""
		return [( r[0], r[1][0], r[1][1] ) for r in self.__comRoots.items()]

	def getLoginRoots( self ) :
		"""
		������¼ʱʵ�õ� UI����������󲻿���ʹ�ã�
		@rtype					: list
		@return					: [( ʵ����, ��, �Ƿ���ӵ� RootUIMgr ), ...]
		"""
		return [( r[0], r[1][0], r[1][1] ) for r in self.__loginRoots.items()]

	# ---------------------------------------
	def getWorldRoots( self ) :
		"""
		��������״̬ UI��������������ʹ�ã�
		@rtype					: list
		@return					: [( ʵ����, ��, �Ƿ���ӵ� RootUIMgr ), ...]
		"""
		# ������ʾ�� UI
		return [( r[0], r[1][0], r[1][1] ) for r in self.__worldRoots.items()]

	# ---------------------------------------
	def createTempRoots( self ) :
		"""
		��ȡ��ʱ UI�������߻��õĹ��ߣ���������Ϸһ�𷢲���
		"""
		tmodules = SmartImport.importAll( "tools", "T_*" )
		for module in tmodules :
			members = inspect.getmembers( module )						# ��ȡģ���е����г�Ա����
			for name, member in members :
				if not inspect.isclass( member ) : continue				# ���˵������Ա
				if not issubclass( member, RootGUI ) : continue			# ���˵����Ǽ̳��� RootGUI ����
				if inspect.getmodule( member ) == module :				# ���˵����ڵ�ǰģ����ʵ�ֵĳ�Ա
					pyTool = member()									# ��������ʵ��

	# -------------------------------------------------
	def relateRoots( self ) :
		"""
		�Դ��ڹ�ϵ��
		"""
		pass


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
uiFactory = UIFactory()
