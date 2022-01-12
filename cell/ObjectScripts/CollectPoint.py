# -*- coding: gb18030 -*-
#

import random
import BigWorld
from NPCObject import NPCObject
import csdefine
import csstatus
import Const
import items
import ECBExtend
import csconst
from bwdebug import *
from MsgLogger import *
from LivingConfigMgr import LivingConfigMgr


g_items = items.instance()

# 熟练度增加的提示。。。
SLE_UP_MSG_MAP = {
	25:csstatus.LIVING_SKILL_SLE_UP_MSG_1,
	50:csstatus.LIVING_SKILL_SLE_UP_MSG_2,
	75:csstatus.LIVING_SKILL_SLE_UP_MSG_3,
	100:csstatus.LIVING_SKILL_SLE_UP_MSG_4,
	150:csstatus.LIVING_SKILL_SLE_UP_MSG_5,
	200:csstatus.LIVING_SKILL_SLE_UP_MSG_6,
	350:csstatus.LIVING_SKILL_SLE_UP_MSG_7,
	500:csstatus.LIVING_SKILL_SLE_UP_MSG_8,
}

class CollectPoint( NPCObject ):
	"""
	QuestBox基础类
	"""

	def __init__( self ):
		"""
		"""

		NPCObject.__init__( self )
		self.questID = 0				# 相关的任务编号
		self.taskIndex = 0				# 任务中的达成目标索引
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
		self.param1 = int( section.readString( "param1" ) )			# 采集点类型(采集技能ID)
		self.param2 = int( section.readString( "param2" ) )			# 采集点所需熟练度
		self.param3 = section.readString( "param3" )				# 可获得物品ID及其几率
		self.param4 = section.readString( "param4" )				# 需要凭证物品ID
		self.param5 = int( section.readString( "param5" ) )			# 增加熟练度
		self.param6 = int( section.readString( "param6" ) )			# 消耗活力值
		self.param7 = int( section.readString( "param7" ) )			# 刷新时间
		self.param8 = int( section.readString( "param8" ) )			# 可增长熟练度的上限
		self.param9 = section.readString( "param9" )				# 刷怪配置，可空，格式：{odd:monsterID, odd:monsterID, ...}
		self.param10 = section.readString( "param10" )
		self.skillName = ""
		if self.param1 == 0:
			return
		if not ( self.param9 is None or self.param9 == "" ):
			self.param9 = eval( self.param9 )
		else:
			self.param9 = {}

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
		if self.skillName == "":
			from Love3 import g_skills
			skillInstance = g_skills[self.param1]
			if skillInstance is None:
				ERROR_MSG( "Living skill %s is None."%(self.param1) )
				return
			self.skillName = skillInstance.getName()

		return NPCObject.createEntity( self, spaceID, position, direction, param )


	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		@param playerEntity: 玩家实体
		@type  playerEntity: entity
		"""
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		playerEntity.endGossip( selfEntity.id )
		if dlgKey != "Talk":
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( False )
			return
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onCollectStatus( 0 )
			return
		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# 不等于0表示已经被触发过了，等待删除中
			playerEntity.clientEntity( selfEntity.id ).onCollectStatus( False )
			return
		# if self.param1 or self.param2 or self.param4 or self.param6 is None: return
		if not self.talkAbleCheck( playerEntity ):		# 普通/特殊采集点所需条件检查
			return
		#根据CSOL-776的要求 此判断取消 by wuxo
		#ids = self.param4.split("|")
		#useItem = None
		#for id in ids:
		#	nItem = playerEntity.findItemFromNKCK_( int( id ) )
		#	if nItem is not None:
		#		useItem = nItem
		#		break
		#if useItem is None:	# 身上没有凭证道具
		#	playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_ITEM )
		#	return
		#if playerEntity.iskitbagsLocked() :
		#	playerEntity.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
		#	return
		## 判断物品是否冻结
		#if useItem.isFrozen():
		#	playerEntity.statusMessage( csstatus.CIB_MSG_FROZEN )
		#	return
		#selfEntity.setTemp( str( playerEntity.id ), useItem.uid )
		playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# 设置临时变量以让玩家能正确吟唱技能
		playerEntity.spellTarget( self.spellID, selfEntity.id )
		
		try:
			spaceLabel = BigWorld.getSpaceDataFirstForKey( playerEntity.spaceID , csconst.SPACE_SPACEDATA_KEY )
			g_logger.collectLog( playerEntity.databaseID, playerEntity.getName(), spaceLabel, selfEntity.className )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		法术到达的回调，由某些特殊技能调用

		@param spell: 技能实例
		"""
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		# 如果此处检测不通过，则表示玩家对某个物件的动作白做了，暂时还没有好的提示方案。
		if not selfEntity.isReal():
			caster.clientEntity( selfEntity.id ).onCollectStatus( 0 )
			return
			
		# 去掉临时标志
		caster.removeTemp( "quest_box_intone_time" )
		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# 不等于0表示已经被触发过了，等待删除中
			caster.clientEntity( selfEntity.id ).onCollectStatus( False )
			caster.statusMessage( csstatus.LIVING_COLLECT_POINT_BUSY )
			return
			
		# 指示客户端播放光效动画
		selfEntity.playEffect = self.effectName
		# 一段时间后干掉自己
		if self.destroyTime > 0.0:
			selfEntity.addFlag( 0 )	# 箱子专用，可能会与FLAG_*冲突，但如果没有特殊原因，应该没有问题
		elif self.destroyTime == 0.0:
			# 销毁时间=0，不隐藏客户端模型
			selfEntity.addFlag( 1 )	# 客户端不隐藏模型
		selfEntity.setTemp( "quest_box_destroyed", 1 )
		caster.clientEntity( selfEntity.id ).onCollectStatus( 0 )
		
		#根据CSOL-776的要求 此判断取消 by wuxo
		
		# 处理凭证物品	 处理道具的使用次数（-1）,归零时消失之
		#useItemUID = selfEntity.queryTemp( str( caster.id ), 0 )
		#if useItemUID is None or useItemUID == 0:
		#	return
		#	
		#useItem = caster.getItemByUid_( useItemUID )
		#if useItem is None:
		#	caster.statusMessage( csstatus.LIVING_SKILL_NOT_ITEM )
		#	return
		#	
		## 判断物品是否冻结
		#if useItem.isFrozen():
		#	caster.statusMessage( csstatus.CIB_MSG_FROZEN )
		#	return
		#if caster.iskitbagsLocked():
		#	caster.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
		#	return
		#useDegree = useItem.getUseDegree() - 1
		#if useDegree <= 0:
		#	caster.removeItem_( useItem.getOrder(), reason = csdefine.DELETE_ITEM_COLLECT_POINT )
		#else:
		#	useItem.setUseDegree( useDegree, caster )
		
		# 增加熟练度 如果技能等级高于采集点等级则不增加
		sel = caster.getSleight( self.param1 )
		if not caster.isSleightLevelMax( self.param1 ) and ( sel in xrange( self.param2, self.param8 ) ):
			caster.addSleight( self.param1, self.param5 )
			now_sle = caster.getSleight( self.param1 )
			now_sle_Max = caster.getSleightMax( self.param1 )
			caster.statusMessage( csstatus.LIVING_SKILL_SLE_UP, self.skillName, now_sle, now_sle_Max )
			if SLE_UP_MSG_MAP.has_key( now_sle ):
				caster.statusMessage( SLE_UP_MSG_MAP[now_sle], self.skillName )
		else:
			caster.statusMessage( csstatus.LIVING_SKILL_SLE_UP_FAILED )
		# 消耗活力值
		if self.param6:
			caster.consumeVim( self.param6 )
		# 把采集得到的物品装箱 玩家要不要就随意了
		if self.param3 is None: return
		itemIDs = self.param3.split("|")
		collectDict = {}
		for itemID in itemIDs:
			if itemID.find(":") <= 0:
				collectDict[int(itemID)] = 1
			else:
				itemInfo = itemID.split(":")
				odd = random.randint(1,100)	# 按需求，每一次都要随机 0:itemID，1:几率，2:数量
				if odd > int( itemInfo[1] ):
					continue
				collectDict[int( itemInfo[0] )] = int( itemInfo[2] )
		selfEntity.removeTemp( str( caster.id ) )
		
		# 采集几率刷怪
		isSpawn = False #是否已经刷出怪物
		if selfEntity.spawnMB and len(selfEntity.monsterDatas) > 0 or len(self.param9) > 0:
			spawnMonsterDatas = eval( selfEntity.monsterDatas ) if len(selfEntity.monsterDatas) > 0 else self.param9
			for odd, monsterID in spawnMonsterDatas.iteritems():
				if random.randint(1, 100) < int(odd*100):
					selfEntity.spawnMB.cell.spawnMonster( str( monsterID ), collectDict )
					isSpawn = True
					break
		
		if isSpawn == False:
			caster.setTemp( "collectItems", collectDict )		# 为防止cell实例共同引用脚本，把获得品实例回归到玩家身上
			caster.clientEntity( selfEntity.id ).pickUpCollectPointItems( collectDict )
			
		# issueID:CSOL-943 资源点消失后都应能正常刷新,与玩家是否拾取无关
		selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

	def corpseDelay( self, selfEntity ):
		"""
		处理场景物件的“死亡”之后做哪些事情
		比如过多久刷新、立即刷新、还是根本就不刷新等

		不同的脚本里，不同的处理
		比如这里的处理方式是：打开场景物件之后，隐藏模型
		并且在selfEntity.rediviousTime的时间过去后重新刷一个出来（再显示模型）
		"""
		# collectPoint死亡时并不destroy自己，仅仅是隐藏模型而已
		if selfEntity.rediviousTime >= 0:
			selfEntity.addTimer( self.param7, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )

	def addQuestTask( self, questID, taskIndex ):
		"""
		@param questID: 任务ID
		@type  questID: INT32
		@param taskIndex: 任务达成目标索引
		@type  taskIndex: INT32
		"""
		pass

	def collectStatus( self, selfEntity, playerEntity ):
		"""
		客户端请求服务器更新在那里的状态
		"""
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onCollectStatus( 0 )
			return
		playerEntity.clientEntity( selfEntity.id ).onCollectStatus( selfEntity.queryTemp( "quest_box_destroyed", 0 ) == 0 )
		playerEntity.clientEntity( selfEntity.id ).onCollectDatas( self.param1, self.param2, self.param8 )

	def onPickUpItemByIndex( self, selfEntity, playerEntity, index ):
		"""
		给与玩家采集物品
		"""
		collectDict = playerEntity.queryTemp( "collectItems", {} )
		# 去掉临时标志
		if len( collectDict ) <= 0:
			playerEntity.removeTemp( "collectItems" )
			return
		if index > len( collectDict ) - 1: return
		itemID = collectDict.keys()[index]
		if itemID == 0: return
		amount = collectDict[itemID]
		if amount == 0: return
		item = g_items.createDynamicItem( itemID )
		if item is None: return
		item.setAmount( amount )
		if not playerEntity.addItemAndNotify_( item, csdefine.ADD_ITEM_COLLECT_POINT ):
			playerEntity.statusMessage( csstatus.CIB_MSG_ITEM_NOT_YOUR )
			return
		collectDict[itemID] = 0
		playerEntity.setTemp( "collectItems", collectDict )
		playerEntity.clientEntity( selfEntity.id ).pickUpItemByIndexBC( index )

	def talkAbleCheck( self, playerEntity ):
		"""
		采集点的检查
		"""
		vim = playerEntity.getVim()
		if vim <= 0 or vim - self.param6 <= 0:	# 活力值不够
			playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_VIM )
			return False
		livSkillsSleight = playerEntity.getSleight( self.param1 )
		if livSkillsSleight < 0: 		# 没有对应技能 等级不够
			playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_SKILL, self.skillName  )
			return False
		if livSkillsSleight < self.param2:	# 熟练度不足
			playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_LEVEL, self.skillName  )
			return False
		return True