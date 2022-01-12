# -*- coding: gb18030 -*-
#
# 贝壳类的场景物件 2009-01-15 SongPeifang
#

from QuestBox import QuestBox
import ECBExtend

class QuestShellBox( QuestBox ):
	"""
	贝壳类的场景物件
	"""
	
	def __init__( self ):
		"""
		"""		
		QuestBox.__init__( self )
	
	def createEntity( self, spaceID, position, direction, param = None ):
		param["isShow"] = int( self.param2 )
		return QuestBox.createEntity( self, spaceID, position, direction, param )
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		判断玩家和箱子的任务状态
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus（ state )
		state == True :  表示有这样的状态，告诉任务箱子可以被选中
		否则: 没有这样的状态，不能被选中
		""" 
		status = 1
		# 玩家必须在日光浴并且处于每天的合法日光浴时间内
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( status )

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
		由该场景物件召唤出来的怪物死亡后的触发
		因为此场景物件目前没有召唤怪物的需求，所以此接口暂时pass
		"""
		pass
		
	def corpseDelay( self, selfEntity ):
		"""
		处理场景物件的“死亡”之后做哪些事情
		比如过多久刷新、立即刷新、还是根本就不刷新等
		
		这里只要场景物件被触发后，就消失（隐藏）而不会再刷新的出来
		刷新是由base端控制的每分钟刷20个，具体怎么刷及为什么要这么刷问林青
		由base控制刷新，这也是新做这个QuestShellBox类型的原因
		"""
		selfEntity.addFlag( 0 )	# 在客户端隐藏掉之后