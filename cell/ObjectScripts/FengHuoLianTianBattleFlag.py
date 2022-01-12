# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from NPCObject import NPCObject
import csdefine
import items
import ECBExtend
from QuestBox import QuestBox

g_items = items.instance()

class FengHuoLianTianBattleFlag( QuestBox ):
	"""
	帮会夺城战复赛（烽火连天）战旗
	"""
	
	def __init__( self ):
		"""
		"""
		
		QuestBox.__init__( self )
		
		
	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: 玩家实体
		@type  playerEntity: entity
		"""
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# 不等于0表示已经被触发过了，等待删除中
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return
		
		if len( self.questData ) > 0:
			allCompleted = True
			for questID, taskIndex in self.questData.iteritems():
				if not playerEntity.taskIsCompleted( questID, taskIndex ):		# 这个箱子指向的任务达成目标没有完成
					allCompleted = False
					break
			if not allCompleted:
				playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# 设置临时变量以让玩家能正确吟唱技能
				playerEntity.spellTarget( self.spellID, selfEntity.id )
				#entity = g_items.createEntity( self.questItemID, selfEntity.spaceID, selfEntity.position, selfEntity.direction)
				#entity.addPickupID( playerEntity.id )
				#selfEntity.destroy( )
		else:
			playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# 设置临时变量以让玩家能正确吟唱技能
			playerEntity.spellTarget( self.spellID, selfEntity.id )
	
	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		法术到达的回调，由某些特殊技能调用
		
		@param spell: 技能实例
		"""
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		# 如果此处检测不通过，则表示玩家对某个物件的动作白做了，暂时还没有好的提示方案。
		if not selfEntity.isReal():
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		# 去掉临时标志
		caster.removeTemp( "quest_box_intone_time" )
		# 指示客户端播放光效动画
		selfEntity.playEffect = self.effectName
		# 一段时间后干掉自己
		if self.destroyTime > 0.0:
			selfEntity.addFlag( 0 )	# 箱子专用，可能会与FLAG_*冲突，但如果没有特殊原因，应该没有问题
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		elif self.destroyTime == 0.0:
			# 销毁时间=0，不隐藏客户端模型
			selfEntity.addFlag( 1 )	# 客户端不隐藏模型
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		else:
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			selfEntity.destroy( )				# 销毁自身
	
	def entityDead( self, selfEntity ):
		"""
		"""
		pass
		
	def corpseDelay( self, selfEntity ):
		"""
		处理场景物件的“死亡”之后做哪些事情
		比如过多久刷新、立即刷新、还是根本就不刷新等
		
		不同的脚本里，不同的处理
		比如这里的处理方式是：打开场景物件之后，隐藏模型
		并且在selfEntity.rediviousTime的时间过去后重新刷一个出来（再显示模型）
		"""
		# QuestBox死亡时并不destroy自己，仅仅是隐藏模型而已
		selfEntity.addTimer( 0, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
		#selfEntity.setTemp( "gossipingID", 0 )

