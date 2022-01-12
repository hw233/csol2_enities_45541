# -*- coding: gb18030 -*-
#
# $Id: ScrollBar.py,v 1.30 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement scrollbar class

2005.06.15: writen by huangyongwei
"""

from LabelGather import labelGather
from guis import *
from guis.common.Frame import VFrame
from guis.common.Frame import HFrame
from guis.common.FrameEx import VFrameEx
from guis.common.FrameEx import HFrameEx
from Control import Control
from Button import Button


# --------------------------------------------------------------------
# 获取文件目录
# --------------------------------------------------------------------
def getFileFolder( texture ) :
	return "/".join( texture.split( "/" )[:-1] )


# --------------------------------------------------------------------
# implement vertical scroll bar class
# --------------------------------------------------------------------
class ScrollBar( Control ) :
	"""
	滚动条基类
	"""
	def __init__( self, sb, pySlot, pyMoveBar, pyBinder = None ) :
		Control.__init__( self, sb, pyBinder )
		self.mouseScrollFocus = True

		self.__scrollScale = 1									# 拉动条与滚动漕的长度比（一定大于 1，因为拉条肯定比漕高）
		self.__perScroll = 0.1									# 点击一下按钮，或滚一下鼠标滚轮的滑动值
		self.__initialize( sb, pySlot, pyMoveBar )

		self.__cycleScrollCBID = 0								# 一直按下鼠标左键，处理连续滚动的 callback ID

	def subclass( self, sb, pySlot, pyMoveBar, pyBinder ) :
		Control.subclass( self, sb, pyBinder )
		self.__initialize( sb, pySlot, pyMoveBar )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ScrollBar :
			INFO_MSG( str( self ) )

	# -------------------------------------------------
	def __initialize( self, sb, pySlot, pyMoveBar ) :
		self.pyMoveBar_ = pyMoveBar									# 拉动条
		self.pyMoveBar_.onLMouseDown.bind( self.onLMouseDown_ )

		self.pySlot_ = pySlot										# 滚动漕
		self.pySlot_.focus = True									# 点击滚动漕，拉条瞬时滚动到鼠标按下的地方
		self.pySlot_.onLClick.bind( self.__onSlotClick )			# 点击滚动漕时，滚动条瞬时跳到鼠标处
		self.pySlot_.onLMouseDown.bind( self.onLMouseDown_ )
		self.pyIncBtn_ = Button( sb.incBtn )						# 增值按钮
		self.pyIncBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyIncBtn_.onLMouseDown.bind( self.__onIncBtnMouseDown, True )
		self.pyIncBtn_.onLMouseDown.bind( self.onLMouseDown_, True )
		self.pyIncBtn_.onLMouseUp.bind( self.__onBtnMouseUp )
		self.pyDecBtn_ = Button( sb.decBtn )						# 减值按钮
		self.pyDecBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyDecBtn_.onLMouseDown.bind( self.__onDecBtnMouseDown, True )
		self.pyDecBtn_.onLMouseDown.bind( self.onLMouseDown_, True )
		self.pyDecBtn_.onLMouseUp.bind( self.__onBtnMouseUp )

		self.scrollScale = 1										# 默认滑动比例是 1:1 ( 拉条填满滚动漕 )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Control.generateEvents_( self )
		self.__onScroll = self.createEvent_( "onScroll" )

	@property
	def onScroll( self ) :
		return self.__onScroll


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getMaxLength( self ) :
		"""
		获取滚动漕的剩余高度
		"""
		slotLength = self.pySlot_.length
		return slotLength - self.pyMoveBar_.length

	def __scroll( self, currLen ) :
		"""
		让滚动条滚动指定的高度值
		"""
		self.pyMoveBar_.start = currLen							# 设置拉条的低值端位置
		maxLen = self.__getMaxLength()
		value = 0
		if maxLen > 0 : value = currLen / maxLen
		self.onScroll( value )

	# -------------------------------------------------
	def __cycleIncScroll( self ) :
		"""
		如果一直按下左键，则循环连续滚动
		"""
		if self.pyIncBtn_.isMouseHit() :						# 只有鼠标击中增值按钮才处理
			self.incScroll()									# 增值滚动
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :				# 直到鼠标提起
			self.__cycleScrollCBID = BigWorld.callback( \
				0.1, self.__cycleIncScroll )					# 循环下一次滚动

	def __cycleDecScroll( self ) :
		"""
		如果一直按下左键，则循环连续滚动
		"""
		if self.pyDecBtn_.isMouseHit() :						# 只有鼠标击中减值按钮才处理
			self.decScroll()									# 减值滚动
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :				# 直到鼠标提起
			self.__cycleScrollCBID = BigWorld.callback( \
				0.1, self.__cycleDecScroll )					# 循环下一次滚动

	# -------------------------------------------------
	def __onIncBtnMouseDown( self ) :
		"""
		点击增值滚动按钮时被触发
		"""
		self.incScroll()										# 增值滚动
		self.__cycleScrollCBID = BigWorld.callback( \
			0.4, self.__cycleIncScroll )						# 0.5 秒后模拟循环点击

	def __onDecBtnMouseDown( self ) :
		"""
		点击减值滚动按钮时被触发
		"""
		self.decScroll()										# 减值滚动
		self.__cycleScrollCBID = BigWorld.callback( \
			0.4, self.__cycleDecScroll )						# 0.5 秒后模拟循环点击

	def __onBtnMouseUp( self ) :
		"""
		鼠标在按钮上提起时被触发
		"""
		BigWorld.cancelCallback( self.__cycleScrollCBID )

	# ---------------------------------------
	def __onSlotClick( self ) :
		"""
		点击滚动漕时被触发
		"""
		maxLen = self.__getMaxLength()							# 获取滚动漕长度
		if maxLen <= 0 : return									# 无效长度
		mstart = self.pySlot_.mouseSit							# 鼠标在滚动漕中的位置（如果是水平，则为 left，如果是垂直则为 top）
		if mstart < self.pyMoveBar_.start :
			self.value = mstart / maxLen
		elif mstart > self.pyMoveBar_.end :
			self.value = ( mstart - self.pyMoveBar_.length ) / maxLen


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		鼠标滚轮消息
		"""
		if dz < 0 : self.incScroll()
		else : self.decScroll()
		return True


	# ----------------------------------------------------------------
	# friend methods of the VMoveBar
	# ----------------------------------------------------------------
	def onMoveBarSlide__( self, inc ) :
		"""
		当滑动条滑动时被调用
		"""
		maxLen = self.__getMaxLength()
		oldLen = self.pyMoveBar_.start
		if inc < 0 and oldLen <= 0 : return
		if inc > 0 and oldLen >= maxLen : return
		newLen = oldLen + inc
		if newLen <= 0 and inc < 0 :
			newLen = 0
		elif newLen >= maxLen and inc > 0 :
			newLen = maxLen
		self.__scroll( newLen )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStatesMapping( self, mode ) :
		"""
		设置滑动调的状态 mapping
		"""
		self.pyMoveBar_.setStatesMapping( mode )

	# -------------------------------------------------
	def incScroll( self, count = 1 ) :
		"""
		增值滚动一个( 或多个 )单位
		"""
		if self.value > 1 - self.__perScroll :			
			self.value = 1
			self.onScroll( self.value )
			
		else :
			self.value += count * self.__perScroll

	def decScroll( self, count = 1 ) :
		"""
		减值滚动一个( 或多个 )单位
		"""
		if self.value < self.__perScroll :
			self.value = 0
			self.onScroll( self.value )
		else :
			self.value -= count * self.__perScroll


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getScrollScale( self ) :
		return self.__scrollScale

	def _setScrollScale( self, scale ) :
		scale = max( 1, scale )
		oldScale = self.__scrollScale
		self.__scrollScale = scale
		slotLen = self.pySlot_.length
		mbLen = slotLen / scale
		self.pyMoveBar_.length = mbLen
		if self.pyMoveBar_.end > slotLen :
			self.pyMoveBar_.end = slotLen
		if scale == 1 and mbLen != slotLen :		# 滚动条长度太短了（比拉条的最小值还小）
			self.pyMoveBar_.visible = False
		else :
			self.pyMoveBar_.visible = True

	# ---------------------------------------
	def _getValue( self ) :
		maxLen = self.__getMaxLength()
		currLen = self.pyMoveBar_.start
		if maxLen == 0 : return 0
		value = currLen / maxLen
		if value > 0.999 :
			return 1.0
		return value

	def _setValue( self, value ) :
		if value <= 0 :
			if self.value == 0.0 :
				return
			value = 0
		elif value >= 1 :
			if self.value == 1.0 :
				return
			value = 1.0
		maxLen = self.__getMaxLength()
		currLen = value * maxLen
		self.__scroll( currLen )

	# ---------------------------------------
	def _getPerScroll( self ) :
		return self.__perScroll

	def _setPerScroll( self, value ) :
		value = max( value, 0 )
		value = min( value, 1 )
		self.__perScroll = value


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	scrollScale = property( _getScrollScale, _setScrollScale )	# 获取/设置内容的最大高度 除以 可视高度( 所以它必定大于或等于 1 )
	value = property( _getValue, _setValue )					# 获取/设置当前滚动值( 0 ~ 1 之间 )
	perScroll = property( _getPerScroll, _setPerScroll ) 		# 获取/设置单位滚动值（当点击向上或向下按钮时的滚动值）


# --------------------------------------------------------------------
# vertical scroll bar
# --------------------------------------------------------------------
"""
① the move bar can be flexed
composing :
	GUI.Window
		-- upBtn ( gui of csui.controls.Button.Button )
		-- downBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
				-- t ( GUI.Simple )
				-- b ( GUI.Simple )
				-- bg ( GUI.Simple ) -- NOTE: bg.tiled = True

② the move bar is fixed
composing :
	GUI.Window
		-- upBtn ( gui of csui.controls.Button.Button )
		-- downBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
"""

class VScrollBar( ScrollBar ) :
	"""
	垂直滚动条
	"""
	def __init__( self, scrollBar = None, pyBinder = None ) :
		if type( scrollBar.slot.moveBar ) is GUI.TextureFrame :
			pyMoveBar = VMoveBarEx( scrollBar.slot.moveBar, self )
		else :
			pyMoveBar = VMoveBar( scrollBar.slot.moveBar, self )
		pySlot = _VSlot( scrollBar.slot )
		ScrollBar.__init__( self, scrollBar, pySlot, pyMoveBar, pyBinder )

	def subclass( self, scrollBar, pyBinder ) :
		ScrollBar.subclass( self, scrollBar, pyBinder )
		return self


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setHeight( self, height ) :
		added = height - self.height
		self.pyIncBtn_.top += added
		self.pySlot_.height += added
		ScrollBar._setHeight( self, height )
		self._setScrollScale( self.scrollScale )
		self._setValue( self.value )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( ScrollBar._getWidth )					 	# 获取滚动条宽度
	height = property( ScrollBar._getHeight, _setHeight )		# 获取/设置滚动条高度


# --------------------------------------------------------------------
# horizontal scroll bar
# --------------------------------------------------------------------
"""
composing :
① the move bar is flexible
	GUI.Window
		-- leftBtn ( gui of csui.controls.Button.Button )
		-- rightBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
				-- l ( GUI.Simple )
				-- r ( GUI.Simple )
				-- bg ( GUI.Simple ) -- NOTE: bg.tiled = True

② the move bar is not flexible
	GUI.Window
		-- leftBtn ( gui of csui.controls.Button.Button )
		-- rightBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
"""

class HScrollBar( ScrollBar ) :
	"""
	水平滚动条
	"""
	def __init__( self, scrollBar = None, pyBinder = None ) :
		if type( scrollBar.slot.moveBar ) is GUI.TextureFrame :
			pyMoveBar = HMoveBarEx( scrollBar.slot.moveBar, self )
		else :
			pyMoveBar = HMoveBar( scrollBar.slot.moveBar, self )
		pySlot = _HSlot( scrollBar.slot )
		ScrollBar.__init__( self, scrollBar, pySlot, pyMoveBar, pyBinder )
		self.pyIncBtn_.onMouseEnter.bind( self.__onScrollBtnMouseEnter )
		self.pyIncBtn_.onMouseLeave.bind( self.__onScrollBtnMouseLeave )
		self.pyDecBtn_.onMouseEnter.bind( self.__onScrollBtnMouseEnter )
		self.pyDecBtn_.onMouseLeave.bind( self.__onScrollBtnMouseLeave )

	def subclass( self, scrollBar, pyBinder ) :
		ScrollBar.subclass( self, scrollBar, pyBinder )
		return self


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onScrollBtnMouseEnter( self, pyBtn ) :
		tips = labelGather.getText( "ScrollBar:main", "tips" )
		toolbox.infoTip.showToolTips( pyBtn, tips )

	def __onScrollBtnMouseLeave( self ) :
		toolbox.infoTip.hide()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		added = width - self.width
		self.pyIncBtn_.left += added
		self.pySlot_.width += added
		ScrollBar._setWidth( self, width )
		self._setScrollScale( self.scrollScale )
		self._setValue( self.value )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( ScrollBar._getWidth, _setWidth )			# 获取/设置滚动条宽度
	height = property( ScrollBar._getHeight )					# 获取/设置滚动条高度


# --------------------------------------------------------------------
# implement move bar base class
# --------------------------------------------------------------------
class MoveBar( Control ) :
	"""
	拉动条基类
	"""
	__cc_min_length			= 16

	def __init__( self, moveBar, pyBinder ) :
		Control.__init__( self, moveBar, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.moveFocus = True

		self.minLength_ = self.__cc_min_length
		self.flexible_ = False							# 是否是可伸缩拉条
		self.mouseSit_ = 0								# 鼠标按下时的位置
		self.canScroll_ = False							# 是否允许滚动

		self.states_ = {}
		self.states_[UIState.COMMON] = self.mapping
		self.states_[UIState.HIGHLIGHT] = self.mapping
		self.states_[UIState.PRESSED] = self.mapping
		self.states_[UIState.DISABLE] = self.mapping

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ScrollBar :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseUp_( self, mods ) :
		self.canScroll_ = False
		if self.isMouseHit() :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
		uiHandlerMgr.uncapUI( self )
		return True

	def onMouseEnter_( self ) :
		if not BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		self.setState( UIState.COMMON )
		return True

	# ---------------------------------------
	def onEnable_( self ) :
		Control.onEnable_( self )
		self.setState( UIState.COMMON )

	def onDisable_( self ) :
		Control.onDisable_( self )
		self.setState( UIState.DISABLE )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		设置状态 mapping
		"""
		if not self.flexible_ :
			self.mapping = self.states_[state]


# --------------------------------------------------------------------
# implement vertical move bar class
# --------------------------------------------------------------------
class VMoveBar( VFrame, MoveBar ) :
	"""
	垂直滑动条
	"""
	def __init__( self, moveBar, pyBinder ) :
		MoveBar.__init__( self, moveBar, pyBinder )
		if hasattr( moveBar, "t" ) :
			VFrame.__init__( self, moveBar )
			self.minLength_ = self.pyT_.height + self.pyB_.height
			self.flexible_ = True

		if self.flexible_ :
			self.states_[UIState.COMMON] = ( self.pyT_.mapping, self.pyBg_.texture, self.pyB_.mapping )
			self.states_[UIState.HIGHLIGHT] = ( self.pyT_.mapping, self.pyBg_.texture, self.pyB_.mapping )
			self.states_[UIState.PRESSED] = ( self.pyT_.mapping, self.pyBg_.texture, self.pyB_.mapping )
			self.states_[UIState.DISABLE] = ( self.pyT_.mapping, self.pyBg_.texture, self.pyB_.mapping )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		MoveBar.onLMouseDown_( self, mods )
		self.mouseSit_ = self.mousePos[1]
		self.setState( UIState.PRESSED )
		self.canScroll_ = True
		uiHandlerMgr.capUI( self )
		return True

	def onMouseMove_( self, dx, dy ) :
		if not self.canScroll_ : return False
		if dy == 0 : return True
		if dy > 0 and self.mousePos[1] < self.mouseSit_ : return True
		if dy < 0 and self.mousePos[1] > self.mouseSit_ : return True
		self.pyBinder.onMoveBarSlide__( dy )
		return True


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def setStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		"""
		rows, cols = stMode
		def getMapping( size ) :
			cmapping = util.getStateMapping( size, stMode, ( 0 / cols + 1, 0 % cols + 1 )  )
			hmapping = util.getStateMapping( size, stMode, ( 1 / cols + 1, 1 % cols + 1 ) )
			pmapping = util.getStateMapping( size, stMode, ( 2 / cols + 1, 2 % cols + 1 ) )
			dmapping = util.getStateMapping( size, stMode, ( 3 / cols + 1, 3 % cols + 1 ) )
			return cmapping, hmapping, pmapping, dmapping

		if not self.flexible_ :
			mappings = getMapping( self.size )
			self.states_[UIState.COMMON] = mappings[0]
			self.states_[UIState.HIGHLIGHT] = mappings[1]
			self.states_[UIState.PRESSED] = mappings[2]
			self.states_[UIState.DISABLE] = mappings[3]
		else :
			tmappings = getMapping( self.pyT_.size )
			bmappings = getMapping( self.pyB_.size )
			cbgtexture = self.pyBg_.textureFolder + "/movebar_cbg.dds"
			hbgtexture = self.pyBg_.textureFolder + "/movebar_hbg.dds"
			pbgtexture = self.pyBg_.textureFolder + "/movebar_pbg.dds"
			dbgtexture = ""

			self.states_[UIState.COMMON] = tmappings[0], cbgtexture, bmappings[0]
			self.states_[UIState.HIGHLIGHT] = tmappings[1], hbgtexture, bmappings[1]
			self.states_[UIState.PRESSED] = tmappings[2], pbgtexture, bmappings[2]
			self.states_[UIState.DISABLE] = tmappings[3], dbgtexture, bmappings[3]

		self.setState( UIState.COMMON )

	def setState( self, state ) :
		"""
		设置状态
		"""
		MoveBar.setState( self, state )
		if self.flexible_ :
			self.pyT_.mapping, self.pyBg_.texture, self.pyB_.mapping = self.states_[state]


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setHeight( self, height ) :
		if self.flexible_ :
			VFrame._setHeight( self, max( self.minLength_, height ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	start = property( MoveBar._getTop, MoveBar._setTop )
	end = property( MoveBar._getBottom, MoveBar._setBottom )
	length = property( MoveBar._getHeight, _setHeight )
	height = property( MoveBar._getHeight, _setHeight )


# --------------------------------------------------------------------
# implement vertical move bar class( 使用新的 GUI.TextureFrame )
# --------------------------------------------------------------------
class VMoveBarEx( VFrameEx, MoveBar ) :
	"""
	垂直滑动条
	"""
	def __init__( self, moveBar, pyBinder ) :
		VFrameEx.__init__( self, moveBar )
		MoveBar.__init__( self, moveBar, pyBinder )
		self.flexible_ = True
		t = moveBar.elements["frm_t"]
		b = moveBar.elements["frm_b"]
		bg = moveBar.elements["frm_bg"]
		self.__textureFolder = getFileFolder( t.texture )
		self.states_[UIState.COMMON] = ( t.mapping, bg.texture, b.mapping )
		self.states_[UIState.HIGHLIGHT] = ( t.mapping, bg.texture, b.mapping )
		self.states_[UIState.PRESSED] = ( t.mapping, bg.texture, b.mapping )
		self.states_[UIState.DISABLE] = ( t.mapping, bg.texture, b.mapping )

		self.minLength_ = t.size.y + b.size.y


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		MoveBar.onLMouseDown_( self, mods )
		self.mouseSit_ = self.mousePos[1]
		self.setState( UIState.PRESSED )
		self.canScroll_ = True
		uiHandlerMgr.capUI( self )
		return True

	def onMouseMove_( self, dx, dy ) :
		if not self.canScroll_ : return False
		if dy == 0 : return True
		if dy > 0 and self.mousePos[1] < self.mouseSit_ : return True
		if dy < 0 and self.mousePos[1] > self.mouseSit_ : return True
		self.pyBinder.onMoveBarSlide__( dy )
		return True


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def setStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		"""
		rows, cols = stMode
		def getMapping( size ) :
			cmapping = util.getStateMapping( size, stMode, ( 0 / cols + 1, 0 % cols + 1 )  )
			hmapping = util.getStateMapping( size, stMode, ( 1 / cols + 1, 1 % cols + 1 ) )
			pmapping = util.getStateMapping( size, stMode, ( 2 / cols + 1, 2 % cols + 1 ) )
			dmapping = util.getStateMapping( size, stMode, ( 3 / cols + 1, 3 % cols + 1 ) )
			return cmapping, hmapping, pmapping, dmapping

		moveBar = self.getGui()
		tmappings = getMapping( moveBar.elements["frm_t"].size )
		bmappings = getMapping( moveBar.elements["frm_b"].size )
		cbgtexture = self.__textureFolder + "/movebar_cbg.dds"
		hbgtexture = self.__textureFolder + "/movebar_hbg.dds"
		pbgtexture = self.__textureFolder + "/movebar_pbg.dds"

		self.states_[UIState.COMMON] = tmappings[0], cbgtexture, bmappings[0]
		self.states_[UIState.HIGHLIGHT] = tmappings[1], hbgtexture, bmappings[1]
		self.states_[UIState.PRESSED] = tmappings[2], pbgtexture, bmappings[2]

		self.setState( UIState.COMMON )

	def setState( self, state ) :
		"""
		设置状态
		"""
		MoveBar.setState( self, state )
		bar = self.getGui()
		tmapping, bgTexture, bmapping = self.states_[state]
		bar.elements['frm_t'] = tmapping
		bar.elements['frm_b'] = bmapping
		bar.elements['frm_bg'].texture = bgTexture


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setHeight( self, height ) :
		VFrameEx._setHeight( self, max( self.minLength_, height ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	start = property( MoveBar._getTop, MoveBar._setTop )
	end = property( MoveBar._getBottom, MoveBar._setBottom )
	length = property( MoveBar._getHeight, _setHeight )
	height = property( MoveBar._getHeight, _setHeight )


# --------------------------------------------------------------------
# implement horizontal move bar calss
# --------------------------------------------------------------------
class HMoveBar( HFrame, MoveBar ) :
	"""
	水平滑动条
	"""
	def __init__( self, moveBar, pyBinder ) :
		MoveBar.__init__( self, moveBar, pyBinder )
		if hasattr( moveBar, "l" ):
			HFrame.__init__( self, moveBar )
			self.minLength_ = self.pyL_.width + self.pyR_.width
			self.flexible_ = True

		if self.flexible_ :
			self.states_[UIState.COMMON] = self.pyL_.mapping, self.pyBg_.texture, self.pyR_.mapping
			self.states_[UIState.HIGHLIGHT] = self.pyL_.mapping, self.pyBg_.texture, self.pyR_.mapping
			self.states_[UIState.PRESSED] = self.pyL_.mapping, self.pyBg_.texture, self.pyR_.mapping
			self.states_[UIState.DISABLE] = self.pyL_.mapping, self.pyBg_.texture, self.pyR_.mapping


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		MoveBar.onLMouseDown_( self, mods )
		self.mouseSit_ = self.mousePos[0]
		self.setState( UIState.PRESSED )
		self.canScroll_ = True
		uiHandlerMgr.capUI( self )
		return True

	def onMouseMove_( self, dx, dy ) :
		if not self.canScroll_ : return False
		if dx == 0 : return True
		if dx > 0 and self.mousePos[0] < self.mouseSit_ : return True
		if dx < 0 and self.mousePos[0] > self.mouseSit_ : return True
		self.pyBinder.onMoveBarSlide__( dx )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		"""
		rows, cols = stMode
		def getMapping( size ) :
			cmapping = util.getStateMapping( size, stMode, ( 0 / cols + 1, 0 % cols + 1 )  )
			hmapping = util.getStateMapping( size, stMode, ( 1 / cols + 1, 1 % cols + 1 ) )
			pmapping = util.getStateMapping( size, stMode, ( 2 / cols + 1, 2 % cols + 1 ) )
			dmapping = util.getStateMapping( size, stMode, ( 3 / cols + 1, 3 % cols + 1 ) )
			return cmapping, hmapping, pmapping, dmapping

		if not self.flexible_ :
			mappings = getMapping( self.size )
			self.states_[UIState.COMMON] = mappings[0]
			self.states_[UIState.HIGHLIGHT] = mappings[1]
			self.states_[UIState.PRESSED] = mappings[2]
			self.states_[UIState.DISABLE] = mappings[3]
		else :
			lmappings = getMapping( self.pyL_.size )
			rmappings = getMapping( self.pyR_.size )
			cbgtexture = self.pyBg_.textureFolder + "/movebar_cbg.dds"
			hbgtexture = self.pyBg_.textureFolder + "/movebar_hbg.dds"
			pbgtexture = self.pyBg_.textureFolder + "/movebar_pbg.dds"
			dbgtexture = ""

			self.states_[UIState.COMMON] = lmappings[0], cbgtexture, rmappings[0]
			self.states_[UIState.HIGHLIGHT] = lmappings[1], hbgtexture, rmappings[1]
			self.states_[UIState.PRESSED] = lmappings[2], pbgtexture, rmappings[2]
			self.states_[UIState.DISABLE] = lmappings[3], dbgtexture, rmappings[3]

		self.setState( UIState.COMMON )

	def setState( self, state ) :
		"""
		设置状态
		"""
		MoveBar.setState( self, state )
		if self.flexible_ :
			self.pyL_.mapping, self.pyBg_.texture, self.pyR_.mapping = self.states_[state]


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		if self.flexible_ :
			HFrame._setWidth( self, max( self.minLength_, width ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	start = property( MoveBar._getLeft, MoveBar._setLeft )
	end = property( MoveBar._getRight, MoveBar._setRight )
	length = property( MoveBar._getWidth, _setWidth )
	width = property( MoveBar._getWidth, _setWidth )



# --------------------------------------------------------------------
# implement horizontal move bar calss( 使用新的 TextureFrame 组件 )
# --------------------------------------------------------------------
class HMoveBarEx( HFrameEx, MoveBar ) :
	"""
	水平滑动条
	"""
	def __init__( self, moveBar, pyBinder ) :
		HFrameEx.__init__( self, moveBar )
		MoveBar.__init__( self, moveBar, pyBinder )
		self.flexible_ = True
		l = moveBar.elements["frm_l"]
		r = moveBar.elements["frm_r"]
		bg = moveBar.elements["frm_bg"]
		self.__textureFolder = getFileFolder( l.texture )
		self.states_[UIState.COMMON] = ( l.mapping, bg.texture, r.mapping )
		self.states_[UIState.HIGHLIGHT] = ( l.mapping, bg.texture, r.mapping )
		self.states_[UIState.PRESSED] = ( l.mapping, bg.texture, r.mapping )
		self.states_[UIState.DISABLE] = ( l.mapping, bg.texture, r.mapping )

		self.minLength_ = l.size.x + r.size.x


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		MoveBar.onLMouseDown_( self, mods )
		self.mouseSit_ = self.mousePos[0]
		self.setState( UIState.PRESSED )
		self.canScroll_ = True
		uiHandlerMgr.capUI( self )
		return True

	def onMouseMove_( self, dx, dy ) :
		if not self.canScroll_ : return False
		if dx == 0 : return True
		if dx > 0 and self.mousePos[0] < self.mouseSit_ : return True
		if dx < 0 and self.mousePos[0] > self.mouseSit_ : return True
		self.pyBinder.onMoveBarSlide__( dx )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		"""
		rows, cols = stMode
		def getMapping( size ) :
			cmapping = util.getStateMapping( size, stMode, ( 0 / cols + 1, 0 % cols + 1 )  )
			hmapping = util.getStateMapping( size, stMode, ( 1 / cols + 1, 1 % cols + 1 ) )
			pmapping = util.getStateMapping( size, stMode, ( 2 / cols + 1, 2 % cols + 1 ) )
			dmapping = util.getStateMapping( size, stMode, ( 3 / cols + 1, 3 % cols + 1 ) )
			return cmapping, hmapping, pmapping, dmapping

		moveBar = self.getGui()
		lmappings = getMapping( moveBar.elements['frm_l'].size )
		rmappings = getMapping( moveBar.elements['frm_r'].size )
		cbgtexture = self.__textureFolder + "/movebar_cbg.dds"
		hbgtexture = self.__textureFolder + "/movebar_hbg.dds"
		pbgtexture = self.__textureFolder + "/movebar_pbg.dds"

		self.states_[UIState.COMMON] = lmappings[0], cbgtexture, rmappings[0]
		self.states_[UIState.HIGHLIGHT] = lmappings[1], hbgtexture, rmappings[1]
		self.states_[UIState.PRESSED] = lmappings[2], pbgtexture, rmappings[2]

		self.setState( UIState.COMMON )

	def setState( self, state ) :
		"""
		设置状态
		"""
		MoveBar.setState( self, state )
		lmapping, bgTexture, rmapping = self.states_[state]
		bar = self.getGui()
		bar.elements['frm_l'] = lmapping
		bar.elements['frm_r'] = rmapping
		bar.elements['frm_bg'].texture = bgTexture


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		HFrameEx._setWidth( self, max( self.minLength_, width ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	start = property( MoveBar._getLeft, MoveBar._setLeft )
	end = property( MoveBar._getRight, MoveBar._setRight )
	length = property( MoveBar._getWidth, _setWidth )
	width = property( MoveBar._getWidth, _setWidth )


# --------------------------------------------------------------------
# implement vertical slot class
# --------------------------------------------------------------------
class _VSlot( Control ) :
	def __init__( self, slot ) :
		Control.__init__( self, slot )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMouseSit( self ) :
		return self.mousePos[1]

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	mouseSit = property( _getMouseSit )
	length = property( Control._getHeight, Control._setHeight )


# --------------------------------------------------------------------
# implement horizontal slot class
# --------------------------------------------------------------------
class _HSlot( Control ) :
	def __init__( self, slot ) :
		Control.__init__( self, slot )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMouseSit( self ) :
		return self.mousePos[0]

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	mouseSit = property( _getMouseSit )
	length = property( Control._getWidth, Control._setWidth )
