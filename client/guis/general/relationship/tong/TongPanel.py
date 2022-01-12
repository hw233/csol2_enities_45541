# -*- coding: gb18030 -*-
#
# $Id: TongPanel.py,v 1.25 2008-08-30 09:12:04 huangyongwei Exp $

"""
implement TongPanel class
"""
from guis import *
from MenuItem import *
import BigWorld
from LabelGather import labelGather
from Function import Functor
from guis.controls.TabCtrl import TabPanel
from guis.controls.ListItem import MultiColListItem
from guis.controls.ListPanel import ListPanel
from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ContextMenu import ContextMenu
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from ManagerPanel import MemberMgr
from ManagerPanel import LeagueMgr
from DutyPanel import DutyPanel
from DutySetting import DutySetting
from GradeSetting import GradeSetting
from TongFund import TongFund
from FoundTong import FoundTong
from AffichePanel import AffichePanel
from InfoPanel import InfoPanel, WEEKSTATE
from RemarkBox import RemarkBox
from  Time import Time
import GUIFacade
import csdefine
import csconst
import Const
import Timer
import math
from ChatFacade import chatFacade
from ChangeNameBox import ChangeNameBox
from AbstractTemplates import MultiLngFuncDecorator

class deco_InitCheckEx( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyCheckEx ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		pyCheckEx.pyText_.charSpace = -1
		pyCheckEx.pyText_.fontSize = 12

class TongPanel( TabPanel ):
	def __init__( self, tabPanel = None, pyBinder = None ):
		TabPanel.__init__( self, tabPanel )
		self.__memberItems = {}
		self.__onlineMembers = []
		self.__gradeDuties = {}
		self.__affiche = ""
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyBinder = pyBinder
		self.sortByNameFlag = False	# 按名字排序的标记，如果为0表示当前是从小到大排，为1则表示从大到小排
		self.sortByLevelFlag = 0	# 按等级排序的标记
		self.sortByMetierFlag = 0	# 按职业排序的标记
		self.areaQueryTime = 0

		self.__pyListPanelSelected = None
		self.__pyListPanel = ListPanel( tabPanel.membsPanel.clipPanel, tabPanel.membsPanel.sbar )
		self.__pyListPanel.rMouseSelect = True
		self.__pyListPanel.autoSelect = False
		self.__pyListPanel.onItemSelectChanged.bind( self.__onItemSelected )

		self.__pyItemsPanel = ItemsPanel( tabPanel.infoBg.clipPanel, tabPanel.infoBg.sbar )

		infopanel = GUI.load( "guis/general/relationwindow/tongpanel/info.gui" )
		uiFixer.firstLoadFix( infopanel )
		self.__pyInfoPanel = InfoPanel( infopanel )
		self.__pyItemsPanel.addItem( self.__pyInfoPanel )
		self.__pyItemsPanel.perScroll = 50.0

		self.__pyStTongName = CSRichText( tabPanel.stTongName )
		self.__pyStTongName.align = "R"
		self.__pyStTongName.foreColor = ( 0, 233, 0, 233 )
		self.__pyStTongName.text = ""

		self.__pyStTongLevel = StaticText( tabPanel.stTongLevel )
		self.__pyStTongLevel.text = ""

#		self.__pyStNum = StaticText( tabPanel.stMemNum )
#		self.__pyStNum.text = ""
		
#		self.__pyStSignCount = StaticText( tabPanel.stSignCount )
#		self.__pyStSignCount.text = ""

#		self.__pyStWeekState = StaticText( tabPanel.stWeekState )	# 本周帮会状态

		self.__pyBtnName = HButtonEx( tabPanel.membsPanel.header.header_0 )
		self.__pyBtnName.setExStatesMapping( UIState.MODE_R3C1 )
		#self.__pyBtnName.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnName, "RelationShip:main", "btnName" )
		self.__pyBtnName.onLClick.bind( self.__onSortByName )

		self.__pyBtnLevel = HButtonEx( tabPanel.membsPanel.header.header_1 )
		self.__pyBtnLevel.setExStatesMapping( UIState.MODE_R3C1 )
		#self.__pyBtnLevel.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnLevel, "RelationShip:main", "btnLevel" )
		self.__pyBtnLevel.onLClick.bind( self.__onSortByLevel )

		self.__pyBtnPro = HButtonEx( tabPanel.membsPanel.header.header_2 )
		self.__pyBtnPro.setExStatesMapping( UIState.MODE_R3C1 )
		#self.__pyBtnPro.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnPro, "RelationShip:main", "btnProf" )
		self.__pyBtnPro.onLClick.bind( self.__onSortByPro )

		self.__pyBtnDutySet = Button( tabPanel.dutySet ) 			#职务设置
		self.__pyBtnDutySet.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDutySet.onLClick.bind( self.__onDutySet )
		labelGather.setPyBgLabel( self.__pyBtnDutySet, "RelationShip:TongPanel", "dutySet" )

		self.__pyBtnGradeSet = Button( tabPanel.gradeSet ) 			#权限设置
		self.__pyBtnGradeSet.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnGradeSet.onLClick.bind( self.__onGradeSet )
		labelGather.setPyBgLabel( self.__pyBtnGradeSet, "RelationShip:TongPanel", "gradeSet" )

		self.__pyBtnLeagueMgr = Button( tabPanel.leagueMgr ) 		#同盟管理
		self.__pyBtnLeagueMgr.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnLeagueMgr.onLClick.bind( self.__onLeagueMgr )
		labelGather.setPyBgLabel( self.__pyBtnLeagueMgr, "RelationShip:TongPanel", "leagueMgr" )

		self.__pyBtnMemberMgr = Button( tabPanel.memberMgr ) 		#成员管理
		self.__pyBtnMemberMgr.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnMemberMgr.onLClick.bind( self.__onMemberMgr )
		labelGather.setPyBgLabel( self.__pyBtnMemberMgr, "RelationShip:TongPanel", "memberMgr" )

		self.__pyBtnAffiche = HButtonEx( tabPanel.btnAffiche ) 		#公告按钮
		self.__pyBtnAffiche.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnAffiche, "RelationShip:TongPanel", "btnAffiche" )
		self.__pyBtnAffiche.onMouseEnter.bind( self.__onShowAffiche )
		self.__pyBtnAffiche.onMouseLeave.bind( self.__onHideAffiche )
		self.__pyBtnAffiche.onLClick.bind( self.__onShowAfficheWnd )
		
		self.__pyBtnFund = HButtonEx( tabPanel.btnFund ) 		#帮会资金按钮
		self.__pyBtnFund.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnFund, "RelationShip:TongPanel", "btnFund" )
		self.__pyBtnFund.onLClick.bind( self.__onFund )
		
		self.__pyBtnSign = HButtonEx( tabPanel.btnSign ) 		#帮会签到按钮
		self.__pyBtnSign.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnSign, "RelationShip:TongPanel", "btnSign" )
		self.__pyBtnSign.onLClick.bind( self.__onSign )

		self.__pyFilterCK = CheckBoxEx( tabPanel.filterCK ) 			#全部，在线选项
		self.__pyFilterCK.checked = True
		self.__pyFilterCK.onCheckChanged.bind( self.__onFilterCheck )
		self.__pyFilterCK.text = labelGather.getText( "RelationShip:main", "ckOffline" )

		self.__pyOptionCB = ODComboBox( tabPanel.membsPanel.header.optionBox )	#帮会，家族等选项
		labelGather.setPyBgLabel( self.__pyOptionCB.pyBox_, "RelationShip:TongPanel", "options" )
		self.__pyOptionCB.foreColor = ( 0, 255, 186, 255 )
		self.__pyOptionCB.autoSelect = False
		self.__pyOptionCB.onItemSelectChanged.bind( self.__onOptionChange )

		area = labelGather.getText( "RelationShip:RelationPanel", "area" )
		remark = labelGather.getText( "RelationShip:TongPanel", "ramark" )
		duty = labelGather.getText( "RelationShip:FamilyPanel", "duty" )
		totalContribute = labelGather.getText( "RelationShip:TongPanel", "totalContribute" )
		currentContribute = labelGather.getText( "RelationShip:TongPanel", "currentContribute" )
		thisWeekContribute = labelGather.getText( "RelationShip:TongPanel", "thisWeekContribute" )
		lastWeekContribute = labelGather.getText( "RelationShip:TongPanel", "lastWeekContribute" )
		self.__pyOptionCB.addItems( [duty, area, remark, totalContribute, currentContribute, thisWeekContribute, lastWeekContribute] )
		self.__pyOptionCB.selItem = duty
		#for pyComText in self.__pyOptionCB.pyItems:
		#	pyComText.h_anchor = "CENTER"
		self.__remainTime = 0
		self.pyMenuItems = {}
		self.__createPopMenu()
		self.__pyGradeSetting = GradeSetting() 	#权限设置面板
		self.__pyRemarkBox = RemarkBox( ) 		#成员备注面板
		self.__pyTongFund = TongFund()			#帮会资金面板
		self.__rTimerID = 0

		self.__initCheckEx( self.__pyFilterCK )

	@deco_InitCheckEx
	def __initCheckEx( self, pyCheckEx ):
		pyCheckEx.pyText_.charSpace = 0
		pyCheckEx.pyText_.fontSize = 12

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_TONG_FOUND"] = self.__onFoundTong 						#与NPC对话弹出家族创建窗口
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_MEMBERINFO"] = self.__setMemberInfo
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_ONLINE_STATE"] = self.__updateMemberOnlineState
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_GRADE"] = self.__updateMemberGrade
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_LEVEL"] = self.__updateMemberLevel
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_NAME"] = self.__updateMemberName
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_SCHOLIUM"] = self.__updateMemberSchlium
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_AREA"] = self.__updateMemberArea
		self.__triggers["EVT_ON_ROLE_CORPS_NAME_CHANGED"] = self.__onTongNameChange
		self.__triggers["EVT_ON_TOGGLE_TONG_REMOVE_MEMBER"] = self.__removeMember
		self.__triggers["EVT_ON_TOGGLE_TONG_INIT_DUTY_NAME"] = self.__onInitDutyName
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_DUTY_NAME"] = self.__onUpdateDutyName
		self.__triggers["EVT_ON_TOGGLE_TONG_INIT_DUTYGRADE"] = self.__onInitDutyGrade
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_DUTYGRADE"] = self.__onUpdateDutyGrade
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_CONTRIBUTE"] = self.__onContributeChange 	#帮会贡献度改变
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_TCONTRIBUTE"] = self.__onTContributeChange	#帮会总贡献度改变
		self.__triggers["EVT_ON_TOGGLE_TONG_CLEAR_ALL"] = self.reset
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_AFFICHE"] = self.__onUpdateAffiche
#		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_FAMILY_GRADE"] = self.__updateMemberFamilyGrade
		self.__triggers["EVT_ON_TOGGLE_TONG_DISSMISS_REMAINTIME"] = self.__setTongDismissRemainTime
		
		#帮会信息
		self.__triggers["EVT_ON_TOGGLE_TONG_SET_LEAGUE"] = self.__onSetLeague 					#初始化帮会同盟
		self.__triggers["EVT_ON_TOGGLE_TONG_ADD_LEAGUE"] = self.__onAddLeague 					#添加帮会同盟
		self.__triggers["EVT_ON_TOGGLE_TONG_DEL_LEAGUE"] = self.__onDelLeague 					#删除帮会同盟
		self.__triggers["EVT_ON_TOGGLE_TONG_SET_WEEKSTATE"] = self.__onSetWeekState 				#帮会状态
		self.__triggers["EVT_ON_TOGGLE_TONG_SET_PRESTIGE"] = self.__onSetPrestige 				#帮会声望
		self.__triggers["EVT_OPEN_TONG_SET_HOLD_CITY"] = self.__onSetHoldCity 					#占领城市
		self.__triggers["EVT_ON_TOGGLE_TONG_MONEY_CHANGE"] = self.__onTongMoneyChange 			#帮会可用资金改变
		self.__triggers["EVT_ON_TOGGLE_TONG_SET_SHENSHOU_INFO"] = self.__onSetShenShouInfo 		#帮会神兽
		self.__triggers["EVT_ON_TOGGLE_TONG_LEVEL_CHANGE"]	= self.__onTongLevelChange 			#帮会等级改变通知
		self.__triggers["EVT_ON_POPUP_REMARKBOX"] = self.__onRemarkBoxPop 						#弹出备注设置面板
		self.__triggers["EVT_ON_TOGGLE_TONG_CHANGE_NAME"] = self.__changeToneName
		self.__triggers["EVT_ON_TOGGLE_TONG_SET_VARIABLE_PRESTIAGE"] =  self.__setVariablePrest #额外声望
		self.__triggers["EVT_ON_TOGGLE_TONG_EXP"]	= self.__onUpdateTongExp					#更新帮会经验条
		self.__triggers["EVT_ON_UPDATE_TONG_SINGCOUNT"] = self.__onUpdateTongSignCount			#更新累计签到次数

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	#--------------------------------------------------------------------------------------
	def __onFoundTong( self, npc ):
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		FoundTong.instance().show()

	def __changeToneName( self, npcID ):
		"""
		帮会改名
		"""
		ChangeNameBox( npcID ).show()

	def __setVariablePrest( self, value ):
		"""
		额外声望
		"""
		self.__pyInfoPanel.setVariablePrest( value )
		
	def __onUpdateTongExp( self, exp ):
		self.__pyInfoPanel.updateTongExp( exp )
		
	def __onUpdateTongSignCount( self, totalSignCount ):
		player = BigWorld.player()
		self.__pyBtnSign.enable = not player.tong_dailySignInRecord
		self.__pyInfoPanel.setSignCount( totalSignCount )

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									#删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		player = BigWorld.player()
		gossiptarget = GUIFacade.getGossipTarget()						#获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				#如果NPC离开玩家对话陷阱
			FoundTong.instance().hide()														#隐藏当前窗口
			self.__delTrap()

	def __setMemberInfo( self, familyDBID, familyGrade, memberDBID ):
		if self.__memberItems.has_key( memberDBID ):
			memberInfo = BigWorld.player().tong_memberInfos[memberDBID]
			self.__memberItems[ memberDBID ].setInfo( memberInfo )
		else:
			pyItem = MemberItem( familyDBID, familyGrade, memberDBID, self )
			pyItem.onLClick.bind( self.__onShowDuty )
			online = pyItem.isOnline()
			if online and not pyItem in self.__onlineMembers:
				self.__onlineMembers.append( pyItem )
			self.__pyListPanel.addItem( pyItem )
			self.__memberItems[ memberDBID ] = pyItem
			self.__pyInfoPanel.memberChange()
			selIndex = self.__pyOptionCB.selIndex
			if selIndex == 1 and not online:
				pyItem.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "unknown" )
			pyItem.setOption( selIndex )
#		self.__pyStNum.text = "%i/%i"%( len( self.__onlineMembers ), len( BigWorld.player().tong_memberInfos ) )

	def __updateMemberOnlineState( self, memberDBID, online ):
		pyItem = self.__memberItems.get( memberDBID, None )
		if pyItem is None:return
		pyItem.updateOnlineState( online )
		if pyItem in self.__onlineMembers and not online :
			self.__onlineMembers.remove( pyItem )
			if not self.__pyFilterCK.checked:
				self.__pyListPanel.removeItem( pyItem )
		if not pyItem in self.__onlineMembers and online:
			self.__onlineMembers.append( pyItem )
			self.__pyListPanel.addItem( pyItem )
#		self.__pyStNum.text = "%i/%i"%( len( self.__onlineMembers ), len( BigWorld.player().tong_memberInfos ) )

	def __updateMemberGrade( self, memberDBID, grade ):
		DutyPanel.instance().onUpdateGrade(memberDBID, grade )
		player = BigWorld.player()
		if self.__pyOptionCB.selIndex != 0:return
		pyItem = self.__memberItems.get( memberDBID, None )
		if pyItem is None:return
		pyItem.updateGrade( grade )
		if memberDBID == player.databaseID:
			self.__updateButtonEnable( grade ) # 更新帮会界面按钮的状态

	def __onInitDutyGrade( self, gradeKey, duties ): #初始化职位权限
		if not self.__gradeDuties.has_key( gradeKey ):
			self.__gradeDuties[gradeKey] = duties

	def __onUpdateDutyGrade( self, gradeKey, duties ): # 职位对应权限改变
		player = BigWorld.player()
		grade = player.tong_grade
		if self.__gradeDuties.has_key( gradeKey ):
			oldDuties = self.__gradeDuties[gradeKey]
			self.__updateButtonEnable( grade ) # 更新帮会界面按钮的状态
			self.__gradeDuties[gradeKey] = duties

	def __onContributeChange( self, memberDBID, contribute ):
		if memberDBID == BigWorld.player().databaseID:
			self.__pyInfoPanel.setContribute( contribute )

	def __onTContributeChange( self, memberDBID, totalContribute ):
		if memberDBID == BigWorld.player().databaseID:
			self.__pyInfoPanel.setTotalContribute( totalContribute )

	def __updateMemberFamilyGrade( self, memberDBID, grade ):
		pyItem = self.__memberItems.get( memberDBID, None )
		if pyItem is None:return
		pyItem.updateFamilyGrade( grade )

	def __setTongDismissRemainTime( self, remainTime ):
		"""
		"""
		self.pyMenuItems[5].endTime = remainTime
		self.pyMenuItems[6].endTime = remainTime
		if remainTime > 0:
			self.__remainTime = Time.time() + remainTime
			self.__rTimerID = Timer.addTimer( 0, 1, self.__showRemainTime )
		else:
			self.__remainTime = 0
			Timer.cancel( self.__rTimerID )
			self.__rTimerID = 0
#			self.__pyDismissTip.text = ""

	def __showRemainTime( self ):
		"""
		"""
		if not self.visible:
			return
		leftTime = self.__remainTime - Time.time()
		if leftTime <= 0:
			Timer.cancel( self.__rTimerID )
			self.__rTimerID = 0
			return
		rHour = int( math.ceil( leftTime / 3600.0 ) )
		tipInfo = labelGather.getText( "RelationShip:TongPanel", "disbandTime" )%rHour
		tipInfo = PL_Font.getSource( tipInfo, fc = ( 230, 0, 0, 255 ) )

	def __updateMemberLevel( self, memberDBID, level ):
		pyItem = self.__memberItems.get( memberDBID, None )
		if pyItem is None:return
		pyItem.updateLevel( level )

	def __updateMemberName( self, memberDBID, name ):
		pyItem = self.__memberItems.get( memberDBID, None )
		if pyItem is None:return
		pyItem.updateName( name )

	def __updateMemberSchlium( self, memberDBID, scholium ):
		if self.__pyOptionCB.selIndex != 2:return
		pyItem = self.__memberItems.get( memberDBID, None )
		if pyItem is None:return
		pyItem.updateScholium( scholium )

	def __updateMemberArea( self, memberDBID, spaceType, position, lineNumber ):
		if self.__pyOptionCB.selIndex != 1: return
		pyItem = self.__memberItems.get( memberDBID, None )
		if pyItem is None:return
		pyItem.updateArea( spaceType, position, lineNumber )
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.getArea(), reverse = False, filter = self.filter )

	def __onTongNameChange( self, role, oldName, tongName ):
		if role is not BigWorld.player():return
		self.pyMenuItems[5].tongName = tongName
		self.__pyStTongName.text = tongName
		if oldName != tongName:
			for pyItem in self.__memberItems.itervalues():
				pyItem.updateTongName( tongName )

	def __onUpdateAffiche( self, affiche ):
		if self.__affiche != affiche:
			self.__affiche = rds.wordsProfanity.filterMsg( affiche )
			if AffichePanel.getInstance() and AffichePanel.getInstance().visible:
				AffichePanel.getInstance().hide()

	def __onInitDutyName( self, dutyKey, name ):
		DutyPanel.instance().onInitDutyName(dutyKey, name )
		DutySetting.instance().onInitDutyName( dutyKey, name )
		if self.__pyOptionCB.selIndex != 0:return
		for pyItem in self.__memberItems.itervalues():
				pyItem.updateGradeName( dutyKey, name )

	def __onUpdateDutyName( self, dutyKey, name ):
		DutySetting.instance().onUpdateDutyName(dutyKey, name)
		DutyPanel.instance().onUpdateDutyName(dutyKey, name)
		if self.__pyOptionCB.selIndex != 0:return
		for pyItem in self.__memberItems.itervalues():
				pyItem.updateGradeName( dutyKey, name )

	def __onSetLeague( self ):
		self.__pyInfoPanel.setLeague()

	def __onAddLeague( self, tongDBID ):
		self.__pyInfoPanel.addLeague( tongDBID )
		if LeagueMgr.getInstance() and LeagueMgr.getInstance().visible:
			LeagueMgr.getInstance().hide()

	def __onDelLeague( self, tongDBID ):
		self.__pyInfoPanel.delLeague( tongDBID )
		if LeagueMgr.getInstance() and LeagueMgr.getInstance().visible:
			LeagueMgr.getInstance().hide()

	def __onSetWeekState( self, state ) :
		stateText = WEEKSTATE.get( state, ("","") )[0]
#		self.__pyStWeekState.text = stateText
		self.__pyInfoPanel.setWeekState( state )

	def __onSetPrestige( self, prestige ):
		self.__pyInfoPanel.setPrestige( prestige )

	def __onSetHoldCity( self, role, city ):
		if role.id == BigWorld.player().id :
			self.__pyInfoPanel.setHoldCity( city )

	def __onTongMoneyChange( self, money ):
		if not BigWorld.player().inWorld or not self.visible:
			return
		self.__pyInfoPanel.updateTongFund( money )
		
	def __onSetShenShouInfo( self, shenshouLevel, shenshouType ):
		self.__pyInfoPanel.setTongShenShou( shenshouLevel, shenshouType )

	def __onTongLevelChange( self, level ):
		self.__pyStTongLevel.text = labelGather.getText( "RelationShip:TongPanel", "tongLevel" )%level

	def __onRemarkBoxPop( self, memberID ):
		self.__pyRemarkBox.show( memberID, self )

	def __createPopMenu( self ):
		"""
		创建右键菜单
		"""
		self.__pyNodeMenu = ContextMenu()
		self.__pyNodeMenu.addBinder( self.__pyListPanel )
		self.__pyNodeMenu.onItemClick.bind( self.__onItemClick )
		self.__pyNodeMenu.onBeforePopup.bind( self.__onMenuPopUp )
		self.pyMenuItems[0] = PlayerNameMItem("")
		self.pyMenuItems[1] = SendMessageMItem()
		self.pyMenuItems[2] = InviteFriendMItem()
		self.pyMenuItems[3] = InviteTeamMItem()
		self.pyMenuItems[4] = ChangeToBlackGroupMItem()
		self.pyMenuItems[5] = QuitTongMItem()
		self.pyMenuItems[6] = CancelDismissTongMItem()
		self.pyMenuItems[7] = AbdicationMItem()
		self.pyMenuItems[8] = KickOutMItem()
		self.pyMenuItems[9] = DismissTongMItem()
		self.pyMenuItems[10] = RemarkMItem()
		self.pyMenuItems[11] = CloseMItem()

	def __onMenuPopUp( self ): # 弹出右键菜单
		"""
		菜单弹出时调用
		"""
		pySelItem = self.__pyListPanel.pySelItem 			# 获取鼠标点中的那个item
		if pySelItem is None : return -1					# 返回 -1 表示拒绝显示菜单
		self.__pyNodeMenu.pyItems.clear()
		player = BigWorld.player()
		self.__pyNodeMenu.pyItems.clear()
		for menuItem in self.pyMenuItems.itervalues():
			if menuItem.check( player, pySelItem ):
				self.__pyNodeMenu.pyItems.add( menuItem )
		return True

	def __onItemClick( self, pyItem ):
		player = BigWorld.player()
		pySelItem = self.__pyListPanel.pySelItem
		if pySelItem is None:return
		pyItem.do( player, pySelItem )
		return True

	def __onItemSelected( self, pyItem ):
		self.__pyListPanelSelected = pyItem
		if pyItem is None or not hasattr( BigWorld.player(), "databaseID" ):return
		player = BigWorld.player()
		online = pyItem.isOnline()
		memberDBID = pyItem.getID()

	def __onSortByName( self ):
		flag = self.sortByNameFlag and True or False
		self.__pyListPanel.sort2( key = lambda n: n.getName(), reverse = flag, filter = self.filter )
		self.sortByNameFlag = not self.sortByNameFlag

	def __onSortByLevel( self ):
		flag = self.sortByLevelFlag and True or False
		self.__pyListPanel.sort2( key = lambda n: n.getLevel(), reverse = flag, filter = self.filter )
		self.sortByLevelFlag = not self.sortByLevelFlag

	def __onSortByPro( self ):
		flag = self.sortByMetierFlag and True or False
		self.__pyListPanel.sort2( key = lambda n: n.getMetier(), reverse = flag, filter = self.filter )
		self.sortByMetierFlag = not self.sortByMetierFlag

	def __onOptionChange( self, pyItem ):
		selIndex = self.__pyOptionCB.selIndex
		player = BigWorld.player()
		if selIndex == 0: #职务
			for pyItem in self.__memberItems.itervalues():
				pyItem.setGradeName()
			self.__pyListPanel.sort2( key = lambda pyItem: pyItem.getTongGrade(), reverse = True, filter = self.filter )
#			self.__pyListPanel.sort2( key = lambda pyItem: pyItem.getFamily(), reverse = False )
		elif selIndex == 1: #地区
			if BigWorld.stime() - self.areaQueryTime < 2:
				return
			self.areaQueryTime = BigWorld.stime()
			for pyItem in self.__memberItems.itervalues():
				pyItem.pyCols[3].text =labelGather.getText( "RelationShip:RelationPanel", "unknown" )
			player.base.tong_requestMemberMapInfos()
		elif selIndex ==2: #备注
			for pyItem in self.__memberItems.itervalues():
				pyItem.setScholium()
			self.__pyListPanel.sort2( key = lambda pyItem: pyItem.getScholium(), reverse = False, filter = self.filter )
		elif selIndex ==3: #累计帮贡
			for pyItem in self.__memberItems.itervalues():
				pyItem.setTotalContribute()
			self.__pyListPanel.sort2( key = lambda pyItem:pyItem.getTotalContribute,reverse = False, filter = self.filter )
		elif selIndex ==4: #剩余帮贡
			for pyItem in self.__memberItems.itervalues():
				pyItem.setCurrentContribute()
			self.__pyListPanel.sort2( key = lambda pyItem:pyItem.getContribute,reverse = False, filter = self.filter )
		elif selIndex ==5: #本周获取帮贡
			for pyItem in self.__memberItems.itervalues():
				pyItem.setThisWeekContribute()
			self.__pyListPanel.sort2( key = lambda pyItem:pyItem.getThisWeekContribute,reverse = False, filter = self.filter )
		elif selIndex ==6: #上周获取帮贡
			for pyItem in self.__memberItems.itervalues():
				pyItem.setLastWeekContribute()
			self.__pyListPanel.sort2( key = lambda pyItem:pyItem.getLastWeekContribute,reverse = False, filter = self.filter )

	def __onInviteTeam( self ):
		pySelItem = self.__pyListPanel.pySelItem
		if not pySelItem is None:
			name = pySelItem.getName()
			BigWorld.player().inviteJoinTeam( name )

	def __onMemberMgr( self ):
		MemberMgr.instance().show( self )

	def __onLeagueMgr( self ):
		LeagueMgr.instance().show( self )

	def __onDutySet( self ):
		DutySetting.instance().show( self )

	def __onGradeSet( self ):
		self.__pyGradeSetting.show( self )
		
	def __onFund( self ):
		self.__pyTongFund.show( self )
		
	def __onSign( self ):
		BigWorld.player().tong_requestSignIn()

	def __onSendMsg( self ):
		pySelItem = self.__pyListPanel.pySelItem
		if pySelItem is None:return
		name = pySelItem.getName()
		chatFacade.whisperWithChatWindow( name )

	def __onShowAffiche( self ):
		afficheText = PL_Space.getSource( 2 ) + labelGather.getText( "RelationShip:FamilyPanel", "afficeInfo" )%( PL_NewLine.getSource(), PL_Space.getSource( 2 ), self.__affiche )
		afficheText = PL_Font.getSource( afficheText, fc = ( 230, 227, 185, 255 ) )
		afficheText += PL_Font.getSource( fc = ( 255,255,255,255 ) )
		toolbox.infoTip.showToolTips( self, afficheText )

	def __onShowAfficheWnd( self ):
		player = BigWorld.player()
		if player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHT_AFFICHE ):
			AffichePanel.instance().show( self.__affiche, self )

	def __onHideAffiche( self ):
		toolbox.infoTip.hide()

	def __removeMember( self, memberDBID ):
		if self.__memberItems.has_key( memberDBID ):
			pyItem = self.__memberItems.pop( memberDBID )
			pyItem.onLClick.unbind( self.__onShowDuty )
			self.__pyListPanel.removeItem( pyItem )
			if pyItem in self.__onlineMembers:
				self.__onlineMembers.remove( pyItem )
#		self.__pyStNum.text = "%i/%i"%( len( self.__onlineMembers ), len( BigWorld.player().tong_memberInfos ) )

	def __onAddMember( self ):
		target = BigWorld.player().targetEntity
		if target:
			if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				BigWorld.player().tong_requestJoin( target.id )


	def __onDelMember( self ):
		if self.__pyListPanelSelected:
			dbid = self.__pyListPanelSelected.getID()
			BigWorld.player().tong_kickFamily( dbid )

	def __onShowDuty( self, pyItem ):
		if pyItem is None:return
		if pyItem != self.__pyListPanelSelected:return
		if pyItem.getID() == BigWorld.player().databaseID:return # 自己

		DutyPanel.instance().show( pyItem )

	def __onFilterCheck( self, check ): # 是否显示不在线成员
		if check:
			self.__showAlls()
		else:
			self.__showOnlines()

	def __showAlls( self ):
		self.__pyListPanel.clearItems()
		onlineMembers = []
		offlineMembers = []
		self.__memberItems = {}
		self.__onlineMembers = []
		members = BigWorld.player().tong_memberInfos
		for dbid, member in members.iteritems():
			if member.isOnline():
				onlineMembers.append( member )
			else:
				offlineMembers.append( member )
		# 分开在线与不在线后，按名字排序
		onlineMembers.sort( key = lambda n: n.getGrade(), reverse = True )
		offlineMembers.sort( key = lambda n: n.getGrade(), reverse = True )
		allMembers = onlineMembers + offlineMembers
		index = self.__pyOptionCB.selIndex
		for member in allMembers:
			self.__setMemberInfo( 0, 0, member._memberDBID )
		if index == 1:
			BigWorld.player().base.tong_requestMemberMapInfos()

	def __showOnlines( self ):
		onlineMembers = []
		self.__pyListPanel.clearItems()
		self.__onlineMembers = []
		members = BigWorld.player().tong_memberInfos
		index = self.__pyOptionCB.selIndex
		for dbid, member in members.iteritems():
			if member.isOnline():
				onlineMembers.append( member )
		onlineMembers.sort( key = lambda n: n.getGrade(), reverse = True )
		for member in onlineMembers:
			pyItem = MemberItem( 0, 0, member._memberDBID, self )
			pyItem.onLClick.bind( self.__onShowDuty )
			online = pyItem.isOnline()
			if self.__memberItems.has_key( member._memberDBID ):
				self.__memberItems[member._memberDBID] = pyItem
			if online and not pyItem in self.__onlineMembers:
				self.__onlineMembers.append( pyItem )
			self.__pyListPanel.addItem( pyItem )
			selIndex = self.__pyOptionCB.selIndex
			if selIndex == 1 and not online:
				pyItem.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "unknown" )
			pyItem.setOption( selIndex )
#		self.__pyStNum.text = "%i/%i"%( len( self.__onlineMembers ), len( BigWorld.player().tong_memberInfos ) )

		if index == 1:
			BigWorld.player().base.tong_requestMemberMapInfos()
	
	def __updateButtonEnable( self, grade ): # 更新帮会界面按钮的状态
		player = BigWorld.player()
		self.__pyBtnLeagueMgr.enable = grade == csdefine.TONG_DUTY_CHIEF #同盟管理
		# 添加和开除成员权限改为一致
		consGrade = kickMemberGrade = player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHT_MEMBER_MANAGE )
		self.__pyBtnMemberMgr.enable = consGrade
		self.__pyBtnGradeSet.enable = grade 							#权限查询
		self.__pyBtnDutySet.enable = grade == csdefine.TONG_DUTY_CHIEF	#更改职位名称
		

	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
	
	def filter( self, items ):
		filterItem = items
		item1 = [item for item in filterItem if item.isOnline()]
		item2 = [item for item in filterItem if not item.isOnline()]
		return [item1,item2]
		
	def reset( self ) :
		if not self.__rTimerID is None:
			Timer.cancel( self.__rTimerID )
		self.__rTimerID = 0
#		self.__pyDismissTip.text = ""
		self.__pyStTongName.text = ""
#		self.__pyStNum.text = ""
		self.areaQueryTime = 0
		self.__pyListPanel.clearItems()
		self.__memberItems = {}
		self.__onlineMembers = []
		self.__pyFilterCK.checked = True
		self.__pyInfoPanel.reset()
		if DutyPanel.getInstance() and DutyPanel.getInstance().visible:
			DutyPanel.getInstance().hide()

	def cancelTimer( self ):
		self.__pyInfoPanel.reset()

	def setTongMemberInfo( self, familyDBID, familyGrade, memberDBID ):
		self.__setMemberInfo( familyDBID, familyGrade, memberDBID )

	def initUIs( self ):
		player = BigWorld.player()
		grade = player.tong_grade
		self.__pyStTongName.text = player.tongName
		self.__pyStTongLevel.text = labelGather.getText( "RelationShip:TongPanel", "tongLevel" )%player.tongLevel
		self.__pyInfoPanel.setTongInfo()
		self.__pyOptionCB.selIndex = 0
		self.__onFilterCheck( self.__pyFilterCK.checked )
		player.cell.tong_onClientOpenTongWindow()
		BigWorld.callback( 3.0, Functor ( self.__updateButtonEnable, grade ) )# 更新帮会界面按钮的状态
		self.__pyBtnSign.enable = not player.tong_dailySignInRecord
#		totalSignCount = player.tong_totalSignInRecord
#		self.__pyStSignCount.text = labelGather.getText( "RelationShip:TongPanel", "stSignCount" ) % totalSignCount
		player.base.requestTongExp()

	def getMembers( self ):
		return self.__memberItems.values()

# --------------------------------------------------------------------------
class MemberItem( MultiColListItem ):
	__cc_item = None

	def __init__( self, familyDBID, familyGrade, memberDBID, pyBinder ):
		if MemberItem.__cc_item is None :
			MemberItem.__cc_item = GUI.load( "guis/general/relationwindow/familypanel/familyitem.gui" )
		item = util.copyGuiTree( MemberItem.__cc_item )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item, pyBinder )
		self._familyDBID = familyDBID 	# 家族编号
		self._memberDBID = memberDBID
		info =  BigWorld.player().tong_memberInfos[memberDBID]
		self._online = info.isOnline()
		self._area = None

		self.setInfo( info )

	def setInfo( self, memberInfo ):
		name = memberInfo.getName()
		level = memberInfo.getLevel()
		metier = memberInfo.getClass()&csdefine.RCMASK_CLASS
		metierText = csconst.g_chs_class[metier]
		self.setTextes( name, str( level ), metierText, '' ) # 名称,职业
		self.updateOnlineState( self._online )

	def updateLevel( self, level ):
		"""
		成员等级
		"""
		self.pyCols[1].text = str( level )

	def updateName( self, name ):
		"""
		成员名字
		"""
		self.pyCols[0].text = str( name )

	def updateScholium( self, scholium ):
		if scholium == "":
			self.pyCols[3].text = labelGather.getText( "RelationShip:TongPanel", "noRamark" )
		else:
			self.pyCols[3].text = scholium

	def updateOnlineState( self, online ):
		"""
		更新在线状态
		"""
		self._online = online
		if online:
			self.commonForeColor = 255,255,255,255
		else:
			self.commonForeColor = 127,127,127,255
			self._area = ""

	def updateTongName( self, tongName ):
		self.pyCols[3].text = tongName

	def updateArea( self, spaceType, position, lineNumber ): #地区
		if spaceType.startswith("fu_ben") and spaceType not in Const.CC_FUBENNAME_DONOT_CONVERT_LIST:
			self._area = labelGather.getText( "RelationShip:RelationPanel", "spaceCopy" )
			self.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "spaceCopy" )
			return
		area = rds.mapMgr.getArea( spaceType, position )
		areaStr = lineNumber and labelGather.getText( "RelationShip:RelationPanel", "lineNumber" )%(area.name,lineNumber) or area.name
		self._area = areaStr
		self.pyCols[3].text = areaStr

	def updateGradeName( self, dutyKey, name ):
		duty = BigWorld.player().tong_memberInfos[self._memberDBID].getGrade()
		if dutyKey == duty:
			self.pyCols[3].text = name
		
	def getFamilyDBID( self ):
		return self._familyDBID

	def getID( self ):
		return self._memberDBID

	def isOnline( self ):
		return self._online

	def getName( self ):
		return self.pyCols[0].text

	def getLevel( self ):
		return int( self.pyCols[1].text )

	def getMetier( self ):
		return self.pyCols[2].text

	def getArea( self ):
		return self._area

	def getFamily( self ):
		return BigWorld.player().tong_familys[self._familyDBID]

	def getTong( self ):
		"""
		帮会名字
		"""
		return BigWorld.player().tong_memberInfos[self._memberDBID].getName()

	def getContribute( self ):
		"""
		贡献度
		"""
		return BigWorld.player().tong_memberInfos[self._memberDBID].getContribute()

	def getTotalContribute( self ):
		"""
		总贡献度
		"""
		return BigWorld.player().tong_memberInfos[self._memberDBID].getTotalContribute()
		
	def getThisWeekContribute( self ):
		"""
		本周获取帮贡
		"""
		return BigWorld.player().tong_memberInfos[self._memberDBID].getWeekTongContribute()	
		
	def getLastWeekContribute( self ):
		"""
		上周获取帮贡
		"""
		return BigWorld.player().tong_memberInfos[self._memberDBID].getLastWeekTotalContribute()	

	def updateFamilyName( self, familyDBID ):
		familyName = ""
		self.pyCols[3].text = familyName

	def updateGrade( self, grade ):
		if BigWorld.player().tong_dutyNames.has_key( grade ):
			gradeName = BigWorld.player().tong_dutyNames[grade]
			self.pyCols[3].text = gradeName

	def setScholium( self ):
		scholium = self.getScholium()
		if scholium == "":
			self.pyCols[3].text = labelGather.getText( "RelationShip:TongPanel", "noRamark" )
		else:
			self.pyCols[3].text = scholium

	def setTongName( self ):
		self.pyCols[3].text = BigWorld.player().tongName


	def setGradeName( self ):
		player = BigWorld.player()
		tongGrade = player.tong_memberInfos[self._memberDBID].getGrade()
		self.pyCols[3].text = player.tong_dutyNames[tongGrade]
	
	def setTotalContribute( self ):
		totalContribute = self.getTotalContribute()
		self.pyCols[3].text = totalContribute
		
	def setCurrentContribute( self ):
		currentContribute = self.getContribute()
		self.pyCols[3].text = currentContribute
		
	def setThisWeekContribute( self ):
		thisWeekContribute = self.getThisWeekContribute()
		self.pyCols[3].text = thisWeekContribute
		
	def setLastWeekContribute( self ):
		lastWeekContribute = self.getLastWeekContribute()
		self.pyCols[3].text = lastWeekContribute
		
	def setOption( self, index ):
		if self.isOnline:
			if index == 0:
				self.setGradeName()
			elif index == 1:
				BigWorld.player().base.tong_requestMemberMapInfos()
			elif index == 2:
				self.setScholium()
			elif index == 3:
				self.setTotalContribute()
			elif index == 4:
				self.setCurrentContribute()
			elif index == 5:
				self.setThisWeekContribute()
			elif index == 6:
				self.setLastWeekContribute()
		else:
			self.pyCols[3].text = "--"

	def getGradeName( self ):
		player = BigWorld.player()
		tongGrade = player.tong_memberInfos[self._memberDBID].getGrade()
		return player.tong_dutyNames[tongGrade]

	def getScholium( self ):
		return BigWorld.player().tong_memberInfos[self._memberDBID].getScholium()

	def getTongGrade( self ):
		return BigWorld.player().tong_memberInfos[self._memberDBID].getGrade()
