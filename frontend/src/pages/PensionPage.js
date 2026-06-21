import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { BadgeDollarSign, ChevronLeft, ChevronRight, Download, Eye, FileSpreadsheet, Loader2, Printer, Search, X } from "lucide-react";
import AppShell from "../components/AppShell";
import GatewayHero from "../components/GatewayHero";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { api, getErrorMessage } from "../lib/api";
import * as XLSX from "xlsx";

export default function PensionPage() {
  const { id } = useParams();
  const [department, setDepartment] = useState(null);
  const [members, setMembers] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [governorates, setGovernorates] = useState([]);
  const [committees, setCommittees] = useState([]);
  const [committeesByGov, setCommitteesByGov] = useState({});
  
  // الفلاتر
  const [governorate, setGovernorate] = useState("");
  const [unionCommittee, setUnionCommittee] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  
  const [showReport, setShowReport] = useState(false);
  const [showPrint, setShowPrint] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // جلب البيانات الأولية
  useEffect(() => {
    (async () => {
      try {
        const [{ data: deps }, { data: tax }] = await Promise.all([
          api.get("/departments"),
          api.get(`/classifications?department_id=${id}`),
        ]);
        setDepartment(deps.find((d) => d.id === id) || null);
        setGovernorates(tax.governorates || []);
        setCommittees(tax.union_committees || []);
        setCommitteesByGov(tax.committees_by_governorate || {});
      } catch (err) {
        setError(getErrorMessage(err));
      }
    })();
  }, [id]);

  // جلب تقرير المعاش
  const loadReport = async (pageNum = 1) => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({
        department_id: id,
        page: pageNum,
        page_size: 20,
      });
      if (governorate) params.set("governorate", governorate);
      if (unionCommittee) params.set("union_committee", unionCommittee);
      if (fromDate) params.set("from_date", fromDate);
      if (toDate) params.set("to_date", toDate);
      if (search) params.set("search", search);

      const { data } = await api.get(`/reports/pension?${params.toString()}`);
      setMembers(data.members || []);
      setTotalCount(data.total_count || 0);
      setPage(data.page || 1);
      setTotalPages(data.total_pages || 1);
      setShowReport(true);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // البحث مع debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // إعادة تحميل التقرير عند تغيير الفلاتر أو البحث
  useEffect(() => {
    if (showReport) {
      loadReport(1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, governorate, unionCommittee, fromDate, toDate]);

  // اللجان المتاحة حسب المحافظة المختارة
  const availableCommittees = useMemo(() => {
    if (!governorate) return committees;
    return committeesByGov[governorate] || [];
  }, [governorate, committees, committeesByGov]);

  // تصدير Excel
  const exportToExcel = () => {
    const data = members.map((m, idx) => ({
      "#": (page - 1) * 20 + idx + 1,
      "الاسم": m.name || "",
      "الرقم القومي": m.national_id || "",
      "تاريخ الميلاد": m.birth_date || "",
      "رقم العضوية": m.membership_number || "",
      "المحافظة": m.governorate || "",
      "اللجنة النقابية": m.union_committee || "",
      "تاريخ المعاش": m.status_date || "",
    }));
    
    // إضافة صف الإجمالي
    data.push({
      "#": "",
      "الاسم": "",
      "الرقم القومي": "",
      "تاريخ الميلاد": "",
      "رقم العضوية": "",
      "المحافظة": "",
      "اللجنة النقابية": `إجمالي الأعضاء: ${totalCount}`,
      "تاريخ المعاش": "",
    });

    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "تقرير المعاش");
    XLSX.writeFile(wb, `تقرير_المعاش_${new Date().toISOString().slice(0, 10)}.xlsx`);
  };

  // تصدير PDF (طباعة)
  const exportToPDF = () => {
    setShowPrint(true);
    setTimeout(() => {
      window.print();
    }, 500);
  };

  // إعادة تعيين الفلاتر
  const resetFilters = () => {
    setGovernorate("");
    setUnionCommittee("");
    setFromDate("");
    setToDate("");
    setSearchInput("");
    setSearch("");
  };

  // تغيير المحافظة
  const handleGovernorateChange = (value) => {
    setGovernorate(value);
    setUnionCommittee(""); // إعادة تعيين اللجنة
  };

  return (
    <AppShell title="تقارير المعاش">
      <div className="space-y-6 print:space-y-4" data-testid="pension-page">
        {/* Header */}
        <GatewayHero
          icon={BadgeDollarSign}
          badge="تقارير المعاش"
          title="تقارير المعاش"
          subtitle={`تقرير مفصل بأسماء الأعضاء الذين حالتهم (معاش) لكل محافظة ولجنة نقابية على حدة`}
          crumbs={[
            { to: "/departments", label: "الإدارات" },
            { to: `/project/${id}`, label: department?.name || "المشروع" },
            { to: `/project/${id}/financial`, label: "الموقف المالي" },
            { label: "المعاش" },
          ]}
          stats={showReport ? [
            { key: "total", label: "إجمالي الأعضاء المتقاعدين", value: totalCount },
            { key: "page", label: "الصفحة الحالية", value: `${page} من ${totalPages}` },
          ] : []}
        />

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* الفلاتر */}
        {!showPrint && (
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-slate-700">الفلاتر والبحث</h3>
                
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  {/* الفترة الزمنية - من */}
                  <div>
                    <Label htmlFor="from-date">من تاريخ</Label>
                    <Input
                      id="from-date"
                      type="date"
                      value={fromDate}
                      onChange={(e) => setFromDate(e.target.value)}
                      className="mt-1"
                    />
                  </div>

                  {/* الفترة الزمنية - إلى */}
                  <div>
                    <Label htmlFor="to-date">إلى تاريخ</Label>
                    <Input
                      id="to-date"
                      type="date"
                      value={toDate}
                      onChange={(e) => setToDate(e.target.value)}
                      className="mt-1"
                    />
                  </div>

                  {/* المحافظة */}
                  <div>
                    <Label htmlFor="governorate">المحافظة</Label>
                    <Select value={governorate} onValueChange={handleGovernorateChange}>
                      <SelectTrigger id="governorate" className="mt-1">
                        <SelectValue placeholder="الكل" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">الكل</SelectItem>
                        {governorates.map((g) => (
                          <SelectItem key={g} value={g}>{g}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* اللجنة النقابية */}
                  <div>
                    <Label htmlFor="committee">اللجنة النقابية</Label>
                    <Select value={unionCommittee} onValueChange={setUnionCommittee} disabled={!governorate}>
                      <SelectTrigger id="committee" className="mt-1">
                        <SelectValue placeholder="الكل" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">الكل</SelectItem>
                        {availableCommittees.map((c) => (
                          <SelectItem key={c} value={c}>{c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* البحث */}
                <div>
                  <Label htmlFor="search">بحث (الاسم - الرقم القومي - رقم العضوية - اسم اللجنة)</Label>
                  <div className="relative mt-1">
                    <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    <Input
                      id="search"
                      type="text"
                      placeholder="ابحث..."
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      className="pr-10"
                    />
                  </div>
                </div>

                {/* الأزرار */}
                <div className="flex flex-wrap gap-3">
                  <Button onClick={() => loadReport(1)} disabled={loading}>
                    {loading ? <Loader2 className="ml-2 h-4 w-4 animate-spin" /> : <Eye className="ml-2 h-4 w-4" />}
                    عرض التقرير
                  </Button>
                  
                  {showReport && (
                    <>
                      <Button onClick={exportToPDF} variant="outline">
                        <Printer className="ml-2 h-4 w-4" />
                        طباعة
                      </Button>
                      <Button onClick={exportToExcel} variant="outline">
                        <FileSpreadsheet className="ml-2 h-4 w-4" />
                        تصدير Excel
                      </Button>
                    </>
                  )}
                  
                  <Button onClick={resetFilters} variant="outline">
                    <X className="ml-2 h-4 w-4" />
                    إعادة تعيين
                  </Button>

                  {showReport && (
                    <Button onClick={() => setShowReport(false)} variant="outline">
                      <X className="ml-2 h-4 w-4" />
                      إغلاق العرض
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* التقرير */}
        {showReport && (
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-bold text-slate-700">
                    نتائج البحث - إجمالي {totalCount} عضو
                  </h3>
                  {!showPrint && totalPages > 1 && (
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => loadReport(page - 1)}
                        disabled={page === 1 || loading}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                      <span className="text-sm text-slate-600">
                        صفحة {page} من {totalPages}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => loadReport(page + 1)}
                        disabled={page === totalPages || loading}
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>

                {members.length === 0 ? (
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center text-slate-500">
                    لا توجد نتائج
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="text-right">#</TableHead>
                          <TableHead className="text-right">الاسم</TableHead>
                          <TableHead className="text-right">الرقم القومي</TableHead>
                          <TableHead className="text-right">تاريخ الميلاد</TableHead>
                          <TableHead className="text-right">رقم العضوية</TableHead>
                          <TableHead className="text-right">المحافظة</TableHead>
                          <TableHead className="text-right">اللجنة النقابية</TableHead>
                          <TableHead className="text-right">تاريخ المعاش</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {members.map((member, idx) => (
                          <TableRow key={member.id}>
                            <TableCell>{(page - 1) * 20 + idx + 1}</TableCell>
                            <TableCell className="font-medium">{member.name || "-"}</TableCell>
                            <TableCell>{member.national_id || "-"}</TableCell>
                            <TableCell>{member.birth_date || "-"}</TableCell>
                            <TableCell>{member.membership_number || "-"}</TableCell>
                            <TableCell>{member.governorate || "-"}</TableCell>
                            <TableCell>{member.union_committee || "-"}</TableCell>
                            <TableCell>{member.status_date || "-"}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}

                {/* الإجمالي */}
                {members.length > 0 && (
                  <div className="rounded-lg border-2 border-emerald-200 bg-emerald-50 p-4 text-center">
                    <p className="text-lg font-bold text-emerald-800">
                      إجمالي الأعضاء المتقاعدين: {totalCount}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* رقم الصفحة للطباعة */}
        {showPrint && (
          <style>{`
            @media print {
              .print\\:hidden { display: none !important; }
              @page { 
                size: A4;
                margin: 1cm;
              }
              body::after {
                content: counter(page);
                position: fixed;
                bottom: 10mm;
                left: 50%;
                transform: translateX(-50%);
                font-size: 10pt;
              }
            }
          `}</style>
        )}
      </div>
    </AppShell>
  );
}
