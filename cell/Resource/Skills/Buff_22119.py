# -*- coding: gb18030 -*-
#
# $Id: Buff_22001.py,v 1.2 2008-05-19 08:01:12 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Normal import Buff_Normal
import time
import math

class Buff_22119( Buff_Normal ):
	"""
	example: 多倍经验奖励 杀怪时人物与宠物所获得的经验与潜能提高一倍
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
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self.isCharge = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

	def getPercent( self ):
		"""
		获取倍率
		"""
		return self._p1

	def updatePercent( self, val ):
		self._p1 = val

	def setRoleExpRecord( self, role ):
		"""
		设置角色经验记录
		"""
		DEBUG_MSG( "query rewardExpHour:%i" % role.queryTemp( "rewardExpHour", 0 ) )

		hour = role.popTemp( "rewardExpHour", 0 )
		if hour > 0 and self.isCharge == 0:
			role.takeExpRecord[ "week" ] = time.localtime()[6]
			role.takeExpRecord[ "remainTime" ] = role.takeExpRecord[ "remainTime" ] - hour
			role.takeExpRecord[ "lastTime" ] = time.time()

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者，None表示不存在
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )

		#判断是否有相同的buff
		if len( buffs ) > 0:
			# 已存在相同类型的buff
			self.doAppend( receiver, buffs[0] )
		else:
			sexp = str( self.getPercent() ) + "%"
			receiver.statusMessage( csstatus.TAKE_EXP_SUCCESS1, receiver.queryTemp( "rewardExpHour", 0 ), sexp )
			self.setRoleExpRecord( receiver )
			receiver.addBuff( self.getNewBuffData( caster, receiver ) )

	def doAppend( self, receiver, buffIndex ):
		"""
		Virtual method.
		对一个或多个已经存在的同类型BUFF进行追加操作
		具体对BUFF数据追加什么由继承者决定
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffs: 玩家身上同类型的BUFF所在attrbuffs的位置,BUFFDAT 可以通过 receiver.getBuff( buffIndex ) 获取
		"""
		buffdata = receiver.getBuff( buffIndex )
		sk = buffdata["skill"]
		sexp = str( self.getPercent() ) + "%"
		sexp1 = str( sk.getPercent() ) + "%"
		isappend = 0

		if sk.getPercent() == self.getPercent():
			# 免费道具与收费道具只能有一个
			if sk.isCharge != self.isCharge:
				if self.isCharge:
					receiver.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp1 )
				else:
					receiver.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST1, sexp1 )
				return
			buffdata["persistent"] += self._persistent
		elif sk.getPercent() < self.getPercent():
			# 如果当前要添加的高倍率BUFF是免费的， 身上的底倍率是收费道具， 则不允许覆盖
			if sk.isCharge and not self.isCharge:
				receiver.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE1, sexp1 )
				return

			#高倍率时间 + 低倍率时间*低倍率倍数/高倍率倍数
			sk_persistent = int( ( buffdata["persistent"] ) - time.time() )
			val = self._persistent + sk_persistent * sk.getPercent() / self.getPercent()
			isappend = val
			buffdata["persistent"] = ( val + time.time() )
			val = self.getPercent() / 100.0
			receiver.multExp = val
			receiver.potential_percent = val
			buffdata["skill"].isCharge = self.isCharge
			buffdata["skill"].updatePercent( self.getPercent() )
		else:
			if self.isCharge:
				receiver.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp1 )
			else:
				receiver.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST1, sexp1 )
			return

		if isappend == 0:
			receiver.statusMessage( csstatus.TAKE_EXP_SUCCESS1, receiver.queryTemp( "rewardExpHour", 0 ), sexp )
		else:
			receiver.statusMessage( csstatus.TAKE_EXP_SUCCESS3, math.ceil( isappend / 60.0 ), sexp )
		self.setRoleExpRecord( receiver )
		receiver.client.onUpdateBuffData( buffIndex, buffdata )

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
		buffData[ "skill" ] = self.createFromDict( { "param": { "p1" : self.getPercent(), "isCharge" : self.isCharge } } )
		val = self.getPercent() / 100.0
		receiver.vehicle_multExp += val

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
		val = buffData[ "skill" ].getPercent() / 100.0
		receiver.vehicle_multExp += val

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		val = self.getPercent() / 100.0
		receiver.vehicle_multExp -= val
		Buff_Normal.doEnd( self, receiver, buffData )

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param": { "p1" : self.getPercent(), "isCharge" : self.isCharge } }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_22119()
		obj.__dict__.update( self.__dict__ )
		obj.updatePercent( data[ "param" ][ "p1" ] )
		obj.isCharge = data[ "param" ][ "isCharge" ]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj