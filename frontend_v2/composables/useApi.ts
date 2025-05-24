import {ref} from 'vue';
import {useFetch, useRuntimeConfig} from 'nuxt/app';

export default function useApi<T>(endpoint: string) {
  const appConfig = useRuntimeConfig().public;
  console.log(appConfig);
  const baseUrl = appConfig.apiURL;

  const data = ref<T[]>([]);
  const error = ref<Error | null>(null);

  const getAll = async () => {
    try {
      const { data: responseData } = await useFetch<T[]>(`${baseUrl}/${endpoint}`);
      data.value = responseData.value || [];
    } catch (err) {
      error.value = err as Error;
    }
  };

  const getById = async (id: string) => {
    try {
      const { data: responseData } = await useFetch<T>(`${baseUrl}/${endpoint}/${id}`);
      return responseData.value;
    } catch (err) {
      error.value = err as Error;
    }
  };

  const create = async (item: Omit<T, 'id'>) => {
    try {
      return await $fetch<T>(`${baseUrl}/${endpoint}`, {
        method: 'post',
        body: item,
      });
    } catch (err) {
      error.value = err as Error;
    }
  };

  const update = async (id: string, item: Partial<T>) => {
    try {
      return await $fetch<T>(`${baseUrl}/${endpoint}/${id}`, {
        method: 'put',
        body: item,
      });
    } catch (err) {
      error.value = err as Error;
    }
  };

  const deleteItem = async (id: string) => {
    try {
      const { data: responseData } = await useFetch(`${baseUrl}/${endpoint}/${id}`, {
        method: 'DELETE',
      });
      return responseData.value;
    } catch (err) {
      error.value = err as Error;
    }
  };

  return {
    data,
    error,
    getAll,
    getById,
    create,
    update,
    deleteItem,
  };
}
