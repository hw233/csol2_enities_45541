# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.6 2008-07-15 04:08:27 kebiao Exp $

"""
SpellTeach技能类。
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
	骑宠加速度Buff描述的更改 改为可以与装备更换影响的加速度同步显示 by姜毅 2009-7-26
	"""
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Buff_Vehicle.__init__( self )
		self._p1 = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
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