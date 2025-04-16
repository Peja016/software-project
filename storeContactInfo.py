from flask import request, jsonify
import requests

def sentData(url_end):
    try:
        # get the data from frontend
        form_data = request.form.to_dict()
        # check if get the data
        if not form_data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # send request to Google Apps Script
        response = requests.post(url_end, data=form_data)
        # return Google Apps Script response to frontend
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
