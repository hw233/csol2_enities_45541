# -*- coding: gb18030 -*-
#
# $Id: Prompter.py,v 1.5 2008-08-04 10:23:28 huangyongwei Exp $

"""
implement search helper class.

2008.04.10: writen by huangyongwei
"""

from Helper import courseHelper
from guis import *
from guis.controls.TextBox import TextBox
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.ButtonEx import HButtonEx
from HelpPanel import HelpPanel
from Notifier import Notifier
from guis.controls.StaticText import StaticText
from LabelGather import labelGather


class Prompter( HelpPanel ) :
	def __init__( self, panel ) :
		HelpPanel.__init__( self, panel )
		self.pyTVTopic_.onTreeNodeBeforeExtend.bind( self.__onTopicBeforeExtend )
		self.pyTVTopic_.onTreeNodeCollapsed.bind( self.__onTopicCollapsed )
		self.__initialize( panel )
		self.__setTopics()

		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, panel ) :
		self.__pyCheckBox = CheckBoxEx( panel.cbPrompt )			# ͣ�ð�����ʾѡ���
		self.__pyCheckBox.onLClick.bind( self.__toggleTrigger )
		self.__pyCheckBox.checked = False

		self.__pyNextBtn = HButtonEx( panel.btnNext )					# ��һ����ʾ��ť
		self.__pyNextBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNextBtn.onLClick.bind( self.__onNextBtnClick )
		self.__pyNextBtn.enable = False

		self.__pyNotifier = Notifier()								# ��˸����ʾ����

		self.__pySTTpTitle = StaticText( panel.tpContent.bgTitle.stTitle )	# ָ�����ݱ���
		self.__pySTTvTitle = StaticText( panel.tvTopic.bgTitle.stTitle )	# ָ����Ŀ����
		self.__pySTText = StaticText( panel.cbPrompt.stext )				# "ֹͣ��ʾ"����

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyLabel( self.__pySTTpTitle, "HelpWindow:prompter", "rbTpTitle" )		# ָ������
		labelGather.setPyLabel( self.__pySTTvTitle, "HelpWindow:prompter", "rbTvTitle" )		# ָ����Ŀ
		labelGather.setPyLabel( self.__pySTText, "HelpWindow:prompter", "rbText" )				# ֹͣ��ʾ
		labelGather.setPyBgLabel( self.__pyNextBtn, "HelpWindow:prompter", "btnNext" )			# ��һ��


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_NEW_COURSE_HELP_ADDED"] = self.__onNewHelpAdded
		self.__triggers["EVT_ON_COURSE_HELP_TRIGGER_CHANGED"] = self.__onTriggerChanged
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def __setTopics( self ) :
		"""
		���ù̶������ж�������
		"""
		topics = courseHelper.getTopics()					# ��Щ�����Ǵ������ж�ȡ�ģ���ɫ��һ�ν�����Ϸʱ�ͼ���
		for topic in topics :
			pyNode = self.createRootTreeNode_( topic )		# ����һ���������ڵ�
			self.pyTVTopic_.pyNodes.add( pyNode )			# ����ӵ���������

	# -------------------------------------------------
	@staticmethod
	def __getTopicTree( topic ) :
		"""
		��ȡ���������������ʽΪ��[..., topic.grandsire, topic.parent, topic]
		"""
		tree = [topic]
		parent = topic.parent
		while parent :
			tree.insert( 0, parent )
			parent = parent.parent
		return tree

	@staticmethod
	def __getTopicNode( pyNodes, topic ) :
		"""
		ͨ����������ĸ�����ڵ㣬��ȡ���������Ӧ������ڵ�
		"""
		for pySubNode in pyNodes :
			if pySubNode.topic == topic :
				return pySubNode
		return None

	#��--------------------------------------
	@staticmethod
	def __getSubHistories( topic ) :
		"""
		��ȡĳ���������ʷ������
		"""
		subTopics = []
		histories = courseHelper.getHistories()
		for ch in topic.children :
			if ch in histories :
				subTopics.append( ch )
		return subTopics

	@staticmethod
	def __hasSubHistories( topic ) :
		"""
		�ж�ָ���ڵ��Ƿ�����ʷ�ӽڵ�
		"""
		histories = courseHelper.getHistories()							# ȫ����ʷ�ڵ�
		interset = set( topic.children ).intersection( histories )		# ����������������Ƿ�����ʷ�����н���
		return len( interset ) > 0										# �н���������ζ��ָ�������⣬������������ʷ����

	def __setSubHistryNodes( self, pyNode, topic = None ) :
		"""
		����ָ���ڵ��������ʷ�ӽڵ㣬��������ָ�������Ӧ��������ڵ�(��� topic ��Ϊ None)
		"""
		pyIndicateNode = None
		subTopics = self.__getSubHistories( pyNode.topic )				# ��ȡȫ���Ѿ���ʾ������ʷ������
		for subTopic in subTopics :
			pySubNode = self.createSubTreeNode_( subTopic )				# ����������
			pyNode.pyNodes.add( pySubNode )
			if self.__hasSubHistories( subTopic ) :						# �����������ڵ㻹����ʷ�ӽڵ�
				pySubNode.showPlusIcon()								# ����ʾ��+����
			else :														# ����
				pySubNode.showMinusIcon()								# ��ʾ��-����
			if topic == subTopic :
				pyIndicateNode = pySubNode
		return pyIndicateNode

	# -------------------------------------------------
	def __showFirstNewTopic( self ) :
		"""
		��ʾ������һ��������ʾ(�������һ������ť�󴥷�����������������ʾ��ťʱ����)
		"""
		firstNewTopic = courseHelper.getFirstNewHelp()				# ��ȡ��һ��������ʾ
		if firstNewTopic is None : return False
		courseHelper.sinkNewHelp( firstNewTopic )					# ����������ʾ������ʷ

		topicTree = self.__getTopicTree( firstNewTopic )			# ����������б����һ����������⣩
		pyNodes = self.pyTVTopic_.pyNodes							# ���ж���ڵ�
		for topic in topicTree :
			pyNode = self.__getTopicNode( pyNodes, topic )
			if pyNode is None :
				ERROR_MSG( "topic '%i' is not in course helper!" % firstNewTopic.id )
				return False
			if topic == firstNewTopic :								# ����Ǵ���������
				pyNode.selected = True								# ��ѡ������ڵ�
				return True
			if pyNode.isExtended :									# ��£��չ��
				pyNode.collapse()
			pyNode.extend()											# ע�⣺չ��ǰ�����Զ�����������ӽڵ�
			pyNodes = pyNode.pyNodes
		return True

	def __setNextBtnState( self ) :
		"""
		���� ��һҳ ��ť��״̬
		"""
		self.__pyNextBtn.enable = courseHelper.getFirstNewHelp() is not None
		if not self.__pyNextBtn.enable :
			self.__pyNotifier.hide()

	# -------------------------------------------------
	def __onTopicBeforeExtend( self, pyNode ) :
		"""
		ĳ������ڵ�չ��֮ǰ������
		"""
		pySelNode = self.__setSubHistryNodes( pyNode, self.selTopic_ )		# ������չ���ڵ��������ʷ�ӽڵ�
		if pySelNode :														# ���֮ǰѡ�еĽڵ���չ���Ľڵ���ӽڵ���
			pySelNode.selected = True										# �򣬼����øýڵ㴦��ѡ��״̬

	def __onTopicCollapsed( self, pyNode ) :
		"""
		�ڵ��£֮�󱻴���
		"""
		if pyNode.selected:
			pyNode.selected = False
		pyNode.pyNodes.clear()
		if self.__hasSubHistories( pyNode.topic ) :					# �����������
			pyNode.showPlusIcon()									# ��ǿ����ʾ��+����

	def __toggleTrigger( self ) :
		"""
		��/�رհ�������
		"""
		courseHelper.toggleTrigger()

	def __onNextBtnClick( self, pyBtn ) :
		"""
		��� ��һҳ ��ť
		"""
		self.__showFirstNewTopic()
		self.__setNextBtnState()

	# ---------------------------------------
	def __onNewHelpAdded( self, topic ) :
		"""
		��һ���µ���ʾ����������ú��������á�
		ע�⣺ֻ�Ǵ�������δ�鿴����˲���������ڵ㣬���ǶԱ���������ڵ�����Ƚڵ�ȫ���ɡ�-���Ÿ�Ϊ��+����
		"""
		topicTree = self.__getTopicTree( topic )				# ��ȡ������
		pyParNode = self.pyTVTopic_								# ����ĸ��ڵ�
		for topic in topicTree :
			pyNode = self.__getTopicNode( \
				pyParNode.pyNodes, topic )						# �����Ӧ�Ľڵ�
			if pyParNode.isExtended :							# ������ڵ㴦��չ��״̬��ֻ�а�������򿪣����ֶ�չ���Ż������������
				if pyNode is None :								# ����ڵ㲻����
					pyNode = self.createSubTreeNode_( topic )	# �򣬴�������ڵ�
				pyParNode = pyNode								# �����ڵ���ӽڵ�
			else :												# ������ڵ㲢�Ǵ���չ��״̬
				pyParNode.showPlusIcon()						# �򣬽�����ʾ��+����
				break											# ���˳�

		self.__setNextBtnState()								# ������һ������ť����Ϊ�ɵ��
#		if not self.__pyCheckBox.checked :						# �������ʾ���̰�����û�б�����
#			self.__pyNotifier.show()							# �򵯳��ʺ�

	def __onTriggerChanged( self, closed ) :
		"""
		���Ƿ񴥷����̰����ı�ʱ��������
		"""
		self.__pyCheckBox.checked = closed


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ) :
		"""
		����ҽ�����Ϸʱ������
		"""
		for pyNode in self.pyTVTopic_.pyNodes :
			pyNode.selected = False
			pyNode.pyNodes.clear()
			if self.__getSubHistories( pyNode.topic ) :	# ������ӽڵ�
				pyNode.showPlusIcon()					# ��ǿ����ʾ�Ӻ�
			else :										# ����
				pyNode.showMinusIcon()					# ǿ����ʾ����

	def onLeaveWorld( self ) :
		"""
		������뿪��Ϸʱ������
		"""
		for pyNode in self.pyTVTopic_.pyNodes :
			pyNode.pyNodes.clear()
		self.pyTPContent_.text = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showCourseHelp( self ) :
		"""
		�����˸��ť����ʾ���̰���
		"""
		self.pyTVTopic_.collapseAll()
		if not self.__showFirstNewTopic() :
			if self.pyTVTopic_.pyNodes.count > 0 :
				self.pyTVTopic_.pyNodes[0].selected = True
		self.__setNextBtnState()
