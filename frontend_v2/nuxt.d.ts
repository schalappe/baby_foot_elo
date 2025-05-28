import { NuxtConfig } from '@nuxt/schema';

declare module '@nuxt/schema' {
  interface NuxtConfig {
    vuetify?: {
      vuetifyOptions?: any;
      moduleOptions?: any;
    };
  }
}