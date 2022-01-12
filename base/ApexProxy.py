# -*- coding: gb18030 -*-
#
# $Id: ApexProxy.py,v 1.119 2009-06-25 03:50:30 LuoCD Exp $


"""
����Ҵ����֡�

"""

import BigWorld
from MsgLogger import g_logger
from bwdebug import *
from Const   import START_APEX_FLAG

class ApexProxy( ):
	def __init__( self ):
		INFO_MSG("init ApexProxy")
		if START_APEX_FLAG :
			self.apexProxy = BigWorld.getApexProxy( )
			self.apexProxy.InitAPexProxy(self.sendMsgToApexClient,self.apexKillRole)
		else:
			INFO_MSG("init ApexProxy START_APEX_FLAG is False")
			self.apexProxy = None

	def getApexStartFlag(self):
		return self.apexProxy != None

	def sendMsgToApexClient( self,nRoleId,pBuffer,nLen):
		INFO_MSG("ApexProxy sendMsgToApexClient: nRoleId(%d),nLen(%d)"%(nRoleId,nLen))
		#Ҫ�ȸ���nRoleId,ȡ��role,�ٵ���role.sendMsgToApexClient(pBuffer,nLen)
		role = BigWorld.entities.get( nRoleId, None )
		if role is None :
			# role is not exist #��ʱ��������
			None
		else :
			# role exists
			role.sendMsgToApexClient(pBuffer,nLen)

	def apexKillRole( self,nRoleId,Action ):
		hiByte = (0xFFFF0000 & Action)>>16
		lowByte = 0x0000FFFF & Action
		INFO_MSG("ApexProxy apexKillRole,  nRoleId(%d),  hiByte(%d),  lowByte(%d)"%(nRoleId,hiByte,lowByte))
		#Ҫ�ȸ���nRoleId,ȡ��role,�ٵ���role.logout()
		role = BigWorld.entities.get( nRoleId, None )
		if role is None :
			# role is not exist #��ʱ��������
			None
		else :
			# role exists
			role.logoff( )
			try:
				g_logger.apexKickRoleLog( role.databaseID, role.getName(), hiByte, lowByte )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


	def startApexProxy( self ):
		INFO_MSG("ApexProxy startApexProxy")
		self.apexProxy.StartApexProxy()

	def stopApexProxy( self ):
		if(self.apexProxy == None):
			INFO_MSG("ApexProxy stopApexProxy self.apexProxy is None")
			return
		INFO_MSG("ApexProxy stopApexProxy")
		self.apexProxy.StopApexProxy()

	def noticeApexProxy( self,cMsgId,nRoleId,pBuf,nBufLen ):
		if(self.apexProxy == None):
			INFO_MSG("ApexProxy noticeApexProxy self.apexProxy is None")
			return
		self.apexProxy.NoticeApexProxy(cMsgId,nRoleId,pBuf,nBufLen)

	def noticeApexProxyMsgG( self,nRoleId,roleName,nameLength ):
		#��G��Ϣ�����Ҫ��role������name����name�ĳ���n
		self.noticeApexProxy('G',nRoleId,roleName,nameLength)

	def noticeApexProxyMsgL( self,nRoleId,roleName,nameLength ):
		#1 �ȷ�L��Ϣ�����Ҫ��role������name����name�ĳ���n
		self.noticeApexProxy('L',nRoleId,roleName,nameLength)

	def noticeApexProxyMsgS( self,nRoleId,roleIPNumber ):
		#��S��Ϣ�����Ҫ��role��ip��ip�ĳ���5��ipҪΪ4�ֽڵ�����
		self.noticeApexProxy('S',nRoleId,str(roleIPNumber),5)

	def noticeApexProxyMsgR( self,nRoleId,nRetNumber ):
		#��R��Ϣ���ѿͻ�����apexClientʱ�ķ���ֵpRet��ת�͸�ApexProxy
		self.noticeApexProxy('R',nRoleId,str(nRetNumber),4)

	def noticeApexProxyMsgT( self,nRoleId,pBuf,nBufLen ):
		#��T��Ϣ���ѿͻ����ռ��������ݣ�ת�͸�ApexProxy
		self.noticeApexProxy('T',nRoleId,pBuf,nBufLen)

	def ApexKillRole( self ):
		self.apexProxy.ApexKillRoleFromBuf( )

	def SendMsgToClient( self ):
		self.apexProxy.SendMsgBuf2Client( )
