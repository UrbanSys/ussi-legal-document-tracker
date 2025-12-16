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
  name,
  rows,
  actions,
  statuses,
  onFieldChange,
  onAddRow,
  onRemoveRow,
  onRemoveTitle
}) {
  return (
    <section className="panel">
      <div className="panel__heading">
        <h3>Title - {name}</h3>
        <div className="panel__actions">
          <button type="button" className = "danger" onClick={() => onRemoveTitle(name)}>
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
                      value={row["Document #"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(name, index, "Document #", e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <input
                      value={row["Description"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(name, index, "Description", e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <textarea
                      value={row["Signatories"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(name, index, "Signatories", e.target.value)
                      }
                    />
                  </td>
                  <td>
                    <select
                      value={row.action_id ?? ""}
                      onChange={(e) =>
                        onFieldChange(name, index, "action_id", Number(e.target.value))
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
                      value={row["Circulation Notes"] ?? ""}
                      onChange={(e) =>
                        onFieldChange(
                          name,
                          index,
                          "Circulation Notes",
                          e.target.value,
                        )
                      }
                    />
                  </td>
                  <td>
                    <select
                      value={row.status_id ?? ""}
                      onChange={(e) =>
                        onFieldChange(name, index, "status_id", Number(e.target.value))
                      }
                    >
                      <option value="">Select action</option>
                      {statuses.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.label}
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
  actions: PropTypes.number.isRequired,
  statuses: PropTypes.number.isRequired,
  onFieldChange: PropTypes.func.isRequired,
  onAddRow: PropTypes.func.isRequired,
  onRemoveRow: PropTypes.func.isRequired,
};

EncumbranceTable.defaultProps = {
  rows: [],
};

export default EncumbranceTable;
