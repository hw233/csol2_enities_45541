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
	帮会香炉基础类
	"""
	
	def __init__( self ):
		"""
		"""
		QuestBox.__init__( self )
		self.questID = []				# 相关的任务编号
		self.taskIndex = []				# 任务中的达成目标索引
	
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		QuestBox.load( self, section )
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		判断玩家和箱子的任务状态
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus（ state )
		state == True :  表示有这样的状态，告诉任务箱子可以被选中
		否则: 没有这样的状态，不能被选中
		""" 
		# 无条件可以点击
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( True )

	def onIncreaseQuestTaskState( self, selfEntity, playerEntity ):
		"""
		通知该任务箱子中某个索引位置上的任务目标已经完成了
		@param selfEntity: 该任务箱子
		@type  selfEntity: entity
		@param playerEntity: 玩家实体
		@type  playerEntity: entity
		@param index: 要设定完成的任务目标的索引位置
		@type  index: INT16
		"""
		if len( self.questID ) > 0:
			for idx, tidx in enumerate( self.taskIndex ):
				if playerEntity.hasTaskIndex( self.questID[ idx ], tidx ):
					playerEntity.questTaskIncreaseState( self.questID[ idx ], tidx )
		
	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: 玩家实体
		@type  playerEntity: entity
		"""
		#playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False ) 不显示可点击
		playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# 设置临时变量以让玩家能正确吟唱技能
		playerEntity.spellTarget( self.spellID, selfEntity.id )
	
	def addQuestTask( self, questID, taskIndex ):
		"""
		@param questID: 任务ID
		@type  questID: INT32
		@param taskIndex: 任务达成目标索引
		@type  taskIndex: INT32		
		"""
		if questID > 0:
			self.questID.append( questID )
			self.taskIndex.append( taskIndex )

	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		法术到达的回调，由某些特殊技能调用
		
		@param spell: 技能实例
		"""
		# 去掉临时标志
		caster.removeTemp( "quest_box_intone_time" )

	def entityDead( self, selfEntity ):
		"""
		"""
		pass
		#selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
