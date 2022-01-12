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

		self.__pyTestUI = None											# Ҫ������ɫ�� UI
		self.__textBG = None											# ���Ҫ���Ե����ı�����������ı��ı� UI

	def __initialize( self, wnd ) :
		self.fcTester_ = wnd.fcTester									# ǰ��ɫ��ɫ���԰�
		self.bcTester_ = wnd.bcTester									# ����ɫ��ɫ���԰�

		self.pyRBFColor_ = RadioButton( wnd.rbFColor )					# ǰ��ɫ����ѡ��
		self.pyRBBColor_ = RadioButton( wnd.rbBColor )					# ����ɫ����ѡ��
		self.pyCheckerGroup_ = CheckerGroup()
		self.pyCheckerGroup_.addChecker( self.pyRBFColor_ )
		self.pyCheckerGroup_.addChecker( self.pyRBBColor_ )
		self.pyCheckerGroup_.onCheckChanged.bind( self.onRBCheckChanged_ )

		self.pyBarR_ = HTrackBar( wnd.barR )							# ��ɫ��ɫ������
		self.pyBarG_ = HTrackBar( wnd.barG )							# ��ɫ��ɫ������
		self.pyBarB_ = HTrackBar( wnd.barB )							# ��ɫ��ɫ������
		self.pyBarA_ = HTrackBar( wnd.barA )							# ��ɫ��ɫ������

		self.pyTBR_ = TextBox( wnd.tbR )								# ��ɫ��ɫֵ�����
		self.pyTBG_ = TextBox( wnd.tbG )								# ��ɫ��ɫֵ�����
		self.pyTBB_ = TextBox( wnd.tbB )								# ��ɫ��ɫֵ�����
		self.pyTBA_ = TextBox( wnd.tbA )								# ��ɫ��ɫֵ�����

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
		��ʾʱ����ʼ����Ӧ�ؼ�
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
			self.pyCBStroke_.checked = hasattr( pyUI.getGui(), "stroker" )	# �Ƿ������
			self.pyCBStroke_.onCheckChanged.unshield()

	# -------------------------------------------------
	def __resetTester( self ) :
		"""
		������ɫ���԰���ɫ
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
		������ɫ���Ƹ˵�λ��
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
		ǰ��ɫ������ɫ֮����л�ʱ������
		"""
		self.__resetControlers()

	def onColorBarSlide_( self, pyTrackBar, value ) :
		"""
		��ɫ��������ʱ������
		"""
		pyTextBox = self.pyBars_[pyTrackBar]
		pyTextBox.onTextChanged.shield()
		pyTextBox.text = "%i" % ( pyTrackBar.value * 255 )
		pyTextBox.onTextChanged.unshield()
		self.__resetTester()

	def onTBColorTextChanged_( self, pyTextBox ) :
		"""
		��ɫֵ�ı�ʱ������
		"""
		pyTrackBar = self.pyTextBoxs_[pyTextBox]
		pyTrackBar.onSlide.shield()
		pyTrackBar.value = int( pyTextBox.text ) / 255.0
		pyTrackBar.onSlide.unshield()
		self.__resetTester()

	# ---------------------------------------
	def onStrokeChanged_( self, checked ) :
		"""
		�Ƿ����
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
		��ȡ���ߵ���������
		"""
		return "�ı���ɫ������"

	# -------------------------------------------------
	def getHitUIs( self, pyRoot, mousePos ) :
		"""
		�ṩһ�� UI �б��û�ѡ��pyRoot �������е����ϲ��Ǹ� UI
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
		�û�ѡȡ��ĳ�� UI��pyRoot �������е����ϲ��Ǹ� UI
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
		��ʾ����
		"""
		if pyUI is None :
			# "���ǿɲ��Ե��ı���ǩ�����������һ���ı���"
			showMessage( 0x0be1, "", MB_OK )
		else :
			self.__assign( pyUI )
			self.pyRBFColor_.checked = True
			Window.show( self )

	def hide( self ) :
		"""
		���ع���
		"""
		Window.hide( self )
		self.__pyTestUI = None
		self.__textBG = None
