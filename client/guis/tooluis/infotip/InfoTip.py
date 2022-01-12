# -*- coding: gb18030 -*-
#
# $Id: InfoTip.py,v 1.2 2008-08-21 09:11:16 huangyongwei Exp $

"""
implement information tip window

-- 2008/08/19 : writen by huangyongwei
"""

import weakref
import csol
from guis import *
from guis.ScreenViewer import ScreenViewer
from guis.tooluis.infotip.ToolTip import ToolTip
from guis.tooluis.infotip.ItemTip import ItemTip
from guis.tooluis.infotip.OperationTip import uiopTipsMgr
from guis.tooluis.infotip.ItemTip import Grid
from guis.tooluis.helptips.HelpTip import helpTipsMgr

class InfoTip( object ) :
	__cg_pyTipWnds = {}
	__cg_pyTipWnds[ItemTip]		= set()			# 物品提示窗口
	__cg_pyTipWnds[ToolTip]		= set()			# 工具提示窗口

	__cc_delayShowTime			= 0.1			# 延时多长时间显示

	def __init__( self ) :
		self.__pyBinder = None					# 绑定的控件
		self.__pyMainWnd = None					# 主窗口
		self.__pyAssistWnds = []				# 辅助窗口
		self.__vsDetectCBID = 0					# 监测绑定控件可见性的 callback ID
		self.__delayShowCBID = 0				# 延时显示的 callback ID

		self.__itemTpls = ()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getTipWindow( self, WndCls ) :
		"""
		根据模板明从对象池中申请一个 tipwindow 或 tooltip
		"""
		if len( self.__cg_pyTipWnds[WndCls] ) :				# 如果对象池中还有对象
			return self.__cg_pyTipWnds[WndCls].pop()		# 则从对象池中弹出一个
		return WndCls()										# 否则重新创建一个

	def __reclaimWnds( self ) :
		"""
		回收提示窗口
		"""
		if self.__pyMainWnd :
			self.__pyMainWnd.hide()
			self.__cg_pyTipWnds[self.__pyMainWnd.__class__].add( self.__pyMainWnd )
			ScreenViewer().removeResistHiddenRoot(self.__pyMainWnd)
		for pyWnd in self.__pyAssistWnds :
			pyWnd.hide()
			self.__cg_pyTipWnds[pyWnd.__class__].add( pyWnd )
		self.__pyAssistWnds = []
		self.__pyBinder = None

	# -------------------------------------------------
	def __locateToolTips( self ) :
		"""
		设置工具提示的位置
		"""
		pyWnd = self.__pyMainWnd
		sw, sh = BigWorld.screenSize()					# 屏幕大小
		x, y = rds.ccursor.pos							# 鼠标指针位置
		dx, dy = rds.ccursor.dpos						# 鼠标右下角位置
		dx = min( dx, sw )
		if pyWnd.width <= sw - dx :
			if pyWnd.height < sh - dy :					# 右下角能放下提示窗口
				pyWnd.pos = dx, dy						# 则将窗口放到鼠标右边
			else :										# 右上角能放下提示窗口
				pyWnd.left = x
				pyWnd.bottom = y
		else :
			if pyWnd.height < sh - dy :					# 左下角能放下提示窗口
				pyWnd.right = dx
				pyWnd.top = dy
			else :										# 只能放左上角
				pyWnd.right = x
				pyWnd.bottom = y

	# -------------------------------------------------
	def __locateESignTips( self ) :
		"""
		设置实体标记提示的位置
		"""
		pyWnd = self.__pyMainWnd
		sw, sh = BigWorld.screenSize()					# 屏幕大小
		x, y = rds.ccursor.pos							# 鼠标指针位置
		dx, dy = rds.ccursor.dpos						# 鼠标右下角位置
		dx = min( dx, sw )
		if pyWnd.height <= sh - dy :					# 如果窗口能放到鼠标下面
			pyWnd.top = dy
			if dx < pyWnd.width / 2 :					# 如果窗口顶尽左边
				pyWnd.left = 0
			elif sw - dx < pyWnd.width / 2 :			# 如果窗口顶尽右边
				pyWnd.right = sw
			else :
				pyWnd.center = dx						# 否则，窗口中间在鼠标下面
		else :											# 如果窗口不能放到鼠标下面
			pyWnd.bottom = y							# 则将其放到鼠标上面
			if dx < pyWnd.width / 2 :
				pyWnd.left = 0
			elif sw - dx < pyWnd.width / 2 :
				pyWnd.right = sw
			else :
				pyWnd.center = x						# 窗口中间在鼠标上面

	# -------------------------------------------------
	def __generateItemTips( self, tips ) :
		"""
		生成一个物品提示窗口
		"""
		pyWnd = self.__getTipWindow( ItemTip )				# 获取一个物品提示窗口
		pyWnd.clear()
		pyWnd.setItemInfo( tips )
		return pyWnd

	def __locateItemTips( self, pyBinder ) :
		"""
		排列所有物品提示窗口
		"""
		width, height = self.size							# 所有窗口的宽度和，最高窗口的高度
		sw, sh = BigWorld.screenSize()						# 屏幕大小
		x, y = rds.ccursor.pos								# 鼠标指针位置
		dx, dy = rds.ccursor.dpos							# 鼠标右下角位置
		dx = max( 0, min( dx, sw ) )
		if height <= sh - dy or y < height :				# 如果鼠标下面能放下所有提示窗口，或者鼠标上面放不下所有提示窗口
			top = self.__pyMainWnd.top = min( dy, sh - height )
			if width <= sw - dx or width > dx :				# 如果所有提示窗口能在右下角显示
				self.__pyMainWnd.left = min( dx, sw - width )
				left = self.__pyMainWnd.right
				for pyWnd in self.__pyAssistWnds :
					pyWnd.left = left
					pyWnd.top = top
					left = pyWnd.right
					pyWnd.show( pyBinder )
			else :											# 如果全部提示窗口能在左下角显示
				self.__pyMainWnd.right = dx
				right = self.__pyMainWnd.left
				for pyWnd in self.__pyAssistWnds :
					pyWnd.right = right
					pyWnd.top = top
					right = pyWnd.left
					pyWnd.show( pyBinder )
		else :												# 所有提示窗口只能在鼠标上面显示
			bottom = self.__pyMainWnd.bottom = y
			if width <= sw - dx or width > x :				# 如果所有提示窗口能右上角显示
				self.__pyMainWnd.left = min( x, sw - width )
				left = self.__pyMainWnd.right
				for pyWnd in self.__pyAssistWnds :
					pyWnd.left = left
					pyWnd.bottom = bottom
					left = pyWnd.right
					pyWnd.show( pyBinder )
			else :											# 所有提示窗口只能在鼠标左上角显示
				self.__pyMainWnd.right = x
				right = self.__pyMainWnd.left
				for pyWnd in self.__pyAssistWnds :
					pyWnd.right = right
					pyWnd.bottom = bottom
					right = pyWnd.left
					pyWnd.show( pyBinder )
		self.__pyMainWnd.show( pyBinder )

	def __visableDetect( self, pyBinder ) :
		"""
		侦测绑定者是否可见，如果不可见，则隐藏所有提示框
		"""
		if not pyBinder.visible :
			self.hide()
		else :
			BigWorld.cancelCallback( self.__vsDetectCBID )
			func = Functor( self.__visableDetect, pyBinder )
			self.__vsDetectCBID = BigWorld.callback( 0.5, func )
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showToolTips( self, pyBinder, text, resistHidden=False ) :
		"""
		显示工具提示
		@type				pyBinder : python UI
		@param				pyBinder : 绑定 UI
		@type				text	 : str
		@param				text	 : 提示内容
		@type				resistHidden : bool
		@param				resistHidden : 是否忽略清屏
		"""
		if text == "" : return
		self.__reclaimWnds()								# 首先回收所有窗口
		self.__pyBinder = weakref.ref( pyBinder )			# 记录绑定控件
		pyWnd = self.__getTipWindow( ToolTip )
		pyWnd.clear()
		pyWnd.setText( text )
		self.__pyMainWnd = pyWnd
		self.__locateToolTips()
		if resistHidden:
			ScreenViewer().addResistHiddenRoot(self.__pyMainWnd)
		pyWnd.show( pyBinder )

	# ---------------------------------------
	def showESignTips( self, pyBinder, text ) :
		"""
		显示大/小地图上 entity 的信息
		"""
		if text == "" : return
		self.__reclaimWnds()								# 首先回收所有窗口
		self.__pyBinder = weakref.ref( pyBinder )			# 记录绑定控件
		pyWnd = self.__getTipWindow( ToolTip )
		pyWnd.clear()
		pyWnd.setText( text )
		self.__pyMainWnd = pyWnd
		self.__locateESignTips()
		pyWnd.show( pyBinder )

	# ---------------------------------------
	def getItemGrid( self, text, tpl ) :
		"""
		获取物品提示格子模板
		@type				text : str
		@param				text : 格子中的文本
		@type				tpl	 : dict
		@param				tpl	 : 格式化字典：
								   "align"		: 文本水平对齐方式，"L"、"C"、"R" 分别表示左中右对齐
								   "lineFlat"	: 文本垂直对齐方式，"T"、"M"、"B" 分别表示顶中下对齐
								   "newline": 是否自动换行
								   全部关键字都为可选，譬如可以仅仅传入：{ "maxWidth" : 100 }
		"""
		return Grid( text, tpl )

	def setItemTemplates( self, *tpls ) :
		"""
		设置物品提示窗口的模板
		@type			tpls : tuple of dict
		@param			tpls : { "minWidth" : 最小宽度, "lMaxWith" : 左边列最大宽度, "rMaxWidth" : 右边列最大宽度 }
		"""
		self.__itemTpls = tpls

	def showItemTips( self, pyBinder, *tips ) :
		"""
		显示物品提示
		@type				pyBinder : python UI
		@param				pyBinder : 绑定 UI
		@type				tips	 : str / list
		@param				tips	 : 提示内容（可以通过传入多个参数来实现多个提示框，每个可变参数表示一个提示框的内容）:
									   如果是单列的文本提示，可以直接传入 str 如：
										   showItemTips( pyBinder, str1 )
									   或：gt1 = getItemGridTemplate( 格子格式化模板, str1 )
										   showItemTips( pyBinder, gt1 )

									   如果要显示多个提示，则可以传入多个提示框的文本内容，如：
										   showItemTips( pyBinder, str1, [str2, [str3, str4]] )
									   或：gt1 = getItemGridTemplate( 格子格式化模板, str1 )
										   gt2 = getItemGridTemplate( 格子格式化模板, str2 )
										   gt3 = getItemGridTemplate( 格子格式化模板, str3 )
										   showItemTips( pyBinder, gt, [gt2, [gt3, str4]] ) 这样，第一个提示框是单列文本，
										   第二个提示框为两行两列文本:
										  ┌──┐┌─────┐
										  │    ││str2      │
										  │str1│├──┬──┤
										  │    ││str3│str4│
										  └──┘└──┴──┘
									   也可以写成：
										   showItemTips( pyBinder, [[str1]], [[str2], [str3, str4]] )
									   也可以写成：
										   showItemTips( pyBinder, [[str1, ""]], [[str2, ""], [str3, str4]] )

									   如果要在某行后增加一个分隔条，则可以这样写：
										   showItemTips( pyBinder, [str1, [], str2] )
										   ┌─────┐
										   │   str1   │---> 仍然是第一行（索引是 0）
										   ├─────┤---> 分隔条
										   │   str2   │---> 仍然是第二行（索引是 1）
                                           └─────┘
		"""
		def delayHandle() :
			self.__reclaimWnds()								# 首先回收所有窗口
			self.__pyBinder = weakref.ref( pyBinder )			# 记录绑定控件
			pyWnds = []
			for idx, tip in enumerate( tips ) :					# 循环解释每个提示框内容
				pyWnd = self.__generateItemTips( tip )			# 创建一个提示框
				if idx < len( self.__itemTpls ) :				# 是否有模板
					pyWnd.setTemplate( self.__itemTpls[idx] )	# 设置模板
				pyWnd.typeset()									# 排版内容
				pyWnds.append( pyWnd )							# 将提示框放到当前提示列表中
			if len( pyWnds ) :
				self.__pyMainWnd = pyWnds[0]
				self.__pyAssistWnds = pyWnds[1:]
				self.__locateItemTips( pyBinder )				# 排列所有窗口位置
				self.__itemTpls = ()							# 清除模板

		BigWorld.cancelCallback( self.__delayShowCBID )
		self.__delayShowCBID = BigWorld.callback( self.__cc_delayShowTime, delayHandle )
		self.__visableDetect( pyBinder )

	# -------------------------------------------------
	def hide( self, pyBinder = None ) :
		"""
		隐藏所有提示窗口
		"""
		BigWorld.cancelCallback( self.__delayShowCBID )
		if self.__pyMainWnd is None : return
		if pyBinder is None or self.pyBinder == pyBinder :
			BigWorld.cancelCallback( self.__vsDetectCBID )
			self.__vsDetectCBID = 0
			self.__reclaimWnds()

	# -------------------------------------------------
	def showOperationTips( self, tipid, pyBinder = None, bound = None ) :
		"""
		显示操作提示
		注意：本提示不跟随鼠标，并且可以同时显示多个
		@type			tipid	 : INT16
		@param			tipid	 : 配置中的提示 ID
		@type			pyBinder : instance of GUIBaseObject
		@param			pyBinder : 要提示的控件：
									如果不为 None，则红色边框的位置相对 pyBinder 的位置
									如果为 None，则红色边框的位置相对屏幕的位置
		@type			bound	 : cscustom::Rect
		@param			bound	 : 圈起来的红色指示边框，如果为 None，则使用配置中指定的区域
		"""
		return uiopTipsMgr.showTips( tipid, pyBinder, bound )

	def hideOperationTips( self, tipid ) :
		"""
		隐藏操作提示
		@type				tipid	 : INT16
		@param				tipid	 : 要提示的操作 id
		"""
		uiopTipsMgr.hideTips( tipid )

	def moveOperationTips( self, tipid, location = None ) :
		"""
		移动操作提示的位置
		@type				tipid	 : INT16
		@param				tipid	 : 要提示的操作 id
		@type				point	 : tuple
		@param				point	 : 提示显示的位置，如果提示的位置为 None，则根据其 pyBinder 的位置进行移动
		"""
		uiopTipsMgr.moveTips( tipid, location )

	def showHelpTips( self, tipid, pyBinder = None, bound = None ):
		"""
		显示帮助提示
		"""
		return helpTipsMgr.showTips( tipid, pyBinder, bound )

	def hideHelpTips( self, tipid ):
		"""
		隐藏帮助提示
		"""
		helpTipsMgr.hideTips( tipid )

	def moveHelpTips( self, tipid, location = None ):
		"""
		移动帮助提示
		"""
		helpTipsMgr.moveTips( tipid, location )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# -------------------------------------------------
	def _getWidth( self ) :
		width = 0
		if self.__pyMainWnd :
			width = self.__pyMainWnd.width
		for pyWnd in self.__pyAssistWnds :
			width += pyWnd.width
		return width

	def _getHeight( self ) :
		height = 0
		if self.__pyMainWnd :
			height = self.__pyMainWnd.height
		for pyWnd in self.__pyAssistWnds :
			height = max( pyWnd.height, height )
		return height

	def _getSize( self ) :
		width = height = 0
		if self.__pyMainWnd :
			width = self.__pyMainWnd.width
			height = self.__pyMainWnd.height
		for pyWnd in self.__pyAssistWnds :
			height = max( pyWnd.height, height )
			width += pyWnd.width
		return width, height


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )								# 当前提示绑定的控件
	width = property( _getWidth )									# 所有提示框的宽度和
	height = property( _getHeight )									# 所有提示框中，最高提示框的高度
	size = property( _getSize )										# ( self.width, self.height )
