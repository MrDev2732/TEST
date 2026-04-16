import './globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <main className="mx-auto max-w-md min-h-screen bg-white shadow-sm">{children}</main>
      </body>
    </html>
  );
}
