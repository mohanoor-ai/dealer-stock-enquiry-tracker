import {defineConfig} from 'vitest/config';
export default defineConfig({server:{proxy:{'/api':'http://127.0.0.1:8090'}},test:{environment:'jsdom',setupFiles:['./src/test-setup.ts'],restoreMocks:true}});
