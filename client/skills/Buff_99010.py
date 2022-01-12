# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.6 2008-07-15 04:08:27 kebiao Exp $

"""
SpellTeach�����ࡣ
"""
import math
from bwdebug import *
from SpellBase import *
from Function import Functor
import BigWorld
import skills as Skill
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
import Define

class Buff_99010( Buff ):
	"""
	example:��贫��	BUFF	��ɫ�ڴ��ڼ䲻�ᱻ������ ���ᱻ��ҿ��ƣ� ���Ϸ���ģ��
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )
		self.teleportVehicleModelNumber = ""
		self.teleportVehicleSeat = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )
		self.teleportVehicleModelNumber = dict[ "Param1" ]
		if len( dict[ "Param2"] ) == 0:
			self.teleportVehicleSeat = 0
		else:
			self.teleportVehicleSeat = int( dict[ "Param2"] )

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_99010 )
		target.filter = BigWorld.AvatarFilter()

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_99010 )
		target.filter = target.filterCreator()

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_99010()
		obj.__dict__.update( self.__dict__ )
		obj.param = data["param"]
		return obj

#
# $Log: not supported by cvs2svn $
#
#