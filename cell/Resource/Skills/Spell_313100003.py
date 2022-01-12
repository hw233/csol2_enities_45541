# -*- coding: gb18030 -*-
#
# $Id: Spell_313100003.py,v 1.9 2008-04-16 08:26:50 zhangyuxing Exp $

"""
"""

from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
import LostItemDistr
import ECBExtend
import BigWorld
import random

MONSTER_RANGE = 50.0				#查找周围怪物的半径

class Spell_313100003( Spell ):
	"""
	召唤
	启动召唤类场景物件，播放动画，召唤怪物
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
		#增加处理，如果一定范围内，找到属于自己的任务怪，则不能再通过任务箱子招唤任务怪
		receiveScript = target.getObject().getScript()
		monsterList = caster.entitiesInRangeExt( MONSTER_RANGE, "Monster", caster.position )
		for m in monsterList:
			if m.className in ( receiveScript.param1, receiveScript.param4, receiveScript.param7 ):
				if m.bootyOwner[1] == 0 and m.bootyOwner[0] == caster.id:
					return csstatus.SKILL_INTONATING
				if caster.teamMailbox is not None and m.bootyOwner[1] == caster.teamMailbox.id:
					return csstatus.SKILL_INTONATING
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

		receiveScript = receiver.getScript()
		npcConfig = (
			( receiveScript.param1, receiveScript.param2, receiveScript.param3, ),
			( receiveScript.param4, receiveScript.param5, receiveScript.param6, ),
			( receiveScript.param7, receiveScript.param8, receiveScript.param9, ),
		)
		rateInt = random.randint( 0, 100 )
		npcs = []
		for npcID, amount, rate in npcConfig:
			if len( npcID ):
				if rate > rateInt:
					amount = int( amount )
					npcs.extend( [ npcID, ] * amount )


		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# 根据等级取得掉落物品分布图
		direction = receiver.direction
		pos = receiver.position

		# 开始放NPC
		for keyName in npcs:
			itemDistr.pop(0)
			x1, z1 = itemDistr[ random.randint( 0, len( itemDistr ) - 1 ) ]	# 取得偏移位置
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# 计算出放置的位置
			entity = receiver.createObjectNearPlanes( keyName, (x, y+2, z), direction, {} )

			# 对召唤出来的任务怪特殊处理，直接设置其bootyOwner
			getEnemyTeam = getattr( caster, "getTeamMailbox", None )	# 如果有队伍则记录队伍mailbox
			if getEnemyTeam and getEnemyTeam():
				entity.bootyOwner = ( caster.id, getEnemyTeam().id )
			else:
				# 进入战斗状态后第一个产生伤害目标将被作为所有者
				entity.bootyOwner = ( caster.id, 0 )
			entity.firstBruise = 1		# 避免Monster中第一次受伤害对bootyOwner处理

			#entity.spawnMB = receiver.base
			receiver.getScript().addMonsterCount( receiver, 1 )
			entity.spawnPos = (x, y, z)	# 制定出生点用于追击范围
			receiver.entityDead()
			"""
			if self._lifetime > 0:
				# 增加一个自动消失的time
				entity.addTimer( self._lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
			"""

# $Log: not supported by cvs2svn $
# Revision 1.8  2007/12/27 03:29:54  phw
# method modified: receive(), 修正无法正确召唤怪物的bug
#
# Revision 1.7  2007/12/27 02:00:39  phw
# method modified: getIntonateTime(), popTemp -> queryTemp
#
# Revision 1.6  2007/12/22 08:23:09  kebiao
# 修改导入模块
#
# Revision 1.5  2007/12/22 08:10:18  kebiao
# 因为该行为是固定的 所以强制了一些条件
#
# Revision 1.4  2007/12/22 03:26:01  kebiao
# 修正吟唱
#
# Revision 1.3  2007/12/22 01:06:12  phw
# method modified: receive(), 对receiver进行回调onReceiveSpell()
#
# Revision 1.2  2007/12/18 05:57:56  kebiao
# 覆盖了一些基础类接口， 因为此技能为固定情况下才会使用的东西不会有这些需求存在
#
# Revision 1.1  2007/12/18 04:16:30  kebiao
# no message
#
#