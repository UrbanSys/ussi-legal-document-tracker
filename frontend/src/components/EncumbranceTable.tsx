import { useState } from 'react';
import type { EncumbranceRow, EncumbranceAction, EncumbranceStatus } from '../types';
import './Table.css';

const headerLabels = [
  '',
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
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set());
  const [bulkAction, setBulkAction] = useState<string>('');
  const [bulkStatus, setBulkStatus] = useState<string>('');

  const allSelected = rows.length > 0 && selectedRows.size === rows.length;
  const someSelected = selectedRows.size > 0;

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(rows.map((_, i) => i)));
    }
  };

  const toggleRow = (index: number) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedRows(newSelected);
  };

  const applyBulkAction = () => {
    if (!bulkAction) return;
    selectedRows.forEach((index) => {
      onFieldChange(name, index, 'action_id', Number(bulkAction));
    });
    setBulkAction('');
    setSelectedRows(new Set());
  };

  const applyBulkStatus = () => {
    if (!bulkStatus) return;
    selectedRows.forEach((index) => {
      onFieldChange(name, index, 'status_id', Number(bulkStatus));
    });
    setBulkStatus('');
    setSelectedRows(new Set());
  };

  const getRowClassName = (row: EncumbranceRow, index: number) => {
    const statusLabel = statuses.find((s) => s.id === row.status_id)?.label ?? 'unknown';
    const statusClass = `status-row status-${statusLabel.toLowerCase().replace(/\s+/g, '-')}`;
    const selectedClass = selectedRows.has(index) ? 'selected-row' : '';
    return `${statusClass} ${selectedClass}`.trim();
  };

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

      {someSelected && (
        <div className="bulk-action-bar">
          <span className="bulk-selection-count">{selectedRows.size} row(s) selected</span>
          <div className="bulk-action-group">
            <label>Set Action:</label>
            <select value={bulkAction} onChange={(e) => setBulkAction(e.target.value)}>
              <option value="">Select...</option>
              {actions.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.label}
                </option>
              ))}
            </select>
            <button type="button" onClick={applyBulkAction} disabled={!bulkAction}>
              Apply
            </button>
          </div>
          <div className="bulk-action-group">
            <label>Set Status:</label>
            <select value={bulkStatus} onChange={(e) => setBulkStatus(e.target.value)}>
              <option value="">Select...</option>
              {statuses.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
            <button type="button" onClick={applyBulkStatus} disabled={!bulkStatus}>
              Apply
            </button>
          </div>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => setSelectedRows(new Set())}
          >
            Clear Selection
          </button>
        </div>
      )}

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th className="checkbox-col">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={toggleSelectAll}
                  disabled={rows.length === 0}
                />
              </th>
              {headerLabels.slice(1).map((label) => (
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
                <tr key={`${name}-${row.id ?? index}`} className={getRowClassName(row, index)}>
                  <td className="checkbox-col">
                    <input
                      type="checkbox"
                      checked={selectedRows.has(index)}
                      onChange={() => toggleRow(index)}
                    />
                  </td>
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
