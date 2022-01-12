# -*- coding: gb18030 -*-
#
# $Id: RootGUI.py,v 1.50 2008-08-26 02:12:34 huangyongwei Exp $

"""
the python gui in GUI.roots()
2005/07/18 : writen by huangyongwei
"""

import weakref
from guis import *
from ScriptObject import ScriptObject
from guis.controls.Button import Button

class RootGUI( ScriptObject ) :
	"""
	顶层 UI
	注意：要释放 Root 窗口，一定要首先调用 dispose 方法
	"""
	__cc_dock_edge		= 50

	def __init__( self, gui = None ) :
		ScriptObject.__init__( self, gui )
		self.__posZSegment = ZSegs.L4				# 窗口层次，在 guis.uidefine.py 中定义
		self.movable_ = True						# 标示窗口是否可以移动
		self.activable_ = True						# 标示窗口是否可被激活
		self.hitable_ = True						# 如果为 False，鼠标点击在窗口上时，仍然判断鼠标点击的是屏幕
		self.escHide_ = True						# 按 esc 键是否会隐藏
		self.__initialize( gui )					# 初始化
		self.h_dockStyle = "LEFT"					# 在屏幕上的水平停靠方式
		self.v_dockStyle = "MIDDLE"					# 在屏幕上的垂直停靠方式

		# ----------------------------------------
		# private
		# ----------------------------------------
		self.__pyOwner = None						# 父窗口，没有则引用的父窗口为 None
		self.__pySubDialogs = None					# 子窗口列表
		self.__pyOkBtn = None						# 默认的 ok 按钮（按回车等于点击该按钮）
		self.__pyCancelBtn = None					# 默认的 cancel 按钮（按 esc 键等于按该按钮）

		self.__mouseDownPos = ( 0, 0 )				# 临时变量，鼠标在窗口上按下时作记录

	def subclass( self, gui ) :
		"""
		重新设置引擎 UI
		"""
		ScriptObject.subclass( self, gui )
		self.__initialize( gui )
		return self

	def __initialize( self, gui ) :
		if gui is None : return
		self.focus = True							# 默认接收鼠标和键盘按键消息
		self.moveFocus = True						# 默认接收鼠标移动消息（用于处理移动窗口）
		gui.visible = False							# 默认不可见
		uiFixer.attach( self )						# 添加到 ui 元素修正器（当屏幕分辨率改变时，重排子 UI 的位置，以致不会错位）

	def dispose( self ) :
		"""
		析构窗口( 注意，要删除窗口时，一定要调用该方法 )
		"""
		pyOwner = self.pyOwner
		if pyOwner :									# 如果存在父窗口
			pyOwner.__removeSubDialog( self )			# 则从父窗口列表中清除我自己
			if rds.ruisMgr.isActRoot( self ) :			# 是否是当前激活的窗口
				rds.ruisMgr.activeRoot( pyOwner )		# 激活父窗口
		if self.__pySubDialogs is not None :
			for pySubDialog in self.__pySubDialogs :	# 通知所有子窗口
				pySubDialog.__onOwnerHide()				# 我已经隐藏
			self.__pySubDialogs = None					# 清除我的所有子窗口
		self.removeFromMgr()							# 从管理器中去掉
		uiFixer.detach( self )							# 从修正器中去掉
		ScriptObject.dispose( self )

	def __del__( self ) :
		ScriptObject.__del__( self )
		if Debug.output_del_RootGUI :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		生成事件
		"""
		ScriptObject.generateEvents_( self )
		self.__onBeforeShow = self.createEvent_( "onBeforeShow" )			# 窗口显示之前被触发
		self.__onAfterShowed = self.createEvent_( "onAfterShowed" )			# 窗口显示之后被触发
		self.__onBeforeClose = self.createEvent_( "onBeforeClose" )			# 窗口隐藏之前被触发
		self.__onAfterClosed = self.createEvent_( "onAfterClosed" )			# 窗口隐藏之后被触发

	@property
	def onBeforeShow( self ) :
		"""
		窗口显示之前被调用
		"""
		return self.__onBeforeShow

	@property
	def onAfterShowed( self ) :
		"""
		窗口显示之后被调用
		"""
		return self.__onAfterShowed

	@property
	def onBeforeClose( self ) :
		"""
		窗口隐藏之前被调用
		"""
		return self.__onBeforeClose

	@property
	def onAfterClosed( self ) :
		"""
		窗口隐藏之后被调用
		"""
		return self.__onAfterClosed


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addSubDialog( self, pyDialog ) :
		"""
		添加一个子窗口
		"""
		if self.__pySubDialogs is None :
			self.__pySubDialogs = WeakList()
			self.__pySubDialogs.append( pyDialog )
		elif pyDialog not in self.__pySubDialogs :
			self.__pySubDialogs.append( pyDialog )

	def __removeSubDialog( self, pyDialog ) :
		"""
		删除一个子窗口
		"""
		if self.__pySubDialogs is None :
			return
		elif pyDialog in self.__pySubDialogs :
			self.__pySubDialogs.remove( pyDialog )
			if len( self.__pySubDialogs ) == 0 :
				self.__pySubDialogs = None

	def __onOwnerHide( self ) :
		"""
		当窗口的父窗口隐藏时被调用
		"""
		self.hide()												# 父窗口隐藏时，自己也隐藏
		self.__pyOwner = None									# 取消对父窗口的引用


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		if self.movable_ and self.isMouseHit() :				# 如果窗口允许被鼠标移动
			uiHandlerMgr.capUI( self )							# cap 窗口（即让窗口优先接收系统消息）
			self.__mouseDownPos = self.mousePos					# 记录下鼠标在我身上的像素位置
		return True

	def onLMouseUp_( self, mods ) :
		uiHandlerMgr.uncapUI( self )							# 鼠标提起时释放 cap
		if rds.worldCamHandler.fixed() :
			rds.worldCamHandler.unfix()

	def onMouseMove_( self, dx, dy ) :
		if uiHandlerMgr.getCapUI() == self :					# 如果窗口当前被 cap，则意味着窗口将被移动
			mx, my = csol.pcursorPosition()						# 获取鼠标屏幕上的像素位置
			wx, wy = self.posToScreen							# 获取窗口在屏幕上的像素位置
			self.left = mx - self.__mouseDownPos[0]				# (水平方向窗口移到鼠标位置，不是鼠标移动的前后位置差)
			self.top = my - self.__mouseDownPos[1]				#（垂直方向窗口移到鼠标位置，不是鼠标移动的前后位置差)
			self.onMove_( dx, dy )								# 触发移动消息
			return True											# 拦截消息
		return ScriptObject.onMouseMove_( self, dx, dy )

	def onKeyDown_( self, key, mods ) :
		if ruisMgr.getActRoot() != self : return False									# 只有窗口处于激活状态时才接收 keydown 消息
		ScriptObject.onKeyDown_( self, key, mods )										# 回调 ScriptObject 的 onKeyDown
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			pyOkBtn = self.pyOkBtn														# 则获取默认的 ok 按钮
			if pyOkBtn is not None and pyOkBtn.rvisible and pyOkBtn.enable :			# 如果该按钮可用
				pyOkBtn.onLClick()														# 则触发按钮的点击事件
				return True																# 拦截消息
		elif ( mods == 0 ) and ( key == KEY_ESCAPE ) :									# 如果按下了 ESC 键
			pyCancelBtn = self.pyCancelBtn												# 则获取默认的取消按钮
			if pyCancelBtn is not None and pyCancelBtn.enable and pyCancelBtn.rvisible :# 如果取消按钮可用
				pyCancelBtn.onLClick()													# 则触发取消按钮的点击消息
				return True																# 拦截消息
		return False																	# 让消息跳过

	# -------------------------------------------------
	def onMove_( self, dx, dy ) :
		"""
		当窗口移动时被调用
		"""
		pass

	def onClose_( self ) :
		"""
		当窗口关闭前被调用
		注意：可以通过重写该函数来控制窗口的关闭，如果返回 False，则取消关闭
			  可以通过重写该函数，关闭窗口之前，在该方法中作一些关闭判断，从而在一定条件下取消窗口的关闭
		"""
		return True


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		pass

	def onInactivated( self ) :
		"""
		当窗口取消激活时状态被调用
		"""
		pass

	# -------------------------------------------------
	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		当游戏状态将要改变时被调用
		@param					onStatus  : 改变前的状态（在 Define.py 中定义）
		@param					newStatus : 改变后的状态（在 Define.py 中定义）
		"""
		pass

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		当游戏状态改变时被调用
		@param					onStatus  : 改变前的状态（在 Define.py 中定义）
		@param					newStatus : 改变后的状态（在 Define.py 中定义）
		"""
		pass

	def onEnterWorld( self ) :
		"""
		当角色初始化完毕进入世界时被调用
		"""
		pass

	def onLeaveWorld( self ) :
		"""
		当角色离开世界时被调用
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addToMgr( self, hookName = "" ) :
		"""
		添加到窗口管理器
		"""
		rds.ruisMgr.add( self, hookName )

	def removeFromMgr( self ) :
		"""
		从窗口管理器中删除
		"""
		rds.ruisMgr.remove( self )

	# -------------------------------------------------
	def show( self, pyOwner = None, floatOwner = True ) :
		"""
		显示窗口
		@type				pyOwner	   : GUIBaseObject
		@param				pyOwner	   : 窗口的父窗口或控件（注：如果是控件，则会被转换为控件所属的窗口）
		@type				floatOwner : bool
		@param				floatOwner : 是否修改 posZSegment，让窗口漂浮在 pyOwner 的上面（pyOwner 不为 None 时，才起作用）
		"""
		if not self.rvisible :
			self.onBeforeShow()												# 如果之前时隐藏状态的，则触发显示消息
		self.__pyOwner = None
		if pyOwner is not None :											# 如果有父窗口（或父控件）
			pyTopParent = pyOwner.pyTopParent								# 获取父窗口的顶层 UI
			assert pyTopParent != self										# 父窗口不能是自己
			if isinstance( pyTopParent, RootGUI ) :							# 父窗口（或父控件的顶层窗口）必须继承于 RootGUI
				self.__pyOwner = weakref.ref( pyOwner.pyTopParent )			# 记录父窗口
				if floatOwner :
					self.posZSegment = self.pyOwner.posZSegment				# 将父窗口设置为与本窗口同层
				self.pyOwner.__addSubDialog( self )							# 调用父窗口添加本本窗口为父窗口的子窗口
			else :															# 如果父窗口不是继承于 RootGUI
				ERROR_MSG( "class of '%s' must be inheired from RootGUI!" \
				% str( pyTopParent ) )										# 则输出错误信息

		from guis.ScreenViewer import ScreenViewer
		if not ScreenViewer().isEmptyScreen() or\
			ScreenViewer().isResistHiddenRoot(self):						# 如果本身是清屏时例外显示的窗口，则照常显示
				ScriptObject._setVisible( self, True )						# 回调父类的显示函数
		rds.ruisMgr.onRootShow( self )										# 告诉管理器我显示本窗口
		self.onAfterShowed()												# 触发显示事件

	def hide( self ) :
		"""
		隐藏窗口
		"""
		if not self.onClose_() : return										# 首先触发 onClose_，如果 onClose_ 返回 False，则取消隐藏
		ruisMgr.onRootHide( self )											# 告诉管理器有一个 UI 隐藏
		isActive = rds.ruisMgr.isActRoot( self )							# 是否是当前激活的 UI
		self.onBeforeClose()												# 触发隐藏前事件
		ScriptObject._setVisible( self, False )								# 回调父类的 visible 属性方法
		if not self.rvisible :												# 如果隐藏成功
			if self.__pySubDialogs is not None :
				for pySubDialog in self.__pySubDialogs :					# 通知所有子窗口
					pySubDialog.__onOwnerHide()								# 我已经隐藏
				self.__pySubDialogs = None									# 清除我的所有子窗口
			pyOwner = self.pyOwner
			if pyOwner is not None :										# 如果有父窗口
				pyOwner.__removeSubDialog( self )							# 则从父窗口列表中清除我自己
				if isActive :
					rds.ruisMgr.activeRoot( pyOwner )						# 激活父窗口
		self.onAfterClosed()												# 触发隐藏后事件

	# -------------------------------------------------
	def setOkButton( self, pyBtn ) :
		"""
		设置默认的确定按钮
		"""
		if pyBtn is None :
			self.__pyOkBtn = None
		else :
			self.__pyOkBtn = weakref.ref( pyBtn )

	# ---------------------------------------
	def setCancelButton( self, pyBtn ) :
		"""
		设置默认的取消按钮
		"""
		if pyBtn is None :
			self.__pyCancelBtn = None
		else :
			self.__pyCancelBtn = weakref.ref( pyBtn )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPosZSegment( self ) :
		return self.__posZSegment

	def _setPosZSegment( self, seg ) :
		oldSeg = self.__posZSegment
		self.__posZSegment = seg
		ruisMgr.onZSegmentChanged( self, oldSeg, seg )

	# -------------------------------------------------
	def _getOwner( self ) :
		if self.__pyOwner is None :
			return None
		return self.__pyOwner()

	def _getOkBtn( self ) :
		if self.__pyOkBtn is None :
			return None
		return self.__pyOkBtn()

	def _getCancelBtn( self ) :
		if self.__pyCancelBtn is None :
			return None
		return self.__pyCancelBtn()

	def _getSubDialogs( self ) :
		if self.__pySubDialogs is None :
			return []
		return self.__pySubDialogs.list()

	# ---------------------------------------
	def _setVisible( self, isVisible ) :
		argCount = self.show.func_code.co_argcount						# show 方法的参数个数
		defs = self.show.im_func.func_defaults							# show 方法的默认参数
		defCount = 0													# show 方法的默认参数个数
		if defs : defCount = len( defs )
		if argCount == defCount + 1 :									# 参数个数等于默认参数个数
			if isVisible : self.show()
			else : self.hide()
		elif self.pyOwner and argCount == 2 :							# 如果有两个参数，并且第二个参数为 pyOwner
			if isVisible : self.show( self.pyOwner )
			else : self.hide()
		else :
			if isVisible : RootGUI.show( self, self.pyOwner )
			else : RootGUI.hide( self )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	posZSegment = property( _getPosZSegment, _setPosZSegment )			# 获取/设置窗口的层次
	hitable = property( lambda self : self.hitable_ )					# 获取窗口是否忽略鼠标点击，如果为 False，则即使鼠标在窗口上，仍然认为鼠标直接点击的是屏幕
	activable = property( lambda self : self.activable_ )				# 获取窗口是否可被激活
	escHide = property( lambda self : self.escHide_ )					# 指出按 esc 键后，窗口是否可以隐藏

	pyOwner = property( _getOwner )										# 获取窗口的父窗口
	pyOkBtn = property( _getOkBtn )										# 获取默认的确认按钮
	pyCancelBtn = property( _getCancelBtn )								# 获取默认的取消按钮
	pySubDialogs = property( _getSubDialogs )							# 获取窗口的所有子窗口
	visible = property( ScriptObject._getVisible, _setVisible )			# 获取/设置窗口的可见性
