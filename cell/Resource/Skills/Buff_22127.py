# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csstatus
import csdefine
import random
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

										 
class Buff_22127( Buff_Normal ):
	"""
	example:变身

	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.currModelNumber = ""
		self.currModelScale = 1.0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = dict[ "Param1" ]
		self._p2 = float( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 1 )

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
		
		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
		self = buffData[ "skill" ]
		
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.begin_body_changing( self._p1, self._p2 )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.modelScale = self._p2

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
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.begin_body_changing( self._p1, self._p2 )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.modelScale = self._p2

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
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.end_body_changing( receiver.id, "" )
		else:
			receiver.modelNumber = self.currModelNumber
			receiver.modelScale = self.currModelScale

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : { "currModelNumber" : self.currModelNumber, "currModelScale" : self.currModelScale } }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = Buff_22127()
		obj.__dict__.update( self.__dict__ )
		self.currModelNumber = data["param"]["currModelNumber"]
		self.currModelScale = data["param"]["currModelScale"]
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