'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

type Me = {
  role: 'seller' | 'branch_admin' | 'tenant_admin' | 'platform_admin';
  full_name: string;
};

export default function RoleGuard({ allowed, children }: { allowed: Me['role'][]; children: React.ReactNode }) {
  const router = useRouter();
  const [ok, setOk] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.replace('/login');
      return;
    }
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((me: Me) => {
        if (allowed.includes(me.role)) {
          setOk(true);
        } else {
          router.replace('/login');
        }
      })
      .catch(() => router.replace('/login'));
  }, [allowed, router]);

  if (!ok) return <div className="p-6">Cargando...</div>;
  return <>{children}</>;
}
