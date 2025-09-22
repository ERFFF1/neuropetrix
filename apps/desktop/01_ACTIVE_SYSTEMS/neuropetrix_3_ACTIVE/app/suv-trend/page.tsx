"use client";
import { useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface SUVMeasurement {
  id: string;
  date: string;
  suvmax: number;
  suvmean: number;
  suvpeak: number;
  lesionSize: number;
  location: string;
  backgroundSUV: number;
}

export default function SUVTrendPage() {
  const [measurements, setMeasurements] = useState<SUVMeasurement[]>([
    {
      id: "1",
      date: "2024-01-15",
      suvmax: 3.2,
      suvmean: 2.8,
      suvpeak: 3.0,
      lesionSize: 15,
      location: "Karaciğer",
      backgroundSUV: 1.2
    },
    {
      id: "2", 
      date: "2024-02-15",
      suvmax: 2.8,
      suvmean: 2.4,
      suvpeak: 2.6,
      lesionSize: 12,
      location: "Karaciğer",
      backgroundSUV: 1.1
    }
  ]);

  const [newMeasurement, setNewMeasurement] = useState({
    patientId: "",
    patientName: "",
    diagnosis: "",
    studyType: "",
    date: "",
    suvmax: "",
    suvmean: "",
    suvpeak: "",
    lesionSize: "",
    location: "",
    backgroundSUV: ""
  });

  const addMeasurement = () => {
    if (!newMeasurement.date || !newMeasurement.suvmax) return;

    const measurement: SUVMeasurement = {
      id: Date.now().toString(),
      date: newMeasurement.date,
      suvmax: parseFloat(newMeasurement.suvmax),
      suvmean: parseFloat(newMeasurement.suvmean) || 0,
      suvpeak: parseFloat(newMeasurement.suvpeak) || 0,
      lesionSize: parseFloat(newMeasurement.lesionSize) || 0,
      location: newMeasurement.location || "Bilinmiyor",
      backgroundSUV: parseFloat(newMeasurement.backgroundSUV) || 0
    };

    setMeasurements([...measurements, measurement]);
    
    // Form'u temizle
    setNewMeasurement({
      patientId: "",
      patientName: "",
      diagnosis: "",
      studyType: "",
      date: "",
      suvmax: "",
      suvmean: "",
      suvpeak: "",
      lesionSize: "",
      location: "",
      backgroundSUV: ""
    });
  };

  const calculateMetrics = () => {
    if (measurements.length < 2) return null;

    const sorted = [...measurements].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    const first = sorted[0];
    const last = sorted[sorted.length - 1];

    const suvmaxChange = ((last.suvmax - first.suvmax) / first.suvmax) * 100;
    const lesionSizeChange = ((last.lesionSize - first.lesionSize) / first.lesionSize) * 100;
    const avgSUVmax = measurements.reduce((sum, m) => sum + m.suvmax, 0) / measurements.length;

    return {
      suvmaxChange: suvmaxChange.toFixed(1),
      lesionSizeChange: lesionSizeChange.toFixed(1),
      avgSUVmax: avgSUVmax.toFixed(2),
      totalMeasurements: measurements.length
    };
  };

  const metrics = calculateMetrics();

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">SUV Trend Analizi</h1>
        <p className="text-muted-foreground">PET/CT SUV değerlerinin zaman içindeki değişimi</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sol Kolon - Hasta Formu */}
        <Card>
          <CardHeader>
            <CardTitle>Hasta Bilgileri</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="patientId">Hasta ID</Label>
                <Input
                  id="patientId"
                  value={newMeasurement.patientId}
                  onChange={(e) => setNewMeasurement({...newMeasurement, patientId: e.target.value})}
                  placeholder="P-001"
                />
              </div>
              <div>
                <Label htmlFor="patientName">Hasta Adı</Label>
                <Input
                  id="patientName"
                  value={newMeasurement.patientName}
                  onChange={(e) => setNewMeasurement({...newMeasurement, patientName: e.target.value})}
                  placeholder="Ahmet Yılmaz"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="diagnosis">Tanı</Label>
              <Input
                id="diagnosis"
                value={newMeasurement.diagnosis}
                onChange={(e) => setNewMeasurement({...newMeasurement, diagnosis: e.target.value})}
                placeholder="Karaciğer Kanseri"
              />
            </div>

            <div>
              <Label htmlFor="studyType">Çalışma Tipi</Label>
              <Select value={newMeasurement.studyType} onValueChange={(value) => setNewMeasurement({...newMeasurement, studyType: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Çalışma tipi seçin" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="baseline">Baseline</SelectItem>
                  <SelectItem value="followup">Follow-up</SelectItem>
                  <SelectItem value="response">Response</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="date">Tarih</Label>
              <Input
                id="date"
                type="date"
                value={newMeasurement.date}
                onChange={(e) => setNewMeasurement({...newMeasurement, date: e.target.value})}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="suvmax">SUVmax</Label>
                <Input
                  id="suvmax"
                  type="number"
                  step="0.1"
                  value={newMeasurement.suvmax}
                  onChange={(e) => setNewMeasurement({...newMeasurement, suvmax: e.target.value})}
                  placeholder="3.2"
                />
              </div>
              <div>
                <Label htmlFor="suvmean">SUVmean</Label>
                <Input
                  id="suvmean"
                  type="number"
                  step="0.1"
                  value={newMeasurement.suvmean}
                  onChange={(e) => setNewMeasurement({...newMeasurement, suvmean: e.target.value})}
                  placeholder="2.8"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="lesionSize">Lezyon Boyutu (mm)</Label>
                <Input
                  id="lesionSize"
                  type="number"
                  step="0.1"
                  value={newMeasurement.lesionSize}
                  onChange={(e) => setNewMeasurement({...newMeasurement, lesionSize: e.target.value})}
                  placeholder="15"
                />
              </div>
              <div>
                <Label htmlFor="location">Lokasyon</Label>
                <Input
                  id="location"
                  value={newMeasurement.location}
                  onChange={(e) => setNewMeasurement({...newMeasurement, location: e.target.value})}
                  placeholder="Karaciğer"
                />
              </div>
            </div>

            <Button onClick={addMeasurement} className="w-full">
              Veriyi Ekle
            </Button>
          </CardContent>
        </Card>

        {/* Sağ Kolon - Ölçümler Tablosu */}
        <Card>
          <CardHeader>
            <CardTitle>SUV Ölçümleri</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tarih</TableHead>
                  <TableHead>SUVmax</TableHead>
                  <TableHead>SUVmean</TableHead>
                  <TableHead>Lezyon (mm)</TableHead>
                  <TableHead>Lokasyon</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {measurements.map((measurement) => (
                  <TableRow key={measurement.id}>
                    <TableCell>{measurement.date}</TableCell>
                    <TableCell className="font-medium">{measurement.suvmax}</TableCell>
                    <TableCell>{measurement.suvmean}</TableCell>
                    <TableCell>{measurement.lesionSize}</TableCell>
                    <TableCell>{measurement.location}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Grafikler */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>SUVmax Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={measurements}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="suvmax" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Lezyon Boyutu Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={measurements}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="lesionSize" stroke="#82ca9d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Özet Metrikler */}
      {metrics && (
        <Card>
          <CardHeader>
            <CardTitle>Özet Metrikler</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{metrics.suvmaxChange}%</div>
                <div className="text-sm text-muted-foreground">SUVmax Değişim</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{metrics.lesionSizeChange}%</div>
                <div className="text-sm text-muted-foreground">Lezyon Boyutu Değişim</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{metrics.avgSUVmax}</div>
                <div className="text-sm text-muted-foreground">Ortalama SUVmax</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{metrics.totalMeasurements}</div>
                <div className="text-sm text-muted-foreground">Toplam Ölçüm</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </main>
  );
}















