# -*- coding:gb18030 -*-

from Skill_Normal import Skill_Normal
from bwdebug import *
import csdefine

class Skill_Posture( Skill_Normal ):
	"""
	��̬�������ܣ���һ��������������Ӱ�����̬
	"""
	def __init__( self ):
		Skill_Normal.__init__( self )
		self._baseType = csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE	# ��init�лᱻ��д�����ǿ����ã����̳������Ķ����Ǵ�����
		self.effectPosture = csdefine.ENTITY_POSTURE_NONE
		
	def init( self, data ):
		"""
		"""
		Skill_Normal.init( self, data )
		self.effectPosture = int( data[ "param1" ] if len( data[ "param1" ] ) > 0 else 0 )
		
	def getEffectPosture( self ):
		"""
		�����Ӱ�����̬
		"""
		return self.effectPosture
		
	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE