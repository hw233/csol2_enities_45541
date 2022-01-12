# -*- coding: gb18030 -*-
#
# $Id: Spell_DigMonster.py,v 1.7 2007-12-18 04:15:42 kebiao Exp $

"""
"""

from SpellBase import *
from bwdebug import *
import ECBExtend
import LostItemDistr
from ObjectScripts.GameObjectFactory import g_objFactory

class Spell_DigMonster( Spell ):
	"""
	召唤
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

		summonsSection = dict["Summons"]
		self._npcs = []											# like as [npc_class_key_name, ...]
		self._lifetime = 0										# NPC/MONSTER存在时间，单位：秒；如果为0则表示不自动消失
		for sec in summonsSection.values():
			if sec.name == "Lifetime":
				self._lifetime = summonsSection.readInt( "Lifetime" )			# 读取存活时间
			elif sec.name == "NPC":
				self._npcs.append( sec.asString )

	def getReceivers( self, caster, targetEntity ):
		"""
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。

		@rtype: list of Entity
		"""
		return []

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		接受法术之前所要做的事情
		"""
		assert receiver is not None		# 强制只能对entity使用

		# 召唤术无目标
		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# 根据等级取得掉落物品分布图
		direction = receiver.direction
		pos = receiver.position

		# 开始放NPC
		for keyName in self._npcs:
			x1, z1 = itemDistr.pop(0)										# 取得偏移位置
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# 计算出放置的位置
			entity = receiver.createObjectNearPlanes( keyName, (x, y, z), direction, {} )
			entity.spawnPos = (x, y, z)	# 制定出生点用于追击范围
			if self._lifetime > 0:
				# 增加一个自动消失的time
				entity.addTimer( self._lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
