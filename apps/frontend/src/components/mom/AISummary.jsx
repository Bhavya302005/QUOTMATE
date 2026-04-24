import ActionItems from './ActionItems';

function ListBlock({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h4 className="mb-1.5 stitch-label opacity-80">{title}</h4>
      <ul className="list-disc space-y-1 pl-5 text-sm font-light text-on-surface">
        {items.map((item, index) => (
          <li key={`${title}-${index}`}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function AISummary({ summaryData }) {
  if (!summaryData) return null;

  return (
    <div className="space-y-3 border border-dashed border-black/30 bg-surface-container p-4">
      <div className="flex items-center justify-between">
        <h3 className="stitch-label">AI preview</h3>
        <div className="   text-outline-muted">
          Confidence {summaryData.confidence ?? 0}%
        </div>
      </div>

      <p className="whitespace-pre-wrap text-sm font-light text-on-surface">
        {summaryData.summary || 'No summary generated.'}
      </p>

      <ListBlock title="Key points" items={summaryData.key_points} />
      <ListBlock title="Decisions" items={summaryData.decisions} />
      <ListBlock title="Next steps" items={summaryData.next_steps} />

      <div>
        <h4 className="mb-1.5 stitch-label opacity-80">
          Action items ({summaryData.action_items?.length || 0})
        </h4>
        <ActionItems items={summaryData.action_items || []} />
      </div>
    </div>
  );
}
