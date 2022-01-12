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
	�ڵ�����һ����Ʒ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		dropitemSection = dict["Dropitem"]
		self._items = []											# like as [(itemKeyName, itemAmount), ...]
		self._lockedPicker = False
		for sec in dropitemSection.values():
			if sec.name == "LockedPicker":
				self._lockedPicker = dropitemSection.readInt( "LockedPicker" )			# �Ƿ�����ʰȡ��Ϊ������(�Ƿ�ֻ�������߿��Լ�)
			elif sec.name == "Item":
				itemKeyName = sec.readInt( "KeyName" )			# ��ƷID
				itemAmount = sec.readInt( "Amount" )				# ��Ʒ��������
				if itemAmount > 0:
					self._items.append( (itemKeyName, itemAmount) )
				else:
					WARNING_MSG( "in %s, item amount is %i, ignore." % (( dict[ "Name" ] if len( dict[ "Name" ] ) > 0 else "" ) , itemAmount) )	

	def getReceivers( self, caster, target ):
		"""
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��

		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None:
			return []
		return [ entity ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# ���ݵȼ�ȡ�õ�����Ʒ�ֲ�ͼ
		itemDistr.pop(0)	# ȥ����0λ,��Ϊ��0λ����������,������
		direction = (0.0, 0.0, 0.0)
		pos = caster.position

		#  ������ȡ����
		if self._lockedPicker:
			propDict = { "ownerIDs": [receiver.id], "planesID" : receiver.planesID }
		else:
			propDict = {}

		# ��ʼ�ŵ���
		for keyName, amount in self._items:
			x1, z1 = itemDistr.pop(0)										# ȡ��ƫ��λ��
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# ��������õ�λ��

			entity = g_items.createEntity( keyName, caster.spaceID, (x, y, z), direction, propDict )
			if entity is None:
				ERROR_MSG( "no such item. %s" % errstr )
			else:
				entity.itemProp.setAmount( amount )