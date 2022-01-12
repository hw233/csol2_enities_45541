# -*- coding: gb18030 -*-
#
# $Id: Buff_Vehicle.py,v 1.2 10:02 2010-12-21 jiangyi Exp $

"""
������Ч��
���buff����buff���������˵�����״̬
"""

import BigWorld
import csconst
import csstatus
import csdefine
import Const
from bwdebug import *
from Buff_Individual import Buff_Individual
from VehicleHelper import getDefaultVehicleData, getVehicleModelNum, canMount,  resetVehicleSkills
from Function import newUID

class Buff_Vehicle( Buff_Individual ):
	"""
	���״̬buff by mushuang
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Individual.__init__( self )
		self._vehicleDBID = 0 # ��ǰ����DBID��ע�������������ÿ�������ص�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Individual.init( self, dict )

	def _onDoBegin( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doBegin���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�		
		"""
		self._vehicleDBID = receiver.currVehicleData[ "id" ]

		# ���ݸĶ�֮��һ�������ݴ����������Ҹ��Ի������޷���ȷǨ�ơ�
		self._packIndividualData( "_vehicleDBID", self._vehicleDBID ) # ���ﴫ���keyֵΪ�����������뱣֤�˶��������������

	def _onDoEnd( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doEnd���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�
		"""
		self._vehicleDBID = 0
		# ���ݸĶ�֮��һ�������ݴ����������Ҹ��Ի������޷���ȷǨ�ơ�
		self._packIndividualData( "_vehicleDBID", self._vehicleDBID ) # ���ﴫ���keyֵΪ�����������뱣֤�˶��������������

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
		casterID = caster.id if caster else 0
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		if not receiver.currVehicleData:
			ERROR_MSG( "Can't find vehicle data on player!" )
			return

		if canMount( receiver, receiver.currVehicleData["id"], receiver.currVehicleData["type"] ) != csstatus.SKILL_GO_ON:
			receiver.currVehicleData = getDefaultVehicleData()  # �ÿյ�ǰ�������
			receiver.planesAllClients( "stopActions", () )					# ֹͣ��ǰ����
			return

		return Buff_Individual.receive( self, caster, receiver )

	def __conjureVehicle( self, player ):
		"""
		���л������ͨ��������׼��������ɣ�׼����ʼ��ʽ�������
		"""
		assert player.isReal(), "receiver must be a real entity!"
		assert player.currVehicleData, "Vehicle data needed!"

		vehicleData = player.currVehicleData
		modelNum = getVehicleModelNum( vehicleData )
		if modelNum == -1: return

		if player.vehicleModelNum != modelNum:
			player.vehicleModelNum = modelNum
		resetVehicleSkills( player, True )

	def __retractVehicle( self, player ):
		"""
		�ջ����
		���ջ����֮ǰ��һЩ����
		�˽ӿ�����buffȡ��ʱ�Ļص���
		һ����Ҳ����������øýӿ�
		����ֱ�������Ӧ��buff����
		"""
		assert player.isReal(),"player must be a real entity!"
		player.currVehicleData = getDefaultVehicleData()
		player.vehicleModelNum = 0

		
	def __addVehicleBuff( self, player ):
		"""
		�����buff�����ص��������
		"""
		assert player.isReal(),"player must be a real entity!"

		# �����buff���ص���ɫ����
		if player.currVehicleData:
			for buff in player.currVehicleData["attrBuffs"]:
				player.addBuff( buff )
				player.currentVehicleBuffIndexs.append( buff["index"] )
			player.currVehicleData["attrBuffs"] = []

	def __removeVehicleBuff( self, player ):
		"""
		��������ϳ������buff
		"""
		assert player.isReal(),"player must be a real entity!"

		# �����buff�ӽ�ɫ����ж��
		buffs = []
		for index in player.currentVehicleBuffIndexs:
			buff = player.getBuffByIndex( index )
			buffs.append(buff)
			player.removeBuffByIndex( index, [csdefine.BUFF_INTERRUPT_VEHICLE_OFF] )
		player.currentVehicleBuffIndexs = []
		if player.currVehicleData:
			player.currVehicleData["attrBuffs"] = buffs
		player.base.updateVehicleBuffs( player.currVehicleData["id"], buffs )

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
		self.__conjureVehicle( receiver )
		self.__addVehicleBuff( receiver )

		#������̻����_onDoBegin������Ҹ��Ի����ݴ������˸���������ϵ������������
		Buff_Individual.doBegin( self, receiver, buffData ) 

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

		self.__conjureVehicle( receiver )
		self.__addVehicleBuff( receiver )
		receiver.addC_VehicleFDTimmer()

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Individual.doEnd( self, receiver, buffData )

		self.__retractVehicle( receiver )
		self.__removeVehicleBuff( receiver )
