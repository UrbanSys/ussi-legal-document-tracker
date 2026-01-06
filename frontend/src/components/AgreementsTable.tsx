import type { AgreementRow } from '../types';
import './Table.css';

const headerLabels = [
  'Item',
  'Document/Desc',
  'Copies/Dept',
  'Signatories',
  'Condition of Approval',
  'Circulation Notes',
  'Status',
];

interface AgreementsTableProps {
  rows: AgreementRow[];
  statusOptions: string[];
  onFieldChange: (index: number, field: string, value: string) => void;
  onAddRow: () => void;
  onRemoveRow: () => void;
}

export function AgreementsTable({
  rows,
  statusOptions,
  onFieldChange,
  onAddRow,
  onRemoveRow,
}: AgreementsTableProps) {
  return (
    <section className="panel">
      <div className="panel__heading">
        <h2>New Agreements Concurrent with Registration</h2>
        <div className="panel__actions">
          <button type="button" onClick={onAddRow}>
            + Row
          </button>
          <button
            type="button"
            onClick={onRemoveRow}
            disabled={rows.length === 0}
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
            {rows.length === 0 ? (
              <tr>
                <td colSpan={headerLabels.length} className="empty-row">
                  No new agreements captured.
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr key={`${row.id}-${index}`}>
                  <td>{index + 1}</td>
                  <td>
                    <input
                      value={row['Document/Desc'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(index, 'Document/Desc', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <input
                      value={row['Copies/Dept'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(index, 'Copies/Dept', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <textarea
                      value={row['Signatories'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(index, 'Signatories', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <textarea
                      value={row['Condition of Approval'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(
                          index,
                          'Condition of Approval',
                          e.target.value,
                        )
                      }
                    />
                  </td>
                  <td>
                    <textarea
                      value={row['Circulation Notes'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(index, 'Circulation Notes', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <select
                      value={row['Status'] ?? statusOptions[0]}
                      onChange={(e) =>
                        onFieldChange(index, 'Status', e.target.value)
                      }
                    >
                      {statusOptions.map((option) => (
                        <option value={option} key={option}>
                          {option}
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

export default AgreementsTable;

