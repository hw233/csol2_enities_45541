# -*- coding: gb18030 -*-
#
# $Id: love3.py,v 1.238 2008-08-30 10:07:09 wangshufeng Exp $
#
# --------------------------------------------------------------------
# This is an Application Personality Script.
# It contains a few classes to control and maintain user interface components.
# Finally a series of BigWorld callback functions are implemented that allow the game's 'personality' to be configured,executed and terminated.
#
# -- 2007/09/08: tidied up by huangyongwei :
# -- ① grouped the imports
# -- ② move the global variables to the RDShare class, if you want to use the variables, you should import them as this: from love3 import rds
# -- ③ tidied up the camera param classes, and move the code about mouse handle camera to the param class
# -- ④ replevied the flexiable camera, and you can use flexiable camera or cursor camera
# -- ⑤ clear up codes in function "handleMouseEvent"
# -- ⑤ tidied up function "handleKeyEvent"
# -- ⑥ clear function "playAction" ( no one use )
# -- ⑦ tidied up function "start"
# -- ⑧ clear function "setCursor" ( no one use )
# -- ⑨ clear function "isFile" ( no one use, model "csol" contains a same function method )
#
# advice：
#	以后所有类似于：
#		from XXX import XXXX
#		g_xxx = XXX.instance()
#	的全局实例都放到 RDShare 中，作为 RDShare 的成员。
#	使用的时侯：
#		from gbref import rds
#		rds.xxx
#
# --------------------------------------------------------------------

"""
主版本：一般来说应该是1，指1.0版，由于现在还没正式发布，因此置为0
次(功能)版本：一般是用于有新功能增加的版本
修正版本：主要是指在bug修正的版本
MMdd：发布日期，如0806
"""
import Language
import Version
import reimpl_login
import config.client.labels.love3 as lbs_love3

versions = Version.getVersion()			# 主版本.次(功能)版本.修正版本.MMdd
serverName = Version.getServerName()	# 服务器名字

# -------------------------------------------
# python
# -------------------------------------------
import math

# -------------------------------------------
# engine
# -------------------------------------------
import BigWorld
import GUI
import csol
from Math import *

# -------------------------------------------
# common
# -------------------------------------------
from bwdebug import *
from LevelEXP import RoleLevelEXP
from LevelEXP import PetLevelEXP
from LevelEXP import VehicleLevelExp
from ItemSystemExp import StuffMergeExp
from ItemSystemExp import EquipStuddedExp
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import EquipBindExp
from ItemSystemExp import EquipQualityExp
from ItemSystemExp import EquipMakeExp
from ItemSystemExp import SpecialComposeExp
from ItemSystemExp import ItemTypeAmendExp
import csdefine
import csconst

# -------------------------------------------
# client global
# -------------------------------------------
import Define
import gbref
import IME
import items
import preload
from QuestModule import QTTask 								# 目的是让客户端在解析服务器任务达成目标的时候，有实例支持
import LoginMgr
import Helper
import PackChecker
import event.EventCenter as ECenter
import MessageBox

from keys import *
from gbref import rds
from items.EquipEffectLoader import EquipEffectLoader
from items.TalismanEffectLoader import TalismanEffectLoader
from CastIndicator import CastIndicator
from OpIndicator import OpIndicator
from QuestRelatedNPCVisible import QuestRelatedNPCVisible
from GlobalSkillMgr import GlobalSkillMgr

# managers
import TongSkillResearchData
import TongItemResearchData
import TongBeastData
import EntityCacheTask
import DamageStatisticMgr					# 玩家伤害输出统计
from WordsProfanity import WordsProfanity
from GameMgr import GameMgr
from StatusMgr import StatusMgr
from CamerasMgr import WorldCamHandler
from Sound import Sound
from LoginMgr import LoginMgr
from MapMgr import MapMgr
from ShortcutMgr import ShortcutMgr
from TargetMgr import TargetMgr
from HyperlinkMgr import HyperlinkMgr
from TitleMgr import TitleMgr
from ViewInfoMgr import ViewInfoMgr
from CustomCursor import CustomCursor
from ResourceLoader import ResourceLoader
from Helper import SystemHelper
from EffectMgr import EffectMgr
from RoleMaker import RoleModelMaker
from NPCDatasMgr import NPCDatasMgr
from ResourceMgr import resLoaderMgr

from TextFormatMgr import TextFormatMgr

from IconsSoundLoader import IconsSoundLoader
from NPCModelLoader import NPCModelLoader
from NPCVoiceLoader import NPCVoiceLoader
from ItemModelLoader import ItemModelLoader
from SpellEffectLoader import SpellEffectLoader
from EquipSuitLoader import EquipSuitLoader
from EquipParticleLoader import EquipParticleLoader
from skills.SpellBase.Effect import Effect
from ModelsFetchManager import ModelsFetchManager
from AreaEffectMgr import AreaEffectMgr
from EnvironmentsEffectMgr import EnvironmentsEffectMgr
from ActionMgr import ActionMgr
from CameraEventMgr import CameraEventMgr
from SpaceEffectMgr import SpaceEffectMgr
from GameSettingMgr import GameSettingMgr
from RoleFlyMgr import RoleFlyMgr
from CameraFlyMgr import CameraFlyMgr
from ClientSpaceCopyFormulas import ClientSpaceCopyFormulas
from GossipVoiceMgr import GossipVoiceMgr

##
import Action

# -------------------------------------------
# about ui
# -------------------------------------------
from guis.RootUIsMgr import RootUIsMgr
from guis.UIFactory import UIFactory
from guis.UIHandlerMgr import UIHandlerMgr
from guis.UIFixer import uiFixer
from guis.MutexShowMgr import MutexShowMgr
from RelationStaticModeMgr import RelationStaticModeMgr




# --------------------------------------------------------------------
# Method: init
# Description:
#	- The init function is called as part of the BigWorld Client initialisation process.
#	- It receives the configuration script in a parsable format.
#	- This is the best place to configure all the application-specific components, like initial Camera view, etc...
#	- init() creates a BigWorld Space and adds the parsed universe to it.
#	- It then creates a camera, configuring it using the values from the appropriate xml data section.
#	- It also creates the ChatConsole class, again using the xml data.
# --------------------------------------------------------------------
def init( scriptsConfig, engineConfig, userPreferences, loadingScreenGUI = None ):
	# ---------------------------------------
	# single piece instances
	# ---------------------------------------
	rds.gameMgr = GameMgr.instance()										# game manager
	rds.statusMgr = StatusMgr.instance()									# status machine
	rds.shortcutMgr = ShortcutMgr()											# shortcut manager
	rds.targetMgr = TargetMgr.instance()									# target manager
	rds.soundMgr = Sound.instance()											# set sound manager to global variable
	rds.worldCamHandler = WorldCamHandler()									# 世界状态中相机处理器
	rds.loginMgr = LoginMgr.instance()										# login space manager
	rds.mapMgr = MapMgr()													# 地图管理器
	rds.npcDatasMgr = NPCDatasMgr.instance()								# 管理纯客户端 npc 数据
	rds.hyperlinkMgr = HyperlinkMgr.instance()								# initialize decorator manager
	rds.titleMgr = TitleMgr.instance()										# 称号管理器
	rds.viewInfoMgr = ViewInfoMgr.instance()								# 自由可视信息设置管理器
	rds.ccursor = CustomCursor()											# 鼠标管理器
	rds.resLoader = ResourceLoader()										# resource loader

	rds.ruisMgr = RootUIsMgr()												# ui manager
	rds.uiHandlerMgr = UIHandlerMgr()										# ui handler manager
	rds.uiFactory = UIFactory()												# ui factory
	rds.mutexShowMgr = MutexShowMgr()										# 互斥窗口管理器

	rds.helper = Helper														# helper
	rds.castIndicator = CastIndicator()										# 道具使用指示器
	rds.opIndicator = OpIndicator()											# 操作指示器
	rds.textFormatMgr = TextFormatMgr.instance()							# 描述字体颜色
	rds.questRelatedNPCVisible = QuestRelatedNPCVisible()					# 任务相关NPC可见性
	rds.globalSkillMgr = GlobalSkillMgr()									# 全局特殊技能管理器

	rds.loginer = rds.loginMgr.loginer
	rds.roleSelector = rds.loginMgr.roleSelector
	rds.roleCreator = rds.loginMgr.roleCreator

	rds.wordsProfanity = WordsProfanity.instance()							# vocabulary filter for chat
	rds.damageStatistic = DamageStatisticMgr.statisticInstance

	rds.equipEffects = EquipEffectLoader.instance()							# 装备附加属性
	rds.talismanEffects = TalismanEffectLoader.instance()					# 法宝配置
	rds.stuffMerge = StuffMergeExp.instance()								# 材料合成
	rds.equipStudded = EquipStuddedExp.instance()							# 装备打孔
	rds.equipIntensify = EquipIntensifyExp.instance()						# 装备强化
	rds.equipBind = EquipBindExp.instance()									# 装备绑定
	rds.equipQuality = EquipQualityExp.instance()							# 品质信息
	rds.equipMake = EquipMakeExp.instance()									# 装备制造/改造
	rds.specialCompose = SpecialComposeExp.instance()						# 特殊合成
	rds.armorAmend = ItemTypeAmendExp.instance()							# 防具防御值类型修正
	rds.iconsSound = IconsSoundLoader.instance()							# 图标声音
	rds.npcModel = NPCModelLoader.instance()								# NPC模型配置
	rds.npcVoice = NPCVoiceLoader.instance()								# NPC发音配置
	rds.itemModel = ItemModelLoader.instance()								# 物品模型配置
	rds.spellEffect = SpellEffectLoader.instance()							# 光效配置
	rds.tongBeasData = TongBeastData.instance()								# 帮会神兽信息加载
	rds.equipsuit = EquipSuitLoader.instance()								# 装备的套装信息
	rds.vehicleExp = VehicleLevelExp.instance()								# 骑宠升级经验信息
	rds.itemsDict = items.instance()

	rds.roleMaker = RoleModelMaker.instance()								# 角色模型管理器
	rds.effectMgr = EffectMgr.instance()									# 效果管理器
	rds.equipParticle = EquipParticleLoader.instance()						# 装备强化、镶嵌效果信息
	rds.skillEffect = Effect.instance()										# 技能效果模块
	rds.modelFetchMgr = ModelsFetchManager.instance()						# 模型后线程加载管理模块
	rds.areaEffectMgr = AreaEffectMgr.instance()
	rds.enEffectMgr = EnvironmentsEffectMgr.instance()						# 环境效果管理模块
	rds.actionMgr = ActionMgr.instance()									# 动作播放管理模块
	rds.cameraEventMgr = CameraEventMgr.instance()							# 摄像头事件管理模块
	rds.spaceEffectMgr = SpaceEffectMgr.instance()							# 场景光效管理模块
	rds.gameSettingMgr = GameSettingMgr.instance()							# 游戏配置管理器
	rds.roleFlyMgr = RoleFlyMgr.instance()	        #玩家飞翔管理
	rds.cameraFlyMgr = CameraFlyMgr.instance()      #曲线飞翔摄像机管理
	rds.spaceCopyFormulas = ClientSpaceCopyFormulas.instance()				# 可排队副本信息管理器
	rds.gossipVoiceMgr = GossipVoiceMgr.instance()							# 对话语音管理器

	# ---------------------------------------
	# config data section
	# ---------------------------------------
	rds.scriptsConfig = scriptsConfig
	rds.engineConfig = engineConfig
	rds.userPreferences = userPreferences
	rds.loadingScreenGUI = loadingScreenGUI


	# ---------------------------------------
	# initialization
	# ---------------------------------------
	IME.initialize()
	PetLevelEXP.initialize()
	RoleLevelEXP.initialize()
	rds.gameMgr.init()
	
	if csol.isPublished():
		csol.setWindowTitle( lbs_love3.vonline % ( versions, serverName ) )	# 窗体名，在第一个进度条不会变化
	else:
		csol.setWindowTitle( lbs_love3.vhybrid % ( versions, serverName ) )
	csol.setWindowActiveCallback( onWindowsActive )


# --------------------------------------------------------------------
# Method: start
# Description:
#	- The start function is called after BigWorld has initialised and is used to begin the game.
#	- Although it receives no data, it uses the shared personality data to initiate the login process.
#	- Other instances may display an introduction or initiate some other game flow process...
# --------------------------------------------------------------------
@reimpl_login.deco_l3Start
def start():
	# ---------------------------------------
	# initialize
	# ---------------------------------------
	BigWorld.callback( 0.5, initCursor )									# 初始化鼠标，因为在本 Frame 内初始化无效，所以 Callback
	rds.soundMgr.initAudioSetting( rds.userPreferences )

	# 一些在发布版本里必须做的事情
	if isPublished:
		# 检查客户端版本，这个检查的由来是由于1.1.4版本更新给玩家的执行文件有一个bug，
		# 这个bug会使树木没有了碰撞，所以加入这个检查，
		# 以避免玩家保留这个版本的执行文件在后续的版本中继续使用。
		try:
			csol.versionGT25630()
		except Exception:
			ERROR_MSG( "游戏资源数据损坏，请重新安装游戏客户端。(1)" )		# 这个描述，是故意这样写的，不想写得太明白，让玩家知道太多的东西。
			MessageBox.showMessage( 0x0101, "", MessageBox.MB_OK, lambda x: gbref.rds.gameMgr.quitGame( False ) )
			return False

		# 无论如何，每次客户端起动，我们都检查一次所有的 space 资源包是否存在
		if not PackChecker.checkAllSpaceDir():
			ERROR_MSG( "游戏资源数据损坏，请重新安装游戏客户端。(2)" )
			MessageBox.showMessage( 0x0102, "", MessageBox.MB_OK, lambda x: gbref.rds.gameMgr.quitGame( False ) )
			return False
	return True


# --------------------------------------------------------------------
# when all resource initialized it will be called
# --------------------------------------------------------------------
def onEngineInitialized() :
	"""
	启动游戏后，引擎初始化资源完毕后被调用
	"""
	pass


# --------------------------------------------------------------------
# initialzie cursor for game
# --------------------------------------------------------------------
def initCursor() :
	"""
	initialize cursour
	"""
	mcursor = GUI.mcursor()
	BigWorld.setCursor( mcursor )
	rds.ccursor.normal()
	mcursor.visible = True
	BigWorld.setCustomProgress( 1 )

# --------------------------------------------------------------------
# Method: fini
# Description:
#	- The fini function is called when BigWorld is about to shutdown. It should be used to clean up the game.
# --------------------------------------------------------------------
def fini():
	try:
		BigWorld.player().onShutdown()
	except:
		pass


# --------------------------------------------------------------------
# Method: handleKeyEvent
# Description:
#	- This is called by BigWorld when a key is pressed.
# --------------------------------------------------------------------
def handleKeyEvent( down, key, mods ):
	imeHandler = csol.ImeHandle()
	if imeHandler.isCnInput() and csol.getShowCursorStatus() == 0:
		if key == KEY_MOUSE0 or key == KEY_MOUSE1 or key == KEY_MOUSE2:
			return True

	if rds.statusMgr.handleKeyEvent( down, key, mods ) :
		return True
	return False


# --------------------------------------------------------------------
# Method: handleMouseEvent
# Description:
#	- This is called by BigWorld when a mouse event is generated.
# --------------------------------------------------------------------

def handleMouseEvent( dx, dy, dz ):
	imeHandler = csol.ImeHandle()
	if imeHandler.isCnInput() and csol.getShowCursorStatus() == 0:
		return True
	result = False
	if rds.statusMgr.handleMouseEvent( dx, dy, dz ) :
		result = True
	return result


# --------------------------------------------------------------------
# Method: handleAxisEvent
# Description:
#    - This is called by BigWorld when ana axis event is generated.
# --------------------------------------------------------------------
def handleAxisEvent( axis, value, dTime ) :
	result = False
	if rds.statusMgr.handleAxisEvent( axis, value, dTime ) :
		result = True
	return result


# --------------------------------------------------------------------
# Method: onChangeEnvironments
# Description:
#	- This is called by BigWorld when player moves from inside to outside environment, or vice versa.
#	- It should be used to adapt any personality related data (eg, camera position/nature, etc).
# --------------------------------------------------------------------
def onChangeEnvironments( inside ):
	pass

# --------------------------------------------------------------------
# Method: onTimeOfDayLocalChange
# Description:
#    - This is called by BigWorld when Time of Day changes on the client
#    - It should only be used to sync game time from client to server
# --------------------------------------------------------------------
def onTimeOfDayLocalChange( gameTime, secondsPerGameHour ):
	try:
		BigWorld.player().cell.syncServTime(1, gameTime, secondsPerGameHour)
	except:
		pass

# --------------------------------------------------------------------
# Method: onRecreateDevice
# Description:
# 	- when resolution changed it will be called by engine
# --------------------------------------------------------------------
_preResolution = BigWorld.screenSize()							# 分辨率修改前的分辨率
def onRecreateDevice() :
	"""
	游戏启动过程中，不会调用该函数
	"""
	global _preResolution
	uiFixer.onResolutionChanged( _preResolution )
	ECenter.fireEvent( "EVT_ON_RESOLUTION_CHANGED", _preResolution )
	_preResolution = BigWorld.screenSize()


# --------------------------------------------------------------------
# functions for temporary use
# --------------------------------------------------------------------
def onCreateSpawnPoint( posstr, monsterType, territory, reviveTime ):
	player = BigWorld.player()
	player.cell.addSpawnPoint( monsterType, 0, eval(posstr), territory, reviveTime )

def onProxyDataDownloadComplete( proxyDataID, data ):
	"""
	This is a callback function that can be implemented by the user.

	If present, this method is called after a proxy data string is downloaded from the associated BaseApp proxy.
	"""
	if proxyDataID == csdefine.PROXYDATA_CSOL_VERSION:
		if data != versions:
			# "版本不匹配，请升级到最新版本。"
			ECenter.fireEvent( "EVT_ON_LOGIN_FAIL", 0x0103 )
			BigWorld.callback( 0, rds.gameMgr.accountLogoff )	# 不能直接在当前帧accountLogoff

def onWindowsActive( active ):
	"""
	窗口得失焦点回调
	"""
	rds.soundMgr.onWindowsActive( active )
	if not active:
		player = BigWorld.player()
		if ( hasattr(player,"isActionState") and player.isActionState( Action.ASTATE_CONTROL)) :
			player.stopMove()

def onSpaceData( spaceID, key, data ):
	"""
	This is a callback function present sapce data.
	"""
	try:
		spaceName = BigWorld.getSpaceName( spaceID )
	except ValueError, ve:
		spaceName = "noMapping"
	DEBUG_MSG( spaceID, spaceName, key, data )

def onAddMappingFailed( spaceID, key, path ):
	"""
	角色进入空间加载地图数据不成功的回调
	"""
	INFO_MSG( "cannot load mapping.spaceID:%i, spaceData key:%i, space mapping path:%s." % ( spaceID, key, path ) )

def preloadLoginSpace():
        loginMgr = __import__( "LoginMgr" )
        loginSpaceID = loginMgr.loginSpaceMgr.loadLoginSpace( Define.LOGIN_TYPE_MAP )
        camMgr = __import__( "CamerasMgr" )
        camMgr.LNCamHandler().use()
        BigWorld.cameraSpaceID( loginSpaceID )
        BigWorld.spaceHold( True )
        return loginSpaceID


def CameraNodeStartEven(id,magicGuiSound):
        """
        新的镜头动画开始触发
        add by wuxo 2011-9-30
        """
        eventIDs = magicGuiSound.split(";")
        for id in eventIDs:
                if id != "":
                        rds.cameraEventMgr.trigger(int(id))
        return True


def CameraNodeEndEven(id, paName, guiName):
        """
        新的镜头动画停止
        add by wuxo 2011-9-30
        """
        return True


def onCameraAnimationEndEven():
	"""
	所有镜头事件结束
	"""
	#无论任何情况 镜头事件结果恢复UI和玩家操作
	ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", 1 )
	for en in BigWorld.entities.values():
		if en.__class__.__name__ == "CameraModel":
			en.cameraEndEven()
	return True

#副本复活点
from SpaceCopyReviveConfigLoader import SpaceCopyReviveConfigLoader
g_SpaceCopyReviveCfg = SpaceCopyReviveConfigLoader.instance()
g_SpaceCopyReviveCfg.initCnfData()

g_relationStaticMgr = RelationStaticModeMgr.instance()
g_relationStaticMgr.initCampRelationCfg()
g_relationStaticMgr.createRelationInstance()

from QuestModule.QuestDataLoader import QuestDataLoader
g_questDataInst = QuestDataLoader.instance()
g_questDataInst.loadConfig( "config/quest/" )
