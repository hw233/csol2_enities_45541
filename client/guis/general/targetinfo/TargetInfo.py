# -*- coding: gb18030 -*-
#
# $Id: TargetInfo.py,v 1.44 2008-09-05 09:27:18 yangkai Exp $

"""
implement target info window
"""

import csdefine
import csconst
import GUIFacade
import BigWorld
import csstatus
import Const
from guis import *
from AbstractTemplates import Singleton
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
from guis.controls.Icon import Icon
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from guis.general.chatwindow.playmatechat.PLMChatMgr import plmChatMgr
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from config.client.msgboxtexts import Datas as mbmsgs
from EspialTarget import espial
from BuffItem import BuffItem
from cscustom import Polygon
from ItemsFactory import BuffItem as BuffInfo
from ChatFacade import chatFacade
from LabelGather import labelGather
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()
from PetFormulas import formulas
from Function import Functor
import Math
from HPSectsConfigLoader import hpSectsLoader
import Timer

TRADE_SWAP_ITEM = 1		# ��Ʒ����
TRADE_SWAP_PET = 0		# ���ｻ��
NAME_LIMIT_SHOW_LEN = 16 # NPC������ʾ��������

PK_STATE_COLOR_MAP = {
	csdefine.PK_STATE_PROTECT			: ( 0, 255, 0, 255 ),
	csdefine.PK_STATE_ATTACK			: ( 153, 51, 0, 255 ),
	csdefine.PK_STATE_PEACE				: ( 255, 255, 255, 255 ),
	csdefine.PK_STATE_BLUENAME			: ( 0, 255, 255, 255 ),
	csdefine.PK_STATE_REDNAME			: ( 255, 0, 0, 255 ),
	csdefine.PK_STATE_ORANGENAME		: ( 255, 255, 0, 255 ),	# ԭ��������˵�е�С����������Ϊ����
	}

ROLE_RELATION_COLOR_MAP = {
	csdefine.RELATION_NONE			: ( 255, 255, 255, 255 ),	# ���κι�ϵ��һ������Ĭ��ֵ
	csdefine.RELATION_FRIEND		: ( 0, 255, 0, 255 ),		# ���ѹ�ϵ( ԭ����C_RELATION_FRIEND )
	csdefine.RELATION_NEUTRALLY		: ( 255, 255, 255, 255 ),	# ������ϵ( ԭ����C_RELATION_NEUTRALLY )
	csdefine.RELATION_ANTAGONIZE	: ( 255, 0, 255, 255 ),		# �жԹ�ϵ( ԭ����C_RELATION_ANTAGONIZE )
	csdefine.RELATION_NOFIGHT		: ( 0, 255, 0, 255 ),		# ��ս��ϵ
	}

HP_SECTION_COLOR_MAP = { 1: (255, 0, 0), 2: (255, 128, 0) , 3: (255, 255, 0) , 4: (128,255,128) , 5:(0, 255, 255) , 6: (0, 128, 255), 7: (128, 0, 255) }

uis_positions = {"bg":{0:(8.0,10.0),1:(24.0,30.0)},
				"border":{0:(4.0,5.0),1:(0.0,0.0)},
				"head":{0:(8.0,9.0),1:(24.0,32.0)},
				"pkModeBtn":{0:(62.0,55.0),1:(72.0,75.0)},
				"mpBar":{0:(79.0,55.0),1:(96.0,67.0)},
				"lbName":{0:(107.0,18.0),1:(146.0,43.0)},
				"lbLevel":{0:(3.5,0.0),1:(3.5,28.0)},
				"captain":{0:(-3.0,19.0),1:(-3.0,19.0)},
				"profession":{0:(82.0,16.0),1:(107.0,40.0)},
				"lbHP":{0:(117.5,37.0),1:(131.0,63.0)},
				"lbMP":{0:(117.5,52.0),1:(0.0,29.0)},
				"levelBg":{0:(1.0,1.0),1:(0.0,29.0)},
				"camp":{0:(6.0,54.0),1:(1.0,54.0)},
				"hpBar_0":{0:(79.0,37.0),1:(95.0,64.0)},
				"hpBar_1":{0:(79.0,37.0),1:(95.0,64.0)},
				"stIndex":{0:(213.0,43.0),1:(231.0,63.0)},
				}


# ----------------------------------------------------------------
# ������������ߴ�������
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_TargetResetPyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		����������µ���������������ĳߴ�
		"""
		SELF._TargetInfo__pyLbHP.fontSize = 11
		SELF._TargetInfo__pyLbHP.charSpace = -1

		SELF._TargetInfo__pyLbMP.fontSize = 11
		SELF._TargetInfo__pyLbMP.charSpace = -1

		SELF._TargetInfo__pyLbLevel.fontSize = 11
		SELF._TargetInfo__pyLbLevel.charSpace = -1


class TargetInfo( Singleton, RootGUI ) :
	__cc_pro_states = {}									# ��ְͬҵ��״̬��� mapping λ
	__cc_pro_states[csdefine.CLASS_FIGHTER]	 = ( 1, 1 )		# սʿ
	__cc_pro_states[csdefine.CLASS_SWORDMAN] = ( 1, 2 )		# ����
	__cc_pro_states[csdefine.CLASS_ARCHER]	 = ( 2, 1 )		# ����
	__cc_pro_states[csdefine.CLASS_MAGE]	 = ( 2, 2 )		# ��ʦ

	_pk_modes = { 
			csdefine.PK_CONTROL_PROTECT_PEACE:( labelGather.getText( "PlayerInfo:main", "protect_peace"), ( 0, 254, 102, 255 ) ),
			csdefine.PK_CONTROL_PROTECT_TONG: ( labelGather.getText( "PlayerInfo:main", "protect_tong"), ( 250, 0, 250, 255 ) ),
			csdefine.PK_CONTROL_PROTECT_RIGHTFUL: ( labelGather.getText( "PlayerInfo:main", "protect_rightful"), ( 0, 254, 102, 255 ) ),
			csdefine.PK_CONTROL_PROTECT_JUSTICE: ( labelGather.getText( "PlayerInfo:main", "protect_justiceful"), ( 180, 255, 0, 255 ) ),
			csdefine.PK_CONTROL_PROTECT_NONE: ( labelGather.getText( "PlayerInfo:main", "protect_none"), ( 254, 1, 0, 255 ) ),
			}
			
	_colors_map = { csdefine.RELATION_FRIEND: ( 0, 255, 0, 255 ),
					csdefine.RELATION_NEUTRALLY: ( 255, 255, 0, 255 ),
					csdefine.RELATION_ANTAGONIZE: ( 255, 0, 0, 255 ),
				}
				
	def __init__( self ) :
		Singleton.__init__( self )
		wnd = GUI.load( "guis/general/targetinfo/common/bg.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.escHide_			= False				# �� esc ����������
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.__initialize( wnd )
		self.addToMgr( "targetInfo")

		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.moveFocus		 = False

		self.__target = None
		self.__triggers = {}
		self.__registerTriggers()

		self.__pyBuffItems = []						# �������� buff ����
		self.__pyDuffItems = []						# �������� debuff ����
		self.__menuItems = {}						# ���������еĲ˵������ÿ����ʾʱ�����´���
		self.__reBuffsCBID = 0						# Buff��ʱˢ��Callback
		self.__createMenuItems()
		self.__currentInviteDanceMessageBox = None  # ��Ŵ򿪵����봰��

		self.__resetPyItems()

	def __initialize( self, wnd ) :
		self.__pyHead = PyGUI( wnd.head )
		self.__pyBorder = PyGUI( wnd.border )
		self.__pyBg = PyGUI( wnd.bg )
		self.__pyCaptain = PyGUI( wnd.captain )
		self.__pyCaptain.visible = False

		self.__pyLevelBg = PyGUI( wnd.levelBg)
		self.__pyLevelBg.visible = True

		self.__pyLbName = StaticText( wnd.lbName )
		self.__pyLbLevel = StaticText( wnd.lbLevel )
		self.__pyLbLevel.fontSize = 12
		self.__pyLbLevel.h_anchor = 'CENTER'

		self.__pyHPBars = {}
		for name, item in wnd.children:
			if not name.startswith( "hpBar_" ): continue
			index = int( name.split("_")[-1] )
			pyHpBar = ProgressBar( item )
			pyHpBar.clipMode = "RIGHT"
			self.__pyHPBars[index] = pyHpBar
		self.__pyMPBar = ProgressBar( wnd.mpBar )
		self.__pyMPBar.clipMode = "RIGHT"

		self.__pyLbHP = StaticText( wnd.lbHP )
		self.__pyLbHP.fontSize = 12
		self.__pyLbHP.text = ""
		self.__pyLbHP.h_anchor = 'CENTER'
		self.__pyLbMP = StaticText( wnd.lbMP )
		self.__pyLbMP.fontSize = 12
		self.__pyLbMP.text = ""
		self.__pyLbMP.h_anchor = 'CENTER'
		
		self.__pyStIndex = StaticText( wnd.stIndex )
		self.__pyStIndex.color = cscolors["c3"]
		self.__pyStIndex.text = ""
		self.__priFontSize = self.__pyStIndex.fontSize

		self.__pyClassMark = Icon( wnd.profession )
		self.__pyClassMark.crossFocus = True
		self.__pyClassMark.onMouseEnter.bind( self.__onProMouseEnter )
		self.__pyClassMark.onMouseLeave.bind( self.__onProMouseLeave )
		self.__pyClassMark.visible = False

		self.__pyCMenu = ContextMenu()
		self.__pyCMenu.addBinder( self )
		self.__pyCMenu.onBeforePopup.bind( self.__onMenuPopUp )
		self.__pyCMenu.onAfterPopUp.bind( self.__onAfterMenuPopUp )
		self.__pyCMenu.onItemClick.bind( self.__onMenuItemClick )
		
		self.__pyCamp = PyGUI( wnd.camp )
		self.__pyCamp.visible = False
		
		self.__pyBtnPkMode = Button( wnd.pkModeBtn )
		self.__pyBtnPkMode.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnPkMode.focus = False
		self.__pyBtnPkMode.crossFocus = False

		self.__rangePolygon = Polygon([])											# ������������
		self.__rangeNPC = [	( 0, 38 ), ( 4, 20 ), ( 22, 4 ), ( 62, 5 ),
							( 77, 15 ), ( 216, 15 ), ( 226, 23 ), ( 231, 53 ),
							( 92, 53 ), ( 59, 81 ), ( 19, 77 ), ( 0, 60 ),
						  ]
		self.__rangeNormal = [	( 0, 38 ), ( 4, 20 ), ( 22, 4 ), ( 62, 5 ),
								( 77, 15 ), ( 216, 15 ), ( 226, 23 ), ( 231, 53 ),
								( 217, 69 ),( 79, 69 ), ( 59, 81 ), ( 19, 77 ),
								( 0, 60 ),
							 ]
		self.__curIndex = 0
		self.__zoomTimerID = 0
		self.__topOffset = 80.0
		self.__minHeight = self.height

	@deco_TargetResetPyItems
	def __resetPyItems( self ) :
		"""
		���貿��UIԪ�ص�λ�á���С�����������
		"""
		pass											# ����汾�����޸�

	def dispose( self ) :
		self.__deregisterTriggers()
		RootGUI.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
#		self.__triggers["EVT_ON_TARGET_BINDED"]			= self.__onShowTargetInfo
#		self.__triggers["EVT_ON_TARGET_UNBINDED"]		= self.__onHideTrargetInfo
		self.__triggers["EVT_ON_ENTITY_HP_CHANGED"]		= self.__onHPChanged
		self.__triggers["EVT_ON_ENTITY_HP_MAX_CHANGED"]	= self.__onHPChanged
		self.__triggers["EVT_ON_ENTITY_MP_CHANGED"]		= self.__onMPChanged
		self.__triggers["EVT_ON_ENTITY_MP_MAX_CHANGED"]	= self.__onMPChanged
		self.__triggers["EVT_ON_ENTITY_LEVEL_CHANGED"]	= self.__onLevelChanged
		self.__triggers["EVT_ON_TEAM_DISBANDED"]		= self.__onTeamDisbanded
		self.__triggers["EVT_ON_TEAM_CAPTAIN_CHANGED"]	= self.__onCaptainChanged
		self.__triggers["EVT_ON_TEAM_MEMBER_ADDED"]		= self.__onTeamMemberAdded
		self.__triggers["EVT_ON_TEAM_MEMBER_LEFT"]		= self.__onTeamMemberLeft
		self.__triggers["EVT_ON_TARGET_UNBINDED"]		= self.__onUnbindTarget
		self.__triggers["EVT_ON_TARGET_BUFFS_CHANGED"]	= self.__setBuffItems
		self.__triggers["EVT_ON_INVITE_JOIN_DANCE"]		= self.__onInviteJoinDance
		self.__triggers["EVT_ON_STOP_REQUEST_DANCE"]	= self.__onStopRequestDance
		self.__triggers["EVT_ON_RECEIVE_MESSAGE_SUANGUAZHANBU"]	= self.__onReceiveMessageSuanGuaZhanBu
		self.__triggers["EVT_ON_SET_TARGET_BOOTY_OWNER"]	= self.__onSetHoldFlag
		self.__triggers["EVT_ON_TARGET_MODEL_CHANGED"] = self.__onTargetModelChange
		self.__triggers["EVT_ON_ENTITY_NAME_CHANGED"] = self.__onNameChanged
		self.__triggers["EVT_ON_NPC_NAMECOLOR_CHANGED"] = self.__onNameColorChanged
		self.__triggers["EVT_ON_ROLE_PKMODE_CHANGED"] = self.__onPKModeChanged
		self.__triggers["EVT_ON_ROLE_SYSPKMODE_CHANGED"] = self.__onSysModeChange	# ϵͳPK�ı�
		for eventMacro in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		for eventMacro in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( eventMacro, self )

	# -------------------------------------------------
	def __createMenuItems( self ) :
		"""
		�������п����õ��Ĳ˵���
		"""
		menuList = []
		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miWhisper" ) )
		pyItem0.handler = self.__whisper
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miEspial" ) )
		pyItem0.handler = self.__espialTarget
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miFollow" ) )
		pyItem0.handler = self.__followTarget
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miTradeItem" ) )
		pyItem0.handler = self.__inviteTradeItem
		pyItem1 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miTradePet" ) )
		pyItem1.handler = self.__inviteTradePet
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pyItem1, pySplitter] )

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miQieCuo" ) )
		pyItem0.handler = self.__requestQieCuo
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )
		self.__menuItems["persistence"] = menuList						# ������һ�飬����˵�ÿ�ε���������ʾ

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miAddToBuddy" ) )	# ��Ӻ���
		pyItem0.handler = self.__addToBuddy
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["addToBuddy"] = [pySplitter, pyItem0]
		
		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miFriendChat" ) )   # ��������
		pyItem0.handler = self.__friendChat
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["friendChat"] = [pySplitter, pyItem0]
		
		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miAddToBlackList" ) ) #��������
		pyItem0.handler = self.__addToBlackList
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["addToBlackList"] = [pySplitter, pyItem0]				

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miJoinTeam" ) )
		pyItem0.handler = self.__inviteJoinTeam
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["inviteJoinTeam"] = [pySplitter, pyItem0]		# ���������飬�������

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miKickOutTeammate" ) )
		pyItem0.handler = self.__kickOutTeammate
		pyItem1 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miChangeCaptain" ) )
		pyItem1.handler = self.__changeCaptain
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )			# �����飬���Ѳ���
		self.__menuItems["teammate"] = [pySplitter, pyItem1, pyItem0]

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miJoinTong" ) )
		pyItem0.handler = self.__InviteJoinTong
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["joinTong"] = [pySplitter, pyItem0]			# �����飬���������

#		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miMountEntity" ) )
#		pyItem0.handler = self.__mountEntity
#		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
#		self.__menuItems["mountDart"] = [pySplitter, pyItem0]			# �����飬�������ڳ�

#		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miDisMountEntity" ) )
#		pyItem0.handler = self.__disMountEntity
#		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
#		self.__menuItems["disMountDart"] = [pySplitter, pyItem0]		# �ڰ��飬�������ڳ�

		pyItem0 = DefMenuItem( labelGather.getText( "TargetInfo:main", "miEspialPet" ) )
		pyItem0.handler = self.__espialPet
		self.__menuItems["espialPet"] = pyItem0

	# -------------------------------------------------
	def __setMarkStatus( self ) :
		"""
		���öӳ���Ǻ�ְҵ���
		"""
		target = self.__target
		if not rds.targetMgr.isRoleTarget( target ) :
			self.__pyCaptain.visible = False
			self.__pyClassMark.visible = False
			return
		# ���öӳ����
		self.__pyCaptain.visible = BigWorld.player().captainID == target.id
		# ����ְҵ���
		self.__pyClassMark.visible = True
		util.setGuiState( self.__pyClassMark.getGui(), ( 2, 2 ), self.__cc_pro_states[target.getClass()] )

	def __setTargetFont( self ):
		"""
		���ñ�ǩ��������ɫ
		"""
		# ���ݵȼ��Ĳ����ʾ��ͬ��������ɫ
		if not hasattr ( self.__target, "getLevel"):
			return
		dlevel = BigWorld.player().getLevel() - self.__target.getLevel()
		if dlevel <= -5 :
			self.__pyLbLevel.colour = 255, 0, 0, 255
		elif dlevel <= 4 :
			self.__pyLbLevel.colour = 255, 255, 255, 255
		elif dlevel  <= 25 :
			self.__pyLbLevel.colour = 0, 255, 0, 255
		else :
			self.__pyLbLevel.colour = 127, 127, 127, 255

	# -------------------------------------------------
	def onShowTargetInfo( self, target ) :
		"""
		��������Ŀ��
		"""
		HEAD_MAPPINGS = { csdefine.GENDER_MALE:{"chiyou": "npcm1000",
											"huangdi": "npcm1002",
											"houyi": "npcm1004",
											"nuwo": "npcm1006",
										},
					csdefine.GENDER_FEMALE:{ "chiyou": "npcm1001",
											"huangdi": "npcm1003",
											"houyi": "npcm1005",
											"nuwo": "npcm1007"
										}
						}
		RootGUI.hide( self )
		self.__target = target
		if target.getEntityType() in Const.DIRECT_TALK:	# �ɼ��㲻��ʾĿ����Ϣ by ����
			return
		title = target.getTitle()
		name = target.getName()
		if name == "":
			return
		self.__pyLbName.color = 226, 238, 0, 255
		color = "c1"
		if target.isEntityType( csdefine.ENTITY_TYPE_NPC ):
			if len( name ) > NAME_LIMIT_SHOW_LEN:
				name = "%s..."%name[:12]
		if target.isEntityType( csdefine.ENTITY_TYPE_CONVOY_MONSTER ):
			ownerName = target.ownerName
			if ownerName:
				name = ownerName + labelGather.getText( "TargetInfo:main", "de" ) + name
		self.__pyLbName.text = name							# ��������Ŀ������
		self.__pyHead.texture = target.getHeadTexture()		# ��������ͷ��
		self.__setMarkStatus()								# �������öӳ���ְҵ���
		self.__setTargetFont()								# ��������������ɫ
		isNpc = target.isEntityType( csdefine.ENTITY_TYPE_MONSTER ) or \
			target.isEntityType( csdefine.ENTITY_TYPE_NPC )#�Ƿ�Ϊ����
		isQBox = target.isEntityType( csdefine.ENTITY_TYPE_QUEST_BOX ) or \
		target.isEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BATTLE_FLAG )#��������
		if hasattr( target, "level" ):
			level = target.getLevel()
			self.__onLevelChanged( target, 1, level )							# �������õȼ�
			if level <= 0:
				self.__pyLevelBg.visible = False
				self.__onHPChanged( target, 1, 1, 1 )
				self.__onMPChanged( target, 1, 1 )
			else:
				self.__pyLevelBg.visible = not isQBox
				if isQBox:
					self.__onHPChanged( target, 1, 1, 1 )
					self.__onLevelChanged( target, 1, "" )
				else:
					self.__onHPChanged( target, target.getHP(), target.getHPMax(), target.getHP() )		# �������� HP ֵ
					self.__onMPChanged( target, target.getMP(), target.getMPMax() )		# �������� MP ֵ
		else:
			self.__pyLevelBg.visible = False
			self.__onLevelChanged( target, 1, "" )
			self.__onHPChanged( target, 1, 1, 1 )	# �������� HP ֵ
			self.__onMPChanged( target, 1, 1 )		# �������� MP ֵ
		self.__pyLbMP.visible = not( isNpc or isQBox )
		self.__pyMPBar.visible = not( isNpc or isQBox)
		self.__pyBtnPkMode.visible = target.isEntityType( csdefine.ENTITY_TYPE_ROLE )
		camp = 0
		if hasattr( target, "getCamp" ):
			camp = target.getCamp()
		self.__pyCamp.visible = ( camp > 0 and not target.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_CMAP ) )
		if camp > 0:
			util.setGuiState( self.__pyCamp.getGui(), ( 1, 2 ), ( 1, camp ) )
		isInSections = False
		isBoss = False
		if hasattr( target,"className" ) and hpSectsLoader.isInSections( target.className ):
			isInSections = True
			isBoss = hpSectsLoader.isBoss( target.className )
		self.__setBarInfos( isNpc or isQBox, isInSections, isBoss )
		self.__setBuffItems()								# �����趨BUFF
		if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			sysPKMode = target.sysPKMode	#ϵͳģʽ
			pkMode = target.pkMode
			modeText = ""
			modeColor = ( 255, 255, 255, 255 )						
			if pkMode in self._pk_modes:
				modeText = self._pk_modes[pkMode][0][0:2]
				modeColor = self._pk_modes[pkMode][1]				
			if sysPKMode in self._pk_modes:	#������ʾϵͳģʽ
				modeText = self._pk_modes[sysPKMode][0][0:2]
				modeColor = self._pk_modes[sysPKMode][1]
				
			self.__pyBtnPkMode.text = csol.asWideString( modeText )
			self.__pyBtnPkMode.commonForeColor = modeColor
			self.__pyBtnPkMode.highlightForeColor = modeColor
			self.__pyBtnPkMode.pressedForeColor = modeColor
			modelNumber = target.currentModelNumber
			if target.state == csdefine.ENTITY_STATE_CHANGING  and modelNumber != "fishing": #����״̬�Ҳ��ǵ����ʱ��ͷ����ͼ�ı�,���治��Ӹ����������ͻ���ɵ������������Ǹ�ͷ����ͼ
				self.__pyHead.texture = g_npcmodel.getHeadTexture( modelNumber )
				if target.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ): #������Ϣ״̬
					self.__onLevelChanged( target, 1, 0 )
					self.__onHPChanged( target, 1, 1, 1 )
					self.__onMPChanged( target, 1, 1 )
					self.__pyLbName.text = ""
					self.__pyClassMark.visible = False
			player = BigWorld.player()
			color = (226, 238, 0, 255)
			if player.id == target.id:
				color = PK_STATE_COLOR_MAP.get( player.pkState, (226, 238, 0, 255) )
			else:
				color = self.getRoleNameColor( target )
			self.__pyLbName.color = color
			spaceType = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) )
			if spaceType == csdefine.SPACE_TYPE_CHALLENGE:
				gender = target.getGender()
				tgID = target.id
				avatar = ""
				if tgID != player.id:
					avatar = player.memberAvatars.get( tgID, "" )
				else:
					avatar = player.avatarType
				headText = HEAD_MAPPINGS[gender][avatar]
				self.__pyHead.texture = "maps/monster_headers/%s.dds"%headText
			elif spaceType == csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI:   # ҹս����ս��
				if target != player:
					self.__pyLbName.text = labelGather.getText( "TargetInfo:main", "fengQiName" )
		self.__resetHoldFlag()						# ���ù���Ȩ��ǵı�����ɫ
		self.show()
	
	def __setBarInfos( self, isNPC, isInSections, isBoss ):
		"""
		����target��������ͷ��
		"""
		bdTexture = ""
		bgTexture = ""
		bgTop = 0.0
		hbTop = 0.0
		range = []
		borderSize = ( 210.0, 80.0 )
		if isNPC:
			range = self.__rangeNPC
			if not isInSections:						#��ͨNPC
				bdTexture = "common/border_npc"
				bgTexture = "common/bg_npc"
				bgTop = 7.0
				hbTop = 43.0
				self.__topOffset = 64.0
			else:									#��Ӣ�ֻ�boss
				bgTexture = "boss/bg_boss"
				bgTop = 30.0
				hbTop = 64.0
				borderSize = ( 230.0, 106.0 )
				self.__topOffset = 96.0
				if isBoss:							#boss
					bdTexture = "boss/border_boss"
				else:								#��Ӣ
					bdTexture = "boss/border_elite"
		else:
			range = self.__rangeNormal
			bdTexture = "common/border"
			bgTexture = "common/bg"
			bgTop = 8.0
			hbTop = 37.0
			self.__topOffset = 80.0
		self.__pyBorder.texture = "guis/general/targetinfo/%s.dds"%bdTexture
		self.__pyBg.texture = "guis/general/targetinfo/%s.dds"%bgTexture
		self.__setUIsPositions( isNPC, isInSections )
		self.__pyBg.top = bgTop
		for pyHpBar in self.__pyHPBars.values():
			pyHpBar.top = hbTop
		self.__pyLbHP.top = hbTop
		self.__pyLbHP.center = self.__pyHPBars[0].center
		self.__pyLbName.center = self.__pyLbHP.center
		self.__pyLbName.bottom = self.__pyHPBars[0].top - 5.0
		self.__pyLbLevel.center = self.__pyLevelBg.center
		self.__rangePolygon.update( range )
		self.__pyBorder.size = borderSize
		util.setGuiState( self.__pyBorder.gui, (1,1),(1,1))
	
	def __setUIsPositions( self, isNPC, isInSections ):
		"""
		����������UIλ��
		"""
		script_map = {"bg": self.__pyBg, "border": self.__pyBorder, "head":self.__pyHead, "captain":self.__pyCaptain,\
					"levelBg":self.__pyLevelBg, "levelBg":self.__pyLevelBg, "lbName": self.__pyLbName, "lbLevel": self.__pyLbLevel, \
					"hpBar_0": self.__pyHPBars[0], "hpBar_1": self.__pyHPBars[1], "mpBar":self.__pyMPBar, "lbHP":self.__pyLbHP,\
					"stIndex":self.__pyStIndex, "profession":self.__pyClassMark,"camp":self.__pyCamp, "pkModeBtn":self.__pyBtnPkMode,
					}
		for name, item in self.gui.children:
			pyScript = script_map.get( name, None )
			if pyScript is None:continue
			postions = uis_positions.get( name, None )
			if postions is None:continue
			postion = postions.get( int(isInSections), None )
			if postion is None:continue
			pyScript.pos = postion
		
	def __onPKModeChanged( self, role, pkMode):
		if self.__target and self.__target.id == role.id:
			pkMode = role.pkMode
			modeText = ""
			modeColor = ( 255, 255, 255, 255 )
			if pkMode in self._pk_modes:
				modeText = self._pk_modes[pkMode][0][0:2]
				modeColor = self._pk_modes[pkMode][1]
			self.__pyBtnPkMode.text = csol.asWideString( modeText )
			self.__pyBtnPkMode.commonForeColor = modeColor
			self.__pyBtnPkMode.highlightForeColor = modeColor
			self.__pyBtnPkMode.pressedForeColor = modeColor
			
	def __onSysModeChange( self, role, sysPKMode ):
		if self.__target and self.__target.id == role.id:
			sysPKMode = role.sysPKMode
			modeText = ""
			modeColor = ( 255, 255, 255, 255 )
			if sysPKMode in self._pk_modes:
				modeText = self._pk_modes[sysPKMode][0][0:2]
				modeColor = self._pk_modes[sysPKMode][1]
			if sysPKMode == 0 and role.pkMode in self._pk_modes:
				pkMode = role.pkMode
				modeText = self._pk_modes[pkMode][0][0:2]
				modeColor = self._pk_modes[pkMode][1]				
			self.__pyBtnPkMode.text = csol.asWideString( modeText )
			self.__pyBtnPkMode.commonForeColor = modeColor
			self.__pyBtnPkMode.highlightForeColor = modeColor
			self.__pyBtnPkMode.pressedForeColor = modeColor

	def onHideTrargetInfo( self, target ) :
		"""
		����Ŀ��
		"""
		self.__target = None
		self.__clearAllBuffs()
		RootGUI.hide( self )

	# ---------------------------------------
	def __onCaptainChanged( self, captainID ) :
		"""
		�ӳ��ı��ʱ�򱻵���
		"""
		self.__setMarkStatus()

	def __onTeamMemberLeft( self, teammateID ) :
		"""
		��Ա���
		"""
		if self.__target is None : return
		if self.__target.isEntityType( csdefine.ENTITY_TYPE_MONSTER ) :
			bootyOwner = self.__target.bootyOwner
			player = BigWorld.player()
			if ( teammateID == player.id and ( bootyOwner[1] != 0 or \
			bootyOwner[0] != teammateID and bootyOwner[0] != 0 ) ) or \
			( teammateID != player.id and bootyOwner[1] == 0 and \
			bootyOwner[0] == teammateID ) :
				self.__onSetHoldFlag( False )

	def __onTeamMemberAdded( self, teammate ) :
		"""
		��Ա����
		"""
		if self.__target is None : return
		if self.__target.isEntityType( csdefine.ENTITY_TYPE_MONSTER ) :
			bootyOwner = self.__target.bootyOwner
			player = BigWorld.player()
			if bootyOwner[1] != 0 and bootyOwner[1] == player.teamID or \
			bootyOwner[1] == 0 and bootyOwner[0] == teammate.objectID :
				self.__onSetHoldFlag( True )

	def __onUnbindTarget( self, entity ) :
		"""
		ȡ����ǰĿ���ѡ��
		"""
		self.hide()

	def __onTeamDisbanded( self ):
		"""
		�����ɢ��ʱ�򱻵���
		"""
		self.__pyCaptain.visible = False
		self.__resetHoldFlag()

	# ---------------------------------------
	def __onHPChanged( self, entity, hp, hpMax, oldValue ) :
		"""
		Ŀ�� HP �ı��ʱ�򱻵���
		"""
		if entity != self.__target : return
		if hp > hpMax:
			hp = hpMax
		self.__pyStIndex.visible = False
		hpPecent = float( hp ) / hpMax
		hpText = ""
		if hasattr( entity, "className" ):
			color = "c1"
			if hasattr( entity, "nameColor" ):
				nameColor = entity.nameColor
				color = self.__getColorByNameColor( nameColor )
			className = entity.className
			sections = hpSectsLoader.getSections( className )
			hpText = "%0.1f%%" %(hpPecent*100)
			if sections > 0:										#�����˶��Ѫ��
				sectperct = 1.0/sections
				curIndex = 0
				for index in range( sections ):
					if hpPecent > sectperct*index and \
					hpPecent <= sectperct*( index + 1):
						curIndex = index + 1
						break
				topColor = HP_SECTION_COLOR_MAP.get( curIndex, None )
				bottomColor = HP_SECTION_COLOR_MAP.get( curIndex - 1, None )
				self.__pyStIndex.visible = curIndex > 1
				if self.__curIndex != curIndex:
					self.__curIndex = curIndex
					if sections != curIndex:
						self.__pyStIndex.fontSize = 32.0
						if self.__zoomTimerID > 0:
							BigWorld.cancelCallback( self.__zoomTimerID )
							self.__zoomTimerID = 0
						self.__zoomTimerID = BigWorld.callback( 0.3, Functor( self.__setIndexFontSize, curIndex ) )
					else:
						self.__pyStIndex.fontSize = self.__priFontSize
						self.__pyStIndex.text = "x%d"%curIndex
				self.__pyHPBars[0].visible = topColor is not None
				self.__pyHPBars[1].visible = bottomColor is not None
				if topColor:
					curPercent = ( hpPecent - sectperct*index )/sectperct
					self.__pyHPBars[0].color = topColor
					self.__pyHPBars[0].value = curPercent
				if bottomColor:
					self.__pyHPBars[1].color = bottomColor
					self.__pyHPBars[1].value = 1.0
			else:
				self.__pyHPBars[0].visible = True
				self.__pyHPBars[1].visible = False
				self.__pyHPBars[0].value = hpPecent
				self.__pyHPBars[0].color = cscolors[color]
				if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
					hpText = "%d/%d"%( hp, hpMax )
					if formulas.isHierarchy( entity.species, csdefine.PET_HIERARCHY_GROWNUP ) :
						color = "c1"
					elif formulas.isHierarchy( entity.species, csdefine.PET_HIERARCHY_INFANCY1 ) :
						color = "c19"
					else :
						color = "c49"
			self.__pyLbName.color = cscolors[color]
		elif entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			self.__pyHPBars[0].visible = True
			self.__pyHPBars[1].visible = False
			self.__pyHPBars[0].value = hpPecent
			self.__pyHPBars[0].color = cscolors["c3"]
			hpText = "%d/%d"%( hp, hpMax )
		if hp == 1 and hpMax == 1:
			hpText = ""
		self.__pyLbHP.text = hpText
	
	def __setIndexFontSize( self, curIndex ):
		"""
		"""
		if self.__pyStIndex.text != "x%d"%curIndex:
			self.__pyStIndex.text = "x%d"%curIndex
		self.__pyStIndex.fontSize = self.__priFontSize
	
	def __getColorByNameColor( self, nameColor ):
		"""
		ͨ��nameColor��ȡ��ɫ
		"""
		color = "c1"
		player = BigWorld.player()
		if nameColor == 0:
			color = "c48"
		elif nameColor == 3:
			color = "c47"
		elif nameColor == 4:
			color = "c47"
		else:
			color = player.getCamp() == nameColor and "c47" or "c48"
		return color

	def __onMPChanged( self, entity, mp, mpMax ) :
		"""
		Ŀ�� MP �ı��ʱ�򱻵���
		"""
		if entity != self.__target : return
		if mpMax > 0 :
			self.__pyMPBar.value = float( mp ) / mpMax
		else :
			self.__pyMPBar.value = 0
		if mp == 1 and mpMax == 1:
			self.__pyLbMP.text = ""
		else:
			self.__pyLbMP.text = "%d/%d" % ( mp, mpMax )

	def __onLevelChanged( self, entity, oldLevel, level ):
		"""
		Ŀ��ȼ��ı��ʱ�򱻵���
		"""
		if entity != self.__target : return
		self.__setTargetFont()
		if level == "" or level == 0:
			self.__pyLevelBg.visible = False
			self.__pyLbLevel.text = ""
		else:
			self.__pyLevelBg.visible = True
			self.__pyLbLevel.text = str( level )

	def __onProMouseEnter( self ) :
		"""
		������ְҵ���ʱ������
		"""
		tips = csconst.g_chs_class[self.__target.getClass()]
		toolbox.infoTip.showToolTips( self, tips )

	def __onProMouseLeave( self ) :
		"""
		����뿪ְҵ���ʱ������
		"""
		toolbox.infoTip.hide()

	def __onTargetModelChange( self, entity, oldModel, newModel ):
		"""
		�Ƿ�������Ϣ
		"""
		if entity != self.__target:return
		headTexture = entity.getHeadTexture()
		if entity.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ): #������Ϣ״̬
			modelNumber = entity.currentModelNumber
			headTexture = g_npcmodel.getHeadTexture( modelNumber )
			self.__onLevelChanged( entity, 1, 0 )
			self.__onHPChanged( entity, 1, 1, 1 )
			self.__onMPChanged( entity, 1, 1 )
			self.__pyLbName.text = ""
			self.__pyClassMark.visible = False
		self.__pyHead.texture = headTexture

	def __onNameChanged( self, entityID, nameText ):
		"""
		���ָı�
		"""
		if self.__target and self.__target.id == entityID:
			self.__pyLbName.text = nameText
	
	def __onNameColorChanged( self, target ):
		"""
		nameColorֵ�ı�
		"""
		if self.__target and self.__target.id == target.id:
			pCamp = BigWorld.player().getCamp()
			nameColor = 0
			if hasattr( target, "nameColor" ):
				nameColor = target.nameColor
				color = self.__getColorByNameColor( nameColor )
				if hasattr( target, "className" ):
					className = entity.className
					sections = hpSectsLoader.getSections( className )
					self.__pyHPBars[1].visible = sections is not None
					if sections: return
					self.__pyLbName.color = cscolors[color]
					self.__pyHPBars[0].color = cscolors[color]
			
	def __onMenuPopUp( self ) :
		"""
		�˵�����ǰ������
		"""
		player = BigWorld.player()
		target = self.__target
		if target == player :
			return -1												# ���� False �����������˵�
		if player.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ) or \
		target.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
			return -1
		if hasattr( target, "onFengQi" ) and target.onFengQi:
			return -1

		if rds.targetMgr.isRoleTarget( target ) :
			# ���ݵ�ǰ�����Ŀ���״̬��������Ҫ��ʾ��Щ�˵���
			self.__pyCMenu.clear()
			pyItems = self.__menuItems["persistence"]					# ÿ�ζ�����ʾ�Ĳ˵���
			self.__pyCMenu.pyItems.adds( pyItems )
			canConsGrade = player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHT_MEMBER_MANAGE )
			grade = player.tong_grade
			targetName = target.getName()
			targetTongName = target.tongName
			if targetName in player.friends:							# Ŀ�����ҵĺ����б�
				pyItems0 = self.__menuItems["friendChat"]
				self.__pyCMenu.pyItems.adds( pyItems0 )
				pyItems1 = self.__menuItems["addToBlackList"]
				self.__pyCMenu.pyItems.adds( pyItems1 )
			else:
				pyItems = self.__menuItems["addToBuddy"]
				self.__pyCMenu.pyItems.adds( pyItems )
			if not player.isJoinTeam() or \
			not player.isTeamMember( target.id ) :
				pyItems = self.__menuItems["inviteJoinTeam"]			# �������
				self.__pyCMenu.pyItems.adds( pyItems )
			elif player.isCaptain() and player.isTeamMember( target.id ) :
				pyItems = self.__menuItems["teammate"]					# ��Ա���
				self.__pyCMenu.pyItems.adds( pyItems )
			if player.isJoinTong() and canConsGrade and \
			targetTongName == "":
				pyItems = self.__menuItems["joinTong"]					# ���������
				self.__pyCMenu.pyItems.adds( pyItems )
			return True
#		elif rds.targetMgr.isSelfDartTarget( target ):
#			self.__pyCMenu.clear()
#			if not target.isRideOwner:
#				pyItems = self.__menuItems["mountDart"]					# ���ڳ�
#				self.__pyCMenu.pyItems.adds( pyItems )
#			else:
#				pyItems = self.__menuItems["disMountDart"]				# ���ڳ�
#				self.__pyCMenu.pyItems.adds( pyItems )
		elif rds.targetMgr.isPetTarget( target ) and target.getOwner().id != player.id:
			self.__pyCMenu.clear()
			pyItem = self.__menuItems["espialPet"]
			self.__pyCMenu.pyItems.add( pyItem )
		else:
			return -1

	def __onAfterMenuPopUp( self ) :
		"""
		�˵����������
		"""
		self.__updateMenu()

	def __onMenuItemClick( self, pyItem ) :
		"""
		����˵�ѡ��ʱ������
		"""
		pyItem.handler( pyItem )

	def __updateMenu( self ) :
		"""
		������ҵ�״̬���²˵������Ч��
		"""
		str = '0'
		if not self.__pyCMenu.visible : return
		if self.__target is None : return
		player = BigWorld.player()
		try:
			str = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_CANNOTQIECUO )			# ��ͼ�Ƿ�����д�,�������д践��1
		except:
			pass
		distance = player.position.flatDistTo( self.__target.position )
		self.__menuItems["persistence"][2].enable = distance <= 10.0								# ���۲족ѡ��
		self.__menuItems["persistence"][4].enable = distance <= 20.0								# �����桱ѡ��
		self.__menuItems["persistence"][6].enable = distance <= csconst.COMMUNICATE_DISTANCE		# ��������Ʒ���ס�ѡ��
		self.__menuItems["persistence"][7].enable = distance <= csconst.COMMUNICATE_DISTANCE		# ��������ｻ�ס�ѡ��
		self.__menuItems["persistence"][9].enable = ( distance <= csconst.QIECUO_REQUEST_MAXDIS ) and not eval( str ) # ���д衱ѡ��
		#self.__menuItems["teammate"][1].enable = distance <= 15									# ��������桱ѡ��
		BigWorld.callback( 0.1, self.__updateMenu )

	def __isSubItemsMouseHit( self ) :
		if self.__pyClassMark.isMouseHit() :
			return True
		for pyBuffItem in self.__pyBuffItems + self.__pyDuffItems :
			if pyBuffItem.isMouseHit() :
				return True
		return False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		RootGUI.onLMouseDown_( self, mods )
		return self.isMouseHit()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		"""
		�ж�����Ƿ���ڶ����������
		"""
		return self.__rangePolygon.isPointIn( self.mousePos ) \
		or self.__isSubItemsMouseHit()

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.__target = None
		self.hide()

	def show( self ) :
		if self.__target is not None :
			RootGUI.show( self )

	def hide( self ) :
		#rds.targetMgr.unbindTarget( self.__target )
		self.__clearAllBuffs()
		self.__target = None
		RootGUI.hide( self )

	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		ϵͳ״̬�ı�֪ͨ
		"""
		if newStatus != Define.GST_IN_WORLD :
			self.__pyCMenu.close()

	def getRelation( self, role ):
		"""
		��ȡ�����������ɫ�Ĺ�ϵ,ֻ��2��
		"""
		player = BigWorld.player()
		if role.id == player.id:
			return csdefine.RELATION_FRIEND
		else:
			if self.canPlayerPkRole( role ) and \
			self.canRolePkPlayer( role ):
				return csdefine.RELATION_ANTAGONIZE
			elif not self.canPlayerPkRole( role ) and \
			self.canRolePkPlayer( role ):
				return csdefine.RELATION_NEUTRALLY
			elif self.canPlayerPkRole( role ) and \
			not self.canRolePkPlayer( role ):
				return csdefine.RELATION_NEUTRALLY
			else:
				return csdefine.RELATION_FRIEND
	
	def canPlayerPkRole( self, role ):
		"""
		�Լ��Ƿ�PK�������
		"""
		player = BigWorld.player()
		return player.canPk( role ) and \
		player.currAreaCanPk() and \
		role.currAreaCanPk()
	
	def canRolePkPlayer( self, role ):
		"""
		��������Ƿ����PK�Լ�
		"""
		return role.canPkPlayer() and \
		role.currAreaCanPk() and \
		BigWorld.player().currAreaCanPk()

	def getRoleNameColor( self, role ):
		"""
		���Ӧ����ʾ��������ֵ���ɫ
		"""
		if hasattr( role, "onFengQi" ) and role.onFengQi:  # ҹս����ս������ʾΪ��ɫ
			return cscolors["c8"]
		player = BigWorld.player()
		pTongDBID = player.tong_dbID
		tong_dbID = 0
		if hasattr( role, "tong_dbID" ):
			tong_dbID = role.tong_dbID
		cwTongInfos = player.tongInfos
		dTongDBID = 0
		if cwTongInfos.has_key( "defend" ):
			dTongDBID = cwTongInfos["defend"]
		if player.tong_isCityWarTong( tong_dbID ):
			if dTongDBID > 0: #�з��ط�
				if pTongDBID == tong_dbID: #ͬһ�����,��ɫ
					return cscolors["c4"]
				else:
					if tong_dbID == dTongDBID: #���ط�
						return cscolors["c8"]	#��ɫ
					else:
						if pTongDBID == dTongDBID:
							return cscolors["c8"]	#��ɫ
						else:
							return cscolors["c48"]	#��ɫ
			else:
				if tong_dbID == pTongDBID:
					return cscolors["c4"]
				else:
					return cscolors["c8"]
		if player.qieCuoTargetID == role.id:
			return cscolors["c8"]
			
		if role.id in player.pkTargetList.keys():
			return cscolors["c8"]

		if player.tong_isRobWarEnemyTong( role.tong_dbID ) :
			return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]

		relation = player.queryRelation( role )

		if player.hasFlag( csdefine.ROLE_FLAG_SPEC_COMPETETE ):						# ������Ӿ��������⾺��
			if player.canPk( role ) :
				return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			else :
				return ROLE_RELATION_COLOR_MAP[ relation ]
		else :
			compState = None
			try :
				compState = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) )
			except :
				pass
			if compState == csdefine.SPACE_TYPE_ROLE_COMPETITION :					# ���˾���
				return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_TONG_COMPETITION :				# ��Ὰ��
				if role.pkState == csdefine.PK_CONTROL_PROTECT_PEACE:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				elif role.tongName == player.tongName:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_TONG_ABA:
				if role.tongName != player.tongName:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_YXLM or compState == csdefine.SPACE_TYPE_YXLM_PVP:							#Ӣ�����˸���
				if role.id in player.teamMember:				#���Լ�����
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ]
			elif compState == csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN:
				if role.tongName == player.tongName:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					return ( 255, 0, 0, 255 )
			elif compState == csdefine.SPACE_TYPE_TONG_TURN_WAR:			#��ᳵ��ս
				if role.id in player.teamMember:
					return ROLE_RELATION_COLOR_MAP[ relation ]
				else:
					relation = self.getRelation( role )
					return self._colors_map.get( relation, ( 255, 255, 255, 255 ) )
			elif compState == csdefine.SPACE_TYPE_CITY_WAR_FINAL:		#���ս����
				pBelong = player.getCityWarTongBelong( pTongDBID )
				rBelong = player.getCityWarTongBelong( role.tong_dbID )
				if pBelong == rBelong:	#���˰�ᣬ��ɫ
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_FRIEND ]
				else:
					return ROLE_RELATION_COLOR_MAP[ csdefine.RELATION_ANTAGONIZE ] 
			else :
				return PK_STATE_COLOR_MAP[ role.pkState ]
	# ----------------------------------------------------------------
	# menuitem handlers
	# ----------------------------------------------------------------
	def __whisper( self, pyItem ) :
		"""
		��Ŀ�����˽��
		"""
		if self.__target is None : return
		chatFacade.whisperWithChatWindow( self.__target.getName() )

	def __espialTarget( self, pyItem ):
		"""
		����۲�Է���װ��������
		"""
		if self.__target is None : return
		espial.onEspialTarget( self.__target )

	def __requestQieCuo( self, pyItem ):
		"""
		�����д�
		"""
		if self.__target is None : return
		BigWorld.player().requestQieCuo( self.__target.id )

	def __followTarget( self, pyItem ):
		"""
		����Ŀ���ƶ�
		"""
		if self.__target is None : return
		#GUIFacade.followTarget( self.__target )
		BigWorld.player().autoFollow( self.__target.id )

	def __inviteJoinTeam( self, pyItem ) :
		"""
		�������
		"""
		if self.__target is None : return
		GUIFacade.inviteToTeam( self.__target )

	def __inviteTradeItem( self, pyItem ) :
		"""
		������Ʒ����
		"""
		if self.__target is None : return
		GUIFacade.inviteSwapItem( self.__target, TRADE_SWAP_ITEM )

	def __inviteTradePet( self, pyItem ):
		"""
		������ｻ��
		"""
		if self.__target is None : return
		GUIFacade.inviteSwapItem( self.__target, TRADE_SWAP_PET )

	def __addToBuddy( self, pyItem ) :
		"""
		��Ϊ����
		"""
		if self.__target is None : return
		BigWorld.player().addFriend( self.__target.getName() )

	def __addToBlackList( self, pyItem ) :
		"""
		�ӵ�������
		"""
		if self.__target is None : return
		name = self.__target.getName()
		BigWorld.player().addBlacklist( name )
	
	def __friendChat( self, pyItem ):
		"""
		��������
		"""
		if self.__target is None : return
		name = self.__target.getName()
		plmChatMgr.onOriginateChat( name )

	def __kickOutTeammate( self, pyItem ) :
		"""
		��������
		"""
		if self.__target is None : return
		GUIFacade.kickoutTeam( self.__target.id )

	def __changeCaptain( self, pyItem ) :
		"""
		����Ŀ��Ϊ�ӳ�
		"""
		if self.__target is None : return
		BigWorld.player().changeCaptain( self.__target.id )

	def __inviteFollow( self, pyItem ) :
		"""
		Ҫ���Ǹ�����
		"""
		if self.__target is None : return
		BigWorld.player().inviteFollow( self.__target.id )

	def __InviteRide( self, pyItem ):
		"""
		���빲��
		"""
		player = BigWorld.player()
		player.cell.inviteRide( self.__target.id )

	def __InviteJoinTong( self, pyItem ):
		"""
		���������
		"""
		player = BigWorld.player()
		player.tong_requestJoin( self.__target.id )

	def __mountEntity( self, pyItem ):
		"""
		�ϳ�
		"""
		player = BigWorld.player()
		player.targetEntity.mountEntity( player, 0 )

	def __disMountEntity( self, pyItem ):
		"""
		�³�
		"""
		player = BigWorld.player()
		player.targetEntity.disMountEntity( player )

	def __espialPet( self, pyItem ):
		"""
		�忴��������
		"""
		if self.__target is None:
			return
		if rds.targetMgr.isPetTarget( self.__target ):
			self.__target.requeryPetDatas()

	# ---------------------------------------------------------------------------------------------
	def __setBuffItems( self ):
		"""
		ˢ������BUFF
		"""
		if self.__reBuffsCBID != 0:
			BigWorld.cancelCallback( self.__reBuffsCBID )
			self.__reBuffsCBID = 0

		if self.__target is None:
			self.__clearAllBuffs()
			return

		# �Գ���Ҫ���⴦��
		target = self.__target
		if target.utype == csdefine.ENTITY_TYPE_PET and target.getOwner() == BigWorld.player():
			self.__showSelfPetBuffItems()
			return

		# ����������һЩѡ�ж�����û��attrBuffItems��
 		try:
 			buffInfos = []
 			duffInfos = []
			for buffItem in target.attrBuffItems:
				if not buffItem.isNotIcon:	# Ҫ��ʾbuffͼ��ĲŸ���
					if buffItem.baseItem.isMalignant():
						duffInfos.append( buffItem )
					else:
						buffInfos.append( buffItem )
			self.__reAllBuffs( duffInfos, True )
			self.__reAllBuffs( buffInfos, False )
			self.__layoutBuffs()
			self.__reBuffsCBID = BigWorld.callback( 1.0, self.__setBuffItems )				# CDʱ�����
		except AttributeError:
			self.__clearAllBuffs()

	def __showSelfPetBuffItems( self ):
		"""
		��ʾ���������buff
		"""
		targetBuffs  = BigWorld.player().pcg_getActPetBuffList()
		buffInfos = []
		duffInfos = []
		for buff in targetBuffs:
			if not buff.isNotIcon:	# Ҫ��ʾbuffͼ��ĲŸ���
				if buff.baseItem.isMalignant():
					duffInfos.append( buff )
				else:
					buffInfos.append( buff )
		self.__reAllBuffs( duffInfos, True )
		self.__reAllBuffs( buffInfos, False )
		self.__layoutBuffs()
		self.__reBuffsCBID = BigWorld.callback( 1.0, self.__setBuffItems )				# CDʱ�����

	def __reAllBuffs( self, buffItems, isDeBuff ):
		"""
		��������BUFF / DeBuff
		"""
		if isDeBuff:
			pyBuffItems = self.__pyDuffItems
		else:
			pyBuffItems = self.__pyBuffItems

		# ����Ѿ���BUFF��ʾ�������ˣ�����һ�¾�����
		for index, itemInfo in enumerate( buffItems ):
			if index < len( pyBuffItems ):
				pyBuffItems[ index ].update( itemInfo )
			else:
				self.__onAddBuff( itemInfo, isDeBuff )

		# ��������BUFFͼ��
		n = len( pyBuffItems ) - len( buffItems )
		while n > 0:
			pyBuffItems[ -1 ].dispose()
			pyBuffItems.pop( -1 )
			n = n - 1

	def __clearAllBuffs( self ):
		"""
		ɾ������BUFF / DeBuff
		"""
		if self.__reBuffsCBID != 0:
			BigWorld.cancelCallback( self.__reBuffsCBID )
			self.__reBuffsCBID = 0
		for pyItem in self.__pyBuffItems :
			pyItem.dispose()
		for pyItem in self.__pyDuffItems :
			pyItem.dispose()
		self.__pyBuffItems = []
		self.__pyDuffItems = []

	def __onAddBuff( self, itemInfo, isDeBuff ):
		"""
		����һ��BUFF / DeBuff
		"""
		if isDeBuff:
			pyBuffItems = self.__pyDuffItems
		else:
			pyBuffItems = self.__pyBuffItems
		pyItem = BuffItem()
		self.addPyChild( pyItem )
		pyItem.update( itemInfo )
		pyBuffItems.append( pyItem )

	def __layoutBuffs( self ) :
		"""
		�������� Buff / DeBuff ��λ��
		"""
		left = self.__pyMPBar.left
		for idx, pyItem in enumerate( self.__pyBuffItems ):
			pyItem.left = left + idx * ( pyItem.width + 2 )
			pyItem.top = self.__topOffset

		for idx, pyItem in enumerate( self.__pyDuffItems ):
			pyItem.left = left + idx * ( pyItem.width + 2 )
			pyItem.top = self.__topOffset + pyItem.height
		if len( self.__pyDuffItems ) > 0:
			self.height = max( self.__minHeight, self.__pyDuffItems[0].bottom + 5.0 )

	def __onInviteJoinDance( self, requestEntityID ):
		"""
		�յ���������
		"""
		requestEntity = BigWorld.entities.get( requestEntityID )
		if requestEntity:
			# "%s �����㹲�裬���Ƿ���ܣ�"
			msg = mbmsgs[0x0d41] % requestEntity.playerName
			def notarize( id ) :
				player = BigWorld.player()
				if id == RS_YES :
					if player.isMoving():
						player.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_NO_MOVING )
						self.__currentInviteDanceMessageBox = showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
						return
					if player.isJumping():
						player.statusMessage( csstatus.JING_WU_SHI_KE_DANCE_NO_JUMPING )
						self.__currentInviteDanceMessageBox = showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
						return
					if player.vehicleDBID:
						player.statusMessage( csstatus.ACTION_CANT_USE_ON_VEHICLE )
						self.__currentInviteDanceMessageBox = showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
						return

					#position = player.position
					#translations = position + ( position - requestEntity.position )
					matrix = Math.Matrix()
					#matrix.setTranslate( translations )
					player.turnaround( matrix, None )	# ת��̶�����

					player.cell.answerDanceRequest( True, requestEntityID )
				else:
					player.cell.answerDanceRequest( False, requestEntityID )
			self.__currentInviteDanceMessageBox = showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def __onStopRequestDance( self ):
		"""
		ȡ�����빲��,�ر�������Ϣ
		"""
		self.__currentInviteDanceMessageBox.dispose()

	def __onReceiveMessageSuanGuaZhanBu( self, money ):
		"""
		�յ�����ռ��
		"""
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.selectSuanGuaZhanBu()
		# "��Ҫ����Ҫ����%d�����Ҫ��ô��"
		msg = mbmsgs[0x0d43] % (money/10000)
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize )

	def __onSetHoldFlag( self, isOwner ) :
		"""
		���ù���Ȩ����ɫ
		"""
		fx = { False : "COLOUR_EFF",  True: "BLEND" }
		for pyHpBar in self.__pyHPBars.values():
			hpBar = pyHpBar.getGui()
			hpBar.materialFX = fx[bool( isOwner )]
		lbHP = self.__pyLbHP.getGui()
		lbHP.materialFX = fx[bool( isOwner )]

	def __resetHoldFlag( self ) :
		"""
		�����仯ʱ�������ù������Ȩ���
		"""
		if self.__target is None : return
		if self.__target.isEntityType( csdefine.ENTITY_TYPE_MONSTER ) :
			player = BigWorld.player()
			bootyOwner = self.__target.bootyOwner
			if ( bootyOwner[1] != 0 and bootyOwner[1] == player.teamID ) or \
			( bootyOwner[1] == 0 and ( bootyOwner[0] == player.id or \
			bootyOwner[0] in player.teamMember ) ) or bootyOwner == ( 0, 0 ) :
				self.__onSetHoldFlag( True )		# �������κ��ˡ�������һ�������ڶ��飬����Ϊ���챳��
			else :
				self.__onSetHoldFlag( False )		# ��������Ϊ��ɫ����
		else :
			self.__onSetHoldFlag( True )