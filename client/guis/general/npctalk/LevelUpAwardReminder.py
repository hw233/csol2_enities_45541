# -*- coding: gb18030 -*-
#
# $Id: CommontalkWindow.py,v 1.20 2008-08-26 02:16:14 huangyongwei Exp $

"""
implement award remind window for level up
"""

from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.controls.StaticText import StaticText
from event import EventCenter as ECenter
from config.client.help.LevelUpAwardReminder import Datas
from LabelGather import labelGather

class LevelUpAwardReminder( Window ) :
	__instance=None
	def __init__( self ) :
		assert LevelUpAwardReminder.__instance is None,"LevelUpAwardReminder instance has been created"
		LevelUpAwardReminder.__instance=self
		wnd = GUI.load( "guis/tooluis/messagebox/okbox.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = True
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.pyBtnShut_ = HButtonEx( wnd.okBtn )
		self.pyBtnShut_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnShut_.onLClick.bind( self.hide )
		self.pyLbTitle_.text = ""

		self.__pyTextPanel = CSTextPanel( wnd.msgPanel, wnd.scrollBar )
		self.__pyTextPanel.opGBLink = True
		self.__pyTextPanel.text = ""
		self.__pyLbMsg = StaticText( wnd.lbMsg ) # 清空UI内容而已
		self.__pyLbMsg.text = ""

		self.__triggers = {}
		self.__registerTriggers()

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.pyBtnShut_, "NPCTalkWnd:LVReminder", "btnOk" )

	@staticmethod
	def instance():
		"""
		to get the exclusive instance of LevelUpAwardReminder
		"""
		if LevelUpAwardReminder.__instance is None:
			LevelUpAwardReminder.__instance=LevelUpAwardReminder()
		return LevelUpAwardReminder.__instance

	@staticmethod
	def getInstance():
		"""
		return LevelUpAwardReminder.__instance, there are two cases,if  LevelUpAwardReminder.__instance
		is None ,this method will return None,else return the exclusive instance of LevelUpAwardReminder
		"""

		return LevelUpAwardReminder.__instance


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers(self):
		"""
		unregister from ecenter
		"""
		for key in self.__triggers:
			ECenter.unregisterEvent(key,self)
		self.__triggers={}

	# -------------------------------------------------
	def __onRoleLevelChanged( self, oldLevel, level ) :
		"""
		角色等级改变时被调用
		"""
		self.addToMgr()
		if BigWorld.player().isFirstEnterWorld() :
			hint = Datas.get( 1, None )
			if hint :
				self.__pyTextPanel.text = hint
				self.show()
			return
		if oldLevel == level : return
		for lv, hint in Datas.iteritems() :
			if oldLevel < lv <= level :
				self.__pyTextPanel.text = hint
				self.show()
				break

	def onRoleLevelChanged( self, oldLevel, level ):
		"""
		"""
		self.__onRoleLevelChanged(oldLevel, level )

	def __onRoleBenefit( self ):
		"""
		角色到时候领取在线奖励提示  by姜毅
		"""
		hint = Datas.get( 0, None )
		self.addToMgr()
		if hint:
			self.__pyTextPanel.text = hint
			self.r_center = 0
			self.r_middle = 0
			self.show()

	def onRoleBenefit(self):
		"""
		"""
		self.__onRoleBenefit()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
	  self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()

	def hide(self):
		"""
		to destroy LevelUpAwardReminder instance
		"""
		self.removeFromMgr()
		self.dispose()
		self.__unregisterTriggers()
		self.__triggers={}
		LevelUpAwardReminder.__instance=None

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass