# -*- coding: gb18030 -*-

"""
implement minimap class
"""

from guis import *
from guis.common.RootGUI import RootGUI
from BDuffItem import BDuffItem

class BDuffPanel( RootGUI ) :

	def __init__( self ) :
		panel = GUI.load( "guis/general/bduffpanel/panel.gui" )
		uiFixer.firstLoadFix( panel )
		RootGUI.__init__( self, panel )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.focus = False
		self.escHide_ = False
		self.activable_ = False
		self.posZSegment = ZSegs.L5
		self.visible = True

		self.__pyBuffItems = []
		self.__pyDuffItems = []
		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_ADD_BUFF"] = self.__onAddBuff
		self.__triggers["EVT_ON_ROLE_ADD_DUFF"] = self.__onAddDuff
		self.__triggers["EVT_ON_ROLE_REMOVE_BUFF"] = self.__onRemoveBuff
		self.__triggers["EVT_ON_ROLE_REMOVE_DUFF"] = self.__onRemoveDuff
		self.__triggers["EVT_ON_ROLE_UPDATE_BUFF"] = self.__onUpdate
		self.__triggers["EVT_ON_ROLE_VEHICLES_INITED"] = self.__onVehicleUpdate	# �������buffͼ��
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __onAddBuff( self, buffInfo ) :
		"""
		���һ������buff
		"""
		pyBuffItem = BDuffItem()
		pyBuffItem.update( buffInfo )
		self.addPyChild( pyBuffItem )
		self.__pyBuffItems.append( pyBuffItem )
		self.__layoutItems()

#		if buffInfo.baseItem.getBuffID() == "006005" :			# ��һ���ٻ������ʾ
#			toolbox.infoTip.showOperationTips( 0x0046, pyBuffItem )

	def __onAddDuff( self, duffInfo  ) :
		"""
		���һ������buff
		"""
		pyDuffItem = BDuffItem()
		pyDuffItem.update( duffInfo )
		self.addPyChild( pyDuffItem )
		self.__pyDuffItems.append( pyDuffItem )
		self.__layoutItems()

	def __onRemoveBuff( self, buffInfo  ) :
		"""
		�Ƴ�һ������buff
		"""
		pyBuffItem = _findPyBDuff( self.__pyBuffItems, buffInfo )
		if pyBuffItem is not None :
			self.__pyBuffItems.remove( pyBuffItem )
			pyBuffItem.dispose()
			self.__layoutItems()
		else :
			ERROR_MSG( "Can't find buff item by id %s when remove buff." % buffInfo.baseItem.getBuffID() )

	def __onRemoveDuff( self, duffInfo ) :
		"""
		�Ƴ�һ������buff
		"""
		pyDuffItem = _findPyBDuff( self.__pyDuffItems, duffInfo )
		if pyDuffItem is not None :
			self.__pyDuffItems.remove( pyDuffItem )
			pyDuffItem.dispose()
			self.__layoutItems()
		else :
			ERROR_MSG( "Can't find duff item by id %s when remove duff." % duffInfo.baseItem.getBuffID() )

	def __onUpdate( self, buffInfo ) :
		"""
		update : buffdata or duffdata
		"""
		pyBDItems = self.__pyBuffItems + self.__pyDuffItems
		pyItem = _findPyBDuff( pyBDItems, buffInfo )
		if pyItem is not None :
			pyItem.update( buffInfo )
		else :
			ERROR_MSG( "Can't find buff item by id %s when update buff." % buffInfo.baseItem.getBuffID() )

	def __onVehicleUpdate( self ):
		for pyItem in self.__pyBuffItems:
			if pyItem.itemInfo.baseItem.getBuffID() == "001022":	# ������Լӳ�buff
				pyItem.update( pyItem.itemInfo )

	def __layoutItems( self ) :
		"""
		����buffͼ��
		"""
		maxCols = 8				# ÿһ�������ʾ��buff����
		currRow = 0				# ��ǰ������
		itemSize = 37, 46		# buffItem�ĳߴ�
		for index, pyItem in enumerate( self.__pyBuffItems ) :				# ����buff��������
			currCol = index % maxCols
			if currCol == 0 and index > 0 : currRow += 1
			pyItem.right = self.width - itemSize[0] * currCol
			pyItem.top = itemSize[1] * currRow
		for index, pyItem in enumerate( self.__pyDuffItems ) :				# ����buff��������buff����
			currCol = index % maxCols
			if currCol == 0 : currRow += 1
			pyItem.right = self.width - itemSize[0] * currCol
			pyItem.top = itemSize[1] * currRow
		buffAmount = len( self.__pyBuffItems )
		if buffAmount or currRow : currRow += 1
		self.height = currRow * itemSize[1]									# �趨buff����ĸ߶�
		maxItems = max( buffAmount, len( self.__pyDuffItems ) )
		columns = min( maxCols, maxItems )
		self.width = columns * itemSize[0]									# �趨buff����Ŀ��

#		toolbox.infoTip.moveOperationTips( 0x0046 )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def isMouseHit( self ) :
		"""
		��д������buff���
		Ŀ���Ƿ�ֹ����/NPC�����ε���嵲ס��������겻�ܱ仯
		���磺�������д�˺����������������Ļ���Ϸ���buff���ʱ�����ŵ��������ϾͲ����ɵ�����״����������
		"""
		if not RootGUI.isMouseHit( self ) :
			return False
		for pyItem in self.__pyBuffItems  + self.__pyDuffItems :
			if pyItem.itemInfo is None :
				continue
			if pyItem.isMouseHit() :
				return True
		return False

	def onEnterWorld( self ) :
		"""
		buff������κ�ʱ����ʾ�ģ�������������н���ʱ���ߣ�
		�����ߺ�������潫������ʾ
		"""
		self.show()

	def onLeaveWorld( self ) :
		for pyItem in self.__pyBuffItems + self.__pyDuffItems :
			pyItem.dispose()
		self.__pyBuffItems = []
		self.__pyDuffItems = []


def _findPyBDuff( pyBDuffList, buffInfo ) :
	"""
	����buff�б��ж�Ӧ��buff
	@param		pyBDuffList	: �����˽���buffԪ�ص��б�
	@param		buffInfo	: ����Ŀ��buff��Ϣ��ʵ��
	@return					: �ҵ����򷵻�һ��pyItem��������None
	"""
	if buffInfo is None:return None
	dstBuffIndex = buffInfo.buffIndex
	for pyItem in pyBDuffList :
		itemInfo = pyItem.itemInfo
		if itemInfo and \
			itemInfo.buffIndex == dstBuffIndex:
				return pyItem
	return None
