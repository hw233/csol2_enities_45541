# -*- coding: gb18030 -*-
#
# $Id: ModelRender.py,v 1.6 2008-08-28 03:53:55 huangyongwei Exp $

"""
implement fitting model render gui

2009/06/12: writen by huangyongwei
"""
from guis import *
import gbref
import Language
from guis.controls.ModelRender import ModelRender
import csdefine
import csconst
import Const
from config.client.msgboxtexts import Datas as mbmsgs
import Define
from gbref import rds

class FittingModelRender( ModelRender ) :

	def __init__( self, mirror ) :
		ModelRender.__init__( self, mirror )
		self.bgTexture = "guis/general/specialshop/fitback.tga"
		self.__itemModelID = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onModelCreated( self, itemModelID, model ) :
		"""
		����ģ�ͻص�
		"""
		if model is None :
			# "����ģ��ʧ�ܣ�"
			showMessage( 0x07a1, "", MB_OK, pyOwner = self )
			self.__itemModelID = 0
		else :
			self.__itemModelID = itemModelID
			effectIDs = rds.itemModel.getMEffects( itemModelID )
			for effectID in effectIDs:
				dictData = rds.spellEffect.getEffectConfigDict( effectID )
				if len( dictData ) == 0: continue
				effect = rds.skillEffect.createEffect( dictData, model, model, Define.TYPE_PARTICLE_PLAYER,  Define.TYPE_PARTICLE_PLAYER )
				effect.start()
		self.setModel( model )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onModelChanged_( self, oldModel ) :
		"""
		ģ�͸ı�ʱ������
		"""
		ModelRender.onModelChanged_( self, oldModel )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, itemModelID, bgCreate = True ) :
		"""
		��������ģ��
		@type			itemModelID : INT32
		@param			itemModelID : ģ�Ͷ�Ӧ����Ʒ ID
		@type			bgCreate	: bool
		@param			bgCreate	: �Ƿ��ں�̨����ģ��
		@return					 	: None
		"""
		if itemModelID == self.__itemModelID :
			return
		if itemModelID is None :
			self.setModel( None )
			self.__itemModelID = 0
			# "���ģ��'%i'�����ڣ�"
			showMessage( mbmsgs[0x07a2] % itemModelID, "", MB_OK, pyOwner = self )
		else :
			if bgCreate :
				rds.itemModel.createModelBG( itemModelID, Functor( self.__onModelCreated, itemModelID ) )
			else :
				model = rds.itemModel.createModel( itemModelID )
				self.__onModelCreated( itemModelID, model )

	# -------------------------------------------------
	def getViewInfos( self ) :
		"""
		��ȡ����ģ����Ϣ
		"""
		player = BigWorld.player()
		profes = player.getClass()
		if profes == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER )
		proName = csconst.g_chs_class[profes]					# ģ�Ͷ�Ӧ��ְҵ����
		pos = self.modelPos
		pitch = self.pitch
		yaw = self.yaw
		modelInfo = self.creatModelInfo_( profes, proName, pos, pitch, yaw )
		return [modelInfo]											# ֻ������ǰְҵ

	def clearModel( self ) :
		"""
		�����ǰ��ʾ��ģ��
		"""
		self.__itemModelID = 0
		self.setModel( None )
