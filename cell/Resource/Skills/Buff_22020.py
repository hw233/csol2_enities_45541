# -*- coding: gb18030 -*-
#��ȫ���߶��ж�buff

from Buff_Normal import Buff_Normal
import csstatus
import csdefine

class Buff_22020( Buff_Normal ):
	"""
	��ȫ���߶��ж�buff
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] ) #��ȫ���ݽ���Y����
		self._p2 = float( dict[ "Param2" ] ) #����߶�
		self._loopSpeed = 3
		

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
		pos = receiver.position
		if pos[1] - self._p1 <= self._p2: #���ڸ߶��򲻽��밲ȫ��
			if not receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#���û�а�ȫ����־
				receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA ) # ������ϼ�һ����ȫ����ı�־������һЩ�������ж�
				receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )# ��ֹPK
				receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )

	def doLoop( self, receiver, buffData ):
		"""
		@add by wuxo 2011-11-11
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		pos = receiver.position
		if pos[1] - self._p1 <= self._p2: #���ڸ߶��򲻽��밲ȫ��
			if not receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#���û�а�ȫ����־
				receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA ) # ������ϼ�һ����ȫ����ı�־������һЩ�������ж�
				receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )# ��ֹPK
				receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )
		else:
			if receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#����а�ȫ����־
				receiver.removeFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# �Ƴ�������ϵİ�ȫ����ı�־
				receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )	
				receiver.statusMessage( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA )
				
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
		pos = receiver.position
		if pos[1] - self._p1 <= self._p2: #���ڸ߶��򲻽��밲ȫ��
			if not receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#���û�а�ȫ����־
				receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA ) # ������ϼ�һ����ȫ����ı�־������һЩ�������ж�
				receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )# ��ֹPK
				receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )
			

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
		if receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#����а�ȫ����־
			receiver.removeFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# �Ƴ�������ϵİ�ȫ����ı�־
			receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )	
			receiver.statusMessage( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA )
