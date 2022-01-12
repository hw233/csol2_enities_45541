# -*- coding: gb18030 -*-

"""
����buff
"""

import math
import items
from bwdebug import *
from SpellBase import *
from Function import Functor
import BigWorld
import skills as Skill
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
from Buff_Vehicle import Buff_Vehicle

class Buff_8006( Buff_Vehicle ):
	"""
	����buff
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Buff_Vehicle.__init__( self )
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff_Vehicle.init( self, dict )
		self._des = dict["Description"]
		self._speedInc = int( dict[ "Param1" ] )

	def getDescription( self ):
		"""
		��ȡ��buff������
		"""
		# ����û����Ӧ�����װ��������ֻ��ʾ�������٣����Ժ����ó��˷�������״̬�����Ը���װ����������٣��ο�buff 6005
		return self._des
	
	
	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff_Vehicle.cast( self, caster, target )
		if target == BigWorld.player():
			target.onEnterFlyState()
	
	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff_Vehicle.end( self, caster,target )

		if target == BigWorld.player():
			# �·������ֹͣ�Զ�Ѱ·
			target.endAutoRun( False )
			target.onLeaveFlyState()
