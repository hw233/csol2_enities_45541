# -*- coding: gb18030 -*-
#



from SpaceCopy import SpaceCopy
import BigWorld
import Const
import cschannel_msgs
import csdefine
import ECBExtend
import csconst
import Math
import random
import utils
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory

SPAWN_MONSTER 		= 1 											#刷怪
#MONSTER_MAPPING_DICT	= { "20732007":"20742021", "20147003":"20712011" }
CALCULATE_MONSTER	= 10											#计算水晶怪物数量
NOTICE_SEND_AI_COMMAND		= 13									#通知光柱发送AI指令
NOTICE_PLAYER				= 15									#刷怪通知玩家

CHECKPOINTS_1		= 1												#第一关
CHECKPOINTS_2		= 2												#第二关
CHECKPOINTS_3		= 3												#第三关

class SpaceCopyShuijing( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )


	def addSpawnPoint( self, spawnPointBaseMB, group, checkpoints ):
		"""
		"""
		key = str(checkpoints) + "and" + str(group)
		spawnPointBaseMBList = self.queryTemp( key, [] )
		spawnPointBaseMBList.append( spawnPointBaseMB )
		self.setTemp( key, spawnPointBaseMBList )
		if group == -1:					#-1 是刷BOSS
			return
		groupSet = self.queryTemp( 'groupCount', set() )
		groupSet.add( key )
		self.setTemp( 'groupCount', groupSet )



	def onMonsterDie( self, params ):
		"""
		define method
		"""
		self.getScript().onMonsterDie( self, params )
	
	def setLeaveTeamPlayerMB( self, baseMailbox ):
		"""
		define method
		"""
		self.setTemp( 'leavePMB', baseMailbox )
		

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		if len( self._players ) == 0:
			player = BigWorld.entities.get( baseMailbox.id, None )
			if player:
				#if player.query( "shuijing_checkPoint" ) != self.params[ "shuijing_checkPoint" ] + 1:
				#	BigWorld.globalData[ "ShuijingManager" ].leaveShuijing( player.shuijingKey )
				BigWorld.globalData[ "ShuijingManager" ].leaveShuijing( player.shuijingKey )
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )
			self.base.closeSpace( True )
	


	
	def spawnShuijingMonster( self ):
		"""
		define method
		开始刷新水晶
		"""
		self.addTimer( 10.0, 0.0, SPAWN_MONSTER)
		
	def calculateMonsterCount( self ):
		"""
		define method
		计算水晶副本每一关的怪物数量
		"""
		self.addTimer( 8.0, 0.0, CALCULATE_MONSTER)
		
	def noticeSendAICommend( self ):
		self.addTimer( 6.0, 0.0, NOTICE_SEND_AI_COMMAND )

	def noticePlayer( self ):
		self.addTimer( 5.0, 0.0, NOTICE_PLAYER )
		
	def spawnSpecialMonster( self ):
		self.getScript().spawnSpecialMonster( self )
		
	def startSpawnMonsterBySkill( self ):
		"""
		陷阱技能触发通知某一关卡开始刷怪
		"""
		if self.queryTemp( "shuijing_SpawnMonster", False ):
			return
		else:
			self.setTemp( "shuijing_SpawnMonster", True )
			self.calculateMonsterCount()
			self.spawnShuijingMonster()
		if self.queryTemp( "shuijing_checkPoint" ) == CHECKPOINTS_3:
			self.spawnSpecialMonster()
			self.noticeSendAICommend()
			self.noticePlayer()
	
	def startSpawnMonsterByTalk( self, playerID, classNameList, mountList, positionAndDirectionLists ):
		"""
		对话触发通知刷新第一关卡的怪物
		"""
		if not self.queryTemp( "shuijing_callEntity", 0 ):
			return
		if self.queryTemp( "shuijing_hasCallEntity", 0 ):
			return
		else:
			self.setTemp( "shuijing_hasCallEntity", 1 )
		player = BigWorld.entities.get( playerID, None )
		if not player:
			return
		monsterAmount = 0
		for subScript,amount in enumerate( mountList ):
			for i in xrange( int( amount ) ):
				className = classNameList[ subScript ]
				positionAndDirection = positionAndDirectionLists[ monsterAmount ].split("|")
				monsterAmount = monsterAmount + 1
				position = positionAndDirection[0]
				direction =positionAndDirection[1]
				if position:
					pos = utils.vector3TypeConvert( position )
					if pos is None:
						ERROR_MSG( "shuijing first checkpoint position Error:%s " %position )
						pos = Math.Vector3( player.position )
				if direction:
					dir = utils.vector3TypeConvert( direction )
					if dir is None:
						ERROR_MSG( "shuijing first checkpoint direction Error:%s " %direction )
						dir = tuple(player.direction)
						
				# 召唤怪物的时候对地面进行碰撞检测避免怪物陷入地下
				collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
				if collide != None:
					pos.y = collide[0].y
					
				# 模型选取参考 ObjectScript/NPCObject.py 中createEntity 的处理方式
				modelNumbers = g_objFactory.getObject( className ).getEntityProperty( "modelNumber" )
				modelScales = g_objFactory.getObject( className ).getEntityProperty( "modelScale" )
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
				
				entity = player.callEntity( className, m_datas, pos, dir )

		self.spawnShuijingMonster()
		self.removeTemp( "shuijing_callEntity" )
		if self.queryTemp( "shuijing_hasCallEntity", 0 ):
			self.removeTemp( "shuijing_hasCallEntity" )



				
