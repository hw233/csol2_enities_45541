# -*- coding: gb18030 -*-
#
# $Id: HelpPanel.py,v 1.4 2008-04-14 10:26:35 huangyongwei Exp $

"""
implement system helper class.

2008.04.10: writen by huangyongwei
"""

from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.TreeView import TreeNode
from guis.controls.TreeView import travelTreeNode
from guis.tooluis.CSTextPanel import CSTextPanel

# --------------------------------------------------------------------
# implement base panel class
# --------------------------------------------------------------------
class HelpPanel( TabPanel ) :
	def __init__( self, panel ) :
		TabPanel.__init__( self, panel )
		tvTopic = panel.tvTopic
		self.pyTVTopic_ = TreeView( tvTopic.clipPanel, tvTopic.sbar )	# 帮助主题树视图
		self.pyTVTopic_.onTreeNodeSelected.bind( self.onTreeNodeSelected_ )

		tpContent = panel.tpContent
		self.pyTPContent_ = CSTextPanel( tpContent.clipPanel, tpContent.sbar )		# 显示帮助内容的文本版面
		self.pyTPContent_.opGBLink = True
		self.selTopic_ = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onTreeNodeSelected_( self, pyNode ) :
		"""
		当某个主题节点被选中时，被调用
		"""
		self.selTopic_ = pyNode.topic
		self.pyTPContent_.text = pyNode.topic.content


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	@staticmethod
	def createSubTreeNode_( topic ) :
		"""
		创建一个新的主题节点
		"""
		pyNode = TreeNode()
		pyNode.highlightForeColor = ( 0, 255, 255, 255 )
		pyNode.alwayShowPlusMinus = True
		pyNode.text = topic.title
		pyNode.topic = topic
		return pyNode

	@staticmethod
	def createRootTreeNode_( topic ) :
		"""
		由于表现上的需求，根节点和子节点采用不用的UI
		"""
		node = GUI.load( "guis/general/helper/treenode.gui" )
		uiFixer.firstLoadFix( node )
		pyNode = TreeNode( node )
		pyNode.autoWidth = False
		pyNode.highlightForeColor = ( 0, 255, 255, 255 )
		pyNode.alwayShowPlusMinus = True
		pyNode.text = topic.title
		pyNode.topic = topic
		return pyNode


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onWindowHid( self ) :
		"""
		窗口关闭时，将所有节点合龙
		"""
		self.pyTVTopic_.collapseAll()
		if len( self.pyTVTopic_.pyNodes ) :
			self.pyTVTopic_.pyNodes[0].selected = True
