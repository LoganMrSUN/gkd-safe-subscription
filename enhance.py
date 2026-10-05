"""Usage: python enhance.py BASE_JSON LIN_JSON5 OUTPUT_JSON; requires json5."""
import json,json5,sys,copy,hashlib,pathlib
# Explicitly reviewed group allowlist. True: dismiss ordinary prompts; False: optional reading helpers.
PICKS={'com.openai.chatgpt':{1:True},'com.deepseek.chat':{2:False},'com.github.android':{2:False},'com.facebook.katana':{1:False},'com.instagram.android':{2:False},'com.reddit.frontpage':{5:False},'com.twitter.android':{4:True,6:False,7:False,11:False},'com.zhihu.android':{17:False,18:False,19:True},'com.tencent.mobileqq':{11:False},'com.moonshot.kimichat':{1:True},'com.adobe.psmobile':{1:True},'com.tencent.qqmusic':{8:True},'com.xingin.xhs':{5:True,6:False,17:False,19:True}}
def build(base,up):
 out=copy.deepcopy(base); added=[]
 for a in out['apps']:a['groups']=[g for g in a['groups'] if not 100000<=g['key']<200000]
 apps={a['id']:a for a in out['apps']}
 for a in up['apps']:
  for src in a.get('groups',[]):
   if src['key'] not in PICKS.get(a['id'],{}):continue
   g=copy.deepcopy(src); enabled=PICKS[a['id']][src['key']]
   # Instagram homepage rule uses coordinate clicking; retain only explicit clickable translation buttons.
   g['rules']=[r for r in g['rules'] if 'position' not in r]
   assert g['rules']
   for r in g['rules']:
    assert r.get('action','click') in ('click','clickCenter','back')
    assert not any(k in r for k in ('position','preKeys','swipeArg','actionCdKey','actionMaximumKey'))
    assert r.get('activityIds') or g.get('activityIds')
    if r.get('action')=='back':assert a['id']=='com.xingin.xhs' and src['key']==5
    r['actionCd']=max(r.get('actionCd',0),3000)
    r['actionMaximum']=1 if enabled else 3
    r['resetMatch']='app'
   g['key']=100000+src['key'];g['enable']=enabled
   g['name']=('界面管理-' if enabled else '阅读辅助-')+src['name'].split('-',1)[-1]
   g['actionMaximum']=1 if enabled else 3;g['actionCd']=3000;g['resetMatch']='app'
   # Prompt dismissals must also work when encountered later in a session.
   g.pop('matchTime',None);g.pop('forcedTime',None)
   if a['id'] not in apps:
    apps[a['id']]={'id':a['id'],'name':a['name'],'groups':[]};out['apps'].append(apps[a['id']])
   assert all(x['key']!=g['key'] for x in apps[a['id']]['groups'])
   apps[a['id']]['groups'].append(g)
   risk='低：仅关闭普通营销/评价提示；界面变化可能误触' if enabled else '低至中：改变阅读界面，可能触发翻译请求、流量消耗或展开过多内容；默认关闭'
   added.append({'app':a['id'],'appName':a['name'],'sourceKey':src['key'],'key':g['key'],'name':g['name'],'defaultEnabled':enabled,'risk':risk,'modifications':'Instagram删除首页坐标规则；统一限次和冷却' if a['id']=='com.instagram.android' else '统一限次和冷却'})
 out['apps']=[a for a in out['apps'] if a['groups']]
 out['categories']=[{'key':0,'name':'开屏广告','enable':True},{'key':100,'name':'界面管理','enable':True},{'key':101,'name':'阅读辅助','enable':False}]
 out['name']='Logan 广告与应用管理保守订阅';out['version']=max(base['version']+1,2026100502)
 assert out['id']==base['id'] and not out['globalGroups']
 assert 'updateUrl' not in out and 'checkUpdateUrl' not in out
 return out,added
if __name__=='__main__':
 b,s,d=map(pathlib.Path,sys.argv[1:4]);base=json.loads(b.read_text());up=json5.loads(s.read_text());out,added=build(base,up)
 d.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 report={'source':'https://github.com/Lin-arm/GKD_subscription','sourceVersion':up['version'],'sourceSHA256':hashlib.sha256(s.read_bytes()).hexdigest(),'version':out['version'],'addedGroups':len(added),'defaultEnabledNew':sum(x['defaultEnabled'] for x in added),'optionalNew':sum(not x['defaultEnabled'] for x in added),'apps':len(out['apps']),'totalGroups':sum(len(a['groups']) for a in out['apps']),'method':'逐组阅读JSON选择器和操作进行静态审查，未实机测试','excluded':'未允许的上游规则全部不导入；支付/银行/安装/权限授权/登录批准/删除/系统设置/隐藏安全警告/重发消息均排除','added':added}
 d.with_name('enhancement-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print({k:v for k,v in report.items() if k not in ('added','excluded')})
