# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99029( Buff_Normal ):
	"""
	���ڱ��ڵİ���Ա����ڳ��Ĺ�����
	��buff���ڳ��ӵ��������
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
	
	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		Buff_Normal.receive( self, caster, receiver )
		receiver.setTemp( "protect_dart_id",caster.id )			# ����Ա��¼�ڳ���id
		receiver.setTemp( "TongDart_level",caster.queryTemp( "level",0 ) )
		receiver.setTemp( "TongDart_factionID",caster.queryTemp("factionID",0) )
	
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
		dartID = receiver.queryTemp( "protect_dart_id",0 )
		
		# ���ڳ��ĺϷ������ߣ��ȼ����ڳ����С��3����¼���������
		if dartID != 0:
			entities = receiver.entitiesInRangeExt( 35, "SlaveDart", receiver.position )
			for dartEntity in entities:
				if dartEntity.id == dartID:
					enemyList = []
					for entityID in dartEntity.enemyForTongDart:
						try:
							entity = BigWorld.entities[entityID]
						except KeyError:
							dartEntity.enemyForTongDart.remove( entityID )
							continue
						if entity.getLevel()- receiver.queryTemp( "TongDart_level",0 ) < csconst.DART_ROB_MIN_LEVEL:
							enemyList.append( entityID )
					receiver.setTemp( "attackDartRoleID", enemyList )
					return Buff_Normal.doLoop( self, receiver, buffData )
			
		if receiver.queryTemp( "attackDartRoleID" ):
			receiver.removeTemp( "attackDartRoleID" )
		if receiver.queryTemp( "protect_dart_id" ):
			receiver.removeTemp( "protect_dart_id" )
		if receiver.queryTemp( "TongDart_level" ):
			receiver.removeTemp( "TongDart_level" )
		if receiver.queryTemp( "TongDart_factionID" ):
			receiver.removeTemp( "TongDart_factionID" )
		return False
		
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
		if receiver.queryTemp( "attackDartRoleID" ):
			receiver.removeTemp( "attackDartRoleID" )
		if receiver.queryTemp( "protect_dart_id" ):
			receiver.removeTemp( "protect_dart_id" )
		if receiver.queryTemp( "TongDart_level" ):
			receiver.removeTemp( "TongDart_level" )
		if receiver.queryTemp( "TongDart_factionID" ):
			receiver.removeTemp( "TongDart_factionID" )