import {useEffect,useState} from 'react';
import App from './App';
import {setAccessToken,configureApi} from './api';

type Config={mode:string;public_demo:boolean};
export default function AuthGate(){
 const [config,setConfig]=useState<Config|null>(null),[ready,setReady]=useState(false),[role,setRole]=useState('viewer'),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function activate(token:string){setAccessToken(token);configureApi(false);const r=await fetch('/auth/me',{headers:{Authorization:'Bearer '+token}});if(!r.ok)throw Error('Your session could not be verified.');setRole((await r.json()).role);setReady(true);}
 async function refresh(){const r=await fetch('/auth/refresh',{method:'POST',headers:{'Content-Type':'application/json'}});if(!r.ok)throw Error('Sign in to continue.');await activate((await r.json()).access_token);}
 useEffect(()=>{let mounted=true;(async()=>{try{const r=await fetch('/auth/config');if(!r.ok)throw Error('Cannot connect to the application.');const c=await r.json();if(!mounted)return;setConfig(c);if(c.mode==='local'){configureApi(false);setRole('operator');setReady(true);}else{try{await refresh();}catch{if(c.public_demo){configureApi(false);setReady(true);}}}}catch(e){if(mounted)setError((e as Error).message)}})();return()=>{mounted=false}},[]);
 useEffect(()=>{if(!ready||config?.mode!=='supabase')return;const id=setInterval(()=>{refresh().catch(()=>{setAccessToken('');setReady(false);setError('Session expired. Sign in again.');})},5*60*1000);return()=>clearInterval(id)},[ready,config]);
 if(ready)return <><div className="session-bar"><span>{config?.mode==='local'?'Local workspace':role==='operator'?'Operator':'Read-only viewer'}</span>{config?.mode==='supabase'&&<button onClick={async()=>{try{await fetch('/auth/logout',{method:'POST',headers:{Authorization:'Bearer '+getToken()}})}finally{setAccessToken('');setReady(false)}}}>Sign out / change account</button>}</div><App live readOnly={role!=='operator'}/></>;
 function getToken(){return currentToken()}
 return <main className="login"><h1>Dealer Desk</h1><p>Sign in to your stock and enquiry workspace.</p>{error&&<p role="alert">{error}</p>}<form onSubmit={async e=>{e.preventDefault();setBusy(true);setError('');const data=new FormData(e.currentTarget);try{const r=await fetch('/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:data.get('email'),password:data.get('password')})});const body=await r.json();if(!r.ok)throw Error(body.error?.message||'Sign-in failed');await activate(body.access_token);}catch(err){setError((err as Error).message)}finally{setBusy(false)}}}><label>Email<input name="email" type="email" autoComplete="username" required maxLength={254}/></label><label>Password<input name="password" type="password" autoComplete="current-password" required maxLength={1024}/></label><button disabled={busy||!config}>{busy?'Signing in…':'Sign in'}</button></form><p>Accounts are provisioned by your administrator. Contact them for access or account recovery.</p></main>;
}
import {getAccessToken as currentToken} from './api';
