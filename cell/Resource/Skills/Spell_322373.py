# -*- coding: gb18030 -*-
"""
�ҽ𵰻�������ӣ����װ������
"""
import csstatus
import random
import items
import BigWorld
import items
import csdefine
import sys
from Spell_Item import Spell_Item
from bwdebug import *
from items.ItemDropLoader import ItemDropInWorldLoader
from items.EquipEffectLoader import EquipEffectLoader

g_itemTreasureBoxPinkDrop = ItemDropInWorldLoader.instance()
from csarithmetic import getRandomElement

g_items = items.instance()

class Spell_322373( Spell_Item ):
	"""
	�ҽ𵰻�������ӣ����װ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._boxLevel = 1							# ����ļ���

		self.dropItemStr = dict["param1"]			# ���������ɫ��Ʒ�������� like:   " 2(������ɫ):70;3:30"

		self._dropItemColorList = []				# �����Ʒ����ɫ
		self._dropItemOddsList = []					# �����Ʒ��ɫ��Ӧ�Ļ�������
		for e in self.dropItemStr.split( ";" ):
			self._dropItemColorList.append( str( e.split( ":" )[0] ) )
			self._dropItemOddsList.append( float( e.split( ":" )[1] ) )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		drop = random.random()

		tmpList = []
		tmpList = self.getTreasureBoxDropItems( receiver )

		if len( tmpList ) == 0:
			Spell_Item.receive( self, caster, receiver )
			return
		bootyOwner = ( caster.id, 0 )
		x1 = random.randint(-1,1)
		z1 = random.randint(-1,1)
		pos = caster.position							# �����λ�ã���ҵ�λ�ã�
		x, y, z = x1 + pos[0], pos[1], z1 + pos[2]		# ����ƫ�������������λ��
		direction = (0.0, 0.0, 0.0)						# ����
		collide = BigWorld.collide( caster.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
		if collide != None:
			# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
			y = collide[0].y
		params = { "dropType" : csdefine.DROPPEDBOX_TYPE_STROE }
		itemBox = receiver.createEntityNearPlanes( "DroppedBox", (x, y, z), direction, params )
		itemBox.init( bootyOwner, tmpList )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		uid = caster.queryTemp( "item_using")
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		self._boxLevel = item.getLevel()
		return Spell_Item.useableCheck( self, caster, target)

	def getTreasureBoxDropItems( self, player ):
		"""
		��ȡ�������
		"""
		dropList = []

		if self._boxLevel == None:
			self._boxLevel = 1

		color = int( getRandomElement( self._dropItemColorList, self._dropItemOddsList ) )		# ���ݸ��ʣ�ѡȡ��Ʒ��ɫ
		dropDatas = g_itemTreasureBoxPinkDrop.getDropItemsEx( color, self._boxLevel )
		if len( dropDatas ) == 0: return dropList

		dropRate = random.random() * g_itemTreasureBoxPinkDrop.getItemsTotalOddsEx( color, self._boxLevel )
		for itemID, quality, prefix, dropOdds in dropDatas:
			if dropRate <= dropOdds:
				itemInst = g_items.createDynamicItem( int( itemID ) , 1 )
				if quality!=0 and prefix != 0:
					itemInst.setQuality( quality )
					itemInst.setPrefix( prefix )
					if not itemInst.createRandomEffect():
						DEBUG_MSG( "getDropPinkItems createRandomEffect failed, item %s, quality %s, prefix %s " % ( itemID, quality, prefix ) )
				itemInst.set( "level", self._boxLevel )
				dropList.append( itemInst )
				break
		return dropList
