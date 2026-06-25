import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.melibaratos.app',
  appName: 'Meli Cheap',
  webDir: 'dist',
  server: {
    cleartext: true,
    allowNavigation: ['*'],
  },
};

export default config;
