// Verification instrumentation: permit downloads only in this recorded test context.
import fs from 'node:fs';
import path from 'node:path';
const [url, directory] = process.argv.slice(2);
if (!url?.startsWith('ws://127.0.0.1:') || !directory) throw Error('Supply local test-browser CDP URL and output directory');
const out=path.resolve(directory);fs.mkdirSync(out,{recursive:true});
const socket=new WebSocket(url), pending=new Map(), events=[];let sequence=0;
const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{
 const id=++sequence;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
});
socket.onmessage=event=>{
 const data=JSON.parse(event.data);
 if(data.id){const p=pending.get(data.id);pending.delete(data.id);if(data.error)p.reject(data.error);else p.resolve(data.result);}
 else if(data.method?.startsWith('Browser.download')){
  events.push(data);console.log(JSON.stringify(data));
  if(data.method==='Browser.downloadProgress'&&data.params.state!=='inProgress'){
   fs.writeFileSync(path.join(out,'cdp-events.json'),JSON.stringify(events,null,2));socket.close();
  }
 }
};
socket.onopen=async()=>{
 const targets=await send('Target.getTargets');let found=false;
 for(const target of targets.targetInfos.filter(t=>t.type==='page'&&t.url.includes('/preferences'))){
  const attached=await send('Target.attachToTarget',{targetId:target.targetId,flatten:true});
  const evaluated=await send('Runtime.evaluate',{expression:'Boolean(window.plnPreferenceResultRaw)',returnByValue:true},attached.sessionId);
  await send('Target.detachFromTarget',{sessionId:attached.sessionId});
  if(evaluated.result.value){
   await send('Browser.setDownloadBehavior',{behavior:'allowAndName',browserContextId:target.browserContextId,downloadPath:out,eventsEnabled:true});
   console.log('READY: native-result page recording context allows a download');found=true;
  }
 }
 if(!found)throw Error('No completed native comparison page found');
};
setTimeout(()=>{fs.writeFileSync(path.join(out,'cdp-events.json'),JSON.stringify(events,null,2));socket.close();},45000).unref();
