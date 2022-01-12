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
		self.__triggers["EVT_ON_ROLE_VEHICLES_INITED"] = self.__onVehicleUpdate	# 更新骑宠buff图标
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __onAddBuff( self, buffInfo ) :
		"""
		获得一个增益buff
		"""
		pyBuffItem = BDuffItem()
		pyBuffItem.update( buffInfo )
		self.addPyChild( pyBuffItem )
		self.__pyBuffItems.append( pyBuffItem )
		self.__layoutItems()

#		if buffInfo.baseItem.getBuffID() == "006005" :			# 第一次召唤骑宠提示
#			toolbox.infoTip.showOperationTips( 0x0046, pyBuffItem )

	def __onAddDuff( self, duffInfo  ) :
		"""
		获得一个减益buff
		"""
		pyDuffItem = BDuffItem()
		pyDuffItem.update( duffInfo )
		self.addPyChild( pyDuffItem )
		self.__pyDuffItems.append( pyDuffItem )
		self.__layoutItems()

	def __onRemoveBuff( self, buffInfo  ) :
		"""
		移除一个增益buff
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
		移除一个减益buff
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
			if pyItem.itemInfo.baseItem.getBuffID() == "001022":	# 骑宠属性加成buff
				pyItem.update( pyItem.itemInfo )

	def __layoutItems( self ) :
		"""
		排列buff图标
		"""
		maxCols = 8				# 每一行最多显示的buff个数
		currRow = 0				# 当前行索引
		itemSize = 37, 46		# buffItem的尺寸
		for index, pyItem in enumerate( self.__pyBuffItems ) :				# 增益buff排在上面
			currCol = index % maxCols
			if currCol == 0 and index > 0 : currRow += 1
			pyItem.right = self.width - itemSize[0] * currCol
			pyItem.top = itemSize[1] * currRow
		for index, pyItem in enumerate( self.__pyDuffItems ) :				# 减益buff排在增益buff下面
			currCol = index % maxCols
			if currCol == 0 : currRow += 1
			pyItem.right = self.width - itemSize[0] * currCol
			pyItem.top = itemSize[1] * currRow
		buffAmount = len( self.__pyBuffItems )
		if buffAmount or currRow : currRow += 1
		self.height = currRow * itemSize[1]									# 设定buff界面的高度
		maxItems = max( buffAmount, len( self.__pyDuffItems ) )
		columns = min( maxCols, maxItems )
		self.width = columns * itemSize[0]									# 设定buff界面的宽度

#		toolbox.infoTip.moveOperationTips( 0x0046 )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def isMouseHit( self ) :
		"""
		重写鼠标进入buff面板
		目的是防止怪物/NPC被隐形的面板挡住，导致鼠标不能变化
		例如：如果不重写此函数，当怪物进入屏幕右上方的buff面板时，鼠标放到怪物身上就不会变成刀的形状，而还是手
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
		buff面板是任何时候都显示的，如果在隐藏所有界面时掉线，
		再上线后这个界面将不会显示
		"""
		self.show()

	def onLeaveWorld( self ) :
		for pyItem in self.__pyBuffItems + self.__pyDuffItems :
			pyItem.dispose()
		self.__pyBuffItems = []
		self.__pyDuffItems = []


def _findPyBDuff( pyBDuffList, buffInfo ) :
	"""
	查找buff列表中对应的buff
	@param		pyBDuffList	: 保存了界面buff元素的列表
	@param		buffInfo	: 包含目标buff信息的实例
	@return					: 找到了则返回一个pyItem，否则是None
	"""
	if buffInfo is None:return None
	dstBuffIndex = buffInfo.buffIndex
	for pyItem in pyBDuffList :
		itemInfo = pyItem.itemInfo
		if itemInfo and \
			itemInfo.buffIndex == dstBuffIndex:
				return pyItem
	return None
