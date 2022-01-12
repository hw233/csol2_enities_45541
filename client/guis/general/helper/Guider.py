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

		self.__pySTTpTitle = StaticText( panel.tpContent.bgTitle.stTitle )	# ָ�����ݱ���
		self.__pySTTvTitle = StaticText( panel.tvTopic.bgTitle.stTitle )	# ָ����Ŀ����

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyLabel( self.__pySTTpTitle, "HelpWindow:guider", "rbTpTitle" )	# ָ������
		labelGather.setPyLabel( self.__pySTTvTitle, "HelpWindow:guider", "rbTvTitle" )	# ָ����Ŀ


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onTopicBeforeExtend( self, pyNode ) :
		"""
		ĳ������ڵ�չ��֮ǰ������
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
		�ڵ����֮�󱻴���
		"""
		if pyNode.selected :
			pyNode.selected = False
		pyNode.pyNodes.clear()
		if len( pyNode.topic.children ) > 0 :			# �����������
			pyNode.showPlusIcon()						# ��ǿ����ʾ��+����


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def __setTopics( self ) :
		"""
		��ʼ�����а�������
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
		����ɫ��������ʱ������
		"""
		if self.pyTVTopic_.pyNodes.count :
			self.pyTVTopic_.pyNodes[1].selected = True

	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		self.pyTVTopic_.collapseAll()
		self.pyTPContent_.text = ""
