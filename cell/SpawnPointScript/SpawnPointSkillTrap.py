# -*- coding: gb18030 -*-
import random

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPoint import SpawnPoint

class SpawnPointSkillTrap( SpawnPoint ):
	"""
	����ר��ˢ�µ�
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		pass

	def onBaseGotCell( self, selfEntity ):
		"""
		��base�ص�������֪ͨspawn point��base�Ѿ������cell��֪ͨ
		"""
		# ��base�����onGetCell()�ص����ٿ�ʼ������������������ܽ���������ʱ�����㲻��ȷ������
		# ��ǰ������ܿ����ǵײ��bug
		pass	# ������������㣬����Ҫ����������Ĺ���
	
	def converSkillID( self, strSkill ):
		if strSkill:
			skills = [ int( sid ) for sid in strSkill.split( ";" ) ]
			return random.choice( skills )
			
		return 0
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = SpawnPoint.getEntityArgs( self, selfEntity, params )
		args[ "enterSpell" ] = self.converSkillID( args[ "enterSpell" ] )
		args[ "leaveSpell" ] = self.converSkillID( args[ "leaveSpell" ] )
		args[ "destroySpell" ] = self.converSkillID( args[ "destroySpell" ] )
		return args

	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		��ʼ������
		"""
		args = self.getEntityArgs( selfEntity, params )
		selfEntity.createEntityNear( "SkillTrap", selfEntity.position, selfEntity.direction, args )