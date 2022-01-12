# -*- coding: gb18030 -*-

"""
implement window with tabctrl that its tabbuttons are in the right of the window
2009/12/28 : writen by huangyongwei
"""

from guis import *
import csstring
from Window import Window
from FrameEx import VFrameEx
from guis.controls.TabCtrl import TabCtrl, TabButton
from guis.controls.StaticText import StaticText

"""
composing :
	GUI.Window
		-- lbTitle  [optional gui]( GUI.Text )-> label for show window title
		-- closeBtn [optional gui]( GUI.XXX  )-> close button
		-- helpBtn  [optional gui]( GUI.XXX  )-> help button
		-- minBtn   [optional gui]( GUI.XXX  )-> minimize button
		-- tc: GUI.Simple
"""
class NestedTabWindow( Window ) :
	def __init__( self, wnd ) :
		Window.__init__( self, wnd )
		self.pyRightTabFrame_ = VFrameEx( wnd.rightTabFrame )
		self.pyTabCtrl_ = TabCtrl( wnd.tc )
		self.pyTabCtrl_.onTabPageSelectedChanged.bind( self.__onTabSelectChanged )
		self.pyNestedCtrls_ = {}						# { pyPage : nested pyTabCtrl }


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onTabSelectChanged( self ) :
		"""
		当父层选项选择改变时被触发
		"""
		pySelPage = self.pyTabCtrl_.pySelPage
		if pySelPage not in self.pyNestedCtrls_ :
			self.layoutTabButtons( [] )
		else :
			self.layoutTabButtons( self.pyNestedCtrls_[pySelPage].pyBtns )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def layoutTabButtons( self, pyBtns, frameSpace = 6 ) :
		"""
		排列所有 tab 按钮
		@type				pyBtns	   : list
		@param				pyBtns	   : 所有 Tab 按钮
		@type				frameSpace : int
		@param				frameSpace : Tab 按钮边框的空隙
		"""
		gui = self.gui
		rt = gui.elements["frm_rt"]							# 右上角
		r = gui.elements["frm_r"]							# 右边
		rb = gui.elements["frm_rb"]							# 右下角
		rtBottom = rt.position.y + rt.size.y				# 右上角底距
		if len( pyBtns ) == 0 :
			self.pyRightTabFrame_.visible = False
			r.position.y = rtBottom
			r.size.y = rb.position.y - rtBottom
		else :
			f_t = self.pyRightTabFrame_.gui.elements['frm_t']
			f_b = self.pyRightTabFrame_.gui.elements['frm_b']
			top = rtBottom + f_t.size.y - frameSpace
			height = 0
			for pyBtn in pyBtns :
				pyBtn.top = top
				top = pyBtn.bottom
				height += pyBtn.height
			self.pyRightTabFrame_.height = height + f_t.size.y + f_b.size.y - frameSpace * 2
			r.position.y = self.pyRightTabFrame_.bottom
			r.size.y = rb.position.y - self.pyRightTabFrame_.bottom
			self.pyRightTabFrame_.visible = True

	# -------------------------------------------------
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
		self.pyTabCtrl_.autoSearchPages( PanelCls, BtnCls, tabMapMode )

	def autoSearchSubPages( self, index, PanelCls = None, BtnCls = None, tabMapMode = UIState.MODE_R1C3 ) :
		"""
		自动检索并创建所有分页
		@type			index		: int
		@param			index		: 要检索嵌套选项卡的父选项卡索引
		@type			PanelCls	: list
		@param			PanelCls	: 所有板面所属的类列表
		@type			BtnCls	 	: list
		@param			BtnCls	 	: 所有按钮所属的类列表
		@type			tabMapMode	: MACRO DEFINATION
		@param			tabMapMode	: 按钮状态模式
		"""
		pyPage = self.pyPages[index]
		panel = pyPage.pyPanel.gui
		if hasattr( panel, "tc" ) :
			pyTabCtrl = TabCtrl( panel.tc )
			self.pyNestedCtrls_[pyPage] = pyTabCtrl
			pyTabCtrl.autoSearchPages( PanelCls, BtnCls, tabMapMode )

	# -------------------------------------------------
	def addPage( self, pyPage ) :
		"""
		添加一个分页
		"""
		self.pyTabCtrl_.addPage( pyPage )

	def removePage( self, pyPage ) :
		"""
		删除一个分页
		"""
		self.pyTabCtrl_.removePage( pyPage )

	def insertPage( self, index, pyPage ) :
		"""
		插入一个分页
		"""
		self.pyTabCtrl_.insertPage( index, pyPage )

	def clearPages( self ) :
		"""
		清除所有分页
		"""
		self.pyTabCtrl_.clearPages()

	# -------------------------------------------------
	def insertNestedPage( self, parentIndex, pyPage, index = None ) :
		"""
		插入一个嵌套的分页
		@type				parentIndex : int
		@param				parentIndex : 要插入嵌套分页的父分页的索引
		@type				pyPage		: TabCtrl::TabPage
		@param				pyPage		: 要嵌套的分页
		@type				index		: int
		@param				index		: 要插入子分页的索引( 如果省略，则往后面追加 )
		"""
		pyParentPage = self.pyPages[parentIndex]
		pyTabCtrl = self.pyNestedCtrls_.get( pyParentPage, None )
		if pyTabCtrl is None :
			raise TypeError( "this parent tabpage is not allow to insert sub tabpage!" )
		if index is None : index = pyTabCtrl.pageCount
		pyTabCtrl.insertPage( index, pyPage )
		if pyParentPage == self.pyTabCtrl_.pySelPage :
			self.layoutTabButtons( pyTabCtrl.pyBtns )

	def removeNestedPage( self, parentIndex, index ) :
		"""
		删除一个嵌套的分页
		@type			parentIndex : int
		@param			parentIndex : 要删除嵌套分页的父分页的索引
		@type			index		: int
		@param			index		: 要删除子分页的索引
		"""
		pyParentPage = self.pyPages[parentIndex]
		pyTabCtrl = self.pyNestedCtrls_.get( pyParentPage, None )
		if pyTabCtrl is None :
			raise TypeError( "this parent tabpage is not allow to insert sub tabpage!" )
		pyTabCtrl.removePage( pyTabCtrl.pyPages[index] )
		if pyParentPage == self.pyTabCtrl_.pySelPage :
			self.layoutTabButtons( pyTabCtrl.pyBtns )

	def clearNestedPages( self, index ) :
		"""
		清除某个选项卡的所有子选项卡
		"""
		pyPage = self.pyPages[index]
		pyNEstCtrl = self.pyNestedCtrls_.get( pyPage, None )
		if pyNEstCtrl :
			pyNEstCtrl.clearPages()
		if pyParentPage == self.pyTabCtrl_.pySelPage :
			self.layoutTabButtons( pyTabCtrl.pyBtns )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSubTabCtrls( self ) :
		pyTabCtrls = []
		for pyPage in self.pyPages :
			pyTabCtrl = self.pyNestedCtrls_.get( pyPage, None )
			pyTabCtrls.append( pyTabCtrl )
		return pyTabCtrls


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyPages = property( lambda self : self.pyTabCtrl_.pyPages )			# 获取所有分页
	pyBtns = property( lambda self : self.pyTabCtrl_.pyBtns )			# 获取所有分页按钮
	pyPanels = property( lambda self : self.pyTabCtrl_.pyPanels )		# 获取所有分页板面
	pySelPage = property( lambda self : self.pyTabCtrl_.pySelPage )		# 获取选中分页
	pySubTabCtrls = property( _getSubTabCtrls )							# 获取每个分页的子选项卡，有可能某个分页没有选项卡，为 None


# --------------------------------------------------------------------
# implement TabButton for NestedTabWindow
# --------------------------------------------------------------------
class RightTabButton( TabButton ) :
	def __init__( self, btn, pyBinder = None ) :
		TabButton.__init__( self, btn, pyBinder )
		self.__text = ""
		self.__font = ""
		self.__space = 0
		count = len( btn.children )
		self.__pySTChars = [None] * count
		for n, ch in btn.children :
			if "tx_" not in n : continue
			self.__text += ch.text
			btn.delChild( ch )
		self._setText( self.__text )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setText( self, text ) :
		self.__text = text
		self.__pySTChars = []
		wtext = csstring.toWideString( text )
		count = len( wtext )
		if count == 0 : return
		center = self.width * 0.5 + 1
		pyFirst = StaticText()
		self.addPyChild( pyFirst, "tx_0" )
		pyFirst.text = wtext[0]
		pyFirst.font = self.__font
		self.__pySTChars.append( pyFirst )
		pyFirst.center = center
		height = count * pyFirst.height + ( count - 1 ) * self.__space
		pyFirst.top = ( self.height - height ) * 0.5
		top = pyFirst.bottom
		for idx, ch in enumerate( wtext[1:] ) :
			pyCh = StaticText()
			pyCh.font = self.__font
			pyCh.text = ch
			self.addPyChild( pyCh, "tx_%i" % ( idx + 1 ) )
			self.__pySTChars.append( pyCh )
			pyCh.center = center
			pyCh.top = top
			top = pyCh.bottom + self.__space

	def _setFont( self, font ) :
		self.__font = font
		count = len( wtext )
		if count == 0 : return
		pyFirst = self.__pySTChars[0]
		pyFirst.font = font
		height = count * pyFirst.height + ( count - 1 ) * self.__space
		top = ( self.height - height ) * 0.5
		for pyCh in self.__pySTChars :
			pyCh.font = font
			pyCh.top = top
			top = pyCh.bottom + self.__space

	def _setSpace( self, space ) :
		self.__space = space
		wtext = csstring.toWideString( self.__text )
		count = len( wtext )
		if count == 0 : return
		pyFirst = self.__pySTChars[0]
		height = count * pyFirst.height + ( count - 1 ) * space
		top = ( self.height - height ) * 0.5
		for pyCh in self.__pySTChars :
			pyCh.top = top
			top = pyCh.bottom + self.__space


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( lambda self : self.__text, _setText )
	font = property( lambda self : self.__font, _setFont )
	space = property( lambda self : self.__space, _setSpace )
