import { useEffect } from "react";
import { createPortal } from "react-dom";
import { X, AlertCircle } from "lucide-react";

const ROW_LABELS = {
  membership_number: "رقم العضوية",
  national_id: "الرقم القومي",
  name: "الاسم الرباعي",
  governorate: "المحافظة",
  union_committee: "اللجنة النقابية",
  birth_date: "تاريخ الميلاد",
  subscription_date: "تاريخ الاشتراك",
  status: "الحالة",
  status_date: "تاريخ الحالة",
  address: "العنوان",
  phone: "الهاتف",
  job: "الوظيفة",
  beneficiary_name: "المستحق للإعانة",
};

const FIELD_ORDER = [
  "membership_number",
  "national_id",
  "name",
  "governorate",
  "union_committee",
  "birth_date",
  "subscription_date",
  "status",
  "status_date",
  "address",
  "phone",
  "job",
  "beneficiary_name",
];

/**
 * Modal shown when the API returns 409 duplicate_member.
 *
 * Props:
 *   open: boolean
 *   message: short Arabic title (from API)
 *   member: the existing duplicate record from the API response
 *   onClose: () => void
 */
export default function DuplicateMemberDialog({ open, message, member, onClose }) {
  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (e.key === "Escape") onClose?.(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  // Render via portal at document.body so we escape the parent Radix Dialog's
  // focus trap & pointer-events lock; otherwise the close button is unclickable.
  const content = (
    <div
      data-testid="duplicate-member-dialog"
      role="dialog"
      aria-modal="true"
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(15,23,42,.55)",
        backdropFilter: "blur(3px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 2147483647,
        padding: "16px",
        pointerEvents: "auto",
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#fff",
          width: "min(560px, 96vw)",
          maxHeight: "90vh",
          overflow: "hidden",
          borderRadius: "14px",
          boxShadow: "0 20px 60px rgba(0,0,0,.3)",
          display: "flex",
          flexDirection: "column",
          fontFamily: "'Cairo','Tahoma',sans-serif",
          direction: "rtl",
          borderTop: "6px solid #b91c1c",
          pointerEvents: "auto",
        }}
      >
        <div style={{ padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid #e5e7eb" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <AlertCircle size={24} color="#b91c1c" />
            <h3 style={{ margin: 0, fontSize: "17px", fontWeight: 800, color: "#0f172a" }}>
              بيانات مكررة — العضو موجود مسبقاً
            </h3>
          </div>
          <button
            data-testid="duplicate-member-dialog-close-x"
            onClick={onClose}
            aria-label="إغلاق"
            style={{
              background: "transparent",
              border: 0,
              cursor: "pointer",
              color: "#475569",
              padding: 4,
              borderRadius: 6,
              display: "inline-flex",
            }}
          >
            <X size={22} />
          </button>
        </div>

        <div style={{ padding: "12px 20px 4px", background: "#fef2f2" }}>
          <p style={{ margin: "6px 0 10px", color: "#7f1d1d", fontSize: "13.5px", fontWeight: 700, lineHeight: 1.6 }}>
            {message || "يوجد عضو مسجّل بنفس البيانات في نفس اللجنة والمحافظة."}
          </p>
        </div>

        <div style={{ padding: "12px 20px 16px", overflowY: "auto", flex: 1 }}>
          <div style={{ marginBottom: 8, fontSize: "12.5px", color: "#475569", fontWeight: 700 }}>
            بيانات العضو الموجود في النظام:
          </div>
          <div
            data-testid="duplicate-member-dialog-data"
            style={{
              border: "1px solid #e5e7eb",
              borderRadius: "10px",
              overflow: "hidden",
              background: "#fff",
            }}
          >
            {FIELD_ORDER.map((key, idx) => {
              const raw = member?.[key];
              if (raw === undefined || raw === null || raw === "") return null;
              return (
                <div
                  key={key}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "150px 1fr",
                    gap: "10px",
                    padding: "8px 12px",
                    background: idx % 2 === 0 ? "#f8fafc" : "#fff",
                    borderBottom: "1px solid #f1f5f9",
                    fontSize: "13px",
                  }}
                >
                  <div style={{ fontWeight: 700, color: "#0f3a73" }}>{ROW_LABELS[key]}</div>
                  <div style={{ color: "#0f172a", wordBreak: "break-word" }}>{String(raw)}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div style={{ padding: "12px 20px", borderTop: "1px solid #e5e7eb", background: "#f8fafc", display: "flex", justifyContent: "flex-end" }}>
          <button
            data-testid="duplicate-member-dialog-close-btn"
            onClick={onClose}
            style={{
              background: "#0f3a73",
              color: "#fff",
              border: 0,
              padding: "9px 22px",
              borderRadius: "8px",
              cursor: "pointer",
              fontFamily: "inherit",
              fontSize: "13.5px",
              fontWeight: 700,
            }}
          >
            إغلاق
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(content, document.body);
}
