# -*- coding: gb18030 -*-
#
# $Id: UIHandlerMgr.py,v 1.20 2008-08-02 09:28:18 huangyongwei Exp $

"""
implement ui global event handlers
2005/10/27 : wirten by huangyongwei
"""

import weakref
import csol
import GUI
import IME
import guis.util as util
from bwdebug import *
from AbstractTemplates import Singleton
from Weaker import WeakList
from Function import Functor
from keys import *
from gbref import rds
from guis.RootUIsMgr import ruisMgr
from ExtraEvents import LastMouseEvent
from ExtraEvents import LastKeyDownEvent
from ExtraEvents import LastKeyUpEvent
from guis.common.ScriptObject import ScriptObject


# --------------------------------------------------------------------
# implement cap ui handler
# --------------------------------------------------------------------
class CapHandler :
	"""
	最高优先级的 UI 消息管理器
	"""
	def __init__( self ) :
		self.__pyCapUI = None						# 保存被 cap 的 UI

		self.__isMouseInCapUI = False				# 临时变量，标记鼠标是否在 UI 身上

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		处理按键消息
		"""
		pyCapUI = self.getCapUI()									# 获取被 cap 的 UI
		if pyCapUI is None : return False							# 如果没有被 cap 的 UI，则不处理消息返回
		if not pyCapUI.rvisible or not pyCapUI.enable :				# 判断被 cap 的 UI 是否可见、可用
			self.uncapUI()											# 如果不可见，也不可用，则取消 cap
			return False											# 不处理消息返回
		if key in KEY_MOUSE_KEYS :									# 如果按键是鼠标键
			if not pyCapUI.focus : return False						# 不接收鼠标按键消息，则忽略
			pyCapUI.handleMouseButtonEvent( pyCapUI.getGui(), \
				key, down, mods, csol.rcursorPosition() )			# 发送鼠标消息
		elif pyCapUI.focus : 										# 如果接受键盘消息
			pyCapUI.handleKeyEvent( down, key, mods )				# 发送键盘消息
		return True													# 总是返回 True，拦截消息往下发

	# ---------------------------------------
	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		处理鼠标移动消息
		"""
		pyCapUI = self.getCapUI()										# 获取被 cap 的 UI
		if pyCapUI is None : return False								# 如果没有被 cap 的 UI
		if not pyCapUI.rvisible :										# 判断被 cap 的 UI 是否可见
			self.uncapUI()												# 如果不可见，也不可用，则取消 cap
			return False												# 不处理消息返回
		pos = csol.rcursorPosition()									# 鼠标的屏幕位置
		isMouseHit = pyCapUI.isMouseHit()								# 鼠标是否在 UI 身上
		if pyCapUI.crossFocus :											# 如果接受鼠标进入事件
			if isMouseHit and not self.__isMouseInCapUI :				# 如果鼠标在 UI 身上，但临时变量不为 True
				pyCapUI.handleMouseEnterEvent( pyCapUI.getGui(), pos )	# 则触发鼠标进入事件
				self.__isMouseInCapUI = True							# 并将临时变量设置为 True
			elif not isMouseHit and self.__isMouseInCapUI :				# 如果鼠标不在 UI身上，但临时变量为 False
				pyCapUI.handleMouseLeaveEvent( pyCapUI.getGui(), pos )	# 则触发鼠标离开事件
				self.__isMouseInCapUI = False							# 将临时变量设置为 False
		if pyCapUI.moveFocus :											# 接受鼠标移动消息
			pyCapUI.handleMouseEvent( pyCapUI.getGui(), pos )			# 则触发鼠标移动消息
		else :															# 如果不接受鼠标消息
			return False
		return True														# 总是拦截鼠标移动消息

	# -------------------------------------------------
	def getCapUI( self ) :
		"""
		获取当前被 cap 的 UI，如果没有被 cap 的 UI，则返回 None
		"""
		if self.__pyCapUI is None :
			return None
		pyCapUI = self.__pyCapUI()
		if not pyCapUI or pyCapUI.disposed :
			self.__pyCapUI = None
			return None
		return pyCapUI

	def capUI( self, pyUI ) :
		"""
		cap 一个 UI
		"""
		assert pyUI is not None											# 不能为 None
		pyCapUI = self.getCapUI()										# 获取当前被 cap 的 UI
		if pyCapUI is None :											# 如果当前没有被 cap 的 UI
			self.__pyCapUI = weakref.ref( pyUI )						# 则 cap 指定 UI
		else :															# 否则，没有释放旧 UI 之前
			del pyCapUI
			ERROR_MSG( "the foregoing caped ui is not released!" )		# 不允许 cap 新的 UI

	def uncapUI( self, pyUI = None ) :
		"""
		释放一个被 cap 的 UI，如果 指定的 UI 为 None，则取消当前被 cap 的UI
		"""
		if pyUI is None or self.getCapUI() == pyUI :
			self.__pyCapUI = None


# --------------------------------------------------------------------
# implement active ui handler
# --------------------------------------------------------------------
class TabInHandler :
	"""
	获得焦点的 UI 消息管理器( 主要处理文本输入 )
	"""
	def __init__( self ) :
		self.__pyTabInUI = None										# 保存当前拥有焦点的 UI

	# --------------------------------------------------------------------
	# public
	# --------------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		处理按键消息
		"""
		if key in KEY_MOUSE_KEYS : return False						# 不处理鼠标按键消息
		pyUI = self.getTabInUI()									# 获取当前拥有焦点的 UI
		if pyUI is None : return False								# 如果没有焦点 UI，则返回
		pyActRoot = ruisMgr.getActRoot()							# 获得激活窗口
		if pyActRoot and pyActRoot != pyUI.pyTopParent :			# 如果焦点控件所属的窗口没有被激活
			return False											# 则不处理消息返回

		if not pyUI.rvisible or not pyUI.enable :					# 如果当前焦点 UI 无效，或不可见
			self.tabOutUI()											# 则取消它的焦点
		elif pyUI.handleKeyEvent( down, key, mods ) :				# 如果焦点 UI 拦截了按键消息
			return True												# 则，折断消息
		return False												# 否则让消息继续往下发

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		处理鼠标移动消息
		"""
		return False												# 焦点 UI 不接受鼠标移动消息

	# -------------------------------------------------
	def getTabInUI( self ) :
		"""
		获取当前拥有焦点的 UI
		"""
		if self.__pyTabInUI is None :
			return None
		pyUI = self.__pyTabInUI()
		if pyUI is None : return None
		if not pyUI.rvisible or not pyUI.enable :
			self.tabOutUI()
			return None
		return pyUI

	def tabInUI( self, pyUI ) :
		"""
		让指定 UI 获得焦点
		"""
		if not pyUI.rvisible : return False			# 获得焦点的 UI 必须可见
		if not pyUI.enable : return False			# 获得焦点的 UI 必须可用
		pyTopParent = pyUI.pyTopParent
		if pyTopParent is None : return False
		if not pyTopParent.activable : return False	# 所属父窗口不可被激活

		pyTabInUI = self.getTabInUI()				# 获得当前焦点 UI
		if pyUI == pyTabInUI : return False			# 已经拥有焦点，则返回
		if pyTabInUI is not None :					# 如果当前有拥有焦点的 UI
			self.__pyTabInUI = None					# 取消之前焦点 UI 的焦点，则，将原焦点 UI 的焦点取消
			pyTabInUI.onTabOut_()					# 并触发它的离焦消息（这里调用它的保护方法，是不好的设计）
		ruisMgr.activeRoot( pyUI.pyTopParent )		# 获得焦点的 UI 的顶层窗口，必须成为当前活动 UI
		self.__pyTabInUI = weakref.ref( pyUI )		# 将焦点 UI 设置为指定的 UI
		pyUI.onTabIn_()								# 并触发它的 tab in 消息（这里调用它的保护方法，是不好的设计）
		return True									# 返回设置成功

	def tabOutUI( self, pyUI = None ) :
		"""
		取消指定的焦点 UI 的焦点，如果没有指定 UI，则取消当前焦点 UI 的焦点
		"""
		pyTabInUI = None
		if self.__pyTabInUI :
			pyTabInUI = self.__pyTabInUI()			# 获取当前焦点 UI
		if pyTabInUI is None : return False			# 如果当前没有焦点 UI，则返回取消失败
		if pyUI is None or pyUI == pyTabInUI :		# 如果指定的 UI 为 None 或指定 UI 正是焦点 UI
			self.__pyTabInUI = None					# 则取消焦点 UI 的焦点
			pyTabInUI.onTabOut_()					# 并触发它的离焦消息（这里调用它的保护方法，是不好的设计）
			return True								# 返回撤销焦点成功
		return False								# 返回撤销失败


# --------------------------------------------------------------------
# implement active ui handler
# --------------------------------------------------------------------
class ActHandler :
	"""
	当前激活窗口的消息管理器
	"""
	def __init__( self ) :
		pass

	def handleKeyEvent( self, down, key, mods ) :
		"""
		处理按键消息
		"""
		if key in KEY_MOUSE_KEYS : return False					# 不处理鼠标键消息
		pyActUI = ruisMgr.getActRoot()							# 获取当前激活的 窗口
		if pyActUI is None : return False						# 如果没有激活窗口
		if not pyActUI.enable :									# 如果被激活的窗口不可用（这种情况几乎不会存在）
			return False										# 则不处理消息返回
		if pyActUI.handleKeyEvent( down, key, mods ) :			# 触发键盘按键消息
			return True											# 如果激活窗口处理了这些消息，则返回 True
		return False											# 否则返回 False

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		处理鼠标移动消息
		"""
		return False											# 激活窗口不处理鼠标移动消息


# --------------------------------------------------------------------
# implement shield ui handler
# --------------------------------------------------------------------
class ShieldHandler :
	"""
	全盘拦截消息 UI 消息管理器
	"""
	def __init__( self ) :
		self.__pyShieldUIs = WeakList()							# 当前被 shield 的 UI 列表
		self.__pyLastHitedUIs = WeakList()						# 临时变量：保存鼠标在其上的 UI 列表（用于处理鼠标进入、离开消息）


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getSubHitUIs( self, pyShieldUI ) :
		"""
		获取指定 UI 的所有被鼠标击中的子 UI
		"""
		shieldUI = pyShieldUI.getGui()									# 获取引擎 UI
		def verifier( pyUI ) :											# 验证函数
			if not pyUI.rvisible : return False, 0						# 不可见，则不再检索其子 UI
			if not pyUI.isMouseHit() : return False, 0					# 鼠标没有击中，则不再检索其子 UI
			if not pyUI.acceptEvent : return False, 1					# 不接受消息
			if not pyUI.enable : return False, 0						# 必须可用，则不再检索其子 UI
			return True, 1
		return util.postFindPyGui( shieldUI, verifier, True )			# 获取所有被鼠标击中的 UI

	# ---------------------------------------
	def __dsbMouseButtonEvent( self, pyShieldUI, down, key, mods ) :
		"""
		分发鼠标按键消息
		"""
		pySubUIs = self.__getSubHitUIs( pyShieldUI )					# 获取所有子 UI
		for pySubUI in pySubUIs :										# 顺序分发消息
			if not pySubUI.focus : continue								# 子 UI 不接受鼠标按键消息，则将消息提交给下一个
			if pySubUI.handleMouseButtonEvent( pySubUI.getGui(), \
				key, down, mods, csol.rcursorPosition() ) :				# 如果子 UI 接受鼠标按键消息，则触发它的按键消息
					return True											# 拦截消息返回
		return False													# 如果没有子 UI 处理鼠标消息，则，将不拦截消息

	def __dsbKeyEvent( self, pyShieldUI, down, key, mods ) :
		"""
		分发键盘消息
		"""
		return True														# 拦截掉所有键盘消息


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		处理按键消息
		"""
		pyShieldUI = self.getShieldUI()											# 获取 shield UI
		if pyShieldUI is None : return False									# 如果 shield UI 不存在
		if not pyShieldUI.rvisible :											# 如果当前被 shield 的 UI 不可见
			self.clearShieldUI( pyShieldUI )									# 则将其从 shield 列表中清除
			return self.handleKeyEvent( down, key, mods )						# 并将消息交给下一个 shield UI
		elif not pyShieldUI.enable :											# 如果 UI 无效（这种情况激活没有）
			return True															# 则返回消息已经处理
		if key in KEY_MOUSE_KEYS :												# 如果是键盘按键
			return self.__dsbMouseButtonEvent( pyShieldUI, down, key, mods )	# 分发鼠标按键消息
		elif self.__dsbKeyEvent( pyShieldUI, down, key, mods ) :				# 分发键盘按键消息
			return True
		return False															# 如果键盘拦掉所有消息，这里永远不会执行

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		处理鼠标移动消息
		"""
		pyShieldUI = self.getShieldUI()												# 获取 shield UI
		if pyShieldUI is None : return False										# 如果没有 shield UI，则不处理返回
		pySubUIs = self.__getSubHitUIs( pyShieldUI )								# 获取鼠标击中的子 UI
		pyNewHitUIs = [u for u in pySubUIs if u not in self.__pyLastHitedUIs]		# 鼠标击中，但不在临时列表中的子 UI
		pyOldHitUIs = [u for u in self.__pyLastHitedUIs if u not in pySubUIs]		# 鼠标没有击中，但在临时列表中的 UI
		for pyUI in pyNewHitUIs :													# 触发所有
			pyUI.handleMouseEnterEvent( pyUI.getGui(), csol.rcursorPosition() )		# 鼠标刚刚击中的子 UI 的鼠标进入事件
		for pyUI in pyOldHitUIs :													# 触发所有
			pyUI.handleMouseLeaveEvent( pyUI.getGui(), csol.rcursorPosition() )		# 鼠标刚刚离开的子 UI 的鼠标离开事件
		self.__pyLastHitedUIs.clear()												# 清除临时列表
		self.__pyLastHitedUIs.appends( pySubUIs )									# 重新对临时列表赋值

		for pySubUI in pySubUIs :														# 对所有被鼠标击中的子 UI
			if pySubUI.handleMouseEvent( pySubUI.getGui(), csol.rcursorPosition() ) :	# 触发它的鼠标移动事件
				break																	# 如果消息被处理掉，则不继续往下发
		return True																		# 拦截掉所有鼠标移动事件

	# -------------------------------------------------
	def getShieldUI( self ) :
		"""
		获取当前屏蔽消息的 UI
		"""
		if len( self.__pyShieldUIs ) :
			return self.__pyShieldUIs[-1]
		return None

	def setShieldUI( self, pyUI ) :
		"""
		设置当前屏蔽消息的 UI
		"""
		if pyUI in self.__pyShieldUIs :
			self.__pyShieldUIs.remove( pyUI )
		self.__pyShieldUIs.append( pyUI )
		self.__pyLastHitedUIs.clear()

	def clearShieldUI( self, pyUI = None ) :
		"""
		清除指定屏蔽消息的 UI，如果指定的 UI 为 None，则删除当前屏蔽消息的 UI
		"""
		if pyUI is None :
			self.__pyShieldUIs.clear()
		elif pyUI in self.__pyShieldUIs :
			self.__pyShieldUIs.remove( pyUI )
		self.__pyLastHitedUIs.clear()


# --------------------------------------------------------------------
# implement cast ui handler
# --------------------------------------------------------------------
class CastHandler :
	"""
	cast UI 的消息管理器（cast UI 一般用于菜单列表和一些其他的下拉列表）
	"""
	def __init__( self ) :
		self.__pyCastUIs = WeakList()						# cast UI 列表

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		处理按键消息
		"""
		pyCastUI = self.getCastUI()										# 获取当前被 cast 的 UI
		if pyCastUI is None : return False								# 当前没有被 cast 的 UI
		if key in KEY_MOUSE_KEYS :										# 如果是鼠标按键消息
			if pyCastUI.handleMouseButtonEvent( pyCastUI.getGui(), \
				key, down, mods, csol.rcursorPosition() ) :				# 如果鼠标消息被 cast UI 处理
					return True											# 拦截掉
			return False												# 让消息穿过
		else :
			pyCastUI.handleKeyEvent( down, key, mods )					# 发送键盘按键消息
		return True														# 不处理，并拦截键盘消息

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		处理鼠标移动消息
		"""
		return False													# 不处理、不屏蔽鼠标移动消息

	# -------------------------------------------------
	def getCastUI( self ) :
		"""
		获取当前被 cast 的 UI
		"""
		count = len( self.__pyCastUIs )
		for idx in xrange( count - 1, -1, -1 ) :
			pyUI = self.__pyCastUIs[idx]
			if not pyUI.rvisible : continue
			if not pyUI.enable : continue
			return pyUI
		return None

	def castUI( self, pyUI ) :
		"""
		设置 cast UI
		"""
		assert pyUI is not None, "you can't cast a none ui!"
		if pyUI in self.__pyCastUIs :
			self.__pyCastUIs.remove( pyUI )
		self.__pyCastUIs.append( pyUI )

	def uncastUI( self, pyUI = None ) :
		"""
		取消指定 UI 的 cast 优先级，如果指定 UI 为 None，则取消当前被 cast 的 UI
		"""
		if pyUI is None :
			self.__pyCastUIs.clear()
		elif pyUI in self.__pyCastUIs :
			self.__pyCastUIs.remove( pyUI )


# --------------------------------------------------------------------
# implement common ui handler
# --------------------------------------------------------------------
class CommonHandler :
	"""
	普通 UI 消息管理器
	"""
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		处理按键消息
		"""
		if key not in KEY_MOUSE_KEYS : return False					# 不处理键盘按键消息
		return GUI.handleKeyEvent( down, key, mods ) 				# 将鼠标按键消息交给引擎处理

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		处理鼠标移动消息
		"""
		return GUI.handleMouseEvent( dx, dy, dz )					# 把鼠标移动事件交给引擎处理


# --------------------------------------------------------------------
# handlerMgr
# --------------------------------------------------------------------
class UIHandlerMgr( Singleton ) :
	"""
	消息管理器
	"""
	def __init__( self ) :
		self.__capHandler = CapHandler()							# cap UI（最高消息优先级的 UI）消息管理器
		self.__tabInHandler = TabInHandler()						# 当前拥有焦点 UI 的消息管理器
		self.__actHandler = ActHandler()							# 当前被激活的 UI 的消息管理器
		self.__shieldHandler = ShieldHandler()						# 屏蔽全部消息的 UI 的消息管理器
		self.__castHandler = CastHandler()							# cast UI 的消息管理器（优先级仅高于普通 UI）
		self.__commonHandler = CommonHandler()						# 普通 UI 的消息管理器

		self.__cycleKey = 0											# 临时变量：记录最后一次被按下的鼠标按键
		self.__cycleKeyCBID = 0										# 连续触发 长时间按下按键 的消息 callback ID
		self.__tmpMousePos = ( 0, 0 )								# 记录鼠标位置
		self.mouseOffset = ( 0, 0 )									# 鼠标每个移动 tick 的差值


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __handleMouseScroll( self, dz ) :
		"""
		处理鼠标滚轮消息
		"""
		def verifier( pyUI ) :
			if not pyUI.rvisible : return False, 0						# 如果该子 UI 不可见，则不再检测该子 UI 的子 UI
			if not pyUI.isMouseHit() : return False, 0					# 如果鼠标没击中该子 UI，则不再检测该子 UI 的子 UI
			if getattr( pyUI, "mouseScrollFocus", False ) :				# 判断释放接收滚轮事件
				return True, 1											# 如果该子 UI 可以接受滚轮事件，则添加到列表中，并且找它的子 UI
			return False, 1												# 如果该子 UI 不接受鼠标滚轮消息，则忽略该子 UI，但继续查找它的子 UI

		pyRoot = ruisMgr.getMouseHitRoot()								# 获取鼠标击中的窗口
		if pyRoot is None : return False								# 如果没有击中的窗口则返回
		pyChs = util.postFindPyGui( pyRoot.getGui(), verifier, True )	# 按 Z 坐标顺序找出所有子 UI
		for pyCh in pyChs :
			res = pyCh.onMouseScroll_( dz )								# 触发子 UI 的滚轮消息（这里调用 UI 的保护函数，设计不好）
			if res is None :
				raise TypeError( "method '%s' must return a bool!" % \
					str( pyCh.onMouseScroll_ ) )
			if res :
				return True
		return False													# 没有处理滚轮消息的子 UI

	# -------------------------------------------------
	def __dsbKeyEvent( self, down, key, mods ) :
		"""
		顺序分发按键事件
		"""
		if self.__capHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__tabInHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__actHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__shieldHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__castHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__commonHandler.handleKeyEvent( down, key, mods ) :
			return True
		return False

	def __cycleKeyDown( self, down, key, mods ) :
		"""
		循环处理鼠标按下消息
		"""
		self.__dsbKeyEvent( down, key, mods )							# 分发消息
		#if not BigWorld.isKeyDown( self.__cycleKey ) : return			# 按键已经提起
		self.__cycleKeyCBID = BigWorld.callback( 0.1, \
			Functor( self.__cycleKeyDown, down, key, mods ) )			# 循环处理

	def __rehandleKeyEvent( self, down, key, mods ) :
		"""
		重复处理按键消息
		"""
		if key in KEY_MOUSE_KEYS :										# 如果是鼠标按键消息
			return self.__dsbKeyEvent( down, key, mods )				# 则分发鼠标按键消息
		elif down or key == self.__cycleKey :							# 如果按下键盘键
			BigWorld.cancelCallback( self.__cycleKeyCBID )				# 则停止之前的循环按键处理
		
		if IME.is9FangInputActivated(): 								# 9方输入法过滤
			if key in KEY_9FANGINPUT_HOOK_KEYS:							# 过滤9方输入法进程捕获的键值
				return True
			if down and key == KEY_W and not csol.isVirtualKeyDown( 0x57 ):	# 过滤9方输入法选取字时，干扰DXInput发送多余的w键值的Bug
				return True
		
		if down :														# 如果是按下键
			self.__cycleKey = key										# 则，记录按下的键
			if key not in KEY_MODIFIER_KEYS and not IME.isActivated() :	# 长久按下附加减，不重复( 注意：IME 激活时不重复，
																		# 原因是 IME 有 bug－－它没拦截键盘按下消息，但拦截了键盘提起消息，
																		# 因此，如果不排除 IME 激活，会造成 callback 不停问题)
				self.__cycleKeyCBID = BigWorld.callback( 0.3, \
					Functor( self.__cycleKeyDown, down, key, mods ) )	# 三秒后处理模拟连续按键
		return self.__dsbKeyEvent( down, key, mods )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getCapUI( self ) :
		"""
		获取被 cap 的 UI
		"""
		return self.__capHandler.getCapUI()

	def capUI( self, pyUI ) :
		"""
		设置 cap 的 UI
		"""
		self.__capHandler.capUI( pyUI )

	def uncapUI( self, pyUI = None ) :
		"""
		取消指定 UI 的 cap，如果指定 UI 为 None，则取消当前被 cap 的 UI
		"""
		return self.__capHandler.uncapUI( pyUI )

	def isCapped( self, pyUI ) :
		"""
		判断某个 UI 是否是被 cap 的 UI
		"""
		return self.__capHandler.getCapUI() == pyUI

	# -------------------------------------------------
	def getTabInUI( self ) :
		"""
		获取当前获得焦点的 UI
		"""
		return self.__tabInHandler.getTabInUI()

	def tabInUI( self, pyUI ) :
		"""
		设置某个 UI 拥有焦点
		"""
		return self.__tabInHandler.tabInUI( pyUI )

	def tabOutUI( self, pyUI = None ) :
		"""
		取消指定 UI 的焦点，如果指定 UI 为 None，则取消当前拥有焦点的 UI
		"""
		return self.__tabInHandler.tabOutUI( pyUI )

	def isTabInUI( self, pyUI ) :
		"""
		判断当前拥有焦点的 UI 是否是指定 UI
		"""
		return self.__tabInHandler.getTabInUI() == pyUI

	# -------------------------------------------------
	def getShieldUI( self ) :
		"""
		获取当前活动的 Shield UI
		"""
		return self.__shieldHandler.getShieldUI()

	def setShieldUI( self, pyUI ) :
		"""
		设置指定 UI 为当前活动的 shield UI
		"""
		return self.__shieldHandler.setShieldUI( pyUI )

	def clearShieldUI( self, pyUI ) :
		"""
		从 shield 列表中清除一个 shield UI
		"""
		self.__shieldHandler.clearShieldUI( pyUI )

	def isShieldUI( self, pyUI ) :
		"""
		判断指定 UI 是否是当前激活的 shield UI
		"""
		return self.__shieldHandler.getShieldUI() == pyUI

	# -------------------------------------------------
	def getCastUI( self ) :
		"""
		获取当前被 cast 的 UI
		"""
		return self.__castHandler.getCastUI()

	def castUI( self, pyUI ) :
		"""
		cast 指定 UI
		"""
		self.__castHandler.castUI( pyUI )

	def uncastUI( self, pyUI = None ) :
		"""
		取消指定 UI 的 cast，如果指定 UI 为 None，则取消当前被 cast 的UI
		"""
		self.__castHandler.uncastUI( pyUI )

	def isCasted( self, pyUI ) :
		"""
		判断当前 cast 的 UI 是否是指定的 UI
		"""
		return self.__castHandler.getCastUI() == pyUI


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRootInactivated( self, pyRoot ) :
		"""
		当某个窗口被激活时调用
		"""
		self.tabOutUI()


	# ----------------------------------------------------------------
	# global handlers
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		处理按键事件
		"""
		result = rds.ruisMgr.dragObj.dragging
		if down and key == KEY_LEFTMOUSE :							# 如果按下鼠标左键
			if not ruisMgr.upgradeMouseHitRoot() :					# 将鼠标击中的 UI 提到最前面
				ruisMgr.inactiveRoot()								# 取消当前被激活窗口的激活状态

		if self.__rehandleKeyEvent( down, key, mods ) :				# 分发按键消息
			result = True											# 如果消息被截获

		if down : LastKeyDownEvent.notify( key, mods )				# 通知鼠标最后按下事件
		else:
			if key == KEY_LEFTMOUSE: 
				pyRoot = ruisMgr.getMouseHitRoot()
				if not result and pyRoot and pyRoot.hitable:
					if rds.worldCamHandler.fixed() :
						rds.worldCamHandler.unfix()
					result = True
			LastKeyUpEvent.notify( key, mods )					# 通知鼠标最后提起事件
		return result

	# ---------------------------------------
	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		处理鼠标移动消息
		"""
		newX, newY = csol.pcursorPosition()
		oldX, oldY = self.__tmpMousePos
		dx, dy = newX - oldX, newY - oldY							# 注意：引擎的 dx，dy 有问题
		self.mouseOffset = dx, dy
		self.__tmpMousePos = newX, newY

		# -----------------------------------
		if dz != 0 and self.__handleMouseScroll( dz ) :				# 处理鼠标滚轮事件
			rds.ccursor.normal()									# 置鼠标指针为普通状态，防止鼠标离开超链接不复原（在这里设置似乎不大合适！）
			result = True

		# -----------------------------------
		result = False
		if self.__capHandler.handleMouseEvent( dx, dy, dz ) :		# 让 cap UI 处理鼠标移动消息
			result = True
		elif self.__tabInHandler.handleMouseEvent( dx, dy, dz ) :	# 让焦点 UI 处理鼠标应消息
			result = True
		elif self.__actHandler.handleMouseEvent( dx, dy, dz ) :		# 让激活窗口处理鼠标移动消息
			result = True
		elif self.__shieldHandler.handleMouseEvent( dx, dy, dz ) :	# 让 shield UI 处理鼠标移动消息
			result = True
		elif self.__castHandler.handleMouseEvent( dx, dy, dz ) :	# 让 cast UI 处理鼠标移动消息
			result = True
		elif self.__commonHandler.handleMouseEvent( dx, dy, dz ) :	# 普通 UI 处理鼠标移动消息
			result = True

		# -----------------------------------
		LastMouseEvent.notify( dx, dy, dz )							# 鼠标移动最后消息

		# -----------------------------------
		return result

	def resetMouseState( self ):
		rds.worldCamHandler.unfix()
	
	def onEnterUIArea( self, pyRoot, down, key ):
		pass
		
	def onLeaveUIArea( self, pyRoot, down, key ):
		pass


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
uiHandlerMgr = UIHandlerMgr()
