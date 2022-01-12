# -*- coding: gb18030 -*-
#
# $Id: ListPanel.py,v 1.36 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement list items panel calss
2009/01/20 : writen by huangyongwei
"""

"""
composing :
	WindowsGUIComponent
	scroll bar
"""

import math
import weakref
import Font
from guis import *
from guis.UIFixer import hfUILoader
from guis.controls.Control import Control
from guis.controls.ClipPanel import VClipPanel
from guis.controls.ScrollBar import VScrollBar
from guis.controls.StaticText import StaticText
from guis.tooluis.fulltext.FullText import FullText

class ODListPanel( VClipPanel ) :
	def __init__( self, panel, scrollBar, pyBinder = None ) :
		VClipPanel.__init__( self, panel, pyBinder )
		self.pySBar = VScrollBar( scrollBar )
		self.pySBar.scrollScale = 1
		self.pySBar.onScroll.bind( self.onScroll_ )

		self.__items = []						# ѡ���б�
		self.__pyViewItems = []					# ����ѡ��
		self.__itemHeight = 18.0				# ѡ��߶�
		self.__ownerDraw = False				# �Ƿ����û��ػ�
		self.__font = Font.defFont				# ѡ��Ĭ������

		self.__selectable = True				# ѡ���Ƿ�ɱ�ѡ��
		self.__selIndex = None					# ��ǰѡ��ѡ�������
		self.__autoSelect = True				# �Ƿ���Ҫ�Զ�ѡ��Ϊ True ʱ�����ɾ����ĳ��ѡ��ѡ�����Զ�ѡ���������ѡ�
		self.__mouseUpSelect = False			# �������ʱѡ��ѡ��
		self.__rMouseSelect = False				# �Ƿ���������Ҽ�ѡ��ѡ����������һ����
		self.__perScrollCount = 1				# �����ֹ���һ��ʱ��ʵ�ʹ�����ѡ������
		
		self.__sbarState = ScrollBarST.AUTO								# Ĭ���Զ���ʾ������
		self.__isRedraw = True					# �Ƿ��ʵʱ�ػ�

		self.__initialize()

	def __del__( self ) :
		VClipPanel.__del__( self )
		if Debug.output_del_ODListPanel :
			INFO_MSG( str( self ) )

	def __initialize( self ) :
		self.mouseScrollFocus = True
		self.__itemForeColors = {}										# ѡ��Ĭ�ϵ�ǰ��ɫ
		self.__itemForeColors[UIState.COMMON] = 255, 255, 255, 255
		self.__itemForeColors[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.__itemForeColors[UIState.SELECTED] = 10, 255, 10, 255
		self.__itemForeColors[UIState.DISABLE] = 128, 128, 128, 255

		self.__itemBackColors = {}										# ѡ��Ĭ�ϵı���ɫ
		self.__itemBackColors[UIState.COMMON] = 255, 255, 255, 0
		self.__itemBackColors[UIState.HIGHLIGHT] = 10, 36, 106, 255
		self.__itemBackColors[UIState.SELECTED] = 34, 61, 69, 255
		self.__itemBackColors[UIState.DISABLE] = 255, 255, 255, 0

		self.__updateScrollBar()										# ���¹��������ܱ�������


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Control.generateEvents_( self )
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# ������ĳѡ��ʱ������
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# �Ҽ����ĳѡ��ʱ������
		self.__onItemLDBClick = self.createEvent_( "onItemLDBClick" )					# ������˫��ʱ������
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# ����ѡ���ʼ��ʱ������
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# ѡ����Ҫ�ػ�ʱ������
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# ѡ����Ҫ�ػ�ʱ������
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# ������ѡ���Ǳ�����
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# ���뿪ѡ���Ǳ�����

	@property
	def onItemLClick( self ) :									# ������ĳѡ��ʱ������
		return self.__onItemLClick

	@property
	def onItemRClick( self ) :									# �Ҽ����ĳѡ��ʱ������
		return self.__onItemRClick

	@property
	def onItemLDBClick( self ) :								# ������˫��ʱ������
		return self.__onItemLDBClick

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
	def onItemMouseEnter( self ) :								# ������ѡ��ʱ��
		return self.__onItemMouseEnter

	@property
	def onItemMouseLeave( self ) :								# ����뿪ѡ��ʱ��
		return self.__onItemMouseLeave


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addViewItem( self, index ) :
		"""
		����һ������ѡ��
		"""
		totalCount = int( math.ceil( self.height / self.__itemHeight ) )	# �������ܹ����������ѡ����
		currCount = self.viewCount											# ��ǰ�Ŀ���ѡ������
		if currCount >= totalCount : return									# �����ǰ����ѡ�������Ѿ��ﵽ����������
		pyViewItem = self.getViewItem_()
		self.addPyChild( pyViewItem )
		pyViewItem.width = self.width
		pyViewItem.height = self.__itemHeight
		pyViewItem.top = currCount * self.__itemHeight
		self.__pyViewItems.append( pyViewItem )
		pyViewItem.rebind_( index )
		self.onViewItemInitialized_( pyViewItem )
		self.onDrawItem_( pyViewItem )

	# -------------------------------------------------
	def __getHideHieight( self ) :
		"""
		��ȡ�����������ݵĸ߶�
		"""
		totleHeight = self.__itemHeight * self.itemCount
		return totleHeight - self.height

	def __getViewItem( self, index ) :
		"""
		��ȡָ��������Ӧ�Ŀ���ѡ��
		"""
		if self.viewCount :
			firstViewIdx = self.__pyViewItems[0].itemIndex
			lastViewIdx = self.__pyViewItems[-1].itemIndex
			if firstViewIdx <= index <= lastViewIdx :
				rindex = index - firstViewIdx
				return self.__pyViewItems[rindex]
		return None

	# -------------------------------------------------
	def __calcGap( self ) :
		"""
		�������߶Ȳ���ǡ�õ������п���ѡ��߶�ʱ
		��Ҫͨ������� scroll ����������߳���ȱ��
		"""
		itemCount = self.itemCount
		if itemCount == 0 :
			self.maxScroll = 0
		else :
			pyLastViewItem = self.__pyViewItems[-1]
			gap = pyLastViewItem.bottom - self.height
			self.maxScroll = max( gap, 0 )

	def __updateScrollBar( self ) :
		"""
		���¹�����
		"""
		viewHeight = self.height
		if viewHeight <= 0 : return
		totleHeight = self.itemCount * self.__itemHeight
		self.pySBar.scrollScale = totleHeight / viewHeight
		if totleHeight > viewHeight :
			hideHeight = totleHeight - viewHeight
			self.pySBar.perScroll = self.__itemHeight / hideHeight
		if self.__sbarState == ScrollBarST.AUTO:
			self.pySBar.visible = totleHeight - viewHeight - self.pySBar.perScroll / 10.0 > 0
		self.__calcGap()

	def __scrollTo( self, index ) :
		"""
		������ָ�������������ʵ���Ϲ�����������Ҫ�������򷵻� False
		"""
		viewCount = self.viewCount
		if not viewCount : return False

		hideHeight = self.__getHideHieight()						# ���ɼ���ѡ���ܸ߶�
		if hideHeight <= 0 :										# ȫ��ѡ��ɼ�
			self.scroll = 0
			return False

		scrolled = True
		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		if index < firstViewIdx :									# ��� ָ��Ҫ��������ѡ�� �����ڰ���ǰ��
			count = max( 0, index )
			hideTop = count * self.__itemHeight						# �ϲ��ֲ��ɼ�ѡ��ĸ߶�
			self.pySBar.value = hideTop / hideHeight				# ��ָ������ѡ����Ϊ��һ������ѡ��
		elif index > lastViewIdx :									# ��� ָ��Ҫ��������ѡ�� �����ڰ������
			count = firstViewIdx + ( index - lastViewIdx )
			hideTop = count * self.__itemHeight						# �ϲ��ֲ��ɼ�ѡ��ĸ߶�
			self.pySBar.value = hideTop / hideHeight				# ��ָ������ѡ����Ϊ��һ������ѡ��
		else :
			scrolled = False

		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		if index == firstViewIdx :									# ָ������ѡ���ǵ�һ��ѡ��
			self.scroll = 0.0										# ��������棬��ѡ��ѡ����Ϊ��һ������ѡ�ȫ���ɼ�
		elif index == lastViewIdx :									# ָ������ѡ�������һ��ѡ��
			self.scroll = self.maxScroll							# ��������棬��ѡ��ѡ����Ϊ���һ������ѡ�ȫ���ɼ�
		return scrolled

	# -------------------------------------------------
	def __redrawAllViewItems( self, firstViewIdx ) :
		"""
		�ػ�����ѡ�firstViewIdx �ǵ�һ������ѡ���Ӧ��ѡ������
		"""
		for pyViewItem in self.__pyViewItems :
			pyViewItem.rebind_( firstViewIdx )
			self.onDrawItem_( pyViewItem )
			firstViewIdx += 1

	def __selectItem( self, index ) :
		"""
		ѡ��ָ������ѡ�ע�⣺���ᴥ��ѡ��ѡ���¼��������ѡ��ɹ����򷵻� True�����򷵻� False
		"""
		oldSelIndex = self.__selIndex								# ��¼�¾ɵ�ѡ������
		self.__selIndex = index
		if index < 0 :												# ���������
			pyOldSelViewItem = self.__getViewItem( oldSelIndex )	# ��ȡ����ǰѡ�е�ѡ��
			if pyOldSelViewItem :
				self.onDrawItem_( pyOldSelViewItem )				# ��֪ͨ�ػ��ɵ�ѡ��ѡ��
		if not self.__scrollTo( index ) :							# ��������ѡ�е�ѡ�( �������������Ҫ�ػ� )
			pyNewSelViewItem = self.__getViewItem( index )
			if pyNewSelViewItem :
				self.onDrawItem_( pyNewSelViewItem )				# ֪ͨ�ػ���ѡ�е�ѡ��

			pyOldSelViewItem = self.__getViewItem( oldSelIndex )	# ��ȡ֮ǰѡ�е�ѡ������Ӧ�Ŀ���ѡ��
			if pyOldSelViewItem :									# ������ɼ�
				self.onDrawItem_( pyOldSelViewItem )				# ��֪ͨ�ػ��ɵ�ѡ��ѡ��

	def __autoSelectItem( self ) :
		"""
		�Զ�ѡ��һ��ѡ��
		"""
		if not self.__autoSelect :
			self.__selIndex = -1
		elif self.itemCount == 0 :
			self.__selIndex = -1
		elif self.__selIndex < 0 :
			self.__selIndex = 0
		elif self.__selIndex >= self.itemCount :
			self.__selIndex -= 1


	# ----------------------------------------------------------------
	# friend methods of ViewItem
	# ----------------------------------------------------------------
	def onViewItemLMouseDown_( self, pyViewItem, mods ) :
		"""
		��������ĳ��ѡ���ϰ���ʱ������
		"""
		self.tabStop = True
		if self.__selectable and not self.__mouseUpSelect :
			self.selIndex = pyViewItem.itemIndex
		return Control.onLMouseDown_( self, mods )

	def onViewItemLMouseUp_( self, pyViewItem, mods ) :
		"""
		��������ĳѡ��������ʱ������
		"""
		if self.__selectable and self.__mouseUpSelect :
			self.selIndex = pyViewItem.itemIndex
		return Control.onLMouseUp_( self, mods )

	def onViewItemLClick_( self, pyViewItem, mods ) :
		"""
		������������ѡ��ʱ������
		"""
		self.onItemLClick( pyViewItem.itemIndex )
		return Control.onLClick_( self, mods )

	def onViewItemRMouseDown_( self, pyViewItem, mods ) :
		"""
		������Ҽ����ڿ���ѡ���ϰ���ʱ������
		"""
		self.tabStop = True
		if self.__selectable and self.__rMouseSelect and \
			not self.__mouseUpSelect :
				self.selIndex = pyViewItem.itemIndex		# ��ѡ�������е�ѡ��
		return Control.onRMouseDown_( self, mods )

	def onViewItemRMouseUp_( self, pyViewItem, mods ) :
		"""
		������Ҽ��ڿ���ѡ��������ʱ������ʱ
		"""
		if self.__selectable and self.__mouseUpSelect and \
			self.__rMouseSelect :							# ��������Զ�ѡ�У��������Ҽ�����
				self.selIndex = pyViewItem.itemIndex		# ��ѡ�������е�ѡ��
		return Control.onRMouseUp_( self, mods )

	def onViewItemRClick_( self, pyViewItem, mods ) :
		"""
		������ڿ���ѡ�����һ�ʱ������
		"""
		self.onItemRClick( pyViewItem.itemIndex )
		return Control.onRClick_( self, mods )

	def onViewItemLDBClick_( self, pyViewItem, mods ) :
		"""
		������ڿ���ѡ����˫��ʱ������
		"""
		self.onItemLDBClick( pyViewItem.itemIndex )
		return Control.onLDBClick_( self, mods )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getViewItem_( self ) :
		"""
		��ȡһ�� ViewItem
		����ͨ����д�÷���ʵ��Ӧ��һ���Զ���� ViewItem�������Զ��� ViewItem ����̳��ڱ�ģ��� ViewItem
		"""
		return ViewItem( self )

	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if self.tabStop :
			if key == KEY_UPARROW and mods == 0 :
				self.upSelect()
			elif key == KEY_DOWNARROW and mods == 0 :
				self.downSelect()
		return Control.onKeyDown_( self, key, mods )

	# ---------------------------------------
	def onLMouseDown_( self, mods ) :
		return False

	def onLMouseUp_( self, mods ) :
		return False

	def onRMouseDown_( self, mods ) :
		return False

	def onRMouseUp_( self, mods ) :
		return False

	# ---------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		�������ֹ���ʱ������
		"""
		if dz > 0 :
			self.pySBar.decScroll( self.__perScrollCount )
		else :
			self.pySBar.incScroll( self.__perScrollCount )
		return True

	# -------------------------------------------------
	def onScroll_( self, value ) :
		"""
		����������ʱ������
		"""
		hideHeight = self.__getHideHieight()						# ���ز������ݵ��ܸ߶�
		hideTop = hideHeight * value								# ���չ���ֵ�����������ϰ벿���������ݵĸ߶�
		firstViewIdx = int( round( hideTop / self.__itemHeight ) )	# ��һ������ѡ����ѡ���б��е�����
		maxFirstViewCount = self.itemCount - self.viewCount
		firstViewIdx = min( firstViewIdx,  maxFirstViewCount )
		self.__redrawAllViewItems( firstViewIdx )					# ֪ͨ�ػ����п���ѡ��
		if hideHeight <= 0.0 :										# ���������ʾ������ѡ��
			self.scroll = 0
		else :
			perScroll = 1.0 / hideHeight
			if value < perScroll / 2 :								# �Ѿ�����������ǰ��
				self.scroll = 0
			elif value > 1 - perScroll / 2 :						# �Ѿ��������������
				self.scroll = self.maxScroll

	# -------------------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		��һ������ѡ���ʼ��ʱ������
		"""
		if self.__ownerDraw :
			self.onViewItemInitialized( pyViewItem )
		else :
			pyViewItem.addDefaultText_()

	def onDrawItem_( self, pyViewItem  ) :
		"""
		����ѡ����Ҫ�ػ�ʱ������
		"""
		if not self.__isRedraw : return								# ��ʱ�����ػ�
		if self.__ownerDraw : 										# �������Ϊ�Ի�
			if self.onViewItemInitialized.count() :					# �Ƿ���˿���ѡ���ʼ���¼���û����֪ͨ�ػ���
				self.onDrawItem( pyViewItem )						# �����ػ��¼�
			else :
				ERROR_MSG( "if 'ownerDraw' is True, 'onViewItemInitialized' must be bound!" )
		else :
			pyViewItem.updateDefaultText_()

	def onItemSelectChanged_( self, index ) :
		"""
		��ǰѡ��ѡ��ı�ʱ������
		"""
		self.onItemSelectChanged( index )

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
		assert item is not None, "item must not be None type"
		index = self.itemCount
		self.__items.append( item )
		if self.__autoSelect and self.__selIndex < 0 :
			self.__selIndex = 0
		self.__addViewItem( index )
		self.__updateScrollBar()

	def removeItem( self, item ) :
		"""
		ɾ��һ��ѡ��
		"""
		if item not in self.__items :
			raise ValueError( "item %s is not exist!" % str( item ) )
		index = self.__items.index( item )
		self.removeItemOfIndex( index )

	def removeItemOfIndex( self, index ) :
		"""
		ɾ��ָ������ѡ��
		"""
		itemCount = self.itemCount
		if index < 0 or index >= itemCount :
			raise IndexError( "index %i out of range!" % index )
		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		viewCount = self.viewCount
		redrawStart = 0												# ����ѡ���У���Ҫ�ػ���ѡ�����ʼ����
		dec = False													# �ػ�����ѡ��ʱ���Ƿ���Ҫ������һ�����������������Ϲ���һ��
		if itemCount <= viewCount :									# ������Է������п���ѡ��
			pyViewItem = self.__getViewItem( index )				# Ҫɾ��ѡ��Ķ�Ӧ����ѡ��
			redrawStart = self.__pyViewItems.index( pyViewItem )
			pyViewItem = self.__pyViewItems.pop()					# ɾ��һ������ѡ��
			self.delPyChild( pyViewItem )
			viewCount -= 1
		elif index < firstViewIdx :									# Ҫɾ����ѡ�������ڰ��������
			dec = True												# �����п���ѡ����ǰŲ
		elif lastViewIdx == itemCount - 1 :							# ������������һ��ѡ�
			dec = True												# �����п���ѡ����ǰŲ
		elif index > lastViewIdx :									# Ҫɾ����ѡ�������ڰ�������
			redrawStart = lastViewIdx
		elif index >= firstViewIdx :								# Ҫɾ����ѡ��ɼ�
			pyViewItem = self.__getViewItem( index )				# Ҫɾ��ѡ��Ķ�Ӧ����ѡ��
			redrawStart = self.__pyViewItems.index( pyViewItem )

		oldSelIndex = self.__selIndex
		self.__items.pop( index )									# ɾ��ָ������ѡ��
		if index == self.__selIndex :								# ���ɾ����ѡ��Ϊ��ǰѡ�е�ѡ��
			self.__autoSelectItem()									# �Զ�ѡ��һ��ѡ��
		elif index < self.__selIndex :								# ���ɾ����ѡ����ѡ��ѡ���ǰ��
			self.__selIndex = max( -1, self.__selIndex - 1 )		# ��ѡ��ѡ�����ع�һ��

		for idx in xrange( redrawStart, viewCount ) :
			pyViewItem = self.__pyViewItems[idx]
			if dec :
				newItemIndex = pyViewItem.itemIndex - 1
				pyViewItem.rebind_( newItemIndex )
			self.onDrawItem_( pyViewItem )
		self.__updateScrollBar()									# ���¹�����

		if oldSelIndex == index :									# ���ɾ����ѡ���ǵ�ǰѡ�е�ѡ��
			self.onItemSelectChanged_( self.__selIndex )			# �򣬴���ѡ��ı��¼�

	def addItems( self, items ) :
		"""
		���һ��ѡ��
		"""
		if isDebuged :
			assert None not in items, "item must not be None type"
		if not len( items ) :
			return
		for item in items :
			index = self.itemCount
			self.__items.append( item )
			self.__addViewItem( index )
		if self.__autoSelect and self.__selIndex < 0 :
			self.__selIndex = 0
		self.__updateScrollBar()

	def clearItems( self ) :
		"""
		�������ѡ��
		"""
		self.__pyViewItems = []
		self.__items = []
		self.__selIndex = -1
		self.__updateScrollBar()
		self.onItemSelectChanged_( -1 )

	def updateItem( self, index, item ) :
		"""
		����ָ��ѡ��
		"""
		itemCount = self.itemCount
		if index < 0 or index >= itemCount :
			raise IndexError( "index %i out of range!" % index )
		self.__items[index] = item
		if len( self.__pyViewItems ) :
			firstViewIdx = self.__pyViewItems[0].itemIndex
			lastViewIdx = self.__pyViewItems[-1].itemIndex
			if firstViewIdx <= index <= lastViewIdx :
				pyViewItem = self.__pyViewItems[index - firstViewIdx]
				self.onDrawItem_( pyViewItem )

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		���ָ�������ŵ�ѡ��
		"""
		return  self.__items[index]

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		ѡ�е�ǰѡ��ѡ���ǰһ��ѡ��
		"""
		itemCount = self.itemCount
		selIndex = self.selIndex
		self.selIndex = ( selIndex - 1 ) % itemCount

	def downSelect( self ) :
		"""
		ѡ�е�ǰѡ��ѡ��ĺ�һ��ѡ��
		"""
		itemCount = self.itemCount
		selIndex = self.selIndex
		self.selIndex = ( selIndex + 1 ) % itemCount

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		��������ѡ��( �����ԭ��ѡ��ѡ���ȡ��ѡ��״̬ )
		"""
		selItem = self.selItem
		self.__items.sort( cmp, key, reverse )
		self.__redrawAllViewItems( 0 )
		if selItem is not None :						# �����ԭ��ѡ��ѡ�����������ı�
			selIndex = self.__items.index( selItem )	# �ҳ�ԭ��ѡ��ѡ������˳���е�����
			self.__selectItem( selIndex )				# ����ѡ�и�����

	# -------------------------------------------------
	def resetState( self ) :
		"""
		�ָ�Ĭ��״̬
		"""
		for pyViewItem in self.__pyViewItems :
			pyViewItem.resetState()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getOwnerDraw( self ) :
		return self.__ownerDraw

	def _setOwnerDraw( self, ownerDraw ) :
		self.__ownerDraw = ownerDraw
		if ownerDraw :
			for pyViewItem in self.__pyViewItems :
				pyViewItem.clearDefaultText_()
				self.onViewItemInitialized_( pyViewItem )
				self.onDrawItem_( pyViewItem )
		else :
			for pyViewItem in self.__pyViewItems :
				pyViewItem.addDefaultText_()
				self.onDrawItem_( pyViewItem )

	def _getItemHeight( self ) :
		return self.__itemHeight

	def _setItemHeight( self, height ) :
		assert height > 0, "item height must more then 0!"
		self.__itemHeight = height
		if self.viewCount == 0 : return
		# ������֪ͨ���п���ѡ���ػ�
		firstViewIdx = self.__pyViewItems[0].itemIndex
		viewCount = int( math.ceil( self.height / self.__itemHeight ) )
		viewCount = min( self.itemCount, viewCount )
		self.__pyViewItems = []
		for idx in xrange( viewCount ) :
			self.__addViewItem( firstViewIdx )
			firstViewIdx += 1
		self.__updateScrollBar()									# ���¹��������ܱ�������

	# -------------------------------------------------
	def _getItems( self ) :
		return self.__items[:]

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, selectable ) :
		if self.__selectable == selectable :
			return
		self.__selectable = selectable
		selIndex = self.__selIndex
		self.__selIndex = -1
		pyViewItem = self.__getViewItem( selIndex )
		if pyViewItem :
			self.onDrawItem_( pyViewItem )
		if selectable and self.__autoSelect \
			and self.itemCount :									# �Զ�ѡ��һ��ѡ��
				self.__selIndex = 0
				self.onItemSelectChanged_( 0 )

	# ---------------------------------------
	def _getAutoSelect( self ) :
		return self.__autoSelect

	def _setAutoSelect( self, autoSelect ) :
		self.__autoSelect = autoSelect
		if self.__selectable and autoSelect :						# �Զ�ѡ��һ��ѡ��
			if self.__selIndex < 0 and self.itemCount :
				self.__selIndex = 0
				self.onItemSelectChanged_( 0 )

	# ---------------------------------------
	def _getMouseUpSelect( self ) :
		return self.__mouseUpSelect

	def _setMouseUpSelect( self, mouseUpSelect ) :
		self.__mouseUpSelect = mouseUpSelect

	# ---------------------------------------
	def _getRMouseSelect( self ) :
		return self.__rMouseSelect

	def _setRMouseSelect( self, rMouseSelect ) :
		self.__rMouseSelect = rMouseSelect

	# -------------------------------------------------
	def _getSelIndex( self ) :
		return self.__selIndex

	def _setSelIndex( self, index ) :
		if not self.__selectable : return
		if index > self.itemCount :
			raise IndexError( "index %i is out of range!" % index )
		if index == self.__selIndex : return
		self.__selectItem( index )
		self.onItemSelectChanged_( index )

	def _getSelItem( self ) :
		if self.__selIndex >= 0 :
			return self.__items[self.__selIndex]
		return  None

	def _setSelItem( self, item ) :
		if not self.__selectable : return
		self.selIndex = self.__items.index( item )

	# ---------------------------------------
	def _getItemCount( self ) :
		return len( self.__items )

	def _getViewCount( self ) :
		return len( self.__pyViewItems )

	# ---------------------------------------
	def _getPerScrollCount( self ) :
		return self.__perScrollCount

	def _setPerScrollCount( self, count ) :
		self.__perScrollCount = max( 1, count )

	# -------------------------------------------------
	def _getFont( self ) :
		return self.__font

	def _setFont( self, font ) :
		self.__font = font
		for pyViewItem in self.__pyViewItems :
			self.onDrawItem_( pyViewItem )

	# ---------------------------------------
	def _getItemCommonForeColor( self ) :
		return self.__itemForeColors[UIState.COMMON]

	def _setItemCommonForeColor( self, color ) :
		self.__itemForeColors[UIState.COMMON] = color
		for pyViewItem in self.__pyViewItems :
			self.onDrawItem_( pyViewItem )

	def _getItemCommonBackColor( self ) :
		return self.__itemBackColors[UIState.COMMON]

	def _setItemCommonBackColor( self, color ) :
		self.__itemBackColors[UIState.COMMON] = color
		for pyViewItem in self.__pyViewItems :
			self.onDrawItem_( pyViewItem )

	# ---------------------------------------
	def _getItemHighlightForeColor( self ) :
		return self.__itemForeColors[UIState.HIGHLIGHT]

	def _setItemHighlightForeColor( self, color ) :
		self.__itemForeColors[UIState.HIGHLIGHT] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.height : continue
			self.onDrawItem_( pyViewItem )
			break

	def _getItemHighlightBackColor( self ) :
		return self.__itemBackColors[UIState.HIGHLIGHT]

	def _setItemHighlightBackColor( self, color ) :
		self.__itemBackColors[UIState.HIGHLIGHT] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.height : continue
			self.onDrawItem_( pyViewItem )
			break

	# ---------------------------------------
	def _getItemSelectedForeColor( self ) :
		return self.__itemForeColors[UIState.SELECTED]

	def _setItemSelectedForeColor( self, color ) :
		self.__itemForeColors[UIState.SELECTED] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.selected : continue
			self.onDrawItem_( pyViewItem )
			break

	def _getItemSelectedBackColor( self ) :
		return self.__itemBackColors[UIState.SELECTED]

	def _setItemSelectedBackColor( self, color ) :
		self.__itemBackColors[UIState.SELECTED] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.selected : continue
			self.onDrawItem_( pyViewItem )
			break

	# ---------------------------------------
	def _getItemDisableForeColor( self ) :
		return self.__itemForeColors[UIState.DISABLE]

	def _setItemDisableForeColor( self, color ) :
		self.__itemForeColors[UIState.DISABLE] = color

	def _getItemDisableBackColor( self ) :
		return self.__itemBackColors[UIState.DISABLE]

	def _setItemDisableBackColor( self, color ) :
		self.__itemBackColors[UIState.DISABLE] = color

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		width = self.width
		for pyViewItem in self.__pyViewItems :
			pyViewItem.width = width
			self.onDrawItem_( pyViewItem )

	def _setHeight( self, height ) :
		Control._setHeight( self, height )
		itemCount = self.itemCount
		if itemCount == 0 : return
		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		viewCount = int( math.ceil( self.height / self.__itemHeight ) )
		viewCount = min( itemCount, viewCount )
		currCount = self.viewCount
		if viewCount < currCount :											# ���ٰ��泤��
			self.__pyViewItems = self.__pyViewItems[:viewCount]				# ȥ�����ಿ�ֿɼ�ѡ��
			self.__updateScrollBar()
			hideCount = self.itemCount - self.viewCount
			if hideCount > 0 :
				self.pySBar.onScroll.unbind( self.onScroll_ )				# ȡ�������󶨣����ⴥ�������ص����Ӷ��ڻص���������Ҫ���ػ�
				firstViewIdx = self.__pyViewItems[0].itemIndex
				self.pySBar.value = float( firstViewIdx ) / hideCount		# �ظ�ԭ���Ĺ���λ��
				self.pySBar.onScroll.bind( self.onScroll_ )
		elif viewCount > currCount :										# ���Ӱ��泤��
			addCount = viewCount - currCount
			addedStart = lastViewIdx + 1									# Ҫ���ӵĵ�һ������ѡ���Ӧ��ѡ������
			if lastViewIdx + addCount >= itemCount :						# ����Ѿ��������������Ҫ�ػ����п���ѡ��
				addedStart = itemCount - addCount
				firstViewIdx = addedStart - currCount		 				# ��һ������ѡ���λ��
				self.__redrawAllViewItems( firstViewIdx )					# �ػ�����ѡ��
			for idx in xrange( addCount ) :									# ���ӿ���ѡ��
				self.__addViewItem( addedStart + idx )
			self.__updateScrollBar()
		else :
			self.__updateScrollBar()

	def _getSBarState( self ) :
		return self.__sbarState

	def _setSBarState( self, state ) :
		self.__sbarState = state
		if state == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif state == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif state == ScrollBarST.AUTO :
			self.pySBar.visible = False
		

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyViewItems = property( lambda self : self.__pyViewItems[:] )								# list of ViewItem : ��ȡ���п���ѡ��
	ownerDraw = property( _getOwnerDraw, _setOwnerDraw )										# bool: ��ȡ/�����Ƿ��Ի�
	itemHeight = property( _getItemHeight, _setItemHeight )										# float: ��ȡ/����ѡ��߶�
	items = property( _getItems )																# list: ��ȡ����ѡ��
	selectable = property( _getSelectable, _setSelectable )										# bool: ��ȡ/�����Ƿ�����ѡ��ѡ��
	autoSelect = property( _getAutoSelect, _setAutoSelect )										# bool: ��ȡ/�����Ƿ��Զ�ѡ��һ��ѡ��
	mouseUpSelect = property ( _getMouseUpSelect, _setMouseUpSelect )							# bool: ��ȡ/�����Ƿ����������ʱѡ��ѡ�selectable Ϊ True ʱ�����ã�
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )								# bool: ��ȡ/��������Ҽ����ѡ��ʱ���Ƿ�ѡ��ѡ��
	selIndex = property( _getSelIndex, _setSelIndex )											# int: ��ȡ/���õ�ǰѡ�е�ѡ������
	selItem = property( _getSelItem, _setSelItem )												# ���͸�����ӵ�ѡ���������ȡ/����ѡ��ѡ��
	itemCount = property( _getItemCount )														# int: ��ȡѡ��������
	viewCount = property( _getViewCount )														# int: ��ȡ���ӵ�ѡ������
	perScrollCount = property( _getPerScrollCount, _setPerScrollCount )							# int: ��ȡ/���������ֻ���һ�¹�����ѡ������

	font = property( _getFont, _setFont )														# str: ��ȡ/����ѡ������
	itemCommonForeColor = property( _getItemCommonForeColor, _setItemCommonForeColor )			# tuple: ��ȡ/������ͨ״̬��ѡ���ǰ��ɫ
	itemCommonBackColor = property( _getItemCommonBackColor, _getItemCommonBackColor )			# tuple: ��ȡ/������ͨ״̬��ѡ��ı���ɫ
	itemHighlightForeColor = property( _getItemHighlightForeColor, _setItemHighlightForeColor )	# tuple: ��ȡ/���ø���״̬��ѡ���ǰ��ɫ
	itemHighlightBackColor = property( _getItemHighlightBackColor, _setItemHighlightBackColor )	# tuple: ��ȡ/���ø���״̬��ѡ���ǰ��ɫ
	itemSelectedForeColor = property( _getItemSelectedForeColor, _setItemSelectedForeColor )	# tuple: ��ȡ/����ѡ��״̬��ѡ���ǰ��ɫ
	itemSelectedBackColor = property( _getItemSelectedBackColor, _setItemSelectedBackColor )	# tuple: ��ȡ/����ѡ��״̬��ѡ���ǰ��ɫ
	itemDisableForeColor = property( _getItemDisableForeColor, _setItemDisableForeColor )		# tuple: ��ȡ/������Ч״̬��ѡ���ǰ��ɫ
	itemDisableBackColor = property( _getItemDisableBackColor, _setItemDisableBackColor )		# tuple: ��ȡ/������Ч״̬��ѡ���ǰ��ɫ

	width = property( Control._getWidth, _setWidth )											# float: ��ȡ/���ð�����
	height = property( Control._getHeight, _setHeight )											# float: ��ȡ/���ð���߶�
	sbarState = property( _getSBarState, _setSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE


# --------------------------------------------------------------------
# implement inner item class
# --------------------------------------------------------------------
class ViewItem( Control ) :
	def __init__( self, pyPanel, item = None, pyBinder = None ) :
		if item is None :
			item = hfUILoader.load( "guis/controls/odlistpanel/viewitem.gui" )
		Control.__init__( self, item, pyBinder )
		self.__pyPanel = pyPanel
		self.focus = True
		self.crossFocus = True

		self.__itemIndex = 0
		self.__pyText = None
		self.__selected = False
		self.__highlight = False

	def __del__( self ) :
		if Debug.output_del_ODListPanel :
			INFO_MSG( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def rebind_( self, index ) :
		"""
		���°�һ���б�ѡ��
		"""
		self.__itemIndex = index
		if self.__pyText :
			listItem = self.listItem
			self.__pyText.text = listItem
			if FullText.pyBinder == self :
				FullText.show( self, self.__pyText, False )

	# -------------------------------------------------
	def addDefaultText_( self ) :
		"""
		����һ��Ĭ�ϵ�ѡ���ı���ǩ( ��ʼ�� ViewItem ʱ������ )
		"""
		if self.__pyText : return
		self.clearChildren()
		staticText = hfUILoader.load( "guis/controls/odlistpanel/itemtext.gui" )
		self.__pyText = StaticText( staticText )
		self.__pyText.text = self.listItem
		self.addPyChild( self.__pyText )
		self.__pyText.r_left = uiFixer.toFixedX( self.__pyText.r_left )
		self.__pyText.middle = self.height / 2

	def updateDefaultText_( self ) :
		"""
		���Ĭ�ϵ�ѡ���ı����ػ�ʱ�����ã�
		"""
		if not self.__pyText : return
		listItem = self.listItem
		if not isinstance( listItem, basestring ) :						# �Ƿ��ǺϷ���Ĭ��ѡ��
			return
		pyPanel = self.pyPanel
		self.__pyText.font = pyPanel.font
		if self.selected :
			self.__pyText.color = pyPanel.itemSelectedForeColor			# ѡ��״̬�µ�ǰ��ɫ
			self.color = pyPanel.itemSelectedBackColor					# ѡ��״̬�µı���ɫ
		elif self.highlight :
			self.__pyText.color = pyPanel.itemHighlightForeColor		# ����״̬�µ�ǰ��ɫ
			self.color = pyPanel.itemHighlightBackColor				# ����״̬�µı���ɫ
		else :
			self.__pyText.color = pyPanel.itemCommonForeColor
			self.color = pyPanel.itemCommonBackColor

	def clearDefaultText_( self ) :
		"""
		���Ĭ����Ϣ
		"""
		if self.__pyText :
			self.delPyChild( self.__pyText )
			self.__pyText = None

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		return self.pyPanel.onViewItemLMouseDown_( self, mods )

	def onLMouseUp_( self, mods ) :
		return self.pyPanel.onViewItemLMouseUp_( self, mods )

	def onLClick_( self, mods ) :
		return self.pyPanel.onViewItemLClick_( self, mods )

	def onRMouseDown_( self, mods ) :
		return self.pyPanel.onViewItemRMouseDown_( self, mods )

	def onRMouseUp_( self, mods ) :
		return self.pyPanel.onViewItemRMouseUp_( self, mods )

	def onRClick_( self, mods ) :
		return self.pyPanel.onViewItemRClick_( self, mods )

	def onLDBClick_( self, mods ) :
		return self.pyPanel.onViewItemLDBClick_( self, mods )

	def onMouseEnter_( self ) :
		self.__highlight = True
		pyPanel = self.pyPanel
		pyPanel.onDrawItem_( self )
		pyPanel.onItemMouseEnter_( self )
		if self.__pyText and self.__pyText.width > self.width :
			FullText.show( self, self.__pyText )
		return True

	def onMouseLeave_( self ) :
		self.__highlight = False
		pyPanel = self.pyPanel
		pyPanel.onDrawItem_( self )
		pyPanel.onItemMouseLeave_( self )
		if self.__pyText :
			FullText.hide()
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
			self.pyPanel.onDrawItem_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemIndex( self ) :
		return self.__itemIndex

	def _getListItem( self ) :
		return self.pyPanel.getItem( self.__itemIndex )

	def _getSelected( self ) :
		return self.__itemIndex == self.pyPanel.selIndex

	def _getHighlight( self ) :
		return self.__highlight
	
	def _getPyText( self ):
		return self.__pyText
	
	def _setPyText( self, pyText ):
		if not self.__pyText:
			self.__pyText = pyText

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyPanel = property( lambda self : self.__pyPanel ) 		# ��ȡ�������б����
	itemIndex = property( _getItemIndex )					# ��ȡ��Ӧѡ�����б�����е�����
	listItem = property( _getListItem )						# ��ȡ��Ӧ���б�ѡ��
	selected = property( _getSelected )						# ��ȡ��ѡ���Ƿ��Ǳ�ѡ��ѡ��
	highlight = property( _getHighlight )					# ��ȡ��ѡ���Ƿ��ڸ���״̬
	pyText = property( _getPyText, _setPyText )			# ��ȡ�ı��ؼ�

