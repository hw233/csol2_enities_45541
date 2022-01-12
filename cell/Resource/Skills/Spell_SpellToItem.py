# -*- coding: gb18030 -*-
#
# $Id: Spell_SpellToItem.py,v 1.5 2008-05-31 03:01:19 yangkai Exp $

"""
技能对物品施展法术基础。
"""

from bwdebug import *
from SpellBase import *
import random
import csdefine

class Spell_SpellToItem( Spell ):
	"""
	对物品使用技能基础
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
		owner = target.getOwner()
		if owner.etype != "REAL" : return
		owner.entity.setTemp( "spellItem_uid", target.getUid() )
		Spell.cast( self, caster, owner.entity )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		uid = receiver.queryTemp( "spellItem_uid", -1 )

		item = receiver.getItemByUid_( uid )
		if item is None:
			ERROR_MSG( "%s(%i): ItemUid %i is error." % ( receiver.id, self._id, uid ) )
			return

		#item.setAmount( item.getAmount() - 1, receiver )
		receiver.removeItemByUid_( item.getUid(), 1, csdefine.DELETE_ITEM_SPELLTOITEM )

