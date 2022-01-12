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

# ��ͷ��ʽ����
STYLE_NONE	= 0
STYLE_UP = 1
STYLE_DOWN = 2
STYLE_LEFT = 3
STYLE_RIGHT = 4

arrowPath = "guis/tooluis/helptips/arrow.gui"

rotatesMap = { STYLE_UP: 0, STYLE_DOWN: math.pi, STYLE_LEFT: math.pi*1.5, STYLE_RIGHT: math.pi/2 }

class ArrowTip( RootGUI ):
	"""
	��ͷָʾ
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
		self.__style = None					# ������ʽ
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
		�����������򣬼���Ӧ��ʹ�õ���ʾ����ʽ
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
		����������ʽ�Ĵ���
		"""
		pyArrow = ArrowTip()										# ����һ����ʾ����
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
		��������λ��
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
		�����ͷλ��
		"""
		pointIn = 0.25
		self.pyTipsArea_.relocate( location )
		style = self.__style
		bound = self.pyTipsArea_.bound
		x, y = location
		x += bound.minX
		y += bound.minY
		if style == STYLE_UP:							# ����
			x += bound.width * 0.5
			y += bound.height
			self.center = x
			self.top = y
		elif style == STYLE_DOWN:						# ����
			x += bound.width * 0.5
			self.center = x
			self.bottom = y
		elif style == STYLE_LEFT:						# ����
			y += bound.height*0.5
			x += bound.width
			self.left = x
			self.middle = y
		elif style == STYLE_RIGHT:						# ����
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
		��Ļ�ֱ��ʸı�ʱ������
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
		��ʾ�ı�
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		@type			pyBinder : instance of GUIBaseObject
		@param			pyBinder : Ҫ��ʾ�Ŀؼ���
									�����Ϊ None�����ɫ�߿��λ����� pyBinder ��λ��
									���Ϊ None�����ɫ�߿��λ�������Ļ��λ��
		@type			bound	 : cscustom::Rect
		@param			bound	 : Ȧ�����ĺ�ɫָʾ�߿����Ϊ None����ʹ��������ָ��������
		@rtype					 : bool
		@param					 : ��ʾ�ɹ����򷵻� True
		"""
		if tipid in SELF.__cg_pyArrows : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		if not tipsInfo : return False										# �����в����ڸ���ʾ ID
		pyArrow = SELF.buildArrowByInfo( tipsInfo, pyBinder, bound )
		pyArrow.show( tipid, pyBinder, tipsInfo.unframe )
		SELF.__cg_pyArrows[tipid] = pyArrow
		return True

	@classmethod
	def hideTips( SELF, tipid ) :
		"""
		������ʾ����
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		"""
		pyArrow = SELF.__cg_pyArrows.get( tipid, None )
		if pyArrow :
			pyArrow.hide()

	@classmethod
	def moveTips( SELF, tipid, location = None ) :
		"""
		�ƶ���ʾ����
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		@type			location : tuple
		@param			location : ָʾ����λ�ã����Ϊ None������ PyBinder �����Ͻ�Ϊָʾ����λ��
		"""
		pyArrow = SELF.__cg_pyArrows.get( tipid, None )
		if not pyArrow : return
		pyArrow.relocate( location )

	@classmethod
	def buildArrowByInfo( SELF, tipsInfo, pyBinder = None, bound = None ) :
		"""
		��ʾ�ı�
		@type			tipsInfo : instance of TipsInfo
		@param			tipsInfo : HelpTipsSetting�е���ʵ��
		@type			pyBinder : instance of GUIBaseObject
		@param			pyBinder : Ҫ��ʾ�Ŀؼ���
									�����Ϊ None�����ɫ�߿��λ����� pyBinder ��λ��
									���Ϊ None�����ɫ�߿��λ�������Ļ��λ��
		@type			bound	 : cscustom::Rect
		@param			bound	 : Ȧ�����ĺ�ɫָʾ�߿����Ϊ None����ʹ��������ָ��������
		@rtype					 : bool
		@param					 : ��ʾ�ɹ����򷵻� True
		"""
		location = 0, 0														# Ĭ�Ϻ�߿�λ�������Ļ
		if pyBinder :														# ����������ؼ�
			location = pyBinder.posToScreen									# ���߿�λ����������ؼ������Ͻ�
			if bound is None :												# ���û��ָ��ָʾ����
				bound = tipsInfo.bound										# ��ʹ�������е�ָʾ����
				if bound.width == 0 :										# ���������Ҳûָ��ָʾ����
					bound = Rect( ( 0, 0 ), pyBinder.size )					# ��ʹ�� pyBinder ����Ӿ�����Ϊָʾ����
		elif bound :														# û�������ؼ�
			location = bound.location										# ��λ�������Ļ
			bound.updateLocation( 0, 0 )
		else :
			raise TypeError( "one of argument 'pyBinder' and 'bound' must be not None!" )

		direct = tipsInfo.direct
		text = tipsInfo.text
		if direct == STYLE_NONE:
			direct = SELF.__calcStyle( location )							# ���������û��ָ��������ʽ��������Զ�ѡ�񴰿���ʽ
		pyArrow = SELF.__createArrow( direct, location, bound, text )	# ������ʽ�������ڷ��
		pyArrow.__relocate( location )										# ���ݺ�ɫ�߿�
		pyArrow.__relocateText()
		return pyArrow

