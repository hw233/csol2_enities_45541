# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.5 2008-07-15 04:08:27 kebiao Exp $

"""
��ͨ������
"""
import BigWorld
import csdefine
import csstatus
import ItemTypeEnum
from bwdebug import *
from skills.SpellBase import *
from Time import Time

class Spell_Physics( Spell ):
	"""
	��ͨ������
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		��ü������͡�
		"""
		return csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL

	def getRangeMax( self, caster ):
		"""
		�����̡�
		"""
		return caster.range	# ��ͨ������ͨ��role�Ĺ����������жϳ���

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if Time.time() < caster.hitDelay + 0.05:					# if current interval less than interval of player in hit
			return csstatus.SKILL_NOT_HIT_TIME							# set this the sign
		return Spell.useableCheck( self, caster, target )
	
	def getIcon( self ):
		pl = BigWorld.player()
		try:
			if pl.primaryHandEmpty():
				return Spell.getIcon( self )
			else:
				item = pl.getItem_( ItemTypeEnum.CWT_RIGHTHAND )
				return item.icon()
		except AttributeError, errstr:
			WARNING_MSG( errstr )
			return Spell.getIcon( self )
