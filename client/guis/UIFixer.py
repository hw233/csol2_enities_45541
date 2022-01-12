# -*- coding: gb18030 -*-
#
# $Id: UIFixer.py,v 1.8 2008-08-02 09:15:05 huangyongwei Exp $


"""
implement resolution adapter
	when resolution changed, it wll be used to fix all uis

2007/03/18: writen by huangyongwei, then it named "ResolutionAdapter"
2008/01/04: rewriten by huangyongwei, rename it "UIFixer"
"""

import sys
import BigWorld
import Math
import GUI
import util
import scale_util as s_util
import UIScriptWrapper
from bwdebug import *
from AbstractTemplates import Singleton
from Weaker import WeakSet
from Function import Functor

class UIFixer( Singleton ) :
	__cc_def_resolution = 1024.0, 768.0							# 拼接界面时，使用的默认分辨率

	def __init__( self ) :
		self.__rates = ( 1, 1 )
		self.__pyUIs = WeakSet()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __fixChildrenPosition( rates, ui ) :
		"""
		当分辨率改变时，修正 ui 的所有子孙 UI 的位置
		@type			rates : tuple
		@param			rates : 新旧分辨率比:( 旧水平分辨率 / 新水平分辨率，就垂直分辨率 / 新垂直分辨率 )
		@type			ui	  : engine ui
		@param			ui	  : 被遍历的每一个 ui
		@return				  : None
		"""
		def verifier( ch ) :
			if ch == ui : return False, 1
			return True, 1

		children = util.preFindGui( ui, verifier )
		for child in children :
			x, y, z = child.position
			newX = x * rates[0]
			newY = y * rates[1]
			child.position = newX, newY, z

	@staticmethod
	def __adaptDock( preReso, ui ) :
		"""
		根据 dock style 重新设置 ui 的停靠位置
		@type				preReso : tuple
		@param				preReso : 旧分辨率
		@type				ui		: engine ui
		@param				ui		: 每个 ui
		@return						: None
		"""
		if ui.parent is not None : return
		pyUI = UIScriptWrapper.unwrap( ui )
		if pyUI is None : return
		oldWidth = preReso[0]
		newWidth = BigWorld.screenWidth()
		oldHeight = preReso[1]
		newHeight = BigWorld.screenHeight()
		deltaW = newWidth - oldWidth
		deltaH = newHeight - oldHeight
		wscale = oldWidth / newWidth
		hscale = oldHeight / newHeight
		if pyUI.h_dockStyle == "LEFT" :
			pyUI.left *= wscale
		elif pyUI.h_dockStyle == "CENTER" :
			pyUI.left = pyUI.left * wscale + deltaW / 2
		elif pyUI.h_dockStyle == "RIGHT" :
			pyUI.left = pyUI.left * wscale + deltaW
		elif pyUI.h_dockStyle == "HFILL" :
			pyUI.left *= wscale
			pyUI.width += deltaW
		elif pyUI.h_dockStyle == "S_LEFT" :
			pass
		elif pyUI.h_dockStyle == "S_CENTER" :
			fixcleft = pyUI.top * wscale + deltaW / 2
			fixcenter = fixcleft + pyUI.width / 2
			pyUI.center = ( newWidth / 2 ) - ( ( newWidth / 2 - fixcenter ) / wscale )
		elif pyUI.h_dockStyle == "S_RIGHT" :
			fixrleft = pyUI.left * wscale + deltaW
			fixright = fixrleft + pyUI.width
			pyUI.right = newWidth - ( ( newWidth - fixright ) / wscale )

		if pyUI.v_dockStyle == "TOP" :
			pyUI.top *= hscale
		elif pyUI.v_dockStyle == "MIDDLE" :
			pyUI.top = pyUI.top * hscale + deltaH / 2
		elif pyUI.v_dockStyle == "BOTTOM" :
			pyUI.top = pyUI.top * hscale + deltaH
		elif pyUI.v_dockStyle == "VFILL" :
			pyUI.top *= hscale
			pyUI.height += deltaH
		elif pyUI.v_dockStyle == "S_TOP" :
			pass
		elif pyUI.v_dockStyle == "S_MIDDLE" :
			fixmtop = pyUI.top * hscale + deltaH / 2
			fixmiddle = fixmtop + pyUI.height / 2
			pyUI.middle = ( newHeight / 2 ) - ( ( newHeight / 2 - fixmiddle ) / hscale )
		elif pyUI.v_dockStyle == "S_BOTTOM" :
			fixbtop = pyUI.top * hscale + deltaH
			fixbottom = fixbtop + pyUI.height
			pyUI.bottom = newHeight - ( ( newHeight - fixbottom ) / hscale )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onResolutionChanged( self, preReso ) :
		"""
		当分辨率改变时被调用
		"""
		hfUILoader.onResolutionChanged( preReso )

		for pyUI in self.__pyUIs :
			try :
				self.fix( preReso, pyUI.getGui() )
			except ReferenceError :
				self.__pyUIs.remove( pyUI )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def attach( self, pyUI ) :
		"""
		加载 ui 到适配列表中
		@type				pyUI : python ui
		@param				pyUI : python ui
		@return					 : None
		"""
		if pyUI not in self.__pyUIs :
			self.__pyUIs.add( pyUI )

	def detach( self, pyUI ) :
		"""
		从适配列表中卸载 ui
		@type				pyUI : python ui
		@param				pyUI : python ui
		@return					 : None
		"""
		if pyUI in self.__pyUIs :
			self.__pyUIs.remove( pyUI )

	# -------------------------------------------------
	def fix( self, preReso, ui ) :
		"""
		当分辨率改变时，调用它来修正 ui 的位置
		@type			preReso : tuple / Vector2
		@type			preReso : 修正前的分辨率
		@type			ui		: engine ui
		@param			ui		: 引擎 ui
		@return					: None
		"""
		rateX = preReso[0] / BigWorld.screenWidth()
		rateY = preReso[1] / BigWorld.screenHeight()
		rates = ( rateX, rateY )
		self.__fixChildrenPosition( rates, ui )
		self.__adaptDock( preReso, ui )

	def firstLoadFix( self, ui ) :
		"""
		当调用 GUI.load 加载 ui 时，调用它来修正 ui 的位置
		@type				ui : engine ui
		@param				ui : 引擎 ui
		@return				   : None
		"""
		defReso = self.__cc_def_resolution
		if defReso == BigWorld.screenSize() : return
		rateX = defReso[0] / BigWorld.screenWidth()
		rateY = defReso[1] / BigWorld.screenHeight()
		rates = ( rateX, rateY )
		self.__fixChildrenPosition( rates, ui )

	# -------------------------------------------------
	def firstDockRoot( self, pyRoot ) :
		"""
		当构造为 RootGUI 时，调用它来根据停靠方式（DockStyle）设置 ui 相对其父亲的停靠位置
		@type				pyRoot : python ui
		@param				pyRoot : python ui( common.RootGUI )
		@return					   : None
		"""
		self.__adaptDock( self.__cc_def_resolution, pyRoot.getGui() )

	# -------------------------------------------------
	def toFixedX( self, defX ) :
		"""
		将默认的 X 轴相对坐标转换为适合当前分辨率下的 X 轴相对坐标
		@type				defX : float
		@param				defX : 默认分辨率下的 X 轴相对坐标
		@rtype					 : float
		@return					 : 当前分辨率下的 X 轴相对坐标
		"""
		return defX * self.__cc_def_resolution[0] / BigWorld.screenWidth()

	def toFixedY( self, defY ) :
		"""
		将默认的 Y 轴相对坐标转换为适合当前分辨率下的 Y 轴相对坐标
		@type				defY : float
		@param				defY : 默认分辨率下的 Y 轴相对坐标
		@rtype					 : float
		@return					 : 当前分辨率下的 Y 轴相对坐标
		"""
		return defY * self.__cc_def_resolution[1] / BigWorld.screenHeight()

	def toFixedPos( self, defPos ) :
		"""
		将默认的相对坐标转换为适合当前分辨率下的相对坐标
		@type				defPos : Vector3
		@param				defPos : 默认分辨率下的相对坐标
		@rtype					   : Vector3/Vector2
		@return					   : 当前分辨率下的相对坐标
		"""
		scx, scy = BigWorld.screenSize()
		x = defPos[0] * self.__cc_def_resolution[0] / scx
		y = defPos[1] * self.__cc_def_resolution[1] / scy
		if len( defPos ) == 2 :
			return Math.Vector2( x, y )
		return Math.Vector3( x, y, defPos[2] )


# --------------------------------------------------------------------
# 实现需要频繁加载的 UI 的加载器
# 通过该加载器进行加载，会减少 firstLoadFix 的调用
# 注意：
#	① 千万别将所有的 UI 都用它来加载，那样会适得其反
#	② 只有整个游戏过程中都需要经常加载的 UI 才用它加载
# --------------------------------------------------------------------
class HFUILoader( Singleton ) :
	"""
	ui loader for load ui high frequency
	"""
	def __init__( self ) :
		self.__uis = {}

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onResolutionChanged( self, preReso ) :
		"""
		分辨率改变时被调用
		"""
		for path in self.__uis.keys() :
			self.__uis[path] = uiFixer.firstLoadFix( GUI.load( path ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def load( self, path ) :
		"""
		加载 UI 配置
		"""
		ui = self.__uis.get( path, None )
		if ui : return util.copyGuiTree( ui )
		ui = GUI.load( path )
		uiFixer.firstLoadFix( ui )
		self.__uis[path] = ui
		return util.copyGuiTree( ui )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
uiFixer = UIFixer()
hfUILoader = HFUILoader()
