# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
import csstatus
import event.EventCenter as ECenter

class RoleJueDiFanJiInterface:
	"""
	���ط����ӿ�
	"""
	def __init__( self ):
		pass

	def onCacheCompleted( self ):
		"""
		"""
		self.cell.onJueDiFanJiLogin()

	def jueDiFanJiSignUp( self ):
		"""
		���ط�������
		"""
		self.cell.jueDiFanJiSignUp()

	def jueDiFanJiEnterConfirm( self ):
		"""
		���ط�������ȷ��
		"""
		self.cell.jueDiFanJiEnterConfirm()

	def jueDiFanJiCancelEnter( self ):
		"""
		���ط����������ȡ������
		"""
		self.cell.jueDiFanJiCancelEnter()

	def selectLeaveOrNot( self, status ):
		"""
		���ط�����ҿͻ��˵����Ի��������ѡ���Ƿ���ʤ
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_RESULT", status )

	def jueDiFanJiStart( self ):
		"""
		���ط������ʼ
		"""
		if self.level < csconst.JUE_DI_FAN_JI_LEVEL_LIMIT:
			return
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_BOX" )

	def jueDiFanJiEnd( self ):
		"""
		���ط����������رհ�
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_BOX" )
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_RANK_LIST" )

	def selectRepeatedVictory( self ):
		"""
		���ط������ѡ����ʤ
		"""
		self.cell.selectRepeatedVictory()

	def selectLeave( self ):
		"""
		���ѡ���뿪
		"""
		#������ʾ�����ȷ���Ƿ��뿪���뿪���������ʤ
		self.cell.selectLeave()
		
	def receiveBulletin( self, scoreList ):
		"""
		���վ��ط����ǰ20���İ�
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_RANK", scoreList )

	def initJueDiFanJiButtonState( self ):
		"""
		��ʼ������ͼ��״̬
		"""
		self.cell.initJueDiFanJiButtonState()

	def leaveJueDiFanJiSpace( self ):
		"""
		����뿪���ط��������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_BOX" )
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_RESULT" )

	def jueDiVictoryCountChange( self, repeatedVictoryCount ):
		"""
		define method
		��ʤ�����ı�
		"""
		ECenter.fireEvent( "EVT_ON_VICTORY_COUNT_CHANGE", repeatedVictoryCount )

	def showJueDiFanJiPanel( self, state ):
		"""
		define method
		����״̬��Ϣ��ʾ���
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_PANEL", state )
		if state == csdefine.JUE_DI_FAN_JI_HAS_ENTERED:	# �Ѿ����븱��
			ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_BOX" )

	def onJueDiSignUp( self ):
		"""
		define method
		�����ɹ�
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_SIGN_UP" )

	def onJueDiMatchSuccess( self ):
		"""
		define method
		ƥ��ɹ�
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_MATCH_SUCCESS" )

	def onJueDiConfirm( self ):
		"""
		define method
		ȷ�Ͻ���
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_CONFIRM" )

	def onJueDiEnter( self ):
		"""
		define method
		�ɹ�����
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_BOX" )

	def onShowJueDiFanJiBox( self ):
		"""
		define method
		������µ�½
		"""
		if self.level < csconst.JUE_DI_FAN_JI_LEVEL_LIMIT:
			return
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_BOX" )

	def showJueDiFanJiRankList( self ):
		"""
		��ʾ���а�
		"""
		self.cell.showJueDiFanJiRankList()

	def receiveScoreInfo( self, score ):
		"""
		���ط����������ʤ����
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_RANK_SCORE", score )

	def onJueDiFanJiCountDown( self, time ):
		"""
		���ط����PK����ʱ�����
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_COUNT_DOWN", time )
		