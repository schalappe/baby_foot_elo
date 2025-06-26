import { defineNuxtConfig } from 'nuxt/config';
import { fr } from 'vuetify/locale';
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg';

export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    'vuetify-nuxt-module',
  ],
  vuetify: {
    vuetifyOptions: {
      icons: {
        defaultSet: 'mdi',
        aliases,
        sets: [
          mdi,
        ],
      },
      locale: {
        locale: 'fr',
        messages: { fr },
      },
      theme: {
        defaultTheme: 'dark',
        themes: {
          light: {
            dark: false,
          colors: {
            primary: '#556B2F', // Vert olive
            secondary: '#6B4423', // Marron Terre de Sienne
            accent: '#F5F5F5', // Blanc cassé base claire
            error: '#FF5252', // Rouge erreurs
            info: '#2196F3', // Bleu informations
            success: '#4CAF50', // Vert succès
            warning: '#FFC107', // Jaune avertissements
          },
          },
          dark: {
            dark: true,
            colors: {
              primary: '#0A1A2F', // Bleu nuit
              secondary: '#FF7F50', // Corail contraste punchy
              accent: '#F5F5F5', // Blanc cassé base claire
              error: '#FF5252', // Rouge erreurs
              info: '#2196F3', // Bleu informations
              success: '#4CAF50', // Vert succès
              warning: '#FFC107', // Jaune avertissements
            },
          },
        },
      },
    },
    moduleOptions: {
      autoImport: true,
      styles: true,
      useVuetifyLabs: false,
    }
  },
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@mdi/font/css/materialdesignicons.css";`,
        },
      },
    },
    vue: {
      template: {
        transformAssetUrls: true,
      },
    },
  },
  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL
    }
  }
});
