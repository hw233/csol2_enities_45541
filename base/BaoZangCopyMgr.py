# -*- coding: gb18030 -*-
import time
import uuid
import random

import BigWorld
import csstatus
from bwdebug import *

LINE_TIME = 60 * 30 # �Ŷ�ʱ��

class ReqTeamInfos( object ):
	def __init__( self, teamMB, level ):
		self.teamMB = teamMB
		self.level = level
	
	def notifyOpenCopy( self, teamMB ):
		# ƥ��ɹ���֪ͨ����
		self.teamMB.baoZangReqSucceed( teamMB )
	
	def getTeamID( self ):
		return self.teamMB.id

class BaoZangCopyMgr( BigWorld.Base ):
	# Ӣ�����˸���������
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "BaoZangCopyMgr", self._onRegisterManager )
		self.reqList = []
		
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register BaoZangCopyMgr Fail!" )
			self.registerGlobally( "BaoZangCopyMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["BaoZangCopyMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("BaoZangCopyMgr Create Complete!")
	
	def req( self, baseEntity, teamMailBox, level):
		"""
		define method
		"""
		for i in self.reqList:
			if teamMailBox.id == i.getTeamID():
				baseEntity.client.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_HAVE_JOIN,"" )
				return
				
		self.reqList.append( ReqTeamInfos( teamMailBox, level ) )
		teamMailBox.baoZangPVPonReq()
		self.startMatching()
		self.addTimer( LINE_TIME, 0, teamMailBox.id  )
	
	def cancel( self,  tid, isMatch ):
		"""
		define method.
		ȡ���Ŷ�
		"""
		for t in self.reqList:
			if t.teamMB.id == tid:
				self.reqList.remove( t )
				t.teamMB.baoZangPVPonCancel( isMatch )
				break

	def startMatching( self ):
		"""
		��ʼƥ��
		"""
		if len( self.reqList ) < 2:
			return
		
		matchTeam = self.reqList[ 0 ]
		self.__match( matchTeam )
	
	def __match( self, matchTeam ):
		isMatchSucceedOne = False
		for t in self.reqList:
			if matchTeam == t:
				continue
				
			if abs( t.level - matchTeam.level ) <= 3:
				matchTeam.notifyOpenCopy( t.teamMB )
				t.notifyOpenCopy( matchTeam.teamMB )
				self.cancel( t.teamMB.id, True )
				self.cancel( matchTeam.teamMB.id, True )
				isMatchSucceedOne = True
				break
				
		if isMatchSucceedOne:
			self.startMatching()
	
	def onTimer( self, id, userArg ):
		self.cancel( userArg, False )