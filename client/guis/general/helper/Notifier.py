# -*- coding: gb18030 -*-
#
# $Id: Notifier.py,v 1.10 2008-08-29 02:39:28 huangyongwei Exp $

"""
implement help notifier class.

2008.02.22: writen by huangyongwei
"""

import event.EventCenter as ECenter
import time
from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI

class Notifier( RootGUI ) :
	def __init__( self ) :
		ui = GUI.load( "guis/general/helper/notifier.gui" )
		RootGUI.__init__( self, ui )
		self.activable_ = False
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.focus = True
		self.crossFocus = True
		self.movable_ = False
		self.escHide_ = False
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"
		self.addToMgr( "helpNotifier" )

		self.__flashCBID = 0
		self.__flashEndTime = 0

		self.__triggers = {}
		self.__registerTriggers()

		self.visible = False


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_LOCATED_NOTIFIER_POSITION"] = self.__located

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __located( self, bottom ) :
		self.bottom = bottom

	def __flashAlpha( self, dec ) :
		if self.alpha >= 255 :
			dec = -abs( dec )
		elif self.alpha <= 50 :
			dec = abs( dec )
		alpha = self.alpha + dec
		self.alpha = max( alpha, 50 )
		self.alpha = min( alpha, 255 )
		if time.time() < self.__flashEndTime :
			self.__flashCBID = BigWorld.callback( 0.04, Functor( self.__flashAlpha, dec ) )
		else :
			self.hide()

	def __startFlash( self ) :
		self.__flashAlpha( 10 )

	def __stopFlash( self ) :
		BigWorld.cancelCallback( self.__flashCBID )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		return True

	def onLClick_( self, mods ) :
		ECenter.fireEvent( "EVT_ON_SHOW_COURSE_HELP" )
		self.hide()
		return True

	def onMouseEnter_( self ) :
		rds.ccursor.set( "hand" )
		return True

	def onMouseLeave_( self ) :
		rds.ccursor.normal()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.__stopFlash()
		self.visible = False

	def show( self ) :
		self.__flashEndTime = time.time() + 300
		if not self.visible :
			self.__startFlash()
		RootGUI.show( self )

	def hide( self ) :
		self.__stopFlash()
		rds.ccursor.normal()
		RootGUI.hide( self )

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

# ---------------------------------------------------------
class KeyNotifier( RootGUI ) :
	"""
	重要过程帮助提示按钮
	"""
	showType=""
	__instance=None
	def __init__( self ) :
		assert KeyNotifier.__instance is None,"KeyNotifier instance has been created"
		KeyNotifier.__instance=self
		ui = GUI.load( "guis/general/helper/keynotifier.gui" )
		RootGUI.__init__( self, ui )
		self.activable_ = False
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.focus = True
		self.crossFocus = True
		self.movable_ = False
		self.escHide_ = False
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.addToMgr( "keyNotifier" )
		#self.showType = ""

		self.visible = False
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	@staticmethod
	def instance():
		"""
		to get the exclusive instance
		"""
		if KeyNotifier.__instance is None:
			KeyNotifier.__instance = KeyNotifier()
		return KeyNotifier.__instance

	@staticmethod
	def getInstance():
		"""
		return None or the exclusive instance
		"""
		return KeyNotifier.__instance

	def onLMouseDown_( self, mods ) :
		self.texture = "guis/general/helper/keynotifier_d.texanim" # 播放鼠标按下的动画
		return True

	def onLMouseUp_( self, mods ) :
		self.texture = "guis/general/helper/keynotifier_n.texanim" # 播放鼠标提起的动画
		return True

	def onLClick_( self, mods ) :
		if self.showType == "u":
			ECenter.fireEvent( "EVT_ON_GET_ITEMS_WINDOW_SHOW" )
		else:
			ECenter.fireEvent( "EVT_ON_PHASES_TIPS_WINDOW_SHOW" )
		self.hide()
		return True

	def onMouseEnter_( self ) :
		msg = ""
		if KeyNotifier.showType == "u" :
			msg = labelGather.getText( "KeyHelperWindow:activityHelp", "itemsClew" )
		elif KeyNotifier.showType == "a" :
			msg = labelGather.getText( "KeyHelperWindow:activityHelp", "levelClew" )
		toolbox.infoTip.showItemTips( self, msg )
		self.texture = "guis/general/helper/keynotifier_i.texanim" # 播放鼠标进入的动画
		return True

	def onMouseLeave_( self ) :
		toolbox.infoTip.hide()
		self.texture = "guis/general/helper/keynotifier_n.texanim" # 播放鼠标离开的动画

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.visible = False

	def show( self ) :
		RootGUI.show( self )

	def hide( self ) :
		RootGUI.hide( self )

	def dispose(self):
		KeyNotifier.__instance=None
		RootGUI.dispose(self)

	def __del__(self):
		"""
		just for testing memory leak
		"""
		RootGUI.__del__( self )
		if Debug.output_del_KeyNotifier :
			INFO_MSG( str( self ) )

# --------------------------------------------------------------
class LevelNotifier( RootGUI ) :
	"""
	等级提示按钮
	"""
	__instance=None
	def __init__( self ) :
		assert LevelNotifier.__instance is None,"LevelNotifier instance has been created"
		LevelNotifier.__instance=self
		ui = GUI.load( "guis/general/helper/keynotifier.gui" )
		RootGUI.__init__( self, ui )
		self.activable_ = False
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.focus = True
		self.crossFocus = True
		self.movable_ = False
		self.escHide_ = False
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.addToMgr( "LevelNotifier" )
		self.top += 52

		self.visible = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	@staticmethod
	def instance():
		"""
		to get the exclusive instance
		"""
		if LevelNotifier.__instance is None:
			LevelNotifier.__instance=LevelNotifier()
		return LevelNotifier.__instance

	@staticmethod
	def getInstance():
		"""
		return None or the exclusive instance
		"""
		return LevelNotifier.__instance

	def onLMouseDown_( self, mods ) :
		self.texture = "guis/general/helper/keynotifier_d.texanim" # 播放鼠标按下的动画
		return True

	def onLMouseUp_( self, mods ) :
		self.texture = "guis/general/helper/keynotifier_n.texanim" # 播放鼠标提起的动画
		return True

	def onLClick_( self, mods ) :
		ECenter.fireEvent( "EVT_ON_TOGGLE_UPGRADE_HELPER" )
		self.hide()
		return True

	def onMouseEnter_( self ) :
		msg = labelGather.getText( "HelpWindow:levelHelper", "lvTips" )
		toolbox.infoTip.showItemTips( self, msg )
		self.texture = "guis/general/helper/keynotifier_i.texanim" # 播放鼠标进入的动画
		return True

	def onMouseLeave_( self ) :
		toolbox.infoTip.hide()
		self.texture = "guis/general/helper/keynotifier_n.texanim" # 播放鼠标离开的动画


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.visible = False

	def show( self ) :
		RootGUI.show( self )

	def hide( self ) :
		RootGUI.hide( self )

	def dispose(self):
		LevelNotifier.__instance=None
		RootGUI.dispose(self)

	def __del__(self):
		"""
		just for testing memory leak
		"""
		RootGUI.__del__( self )
		if Debug.output_del_LevelNotifier :
			INFO_MSG( str( self ) )
