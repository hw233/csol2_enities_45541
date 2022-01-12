# -*- coding: gb18030 -*-

"""
"""
# 图腾技能

import random
from SpellBase import *
import csstatus
import items
import LostItemDistr
import csdefine

BUFF_ID1_1		=	13008
BUFF_ID1_2		=	13009
BUFF_ID1_3		=	13010
BUFF_ID2		=	62004
BUFF_ID_S = [BUFF_ID1_1, BUFF_ID1_2, BUFF_ID1_3]

class Spell_313100007( Spell ):
	"""
	巫妖王之影专用图腾技能
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
		
		self.param1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 			# 图腾作用距离
		self.param2 = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 		# 图腾作用怪物的className
		
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# 受术者对象，其中包括受术者的一些合法性判断
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# 施展目标类型，see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		
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
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		
		isFindBoss = False
		boss = None
		monsterList = receiver.entitiesInRangeExt( self.param1, "Monster", receiver.position )
		for e in monsterList:
			if e.className == self.param2:
				boss = e
				isFindBoss = True
				break
		if boss is None or not isFindBoss:
			receiver.onReceiveSpell( caster, self )
			return
		boss.removeTemp( "buffBeInteruptFromTuteng" )
		# 如果在一定范围内，找到相应的boss
		# 判断开启的图腾是否与boss的buff一致
		for buffID in BUFF_ID_S:
			if len( boss.findBuffsByBuffID(buffID) ) <= 0:	# 如果boss身上没有buff
				continue
			if int( receiver.getScript().param2 ) != buffID:
				boss.addHP( int(boss.HP_Max / 10) )	# 给boss增加10%的血量
				continue
			boss.removeAllBuffByBuffID( buffID, [csdefine.BUFF_INTERRUPT_NONE]  )
			boss.removeAllBuffByBuffID( BUFF_ID2, [csdefine.BUFF_INTERRUPT_NONE]  )
			boss.setTemp("buffBeInteruptFromTuteng",True)
			
		if boss.queryTemp("buffBeInteruptFromTuteng"):
			# 特殊任务需求，减少BOSS身上一个技能的使用次数属性
			skUseCount = boss.queryTemp( "uskCount", 0 )
			boss.setTemp( "uskCount", skUseCount - 1 )
			
		receiver.onReceiveSpell( caster, self )