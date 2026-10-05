"""Prueba real contra el stack original. No levanta ni simula Docker."""
import argparse,json,time,uuid,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
parser=argparse.ArgumentParser()
parser.add_argument('--project',choices=['BANKPULSE','LOGISTPULSE'],required=True)
parser.add_argument('--base',default='http://localhost:8080')
parser.add_argument('--out',default='evidencias/sprint1.json')
args=parser.parse_args();steps=[]
report={'project':args.project,'date':datetime.now(timezone.utc).isoformat(),'base':args.base,'steps':steps,'result':'RUNNING'}
def request(method,path,data=None,key=None):
    headers={'Content-Type':'application/json'}
    if key: headers['X-Idempotency-Key']=key
    req=urllib.request.Request(args.base.rstrip('/')+path,data=json.dumps(data).encode() if data is not None else None,method=method,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=30) as r:return {'http':r.status,'body':json.load(r)}
    except urllib.error.HTTPError as e:
        raw=e.read().decode();
        try: body=json.loads(raw)
        except ValueError:body=raw
        return {'http':e.code,'body':body}
def check(id,result,condition):
    steps.append({'test':id,'result':'PASS' if condition else 'FAIL','response':result})
    if not condition:raise AssertionError(id)
try:
    bank=args.project=='BANKPULSE';prefix='BP' if bank else 'LP'
    health=request('GET','/health/payments' if bank else '/health/fulfillment')
    check('SALUD-'+prefix,health,health['http']==200)
    if bank:
        key='VRJ-'+str(uuid.uuid4());sample={'account':'EC-VRJ-'+key[-8:],'amount':25.00,'currency':'USD'}
        created=request('POST','/api/payments',sample,key)
        check('T-BP-01',created,created['http']==200 and created['body'].get('status')=='ACCEPTED' and bool(created['body'].get('id')))
        ident=created['body']['id']
        retry=request('POST','/api/payments',sample,key)
        check('T-BP-03',retry,retry['http']==200 and retry['body'].get('id')==ident)
        listing=request('GET','/api/payments');rows=listing['body']
        check('T-BP-04',listing,listing['http']==200 and isinstance(rows,list) and len(rows)<=50 and sum(r['id']==ident for r in rows)==1 and rows==sorted(rows,key=lambda r:r['createdAt'],reverse=True))
        invalid=[]
        for field,value in [('account',''),('amount',-1),('currency','US')]:
            badkey='VRJ-INVALID-'+str(uuid.uuid4());r=request('POST','/api/payments',{**sample,field:value},badkey)
            check('T-BP-02-'+field,r,r['http']==400);invalid.append(badkey)
        after=request('GET','/api/payments')
        check('T-BP-02-SIN-REGISTRO',after,all(r.get('idempotencyKey') not in invalid for r in after['body']))
    else:
        sample={'storeId':'VRJ-'+uuid.uuid4().hex[:8],'channel':'MOBILE','total':18.50}
        created=request('POST','/api/fulfillment/orders',sample)
        check('T-LP-01',created,created['http']==201 and created['body'].get('status')=='WAITING' and bool(created['body'].get('orderId')))
        ident=created['body']['orderId'];states=['WAITING'];deadline=time.monotonic()+60
        listed=False;polls=[]
        while time.monotonic()<deadline:
            listing=request('GET','/api/fulfillment/orders');rows=listing['body']
            if not listed:
                check('T-LP-02',listing,listing['http']==200 and isinstance(rows,list) and len(rows)<=20 and rows==sorted(rows,key=lambda r:r['createdAt'],reverse=True) and any(r['orderId']==ident for r in rows));listed=True
            item=next((r for r in rows if r['orderId']==ident),None)
            if item:
                polls.append({'state':item['status'],'updatedAt':str(item['updatedAt'])})
                if item['status'] not in states:states.append(item['status'])
                if item['status']=='READY':break
            time.sleep(.2)
        check('T-LP-03',{'orderId':ident,'observed':states},'PREPARING' in states)
        check('T-LP-04',{'orderId':ident,'observed':states,'polls':polls},states==['WAITING','PREPARING','READY'])
    report['result']='PASS'
except Exception as e:
    report['result']='FAIL';report['error']=str(e)
finally:
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report['result']=='PASS' else 1)
