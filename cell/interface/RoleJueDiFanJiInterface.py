# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Const
import ECBExtend
import csdefine
import csstatus
import VehicleHelper

import csconst

# ��ʱ�˳�������λ��
TEMP_FORET_POSITION = ( 98.295, 12.108, 135.196 )
TEMP_FORET_DIRECTION = ( 0, 0, 0.1964 )
TEMP_FORET_SPACE = "fengming"



class RoleJueDiFanJiInterface:
	"""
	���ط����ӿ�
	"""
	def __init__( self ):
		pass

	def initJueDiFanJiButtonState( self, srcEntityID ):
		"""
		Exposed method
		��¼ʱ��ʼ�����ط������ť״̬
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ):
			state = self.queryTemp( "jueDiFanJi_state", 0 )
			repeatedVictoryCount = self.queryTemp( "jueDiFanJi_repeatedVictoryCount", 0 )
			if state == csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP:
				self.client.jueDiVictoryCountChange( repeatedVictoryCount )
			self.client.showJueDiFanJiPanel( state )
		else:
			self.client.showJueDiFanJiPanel( csdefine.JUE_DI_FAN_JI_SHOW_RANK_LIST )
			if self.queryTemp( "jueDiFanJi_state", 0 ):
				self.removeTemp( "jueDiFanJi_state" )
				self.removeTemp( "jueDiFanJi_repeatedVictoryCount" )

	def jueDiFanJiSignUp( self, srcEntityID ):
		"""
		���ط�������
		"""
		if self.id != srcEntityID:
			return
		if self.level < csconst.JUE_DI_FAN_JI_LEVEL_LIMIT:
			return
		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiSignUp( self.base, self.databaseID, self.getName(), self.getLevel(), self.getClass() )

	def jueDiFanJiEnterConfirm( self, srcEntityID ):
		"""
		���ط�������ȷ��
		"""
		if self.id != srcEntityID:
			return
		if not self.transConditionCheck():
			return

		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiEnterConfirm( self.base, self.databaseID )
		
	def noticeAddTimer( self, time ):
		self.jueDiFanJiTimer = self.addTimer( time, 0, ECBExtend.JUE_DI_FAN_JI_CONFIRM )
		
	def onTimer_jueDiFanJiConfirm( self, timerID, cbID ):
		"""
		���ط���ȷ��ʱ�䵽��timer
		"""
		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiReachTimeConfirm( self.databaseID )

	def jueDiFanJiCancelEnter( self, srcEntityID ):
		"""
		���ط����������ȡ������
		"""
		if self.id != srcEntityID:
			return
		self.jueDiFanJiCanCelTimer()
		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiCancelEnter( self.base, self.databaseID )

	def selectRepeatedVictory( self, srcEntityID ):
		"""
		���ѡ����ʤ
		"""
		if self.id != srcEntityID:
			return
		self.gotoForetime()
		self.setTemp( "selectRepeatedVictory", 1)
		BigWorld.globalData[ "JueDiFanJiMgr" ].onSelectRepeatedVictory( self.base, self.databaseID, self.HP, self.getName(), self.getLevel(), self.getClass() )

	def selectLeave( self, srcEntityID ):
		"""
		���ѡ���뿪
		"""
		if self.id != srcEntityID:
			return
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #ˢ���ٶ�
		self.gotoForetime()
		#self.gotoSpace( TEMP_FORET_SPACE, TEMP_FORET_POSITION, TEMP_FORET_DIRECTION )
		BigWorld.globalData[ "JueDiFanJiMgr" ].clearVictoryCountDict( self.databaseID )

	def onRoleReviveCallBack( self, spaceName, position, direction ):
		"""
		����ڸ����������󸴻�
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #ˢ���ٶ�
		self.teleport( None, position, direction )


	def onJueDiFanJiLogin( self, srcEntityID ):
		"""
		Exposed method
		������µ�½
		"""
		if self.id != srcEntityID: return
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) or self.query( "jueDiFanJi_scoreList", None ) != None:
			self.client.onShowJueDiFanJiBox()

	def onReceiveStateInfo( self, state, repeatedVictoryCount ):
		"""
		����״̬��Ϣ
		"""
		if state == csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP:
			self.client.onJueDiSignUp()
		elif state == csdefine.JUE_DI_FAN_JI_HAS_MATCHED:
			self.client.onJueDiMatchSuccess()
		elif state == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
			self.client.onJueDiConfirm()
		self.setTemp( "jueDiFanJi_state", state )
		self.setTemp( "jueDiFanJi_repeatedVictoryCount", repeatedVictoryCount )

	def jueDiFanJiCanCelTimer( self ):
		"""
		ȡ�����ط����Timer
		"""
		self.cancel( self.jueDiFanJiTimer )

	def receiveBulletin( self, scoreList ):
		"""
		���վ��ط����ǰ20���İ�
		"""
		self.set( "jueDiFanJi_scoreList", scoreList )
		self.client.receiveBulletin( scoreList )

	def showJueDiFanJiRankList( self, srcEntityID ):
		"""
		Exposed method
		��ʾ��
		"""
		if self.id != srcEntityID: return
		if self.query( "jueDiFanJi_scoreList", None ) != None:
			scoreList = self.query( "jueDiFanJi_scoreList", None )
			self.client.receiveBulletin( scoreList )
		else:
			self.statusMessage( csstatus.JUE_DI_SHOW_RANK_LIST_NOT_JOIN )

	def removeBulletin( self ):
		"""
		�Ƴ����������
		"""
		self.remove( "jueDiFanJi_scoreList" )
		