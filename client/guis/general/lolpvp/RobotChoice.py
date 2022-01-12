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
from guis.controls.ODListPanel import ODListPanel
from RobotItem import RobotItem
from RobotRender import RobotRender
from RobotInfosLoader import robotInfosLoader
import csdefine
import csconst
import GUIFacade

class RobotChoice( Window ):
	"""
	机器人选择界面
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/lolpvp/choicewnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__trapID = 0
		self.__pyMsgBox = None
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__teamPanels = {}
		for name, child in wnd.children:
			if name.startswith( "teamPanel_" ):
				index = int( name.split( "_" )[1] )							#index 为0则为玩家队伍，1为随机机器人队伍
				pyTeamPanel = TeamPanel( index, child )
				self.__teamPanels[index] = pyTeamPanel
			if name.startswith( "tmText_" ):
				pyStTmTitle = StaticText( child )
				labelGather.setPyLabel( pyStTmTitle, "LolPVP:main", name )
		
		self.__pyBtnEnter = HButtonEx( wnd.btnEnter )
		self.__pyBtnEnter.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnEnter.onLClick.bind( self.__onEnter )
		labelGather.setPyBgLabel( self.__pyBtnEnter, "LolPVP:main", "btnEnter" )
		
		self.__pyBtnCancel = HButtonEx( wnd.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "LolPVP:main", "btnCancel" )
		
		labelGather.setPyLabel( self.pyLbTitle_, "LolPVP:main", "lbTitle" )
	
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
			self.hide()														#隐藏当前与NPC对话窗口
			self.__delTrap()
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_ROBOT_CHOICE_WND"] = self.__onWndShow
		self.__triggers["EVT_ON_ADD_PVE_ROBOT"] = self.__onAddRobot
		self.__triggers["EVT_ON_REMOVE_PVE_ROBOT"] = self.__onRemoveRobot
		self.__triggers["EVT_ON_UPDATE_PVE_ROBOT"] = self.__onUpdateRobot
		self.__triggers["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onMemberJoinIn
		self.__triggers["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onMemberLeft
		self.__triggers["EVT_ON_SHOW_YXLMCOPY_MINIMAP"] = self.__onHideWnd
		self.__triggers["EVT_ON_SET_PVE_ROBOTS"] = self.__onSetRobots
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )
	# ------------------------------------------------------------
	def __onWndShow( self, rbtClassNames ):
		player = BigWorld.player()
		members = player.teamMember
		self.__clearItems()
		for objectID, member in members.items():
			robot = None
			if objectID == player.id:
				robot = Robot( objectID, player.getName(), player.getClass(), player.level, \
				player.getHP(), player.getHPMax(), player.getMP(), player.getMPMax(), player.getHeadTexture(), False )
			else:
				robot = Robot( objectID, member.name, member.raceclass, member.level, \
				member.hp, member.hpMax, member.mp, member.mpMax, member.header, False )
			if robot is None:continue
			self.__teamPanels[0].addMember( robot )
		for rbtClassName in rbtClassNames:
			if rbtClassName in player.baoZangRobotInfos:
				rbtInfo = player.baoZangRobotInfos[rbtClassName]
				header = ""
				rbtUIInfo = robotInfosLoader.getRobotInfo( rbtClassName )
				if rbtUIInfo:
					header = rbtUIInfo.header
				robot = Robot( rbtClassName, rbtInfo["robotName"], rbtInfo["robotClass"], rbtInfo["level"], \
				rbtInfo["hp_max"], rbtInfo["hp_max"], 0, 0, header, True )
				self.__teamPanels[1].addRobot( robot )
		for pyTeamPanel in self.__teamPanels.values():
			pyTeamPanel.setAddBtnState()
		self.show()
		self.__addTrap()
	
	def __onAddRobot( self, teamNumber, rbtInfo ):
		"""
		增加机器人
		"""
		pyTeamPanel = self.__teamPanels.get( teamNumber )
		if pyTeamPanel is None:return
		rbtCls = self.__getRbtCls()
		rbtClassName = rbtInfo.className
		if rbtClassName in rbtCls:
			self.__showMessage( 0x1001 )
			return
		rbtCls += [rbtClassName]
		BigWorld.player().baoZangPVESetRobot( rbtCls )
	
	def __onRemoveRobot( self, teamNumber, index ):
		"""
		删除机器人
		"""
		pyTeamPanel = self.__teamPanels.get( teamNumber )
		if pyTeamPanel is None:return
		rbtCls = self.__getRbtCls()
		rbtCls.pop( index )
		BigWorld.player().baoZangPVESetRobot( rbtCls )
	
	def __onUpdateRobot( self, teamNumber, index, rbtInfo ):
		"""
		更新机器人
		"""
		pyTeamPanel = self.__teamPanels.get( teamNumber )
		if pyTeamPanel is None:return
		rbtCls = self.__getRbtCls()
		rbtClassName = rbtInfo.className
		if rbtClassName in rbtCls:
			self.__showMessage( 0x1001 )
			return
		rbtCls.pop( index )
		rbtCls.insert( index, rbtInfo.className )
		BigWorld.player().baoZangPVESetRobot( rbtCls )
	
	def __onMemberJoinIn( self, joinor ):
		"""
		玩家进队
		"""
		if not self.visible:return
		objectID = joinor.objectID
		player = BigWorld.entities.get( objectID )
		robot = None
		if player:
			robot = Robot( objectID, player.getName(), player.getClass(), player.level, \
			player.getHP(), player.getHPMax(), player.getMP(), player.getMPMax(), player.getHeadTexture(), False )
		else:
			robot = Robot( joinor.objectID, joinor.name, joinor.raceclass, joinor.level, \
					joinor.hp, joinor.hpMax, joinor.mp, joinor.mpMax, joinor.header, False )
		if robot is None:return
		self.__teamPanels[0].addMember( robot )
	
	def __onMemberLeft( self, objectID ):
		"""
		队员离队
		"""
		self.__teamPanels[0].removeMember( objectID )
	
	def __onEnter( self ):
		"""
		进入副本
		"""
		player = BigWorld.player()
		rbtClsNames = []
		for teamPanel in self.__teamPanels.values():
			robots = teamPanel.getRobots()
			rbtClsNames += [robot.objectID for robot in robots]
		player.baoZangOnReqPVE( rbtClsNames )

	def __onCancel( self ):
		"""
		取消
		"""
		self.hide()
	
	def __onHideWnd( self, spaceLabel ):
		"""
		隐藏界面
		"""
		self.__clearItems()
		self.hide()
		self.__delTrap()
	
	def __onSetRobots( self, rbtCls ):
		"""
		队员设置机器人
		"""
		self.__teamPanels[0].clearRbtItems()
		player = BigWorld.player()
		for rbtCl in rbtCls:
			if rbtCl in player.baoZangRobotInfos:
				rbtInfo = player.baoZangRobotInfos[rbtCl]
				header = ""
				rbtUIInfo = robotInfosLoader.getRobotInfo( rbtCl )
				if rbtUIInfo:
					header = rbtUIInfo.header
				robot = Robot( rbtCl, rbtInfo["robotName"], rbtInfo["robotClass"], rbtInfo["level"], \
				rbtInfo["hp_max"], rbtInfo["hp_max"], 0, 0, header, True )
				self.__teamPanels[0].addRobot( robot )
	
	def __clearItems( self ):
		 for teamPanel in self.__teamPanels.values():
		 	 teamPanel.clearItems()
	
	def __getRbtCls( self ):
		robots = self.__teamPanels[0].getRobots()
		rbtCls = [robot.objectID for robot in robots]
		return rbtCls

	def __showMessage( self, msg, style = MB_OK, cb = None ) :
		"""
		弹出提示框，同时只能弹出一个
		"""
		def callback( res ) :
			self.__pyMsgBox = None
			if callable( cb ) :
				cb( res )
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", style, callback, self )
		
	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.__clearItems()
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		Window.hide( self )

# -----------------------------------------------------------------------------------------------------
class TeamPanel( PyGUI ):
	"""
	队伍面板
	"""
	_cc_max_count = 5
	
	def __init__( self, index, panel ):
		PyGUI.__init__( self, panel )
		self.teamNumber = index
		self.__pyListPanel = ODListPanel( panel.listPanel, panel.listBar )
		self.__pyListPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.autoSelect = True
		self.__pyListPanel.itemHeight = 65.0
		self.__pyListPanel.onItemSelectChanged.bind( self.__onItemSlected )
		
		self.__pyBtnAdd = Button( panel.btnAdd )
		self.__pyBtnAdd.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnAdd.onLClick.bind( self.__onAdd )

	def __initListItem( self, pyViewItem ) :
		index = pyViewItem.itemIndex
		robotInfo = pyViewItem.listItem
		item = GUI.load( "guis/general/lolpvp/rbtitem.gui" )
		if robotInfo.isRobot:
			item = GUI.load( "guis/general/lolpvp/isrbtitem.gui" )
		uiFixer.firstLoadFix( item )
		pyRobot = RobotItem( item, self, index )
		pyViewItem.addPyChild( pyRobot )
		pyViewItem.crossFocus = False
		pyRobot.pos = -1.0, 1
		pyViewItem.pyItem = pyRobot

	def __drawListItem( self, pyViewItem ) :
		pyRobot = pyViewItem.pyItem
		robotInfo = pyViewItem.listItem
		pyRobot.updateInfo( robotInfo )

	def __onItemSlected( self, index ):
		"""
		选取某个机器人
		"""
		if index < 0:return
		selRobot = self.__pyListPanel.selItem
		if selRobot is None:return
	
	def __onAdd( self ):
		"""
		弹出机器人属性界面
		"""
		robotPro = rds.ruisMgr.robotProperty
		robotPro.show( self.teamNumber, -1, self.pyTopParent )
	
	def addRobot( self, robot ):
		"""
		增加一个机器人
		"""
		if self.__pyListPanel.itemCount >= self._cc_max_count:
			return
		if not robot in self.__pyListPanel.items:
			self.__pyListPanel.addItem( robot )
		self.__setAddBtnState()
	
	def removeRobot( self, index ):
		"""
		删除机器人
		"""
		if index <0 or index > self.__pyListPanel.itemCount:
			return
		robot = self.__pyListPanel.items[index]
		self.__pyListPanel.removeItem( robot )
		self.__setAddBtnState()
	
	def addMember( self, member ):
		"""
		添加一个成员
		"""
		if self.__pyListPanel.itemCount >= self._cc_max_count:
			return
		if member.isRobot:return
		if not member.objectID in [item.objectID for item in self.__pyListPanel.items if not item.isRobot]:
			self.__pyListPanel.addItem( member )
		self.__setAddBtnState()
	
	def removeMember( self, objectID ):
		"""
		删除一个队友
		"""
		for robot in self.__pyListPanel.items:
			if robot.objectID == objectID:
				self.__pyListPanel.removeItem( robot )
		self.__setAddBtnState()

	def updateRobot( self, index, newRbt ):
		"""
		修改一个机器人
		"""
		if index <0 or index > self.__pyListPanel.itemCount:
			return
		self.__pyListPanel.updateItem( index, newRbt )
		self.__setAddBtnState()
	
	def clearItems( self ):
		"""
		清空面板
		"""
		self.__pyListPanel.clearItems()
	
	def clearRbtItems( self ):
		"""
		清空机器人
		"""
		for robot in self.__pyListPanel.items:
			if robot.isRobot:
				self.__pyListPanel.removeItem( robot )
	
	def __setAddBtnState( self ):
		"""
		设置+按钮状态
		"""
		isCaptain = BigWorld.player().isCaptain()
		self.__pyBtnAdd.visible = self.__pyListPanel.itemCount < 5 and isCaptain
		self.__pyBtnAdd.top = ( self.__pyListPanel.itemCount + 1 )*60
	
	def setAddBtnState( self ):
		self.__setAddBtnState()
	
	def getRobots( self ):
		"""
		获取机器人
		"""
		robots = []
		for item in self.__pyListPanel.items:
			if item.isRobot:
				robots.append( item )
		return robots
		
class Robot:
	"""
	机器人数据
	"""
	def __init__( self, objectID, name, raceclass, level, hp, hpMax, mp, mpMax, header, isRobot ):
		self.objectID = objectID
		self.name = name
		self.raceclass = raceclass
		self.level = level
		self.hp = hp
		self.hpMax = hpMax
		self.mp = mp
		self.mpMax = mpMax
		self.header = header
		self.isRobot = isRobot