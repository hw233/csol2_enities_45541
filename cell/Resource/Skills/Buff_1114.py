# -*- coding:gb18030 -*-

from Buff_Shield import Buff_Shield
from Function import newUID
import time

class Buff_1114( Buff_Shield ):
	"""
	��������֤entity��Ѫ����ĳһ���ٷֱȣ����ڱ�֤npc��Ѫ��ʹnpc������ɱ����ִ��һЩ��Ҫ��ai
	"""
	def __init__( self ):
		Buff_Shield.__init__( self )
		self.holdPercent = 0.0	# ����Ҫholdס��Ѫ���ٷֱ�
		
	def init( self, data ):
		Buff_Shield.init( self, data )
		self.holdPercent = int( data["Param1"] ) / 100.0 if len( data["Param1"] ) else 0
		
	def doShield( self, receiver, damageType, damage ):
		"""
		virtual method.
		ִ�л���������  �磺������ת���˺�ΪMP 
		ע��: �˽ӿڲ����ֶ�ɾ���û���
		@param receiver: ������
		@param damageType: �˺�����
		@param damage : �����˺�ֵ
		@rtype: ���ر���������˺�ֵ
		"""
		damageInfo = receiver.queryTemp( "shieldDamage_1114", [ 0, 0 ] )		# �˺�����ʱ������ԣ��Ա��ж��˺��ڴ˴ι������Ƿ���Ч
		now = int( time.time() )
		if damageInfo[1] != now:
			damageInfo[0] = 0
			damageInfo[1] = now
		existDamage = damageInfo[0]
		maxDamage = max( 0, receiver.HP - receiver.HP_Max * self.holdPercent )	# ��Ѫ������ָ���ٷֱ�ʱ���������˺�
		finalDamage = maxDamage - existDamage
		if damage > finalDamage:
			damage = finalDamage
		damageInfo[0] = damage + existDamage
		receiver.setTemp( "shieldDamage_1114", damageInfo )	# һ�ι����п����ж����˺����Ͷ��һ�ֱ���㣬��¼�˺��������˺�����ʱ��
		return damage
		
	def isDisabled( self, receiver ):
		"""
		virtual method.
		�����Ƿ�ʧЧ
		@param receiver: ������
		"""
		return False
		
	def doBegin( self, receiver, buffData ):
		Buff_Shield.doBegin( self, receiver, buffData )
		buffData[ "skill" ] = self.createFromDict( { "uid":newUID() } )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doReload( self, receiver, buffData ):
		Buff_Shield.doReload( self, receiver, buffData )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		Buff_Shield.doEnd( self, receiver, buffData )
		receiver.removeShield( buffData[ "skill" ].getUID() )
		receiver.removeTemp( "shieldDamage_1114" )
		
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		obj = Buff_1114()
		obj.__dict__.update( self.__dict__ )
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj