# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffNormal.py,v 1.10 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
import csconst
from Spell_Item import Spell_Item

class Spell_922218( Spell_Item ):
	"""
	�շѵ��߾��齱��
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
		self._expHour = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  	#��������Сʱ��

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
		if caster.takeExpRecord[ "freezeTime" ] > 0:
			return csstatus.TAKE_EXP_NOT_RESUME_FAIL
		
		buffs = caster.findBuffsByBuffID( 22117 )
			
		if len( buffs ) > 0:
			buff = caster.getBuff( buffs[ 0 ] )["skill"]
			if ( buff._persistent + self._expHour ) > 5 * 60 * 60: # ������ӵ����Ͻ��ᳬ��5Сʱ ��˲�����
				return csstatus.TAKE_EXP_HOUR_MAX
				
			sk = caster.getBuff( buffs[ 0 ] )["skill"]
			sexp = str( sk.getPercent() ) + "%"
			selfBuff = self.getBuffLink(0).getBuff()
			
			if sk.getPercent() == selfBuff.getPercent():
				# ��ѵ������շѵ���ֻ����һ��
				if sk.isCharge != selfBuff.isCharge:
					if selfBuff.isCharge:
						caster.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp )
					else:
						caster.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST, sexp )
					return csstatus.SKILL_NO_MSG
			elif sk.getPercent() < selfBuff.getPercent():
				# �����ǰҪ��ӵĸ߱���BUFF����ѵģ� ���ϵĵױ������շѵ��ߣ� ��������
				if sk.isCharge and not selfBuff.isCharge:
					caster.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE1, sexp )
					return csstatus.SKILL_NO_MSG
			else:
				if selfBuff.isCharge:
					caster.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp )
				else:
					caster.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST, sexp )
				return csstatus.SKILL_NO_MSG
				
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		receiver.setTemp( "rewardExpHour", self._expHour )
		self.receiveLinkBuff( caster, receiver )		# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)
		
#
# $Log: not supported by cvs2svn $#
#
#