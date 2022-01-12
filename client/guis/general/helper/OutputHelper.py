# -*- coding: gb18030 -*-
#
# $Id: LevelHelper.py,fangpengjun Exp $

"""
implement level helper class.

"""

from guis import *
from HelpPanel import HelpPanel
from config.client.help.OutputHelpConfig import Datas as outputDatas
from guis.controls.TreeView import travelTreeNode
from guis.controls.StaticText import StaticText
from LabelGather import labelGather

class OutputHelper( HelpPanel ):
	def __init__( self, panel ):
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
		topics = []
		for index, data in outputDatas.items():
			if index == 0:continue
			title = data["OutPutDes"]
			content = data["Des"]
			topic = Topic( index, title, content )
			topics.append( topic )
		topics.sort( key = lambda topic : topic.index )
		pyNodes = MapList()
		for topic in topics :
			pyNode = self.createRootTreeNode_( topic )
			self.pyTVTopic_.pyNodes.add( pyNode )
			if len( topic.children ):
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
		if self.pyTVTopic_.pyNodes.count:
			self.pyTVTopic_.pyNodes[0].selected = True

	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		self.pyTVTopic_.collapseAll()
		self.pyTPContent_.text = ""

	def showOutput( self ):
		"""
		������ʾ
		"""
		pass

class Topic( object ) :
	"""
	�ڵ���Ϣ
	"""
	def __init__( self, index, title, content = "" ) :
		self.index = index
		self.title = title
		self.parent = None							# ������ڵ�
		self.children = []							# ������
		self.__parentID = -1
		self.content = content

	def addChild( self, topic ) :
		"""
		����ӽڵ�
		"""
		if topic not in self.children :
			self.children.append( topic )
			topic.parent = self