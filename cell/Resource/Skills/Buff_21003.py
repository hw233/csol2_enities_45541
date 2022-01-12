# -*- coding: gb18030 -*-

"""
持续性效果
"""
import copy

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID
from Domain_Fight import g_fightMgr

class Buff_21003( Buff_Normal ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._param = { "p1" : 0, "p2" : 1 } #p1攻击力, p2伤害倍数

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		param1 = dict[ "Param1" ].split( ";" )
		self._param[ "p1" ] = int( param1[0] ) # 伤害值
		self._damageMultiple = float( param1[1] ) # 伤害倍数
		self._radius = float( dict[ "Param2" ] )
		self._maxCount = int( dict[ "Param3" ] )
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		id = buffData["caster"]
		if BigWorld.entities.has_key( id ):
			caster = BigWorld.entities[ id ]
			p = self.initPhysicsDotDamage( caster, receiver, self._param[ "p1" ] ) # 转换成技能的伤害值
			buffData[ "skill" ] = self.createFromDict( { "param":{ "p1":p } } )

			
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		maxCount = self._maxCount
		entityList = receiver.entitiesInRangeExt( self._radius, None, receiver.position )	
		for e in entityList:
			if receiver.queryRelation( e ) == csdefine.RELATION_ANTAGONIZE:
				damage = self._damageMultiple * self.calcDotDamage( receiver, e, csdefine.DAMAGE_TYPE_MAGIC, int( self._param[ "p1" ] ) )
				
				g_fightMgr.buildEnemyRelation( e, receiver )
				e.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				e.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
				maxCount -= 1
			
				if maxCount <= 0:
					break
					
		return Buff_Normal.doLoop( self, receiver, buffData )

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self._param }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = Buff_21003()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		return obj
