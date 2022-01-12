# -*- coding: gb18030 -*-
#
"""
������ϵͳģ��
2010.06.09: rewriten by huangyongwei
"""

import time
import BigWorld
import csdefine

class AntiWallow :
	"""
	δ�����˷�����ϵͳ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		self.bWallow_isAdult = False				# �Ƿ��ǳ����ˣ�defined��


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onGetCell( self ) :
		eAccount = getattr( self, "accountEntity", None )
		if eAccount :
			isAdult = eAccount.customData.query( "adult" )
			if isAdult == "" or not isAdult :						# ����Ϊ�ջ�δ���ã�������Ϊ��δ����
				isAdult = False
			else:
				isAdult = int( isAdult )
		else:
			ERROR_MSG( "%s(%i:%i): I has no account entity." % ( self.getName(), self.databaseID, self.id ) )
			return	# �Ҳ��������ʺ�����֤�Ƿ�δ���꣬ʹ��Ĭ��ֵ�ͺ�
		
		if not isAdult:												# �����δ������
			gwp = BigWorld.globalBases["AntiWallowBridge"]
			gwp.onAccountLogin( eAccount.playerName )				# ��������Ժ�̨���͵�¼��Ϣ
		
		self.bWallow_isAdult = isAdult
		self.cell.wallow_setAgeState( isAdult )

	def onLoseCell( self ) :
		eAccount = getattr( self, "accountEntity", None )
		if eAccount and not self.bWallow_isAdult :						# ����Ƿǳ�����
			gwp = BigWorld.globalBases["AntiWallowBridge"]
			gwp.onAccountLogout( eAccount.playerName )					# ��������Ժ�̨���͵ǳ���Ϣ

	# -------------------------------------------------
	def wallow_onWallowNotify( self, state, olTime ) :
		"""
		defined.
		��������
		@type			state  : MACRO DEFINATION
		@param			state  : ����״̬���� csdefine �ж��壺WALLOW_XXX
		@type			olTime : INT64
		@param			olTime : ����ʱ��
		"""
		self.cell.wallow_onWallowNotify( state, olTime )


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def wallow_setAgeState( self, isAdult ) :
		"""
		defined.
		��������״̬
		@type			isAdult : BOOL
		@param			isAdult : �Ƿ��ǳ���
		"""
		eAccount = getattr( self, "accountEntity", None )
		if eAccount :
			eAccount.customData.set( "adult", str( int( isAdult ) ) )	# �� BOOL �͵� isAdult ת��Ϊ�ַ�'0','1'����ԭ���ݱ��������Է�ʹ�õ�ʱ��֪����ֻ�ᱻ�޸Ķ�����
			self.bWallow_isAdult = isAdult
			self.cell.wallow_setAgeState( isAdult )
