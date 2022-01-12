# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
from SpaceCopyMaps import SpaceCopyMaps
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
import csconst
import Const

GUI_YING_SHI_NUM = [3, 3, 3]

class SpaceCopyWuYaoQianShao( SpaceCopyMaps ):
	"""
	����ǰ�ڸ���
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopyMaps.__init__( self )
		self.isNotRevive = False		# ����Ƿ񸱱��й��ﲻ�ٳ���

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyMaps.onEnterCommon( self, baseMailbox, params )
		
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			skills = {}
			if self.className in player.mapSkills:
				skills = player.mapSkills[self.className]
			player.client.showPGControlPanel( skills )
			INFO_MSG( "%s enter copy wu yao qian shao." % player.getName() )
		else :
			INFO_MSG( "Something enter copy wu yao qian shao." )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyMaps.onLeaveCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.resetAccumPoint()							# ����뿪����������ֵ��0
			player.removeTemp( "callPGDict" )							# ���ٻ��б����
			player.removeTemp( "pg_formation" )
			player.client.closePGControlPanel()	
			player.removeTemp( "ROLE_CALL_PGNAGUAL_LIMIT" )
			INFO_MSG( "%s leave copy wu yao qian shao." % player.getName() )
		else :
			INFO_MSG( "Something leave copy wu yao qian shao." )

	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
		]
		"""
		# ��ʾʣ��С�֣����ɣ�ʣ��BOSS��ʣ��ʱ�䡣 
		return [ 0, 1, 3, 15, 16 ]

	def checkSpaceIsFull( self ):
		"""
		���ռ��Ƿ���Ա
		"""
		if self.getPlayerNumber() >= csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ self.getScript().difficulty ]:
			return True
			
		return False