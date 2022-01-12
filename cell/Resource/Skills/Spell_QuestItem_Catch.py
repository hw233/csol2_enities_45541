# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from Spell_Item import Spell_Item
import items
import random
import csdefine
import ECBExtend
g_items = items.instance()

class Spell_QuestItem_Catch( Spell_Item ):
	"""
	抓捕怪物生成任务道具
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		self._monsterID = ""		# 怪物ID
		self._isAllCatch = False	# 是否全部抓捕
		self._itemID = 0			# 任务物品ID

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._monsterID = str( dict["param1"] )
		self._isAllCatch = bool( int( dict["param2"] ) )	# 填0抓捕一个，填1全部抓捕
		self._itemID = int( dict["param4"] )

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 引导技能检测
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )

		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		if delay <= 0.5:
			# 瞬发
			self.onArrive( caster, target )
		else:
			# 延迟
			caster.addCastQueue( self, target, delay )

		#更新物品 只有物品成功使用之后才可以对物品的消减进行操作
		self.updateItem( caster )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 获取所有受术者
		receivers = self.getReceivers( caster, target )
		usefulReceivers = []
		for receiver in receivers:
			if not hasattr( receiver, "className" ) or receiver.className != self._monsterID:	# 不符合条件的受术者直接跳过
				continue
			receiver.clearBuff( self._triggerBuffInterruptCode )
			usefulReceivers.append( receiver )

		if self._isAllCatch:	# 全部抓捕
			for re in usefulReceivers:
				self.receive( caster, re )
				self.receiveEnemy( caster, re )
		else:
			if len( usefulReceivers ):
				en = random.choice( usefulReceivers ) # 随机取一个
				self.receive( caster, en )
				self.receiveEnemy( caster, en )

		if not caster.isDestroyed:
			caster.onSkillArrive( self, usefulReceivers )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell_Item.receive( self, caster, receiver )

		receiver.addTimer( 0.1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )	# 销毁怪物
		item = g_items.createDynamicItem( self._itemID , 1 )
		caster.addItem( item, csdefine.ADD_ITEM_QTSGIVEITEMS )	# 任务道具