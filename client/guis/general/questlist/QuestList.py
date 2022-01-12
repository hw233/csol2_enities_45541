# -*- coding: gb18030 -*-
#
# $Id: QuestList.py,v 1.67 2008-09-02 01:00:40 songpeifang Exp $

"""
implement quest list class
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.ButtonEx import HButtonEx
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.controls.StaticText import StaticText
from QuestTrace import QuestTraceWindow
from DspPanel import DspPanel
from TypeNode import TypeNode
from QuestNotifier import NewQuestNotifier, CommitNotifier
from ContentPanel import ContentPanel
import csdefine
import csstatus
import event.EventCenter as ECenter
import GUIFacade
import Timer
import BigWorld
import Const
from config.client.msgboxtexts import Datas as mbmsgs
from config.client.RemindEffQuestID import Datas as effQuestID
import Define

MAX_TRACE_QUEST_NUM = 20 # �߻�Ҫ������׷���޴������ƣ������Ȱ�׷�����Ƹ�Ϊ���ɽ�������


class QuestList( TabPanel ):

	_commit_direct_quest_type = 901	# ��ֱ���ύ����������
	_casual_ids = [901,902]			# �����������
	_ring_ids = [301,302,305,306] # ����������
	_const_ids = [102, 201, 202] #Ĭ��һֱ��ʾ��3������

	def __init__( self, panel = None, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )

		self.__questUpdateTimeID = 0
		self.__questItems = []			# wsf��list of pyItem������ѡ���б�
		self.__typeNodes = {} # �������ͽڵ�
		self.__checkTraced = True
		self.startAdd = True 			#�ǲ���һ��ʼ�ͼ����������־(��Ҫ��Ϊ�˴������������ʾ)
		self.__questID = 0				#��ǰ����ID
		self.__isLogInited = False
		self.__triggers = {}
		self.__registerTriggers()
		self.traceQuestList	= []		# wsf,����׷�ٵ������б�
		self.__effectTop = 0			#�������Ч�����ѵ�����λ��
		self.effectTime = 3			# �������Ч�����ŵĳ���ʱ��
		self.effectTimer = 0
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		labelGather.setLabel( panel.stQuests, "QuestHelp:QuestList", "questList" )
		self.__pyTVQuets = TreeView( panel.tvQuests, panel.vSBQuests ) # ��������ͼ
		self.__pyTVQuets.nodeOffset = 0
		self.__pyTVQuets.onTreeNodeSelected.bind( self.__onQuestSelected )

		self.__pyContentPanel = ContentPanel( panel.contentPanel.clipPanel,panel.contentPanel.sbar)

		self.__pyBtnTrace = HButtonEx( panel.btnTrace ) # ����׷�ٰ�ť
		self.__pyBtnTrace.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTrace.commonForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnTrace.highlightForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnTrace.selectedForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnTrace.onLClick.bind( self.__onTraceQuest )
		self.__pyBtnTrace.enable = False
		labelGather.setPyBgLabel( self.__pyBtnTrace, "QuestHelp:QuestList", "btnTrace" )
		self.__pyBtnTrace.font = "MSYHBD.TTF"

		self.__pyBtnAbandon = HButtonEx( panel.btnAbandon ) # ���������ť
		self.__pyBtnAbandon.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnAbandon.commonForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnAbandon.highlightForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnAbandon.selectedForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnAbandon.onLClick.bind( self.__onAbandonQuest )
		self.__pyBtnAbandon.enable = False
		labelGather.setPyBgLabel( self.__pyBtnAbandon, "QuestHelp:QuestList", "btnAbandon" )
		self.__pyBtnAbandon.font = "MSYHBD.TTF"

		self.__pyBtnCommit = HButtonEx( panel.btnCommit )					# �������ť�������ύ��ֱ����ɣ�����ͨ��NPC�Ի�������
		self.__pyBtnCommit.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCommit.commonForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnCommit.highlightForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnCommit.selectedForeColor = ( 252, 235, 179, 255 )
		self.__pyBtnCommit.onLClick.bind( self.__onCasualQuestCommit )
		self.__pyBtnCommit.visible = False
		labelGather.setPyBgLabel( self.__pyBtnCommit, "QuestHelp:QuestList", "btnCommit" )
		self.__pyBtnCommit.font = "MSYHBD.TTF"
		
		self.__circleEff = PyGUI( panel.circleEff )
		self.__circleEff.visible = 0
		
		self.__blastEff = PyGUI( panel.blastEff )
		self.__blastEff.visible = 0
		
		twnd = GUI.load( "guis/general/questlist/questtrace/traceWindow.gui" )
		uiFixer.firstLoadFix( twnd )
		self.traceWindow = QuestTraceWindow( twnd, self )
		GUI.addRoot( twnd )

		self.__pyCheckBox = CheckBoxEx( panel.ckTrace ) # �Ƿ���ʾ����׷�ٴ���
		self.__pyCheckBox.onCheckChanged.bind( self.__onCheckTrace )
		self.__pyCheckBox.checked = True
		labelGather.setPyLabel( self.__pyCheckBox.pyText_, "QuestHelp:QuestList", "questTrace" )

		self.__pyQuestNum = StaticText( panel.stNumber )
		self.__pyQuestNum.font = "MSYHBD.TTF"
		self.__pyQuestNum.fontSize = 12.0
		self.__pyQuestNum.text = "0/20"
		

		self.__pyNotifierNew = NewQuestNotifier()
		self.__pyNotifierCommit = CommitNotifier()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUEST_LOG_ADD"] = self.__onQuestAdd
		self.__triggers["EVT_ON_QUEST_LOG_REMOVED"] = self.__onQuestRemove
		self.__triggers["EVT_ON_QUEST_TASK_STATE_CHANGED"] = self.__onQuestStateChagned
		self.__triggers["EVT_ON_QUEST_LOG_SELECTED"] = self.__selectedQuest
		self.__triggers["EVT_ON_QUEST_REWARDS_CHANGED"] = self.__onQuestRewardChanged
		self.__triggers["EVT_ON_ACCEPT_TRUE"] = self.__onAcceptTrue
		self.__triggers["EVT_ON_INVITE_FAMILY_DART"] = self.__onInviteFamilyDart
		self.__triggers["EVT_ON_LOOP_GROUP_READ_RECORD"] = self.__onLoopGroupReadRecord
		self.__triggers["EVT_ON_ACCEPT_QUEST_CONFIRM"] = self.__onAcceptQuestConfirm
		self.__triggers["EVT_ON_ROLE_QUESTLOG_INITED"] = self.__onQtLogInited
		self.__triggers["EVT_ON_TRAP_QUEST_TIP_SHOW"] = self.__onTrapQuestTipShow
		self.__triggers["EVT_ON_TRAP_QUEST_TIP_HIDE"] = self.__onTrapQuestTipHide
		self.__triggers["EVT_ON_PLAY_QUEST_EFFECT"] = self.__onPLayQuestEff
		self.__triggers["EVT_ON_QUEST_COMPLETED"] = self.__onQuestCompleted
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# ------------------------------------------------------------------------
	def __addRewardInfos( self, questID ) : # ��Ӹ��ֽ���
		self.__pyContentPanel.addRewards( questID )
		

	# ------------------------------------------------------------------------
	def __onQuestAdd( self, questID ) :
		"""
		�������ڵ�,��������������������ڵ�
		"""
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		elif typeID in self._casual_ids :
			typeID = self._casual_ids[0]
		typeNode = self.__typeNodes.get( typeID )
		if typeNode is None :
			typeNode = TypeNode( typeID, self )
			typeNode.selectable = False
			typeNode.nodeOffset = 0.0
			typeNode.text = typeStr
			self.__pyTVQuets.pyNodes.add( typeNode )
			self.__pyTVQuets.pyNodes.sort( key = lambda pyNode : pyNode.typeID )
			typeNode.extend()
			self.__typeNodes[typeID] = typeNode
		self.__pyQuestNum.text = "%d/%d"%( len( GUIFacade.getQuestLogs() ), 20 )
		typeNode.onQuestAdded( questID )
		if not typeNode.isExtended :
			typeNode.extend()
		ECenter.fireEvent( "EVT_ON_QUEST_CAN_ACCEPT_REMOVE", questID ) #�ӿɽ�������ɾ��
		# ��ʱ��׷�������Զ���ӵ�����׷�ٴ���
		pySelNode = self.__pyTVQuets.pySelNode
		if pySelNode is None:return
		if self.__isTraceQuest( pySelNode.itemInfo.id ):
			self.__pyCheckBox._setChecked( True )
			self.__onCheckTrace( True )
			self.__onTraceQuest()

	def __onQuestRemove( self, questID ) :
		"""
		 �Ƴ�ĳ������
		"""
		if GUIFacade.getQuestLogSelection() == questID :#��ǰѡ��ڵ���ɾ���ڵ���ͬ
			self.__pyBtnCommit.visible = False
			self.__pyContentPanel.clearItems()
			self.__pyBtnAbandon.enable = False
			self.__pyBtnTrace.enable = False
			if self.__questUpdateTimeID != 0:
				self.__closeQuestTimer()
		for temp in self.__questItems:	# wsf���Ƴ�����ʱ����self.__questItems
			if temp.itemInfo.id == questID:
				self.__questItems.remove( temp )
				break
		if questID in self.traceQuestList:
			self.traceQuestList.remove( questID )
		typeID = GUIFacade.getQuestTypeStr( questID )[0]
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		elif typeID in self._casual_ids :
			self.__pyNotifierCommit.shutdown( questID )					# �����������ʾ���Ƴ�
			typeID = self._casual_ids[0]
		typeNode = self.__typeNodes.get( typeID )
		typeNode.onQuestRemoved( questID )
		self.__pyQuestNum.text = "%d/%d"%( len( GUIFacade.getQuestLogs() ), 20 )
		if typeNode.pyNodes.count <= 0:
			typeID = typeNode.typeID
			if typeID in self._const_ids:return
			del self.__typeNodes[typeID]

	def __onQuestStateChagned( self, questID, taskIndex ) :
		"""
		ĳ�������״̬�ı����
		"""
		typeID = GUIFacade.getQuestTypeStr( questID )[0]
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		elif typeID in self._casual_ids :
			if typeID == self._commit_direct_quest_type :
				isQuestCompleted = GUIFacade.questIsCompleted( questID )
				if self.__pyBtnCommit.visible :
					self.__pyBtnCommit.enable = isQuestCompleted
				if isQuestCompleted :											# ���������������������
					self.__pyNotifierCommit.notify( questID )					# ����ӵ����������ʾ��
				else :															# ����
					self.__pyNotifierCommit.shutdown( questID )					# �����������ʾ���Ƴ�
			typeID = self._casual_ids[0]
		typeNode = self.__typeNodes.get( typeID )
		if typeNode is None:return
		typeNode.onQuestStateChanged( questID )									# ����״̬��Ϣ

		questInfo = typeNode.getQuestItemInfo( questID )
		if questInfo is None : return
		nowQuestID = GUIFacade.getQuestLogSelection()							# ��ǰ��ʾ������
		if nowQuestID == questID :
			self.__pyContentPanel.pyQTCondition.resetFinishState( questInfo.conditions )		# ˢ�����������Ϣ

		if questID not in self.traceQuestList and self.__checkTraced and \
		self.traceWindow.autoQuestTrace( questID ) and self.__isAddSucced( questID ):							# ����׷��
			self.traceQuestList.append( questID )
		if questID in self.traceQuestList:
			self.traceWindow.onQuestStateChagned( questID )
		if questID == self.__pyTVQuets.pySelNode.itemInfo.id:
			self.__selectedQuest( questID )	
#		self.__onQuestRewardChanged( questID )
			#Ŀǰ��������������ɺ�ɾ��������������ɾ��
#		self.__pyContentPanel.layOut()	
		

	def __selectedQuest( self, questID, isTraceSelect = False ) :
		"""
		ѡ��ĳ�������ѯ
		"""
		self.__questID = questID
		self.__pyContentPanel.clearItems()
		itemInfo = None
		typeID = GUIFacade.getQuestTypeStr( questID )[0]
		self.__pyBtnCommit.visible = typeID == self._commit_direct_quest_type
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		elif typeID in self._casual_ids :
			self.__pyBtnCommit.enable = GUIFacade.questIsCompleted( questID )
			typeID = self._casual_ids[0]
		typeNode = self.__typeNodes.get( typeID )
		if typeNode is not None :
			itemInfo = typeNode.onQuestSelected( questID )
			content = PL_Font.getSource( itemInfo.content, fc = ( 51, 76, 97, 255 ) )
			self.__pyContentPanel.addTitle( itemInfo.name )
			self.__pyContentPanel.addCondition( questID, itemInfo )
			self.__pyContentPanel.addContext( content )
			
		try :
			self.__addRewardInfos( questID )
		except : pass
		self.__checkQuestTimer( questID )
		self.__pyBtnAbandon.enable = itemInfo is not None
		self.__pyBtnTrace.enable = itemInfo is not None
		if isTraceSelect and typeNode:
			for questNode in typeNode.pyNodes: # �ڵ㴦�Զ�ѡ�е�ǰѡ�������
				# pySelNode��������裬����Ӷ�Щ�жϻᱣ��һ��  --pj
				if questNode and questNode.itemInfo and questNode.itemInfo.id == questID and self.__pyTVQuets.pySelNode != questNode:
					self.__pyTVQuets.pySelNode = questNode
					break

	def __onQuestRewardChanged( self, questID ):
		"""
		ĳ���������ı����
		"""
		if questID == self.__pyTVQuets.pySelNode.itemInfo.id :
			self.__addRewardInfos( questID )

	def __onQtLogInited( self ):
		self.__isLogInited = True
		self.traceWindow.isLogInited = True
		tcQuests = self.traceWindow.TQuestIDList
		self.traceWindow.visible = len(tcQuests) > 0
		self.__pyCheckBox.checked = len(tcQuests) > 0

	def __onTrapQuestTipShow( self, questId ) :
		"""�������������ɽ�"""
		self.__pyNotifierNew.notify( questId )

	def __onTrapQuestTipHide( self, questId ) :
		"""�������������ɽ�"""
		self.__pyNotifierNew.shutdown( questId )
		
	def __onPLayQuestEff( self, questID ):
		"""
		����Ч��
		"""
		self.__searchQuestHeith( questID )

	def __onQuestCompleted( self ):
		rds.soundMgr.playUI( "ui/iQuestComplete" )		#�������������Ч
	# ---------------------------------------------------------------
	def __checkQuestTimer( self, questID ):
		"""
		�����ʱ����
		"""
		if not GUIFacade.hasQuestLog( questID ):
			self.__closeQuestTimer()
			return
		if GUIFacade.hasQuestTaskType( questID, csdefine.QUEST_OBJECTIVE_TIME ):
			if self.__questUpdateTimeID == 0:
				self.__questUpdateTimeID = Timer.addTimer( 0, 1, self.__persistChange )
		else:
			self.__closeQuestTimer()

	def __persistChange( self ):
		"""
		ˢ��δ��ɵ�ʱ����������
		"""
		questID = GUIFacade.getQuestLogSelection()
		typeID = GUIFacade.getQuestTypeStr( questID )[0]
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		elif typeID in self._casual_ids :
			typeID = self._casual_ids[0]
		typeNode = self.__typeNodes.get( typeID )
		if typeNode is None:return
		questInfo = typeNode.getQuestItemInfo( questID )
		if questInfo is None:return
		if questInfo.resultText != "": #����ʧ�ܣ�����Ҫ����
			self.__closeQuestTimer()
		else:
			typeNode.onQuestStateChanged( questID )
		itemInfo = typeNode.getQuestItemInfo( questID )
		self.__pyContentPanel.pyQTCondition.resetFinishState( itemInfo.conditions )

	def __onQuestSelected( self, pyNode ) :
		"""
		ѡȡĳһ������ڵ�
		"""
		if pyNode.itemInfo is None : return
		GUIFacade.setQuestLogSelect( pyNode.itemInfo.id )

	def __onTraceQuest( self ):
		"""
		��������
		"""
		pySelNode = self.__pyTVQuets.pySelNode
		if pySelNode is None:return
		if pySelNode.itemInfo is None : return
		selQuestID = pySelNode.itemInfo.id
#		if self.__checkTraced: #����׷�ٽ���ɼ�ʱ�����ӻ�ɾ��
		if not self.__isTraceQuest( selQuestID ):
			DEBUG_MSG( "���ǿ�׷������" )
			BigWorld.player().statusMessage( csstatus.ROLE_QUEST_CANT_TRACE )
			return
		if selQuestID in self.traceQuestList:		# ����������ڱ�׷����
			self.traceQuestList.remove( selQuestID )
			pySelNode.isTraced = False
		else:
			if len( self.traceQuestList ) >= MAX_TRACE_QUEST_NUM:
				DEBUG_MSG( "���ֻ��׷��%i������" % MAX_TRACE_QUEST_NUM )
				BigWorld.player().statusMessage( csstatus.ROLE_QUEST_MAX_TRACE, MAX_TRACE_QUEST_NUM )
				return
		self.traceWindow.showQuestTrace( selQuestID )
		if selQuestID in self.traceWindow.TQuestIDList:
			self.traceQuestList.append( selQuestID )
			self.__onCheckTrace( self.__checkTraced )
			pySelNode.isTraced = True

	def __onAbandonQuest( self ) :
		"""
		����ĳһ������
		"""
		pyabandonNode = self.__pyTVQuets.pySelNode
		if pyabandonNode is None : return
		if pyabandonNode.itemInfo is None : return
		def query( rs_id ):
			if rs_id == RS_OK:
				pyabandonNode.selected = False
				GUIFacade.abandonQuest( pyabandonNode )
			if rs_id == RS_CANCEL :
				self.__pyBtnAbandon.enable = True
		# "�Ƿ��������%s?"
		itemInfo = pyabandonNode.itemInfo
		name = itemInfo.name
		stateColor = ( 193, 23, 0, 255 )
		if itemInfo.state:
			stateColor = ( 0, 128, 0, 255 )
		nameText = PL_Font.getSource( name, fc = stateColor )
		showMessage( mbmsgs[0x0581]%nameText, "", MB_OK_CANCEL, query, pyOwner = self.pyBinder )
		self.__pyBtnAbandon.enable = False # �������ĳһ������󣬰�ť��Ϊ���ɵ��
		return True

	def __onCasualQuestCommit( self ) :
		"""
		��������������
		"""
		pySelNode = self.__pyTVQuets.pySelNode
		if pySelNode is None or pySelNode.itemInfo is None : return
		questID = pySelNode.itemInfo.id
		if GUIFacade.getQuestTypeStr( questID )[0] == self._commit_direct_quest_type :
			GUIFacade.commitCasualQuest( questID )

	def __isTraceQuest( self, questID ):
		"""
		�Ƿ��׷�ٵ��������򷵻�True
		"""
		typeList = GUIFacade.getTaskGoalType( questID )
		for i in typeList:
			if i in Const.TRACE_QUEST_TYPE:
				return True
		return True

	def __isAddSucced( self, questID ):
		return self.traceWindow.isAddSucced( questID )

	def __onCheckTrace( self, checked ):
		self.__checkTraced = checked
		if len(self.traceQuestList)==0:
			checked =0
		self.traceWindow.visible = checked

	def __closeQuestTimer( self ):
		Timer.cancel( self.__questUpdateTimeID )
		self.__questUpdateTimeID = 0
		#����NPC���²�ѯ����״̬ by����
		for key, entity in BigWorld.entities.items():
			if hasattr( entity, "refurbishQuestStatus" ):
				entity.refurbishQuestStatus()

	def __onInviteFamilyDart( self, questID, questEntityID ):
		"""
		�����������
		"""
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.questAcceptForce( questID, questEntityID )
		# "�峤��������������������Ƿ���ܣ�"
		showMessage( 0x0582, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def __onLoopGroupReadRecord( self, questID ):
		"""
		��ȡ�����񱣴�ļ�¼ ��ʾ
		"""
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.readRandomQuestRecord( questID )
		# "�Ƿ�����ѱ���Ļ�����"
		showMessage( 0x0583, "", MB_YES_NO, notarize )

	def __onAcceptQuestConfirm( self, questID, msgStr ):
		"""
		��ȡ����ȷ�Ͽ�
		"""
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.questAcceptForce( questID, 0 )
		showMessage( msgStr, "", MB_YES_NO, notarize )

	def __onAcceptTrue( self ):
		"""
		"""
		self.startAdd = False	
	
	def __searchQuestHeith( self, questID ):
		"""
		�������Ч�����ѵ������λ��
		"""
		if not self.__isLogInited:		#�ͳ�ʼ��ʱ�����������
			return
		if not  questID in [int( quest["questID"] ) for quest in effQuestID]:
			return
		Timer.cancel( self.effectTimer )
		self.effectTime = 3
		self.__effectTop = 0
		for pyNode in self.__pyTVQuets.pyNodes:
			effectTop = self.__pyTVQuets.top
			effectTop += pyNode.pyParent.top
			effectTop += pyNode.top
			questDict = pyNode.quests
			if questDict.has_key( questID ):
				effectTop += questDict[questID].pyParent.top
				effectTop += questDict[questID].top
				self.effectTimer = Timer.addTimer( 0, 1, self.__playEffect )
				self.__effectTop = effectTop
					
	def __playEffect( self ):
		"""
		���������������Ч��
		"""
		if self.effectTime > 1:	#��һ����������2��ʱ��
			self.effectTime -= 1
			self.__circleEff.top = self.__effectTop -120
			self.__circleEff.visible = 1
		elif self.effectTime > 0:	#�ڶ�������1��
			self.__circleEff.visible = 0
			self.effectTime -= 1
			self.__blastEff.top = self.__effectTop - 120
			self.__blastEff.visible =1
		else:
			Timer.cancel( self.effectTimer )
			self.__blastEff.visible = 0
			self.__circleEff.visible = 0

	def __onResolutionChanged( self, preReso ):
		"""
		�ֱ��ʸı�
		"""
		pass

	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def enableQuestTraced( self, isTraced ) :
		"""��������׷��"""
		self.__pyCheckBox.checked = isTraced

	def initConstQuestType( self ): #��ʼ��3���������ͽڵ�
		for typeID in self._const_ids:#
			if not self.__typeNodes.has_key( typeID ):
				newID, typeStr = GUIFacade.getQuestTypeStr( typeID )
				pyTypeNode = TypeNode( typeID, self )
				pyTypeNode.text = typeStr
				self.__typeNodes[typeID] = pyTypeNode
				self.__pyTVQuets.pyNodes.add( pyTypeNode )
				self.__pyTVQuets.pyNodes.sort( key = lambda pyNode : pyNode.typeID )
		self.traceWindow.onEnterWorld()

	def reset( self ):
		self.__questItems = []
		self.__typeNodes = {}
		self.__pyTVQuets.pyNodes.clear()
		self.__pyContentPanel.clearItems()
		self.__pyQuestNum.text = "0/20"
		self.__pyCheckBox.checked = True
		self.startAdd = True
		self.__isLogInited = False
		self.traceQuestList	= []
		self.effectTime = 3
		self.__effectTop = 0
		self.traceWindow.reset()
#		self.__layOut()

	def afterStatusChanged( self, oldStatus, newStatus ) :
		#return
		if oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING :
			self.reset()

	def onNodeAdd( self, questID ):
		if not self.startAdd:
			self.__pyBtnAbandon.enable = True
			self.__pyBtnTrace.enable = True
			GUIFacade.setQuestLogSelect( questID )
			if questID in [80101,80102,80103,80104,80105,80106,80107,80108,80109,80110,80111,80112,80113,80114,80115]:
				ECenter.fireEvent( "EVT_ON_SHOW_QUEST_WINDOW" )
		rds.soundMgr.playUI( "ui/iQuestActivate" )		#���������������

	def onQuestNodeLClick( self ):
		self.__onTraceQuest()
	

	def onShow( self ):
		TabPanel.onShow( self )
	def onHide( self ):
		TabPanel.onHide( self )

	def onMove( self, dx, dz ):
		pass
