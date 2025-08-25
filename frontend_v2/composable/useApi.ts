import { useFetch, useRuntimeConfig } from 'nuxt/app';
import type { UseFetchOptions } from 'nuxt/app';
import { ofetch } from 'ofetch';
import { ref } from 'vue';

// Définition d'une interface pour les options de useFetch pour étendre ou les restreindre
// type FetchOptions = UseFetchOptions<T>;
export const useApi = () => {
  const config = useRuntimeConfig();
  const apiError = ref<Error | null>(null); // Gestion d'erreur globale

  // Créez une instance de $fetch avec une configuration de base
  const $http = ofetch.create({
    baseURL: config.public.apiUrl as string,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    // Intercepteurs pour gérer les erreurs globalement
    onResponseError({ response }) {
      console.error('API Error:', response._data || response.statusText);
      apiError.value = new Error(response._data?.message || 'Une erreur est survenue lors de la requête API.');
      // Vous pouvez choisir de relancer l'erreur ou de la gérer silencieusement
      throw new Error(response._data?.message || 'Failed to fetch data');
    },
  });

  // --- Opérations de Mutation (Création, Mise à jour, Suppression) : Utilisation de $http (ofetch) ---
  /**
   * Crée une nouvelle ressource.
   * @param endpoint L'endpoint de l'API (ex: 'players').
   * @param data Les données de la nouvelle ressource (sans l'ID généré par le serveur).
   * @returns La ressource créée avec l'ID.
   */
  const create = async <T>(
      endpoint: string,
      data: Omit<T, 'player_id' | 'global_elo' | 'created_at' | 'matches_played' | 'wins' | 'losses'>): Promise<T> => {
    try {
      // $fetch gère automatiquement la sérialisation de 'body' en JSON
      return await $http<T>(endpoint, {
        method: 'POST',
        body: data,
      });
    } catch (error) {
      console.error('Error creating resource:', error);
      // L'erreur est déjà gérée par l'intercepteur onResponseError, mais on la propager
      throw error;
    }
  };

  /**
   * Met à jour une ressource existante.
   * @param endpoint L'endpoint de l'API (ex: 'players').
   * @param id L'ID de la ressource à mettre à jour.
   * @param data Les données partielles de la ressource à mettre à jour.
   * @returns La ressource mise à jour.
   */
  const update = async <T>(endpoint: string, id: string | number, data: Partial<T>): Promise<T> => {
    try {
      return await $http<T>(`${endpoint}/${id}`, {
        method: 'PUT',
        body: data, // $fetch gère automatiquement la sérialisation
      });
    } catch (error) {
      console.error('Error updating resource:', error);
      throw error;
    }
  };

  /**
   * Supprime une ressource.
   * @param endpoint L'endpoint de l'API (ex: 'players').
   * @param id L'ID de la ressource à supprimer.
   * @returns Une promesse vide.
   */
  const remove = async (endpoint: string, id: string | number): Promise<void> => {
    try {
      await $http(`${endpoint}/${id}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error('Error deleting resource:', error);
      throw error;
    }
  };

  // --- Opérations de Lecture (useFetch) ---
  /**
   * Récupère toutes les ressources d'un endpoint.
   * @param endpoint L'endpoint de l'API (ex: 'players').
   * @param options Options supplémentaires pour useFetch (ex: { lazy: true, server: false }).
   * @returns Un objet useFetch avec 'data', 'pending', 'error'.
   */
  const read = <T>(endpoint: string, options?: UseFetchOptions<T[]>) => {
    return useFetch<T[]>(endpoint, {
      baseURL: config.public.apiUrl as string, // S'assurer que baseURL est appliqué
      headers: {
        'Accept': 'application/json',
      },
      ...options,
    });
  };

  /**
   * Récupère une seule ressource par son ID.
   * @param endpoint L'endpoint de l'API (ex: 'players').
   * @param id L'ID de la ressource à récupérer.
   * @param options Options supplémentaires pour useFetch.
   * @returns Un objet useFetch avec 'data', 'pending', 'error'.
   */
  const readOne = <T>(endpoint: string, id: string | number, options?: UseFetchOptions<T[]>) => {
    return useFetch<T[]>(`${endpoint}/${id}`, {
      baseURL: config.public.apiUrl as string,
      headers: {
        'Accept': 'application/json',
      },
      ...options,
    });
  };

  return {
    apiError,
    create,
    read,
    readOne,
    update,
    remove,
  };
};