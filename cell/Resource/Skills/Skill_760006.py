# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *

from SpellBase import *
from Spell_BuffRacehorse import Spell_BuffRacehorse


class Skill_760006( Spell_BuffRacehorse ):
	"""
	������̶
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffRacehorse.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffRacehorse.init( self, dict )
		self.param = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" )


	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_BuffRacehorse.receive( self, caster, receiver )

	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		caster.removeRaceItem( item.getOrder() )
		caster.removeTemp( "item_using" )


	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		��Ҫ��������Ϣ�����ⲻ��ʹ����Ʒʱ��ʾʹ�ü���
		"""
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON