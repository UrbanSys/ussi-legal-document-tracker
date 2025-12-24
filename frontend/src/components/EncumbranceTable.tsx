import type { EncumbranceRow, EncumbranceAction, EncumbranceStatus } from '../types';
import './Table.css';

const headerLabels = [
  'Item',
  'Document #',
  'Description',
  'Signatories',
  'Action',
  'Circulation Notes',
  'Status',
];

interface EncumbranceTableProps {
  name: string;
  rows: EncumbranceRow[];
  actions: EncumbranceAction[];
  statuses: EncumbranceStatus[];
  onFieldChange: (name: string, index: number, field: string, value: string | number) => void;
  onAddRow: (name: string) => void;
  onRemoveRow: (name: string) => void;
  onRemoveTitle: (name: string) => void;
}

export function EncumbranceTable({
  name,
  rows = [],
  actions,
  statuses,
  onFieldChange,
  onAddRow,
  onRemoveRow,
  onRemoveTitle,
}: EncumbranceTableProps) {
  return (
    <section className="panel">
      <div className="panel__heading">
        <h3>Title - {name}</h3>
        <div className="panel__actions">
          <button type="button" className="danger" onClick={() => onRemoveTitle(name)}>
            - Title
          </button>
          <button type="button" onClick={() => onAddRow(name)}>
            + Row
          </button>
          <button
            type="button"
            onClick={() => onRemoveRow(name)}
            disabled={!rows || rows.length === 0}
          >
            - Row
          </button>
        </div>
      </div>
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              {headerLabels.map((label) => (
                <th key={label}>{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {!rows || rows.length === 0 ? (
              <tr>
                <td colSpan={headerLabels.length} className="empty-row">
                  No encumbrances captured yet.
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr key={`${name}-${row.id ?? index}`}>
                  <td>{index + 1}</td>
                  <td>
                    <input
                      value={row['Document #'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(name, index, 'Document #', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <input
                      value={row['Description'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(name, index, 'Description', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <textarea
                      value={row['Signatories'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(name, index, 'Signatories', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <select
                      value={row.action_id ?? ''}
                      onChange={(e) =>
                        onFieldChange(name, index, 'action_id', Number(e.target.value))
                      }
                    >
                      <option value="">Select action</option>
                      {actions.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <textarea
                      value={row['Circulation Notes'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(
                          name,
                          index,
                          'Circulation Notes',
                          e.target.value,
                        )
                      }
                    />
                  </td>
                  <td>
                    <select
                      value={row.status_id ?? ''}
                      onChange={(e) =>
                        onFieldChange(name, index, 'status_id', Number(e.target.value))
                      }
                    >
                      <option value="">Select status</option>
                      {statuses.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.label}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default EncumbranceTable;

