import { useRuntimeConfig } from 'nuxt/app';
import { $fetch } from 'ofetch';

export const useApi = () => {
  const config = useRuntimeConfig();
  const $http = $fetch.create({
    baseURL: config.public.apiUrl as string,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
  });

  // Create
  const create = async <T>(endpoint: string, data: Omit<T, 'player_id'>): Promise<T> => {
    return await $http<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  };

  // Read
  const read = async <T>(endpoint: string): Promise<T[]> => {
    return await $http<T[]>(endpoint, {
      method: 'GET',
    });
  };

  // Read one
  const readOne = async <T>(endpoint: string, player_id: number): Promise<T> => {
    return await $http<T>(`${endpoint}/${player_id}`, {
      method: 'GET',
    });
  };

  // Update
  const update = async <T>(endpoint: string, player_id: number, data: Partial<T>): Promise<T> => {
    return await $http<T>(`${endpoint}/${player_id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  };

  // Delete
  const remove = async (endpoint: string, player_id: number): Promise<void> => {
    await $http(`${endpoint}/${player_id}`, {
      method: 'DELETE',
    });
  };

  return {
    create,
    read,
    readOne,
    update,
    remove,
  };
};