# -*- coding: gb18030 -*-
# --------------------------------------------------------------------
# 属性改变管理器
# 需要提醒发生改变的属性全部先放到管理器中，由管理器统一计算改变值并
# 发送属性改变消息。
#
# 设计思路：
# 在服务器端类似于“换装”这样的行为是先把装备脱下来后再穿上，会有两次
# 属性上的变化，但这种变化明显不是策划想要的。假设需要显示的属性如果在
# 很短的一个时间周期内（如0.1秒）有多次的改变， 我们可以为认这个改变很
# 可能是在同一个行为里产生的”。在此理论上我们可以在客户端产生一个类似
# 的属性值改变的管理器， 当set_xxx()方法收到相关的数值改变时扔到这个管
# 理器中，由管理器统一去计算并执行显示。
# written by gjx 2009-5-15
# --------------------------------------------------------------------

from ChatFacade import chatFacade
from AbstractTemplates import Singleton
import csstatus
import BigWorld

# 用列表定义属性显示优先顺序
showOrder = [ "HP_Max", "MP_Max", "PHYSICS_DMG", "PHYSICS_ARMOR", "MAGIC_DMG", "MAGIC_ARMOR" ]

# 属性变化消息ID
attrMaps = {
			"HP_Max_INC" : csstatus.ROLE_ATTR_HP_MAX_INC,				"HP_Max_DEC" : csstatus.ROLE_ATTR_HP_MAX_DEC,
			"MP_Max_INC" : csstatus.ROLE_ATTR_MP_MAX_INC,				"MP_Max_DEC" : csstatus.ROLE_ATTR_MP_MAX_DEC,
			"PHYSICS_DMG_INC" : csstatus.ROLE_ATTR_PHYSICS_DMG_INC,		"PHYSICS_DMG_DEC" : csstatus.ROLE_ATTR_PHYSICS_DMG_DEC,
			"PHYSICS_ARMOR_INC" : csstatus.ROLE_ATTR_PHYSICS_ARMOR_INC, "PHYSICS_ARMOR_DEC" : csstatus.ROLE_ATTR_PHYSICS_ARMOR_DEC,
			"MAGIC_DMG_INC" : csstatus.ROLE_ATTR_MAGIC_DMG_INC,			"MAGIC_DMG_DEC" : csstatus.ROLE_ATTR_MAGIC_DMG_DEC,
			"MAGIC_ARMOR_INC" : csstatus.ROLE_ATTR_MAGIC_ARMOR_INC,		"MAGIC_ARMOR_DEC" : csstatus.ROLE_ATTR_MAGIC_ARMOR_DEC,
			}


class AttrChangeMgr( Singleton ) :

	_tmp_time = 0.2								# 在此时间段接收到的相同属性改变的消息
												# 将视为同一次操作发送的消息。
	def __init__( self ) :
		self.__attrChangeValue = {}				# { attrName: [ oldValue, newValue ] }


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def deliverAttrMsg( self, attrName, value ) :
		"""
		接收属性改变消息
		@param		attrName	: 属性名称
		@param		value		: 属性改变值
		return		None
		"""
		if self.__attrChangeValue.has_key( attrName ) :
			self.__attrChangeValue[attrName][1] = value[1]
		else :
			if self.__attrChangeValue == {} :
				BigWorld.callback( self._tmp_time, self.__delayFire )
			self.__attrChangeValue[attrName] = value


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __delayFire( self ) :
		"""
		延时时间到时,按照定义的顺序发送属性改变消息
		"""
		for attrName in showOrder :
			value = self.__attrChangeValue.get( attrName, [0,0] )
			value = int( value[1] ) - int( value[0] )				# 该计算方法是为了与界面显示保持一致
			self.__fireMsg( attrName, value )
		self.__attrChangeValue = {}

	def __fireMsg( self, attrName, value ) :
		"""
		延时发送函数,只有属性值发生了改变才发送消息
		"""
		if value > 0 :
			attrName += "_INC"
		elif value < 0 :
			attrName += "_DEC"
			value = -value
		else :
			return
		statusID = attrMaps[attrName]
		chatFacade.rcvStatusMsg( statusID, value )


attrChangeMgr = AttrChangeMgr()