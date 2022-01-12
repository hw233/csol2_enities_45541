# -*- coding: gb18030 -*-
#
import csdefine
from Buff_Normal import Buff_Normal

 
class Buff_22130( Buff_Normal ):
	"""
	身轻如燕
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._p2 = 0
		self._p3 = 0 #1表示轻功系统buff
		#self.modelNum = None	#记录上下骑宠add by wuxo 2011-11-11

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
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
		使用恶性技能被触发
		"""
		if not self._p3: return
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def springOnDamage( self, caster, skill ):
		"""
		接收伤害后
		"""
		if not self._p3: return
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
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
					
				if receiver.energy < self._p2: #跳跃能量值不够
					buffID = self.getBuffID()
					if self._p3: #只有是轻功系统的buff才删除
						receiver.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					receiver.calEnergy( - self._p2 )
			else:
				if isAccelerate:
					receiver.move_speed_percent -= self._p1
					receiver.calcMoveSpeed()
					isAccelerate = False
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
					
		receiver.withdrawEidolonBeforeBuff( receiver.id )		# 如果有小精灵则要收回

	def doLoop( self, receiver, buffData ):
		"""
		@add by wuxo 2011-11-11
		@param receiver: 效果要影响的实体
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
				if receiver.energy < self._p2: #跳跃能量值不够
					buffID = self.getBuffID()
					if self._p3: #只有是轻功系统的buff才删除
						receiver.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					receiver.calEnergy( - self._p2 )
			else:
				if isAccelerate:
					receiver.move_speed_percent -= self._p1
					receiver.calcMoveSpeed()
					isAccelerate = False
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
					
		receiver.withdrawEidolonBeforeBuff( receiver.id )		# 如果有小精灵则要收回
		return  Buff_Normal.doLoop( self, receiver, buffData )
	
	
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
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
				
				if receiver.energy < self._p2: #跳跃能量值不够
					buffID = self.getBuffID()
					if self._p3: #只有是轻功系统的buff才删除
						receiver.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					receiver.calEnergy( - self._p2 )
			else:
				if isAccelerate:
					receiver.move_speed_percent -= self._p1
					receiver.calcMoveSpeed()
					isAccelerate = False
					receiver.setTemp( "BUFF_ISACCELERATE", isAccelerate )
		receiver.withdrawEidolonBeforeBuff( receiver.id )		# 如果有小精灵则要收回

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
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
		receiver.conjureEidolonAfterBuff( receiver.id )		# 如果原来有小精灵则要做召回处理
