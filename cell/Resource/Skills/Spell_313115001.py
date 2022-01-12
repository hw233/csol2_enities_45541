# -*- coding: gb18030 -*-
#

from bwdebug import *
import random
from SpellBase import *
import csstatus
import items
import LostItemDistr
import csdefine
import BigWorld
import sys

g_items = items.instance()

class Spell_313115001( Spell ):
	"""
	异界战场占领阵营柱时所用技能
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
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# 受术者对象，其中包括受术者的一些合法性判断
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE			# 施展目标类型，see also CAST_OBJECT_TYPE_*
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
		
		if BigWorld.entities.has_key( caster.id ) and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			if caster.yiJieFaction != 0 and caster.yiJieFaction == target.getObject().ownBattleFaction :
				caster.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_OCCUPY_AGAIN, "" )
				return
			elif caster.yiJieAlliance != 0 and caster.yiJieAlliance == target.getObject().ownBattleFaction :
				caster.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_OCCUPY_ALLIANCE, "" )
				return
		return Spell.useableCheck( self, caster, target )
		

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

		#receiver.onReceiveSpell( caster, self )

		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# 根据等级取得掉落物品分布图
		itemDistr.pop(0)	# 去掉第0位,因为第0位在人物中心,捡不起来
		direction = (0.0, 0.0, 0.0)
		pos = receiver.position

		#  锁定捡取对像
		propDict = { "ownerIDs": [caster.id] }

		receiveScript = receiver.getScript()
		items = (
			( receiveScript.param1, receiveScript.param2, receiveScript.param3 ),
			( receiveScript.param4, receiveScript.param5, receiveScript.param6 ),
			#( receiveScript.param7, receiveScript.param8, receiveScript.param9 ),
		)

		# 开始放道具
		tempList = []
		for keyName, amount, rate in items:
			if len( keyName ) == 0:
				continue
				
			if not rate:
				continue
				
			if random.random() > float( rate ):
				continue
				
			amount = int( amount )

			item = g_items.createDynamicItem( int( keyName, 10 ), 1 )
			if item is None:
				ERROR_MSG( "Create drop item error: monster's className:%s ,item's ID:%s" % ( receiver.className, int( keyName, 10 ) ) )
				continue
			item.setAmount( amount )
			tempList.append( item )

		receiver.onItemsArrived( caster, tempList )

