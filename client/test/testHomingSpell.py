# -*- coding: gb18030 -*-
#用于检测角色连击技能中配置的施法动作使用的是带真实位移的动作。

from config.client.SkillEffect.SpellEffect import Datas
from config.skill.Skill.SkillDataMgr import Datas as SkillData
import skills 
import csv
import ResMgr
import os

HomingSkillIDs = {}
ImpactingActions = []
LeafKey = ['isImpacting']
ERRORSKILLIDANDACTIONS = {}


def getType(path):
	if "." in path:
		type_ = os.path.splitext(path)[1]
		if len(type_) > 1:
			return type_[1:].lower()
	return None

def dealdir(path, callback = None, key = None):
	#处理F:/csol/datas/***, F:/csol/res/***文件夹
	folder = path
	if "/datas/" in path:
		folder = path.split("datas/")[1]
	elif "/res/" in path:
		folder = path.split("res/")[1]
	if path.endswith("datas"):
		folder = "../datas"
	for i in os.listdir(folder):
		newpath = path + "/" + i
		if os.path.isfile(newpath):  #文件
			if i[0] == "."  or i.startswith("#") or "thumbnail" in i or i.endswith( ".original" ) or "~" in i:  #pass .svn not see file
				continue
			filename = os.path.basename(newpath)
			if callback:
				callback(newpath, key)
		elif os.path.isdir(newpath):  #目录
			print newpath
			dealdir(newpath, callback, key)

def callback(path, LeafKey = []):
	if getType(path) != "model":
		return 
	relativepath = path
	if "/datas/" in path:
		relativepath = path.split("/datas/")[1]
	elif "/res/" in path:
		#print "111",relativepath
		relativepath = path.split("/res/")[1]
	sect = ResMgr.openSection(relativepath)
	if not sect:
		print "relativepath",relativepath
		return 
		
	checkKey(path, sect, LeafKey) 

		 
			
def checkKey(path, value, LeafKey = [] ):
	if len(value.items()) > 0:
		for k, v in value.items():
			if k in LeafKey and v.asString:
				if value["name"].asString not in ImpactingActions:
					ImpactingActions.append(value["name"].asString)	
			else:
				checkKey(path, v, LeafKey)

def test(path):
	dealdir(path, callback, LeafKey)
	tmp = {}
	for key, value in Datas.items():
		action = ""
		if value.has_key("spell_action_cast"):
			action = value["spell_action_cast"]
		if len(str(key)) == 6: key = key * 1000 + 1
		if SkillData.has_key(key):
			try:
				try:
					if skills.getSkill(key):
						if skills.getSkill(key).isHomingSkill():
							if action in ImpactingActions:
								addKV( HomingSkillIDs, key, action )
							elif action == '':
								continue
							else:
								addKV(tmp, key, action)
								print "Error skill[%d] config, spell_action_cast[%s] is not real-life movements "%(key, action)
				except:
					print "skillConfig has not key %d"%key 
			except KeyError:
				print "skillConfig has not key %d"%key 
	for key,value in tmp.items():
		addKV(ERRORSKILLIDANDACTIONS, key, value[0][0][0])


        

def addKV(d, key, value):
	if type(d) is dict:
		if key not in d.keys():
			d.update({key:[value,]})
		else:
			if value not in d[key]:
				d[key].append(value)

def writecsv(d, filename):
	#d = {key:[value,]}
	if not d:
		return
	f = open(filename, "wb")
	w = csv.writer(f)
	#w.writerow([filename.split(".")[0],])
	if type(d) == dict:
		for key, value in sorted(d.items(), key = lambda d:d[0]):
			tmp = []
			tmp.append(key)
			if len(value) > 1:
				tmp.extend(value)
			if len(value) ==1:
				tmp.append(value[0])
			w.writerow(tmp)
	elif type(d) == list:
		for item in d:
			w.writerow([item,])
	f.close()
            
        
        
        
