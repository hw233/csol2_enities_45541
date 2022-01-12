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
	�������������˺ͳ�����ƶ��ٶȡ�
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
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._param1 = int( float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  * 100.0 )
		self._param2 = int( float( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 )  * 100.0 )
		self._param3 = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 )

	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
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
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
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
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self.tempValue }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

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

