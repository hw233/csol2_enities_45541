# -*- coding: gb18030 -*-
#
# $Id: Spell_SpellToItem.py,v 1.5 2008-05-31 03:01:19 yangkai Exp $

"""
���ܶ���Ʒʩչ����������
"""

from bwdebug import *
from SpellBase import *
import random
import csdefine

class Spell_SpellToItem( Spell ):
	"""
	����Ʒʹ�ü��ܻ���
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

	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		owner = target.getOwner()
		if owner.etype != "REAL" : return
		owner.entity.setTemp( "spellItem_uid", target.getUid() )
		Spell.cast( self, caster, owner.entity )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
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

