# -*- coding: gb18030 -*-
#


"""
持续性效果
"""
import random
import Math
import BigWorld
import time
import csstatus
import csdefine
import csconst
from bwdebug import *
from Function import newUID

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal



class Buff_22135( Buff_Normal ):
	"""
	舞王经验buff
	(Lv^1.5 * 3.5 + 9) * param1  #每分钟获得经验；
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 )

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
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #每分钟获得经验
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCEKING_BUFF )
		DEBUG_MSG("Buff_22135 doLoop add exp:%f to playerName:%s"%(exp, receiver.playerName))
		return Buff_Normal.doLoop( self, receiver, buffData )

	def receive( self, caster, receiver ):
		if receiver.findBuffByBuffID(csconst.DancingBuffID):   #在有舞厅buff的基础上才加舞王buff
			Buff_Normal.receive( self, caster, receiver )

	def getNewBuffData( self, caster, receiver ):
		newBuffData = {}
		newBuffData[ "skill" ] = self
		newBuffData[ "persistent" ] = self.calculateTime( receiver )
		newBuffData[ "currTick" ] = 0
		newBuffData[ "caster" ] = self._casterID
		newBuffData[ "state" ] = 0
		newBuffData[ "index" ] = 0
		newBuffData[ "sourceType" ] = self.getSourceType()
		newBuffData[ "isNotIcon" ] = self.isNotIcon()
		return newBuffData

	def calculateTime( self, receiver ):
		"""
		"""
		return receiver.findBuffByBuffID(csconst.DancingBuffID)["persistent"]

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #每分钟获得经验
		DEBUG_MSG("Buff_22135 doReload add exp:%f to playerName:%s"%(exp, receiver.playerName))
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCEKING_BUFF )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #每分钟获得经验
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCEKING_BUFF )
		DEBUG_MSG("Buff_22135 doEnd add exp:%f to playerName:%s"%(exp, receiver.playerName))
		if csconst.DancingKingBuffID in [skillData["skill"].getBuffID() for skillData in receiver.attrBuffs]:  #在舞厅buff时间到的时候也要去掉舞王buff
			receiver.removeBuffByID( DancingKingBuffID,  [csdefine.BUFF_INTERRUPT_NONE] )   #buff时间到了，自动去掉舞王buff	
		Buff_Normal.doEnd( self, receiver, buffData )

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = Buff_22135()
		obj.__dict__.update( self.__dict__ )
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

#
# $Log: not supported by cvs2svn $
#
# 
#