import { useState, useEffect, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { cn } from "@/lib/utils";
import { supabase } from "@/lib/supabase";
import {
  Save,
  Loader2,
  Building2,
  Link2,
  Key,
  Users,
  Eye,
  EyeOff,
  Info,
  ChevronDown,
} from "lucide-react";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "\u0627\u0644\u0625\u0639\u062F\u0627\u062F\u0627\u062A",
    subtitle: "\u0639\u062F\u0651\u0644 \u0628\u064A\u0627\u0646\u0627\u062A \u0627\u0644\u0634\u0631\u0643\u0629 \u0648\u0627\u0644\u0631\u0648\u0627\u0628\u0637 \u0648\u0635\u0644\u0627\u062D\u064A\u0627\u062A \u0627\u0644\u0645\u0633\u062A\u062E\u062F\u0645\u064A\u0646 \u0628\u0634\u0643\u0644 \u0622\u0645\u0646 \u0648\u0648\u0627\u0636\u062D",
    companyInfo: "\u0645\u0639\u0644\u0648\u0645\u0627\u062A \u0627\u0644\u0634\u0631\u0643\u0629",
    nameAr: "\u0627\u0633\u0645 \u0627\u0644\u0634\u0631\u0643\u0629 (\u0639\u0631\u0628\u064A)",
    nameEn: "\u0627\u0633\u0645 \u0627\u0644\u0634\u0631\u0643\u0629 (\u0625\u0646\u062C\u0644\u064A\u0632\u064A)",
    email: "\u0627\u0644\u0628\u0631\u064A\u062F \u0627\u0644\u0625\u0644\u0643\u062A\u0631\u0648\u0646\u064A",
    phone: "\u0631\u0642\u0645 \u0627\u0644\u0647\u0627\u062A\u0641",
    addressAr: "\u0627\u0644\u0639\u0646\u0648\u0627\u0646 (\u0639\u0631\u0628\u064A)",
    addressEn: "\u0627\u0644\u0639\u0646\u0648\u0627\u0646 (\u0625\u0646\u062C\u0644\u064A\u0632\u064A)",
    socialLinks: "\u0631\u0648\u0627\u0628\u0637 \u0627\u0644\u062A\u0648\u0627\u0635\u0644 \u0627\u0644\u0627\u062C\u062A\u0645\u0627\u0639\u064A",
    twitter: "Twitter / X",
    linkedin: "LinkedIn",
    instagram: "Instagram",
    facebook: "Facebook",
    whatsapp: "WhatsApp",
    integrationKeys: "\u0645\u0641\u0627\u062A\u064A\u062D \u0627\u0644\u062A\u0643\u0627\u0645\u0644",
    ga4Id: "Google Analytics 4 ID",
    posthogKey: "PostHog Key",
    hotjarId: "Hotjar ID",
    save: "\u062D\u0641\u0638",
    saving: "\u062C\u0627\u0631\u064A \u0627\u0644\u062D\u0641\u0638...",
    saved: "\u062A\u0645 \u0627\u0644\u062D\u0641\u0638",
    userManagement: "\u0625\u062F\u0627\u0631\u0629 \u0627\u0644\u0645\u0633\u062A\u062E\u062F\u0645\u064A\u0646",
    userManagementDesc: "\u062A\u062D\u0643\u0645 \u0641\u064A \u0623\u062F\u0648\u0627\u0631 \u0645\u0633\u062A\u062E\u062F\u0645\u064A \u0644\u0648\u062D\u0629 \u0627\u0644\u0625\u062F\u0627\u0631\u0629 \u062D\u0633\u0628 \u0627\u0644\u0645\u0633\u0624\u0648\u0644\u064A\u0629",
    adminUsers: "\u0645\u0633\u062A\u062E\u062F\u0645\u064A \u0627\u0644\u0646\u0638\u0627\u0645",
    role: "\u0627\u0644\u062F\u0648\u0631",
    changeRole: "\u062A\u063A\u064A\u064A\u0631 \u0627\u0644\u062F\u0648\u0631",
    addUserNote: "\u0644\u0625\u0636\u0627\u0641\u0629 \u0645\u0633\u062A\u062E\u062F\u0645 \u062C\u062F\u064A\u062F\u060C \u0627\u0633\u062A\u062E\u062F\u0645 Supabase Dashboard \u0623\u0648 service role API \u0644\u0625\u0646\u0634\u0627\u0621 \u0627\u0644\u0645\u0633\u062A\u062E\u062F\u0645 \u062B\u0645 \u0623\u0636\u0641 \u0633\u062C\u0644 \u0641\u064A \u062C\u062F\u0648\u0644 profiles.",
    noUsers: "\u0644\u0627 \u064A\u0648\u062C\u062F \u0645\u0633\u062A\u062E\u062F\u0645\u0648\u0646 \u062D\u0627\u0644\u064A\u064B\u0627. \u0623\u0636\u0641 \u0645\u0633\u062A\u062E\u062F\u0645\u064B\u0627 \u0645\u0646 Supabase \u062B\u0645 \u062D\u062F\u062F \u062F\u0648\u0631\u0647 \u0647\u0646\u0627.",
    masked: "\u0645\u062E\u0641\u064A",
    readOnly: "\u0644\u0644\u0642\u0631\u0627\u0621\u0629 \u0641\u0642\u0637",
    owner: "\u0645\u0627\u0644\u0643",
    developer: "\u0645\u0637\u0648\u0631",
    admin: "\u0645\u062F\u064A\u0631",
    roleUpdated: "\u062A\u0645 \u062A\u062D\u062F\u064A\u062B \u0627\u0644\u062F\u0648\u0631",
    saveFailed: "\u0641\u0634\u0644 \u0627\u0644\u062D\u0641\u0638",
    saveCompanyHint: "\u062D\u0641\u0638 \u0645\u0639\u0644\u0648\u0645\u0627\u062A \u0627\u0644\u0634\u0631\u0643\u0629 \u0627\u0644\u0623\u0633\u0627\u0633\u064A\u0629 \u0627\u0644\u0645\u0639\u0631\u0648\u0636\u0629 \u0641\u064A \u0627\u0644\u0645\u0648\u0642\u0639.",
    saveSocialHint: "\u062D\u0641\u0638 \u0631\u0648\u0627\u0628\u0637 \u0627\u0644\u062A\u0648\u0627\u0635\u0644 \u0627\u0644\u0627\u062C\u062A\u0645\u0627\u0639\u064A \u0648\u0627\u0644\u0648\u0627\u062A\u0633\u0627\u0628.",
    toggleKeyHint: "\u0625\u0638\u0647\u0627\u0631 \u0623\u0648 \u0625\u062E\u0641\u0627\u0621 \u0645\u0641\u0627\u062A\u064A\u062D \u0627\u0644\u062A\u0643\u0627\u0645\u0644 \u0644\u0644\u0642\u0631\u0627\u0621\u0629 \u0641\u0642\u0637.",
    roleHint: "\u062A\u062D\u062F\u064A\u062F \u0635\u0644\u0627\u062D\u064A\u0629 \u0627\u0644\u0645\u0633\u062A\u062E\u062F\u0645 \u062F\u0627\u062E\u0644 \u0644\u0648\u062D\u0629 \u0627\u0644\u0625\u062F\u0627\u0631\u0629.",
  },
  en: {
    title: "Settings",
    subtitle: "Update company data, links, and user permissions clearly and safely",
    companyInfo: "Company Info",
    nameAr: "Company Name (Arabic)",
    nameEn: "Company Name (English)",
    email: "Email",
    phone: "Phone",
    addressAr: "Address (Arabic)",
    addressEn: "Address (English)",
    socialLinks: "Social Links",
    twitter: "Twitter / X",
    linkedin: "LinkedIn",
    instagram: "Instagram",
    facebook: "Facebook",
    whatsapp: "WhatsApp",
    integrationKeys: "Integration Keys",
    ga4Id: "Google Analytics 4 ID",
    posthogKey: "PostHog Key",
    hotjarId: "Hotjar ID",
    save: "Save",
    saving: "Saving...",
    saved: "Saved",
    userManagement: "User Management",
    userManagementDesc: "Control admin roles based on responsibility",
    adminUsers: "Admin Users",
    role: "Role",
    changeRole: "Change Role",
    addUserNote:
      "To add a new user, use Supabase Dashboard or the service role API to create the user, then add a record in the profiles table.",
    noUsers: "No users found yet. Add a user in Supabase, then assign a role here.",
    masked: "Hidden",
    readOnly: "Read-only",
    owner: "Owner",
    developer: "Developer",
    admin: "Admin",
    roleUpdated: "Role updated",
    saveFailed: "Save failed",
    saveCompanyHint: "Save core company information shown on the website.",
    saveSocialHint: "Save social media and WhatsApp links.",
    toggleKeyHint: "Show or hide integration keys in read-only mode.",
    roleHint: "Set this user's permission level in admin.",
  },
};

/* ================================================================== */
/*  Supabase helpers                                                   */
/* ================================================================== */
async function loadSetting(key) {
  const { data } = await supabase
    .from("settings")
    .select("value")
    .eq("key", key)
    .maybeSingle();
  return data?.value || {};
}

async function saveSetting(key, value) {
  const { data: existing } = await supabase
    .from("settings")
    .select("id")
    .eq("key", key)
    .maybeSingle();

  if (existing) {
    const { error } = await supabase
      .from("settings")
      .update({ value, updated_at: new Date().toISOString() })
      .eq("key", key);
    if (error) throw error;
  } else {
    const { error } = await supabase
      .from("settings")
      .insert({ key, value });
    if (error) throw error;
  }
}

/* ================================================================== */
/*  Component                                                          */
/* ================================================================== */
export default function SettingsPanel() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";

  /* ---- Company info state ---- */
  const [company, setCompany] = useState({
    name_ar: "",
    name_en: "",
    email: "",
    phone: "",
    address_ar: "",
    address_en: "",
  });
  const [companySaving, setCompanySaving] = useState(false);
  const [companySaved, setCompanySaved] = useState(false);

  /* ---- Social links state ---- */
  const [social, setSocial] = useState({
    twitter: "",
    linkedin: "",
    instagram: "",
    facebook: "",
    whatsapp: "",
  });
  const [socialSaving, setSocialSaving] = useState(false);
  const [socialSaved, setSocialSaved] = useState(false);

  /* ---- Integration keys (display-only) ---- */
  const [integrations, setIntegrations] = useState({
    ga4_id: "G-SD3PE755EP",
    posthog_key: "",
    hotjar_id: "",
  });
  const [showKeys, setShowKeys] = useState(false);

  /* ---- Users state ---- */
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [roleUpdating, setRoleUpdating] = useState(null);

  /* ---- Load all settings on mount ---- */
  useEffect(() => {
    loadSetting("company").then((val) => {
      if (val && typeof val === "object") {
        setCompany((prev) => ({ ...prev, ...val }));
      }
    });
    loadSetting("social_links").then((val) => {
      if (val && typeof val === "object") {
        setSocial((prev) => ({ ...prev, ...val }));
      }
    });
    loadSetting("integrations").then((val) => {
      if (val && typeof val === "object") {
        setIntegrations((prev) => ({ ...prev, ...val }));
      }
    });

    supabase
      .from("profiles")
      .select("*")
      .order("created_at", { ascending: true })
      .then(({ data }) => {
        setUsers(data || []);
        setUsersLoading(false);
      })
      .catch(() => setUsersLoading(false));
  }, []);

  const [integrationsSaved, setIntegrationsSaved] = useState(false);
  const [integrationsSaving, setIntegrationsSaving] = useState(false);

  /* ---- Handlers ---- */
  const handleSaveIntegrations = useCallback(async () => {
    setIntegrationsSaving(true);
    setIntegrationsSaved(false);
    try {
      await saveSetting("integrations", integrations);
      setIntegrationsSaved(true);
      setTimeout(() => setIntegrationsSaved(false), 2000);
    } catch (err) {
      console.error("Failed to save integration settings:", err);
    }
    setIntegrationsSaving(false);
  }, [integrations]);

  const handleSaveCompany = useCallback(async () => {
    setCompanySaving(true);
    setCompanySaved(false);
    try {
      await saveSetting("company", company);
      setCompanySaved(true);
      setTimeout(() => setCompanySaved(false), 2000);
    } catch (err) {
      console.error("Failed to save company settings:", err);
    }
    setCompanySaving(false);
  }, [company]);

  const handleSaveSocial = useCallback(async () => {
    setSocialSaving(true);
    setSocialSaved(false);
    try {
      await saveSetting("social_links", social);
      setSocialSaved(true);
      setTimeout(() => setSocialSaved(false), 2000);
    } catch (err) {
      console.error("Failed to save social settings:", err);
    }
    setSocialSaving(false);
  }, [social]);

  const handleRoleChange = useCallback(
    async (userId, newRole) => {
      setRoleUpdating(userId);
      try {
        const { error } = await supabase
          .from("profiles")
          .update({ role: newRole })
          .eq("id", userId);

        if (error) throw error;

        setUsers((prev) =>
          prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
        );
      } catch (err) {
        console.error("Failed to update role:", err);
      }
      setRoleUpdating(null);
    },
    []
  );

  const setC = (key, value) => setCompany((prev) => ({ ...prev, [key]: value }));
  const setS = (key, value) => setSocial((prev) => ({ ...prev, [key]: value }));

  /* ---- Shared styles ---- */
  const inputCls = cn(
    "w-full rounded-lg border px-3 py-2.5 text-sm outline-none transition-colors",
    isDark
      ? "bg-slate-800 border-white/10 text-white placeholder:text-gray-500 focus:border-purple-500"
      : "bg-white border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-purple-500"
  );

  const sectionCls = cn(
    "rounded-xl border p-6 mb-6",
    isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200 shadow-sm"
  );

  const sectionTitle = (icon, label) => (
    <div className="flex items-center gap-2 mb-4">
      {icon}
      <h2 className={cn("text-lg font-bold", isDark ? "text-white" : "text-gray-900")}>
        {label}
      </h2>
    </div>
  );

  const labelCls = cn("block text-xs font-semibold mb-1.5", isDark ? "text-gray-400" : "text-gray-500");

  const saveBtnCls = (saving, saved) =>
    cn(
      "inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50",
      saved
        ? "bg-green-600 text-white"
        : "bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700"
    );

  const maskValue = (val) => {
    if (!val) return "";
    if (val.length <= 4) return "****";
    return val.slice(0, 4) + "*".repeat(Math.max(val.length - 4, 4));
  };

  const ROLE_OPTIONS = ["owner", "admin", "developer"];

  return (
    <div className="max-w-4xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>
      {/* Header */}
      <div className="mb-8">
        <h1 className={cn("text-3xl font-black", isDark ? "text-white" : "text-gray-900")}>
          {t.title}
        </h1>
        <p className={cn("text-sm mt-1", isDark ? "text-gray-400" : "text-gray-500")}>
          {t.subtitle}
        </p>
      </div>

      {/* ============================================================ */}
      {/*  Company Info                                                 */}
      {/* ============================================================ */}
      <div className={sectionCls}>
        {sectionTitle(
          <Building2 size={20} className="text-purple-500" />,
          t.companyInfo
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className={labelCls}>{t.nameAr}</label>
            <input
              value={company.name_ar}
              onChange={(e) => setC("name_ar", e.target.value)}
              className={inputCls}
              dir="rtl"
            />
          </div>
          <div>
            <label className={labelCls}>{t.nameEn}</label>
            <input
              value={company.name_en}
              onChange={(e) => setC("name_en", e.target.value)}
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.email}</label>
            <input
              type="email"
              value={company.email}
              onChange={(e) => setC("email", e.target.value)}
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.phone}</label>
            <input
              value={company.phone}
              onChange={(e) => setC("phone", e.target.value)}
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.addressAr}</label>
            <input
              value={company.address_ar}
              onChange={(e) => setC("address_ar", e.target.value)}
              className={inputCls}
              dir="rtl"
            />
          </div>
          <div>
            <label className={labelCls}>{t.addressEn}</label>
            <input
              value={company.address_en}
              onChange={(e) => setC("address_en", e.target.value)}
              className={inputCls}
              dir="ltr"
            />
          </div>
        </div>
        <button
          onClick={handleSaveCompany}
          disabled={companySaving}
          title={t.saveCompanyHint}
          className={saveBtnCls(companySaving, companySaved)}
        >
          {companySaving ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Save size={16} />
          )}
          {companySaving ? t.saving : companySaved ? t.saved : t.save}
        </button>
      </div>

      {/* ============================================================ */}
      {/*  Social Links                                                 */}
      {/* ============================================================ */}
      <div className={sectionCls}>
        {sectionTitle(
          <Link2 size={20} className="text-cyan-500" />,
          t.socialLinks
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className={labelCls}>{t.twitter}</label>
            <input
              value={social.twitter}
              onChange={(e) => setS("twitter", e.target.value)}
              placeholder="https://twitter.com/..."
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.linkedin}</label>
            <input
              value={social.linkedin}
              onChange={(e) => setS("linkedin", e.target.value)}
              placeholder="https://linkedin.com/company/..."
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.instagram}</label>
            <input
              value={social.instagram}
              onChange={(e) => setS("instagram", e.target.value)}
              placeholder="https://instagram.com/..."
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.facebook}</label>
            <input
              value={social.facebook}
              onChange={(e) => setS("facebook", e.target.value)}
              placeholder="https://facebook.com/..."
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div className="sm:col-span-2">
            <label className={labelCls}>{t.whatsapp}</label>
            <input
              value={social.whatsapp}
              onChange={(e) => setS("whatsapp", e.target.value)}
              placeholder="+966..."
              className={inputCls}
              dir="ltr"
            />
          </div>
        </div>
        <button
          onClick={handleSaveSocial}
          disabled={socialSaving}
          title={t.saveSocialHint}
          className={saveBtnCls(socialSaving, socialSaved)}
        >
          {socialSaving ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Save size={16} />
          )}
          {socialSaving ? t.saving : socialSaved ? t.saved : t.save}
        </button>
      </div>

      {/* ============================================================ */}
      {/*  Integration Keys (Editable, masked)                          */}
      {/* ============================================================ */}
      <div className={sectionCls}>
        {sectionTitle(
          <Key size={20} className="text-amber-500" />,
          t.integrationKeys
        )}
        <div className="flex items-center gap-2 mb-4">
          <button
            onClick={() => setShowKeys(!showKeys)}
            title={t.toggleKeyHint}
            className={cn(
              "rounded-lg p-1.5 transition-colors flex items-center gap-1.5",
              isDark ? "hover:bg-white/10 text-gray-400 font-semibold text-xs" : "hover:bg-gray-100 text-gray-500 font-semibold text-xs"
            )}
          >
            {showKeys ? <EyeOff size={14} /> : <Eye size={14} />}
            {showKeys ? t.masked : t.showKeys || "Show Keys"}
          </button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div>
            <label className={labelCls}>{t.ga4Id}</label>
            <input
              value={showKeys ? (integrations.ga4_id || "") : maskValue(integrations.ga4_id)}
              onChange={(e) => setIntegrations(prev => ({ ...prev, ga4_id: e.target.value }))}
              placeholder="G-XXXXXXX"
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.posthogKey}</label>
            <input
              value={showKeys ? (integrations.posthog_key || "") : maskValue(integrations.posthog_key)}
              onChange={(e) => setIntegrations(prev => ({ ...prev, posthog_key: e.target.value }))}
              placeholder="phc_XXXXXXX"
              className={inputCls}
              dir="ltr"
            />
          </div>
          <div>
            <label className={labelCls}>{t.hotjarId}</label>
            <input
              value={showKeys ? (integrations.hotjar_id || "") : maskValue(integrations.hotjar_id)}
              onChange={(e) => setIntegrations(prev => ({ ...prev, hotjar_id: e.target.value }))}
              placeholder="XXXXXXX"
              className={inputCls}
              dir="ltr"
            />
          </div>
        </div>
        <button
          onClick={handleSaveIntegrations}
          disabled={integrationsSaving}
          className={saveBtnCls(integrationsSaving, integrationsSaved)}
        >
          {integrationsSaving ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Save size={16} />
          )}
          {integrationsSaving ? t.saving : integrationsSaved ? t.saved : t.save}
        </button>
      </div>

      {/* ============================================================ */}
      {/*  User Management                                              */}
      {/* ============================================================ */}
      <div className={sectionCls}>
        {sectionTitle(
          <Users size={20} className="text-green-500" />,
          t.userManagement
        )}
        <p className={cn("text-xs mb-4", isDark ? "text-gray-500" : "text-gray-400")}>
          {t.userManagementDesc}
        </p>

        {usersLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-purple-500" size={24} />
          </div>
        ) : users.length === 0 ? (
          <p className={cn("text-sm py-4", isDark ? "text-gray-500" : "text-gray-400")}>
            {t.noUsers}
          </p>
        ) : (
          <div className="space-y-2 mb-4">
            {users.map((user) => (
              <div
                key={user.id}
                className={cn(
                  "rounded-lg border px-4 py-3 flex flex-wrap items-center justify-between gap-3",
                  isDark ? "border-white/10 bg-slate-900/40" : "border-gray-100 bg-gray-50"
                )}
              >
                <div className="min-w-0">
                  <div className={cn("font-semibold text-sm", isDark ? "text-white" : "text-gray-900")}>
                    {user.full_name || user.email || user.id}
                  </div>
                  {user.email && (
                    <div className={cn("text-xs mt-0.5 truncate", isDark ? "text-gray-500" : "text-gray-400")}>
                      {user.email}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  {/* Role selector */}
                  <div className="relative">
                    <select
                      value={user.role || "developer"}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      disabled={roleUpdating === user.id}
                      title={t.roleHint}
                      className={cn(
                        "appearance-none rounded-lg pl-3 pr-7 py-1.5 text-xs font-bold border cursor-pointer outline-none transition-colors",
                        user.role === "owner"
                          ? "bg-purple-500/15 text-purple-400 border-purple-500/30"
                          : user.role === "admin"
                          ? "bg-blue-500/15 text-blue-400 border-blue-500/30"
                          : "bg-gray-500/15 text-gray-400 border-gray-500/30",
                        roleUpdating === user.id && "opacity-50"
                      )}
                    >
                      {ROLE_OPTIONS.map((role) => (
                        <option key={role} value={role}>
                          {t[role] || role}
                        </option>
                      ))}
                    </select>
                    <ChevronDown
                      size={12}
                      className={cn(
                        "absolute top-1/2 -translate-y-1/2 pointer-events-none",
                        isRTL ? "left-2" : "right-2",
                        isDark ? "text-gray-400" : "text-gray-500"
                      )}
                    />
                  </div>

                  {roleUpdating === user.id && (
                    <Loader2 size={14} className="animate-spin text-purple-500" />
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info note about adding users */}
        <div
          className={cn(
            "rounded-lg border px-4 py-3 flex items-start gap-3",
            isDark ? "border-blue-500/20 bg-blue-500/5" : "border-blue-200 bg-blue-50"
          )}
        >
          <Info size={16} className="text-blue-400 mt-0.5 shrink-0" />
          <p className={cn("text-xs leading-relaxed", isDark ? "text-blue-300" : "text-blue-700")}>
            {t.addUserNote}
          </p>
        </div>
      </div>
    </div>
  );
}
