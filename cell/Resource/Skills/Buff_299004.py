# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal

class Buff_299004( Buff_Normal ):
	"""
	����·������Buff
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Buff_Normal.__init__( self )
		self.lifeTime = 0				# ��������ʱ��
		self.repeatTime = 0				# ѭ���˺�ʱ��
		self.loopTime = 0.0				# ����������ʱ��
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���
		self.destroySpell = 0			# ��������ʱ�ͷŵļ���
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)
		self.isDisposable = 0			# �Ƿ�һ�������壨������һ�ξ����٣�
		self.skillID = 0				# �����Դ�����ID
		self.moveEffective = False		# �Ƿ��ƶ���Ч��Ĭ���ƶ���Ч

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		timeStr = dict["Param1"].split( ";" )
		if len( timeStr ) >= 3:
			self.lifeTime = int( timeStr[0] )
			self.repeatTime = int( timeStr[1] )
			self.loopTime = float( timeStr[2] )
		spellStr = dict["Param2"].split( ";" )
		if len( spellStr ) >= 4:
			self.enterSpell = int( spellStr[0] )
			self.leaveSpell = int( spellStr[1] )
			self.destorySpell = int( spellStr[2] )
			self.skillID = int( spellStr[3] )
		modelStr = dict["Param3"].split( ";" )
		if len( modelStr ) >= 3:
			self.radius = float( modelStr[0] )
			self.isDisposable = int( modelStr[1] )
			self.modelNumber = str( modelStr[2] )
			try:
				self.moveEffective = bool( int( modelStr[3] ) )
			except:
				self.moveEffective = False	# ����Ĭ���ƶ���Ч

	def _getDict( self, receiver ):
		"""
		"""
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"destroySpell" : self.destroySpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : self.lifeTime, \
			"repeattime" : self.repeatTime, \
			"casterID" : receiver.id, \
			"uname" : self.getName() }
		return dict

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
		# ���ɻ�������
		receiver.setTemp( "FLAME_TRAP_DICT", self._getDict( receiver ) )
		receiver.setTemp( "FLAME_SKILLID", self.skillID )
		receiver.setTemp( "FLAME_MOVE_EFFECTIVE", self.moveEffective )
		receiver.getFlameWay( self.loopTime )

	def doReload( self,  receiver, buffData ):
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
		# ���ɻ�������
		receiver.setTemp( "FLAME_TRAP_DICT", self._getDict( receiver ) )
		receiver.setTemp( "FLAME_SKILLID", self.skillID )
		receiver.setTemp( "FLAME_MOVE_EFFECTIVE", self.moveEffective )
		receiver.getFlameWay( self.loopTime )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.delFlameWay()
