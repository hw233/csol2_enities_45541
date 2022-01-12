# -*- coding: gb18030 -*-
#
# $Id: ComboBox.py,v 1.34 2008-08-26 02:12:45 huangyongwei Exp $

"""
implement ownerdraw combobox component
2009.02.07: modified by huangyongwei
"""

"""
composing :
	GUI.Window
		btnDown( GUI.Simple or GUI.Window )
		box( GUI.Window ) : ��� box ��Ϊ pyBox ���룬���������û��
			-- lbView ( GUI.Text )
"""

import weakref
from AbstractTemplates import AbstractClass
from guis import *
from guis.common.ODListWindow import ODListWindow
from Control import Control
from BaseInput import BaseInput
from TextBox import TextBox
from StaticText import StaticText
from Button import Button


# --------------------------------------------------------------------
# implement combobox class
# --------------------------------------------------------------------
class ODComboBox( Control ) :
	def __init__( self, comboBox = None, clsBox = None, pyBinder = None ) :
		Control.__init__( self, comboBox, pyBinder )
		self.__initialize( comboBox, clsBox )
		self.__selIndex = -1

		self.readOnly = True

	def __initialize( self, comboBox, clsBox ) :
		if clsBox is None :
			self.pyBox_ = InputBox( comboBox.box, self )
		elif not issubclass( clsBox, IBox ) :
			raise TypeError( "box for combobox must implement IBox interface!" )
		elif not issubclass( clsBox, Control ) :
			raise TypeError( "box for combobox must inherit from Control!" )
		else :
			self.pyBox_ = clsBox( comboBox.box, self )
		self.pyBox_.h_dockStyle = "HFILL"
		self.pyBox_.onKeyDown.bind( self.onKeyDown_ )
		self.pyBox_.onLMouseDown.bind( self.onViewBoxLMouseDown_ )
		self.pyBox_.onTabIn.bind( self.onTabIn_ )
		self.pyBox_.onTabOut.bind( self.__onBoxTabOut )

		self.pyComboList_ = ComboList( self )
		self.pyComboList_.onViewItemInitialized.bind( self.onViewItemInitialized_ )
		self.pyComboList_.onDrawItem.bind( self.onDrawItem_ )
		self.pyComboList_.onItemSelectChanged.bind( self.pyBox_.onItemPreSelectChanged_ )
		self.pyComboList_.onItemLClick.bind( self.onItemLClick_ )
		self.pyComboList_.onItemRClick.bind( self.onItemRClick_ )
		self.pyComboList_.onItemMouseEnter.bind( self.onItemMouseEnter_ )
		self.pyComboList_.onItemMouseLeave.bind( self.onItemMouseLeave_ )
		self.pyComboList_.width = self.width

		self.pyBtnDown_ = Button( comboBox.btnDown )
		self.pyBtnDown_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnDown_.h_dockStyle = "RIGHT"
		self.pyBtnDown_.onLClick.bind( self.__onBtnDownClick )

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ODComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Control.generateEvents_( self )
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# ����ѡ���ʼ��ʱ������
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# ѡ���ػ�ʱ������
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# ѡ��ѡ��ʱ������
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# ���������ѡ��ʱ������
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# ����Ҽ����ѡ��ʱ������
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# ������ѡ���Ǳ�����
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# ���뿪ѡ���Ǳ�����
		self.__onBeforeDropDown = self.createEvent_( "onBeforeDropDown" )				# ��ѡ���б�ǰ������
		self.__onAfterDropDown = self.createEvent_( "onAfterDropDown" )					# ��ѡ���б�󱻴���
		self.__onBeforeCollapsed = self.createEvent_( "onBeforeCollapsed" )				# �ر�ѡ���б�ǰ������
		self.__onAfterCollapsed = self.createEvent_( "onAfterCollapsed" )				# �ر�ѡ���б�󱻴���

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

	@property
	def onBeforeDropDown( self ) :								# չ��ѡ���б�ǰ������
		return self.__onBeforeDropDown

	@property
	def onAfterDropDown( self ) :								# չ��ѡ���б�󱻴���
		return self.__onAfterDropDown

	@property
	def onBeforeCollapsed( self ) :								# ��£ѡ���б�ǰ������
		return self.__onBeforeCollapsed

	@property
	def onAfterCollapsed( self ) :								# ��£ѡ���б�󱻴���
		return self.__onAfterCollapsed


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __locateComboList( self ) :
		"""
		�����б�λ��
		"""
		if not self.visible : return
		self.pyComboList_.left = self.leftToScreen
		scHeight = BigWorld.screenHeight()
		height = self.pyComboList_.height
		bottom = self.bottomToScreen
		if bottom + height <= scHeight :
			self.pyComboList_.top = bottom
		else :
			self.pyComboList_.bottom = self.topToScreen

	# -------------------------------------------------
	def __selectItem( self, index, updateView ) :
		"""
		ѡ��ָ������ѡ��
		updateView ָʾ����� box �е����ݸ�ѡ��ѡ�һ�µĻ����Ƿ�����Ϊһ��
		"""
		if index != self.pyComboList_.selIndex :
			self.pyComboList_.selIndex = index
		if self.__selIndex != index :
			self.__selIndex = index
			if updateView and self.viewItem != self.selItem :		# ֻ�� readonly Ϊ False ʱ���Ż������������һ��
				self.pyBox_.onItemSelectChanged_( index )
			self.onItemSelectChanged_( index )
		elif updateView and self.viewItem != self.selItem :			# ֻ�� readonly Ϊ False ʱ���Ż������������һ��
			self.pyBox_.onItemSelectChanged_( index )

	# -------------------------------------------------
	def __onBtnDownClick( self ) :
		"""
		������ť�����ʱ����
		"""
		if self.isDropped :
			self.collapse( False, False )
		else :
			self.dropDown()

	# -------------------------------------------------
	def __onBoxTabOut( self ) :
		"""
		���㳷�� Box ʱ������
		"""
		self.onTabOut_()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		��������ʱ�����ã����б�򽹵��� Box ��ʱ�����ã�
		"""
		if self.pyComboList_.onComboKeyDown_( key, mods ) :
			return True
		return self.onKeyDown( key, mods )

	def onViewBoxLMouseDown_( self ) :
		"""
		����� Box �ϰ���ʱ������
		"""
		if self.readOnly :							# ���ֻ��
			self.__onBtnDownClick()					# �򣬵�������ʱ����ʾѡ���б�

	def onTabOut_( self ) :
		"""
		ʧȥ����ʱ������( ������ box ʧȥ����Ҳ�ᱻ���� )
		"""
		Control.onTabOut_( self )
		if self.isDropped :
			self.collapse( False, False )

	# -------------------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		��һ������ѡ���ʼ������Ǳ�����
		"""
		self.onViewItemInitialized( pyViewItem )

	def onDrawItem_( self, pyViewItem ) :
		"""
		ĳ��ѡ���ػ�ʱ������
		"""
		self.onDrawItem( pyViewItem )

	def onItemSelectChanged_( self, index ) :
		"""
		ѡ��ѡ��ʱ������
		"""
		self.onItemSelectChanged( index )

	def onItemLClick_( self, index ) :
		"""
		ĳ��ѡ����������ʱ����
		"""
		self.collapse( True, True )
		self.onItemLClick( index )

	def onItemRClick_( self, index ) :
		"""
		ĳ��ѡ�����Ҽ����ʱ����
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

	# ---------------------------------------
	def onBeforeDropDown_( self ) :
		"""
		��ʾѡ���б�ǰ������
		"""
		self.pyBox_.onBeforeDropDown_()
		self.onBeforeDropDown()

	def onAfterDropDown_( self ) :
		"""
		��ʾѡ���б�󱻵���
		"""
		self.pyBox_.onAfterDropDown_()
		self.onAfterDropDown()

	def onBeforeCollapsed_( self ) :
		"""
		�ر�ѡ���б�ǰ������
		"""
		self.pyBox_.onBeforeCollapsed_()
		self.onBeforeCollapsed()

	def onAfterCollapsed_( self ) :
		"""
		�ر�ѡ���б�󱻵���
		"""
		self.pyBox_.onAfterCollapsed_()
		self.onAfterCollapsed()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		"""
		ָ������Ƿ����ڿؼ�����
		"""
		if self.pyBox_.isMouseHit() :
			return True
		if self.pyBtnDown_.isMouseHit() :
			return True
		return False

	# -------------------------------------------------
	def addItem( self, item ) :
		"""
		���һ��ѡ��
		"""
		self.pyComboList_.addItem( item )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def addItems( self, items ) :
		"""
		���һ��ѡ��
		"""
		self.pyComboList_.addItems( items )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def removeItem( self, item ) :
		"""
		ɾ��ָ��ѡ��
		"""
		self.pyComboList_.removeItem( item )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def removeItemOfIndex( self, index ) :
		"""
		ɾ��ָ��������ѡ��
		"""
		self.pyComboList_.removeItemOfIndex( index )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def clearItems( self ) :
		"""
		�������ѡ��
		"""
		self.pyComboList_.clearItems()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def updateItem( self, index, item ) :
		"""
		����ָ��ѡ��
		"""
		updateView = self.viewItem == self.selItem
		self.pyComboList_.updateItem( index, item )
		if index == self.__selIndex and updateView :
			self.__selectItem( self.pyComboList_.selIndex, True )

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		��ȡָ����������ѡ��
		"""
		return self.pyComboList_.getItem( index )

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		��������ѡ��
		"""
		self.pyComboList_.sort( cmp, key, reverse )
		self.__selectItem( self.pyComboList_.selIndex, False )

	# -------------------------------------------------
	def isOverView( self ) :
		"""
		ѡ���������Ƿ񳬳�����ѡ������
		"""
		return self.itemCount > self.viewCount

	# ---------------------------------------
	def abandonRedraw( self ) :
		"""
		ʹѡ����ʱ�����ػ��������� insistRedraw ���׳��֣�
		"""
		self.pyComboList_.abandonRedraw()

	def insistRedraw( self ) :
		"""
		�ָ�ѡ���ػ��������� abandonRedraw ���׳��֣��� abandonRedraw ֮����ã�
		"""
		self.pyComboList_.insistRedraw()

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		ѡ�е�ǰѡ��ѡ���ǰһ��ѡ��
		"""
		if self.itemCount == 0 :
			return
		if self.__selIndex <= 0 :
			self.selIndex = self.itemCount - 1
		else :
			self.selIndex -= 1

	def downSelect( self ) :
		"""
		ѡ�е�ǰѡ��ѡ��ĺ�һ��ѡ��
		"""
		if self.itemCount == 0 :
			return
		if self.__selIndex >= self.itemCount :
			self.selIndex = 0
		else :
			self.selIndex += 1

	def selectItemViaKey( self, fnItemKey ) :
		"""
		ѡ���� key ���ص�ָ��ѡ����ѡ�гɹ��򷵻� True�����򷵻� False
		@type				fnItemKey : callable object
		@param				fnItemKey : ѡ key �ص�����������������index����ѡ��������item����ѡ�
		"""
		if self.pyComboList_.selectItemViaKey( fnItemKey ) :
			self.__selectItem( self.pyComboList_.selIndex, True )

	# -------------------------------------------------
	def dropDown( self ) :
		"""
		��������ʾ��ѡ���б�
		"""
		if self.isDropped : return
		self.onBeforeDropDown_()
		if self.itemCount == 0 : return
		self.__locateComboList()
		self.pyComboList_.show()
		if self.readOnly :
			self.tabStop = True
		self.onAfterDropDown_()

	def collapse( self, confirmSelect = False, updateView = False ) :
		"""
		�۵������أ�ѡ���б�
		@type			confirmSelect : bool
		@param			confirmSelect : �Ƿ�ȷ��ѡ���б���ѡ�е�ѡ��
		@type			updateView	  : bool
		@param			updateView	  : ��� box �е����ݸ�ѡ���ͬʱ���Ƿ���� box �е����ݣ�ֻ�� readOnly == False ʱ�����ã�
		"""
		if not self.isDropped : return
		index = self.__selIndex
		if confirmSelect :
			index = self.pyComboList_.selIndex
		self.__selectItem( index, updateView )			# �ָ�Ϊչ��ǰ��ѡ��ѡ��
		self.onBeforeCollapsed_()						# ������£�б��¼�
		self.pyComboList_.hide()
		self.onAfterCollapsed_()
		if self.readOnly :								# �����ֻ��
			self.tabStop = False						# �򣬳�������


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSelIndex( self ) :
		return self.__selIndex

	def _setSelIndex( self, index ) :
		self.__selectItem( index, True )

	def _getSelItem( self ) :
		if self.__selIndex < 0 : return None
		return self.items[self.__selIndex]

	def _setSelItem( self, item ) :
		self.pyComboList_.selItem = item
		self.__selectItem( self.pyComboList_.selIndex, True )

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyComboList_.font

	def _setFont( self, font ) :
		self.pyComboList_.font = font

	# ---------------------------------------
	def _getTabStop( self ) :
		if self.readOnly :
			if self.isDropped :
				return Control._getTabStop( self )
			return False
		return self.pyBox_.tabStop

	def _setTabStop( self, tabStop ) :
		if self.readOnly :
			Control._setTabStop( self, tabStop )
		else :
			self.pyBox_.tabStop = tabStop

	def _setReadOnly( self, readOnly ) :
		self.pyBox_.readOnly = readOnly
		if readOnly and self.isDropped :
			Control._setTabStop( self, True )
		if readOnly :
			if self.viewItem != self.selItem :						# ��Ϊֻ������� box �е��ı���ѡ���ı���һ��
				self.pyBox_.onItemSelectChanged_( self.selIndex )	# ��֪ͨ box �����ı�

	def _setItemHeight( self, height ) :
		self.pyComboList_._setItemHeight( height )

	# -------------------------------------------------
	def _setAutoSelect( self, autoSelect ) :
		self.pyComboList_.autoSelect = autoSelect

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		self.pyComboList_.width = width


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyViewItems = property( lambda self : self.pyComboList_.pyViewItems )						# list of ODListPanel.ViewItem: ��ȡ���п���ѡ��
	selIndex = property( _getSelIndex, _setSelIndex )											# int ��ǰѡ�е�ѡ������
	selItem = property( _getSelItem, _setSelItem )												# ����Ϊ addItem ʱ�����ѡ�����ͣ���ǰѡ�е�ѡ��
	font = property( _getFont, _setFont )														# str: ����]
	width = property( Control._getWidth, _setWidth )											# float: ���
	tabStop = property( _getTabStop, _setTabStop )												# bool: ��ȡ/�������뽹��

	# ���������
	pyBox = property( lambda self : self.pyBox_ )												# IBox: ��ȡ ComboBox �� Box ���֣������ⲿ��ʵΪ������֮�٣���Ϊ�˷��㣬��ʱ����
	viewItem = property( lambda self : self.pyBox_.getViewItem_(), \
		lambda self, v : self.pyBox_.setViewItem_( v ) )										# ����Ϊ addItem ʱ�����ѡ�����ͣ���ȡ/����ѡ��ѡ��

	readOnly = property( lambda self : self.pyBox_.readOnly, _setReadOnly )						# bool: �Ƿ���ֻ��

	# �����б�����
	ownerDraw = property( lambda self : self.pyComboList_.ownerDraw, \
		lambda self, v : self.pyComboList_._setOwnerDraw( v ) )									# bool: �Ƿ����Ի�ѡ���
	isDropped = property( lambda self : self.pyComboList_.visible )								# bool: �Ƿ�������״̬
	items = property( lambda self : self.pyComboList_.items )									# list: ��ȡ����ѡ��
	itemHeight = property( lambda self : self.pyComboList_.itemHeight, _setItemHeight )			# float: ��ȡ/����ѡ��߶�
	itemCount = property( lambda self : self.pyComboList_.itemCount )							# int: ��ȡѡ������
	viewCount = property( lambda self : self.pyComboList_.viewCount, \
		lambda self, v : self.pyComboList_._setViewCount( v ) )									# int: ��ȡ����ѡ������( ������ڻ���� 2 )
	perScrollCount = property( lambda self : self.pyComboList_.perScrollCount, \
		lambda self, v : self.pyComboList_._setPerScrollCount( v ) )							# int: ��ȡ/���������ֻ���һ�¹�����ѡ������
	autoSelect = property( lambda self : self.pyComboList_.autoSelect, _setAutoSelect )			# bool: �κ�ʱ���Ƿ��Զ�ѡ��һ��
	itemCommonForeColor = property( lambda self : self.pyComboList_.itemCommonForeColor, \
		lambda self, v : self.pyComboList_._setItemCommonForeColor( v ) )						# tuple: ��ȡ/������ͨ״̬��ѡ���ǰ��ɫ
	itemCommonBackColor = property( lambda self : self.pyComboList_.itemCommonBackColor, \
		lambda self, v : self.pyComboList_._getItemCommonBackColor( v ) )						# tuple: ��ȡ/������ͨ״̬��ѡ��ı���ɫ
	itemHighlightForeColor = property( lambda self : self.pyComboList_.itemHighlightForeColor, \
		lambda self, v : self.pyComboList_._setItemHighlightForeColor( v ) )					# tuple: ��ȡ/���ø���״̬��ѡ���ǰ��ɫ
	itemHighlightBackColor = property( lambda self : self.pyComboList_.itemHighlightBackColor,\
		lambda self, v : self.pyComboList_._setItemHighlightBackColor( v ) )					# tuple: ��ȡ/���ø���״̬��ѡ���ǰ��ɫ
	itemSelectedForeColor = property( lambda self : self.pyComboList_.itemSelectedForeColor, \
		lambda self, v : self.pyComboList_._setItemSelectForeColor( v ) )						# tuple: ��ȡ/����ѡ��״̬��ѡ���ǰ��ɫ
	itemSelectedBackColor = property( lambda self : self.pyComboList_.itemSelectedBackColor, \
		lambda self, v : self.pyComboList_._setItemSelectBackColor( v ) )						# tuple: ��ȡ/����ѡ��״̬��ѡ���ǰ��ɫ
	itemDisableForeColor = property( lambda self : self.pyComboList_.itemDisableForeColor, \
		lambda self, v : self.pyComboList_._setItemDisableForeColor( v ) )						# tuple: ��ȡ/������Ч״̬��ѡ���ǰ��ɫ
	itemDisableBackColor = property( lambda self : self.pyComboList_.itemDisableBackColor, \
		lambda self, v : self.pyComboList_._setItemDisableBackColor( v ) )						# tuple: ��ȡ/������Ч״̬��ѡ���ǰ��ɫ


# --------------------------------------------------------------------
# implement combo viewer for comobox
# ע�⣺�� ComboBox Ϊ IBox ����Ԫ��
# --------------------------------------------------------------------
class IBox( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self, pyCombo ) :
		self.__pyCombo = weakref.ref( pyCombo )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onBeforeDropDown_( self ) :
		"""
		��ʾѡ���б�ǰ������
		"""
		pass

	def onAfterDropDown_( self ) :
		"""
		��ʾѡ���б�󱻵���
		"""
		pass

	def onBeforeCollapsed_( self ) :
		"""
		�ر�ѡ���б�ǰ������
		"""
		pass

	def onAfterCollapsed_( self ) :
		"""
		�ر�ѡ���б�󱻵���
		"""
		pass

	# -------------------------------------------------
	def getExposedAttr_( self, name ) :
		"""
		ͨ����д�÷������԰� Box ������ת��Ϊ ComboBox ������
		"""
		raise AttributeError( "ComboBox has no attribute '%s'." % name )

	def setExposedAttr_( self, name, value ) :
		"""
		ͨ����д�÷������԰� Box ������ת��Ϊ ComboBox ������
		"""
		raise AttributeError( "ComboBox has no attribute '%s'." % name )

	def getViewItem_ ( self ) :
		"""
		��ȡ��ǰ Box �е����ݣ���� readOnly Ϊ True���������� selItem ��
		"""
		pass

	def setViewItem_( self, viewItem ) :
		"""
		���õ�ǰ Box �е����ݣ���� readOnly Ϊ True������Ӧ������һ��
		"""
		raise AttributeError( "can't set attribute" )

	# -------------------------------------------------
	def onItemPreSelectChanged_( self, index ) :
		"""
		��ѡ���б�Ԥѡ��ʱ������
		"""
		pass

	def onItemSelectChanged_( self, index ) :
		"""
		ĳ��ѡ��ȷ�ϱ�ѡ�к����
		"""
		pass


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getComboBox( self ) :
		return self.__pyCombo()

	def _getComboList( self ) :
		return self.__pyCombo().pyComboList_

	# -------------------------------------------------
	def _getReadOnly( self ) :
		return False

	def _setReadOnly( self, readOnly ) :
		pass


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyComboList_ = property( _getComboList )
	pyComboBox = property( _getComboBox )
	readOnly = property( _getReadOnly, _setReadOnly )					# �����������룬�������д������


	# ----------------------------------------------------------------
	# add as abstract method
	# ----------------------------------------------------------------
	__abstract_methods.add( getViewItem_ )
	__abstract_methods.add( setViewItem_ )
	__abstract_methods.add( onItemSelectChanged_ )


# --------------------------------------------------------------------
# implement text box in combox
# --------------------------------------------------------------------
class InputBox( IBox, TextBox ) :
	__cc_exposed_attrs = set( [
		"text",											# ��ǰ�ı�
		"maxLength",									# �������������ַ���
		] )												# ��Ҫ������Ϊ ComboBox ���Ե�����

	def __init__( self, box, pyCombo ) :
		self.pyLBView_ = StaticText( box.lbView )						# �ı���ǩ
		self.pyLBView_.h_dockStyle = self.pyLBView_.h_anchor			# ���ﱾ��������ô���õģ�ֻ������ h_dockStyle �� h_anchor ��ֵ
																		# �ڿ��󡢾��С������ϸպö�Ϊ��"LEFT"��"CENTER"��"RIGHT"
		TextBox.__init__( self, box )
		IBox.__init__( self, pyCombo )
		self.pyLBView_.text = ""
		middle = self.pyLBView_.middle
		self.pyLText_.middle = middle
		self.pyRText_.middle = middle									# ���� textbox �е��ı���ǩ�� ComboBox �ı��ĸ߶�һ��
		self.foreColor = self.pyLBView_.color							# ���� textbox ��ǰ��ɫ�� ComboBox �ı�����ɫһ��
		self.font = self.pyLBView_.font									# ���� textbox �������� ComboBox �ı�������һ��

		self.__followSelCBID = 0										# �����ı�ʱ������ѡ���б�ѡ��� callback ID

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __selectStartswithInput( self ) :
		"""
		ѡ���� box ��������ı���ͷ��ѡ��
		"""
		if self.readOnly : return								# ֻ���ڷ�ֻ��ʱ���Ż�����ı����е��ı���ѡ���ı���һ�µ�����
		if self.text == "" : return								# ���ı�������
		pyComboList_ = self.pyComboList_
		text = self.text
		if text == "" :
			pyComboList_.selIndex = -1
			return
		items = []
		for index, item in enumerate( pyComboList_.items ) :	# ��ȡ�б��������� Box ���ı���ͷ��ѡ��
			if item.startswith( text  ) :
				items.append( ( index, item ) )
		if len( items ) == 0 :									# ���û���� Box ���ı���ͷ��ѡ��
			pyComboList_.selIndex = -1							# ��Ԥ��ѡ���κ�ѡ��
		else :													# ����
			items.sort( key = lambda item : item[1] )			# ѡ���б��е�һ��ѡ��
			pyComboList_.selIndex = items[0][0]


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onBeforeDropDown_( self ) :
		"""
		��ʾѡ���б�ǰ������
		"""
		self.__selectStartswithInput()

	# -------------------------------------------------
	def getExposedAttr_( self, name ) :
		"""
		ͨ����д�÷������԰� Box ������ת��Ϊ ComboBox ������
		"""
		if name in self.__cc_exposed_attrs :
			return getattr( self, name )
		return IBox.getExposedAttr_( self, name )

	def setExposedAttr_( self, name, value ) :
		"""
		ͨ����д�÷������԰� Box ������ת��Ϊ ComboBox ������
		"""
		if name in self.__cc_exposed_attrs :
			setattr( self, name, value )
		IBox.setExposedAttr_( self, name, value )

	def getViewItem_ ( self ) :
		"""
		��ȡ��ǰ Box �е����ݣ���� readOnly Ϊ True���������� selItem ��
		"""
		return self.text

	def setViewItem_( self, viewItem ) :
		"""
		���õ�ǰ Box �е����ݣ���� readOnly Ϊ True������Ӧ������һ��
		"""
		if not self.readOnly :
			self.text = viewItem
		else :
			IBox.setViewItem_( self, viewItem )

	# -------------------------------------------------
	def onTextChanged_( self ) :
		"""
		�ı��ı�ʱ�����ã����� combobox ���ı��� textbox ���ı�һ��
		"""
		TextBox.onTextChanged_( self )
		self.pyLBView_.text = TextBox._getText( self )
		if not self.pyComboBox.isDropped : return
		BigWorld.cancelCallback( self.__followSelCBID )
		self.__followSelCBID = BigWorld.callback( 0.3, self.__selectStartswithInput )

	def onItemSelectChanged_( self, index ) :
		"""
		ѡ��ı�ʱ������
		"""
		pyCombo = self.pyComboBox
		if not pyCombo.ownerDraw :
			self.text = "" if index < 0 else pyCombo.items[index]

	# -------------------------------------------------
	def onTabIn_( self ) :
		"""
		��ý���ʱ������
		"""
		TextBox.onTabIn_( self )
		self.pyLBView_.visible = False
		self.pyLText_.visible = True
		self.pyRText_.visible = True

	def onTabOut_( self ) :
		"""
		���뽹��ʱ������
		"""
		self.pyLBView_.visible = True
		self.pyLText_.visible = False
		self.pyRText_.visible = False
		TextBox.onTabOut_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyLBView_.text

	def _setText( self, text ) :
		self.pyLBView_.text = text
		TextBox._setText( self, text )

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyLBView_.font

	def _setFont( self, font ) :
		self.pyLBView_.font = font
		TextBox._setFont( self, font )

	# ---------------------------------------
	def _setForeColor( self, color ) :
		self.pyLBView_.color = color
		TextBox._setForeColor( self, color )

	# ---------------------------------------
	def _setReadOnly( self, readOnly ) :
		TextBox._setReadOnly( self, readOnly )
		if readOnly :
			self.pyLText_.visible = False
			self.pyRText_.visible = False
			self.pyLBView_.visible = True

	# -------------------------------------------------
	def _setWidth( self, width ) :
		self.pyLBView_.text = self.pyLBView_.text
		if self.pyLBView_.h_anchor == "CENTER" :
			self.pyLBView_.left += ( width - self.width ) / 2
		elif self.pyLBView_.h_anchor == "RIGHT" :
			self.pyLBView_.left += width - self.width
		TextBox._setWidth( self, width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )									# ��ȡ/�����ı�
	font = property( TextBox._getFont, _setFont )							# ��ȡ/��������
	foreColor = property( TextBox._getForeColor, _setForeColor )			# ��ȡ/����ǰ��ɫ
	readOnly = property( TextBox._getReadOnly, _setReadOnly )				# ��ȡ/�����Ƿ�ֻ��
	width = property( TextBox._getWidth, _setWidth )						# ��ȡ/���ÿ��



# --------------------------------------------------------------------
# implement item list for combobox
# --------------------------------------------------------------------
class ComboList( ODListWindow ) :
	def __init__( self, pyCombo ) :
		ODListWindow.__init__( self, pyBinder = pyCombo )
		self.addToMgr( "comboList" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __confirmSelect( self ) :
		"""
		ȷ������Ͽ�ѡ�е�ǰ�б��е�ѡ��ѡ��
		"""
		self.pyBinder.collapse( True, True )

	def __cancelSelect( self ) :
		"""
		ȡ���б��е�ǰѡ�е�ѡ��
		"""
		self.selIndex = self.pyBinder.selIndex
		self.pyBinder.collapse( False, False )

	# -------------------------------------------------
	def __onLastKeyDown( self, key, down ) :
		if ( key == KEY_LEFTMOUSE or key == KEY_RIGHTMOUSE ) and \
			not self.isMouseHit() and not self.pyBinder.isMouseHit() :
				self.pyBinder.collapse(  False, False )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onComboKeyDown_( self, key, mods ) :
		"""
		���հ�����Ϣ
		"""
		if self.visible :										# �ɼ�״̬��
			if mods != 0 : return False
			if key == KEY_UPARROW :								# ����ѡ��
				self.upSelect()
				return True
			elif key == KEY_DOWNARROW :							# ����ѡ��
				self.downSelect()
				return True
			elif key == KEY_RETURN or key == KEY_NUMPADENTER :	# ȷ������Ͽ�ѡ�е�ǰ�б��е�ѡ��ѡ��
				if self.selIndex < 0 :
					self.__cancelSelect()
				else :
					self.__confirmSelect()
				return True
			elif key == KEY_ESCAPE :							# ȡ���б��е�ǰѡ�е�ѡ��
				self.__cancelSelect()
				return True
		else :													# ���ɼ�״̬��
			if mods != 0 : return
			if key == KEY_UPARROW or key == KEY_DOWNARROW :
				self.pyBinder.dropDown()
				return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def selectItemViaKey( self, fnItemKey ) :
		"""
		ѡ���� key ���ص�ָ��ѡ����ѡ�гɹ��򷵻� True�����򷵻� False
		"""
		for index, item in enumerate( self.items ) :
			if fnItemKey( index, item ) :
				self.selIndex = index
				return True
		return False

	# -------------------------------------------------
	def show( self ) :
		self.__tmpSelIndex = self.selIndex
		ODListWindow.show( self )
		LastKeyDownEvent.attach( self.__onLastKeyDown )

	def hide( self ) :
		self.__tmpSelIndex = -1
		ODListWindow.hide( self )
		LastKeyDownEvent.detach( self.__onLastKeyDown )
