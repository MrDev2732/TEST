import RoleGuard from '../../components/RoleGuard';

export default function Page() {
  return (
    <RoleGuard allowed={['branch_admin']}>
      <div className="p-6">
        <h1 className="text-2xl font-bold">branch-admin home</h1>
        <p>Vista protegida del Sprint 1.</p>
      </div>
    </RoleGuard>
  );
}
