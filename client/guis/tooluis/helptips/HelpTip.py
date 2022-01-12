# -*- coding: gb18030 -*-
#
# $Id: HelpTip.py

from guis import *
import weakref
from guis.common.RootGUI import RootGUI
from guis.common.FrameEx import HVFrameEx
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.infotip.TipsArea import TipsArea
from cscustom import Rect
from ArrowTip import ArrowTip
from AbstractTemplates import Singleton
from HelpTipsSetting import helpTipsSetting

class HelpTip( RootGUI, HVFrameEx ):
	"""
	泡泡指示
	"""
	cc_edge_width_			= 10.0		# 文字与边沿的距离
	__cc_min_width = 65.0				# 最小宽度
	__cg_pyHelpTips = {}

	def __init__( self ):
		tip = GUI.load( "guis/tooluis/helptips/helptip.gui" )
		uiFixer.firstLoadFix( tip )
		RootGUI.__init__( self, tip )
		HVFrameEx.__init__( self, tip )
		self.addToMgr()
		self.focus = False
		self.moveFocus = False
		self.escHide_ 		 = False
		self.posZSegment = ZSegs.L4
		pointer = tip.elements["pointer"]
		self.__prSitScale = float( pointer.position[0] )/ self.width

		self.pyRtMsg_ = CSRichText( tip.rtMsg )
		self.pyRtMsg_.maxWidth = 180.0
		self.pyRtMsg_.align = "L"
		self.pyRtMsg_.opGBLink = True
		self.pyRtMsg_.left = self.cc_edge_width_
		self.pyRtMsg_.top = self.cc_edge_width_

		self.__vsDetectCBID = 0
		self.__mapID = 0
		self.pyTipsArea_ = None

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def dispose( self ) :
		BigWorld.cancelCallback( self.__vsDetectCBID )
		if self.__mapID in self.__cg_pyHelpTips :
			self.__cg_pyHelpTips.pop( self.__mapID )
		self.pyTipsArea_.dispose()
		RootGUI.dispose( self )

	def __del__( self ) :
		self.pyTipsArea_.dispose()
		RootGUI.__del__( self )

	def __layout( self ) :
		"""
		设置窗口适应文本大小
		"""
		elements = self.gui.elements
		self.width = self.pyRtMsg_.right + self.cc_edge_width_#加0.6是用于去掉泡泡外边的黑条的（暂时只能这样）
		self.height = self.pyRtMsg_.bottom + elements["frm_b"].size[1]

	# -------------------------------------------------
	def __relocate( self, location ) :
		"""
		计算箭头位置
		"""
		elements = self.gui.elements
		self.pyTipsArea_.relocate( location )
		bound = self.pyTipsArea_.bound
		x, y = location
		x += bound.minX
		y += bound.minY
		self.top = y + 15.0
		self.center = x #- elements["pointer"].size[0]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, tipid, msg, pyBinder, unshowFrame ) :
		self.pyRtMsg_.text = msg
		if len( msg ) <= 5:
			self.pyRtMsg_.center = self.__cc_min_width / 2.0
		if pyBinder :
			self.__pyBinder = weakref.ref( pyBinder )
			BigWorld.callback( 1.0, self.__visibleDetect )
		self.__mapID = tipid
		self.__cg_pyHelpTips[tipid] = self
		if not unshowFrame :
			self.pyTipsArea_.show( pyBinder )
		self.__layout()
		self.visible = True

	def hide( self ) :
		self.visible = False
		self.dispose()

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		width = max( self.__cc_min_width, width )
		HVFrameEx._setWidth( self, width )
		elements = self.gui.elements
		tl = elements["frm_tl"]
		tr = elements["frm_tr"]
		pointer = elements["pointer"]
		lt = elements["frm_lt"]
		rt = elements["frm_rt"]
		r = elements["frm_r"]
		pointer.position[0] = max( tl.position[0]+tl.size[0], width*self.__prSitScale )
		tl.size[0] = pointer.position[0] - ( lt.position[0] + lt.size[0] )
		tr.size[0] = rt.position[0] - ( pointer.position[0] + pointer.size[0] )
		tr.position[0] = rt.position[0] - tr.size[0]
		self.pyRtMsg_.left = self.cc_edge_width_

	def _setHeight( self, height ) :
		HVFrameEx._setHeight( self, height )
		elements = self.gui.elements
		t = elements["frm_t"]
		tl = elements["frm_tl"]
		tr = elements["frm_tr"]
		pointer = elements["pointer"]
		bottom = t.position[1] + t.size[1]
		tl.position[1] = bottom - tl.size[1]
		pointer.position[1] = bottom - pointer.size[1]
		tr.position[1] = bottom - tr.size[1]
		self.pyRtMsg_.top = tl.position[1] + self.cc_edge_width_

	def _getCenter( self ):
		offset = self.width*( 0.5 - self.__prSitScale )
		center = HVFrameEx._getCenter( self )
		return center - offset

	def _setCenter( self, center ):
		offset = self.width*( 0.5 - self.__prSitScale )
		HVFrameEx._setCenter( self, center + offset )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HVFrameEx._getWidth, _setWidth )
	height = property( HVFrameEx._getHeight, _setHeight )
	center = property( _getCenter, _setCenter )

	#-----------------------------------------------------------------
	# staticmethod
	# ----------------------------------------------------------------
	@staticmethod
	def __createHelpTip( location, bound ) :
		"""
		构建各种样式的窗口
		"""
		pyHelpTip = HelpTip()										# 创建一个提示窗口
		pyHelpTip.pyTipsArea_ = TipsArea( location, bound )
		return pyHelpTip

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
		if tipid in SELF.__cg_pyHelpTips : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		if not tipsInfo : return False										# 配置中不存在该提示 ID
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
		text = tipsInfo.text
		pyHelpTip = SELF.__createHelpTip( location, bound )	# 根据样式构建窗口风格
		pyHelpTip.__relocate( location )										# 根据红色边框
		pyHelpTip.show( tipid, text, pyBinder, tipsInfo.unframe )
		return True

	@classmethod
	def hideTips( SELF, tipid ) :
		"""
		隐藏提示窗口
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		"""
		pyHelpTip = SELF.__cg_pyHelpTips.get( tipid, None )
		if pyHelpTip :
			pyHelpTip.hide()

	@classmethod
	def moveTips( SELF, tipid, location = None ) :
		"""
		移动提示窗口
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		@type			location : tuple
		@param			location : 指示区域位置，如果为 None，则以 PyBinder 的左上角为指示区域位置
		"""
		pyHelpTip = SELF.__cg_pyHelpTips.get( tipid, None )
		if not pyHelpTip : return
		if location is None :
			pyBinder = pyHelpTip.__pyBinder
			if pyBinder and pyBinder() :
				location = pyBinder().posToScreen
			else :
				raise TypeError( "argument location must be a tuple or Vector2!" )
		pyHelpTip.__relocate( location )

# -----------------------------------------------------------------------
class HelpTipsMgr( Singleton ):
	"""
	帮助提示管理器
	"""
	def __init__( self ):

		self.__helpTips = {}

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showTips( self, tipid, pyBinder, bound ) :
		"""
		通知显示一个提示，在这里区分是箭头还是泡泡指示
		"""
		if not helpTipsSetting.hasTips( tipid ) : return False
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		style = tipsInfo.style
		if style == 0:
			ArrowTip.showTips( tipid, pyBinder, bound )
		else:
			HelpTip.showTips( tipid, pyBinder, bound )
		return True

	def hideTips( self, tipid ) :
		"""
		通知关闭一个提示
		"""
		if not helpTipsSetting.hasTips( tipid ) : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		style = tipsInfo.style
		if style == 0:
			ArrowTip.hideTips( tipid )
		else:
			HelpTip.hideTips( tipid )

	def moveTips( self, tipid, location = None ) :
		"""
		通知移动一个提示
		"""
		if not helpTipsSetting.hasTips( tipid ) : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		style = tipsInfo.style
		if style == 0:
			ArrowTip.moveTips( tipid, location )					# 则通知位置调整
		else:
			HelpTip.moveTips( tipid, location )

helpTipsMgr = HelpTipsMgr()
