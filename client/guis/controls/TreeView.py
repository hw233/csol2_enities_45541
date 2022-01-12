# -*- coding: gb18030 -*-
#
# $Id: TreeView.py,v 1.50 2008-08-30 09:04:58 huangyongwei Exp $

"""
implement listitem class
2005/12/02 : writen by huangyongwei
"""

import weakref
from guis import *
from guis.UIFixer import hfUILoader
from guis.controls.Control import Control
from guis.controls.ScrollPanel import HVScrollPanel
from guis.controls.ScrollPanel import VScrollPanel
from guis.controls.StaticText import StaticText
from guis.controls.Icon import Icon
from guis.tooluis.fulltext.FullText import FullText
import csstring
import Font

# --------------------------------------------------------------------
# global functions
# --------------------------------------------------------------------
def travelTreeNode( pyNode, doFunc ) :
	"""
	遍历某个树节点
	@type				pyNode : TreeNone
	@param				pyNode : 要遍历的树节点
	@type				doFunc : function
	@param				doFunc : callback 遍历每一个节点时，该函数将会被调用，它必须包含一个参数，以表示当前遍历到的节点
	@return					   : None
	"""
	stack = Stack()
	stack.push( pyNode )
	while( stack.size() ) :
		pyNode = stack.pop()
		if doFunc( pyNode ) :
			return True
		pyNodes = pyNode.pyNodes[:]
		pyNodes.reverse()
		stack.pushs( pyNodes )
	return False


# --------------------------------------------------------------------
# implement treeview base class
"""
composing :
	-- clipPanel ( GUI.Window )
		-- nodesPanel ( GUI.Window )
	-- hScrollBar ( GUI.Window )
		-- incBtn ( GUI.Simple )
		-- decBtn ( GUI.Simple )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Window )
	-- vScrollBar ( GUI.Window )
		-- incBtn ( GUI.Simple )
		-- decBtn ( GUI.Simple )
		-- slot ( GUI.Window )
			-- moveBar ( GUI.Window )
"""
# --------------------------------------------------------------------
class TreeViewBase :
	def __init__( self, panel ) :
		self.__pyNodes = Nodes( panel.nodesPanel, self, self )			# 节点集合板面
		self.__nodeOffset = 0											# 子节点与父节点的水平位置偏移
		self.__showPlusMinus = True										# 是否显示加减号
		self.__rightClickSelect = False									# 右键点击节点时，是否选中节点
		self.__pySelNode = None											# 当前选中的节点
		self.__pyHighlightNode = None									# 当前处于高亮状态的节点
		self.__wspon = False											# 是否显示没有子节点的节点的“＋”号

		self.nodeOffset = 16											# 节点偏移默认为 16 个像素
		self.isExtended = True											# 树视图默认是展开的


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		生成事件
		"""
		self.__onTreeNodeLClick = self.createEvent_( "onTreeNodeLClick" )					# 但左键点击某个节点时被触发
		self.__onTreeNodeRClick = self.createEvent_( "onTreeNodeRClick" )					# 当右键点击某个节点时被触发
		self.__onTreeNodeSelected = self.createEvent_( "onTreeNodeSelected" )				# 当选中某个节点时被触发
		self.__onTreeNodeDeselected = self.createEvent_( "onTreeNodeDeselected" )			# 当某个节点取消选中状态时被触发
		self.__onTreeNodeBeforeExtend = self.createEvent_( "onTreeNodeBeforeExtend" )		# 当某个节点将要展开时被触发
		self.__onTreeNodeBeforeCollapse = self.createEvent_( "onTreeNodeBeforeCollapse" )	# 当某个节点将要折叠时被触发
		self.__onTreeNodeExtended = self.createEvent_( "onTreeNodeExtended" )				# 当某个节点展开时被触发
		self.__onTreeNodeCollapsed = self.createEvent_( "onTreeNodeCollapsed" )				# 当某个节点折叠时被触发
		self.__onTreeNodeAdded = self.createEvent_( "onTreeNodeAdded" )						# 当添加某个节点时被触发
		self.__onTreeNodeRemoved = self.createEvent_( "onTreeNodeRemoved" )					# 当删除某个节点时被触发

	# -------------------------------------------------
	@property
	def onTreeNodeLClick( self ) :
		"""
		但左键点击某个节点时被触发
		"""
		return self.__onTreeNodeLClick

	@property
	def onTreeNodeRClick( self ) :
		"""
		当右键点击某个节点时被触发
		"""
		return self.__onTreeNodeRClick

	@property
	def onTreeNodeSelected( self ) :
		"""
		当选中某个节点时被触发
		"""
		return self.__onTreeNodeSelected

	@property
	def onTreeNodeDeselected( self ) :
		"""
		当某个节点取消选中状态时被触发
		"""
		return self.__onTreeNodeDeselected

	# ---------------------------------------
	@property
	def onTreeNodeBeforeExtend( self ) :
		"""
		当某个节点将要展开时被触发
		"""
		return self.__onTreeNodeBeforeExtend

	@property
	def onTreeNodeBeforeCollapse( self ) :
		"""
		当某个节点将要折叠时被触发
		"""
		return self.__onTreeNodeBeforeCollapse

	@property
	def onTreeNodeExtended( self ) :
		"""
		当某个节点展开时被触发
		"""
		return self.__onTreeNodeExtended

	@property
	def onTreeNodeCollapsed( self ) :
		"""
		当某个节点折叠时被触发
		"""
		return self.__onTreeNodeCollapsed

	@property
	def onTreeNodeAdded( self ) :
		"""
		当添加某个节点时被触发
		"""
		return self.__onTreeNodeAdded

	@property
	def onTreeNodeRemoved( self ) :
		"""
		当删除某个节点时被触发
		"""
		return self.__onTreeNodeRemoved


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onScroll_( self, value ) :
		"""
		内容随滚动条滚动时被调用
		"""
		pyHNode = self.pyHighlightNode
		if pyHNode is not None :
			pyHNode.onMouseLeave__()			# 内容滚动时，主动触发高亮节点的鼠标离开函数

	# -------------------------------------------------
	def onNodesWidthChanged_( self, width ) :
		"""
		全部节点的宽度改变时被调用
		"""
		pass

	def onModesHeightChanged_( self, height ) :
		"""
		全部节点的高度改变时被调用
		"""
		pass

	# ---------------------------------------
	def scrollToNode( self, pyNode ) :
		"""
		如果某个节点不可见，则滚动到某个节点处（让某个节点可见）
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def extendAll( self ) :
		"""
		展开所有节点
		"""
		def extendNode( pyNode ) :
			pyNode.extend()
		for pyNode in self.__pyNodes :
			travelTreeNode( pyNode, extendNode )

	def collapseAll( self ) :
		"""
		合拢所有节点
		"""
		def collapseNode( pyNode ) :
			pyNode.collapse()
		for pyNode in self.__pyNodes :
			travelTreeNode( pyNode, collapseNode )

	# -------------------------------------------------
	def getNodeAt( self, x, y ) :
		"""
		获取指定像素坐标下的节点，如果没有则返回 None
		"""
		def isNodePoint( pyNode ) :								# 判断指定点是否落在节点上
			if pyNode.hitTest( x, y ) :							# 如果是
				return True										# 则返回 True
			return False										# 否则返回 False

		def isCollapsed( pyNode ) :								# 判断指定节点是否处于合拢状态
			pyParentNode = pyNode.pyParentNode					# 节点的父节点
			while isinstance( pyParentNode, TreeNode ) :		# 遍历父节点
				if not pyParentNode.isExtended :				# 如果有任何一个父节点是合拢的
					return True									# 则返回 True，表示节点处于合拢状态
				pyParentNode = pyParentNode.pyParentNode		# 否则，纵向继续节点的父节点
			return False										# 如果全部都没有处于合拢状态，则返回 False

		queue = Queue()											# 创建一个临时队列
		queue.enters( self.__pyNodes )							# 将所有顶层节点入队
		while queue.length() :									# 遍历树视图，直到队列为空
			pyNode = queue.leave()								# 让一个节点离队
			collapsed = isCollapsed( pyNode )					# 判断出列的节点是否是合拢的
			if isNodePoint( pyNode ) and not collapsed :		# 判断指定的坐标是否落在节点上
				return pyNode									# 如果指定坐标落在节点上，并且节点没有处于合拢状态，则返回该节点
			if not collapsed and pyNode.isExtended :			# 如果节点的父节点是展开的，而且节点本身也是展开的
				queue.enters( pyNode.pyNodes )					# 则继续将节点的子节点入队
		return None												# 指定的坐标下没有相应的节点

	def getHitNode( self ) :
		"""
		获取鼠标指向位置处的节点，存在则返回指向的节点，否则返回 None
		"""
		x, y = csol.pcursorPosition()
		return self.getNodeAt( x, y )

	# -------------------------------------------------
	def travelAllNodes( self, doFunc ) :
		"""
		遍历所有子节点
		@type				doFunc : function
		@param				doFunc : callback 遍历每一个节点时，该函数将会被调用，它必须包含一个参数，以表示当前遍历到的节点
		@rtype					   : bool
		@param					   : 如果找到，则返回 True，如果没找到，则返回 False
		"""
		for pyNode in self.__pyNodes :
			if travelTreeNode( pyNode, doFunc ) :
				return True
		return False


	# ----------------------------------------------------------------
	# friend methods of treenode
	# ----------------------------------------------------------------
	def onSubNodeBeforeExtend__( self, pyNode ) :
		"""
		当某个子节点将要展开时被调用
		"""
		self.onTreeNodeBeforeExtend( pyNode )

	def onSubNodeBeforeCollapse__( self, pyNode ) :
		"""
		当某个子节点将要展开时被调用
		"""
		self.onTreeNodeBeforeCollapse( pyNode )

	# ---------------------------------------
	def onSubNodeExtended__( self, pyNode, pyExtendedNode ) :
		"""
		某个子节点展开则被调用
		"""
		self.onModesHeightChanged_( self.__pyNodes.height )	# 节点版面高度改变
		self.onTreeNodeExtended( pyExtendedNode )			# 触发节点展开事件

	def onSubNodeCollapsed__( self, pyNode, pyCollapsedNode ) :
		"""
		某个子节点合拢时被调用
		"""
		self.onModesHeightChanged_( self.__pyNodes.height )	# 节点版面高度改变
		self.onTreeNodeCollapsed( pyCollapsedNode )			# 触发节点合拢事件

	# ---------------------------------------
	def onSubNodeAddSubNode__( self, pyNode ) :
		"""
		某个子节点添加子节点时被调用
		"""
		self.onModesHeightChanged_( self.__pyNodes.height )	# 节点版面高度改变
		self.onTreeNodeAdded( pyNode )						# 触发添加节点事件

	def onSubNodeRemoveSubNode__( self, pyNode ) :
		"""
		某个节点删除子节点时被调用
		"""
		if self.__pySelNode == pyNode :						# 如果当前选中的节点是被删除节点
			self.__pySelNode = None							# 则，设置被选中节点为 None
		self.onModesHeightChanged_( self.__pyNodes.height )	# 节点版面高度改变
		self.onTreeNodeRemoved( pyNode )					# 触发删除节点事件

	#----------------------------------------
	def onSubNodesWidthChanged__( self ) :
		"""
		所有节点宽度改变时被调用
		"""
		self.onNodesWidthChanged_( self.__pyNodes.right )	# 节点版面宽度改变

	#----------------------------------------
	def onNodeSelected__( self, pyNode ) :
		"""
		当某个节点选中时被调用
		"""
		if pyNode == self.__pySelNode : return				# 如果节点已经被选中，则返回
		if self.__pySelNode is not None :					# 如果之前有选中的节点
			self.__pySelNode.selected = False				# 则将之前选中的节点设置为没有被选中
		self.__pySelNode = pyNode							# 重新设置当前被选中的节点
		self.onNodeHighlight__( pyNode )					# 高亮显示新选中的节点
		self.onTreeNodeSelected( pyNode )					# 触发节点选中事件

	def onNodeDeselected__( self, pyNode ) :
		"""
		节点取消选中时被调用
		"""
		self.__pySelNode = None								# 设置当前选中的节点为 None
		self.onTreeNodeDeselected( pyNode )					# 触发节点取消选中事件

	# ---------------------------------------
	def onNodeHighlight__( self, pyNode ) :
		"""
		当要某个节点高亮显示时被调用
		"""
		pyHNode = self.pyHighlightNode						# 之前高亮显示的节点
		if pyNode == pyHNode : return						# 如果与之前的节点一致，则返回
		if pyHNode : pyHNode.setState( UIState.COMMON )		# 如果之前有高亮显示的节点，则将之前的高亮节点设置普通状态
		if pyNode is None :
			self.__pyHighlightNode = None
		else :
			self.__pyHighlightNode = weakref.ref( pyNode )	# 重新设置新的高亮节点


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getParentNode( self ) :
		return None

	# ---------------------------------------
	def _getNodes( self ) :
		return self.__pyNodes

	# ---------------------------------------
	def _getNodeOffset( self ) :
		return self.__nodeOffset

	def _setNodeOffset( self, offset ) :
		self.__nodeOffset = offset
		self.__pyNodes.setNodeOffset__( offset )

	# -------------------------------------------------
	def _getPySelNode( self ) :
		return self.__pySelNode

	def _setPySelNode( self, pyNode ) :
		pyNode.selected = True

	# ---------------------------------------
	def _getHighlightNode( self ) :
		if self.__pyHighlightNode is None :
			return None
		return self.__pyHighlightNode()

	# -------------------------------------------------
	def _getShowPlusMinus( self ) :
		return self.__showPlusMinus

	def _setShowPlusMinus( self, value ) :
		self.__showPlusMinus = value
		for pyNode in self.pyNodes :
			pyNode.showPlusMinus = value

	# -------------------------------------------------
	def _getRCSelect( self ) :
		return self.__rightClickSelect

	def _setRCSelect( self, value ) :
		self.__rightClickSelect = value
		self.__pyNodes.toggleRightClickSelect__( value )

	# -------------------------------------------------
	def _getWspon( self ) :
		return self.__wspon

	def _setWspon( self, wspon ) :
		self.__wspon = wspon


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyParentNode = property( _getParentNode )							# 父节点，始终返回 None
	pyNodes = property( _getNodes )										# Nones：节点板面同时也时节点集合
	nodeOffset = property( _getNodeOffset, _setNodeOffset )				# 节点与父节点的水平偏移
	pySelNode = property( _getPySelNode, _setPySelNode )				# 当前被选中的节点
	pyHighlightNode = property( _getHighlightNode )						# 当前处于高亮状态的按钮
	showPlusMinus = property( _getShowPlusMinus, _setShowPlusMinus )	# 是否显示加减号
	rightClickSelect = property( _getRCSelect, _setRCSelect )			# 是否设置为右键点击选中
	wspon = property( _getWspon, _setWspon )							# 是否显示没有子节点的节点的“+”号（whether show plus of the node which has no sub nodes）
																		# 也就是说，如果某个节点即使它没有子节点，当其处于折叠状态时，也会显示前面的加号


# --------------------------------------------------------------------
# implement tree nodes panel
# --------------------------------------------------------------------
class Nodes( Control ) :
	def __init__( self, panel = None, pyOwner = None, pyTreeView = None ) :
		Control.__init__( self, panel )
		self.__pyTreeView = None
		self.__pyOwner = None
		self.__initialize( panel, pyOwner, pyTreeView )					# 初始化
		self.__pyNodes = []												# 所有节点列表
		

		self.__nodeOffset = 0											# 节点与父节点的水平偏移
		self.__rightClickSelect = False									# 是否右键点击选中节点

	def subclass( self, panel, pyOwner, pyTreeView ) :
		Control.subclass( self, panel )
		self.__initialize( panel, pyOwner, pyTreeView )
		return self

	def __del__( self ) :
		self.clear()											# 清除所有节点（注意：不能 dispose 所有节点，因为外部可能还有人引用它们）
		Control.__del__( self )
		if Debug.output_del_TreeView :
			INFO_MSG( "TreeNodes<%i>" % id( self ) )

	# ---------------------------------------
	def __initialize( self, panel, pyOwner, pyTreeView ) :
		if panel is None : return
		if pyTreeView :
			self.__pyTreeView = weakref.ref( pyTreeView )		# 所属的树视图
		if pyOwner :
			self.__pyOwner = weakref.ref( pyOwner )				# 所属的父节点（如果是顶层列表，则它等于所属的树视图）
		Control._setSize( self, ( 0, 0 ) )						# 默认没有任何节点，所以高度默认为 0


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		try :
			return "TeeeNodes(%s)" % str( self.__pyNodes )
		except :
			return "TreeNodes<%s>" % id( self )

	def __str__( self ) :
		return self.__repr__()

	def __contains__( self, pyNode ) :
		return pyNode in self.__pyNodes

	def __len__( self ) :
		return len( self.__pyNodes )

	def __iter__( self ) :
		return self.__pyNodes.__iter__()

	def __getitem__( self, index ) :
		return self.__pyNodes[index]

	def __getslice__( self, start, end ) :
		return self.__pyNodes.__getslice__( start, end )

	def __radd__( self, pyNodes ) :
		return pyNodes + self.__pyNodes


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layoutNode( self, pyNode ) :
		"""
		排列指定节点的位置
		"""
		pyFore = pyNode.pyFore								# 指定节点的前一个节点
		if pyFore is None : pyNode._setTop( 0 )				# 如果指定节点是第一个节点，则将顶距设置为 0
		else : pyNode._setTop( pyFore.bottom )				# 否则，将指定节点的顶距设置为它前面一个节点的底距
		pyNode._setLeft( 0 )								# 节点的左距为 0

	def __layoutNodes( self, pyStart = None ) :
		"""
		排列所有节点的位置（从指定节点 pyStart 开始排列）
		这样设计的目的是：当后面添加一个节点时，无需重排前面节点的位置，插入一个节点时，也无需重排插入节点前面节点的位置
		"""
		while( pyStart is not None ) :						# 从指定的节点开始遍历它后面的节点
			self.__layoutNode( pyStart )					# 设置节点位置
			pyStart = pyStart.pyNext						# 将 start 指向下一个节点
		if self.pyLast is None :							# 如果最后一个节点为 None，则意味着没有任何节点
			Control._setHeight( self, 0 )					# 则，设置节点列表高度为 0
		else :												# 否则
			Control._setHeight( self, self.pyLast.bottom )	# 高度为最后一个节点的底距

	# -------------------------------------------------
	def __pasteNode( self, pyNode ) :
		"""
		向列表板面上粘贴一个节点
		"""
		pyPNode = self.pyOwner								# 节点列表的所属节点
		while pyPNode is not None :							# 循环遍历父节点
															# 如果将父节点添加到列表中，则引发一个错误
			assert pyPNode != pyNode, "you can't add its parent node as its child node!"
			pyPNode = pyPNode.pyParentNode					# 重新指向父节点的父节点

		if pyNode.pyParentNode is not None :				# 如果要添加的节点还有父节点
			pyNode.pyParentNode.pyNodes.remove( pyNode )	# 则首先将其从它的父节点中删除
		self.addPyChild( pyNode )							# 粘贴节点
		return True											# 返回粘贴成功

	# -------------------------------------------------
	def __attachSubNode( self, pyNode ) :
		"""
		初始化要添加的节点(绑定节点的一些属性)
		"""
		pyNode.setTreeView__( self.pyTreeView )							# 设置节点的所属树视图
		pyNode.setParentNode__( self.pyOwner )							# 设置节点所属的父节点
		pyNode.toggleRightClickSelect__( self.__rightClickSelect )		# 设置是否右键点击选中节点
		pyNode.nodeOffset = self.__nodeOffset							# 设置节点的父子节点水平位置偏移
		if pyNode.selected : pyNode.selected = False					# 如果节点处于选中状态，则取消节点的选中状态

	def __detachSubNode( self, pyNode ) :
		"""
		取消指定节点的属性绑定
		"""
		pyNode.setParentNode__( None )					# 取消所属父节点的绑定
		pyNode.toggleRightClickSelect__( False )		# 取消右键点击选中属性
		pyNode.setForeNode__( None )					# 取消前接兄弟节点
		pyNode.setNextNode__( None )					# 取消后接兄弟节点
		pyNode.collapse()								# 合拢节点
		pyNode.detach__()								# 释放节点


	# ----------------------------------------------------------------
	# friend methods of this module
	# ----------------------------------------------------------------
	def onNodeExtended__( self, pyNode, pyExtendedNode ) :
		"""
		当某个节点展开时被调用
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeExtended__( pyNode, pyExtendedNode )

	def onNodeCollapsed__( self, pyNode, pyCollapsedNode ) :
		"""
		当某个节点合拢或子节点的孙节点合龙时被调用
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeCollapsed__( pyNode, pyCollapsedNode )

	# -------------------------------------------------
	def onNodeAddSubNode__( self, pyNode ) :
		"""
		当某个节点天际子节点时被调用
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeAddSubNode__( pyNode )

	def onNodeRemoveSubNode__( self, pyNode ) :
		"""
		当某个节点删除子节点时被调用
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeRemoveSubNode__( pyNode )

	# ---------------------------------------
	def onNodeWidthChanged__( self, pyNode = None ) :
		"""
		某节点宽度改变时被调用
		"""
		pyOwner = self.pyOwner
		if self.count == 0 :									# 没有子了节点
			Control._setWidth( self, 0 )						# 设置宽度为 0
			if pyOwner : pyOwner.onSubNodesWidthChanged__()		# 如果存在父节点，则，通知父节点，宽度改变
			return

		currWidth = self.width									# 当前宽度
		if not pyNode or currWidth > pyNode.right :				# 如果没有想过的宽度改变节点，或当前宽度大于宽度改变节点的宽度
			newWidth = 0
			for pyNode in self :								# 则，需要重新找出宽度最大的节点
				newWidth = max( newWidth, pyNode.right )
			if newWidth == currWidth : return					# 如果最大宽度节点仍然不变，则意味着板面宽度不用改变
			Control._setWidth( self, newWidth )					# 如果宽度改变了，则更新板面宽度
			if pyOwner : pyOwner.onSubNodesWidthChanged__()		# 则，通知父节点，宽度改变
		elif currWidth == pyNode.right :						# 如果当前宽度与宽度改变节点的宽度一样，则板面宽度不变
			return
		else :
			newWidth = pyNode.right								# 新宽度默认为宽度改变的节点的宽度
			Control._setWidth( self, newWidth )					# 则将宽度变大
			if pyOwner : pyOwner.onSubNodesWidthChanged__()		# 通知父节点，宽度改变


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def adds( self, pyNodes ) :
		"""
		添加一组节点
		"""
		for pyNode in pyNodes :
			self.add( pyNode )

	def add( self, pyNode ) :
		"""
		添加节点
		"""
		if not self.__pasteNode( pyNode ) : return					# 如果粘贴节点不成功，则返回
		self.__attachSubNode( pyNode )							# 绑定节点属性

		if self.pyLast is not None :								# 如果添加之前已经有节点
			self.pyLast.setNextNode__( pyNode )						# 则将之前的最后一个节点的后接节点设置为新的节点
		pyNode.setForeNode__( self.pyLast )							# 将新节点的前接节点设置为之前最后一个节点
		pyNode.setNextNode__( None )								# 并将新节点的后接节点设置为 None
		self.__pyNodes.append( pyNode )								# 添加到内部列表
		self.__layoutNodes( pyNode )								# 重新排列新添加的节点
		self.onNodeWidthChanged__( pyNode )							# 通知板面宽度可能要改变
		self.pyOwner.onSubNodeAddSubNode__( pyNode )				# 向所属节点触发添加子节点回调

	def insert( self, index, pyNode ) :
		"""
		插入一个节点
		"""
		if index >= self.count :									# 如果插入位置大于元素个数
			self.add( pyNode )										# 则，等于在尾部添加
			return
		if index < 0 :
			index = max( 0, self.count + index ) 					# 如果是负索引，则转换为正索引

		if pyNode in self and \
			index == self.__pyNodes.index( pyNode ) :				# 如果要插入的节点已经在列表中，并且在同一个位置
				return												# 则返回
		pyNNode = self[index]										# 获取插入索引处的节点
		if not self.__pasteNode( pyNode ) : return					# 粘贴节点，失败则返回
		self.__attachSubNode( pyNode )							# 绑定插入节点属性
		index = self.__pyNodes.index( pyNNode )						# 获取要插入处的索引（注意：有可能要插入的节点已经在列表中，
																	# 因此写这个不是多余的。如果是这样的话，在 pastNode 的时候
																	# 要插入的节点已经从列表中删除，这样，索引就变更了，得重新获取索引）
		pyFore = pyNNode.pyFore										# 检查插入位置前的节点是否存在
		if pyFore is not None :										# 如果存在
			pyFore.setNextNode__( pyNode )							# 则将它的后接节点设置为新节点
		pyNode.setForeNode__( pyFore )								# 将新节点的前接节点设置为插入索引的前节点
		pyNode.setNextNode__( pyNNode )								# 将新插入节点的后接节点设置为插入索引处的原节点
		pyNNode.setForeNode__( pyNode )								# 插入索引出的原节点的前接节点设置为新节点
		self.__pyNodes.insert( index, pyNode )						# 将新节点插入到内部列表
		self.__layoutNodes( pyNode )								# 重排节点位置
		self.onNodeWidthChanged__( pyNode )							# 通知板面宽度可能要改变
		self.pyOwner.onSubNodeAddSubNode__( pyNode )				# 向所属节点触发添加子节点回调

	def remove( self, pyNode ) :
		"""
		删除一个节点
		"""
		if pyNode not in self :
			ERROR_MSG( "%s is not in my list!" % str( pyNode ) )
			return													# 首先判断删除的节点是否存在

		pyFore = pyNode.pyFore										# 获取前接节点
		pyNext = pyNode.pyNext										# 获取后接节点
		if pyFore is not None :										# 如果前接节点存在
			pyFore.setNextNode__( pyNext )							# 则将前接节点的后接节点设置为新的后接节点
		if pyNext is not None :										# 如果原后接节点存在
			pyNext.setForeNode__( pyFore )							# 则将后接节点的前接节点设置为新的前接节点
		self.delPyChild( pyNode )									# UI 上删除之
		self.__pyNodes.remove( pyNode )								# 列表上删除之
		self.__detachSubNode( pyNode )							# 解除属性绑定
		self.__layoutNodes( pyNext )								# 重新排列节点
		self.onNodeWidthChanged__()									# 通知板面宽度可能要改变
		if self.pyOwner :											# 如果父节点存在
			self.pyOwner.onSubNodeRemoveSubNode__( pyNode )			# 则，向所属节点告知删除节点

	def clear( self ) :
		"""
		清除所有节点
		"""
		for idx in xrange( self.count - 1, -1, -1 ) :
			self.remove( self.__pyNodes[idx] )
		self.onNodeWidthChanged__()									# 通知板面，宽度可能要改变
		Control._setHeight( self, 0 )

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		按条件重新排列节点位置
		@type				cmp		: functor
		@param				cmp		: cmp(x, y) -> -1, 0, 1
		@type				key		: functor
		@param				key		: lambda x : x.XXX
		@type				reverse : bool
		@param				reverse : 是否反向
		@return						: None
		"""
		if self.count < 2 : return
		top = self.__pyNodes[0].top
		self.__pyNodes.sort( cmp, key, reverse )
		pyFore = self.__pyNodes[0]
		pyFore.setForeNode__( None )
		pyFore._setTop( top )
		for idx in xrange( 1, self.count ) :
			pyNode = self.__pyNodes[idx]
			pyNode._setTop( pyFore.bottom )
			pyFore.setNextNode__( pyNode )
			pyNode.setForeNode__( pyFore )
			pyFore = pyNode
		self.__pyNodes[-1].setNextNode__( None )


	# ----------------------------------------------------------------
	# friend methods of treeview or treenode
	# ----------------------------------------------------------------
	def setTreeView__( self, pyTreeView ) :
		if pyTreeView is None :
			self.__pyTreeView = None
		else :
			self.__pyTreeView = weakref.ref( pyTreeView )
		for pyNode in self :
			pyNode.setTreeView__( pyTreeView )

	def toggleRightClickSelect__( self, value ) :
		self.__rightClickSelect = value
		for pyNode in self :
			pyNode.toggleRightClickSelect__( value )

	# ---------------------------------------
	def getNodeOffset__( self ) :
		return self.__nodeOffset

	def setNodeOffset__( self, offset ) :
		self.__nodeOffset = offset
		for pyNode in self :
			pyNode.nodeOffset = offset

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTreeView( self ) :
		if self.__pyTreeView is None :
			return None
		return self.__pyTreeView()

	def _getOwner( self ) :
		if self.__pyOwner is None :
			return None
		return self.__pyOwner()

	# -------------------------------------------------
	def _getCount( self ) :
		return len( self.__pyNodes )

	# -------------------------------------------------
	def _getExtendedNodes( self ) :
		return [pyNode for pyNode in self if pyNode.isExtended]

	# ---------------------------------------
	def _getPyFirst( self ) :
		if self.count > 0 :
			return self[0]
		return None

	# ---------------------------------------
	def _getPyLast( self ) :
		if self.count > 0 :
			return self[-1]
		return None


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyTreeView = property( _getTreeView )			# 获取树视图
	pyOwner = property( _getOwner )					# 获取子节点板面所属的节点（如果是顶层节点集合，则它等于 pyTeeView）
	count = property( _getCount )					# 节点数量
	pyExtendedNodes = property( _getExtendedNodes )	# 获取所有展开的节点
	pyFirst = property( _getPyFirst )				# 第一个节点
	pyLast = property( _getPyLast )					# 最后一个节点

	left = property( Control._getLeft )				# 设置左距为只读
	center = property( Control._getCenter )			# 设置水平中距为只读
	right = property( Control._getRight )			# 设置右距为只读
	top = property( Control._getTop )				# 设置顶距为只读
	middle = property( Control._getMiddle )			# 设置垂直中距为只读
	bottom = property( Control._getBottom )			# 设置底距为只读
	width = property( Control._getWidth )			# 将宽度设置为只读
	height = property( Control._getHeight )			# 将高度设置为只读
	size = property( Control._getSize )				# 将大小设置为只读


# --------------------------------------------------------------------
# implement tree node panel
"""
composing :
	-- nodePanel ( GUI.Window )
		-- plusMinus ( GUI.Simple ) -- optional
		-- node ( GUI.TextureFrame )
			-- icon ( GUI.Texture )
			-- lbText ( GUI.Text )
		-- nodesPanel ( GUI.Window )
			treeNode ( 递归 )
"""
# --------------------------------------------------------------------
class TreeNode( Control ) :
	"""
	树节点（包括子节点板面）
	"""
	# ----------------------------------------------------------------
	# 不包括子节点板面的节点
	# ----------------------------------------------------------------
	class Node( Control ) :
		__cc_edge_width = 8.0

		def __init__( self, node, pyBinder ) :
			Control.__init__( self, node, pyBinder )
			self.focus = True									# 可被点击
			self.crossFocus = True								# 可接收鼠标进入消息
			self.__pyText = StaticText( node.sText )			# 节点文本
			self.__icon = node.elements["icon"]
			self.__autoWidth = True								# 是否自适应文本宽度
			self.__orignWidth = node.width						# 节点的原始宽度
			self.icon = ""										# 默认没有图标

		def __del__( self ) :
			if Debug.output_del_TreeView :
				INFO_MSG( str( self ) )


		# ---------------------------------------------
		# protected
		# ---------------------------------------------
		def resetNodeWidth_( self ) :
			"""
			获取节点宽度
			"""
			if self.__autoWidth :
				width = self.__pyText.right + self.__cc_edge_width
				Control._setWidth( self, width )
				self.pyBinder.onSubNodesWidthChanged__()
			elif self.__orignWidth != self.width :
				Control._setWidth( self, self.__orignWidth )
				self.pyBinder.onSubNodesWidthChanged__()

		# -----------------------------------
		def onLMouseDown_( self, mods ) :
			return self.pyBinder.onLMouseDown__( mods )

		def onLMouseUp_( self, mods ) :
			return self.pyBinder.onLMouseUp__( mods )

		def onRMouseDown_( self, mods ) :
			return self.pyBinder.onRMouseDown__( mods )

		def onRMouseUp_( self, mods ) :
			return self.pyBinder.onRMouseUp__( mods )

		# -----------------------------------
		def onLClick_( self, mods ) :
			self.pyBinder.onLClick__( mods )
			return True

		def onRClick_( self, mods ) :
			return self.pyBinder.onRClick__( mods )

		def onLDBClick_( self, mods ) :
			return self.pyBinder.onLDBClick__( mods )

		# -----------------------------------
		def onMouseEnter_( self ) :
			res = self.pyBinder.onMouseEnter__()
			if self.pyBinder.trueText != "":
				toolbox.infoTip.showToolTips( self, self.pyBinder.trueText )
#				FullText.show( self, self.__pyText )
			return res

		def onMouseLeave_( self ) :
			return self.pyBinder.onMouseLeave__()

		def onMouseMove_( self, dx, dy ) :
			return self.pyBinder.onMouseMove__( dx, dy )

		# -----------------------------------
		def onDragStart_( self, pyDragged ) :
			Control.onDragStart_( self, pyDragged )
			return self.pyBinder.onDragStart__( pyDragged )

		def onDragStop_( self, pyDragged ) :
			return self.pyBinder.onDragStop__( pyDragged )

		def onDrop_( self, pyTarget, pyDropped ) :
			Control.onDrop_( self, pyTarget, pyDropped )
			return self.pyBinder.onDrop__( pyTarget, pyDropped )

		def onDragEnter_( self, pyTarget, pyDragged ) :
			return self.pyBinder.onDragEnter__( pyTarget, pyDragged )

		def onDragLeave_( self, pyTarget, pyDragged ) :
			return self.pyBinder.onDragLeave__( pyTarget, pyDragged )

		# ---------------------------------------------
		# property methods
		# ---------------------------------------------
		def _getText( self ) :
			return self.__pyText.text

		def _setText( self, text ) :
			self.__pyText.text = text
			self.resetNodeWidth_()

		# -----------------------------------
		def _getFont( self ) :
			return self.__pyText.font

		def _setFont( self, font ) :
			self.__pyText.font = font
			self.resetNodeWidth_()

		# -----------------------------------
		def _getForeColor( self ) :
			return self.__pyText.color

		def _setForeColor( self, color ) :
			self.__pyText.color = color

		def _getBackColor( self ) :
			return self.color

		def _setBackColor( self, color ) :
			self.color = color

		# -----------------------------------
		def _getIcon( self ) :
			return self.__icon.texture

		def _setIcon( self, icon ) :
			if icon == "" or icon is None or \
				( type( icon ) is tuple and icon[0] == "" ) :
					self.__icon.visible = False
					self.__pyText.left = s_util.getFElemLeft( self.__icon ) + 2
			else :
				self.__icon.visible = True
				self.__pyText.left = s_util.getFElemRight( self.__icon ) + 2
			self.__icon.texture = icon

		# -----------------------------------
		def _getAutoWidth( self ) :
			return self.__autoWidth

		def _setAutoWidth( self, autoWidth ) :
			self.__autoWidth = autoWidth
			self.resetNodeWidth_()
		
		def _getFontSize( self ):
			return self.__pyText.fontSize
		
		def _setFontSize( self, fontSize ):
			self.__pyText.fontSize = fontSize
			self.resetNodeWidth_()

		def _getLimning( self ):
			return self.__pyText.limning
		
		def _setLimning( self, limning ):
			 self.__pyText.limning = limning
			
		def _getLimnColor( self ):
			return self.__pyText.limnColor
		
		def _setLimnColor( self, limnColor ):
			 self.__pyText.limnColor = limnColor
		
		# ---------------------------------------------
		# properties
		# ---------------------------------------------
		text = property( _getText, _setText )								# 获取/设置文本
		font = property( _getFont, _setFont )								# 获取/设置文本字体
		foreColor = property( _getForeColor, _setForeColor )				# 获取/设置前景色
		backColor = property( _getBackColor, _setBackColor )				# 获取/设置背景色
		icon = property( _getIcon, _setIcon )								# 获取/设置图标：( 路径, mapping )
		autoWidth = property( _getAutoWidth, _setAutoWidth )				# 节点宽度是否自适应文本宽度
		fontSize = property( _getFontSize, _setFontSize )
		limning = property( _getLimning, _setLimning )				# MACRO DEFINATION: 获取/设置描边效果：Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
		limnColor = property( _getLimnColor, _setLimnColor )		# tuple: 获取/设置描边颜色

	# ----------------------------------------------------------------
	# tree node including sub node
	# ----------------------------------------------------------------
	def __init__( self, tNode = None, pyBinder = None ) :
		if tNode is None :
			tNode = hfUILoader.load( "guis/controls/treeview/node.gui" )
		Control.__init__( self, tNode, pyBinder )
		self.__pyTreeView = None								# 所属的树视图
		self.__pyParentNode = None								# 所属的父节点

		self.__selectable = True								# 节点是否可以被选中
		self.__selected = False									# 当前是否处于选中状态
		self.__isExtended = False								# 当前是否处于展开状态
		self.__canBeHighlight = True							# 是否允许高亮（鼠标进入时）
		self.__rightClickSelect = False							# 是否允许右键点击选中
		self.__showPlusMinus = True								# 是否显示加减号

		self.__pyFore = None									# 前一个兄弟节点
		self.__pyNext = None									# 后一个兄弟节点
		
		self.__viewTextNum = -1								# 显示多少个字符，超出用...代替，默认全部显示
		self.__trueText = ""								# 悬浮框要显示的字符

		self.__initialize( tNode )								# 初始化节点
		self.showPlusMinus = self.__pyPlusMinus.rvisible		# 是否显示加减号，某人跟 load 给出的引擎 UI 的加减号的可见性一致

	def subclass( self, tNode ) :
		Control.subclass( self, tNode )
		self.__initialize( tNode )
		return self

	def dispose( self ) :
		if self.pyParentNode :									# 手动释放之前，判断是否有父节点
			self.pyParentNode.pyNodes.remove( self )			# 如果有，则首先从父节点中清理
		Control.dispose( self )

	def __del__( self ) :
		if Debug.output_del_TreeView :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, tNode ) :
		if tNode is None : return
		self.pyNode_ = self.Node( tNode.node, self )												# 不包含子节点的节点
		self.pySubNodes_ = Nodes( tNode.nodesPanel, self, self.pyTreeView )							# 所有子节点列表

		self.__pyPlusMinus = Icon( tNode.plusMinus )												# 加减号
		self.__pyPlusMinus.focus = True																# 加减号允许点击
		self.__pyPlusMinus.onLMouseDown.bind( self.__toggleExtended )								# 绑定加减号的点击事件
		size = self.__pyPlusMinus.size																# 加减号的大小
		self.__plusMapping = util.getStateMapping( size, UIState.MODE_R1C2, UIState.MODE_R1C1 )		# 加号 mapping
		self.__minusMapping = util.getStateMapping( size, UIState.MODE_R1C2, UIState.MODE_R1C2 )	# 减号 mapping
		self.__pyPlusMinus.mapping = self.__minusMapping											# 默认显示为减号

		self.__mappings = {}																		# 节点状态 napping
		size = self.pyNode_.size
		self.__mappings[UIState.COMMON] = util.getStateMapping( size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__mappings[UIState.HIGHLIGHT] = util.getStateMapping( size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__mappings[UIState.SELECTED] = util.getStateMapping( size, UIState.MODE_R3C1, UIState.ST_R3C1 )

		self.foreColors_ = {}																		# 节点状态前景色
		self.foreColors_[UIState.COMMON] = self.pyNode_.foreColor
		self.foreColors_[UIState.HIGHLIGHT] = ( 40, 23, 250, 255 )
		self.foreColors_[UIState.SELECTED] = ( 0, 255, 0, 255 )

		self.backColors_ = {}																		# 节点状态背景色
		self.backColors_[UIState.COMMON] = self.pyNode_.backColor
		self.backColors_[UIState.HIGHLIGHT] = self.backColors_[UIState.COMMON]
		self.backColors_[UIState.SELECTED] = self.backColors_[UIState.COMMON]

		Control._setSize( self, ( self.pyNode_.right, self.pySubNodes_.top) )

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Control.generateEvents_( self )
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )		# 当节点被选中状态改变时触发
		self.__onBeforeExtend = self.createEvent_( "onBeforeExtend" )		# 当节点将要展开时被触发
		self.__onBeforeCollapse = self.createEvent_( "onBeforeCollapse" )	# 当节点将要合拢时被触发
		self.__onExtended = self.createEvent_( "onExtended" )				# 当节点展开时触发
		self.__onCollapsed = self.createEvent_( "onCollapsed" )				# 当节点合拢时触发
		self.__onSubNodeAdded = self.createEvent_( "onSubNodeAdded" )		# 当添加一个子节点时被触发
		self.__onSubNodeRemoved = self.createEvent_( "onSubNodeRemoved" )	# 当删除一个子节点时被触发

	# -------------------------------------------------
	@property
	def onSelectChanged( self ) :
		"""
		当节点被选中时触发
		"""
		return self.__onSelectChanged

	# ---------------------------------------
	@property
	def onBeforeExtend( self ) :
		"""
		当节点将要展开时被触发
		"""
		return self.__onBeforeExtend

	@property
	def onBeforeCollapse( self ) :
		"""
		当节点将要合拢时被触发
		"""
		return self.__onBeforeCollapse

	@property
	def onExtended( self ) :
		"""
		当节点展开时触发
		"""
		return self.__onExtended

	@property
	def onCollapsed( self ) :
		"""
		当节点合拢时触发
		"""
		return self.__onCollapsed

	# ---------------------------------------
	@property
	def onSubNodeAdded( self ) :
		"""
		当添加一个子节点时被触发
		"""
		return self.__onSubNodeAdded

	@property
	def onSubNodeRemoved( self ) :
		"""
		当删除一个子节点时被触发
		"""
		return self.__onSubNodeRemoved


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ) :
		"""
		选中节点
		"""
		self.setState( UIState.SELECTED )					# 设置为选中状态
		self.__selected = True								# 设置选中属性为 True
		if self.pyTreeView :								# 如果所属树视图不为 None
			self.pyTreeView.onNodeSelected__( self )		# 告知树视图节点被选中
		self.onSelectChanged( True )						# 触发节点选中事件

	def __deselect( self ) :
		"""
		取消节点的选中状态
		"""
		self.__selected = False								# 取消选中属性
		self.setState( UIState.COMMON )						# 设置为普通状态
		if self.pyTreeView is not None :					# 如果存在所属树视图
			self.pyTreeView.onNodeDeselected__( self )		# 则，告知某节点取消选中
		self.onSelectChanged( False )						# 触发取消选中事件

	# ---------------------------------------
	def __toggleExtended( self ) :
		"""
		改变展开/折叠状态
		"""
		if self.__isExtended : self.collapse()
		else : self.extend()

	def __setPlusMinusState( self ) :
		"""
		设置加减号状态
		"""
		if self.pyNodes.count or getattr( self.pyTreeView, "wspon", False ) :
			if self.isExtended :
				self.__pyPlusMinus.mapping = self.__minusMapping
			else :
				self.__pyPlusMinus.mapping = self.__plusMapping
		else :
			self.__pyPlusMinus.mapping = self.__minusMapping


	# ----------------------------------------------------------------
	# friend methods of nodes
	# ----------------------------------------------------------------
	def setTreeView__( self, pyTreeView ) :
		"""
		重新设置所属树视图
		"""
		if pyTreeView is None :
			self.__pyTreeView = None
		else :
			self.__pyTreeView = weakref.ref( pyTreeView )
		self.__setPlusMinusState()
		self.pySubNodes_.setTreeView__( pyTreeView )

	def setParentNode__( self, pyParent ) :
		"""
		设置所属父节点
		"""
		if pyParent is None :
			self.__pyParentNode = None
		else :
			self.__pyParentNode = weakref.ref( pyParent )

	# ---------------------------------------
	def toggleRightClickSelect__( self, value ) :
		"""
		设置是否右键点击选中节点
		"""
		self.__rightClickSelect = value
		self.pySubNodes_.toggleRightClickSelect__( value )

	# -------------------------------------------------
	def onSubNodeExtended__( self, pyNode, pyExtendedNode ) :
		"""
		当某个子节点展开时被调用
		"""
		if self.isExtended :
			Control._setHeight( self, self.pySubNodes_.bottom )
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeExtended__( self, pyExtendedNode )		# 告诉父节点板面有子节点展开

	def onSubNodeCollapsed__( self, pyNode, pyCollapsedNode ) :
		"""
		当某个子节点或子节点的孙节点合拢时被调用
		"""
		if self.isExtended :
			Control._setHeight( self, self.pySubNodes_.bottom )
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeCollapsed__( self, pyCollapsedNode )	# 告诉父节点板面有子节点合龙

	# ---------------------------------------
	def onSubNodeAddSubNode__( self, pyNode ) :
		"""
		当某个子节点添加子节点时本调用
		"""
		if self.isExtended :
			Control._setHeight( self, self.pySubNodes_.bottom )
		self.__setPlusMinusState()
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeAddSubNode__( self )
		self.onSubNodeAdded()

	def onSubNodeRemoveSubNode__( self, pyNode ) :
		"""
		当某个子节点删除子节点时被调用
		"""
		if self.isExtended :
			Control._setHeight( self, self.pySubNodes_.bottom )
		self.__setPlusMinusState()
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeRemoveSubNode__( self )
		self.onSubNodeRemoved()

	# ---------------------------------------
	def onSubNodesWidthChanged__( self ) :
		"""
		所有节点宽度改变时被调用
		"""
		width = self.pyNode_.right
		if self.__isExtended :											# 如果节点出于展开状态
			width = max( width, self.pySubNodes_.right )				# 则板面宽度等于节点宽度与子节点板面宽度中较大者
		if self.width == width : return									# 如果字节的板面宽度与本节点板面宽度一至，则不需要更改宽度
		Control._setWidth( self, width )								# 重新设置板面宽度
		if self.pyParentNode :											# 如果存在父节点
			self.pyParentNode.pyNodes.onNodeWidthChanged__( self )		# 则通知父节点的子节点板面某节点宽度改变

	# -------------------------------------------------
	def setForeNode__( self, pyNode ) :
		"""
		设置前置兄弟节点
		"""
		if pyNode is None :
			self.__pyFore = None
		else :
			self.__pyFore = weakref.ref( pyNode )

	def setNextNode__( self, pyNode ) :
		"""
		设置后置兄弟节点
		"""
		if pyNode is None :
			self.__pyNext = None
		else :
			self.__pyNext = weakref.ref( pyNode )

	def detach__( self ) :
		"""
		本节点或本节点的父节点被移除
		"""
		if self.selected :
			self.selected = False						# 取消选中状态
		self.__pyTreeView = None						# 取消所属的树视图绑定
		for pyNode in self.pyNodes :
			pyNode.detach__()							# 通知所有子节点 detach


	# -------------------------------------------------
	# friend methods of inner node
	# -------------------------------------------------
	def onLMouseDown__( self, mods ) :
		"""
		鼠标左键在节点上按下
		"""
		return Control.onLMouseDown_( self, mods )

	def onLMouseUp__( self, mods ) :
		"""
		鼠标左键在节点上提起
		"""
		return Control.onLMouseUp_( self, mods )

	def onRMouseDown__( self, mods ) :
		"""
		鼠标右键在节点上按下
		"""
		return Control.onRMouseDown_( self, mods )

	def onRMouseUp__( self, mods ) :
		"""
		鼠标右键在节点上提起
		"""
		return Control.onRMouseUp_( self, mods )

	# ---------------------------------------
	def onLClick__( self, mods ) :
		"""
		鼠标左键点击
		"""
		self.selected = True
		Control.onLClick_( self, mods )
		if self.pyTreeView :
			self.pyTreeView.onTreeNodeLClick( self )
		return True

	def onRClick__( self, mods ) :
		"""
		鼠标右键点击
		"""
		if self.__rightClickSelect :
			self.selected = True
		Control.onRClick_( self, mods )
		if self.pyTreeView :
			self.pyTreeView.onTreeNodeRClick( self )
		return True

	def onLDBClick__( self, mods ) :
		"""
		鼠标双击
		"""
		self.__toggleExtended()
		Control.onLDBClick_( self, mods )
		return True

	def onMouseEnter__( self ) :
		"""
		鼠标进入
		"""
		if self.canBeHighlight :
			self.setState( UIState.HIGHLIGHT )
		Control.onMouseEnter_( self )
		return True

	def onMouseLeave__( self ) :
		"""
		鼠标离开
		"""
		if not self.canBeHighlight : return
		if self.__selected :
			self.setState( UIState.SELECTED )
		else :
			self.setState( UIState.COMMON )
		toolbox.infoTip.hide()
#		FullText.hide()
		Control.onMouseLeave_( self )
		return True

	def onMouseMove__( self, dx, dy ) :
		"""
		鼠标移动
		"""
		return Control.onMouseMove_( self, dx, dy )

	# ---------------------------------------
	def onDragStart__( self, pyDragged ) :
		"""
		开始拖起
		"""
		self.onDragStart()
		return True

	def onDragStop__( self, pyDragged ) :
		"""
		拖放结束
		"""
		return Control.onDragStop_( self, pyDragged.pyBinder )

	def onDrop__( self, pyTarget, pyDropped ) :
		"""
		放下
		"""
		return Control.onDrop_( self, self, pyDropped.pyBinder )

	def onDragEnter__( self, pyTarget, pyDragged ) :
		"""
		拖放进入
		"""
		return Control.onDragEnter_( self, self, pyDragged.pyBinder )

	def onDragLeave__( self, pyTarget, pyDragged ) :
		"""
		拖放离开
		"""
		return Control.onDragLeave_( self, self, pyDragged.pyBinder )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		"""
		节点状态改变时被调用
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		设置节点状态
		"""
		if state == UIState.COMMON and self.selected :				# 如果节点被选中
			state = UIState.SELECTED								# 则状态始终是选中状态
		self.pyNode_.mapping = self.__mappings[state]				# 设置状态 mapping
		self.pyNode_.foreColor = self.foreColors_[state]			# 设置状态前景色
		self.pyNode_.backColor = self.backColors_[state]			# 设置状态背景色
		self.onStateChanged_( state )								# 回调保护方法
		if state == UIState.HIGHLIGHT and self.pyTreeView :			# 如果树视图存在
			self.pyTreeView.onNodeHighlight__( self )				# 则通知树视图，有节点状态改变

	# -------------------------------------------------
	def extend( self ) :
		"""
		展开节点
		"""
		if self.__isExtended : return								# 如果已经展开，则返回
		self.onBeforeExtend()										# 触发展开之前事件
		if self.pyTreeView :										# 如果所属的树视图存在
			self.pyTreeView.onSubNodeBeforeExtend__( self )			# 则通知树视图节点将要展开
		self.__isExtended = True									# 设置展开属性为 True
		Control._setHeight( self, self.pySubNodes_.bottom )			# 设置节点高度
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeExtended__( self, self )# 告诉父节点板面有子节点展开
		self.onSubNodesWidthChanged__()								# 告知本节点宽度已改变
		self.__setPlusMinusState()									# 设置加减号状态
		self.onExtended()

	def collapse( self ) :
		"""
		合拢节点
		"""
		if not self.__isExtended : return							# 如果本来就没有展开，则返回
		self.onBeforeCollapse()										# 触发将要合拢事件
		if self.pyTreeView :										# 如果所属的树视图存在
			self.pyTreeView.onSubNodeBeforeCollapse__( self )		# 则通知树视图，将要合拢
		self.__isExtended = False									# 设置展开属性为 False
		Control._setHeight( self, self.pySubNodes_.top )			# 重新设置节点高度( 减去 0.1 的原因是抵消误差)
		self.__setPlusMinusState()									# 设置加减号
		self.onSubNodesWidthChanged__()								# 告知本节点宽度已改变
		self.onCollapsed()											# 触发合拢事件
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeCollapsed__( self, self )	# 告诉父节点板面有子节点合龙

	# -------------------------------------------------
	def hitTest( self, x, y ) :
		"""
		判断指定像素点是否落在节点上
		"""
		return self.pyNode_.hitTest( x, y )

	def isMouseHit( self ) :
		"""
		判断鼠标是否击中节点
		"""
		return self.pyNode_.isMouseHit()

	# -------------------------------------------------
	def showPlusMinusIcon( self ) :
		"""
		显示加减号
		"""
		self.__showPlusMinus = True
		self.__pyPlusMinus.visible = True

	def hidePlusMinusIcon( self ) :
		"""
		隐藏加减号
		"""
		self.__showPlusMinus = False
		self.__pyPlusMinus.visible = False

	# ---------------------------------------
	def showPlusIcon( self ) :
		"""
		如果 self.__showPlusMinus == True，则无条件地显示加号图标
		"""
		self.__pyPlusMinus.mapping = self.__plusMapping

	def showMinusIcon( self ) :
		"""
		如果 self.__showPlusMinus == True，则无条件地显示减号图标
		"""
		self.__pyPlusMinus.mapping = self.__minusMapping


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getFocus( self ) :
		return self.pyNode_.focus

	def _setFocus( self, focus ) :
		self.pyNode_.focus = focus

	# ---------------------------------------
	def _getCrossFocus( self ) :
		return self.pyNode_.crossFocus

	def _setCrossFocus( self, focus ) :
		self.pyNode_.crossFocus = focus

	# ---------------------------------------
	def _getMoveFocus( self ) :
		return self.pyNode_.moveFocus

	def _setMoveFocus( self, focus ) :
		self.pyNode_.moveFocus = focus

	# ---------------------------------------
	def _getDragFocus( self ) :
		return self.pyNode_.dragFocus

	def _setDragFocus( self, focus ) :
		self.pyNode_.dragFocus = focus

	# ---------------------------------------
	def _getDropFocus( self ) :
		return self.pyNode_.dropFocus

	def _setDropFocus( self, focus ) :
		self.pyNode_.dropFocus = focus

	# -------------------------------------------------
	def _getTreeView( self ) :
		if self.__pyTreeView is None :
			return None
		return self.__pyTreeView()

	def _getParentNode( self ) :
		if self.__pyParentNode is None :
			return None
		return self.__pyParentNode()

	# ---------------------------------------
	def _getForeNode( self ) :
		if self.__pyFore is None :
			return None
		return self.__pyFore()

	def _getNextNode( self ) :
		if self.__pyNext is None :
			return None
		return self.__pyNext()

	# -------------------------------------------------
	def _getNodes( self ) :
		return self.pySubNodes_

	# -------------------------------------------------
	def _getText( self ) :
		return self.pyNode_.text

	def _setText( self, text ) :
		uText = csstring.toWideString( text )
		self.__trueText = text
		if self.__viewTextNum > 0  and len( uText ) > self.__viewTextNum:
			uText = "%s..."%uText[:self.__viewTextNum]
			self.__trueText = text
		else:
			self.__trueText = ""
		self.pyNode_.text = uText
		self.onSubNodesWidthChanged__()								# 告知本节点宽度已改变

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyNode_.font

	def _setFont( self, font ) :
		self.pyNode_.font = font
		self.onSubNodesWidthChanged__()								# 告知本节点宽度已改变

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.pyNode_.foreColor

	def _setForeColor( self, color ) :
		self.pyNode_.foreColor = color

	# ---------------------------------------
	def _getBackColor( self ) :
		return self.pyNode_.backColor

	def _setBackColor( self, color ) :
		self.pyNode_.backColor = color

	# ---------------------------------------
	def _getIcon( self ) :
		return self.pyNode_.icon
		self.onSubNodesWidthChanged__()								# 告知本节点宽度已改变

	def _setIcon( self, icon ) :
		self.pyNode_.icon = icon

	# -------------------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.foreColors_[UIState.COMMON] = color

	# ---------------------------------------
	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color

	# ---------------------------------------
	def _getSelectedForeColor( self ) :
		return self.foreColors_[UIState.SELECTED]

	def _setSelectedForeColor( self, color ) :
		self.foreColors_[UIState.SELECTED] = color

	# -------------------------------------------------
	def _getCommonBackColor( self ) :
		return self.backColors_[UIState.COMMON]

	def _setCommonBackColor( self, color ) :
		self.backColors_[UIState.COMMON] = color

	# ---------------------------------------
	def _getHighlightBackColor( self ) :
		return self.backColors_[UIState.HIGHLIGHT]

	def _setHighlightBackColor( self, color ) :
		self.backColors_[UIState.HIGHLIGHT] = color

	# ---------------------------------------
	def _getSelectedBackColor( self ) :
		return self.backColors_[UIState.SELECTED]

	def _setSelectedBackColor( self, color ) :
		self.backColors_[UIState.SELECTED] = color

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, value ) :
		self.__selectable = value

	# ---------------------------------------
	def _getSelected( self ) :
		return self.__selected

	def _setSelected( self, isSel ) :
		if not self.selectable : return
		if isSel == self.__selected : return
		if isSel : self.__select()
		else : self.__deselect()

	# ---------------------------------------
	def _getIsExtended( self ) :
		return self.__isExtended

	# ---------------------------------------
	def _getShowPlusMinus( self ) :
		return self.__showPlusMinus

	def _setShowPlusMinus( self, value ) :
		self.__showPlusMinus = value
		self.__pyPlusMinus.visible = value
		for pyNode in self.pyNodes :
			pyNode.showPlusMinus = value

	# ---------------------------------------
	def _getCanBeHighlight( self ) :
		return self.__canBeHighlight

	def _setCanBeHighlight( self, value ) :
		self.__canBeHighlight = value

	# -------------------------------------------------
	def _getNodeHeight( self ) :
		return self.pyNode_.height

	# ---------------------------------------
	def _getNodeOffset( self ) :
		return self.pySubNodes_.getNodeOffset__()

	def _setNodeOffset( self, offset ) :
		self.pySubNodes_._setLeft( offset )
		self.pySubNodes_.setNodeOffset__( offset )

	# ---------------------------------------
	def _getAutoWidth( self ) :
		return self.pyNode_.autoWidth

	def _setAutoWidth( self, autoWidth ) :
		self.pyNode_.autoWidth = autoWidth
		
	def _getViewTextNum( self ):
		return self.__viewTextNum
		
	def _setViewTextNum( self, viewTextNum ):
		self.__viewTextNum = viewTextNum
		
	def _getTrueText( self ):
		return self.__trueText

	def _getFontSize( self ):
		return self.pyNode_.fontSize
		
	def _setFontSize( self, fontSize ):
		self.pyNode_.fontSize = fontSize
		self.onSubNodesWidthChanged__()
	
	def _getLimning( self ):
		return self.pyNode_.limning
	
	def _setLimning( self, limning ):
		self.pyNode_.limning = limning
	
	def _getLimnColor( self ):
		return self.pyNode_.limnColor
	
	def _setLimnColor( self, limnColor ):
		self.pyNode_.limnColor = limnColor

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	focus = property( _getFocus, _setFocus )										# 获取/设置节点是否接收按键消息
	crossFocus = property( _getCrossFocus, _setCrossFocus )							# 获取/设置节点是否接收鼠标进入消息
	moveFocus = property( _getMoveFocus, _setMoveFocus )							# 获取/设置节点是否接收鼠标移动消息
	dragFocus = property( _getDragFocus, _setDragFocus )							# 获取/设置节点是否接收拖起消息
	dropFocus = property( _getDropFocus, _setDropFocus )							# 获取/设置节点是否接收放下消息

	pyTreeView = property( _getTreeView )											# 获取所属的树视图，没有则为 None
	pyParentNode = property( _getParentNode )										# 获取所属的父节点，没有则为 None
	pyFore = property( _getForeNode )												# 获取前一个兄弟节点，没有则为 None
	pyNext = property( _getNextNode )												# 获取后一个兄弟节点，没有则为 None

	text = property( _getText, _setText )											# 获取/设置节点文本
	font = property( _getFont, _setFont )											# 获取/设置节点文本字体
	foreColor = property( _getForeColor, _setForeColor )							# 获取/设置节点文本前景色
	backColor = property( _getBackColor, _setBackColor )							# 获取/设置节点文本背景色
	icon = property( _getIcon, _setIcon )											# 获取/设置节点图标

	pyNodes = property( _getNodes )													# 获取子节点列表板面

	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )			# 获取/设置普通状态下的前景色
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor )	# 获取/设置高亮状态下的前景色
	selectedForeColor = property( _getSelectedForeColor, _setSelectedForeColor )	# 获取/设置选中状态下的前景色
	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )			# 获取/设置普通状态下的背景色
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor )	# 获取/设置高亮状态下的背景色
	selectedBackColor = property( _getSelectedBackColor, _setSelectedBackColor )	# 获取/设置选中状态下的背景色

	selectable = property( _getSelectable, _setSelectable )							# 获取/设置节点是否可以被选中
	canBeHighlight = property( _getCanBeHighlight, _setCanBeHighlight )				# 获取/设置鼠标进入节点时，是否表现为高亮
	showPlusMinus = property( _getShowPlusMinus, _setShowPlusMinus )				# 获取/设置是否显示加减号

	selected = property( _getSelected, _setSelected )								# 获取/设置节点的选中状态
	isExtended = property( _getIsExtended )											# 获取节点是否处于展开状态

	nodeHeight = property( _getNodeHeight )											# 获取节点高度
	nodeOffset = property( _getNodeOffset, _setNodeOffset )							# 获取/设置节点与其父节点的水平位置偏移
	autoWidth = property( _getAutoWidth, _setAutoWidth )							# 获取/设置节点宽度是否自适应节点文本的宽度

	width = property( Control._getWidth )											# 获取节点宽度
	height = property( Control._getHeight )											# 获取节点高度
	size = property( Control._getSize )												# 获取节点大小
	left = property( Control._getLeft )												# 获取节点左距
	center = property( Control._getCenter )											# 获取节点水平中距
	right = property( Control._getRight )											# 获取节点右距
	top = property( Control._getTop )												# 获取节点顶距
	middle = property( Control._getMiddle )											# 获取节点垂直中距
	bottom = property( Control._getBottom )											# 获取节点底距
	viewTextNum = property( _getViewTextNum, _setViewTextNum )						# 获取/设置可视字符数
	trueText = property( _getTrueText )												# 获取悬浮框要显示的字符
	fontSize = property( _getFontSize, _setFontSize )
	limning = property( _getLimning, _setLimning )				# MACRO DEFINATION: 获取/设置描边效果：Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( _getLimnColor, _setLimnColor )		# tuple: 获取/设置描边颜色

# --------------------------------------------------------------------
# implement treeview contains a horizontal scrollbar and a vertical scroll bar
# --------------------------------------------------------------------
class HVTreeView( TreeViewBase, HVScrollPanel ) :
	def __init__( self, panel, hsbar, vsbar, pyBinder = None ) :
		HVScrollPanel.__init__( self, panel, hsbar, vsbar, pyBinder )
		TreeViewBase.__init__( self, panel )
		self.h_perScroll = 20											# 默认水平上每次滚动条滚动 20 个单位的像素
		self.v_perScroll = 40											# 默认垂直上每次滚动条滚动 40 个单位的像素

	def __del__( self ) :
		HVScrollPanel.__del__( self )
		if Debug.output_del_TreeView :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		HVScrollPanel.generateEvents_( self )
		TreeViewBase.generateEvents_( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onVScroll_( self, value ) :
		"""
		内容随滚动条滚动时被调用
		"""
		HVScrollPanel.onVScroll_( self, value )
		TreeViewBase.onScroll_( self, value )

	# -------------------------------------------------
	def onNodesWidthChanged_( self, width ) :
		"""
		全部节点的宽度改变时被调用
		"""
		self.h_wholeLen = width

	def onModesHeightChanged_( self, height ) :
		"""
		全部节点的高度改变时被调用
		"""
		self.v_wholeLen = height

	def scrollToNode( self, pyNode ) :
		"""
		如果某个节点不可见，则滚动到某个节点处（让某个节点可见）
		"""
		t = pyNode.getTopToUI( self )									# 节点在树视图上的顶距
		subHeight = pyNode.height - pyNode.nodeHeight					# 所有子节点的高度
		b = pyNode.getBottomToUI( self ) - subHeight					# 节点在树视图上的底距
		if t < 0 :														# 如果节点隐藏在树视图上面
			self.v_scroll += t - pyNode.nodeHeight / 2					# 则滚动到，让指定节点刚好在树视图可见的最上面
		elif b > self.height :											# 如果节点隐藏在树视图下面
			self.v_scroll += b - self.height + pyNode.nodeHeight / 2	# 则滚动到，让指定节点刚好在树视图可见的最下面


# --------------------------------------------------------------------
# implement treeview contains only one vertical scroll bar
# --------------------------------------------------------------------
class VTreeView( TreeViewBase, VScrollPanel ) :
	def __init__( self, panel, vsbar, pyBinder = None ) :
		VScrollPanel.__init__( self, panel, vsbar, pyBinder )
		TreeViewBase.__init__( self, panel )
		self.perScroll = 40											# 默认每次滚动条滚动 40 个单位的像素

	def __del__( self ) :
		VScrollPanel.__del__( self )
		if Debug.output_del_TreeView :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		VScrollPanel.generateEvents_( self )
		TreeViewBase.generateEvents_( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onScroll_( self, value ) :
		"""
		内容随滚动条滚动时被调用
		"""
		VScrollPanel.onScroll_( self, value )
		TreeViewBase.onScroll_( self, value )

	# -------------------------------------------------
	def onModesHeightChanged_( self, height ) :
		"""
		全部节点的高度改变时被调用
		"""
		self.wholeLen = height

	def scrollToNode( self, pyNode ) :
		"""
		如果某个节点不可见，则滚动到某个节点处（让某个节点可见）
		"""
		t = pyNode.getTopToUI( self )								# 节点在树视图上的顶距
		subHeight = pyNode.height - pyNode.nodeHeight				# 所有子节点的高度
		b = pyNode.getBottomToUI( self ) - subHeight				# 节点在树视图上的底距
		if t < 0 :													# 如果节点隐藏在树视图上面
			self.scroll += t - pyNode.nodeHeight / 2				# 则滚动到，让指定节点刚好在树视图可见的最上面
		elif b > self.height :										# 如果节点隐藏在树视图下面
			self.scroll += b - self.height + pyNode.nodeHeight / 2	# 则滚动到，让指定节点刚好在树视图可见的最下面