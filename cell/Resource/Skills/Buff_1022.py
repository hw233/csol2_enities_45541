# -*- coding:gb18030 -*-

from bwdebug import *
from Buff_Individual import Buff_Individual
from VehicleHelper import getDefaultVehicleData_Attr

class Buff_1022( Buff_Individual ):
	"""
	������Լӳ�buff
	"""
	def __init__( self ):
		"""
		"""
		Buff_Individual.__init__( self )
		self._vehicleData = {} # ��ǰ����DBID��ע�������������ÿ�������ص�

	def init( self, dict ):
		"""
		"""
		Buff_Individual.init( self, dict )
		
	def _onDoBegin( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doBegin���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�		
		"""
		self._vehicleData = receiver.currAttrVehicleData
		# ���ݸĶ�֮��һ�������ݴ����������Ҹ��Ի������޷���ȷǨ�ơ�
		self._packIndividualData( "_vehicleData", self._vehicleData ) # ���ﴫ���keyֵΪ�����������뱣֤�˶��������������

	def _onDoEnd( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doEnd���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�
		"""
		self._vehicleData = {}
		# ���ݸĶ�֮��һ�������ݴ����������Ҹ��Ի������޷���ȷǨ�ơ�
		self._packIndividualData( "_vehicleData", self._vehicleData ) # ���ﴫ���keyֵΪ�����������뱣֤�˶��������������

	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Individual.doBegin( self, receiver, buffData )
		vehicleData= receiver.currAttrVehicleData
		strength   = vehicleData["strength"]
		intellect  = vehicleData["intellect"]
		dexterity  = vehicleData["dexterity"]
		corporeity = vehicleData["corporeity"]

		receiver.strength_value += strength
		receiver.intellect_value += intellect
		receiver.dexterity_value +=  dexterity
		receiver.corporeity_value +=  corporeity
		receiver.calcDynamicProperties()

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
		Buff_Individual.doReload( self, receiver, buffData )
		vehicleData= receiver.currAttrVehicleData

		#���½��м���
		receiver.addA_VehicleFDTimmer()

		strength   = vehicleData["strength"]
		intellect  = vehicleData["intellect"]
		dexterity  = vehicleData["dexterity"]
		corporeity = vehicleData["corporeity"]

		receiver.strength_value += strength
		receiver.intellect_value += intellect
		receiver.dexterity_value +=  dexterity
		receiver.corporeity_value +=  corporeity

	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Individual.doEnd( self, receiver, buffData )
		vehicleData= receiver.currAttrVehicleData
		strength   = vehicleData["strength"]
		intellect  = vehicleData["intellect"]
		dexterity  = vehicleData["dexterity"]
		corporeity = vehicleData["corporeity"]

		receiver.strength_value -= strength
		receiver.intellect_value -= intellect
		receiver.dexterity_value -=  dexterity
		receiver.corporeity_value -=  corporeity
		receiver.calcDynamicProperties()
		receiver.currAttrVehicleData  = getDefaultVehicleData_Attr()
