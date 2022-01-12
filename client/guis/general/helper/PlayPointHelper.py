# -*- coding: gb18030 -*-
#
# $Id: PlayPointHelper.py,fangpengjun Exp $

"""
implement play point helper class.

"""
from guis import *
from HelpPanel import HelpPanel
from config.client.help.PlayPointHelpConfig import Datas as pointDatas
from guis.controls.TreeView import travelTreeNode
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
from OutputHelper import Topic

class PlayPointHelper( HelpPanel ):
	def __init__( self, panel ):
		HelpPanel.__init__( self, panel )
		self.pyTVTopic_.onTreeNodeBeforeExtend.bind( self.__onTopicBeforeExtend )
		self.pyTVTopic_.onTreeNodeCollapsed.bind( self.__onTopicCollapsed )

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
		player = BigWorld.player()
		pLevel = player.getLevel()
		topics = []
		for level, content in pointDatas.items():
			if level > pLevel:break
			title = labelGather.getText( "HelpWindow:outputHelper", "level", level )
			topic = Topic( level, title, content )
			topics.append( topic )
		topics.sort( key = lambda topic : topic.index )
		pyNodes = MapList()
		justLevel = 0
		for topic in topics:
			if topic.index >= pLevel:
				justLevel = topic.index
				break
		if justLevel == 0 and len( topics ):
			justLevel = topics[-1].index
		for topic in topics :
			pyNode = self.createRootTreeNode_( topic )
			self.pyTVTopic_.pyNodes.add( pyNode )
			if len( topic.children ):
				pyNode.showPlusIcon()
			else :
				if pyNode.topic.index == justLevel:
					self.onTreeNodeSelected_( pyNode )
					pyNode.selected = True
				pyNode.showMinusIcon()

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		"""
		����ɫ��������ʱ������
		"""
		if self.pyTVTopic_.pyNodes.count:
			self.pyTVTopic_.pyNodes[0].selected = True

	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		self.pyTVTopic_.collapseAll()
		self.pyTPContent_.text = ""

	def showPlayPoint( self ):
		"""
		������ʾ
		"""
		self.pyTVTopic_.pyNodes.clear()
		self.__setTopics()

	def onLevelChange( self, oldLevel, newLevel ):
		"""
		��ɫ�ȼ��ı�ʱ������
		"""
		maxLevel = oldLevel
		if self.pyTVTopic_.pyNodes.count:
			maxLevel = self.pyTVTopic_.pyNodes[-1].topic.index
		topics = []
		for level in range( maxLevel+1, newLevel+1 ):
			content = pointDatas.get( level, None )
			if content is None:continue
			title = labelGather.getText( "HelpWindow:outputHelper", "level", level )
			topic = Topic( level, title, content )
			topics.append( topic )
		topics.sort( key = lambda topic : topic.index )
		justLevel = 0
		for topic in topics:
			if topic.index >= newLevel:
				justLevel = topic.index
				break
		if justLevel == 0 and len( topics ):
			justLevel = topics[-1].index
		for topic in topics :
			pyNode = self.createRootTreeNode_( topic )
			self.pyTVTopic_.pyNodes.add( pyNode )
			if pyNode.topic.index == justLevel:
				self.onTreeNodeSelected_( pyNode )
				pyNode.selected = True