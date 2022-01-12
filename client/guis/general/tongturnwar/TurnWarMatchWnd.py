#-*- coding: gb18030 -*-

import GUI
import BigWorld
from guis import UIState
from guis.UIFixer import uiFixer
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from event import EventCenter as ECenter
from LabelGather import labelGather
from guis.common.FrameEx import HVFrameEx
from guis.common.FlexExWindow import HVFlexExWindow


class TurnWarMatchWnd( HVFlexExWindow ):
	_INTERVAL = 25

	def __init__( self ):
		wnd = GUI.load("guis/general/tongturnwar/wnd.gui")
		uiFixer.firstLoadFix(wnd)
		HVFlexExWindow.__init__( self, wnd )
		self._pyTeammates = []
		self._pyOpponents = []
		self._triggers = {}
		self.__initialize(wnd)
		self.__registerTriggers()
		

	def __initialize( self, wnd ):
		self.__memberPanel = HVFrameEx( wnd.frame_member )
		self.__memberPanel.h_dockStyle = "HFILL"
		self.__memberPanel.v_dockStyle = "VFILL"
		self.__enemyPanel = HVFrameEx( wnd.frame_enemy )
		self.__enemyPanel.h_dockStyle = "HFILL"
		self.__enemyPanel.v_dockStyle = "VFILL"
		
		# ui文本
		labelGather.setLabel( wnd.lbTitle, "tongturnwar:main", "lbTitle" )
		labelGather.setLabel( wnd.frame_enemy.bgTitle.stTitle, "tongturnwar:main", "stTitle_enemy" )
		labelGather.setLabel( wnd.frame_member.bgTitle.stTitle, "tongturnwar:main", "stTitle_member" )

	def __registerTriggers( self ):
		self._triggers["EVT_ON_TURNWAR_RECEIVE_SELF_MEMBERS"] = self.__onReceiveSelfMembers
		self._triggers["EVT_ON_TURNWAR_RECEIVE_ENEMY_MEMBERS"] = self.__onReceiveEnemyMembers
		self._triggers["EVT_ON_TURNWAR_UPDATE_WARRIOR_STATE"] = self.__onUpdateWarriorState
		self._triggers["EVT_ON_TURNWAR_SIGN_UP"] = self.__onSignUp
		self._triggers["EVT_ON_TURNWAR_HIDE_WINDOW"] = self.hide
		for evt in self._triggers.iterkeys():
			ECenter.registerEvent( evt, self )

	def __onSignUp( self ):
		for pyItem in self._pyTeammates + self._pyOpponents:
			pyItem.update({})
		self.show()

	def __onReceiveSelfMembers( self, members ):
		self._pyTeammates = self.__addWarriors( self.__memberPanel, members )
		self.__reSize()
		self.show()

	def __onReceiveEnemyMembers( self, members ):
		self._pyOpponents = self.__addWarriors( self.__enemyPanel, members )
		self.__reSize()
		self.show()

	def __onUpdateWarriorState( self, name, state ):
		"""更新挑战者的状态"""
		for pyItem in self._pyTeammates + self._pyOpponents:
			if pyItem.name == name:
				pyItem.updateState(state)
				break
				
	def __addWarriors( self, pyPanel, warriors ):
		"""
		往某个面板添加孩子
		"""
		for name, child in pyPanel.gui.children:
			if name != "bgTitle":
				pyPanel.gui.delChild(child)
		pyWarriors = []
		for index, warrior in enumerate( warriors ):
			pyW = WarriorItem()
			pyW.update(warrior)
			pyPanel.addPyChild(pyW)
			pyW.top = 20
			pyW.left = self._INTERVAL + (pyW.width + self._INTERVAL) * index
			pyWarriors.append( pyW )
		return pyWarriors

	def __reSize( self ):
		"""调整窗口到合适宽度"""
		item_width = 0
		if self._pyOpponents:
			item_width = self._pyOpponents[0].width + self._INTERVAL
		elif self._pyTeammates:
			item_width = self._pyTeammates[0].width + self._INTERVAL
		item_col = max(2, len(self._pyTeammates), len(self._pyOpponents))
		self.width = 100 + item_width * item_col
		
	def onEvent( self, evtMacro, *args ):
		self._triggers[evtMacro](*args)

	def onLeaveWorld( self ):
		self.hide()
	
	def hide( self ):
		self.clearPanels()
		self._pyTeammates = []
		self._pyOpponents = []
		HVFlexExWindow.hide( self )
	
	def clearPanels( self ):
		for name, child in self.__memberPanel.gui.children:
			if name != "bgTitle":
				self.__memberPanel.gui.delChild(child)
		for name, child in self.__enemyPanel.gui.children:
			if name != "bgTitle":
				self.__enemyPanel.gui.delChild(child)

class WarriorItem( GUIBaseObject ):

	def __init__( self ):
		guiObj = GUI.load( "guis/general/tongturnwar/warrior.gui" )
		uiFixer.firstLoadFix(guiObj)
		GUIBaseObject.__init__( self, guiObj )
		self._btnFlash_cbid = 0
		self._alpha_shader = GUI.AlphaShader()
		self._alpha_shader.speed = 0.3
		self.__initialize(guiObj)

	def __initialize( self, guiObj ):
		# 出战顺序
		self._pyOrder = StaticText(guiObj.st_order)
		# 玩家名字
		self._pyName = StaticText(guiObj.st_name)
		# 玩家头像
		self._pyIcon = GUIBaseObject(guiObj.head_icon)
		# 准备按钮
		self._pyBtnPrepare = HButtonEx(guiObj.btn_ready)
		self._pyBtnPrepare.setExStatesMapping(UIState.MODE_R4C1)
		self._pyBtnPrepare.onLClick.bind( self.__onPrepareBtnClicked )
		self._pyBtnPrepare.gui.addShader(self._alpha_shader)
		labelGather.setPyBgLabel( self._pyBtnPrepare, "tongturnwar:main", "lbText_prepare" )
		# 出战按钮
		self._pyBtnFight = HButtonEx(guiObj.btn_fight)
		self._pyBtnFight.setExStatesMapping(UIState.MODE_R4C1)
		self._pyBtnFight.onLClick.bind( self.__onFightBtnClicked )
		self._pyBtnFight.gui.addShader(self._alpha_shader)
		labelGather.setPyBgLabel( self._pyBtnFight, "tongturnwar:main", "lbText_fighting" )

	def __onPrepareBtnClicked( self ):
		player = BigWorld.player()
		if player.campTurnWar_isSignUp:
			player.campTurnWar_onPrepared()
		else:
			player.turnWar_onPrepared()
		self.__stopFlashing()

	def __onFightBtnClicked( self ):
		player = BigWorld.player()
		if player.campTurnWar_isSignUp:
			BigWorld.player().cell.campTurnWar_onEnterSpace()
		else:
			BigWorld.player().cell.turnWar_onEnterSpace()
		self.__stopFlashing()
		self.pyTopParent.hide()

	def update( self, info ):
		self._pyName.text = info.get("name", "")
		self._pyOrder.text = info.get("order", "")
		self._pyIcon.texture = info.get("headIcon", "")
		self.__enableButtons(info.get("state", "other_preparing"))

	def updateState( self, state ):
		"""更新状态"""
		self.__enableButtons( state )

	def __enableButtons( self, state ):
		if state == "own_preparing":
			self._pyBtnFight.visible = False
			self._pyBtnPrepare.visible = True
			self._pyBtnPrepare.enable = True
			self._pyBtnPrepare.setStateView_(UIState.COMMON)
			self.__startFlashing()
		elif state == "own_prepared":
			if not self._pyBtnFight.visible:
				self._pyBtnPrepare.visible = True
				self._pyBtnPrepare.enable = False
				self._pyBtnPrepare.setStateView_(UIState.DISABLE)
				self.__stopFlashing()
		elif state == "other_preparing":
			self._pyBtnPrepare.visible = True
			self._pyBtnPrepare.enable = False
			self._pyBtnPrepare.setStateView_(UIState.COMMON)
			#self._pyBtnFight.visible = False
			self.__stopFlashing()
		elif state == "other_prepared":
			self._pyBtnPrepare.visible = True
			self._pyBtnPrepare.enable = False
			self._pyBtnPrepare.setStateView_(UIState.DISABLE)
			#self._pyBtnFight.visible = False
			self.__stopFlashing()
		elif state == "own_fighting":
			self._pyBtnPrepare.visible = False
			self._pyBtnFight.visible = True
			self._pyBtnFight.enable = True
			self._pyBtnFight.setStateView_(UIState.COMMON)
			self.__startFlashing()
		elif state == "own_fighted":
			self._pyBtnPrepare.visible = False
			self._pyBtnFight.visible = True
			self._pyBtnFight.enable = False
			self._pyBtnFight.setStateView_(UIState.DISABLE)
			self.__stopFlashing()
		elif state == "other_fighting":
			self._pyBtnFight.visible = True
			self._pyBtnFight.enable = False
			self._pyBtnFight.setStateView_(UIState.COMMON)
			self._pyBtnPrepare.visible = False
			self.__stopFlashing()
		elif state == "other_fighted":
			self._pyBtnFight.visible = True
			self._pyBtnFight.enable = False
			self._pyBtnFight.setStateView_(UIState.DISABLE)
			self._pyBtnPrepare.visible = False
			self.__stopFlashing()
		else:
			self._pyBtnPrepare.visible = True
			self._pyBtnPrepare.enable = False
			self._pyBtnFight.visible = False
			self.__stopFlashing()

	def __flashingBtn( self ):
		"""让按钮闪烁"""
		if self._alpha_shader.value == 1.0:
			self._alpha_shader.value = 0.5
		else:
			self._alpha_shader.value = 1.0
		self._btnFlash_cbid = BigWorld.callback( 0.5, self.__flashingBtn )

	def __startFlashing( self ):
		"""
		开始闪烁
		"""
		self.__stopFlashing()
		self.__flashingBtn()

	def __stopFlashing( self ):
		"""
		停止闪烁
		"""
		if self._btnFlash_cbid:
			BigWorld.cancelCallback( self._btnFlash_cbid )
			self._btnFlash_cbid = 0
		self._alpha_shader.value = 1.0

	@property
	def name(self):
		return self._pyName.text
