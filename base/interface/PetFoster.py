# -*- coding: gb18030 -*-
#
# $Id: PetFoster.py,v 1.19 2008-08-05 03:09:56 yangkai Exp $

"""
this module implements pet cage interface.

2007/11/07: writen by huangyongwei
"""

import time
import BigWorld
import csdefine
import csconst
import csstatus
import Const
from bwdebug import *
from PetFormulas import formulas
from Function import Functor
from ObjectScripts.GameObjectFactory import g_objFactory
from PetEpitome import queryFosterPets

class PetFoster :
	def __init__( self ) :
		pass

	def onGetCell( self ):
		"""
		"""
		BigWorld.globalData["PetProcreationMgr"].onPlayerGetCell( self.databaseID, self )

	def pft_changePet( self, targetBase, petDBID ):
		"""
		Define method.
		�ı������ڷ�ֳ�ĳ���ѳ������ݷ����Է��ͻ���
		"""
		targetBase.client.pft_dstPetChanged( self.pcg_getPetEpitome( petDBID ) )

	def pft_procreatePet( self, dstDatabaseID, petDBID, endTime ):
		"""
		Define method.
		�������ϣ���ʼ��ֳ����Ĵ���

		@param petDBID : ���뷱ֳ�ĳ���dbid
		@type petDBID : DATABASE_ID
		"""
		# ��Ӫ�����������ﷱֳ�����־ by ����
		pe = self.pcg_getPetEpitome( petDBID )
		ppm = BigWorld.globalData["PetProcreationMgr"]
		name = pe.getAttr("name")
		if name == "":
			name = pe.getAttr("uname")
		name = "%s(%s)"%("name", name )
		isBinded = "%s(%s)"%("isBinded", pe.getAttr("isBinded"))
		# ���ڳ�������¼�������޸ľ����������
		nimbus = "%s(%s)"%("nimbus", pe.getAttr("nimbus"))
		species = "%s(%s)"%("species", pe.getAttr("species"))
		dbid = "%s(%s)"%("dbid", petDBID)
		className = "%s(%s)"%( "className", pe.getAttr("className") )
		petDataStr = "%s %s %s %s %s %s"%( name, isBinded, nimbus, species, dbid, className )
		ppm.procreatePetRecord( petDBID, petDataStr )
		# ��ʼ��ֳ����Ĵ���
		self.pcg_removePet_( petDBID, csdefine.DELETEPET_PROCREATEPET )
		ppm.procreatePet( self.databaseID, self.getName(), dstDatabaseID, petDBID, endTime )

	def pft_remind( self, dstPlayerDBID ):
		"""
		Exposed method.
		���ﷱֳ��֪ͨ��ʱ���ڿͻ��ˣ��ͻ����յ���ֳ��Ϣ��������ȷ����ǰ�Ƿ��Ѿ���ֳ��ϣ�Ȼ���������������Ӧ����

		@param dstPlayerDBID : ��ֳ�����dbid
		@type dstPlayerDBID : DATABASE_ID
		"""
		BigWorld.globalData["PetProcreationMgr"].updateProcreateState( self.databaseID, dstPlayerDBID, self )

	def pft_takePet( self, myPetDBID, dstPetDBID ):
		"""
		Define method.
		��ֳ�ɹ�����ó���

		@param myPetDBID : �������ڷ�ֳ�ĳ���dbid
		@type myPetDBID : DATABASE_ID
		@param dstPlayerDBID : �Է����ڷ�ֳ�ĳ���dbid
		@type dstPlayerDBID : DATABASE_ID
		"""
		def onUpdateParent( epitome, attrs, res ):
			if res < 0:
				ERROR_MSG( "player( %s ) reduce parents( %i )' life fail when procreated!" % ( self.getName(), epitome.databaseID ) )
			else:
				INFO_MSG( "update life of the pet %i success!" % epitome.databaseID )

		def updateParents( epitome ) :
			life = max( 0, epitome.getAttr( "life" ) - formulas.getProcreateLifeDecreasement() )
			attrs = { "life" : life, "procreated" : csdefine.PET_PROCREATE_STATUS_PROCREATED }
			epitome.updateByDict( attrs, self, Functor( onUpdateParent, epitome, attrs ) )

		def onGetChild( myOwnPetDBID, epitomes, childEpitome ):
			if childEpitome is None :
				ERROR_MSG( "save child pet fail!" )
			else :
				myPetEpitome = epitomes[0]
				if myPetEpitome.databaseID != myOwnPetDBID:
					myPetEpitome = epitomes[1]
				self.pcg_addPet_( myPetEpitome, csdefine.ADDPET_FOSTER )
				self.pcg_addPet_( childEpitome, csdefine.ADDPET_FOSTER )
				self.statusMessage( csstatus.PET_PROCREATE_GET_SUCCESS, childEpitome.getDisplayName() )
				updateParents( myPetEpitome )

				# LOG ��Ϣ 17:50 2008-7-21 yk
				species = childEpitome.getAttr("species")
				LOG_MSG( "databaseID(%i), playerName(%s), playerClass(%i), playerLevel(%i), mapMonster(%s), petLevel(%i), petName(%s), hierarchy(%i), ptype(%i), ability(%i)"
					%( self.databaseID, self.getName(), self.getClass(), self.level, childEpitome.getAttr("mapMonster"), childEpitome.getAttr("level"), childEpitome.getAttr("uname"),\
						species & csdefine.PET_HIERARCHY_MASK, species & csdefine.PET_TYPE_MASK, childEpitome.getAttr("ability") ) )

		def onTakePet( success, epitomes ):
			if not success:
				ERROR_MSG( "take procreated pet fail!" )
				self.statusMessage( csstatus.PET_PROCREATE_GET_FAIL_UNKNOW )
			else :
				epitomes = epitomes.values()
				className = epitomes[0].getAttr( "className" )
				child = g_objFactory.getObject( className )
				father, mother = epitomes
				if mother.getAttr( "gender" ) == csdefine.GENDER_MALE :
					father, mother = mother, father
				child.procreatePet( self.databaseID, father, mother, Functor( onGetChild, myPetDBID, epitomes ) )
		queryFosterPets( [myPetDBID, dstPetDBID], onTakePet )
