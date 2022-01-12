# -*- coding: utf-8 -*-
from guis import *
import weakref
from guis.UIFixer import hfUILoader
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.tooluis.infotip.TipsArea import TipsArea
from cscustom import Rect
from HelpTipsSetting import helpTipsSetting
from guis.controls.StaticText import StaticText
import math

# 箭头样式定义
STYLE_NONE	= 0
STYLE_UP = 1
STYLE_DOWN = 2
STYLE_LEFT = 3
STYLE_RIGHT = 4

arrowPath = "guis/tooluis/helptips/arrow.gui"

rotatesMap = { STYLE_UP: 0, STYLE_DOWN: math.pi, STYLE_LEFT: math.pi*1.5, STYLE_RIGHT: math.pi/2 }

class ArrowTip( RootGUI ):
	"""
	箭头指示
	"""
	__cg_pyArrows = {}

	def __init__( self ):
		arrow = hfUILoader.load( arrowPath )
		RootGUI.__init__( self, arrow )
		self.addToMgr()

		self.focus = False
		self.moveFocus = False
		self.escHide_ 		 = False

		self.__mapID = -1
		self.__pyBinder = None
		self.__style = None					# 窗口样式
		self.__vsDetectCBID = 0

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def dispose( self ) :
		BigWorld.cancelCallback( self.__vsDetectCBID )
		self.__vsDetectCBID = 0
		if self.__mapID in self.__cg_pyArrows :
			self.__cg_pyArrows.pop( self.__mapID )
			self.__mapID = -1
		self.pyTipsArea_.dispose()
		if hasattr( self, "pyText_" ):
			self.pyText_.dispose()
		RootGUI.dispose( self )

	def __del__( self ) :
		self.pyTipsArea_.dispose()
		if hasattr( self, "pyText_" ):
			self.pyText_.dispose()
		RootGUI.__del__( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __calcStyle( location ) :
		"""
		根据描述区域，计算应该使用的提示框样式
		"""
		x, y = location
		scw, sch = BigWorld.screenSize()
		hscw, hsch = scw * 0.5, sch * 0.5
		if x < hscw :
			if y < hsch :
				return STYLE_RIGHT
			else :
				return STYLE_UP
		else :
			if y < hsch :
				return STYLE_LEFT
			else :
				return STYLE_DOWN

	@staticmethod
	def __createArrow( style, location, bound, text = "" ) :
		"""
		构建各种样式的窗口
		"""
		pyArrow = ArrowTip()										# 创建一个提示窗口
		pyArrow.__style = style
		pyArrow.pyTipsArea_ = TipsArea( location, bound )
		if text != "":
			pyArrow.pyText_ = StaticText()
			pyArrow.pyText_.text = text
			pyArrow.pyText_.visible = False
			pyArrow.pyText_.gui.position.z = 0.3
			GUI.addRoot( pyArrow.pyText_.gui )

		arrow = pyArrow.gui
		rotate = rotatesMap.get( style, 0 )
		util.rotateGui( arrow, rotate )
		return pyArrow

	# -------------------------------------------------
	
	def __relocateText( self ):
		"""
		计算文字位置
		"""
		if hasattr( self, "pyText_" ):
			if self.__style == STYLE_UP:
				self.pyText_.h_anchor = "CENTER"
				self.pyText_.center = self.center
				self.pyText_.top = self.bottom
			elif self.__style == STYLE_DOWN:
				self.pyText_.h_anchor = "CENTER"
				self.pyText_.center = self.center
				self.pyText_.bottom = self.top
			elif self.__style == STYLE_LEFT:
				self.pyText_.h_anchor = "RIGHT"
				self.pyText_.left = self.right
				self.pyText_.middle = self.middle
			elif self.__style == STYLE_RIGHT:
				self.pyText_.h_anchor = "LEFT"
				self.pyText_.right = self.left
				self.pyText_.middle = self.middle
		
	
	def __relocate( self, location ) :
		"""
		计算箭头位置
		"""
		pointIn = 0.25
		self.pyTipsArea_.relocate( location )
		style = self.__style
		bound = self.pyTipsArea_.bound
		x, y = location
		x += bound.minX
		y += bound.minY
		if style == STYLE_UP:							# 向上
			x += bound.width * 0.5
			y += bound.height
			self.center = x
			self.top = y
		elif style == STYLE_DOWN:						# 向下
			x += bound.width * 0.5
			self.center = x
			self.bottom = y
		elif style == STYLE_LEFT:						# 向左
			y += bound.height*0.5
			x += bound.width
			self.left = x
			self.middle = y
		elif style == STYLE_RIGHT:						# 向右
			y += bound.height * 0.5
			self.right = x
			self.middle = y

	# -------------------------------------------------
	def __visibleDetect( self ) :
		if self.__pyBinder is None or \
			self.__pyBinder() is None or \
			not self.__pyBinder().rvisible :
				self.dispose()
		else :
			self.__vsDetectCBID = BigWorld.callback( 1.0, self.__visibleDetect )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventName, oldRso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		pyBinder = self.__pyBinder
		if pyBinder and pyBinder() :
			self.__relocate( pyBinder().posToScreen )
			self.__relocateText()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, tipid, pyBinder, unshowFrame ) :
		if pyBinder: #and pyBinder != self.__pyBinder
			self.__pyBinder = weakref.ref( pyBinder )
			self.__vsDetectCBID = BigWorld.callback( 1.0, self.__visibleDetect )
		self.__mapID = tipid
		if not unshowFrame :
			self.pyTipsArea_.show( pyBinder )
		if hasattr( self, "pyText_" ):
			self.pyText_.visible = True
		RootGUI.show( self, pyBinder )

	def hide( self ) :
		RootGUI.hide( self )
		if hasattr( self, "pyText_" ):
			self.pyText_.visible = False
		self.dispose()

	def relocate( self, location = None ) :
		if location is None :
			pyBinder = self.__pyBinder
			if pyBinder and pyBinder() :
				location = pyBinder().posToScreen
			else :
				raise TypeError( "argument location must be a tuple or Vector2!" )
		self.__relocate( location )
		self.__relocateText()

	# -------------------------------------------------
	@classmethod
	def showTips( SELF, tipid, pyBinder = None, bound = None ) :
		"""
		显示文本
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		@type			pyBinder : instance of GUIBaseObject
		@param			pyBinder : 要提示的控件：
									如果不为 None，则红色边框的位置相对 pyBinder 的位置
									如果为 None，则红色边框的位置相对屏幕的位置
		@type			bound	 : cscustom::Rect
		@param			bound	 : 圈起来的红色指示边框，如果为 None，则使用配置中指定的区域
		@rtype					 : bool
		@param					 : 提示成功，则返回 True
		"""
		if tipid in SELF.__cg_pyArrows : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		if not tipsInfo : return False										# 配置中不存在该提示 ID
		pyArrow = SELF.buildArrowByInfo( tipsInfo, pyBinder, bound )
		pyArrow.show( tipid, pyBinder, tipsInfo.unframe )
		SELF.__cg_pyArrows[tipid] = pyArrow
		return True

	@classmethod
	def hideTips( SELF, tipid ) :
		"""
		隐藏提示窗口
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		"""
		pyArrow = SELF.__cg_pyArrows.get( tipid, None )
		if pyArrow :
			pyArrow.hide()

	@classmethod
	def moveTips( SELF, tipid, location = None ) :
		"""
		移动提示窗口
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		@type			location : tuple
		@param			location : 指示区域位置，如果为 None，则以 PyBinder 的左上角为指示区域位置
		"""
		pyArrow = SELF.__cg_pyArrows.get( tipid, None )
		if not pyArrow : return
		pyArrow.relocate( location )

	@classmethod
	def buildArrowByInfo( SELF, tipsInfo, pyBinder = None, bound = None ) :
		"""
		显示文本
		@type			tipsInfo : instance of TipsInfo
		@param			tipsInfo : HelpTipsSetting中的类实例
		@type			pyBinder : instance of GUIBaseObject
		@param			pyBinder : 要提示的控件：
									如果不为 None，则红色边框的位置相对 pyBinder 的位置
									如果为 None，则红色边框的位置相对屏幕的位置
		@type			bound	 : cscustom::Rect
		@param			bound	 : 圈起来的红色指示边框，如果为 None，则使用配置中指定的区域
		@rtype					 : bool
		@param					 : 提示成功，则返回 True
		"""
		location = 0, 0														# 默认红边框位置相对屏幕
		if pyBinder :														# 如果有所属控件
			location = pyBinder.posToScreen									# 则红边框位置相对所属控件的左上角
			if bound is None :												# 如果没有指定指示区域
				bound = tipsInfo.bound										# 则使用配置中的指示区域
				if bound.width == 0 :										# 如果配置中也没指定指示区域
					bound = Rect( ( 0, 0 ), pyBinder.size )					# 则使用 pyBinder 的外接矩形作为指示区域
		elif bound :														# 没有所属控件
			location = bound.location										# 则位置相对屏幕
			bound.updateLocation( 0, 0 )
		else :
			raise TypeError( "one of argument 'pyBinder' and 'bound' must be not None!" )

		direct = tipsInfo.direct
		text = tipsInfo.text
		if direct == STYLE_NONE:
			direct = SELF.__calcStyle( location )							# 如果配置中没有指定窗口样式，则程序自动选择窗口样式
		pyArrow = SELF.__createArrow( direct, location, bound, text )	# 根据样式构建窗口风格
		pyArrow.__relocate( location )										# 根据红色边框
		pyArrow.__relocateText()
		return pyArrow

