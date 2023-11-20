from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize 10 sample keys with an additional field for machine ID
keys = {
    "KEY0001": {"used": False, "machine_id": None},
    "KEY0002": {"used": False, "machine_id": None},
    "KEY0003": {"used": False, "machine_id": None},
    "KEY0004": {"used": False, "machine_id": None},
    "KEY0005": {"used": False, "machine_id": None},
    "KEY0006": {"used": False, "machine_id": None},
    "KEY0007": {"used": False, "machine_id": None},
    "KEY0008": {"used": False, "machine_id": None},
    "KEY0009": {"used": False, "machine_id": None},
    "KEY0010": {"used": False, "machine_id": None}
}

@app.route('/validate', methods=['POST'])
def validate_key():
    key = request.form.get('key')
    machine_id = request.form.get('machine_id')
    check_only = request.form.get('check_only', 'False') == 'True'

    if key and key in keys:
        key_data = keys[key]
        if not key_data['used']:
            if not check_only:
                key_data['used'] = True
                key_data['machine_id'] = machine_id
                print(f"Key '{key}' activated for machine ID: {machine_id}.")  # Debug print
            return jsonify({"valid": True, "message": "Key is valid."})
        elif check_only and key_data['machine_id'] == machine_id:
            return jsonify({"valid": True, "message": "Key is valid for this machine."})
        else:
            return jsonify({"valid": False, "message": "Key has already been used or machine ID does not match."})
    
    return jsonify({"valid": False, "message": "Invalid key."})

if __name__ == '__main__':
    app.run(debug=True)

