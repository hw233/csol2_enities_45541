# -*- coding:gb18030 -*-

from SpaceMultiLine import SpaceMultiLine
from bwdebug import *
import Const


class SpaceCopyFishingJoy( SpaceMultiLine ):
	def __init__( self ):
		SpaceMultiLine.__init__( self )
	
	def onEnter( self, selfEntity, baseMailbox, params ):
		SpaceMultiLine.onEnter( self, selfEntity, baseMailbox, params )
		BigWorld.globalData["FishingJoyMgr"].enterRoom( params["playerName"], baseMailbox, selfEntity.id )
		
	def onLeave( self, selfEntity, baseMailbox, params ):
		SpaceMultiLine.onLeave( self, selfEntity, baseMailbox, params )
		BigWorld.globalData["FishingJoyMgr"].leaveRoom( baseMailbox.id )
		
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		pickDict = SpaceMultiLine.packedSpaceDataOnEnter( self, entity )
		pickDict[ "playerName" ] = entity.getName()
		return pickDict