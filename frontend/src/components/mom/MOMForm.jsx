import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { createPortal } from 'react-dom';
import { Eye, Sparkles, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { momAPI, getApiErrorMessage } from '../../services/api';
import {
  loadDraft,
  saveDraft,
  clearDraft,
  momDraftHasContent,
} from '../../utils/draftStorage';
import Button from '../common/Button';
import AISummary from './AISummary';
import MOMPreview from './MOMPreview';

function normalizeTimeForInput(value) {
  if (!value) return '';
  return String(value).slice(0, 5);
}

function splitLines(value) {
  return String(value || '')
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function splitAttendees(value) {
  return String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizeActionItems(items = []) {
  return (items || []).map((item, index) => ({
    id: item?.id || `preview-${index}`,
    title: item?.title || item?.task || 'Untitled task',
    description: item?.description || '',
    assigned_to: item?.assigned_to || null,
    due_date: item?.due_date || item?.deadline || null,
    priority: item?.priority || 'medium',
    status: item?.status || 'pending',
  }));
}

function buildDefaults(source, defaultMode) {
  return {
    document_id: source?.document_id || '',
    meeting_title: source?.meeting_title || '',
    meeting_date: source?.meeting_date ? String(source.meeting_date).slice(0, 10) : '',
    meeting_time: normalizeTimeForInput(source?.meeting_time),
    location: source?.location || '',
    attendees_text: Array.isArray(source?.attendees) ? source.attendees.join(', ') : '',
    raw_notes: source?.raw_notes || '',
    trigger_ai_summary:
      source?.trigger_ai_summary !== undefined ? Boolean(source.trigger_ai_summary) : defaultMode === 'ai',
    meeting_context: source?.meeting_context || '',
    ai_summary: source?.ai_summary || '',
    key_points_text: Array.isArray(source?.key_points) ? source.key_points.join('\n') : '',
    decisions_text: Array.isArray(source?.decisions) ? source.decisions.join('\n') : '',
    next_steps_text: Array.isArray(source?.next_steps) ? source.next_steps.join('\n') : '',
    original_image_url: source?.original_image_url || '',
    ocr_raw_text: source?.ocr_raw_text || source?.raw_notes || '',
    ocr_confidence: source?.ocr_confidence ?? '',
  };
}

const EMPTY_MOM = {};

export default function MOMForm({ initialData, ocrData, onSuccess, defaultMode = 'manual', resumeDraft = false }) {
  const sourceData = useMemo(() => ocrData || initialData || EMPTY_MOM, [initialData, ocrData]);
  const draftSlot = initialData?.id || 'new';
  const exitCleanRef = useRef(false);
  const [showPreview, setShowPreview] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [aiPreview, setAiPreview] = useState(null);

  const {
    register,
    handleSubmit,
    watch,
    reset,
    setValue,
    getValues,
    formState: { errors, isDirty },
  } = useForm({
    defaultValues: buildDefaults(sourceData, defaultMode),
  });

  const getValuesRef = useRef(getValues);
  const draftSlotRef = useRef(draftSlot);
  const isDirtyRef = useRef(isDirty);
  const aiPreviewRef = useRef(aiPreview);
  const defaultModeRef = useRef(defaultMode);
  getValuesRef.current = getValues;
  draftSlotRef.current = draftSlot;
  isDirtyRef.current = isDirty;
  aiPreviewRef.current = aiPreview;
  defaultModeRef.current = defaultMode;

  const formValues = watch();
  const triggerAISummary = watch('trigger_ai_summary');
  const ocrFingerprint = useMemo(() => (ocrData ? JSON.stringify(ocrData) : ''), [ocrData]);

  useEffect(() => {
    exitCleanRef.current = false;
    const base = buildDefaults(sourceData, defaultMode);
    const shouldLoadDraft = draftSlot !== 'new' || resumeDraft;
    const stored = shouldLoadDraft ? loadDraft('mom', draftSlot) : null;
    if (stored?.values && momDraftHasContent(stored.values)) {
      reset({ ...base, ...stored.values });
      if (stored.aiPreview) setAiPreview(stored.aiPreview);
      else setAiPreview(null);
    } else {
      reset(base);
      setAiPreview(null);
    }
  }, [draftSlot, reset, sourceData, defaultMode, ocrFingerprint, resumeDraft]);

  useEffect(() => {
    const t = setTimeout(() => {
      const values = getValues();
      if (momDraftHasContent(values)) {
        saveDraft('mom', draftSlot, { values, aiPreview, defaultMode });
      } else {
        clearDraft('mom', draftSlot);
      }
    }, 500);
    return () => clearTimeout(t);
  }, [formValues, draftSlot, getValues, aiPreview, defaultMode]);

  const flushDraft = useRef(() => {});
  flushDraft.current = () => {
    if (exitCleanRef.current) return;
    const values = getValuesRef.current();
    const slot = draftSlotRef.current;
    if (isDirtyRef.current || momDraftHasContent(values)) {
      saveDraft('mom', slot, {
        values,
        aiPreview: aiPreviewRef.current,
        defaultMode: defaultModeRef.current,
      });
    } else {
      clearDraft('mom', slot);
    }
  };

  useEffect(() => {
    const onPageLeave = () => flushDraft.current();
    const onVis = () => {
      if (document.visibilityState === 'hidden') flushDraft.current();
    };
    window.addEventListener('pagehide', onPageLeave);
    window.addEventListener('beforeunload', onPageLeave);
    document.addEventListener('visibilitychange', onVis);
    return () => {
      window.removeEventListener('pagehide', onPageLeave);
      window.removeEventListener('beforeunload', onPageLeave);
      document.removeEventListener('visibilitychange', onVis);
    };
  }, []);

  useLayoutEffect(() => {
    return () => {
      flushDraft.current();
    };
  }, []);

  useEffect(() => {
    setIsMounted(true);
    return () => setIsMounted(false);
  }, []);

  const handleSummarize = async () => {
    const rawNotes = String(formValues.raw_notes || '').trim();
    if (rawNotes.length < 10) {
      toast.error('Add at least 10 characters of raw notes for AI summary');
      return;
    }

    setIsSummarizing(true);
    try {
      const response = await momAPI.summarize({
        raw_notes: rawNotes,
        meeting_context: formValues.meeting_context || null,
      });
      setAiPreview(response.data);
      toast.success('AI summary generated');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to generate AI summary'));
    } finally {
      setIsSummarizing(false);
    }
  };

  const applyAISummaryToFields = () => {
    if (!aiPreview) return;
    setValue('ai_summary', aiPreview.summary || '');
    setValue('key_points_text', (aiPreview.key_points || []).join('\n'));
    setValue('decisions_text', (aiPreview.decisions || []).join('\n'));
    setValue('next_steps_text', (aiPreview.next_steps || []).join('\n'));
    toast.success('AI summary applied to editable fields');
  };

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      const structuredPayload = {
        ai_summary: data.ai_summary || null,
        key_points: splitLines(data.key_points_text),
        decisions: splitLines(data.decisions_text),
        next_steps: splitLines(data.next_steps_text),
      };

      const commonPayload = {
        meeting_title: String(data.meeting_title || '').trim(),
        meeting_date: data.meeting_date,
        meeting_time: data.meeting_time || null,
        location: data.location || null,
        attendees: splitAttendees(data.attendees_text),
        raw_notes: String(data.raw_notes || '').trim(),
      };

      if (!commonPayload.meeting_title || !commonPayload.meeting_date || !commonPayload.raw_notes) {
        toast.error('Meeting title, date, and raw notes are required');
        return;
      }

      const response = initialData?.id
        ? await momAPI.update(initialData.id, {
          ...commonPayload,
          ...structuredPayload,
        })
        : await (async () => {
          const parsedOcrConfidence = Number(data.ocr_confidence);
          const ocrConfidence = Number.isFinite(parsedOcrConfidence) ? parsedOcrConfidence : null;

          const created = await momAPI.create({
            document_id: data.document_id || undefined,
            ...commonPayload,
            trigger_ai_summary: Boolean(data.trigger_ai_summary),
            meeting_context: data.meeting_context || null,
            original_image_url: data.original_image_url || null,
            ocr_raw_text: data.ocr_raw_text || commonPayload.raw_notes,
            ocr_confidence: ocrConfidence,
          });

          const hasStructuredData = Boolean(
            structuredPayload.ai_summary ||
            structuredPayload.key_points.length > 0 ||
            structuredPayload.decisions.length > 0 ||
            structuredPayload.next_steps.length > 0
          );

          if (!hasStructuredData) {
            return created;
          }

          return await momAPI.update(created.data.id, structuredPayload);
        })();

      exitCleanRef.current = true;
      clearDraft('mom', draftSlot);
      queueMicrotask(() => {
        exitCleanRef.current = false;
      });
      toast.success(initialData?.id ? 'MOM updated' : 'MOM created');
      onSuccess?.(response.data);
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to save MOM'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const previewData = useMemo(() => {
    const keyPoints = splitLines(formValues.key_points_text);
    const decisions = splitLines(formValues.decisions_text);
    const nextSteps = splitLines(formValues.next_steps_text);

    return {
      id: initialData?.id,
      meeting_title: formValues.meeting_title,
      meeting_date: formValues.meeting_date || null,
      meeting_time: formValues.meeting_time || null,
      location: formValues.location || null,
      attendees: splitAttendees(formValues.attendees_text),
      raw_notes: formValues.raw_notes || '',
      ai_summary: formValues.ai_summary || aiPreview?.summary || '',
      key_points: keyPoints.length > 0 ? keyPoints : (aiPreview?.key_points || []),
      decisions: decisions.length > 0 ? decisions : (aiPreview?.decisions || []),
      next_steps: nextSteps.length > 0 ? nextSteps : (aiPreview?.next_steps || []),
      action_items: initialData?.action_items?.length
        ? initialData.action_items
        : normalizeActionItems(aiPreview?.action_items || []),
      mom_number: initialData?.mom_number || 'DRAFT',
      status: initialData?.status || 'draft',
    };
  }, [aiPreview, formValues, initialData]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <input type="hidden" {...register('document_id')} />
      <input type="hidden" {...register('original_image_url')} />
      <input type="hidden" {...register('ocr_raw_text')} />
      <input type="hidden" {...register('ocr_confidence')} />

      <div className="space-y-4 border border-black bg-surface-white p-4">
        <h3 className="stitch-label opacity-80">Meeting details</h3>

        <div>
          <label className="mb-1.5 block stitch-label">Meeting title</label>
          <input type="text" className="stitch-input" {...register('meeting_title', { required: 'Meeting title is required' })} />
          {errors.meeting_title && (
            <p className="mt-1  text-error">{errors.meeting_title.message}</p>
          )}
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block stitch-label">Meeting date</label>
            <input type="date" className="stitch-input" {...register('meeting_date', { required: 'Meeting date is required' })} />
            {errors.meeting_date && (
              <p className="mt-1  text-error">{errors.meeting_date.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1.5 block stitch-label">Meeting time</label>
            <input type="time" className="stitch-input" {...register('meeting_time')} />
          </div>
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Location</label>
          <input type="text" className="stitch-input" {...register('location')} />
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Attendees</label>
          <input
            type="text"
            placeholder="Comma separated"
            className="stitch-input"
            {...register('attendees_text')}
          />
        </div>
      </div>

      <div className="space-y-4 border border-black bg-surface-white p-4">
        <h3 className="stitch-label opacity-80">Notes &amp; AI</h3>

        <div>
          <label className="mb-1.5 block stitch-label">Raw notes</label>
          <textarea rows={6} className="stitch-input min-h-[8rem]" {...register('raw_notes', { required: 'Raw notes are required' })} />
          {errors.raw_notes && (
            <p className="mt-1  text-error">{errors.raw_notes.message}</p>
          )}
        </div>

        {!initialData?.id && (
          <label className="flex items-center gap-2 border border-outline-variant bg-surface-white px-3 py-2.5    text-on-surface">
            <input type="checkbox" {...register('trigger_ai_summary')} />
            Generate AI summary on create
          </label>
        )}

        {triggerAISummary && !initialData?.id && (
          <div>
            <label className="mb-1.5 block stitch-label">Meeting context (optional)</label>
            <textarea rows={2} className="stitch-input min-h-[3.5rem]" {...register('meeting_context')} />
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="outline" onClick={handleSummarize} isLoading={isSummarizing}>
            <Sparkles className="mr-2 h-4 w-4" /> Generate AI Preview
          </Button>
          {aiPreview && (
            <Button type="button" variant="outline" onClick={applyAISummaryToFields}>
              Apply AI Output
            </Button>
          )}
        </div>

        <AISummary summaryData={aiPreview} />
      </div>

      <div className="space-y-4 border border-black bg-surface-white p-4">
        <h3 className="stitch-label opacity-80">Structured summary</h3>

        <div>
          <label className="mb-1.5 block stitch-label">Summary</label>
          <textarea rows={3} className="stitch-input min-h-[4.5rem]" {...register('ai_summary')} />
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Key points (one per line)</label>
          <textarea rows={3} className="stitch-input min-h-[4.5rem]" {...register('key_points_text')} />
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Decisions (one per line)</label>
          <textarea rows={3} className="stitch-input min-h-[4.5rem]" {...register('decisions_text')} />
        </div>

        <div>
          <label className="mb-1.5 block stitch-label">Next steps (one per line)</label>
          <textarea rows={3} className="stitch-input min-h-[4.5rem]" {...register('next_steps_text')} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <Button type="button" variant="outline" fullWidth onClick={() => setShowPreview(true)}>
          <Eye className="mr-2 h-4 w-4" /> Preview
        </Button>
        <Button type="submit" fullWidth isLoading={isSubmitting}>
          {initialData?.id ? 'Update MOM' : 'Create MOM'}
        </Button>
      </div>

      {showPreview && isMounted && createPortal(
        <div className="fixed inset-0 z-[70] bg-black/50 p-3 sm:p-6">
          <div className="mx-auto flex h-full max-w-5xl flex-col overflow-hidden border border-black bg-surface-white">
            <div className="flex items-center justify-between border-b border-black px-4 py-3">
              <h2 className="text-on-surface">Preview</h2>
              <button
                type="button"
                onClick={() => setShowPreview(false)}
                className="border border-black bg-white p-2 text-on-surface transition-colors duration-100 hover:bg-black hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto p-4">
              <MOMPreview mom={previewData} showActions={false} />
            </div>
          </div>
        </div>,
        document.body
      )}
    </form>
  );
}
