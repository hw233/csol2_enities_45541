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
		self.__pyCheckBox = CheckBoxEx( panel.cbPrompt )			# 停用帮助提示选择框
		self.__pyCheckBox.onLClick.bind( self.__toggleTrigger )
		self.__pyCheckBox.checked = False

		self.__pyNextBtn = HButtonEx( panel.btnNext )					# 下一条提示按钮
		self.__pyNextBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNextBtn.onLClick.bind( self.__onNextBtnClick )
		self.__pyNextBtn.enable = False

		self.__pyNotifier = Notifier()								# 闪烁的提示符号

		self.__pySTTpTitle = StaticText( panel.tpContent.bgTitle.stTitle )	# 指引内容标题
		self.__pySTTvTitle = StaticText( panel.tvTopic.bgTitle.stTitle )	# 指引条目标题
		self.__pySTText = StaticText( panel.cbPrompt.stext )				# "停止提示"文字

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyLabel( self.__pySTTpTitle, "HelpWindow:prompter", "rbTpTitle" )		# 指引内容
		labelGather.setPyLabel( self.__pySTTvTitle, "HelpWindow:prompter", "rbTvTitle" )		# 指引条目
		labelGather.setPyLabel( self.__pySTText, "HelpWindow:prompter", "rbText" )				# 停止提示
		labelGather.setPyBgLabel( self.__pyNextBtn, "HelpWindow:prompter", "btnNext" )			# 下一条


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
		设置固定的所有顶层主题
		"""
		topics = courseHelper.getTopics()					# 这些主题是从配置中读取的，角色第一次进入游戏时就加载
		for topic in topics :
			pyNode = self.createRootTreeNode_( topic )		# 创建一个主题树节点
			self.pyTVTopic_.pyNodes.add( pyNode )			# 并添加到树版面上

	# -------------------------------------------------
	@staticmethod
	def __getTopicTree( topic ) :
		"""
		获取主题的祖先树，格式为：[..., topic.grandsire, topic.parent, topic]
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
		通过帮助主题的父主题节点，获取帮助主题对应的主题节点
		"""
		for pySubNode in pyNodes :
			if pySubNode.topic == topic :
				return pySubNode
		return None

	#　--------------------------------------
	@staticmethod
	def __getSubHistories( topic ) :
		"""
		获取某个主题的历史子主题
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
		判断指定节点是否有历史子节点
		"""
		histories = courseHelper.getHistories()							# 全部历史节点
		interset = set( topic.children ).intersection( histories )		# 给定主题的子主题是否与历史主题有交集
		return len( interset ) > 0										# 有交集，则意味着指定的主题，其子主题有历史主题

	def __setSubHistryNodes( self, pyNode, topic = None ) :
		"""
		设置指定节点的所有历史子节点，并返回与指定主题对应的子主题节点(如果 topic 不为 None)
		"""
		pyIndicateNode = None
		subTopics = self.__getSubHistories( pyNode.topic )				# 获取全部已经提示过的历史子主题
		for subTopic in subTopics :
			pySubNode = self.createSubTreeNode_( subTopic )				# 创建子主题
			pyNode.pyNodes.add( pySubNode )
			if self.__hasSubHistories( subTopic ) :						# 如果该子主题节点还有历史子节点
				pySubNode.showPlusIcon()								# 则，显示“+”号
			else :														# 否则
				pySubNode.showMinusIcon()								# 显示“-”号
			if topic == subTopic :
				pyIndicateNode = pySubNode
		return pyIndicateNode

	# -------------------------------------------------
	def __showFirstNewTopic( self ) :
		"""
		显示最上面一条帮助提示(点击“下一条”按钮后触发，或点击“？”号提示按钮时触发)
		"""
		firstNewTopic = courseHelper.getFirstNewHelp()				# 获取第一条帮助提示
		if firstNewTopic is None : return False
		courseHelper.sinkNewHelp( firstNewTopic )					# 将看过的提示存入历史

		topicTree = self.__getTopicTree( firstNewTopic )			# 主题的祖先列表（最后一个是最顶层主题）
		pyNodes = self.pyTVTopic_.pyNodes							# 所有顶层节点
		for topic in topicTree :
			pyNode = self.__getTopicNode( pyNodes, topic )
			if pyNode is None :
				ERROR_MSG( "topic '%i' is not in course helper!" % firstNewTopic.id )
				return False
			if topic == firstNewTopic :								# 如果是触发的主题
				pyNode.selected = True								# 则选中这个节点
				return True
			if pyNode.isExtended :									# 合拢再展开
				pyNode.collapse()
			pyNode.extend()											# 注意：展开前，会自动添加其所有子节点
			pyNodes = pyNode.pyNodes
		return True

	def __setNextBtnState( self ) :
		"""
		设置 下一页 按钮的状态
		"""
		self.__pyNextBtn.enable = courseHelper.getFirstNewHelp() is not None
		if not self.__pyNextBtn.enable :
			self.__pyNotifier.hide()

	# -------------------------------------------------
	def __onTopicBeforeExtend( self, pyNode ) :
		"""
		某个主题节点展开之前被触发
		"""
		pySelNode = self.__setSubHistryNodes( pyNode, self.selTopic_ )		# 创建被展开节点的所有历史子节点
		if pySelNode :														# 如果之前选中的节点在展开的节点的子节点中
			pySelNode.selected = True										# 则，继续让该节点处于选中状态

	def __onTopicCollapsed( self, pyNode ) :
		"""
		节点合拢之后被触发
		"""
		if pyNode.selected:
			pyNode.selected = False
		pyNode.pyNodes.clear()
		if self.__hasSubHistories( pyNode.topic ) :					# 如果有子主题
			pyNode.showPlusIcon()									# 则强制显示“+”号

	def __toggleTrigger( self ) :
		"""
		打开/关闭帮助触发
		"""
		courseHelper.toggleTrigger()

	def __onNextBtnClick( self, pyBtn ) :
		"""
		点击 下一页 按钮
		"""
		self.__showFirstNewTopic()
		self.__setNextBtnState()

	# ---------------------------------------
	def __onNewHelpAdded( self, topic ) :
		"""
		当一个新的提示被触发，则该函数被调用。
		注意：只是触发，并未查看，因此不创建主题节点，而是对被触发主题节点的祖先节点全部由“-”号改为“+”号
		"""
		topicTree = self.__getTopicTree( topic )				# 获取主题树
		pyParNode = self.pyTVTopic_								# 主题的父节点
		for topic in topicTree :
			pyNode = self.__getTopicNode( \
				pyParNode.pyNodes, topic )						# 主题对应的节点
			if pyParNode.isExtended :							# 如果父节点处于展开状态（只有帮助界面打开，并手动展开才会有这种情况）
				if pyNode is None :								# 如果节点不存在
					pyNode = self.createSubTreeNode_( topic )	# 则，创建这个节点
				pyParNode = pyNode								# 继续节点的子节点
			else :												# 如果父节点并非处于展开状态
				pyParNode.showPlusIcon()						# 则，仅仅显示“+”号
				break											# 并退出

		self.__setNextBtnState()								# 将“下一条”按钮设置为可点击
#		if not self.__pyCheckBox.checked :						# 如果“显示过程帮助”没有被屏蔽
#			self.__pyNotifier.show()							# 则弹出问号

	def __onTriggerChanged( self, closed ) :
		"""
		当是否触发过程帮助改变时，被调用
		"""
		self.__pyCheckBox.checked = closed


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ) :
		"""
		当玩家进入游戏时被调用
		"""
		for pyNode in self.pyTVTopic_.pyNodes :
			pyNode.selected = False
			pyNode.pyNodes.clear()
			if self.__getSubHistories( pyNode.topic ) :	# 如果有子节点
				pyNode.showPlusIcon()					# 则强制显示加号
			else :										# 否则
				pyNode.showMinusIcon()					# 强制显示减号

	def onLeaveWorld( self ) :
		"""
		当玩家离开游戏时被调用
		"""
		for pyNode in self.pyTVTopic_.pyNodes :
			pyNode.pyNodes.clear()
		self.pyTPContent_.text = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showCourseHelp( self ) :
		"""
		点击闪烁按钮后，显示过程帮助
		"""
		self.pyTVTopic_.collapseAll()
		if not self.__showFirstNewTopic() :
			if self.pyTVTopic_.pyNodes.count > 0 :
				self.pyTVTopic_.pyNodes[0].selected = True
		self.__setNextBtnState()
