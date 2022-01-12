# -*- coding: gb18030 -*-
#
# $Id: ProgressBar.py,v 1.18 2008-08-06 03:09:01 huangyongwei Exp $

"""
implement progressbar class
2005/05/18 : writen by huangyongwei
"""


import sys
import weakref
from guis import *
from guis.common.Frame import HFrame
from Control import Control

# --------------------------------------------------------------------
# implement horizontal progress bar
# --------------------------------------------------------------------
"""
composing :
	GUI.Simple
		-- clipper ( GUI.ClipShader )
"""

class HProgressBar( Control ) :
	def __init__( self, pbar = None, pyBinder = None ) :
		Control.__init__( self, pbar, pyBinder )
		self.__initialize( pbar )

		self.__value = self.currValue					# 当前设置的进度值
		self.__clipInterval = 0.001						# 递进的时间速度（即多长时间截取一次）
		self.__speed = 0.0								# 递进的位移速度
		self.__clipCBID = 0								# callback ID

	def subclass( self, pbar, pyBinder = None ) :
		Control.subclass( self, pbar, pyBinder )
		self.__initialize( pbar )
		return self

	def __initialize( self, pbar ) :
		if pbar is None : return
		self.__clipper = pbar.clipper


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onProgressChanged = self.createEvent_( "onProgressChanged" )
		self.__onCurrentValueChanged = self.createEvent_( "onCurrentValueChanged" )

	@property
	def onProgressChanged( self ) :
		return self.__onProgressChanged

	@property
	def onCurrentValueChanged( self ) :
		return self.__onCurrentValueChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cycleClip( self, currValue ) :
		if self.__speed <= 0 :												# 如果裁切速度小于或等于 0
			currValue = self.__value										# 则裁切瞬间裁切
		elif self.__value > currValue :										# 渐增
			currValue += self.__speed										# 当前实际值加上速度值
			currValue = min( self.__value, currValue )						# 控制当前实际值小于新值
		else :																# 渐减
			currValue -= self.__speed										# 当前实际之减去速度值
			currValue = max( self.__value, currValue )						# 控制当前实际值大于新值
		self.__clipper.value = currValue									# 设置 shader 的值
		self.onCurrProgressChanged_( currValue )							# 触发实际进度改变事件
		if currValue != self.__value :										# 如果当前实际值还不等于新设置的值
			func = Functor( self.__cycleClip, currValue )					# 则继续裁切
			self.__clipCBID = BigWorld.callback( self.__clipInterval, func )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onPorgressChanged_( self, value ) :
		"""
		进度值改变时被调用
		"""
		self.onProgressChanged( value )

	def onCurrProgressChanged_( self, value ) :
		"""
		实时进度值改变时被调用
		"""
		self.onCurrentValueChanged( value )

	def onDisable( self ) :
		"""
		无效时被调用
		"""
		self.materialFX = "BLEND"


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self, value = 0 ) :
		"""
		快速设置进度值
		@type			value : float
		@param			value : new value
		@return				  : None
		"""
		value = min( 1, value )
		value = max( 0, value )
		BigWorld.cancelCallback( self.__clipCBID )
		changed = self.__value != value
		self.__value = value
		self.__clipper.value = value
		self.__clipper.reset()
		if changed :
			self.onCurrProgressChanged_( value )
			self.onPorgressChanged_( value )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getClipMode( self ) :
		return self.__clipper.mode

	def _setClipMode( self, mode ) :
		self.__clipper.mode = mode

	# -------------------------------------------------
	def _getValue( self ) :
		return self.__value

	def _setValue( self, value ) :
		value = min( value, 1.0 )						# 限制值不能大于 1.0
		value = max( 0, value )							# 限制值不能小于 0.0
		oldValue = self.__value							# 保存旧值
		if oldValue == value : return					# 如果要设置的值等于当前值，则返回
		BigWorld.cancelCallback( self.__clipCBID )		# 如果当前正在裁切，则停止当前的裁切动作
		self.__value = value							# 设置新值
		self.__cycleClip( oldValue )					# 开始裁切
		self.onPorgressChanged_( value )				# 触发进度改变事件

	# ---------------------------------------
	def _getCurrValue( self ) :
		return self.__clipper.value

	# ---------------------------------------
	def _getSpeed( self ) :
		return self.__speed * 100

	def _setSpeed( self, value ) :
		speed = max( 0, value )
		self.__speed = speed / 100.0


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	clipMode = property( _getClipMode, _setClipMode )				# 获取/设置进度方向："LEFT", "RIGHT"
	value = property( _getValue, _setValue )						# 获取/设置进度值，范围为 0～1
	currValue = property( _getCurrValue )							# 获取当前的真实进度值（因为进度有可能是渐进的）
	speed = property( _getSpeed, _setSpeed )						# 渐进速度，必须大于 0，该值越大，其渐进速度越快


# --------------------------------------------------------------------
# implement horizontal frame progress bar
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
		-- l ( GUI.Simple )
		-- r ( GUI.Simple )
		-- bg ( GUI.Simple )
"""

class HFProgressBar( HFrame, Control ) :
	def __init__( self, pb = None, pyBinder = None ) :
		HFrame.__init__( self, pb )
		Control.__init__( self, pb, pyBinder )
		self.__width = HFrame._getWidth( self )				# 宽度
		self.__value = self.currValue						# 进度值
		self.__clipInterval = 0.001							# 渐进时，进度的单位时间间隔
		self.__speed = 0.0									# 渐进速度
		self.__clipCBID = 0									# callback ID


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onProgressChanged = self.createEvent_( "onProgressChanged" )
		self.__onCurrentValueChanged = self.createEvent_( "onCurrentValueChanged" )

	@property
	def onProgressChanged( self ) :
		return self.__onProgressChanged

	@property
	def onCurrentValueChanged( self ) :
		return self.__onCurrentValueChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cycleClip( self, currValue ) :
		if self.__speed <= 0 :												# 如果裁切速度小于或等于 0
			currValue = self.__value										# 则裁切瞬间裁切
		elif self.__value > currValue :										# 渐增
			currValue += self.__speed										# 当前实际值加上速度值
			currValue = min( self.__value, currValue )						# 控制当前实际值小于新值
		else :																# 渐减
			currValue -= self.__speed										# 当前实际之减去速度值
			currValue = max( self.__value, currValue )						# 控制当前实际值大于新值
		HFrame._setWidth( self, self.width * currValue )					# 设置宽度值的值
		self.onCurrProgressChanged_( currValue )							# 触发实际进度改变事件
		if currValue != self.__value :										# 如果当前实际值还不等于新设置的值
			func = Functor( self.__cycleClip, currValue )					# 则继续裁切
			self.__clipCBID = BigWorld.callback( self.__clipInterval, func )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onPorgressChanged_( self, value ) :
		"""
		进度值改变时被调用
		"""
		self.onProgressChanged( value )

	def onCurrProgressChanged_( self, value ) :
		"""
		实时进度值改变时被调用
		"""
		self.onCurrentValueChanged( value )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self, value = 0 ) :
		value = min( 1.0, value )
		value = max( value, 0 )
		BigWorld.cancelCallback( self.__clipCBID )
		changed = self.__value != value
		self.__value = value
		HFrame._setWidth( self, self.width * value )
		if changed :
			self.onCurrProgressChanged_( value )
			self.onPorgressChanged_( value )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getValue( self ) :
		return self.__value

	def _setValue( self, value ) :
		value = min( value, 1.0 )						# 限制值不能大于 1.0
		value = max( 0, value )							# 限制值不能小于 0.0
		oldValue = self.__value							# 保存旧值
		if oldValue == value : return					# 如果要设置的值等于当前值，则返回
		BigWorld.cancelCallback( self.__clipCBID )		# 如果当前正在裁切，则停止当前的裁切动作
		self.__value = value							# 设置新值
		self.__cycleClip( oldValue )					# 开始裁切
		self.onPorgressChanged_( value )				# 触发进度改变事件

	def _getCurrValue( self ) :
		if self.width <= 0 : return 0
		return HFrame._getWidth( self ) / self.width

	# ---------------------------------------
	def _getSpeed( self ) :
		return self.__speed * 100

	def _setSpeed( self, value ) :
		speed = max( 0, value )
		self.__speed = speed / 100.0

	# -------------------------------------------------
	def _getWidth( self ) :
		return self.__width

	def _setWidth( self, width ) :
		self.__width = width
		HFrame._setWidth( self, width * self.value )

	# -------------------------------------------------
	def _getRWidth( self ) :
		return s_util.toRXMeasure( self.__width )

	def _setRWidth( self, width ) :
		self.width = s_util.toPXMeasure( width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	value = property( _getValue, _setValue )							# 获取/设置进度值
	currValue = property( _getCurrValue )								# 获取当前表现值（因为有可能是渐进的）
	speed = property( _getSpeed, _setSpeed )							# 渐进速度，必须大于 0，该值越大，其渐进速度越快
	width = property( _getWidth, _setWidth )							# 获取/设置像素坐标宽度
	r_width = property( _getRWidth, _setRWidth )						# 获取/设置相对坐标宽度
