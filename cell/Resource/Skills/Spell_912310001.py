# -*- coding: gb18030 -*-
#
# $Id: Spell_912310001.py,v 1.1 2008-08-12 08:55:15 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import csdefine
import csconst

class Spell_912310001( Spell_Item ):
	"""
	����������	����								�����߼����Ա�ٻ����Լ���ߣ�ֻ���峤ʹ�á�
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

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if not target.getObject().isTongChief():
			return csstatus.TONG_CHIEF_ITEM
		if not target.getObject().tong_getTongEntity( target.getObject().tong_dbID ):
			return csstatus.TONG_CHIEF_ITEM
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		position = receiver.position
		dbid = receiver.databaseID
		lineNumber = receiver.getCurrentSpaceLineNumber()
		tong = receiver.tong_getTongEntity( receiver.tong_dbID )
		if tong:
			tong.chiefCommand_conjure( dbid, lineNumber, spaceType, position )
		
# $Log: not supported by cvs2svn $
#