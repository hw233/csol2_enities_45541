# -*- coding: gb18030 -*-
#
# $Id: PushButton.py,v 1.3 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement button class。
-- 2008/06/18 : writen by huangyongwei
"""
"""
composing :
	GUI.XXX

or
	GUI.Window
		-- lbText：GUI.Text( 可以没有 )
"""


from guis import *
from Button import Button

class PushButton( Button ) :
	"""
	鼠标左键点击一下则按下，重复点击一下则提起的按钮
	"""
	def __init__( self, button = None, pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		self.__initialize( button )						# 初始化
		self.__pushed = False							# 是否处于按下状态

	def subclass( self, button, pyBinder = None ) :
		Button.subclass( self, button, pyBinder )
		self.__initialize( button )
		return self

	def __del__( self ) :
		Button.__del__( self )
		if Debug.output_del_Button :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, button ) :
		pass


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Button.generateEvents_( self )
		self.__onPushed = self.createEvent_( "onPushed" )			# 当按下时触发
		self.__onRaised = self.createEvent_( "onRaised" )			# 当弹起时触发

	@property
	def onPushed( self ) :
		"""
		当按下时触发
		"""
		return self.__onPushed

	@property
	def onRaised( self ) :
		"""
		当弹起时触发
		"""
		return self.__onRaised


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __push( self ) :
		"""
		设置为选中状态
		"""
		if self.pushed : return
		self.__pushed = True
		self.setState( UIState.PRESSED )
		self.onPushed()

	def __raise( self ) :
		"""
		取消选中
		"""
		if not self.pushed : return
		self.__pushed = False
		self.setState( UIState.COMMON )
		self.onRaised()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseUp_( self, mods ) :
		Button.onLMouseUp_( self, mods )
		if self.enable and self.pushed :
			self.setState( UIState.PRESSED )
		return True

	# ---------------------------------------
	def onLClick_( self, mods ) :
		Button.onLClick_( self, mods )
		if self.isMouseHit() :
			self.pushed = not self.pushed
		return True

	# ---------------------------------------
	def onMouseEnter_( self ) :
		Button.onMouseEnter_( self )
		if self.pushed :
			self.setState( UIState.PRESSED )
		else :
			self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		Button.onMouseLeave_( self )
		if self.pushed :
			self.setState( UIState.PRESSED )
		else :
			self.setState( UIState.COMMON )
		return True

	# ---------------------------------------
	def onEnable_( self ) :
		Button.onEnable_( self )
		if self.pushed :
			self.setState( UIState.PRESSED )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPushed( self ) :
		return self.__pushed

	def _setPushed( self, pushed ) :
		if pushed : self.__push()
		else : self.__raise()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pushed = property( _getPushed, _setPushed )										# 设置选中状态
