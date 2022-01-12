# -*- coding: gb18030 -*-
#


"""
BUFF�����ࡣ
"""
from bwdebug import *
from SpellBase import *
import BigWorld
import skills as Skill
import Define

class Buff_108012( Buff ):
	"""
	������������
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		if target == BigWorld.player():
			target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_108012 )

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		if target == BigWorld.player():
			target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_108012  )

	