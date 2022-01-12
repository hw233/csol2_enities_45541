# -*- coding: gb18030 -*-
#
# $Id: QuickBar.py,v 1.52 2008-09-02 10:26:25 fangpengjun Exp $

"""
implement root gui factory
2006/07/15: writen by huangyongwei
2008/05/06: add ch. comment
"""
from bwdebug import *
from guis import *
import ItemTypeEnum
import Language
import ResMgr
from cscustom import Rect
from AbstractTemplates import MultiLngFuncDecorator
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.controls.ProgressBar import HFProgressBar as ProgressBar
from guis.general.systemwindow.SystemWindow import  SystemWindow
from guis.general.autoFightWindow.AutoFightWindow import AutoFightWindow
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.share import defParser
from CopyTeamMenu import CopyTeamMenu
from PetBar import PetBar
from RaceBar import RaceBar
from SpaceSkillBar import SpaceSkillBar
from PostureBar import PostureBar
from SystemButton import SystemButton
from AutoFightBar import AutoFightBar
from GuardsBar import GuardsBar
from EnterItemPanel import EnterItemPanel
from QBItem import QBItem
from ItemsFactory import SkillItem
import skills as Skill
from ShortcutMgr import shortcutMgr
from LabelGather import labelGather
from cscustom import Polygon
from config.ChallengeAvatarSkills import MapDatas as challengeMapDatas
from config.client.msgboxtexts import Datas as mbmsgs
import csconst
import GUIFacade
import csdefine
from Function import Functor
import Const
from Time import Time
import Timer

POSTURE_IDX_MAP = {							# ��ͬ����̬��Ӧ��ͬ�Ŀ��������
	csdefine.ENTITY_POSTURE_NONE			: csdefine.QB_IDX_POSTURE_NONE,			# ����̬
	csdefine.ENTITY_POSTURE_DEFENCE			: csdefine.QB_IDX_POSTURE_DEFENCE,		# ����
	csdefine.ENTITY_POSTURE_VIOLENT			: csdefine.QB_IDX_POSTURE_VIOLENT,		# ��
	csdefine.ENTITY_POSTURE_DEVIL_SWORD		: csdefine.QB_IDX_POSTURE_DEVIL_SWORD,	# ħ��
	csdefine.ENTITY_POSTURE_SAGE_SWORD		: csdefine.QB_IDX_POSTURE_SAGEL_SWORD,	# ʥ��
	csdefine.ENTITY_POSTURE_SHOT			: csdefine.QB_IDX_POSTURE_SHOT,			# ����
	csdefine.ENTITY_POSTURE_PALADIN			: csdefine.QB_IDX_POSTURE_PALADIN,		# ����
	csdefine.ENTITY_POSTURE_MAGIC			: csdefine.QB_IDX_POSTURE_MAGIC,		# ����
	csdefine.ENTITY_POSTURE_CURE			: csdefine.QB_IDX_POSTURE_CURE,			# ҽ��
	}

SPACE_TYPES = [csdefine.SPACE_TYPE_BEFORE_NIRVANA, csdefine.SPACE_TYPE_CHALLENGE,csdefine.SPACE_TYPE_TEACH_KILL_MONSTER, csdefine.SPACE_TYPE_PLOT_LV40, csdefine.SPACE_TYPE_DANCECOPY_CHALLENGE, csdefine.SPACE_TYPE_DANCECOPY_PARCTICE]
KEYS_MAP = {"MINUS":"-","EQUALS":"=","BACKSLASH":"\\"}

class languageDepart( MultiLngFuncDecorator ):
	"""
	�����԰汾���������� by ����
	"""
	@staticmethod
	def locale_default( autoFightTimer ):
		"""
		�����
		"""
		languageDepart.originalFunc( autoFightTimer )
		autoFightTimer.endTime = Time.time() + Const.AUTO_FIGHT_PERSISTENT_TIME
		autoFightTimer._AutoFightTimer__detect()
		autoFightTimer.visible = True
		ECenter.fireEvent( "EVT_ON_LOCATED_NOTIFIER_POSITION", autoFightTimer.topToScreen - 2 )

	@staticmethod
	def locale_big5( autoFightTimer ):
		"""
		�����
		"""
		languageDepart.originalFunc( autoFightTimer )
		t = 0
		player = BigWorld.player()
		if player.af_time_extra > 0:
			t = player.af_time_extra
		else:
			t = player.af_time_limit
		autoFightTimer.endTime = Time.time() + t
		autoFightTimer._AutoFightTimer__detect()
		autoFightTimer.visible = True
		ECenter.fireEvent( "EVT_ON_LOCATED_NOTIFIER_POSITION", autoFightTimer.topToScreen - 2 )

class QuickBar( RootGUI ) :
	__qb_count = 39 												 	# �������ʾ��������
	def __init__( self ) :
		qb = GUI.load( "guis/general/quickbar/qb_wnd.gui" )
		uiFixer.firstLoadFix( qb )
		RootGUI.__init__( self, qb )
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.movable_ = False
		self.escHide_ = False
		self.moveFocus = False
		self.activable_ = False
		self.focus = True
		
		self.__isLocked = False											#�������Ƿ���ס
		self.__pyItems = {}
		self.__svrTimeCBID = 0
		self.__initSkills = {}
		self.__initialize( qb )

		self.__spellingItems = []										# ��¼����ʩ�ŵļ���
		self.__invalidItems = []										# ѡ�еĲ����ü���
		self.__cancelCoverCBID = 0
		self.__riseAutoCBID = 0
		self.__flashcbids = {}
		self.__cfgPath = ""
		self.__cfgSect = None
		self.__ignoreInits = set([])

		self.__eachPageCount = len( self.__pyItems )
		self.__maxPages = self.__qb_count / self.__eachPageCount
		self.__pageIndex = 0											# ��ǰҳ�������� 0 ��ʼ������ 1��
		#self.__setPageIndex( 0 )										# ��ʼ��Ϊ��һҳ

		self.__triggers = {}
		self.__registerTriggers()
		self.lackitems = []

	def __initialize( self, qb ) :
		self.__initQBItems( qb.skillBar )								# �������ܸ�

		self.__pyLbICndex = StaticText( qb.pageCtrl.lbPage )			# ҳ������ǩ
		self.__pyUpBtn = Button( qb.pageCtrl.upBtn )					# �Ϸ�ҳ��ť
		self.__pyUpBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyUpBtn.onLClick.bind( self.__pageUp )
		self.__pyDownBtn = Button( qb.pageCtrl.downBtn )				# �·�ҳ��ť
		self.__pyDownBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDownBtn.onLClick.bind( self.__pageDown )

		self.__pyAutoBtn = Button( qb.autoBtn )						# ��ʾ�Զ�ս������
		self.__pyAutoBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyAutoBtn.onLClick.bind( self.__swicthAutoFight )
		self.__pyAutoBtn.visible = False

		self.__pyPetBar = PetBar( qb.petBar )
		self.__pyPetBar.visible = False

		self.__pyAutoFightBar = AutoFightBar( qb.autoFightBar )
		self.autoFightBar = self.__pyAutoFightBar
		self.__pyAutoFightBar.visible = False
		self.__pyAutoFightBar.top = self.height + 2.0
		self.__pyAutoBtn.top = self.__pyAutoFightBar.top + 18.0
		self.__pyAutoBtn.visible = 0
		self.__autoFader = qb.autoFightBar.fader
		self.__autoFader.speed = 0.5
		self.__autoFader.value = 0.0

		self.__pyRaceBar = RaceBar( qb.raceBar, self )
		
		self.__pySpaceSkillBar = SpaceSkillBar( qb.spaceSkillBar, self )

		self.__pyExpBar = ProgressBar( qb.expBar )
		self.__pyExpBar.value = 0
		self.__pyExpBar.crossFocus = False
		
		self.__pyGuardsBar = GuardsBar( qb.guardsBar )
		self.__pyGuardsBar.visible = False

		self.__pyPostureBar = PostureBar( qb.postureBar )
		self.__pyPostureBar.visible = False

		win=GUI.Window("guis/empty.dds")
		self.__expBg=Control(win)
		self.__expBg.color=(255,255,255,0)
		self.__expBg.size=(528,8)
		self.__expBg.crossFocus=True
		qb.addChild(self.__expBg.gui)
		self.__expBg.h_anchor='LEFT'
		self.__expBg.gui.position=self.__pyExpBar.gui.position
		self.__expBg.onMouseEnter.bind( self.__onXBMouseEnter )
		self.__expBg.onMouseLeave.bind( self.__onXBMouseLeave )

		self.__pyStExp = StaticText( qb.expRate )
		self.__pyStExp.h_anchor = 'CENTER'
		self.__pyStExp.text = ""

		self.__autoFightText = AutoFightTimer( qb.autoFightText )
		self.__autoFightText.center = self.__pyAutoFightBar.center

		self.__pyStServerTime = StaticText( qb.stServerTime )
		self.__pyStServerTime.text = ""
		self.__pyStServerTime.fontSize = 12

		self.__pyAirTrPanel = PyGUI( qb.airTrPanel )
		self.__pyAirTrPanel.visible = False
		
		self.__pyAirIcon = Control( qb.airTrPanel.airIcon )
		self.__pyAirIcon.crossFocus = True
		self.__pyAirIcon.onMouseEnter.bind( self.__onShowAirPoint )
		self.__pyAirIcon.onMouseLeave.bind( self.__onHideAirPoint )
		
		self.__pyStAirPoint = StaticText( qb.airTrPanel.stAirPoint )
		self.__pyStAirPoint.text = ""

		self.__pyRtGuards = RichText( qb.rtGuards )
		self.__pyRtGuards.text = ""
		self.__pyRtGuards.visible = False

		self.__rangePolygon = Polygon([
										(68, 174), (121, 143), (148, 110), 
										(868, 110), (881, 143), (940, 174)
										])

	def dispose( self ) :
		RootGUI.dispose( self )
		self.__deregisterTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initQBItems( self, bar ) :
		for name, item in bar.children :
			if "item_" not in name : continue							# ��Ʒ������ǰ׺����Ϊ��item_��
			index = int( name.split( "_" )[1] )
			pyItem = QBSkItem( item )
			if index < 10:
				scTag = "B_QB_GRID_" + str( ( index + 1 ) % 10 )
			else:
				scTag = "B_QB_GRID_%s"%index
			scInfo = shortcutMgr.getShortcutInfo( scTag )
			scKeyStr = scInfo.shortcutString
			if index >= 10:
				scKeyStr = KEYS_MAP.get( scKeyStr, "" )
			pyItem.setScKeyStr( scKeyStr )
			pyItem.bindShortcut( scTag )
			pyItem.scTag = scTag
			self.__pyItems[index] = pyItem

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUICKBAR_UPDATE_ITEM"]	= self.__onUpdateItem				# ��ĳ����Ʒ�񱻸���ʱ����
		self.__triggers["EVT_ON_ROLE_EXP_CHANGED"] 		= self.__onUpdateEXP				# EXP changed trigger
		self.__triggers["EVT_ON_PET_ENTER_WORKLD"] 		= self.__onPetEnterWorld			# �������������ʱ������
		self.__triggers["EVT_ON_PET_LEAVE_WORLD"]		= self.__onPetLeaveWorld 			# ����leaveworldʱ����
		self.__triggers["EVT_ON_PET_WITHDRAWED"]		= self.__onPetWithdraw
#		self.__triggers["EVT_ON_ICON_PLAY"]				= self.__onIconPlay
		self.__triggers["EVT_ON_SHOW_SPELLING_COVER"]	= self.__onShowSpellingCover		# ������ʾ����ʩ�ŵļ���
		self.__triggers["EVT_ON_HIDE_SPELLING_COVER"]	= self.__onHideSpellingCover		# ���ؼ��ܵĸ�����ʾ
		self.__triggers["EVT_ON_SHOW_INVALID_COVER"]	= self.__onShowInvalidCover			# ��������ü���ʱ��ʾ��ɫ�߿�
		self.__triggers["EVT_ON_START_AUTOFIGHT"]		= self.__onStartAutoFight			# �Զ�ս����ʼ
		self.__triggers["EVT_ON_STOP_AUTOFIGHT"]		= self.__onStopAutoFight			# �Զ�ս��ֹͣ
		self.__triggers["EVT_ON_AUTO_FIGHT_BAR_SHOW"]	= self.__onAutoFightBarShow			# �Զ�ս������ʾʱ�����Զ�ս��ʣ��ʱ���λ��
		self.__triggers["EVT_ON_AUTO_FIGHT_BAR_HIDE"]	= self.__onAutoFightBarHide			# �Զ�ս��������ʱ�����Զ�ս��ʣ��ʱ���λ��
		self.__triggers["EVT_ON_AUTO_NOR_SKILL_CHANGE"] = self.__onAutoSkChange				# �Զ��������ܸı�
		self.__triggers["EVT_ON_STOP_AUTO_SKILL"]		= self.__onAutoSkStop
		self.__triggers["EVT_ON_QUEST_TASK_STATE_CHANGED"] = self.__onQuestStateChanged
		self.__triggers["EVT_ON_AUTO_FIGHT_TIMER_SHOW_ONLY"] = self.__onAFOnlyTimerShow
		self.__triggers["EVT_ON_PLAYER_POSTURE_CHANGED"] = self.__onPostureChanged			# �����̬�ı�
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"]	= self.__onRoleLevelChanged
		self.__triggers["EVT_ON_ENTER_SPECIAL_COPYSPACE"] = self.__onEnterSpaceCopy
		self.__triggers["EVT_ON_CLOSE_COPY_INTERFACE"] = self.__onLeaveSpaceCopy
		self.__triggers["EVT_ON_TEMP_SHORTCUT_TAG_SET"] = self.__onOnShortcutSet
		self.__triggers["EVT_ON_SKILL_TRIGGER_SPELL"] = self.__onTriggerSpell
		self.__triggers["EVT_ON_QUEST_LOG_ADD"]			= self.__onQuestAdd
		self.__triggers[ "EVT_ON_TRIGGER_PG_CONTROL_PANEL" ] = self.__onTriggerPGShow
		self.__triggers[ "EVT_ON_HIDE_PG_CONTROL_PANEL" ] = self.__onTriggerPGHide
		self.__triggers[ "EVT_ON_PLAYERROLE_ACCUMPOINT_CHANGE" ] = self.__onRoleAccumChange
		self.__triggers["EVT_ON_PLAYERROLE_ADD_SKILL"] = self.__onAddSkill
		self.__triggers["EVT_ON_QB_REMOVE_INITE_SKILL"] = self.__onQBRemoveInitSk
		self.__triggers["EVT_ON_SHOW_YXLMCOPY_MINIMAP"] = self.__onTrigSoulCionShow
		self.__triggers["EVT_ON_HIDE_YXLMCOPY_MINIMAP"] = self.__onTrigSoulCionHide
		self.__triggers["EVT_ON_LOCK_QUICKBAR"] = self.__onLockQuickBar					# ��ס������
		self.__triggers["EVT_ON_UNLOCK_QUICKBAR"] = self.__onUnlockQuickBar				# ����������
		self.__triggers["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onMountVehicle #������
		self.__triggers["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onDisMountVehicle #������

		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __setPageIndex( self, pgIndex ) :
		"""
		����ҳ����
		"""
		if not rds.statusMgr.isInWorld() : return
		player = BigWorld.player()
		skills = player.spaceSkillList
		pgIndex = pgIndex % self.__maxPages
		self.__pageIndex = pgIndex
		self.__pyLbICndex.text = str( pgIndex + 1 )
		spaceType = player.spaceSkillSpaceType
		isChallengeSpace = spaceType == csdefine.SPACE_TYPE_CHALLENGE
		posture = player.posture
		if pgIndex == 0 and not isChallengeSpace:				# ���ڼ�������̬������������Ҫ
			pgIndex = POSTURE_IDX_MAP[posture]			# ������ҵ���̬ȷ�������������
		itemInfos = player.qb_getItems()
		start = pgIndex * self.__eachPageCount
		if spaceType in SPACE_TYPES and len( skills ):  # ������һЩ���пռ似�ܵĸ�����
			for index, pyItem in self.__pyItems.iteritems() :			# �л���̬��ʱ����Ҫ�����ռ似��
				gbIndex = start + index
				pyItem.gbIndex = gbIndex
				itemInfo = itemInfos.get( gbIndex, None )
				if itemInfo:
					itemId = itemInfo.id
					chMapSkill = self.__getChMapSkill( itemId, skills )
					if chMapSkill:
						skill = Skill.getSkill( chMapSkill )
						itemInfo = SkillItem( skill )
				pyItem.update( itemInfo )
				pyItem.updateIconState()
				skItem = pyItem.skItem
				skItem.dragFocus = isChallengeSpace
				skItem.dropFocus = isChallengeSpace
		else:
			for index, pyItem in self.__pyItems.iteritems():
				gbIndex = start + index
				itemInfo = itemInfos.get( gbIndex, None )
				initInfo = None
				isNotInit = False
				for intSkid, initSkill in self.__initSkills.items():
					qbIndex = initSkill.qbIndex
					isPosture = initSkill.isPosture
					skPosture = initSkill.posture
					if ( posture == skPosture or skPosture == csdefine.ENTITY_POSTURE_NONE ) or \
					 posture ==csdefine.ENTITY_POSTURE_NONE:
						qbIndex = initSkill.qbIndex + start
					if (intSkid, qbIndex) in self.__ignoreInits:
						continue
					if gbIndex == qbIndex and itemInfo is None:
						mapSkid, isHas = self._getMapSkillID( intSkid )
						skill = Skill.getSkill( mapSkid )
						initInfo = SkillItem( skill )
						if isHas and posture != csdefine.ENTITY_POSTURE_NONE and \
						pgIndex == POSTURE_IDX_MAP[posture]:
							player.qb_updateItem( gbIndex, csdefine.QB_ITEM_SKILL, skill )
				if itemInfo is None and \
				pgIndex == POSTURE_IDX_MAP[posture] and \
				initInfo:
					itemInfo = initInfo
				if itemInfo is not None:
					if hasattr( itemInfo, "qbType" ) and itemInfo.qbType != csdefine.QB_ITEM_SKILL:
						isNotInit = True
					else:
						isNotInit = itemInfo.id in player.skillList_	# ֻ�м��ܲ���Ҫ�ж��Ƿ�����Ҽ����б���
				pyItem.gbIndex = gbIndex
				pyItem.update( itemInfo, isNotInit )
				pyItem.updateIconState()
				isEffect = initInfo is not None and pyItem.isLearnable( player.level )
				pyItem.isShowEffect( isEffect )

	def _getMapSkillID( self, initSkillID ):
		player = BigWorld.player()
		for skillID in player.skillList_:
			if skillID/1000 == initSkillID/1000:
				return skillID, True
		return initSkillID, False
	# -------------------------------------------------
	def __onShowSpellingCover( self, skillID ) :
		"""
		�ø���ͼ���ʶ����ʩ�ŵļ���
		@param		skillID	:	����ID
		@type		skillID	:	SKILLID( INT64 )
		"""
		self.__onHideSpellingCover()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__spellingItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__spellingItems.append( pyItem )
				toolbox.itemCover.showSpellingItemCover( pyItem.skItem )

	def __onHideSpellingCover( self ) :
		"""
		����ͼ��ĸ�����ʾ״̬
		"""
		for pyItem in self.__spellingItems :
			toolbox.itemCover.hideItemCover( pyItem.skItem )
		self.__spellingItems = []

	def __onShowInvalidCover( self, skillID ) :
		"""
		��������ü���ʱ�ú�ɫ�߿���ʾ
		"""
		BigWorld.cancelCallback( self.__cancelCoverCBID )
		self.__hideInvalidItemCovers()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__invalidItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__invalidItems.append( pyItem )
				toolbox.itemCover.showInvalidItemCover( pyItem.skItem )
		self.__cancelCoverCBID = BigWorld.callback( 1, self.__hideInvalidItemCovers )		# �����1����Զ�����

	def __hideInvalidItemCovers( self ) :
		"""
		���ز����ü��ܵĺ�ɫ�߿�
		"""
		for pyItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pyItem.skItem )
		self.__invalidItems = []

	def __onUpdateItem( self, gbIndex, itemInfo ) :
		"""
		����ĳ����Ʒ��
		"""
		index = gbIndex % self.__eachPageCount
		pySkItem = self.__pyItems.get( index )
		if pySkItem.gbIndex != gbIndex :
			#INFO_MSG( "Quick bar update item %s, but it is not in current line!" % itemInfo.id )
			return
		pySkItem.update( itemInfo )
		pySkItem.updateIconState()

	def __updateIconsState( self ) :
		"""
		���¸���ͼ����ɫ
		"""
		for pyItem in self.__pyItems.itervalues():
			if pyItem and pyItem.itemInfo:
				pyItem.updateIconState()

	def __onPetEnterWorld( self, dbid ):
		self.__pyPetBar.visible = True			# �������������ʱ��ʾ�����13:14 2008-6-18��wsf
		self.__pyPetBar.onPetEnterWorld()
#		toolbox.infoTip.showOperationTips( 0x004e, self.__pyPetBar, Rect( (300, 0), (158, 36) ) )
#		toolbox.infoTip.showOperationTips( 0x004f, self.__pyPetBar, Rect( (0, 0), (160, 40) ) )
		self.__layoutAutoBar()

	def __onPetLeaveWorld( self, dbid ):
		self.__pyPetBar.visible = False
		toolbox.infoTip.hideOperationTips( 0x004e )
		toolbox.infoTip.hideOperationTips( 0x004f )
		self.__layoutAutoBar()

	def __onPetWithdraw( self, dbid ):
		self.__pyPetBar.visible = False
		toolbox.infoTip.hideOperationTips( 0x004e )
		toolbox.infoTip.hideOperationTips( 0x004f )
		self.__layoutAutoBar()

	def __layoutAutoBar( self ):
		"""
		�����Զ�ս����λ��
		"""
		if self.__pyPetBar.visible:
			self.__pyAutoFightBar.bottom = self.__pyPetBar.top - 2.0
			if self.__pyGuardsBar.visible:
				self.__pyGuardsBar.bottom = self.__pyAutoFightBar.bottom
				self.__pyAutoFightBar.left = self.__pyGuardsBar.right + 2.0
			else:
				self.__pyAutoFightBar.center = self.__pyPetBar.center
		else:
			self.__pyAutoFightBar.bottom = self.__pyPetBar.bottom - 2.0
			if self.__pyGuardsBar.visible:
				self.__pyGuardsBar.bottom = self.__pyAutoFightBar.bottom
				self.__pyAutoFightBar.left = self.__pyGuardsBar.right + 2.0
			else:
				self.__pyAutoFightBar.center = self.__pyPetBar.center
		bottom = self.bottom - ( self.height - self.__pyAutoFightBar.top )
		rds.ruisMgr.chatWindow.bottom = bottom
		self.__pyAutoBtn.top = self.__pyAutoFightBar.top + 18.0
		self.__pyAutoBtn.left = self.__pyAutoFightBar.right - 18.0
		self.__autoFightText.center = self.__pyAutoFightBar.center
		self.__autoFightText.bottom = self.__pyAutoFightBar.top - 2.0

	def __initialAutoBar( self ):
		"""
		�����Զ�ս������ʼ��λ��
		"""
		if self.__pyGuardsBar.visible:
			self.__pyAutoFightBar.left = self.__pyGuardsBar.right + 2.0
		else:
			self.__pyAutoFightBar.center = self.__pyPetBar.center
		self.__pyAutoBtn.left = self.__pyAutoFightBar.right - 18.0
		self.__autoFightText.center = self.__pyAutoFightBar.center

	def __onIconPlay( self, itemInfo ):
		if not rds.statusMgr.isInWorld():
			return
		else:
			if self.__pyEnterItemPanel.isPlaying:#��һ��ͼ�궯��û�в�����
				return
			else:
				self.__pyEnterItemPanel.onPlayIcon( itemInfo )

	def __onUpdateEXP( self, inreasedExp, reason ) :
		"""
		update exp
		"""
		player = BigWorld.player()
		xp = player.getEXP()
		xpMax = player.getEXPMax()
		xp = float( xp )
		if xpMax <= 0 :
			self.__pyExpBar.value = 0
		else :
			value = xp / xpMax
			self.__pyExpBar.value = xp / xpMax
			if value < 0.0001:		# ���뾫�ȿ��ƣ�����value̫Сpythonʹ�ÿ�ѧ��������ʾ�����ʾ����ȷ�����⡣
				self.__pyStExp.text = "0.0%"
				return
			textList = str( value * 100 ).split( "." )
			self.__pyStExp.text = "%s%%" % ( textList[0] + "." + textList[1][0] )

	# -------------------------------------------------
	def __pageUp( self ) :
		"""
		����Ϸ�ҳ��ťʱ������
		"""
		self.__setPageIndex( self.__pageIndex + 1 )

	def __pageDown( self ) :
		"""
		����·�ҳ��ťʱ������
		"""
		self.__setPageIndex( self.__pageIndex - 1 )

	def __swicthAutoFight( self ):
		"""
		�л��Զ�ս����
		"""
		self.__pyAutoFightBar.visible = not self.__pyAutoFightBar.visible
		self.autoBarShow = self.__pyAutoFightBar.visible
		toolbox.infoTip.hideOperationTips( 0x0090 )
		toolbox.infoTip.hideOperationTips( 0x0091 )
		toolbox.infoTip.hideOperationTips( 0x0092 )
		if self.__pyPetBar.visible:
			toolbox.infoTip.hideOperationTips( 0x0093 )
		bottom = rds.ruisMgr.chatWindow.bottom
		if self.autoBarShow:
			bottom = self.bottom - ( self.height - self.__pyAutoFightBar.top )
		else:
			bottom = self.bottom - ( self.height - self.__pyAutoFightBar.bottom )
		if not self.__pyGuardsBar.visible:
			rds.ruisMgr.chatWindow.bottom = bottom

	def __onXBMouseEnter( self, pyPB ) :
		player = BigWorld.player()
		xp = player.getEXP()
		xpMax = player.getEXPMax()
		if pyPB == self.__expBg :
			msg = "%d/%d" % ( xp, xpMax )
			toolbox.infoTip.showToolTips( self.__expBg, msg )

	def __onXBMouseLeave( self, pyPB ) :
		toolbox.infoTip.hide()

	def __onAutoFightBarShow( self ) :
		self.__autoFightText.bottom = self.__pyAutoFightBar.top - 2

	def __onAutoFightBarHide( self ) :
		self.__autoFightText.bottom = self.__pyAutoFightBar.bottom - 2

	def __onStartAutoFight( self ):
		"""
		�Զ�ս����ʼ��
		"""
		self.__autoFightText.start()
		if self.__pyAutoFightBar.visible:
			self.__autoFightText.bottom = self.__pyAutoFightBar.top - 2
		else:
			self.__autoFightText.bottom = self.__pyAutoFightBar.bottom - 2

	def __onStopAutoFight( self ):
		"""
		�Զ�ս��ֹͣ
		"""
		self.__autoFightText.stop()

	def __onAutoSkChange( self, defaultSkID ):
		"""
		��ҫ�Զ�ʩ�ż���
		"""
		for index, pyItem in self.__pyItems.items():
			if pyItem.itemInfo is None:continue
			skItem = pyItem.skItem
			if pyItem.itemInfo.id == defaultSkID:
				skItem.showAutoParticle()
			else:
				skItem.hideAutoParticle()

	def __onAutoSkStop( self, defaultSkID ):
		for index, pyItem in self.__pyItems.items():
			if pyItem.itemInfo is None:continue
			if pyItem.itemInfo.id == defaultSkID:
				skItem = pyItem.skItem
				skItem.hideAutoParticle()
				break

	def __onQuestStateChanged( self, questID, taskIndex ) :
		"""
		����״̬�ı�ʱ����
		"""
		if questID == 10201051 : 					# ������񡰶��ž�ѧ��
			questNodes = GUIFacade.getObjectiveDetail( questID )
			isCompleted = True
			for qNode in questNodes :
				isCompleted = isCompleted and qNode[5]
			if isCompleted :
				areTipsShow = False
				if areTipsShow :
					BigWorld.callback( 30, self.__hideOpTips )
					
	def __onQuestAdd( self, questID ) :
		"""�������"""
		player = BigWorld.player()
		if player.hasAutoFight: return
		if questID in Const.SHOW_AUTOBAR_QUEST_LIST:
			def query( rs_id ):
				if rs_id == RS_OK:
					BigWorld.cancelCallback( self.__riseAutoCBID )
					self.__pyAutoFightBar.visible = True
					player.cell.openAutoFight()	 # �����Զ�ս������
					self.__initialAutoBar()
					self.__riseAutoCBID = BigWorld.callback( 0.0, self.__riseAutoBar )
			pyOkBox = showMessage( 0x0ec5, "", MB_OK, query, self )
			pyOkBox.escHide_ = False
			pyOkBox.pyCloseBtn_.visible = False
	
	def __onTriggerPGShow( self, skills ):
		"""
		�����̹��ٻ�������
		"""
		return
		self.__pyGuardsBar.visible = True
		self.__pyAirTrPanel.visible = True
		self.__pyRtGuards.visible = True
		self.__layoutAutoBar()
		self.__pyGuardsBar.initMapSkills( skills )
	
	def __onTriggerPGHide( self ):
		"""
		�����̹��ٻ�������
		"""
		return
		self.__pyGuardsBar.visible = False
		self.__pyAirTrPanel.visible = False
		self.__pyRtGuards.visible = False
		self.__pyGuardsBar.reset()
		self.__layoutAutoBar()
	
	def __onRoleAccumChange( self, accumPoint ):
		"""
		���˵�仯
		"""
		self.__pyStAirPoint.text = labelGather.getText( "quickbar:guardsBar", "airTrans" )%accumPoint
	
	def __onAddSkill( self, skillInfo ):
		"""
		��Ӽ��ܴ���
		"""
		if skillInfo is None:return
		player = BigWorld.player()
		skillid = skillInfo.id
		baseItem = skillInfo.baseItem
		pgIndex = POSTURE_IDX_MAP[player.posture]
		start = pgIndex * self.__eachPageCount
		for initSkid, initSkill in self.__initSkills.items():
			qbIndex = initSkill.qbIndex
			posture = initSkill.posture
			gbIndex = qbIndex + start
			if skillid/1000 == initSkid/1000:
				player.qb_updateItem( gbIndex, csdefine.QB_ITEM_SKILL, baseItem )
				if player.posture > 0:
					player.qb_updateItem( gbIndex - start, csdefine.QB_ITEM_SKILL, baseItem )
				else:
					pgIndex = POSTURE_IDX_MAP[posture]
					start = pgIndex * self.__eachPageCount
					player.qb_updateItem( qbIndex + start, csdefine.QB_ITEM_SKILL, baseItem )
				pyItem = self.__pyItems.get( qbIndex, None )
				if pyItem is None:return
				order = 0
				while order in self.__flashcbids : order += 1
				pyItem.startFlash()
				pyItem.removeEffect()
				self.__flashcbids[order] = BigWorld.callback( 10.0, Functor( self.__stopFlash, pyItem, order ) )
	
	def __onQBRemoveInitSk( self, skillID, gbIndex ):
		"""
		�Ƴ���ʼ����
		"""
		if skillID in self.__initSkills and \
		not (skillID,gbIndex) in self.__ignoreInits:
			sect = self.__cfgSect.createSection( str(skillID) )
			sect.writeInt64( "skillID", skillID )
			sect.writeInt( "gbIndex", gbIndex )
			self.__cfgSect.save()
			ResMgr.purge( self.__cfgPath )
			self.__ignoreInits.add((skillID, gbIndex))
	
	def __onTrigSoulCionShow( self, spaceLabel ):
		"""
		��ʾ����
		"""
		self.__pyAirTrPanel.visible = True
		self.__pyStAirPoint.text = labelGather.getText( "quickbar:guardsBar", "airTrans" )%BigWorld.player().accumPoint
		
	def __onLockQuickBar( self ):
		"""
		��ס���ܿ����
		"""
		self.__isLocked = True
		self.__updateIconsState()
		self.__pyAutoFightBar.updateIconState()
		
	def __onUnlockQuickBar( self ):
		"""
		�������ܿ����
		"""
		self.__isLocked = False
		self.__updateIconsState()
		self.__pyAutoFightBar.updateIconState()
		
	def __onMountVehicle( self ):
		"""
		�����ص�
		"""
		self.__updateIconsState()
		
	def __onDisMountVehicle( self ):
		"""
		�����ص�
		"""
		self.__updateIconsState()

	def __onTrigSoulCionHide( self ):
		"""
		��������
		"""
		self.__pyAirTrPanel.visible = False
		self.__pyStAirPoint.text = ""
	
	def __stopFlash( self, pyItem,order ):
		pyItem.stopFlash()
		BigWorld.cancelCallback( self.__flashcbids.pop( order ) )
	
	def __onShowAirPoint( self, pyAirIcon ):
		if pyAirIcon is None:return
		spaceLabel = BigWorld.player().getSpaceLabel()
		airInfo = labelGather.getText( "quickbar:guardsBar", "airPoints" )
		if spaceLabel == "fu_ben_ying_xiong_lian_meng_01":
			airInfo = labelGather.getText( "quickbar:guardsBar", "soulCoins" )
		toolbox.infoTip.showToolTips( pyAirIcon, airInfo )
	
	def __onHideAirPoint( self ):
		toolbox.infoTip.hide()

	def __onAFOnlyTimerShow( self, times ):
		"""
		ֻ��ʾ�Զ�ս��ʱ�� by ����
		"""
		self.__onAutoFightBarShow()
		self.__autoFightText.startTimeOnly( times )

	def __hideOpTips( self ) :
		pass
#		toolbox.infoTip.hideOperationTips( 0x0090 )
#		toolbox.infoTip.hideOperationTips( 0x0091 )
#		toolbox.infoTip.hideOperationTips( 0x0092 )
#		toolbox.infoTip.hideOperationTips( 0x0093 )

	def __onPostureChanged( self, newPosture, oldPosture ) :
		"""
		�����̬�����ı�
		@param		newPosture : ����̬
		@param		oldPosture : ����̬
		"""
		player = BigWorld.player()
		spaceType = player.spaceSkillSpaceType
		if spaceType == csdefine.SPACE_TYPE_CHALLENGE: return
		if self.__pageIndex == 0 :									# �����ǰ���������
			self.__setPageIndex( self.__pageIndex )					# ��ˢ��һ����������
			if newPosture == csdefine.ENTITY_POSTURE_NONE:
				return
			pgIndex = POSTURE_IDX_MAP[newPosture]
			start = pgIndex * self.__eachPageCount
			itemInfos = player.qb_getItems()
		self.__updateIconsState()

	def __onRoleLevelChanged( self, oldLevel, newLevel ):
		"""
		��ɫ�ȼ��ı�
		"""
		player = BigWorld.player()
		for pyItem in self.__pyItems.values():
			itemInfo = pyItem.itemInfo
			if itemInfo is None:continue
			itemId = itemInfo.id
			if itemId in self.__initSkills and \
			pyItem.isLearnable( newLevel ) and \
			not itemId in player.skillList_:
				pyItem.addEffect()
		if player.hasAutoFight: return
		if newLevel >= Const.SHOW_AUTOBAR_LEVEL_LIMITED and oldLevel < Const.SHOW_AUTOBAR_LEVEL_LIMITED:
			def query( rs_id ):
				if rs_id == RS_OK:
					BigWorld.cancelCallback( self.__riseAutoCBID )
					self.__pyAutoFightBar.visible = True
					player.cell.openAutoFight()	 # �����Զ�ս������
					self.__initialAutoBar()
					self.__riseAutoCBID = BigWorld.callback( 0.0, self.__riseAutoBar )
			pyOkBox = showMessage( 0x0ec5, "", MB_OK, query, self )
			pyOkBox.escHide_ = False
			pyOkBox.pyCloseBtn_.visible = False

	def __onEnterSpaceCopy( self, skills, spaceType ):
		if spaceType in SPACE_TYPES:
			isChallengeSpace = spaceType == csdefine.SPACE_TYPE_CHALLENGE
			self.__pyUpBtn.enable = isChallengeSpace
			self.__pyDownBtn.enable = isChallengeSpace
			itemInfos = BigWorld.player().qb_getItems()
			for index, pySkItem in self.__pyItems.items():
				if isChallengeSpace:
					start = self.__pageIndex * self.__eachPageCount
					gbIndex = start + index
					itemInfo = itemInfos.get( gbIndex, None )
					if itemInfo:
						itemId = itemInfo.id
						chMapSkill = self.__getChMapSkill( itemId, skills )
						if chMapSkill:
							skill = Skill.getSkill( chMapSkill )
							itemInfo = SkillItem( skill )
				elif spaceType in [ csdefine.SPACE_TYPE_PLOT_LV40 ,csdefine.SPACE_TYPE_DANCECOPY_CHALLENGE, csdefine.SPACE_TYPE_DANCECOPY_PARCTICE ] :
					self.__pyUpBtn.enable = False
					self.__pyDownBtn.enable = False 
					if index < len(BigWorld.player().spaceSkillList):
						spSkId = BigWorld.player().spaceSkillList[index]
						skill = Skill.getSkill( spSkId )
						itemInfo = SkillItem( skill )
					else:
						itemInfo = None
				else:
					spSkId = BigWorld.player().spaceSkillList[index]
					skill = Skill.getSkill( spSkId )
					itemInfo = SkillItem( skill )
				pySkItem.update( itemInfo )
				pySkItem.updateIconState()
				skItem = pySkItem.skItem
				skItem.dragFocus = isChallengeSpace
				skItem.dropFocus = isChallengeSpace

	def __onLeaveSpaceCopy( self ):
		self.__pyUpBtn.enable = True
		self.__pyDownBtn.enable = True
		self.__setPageIndex( self.__pageIndex )
		for pyItem in self.__pyItems.values():
			skItem = pyItem.skItem
			if not skItem.dragFocus:
				skItem.dragFocus = True
			if not skItem.dropFocus:
				skItem.dropFocus = True

	def __onOnShortcutSet( self, tag, keyStr ):
		for pyItem in self.__pyItems.values():
			if pyItem.scTag == tag:
				if keyStr in KEYS_MAP:
					keyStr = KEYS_MAP[keyStr]
				pyItem.setScKeyStr( keyStr )

	def __onTriggerSpell( self, ptSkID, skillID ):
		"""
		�������ܴ���
		"""
		if skillID != 0:
			for pyItem in self.__pyItems.values():
				itemInfo = pyItem.itemInfo
				if itemInfo is None:continue
				if itemInfo.id == ptSkID:
					pyItem.ptSkID = ptSkID
					skill = Skill.getSkill( skillID )
					skillInfo = SkillItem( skill )
					pyItem.update( skillInfo )
				if pyItem.ptSkID == ptSkID:
					skill = Skill.getSkill( skillID )
					skillInfo = SkillItem( skill )
					pyItem.update( skillInfo )
		else:
			for pyItem in self.__pyItems.values():
				itemInfo = pyItem.itemInfo
				if itemInfo is None:continue
				if pyItem.ptSkID == ptSkID:
					skill = Skill.getSkill( ptSkID )
					skillInfo = SkillItem( skill )
					pyItem.update( skillInfo )
					pyItem.ptSkID = 0

	def __riseAutoBar( self ):
		"""
		���������Զ�ս����
		"""
		self.__pyAutoFightBar.bottom -= 7.0
		self.__autoFader.value += 0.1
		if self.__pyPetBar.visible:	#���＼�����ɼ�
			if self.__pyAutoFightBar.bottom <= self.__pyPetBar.top - 2.0:
				self.__cancelRiseAuto()
				return
		else:
			if self.__pyAutoFightBar.bottom <= self.__pyPetBar.bottom - 2.0:
				self.__cancelRiseAuto()
				return
		self.__pyAutoBtn.top = self.__pyAutoFightBar.top + 18.0
		self.__autoFightText.bottom = self.__pyAutoFightBar.top - 2.0
		self.__riseAutoCBID = BigWorld.callback( 0.1, self.__riseAutoBar )

	def __cancelRiseAuto( self ):
		BigWorld.cancelCallback( self.__riseAutoCBID )
		self.__riseAutoCBID = 0
		self.__autoFader.value = 1.0
		self.__pyAutoBtn.visible = True
		self.__layoutAutoBar()

	def __setCustomSCTags( self ):
		for pyItem in self.__pyItems.values():
			scTag = pyItem.scTag
			scInfo = shortcutMgr.getShortcutInfo( scTag )
			scKeyStr = scInfo.shortcutString
			if KEYS_MAP.has_key( scKeyStr ):
				scKeyStr = KEYS_MAP[scKeyStr]
			pyItem.setScKeyStr( scKeyStr )

	def __updateServerTime( self ):
		serverTimes = Time.localtime()
		hour = serverTimes[3]
		minute = serverTimes[4]
		self.__pyStServerTime.text = "%d:%02d"%( hour, minute )
		disSec = 60.0 - serverTimes[5]
		self.__svrTimeCBID = BigWorld.callback( disSec, self.__updateServerTime )

	def __cancelUpdateTimer( self ):
		if self.__svrTimeCBID > 0:
			BigWorld.cancelCallback( self.__svrTimeCBID )
			self.__svrTimeCBID = 0

	def __getChMapSkill( self, itemId, skills ):
		"""
		���ݵ�ǰ��������ܲ��Ҹ�������,���滻
		"""
		skillType = itemId/1000
		skLvStr = str(itemId)[6:]
		player = BigWorld.player()
		mapSkills = self.__getMapSkills( skills )
		for key, value in challengeMapDatas.items(): #key Ϊ�������ܣ�valueΪ��ɫ���м���
			if value == skillType and key in mapSkills:
				mapStr = str( key ) + skLvStr
				mapSkId = int( mapStr )
				if not mapSkId in player.spaceSkillList:
					mapIndex = player.spaceSkillList.index( key )
					player.spaceSkillList[mapIndex] = mapSkId
				return mapSkId
		return 0
	
	def __getMapSkills( self, skills ):
		mapSkills = []
		for skill in skills:
			if len( str( skill ) ) >= 9:
				skill = skill/1000
			mapSkills.append( skill )
		return mapSkills
	
	def __isSubItemsMouseHit( self ):
		if self.__autoFightText.isMouseHit():
			return True
		if self.__pyAutoFightBar.isMouseHit() :
			return True
		if self.__pyPetBar.isMouseHit() :
			return True
		if self.__pyRaceBar.isMouseHit() :
			return True
		if self.__pySpaceSkillBar.isMouseHit() :
			return True
		if self.__pyExpBar.isMouseHit() :
			return True
		if self.__expBg.isMouseHit() :
			return True
		if self.__pyGuardsBar.isMouseHit() :
			return True
		if s_util.isMouseHit( self.gui.skillBar ) :
			return True
		if self.__pyAirIcon.isMouseHit() :
			return True
		if self.__pyPostureBar.isMouseHit():
			return True
		return False
	
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		RootGUI.onLMouseDown_( self, mods )
		return self.isMouseHit()

	def onMouseMove_( self, dx, dy ):
		RootGUI.onMouseMove_( self, dx, dy )

	def onLClick_( self,mods ):
		if not self.isMouseHit() : 
			return False
		RootGUI.onLClick_( self,mods )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def isMouseHit( self ) :
		return self.__rangePolygon.isPointIn( self.mousePos ) \
		or self.__isSubItemsMouseHit()

	def hightlightLack( self ) :
		if self.pyTopParent.isLocked():	#���������ѱ���ס�����ٸ�����ʾ
			return
		self.lackitems = [ pyItem for pyItem in self.__pyItems.values() if pyItem.itemInfo is None  ]
		for pyItem in self.lackitems:
			if pyItem.itemInfo is None :
				toolbox.itemCover.showItemCover( pyItem.skItem )

	def hidelightLack( self ) :
		for pyItem in self.lackitems:
			if pyItem.itemInfo is None :
				toolbox.itemCover.hideItemCover( pyItem.skItem )
				
	def isLocked( self ):
		return self.__isLocked

	def onLeaveWorld( self ) :
		"""
		��ɫ�뿪����ʱ������
		"""
		self.hide()
		for index, pyItem in self.__pyItems.iteritems() :
			pyItem.gbIndex = index
			pyItem.update( None )
			pyItem.stopFlash()
		self.__pyPetBar.onLeaveWorld()
		self.__pyAutoFightBar.onLeaveWorld()
		self.__pyRaceBar.onLeaveWorld()
		self.__pySpaceSkillBar.onLeaveWorld()
		self.__pyPostureBar.onLeaveWorld()
		self.__onHideSpellingCover()
		self.__autoFightText.stop()
		self.__pyAutoFightBar.visible = False
		BigWorld.cancelCallback( self.__riseAutoCBID )
		self.__riseAutoCBID = 0
		self.__cancelUpdateTimer()
		self.__pyStServerTime.text = ""
		self.__pyAirTrPanel.visible = False
		self.__initSkills = {}
		self.__flashcbids = {}
		self.__ignoreInits = set([])
		self.__pyRtGuards.visible = False
		self.__isLocked = False

	def onEnterWorld( self ) :
		"""
		��ɫ��������ʱ������
		"""
		player = BigWorld.player()
		isShowAutoBar = player.hasAutoFight
		self.autoBarShow = isShowAutoBar
		self.__pyAutoFightBar.visible = isShowAutoBar
		self.__pyAutoBtn.visible = isShowAutoBar
		self.__pyAutoFightBar.onEnterWorld()
		self.__pyPostureBar.onEnterWorld()
		self.__cancelUpdateTimer()
		if isShowAutoBar:
			self.__layoutAutoBar()
			self.__autoFader.value = 1.0
		else:
			self.__autoFader.value = 0.0
		self.__pyRaceBar.visible = player.state == csdefine.ENTITY_STATE_RACER
		self.__setCustomSCTags()
		self.__svrTimeCBID = BigWorld.callback( 0.0, self.__updateServerTime )
		self.show()
		section= Language.openConfigSection( "config/client/InitialQBSkills.xml" )
		if section is None:return
		pclass = player.getClass()
		for node in section.values():
			rclass = node.readInt( "class" )
			if rclass != pclass:continue
			skillID = node.readInt64( "skillID" )
			isPosture = bool( node.readInt( "isPosture" ) )
			qbIndex = node.readInt( "qbIndex" ) - 1
			posture = node.readInt( "posture" )
			self.__initSkills[skillID] = InitQBSkill( skillID, isPosture, qbIndex, posture )
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__cfgPath = "account/%s/%s/ignoreinits.xml"%( accountName, roleName )
		self.__cfgSect = ResMgr.openSection( self.__cfgPath )
		if self.__cfgSect is None:
			self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )
			self.__cfgSect.save()
		else:
			for node in self.__cfgSect.values():
				skillID = node.readInt64( "skillID" )
				gbIndex = node.readInt( "gbIndex" )
				self.__ignoreInits.add((skillID,gbIndex))
		ResMgr.purge( self.__cfgPath )
		self.__setPageIndex( 0 )

# --------------------------------------------------------------------
# system bar
# --------------------------------------------------------------------
from guis.OpIndicatorObj import OpIndicatorObj

class SystemBar( RootGUI, OpIndicatorObj ) :
	def __init__( self ) :
		bar = GUI.load( "guis/general/quickbar/rightbar/sysbar.gui" )
		uiFixer.firstLoadFix( bar )
		RootGUI.__init__( self, bar )
		OpIndicatorObj.__init__( self )
		self.focus = False
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "BOTTOM"
		self.movable_ = False
		self.escHide_ = False
		self.activable_ = False
		self.visible = True
		self.__sysFader = bar.sysBar.fader
		self.__sysFader.speed = 0.5
		self.__sysFader.value = 1.0
		self.__fadeCBID = 0
		self.__handlers = []
		self.pyBox = None
		# ��Ӧ������е�ÿ����ť��˳���ܵ���
		self.__handlers.append( ( "UI_TOGGLE_EQUIPWINDOW", self.__toggleEquipWnd ) )			# װ��
		self.__handlers.append( ( "UI_TOGGLE_KITBAG", self.__toggleKitbag ) )					# ����
		self.__handlers.append( ( "UI_TOGGLE_SKILLWINDOW", self.__toggleSkillWindow ) )			# ����
		self.__handlers.append( ( "UI_TOGGLE_PET_PROPERTY", self.__togglePetWindow ) )			# ����
		self.__handlers.append( ( "UI_TOGGLE_QUESTWINDOW", self.__toggleQuestWindow ) )			# ����
		self.__handlers.append( ( "UI_TOGGLE_FRIENDWINDOW", self.__toggleFriendWindow ) )		# ����
		self.__handlers.append( ( "UI_TOGGLE_TONGWINDOW", self.__toggleToneWindow ) )			# ���
		self.__handlers.append( ( "FIXED_TOGGLE_SYSTEMWINDOW", self.__toggleSystemWindow ) )	# ϵͳ
		self.__handlers.append( ( "UI_TOGGLE_TEAMCOPY_WNDS", self.__toggleTeamCopyWnds ) )		# ������ӽ���
		self.__handlers.append( ( "UI_TOGGLE_SERMONWINDOW", self.__toggleSermonWnd) )		# ֤������

		# ����������ʾ/���ؿ�ݼ�
		self.__handlers.append( ( "UI_TOGGLE_FPS_VIEW", self.__toggleFPS ) )					# ֡������
		self.__handlers.append( ( "UI_TOGGLE_BIGMAP", self.__toggleBigMap ) )					# ���ͼ
		self.__handlers.append( ( "UI_TOGGLE_MINIMAP", self.__toggleMiniMap ) )					# С��ͼ
		self.__handlers.append( ( "UI_TOGGLE_SUBKITBAGS", self.__toggleSubKitbags ) )			# ����С����
		self.__handlers.append( ( "UI_TOGGLE_STALLAGE", self.__toggleStallageWindiw ) )			# ��̯
		self.__handlers.append( ( "UI_TOGGLE_PET_SKILL", self.__togglePetSkill ) )				# ���＼��
		self.__handlers.append( ( "UI_TOGGLE_VEHICLEWINDOW", self.__toggleVechicleWindow ) )	# ���
		self.__handlers.append( ( "UI_TOGGLE_CREDITWINDOW", self.__toggleCreditWindow ) )		# ����
		self.__handlers.append( ( "UI_TOGGLE_TEAMMATEWINDOW", self.__toggleTeammateWindow ) )	# �������
		self.__handlers.append( ( "UI_TOGGLE_GEMWINDOW", self.__toggleGemWindow ) )				# ��ʯ
		self.__handlers.append( ( "UI_TOGGLE_HELPWINDOW", self.__toggleHelpWindow ) )			# ����
		self.__handlers.append( ( "UI_TOGGLE_LEVELWINDOW", self.__toggleLevelWindow ) )			# �ȼ�
		self.__handlers.append( ( "UI_TOGGLE_AUTOFIGHTBAR", self.__toggleAutoFightWindow ) )	# �Զ�ս��
#		self.__handlers.append( ( "UI_TOGGLE_TALISMANWINDOW", self.__toggleTalismanWindow ) )	# ��������
		self.__handlers.append( ( "UI_TOGGLE_TEAMINFO_WINDOW", self.__toggleTeamInfoWindow ) )	# ��ӽ���
		self.__handlers.append( ( "UI_TOGGLE_FENGQI_REPORT", self.__toggleFengQiReport ) )	# ҹս����ͳ��

		for handler in self.__handlers :														# ע���ݼ�
			shortcutMgr.setHandler( handler[0], handler[1] )

		self.__initialize( bar )

		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUEST_LOG_ADD"]			= self.__onAddQuestLog		# �������
		self.__triggers["EVT_ON_PLAYER_ADD_VEHICLE"]	= self.__onAddVehicle		# ������
		self.__triggers["EVT_ON_PCG_ADD_PET"]		 	= self.__onAddPet			# ��ó���
		self.__triggers["EVT_ON_KITBAG_ADD_ITEM"] 		= self.__onAddItem			# �����Ʒ
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"]	= self.__onRoleLevelChanged
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __initialize( self, bar ) :
		self.__pyBtnDown = Button( bar.btnDown )
		self.__pyBtnDown.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnDown.onLClick.bind( self.__hideSysBar )

		self.__pyBtnUp = Button( bar.btnUp)
		self.__pyBtnUp.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnUp.onLClick.bind( self.__showSysBar )

		self.__pySysBar = PyGUI( bar.sysBar )
		self.__initButtons( bar.sysBar )

	def __initButtons( self, sysBar ):
		self.__pyBtns = []
		for name, btn in sysBar.children :
			if "btn_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyBtn = Button( btn )
			pyBtn.setStatesMapping( UIState.MODE_R1C3 )
			pyBtn.index = index
			self.__pyBtns.append( pyBtn )
			pyBtn.onLClick.bind( self.__onButtonClick )
			pyBtn.onLMouseDown.bind( self.__onButtonLMouseDown )
			pyBtn.onMouseEnter.bind( self.__onButtonMouseEnter )
			pyBtn.onMouseLeave.bind( self.__onButtonMouseLeave )

			scTag, handler = self.__handlers[index]
			pyBtn.handler = handler
			scInfo = shortcutMgr.getShortcutInfo( scTag )
			pyBtn.description = scInfo.comment
			pyBtn.scTag = scTag

	# -------------------------------------------------
	def __hideSysBar( self ):
		BigWorld.cancelCallback( self.__fadeCBID )
		self.__sysFader.value = 0.0
		self.__pyBtnUp.visible = True
		self.__pyBtnDown.visible = False
		self.__fadeCBID = BigWorld.callback( self.__sysFader.speed, self.hideSysBar )

	def __showSysBar( self ):
		BigWorld.cancelCallback( self.__fadeCBID )
		self.__sysFader.value = 1.0
		self.__pyBtnUp.visible = False
		self.__pyBtnDown.visible = True
		self.__fadeCBID = BigWorld.callback( self.__sysFader.speed, self.showSysBar )

	def hideSysBar( self ):
		self.__pySysBar.visible = False

	def showSysBar( self ):
		self.__pySysBar.visible = True

	def __onButtonClick( self, pyBtn ) :
		pyBtn.handler()

	def __onButtonLMouseDown( self, pyBtn ) :
		toolbox.infoTip.hide()

	def __onButtonMouseEnter( self, pyBtn ) :
		dsp = pyBtn.description
		if hasattr( pyBtn, "scTag" ) :
			strKey = shortcutMgr.getShortcutInfo( pyBtn.scTag ).shortcutString
			#strKey = strKey == "ESCAPE" and "ESC" or strKey				# ��ݼ��ַ�����ESCAPE����Ϊ��ESC����ת�����ƶ����ײ���У�
			if strKey != "" :
				dsp = dsp + PL_NewLine.getSource() + \
				labelGather.getText( "quickbar:SysBar", "tipsKeyClew" ) % strKey
		toolbox.infoTip.showToolTips( self, dsp )

	def __onButtonMouseLeave( self, pyBtn ) :
		toolbox.infoTip.hide()
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self ):
		self.visible = True
		player = BigWorld.player()
		if self.__pySysBar.visible:
			self.__pyBtnUp.visible = False
			self.__pyBtnDown.visible = True
		else:
			self.__pyBtnUp.visible = True
			self.__pyBtnDown.visible = False
		for pyBtn in self.__pyBtns:
			if pyBtn.index == 8:
				pyBtn.enable = player.level >= 30
		SystemWindow.instance().onEnterWorld()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","systemBar" ) )

	def onLeaveWorld( self ):
		self.visible = False
		self.__fadeCBID = 0
		SystemWindow.instance().onLeaveWorld()

	# ----------------------------------------------------------------
	# operate indication methods
	# ----------------------------------------------------------------
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		trigger = ( "gui_visible","systemBar" )
		condition1 = ( "quest_uncompleted", )
		condition2 = ( "quest_uncompleted", "checkNotHasVehicle" )
		condition3 = ( "quest_uncompleted", "checkHasVehicle" )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition1, trigger )
		idtIds += rds.opIndicator.idtIdsOfCmd( condition2, trigger )
		idtIds += rds.opIndicator.idtIdsOfCmd( condition3, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showIndicationBindToButton
		
	def __showIndicationBindToButton( self, idtId, label ) :
		"""
		"""
		labelMap = {
			"btn_sysSetting" : 0,
			"btn_tong" : 1,
			"btn_relation" : 2,
			"btn_quest" : 3,
			"btn_pet" : 4,
			"btn_skill" : 5,
			"btn_kitbag" : 6,
			"btn_equip" : 7,
		}
		if label in labelMap:
			pyBtn = self.__pyBtns[labelMap[label]]
			toolbox.infoTip.showHelpTips( idtId, pyBtn )
			self.addVisibleOpIdt( idtId )
				

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def __onAddQuestLog( self, questID ) :
		"""
		�������
		"""
		pass

	def __onAddVehicle( self, petDBID ) :
		"""
		������
		"""
#		toolbox.infoTip.showOperationTips( 0x0040, self.__pyBtns[4] )

	def __onAddPet( self, petEpitome ):
		"""
		��ó���
		"""
		toolbox.infoTip.showOperationTips( 0x004a, self.__pyBtns[4] )

	def __onAddItem( self, itemInfo ):
		if itemInfo is None:return
#		if itemInfo.itemType == ItemTypeEnum.ITEM_SYSTEM_VEHICLE:
#			toolbox.infoTip.showOperationTips( 0x0043, self.__pyBtns[6] )
		baseItem = itemInfo.baseItem
		if not rds.statusMgr.isInWorld():return
#		if baseItem.isEquip():
#			if baseItem.canWield( BigWorld.player() ):
#				toolbox.infoTip.showOperationTips( 0x0062, self, Rect( (2, 2), (102, 50) ) )
	
	def __onRoleLevelChanged( self, oldLevel, newLevel ):
		"""
		��ɫ�ȼ��ı�
		"""
		for pyBtn in self.__pyBtns:
			if pyBtn.index in [8, 9]:
				pyBtn.enable = newLevel >= 30
				

	# ----------------------------------------------------------------
	# shortcut triggers
	# ----------------------------------------------------------------
	def __toggleEquipWnd( self ):
		"""
		��ʾ/����װ������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_EQUIP_WINDOW" )
		toolbox.infoTip.hideOperationTips( 0x0062 )
		return True

	def __toggleKitbag( self ) :
		"""
		��ʾ/���ر���
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_KITBAG" )
#		toolbox.infoTip.hideOperationTips( 0x0043 )
#		toolbox.infoTip.hideOperationTips( 0x0062 )
		trigger = ( "gui_visible","systemBar" )
		idtIds = rds.opIndicator.getRegIdtsOfTrigger(trigger,"systemBar","btn_kitbag")
		for idtId in idtIds:
			self.clearIndicationsById( idtId )
		return True

	def __toggleSkillWindow( self ) :
		"""
		��ʾ/���ؼ��ܴ���
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_SKILL_WINDOW" )
		return True

	def __togglePetWindow( self ) :
		"""
		��ʾ/���س������Դ���
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_PET_WINDOW" )
#		toolbox.infoTip.hideOperationTips( 0x0040 )
#		toolbox.infoTip.hideOperationTips( 0x004a )
		toolbox.infoTip.hideHelpTips( 47 )
		toolbox.infoTip.hideHelpTips( 141 )
		trigger = ( "gui_visible","systemBar" )
		idtIds = rds.opIndicator.getRegIdtsOfTrigger(trigger,"systemBar","btn_pet")
		for idtId in idtIds:
			self.clearIndicationsById( idtId )
		return True

	def __toggleQuestWindow( self ) :
		"""
		��ʾ/�������񴰿�
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_QUEST_WINDOW" )
#		toolbox.infoTip.showOperationTips( 0x0030, self.__pyBtns[5] )
		return True

	def __toggleFriendWindow( self ) :
		"""
		��ʾ/���غ��Ѵ���
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_SOCIALITY_WINDOW" )
		return True

	def __toggleToneWindow( self ) :
		"""
		��ʾ/���ذ�ᴰ��
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_WINDOW" )
		return True

	def __toggleSystemWindow( self ) :
		"""
		��ʾ/����ϵͳ����
		"""
		SystemWindow.instance().toggleWindow()
		return True

	# -------------------------------------------------
	def __toggleFPS( self ) :
		"""
		��ʾ/����֡����ʾ����
		"""
		#ECenter.fireEvent( "" )
		return True

	def __toggleBigMap( self ) :
		"""
		��ʾ/���ش��ͼ
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_BIGMAP" )
		return True

	def __toggleMiniMap( self ) :
		"""
		��ʾ/����С��ͼ
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_MINMAP" )
		return True

	def __toggleSubKitbags( self ) :
		"""
		��ʾ/��������С����
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_SUBKITBAGS" )
		return True

	def __toggleStallageWindiw( self ) :
		"""
		��ʾ/���ذ�̯����
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_VENDWINDOW" )
		return True

	def __togglePetSkill( self ) :
		"""
		��ʾ/���س��＼�ܴ���
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_PETSKILL_WINDOW" )
		return True

	def __toggleVechicleWindow( self ) :
		"""
		��ʾ/������贰��
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_VEHICLE_WINDOW" )
		return True

	def __toggleCreditWindow( self ) :
		"""
		��ʾ/������������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_CREDIT_WINDOW" )
		return True

	def __toggleTalismanWindow( self ) :
		"""
		��ʾ/���ط�������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TALISMAN_WINDOW" )
		return True

	def __toggleTeammateWindow( self ):
		"""
		��ʾ/���ض������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TEAMMATESWINDOW" )
		return True

	def __toggleTeamInfoWindow( self ) :
		"""
		��ʾ/������Ӵ���
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TEAM_INFO_WND" )
		return True
	
	def __toggleFengQiReport( self ):
		"""
		��ʾ/����ҹս����ͳ�ƴ���
		"""
		if not BigWorld.player().onFengQi:return
		ECenter.fireEvent( "EVT_ON_SHOW_FENGQI_RANK_WINDOW" )
		return True
	
	def __toggleTeamCopyWnds( self ):
		"""
		��ʾ/���ظ�����ӽ���
		"""
		status_map = { csdefine.MATCH_STATUS_PERSONAL_NORMAL: "EVT_ON_TOGGLE_TEAMCOPY_SYSTEM_WND",
						csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY: "EVT_ON_TOGGLE_TEAMCOPY_SYSTEM_WND",
						csdefine.MATCH_STATUS_PERSONAL_MATCHING: "EVT_ON_TOGGLE_TEAMCOPY_MATCHING_WND",
						csdefine.MATCH_STATUS_PERSONAL_CONFIRMING: "EVT_ON_TOGGLE_TEAMCOPY_CONFIRMING_WND",
					}
		player = BigWorld.player()
		matchStatus = player.matchStatus	#��ǰ״̬
		matchedCopy = player.labelOfMatchedCopy
		if matchedCopy:							#�Ѿ���ƥ��ĸ��������У������˵�
			CopyTeamMenu.instance().show()
		else:
			toggleTag = status_map.get( matchStatus )
			if toggleTag is None:return
			ECenter.fireEvent( toggleTag )
		return True
	
	def __toggleSermonWnd( self ):
		"""
		��ʾ/����֤������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SERMON_WND" )
		return True

	def __toggleGemWindow( self ) :
		"""
		��ʾ/���ر�ʯ����
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_GEM_WINDOW" )
		return True

	def __toggleHelpWindow( self ) :
		"""
		��ʾ/���ذ�������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_HELP_WINDOW" )
		return True

	def __toggleLevelWindow( self ) :
		"""
		��ʾ/���صȼ�����
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_UPGRADE_HELPER" )
		return True

	def __toggleAutoFightWindow( self ) :
		"""
		��ʾ/�����Զ�ս�����ƴ���
		"""
		if not BigWorld.player().hasAutoFight:
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			self.pyBox = showMessage( mbmsgs[0x0ec6], "", MB_OK )
			return False
		AutoFightWindow.instance().toggleAuotFightWindow()
		return True

from Time import Time
class AutoFightTimer( PyGUI ):
	"""
	"""
	def __init__( self, wnd ):
		"""
		"""
		PyGUI.__init__( self, wnd )
		self.visible = False
		self.timerID = 0
		self.endTime = 0
		self.timerText = StaticText( wnd.leaveTime )
		self.timerText.h_anchor = "CENTER"

	@languageDepart
	def start( self ):
		"""
		��ʼ
		"""
		pass

	def stop( self ):
		"""
		ֹͣ
		"""
		self.visible = False
		self.timerText.text = ""
		BigWorld.cancelCallback( self.timerID )
		ECenter.fireEvent( "EVT_ON_LOCATED_NOTIFIER_POSITION", self.bottomToScreen - 2 )

	def startTimeOnly( self, times ):
		"""
		ֻ��ʾ��ʱ by ����
		"""
		self.endTime = Time.time() + times
		self.__detect()
		self.visible = True

	def __detect( self ):
		"""
		"""
		showTime = int( self.endTime - Time.time() )
		if showTime < 0:
			self.stop()
		hour = showTime / 3600
		min = ( showTime - int(hour)*3600 ) / 60
		sec = showTime % 60
		hourStr = "leaveTimeHour"
		secStr = "leaveTime"
		player = BigWorld.player()
		if player is not None and player.isPlayer() and player.af_time_extra > 0:
			hourStr = "leaveTimeHourExtra"
			secStr = "leaveTimeExtra"
		if hour > 0:
			self.timerText.text = labelGather.getText( "quickbar:afTimer", hourStr ) % ( hour, min, sec )
			self.width = self.timerText.width * 2
		else:
			self.timerText.text = labelGather.getText( "quickbar:afTimer", secStr ) % ( min, sec )
			self.width = self.timerText.width * 1.5
		if showTime < 60:
			self.timerText.color = defParser.tranColor( "c3" ) 	# ��ɫ
		else:
			self.timerText.color = defParser.tranColor( "c6" ) 	# ��ɫ

		self.timerID=BigWorld.callback( 1, self.__detect )

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setBottom( self, bottom ) :
		PyGUI._setBottom( self, bottom )
		if self.visible :
			ECenter.fireEvent( "EVT_ON_LOCATED_NOTIFIER_POSITION", self.topToScreen - 2 )
		else :
			ECenter.fireEvent( "EVT_ON_LOCATED_NOTIFIER_POSITION", self.bottomToScreen - 2 )

	# -------------------------------------------------
	bottom = property( PyGUI._getBottom, _setBottom )

# -----------------------------------------------------------------
# QBSkItem
# -----------------------------------------------------------------

class QBSkItem( PyGUI ):
	"""
	 ���ܸ�
	"""
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pySKItem = QBItem( item.icon, self )
		self.__pyStIndex = StaticText( item.stLabel )
		self.__pyStIndex.h_anchor = "CENTER"
		self.__pyStIndex.fontSize = 11
		
		self.__pySkCover = PyGUI( item.skCover )
		self.__ptSkID = 0
		self.__pyEffect = None

	def update( self, itemInfo, isNotInit = True ):
		if isNotInit:
			self.removeEffect()
		self.__pySKItem.update( itemInfo, isNotInit )

	def updateIconState( self ):
		self.__pySKItem.updateIconState()

	def bindShortcut( self, scTag ):

		self.__pySKItem.bindShortcut( scTag )

	def setScKeyStr( self, scTag ):

		self.__pyStIndex.text = labelGather.getText( "quickbar:skillBar", "skIndex" )%scTag
	
	def startFlash( self ):
		
		self.__pySKItem.startFlash()
	
	def stopFlash( self ):
		self.__pySKItem.stopFlash()
	
	def addEffect( self ):
		if self.__pyEffect is not None:
			self.__pyEffect.visible = True
			return
		effect = GUI.load( "guis/general/quickbar/effect.gui" )
		uiFixer.firstLoadFix( effect )
		self.__pyEffect = PyGUI( effect )
		self.addPyChild( self.__pyEffect )
		self.__pyEffect.center = self.__pySkCover.center
		self.__pyEffect.posZ = 0.5
		self.getGui().reSort()
	
	def isLearnable( self, pLevel ):
		
		return self.__pySKItem.isLearnable( pLevel )
	
	def removeEffect( self ):
		if self.__pyEffect:
			self.delPyChild( self.__pyEffect )
			self.__pyEffect = None
	
	def isShowEffect( self, isShow ):
		if self.__pyEffect:
			self.__pyEffect.visible = isShow
			
	def updateIndexColor( self, color ):
		self.__pyStIndex.color = color

	def _getGBIndex( self ) :
		return self.__pySKItem.gbIndex

	def _setGBIndex( self, index ) :

		self.__pySKItem.gbIndex = index

	def _getSKItem( self ):
		return self.__pySKItem

	def _getItemInfo( self ):
		return self.__pySKItem.itemInfo

	def _getPtSkID( self ):
		return self.__ptSkID

	def _setPtSkID( self, ptSkID ):
		self.__ptSkID = ptSkID
		
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	gbIndex = property( _getGBIndex, _setGBIndex )
	skItem = property( _getSKItem )
	itemInfo = property( _getItemInfo )
	ptSkID = property( _getPtSkID, _setPtSkID )

class InitQBSkill:
	def __init__( self, skillID, isPosture, qbIndex, posture ):
		self.skillID = skillID
		self.isPosture = isPosture
		self.qbIndex = qbIndex
		self.posture = posture
	
	def updateSkillID( self, skillID ):
		self.skillID = skillID