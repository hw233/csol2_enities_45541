# -*- coding: gb18030 -*-
#
# $Id: $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID
import csdefine
from Domain_Fight import g_fightMgr


class Buff_107018( Buff_Normal ):
	"""
	example:使目标每2秒一次直接伤害185(30级)/439(60级)点，持续10秒。如果目标在此过程中死亡，将对周围5米最多10个目标造成每个494/1171点直接伤害。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 # 消耗总hP值 
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		value = dict[ "Param1" ].split(",")
		self._p1 = int( value[0] )
		self._p2 = int( value[1] )
		
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
			p = self.initMagicDotDamage( caster, receiver, self._p1 )
			
			buff = self.createFromDict( { "param":{ "p1":p, "rid" : receiver.id, "casterID" : id } } )
			buffData[ "skill" ] = buff
			
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
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_MAGIC, self._p1 )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
		return Buff_Normal.doLoop( self, receiver, buffData )

	def cancelBuff( self, reasons ):
		"""
		virtual method.
		取消一个BUFF
		@param reasons: 取消的原因
		@rtype  : bool
		"""
		if not Buff_Normal.cancelBuff( self, reasons ):
			return False
		
		if csdefine.BUFF_INTERRUPT_ON_DIE in reasons:
			maxCount = self._maxCount
			receiver = BigWorld.entities.get( self._param[ "rid" ] )			
			casterID = self._param[ "casterID" ]			
			# 尝试寻找一下施法者，如果找不到就不再执行AOE伤害 by mushuang
			caster = BigWorld.entities.get( casterID )
			if not caster: return True
			entityList = receiver.entitiesInRangeExt( self._radius, receiver.__class__.__name__, receiver.position )	
			for e in entityList:
				if caster.queryRelation( e ) != csdefine.RELATION_ANTAGONIZE: continue
				if e.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0: continue
				damage = self.calcDotDamage( receiver, e, csdefine.DAMAGE_TYPE_MAGIC, self._p2 )
				g_fightMgr.buildEnemyRelation( e, caster )
				e.receiveSpell( casterID, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				e.receiveDamage( casterID, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
					
				maxCount -= 1
			
				if maxCount <= 0:
					break
						
		return True
		
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
		obj = Buff_107018()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
		
#
# $Log: not supported by cvs2svn $
#