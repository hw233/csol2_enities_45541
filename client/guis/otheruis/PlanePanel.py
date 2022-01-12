#-*- coding: gb18030 -*-

import GUI
import BigWorld

import csstatus
import csdefine

from guis.UIFixer import uiFixer
from guis.uidefine import UIState
from guis.common.Window import Window
from guis.controls.Button import Button
from guis import toolbox
from AbstractTemplates import Singleton
from LabelGather import labelGather


class PlanePanel(Window, Singleton):

	def __init__( self ):
		gui = GUI.Window("")
		uiFixer.firstLoadFix(gui)
		Window.__init__( self, gui )
		self.setToDefault()
		self.movable_ = False
		self.escHide_ = False
		self.v_dockStyle = "TOP"
		self.h_dockStyle = "RIGHT"
		self.__initialize(gui)
		self.addToMgr()

	def __initialize(self, gui):
		btn_gui = GUI.load("guis/otheruis/planepanel/button.gui")
		uiFixer.firstLoadFix(btn_gui)
		self._py_button = Button(btn_gui)
		self._py_button.setStatesMapping(UIState.MODE_R1C1)
		self._py_button.onLClick.bind(self.onLeavePlaneBtnClicked)
		self._py_button.onMouseEnter.bind(self.onMouseEnterPlaneBtn)
		self._py_button.onMouseLeave.bind(self.onMouseLeavePlaneBtn)

		self.addPyChild(self._py_button)
		self._py_button.pos = (0, 0)

		self.size = self._py_button.size
		self.top = 200
		self.right = BigWorld.screenWidth() - 130

	def onLeavePlaneBtnClicked(self):
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_DEAD:
			player.statusMessage(csstatus.ROLE_TELEPORT_DEAD_FORBID)
		elif player.state == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage(csstatus.CANNOT_FLY_WHILE_FIGHTING)
		else:
			BigWorld.player().cell.telportToPlaneEntry()

	def onMouseEnterPlaneBtn(self):
		tip = labelGather.getText("PlanePanel:main", "goto_entry" )
		toolbox.infoTip.showToolTips(self, tip)

	def onMouseLeavePlaneBtn(self):
		toolbox.infoTip.hide(self)

	def onLeaveWorld(self):
		self.__class__.cls_trigger(False)

	@classmethod
	def cls_trigger(CLS, visible):
		if visible:
			if not CLS.inst.visible:
				CLS.inst.visible = True
		elif CLS.insted:
			CLS.inst.dispose()
			CLS.releaseInst()

