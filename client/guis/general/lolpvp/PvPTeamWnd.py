# -*- coding: gb18030 -*-
#
# $Id: EspialWindow.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.RichText import RichText
from guis.controls.ODListPanel import ODListPanel
from RobotChoice import Robot
from RobotItem import RobotItem
import csdefine
import GUIFacade
import Timer
import csconst

class PvPTeamWnd( Window ):
	"""
	组队pvp界面
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/lolpvp/pvpteam.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__timeCBID = 0
		self.__readyTime = 0
		self.__enterTime = 0
		self.__isTeamReady = False
		self.__trapID = 0
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__teamPanels = {}
		for name, child in wnd.children:
			if name.startswith( "teamPanel_" ):
				index = int( name.split( "_" )[1] )							#index 为0则为玩家队伍，1为随机机器人队伍
				pyTeamPanel = ODListPanel( child.listPanel, child.listBar )
				pyTeamPanel.index = index
				pyTeamPanel.onViewItemInitialized.bind( self.__initListItem )
				pyTeamPanel.onDrawItem.bind( self.__drawListItem )
				pyTeamPanel.ownerDraw = True
				pyTeamPanel.autoSelect = True
				pyTeamPanel.itemHeight = 65.0
				pyTeamPanel.onItemSelectChanged.bind( self.__onItemSlected )
				self.__teamPanels[index] = pyTeamPanel
			if name.startswith( "tmText_" ):
				pyStTmTitle = StaticText( child )
				labelGather.setPyLabel( pyStTmTitle, "LolPVP:main", name )
		
		self.__pyRtWarning = RichText( wnd.rtWarning )
		self.__pyRtWarning.align = "C"
		self.__pyRtWarning.text = ""
		self.__pyRtWarning.visible = True
		
		labelGather.setPyLabel( self.pyLbTitle_, "LolPVP:PvPTeamWnd", "lbTitle" )
	
	def __addTrap( self ):
		if self.__trapID:
			self.__delTrap()

		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()  + 0.5	# +0.5 避免陷阱大小和对话距离相等而导致在陷阱边缘对话时对话框会一闪消失的问题。
		self.__trapID = player.addTrapExt( distance, self.__onEntitiesTrapThrough )		#打开窗口后为玩家添加对话陷阱s

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )											#删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()									#获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:						#如果NPC离开玩家对话陷阱
			self.__onCloseWnd()														#隐藏当前与NPC对话窗口
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PVP_TEAM_TOGGLE_WND"] = self.__onWndShow
		self.__triggers["EVT_ON_PVP_TEAM_CLOSE_WND"]	=  self.__onCloseWnd
#		self.__triggers["EVT_ON_PVP_TEAM_ENTER_COUNT_DOWN"]	=  self.__onEnterContDown
#		self.__triggers["EVT_ON_TOGGLE_PVP_ADD_MEMBER"] = self.__onAddMember
#		self.__triggers["EVT_ON_TOGGLE_PVP_REMOVE_MEMBER"] = self.__onRemoveMember
#		self.__triggers["EVT_ON_TOGGLE_PVP_REMOVE_MEMBER"] = self.__onRemoveMember
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )
	# -----------------------------------------------------------------
	def __initListItem( self, pyViewItem ) :
		pyPanel = pyViewItem.pyPanel
		item = GUI.load( "guis/general/lolpvp/rbtitem.gui" )
		uiFixer.firstLoadFix( item )
		pyMember = RobotItem( item, pyPanel )
		pyViewItem.addPyChild( pyMember )
		pyViewItem.crossFocus = False
		pyMember.pos = -1.0, 1
		pyViewItem.pyItem = pyMember

	def __drawListItem( self, pyViewItem ) :
		pyMember = pyViewItem.pyItem
		memberInfo = pyViewItem.listItem
		pyMember.updateInfo( memberInfo )
	
	def __onItemSlected( self, selIndex ):
		if selIndex < 0:return
		
	def __onWndShow( self, memberIds, countDown, isReady ):
		"""
		显示
		"""
		if self.__timeCBID > 0:
			Timer.cancel( self.__timeCBID )
			self.__timeCBID = 0
		if isReady:
			self.__isTeamReady = isReady
			self.__setTeamMembers( memberIds )
			self.__readyTime = countDown
			self.__timeCBID = Timer.addTimer( 0, 1, self.__countdownReady )
			self.show()
		elif self.__isTeamReady:						#自己的队伍已经准备好了，更新对方队伍的
			self.__setTeamMembers( memberIds )
			self.__readyTime = countDown
			self.__timeCBID = Timer.addTimer( 0, 1, self.__countdownReady )
			if not self.visible:
				self.show()
		self.__addTrap()
		
	def __setTeamMembers( self, memberIds ):
		self.__clearItems()
		player = BigWorld.player()
		members = player.teamMember
		for objectID, member in members.items():
			robot = None
			if objectID == player.id:
				robot = Robot( objectID, player.getName(), player.getClass(), player.level, \
				player.getHP(), player.getHPMax(), player.getMP(), player.getMPMax(), player.getHeadTexture(), False )
			else:
				robot = Robot( objectID, member.name, member.raceclass, member.level, \
				member.hp, member.hpMax, member.mp, member.mpMax, member.header, False )
			if robot is None:continue
			self.__teamPanels[0].addItem( robot )
		for memberId in memberIds:
			member = BigWorld.entities.get( memberId )
			if member is None:continue
			robot = Robot( objectID, member.getName(), member.getClass(), member.level, \
			member.getHP(), member.getHPMax(), member.getMP(), member.getMPMax(), member.getHeadTexture(), False )
			self.__teamPanels[1].addItem( robot )

	def __countdownReady( self ):
		self.__readyTime -= 1.0
		if self.__readyTime > 0:
			self.__pyRtWarning.text = labelGather.getText( "LolPVP:PvPTeamWnd", "pleaseWait" )%self.__readyTime
		else:
			self.__onCloseWnd()
	
	def __countdownEnter( self ):
		self.__enterTime -= 1.0
		if self.__enterTime > 0:
			self.__pyRtWarning.text = labelGather.getText( "LolPVP:PvPTeamWnd", "countDown" )%self.__enterTime
		else:
			self.__onCloseWnd()
	
	def __onCloseWnd( self ):
		"""
		关闭窗口
		"""
		for teamPanel in self.__teamPanels.values():
			teamPanel.clearItems()
		Timer.cancel( self.__timeCBID )
		self.__timeCBID = 0
		self.__isTeamReady = False
		self.hide()
		self.__delTrap()
	
	def __onAddMember( self, member ):
		"""
		增加成员
		"""
		objectID = member.objectID
		teamID = member.teamID
		teamIndex = self.__getTeamIndex( teamID )
		pyTeamPanel = self.__teamPanels.get( teamIndex )
		if pyTeamPanel is None:return
		if not objectID in [item.objectID for item in pyTeamPanel.items]:
			robot = Robot( member.objectID, member.name, member.raceclass, member.level, \
			member.hp, member.hpMax, member.mp, member.mpMax, member.header, False )
			pyTeamPanel.addItem( robot )
	
	def __onRemoveMember( self, member ):
		"""
		移除成员
		"""
		objectID = member.objectID
		teamID = member.teamID
		teamIndex = self.__getTeamIndex( teamID )
		pyTeamPanel = self.__teamPanels.get( teamIndex )
	
	def __getTeamIndex( self, teamID ):
		"""
		获取队伍索引
		"""
		for index, pyTeamPanel in self.__teamPanels.items():
			if pyTeamPanel.itemCount <= 0:
				return index
	
	def __clearItems( self ):
		"""
		清空队伍列表
		"""
		for teamPanel in self.__teamPanels.values():
			teamPanel.clearItems()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.__onCloseWnd()

	def show( self ):
		Window.show( self )

	def hide( self ):
		Window.hide( self )