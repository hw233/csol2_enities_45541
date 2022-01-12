# -*- coding: gb18030 -*-

"""
������
"""
from Buff_Normal import Buff_Normal
import Math
import csdefine

class Buff_208003( Buff_Normal ):
	"""
	example:
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.height = float( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		if not receiver.queryTemp("upHeight",False) and receiver.getEntityType() == csdefine.ENTITY_TYPE_MONSTER:
			receiver.setTemp("upHeight",True)
			receiver.openVolatileInfo()
			receiver.position += Math.Vector3( 0, self.height, 0 )
		return Buff_Normal.doLoop( self, receiver, buffData )
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "upHeight" )
 