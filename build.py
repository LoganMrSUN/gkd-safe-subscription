"""Build conservative splash-only subscription. Requires json5; never executes upstream."""
import json,json5,re,hashlib,pathlib,collections
root=pathlib.Path(__file__).parent
source=root.parent/'upstream.json5'
p=json5.loads(source.read_text())
removed=[]; apps=[]
sensitive=re.compile(r'银行|证券|支付|钱包|金融|贷款|借贷|理财|交易|基金|保险|信用|安装|权限|文件管理|系统设置|认证|密码|验证码|登录|登陆|删除|卸载|授权|允许|确认|同意|继续|风险|美国居民|考试')
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values(): yield from walk(v)
 elif isinstance(x,list):
  for v in x: yield from walk(v)
counts=collections.Counter()
for app in p.get('apps',[]):
 gs=[]
 for g in app.get('groups',[]):
  reason=None
  raw=json.dumps(g,ensure_ascii=False)
  if not g.get('name','').startswith('开屏广告'): reason='非开屏广告'
  elif sensitive.search(app.get('name','')+' '+app['id']): reason='敏感应用'
  elif app['id'].startswith(('com.android.','com.google.android.permission','com.miui.security','com.huawei.system','com.coloros.safecenter')): reason='系统组件'
  elif sensitive.search(raw): reason='涉及敏感词，保守排除'
  elif any(d.get('action','click') not in ('click',) or 'position' in d for d in walk(g)): reason='非普通点击或坐标点击'
  elif any(k in d for d in walk(g) for k in ('preKeys','actionCdKey','actionMaximumKey')): reason='跨规则依赖'
  else:
   rules=g.get('rules',[]); rules=[rules] if isinstance(rules,dict) else rules
   if not rules or any(not isinstance(r,dict) or not re.search(r'跳过|跳過|(?i:skip)',json.dumps(r.get('matches',''),ensure_ascii=False)) for r in rules): reason='未明确匹配跳过文字'
  if reason:
   removed.append({'app':app['id'],'name':app.get('name'),'key':g.get('key'),'group':g.get('name'),'reason':reason}); counts[reason]+=1
  else:
   g['enable']=True; g['matchTime']=min(g.get('matchTime',10000),10000); g['actionMaximum']=1; g['resetMatch']='app'
   for r in rules:
    if 'matchTime' in r:r['matchTime']=min(r['matchTime'],10000)
    if 'actionMaximum' in r:r['actionMaximum']=1
   gs.append(g)
 if gs: apps.append({'id':app['id'],'name':app.get('name',app['id']),'groups':gs})
out={'id':159916922,'name':'Logan 开屏广告保守订阅','version':2026100501,'author':'LoganMrSUN；规则来源见 README','categories':[{'key':0,'name':'开屏广告','enable':True}],'globalGroups':[],'apps':apps}
(root/'gkd.json5').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
report={'upstreamSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'originalGroups':len(removed)+sum(len(a['groups']) for a in apps),'retainedGroups':sum(len(a['groups']) for a in apps),'retainedApps':len(apps),'removedByReason':dict(counts),'removed':removed}
(root/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert not out.get('updateUrl') and not out.get('checkUpdateUrl') and not out['globalGroups']
assert all(g['name'].startswith('开屏广告') for a in apps for g in a['groups'])
print({k:v for k,v in report.items() if k!='removed'})
