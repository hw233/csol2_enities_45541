# -*- coding: gb18030 -*-
#
# 2008-12-11 15:22 SongPeiFang
#

from FuncTeleport import FuncTeleport
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import random
import re
import Const
import csdefine


class FuncTeleToSunBath( FuncTeleport ):
	"""
	�������չ�ԡ��ͼ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.spaceName = section.readString( "param1" )
		positionsAndDirection = section.readString( "param2" ).split( ';' )	# �漴���꣨һ�飩;����һ����
		if len( positionsAndDirection ) <= 1:
			# ����ָ����鲻��ȷ��һ�������õĸ�ʽ������
			ERROR_MSG( "Config error, bad format for positions infomations!" )
		self.positions = positionsAndDirection[0].split( '|' )
		self.direction = eval( re.sub( "\s*;\s*|\s+", ",", positionsAndDirection[1] ) )	# ����
		self.repLevel = section.readInt( "param3" )										# �ƶ�����ȼ�
		self.radius = section.readFloat( "param4" )										# �ƶ�����λ�ý����漴ƫ�Ƶ�ֵ
		self.repMoney = section.readInt( "param5" )										# �ƶ������Ǯ
	
	def calcPosition( self, hardPoint ):
		"""
		 ���㱻���͵�����λ�ã����λ���ǰ���hardPoint�̶�������뾶5�׵�һ��Բ�η�Χ
		 @param hardPoint: Բ��
		"""
		return FuncTeleport.calcPosition( self, hardPoint )
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������
		"""
		if player.hasMerchantItem():
			player.setGossipText( cschannel_msgs.CAIJI_SKILL_VOICE_3 )
			player.sendGossipComplete( talkEntity.id )
			return

		# ����з�������buff
		if len( player.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# �������Ѿ���������ô��������
			return
			
		positionIndex = random.randint( 0, len( self.positions ) - 1 )
		self.position = eval( re.sub( "\s*;\s*|\s+", ",", self.positions[positionIndex] ) )	# ����
		FuncTeleport.do( self, player, talkEntity )
	
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		"""
		return True

# FuncTeleToSunBath.py