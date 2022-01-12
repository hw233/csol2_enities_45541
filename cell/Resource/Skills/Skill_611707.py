# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csdefine
import csstatus
from Function import newUID
from SpellBase import *
from Skill_Normal import Skill_Normal


class Skill_611707( Skill_Normal ):
	"""
	按比例增加主人和宠物的移动速度。
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self._param1 = 0
		self._param2 = 0
		self._param3 = 0
		self.tempValue = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._param1 = int( float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  * 100.0 )
		self._param2 = int( float( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 )  * 100.0 )
		self._param3 = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 )

	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if ownerEntity.__class__.__name__ == "Pet":
			if ownerEntity.character == self._param3:
				effectValue = self._param2
			else:
				effectValue = self._param1
			ownerEntity.move_speed_percent += effectValue
			ownerEntity.calcMoveSpeed()

			petOwner = ownerEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				entity.move_speed_percent += effectValue
				entity.calcMoveSpeed()
			else:
				tempSkill = self.createFromDict( { "param" : effectValue } )
				entity.attachSkillOnReal( tempSkill )
		else:
			ownerEntity.move_speed_percent += self.tempValue
			ownerEntity.calcMoveSpeed()

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if ownerEntity.__class__.__name__ == "Pet":
			if ownerEntity.character == self._param3:
				effectValue = self._param2
			else:
				effectValue = self._param1
			ownerEntity.move_speed_percent -= effectValue
			ownerEntity.calcMoveSpeed()

			petOwner = ownerEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				entity.move_speed_percent -= effectValue
				entity.calcMoveSpeed()
			else:
				tempSkill = self.createFromDict( { "param" : effectValue } )
				entity.detachSkillOnReal( tempSkill )
		else:
			ownerEntity.move_speed_percent -= self.tempValue
			ownerEntity.calcMoveSpeed()

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self.tempValue }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Skill_611707()
		obj.__dict__.update( self.__dict__ )
		obj.tempValue = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

