# -*- coding: gb18030 -*-
#
# �������NPC 2009-01-17 SongPeifang
#

from bwdebug import *
from NPC import NPC
import random
import csdefine
import csconst
import csstatus
import cschannel_msgs

SAY_CHANGE_MODEL	= 0
CHANGE_TO_MODEL		= 1
CHANGE_LIE_MODEL	= 2
WAIT_TO_CHECK		= 3
CHECK_MEMBERS 		= 4

class BCNPC( NPC ):
	"""
	�������NPC
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_NPC )
		self._canLogin	= False	# �ܷ���
		self._members	= {}	# �������������{������databaseID:�ɹ���ɴ���}
		self._passMembers = []	# ������¼���ص���ҵ��콱���
		self._currentCount = 0	# ��ǰ�ǵڼ��α���
		self._animals = cschannel_msgs.BCNPC_S_1
		self.modelNumberStored = self.modelNumber
		self.modelScaleStored = self.modelScale

	def loginBCGame( self, player ):
		"""
		�����μӱ������
		"""
		self._members[ player.databaseID ] = 0
		self.base.getLoginMembers( len( self._members ) )

	def getLoginState( self, loginState ):
		"""
		Define Method.
		��base��ȡ���Ƿ���Ա���
		"""
		self._canLogin = loginState

	def isPlayerLogin( self, player ):
		"""
		ȡ����ұ���״̬
		"""
		return self._members.has_key( player.databaseID )

	def canLogin( self ):
		"""
		�Ƿ���Ա���
		"""
		return self._canLogin

	def hasMembers( self ):
		"""
		�Ƿ�����Ҳμ�
		"""
		return len( self._members ) != 0

	def bcGameStart( self ):
		"""
		Define Method.
		���������ʽ��ʼ��
		"""
		self.say( cschannel_msgs.BCNPC_1 )
		self.addTimer( 2, 0, SAY_CHANGE_MODEL )

	def sayChangeModel( self ):
		"""
		NPC��������Լ�Ҫ���ʲô
		"""
		self._currentCount += 1
		if len( self._members ) <= 0:
			self.say( cschannel_msgs.BCNPC_2 )
			self._canLogin	= False
			self._currentCount = 0
			return
		elif self._currentCount > 20:
			count = 0
			for i in self._members:
				if self._members[i] == 20:
					self._passMembers.append( i )
					count += 1
			self.say( cschannel_msgs.BCNPC_3 % count )
			
			self._members.clear()
			self._canLogin	= False
			self._currentCount = 0
			return
		animalIndex = random.randint( 0, len( self._animals ) - 1 )
		self._animalKey = self._animals.keys()[ animalIndex ]
		animal = self._animals[ self._animalKey ]
		self.say( cschannel_msgs.BCNPC_4 % animal )
		sayWait = self.afterSayWaitTime()
		honest = 0.7	# ��ʵ������70%,˵�Ѽ�����30%
		r = random.random()
		if r <= honest:
			self.addTimer( sayWait, 0, CHANGE_TO_MODEL )
		else:
			newIndex = self.getDiffIndex( animalIndex )
			self._animalKey = self._animals.keys()[ newIndex ]
			self.addTimer( sayWait, 0, CHANGE_LIE_MODEL )

	def changeBody( self ):
		"""
		NPC���ĳģ��
		"""
		self.modelScale = 2.0
		self.modelNumber = self._animalKey
		changeCheckWaitTime = self.afterChangeCheckTime()
		members = self.entitiesInRangeExt( 50, "Role", self.position )
		for p in members:
			if p.databaseID in self._members:
				p.client.playIntonateBar( changeCheckWaitTime )
				p.statusMessage( csstatus.SKILL_BODY_CHANGING_CHECK )
		self.addTimer( changeCheckWaitTime, 0, WAIT_TO_CHECK )

	def changeLieBody( self ):
		"""
		NPC˵�ѵı��ĳģ��
		"""
		self.say( cschannel_msgs.BCNPC_5 )
		self.changeBody()

	def checkMembers( self ):
		"""
		NPC�����Χ50������ұ������
		"""
		members = self.entitiesInRangeExt( 50, "Role", self.position )
		for p in members:
			if p.databaseID in self._members:
				if p.getCurrentBodyNumber() == self.modelNumber:
					self._members[p.databaseID] += 1
					p.addExp( self.getSuccessExpRwd( p.level, self._members[p.databaseID] ), csdefine.CHANGE_EXP_BCNPC )
					p.statusMessage( csstatus.BC_CHANGE_BODY_SUCCESSFUL )
				else:
					self._members[p.databaseID] = 0
					p.statusMessage( csstatus.BC_CHANGE_BODY_FAILED )
			if self._currentCount >= 20:
				p.statusMessage( csstatus.SKILL_BODY_CHANGE_FINISH )
				
		checkWaitTime = self.afterCheckWaitTime()		# �����֮����Ϣ�೤ʱ�������һ�α���
		self.modelScale = self.modelScaleStored			# �����֮�󣬻ָ�NPC��ģ��Ϊԭʼ�ߴ�
		self.modelNumber = self.modelNumberStored		# �����֮�󣬻ָ�NPC��ģ��Ϊԭʼģ��
		self.addTimer( checkWaitTime, 0, SAY_CHANGE_MODEL )	# ��checkWaitTimeʱ��������һ�α���

	def onTimer( self, id, userArg ):
		"""
		֪ͨ������ұ��������ʼ
		"""
		NPC.onTimer( self, id, userArg )
		if userArg == SAY_CHANGE_MODEL:
			# ˵��������ҡ���Ҫ���XXX��
			self.sayChangeModel()
		elif userArg == CHANGE_TO_MODEL:
			# NPC���б�����ģ��
			self.changeBody()
		elif userArg == CHANGE_LIE_MODEL:
			# NPC���б�����ģ�ͣ����ǻ���ģ�Ͳ�����˵��Ҫ���ģ��
			self.changeLieBody()
		elif userArg == WAIT_TO_CHECK:
			# �����Щ���ͨ������Щ��ұ���̭
			self.checkMembers()

	def getDiffIndex( self, index ):
		"""
		ȡ��һ����ͬ��ģ������
		"""
		animalIndex = index
		while( animalIndex == index ):
			# ��Ȼ��˵�ѣ���ôһ��Ҫȡ��һ����ͬ��ģ��
			animalIndex = random.randint( 0, len( self._animals ) - 1 )
		return animalIndex

	def afterSayWaitTime( self ):
		"""
		NPC���Ժ�ȴ��೤ʱ����б���
		"""
		if self._currentCount >= 1 and self._currentCount <= 8:
			# 1-8�� ���Ժ�5����Ա���
			return 5
		elif self._currentCount >= 9 and self._currentCount <= 15:
			# 9-15�� ���Ժ�5����Ա���
			return 5
		else:
			# 16-20�� ���Ժ�2����Ա���
			return 2

	def afterChangeCheckTime( self ):
		"""
		NPC�����ȴ��೤ʱ����м�顢��̭���
		"""
		if self._currentCount >= 1 and self._currentCount <= 8:
			# 1-8�� �����5�뿪ʼ�����ұ������
			return 5
		elif self._currentCount >= 9 and self._currentCount <= 15:
			# 9-15�� �����3�뿪ʼ�����ұ������
			return 3
		else:
			# 16-20�� �����3�뿪ʼ�����ұ������
			return 3

	def afterCheckWaitTime( self ):
		"""
		NPC��顢��̭����Һ󣬵ȴ��೤ʱ�������һ�α���
		"""
		if self._currentCount >= 1 and self._currentCount <= 8:
			# 1-8�� ������Ϣ5�뿪ʼ��һ�α���˵��
			return 5
		elif self._currentCount >= 9 and self._currentCount <= 15:
			# 9-15�� ������Ϣ3�뿪ʼ��һ�α���˵��
			return 3
		else:
			# 16-20�� ������Ϣ1�뿪ʼ��һ�α���˵��
			return 1

	def clearPassMembers( self, player = None ):
		"""
		�����ȡ�����������
		"""
		if player == None:
			self._passMembers = []
		elif player.databaseID in self._passMembers:
			self._passMembers.remove( player.databaseID )

	def getSuccessExpRwd( self, level, cCount ):
		"""
		ÿ�α����ԣ���þ��齱��
		(LV+23) * ������� * 5
		"""
		return csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_BIAN_SHEN_DA_SAI, level, cCount )