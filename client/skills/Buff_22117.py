# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.6 2008-07-15 04:08:27 kebiao Exp $

"""
SpellTeach技能类。
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

class Buff_22117( Buff ):
	"""
	多倍经验奖励 杀怪时人物与宠物所获得的经验与潜能提高一倍
	"""
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Buff.__init__( self )
		self.param = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def getDescription( self ):
		sexp = str( self.param["p1"] ) + "%"
		return self._datas[ "Description" ] % sexp
		
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_22117()
		obj.__dict__.update( self.__dict__ )
		obj.param = data["param"]
		return obj

#
# $Log: not supported by cvs2svn $
#
#