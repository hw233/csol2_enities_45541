# -*- coding: gb18030 -*-
#
# 召唤保护怪技能

from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal
from ObjectScripts.GameObjectFactory import g_objFactory



class Spell_ProtectedSummon( Spell_BuffNormal ):
	"""
	召唤
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )
		self.className = "" #创建的NPC的classname
		self.level = 1	#创建的NPC等级 默认1
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.className = dict["param1"]
		if dict["param2"] != "" :
			self.level = int(dict["param2"])


	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		entity = receiver.createObjectNearPlanes( self.className, tuple( receiver.position ), receiver.direction,{"level":self.level,"spawnPos":tuple( receiver.position ) } )
		entity.targetID = receiver.id
		self.receiveLinkBuff( caster, receiver )
		
