# -*- coding: gb18030 -*-
#
# $Id: TipWindow.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

"""
implement tips window for operation help

-- 2010/04/15 : writen by huangyongwei
"""

import random
import weakref
from cscustom import Rect
from Function import Functor
from Helper import uiopHelper
from AbstractTemplates import Singleton
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.common.Window import Window
from guis.tooluis.CSRichText import CSRichText
from TipsArea import TipsArea

"""
样式
1 :						2 :						3 :						4 :
						 |\						 		/|
--┌────┐			┌────┐			┌────┐			┌────┐--
 \│        │			│        │			│        │			│        │/
  │        │			│        │			│        │			│        │
  │        │			│        │			│        │			│        │
  └────┘			└────┘			└────┘			└────┘

5 :						6 :						7 :						8 :
  ┌────┐			┌────┐			┌────┐			┌────┐
  │        │			│        │			│        │			│        │
  │        │			│        │			│        │			│        │
  │        │\			│        │			│        │		   /│        │
  └────┘--		└────┘			└────┘		  --└────┘
								 \|				 |/
"""
# --------------------------------------------------------------------
# 全局定义
# --------------------------------------------------------------------
# 窗口样式定义
STYLE_LT = 1
STYLE_TL = 2
STYLE_TR = 3
STYLE_RT = 4
STYLE_RB = 5
STYLE_BR = 6
STYLE_BL = 7
STYLE_LB = 8

# -------------------------------------------
_wndPath = "guis/tooluis/infotip/ophelper/wnd.gui"


# --------------------------------------------------------------------
# 提示窗口的布局信息
# --------------------------------------------------------------------
class FormerInfo( object ) :
	bgSiteX = 0.0								# 提示文本板面相对指针的位置
	bgSiteY = 0.0

	cpBound = ( 0, 0, 0, 0 )					# clipPanel 相对 bg 的位置
	ptmappings = {}								# 各种样式下指针的 mapping
	ptSizes = {}								# 各种样式下指针的大小
	ptPlaces = {}								# 各种样式下指针的占位大小

	@staticmethod
	def rebuildFormerInfo() :
		"""
		重新构建样板窗口信息
		"""
		wnd = hfUILoader.load( _wndPath )											# 提示窗口
		pointer = wnd.elements["pointer"]											# 指针
		bg = wnd.elements["bg"]
		clipPanel = wnd.clipPanel
		ptmapping = pointer.mapping
		bgSiteX = bg.position.x														# 提示文本板面相对指针的位置
		bgSiteY = bg.position.y
		cpBound = (
			s_util.getGuiLeft( clipPanel ) - bgSiteX,								# clipPanel 相对 bg 的左距
			s_util.getGuiTop( clipPanel ) - bgSiteY,								# clipPanel 相对 bg 的右距
			bg.size.x - clipPanel.width,
			bg.size.y - clipPanel.height,
			)

		ptmappings = {																# 各种样式下指针的 mapping
			STYLE_LT : ptmapping,
			STYLE_TL : util.hflipMapping( util.cwRotateMapping90( ptmapping ) ),
			STYLE_TR : util.cwRotateMapping90( ptmapping ),
			STYLE_RT : util.hflipMapping( ptmapping ),
			STYLE_RB : util.cwRotateMapping180( ptmapping ),
			STYLE_BR : util.hflipMapping( util.ccwRotateMapping90( ptmapping ) ),
			STYLE_BL : util.ccwRotateMapping90( ptmapping ),
			STYLE_LB : util.vflipMapping( ptmapping ),
			}
		ptSizes = {																	# 各种样式下指针的大小
			STYLE_LT : pointer.size,
			STYLE_TL : ( pointer.size[1], pointer.size[0] ),
			STYLE_TR : ( pointer.size[1], pointer.size[0] ),
			STYLE_RT : pointer.size,
			STYLE_RB : pointer.size,
			STYLE_BR : ( pointer.size[1], pointer.size[0] ),
			STYLE_BL : ( pointer.size[1], pointer.size[0] ),
			STYLE_LB : pointer.size,
			}
		ptPlaces = {																# 各种样式下指针的占位大小
			STYLE_LT : ( bgSiteX, bgSiteY ),
			STYLE_TL : ( bgSiteY, bgSiteX ),
			STYLE_TR : ( bgSiteY, bgSiteX ),
			STYLE_RT : ( bgSiteX, bgSiteY ),
			STYLE_RB : ( bgSiteX, bgSiteY ),
			STYLE_BR : ( bgSiteY, bgSiteX ),
			STYLE_BL : ( bgSiteY, bgSiteX ),
			STYLE_LB : ( bgSiteX, bgSiteY ),
			}

		FormerInfo.bgSiteX = bgSiteX
		FormerInfo.bgSiteY = bgSiteY

		FormerInfo.cpBound = cpBound
		FormerInfo.ptmappings = ptmappings
		FormerInfo.ptSizes = ptSizes
		FormerInfo.ptPlaces = ptPlaces

	@classmethod
	def onEvent( SELF, eventName, oldRso ) :
		SELF.rebuildFormerInfo()

FormerInfo.rebuildFormerInfo()
ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", FormerInfo )


# --------------------------------------------------------------------
# 提示窗口
# --------------------------------------------------------------------
class OperationTip( Window ) :
	__cg_pyWnds = {}

	def __init__( self ) :
		wnd = hfUILoader.load( _wndPath )
		Window.__init__( self, wnd )
		self.addToMgr()
		self.posZSegment = ZSegs.L5
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False

		self.__mapID = -1
		self.pyRich_ = CSRichText( wnd.clipPanel )
		self.pyRich_.autoNewline = False
		self.pyRich_.widthAdapt = True
		self.pyTipsArea_ = None
		self.pyIcon_ = None

		self.__pyBinder = None
		self.__style = None					# 窗口样式
		self.__vsDetectCBID = 0

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def dispose( self ) :
		BigWorld.cancelCallback( self.__vsDetectCBID )
		if self.__mapID in self.__cg_pyWnds :
			self.__cg_pyWnds.pop( self.__mapID )
		self.pyTipsArea_.dispose()
		uiopTipsMgr.onTipsHide( self.__mapID )
		Window.dispose( self )

	def __del__( self ) :
		if Debug.output_del_OperationTip :
			INFO_MSG( str( self ) )
		self.pyTipsArea_.dispose()
		Window.__del__( self )


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
				return random.choice( ( STYLE_LT, STYLE_TL ) )
			else :
				return random.choice( ( STYLE_LB, STYLE_BL ) )
		else :
			if y < hsch :
				return random.choice( ( STYLE_TR, STYLE_RT ) )
			else :
				return random.choice( ( STYLE_RB, STYLE_BR ) )

	@staticmethod
	def __createWindow( text, style, location, bound, pyIcon ) :
		"""
		构建各种样式的窗口
		"""
		pyWnd = OperationTip()										# 创建一个提示窗口
		pyWnd.__style = style
		pyWnd.pyRich_.text = text
		pyWnd.pyTipsArea_ = TipsArea( location, bound )

		wnd = pyWnd.gui
		pointer = wnd.elements["pointer"]							# 指示针
		bg = wnd.elements["bg"]

		pointer.mapping = FormerInfo.ptmappings[style]				# 设置指针属性
		pointer.size = FormerInfo.ptSizes[style]

		bgWidth = pyWnd.pyRich_.width + FormerInfo.cpBound[2]
		bgHeight = pyWnd.pyRich_.height + FormerInfo.cpBound[3]
		if pyIcon :
			pyWnd.pyIcon_ = pyIcon
			pyWnd.addPyChild( pyIcon, "icon" )						# 设置图标
			bgWidth += ( pyIcon.width - pyWnd.pyCloseBtn_.width )
		bg.size = bgWidth, bgHeight									# 设置底板属性

		if style == STYLE_LT :										# 1
			pointer.position = 0, 0, 1
			bg.position.x = FormerInfo.bgSiteX
			bg.position.y = FormerInfo.bgSiteY
			wnd.width = s_util.getFElemRight( bg )
			wnd.height = s_util.getFElemBottom( bg )
		elif style == STYLE_TL :									# 2
			pointer.position = 0, 0, 1
			bg.position.x = FormerInfo.bgSiteY
			bg.position.y = FormerInfo.bgSiteX
			wnd.width = s_util.getFElemRight( bg )
			wnd.height = s_util.getFElemBottom( bg )
		elif style == STYLE_TR :									# 3
			pointer.position.y = 0
			bg.position.y = FormerInfo.bgSiteX
			wnd.height = s_util.getFElemBottom( bg )
			bg.position.x = 0
			wnd.width = bg.size.x + FormerInfo.bgSiteY
			pointer.position.x = wnd.width - pointer.size.x
		elif style == STYLE_RT :									# 4
			pointer.position.y = 0
			bg.position.y = FormerInfo.bgSiteY
			wnd.height = s_util.getFElemBottom( bg )
			bg.position.x = 0
			pointer.position.x = bg.size.x
			wnd.width = s_util.getFElemRight( pointer )
		elif style == STYLE_RB :									# 5
			bg.position = 0, 0, 1
			pointer.position.x = bg.size.x
			wnd.width = s_util.getFElemRight( pointer )
			wnd.height = bg.size.y + FormerInfo.bgSiteY
			pointer.position.y = wnd.height - pointer.size.y
		elif style == STYLE_BR :									# 6
			bg.position = 0, 0, 1
			pointer.position.y = s_util.getFElemBottom( bg )
			wnd.height = s_util.getFElemBottom( pointer )
			wnd.width = bg.size.x + FormerInfo.bgSiteY
			pointer.position.x = wnd.width - pointer.size.x
		elif style == STYLE_BL :									# 7
			pointer.position.x = 0
			bg.position.x = FormerInfo.bgSiteY
			wnd.width = s_util.getFElemRight( bg )
			bg.position.y = 0
			pointer.position.y = bg.size.y
			wnd.height = s_util.getFElemBottom( pointer )
		else :														# 8
			pointer.position.x = 0
			bg.position.x = FormerInfo.bgSiteX
			wnd.width = s_util.getFElemRight( bg )
			bg.position.y = 0
			wnd.height = s_util.getFElemBottom( bg ) + FormerInfo.bgSiteY
			pointer.position.y = wnd.height - pointer.size.y
		pyWnd.pyCloseBtn_.right = s_util.getFElemRight( bg )
		pyWnd.pyCloseBtn_.top = bg.position.y
		pyWnd.pyRich_.left = bg.position.x + FormerInfo.cpBound[0]
		pyWnd.pyRich_.top = bg.position.y + FormerInfo.cpBound[1]
		if pyIcon :
			pyIcon.left = pyWnd.pyRich_.right
			pyIcon.top = pyWnd.pyCloseBtn_.bottom + 10
			bottom = pyIcon.bottom
			if wnd.height < bottom :
				wnd.height = bottom
		return pyWnd

	# -------------------------------------------------
	def __relocate( self, location ) :
		"""
		计算窗口位置
		"""
		self.pyTipsArea_.relocate( location )

		pointIn = 0.25
		style = self.__style
		bound = self.pyTipsArea_.bound
		x, y = location
		x += bound.minX
		y += bound.minY
		if style == STYLE_LT :							# 1
			x += bound.width - FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.pos = x, y
		elif style == STYLE_TL :						# 2
			x += bound.width * 0.5
			y += bound.height - FormerInfo.bgSiteX * pointIn
			self.pos = x, y
		elif style == STYLE_TR :						# 3
			x += bound.width * 0.5
			y += bound.height - FormerInfo.bgSiteX * pointIn
			self.right = x
			self.top = y
		elif style == STYLE_RT :						# 4
			x += FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.right = x
			self.top = y
		elif style == STYLE_RB :						# 5
			x += FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.right = x
			self.bottom = y
		elif style == STYLE_BR :						# 6
			x += bound.width * 0.5
			y += FormerInfo.bgSiteX * pointIn
			self.right = x
			self.bottom = y
		elif style == STYLE_BL :						# 7
			x += bound.width * 0.5
			y += FormerInfo.bgSiteX * pointIn
			self.left = x
			self.bottom = y
		else :											# 8
			x += bound.width - FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.left = x
			self.bottom = y

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


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, tipid, pyBinder, unshowFrame ) :
		if pyBinder :
			self.__pyBinder = weakref.ref( pyBinder )
			BigWorld.callback( 1.0, self.__visibleDetect )
		self.__mapID = tipid
		self.__cg_pyWnds[tipid] = self
		if not unshowFrame :
			self.pyTipsArea_.show( pyBinder )
		Window.show( self, pyBinder )

	def hide( self ) :
		Window.hide( self )
		self.dispose()

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
		if tipid in SELF.__cg_pyWnds : return
		tipsInfo = uiopHelper.getTips( tipid )
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

		style = tipsInfo.style												# 窗口样式
		if style == 0 :
			style = SELF.__calcStyle( location )							# 如果配置中没有指定窗口样式，则程序自动选择窗口样式

		pyIcon = None
		if tipsInfo.icon != "" :											# 如果右边存在一个指示图标
			try :
				icon = GUI.load( "maps/ophelp_icons/%s" % tipsInfo.icon )
				pyIcon = PyGUI( icon )
			except ValueError, err :
				ERROR_MSG( err )

		text = tipsInfo.text
		pyWnd = SELF.__createWindow( text, style, location, bound, pyIcon )	# 根据样式构建窗口风格
		pyWnd.__relocate( location )										# 根据红色边框
		pyWnd.show( tipid, pyBinder, tipsInfo.unframe )
		return True

	@classmethod
	def hideTips( SELF, tipid ) :
		"""
		隐藏提示窗口
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		"""
		pyWnd = SELF.__cg_pyWnds.get( tipid, None )
		if pyWnd :
			pyWnd.hide()

	@classmethod
	def moveTips( SELF, tipid, location = None ) :
		"""
		移动提示窗口
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		@type			location : tuple
		@param			location : 指示区域位置，如果为 None，则以 PyBinder 的左上角为指示区域位置
		"""
		pyWnd = SELF.__cg_pyWnds.get( tipid, None )
		if not pyWnd : return
		if location is None :
			pyBinder = pyWnd.__pyBinder
			if pyBinder and pyBinder() :
				location = pyBinder().posToScreen
			else :
				raise TypeError( "argument location must be a tuple or Vector2!" )
		pyWnd.__relocate( location )


class UIOpTipsMgr( Singleton ) :
	"""Implement ui operation tips rule, such as max amount
	showed at one time、priority, etc"""
	__cc_GROUP_ROOT = 0													# 默认的分组（添加到屏幕的UI）
	__cc_MAX_SHOW_TIPS = 3												# 最大显示数量
	__cc_TIPS_HOLD_TIME = 10											# 持续显示时间

	def __init__( self ) :
		"""
		"""
		self.__tips2Group = {}											# 正在显示的脚本UI实例
		self.__tipsQueue = {}											# 提示等待显示队列
		self.__visibleTips = set()										# 正在显示的提示

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __isTipsFull( self ) :
		"""判断当前显示的提示是否已经达到上限"""
		return len( self.__visibleTips ) >= UIOpTipsMgr.__cc_MAX_SHOW_TIPS

	def __enterQueue( self, tipid, args ) :
		"""进入队列等待"""
		pyBinder = args[0]
		groupKey = UIOpTipsMgr.__cc_GROUP_ROOT
		if pyBinder is not None :
			groupKey = id( pyBinder.pyTopParent )						# 按照父窗口来进行分组
		self.__tips2Group[tipid] = groupKey
		tipsGroup = self.__tipsQueue.get( groupKey )
		if tipsGroup is None :
			tipsGroup = []
			self.__tipsQueue[groupKey] = tipsGroup
		tipsGroup.append( ( tipid, args ) )

	def __showTips( self, tipid, args ) :
		"""显示提示"""
		if OperationTip.showTips( tipid, *args ) :
			pyBinder = args[0]
			groupKey = UIOpTipsMgr.__cc_GROUP_ROOT
			if pyBinder is not None :
				groupKey = id( pyBinder.pyTopParent )
			self.__visibleTips.add( tipid )								# 记录下提示所在的分组
			self.__tips2Group[ tipid ] = groupKey						# 记录下提示所在的分组
			hideFunc = Functor( self.hideTips, tipid )
			BigWorld.callback( UIOpTipsMgr.__cc_TIPS_HOLD_TIME, hideFunc )
		else :
			DEBUG_MSG( "------->>> Tips shows false! %s %s" % ( tipid, args ) )
			self.__showNextTips( self.__popTips( tipid ) )

	def __showNextTips( self, groupKey = None ) :
		"""根据关闭的提示，找到下一条需要显示的提示"""
		if self.__isTipsFull() :
			return
		tipsGroup = self.__tipsQueue.get( groupKey )
		if not tipsGroup :
			for tipsGroup in self.__tipsQueue.itervalues() :
				if len( tipsGroup ) > 0 : break
			else :
				return													# 所有提示已经显示完
		tipid, args = tipsGroup.pop( 0 )
		del self.__tips2Group[tipid]									# 从记录中删去以便重新显示
		self.showTips( tipid, *args )

	def __popTips( self, tipid ) :
		"""移除掉tipid的数据"""
		groupKey = self.__tips2Group.pop( tipid, None )					# 删除掉已经显示过的提示
		if groupKey is None :
			return														# 没有相关的记录
		tipsGroup = self.__tipsQueue.get( groupKey )
		if tipsGroup is None :
			return
		for tip in tipsGroup :											# 从队列中删除
			if tip[0] == tipid :
				tipsGroup.remove( tip )
		if len( tipsGroup ) == 0 :
			del self.__tipsQueue[groupKey]
		return groupKey

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showTips( self, tipid, *args ) :
		"""通知显示一个提示"""
		if tipid in self.__tips2Group :
			return False
		if not uiopHelper.hasTips( tipid ) : return False
		if self.__isTipsFull() :
			self.__enterQueue( tipid, args )
		else :
			self.__showTips( tipid, args )
		return True

	def hideTips( self, tipid ) :
		"""通知关闭一个提示"""
		if tipid in self.__visibleTips :								# 该提示当前正在显示
			OperationTip.hideTips( tipid )
		else :
			self.__showNextTips( self.__popTips( tipid ) )

	def moveTips( self, tipid, location = None ) :
		"""通知移动一个提示"""
		if tipid in self.__visibleTips :								# 如果该提示当前正在显示
			OperationTip.moveTips( tipid, location )					# 则通知位置调整

	def onTipsHide( self, tipid ) :
		"""某个提示成功关闭后的通知"""
		if tipid in self.__visibleTips :
			self.__visibleTips.remove( tipid )
		else :
			DEBUG_MSG( "-------->>> Tip %i is unvisible, but it hide." % tipid )
		self.__showNextTips( self.__popTips( tipid ) )

	def clear( self ) :
		"""清空所有数据"""
		self.__tipsQueue.clear()
		self.__tips2Group.clear()
		self.__visibleTips.clear()


uiopTipsMgr = UIOpTipsMgr()
