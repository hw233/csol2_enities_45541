# -*- coding: gb18030 -*-
#
# $Id: Control.py,v 1.35 2008-08-07 10:39:24 huangyongwei Exp $

"""
implement control base class
-- 2005/04/16 : writen by huangyongwei
"""

import weakref
import IME
from guis import *
from guis.common.ScriptObject import ScriptObject

class Control( ScriptObject ) :
	"""
	所有控件的基类
	"""
	def __init__( self, control = None, pyBinder = None ) :
		ScriptObject.__init__( self, control )
		self.__pyBinder = None								# 控件绑定者，可以为 None
		self.__initialize( control, pyBinder )				# 初始化控件
		self.__canTabIn = True								# 控件是否可以获得焦点
		self.__tabStop = False								# 控件是否获得焦点
		self.__escTabOut = True								# 按下 ESC 键时，是否撤离焦点（设计该属性是不合理的，但是为了方便就此放置）

	def subclass( self, control, pyBinder = None ) :
		"""
		重新设置控件绑定的引擎 UI
		"""
		ScriptObject.subclass( self, control )
		self.__pyBinder = None
		self.__initialize( control, pyBinder )
		return self

	def dispose( self ) :
		"""
		析构控件
		"""
		self.__pyBinder = None
		ScriptObject.dispose( self )

	def __del__( self ) :
		ScriptObject.__del__( self )
		if Debug.output_del_Control :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, control, pyBinder ) :
		if control is None : return
		if pyBinder is not None :
			self.__pyBinder = weakref.ref( pyBinder )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生控件事件
		"""
		ScriptObject.generateEvents_( self )
		self.__onTabIn = None
		self.__onTabOut = None
		self.__onEnable = None
		self.__onDisable = None
		self.__onKeyDown = None
		self.__onKeyUp = None
		self.__onMouseEnter = None
		self.__onMouseLeave = None
		self.__onMouseMove = None
		self.__onMouseScroll = None
		self.__onDragStart = None
		self.__onDragStop = None
		self.__onDrop = None
		self.__onDragEnter = None
		self.__onDragLeave = None
		# ----------------------------------------------------------------------
		#self.__onTabIn = self.createEvent_( "onTabIn" )				# 获得焦点时被触发
		#self.__onTabOut = self.createEvent_( "onTabOut" )			# 焦点离开时被触发
		#self.__onEnable = self.createEvent_( "onEnable" )			# 启用时被触发
		#self.__onDisable = self.createEvent_( "onDisable" )			# 禁用时被触发
		#self.__onKeyDown = self.createEvent_( "onKeyDown" )			# 键盘按键按下时被触发( 如果有一个事件返回 True，则消息不会继续往下发 )
		#self.__onKeyUp = self.createEvent_( "onKeyUp" )				# 键盘按键提起时被触发( 如果有一个事件返回 True，则消息不会继续往下发 )
		#self.__onMouseEnter = self.createEvent_( "onMouseEnter" )	# 鼠标进入时被触发
		#self.__onMouseLeave = self.createEvent_( "onMouseLeave" )	# 鼠标离开时被触发
		#self.__onMouseMove = self.createEvent_( "onMouseMove" )		# 鼠标在控件上移动时被触发
		#self.__onMouseScroll = self.createEvent_( "onMouseScroll" )	# 鼠标在控件上滚动中键时被触发
		#self.__onDragStart = self.createEvent_( "onDragStart" )		# 起拖时被触发
		#self.__onDragStop = self.createEvent_( "onDragStop" )		# 拖放结束时被触发
		#self.__onDrop = self.createEvent_( "onDrop" )				# 放下时被触发
		#self.__onDragEnter = self.createEvent_( "onDragEnter" )		# 拖放进入时被触发
		#self.__onDragLeave = self.createEvent_( "onDragLeave" )		# 拖放离开时被触发

	# -------------------------------------------------
	@property
	def onTabIn( self ) :
		"""
		获得焦点时被触发
		"""
		if self.__onTabIn is None:
			self.__onTabIn = self.createEvent_( "onTabIn" )				# 获得焦点时被触发
		return self.__onTabIn

	@property
	def onTabOut( self ) :
		"""
		焦点离开时被触发
		"""
		if self.__onTabOut is None:
			self.__onTabOut = self.createEvent_( "onTabOut" )				# 获得焦点时被触发
		return self.__onTabOut

	# ---------------------------------------
	@property
	def onEnable( self ) :
		"""
		启用时被触发
		"""
		if self.__onEnable is None:
			self.__onEnable = self.createEvent_( "onEnable" )				# 获得焦点时被触发
		return self.__onEnable

	@property
	def onDisable( self ) :
		"""
		禁用时被触发
		"""
		if self.__onDisable is None:
			self.__onDisable = self.createEvent_( "onDisable" )				# 获得焦点时被触发
		return self.__onDisable

	# ---------------------------------------
	@property
	def onKeyDown( self ) :
		"""
		键盘按键按下时被触发
		"""
		if self.__onKeyDown is None:
			self.__onKeyDown = self.createEvent_( "onKeyDown" )				# 获得焦点时被触发
		return self.__onKeyDown

	@property
	def onKeyUp( self ) :
		"""
		键盘按键提起时被触发
		"""
		if self.__onKeyUp is None:
			self.__onKeyUp = self.createEvent_( "onKeyUp" )				# 获得焦点时被触发
		return self.__onKeyUp

	# ---------------------------------------
	@property
	def onMouseEnter( self ) :
		"""
		鼠标进入时被触发
		"""
		if self.__onMouseEnter is None:
			self.__onMouseEnter = self.createEvent_( "onMouseEnter" )				# 获得焦点时被触发
		return self.__onMouseEnter

	@property
	def onMouseLeave( self ) :
		"""
		鼠标离开时被触发
		"""
		if self.__onMouseLeave is None:
			self.__onMouseLeave = self.createEvent_( "onMouseLeave" )				# 获得焦点时被触发
		return self.__onMouseLeave

	# ---------------------------------------
	@property
	def onMouseMove( self ) :
		"""
		鼠标在控件上移动时被触发
		"""
		if self.__onMouseMove is None:
			self.__onMouseMove = self.createEvent_( "onMouseMove" )				# 获得焦点时被触发
		return self.__onMouseMove

	@property
	def onMouseScroll( self ) :
		"""
		鼠标在控件上滚动中键时被触发
		"""
		if self.__onMouseScroll is None:
			self.__onMouseScroll = self.createEvent_( "onMouseScroll" )				# 获得焦点时被触发
		return self.__onMouseScroll

	# ---------------------------------------
	@property
	def onDragStart( self ) :
		"""
		起拖时被触发
		"""
		if self.__onDragStart is None:
			self.__onDragStart = self.createEvent_( "onDragStart" )				# 获得焦点时被触发
		return self.__onDragStart

	@property
	def onDragStop( self ) :
		"""
		拖放结束时被触发
		"""
		if self.__onDragStop is None:
			self.__onDragStop = self.createEvent_( "onDragStop" )				# 获得焦点时被触发
		return self.__onDragStop

	@property
	def onDrop( self ) :
		"""
		放下时被触发
		"""
		if self.__onDrop is None:
			self.__onDrop = self.createEvent_( "onDrop" )				# 获得焦点时被触发
		return self.__onDrop

	@property
	def onDragEnter( self ) :
		"""
		拖放进入时被触发
		"""
		if self.__onDragEnter is None:
			self.__onDragEnter = self.createEvent_( "onDragEnter" )				# 获得焦点时被触发
		return self.__onDragEnter

	@property
	def onDragLeave( self ) :
		"""
		拖放离开时被触发
		"""
		if self.__onDragLeave is None:
			self.__onDragLeave = self.createEvent_( "onDragLeave" )				# 获得焦点时被触发
		return self.__onDragLeave


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabIn_( self ) :
		"""
		当获得焦点时被调用
		"""
		self.onTabIn()
		if hasattr( self, "notifyInput" ) :
			IME.active()

	def onTabOut_( self ) :
		"""
		当焦点离开时被调用
		"""
		self.onTabOut()
		IME.inactive()

	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		当键盘键按下时被调用
		"""
		if self.onKeyDown( key, mods ) :
			return True
		if self.__escTabOut and key == KEY_ESCAPE and mods == 0 :
			self.tabStop = False									# 按下 ESC 键把焦点撤离
			ScriptObject.onKeyDown_( self, key, mods )
			return True
		return ScriptObject.onKeyDown_( self, key, mods )

	def onKeyUp_( self, key, mods ) :
		"""
		当键盘键提起时被调用
		"""
		if self.onKeyUp( key, mods ) :
			return True
		return ScriptObject.onKeyUp_( self, key, mods )

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		鼠标进入时被调用
		"""
		self.onMouseEnter()
		return ScriptObject.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		"""
		鼠标离开时被调用
		"""
		self.onMouseLeave()
		return ScriptObject.onMouseLeave_( self )

	def onMouseMove_( self, dx, dy ) :
		"""
		鼠标在控件上移动时被调用
		"""
		self.onMouseMove( dx, dy )
		return ScriptObject.onMouseMove_( self, dx, dy )

	def onMouseScroll_( self, dz ) :
		"""
		鼠标在控件上滚动时被调用
		"""
		ScriptObject.onMouseScroll_( self, dz )
		self.onMouseScroll( dz )
		return True

	# ---------------------------------------
	def onDragStart_( self, pyDragged ) :
		"""
		控件被拖起时调用
		"""
		ScriptObject.onDragStart_( self, pyDragged )
		self.onDragStart()
		return True

	def onDragStop_( self, pyDragged ) :
		"""
		控件被放下时被调用
		"""
		self.onDragStop()

	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		有拖放 UI 放下时被调用
		"""
		ScriptObject.onDrop_( self, pyTarget, pyDropped )
		self.onDrop( pyDropped )
		return True

	def onDragEnter_( self, pyTarget, pyDragged ) :
		"""
		拖放进入控件时被调用
		"""
		self.onDragEnter( pyDragged )

	def onDragLeave_( self, pyTarget, pyDragged ) :
		"""
		拖放离开控件时被调用
		"""
		self.onDragLeave( pyDragged )

	# ---------------------------------------
	def onEnable_( self ) :
		ScriptObject.onEnable_( self )
		if hasattr( self, "_Control__oldFX" ) :
			self.materialFX = self.__oldFX
			del self.__oldFX
		self.onEnable()

	def onDisable_( self ) :
		ScriptObject.onDisable_( self )
		self.tabStop = False
		self.__oldFX = self.materialFX
		self.materialFX = "COLOUR_EFF"
		r, g, b, a = self.gui.colourLightFactor
		self.gui.colourLightFactor = ( r, g, b, self.alpha / 255.0 )
		self.onDisable()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPyBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# ---------------------------------------
	def _getCanTabIn( self ) :
		return self.__canTabIn

	def _setCanTabIn( self, value ) :
		self.__canTabIn = value
		if not value :
			self.tabStop = False

	def _getTabStop( self ) :
		return rds.uiHandlerMgr.getTabInUI() == self

	def _setTabStop( self, value ) :
		if value and self.canTabIn :
			rds.uiHandlerMgr.tabInUI( self )
		else :
			rds.uiHandlerMgr.tabOutUI( self )

	def _getESCTabOut( self ) :
		return self.__escTabOut

	def _setESCTabOut( self, escTabOut ) :
		self.__escTabOut = escTabOut

	# -------------------------------------------------
	def _setVisible( self, visible ) :
		ScriptObject._setVisible( self, visible )
		if not self.rvisible and self.tabStop :
			self.tabStop = False


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getPyBinder )											# 获取/设置控件的绑定者
	canTabIn = property( _getCanTabIn, _setCanTabIn )							# 获取/设置控件是否允许获取焦点
	tabStop = property( _getTabStop, _setTabStop )								# 设置控件焦点状况
	escTabOut = property( _getESCTabOut, _setESCTabOut )					 	# 按下 ESC 键时，是否撤离焦点
	visible = property( ScriptObject._getVisible, _setVisible )					# 获取/设置控件的可见性
