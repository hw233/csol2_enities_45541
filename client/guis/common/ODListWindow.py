# -*- coding: gb18030 -*-
#
# $Id: ODListWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement ownerdraw list window class

2009/03/17: writen by huangyongwei
"""

import weakref
from guis import *
from guis.util import copyGuiTree
from FlexExWindow import HVFlexExWindow
from PyGUI import PyGUI
from RootGUI import RootGUI
from guis.controls.ODListPanel import ODListPanel

"""
composing :
	sbBox( GUI.Window )				# ��������
		-- l ( GUI.Simple )
		-- r ( GUI.Simple )
		-- t ( GUI.Simple )
		-- b ( GUI.Simple )
		-- lt ( GUI.Simple )
		-- rt ( GUI.Simple )
		-- lb ( GUI.Simple )
		-- rb ( GUI.Simple )
		-- splitter
		-- clipPanel ( GUI.Window )
		-- scrollBar ( GUI.Window )
			-- just likes HScrollBar
"""

class ODListWindow( HVFlexExWindow ) :
	__cg_wnd			= None
	__cc_view_count		= 6

	def __init__( self, wnd = None, pyBinder = None ) :
		if ODListWindow.__cg_wnd is None :
			ODListWindow.__cg_wnd = GUI.load( "guis_v2/common/odlistwindow/wnd.gui" )
		if wnd is None :
			wnd = copyGuiTree( ODListWindow.__cg_wnd )
			uiFixer.firstLoadFix( wnd )
		HVFlexExWindow.__init__( self, wnd )
		self.moveFocus = False													# ������������϶�
		self.posZSegment = ZSegs.L2												# ���ڵڶ��� UI
		self.activable_ = False													# �����Ա�����
		self.escHide_ 		 = True												# ������ ESC ������
		self.addToMgr( "comboBoxListMenu" )

		self.__pyBinder = None
		if pyBinder : self.__pyBinder = weakref.ref( pyBinder )

		splitter = wnd.elements['splitter']
		self.__spRight = wnd.width - splitter.position.x						# �ָ�����ߵ������ұߵľ���
		self.__spHightShort = wnd.height - splitter.size.y						# �ָ����ȴ��ڶ̶���
		self.__sbarRight = wnd.width - s_util.getGuiLeft( wnd.sbar )			# ��������ߵ������ұߵľ���
		self.__sbarHeightShort = wnd.height - wnd.sbar.height					# �������ȴ��ڶ̶���
		self.__viewCount = 6													# ����ѡ������
		self.__initialize( wnd )

	def __initialize( self, wnd ) :
		self.pyListPanel_ = ODListPanel( wnd.clipPanel, wnd.sbar )				# ѡ���б����
		self.pyListPanel_.h_dockStyle = "HFILL"
		self.pyListPanel_.onViewItemInitialized.bind( self.onViewItemInitialized_ )
		self.pyListPanel_.onDrawItem.bind( self.onDrawItem_ )
		self.pyListPanel_.onItemSelectChanged.bind( self.onItemSelectChanged_ )
		self.pyListPanel_.onItemLClick.bind( self.onItemLClick_ )
		self.pyListPanel_.onItemRClick.bind( self.onItemRClick_ )
		self.pyListPanel_.onItemMouseEnter.bind( self.onItemMouseEnter_ )
		self.pyListPanel_.onItemMouseLeave.bind( self.onItemMouseLeave_ )
		self.pySBar_ = self.pyListPanel_.pySBar

		self.__hideScrollBar()
		self.viewCount = self.__cc_view_count									# Ĭ����ʾ 6 ��ѡ��

	def __del__( self ) :
		HVFlexExWindow.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		HVFlexExWindow.generateEvents_( self )
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# ��ʼ������ѡ��ʱ������
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# �ػ�ѡ��ʱ������
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# ĳ��ѡ�ѡ��ʱ����
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# ���������ʱ������
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# ����Ҽ����ʱ������
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# ������ѡ���Ǳ�����
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# ���뿪ѡ���Ǳ�����

	@property
	def onViewItemInitialized( self ) :
		return self.__onViewItemInitialized						# ����ѡ���ʼ��ʱ������

	@property
	def onDrawItem( self ) :									# ѡ����Ҫ�ػ�ʱ������
		return self.__onDrawItem

	@property
	def onItemSelectChanged( self ) :							# ĳ��ѡ��ѡ��ʱ������
		return self.__onItemSelectChanged

	@property
	def onItemLClick( self ) :									# ������ĳѡ��ʱ������
		return self.__onItemLClick

	@property
	def onItemRClick( self ) :									# �Ҽ����ĳѡ��ʱ������
		return self.__onItemRClick

	@property
	def onItemMouseEnter( self ) :								# ������ѡ��ʱ��
		return self.__onItemMouseEnter

	@property
	def onItemMouseLeave( self ) :								# ����뿪ѡ��ʱ��
		return self.__onItemMouseLeave


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setPanelHeight( self, itemCount = None ) :
		"""
		���ð���߶ȣ�ע�⣺�п����ػ����ֻ�ȫ��ѡ�
		"""
		if itemCount is None :
			itemCount = self.itemCount
		count = min( itemCount, self.__viewCount )
		panelHeight = count * self.itemHeight
		height = panelHeight + 2 * self.pyListPanel_.top
		HVFlexExWindow._setHeight( self, height )
		self.pyListPanel_.height = panelHeight
		self.pySBar_.height = height - self.__sbarHeightShort
		self.txelems["splitter"].size.y = height - self.__spHightShort
		self.txelems["sbar_bg"].size.y = panelHeight

	def __showScrollBar( self ) :
		"""
		��ʾ������
		"""
		self.pySBar_.visible = True
		splitter = self.txelems['splitter']
		splitter.visible = True
		sbar_bg = self.txelems['sbar_bg']
		sbar_bg.visible = True
		self.pyListPanel_.width = splitter.position.x - self.pyListPanel_.left + 3

	def __hideScrollBar( self ) :
		"""
		���ع�����
		"""
		self.pySBar_.visible = False
		self.txelems['splitter'].visible = False
		self.txelems['sbar_bg'].visible = False
		self.pyListPanel_.width = self.width - 2 * self.pyListPanel_.left + 3

	def __setScrollState( self ) :
		"""
		���ù�����״̬
		"""
		if self.isOverView() :
			self.__showScrollBar()
		else :
			self.__hideScrollBar()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		��һ������ѡ���ʼ�����ʱ������
		"""
		self.onViewItemInitialized( pyViewItem )

	def onDrawItem_( self, pyViewItem ) :
		"""
		��һ��ѡ����Ҫ�ػ�ʱ������
		"""
		self.onDrawItem( pyViewItem )

	def onItemSelectChanged_( self, index ) :
		"""
		��һ��ѡ�ѡ��ʱ����
		"""
		self.onItemSelectChanged( index )

	def onItemLClick_( self, index ) :
		"""
		��һ��ѡ����������ʱ����
		"""
		self.onItemLClick( index )

	def onItemRClick_( self, index ) :
		"""
		��һ��ѡ�����Ҽ����ʱ����
		"""
		self.onItemRClick( index )

	def onItemMouseEnter_( self, pyViewItem ) :
		"""
		��������ѡ��ʱ������
		"""
		self.onItemMouseEnter( pyViewItem )

	def onItemMouseLeave_( self, pyViewItem ) :
		"""
		������뿪ѡ��ʱ������
		"""
		self.onItemMouseLeave( pyViewItem )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onActivated( self ) :
		"""
		�����ڼ���ʱ������
		"""
		RootGUI.onActivated( self )
		self.pyListPanel_.tabStop = True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isOverView( self ) :
		"""
		ѡ���������Ƿ񳬳�����ѡ������
		"""
		return self.itemCount > self.viewCount

	# -------------------------------------------------
	def abandonRedraw( self ) :
		"""
		ʹѡ����ʱ�����ػ��������� insistRedraw ���׳��֣�
		"""
		self.pyListPanel_.abandonRedraw()

	def insistRedraw( self ) :
		"""
		�ָ�ѡ���ػ��������� abandonRedraw ���׳��֣��� abandonRedraw ֮����ã�
		"""
		self.pyListPanel_.insistRedraw()

	# -------------------------------------------------
	def addItem( self, item ) :
		"""
		���һ��ѡ��
		"""
		itemCount = self.itemCount
		if itemCount == self.__viewCount :
			self.pyListPanel_.abandonRedraw()				# ���ѡ��ʱ��Ҫ�ػ�ѡ��
			self.pyListPanel_.addItem( item )
			self.pyListPanel_.insistRedraw()				# �ָ��ػ�ѡ��
			self.__setScrollState()							# ������ػ�����ѡ��
		elif itemCount < self.__viewCount :					# ��ѡ��������С�ڿ���ѡ��ʱ
			self.pyListPanel_.abandonRedraw()				#ʹѡ����ʱ�����ػ�
			self.__setPanelHeight( itemCount + 1 )			# ����ѡ������ʵʱ���ð���߶�
			self.pyListPanel_.insistRedraw()				# �ָ��ػ�ѡ��
			self.pyListPanel_.addItem( item )
		else :												# ���ѡ���������ڿ���ѡ����
			self.pyListPanel_.addItem( item )
		self.pySBar_.value = 0

	def addItems( self, items ) :
		"""
		���һ��ѡ��
		"""
		addCount = len( items )
		if not addCount : return
		itemCount = self.itemCount
		newCount = itemCount + addCount
		if newCount <= self.__viewCount :					# ��ѡ����С�ڿ���ѡ����
			self.pyListPanel_.abandonRedraw()				# ɾ��ѡ��ʱ����Ҫ�ػ�ѡ��
			self.__setPanelHeight( newCount )				# ����ѡ������ʵʱ���ð���߶�
			self.pyListPanel_.insistRedraw()				# �ָ��ػ�ѡ��
			self.pyListPanel_.addItems( items )
		elif itemCount <= self.__viewCount :				# ��ѡ�������ڿ���ѡ�������������֮ǰ��ѡ����С�ڿ���ѡ����
			self.pyListPanel_.abandonRedraw()				# ɾ��ѡ��ʱ����Ҫ�ػ�ѡ��
			if itemCount < self.__viewCount :
				self.__setPanelHeight( newCount )			# ����ѡ������ʵʱ���ð���߶�
			self.pyListPanel_.addItems( items )
			self.pyListPanel_.insistRedraw()				# �ָ��ػ�ѡ��
			self.__setScrollState()							# �������ù������Ƿ�ɼ�ʱ�����ػ�����ѡ��
		else :												# ���֮ǰ��ѡ�����ʹ��ڿ���ѡ����
			self.pyListPanel_.addItems( items )
		self.pySBar_.value = 0

	def removeItem( self, item ) :
		"""
		ɾ��һ��ѡ��
		"""
		if item not in self.pyListPanel_.items :
			raise ValueError( "item %s is not exist!" % str( item ) )
		index = self.pyListPanel_.items.index( item )
		self.removeItemOfIndex( index )

	def removeItemOfIndex( self, index ) :
		"""
		ɾ��ָ����������ѡ��
		"""
		itemCount = self.itemCount
		if index < 0 or index >= itemCount :
			raise IndexError( "index %i out of range!" % index )
		if itemCount <= 1 :
			self.hide()

		if itemCount == self.__viewCount + 1 :
			self.pyListPanel_.abandonRedraw()				# ��Ҫ�ػ�ѡ��
			self.pyListPanel_.removeItemOfIndex( index )
			self.pyListPanel_.insistRedraw()				# �ָ��ػ�ѡ��
			self.__setScrollState()
		elif itemCount <= self.__viewCount :
			self.pyListPanel_.abandonRedraw()				# ��Ҫ�ػ�ѡ��
			self.pyListPanel_.removeItemOfIndex( index )
			self.__setPanelHeight( itemCount - 1 )			# ����ѡ������ʵʱ���ð���߶�
			self.pyListPanel_.insistRedraw()				# �ָ��ػ�ѡ��
		else :
			self.pyListPanel_.removeItemOfIndex( index )

	def clearItems( self ) :
		"""
		�������ѡ��
		"""
		self.hide()
		self.pyListPanel_.clearItems()
		self.__setScrollState()

	def updateItem( self, index, item ) :
		"""
		����ָ��ѡ��
		"""
		self.pyListPanel_.updateItem( index, item )

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		��ȡָ��������ѡ��
		"""
		return self.pyListPanel_.getItem( index )

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		ѡ�е�ǰѡ��ѡ���ǰһ��ѡ��
		"""
		self.pyListPanel_.upSelect()

	def downSelect( self ) :
		"""
		ѡ�е�ǰѡ��ѡ��ĺ�һ��ѡ��
		"""
		self.pyListPanel_.downSelect()

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		��������ѡ��
		"""
		self.pyListPanel_.sort( cmp, key, reverse )

	# -------------------------------------------------
	def show( self ) :
		if self.itemCount == 0 :
			return False
		self.pyListPanel_.resetState()
		HVFlexExWindow.show( self )
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	def _getViewCount( self ) :
		return self.__viewCount

	def _setViewCount( self, count ) :
		self.__viewCount = max( 2, count )
		self.__setPanelHeight()

	def _setOwnerDraw( self, ownerdraw ) :
		self.pyListPanel_._setOwnerDraw( ownerdraw )

	# -------------------------------------------------
	def _setItemHeight( self, height ) :
		assert height > 0, "item height must more then 0!"
		self.pyListPanel_.abandonRedraw()
		self.__setPanelHeight()
		self.pyListPanel_.insistRedraw()
		self.pyListPanel_.itemHeight = height

	# ---------------------------------------
	def _setWidth( self, width ) :
		HVFlexExWindow._setWidth( self, width )
		splitter = self.txelems["splitter"]
		splitter.position.x = self.width - self.__spRight 
		sbar_bg = self.txelems["sbar_bg"]
		sbar_bg.position.x = self.width - self.__spRight 
		self.pySBar_.left = self.width - self.__sbarRight + 1


	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )
	ownerDraw = property( lambda self : self.pyListPanel_.ownerDraw, _setOwnerDraw )			# bool: �Ƿ����Ի�ѡ���
	items = property( lambda self : self.pyListPanel_.items )									# list: ��ȡ����ѡ��
	itemCount = property( lambda self : self.pyListPanel_.itemCount )							# int: ��ȡѡ������
	viewCount = property( _getViewCount, _setViewCount )										# int: ��ȡ����ѡ������( ������ڻ���� 2 )
	perScrollCount = property( lambda self : self.pyListPanel_.perScrollCount, \
		lambda self, v : self.pyListPanel_._setPerScrollCount( v ) )							# int: ��ȡ/���������ֻ���һ�¹�����ѡ������
	autoSelect = property( lambda self : self.pyListPanel_.autoSelect, \
		lambda self, v : self.pyListPanel_._setAutoSelect( v ) )								# bool: �κ�ʱ���Ƿ��Զ�ѡ��һ��
	selItem = property( lambda self : self.pyListPanel_.selItem, \
		lambda self, v : self.pyListPanel_._setSelItem( v ) )									# ���͸����û������ѡ�����: ��ȡ/���õ�ǰѡ�е�ѡ��
	selIndex = property( lambda self : self.pyListPanel_.selIndex, \
		lambda self, v : self.pyListPanel_._setSelIndex( v ) )									# int: ��ȡ/���õ�ǰѡ�е�����
	pyViewItems = property( lambda self : self.pyListPanel_.pyViewItems )						# list of ODListPanel.ViewItem: ��ȡ���п���ѡ��

	font = property( lambda self : self.pyListPanel_.font, \
		lambda self, v : self.pyListPanel_._setFont( v ) )										# str: ��ȡ/����ѡ������
	itemCommonForeColor = property( lambda self : self.pyListPanel_.itemCommonForeColor, \
		lambda self, v : self.pyListPanel_._setItemCommonForeColor( v ) )						# tuple: ��ȡ/������ͨ״̬��ѡ���ǰ��ɫ
	itemCommonBackColor = property( lambda self : self.pyListPanel_.itemCommonBackColor, \
		lambda self, v : self.pyListPanel_._getItemCommonBackColor( v ) )						# tuple: ��ȡ/������ͨ״̬��ѡ��ı���ɫ
	itemHighlightForeColor = property( lambda self : self.pyListPanel_.itemHighlightForeColor, \
		lambda self, v : self.pyListPanel_._setItemHighlightForeColor( v ) )					# tuple: ��ȡ/���ø���״̬��ѡ���ǰ��ɫ
	itemHighlightBackColor = property( lambda self : self.pyListPanel_.itemHighlightBackColor,\
		lambda self, v : self.pyListPanel_._setItemHighlightBackColor( v ) )					# tuple: ��ȡ/���ø���״̬��ѡ���ǰ��ɫ
	itemSelectedForeColor = property( lambda self : self.pyListPanel_.itemSelectedForeColor, \
		lambda self, v : self.pyListPanel_._setItemSelectForeColor( v ) )						# tuple: ��ȡ/����ѡ��״̬��ѡ���ǰ��ɫ
	itemSelectedBackColor = property( lambda self : self.pyListPanel_.itemSelectedBackColor, \
		lambda self, v : self.pyListPanel_._setItemSelectBackColor( v ) )						# tuple: ��ȡ/����ѡ��״̬��ѡ���ǰ��ɫ
	itemDisableForeColor = property( lambda self : self.pyListPanel_.itemDisableForeColor, \
		lambda self, v : self.pyListPanel_._setItemDisableForeColor( v ) )						# tuple: ��ȡ/������Ч״̬��ѡ���ǰ��ɫ
	itemDisableBackColor = property( lambda self : self.pyListPanel_.itemDisableBackColor, \
		lambda self, v : self.pyListPanel_._setItemDisableBackColor( v ) )						# tuple: ��ȡ/������Ч״̬��ѡ���ǰ��ɫ

	tabStop = property( lambda self : self.pyListPanel_.tabStop, \
		lambda self, v : self.pyListPanel_._setTabStop( v ) )									# bool: ��ȡ/���ý���

	itemHeight = property( lambda self : self.pyListPanel_.itemHeight, _setItemHeight )			# float: ��ȡ/����ѡ��߶�
	width = property( HVFlexExWindow._getWidth, _setWidth )										# float: ��ȡ/���ÿ��
	height = property( HVFlexExWindow._getHeight )												# float: ���߶�����Ϊֻ��
