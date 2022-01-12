# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Key.py
"""
ʹ����ƷԿ�׿���
"""

from bwdebug import *
from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import BigWorld
import csconst
import csdefine

class Spell_Item_Key( Spell_Item ):
	"""
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
		self._doorID = dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else ""
		print '---------------------------here self._doorID:', self._doorID
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		spaceBase = caster.getCurrentSpaceBase()
		spaceBase.openDoor( { "entityName" : self._doorID } )		# ������
		spaceBase.cell.onConditionChange( {} )						# ����������һ����
		
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if caster.getCurrentSpaceType() != csdefine.SPACE_TYPE_FJSG:		# �����ڷ⽣�񹬲ſ�����
			return csstatus.CIB_MSG_ITEM_NOT_USED_IN_HERE
		return Spell_Item.useableCheck( self, caster, target)
