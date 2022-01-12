# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import random
from Spell_Item import Spell_Item
from bwdebug import *
import BigWorld

class Spell_GrowTree( Spell_Item ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.p1 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.p1 = int( dict[ "param1" ] )		# ��Ч��Ŀ��entity����

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		receiver.onRipe()

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		targetEntity = target.getObject()
		if targetEntity is None: return csstatus.SKILL_CANT_CAST_ENTITY
		if targetEntity.isDestroyed: return csstatus.SKILL_CANT_CAST_ENTITY
		# ʩ��Ŀ�겻��ȷ
		if not targetEntity.isEntityType( self.p1 ): return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		# Ŀ������ѳ���
		if targetEntity.isRipe: return csstatus.FRUIT_ISRIPE
		# Ŀ����������Լ�����
		if targetEntity.planterDBID != caster.databaseID: return csstatus.FRUIT_NOT_YOU

		return Spell_Item.useableCheck( self, caster, target)

