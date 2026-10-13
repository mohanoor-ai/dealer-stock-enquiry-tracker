import {request, money, poundsToPence} from './api.js';
const get = id => document.getElementById(id);
let editing = null;
function item(tag,text,parent) {const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(parent)parent.appendChild(node);return node;}
function report(error) {get('message').textContent=error.message;}
async function refresh() {
  try {
    const query = new URLSearchParams({q:get('search').value,include_archived:get('archived').checked});
    const [vehicles,enquiries,summary,active] = await Promise.all([request('/api/vehicles?'+query),request('/api/enquiries'),request('/api/dashboard'),request('/api/vehicles')]);
    get('dashboard').replaceChildren();
    for(const [label,value] of Object.entries(summary)) item('div',`${label.replaceAll('_',' ')}: ${label.endsWith('pence')?money(value):value}`,get('dashboard')).className='metric';
    get('vehicles').replaceChildren();
    if(!vehicles.length)item('p','No matching vehicles.',get('vehicles'));
    for(const vehicle of vehicles) {
      const row=item('div',undefined,get('vehicles'));row.className='row';
      item('strong',`${vehicle.make} ${vehicle.model} (${vehicle.year}) • ${money(vehicle.price_pence)}`,row);
      const select=item('select',undefined,row);select.setAttribute('aria-label',`Status for ${vehicle.make} ${vehicle.model}`);
      for(const status of ['available','reserved','sold']){const option=item('option',status,select);option.value=status;option.selected=status===vehicle.status;}
      select.onchange=async()=>{try{await request(`/api/vehicles/${vehicle.id}`,'PATCH',{status:select.value,archived:!!vehicle.archived});await refresh();}catch(error){report(error);}};
      item('button','Edit',row).onclick=()=>{editing=vehicle.id;const form=get('vehicle-form');for(const name of ['make','model','year'])form.elements[name].value=vehicle[name];form.elements.price.value=(vehicle.price_pence/100).toFixed(2);get('form-title').textContent='Edit vehicle';};
      item('button',vehicle.archived?'Restore':'Archive',row).onclick=async()=>{try{await request(`/api/vehicles/${vehicle.id}`,'PATCH',{status:vehicle.status,archived:!vehicle.archived});await refresh();}catch(error){report(error);}};
    }
    get('vehicle-options').replaceChildren();
    for(const vehicle of active){const option=item('option',`${vehicle.make} ${vehicle.model} • #${vehicle.id}`,get('vehicle-options'));option.value=vehicle.id;}
    get('enquiries').replaceChildren();
    if(!enquiries.length)item('p','No enquiries yet.',get('enquiries'));
    for(const enquiry of enquiries){const row=item('div',undefined,get('enquiries'));row.className='row';item('p',`${enquiry.customer} • vehicle #${enquiry.vehicle_id} • ${enquiry.message} • follow up ${enquiry.follow_up||'not set'}`,row);item('button',enquiry.completed?'Reopen':'Mark complete',row).onclick=async()=>{try{await request(`/api/enquiries/${enquiry.id}`,'PATCH',{completed:!enquiry.completed});await refresh();}catch(error){report(error);}};}
  }catch(error){report(error);}
}
get('vehicle-form').onsubmit=async event=>{event.preventDefault();const form=event.target;try{const data={make:form.elements.make.value,model:form.elements.model.value,year:Number(form.elements.year.value),price_pence:poundsToPence(form.elements.price.value)};await request(editing?`/api/vehicles/${editing}`:'/api/vehicles',editing?'PUT':'POST',data);form.reset();editing=null;get('form-title').textContent='Add a vehicle';get('message').textContent='Vehicle saved.';await refresh();}catch(error){report(error);}};
get('enquiry-form').onsubmit=async event=>{event.preventDefault();const form=event.target;try{await request('/api/enquiries','POST',{vehicle_id:Number(form.elements.vehicle_id.value),customer:form.elements.customer.value,message:form.elements.message.value,follow_up:form.elements.follow_up.value||null});form.reset();get('message').textContent='Enquiry saved.';await refresh();}catch(error){report(error);}};
get('cancel').onclick=()=>{editing=null;get('vehicle-form').reset();get('form-title').textContent='Add a vehicle';};
get('search').oninput=refresh;get('archived').onchange=refresh;refresh();
