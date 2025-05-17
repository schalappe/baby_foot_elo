import { useRuntimeConfig } from 'nuxt/app';
import { $fetch } from 'ofetch';
import type { PlayerModel } from '../models/player';

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
  const create = async <T extends PlayerModel>(endpoint: string, data: Omit<T, 'id'>): Promise<T> => {
    return await $http<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  };

  // Read
  const read = async <T extends PlayerModel>(endpoint: string): Promise<T[]> => {
    return await $http<T[]>(endpoint, {
      method: 'GET',
    });
  };

  // Read one
  const readOne = async <T extends PlayerModel>(endpoint: string, id: number): Promise<T> => {
    return await $http<T>(`${endpoint}/${id}`, {
      method: 'GET',
    });
  };

  // Update
  const update = async <T extends PlayerModel>(endpoint: string, id: number, data: Partial<T>): Promise<T> => {
    return await $http<T>(`${endpoint}/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  };

  // Delete
  const remove = async (endpoint: string, id: number): Promise<void> => {
    await $http(`${endpoint}/${id}`, {
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