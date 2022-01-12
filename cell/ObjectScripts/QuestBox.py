# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from NPCObject import NPCObject
import csdefine
import items
import ECBExtend

g_items = items.instance()

class QuestBox( NPCObject ):
	"""
	QuestBox基础类
	"""
	
	def __init__( self ):
		"""
		"""
		
		NPCObject.__init__( self )
		self.questData = {}
		#self.questID = []				# 相关的任务编号
		#self.taskIndex = []				# 任务中的达成目标索引
		self.questItemID = ""
		
		self.effectName = ""			# 被触发时播放的光效名称
		self.spellID = 0				# 被触发时让玩家施展的动作
		self.spellIntoneTime = 0.0		# 动作施展时的吟唱时间
		self.destroyTime = 0			# 销毁时间
		self.param1 = None				# 额外的附加参数
		self.param2 = None
		self.param3 = None
		self.param4 = None
		self.param5 = None
		self.param6 = None
		self.param7 = None
		self.param8 = None
		self.param9 = None
		self.param10 = None
		
	
	
	# ----------------------------------------------------------------
	# overrite method / protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, sect ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initializes.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" file
		@ptype			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		NPCObject.onLoadEntityProperties_( self, sect )
		# 注：下面的属性不需要读取，在创建的时候由出生点配置直接传进来
		#self.setEntityProperty( "rediviousTime", sect.readFloat( "rediviousTime" ) )	# 用于隐藏一段时间后恢复显示
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		selfEntity.removeFlag( 0 )
	
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		NPCObject.load( self, section )
		
		self.effectName = section.readString( "effectName" )			# 被触发时播放的动画
		self.spellID = section.readInt( "spellID" )						# 被触发时让玩家施展的动作
		self.spellIntoneTime = section.readFloat( "spellIntoneTime" )	# 动作施展时的吟唱时间
		self.destroyTime = section.readFloat( "destroyTime" )			# 销毁时间
		self.param1 = section.readString( "param1" )					# 额外的附加参数
		self.param2 = section.readString( "param2" )
		self.param3 = section.readString( "param3" )
		self.param4 = section.readString( "param4" )
		self.param5 = section.readString( "param5" )
		self.param6 = section.readString( "param6" )
		self.param7 = section.readString( "param7" )
		self.param8 = section.readString( "param8" )
		self.param9 = section.readString( "param9" )
		self.param10 = section.readString( "param10" )
	
	def createEntity( self, spaceID, position, direction, param = None ):
		"""
		创建一个NPC实体在地图上
		@param   spaceID: 地图ID号
		@type    spaceID: INT32
		@param  position: entity的出生位置
		@type   position: VECTOR3
		@param direction: entity的出生方向
		@type  direction: VECTOR3
		@param      param: 该参数默认值为None，传给实体的数据
		@type    	param: dict
		@return:          一个新的NPC Entity
		@rtype:           Entity
		"""		
		return NPCObject.createEntity( self, spaceID, position, direction, param )
		
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		判断玩家和箱子的任务状态
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus（ state )
		state == True :  表示有这样的状态，告诉任务箱子可以被选中
		否则: 没有这样的状态，不能被选中
		""" 
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
			
		if len( self.questData ) <= 0:
			if self.spellID <= 0:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			else:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( selfEntity.queryTemp( "quest_box_destroyed", 0 ) == 0 )
			return
			
		findQuest = False
		for id in self.questData.keys():
			quest = self.getQuest( id )
			if quest != None:
				findQuest = True
				break
		if not findQuest:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# 不等于0表示已经被触发过了，等待删除中
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		indexTaskState = False
		for questID, taskIndex in self.questData.iteritems():
			if not playerEntity.taskIsCompleted( questID, taskIndex ):
				indexTaskState = True
				break
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( indexTaskState )

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
		if len( self.questData ) > 0:
			for questID, taskIndex in self.questData.iteritems():
				playerEntity.questTaskIncreaseState( questID, taskIndex )
		
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
	
	def addQuestTask( self, questID, taskIndex ):
		"""
		@param questID: 任务ID
		@type  questID: INT32
		@param taskIndex: 任务达成目标索引
		@type  taskIndex: INT32		
		"""
		if self.questData.get( questID ):
			return
		self.questData[ questID ] = taskIndex

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
		#selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
		
	def corpseDelay( self, selfEntity ):
		"""
		处理场景物件的“死亡”之后做哪些事情
		比如过多久刷新、立即刷新、还是根本就不刷新等
		
		不同的脚本里，不同的处理
		比如这里的处理方式是：打开场景物件之后，隐藏模型
		并且在selfEntity.rediviousTime的时间过去后重新刷一个出来（再显示模型）
		"""
		# QuestBox死亡时并不destroy自己，仅仅是隐藏模型而已
		if selfEntity.rediviousTime >= 0:
			selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )

