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
# ��ȡ�ļ�Ŀ¼
# --------------------------------------------------------------------
def getFileFolder( texture ) :
	return "/".join( texture.split( "/" )[:-1] )


# --------------------------------------------------------------------
# implement vertical scroll bar class
# --------------------------------------------------------------------
class ScrollBar( Control ) :
	"""
	����������
	"""
	def __init__( self, sb, pySlot, pyMoveBar, pyBinder = None ) :
		Control.__init__( self, sb, pyBinder )
		self.mouseScrollFocus = True

		self.__scrollScale = 1									# �������������ĳ��ȱȣ�һ������ 1����Ϊ�����϶�����ߣ�
		self.__perScroll = 0.1									# ���һ�°�ť�����һ�������ֵĻ���ֵ
		self.__initialize( sb, pySlot, pyMoveBar )

		self.__cycleScrollCBID = 0								# һֱ�������������������������� callback ID

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
		self.pyMoveBar_ = pyMoveBar									# ������
		self.pyMoveBar_.onLMouseDown.bind( self.onLMouseDown_ )

		self.pySlot_ = pySlot										# ������
		self.pySlot_.focus = True									# ������������˲ʱ��������갴�µĵط�
		self.pySlot_.onLClick.bind( self.__onSlotClick )			# ���������ʱ��������˲ʱ������괦
		self.pySlot_.onLMouseDown.bind( self.onLMouseDown_ )
		self.pyIncBtn_ = Button( sb.incBtn )						# ��ֵ��ť
		self.pyIncBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyIncBtn_.onLMouseDown.bind( self.__onIncBtnMouseDown, True )
		self.pyIncBtn_.onLMouseDown.bind( self.onLMouseDown_, True )
		self.pyIncBtn_.onLMouseUp.bind( self.__onBtnMouseUp )
		self.pyDecBtn_ = Button( sb.decBtn )						# ��ֵ��ť
		self.pyDecBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyDecBtn_.onLMouseDown.bind( self.__onDecBtnMouseDown, True )
		self.pyDecBtn_.onLMouseDown.bind( self.onLMouseDown_, True )
		self.pyDecBtn_.onLMouseUp.bind( self.__onBtnMouseUp )

		self.scrollScale = 1										# Ĭ�ϻ��������� 1:1 ( �������������� )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
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
		��ȡ�������ʣ��߶�
		"""
		slotLength = self.pySlot_.length
		return slotLength - self.pyMoveBar_.length

	def __scroll( self, currLen ) :
		"""
		�ù���������ָ���ĸ߶�ֵ
		"""
		self.pyMoveBar_.start = currLen							# ���������ĵ�ֵ��λ��
		maxLen = self.__getMaxLength()
		value = 0
		if maxLen > 0 : value = currLen / maxLen
		self.onScroll( value )

	# -------------------------------------------------
	def __cycleIncScroll( self ) :
		"""
		���һֱ�����������ѭ����������
		"""
		if self.pyIncBtn_.isMouseHit() :						# ֻ����������ֵ��ť�Ŵ���
			self.incScroll()									# ��ֵ����
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :				# ֱ���������
			self.__cycleScrollCBID = BigWorld.callback( \
				0.1, self.__cycleIncScroll )					# ѭ����һ�ι���

	def __cycleDecScroll( self ) :
		"""
		���һֱ�����������ѭ����������
		"""
		if self.pyDecBtn_.isMouseHit() :						# ֻ�������м�ֵ��ť�Ŵ���
			self.decScroll()									# ��ֵ����
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :				# ֱ���������
			self.__cycleScrollCBID = BigWorld.callback( \
				0.1, self.__cycleDecScroll )					# ѭ����һ�ι���

	# -------------------------------------------------
	def __onIncBtnMouseDown( self ) :
		"""
		�����ֵ������ťʱ������
		"""
		self.incScroll()										# ��ֵ����
		self.__cycleScrollCBID = BigWorld.callback( \
			0.4, self.__cycleIncScroll )						# 0.5 ���ģ��ѭ�����

	def __onDecBtnMouseDown( self ) :
		"""
		�����ֵ������ťʱ������
		"""
		self.decScroll()										# ��ֵ����
		self.__cycleScrollCBID = BigWorld.callback( \
			0.4, self.__cycleDecScroll )						# 0.5 ���ģ��ѭ�����

	def __onBtnMouseUp( self ) :
		"""
		����ڰ�ť������ʱ������
		"""
		BigWorld.cancelCallback( self.__cycleScrollCBID )

	# ---------------------------------------
	def __onSlotClick( self ) :
		"""
		���������ʱ������
		"""
		maxLen = self.__getMaxLength()							# ��ȡ�������
		if maxLen <= 0 : return									# ��Ч����
		mstart = self.pySlot_.mouseSit							# ����ڹ������е�λ�ã������ˮƽ����Ϊ left������Ǵ�ֱ��Ϊ top��
		if mstart < self.pyMoveBar_.start :
			self.value = mstart / maxLen
		elif mstart > self.pyMoveBar_.end :
			self.value = ( mstart - self.pyMoveBar_.length ) / maxLen


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		��������Ϣ
		"""
		if dz < 0 : self.incScroll()
		else : self.decScroll()
		return True


	# ----------------------------------------------------------------
	# friend methods of the VMoveBar
	# ----------------------------------------------------------------
	def onMoveBarSlide__( self, inc ) :
		"""
		������������ʱ������
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
		���û�������״̬ mapping
		"""
		self.pyMoveBar_.setStatesMapping( mode )

	# -------------------------------------------------
	def incScroll( self, count = 1 ) :
		"""
		��ֵ����һ��( ���� )��λ
		"""
		if self.value > 1 - self.__perScroll :			
			self.value = 1
			self.onScroll( self.value )
			
		else :
			self.value += count * self.__perScroll

	def decScroll( self, count = 1 ) :
		"""
		��ֵ����һ��( ���� )��λ
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
		if scale == 1 and mbLen != slotLen :		# ����������̫���ˣ�����������Сֵ��С��
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
	scrollScale = property( _getScrollScale, _setScrollScale )	# ��ȡ/�������ݵ����߶� ���� ���Ӹ߶�( �������ض����ڻ���� 1 )
	value = property( _getValue, _setValue )					# ��ȡ/���õ�ǰ����ֵ( 0 ~ 1 ֮�� )
	perScroll = property( _getPerScroll, _setPerScroll ) 		# ��ȡ/���õ�λ����ֵ����������ϻ����°�ťʱ�Ĺ���ֵ��


# --------------------------------------------------------------------
# vertical scroll bar
# --------------------------------------------------------------------
"""
�� the move bar can be flexed
composing :
	GUI.Window
		-- upBtn ( gui of csui.controls.Button.Button )
		-- downBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
				-- t ( GUI.Simple )
				-- b ( GUI.Simple )
				-- bg ( GUI.Simple ) -- NOTE: bg.tiled = True

�� the move bar is fixed
composing :
	GUI.Window
		-- upBtn ( gui of csui.controls.Button.Button )
		-- downBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
"""

class VScrollBar( ScrollBar ) :
	"""
	��ֱ������
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
	width = property( ScrollBar._getWidth )					 	# ��ȡ���������
	height = property( ScrollBar._getHeight, _setHeight )		# ��ȡ/���ù������߶�


# --------------------------------------------------------------------
# horizontal scroll bar
# --------------------------------------------------------------------
"""
composing :
�� the move bar is flexible
	GUI.Window
		-- leftBtn ( gui of csui.controls.Button.Button )
		-- rightBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
				-- l ( GUI.Simple )
				-- r ( GUI.Simple )
				-- bg ( GUI.Simple ) -- NOTE: bg.tiled = True

�� the move bar is not flexible
	GUI.Window
		-- leftBtn ( gui of csui.controls.Button.Button )
		-- rightBtn ( gui of csui.controls.Button.Button )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Simple )
"""

class HScrollBar( ScrollBar ) :
	"""
	ˮƽ������
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
	width = property( ScrollBar._getWidth, _setWidth )			# ��ȡ/���ù��������
	height = property( ScrollBar._getHeight )					# ��ȡ/���ù������߶�


# --------------------------------------------------------------------
# implement move bar base class
# --------------------------------------------------------------------
class MoveBar( Control ) :
	"""
	����������
	"""
	__cc_min_length			= 16

	def __init__( self, moveBar, pyBinder ) :
		Control.__init__( self, moveBar, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.moveFocus = True

		self.minLength_ = self.__cc_min_length
		self.flexible_ = False							# �Ƿ��ǿ���������
		self.mouseSit_ = 0								# ��갴��ʱ��λ��
		self.canScroll_ = False							# �Ƿ��������

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
		����״̬ mapping
		"""
		if not self.flexible_ :
			self.mapping = self.states_[state]


# --------------------------------------------------------------------
# implement vertical move bar class
# --------------------------------------------------------------------
class VMoveBar( VFrame, MoveBar ) :
	"""
	��ֱ������
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
		����״̬ mapping
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
		����״̬
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
# implement vertical move bar class( ʹ���µ� GUI.TextureFrame )
# --------------------------------------------------------------------
class VMoveBarEx( VFrameEx, MoveBar ) :
	"""
	��ֱ������
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
		����״̬ mapping
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
		����״̬
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
	ˮƽ������
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
		����״̬ mapping
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
		����״̬
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
# implement horizontal move bar calss( ʹ���µ� TextureFrame ��� )
# --------------------------------------------------------------------
class HMoveBarEx( HFrameEx, MoveBar ) :
	"""
	ˮƽ������
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
		����״̬ mapping
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
		����״̬
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
