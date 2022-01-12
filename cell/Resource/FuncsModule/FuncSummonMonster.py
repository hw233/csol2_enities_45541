# -*- coding: gb18030 -*-
from Function import Function
from bwdebug import *
import random
import math
import Math
import utils
import csstatus
import csdefine
import csconst
import BigWorld

from ObjectScripts.GameObjectFactory import g_objFactory

class FuncSummonMonster( Function ):
	"""
	�ٻ�Monster
	"""
	
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section.readString( "param1" )						# className
		self.position = ""
		self.direction = ""

		position = section.readString( "param2" )
		if position:
			pos = utils.vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param2 " % ( self.__class__.__name__, position ) )
			else:
				self.position = pos

		direction = section.readString( "param3" )
		if direction:
			dir = utils.vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param3 " % ( self.__class__.__name__, direction ) )
			else:
				self.direction = dir

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pos = Math.Vector3( player.position )
		direction = player.direction

		pos.x = player.position.x  +  random.random() * random.randint( -3, 3 )
		pos.z = player.position.z  +  random.random() * random.randint( -3, 3 )

		if self.position:
			pos = self.position
		if self.direction:
			direction = self.direction

		# �ٻ������ʱ��Ե��������ײ����������������
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y
		
		# ģ��ѡȡ�ο� ObjectScript/NPCObject.py ��createEntity �Ĵ���ʽ
		modelNumbers = g_objFactory.getObject( self.param1 ).getEntityProperty( "modelNumber" )
		modelScales = g_objFactory.getObject( self.param1 ).getEntityProperty( "modelScale" )
		if len( modelNumbers ):
			index = random.randint( 0, len(modelNumbers) - 1 )
			modelNumber = modelNumbers[ index ]
			if len( modelScales ) ==  1:
				modelScale = float( modelScales[ 0 ] )
			elif len( modelScales ) >= ( index + 1 ):
				modelScale = float( modelScales[ index ] )
			else:
				modelScale = 1.0
		else:
			modelNumber = ""
			modelScale = 1.0
		
		m_datas = { "spawnPos" : tuple( pos ), "modelScale" : modelScale, "modelNumber" : modelNumber, }
		
		entity = player.callEntity( self.param1, m_datas, pos, direction )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True