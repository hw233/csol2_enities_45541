# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.6 2008-07-15 04:08:27 kebiao Exp $

"""
SpellTeach�����ࡣ
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

class Buff_6005( Buff_Vehicle ):
	"""
	�����ٶ�Buff�����ĸ��� ��Ϊ������װ������Ӱ��ļ��ٶ�ͬ����ʾ by���� 2009-7-26
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Buff_Vehicle.__init__( self )
		self._p1 = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff_Vehicle.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self._des = dict["Description"]

	def getDescription( self ):
#		sexp = str( self._p1["p1"] ) + "%"
		#player = BigWorld.player()
		#vehicleDBID = player.vehicleDBID
		#baseRate = self._p1
		return self._des
		

#
# $Log: not supported by cvs2svn $
#
#