# -*- coding:gb18030 -*-

from Skill_Normal import Skill_Normal
from bwdebug import *
import csdefine

class Skill_Posture( Skill_Normal ):
	"""
	姿态被动技能，第一个参数必须填受影响的姿态
	"""
	def __init__( self ):
		Skill_Normal.__init__( self )
		self._baseType = csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE	# 在init中会被改写，这是可配置，但继承与此类的都会是此类型
		self.effectPosture = csdefine.ENTITY_POSTURE_NONE
		
	def init( self, data ):
		"""
		"""
		Skill_Normal.init( self, data )
		self.effectPosture = int( data[ "param1" ] if len( data[ "param1" ] ) > 0 else 0 )
		
	def getEffectPosture( self ):
		"""
		获得受影响的姿态
		"""
		return self.effectPosture
		
	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE