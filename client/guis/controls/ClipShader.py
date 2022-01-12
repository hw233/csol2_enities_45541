# -*- coding: gb18030 -*-
#
# $Id: ClipShader.py,v 1.8 2008-06-21 01:46:57 huangyongwei Exp $

"""
implement alpha shader class

2007/3/18 : writen by huangyongwei
"""
"""
composing :
	GUI.Window
		-- clipper ( GUI.ClipShader )
"""

from guis import *
from guis.common.PyGUI import PyGUI

class ClipShader( object ) :
	"""
	裁剪 Shader
	"""
	def __init__( self, gui ) :
		object.__init__( self )
		self.__initialize( gui )
		self.__clipMode = "RIGHT"								# 裁剪模式："LEFT"、"RIGHT"、"TOP"、"BOTTOM"
		self.__value = 1										# 裁剪默认值
		self.__speed = 1										# 裁剪速度

		self.__perClipValue = 1.0								# 临时变量，保存每一 tick 应该裁切的 value 值
		self.__clipCBID = 0										# 裁切的 callback ID

	def subclass( self, gui ) :
		self.__initialize( gui )
		return self

	def __del__( self ) :
		self.__stopClipping()
		self.__gui = None
		if Debug.output_del_ClipShader :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, gui ) :
		if isDebuged :
			assert gui.size[0] > 0 and gui.size[1] > 0, "the ui's size clip shader attach to must large than 0!"
		self.__gui = gui
		self.__defMapping = gui.mapping											# UI 的原始 mapping
		self.__defMapBound = util.getGuiMappingBound( gui.size, gui.mapping ) 	# UI 的原始 mapping Bound
		self.__defSize = tuple( gui.size )										# UI 的原始大小
		self.__defPos = s_util.getGuiPos( gui )									# UI 的原始位置
		self.__defRight = s_util.getGuiRight( gui )								# UI 的原始右距
		self.__defBottom = s_util.getGuiBottom( gui )							# UI 的原始底距

		self.__clipFuncs = {}											# 裁切函数
		self.__clipFuncs["LEFT"]	= RefEx( self.__leftClip )			# 裁切左边
		self.__clipFuncs["RIGHT"]	= RefEx( self.__rightClip )			# 裁切右边
		self.__clipFuncs["TOP"]		= RefEx( self.__topClip )			# 裁切上边
		self.__clipFuncs["BOTTOM"]	= RefEx( self.__bottomClip )		# 裁切下边


	# --------------------------------------------------------------------
	# private
	# --------------------------------------------------------------------
	def __stopClipping( self ) :
		"""
		停止当前的裁切
		"""
		BigWorld.cancelCallback( self.__clipCBID )				# 手动停止裁切
		self.__value = self.currValue							# 将 value 改为实际值

	# -------------------------------------------------
	def __leftClip( self, currValue ) :
		"""
		模式为左边的裁切
		"""
		value = currValue + self.__perClipValue					# 当前 tick 的 value
		if self.__perClipValue > 0 :							# 如果值在逐渐增大
			value = min( self.__value, value )					# 则，cuur 值不能大于所设置的值
		else :													# 否则
			value = max( self.__value, value )					# cuur 值不能小于所设置的值

		defWidth = self.__defSize[0]							# 原始宽度
		width = defWidth * value								# 当前 tick 应该设置的宽度
		self.__gui.width = width								# 设置为新的大小

		left, right, top, bottom = self.__defMapBound			# 原始 Mapping Bound
		defMWidth = right - left								# 原始 mapping width
		left += defMWidth * ( 1 - value )						# 新的 mapping 左距
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		s_util.setGuiRight( self.__gui, self.__defRight )		# 设置 UI 的位置（固定在右边）

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__leftClip, value ) )

	def __rightClip( self, currValue ) :
		"""
		模式为右边的裁切
		"""
		value = currValue + self.__perClipValue					# 当前 tick 的 value
		if self.__perClipValue > 0 :							# 如果值在逐渐增大
			value = min( self.__value, value )					# 则，cuur 值不能大于所设置的值
		else :													# 否则
			value = max( self.__value, value )					# cuur 值不能小于所设置的值

		defWidth = self.__defSize[0]							# 原始宽度
		width = defWidth * value								# 当前 tick 应该设置的宽度
		self.__gui.width = width								# 设置为新的大小

		left, right, top, bottom = self.__defMapBound			# 原始 Mapping Bound
		defMWidth = right - left								# 原始 mapping width
		right = left + defMWidth * value						# 新的 mapping 左距
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__rightClip, value ) )

	def __topClip( self, currValue ) :
		"""
		模式为上部的裁切
		"""
		value = currValue + self.__perClipValue					# 当前 tick 的 value
		if self.__perClipValue > 0 :							# 如果值在逐渐增大
			value = min( self.__value, value )					# 则，cuur 值不能大于所设置的值
		else :													# 否则
			value = max( self.__value, value )					# cuur 值不能小于所设置的值

		defHeight = self.__defSize[1]							# 原始高度
		height = defHeight * value								# 当前 tick 应该设置的宽度
		self.__gui.height = height								# 设置为新的大小

		left, right, top, bottom = self.__defMapBound			# 原始 Mapping Bound
		defMHeight = bottom - top								# 原始 mapping width
		top += defMHeight * ( 1 - value )						# 新的 mapping 左距
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		s_util.setGuiBottom( self.__gui, self.__defBottom )

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__topClip, value ) )

	def __bottomClip( self, currValue ) :
		"""
		模式为底部的裁切
		"""
		value = currValue + self.__perClipValue					# 当前 tick 的 value
		if self.__perClipValue > 0 :							# 如果值在逐渐增大
			value = min( self.__value, value )					# 则，cuur 值不能大于所设置的值
		else :													# 否则
			value = max( self.__value, value )					# cuur 值不能小于所设置的值

		defHeight = self.__defSize[1]							# 原始高度
		height = defHeight * value								# 当前 tick 应该设置的宽度
		self.__gui.height = height								# 设置为新的大小

		left, right, top, bottom = self.__defMapBound			# 原始 Mapping Bound
		defMHeight = bottom - top								# 原始 mapping width
		bottom = top + defMHeight * value 						# 新的 mapping 左距
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__bottomClip, value ) )


	# --------------------------------------------------------------------
	# property methods
	# --------------------------------------------------------------------
	def _getGui( self ) :
		return self.__gui

	# -------------------------------------------------
	def _getClipMode( self ) :
		return self.__clipMode

	def _setClipMode( self, clipMode ) :
		if isDebuged :
			assert clipMode in self.__clipFuncs, "clip mode must be 'LEFT' or 'RIGHT' or 'TOP' or 'BOTTOM'"
		self.__gui.size = self.__defSize 						# 恢复原始大小
		self.__gui.mapping = self.__defMapping					# 恢复原始的 mapping
		s_util.setGuiPos( self.__gui, self.__defPos )			# 恢复原始位置
		self.__stopClipping()									# 如果正在裁切，则停止
		self.__clipMode = clipMode

	# -------------------------------------------------
	def _getValue( self ) :
		return self.__value

	def _setValue( self, value ) :
		value = min( 1.0, value )
		value = max( 0.0, value )
		if self.__value == value : return								# 如果设置的值与当前值一致，则返回
		self.__stopClipping()											# 如果正在执行上一次的裁切，则停止裁切
		self.__perClipValue = ( value - self.__value ) * self.__speed	# 保存每一 tick 应该裁切的 value 值
		oldValue = self.__value
		self.__value = value											# 设置新值
		self.__clipFuncs[self.__clipMode]()( oldValue )					# 调用裁切函数进行逐步裁切

	# ---------------------------------------
	def _getSpeed( self ) :
		return self.__speed

	def _setSpeed( self, speed ) :
		speed = max( 0.0, speed )
		if speed == 0.0 : speed = 1.0
		self.__speed = min( speed, 1.0 )

	# -------------------------------------------------
	def _getCurrValue( self ) :
		size = self.__gui.size
		if self.__clipMode == "LEFT" or self.__clipMode == "RIGHT" :
			return size[0] / self.__defSize[0]
		return size[1] / self.__defSize[1]


	# --------------------------------------------------------------------
	# properties
	# --------------------------------------------------------------------
	gui = property( _getGui )								# 获取被裁切的 UI
	clipMode = property( _getClipMode, _setClipMode )		# 裁切模式: "LEFT", "RIGHT", "TOP", "BOTTOM"
	value = property( _getValue, _setValue )				# 裁切比值：0～1.0
	speed = property( _getSpeed, _setSpeed )				# 裁切速度：0～1.0 ( 0 与 1.0 的效果都一样，都是瞬时到达裁切值 )
	currValue = property( _getCurrValue )					# 获取当前真实裁切值
