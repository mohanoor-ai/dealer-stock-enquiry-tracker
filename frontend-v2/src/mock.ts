import sampleStock from './education-stock.json';
import type {Vehicle,Enquiry,Task} from './types';
// In-memory prototype only: no backend, persistence, auth or live model.
const stamp=()=>new Date().toISOString();
let vehicles:Vehicle[]=[];let enquiries:Enquiry[]=[];let tasks:Task[]=[];
export function resetDemo(){vehicles=[{id:1,make:'Demo Motors',model:'City',year:2020,price_pence:950000,approved_facts:[],status:'available',archived:false,revision:1,created_at:stamp(),updated_at:stamp()}];enquiries=[];tasks=[];}
export function loadSampleStock(){
  vehicles=sampleStock.map((row,index)=>({...row,id:index+1,status:index%9===0?'sold':index%5===0?'reserved':'available',archived:false,revision:1,created_at:stamp(),updated_at:stamp()} as Vehicle));
  enquiries=[];tasks=[];
}
resetDemo();
function page<T>(items:T[],url:URL){const offset=Number(url.searchParams.get('offset')||0);const limit=Number(url.searchParams.get('limit')||100);return {items:items.slice(offset,offset+limit),total:items.length,offset,limit};}
function find<T extends {id:number}>(items:T[],id:number):T {const item=items.find(x=>x.id===id);if(!item)throw Error('Record not found.');return item;}
function revise<T extends {revision:number;updated_at:string}>(item:T,data:Record<string,unknown>){if(data.revision!==item.revision)throw Error('This record changed. Refresh before editing.');Object.assign(item,data,{revision:item.revision+1,updated_at:stamp()});return item;}
export async function mockRequest(path:string,method:string,body:unknown):Promise<unknown>{
  const url=new URL(path,'http://demo.local');const data=(body||{}) as Record<string,unknown>;const bits=url.pathname.split('/');const id=Number(bits[3]);
  if(bits[2]==='vehicles'){
    if(method==='GET')return id?find(vehicles,id):page([...vehicles].filter(v=>!v.archived).reverse(),url);
    if(method==='POST'){const vehicle={...data,id:Math.max(0,...vehicles.map(v=>v.id))+1,approved_facts:data.approved_facts||[],status:'available',archived:false,revision:1,created_at:stamp(),updated_at:stamp()} as Vehicle;vehicles.push(vehicle);return vehicle;}
    if(method==='PATCH')return revise(find(vehicles,id),data);
  }
  if(bits[2]==='enquiries'){
    if(method==='GET')return id?find(enquiries,id):page([...enquiries].reverse(),url);
    if(method==='POST'){if(find(vehicles,Number(data.vehicle_id)).archived)throw Error('Vehicle is archived.');const enquiry={...data,id:Math.max(0,...enquiries.map(e=>e.id))+1,status:'new',revision:1,created_at:stamp(),updated_at:stamp()} as Enquiry;enquiries.push(enquiry);return enquiry;}
    if(method==='PATCH')return revise(find(enquiries,id),data);
  }
  if(bits[2]==='tasks'){
    if(method==='GET')return id?find(tasks,id):page([...tasks].reverse(),url);
    if(method==='POST'){if(find(enquiries,Number(data.enquiry_id)).status==='closed')throw Error('Enquiry is closed.');const task={...data,id:Math.max(0,...tasks.map(t=>t.id))+1,note:data.note||'',completed:false,revision:1,created_at:stamp(),updated_at:stamp()} as Task;tasks.push(task);return task;}
    if(method==='PATCH')return revise(find(tasks,id),data);
  }
  throw Error('Prototype route not implemented.');
}
