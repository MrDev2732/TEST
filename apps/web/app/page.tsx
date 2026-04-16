import Link from 'next/link';

export default function Home() {
  return (
    <div className="p-6 space-y-3">
      <h1 className="text-2xl font-bold">FoodTruck SaaS</h1>
      <p>Base Sprint 1 lista para autenticación, tenants y sucursales.</p>
      <Link className="text-blue-600 underline" href="/login">
        Ir a login demo
      </Link>
    </div>
  );
}
