# -*- coding: gb18030 -*-
#
# $Id: ContextMenu.py,v 1.29 2008-08-30 09:04:58 huangyongwei Exp $

"""
implement contextmenu class��

2008.04.15 : writen by huangyongwei
"""

import weakref
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.PyGUI import PyGUI
from guis.common.FlexExWindow import HVFlexExWindow
from Control import Control
from StaticText import StaticText
from CheckBox import CheckBox


# --------------------------------------------------------------------
# items panel
# --------------------------------------------------------------------
class Items( HVFlexExWindow ) :
	def __init__( self, panel = None, pyParent = None, pyMenu = None ) :
		if panel is None :
			panel = hfUILoader.load( "guis_v2/controls/contextmenu/panel.gui" )
		HVFlexExWindow.__init__( self, panel )
		self.__itemWidth = 0										# ѡ����
		self.__pyMenu = None										# �����˵�
		self.__pyParentItem = None									# �����˵�ѡ��
		self.__initialize( panel, pyParent, pyMenu )
		self.__pyItems = []

	def subclass( self, panel, pyParent, pyMenu ) :
		HVFlexExWindow.subclass( self, panel )
		self.__initialize( self, panel, pyParent, pyMenu )

	def dispose( self ) :
		self.clear()
		HVFlexExWindow.dispose( self )

	def __del__( self ) :
		self.clear()
		HVFlexExWindow.__del__( self )
		if Debug.output_del_ContextMenu :
			INFO_MSG( "delete Context MenuItem:<%i>" % id( self ) )

	# ---------------------------------------
	def __initialize( self, panel, pyParent, pyMenu ) :
		if panel is None : return
		self.posZSegment = ZSegs.L2									# ����Ϊ�ڶ���
		self.movable_ = False										# �����Ա��ƶ�
		self.activable_ = False										# ���ɼ���
		self.hitable_ = True										# �����������λ��
		self.escHide_ = True										# ���԰� esc ����
		self.__pyClipPanel = PyGUI( panel.clipPanel )				# �˵������
		if pyMenu : self.__pyMenu = weakref.ref( pyMenu )			# ���������˵�
		if pyParent : self.__pyParentItem = weakref.ref( pyParent )	# ���������˵���

		self.addToMgr( "contextMenuItems" )							# ��ӵ� UI ������


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		try :
			return "MenuItems" + str( self.__pyItems )
		except :
			return "MenuItems<%s>" % id( self )

	def __str__( self ) :
		return self.__repr__()

	def __contains__( self, pyItem ) :
		return pyItem in self.__pyItems

	def __iter__( self ) :
		return self.__pyItems.__iter__()

	def __getitem__( self, index ) :
		return self.__pyItems[index]

	def __getslice__( self, start, end ) :
		return self.__pyItems.__getslice__( start, end )

	def __radd__( self, pyItems ) :
		return pyItems + self.__pyItems


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getItemMaxRealWidth( self ) :
		"""
		��ò˵�����������ʵ���
		"""
		maxWith = 0
		for pyItem in self.__pyItems :
			maxWith = max( pyItem.getRealWidth(), maxWith )
		return maxWith

	# -------------------------------------------------
	def __pasteItem( self, pyItem ) :
		"""
		ճ��һ��ѡ��
		"""
		pyPItem = self.pyParentItem
		while pyPItem is not None :						# �ж�ѡ���Ƿ����ҵĸ�ѡ�������Ӹ�ѡ�������ѭ����
			if pyPItem == pyItem :
				DEBUG_MSG( "you can't add its parent node as its child node!" )
				return False
			pyPItem = pyPItem.pyParent

		if pyItem.pySelfItems is not None :				# ����˵����Ѿ����ҵ��б��У���ɾ��֮���������
			pyItem.pySelfItems.remove( pyItem )
		self.__pyClipPanel.addPyChild( pyItem )
		return True

	def __layoutItems( self ) :
		"""
		�������в˵�λ�ã�pyStart ��ʾ���ĸ��˵��ʼ����
		"""
		top = 0
		for pyItem in self.__pyItems :
			if not pyItem.visible :
				continue
			else :
				pyItem.top = top
				top = pyItem.bottom
		if top == 0 and self.pyParentItem :						# ���û�пɼ��˵���
			self.pyParentItem.close()							# ��֪ͨ�������˵�������ȫ���Ӳ˵�
		else :													# �������µ����˵��б�߶�
			space = self.height - self.__pyClipPanel.bottom
			self.__pyClipPanel.height = top
			height = self.__pyClipPanel.bottom + space
			HVFlexExWindow._setHeight( self, height )
		self.__rewidth( self.__itemWidth )						# ���õ�ǰ�Ŀ��Ϊ�˵����������ʵ���

	def __rewidth( self, width ) :
		"""
		�������ò˵���Ŀ��
		"""
		for pyItem in self.__pyItems :
			pyItem.rewidth__( width )
		space = self.width - self.__pyClipPanel.right
		self.__pyClipPanel.width = width
		width = self.__pyClipPanel.right + space
		HVFlexExWindow._setWidth( self, width )

	# -------------------------------------------------
	def __bindAddedItem( self, pyItem ) :
		"""
		��һ����ӵĲ˵���
		"""
		pyItem.setMenu__( self.pyMenu )
		pyItem.setSelfItems__( self )
		width = pyItem.getRealWidth()
		if width > self.__itemWidth :							# �˵����Ϊ�����ѡ��Ŀ��
			self.__itemWidth = width
		pyItem.rewidth__( self.__itemWidth )					# ���������ѡ��Ŀ��
		self.__layoutItems()
		if self.pyParentItem :
			self.pyParentItem.onItemAdded__( pyItem )

	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def setMenu__( self, pyMenu ) :
		"""
		���������˵�
		"""
		if pyMenu is None :
			self.__pyMenu = None
		else :
			self.__pyMenu = weakref.ref( pyMenu )
		for pyItem in self.__pyItems :
			pyItem.setMenu__( pyMenu )

	# -------------------------------------------------
	def onItemRewidth__( self, pyItem ) :
		"""
		��ĳ���˵���Ŀ�ȸı�ʱ���ú���������
		"""
		width = pyItem.getRealWidth()
		if width > self.__pyClipPanel.width :
			self.__rewidth( width )

	# -------------------------------------------------
	def getPopUpItem__( self ) :
		"""
		��ȡ���ڵ���״̬���Ӳ˵���
		"""
		for pyItem in self.__pyItems :
			if pyItem.isPopUp :
				return pyItem
		return None

	def onItemToogleVisible__( self, pyItem ) :
		"""
		��ĳ���Ӳ˵�������/��ʾʱ������
		"""
		self.__layoutItems()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def isMouseHitSubMenu_( self ) :
		if self.isMouseHit() : return True
		for pyItem in self.__pyItems :
			if pyItem.isMouseHitSubMenu__() :
				return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def adds( self, pyItems ) :
		"""
		���һ��˵���
		@type			pyItems : list/tuple of MenuItem
		@param			pyItems : Ҫ��ӵĲ˵�ѡ���б�
		"""
		for pyItem in pyItems :
			self.add( pyItem )

	def add( self, pyItem ) :
		"""
		���һ���˵���
		@type			pyItem : MenuItem
		@param			pyItem : Ҫ��ӵĲ˵�ѡ��
		"""
		if not self.__pasteItem( pyItem ) :
			return
		self.__pyItems.append( pyItem )
		self.__bindAddedItem( pyItem )

	def insert( self, index, pyItem ) :
		"""
		����һ���˵���
		@type			index  : int
		@param			index  : �����λ��
		@type			pyItem : MenuItem
		@param			pyItem : Ҫ����Ĳ˵�ѡ��
		"""
		if index < 0 or index >= self.count :
			DEBUG_MSG( "index is out of range!" )
			return
		if not self.__pasteItem( pyItem ) :
			return
		self.__pyItems.insert( index, pyItem )
		self.__bindAddedItem( pyItem )

	def remove( self, pyItem ) :
		"""
		ɾ��һ���˵���
		@type			pyItem : MenuItem
		@param			pyItem : Ҫɾ���Ĳ˵�ѡ��
		"""
		if isDebuged :
			assert pyItem in self.__pyItems, "%s is not in self!" % pyItem
		self.__pyClipPanel.delPyChild( pyItem )
		self.__pyItems.remove( pyItem )
		pyItem.setMenu__( None )
		pyItem.setSelfItems__( None )
		self.__itemWidth = 0
		for pyItem in self.__pyItems :
			width = pyItem.getRealWidth()
			if width > self.__itemWidth :
				self.__itemWidth = width
		if self.count > 0 :
			self.__layoutItems()
		else :
			self.hide()
		if self.pyParentItem :
			self.pyParentItem.onItemRemoved__( pyItem )

	def clear( self ) :
		"""
		������в˵���
		"""
		for pyItem in self.__pyItems :
			self.__pyClipPanel.delPyChild( pyItem )
			pyItem.setMenu__( None )
			pyItem.setSelfItems__( None )
		if self.pyParentItem :
			self.pyParentItem.onItemRemoveds__( pyItem )
		self.__itemWidth = 0
		self.hide()
		self.__pyItems = []

	def reset( self ) :
		"""
		������������ѡ��״̬
		"""
		for pyItem in self.__pyItems :
			pyItem.reset()

	# -------------------------------------------------
	def show( self, pyOwner = None ) :
		self.reset()
		HVFlexExWindow.show( self, pyOwner, False )

	def hide( self ) :
		for pyItem in self.__pyItems :
			if pyItem.isPopUp :
				pyItem.close()
		HVFlexExWindow.hide( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMenu( self ) :
		if self.__pyMenu is None :
			return None
		return self.__pyMenu()

	def _getParentItem( self ) :
		if self.__pyParentItem is None :
			return None
		return self.__pyParentItem()

	# -------------------------------------------------
	def _getCount( self ) :
		return len( self.__pyItems )

	# -------------------------------------------------
	def _getFirst( self ) :
		if self.count > 0 :
			return self.__pyItems[0]
		return None

	def _getLast( self ) :
		if self.count > 0 :
			return self.__pyItems[-1]
		return None

	# -------------------------------------------------
	def _getTopEdgeHeight( self ) :
		return self.__pyClipPanel.top

	def _getBottomEdgeHeight( self ) :
		return self.height - self.__pyClipPanel.bottom


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyMenu = property( _getMenu )											# ��ȡ�����˵�
	pyParentItem = property( _getParentItem )								# ��ȡ�����˵���
	count = property( _getCount )											# ��ȡ�˵��������
	pyFirst = property( _getFirst )											# ��ȡ��һ���˵���
	pyLast = property( _getLast )											# ��ȡ�ڶ����˵���
	width = property( HVFlexExWindow._getWidth )							# ��ȡ�˵��б�Ŀ��
	height = property( HVFlexExWindow._getHeight )							# ��ȡ�˵��б�ĸ߶�

	itemWidth = property( lambda self : self.__itemWidth )					# ��ȡ�˵���Ŀ��
	topEdgeHeight = property( _getTopEdgeHeight )							# ��ȡ�����ظ߶�
	bottomEdgeHeight = property( _getBottomEdgeHeight )						# ��ȡ�ױ��ظ߶�


# --------------------------------------------------------------------
# implement context menu class
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
		-- lt : GUI.Simple
		-- t  : GUI.Simple ( tiled = True )
		-- rt : GUI.Simple
		-- l  : GUI.Simple ( tiled = True )
		-- bg : GUI.Simple ( tiled = True )
		-- r  : GUI.Simple ( tiled = True )
		-- lb : GUI.Simple
		-- b  : GUI.Simple ( tiled = True )
		-- rb : GUI.Simple

		-- clipPanel : GUI.Window
"""

class ContextMenu( Items ) :
	cg_pyMenus_ = WeakSet()					# ��¼�����в˵�ʵ��

	def __init__( self, panel = None ) :
		Items.__init__( self, panel, None, self )
		LastKeyUpEvent.attach( ContextMenu.__onLastKeyUp )		# �����ظ����ӵģ�����¼��б����Ѿ��У��򲻻��ٸ��ӣ�������ﲻ��Ҫ�ж�
																# LastKeyEvent �б����Ƿ��б�ע��Ĳ˵�����
		self.__autoPopUp = True									# �Ƿ��Զ����������Ϊ True��������Ҽ���� binders ʱ���˵����ᵯ��
		self.__pyBinders = WeakList()							# ����ui����� autoPopUp Ϊ True�����Ҽ������Щ binders ��ᵯ���˵�
																# ��� autoPopUp Ϊ False������������Щ Triggers�����ᵯ��/����˵�
		self.__vsDetectCBID = 0									# ��� binder �Ƿ�ɼ������ɼ������ز˵�
		self.__loadingHide = True								# ���봫��״̬ʱ�Ƿ�رղ˵�

		ContextMenu.cg_pyMenus_.add( self )					# ��ӵ�ȫ�ֱ�

	def __del__( self ) :
		if len( ContextMenu.cg_pyMenus_ ) == 0 :				# ������в˵�ʵ������ɾ��
			LastKeyUpEvent.detach( ContextMenu.__onLastKeyUp )	# ����� LastKeyUpEvent �¼�
		self.__unbindBindersClickEvent()						# ȡ���󶨿ؼ����¼���
		self.__pyBinders.clear()								# ȡ���԰󶨿ؼ�������
		Items.__del__( self )
		if Debug.output_del_ContextMenu :
			INFO_MSG( "delete Context Menu:<%i>" % id( self ) )


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "ContextMenu instance at %s" % hex( id( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Items.generateEvents_( self )
		self.__onBeforePopUp = self.createEvent_( "onBeforePopup" )				# ���˵�����ʱ������
		self.__onBeforeClose = self.createEvent_( "onBeforeClose" )				# ���˵��ر�ǰ������
		self.__onAfterPopUp = self.createEvent_( "onAfterPopUp" )				# ���˵������󱻴���
		self.__onAfterClose = self.createEvent_( "onAfterClose" )				# ���˵�����󱻴���
		self.__onItemClick = self.createEvent_( "onItemClick" )					# ��һ���˵�����ʱ������
		self.__onItemCheckChanged = self.createEvent_( "onItemCheckChanged" )	# ��һ���˵��ѡ��ʱ������

	@property
	def onBeforePopup( self ) :
		"""
		���˵�����ǰ��������������¼������߷��� ��1����˵�����ʧ�ܣ�
		"""
		return self.__onBeforePopUp

	@property
	def onBeforeClose( self ) :
		"""
		���˵��ر�ǰ������
		"""
		return self.__onBeforeClose

	@property
	def onAfterPopUp( self ) :
		"""
		���˵������󱻴���
		"""
		return self.__onAfterPopUp

	@property
	def onAfterClose( self ) :
		"""
		���˵�����󱻴���
		"""
		return self.__onAfterClose

	@property
	def onItemClick( self ) :
		"""
		��һ���˵�����ʱ������
		"""
		return self.__onItemClick

	@property
	def onItemCheckChanged( self ) :
		"""
		��һ���˵��ѡ��ʱ������
		"""
		return self.__onItemCheckChanged


	# ---------------------------------------------------------------
	# private
	# ---------------------------------------------------------------
	def __locateToCursor( self ) :
		"""
		�Զ����õ���λ��
		"""
		px, py = csol.pcursorPosition()
		if px + self.width <= BigWorld.screenWidth() :
			self.left = px
		else :
			self.right = px
		if py + self.height <= BigWorld.screenHeight() :
			self.top = py
		else :
			self.bottom = py

	def __detectBinderVisible( self ) :
		"""
		��� binder �Ƿ�ɼ������ɼ������ز˵�
		"""
		if not self.rvisible or len( self.__pyBinders ) == 0 :
			BigWorld.cancelCallback( self.__vsDetectCBID )
			return
		for pyBinder in self.__pyBinders :
			if pyBinder.rvisible :
				self.__vsDetectCBID = BigWorld.callback( 1.5, Functor( self.__detectBinderVisible ) )
				return
		self.hide()
		BigWorld.cancelCallback( self.__vsDetectCBID )

	def __bindBindersClick( self, pyBinder = None ) :
		"""
		ע�� binder ���������¼�, ��� pyBinder Ϊ None, ��ע�ᵱǰ���� binder
		��� autoPopUp ����ֵΪ False����Ĭ�������� binder ʱ����ʾ�˵�
		"""
		def bind( pyBinder ) :
			if hasattr( pyBinder, "onLClick" ) :
				pyBinder.onLClick.bind( self.__onBinderLClick )		# ע�⣺bind �����������汾����������ͬһ�� binder �ظ��󶨶��Ҳ��������ظ�

		if pyBinder is None :
			for pyBinder in self.__pyBinders :
				bind( pyBinder )
		else :
			bind( pyBinder )

	def __unbindBindersClickEvent( self, pyBinder = None ) :
		"""
		��ע�� binder ���������¼������ pyBinder Ϊ None����ȡ��ע�ᵱǰ���� binder
		"""
		def unbind( pyBinder ) :
			if hasattr( pyBinder, "onLClick" ) :
				pyBinder.onLClick.unbind( self.__onBinderLClick )

		if pyBinder is None :
			for pyBinder in self.__pyBinders :
				unbind( pyBinder )
		else :
			unbind( pyBinder )

	# -------------------------------------------------
	def __onBinderLClick( self, pyBinder ) :
		"""
		������������ UI ʱ������
		"""
		if self.__autoPopUp : return
		if not self.rvisible :
			self.show( pyBinder )
		else :
			self.hide()

	# ---------------------------------------
	def __isHitTrigger( self ) :
		"""
		�ж�����Ƿ�����ĳ�� trigger ��
		"""
		for pyBinder in self.__pyBinders :
			if pyBinder.isMouseHit() :
				return True
		return False

	def __onLastKeyDown( self, key, mods ) :
		"""
		����ʲô����£����¼��̼������ʱ���ᱻ����
		"""
		if self.isMouseHitMenu() :							# �������ڲ˵���
			return
		if not self.autoPopUp :								# ����˵������Ҽ�����Զ�������
			return
		if self.__isHitTrigger() and \
			key == KEY_RIGHTMOUSE :							# �������ڲ˵������ؼ��ϣ����������°�������Ҽ�
				return
		if key == KEY_LEFTMOUSE or \
			key == KEY_RIGHTMOUSE or \
			key == KEY_RETURN or \
			key == KEY_NUMPADENTER :
				self.hide()

	@staticmethod
	def __onLastKeyUp( key, mods ) :
		"""
		����ʲô����£�������̼������ʱ���ᱻ����
		"""
		if mods != 0 : return
		if key != KEY_RIGHTMOUSE : return				# �������Ĳ����Ҽ����򲻻ᵯ���˵�
		pyRoot = rds.ruisMgr.getMouseHitRoot()
		if pyRoot is None : return						# �Ҽ�û�л����κ� UI���򲻻ᵯ���˵�
		for pyMenu in ContextMenu.cg_pyMenus_ :
			for pyBinder in pyMenu.__pyBinders :
				if not pyBinder.rvisible :				# ����󶨿ؼ����ɼ�
					continue
				if pyBinder.pyTopParent != pyRoot :		# ������û���ڰ󶨿ؼ��ĸ�������
					continue
				if not pyBinder.isMouseHit() :			# ������û���ڰ󶨿ؼ���
					continue
				pyMenu.popup( pyBinder )				# �������Ҽ�����˲˵��󶨿ؼ�������ʾ�˵�
				return


	# ---------------------------------------------------------------
	# frient methods
	# ---------------------------------------------------------------
	def onItemClick__( self, pyItem ) :
		"""
		��ĳ���˵�����ʱ����
		"""
		self.onItemClick( pyItem )
		if pyItem.clickClose :
			self.hide()										# ע�ͺ����κ�ѡ����رղ˵�

	def onItemCheckChanged__( self, pyItem ) :
		"""
		��ĳ���˵��ѡ��/ȡ��ѡ��״̬ʱ������
		"""
		self.onItemCheckChanged( pyItem )


	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		��Ϸ״̬�ı�ʱ����
		"""
		if oldStatus == newStatus : return
		if newStatus == Define.GST_SPACE_LOADING :
			if self.visible and self.__loadingHide :
				self.hide()

	def isMouseHitMenu( self ) :
		"""
		�ж�����Ƿ����ڲ˵��ϣ������Ӳ˵���
		"""
		return self.isMouseHitSubMenu_()

	# -------------------------------------------------
	def addBinder( self, pyBinder ) :
		"""
		���һ���󶨿ؼ�
		"""
		if pyBinder not in self.__pyBinders :
			self.__pyBinders.append( pyBinder )
			if not self.autoPopUp :
				self.__bindBindersClick( pyBinder )

	def addBinders( self, pyBinders ) :
		"""
		���һ��󶨿ؼ�
		"""
		for pyBinder in pyBinders :
			self.addBinder( pyBinder )

	def removeBinder( self, pyBinder ) :
		"""
		ɾ���󶨿ؼ�
		"""
		if pyBinder in self.__pyBinders :
			self.__pyBinders.remove( pyBinder )
			self.__unbindBindersClickEvent( pyBinder )

	def clearBinders( self ) :
		"""
		ɾ�����а󶨿ؼ�
		"""
		for pyBinder in self.__pyBinders :
			self.__unbindBindersClickEvent( pyBinder )
		self.__pyBinders.clear()

	# -------------------------------------------------
	def popup( self, pyOwner = None ) :
		"""
		�����˵��������˵�ʱ���˵���λ�ý��������꣩
		ע�������ע�� onBeforePopup �¼������¼���ѡ���Եľ����Ƿ�Ҫ�����˵���
			onBeforePopup ���� True ����ʾ��������ʾ����˵���ע���� onBeforePopup �¼�������Ҫ��ʾ�˵������¼���һ��Ҫ���� True
			ͬʱ������� onBeforePopup �¼������ò˵���λ��
		"""
		pyItem = self.getPopUpItem__()						# ��ô��ڵ���״̬���Ӳ˵���
		if pyItem : pyItem.close()							# �������ڵ���״̬�Ĳ˵�����Ӳ˵�
		if self.onBeforePopup() >= 0 :						# �������жϵ�Ŀ���ǣ�ʹ�ò˵�����֮ǰ���û������� onBeforePopup ���޸Ĳ˵���
			if self.pyItems.count == 0 : return				# û���κβ˵��
			self.__locateToCursor()							# �Զ����ò˵���λ��Ϊ�������
			Items.show( self, pyOwner )
			self.__detectBinderVisible()					# ��� binder �Ƿ�ɼ������ɼ������ز˵�
			LastKeyDownEvent.attach( self.__onLastKeyDown )
			self.onAfterPopUp()
		elif self.rvisible :
			self.hide()

	def close( self ) :
		"""
		����˵�
		"""
		self.hide()

	# ---------------------------------------
	def show( self, pyOwner = None ) :
		"""
		��ʾ�˵�����ʾ�˵�ʱ���˵�λ��Ҫ�Լ����ã�
		ע�������ע�� onBeforePopup �¼������¼���ѡ���Եľ����Ƿ�Ҫ�����˵���
			onBeforePopup ���� True ����ʾ��������ʾ����˵���ע���� onBeforePopup �¼�������Ҫ��ʾ�˵������¼���һ��Ҫ���� True
			ͬʱ������� onBeforePopup �¼������ò˵���λ��
		"""
		pyItem = self.getPopUpItem__()						# ��ô��ڵ���״̬���Ӳ˵���
		if pyItem : pyItem.close()							# �������ڵ���״̬�Ĳ˵�����Ӳ˵�
		if self.onBeforePopup() :							# �������жϵ�Ŀ���ǣ�ʹ�ò˵�����֮ǰ���û������� onBeforePopup ���޸Ĳ˵���
			if self.pyItems.count == 0 : return				# û���κβ˵��
			Items.show( self, pyOwner )
			self.__detectBinderVisible()					# ��� binder �Ƿ�ɼ������ɼ������ز˵�
			LastKeyDownEvent.attach( self.__onLastKeyDown )
			self.onAfterPopUp()
		elif self.rvisible :
			self.hide()

	def hide( self ) :
		"""
		���ز˵�
		"""
		LastKeyDownEvent.detach( self.__onLastKeyDown )
		self.onBeforeClose()
		Items.hide( self )
		self.onAfterClose()


	# ---------------------------------------------------------------
	# property methods
	# ---------------------------------------------------------------
	def _setVisible( self, visible ) :
		raise "'visible' is a read-only property.\n'popup' and 'close' called to toggle context menu!"

	# -------------------------------------------------
	def _getItems( self ) :
		return self

	# -------------------------------------------------
	def _getAutoPopUp( self ) :
		return self.__autoPopUp

	def _setAutoPopUp( self, autoPopUp ) :
		self.__autoPopUp = autoPopUp
		if autoPopUp :
			self.__unbindBindersClickEvent()
		else :
			self.__bindBindersClick()

	# -------------------------------------------------
	def _getBinders( self ) :
		return self.__pyBinders[:]

	# -------------------------------------------------
	def _getLoadingHide( self ) :
		return self.__loadingHide

	def _setLoadingHide( self, loadingHide ) :
		self.__loadingHide = loadingHide

	# ---------------------------------------------------------------
	# properties
	# ---------------------------------------------------------------
	visible = property( Items._getVisible, _setVisible )						# ��ȡ�ɼ���
	pyItems = property( _getItems )												# ��ȡ���в˵������
	autoPopUp = property( _getAutoPopUp, _setAutoPopUp )						# ��ȡ/�����Ƿ��Զ�����
	loadingHide = property( _getLoadingHide, _setLoadingHide )					# ��ȡ/���ý��봫��״̬ʱ�Ƿ�رղ˵�

	pyBinders = property( _getBinders )											# ��ȡ�˵����а󶨣��������Ŀؼ�


# --------------------------------------------------------------------
# implement menu item
# --------------------------------------------------------------------
class MenuItem( Control ) :
	__cg_commonItem = None
	__cg_checkableItem = None
	__cg_splitter = None

	def __init__( self, style = MIStyle.COMMON, item = None ) :
		"""
		@type					style : MACRO DEFINATION
		@param					style : �˵���ʽ���� uidefine.py �ж���( ��� item ���� None�����ֵ��Ч )
		@type					item  : engine ui
		@param					item  : ���� ui
		"""
		if MenuItem.__cg_commonItem is None :
			MenuItem.__cg_commonItem = GUI.load( "guis_v2/controls/contextmenu/commonitem.gui" )
			MenuItem.__cg_checkableItem = GUI.load( "guis_v2/controls/contextmenu/checkitem.gui" )
			MenuItem.__cg_splitter = GUI.load( "guis_v2/controls/contextmenu/splitter.gui" )

		if item is None :												# ���û�д���� UI�������Ĭ�õ� UI
			if style == MIStyle.COMMON :
				item = util.copyGuiTree( MenuItem.__cg_commonItem )
			if style == MIStyle.CHECKABLE :
				item = util.copyGuiTree( MenuItem.__cg_checkableItem )
			if style == MIStyle.SPLITTER :
				item = util.copyGuiTree( MenuItem.__cg_splitter )
			uiFixer.firstLoadFix( item )
		Control.__init__( self, item )
		self.__pySubItems = None
		self.pyText_ = None											# �ı���ǩ�����û�У����ʾ�Ƿָ�����
		self.pyCheckBox_ = None										# ��ѡ��
		self.pyArrow_ = None										# �Ӳ˵���ͷ
		self.state_ = UIState.COMMON								# �˵�״̬
		self.__style = style										# �˵���ʽ
		self.__clickClose = True									# ����˵�����Ƿ�ر������˵�(����û�Ӳ˵���Ĳ˵�����Ч)
		self.__initialize( item, style )

		self.__pyMenu = None										# �����Ĳ˵�
		self.__pySelfItems = None									# �����˵��б�ѡ�����

	def dispose( self ) :
		if self.pySelfItems :
			self.pySelfItems.remove( self )
		if self.__pySubItems :
			self.__pySubItems.dispose()
		Control.dispose( self )

	def __del__( self ) :
		del self.__pyMenu
		if self.__pySubItems :
			self.__pySubItems.dispose()
		Control.__del__( self )
		if Debug.output_del_ContextMenu :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, item, style ) :
		if hasattr( item, "lbText" ) :									# ����б�ǩ
			self.pyText_ = StaticText( item.lbText )
			self.focus = True
			self.crossFocus = True
			self.__pySubItems = Items( pyParent = self, pyMenu = None ) # �Ӳ˵������
		if hasattr( item, "arrow" ) :									# ������Ӳ˵���ͷ
			self.pyArrow_ = PyGUI( item.arrow )
			self.pyArrow_.h_dockStyle = "RIGHT"
			self.pyArrow_.visible = False
		if hasattr( item, "checkBox" ) :								# ����� check ��ť
			self.pyCheckBox_ = CheckBox( item.checkBox )
			self.pyCheckBox_.focus = False
			self.pyCheckBox_.h_dockStyle = "RIGHT"
			self.pyCheckBox_.checked = False
			self.pyCheckBox_.onCheckChanged.bind( self.onCheckChanged_ )
			self.__clickClose = False									# ����˵����ǿ�ѡ�в˵������˵����ر������˵�

		self.foreColors_ = {}											# ����״̬�µ�ǰ��ɫ
		self.foreColors_[UIState.COMMON] = 255, 255, 255, 255
		self.foreColors_[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.foreColors_[UIState.DISABLE] = 128, 128, 128, 255
		self.backColors_ = {}											# ����״̬�µı���ɫ
		self.backColors_[UIState.COMMON] = 255, 255, 255, 0
		self.backColors_[UIState.HIGHLIGHT] = 10, 36, 106, 255
		self.backColors_[UIState.DISABLE] = 255, 255, 255, 0


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setSubItemsPosition( self ) :
		"""
		�����Ӳ˵����λ��
		"""
		pySubItems = self.__pySubItems
		if pySubItems is None : return
		pySelfItems = self.pySelfItems								# ���ڲ˵�����
		if pySelfItems is None : return
		right = pySelfItems.right + pySubItems.width
		if right <= BigWorld.screenWidth() :						# ������ұ��г����ᳬ����Ļ�����
			pySubItems.left = pySelfItems.right - 2					# ����ұ��г�
		else :														# ����
			pySubItems.right = pySelfItems.left + 2					# ������г�

		top = self.topToScreen - pySubItems.topEdgeHeight
		if top + pySubItems.height <= BigWorld.screenHeight() :		# ��������г����ᳬ����Ļ�����߶�
			pySubItems.top = top									# �������г�
		else :														# ���������г�
			pySubItems.bottom = self.bottomToScreen + pySubItems.bottomEdgeHeight

	def __getCheckBoxWidth( self ) :
		"""
		��ȡ CheckBox �Ŀ��
		"""
		if self.pyCheckBox_ :
			return self.pyCheckBox_.width
		return 0

	def __getArrowWidth( self ) :
		"""
		��ȡ�Ӳ˵����ͷ�Ĵ�С
		"""
		if self.pyArrow_ and self.pySubItems.count :
			return self.pyArrow_.width
		return 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		������ʱ������
		"""
		Control.onMouseEnter_( self )
		self.setState( UIState.HIGHLIGHT )
		self.popup()

	def onMouseLeave_( self ) :
		"""
		����뿪ʱ������
		"""
		Control.onMouseLeave_( self )
		if not self.isPopUp :
			self.setState( UIState.COMMON )
		else :
			px, py = csol.pcursorPosition()
			if self.__pySubItems.left + 2 >= self.rightToScreen : 		# �Ӳ˵���ʾ���ұ�
				if px < self.rightToScreen :							# ��겢�ǻ����Ӳ˵�
					self.close()										# �������Ӳ˵�
			elif self.__pySubItems.right - 2 <= self.leftToScreen :		# �Ӳ˵���ʾ�����
				if px > self.leftToScreen :								# ��겢�ǻ����Ӳ˵�
					self.close()										# �������Ӳ˵�

	# ---------------------------------------
	def onLClick_( self, mods ) :
		if self.checkable and self.clickCheck :
			self.checked = not self.checked
		Control.onLClick_( self, mods )
		if self.pyMenu is not None :
			self.pyMenu.onItemClick__( self )
			if self.pySubItems.count == 0 :
				self.setState( UIState.COMMON )

	def onCheckChanged_( self, checked ) :
		if self.pyMenu is not None :
			self.pyMenu.onItemCheckChanged__( self )

	# ---------------------------------------
	def onEnable_( self ) :
		"""
		����Ч��Ϊ��Ч״̬ʱ������
		"""
		Control.onEnable_( self )
		if self.__style != MIStyle.SPLITTER :		# �ָ�����ʽ����Ӧ enable ���Եĸ���
			self.setState( UIState.COMMON )
		if self.pyArrow_ :
			self.pyArrow_.materialFX = "BLEND"

	def onDisable_( self ) :
		"""
		��Ϊ��Ч״̬ʱ������
		"""
		Control.onDisable_( self )
		if self.__style != MIStyle.SPLITTER :		# �ָ�����ʽ����Ӧ enable ���Եĸ���
			self.setState( UIState.DISABLE )
			if self.isPopUp :						# ����Ӳ˵����ڵ���״̬
				self.pySubItems.hide()				# �������Ӳ˵�
		if self.pyArrow_ :
			self.pyArrow_.materialFX = "COLOUR_EFF"


	# ----------------------------------------------------------------
	# firend mehods
	# ----------------------------------------------------------------
	def setMenu__( self, pyMenu ) :
		"""
		���������˵�
		"""
		if pyMenu is None :
			self.__pyMenu = None
		else :
			self.__pyMenu = weakref.ref( pyMenu )
		if self.__pySubItems is not None :
			self.__pySubItems.setMenu__( pyMenu )

	def setSelfItems__( self, pyItems ) :
		"""
		���������ĸ��˵���
		"""
		if pyItems is None :
			self.__pySelfItems = None
		else :
			self.__pySelfItems = weakref.ref( pyItems )
		if self.pySubItems :
			self.pySubItems.hide()

	# -------------------------------------------------
	def onItemAdded__( self, pyItem ) :
		"""
		�������һ���Ӳ˵���󣬸ú���������
		"""
		if self.pyArrow_ is not None :
			self.pyArrow_.visible = True

	def onItemRemoved__( self, pyItem ) :
		"""
		��ĳ���Ӳ˵��ɾ��ʱ���ú���������
		"""
		if self.pySubItems.count == 0 :
			if self.pyArrow_ is not None :
				self.pyArrow_.visible = False
			self.close()

	def onItemRemoveds__( self, pyItem ) :
		"""
		��ĳ���Ӳ˵������ѡ��ʱ������
		"""
		if self.pyArrow_ is not None :
			self.pyArrow_.visible = False
		self.close()

	# ---------------------------------------
	def isMouseHitSubMenu__( self ) :
		"""
		�ж�����Ƿ����� item ���� item ��
		"""
		if self.isMouseHit() :
			return True
		if self.__pySubItems is None :
			return False
		return self.__pySubItems.isMouseHitSubMenu_()

	def rewidth__( self, width ) :
		"""
		�������ò˵���Ŀ��
		"""
		Control._setWidth( self, width )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		����״̬�����
		@type			state : MACRO DEFINATION
		@param			state : UIState.COMMON / UIState.HIGHLIGHT / UIState.DISABLE
		"""
		if self.__style == MIStyle.SPLITTER :
			return
		self.color = self.backColors_[state]
		if self.pyText_ is not None :
			self.pyText_.color = self.foreColors_[state]
		self.state_ = state

	# -------------------------------------------------
	def resetMemuPanel( self, panel ) :
		"""
		���������Ӳ˵��������ʽ
		@type				panel : engine ui
		@param				panel : �Ӳ˵������ ui
		"""
		self.__pySubItems.subclass( panel, self, self.pyMenu )

	def getRealWidth( self ) :
		"""
		��ȡ�˵������ʵ���
		"""
		if self.pyText_ is None : return 0
		stuffWidth = 0														# checkBox �Ŀ�ȣ����ͷ�Ŀ�ȣ�ȡ����ߣ�
		if self.pySelfItems is not None :
			for pyItem in self.pySelfItems :
				stuffWidth = max( stuffWidth, pyItem.__getCheckBoxWidth() )
				stuffWidth = max( stuffWidth, pyItem.__getArrowWidth() )
		else :
			stuffWidth = max( stuffWidth, self.__getCheckBoxWidth() )
			stuffWidth = max( stuffWidth, self.__getArrowWidth() )
		return self.pyText_.right + self.pyText_.left + stuffWidth

	# -------------------------------------------------
	def popup( self ) :
		"""
		�����Ӳ˵�
		"""
		pyItem = self.pySelfItems.getPopUpItem__()
		if pyItem is not None :
			pyItem.close()													# ����ͬ���˵�����Ӳ˵�
		if self.pySubItems and self.pySubItems.count :
			self.__setSubItemsPosition()
			self.pySubItems.show()

	def close( self ) :
		"""
		�����Ӳ˵�
		"""
		if self.isPopUp :
			self.pySubItems.hide()
		self.setState( UIState.COMMON )

	def reset( self ) :
		"""
		�ָ�ԭʼ״̬
		"""
		if self.state_ != UIState.DISABLE :
			self.setState( UIState.COMMON )
		if self.state_ == UIState.HIGHLIGHT :
			pySubItems = self.pySubItems
			if pySubItems :
				pySubItems.reset()


	# ----------------------------------------------------------------
	# property mehtods
	# ----------------------------------------------------------------
	def _getMenu( self ) :
		if self.__pyMenu is None :
			return None
		return self.__pyMenu()

	def _getSelfItems( self ) :
		if self.__pySelfItems is None :
			return None
		return self.__pySelfItems()

	# ---------------------------------------
	def _getSubItems( self ) :
		return self.__pySubItems

	def _getVisibleSubItems( self ) :
		return [pyItem for pyItem in self.__pySubItems if pyItem.visible]

	# -------------------------------------------------
	def _getText( self ) :
		if self.pyText_ is None :
			return ""
		return self.pyText_.text

	def _setText( self, text ) :
		if self.pyText_ is None :
			return
		self.pyText_.text = text
		self.width = self.getRealWidth()

	def _getFont( self ) :
		if self.pyText_ is None :
			return ""
		return self.pyText_.font

	def _setFont( self, font ) :
		if self.pyText_ is None :
			return
		self.pyText_.font = font
		self.width = self.getRealWidth()

	# ---------------------------------------
	def _getCharSpace( self ) :
		if self.pyText_ is None :
			return 0
		return self.pyText_.charSpace

	def _setCharSpace( self, space ) :
		if self.pyText_ is None :
			return
		self.pyText_._setCharSpace( space )

	def _getLimning( self ) :
		if self.pyText_ is None :
			return Font.LIMN_NONE
		return self.pyText_.limning

	def _setLimning( self, style ) :
		if self.pyText_ is None :
			return
		self.pyText_.limning = style

	def _getLimnColor( self ) :
		if self.pyText_ is None :
			return Font.defLimnColor
		return self.pyText_.limnColor

	def _setLimnColor( self, color ) :
		if self.pyText_ is None :
			return
		self.pyText_._setLimnColor( color )

	# -------------------------------------------------
	def _getCheckable( self ) :
		return self.pyCheckBox_ is not None

	def _getChecked( self ) :
		assert self.pyCheckBox_, "it is not a checkable item!"
		return self.pyCheckBox_.checked

	def _setChecked( self, checked ) :
		assert self.pyCheckBox_, "it is not a checkable item!"
		if self.pyCheckBox_ is None : return
		self.pyCheckBox_.checked = checked

	# ---------------------------------------
	def _getClickCheck( self ) :
		if self.pyCheckBox_ :
			return self.pyCheckBox_.clickCheck
		return False

	def _setClickCheck( self, clickCheck ) :
		if self.pyCheckBox_ :
			self.pyCheckBox_.clickCheck = clickCheck

	# ---------------------------------------
	def _getClickClose( self ) :
		if self.pySubItems.count :
			return False
		return self.__clickClose

	def _setClickClose( self, clickClose ) :
		self.__clickClose = clickClose

	# ---------------------------------------
	def _getIsPopUp( self ) :
		if self.__pySubItems is None :
			return False
		return self.__pySubItems.rvisible

	# -------------------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.foreColors_[UIState.COMMON] = color
		self.pyText_.color = color

	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color

	def _getDisableForeColor( self ) :
		return self.foreColors_[UIState.DISABLE]

	def _setDisableForeColor( self, color ) :
		self.foreColors_[UIState.DISABLE] = color

	# -------------------------------------------------
	def _getCommonBackColor( self ) :
		return self.backColors_[UIState.COMMON]

	def _setCommonBackColor( self, color ) :
		self.backColors_[UIState.COMMON] = color

	def _getHighlightBackColor( self ) :
		return self.backColors_[UIState.HIGHLIGHT]

	def _setHighlightBackColor( self, color ) :
		self.backColors_[UIState.HIGHLIGHT] = color

	def _getDisableBackColor( self ) :
		return self.backColors_[UIState.DISABLE]

	def _setDisableBackColor( self, color ) :
		self.backColors_[UIState.DISABLE] = color

	# -------------------------------------------------
	def _setVisible( self, visible ) :
		Control._setVisible( self, visible )
		if self.pySelfItems :
			self.pySelfItems.onItemToogleVisible__( self )			# ֪ͨ�����˵��б��������в˵���
		if not visible :											# �����Ϊ���ɼ�
			self.setState( UIState.COMMON )
			if self.__pySubItems :
				self.__pySubItems.hide()							# �����������Ӳ˵�

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		if self.pySelfItems is not None :
			self.pySelfItems.onItemRewidth__( self )				# ֪ͨѡ���б�������������ѡ��Ŀ��


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyMenu = property( _getMenu )														# ��ȡ�����˵�
	pySelfItems = property( _getSelfItems )												# ��ȡ�����ĸ��˵���
	pySubItems = property( _getSubItems )												# ��ȡ�Ӳ˵������
	pyVSSubItems = property( _getVisibleSubItems )										# ��ȡ���пɼ��˵���
	itemStyle = property( lambda self : self.__style )									# �˵�����ʽ
	text = property( _getText, _setText )												# ��ȡ/���ò˵��ı�
	font = property( _getFont, _setFont )												# ��ȡ/��������
	charSpace = property( _getCharSpace, _setCharSpace )								# ��ȡ/�����ּ��
	limning = property( _getLimning, _setLimning )										# ��ȡ/���������ʽ
	limnColor = property( _getLimnColor, _setLimnColor )								# ��ȡ/���������ɫ

	checkable = property( _getCheckable )												# ��øò˵����Ƿ�ɱ�ѡ��
	checked = property( _getChecked, _setChecked )										# ��ȡ/���ò˵���ѡ��״̬
	clickCheck = property( _getClickCheck, _setClickCheck )								# ��ȡ/���õ��ʱ���Ƿ�ѡ��
	clickClose = property( _getClickClose, _setClickClose )								# ��ȡ/���ò˵����������Ƿ�ر������˵�
	isPopUp = property( _getIsPopUp )													# ����Ӳ˵����Ƿ��ڵ���״̬

	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )				# ��ȡ/������ͨ״̬�µ�ǰ��ɫ
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor)		# ��ȡ/���ø���״̬�µ�ǰ��ɫ
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )			# ��ȡ/������Ч״̬�µ�ǰ��ɫ

	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )				# ��ȡ/������ͨ״̬�µı���ɫ
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor ) 	# ��ȡ/���ø���״̬�µı���ɫ
	disableBackColor = property( _getDisableBackColor, _setDisableBackColor )			# ��ȡ/������Ч״̬�µı���ɫ

	visible = property( Control._getVisible, _setVisible )								# ��ȡ/���ò˵���Ŀɼ���

	width = property( Control._getWidth, _setWidth )									# ��ȡ/���ò˵���Ŀ��


# --------------------------------------------------------------------
# implement default menuitem class
# --------------------------------------------------------------------
class DefMenuItem( MenuItem ) :
	"""
	Ĭ����ʽ�Ĳ˵���
	"""
	def __init__( self, text = "", style = MIStyle.COMMON ) :
		MenuItem.__init__( self, style )
		self.text = text
