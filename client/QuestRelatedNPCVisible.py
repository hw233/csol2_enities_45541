# -*- coding: gb18030 -*-

# common
from bwdebug import ERROR_MSG
from AbstractTemplates import Singleton

# client
import BigWorld
import GUIFacade
import event.EventCenter as ECenter
from gbref import rds

# config
from config.client.QuestRelatedNPCVisible import Datas as QRNVDatas

QUEST_STATE_NOT_FINISH 	= 0				# ����δ���
QUEST_STATE_FINISH 		= 1				# ��������ɣ����ύ��
QUEST_STATE_COMPLETE 	= 2				# ��������ɣ����ύ��

class QuestRelatedNPCVisible( Singleton ) :
	"""�������NPC�ɼ��Թ���"""
	def __init__( self ) :
		self.__classNameAndID = {}					# NPC��className�Լ���Ӧ��ID

		self.__triggers = {}
		self.__registerTriggers()

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUEST_ENTITY_ENTER_WORLD"]			= self.__onQuestEntityEnterWorld
		self.__triggers["EVT_ON_QUEST_ENTITY_LEAVE_WORLD"]			= self.__onQuestEntityLeaveWorld
		self.__triggers["EVT_ON_QUEST_LOG_ADD"]			= self.__onQuestAdd
		self.__triggers["EVT_ON_QUEST_LOG_REMOVED"]		= self.__onQuestRemove
		self.__triggers["EVT_ON_QUEST_TASK_STATE_CHANGED"] = self.__onQuestStateChanged
		for evt in self.__triggers.iterkeys() :
			ECenter.registerEvent( evt, self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onQuestEntityEnterWorld( self, className, npcId ):
		"""NPC enterWorld"""
		qrnv = self.__searchByClassName( className )
		if qrnv:
			self.__classNameAndID[ className ] = npcId
			questRelatedVisible = qrnv["visibleSituation"].get("quest")
			questRelatedInvisible = qrnv["invisibleSituation"].get("quest")
			qtaskRelatedVisible = qrnv["visibleSituation"].get("qtask")
			qtaskRelatedInvisible = qrnv["invisibleSituation"].get("qtask")
			if questRelatedVisible:
				for questID, state in questRelatedVisible.iteritems():
					if GUIFacade.hasQuestLog( questID ):
						NPC = BigWorld.entities.get( npcId )
						if GUIFacade.questIsCompleted( questID ) and QUEST_STATE_FINISH in state:
							if NPC:
								NPC.setVisible( True )
								return
						elif QUEST_STATE_NOT_FINISH in state:
							if NPC:
								NPC.setVisible( True )
					elif questID in BigWorld.player().completedQuestIDList and QUEST_STATE_COMPLETE in state:
						NPC = BigWorld.entities.get( npcId )
						if NPC:
							NPC.setVisible( True )
			if questRelatedInvisible:
				for questID, state in questRelatedInvisible.iteritems():
					if GUIFacade.hasQuestLog( questID ):
						NPC = BigWorld.entities.get( npcId )
						if GUIFacade.questIsCompleted( questID ) and QUEST_STATE_FINISH in state:
							if NPC:
								NPC.setVisible( False )
								return
						elif QUEST_STATE_NOT_FINISH in state:
							if NPC:
								NPC.setVisible( False )
					elif questID in BigWorld.player().completedQuestIDList and QUEST_STATE_COMPLETE in state:
						NPC = BigWorld.entities.get( npcId )
						if NPC:
							NPC.setVisible( False )
			if qtaskRelatedVisible:
				for questID, taskIndexs in qtaskRelatedVisible.iteritems():
					if GUIFacade.hasQuestLog( questID ):
						for taskIndex in taskIndexs:
							if GUIFacade.isTaskCompleted( questID, taskIndex ):
								NPC = BigWorld.entities.get( npcId )
								if NPC:
									NPC.setVisible( True )
			if qtaskRelatedInvisible:
				for questID, taskIndexs in qtaskRelatedInvisible.iteritems():
					if GUIFacade.hasQuestLog( questID ):
						for taskIndex in taskIndexs:
							if GUIFacade.isTaskCompleted( questID, taskIndex ):
								NPC = BigWorld.entities.get( npcId )
								if NPC:
									NPC.setVisible( False )
		
	def __onQuestEntityLeaveWorld( self, className, npcId ):
		"""NPC leaveWorld"""
		if self.__classNameAndID.has_key( className ):
			del self.__classNameAndID[ className ]

	def __onQuestAdd( self, questId ) :
		"""�������"""
		qrnvIds = self.__searchByQuestId( questId )
		visibleNPCList = qrnvIds.get("visible")
		invisibleNPCList = qrnvIds.get("invisible")
		if visibleNPCList:
			for className, state in visibleNPCList:
				if not GUIFacade.questIsCompleted( questId ) and QUEST_STATE_NOT_FINISH in state:
					if self.__classNameAndID.has_key( className ):
						npcId = self.__classNameAndID[ className ]
						if npcId:
							NPC = BigWorld.entities.get( npcId )
							if NPC:
								NPC.setVisible( True )
				elif QUEST_STATE_FINISH in state:
					if self.__classNameAndID.has_key( className ):
						npcId = self.__classNameAndID[ className ]
						if npcId:
							NPC = BigWorld.entities.get( npcId )
							if NPC:
								NPC.setVisible( True )
		if invisibleNPCList:
			for className, state in invisibleNPCList:
				if not GUIFacade.questIsCompleted( questId ) and QUEST_STATE_NOT_FINISH in state:
					if self.__classNameAndID.has_key( className ):
						npcId = self.__classNameAndID[ className ]
						if npcId:
							NPC = BigWorld.entities.get( npcId )
							if NPC:
								NPC.setVisible( False )
				elif QUEST_STATE_FINISH in state:
					if self.__classNameAndID.has_key( className ):
						npcId = self.__classNameAndID[ className ]
						if npcId:
							NPC = BigWorld.entities.get( npcId )
							if NPC:
								NPC.setVisible( False )

	def __onQuestRemove( self, questId ) :
		"""�����Ƴ�"""
		qrnvIds = self.__searchByQuestId( questId )
		visibleNPCList = qrnvIds.get("visible")
		invisibleNPCList = qrnvIds.get("invisible")
		if visibleNPCList:
			for className, state in visibleNPCList:
				if self.__classNameAndID.has_key( className ):
					npcId = self.__classNameAndID[ className ]
					if npcId:
						NPC = BigWorld.entities.get( npcId )
						if NPC:
							NPC.updateVisibility()
		if invisibleNPCList:
			for className, state in invisibleNPCList:
				if self.__classNameAndID.has_key( className ):
					npcId = self.__classNameAndID[ className ]
					if npcId:
						NPC = BigWorld.entities.get( npcId )
						if NPC:
							NPC.updateVisibility()

	def __onQuestStateChanged( self, questId, taskIndex ) :
		"""����״̬�ı�"""
		if GUIFacade.questIsCompleted( questId ) :
			qrnvIds = self.__searchByQuestId( questId )
			visibleNPCList = qrnvIds.get("visible")
			invisibleNPCList = qrnvIds.get("invisible")
			if visibleNPCList:
				for className, state in visibleNPCList:
					if QUEST_STATE_FINISH not in state:
						continue
					if self.__classNameAndID.has_key( className ):
						npcId = self.__classNameAndID[ className ]
						if npcId:
							NPC = BigWorld.entities.get( npcId )
							if NPC:
								NPC.setVisible( True )
			if invisibleNPCList:
				for className, state in invisibleNPCList:
					if QUEST_STATE_FINISH not in state:
						continue
					if self.__classNameAndID.has_key( className ):
						npcId = self.__classNameAndID[ className ]
						if npcId:
							NPC = BigWorld.entities.get( npcId )
							if NPC:
								NPC.setVisible( False )
		else :
			qrnvIds = self.__searchByQuestAndTaskId( questId, taskIndex )
			visibleNPCList = qrnvIds.get("visible")
			invisibleNPCList = qrnvIds.get("invisible")
			if GUIFacade.hasQuestLog( questId ) and GUIFacade.isTaskCompleted( questId, taskIndex ) :
				if visibleNPCList:
					for className in visibleNPCList:
						if self.__classNameAndID.has_key( className ):
							npcId = self.__classNameAndID[ className ]
							if npcId:
								NPC = BigWorld.entities.get( npcId )
								if NPC:
									NPC.setVisible( True )
				if invisibleNPCList:
					for className in invisibleNPCList:
						if self.__classNameAndID.has_key( className ):
							npcId = self.__classNameAndID[ className ]
							if npcId:
								NPC = BigWorld.entities.get( npcId )
								if NPC:
									NPC.setVisible( False )

	def __searchByClassName( self, className ) :
		"""����ָʾID���Ҷ�Ӧ��NPC�ɼ���"""
		return QRNVDatas.get( className )

	def __searchByQuestId( self, questId ):
		"""��������ID���Ҷ�Ӧ��NPC�ɼ���"""
		result = {"visible":[],"invisible":[]}
		if not QRNVDatas:
			return result
		for className, npcVisibleSituation in QRNVDatas.iteritems():
			questRelatedVisible = npcVisibleSituation["visibleSituation"].get("quest")
			questRelatedInvisible = npcVisibleSituation["invisibleSituation"].get("quest")
			if questRelatedVisible and questRelatedVisible.get( questId ) is not None :
				result["visible"].append( [ className, questRelatedVisible.get( questId ) ] )
			if questRelatedInvisible and questRelatedInvisible.get( questId ) is not None :
				result["invisible"].append( [ className, questRelatedInvisible.get( questId )] )
		return result

	def __searchByQuestAndTaskId( self, questId, taskIndex ):
		"""��������ID������Ŀ��ID���Ҷ�Ӧ��NPC�ɼ���"""
		result = {"visible":[],"invisible":[]}
		if not QRNVDatas:
			return result
		for className, npcVisibleSituation in QRNVDatas.iteritems():
			qtaskRelatedVisible = npcVisibleSituation["visibleSituation"].get("qtask")
			qtaskRelatedInvisible = npcVisibleSituation["invisibleSituation"].get("qtask")
			if qtaskRelatedVisible and qtaskRelatedVisible.get( questId ) and taskIndex in qtaskRelatedVisible.get( questId ) :
				result["visible"].append( className )
			if qtaskRelatedInvisible and qtaskRelatedInvisible.get( questId ) and taskIndex in qtaskRelatedInvisible.get( questId ):
				result["invisible"].append( className )
		return result

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		"""ע����¼�����"""
		self.__triggers[evtMacro]( *args )

	def clear( self ) :
		"""��յ���������"""
		self.__classNameAndID = {}					# NPC��className�Լ���Ӧ��ID