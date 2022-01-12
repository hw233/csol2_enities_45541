# -*- coding: gb18030 -*-
#
# $Id: Buff_1001.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import random
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_127006( Buff_Normal ):
	"""
	example: 随机降低敌人某种元素抗性
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._type = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )

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
		self._type = random.randint(0, 3)
		
		if self._type == 0:
			receiver.elem_huo_derate_ratio_base -= self._p1
			receiver.calcElemHuoDerateRatio()				# 计算火元素抗性
		elif self._type == 1:
			receiver.elem_xuan_derate_ratio_base -= self._p1
			receiver.calcElemXuanDerateRatio()				# 计算玄元素抗性
		elif self._type == 2:
			receiver.elem_lei_derate_ratio_base -= self._p1
			receiver.calcElemLeiDerateRatio()				# 计算雷元素抗性
		elif self._type == 3:
			receiver.elem_bing_derate_ratio_base -= self._p1
			receiver.calcElemBingDerateRatio()				# 计算冰元素抗性

		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
		
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
		self.doBegin( receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if self._type == 0:
			receiver.elem_huo_derate_ratio_base += self._p1
			receiver.calcElemHuoDerateRatio()				# 计算火元素抗性
		elif self._type == 1:
			receiver.elem_xuan_derate_ratio_base += self._p1
			receiver.calcElemXuanDerateRatio()				# 计算玄元素抗性
		elif self._type == 2:
			receiver.elem_lei_derate_ratio_base += self._p1
			receiver.calcElemLeiDerateRatio()				# 计算雷元素抗性
		elif self._type == 3:
			receiver.elem_bing_derate_ratio_base += self._p1
			receiver.calcElemBingDerateRatio()				# 计算冰元素抗性

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self._type }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = Buff_127006()
		obj.__dict__.update( self.__dict__ )
		obj._type = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
		
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#