# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from QuestBox import QuestBox
import csdefine
import items
import ECBExtend

g_items = items.instance()

class TongCenser( QuestBox ):
	"""
	�����¯������
	"""
	
	def __init__( self ):
		"""
		"""
		QuestBox.__init__( self )
		self.questID = []				# ��ص�������
		self.taskIndex = []				# �����еĴ��Ŀ������
	
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		QuestBox.load( self, section )
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		�ж���Һ����ӵ�����״̬
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus�� state )
		state == True :  ��ʾ��������״̬�������������ӿ��Ա�ѡ��
		����: û��������״̬�����ܱ�ѡ��
		""" 
		# ���������Ե��
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( True )

	def onIncreaseQuestTaskState( self, selfEntity, playerEntity ):
		"""
		֪ͨ������������ĳ������λ���ϵ�����Ŀ���Ѿ������
		@param selfEntity: ����������
		@type  selfEntity: entity
		@param playerEntity: ���ʵ��
		@type  playerEntity: entity
		@param index: Ҫ�趨��ɵ�����Ŀ�������λ��
		@type  index: INT16
		"""
		if len( self.questID ) > 0:
			for idx, tidx in enumerate( self.taskIndex ):
				if playerEntity.hasTaskIndex( self.questID[ idx ], tidx ):
					playerEntity.questTaskIncreaseState( self.questID[ idx ], tidx )
		
	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: ���ʵ��
		@type  playerEntity: entity
		"""
		#playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False ) ����ʾ�ɵ��
		playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# ������ʱ���������������ȷ��������
		playerEntity.spellTarget( self.spellID, selfEntity.id )
	
	def addQuestTask( self, questID, taskIndex ):
		"""
		@param questID: ����ID
		@type  questID: INT32
		@param taskIndex: ������Ŀ������
		@type  taskIndex: INT32		
		"""
		if questID > 0:
			self.questID.append( questID )
			self.taskIndex.append( taskIndex )

	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		��������Ļص�����ĳЩ���⼼�ܵ���
		
		@param spell: ����ʵ��
		"""
		# ȥ����ʱ��־
		caster.removeTemp( "quest_box_intone_time" )

	def entityDead( self, selfEntity ):
		"""
		"""
		pass
		#selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
