from flask import request, jsonify, session, make_response
import requests

def accessData(url_end):
    try:
        form_data = request.form.to_dict()
        # check if get the data
        if not form_data:
            return make_response(jsonify({"status": "error", "message": "No data received"}), 400)

        # send request to Google Apps Script
        response = requests.post(url_end, data=form_data)

        if response.json().get("status") != 'error':
            name = form_data.get('name')
            session['name'] = name
        # return Google Apps Script response to frontend
        return jsonify(response.json())

    except Exception as e:
        return make_response(jsonify({"status": "error", "message": str(e)}), 500)