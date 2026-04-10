import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { momAPI, ocrAPI, getApiErrorMessage } from '../../services/api';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ImageUpload from '../ocr/ImageUpload';
import MOMForm from './MOMForm';
import MOMOCRResult from './MOMOCRResult';

function suggestMeetingTitle(text) {
  const firstLine = String(text || '')
    .split('\n')
    .map((line) => line.trim())
    .find((line) => line.length > 0);

  if (!firstLine) {
    return 'Meeting Notes';
  }

  return firstLine.slice(0, 120);
}

function cleanupListItem(value) {
  return String(value || '')
    .replace(/^[\s*•\d.)-]+/, '')
    .trim();
}

function splitNames(value) {
  return String(value || '')
    .split(/,|;|\band\b/gi)
    .map((item) => item.trim())
    .filter(Boolean);
}

function extractAttendees(text) {
  const lines = String(text || '')
    .split('\n')
    .map((line) => line.trim());

  for (const line of lines) {
    const directMatch = line.match(/^(attendees?|participants?|present)\s*[:-]\s*(.+)$/i);
    if (directMatch?.[2]) {
      return splitNames(directMatch[2]).slice(0, 20);
    }
  }

  const headingRegex = /^(attendees?|participants?|present)\s*:?$/i;
  for (let i = 0; i < lines.length; i += 1) {
    if (!headingRegex.test(lines[i])) continue;
    const names = [];
    for (let j = i + 1; j < lines.length; j += 1) {
      const currentLine = lines[j];
      if (!currentLine) break;
      if (/^[A-Za-z ]+\s*[:-]/.test(currentLine)) break;
      const cleaned = cleanupListItem(currentLine);
      if (cleaned) {
        names.push(...splitNames(cleaned));
      }
    }
    if (names.length > 0) {
      return [...new Set(names)].slice(0, 20);
    }
  }

  const sentenceMatch = String(text || '').match(
    /attendees?\s+(?:were|include(?:d)?|:)\s*(.+?)(?:[.]|\n|$)/i
  );
  if (sentenceMatch?.[1]) {
    return splitNames(sentenceMatch[1]).slice(0, 20);
  }

  return [];
}

function extractMeetingContext(text) {
  const lines = String(text || '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  for (const line of lines) {
    const match = line.match(/^(meeting context|context|agenda|objective|purpose)\s*[:-]\s*(.+)$/i);
    if (match?.[2]) {
      return match[2].trim().slice(0, 500);
    }
  }

  const ignoreLine = /^(attendees?|participants?|present|date|time|location|meeting title)\s*[:-]/i;
  const candidates = lines.filter((line) => !ignoreLine.test(line));
  const fallback = candidates.slice(0, 2).join(' ').trim();
  return fallback.slice(0, 500);
}

function extractSectionList(text, sectionPatterns) {
  const lines = String(text || '').split('\n');
  const sectionRegex = new RegExp(`^(${sectionPatterns.join('|')})\\s*:?$`, 'i');

  for (let i = 0; i < lines.length; i += 1) {
    if (!sectionRegex.test(lines[i].trim())) continue;
    const items = [];
    for (let j = i + 1; j < lines.length; j += 1) {
      const currentLine = lines[j].trim();
      if (!currentLine) break;
      if (/^[A-Za-z ]+\s*:?$/.test(currentLine) && !/^[\d*•-]/.test(currentLine)) break;
      const cleaned = cleanupListItem(currentLine);
      if (cleaned) items.push(cleaned);
    }
    if (items.length > 0) return items.slice(0, 10);
  }

  return [];
}

function fallbackSummary(text) {
  const normalized = String(text || '').replace(/\s+/g, ' ').trim();
  if (!normalized) return '';
  const sentences = normalized.match(/[^.!?]+[.!?]?/g) || [];
  return sentences.slice(0, 2).join(' ').trim().slice(0, 800);
}

function toFourDigitYear(value) {
  const year = Number(value);
  if (!Number.isFinite(year)) return null;
  if (year >= 1000) return year;
  if (year >= 70) return 1900 + year;
  if (year >= 0) return 2000 + year;
  return null;
}

function toISODate(year, month, day) {
  const y = Number(year);
  const m = Number(month);
  const d = Number(day);
  if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(d)) return null;
  const test = new Date(Date.UTC(y, m - 1, d));
  if (
    test.getUTCFullYear() !== y ||
    test.getUTCMonth() + 1 !== m ||
    test.getUTCDate() !== d
  ) {
    return null;
  }
  return `${String(y).padStart(4, '0')}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}

function extractDateFromCandidate(value) {
  const text = String(value || '').trim();
  if (!text) return null;

  const monthMap = {
    jan: 1, january: 1,
    feb: 2, february: 2,
    mar: 3, march: 3,
    apr: 4, april: 4,
    may: 5,
    jun: 6, june: 6,
    jul: 7, july: 7,
    aug: 8, august: 8,
    sep: 9, sept: 9, september: 9,
    oct: 10, october: 10,
    nov: 11, november: 11,
    dec: 12, december: 12,
  };

  let match = text.match(/\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\s*,?\s*(\d{2,4})\b/);
  if (match) {
    const day = Number(match[1]);
    const month = monthMap[match[2].toLowerCase()];
    const year = toFourDigitYear(match[3]);
    if (month && year) return toISODate(year, month, day);
  }

  match = text.match(/\b([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{2,4})\b/);
  if (match) {
    const month = monthMap[match[1].toLowerCase()];
    const day = Number(match[2]);
    const year = toFourDigitYear(match[3]);
    if (month && year) return toISODate(year, month, day);
  }

  match = text.match(/\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b/);
  if (match) {
    const a = Number(match[1]);
    const b = Number(match[2]);
    const year = toFourDigitYear(match[3]);
    if (!year) return null;

    let day = a;
    let month = b;

    if (a <= 12 && b > 12) {
      month = a;
      day = b;
    } else if (a <= 12 && b <= 12) {
      day = a;
      month = b;
    }

    return toISODate(year, month, day);
  }

  return null;
}

function extractTimeFromCandidate(value) {
  const text = String(value || '').trim();
  if (!text) return null;

  let match = text.match(/\b([01]?\d|2[0-3]):([0-5]\d)\b/);
  if (match) {
    return `${String(Number(match[1])).padStart(2, '0')}:${match[2]}`;
  }

  match = text.match(/\b(\d{1,2})(?::([0-5]\d))?\s*(am|pm)\b/i);
  if (match) {
    let hour = Number(match[1]);
    const minute = match[2] || '00';
    const meridian = match[3].toLowerCase();

    if (hour === 12) {
      hour = meridian === 'am' ? 0 : 12;
    } else if (meridian === 'pm') {
      hour += 12;
    }

    if (hour >= 0 && hour <= 23) {
      return `${String(hour).padStart(2, '0')}:${minute}`;
    }
  }

  return null;
}

function extractMeetingDateAndTime(text) {
  const raw = String(text || '');
  const lines = raw.split('\n').map((line) => line.trim()).filter(Boolean);
  const today = new Date().toISOString().slice(0, 10);

  let meetingDate = null;
  let meetingTime = null;

  for (const line of lines) {
    if (!meetingDate) {
      const dateMatch = line.match(/^(meeting date|date)\s*[:-]\s*(.+)$/i);
      if (dateMatch?.[2]) {
        meetingDate = extractDateFromCandidate(dateMatch[2]);
      }
    }

    if (!meetingTime) {
      const timeMatch = line.match(/^(meeting time|time)\s*[:-]\s*(.+)$/i);
      if (timeMatch?.[2]) {
        meetingTime = extractTimeFromCandidate(timeMatch[2]);
      }
    }

    if (meetingDate && meetingTime) break;
  }

  if (!meetingDate) {
    for (const line of lines) {
      meetingDate = extractDateFromCandidate(line);
      if (meetingDate) break;
    }
  }

  if (!meetingTime) {
    for (const line of lines) {
      meetingTime = extractTimeFromCandidate(line);
      if (meetingTime) break;
    }
  }

  return {
    meeting_date: meetingDate || today,
    meeting_time: meetingTime || '',
  };
}

function parseMomSignalsFromText(text) {
  const dateTime = extractMeetingDateAndTime(text);

  return {
    meeting_title: suggestMeetingTitle(text),
    meeting_date: dateTime.meeting_date,
    meeting_time: dateTime.meeting_time,
    attendees: extractAttendees(text),
    meeting_context: extractMeetingContext(text),
    key_points: extractSectionList(text, ['key points?', 'discussion points?', 'highlights?']),
    decisions: extractSectionList(text, ['decisions?', 'decisions made', 'resolution']),
    next_steps: extractSectionList(text, ['next steps?', 'next efforts?', 'follow[- ]?ups?', 'action items?']),
    ai_summary: fallbackSummary(text),
  };
}

export default function OCRFlowWithMOM({ onSuccess, onCancel }) {
  const [step, setStep] = useState('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [ocrPayload, setOcrPayload] = useState(null);

  const handleExtract = async (formData) => {
    setIsLoading(true);
    setLoadingMessage('Scanning meeting notes...');

    try {
      const ocrResponse = await ocrAPI.upload(formData);
      const extractedText = ocrResponse.data?.ocr_result?.text || '';
      const confidence = ocrResponse.data?.ocr_result?.confidence || 0;
      const imageUrl = ocrResponse.data?.original_image_url || null;

      if (!extractedText.trim()) {
        toast.error('No text was extracted from the image.');
        return;
      }

      const parsed = parseMomSignalsFromText(extractedText);

      setLoadingMessage('Generating AI summary and action items...');
      let aiSummaryData = null;
      try {
        const summarizeResponse = await momAPI.summarize({
          raw_notes: extractedText,
          meeting_context: parsed.meeting_context || null,
        });
        aiSummaryData = summarizeResponse.data;
      } catch {
        aiSummaryData = null;
      }

      setOcrPayload({
        meeting_title: parsed.meeting_title,
        meeting_date: parsed.meeting_date,
        meeting_time: parsed.meeting_time,
        raw_notes: extractedText,
        ocr_raw_text: extractedText,
        ocr_confidence: confidence,
        original_image_url: imageUrl,
        attendees: parsed.attendees,
        meeting_context: parsed.meeting_context,
        ai_summary: aiSummaryData?.summary || parsed.ai_summary,
        key_points: (aiSummaryData?.key_points || parsed.key_points || []).slice(0, 12),
        decisions: (aiSummaryData?.decisions || parsed.decisions || []).slice(0, 12),
        next_steps: (aiSummaryData?.next_steps || parsed.next_steps || []).slice(0, 12),
        trigger_ai_summary: false,
        action_items: aiSummaryData?.action_items || [],
      });
      setStep('review');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to process image'));
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h2 className="text-base font-light tracking-tight text-on-surface">
          {step === 'upload' ? 'Scan MOM notes' : step === 'review' ? 'Review OCR' : 'Create MOM'}
        </h2>
      </div>

      {step === 'upload' && (
        <ImageUpload onExtract={handleExtract} isLoading={isLoading} />
      )}

      {step === 'review' && (
        <MOMOCRResult
          text={ocrPayload?.ocr_raw_text}
          confidence={ocrPayload?.ocr_confidence}
          imageUrl={ocrPayload?.original_image_url}
          suggestedTitle={ocrPayload?.meeting_title}
          meetingDate={ocrPayload?.meeting_date}
          meetingTime={ocrPayload?.meeting_time}
          attendees={ocrPayload?.attendees}
          meetingContext={ocrPayload?.meeting_context}
          summary={ocrPayload?.ai_summary}
          keyPoints={ocrPayload?.key_points}
          decisions={ocrPayload?.decisions}
          nextSteps={ocrPayload?.next_steps}
          onRetake={() => setStep('upload')}
          onEdit={() => setStep('form')}
          onAccept={() => setStep('form')}
        />
      )}

      {step === 'form' && (
        <MOMForm
          ocrData={ocrPayload}
          defaultMode="ai"
          onSuccess={onSuccess}
        />
      )}

      {isLoading && (
        <div className="fixed inset-0 z-50 md:left-64 flex flex-col items-center justify-center bg-surface">
          <LoadingSpinner size="lg" />
          <p className="mt-3    text-outline-muted">{loadingMessage || 'Processing…'}</p>
        </div>
      )}
    </div>
  );
}
