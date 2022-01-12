# -*- coding: gb18030 -*-
#
#$Id: TypeNode.py,v 1.16 2008-08-25 07:07:01 huangyongwei Exp $
#

"""
implement friendnode item class
"""
from guis import *
from guis.controls.TreeView import TreeNode
from QuestNode import QuestNode
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import GUIFacade
import csdefine
import Const
import Font

class TypeNode( TreeNode ):
	def __init__( self, typeID, pyBinder = None):
		node = GUI.load( "guis/general/questlist/node.gui" )
		uiFixer.firstLoadFix( node )
		TreeNode.__init__( self, node, pyBinder = pyBinder )
		self.autoWidth = False
		self.focus = True
		self.crossFocus = True
		self.selectable = True
		self.font = "STLITI.TTF"
		self.fontSize = 16.0
		self.commonForeColor = ( 231, 205, 140, 255 )
		self.highlightForeColor = ( 231, 205, 140, 255 )
		self.selectedForeColor = ( 231, 205, 140, 255 )
		self.limning = Font.LIMN_OUT
		self.limnColor = (0, 0, 0, 255 )
		self.__pyHooker = PyGUI( node.hook )
		self.__pyHooker.visible = False
		self.__pyNodeBg = PyGUI( node.nodeBg )
		self.__pyNodeBg.visible = False
		self.__typeID = typeID
		self.__quests = {} # �����ӽ��
		self.itemInfo = None
		self.__pyIsComp = None

	# -----------------------------------------
	# private
	# -----------------------------------------
	def __analyzeQuest( self, questID, itemInfo ) : # ��ȡ�����µ�״̬
		# name & level & degree
		itemInfo.name, itemInfo.level = GUIFacade.getQuestLogTitle( questID )
		# quest content
		detailText, objectiveText = GUIFacade.getQuestLogQuestText( questID )
		itemInfo.content = detailText
		itemInfo.objectText = objectiveText
		# if quest is strFinished & condition
		itemInfo.state = True
		# rewards
		args = GUIFacade.getObjectiveDetail( questID )
		maxCompleteCount = len( args )
		completeCount = 0
		resultText = "" #����״̬
		taskTimeIndex = -1
		taskTimeFinish = False
		completeRuleType = GUIFacade.getCompleteRuleType( questID )
		for taskType, index, title, tag, isCollapsed, isComplete, itemID,showOrder, npcID in args :
			stateText = "" #ÿ������״̬
			if taskType == csdefine.QUEST_OBJECTIVE_TIME:
				stateText = ""
				completeCount += 1
				taskTimeIndex = index
			else:
				if isComplete :
					if taskType == csdefine.QUEST_OBJECTIVE_DART_KILL:
						# ��������ǿ�����
						taskTimeFinish = True
					stateText = labelGather.getText( "QuestHelp:typeNode", "stComplete" )
					completeCount += 1
				else:
					stateText = PL_Font.getSource( labelGather.getText( "QuestHelp:typeNode", "stUncomplete" ), fc = ( 255, 0, 0 ))
					tag = PL_Font.getSource( tag, fc = ( 255, 0, 0 ))
			if isCollapsed : #ʧ��
				resultText = labelGather.getText( "QuestHelp:typeNode", "stCollapsed" )
				stateText = PL_Font.getSource( labelGather.getText( "QuestHelp:typeNode", "stCollapsed" ),fc = ( 255,0,0) )
				tag = PL_Font.getSource( tag, fc =( 255, 0, 0))
			forceTips = ""
			if completeRuleType == csdefine.QUEST_COMPLETE_RULE_PART_TASK_COM:
				forceTips = labelGather.getText( "QuestHelp:typeNode", "forceTips" )
			itemInfo.conditions[index] = {"title" : title, "tag": tag, "stateText": stateText, "forceTips":forceTips } #ÿ��������״̬
			
		itemInfo.resultText = resultText #ֻ��������ʧ�ܲŸ�ֵ
		itemInfo.state = maxCompleteCount == completeCount #�Ƿ����
		if taskTimeFinish and taskTimeIndex != -1:
			itemInfo.resultText = labelGather.getText( "QuestHelp:typeNode", "stComplete" )
			itemInfo.conditions[taskTimeIndex]["stateText"] =  labelGather.getText( "QuestHelp:typeNode", "stComplete" )
			itemInfo.state = True
		return itemInfo

	# -----------------------------------------
	# public
	# -----------------------------------------
	def onQuestAdded( self, questID ):
		if questID in self.__quests:return #�����ظ����
		itemInfo = QuestItemInfo( questID )
		questNode = QuestNode( self.pyBinder )
		questNode.viewTextNum = 17
		newItemInfo = self.__analyzeQuest( questID, itemInfo ) # ��������״̬
		questNode.showPlusMinus = False
		questNode.crossFocus = True
		questNode.selected = False
		questNode.itemInfo = newItemInfo
		questNode.itemInfo.level = GUIFacade.getQuestLogTitle( questID )[ 1 ]	# wsf���������ĵȼ���Ϣ�Ա�����
		showLevel = GUIFacade.getQuestShowLevelByID( questID, newItemInfo.level )
		questNode.text ="(%d)%s"%( showLevel, newItemInfo.name )
		if newItemInfo.resultText != "": #����ʧ��
			questNode.text += "(%s)"% newItemInfo.resultText
			questNode.isComp = False
		else:
			state = newItemInfo.state
			if state:
				questNode.text += labelGather.getText( "QuestHelp:typeNode", "stComplete_2" )
				questNode.isComp = True
			else:
				questNode.text += labelGather.getText( "QuestHelp:typeNode", "stUncomplete_2" )

		# �������񼶱����ɫ������������ɫ
		temp =  itemInfo.level - BigWorld.player().level
		if temp <= -5:
			tempColor = ( 51, 76, 97, 255 )	#��ɫ
		elif temp> -5 and temp <= 0:
			tempColor = ( 255, 255, 255, 255 )	#��ɫ
		elif temp > 0 and temp <=3:
			tempColor = ( 255, 127, 0, 255 ) #��ɫ
		else:
			tempColor = ( 193, 23, 0, 255 ) #��ɫ
		questNode.commonForeColor = tempColor
		questNode.highlightForeColor = tempColor
		questNode.foreColor = questNode.commonForeColor

		self.__quests[questID] = questNode
#		self.__addResortNode( questNode ) # ��������ӽ��
		self.pyNodes.add( questNode )
		self.pyNodes.sort( key = lambda questNode : questNode.itemInfo.level )
		self.pyBinder.onNodeAdd( questID )
		questNode.selected = True									# ѡ�и���ӵ�����

	def __addResortNode( self, questNode ): # *��Ӳ�����
		if self.pyNodes.count <= 0:
			self.pyNodes.add( questNode )
		tempLevel = questNode.itemInfo.level
		for index, existNode in enumerate( self.pyNodes ):
			if existNode.itemInfo.level > tempLevel:
				self.pyNodes.insert( index,questNode )
			else:
				self.pyNodes.add( questNode )
				return
#				if existNode.itemInfo.level > tempLevel and self.pyNodes[index-1].itemInfo.level <= tempLevel:
#					self.pyNodes.insert( index, questNode )
#					return

	def onQuestRemoved( self, questID ):
		if not self.__quests.has_key( questID ):
			return
		questNode = self.__quests.pop( questID )
		self.pyNodes.remove( questNode )
#		questNode.isTraced = False
		if self.pyNodes.count <= 0: #�ӽ��Ϊ�գ��������Լ�
			if self.__typeID in [102, 201, 202]: #��Ϊ3��һֱ��������Ͳ�����
				return
			self.dispose()

	def onQuestStateChanged( self, questID ):
		if self.__quests.has_key( questID ):
			questNode = self.__quests[questID]
			newItemInfo = self.__analyzeQuest( questID, questNode.itemInfo )
			questNode.itemInfo = newItemInfo
#			questNode.state = newItemInfo.state
			showLevel = GUIFacade.getQuestShowLevelByID( questID, newItemInfo.level )
			questNode.text = "(%d)%s"%( showLevel, newItemInfo.name )
			if newItemInfo.resultText != "": #����ʧ��
				questNode.text += "(%s)"% newItemInfo.resultText
				questNode.isComp = False
			else:
				state = newItemInfo.state
				if state:
					questNode.text += labelGather.getText( "QuestHelp:typeNode", "stComplete_2" )
					questNode.isComp = True
				else:
					questNode.text += labelGather.getText( "QuestHelp:typeNode", "stUncomplete_2" )

	def onQuestSelected( self, questID ):
		if self.__quests.has_key( questID ):
			questNode = self.__quests[questID]
			itemInfo = questNode.itemInfo
			newItemInfo = self.__analyzeQuest( questID, itemInfo )
#			questNode.state = itemInfo.state
			return newItemInfo

	def getQuestItemInfo( self, questID ):
		if self.__quests.has_key( questID ):
			questNode = self.__quests[questID]
			itemInfo = questNode.itemInfo
			return 	itemInfo

	#	 ---------------------------------------------
	#	 property methods
	#	 ---------------------------------------------
	def _setForeColor( self, color ) : #�������;�����ɫ
		TreeNode._setForeColor( self, color )
#		self.__pyLbLevel.color = color
#		self.__pyLbOption.color = color

	def _getForeColor( self ):
		TreeNode._getForeColor( self )
#		return self.__pyLbLevel.color

	def _setTypeID( self, id ):
		self.__typeID = id

	def _getTypeID( self ):
		return self.__typeID
		
	def _getQuests( self ):
		return self.__quests

	foreColor = property( _getForeColor, _setForeColor )
	typeID = property( _getTypeID, _setTypeID )
	quests = property( _getQuests )

# --------------------------------------------------------------------
# quest item info
# --------------------------------------------------------------------
class QuestItemInfo :
	def __init__( self, questID ) :
		self.id = questID			# quest id
		self.name = ""				# quest name
		self.level = 0				# quest level
		self.state = False			# has finish or not
#		self.degree = 0				# coefficient of difficulty
		self.content = ""			# content of quest
		self.conditions = {}		# conditions of quest
		self.objectText = ""		# object of quest
		self.plize = ""				# plize of quest
		self.type = -1				# type of quest
		self.resultText = ""		# ״̬�����ֶ�