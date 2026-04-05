import { useState, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { siteApi } from "@/api/siteApi";
import { cn } from "@/lib/utils";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import {
  Plus,
  Edit,
  Trash2,
  GripVertical,
  X,
  Save,
  Loader2,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronUp,
  HelpCircle,
} from "lucide-react";

/* ================================================================== */
/*  Bilingual labels                                                   */
/* ================================================================== */
const L = {
  ar: {
    title: "إدارة الأسئلة الشائعة",
    subtitle: "إضافة وتعديل وترتيب الأسئلة الشائعة",
    newFaq: "سؤال جديد",
    editFaq: "تعديل السؤال",
    questionAr: "السؤال (عربي)",
    questionEn: "السؤال (إنجليزي)",
    answerAr: "الإجابة (عربي)",
    answerEn: "الإجابة (إنجليزي)",
    category: "التصنيف",
    order: "الترتيب",
    actions: "إجراءات",
    save: "حفظ",
    saving: "جاري الحفظ...",
    cancel: "إلغاء",
    deleteConfirm: "هل تريد حذف هذا السؤال؟",
    noResults: "لا توجد أسئلة شائعة",
    dragHint: "اسحب لإعادة الترتيب",
    published: "منشور",
    unpublished: "غير منشور",
    publish: "نشر",
    unpublish: "إلغاء النشر",
    totalFaqs: "إجمالي الأسئلة",
    publishedCount: "منشور",
    expandAll: "توسيع الكل",
    collapseAll: "طي الكل",
    answer: "الإجابة",
  },
  en: {
    title: "FAQ Manager",
    subtitle: "Add, edit, and reorder frequently asked questions",
    newFaq: "New FAQ",
    editFaq: "Edit FAQ",
    questionAr: "Question (Arabic)",
    questionEn: "Question (English)",
    answerAr: "Answer (Arabic)",
    answerEn: "Answer (English)",
    category: "Category",
    order: "Order",
    actions: "Actions",
    save: "Save",
    saving: "Saving...",
    cancel: "Cancel",
    deleteConfirm: "Are you sure you want to delete this FAQ?",
    noResults: "No FAQs found",
    dragHint: "Drag to reorder",
    published: "Published",
    unpublished: "Unpublished",
    publish: "Publish",
    unpublish: "Unpublish",
    totalFaqs: "Total FAQs",
    publishedCount: "Published",
    expandAll: "Expand All",
    collapseAll: "Collapse All",
    answer: "Answer",
  },
};

/* ================================================================== */
/*  Blank form template                                                */
/* ================================================================== */
const BLANK = {
  question_ar: "",
  question_en: "",
  answer_ar: "",
  answer_en: "",
  category: "",
  published: true,
  display_order: 0,
};

/* ================================================================== */
/*  FAQManager                                                         */
/* ================================================================== */
export default function FAQManager() {
  const { lang = "ar", theme = "dark" } = useOutletContext() || {};
  const t = L[lang] || L.ar;
  const isDark = theme === "dark";
  const isRTL = lang === "ar";
  const qc = useQueryClient();

  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(BLANK);
  const [expandedCards, setExpandedCards] = useState(new Set());

  /* ---- Fetch FAQs ---- */
  const { data: faqs = [], isLoading } = useQuery({
    queryKey: ["admin-faqs"],
    queryFn: () => siteApi.entities.FAQItem.list("display_order", 200),
  });

  /* ---- Mutations ---- */
  const saveMutation = useMutation({
    mutationFn: () => {
      if (editing === "new") {
        return siteApi.entities.FAQItem.create({
          ...form,
          display_order: faqs.length,
        });
      }
      return siteApi.entities.FAQItem.update(editing, form);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-faqs"] });
      setEditing(null);
      setForm(BLANK);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => siteApi.entities.FAQItem.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-faqs"] }),
  });

  const togglePublishMutation = useMutation({
    mutationFn: ({ id, published }) =>
      siteApi.entities.FAQItem.update(id, { published: !published }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-faqs"] }),
  });

  const reorderMutation = useMutation({
    mutationFn: async (updates) => {
      for (const { id, display_order } of updates) {
        await siteApi.entities.FAQItem.update(id, { display_order });
      }
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-faqs"] }),
  });

  /* ---- Handlers ---- */
  const handleDelete = useCallback(
    (id) => {
      if (window.confirm(t.deleteConfirm)) {
        deleteMutation.mutate(id);
      }
    },
    [t.deleteConfirm, deleteMutation]
  );

  const startEdit = (item) => {
    setEditing(item.id);
    setForm({
      question_ar: item.question_ar || "",
      question_en: item.question_en || "",
      answer_ar: item.answer_ar || "",
      answer_en: item.answer_en || "",
      category: item.category || "",
      published: item.published ?? true,
      display_order: item.display_order || 0,
    });
  };

  const startNew = () => {
    setEditing("new");
    setForm(BLANK);
  };

  const cancelEdit = () => {
    setEditing(null);
    setForm(BLANK);
  };

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const toggleExpand = (id) => {
    setExpandedCards((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const toggleExpandAll = () => {
    if (expandedCards.size === faqs.length) {
      setExpandedCards(new Set());
    } else {
      setExpandedCards(new Set(faqs.map((f) => f.id)));
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;
    const srcIdx = result.source.index;
    const dstIdx = result.destination.index;
    if (srcIdx === dstIdx) return;

    const reordered = Array.from(faqs);
    const [moved] = reordered.splice(srcIdx, 1);
    reordered.splice(dstIdx, 0, moved);

    const updates = reordered.map((item, idx) => ({
      id: item.id,
      display_order: idx,
    }));

    qc.setQueryData(["admin-faqs"], reordered);
    reorderMutation.mutate(updates);
  };

  /* ---- Styling helpers ---- */
  const inputCls = cn(
    "w-full rounded-lg border px-3 py-2.5 text-sm outline-none transition-colors",
    isDark
      ? "bg-slate-800 border-white/10 text-white placeholder:text-gray-500 focus:border-purple-500"
      : "bg-white border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-purple-500"
  );

  const labelCls = cn("block text-xs font-semibold mb-1.5", isDark ? "text-gray-400" : "text-gray-500");

  const publishedCount = faqs.filter((f) => f.published !== false).length;

  return (
    <div className="max-w-7xl mx-auto" dir={isRTL ? "rtl" : "ltr"}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h1 className={cn("text-3xl font-black", isDark ? "text-white" : "text-gray-900")}>
            {t.title}
          </h1>
          <p className={cn("text-sm mt-1", isDark ? "text-gray-400" : "text-gray-500")}>
            {t.subtitle}
          </p>
        </div>
        {!editing && (
          <button
            onClick={startNew}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition-colors"
          >
            <Plus size={16} /> {t.newFaq}
          </button>
        )}
      </div>

      {/* Summary chips */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div
          className={cn(
            "inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm",
            isDark ? "bg-slate-800/60 border border-white/10" : "bg-white border border-gray-200 shadow-sm"
          )}
        >
          <HelpCircle size={14} className="text-purple-500" />
          <span className={isDark ? "text-gray-400" : "text-gray-500"}>{t.totalFaqs}:</span>
          <span className={cn("font-bold", isDark ? "text-white" : "text-gray-900")}>{faqs.length}</span>
        </div>
        <div
          className={cn(
            "inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm",
            isDark ? "bg-slate-800/60 border border-white/10" : "bg-white border border-gray-200 shadow-sm"
          )}
        >
          <Eye size={14} className="text-green-500" />
          <span className={isDark ? "text-gray-400" : "text-gray-500"}>{t.publishedCount}:</span>
          <span className={cn("font-bold", isDark ? "text-white" : "text-gray-900")}>{publishedCount}</span>
        </div>
        {faqs.length > 0 && (
          <button
            onClick={toggleExpandAll}
            className={cn(
              "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors",
              isDark ? "bg-white/8 text-gray-300 hover:bg-white/12" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            )}
          >
            {expandedCards.size === faqs.length ? t.collapseAll : t.expandAll}
          </button>
        )}
      </div>

      {/* Edit / New Form */}
      {editing && (
        <div
          className={cn(
            "rounded-xl border p-6 mb-6",
            isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200 shadow-sm"
          )}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className={cn("text-lg font-bold", isDark ? "text-white" : "text-gray-900")}>
              {editing === "new" ? t.newFaq : t.editFaq}
            </h2>
            <button onClick={cancelEdit} className="text-gray-400 hover:text-gray-300 transition-colors">
              <X size={20} />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className={labelCls}>{t.questionAr}</label>
              <input
                value={form.question_ar}
                onChange={(e) => set("question_ar", e.target.value)}
                className={inputCls}
                dir="rtl"
              />
            </div>
            <div>
              <label className={labelCls}>{t.questionEn}</label>
              <input
                value={form.question_en}
                onChange={(e) => set("question_en", e.target.value)}
                className={inputCls}
                dir="ltr"
              />
            </div>
            <div>
              <label className={labelCls}>{t.answerAr}</label>
              <textarea
                value={form.answer_ar}
                onChange={(e) => set("answer_ar", e.target.value)}
                rows={4}
                className={cn(inputCls, "resize-y")}
                dir="rtl"
              />
            </div>
            <div>
              <label className={labelCls}>{t.answerEn}</label>
              <textarea
                value={form.answer_en}
                onChange={(e) => set("answer_en", e.target.value)}
                rows={4}
                className={cn(inputCls, "resize-y")}
                dir="ltr"
              />
            </div>
            <div>
              <label className={labelCls}>{t.category}</label>
              <input
                value={form.category}
                onChange={(e) => set("category", e.target.value)}
                className={inputCls}
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.published}
                onChange={(e) => set("published", e.target.checked)}
                className="h-4 w-4 accent-purple-600 rounded"
              />
              <span className={cn("text-sm font-semibold", isDark ? "text-gray-300" : "text-gray-600")}>
                {t.published}
              </span>
            </label>
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 transition-colors"
            >
              {saveMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
              {saveMutation.isPending ? t.saving : t.save}
            </button>
            <button
              onClick={cancelEdit}
              className={cn(
                "px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors",
                isDark ? "bg-white/10 text-white hover:bg-white/15" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              )}
            >
              {t.cancel}
            </button>
          </div>

          {saveMutation.isError && (
            <div className="mt-3 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-2.5 text-sm text-red-400">
              {saveMutation.error?.message || "Error saving FAQ"}
            </div>
          )}
        </div>
      )}

      {/* Drag and drop list */}
      {isLoading ? (
        <div className={cn("rounded-xl border p-16 flex justify-center", isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200")}>
          <Loader2 className="animate-spin text-purple-500" size={28} />
        </div>
      ) : faqs.length === 0 ? (
        <div className={cn("rounded-xl border text-center py-16", isDark ? "bg-slate-800/60 border-white/10" : "bg-white border-gray-200")}>
          <HelpCircle size={32} className={cn("mx-auto mb-3", isDark ? "text-gray-600" : "text-gray-300")} />
          <p className={cn("text-sm", isDark ? "text-gray-500" : "text-gray-400")}>{t.noResults}</p>
        </div>
      ) : (
        <>
          <p className={cn("text-xs mb-3", isDark ? "text-gray-500" : "text-gray-400")}>
            {t.dragHint}
          </p>
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="faq-list">
              {(provided) => (
                <div ref={provided.innerRef} {...provided.droppableProps} className="space-y-2">
                  {faqs.map((faq, idx) => {
                    const isExpanded = expandedCards.has(faq.id);
                    const question = lang === "ar"
                      ? (faq.question_ar || faq.question_en)
                      : (faq.question_en || faq.question_ar);
                    const answer = lang === "ar"
                      ? (faq.answer_ar || faq.answer_en)
                      : (faq.answer_en || faq.answer_ar);

                    return (
                      <Draggable key={faq.id} draggableId={String(faq.id)} index={idx}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            className={cn(
                              "rounded-xl border transition-all",
                              snapshot.isDragging
                                ? "shadow-lg ring-2 ring-purple-500/30"
                                : "",
                              isDark
                                ? "bg-slate-800/60 border-white/10 hover:bg-slate-800/80"
                                : "bg-white border-gray-200 hover:bg-gray-50 shadow-sm"
                            )}
                          >
                            {/* Main row */}
                            <div className="flex items-center gap-3 p-4">
                              {/* Drag handle */}
                              <div
                                {...provided.dragHandleProps}
                                className={cn(
                                  "cursor-grab active:cursor-grabbing p-1 rounded flex-shrink-0",
                                  isDark ? "text-gray-600 hover:text-gray-400" : "text-gray-300 hover:text-gray-500"
                                )}
                              >
                                <GripVertical size={18} />
                              </div>

                              {/* Order badge */}
                              <span
                                className={cn(
                                  "flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold",
                                  isDark ? "bg-white/8 text-gray-400" : "bg-gray-100 text-gray-500"
                                )}
                              >
                                {idx + 1}
                              </span>

                              {/* Question text */}
                              <button
                                onClick={() => toggleExpand(faq.id)}
                                className="flex-1 min-w-0 text-start"
                              >
                                <div className={cn("font-semibold text-sm truncate", isDark ? "text-white" : "text-gray-900")}>
                                  {question}
                                </div>
                                <div className={cn("text-xs mt-0.5 flex flex-wrap items-center gap-2", isDark ? "text-gray-500" : "text-gray-400")}>
                                  {faq.category && <span>{faq.category}</span>}
                                </div>
                              </button>

                              {/* Published badge */}
                              <span
                                className={cn(
                                  "flex-shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold border",
                                  faq.published !== false
                                    ? "bg-green-500/15 text-green-400 border-green-500/30"
                                    : "bg-gray-500/15 text-gray-400 border-gray-500/30"
                                )}
                              >
                                {faq.published !== false ? t.published : t.unpublished}
                              </span>

                              {/* Action buttons */}
                              <div className="flex items-center gap-1 flex-shrink-0">
                                <button
                                  onClick={() =>
                                    togglePublishMutation.mutate({
                                      id: faq.id,
                                      published: faq.published !== false,
                                    })
                                  }
                                  title={faq.published !== false ? t.unpublish : t.publish}
                                  className={cn(
                                    "rounded-lg p-2 transition-colors",
                                    faq.published !== false
                                      ? "text-green-400 hover:bg-green-500/10"
                                      : isDark
                                      ? "text-gray-500 hover:bg-white/10"
                                      : "text-gray-400 hover:bg-gray-100"
                                  )}
                                >
                                  {faq.published !== false ? <Eye size={15} /> : <EyeOff size={15} />}
                                </button>
                                <button
                                  onClick={() => startEdit(faq)}
                                  className="rounded-lg p-2 text-purple-400 hover:bg-purple-500/10 transition-colors"
                                >
                                  <Edit size={15} />
                                </button>
                                <button
                                  onClick={() => handleDelete(faq.id)}
                                  className="rounded-lg p-2 text-red-400 hover:bg-red-500/10 transition-colors"
                                >
                                  <Trash2 size={15} />
                                </button>
                                <button
                                  onClick={() => toggleExpand(faq.id)}
                                  className={cn(
                                    "rounded-lg p-2 transition-colors",
                                    isDark ? "text-gray-400 hover:bg-white/10" : "text-gray-400 hover:bg-gray-100"
                                  )}
                                >
                                  {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                                </button>
                              </div>
                            </div>

                            {/* Expanded answer area */}
                            {isExpanded && answer && (
                              <div
                                className={cn(
                                  "px-4 pb-4 pt-0",
                                  isRTL ? "mr-[70px]" : "ml-[70px]"
                                )}
                              >
                                <div
                                  className={cn(
                                    "rounded-lg p-3 text-sm leading-relaxed",
                                    isDark ? "bg-white/5 text-gray-300" : "bg-gray-50 text-gray-600"
                                  )}
                                >
                                  <span className={cn("text-xs font-bold uppercase tracking-wide block mb-1.5", isDark ? "text-gray-500" : "text-gray-400")}>
                                    {t.answer}
                                  </span>
                                  {answer}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </Draggable>
                    );
                  })}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </>
      )}
    </div>
  );
}
