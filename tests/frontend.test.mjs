import test from 'node:test';
import assert from 'node:assert/strict';
import {poundsToPence,money,request} from '../frontend/api.js';
test('money input keeps exact pennies and rejects malformed amounts',()=>{
 assert.equal(poundsToPence('12.30'),1230);
 assert.equal(poundsToPence('0.01'),1);
 for(const value of ['-1','1.001','abc','1e3']) assert.throws(()=>poundsToPence(value));
 assert.equal(money(1230),'£12.30');
});
test('API helper sends JSON and surfaces failures',async()=>{
 const original=globalThis.fetch;
 try{
  globalThis.fetch=async(path,options)=>{assert.equal(path,'/api/vehicles');assert.equal(options.method,'POST');assert.deepEqual(JSON.parse(options.body),{make:'Demo'});return {ok:true,json:async()=>({id:1})};};
  assert.deepEqual(await request('/api/vehicles','POST',{make:'Demo'}),{id:1});
  globalThis.fetch=async()=>({ok:false,status:404,json:async()=>({detail:'Vehicle not found'})});
  await assert.rejects(request('/missing'),/Vehicle not found/);
 }finally{globalThis.fetch=original;}
});
