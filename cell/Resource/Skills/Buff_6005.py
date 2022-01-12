# -*- coding: gb18030 -*-
#
# $Id: Buff_6005.py,v 1.1 2008-09-04 06:44:02 yangkai Exp $

"""
������Ч��
"""

from Buff_Vehicle import Buff_Vehicle
import Const
import csdefine
import csconst

class Buff_6005( Buff_Vehicle ):
	"""
	���ר��buff
	��buff��������ʹ�ã��������ط�ʹ�û�����������Buff_Vehicle�е�ʵ��
	example:�ƶ��ٶ����%
	
	���������BUFF���ݽṹ�������ݽṹ�������ദ���������ദ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Vehicle.__init__( self )
		self.speedIncPercent = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Vehicle.init( self, dict )
		self.speedIncPercent = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0

	def springOnUseMaligSkill( self, caster, skill ):
		"""
		ʹ�ö��Լ��ܱ�����
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

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
		Buff_Vehicle.doBegin( self, receiver, buffData )
		# ʹ�ö��Լ��ܺ󴥷����˺������
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# �߻�Ҫ��ֻ����û����������²Ŵ���ˮ�����Ч��
		if hasattr( receiver, "onWaterArea" ):
			if receiver.onWaterArea:
				if receiver.isAccelerate:
					receiver.move_speed_value -= Const.WATER_SPEED_ACCELERATE
					receiver.isAccelerate = False
		receiver.move_speed_percent += self.speedIncPercent * csconst.FLOAT_ZIP_PERCENT
		receiver.calcMoveSpeed()
	
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
		Buff_Vehicle.doReload( self, receiver, buffData )
		# ʹ�ö��Լ��ܺ󴥷����˺������
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# �߻�Ҫ��ֻ����û����������²Ŵ���ˮ�����Ч��
		if hasattr( receiver, "onWaterArea" ):
			if receiver.onWaterArea:
				if receiver.isAccelerate:
					receiver.move_speed_value -= Const.WATER_SPEED_ACCELERATE
					receiver.isAccelerate = False
		receiver.move_speed_percent += self.speedIncPercent * csconst.FLOAT_ZIP_PERCENT

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Vehicle.doEnd( self, receiver, buffData )
		# ʹ�ö��Լ��ܺ󴥷����˺������
		receiver.removeOnUseMaligSkill( buffData[ "skill" ].getUID() )
		# ��ˮ�������ˮ�����Ч�����¼���
		if hasattr( receiver, "onWaterArea" ):
			if receiver.onWaterArea:
				if not receiver.isAccelerate:
					receiver.move_speed_value += Const.WATER_SPEED_ACCELERATE
					receiver.isAccelerate = True
		receiver.move_speed_percent -= self.speedIncPercent * csconst.FLOAT_ZIP_PERCENT
		receiver.calcMoveSpeed()
		
# $Log: not supported by cvs2svn $