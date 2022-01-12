# -*- coding: gb18030 -*-
#
import csdefine
from Buff_Normal import Buff_Normal

 
class Buff_22130( Buff_Normal ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._p2 = 0
		self._p3 = 0 #1��ʾ�Ṧϵͳbuff
		#self.modelNum = None	#��¼�������add by wuxo 2011-11-11

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100
		self._loopSpeed = 1
		if dict[ "Param2" ] != "":
			self._p2 = int( dict[ "Param2" ] )
		if dict[ "Param3" ] != "":
			self._p3 = int( dict[ "Param3" ] )

	def springOnUseMaligSkill( self, caster, skill ):
		"""
		ʹ�ö��Լ��ܱ�����
		"""
		if not self._p3: return
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def springOnDamage( self, caster, skill ):
		"""
		�����˺���
		"""
		if not self._p3: return
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
		Buff_Normal.doBegin( self, receiver, buffData )
		isAccelerate = False
		receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate ) 
		if hasattr(receiver,"onWaterArea") :
			if receiver.onWaterArea :
				if not isAccelerate:
					receiver.move_speed_percent += self._p1
					receiver.calcMoveSpeed()
					isAccelerate = True
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
					
				if receiver.energy < self._p2: #��Ծ����ֵ����
					buffID = self.getBuffID()
					if self._p3: #ֻ�����Ṧϵͳ��buff��ɾ��
						receiver.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					receiver.calEnergy( - self._p2 )
			else:
				if isAccelerate:
					receiver.move_speed_percent -= self._p1
					receiver.calcMoveSpeed()
					isAccelerate = False
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
					
		receiver.withdrawEidolonBeforeBuff( receiver.id )		# �����С������Ҫ�ջ�

	def doLoop( self, receiver, buffData ):
		"""
		@add by wuxo 2011-11-11
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		isAccelerate = receiver.queryTemp( "BUFF_ISACCELERATE", False )
		if hasattr(receiver,"onWaterArea") :
			if receiver.onWaterArea :
				if not isAccelerate:
					receiver.move_speed_percent += self._p1
					receiver.calcMoveSpeed()
					isAccelerate = True
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
				if receiver.energy < self._p2: #��Ծ����ֵ����
					buffID = self.getBuffID()
					if self._p3: #ֻ�����Ṧϵͳ��buff��ɾ��
						receiver.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					receiver.calEnergy( - self._p2 )
			else:
				if isAccelerate:
					receiver.move_speed_percent -= self._p1
					receiver.calcMoveSpeed()
					isAccelerate = False
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
					
		receiver.withdrawEidolonBeforeBuff( receiver.id )		# �����С������Ҫ�ջ�
		return  Buff_Normal.doLoop( self, receiver, buffData )
	
	
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
		isAccelerate = receiver.queryTemp( "BUFF_ISACCELERATE", False )
		if hasattr(receiver,"onWaterArea") :
			if receiver.onWaterArea :
				if not isAccelerate:
					receiver.move_speed_percent += self._p1
					receiver.calcMoveSpeed()
					isAccelerate = True
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
				
				if receiver.energy < self._p2: #��Ծ����ֵ����
					buffID = self.getBuffID()
					if self._p3: #ֻ�����Ṧϵͳ��buff��ɾ��
						receiver.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					receiver.calEnergy( - self._p2 )
			else:
				if isAccelerate:
					receiver.move_speed_percent -= self._p1
					receiver.calcMoveSpeed()
					isAccelerate = False
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
		receiver.withdrawEidolonBeforeBuff( receiver.id )		# �����С������Ҫ�ջ�

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
		isAccelerate = receiver.queryTemp( "BUFF_ISACCELERATE", False )
		if isAccelerate:
			receiver.move_speed_percent -= self._p1
			receiver.calcMoveSpeed()
		receiver.removeTemp( "BUFF_ISACCELERATE" )
		receiver.conjureEidolonAfterBuff( receiver.id )		# ���ԭ����С������Ҫ���ٻش���
