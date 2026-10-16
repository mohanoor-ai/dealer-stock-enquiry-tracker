import {afterEach,expect,test,vi} from 'vitest';
import {configureApi,setAccessToken,request} from './api';
afterEach(()=>{vi.unstubAllGlobals();configureApi(true,'')});
test('live mode retains memory access token when configured by the app',async()=>{
 setAccessToken('memory-token');configureApi(false);
 const fetcher=vi.fn(async(_p:string,o:RequestInit)=>{expect((o.headers as Record<string,string>).Authorization).toBe('Bearer memory-token');return {ok:true,json:async()=>({id:1})}});
 vi.stubGlobal('fetch',fetcher);expect(await request('/api/vehicles')).toEqual({id:1});
});
test('non-JSON response gives a useful error',async()=>{
 configureApi(false);vi.stubGlobal('fetch',vi.fn(async()=>({ok:false,status:502,json:async()=>{throw Error('html')}})));
 await expect(request('/api/vehicles')).rejects.toThrow(/unreadable/);
});
