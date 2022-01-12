# -*- coding: gb18030 -*-

"""
"""
# 图腾技能

import BigWorld
import random
from SpellBase import *
import csstatus
import items
import LostItemDistr
import csdefine
import utils

areaToNumList = {
					'a' : [1,2],
					'b' : [2,3],
					'c' : [3,4],
					'd' : [4,5],
					'e' : [5,1]
				}

class Spell_laser( Spell ):
	"""
	图腾技能
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
		self.param2 = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 				# 图腾作用怪物的entityType

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

		entityList = receiver.entitiesInRangeExt( self.param1, self.param2, receiver.position )
		if len( entityList ) <= 0:
			receiver.onReceiveSpell( caster, self )
			return
		# 如果在一定范围内，找到entityType的entity
		findEntity = entityList[0]

		# 转向--机关转向目标
		y = utils.yawFromPos( receiver.position, findEntity.position )
		receiver.direction = ( 0, 0, y )
		receiver.planesAllClients( "setFilterYaw", ( y, ) )

		area = findEntity.queryTemp( "trapArea", 'a' )		# 取出findEntity上代表所在区域
		numList = areaToNumList[area]					# 找到findEntity所在区域，对应的机关编号

		spaceBase = BigWorld.cellAppData["spaceID.%i" % receiver.spaceID]
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# 找到副本
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		lastNum = spaceEntity.queryTemp( "lastNum", 0 ) # 取出spaceEntity副本中上次记录的机关编号

		num = int(receiver.getScript().param1)		# 取出laser的编号，这次开启的机关编号

		if [lastNum,num] == numList or [num, lastNum] == numList: 		# 如果，先后2次开启的机关 符合规则
			findEntity.onDestroySelfTimer(0,0)		# 机关生效，销毁findEntity
			spaceEntity.setTemp( "lastNum", 0 )		# 机关生效后，把最后一次点击的机关记录设置为0；重新开始。
		else:
			spaceEntity.setTemp( "lastNum", num )	# spaceEntity副本中没有触发，覆盖上一次值

		receiver.onReceiveSpell( caster, self )
