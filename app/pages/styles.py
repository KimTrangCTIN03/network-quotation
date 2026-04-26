BASE_STYLE = """
<style>
    * { box-sizing: border-box; }
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        background: #f4f7fb;
        color: #0f172a;
    }
    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px;
    }
    h1 {
        margin: 0 0 8px 0;
        font-size: 36px;
    }
    .subtitle {
        color: #475569;
        font-size: 17px;
        margin-bottom: 20px;
    }
    .stepbar {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 22px;
    }
    .step {
        background: white;
        border: 1px solid #dbe3ef;
        border-radius: 14px;
        padding: 14px;
        color: #64748b;
        font-weight: bold;
    }
    .step.active {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }
    .card {
        background: #fff;
        border-radius: 16px;
        border: 1px solid #dbe3ef;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        padding: 20px;
        margin-bottom: 18px;
    }
    .section-title {
        font-size: 17px;
        font-weight: bold;
        margin: 20px 0 12px;
        color: #0f172a;
        padding-bottom: 8px;
        border-bottom: 1px solid #e2e8f0;
    }
    label {
        display: block;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
        color: #334155;
    }
    input[type="text"],
    input[type="number"] {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        font-size: 14px;
        background: #fff;
    }
    input[type="checkbox"] {
        transform: scale(1.1);
        margin-right: 8px;
    }
    .checkbox-row {
        display: flex;
        align-items: center;
        margin-top: 8px;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }
    .sub-card {
        border: 1px solid #dbe3ef;
        border-radius: 14px;
        padding: 14px;
        background: #fafcff;
        margin-bottom: 12px;
    }
    .sub-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .sub-card-title {
        font-weight: bold;
        font-size: 14px;
    }
    .btn {
        border: none;
        padding: 11px 16px;
        border-radius: 10px;
        cursor: pointer;
        font-weight: bold;
        font-size: 14px;
        text-decoration: none;
        display: inline-block;
    }
    .btn-primary {
        background: #2563eb;
        color: white;
    }
    .btn-secondary {
        background: #e2e8f0;
        color: #0f172a;
    }
    .btn-danger {
        background: #ef4444;
        color: white;
        padding: 8px 12px;
        font-size: 12px;
    }
    .actions {
        display: flex;
        gap: 10px;
        margin-top: 18px;
        flex-wrap: wrap;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: white;
    }
    th, td {
        border: 1px solid #dbe3ef;
        padding: 8px;
        text-align: left;
        vertical-align: top;
    }
    th {
        background: #eff6ff;
        font-weight: bold;
    }
    select {
        width: 100%;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        font-size: 13px;
        background: #fff;
    }
    .small {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }
    .error-box {
        display: none;
        margin-top: 12px;
        padding: 12px;
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        border-radius: 10px;
        white-space: pre-wrap;
    }
    .success-box {
        display: none;
        margin-top: 12px;
        padding: 12px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        border-radius: 10px;
    }
    .empty-state {
        padding: 30px;
        text-align: center;
        color: #64748b;
        border: 1px dashed #cbd5e1;
        border-radius: 14px;
        background: #f8fafc;
    }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }
    .metric {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
    }
    .metric-label {
        color: #64748b;
        font-size: 13px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: bold;
        margin-top: 6px;
    }
    pre {
        margin: 0;
        white-space: pre-wrap;
        font-family: Consolas, monospace;
        font-size: 12px;
    }
</style>
"""
