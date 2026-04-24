import Button from '../common/Button';
import ConfidenceIndicator from '../ocr/ConfidenceIndicator';

export default function MOMOCRResult({
  text,
  confidence,
  suggestedTitle,
  imageUrl,
  meetingDate,
  meetingTime,
  attendees = [],
  meetingContext,
  summary,
  keyPoints = [],
  decisions = [],
  nextSteps = [],
  onRetake,
  onEdit,
  onAccept,
}) {
  return (
    <div className="space-y-4">
      <div className="border border-black bg-surface-white p-4">
        <h3 className="mb-3 stitch-label opacity-80">OCR output</h3>
        <ConfidenceIndicator confidence={confidence || 0} />
        <pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap border border-outline-variant bg-surface-container p-3  text-on-surface">
          {text || 'No text extracted'}
        </pre>
      </div>

      <div className="border border-black bg-surface-white p-4">
        <h3 className="mb-3 stitch-label opacity-80">Suggested fields</h3>
        <div className="space-y-1 text-sm font-light text-on-surface">
          <p>
            <span className="   text-outline-muted">Title: </span>
            {suggestedTitle || 'Meeting notes'}
          </p>
          <p>
            <span className="   text-outline-muted">Date: </span>
            {meetingDate || '—'}
          </p>
          <p>
            <span className="   text-outline-muted">Time: </span>
            {meetingTime || '—'}
          </p>
          <p>
            <span className="   text-outline-muted">Attendees: </span>
            {attendees.length > 0 ? attendees.join(', ') : '—'}
          </p>
          <p>
            <span className="   text-outline-muted">Context: </span>
            {meetingContext || '—'}
          </p>
          <p className="  text-outline-muted">
            Key {keyPoints.length} · Decisions {decisions.length} · Next {nextSteps.length}
          </p>
        </div>

        <div className="mt-3 border border-dashed border-black/30 bg-surface-container p-2    text-on-surface">
          Review extracted text before continuing.
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <Button type="button" variant="outline" onClick={onRetake}>
          Retake
        </Button>
        <Button type="button" variant="ghost" onClick={onEdit}>
          Edit
        </Button>
        <Button type="button" onClick={onAccept}>
          Continue
        </Button>
      </div>
    </div>
  );
}
