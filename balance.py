"""python balance.py BASE.json UPSTREAM.json5 OUTPUT.json5. Static screening, not device verification."""
import json,json5,sys,pathlib,copy,re,collections,hashlib
ADS=('开屏广告','全屏广告','局部广告','分段广告'); PROMPTS=('评价提示','通知提示')
DANGER=re.compile(r'同意|允许|确认|确定|领取|购买|立即体验|发送|分享|授权|权限|安装|卸载|删除|清理|确认登录|批准|密码|验证码|支付|付款|转账|风险|安全警告|隐私政策|用户协议|实名认证|生物识别|美国居民|考试|自动发送|自动重试发送|青少年')
SENSITIVE=re.compile(r'银行|证券|钱包|支付|金融|贷款|借贷|理财|交易|基金|保险|信用|安装器|系统|文件选择器|权限控制|密码|Authenticator|远程',re.I)
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def build(base,up):
 out=copy.deepcopy(base);apps={a['id']:a for a in out['apps']};audit=[]
 for a in up['apps']:
  for src in a.get('groups',[]):
   prefix=src['name'].split('-')[0];reason=None
   rules=src.get('rules',[]);rules=[rules] if isinstance(rules,dict) else rules
   nodes=list(walk(src));behavior=json.dumps({k:v for k,v in src.items() if k not in ('snapshotUrls','exampleUrls','excludeSnapshotUrls')},ensure_ascii=False)
   if prefix not in ADS+PROMPTS:reason='非广告/普通提示分类，除已审查21组之外不导入'
   elif SENSITIVE.search(a.get('name','')) or a['id']=='android' or a['id'].startswith(('com.miui.security','com.google.android.permission','com.android.packageinstaller','com.google.android.documentsui')):reason='敏感应用/系统组件'
   elif DANGER.search(behavior):reason='包含敏感操作或安全提示线索'
   elif not rules or any(not isinstance(r,dict) for r in rules):reason='不支持的规则形式'
   elif any(k in n for n in nodes for k in ('actionCdKey','actionMaximumKey','scopeKeys')):reason='跨组引用尚未验证'
   elif any(n.get('action','click') not in ('click','clickCenter','back','swipe') for n in nodes):reason='长按或未知动作'
   elif any(not(r.get('matches') or r.get('anyMatches')) for r in rules):reason='缺少选择器'
   if not reason:
    keys={r['key'] for r in rules if 'key' in r}
    for r in rules:
     pre=r.get('preKeys',[]);pre=pre if isinstance(pre,list) else [pre]
     if any(k not in keys for k in pre):reason='规则链引用缺失'
   if reason:
    audit.append({'app':a['id'],'key':src['key'],'name':src['name'],'decision':'excluded','reason':reason});continue
   existing=apps.get(a['id'],{}).get('groups',[])
   # Keep existing group identities; don't duplicate previously deployed splash rules.
   if any(g['name']==src['name'] for g in existing):continue
   g=copy.deepcopy(src);g['key']=300000+src['key']
   selector=json.dumps([r.get('matches',r.get('anyMatches')) for r in rules],ensure_ascii=False)
   strong=all(re.search(r'跳过|跳過|(?i:skip|splash_skip|skip_btn|skip_view)',json.dumps(r.get('matches',r.get('anyMatches')),ensure_ascii=False)) for r in rules)
   plain=not any('position' in n or 'swipeArg' in n or n.get('action','click') not in ('click','clickCenter') or 'preKeys' in n for n in nodes)
   enabled=bool(prefix=='开屏广告' and strong and plain and src.get('enable',True))
   # Everything beyond narrowly identified splash skipping is optional.
   g['enable']=enabled
   if enabled:
    g['matchTime']=min(g.get('matchTime',10000),10000);g['actionMaximum']=2;g['resetMatch']='app'
    for r in g['rules']:
     if 'matchTime' in r:r['matchTime']=min(r['matchTime'],10000)
     r['actionMaximum']=min(r.get('actionMaximum',2),2);r['resetMatch']='app'
   if prefix=='开屏广告' and not enabled:g['name']='可选开屏广告-'+src['name'].split('-',1)[-1]
   audit.append({'app':a['id'],'key':g['key'],'sourceKey':src['key'],'name':g['name'],'decision':'enabled' if enabled else 'optional','reason':'明确跳过文字/控件且普通点击' if enabled else '扩展覆盖；需逐组开启，未实机验证'})
   if a['id'] not in apps:
    apps[a['id']]={'id':a['id'],'name':a['name'],'groups':[]};out['apps'].append(apps[a['id']])
   apps[a['id']]['groups'].append(g)
 out['categories']=[{'key':0,'name':'开屏广告','enable':True}]+[{'key':i,'name':n,'enable':False} for i,n in enumerate(('全屏广告','局部广告','分段广告','评价提示','通知提示','可选开屏广告'),1)]+[{'key':100,'name':'界面管理','enable':True},{'key':101,'name':'阅读辅助','enable':False}]
 out['version']=base['version']+1;out['name']='Logan 广告与应用管理平衡订阅'
 assert out['id']==base['id'] and not out['globalGroups'] and not out.get('updateUrl') and not out.get('checkUpdateUrl')
 for a in out['apps']:assert len({g['key'] for g in a['groups']})==len(a['groups'])
 return out,audit
if __name__=='__main__':
 b,s,d=map(pathlib.Path,sys.argv[1:4]);base=json.loads(b.read_text());up=json5.loads(s.read_text());out,audit=build(base,up)
 d.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 report={'version':out['version'],'sourceVersion':up['version'],'sourceSHA256':hashlib.sha256(s.read_bytes()).hexdigest(),'source':'https://github.com/Lin-arm/GKD_subscription','apps':len(out['apps']),'groups':sum(len(a['groups']) for a in out['apps']),'newDecisions':dict(collections.Counter(x['decision'] for x in audit)),'retainedPreviousGroups':sum(len(a['groups']) for a in base['apps']),'method':'自动静态筛选与分层默认开关；不是逐组人工或实机验证；敏感词过滤不能证明无风险','groupsAudit':audit}
 d.with_name('balance-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print({k:v for k,v in report.items() if k!='groupsAudit'})
