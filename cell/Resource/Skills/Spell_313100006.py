# -*- coding: gb18030 -*-
"""
开启日光浴海滩贝壳的技能 2009-01-15 SongPeifang
"""

from SpellBase import *
from bwdebug import *
import csstatus
import csdefine
import items
import random
import BigWorld
import sys

g_items = items.instance()

class Spell_313100006( Spell ):
	"""
	开启日光浴海滩贝壳,播放动画，获得物品或者产生buff效果
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._receiverObject = ReceiverObject.newInstance( 0, self )# 受术者对象，其中包括受术者的一些合法性判断
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# 施展目标类型，see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		eventRatesStr = dict["param1"].split( '|' )	# 触发各种事件的概率 获得五色珍珠的概率:pram2|获得彩虹宝珠的概率:pram3|获得情缘香珠的概率:pram4|获得彩色珍珠的概率:pram5
		fiveColorPearls = dict["param2"].split( '|' )	# 五色珍珠的集合 id1|id2|id3|id4|id5
		rainbowPearls = dict["param3"].split( '|' )	# 彩虹宝珠的集合 id1|id2|id3|id4|id5|id6|id7
		friendlyPearls = dict["param4"].split( '|' )	# 情缘香珠的集合 id1|id2
		colorPearls = [ dict["param5"] ]				# 彩色珍珠 id
		tempDict = { "param2":fiveColorPearls, "param3":rainbowPearls, "param4":friendlyPearls, "param5":colorPearls }

		self._ratesEvent = {}						# 概率及对应的事件 {概率:物品数组} 如 {0.15:[50101046,50101047,50101048,50101049,50101050]}
		tempRate = 0								# 整数
		for rateStr in eventRatesStr:				# eventRatesStr就是数组[ "0.15:param2", "0.15:param3", "0.5:param4", "0.25:param5", "0.4:param6" ]
			tempArr = rateStr.split( ':' )			# tempArr就是数组[概率,参数名] 如 [0.5,param3]
			rate = tempRate + int( ( float( tempArr[0] ) + 0.0005 ) * 1000 ) # 概率要加起来作为Key这样绝对不会重复，因为不会配成0
			self._ratesEvent[ rate ] = tempDict[ tempArr[1] ]	# {概率(整数，后面要除以1000的):物品数组}
			tempRate = rate

	def getIntonateTime( self , caster ):
		"""
		virtual method.
		获取技能自身的吟唱时间，此吟唱时间如果有必要，可以根据吟唱者决定具体的时长。

		@param caster:	使用技能的实体。用于以后扩展，如某些天赋会影响某些技能的默认吟唱时间。
		@type  caster:	Entity
		@return:		释放时间
		@rtype:			float
		"""
		return caster.queryTemp( "quest_box_intone_time", 0.0 )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_GO_ON

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None or entity.isDestroyed:
			return []
		return [ entity ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		# 施法者可能找不到 参见receiveOnReal接口
		if not caster:
			return

		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 回调以让箱子自己执行某些事情
		receiver.onReceiveSpell( caster, self )
		eventRate = random.random()
		items = []	# String数组，储存物品ID的字符串
		keyArray = self._ratesEvent.keys()
		keyArray.sort()
		for r in keyArray:
			if eventRate <= r/1000.0:
				items = self._ratesEvent[r]
				break
		if len( items ) > 0:
			# 找到了物品列表，说明这个贝壳是掉物品的
			direction = (0.0, 0.0, 0.0)
			pos = receiver.position					# 掉落的位置
			propDict = { "ownerIDs": [caster.id] }	# 锁定捡取对像
			index = random.randint( 0, len( items )-1 )
			itemID = int( items[ index ] )
			# 计算偏移位置
			x1 = random.randint( -1, 1 )
			y1 = 1
			z1 = random.randint( -1, 1 )
			# 开始放道具
			amount = 1
			item = g_items.createDynamicItem( itemID , amount )
			tmpList = [ item ]
			x, y, z = x1 + pos[0], y1 + pos[1], z1 + pos[2]	# 计算出放置的位置的偏移位置
			bootyOwner = ( caster.id, 0 )
			collide = BigWorld.collide( caster.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
			if collide != None:
				# 掉落物品的时候对地面进行碰撞检测避免物品陷入地下
				y = collide[0].y
			itemBox = receiver.createEntityNearPlanes( "DroppedBox", (x, y, z), direction, {} )
			itemBox.init( bootyOwner, tmpList )
		else:
			# 没有找到物品列表，说明eventRate不在掉落物品的概率内，即本次贝壳会释放buff
			receiveScript = receiver.getScript()
			skills = receiveScript.param1.split( "|" )
			if len( skills ) == 0:
				ERROR_MSG( "贝壳QuestBox参数错误,无效的技能ID!" )
			index = random.randint( 0, len( skills )-1 )
			skill = int( skills[ index ] )
			receiver.spellTarget( skill, caster.id )
