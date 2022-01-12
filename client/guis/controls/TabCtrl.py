# -*- coding: gb18030 -*-
#
# $Id: TabCtrl.py,v 1.18 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement tabcontrl

2006.04.20: writen by huangyongwei
"""
"""
composing :
	GUI.Window
		-- btn_0 ( GUI.Window )    -> button for activate tab page
			-- lbText ( GUI.Text ) -> label for showing text of tab button
		-- panel_0 ( GUI.Window )
		-- btn_1 ( GUI.Window )    -> button for activate tab page
			-- lbText ( GUI.Text ) -> label for showing text of tab button
		-- panel_1 ( GUI.Window )
		.
		.
		.
"""

import weakref
from guis import *
from Control import Control
from SelectableButton import SelectableButton

class TabCtrl( Control ) :
	"""
	选项卡
	选项页的按钮必须以 "btn_" 开头，后面紧跟顺序索引值
	选项也的分页必须以 "panel_" 开头，后面紧跟顺序索引值
	"""
	def __init__( self, tabCtrl = None, pyBinder = None ) :
		Control.__init__( self, tabCtrl, pyBinder )
		self.__pyPages = []									# 保存所有选项页
		self.__initialize( tabCtrl )
		self.__rMouseSelect = False							# 是否允许右键选中

	def subclass( self, tabCtrl, pyBinder = None ) :
		Control.subclass( self, tabCtrl, pyBinder )
		self.__initialize( tabCtrl )
		return self

	def __del__( self ) :
		del self.__tabCtrl
		Control.__del__( self )
		if Debug.output_del_TabCtrl :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, tabCtrl ) :
		if tabCtrl is None : return
		self.__tabCtrl = tabCtrl


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Control.generateEvents_( self )
		self.__onTabPageSelectedChanged = self.createEvent_( "onTabPageSelectedChanged" )		# 当选页改变时被触发

	@property
	def onTabPageSelectedChanged( self ) :
		"""
		当选页改变时被触发
		"""
		return self.__onTabPageSelectedChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layoutTabs( self ) :
		"""
		重新排列 tab 按钮的 Z 坐标，以实现选中页按钮覆盖未选中页的按钮
		"""
		seg = 0.5 / self.pageCount
		for index, pyPage in enumerate( self.__pyPages ) :
			if pyPage.selected : pyPage.pyBtn.posZ = 0.4
			else : pyPage.pyBtn.posZ = 0.5 + index * seg
		self.resort()
		GUI.reSortFocusList( self.__tabCtrl )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onPageSelected_( self, pyPage ) :
		"""
		当某选项页选中时被调用
		"""
		for pyTmp in self.__pyPages :
			if not pyTmp.selected : continue
			if pyTmp == pyPage : continue
			pyTmp.selected = False
			break
		self.__layoutTabs()
		self.onTabPageSelectedChanged()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def calcTabCount( self ) :
		"""
		计算默认分页数（注意：只检索 "btn_" 前缀加索引号的分页，并且索引号要从 0 开始依次递增）
		"""
		count = 0
		for n, ch in self.gui.children :
			if "btn_" in n :
				count +=1
		return count

	def autoSearchPages( self, PanelCls = None, BtnCls = None, tabMapMode = UIState.MODE_R3C1 ) :
		"""
		自动检索并创建所有分页
		@type			PanelCls	: list
		@param			PanelCls	: 所有板面所属的类列表
		@type			BtnCls	 	: list
		@param			BtnCls	 	: 所有按钮所属的类列表
		@type			tabMapMode	: MACRO DEFINATION
		@param			tabMapMode	: 按钮状态模式
		"""
		index = 0													# 初始化索引为 0
		while True :												# 循环检索
			tabName = "btn_" + str( index )							# 按钮的名称
			btn = getattr( self.__tabCtrl, tabName, None )			# 获取 btn 按钮的引擎 UI 实例
			if btn is None : break									# 检索按钮完毕跳出
			panelName = "panel_" + str( index )						# 板面名字
			panel = getattr( self.__tabCtrl, panelName, None )		# 获取 btn 板面引擎 UI 实例
			if panel is None : break								# 检索完毕跳出
			if BtnCls is None :
				pyBtn = TabButton( btn )							# 创建 btn 按钮的 python UI
			else :
				pyBtn = BtnCls[index]( btn )
			pyBtn.setStatesMapping( tabMapMode )					# 设置按钮的状态 mapping
			if PanelCls and index < len( PanelCls ) :
				pyPanel = PanelCls[index]( panel )
			else :
				pyPanel = TabPanel( panel )							# 创建 btn 板面的 python UI
			pyPage = TabPage( pyBtn, pyPanel )						# 创建 btn 页实例
			self.addPage( pyPage )									# 添加一个 btn 页
			index += 1												# 增加索引，继续检索

	def addPage( self, pyPage ) :
		"""
		添加一个选项页
		"""
		if pyPage in self.__pyPages :								# 已经添加
			ERROR_MSG( "page %s has been added!" )
			return
		pyPage.setTabCtrl__( self )									# 设置选项页所属的选项卡控件
		pyPage.setIndex__( self.pageCount )							# 设置选项页的索引
		pyPage.pyPanel.h_dockStyle = "HFILL"
		pyPage.pyPanel.v_dockStyle = "VFILL"
		self.__pyPages.append( pyPage )								# 添加到页列表
		if self.pySelPage is None :									# 当前如果没有选中的页
			self.__pyPages[0].selected = True						# 则默认选中第一页
		self.__layoutTabs()											# 重新排列按钮的层次关系

	def insertPage( self, index, pyPage ) :
		"""
		插入一个选项页
		"""
		if pyPage in self.__pyPages :								# 已经添加
			ERROR_MSG( "page %s has been added!"%str( index ) )
			return
		if pyPage.selected :
			pyPage.selected = False
		pyPage.setTabCtrl__( self )									# 设置选项页所属的选项卡控件
		self.__pyPages.insert( index, pyPage )						# 添加到页列表
		pyPage.pyPanel.h_dockStyle = "HFILL"
		pyPage.pyPanel.v_dockStyle = "VFILL"
		for idx, pyPage in enumerate( self.__pyPages ) :
			pyPage.setIndex__( idx)									# 设置选项页的索引
		if self.pySelPage is None :									# 当前如果没有选中的页
			self.__pyPages[0].selected = True						# 则默认选中第一页
		self.__layoutTabs()											# 重新排列按钮的层次关系

	def addPages( self, *pyPages ) :
		"""
		添加一组选项页
		"""
		for pyPage in pyPages :
			self.addPage( pyPage )

	def removePage( self, pyPage ) :
		"""
		删除一个选项页
		"""
		if pyPage not in self.__pyPages :							# 验证选项页是否在选项卡控件中
			ERROR_MSG( "tab page %s is not in tab control!" )
			return
		index = pyPage.index										# 获取删除页的索引
		self.__pyPages.remove( pyPage )								# 从页列表中清除
		pyPage.setTabCtrl__( None )									# 将删除页的所属控件清空
		pyPage.setIndex__( -1 )										# 将索引设置为 －1 表示没有所属的选项卡
		if pyPage.selected :										# 如果删除页是被选中的页
			pyPage.selected = False									# 则取消删除页的选中状态
			if self.pageCount :										# 如果还有剩余页
				self.__pyPages[0].selected = True					# 则默认选中第一页
		for idx in xrange( index, self.pageCount ) :				# 重新设置删除页的后面页的索引
			self.__pyPages[idx].setIndex__( idx )

	def clearPages( self ) :
		"""
		清除所有选项页
		"""
		count = self.pageCount
		for index in xrange( count - 1, -1, -1 ) :
			self.removePage( self.__pyPages[index] )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSelectedPage( self ) :
		for pyPage in self.__pyPages :
			if pyPage.selected :
				return pyPage
		return None

	def _setSelectedPage( self, pyPage ) :
		pyPage.selected = True

	# ---------------------------------------
	def _getRMouseSelect( self ) :
		return self.__rMouseSelect

	def _setRMouseSelect( self, value ) :
		self.__rMouseSelect = value


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyPages = property( lambda self : self.__pyPages[:] )								# 获取所有分页
	pyBtns = property( lambda self : [pyPage.pyBtn for pyPage in self.__pyPages] )		# 获取所有分页按钮
	pyPanels = property( lambda self : [pyPage.pyPanel for pyPage in self.__pyPages] )	# 获取所有分页板面
	pageCount = property( lambda self : len( self.__pyPages ) )							# 获取分页总数量
	pySelPage = property( _getSelectedPage, _setSelectedPage )							# 获取当前被选中的分页
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )						# 是否允许右键选中选项


# --------------------------------------------------------------------
# implement tabbutton class
# --------------------------------------------------------------------
class TabButton( SelectableButton ) :
	def __init__( self, button = None, pyBinder = None )  :
		SelectableButton.__init__( self, button, pyBinder )
		self.effDisable = False
		self.__initialize( button )
		self.__pyPage = None

	def subclass( self, button ) :
		Control.subclass( self, button )
		self.__initialize( button )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_TabCtrl :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, button ) :
		if button is None : return
		self.setStatesMapping( UIState.MODE_R3C1 )
		self.mapping = self.mappings_[UIState.COMMON]


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRMouseDown_( self, mods ) :
		SelectableButton.onRMouseDown_( self, mods )
		pyCtrl = self.pyTabPage.pyTabCtrl
		if pyCtrl and pyCtrl.rMouseSelect :
			self.selected = True
			if self.enable :
				self.setState( UIState.SELECTED )
		return True


	# ----------------------------------------------------------------
	# friend methods of tab page
	# ----------------------------------------------------------------
	def setTabPage__( self, pyPage ) :
		"""
		设置所属 tab 页
		"""
		if pyPage is None :
			self.__pyPage = None
		else :
			self.__pyPage = weakref.ref( pyPage )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		"""
		row, col = stMode
		comMapping = util.getStateMapping( self.size, stMode, UIState.ST_R1C1 )
		self.mappings_[UIState.COMMON] = comMapping
		self.mappings_[UIState.HIGHLIGHT] = comMapping
		idx = 1
		if stMode[0] * stMode[1] > 3 :										# 超过 3 种状态，则意味着有高亮状态
			state = ( idx / col + 1, idx % col + 1 )
			idx += 1
			self.mappings_[UIState.HIGHLIGHT] = util.getStateMapping( self.size, stMode, state )
		state = ( idx / col + 1, idx % col + 1 )
		idx += 1
		self.mappings_[UIState.SELECTED] = util.getStateMapping( self.size, stMode, state )
		self.mappings_[UIState.PRESSED] = self.mappings_[UIState.SELECTED]
		state = ( idx / col + 1, idx % col + 1 )
		self.mappings_[UIState.DISABLE] = util.getStateMapping( self.size, stMode, state )
		self.mapping = self.mappings_[self.state]


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPage( self ) :
		if self.__pyPage is None :
			return None
		return self.__pyPage()

	def _setSelected( self, selected ) :
		if self.selected == selected : return
		SelectableButton._setSelected( self, selected )
		if self.pyTabPage :
			self.pyTabPage.onSelectChanged_( self.selected )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyTabPage = property( _getPage )											# 获取所属的 tab 页
	selected = property( SelectableButton._getSelected, _setSelected )			# 获取/设置是否选中



# --------------------------------------------------------------------
# implement tabpanel class
# --------------------------------------------------------------------
class TabPanel( Control ) :
	def __init__( self, panel, pyBinder = None ) :
		Control.__init__( self, panel, pyBinder )
		self.focus = False
		self.__pyPage = None

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_TabCtrl :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onShow( self ) :
		pass

	def onHide( self ) :
		pass

	# ----------------------------------------------------------------
	# friend methods of tab page
	# ----------------------------------------------------------------
	def setTabPage__( self, pyPage ) :
		if pyPage is None :
			self.__pyPage = None
		else :
			self.__pyPage = weakref.ref( pyPage )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPage( self ) :
		if self.__pyPage is None :
			return None
		return self.__pyPage()

	# -------------------------------------------------
	def _setVisible( self, visible ) :
		Control._setVisible( self, visible )
		if visible : self.onShow()
		else : self.onHide()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyTabPage = property( _getPage )
	visible = property( Control._getVisible, _setVisible )


# --------------------------------------------------------------------
# implement tabpage class
# --------------------------------------------------------------------
class TabPage( object ) :
	def __init__( self, pyBtn = None, pyPanel = None ) :
		object.__init__( self )
		self.__pyTabCtrl = None						# 所属的选项卡控件
		self.__pyBtn = None							# 的选项按钮
		self.__pyPanel = None						# 选项板面
		self.__index = -1							# 在选项卡中的索引
		self.__events = []							# 事件列表
		self.generateEvents_()
		if pyBtn and pyPanel :
			self.setPage( pyBtn, pyPanel )

	def __del__( self ) :
		self.__events = []
		if Debug.output_del_TabCtrl :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		"""
		创建事件
		"""
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		"""
		生成事件
		"""
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )			# 选中状态改变时被触发

	@property
	def onSelectChanged( self ) :
		"""
		当选中时被触发
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelectChanged_( self, selected ) :
		"""
		选中该页（由 tab 按钮调用）
		"""
		if selected :
			self.__pyPanel.visible = True
			self.onSelectChanged( True )
			if self.pyTabCtrl :
				self.pyTabCtrl.onPageSelected_( self )
		else :
			self.__pyPanel.visible = False
			self.onSelectChanged( False )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setPage( self, pyBtn, pyPanel ) :
		"""
		设置一个选项页的按钮和板面
		"""
		pyBtn.selected = False
		self.__pyBtn = pyBtn
		self.__pyBtn.setTabPage__( self )
		pyPanel.visible = False
		self.__pyPanel = pyPanel
		self.__pyPanel.setTabPage__( self )


	# ----------------------------------------------------------------
	# friend methods of this module
	# ----------------------------------------------------------------
	def setTabCtrl__( self, pyTabCtrl ) :
		"""
		设置所属的 tab Ctrl
		"""
		if pyTabCtrl is None :
			self.__pyTabCtrl = None
		else :
			self.__pyTabCtrl = weakref.ref( pyTabCtrl )

	def setIndex__( self, index ) :
		"""
		设置选项页的索引
		"""
		self.__index = index


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPyTabCtrl( self ) :
		if self.__pyTabCtrl is None :
			return None
		return self.__pyTabCtrl()

	# -------------------------------------------------
	def _getPyBtn( self ) :
		return self.__pyBtn

	def _getPyPanel( self )  :
		return self.__pyPanel

	# ---------------------------------------
	def _getIndex( self ) :
		return self.__index

	# -------------------------------------------------
	def _getEnable( self ) :
		return self.__pyBtn.enable

	def _setEnable( self, enable ) :
		self.__pyBtn.enable = enable
		self.__pyPanel.enable = enable

	# ---------------------------------------
	def _getSelected( self ) :
		return self.__pyBtn.selected

	def _setSelected( self, value ) :
		self.__pyBtn.selected = value


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyTabCtrl = property( _getPyTabCtrl )							# 获取所属的选项卡控件
	pyBtn = property( _getPyBtn )									# 获取 tab 按钮
	pyPanel = property( _getPyPanel )								# 获取 tab 板面
	index = property( _getIndex )									# 获取板面在选项卡中的索引

	enable = property( _getEnable, _setEnable )						# 获取/设置是否可用
	selected = property( _getSelected, _setSelected )				# 获取/设置是否被选中
