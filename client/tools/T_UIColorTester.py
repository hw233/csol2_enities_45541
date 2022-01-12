# -*- coding: gb18030 -*-
#
# $Id: T_SoundSetter.py,v 1.5 2008-08-30 09:12:53 huangyongwei Exp $
#
"""
implement text color setter
2009/05/23: created by huangyongwei
"""

from guis import *
from guis.common.Window import Window
from guis.controls.RadioButton import RadioButton
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.TextBox import TextBox
from guis.controls.TrackBar import HTrackBar
from guis.controls.StaticText import StaticText
from guis.controls.CheckBox import CheckBox
from guis.controls.ListItem import ListItem
from guis.controls.ODListPanel import ViewItem
from tools import toolMgr
from ITool import ITool

class UIColorTester( Window, ITool ) :
	def __init__( self ) :
		toolMgr.addTool( self )
		wnd = GUI.load( "guis/clienttools/uicolortester/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		ITool.__init__( self )
		self.posZSegment_ = ZSegs.L2
		self.addToMgr()
		self.__initialize( wnd )

		self.__pyTestUI = None											# 要测试颜色的 UI
		self.__textBG = None											# 如果要测试的是文本，则这个是文本的背 UI

	def __initialize( self, wnd ) :
		self.fcTester_ = wnd.fcTester									# 前景色颜色测试板
		self.bcTester_ = wnd.bcTester									# 背景色颜色测试板

		self.pyRBFColor_ = RadioButton( wnd.rbFColor )					# 前景色设置选择
		self.pyRBBColor_ = RadioButton( wnd.rbBColor )					# 背景色设置选择
		self.pyCheckerGroup_ = CheckerGroup()
		self.pyCheckerGroup_.addChecker( self.pyRBFColor_ )
		self.pyCheckerGroup_.addChecker( self.pyRBBColor_ )
		self.pyCheckerGroup_.onCheckChanged.bind( self.onRBCheckChanged_ )

		self.pyBarR_ = HTrackBar( wnd.barR )							# 红色颜色设置条
		self.pyBarG_ = HTrackBar( wnd.barG )							# 绿色颜色设置条
		self.pyBarB_ = HTrackBar( wnd.barB )							# 蓝色颜色设置条
		self.pyBarA_ = HTrackBar( wnd.barA )							# 蓝色颜色设置条

		self.pyTBR_ = TextBox( wnd.tbR )								# 红色颜色值输入框
		self.pyTBG_ = TextBox( wnd.tbG )								# 绿色颜色值输入框
		self.pyTBB_ = TextBox( wnd.tbB )								# 蓝色颜色值输入框
		self.pyTBA_ = TextBox( wnd.tbA )								# 蓝色颜色值输入框

		self.pyBars_ = {}
		self.pyBars_[self.pyBarR_] = self.pyTBR_
		self.pyBars_[self.pyBarG_] = self.pyTBG_
		self.pyBars_[self.pyBarB_] = self.pyTBB_
		self.pyBars_[self.pyBarA_] = self.pyTBA_
		for pyBar in self.pyBars_ :
			pyBar.stepCount = 255
			pyBar.onSlide.bind( self.onColorBarSlide_ )

		self.pyTextBoxs_ = {}
		self.pyTextBoxs_[self.pyTBR_] = self.pyBarR_
		self.pyTextBoxs_[self.pyTBG_] = self.pyBarG_
		self.pyTextBoxs_[self.pyTBB_] = self.pyBarB_
		self.pyTextBoxs_[self.pyTBA_] = self.pyBarA_
		for pyTextBox in self.pyTextBoxs_ :
			pyTextBox.inputMode = InputMode.INTEGER
			pyTextBox.filterChars = ['-']
			pyTextBox.maxLength = 3
			pyTextBox.text = '0'
			pyTextBox.onTextChanged.bind( self.onTBColorTextChanged_ )

		self.pyCBStroke_ = CheckBox( wnd.cbStroke )
		self.pyCBStroke_.checked = False
		self.pyCBStroke_.onCheckChanged.bind( self.onStrokeChanged_ )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __assign( self, pyUI ) :
		"""
		显示时，初始化相应控件
		"""
		self.__pyTestUI = pyUI
		r, g, b, a = pyUI.color
		self.pyTBR_.text = str( int( r ) )
		self.pyTBG_.text = str( int( g ) )
		self.pyTBB_.text = str( int( b ) )
		self.pyTBA_.text = str( int( a ) )

		self.pyCBStroke_.onCheckChanged.shield()
		self.pyCBStroke_.checked = False
		self.pyCBStroke_.onCheckChanged.unshield()
		self.pyCBStroke_.enable = False
		self.pyRBBColor_.enable = False
		if isinstance( pyUI, StaticText ) :
			pyBG = self.__pyTestUI.pyParent
			if pyBG :
				self.pyRBBColor_.enable = True
				self.__textBG = pyBG.getGui()
				self.bcTester_.textureName = self.__textBG.textureName
				self.bcTester_.mapping = self.__textBG.mapping
				self.bcTester_.colour = self.__textBG.colour
			else :
				self.__textBG = None
				self.bcTester_.textureName = ''

			self.pyCBStroke_.enable = True
			self.pyCBStroke_.onCheckChanged.shield()
			self.pyCBStroke_.checked = hasattr( pyUI.getGui(), "stroker" )	# 是否有描边
			self.pyCBStroke_.onCheckChanged.unshield()

	# -------------------------------------------------
	def __resetTester( self ) :
		"""
		设置颜色测试板颜色
		"""
		r = int( self.pyTBR_.text )
		g = int( self.pyTBG_.text )
		b = int( self.pyTBB_.text )
		a = int( self.pyTBA_.text )
		if self.pyRBFColor_.checked :
			self.fcTester_.colour = r, g, b, a
			self.__pyTestUI.color = r, g, b, a
		elif self.__textBG :
			self.bcTester_.colour = r, g, b, a
			self.__textBG.colour = r, g, b, a

	def __resetControlers( self ) :
		"""
		设置颜色控制杆的位置
		"""
		if self.pyRBFColor_.checked :
			r, g, b, a = self.fcTester_.colour
		else :
			r, g, b, a = self.bcTester_.colour
		self.pyTBR_.text = str( int( r ) )
		self.pyTBG_.text = str( int( g ) )
		self.pyTBB_.text = str( int( b ) )
		self.pyTBA_.text = str( int( a ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRBCheckChanged_( self, pyChecker ) :
		"""
		前景色，背景色之间的切换时被触发
		"""
		self.__resetControlers()

	def onColorBarSlide_( self, pyTrackBar, value ) :
		"""
		颜色滑条滑动时被触发
		"""
		pyTextBox = self.pyBars_[pyTrackBar]
		pyTextBox.onTextChanged.shield()
		pyTextBox.text = "%i" % ( pyTrackBar.value * 255 )
		pyTextBox.onTextChanged.unshield()
		self.__resetTester()

	def onTBColorTextChanged_( self, pyTextBox ) :
		"""
		颜色值改变时被触发
		"""
		pyTrackBar = self.pyTextBoxs_[pyTextBox]
		pyTrackBar.onSlide.shield()
		pyTrackBar.value = int( pyTextBox.text ) / 255.0
		pyTrackBar.onSlide.unshield()
		self.__resetTester()

	# ---------------------------------------
	def onStrokeChanged_( self, checked ) :
		"""
		是否描边
		"""
		staticText = self.__pyTestUI.getGui()
		if checked :
			s = GUI.FringeShader()
			s.gray = False
			s.colour = 0, 0, 0, 255
			staticText.addShader( s, "stroker" )
		else :
			staticText.delShader( staticText.stroker )


	# ----------------------------------------------------------------
	# virtual methods
	# ----------------------------------------------------------------
	def getCHName( self ) :
		"""
		获取工具的中文名称
		"""
		return "文本颜色测试器"

	# -------------------------------------------------
	def getHitUIs( self, pyRoot, mousePos ) :
		"""
		提供一组 UI 列表供用户选择，pyRoot 是鼠标击中的最上层那个 UI
		"""
		def doFunc( pyUI ) :
			if not pyUI.rvisible : return False, 0
			if not pyUI.hitTest( *mousePos ) : return False, 0
			return True, 1
		pyUIs = []
		for pyUI in util.postFindPyGui( pyRoot.getGui(), doFunc, True ) :
			if isinstance( pyUI, StaticText ) :
				name = "@->%s" % pyUI.text
			elif isinstance( pyUI, ListItem ) or \
				isinstance( pyUI, ViewItem ) :
					name = "@->%s" % pyUI.__class__.__name__
			else :
				name = pyUI.__class__.__name__
			pyUIs.append( ( name, pyUI ) )
		return pyUIs

	def getHitUI( self, pyRoot, mousePos ) :
		"""
		用户选取了某个 UI，pyRoot 是鼠标击中的最上层那个 UI
		"""
		pyUIs = []
		for name, pyUI in self.getHitUIs( pyRoot, mousePos ) :
			if isinstance( pyUI, StaticText ) or \
				isinstance( pyUI, ListItem ) or \
				isinstance( pyUI, ViewItem ) :
					pyUIs.append( pyUI )
		if len( pyUIs ) == 0 :
			return None
		return sorted( pyUIs, key = lambda i : i.__class__.__name__ )[0]

	def show( self, pyUI ) :
		"""
		显示工具
		"""
		if pyUI is None :
			# "不是可测试的文本标签（鼠标必须击中一段文本）"
			showMessage( 0x0be1, "", MB_OK )
		else :
			self.__assign( pyUI )
			self.pyRBFColor_.checked = True
			Window.show( self )

	def hide( self ) :
		"""
		隐藏工具
		"""
		Window.hide( self )
		self.__pyTestUI = None
		self.__textBG = None
