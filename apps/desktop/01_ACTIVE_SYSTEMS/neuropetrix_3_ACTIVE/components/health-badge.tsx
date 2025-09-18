"use client";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { health } from "@/lib/api";

export default function HealthBadge() {
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    let stop = false;
    const ping = async () => {
      try {
        const res = await health();
        if (!stop) setOk(!!res?.status || true);
      } catch {
        if (!stop) setOk(false);
      }
    };
    ping();
    const id = setInterval(ping, 5000);
    return () => { stop = true; clearInterval(id); };
  }, []);

  if (ok === null) return <Badge variant="secondary">Kontrol ediliyor…</Badge>;
  return ok ? (
    <Badge className="bg-emerald-600 hover:bg-emerald-600">Backend: OK</Badge>
  ) : (
    <Badge className="bg-rose-600 hover:bg-rose-600">Backend: OFF</Badge>
  );
}















