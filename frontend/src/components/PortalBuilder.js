import { useEffect, useState } from "react";
import {
  Box,
  Plus,
  Edit2,
  Trash2,
  Eye,
  EyeOff,
  Save,
  X,
  FileText,
  BarChart3,
  FormInput,
  Settings,
  ChevronDown,
  ChevronUp,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "./ui/dialog";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import { api, getErrorMessage } from "../lib/api";

// قائمة الأيقونات المتاحة
const AVAILABLE_ICONS = [
  "Box", "FileText", "BarChart3", "FormInput", "Users", "Settings",
  "Database", "Folder", "Package", "ShoppingCart", "Truck", "Warehouse",
  "Calendar", "Clock", "DollarSign", "TrendingUp", "Activity", "Archive"
];

export default function PortalBuilder() {
  const [portals, setPortals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingPortal, setEditingPortal] = useState(null);
  const [expandedPortal, setExpandedPortal] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    permission_key: "",
    icon: { type: "lucide", name: "Box", color: "#3b82f6" }
  });

  useEffect(() => {
    loadPortals();
  }, []);

  const loadPortals = async () => {
    setLoading(true);
    try {
      const res = await api.get("/portals/dynamic/all");
      setPortals(res.data);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.post("/portals/dynamic", formData);
      toast.success("تم إنشاء البوابة بنجاح");
      setShowCreateDialog(false);
      resetForm();
      loadPortals();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const handleUpdate = async (portalId, updates) => {
    try {
      await api.put(`/portals/dynamic/${portalId}`, updates);
      toast.success("تم تحديث البوابة بنجاح");
      loadPortals();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const handleDelete = async (portalId) => {
    if (!window.confirm("هل أنت متأكد من حذف هذه البوابة؟")) return;

    try {
      await api.delete(`/portals/dynamic/${portalId}`);
      toast.success("تم حذف البوابة بنجاح");
      loadPortals();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const toggleActive = async (portal) => {
    handleUpdate(portal.id, { is_active: !portal.is_active });
  };

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      permission_key: "",
      icon: { type: "lucide", name: "Box", color: "#3b82f6" }
    });
    setEditingPortal(null);
  };

  const openEditDialog = (portal) => {
    setFormData({
      name: portal.name,
      description: portal.description || "",
      permission_key: portal.permission_key,
      icon: portal.icon || { type: "lucide", name: "Box", color: "#3b82f6" }
    });
    setEditingPortal(portal);
    setShowCreateDialog(true);
  };

  const handleSave = async () => {
    if (editingPortal) {
      await handleUpdate(editingPortal.id, formData);
      setShowCreateDialog(false);
      resetForm();
    } else {
      await handleCreate();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">منشئ البوابات الديناميكي</h2>
          <p className="text-sm text-gray-500 mt-1">
            إنشاء وإدارة البوابات المخصصة بدون كتابة كود
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          إنشاء بوابة جديدة
        </Button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <div className="grid gap-4">
          {portals.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                <Box className="h-12 w-12 mx-auto mb-4 opacity-20" />
                <p>لا توجد بوابات ديناميكية حالياً</p>
                <p className="text-sm mt-2">قم بإنشاء أول بوابة لك</p>
              </CardContent>
            </Card>
          ) : (
            portals.map((portal) => (
              <Card key={portal.id} className="overflow-hidden">
                <CardHeader className="bg-gray-50/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className="h-10 w-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: portal.icon?.color + "20" }}
                      >
                        <Box
                          className="h-5 w-5"
                          style={{ color: portal.icon?.color || "#3b82f6" }}
                        />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{portal.name}</CardTitle>
                        <p className="text-sm text-gray-500 mt-1">
                          {portal.description || "لا يوجد وصف"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={portal.is_active ? "default" : "secondary"}>
                        {portal.is_active ? "مفعّلة" : "معطّلة"}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() =>
                          setExpandedPortal(expandedPortal === portal.id ? null : portal.id)
                        }
                      >
                        {expandedPortal === portal.id ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                {expandedPortal === portal.id && (
                  <CardContent className="pt-4">
                    <div className="space-y-4">
                      {/* Portal Info */}
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-600">مفتاح الصلاحية:</span>
                          <code className="ml-2 px-2 py-1 bg-gray-100 rounded text-xs">
                            {portal.permission_key}
                          </code>
                        </div>
                        <div>
                          <span className="font-medium text-gray-600">عدد الصفحات:</span>
                          <span className="ml-2">{portal.pages?.length || 0}</span>
                        </div>
                      </div>

                      {/* Pages List */}
                      {portal.pages && portal.pages.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2">الصفحات:</h4>
                          <div className="grid gap-2">
                            {portal.pages.map((page) => (
                              <div
                                key={page.id}
                                className="flex items-center justify-between p-2 bg-gray-50 rounded border"
                              >
                                <div className="flex items-center gap-2">
                                  {page.type === "form" && <FormInput className="h-4 w-4 text-blue-500" />}
                                  {page.type === "report" && <BarChart3 className="h-4 w-4 text-green-500" />}
                                  {page.type === "custom" && <FileText className="h-4 w-4 text-purple-500" />}
                                  <span className="text-sm font-medium">{page.name}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {page.type}
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-2 pt-4 border-t">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditDialog(portal)}
                          className="gap-2"
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                          تعديل
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleActive(portal)}
                          className="gap-2"
                        >
                          {portal.is_active ? (
                            <>
                              <EyeOff className="h-3.5 w-3.5" />
                              إخفاء
                            </>
                          ) : (
                            <>
                              <Eye className="h-3.5 w-3.5" />
                              إظهار
                            </>
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="gap-2 text-blue-600 hover:text-blue-700"
                        >
                          <Settings className="h-3.5 w-3.5" />
                          إدارة الصفحات
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(portal.id)}
                          className="gap-2 mr-auto"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          حذف
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>
            ))
          )}
        </div>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingPortal ? "تعديل البوابة" : "إنشاء بوابة جديدة"}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Name */}
            <div>
              <Label htmlFor="name">اسم البوابة *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="مثال: إدارة المخزون"
              />
            </div>

            {/* Description */}
            <div>
              <Label htmlFor="description">الوصف</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="وصف مختصر للبوابة..."
                rows={3}
              />
            </div>

            {/* Permission Key */}
            <div>
              <Label htmlFor="permission_key">مفتاح الصلاحية *</Label>
              <Input
                id="permission_key"
                value={formData.permission_key}
                onChange={(e) =>
                  setFormData({ ...formData, permission_key: e.target.value.toLowerCase() })
                }
                placeholder="مثال: dynamic.inventory"
                disabled={!!editingPortal}
              />
              <p className="text-xs text-gray-500 mt-1">
                يُستخدم لتحديد من يمكنه الوصول للبوابة (لا يمكن تغييره لاحقاً)
              </p>
            </div>

            {/* Icon Selection */}
            <div>
              <Label>الأيقونة</Label>
              <div className="grid grid-cols-8 gap-2 mt-2">
                {AVAILABLE_ICONS.map((iconName) => (
                  <button
                    key={iconName}
                    onClick={() =>
                      setFormData({
                        ...formData,
                        icon: { ...formData.icon, name: iconName },
                      })
                    }
                    className={`
                      h-12 w-12 rounded-lg border-2 flex items-center justify-center
                      transition-all hover:scale-110
                      ${
                        formData.icon.name === iconName
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }
                    `}
                  >
                    <Box className="h-5 w-5" style={{ color: formData.icon.color }} />
                  </button>
                ))}
              </div>
            </div>

            {/* Icon Color */}
            <div>
              <Label htmlFor="icon_color">لون الأيقونة</Label>
              <div className="flex gap-2">
                <Input
                  id="icon_color"
                  type="color"
                  value={formData.icon.color}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      icon: { ...formData.icon, color: e.target.value },
                    })
                  }
                  className="w-20 h-10"
                />
                <Input
                  value={formData.icon.color}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      icon: { ...formData.icon, color: e.target.value },
                    })
                  }
                  placeholder="#3b82f6"
                  className="flex-1"
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowCreateDialog(false);
              resetForm();
            }}>
              إلغاء
            </Button>
            <Button
              onClick={handleSave}
              disabled={!formData.name || !formData.permission_key}
            >
              <Save className="h-4 w-4 ml-2" />
              {editingPortal ? "حفظ التغييرات" : "إنشاء البوابة"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
