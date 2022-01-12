# -*- coding: gb18030 -*-
#
# $Id: Buff_23003.py,v 1.3 2008-02-28 08:25:56 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Shield import Buff_Shield

class Buff_23003( Buff_Shield ):
	"""
	example:将受到的所有伤害，按x%的比率，扣除法力值，最多转化y点伤害，转化完后，护盾消失
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Shield.__init__( self )
		self._p1 = 0 # 按x%的比率
		self._p2 = 0 # 最多转化y点伤害
		self._param = {}
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Shield.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0	
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 	
		
		
	def doShield( self, receiver, damageType, damage ):
		"""
		virtual method.
		执行护盾自身功能  如：法术形转化伤害为MP 
		注意: 此接口不可手动删除该护盾
		@param receiver: 受术者
		@param damageType: 伤害类型
		@param damage : 本次伤害值
		@rtype: 返回被消减后的伤害值
		"""
		if self.isDisabled( receiver ):
			return damage
		
		finiDamage = damage # 最终伤害
		mpNeeded = damage * self._p1 # 抵挡此次伤害所需要的魔法
		
		if receiver.MP < mpNeeded:
			self._param["disabled"] = True
			return finiDamage
			
		# 这里必须判断real 否则可能会被设置2次， 具体看shieldConsume机制
		if receiver.isReal(): # 扣除消耗的操作在receiver是real entity时才执行
			# CSOL-10126: 比如5000点伤害打在能吸收2100伤害的盾上，吸收掉2100，造成2900伤害
			if self._param["p2"] < damage:
				finiDamage = damage - self._param["p2"]
				self._param["disabled"] = True
				mpNeeded = self._param["p2"] * self._p1 # 重新计算抵挡此次攻击需要的魔法
				self._param["p2"] = 0
			else:
				self._param["p2"] -= damage
				finiDamage = 0
			
			receiver.setMP( int( receiver.MP - mpNeeded ) )
			receiver.statusMessage( csstatus.SKILL_DAMAGE_SUCK_TO, receiver.getName() + self.getName(), damage - finiDamage )
			return finiDamage
		else: # 对于ghost，不必扣除任何消耗，返回一个正确的值就可以了，消耗会在随后对real entity的调用中实现，具体看shieldConsume机制（这个机制真纠结。。。）
			INFO_MSG( "Operating on ghost entity!" )
			if self._param["p2"] < damage:
				return self._param["p2"]
			else:
				return 0
			
		
		
	def isDisabled( self, receiver ):
		"""
		virtual method.
		护盾是否失效
		@param receiver: 受术者
		"""
		return self._param.has_key( "disabled" )#由于护盾是被动态创建出来的 因此可以判断自身数据
		
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
		self.triggerInterruptCode( receiver, buffData )
		#由于createFromDict复制了父类的属性而p1是不会被 个体实例所改变的 因此不需要打包p1
		buffData[ "skill" ] = self.createFromDict( { "param":{ "p2":self._p2 } } )
		receiver.appendShield( buffData[ "skill" ] )
		
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
		Buff_Shield.doReload( self, receiver, buffData )
		buffData[ "skill" ] = self.createFromDict( { "param":{ "p2":self._p2 } } )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Shield.doEnd( self, receiver, buffData )
		receiver.removeShield( buffData[ "skill" ].getUID() )

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
		obj = Buff_23003()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/12/20 02:50:31  kebiao
# no message
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#