# -*- coding: gb18030 -*-
#
# $Id: Guider.py,v 1.1 2008-04-14 10:26:35 huangyongwei Exp $

"""
implement system helper class.

2008.04.10: writen by huangyongwei
"""

from Helper import systemHelper
from guis import *
from HelpPanel import HelpPanel
from guis.controls.TreeView import travelTreeNode
from guis.controls.StaticText import StaticText
from LabelGather import labelGather


class Guider( HelpPanel ) :
	def __init__( self, panel ) :
		HelpPanel.__init__( self, panel )
		self.pyTVTopic_.onTreeNodeBeforeExtend.bind( self.__onTopicBeforeExtend )
		self.pyTVTopic_.onTreeNodeCollapsed.bind( self.__onTopicCollapsed )
		self.__setTopics()

		self.__pySTTpTitle = StaticText( panel.tpContent.bgTitle.stTitle )	# 指引内容标题
		self.__pySTTvTitle = StaticText( panel.tvTopic.bgTitle.stTitle )	# 指引条目标题

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyLabel( self.__pySTTpTitle, "HelpWindow:guider", "rbTpTitle" )	# 指引内容
		labelGather.setPyLabel( self.__pySTTvTitle, "HelpWindow:guider", "rbTvTitle" )	# 指引条目


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onTopicBeforeExtend( self, pyNode ) :
		"""
		某个主题节点展开之前被触发
		"""
		for topic in pyNode.topic.children :
			pyCH = self.createSubTreeNode_( topic )
			pyNode.pyNodes.add( pyCH )
			if topic.children :
				pyCH.showPlusIcon()
			else :
				pyCH.showMinusIcon()
			if topic == self.selTopic_ :
				self.pyTVTopic_.onTreeNodeSelected.shield()
				pyCH.selected = True
				self.pyTVTopic_.onTreeNodeSelected.unshield()

	def __onTopicCollapsed( self, pyNode ) :
		"""
		节点合龙之后被触发
		"""
		if pyNode.selected :
			pyNode.selected = False
		pyNode.pyNodes.clear()
		if len( pyNode.topic.children ) > 0 :			# 如果有子主题
			pyNode.showPlusIcon()						# 则强制显示“+”号


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def __setTopics( self ) :
		"""
		初始化所有帮助主题
		"""
		topics = systemHelper.getTopics()
		pyNodes = MapList()
		for topic in topics :
			pyNode = self.createRootTreeNode_( topic )
			self.pyTVTopic_.pyNodes.add( pyNode )
			if topic.children :
				pyNode.showPlusIcon()
			else :
				pyNode.showMinusIcon()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		"""
		当角色进入世界时被调用
		"""
		if self.pyTVTopic_.pyNodes.count :
			self.pyTVTopic_.pyNodes[1].selected = True

	def onLeaveWorld( self ) :
		"""
		当角色离开世界时被调用
		"""
		self.pyTVTopic_.collapseAll()
		self.pyTPContent_.text = ""
