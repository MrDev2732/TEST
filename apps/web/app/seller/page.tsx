import RoleGuard from '../../components/RoleGuard';

export default function Page() {
  return (
    <RoleGuard allowed={['seller']}>
      <div className="p-6">
        <h1 className="text-2xl font-bold">seller home</h1>
        <p>Vista protegida del Sprint 1.</p>
      </div>
    </RoleGuard>
  );
}
