import type {Vehicle, Enquiry, Task, Snapshot, Page} from './types';
import {mockRequest} from './mock';
let token = '';
let demo = true;
export function configureApi(useDemo:boolean, accessToken='') {demo=useDemo;token=accessToken;}
export class ApiError extends Error {
  constructor(public status:number, message:string) {super(message);}
}
// This is the only place that calls fetch. Do not automatically retry writes.
export async function request<T>(path:string, method='GET', data?:unknown):Promise<T> {
  if(demo) return mockRequest(path,method,data) as Promise<T>;
  const controller = new AbortController();
  const timeout=setTimeout(()=>controller.abort(),10000);
  try {
    const response=await fetch(path,{method,signal:controller.signal,headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},body:data===undefined?undefined:JSON.stringify(data)});
    const result=await response.json();
    if(!response.ok) throw new ApiError(response.status,result.error?.message || `Request failed (${response.status})`);
    return result;
  }finally{clearTimeout(timeout);}
}
async function allPages<T>(path:string):Promise<T[]> {
  const result:T[]=[];
  let offset=0;
  while(true){const page=await request<Page<T>>(`${path}?offset=${offset}&limit=100`);result.push(...page.items);offset+=page.items.length;if(offset>=page.total || page.items.length===0)return result;}
}
export async function loadSnapshot():Promise<Snapshot> {
  const [vehicles,enquiries,tasks]=await Promise.all([allPages<Vehicle>('/api/vehicles'),allPages<Enquiry>('/api/enquiries'),allPages<Task>('/api/tasks')]);
  return {vehicles,enquiries,tasks};
}
export function poundsToPence(value:string):number {
  if(!/^\d+(\.\d{1,2})?$/.test(value))throw Error('Use pounds with up to two decimal places.');
  const [whole,decimal='']=value.split('.');const pence=Number(whole)*100+Number(decimal.padEnd(2,'0'));
  if(!Number.isSafeInteger(pence)||pence>100000000)throw Error('Price is too large.');return pence;
}
export function money(value:number){return new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP'}).format(value/100);}
