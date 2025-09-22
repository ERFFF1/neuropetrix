import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import HealthBadge from "@/components/health-badge";
import Link from "next/link";

export default function Page() {
  return (
    <main className="mx-auto max-w-7xl p-6 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">NeuroPETrix Dashboard</h1>
        <HealthBadge />
      </header>

      <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {["Toplam Hasta","AI Analiz","Rapor","Ort. Süre"].map((t,i)=>(
          <Card key={i}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">{t}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">—</div>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Aktif İşlemler</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Liste/Progress burada…
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Son Aktiviteler</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Log özeti burada…
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href="/suv-trend">
          <Card className="hover:shadow-md transition">
            <CardHeader>
              <CardTitle>SUV Trend</CardTitle>
            </CardHeader>
            <CardContent>Grafikler ve metrikler</CardContent>
          </Card>
        </Link>
        <Link href="/evidence">
          <Card className="hover:shadow-md transition">
            <CardHeader>
              <CardTitle>Evidence (PICO)</CardTitle>
            </CardHeader>
            <CardContent>PICO formu ve sonuçlar</CardContent>
          </Card>
        </Link>
        <Link href="/asr">
          <Card className="hover:shadow-md transition">
            <CardHeader>
              <CardTitle>ASR Panel</CardTitle>
            </CardHeader>
            <CardContent>Canlı transkript</CardContent>
          </Card>
        </Link>
      </section>
    </main>
  );
}















