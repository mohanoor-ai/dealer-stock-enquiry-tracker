export type Status = 'available' | 'reserved' | 'sold';
export type Vehicle = {id:number;make:string;model:string;year:number;price_pence:number;approved_facts:string[];status:Status;archived:boolean;revision:number;created_at:string;updated_at:string};
export type Enquiry = {id:number;vehicle_id:number;customer:string;message:string;status:'new'|'contacted'|'closed';revision:number;created_at:string;updated_at:string};
export type Task = {id:number;enquiry_id:number;due_date:string;note:string;completed:boolean;revision:number;created_at:string;updated_at:string};
export type Page<T> = {items:T[];total:number;offset:number;limit:number};
export type Snapshot = {vehicles:Vehicle[];enquiries:Enquiry[];tasks:Task[]};
