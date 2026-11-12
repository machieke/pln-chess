// Local test instrumentation: configure downloads and supply a real user gesture.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const [url,directory,action='export']=process.argv.slice(2);
if(!url?.startsWith('ws://127.0.0.1:')||!directory||!['export','reconstruct'].includes(action))throw Error('Local browser URL, output directory, and archive action required');
const out=path.resolve(directory);fs.mkdirSync(out,{recursive:true});
const socket=new WebSocket(url),pending=new Map(),events=[];let sequence=0,targetSession,metadata;
const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{
 const id=++sequence;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
});
const timer=setTimeout(()=>{fs.writeFileSync(path.join(out,action+'-timeout.json'),JSON.stringify({events},null,2));socket.close();process.exitCode=1;},55000);
socket.onmessage=async event=>{
 const data=JSON.parse(event.data);
 if(data.id){const p=pending.get(data.id);pending.delete(data.id);if(data.error)p.reject(data.error);else p.resolve(data.result);return;}
 if(!data.method?.startsWith('Browser.download'))return;
 events.push(data);
 if(data.method==='Browser.downloadWillBegin')metadata=data.params;
 if(data.method==='Browser.downloadProgress'&&data.params.state==='completed'){
  const file=[path.join(out,data.params.guid),path.join(out,metadata.suggestedFilename)].find(p=>fs.existsSync(p));
  if(!file)throw Error('Browser reported completion but download file is absent');
  const bytes=fs.readFileSync(file),sha256=crypto.createHash('sha256').update(bytes).digest('hex');
  const state=await send('Runtime.evaluate',{expression:'JSON.stringify({status:document.getElementById("archive-status").textContent,reconstruction:window.plnCompactReconstruction,overflow:document.documentElement.scrollWidth>innerWidth})',returnByValue:true},targetSession);
  const ui=JSON.parse(state.result.value);
  if(action==='reconstruct'&&(!ui.reconstruction?.verified||ui.reconstruction.sha256!==sha256||ui.reconstruction.bytes!==bytes.length))throw Error('Filesystem download differs from browser verified reconstruction');
  const saved=path.join(out,metadata.suggestedFilename);if(file!==saved)fs.renameSync(file,saved);
  fs.writeFileSync(path.join(out,action+'-receipt.json'),JSON.stringify({passed:true,file:path.basename(saved),bytes:bytes.length,sha256,ui,events,real_browser_download:true},null,2)+'\n');
  console.log(JSON.stringify({passed:true,action,bytes:bytes.length,sha256}));clearTimeout(timer);socket.close();
 }
};
socket.onopen=async()=>{
 try{
  const targets=await send('Target.getTargets');const target=targets.targetInfos.find(t=>t.type==='page'&&/^http:\/\/(localhost|127\.0\.0\.1):\d+\/compact-preferences$/.test(t.url));
  if(!target)throw Error('No compact inspector page in this isolated browser');
  targetSession=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true})).sessionId;
  await send('Browser.setDownloadBehavior',{behavior:'allowAndName',browserContextId:target.browserContextId,downloadPath:out,eventsEnabled:true});
  const result=await send('Runtime.evaluate',{expression:`(()=>{const button=document.getElementById(${JSON.stringify(action)});if(button.disabled)throw Error('Archive action still pending');button.scrollIntoView();button.click();return 'clicked';})()`,userGesture:true,returnByValue:true},targetSession);
  if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));
 }catch(error){clearTimeout(timer);console.error(error);socket.close();process.exitCode=1;}
};
