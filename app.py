from flask import Flask, make_response, request, jsonify
from app.report import get_report, trigger_report_generation, get_report_status
app = Flask(__name__)
from datetime import datetime
import json

@app.route('/trigger_report', methods=['GET'])
def trigger_report():
    """Only GET method is allowed."""
    report_id = trigger_report_generation()
    return {"report_id": report_id}, 200

@app.route('/get_report', methods=["GET", 'POST'])
def download_report():
    """Both GET & POST methods are allowed."""
    report_id = request.data.decode("utf-8")
    # report_id = request.args.get('report_id')
    report_status = get_report_status(report_id)

    if report_status == "running":
        return {"report status": "running"}, 200
    elif report_status == "complete":
        csv_data = get_report(report_id).to_csv(index=False)
        csv_bytes = csv_data.encode('utf-8')
        message = {"report status": report_status}
        response = make_response(csv_bytes)
        # response.headers['Content-Type'] = 'text/csv'
        f_name = 'report_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
        response.headers['Content-Disposition'] = 'attachment; filename={f_name}'.format(f_name=f_name)
        # response.headers['X-Message'] = jsonify({"report status": report_status})
        # response.set_data(json.dumps(message))
        return response, 200
    elif report_status == "invalid":
        return {"Report id not found"}, 400
    else:
        return report_status, 500
    
app.run(host='localhost', port=5000, debug=True)