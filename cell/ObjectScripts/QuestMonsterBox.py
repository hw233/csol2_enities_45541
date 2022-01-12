# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from QuestBox import QuestBox
import csdefine
import items
import ECBExtend

g_items = items.instance()

class QuestMonsterBox( QuestBox ):
	"""
	QuestBox基础类
	"""
	
	def __init__( self ):
		"""
		"""
		
		QuestBox.__init__( self )


	def addMonsterCount( self, selfEntity, monsterCount ):
		"""
		设置QuestBox已经召唤出来的怪物数量
		"""
		selfEntity.setTemp( "questMonsterCount", selfEntity.queryTemp( "questMonsterCount", 0 ) + monsterCount )

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
			# 销毁时间>0，要隐藏客户端模型
			selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		elif self.destroyTime == 0.0:
			# 销毁时间=0，不隐藏客户端模型
			selfEntity.addFlag( 1 )	# 客户端不隐藏模型
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		else:
			self.taskStatus( selfEntity, caster )
		
	def entityDead( self, selfEntity ):
		"""
		"""
		self.addMonsterCount( selfEntity, -1 )
		if selfEntity.queryTemp( "questMonsterCount", 0 ) <= 0 and selfEntity.rediviousTime >= 0:
			selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
			
	def corpseDelay( self, selfEntity ):
		"""
		处理场景物件的“死亡”之后做哪些事情
		比如过多久刷新、立即刷新、还是根本就不刷新等
		"""
		# QuestBox死亡时并不destroy自己，仅仅是隐藏模型而已
		selfEntity.addFlag( 0 )	# 箱子专用，可能会与FLAG_*冲突，但如果没有特殊原因，应该没有问题
		if selfEntity.rediviousTime >= 0 and selfEntity.queryTemp( "questMonsterCount", 0 ) <= 0:
			selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
