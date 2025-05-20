import type { PlayerModel } from '../models/PlayerModel';
import { useApi } from './useApi';

export const apiMethod = () => {
    const { read, readOne, create, update, remove } = useApi();

    const fetchData = async () => {
        const data = await read<PlayerModel>('/players');
        console.log(data);
    }
    
    const fetchSingleData = async (id: number) => {
        const data = await readOne<PlayerModel>('/players', id);
        console.log(data);
    };

    const createData = async (name: string) => {
        const newData = await create<PlayerModel>('/players', { name });
        console.log(newData);
    };
    
    const updateData = async (id: number, player: PlayerModel) => {
        const updatedData = await update<PlayerModel>('/players', id, player);
        console.log(updatedData);
    };

    const deleteData = async (id: number) => {
        await remove('/players', id);
        console.log('Item deleted');
    }
}