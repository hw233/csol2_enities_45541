# -*- coding: gb18030 -*-
#
# $Id: ListPanel.py,v 1.36 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement pages panel calss
2009/04/25 : writen by huangyongwei
"""

"""
composing :
	WindowsGUIComponent							# ѡ�����
	control bar : GUI.Window					# ���ư���
		-- btnDec    : GUI.Window/GUI.Simple	# ���ط�ҳ��ť
		-- btnInc    : GUI.Window/GUI.Simple	# ��ǰ��ҳ��ť
		-- stPgIndex : GUI.Text					# ҳ���ǩ
"""

from guis import *
from Control import Control
from Button import Button
from StaticText import StaticText


class ODPagesPanel( Control ) :
	def __init__( self, panel, ctrlBar, pyBinder = None ) :
		Control.__init__( self, panel, pyBinder )
		self.__items = []										# ѡ���б�
		self.__pyViewItems = []									# ����ѡ���б�
		self.__viewRows = 1										# ����ѡ������
		self.__viewCols = 1										# ����ѡ������
		self.__pgIndex = 0										# ��ǰҳ��
		self.__isRedraw = True									# ��Ҫ�ػ�ʱ���Ƿ������ػ�

		self.__selectable = False								# ѡ���Ƿ���Ա�ѡ��
		self.__selIndex = -1									# ��ǰѡ�е�ѡ������
		self.__nOrder = False									# �Ƿ���á�N����˳������ѡ��
		self.__rMouseSelect = False

		self.__initialize( panel, ctrlBar )

	def __del__( self ) :
		if Debug.output_del_ODPagesPanel :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		Control.generateEvents_( self )
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# ������ѡ�����
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# ����뿪ѡ�����
		self.__onItemLMouseDown = self.createEvent_( "onItemLMouseDown" )				# �����ѡ���ϰ������ʱ������
		self.__onItemLMouseUp = self.createEvent_( "onItemLMouseUp" )					# �����ѡ���ϰ����Ҽ�ʱ������
		self.__onItemRMouseDown = self.createEvent_( "onItemRMouseDown" )				# �����ѡ���ϰ������ʱ������
		self.__onItemRMouseUp = self.createEvent_( "onItemRMouseUp" )					# �����ѡ���ϰ����Ҽ�ʱ������
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# �����ѡ���ϵ�����ʱ������
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# �����ѡ���ϵ���Ҽ�ʱ������
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# ����ʼ��һ������ѡ��ʱ������
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# �ػ�ѡ��֪ͨ
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# ��ѡ�ѡ��ʱ����
		self.__onItemLDBClick = self.createEvent_( "onItemLDBClick" )				# ��ѡ��˫��ʱ����
		

	@property
	def onItemMouseEnter( self ) :
		return self.__onItemMouseEnter

	@property
	def onItemMouseLeave( self ) :
		return self.__onItemMouseLeave

	@property
	def onItemLMouseDown( self ) :
		return self.__onItemLMouseDown

	@property
	def onItemLMouseUp( self ) :
		return self.__onItemLMouseUp

	@property
	def onItemRMouseDown( self ) :
		return self.__onItemRMouseDown

	@property
	def onItemRMouseUp( self ) :
		return self.__onItemRMouseUp

	@property
	def onItemLClick( self ) :
		return self.__onItemLClick

	@property
	def onItemRClick( self ) :
		return self.__onItemRClick

	@property
	def onViewItemInitialized( self ) :
		return self.__onViewItemInitialized

	@property
	def onDrawItem( self ) :
		return self.__onDrawItem

	@property
	def onItemSelectChanged( self ) :
		return self.__onItemSelectChanged
		
	@property
	def onItemLDBClick( self ):
		return self.__onItemLDBClick

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel, ctrlBar ) :
		self.pyBtnDec = Button( ctrlBar.btnDec )						# ��ǰ��ҳ��ť
		self.pyBtnDec.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnDec.onLClick.bind( self.onBtnDecClick_ )

		self.pyBtnInc = Button( ctrlBar.btnInc )						# ����ҳ��ť
		self.pyBtnInc.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnInc.onLClick.bind( self.onBtnIncClick_ )

		self.pySTIndex_ = StaticText( ctrlBar.stPgIndex )				# ��ʾ�����ı�ǩ

		self.viewSize = ( 1, 1 )										# ��ʼ��Ϊһ��һ��
		self.__resetPageIndex( 0 )

	# -------------------------------------------------
	def __resetPageIndex( self, index ) :
		"""
		����ҳ����
		"""
		self.__pgIndex = index
		self.pySTIndex_.text = "%d/%d"%( index + 1, self.maxPageIndex + 1 )
		if index == 0 :
			self.pyBtnDec.enable = False
		else :
			self.pyBtnDec.enable = True
		if index == self.maxPageIndex :
			self.pyBtnInc.enable = False
		else :
			self.pyBtnInc.enable = True

	# ---------------------------------------
	def __redrawItems( self, first ) :
		"""
		�ػ���ָ��������ʼ��ѡ�first ΪҪ�ػ��ĵ�һ��ѡ������
		"""
		start = self.__pgIndex * self.viewCount							# ��һ������ѡ���Ӧ��ѡ������
		end = start + self.viewCount									# ���һ������ѡ���Ӧ��ѡ������
		for idx in xrange( first, end ) :
			pyViewItem = self.__pyViewItems[idx - start]
			pyViewItem.rebind_( idx )
			self.onDrawItem_( pyViewItem )

	def __locateViewItem( self, pyViewItem, index ) :
		"""
		���ÿ���ѡ���λ��
		"""
		viewRows, viewCols = self.__viewRows, self.__viewCols
		itemWidth, itemHeight = pyViewItem.size
		if self.__nOrder :
			left = itemWidth * ( index / viewRows )
			top = itemHeight * ( index % viewRows )
		else :
			left = itemWidth * ( index % viewCols )
			top = itemHeight * ( index / viewCols )
		pyViewItem.pos = left, top

	def __relocateAllViewItems( self ) :
		"""
		������������ѡ��λ��
		"""
		for idx, pyViewItem in enumerate( self.__pyViewItems ) :
			self.__locateViewItem( pyViewItem, idx )

	def __resizeAllViewItems( self ) :
		"""
		�ػ�����ѡ��
		"""
		viewRows, viewCols = self.__viewRows, self.__viewCols
		itemWidth = self.width / viewCols								# ѡ����
		itemHeight = self.height / viewRows								# ѡ��߶�
		for idx, pyViewItem in enumerate( self.__pyViewItems ) :
			pyViewItem.size = itemWidth, itemHeight
			self.__locateViewItem( pyViewItem, idx )
			self.onDrawItem_( pyViewItem )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onBtnDecClick_( self ) :
		"""
		��ǰ��ҳ��ť�����ʱ����
		"""
		self.pageIndex -= 1

	def onBtnIncClick_( self ) :
		"""
		���ҳ��ť�����ʱ����
		"""
		self.pageIndex += 1

	# -------------------------------------------------
	def onItemMouseEnter_( self, pyViewItem ) :
		"""
		��������ѡ��ʱ������
		"""
		self.onDrawItem_( pyViewItem )
		self.onItemMouseEnter( pyViewItem )

	def onItemMouseLeave_( self, pyViewItem ) :
		"""
		������뿪ѡ��ʱ������
		"""
		self.onDrawItem_( pyViewItem )
		self.onItemMouseLeave( pyViewItem )

	# ---------------------------------------
	def onItemLMouseDown_( self, pyViewItem, mods ) :
		"""
		�������ѡ���ϰ���ʱ������
		"""
		if self.__selectable :
			index = pyViewItem.itemIndex
			if index < self.itemCount :
				self.selIndex = index
		self.onItemLMouseDown( pyViewItem )

	def onItemLMouseUp_( self, pyViewItem, mods ) :
		"""
		�������ѡ��������ʱ������
		"""
		self.onItemLMouseUp( pyViewItem )

	def onItemRMouseDown_( self, pyViewItem, mods ) :
		"""
		�������ѡ���ϰ���ʱ������
		"""
		self.onItemRMouseDown( pyViewItem )

	def onItemRMouseUp_( self, pyViewItem, mods ) :
		"""
		�������ѡ��������ʱ������
		"""
		self.onItemRMouseUp( pyViewItem )

	# ---------------------------------------
	def onItemLClick_( self, pyViewItem, mods ) :
		"""
		�������ѡ����������ʱ������
		"""
		self.onItemLClick( pyViewItem )

	def onItemRClick_( self, pyViewItem, mods ) :
		"""
		������Ҽ���ѡ���ϵ��ʱ������
		"""
		if self.__selectable and self.__rMouseSelect :		#�Ҽ����ʱѡ�У���ODListPanel��ͬ�����ﲻ�ְ�������
			self.selIndex = pyViewItem.itemIndex
		self.onItemRClick( pyViewItem )
	
	def onItemLDBClick_( self, pyViewItem, mods ):
		"""
		������˫������
		"""
		self.onItemLDBClick( pyViewItem )

	# ---------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		��һ������ѡ���ʼ�����ʱ������
		"""
		self.onViewItemInitialized( pyViewItem )

	def onDrawItem_( self, pyViewItem ) :
		"""
		����ѡ����Ҫ�ػ�ʱ������
		"""
		if not self.__isRedraw : return
		onDrawItem = self.onDrawItem
		if self.onViewItemInitialized.count() :
			self.onDrawItem( pyViewItem )

	def onItemSelectChanged_( self, index ) :
		"""
		ĳ��ѡ�ѡ��ʱ����
		"""
		start = self.__pgIndex * self.viewCount							# ��һ������ѡ���Ӧ��ѡ������
		end = start + self.viewCount									# ���һ������ѡ���Ӧ��ѡ������
		if start <= index < end :
			self.onDrawItem( self.__pyViewItems[index - start] )
		self.onItemSelectChanged( index )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEventBinded( self, eventName, event ) :
		"""
		���¼���ʱ������
		"""
		if eventName == "onViewItemInitialized" :
			for pyViewItem in self.__pyViewItems :
				self.onViewItemInitialized_( pyViewItem )
		elif eventName == "onDrawItem" :
			for pyViewItem in self.__pyViewItems :
				self.onDrawItem_( pyViewItem )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def abandonRedraw( self ) :
		"""
		ʹѡ����ʱ�����ػ��������� insistRedraw ���׳��֣�ֻ�ʺϵ��̣߳�
		"""
		self.__isRedraw = False

	def insistRedraw( self ) :
		"""
		�ظ�ѡ���ػ��������� abandonRedraw ���׳��֣��� abandonRedraw ֮����ã�
		"""
		self.__isRedraw = True

	# -------------------------------------------------
	def addItem( self, item ) :
		"""
		���һ��ѡ��
		"""
		assert item is not None, "item must not be None type!"
		index = self.itemCount											# �����ѡ�������
		viewCount = self.viewCount										# ����ѡ������
		firstViewIndex = self.__pgIndex * viewCount						# ��һ������ѡ���Ӧ��ѡ������
		lastViewIndex = firstViewIndex + viewCount - 1					# ���һ������ѡ���Ӧ��ѡ������
		self.__items.append( item )
		if firstViewIndex <= index <= lastViewIndex :					# �������ӵ�ѡ�����
			pyViewItem = self.__pyViewItems[index - firstViewIndex]		# ��ȡ�����ѡ���Ӧ�Ŀ���ѡ��
			pyViewItem.rebind_( index )									# ���øÿ���ѡ��ָ������ӵ�ѡ��
			self.onDrawItem_( pyViewItem )								# �ػ������ѡ��
		self.__resetPageIndex( self.__pgIndex )
		
	# -------------------------------------------------
	def insterItem( self, index, item ) :
		"""
		���һ��ѡ������һ��
		"""
		assert item is not None, "item must not be None type!"
		viewCount = self.viewCount										# ����ѡ������
		firstViewIndex = self.__pgIndex * viewCount						# ��һ������ѡ���Ӧ��ѡ������
		lastViewIndex = firstViewIndex + viewCount - 1					# ���һ������ѡ���Ӧ��ѡ������
		self.__items.insert( index, item )
		for i,v in enumerate( self.__pyViewItems ):
			v.rebind_( firstViewIndex + i )
			self.onDrawItem_( v ) 
		self.__resetPageIndex( self.__pgIndex )
#		self.__resizeAllViewItems()

	def removeItem( self, item ) :
		"""
		ɾ��һ��ѡ��
		"""
		if item not in self.__items :
			raise ValueError( "item %s is not exist!" % str( item ) )
		self.removeItemOfIndex( self.__items.index( item ) )

	def removeItemOfIndex( self, index ) :
		"""
		ɾ��ָ������ѡ��
		"""
		if index < 0 or index >= self.itemCount :
			raise IndexError( "list index out of range!" )
		self.__items.pop( index )
		maxPgIndex = max( 0, ( self.itemCount - 1 ) / self.viewCount )	# ɾ��һ��ѡ�������ҳ����

		oldSelIndex = self.__selIndex
		itemCount = self.itemCount										# ʣ��ѡ������
		if index < self.__selIndex :									# ���ɾ����ѡ������С�ڵ�ǰѡ�е�ѡ������
			self.__selIndex -= 1										# ��ѡ��������һ( ��ԭ��ѡ��ѡ����ǰ����һ��λ�� )
		elif index == self.__selIndex :									# ���ɾ�����ǵ�ǰѡ��ѡ��
			if index == itemCount :										# ���������һ��ѡ��
				self.__selIndex -= 1									# ��ѡ��ѡ����ǰ�ƶ�һ��λ��

		if self.__pgIndex > maxPgIndex :								# ���ɾ��һ��ѡ��󣬷�ҳ��Ҫ������
			self.pageIndex = maxPgIndex 								# �򣬽���ǰѡ��ҳ��Ϊ���ҳ( ���÷�ҳʱ��ȫ������ѡ���Ѿ��õ��ػ� )
		else :
			self.__redrawItems( index )									# �ػ���ɾ��ѡ����������ѡ��

		if index == oldSelIndex :										# ���ɾ����ѡ���ǵ�ǰѡ��ѡ��
			self.onItemSelectChanged_( self.__selIndex )				# �򣬴���ѡ��ı��¼�
		self.__resetPageIndex( self.__pgIndex )

	def addItems( self, items ) :
		"""
		���һ��ѡ��
		"""
		for item in items :
			self.addItem( item )

	def clearItems( self ) :
		"""
		�������ѡ��
		"""
		self.__items = []
		for pyViewItem in self.__pyViewItems :
			pyViewItem.rebind_( -1 )
			self.onDrawItem_( pyViewItem )

		if self.__selIndex >= 0 :
			self.__selIndex = -1
			self.onItemSelectChanged_( -1 )
		self.__resetPageIndex( 0 )

	def updateItem( self, index, item ) :
		"""
		����ָ��ѡ��
		"""
		assert item is not None, "item must not be None type!"
		if index < 0 or index >= self.itemCount :
			raise IndexError( "list index out of range!" )
		self.__items[index] = item
		first, last = self.viewScope
		if first <= index <= last :
			pyViewItem = self.__pyViewItems[index - first]		# Ҫ���µ�ѡ������Ӧ�Ŀ���ѡ��
			self.onDrawItem_( pyViewItem )
			
	def queryItem( self, item ):
		"""
		��ѯѡ�����ڵڼ�ҳ�ڼ��� 
		"""
		pageIndex = -1
		itemIndex = -1
		totalIndex = -1
		
		for index,xitem in enumerate( self.items ):
			if item == xitem:
				totalIndex  = index
		if totalIndex >= 0:
			pageIndex = totalIndex / len( self.pyViewItems )
			itemIndex = totalIndex % len( self.pyViewItems ) 
		return ( pageIndex, itemIndex )

	# -------------------------------------------------
	def pageUp( self, count = 1 ) :
		"""
		��ǰ��ָ����ҳ��
		"""
		self.pageIndex -= count

	def pageDown( self, count = 1 ) :
		"""
		���·�ָ����ҳ��
		"""
		self.pageIndex += count

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		��������ѡ��( �����ԭ��ѡ��ѡ���ȡ��ѡ��״̬ )
		"""
		self.__items.sort( cmp, key, reverse )
		self.__resetPageIndex( 0 )
		self.__redrawItems( 0 )

	def separateSort( self, cmp = None, key = None, reverse = False ) :
		"""
		�ֿ�ÿҳ���԰�ָ����������( �����ԭ��ѡ��ѡ���ȡ��ѡ��״̬ )
		"""
		if not len( self.__items ) :
			return
		pgCount = self.maxPageIndex + 1
		viewCount = self.viewCount
		newItems = []
		for pgIdx in xrange( pgCount ) :
			start = pgIdx * viewCount
			end = start + viewCount
			items = self.__items[start:end]
			items.sort( cmp, key, reverse )
			newItems += items
		self.__items = newItems
		self.__selIndex = -1
		self.__redrawItems( self.viewScope[0] )

	# -------------------------------------------------
	def resetState( self ) :
		"""
		�ָ�Ĭ��״̬( ���������ڹر�ʱ��Ӧ�õ��ø÷��� )
		"""
		for pyViewItem in self.__pyViewItems :
			pyViewItem.resetState()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setNOrder( self, nOrder ) :
		if self.__nOrder == nOrder :
			return
		self.__nOrder = nOrder
		self.__relocateAllViewItems()

	# ---------------------------------------
	def _getViewSize( self ) :
		return self.__viewRows, self.__viewCols

	def _setViewSize( self, size ) :
		self.__viewRows = viewRows = max( 1, size[0] )					# ��������
		self.__viewCols = viewCols = max( 1, size[1] )					# ��������
		itemWidth = self.width / viewCols								# ѡ����
		itemHeight = self.height / viewRows								# ѡ��߶�

		oldCount = len( self.__pyViewItems )							# ԭ���Ŀ���ѡ������
		newCount = self.__viewRows * self.__viewCols					# �µĿ���ѡ������
		if oldCount > newCount :										# ���ӿ���ѡ������������
			self.__pyViewItems = self.__pyViewItems[:newCount]			# �򣬺��Զ����

		self.__resetPageIndex( 0 )										# �޸�Ϊ��ʾ��һҳ
		for idx in xrange( newCount ) :
			if idx < oldCount :
				pyViewItem = self.__pyViewItems[idx]
				pyViewItem.size = itemWidth, itemHeight
				self.__locateViewItem( pyViewItem, idx )
			else :														# ����ѡ�����
				pyViewItem = ViewItem( self )
				self.addPyChild( pyViewItem )
				self.__pyViewItems.append( pyViewItem )
				pyViewItem.size = itemWidth, itemHeight
				self.__locateViewItem( pyViewItem, idx )
				self.onViewItemInitialized_( pyViewItem )
			self.onDrawItem_( pyViewItem )

	# -------------------------------------------------
	def _getPageIndex( self ) :
		return self.__pgIndex

	def _setPageIndex( self, index ) :
		viewCount = self.viewCount
		maxIndex = ( self.itemCount - 1 ) / viewCount
		oldIndex = self.__pgIndex
		index = max( 0, min( index, maxIndex ) )
		self.__resetPageIndex( index )
		if oldIndex != index :
			self.__redrawItems( index * viewCount )

	def _getMaxPageIndex( self ) :
		return max( 0, self.itemCount - 1 ) / self.viewCount

	# -------------------------------------------------
	def _getViewScope( self ) :
		itemCount = self.itemCount
		if itemCount == 0 :
			return ( -1, -1 )
		viewCount = self.viewCount
		first = self.__pgIndex * viewCount					# ��һ������ѡ��Ķ�Ӧ����
		last = first + viewCount - 1						# ���һ������ѡ���Ӧ������
		last = min( last, self.itemCount - 1 )				# ���һ����Ч����ѡ���Ӧ������
		return first, last

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, selectable ) :
		if self.__selectable == selectable :
			return
		self.__selectable = selectable
		if selectable : return
		selIndex = self.__selIndex
		self.__selIndex = -1										# ����Ϊûѡ��ѡ��
		first, last = self.viewScope								# ����ѡ���������Χ
		if first <= selIndex <= last :								# ���֮ǰ��ѡ��ѡ��Ϊ����ѡ��
			pyViewItem = self.__pyViewItems[selIndex - first]		# �ҳ���ѡ��
			self.onDrawItem_( pyViewItem )							# ���ػ�
		if selIndex > 0 :											# ֮ǰ��ѡ��ѡ��
			self.onItemSelectChanged_( -1 )							# ����ѡ��ѡ��ı��¼�

	def _getSelIndex( self ) :
		return self.__selIndex

	def _setSelIndex( self, index ) :
		if not self.__selectable : return							# ����ѡ��ѡ��
		if index >= self.itemCount :
			raise IndexError( "error index!" )
		oldSelIndex = self.__selIndex								# �ɵ�ѡ��ѡ��
		if index == oldSelIndex : return							# ָ��ѡ���Ѿ�����ѡ��״̬
		self.__selIndex = index
		first, last = self.viewScope								# ����ѡ���������Χ
		if first <= oldSelIndex <= last :							# �ɵ�ѡ��ѡ���Ƿ����
			pyViewItem = self.__pyViewItems[oldSelIndex - first]	# ��ѡ��ѡ���Ӧ�Ŀ���ѡ��
			self.onDrawItem_( pyViewItem )
		if first <= index <= last :									# �µ�ѡ��ѡ���Ƿ����
			pyViewItem = self.__pyViewItems[index - first]			# ��ѡ���Ӧ�Ŀ���ѡ��
			self.onDrawItem_( pyViewItem )
		self.onItemSelectChanged_( index )							# ����ѡ��ѡ���¼�

	def _getSelItem( self ) :
		if self.__selIndex >= 0 :
			return self.__items[self.__selIndex]
		return None

	def _setSelItem( self, item ) :
		if not self.__selectable : return
		self._setSelIndex( self.__items.index( item ) )

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		self.__resizeAllViewItems()

	def _setHeight( self, height ) :
		Controls._setHeight( self, height )
		self.__resizeAllViewItems()
		
	# ---------------------------------------
	def _getRMouseSelect( self ) :
		return self.__rMouseSelect

	def _setRMouseSelect( self, rMouseSelect ) :
		self.__rMouseSelect = rMouseSelect


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyViewItems = property( lambda self : self.__pyViewItems[:] )					# list of ViewItem : ��ȡ���п���ѡ��
	nOrder = property( lambda self : self.__nOrder, _setNOrder )					# bool: �Ƿ��ԡ�N����˳������ѡ��
	viewSize = property( _getViewSize, _setViewSize )								# tuple: ���ӣ���,�У���
	viewCount = property( lambda self : self.__viewRows * self.__viewCols )			# int: ����ѡ������== viewSize[0] * viewSize[1]��
	items = property( lambda self : self.__items[:] )								# list: ����ѡ��
	itemCount = property( lambda self : len( self.__items ) )						# int: ѡ������
	pageIndex = property( _getPageIndex, _setPageIndex )							# int: ��ȡ/����ҳ����
	maxPageIndex = property( _getMaxPageIndex )										# int: ��ȡ���ҳ��
	viewScope = property( _getViewScope )											# tuple: ����ѡ��������Χ:( ��һ������ѡ���Ӧ�����������һ����Чѡ���Ӧ��ѡ������)

	selectable = property( _getSelectable, _setSelectable )							# bool: ѡ���Ƿ�ɱ�ѡ��
	selIndex = property( _getSelIndex, _setSelIndex )								# int: ��ǰѡ�е�ѡ������
	selItem = property( _getSelItem, _setSelItem )									# all types: ��ǰѡ�е�ѡ�ע�⣺����ж����ͬѡ���ѡ�е���˳���һ����

	width = property( Control._getWidth, _setWidth )								# float: ��ȡ/���ð�����
	height = property( Control._getHeight, _setHeight )								# float: ��ȡ/���ð���߶�
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )					# bool: ��ȡ/��������Ҽ����ѡ��ʱ���Ƿ�ѡ��ѡ��

# --------------------------------------------------------------------
# implement view item class for panel
# --------------------------------------------------------------------
class ViewItem( Control ) :
	def __init__( self, pyPanel ) :
		item = GUI.load( "guis/controls/odpagespanel/viewitem.gui" )				# ֻ��һ�� UI����˲���Ҫ firstLoadFix
		Control.__init__( self, item, pyPanel )
		self.__itemIndex = -1
		self.__highlight = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def rebind_( self, index ) :
		"""
		���°�һ���б�ѡ��
		"""
		self.__itemIndex = index

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		self.__highlight = True
		self.pyBinder.onItemMouseEnter_( self )
		return True

	def onMouseLeave_( self ) :
		self.__highlight = False
		self.pyBinder.onItemMouseLeave_( self )
		return True

	# ---------------------------------------
	def onLMouseDown_( self, mods ) :
		self.pyBinder.onItemLMouseDown_( self, mods )
		return True

	def onLMouseUp_( self, mods ) :
		self.pyBinder.onItemLMouseUp_( self, mods )
		return True

	def onRMouseDown_( self, mods ) :
		self.pyBinder.onItemRMouseDown_( self, mods )
		return True

	def onRMouseUp_( self, mods ) :
		self.pyBinder.onItemRMouseUp_( self, mods )
		return True

	# ---------------------------------------
	def onLClick_( self, mods ) :
		self.pyBinder.onItemLClick_( self, mods )
		return True

	def onRClick_( self, mods ) :
		self.pyBinder.onItemRClick_( self, mods )
		return True
	
	def onLDBClick_( self, mods ):
		self.pyBinder.onItemLDBClick_( self, mods)
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetState( self ) :
		"""
		�ָ�Ĭ��״̬
		"""
		if self.__highlight :
			self.__highlight = False
			self.pyBinder.onDrawItem_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPageItem( self ) :
		if self.__itemIndex < 0 : return None
		items = self.pyBinder.items
		if self.__itemIndex < len( items ) :
			return items[self.__itemIndex]
		return None

	# ---------------------------------------
	def _getSelected( self ) :
		return self.__itemIndex != -1 and \
		self.__itemIndex == self.pyBinder.selIndex


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemIndex = property( lambda self : self.__itemIndex )				# ��Ӧ��ѡ������
	pageItem = property( _getPageItem )									# ��Ӧ��ѡ��
	selected = property( _getSelected )									# ��ȡ��ѡ���Ƿ��Ǳ�ѡ��ѡ��
	highlight = property( lambda self : self.__highlight )				# ��ȡ��ѡ���Ƿ��ڸ���״̬
