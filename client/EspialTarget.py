# -*- coding: gb18030 -*-
#
# $Id: EspialTarget.py,v 1.00 2008/09/6 11:19:09 huangdong Exp $

import GUIFacade
import csdefine
import event.EventCenter as ECenter
import BigWorld
from ItemsFactory import ObjectItem as ItemInfo
import csstatus


class EspialTarget:
	"""
	�۲�Է���ģ�飬��Ҫ����������ݺͽ��ܴ������ݵ�����
	"""
	_instance = None
	def __init__ ( self ):
		self.__assignmentData = [] #��¼��Ҫȥcellȡ���ݵ�����
		self.target = None			#Ҫ�۲�Ķ���
		self.callback = 0			#��¼�������ݵĻص�����
		self.NowAssignment = 0		#��ǰ����ɵ�����
		self.getNumber = 0			#��¼һ��ȡ������
		self.haveGetNumber = 0		#��¼����Ӧ�ô���ȡ
		self.endEspial = False		#��¼�Ƿ�����۲�

	def onEspialTarget(self ,target ):
		"""
		�۲�Է�
		@param   target: �Է����
		@type    target: ROLE
		from EspialTarget import espial
		espial.onEspialTarget(BigWorld.player())
		"""
		if target.__class__.__name__ != "Role":		# ��ĳЩ����� ���������������͵Ķ���
			return
		BigWorld.cancelCallback( self.callback )
		self.target = target
		self.endEspial = False
		lenth = BigWorld.player().position.flatDistTo(target.position) #���������Ŀ��ľ���
		if lenth > 10.0: #������볬��10�� ��ʾ�����Զ ���ܲ鿴
			BigWorld.player().statusMessage( csstatus.ESPIAL_TARGET_TOOFAR )
			return
		BigWorld.player().targetItems = [] #���Ҫ�۲�Ķ����װ���б� �Ա�ӷ��������»�ȡ
		BigWorld.player().espial_id = target.id	#��¼�۲�ĶԷ���ID
		self.SetAssignment(0, 4)	#��ʼ�趨Ҫȥ������ȡ������,1��ȡ4��
		self.NowAssignment = 0		#��ǰ����ɵ���������
		self.__assignmentData = [  #��¼��Ҫȡ������
					 "property",
					 "equip",	#��ȡװ�� һ��4��
					]
		ECenter.fireEvent( "EVT_ON_SHOW_TARGET", target )		#������Ϣ �ý���ȥ��ʾUI(��ʱUIû������ ֻ�пյĽ���)
		self.showTargetModel(target)	#��ʾ�Է������ģ��(��������ģ�Ͳ���ͨ����������ȡ������ֱ����ʾ)
		self.getInfos()					#�������������Ҫ�ĶԷ���ҵ���Ϣ

	def SetAssignment( self ,beginPos, OnceNumber ):
		"""
		���Ի�ȡ�����������ݣ���¼ȡ�Ŀ�ʼλ�ú��������Ա�ֶ��ȥ��ȡ���ݣ�����һ������������� �����������
		@param   beginPos: ��ʼȡ��λ��(����ȡ�����װ������װ����LIST�ж���������ʼȡ)
		@type    beginPos: INT
		@param   OnceNumber: ȡ������(����ȡ�����װ������װ����LIST��ȡ���ٸ�)
		@type    OnceNumber: INT
		"""
		self.BeginPos = beginPos
		self.getNumber = OnceNumber

	def SetNextAssignment(self ,beginPos, OnceNumber ):
		"""
		��ʼ�´�����ʱ,�趨ȡ�Ŀ�ʼλ�ú�����
		@param   beginPos: ��ʼȡ��λ��(����ȡ�����װ������װ����LIST�ж���������ʼȡ)
		@type    beginPos: INT
		@param   OnceNumber: ȡ������(����ȡ�����װ������װ����LIST��ȡ���ٸ�)
		@type    OnceNumber: INT
		"""
		self.SetAssignment( beginPos, OnceNumber )	#��������ȡ��λ�ú�����
		self.NowAssignment += 1						#���������1 ��ʾ��ʼ__assignmentData�б��е��¸�����

	def getInfos(self ):
		"""
		��ȡ���ݵĻص�������ÿ0.2���ȡһ���ֶԷ���ҵ���Ϣ �����������
		�����Ҫ�����µ����� �����޸Ĵ˺��� �����µ������֧
		"""
		try:
			assignment = self.__assignmentData[self.NowAssignment]		#��ȡ��ǰ������
		except IndexError:	#����Ѿ������������б��ʾ�Ѿ������� ��ô ���ٻص�
			return
		if self.endEspial:	#���ǿ�ƽ���,��ôֹͣ��ȡ��
			return
		if assignment == "property":	#����ֱ��ж���������ò�ͬ�������� �����ǻ�ȡ�Է�����
			BigWorld.player().cell.getTargetAttribute(self.target.id) #��ȡ�Է���������Ϣ
			self.SetNextAssignment(0, 4 )#��ʼ��ȡ��һ������ ��Ϊ������һ�λ�ȡ
		elif assignment == "equip":		 #��ȡ�Է�װ��
			if	self.BeginPos > 15:		 #����Ѿ���ͼ��ȡ��װ������ ����15�� ��ôֹͣ��ȡ ��ֹ����û�н��յ�������ϵ���Ϣ ��������ѭ��
				return
			BigWorld.player().cell.getTargetEquip(self.target.id,self.BeginPos,self.getNumber)	#��ȡ�Է���װ����Ϣ
			self.SetAssignment(self.getNumber + self.BeginPos, 4)								#��ʼ��ȡ��һ��
		else:
			return
		self.callback = BigWorld.callback( 0.2, self.getInfos ) 	#������ȡ

	def showTargetEquip(self , items, ifEnd):
		"""
		��ʾ��ҵ�װ��
		@param   items: �Է�װ�����б�һ�λ�ȡ��װ��������һ����4����
		@type    items: List
		@param   ifEnd: ��¼�Ƿ��Ѿ�ȡ��
		@type    ifEnd: BOOL
		"""
		if  ifEnd:	#���ȡ���ˣ���ô ��ʼ�¸�����
			self.SetNextAssignment(0, 0)
		itemInfos = []
		for item in items:	#�ֶ����UI����װ������
			BigWorld.player().targetItems.append( item )
			itemsInfo = ItemInfo( item ) #��װһ��װ��
			itemInfos.append(itemsInfo)	 #���������б�
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_EQUIP", ( itemInfos ) ) #֪ͨ���� ֻ֪ͨһ�αȷֶ��֪ͨ����Լ����

	def showTargetOtherInfo(self ,otherInfo):
		"""
		��ʾ��ҵİ�� ְλ �ȼ� �Ա�......
		@param   otherInfo: �Է�����ҵİ�� ְλ �ȼ� �Ա�......����
		@type    otherInfo: dictionary
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_TFINFO", (otherInfo) )	#��ʾ�����������

	def showTargetModel(self, target):
		"""
		��ʾ�Է���ҵ�ģ��
		@param   target: �Է���ҵ�ʵ��
		@type    target: PLAYERROLE
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_SHWO_TARGET_MODEL", target )	#��ʾ��ҵ�ģ��

	def stopEspial( self ):
		"""
		ֹͣ�۲�Է���ͨ����������ܳ��Լ���AOI���غ󴥷���
		�۲����ر�ʱҲ�ᴥ����
		"""
		BigWorld.cancelCallback( self.callback )
		BigWorld.player().espial_id = 0
		self.endEspial = True		# ����ǿ�ƽ�����ȡ���ݵı�־
		ECenter.fireEvent( "EVT_ON_END_SHOW_TARGET" )

	@staticmethod
	def instance():
		"""
		��ȡģ���ʵ��
		"""
		if EspialTarget._instance is None:
			EspialTarget._instance = EspialTarget()
		return EspialTarget._instance

def instance():
	return EspialTarget.instance()

espial = EspialTarget.instance()