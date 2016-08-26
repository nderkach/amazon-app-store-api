"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import re
import requests

app = Flask(__name__)

###
# Routing for your application.
###


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/results', methods=['POST'])
def results():
    """Render search results."""
    return render_template(
        'results.html',
        title=request.form.get("title"),
        version=request.form.get("version"),
        release_date=request.form.get("release_date"),
        release_notes=request.form.getlist("release_notes[]"))


@app.route('/<item_id>')
def get_item(item_id):
    """Get Amazon App Store item info."""
    if not re.match(
        '^[A-Z0-9]{10}$',
            item_id):  # potentially make the input check even more strict
        return make_response(
            jsonify({"error": "Invalid app id: {}".format(item_id)}), 400)

    url = 'https://mas-ssr.amazon.com/gp/masclient/dp/' + item_id

    headers = {
        'host': 'mas-ssr.amazon.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'Appstore/release-11.0004.790.6C_641000410 (Android/4.4.4/19/A1-850)',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'en-US',
        'Cookie': 'masclient-device-info=dpi:1.3312501|w:800|h:1216|xdpi:188.148|ydpi:189.023|deviceType:A3GFS040JDOGQR|cor:US|pfm:ATVPDKIKX0DER|layout:268435539|deviceDescriptorId:MDD-S-2SWPF7EAH86SV|ref_encoded:preload_carrier%3DACER%3Bpreload_campaign%3D2014_1%3Bdevice_model%3Dacer-canary%3B|baseFont:23|phoneType:0|cloudLibrary:0|lang:en-US|testDriveSdkVersion:1.0|carrier_encoded:unknown|build_product_encoded:a1850_ww_gen1|build_fingerprint_encoded:acer%2Fa1850_ww_gen1%2Fvespa8%3A4.4.4%2FKTU84P%2F1417433162%3Auser%2Frelease-keys|manufacturer_encoded:Acer|carrierBillingEligible:0|carrierBillingEnabled:0|androidTargetSdkVersion:19|androidApkInstallSource:UNKNOWN;',
        'X-Requested-With': 'com.amazon.venezia'
    }

    response = requests.get(
        url=url,
        headers=headers
    )

    data = response.json()[-1]["contents"]  # block: data
    product_details = data[-2]["contents"]  # id: productDetailsView
    release_notes = data[3]["contents"]  # id: releaseNotes

    title = product_details["displayTitle"]

    if not title:
        # invalid item id
        return make_response(
            jsonify({"error": "Invalid app id: {}".format(item_id)}), 400)

    version = product_details["version"]
    release_date = product_details["technicalInfo"]["latestVersionReleaseDate"]
    release_notes = [note["label"] for note in release_notes["items"]]

    return jsonify({"title": title,
                    "version": version,
                    "release_date": release_date,
                    "release_notes": release_notes})


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
