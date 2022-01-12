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
	����ĳ�����ڵ�
	@type				pyNode : TreeNone
	@param				pyNode : Ҫ���������ڵ�
	@type				doFunc : function
	@param				doFunc : callback ����ÿһ���ڵ�ʱ���ú������ᱻ���ã����������һ���������Ա�ʾ��ǰ�������Ľڵ�
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
		self.__pyNodes = Nodes( panel.nodesPanel, self, self )			# �ڵ㼯�ϰ���
		self.__nodeOffset = 0											# �ӽڵ��븸�ڵ��ˮƽλ��ƫ��
		self.__showPlusMinus = True										# �Ƿ���ʾ�Ӽ���
		self.__rightClickSelect = False									# �Ҽ�����ڵ�ʱ���Ƿ�ѡ�нڵ�
		self.__pySelNode = None											# ��ǰѡ�еĽڵ�
		self.__pyHighlightNode = None									# ��ǰ���ڸ���״̬�Ľڵ�
		self.__wspon = False											# �Ƿ���ʾû���ӽڵ�Ľڵ�ġ�������

		self.nodeOffset = 16											# �ڵ�ƫ��Ĭ��Ϊ 16 ������
		self.isExtended = True											# ����ͼĬ����չ����


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		self.__onTreeNodeLClick = self.createEvent_( "onTreeNodeLClick" )					# ��������ĳ���ڵ�ʱ������
		self.__onTreeNodeRClick = self.createEvent_( "onTreeNodeRClick" )					# ���Ҽ����ĳ���ڵ�ʱ������
		self.__onTreeNodeSelected = self.createEvent_( "onTreeNodeSelected" )				# ��ѡ��ĳ���ڵ�ʱ������
		self.__onTreeNodeDeselected = self.createEvent_( "onTreeNodeDeselected" )			# ��ĳ���ڵ�ȡ��ѡ��״̬ʱ������
		self.__onTreeNodeBeforeExtend = self.createEvent_( "onTreeNodeBeforeExtend" )		# ��ĳ���ڵ㽫Ҫչ��ʱ������
		self.__onTreeNodeBeforeCollapse = self.createEvent_( "onTreeNodeBeforeCollapse" )	# ��ĳ���ڵ㽫Ҫ�۵�ʱ������
		self.__onTreeNodeExtended = self.createEvent_( "onTreeNodeExtended" )				# ��ĳ���ڵ�չ��ʱ������
		self.__onTreeNodeCollapsed = self.createEvent_( "onTreeNodeCollapsed" )				# ��ĳ���ڵ��۵�ʱ������
		self.__onTreeNodeAdded = self.createEvent_( "onTreeNodeAdded" )						# �����ĳ���ڵ�ʱ������
		self.__onTreeNodeRemoved = self.createEvent_( "onTreeNodeRemoved" )					# ��ɾ��ĳ���ڵ�ʱ������

	# -------------------------------------------------
	@property
	def onTreeNodeLClick( self ) :
		"""
		��������ĳ���ڵ�ʱ������
		"""
		return self.__onTreeNodeLClick

	@property
	def onTreeNodeRClick( self ) :
		"""
		���Ҽ����ĳ���ڵ�ʱ������
		"""
		return self.__onTreeNodeRClick

	@property
	def onTreeNodeSelected( self ) :
		"""
		��ѡ��ĳ���ڵ�ʱ������
		"""
		return self.__onTreeNodeSelected

	@property
	def onTreeNodeDeselected( self ) :
		"""
		��ĳ���ڵ�ȡ��ѡ��״̬ʱ������
		"""
		return self.__onTreeNodeDeselected

	# ---------------------------------------
	@property
	def onTreeNodeBeforeExtend( self ) :
		"""
		��ĳ���ڵ㽫Ҫչ��ʱ������
		"""
		return self.__onTreeNodeBeforeExtend

	@property
	def onTreeNodeBeforeCollapse( self ) :
		"""
		��ĳ���ڵ㽫Ҫ�۵�ʱ������
		"""
		return self.__onTreeNodeBeforeCollapse

	@property
	def onTreeNodeExtended( self ) :
		"""
		��ĳ���ڵ�չ��ʱ������
		"""
		return self.__onTreeNodeExtended

	@property
	def onTreeNodeCollapsed( self ) :
		"""
		��ĳ���ڵ��۵�ʱ������
		"""
		return self.__onTreeNodeCollapsed

	@property
	def onTreeNodeAdded( self ) :
		"""
		�����ĳ���ڵ�ʱ������
		"""
		return self.__onTreeNodeAdded

	@property
	def onTreeNodeRemoved( self ) :
		"""
		��ɾ��ĳ���ڵ�ʱ������
		"""
		return self.__onTreeNodeRemoved


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onScroll_( self, value ) :
		"""
		���������������ʱ������
		"""
		pyHNode = self.pyHighlightNode
		if pyHNode is not None :
			pyHNode.onMouseLeave__()			# ���ݹ���ʱ���������������ڵ������뿪����

	# -------------------------------------------------
	def onNodesWidthChanged_( self, width ) :
		"""
		ȫ���ڵ�Ŀ�ȸı�ʱ������
		"""
		pass

	def onModesHeightChanged_( self, height ) :
		"""
		ȫ���ڵ�ĸ߶ȸı�ʱ������
		"""
		pass

	# ---------------------------------------
	def scrollToNode( self, pyNode ) :
		"""
		���ĳ���ڵ㲻�ɼ����������ĳ���ڵ㴦����ĳ���ڵ�ɼ���
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def extendAll( self ) :
		"""
		չ�����нڵ�
		"""
		def extendNode( pyNode ) :
			pyNode.extend()
		for pyNode in self.__pyNodes :
			travelTreeNode( pyNode, extendNode )

	def collapseAll( self ) :
		"""
		��£���нڵ�
		"""
		def collapseNode( pyNode ) :
			pyNode.collapse()
		for pyNode in self.__pyNodes :
			travelTreeNode( pyNode, collapseNode )

	# -------------------------------------------------
	def getNodeAt( self, x, y ) :
		"""
		��ȡָ�����������µĽڵ㣬���û���򷵻� None
		"""
		def isNodePoint( pyNode ) :								# �ж�ָ�����Ƿ����ڽڵ���
			if pyNode.hitTest( x, y ) :							# �����
				return True										# �򷵻� True
			return False										# ���򷵻� False

		def isCollapsed( pyNode ) :								# �ж�ָ���ڵ��Ƿ��ں�£״̬
			pyParentNode = pyNode.pyParentNode					# �ڵ�ĸ��ڵ�
			while isinstance( pyParentNode, TreeNode ) :		# �������ڵ�
				if not pyParentNode.isExtended :				# ������κ�һ�����ڵ��Ǻ�£��
					return True									# �򷵻� True����ʾ�ڵ㴦�ں�£״̬
				pyParentNode = pyParentNode.pyParentNode		# ������������ڵ�ĸ��ڵ�
			return False										# ���ȫ����û�д��ں�£״̬���򷵻� False

		queue = Queue()											# ����һ����ʱ����
		queue.enters( self.__pyNodes )							# �����ж���ڵ����
		while queue.length() :									# ��������ͼ��ֱ������Ϊ��
			pyNode = queue.leave()								# ��һ���ڵ����
			collapsed = isCollapsed( pyNode )					# �жϳ��еĽڵ��Ƿ��Ǻ�£��
			if isNodePoint( pyNode ) and not collapsed :		# �ж�ָ���������Ƿ����ڽڵ���
				return pyNode									# ���ָ���������ڽڵ��ϣ����ҽڵ�û�д��ں�£״̬���򷵻ظýڵ�
			if not collapsed and pyNode.isExtended :			# ����ڵ�ĸ��ڵ���չ���ģ����ҽڵ㱾��Ҳ��չ����
				queue.enters( pyNode.pyNodes )					# ��������ڵ���ӽڵ����
		return None												# ָ����������û����Ӧ�Ľڵ�

	def getHitNode( self ) :
		"""
		��ȡ���ָ��λ�ô��Ľڵ㣬�����򷵻�ָ��Ľڵ㣬���򷵻� None
		"""
		x, y = csol.pcursorPosition()
		return self.getNodeAt( x, y )

	# -------------------------------------------------
	def travelAllNodes( self, doFunc ) :
		"""
		���������ӽڵ�
		@type				doFunc : function
		@param				doFunc : callback ����ÿһ���ڵ�ʱ���ú������ᱻ���ã����������һ���������Ա�ʾ��ǰ�������Ľڵ�
		@rtype					   : bool
		@param					   : ����ҵ����򷵻� True�����û�ҵ����򷵻� False
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
		��ĳ���ӽڵ㽫Ҫչ��ʱ������
		"""
		self.onTreeNodeBeforeExtend( pyNode )

	def onSubNodeBeforeCollapse__( self, pyNode ) :
		"""
		��ĳ���ӽڵ㽫Ҫչ��ʱ������
		"""
		self.onTreeNodeBeforeCollapse( pyNode )

	# ---------------------------------------
	def onSubNodeExtended__( self, pyNode, pyExtendedNode ) :
		"""
		ĳ���ӽڵ�չ���򱻵���
		"""
		self.onModesHeightChanged_( self.__pyNodes.height )	# �ڵ����߶ȸı�
		self.onTreeNodeExtended( pyExtendedNode )			# �����ڵ�չ���¼�

	def onSubNodeCollapsed__( self, pyNode, pyCollapsedNode ) :
		"""
		ĳ���ӽڵ��£ʱ������
		"""
		self.onModesHeightChanged_( self.__pyNodes.height )	# �ڵ����߶ȸı�
		self.onTreeNodeCollapsed( pyCollapsedNode )			# �����ڵ��£�¼�

	# ---------------------------------------
	def onSubNodeAddSubNode__( self, pyNode ) :
		"""
		ĳ���ӽڵ�����ӽڵ�ʱ������
		"""
		self.onModesHeightChanged_( self.__pyNodes.height )	# �ڵ����߶ȸı�
		self.onTreeNodeAdded( pyNode )						# ������ӽڵ��¼�

	def onSubNodeRemoveSubNode__( self, pyNode ) :
		"""
		ĳ���ڵ�ɾ���ӽڵ�ʱ������
		"""
		if self.__pySelNode == pyNode :						# �����ǰѡ�еĽڵ��Ǳ�ɾ���ڵ�
			self.__pySelNode = None							# �����ñ�ѡ�нڵ�Ϊ None
		self.onModesHeightChanged_( self.__pyNodes.height )	# �ڵ����߶ȸı�
		self.onTreeNodeRemoved( pyNode )					# ����ɾ���ڵ��¼�

	#----------------------------------------
	def onSubNodesWidthChanged__( self ) :
		"""
		���нڵ��ȸı�ʱ������
		"""
		self.onNodesWidthChanged_( self.__pyNodes.right )	# �ڵ�����ȸı�

	#----------------------------------------
	def onNodeSelected__( self, pyNode ) :
		"""
		��ĳ���ڵ�ѡ��ʱ������
		"""
		if pyNode == self.__pySelNode : return				# ����ڵ��Ѿ���ѡ�У��򷵻�
		if self.__pySelNode is not None :					# ���֮ǰ��ѡ�еĽڵ�
			self.__pySelNode.selected = False				# ��֮ǰѡ�еĽڵ�����Ϊû�б�ѡ��
		self.__pySelNode = pyNode							# �������õ�ǰ��ѡ�еĽڵ�
		self.onNodeHighlight__( pyNode )					# ������ʾ��ѡ�еĽڵ�
		self.onTreeNodeSelected( pyNode )					# �����ڵ�ѡ���¼�

	def onNodeDeselected__( self, pyNode ) :
		"""
		�ڵ�ȡ��ѡ��ʱ������
		"""
		self.__pySelNode = None								# ���õ�ǰѡ�еĽڵ�Ϊ None
		self.onTreeNodeDeselected( pyNode )					# �����ڵ�ȡ��ѡ���¼�

	# ---------------------------------------
	def onNodeHighlight__( self, pyNode ) :
		"""
		��Ҫĳ���ڵ������ʾʱ������
		"""
		pyHNode = self.pyHighlightNode						# ֮ǰ������ʾ�Ľڵ�
		if pyNode == pyHNode : return						# �����֮ǰ�Ľڵ�һ�£��򷵻�
		if pyHNode : pyHNode.setState( UIState.COMMON )		# ���֮ǰ�и�����ʾ�Ľڵ㣬��֮ǰ�ĸ����ڵ�������ͨ״̬
		if pyNode is None :
			self.__pyHighlightNode = None
		else :
			self.__pyHighlightNode = weakref.ref( pyNode )	# ���������µĸ����ڵ�


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
	pyParentNode = property( _getParentNode )							# ���ڵ㣬ʼ�շ��� None
	pyNodes = property( _getNodes )										# Nones���ڵ����ͬʱҲʱ�ڵ㼯��
	nodeOffset = property( _getNodeOffset, _setNodeOffset )				# �ڵ��븸�ڵ��ˮƽƫ��
	pySelNode = property( _getPySelNode, _setPySelNode )				# ��ǰ��ѡ�еĽڵ�
	pyHighlightNode = property( _getHighlightNode )						# ��ǰ���ڸ���״̬�İ�ť
	showPlusMinus = property( _getShowPlusMinus, _setShowPlusMinus )	# �Ƿ���ʾ�Ӽ���
	rightClickSelect = property( _getRCSelect, _setRCSelect )			# �Ƿ�����Ϊ�Ҽ����ѡ��
	wspon = property( _getWspon, _setWspon )							# �Ƿ���ʾû���ӽڵ�Ľڵ�ġ�+���ţ�whether show plus of the node which has no sub nodes��
																		# Ҳ����˵�����ĳ���ڵ㼴ʹ��û���ӽڵ㣬���䴦���۵�״̬ʱ��Ҳ����ʾǰ��ļӺ�


# --------------------------------------------------------------------
# implement tree nodes panel
# --------------------------------------------------------------------
class Nodes( Control ) :
	def __init__( self, panel = None, pyOwner = None, pyTreeView = None ) :
		Control.__init__( self, panel )
		self.__pyTreeView = None
		self.__pyOwner = None
		self.__initialize( panel, pyOwner, pyTreeView )					# ��ʼ��
		self.__pyNodes = []												# ���нڵ��б�
		

		self.__nodeOffset = 0											# �ڵ��븸�ڵ��ˮƽƫ��
		self.__rightClickSelect = False									# �Ƿ��Ҽ����ѡ�нڵ�

	def subclass( self, panel, pyOwner, pyTreeView ) :
		Control.subclass( self, panel )
		self.__initialize( panel, pyOwner, pyTreeView )
		return self

	def __del__( self ) :
		self.clear()											# ������нڵ㣨ע�⣺���� dispose ���нڵ㣬��Ϊ�ⲿ���ܻ������������ǣ�
		Control.__del__( self )
		if Debug.output_del_TreeView :
			INFO_MSG( "TreeNodes<%i>" % id( self ) )

	# ---------------------------------------
	def __initialize( self, panel, pyOwner, pyTreeView ) :
		if panel is None : return
		if pyTreeView :
			self.__pyTreeView = weakref.ref( pyTreeView )		# ����������ͼ
		if pyOwner :
			self.__pyOwner = weakref.ref( pyOwner )				# �����ĸ��ڵ㣨����Ƕ����б�������������������ͼ��
		Control._setSize( self, ( 0, 0 ) )						# Ĭ��û���κνڵ㣬���Ը߶�Ĭ��Ϊ 0


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
		����ָ���ڵ��λ��
		"""
		pyFore = pyNode.pyFore								# ָ���ڵ��ǰһ���ڵ�
		if pyFore is None : pyNode._setTop( 0 )				# ���ָ���ڵ��ǵ�һ���ڵ㣬�򽫶�������Ϊ 0
		else : pyNode._setTop( pyFore.bottom )				# ���򣬽�ָ���ڵ�Ķ�������Ϊ��ǰ��һ���ڵ�ĵ׾�
		pyNode._setLeft( 0 )								# �ڵ�����Ϊ 0

	def __layoutNodes( self, pyStart = None ) :
		"""
		�������нڵ��λ�ã���ָ���ڵ� pyStart ��ʼ���У�
		������Ƶ�Ŀ���ǣ����������һ���ڵ�ʱ����������ǰ��ڵ��λ�ã�����һ���ڵ�ʱ��Ҳ�������Ų���ڵ�ǰ��ڵ��λ��
		"""
		while( pyStart is not None ) :						# ��ָ���Ľڵ㿪ʼ����������Ľڵ�
			self.__layoutNode( pyStart )					# ���ýڵ�λ��
			pyStart = pyStart.pyNext						# �� start ָ����һ���ڵ�
		if self.pyLast is None :							# ������һ���ڵ�Ϊ None������ζ��û���κνڵ�
			Control._setHeight( self, 0 )					# �����ýڵ��б�߶�Ϊ 0
		else :												# ����
			Control._setHeight( self, self.pyLast.bottom )	# �߶�Ϊ���һ���ڵ�ĵ׾�

	# -------------------------------------------------
	def __pasteNode( self, pyNode ) :
		"""
		���б������ճ��һ���ڵ�
		"""
		pyPNode = self.pyOwner								# �ڵ��б�������ڵ�
		while pyPNode is not None :							# ѭ���������ڵ�
															# ��������ڵ���ӵ��б��У�������һ������
			assert pyPNode != pyNode, "you can't add its parent node as its child node!"
			pyPNode = pyPNode.pyParentNode					# ����ָ�򸸽ڵ�ĸ��ڵ�

		if pyNode.pyParentNode is not None :				# ���Ҫ��ӵĽڵ㻹�и��ڵ�
			pyNode.pyParentNode.pyNodes.remove( pyNode )	# �����Ƚ�������ĸ��ڵ���ɾ��
		self.addPyChild( pyNode )							# ճ���ڵ�
		return True											# ����ճ���ɹ�

	# -------------------------------------------------
	def __attachSubNode( self, pyNode ) :
		"""
		��ʼ��Ҫ��ӵĽڵ�(�󶨽ڵ��һЩ����)
		"""
		pyNode.setTreeView__( self.pyTreeView )							# ���ýڵ����������ͼ
		pyNode.setParentNode__( self.pyOwner )							# ���ýڵ������ĸ��ڵ�
		pyNode.toggleRightClickSelect__( self.__rightClickSelect )		# �����Ƿ��Ҽ����ѡ�нڵ�
		pyNode.nodeOffset = self.__nodeOffset							# ���ýڵ�ĸ��ӽڵ�ˮƽλ��ƫ��
		if pyNode.selected : pyNode.selected = False					# ����ڵ㴦��ѡ��״̬����ȡ���ڵ��ѡ��״̬

	def __detachSubNode( self, pyNode ) :
		"""
		ȡ��ָ���ڵ�����԰�
		"""
		pyNode.setParentNode__( None )					# ȡ���������ڵ�İ�
		pyNode.toggleRightClickSelect__( False )		# ȡ���Ҽ����ѡ������
		pyNode.setForeNode__( None )					# ȡ��ǰ���ֵܽڵ�
		pyNode.setNextNode__( None )					# ȡ������ֵܽڵ�
		pyNode.collapse()								# ��£�ڵ�
		pyNode.detach__()								# �ͷŽڵ�


	# ----------------------------------------------------------------
	# friend methods of this module
	# ----------------------------------------------------------------
	def onNodeExtended__( self, pyNode, pyExtendedNode ) :
		"""
		��ĳ���ڵ�չ��ʱ������
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeExtended__( pyNode, pyExtendedNode )

	def onNodeCollapsed__( self, pyNode, pyCollapsedNode ) :
		"""
		��ĳ���ڵ��£���ӽڵ����ڵ����ʱ������
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeCollapsed__( pyNode, pyCollapsedNode )

	# -------------------------------------------------
	def onNodeAddSubNode__( self, pyNode ) :
		"""
		��ĳ���ڵ�����ӽڵ�ʱ������
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeAddSubNode__( pyNode )

	def onNodeRemoveSubNode__( self, pyNode ) :
		"""
		��ĳ���ڵ�ɾ���ӽڵ�ʱ������
		"""
		if pyNode not in self : return
		self.__layoutNodes( pyNode.pyNext )
		if self.pyOwner :
			self.pyOwner.onSubNodeRemoveSubNode__( pyNode )

	# ---------------------------------------
	def onNodeWidthChanged__( self, pyNode = None ) :
		"""
		ĳ�ڵ��ȸı�ʱ������
		"""
		pyOwner = self.pyOwner
		if self.count == 0 :									# û�����˽ڵ�
			Control._setWidth( self, 0 )						# ���ÿ��Ϊ 0
			if pyOwner : pyOwner.onSubNodesWidthChanged__()		# ������ڸ��ڵ㣬��֪ͨ���ڵ㣬��ȸı�
			return

		currWidth = self.width									# ��ǰ���
		if not pyNode or currWidth > pyNode.right :				# ���û������Ŀ�ȸı�ڵ㣬��ǰ��ȴ��ڿ�ȸı�ڵ�Ŀ��
			newWidth = 0
			for pyNode in self :								# ����Ҫ�����ҳ�������Ľڵ�
				newWidth = max( newWidth, pyNode.right )
			if newWidth == currWidth : return					# �������Ƚڵ���Ȼ���䣬����ζ�Ű����Ȳ��øı�
			Control._setWidth( self, newWidth )					# �����ȸı��ˣ�����°�����
			if pyOwner : pyOwner.onSubNodesWidthChanged__()		# ��֪ͨ���ڵ㣬��ȸı�
		elif currWidth == pyNode.right :						# �����ǰ������ȸı�ڵ�Ŀ��һ����������Ȳ���
			return
		else :
			newWidth = pyNode.right								# �¿��Ĭ��Ϊ��ȸı�Ľڵ�Ŀ��
			Control._setWidth( self, newWidth )					# �򽫿�ȱ��
			if pyOwner : pyOwner.onSubNodesWidthChanged__()		# ֪ͨ���ڵ㣬��ȸı�


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def adds( self, pyNodes ) :
		"""
		���һ��ڵ�
		"""
		for pyNode in pyNodes :
			self.add( pyNode )

	def add( self, pyNode ) :
		"""
		��ӽڵ�
		"""
		if not self.__pasteNode( pyNode ) : return					# ���ճ���ڵ㲻�ɹ����򷵻�
		self.__attachSubNode( pyNode )							# �󶨽ڵ�����

		if self.pyLast is not None :								# ������֮ǰ�Ѿ��нڵ�
			self.pyLast.setNextNode__( pyNode )						# ��֮ǰ�����һ���ڵ�ĺ�ӽڵ�����Ϊ�µĽڵ�
		pyNode.setForeNode__( self.pyLast )							# ���½ڵ��ǰ�ӽڵ�����Ϊ֮ǰ���һ���ڵ�
		pyNode.setNextNode__( None )								# �����½ڵ�ĺ�ӽڵ�����Ϊ None
		self.__pyNodes.append( pyNode )								# ��ӵ��ڲ��б�
		self.__layoutNodes( pyNode )								# ������������ӵĽڵ�
		self.onNodeWidthChanged__( pyNode )							# ֪ͨ�����ȿ���Ҫ�ı�
		self.pyOwner.onSubNodeAddSubNode__( pyNode )				# �������ڵ㴥������ӽڵ�ص�

	def insert( self, index, pyNode ) :
		"""
		����һ���ڵ�
		"""
		if index >= self.count :									# �������λ�ô���Ԫ�ظ���
			self.add( pyNode )										# �򣬵�����β�����
			return
		if index < 0 :
			index = max( 0, self.count + index ) 					# ����Ǹ���������ת��Ϊ������

		if pyNode in self and \
			index == self.__pyNodes.index( pyNode ) :				# ���Ҫ����Ľڵ��Ѿ����б��У�������ͬһ��λ��
				return												# �򷵻�
		pyNNode = self[index]										# ��ȡ�����������Ľڵ�
		if not self.__pasteNode( pyNode ) : return					# ճ���ڵ㣬ʧ���򷵻�
		self.__attachSubNode( pyNode )							# �󶨲���ڵ�����
		index = self.__pyNodes.index( pyNNode )						# ��ȡҪ���봦��������ע�⣺�п���Ҫ����Ľڵ��Ѿ����б��У�
																	# ���д������Ƕ���ġ�����������Ļ����� pastNode ��ʱ��
																	# Ҫ����Ľڵ��Ѿ����б���ɾ���������������ͱ���ˣ������»�ȡ������
		pyFore = pyNNode.pyFore										# ������λ��ǰ�Ľڵ��Ƿ����
		if pyFore is not None :										# �������
			pyFore.setNextNode__( pyNode )							# �����ĺ�ӽڵ�����Ϊ�½ڵ�
		pyNode.setForeNode__( pyFore )								# ���½ڵ��ǰ�ӽڵ�����Ϊ����������ǰ�ڵ�
		pyNode.setNextNode__( pyNNode )								# ���²���ڵ�ĺ�ӽڵ�����Ϊ������������ԭ�ڵ�
		pyNNode.setForeNode__( pyNode )								# ������������ԭ�ڵ��ǰ�ӽڵ�����Ϊ�½ڵ�
		self.__pyNodes.insert( index, pyNode )						# ���½ڵ���뵽�ڲ��б�
		self.__layoutNodes( pyNode )								# ���Žڵ�λ��
		self.onNodeWidthChanged__( pyNode )							# ֪ͨ�����ȿ���Ҫ�ı�
		self.pyOwner.onSubNodeAddSubNode__( pyNode )				# �������ڵ㴥������ӽڵ�ص�

	def remove( self, pyNode ) :
		"""
		ɾ��һ���ڵ�
		"""
		if pyNode not in self :
			ERROR_MSG( "%s is not in my list!" % str( pyNode ) )
			return													# �����ж�ɾ���Ľڵ��Ƿ����

		pyFore = pyNode.pyFore										# ��ȡǰ�ӽڵ�
		pyNext = pyNode.pyNext										# ��ȡ��ӽڵ�
		if pyFore is not None :										# ���ǰ�ӽڵ����
			pyFore.setNextNode__( pyNext )							# ��ǰ�ӽڵ�ĺ�ӽڵ�����Ϊ�µĺ�ӽڵ�
		if pyNext is not None :										# ���ԭ��ӽڵ����
			pyNext.setForeNode__( pyFore )							# �򽫺�ӽڵ��ǰ�ӽڵ�����Ϊ�µ�ǰ�ӽڵ�
		self.delPyChild( pyNode )									# UI ��ɾ��֮
		self.__pyNodes.remove( pyNode )								# �б���ɾ��֮
		self.__detachSubNode( pyNode )							# ������԰�
		self.__layoutNodes( pyNext )								# �������нڵ�
		self.onNodeWidthChanged__()									# ֪ͨ�����ȿ���Ҫ�ı�
		if self.pyOwner :											# ������ڵ����
			self.pyOwner.onSubNodeRemoveSubNode__( pyNode )			# ���������ڵ��֪ɾ���ڵ�

	def clear( self ) :
		"""
		������нڵ�
		"""
		for idx in xrange( self.count - 1, -1, -1 ) :
			self.remove( self.__pyNodes[idx] )
		self.onNodeWidthChanged__()									# ֪ͨ���棬��ȿ���Ҫ�ı�
		Control._setHeight( self, 0 )

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		�������������нڵ�λ��
		@type				cmp		: functor
		@param				cmp		: cmp(x, y) -> -1, 0, 1
		@type				key		: functor
		@param				key		: lambda x : x.XXX
		@type				reverse : bool
		@param				reverse : �Ƿ���
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
	pyTreeView = property( _getTreeView )			# ��ȡ����ͼ
	pyOwner = property( _getOwner )					# ��ȡ�ӽڵ���������Ľڵ㣨����Ƕ���ڵ㼯�ϣ��������� pyTeeView��
	count = property( _getCount )					# �ڵ�����
	pyExtendedNodes = property( _getExtendedNodes )	# ��ȡ����չ���Ľڵ�
	pyFirst = property( _getPyFirst )				# ��һ���ڵ�
	pyLast = property( _getPyLast )					# ���һ���ڵ�

	left = property( Control._getLeft )				# �������Ϊֻ��
	center = property( Control._getCenter )			# ����ˮƽ�о�Ϊֻ��
	right = property( Control._getRight )			# �����Ҿ�Ϊֻ��
	top = property( Control._getTop )				# ���ö���Ϊֻ��
	middle = property( Control._getMiddle )			# ���ô�ֱ�о�Ϊֻ��
	bottom = property( Control._getBottom )			# ���õ׾�Ϊֻ��
	width = property( Control._getWidth )			# ���������Ϊֻ��
	height = property( Control._getHeight )			# ���߶�����Ϊֻ��
	size = property( Control._getSize )				# ����С����Ϊֻ��


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
			treeNode ( �ݹ� )
"""
# --------------------------------------------------------------------
class TreeNode( Control ) :
	"""
	���ڵ㣨�����ӽڵ���棩
	"""
	# ----------------------------------------------------------------
	# �������ӽڵ����Ľڵ�
	# ----------------------------------------------------------------
	class Node( Control ) :
		__cc_edge_width = 8.0

		def __init__( self, node, pyBinder ) :
			Control.__init__( self, node, pyBinder )
			self.focus = True									# �ɱ����
			self.crossFocus = True								# �ɽ�����������Ϣ
			self.__pyText = StaticText( node.sText )			# �ڵ��ı�
			self.__icon = node.elements["icon"]
			self.__autoWidth = True								# �Ƿ�����Ӧ�ı����
			self.__orignWidth = node.width						# �ڵ��ԭʼ���
			self.icon = ""										# Ĭ��û��ͼ��

		def __del__( self ) :
			if Debug.output_del_TreeView :
				INFO_MSG( str( self ) )


		# ---------------------------------------------
		# protected
		# ---------------------------------------------
		def resetNodeWidth_( self ) :
			"""
			��ȡ�ڵ���
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
		text = property( _getText, _setText )								# ��ȡ/�����ı�
		font = property( _getFont, _setFont )								# ��ȡ/�����ı�����
		foreColor = property( _getForeColor, _setForeColor )				# ��ȡ/����ǰ��ɫ
		backColor = property( _getBackColor, _setBackColor )				# ��ȡ/���ñ���ɫ
		icon = property( _getIcon, _setIcon )								# ��ȡ/����ͼ�꣺( ·��, mapping )
		autoWidth = property( _getAutoWidth, _setAutoWidth )				# �ڵ����Ƿ�����Ӧ�ı����
		fontSize = property( _getFontSize, _setFontSize )
		limning = property( _getLimning, _setLimning )				# MACRO DEFINATION: ��ȡ/�������Ч����Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
		limnColor = property( _getLimnColor, _setLimnColor )		# tuple: ��ȡ/���������ɫ

	# ----------------------------------------------------------------
	# tree node including sub node
	# ----------------------------------------------------------------
	def __init__( self, tNode = None, pyBinder = None ) :
		if tNode is None :
			tNode = hfUILoader.load( "guis/controls/treeview/node.gui" )
		Control.__init__( self, tNode, pyBinder )
		self.__pyTreeView = None								# ����������ͼ
		self.__pyParentNode = None								# �����ĸ��ڵ�

		self.__selectable = True								# �ڵ��Ƿ���Ա�ѡ��
		self.__selected = False									# ��ǰ�Ƿ���ѡ��״̬
		self.__isExtended = False								# ��ǰ�Ƿ���չ��״̬
		self.__canBeHighlight = True							# �Ƿ����������������ʱ��
		self.__rightClickSelect = False							# �Ƿ������Ҽ����ѡ��
		self.__showPlusMinus = True								# �Ƿ���ʾ�Ӽ���

		self.__pyFore = None									# ǰһ���ֵܽڵ�
		self.__pyNext = None									# ��һ���ֵܽڵ�
		
		self.__viewTextNum = -1								# ��ʾ���ٸ��ַ���������...���棬Ĭ��ȫ����ʾ
		self.__trueText = ""								# ������Ҫ��ʾ���ַ�

		self.__initialize( tNode )								# ��ʼ���ڵ�
		self.showPlusMinus = self.__pyPlusMinus.rvisible		# �Ƿ���ʾ�Ӽ��ţ�ĳ�˸� load ���������� UI �ļӼ��ŵĿɼ���һ��

	def subclass( self, tNode ) :
		Control.subclass( self, tNode )
		self.__initialize( tNode )
		return self

	def dispose( self ) :
		if self.pyParentNode :									# �ֶ��ͷ�֮ǰ���ж��Ƿ��и��ڵ�
			self.pyParentNode.pyNodes.remove( self )			# ����У������ȴӸ��ڵ�������
		Control.dispose( self )

	def __del__( self ) :
		if Debug.output_del_TreeView :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, tNode ) :
		if tNode is None : return
		self.pyNode_ = self.Node( tNode.node, self )												# �������ӽڵ�Ľڵ�
		self.pySubNodes_ = Nodes( tNode.nodesPanel, self, self.pyTreeView )							# �����ӽڵ��б�

		self.__pyPlusMinus = Icon( tNode.plusMinus )												# �Ӽ���
		self.__pyPlusMinus.focus = True																# �Ӽ���������
		self.__pyPlusMinus.onLMouseDown.bind( self.__toggleExtended )								# �󶨼Ӽ��ŵĵ���¼�
		size = self.__pyPlusMinus.size																# �Ӽ��ŵĴ�С
		self.__plusMapping = util.getStateMapping( size, UIState.MODE_R1C2, UIState.MODE_R1C1 )		# �Ӻ� mapping
		self.__minusMapping = util.getStateMapping( size, UIState.MODE_R1C2, UIState.MODE_R1C2 )	# ���� mapping
		self.__pyPlusMinus.mapping = self.__minusMapping											# Ĭ����ʾΪ����

		self.__mappings = {}																		# �ڵ�״̬ napping
		size = self.pyNode_.size
		self.__mappings[UIState.COMMON] = util.getStateMapping( size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__mappings[UIState.HIGHLIGHT] = util.getStateMapping( size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__mappings[UIState.SELECTED] = util.getStateMapping( size, UIState.MODE_R3C1, UIState.ST_R3C1 )

		self.foreColors_ = {}																		# �ڵ�״̬ǰ��ɫ
		self.foreColors_[UIState.COMMON] = self.pyNode_.foreColor
		self.foreColors_[UIState.HIGHLIGHT] = ( 40, 23, 250, 255 )
		self.foreColors_[UIState.SELECTED] = ( 0, 255, 0, 255 )

		self.backColors_ = {}																		# �ڵ�״̬����ɫ
		self.backColors_[UIState.COMMON] = self.pyNode_.backColor
		self.backColors_[UIState.HIGHLIGHT] = self.backColors_[UIState.COMMON]
		self.backColors_[UIState.SELECTED] = self.backColors_[UIState.COMMON]

		Control._setSize( self, ( self.pyNode_.right, self.pySubNodes_.top) )

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Control.generateEvents_( self )
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )		# ���ڵ㱻ѡ��״̬�ı�ʱ����
		self.__onBeforeExtend = self.createEvent_( "onBeforeExtend" )		# ���ڵ㽫Ҫչ��ʱ������
		self.__onBeforeCollapse = self.createEvent_( "onBeforeCollapse" )	# ���ڵ㽫Ҫ��£ʱ������
		self.__onExtended = self.createEvent_( "onExtended" )				# ���ڵ�չ��ʱ����
		self.__onCollapsed = self.createEvent_( "onCollapsed" )				# ���ڵ��£ʱ����
		self.__onSubNodeAdded = self.createEvent_( "onSubNodeAdded" )		# �����һ���ӽڵ�ʱ������
		self.__onSubNodeRemoved = self.createEvent_( "onSubNodeRemoved" )	# ��ɾ��һ���ӽڵ�ʱ������

	# -------------------------------------------------
	@property
	def onSelectChanged( self ) :
		"""
		���ڵ㱻ѡ��ʱ����
		"""
		return self.__onSelectChanged

	# ---------------------------------------
	@property
	def onBeforeExtend( self ) :
		"""
		���ڵ㽫Ҫչ��ʱ������
		"""
		return self.__onBeforeExtend

	@property
	def onBeforeCollapse( self ) :
		"""
		���ڵ㽫Ҫ��£ʱ������
		"""
		return self.__onBeforeCollapse

	@property
	def onExtended( self ) :
		"""
		���ڵ�չ��ʱ����
		"""
		return self.__onExtended

	@property
	def onCollapsed( self ) :
		"""
		���ڵ��£ʱ����
		"""
		return self.__onCollapsed

	# ---------------------------------------
	@property
	def onSubNodeAdded( self ) :
		"""
		�����һ���ӽڵ�ʱ������
		"""
		return self.__onSubNodeAdded

	@property
	def onSubNodeRemoved( self ) :
		"""
		��ɾ��һ���ӽڵ�ʱ������
		"""
		return self.__onSubNodeRemoved


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ) :
		"""
		ѡ�нڵ�
		"""
		self.setState( UIState.SELECTED )					# ����Ϊѡ��״̬
		self.__selected = True								# ����ѡ������Ϊ True
		if self.pyTreeView :								# �����������ͼ��Ϊ None
			self.pyTreeView.onNodeSelected__( self )		# ��֪����ͼ�ڵ㱻ѡ��
		self.onSelectChanged( True )						# �����ڵ�ѡ���¼�

	def __deselect( self ) :
		"""
		ȡ���ڵ��ѡ��״̬
		"""
		self.__selected = False								# ȡ��ѡ������
		self.setState( UIState.COMMON )						# ����Ϊ��ͨ״̬
		if self.pyTreeView is not None :					# ���������������ͼ
			self.pyTreeView.onNodeDeselected__( self )		# �򣬸�֪ĳ�ڵ�ȡ��ѡ��
		self.onSelectChanged( False )						# ����ȡ��ѡ���¼�

	# ---------------------------------------
	def __toggleExtended( self ) :
		"""
		�ı�չ��/�۵�״̬
		"""
		if self.__isExtended : self.collapse()
		else : self.extend()

	def __setPlusMinusState( self ) :
		"""
		���üӼ���״̬
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
		����������������ͼ
		"""
		if pyTreeView is None :
			self.__pyTreeView = None
		else :
			self.__pyTreeView = weakref.ref( pyTreeView )
		self.__setPlusMinusState()
		self.pySubNodes_.setTreeView__( pyTreeView )

	def setParentNode__( self, pyParent ) :
		"""
		�����������ڵ�
		"""
		if pyParent is None :
			self.__pyParentNode = None
		else :
			self.__pyParentNode = weakref.ref( pyParent )

	# ---------------------------------------
	def toggleRightClickSelect__( self, value ) :
		"""
		�����Ƿ��Ҽ����ѡ�нڵ�
		"""
		self.__rightClickSelect = value
		self.pySubNodes_.toggleRightClickSelect__( value )

	# -------------------------------------------------
	def onSubNodeExtended__( self, pyNode, pyExtendedNode ) :
		"""
		��ĳ���ӽڵ�չ��ʱ������
		"""
		if self.isExtended :
			Control._setHeight( self, self.pySubNodes_.bottom )
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeExtended__( self, pyExtendedNode )		# ���߸��ڵ�������ӽڵ�չ��

	def onSubNodeCollapsed__( self, pyNode, pyCollapsedNode ) :
		"""
		��ĳ���ӽڵ���ӽڵ����ڵ��£ʱ������
		"""
		if self.isExtended :
			Control._setHeight( self, self.pySubNodes_.bottom )
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeCollapsed__( self, pyCollapsedNode )	# ���߸��ڵ�������ӽڵ����

	# ---------------------------------------
	def onSubNodeAddSubNode__( self, pyNode ) :
		"""
		��ĳ���ӽڵ�����ӽڵ�ʱ������
		"""
		if self.isExtended :
			Control._setHeight( self, self.pySubNodes_.bottom )
		self.__setPlusMinusState()
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeAddSubNode__( self )
		self.onSubNodeAdded()

	def onSubNodeRemoveSubNode__( self, pyNode ) :
		"""
		��ĳ���ӽڵ�ɾ���ӽڵ�ʱ������
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
		���нڵ��ȸı�ʱ������
		"""
		width = self.pyNode_.right
		if self.__isExtended :											# ����ڵ����չ��״̬
			width = max( width, self.pySubNodes_.right )				# ������ȵ��ڽڵ������ӽڵ�������нϴ���
		if self.width == width : return									# ����ֽڵİ������뱾�ڵ������һ��������Ҫ���Ŀ��
		Control._setWidth( self, width )								# �������ð�����
		if self.pyParentNode :											# ������ڸ��ڵ�
			self.pyParentNode.pyNodes.onNodeWidthChanged__( self )		# ��֪ͨ���ڵ���ӽڵ����ĳ�ڵ��ȸı�

	# -------------------------------------------------
	def setForeNode__( self, pyNode ) :
		"""
		����ǰ���ֵܽڵ�
		"""
		if pyNode is None :
			self.__pyFore = None
		else :
			self.__pyFore = weakref.ref( pyNode )

	def setNextNode__( self, pyNode ) :
		"""
		���ú����ֵܽڵ�
		"""
		if pyNode is None :
			self.__pyNext = None
		else :
			self.__pyNext = weakref.ref( pyNode )

	def detach__( self ) :
		"""
		���ڵ�򱾽ڵ�ĸ��ڵ㱻�Ƴ�
		"""
		if self.selected :
			self.selected = False						# ȡ��ѡ��״̬
		self.__pyTreeView = None						# ȡ������������ͼ��
		for pyNode in self.pyNodes :
			pyNode.detach__()							# ֪ͨ�����ӽڵ� detach


	# -------------------------------------------------
	# friend methods of inner node
	# -------------------------------------------------
	def onLMouseDown__( self, mods ) :
		"""
		�������ڽڵ��ϰ���
		"""
		return Control.onLMouseDown_( self, mods )

	def onLMouseUp__( self, mods ) :
		"""
		�������ڽڵ�������
		"""
		return Control.onLMouseUp_( self, mods )

	def onRMouseDown__( self, mods ) :
		"""
		����Ҽ��ڽڵ��ϰ���
		"""
		return Control.onRMouseDown_( self, mods )

	def onRMouseUp__( self, mods ) :
		"""
		����Ҽ��ڽڵ�������
		"""
		return Control.onRMouseUp_( self, mods )

	# ---------------------------------------
	def onLClick__( self, mods ) :
		"""
		���������
		"""
		self.selected = True
		Control.onLClick_( self, mods )
		if self.pyTreeView :
			self.pyTreeView.onTreeNodeLClick( self )
		return True

	def onRClick__( self, mods ) :
		"""
		����Ҽ����
		"""
		if self.__rightClickSelect :
			self.selected = True
		Control.onRClick_( self, mods )
		if self.pyTreeView :
			self.pyTreeView.onTreeNodeRClick( self )
		return True

	def onLDBClick__( self, mods ) :
		"""
		���˫��
		"""
		self.__toggleExtended()
		Control.onLDBClick_( self, mods )
		return True

	def onMouseEnter__( self ) :
		"""
		������
		"""
		if self.canBeHighlight :
			self.setState( UIState.HIGHLIGHT )
		Control.onMouseEnter_( self )
		return True

	def onMouseLeave__( self ) :
		"""
		����뿪
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
		����ƶ�
		"""
		return Control.onMouseMove_( self, dx, dy )

	# ---------------------------------------
	def onDragStart__( self, pyDragged ) :
		"""
		��ʼ����
		"""
		self.onDragStart()
		return True

	def onDragStop__( self, pyDragged ) :
		"""
		�ϷŽ���
		"""
		return Control.onDragStop_( self, pyDragged.pyBinder )

	def onDrop__( self, pyTarget, pyDropped ) :
		"""
		����
		"""
		return Control.onDrop_( self, self, pyDropped.pyBinder )

	def onDragEnter__( self, pyTarget, pyDragged ) :
		"""
		�ϷŽ���
		"""
		return Control.onDragEnter_( self, self, pyDragged.pyBinder )

	def onDragLeave__( self, pyTarget, pyDragged ) :
		"""
		�Ϸ��뿪
		"""
		return Control.onDragLeave_( self, self, pyDragged.pyBinder )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		"""
		�ڵ�״̬�ı�ʱ������
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		���ýڵ�״̬
		"""
		if state == UIState.COMMON and self.selected :				# ����ڵ㱻ѡ��
			state = UIState.SELECTED								# ��״̬ʼ����ѡ��״̬
		self.pyNode_.mapping = self.__mappings[state]				# ����״̬ mapping
		self.pyNode_.foreColor = self.foreColors_[state]			# ����״̬ǰ��ɫ
		self.pyNode_.backColor = self.backColors_[state]			# ����״̬����ɫ
		self.onStateChanged_( state )								# �ص���������
		if state == UIState.HIGHLIGHT and self.pyTreeView :			# �������ͼ����
			self.pyTreeView.onNodeHighlight__( self )				# ��֪ͨ����ͼ���нڵ�״̬�ı�

	# -------------------------------------------------
	def extend( self ) :
		"""
		չ���ڵ�
		"""
		if self.__isExtended : return								# ����Ѿ�չ�����򷵻�
		self.onBeforeExtend()										# ����չ��֮ǰ�¼�
		if self.pyTreeView :										# �������������ͼ����
			self.pyTreeView.onSubNodeBeforeExtend__( self )			# ��֪ͨ����ͼ�ڵ㽫Ҫչ��
		self.__isExtended = True									# ����չ������Ϊ True
		Control._setHeight( self, self.pySubNodes_.bottom )			# ���ýڵ�߶�
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeExtended__( self, self )# ���߸��ڵ�������ӽڵ�չ��
		self.onSubNodesWidthChanged__()								# ��֪���ڵ����Ѹı�
		self.__setPlusMinusState()									# ���üӼ���״̬
		self.onExtended()

	def collapse( self ) :
		"""
		��£�ڵ�
		"""
		if not self.__isExtended : return							# ���������û��չ�����򷵻�
		self.onBeforeCollapse()										# ������Ҫ��£�¼�
		if self.pyTreeView :										# �������������ͼ����
			self.pyTreeView.onSubNodeBeforeCollapse__( self )		# ��֪ͨ����ͼ����Ҫ��£
		self.__isExtended = False									# ����չ������Ϊ False
		Control._setHeight( self, self.pySubNodes_.top )			# �������ýڵ�߶�( ��ȥ 0.1 ��ԭ���ǵ������)
		self.__setPlusMinusState()									# ���üӼ���
		self.onSubNodesWidthChanged__()								# ��֪���ڵ����Ѹı�
		self.onCollapsed()											# ������£�¼�
		if self.pyParentNode :
			self.pyParentNode.pyNodes.onNodeCollapsed__( self, self )	# ���߸��ڵ�������ӽڵ����

	# -------------------------------------------------
	def hitTest( self, x, y ) :
		"""
		�ж�ָ�����ص��Ƿ����ڽڵ���
		"""
		return self.pyNode_.hitTest( x, y )

	def isMouseHit( self ) :
		"""
		�ж�����Ƿ���нڵ�
		"""
		return self.pyNode_.isMouseHit()

	# -------------------------------------------------
	def showPlusMinusIcon( self ) :
		"""
		��ʾ�Ӽ���
		"""
		self.__showPlusMinus = True
		self.__pyPlusMinus.visible = True

	def hidePlusMinusIcon( self ) :
		"""
		���ؼӼ���
		"""
		self.__showPlusMinus = False
		self.__pyPlusMinus.visible = False

	# ---------------------------------------
	def showPlusIcon( self ) :
		"""
		��� self.__showPlusMinus == True��������������ʾ�Ӻ�ͼ��
		"""
		self.__pyPlusMinus.mapping = self.__plusMapping

	def showMinusIcon( self ) :
		"""
		��� self.__showPlusMinus == True��������������ʾ����ͼ��
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
		self.onSubNodesWidthChanged__()								# ��֪���ڵ����Ѹı�

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyNode_.font

	def _setFont( self, font ) :
		self.pyNode_.font = font
		self.onSubNodesWidthChanged__()								# ��֪���ڵ����Ѹı�

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
		self.onSubNodesWidthChanged__()								# ��֪���ڵ����Ѹı�

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
	focus = property( _getFocus, _setFocus )										# ��ȡ/���ýڵ��Ƿ���հ�����Ϣ
	crossFocus = property( _getCrossFocus, _setCrossFocus )							# ��ȡ/���ýڵ��Ƿ������������Ϣ
	moveFocus = property( _getMoveFocus, _setMoveFocus )							# ��ȡ/���ýڵ��Ƿ��������ƶ���Ϣ
	dragFocus = property( _getDragFocus, _setDragFocus )							# ��ȡ/���ýڵ��Ƿ����������Ϣ
	dropFocus = property( _getDropFocus, _setDropFocus )							# ��ȡ/���ýڵ��Ƿ���շ�����Ϣ

	pyTreeView = property( _getTreeView )											# ��ȡ����������ͼ��û����Ϊ None
	pyParentNode = property( _getParentNode )										# ��ȡ�����ĸ��ڵ㣬û����Ϊ None
	pyFore = property( _getForeNode )												# ��ȡǰһ���ֵܽڵ㣬û����Ϊ None
	pyNext = property( _getNextNode )												# ��ȡ��һ���ֵܽڵ㣬û����Ϊ None

	text = property( _getText, _setText )											# ��ȡ/���ýڵ��ı�
	font = property( _getFont, _setFont )											# ��ȡ/���ýڵ��ı�����
	foreColor = property( _getForeColor, _setForeColor )							# ��ȡ/���ýڵ��ı�ǰ��ɫ
	backColor = property( _getBackColor, _setBackColor )							# ��ȡ/���ýڵ��ı�����ɫ
	icon = property( _getIcon, _setIcon )											# ��ȡ/���ýڵ�ͼ��

	pyNodes = property( _getNodes )													# ��ȡ�ӽڵ��б����

	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )			# ��ȡ/������ͨ״̬�µ�ǰ��ɫ
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor )	# ��ȡ/���ø���״̬�µ�ǰ��ɫ
	selectedForeColor = property( _getSelectedForeColor, _setSelectedForeColor )	# ��ȡ/����ѡ��״̬�µ�ǰ��ɫ
	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )			# ��ȡ/������ͨ״̬�µı���ɫ
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor )	# ��ȡ/���ø���״̬�µı���ɫ
	selectedBackColor = property( _getSelectedBackColor, _setSelectedBackColor )	# ��ȡ/����ѡ��״̬�µı���ɫ

	selectable = property( _getSelectable, _setSelectable )							# ��ȡ/���ýڵ��Ƿ���Ա�ѡ��
	canBeHighlight = property( _getCanBeHighlight, _setCanBeHighlight )				# ��ȡ/����������ڵ�ʱ���Ƿ����Ϊ����
	showPlusMinus = property( _getShowPlusMinus, _setShowPlusMinus )				# ��ȡ/�����Ƿ���ʾ�Ӽ���

	selected = property( _getSelected, _setSelected )								# ��ȡ/���ýڵ��ѡ��״̬
	isExtended = property( _getIsExtended )											# ��ȡ�ڵ��Ƿ���չ��״̬

	nodeHeight = property( _getNodeHeight )											# ��ȡ�ڵ�߶�
	nodeOffset = property( _getNodeOffset, _setNodeOffset )							# ��ȡ/���ýڵ����丸�ڵ��ˮƽλ��ƫ��
	autoWidth = property( _getAutoWidth, _setAutoWidth )							# ��ȡ/���ýڵ����Ƿ�����Ӧ�ڵ��ı��Ŀ��

	width = property( Control._getWidth )											# ��ȡ�ڵ���
	height = property( Control._getHeight )											# ��ȡ�ڵ�߶�
	size = property( Control._getSize )												# ��ȡ�ڵ��С
	left = property( Control._getLeft )												# ��ȡ�ڵ����
	center = property( Control._getCenter )											# ��ȡ�ڵ�ˮƽ�о�
	right = property( Control._getRight )											# ��ȡ�ڵ��Ҿ�
	top = property( Control._getTop )												# ��ȡ�ڵ㶥��
	middle = property( Control._getMiddle )											# ��ȡ�ڵ㴹ֱ�о�
	bottom = property( Control._getBottom )											# ��ȡ�ڵ�׾�
	viewTextNum = property( _getViewTextNum, _setViewTextNum )						# ��ȡ/���ÿ����ַ���
	trueText = property( _getTrueText )												# ��ȡ������Ҫ��ʾ���ַ�
	fontSize = property( _getFontSize, _setFontSize )
	limning = property( _getLimning, _setLimning )				# MACRO DEFINATION: ��ȡ/�������Ч����Font.LIMN_NONE/Font.LIMN_OUT/Font.LIMN_SHD
	limnColor = property( _getLimnColor, _setLimnColor )		# tuple: ��ȡ/���������ɫ

# --------------------------------------------------------------------
# implement treeview contains a horizontal scrollbar and a vertical scroll bar
# --------------------------------------------------------------------
class HVTreeView( TreeViewBase, HVScrollPanel ) :
	def __init__( self, panel, hsbar, vsbar, pyBinder = None ) :
		HVScrollPanel.__init__( self, panel, hsbar, vsbar, pyBinder )
		TreeViewBase.__init__( self, panel )
		self.h_perScroll = 20											# Ĭ��ˮƽ��ÿ�ι��������� 20 ����λ������
		self.v_perScroll = 40											# Ĭ�ϴ�ֱ��ÿ�ι��������� 40 ����λ������

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
		���������������ʱ������
		"""
		HVScrollPanel.onVScroll_( self, value )
		TreeViewBase.onScroll_( self, value )

	# -------------------------------------------------
	def onNodesWidthChanged_( self, width ) :
		"""
		ȫ���ڵ�Ŀ�ȸı�ʱ������
		"""
		self.h_wholeLen = width

	def onModesHeightChanged_( self, height ) :
		"""
		ȫ���ڵ�ĸ߶ȸı�ʱ������
		"""
		self.v_wholeLen = height

	def scrollToNode( self, pyNode ) :
		"""
		���ĳ���ڵ㲻�ɼ����������ĳ���ڵ㴦����ĳ���ڵ�ɼ���
		"""
		t = pyNode.getTopToUI( self )									# �ڵ�������ͼ�ϵĶ���
		subHeight = pyNode.height - pyNode.nodeHeight					# �����ӽڵ�ĸ߶�
		b = pyNode.getBottomToUI( self ) - subHeight					# �ڵ�������ͼ�ϵĵ׾�
		if t < 0 :														# ����ڵ�����������ͼ����
			self.v_scroll += t - pyNode.nodeHeight / 2					# �����������ָ���ڵ�պ�������ͼ�ɼ���������
		elif b > self.height :											# ����ڵ�����������ͼ����
			self.v_scroll += b - self.height + pyNode.nodeHeight / 2	# �����������ָ���ڵ�պ�������ͼ�ɼ���������


# --------------------------------------------------------------------
# implement treeview contains only one vertical scroll bar
# --------------------------------------------------------------------
class VTreeView( TreeViewBase, VScrollPanel ) :
	def __init__( self, panel, vsbar, pyBinder = None ) :
		VScrollPanel.__init__( self, panel, vsbar, pyBinder )
		TreeViewBase.__init__( self, panel )
		self.perScroll = 40											# Ĭ��ÿ�ι��������� 40 ����λ������

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
		���������������ʱ������
		"""
		VScrollPanel.onScroll_( self, value )
		TreeViewBase.onScroll_( self, value )

	# -------------------------------------------------
	def onModesHeightChanged_( self, height ) :
		"""
		ȫ���ڵ�ĸ߶ȸı�ʱ������
		"""
		self.wholeLen = height

	def scrollToNode( self, pyNode ) :
		"""
		���ĳ���ڵ㲻�ɼ����������ĳ���ڵ㴦����ĳ���ڵ�ɼ���
		"""
		t = pyNode.getTopToUI( self )								# �ڵ�������ͼ�ϵĶ���
		subHeight = pyNode.height - pyNode.nodeHeight				# �����ӽڵ�ĸ߶�
		b = pyNode.getBottomToUI( self ) - subHeight				# �ڵ�������ͼ�ϵĵ׾�
		if t < 0 :													# ����ڵ�����������ͼ����
			self.scroll += t - pyNode.nodeHeight / 2				# �����������ָ���ڵ�պ�������ͼ�ɼ���������
		elif b > self.height :										# ����ڵ�����������ͼ����
			self.scroll += b - self.height + pyNode.nodeHeight / 2	# �����������ָ���ڵ�պ�������ͼ�ɼ���������