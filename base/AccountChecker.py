# -*- coding: gb18030 -*-
#
"""
�˺ż����ģ��:
	�˺ż����ģ���Ϊ�˺ż�������(Checker)���˺ż�������(BaseChecker......),����µ����ʱ,��Ҫ�̳м�������������BaseChecker
	����д���ṩ��ģ�顣�µ������Ҫ���ӵ�����б��У�checkers���У����б�������ġ����ռ����Ⱥ�˳��������С�
"""


import BigWorld
import Const
import time
import random
import weakref
from bwdebug import *
import csstatus

class Checker:
	"""
	�˺ż����
	"""
	_instance = None
	def __init__( self, accountID ):
		"""
		��ʼ��
		"""
		self.checkers = []												# ���еļ�����б�
		self.accountID = accountID								# �˺�ʵ��
		self.currentChecker = -1										# ��ǰʹ�õļ��������
		for checker in checkers:										# ��ʼ�����еļ��ģ��
			self.checkers.append( checker( self.accountID ))

	def checkAccount( self ):
		"""
		����˺��Ƿ��ܹ���¼
		"""
		self.clear()
		self.checkAlong()

	def account( self ):
		"""
		��ȡ��ҵ��˺�
		"""
		try:
			return BigWorld.entities[self.accountID]
		except:
			ERROR_MSG( "account is not exist, id = %s" % self.accountID )
			return None

	def checkAlong( self ):
		"""
		����˺�
		"""
		if not self.account():										# ����˺��Ѿ���������,��ôֱ���˳���
			self.clear()
			return
		self.currentChecker += 1									# ���������ָ����һ���������(��ʼΪ-1.+1�󼴴ӵ�һ����ʼ���)
		if self.currentChecker < 0:									# ��������ȷ�����,���������������Զ�������
			self.clear()
			ERROR_MSG( "get a error checker index = %s" % self.currentChecker )
			return
		elif self.currentChecker < len( self.checkers ):			# ������ȷ�����
			self.checkers[self.currentChecker].onCheck()			# �����Ȩ������������
		else:														# �����ϻ���û�м���������
			self.account().onBeginLogAccount()						# ���Ե�¼
			self.clear()											# �ָ����������

	def getCurrentChecker( self ):
		"""
		��ȡ��ǰ��checker
		"""
		try:
			return self.checkers[self.currentChecker]
		except:
			return None

	def clear( self ):
		"""
		�ָ�����,�Ա㵱���˼��ͻ��˵�ʱ�����¼��
		"""
		self.currentChecker = -1
		for checker in self.checkers:				# �ָ���������������
			checker.clear()


class BaseChecker:
	"""
	���������Ļ���ģ��
	"""
	def __init__( self, accountID ):
		"""
		��ʼ��
		"""
		self.accountID = accountID		# �洢����˺� entity ID

	def onCheck( self ):
		"""
		�������Ƿ񱻷��,���뱻��д
		"""
		pass

	def clear( self ):
		"""
		��ԭchecker���ݣ� ���뱻��д
		"""
		pass

	def account( self ):
		"""
		��ȡ��ҵ��˺�
		"""
		try:
			return BigWorld.entities[self.accountID]
		except:
			ERROR_MSG( "account is not exist, id = %s" % self.accountID )
			return None



class BlockChecker( BaseChecker ):
	"""
	�˺ŷ�������
	"""
	def __init__( self, accountID ):
		"""
		��ʼ��
		"""
		BaseChecker.__init__( self, accountID )

	def onCheck( self ):
		"""
		�������Ƿ񱻷��
		"""
		if self.checkBlock():							# �˺ű����
			self.checkFailed()							# ֪ͨ�ͻ��˶Ͽ�����
		else:											# ͨ�����
			self.account().getChecker().checkAlong()		# �ѿ���Ȩ������ Checker

	def checkBlock( self ):
		"""
		����Ƿ񱻷��
		@param accountIns : �˺ŵ�ʵ��
		@type  accountIns : Account
		"""
		if self.account().block_state:
			now = time.time()
			if now <= self.account().block_end_time or self.account().block_end_time == -1:
				return True
			else:
				self.account().block_state = 0
				self.account().block_end_time = 0
				return False
		return False

	def checkFailed( self ):
		"""
		���ʧ�� ֪ͨ�˺�
		@param accountIns : �˺ŵ�ʵ��
		@type  accountIns : Account
		"""
		self.account().onAccountlockedNotify( self.account().block_end_time )		#֪ͨ�ͻ�����ס��
		self.account().getChecker().clear()											#�ͷ�����



class PasswdProtect_Matrix( BaseChecker ):
	"""
	���뱣��������

	ע: �ܱ���״̬��Ϊ����:
		1- δ��
		2- �Ѱ�
		3- ��ʧ��ͣ
	"""
	COORDINATENUM = 6	# Ҫ��ұȶԵ�����λ��( 6����3������ �� 11 21 31 )
	def __init__(  self, accountID  ):
		"""
		��ʼ��
		"""
		BaseChecker.__init__( self, accountID )
		self.passwdPro_state = "" 	# ����״̬
		self.matrix_value = []		# ���󿨵�ֵ
		self.answer       = []		# �˴ε�½�ľ��󿨵Ĵ�
		self.position     = 0		# �˴ε�½�ľ��󿨵�����
		self.inputTimes   = 0		# �ͻ����������ֵ�ô���

	def init( self ):
		"""
		��ȡ��������
		"""
		self.passwdPro_state   =  self.account().customData.query( "passwdPro_state")		# ��¼��ǰ����״̬
		matrix_value = self.account().customData.query( "matrix_value")						# ��¼��ǰ����ֵ

		if not self.passwdPro_state or not matrix_value:
			return

		self.passwdPro_state = int( self.passwdPro_state)
		if matrix_value.find(',') >= 0:
			self.matrix_value = matrix_value.split(',')
		else:
			for i in range( 0, len(matrix_value), 2):
				self.matrix_value.append( matrix_value[i:i+2] )

	def onCheck( self ):
		"""
		���ݿ��л�ȡ��Ӧ������,��������״̬��֪ͨ�ͻ������ݾ���ֵ
		"""
		self.init()								# ��ȡ��������
		if not self.passwdPro_state:
		# ���û�в��ҵ����ݣ�˵��û�а��ܱ���
		# (ע���������޸�Ϊ�鿴����Ƿ��п�ͨ�ܱ�������,Ŀǰ��ͨ�ܱ��������ܱ�������û�и����Ƿ�Ҫ���Ĵ�)
			self.account().getChecker().checkAlong()
		elif self.passwdPro_state == 1:
		# δ�󶨾��� ����ͨ��
			self.account().getChecker().checkAlong()
		elif self.passwdPro_state == 2:
		# ��ͨ�˾��� ��Ҫ֪ͨ�ͻ����������ֵ
			self.position,self.answer = self.random_checkValues()
			self.account().client.input_passwdPro_matrix( self.position, self.inputTimes )	# ������Ϣ�ÿͻ��������
		elif self.passwdPro_state == 3:
		# ��ʧ��ͣ״̬����ʧ��ͣ�ķ�ͣ״̬��ʱ������,�������ʱ��,�ǿ���������½��,��������˵���Ѿ������Ƿ���,
		# ��������һ���ǹ�ʧ�ҷ�ͣʱ�䳬����״̬�������½��
			self.account().getChecker().checkAlong()


	def random_checkValues( self ):
		"""
		������󿨵�ֵ�;���ֵ����
		"""
		keys   = 0
		values = []
		for i in xrange( 0, self.COORDINATENUM, 2 ):
			cs = random.randint(1,9)
			ip = random.randint(1,9)
			baseValue = 10 ** i
			keys += ( cs * 10 + ip ) * baseValue
			values.insert( 0, self.get_checkValue( cs, ip ) )
		return ( keys,  ",".join( values ) )
		#ע: ����ֱ�ӷ�������ֵ,��values��һ���ַ�ֵΪ0ʱ�ᱻ����,���ǿͻ��˴���ʱ��Ȼ�ô˷���ת��������ֵ���Դ𰸵Ĵ�С������Ӱ��

	def get_checkValue( self, cs, ip ):
		"""
		��ȡ��Ӧ�����checkֵ
		@type  pos : string
		@param pos : ��ֵ��λ�� ���� 11
		"""
		#-----����λ�õķ�ʽ������+����  cs-1  ip-1 ��λ�õ��±�
		line = 9 * (cs-1)
		index   = line + (ip - 1)
		return self.matrix_value[ index]

	def check_passwdProMatrixValue( self, value ):
		"""
		����������Ĵ�,��������ظ��ͻ���
		@type  value : STRING
		@param value : �ͻ��˴����ľ��󿨴�
		"""
		if self.ifRightAnswert( value ):
			self.account().client.input_passwdPro_matrix(  self.position, 255 )				# ���߿ͻ���ͨ�������ܱ���� 255����ͨ�����
			self.account().getChecker().checkAlong()											# �ѿ���Ȩ�������˺ż����
		else:
			self.inputTimes += 1															# �������ݴ���
			self.account().client.input_passwdPro_matrix(  self.position, self.inputTimes  )	# ֪ͨ�ͻ���������󣬷������������ʹ���

	def ifRightAnswert( self, value ):
		"""
		���ͻ��˵���������������ܱ����Ĵ�
		@type  value : UINT32
		@param value : �ͻ��˴����ľ��󿨴�
		"""
		return (self.answer == value) and (self.answer )

	def clear( self ):
		"""
		�ָ���������
		"""
		self.answer       = []		# �˴ε�½�ľ��󿨵Ĵ�
		self.position     = 0		# �˴ε�½�ľ��󿨵�����
		self.inputTimes   = 0		# �ͻ����������ֵ�ô���

	def reCheck( self ):
		"""
		�ٴμ������ܱ�
		"""
		self.clear()				# �ָ�����
		self.position,self.answer = self.random_checkValues()
		self.account().client.input_passwdPro_matrix( self.position, self.inputTimes )	# ������Ϣ�ÿͻ��������

class checkBaseSectionMD5( BaseChecker ):
	"""
	Account���ݿ��ֶ�MD5����� by ����
	"""
	def __init__( self, accountID ):
		"""
		��ʼ��
		"""
		BaseChecker.__init__( self, accountID )

	def onCheck( self ):
		"""
		Account��Ĳ����ֶε�MD5���
		"""
		accountEntity = self.account()
		if accountEntity.checkPropertyMD5():
			INFO_MSG( "%s account md5 check passed"%( accountEntity.playerName ) )
			accountEntity.getChecker().checkAlong()		# �ѿ���Ȩ������ Checker
		else:
			ERROR_MSG( "%s account md5 check failed"%( accountEntity.playerName ) )
			accountEntity.statusMessage( csstatus.ACCOUNT_MD5_CHECK_FAILED, "" )
			accountEntity.getChecker().clear()											#�ͷ�����
			accountEntity.logoff()

	def clear( self ):
		"""
		"""
		pass

#---------------checkerģ���б�---------------
checkers = [									# ע ���б�������ģ���Ҫ�����Ⱥ�˳���⡣
				BlockChecker,
				PasswdProtect_Matrix,
				checkBaseSectionMD5,
			]