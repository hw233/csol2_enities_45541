# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.64 2008-09-04 07:45:07 kebiao Exp $

"""
怪物NPC的类
"""
import math
import Math
from NPCObject import NPCObject
import Language
from bwdebug import *
import LostItemDistr
import items
import random
import ItemTypeEnum
import csdefine
import csconst
import BigWorld
import time
import csstatus
import Resource.AIData
import ECBExtend
import Const
from NPCBaseAttrLoader import NPCBaseAttrLoader					# 怪物四项基础属性加载器
from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader	# NPC的任务掉落物品配置表
from MonsterIntensifyPropertyData import MonsterIntensifyPropertyData
from ItemSystemExp import ItemTypeAmendExp
from Resource.BigWorldLevelMaps import BigWorldLevelMaps
from MonsterDropManager import MonsterDropManager
from LevelEXP import AmendExp
from DaohengLoader import DaohengLoader
from MsgLogger import g_logger
from Domain_Fight import g_fightMgr
from Resource.AI.AIBase import AIBase
from ObjectScripts.GameObjectFactory import g_objFactory
from interface.CombatUnit import CombatUnit

g_items = items.instance()
g_npcQuestDroppedItems = NPCQuestDroppedItemLoader.instance()
g_aiDatas = Resource.AIData.aiData_instance()
g_npcaiDatas = Resource.AIData.NPCAI_instance()
g_monsterIntensifyAttr = MonsterIntensifyPropertyData.instance()
g_produceMin = 3	# 爆物品最小可能次数
g_produceMax = 5	# 爆物品最大可能次数
g_BigWorldLevelMaps = BigWorldLevelMaps.instance()		# 世界地图对应的怪物级别信息
g_monsterdropmanager = MonsterDropManager.instance()	# 掉落管理
g_daoheng = DaohengLoader.instance()			# 道行

ITEMS_BOX_ID = 40301001
class Monster(NPCObject):
	"""
	怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPCObject.__init__( self )
		# 存储所有与自身相同标识符的实例，用于创建entity时从此列表中随机选择需要的数据
		# key == level; value == instance of Monster
		self.equips = {}						# 怪物的装备列表；key == order, value == itemID
		self.aiData	= {}						# 怪物的AI数据表
		self._expRate = 0.0						# 怪物经验比率的计算
		self._daohengRate = 0.0                 # 怪物击杀道行奖励比率的计算
		self._campMoraleRate = 0.0				# 阵营士气奖励比率的计算
		self._daohengAtt = 0.0                  # 怪物道行属性比率的计算
		self.callList = []						# 呼叫同伴表 [npcid,...]
		self.attrAIDefLevel = 0					# 怪物的默认AI等级
		self.prestige = []						# 被杀死后主角可获得的声望值；[ (id, value), ...]; id == 势力索引，value == 增加的数量
		self.hasPreAction = 0					# 怪物的出场动作 默认是0
		self.isMovedAction = 0					# 怪物是否带位移出场
		self.preActionTime = 0					# 怪物出场动作持续时间
		self.jumpPoint = None
		self.jumpPointType = 0
		self.comboAITable = {}					# 连续AI
		self.comboAIActivate = 0				# 连续AI执行概率
		self.isComboAILoaded = 0				# 连续AI是否加载

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		NPCObject.onLoadEntityProperties_( self, section )

		# 性别、职业、种族、势力
		raceclass = 0
		#raceclass += section.readInt( "gender" )			# 暂时忽略此功能，全部默认为男，因为策划这部份暂时没用上
		raceclass |= section.readInt( "class" ) << 4
		raceclass |= section.readInt( "race" ) << 8
		raceclass |= section.readInt( "faction" ) << 12
		raceclass |= section.readInt( "camp" ) << 20
		self.setEntityProperty( "raceclass", raceclass )
		self.setEntityProperty( "level", section.readInt( "level" ) )
		self._expRate = section.readFloat( "expRate" )
		self._accumRate = section.readFloat( "accumRate" )		# 气运值倍率
		self._potentialRate = section.readFloat( "potentialRate" )
		self.setEntityProperty( "baseAtt", section.readFloat( "baseAtt" ) )
		self.setEntityProperty( "excAtt", section.readFloat( "excAtt" ) )
		#设置道行值
		self._daohengAtt = section.readFloat( "daohengAtt" )
		self._daohengRate = section.readFloat( "daohengRate" )
		
		if section.has_key( "campMoraleRate" ):
			self._campMoraleRate = section.readFloat( "campMoraleRate" )
		
		# AI
		#self.setEntityProperty( "attackSkill",				section.readInt("attackSkill") )				# 攻击技能，无此技能时为物理攻击
		if section.has_key( "walkPath" ):
			self.setEntityProperty( "walkPath",				eval(section.readString("walkPath")) )			# 巡逻路径
		if section.has_key( "initiativeRange" ):
			self.setEntityProperty( "initiativeRange",		section["initiativeRange"].asInt )				# 主动攻击范围
		#self.setEntityProperty( "range_base",				int( section["range_base"].asFloat * csconst.FLOAT_ZIP_PERCENT ) )					# 攻击距离基础值
		self.setEntityProperty( "viewRange",				section["viewRange"].asInt )					# 视野范围（主动攻击范围）
		self.setEntityProperty( "territory",				section["territory"].asInt )					# 领域范围（追击范围）
		if section.has_key( "petName" ):
			self.setEntityProperty( "petName",				section["petName"].asString )					# 宠物名字
		if section.has_key( "callRange" ):
			self.setEntityProperty( "callRange",			section["callRange"].asInt )					# 呼叫同伴范围
		self.attrAIDefLevel = section.readInt("attrAIDefLevel")
		
		if section.has_key( "battleCamp" ):
			self.setEntityProperty( "battleCamp",			section["battleCamp"].asInt )					# 阵营
		if section.has_key( "hasPreAction" ):
			self.hasPreAction = section.readInt( "hasPreAction" )										# 入场动作
		if section.has_key( "isMovedAction" ):
			self.isMovedAction = section.readInt( "isMovedAction" )										# 入场动作是否有位移
		if section.has_key( "preActionTime" ):
			self.preActionTime = section.readFloat("preActionTime")										# 入场动作播放时间
		if section.has_key( "jumpPointType" ):
			self.jumpPointType = section.readInt( "jumpPointType" )										# 落地点类型
		if section.has_key( "jumpPoint" ):
			self.jumpPoint = section.readString("jumpPoint") 											# 落地点为固定位置时落点坐标
			
		#if section.has_key( "accumPoint" ):
		#	self.setEntityProperty( "accumPoint",			section["accumPoint"].asInt )					# 气运值
			
		#self.setEntityProperty( "randomWalkRange",			section["randomWalkRange"].asFloat )			# 随机行走范围
		#self.setEntityProperty( "fleePercent",				section["fleePercent"].asInt )					# 逃跑机率范围

		# phw: 将来AI会有大改动，现在测试不乐意填写相关数据，因此只好使用默认值。
		#self.setEntityProperty( "attackSkill",				1 )				# 攻击技能，无此技能时为物理攻击；2 为怪物的普通物理攻击
		#self.setEntityProperty( "range_base",				2.0 )			# 攻击距离基础值
		#self.setEntityProperty( "viewRange",				50.0 )			# 视野范围（主动攻击范围）
		#self.setEntityProperty( "territory",				30.0 )			# 领域范围（追击范围）
		#self.setEntityProperty( "callRange",				0.0 )			# 呼叫同伴范围
		#self.setEntityProperty( "randomWalkRange",			3.0 )			# 随机行走范围
		#self.setEntityProperty( "initiativeRange",			0.0 )			# 主动攻击范围
		#self.setEntityProperty( "fleePercent",				0 )				# 逃跑机率范围

		# 武器模型显示相关
		"""
		modelNumber = section.readString( "lefthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "lefthandNumber", modelNumber )

		modelNumber = section.readString( "righthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "righthandNumber", modelNumber )
		"""
		self._lefthandNumbers = []
		self._righthandNumbers = []
		if section.has_key( "lefthandNumber" ):
			self._lefthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["lefthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "righthandNumber" ):
			self._righthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["righthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "callList" ):
			for item in section[ "callList" ].values():
				self.callList.append( item.asString )
		if section.has_key( "isNotifyDie" ):
			self.setEntityProperty( "isNotifyDie",			section["isNotifyDie"].asInt )					# 通知副本死亡时计数
			
		if section.has_key( "relationMode" ):
			self.setEntityProperty( "relationMode", section[ "relationMode" ].asInt )					# 战斗关系模式
		else:
			self.setEntityProperty( "relationMode", 0 )					# 战斗关系模式
			
		if section.has_key( "isUseCombatCamp" ):
			self.setEntityProperty( "isUseCombatCamp", section[ "isUseCombatCamp" ].asInt )					# 是否启用战斗阵营
		else:
			self.setEntityProperty( "isUseCombatCamp", 0 )
			
		if section.has_key( "combatCamp" ):
			self.setEntityProperty( "combatCamp", section[ "combatCamp" ].asInt )							# 战斗阵营
		
		# 记录最小、最大等级，创建时根据最小、最大等级随机产生
		self.minLv = section.readInt("minLv")
		self.maxLv = section.readInt("maxLv")

		self.mapPetID = section.readString( "petID" )
		self.takeLevel = section.readInt( "takeLevel" )
		
		self.petInbornSkills = []
		self.petInbornSkillRate = 0.0
		petInbornSkills = section.readString( "petInbornSkills" )
		if petInbornSkills != "":
			self.petInbornSkills = [int( skillID ) for skillID in petInbornSkills.split( ";" )]
			# 获得每一个宠物技能的概率，设计原则是1000个宠物中有一个会获得全天赋技能，即宠物获得所有天赋技能的
			# 概率为1/1000，则获得每一个天赋技能的概率是0.001 ** ( 1.0/宠物天赋技能个数 )
			self.petInbornSkillRate = csconst.PET_HAS_ALL_INBORN_SKILL_RATE ** ( 1.0/len(self.petInbornSkills) )
			
		flags = self.getEntityProperty( "flags" )
		inaRng = self.getEntityProperty( "initiativeRange" )
		if inaRng > 0 :													# 如果主动攻击范围大于 0
			if flags is None :											# 则，给怪物添加一个主动攻击标记（hyw--09.03.03）
				flags = 1 << csdefine.ENTITY_FLAG_MONSTER_INITIATIVE
			else :
				flags |= 1 << csdefine.ENTITY_FLAG_MONSTER_INITIATIVE
			self.setEntityProperty( "flags", flags )
		if self.mapPetID != "":
			if flags is None:
				flags = 1 << csdefine.ENTITY_FLAG_CAN_CATCH
			else:
				flags |= 1 << csdefine.ENTITY_FLAG_CAN_CATCH
			self.setEntityProperty( "flags", flags )

		#-------------掉落相关，这里将掉落配置到怪物本身，格式为 index:odds
		if section.has_key( "drops" ):
			dropInfos = []
			drops = section["drops"]
			for value in drops.values():
				Infos = {}
				temp = value.asString
				if not temp:
					continue
				dropType,amount,dropOdds = temp.split(':')
				Infos["dropType"] = int(dropType)
				Infos["dropOdds"] = eval(dropOdds) / 100.0
				Infos["dropAmount"] = int(amount)
				dropInfos.append(Infos)
			self.setEntityProperty( "drops", dropInfos)
		if section.has_key( "luckyDropOdds" ):
			luckyDropOdds = section["luckyDropOdds"].asInt
			self.setEntityProperty( "luckyDropOdds", luckyDropOdds)

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		NPCObject.load( self, section )
		# 加载声望配置
		if section["prestige"] is not None:
			for e in section["prestige"].readVector2s( "item" ):
				self.prestige.append( ( int( e[0] ), int( e[1] ) ) )		# 必须转成整数

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		# 初始化附加数据放在前头
		selfEntity.setLevel( selfEntity.level )
		self._initAI( selfEntity )
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_MONSTER )

	def _initDefaultAI( self, selfEntity ):
		"""
		初始化怪物默认的AI
		"""
		# 没有配置AI就添加默认AI
		selfEntity.addAI( 0, g_aiDatas[ 1 ], csdefine.AI_TYPE_GENERIC_ATTACK )  			  # 检测攻击对象有效性
		selfEntity.addAI( 0, g_aiDatas[ 0 ], csdefine.AI_TYPE_SPECIAL )		  				  # 普通攻击
		# 有entity进入陷阱时 该事件下的所有AI被触发
		selfEntity.addEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP, 0, g_aiDatas[ 2 ] ) 	  	  # 对进入陷阱的entity添加敌意
		selfEntity.addEventAI( csdefine.AI_EVENT_ENEMY_LIST_CHANGED, 0, g_aiDatas[ 3 ] )	  # 当仇恨列表改变的时候 如果状态为休息 则攻击该目标
		selfEntity.addEventAI( csdefine.AI_EVENT_ENEMY_LIST_CHANGED, 0, g_aiDatas[ 4 ] ) 	  # 当仇恨列表改变的时候 如果是在战斗状态 且敌人列表没有敌人了 就置为闲置状态 这个状态也回导致回走
		selfEntity.addEventAI( csdefine.AI_EVENT_ATTACKER_ON_REMOVE, 0, g_aiDatas[ 5 ] )	  # 默认怪物战斗AI   功能: 当仇恨列表改变的时候 丢失或者删除一个正在攻击的目标时 寻找下一个目标
		#selfEntity.addEventAI( csdefine.AI_EVENT_DAMAGE_LIST_CHANGED, 0, g_aiDatas[ 6 ] )	  # 默认怪物战斗AI   功能: 当伤害列表改变的时候 判断当前攻击的目标是否是一个宠物，打我的目标是否是一个role, 是就转向攻击role

	def _initAI( self, selfEntity ):
		"""
		初始化怪物的AI
		"""
		if not g_npcaiDatas.has( self.className ):
			self._initDefaultAI( selfEntity )
			return

		aiData = g_npcaiDatas[ self.className ]
		for type, dataList in aiData.iteritems():
			if type not in [ csdefine.AI_TYPE_EVENT, csdefine.AI_TYPE_COMBO, csdefine.AI_TYPE_COMBO_ACTIVERATE ]:
				for d in dataList:
					selfEntity.addAI( d["level"], d["data"], d["type"] )
			elif type == csdefine.AI_TYPE_EVENT:
				for d in dataList:
					selfEntity.addEventAI( d["eventID"], d["level"], d["data"] )
			elif type == csdefine.AI_TYPE_COMBO:
				if self.isComboAILoaded:
					continue
				for d in dataList:
					self.addComboAI( d[ "level" ], d[ "comboID"], d[ "activeRate" ], d[ "data" ] )
			elif type == csdefine.AI_TYPE_COMBO_ACTIVERATE:
				if self.isComboAILoaded:
					continue
				self.comboActiveRate = dataList

		self.isComboAILoaded = True			# 只加载一次

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		if selfEntity.getCamp() !=0 and selfEntity.getCamp() != playerEntity.getCamp():
			playerEntity.client.onStatusMessage( csstatus.CAMP_NPC_DIFFERENT, "" )
			return 

		NPCObject.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def getDropItems( self, selfInstance ):
		"""
		virtual method
		获得怪物掉落的物品
		@param selfInstance: 与全局数据对应的继承于Monster的real Monster entity实例
		@type  selfInstance: Monster
		@return :array of tuple, tuple like as  [(itemKeyName, {...}, owners) ,...]
		"""
		return g_monsterdropmanager.getDropItems( self, selfInstance )

	def dropItemBox( self, selfEntity, bootyOwner ):
		"""
		掉落箱子
		"""
		pos = selfEntity.position
		spaceID = selfEntity.spaceID
		direction = selfEntity.direction

		x, y, z = pos
		collide = BigWorld.collide( selfEntity.spaceID, ( x, y + 4, z ), ( x, y - 10, z ) )
		if collide != None:
			# 掉落物品的时候对地面进行碰撞检测避免物品陷入地下
			y = collide[0].y

		tempList = []
		itemsList = []
		drop_configed_items_info = selfEntity.popTemp( "drop_configed" )	# 动态配置掉落信息
		if drop_configed_items_info is not None:
			for itemID, amount in drop_configed_items_info.iteritems():
				item = g_items.createDynamicItem( itemID )
				item.setAmount( amount )
				itemsList.append( item )
		else:
			itemsList = self.getDropItems( BigWorld.entities.get(bootyOwner[0], None) )

		params = { "dropType" : csdefine.DROPPEDBOX_TYPE_MONSTER, "droperName" : selfEntity.getName() }
		itemBox = BigWorld.createEntity( "DroppedBox", spaceID, (x, y+2, z), direction, params )

		if bootyOwner[1] != 0:
			players = [ e for e in selfEntity.entitiesInRangeExt( 30.0, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == bootyOwner[1] ]
			if len(players) == 0:
				return
			multDrop = players[0].queryTemp( "MULT_DROP", 0 )
			if multDrop > 0:		# 掉落翻倍
				for item in itemsList:
					item.setAmount( item.amount *( 1 + multDrop ) )
			
			itemBox.init( bootyOwner, itemsList )
			players[0].addTeamMembersTasksItem(  itemBox.id, self.className )
		else:
			entity = BigWorld.entities.get( bootyOwner[0], None )
			if entity:
				player = None
				if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					player = entity
				elif entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
					owner = BigWorld.entities.get( entity.ownerID, None )
					if owner:
						player = owner
				if player:
					multDrop = player.queryTemp( "MULT_DROP", 0 )
					if multDrop > 0:		# 掉落翻倍
						for item in itemsList:
							item.setAmount( item.amount *( 1 + multDrop ) )
					
					itemBox.init( bootyOwner, itemsList )
					player.addTasksItem(  itemBox.id, self.className )

	def getBootyOwner( self, selfEntity ):
		"""
		获得战利品的拥有者；
		如果想知道返回的拥有者是否有队伍，需要自己去检查该拥有者的队伍情况；
		如果返回0则表示没有拥有者；如果返回不是0且自己拥有队伍，那么它的值应该是指向队长的teamMailbox's entityID。

		@return: tuple of Entity ID --> (拥有者ID, 拥有者队长ID)，两者只会出现一个,拥有者ID优先，两者为0表示所有人都可以捡；
		@rtype:  TUPLE OF OBJECT_ID
		"""
		if len( selfEntity.bootyOwner ):
			return selfEntity.bootyOwner
		return (0,0)

	def queryRelation( self, selfEntity, entity ):
		"""
		virtual method.
		取得自己与目标的关系
		注意: 因为这个函数的使用频率极其的高，为了效率，部分的处理将不走函数调用的方式
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		#if selfEntity.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not selfEntity.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if selfEntity.isUseCombatCamp and entity.isUseCombatCamp:
			entity = entity.getRelationEntity()
			if entity:
				combatConstraint = self.queryGlobalCombatConstraint( selfEntity, entity )
				if combatConstraint != csdefine.RELATION_NONE:
					return combatConstraint
				else:
					return selfEntity.queryCombatRelation( entity )
			else:
				return csdefine.RELATION_FRIEND
			
		def commonRelationCheck( selfEntity, entity ):
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_MONSTER ): # 不能被怪物攻击标志
				return csdefine.RELATION_NOFIGHT
			
			if entity.state in [csdefine.ENTITY_STATE_PENDING, csdefine.ENTITY_STATE_QUIZ_GAME, csdefine.ENTITY_STATE_DEAD]:
				return csdefine.RELATION_NOFIGHT

			# 全体免战判定
			if selfEntity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
				entity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
					return csdefine.RELATION_NOFIGHT
			
			return csdefine.RELATION_ANTAGONIZE
		
		# it's a pet
		if entity.utype == csdefine.ENTITY_TYPE_PET:
			owner = entity.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_NOFIGHT
			# 把宠物的敌对比较转嫁给它的主人
			# 虽然此关系未来可能会根据不同的状态或buff导致关系的改变，但当前并没有此需求
			entity = owner.entity

		if entity.utype == csdefine.ENTITY_TYPE_ROLE:

			bootyOwner = selfEntity.queryTemp( "ToxinFrog_bootyOwner", () )
			if bootyOwner:
				getTeam = getattr( entity, "getTeamMailbox", None )
				if getTeam and getTeam():
					if getTeam().id != bootyOwner[1]:
						return csdefine.RELATION_NOFIGHT
				else:
					if entity.id != bootyOwner[0]:
						return csdefine.RELATION_NOFIGHT

			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT

			# GM观察者模式
			if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
				return csdefine.RELATION_NOFIGHT

			if selfEntity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE	 ):
				return csdefine.RELATION_NOFIGHT

			# 友好阵营列表判断
			return selfEntity.queryCampRelation( entity )


		if entity.utype in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_CONVOY_MONSTER ]:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT
			
			if ( selfEntity.battleCamp != 0 or entity.battleCamp !=0 ):
				if selfEntity.battleCamp == entity.battleCamp:			# 如果设置了阵营值，目标是怪物且跟自己属于同一个阵营
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE

			if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ) or selfEntity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ):
				return csdefine.RELATION_ANTAGONIZE

			# 友好阵营列表判断
			return selfEntity.queryCampRelation( entity )


		if entity.utype in [csdefine.ENTITY_TYPE_SLAVE_MONSTER, csdefine.ENTITY_TYPE_VEHICLE_DART, csdefine.ENTITY_TYPE_PANGU_NAGUAL]:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:

				return csdefine.RELATION_NOFIGHT

			if selfEntity.queryTemp( 'is_dart_banditti', False ) == True:
				# 如果是劫匪不用想了，和镖车及保镖肯定是敌对的
				return csdefine.RELATION_ANTAGONIZE
			ownerID = entity.ownerID
			if ownerID is 0:
				return csdefine.RELATION_ANTAGONIZE
			if BigWorld.entities.has_key( ownerID ):	#判定怪物主人的敌对关系
				return selfEntity.queryRelation( BigWorld.entities[ownerID] )
			return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_YAYU:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT

			if ( selfEntity.battleCamp != 0 or entity.battleCamp !=0 ):
				if selfEntity.battleCamp == entity.battleCamp:			# 如果设置了阵营值，目标是怪物且跟自己属于同一个阵营
					return csdefine.RELATION_FRIEND

			return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_CALL_MONSTER:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT

			return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_FRIEND

	def queryGlobalCombatConstraint( self, selfEntity, entity ):
		"""
		查询全局战斗约束
		"""
		#if not isinstance( entity, CombatUnit ):
		#	return csdefine.RELATION_FRIEND

		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_MONSTER ): # 不能被怪物攻击标志
			return csdefine.RELATION_NOFIGHT
			
		if entity.state in [csdefine.ENTITY_STATE_PENDING, csdefine.ENTITY_STATE_QUIZ_GAME, csdefine.ENTITY_STATE_DEAD]:
			return csdefine.RELATION_NOFIGHT
			
		# 全体免战判定
		if selfEntity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT
		
		if entity.effect_state & csdefine.EFFECT_STATE_PROWL:	# 如果entity处于潜行效果状态
			return csdefine.RELATION_NOFIGHT
		
		# GM观察者模式
		if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
			return csdefine.RELATION_NOFIGHT
			
		if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			return csdefine.RELATION_NOFIGHT
			
		if entity.utype == csdefine.ENTITY_TYPE_ROLE:
			if selfEntity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
				return csdefine.RELATION_NOFIGHT
				
		if entity.utype in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_CONVOY_MONSTER ]:
			if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ) or selfEntity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ):
				return csdefine.RELATION_ANTAGONIZE
				
		return csdefine.RELATION_NONE


	def dieNotify( self, selfEntity, killerID ):
		"""
		virtual method
		死亡通知
		"""
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase :
			spaceKey = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			spaceScript = g_objFactory.getObject( spaceKey )
			spaceScript.copyTemplate_onMonsterDie( spaceBase, selfEntity.id, selfEntity.className, killerID )		# 新副本结构下的怪物死亡通知
		
		if selfEntity.isNotifyDie:							#死亡是否通知副本计数
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal():
				spaceEntity.getScript().onOneTypeMonsterDie( spaceEntity, selfEntity.id, selfEntity.className )
			elif spaceBase:
				spaceBase.cell.remoteScriptCall( "onOneTypeMonsterDie", ( selfEntity.id, selfEntity.className ) )

	def onMonsterDie( self, selfEntity, killerID ):
		"""
		virtual method
		怪物死亡相关处理
		"""
		self.dieNotify( selfEntity, killerID )
		selfEntity.calculateBootyOwner()							# 计算出最后这个怪物是属于谁拥有
		killers = []
		# 经验拥有者
		bootyOwner = selfEntity.getBootyOwner()
		if bootyOwner[1] != 0:		#先判断是否有组队，然后在判断是否是个人 hd
			# 获取组队经验
			killers = selfEntity.searchTeamMember( bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			if len( killers ) == 1:
				# 如果仍然只满足一个人获得经验，走获取单人杀怪经验路线
				killers = selfEntity.gainSingleReward( killers[0].id )
			else:
				# 获取组队经验
				selfEntity.gainTeamReward( killers)
				for entity in killers:
					entity.base.addTeamFriendlyValue( [e.databaseID for e in killers if e.databaseID != entity.databaseID] )

		elif bootyOwner[0] != 0:
			# 获得单人杀怪经验
			killers = selfEntity.gainSingleReward( bootyOwner[0] )
		else:
			INFO_MSG( "%s(%i): I died, but no booty owner." % ( selfEntity.className, selfEntity.id ) )
			return

		self.dropItemBox( selfEntity, bootyOwner )
		# 死亡时对任务的判断
		for entity in killers:
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				entity.questMonsterKilled( selfEntity )
		
		# 声望奖励
		killer = BigWorld.entities.get( killerID )
		if killer is None:
			return
				
		if killer.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or killer.isEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER ):
			killer = killer.getOwner()
			if killer is None: return
		elif killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity

		for prestigeItem in self.prestige:
			if not killer.isReal():
				killer.remoteCall( "addPrestige", ( prestigeItem[ 0 ], prestigeItem[ 1 ] ) )
			else:
				killer.addPrestige( prestigeItem[ 0 ], prestigeItem[ 1 ] )

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
		if param is None:
			param = {}
		if param.has_key( 'level' ):
			tempLevel = min( param["level"], self.maxLv )
			param["level"] = max( tempLevel, self.minLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		#设置道行值
		dh_l = g_daoheng.get( param["level"] )
		dh = self._daohengAtt * dh_l
		dh = max( 1, dh )
		param["daoheng"] = dh 
		return NPCObject.createEntity( self, spaceID, position, direction, param )

	def doGoBack( self, selfEntity ):
		"""
		"""
		return selfEntity.gotoPosition( selfEntity.spawnPos )

	def getScriptName( self ):
		"""
		获取自己的脚本名字，该名字可区分不同的怪物类型
		"""
		return self.__class__.__name__

	def antiIndulgenceFilter( self, itemsData, player ):
		"""
		防沉迷系统过滤个人掉落物品（组队不受的掉落不受影响，影响的是分配）
		"""
		if player != None:
			gameYield = player.wallow_getLucreRate()
			print "------->>>>>gameYield = ", gameYield
			newData = []
			if gameYield == 1.0:
				return itemsData
			elif itemsData == 0:
				return newData
			else:
				for i in itemsData:
					if random.random() <= gameYield:
						newData.append( i )
				return newData
		return itemsData

	def getExpAmendRate( self, levelFall ):
		"""
		根据等级差获得经验修正值

		@param levelFall : 玩家和怪物的等级差
		"""
		return AmendExp.instance().getLevelRate( levelFall )

	def getInbornSkillsCount( self ):
		"""
		获得此类怪物天赋技能的个数
		"""
		return len( self.petInbornSkills )
		
	def getInbornSkills( self ):
		"""
		获得此类monster的天赋技能列表
		"""
		return self.petInbornSkills
		
	def getAccumAmemdRate( self, levelFall ):
		"""
		根据等级差获得气运修正值
		@param levelFall : 玩家和怪物的等级差
		"""
		if  -5 <= levelFall < 150:
			return 1.0
		elif -10 <= levelFall < -5:
			return 0.85
		elif -20 <= levelFall < -10:
			return 0.7
		else:
			return 0.5
	
	def onHPChanged( self, selfEntity ):
		"""
		血量发生改变
		"""
		pass
		
	def onWitnessed( self, selfEntity, isWitnessed ):
		"""
		This method is called when the state of this entity being witnessed changes.
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		pass
		
	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		virtual method
		进入陷阱
		"""
		guardTrapID = selfEntity.queryTemp( "guardProximityID", 0 )
		if guardTrapID != 0 and guardTrapID == controllerID:
			return
		state = selfEntity.getState()
		if state == csdefine.ENTITY_STATE_FIGHT or state == csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT:						# 休息状态.....似乎没有用到
			# 在战斗状态的时候取消陷井
			if selfEntity.queryTemp( "proximityID", -1 ) == -1:
				return
			selfEntity.cancel( controllerID )
			selfEntity.removeTemp( "proximityID" )
			selfEntity.removeTemp( "test_Proximity" )
			return

		if selfEntity.checkEnterTrapEntityType( entity ):	# 如果玩家进入我的视野
			DEBUG_MSG( "%s(%i): %s into my initiativeRange." % ( selfEntity.getName(), selfEntity.id, entity.getName() ) )
			DEBUG_MSG( "my position =", selfEntity.position, "role position =", entity.position, "distance =", entity.position.distTo( selfEntity.position ), "my initiativeRange =", selfEntity.initiativeRange, "range =", range )
			selfEntity.aiTargetID = entity.id
			selfEntity.doAllEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP )
			selfEntity.aiTargetID = 0
		
	def onStateChanged( self, selfEntity, old, new ):
		"""
		virtual method
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
			@type new	:	integer
		"""
		pass

	def addComboAI( self, level, comboID, activeRate, ai ):
		"""
		define method.
		向该entity添加comboAI,连续执行
		@param ai   : ai of instance
		@param event: 事件
		@param level: 设定此AI的运行级别, 即 AI系统在此级别时才会运行该AI
		"""
		if isinstance( ai, AIBase ):
			if self.comboAITable.has_key( level ):
				if self.comboAITable[ level ].has_key( comboID ):
					self.comboAITable[ level ][ comboID ]["aiDatas"].append( ai )
					self.comboAITable[ level ][ comboID ]["activeRate"] = activeRate
				else:
					self.comboAITable[ level ][ comboID ] = { "aiDatas": [ ai ], "activeRate": activeRate }
			else:
				self.comboAITable[ level ] = { comboID : { "aiDatas":[ ai ], "activeRate": activeRate } }
		else:
			ERROR_MSG( "addComboAI only receive an AIBase of instance." )
	
	def onChangeTarget( self, selfEntity, oldEnemyID ):
		"""
		virtual method
		"""
		pass
		
	def receiveDamage( self, selfEntity, casterID, skillID, damageType, damage ):
		"""
		virtual method
		"""
		pass
		
	def canThink( self, selfEntity ):
		"""
		virtual method.
		判定是否可以think
		"""
		if selfEntity.state == csdefine.ENTITY_STATE_DEAD or selfEntity.isDestroyed: 		# 死亡了停止think
			return False

		if selfEntity.subState == csdefine.M_SUB_STATE_GOBACK: 						# 如果目前没有玩家看见我或正在回走，那么我将停止think
			return False

		if selfEntity.hasFlag( csdefine.ENTITY_FLAG_MONSTER_THINK ):					# 无论怪物是否被玩家看到都会think(用于40级剧情副本)
			return True

		if not selfEntity.isWitnessed and selfEntity.patrolList is None:
			return False

		return True
		
	def afterDie( self, selfEntity, killerID ):
		"""
		virtual method.
		"""
		g_fightMgr.breakGroupEnemyRelationByIDs( selfEntity, selfEntity.enemyList.keys() )

		selfEntity.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		# 以下代码用于信息统计 10:08 2008-7-21 yk
		k = BigWorld.entities.get( killerID )
		if k is None: return
		if k.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = k.getOwner()
			if owner.etype == "MAILBOX" :
				return
			k = owner.entity
		if k.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			LOG_MSG("NPCClass(%s), NPCName(%s), NPCLevel(%i),databaseID(%i), playerName(%s), playerClass(%i), playerLevel(%i), killTime(%i)"\
				%( selfEntity.className, selfEntity.getName(), selfEntity.level, k.databaseID, k.getName(), k.getClass(), k.level, int( time.time() - selfEntity.fightStartTime ) ) )
			
			try:
				g_logger.actMonsterDieLog( selfEntity.className, k.databaseID, k.getName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def onGetNonRepeatedPatrolGraphID( self, selfEntity, patrolGraphID ) :
		"""
		新副本模板 CopyTemplate 下的 getNonRepeatedPatrolGraphID 方法回调,用于 AIAction300
		加在 Monster 而没有新写怪物脚本的原因：
		添加 AIAction300 是为了让怪物可以整齐的像一波怪物按巡逻路径走来，目前我们这方面没有很好的支持，故加在这里，方便其他怪物也可配置此 AIAction
		"""
		selfEntity.setTemp( "AIAction300_patrolGraphID", patrolGraphID )
		patrolList = BigWorld.PatrolPath( patrolGraphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Patrol(%s) unWorked in %s. it's not ready or not have such patrolGraphID!"%(patrolGraphID, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )) )
		else:
			patrolPathNode, position = patrolList.nearestNode( selfEntity.position )
			selfEntity.doPatrol( patrolPathNode, patrolList  )

	def getOwner( self, selfEntity ):
		"""
		virtual method
		获得所有者
		"""
		return None
		
	def getOwnerID( self, selfEntity ):
		"""
		virtual method
		获得所有者ID
		"""
		return 0
		
	def setOwner( self, selfEntity, owner ):
		"""
		设置所有者
		virtual method
		"""
		pass