import Image from "next/image";
import BackendTestInfo from "../components/BackendTestInfo";

export default function Home() {
  return (
    <>
    <section className="w-full flex flex-col items-center gap-12 py-12">
      <div className="text-center">
        <h1 className="text-4xl sm:text-5xl font-extrabold mb-4 text-primary dark:text-primary drop-shadow-lg">Classement Baby Foot Elo</h1>
      </div>
      <div className="w-full max-w-3xl bg-gray-100 dark:bg-zinc-800 rounded-xl shadow-lg p-8 flex flex-col gap-6">
        <h2 className="text-2xl font-bold text-primary mb-4 drop-shadow">Top Joueurs</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left">
  <thead>
    <tr>
      <th className="py-2 px-3 bg-primary text-white rounded-l">#</th>
      <th className="py-2 px-3 bg-primary text-white">Nom</th>
      <th className="py-2 px-3 bg-primary text-white">Elo</th>
      <th className="py-2 px-3 bg-primary text-white rounded-r">Parties</th>
    </tr>
  </thead>
  <tbody>
    <tr className="border-b last:border-0 bg-white dark:bg-zinc-700">
      <td className="py-2 px-3 font-bold text-black dark:text-white">1</td>
      <td className="py-2 px-3 text-black dark:text-white font-semibold">Alice</td>
      <td className="py-2 px-3 text-primary font-semibold">1480</td>
      <td className="py-2 px-3 text-black dark:text-white">32</td>
    </tr>
    <tr className="border-b last:border-0 bg-gray-100 dark:bg-zinc-800">
      <td className="py-2 px-3 font-bold text-black dark:text-white">2</td>
      <td className="py-2 px-3 text-black dark:text-white font-semibold">Bob</td>
      <td className="py-2 px-3 text-primary font-semibold">1455</td>
      <td className="py-2 px-3 text-black dark:text-white">28</td>
    </tr>
    <tr className="bg-white dark:bg-zinc-700">
      <td className="py-2 px-3 font-bold text-black dark:text-white">3</td>
      <td className="py-2 px-3 text-black dark:text-white font-semibold">Charlie</td>
      <td className="py-2 px-3 text-primary font-semibold">1420</td>
      <td className="py-2 px-3 text-black dark:text-white">25</td>
    </tr>
  </tbody>
</table>
        </div>
        <div className="flex justify-end mt-4">
          <a href="#" className="px-6 py-2 rounded bg-primary text-white font-semibold shadow border border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary transition">Voir tout le classement</a>
        </div>
      </div>
      <div className="mt-8">
        <a href="#" className="inline-block px-8 py-3 rounded-full bg-primary text-white text-lg font-bold shadow-lg border border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary transition">Ajouter une partie</a>
      </div>
    </section>
    <BackendTestInfo />
    </>
  );
}
