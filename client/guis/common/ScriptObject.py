# -*- coding: gb18030 -*-
#
# $Id: ScriptObject.py,v 1.27 2008-08-05 01:18:53 huangyongwei Exp $

"""
python gui contains events
2006/08/20 : writen by huangyongwei
"""

from guis import *
from guis.ExtraEvents import ControlEvent
from GUIBaseObject import GUIBaseObject
from gbref import rds

class ScriptObject( GUIBaseObject ) :
	def __init__( self, gui = None ) :
		GUIBaseObject.__init__( self, gui )
		self.__initialize( gui )					# 初始化
		self.__mouseScrollFocus = False				# 增加一个额外的鼠标滚轮 focus

		self.__enable = True						# 记录是否可用（不是灰色状态）
		self.__dragMark = DragMark.NONE				# 设置默认的拖放标记

		self.__isLMouseDown = False					# 临时变量：当鼠标左键按下时记录为 True，当鼠标左键提起时，根据它来判断是否是点击
		self.__isRMouseDown = False					# 临时变量：当鼠标右键按下时记录为 True，当鼠标右键提起时，根据它来判断是否是点击
		self.__clickCount = 0						# 临时变量：记录鼠标连续左键点击的次数，以实现双击
		self.__dbclickCBID = 0						# 临时变量：实现双击的 callback ID，鼠标按下时，延时，时间到后，清除 __clickCount，以丢弃双击记录

		self.generateEvents_()						# 生成事件

	def subclass( self, gui ) :
		GUIBaseObject.subclass( self, gui )
		self.__initialize( gui )
		return self

	def dispose( self ) :
		"""
		release resource
		"""
		self.focus = False
		self.moveFocus = False
		self.crossFocus = False
		self.dragFocus = False
		self.dropFocus = False
		self.mouseScrollFocus = False
		GUIBaseObject.dispose( self )

	def __del__( self ) :
		self.__guiObject = None
		GUIBaseObject.__del__( self )
		if Debug.output_del_ScriptObject :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, gui ) :
		"""
		初始化
		"""
		if gui is None : return
		self.__guiObject = gui


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		event = ControlEvent( ename, self )
		return event

	def generateEvents_( self ) :
		self.__onLMouseDown = None
		self.__onLMouseUp = None
		self.__onRMouseDown = None
		self.__onRMouseUp = None
		self.__onLClick = None
		self.__onRClick = None
		self.__onLDBClick = None
		
		# 在使用时才生成，游戏过程中只会有一部分ui会被使用到，这部分ui中也只有若干个事件会被触发。16:15 2013-4-25 by wsf
		#self.__onLMouseDown = self.createEvent_( "onLMouseDown" )		# 当鼠标左键按下时被触发
		#self.__onLMouseUp = self.createEvent_( "onLMouseUp" )			# 当鼠标左键提起时被触发
		#self.__onRMouseDown = self.createEvent_( "onRMouseDown" )		# 当鼠标右键按下时被触发
		#self.__onRMouseUp = self.createEvent_( "onRMouseUp" )			# 当鼠标右键提起时被触发
		#self.__onLClick = self.createEvent_( "onLClick" )				# 当鼠标左键点击时被触发
		#self.__onRClick = self.createEvent_( "onRClick" )				# 当鼠标右键点击时被触发
		#self.__onLDBClick = self.createEvent_( "onLDBClick" )			# 当鼠标左键双击时被触发

	# ---------------------------------------
	@property
	def onLMouseDown( self ) :
		"""
		当鼠标左键按下时被触发
		"""
		if self.__onLMouseDown is None:
			self.__onLMouseDown = self.createEvent_( "onLMouseDown" )	
		return self.__onLMouseDown

	@property
	def onLMouseUp( self ) :
		"""
		当鼠标左键提起时被触发
		"""
		if self.__onLMouseUp is None:
			self.__onLMouseUp = self.createEvent_( "onRMouseUp" )
		return self.__onLMouseUp

	@property
	def onRMouseDown( self ) :
		"""
		当鼠标右键按下时被触发
		"""
		if self.__onRMouseDown is None:
			self.__onRMouseDown = self.createEvent_( "onRMouseDown" )
		return self.__onRMouseDown

	@property
	def onRMouseUp( self ) :
		"""
		当鼠标右键提起时被触发
		"""
		if self.__onRMouseUp is None:
			self.__onRMouseUp = self.createEvent_( "onRMouseUp" )
		return self.__onRMouseUp

	# ---------------------------------------
	@property
	def onLClick( self ) :
		"""
		当鼠标左键点击时被触发
		"""
		if self.__onLClick is None:
			self.__onLClick = self.createEvent_( "onLClick" )
		return self.__onLClick

	@property
	def onRClick( self ) :
		"""
		当鼠标右键点击时被触发
		"""
		if self.__onRClick is None:
			self.__onRClick = self.createEvent_( "onRClick" )
		return self.__onRClick

	@property
	def onLDBClick( self ) :
		"""
		当鼠标左键双击时被触发
		"""
		if self.__onLDBClick is None:
			self.__onLDBClick = self.createEvent_( "onLDBClick" )
		return self.__onLDBClick


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __enableAllChildren( self ) :
		"""
		恢复 enable 之前所有 enable 为 True 的孩子的 enable 属性
		"""
		def verifier( pyCh ) :
			if not pyCh.acceptEvent :							# 如果该子 UI 不接受事件
				return False, 1									# 则忽略该子 UI，并继续检查该子 UI 的子 UI
			if not pyCh.enable :								# 如果该子 UI 还是 disable，则它的所有子 UI 肯定也是 disable
				return False, 0									# 因此，忽略该在 UI，并且不再检查它的所有子 UI
			return True, 1										# 如果该子 UI 已经 由 disable 变为 enable，则将该子 UI 添加到列表，并继续检查该子 UI 的子 UI

		pyChs = util.preFindPyGui( self.__guiObject, verifier )	# 前序搜索所有的子 UI
		for pyCh in pyChs : pyCh.onEnable_()					# 并触发已经处于 enable 状态的子 UI 的 onEnable_ 函数

	def __disableAllChildren( self ) :
		"""
		disable 时，同时 disable 所有的孩子
		"""
		def verifier( pyCh ) :
			if pyCh == self :									# 如果该 UI 就是我本身
				return True, 1									# 则接受到列表，并继续检查我子 UI
			if not pyCh.acceptEvent :							# 如果该子 UI 不接受事件
				return False, 1									# 则忽略该子 UI，并继续检查该子 UI 的子 UI
			if not pyCh.__enable :								# 如果该子 UI 原本就处于无效状态
				return False, 0									# 则忽略该子 UI，并且不再检查该子 UI 的所有子 UI
			return True, 1										# 如果该子 UI 已经由 enable 变为 disable，则将该子 UI 添加到列表，并继续检查该子 UI 的子 UI
		pyChs = util.preFindPyGui( self.__guiObject, verifier )	# 前序搜索所有的子 UI
		for pyCh in pyChs : pyCh.onDisable_()					# 并触发已经处于 disable 状态的子 UI 的 onEnable_ 函数

	# -------------------------------------------------
	def __onDCHoldingEnd( self ) :
		"""
		记录双击延时到时被调用
		"""
		self.__clickCount = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def resetBindingUI_( self, gui ) :
		"""
		重新绑定一个新的引擎 UI
		"""
		if gui == self.__guiObject : return
		GUIBaseObject.resetBindingUI_( self, gui )
		self.__guiObject = gui


	# -------------------------------------------------
	# about keyboard
	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		当键盘键按下时被调用
		"""
		return False

	def onKeyUp_( self, key, mods ) :
		"""
		当键盘键提起时本调用
		"""
		return False


	# -------------------------------------------------
	# about mouse
	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		"""
		当鼠标左键按下时被调用
		"""
		self.onLMouseDown()
		return True

	def onLMouseUp_( self, mods ) :
		"""
		当鼠标左键提起时被调用
		"""
		self.onLMouseUp()
		if rds.worldCamHandler._WorldCamHandler__isFixup :
			rds.worldCamHandler.unfix()
		return True


	def onRMouseDown_( self, mods ) :
		"""
		当鼠标右键按下时被调用
		"""
		self.onRMouseDown()
		return True

	def onRMouseUp_( self, mods ) :
		"""
		当鼠标右键提起时被调用
		"""
		self.onRMouseUp()
		if rds.worldCamHandler._WorldCamHandler__isFixup :
			rds.worldCamHandler.unfix()
		return True

	# ------------------------------------------------
	def onLClick_( self, mods ) :
		"""
		当鼠标左键点击时被调用
		"""
		self.onLClick()
		return True

	def onRClick_( self, mods ) :
		"""
		当鼠标右键点击时被调用
		"""
		self.onRClick()
		return True

	def onLDBClick_( self, mods ) :
		"""
		当鼠标双击时被调用
		"""
		self.onLDBClick()
		return True

	# ------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		当鼠标进入时被调用
		"""
		pass

	def onMouseLeave_( self ) :
		"""
		当鼠标离开时被调用
		"""
		pass

	# ------------------------------------------------
	def onMouseMove_( self, dx, dy ) :
		"""
		当鼠标移动时被调用
		"""
		return True

	def onMouseScroll_( self, dx ) :
		"""
		当鼠标滚轮滚动时被调用
		"""
		return True


	# -------------------------------------------------
	# about drag & drop
	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		"""
		当开始拖起一个 UI 对象时被调用
		"""
		if self.__guiObject is None : return False
		if not BigWorld.isKeyDown( KEY_LEFTMOUSE ) : return True
		rds.ruisMgr.dragObj.show( self, self.dragMark )
		return self.isMouseHit()

	def onDragStop_( self, pyDragged ) :
		"""
		当拖放结束时被调用
		"""
		pass

	# ---------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		当一个拖放一个 UI 对象在我身上放下时被调用
		"""
		return False

	# ---------------------------------------
	def onDragEnter_( self, pyTarget, pyDragged ) :
		"""
		当拖放进入时被调用
		"""
		pass

	def onDragLeave_( self, pyTarget, pyDragged ) :
		"""
		当拖放离开时被调用
		"""
		pass

	# ---------------------------------------
	def onEnable_( self ) :
		"""
		从无效变为有效状态时被调用
		"""
		pass

	def onDisable_( self ) :
		"""
		从有效变为无效状态时被调用
		"""
		pass


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# keyboard relative
	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		当键盘键按下或提起时被调用
		"""
		if key in KEY_MOUSE_KEYS : return False				# 不处理鼠标按键消息
		if down and self.onKeyDown_( key, mods ) :			# 触发按键按下事件
			return True
		if not down and self.onKeyUp_( key, mods ) :		# 触发按键提起事件
			return True
		return False

	def handleAxisEvent( self, axis, value, dTime ):
		if not self.enable : return True
		return False


	# ----------------------------------------------------------------
	# mouse relative
	# ----------------------------------------------------------------
	def handleMouseButtonEvent( self, comp, key, down, mods, pos ) :
		"""
		当鼠标按键按下或提起时被调用
		"""
		if not self.enable : return False						# 如果不可用，则返回
		if rds.ruisMgr.dragObj.dragging : return True			# 如果处于拖放状态，则返回

		result = False
		# -----------------------------------
		# 触发按键事件
		# -----------------------------------
		if down and key == KEY_LEFTMOUSE :						# 如果按下左键
			self.__isLMouseDown = True							# 则，设置左键按下标记
			self.__clickCount += 1								# 将单击计数加 1
			self.__dbclickCBID = BigWorld.callback( 0.8, \
				self.__onDCHoldingEnd )							# 延时 0.8 秒后清空点击计数
			result = self.onLMouseDown_( mods )					# 触发按下左键事件
		if down and key == KEY_RIGHTMOUSE :						# 如果按下右键
			self.__isRMouseDown = True							# 则，设置右键按下标记
			result = self.onRMouseDown_( mods )					# 触发按下右键事件

		if not down and key == KEY_LEFTMOUSE :					# 如果提起左键
			clickResult = False									# 设置一个临时变量，记录本嵌套内的触发事件结果
			if self.__isLMouseDown :							# 如果左键按下标记为 True（表示鼠标在我身上按下）
				clickResult = self.onLClick_( mods )			# 则，触发点击事件（在我身上按下，在我身上提起，则属于点击）
				self.__isLMouseDown = False						# 清空左键按下标记（防止下次左键仅仅在我身上提起也会触发点击）
			if self.__clickCount == 2 :							# 统计鼠标在规定时间内在我身上按下的次数，如果等于 2
				BigWorld.cancelCallback( self.__dbclickCBID )	# 则，取消计数延时（清空本次双击计数）
				self.onLDBClick_( mods )						# 触发双击事件
			upResult = self.onLMouseUp_( mods )					# 最后触发鼠标提起事件
			result = upResult or clickResult					# 结果是，外围结果与嵌套内结果的或操作
		if not down and key == KEY_RIGHTMOUSE :					# 如果提起鼠标右键
			clickResult = False									# 设置一个临时变量，记录本嵌套内的触发事件结果
			if self.__isRMouseDown :							# 如果右键提起标记为 True（说明右键在我身上按下）
				clickResult = self.onRClick_( mods )			# 则，触发右击事件（只有在我身上按下，同时也在我身上提起才属于点击）
				self.__isRMouseDown = False						# 清空右键按下标记（防止下次右键仅仅在我身上提起也会触发点击）
			upResult = self.onRMouseUp_( mods )					# 触发右键提起事件
			result = upResult or clickResult					# 选取或结果
		return result											# 返回点击结果

	def handleMouseClickEvent( self, comp, pos ) :
		"""
		当鼠标单击时被调用
		"""
		if not self.enable : return True
		return False

	def handleMouseEvent( self, comp, pos ) :
		"""
		当鼠标移动时被调用
		"""
		if not self.enable : return True						# 如果无效，则返回
		dx, dy = rds.uiHandlerMgr.mouseOffset					# 移动前后位置差
		if rds.uiHandlerMgr.isCapped( self ) :					# 优先处理 cap UI
			return self.onMouseMove_( dx, dy )					# 触发鼠标移动事件
		if self.isMouseHit() :									# 如果不是 cap UI，则只有鼠标在 UI 身上
			return self.onMouseMove_( dx, dy )					# 才触发移动事件
		return False

	# -------------------------------------------------
	def handleMouseEnterEvent( self, comp, pos ) :
		"""
		当鼠标进入时被调用
		"""
		if not self.enable : return True						# 不可用，则返回
		if ruisMgr.getMouseHitRoot() == self.pyTopParent :		# 鼠标击中的是我所属的窗口
			self.onMouseEnter_()								# 触发鼠标进入事件
		return True

	def handleMouseLeaveEvent( self, comp, pos ) :
		"""
		当鼠标离开时被调用
		"""
		if not self.enable : return True						# 不可用，则返回
		self.onMouseLeave_()									# 触发鼠标离开事件
		return True

	# -------------------------------------------------
	# drag & drop relative
	# -------------------------------------------------
	def handleDragStartEvent( self, comp, pos ) :
		"""
		当开始拖放时被调用
		"""
		if not self.enable : return False							# 不可用，则不处理拖放事件
		if not BigWorld.isKeyDown( KEY_LEFTMOUSE ) : return False	# 鼠标没有点下去，则不处理拖放事件
		def resetDragItemMouseInPos( itemPos, pos ) :				# 设置鼠标在拖放对象身上的坐标
			left = pos[0] - itemPos[0]
			top = pos[1] - itemPos[1]
			rds.ruisMgr.dragObj.mouseInPos = ( left, top )

		pyDraged = UIScriptWrapper.unwrap( comp )					# 拖放对象的 python UI
		if pyDraged is None : return False							# 如果不存在，则取消拖放
		if not pyDraged.rvisible : return False						# 如果拖放对象不可见，则取消拖放
		if ruisMgr.getMouseHitRoot() == pyDraged.pyTopParent :		# 拖放对象的父窗口，必须被鼠标击中
			done = self.onDragStart_( pyDraged )					# 触发拖放事件
			resetDragItemMouseInPos( pyDraged.r_posToScreen, pos )	# 设置拖放对象的位置
			return done												# 返回拖放成功
		return False

	def handleDragStopEvent( self, comp, pos ) :
		"""
		当拖放结束时被调用
		"""
		if not self.enable : return True							# 拖放对象不可用
		pyDraged = UIScriptWrapper.unwrap( comp )					# 获取拖放对象的 python UI
		if pyDraged is None : return False							# 不存在，则取消拖放结束通知
		self.onDragStop_( pyDraged )								# 触发拖放结束事件
		return True

	# ---------------------------------------
	def handleDropEvent( self, comp, pos, dropped ) :
		"""
		当拖放在我身上放下时被调用
		"""
		if not self.enable : return True							# 不可用则返回
		pyTarget = UIScriptWrapper.unwrap( comp )					# 获取放下对象的 python UI
		self.onDrop_( pyTarget, UIScriptWrapper.unwrap( dropped ) )	# 触发放下事件
		return True

	# ---------------------------------------
	def handleDragEnterEvent( self, comp, pos, dragged ) :
		"""
		当拖放进入时被调用
		"""
		if not self.enable : return True
		pyTarget = UIScriptWrapper.unwrap( comp )
		if pyTarget is None : return False
		self.onDragEnter_( pyTarget, UIScriptWrapper.unwrap( dragged ) )
		return True

	def handleDragLeaveEvent( self, comp, pos, dragged ) :
		"""
		当拖放离开时被调用
		"""
		if not self.enable : return True
		pyTarget = UIScriptWrapper.unwrap( comp )
		if pyTarget is None : return False
		self.onDragLeave_( pyTarget, UIScriptWrapper.unwrap( dragged ) )
		return True


	# -------------------------------------------------
	# inner methods
	# -------------------------------------------------
	def focus( self, state ) :
		"""
		该方法是引擎内部方法，因为不会用到，属性 focus 把它覆盖
		"""
		pass

	def crossFocus( self, state ) :
		"""
		该方法是引擎内部方法，因为不会用到，属性 crossFocus 把它覆盖
		"""
		pass

	def moveFocus( self, state ) :
		"""
		该方法是引擎内部方法，因为不会用到，属性 moveFocus 把它覆盖
		"""
		pass

	def dragFocus( self, state ) :
		"""
		该方法是引擎内部方法，因为不会用到，属性 dragFocus 把它覆盖
		"""
		pass

	def dropFocus( self, state ) :
		"""
		该方法是引擎内部方法，因为不会用到，属性 dropFocus 把它覆盖
		"""
		pass

	# -------------------------------------------------
	def onLoad( self, dataSection ) :
		pass

	def onDelete( self ) :
		pass

	def onSave( self, dataSection ) :
		pass

	def onBound( self ) :
		pass


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getScriptParent( self ) :
		parent = self.__guiObject.parent
		while parent :
			pyParent = UIScriptWrapper.unwrap( parent )
			if pyParent and pyParent.acceptEvent :
				return pyParent
			parent = parent.parent
		return None

	# -------------------------------------------------
	def _getFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.focus

	def _setFocus( self, value ) :
		self.__guiObject.focus = False					# 首先从 focus 列表中清除（这是引擎的 bug，如果这里不首先设置为 False，下面的设置将无效）
		self.__guiObject.focus = value					# 再加入 focus 列表

	# ---------------------------------------
	def _getMoveFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.moveFocus

	def _setMoveFocus( self, value ) :
		self.__guiObject.moveFocus = value

	# ---------------------------------------
	def _getCrossFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.crossFocus

	def _setCrossFocus( self, value ) :
		self.__guiObject.crossFocus = value

	# ---------------------------------------
	def _getMouseScrollFocus( self ) :
		if not self.enable : return False
		return self.__mouseScrollFocus

	def _setMouseScrollFocus( self, value ) :
		self.__mouseScrollFocus = value

	# ---------------------------------------
	def _getDragFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.dragFocus

	def _setDragFocus( self, value ) :
		self.__guiObject.dragFocus = value

	# ---------------------------------------
	def _getDropFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.dropFocus

	def _setDropFocus( self, value ) :
		self.__guiObject.dropFocus = value

	# ---------------------------------------
	def _getEnable( self ) :
		if not self.__enable : return False
		pyParent = self.pyScriptParent
		while pyParent :										# 如果有父 UI 的是 disable
			if not pyParent.enable :							# 则
				return False									# 所有子 UI 也是 disable
			pyParent = pyParent.pyScriptParent
		return True

	def _setEnable( self, enable ) :
		if self.__enable == enable : return						# 属性值没变则返回
		self.__enable = enable									# 否则设置为信息可用状态
		if enable :
			if self.enable :									# 没有 disable 的父亲
				self.__enableAllChildren()						# 让所有原来为 enable 的子 UI 一同 enable
		else :
			pyParent = self.pyScriptParent
			if not pyParent or pyParent.enable :				# 父亲 enable
				self.__disableAllChildren()						# 将所有子 UI 设置为 disable

	# -------------------------------------------------
	def _getDragMark( self ) :
		return self.__dragMark

	def _setDragMark( self, mark ) :
		self.__dragMark = mark


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyScriptParent = property( _getScriptParent )								# 获取最近一个层次的继承于 ScriptObject 的 parent
	acceptEvent = property( lambda self : True )								# 指出 python 是否接受系统消息
	focus = property( _getFocus, _setFocus )									# 获取/设置是否接收按键及鼠标点击消息
	moveFocus = property( _getMoveFocus, _setMoveFocus )						# 获取/设置是否接收鼠标移动消息
	crossFocus = property( _getCrossFocus, _setCrossFocus )						# 获取/设置是否接收鼠标进入消息
	mouseScrollFocus = property( _getMouseScrollFocus, _setMouseScrollFocus )	# 获取/设置是否接收鼠标滚轮消息
	dragFocus = property( _getDragFocus, _setDragFocus )						# 获取/设置是否接收鼠标拖起消息
	dropFocus = property( _getDropFocus, _setDropFocus )						# 获取/设置是否接收鼠标放下消息
	enable = property( _getEnable, _setEnable )									# 获取/设置本 UI 是否可用（非灰色状态）

	dragMark = property( _getDragMark, _setDragMark )							# 获取/设置拖放标记
