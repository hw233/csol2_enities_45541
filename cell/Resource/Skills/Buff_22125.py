# -*- coding: gb18030 -*-

"""
����buff��buff������ı�Ϊ����״̬
"""
import csdefine
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

class Buff_22125( Buff_Normal ):
	"""
	����buff
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._modelScale = 1.0			# ����ģ�����ű���
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._model = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 								# ���ܶ�Ӧ��ģ�ͱ��
		self._modelScale = float( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0.0 ) 					# �����ģ�����ű���
		
	def doBegin( self, receiver, buffData ):
		# ֪ͨ��������ģ��
		print "=======>>>>>>skills self.getBuffID() = ", self.getBuffID()
		receiver.setTemp( "body_changing_buff_id", self.getBuffID() )
		
		# �������
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.currentModelNumber = self._model
			receiver.currentModelScale = self._modelScale
		else:
			receiver.setTemp("oldModelNumber", receiver.modelNumber )
			receiver.setTemp("oldModelScale", receiver.modelScale )
			receiver.modelNumber = self._model
			receiver.modelScale = self._modelScale
		
		Buff_Normal.doBegin( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		����buff�����󣬽�ɫ�ָ�����״̬
		"""
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if not receiver.queryTemp( "body_changed_replace_buff", False ):	# �����ɫΪ����״̬
				receiver.currentModelNumber = ""
		else:
			receiver.modelNumber = receiver.queryTemp( "oldModelNumber" )
			receiver.modelScale = receiver.queryTemp( "oldModelScale" )
		receiver.removeTemp( "body_changed_replace_buff" )
		receiver.removeTemp( "body_changing_buff_id" )
		Buff_Normal.doEnd( self, receiver, buffData )
	
	def _replaceLowLvBuff( self, caster, receiver, newBuff, buffs ):
		"""
		Buff �� �滻������  ��buffs���滻��ͼ����BUFF
		@param receiver: �ܻ���
		@type  receiver: Entity
		@param newBuff: ��BUFF������
		@type  newBuff: BUFF
		@param buffs: ׼�������жϵ�buff�����б�
		"""
		receiver.setTemp( "body_changed_replace_buff", True )
		Buff_Normal._replaceLowLvBuff( self, caster, receiver, newBuff, buffs )
