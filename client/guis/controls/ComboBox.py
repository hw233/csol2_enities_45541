# -*- coding: gb18030 -*-
#
# $Id: ComboBox.py,v 1.34 2008-08-26 02:12:45 huangyongwei Exp $

"""
implement combobox component

2006.07.20: writen by huangyongwei
2008.04.17: modified by huangyongwei: ��� ComboList
"""
"""
composing :
	GUI.Window
		downBtn( GUI.Simple or GUI.Window )
		textBox( GUI.Window )
			-- lbText ( GUI.Text )
"""

import weakref
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.FlexWindow import HVFlexWindow as FlexWindow
from Control import Control
from TextBox import TextBox
from StaticText import StaticText
from Button import Button
from ListPanel import ListPanel
from ListItem import ListItem
from ListItem import SingleColListItem


# --------------------------------------------------------------------
# implement combobox class
# --------------------------------------------------------------------
class ComboBox( Control ) :
	def __init__( self, comboBox = None ) :
		Control.__init__( self, comboBox )
		self.__initialize( comboBox )

		self.__pySelItem = None												# ��ǰѡ�е�ѡ��ʵ��

	def subclass( self, comboBox ) :
		Control.subclass( self, comboBox )
		self.__initialize( comboBox )

	def __del__( self ) :
		self.pyListPanel_.dispose()
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, comboBox ) :
		if comboBox is None : return
		self.pyBox_ = Box( self, comboBox.textBox )							# ѡ���ı���
		self.pyBox_.h_dockStyle = "HFILL"

		self.pyDownBtn_ = Button( comboBox.downBtn )						# ������ť
		self.pyDownBtn_.h_dockStyle = "RIGHT"
		self.pyDownBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyDownBtn_.onLMouseDown.bind( self.__toggleDropDown )

		self.pyListPanel_ = self.createListMenu_()							# �����б�
		self.pyListPanel_.setWidth__( self.width )
		self.pyListPanel_.visible = False

		self.canTabIn = True												# �Ƿ���Ի�ý��㣬��ý�����ζ����������
		self.readOnly = True												# ���������Ϊ True���򲻿�������
		self.autoSelect = True												# ��û��ѡ����ʱ���Ƿ��Զ�ѡ��һ��������ѡ��


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onDropDown = self.createEvent_( "onDropDown" )					# ����ʾ�����б�ʱ������
		self.__onCollapsed = self.createEvent_( "onCollapsed" )					# �������������ʱ������
		self.__onItemLClick = self.createEvent_( "onItemLClick" )				# ��ĳ��ѡ����ʱ������
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )	# �ı䵱ǰѡ��ʱ������
		self.__onTextChanged = self.createEvent_( "onItemSelectChanged" )		# �ı��ı�ʱ������

	@property
	def onDropDown( self ) :
		"""
		����ʾ�����б�ʱ������
		"""
		return self.__onDropDown

	@property
	def onCollapsed( self ) :
		"""
		�������������ʱ������
		"""
		return self.__onCollapsed

	# -------------------------------------------------
	@property
	def onItemLClick( self ) :
		"""
		��ĳ��ѡ����ʱ������
		"""
		return self.__onItemLClick

	@property
	def onItemSelectChanged( self ) :
		"""
		�ı䵱ǰѡ��ʱ������
		"""
		return self.__onItemSelectChanged

	@property
	def onTextChanged( self ) :
		"""
		������е��ı��ı�ʱ������
		"""
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __locateListMenu( self ) :
		"""
		���������б��λ��
		"""
		self.pyListPanel_.left = self.leftToScreen
		self.pyListPanel_.top = self.bottomToScreen
		if self.pyListPanel_.r_bottomToScreen < -1 :
			self.pyListPanel_.bottom = self.topToScreen + 2			# �� 2 ����Ϊ��ͼ���

	def __selectItem( self, pyItem ) :
		"""
		ѡ��һ��ѡ��
		"""
		isSameItem = self.__pySelItem == pyItem
		self.__pySelItem = pyItem
		if not isSameItem :
			self.onItemSelectChanged( pyItem )
		text = getattr( pyItem, "text", None )
		if text is not None : self.pyBox_.text = text

	# -------------------------------------------------
	def __toggleDropDown( self ) :
		"""
		����/���������б�
		"""
		if self.isDropDown :
			self.collapse()
		else :
			self.dropDown()


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# friend of box
	# -------------------------------------------------
	def onBoxLMouseDown__( self ) :
		"""
		������� box ʱ������
		"""
		if self.pyBox_.readOnly :
			self.__toggleDropDown()
		else :
			self.pyListPanel_.hide()
			self.tabStop = True


	# -------------------------------------------------
	# frient of list menut
	# -------------------------------------------------
	def onItemLClick__( self, pyItem ) :
		"""
		��ĳ��ѡ����ʱ������
		"""
		self.collapse()
		if self.__pySelItem != pyItem :
			self.__selectItem( pyItem )
		self.onItemLClick( pyItem )

	def onItemSelectChanged__( self, pyItem ) :
		"""
		��ĳ��ѡ�ѡ��ʱ��������
		"""
		if self.isDropDown :
			if not self.readOnly :
				self.tabStop = True
		else :
			self.__selectItem( pyItem )
		self.onItemSelectChanged_( pyItem )

	def onDropDown__( self ) :
		"""
		��ʾ�����б�ʱ������
		"""
		rds.uiHandlerMgr.castUI( self )
		self.onDropDown()

	def onCollapsed__( self ) :
		"""
		���������б�ʱ������
		"""
		rds.uiHandlerMgr.uncastUI( self )
		self.onCollapsed()

	# -------------------------------------------------
	# frient of combo item
	# -------------------------------------------------
	def onItemTextChanged__( self, pyItem ) :
		"""
		ĳ����ѡ����ı��ı�ʱ������
		"""
		if pyItem == self.pySelItem :
			self.pyBox_.text = pyItem.text


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def createListMenu_( self ) :
		"""
		���������б�����ͨ����д�ú��������������б�����
		"""
		return ComboList( self )

	def onItemSelectChanged_( self, pyItem ) :
		"""
		��һ��ѡ�Ԥѡ��ʱ���ú��������ã������� Item û�� text ���ԣ��������д�÷���������Ԥѡ�е�����
		"""
		if pyItem is None : return
		if hasattr( pyItem, "text" ) :
			self.pyBox_.text = pyItem.text
		else :
			WARNING_MSG( "the comboitem instance of %s is not contain 'text' property!" % pyItem.__class__ )

	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if self.isDropDown :											# �����������״̬
			if key == KEY_UPARROW :
				self.pyListPanel_.upSelect()
			elif key == KEY_DOWNARROW :
				self.pyListPanel_.downSelect()
			elif key == KEY_ESCAPE :
				self.cancelDrop()										# ���������б�ȡ��ѡ��
			elif key == KEY_RETURN or key == KEY_NUMPADENTER :
				self.collapse()											# ���������б����ѡ��
			return True
		if self.tabStop :												# ��ý��㲢��û�д�������״̬
			res = False
			if key == KEY_UPARROW or key == KEY_DOWNARROW :
				self.dropDown()
			else :
				res = self.pyBox_.onKeyDown__( key, mods )
			return Control.onKeyDown_( self, key, mods ) or res
		return Control.onKeyDown_( self, key, mods )

	def onKeyUp_( self, key, mods ) :
		if self.isDropDown : return False								# ��������ʱȡ����Ϣ�����Σ����Ҳ������¼�
		return Control.onKeyUp_( self, key, mods )

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		if self.isDropDown :
			if not self.pyListPanel_.isMouseHit() and \
				not self.pyBox_.isMouseHit() and \
				not self.pyDownBtn_.isMouseHit() :
					self.collapse()
			return False												# ��������ʱȡ����Ϣ�����Σ����Ҳ������¼�
		return Control.onLMouseDown_( self, mods )

	def onRMouseDown_( self, mods ) :
		if self.isDropDown :
			if not self.pyListPanel_.isMouseHit() and \
				not self.pyBox_.isMouseHit() and \
				not self.pyDownBtn_.isMouseHit() :
					self.collapse()
			return False												# ��������ʱȡ����Ϣ�����Σ����Ҳ������¼�
		return Control.onRMouseDown_( self, mods )

	def onLMouseUp_( self, mods ) :
		if self.isDropDown : return False								# ��������ʱȡ����Ϣ�����Σ����Ҳ������¼�
		return Control.onLMouseUp_( self, mods )

	def onRMouseUp_( self, mods ) :
		if self.isDropDown : return False								# ��������ʱȡ����Ϣ�����Σ����Ҳ������¼�
		return Control.onRMouseUp_( self, mods )

	# -------------------------------------------------
	def onLClick_( self, mods ) :
		if self.isDropDown : return False								# ��������ʱȡ����Ϣ�����Σ����Ҳ������¼�
		return Control.onLClick_( self, mods )

	# -------------------------------------------------
	def onTabIn_( self ) :
		Control.onTabIn_( self )
		if self.readOnly : return
		self.pyBox_.tabStop = True

	def onTabOut_( self ) :
		Control.onTabOut_( self )
		self.pyBox_.tabStop = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addItem( self, pyItem ) :
		"""
		���һ��ѡ��
		"""
		pySelItem = self.pyListPanel_.pySelItem
		self.pyListPanel_.addItem( pyItem )
		self.__locateListMenu()
		if pySelItem != self.pyListPanel_.pySelItem :			# ��� autoSelect Ϊ True�������ѡ��֮ǰ���û��ѡ�е�ѡ��
			self.__selectItem( self.pyListPanel_.pySelItem )	# �����ѡ���ȴ�Զ�ѡ����һ��ѡ�����Ҫ���������е��޴�������Ч��

	def addItems( self, pyItems ) :
		"""
		���һ��ѡ��
		"""
		pySelItem = self.pyListPanel_.pySelItem
		self.pyListPanel_.addItems( pyItems )
		if pySelItem != self.pyListPanel_.pySelItem :
			self.__selectItem( self.pyListPanel_.pySelItem )

	def removeItem( self, pyItem ) :
		"""
		ɾ��һ��ѡ��
		"""
		self.pyListPanel_.removeItem( pyItem )
		self.__locateListMenu()									# ��������б���������չ�ģ�����Ҫ������������λ��
		if pyItem == self.__pySelItem :
			self.__selectItem( self.pyListPanel_.pySelItem )

	def clearItems( self ) :
		"""
		�������ѡ��
		"""
		self.pyListPanel_.clearItems()
		self.__selectItem( None )
		self.pyBox_.text = ""

	# -------------------------------------------------
	def getSameTextItem( self, text ) :
		"""
		��ȡ�ı���ͬ�ĵ�һ��ѡ�û���ҵ��򷵻� None
		"""
		for pyItem in self.pyItems :
			if pyItem.text == text :
				return pyItem
		return None

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		ѡ��ǰѡ�����һ��ѡ��
		"""
		self.pyListPanel_.upSelect()

	def downSelect( self ) :
		"""
		ѡ��ǰѡ�����һ��ѡ��
		"""
		self.pyListPanel_.downSelect()

	# -------------------------------------------------
	def notifyInput( self, text ) :
		"""
		�����뷨���ã����������ı�
		"""
		self.pyBox_.notifyInput( text )

	# -------------------------------------------------
	def dropDown( self ) :
		"""
		��������ʾ��ѡ���б�
		"""
		if self.itemCount == 0 : return
		if self.isDropDown : return
		self.__locateListMenu()
		self.pyListPanel_.show()

	def collapse( self ) :
		"""
		�۵������أ��б�������ǰ�б���ѡ�е�ѡ����Ϊ ComboBox ��ѡ��ѡ��
		"""
		if not self.isDropDown : return
		self.__selectItem( self.pyListPanel_.pySelItem )
		if not self.readOnly :
			self.pyBox_.selectAll()
		self.pyListPanel_.hide()

	def cancelDrop( self ) :
		"""
		�۵������أ��б���������ǰ�б���ѡ�е�ѡ����Ϊ ComboBox ��ѡ��ѡ��
		"""
		if not self.isDropDown : return
		self.pyListPanel_.pySelItem = self.__pySelItem
		self.pyListPanel_.hide()

	def moveCursorTo( self, idx ) :
		"""
		�ƶ���굽ָ���ط�
		"""
		self.pyBox_.moveCursorTo( idx )

	def select( self, start, end ) :
		"""
		ѡ��ָ���ı�
		"""
		self.pyBox_.select( start, end )

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		��������ѡ��
		"""
		self.pyListPanel_.sort( cmp, key, reverse )


	# ----------------------------------------------------------------
	# proeprty methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyBox_.text

	def _setText( self, text ) :
		if not self.readOnly :
			self.pyBox_.text = text

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyBox_.font

	def _setFont( self, font ) :
		self.pyBox_.font = font

	def _getFontSize( self ) :
		return self.pyBox_.fontSize

	def _setFontSize( self, fontSize ) :
		self.pyBox_.fontSize = fontSize

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.pyBox_.foreColor

	def _setForeColor( self, color ) :
		self.pyBox_.foreColor = color

	# ---------------------------------------
	def _getMaxLength( self ) :
		return self.pyBox_.maxLength

	def _setMaxLength( self, length ) :
		self.pyBox_.maxLength = length

	# -------------------------------------------------
	def _getItems( self ) :
		return self.pyListPanel_.pyItems

	def _getItemCount( self ) :
		return self.pyListPanel_.itemCount

	# -------------------------------------------------
	def _getSelItem( self ) :
		if self.__pySelItem in self.pyItems :
			return self.__pySelItem
		self.__pySelItem = None
		return None

	def _setSelItem( self, pyItem ) :
		if pyItem is None and self.__pySelItem :
			self.__pySelItem.selected = False
			self.__pySelItem = None
		else :
			pyItem.selected = True

	# ---------------------------------------
	def _getSelIndex( self ) :
		if self.__pySelItem in self.pyItems :
			return self.pyItems.index( self.__pySelItem )
		return -1

	def _setSelIndex( self, index ) :
		self.pyListPanel_.selIndex = index

	# -------------------------------------------------
	def _getViewCount( self ) :
		return self.pyListPanel_.viewCount

	def _setViewCount( self, count ) :
		self.pyListPanel_.viewCount = count

	# -------------------------------------------------
	def _getAutoSelect( self ) :
		return self.pyListPanel_.autoSelect

	def _setAutoSelect( self, auto ) :
		self.pyListPanel_.autoSelect = auto

	# -------------------------------------------------
	def _getReadOnly( self ) :
		return self.pyBox_.readOnly

	def _setReadOnly( self, readOnly ) :
		self.pyBox_.readOnly = readOnly
		if readOnly and self.tabStop :
			self.tabStop = False

	# -------------------------------------------------
	def _getIsDropDown( self ) :
		if self.pyListPanel_.itemCount == 0 :
			return False
		return self.pyListPanel_.rvisible

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		self.pyListPanel_.setWidth__( width )


	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )								# ��ȡ/���õ�ǰѡ��ѡ����ı�
	font = property( _getFont, _setFont )								# ��ȡ/��������
	fontSize = property( _getFontSize, _setFontSize )							# ��ȡ/���������С
	foreColor = property( _getForeColor, _setForeColor )				# ��ȡ/����ǰ��ɫ
	maxLength = property( _getMaxLength, _setMaxLength )				# ��ȡ�����������������ı�

	pyItems = property( _getItems )										# ��ȡ����ѡ��
	itemCount = property( _getItemCount )								# ��ȡѡ���������
	pySelItem = property( _getSelItem, _setSelItem )					# ��ȡ��ǰѡ�е�ѡ��ʵ��
	selIndex = property( _getSelIndex, _setSelIndex )					# ��ȡ/���õ�ǰѡ��ѡ�����б��е�����
	viewCount = property( _getViewCount, _setViewCount )				# ��ȡ/��������ѡ��Ŀ�������
	autoSelect = property( _getAutoSelect, _setAutoSelect )				# ��ȡ/�����Ƿ����κ�ʱ���Զ�ѡ��һ��ѡ��
	readOnly = property( _getReadOnly, _setReadOnly )					# ��ȡ/�����Ƿ�ֻ�����������ֹ����룬Ĭ��Ϊ True��
	isDropDown = property( _getIsDropDown )								# ��ȡ��ǰ�Ƿ�������״̬

	width = property( Control._getWidth, _setWidth )					# ��ȡ/���ÿ��


# --------------------------------------------------------------------
# implement text box in combox
# --------------------------------------------------------------------
class Box( TextBox ) :
	def __init__( self, pyBinder, box ) :
		self.__pyText = StaticText( box.lbText )						# �ı���ǩ
		self.__pyText.h_dockStyle = self.__pyText.h_anchor				# ���ﱾ��������ô���õģ�ֻ������ h_dockStyle �� h_anchor ��ֵ
																		# �ڿ��󡢾��С������ϸպö�Ϊ��"LEFT"��"CENTER"��"RIGHT"
		TextBox.__init__( self, box, pyBinder )

		self.pyLText_.top = self.pyRText_.top = self.__pyText.top		# ���� textbox �е��ı���ǩ�� ComboBox �ı��ĸ߶�һ��
		self.foreColor = self.__pyText.color							# ���� textbox ��ǰ��ɫ�� ComboBox �ı�����ɫһ��
		self.font = self.__pyText.font									# ���� textbox �������� ComboBox �ı�������һ��

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		"""
		�����ʱ������
		"""
		self.pyBinder.onBoxLMouseDown__()
		if self.tabStop :
			TextBox.onLMouseDown_( self, mods )
		return True

	def onTextChanged_( self ) :
		"""
		�ı��ı�ʱ�����ã����� combobox ���ı��� textbox ���ı�һ��
		"""
		TextBox.onTextChanged_( self )
		self.__pyText.text = TextBox._getText( self )
		pyBinder = self.pyBinder
		if pyBinder : pyBinder.onTextChanged()


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def onKeyDown__( self, key, mods ) :
		return self.onKeyDown_( key, mods )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.__pyText.text

	def _setText( self, text ) :
		self.__pyText.text = text
		if self.pyCursor_.capped( self ) :
			TextBox._setText( self, text )

	# ---------------------------------------
	def _getFont( self ) :
		return self.__pyText.font

	def _setFont( self, font ) :
		self.__pyText.font = font
		TextBox._setFont( self, font )

	def _getFontSize( self ) :
		return self.__pyText.fontSize

	def _setFontSize( self, fontSize ) :
		self.__pyText.fontSize = fontSize
		TextBox._setFontSize( self, fontSize )

	# ---------------------------------------
	def _setForeColor( self, color ) :
		self.__pyText.color = color
		TextBox._setForeColor( self, color )

	# ---------------------------------------
	def _setReadOnly( self, readOnly ) :
		TextBox._setReadOnly( self, readOnly )
		if readOnly :
			self.pyBinder.tabStop = False
			self.pyLText_.visible = False
			self.pyRText_.visible = False

	# -------------------------------------------------
	def _getTabStop( self ) :
		return self.pyBinder.tabStop

	def _setTabStop( self, tabStop ) :
		if tabStop :
			if self.readOnly : return
			self.pyLText_.visible = self.pyRText_.visible = True
			self.__pyText.visible = False
			self.showCursor_()
		else :
			TextBox.hideCursor_( self )
			self.pyLText_.visible = self.pyRText_.visible = False
			self.__pyText.visible = True

	# -------------------------------------------------
	def _setWidth( self, width ) :
		self.__pyText.text = self.__pyText.text
		if self.__pyText.h_anchor == "CENTER" :
			self.__pyText.left += ( width - self.width ) / 2
		elif self.__pyText.h_anchor == "RIGHT" :
			self.__pyText.left += width - self.width
		TextBox._setWidth( self, width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )								# ��ȡ/�����ı�
	font = property( TextBox._getFont, _setFont )						# ��ȡ/��������
	fontSize = property( _getFontSize, _setFontSize )								# ��ȡ/���������С
	foreColor = property( TextBox._getForeColor, _setForeColor )		# ��ȡ/����ǰ��ɫ
	readOnly = property( TextBox._getReadOnly, _setReadOnly )			# ��ȡ/�����Ƿ�ֻ��

	tabStop = property( _getTabStop, _setTabStop )						# ��ȡ/�������뽹��

	width = property( TextBox._getWidth, _setWidth )					# ��ȡ/���ÿ��



# --------------------------------------------------------------------
# implement listment class in combobox
# --------------------------------------------------------------------
class ComboList( FlexWindow, Control ) :
	__cc_sbar_panel  = "guis/controls/combobox/panel/spanel.gui"		# ���������İ���
	__cc_nobar_panel = "guis/controls/combobox/panel/npanel.gui"		# �����������İ���

	def __init__( self, pyBinder, spanel = None, npanel = None ) :
		panel = hfUILoader.load( self.__cc_sbar_panel )
		FlexWindow.__init__( self, panel )
		Control.__init__( self, panel, pyBinder )
		self.moveFocus = False															# ������������϶�
		self.posZSegment = ZSegs.L2														# ���ڵڶ��� UI
		self.activable_ = False															# �����Ա�����
		self.escHide_ = True															# ������ ESC ������

		self.__pyListPanel = ListPanel( panel.clipPanel, panel.scrollBar )				# item ����
		self.__pyListPanel.selectable = True											# ����ѡ��ĳ��
		self.__pyListPanel.mouseUpSelect = True
		self.__pyListPanel.onItemLClick.bind( self.__onItemLClick )
		self.__pyListPanel.onItemSelectChanged.bind( self.__onItemSelectChanged )
		self.__pyScrollBar = self.__pyListPanel.pySBar									# ������
		self.__pyScrollBar.h_dockStyle = "RIGHT"
		self.__pyScrollBar.v_dockStyle = "VFILL"

		self.__viewCount = 6															# ����ѡ������
		self.__hideScroll()																# Ĭ�����ع�����

		self.addToMgr( "comboBoxListMenu" )


	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __rewidthItem( self, pyItem ) :
		"""
		�����б�Ŀ������ĳ��ѡ��Ŀ��
		"""
		pyItem.width = self.__pyListPanel.width

	def __rewidthItems( self ) :
		"""
		�����б�Ŀ����������ѡ��Ŀ��
		"""
		for pyItem in self.pyItems :
			self.__rewidthItem( pyItem )

	def __reheight( self ) :
		"""
		�����б����ĸ߶�
		"""
		itemCount = self.itemCount
		viewCount = self.viewCount
		if itemCount == 0 : return									# û��ѡ��
		if self.isOverView() :										# ѡ��������������ѡ������
			itemsHeight = self.pyItems[viewCount - 1].bottom		# ��߶ȼ��㵽����ѡ������Ϊֹ
			bg = hfUILoader.load( self.__cc_sbar_panel )			# ������������
		else :														# ����
			itemsHeight = self.getItem( -1 ).bottom					# ��ѡ������ʵ�ʸ߶������б�߶�
			bg = hfUILoader.load( self.__cc_nobar_panel )			# ��������������
		self.__pyListPanel.pos = s_util.getGuiPos( bg.clipPanel )
		self.__pyListPanel.height = itemsHeight
		space = bg.height - bg.clipPanel.height
		height = itemsHeight + space
		FlexWindow._setHeight( self, height )						# �������ð���ĸ߶�
		sbSpace = bg.height - bg.scrollBar.height
		self.__pyScrollBar.height = height - sbSpace				# �������ù������ĸ߶�

	# ---------------------------------------
	def __copyFrame( self, srcPanel ) :
		"""
		���ư�����ͼ
		"""
		self.pyRT_.texture = srcPanel.rt.textureName
		self.pyR_.texture = srcPanel.r.textureName
		self.pyRB_.texture = srcPanel.rb.textureName
		cpRight = s_util.getGuiRight( srcPanel.clipPanel )
		space = srcPanel.width - cpRight
		self.__pyListPanel.width = self.width - self.__pyListPanel.left - space

	def __showScroll( self ) :
		"""
		��ʾ������
		"""
		self.__pyScrollBar.visible = True
		sbarPanel = hfUILoader.load( self.__cc_sbar_panel )
		self.__copyFrame( sbarPanel )
		self.__rewidthItems()

	def __hideScroll( self ) :
		"""
		���ع�����
		"""
		self.__pyScrollBar.visible = False
		nobarPanel = hfUILoader.load( self.__cc_nobar_panel )
		self.__copyFrame( nobarPanel )
		self.__rewidthItems()

	# -------------------------------------------------
	def __onItemLClick( self, pyItem ) :
		"""
		��һ��ѡ����ʱ������
		"""
		self.pyBinder.onItemLClick__( pyItem )

	def __onItemSelectChanged( self, pyItem ) :
		"""
		��һ��ѡ�ѡ��ʱ������
		"""
		self.pyBinder.onItemSelectChanged__( pyItem )


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def setWidth__( self, width ) :
		"""
		���� comboBox  ���ÿ��
		"""
		self.__pyListPanel.width += width - self.width
		FlexWindow._setWidth( self, width )
		self.__rewidthItems()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		if self.itemCount == 0 : return
		FlexWindow.show( self )
		self.pyBinder.onDropDown__()

	def hide( self ) :
		FlexWindow.hide( self )
		self.pyBinder.onCollapsed__()

	# -------------------------------------------------
	def addItem( self, pyItem ) :
		"""
		���һ��ѡ��
		"""
		assert isinstance( pyItem, ComboItem ), "item '%s' added to ComboBox must inherit from ComboItem!" % str( pyItem )
		pre = pyItem not in self.pyItems				# �ж�ѡ���Ƿ��Ѿ����б���
		pyItem.setComboBox__( self.pyBinder )			# �������� ComboBox
		self.__pyListPanel.addItem( pyItem )			# ��ӵ��б�
		lat = pyItem in self.pyItems					# �ٴ��ж�ѡ���Ƿ����б��У���Ϊ�п������ʧ�ܣ�
		if not ( pre and lat ) : return					# ������ʧ�ܣ��򷵻�

		itemCount = self.itemCount
		viewCount = self.viewCount
		if itemCount <= viewCount :						# ���ѡ��������С�ڿ���ѡ������
			self.__reheight()							# ʵʱ���ð���߶�
			self.__rewidthItem( pyItem )				# ���������ѡ��ĸ߶�
		elif itemCount == viewCount + 1 :				# ѡ�������պó�������ѡ������
			self.__showScroll()							# ����ʾ��������ע������ҲҪ���������ѡ��Ŀ�ȣ�ֻ����һ���Ѿ��� showScroll �����ˣ�
		else :											# ѡ�������������ͳ�������ѡ�������
			self.__rewidthItem( pyItem )				# ����ֻ��Ҫ������ѡ��ĸ߶�

	def addItems( self, pyItems ) :
		"""
		���һ��ѡ��
		"""
		for pyItem in pyItems :
			self.addItem( pyItem )

	def removeItem( self, pyItem ) :
		"""
		ɾ��һ��ѡ��
		"""
		if pyItem not in self.pyItems : return
		self.__pyListPanel.removeItem( pyItem )
		pyItem.setComboBox__( None )

		itemCount = self.itemCount
		viewCount = self.viewCount
		if itemCount < viewCount :						# ���ѡ������С�ڿ���ѡ������
			self.__reheight()							# �������ð���߶�
		elif itemCount == viewCount :					# ���ѡ�������պõ��ڿ�������
			self.__hideScroll()							# �����ع�����

	def clearItems( self ) :
		"""
		ɾ������ѡ��
		"""
		for pyItem in self.pyItems :
			pyItem.setComboBox__( None )
		self.__pyListPanel.clearItems()
		self.__hideScroll()
		self.hide()

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		��ȡָ����������ѡ��
		"""
		return self.__pyListPanel.getItem( index )

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		����ѡ��һ��
		"""
		self.__pyListPanel.upSelect()

	def downSelect( self ) :
		"""
		����ѡ��һ��
		"""
		self.__pyListPanel.downSelect()

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		��������ѡ��
		"""
		if cmp is None and key is None :
			self.__pyListPanel.sort( key = lambda pyItem : pyItem.text )
		else :
			self.__pyListPanel.sort( cmp, key, reverse )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItems( self ) :
		return self.__pyListPanel.pyItems

	# ---------------------------------------
	def _getItemCount( self ) :
		return self.__pyListPanel.itemCount

	# ---------------------------------------
	def _getViewCount( self ) :
		return self.__viewCount

	def _setViewCount( self, count ) :
		count = max( count, 1 )
		self.__viewCount = count

	# ---------------------------------------
	def isOverView( self ) :
		return self.itemCount > self.viewCount

	# -------------------------------------------------
	def _getSelItem( self ) :
		return self.__pyListPanel.pySelItem

	def _setSelItem( self, pyItem ) :
		self.__pyListPanel.pySelItem = pyItem

	# ---------------------------------------
	def _getSelIndex( self ) :
		return self.__pyListPanel.selIndex

	def _setSelIndex( self, index ) :
		self.__pyListPanel.selIndex = index

	# ---------------------------------------
	def _getAutoSelect( self ) :
		return self.__pyListPanel.autoSelect

	def _setAutoSelect( self, auto ) :
		self.__pyListPanel.autoSelect = auto



	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	pyItems = property( _getItems )										# ��ȡ����ѡ��
	itemCount = property( _getItemCount )								# ��ȡѡ������
	viewCount = property( _getViewCount, _setViewCount )				# ��ȡ����ѡ������
	autoSelect = property( _getAutoSelect, _setAutoSelect )				# �κ�ʱ���Ƿ��Զ�ѡ��һ��
	pySelItem = property( _getSelItem, _setSelItem )					# ��ȡ/���õ�ǰѡ�е�ѡ��
	selIndex = property( _getSelIndex, _setSelIndex )					# ��ȡ/���õ�ǰѡ�е�����

	width = property( FlexWindow._getWidth )							# ��ȡ�����б�Ŀ��
	height = property( FlexWindow._getHeight )							# ��ȡ�����б�ĸ߶�


# --------------------------------------------------------------------
# implement combo item class
# --------------------------------------------------------------------
class ComboItem( SingleColListItem ) :
	def __init__( self, text = "", item = None ) :
		SingleColListItem.__init__( self, item )
		self.__pyComboBox = None
		self.text = text

	def __del__( self ) :
		SingleColListItem.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def setComboBox__( self, pyComboBox ) :
		"""
		���������� comboBox��ֻ�� ComboList ���ã�
		"""
		if pyComboBox is None :
			self.__pyComboBox = None
		else :
			self.__pyComboBox = weakref.ref( pyComboBox )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getComboBox( self ) :
		if self.__pyComboBox is None :
			return self.__pyComboBox
		return self.__pyComboBox()

	def _setText( self, text ) :
		if text == self.text : return
		SingleColListItem._setText( self, text )
		if self.pyComboBox :
			self.pyComboBox.onItemTextChanged__( self )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyComboBox = property( _getComboBox )									# ��ȡ������ ComboBox
	text = property( SingleColListItem._getText, _setText )
