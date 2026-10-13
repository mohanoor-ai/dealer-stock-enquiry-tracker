import {beforeEach,afterEach,expect,test} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import App from './App';
import {configureApi,poundsToPence,request} from './api';
import {resetDemo} from './mock';
beforeEach(()=>{resetDemo();configureApi(true);});
afterEach(cleanup);
test('exact money conversion rejects malformed amounts',()=>{expect(poundsToPence('12.30')).toBe(1230);expect(poundsToPence('0.01')).toBe(1);for(const bad of ['-1','1.005','abc'])expect(()=>poundsToPence(bad)).toThrow();});
test('stale prototype edit cannot overwrite stock',async()=>{await request('/api/vehicles/1','PATCH',{revision:1,status:'reserved'});await expect(request('/api/vehicles/1','PATCH',{revision:1,status:'sold'})).rejects.toThrow(/changed/);});
test('create enquiry, schedule and complete follow-up',async()=>{
 render(<App/>);await screen.findByRole('heading',{name:'Demo Motors City'});
 fireEvent.change(screen.getByLabelText('Fictional customer'),{target:{value:'Demo buyer'}});fireEvent.change(screen.getByLabelText('Message'),{target:{value:'Please call'}});fireEvent.click(screen.getByRole('button',{name:'Save enquiry'}));
 await screen.findByText('Demo buyer · stock #1');await waitFor(()=>expect(screen.getByRole('button',{name:'Save follow-up'})).not.toBeDisabled());
 fireEvent.change(screen.getByLabelText('Due date'),{target:{value:'2026-10-20'}});fireEvent.change(screen.getByLabelText('Task note'),{target:{value:'Demo call'}});fireEvent.click(screen.getByRole('button',{name:'Save follow-up'}));
 const complete=await screen.findByRole('button',{name:'Complete task'});fireEvent.click(complete);await screen.findByRole('button',{name:'Reopen task'});
});
test('search shows a useful empty state',async()=>{render(<App/>);await screen.findByRole('heading',{name:'Demo Motors City'});fireEvent.change(screen.getByLabelText('Search stock'),{target:{value:'no-match'}});expect(screen.getByText('No matching vehicles.')).toBeInTheDocument();});
