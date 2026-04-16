'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

const roleRoute: Record<string, string> = {
  seller: '/seller',
  branch_admin: '/branch-admin',
  tenant_admin: '/tenant-admin',
  platform_admin: '/platform-admin'
};

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('seller@demo.com');
  const [password, setPassword] = useState('Pass1234!');
  const [error, setError] = useState('');

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const loginRes = await fetch(`${api}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!loginRes.ok) {
      setError('Credenciales inválidas');
      return;
    }
    const token = await loginRes.json();
    localStorage.setItem('access_token', token.access_token);

    const meRes = await fetch(`${api}/auth/me`, {
      headers: { Authorization: `Bearer ${token.access_token}` }
    });
    const me = await meRes.json();
    router.push(roleRoute[me.role] ?? '/');
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-4">Login</h1>
      <form className="space-y-3" onSubmit={onSubmit}>
        <input className="w-full border rounded p-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" />
        <input className="w-full border rounded p-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" />
        <button className="w-full bg-blue-600 text-white rounded p-2">Ingresar</button>
      </form>
      {error ? <p className="text-red-600 mt-3">{error}</p> : null}
      <p className="text-xs text-slate-600 mt-4">Usuarios demo: seller@demo.com, branch@demo.com, tenant@demo.com, platform@demo.com</p>
    </div>
  );
}
