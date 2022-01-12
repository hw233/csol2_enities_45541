# -*- coding: gb18030 -*-
#
# $Id: LevelHelper.py,fangpengjun Exp $

"""
implement level helper class.

"""
from guis import *
from HelpPanel import HelpPanel
from guis.controls.TreeView import travelTreeNode
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
from OutputHelper import Topic
from config.client.help.LevelHelpConfig import Datas as levelDatas
import csdefine
import csconst

class LevelHelper( HelpPanel ):

	pro_maps = {1:csdefine.CLASS_FIGHTER, 2:csdefine.CLASS_SWORDMAN, 3:csdefine.CLASS_ARCHER, 4:csdefine.CLASS_MAGE }

	def __init__( self, panel ):
		HelpPanel.__init__( self, panel )
		self.pyTVTopic_.onTreeNodeBeforeExtend.bind( self.__onTopicBeforeExtend )
		self.pyTVTopic_.onTreeNodeCollapsed.bind( self.__onTopicCollapsed )
#		self.__setTopics()

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
			if topic.index > BigWorld.player().getLevel():continue
			pyCH = self.createSubTreeNode_( topic )
			if pyCH.topic.index in [subNode.topic.index for subNode in pyNode.pyNodes ]:continue
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
		topicDict = {}
		pyNodes = MapList()
		player = BigWorld.player()
		proKey = player.getClass()
		chName = csconst.g_chs_class[proKey]
		for proKey, proData in levelDatas.items():
			title = proData["Profession"]
			if chName == title :
				proTopic = Topic( proKey, title )
				topicDict[proKey] = proTopic
				for level, proDes in proData["content"].items():
					title = labelGather.getText( "HelpWindow:levelHelper", "level", level )
					lTopic = Topic( level, title, proDes )
					proTopic.addChild( lTopic )
				proTopic.children.sort( key = lambda lTopic : lTopic.index )
		topics = topicDict.values()
		topics.sort( key = lambda topic : topic.index )
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
		self.__setTopics()
		if self.pyTVTopic_.pyNodes.count:
			self.pyTVTopic_.pyNodes[0].selected = True

	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		self.pyTVTopic_.collapseAll()
		self.pyTPContent_.text = ""
		self.pyTVTopic_.pyNodes.clear()

	def showLevelTips( self ):
		"""
		������ɫ��ǰ�ȼ���Ϣ
		"""
		player = BigWorld.player()
		proKey = player.getClass()
		level = player.getLevel()
		for pyProNode in self.pyTVTopic_.pyNodes:
			topic = pyProNode.topic
			pro = self.pro_maps.get( topic.index, -1 )
			if pro != proKey:continue
			self.pyTVTopic_.onTreeNodeSelected.shield()
			pyProNode.selected = True
			self.pyTVTopic_.onTreeNodeSelected.unshield()
			pyProNode.extend()
			for pyLVNode in pyProNode.pyNodes:
				if pyLVNode.topic.index == level:
					self.onTreeNodeSelected_( pyLVNode )
					pyLVNode.selected = True
					break

	def onLevelChange( self, oldLevel, newLevel ):
		"""
		��ɫ�ȼ��ı�ʱ������
		"""
		player = BigWorld.player()
		proKey = player.getClass()
		pyCurNode = self.pyTVTopic_.pyNodes[0]
		for pyProNode in self.pyTVTopic_.pyNodes:
			topic = pyProNode.topic
			pro = self.pro_maps.get( topic.index, -1 )
			if pro != proKey:continue
			pyCurNode = pyProNode
		if pyCurNode.isExtended:
			topic = pyCurNode.topic
			lstIndex = pyCurNode.pyNodes[-1].topic.index
			for chidTopic in topic.children:
				childIndex = chidTopic.index
				if childIndex <= newLevel and childIndex > lstIndex:
					pyNode = self.createSubTreeNode_( chidTopic )
					pyCurNode.pyNodes.add( pyNode )
			for pyNode in pyCurNode.pyNodes:
				if newLevel == pyNode.topic.index:
					self.onTreeNodeSelected_( pyNode )
					pyNode.selected = True
					break