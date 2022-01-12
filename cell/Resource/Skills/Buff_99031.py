# -*- coding: gb18030 -*-

import math
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_99031( Buff_Normal ):
	"""
	�������������Ӣ����������ʹ�ã�
	��ʽ X=A*(Lv+C)+B
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Buff_Normal.__init__( self )
		self._pA1 = 0.0
		self._pB1 = 0.0
		self._pC1 = 0.0
		self._level = 0	# �����ȼ�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		p1 = dict["Param1"].split( ";" )
		if len( p1 ) >= 3:
			self._pA1 = float( p1[0] )
			self._pB1 = float( p1[1] )
			self._pC1 = float( p1[2] )

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
		self._level = receiver.getSpaceCopyLevel()
		armor_value = int( math.ceil( self._pA1 * ( self._level + self._pC1 ) + self._pB1 ) )
		receiver.armor_value += armor_value
		receiver.calcArmor()

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
		self._level = receiver.getSpaceCopyLevel()
		armor_value = int( math.ceil( self._pA1 * ( self._level + self._pC1 ) + self._pB1 ) )
		receiver.armor_value += armor_value

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
		armor_value = int( math.ceil( self._pA1 * ( self._level + self._pC1 ) + self._pB1 ) )
		receiver.armor_value -= armor_value
		receiver.calcArmor()

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self._level }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		""" 
		obj = Buff_99031()
		obj.__dict__.update( self.__dict__ )
		obj._level = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
