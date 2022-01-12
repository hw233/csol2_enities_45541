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
	ѡ�
	ѡ��ҳ�İ�ť������ "btn_" ��ͷ���������˳������ֵ
	ѡ��Ҳ�ķ�ҳ������ "panel_" ��ͷ���������˳������ֵ
	"""
	def __init__( self, tabCtrl = None, pyBinder = None ) :
		Control.__init__( self, tabCtrl, pyBinder )
		self.__pyPages = []									# ��������ѡ��ҳ
		self.__initialize( tabCtrl )
		self.__rMouseSelect = False							# �Ƿ������Ҽ�ѡ��

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
		�����¼�
		"""
		Control.generateEvents_( self )
		self.__onTabPageSelectedChanged = self.createEvent_( "onTabPageSelectedChanged" )		# ��ѡҳ�ı�ʱ������

	@property
	def onTabPageSelectedChanged( self ) :
		"""
		��ѡҳ�ı�ʱ������
		"""
		return self.__onTabPageSelectedChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layoutTabs( self ) :
		"""
		�������� tab ��ť�� Z ���꣬��ʵ��ѡ��ҳ��ť����δѡ��ҳ�İ�ť
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
		��ĳѡ��ҳѡ��ʱ������
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
		����Ĭ�Ϸ�ҳ����ע�⣺ֻ���� "btn_" ǰ׺�������ŵķ�ҳ������������Ҫ�� 0 ��ʼ���ε�����
		"""
		count = 0
		for n, ch in self.gui.children :
			if "btn_" in n :
				count +=1
		return count

	def autoSearchPages( self, PanelCls = None, BtnCls = None, tabMapMode = UIState.MODE_R3C1 ) :
		"""
		�Զ��������������з�ҳ
		@type			PanelCls	: list
		@param			PanelCls	: ���а������������б�
		@type			BtnCls	 	: list
		@param			BtnCls	 	: ���а�ť���������б�
		@type			tabMapMode	: MACRO DEFINATION
		@param			tabMapMode	: ��ť״̬ģʽ
		"""
		index = 0													# ��ʼ������Ϊ 0
		while True :												# ѭ������
			tabName = "btn_" + str( index )							# ��ť������
			btn = getattr( self.__tabCtrl, tabName, None )			# ��ȡ btn ��ť������ UI ʵ��
			if btn is None : break									# ������ť�������
			panelName = "panel_" + str( index )						# ��������
			panel = getattr( self.__tabCtrl, panelName, None )		# ��ȡ btn �������� UI ʵ��
			if panel is None : break								# �����������
			if BtnCls is None :
				pyBtn = TabButton( btn )							# ���� btn ��ť�� python UI
			else :
				pyBtn = BtnCls[index]( btn )
			pyBtn.setStatesMapping( tabMapMode )					# ���ð�ť��״̬ mapping
			if PanelCls and index < len( PanelCls ) :
				pyPanel = PanelCls[index]( panel )
			else :
				pyPanel = TabPanel( panel )							# ���� btn ����� python UI
			pyPage = TabPage( pyBtn, pyPanel )						# ���� btn ҳʵ��
			self.addPage( pyPage )									# ���һ�� btn ҳ
			index += 1												# ������������������

	def addPage( self, pyPage ) :
		"""
		���һ��ѡ��ҳ
		"""
		if pyPage in self.__pyPages :								# �Ѿ����
			ERROR_MSG( "page %s has been added!" )
			return
		pyPage.setTabCtrl__( self )									# ����ѡ��ҳ������ѡ��ؼ�
		pyPage.setIndex__( self.pageCount )							# ����ѡ��ҳ������
		pyPage.pyPanel.h_dockStyle = "HFILL"
		pyPage.pyPanel.v_dockStyle = "VFILL"
		self.__pyPages.append( pyPage )								# ��ӵ�ҳ�б�
		if self.pySelPage is None :									# ��ǰ���û��ѡ�е�ҳ
			self.__pyPages[0].selected = True						# ��Ĭ��ѡ�е�һҳ
		self.__layoutTabs()											# �������а�ť�Ĳ�ι�ϵ

	def insertPage( self, index, pyPage ) :
		"""
		����һ��ѡ��ҳ
		"""
		if pyPage in self.__pyPages :								# �Ѿ����
			ERROR_MSG( "page %s has been added!"%str( index ) )
			return
		if pyPage.selected :
			pyPage.selected = False
		pyPage.setTabCtrl__( self )									# ����ѡ��ҳ������ѡ��ؼ�
		self.__pyPages.insert( index, pyPage )						# ��ӵ�ҳ�б�
		pyPage.pyPanel.h_dockStyle = "HFILL"
		pyPage.pyPanel.v_dockStyle = "VFILL"
		for idx, pyPage in enumerate( self.__pyPages ) :
			pyPage.setIndex__( idx)									# ����ѡ��ҳ������
		if self.pySelPage is None :									# ��ǰ���û��ѡ�е�ҳ
			self.__pyPages[0].selected = True						# ��Ĭ��ѡ�е�һҳ
		self.__layoutTabs()											# �������а�ť�Ĳ�ι�ϵ

	def addPages( self, *pyPages ) :
		"""
		���һ��ѡ��ҳ
		"""
		for pyPage in pyPages :
			self.addPage( pyPage )

	def removePage( self, pyPage ) :
		"""
		ɾ��һ��ѡ��ҳ
		"""
		if pyPage not in self.__pyPages :							# ��֤ѡ��ҳ�Ƿ���ѡ��ؼ���
			ERROR_MSG( "tab page %s is not in tab control!" )
			return
		index = pyPage.index										# ��ȡɾ��ҳ������
		self.__pyPages.remove( pyPage )								# ��ҳ�б������
		pyPage.setTabCtrl__( None )									# ��ɾ��ҳ�������ؼ����
		pyPage.setIndex__( -1 )										# ����������Ϊ ��1 ��ʾû��������ѡ�
		if pyPage.selected :										# ���ɾ��ҳ�Ǳ�ѡ�е�ҳ
			pyPage.selected = False									# ��ȡ��ɾ��ҳ��ѡ��״̬
			if self.pageCount :										# �������ʣ��ҳ
				self.__pyPages[0].selected = True					# ��Ĭ��ѡ�е�һҳ
		for idx in xrange( index, self.pageCount ) :				# ��������ɾ��ҳ�ĺ���ҳ������
			self.__pyPages[idx].setIndex__( idx )

	def clearPages( self ) :
		"""
		�������ѡ��ҳ
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
	pyPages = property( lambda self : self.__pyPages[:] )								# ��ȡ���з�ҳ
	pyBtns = property( lambda self : [pyPage.pyBtn for pyPage in self.__pyPages] )		# ��ȡ���з�ҳ��ť
	pyPanels = property( lambda self : [pyPage.pyPanel for pyPage in self.__pyPages] )	# ��ȡ���з�ҳ����
	pageCount = property( lambda self : len( self.__pyPages ) )							# ��ȡ��ҳ������
	pySelPage = property( _getSelectedPage, _setSelectedPage )							# ��ȡ��ǰ��ѡ�еķ�ҳ
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )						# �Ƿ������Ҽ�ѡ��ѡ��


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
		�������� tab ҳ
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
		����״̬ mapping
		"""
		row, col = stMode
		comMapping = util.getStateMapping( self.size, stMode, UIState.ST_R1C1 )
		self.mappings_[UIState.COMMON] = comMapping
		self.mappings_[UIState.HIGHLIGHT] = comMapping
		idx = 1
		if stMode[0] * stMode[1] > 3 :										# ���� 3 ��״̬������ζ���и���״̬
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
	pyTabPage = property( _getPage )											# ��ȡ������ tab ҳ
	selected = property( SelectableButton._getSelected, _setSelected )			# ��ȡ/�����Ƿ�ѡ��



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
		self.__pyTabCtrl = None						# ������ѡ��ؼ�
		self.__pyBtn = None							# ��ѡ�ť
		self.__pyPanel = None						# ѡ�����
		self.__index = -1							# ��ѡ��е�����
		self.__events = []							# �¼��б�
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
		�����¼�
		"""
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )			# ѡ��״̬�ı�ʱ������

	@property
	def onSelectChanged( self ) :
		"""
		��ѡ��ʱ������
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelectChanged_( self, selected ) :
		"""
		ѡ�и�ҳ���� tab ��ť���ã�
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
		����һ��ѡ��ҳ�İ�ť�Ͱ���
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
		���������� tab Ctrl
		"""
		if pyTabCtrl is None :
			self.__pyTabCtrl = None
		else :
			self.__pyTabCtrl = weakref.ref( pyTabCtrl )

	def setIndex__( self, index ) :
		"""
		����ѡ��ҳ������
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
	pyTabCtrl = property( _getPyTabCtrl )							# ��ȡ������ѡ��ؼ�
	pyBtn = property( _getPyBtn )									# ��ȡ tab ��ť
	pyPanel = property( _getPyPanel )								# ��ȡ tab ����
	index = property( _getIndex )									# ��ȡ������ѡ��е�����

	enable = property( _getEnable, _setEnable )						# ��ȡ/�����Ƿ����
	selected = property( _getSelected, _setSelected )				# ��ȡ/�����Ƿ�ѡ��
