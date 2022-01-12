# -*- coding: gb18030 -*-
#
# $Id: Spell_AlwaysTogether.py,v 1.1 2008-04-09 08:44:24 wangshufeng Exp $

"""
"""
from bwdebug import *
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase
import csstatus
import csconst
import csdefine
import BigWorld


class Spell_322361003( Spell_Item, Spell_TeleportBase ):
	"""
	���޼���:��Ӱ����,���͵��������
	ֻҪ�������ߣ�����������ʹ�÷�������������ô���ܹ�ʹ�á�
	����ʹ�õĽ����Σ�����Է��ڸ��������ܴ��͵��Է���ߣ������۴����Ƿ�ɹ���ֻҪʹ�óɹ����Ϳ�ʼcooldown
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		Spell_TeleportBase.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_TeleportBase.init( self, dict )

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
		state = Spell_Item.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# �ȼ��cooldown������
			return state

		state = Spell_TeleportBase.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		if not caster.hasCouple():
			return csstatus.SKILL_COUPLE_DIVORCE
		loverBaseMB = caster.getCoupleMB()
		if loverBaseMB is None:
			DEBUG_MSG( "���( %s )�İ��˲����ߡ�" % ( caster.getName() ) )
			return csstatus.SKILL_LOVER_OFFLINE
			
		caster.setTemp( "couple_teleportRequesting", True )
		loverBaseMB.cell.couple_requestPosition()
		return state
		
	def castValidityCheck( self, caster, receiver ):
		"""
		"""
		state = Spell_Item.castValidityCheck( self, caster, receiver )
		if state != csstatus.SKILL_GO_ON:	# �ȼ��cooldown������
			return state
		if caster.queryTemp( "couple_teleportRequesting", False ):
			teleportInfo = caster.queryTemp( "couple_ringTeleport", () )
			if teleportInfo:
				uid = caster.queryTemp( "item_using" )
				item = caster.getByUid( uid )
				if item is None:
					ERROR_MSG( "cannot find the item form uid[%s]." % uid )
					return
				if teleportInfo[4] != item.query( "creator", "" ):
					return csstatus.SKILL_COUPLE_DIVORCE
				else:
					return csstatus.SKILL_GO_ON
			return csstatus.COUPLE_CANT_TELEPORT_SPECIAL_SPACE
		else:
			return state

	def onSpellInterrupted( self, caster ):
		"""
		��ʩ�������ʱ��֪ͨ��
		��Ϻ���Ҫ��һЩ����
		"""
		Spell_Item.onSpellInterrupted( self, caster )
		caster.removeTemp( "couple_teleportRequesting" )
		caster.removeTemp( "couple_ringTeleport" )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		teleportInfo = caster.queryTemp( "couple_ringTeleport", () )
		caster.removeTemp( "couple_teleportRequesting" )
		caster.removeTemp( "couple_ringTeleport" )
		if teleportInfo:
			caster.gotoSpaceLineNumber( teleportInfo[0], teleportInfo[1], teleportInfo[2], teleportInfo[3] )

# $Log: not supported by cvs2svn $
