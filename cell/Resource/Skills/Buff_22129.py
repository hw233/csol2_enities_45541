# -*- coding: gb18030 -*-
#
# $Id: Buff_2008.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

"""
��buff����֮�󽫻����Ҵ��͵�ָ��λ�ö��ҽ�����ͬһ�ռ��� by mushuang
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import get3DVectorFromStr
from math import radians

class Buff_22129( Buff_Normal ):
	"""
	example:
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		
		self._position = ( 0.0, 0.0, 0.0 ) # �����Ҫ�����͵���λ�ã�ע�����������ÿ��buff�����ģ���Ҫ��¡����
		self._yaw = 0.0 # ����֮����ҵķ���
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		# Param1 ���������Ҫ�����͵���λ�ã�x,y,z����������ʹ�ÿո�ֿ����磺1.0 2.0 3.0
		# Param2 ��������Ҵ���֮��Χ��y�����ת�������ر��е�yawֵ
		
		Buff_Normal.init( self, dict )
		self._position = get3DVectorFromStr( dict[ "Param1" ] )
		
		self._yaw = radians( float( dict[ "Param2" ] ) ) # ���߻��ر��п������ǽǶȣ��������Ҫת���ɻ��Ȳ�����teleport������ʹ��
	
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		# ��¼��buff�ӵ��������ʱ������ڵ�sapceID, ��Ҫ��������֤�ڴ���ʱ�Ƿ���Ȼ����ͬһ�ռ䣬
		# ��ֹ��������߳��ռ�֮���ٱ����Ͷ������������
		receiver.setTemp( "Buff_22129_Space_ID", receiver.spaceID )
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		# ��¼������ڿռ�
		receiver.setTemp( "Buff_22129_Space_ID", receiver.spaceID )
		
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
		spaceID = receiver.popTemp( "Buff_22129_Space_ID", -1 )
		
		if spaceID == receiver.spaceID:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				# ����ʱ��Ӧ���е����˺�,���Խ�����ʼ����ĸ߶ȡ�����ΪҪ���͵���λ�õĸ߶�
				receiver.fallDownHeight = self._position[ 1 ]
				# �������������ң���ô����֪ͨ�ͻ���ͬ��yaw��Ϣ������yaw�������������ã�ԭ���unifyYaw��ע�͡�
				receiver.client.unifyYaw() 
			receiver.teleport( None, self._position, ( 0.0, 0.0, self._yaw ) )
		else:
			ERROR_MSG( "Incorrect use of this buff, check the instructions at the beginning of the module please!" )
			
