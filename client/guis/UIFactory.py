# -*- coding: gb18030 -*-
#
# $Id: UIFactory.py,v 1.116 2008-09-02 10:09:49 fangpengjun Exp $

"""
implement root gui factory

2006.07.04: writen by huangyongwei
"""

# -----------------------------------------------------
# 常规 UI（无论登录状态还是在世界状态都可以用的 UI ）
# -----------------------------------------------------
from guis.common.DragObject import DragObject
from guis.otheruis.LoadingGround import LoadingGround

# -----------------------------------------------------
# 登录 UI（在登录的时侯就要用到的 UI）
# -----------------------------------------------------
from guis.loginuis.logindialog.LoginDialog import LoginDialog
from guis.loginuis.roleselector.RoleSelector import RoleSelector
from guis.loginuis.rolecreator.RoleCreator import RoleCreator
from guis.loginuis.campselector.CampSelector import CampSelector

# -----------------------------------------------------
# 世界状态 UI（只有玩家进入世界后才用到的 UI）
# -----------------------------------------------------
# 世界状态下的常规 UI（玩家一进入世界就可以看见的 UI）
from guis.general.minimap.MiniMap import MiniMap
from guis.general.bigmap.BigMap import BigMap
from guis.general.playerinfo.PlayerInfo import PlayerInfo
from guis.general.chatwindow.ChatWindow import ChatWindow
from guis.general.quickbar.QuickBar import QuickBar
from guis.general.quickBar.QuickBar import SystemBar
from guis.general.quickbar.HideBar import HideBar

# 世界状态下的非常规通用 UI（玩家进入世界时，不可以看见的，可以被作为工具用的 UI）
from guis.tooluis.passwordbox.PasswordWindow import PasswordWindow
from guis.tooluis.pickupbox.PickupBox import PickupBox
from guis.tooluis.pickupbox.PickupBox import PickupQuestBox

from guis.otheruis.FlyText import FlyTextDrive
from guis.otheruis.floatnames.NameFactory import NameFactory
from guis.otheruis.CenterMessage import CenterMessageController
from guis.general.targetinfo.TargetMgr import TargetMgr

# 世界状态下的非常规具体 UI（玩家进入世界时，不可以看见的 UI）

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
from guis.general.rolestrading.TradingWindow import TradingWindow	# 玩家交易窗口
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

from guis.otheruis.StatusText import StatusTextController	#自动打怪和自动寻路提示信息， 2007-10-23，gjx

from guis.general.vendwindow.sellwindow.SellWindow import VendSellWindow
from guis.general.vendwindow.buywindow.BuyWindow import VendBuyWindow
from guis.general.playerprowindow.EspialWindow import EspialWindow	#载入观察对方的UI
from guis.general.playerprowindow.EspialWindowRemote import EspialWindowRemote	#载入远程观察对方的UI

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
# 单例式窗口（只需 import 无需创建）
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
	UI 工厂，用于创建游戏中需要的所有常驻窗口
	注意：在这里创建的 UI 都是常驻内存的（游戏运行中不会被删除，包括返回角色选择或角色登录）
	"""
	def __init__( self ) :
		self.__comRoots = MapList()					# 通用窗口（初始化完毕后被清空）
		self.__loginRoots = MapList()				# 登录相关窗口（初始化完毕后被清空）
		self.__worldRoots = MapList()				# 进入世界后采用到的窗口（初始化完毕后被清空）
		self.__setCommonRoots()						# 设所有置通用窗口（初始化完毕后被清空）
		self.__setLoginRoots()						# 设置所有登录窗口（初始化完毕后被清空）
		self.__setWorldRoots()						# 设置所有世界窗口（初始化完毕后被清空）

	# -------------------------------------------------
	def __setCommonRoots( self ) :
		"""
		创建通用 UI（无论登录时还是进入世界后都可以用）
		注意：值的第二维是布尔值，标示是否添加到 UI 管理器
		"""
		self.__comRoots["dragObj"]				= ( DragObject, True ) 				# 拖放对象
		self.__comRoots["loadingGround"]		= ( LoadingGround, True )			# 场景加载界面

	@reimpl_login.deco_uiFactorySetLoginRoots
	def __setLoginRoots( self ) :
		"""
		创建登录时使用的 UI（进入世界后不可以使用）
		注意：值的第二维是布尔值，标示是否添加到 UI 管理器
		"""
		self.__loginRoots["loginDialog"]		= ( LoginDialog, True ) 			# 登录界面
		self.__loginRoots["roleSelector"]		= ( RoleSelector, True )			# 角色选择界面
		self.__loginRoots["roleCreator"]		= ( RoleCreator, True ) 			# 角色创建界面
		self.__loginRoots["campSelector"]		= ( CampSelector, True ) 
	@reimpl_login.deco_uiFactorySetWorldRoots
	def __setWorldRoots( self ) :
		"""
		进入世界状态 UI（进入世界后才能使用）
		注意：值的第二维是布尔值，标示是否添加到 UI 管理器
		"""
		# 常规显示的 UI
		self.__worldRoots["miniMap"]			= ( MiniMap, True )					# 小地图
		self.__worldRoots["bigMap"]				= ( BigMap, True )					# 大地图
		self.__worldRoots["playerInfo"]			= ( PlayerInfo, True )				# 角色信息
		self.__worldRoots["chatWindow"]			= ( ChatWindow, True )				# 聊天
		self.__worldRoots["quickBar"]			= ( QuickBar, True )				# 技能快捷栏
		self.__worldRoots["systemBar"]			= ( SystemBar, True )				# 技能快捷栏
		self.__worldRoots["hideBar"]			= ( HideBar, True )

		# 非常规显示的通用 UI
		self.__worldRoots["pickupBox"]			= ( PickupBox, True )				# 物品拾取框
		self.__worldRoots["pickupQuestBox"]		= ( PickupQuestBox, True )			# 场景物件物品拾取框

		self.__worldRoots["flyTextDrive"]		= ( FlyTextDrive, False )			# 飞扬文字
		self.__worldRoots["nameFactory"]		= ( NameFactory, False )			# entity 名字工厂
		self.__worldRoots["centerMessageCtrl"]	= ( CenterMessageController, False )# 屏幕中间信息提示
		self.__worldRoots["targetMgr"] 			=  ( TargetMgr, False )		# 目标选择头像

		# 非常规显示的具体 UI
		self.__worldRoots["helpWindow"]			= ( HelpWindow, True )				# 系统帮助窗口
		self.__worldRoots["castIndicator"]			= ( CastIndicator, True )		# 系统帮助窗口
#		self.__worldRoots["targetInfo"]			= ( TargetInfo, True )				# 目标信息小界面
		self.__worldRoots["vehicleHead"]		= ( VehicleInfo, True )				# 骑宠头像信息
		self.__worldRoots["teammateArray"]		= ( TeammateArray, True )			# 队友列表
		self.__worldRoots["teamInfoWindow"]		= ( TeamInfoWindow, True )			# 队伍信息窗口
		self.__worldRoots["playProWindow"]		= ( PlayProWindow, True )			# 角色属性窗口
		self.__worldRoots["espialWindow"]		= ( EspialWindow, True )			# 查看对方装备和属性窗口
		self.__worldRoots["espialWindowRemote"]		= ( EspialWindowRemote, True )			# 查看对方装备和属性窗口
		self.__worldRoots["kitBag"]				= ( KitBag, True )					# 背包
		self.__worldRoots["equipDurability"]	= ( EquipDurability, True )			# 装备耐久显示
		self.__worldRoots["skillTree"]			= ( SkillTree, True )				# 技能列表窗口
		self.__worldRoots["skillList"]			= ( SkillList, True )				# 技能列表窗口
		self.__worldRoots["skillTrainer"]		= ( SkillTrainer, True )			# 技能学习窗口
		self.__worldRoots["questHelp"]			= ( QuestHelp, True )				# 任务列表窗口
		self.__worldRoots["rewardQuestList"]	= ( RewardQuestList, True )			# 悬赏任务窗口
		self.__worldRoots["bduffPanel"]			= ( BDuffPanel, True )				# buff 窗口
		self.__worldRoots["tradeWindow"]		= ( TradeWindow, True )				# 交易窗口
		self.__worldRoots["petTrade"]			= ( PetTrade, True )				# 宠物交易界面
		self.__worldRoots["specialMerchantWindow"]		= ( SpecialMerchantWindow, True )		# 跑商窗口
		self.__worldRoots["darkMerchantWindow"]		= ( DarkMerchantWindow, True )			# 黑市商人窗口
		self.__worldRoots["darkTradeWindow"]	= ( DarkTradeWindow, True )			# 投机商人交易窗口
		self.__worldRoots["itemChapmanTradeWindow"]	= ( ItemChapmanTradeWindow, True )	# 特殊商人交易窗口（用某物品换取某物品的交易）
		self.__worldRoots["pointChapmanTradeWindow"]= ( PointChapmanTradeWindow, True )	# 特殊商人交易窗口（用积分换取某物品的交易）

		self.__worldRoots["tradingWindow"]		= ( TradingWindow, True )			# 玩家间交易窗口
		self.__worldRoots["talkingWindow"]		= ( TalkingWindow, True )			# 与 NPC 对话窗口
		self.__worldRoots["npcMsgWindow"]		= ( NpcMsgWindow, True )			# 与 NPC 消息窗口
		self.__worldRoots["groupRewards"]		= ( GroupRewards, True )			# 奖励？（fpj：放到 TalkingWindow 中，作为成员）
		self.__worldRoots["artiRefine"]			= ( ArtiRefine, True )				# 神器炼化界面
		self.__worldRoots["intonateBar"]		= ( IntonateBar, True )				# 吟唱条

		self.__worldRoots["storeWindow"]		= ( StoreWindow, True )				# 仓库

		self.__worldRoots["relationWindow"]		= ( RelationWindow, True )			# 人际关系窗口

		self.__worldRoots["petWindow"]			= ( PetWindow, True)				# 宠物窗口
		self.__worldRoots["petInfo"]			= ( PetInfo, True )					# 宠物信息图像
		self.__worldRoots["petFoster"]			= ( PetFoster, True )				# 宠物繁殖界面
		self.__worldRoots["petStorage"]			= ( PetStorage, True )				# 宠物仓库界面
		self.__worldRoots["storageTenancy"]		= ( StorageTenancy, True )			# 宠物仓库租赁

#		self.__worldRoots["videoSetting"]		= ( VideoSetting, True )			# 显示设置窗口
#		self.__worldRoots["audioSetting"]		= ( AudioSetting, True )			# 音频设置窗口
		#self.__worldRoots["shortcutSettingWindow"] = ( ShortcutSettingWindow, True )# 快捷键设置窗口


		self.__worldRoots["entityResume"]		= ( EntityResume, False )			# 对象描述


		self.__worldRoots["mailWindow"]			= ( MailWindow, True )				# 邮件窗口
		self.__worldRoots["equipProduce"]		= ( EquipProduce, True )			# 装备打造窗口

		self.__worldRoots["statusTextController"]= ( StatusTextController, False )	# 自动打怪和自动寻路图片


		self.__worldRoots["tishouSellWnd"]		= ( TiShouSellWindow, True )		# 替售物品管理窗口
		self.__worldRoots["tishouBuyWnd"]		= ( TiShouBuyWindow, True )			# 替售物品购买窗口

		self.__worldRoots["pointCardBuyWnd"]	= ( PCBuyWindow, True )				# 点卡寄售出售窗口
		self.__worldRoots["pointCardSellWnd"]	= ( PCSellWindow, True )			# 点卡寄售购买窗口

		self.__worldRoots["sellWindow"]			= ( VendSellWindow, True )			# 卖家摆摊界面
		self.__worldRoots["buyWindow"]			= ( VendBuyWindow, True )			# 买家查看摆摊界面
		self.__worldRoots["specialShop"]		= ( SpecialShop, True )				# 道具商城
		self.__worldRoots["statWindow"]			= ( StatWindow, True )				# NPC争夺战场统计
		self.__worldRoots["fcStatusWindow"]		= ( FCStatusWindow, True )			# 家族挑战战况窗口
		self.__worldRoots["reliveMsgBox"]		= ( ReliveMsgBox, True )			# NPC争夺战死亡复活窗口
		self.__worldRoots["reliveMsgBoxAba"]	= ( ReliveMsgBoxAba, True )			# 家族擂台死亡复活窗口
		self.__worldRoots["reviveTeamCompeteBox"]= ( ReviveTeamCompeteBox, True )	# 组队竞赛死亡复活窗口
		self.__worldRoots["tipsPanel"]			= ( TipsPanel, True )
		self.__worldRoots["TongDetails"]			= ( TongDetails, True )			# 查看邀请者帮会界面

		self.__worldRoots["lotteryWindow"]		= ( LotteryWindow, True )			# 锦囊界面

		self.__worldRoots["shenShouBeckon"]		= ( ShenShouBeckon, True )			# 帮会神兽召唤
		self.__worldRoots["storageWindow"]		= ( StorageWindow, True )			# 帮会仓库
		self.__worldRoots["applyRobWar"]		= ( ApplyRobWar, True )				# 帮会掠夺站申请接界面
		self.__worldRoots["tongQuery"]			= ( TongQuery, True )				# 帮会信息查询
		self.__worldRoots["warIntergral"]		= ( WarIntergral, True )			# 帮会城战积分
		self.__worldRoots["warRanking"]			= ( WarRanking, True )				# 帮会城战逐鹿榜
#		self.__worldRoots["warFixture"]			= ( WarFixture, True )				# 帮会赛程、赛况表
		self.__worldRoots["markTips"]			= ( MarkTips, True )				# 帮会城战积分统计
		self.__worldRoots["tongFixture"]		= ( TongFixture, True )				# 新帮会赛程、赛况表
		self.__worldRoots["turnwarwnd"]			= ( TurnWarMatchWnd, True )			# 帮会车轮战队伍匹配界面

		self.__worldRoots["activityCalendar"]	= ( ActivityCalendar, True )		# 活动提示界面

#		self.__worldRoots["searchMaster"]		= ( SearchMaster, True )			# 搜索师傅界面
#		self.__worldRoots["searchPrentice"]		= ( SearchPrenticeWindow, True )	# 搜索徒弟界面
		self.__worldRoots["searchTeachWindow"]		= ( SearchTeachWindow, True )			# 搜索师徒界面

		self.__worldRoots["qandAWindow"]		= ( QandAWindow, True )				# 任务问答界面
		self.__worldRoots["gameQuizWnd"]		= ( GameQuizWnd, True )				# 知识问答界面

		self.__worldRoots["copySpaceInfo"]		= ( CopySpaceInfo, True )			# 副本统计信息
		self.__worldRoots["teamPoints"]			= ( TeamPoints, True )				# 组队竞赛积分统计
		self.__worldRoots["raceHorseData"]		= ( RaceHorseDataPanel, True )		# 赛马统计界面
		self.__worldRoots["rollsManager"]		= ( RollsManager, False )			# 队伍分配ROLL界面
		self.__worldRoots["rankWindow"]			= ( RankWindow, True )				# 排行榜界面
		self.__worldRoots["fixRewardBox"]		= ( FixRewardBox, True ) 			# 固定时间奖励
		self.__worldRoots["espialPet"]			= ( EspialPet, True )				# 查看对方宠物属性
		self.__worldRoots["petEnhance"]			= ( PetEnhance, True )				# 宠物强化界面
#		self.__worldRoots["EidolonWindow"]		= ( EidolonWindow, True ) 			# 创世精灵界面
		self.__worldRoots["bulletinBoard"]		= ( BulletinBoard, True )			# 七夕留言板
		self.__worldRoots["pixieWindow"]		= ( PixieWindow, True )				# 随身精灵对话界面
		self.__worldRoots["emotionBox"]			= ( EmotionBox, True )				# 表情显示界面
		self.__worldRoots["challengeCopy"]		= ( ChallengeCopy, True )			# 挑战副本界面
		self.__worldRoots["trigIntorMgr"]		= ( TrigIntorMgr, False )			# 挑战副本界面
		self.__worldRoots["SpaceCopyPlotLv40"]	= ( SpaceCopyPlotLv40, True )		# 40级剧情副本单独显示血条
		self.__worldRoots["copyTeamSys"]		= ( CopyTeamSys, True )				# 副本组队系统界面
		self.__worldRoots["fixedTeamNotify"]	= ( FixedTeamNotify, True )			# 副本组队系统界面
		self.__worldRoots["lolMiniMap"]			= ( LoLMiniMap, True )				# 英雄联盟副本小地图
		self.__worldRoots["lolTradeWnd"]			= ( LolTradeWnd, True )		# 英雄联盟副本交易窗口
		self.__worldRoots["robotChoice"]			= ( RobotChoice, True )			# 失落宝藏pve机器人界面
		self.__worldRoots["robotProperty"]			= ( RobotProperty, True )		# 失落宝藏pve机器人属性界面
		self.__worldRoots["pvpTeamWnd"]			= ( PvPTeamWnd, True )		# 失落宝藏pvp界面
		self.__worldRoots["yeZhanRank"]			= ( YeZhanRank, True )		# 夜战凤栖积分统计界面
		self.__worldRoots["fhltRankWnd"]			= ( FHLTRankWnd, True )	# 烽火连天统计界面
		self.__worldRoots["fhltAgainst"]			= ( FHLTAgainst, True )			# 夺城战复赛对阵表
		self.__worldRoots["sermonWnd"]			= ( SermonWnd, True )			# 证道界面
		self.__worldRoots["portraitDriver"]			= ( PortraitDriver, False )			# AI触发消息界面
		self.__worldRoots["destransWnd"]			= ( DestransWnd, True )			# AI触发消息界面
#		self.__worldRoots["gameSetting"]			= ( GameSetting, True )		# 游戏设置界面
		self.__worldRoots["spaceCopyLiuWangMuRank"] = ( SpaceCopyLiuWangMuRank, True )		# 六王墓排行榜界面
		self.__worldRoots["spaceCopyTBBattleRank"] = ( SpaceCopyTBBattleRank, True )		# 仙魔论战排行榜界面
		self.__worldRoots["copyTBBattleTransBox"] = ( CopyTBBattleTransBox, True )	# 仙魔论战传送界面
		self.__worldRoots["copyTBBattleTransPanel"] = ( CopyTBBattleTransPanel, True )
		self.__worldRoots["copyJueDiFanJiBox"] = ( CopyJueDiFanJiBox, True )	# 绝地反击活动界面
		self.__worldRoots["copyJueDiFanJiResult"] = ( CopyJueDiFanJiResult, True )
		self.__worldRoots["copyJueDiFanJiRank"] = ( CopyJueDiFanJiRank, True )
		self.__worldRoots["highDanceEntrance"] = ( HighDanceEntrance, True )		# 劲舞舞王榜
		self.__worldRoots["highDance"] = ( HighDance, True )		# 劲舞相关按钮
		self.__worldRoots["tongSpecialShop"] = ( TongSpecialShop, True )		# 帮会特殊商城界面
		self.__worldRoots["copyAoZhanBox"] = ( CopyAoZhanBox, True )		# 鏖战群雄活动界面
		self.__worldRoots["copyAoZhanSignUp"] = ( CopyAoZhanSignUp, True )
		self.__worldRoots["copyAoZhanRank"] = ( CopyAoZhanRank, True )
		self.__worldRoots["copyAoZhanResult"] = ( CopyAoZhanResult, True )
		self.__worldRoots["yiJieSignUp"] = ( YiJieSignUp, True )				# 异界战场报名界面
		self.__worldRoots["angerPoint"] = ( AngerPoint, True )					# 异界战场怒气点界面
		self.__worldRoots["yiJieScore"] = ( YiJieScore, True )					# 异界战场积分榜界面
		self.__worldRoots["yiJieBattleInfos"] = ( YiJieBattleInfos, True )		# 异界战场战况统计界面
		self.__worldRoots["tongAlliance"] = ( TongsAlliance, True )				# 帮会战场联盟战界面
		self.__worldRoots["slotMachine"] = ( SlotMachine, True )				# 老虎机
		self.__worldRoots["campFHLTRankWnd"] = ( CampFHLTRankWnd, True )			# 阵营烽火连天活动信息
		self.__worldRoots["campFHLTSign"] = ( CampFHLTSign, True )					# 阵营烽火连天报名

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def createRoot( self, hookName, UIClass, addToMgr = True ) :
		"""
		创建一个 Root UI 实例（注意：在这里创建的 UI 都是常驻内存的）
		@type				UIClass	 : classtype
		@param				UIClass	 : ui 类
		@type				hookName : str
		@param				hookName : ui 名称
		@type				addToMgr : bool
		@param				addToMgr : 是否添加到管理器（必须继承于 RootGUI 才能添加到管理器）
		"""
		pyRoot = UIClass()														# 创建实例
		setattr( ruisMgr, hookName, pyRoot )
		if addToMgr : ruisMgr.add( pyRoot, hookName )							# 添加到管理器
		uiSounder.initRootSound( pyRoot )

		if hookName in self.__comRoots :
			self.__comRoots.pop( hookName )
		if hookName in self.__loginRoots :
			self.__loginRoots.pop( hookName )
		if hookName in self.__worldRoots :
			self.__worldRoots.pop( hookName )									# 从列表中清除（只创建一次）

	# ---------------------------------------
	def getCommonRoots( self ) :
		"""
		创建通用 UI（无论登录时还是进入世界后都可以用）
		@rtype					: list
		@return					: [( 实例名, 类, 是否添加到 RootUIMgr ), ...]
		"""
		return [( r[0], r[1][0], r[1][1] ) for r in self.__comRoots.items()]

	def getLoginRoots( self ) :
		"""
		创建登录时实用的 UI（进入世界后不可以使用）
		@rtype					: list
		@return					: [( 实例名, 类, 是否添加到 RootUIMgr ), ...]
		"""
		return [( r[0], r[1][0], r[1][1] ) for r in self.__loginRoots.items()]

	# ---------------------------------------
	def getWorldRoots( self ) :
		"""
		进入世界状态 UI（进入世界后才能使用）
		@rtype					: list
		@return					: [( 实例名, 类, 是否添加到 RootUIMgr ), ...]
		"""
		# 常规显示的 UI
		return [( r[0], r[1][0], r[1][1] ) for r in self.__worldRoots.items()]

	# ---------------------------------------
	def createTempRoots( self ) :
		"""
		获取临时 UI（即给策划用的工具，不会随游戏一起发布）
		"""
		tmodules = SmartImport.importAll( "tools", "T_*" )
		for module in tmodules :
			members = inspect.getmembers( module )						# 获取模块中的所有成员名称
			for name, member in members :
				if not inspect.isclass( member ) : continue				# 过滤掉非类成员
				if not issubclass( member, RootGUI ) : continue			# 过滤掉不是继承于 RootGUI 的类
				if inspect.getmodule( member ) == module :				# 过滤掉不在当前模块中实现的成员
					pyTool = member()									# 创建工具实例

	# -------------------------------------------------
	def relateRoots( self ) :
		"""
		对窗口关系化
		"""
		pass


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
uiFactory = UIFactory()
