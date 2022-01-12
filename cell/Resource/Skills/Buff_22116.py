# -*- coding: gb18030 -*-

"""
����buff��buff������ı�Ϊ����״̬
"""
import csdefine
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22116( Buff_Normal ):
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
		receiver.begin_body_changing( self._model, self._modelScale )
		Buff_Normal.doBegin( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		����buff�����󣬽�ɫ�ָ�����״̬
		"""
		receiver.end_body_changing( receiver.id, "" )
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

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		if receiver.getState() != csdefine.ENTITY_STATE_CHANGING:
			receiver.end_body_changing( receiver.id, "" )
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
