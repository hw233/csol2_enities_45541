# -*- coding: gb18030 -*-
#
# $Id: Spell_DropItem.py,v 1.11 2008-08-09 01:52:53 wangshufeng Exp $

"""
"""

from SpellBase import *
from bwdebug import *
import items
import LostItemDistr

g_items = items.instance()

class Spell_DropItem( Spell ):
	"""
	在地上扔一个物品
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

		dropitemSection = dict["Dropitem"]
		self._items = []											# like as [(itemKeyName, itemAmount), ...]
		self._lockedPicker = False
		for sec in dropitemSection.values():
			if sec.name == "LockedPicker":
				self._lockedPicker = dropitemSection.readInt( "LockedPicker" )			# 是否锁定拾取者为受术者(是否只有受术者可以捡)
			elif sec.name == "Item":
				itemKeyName = sec.readInt( "KeyName" )			# 物品ID
				itemAmount = sec.readInt( "Amount" )				# 物品叠加数量
				if itemAmount > 0:
					self._items.append( (itemKeyName, itemAmount) )
				else:
					WARNING_MSG( "in %s, item amount is %i, ignore." % (( dict[ "Name" ] if len( dict[ "Name" ] ) > 0 else "" ) , itemAmount) )	

	def getReceivers( self, caster, target ):
		"""
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。

		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None:
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

		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# 根据等级取得掉落物品分布图
		itemDistr.pop(0)	# 去掉第0位,因为第0位在人物中心,捡不起来
		direction = (0.0, 0.0, 0.0)
		pos = caster.position

		#  锁定捡取对像
		if self._lockedPicker:
			propDict = { "ownerIDs": [receiver.id], "planesID" : receiver.planesID }
		else:
			propDict = {}

		# 开始放道具
		for keyName, amount in self._items:
			x1, z1 = itemDistr.pop(0)										# 取得偏移位置
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# 计算出放置的位置

			entity = g_items.createEntity( keyName, caster.spaceID, (x, y, z), direction, propDict )
			if entity is None:
				ERROR_MSG( "no such item. %s" % errstr )
			else:
				entity.itemProp.setAmount( amount )