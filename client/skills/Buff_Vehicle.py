# -*- coding: gb18030 -*-

from bwdebug import *
from Buff_Individual import Buff_Individual
import event.EventCenter as ECenter
import BigWorld
import csstatus
from Role import PlayerRole
from ModelHelper import isInNarrowSpace
from gbref import rds

class Buff_Vehicle( Buff_Individual ):
	"""
	���buff���ͻ��˽ӿ� by mushuang
	"""
	def __init__( self ):
		Buff_Individual.__init__( self )
		self._vehicleDBID = 0

	def __narrowSpaceHandling( self, player ):
		"""
		������խ�ռ��ٻ����ʱ����ش����߼�
		"""
		if not isInNarrowSpace( player ):
			return

		DEBUG_MSG( "Summon vehicle in narrow space!" )

		# ����խ�ռ��ٻ����᲻�ɹ�������ʾ���
		buffData = player.findBuffByID( self.getID() )
		if buffData:
			player.cell.requestRemoveBuff( buffData[ "index" ] )
			player.statusMessage( csstatus.SPACE_TOO_NARROW_FOR_VEHICLE )


	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff_Individual.cast( self, caster, target )
		if target != BigWorld.player():
			return
		target.vehicleDBID = self._vehicleDBID # �趨��ǰ���DBID
		DEBUG_MSG( "Setting Role.vehicleDBID to %s "%BigWorld.player().vehicleDBID )

		# ֪ͨ����
		ECenter.fireEvent( "EVT_ON_PLAYER_UP_VEHICLE" )

		self.__narrowSpaceHandling( target )

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""


		self._vehicleDBID = 0
		target.vehicleDBID = 0
		DEBUG_MSG( "Clear Role.vehicleDBID to 0 " )

		if target != BigWorld.player():
			return
		# ���Բ���һ������bug����ĳЩʱ������target��Role�����������ԭ��δ֪��
		if isDebuged:
			assert isinstance( target, PlayerRole )

		target.updateMoveMode()		# ����ʱ���������ý�ɫ�ƶ��ٶȣ�hyw--2008.12.30��

		# ֹͣ�Զ�Ѱ·
#		target.endAutoRun( False )

		# ֪ͨ����
		ECenter.fireEvent( "EVT_ON_PLAYER_DOWN_VEHICLE" )
		target.resetCamera()
		Buff_Individual.end( self, caster, target )
