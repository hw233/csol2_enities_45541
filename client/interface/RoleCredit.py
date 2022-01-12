# -*- coding: gb18030 -*-
#
# $Id: RoleCredit.py,v 1.5 2008-08-30 10:08:47 wangshufeng Exp $


import BigWorld
from bwdebug import *
import event.EventCenter as ECenter
from FactionMgr import factionMgr
import csdefine
import csconst
import csstatus
import Language
import Math
import config.client.labels.RoleCredit as lbDatas
from config.Title import Datas as g_TitleData
from Color import cscolors

prestigeStrDict = { csdefine.PRESTIGE_ENEMY : lbDatas.PRESTIGE_ENEMY,
					csdefine.PRESTIGE_STRANGE:lbDatas.PRESTIGE_STRANGE,
					csdefine.PRESTIGE_NEUTRAL:lbDatas.PRESTIGE_NEUTRAL,
					csdefine.PRESTIGE_FRIENDLY:lbDatas.PRESTIGE_FRIENDLY,
					csdefine.PRESTIGE_RESPECT:lbDatas.PRESTIGE_RESPECT,
					csdefine.PRESTIGE_ADMIRE:lbDatas.PRESTIGE_ADMIRE,
					csdefine.PRESTIGE_ADORE:lbDatas.PRESTIGE_ADORE,
					}

class RoleCredit:
	"""
	��ɫ���������ƺš�����interface
	"""
	def __init__( self ):
		"""
		"""
		self.prestige = {}		# ��������

	def prestigeUpdate( self, factionID, value ):
		"""
		Define method.
		�����ı䣬�ṩ��server��֪ͨ����

		@param factionID : ����factionID
		@type factionID : UINT8
		@param value : ���ӻ���ٵ�����ֵ
		@type value : INT32
		"""
		if not self.prestige.has_key( factionID ):
			ERROR_MSG( "Key error on faction ID:%s, maybe not initiated yet." % factionID )
			return
		oldLevel = self.getPretigeLevel( factionID )
		self.prestige[ factionID ] += value
		if self.prestige[ factionID ] > csconst.PRESTIGE_UPLIMIT:
			self.prestige[ factionID ] = csconst.PRESTIGE_UPLIMIT
		if self.prestige[ factionID ] < csconst.PRESTIGE_LOWERLIMIT:
			self.prestige[ factionID ] = csconst.PRESTIGE_LOWERLIMIT
		newLevel = self.getPretigeLevel( factionID )
		if value != 0:
			if value >= 1:
				self.statusMessage( csstatus.PRESTIGE_VALUE_INCREASE, factionMgr.getName( factionID ), value )
			else:
				self.statusMessage( csstatus.PRESTIGE_VALUE_REDUCE, factionMgr.getName( factionID ), abs( value ) )
		powerName = factionMgr.getName( factionID )
		if newLevel != oldLevel:
			self.statusMessage( csstatus.PRESTIGE_VALUE_UPDATE, powerName, prestigeStrDict[newLevel] )
		ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_UPDATE", factionID ) # ��������


	def receivePrestige( self, factionID, value ):
		"""
		Define method.
		��ҵ�¼�������������ݵĺ���

		@param factionID : ����factionID
		@type factionID : UINT8
		@param value : ����ֵ
		@type value : INT32
		"""
		self.prestige[ factionID ] = value
		ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_UPDATE", factionID ) # ��������


	def turnOnPrestige( self, factionID, value ):
		"""
		Define method.
		�״�������������������
		@param factionID : ����factionID
		@type factionID : UINT8
		@param value : ���ӵ�����ֵ
		@type value : INT32
		"""
		self.prestige[ factionID ] = value
		if value != 0:
			if value >= 1:
				self.statusMessage( csstatus.PRESTIGE_VALUE_INCREASE, factionMgr.getName( factionID ), value )
			else:
				self.statusMessage( csstatus.PRESTIGE_VALUE_REDUCE, factionMgr.getName( factionID ), abs( value ) )
		ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_ADD", factionID ) #����ĳ������

	def getPrestige( self, factionID ):
		"""
		��ö�ӦfactionID����������

		@param factionID : ����factionID
		@type factionID : UINT32
		"""
		try:
			return self.prestige[ factionID ]
		except KeyError:
			ERROR_MSG( "Key error on faction ID %s:" % factionID )
			return None

	def getPretigeLevel( self, factionID ):
		"""
		��ö�ӦfactionID�����������ȼ�

		PRESTIGE_ENEMY				=			1	# ���
		PRESTIGE_STRANGE			=			2	# �䵭
		PRESTIGE_NEUTRAL			=			3	# ����
		PRESTIGE_FRIENDLY			=			4	# ����
		PRESTIGE_RESPECT			=			5	# ����
		PRESTIGE_ADMIRE				=			6	# �羴
		PRESTIGE_ADORE				=			7	# ���
		"""
		return self.getPrestige( factionID ) < -3000 and csdefine.PRESTIGE_ENEMY \
			or self.getPrestige( factionID ) < 0     and csdefine.PRESTIGE_STRANGE \
			or self.getPrestige( factionID ) < 3000  and csdefine.PRESTIGE_NEUTRAL \
			or self.getPrestige( factionID ) < 9000  and csdefine.PRESTIGE_FRIENDLY \
			or self.getPrestige( factionID ) < 21000 and csdefine.PRESTIGE_RESPECT \
			or self.getPrestige( factionID ) < 42000 and csdefine.PRESTIGE_ADMIRE \
			or csdefine.PRESTIGE_ADORE

	def getPretigeDes( self, value ):
		"""
		��ö�ӦfactionID�����������ȼ�

		PRESTIGE_ENEMY				=			1	# ���
		PRESTIGE_STRANGE			=			2	# �䵭
		PRESTIGE_NEUTRAL			=			3	# ����
		PRESTIGE_FRIENDLY			=			4	# ����
		PRESTIGE_RESPECT			=			5	# ����
		PRESTIGE_ADMIRE				=			6	# �羴
		PRESTIGE_ADORE				=			7	# ���
		"""
		return value < -3000 and prestigeStrDict[ csdefine.PRESTIGE_ENEMY ] \
			or value < 0     and prestigeStrDict[ csdefine.PRESTIGE_STRANGE ] \
			or value < 3000  and prestigeStrDict[ csdefine.PRESTIGE_NEUTRAL ] \
			or value < 9000  and prestigeStrDict[ csdefine.PRESTIGE_FRIENDLY ]\
			or value < 21000 and prestigeStrDict[ csdefine.PRESTIGE_RESPECT ]\
			or value < 42000 and prestigeStrDict[ csdefine.PRESTIGE_ADMIRE ]\
			or prestigeStrDict[ csdefine.PRESTIGE_ADORE ]

	def onTitleAdded( self, titleID ) :
		"""
		@type 		titleID : UINT8

		�¼ӳƺŵ�֪ͨ
		"""
		titleName = self.getAddTitle( titleID )
		if titleID not in [ csdefine.TITLE_ALLY_ID, csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID, csdefine.TITLE_TEACH_PRENTICE_ID ]:
			self.statusMessage( csstatus.TITLE_ADDED, titleName )
		ECenter.fireEvent( "EVT_ON_ROLE_TITLE_ADD", titleID, titleName )

	def onTitleRemoved( self, titleID ):
		"""
		@type 		titleID : UINT8

		�Ƴ��ƺŵ�֪ͨ
		"""
		title = self.getAddTitle( titleID )
		if titleID == csdefine.TITLE_COUPLE_MALE_ID or titleID == csdefine.TITLE_COUPLE_FEMALE_ID:
			titleName = lbDatas.TITLE_COUPLE
		elif titleID == csdefine.TITLE_TEACH_PRENTICE_ID:
			titleName = lbDatas.TITLE_PRENTICE
		elif titleID == csdefine.TITLE_ALLY_ID:
			titleName = lbDatas.TITLE_ALLY
		else:
			titleName = title
		self.statusMessage( csstatus.TITLE_LOSED, titleName )
		ECenter.fireEvent( "EVT_ON_ROLE_TITLE_REMOVE", titleID )

	def getAddTitle( self, titleID ):
		"""
		@type 		titleID: INT32
		"""
		try:
			return g_TitleData[ titleID ]["name"]
		except KeyError, err:
			DEBUG_MSG( "%s--%s", KeyError, err )
			return ""

	def getTitleColor( self, titleID ):
		"""
		@type		titleID: INT32
		"""
		try:
			color = g_TitleData[ titleID ][ "color" ]
			return  cscolors[ color ]
		except KeyError, err:
			DEBUG_MSG( "%s--%s", KeyError, err )
			return (51.0, 204.0, 240.0, 255.0)	#����Ĭ����ɫֵ

	def updateTitlesDartRob( self, factionID ):
		"""
		Define method.
		���¿ͻ��˳ƺŵ���ʾ
		"""
		if self.isRobbing( self ):
			# ����ǽ��ڣ�ÿ���ƺź��涼��ʾ����·����������������ѡ���ޡ��ƺţ���ֱ����ʾ����·����
			pass
		elif self.isDarting( self ):
			# ������ڣ���ÿ���ƺź�����ʾ����¡�š��򡰲�ƽ�š�
			if factionID == 37:
				# ��ʾ����¡�š�
				pass
			else:
				# ��ʾ����ƽ�š�
				pass

	def onPrestigeChange( self ):
		"""
		Define method
		�����ı��ڿͻ��˵Ĵ���
		"""
		self.refurbishAroundQuestStatus()
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/07/19 01:56:53  wangshufeng
# ��ӳƺ�ϵͳ
#
# Revision 1.3  2008/07/17 03:16:45  fangpengjun
# ��������25�����ӵ�30��
#
# Revision 1.2  2008/07/16 10:16:27  fangpengjun
# ��ӽ���������Ϣ
#
# Revision 1.1  2008/07/14 04:13:49  wangshufeng
# add new interface��RoleCredit
#
#
