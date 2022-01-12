# -*- coding: gb18030 -*-

# 前身是FlashFlag。
# 重新实现了闪烁控件，由继承于Control改为继承于GUIBaseObject
# 默认情况下这类控件不接收消息。如果有需要接收消息的闪烁控件，
# 则可由此再继承出一个新的类。
# written by ganjinxing 2010-07-15

from guis import *
from guis.common.GUIBaseObject import GUIBaseObject


class AnimatedGUI( GUIBaseObject ) :

	def __init__( self, gui ) :
		GUIBaseObject.__init__( self, gui )

		self.__loopAmount = -1							# 循环闪烁多少次后自动停止(为负则无限循环)
		self.__loopSpeed = 1.0							# 每帧的时间（单位：秒）
		self.__loopCounter = 0							# 记录已循环多少次
		self.__frameAmount = 0							# 总共多少帧
		self.__frameIndex = 0							# 当前是第几帧
		self.__framesMapping = []						# 记录每一帧的mapping值
		self.__loopCBID = 0								# 循环timerID

	def __del__( self ) :
		if Debug.output_del_AnimatedGUI :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __loop( self ) :
		"""
		循环闪烁
		"""
		if self.__frameIndex >= self.__frameAmount :	# 循环了一圈
			loopAmount = self.__loopAmount
			if loopAmount > 0 :							# 如果设定了循环次数
				self.__loopCounter += 1
				if self.__loopCounter >= loopAmount :	# 循环次数已到
					self.reset_()						# 循环结束
					self.stopPlay_()
					return
			self.__frameIndex = 0						# 重新回到第一帧
		self.mapping = self.__framesMapping[self.__frameIndex]
		self.__frameIndex += 1
		self.__loopCBID = BigWorld.callback( self.__loopSpeed, self.__loop )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def stopPlay_( self ) :
		"""
		停止闪烁
		"""
		if self.__loopCBID :
			BigWorld.cancelCallback( self.__loopCBID )
			self.__loopCBID = 0
			
	def reset_( self ) :
		"""
		重设动画参数，
		"""
		self.__frameIndex = 0							# 重新回到第一帧
		self.__loopCounter = 0							# 重设循环计数
		self.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def playAnimation( self ) :
		"""
		播放动画，不提供手动结束播放的接口，需要初始化
		时首先设定好动画的播放次数及每帧的速度。
		"""
		self.stopPlay_()
		self.reset_()
		self.visible = True
		self.__loop()
		
	def initAnimation( self, loopAmount, frameAmount, mappingMode, orderStyle = "Z" ) :
		"""
		设置动画参数
		@param		loopAmount	: 循环次数（为负则无限循环）
		@type		loopAmount	: int
		@param		frameAmount : 每次循环的帧数
		@type		frameAmount : int
		@param		mappingMode : 贴图的mapping模式
		@type		mappingMode : tuple with two elements
		@param		orderStyple : mapping的顺序（“Z”或者“N”字形）
		@type		orderStyple : character of "Z" or "N"( in upper case )
		"""
		self.__loopAmount = loopAmount
		self.__frameAmount = frameAmount
		util.setGuiState( self.gui, mappingMode )
		uiSize = self.size
		row, col = mappingMode
		self.__framesMapping = []
		orderStyle = orderStyle.upper()
		if orderStyle == "Z" :
			for i in xrange( 1, row + 1 ) :
				for j in xrange( 1, col + 1 ) :
					if frameAmount <= 0 : return
					frameAmount -= 1
					mapping = util.getStateMapping( uiSize, mappingMode, ( i, j ) )
					self.__framesMapping.append( mapping )
		elif orderStyle == "N" :
			for j in xrange( 1, col + 1 ) :
				for i in xrange( 1, row + 1 ) :
					if frameAmount <= 0 : return
					frameAmount -= 1
					mapping = util.getStateMapping( uiSize, mappingMode, ( i, j ) )
					self.__framesMapping.append( mapping )
		else :
			ERROR_MSG( "Error order style: %s! orderStyle must be \"Z\" or \"N\"." % orderStyle )
		self.reset_()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getSpf( self ) :
		"""
		获取一帧的速度
		"""
		return self.__loopSpeed

	def _setSpf( self, spf ) :
		"""
		设置一帧的速度
		"""
		self.__loopSpeed = spf

	def _getCycle( self ) :
		"""
		获取周期
		"""
		return self.__loopSpeed * self.__frameAmount

	def _setCycle( self, cycle ) :
		"""
		设置周期
		"""
		self.__loopSpeed = float( cycle ) / self.__frameAmount


	spf = property( _getSpf, _setSpf )					# 获取/设置每帧的时间( second per frame )
	cycle = property( _getCycle, _setCycle )			# 获取/设置周期（循环一次的时间）
