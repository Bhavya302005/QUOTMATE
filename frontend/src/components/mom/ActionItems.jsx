function formatDate(value) {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function normalizeItem(item, index) {
  return {
    id: item?.id || `item-${index}`,
    title: item?.title || item?.task || 'Untitled task',
    assigned_to: item?.assigned_to || null,
    due_date: item?.due_date || item?.deadline || null,
    status: item?.status || 'pending',
    priority: item?.priority || 'medium',
  };
}

export default function ActionItems({ items = [], emptyText = 'No action items.' }) {
  const normalizedItems = (items || []).map(normalizeItem);

  if (normalizedItems.length === 0) {
    return <p className="   text-outline-muted">{emptyText}</p>;
  }

  return (
    <div className="overflow-x-auto border border-black">
      <table className="min-w-full text-left text-sm font-light">
        <thead className="border-b border-black bg-surface-container    text-on-surface">
          <tr>
            <th className="px-3 py-2 font-normal">Task</th>
            <th className="px-3 py-2 font-normal">Assigned</th>
            <th className="px-3 py-2 font-normal">Due</th>
            <th className="px-3 py-2 font-normal">Priority</th>
            <th className="px-3 py-2 font-normal">Status</th>
          </tr>
        </thead>
        <tbody>
          {normalizedItems.map((item) => (
            <tr key={item.id} className="border-b border-outline-variant">
              <td className="px-3 py-2 text-on-surface">{item.title}</td>
              <td className="px-3 py-2 ">{item.assigned_to || '—'}</td>
              <td className="px-3 py-2 ">{formatDate(item.due_date)}</td>
              <td className="px-3 py-2 ">{item.priority || '—'}</td>
              <td className="px-3 py-2 ">{item.status || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
