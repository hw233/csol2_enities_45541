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
# -- �� grouped the imports
# -- �� move the global variables to the RDShare class, if you want to use the variables, you should import them as this: from love3 import rds
# -- �� tidied up the camera param classes, and move the code about mouse handle camera to the param class
# -- �� replevied the flexiable camera, and you can use flexiable camera or cursor camera
# -- �� clear up codes in function "handleMouseEvent"
# -- �� tidied up function "handleKeyEvent"
# -- �� clear function "playAction" ( no one use )
# -- �� tidied up function "start"
# -- �� clear function "setCursor" ( no one use )
# -- �� clear function "isFile" ( no one use, model "csol" contains a same function method )
#
# advice��
#	�Ժ����������ڣ�
#		from XXX import XXXX
#		g_xxx = XXX.instance()
#	��ȫ��ʵ�����ŵ� RDShare �У���Ϊ RDShare �ĳ�Ա��
#	ʹ�õ�ʱ�
#		from gbref import rds
#		rds.xxx
#
# --------------------------------------------------------------------

"""
���汾��һ����˵Ӧ����1��ָ1.0�棬�������ڻ�û��ʽ�����������Ϊ0
��(����)�汾��һ�����������¹������ӵİ汾
�����汾����Ҫ��ָ��bug�����İ汾
MMdd���������ڣ���0806
"""
import Language
import Version
import reimpl_login
import config.client.labels.love3 as lbs_love3

versions = Version.getVersion()			# ���汾.��(����)�汾.�����汾.MMdd
serverName = Version.getServerName()	# ����������

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
from QuestModule import QTTask 								# Ŀ�����ÿͻ����ڽ���������������Ŀ���ʱ����ʵ��֧��
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
import DamageStatisticMgr					# ����˺����ͳ��
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
	rds.worldCamHandler = WorldCamHandler()									# ����״̬�����������
	rds.loginMgr = LoginMgr.instance()										# login space manager
	rds.mapMgr = MapMgr()													# ��ͼ������
	rds.npcDatasMgr = NPCDatasMgr.instance()								# �����ͻ��� npc ����
	rds.hyperlinkMgr = HyperlinkMgr.instance()								# initialize decorator manager
	rds.titleMgr = TitleMgr.instance()										# �ƺŹ�����
	rds.viewInfoMgr = ViewInfoMgr.instance()								# ���ɿ�����Ϣ���ù�����
	rds.ccursor = CustomCursor()											# ��������
	rds.resLoader = ResourceLoader()										# resource loader

	rds.ruisMgr = RootUIsMgr()												# ui manager
	rds.uiHandlerMgr = UIHandlerMgr()										# ui handler manager
	rds.uiFactory = UIFactory()												# ui factory
	rds.mutexShowMgr = MutexShowMgr()										# ���ⴰ�ڹ�����

	rds.helper = Helper														# helper
	rds.castIndicator = CastIndicator()										# ����ʹ��ָʾ��
	rds.opIndicator = OpIndicator()											# ����ָʾ��
	rds.textFormatMgr = TextFormatMgr.instance()							# ����������ɫ
	rds.questRelatedNPCVisible = QuestRelatedNPCVisible()					# �������NPC�ɼ���
	rds.globalSkillMgr = GlobalSkillMgr()									# ȫ�����⼼�ܹ�����

	rds.loginer = rds.loginMgr.loginer
	rds.roleSelector = rds.loginMgr.roleSelector
	rds.roleCreator = rds.loginMgr.roleCreator

	rds.wordsProfanity = WordsProfanity.instance()							# vocabulary filter for chat
	rds.damageStatistic = DamageStatisticMgr.statisticInstance

	rds.equipEffects = EquipEffectLoader.instance()							# װ����������
	rds.talismanEffects = TalismanEffectLoader.instance()					# ��������
	rds.stuffMerge = StuffMergeExp.instance()								# ���Ϻϳ�
	rds.equipStudded = EquipStuddedExp.instance()							# װ�����
	rds.equipIntensify = EquipIntensifyExp.instance()						# װ��ǿ��
	rds.equipBind = EquipBindExp.instance()									# װ����
	rds.equipQuality = EquipQualityExp.instance()							# Ʒ����Ϣ
	rds.equipMake = EquipMakeExp.instance()									# װ������/����
	rds.specialCompose = SpecialComposeExp.instance()						# ����ϳ�
	rds.armorAmend = ItemTypeAmendExp.instance()							# ���߷���ֵ��������
	rds.iconsSound = IconsSoundLoader.instance()							# ͼ������
	rds.npcModel = NPCModelLoader.instance()								# NPCģ������
	rds.npcVoice = NPCVoiceLoader.instance()								# NPC��������
	rds.itemModel = ItemModelLoader.instance()								# ��Ʒģ������
	rds.spellEffect = SpellEffectLoader.instance()							# ��Ч����
	rds.tongBeasData = TongBeastData.instance()								# ���������Ϣ����
	rds.equipsuit = EquipSuitLoader.instance()								# װ������װ��Ϣ
	rds.vehicleExp = VehicleLevelExp.instance()								# �������������Ϣ
	rds.itemsDict = items.instance()

	rds.roleMaker = RoleModelMaker.instance()								# ��ɫģ�͹�����
	rds.effectMgr = EffectMgr.instance()									# Ч��������
	rds.equipParticle = EquipParticleLoader.instance()						# װ��ǿ������ǶЧ����Ϣ
	rds.skillEffect = Effect.instance()										# ����Ч��ģ��
	rds.modelFetchMgr = ModelsFetchManager.instance()						# ģ�ͺ��̼߳��ع���ģ��
	rds.areaEffectMgr = AreaEffectMgr.instance()
	rds.enEffectMgr = EnvironmentsEffectMgr.instance()						# ����Ч������ģ��
	rds.actionMgr = ActionMgr.instance()									# �������Ź���ģ��
	rds.cameraEventMgr = CameraEventMgr.instance()							# ����ͷ�¼�����ģ��
	rds.spaceEffectMgr = SpaceEffectMgr.instance()							# ������Ч����ģ��
	rds.gameSettingMgr = GameSettingMgr.instance()							# ��Ϸ���ù�����
	rds.roleFlyMgr = RoleFlyMgr.instance()	        #��ҷ������
	rds.cameraFlyMgr = CameraFlyMgr.instance()      #���߷������������
	rds.spaceCopyFormulas = ClientSpaceCopyFormulas.instance()				# ���ŶӸ�����Ϣ������
	rds.gossipVoiceMgr = GossipVoiceMgr.instance()							# �Ի�����������

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
		csol.setWindowTitle( lbs_love3.vonline % ( versions, serverName ) )	# ���������ڵ�һ������������仯
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
	BigWorld.callback( 0.5, initCursor )									# ��ʼ����꣬��Ϊ�ڱ� Frame �ڳ�ʼ����Ч������ Callback
	rds.soundMgr.initAudioSetting( rds.userPreferences )

	# һЩ�ڷ����汾�������������
	if isPublished:
		# ���ͻ��˰汾�������������������1.1.4�汾���¸���ҵ�ִ���ļ���һ��bug��
		# ���bug��ʹ��ľû������ײ�����Լ��������飬
		# �Ա�����ұ�������汾��ִ���ļ��ں����İ汾�м���ʹ�á�
		try:
			csol.versionGT25630()
		except Exception:
			ERROR_MSG( "��Ϸ��Դ�����𻵣������°�װ��Ϸ�ͻ��ˡ�(1)" )		# ����������ǹ�������д�ģ�����д��̫���ף������֪��̫��Ķ�����
			MessageBox.showMessage( 0x0101, "", MessageBox.MB_OK, lambda x: gbref.rds.gameMgr.quitGame( False ) )
			return False

		# ������Σ�ÿ�οͻ����𶯣����Ƕ����һ�����е� space ��Դ���Ƿ����
		if not PackChecker.checkAllSpaceDir():
			ERROR_MSG( "��Ϸ��Դ�����𻵣������°�װ��Ϸ�ͻ��ˡ�(2)" )
			MessageBox.showMessage( 0x0102, "", MessageBox.MB_OK, lambda x: gbref.rds.gameMgr.quitGame( False ) )
			return False
	return True


# --------------------------------------------------------------------
# when all resource initialized it will be called
# --------------------------------------------------------------------
def onEngineInitialized() :
	"""
	������Ϸ�������ʼ����Դ��Ϻ󱻵���
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
_preResolution = BigWorld.screenSize()							# �ֱ����޸�ǰ�ķֱ���
def onRecreateDevice() :
	"""
	��Ϸ���������У�������øú���
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
			# "�汾��ƥ�䣬�����������°汾��"
			ECenter.fireEvent( "EVT_ON_LOGIN_FAIL", 0x0103 )
			BigWorld.callback( 0, rds.gameMgr.accountLogoff )	# ����ֱ���ڵ�ǰ֡accountLogoff

def onWindowsActive( active ):
	"""
	���ڵ�ʧ����ص�
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
	��ɫ����ռ���ص�ͼ���ݲ��ɹ��Ļص�
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
        �µľ�ͷ������ʼ����
        add by wuxo 2011-9-30
        """
        eventIDs = magicGuiSound.split(";")
        for id in eventIDs:
                if id != "":
                        rds.cameraEventMgr.trigger(int(id))
        return True


def CameraNodeEndEven(id, paName, guiName):
        """
        �µľ�ͷ����ֹͣ
        add by wuxo 2011-9-30
        """
        return True


def onCameraAnimationEndEven():
	"""
	���о�ͷ�¼�����
	"""
	#�����κ���� ��ͷ�¼�����ָ�UI����Ҳ���
	ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", 1 )
	for en in BigWorld.entities.values():
		if en.__class__.__name__ == "CameraModel":
			en.cameraEndEven()
	return True

#���������
from SpaceCopyReviveConfigLoader import SpaceCopyReviveConfigLoader
g_SpaceCopyReviveCfg = SpaceCopyReviveConfigLoader.instance()
g_SpaceCopyReviveCfg.initCnfData()

g_relationStaticMgr = RelationStaticModeMgr.instance()
g_relationStaticMgr.initCampRelationCfg()
g_relationStaticMgr.createRelationInstance()

from QuestModule.QuestDataLoader import QuestDataLoader
g_questDataInst = QuestDataLoader.instance()
g_questDataInst.loadConfig( "config/quest/" )
