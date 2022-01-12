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
from VehicleHelper import getCurrVehicleID


class Buff_22136( Buff_Normal ):
	"""
	舞厅中经验Buff
	(Lv^1.5 * 3.5 + 9 ) * self.param1  #每分钟获得经验；
	持续480分钟
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
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1   #每分钟获得经验
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCE_BUFF )
		DEBUG_MSG("Buff_22136 doLoop add exp:%f to playerName:%s"%(exp, receiver.playerName))
		return Buff_Normal.doLoop( self, receiver, buffData )

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
		if self._persistent <= 0: return 0
		print "receiver.DanceBuffPersistentTime =",receiver.DanceBuffPersistentTime,"persistent time = ",8 * 3600 -  receiver.DanceBuffPersistentTime
		print "test =",( (time.gmtime(receiver.LastAddDanceBuffTime)[0] == time.localtime()[0]) and (time.gmtime(receiver.LastAddDanceBuffTime)[-2] == time.localtime()[-2]) )
		if ( (time.gmtime(receiver.LastAddDanceBuffTime)[0] == time.localtime()[0]) and (time.gmtime(receiver.LastAddDanceBuffTime)[-2] == time.localtime()[-2]) ):  #同一天
			if receiver.DanceBuffPersistentTime < 8 * 3600 :   #当天舞厅buff累计时间不足8个时
				return int(time.time() + 8 * 3600 -  receiver.DanceBuffPersistentTime)   #在添加buff时计算持续时间    
			else :
				return 0  #当天的buff时间已经达到了,再次加的时候没有作用
		return time.time() + self._persistent

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
		#可以加舞厅buff的情况
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.LastAddDanceBuffTime = time.time() #记录加舞厅buff的时间
		DEBUG_MSG("Buff_22136 doBegin")


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
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCE_BUFF )	
		DEBUG_MSG("Buff_22136 doReload add exp:%f to playerName:%s"%(exp, receiver.playerName))
		
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
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCE_BUFF )
		DEBUG_MSG("Buff_22136 doEnd add exp:%f to playerName:%s"%(exp, receiver.playerName))
		if receiver.findBuffByBuffID(csconst.DancingKingBuffID):  #在舞厅buff时间到的时候也要去掉舞王buff
			receiver.removeBuffByID( csconst.DancingKingBuffID,  [csdefine.BUFF_INTERRUPT_NONE] )   #buff时间到了，自动去掉舞王buff		
		Buff_Normal.doEnd( self, receiver, buffData )
		

	def createFromDict( self, data ):
		"""
		virtual method.	
		@type data: dict
		"""
		obj = Buff_22136()
		obj.__dict__.update( self.__dict__ )
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

