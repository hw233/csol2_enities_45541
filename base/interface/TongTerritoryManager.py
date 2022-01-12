# -*- coding: gb18030 -*-
#
# $Id: TongCityWarManager.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

import time
import BigWorld
import csdefine
import csstatus
import csconst
import random
from bwdebug import *
from Function import Functor
from ObjectScripts.GameObject import GameObject

class TongTerritoryManager:
	"""
	��ع��������������صĴ����� ��������е���ء�
	���ǵİ��������û�г�Ա��������ENTITY���ᱻ������ ����صĹ������κ��˶�����ȥ�����������
	���Ը���صĴ��ڲ�������ENTITY�Ĵ��ڣ� �����ENTITY����Ҫ֪�����MAILBOX�ģ������ҵ������������ر�����
	���ENTITY�Ѿ���������ֱ��ע������ENTITY���������ɰ��ENTITY������ʱ�����ENTITY����Ҫ��ù����������ע�����,
	���⼴ʹ�Լ����ĸ������������� �����û�г�Ա����Ҳ���ᴴ���� �����ô��ơ�
	"""
	def __init__( self ):
		self.territorys = {}	# �����汣�������а������

	def onManagerInitOver( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		pass
		
	def onTongDismiss( self, tongDBID ):
		"""
		define method.
		ĳ����ᱻ��ɢ�ˣ�׼�����������������
		"""
		# �п��ܰ��մ���û���������������ذ���ֽ�ɢ�ˣ������Ҫ�ж�
		if self.territorys.has_key( tongDBID ):
			territory = self.territorys.pop( tongDBID )
			territory.onTongDismiss()
	
	def findTerritoryByTongDBID( self, tongDBID ):
		"""
		Ѱ��ĳ�������
		"""
		if tongDBID in self.territorys:
			return self.territorys[ tongDBID ]
		return None
		
	def onRegisterTerritory( self, tongDBID, territory ):
		"""
		define method.
		@param tongDBID: ���DBID
		@param territory:��ظ�����basemailbox
		"""
		self.territorys[ tongDBID ] = territory
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onRegisterTerritory( territory )
		
	def onTongEntityRequestTerritory( self, tongEntity, tongDBID ):
		"""
		define method.
		��ᱻ�������������Ҫ��ظ�����mailbox (�������������)
		"""
		if not tongDBID in self.territorys:
			return
		tongEntity.onRegisterTerritory( self.territorys[ tongDBID ] )
		
	def onRequestCreateTongTerritory( self, spaceDomain, tongDBID ):
		"""
		define method.
		spaceDomain ������������� ĳ�����ص���Ϣȥ����һ�������ظ���
		@param spaceDomain: ����������
		@param tongDBID	  : ���������صİ��
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onRequestCreateTongTerritory( spaceDomain )
		else:
			cmd = "select sm_level, sm_jk_level, sm_ssd_level, sm_ck_level, sm_tjp_level, sm_sd_level, sm_yjy_level, sm_shenshouType, sm_shenshouReviveTime from tbl_TongEntity where id = %i;" % tongDBID
			BigWorld.executeRawDatabaseCommand( cmd, Functor( self.onQueryDB_onCreateTongTerritoryCallBack, spaceDomain, tongDBID ) )
	
	def onQueryDB_onCreateTongTerritoryCallBack( self, spaceDomain, tongDBID, result, dummy, error ):
		"""
		ɾ����Ա��Ϣ ���ݿ�ص�
		"""
		if (error):
			ERROR_MSG( error )
			spaceDomain.onCreateTongTerritoryError( tongDBID )
			return

		try:
			ysdt_level = int( result[0][0] )
			jk_level = int( result[0][1] )
			ssd_level = int( result[0][2] )
			ck_level = int( result[0][3] )
			tjp_level = int( result[0][4] )
			sd_level = int( result[0][5] )
			yjy_level = int( result[0][6] )
			shenshouType = int( result[0][7] )
			shenshouReviveTime = int( result[0][8] )
			spaceDomain.onCreateTongTerritory( tongDBID, ysdt_level, jk_level, ssd_level, ck_level, tjp_level, sd_level, yjy_level, shenshouType, shenshouReviveTime )
		except IndexError:
			ERROR_MSG( "onQueryDB_onCreateTongTerritoryCallBack is error!" )
			spaceDomain.onCreateTongTerritoryError( tongDBID )
			
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""	
		pass

#
# $Log: not supported by cvs2svn $
#