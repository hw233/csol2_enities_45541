# -*- coding: gb18030 -*-

# ����Ҫ��ӶԻ�����Ĵ��ڳ������������������Ӻ��Ƴ��Ի�����
# �ı�������
# by gjx 2010-08-18

from Window import Window
import BigWorld
import csconst

class TrapWindowBase( Window ) :

	def __init__( self, wnd = None ) :
		Window.__init__( self, wnd )

		self.__trappedEntityID = 0						# id of the trapped entity
		self.trapID_ = 0								# id of the added trap


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addTrap_( self ) :
		"""
		�������
		"""
		pass

	def delTrap_( self ) :
		"""
		�Ƴ�����
		"""
		pass

	def onTrapTriggered_( self, *args ) :
		"""
		���崥��
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTrappedEntID( self, id ) :
		"""
		�ṩ�ýӿڸ��ⲿ����entity��ID
		Ӧ���ڴ�����ʾ֮ǰ����entityID
		"""
		self.__trappedEntityID = id

	def show( self ) :
		"""
		Ĭ�ϴ�����ʾʱ�������
		"""
		Window.show( self )
		self.addTrap_()

	def hide( self ) :
		"""
		Ĭ�ϴ��ڹر�ʱ�Ƴ�����
		"""
		Window.hide( self )
		self.delTrap_()

	def dispose( self ) :
		"""
		��������ʱ����
		"""
		self.delTrap_()
		Window.dispose( self )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def trappedEntity( self ) :
		return BigWorld.entities.get( self.__trappedEntityID )


class FixedTrapWindow( TrapWindowBase ) :
	"""�����λ���ǹ̶��ģ���ҽ�������ʱ���лص���
	�����ڴ���֮��Ͳ������ٵ�Entity"""

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addTrap_( self ) :
		"""
		Ĭ�������һ����̬������
		"""
		self.delTrap_()
		trapEnt = self.trappedEntity
		if trapEnt :
			distance = csconst.COMMUNICATE_DISTANCE
			if hasattr( trapEnt, "getRoleAndNpcSpeakDistance" ) :
				distance = trapEnt.getRoleAndNpcSpeakDistance()
			self.trapID_ = BigWorld.addPot( trapEnt.matrix, distance, self.onTrapTriggered_ )
		else :
			self.hide()

	def delTrap_( self ) :
		"""
		�Ƴ�����
		"""
		if self.trapID_ > 0 :
			BigWorld.delPot( self.trapID_ )
			self.trapID_ = 0

	def onTrapTriggered_( self, enteredTrap, handle ) :
		"""
		���崥��
		@param	enteredTrap		: �Ƿ����������
		@type	enteredTrap		: int( ����������1, ������0 )
		@param	handle			: ����ID
		@type	handle			: int
		"""
		if not enteredTrap :
			self.hide()


class UnfixedTrapWindow( TrapWindowBase ) :
	"""���������������ϣ���Entity��������ʱ���лص���
	�����ڴ���֮������ٵ�Entity"""

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addTrap_( self ) :
		"""
		Ĭ�������һ����̬������
		"""
		self.delTrap_()
		trapEnt = self.trappedEntity
		if trapEnt :
			distance = csconst.COMMUNICATE_DISTANCE
			if hasattr( trapEnt, "getRoleAndNpcSpeakDistance" ) :
				distance = trapEnt.getRoleAndNpcSpeakDistance()
			self.trapID_ = BigWorld.player().addTrapExt( distance, self.onTrapTriggered_ )
		else :
			self.hide()

	def delTrap_( self ) :
		"""
		�Ƴ�����
		"""
		if self.trapID_ > 0 :
			BigWorld.player().delTrap( self.trapID_ )
			self.trapID_ = 0

	def onTrapTriggered_( self, entitiesInTrap ) :
		"""
		���崥��
		@param	enteredTrap		: �Ƿ����������
		@type	enteredTrap		: int( ����������1, ������0 )
		@param	handle			: ����ID
		@type	handle			: int
		"""
		if self.trappedEntity not in entitiesInTrap :
			self.hide()
