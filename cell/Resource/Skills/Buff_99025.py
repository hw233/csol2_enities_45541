# -*- coding:gb18030 -*-

import BigWorld
import csdefine
from bwdebug import *
import random
from Buff_Normal import Buff_Normal
from Function import newUID


class Buff_99025( Buff_Normal ):
	"""
	蒙面巾buff，仅适用于角色，更换头部模型，在其他客户端屏蔽玩家的名字、帮会、称号的信息。
	"""
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.hairModelDict = eval( data["Param1"] )
		self.oldHairModelNum = 0

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.addFlag( csdefine.ROLE_FLAG_HIDE_INFO )
		self.oldHairModelNum = receiver.hairNumber
		try:
			hairModelNum = random.choice( self.hairModelDict[( receiver.getGender(),receiver.getClass() )] )
		except:
			EXCEHOOK_MSG( "player oldHairModelNum:%i" % self.oldHairModelNum )
			hairModelNum = 0
		receiver.hairNumber = hairModelNum
		
	def doReload( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.addFlag( csdefine.ROLE_FLAG_HIDE_INFO )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeFlag( csdefine.ROLE_FLAG_HIDE_INFO )
		receiver.hairNumber = self.oldHairModelNum
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self.oldHairModelNum }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_99025()
		obj.__dict__.update( self.__dict__ )
		obj.oldHairModelNum = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
		