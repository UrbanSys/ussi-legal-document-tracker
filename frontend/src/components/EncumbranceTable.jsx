import PropTypes from "prop-types";
import "./Table.css";

const headerLabels = [
  "Item",
  "Document #",
  "Description",
  "Signatories",
  "Action",
  "Circulation Notes",
  "Status",
];

export function EncumbranceTable({
  rows,
  actionOptions,
  statusOptions,
  onFieldChange,
  onAddRow,
  onRemoveRow,
}) {
  return (
    <section className="panel">
      <div className="panel__heading">
        <h2>Existing Encumbrances on Title</h2>
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
                  No encumbrances captured yet.
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr key={`${row.id}-${index}`}>
                  <td>{index + 1}</td>
                  <td>
                    <input
                      value={row["Document #"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(index, "Document #", e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <input
                      value={row["Description"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(index, "Description", e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <textarea
                      value={row["Signatories"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(index, "Signatories", e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <select
                      value={row["Action"] ?? actionOptions[0]}
                      onChange={(e) =>
                        onFieldChange(index, "Action", e.target.value)
                      }
                    >
                      {actionOptions.map((option) => (
                        <option value={option} key={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <textarea
                      value={row["Circulation Notes"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(index, "Circulation Notes", e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <select
                      value={row["Status"] ?? statusOptions[0]}
                      onChange={(e) =>
                        onFieldChange(index, "Status", e.target.value)
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

EncumbranceTable.propTypes = {
  rows: PropTypes.arrayOf(PropTypes.object).isRequired,
  actionOptions: PropTypes.arrayOf(PropTypes.string).isRequired,
  statusOptions: PropTypes.arrayOf(PropTypes.string).isRequired,
  onFieldChange: PropTypes.func.isRequired,
  onAddRow: PropTypes.func.isRequired,
  onRemoveRow: PropTypes.func.isRequired,
};

export default EncumbranceTable;
