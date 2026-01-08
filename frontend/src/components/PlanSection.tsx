import type { DocumentTaskStatus, PlanRow } from '../types';
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

interface PlanSectionProps {
  name: string;
  rows: PlanRow[];
  statusOptions: DocumentTaskStatus[];
  onFieldChange: (name: string, index: number, field: string, value: string) => void;
  onAddRow: (name: string) => void;
  onRemoveRow: (name: string) => void;
  onRemovePlan: (name: string) => void;
}

export function PlanSection({
  name,
  rows = [],
  statusOptions,
  onFieldChange,
  onAddRow,
  onRemoveRow,
  onRemovePlan,
}: PlanSectionProps) {
  return (
    <section className="panel">
      <div className="panel__heading">
        <h3>Plan – {name}</h3>
        <div className="panel__actions">
          <button type="button" className="danger" onClick={() => onRemovePlan(name)}>
            - Plan
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
                  No plan documents captured.
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr
                  key={`${name}-${row.id ?? index}`}
                >
                  <td>{index + 1}</td>
                  <td>
                    <input
                      value={row['Document/Desc'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(name, index, 'Document/Desc', e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <input
                      value={row['Copies/Dept'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(name, index, 'Copies/Dept', e.target.value)
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
                    <textarea
                      value={row['Condition of Approval'] ?? ''}
                      onChange={(e) =>
                        onFieldChange(
                          name,
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
                        onFieldChange(name, index, 'Status', e.target.value)
                      }
                    >
                      {statusOptions.map((s) => (
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

export default PlanSection;

