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

class Buff_108007( Buff ):
	"""
	������
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
		if not caster:return
		target.beHomingCasterID = caster.id
		if target.id == BigWorld.player().id:
			target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_108007  )

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		target.beHomingCasterID = 0
		target.homingDir = None
		if target.id == BigWorld.player().id:
			target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_108007  )
	